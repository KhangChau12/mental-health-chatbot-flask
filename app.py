"""
File Flask chính cho ứng dụng Chatbot Sàng lọc Sức khỏe Tâm thần
Cập nhật để xử lý lịch sử chat từ localStorage
"""

import os
import logging
import json
import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session

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
    Route cho trang chủ
    """
    return render_template('index.html')

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """
    API endpoint nhận tin nhắn từ người dùng và trả về phản hồi
    Cập nhật để nhận lịch sử chat từ client
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        use_ai = data.get('useAI', True)
        message_history = data.get('messageHistory', [])  # Lấy lịch sử từ client
        client_chat_state = data.get('chatState')  # Lấy trạng thái chat từ client
        
        # Sử dụng chat state từ client nếu có, không thì khởi tạo mới
        chat_state = client_chat_state if client_chat_state else initialize_chat()
        
        # Xử lý tin nhắn bằng logic cứng
        updated_chat_state = process_message(chat_state.copy(), user_message)
        
        bot_response = ''
        
        # Sử dụng AI nếu được yêu cầu và có thể
        if use_ai:
            try:
                # Tạo contextual prompt
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
        
        # Tạo thông tin tin nhắn bot
        bot_msg_id = str(datetime.datetime.now().timestamp())
        timestamp = datetime.datetime.now().strftime('%H:%M')
        
        # Trả về phản hồi và trạng thái chat mới
        return jsonify({
            'text': bot_response,
            'id': bot_msg_id,
            'timestamp': timestamp,
            'state': updated_chat_state.get('state', ''),
            'chatState': updated_chat_state  # Trả về trạng thái chat mới để client lưu
        })
        
    except Exception as e:
        logger.exception("Error processing message", exc_info=e)
        return jsonify({
            'error': str(e),
            'text': "Xin lỗi, đã xảy ra lỗi khi xử lý tin nhắn của bạn. Vui lòng thử lại sau."
        }), 500

@app.route('/api/restart', methods=['POST'])
def restart_chat():
    """
    API endpoint để khởi động lại cuộc trò chuyện
    """
    try:
        data = request.get_json() if request.is_json else {}
        preserve_local_messages = data.get('preserveLocalMessages', False)
        
        # Khởi tạo lại chat state
        new_chat_state = initialize_chat()
        
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
            'chatState': new_chat_state  # Trả về trạng thái chat mới cho client
        })
        
    except Exception as e:
        logger.exception("Error restarting chat", exc_info=e)
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/toggle_ai', methods=['POST'])
def toggle_ai():
    """
    API endpoint để bật/tắt chế độ AI
    """
    try:
        data = request.get_json()
        use_ai = data.get('useAI', True)
        
        return jsonify({
            'success': True,
            'useAI': use_ai
        })
        
    except Exception as e:
        logger.exception("Error toggling AI mode", exc_info=e)
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)