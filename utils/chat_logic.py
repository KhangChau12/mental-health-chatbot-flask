"""
Logic điều khiển luồng chat
Phiên bản cải tiến kết hợp trò chuyện tự nhiên và giao diện poll
"""

import logging
import random
import datetime
from data.questionnaires import questionnaires, emergency_message
from data.question_bank import question_bank, get_random_question, get_question_category, has_risk_flag, QUESTION_IDS
from data.conversation_map import get_next_question, has_sufficient_screening
from utils.scoring import calculate_scores, get_severity_level, check_risk_flags
from data.resources import get_resources_for_severity, format_resources_html
from data.diagnostic import format_disorder_info

logger = logging.getLogger(__name__)

# Trạng thái chat
CHAT_STATES = {
    'GREETING': 'greeting',
    'COLLECTING_ISSUE': 'collecting_issue',
    'NATURAL_CONVERSATION': 'natural_conversation',  # Trạng thái mới cho trò chuyện tự nhiên
    'POLL_INTERACTION': 'poll_interaction',          # Trạng thái mới cho giao diện poll
    'INITIAL_SCREENING': 'initial_screening',
    'DETAILED_ASSESSMENT': 'detailed_assessment',
    'ADDITIONAL_ASSESSMENT': 'additional_assessment',
    'SUICIDE_ASSESSMENT': 'suicide_assessment',
    'SUMMARY': 'summary',
    'RESOURCES': 'resources',
    'DISORDER_INFO': 'disorder_info',
    'CLOSING': 'closing'
}

def initialize_chat(mode='ai'):
    """
    Khởi tạo trạng thái chat
    
    Args:
        mode (str): Chế độ chat ('ai' hoặc 'logic')
        
    Returns:
        dict: Trạng thái chat ban đầu
    """
    # Chế độ logic: bỏ qua greeting và collecting_issue, đi thẳng vào poll
    if mode == 'logic':
        return {
            'state': CHAT_STATES['INITIAL_SCREENING'],
            'currentAssessment': 'initialScreening',
            'currentQuestionIndex': 0,
            'userResponses': {},
            'scores': {},
            'severityLevels': {},
            'flags': {
                'suicideRisk': False
            },
            'interfaceMode': 'poll',  # Luôn sử dụng poll cho phiên bản logic
            'botMessage': questionnaires['initialScreening']['questions'][0]['text']
        }
    
    # Chế độ AI: bắt đầu với greeting và trò chuyện tự nhiên
    return {
        'state': CHAT_STATES['GREETING'],
        'currentAssessment': None,
        'currentQuestionIndex': 0,
        'currentQuestionId': None,
        'naturalConversation': {
            'askedQuestions': [],
            'scores': {},
            'summaryAnswers': {},
        },
        'userResponses': {},
        'scores': {},
        'severityLevels': {},
        'flags': {
            'suicideRisk': False
        },
        'interfaceMode': 'chat',  # Bắt đầu với chat cho phiên bản AI
        'botMessage': "Xin chào! Tôi là một trợ lý AI được thiết kế để hỗ trợ sàng lọc sức khỏe tâm thần. Tôi sẽ trò chuyện với bạn để hiểu hơn về cảm xúc và trải nghiệm của bạn. Cuộc trò chuyện này hoàn toàn riêng tư và chỉ nhằm mục đích cung cấp thông tin tham khảo. Tôi không phải là chuyên gia y tế và không thay thế cho tư vấn chuyên nghiệp.\n\nTrước khi bắt đầu, bạn có thể cho tôi biết lý do bạn tìm đến dịch vụ này hôm nay không?"
    }

def process_message(chat_state, user_message):
    """
    Xử lý tin nhắn người dùng và xác định tin nhắn bot tiếp theo
    
    Args:
        chat_state: Dict trạng thái chat hiện tại
        user_message: String tin nhắn người dùng
        
    Returns:
        Dict trạng thái chat đã cập nhật
    """
    if not chat_state or not user_message:
        logger.warning("Missing chat_state or user_message in process_message")
        return chat_state or initialize_chat()

    # Xác định chế độ giao diện hiện tại
    interface_mode = chat_state.get('interfaceMode', 'chat')
    
    # Nếu đang ở chế độ logic, luôn sử dụng poll
    if interface_mode == 'poll':
        # Xử lý response poll trực tiếp thay vì tin nhắn
        # Giả định user_message là chỉ số tùy chọn đã chọn
        return handle_poll_message(chat_state, user_message)
    
    # Nếu đang ở chế độ AI (chat), xử lý dựa trên trạng thái
    state = chat_state.get('state')
    
    if state == CHAT_STATES['GREETING']:
        return handle_greeting(chat_state, user_message)
    
    elif state == CHAT_STATES['COLLECTING_ISSUE']:
        return handle_collecting_issue(chat_state, user_message)
    
    elif state == CHAT_STATES['NATURAL_CONVERSATION']:
        return handle_natural_conversation(chat_state, user_message)
    
    elif state == CHAT_STATES['POLL_INTERACTION']:
        return handle_poll_interaction(chat_state, user_message)
    
    elif state == CHAT_STATES['INITIAL_SCREENING']:
        return handle_assessment(chat_state, user_message, 'initialScreening')
    
    elif state == CHAT_STATES['DETAILED_ASSESSMENT']:
        return handle_assessment(chat_state, user_message, chat_state.get('currentAssessment'))
    
    elif state == CHAT_STATES['ADDITIONAL_ASSESSMENT']:
        return handle_assessment(chat_state, user_message, chat_state.get('currentAssessment'))
    
    elif state == CHAT_STATES['SUICIDE_ASSESSMENT']:
        return handle_assessment(chat_state, user_message, 'suicideRiskAssessment')
    
    elif state == CHAT_STATES['SUMMARY']:
        return handle_summary(chat_state, user_message)
    
    elif state == CHAT_STATES['RESOURCES']:
        return handle_resources(chat_state, user_message)
    
    elif state == CHAT_STATES['DISORDER_INFO']:
        return handle_disorder_info(chat_state, user_message)
    
    elif state == CHAT_STATES['CLOSING']:
        return handle_closing(chat_state, user_message)
    
    else:
        logger.warning(f"Unknown chat state: {state}")
        return {
            **chat_state,
            'botMessage': "Xin lỗi, tôi không hiểu. Hãy thử lại."
        }

