# Kiến trúc và Kỹ thuật của Chatbot Sức khỏe Tâm thần

## Tổng quan dự án

Chatbot Sức khỏe Tâm thần là một ứng dụng web sàng lọc sức khỏe tâm thần, được xây dựng trên Flask và hỗ trợ hai phương thức tương tác khác nhau: phiên bản Poll thuần túy và phiên bản AI kết hợp chat. Phiên bản AI tích hợp với mô hình Llama 3.3 70B thông qua Together AI. Ứng dụng được thiết kế để cung cấp công cụ sàng lọc ban đầu về các vấn đề sức khỏe tâm thần phổ biến như trầm cảm, lo âu và căng thẳng, với trọng tâm là hỗ trợ tiếng Việt.

## Kiến trúc hệ thống

### 1. Kiến trúc tổng thể

Dự án được xây dựng theo mô hình MVC (Model-View-Controller) với hai phiên bản giao diện người dùng:

- **Backend**: Flask (Python)
- **Frontend**: 
  - Phiên bản Poll: HTML, CSS, JavaScript
  - Phiên bản AI: HTML, CSS, JavaScript + Together AI
- **Database**: Hiện tại sử dụng lưu trữ tạm thời (session storage và localStorage)
- **AI Integration**: Together AI API (Llama 3.3 70B) - chỉ cho phiên bản AI

### 2. Cấu trúc thư mục

```
mental-health-chatbot-flask/
├── app.py                  # File Flask chính (với routes cho cả 2 phiên bản)
├── config.py               # Cấu hình
├── static/                 # Tài nguyên tĩnh (CSS, JS, images)
│   ├── css/
│   │   └── style.css       # Stylesheet chung
│   ├── js/
│   │   ├── chat.js         # JavaScript cho phiên bản AI
│   │   └── logic.js        # JavaScript cho phiên bản Poll
│   └── images/
├── templates/              # Templates HTML
│   ├── base.html           # Template cơ sở
│   ├── index.html          # Giao diện phiên bản AI
│   ├── logic.html          # Giao diện phiên bản Poll
│   └── home.html           # Trang chọn phiên bản
├── utils/                  # Các module tiện ích
│   ├── together_ai.py      # Xử lý Together AI API
│   ├── chat_logic.py       # Logic điều khiển luồng chat
│   ├── logic_poll.py       # Logic điều khiển luồng poll thuần túy
│   ├── scoring.py          # Tính điểm và xác định mức độ
│   └── contextual_prompt.py # Tạo prompt cho AI
├── data/                   # Dữ liệu cho ứng dụng
│   ├── questionnaires.py   # Dữ liệu bộ câu hỏi
│   ├── question_bank.py    # Ngân hàng câu hỏi tự nhiên
│   ├── conversation_map.py # Bản đồ trò chuyện
│   ├── resources.py        # Tài nguyên hỗ trợ
│   └── diagnostic.py       # Tiêu chí chẩn đoán
```

## Hai phiên bản tương tác

### 1. Phiên bản Poll (Logic Mode)

- **Truy cập**: `/logic`
- **Đặc điểm**:
  - Giao diện poll trắc nghiệm thuần túy
  - Không sử dụng AI
  - Luồng xử lý tuyến tính và xác định
  - Tập trung vào việc thu thập dữ liệu nhanh chóng
  - Bắt đầu ngay với bộ sàng lọc ban đầu, bỏ qua giai đoạn trò chuyện

### 2. Phiên bản AI (Chat Mode)

- **Truy cập**: `/ai`
- **Đặc điểm**:
  - Kết hợp chat tự nhiên và poll
  - Tích hợp với Together AI (Llama 3.3 70B)
  - Mô phỏng trò chuyện tự nhiên với chuyên gia
  - Thu thập dữ liệu thông qua cuộc trò chuyện
  - Chuyển sang poll cho các đánh giá chuyên sâu

### 3. Trang chọn phiên bản

- **Truy cập**: `/` (trang chủ)
- **Đặc điểm**:
  - Cho phép người dùng lựa chọn phiên bản họ muốn sử dụng
  - Mô tả ngắn gọn đặc điểm của mỗi phiên bản
  - Thiết kế thân thiện với người dùng

## Kỹ thuật điều hướng trò chuyện

### 1. Phiên bản Poll (Logic Mode)

Sử dụng máy trạng thái (state machine) đơn giản với các trạng thái:
```python
POLL_STATES = {
    'GREETING': 'greeting',
    'INITIAL_SCREENING': 'initial_screening',
    'DETAILED_ASSESSMENT': 'detailed_assessment',
    'ADDITIONAL_ASSESSMENT': 'additional_assessment',
    'SUICIDE_ASSESSMENT': 'suicide_assessment',
    'SUMMARY': 'summary',
    'RESOURCES': 'resources'
}
```

Quy trình xử lý:
1. Bắt đầu với màn hình chào mừng
2. Chuyển thẳng đến bộ sàng lọc ban đầu (initialScreening)
3. Dựa vào kết quả, chuyển đến đánh giá chi tiết hoặc tổng kết
4. Hiển thị tài nguyên phù hợp
5. Toàn bộ giao diện dưới dạng poll với các tùy chọn trắc nghiệm

### 2. Phiên bản AI (Chat Mode)

Kết hợp máy trạng thái và LLM:
```python
CHAT_STATES = {
    'GREETING': 'greeting',
    'COLLECTING_ISSUE': 'collecting_issue',
    'NATURAL_CONVERSATION': 'natural_conversation',
    'POLL_INTERACTION': 'poll_interaction',
    'INITIAL_SCREENING': 'initial_screening',
    'DETAILED_ASSESSMENT': 'detailed_assessment',
    'ADDITIONAL_ASSESSMENT': 'additional_assessment',
    'SUICIDE_ASSESSMENT': 'suicide_assessment',
    'SUMMARY': 'summary',
    'RESOURCES': 'resources',
    'DISORDER_INFO': 'disorder_info',
    'CLOSING': 'closing'
}
```

