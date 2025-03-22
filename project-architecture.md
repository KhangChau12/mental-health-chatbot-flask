# Kiến trúc và Kỹ thuật của Chatbot Sức khỏe Tâm thần

## Tổng quan dự án

Chatbot Sức khỏe Tâm thần là một ứng dụng web chatbot sàng lọc sức khỏe tâm thần, được xây dựng trên Flask và tích hợp với mô hình AI Llama 3.3 70B thông qua Together AI. Ứng dụng được thiết kế để cung cấp công cụ sàng lọc ban đầu về các vấn đề sức khỏe tâm thần phổ biến như trầm cảm, lo âu và căng thẳng, với trọng tâm là hỗ trợ tiếng Việt.

## Kiến trúc hệ thống

### 1. Kiến trúc tổng thể

Dự án được xây dựng theo mô hình MVC (Model-View-Controller) với các thành phần chính:

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript với Jinja2 Templates
- **Database**: Hiện tại sử dụng lưu trữ tạm thời (session storage và localStorage)
- **AI Integration**: Together AI API (Llama 3.3 70B)

### 2. Cấu trúc thư mục

```
mental-health-chatbot-flask/
├── app.py                  # File Flask chính
├── config.py               # Cấu hình
├── static/                 # Tài nguyên tĩnh (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/              # Templates HTML
├── utils/                  # Các module tiện ích
│   ├── together_ai.py      # Xử lý Together AI API
│   ├── chat_logic.py       # Logic điều khiển luồng chat
│   ├── scoring.py          # Tính điểm và xác định mức độ
│   └── contextual_prompt.py # Tạo prompt cho AI
├── data/                   # Dữ liệu cho ứng dụng
│   ├── questionnaires.py   # Dữ liệu bộ câu hỏi
│   ├── resources.py        # Tài nguyên hỗ trợ
│   └── diagnostic.py       # Tiêu chí chẩn đoán
```

## Kỹ thuật điều hướng trò chuyện (Conversation Routing)

### 1. Hybrid State Machine + LLM Approach

Hệ thống sử dụng một cách tiếp cận hybrid kết hợp giữa máy trạng thái (state machine) và mô hình ngôn ngữ lớn:

- **Máy trạng thái**: Core của hệ thống sử dụng máy trạng thái được định nghĩa sẵn để kiểm soát luồng trò chuyện và đảm bảo tính nhất quán.
- **LLM Enhancement**: Tích hợp LLM (Llama 3.3 70B) để làm phong phú phản hồi, làm cho cuộc trò chuyện tự nhiên và đồng cảm hơn.

Mô hình này đảm bảo độ tin cậy của state machine trong khi vẫn tận dụng khả năng ngôn ngữ tự nhiên của LLM.

### 2. Các trạng thái trò chuyện

Hệ thống sử dụng 10 trạng thái chính để điều hướng cuộc trò chuyện:

```python
CHAT_STATES = {
    'GREETING': 'greeting',               # Chào hỏi ban đầu
    'COLLECTING_ISSUE': 'collecting_issue', # Thu thập vấn đề người dùng
    'INITIAL_SCREENING': 'initial_screening', # Sàng lọc ban đầu
    'DETAILED_ASSESSMENT': 'detailed_assessment', # Đánh giá chi tiết
    'ADDITIONAL_ASSESSMENT': 'additional_assessment', # Đánh giá bổ sung
    'SUICIDE_ASSESSMENT': 'suicide_assessment', # Đánh giá nguy cơ tự tử
    'SUMMARY': 'summary',                 # Tóm tắt kết quả
    'RESOURCES': 'resources',             # Cung cấp tài nguyên
    'DISORDER_INFO': 'disorder_info',     # Thông tin về rối loạn
    'CLOSING': 'closing'                  # Kết thúc cuộc trò chuyện
}
```

Mỗi trạng thái có một handler function riêng, xử lý việc xác định phản hồi và trạng thái tiếp theo.

### 3. Quy trình xử lý tin nhắn

```
User Message → process_message() → handler function → Determine next state → AI enhancement (optional) → Response
```

Cụ thể:
1. Người dùng gửi tin nhắn
2. `process_message()` xác định trạng thái hiện tại và chuyển tin nhắn tới handler thích hợp
3. Handler xử lý tin nhắn, cập nhật trạng thái chat và xác định trạng thái tiếp theo
4. Nếu AI mode được bật, phản hồi được tăng cường bằng LLM
5. Phản hồi được gửi về client

### 4. Bộ câu hỏi và đánh giá tự động

Hệ thống sử dụng các bộ câu hỏi đánh giá tiêu chuẩn:

- **Initial Screening**: Bộ câu hỏi sàng lọc ban đầu, xác định vấn đề chính
- **PHQ-9**: Đánh giá trầm cảm (Patient Health Questionnaire)
- **GAD-7**: Đánh giá lo âu (Generalized Anxiety Disorder Assessment)
- **DASS-21**: Đánh giá căng thẳng (Depression, Anxiety and Stress Scale)
- **Suicide Risk Assessment**: Đánh giá nguy cơ tự tử trong trường hợp phát hiện dấu hiệu

