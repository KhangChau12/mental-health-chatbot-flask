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

def format_resources_html(resources_list):
    """
    Định dạng danh sách tài nguyên thành HTML với chức năng tương tác đầy đủ
    
    Args:
        resources_list (list): Danh sách tài nguyên
        
    Returns:
        str: HTML tài nguyên
    """
    # Tạo cấu trúc danh mục tài nguyên
    categories = [
        {
            'id': 'mindfulness',
            'title': 'Ứng dụng thiền và chánh niệm',
            'description': 'Giúp thư giãn và giảm căng thẳng thông qua các bài thiền hướng dẫn',
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>',
            'color': 'purple',
            'items': [
                {'name': 'Headspace', 'link': 'https://www.headspace.com/'},
                {'name': 'Calm', 'link': 'https://www.calm.com/'},
                {'name': 'Insight Timer', 'link': 'https://insighttimer.com/'}
            ]
        },
        {
            'id': 'exercise',
            'title': 'Luyện tập thể dục đều đặn',
            'description': 'Hoạt động thể chất giúp cải thiện tâm trạng và giảm căng thẳng',
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>',
            'color': 'purple',
            'items': [
                {'name': 'Đi bộ 30 phút mỗi ngày'},
                {'name': 'Yoga nhẹ nhàng'},
                {'name': 'Bơi lội'}
            ]
        },
        {
            'id': 'social',
            'title': 'Duy trì kết nối xã hội',
            'description': 'Giao tiếp đều đặn với bạn bè và người thân giúp cải thiện sức khỏe tâm thần',
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
            'color': 'purple',
            'items': [
                {'name': 'Gọi điện cho bạn bè thường xuyên'},
                {'name': 'Tham gia các nhóm sở thích'},
                {'name': 'Tham gia hoạt động tình nguyện trong cộng đồng'}
            ]
        },
        {
            'id': 'lifestyle',
            'title': 'Duy trì lối sống lành mạnh',
            'description': 'Đảm bảo giấc ngủ đầy đủ, chế độ ăn uống cân bằng, và giới hạn rượu/caffeine',
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>',
            'color': 'purple',
            'items': [
                {'name': 'Ngủ 7-8 tiếng mỗi đêm'},
                {'name': 'Ăn nhiều rau quả, ít đồ ăn chế biến sẵn'},
                {'name': 'Uống nhiều nước, hạn chế đồ uống có cồn và caffeine'}
            ]
        },
        {
            'id': 'emergency',
            'title': 'Số điện thoại khẩn cấp',
            'description': 'Liên hệ ngay khi cảm thấy khủng hoảng hoặc có suy nghĩ tự hại',
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ff4757" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15.6 11.6L22 7v10l-6.4-4.5v-1zM4 5h9a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7c0-1.1.9-2 2-2z" /></svg>',
            'color': 'red',
            'items': [
                {'name': 'Đường dây nóng phòng chống tự tử: 1800-8440', 'phone': '1800-8440'},
                {'name': 'Cấp cứu: 115', 'phone': '115'},
                {'name': 'Trung tâm sức khỏe tâm thần Bệnh viện Bạch Mai: 024.3869.3731', 'phone': '024.3869.3731'}
            ]
        }
    ]
    
    # Thêm tài nguyên từ tham số đầu vào
    if resources_list:
        # Tạo danh mục tài nguyên tùy chỉnh từ resources_list
        custom_resources = []
        
        for resource in resources_list:
            item = {'name': resource.get('title', 'Tài nguyên')}
            
            if 'link' in resource:
                item['link'] = resource['link']
                
            if resource.get('examples'):
                item['description'] = f"Ví dụ: {resource['examples']}"
                
            if resource.get('phone'):
                item['phone'] = resource['phone']
                
            # Phân loại tài nguyên vào danh mục phù hợp
            category_id = None
            if "thiền" in resource.get('title', '').lower() or "thiền" in resource.get('description', '').lower():
                category_id = "mindfulness"
            elif "thể dục" in resource.get('title', '').lower() or "tập" in resource.get('title', '').lower():
                category_id = "exercise"
            elif "xã hội" in resource.get('title', '').lower() or "kết nối" in resource.get('title', '').lower():
                category_id = "social"
            elif "giấc ngủ" in resource.get('title', '').lower() or "ăn uống" in resource.get('title', '').lower():
                category_id = "lifestyle"
            elif "khẩn cấp" in resource.get('title', '').lower() or "tự tử" in resource.get('title', '').lower() or resource.get('phone'):
                category_id = "emergency"
            
            if category_id:
                # Tìm danh mục và thêm vào
                for cat in categories:
                    if cat['id'] == category_id:
                        cat['items'].append(item)
                        break
            else:
                # Nếu không tìm thấy danh mục phù hợp, thêm vào custom_resources
                custom_resources.append(item)
    
    # Bắt đầu tạo HTML
    html = """
    <div class="resources-container p-6 bg-gray-900 rounded-lg shadow-lg">
        <div class="mb-6">
            <h2 class="text-2xl font-bold text-white flex items-center mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-3 text-purple-500">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
                Tài nguyên hỗ trợ
            </h2>
            <p class="text-gray-300">Dưới đây là một số tài nguyên có thể hữu ích cho việc cải thiện sức khỏe tâm thần:</p>
        </div>
    """
    
    # Thêm phần thông tin về rối loạn
    html += """
        <div class="mb-6 bg-gray-800 rounded-lg p-4 border-l-4 border-purple-500">
            <h3 class="text-lg font-semibold text-white mb-2">Rối loạn liên quan đến căng thẳng</h3>
            <p class="text-gray-300 mb-3">Căng thẳng quá mức có thể dẫn đến nhiều vấn đề sức khỏe tâm thần và thể chất.</p>
            
            <div class="bg-gray-700 p-3 rounded-md">
                <h4 class="font-medium text-purple-400 mb-1">Triệu chứng chính:</h4>
                <ul class="text-gray-300 grid grid-cols-1 md:grid-cols-2 gap-1">
                    <li class="flex items-center">
                        <span class="mr-2 text-purple-500">•</span>Cảm thấy quá tải hoặc áp lực
                    </li>
                    <li class="flex items-center">
                        <span class="mr-2 text-purple-500">•</span>Khó thư giãn hoặc nghỉ ngơi
                    </li>
                    <li class="flex items-center">
                        <span class="mr-2 text-purple-500">•</span>Dễ cáu kỉnh hoặc tức giận
                    </li>
                    <li class="flex items-center">
                        <span class="mr-2 text-purple-500">•</span>Mệt mỏi, khó tập trung
                    </li>
                    <li class="flex items-center">
                        <span class="mr-2 text-purple-500">•</span>Căng cơ hoặc đau
                    </li>
                    <li class="flex items-center">
                        <span class="mr-2 text-purple-500">•</span>Thay đổi về giấc ngủ hoặc ăn uống
                    </li>
                </ul>
            </div>
        </div>
    """
    
    # Tạo các danh mục tài nguyên
    html += '<div class="resources-list space-y-4">'
    
    # Duyệt qua từng danh mục và tạo HTML
    for category in categories:
        if not category['items']:  # Bỏ qua danh mục không có mục nào
            continue
            
        html += f"""
            <div class="resource-category transition-all duration-300 border border-gray-700 rounded-lg overflow-hidden bg-gray-800 hover:bg-gray-700">
                <div class="category-header p-4 flex items-center justify-between cursor-pointer" onclick="toggleResourceCategory('{category['id']}')">
                    <div class="flex items-center">
                        <div class="category-icon p-2 rounded-full mr-3 bg-{category['color']}-900 text-{category['color']}-400">
                            {category['icon']}
                        </div>
                        <div>
                            <h3 class="font-semibold text-white">{category['title']}</h3>
                            <p class="text-sm text-gray-400">{category['description']}</p>
                        </div>
                    </div>
                    <svg 
                        xmlns="http://www.w3.org/2000/svg" 
                        width="20" height="20" 
                        viewBox="0 0 24 24" 
                        fill="none" 
                        stroke="currentColor" 
                        stroke-width="2" 
                        stroke-linecap="round" 
                        stroke-linejoin="round" 
                        class="category-arrow text-gray-400 transition-transform"
                        id="{category['id']}-arrow"
                    >
                        <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                </div>
                
                <div class="category-content p-4 pt-0 border-t border-gray-700 hidden" id="{category['id']}-content">
                    <ul class="resource-items space-y-2 mt-2">
        """
        
        # Thêm các mục trong danh mục
        for item in category['items']:
            if 'phone' in item:
                html += f"""
                        <li class="resource-item flex items-center">
                            <a href="tel:{item.get('phone')}" class="text-gray-300 hover:text-{category['color']}-400 flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
                                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                                </svg>
                                {item['name']}
                            </a>
                        </li>
                """
            elif 'link' in item:
                html += f"""
                        <li class="resource-item flex items-center">
                            <a href="{item['link']}" target="_blank" rel="noopener noreferrer" class="text-gray-300 hover:text-{category['color']}-400 flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
                                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                                    <polyline points="15 3 21 3 21 9"></polyline>
                                    <line x1="10" y1="14" x2="21" y2="3"></line>
                                </svg>
                                {item['name']}
                            </a>
                        </li>
                """
            else:
                html += f"""
                        <li class="resource-item flex items-center">
                            <span class="text-gray-300 flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
                                    <polyline points="9 11 12 14 22 4"></polyline>
                                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                                </svg>
                                {item['name']}
                                {f"<span class='ml-2 text-sm text-gray-500'>{item.get('description', '')}</span>" if 'description' in item else ""}
                            </span>
                        </li>
                """
        
        # Đóng danh mục
        html += """
                    </ul>
                </div>
            </div>
        """
    
    # Đóng danh sách danh mục
    html += '</div>'
    
    # Thêm lưu ý và disclaimer
    html += """
        <div class="mt-6 p-3 bg-gray-800 border-l-4 border-yellow-500 rounded text-sm">
            <p class="text-gray-300">
                <strong class="text-yellow-400">Lưu ý:</strong> Thông tin này chỉ mang tính chất tham khảo. 
                Chỉ chuyên gia sức khỏe tâm thần mới có thể đưa ra chẩn đoán và kế hoạch điều trị chính xác.
            </p>
        </div>
    """
    
    # Thêm các nút điều hướng
    html += """
        <div class="mt-6 flex flex-wrap gap-3">
            <button 
                class="action-button px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md transition-colors shadow-md flex items-center"
                onclick="restartSurvey()"
            >
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <polyline points="1 20 1 14 7 14"></polyline>
                    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                </svg>
                Làm Lại Khảo Sát
            </button>
            <button 
                class="action-button px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-md transition-colors shadow-md flex items-center"
                onclick="completeSurvey()"
            >
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
                    <path d="M18 6L6 18"></path>
                    <path d="M6 6l12 12"></path>
                </svg>
                Hoàn Thành
            </button>
        </div>
    """
    
    # Thêm script để xử lý việc mở/đóng danh mục và các chức năng tương tác
    html += """
        <script>
            // Hàm mở/đóng danh mục tài nguyên
            function toggleResourceCategory(categoryId) {
                var content = document.getElementById(categoryId + '-content');
                var arrow = document.getElementById(categoryId + '-arrow');
                
                if (content.classList.contains('hidden')) {
                    // Đóng tất cả các danh mục khác
                    document.querySelectorAll('.category-content').forEach(function(el) {
                        el.classList.add('hidden');
                    });
                    document.querySelectorAll('.category-arrow').forEach(function(el) {
                        el.classList.remove('transform', 'rotate-180');
                    });
                    
                    // Mở danh mục hiện tại
                    content.classList.remove('hidden');
                    arrow.classList.add('transform', 'rotate-180');
                } else {
                    // Đóng danh mục hiện tại
                    content.classList.add('hidden');
                    arrow.classList.remove('transform', 'rotate-180');
                }
                
                // Cuộn đến vị trí của danh mục
                setTimeout(function() {
                    var headerElement = document.querySelector('.category-header');
                    if (headerElement) {
                        headerElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                }, 100);
            }
            
            // Hàm khởi động lại khảo sát
            function restartSurvey() {
                if (confirm("Bạn có chắc chắn muốn bắt đầu lại khảo sát? Tất cả dữ liệu sẽ bị xóa.")) {
                    fetch('/api/poll_flow', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ action: 'restart' })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.reload();
                        } else {
                            alert("Có lỗi xảy ra: " + (data.error || "Không thể khởi động lại khảo sát"));
                        }
                    })
                    .catch(error => {
                        console.error("Error restarting survey:", error);
                        alert("Đã xảy ra lỗi khi khởi động lại khảo sát.");
                    });
                }
            }
            
            // Hàm hoàn thành khảo sát
            function completeSurvey() {
                var welcomeContainer = document.getElementById('welcome-container');
                var resourcesContainer = document.getElementById('resources-container');
                
                if (welcomeContainer && resourcesContainer) {
                    resourcesContainer.classList.add('hidden');
                    welcomeContainer.classList.remove('hidden');
                    
                    // Hiển thị thông báo hoàn thành
                    alert("Cảm ơn bạn đã hoàn thành khảo sát. Chúc bạn một ngày tốt lành!");
                    
                    // Cuộn lên đầu trang
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            }
            
            // Mở danh mục đầu tiên mặc định
            document.addEventListener('DOMContentLoaded', function() {
                var firstCategory = document.querySelector('.resource-category');
                if (firstCategory) {
                    var categoryId = firstCategory.querySelector('.category-header').getAttribute('onclick');
                    if (categoryId) {
                        categoryId = categoryId.replace("toggleResourceCategory('", "").replace("')", "");
                        toggleResourceCategory(categoryId);
                    }
                }
            });
        </script>
    """
    
    # Thêm CSS inline để đảm bảo các style được áp dụng
    html += """
        <style>
            .resources-container {
                animation: fadeIn 0.4s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .resource-category {
                transition: all 0.3s ease;
            }
            
            .resource-category:hover {
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
            
            .category-content {
                max-height: 0;
                opacity: 0;
                transition: max-height 0.3s ease, opacity 0.3s ease, padding 0.3s ease;
                overflow: hidden;
            }
            
            .category-content:not(.hidden) {
                max-height: 1000px;
                opacity: 1;
                padding: 1rem;
                padding-top: 0;
            }
            
            .action-button {
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            .action-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }
            
            /* Fix Tailwind nếu không được load đầy đủ */
            .text-purple-400 { color: rgb(167, 139, 250); }
            .text-purple-500 { color: rgb(139, 92, 246); }
            .text-red-400 { color: rgb(248, 113, 113); }
            .bg-purple-600 { background-color: rgb(124, 58, 237); }
            .bg-purple-700 { background-color: rgb(109, 40, 217); }
            .bg-purple-900 { background-color: rgb(76, 29, 149); }
            .bg-red-900 { background-color: rgb(127, 29, 29); }
            .border-purple-500 { border-color: rgb(139, 92, 246); }
            .border-yellow-500 { border-color: rgb(234, 179, 8); }
            .hover\:bg-purple-700:hover { background-color: rgb(109, 40, 217); }
            .hover\:bg-gray-600:hover { background-color: rgb(75, 85, 99); }
            .hover\:text-purple-400:hover { color: rgb(167, 139, 250); }
            .hover\:text-red-400:hover { color: rgb(248, 113, 113); }
        </style>
    """
    
    # Đóng container chính
    html += "</div>"
    
    return html