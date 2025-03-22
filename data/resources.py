"""
Tài nguyên và đề xuất cho người dùng dựa trên kết quả đánh giá
Chuyển đổi từ resources.js sang Python
"""

# Danh sách tài nguyên
resources = {
    "general": [
        {
            "title": "Ứng dụng thiền và chánh niệm",
            "description": "Giúp thư giãn và giảm căng thẳng thông qua các bài thiền hướng dẫn",
            "examples": "Headspace, Calm, Insight Timer",
            "link": "https://www.headspace.com/"
        },
        {
            "title": "Luyện tập thể dục đều đặn",
            "description": "Hoạt động thể chất giúp cải thiện tâm trạng và giảm căng thẳng",
            "examples": "Đi bộ 30 phút mỗi ngày, yoga, bơi lội"
        },
        {
            "title": "Duy trì kết nối xã hội",
            "description": "Giao tiếp đều đặn với bạn bè và người thân giúp cải thiện sức khỏe tâm thần",
            "examples": "Gọi điện cho bạn bè, tham gia các nhóm sở thích, tình nguyện viên"
        },
        {
            "title": "Duy trì lối sống lành mạnh",
            "description": "Đảm bảo giấc ngủ đầy đủ, chế độ ăn uống cân bằng, và giới hạn rượu/caffeine",
            "examples": "Ngủ 7-8 tiếng mỗi đêm, ăn nhiều rau quả, uống nhiều nước"
        }
    ],
    
    "depression": {
        "mild": [
            {
                "title": "Sách về chữa trị trầm cảm",
                "description": "Sách tự giúp đỡ dựa trên phương pháp nhận thức hành vi",
                "examples": "\"Feeling Good\" của David Burns, \"The Upward Spiral\" của Alex Korb"
            },
            {
                "title": "Nhật ký biết ơn",
                "description": "Ghi lại 3 điều bạn biết ơn mỗi ngày để tăng cường tập trung vào mặt tích cực",
                "examples": "Sử dụng sổ tay hoặc ứng dụng như Gratitude Journal"
            }
        ],
        "moderate": [
            {
                "title": "Tư vấn tâm lý trực tuyến",
                "description": "Dịch vụ tư vấn từ xa với các chuyên gia tâm lý được cấp phép",
                "examples": "Cơ sở y tế địa phương, ứng dụng tư vấn trực tuyến"
            },
            {
                "title": "Các nhóm hỗ trợ trầm cảm",
                "description": "Tham gia cộng đồng những người có trải nghiệm tương tự",
                "examples": "Nhóm hỗ trợ tại địa phương, diễn đàn trực tuyến"
            }
        ],
        "severe": [
            {
                "title": "Tìm kiếm hỗ trợ chuyên nghiệp ngay",
                "description": "Khi trầm cảm ở mức độ nghiêm trọng, việc tư vấn chuyên nghiệp là cần thiết",
                "examples": "Tâm lý học, bác sĩ tâm thần, trung tâm sức khỏe tâm thần"
            },
            {
                "title": "Liệu pháp nhận thức hành vi (CBT)",
                "description": "Phương pháp điều trị hiệu quả cho trầm cảm",
                "examples": "Tìm kiếm chuyên gia CBT tại địa phương"
            }
        ]
    },
    
    "anxiety": {
        "mild": [
            {
                "title": "Kỹ thuật thở sâu",
                "description": "Phương pháp đơn giản để giảm lo âu và căng thẳng",
                "examples": "Thở bụng sâu 4-7-8 (hít vào 4 giây, giữ 7 giây, thở ra 8 giây)"
            },
            {
                "title": "Thiền chánh niệm",
                "description": "Tập trung vào khoảnh khắc hiện tại để giảm lo âu về tương lai",
                "examples": "Ứng dụng như Headspace, Calm có các bài thiền chuyên về lo âu"
            }
        ],
        "moderate": [
            {
                "title": "Workbook lo âu",
                "description": "Sách bài tập giúp hiểu và quản lý triệu chứng lo âu",
                "examples": "\"The Anxiety and Worry Workbook\" của Clark và Beck"
            },
            {
                "title": "Giảm caffeine và rượu",
                "description": "Các chất kích thích có thể làm tăng triệu chứng lo âu",
                "examples": "Thay thế cà phê bằng trà thảo mộc, giảm rượu"
            }
        ],
        "severe": [
            {
                "title": "Tham vấn chuyên gia sức khỏe tâm thần",
                "description": "Lo âu nghiêm trọng cần được điều trị chuyên nghiệp",
                "examples": "Tâm lý học, bác sĩ tâm thần, trung tâm sức khỏe tâm thần"
            },
            {
                "title": "Liệu pháp tiếp xúc",
                "description": "Phương pháp điều trị hiệu quả cho các rối loạn lo âu",
                "examples": "Tìm kiếm chuyên gia về liệu pháp tiếp xúc"
            }
        ]
    },
    
    "stress": {
        "mild": [
            {
                "title": "Quản lý thời gian",
                "description": "Lập kế hoạch và ưu tiên nhiệm vụ để giảm áp lực",
                "examples": "Sử dụng lịch, danh sách việc cần làm, kỹ thuật Pomodoro"
            },
            {
                "title": "Hoạt động thư giãn",
                "description": "Dành thời gian cho các hoạt động bạn yêu thích",
                "examples": "Đọc sách, nghe nhạc, tắm nước ấm, đi dạo trong thiên nhiên"
            }
        ],
        "moderate": [
            {
                "title": "Kỹ thuật thư giãn cơ tiến triển",
                "description": "Căng và thư giãn từng nhóm cơ để giảm căng thẳng thể chất",
                "examples": "Tìm kiếm hướng dẫn trực tuyến về kỹ thuật này"
            },
            {
                "title": "Thiết lập ranh giới",
                "description": "Học cách nói 'không' và đặt ra giới hạn lành mạnh",
                "examples": "Giới hạn thời gian làm việc, tắt thông báo sau giờ làm việc"
            }
        ],
        "severe": [
            {
                "title": "Đánh giá lại nguồn căng thẳng",
                "description": "Xác định và giải quyết các nguồn căng thẳng chính trong cuộc sống",
                "examples": "Cân nhắc thay đổi công việc, tham vấn tài chính, hoặc tư vấn quan hệ"
            },
            {
                "title": "Tìm kiếm hỗ trợ chuyên nghiệp",
                "description": "Căng thẳng kéo dài có thể cần sự hỗ trợ của chuyên gia",
                "examples": "Tâm lý học, huấn luyện viên cuộc sống (life coach)"
            }
        ]
    },
    
    "emergency": [
        {
            "title": "Đường dây nóng phòng chống tự tử",
            "description": "Hỗ trợ khủng hoảng 24/7",
            "phone": "1800-8440 (miễn phí)"
        },
        {
            "title": "Cấp cứu",
            "description": "Trong trường hợp khẩn cấp",
            "phone": "115"
        },
        {
            "title": "Trung tâm sức khỏe tâm thần Bệnh viện Bạch Mai",
            "phone": "024.3869.3731"
        },
        {
            "title": "Bệnh viện Tâm thần Trung ương 1",
            "phone": "024.3825.3028"
        }
    ]
}