def handle_poll_message(chat_state, user_message):
    """
    Xử lý tin nhắn dưới dạng poll (chế độ logic)
    
    Args:
        chat_state: Dict trạng thái chat hiện tại
        user_message: String tin nhắn người dùng (chỉ số tùy chọn hoặc text)
        
    Returns:
        Dict trạng thái chat đã cập nhật
    """
    try:
        # Lấy thông tin assessment hiện tại
        assessment_id = chat_state.get('currentAssessment')
        if not assessment_id or assessment_id not in questionnaires:
            logger.error(f"Invalid assessment {assessment_id} in handle_poll_message")
            return {
                **chat_state,
                'botMessage': "Xin lỗi, đã xảy ra lỗi. Vui lòng thử lại."
            }
        
        assessment = questionnaires[assessment_id]
        current_index = chat_state.get('currentQuestionIndex', 0)
        
        # Kiểm tra index hợp lệ
        if current_index < 0 or current_index >= len(assessment['questions']):
            logger.error(f"Invalid question index {current_index} for assessment {assessment_id}")
            return {
                **chat_state,
                'botMessage': "Xin lỗi, đã xảy ra lỗi. Vui lòng thử lại."
            }
        
        current_question = assessment['questions'][current_index]
        
        # Xử lý phản hồi
        option_index = -1
        
        # Nếu user_message là số, giả định là chỉ số tùy chọn
        if user_message.isdigit():
            option_index = int(user_message)
        else:
            # Nếu không, cố gắng so khớp với text của tùy chọn
            for i, option in enumerate(current_question['options']):
                option_text = option.get('text', '').lower()
                if option_text in user_message.lower():
                    option_index = i
                    break
        
        # Nếu không tìm thấy tùy chọn phù hợp, giả định tùy chọn đầu tiên
        if option_index < 0 or option_index >= len(current_question['options']):
            option_index = 0
        
        option_value = current_question['options'][option_index]['value']
        
        # Ghi lại phản hồi
        user_responses = chat_state.get('userResponses', {})
        assessment_responses = user_responses.get(assessment_id, {})
        assessment_responses[current_question['id']] = option_value
        
        updated_responses = {
            **user_responses,
            assessment_id: assessment_responses
        }
        
        # Cập nhật trạng thái chat
        updated_chat_state = {
            **chat_state,
            'userResponses': updated_responses
        }
        
        # Kiểm tra cờ nguy cơ
        updated_flags = dict(chat_state.get('flags', {}))
        if current_question.get('flag') == 'suicide_risk' and option_value >= 3:
            updated_flags['suicideRisk'] = True
            updated_chat_state['flags'] = updated_flags
        
        # Chuyển sang câu hỏi tiếp theo
        next_index = current_index + 1
        
        # Kiểm tra xem đã hoàn thành assessment hiện tại chưa
        if next_index >= len(assessment['questions']):
            # Tính điểm và mức độ nghiêm trọng
            scores = calculate_scores(assessment_responses, assessment)
            severity = get_severity_level(scores, assessment)
            
            # Cập nhật điểm và mức độ
            updated_chat_state['scores'] = {
                **chat_state.get('scores', {}),
                assessment_id: scores
            }
            
            updated_chat_state['severityLevels'] = {
                **chat_state.get('severityLevels', {}),
                assessment_id: severity
            }
            
            # Xác định trạng thái tiếp theo
            next_state = determine_next_state(updated_chat_state, assessment, severity, updated_flags)
            updated_chat_state.update(next_state)
            
            # Nếu chuyển sang assessment khác, lấy câu hỏi đầu tiên
            if updated_chat_state['state'] in [CHAT_STATES['DETAILED_ASSESSMENT'], CHAT_STATES['ADDITIONAL_ASSESSMENT'], CHAT_STATES['SUICIDE_ASSESSMENT']]:
                next_assessment = updated_chat_state['currentAssessment']
                if next_assessment and next_assessment in questionnaires:
                    next_question = questionnaires[next_assessment]['questions'][0]
                    updated_chat_state['botMessage'] = next_question['text']
                    updated_chat_state['pollOptions'] = [option['text'] for option in next_question['options']]
                    return updated_chat_state
            
            # Nếu chuyển sang summary hoặc trạng thái khác
            if updated_chat_state['state'] == CHAT_STATES['SUMMARY']:
                summary = generate_summary(updated_chat_state.get('scores', {}), updated_chat_state.get('severityLevels', {}))
                updated_chat_state['botMessage'] = summary
                return updated_chat_state
            
            # Fallback
            updated_chat_state['botMessage'] = "Cảm ơn bạn đã hoàn thành. Bạn có muốn tiếp tục không?"
            return updated_chat_state
        
        # Nếu chưa hết câu hỏi, chuyển sang câu hỏi tiếp theo
        updated_chat_state['currentQuestionIndex'] = next_index
        next_question = assessment['questions'][next_index]
        
        # Chuẩn bị phản hồi với câu hỏi tiếp theo
        updated_chat_state['botMessage'] = next_question['text']
        updated_chat_state['pollOptions'] = [option['text'] for option in next_question['options']]
        
        return updated_chat_state
        
    except Exception as e:
        logger.exception("Error in handle_poll_message", exc_info=e)
        return {
            **chat_state,
            'botMessage': "Xin lỗi, đã xảy ra lỗi khi xử lý câu trả lời của bạn. Vui lòng thử lại."
        }
    
def prepare_detailed_assessment(chat_state, asked_questions, scores, flags, summary_answers=None):
    """
    Chuẩn bị chuyển sang đánh giá chi tiết sau khi đã thu thập đủ thông tin từ trò chuyện tự nhiên
    
    Args:
        chat_state: Dict trạng thái chat hiện tại
        asked_questions: List các câu hỏi đã hỏi
        scores: Dict điểm số
        flags: Dict các cờ
        summary_answers: Dict tóm tắt câu trả lời
        
    Returns:
        Dict trạng thái chat đã cập nhật
    """
    # Xử lý kết quả từ trò chuyện tự nhiên
    category_scores = calculate_natural_conversation_scores(asked_questions, scores)
    
    # Thông báo chuyển tiếp
    transition_message = "Cảm ơn bạn đã chia sẻ. Dựa trên những gì bạn đã nói, tôi muốn đánh giá chi tiết hơn "
    
    # Xác định loại đánh giá chuyên sâu cần thực hiện
    assessment_needed = determine_assessment_needed(category_scores)
    
    # Đảm bảo summary_answers không bị None
    if summary_answers is None:
        summary_answers = {}
    
    # Xử lý nguy cơ tự tử nếu phát hiện
    if flags.get('suicideRisk'):
        return {
            **chat_state,
            'state': CHAT_STATES['SUICIDE_ASSESSMENT'],
            'currentAssessment': 'suicideRiskAssessment',
            'currentQuestionIndex': 0,
            'scores': {
                'initialScreening': category_scores
            },
            'severityLevels': {
                'initialScreening': get_severity_level(category_scores, questionnaires['initialScreening'])
            },
            'flags': flags,
            'naturalConversation': {
                'askedQuestions': asked_questions,
                'scores': scores,
                'summaryAnswers': summary_answers
            },
            'interfaceMode': 'poll',
            'botMessage': "Tôi nhận thấy một số điều bạn đã chia sẻ cho thấy bạn có thể đang gặp khó khăn nghiêm trọng. Tôi muốn hỏi thêm một vài câu hỏi để hiểu rõ hơn. Bây giờ tôi sẽ chuyển sang định dạng có các nút để bạn dễ dàng lựa chọn câu trả lời.\n\n" + questionnaires['suicideRiskAssessment']['questions'][0]['text'],
            'pollOptions': [option['text'] for option in questionnaires['suicideRiskAssessment']['questions'][0]['options']]
        }
    
    # Nếu không cần đánh giá chi tiết, chuyển sang tóm tắt
    if not assessment_needed:
        return {
            **chat_state,
            'state': CHAT_STATES['SUMMARY'],
            'scores': {
                'initialScreening': category_scores
            },
            'severityLevels': {
                'initialScreening': get_severity_level(category_scores, questionnaires['initialScreening'])
            },
            'flags': flags,
            'naturalConversation': {
                'askedQuestions': asked_questions,
                'scores': scores,
                'summaryAnswers': summary_answers
            },
            'interfaceMode': 'chat',
            'botMessage': "Cảm ơn bạn đã chia sẻ. Dựa trên những gì bạn đã nói, tôi có thể cung cấp một số thông tin sơ bộ về trạng thái sức khỏe tâm thần của bạn."
        }
    
    # Chuyển sang đánh giá chi tiết với giao diện poll
    assessment_name = {
        'phq9': 'trầm cảm',
        'gad7': 'lo âu',
        'dass21_stress': 'căng thẳng'
    }.get(assessment_needed, 'sức khỏe tâm thần')
    
    return {
        **chat_state,
        'state': CHAT_STATES['POLL_INTERACTION'],
        'currentAssessment': assessment_needed,
        'currentQuestionIndex': 0,
        'scores': {
            'initialScreening': category_scores
        },
        'severityLevels': {
            'initialScreening': get_severity_level(category_scores, questionnaires['initialScreening'])
        },
        'flags': flags,
        'naturalConversation': {
            'askedQuestions': asked_questions,
            'scores': scores,
            'summaryAnswers': summary_answers
        },
        'interfaceMode': 'poll',
        'botMessage': f"{transition_message}{assessment_name} của bạn. Từ giờ, tôi sẽ chuyển sang định dạng có các nút để bạn dễ dàng lựa chọn câu trả lời.\n\n{questionnaires[assessment_needed]['questions'][0]['text']}",
        'pollOptions': [option['text'] for option in questionnaires[assessment_needed]['questions'][0]['options']]
    }

def calculate_natural_conversation_scores(asked_questions, scores):
    """
    Tính toán điểm số cho từng danh mục từ kết quả trò chuyện tự nhiên
    
    Args:
        asked_questions: List các câu hỏi đã hỏi
        scores: Dict điểm số từng câu hỏi
        
    Returns:
        Dict điểm số theo danh mục (depression, anxiety, stress)
    """
    category_scores = {
        'depression': 0,
        'anxiety': 0,
        'stress': 0
    }
    
    category_counts = {
        'depression': 0,
        'anxiety': 0,
        'stress': 0
    }
    
    # Tính tổng điểm và số câu hỏi cho mỗi danh mục
    for question_id in asked_questions:
        if question_id in scores:
            category = get_question_category(question_id)
            if category in category_scores:
                category_scores[category] += scores[question_id]
                category_counts[category] += 1
    
    # Tính điểm trung bình và nhân với số câu hỏi chuẩn để có thang điểm tương tự
    for category in category_scores:
        if category_counts[category] > 0:
            avg_score = category_scores[category] / category_counts[category]
            
            # Số câu hỏi trong các danh mục chuẩn
            standard_counts = {
                'depression': 4,  # 4 câu hỏi depression trong initialScreening
                'anxiety': 3,     # 3 câu hỏi anxiety trong initialScreening
                'stress': 3       # 3 câu hỏi stress trong initialScreening
            }
            
            # Điều chỉnh thang điểm tương đương với bộ câu hỏi tiêu chuẩn
            category_scores[category] = round(avg_score * standard_counts[category])
    
    return category_scores

