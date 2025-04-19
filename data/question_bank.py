"""
Ngân hàng câu hỏi phong phú cho giai đoạn đối thoại tự nhiên
"""

# Cấu trúc: Mỗi nhóm câu hỏi chứa:
# - variants: Các phiên bản câu hỏi khác nhau để AI lựa chọn
# - follow_ups: Câu hỏi đào sâu khi người dùng đề cập đến vấn đề
# - transitions: Các cách chuyển tiếp tự nhiên sang chủ đề tiếp theo
# - explicit_rating: Câu hỏi đánh giá cụ thể nếu chưa thể xác định mức độ

question_bank = {
    "feeling_tired": {
        "category": "stress",
        "variants": [
            "Dạo này mức năng lượng của bạn thế nào?",
            "Bạn có thường cảm thấy kiệt sức không, kể cả khi không làm việc nặng?",
            "Có bao giờ bạn thấy mệt mỏi dù đã nghỉ ngơi đủ không?",
            "Bạn có nhận thấy mình dễ mệt mỏi hơn bình thường không?"
        ],
        "follow_ups": [
            "Mệt mỏi đó ảnh hưởng đến hoạt động hàng ngày của bạn thế nào?",
            "Bạn có nhận thấy kiểu mệt mỏi này khác với cảm giác mệt thông thường không?",
            "Bạn đã thử phương pháp nào để đối phó với tình trạng mệt mỏi này chưa?"
        ],
        "transitions": [
            "Sự mệt mỏi đôi khi có thể ảnh hưởng đến giấc ngủ của chúng ta. Bạn có gặp khó khăn khi ngủ không?",
            "Ngoài mệt mỏi, bạn có cảm thấy tâm trạng của mình bị ảnh hưởng không?",
            "Tôi hiểu về vấn đề mệt mỏi của bạn. Điều này có làm bạn cảm thấy lo lắng không?"
        ],
        "explicit_rating": "Trên thang điểm từ 0-4, với 0 là không bao giờ và 4 là luôn luôn, bạn sẽ đánh giá mức độ mệt mỏi không rõ lý do của mình ở đâu?"
    },
    
    "worried": {
        "category": "anxiety",
        "variants": [
            "Bạn có hay cảm thấy lo lắng về những việc hàng ngày không?",
            "Có thường xuyên xuất hiện những suy nghĩ lo âu trong đầu bạn không?",
            "Bạn có dễ bị căng thẳng hoặc bồn chồn không?",
            "Gần đây bạn có thấy mình lo lắng nhiều hơn bình thường không?"
        ],
        "follow_ups": [
            "Những lo lắng này thường về vấn đề gì?",
            "Bạn thấy mình kiểm soát những lo lắng này thế nào?",
            "Lo lắng ảnh hưởng đến sinh hoạt hàng ngày của bạn như thế nào?"
        ],
        "transitions": [
            "Lo lắng kéo dài đôi khi khiến chúng ta khó thư giãn. Bạn có gặp khó khăn khi cố gắng thư giãn không?",
            "Khi lo lắng, nhiều người cảm thấy khó tập trung vào các hoạt động yêu thích. Bạn có thấy mình mất hứng thú với những việc trước đây bạn thích không?",
            "Lo lắng thường đi kèm với cảm giác căng thẳng. Bạn có thấy cơ thể mình căng cứng không?"
        ],
        "explicit_rating": "Trên thang điểm từ 0-4, với 0 là không bao giờ và 4 là luôn luôn, bạn đánh giá mức độ lo lắng, căng thẳng hoặc bồn chồn của mình ở đâu?"
    },
    
    "relax_difficulty": {
        "category": "anxiety",
        "variants": [
            "Bạn có dễ dàng thư giãn sau một ngày căng thẳng không?",
            "Bạn có thấy khó buông bỏ những suy nghĩ lo lắng khi muốn nghỉ ngơi không?",
            "Cơ thể bạn có thường xuyên cảm thấy căng cứng không?",
            "Bạn thấy việc 'tắt' những suy nghĩ và thư giãn có dễ dàng không?"
        ],
        "follow_ups": [
            "Bạn thường làm gì để cố gắng thư giãn?",
            "Điều gì khiến bạn cảm thấy khó thư giãn nhất?",
            "Cảm giác căng thẳng này thường xuất hiện vào thời điểm nào trong ngày?"
        ],
        "transitions": [
            "Khi không thể thư giãn, nhiều người cảm thấy dễ bị hoảng sợ. Bạn có bao giờ cảm thấy lo sợ đột ngột không?",
            "Khó khăn khi thư giãn đôi khi liên quan đến tâm trạng. Bạn có cảm thấy buồn bã nhiều không?",
            "Khi không thể thư giãn, bạn có thấy khó ngủ không?"
        ],
        "explicit_rating": "Trên thang điểm từ 0-4, với 0 là không bao giờ và 4 là luôn luôn, bạn đánh giá mức độ khó thư giãn của mình ở đâu?"
    },
    
    "sad_feelings": {
        "category": "depression",
        "variants": [
            "Gần đây tâm trạng của bạn thế nào?",
            "Bạn có thường cảm thấy buồn bã hoặc chán nản không?",
            "Bạn có những lúc cảm thấy u uất mà không rõ lý do không?",
            "Bạn có thường cảm thấy không vui vẻ hoặc trống rỗng không?"
        ],
        "follow_ups": [
            "Cảm giác buồn bã này kéo dài bao lâu rồi?",
            "Có điều gì cụ thể gây ra cảm giác buồn bã này không?",
            "Bạn làm gì để đối phó với những cảm xúc này?"
        ],
        "transitions": [
            "Khi cảm thấy buồn, nhiều người cũng mất hứng thú với những hoạt động họ từng yêu thích. Bạn có thấy mình ít quan tâm đến những thứ trước đây bạn thích không?",
            "Tâm trạng buồn bã đôi khi có thể ảnh hưởng đến cách chúng ta nhìn nhận bản thân. Bạn có bao giờ cảm thấy không hài lòng về bản thân không?",
            "Buồn bã kéo dài đôi khi có thể ảnh hưởng đến giấc ngủ. Bạn có gặp vấn đề về giấc ngủ không?"
        ],
        "explicit_rating": "Trên thang điểm từ 0-4, với 0 là không bao giờ và 4 là luôn luôn, bạn đánh giá mức độ buồn bã hoặc chán nản của mình ở đâu?"
    },
    
    "lost_interest": {
        "category": "depression",
        "variants": [
            "Bạn vẫn duy trì được sở thích và các hoạt động bạn yêu thích chứ?",
            "Gần đây bạn có còn hứng thú với những việc bạn thường thích làm không?",
            "Bạn có thấy khó khăn khi tìm niềm vui trong các hoạt động hàng ngày không?",
            "Bạn có nhận thấy mình ít quan tâm đến những thứ trước đây từng làm bạn vui vẻ không?"
        ],
        "follow_ups": [
            "Có hoạt động nào cụ thể mà bạn đã mất hứng thú không?",
            "Bạn đã cố gắng tạo hứng thú trở lại bằng cách nào?",
            "Việc mất hứng thú này ảnh hưởng đến cuộc sống của bạn như thế nào?"
        ],
        "transitions": [
            "Việc mất hứng thú đôi khi đi kèm với cảm giác về giá trị bản thân. Bạn có bao giờ cảm thấy bản thân mình không có giá trị không?",
            "Khi mất hứng thú với những điều trước đây, nhiều người cũng cảm thấy mệt mỏi hơn. Bạn có thường xuyên cảm thấy mệt mỏi không?",
            "Mất hứng thú đôi khi có thể tác động đến cách chúng ta nhìn nhận tương lai. Bạn có cảm thấy lạc quan về tương lai không?"
        ],
        "explicit_rating": "Trên thang điểm từ 0-4, với 0 là không bao giờ và 4 là luôn luôn, bạn đánh giá mức độ mất hứng thú với những hoạt động trước đây bạn thích ở đâu?"
    },
    
    "worthless": {
        "category": "depression",
        "variants": [
            "Bạn có cảm thấy tự tin về bản thân mình không?",
            "Bạn có thường đánh giá thấp giá trị của bản thân không?",
            "Bạn có hay có những suy nghĩ tiêu cực về bản thân mình không?",
            "Bạn nghĩ gì về những đóng góp và vai trò của mình trong cuộc sống?"
        ],
        "follow_ups": [
            "Những suy nghĩ này xuất hiện trong những tình huống nào?",
            "Bạn có thể chia sẻ thêm về lý do bạn cảm thấy như vậy không?",
            "Những suy nghĩ này ảnh hưởng đến quyết định của bạn như thế nào?"
        ],
        "transitions": [
            "Cảm giác về giá trị bản thân đôi khi có thể ảnh hưởng đến cách chúng ta nhìn nhận cuộc sống. Bạn có bao giờ cảm thấy cuộc sống không đáng sống không?",
            "Khi cảm thấy không có giá trị, nhiều người cũng cảm thấy lo lắng về cách người khác nhìn nhận họ. Bạn có hay lo lắng không?",
            "Cảm giác về giá trị bản thân có thể ảnh hưởng đến giấc ngủ. Bạn có gặp vấn đề về giấc ngủ không?"
        ],
        "explicit_rating": "Trên thang điểm từ 0-4, với 0 là không bao giờ và 4 là luôn luôn, bạn đánh giá mức độ cảm thấy vô giá trị của mình ở đâu?"
    },
    
    "life_not_worth": {
        "category": "depression",
        "flag": "suicide_risk",
        "variants": [
            "Bạn có cảm thấy lạc quan về tương lai không?",
            "Bạn có bao giờ cảm thấy cuộc sống quá khó khăn đến mức không đáng để tiếp tục không?",
            "Bạn nghĩ gì về ý nghĩa của cuộc sống hiện tại?",
            "Bạn có bao giờ cảm thấy cuộc sống không còn ý nghĩa nữa không?"
        ],
        "follow_ups": [
            "Bạn có thể chia sẻ thêm về những suy nghĩ này không?",
            "Những suy nghĩ này có thường xuyên xuất hiện không?",
            "Bạn đã nói chuyện với ai về những cảm xúc này chưa?"
        ],
        "transitions": [
            "Những suy nghĩ như vậy thường đi kèm với cảm giác mệt mỏi. Bạn có thường cảm thấy kiệt sức không?",
            "Khi cảm thấy như vậy, nhiều người cũng gặp vấn đề về giấc ngủ. Bạn có gặp khó khăn khi ngủ không?",
            "Những suy nghĩ này có thể ảnh hưởng đến thói quen ăn uống. Bạn có nhận thấy sự thay đổi trong cách ăn uống của mình không?"
        ],
        "explicit_rating": "Trên thang điểm từ 0-4, với 0 là không bao giờ và 4 là luôn luôn, bạn đánh giá mức độ cảm thấy cuộc sống không đáng sống của mình ở đâu?"
    },
    
    "sleep_issues": {
        "category": "stress",
        "variants": [
            "Bạn có ngủ ngon không?",
            "Giấc ngủ của bạn gần đây thế nào?",
            "Bạn có gặp khó khăn khi đi vào giấc ngủ hoặc duy trì giấc ngủ không?",
            "Bạn có thường thức dậy quá sớm hoặc ngủ quá nhiều không?"
        ],
        "follow_ups": [
            "Vấn đề giấc ngủ này đã kéo dài bao lâu rồi?",
            "Có điều gì cụ thể gây ra vấn đề giấc ngủ của bạn không?",
            "Làm thế nào vấn đề giấc ngủ ảnh hưởng đến bạn vào ban ngày?"
        ],
        "transitions": [
            "Vấn đề về giấc ngủ thường liên quan đến thói quen ăn uống. Bạn có nhận thấy sự thay đổi trong cách ăn uống của mình không?",
            "Khi không ngủ đủ giấc, nhiều người cảm thấy lo lắng hơn. Bạn có dễ cảm thấy lo lắng không?",
            "Vấn đề giấc ngủ thường ảnh hưởng đến năng lượng. Bạn có cảm thấy mệt mỏi trong ngày không?"
        ],
        "explicit_rating": "Trên thang điểm từ 0-4, với 0 là không bao giờ và 4 là luôn luôn, bạn đánh giá mức độ gặp vấn đề về giấc ngủ (ngủ quá nhiều hoặc quá ít) của mình ở đâu?"
    },
    
    "eating_issues": {
        "category": "stress",
        "variants": [
            "Thói quen ăn uống của bạn gần đây thế nào?",
            "Bạn có nhận thấy sự thay đổi trong cảm giác ngon miệng không?",
            "Bạn có xu hướng ăn nhiều hơn hoặc ít hơn khi cảm thấy căng thẳng không?",
            "Cảm giác ngon miệng của bạn có ổn định không?"
        ],
        "follow_ups": [
            "Sự thay đổi này đã diễn ra trong bao lâu?",
            "Bạn có nhận thấy mình giảm cân hoặc tăng cân không?",
            "Thói quen ăn uống này liên quan đến tâm trạng của bạn như thế nào?"
        ],
        "transitions": [
            "Thay đổi trong thói quen ăn uống đôi khi liên quan đến cảm giác lo lắng. Bạn có hay cảm thấy lo lắng không?",
            "Thói quen ăn uống thay đổi thường đi kèm với vấn đề về giấc ngủ. Bạn có ngủ tốt không?",
            "Khi thói quen ăn uống thay đổi, nhiều người cũng nhận thấy sự thay đổi trong tâm trạng. Bạn có hay cảm thấy buồn không?"
        ],
        "explicit_rating": "Trên thang điểm từ 0-4, với 0 là không bao giờ và 4 là luôn luôn, bạn đánh giá mức độ gặp vấn đề về ăn uống (ăn quá nhiều hoặc quá ít) của mình ở đâu?"
    },
    
    "panic": {
        "category": "anxiety",
        "variants": [
            "Bạn có hay cảm thấy hoảng sợ đột ngột không?",
            "Bạn có bao giờ trải qua những khoảnh khắc sợ hãi mạnh mẽ mà không rõ nguyên nhân không?",
            "Có khi nào bạn cảm thấy lo lắng đến mức tim đập nhanh, khó thở hoặc chóng mặt không?",
            "Bạn có dễ bị giật mình hoặc cảm thấy lo sợ không?"
        ],
        "follow_ups": [
            "Những cảm giác này thường xuất hiện trong tình huống nào?",
            "Bạn cảm thấy như thế nào khi trải qua những khoảnh khắc hoảng sợ này?",
            "Bạn làm gì để đối phó khi cảm thấy hoảng sợ?"
        ],
        "transitions": [
            "Cảm giác hoảng sợ thường đi kèm với khó thư giãn. Bạn có thấy khó thư giãn không?",
            "Khi cảm thấy hoảng sợ, nhiều người lo lắng về sức khỏe của mình. Bạn có thường lo lắng không?",
            "Cảm giác hoảng sợ có thể ảnh hưởng đến giấc ngủ. Bạn có gặp vấn đề về giấc ngủ không?"
        ],
        "explicit_rating": "Trên thang điểm từ 0-4, với 0 là không bao giờ và 4 là luôn luôn, bạn đánh giá mức độ dễ bị hoảng sợ hoặc sợ hãi của mình ở đâu?"
    }
}

# Hàm truy xuất câu hỏi ngẫu nhiên theo category
def get_random_question(question_id, question_type="variants"):
    """
    Lấy câu hỏi ngẫu nhiên từ ngân hàng câu hỏi
    
    Args:
        question_id: ID của câu hỏi (ví dụ: feeling_tired)
        question_type: Loại câu hỏi (variants, follow_ups, transitions, explicit_rating)
        
    Returns:
        Một câu hỏi ngẫu nhiên thuộc loại được chỉ định
    """
    import random
    
    if question_id not in question_bank:
        return None
    
    if question_type in question_bank[question_id] and question_bank[question_id][question_type]:
        questions = question_bank[question_id][question_type]
        return random.choice(questions)
    
    return None

# Hàm lấy category của câu hỏi
def get_question_category(question_id):
    """
    Lấy category của câu hỏi
    
    Args:
        question_id: ID của câu hỏi
        
    Returns:
        Category của câu hỏi (depression, anxiety, stress) hoặc None
    """
    if question_id in question_bank:
        return question_bank[question_id].get('category')
    
    return None

# Hàm kiểm tra cờ nguy cơ
def has_risk_flag(question_id):
    """
    Kiểm tra câu hỏi có cờ nguy cơ hay không
    
    Args:
        question_id: ID của câu hỏi
        
    Returns:
        Cờ nguy cơ (suicide_risk) hoặc None
    """
    if question_id in question_bank and 'flag' in question_bank[question_id]:
        return question_bank[question_id]['flag']
    
    return None

# Danh sách IDs câu hỏi theo thứ tự ưu tiên mặc định
QUESTION_IDS = [
    "feeling_tired",
    "worried",
    "relax_difficulty",
    "sad_feelings",
    "lost_interest",
    "worthless",
    "life_not_worth",
    "sleep_issues",
    "eating_issues",
    "panic"
]