# Chatbot Sàng Lọc Sức Khỏe Tâm Thần

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red.svg)
![License](https://img.shields.io/badge/license-ISC-orange.svg)

Ứng dụng web chatbot sàng lọc sức khỏe tâm thần sử dụng Flask và tích hợp với mô hình AI Llama 3.3 70B thông qua Together AI. Chatbot được thiết kế để cung cấp đánh giá sàng lọc ban đầu về các vấn đề sức khỏe tâm thần phổ biến như trầm cảm, lo âu và căng thẳng với giao diện trò chuyện tự nhiên bằng tiếng Việt.

## Tính năng chính

- 🔍 **Sàng lọc sức khỏe tâm thần** sử dụng các bộ công cụ đánh giá chuẩn (PHQ-9, GAD-7, DASS-21)
- 🤖 **Tích hợp AI** với Llama 3.3 70B cho trải nghiệm trò chuyện tự nhiên, đồng cảm
- 🚨 **Phát hiện nguy cơ** tự động đối với các dấu hiệu tự tử và cung cấp tài nguyên khẩn cấp
- 📊 **Đánh giá chi tiết** với điểm số và mức độ nghiêm trọng
- 📚 **Cung cấp tài nguyên** phù hợp với kết quả sàng lọc
- 🚀 **Hỗ trợ hai chế độ**: AI (linh hoạt) và Logic (tiêu chuẩn)
- 📱 **Giao diện responsive** tương thích với nhiều kích thước màn hình

## Kiến trúc hệ thống

Ứng dụng được xây dựng trên kiến trúc hybrid kết hợp máy trạng thái (state machine) truyền thống và mô hình ngôn ngữ lớn (LLM):

- **Core Router**: Sử dụng máy trạng thái để điều khiển luồng trò chuyện, đảm bảo tính nhất quán và tin cậy
- **LLM Enhancement**: Tích hợp Llama 3.3 70B để làm phong phú phản hồi, tạo cuộc trò chuyện tự nhiên và đồng cảm
- **Client-side Storage**: Lưu trữ lịch sử trò chuyện và trạng thái trong localStorage

### Sơ đồ trạng thái

```
GREETING → COLLECTING_ISSUE → INITIAL_SCREENING → DETAILED_ASSESSMENT → SUMMARY → RESOURCES → CLOSING
                                      ↓                    ↓
                                      ↓             SUICIDE_ASSESSMENT
                                      ↓
                               ADDITIONAL_ASSESSMENT
```

## Cài đặt

### Yêu cầu

- Python 3.8+
- pip

### Bước 1: Clone repository

```bash
git clone https://github.com/yourusername/mental-health-chatbot-flask.git
cd mental-health-chatbot-flask
```

### Bước 2: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình

Tạo file `.env` trong thư mục gốc:

```
TOGETHER_API_KEY=your_api_key_here
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here
```

Bạn có thể nhận API key từ [Together AI](https://together.ai).

### Bước 4: Chạy ứng dụng

```bash
python app.py
```

Ứng dụng sẽ chạy tại `http://localhost:5000`

## Cấu trúc dự án

```
mental-health-chatbot-flask/
├── app.py                  # File Flask chính
├── config.py               # Cấu hình
├── static/                 # Tài nguyên tĩnh (CSS, JS, images)
│   ├── css/
│   │   └── style.css       # CSS chuyển từ globals.css + tailwind
│   ├── js/
│   │   └── chat.js         # JavaScript xử lý tương tác chat
│   └── images/
│       └── favicon.ico
├── templates/              # Templates HTML
│   ├── base.html           # Template cơ sở
│   ├── index.html          # Trang chính
│   ├── about.html          # Trang giới thiệu
│   ├── resources.html      # Trang tài nguyên
│   └── privacy.html        # Trang quyền riêng tư
├── utils/                  # Các module tiện ích
│   ├── together_ai.py      # Xử lý Together AI API
│   ├── chat_logic.py       # Logic điều khiển luồng chat
│   ├── scoring.py          # Tính điểm và xác định mức độ
│   └── contextual_prompt.py # Tạo prompt cho AI
├── data/                   # Dữ liệu cho ứng dụng
│   ├── questionnaires.py   # Dữ liệu bộ câu hỏi
│   ├── resources.py        # Tài nguyên hỗ trợ
│   └── diagnostic.py       # Tiêu chí chẩn đoán
├── requirements.txt        # Dependencies
└── README.md
```

## Chi tiết kỹ thuật

### Quy trình xử lý tin nhắn

1. Người dùng gửi tin nhắn
2. Server xác định trạng thái hiện tại và chuyển tin nhắn tới handler thích hợp
3. Handler xử lý tin nhắn, cập nhật trạng thái chat và xác định trạng thái tiếp theo
4. Nếu AI mode được bật, phản hồi được tăng cường bằng LLM
5. Phản hồi được gửi về client

### Các bộ câu hỏi sàng lọc

Hệ thống sử dụng các bộ câu hỏi đánh giá được công nhận rộng rãi:

- **Initial Screening**: Bộ câu hỏi sàng lọc ban đầu, xác định vấn đề chính
- **PHQ-9**: Đánh giá trầm cảm (Patient Health Questionnaire)
- **GAD-7**: Đánh giá lo âu (Generalized Anxiety Disorder Assessment)
- **DASS-21**: Đánh giá căng thẳng (Depression, Anxiety and Stress Scale)
- **Suicide Risk Assessment**: Đánh giá nguy cơ tự tử trong trường hợp phát hiện dấu hiệu

### Contextual Prompt Engineering

Hệ thống sử dụng kỹ thuật tạo prompt động cho LLM dựa trên:
- Trạng thái hiện tại của cuộc trò chuyện
- Lịch sử trò chuyện gần đây
- Thông tin về câu hỏi và đánh giá hiện tại
- Kết quả và điểm số đã tích lũy

## Lưu ý quan trọng

⚠️ **Miễn trừ trách nhiệm**: Ứng dụng này chỉ cung cấp công cụ sàng lọc sơ bộ và không phải là công cụ chẩn đoán chính thức. Kết quả chỉ mang tính chất tham khảo và không thay thế cho tư vấn y tế chuyên nghiệp. Luôn khuyến khích người dùng tham khảo ý kiến của chuyên gia sức khỏe tâm thần có trình độ.

## Hướng phát triển tương lai

- [ ] Tích hợp cơ sở dữ liệu để lưu trữ kết quả đánh giá
- [ ] Thêm nhiều bộ đánh giá chuyên sâu (ADHD, Lưỡng cực, PTSD...)
- [ ] Phát triển tính năng theo dõi tiến triển qua thời gian
- [ ] Tạo dashboard và báo cáo chi tiết
- [ ] Hỗ trợ đa ngôn ngữ và địa phương hóa tài nguyên

## Dữ liệu và quyền riêng tư

Dữ liệu của người dùng chỉ được lưu trữ tạm thời trong phiên trò chuyện hiện tại và localStorage của trình duyệt. Ứng dụng không thu thập hoặc lưu trữ dữ liệu cá nhân dài hạn.

## Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng xem [hướng dẫn đóng góp](CONTRIBUTING.md) để biết thêm thông tin.

## Giấy phép

Dự án này được cấp phép theo giấy phép ISC - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## Liên hệ

Nếu bạn có bất kỳ câu hỏi hoặc góp ý nào, vui lòng liên hệ qua email: phuckhangtdn@gmail.com