def determine_assessment_needed(category_scores):
    """
    Xác định loại đánh giá chi tiết cần thực hiện dựa trên điểm số
    
    Args:
        category_scores: Dict điểm số theo danh mục
        
    Returns:
        String: assessment_id hoặc None nếu không cần đánh giá chi tiết
    """
    # Ngưỡng điểm để quyết định cần đánh giá chi tiết
    thresholds = {
        'depression': 6,  # mild threshold in initialScreening
        'anxiety': 5,     # mild threshold in initialScreening
        'stress': 5       # mild threshold in initialScreening
    }
    
    # Tìm danh mục có điểm cao nhất
    max_category = None
    max_score_relative = -1  # Điểm số tương đối so với ngưỡng
    
    for category, score in category_scores.items():
        relative_score = score / thresholds[category] if thresholds[category] > 0 else 0
        if relative_score > max_score_relative and relative_score >= 1:  # Chỉ xem xét khi điểm >= ngưỡng
            max_score_relative = relative_score
            max_category = category
    
    # Ánh xạ danh mục sang bộ đánh giá tương ứng
    assessment_mapping = {
        'depression': 'phq9',
        'anxiety': 'gad7',
        'stress': 'dass21_stress'
    }
    
    # Trả về id đánh giá chi tiết hoặc None nếu không cần
    return assessment_mapping.get(max_category) if max_category else None

def handle_poll_interaction(chat_state, user_message):
    """
    Xử lý giai đoạn tương tác poll
    
    Args:
        chat_state: Dict trạng thái chat hiện tại
        user_message: String tin nhắn người dùng hoặc index của tùy chọn được chọn
        
    Returns:
        Dict trạng thái chat đã cập nhật
    """
    assessment_id = chat_state.get('currentAssessment')
    if not assessment_id or assessment_id not in questionnaires:
        logger.error(f"Invalid assessment {assessment_id} in poll interaction")
        return {
            **chat_state,
            'botMessage': "Xin lỗi, đã xảy ra lỗi. Hãy thử lại."
        }
    
    assessment = questionnaires[assessment_id]
    current_question_index = chat_state.get('currentQuestionIndex', 0)
    
    if current_question_index >= len(assessment['questions']):
        logger.error(f"Question index {current_question_index} out of range for {assessment_id}")
        return {
            **chat_state,
            'botMessage': "Xin lỗi, đã xảy ra lỗi. Hãy thử lại."
        }
    
    current_question = assessment['questions'][current_question_index]
    
    # Xử lý phản hồi người dùng
    try:
        # Nếu tin nhắn người dùng là chỉ số của tùy chọn đã chọn
        if user_message.isdigit() and 0 <= int(user_message) < len(current_question['options']):
            option_index = int(user_message)
            option_value = current_question['options'][option_index]['value']
        else:
            # Nếu không, phân tích tin nhắn để xác định giá trị
            option_value = parse_response(user_message, current_question)
        
        # Ghi lại phản hồi
        user_responses = chat_state.get('userResponses', {})
        assessment_responses = user_responses.get(assessment_id, {})
        assessment_responses[current_question['id']] = option_value
        
        updated_responses = {
            **user_responses,
            assessment_id: assessment_responses
        }
        
        # Kiểm tra cờ nguy cơ
        updated_flags = dict(chat_state.get('flags', {}))
        if current_question.get('flag') == 'suicide_risk' and option_value >= 3:
            updated_flags['suicideRisk'] = True
        
        # Kiểm tra xem đã hoàn thành bộ câu hỏi chưa
        next_question_index = current_question_index + 1
        
        if next_question_index >= len(assessment['questions']):
            # Tính điểm
            scores = calculate_scores(assessment_responses, assessment)
            severity = get_severity_level(scores, assessment)
            
            # Cập nhật scores và severity
            updated_scores = {
                **chat_state.get('scores', {}),
                assessment_id: scores
            }
            
            updated_severity = {
                **chat_state.get('severityLevels', {}),
                assessment_id: severity
            }
            
            # Cập nhật thêm summaryAnswers để theo dõi
            natural_convo = chat_state.get('naturalConversation', {})
            summary_answers = natural_convo.get('summaryAnswers', {})
            
            # Thêm responses của assessment hiện tại vào summaryAnswers
            for q_id, value in assessment_responses.items():
                summary_answers[q_id] = {
                    'score': value,
                    'response': f"Đã chọn: {option_value}",
                    'answered_at': datetime.datetime.now().isoformat()
                }
            
            # Xác định trạng thái tiếp theo
            if assessment_id == 'suicideRiskAssessment':
                # Nếu đang đánh giá nguy cơ tự tử
                next_state = CHAT_STATES['SUMMARY']
                additional_message = ""
                
                if severity in ['high', 'severe']:
                    additional_message = emergency_message + "\n\n"
                
                return {
                    **chat_state,
                    'state': next_state,
                    'userResponses': updated_responses,
                    'scores': updated_scores,
                    'severityLevels': updated_severity,
                    'flags': updated_flags,
                    'naturalConversation': {
                        **natural_convo,
                        'summaryAnswers': summary_answers
                    },
                    'interfaceMode': 'chat',
                    'botMessage': additional_message + "Cảm ơn bạn đã hoàn thành bộ câu hỏi. Bây giờ chúng ta có thể quay lại trò chuyện và tôi sẽ cung cấp thông tin dựa trên những gì bạn đã chia sẻ."
                }
            
            # Cho đánh giá thông thường
            # Có thể thêm logic để xác định liệu có cần đánh giá bổ sung hay không
            return {
                **chat_state,
                'state': CHAT_STATES['SUMMARY'],
                'userResponses': updated_responses,
                'scores': updated_scores,
                'severityLevels': updated_severity,
                'flags': updated_flags,
                'naturalConversation': {
                    **natural_convo,
                    'summaryAnswers': summary_answers
                },
                'interfaceMode': 'chat',
                'botMessage': "Cảm ơn bạn đã hoàn thành bộ câu hỏi. Bây giờ chúng ta có thể quay lại trò chuyện và tôi sẽ cung cấp một bản tóm tắt dựa trên thông tin bạn đã chia sẻ."
            }
        
        # Nếu chưa hết câu hỏi, hiển thị câu hỏi tiếp theo
        next_question = assessment['questions'][next_question_index]
        
        return {
            **chat_state,
            'currentQuestionIndex': next_question_index,
            'userResponses': updated_responses,
            'flags': updated_flags,
            'botMessage': next_question['text'],
            'pollOptions': [option['text'] for option in next_question['options']]
        }
    except Exception as e:
        logger.exception("Error in handle_poll_interaction", exc_info=e)
        return {
            **chat_state,
            'botMessage': "Xin lỗi, đã xảy ra lỗi khi xử lý câu trả lời của bạn. Vui lòng thử lại hoặc chọn một trong các tùy chọn được cung cấp."
        }