def get_resources_for_severity(category, severity):
    """
    Lấy danh sách tài nguyên phù hợp cho danh mục và mức độ nghiêm trọng
    """
    result = []
    
    # Luôn thêm tài nguyên chung
    result = result + resources["general"]
    
    # Thêm tài nguyên theo danh mục và mức độ
    if category in resources and severity in resources[category]:
        result = result + resources[category][severity]
    
    # Nếu mức độ nghiêm trọng, thêm thông tin khẩn cấp
    if severity in ['severe', 'moderatelySevere', 'extremelySevere']:
        result = result + resources["emergency"]
    
    return result

def format_resources_message(resource_list):
    """
    Định dạng danh sách tài nguyên thành tin nhắn có thể hiển thị
    """
    message = "Đây là một số tài nguyên có thể hữu ích cho bạn:\n\n"
    
    for index, resource in enumerate(resource_list):
        message += f"{index + 1}. **{resource['title']}**\n"
        if 'description' in resource:
            message += f"   {resource['description']}\n"
        if 'examples' in resource and resource['examples']:
            message += f"   Ví dụ: {resource['examples']}\n"
        if 'phone' in resource and resource['phone']:
            message += f"   Liên hệ: {resource['phone']}\n"
        if 'link' in resource and resource['link']:
            message += f"   Tham khảo: {resource['link']}\n"
        message += "\n"
    
    return message