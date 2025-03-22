/**
 * contact.js - JavaScript cho trang Liên hệ
 */

document.addEventListener('DOMContentLoaded', function() {
    // Cấu hình URL Google Form
    const GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform";
    const feedbackFormLink = document.getElementById('feedback-form-link');
    if (feedbackFormLink) {
        feedbackFormLink.href = GOOGLE_FORM_URL;
    }
    
    // Xử lý FAQ accordion
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        question.addEventListener('click', function() {
            // Toggle active class
            item.classList.toggle('active');
            
            // Animation cho phần answer
            const answer = item.querySelector('.faq-answer');
            if (item.classList.contains('active')) {
                answer.style.maxHeight = answer.scrollHeight + 'px';
            } else {
                answer.style.maxHeight = '0px';
            }
        });
    });
    
    // Khởi tạo animation ban đầu cho FAQ
    faqItems.forEach(item => {
        const answer = item.querySelector('.faq-answer');
        answer.style.maxHeight = '0px';
        answer.style.overflow = 'hidden';
        answer.style.transition = 'max-height 0.3s ease-out';
    });
    
    // Xử lý hover effect cho contact cards
    const contactCards = document.querySelectorAll('.contact-card');
    contactCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            card.classList.add('contact-card-hover');
        });
        
        card.addEventListener('mouseleave', function() {
            card.classList.remove('contact-card-hover');
        });
    });
    
    // Animation cho social links
    const socialLinks = document.querySelectorAll('.social-link');
    socialLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            const icon = link.querySelector('svg');
            icon.style.transform = 'scale(1.2)';
            icon.style.transition = 'transform 0.3s ease';
        });
        
        link.addEventListener('mouseleave', function() {
            const icon = link.querySelector('svg');
            icon.style.transform = 'scale(1)';
        });
    });
    
    // Tracking để biết các URLs đã được click
    const trackableLinks = document.querySelectorAll('a.contact-link, a.emergency-phone, a.social-link');
    trackableLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Lưu vào localStorage thông tin link đã click
            const clickHistory = JSON.parse(localStorage.getItem('contactClickHistory') || '[]');
            clickHistory.push({
                link: this.href,
                text: this.textContent.trim(),
                timestamp: new Date().toISOString()
            });
            localStorage.setItem('contactClickHistory', JSON.stringify(clickHistory));
            
            // Nếu link là số điện thoại khẩn cấp, hiển thị thông báo
            if (this.classList.contains('emergency-phone')) {
                // Khởi tạo toast notification
                createToastNotification('Đang kết nối đến dịch vụ khẩn cấp...', 'warning');
            }
        });
    });
    
    // Thêm animations khi scroll
    const animatedElements = document.querySelectorAll('.page-section');
    
    function checkScroll() {
        animatedElements.forEach(element => {
            const position = element.getBoundingClientRect();
            
            // Nếu phần tử đang hiển thị trong viewport
            if (position.top < window.innerHeight - 100) {
                element.classList.add('section-visible');
            }
        });
    }
    
    // Khởi tạo style cho animation
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
    });
    
    // Check scroll ban đầu và thêm listener
    window.addEventListener('scroll', checkScroll);
    checkScroll(); // Kiểm tra vị trí ban đầu
    
    // Toast notification helper function
    function createToastNotification(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Hiển thị toast
        setTimeout(() => {
            toast.classList.add('toast-visible');
        }, 100);
        
        // Xóa toast sau 3 giây
        setTimeout(() => {
            toast.classList.remove('toast-visible');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    // Add responsive behavior for contact cards
    function adjustContactCards() {
        const container = document.querySelector('.contact-cards-container');
        if (window.innerWidth < 768) {
            container.classList.add('contact-cards-mobile');
        } else {
            container.classList.remove('contact-cards-mobile');
        }
    }
    
    // Check initial state and add listener
    window.addEventListener('resize', adjustContactCards);
    adjustContactCards();
});