def handle_assessment(chat_state, user_message, assessment_id):
    """
    Xử lý các trạng thái đánh giá (chỉ sử dụng khi cần fallback từ cơ chế mới)
    
    Args:
        chat_state: Dict trạng thái chat hiện tại
        user_message: String tin nhắn người dùng
        assessment_id: ID của bộ đánh giá hiện tại
        
    Returns:
        Dict trạng thái chat đã cập nhật
    """
    try:
        if assessment_id not in questionnaires:
            logger.error(f"Assessment {assessment_id} not found")
            return {
                **chat_state,
                'botMessage': "Xin lỗi, đã xảy ra lỗi trong quá trình đánh giá. Vui lòng thử lại."
            }
        
        assessment = questionnaires[assessment_id]
        current_question_index = chat_state.get('currentQuestionIndex', 0)
        
        if current_question_index >= len(assessment['questions']):
            logger.error(f"Question at index {current_question_index} not found for assessment {assessment_id}")
            return {
                **chat_state,
                'botMessage': "Xin lỗi, đã xảy ra lỗi trong quá trình đánh giá. Vui lòng thử lại."
            }
        
        current_question = assessment['questions'][current_question_index]
        
        # Ghi lại phản hồi của người dùng
        user_responses = chat_state.get('userResponses', {})
        assessment_responses = user_responses.get(assessment_id, {})
        response_value = parse_response(user_message, current_question)
        assessment_responses[current_question['id']] = response_value
        
        updated_responses = {
            **user_responses,
            assessment_id: assessment_responses
        }
        
        # Cập nhật summaryAnswers để theo dõi
        natural_convo = chat_state.get('naturalConversation', {})
        summary_answers = natural_convo.get('summaryAnswers', {})
        
        # Thêm response hiện tại vào summaryAnswers
        summary_answers[current_question['id']] = {
            'score': response_value,
            'response': user_message,
            'answered_at': datetime.datetime.now().isoformat()
        }
        
        # Kiểm tra cờ nguy cơ tự tử
        updated_flags = dict(chat_state.get('flags', {}))
        if current_question.get('flag') == 'suicide_risk' and response_value >= 3:
            updated_flags['suicideRisk'] = True
        
        # Kiểm tra xem đã hoàn thành đánh giá hiện tại chưa
        next_question_index = current_question_index + 1
        
        if next_question_index >= len(assessment['questions']):
            # Tính điểm cho đánh giá này
            scores = calculate_scores(assessment_responses, assessment)
            severity = get_severity_level(scores, assessment)
            
            # Xác định trạng thái tiếp theo
            next_state = determine_next_state(chat_state, assessment, severity, updated_flags)
            
            return {
                **chat_state,
                **next_state,
                'userResponses': updated_responses,
                'scores': {
                    **chat_state.get('scores', {}),
                    assessment_id: scores
                },
                'severityLevels': {
                    **chat_state.get('severityLevels', {}),
                    assessment_id: severity
                },
                'naturalConversation': {
                    **natural_convo,
                    'summaryAnswers': summary_answers
                },
                'flags': updated_flags
            }
        
        # Chuyển sang câu hỏi tiếp theo
        next_question = assessment['questions'][next_question_index]
        
        return {
            **chat_state,
            'currentQuestionIndex': next_question_index,
            'userResponses': updated_responses,
            'naturalConversation': {
                **natural_convo,
                'summaryAnswers': summary_answers
            },
            'flags': updated_flags,
            'botMessage': next_question['text'] + "\n\n" + format_options(next_question.get('options', []))
        }
    except Exception as e:
        logger.exception("Error in handle_assessment", exc_info=e)
        return {
            **chat_state,
            'botMessage': "Xin lỗi, đã xảy ra lỗi trong quá trình đánh giá. Vui lòng thử lại."
        }

def determine_next_state(chat_state, assessment, severity, flags):
    """
    Xác định trạng thái tiếp theo dựa trên kết quả đánh giá
    """
    # Logic giữ nguyên từ phiên bản cũ
    try:
        # Nếu phát hiện nguy cơ tự tử, chuyển sang đánh giá tự tử
        if flags.get('suicideRisk', False) and assessment.get('id') != 'suicideRiskAssessment':
            return {
                'state': CHAT_STATES['SUICIDE_ASSESSMENT'],
                'currentAssessment': 'suicideRiskAssessment',
                'currentQuestionIndex': 0,
                'interfaceMode': 'poll',
                'botMessage': f"Tôi nhận thấy bạn đã đề cập đến suy nghĩ về cái chết hoặc tự làm hại bản thân. Tôi muốn hỏi thêm một vài câu hỏi để hiểu rõ hơn tình hình.\n\n{questionnaires['suicideRiskAssessment']['questions'][0]['text']}",
                'pollOptions': [option['text'] for option in questionnaires['suicideRiskAssessment']['questions'][0]['options']]
            }
        
        if assessment.get('id') == 'suicideRiskAssessment':
            risk_level = severity
            
            if risk_level in ['severe', 'high']:
                return {
                    'state': CHAT_STATES['SUMMARY'],
                    'interfaceMode': 'chat',
                    'botMessage': emergency_message + "\n\nTôi thực sự lo lắng về sự an toàn của bạn dựa trên thông tin bạn đã chia sẻ. Việc tìm kiếm hỗ trợ ngay là rất quan trọng. Bạn không đơn độc, và có những người sẵn sàng giúp đỡ bạn vượt qua giai đoạn khó khăn này."
                }
            
            # Chuyển sang tóm tắt nếu nguy cơ thấp hơn
            return {
                'state': CHAT_STATES['SUMMARY'],
                'interfaceMode': 'chat',
                'botMessage': "Cảm ơn bạn đã trả lời thêm những câu hỏi này. Dựa trên câu trả lời của bạn, tôi có thể cung cấp một số thông tin sơ bộ."
            }
        
        if assessment.get('id') == 'initialScreening':
            # Kiểm tra các danh mục trung bình hoặc nặng
            if isinstance(severity, dict):
                for category, level in severity.items():
                    if level in ['moderate', 'severe']:
                        # Chuyển sang đánh giá chi tiết cho danh mục này
                        next_assessment = assessment.get('nextAssessment', {}).get(category)
                        if next_assessment and next_assessment in questionnaires:
                            category_name = "tâm trạng" if category == 'depression' else "lo âu" if category == 'anxiety' else "căng thẳng"
                            return {
                                'state': CHAT_STATES['POLL_INTERACTION'],  # Chuyển sang giao diện poll
                                'currentAssessment': next_assessment,
                                'currentQuestionIndex': 0,
                                'interfaceMode': 'poll',
                                'botMessage': f"Dựa trên câu trả lời của bạn, tôi muốn hỏi thêm một số câu hỏi cụ thể về {category_name} của bạn.\n\n{questionnaires[next_assessment]['questions'][0]['text']}",
                                'pollOptions': [option['text'] for option in questionnaires[next_assessment]['questions'][0]['options']]
                            }
            
            # Nếu không có vấn đề nghiêm trọng, chuyển sang tóm tắt
            return {
                'state': CHAT_STATES['SUMMARY'],
                'interfaceMode': 'chat',
                'botMessage': "Cảm ơn bạn đã trả lời các câu hỏi. Dựa trên câu trả lời của bạn, tôi có thể cung cấp một số thông tin sơ bộ."
            }
        
        # Cho các đánh giá chi tiết, chuyển sang tóm tắt
        return {
            'state': CHAT_STATES['SUMMARY'],
            'interfaceMode': 'chat',
            'botMessage': "Cảm ơn bạn đã trả lời các câu hỏi này. Bây giờ tôi sẽ cung cấp một bản tóm tắt dựa trên thông tin bạn đã chia sẻ."
        }
    except Exception as e:
        logger.exception("Error in determine_next_state", exc_info=e)
        return {
            'state': CHAT_STATES['SUMMARY'],
            'interfaceMode': 'chat',
            'botMessage': "Cảm ơn bạn đã trả lời các câu hỏi. Tôi sẽ cung cấp một bản tóm tắt dựa trên thông tin bạn đã chia sẻ."
        }

def format_options(options):
    """
    Định dạng hiển thị các lựa chọn
    """
    if not options or not isinstance(options, list):
        logger.warning("Invalid options in format_options")
        return ""
    
    return '\n'.join([f"{option.get('value')}: {option.get('text')}" for option in options])

