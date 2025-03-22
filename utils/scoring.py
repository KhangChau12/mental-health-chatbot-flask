"""
Logic tính điểm và xác định mức độ nghiêm trọng
Chuyển đổi từ scoring.js sang Python
"""

import logging

logger = logging.getLogger(__name__)

def calculate_scores(responses, assessment):
    """
    Tính tổng điểm cho một bộ câu hỏi
    
    Args:
        responses (dict): Phản hồi của người dùng (question_id: value)
        assessment (dict): Thông tin về bộ đánh giá
        
    Returns:
        Đối với đánh giá ban đầu: dict với điểm cho từng danh mục
        Đối với các đánh giá khác: số tổng điểm
    """
    if not responses or not assessment or 'scoring' not in assessment:
        logger.warning("Missing data in calculate_scores", extra={"responses": responses, "assessment": assessment})
        return None
    
    # Nếu đánh giá ban đầu, tính điểm cho từng danh mục
    if assessment.get('id') == 'initialScreening':
        category_scores = {}
        
        # Duyệt qua từng danh mục
        for category, data in assessment['scoring'].items():
            if category == 'nextAssessment':
                continue  # Bỏ qua nếu không phải danh mục
            
            # Lấy IDs câu hỏi cho danh mục này
            question_ids = data.get('questions', [])
            if not question_ids or not isinstance(question_ids, list):
                logger.warning(f"Invalid questionIds for category {category}")
                continue
            
            # Tính tổng điểm
            total = 0
            valid_responses = 0
            
            for qid in question_ids:
                if qid in responses:
                    total += responses[qid]
                    valid_responses += 1
            
            # Nếu có phản hồi hợp lệ, lưu điểm
            if valid_responses > 0:
                category_scores[category] = total
        
        return category_scores
    
    # Cho các bộ câu hỏi khác, tính tổng điểm
    total = 0
    valid_responses = 0
    
    # Lấy danh sách ID câu hỏi từ scoring
    question_ids = assessment['scoring'].get('questions', [])
    if not question_ids or not isinstance(question_ids, list):
        logger.warning("Invalid questionIds in assessment scoring")
        return None
    
    for qid in question_ids:
        if qid in responses:
            total += responses[qid]
            valid_responses += 1
    
    # Nếu không có phản hồi hợp lệ, trả về None
    if valid_responses == 0:
        return None
    
    return total

def get_severity_level(scores, assessment):
    """
    Xác định mức độ nghiêm trọng dựa trên điểm số
    
    Args:
        scores: Điểm số hoặc dict điểm số theo danh mục
        assessment: Thông tin về bộ đánh giá
        
    Returns:
        Đối với đánh giá ban đầu: dict với mức độ cho từng danh mục
        Đối với các đánh giá khác: mức độ nghiêm trọng (string)
    """
    if not scores or not assessment or 'scoring' not in assessment:
        logger.warning("Missing data in get_severity_level", extra={"scores": scores, "assessment": assessment})
        return None
    
    # Nếu đánh giá ban đầu, xác định mức độ nghiêm trọng cho từng danh mục
    if assessment.get('id') == 'initialScreening':
        severity_levels = {}
        
        # Duyệt qua từng danh mục
        for category, data in assessment['scoring'].items():
            if category == 'nextAssessment':
                continue  # Bỏ qua nếu không phải danh mục
            
            # Lấy điểm số cho danh mục này
            if category not in scores:
                continue
                
            score = scores[category]
            
            # Lấy ngưỡng điểm
            thresholds = data.get('thresholds')
            if not thresholds:
                logger.warning(f"Missing thresholds for category {category}")
                continue
            
            # Xác định mức độ nghiêm trọng
            severity_levels[category] = determine_level(score, thresholds)
        
        return severity_levels
    
    # Cho các bộ câu hỏi khác, xác định mức độ nghiêm trọng dựa trên tổng điểm
    thresholds = assessment['scoring'].get('thresholds')
    if not thresholds:
        logger.warning("Missing thresholds in assessment scoring")
        return None
    
    return determine_level(scores, thresholds)

def determine_level(score, thresholds):
    """
    Hàm trợ giúp xác định mức độ dựa trên ngưỡng
    
    Args:
        score: Điểm số
        thresholds: Dict với ngưỡng điểm cho từng mức độ
        
    Returns:
        String mức độ nghiêm trọng
    """
    if not score or not thresholds or not isinstance(thresholds, dict):
        logger.warning("Invalid score or thresholds in determine_level")
        return "minimal"  # Mặc định
    
    try:
        # Sắp xếp các ngưỡng theo thứ tự giảm dần
        levels = sorted(thresholds.keys(), key=lambda x: thresholds[x], reverse=True)
        
        # Tìm mức độ đầu tiên mà điểm số vượt qua ngưỡng
        for level in levels:
            if score >= thresholds[level]:
                return level
        
        # Mặc định trả về mức độ thấp nhất
        return levels[-1] if levels else "minimal"
    except Exception as e:
        logger.error(f"Error in determine_level: {e}")
        return "minimal"  # Mặc định trong trường hợp lỗi

def check_risk_flags(responses, assessment):
    """
    Kiểm tra cờ rủi ro từ phản hồi
    
    Args:
        responses: Dict phản hồi của người dùng
        assessment: Thông tin về bộ đánh giá
        
    Returns:
        Dict với các cờ rủi ro
    """
    if not responses or not assessment or 'questions' not in assessment:
        logger.warning("Missing data in check_risk_flags", extra={"responses": responses, "assessment": assessment})
        return {"suicideRisk": False}
    
    flags = {
        "suicideRisk": False,
        # Thêm các cờ rủi ro khác khi cần
    }
    
    # Duyệt qua tất cả câu hỏi để tìm cờ
    for question in assessment['questions']:
        if question.get('flag') == 'suicide_risk':
            if question['id'] in responses and responses[question['id']] >= 3:
                flags["suicideRisk"] = True
    
    return flags