Quy trình xử lý:
1. Bắt đầu với chat tự nhiên (greeting, collecting_issue)
2. Chuyển sang natural_conversation để thu thập dữ liệu từ 10 câu hỏi ban đầu
3. Phân tích câu trả lời tự nhiên và chuyển thành điểm số
4. Chuyển sang poll_interaction cho các bộ đánh giá chuyên sâu
5. Trở lại chat cho phần tổng kết và tài nguyên

## Bản đồ trò chuyện tự nhiên

Đối với phiên bản AI, hệ thống sử dụng bản đồ trò chuyện (conversation map) để chuyển tiếp giữa các chủ đề một cách tự nhiên:

```python
CONVERSATION_MAP = {
    "greeting": {
        "next": ["feeling_tired", "worried", "sad_feelings"],
        "transition_conditions": {}
    },
    
    "feeling_tired": {
        "next": ["sleep_issues", "sad_feelings", "worried"],
        "transition_conditions": {
            "high_score": "sad_feelings"
        }
    },
    ...
}
```

Bản đồ này cho phép:
- Xác định chủ đề tiếp theo dựa trên điểm số và chủ đề hiện tại
- Tạo cảm giác trò chuyện tự nhiên thay vì khảo sát tuyến tính
- Ưu tiên các chủ đề dựa trên phản hồi của người dùng

## Contextual Prompt Engineering

Trong phiên bản AI, hệ thống xây dựng prompt động cho LLM dựa trên:

- Trạng thái hiện tại của cuộc trò chuyện
- Lịch sử trò chuyện gần đây
- Thông tin về câu hỏi và đánh giá hiện tại
- Kết quả và điểm số đã tích lũy

```python
prompt = f"""
Bạn là một trợ lý AI chuyên về sàng lọc sức khỏe tâm thần, được thiết kế để hỗ trợ đánh giá sơ bộ 
các vấn đề sức khỏe tâm thần phổ biến như trầm cảm, lo âu và căng thẳng. Bạn giao tiếp với người dùng 
bằng tiếng Việt, với giọng điệu chuyên nghiệp, đồng cảm và hỗ trợ.

THÔNG TIN HIỆN TẠI:
- Trạng thái chat: {state}
- Chế độ giao diện: {interface}
- Đánh giá hiện tại: {current_assessment}
...
"""
```

## Xử lý API và Endpoints

### 1. Endpoints chung

- `/`: Trang chủ, cho phép chọn phiên bản
- `/api/restart`: Khởi động lại trò chuyện/khảo sát

### 2. Endpoints riêng

**Phiên bản Poll:**
- `/logic`: Route cho giao diện poll
- `/api/poll_flow`: Xử lý luồng poll thuần túy

**Phiên bản AI:**
- `/ai`: Route cho giao diện chat + poll
- `/api/send_message`: Xử lý tin nhắn chat

## Kỹ thuật quản lý state và storage

### 1. Phiên bản Poll (Logic Mode)

**Server-side State:**
```python
{
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
```

**Client-side Storage:**
- Lưu trạng thái poll trong localStorage
- Lưu lịch sử câu trả lời

### 2. Phiên bản AI (Chat Mode)

**Server-side State:**
```python
{
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
    'interfaceMode': 'chat',
    'botMessage': '...'
}
```

**Client-side Storage:**
- Lưu lịch sử trò chuyện và trạng thái trong localStorage
- Đồng bộ trạng thái giữa client và server

## Xử lý nguy cơ (Risk Handling)

Hệ thống có cơ chế phát hiện và can thiệp tự động khi phát hiện nguy cơ tự tử:

1. **Phát hiện nguy cơ**:
   - Xác định câu hỏi có cờ `suicide_risk`
   - Kiểm tra phản hồi vượt ngưỡng

2. **Can thiệp tự động**:
   - Chuyển sang `SUICIDE_ASSESSMENT`
   - Cung cấp thông báo khẩn cấp và tài nguyên
   - Hiển thị đường dây nóng và hướng dẫn hỗ trợ

## Tính năng chuyển đổi khi lỗi

Khi phiên bản AI gặp lỗi, hệ thống cung cấp cơ chế chuyển sang phiên bản Poll:

```javascript
function showErrorMessage(errorMessage) {
    // ...
    retryButton.textContent = "Chuyển sang phiên bản Poll";
    retryButton.addEventListener('click', function() {
        // Chuyển hướng sang phiên bản poll
        window.location.href = '/logic';
    });
    // ...
}
```

## Tổng kết

Chatbot Sức khỏe Tâm thần cung cấp hai phương thức tương tác khác nhau:

1. **Phiên bản Poll (Logic Mode)**:
   - Đơn giản, nhanh chóng và hiệu quả
   - Phù hợp với người dùng ưu tiên tốc độ và tính trực tiếp
   - Không phụ thuộc vào AI, đảm bảo hoạt động ổn định

2. **Phiên bản AI (Chat Mode)**:
   - Trải nghiệm trò chuyện tự nhiên và đồng cảm
   - Kết hợp chat và poll để tối ưu trải nghiệm
   - Sử dụng LLM để tạo phản hồi phong phú

Cả hai phiên bản đều sử dụng cùng một cơ sở kiến thức và bộ câu hỏi đánh giá tiêu chuẩn, đảm bảo kết quả nhất quán dù người dùng chọn phương thức tương tác nào. Thiết kế này cho phép ứng dụng vừa tận dụng sức mạnh của AI, vừa đảm bảo hoạt động ổn định với phiên bản không phụ thuộc AI.