def parse_response(user_message, question, use_ai=False):
    """
    Hàm trợ giúp phân tích phản hồi người dùng dựa trên loại câu hỏi
    """
    # Logic giữ nguyên từ phiên bản cũ
    if not user_message or not question or 'options' not in question:
        logger.warning("Missing user_message, question, or options in parse_response")
        return 0  # Giá trị mặc định
    
    if use_ai:
        try:
            # Sử dụng import theo yêu cầu
            from utils.contextual_prompt import create_response_classification_prompt
            from utils.together_ai import generate_chat_completion, extract_text_from_response
            
            # Tạo prompt phân loại
            prompt = create_response_classification_prompt(question, question['options'], user_message)
            
            # Tạo API call riêng biệt chỉ cho nhiệm vụ phân loại
            messages = [{"role": "system", "content": "Bạn là trợ lý phân loại câu trả lời. Chỉ trả về giá trị số phù hợp."}, 
                      {"role": "user", "content": prompt}]
            
            ai_response = generate_chat_completion(messages)
            
            if ai_response:
                response_text = extract_text_from_response(ai_response)
                parsed_value = parse_ai_response(response_text)
                
                # Kiểm tra xem giá trị có hợp lệ không
                option_values = [opt.get('value') for opt in question['options']]
                if parsed_value in option_values:
                    return parsed_value
        except Exception as e:
            logger.error(f"Error using AI for response classification: {str(e)}")
    
    # Phương pháp hiện tại nếu AI không được sử dụng hoặc gặp lỗi
    # Đối với tin nhắn dạng số
    try:
        num_value = int(user_message.strip())
        # Kiểm tra xem giá trị có trong phạm vi tùy chọn không
        option_values = [opt.get('value') for opt in question['options']]
        if num_value in option_values:
            return num_value
    except (ValueError, TypeError):
        pass
    
    # Cố gắng khớp với văn bản tùy chọn
    lowercase_message = user_message.lower()
    for option in question['options']:
        if option.get('text', '').lower() in lowercase_message:
            return option.get('value', 0)
    
    # Hỗ trợ phản hồi đơn giản như "có/không"
    if len(question['options']) == 2:
        positive_words = ['có', 'đúng', 'phải', 'vâng', 'ok', 'ừ']
        negative_words = ['không', 'sai', 'ko', 'k', 'no']
        
        for word in positive_words:
            if word in lowercase_message:
                return question['options'][1].get('value', 0)  # Thường là "Có"
        
        for word in negative_words:
            if word in lowercase_message:
                return question['options'][0].get('value', 0)  # Thường là "Không"
    
    # Mặc định giá trị nếu không thể phân tích
    return question['options'][0].get('value', 0)

def parse_natural_response(user_message, question_id):
    """
    Phân tích phản hồi tự nhiên của người dùng và xác định điểm (0-4)
    
    Args:
        user_message: String tin nhắn người dùng
        question_id: ID của câu hỏi hiện tại
        
    Returns:
        Int: Điểm số 0-4
    """
    try:
        # Cố gắng từ AI nếu có thể
        # Xảy ra trong một hàm riêng ngoài phạm vi
        
        # Hàm đơn giản để phân tích tin nhắn
        # Có thể mở rộng với phương pháp học máy hoặc NLP phức tạp hơn
        
        # Tìm các cụm từ biểu thị mức độ
        message = user_message.lower()
        
        # Tìm các biểu thứ rõ ràng về tần suất
        high_frequency = ['luôn luôn', 'rất thường xuyên', 'liên tục', 'hầu hết thời gian', 'hầu như lúc nào cũng', 'chắc chắn']
        medium_high_frequency = ['thường xuyên', 'nhiều lần', 'khá thường xuyên', 'hay', 'thường', 'đúng vậy']
        medium_frequency = ['thỉnh thoảng', 'đôi khi', 'lúc có lúc không', 'thỉnh thoảng có', 'không thường xuyên lắm']
        low_frequency = ['hiếm khi', 'hiếm', 'rất ít khi', 'không mấy khi', 'có nhưng ít']
        never = ['không bao giờ', 'chưa từng', 'không', 'chưa', 'không hề', 'tôi không']
        
        # Kiểm tra các từ phủ định
        has_negation = any(word in message for word in ['không', 'chưa', 'không hề', 'chưa từng', 'không bao giờ'])
        
        # Tìm cụm từ phủ định đặc biệt
        if question_id in ['relax_difficulty', 'lost_interest']:
            # Đối với câu hỏi về khả năng thư giãn, mất hứng thú, phủ định có ý nghĩa ngược lại
            # Ví dụ: "tôi dễ dàng thư giãn" = thấp, "tôi không dễ dàng thư giãn" = cao
            special_positive = ['dễ dàng', 'không khó', 'vẫn duy trì', 'vẫn hứng thú', 'vẫn còn hứng thú']
            if any(term in message for term in special_positive) and not has_negation:
                return 0  # Không khó khăn = điểm thấp
            elif any(term in message for term in special_positive) and has_negation:
                return 3  # Phủ định của không khó khăn = điểm cao
        
        # Tìm chỉ số rõ ràng
        if any(term in message for term in high_frequency):
            return 4
        elif any(term in message for term in medium_high_frequency):
            return 3
        elif any(term in message for term in medium_frequency):
            return 2
        elif any(term in message for term in low_frequency):
            return 1
        elif any(term in message for term in never):
            return 0
        
        # Tìm từ ngữ cảm xúc
        if question_id in ['sad_feelings', 'worthless', 'life_not_worth']:
            # Đối với câu hỏi về cảm xúc tiêu cực
            very_negative = ['rất buồn', 'cực kỳ buồn', 'vô cùng buồn', 'hoàn toàn vô giá trị', 'hoàn toàn vô nghĩa']
            negative = ['buồn', 'chán nản', 'không vui', 'vô giá trị', 'không có ý nghĩa', 'không đáng sống']
            if any(term in message for term in very_negative):
                return 4
            elif any(term in message for term in negative) and not has_negation:
                return 3
        
        # Với câu hỏi về lo âu, hoảng sợ
        if question_id in ['worried', 'panic']:
            anxiety_high = ['rất lo lắng', 'lo lắng quá mức', 'hoảng sợ', 'sợ hãi dữ dội']
            anxiety_med = ['lo lắng', 'lo âu', 'bồn chồn', 'sợ']
            if any(term in message for term in anxiety_high):
                return 4
            elif any(term in message for term in anxiety_med) and not has_negation:
                return 3
        
        # Câu trả lời có hàm ý khẳng định nhưng không rõ mức độ
        affirmative = ['có', 'đúng vậy', 'phải', 'đúng thế', 'vâng', 'ừ']
        if any(word in message for word in affirmative) and not has_negation:
            return 2  # Mức trung bình khi có khẳng định nhưng không rõ mức độ
        
        # Nếu không thể xác định, giả định mức trung bình-thấp
        return 1
    except Exception as e:
        logger.exception("Error in parse_natural_response", exc_info=e)
        return 2  # Mức trung bình-thấp là an toàn khi có lỗi

def create_natural_response(user_message, score, follow_up, transition, next_question):
    """
    Tạo phản hồi tự nhiên từ AI dựa trên câu trả lời của người dùng và câu hỏi tiếp theo
    
    Args:
        user_message: String tin nhắn người dùng
        score: Int điểm số 0-4
        follow_up: String câu hỏi đào sâu (nếu có)
        transition: String câu chuyển tiếp (nếu có)
        next_question: String câu hỏi tiếp theo
        
    Returns:
        String phản hồi tự nhiên
    """
    # Phản hồi đồng cảm dựa trên điểm số
    acknowledgements = {
        0: [
            "Tốt quá, điều đó thật tích cực.",
            "Rất mừng khi nghe bạn nói vậy.",
            "Thật tốt khi biết điều đó.",
        ],
        1: [
            "Tôi hiểu, đôi khi điều đó cũng xảy ra.",
            "Cảm ơn bạn đã chia sẻ điều này.",
            "Điều đó có thể xảy ra với bất kỳ ai."
        ],
        2: [
            "Cảm ơn bạn đã chia sẻ. Điều đó có vẻ là một trải nghiệm không dễ dàng.",
            "Tôi hiểu, điều đó có thể gây khó khăn đôi khi.",
            "Tôi thấy rồi, cảm ơn vì đã chia sẻ thẳng thắn."
        ],
        3: [
            "Tôi rất tiếc khi nghe điều này đang ảnh hưởng đến bạn nhiều như vậy.",
            "Điều đó nghe có vẻ thực sự khó khăn, cảm ơn vì đã tin tưởng chia sẻ.",
            "Tôi đánh giá cao sự cởi mở của bạn về điều này. Nghe có vẻ là một thách thức đáng kể."
        ],
        4: [
            "Cảm ơn bạn vì đã chia sẻ điều gì đó rất khó khăn. Điều bạn đang trải qua nghe thực sự đau đớn.",
            "Tôi thực sự lắng nghe và thấu hiểu điều này rất khó khăn đối với bạn.",
            "Tôi rất tiếc khi nghe điều này đang ảnh hưởng nhiều đến bạn. Bạn rất dũng cảm khi chia sẻ."
        ]
    }
    
    # Chọn một lời thừa nhận ngẫu nhiên dựa trên điểm số
    import random
    acknowledgement = random.choice(acknowledgements.get(score, acknowledgements[2]))
    
    # Tạo phản hồi
    response = acknowledgement
    
    # Thêm câu hỏi đào sâu nếu có và điểm số cao
    if follow_up and score >= 2:
        response += " " + follow_up
        # Nếu có follow-up thì không cần transition ngay
        return response
    
    # Thêm câu chuyển tiếp nếu có
    if transition:
        response += " " + transition
    
    # Thêm câu hỏi tiếp theo
    response += " " + next_question
    
    return response

