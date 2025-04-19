"""
File Flask chính cho ứng dụng Chatbot Sàng lọc Sức khỏe Tâm thần
Cập nhật để xử lý lịch sử chat từ localStorage
"""

import uuid
import os
import logging
import json
import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from data.questionnaires import questionnaires

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import các module cần thiết
from config import Config
from utils.chat_logic import initialize_chat, process_message
from utils.together_ai import initialize_together_client, generate_chat_completion, extract_text_from_response
from utils.contextual_prompt import create_contextual_prompt

# Khởi tạo Flask app
app = Flask(__name__)
app.config.from_object(Config)
Session(app)

# Khởi tạo Together AI client
initialize_together_client()

@app.route('/')
def index():
    """
    Route cho trang chủ - hiển thị trang lựa chọn phiên bản
    """
    return render_template('home.html')

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """
    API endpoint nhận tin nhắn từ người dùng và trả về phản hồi
    Hỗ trợ cả chế độ AI (chat + poll) và chế độ Logic (poll-only)
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        use_ai = data.get('useAI', True)
        message_history = data.get('messageHistory', [])  # Lấy lịch sử từ client
        client_chat_state = data.get('chatState')  # Lấy trạng thái chat từ client
        
        # Thêm session ID nếu chưa có để làm khóa cho phân tích
        if client_chat_state and 'sessionId' not in client_chat_state:
            session_id = str(uuid.uuid4())
            client_chat_state['sessionId'] = session_id
        
        # Xác định chế độ (ai hoặc logic)
        interface_mode = client_chat_state.get('interfaceMode', 'chat') if client_chat_state else 'chat'
        
        # Sử dụng chat state từ client nếu có, không thì khởi tạo mới
        chat_state = client_chat_state if client_chat_state else initialize_chat(
            'logic' if interface_mode == 'poll' else 'ai'
        )
        
        # Xử lý tin nhắn - sẽ trả về phản hồi ngay lập tức
        updated_chat_state = process_message(chat_state.copy(), user_message)
        
        bot_response = ''
        poll_options = []
        
        # Sử dụng AI nếu được yêu cầu và trong chế độ AI (không phải chế độ logic)
        if use_ai and interface_mode != 'poll':
            try:
                # Tạo contextual prompt
                from utils.contextual_prompt import create_contextual_prompt
                contextual_prompt = create_contextual_prompt(updated_chat_state, user_message, message_history)
                
                # Gọi Together API với lịch sử từ client
                ai_response = generate_chat_completion(message_history, contextual_prompt)
                
                if ai_response:
                    # Trích xuất phản hồi từ API
                    bot_response = extract_text_from_response(ai_response)
                else:
                    # Fallback to logic mode
                    logger.warning("AI response failed, falling back to logic mode")
                    bot_response = updated_chat_state.get('botMessage', '')
            except Exception as e:
                logger.error(f"Error using AI mode: {str(e)}")
                bot_response = updated_chat_state.get('botMessage', '')
        else:
            # Sử dụng logic cứng
            bot_response = updated_chat_state.get('botMessage', '')
            poll_options = updated_chat_state.get('pollOptions', [])
        
        # Tạo thông tin tin nhắn bot
        bot_msg_id = str(datetime.datetime.now().timestamp())
        timestamp = datetime.datetime.now().strftime('%H:%M')
        
        # Tạo một đối tượng với thông tin chi tiết về đánh giá hiện tại
        assessment_details = {}
        if updated_chat_state.get('currentAssessment') in questionnaires:
            current_assessment = questionnaires[updated_chat_state.get('currentAssessment')]
            assessment_details = {
                'name': current_assessment.get('name', ''),
                'description': current_assessment.get('description', ''),
                'id': current_assessment.get('id', '')
            }
        
        # Trả về phản hồi và trạng thái chat mới
        response = {
            'text': bot_response,
            'id': bot_msg_id,
            'timestamp': timestamp,
            'state': updated_chat_state.get('state', ''),
            'chatState': {
                'sessionId': updated_chat_state.get('sessionId', str(uuid.uuid4())),
                'state': updated_chat_state.get('state', ''),
                'currentAssessment': updated_chat_state.get('currentAssessment'),
                'currentQuestionIndex': updated_chat_state.get('currentQuestionIndex', 0),
                'totalQuestions': get_total_questions(updated_chat_state),
                'scores': updated_chat_state.get('scores', {}),
                'severityLevels': updated_chat_state.get('severityLevels', {}),
                'flags': updated_chat_state.get('flags', {}),
                'assessmentDetails': assessment_details,
                'interfaceMode': updated_chat_state.get('interfaceMode', 'chat')
            }
        }
        
        # Thêm poll options nếu có
        if poll_options:
            response['pollOptions'] = poll_options
        
        return jsonify(response)
        
    except Exception as e:
        logger.exception("Error processing message", exc_info=e)
        return jsonify({
            'error': str(e),
            'text': "Xin lỗi, đã xảy ra lỗi khi xử lý tin nhắn của bạn. Vui lòng thử lại sau."
        }), 500
    
# Hàm trợ giúp để lấy tổng số câu hỏi
def get_total_questions(chat_state):
    current_assessment = chat_state.get('currentAssessment')
    if current_assessment and current_assessment in questionnaires:
        return len(questionnaires[current_assessment].get('questions', []))
    return 0

@app.route('/api/restart', methods=['POST'])
def restart_chat():
    """
    API endpoint để khởi động lại cuộc trò chuyện
    """
    try:
        data = request.get_json() if request.is_json else {}
        preserve_local_messages = data.get('preserveLocalMessages', False)
        mode = data.get('mode', 'ai')  # Mặc định là chế độ AI
        
        # Khởi tạo lại chat state với mode tương ứng
        new_chat_state = initialize_chat(mode)
        
        # Tạo tin nhắn chào mừng
        welcome_message = {
            'role': 'assistant',
            'content': new_chat_state.get('botMessage', ''),
            'id': 'welcome-message-restart',
            'timestamp': datetime.datetime.now().strftime('%H:%M')
        }
        
        return jsonify({
            'success': True,
            'welcomeMessage': welcome_message,
            'chatState': {
                'state': new_chat_state.get('state', ''),
                'currentAssessment': new_chat_state.get('currentAssessment'),
                'currentQuestionIndex': new_chat_state.get('currentQuestionIndex', 0),
                'totalQuestions': get_total_questions(new_chat_state),
                'scores': new_chat_state.get('scores', {}),
                'severityLevels': new_chat_state.get('severityLevels', {}),
                'flags': new_chat_state.get('flags', {}),
                'interfaceMode': new_chat_state.get('interfaceMode', 'chat'),
                # Thêm thông tin chi tiết về giai đoạn greeting
                'assessmentDetails': {
                    'name': 'Bắt đầu trò chuyện' if mode == 'ai' else 'Sàng lọc Ban đầu',
                    'description': 'Chào mừng bạn đến với Trợ lý Sức khỏe Tâm thần',
                    'id': 'greeting' if mode == 'ai' else 'initialScreening'
                }
            }
        })
        
    except Exception as e:
        logger.exception("Error restarting chat", exc_info=e)
        return jsonify({
            'error': str(e),
            'success': False
        }), 500
def get_assessment_details(assessment_id):
    """
    Hàm trợ giúp để lấy thông tin chi tiết về bộ đánh giá
    """
    if assessment_id in questionnaires:
        assessment = questionnaires[assessment_id]
        return {
            'name': assessment.get('name', ''),
            'description': assessment.get('description', ''),
            'id': assessment.get('id', ''),
            'questionCount': len(assessment.get('questions', []))
        }
    return {}

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    """
    Route cho trang Điều khoản
    """
    return render_template('terms.html')

@app.route('/contact')
def contact():
    """
    Route cho trang Liên hệ
    """
    return render_template('contact.html')

@app.route('/logic')
def logic():
    """
    Route cho trang khảo sát thuần túy (poll-only)
    """
    return render_template('logic.html')

@app.route('/ai')
def ai():
    """
    Route cho trang AI (chat + poll)
    """
    return render_template('index.html')

@app.route('/api/poll_flow', methods=['POST'])
def poll_flow():
    """
    API endpoint xử lý luồng poll thuần túy
    Không sử dụng chat, chỉ sử dụng poll
    """
    try:
        data = request.get_json()
        action = data.get('action', '')
        
        if action == 'start':
            # Bắt đầu khảo sát mới
            from utils.logic_poll import start_poll
            result = start_poll()
            return jsonify(result)
        
        elif action == 'submit':
            # Xử lý phản hồi poll
            response = data.get('response', '')
            details = data.get('details', '')
            chat_state = data.get('chatState')
            
            # Xử lý trường hợp đặc biệt cho trạng thái preview
            if chat_state and chat_state.get('state') == 'results_preview':
                from utils.logic_poll import handle_results_preview
                result = handle_results_preview(chat_state, 'continue')
                return jsonify(result)
            
            # Xử lý bình thường
            from utils.logic_poll import process_poll_response
            result = process_poll_response(chat_state, response, details)
            
            # Nếu kết quả cho trang preview, thêm dữ liệu HTML và biểu đồ
            if result and 'chatState' in result and result['chatState'].get('state') == 'results_preview':
                from utils.logic_poll import generate_preview_html, generate_preview_chart_data
                
                scores = result['chatState'].get('scores', {})
                severity_levels = result['chatState'].get('severityLevels', {})
                
                result['previewHtml'] = generate_preview_html(scores, severity_levels)
                result['chartData'] = generate_preview_chart_data(scores)
            
            return jsonify(result)
        
        elif action == 'resources':
            # Lấy tài nguyên
            chat_state = data.get('chatState')
            
            from utils.logic_poll import get_resources
            result = get_resources(chat_state)
            return jsonify(result)
        
        elif action == 'restart':
            # Khởi động lại khảo sát
            from utils.logic_poll import initialize_poll
            poll_state = initialize_poll()
            return jsonify({
                'success': True,
                'chatState': poll_state
            })
        
        else:
            return jsonify({
                'error': 'Hành động không hợp lệ'
            }), 400
    
    except Exception as e:
        logger.exception("Error in poll_flow", exc_info=e)
        return jsonify({
            'error': str(e)
        }), 500
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)