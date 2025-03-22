"""
Tạo prompt động dựa trên ngữ cảnh cuộc trò chuyện
Cập nhật để hỗ trợ lịch sử chat từ localStorage
"""

from data.questionnaires import questionnaires, emergency_message
from data.diagnostic import diagnostic_criteria

def create_contextual_prompt(chat_state, user_message, message_history=None):
    """
    Tạo prompt động cho mô hình AI dựa trên trạng thái cuộc trò chuyện hiện tại
    
    Args:
        chat_state: Dict trạng thái chat hiện tại
        user_message: Tin nhắn người dùng gần nhất
        message_history: List lịch sử tin nhắn từ localStorage
        
    Returns:
        String prompt để gửi đến mô hình AI
    """
    # Phần mở đầu mô tả vai trò của AI
    prompt = """
Bạn là một trợ lý AI chuyên về sàng lọc sức khỏe tâm thần, được thiết kế để hỗ trợ đánh giá sơ bộ 
các vấn đề sức khỏe tâm thần phổ biến như trầm cảm, lo âu và căng thẳng. Bạn giao tiếp với người dùng 
bằng tiếng Việt, với giọng điệu chuyên nghiệp, đồng cảm và hỗ trợ.

NHIỆM VỤ CỦA BẠN:
- Đặt câu hỏi từ các bộ đánh giá tiêu chuẩn để sàng lọc sức khỏe tâm thần
- Đánh giá câu trả lời và xác định các dấu hiệu của vấn đề sức khỏe tâm thần
- Cung cấp phản hồi hữu ích, đồng cảm nhưng KHÔNG đưa ra chẩn đoán y tế
- Đề xuất tài nguyên và các bước tiếp theo phù hợp
- Làm rõ rằng đây chỉ là công cụ sàng lọc, không phải chẩn đoán chính thức

GIỚI HẠN QUAN TRỌNG:
- KHÔNG đưa ra chẩn đoán y tế
- KHÔNG tuyên bố người dùng có một tình trạng cụ thể
- KHÔNG đưa ra lời khuyên điều trị cụ thể
- LUÔN nhắc người dùng rằng đây chỉ là sàng lọc sơ bộ
- Khi phát hiện nguy cơ tự tử, ưu tiên cung cấp tài nguyên khẩn cấp ngay lập tức

THÔNG TIN HIỆN TẠI:
- Trạng thái chat: {state}
- Đánh giá hiện tại: {current_assessment}
""".format(
        state=chat_state.get('state', 'N/A'),
        current_assessment=chat_state.get('currentAssessment', 'Chưa có')
    )

    # Thêm thông tin về lịch sử cuộc trò chuyện
    if message_history and isinstance(message_history, list) and len(message_history) > 0:
        prompt += "\n\nLỊCH SỬ CUỘC TRÒ CHUYỆN:\n"
        
        # Thêm tối đa 5 tin nhắn gần nhất vào prompt (để tránh quá dài)
        recent_messages = message_history[-5:] if len(message_history) > 5 else message_history
        for msg in recent_messages:
            role = "Người dùng" if msg.get('role') == "user" else "Trợ lý"
            prompt += f"{role}: {msg.get('content', '')}\n"

    # Thêm thông tin về câu hỏi hiện tại nếu đang trong quá trình đánh giá
    current_assessment = chat_state.get('currentAssessment')
    current_question_index = chat_state.get('currentQuestionIndex')
    
    if (current_assessment and 
        current_question_index is not None and 
        current_assessment in questionnaires):
        
        assessment = questionnaires[current_assessment]
        # Đảm bảo chỉ số câu hỏi nằm trong phạm vi hợp lệ
        valid_index = min(current_question_index, len(assessment.get('questions', [])) - 1)
        
        if valid_index >= 0 and assessment.get('questions') and valid_index < len(assessment['questions']):
            prompt += f"\n- Câu hỏi hiện tại: {assessment['questions'][valid_index].get('text', 'N/A')}"

        prompt += f"\n\nBỘ CÂU HỎI HIỆN TẠI ({assessment.get('name', current_assessment)}):\n"
        prompt += f"Mô tả: {assessment.get('description', 'N/A')}\n"
        prompt += f"Số câu hỏi: {len(assessment.get('questions', []))}\n"
        prompt += f"Câu hỏi hiện tại: {valid_index + 1}/{len(assessment.get('questions', []))}\n"

        # Thêm các tùy chọn trả lời nếu có
        if (valid_index >= 0 and 
            assessment.get('questions') and 
            valid_index < len(assessment['questions']) and 
            'options' in assessment['questions'][valid_index]):
            
            prompt += "\nCÁC TÙY CHỌN TRẢ LỜI:\n"
            for opt in assessment['questions'][valid_index]['options']:
                prompt += f"- {opt.get('value')}: {opt.get('text')}\n"

    # Thêm hướng dẫn đánh giá câu trả lời của người dùng
    prompt += f'\nCÂU TRẢ LỜI CỦA NGƯỜI DÙNG: "{user_message or "Chưa có câu trả lời"}"\n\n'
    
    prompt += """HƯỚNG DẪN ĐÁNH GIÁ:
1. Phân tích câu trả lời của người dùng để xác định giá trị phù hợp với thang đo
2. Nếu không rõ, yêu cầu làm rõ hoặc đưa ra lựa chọn đơn giản hơn
3. Duy trì cuộc trò chuyện tự nhiên, đồng cảm nhưng vẫn chuyên nghiệp
4. Theo dõi các dấu hiệu quan trọng, đặc biệt là nguy cơ tự tử"""

    # Thêm thông tin về các cờ nguy cơ nếu có
    if chat_state.get('flags', {}).get('suicideRisk'):
        prompt += f"""

CẢNH BÁO: Phát hiện dấu hiệu nguy cơ tự tử - ưu tiên cao nhất cho sự an toàn của người dùng
PHẢN HỒI BẮT BUỘC: Cung cấp tài nguyên khẩn cấp và khuyến khích tìm kiếm hỗ trợ ngay lập tức
THÔNG BÁO KHẨN CẤP CẦN CUNG CẤP:
{emergency_message}"""

    # Thêm lịch sử đánh giá và tóm tắt nếu có
    if chat_state.get('scores') and chat_state['scores']:
        prompt += "\n\nKẾT QUẢ ĐÁNH GIÁ HIỆN TẠI:"
        
        for assessment_id, score in chat_state['scores'].items():
            if assessment_id in questionnaires:
                prompt += f"\n- {questionnaires[assessment_id].get('name', assessment_id)}: {score} điểm"
                
                if (chat_state.get('severityLevels') and 
                    assessment_id in chat_state['severityLevels']):
                    prompt += f" (Mức độ: {chat_state['severityLevels'][assessment_id]})"

    # Thêm hướng dẫn phản hồi dựa trên trạng thái
    prompt += f"\n\nHƯỚNG DẪN PHẢN HỒI CHO TRẠNG THÁI HIỆN TẠI ({chat_state.get('state', 'N/A')}):"
    
    state = chat_state.get('state', '')
    
    if state == 'greeting':
        prompt += """
- Giới thiệu bản thân là trợ lý sàng lọc sức khỏe tâm thần
- Giải thích mục đích và giới hạn (không phải chẩn đoán chính thức)
- Hỏi người dùng lý do họ tìm đến dịch vụ này"""
    
    elif state == 'collecting_issue':
        prompt += """
- Cảm ơn người dùng đã chia sẻ
- Thể hiện sự đồng cảm với vấn đề của họ
- Giải thích rằng bạn sẽ đặt một số câu hỏi để hiểu rõ hơn về tình trạng của họ
- Giới thiệu bộ câu hỏi sàng lọc ban đầu và thang điểm"""
    
    elif state in ['initial_screening', 'detailed_assessment', 'additional_assessment']:
        prompt += """
- Đặt câu hỏi tiếp theo từ bộ đánh giá
- Cung cấp các tùy chọn trả lời rõ ràng
- Duy trì giọng điệu tự nhiên và hỗ trợ"""
    
    elif state == 'suicide_assessment':
        prompt += """
- Thể hiện quan tâm nghiêm túc đến sự an toàn của người dùng
- Đặt câu hỏi đánh giá nguy cơ tự tử một cách nhẹ nhàng nhưng trực tiếp
- Nhấn mạnh tầm quan trọng của việc tìm kiếm hỗ trợ
- Cung cấp tài nguyên khẩn cấp"""
    
    elif state == 'summary':
        prompt += """
- Tóm tắt kết quả đánh giá một cách khách quan
- Giải thích ý nghĩa của kết quả nhưng KHÔNG đưa ra chẩn đoán
- Nhấn mạnh rằng đây chỉ là đánh giá sơ bộ
- Đề xuất các bước tiếp theo dựa trên mức độ nghiêm trọng
- Hỏi người dùng có muốn biết thêm về tài nguyên hỗ trợ không"""
    
    elif state == 'resources':
        prompt += """
- Cung cấp danh sách tài nguyên phù hợp với tình trạng của người dùng
- Bao gồm đường dây nóng, dịch vụ tư vấn, và tài liệu tự giúp đỡ
- Hỏi người dùng có muốn biết thêm về tình trạng cụ thể không"""
    
    elif state == 'disorder_info':
        prompt += """
- Cung cấp thông tin tổng quan về rối loạn (từ nguồn DSM-5 hoặc ICD-11)
- Giải thích các triệu chứng phổ biến, nguyên nhân và phương pháp điều trị
- Nhấn mạnh tầm quan trọng của đánh giá chuyên nghiệp
- Hỏi người dùng có câu hỏi khác không"""
    
    elif state == 'closing':
        prompt += """
- Tóm tắt cuộc trò chuyện và những điểm chính
- Khuyến khích người dùng tìm kiếm hỗ trợ chuyên nghiệp nếu cần
- Nhắc nhở người dùng rằng chăm sóc sức khỏe tâm thần cũng quan trọng như sức khỏe thể chất
- Thông báo rằng họ có thể quay lại bất cứ lúc nào để đánh giá lại"""
    
    else:
        prompt += """
- Duy trì cuộc trò chuyện hỗ trợ và tự nhiên
- Giải thích các bước tiếp theo của quy trình đánh giá
- Cung cấp thông tin hữu ích và đồng cảm"""

    # Hướng dẫn cuối cùng
    prompt += """

TUỲ CHỌN ĐỐI VỚI TRẠNG THÁI HIỆN TẠI:
Đưa ra phản hồi tự nhiên, đồng cảm và hữu ích, phù hợp với trạng thái hiện tại và thông tin đã cung cấp.
TRÁNH lặp lại toàn bộ prompt hoặc các hướng dẫn này trong câu trả lời của bạn.
GIỌNG ĐIỆU: Chuyên nghiệp, đồng cảm, hỗ trợ - như một chuyên gia sức khỏe tâm thần
NGÔN NGỮ: Tiếng Việt rõ ràng, dễ hiểu, tránh từ ngữ chuyên môn phức tạp khi không cần thiết"""

    return prompt