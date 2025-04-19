"""
Xử lý Together AI API
Cập nhật để sử dụng API mới
"""

import logging
from together import Together
from config import Config

logger = logging.getLogger(__name__)

# Biến toàn cục để lưu client
client = None

def initialize_together_client():
    """
    Khởi tạo Together client
    
    Returns:
        bool: True nếu khởi tạo thành công, False nếu có lỗi
    """
    try:
        # Khởi tạo client với API key
        global client
        client = Together(api_key=Config.TOGETHER_API_KEY)
        logger.info("Together client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing Together client: {str(e)}")
        return False

def generate_chat_completion(messages, contextual_prompt=None):
    """
    Tạo phản hồi chat từ mô hình AI
    
    Args:
        messages (list): Danh sách các tin nhắn trong cuộc trò chuyện
        contextual_prompt (str, optional): Prompt hệ thống tùy chỉnh
        
    Returns:
        dict: Phản hồi từ API hoặc None nếu có lỗi
    """
    try:
        # Kiểm tra client đã được khởi tạo chưa
        global client
        if client is None:
            initialize_together_client()
        
        # Chuẩn bị messages cho API
        api_messages = []
        
        # Thêm system prompt nếu có
        if contextual_prompt:
            api_messages.append({
                "role": "system",
                "content": contextual_prompt
            })
        
        # Thêm tin nhắn người dùng
        for msg in messages:
            # Sửa đổi ở đây: Chuyển đổi 'bot' thành 'assistant'
            role = msg.get("role", "user")
            if role == "bot":
                role = "assistant"
            
            api_messages.append({
                "role": role,
                "content": msg.get("content", "")
            })
        
        # Gọi API Together với cú pháp mới
        response = client.chat.completions.create(
            model=Config.TOGETHER_MODEL,
            messages=api_messages,
            max_tokens=Config.AI_MAX_TOKENS,
            temperature=Config.AI_TEMPERATURE,
            top_p=Config.AI_TOP_P,
            top_k=Config.AI_TOP_K,
            repetition_penalty=Config.AI_REPETITION_PENALTY,
            stop=Config.AI_STOP
        )
        
        logger.info("Together API response received")
        return response
        
    except Exception as e:
        logger.error(f"Error using Together API: {str(e)}")
        return None

def extract_text_from_response(response):
    """
    Trích xuất nội dung văn bản từ phản hồi API
    
    Args:
        response: Phản hồi từ Together API
        
    Returns:
        str: Nội dung phản hồi hoặc thông báo lỗi
    """
    try:
        if not response:
            return "Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn."
            
        text = response.choices[0].message.content
        return text
    except Exception as e:
        logger.error(f"Error extracting text from API response: {str(e)}")
        return "Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn."