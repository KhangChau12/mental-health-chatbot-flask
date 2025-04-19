"""
Tạo prompt động dựa trên ngữ cảnh cuộc trò chuyện
Hỗ trợ cả chế độ trò chuyện tự nhiên và giao diện poll
"""

import logging
import datetime
from data.questionnaires import questionnaires, emergency_message
from data.question_bank import question_bank, get_random_question, get_question_category, has_risk_flag, QUESTION_IDS
from data.conversation_map import get_next_question
from data.diagnostic import diagnostic_criteria
from utils.chat_logic import format_chat_history

logger = logging.getLogger(__name__)

def create_contextual_prompt(chat_state, user_message, message_history=None):
    """
    Tạo prompt động cho mô hình AI dựa trên trạng thái cuộc trò chuyện hiện tại
    
    Args:
        chat_state: Dict trạng thái chat hiện tại
        user_message: String tin nhắn người dùng gần nhất
        message_history: List lịch sử tin nhắn từ localStorage
        
    Returns:
        String prompt để gửi đến mô hình AI
    """
    # Xác định chế độ giao diện hiện tại
    interface_mode = chat_state.get('interfaceMode', 'chat')
    
    # Phần mở đầu mô tả vai trò của AI
    prompt = """
Bạn là một trợ lý AI chuyên về sàng lọc sức khỏe tâm thần, được thiết kế để hỗ trợ đánh giá sơ bộ 
các vấn đề sức khỏe tâm thần phổ biến như trầm cảm, lo âu và căng thẳng. Bạn giao tiếp với người dùng 
bằng tiếng Việt, với giọng điệu chuyên nghiệp, đồng cảm và hỗ trợ.

NHIỆM VỤ CỦA BẠN:
- Tạo cảm giác đang trò chuyện tự nhiên, như một nhà trị liệu thực sự
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
- Chế độ giao diện: {interface}
- Đánh giá hiện tại: {current_assessment}
""".format(
        state=chat_state.get('state', 'N/A'),
        interface=interface_mode,
        current_assessment=chat_state.get('currentAssessment', 'Chưa có')
    )
    
    # Thêm hướng dẫn về phong cách trả lời
    prompt += """
HƯỚNG DẪN VỀ PHONG CÁCH TRẢ LỜI:
- Giữ phản hồi NGẮN GỌN và TẬP TRUNG - tối đa 2-3 câu cho mỗi ý
- Thể hiện sự đồng cảm nhưng TRÁNH lặp lại những lời động viên giống nhau
- Đặt câu hỏi TRỰC TIẾP sau khi phản hồi ngắn gọn thay vì nhiều lời dẫn dắt
- Khi người dùng đã chia sẻ đủ về một chủ đề, hãy CHUYỂN SANG chủ đề tiếp theo ngay lập tức
- Ưu tiên câu hỏi mở đầu ngắn gọn, đi thẳng vào vấn đề
- QUAN TRỌNG: Đừng để người dùng cảm thấy đang bị khảo sát - duy trì đối thoại tự nhiên nhưng hiệu quả
"""
    
    # Thêm hướng dẫn cụ thể cho chế độ trò chuyện tự nhiên
    if interface_mode == 'chat' and chat_state.get('state') == 'natural_conversation':
        current_question_id = chat_state.get('currentQuestionId')
        if current_question_id and current_question_id in question_bank:
            question_info = question_bank[current_question_id]
            prompt += f"""
CHẾ ĐỘ TRÒ CHUYỆN TỰ NHIÊN:
- Câu hỏi hiện tại: {current_question_id} (Chủ đề: {question_info.get('category', 'N/A')})
- Cách tiếp cận: Đặt câu hỏi tự nhiên, không phải dạng khảo sát
- Độ ưu tiên: Tạo cuộc trò chuyện tự nhiên, KHÔNG yêu cầu đánh giá mức 0-4 trừ khi cần thiết
- Biến đổi cách hỏi: Sử dụng nhiều cách diễn đạt khác nhau
- Phản ứng với câu trả lời: Thể hiện sự đồng cảm ngắn gọn, sau đó chuyển sang chủ đề tiếp theo một cách tự nhiên

GỢI Ý KỸ THUẬT TRÒ CHUYỆN:
1. Thừa nhận cảm xúc ngắn gọn: "Tôi hiểu điều đó khó khăn"
2. Đào sâu khi cần: Khi phát hiện vấn đề, hỏi thêm một câu ngắn gọn và chuyển chủ đề
3. Giữ cuộc trò chuyện luân chuyển, tránh để người dùng cảm thấy đang làm khảo sát
"""

    # Thêm hướng dẫn cụ thể cho chế độ poll
    elif interface_mode == 'poll':
        prompt += """
CHẾ ĐỘ POLL:
- Phương pháp: Sử dụng các câu hỏi tiêu chuẩn với các lựa chọn cụ thể
- Nhiệm vụ: Cung cấp phản hồi tự nhiên nhằm hướng dẫn người dùng qua bộ câu hỏi
- Giọng điệu: Đồng cảm, chuyên nghiệp, rõ ràng
- Giải thích: Giải thích rõ ý nghĩa của các câu hỏi khi cần thiết
- Chuyển tiếp: Khi hoàn thành, thông báo chuyển từ poll trở lại trò chuyện tự nhiên
"""

    # Thêm thông tin về lịch sử cuộc trò chuyện
    if message_history and isinstance(message_history, list) and len(message_history) > 0:
        prompt += "\n\nLỊCH SỬ CUỘC TRÒ CHUYỆN:\n"
        
        # Thêm nhiều tin nhắn gần nhất vào prompt để tạo ngữ cảnh tốt hơn
        recent_messages = message_history[-15:] if len(message_history) > 15 else message_history
        for msg in recent_messages:
            role = "Người dùng" if msg.get('role') == "user" else "Trợ lý"
            prompt += f"{role}: {msg.get('content', '')}\n"
    
    # Thêm thông tin về trò chuyện tự nhiên
    if interface_mode == 'chat' and chat_state.get('state') == 'natural_conversation':
        natural_convo = chat_state.get('naturalConversation', {})
        asked_questions = natural_convo.get('askedQuestions', [])
        scores = natural_convo.get('scores', {})
        
        next_question_id = get_next_question(
            chat_state.get('currentQuestionId'), 
            scores, 
            asked_questions
        )
        
        prompt += f"""
TIẾN TRÌNH THU THẬP THÔNG TIN:
- Đã thu thập: {', '.join(asked_questions) if asked_questions else 'Chưa có'}
- Cần thu thập: {', '.join([q_id for q_id in QUESTION_IDS if q_id not in asked_questions])}
- Câu hỏi ưu tiên tiếp theo: {next_question_id or "Hoàn thành"}

CHIẾN LƯỢC PHỎNG VẤN:
1. HỎI thông tin về các chủ đề cần thiết một cách tự nhiên
2. ĐÁNH GIÁ mức độ dựa trên câu trả lời
3. CHUYỂN sang chủ đề tiếp theo khi đã có đủ thông tin
4. TRÁNH sa đà quá lâu vào một chủ đề cụ thể

QUAN TRỌNG: Thông tin này chỉ để bạn theo dõi nội bộ, ĐỪNG đề cập đến nó trong cuộc trò chuyện với người dùng.
"""

        # Thêm tóm tắt câu trả lời đã thu thập nếu có
        if scores:
            prompt += "\nTÓM TẮT CÂU TRẢ LỜI ĐÃ THU THẬP:\n"
            for q_id, score in scores.items():
                prompt += f"- {q_id}: Điểm {score}\n"
        
        if asked_questions:
            prompt += "\n\nCÁC CÂU HỎI ĐÃ HỎI TRONG TRÒ CHUYỆN TỰ NHIÊN:\n"
            for q_id in asked_questions:
                score_text = f" (Điểm: {scores.get(q_id, 'chưa đánh giá')})" if q_id in scores else ""
                prompt += f"- {q_id}{score_text}\n"
    
    # Thêm thông tin về câu hỏi hiện tại nếu đang trong chế độ poll
    elif interface_mode == 'poll':
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
    
    if interface_mode == 'chat' and chat_state.get('state') == 'natural_conversation':
        prompt += """HƯỚNG DẪN ĐÁNH GIÁ TRONG CHẾ ĐỘ TRÒ CHUYỆN TỰ NHIÊN:
1. Phân tích câu trả lời của người dùng để xác định mức độ nghiêm trọng (0-4)
2. Đánh giá ngầm: KHÔNG yêu cầu người dùng cung cấp mức độ 0-4 trực tiếp
3. Duy trì cuộc trò chuyện tự nhiên, tránh cảm giác đang làm khảo sát
4. Theo dõi các dấu hiệu quan trọng, đặc biệt là nguy cơ tự tử
5. Phản hồi ngắn gọn và đồng cảm, sau đó chuyển sang chủ đề tiếp theo"""
    else:
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

    # Thêm hướng dẫn phản hồi dựa trên trạng thái và chế độ
    prompt += f"\n\nHƯỚNG DẪN PHẢN HỒI CHO TRẠNG THÁI HIỆN TẠI ({chat_state.get('state', 'N/A')}):"
    
    state = chat_state.get('state', '')
    
    if state == 'greeting':
        prompt += """
- Giới thiệu bản thân ngắn gọn là trợ lý sàng lọc sức khỏe tâm thần
- Giải thích ngắn gọn mục đích và giới hạn (không phải chẩn đoán chính thức)
- Hỏi trực tiếp lý do họ tìm đến dịch vụ này"""
    
    elif state == 'collecting_issue':
        prompt += """
- Cảm ơn người dùng đã chia sẻ ngắn gọn
- Thể hiện sự đồng cảm ngắn gọn với vấn đề của họ
- Giải thích ngắn gọn rằng bạn sẽ đặt một số câu hỏi 
- Giới thiệu cách tiếp cận trò chuyện tự nhiên"""
    
    elif state == 'natural_conversation':
        prompt += """
CHẾ ĐỘ TRÒ CHUYỆN TỰ NHIÊN:
- Tạo cuộc trò chuyện TỰ NHIÊN, kéo dài (~20 lượt trao đổi) để thu thập đủ thông tin
- PHONG CÁCH: Giống như bạn bè nói chuyện, TRÁNH cảm giác đang làm bảng khảo sát
- CHIẾN LƯỢC THU THẬP THÔNG TIN:
  1. ĐẶT các câu hỏi MỞ, không trực tiếp yêu cầu người dùng đánh giá 0-4
  2. ĐÀO SÂU khi thấy manh mối về vấn đề
  3. THỂ HIỆN ĐỒNG CẢM tự nhiên trước khi chuyển chủ đề
  4. Khi đã thử 2 lần mà vẫn không đủ thông tin để đánh giá, chỉ khi đó mới HỎI TRỰC TIẾP về mức độ 0-4
  
QUAN TRỌNG VỀ CHUYỂN CHỦ ĐỀ:
- KHÔNG chuyển chủ đề đột ngột
- Sử dụng các CÂU CHUYỂN TIẾP tự nhiên, kết nối giữa chủ đề cũ và mới
- Đảm bảo người dùng không cảm thấy đang bị hỏi theo mẫu có sẵn
"""
    
    elif state == 'poll_interaction':
        prompt += """
- Trả lời rõ ràng, chuyên nghiệp nhưng NGẮN GỌN
- Giải thích tầm quan trọng của từng câu hỏi TỐI THIỂU
- Hướng dẫn người dùng chọn tùy chọn phù hợp nhất
- Giới thiệu câu hỏi tiếp theo một cách tự nhiên"""
    
    elif state in ['initial_screening', 'detailed_assessment', 'additional_assessment']:
        prompt += """
- Đặt câu hỏi tiếp theo từ bộ đánh giá NGẮN GỌN
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
- Tóm tắt ngắn gọn kết quả đánh giá một cách khách quan
- TRÁNH đưa ra chẩn đoán, chỉ nói về các dấu hiệu và mức độ
- Nhấn mạnh rằng đây chỉ là đánh giá sơ bộ
- Đề xuất các bước tiếp theo dựa trên mức độ nghiêm trọng"""
    
    elif state == 'resources':
        prompt += """
- Cung cấp danh sách tài nguyên phù hợp NGẮN GỌN
- Tập trung vào các tài nguyên phù hợp nhất với tình trạng người dùng
- Hỏi người dùng có muốn biết thêm về tình trạng cụ thể không"""
    
    elif state == 'disorder_info':
        prompt += """
- Cung cấp thông tin tổng quan NGẮN GỌN về rối loạn
- Nhấn mạnh tầm quan trọng của đánh giá chuyên nghiệp
- Hỏi người dùng có câu hỏi khác không"""
    
    elif state == 'closing':
        prompt += """
- Tóm tắt cuộc trò chuyện NGẮN GỌN
- Khuyến khích người dùng tìm kiếm hỗ trợ chuyên nghiệp nếu cần
- Nhắc nhở người dùng rằng họ có thể quay lại bất cứ lúc nào"""
    
    else:
        prompt += """
- Duy trì cuộc trò chuyện hỗ trợ và tự nhiên
- Giải thích các bước tiếp theo của quy trình đánh giá
- Cung cấp thông tin hữu ích và đồng cảm"""

    # Hướng dẫn cuối cùng
    prompt += """

TUỲ CHỌN ĐỐI VỚI TRẠNG THÁI HIỆN TẠI:
Đưa ra phản hồi tự nhiên, đồng cảm và NGẮN GỌN, phù hợp với trạng thái hiện tại và thông tin đã cung cấp.
TRÁNH lặp lại toàn bộ prompt hoặc các hướng dẫn này trong câu trả lời của bạn.
GIỌNG ĐIỆU: Chuyên nghiệp, đồng cảm, hỗ trợ - như một chuyên gia sức khỏe tâm thần thực sự
NGÔN NGỮ: Tiếng Việt rõ ràng, dễ hiểu, tự nhiên, tránh từ ngữ chuyên môn phức tạp khi không cần thiết

ƯU TIÊN CAO NHẤT: Giữ phản hồi NGẮN GỌN, TRỰC TIẾP, HIỆU QUẢ."""

    return prompt

