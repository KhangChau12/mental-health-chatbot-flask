"""
Cấu hình cho ứng dụng Flask
"""

import os
from dotenv import load_dotenv

# Nạp biến môi trường từ file .env
load_dotenv()

# Cấu hình chung
class Config:
    # Cấu hình Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-should-be-changed-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG') or False
    
    # Cấu hình Together AI
    TOGETHER_API_KEY = os.environ.get('TOGETHER_API_KEY') or '148568d44f2a7007651f0d3a035db1981348ccc61be4fb5470613d4599b85aff'
    TOGETHER_MODEL = os.environ.get('TOGETHER_MODEL') or 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'
    
    # Cấu hình session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 phút

    # Giá trị mặc định cho tham số AI
    AI_MAX_TOKENS = 1000
    AI_TEMPERATURE = 0.7
    AI_TOP_P = 0.7
    AI_TOP_K = 50
    AI_REPETITION_PENALTY = 1.0
    AI_STOP = ["<|eot_id|>", "<|eom_id|>"]