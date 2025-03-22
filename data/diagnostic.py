"""
Tiêu chí chẩn đoán đơn giản hóa từ DSM-5 và ICD-11
Chuyển đổi từ diagnostic.js sang Python
"""

# Tiêu chí chẩn đoán cho các rối loạn
diagnostic_criteria = {
    "depression": {
        "name": "Rối loạn trầm cảm",
        "description": "Rối loạn trầm cảm chính (Major Depressive Disorder) được đặc trưng bởi các giai đoạn tâm trạng trầm buồn kéo dài, mất hứng thú với hầu hết các hoạt động, và các triệu chứng khác.",
        "symptoms": [
            "Tâm trạng buồn bã, trống rỗng hoặc vô vọng",
            "Mất hứng thú hoặc niềm vui trong hầu hết các hoạt động",
            "Giảm cân đáng kể hoặc tăng cân không chủ ý",
            "Mất ngủ hoặc ngủ quá nhiều",
            "Kích động hoặc chậm chạp về tâm thần vận động",
            "Mệt mỏi hoặc mất năng lượng",
            "Cảm giác vô giá trị hoặc tội lỗi quá mức",
            "Khả năng tập trung hoặc suy nghĩ giảm sút",
            "Suy nghĩ tái diễn về cái chết hoặc ý định tự tử"
        ],
        "duration": "Các triệu chứng xuất hiện hầu hết ngày, gần như mỗi ngày, trong ít nhất 2 tuần",
        "impairment": "Gây suy giảm chức năng xã hội, nghề nghiệp hoặc các lĩnh vực quan trọng khác",
        "exclusions": "Không do các tác dụng sinh lý của một chất hoặc tình trạng y tế khác",
        "severity": {
            "mild": "Một số triệu chứng vượt quá mức cần thiết để chẩn đoán, gây suy giảm chức năng nhẹ",
            "moderate": "Các triệu chứng và suy giảm chức năng ở giữa 'nhẹ' và 'nặng'",
            "severe": "Số lượng triệu chứng vượt xa mức cần thiết, cường độ triệu chứng gây đau khổ lớn, và suy giảm chức năng nghiêm trọng"
        },
        "treatmentOptions": [
            "Tâm lý trị liệu (Liệu pháp nhận thức hành vi - CBT, Liệu pháp liên cá nhân - IPT)",
            "Thuốc chống trầm cảm (SSRIs, SNRIs)",
            "Kết hợp tâm lý trị liệu và thuốc",
            "Liệu pháp kích hoạt hành vi",
            "Tập thể dục thường xuyên",
            "Cải thiện giấc ngủ"
        ]
    },
    
    "anxiety": {
        "name": "Rối loạn lo âu",
        "description": "Rối loạn lo âu lan tỏa (Generalized Anxiety Disorder) đặc trưng bởi lo lắng và căng thẳng quá mức về nhiều sự kiện hoặc hoạt động, khó kiểm soát lo lắng, và nhiều triệu chứng thể chất.",
        "symptoms": [
            "Lo lắng và căng thẳng quá mức",
            "Khó kiểm soát những lo lắng",
            "Cảm thấy bồn chồn hoặc căng thẳng",
            "Dễ mệt mỏi",
            "Khó tập trung hoặc đầu óc trống rỗng",
            "Dễ cáu kỉnh",
            "Căng cơ",
            "Khó ngủ hoặc ngủ không ngon giấc"
        ],
        "duration": "Lo lắng xuất hiện nhiều ngày hơn không, trong ít nhất 6 tháng",
        "impairment": "Gây đau khổ đáng kể hoặc suy giảm chức năng xã hội, nghề nghiệp, hoặc các lĩnh vực quan trọng khác",
        "exclusions": "Không do các tác dụng sinh lý của một chất hoặc tình trạng y tế khác",
        "severity": {
            "mild": "Một số triệu chứng vượt quá mức cần thiết để chẩn đoán, gây suy giảm chức năng nhẹ",
            "moderate": "Các triệu chứng và suy giảm chức năng ở giữa 'nhẹ' và 'nặng'",
            "severe": "Số lượng triệu chứng vượt xa mức cần thiết, cường độ triệu chứng gây đau khổ lớn, và suy giảm chức năng nghiêm trọng"
        },
        "treatmentOptions": [
            "Tâm lý trị liệu (Liệu pháp nhận thức hành vi - CBT)",
            "Thuốc (SSRIs, SNRIs, Benzodiazepines trong ngắn hạn)",
            "Kỹ thuật thư giãn",
            "Thiền chánh niệm",
            "Tập thể dục thường xuyên",
            "Giảm caffeine và rượu"
        ]
    },
    
    "stress": {
        "name": "Rối loạn liên quan đến căng thẳng",
        "description": "Căng thẳng quá mức có thể dẫn đến nhiều vấn đề sức khỏe tâm thần và thể chất.",
        "symptoms": [
            "Cảm thấy quá tải hoặc áp lực",
            "Khó thư giãn hoặc nghỉ ngơi",
            "Dễ cáu kỉnh hoặc tức giận",
            "Mệt mỏi",
            "Khó tập trung",
            "Căng cơ hoặc đau",
            "Thay đổi về giấc ngủ hoặc ăn uống",
            "Sử dụng rượu hoặc chất kích thích khác để đối phó"
        ],
        "duration": "Triệu chứng có thể cấp tính (ngắn hạn do một sự kiện cụ thể) hoặc mãn tính (kéo dài)",
        "impairment": "Gây đau khổ hoặc ảnh hưởng đến chức năng hàng ngày",
        "severity": {
            "mild": "Các triệu chứng thỉnh thoảng xuất hiện nhưng có thể quản lý được",
            "moderate": "Các triệu chứng thường xuyên hơn và đôi khi khó quản lý",
            "severe": "Các triệu chứng liên tục và gây suy giảm đáng kể chất lượng cuộc sống"
        },
        "treatmentOptions": [
            "Kỹ thuật quản lý căng thẳng",
            "Kỹ thuật thư giãn và chánh niệm",
            "Tập thể dục thường xuyên",
            "Cải thiện giấc ngủ",
            "Tâm lý trị liệu",
            "Thay đổi lối sống hoặc môi trường"
        ]
    }
}

def get_disorder_info(disorder):
    """
    Lấy thông tin về rối loạn dựa trên loại rối loạn
    """
    return diagnostic_criteria.get(disorder, None)

def format_disorder_info(disorder):
    """
    Định dạng thông tin về rối loạn thành tin nhắn có thể hiển thị
    """
    info = get_disorder_info(disorder)
    if not info:
        return ""
    
    message = f"## {info['name']}\n\n"
    message += f"{info['description']}\n\n"
    
    message += "### Triệu chứng chính\n"
    for symptom in info['symptoms']:
        message += f"- {symptom}\n"
    message += "\n"
    
    if 'duration' in info:
        message += f"### Thời gian: {info['duration']}\n\n"
    
    if 'impairment' in info:
        message += f"### Ảnh hưởng: {info['impairment']}\n\n"
    
    message += "### Mức độ nghiêm trọng\n"
    for level, description in info['severity'].items():
        message += f"- **{level}**: {description}\n"
    message += "\n"
    
    message += "### Các phương pháp điều trị có thể\n"
    for option in info['treatmentOptions']:
        message += f"- {option}\n"
    
    message += "\n*Lưu ý: Thông tin này chỉ mang tính chất tham khảo. Chỉ chuyên gia sức khỏe tâm thần mới có thể đưa ra chẩn đoán và kế hoạch điều trị chính xác.*"
    
    return message