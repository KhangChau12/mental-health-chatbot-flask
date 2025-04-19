"""
Logic xử lý poll thuần túy cho phiên bản Logic
Tập trung vào trải nghiệm trắc nghiệm không có chat
"""

import logging
import uuid
import datetime
from data.questionnaires import questionnaires, emergency_message
from utils.scoring import calculate_scores, get_severity_level, check_risk_flags
from data.resources import get_resources_for_severity, format_resources_html
from data.diagnostic import format_disorder_info

logger = logging.getLogger(__name__)

# Trạng thái poll
POLL_STATES = {
    'GREETING': 'greeting',
    'INITIAL_SCREENING': 'initial_screening',
    'RESULTS_PREVIEW': 'results_preview',  # Trạng thái mới
    'DETAILED_ASSESSMENT': 'detailed_assessment',
    'ADDITIONAL_ASSESSMENT': 'additional_assessment',
    'SUICIDE_ASSESSMENT': 'suicide_assessment',
    'SUMMARY': 'summary',
    'RESOURCES': 'resources'
}

def initialize_poll():
    """
    Khởi tạo trạng thái poll
    
    Returns:
        dict: Trạng thái khảo sát ban đầu
    """
    return {
        'sessionId': str(uuid.uuid4()),
        'state': POLL_STATES['GREETING'],
        'currentAssessment': None,
        'currentQuestionIndex': 0,
        'totalQuestions': 0,
        'userResponses': {},
        'scores': {},
        'severityLevels': {},
        'flags': {
            'suicideRisk': False
        }
    }

def start_poll():
    """
    Bắt đầu luồng poll với sàng lọc ban đầu
    
    Returns:
        dict: Thông tin cho câu hỏi đầu tiên và trạng thái poll
    """
    # Khởi tạo trạng thái poll
    poll_state = initialize_poll()
    
    # Cập nhật trạng thái
    poll_state['state'] = POLL_STATES['INITIAL_SCREENING']
    poll_state['currentAssessment'] = 'initialScreening'
    poll_state['currentQuestionIndex'] = 0
    poll_state['totalQuestions'] = len(questionnaires['initialScreening']['questions'])
    
    # Lấy câu hỏi đầu tiên
    first_question = questionnaires['initialScreening']['questions'][0]
    chart_data = []

    return {
        'chatState': poll_state,
        'question': first_question['text'],
        'options': [option['text'] for option in first_question['options']],
        'chartData': chart_data
    }