def create_evaluation_prompt(chat_history, question_id):
    """
    Tạo prompt để đánh giá mức độ của một câu hỏi dựa trên toàn bộ cuộc trò chuyện
    
    Args:
        chat_history: Lịch sử trò chuyện
        question_id: ID của câu hỏi cần đánh giá
        
    Returns:
        str: Prompt để gửi tới AI để đánh giá
    """
    # Lấy thông tin câu hỏi
    question_info = question_bank.get(question_id, {})
    category = question_info.get('category', 'unknown')
    question_texts = question_info.get('variants', [''])
    
    prompt = f"""
NHIỆM VỤ: Phân tích cuộc trò chuyện và xác định mức độ (0-4) mà người dùng đang trải qua đối với vấn đề sau:

VẤN ĐỀ: {question_id} (Loại: {category})
MÔ TẢ: {question_texts[0] if question_texts else ''}

THANG ĐIỂM:
0: Không bao giờ/Không có - Người dùng không có biểu hiện của vấn đề này
1: Hiếm khi/Nhẹ - Người dùng hiếm khi gặp phải, ảnh hưởng rất ít
2: Thỉnh thoảng/Trung bình - Người dùng đôi khi gặp phải, có một số ảnh hưởng
3: Thường xuyên/Đáng kể - Người dùng thường xuyên gặp phải, ảnh hưởng đáng kể
4: Luôn luôn/Nghiêm trọng - Người dùng liên tục gặp phải, ảnh hưởng nghiêm trọng

CUỘC TRÒ CHUYỆN:
{format_chat_history(chat_history)}

CÂU HỎI MỞ RỘNG:
1. Người dùng có đề cập trực tiếp hoặc gián tiếp đến vấn đề này không?
2. Người dùng có miêu tả mức độ nghiêm trọng không?
3. Mức độ ảnh hưởng của vấn đề này đến cuộc sống của họ?

CHỈ TRẢ VỀ MỘT CON SỐ (0, 1, 2, 3 hoặc 4) dựa trên bằng chứng từ cuộc trò chuyện. Không cần giải thích.
"""
    return prompt