def handle_summary(chat_state, user_message):
    """
    Xử lý trạng thái tóm tắt
    """
    try:
        # Tạo tóm tắt dựa trên điểm số và mức độ nghiêm trọng
        summary = generate_summary(
            chat_state.get('scores', {}), 
            chat_state.get('severityLevels', {})
        )
        
        return {
            **chat_state,
            'state': CHAT_STATES['RESOURCES'],
            'summary': summary,
            'interfaceMode': 'chat',
            'botMessage': summary + "\n\nBạn có muốn tôi cung cấp thêm thông tin hoặc tài nguyên hỗ trợ không?"
        }
    except Exception as e:
        logger.exception("Error in handle_summary", exc_info=e)
        return {
            **chat_state,
            'state': CHAT_STATES['RESOURCES'],
            'interfaceMode': 'chat',
            'botMessage': "Xin lỗi, đã xảy ra lỗi khi tạo tóm tắt. Bạn có muốn tôi cung cấp thông tin hoặc tài nguyên hỗ trợ không?"
        }

def handle_resources(chat_state, user_message):
    """
    Xử lý trạng thái tài nguyên
    """
    # Logic giữ nguyên từ phiên bản cũ
    try:
        # Kiểm tra nếu người dùng muốn tài nguyên
        positive_words = ['có', 'vâng', 'đồng ý', 'muốn', 'ok', 'ừ', 'được']
        
        if any(word in user_message.lower() for word in positive_words):
            # Xác định tài nguyên phù hợp
            primary_disorder = 'depression'  # Mặc định
            primary_severity = 'mild'  # Mặc định
            
            # Xác định rối loạn chính và mức độ nghiêm trọng
            if chat_state.get('severityLevels', {}).get('initialScreening'):
                initial_screening = chat_state['severityLevels']['initialScreening']
                
                # Tìm danh mục nghiêm trọng nhất
                max_severity = 'minimal'
                
                for category, severity in initial_screening.items():
                    if severity_weight(severity) > severity_weight(max_severity):
                        max_severity = severity
                        primary_disorder = category
                
                primary_severity = max_severity
            
            # Sử dụng đánh giá chi tiết nếu có
            detailed_assessments = [a for a in chat_state.get('severityLevels', {}).keys() 
                                  if a not in ['initialScreening', 'suicideRiskAssessment']]
            
            if detailed_assessments:
                # Lấy đánh giá chi tiết đầu tiên
                assessment_id = detailed_assessments[0]
                
                if assessment_id == 'phq9':
                    primary_disorder = 'depression'
                elif assessment_id == 'gad7':
                    primary_disorder = 'anxiety'
                elif assessment_id == 'dass21_stress':
                    primary_disorder = 'stress'
                
                primary_severity = chat_state['severityLevels'][assessment_id]
            
            # Lấy tài nguyên phù hợp
            resources_list = get_resources_for_severity(primary_disorder, primary_severity)
            resources_message = format_resources_html(resources_list)
            
            return {
                **chat_state,
                'state': CHAT_STATES['DISORDER_INFO'],
                'resources': resources_list,
                'primaryDisorder': primary_disorder,
                'interfaceMode': 'chat',
                'botMessage': resources_message + "\n\nBạn có muốn biết thêm thông tin về " + 
                    ('trầm cảm' if primary_disorder == 'depression' else 
                     'lo âu' if primary_disorder == 'anxiety' else 'căng thẳng') + " không?"
            }
        
# Nếu người dùng không muốn tài nguyên
        return {
            **chat_state,
            'state': CHAT_STATES['CLOSING'],
            'interfaceMode': 'chat',
            'botMessage': "Tôi hiểu. Bạn có câu hỏi nào khác không?"
        }
    except Exception as e:
        logger.exception("Error in handle_resources", exc_info=e)
        return {
            **chat_state,
            'state': CHAT_STATES['CLOSING'],
            'interfaceMode': 'chat',
            'botMessage': "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Bạn có câu hỏi nào khác không?"
        }

def severity_weight(severity):
    """
    Hàm trợ giúp đánh giá mức độ nghiêm trọng
    """
    weights = {
        'minimal': 0,
        'normal': 0,
        'low': 1,
        'mild': 2,
        'moderate': 3,
        'moderatelySevere': 4,
        'severe': 5,
        'high': 5,
        'extremelySevere': 6
    }
    
    return weights.get(severity, 0)

def handle_disorder_info(chat_state, user_message):
    """
    Xử lý trạng thái thông tin rối loạn
    """
    try:
        # Kiểm tra nếu người dùng muốn thông tin thêm
        positive_words = ['có', 'vâng', 'đồng ý', 'muốn', 'ok', 'ừ', 'được']
        
        if any(word in user_message.lower() for word in positive_words):
            disorder_info = format_disorder_info(chat_state.get('primaryDisorder', 'depression'))
            
            return {
                **chat_state,
                'state': CHAT_STATES['CLOSING'],
                'interfaceMode': 'chat',
                'botMessage': disorder_info + "\n\nBạn có câu hỏi nào khác không?"
            }
        
        # Nếu người dùng không muốn thông tin thêm
        return {
            **chat_state,
            'state': CHAT_STATES['CLOSING'],
            'interfaceMode': 'chat',
            'botMessage': "Tôi hiểu. Bạn có câu hỏi nào khác không?"
        }
    except Exception as e:
        logger.exception("Error in handle_disorder_info", exc_info=e)
        return {
            **chat_state,
            'state': CHAT_STATES['CLOSING'],
            'interfaceMode': 'chat',
            'botMessage': "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Bạn có câu hỏi nào khác không?"
        }

def handle_closing(chat_state, user_message):
    """
    Xử lý trạng thái kết thúc
    """
    try:
        # Kiểm tra nếu người dùng có thêm câu hỏi
        positive_words = ['có', 'vâng', 'câu hỏi', 'muốn hỏi']
        
        if any(word in user_message.lower() for word in positive_words):
            return {
                **initialize_chat(),
                'botMessage': "Bạn có câu hỏi gì? Tôi sẵn sàng trợ giúp."
            }
        
        # Nếu không, kết thúc cuộc trò chuyện
        return {
            **chat_state,
            'botMessage': "Cảm ơn bạn đã chia sẻ với tôi hôm nay. Hãy nhớ rằng chăm sóc sức khỏe tâm thần cũng quan trọng như chăm sóc sức khỏe thể chất. Nếu bạn cảm thấy không khỏe, việc tìm kiếm sự hỗ trợ là một bước tích cực.\n\nTôi hy vọng cuộc trò chuyện này đã cung cấp cho bạn một số hiểu biết và tài nguyên hữu ích. Bạn có thể quay lại bất cứ lúc nào nếu bạn muốn nói chuyện thêm.\n\nChúc bạn một ngày tốt lành và hãy nhớ chăm sóc bản thân!"
        }
    except Exception as e:
        logger.exception("Error in handle_closing", exc_info=e)
        return {
            **chat_state,
            'botMessage': "Cảm ơn bạn đã chia sẻ với tôi hôm nay. Chúc bạn một ngày tốt lành và hãy nhớ chăm sóc bản thân!"
        }
    
def parse_ai_response(ai_response_text):
    """
    Trích xuất giá trị số từ phản hồi của AI
    
    Args:
        ai_response_text: Văn bản phản hồi từ AI
        
    Returns:
        int: Giá trị số được trích xuất hoặc 0 nếu không tìm thấy
    """
    try:
        # Thử tìm giá trị trong thẻ <value>
        import re
        value_match = re.search(r'<value>(\d+)</value>', ai_response_text)
        if value_match:
            return int(value_match.group(1))
        
        # Nếu không tìm thấy thẻ, tìm bất kỳ số nào trong văn bản
        number_match = re.search(r'(\d+)', ai_response_text)
        if number_match:
            return int(number_match.group(1))
        
        # Nếu không có số, kiểm tra các từ khóa
        lowercase_response = ai_response_text.lower()
        if any(word in lowercase_response for word in ["không bao giờ", "không", "never"]):
            return 0
        elif any(word in lowercase_response for word in ["hiếm khi", "rarely"]):
            return 1
        elif any(word in lowercase_response for word in ["thỉnh thoảng", "sometimes"]):
            return 2
        elif any(word in lowercase_response for word in ["thường xuyên", "often"]):
            return 3
        elif any(word in lowercase_response for word in ["luôn luôn", "always"]):
            return 4
        
        # Mặc định
        return 0
    except Exception as e:
        logger.error(f"Error parsing AI response: {e}")
        return 0