def process_poll_response(poll_state, response, details=None):
    """
    Xử lý phản hồi từ người dùng trong luồng poll
    
    Args:
        poll_state (dict): Trạng thái poll hiện tại
        response (str): Phản hồi của người dùng (thường là chỉ số của tùy chọn)
        details (str, optional): Chi tiết bổ sung do người dùng cung cấp
        
    Returns:
        dict: Thông tin cho câu hỏi tiếp theo hoặc kết quả và trạng thái poll mới
    """
    if poll_state.get('state') == POLL_STATES['RESULTS_PREVIEW']:
        return handle_results_preview(poll_state, response)
    
    if not poll_state:
        logger.error("Missing poll state in process_poll_response")
        return {'error': "Trạng thái không hợp lệ"}
    
    # Lấy thông tin assessment hiện tại
    assessment_id = poll_state.get('currentAssessment')
    if not assessment_id or assessment_id not in questionnaires:
        logger.error(f"Invalid assessment {assessment_id} in process_poll_response")
        return {'error': "Đánh giá không hợp lệ"}
    
    assessment = questionnaires[assessment_id]
    current_index = poll_state.get('currentQuestionIndex', 0)
    
    # Kiểm tra chỉ số câu hỏi hợp lệ
    if current_index < 0 or current_index >= len(assessment['questions']):
        logger.error(f"Invalid question index {current_index} for assessment {assessment_id}")
        return {'error': "Chỉ số câu hỏi không hợp lệ"}
    
    current_question = assessment['questions'][current_index]
    
    # Xử lý phản hồi
    try:
        option_index = int(response)
        if option_index < 0 or option_index >= len(current_question['options']):
            logger.error(f"Invalid option index {option_index}")
            return {'error': "Tùy chọn không hợp lệ"}
        
        option_value = current_question['options'][option_index]['value']
        
        # Ghi lại phản hồi
        user_responses = poll_state.get('userResponses', {})
        assessment_responses = user_responses.get(assessment_id, {})
        assessment_responses[current_question['id']] = option_value
        
        updated_responses = {
            **user_responses,
            assessment_id: assessment_responses
        }
        
        # Cập nhật trạng thái poll
        updated_poll_state = {
            **poll_state,
            'userResponses': updated_responses
        }
        
        # Kiểm tra cờ nguy cơ
        updated_flags = dict(poll_state.get('flags', {}))
        if current_question.get('flag') == 'suicide_risk' and option_value >= 3:
            updated_flags['suicideRisk'] = True
            updated_poll_state['flags'] = updated_flags
        
        # Chuyển sang câu hỏi tiếp theo
        next_index = current_index + 1
        
        # Kiểm tra xem đã hoàn thành assessment hiện tại chưa
        if next_index >= len(assessment['questions']):
            # Tính điểm và mức độ nghiêm trọng
            scores = calculate_scores(assessment_responses, assessment)
            severity = get_severity_level(scores, assessment)
            
            # Cập nhật điểm và mức độ
            updated_poll_state['scores'] = {
                **poll_state.get('scores', {}),
                assessment_id: scores
            }
            
            updated_poll_state['severityLevels'] = {
                **poll_state.get('severityLevels', {}),
                assessment_id: severity
            }
            
            # Xác định trạng thái tiếp theo
            next_state = determine_next_state(updated_poll_state, assessment, severity, updated_flags)
            
            # Nếu chuyển sang summary, trả về kết quả
            if next_state['state'] == POLL_STATES['SUMMARY']:
                # Tạo tóm tắt kết quả
                summary_html = generate_summary_html(updated_poll_state['scores'], updated_poll_state['severityLevels'])
                
                return {
                    'chatState': {
                        **updated_poll_state,
                        **next_state
                    },
                    'showResults': True,
                    'resultsHtml': summary_html
                }
            
            # Nếu chuyển sang assessment khác, cập nhật câu hỏi đầu tiên
            updated_poll_state.update(next_state)
            next_assessment = updated_poll_state['currentAssessment']
            
            if next_assessment and next_assessment in questionnaires:
                next_question = questionnaires[next_assessment]['questions'][0]
                updated_poll_state['totalQuestions'] = len(questionnaires[next_assessment]['questions'])
                
                return {
                    'chatState': updated_poll_state,
                    'question': next_question['text'],
                    'options': [option['text'] for option in next_question['options']]
                }
        else:
            # Cập nhật chỉ số câu hỏi và lấy câu hỏi tiếp theo
            updated_poll_state['currentQuestionIndex'] = next_index
            next_question = assessment['questions'][next_index]
            
            return {
                'chatState': updated_poll_state,
                'question': next_question['text'],
                'options': [option['text'] for option in next_question['options']]
            }
    except Exception as e:
        logger.exception("Error in process_poll_response", exc_info=e)
        return {'error': f"Lỗi xử lý phản hồi: {str(e)}"}

