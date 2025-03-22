"""
Logic điều khiển luồng chat
Chuyển đổi từ chat-logic.js sang Python
"""

import logging
from data.questionnaires import questionnaires, emergency_message
from utils.scoring import calculate_scores, get_severity_level, check_risk_flags
from data.resources import get_resources_for_severity, format_resources_message
from data.diagnostic import format_disorder_info

logger = logging.getLogger(__name__)

# Trạng thái chat
CHAT_STATES = {
    'GREETING': 'greeting',
    'COLLECTING_ISSUE': 'collecting_issue',
    'INITIAL_SCREENING': 'initial_screening',
    'DETAILED_ASSESSMENT': 'detailed_assessment',
    'ADDITIONAL_ASSESSMENT': 'additional_assessment',
    'SUICIDE_ASSESSMENT': 'suicide_assessment',
    'SUMMARY': 'summary',
    'RESOURCES': 'resources',
    'DISORDER_INFO': 'disorder_info',
    'CLOSING': 'closing'
}

def initialize_chat():
    """
    Khởi tạo trạng thái chat
    """
    return {
        'state': CHAT_STATES['GREETING'],
        'currentAssessment': None,
        'currentQuestionIndex': 0,
        'assessments': {},
        'userResponses': {},
        'scores': {},
        'severityLevels': {},
        'flags': {
            'suicideRisk': False
        },
        'botMessage': "Xin chào! Tôi là một trợ lý AI được thiết kế để hỗ trợ sàng lọc sức khỏe tâm thần. Tôi sẽ hỏi bạn một số câu hỏi để hiểu hơn về cảm xúc và trải nghiệm của bạn. Cuộc trò chuyện này hoàn toàn riêng tư và chỉ nhằm mục đích cung cấp thông tin tham khảo. Tôi không phải là chuyên gia y tế và không thay thế cho tư vấn chuyên nghiệp.\n\nTrước khi bắt đầu, bạn có thể cho tôi biết lý do bạn tìm đến dịch vụ này hôm nay không?"
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

    state = chat_state.get('state')
    
    if state == CHAT_STATES['GREETING']:
        return handle_greeting(chat_state, user_message)
    
    elif state == CHAT_STATES['COLLECTING_ISSUE']:
        return handle_collecting_issue(chat_state, user_message)
    
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

def handle_greeting(chat_state, user_message):
    """
    Xử lý trạng thái chào hỏi
    """
    return {
        **chat_state,
        'state': CHAT_STATES['COLLECTING_ISSUE'],
        'botMessage': "Cảm ơn bạn đã liên hệ. Tôi hiểu rằng việc chia sẻ có thể khó khăn, và tôi đánh giá cao sự cởi mở của bạn. Bạn có thể cho tôi biết thêm về những gì bạn đang trải qua không? Điều gì khiến bạn tìm kiếm hỗ trợ vào lúc này?"
    }

def handle_collecting_issue(chat_state, user_message):
    """
    Xử lý trạng thái thu thập vấn đề
    """
    return {
        **chat_state,
        'state': CHAT_STATES['INITIAL_SCREENING'],
        'currentAssessment': 'initialScreening',
        'currentQuestionIndex': 0,
        'userIssue': user_message,
        'botMessage': "Cảm ơn bạn đã chia sẻ. Bây giờ, tôi sẽ hỏi bạn một số câu hỏi về cảm xúc và trải nghiệm của bạn trong 2 tuần qua để hiểu rõ hơn về tình hình. Vui lòng trả lời từ 0-4 tương ứng với mức độ:\n\n0: Không bao giờ\n1: Hiếm khi\n2: Thỉnh thoảng\n3: Thường xuyên\n4: Luôn luôn\n\nCâu hỏi đầu tiên: " + questionnaires['initialScreening']['questions'][0]['text']
    }

def handle_assessment(chat_state, user_message, assessment_id):
    """
    Xử lý các trạng thái đánh giá
    
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
        assessment_responses[current_question['id']] = parse_response(user_message, current_question)
        
        updated_responses = {
            **user_responses,
            assessment_id: assessment_responses
        }
        
        # Kiểm tra cờ nguy cơ tự tử
        updated_flags = dict(chat_state.get('flags', {}))
        if current_question.get('flag') == 'suicide_risk' and parse_response(user_message, current_question) >= 3:
            updated_flags['suicideRisk'] = True
        
        # Kiểm tra xem đã hoàn thành đánh giá hiện tại chưa
        if current_question_index >= len(assessment['questions']) - 1:
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
                'flags': updated_flags
            }
        
        # Chuyển sang câu hỏi tiếp theo
        next_question_index = current_question_index + 1
        next_question = assessment['questions'][next_question_index]
        
        return {
            **chat_state,
            'currentQuestionIndex': next_question_index,
            'userResponses': updated_responses,
            'flags': updated_flags,
            'botMessage': next_question['text'] + "\n\n" + format_options(next_question.get('options', []))
        }
    except Exception as e:
        logger.exception("Error in handle_assessment", exc_info=e)
        return {
            **chat_state,
            'botMessage': "Xin lỗi, đã xảy ra lỗi trong quá trình đánh giá. Vui lòng thử lại."
        }

def format_options(options):
    """
    Định dạng hiển thị các lựa chọn
    """
    if not options or not isinstance(options, list):
        logger.warning("Invalid options in format_options")
        return ""
    
    return '\n'.join([f"{option.get('value')}: {option.get('text')}" for option in options])

def parse_response(user_message, question):
    """
    Hàm trợ giúp phân tích phản hồi người dùng dựa trên loại câu hỏi
    
    Args:
        user_message: String tin nhắn người dùng
        question: Dict thông tin câu hỏi
        
    Returns:
        Giá trị phản hồi (int)
    """
    if not user_message or not question or 'options' not in question:
        logger.warning("Missing user_message, question, or options in parse_response")
        return 0  # Giá trị mặc định
    
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

def determine_next_state(chat_state, assessment, severity, flags):
    """
    Xác định trạng thái tiếp theo dựa trên kết quả đánh giá
    
    Args:
        chat_state: Dict trạng thái chat hiện tại
        assessment: Dict thông tin bộ đánh giá
        severity: Mức độ nghiêm trọng
        flags: Dict các cờ
        
    Returns:
        Dict cập nhật cho trạng thái tiếp theo
    """
    try:
        # Nếu phát hiện nguy cơ tự tử, chuyển sang đánh giá tự tử
        if flags.get('suicideRisk', False) and assessment.get('id') != 'suicideRiskAssessment':
            return {
                'state': CHAT_STATES['SUICIDE_ASSESSMENT'],
                'currentAssessment': 'suicideRiskAssessment',
                'currentQuestionIndex': 0,
                'botMessage': f"Tôi nhận thấy bạn đã đề cập đến suy nghĩ về cái chết hoặc tự làm hại bản thân. Tôi muốn hỏi thêm một vài câu hỏi để hiểu rõ hơn tình hình.\n\n{questionnaires['suicideRiskAssessment']['questions'][0]['text']}\n\n{format_options(questionnaires['suicideRiskAssessment']['questions'][0]['options'])}"
            }
        
        if assessment.get('id') == 'suicideRiskAssessment':
            risk_level = severity
            
            if risk_level in ['severe', 'high']:
                return {
                    'state': CHAT_STATES['SUMMARY'],
                    'botMessage': emergency_message + "\n\nTôi thực sự lo lắng về sự an toàn của bạn dựa trên thông tin bạn đã chia sẻ. Việc tìm kiếm hỗ trợ ngay là rất quan trọng. Bạn không đơn độc, và có những người sẵn sàng giúp đỡ bạn vượt qua giai đoạn khó khăn này."
                }
            
            # Chuyển sang tóm tắt nếu nguy cơ thấp hơn
            return {
                'state': CHAT_STATES['SUMMARY'],
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
                                'state': CHAT_STATES['DETAILED_ASSESSMENT'],
                                'currentAssessment': next_assessment,
                                'currentQuestionIndex': 0,
                                'botMessage': f"Dựa trên câu trả lời của bạn, tôi muốn hỏi thêm một số câu hỏi cụ thể về {category_name} của bạn.\n\n{questionnaires[next_assessment]['questions'][0]['text']}\n\n{format_options(questionnaires[next_assessment]['questions'][0]['options'])}"
                            }
            
            # Nếu không có vấn đề nghiêm trọng, chuyển sang tóm tắt
            return {
                'state': CHAT_STATES['SUMMARY'],
                'botMessage': "Cảm ơn bạn đã trả lời các câu hỏi. Dựa trên câu trả lời của bạn, tôi có thể cung cấp một số thông tin sơ bộ."
            }
        
        # Cho các đánh giá chi tiết, chuyển sang tóm tắt
        return {
            'state': CHAT_STATES['SUMMARY'],
            'botMessage': "Cảm ơn bạn đã trả lời các câu hỏi này. Bây giờ tôi sẽ cung cấp một bản tóm tắt dựa trên thông tin bạn đã chia sẻ."
        }
    except Exception as e:
        logger.exception("Error in determine_next_state", exc_info=e)
        return {
            'state': CHAT_STATES['SUMMARY'],
            'botMessage': "Cảm ơn bạn đã trả lời các câu hỏi. Tôi sẽ cung cấp một bản tóm tắt dựa trên thông tin bạn đã chia sẻ."
        }

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
            'botMessage': summary + "\n\nBạn có muốn tôi cung cấp thêm thông tin hoặc tài nguyên hỗ trợ không?"
        }
    except Exception as e:
        logger.exception("Error in handle_summary", exc_info=e)
        return {
            **chat_state,
            'state': CHAT_STATES['RESOURCES'],
            'botMessage': "Xin lỗi, đã xảy ra lỗi khi tạo tóm tắt. Bạn có muốn tôi cung cấp thông tin hoặc tài nguyên hỗ trợ không?"
        }

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

def handle_resources(chat_state, user_message):
    """
    Xử lý trạng thái tài nguyên
    """
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
            resources_message = format_resources_message(resources_list)
            
            return {
                **chat_state,
                'state': CHAT_STATES['DISORDER_INFO'],
                'resources': resources_list,
                'primaryDisorder': primary_disorder,
                'botMessage': resources_message + "\n\nBạn có muốn biết thêm thông tin về " + 
                    ('trầm cảm' if primary_disorder == 'depression' else 
                     'lo âu' if primary_disorder == 'anxiety' else 'căng thẳng') + " không?"
            }
        
        # Nếu người dùng không muốn tài nguyên
        return {
            **chat_state,
            'state': CHAT_STATES['CLOSING'],
            'botMessage': "Tôi hiểu. Bạn có câu hỏi nào khác không?"
        }
    except Exception as e:
        logger.exception("Error in handle_resources", exc_info=e)
        return {
            **chat_state,
            'state': CHAT_STATES['CLOSING'],
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
                'botMessage': disorder_info + "\n\nBạn có câu hỏi nào khác không?"
            }
        
        # Nếu người dùng không muốn thông tin thêm
        return {
            **chat_state,
            'state': CHAT_STATES['CLOSING'],
            'botMessage': "Tôi hiểu. Bạn có câu hỏi nào khác không?"
        }
    except Exception as e:
        logger.exception("Error in handle_disorder_info", exc_info=e)
        return {
            **chat_state,
            'state': CHAT_STATES['CLOSING'],
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