def generate_summary(scores, severity_levels):
    """
    Tạo tóm tắt từ điểm số
    """
    if not scores or not severity_levels:
        return "## Kết quả đánh giá sơ bộ\n\nKhông có đủ thông tin để cung cấp đánh giá chi tiết. Vui lòng tiếp tục trả lời các câu hỏi để nhận kết quả chính xác hơn."
    
    summary = "## Kết quả đánh giá sơ bộ\n\n"
    found_any_issue = False
    
    # Xử lý sàng lọc ban đầu
    if 'initialScreening' in severity_levels:
        summary += "Dựa trên sàng lọc ban đầu:\n\n"
        
        for category, level in severity_levels['initialScreening'].items():
            category_name = {
                'depression': 'Trầm cảm',
                'anxiety': 'Lo âu',
                'stress': 'Căng thẳng'
            }.get(category, category)
            
            summary += f"- **{category_name}**: {format_severity(level)}\n"
            
            if level != 'minimal':
                found_any_issue = True
        
        summary += "\n"
    
    # Xử lý đánh giá chi tiết
    detailed_assessments = [a for a in severity_levels.keys() 
                            if a not in ['initialScreening', 'suicideRiskAssessment']]
    
    if detailed_assessments:
        summary += "Kết quả đánh giá chi tiết:\n\n"
        
        for assessment_id in detailed_assessments:
            level = severity_levels[assessment_id]
            assessment_name = questionnaires.get(assessment_id, {}).get('name', assessment_id)
            
            summary += f"- **{assessment_name}**: {format_severity(level)}\n"
        
        summary += "\n"
    
    # Xử lý đánh giá nguy cơ tự tử
    if 'suicideRiskAssessment' in severity_levels:
        level = severity_levels['suicideRiskAssessment']
        
        if level in ['high', 'severe']:
            summary += "⚠️ **CẢNH BÁO: Phát hiện nguy cơ tự tử đáng kể** ⚠️\n\n"
            summary += "Vui lòng liên hệ ngay với các dịch vụ hỗ trợ khẩn cấp được liệt kê ở phần cuối.\n\n"
        elif level == 'moderate':
            summary += "⚠️ **Lưu ý: Phát hiện một số dấu hiệu nguy cơ tự tử** ⚠️\n\n"
            summary += "Khuyến nghị tham khảo ý kiến chuyên gia sức khỏe tâm thần.\n\n"
    
    # Thêm lời khuyên chung
    if found_any_issue:
        summary += "### Đề xuất tiếp theo\n\n"
        summary += "Dựa trên đánh giá sơ bộ này, việc tham khảo ý kiến của chuyên gia sức khỏe tâm thần có thể mang lại lợi ích. Họ có thể cung cấp đánh giá toàn diện hơn và thảo luận về các phương án hỗ trợ phù hợp với nhu cầu cụ thể của bạn.\n\n"
    else:
        summary += "### Đề xuất tiếp theo\n\n"
        summary += "Mặc dù bạn không có dấu hiệu đáng kể của các vấn đề sức khỏe tâm thần dựa trên đánh giá sơ bộ này, việc duy trì thói quen chăm sóc bản thân vẫn rất quan trọng. Nếu bạn tiếp tục cảm thấy lo lắng về sức khỏe tâm thần của mình, hãy cân nhắc nói chuyện với chuyên gia chăm sóc sức khỏe.\n\n"
    
    summary += "### Lưu ý quan trọng\n\n"
    summary += "Thông tin này chỉ mang tính chất tham khảo và không phải là chẩn đoán chính thức. Chỉ chuyên gia sức khỏe tâm thần mới có thể đưa ra chẩn đoán chính xác."
    
    return summary

def format_severity(level):
    """
    Định dạng mức độ nghiêm trọng
    """
    if not level:
        return "Không xác định"
    
    severity_map = {
        'minimal': 'Tối thiểu',
        'mild': 'Nhẹ',
        'moderate': 'Trung bình',
        'moderatelySevere': 'Trung bình đến nặng',
        'severe': 'Nặng',
        'extremelySevere': 'Cực kỳ nặng',
        'low': 'Thấp',
        'high': 'Cao',
        'normal': 'Bình thường'
    }
    
    return severity_map.get(level, level)

def format_chat_history(chat_history):
    # Định dạng lịch sử chat để sử dụng trong prompt
    formatted_history = ""
    for msg in chat_history:
        role = "User" if msg.get('role') == 'user' else "Assistant"
        formatted_history += f"{role}: {msg.get('content', '')}\n"
    return formatted_history

def handle_greeting(chat_state, user_message):
    """
    Xử lý trạng thái chào hỏi ban đầu và chuyển sang thu thập vấn đề
    """
    # Phân tích tin nhắn đầu tiên để hiểu mục đích người dùng tìm đến dịch vụ
    initial_response = "Cảm ơn bạn đã chia sẻ. Tôi hiểu việc chia sẻ những vấn đề cá nhân không phải lúc nào cũng dễ dàng. Hãy trò chuyện thêm để tôi có thể hiểu rõ hơn trải nghiệm của bạn. Bạn có thể chia sẻ thêm về những gì bạn đang cảm thấy không?"
    
    # Lưu trữ lịch sử tin nhắn
    message_history = [
        {'role': 'assistant', 'content': chat_state.get('botMessage', '')},
        {'role': 'user', 'content': user_message}
    ]
    
    return {
        **chat_state,
        'state': CHAT_STATES['COLLECTING_ISSUE'],
        'messageHistory': message_history,
        'botMessage': initial_response
    }


def handle_collecting_issue(chat_state, user_message):
    """
    Thu thập vấn đề từ người dùng và chuyển sang trò chuyện tự nhiên
    """
    # Cập nhật lịch sử tin nhắn
    message_history = chat_state.get('messageHistory', [])
    message_history.append({'role': 'user', 'content': user_message})
    
    # Phân tích vấn đề để xác định câu hỏi đầu tiên phù hợp
    initial_question_id = determine_initial_question(user_message)
    if not initial_question_id:
        initial_question_id = QUESTION_IDS[0]  # Mặc định bắt đầu với câu hỏi đầu tiên
    
    # Lấy câu hỏi ngẫu nhiên từ tập câu hỏi về chủ đề đã chọn
    initial_question = get_random_question(initial_question_id)
    
    # Tạo phản hồi tự nhiên
    response = f"Cảm ơn bạn đã chia sẻ điều đó. Tôi có thể hiểu việc này khá khó khăn với bạn. {initial_question}"
    
    # Cập nhật lịch sử với phản hồi của trợ lý
    message_history.append({'role': 'assistant', 'content': response})
    
    return {
        **chat_state,
        'state': CHAT_STATES['NATURAL_CONVERSATION'],
        'currentQuestionId': initial_question_id,
        'naturalConversation': {
            'askedQuestions': [initial_question_id],
            'scores': {},
            'summaryAnswers': {}
        },
        'messageHistory': message_history,
        'interfaceMode': 'chat',
        'botMessage': response
    }


def determine_initial_question(user_message):
    """
    Xác định câu hỏi đầu tiên phù hợp dựa trên vấn đề người dùng đề cập
    """
    message = user_message.lower()
    
    # Các từ khóa liên quan đến các chủ đề
    if any(word in message for word in ['mệt mỏi', 'kiệt sức', 'uể oải', 'không có năng lượng']):
        return 'feeling_tired'
    elif any(word in message for word in ['lo lắng', 'lo âu', 'căng thẳng', 'sợ hãi', 'bồn chồn']):
        return 'worried'
    elif any(word in message for word in ['buồn', 'chán nản', 'trầm cảm', 'không vui']):
        return 'sad_feelings'
    elif any(word in message for word in ['mất hứng thú', 'không còn thích', 'không quan tâm']):
        return 'lost_interest'
    elif any(word in message for word in ['vô giá trị', 'không đáng', 'thất bại', 'tệ']):
        return 'worthless'
    elif any(word in message for word in ['không muốn sống', 'muốn chết', 'kết thúc cuộc sống']):
        return 'life_not_worth'
    elif any(word in message for word in ['khó ngủ', 'mất ngủ', 'ngủ không ngon', 'ngủ quá nhiều']):
        return 'sleep_issues'
    elif any(word in message for word in ['ăn không ngon', 'chán ăn', 'ăn quá nhiều']):
        return 'eating_issues'
    elif any(word in message for word in ['khó thư giãn', 'không nghỉ ngơi được']):
        return 'relax_difficulty'
    elif any(word in message for word in ['hoảng sợ', 'hoảng loạn', 'sợ hãi đột ngột']):
        return 'panic'
    
    # Nếu không tìm thấy từ khóa nào, mặc định bắt đầu với feeling_tired
    return 'feeling_tired'