def determine_next_state(poll_state, assessment, severity, flags):
    """
    Xác định trạng thái tiếp theo dựa trên kết quả đánh giá
    """
    # Nếu phát hiện nguy cơ tự tử, chuyển sang đánh giá tự tử
    if flags.get('suicideRisk', False) and assessment.get('id') != 'suicideRiskAssessment':
        return {
            'state': POLL_STATES['SUICIDE_ASSESSMENT'],
            'currentAssessment': 'suicideRiskAssessment',
            'currentQuestionIndex': 0,
            'totalQuestions': len(questionnaires['suicideRiskAssessment']['questions'])
        }
    
    # Nếu đã làm đánh giá tự tử, chuyển sang tóm tắt
    if assessment.get('id') == 'suicideRiskAssessment':
        return {
            'state': POLL_STATES['SUMMARY']
        }
    
    # Xử lý kết quả từ sàng lọc ban đầu
    if assessment.get('id') == 'initialScreening':
        # Thay vì kiểm tra mức độ ngay, chuyển sang trang kết quả sơ bộ
        return {
            'state': POLL_STATES['RESULTS_PREVIEW']
        }
    
    # Nếu đang ở trạng thái results_preview, phản hồi này là từ nút "Tiếp tục"
    if poll_state.get('state') == POLL_STATES['RESULTS_PREVIEW']:
        # Kiểm tra các danh mục trung bình hoặc nặng
        if isinstance(severity, dict):
            # Thêm log để kiểm tra severity
            print(f"Severity levels: {severity}")
            
            # Thay đổi: Ưu tiên lo âu nếu có mức độ nặng/trung bình
            for priority_category in ['anxiety', 'depression', 'stress']:
                if priority_category in severity:
                    level = severity[priority_category]
                    if level in ['moderate', 'severe', 'nặng']:
                        # Lấy đánh giá chi tiết tương ứng
                        assessment_mappings = {
                            'anxiety': 'gad7',
                            'depression': 'phq9',
                            'stress': 'dass21_stress'
                        }
                        next_assessment = assessment_mappings.get(priority_category)
                        
                        # Kiểm tra xem đánh giá có tồn tại không
                        if next_assessment and next_assessment in questionnaires:
                            print(f"Chuyển sang đánh giá chi tiết: {next_assessment}")
                            return {
                                'state': POLL_STATES['DETAILED_ASSESSMENT'],
                                'currentAssessment': next_assessment,
                                'currentQuestionIndex': 0,
                                'totalQuestions': len(questionnaires[next_assessment]['questions'])
                            }
        
        # Nếu không có vấn đề nghiêm trọng, chuyển sang tóm tắt
        return {
            'state': POLL_STATES['SUMMARY']
        }
    
    # Cho các đánh giá chi tiết, chuyển sang tóm tắt
    return {
        'state': POLL_STATES['SUMMARY']
    }

def handle_results_preview(poll_state, response):
    """
    Xử lý khi người dùng nhấn nút "Tiếp tục" từ trang preview
    
    Args:
        poll_state (dict): Trạng thái poll hiện tại
        response (str): Phản hồi của người dùng (không quan trọng trong trường hợp này)
        
    Returns:
        dict: Thông tin cho câu hỏi tiếp theo và trạng thái poll mới
    """
    # Xác định đánh giá chi tiết tiếp theo dựa trên kết quả sàng lọc ban đầu
    assessment_id = 'initialScreening'
    severity = poll_state.get('severityLevels', {}).get(assessment_id, {})
    
    # Xác định trạng thái tiếp theo
    next_state = determine_next_state(
        {**poll_state, 'state': POLL_STATES['RESULTS_PREVIEW']},
        questionnaires.get(assessment_id, {}),
        severity,
        poll_state.get('flags', {})
    )
    
    updated_poll_state = {**poll_state, **next_state}
    
    # Nếu chuyển sang đánh giá chi tiết, chuẩn bị câu hỏi đầu tiên
    if next_state['state'] == POLL_STATES['DETAILED_ASSESSMENT']:
        next_assessment = updated_poll_state['currentAssessment']
        next_question = questionnaires[next_assessment]['questions'][0]
        
        return {
            'chatState': updated_poll_state,
            'question': next_question['text'],
            'options': [option['text'] for option in next_question['options']]
        }
    
    # Nếu chuyển sang tóm tắt, tạo HTML tóm tắt
    if next_state['state'] == POLL_STATES['SUMMARY']:
        summary_html = generate_summary_html(
            poll_state.get('scores', {}), 
            poll_state.get('severityLevels', {})
        )
        
        return {
            'chatState': updated_poll_state,
            'showResults': True,
            'resultsHtml': summary_html
        }
    
    # Fallback
    return {
        'chatState': updated_poll_state,
        'error': 'Không thể xác định bước tiếp theo'
    }