Điều hướng giữa các bộ câu hỏi được thực hiện tự động dựa trên kết quả:

```python
"nextAssessment": {
    "depression": "phq9",
    "anxiety": "gad7",
    "stress": "dass21_stress"
}
```

## Contextual Prompt Engineering

### 1. Dynamic Prompt Construction

File `contextual_prompt.py` xây dựng prompt động cho LLM dựa trên:
- Trạng thái hiện tại của cuộc trò chuyện
- Lịch sử trò chuyện gần đây
- Thông tin về câu hỏi và đánh giá hiện tại
- Kết quả và điểm số đã tích lũy

Prompt được cấu trúc với:
- Thông tin vai trò (Trợ lý sức khỏe tâm thần)
- Nhiệm vụ và giới hạn (không đưa ra chẩn đoán y tế)
- Thông tin về trạng thái hiện tại
- Lịch sử trò chuyện
- Hướng dẫn đánh giá và phản hồi dựa trên trạng thái

### 2. Tích hợp with Together AI

File `together_ai.py` xử lý việc tương tác với API Together AI:
- Khởi tạo client với API key
- Tạo chat completion với contextual prompt
- Xử lý response và trích xuất text
- Fallback gracefully khi API call thất bại

## Kỹ thuật quản lý state và storage

### 1. Server-side State Management

- Sử dụng Dict Python để lưu trữ trạng thái cuộc trò chuyện, bao gồm:
  - Trạng thái hiện tại (`state`)
  - Đánh giá hiện tại (`currentAssessment`)
  - Chỉ số câu hỏi hiện tại (`currentQuestionIndex`)
  - Phản hồi của người dùng (`userResponses`)
  - Điểm số và mức độ nghiêm trọng (`scores`, `severityLevels`)
  - Cờ cảnh báo (`flags`)

### 2. Client-side Storage

- Sử dụng localStorage để lưu trữ lịch sử trò chuyện và trạng thái
- Hỗ trợ tải lại trang mà không mất context
- Đồng bộ trạng thái giữa client và server

## Xử lý nguy cơ (Risk Handling)

Hệ thống có cơ chế phát hiện và can thiệp tự động khi phát hiện nguy cơ tự tử:

1. **Phát hiện nguy cơ**:
   - Xác định câu hỏi có cờ `suicide_risk`
   - Kiểm tra phản hồi có vượt ngưỡng không

2. **Can thiệp tự động**:
   - Chuyển sang trạng thái `SUICIDE_ASSESSMENT`
   - Cung cấp thông báo khẩn cấp và tài nguyên
   - Hiển thị đường dây nóng và hướng dẫn hỗ trợ

## Tạo Scoring và Diagnostics

### 1. Hệ thống tính điểm

File `scoring.py` xử lý:
- Tính tổng điểm cho từng danh mục (trầm cảm, lo âu, căng thẳng)
- Xác định mức độ nghiêm trọng dựa trên ngưỡng tiêu chuẩn
- Kiểm tra các cờ rủi ro

### 2. Tiêu chí chẩn đoán

File `diagnostic.py` cung cấp:
- Thông tin chẩn đoán dựa trên DSM-5 và ICD-11
- Mô tả triệu chứng, tiêu chí, mức độ nghiêm trọng
- Phương pháp điều trị tiềm năng
- Thông tin để người dùng hiểu rõ hơn về tình trạng của họ

## UI/UX và Tương tác người dùng

### 1. Responsive Design

- Giao diện thích ứng với nhiều kích thước màn hình
- Xử lý tin nhắn và hiệu ứng mượt mà

### 2. Contextual Mode Switching

- Toggle giữa AI Mode và Logic Mode
- Hiển thị trạng thái đánh giá hiện tại
- Markdown rendering cho phản hồi được định dạng

### 3. Progressive Disclosure

- Cung cấp thông tin theo cách tiếp cận dần dần
- Hiển thị tài nguyên phù hợp với mức độ nghiêm trọng

## Tổng kết

Chatbot Sức khỏe Tâm thần là một ví dụ về ứng dụng kết hợp giữa rule-based system truyền thống và khả năng của LLM. Bằng cách sử dụng máy trạng thái cốt lõi kết hợp với khả năng ngôn ngữ tự nhiên của Llama 3.3 70B, hệ thống cung cấp trải nghiệm trò chuyện tự nhiên mà vẫn đảm bảo tính chính xác và an toàn trong lĩnh vực nhạy cảm như sức khỏe tâm thần.

Cách tiếp cận hybrid này cho phép:
1. Độ tin cậy và kiểm soát của flow cuộc trò chuyện
2. Khả năng mở rộng dễ dàng với bộ câu hỏi mới
3. Phản hồi tự nhiên và đồng cảm từ mô hình ngôn ngữ

Ứng dụng có thể được cải thiện trong tương lai với các tính năng như lưu trữ dữ liệu dài hạn, theo dõi tiến triển, và tích hợp nhiều bộ đánh giá chuyên sâu hơn.