def evaluate_conversation_for_question(chat_history, question_id):
    """
    Sử dụng AI để đánh giá mức độ của vấn đề từ lịch sử trò chuyện
    """
    try:
        # Tạo prompt đánh giá
        from utils.contextual_prompt import create_evaluation_prompt
        from utils.together_ai import generate_chat_completion, extract_text_from_response
        
        # Tạo prompt đánh giá chuyên biệt
        prompt = create_evaluation_prompt(chat_history, question_id)
        
        # Gọi API với context khác để đánh giá
        evaluation_messages = [
            {"role": "system", "content": "Bạn là trợ lý đánh giá cuộc trò chuyện. Nhiệm vụ của bạn là đánh giá mức độ nghiêm trọng của vấn đề."},
            {"role": "user", "content": prompt}
        ]
        
        ai_response = generate_chat_completion(evaluation_messages)
        
        if ai_response:
            response_text = extract_text_from_response(ai_response)
            
            # Cố gắng tìm số từ 0-4 trong phản hồi
            import re
            match = re.search(r'[0-4]', response_text)
            if match:
                return int(match.group(0))
            
            # Phân tích văn bản nếu không tìm thấy số
            response_lower = response_text.lower()
            if any(term in response_lower for term in ["không bao giờ", "không", "không hề"]):
                return 0
            elif any(term in response_lower for term in ["hiếm khi", "nhẹ", "ít khi"]):
                return 1
            elif any(term in response_lower for term in ["thỉnh thoảng", "trung bình", "đôi khi"]):
                return 2
            elif any(term in response_lower for term in ["thường xuyên", "đáng kể", "khá thường xuyên"]):
                return 3
            elif any(term in response_lower for term in ["luôn luôn", "nghiêm trọng", "rất thường xuyên"]):
                return 4
        
        # Mặc định mức trung bình
        return 2
    except Exception as e:
        logger.exception(f"Error evaluating conversation for question {question_id}", exc_info=e)
        return 2  # Giá trị an toàn


def handle_natural_conversation(chat_state, user_message):
    """
    Xử lý trò chuyện tự nhiên với AI, tạo cảm giác tự nhiên không giống khảo sát
    """
    try:
        # Lấy thông tin từ trạng thái hiện tại
        natural_convo = chat_state.get('naturalConversation', {})
        asked_questions = natural_convo.get('askedQuestions', [])
        scores = natural_convo.get('scores', {})
        summary_answers = natural_convo.get('summaryAnswers', {})
        
        # Cập nhật lịch sử tin nhắn
        message_history = chat_state.get('messageHistory', [])
        message_history.append({'role': 'user', 'content': user_message})
        
        # Xử lý câu hỏi hiện tại
        current_question_id = chat_state.get('currentQuestionId')
        
        # Đánh giá câu trả lời cho câu hỏi trước đó
        if current_question_id:
            # Lưu câu trả lời vào summary
            summary_answers[current_question_id] = {
                'response': user_message,
                'answered_at': datetime.datetime.now().isoformat()
            }
            
            # Đếm số lần hỏi về chủ đề này
            topic_attempts = sum(1 for q in asked_questions if q == current_question_id)
            
            # Nếu hỏi lần thứ hai trở lên, sử dụng AI để đánh giá
            if topic_attempts >= 1:
                try:
                    score = evaluate_conversation_for_question(message_history, current_question_id)
                    scores[current_question_id] = score
                    summary_answers[current_question_id]['score'] = score
                    
                    # Kiểm tra nguy cơ tự tử
                    if has_risk_flag(current_question_id) == 'suicide_risk' and score >= 3:
                        updated_flags = dict(chat_state.get('flags', {}))
                        updated_flags['suicideRisk'] = True
                        
                        return {
                            **chat_state,
                            'state': CHAT_STATES['SUICIDE_ASSESSMENT'],
                            'currentAssessment': 'suicideRiskAssessment',
                            'currentQuestionIndex': 0,
                            'flags': updated_flags,
                            'messageHistory': message_history,
                            'interfaceMode': 'poll',
                            'botMessage': "Tôi rất quan tâm đến những gì bạn vừa chia sẻ. Tôi muốn hỏi bạn một vài câu hỏi cụ thể hơn. Tôi sẽ chuyển sang định dạng có các nút để bạn dễ dàng lựa chọn.\n\n" + questionnaires['suicideRiskAssessment']['questions'][0]['text'],
                            'pollOptions': [option['text'] for option in questionnaires['suicideRiskAssessment']['questions'][0]['options']]
                        }
                except Exception as e:
                    logger.error(f"Error evaluating response: {str(e)}")
        
        # Xác định câu hỏi tiếp theo
        next_question_id = get_next_question(current_question_id, scores, asked_questions)
        
        # Nếu không còn câu hỏi, chuyển sang đánh giá chi tiết
        if not next_question_id:
            # Đánh giá tất cả câu hỏi còn thiếu
            for q_id in asked_questions:
                if q_id not in scores:
                    scores[q_id] = evaluate_conversation_for_question(message_history, q_id)
            
            return prepare_detailed_assessment(
                chat_state,
                asked_questions,
                scores,
                chat_state.get('flags', {'suicideRisk': False}),
                summary_answers
            )
        
        # Thêm câu hỏi tiếp theo vào danh sách đã hỏi
        if next_question_id not in asked_questions:
            asked_questions.append(next_question_id)
        
        # Kiểm tra số lần đã hỏi về chủ đề này
        next_topic_attempts = sum(1 for q in asked_questions if q == next_question_id)
        
        # Tạo phản hồi tự nhiên
        bot_message = ""
        
        # Nếu đã hỏi 2 lần mà chưa đánh giá được, hỏi trực tiếp
        if next_topic_attempts >= 2 and next_question_id not in scores:
            explicit_rating = get_random_question(next_question_id, "explicit_rating")
            if explicit_rating:
                bot_message = f"Cảm ơn bạn đã chia sẻ. Để hiểu rõ hơn, {explicit_rating}"
            else:
                # Fallback nếu không có explicit_rating
                bot_message = f"Cảm ơn bạn đã chia sẻ. {get_random_question(next_question_id)}"
        else:
            # Tạo phản hồi tự nhiên
            acknowledgement = random.choice([
                "Cảm ơn bạn đã chia sẻ.",
                "Tôi hiểu điều đó có thể khó khăn.",
                "Tôi đánh giá cao sự cởi mở của bạn."
            ])
            
            # Thêm follow-up nếu cần
            follow_up = ""
            if current_question_id == next_question_id and random.random() < 0.7:
                follow_up = get_random_question(current_question_id, "follow_ups") or ""
            
            # Thêm câu chuyển tiếp nếu chuyển chủ đề
            transition = ""
            if current_question_id != next_question_id:
                transition = get_random_question(current_question_id, "transitions") or ""
            
            # Câu hỏi tiếp theo
            next_question = get_random_question(next_question_id)
            
            # Kết hợp các phần
            bot_message = acknowledgement
            if follow_up:
                bot_message += " " + follow_up
            if transition:
                bot_message += " " + transition
            bot_message += " " + next_question
        
        # Cập nhật lịch sử
        message_history.append({'role': 'assistant', 'content': bot_message})
        
        # Kiểm tra đã đủ thông tin cho sàng lọc ban đầu chưa
        if has_sufficient_screening(asked_questions):
            # Đánh giá tất cả câu hỏi còn thiếu
            for q_id in asked_questions:
                if q_id not in scores:
                    scores[q_id] = evaluate_conversation_for_question(message_history, q_id)
            
            return prepare_detailed_assessment(
                chat_state,
                asked_questions,
                scores,
                chat_state.get('flags', {'suicideRisk': False}),
                summary_answers
            )
        
        # Cập nhật trạng thái
        return {
            **chat_state,
            'currentQuestionId': next_question_id,
            'naturalConversation': {
                'askedQuestions': asked_questions,
                'scores': scores,
                'summaryAnswers': summary_answers
            },
            'messageHistory': message_history,
            'botMessage': bot_message
        }
    except Exception as e:
        logger.exception("Error in handle_natural_conversation", exc_info=e)
        return {
            **chat_state,
            'botMessage': "Xin lỗi, đã xảy ra lỗi khi xử lý tin nhắn của bạn. Bạn có thể chia sẻ thêm về những gì bạn đang cảm nhận không?"
        }