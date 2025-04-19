"""
Bản đồ trò chuyện cho chatbot sức khỏe tâm thần
Định nghĩa cấu trúc trò chuyện tự nhiên thay vì danh sách tuyến tính
"""

# Bản đồ trò chuyện mô tả cách các chủ đề kết nối với nhau
# Mỗi nút chứa:
# - next: Danh sách các nút tiếp theo có thể chuyển đến (theo thứ tự ưu tiên)
# - transition_conditions: Điều kiện chuyển đến nút tiếp theo (ví dụ: nếu điểm cao thì ưu tiên một nút cụ thể)

CONVERSATION_MAP = {
    "greeting": {
        "next": ["feeling_tired", "worried", "sad_feelings"],
        "transition_conditions": {}
    },
    
    # Nhóm năng lượng/mệt mỏi/giấc ngủ
    "feeling_tired": {
        "next": ["sleep_issues", "sad_feelings", "worried"],
        "transition_conditions": {
            "high_score": "sad_feelings"  # Nếu điểm cao, ưu tiên chuyển sang chủ đề buồn bã
        }
    },
    "sleep_issues": {
        "next": ["eating_issues", "sad_feelings", "worried"],
        "transition_conditions": {}
    },
    "eating_issues": {
        "next": ["sad_feelings", "worried", "relax_difficulty"],
        "transition_conditions": {}
    },
    
    # Nhóm lo âu/căng thẳng
    "worried": {
        "next": ["relax_difficulty", "panic", "sad_feelings"],
        "transition_conditions": {
            "high_score": "panic"  # Nếu điểm cao, ưu tiên chuyển sang chủ đề hoảng sợ
        }
    },
    "relax_difficulty": {
        "next": ["panic", "sad_feelings", "sleep_issues"],
        "transition_conditions": {}
    },
    "panic": {
        "next": ["sad_feelings", "sleep_issues", "worthless"],
        "transition_conditions": {}
    },
    
    # Nhóm trầm cảm
    "sad_feelings": {
        "next": ["lost_interest", "worthless", "life_not_worth"],
        "transition_conditions": {
            "high_score": "worthless"  # Nếu điểm cao, ưu tiên chuyển sang chủ đề vô giá trị
        }
    },
    "lost_interest": {
        "next": ["worthless", "life_not_worth", "sleep_issues"],
        "transition_conditions": {}
    },
    "worthless": {
        "next": ["life_not_worth", "sleep_issues", "feeling_tired"],
        "transition_conditions": {}
    },
    "life_not_worth": {
        "next": ["sleep_issues", "eating_issues", "feeling_tired"],
        "transition_conditions": {}
    }
}

# Hàm xác định câu hỏi tiếp theo dựa trên câu hỏi hiện tại và điểm số
def get_next_question(current_question_id, scores=None, asked_questions=None):
    """
    Xác định câu hỏi tiếp theo dựa trên bản đồ trò chuyện
    
    Args:
        current_question_id: ID của câu hỏi hiện tại
        scores: Dict điểm số các câu hỏi đã hỏi
        asked_questions: List các câu hỏi đã hỏi
    
    Returns:
        ID của câu hỏi tiếp theo
    """
    if asked_questions is None:
        asked_questions = []
    
    if scores is None:
        scores = {}
    
    # Nếu không có câu hỏi hiện tại hoặc không có trong bản đồ, bắt đầu từ greeting
    if not current_question_id or current_question_id not in CONVERSATION_MAP:
        current_question_id = "greeting"
    
    # Lấy thông tin của nút hiện tại
    current_node = CONVERSATION_MAP[current_question_id]
    
    # Kiểm tra điều kiện chuyển đổi
    if scores and current_question_id in scores:
        score = scores[current_question_id]
        # Nếu điểm cao (3-4), áp dụng điều kiện chuyển đổi đặc biệt
        if score >= 3 and "high_score" in current_node["transition_conditions"]:
            priority_next = current_node["transition_conditions"]["high_score"]
            if priority_next not in asked_questions:
                return priority_next
    
    # Duyệt qua danh sách các nút tiếp theo theo thứ tự ưu tiên
    for next_id in current_node["next"]:
        if next_id not in asked_questions:
            return next_id
    
    # Nếu tất cả nút ưu tiên đã được hỏi, tìm câu hỏi chưa được hỏi từ danh sách đầy đủ
    from data.question_bank import QUESTION_IDS
    for question_id in QUESTION_IDS:
        if question_id not in asked_questions:
            return question_id
    
    # Nếu tất cả câu hỏi đã được hỏi, trả về None
    return None

# Hàm đánh giá đã đủ thông tin cho sàng lọc ban đầu chưa
def has_sufficient_screening(asked_questions):
    """
    Kiểm tra xem đã thu thập đủ thông tin cho sàng lọc ban đầu chưa
    
    Args:
        asked_questions: Danh sách các câu hỏi đã hỏi
    
    Returns:
        Boolean: True nếu đã đủ thông tin, False nếu chưa
    """
    from data.question_bank import QUESTION_IDS
    
    # Định nghĩa số lượng câu hỏi tối thiểu cần thiết
    min_required = 7  # Yêu cầu ít nhất 7/10 câu hỏi ban đầu
    
    # Đếm số câu hỏi đã hỏi từ danh sách câu hỏi chuẩn
    asked_count = sum(1 for q_id in QUESTION_IDS if q_id in asked_questions)
    
    return asked_count >= min_required