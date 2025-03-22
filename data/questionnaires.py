"""
Dữ liệu các bộ câu hỏi đánh giá sức khỏe tâm thần
Chuyển đổi từ questionnaires.js sang Python
"""

# Dữ liệu bộ câu hỏi
questionnaires = {
    "initialScreening": {
        "id": "initialScreening",
        "name": "Sàng lọc Ban đầu",
        "description": "Câu hỏi tổng quát để hiểu tình trạng của bạn",
        "questions": [
            {
                "id": "feeling_tired",
                "text": "Trong 2 tuần qua, bạn có thường cảm thấy mệt mỏi mà không có lý do rõ ràng không?",
                "options": [
                    { "value": 0, "text": "Không bao giờ" },
                    { "value": 1, "text": "Hiếm khi" },
                    { "value": 2, "text": "Thỉnh thoảng" },
                    { "value": 3, "text": "Thường xuyên" },
                    { "value": 4, "text": "Luôn luôn" }
                ],
                "category": "stress"
            },
            {
                "id": "worried",
                "text": "Bạn có thường cảm thấy lo lắng, căng thẳng hoặc bồn chồn không?",
                "options": [
                    { "value": 0, "text": "Không bao giờ" },
                    { "value": 1, "text": "Hiếm khi" },
                    { "value": 2, "text": "Thỉnh thoảng" },
                    { "value": 3, "text": "Thường xuyên" },
                    { "value": 4, "text": "Luôn luôn" }
                ],
                "category": "anxiety"
            },
            {
                "id": "relax_difficulty",
                "text": "Bạn có thấy khó thư giãn không?",
                "options": [
                    { "value": 0, "text": "Không bao giờ" },
                    { "value": 1, "text": "Hiếm khi" },
                    { "value": 2, "text": "Thỉnh thoảng" },
                    { "value": 3, "text": "Thường xuyên" },
                    { "value": 4, "text": "Luôn luôn" }
                ],
                "category": "anxiety"
            },
            {
                "id": "sad_feelings",
                "text": "Bạn có thường cảm thấy buồn bã hoặc chán nản không?",
                "options": [
                    { "value": 0, "text": "Không bao giờ" },
                    { "value": 1, "text": "Hiếm khi" },
                    { "value": 2, "text": "Thỉnh thoảng" },
                    { "value": 3, "text": "Thường xuyên" },
                    { "value": 4, "text": "Luôn luôn" }
                ],
                "category": "depression"
            },
            {
                "id": "lost_interest",
                "text": "Bạn có mất hứng thú với những hoạt động mà trước đây bạn thích thú không?",
                "options": [
                    { "value": 0, "text": "Không bao giờ" },
                    { "value": 1, "text": "Hiếm khi" },
                    { "value": 2, "text": "Thỉnh thoảng" },
                    { "value": 3, "text": "Thường xuyên" },
                    { "value": 4, "text": "Luôn luôn" }
                ],
                "category": "depression"
            },
            {
                "id": "worthless",
                "text": "Bạn có cảm thấy vô giá trị không?",
                "options": [
                    { "value": 0, "text": "Không bao giờ" },
                    { "value": 1, "text": "Hiếm khi" },
                    { "value": 2, "text": "Thỉnh thoảng" },
                    { "value": 3, "text": "Thường xuyên" },
                    { "value": 4, "text": "Luôn luôn" }
                ],
                "category": "depression"
            },
            {
                "id": "life_not_worth",
                "text": "Bạn có cảm thấy cuộc sống không đáng sống không?",
                "options": [
                    { "value": 0, "text": "Không bao giờ" },
                    { "value": 1, "text": "Hiếm khi" },
                    { "value": 2, "text": "Thỉnh thoảng" },
                    { "value": 3, "text": "Thường xuyên" },
                    { "value": 4, "text": "Luôn luôn" }
                ],
                "category": "depression",
                "flag": "suicide_risk"
            },
            {
                "id": "sleep_issues",
                "text": "Bạn có gặp khó khăn trong việc ngủ (ngủ quá nhiều hoặc quá ít) không?",
                "options": [
                    { "value": 0, "text": "Không bao giờ" },
                    { "value": 1, "text": "Hiếm khi" },
                    { "value": 2, "text": "Thỉnh thoảng" },
                    { "value": 3, "text": "Thường xuyên" },
                    { "value": 4, "text": "Luôn luôn" }
                ],
                "category": "stress"
            },
            {
                "id": "eating_issues",
                "text": "Bạn có gặp vấn đề về ăn uống (ăn quá nhiều hoặc quá ít) không?",
                "options": [
                    { "value": 0, "text": "Không bao giờ" },
                    { "value": 1, "text": "Hiếm khi" },
                    { "value": 2, "text": "Thỉnh thoảng" },
                    { "value": 3, "text": "Thường xuyên" },
                    { "value": 4, "text": "Luôn luôn" }
                ],
                "category": "stress"
            },
            {
                "id": "panic",
                "text": "Bạn có dễ bị hoảng sợ hoặc sợ hãi không?",
                "options": [
                    { "value": 0, "text": "Không bao giờ" },
                    { "value": 1, "text": "Hiếm khi" },
                    { "value": 2, "text": "Thỉnh thoảng" },
                    { "value": 3, "text": "Thường xuyên" },
                    { "value": 4, "text": "Luôn luôn" }
                ],
                "category": "anxiety"
            }
        ],
        "scoring": {
            "depression": {
                "questions": ["sad_feelings", "lost_interest", "worthless", "life_not_worth"],
                "thresholds": { "minimal": 3, "mild": 6, "moderate": 9, "severe": 12 }
            },
            "anxiety": {
                "questions": ["worried", "relax_difficulty", "panic"],
                "thresholds": { "minimal": 2, "mild": 5, "moderate": 8, "severe": 10 }
            },
            "stress": {
                "questions": ["feeling_tired", "sleep_issues", "eating_issues"],
                "thresholds": { "minimal": 2, "mild": 5, "moderate": 8, "severe": 10 }
            }
        },
        "nextAssessment": {
            "depression": "phq9",
            "anxiety": "gad7",
            "stress": "dass21_stress"
        }
    },
    
    "phq9": {
        "id": "phq9",
        "name": "PHQ-9",
        "description": "Bộ câu hỏi đánh giá trầm cảm",
        "questions": [
            {
                "id": "phq9_interest",
                "text": "Bạn có ít hứng thú hoặc niềm vui khi làm mọi việc không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "phq9_depressed",
                "text": "Bạn có cảm thấy buồn bã, chán nản, hoặc tuyệt vọng không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "phq9_sleep",
                "text": "Bạn có gặp khó khăn khi ngủ, ngủ không ngon giấc, hoặc ngủ quá nhiều không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "phq9_tired",
                "text": "Bạn có cảm thấy mệt mỏi hoặc ít năng lượng không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "phq9_appetite",
                "text": "Bạn có ăn kém ngon miệng hoặc ăn quá nhiều không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "phq9_feeling_bad",
                "text": "Bạn có cảm thấy không tốt về bản thân - hoặc cảm thấy mình là người thất bại hay đã làm thất vọng bản thân hoặc gia đình không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "phq9_concentration",
                "text": "Bạn có khó tập trung vào mọi việc, chẳng hạn như đọc báo hoặc xem TV không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "phq9_moving",
                "text": "Bạn có di chuyển hoặc nói chuyện chậm chạp đến mức người khác có thể nhận thấy? Hoặc ngược lại - cảm thấy bồn chồn hoặc không thể ngồi yên đến mức bạn di chuyển nhiều hơn bình thường không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "phq9_suicide",
                "text": "Bạn có nghĩ rằng mình nên chết đi hoặc nghĩ đến việc tự làm tổn thương bản thân bằng cách nào đó không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ],
                "flag": "suicide_risk"
            },
            {
                "id": "phq9_difficulty",
                "text": "Nếu bạn đã đánh dấu bất kỳ vấn đề nào ở trên, những vấn đề này đã gây khó khăn cho bạn như thế nào trong việc làm việc, chăm sóc mọi thứ ở nhà, hoặc hòa hợp với mọi người?",
                "options": [
                    { "value": 0, "text": "Không khó khăn gì" },
                    { "value": 1, "text": "Hơi khó khăn" },
                    { "value": 2, "text": "Rất khó khăn" },
                    { "value": 3, "text": "Cực kỳ khó khăn" }
                ]
            }
        ],
        "scoring": {
            "questions": ["phq9_interest", "phq9_depressed", "phq9_sleep", "phq9_tired", "phq9_appetite", "phq9_feeling_bad", "phq9_concentration", "phq9_moving", "phq9_suicide"],
            "thresholds": { 
                "minimal": 4, 
                "mild": 9, 
                "moderate": 14, 
                "moderatelySevere": 19, 
                "severe": 27 
            }
        }
    },
    
    "gad7": {
        "id": "gad7",
        "name": "GAD-7",
        "description": "Bộ câu hỏi đánh giá lo âu",
        "questions": [
            {
                "id": "gad7_nervous",
                "text": "Bạn có cảm thấy lo lắng, bồn chồn hoặc căng thẳng không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "gad7_control",
                "text": "Bạn có không thể ngừng hoặc kiểm soát lo lắng không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "gad7_worry",
                "text": "Bạn có lo lắng quá nhiều về nhiều thứ khác nhau không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "gad7_relax",
                "text": "Bạn có khó thư giãn không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "gad7_restless",
                "text": "Bạn có bồn chồn đến mức khó ngồi yên không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "gad7_irritable",
                "text": "Bạn có dễ cáu kỉnh hoặc khó chịu không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "gad7_afraid",
                "text": "Bạn có cảm thấy sợ hãi như thể điều gì đó tồi tệ có thể xảy ra không?",
                "options": [
                    { "value": 0, "text": "Không có" },
                    { "value": 1, "text": "Vài ngày" },
                    { "value": 2, "text": "Hơn nửa số ngày" },
                    { "value": 3, "text": "Gần như mỗi ngày" }
                ]
            },
            {
                "id": "gad7_difficulty",
                "text": "Nếu bạn đã đánh dấu bất kỳ vấn đề nào, những vấn đề này đã gây khó khăn cho bạn như thế nào trong công việc, chăm sóc mọi thứ ở nhà, hoặc hòa hợp với mọi người?",
                "options": [
                    { "value": 0, "text": "Không khó khăn gì" },
                    { "value": 1, "text": "Hơi khó khăn" },
                    { "value": 2, "text": "Rất khó khăn" },
                    { "value": 3, "text": "Cực kỳ khó khăn" }
                ]
            }
        ],
        "scoring": {
            "questions": ["gad7_nervous", "gad7_control", "gad7_worry", "gad7_relax", "gad7_restless", "gad7_irritable", "gad7_afraid"],
            "thresholds": { 
                "minimal": 4, 
                "mild": 9, 
                "moderate": 14, 
                "severe": 21 
            }
        }
    },
    
    "dass21_stress": {
        "id": "dass21_stress",
        "name": "DASS-21 (Phần Căng thẳng)",
        "description": "Đánh giá mức độ căng thẳng",
        "questions": [
            {
                "id": "dass_relax",
                "text": "Bạn có thấy khó thư giãn không?",
                "options": [
                    { "value": 0, "text": "Không áp dụng với tôi" },
                    { "value": 1, "text": "Áp dụng với tôi ở một mức độ nhất định, hoặc thỉnh thoảng" },
                    { "value": 2, "text": "Áp dụng với tôi ở mức đáng kể, hoặc phần lớn thời gian" },
                    { "value": 3, "text": "Áp dụng rất nhiều với tôi, hoặc hầu hết thời gian" }
                ]
            },
            {
                "id": "dass_overreact",
                "text": "Bạn có nhận thấy mình dễ phản ứng thái quá không?",
                "options": [
                    { "value": 0, "text": "Không áp dụng với tôi" },
                    { "value": 1, "text": "Áp dụng với tôi ở một mức độ nhất định, hoặc thỉnh thoảng" },
                    { "value": 2, "text": "Áp dụng với tôi ở mức đáng kể, hoặc phần lớn thời gian" },
                    { "value": 3, "text": "Áp dụng rất nhiều với tôi, hoặc hầu hết thời gian" }
                ]
            },
            {
                "id": "dass_nervous",
                "text": "Bạn có cảm thấy căng thẳng thần kinh không?",
                "options": [
                    { "value": 0, "text": "Không áp dụng với tôi" },
                    { "value": 1, "text": "Áp dụng với tôi ở một mức độ nhất định, hoặc thỉnh thoảng" },
                    { "value": 2, "text": "Áp dụng với tôi ở mức đáng kể, hoặc phần lớn thời gian" },
                    { "value": 3, "text": "Áp dụng rất nhiều với tôi, hoặc hầu hết thời gian" }
                ]
            },
            {
                "id": "dass_impatient",
                "text": "Bạn có thấy mình khó chịu đựng khi bị gián đoạn không?",
                "options": [
                    { "value": 0, "text": "Không áp dụng với tôi" },
                    { "value": 1, "text": "Áp dụng với tôi ở một mức độ nhất định, hoặc thỉnh thoảng" },
                    { "value": 2, "text": "Áp dụng với tôi ở mức đáng kể, hoặc phần lớn thời gian" },
                    { "value": 3, "text": "Áp dụng rất nhiều với tôi, hoặc hầu hết thời gian" }
                ]
            },
            {
                "id": "dass_agitated",
                "text": "Bạn có thấy mình dễ bị kích động không?",
                "options": [
                    { "value": 0, "text": "Không áp dụng với tôi" },
                    { "value": 1, "text": "Áp dụng với tôi ở một mức độ nhất định, hoặc thỉnh thoảng" },
                    { "value": 2, "text": "Áp dụng với tôi ở mức đáng kể, hoặc phần lớn thời gian" },
                    { "value": 3, "text": "Áp dụng rất nhiều với tôi, hoặc hầu hết thời gian" }
                ]
            },
            {
                "id": "dass_intolerant",
                "text": "Bạn có thấy khó dung nạp bất cứ điều gì cản trở bạn tiếp tục những việc bạn đang làm không?",
                "options": [
                    { "value": 0, "text": "Không áp dụng với tôi" },
                    { "value": 1, "text": "Áp dụng với tôi ở một mức độ nhất định, hoặc thỉnh thoảng" },
                    { "value": 2, "text": "Áp dụng với tôi ở mức đáng kể, hoặc phần lớn thời gian" },
                    { "value": 3, "text": "Áp dụng rất nhiều với tôi, hoặc hầu hết thời gian" }
                ]
            },
            {
                "id": "dass_touchy",
                "text": "Bạn có thấy mình dễ lo lắng không?",
                "options": [
                    { "value": 0, "text": "Không áp dụng với tôi" },
                    { "value": 1, "text": "Áp dụng với tôi ở một mức độ nhất định, hoặc thỉnh thoảng" },
                    { "value": 2, "text": "Áp dụng với tôi ở mức đáng kể, hoặc phần lớn thời gian" },
                    { "value": 3, "text": "Áp dụng rất nhiều với tôi, hoặc hầu hết thời gian" }
                ]
            }
        ],
        "scoring": {
            "questions": ["dass_relax", "dass_overreact", "dass_nervous", "dass_impatient", "dass_agitated", "dass_intolerant", "dass_touchy"],
            "thresholds": { 
                "normal": 7, 
                "mild": 9, 
                "moderate": 12, 
                "severe": 16, 
                "extremelySevere": 21 
            }
        }
    },
    
    "suicideRiskAssessment": {
        "id": "suicideRiskAssessment",
        "name": "Đánh giá Nguy cơ Tự tử",
        "description": "Câu hỏi đánh giá khẩn cấp khi phát hiện dấu hiệu nguy cơ",
        "questions": [
            {
                "id": "suicide_intent",
                "text": "Bạn có đang có ý định tự làm hại bản thân không?",
                "options": [
                    { "value": 0, "text": "Không" },
                    { "value": 3, "text": "Có" }
                ]
            },
            {
                "id": "suicide_plan",
                "text": "Bạn đã có kế hoạch cụ thể nào để tự làm hại bản thân chưa?",
                "options": [
                    { "value": 0, "text": "Không" },
                    { "value": 3, "text": "Có" }
                ]
            },
            {
                "id": "suicide_history",
                "text": "Bạn có từng cố gắng tự làm hại bản thân trước đây không?",
                "options": [
                    { "value": 0, "text": "Không" },
                    { "value": 2, "text": "Có" }
                ]
            }
        ],
        "scoring": {
            "questions": ["suicide_intent", "suicide_plan", "suicide_history"],
            "thresholds": { 
                "low": 1, 
                "moderate": 3, 
                "high": 5, 
                "severe": 8 
            }
        }
    }
}

# Thông báo khẩn cấp cho nguy cơ tự tử
emergency_message = """THÔNG BÁO KHẨN CẤP: Nếu bạn đang có ý định tự hại bản thân, vui lòng liên hệ ngay với các dịch vụ hỗ trợ khủng hoảng sau:  
- Đường dây nóng phòng chống tự tử: 1800-8440 (miễn phí)
- Gọi cho người thân hoặc bạn bè tin cậy  
- Đến phòng cấp cứu gần nhất  
- Gọi số cấp cứu: 115"""