def get_resources(poll_state):
    """
    Lấy tài nguyên phù hợp với kết quả đánh giá
    
    Args:
        poll_state (dict): Trạng thái poll hiện tại
        
    Returns:
        dict: HTML tài nguyên và trạng thái poll mới
    """
    try:
        # Xác định rối loạn chính và mức độ nghiêm trọng
        primary_disorder = 'depression'  # Mặc định
        primary_severity = 'mild'  # Mặc định
        
        # Xác định từ kết quả sàng lọc ban đầu
        if poll_state.get('severityLevels', {}).get('initialScreening'):
            initial_screening = poll_state['severityLevels']['initialScreening']
            
            # Tìm danh mục nghiêm trọng nhất
            max_severity = 'minimal'
            
            for category, severity in initial_screening.items():
                if severity_weight(severity) > severity_weight(max_severity):
                    max_severity = severity
                    primary_disorder = category
            
            primary_severity = max_severity
        
        # Sử dụng đánh giá chi tiết nếu có
        detailed_assessments = [a for a in poll_state.get('severityLevels', {}).keys() 
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
            
            primary_severity = poll_state['severityLevels'][assessment_id]
        
        # Lấy tài nguyên phù hợp - không cần sử dụng resources_list ở đây nữa
        resources_html = format_resources_html([])  # Truyền một danh sách rỗng, vì tất cả tài nguyên đã hard-code trong template
        
        # Cập nhật trạng thái
        updated_poll_state = {
            **poll_state,
            'state': POLL_STATES['RESOURCES'],
            'primaryDisorder': primary_disorder
        }
        
        return {
            'chatState': updated_poll_state,
            'showResources': True,
            'resourcesHtml': resources_html
        }
    except Exception as e:
        logger.exception("Error in get_resources", exc_info=e)
        return {
            'error': f"Lỗi khi lấy tài nguyên: {str(e)}"
        }

def severity_weight(severity):
    """
    Hàm trợ giúp đánh giá mức độ nghiêm trọng
    
    Args:
        severity (str): Mức độ nghiêm trọng
        
    Returns:
        int: Trọng số
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

def generate_summary_html(scores, severity_levels):
    """
    Tạo HTML tóm tắt kết quả đánh giá
    
    Args:
        scores (dict): Điểm số các bộ đánh giá
        severity_levels (dict): Mức độ nghiêm trọng
        
    Returns:
        str: HTML tóm tắt
    """
    if not scores or not severity_levels:
        return "<h2>Kết quả đánh giá sơ bộ</h2><p>Không có đủ thông tin để cung cấp đánh giá chi tiết.</p>"
    
    html = "<h2>Kết quả đánh giá sơ bộ</h2>"
    found_any_issue = False
    
    # Xử lý sàng lọc ban đầu
    if 'initialScreening' in severity_levels:
        html += "<h3>Dựa trên sàng lọc ban đầu:</h3><ul>"
        
        for category, level in severity_levels['initialScreening'].items():
            category_name = {
                'depression': 'Trầm cảm',
                'anxiety': 'Lo âu',
                'stress': 'Căng thẳng'
            }.get(category, category)
            
            html += f"<li><strong>{category_name}</strong>: {format_severity(level)}</li>"
            
            if level != 'minimal':
                found_any_issue = True
        
        html += "</ul>"
    
    # Xử lý đánh giá chi tiết
    detailed_assessments = [a for a in severity_levels.keys() 
                           if a not in ['initialScreening', 'suicideRiskAssessment']]
    
    if detailed_assessments:
        html += "<h3>Kết quả đánh giá chi tiết:</h3><ul>"
        
        for assessment_id in detailed_assessments:
            level = severity_levels[assessment_id]
            assessment_name = questionnaires.get(assessment_id, {}).get('name', assessment_id)
            
            html += f"<li><strong>{assessment_name}</strong>: {format_severity(level)}</li>"
        
        html += "</ul>"
    
    # Xử lý đánh giá nguy cơ tự tử
    if 'suicideRiskAssessment' in severity_levels:
        level = severity_levels['suicideRiskAssessment']
        
        if level in ['high', 'severe']:
            html += "<div class='warning-box'>"
            html += "<h3>⚠️ CẢNH BÁO: Phát hiện nguy cơ tự tử đáng kể ⚠️</h3>"
            html += "<p>Vui lòng liên hệ ngay với các dịch vụ hỗ trợ khẩn cấp được liệt kê ở phần tiếp theo.</p>"
            html += "</div>"
        elif level == 'moderate':
            html += "<div class='warning-box'>"
            html += "<h3>⚠️ Lưu ý: Phát hiện một số dấu hiệu nguy cơ tự tử ⚠️</h3>"
            html += "<p>Khuyến nghị tham khảo ý kiến chuyên gia sức khỏe tâm thần.</p>"
            html += "</div>"
    
    # Thêm lời khuyên chung
    html += "<h3>Đề xuất tiếp theo</h3>"
    
    if found_any_issue:
        html += "<p>Dựa trên đánh giá sơ bộ này, việc tham khảo ý kiến của chuyên gia sức khỏe tâm thần có thể mang lại lợi ích. Họ có thể cung cấp đánh giá toàn diện hơn và thảo luận về các phương án hỗ trợ phù hợp với nhu cầu cụ thể của bạn.</p>"
    else:
        html += "<p>Mặc dù bạn không có dấu hiệu đáng kể của các vấn đề sức khỏe tâm thần dựa trên đánh giá sơ bộ này, việc duy trì thói quen chăm sóc bản thân vẫn rất quan trọng. Nếu bạn tiếp tục cảm thấy lo lắng về sức khỏe tâm thần của mình, hãy cân nhắc nói chuyện với chuyên gia chăm sóc sức khỏe.</p>"
    
    html += "<div class='note-box'>"
    html += "<h3>Lưu ý quan trọng</h3>"
    html += "<p>Thông tin này chỉ mang tính chất tham khảo và không phải là chẩn đoán chính thức. Chỉ chuyên gia sức khỏe tâm thần mới có thể đưa ra chẩn đoán chính xác.</p>"
    html += "</div>"
    
    return html

def format_severity(level):
    """
    Định dạng mức độ nghiêm trọng thành văn bản
    
    Args:
        level (str): Mức độ nghiêm trọng
        
    Returns:
        str: Văn bản hiển thị
    """
    if not level:
        return "Không xác định"
    
    severity_map = {
        'minimal': "Tối thiểu",
        'mild': "Nhẹ",
        'moderate': "Trung bình",
        'moderatelySevere': "Trung bình đến nặng",
        'severe': "Nặng",
        'extremelySevere': "Cực kỳ nặng",
        'low': "Thấp",
        'high': "Cao",
        'normal': "Bình thường"
    }
    
    return severity_map.get(level, level)

def generate_preview_chart_data(scores):
    """
    Tạo dữ liệu biểu đồ cho trang preview
    
    Args:
        scores (dict): Điểm số theo danh mục
        
    Returns:
        dict: Dữ liệu biểu đồ định dạng JSON
    """
    # Tạo dữ liệu cho biểu đồ
    chart_data = []
    
    if 'initialScreening' in scores:
        category_scores = scores['initialScreening']
        
        max_score = {
            'depression': 16,  # Tổng điểm tối đa có thể
            'anxiety': 12,
            'stress': 12
        }
        
        for category, score in category_scores.items():
            if category in max_score:
                percentage = (score / max_score[category]) * 100
                chart_data.append({
                    'category': category,
                    'score': score,
                    'percentage': round(percentage, 1),
                    'maxScore': max_score[category]
                })
    
    return chart_data

def generate_preview_html(scores, severity_levels):
    """
    Tạo HTML cho trang preview kết quả đẹp mắt hơn
    
    Args:
        scores (dict): Điểm số các bộ đánh giá
        severity_levels (dict): Mức độ nghiêm trọng
        
    Returns:
        str: HTML preview
    """
    html = """
    <div class="results-preview-container">
        <h2 class="text-center mb-4">Kết quả đánh giá sơ bộ</h2>
        
        <div class="info-card mb-4">
            <div class="info-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
            </div>
            <div class="info-content">
                <p>Dưới đây là kết quả sơ bộ dựa trên câu trả lời của bạn cho bộ câu hỏi sàng lọc ban đầu. Hãy tiếp tục với đánh giá chi tiết để có kết quả chính xác hơn.</p>
            </div>
        </div>
    """
    
    # Thêm container cho biểu đồ
    html += """
        <div class="score-visualization">
            <h3 class="section-title">Phân tích kết quả</h3>
    """
    
    # Thêm các thanh biểu đồ
    if 'initialScreening' in severity_levels:
        categories = {
            'depression': {'name': 'Trầm cảm', 'maxScore': 16, 'icon': '<path d="M9.1 11.5a.5.5 0 0 1 .4-.8h5a.5.5 0 0 1 .4.8 4 4 0 0 1-5.8 0Z"></path><path d="M9 16h6v-2H9v2Z"></path><circle cx="12" cy="12" r="10"></circle>'},
            'anxiety': {'name': 'Lo âu', 'maxScore': 12, 'icon': '<path d="M9 9h6l-3 6Z"></path><circle cx="12" cy="12" r="10"></circle>'},
            'stress': {'name': 'Căng thẳng', 'maxScore': 12, 'icon': '<path d="m8 12 2.7 3.6a1 1 0 0 0 .8.4c.3 0 .5-.1.7-.3L17 12"></path><circle cx="12" cy="12" r="10"></circle>'}
        }
        
        html += '<div class="score-bars">'
        
        for category, level in severity_levels['initialScreening'].items():
            if category in categories:
                category_info = categories[category]
                category_name = category_info['name']
                max_score = category_info['maxScore']
                icon = category_info['icon']
                score = scores.get('initialScreening', {}).get(category, 0)
                
                # Xác định màu và label dựa trên mức độ
                color_class = 'low-score'
                severity_label = 'Nhẹ'
                
                if level == 'minimal':
                    color_class = 'normal-score'
                    severity_label = 'Bình thường'
                elif level == 'mild':
                    color_class = 'mild-score'
                    severity_label = 'Nhẹ'
                elif level == 'moderate':
                    color_class = 'medium-score'
                    severity_label = 'Trung bình'
                elif level in ['severe', 'moderatelySevere', 'extremelySevere']:
                    color_class = 'high-score'
                    severity_label = 'Nặng'
                
                # Đặt tỷ lệ phần trăm dựa trên điểm số
                percentage = min(100, int((score / max_score) * 100))
                
                html += f"""
                <div class="score-bar-container">
                    <div class="score-header">
                        <div class="score-label">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="category-icon">
                                {icon}
                            </svg>
                            <span>{category_name}</span>
                        </div>
                        <div class="score-value-badge {color_class}-badge">{severity_label}</div>
                    </div>
                    <div class="score-bar">
                        <div class="score-fill {color_class}" style="width: {percentage}%">
                            <span class="score-label-inner">{score}/{max_score}</span>
                        </div>
                    </div>
                </div>
                """
        
        html += '</div>'
    
    html += '</div>'
    
    # Thêm phần diễn giải
    html += """
        <div class="results-interpretation">
            <h3 class="section-title">Diễn giải</h3>
            <div class="interpretation-card">
    """
    
    found_issues = False
    html += '<ul class="interpretation-list">'
    
    if 'initialScreening' in severity_levels:
        for category, level in severity_levels['initialScreening'].items():
            if level != 'minimal':
                found_issues = True
                category_name = {
                    'depression': 'trầm cảm',
                    'anxiety': 'lo âu',
                    'stress': 'căng thẳng'
                }.get(category, category)
                
                # Đặt màu sắc dựa trên mức độ
                level_class = "level-mild"
                if level == 'moderate':
                    level_class = "level-moderate"
                elif level in ['severe', 'moderatelySevere', 'extremelySevere']:
                    level_class = "level-severe"
                
                html += f"""
                <li>
                    <span class="level-indicator {level_class}"></span>
                    Bạn có dấu hiệu <strong class="{level_class}-text">{format_severity(level).lower()}</strong> của <strong>{category_name}</strong>
                </li>
                """
    
    if not found_issues:
        html += """
        <li>
            <span class="level-indicator level-normal"></span>
            Không phát hiện dấu hiệu đáng kể của vấn đề sức khỏe tâm thần
        </li>
        """
    
    html += """
            </ul>
            </div>
        </div>
    """
    
    # Thêm hướng dẫn tiếp theo
    html += """
        <div class="next-steps">
            <h3 class="section-title">Bước tiếp theo</h3>
            <div class="next-steps-card">
                <div class="next-steps-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="8" y1="6" x2="21" y2="6"></line>
                        <line x1="8" y1="12" x2="21" y2="12"></line>
                        <line x1="8" y1="18" x2="21" y2="18"></line>
                        <line x1="3" y1="6" x2="3.01" y2="6"></line>
                        <line x1="3" y1="12" x2="3.01" y2="12"></line>
                        <line x1="3" y1="18" x2="3.01" y2="18"></line>
                    </svg>
                </div>
                <div class="next-steps-content">
                    <p>Dựa trên kết quả sơ bộ này, chúng tôi có thể đánh giá chi tiết hơn về các lĩnh vực có liên quan. 
                    Việc tiếp tục với bộ câu hỏi chi tiết sẽ giúp có được đánh giá chính xác hơn.</p>
                    <p class="disclaimer">Lưu ý: Kết quả này chỉ mang tính chất tham khảo và không phải chẩn đoán chính thức.</p>
                </div>
            </div>
        </div>
    """
    
    # Thêm CSS cho giao diện đẹp hơn
    html += """
        <style>
            .results-preview-container {
                max-width: 800px;
                margin: 0 auto;
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                animation: fadeIn 0.5s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .text-center {
                text-align: center;
            }
            
            .mb-4 {
                margin-bottom: 2rem;
            }
            
            h2 {
                font-size: 1.75rem;
                font-weight: 700;
                color: white;
                margin-bottom: 1.5rem;
                position: relative;
                padding-bottom: 0.75rem;
            }
            
            h2:after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 50%;
                transform: translateX(-50%);
                width: 80px;
                height: 4px;
                background: linear-gradient(to right, rgb(139, 92, 246), rgb(236, 72, 153));
                border-radius: 2px;
            }
            
            .section-title {
                font-size: 1.25rem;
                font-weight: 600;
                color: white;
                margin-bottom: 1rem;
                border-left: 4px solid rgb(139, 92, 246);
                padding-left: 0.75rem;
            }
            
            .info-card {
                background: rgba(38, 38, 38, 0.6);
                border: 1px solid rgba(61, 61, 61, 0.8);
                border-radius: 0.75rem;
                padding: 1.25rem;
                display: flex;
                align-items: flex-start;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .info-icon {
                flex-shrink: 0;
                margin-right: 1rem;
                color: rgb(139, 92, 246);
            }
            
            .info-content p {
                margin: 0;
                color: rgb(200, 200, 200);
                line-height: 1.6;
            }
            
            .score-visualization {
                background: rgba(46, 46, 46, 0.6);
                border: 1px solid rgba(61, 61, 61, 0.8);
                border-radius: 0.75rem;
                padding: 1.5rem;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .score-bars {
                display: flex;
                flex-direction: column;
                gap: 1.25rem;
            }
            
            .score-bar-container {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .score-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .score-label {
                display: flex;
                align-items: center;
                font-weight: 500;
                color: white;
            }
            
            .category-icon {
                margin-right: 0.5rem;
            }
            
            .score-value-badge {
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
            }
            
            .normal-score-badge {
                background-color: rgba(16, 185, 129, 0.2);
                color: rgb(16, 185, 129);
            }
            
            .mild-score-badge {
                background-color: rgba(250, 204, 21, 0.2);
                color: rgb(250, 204, 21);
            }
            
            .medium-score-badge {
                background-color: rgba(249, 115, 22, 0.2);
                color: rgb(249, 115, 22);
            }
            
            .high-score-badge {
                background-color: rgba(239, 68, 68, 0.2);
                color: rgb(239, 68, 68);
            }
            
            .score-bar {
                height: 28px;
                background-color: rgba(50, 50, 50, 0.5);
                border-radius: 14px;
                overflow: hidden;
                border: 1px solid rgba(61, 61, 61, 0.8);
            }
            
            .score-fill {
                height: 100%;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 0.75rem;
                font-size: 0.875rem;
                font-weight: 600;
                transition: width 1.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            }
            
            .score-label-inner {
                color: white;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
            }
            
            .normal-score {
                background: linear-gradient(to right, rgb(16, 185, 129), rgb(5, 150, 105));
            }
            
            .low-score {
                background: linear-gradient(to right, rgb(74, 222, 128), rgb(22, 163, 74));
            }
            
            .mild-score {
                background: linear-gradient(to right, rgb(250, 204, 21), rgb(234, 179, 8));
            }
            
            .medium-score {
                background: linear-gradient(to right, rgb(249, 115, 22), rgb(234, 88, 12));
            }
            
            .high-score {
                background: linear-gradient(to right, rgb(248, 113, 113), rgb(239, 68, 68));
            }
            
            .results-interpretation, .next-steps {
                margin-bottom: 2rem;
            }
            
            .interpretation-card, .next-steps-card {
                background: rgba(46, 46, 46, 0.6);
                border: 1px solid rgba(61, 61, 61, 0.8);
                border-radius: 0.75rem;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .next-steps-card {
                display: flex;
            }
            
            .next-steps-icon {
                flex-shrink: 0;
                margin-right: 1rem;
                color: rgb(139, 92, 246);
            }
            
            .next-steps-content p {
                margin: 0 0 1rem;
                color: rgb(200, 200, 200);
                line-height: 1.6;
            }
            
            .next-steps-content p:last-child {
                margin-bottom: 0;
            }
            
            .disclaimer {
                font-style: italic;
                color: rgb(156, 163, 175);
                font-size: 0.875rem;
            }
            
            .interpretation-list {
                list-style-type: none;
                padding: 0;
                margin: 0;
            }
            
            .interpretation-list li {
                display: flex;
                align-items: center;
                padding: 0.5rem 0;
                color: rgb(200, 200, 200);
            }
            
            .level-indicator {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 0.75rem;
                flex-shrink: 0;
            }
            
            .level-normal {
                background-color: rgb(16, 185, 129);
            }
            
            .level-mild {
                background-color: rgb(250, 204, 21);
            }
            
            .level-moderate {
                background-color: rgb(249, 115, 22);
            }
            
            .level-severe {
                background-color: rgb(239, 68, 68);
            }
            
            .level-mild-text {
                color: rgb(250, 204, 21);
            }
            
            .level-moderate-text {
                color: rgb(249, 115, 22);
            }
            
            .level-severe-text {
                color: rgb(239, 68, 68);
            }
        </style>
    """
    
    return html

def handle_results_preview(poll_state, response):
    """
    Xử lý khi người dùng nhấn nút "Tiếp tục" từ trang preview
    
    Args:
        poll_state (dict): Trạng thái poll hiện tại
        response (str): Phản hồi của người dùng (không quan trọng trong trường hợp này)
        
    Returns:
        dict: Thông tin cho câu hỏi tiếp theo và trạng thái poll mới
    """
    try:
        # Lấy thông tin severity từ kết quả sàng lọc ban đầu
        assessment_id = 'initialScreening'
        severity_levels = poll_state.get('severityLevels', {}).get(assessment_id, {})
        scores = poll_state.get('scores', {})
        
        # Log để debug
        logger.info(f"Processing results preview. Severity: {severity_levels}")
        
        # Xác định đánh giá chi tiết tiếp theo dựa trên mức độ nghiêm trọng
        # Tìm danh mục có mức độ nghiêm trọng cao nhất
        highest_category = None
        highest_severity = "minimal"
        severity_rank = {"minimal": 0, "mild": 1, "moderate": 2, "severe": 3}
        
        for category, level in severity_levels.items():
            if severity_rank.get(level, 0) > severity_rank.get(highest_severity, 0):
                highest_severity = level
                highest_category = category
        
        # Nếu có mức độ moderate hoặc severe, chuyển sang đánh giá chi tiết
        if highest_severity in ['moderate', 'severe'] and highest_category:
            # Lấy thông tin về đánh giá tiếp theo cho danh mục này
            next_assessment = questionnaires['initialScreening'].get('nextAssessment', {}).get(highest_category)
            
            if next_assessment and next_assessment in questionnaires:
                logger.info(f"Moving to detailed assessment: {next_assessment} for {highest_category}")
                
                # Cập nhật trạng thái và lấy câu hỏi đầu tiên
                updated_poll_state = {
                    **poll_state,
                    'state': POLL_STATES['DETAILED_ASSESSMENT'],
                    'currentAssessment': next_assessment,
                    'currentQuestionIndex': 0,
                    'totalQuestions': len(questionnaires[next_assessment]['questions'])
                }
                
                next_question = questionnaires[next_assessment]['questions'][0]
                
                return {
                    'chatState': updated_poll_state,
                    'question': next_question['text'],
                    'options': [option['text'] for option in next_question['options']]
                }
        
        # Nếu không có danh mục nào nghiêm trọng, chuyển sang tóm tắt
        logger.info("No severe categories found, moving to summary")
        summary_html = generate_summary_html(scores, severity_levels)
        
        return {
            'chatState': {
                **poll_state,
                'state': POLL_STATES['SUMMARY']
            },
            'showResults': True,
            'resultsHtml': summary_html
        }
        
    except Exception as e:
        logger.exception(f"Error in handle_results_preview: {str(e)}")
        # Trả về lỗi với thông báo cụ thể
        return {
            'chatState': poll_state,
            'error': f"Lỗi xử lý kết quả: {str(e)}"
        }
    
