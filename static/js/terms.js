/**
 * terms.js - JavaScript cho trang Điều khoản sử dụng
 */

document.addEventListener('DOMContentLoaded', function() {
    // Giả lập đếm số lượt xem điều khoản dịch vụ
    const viewCounter = localStorage.getItem('termsViewCount') || 0;
    localStorage.setItem('termsViewCount', parseInt(viewCounter) + 1);

    // Tự động thêm links cho các mục quan trọng
    const emergencyItems = document.querySelectorAll('.emergency-list li');
    emergencyItems.forEach(item => {
        const text = item.textContent;
        if (text.includes('115')) {
            item.innerHTML = item.innerHTML.replace('115', '<a href="tel:115" class="emergency-link">115</a>');
        }
        if (text.includes('1800-8440')) {
            item.innerHTML = item.innerHTML.replace('1800-8440', '<a href="tel:18008440" class="emergency-link">1800-8440</a>');
        }
    });

    // Thêm timestamp cho thời gian xem điều khoản
    const termsDateElement = document.querySelector('.terms-date');
    if (termsDateElement) {
        const viewTimestamp = document.createElement('p');
        viewTimestamp.className = 'terms-view-timestamp';
        viewTimestamp.innerHTML = `<small>Thời gian xem: ${new Date().toLocaleString('vi-VN')}</small>`;
        termsDateElement.appendChild(viewTimestamp);
    }

    // Highlight các từ khóa quan trọng
    const highlightKeywords = ['không phải dịch vụ y tế', 'không phải là dịch vụ ứng phó khẩn cấp', 'không nên được sử dụng thay thế'];
    const paragraphs = document.querySelectorAll('.privacy-card p');
    
    paragraphs.forEach(paragraph => {
        highlightKeywords.forEach(keyword => {
            if (paragraph.innerHTML.includes(keyword) && !paragraph.innerHTML.includes(`<span class="highlight">${keyword}</span>`)) {
                paragraph.innerHTML = paragraph.innerHTML.replace(
                    keyword, 
                    `<span class="highlight">${keyword}</span>`
                );
            }
        });
    });

    // Animation cho các card khi scroll
    const privacyCards = document.querySelectorAll('.privacy-card');
    
    function checkCardVisibility() {
        privacyCards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const isVisible = (
                rect.top >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight)
            );
            
            if (isVisible) {
                card.classList.add('card-visible');
            }
        });
    }
    
    // Check initial visibility
    checkCardVisibility();
    
    // Listen for scroll events
    window.addEventListener('scroll', checkCardVisibility);
});