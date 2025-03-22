/**
 * Chat.js - Xử lý logic giao diện cho ứng dụng chatbot
 * Cập nhật để sử dụng localStorage thay vì session
 */

document.addEventListener('DOMContentLoaded', function() {
    // Các element
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const aiModeToggle = document.getElementById('ai-mode-toggle');
    const chatModeIndicator = document.getElementById('chat-mode-indicator');
    const restartButton = document.getElementById('restart-chat');
    const toggleInfoButton = document.getElementById('toggle-info');
    const closeInfoButton = document.getElementById('close-info');
    const infoSidebar = document.getElementById('info-sidebar');
    const currentAssessment = document.getElementById('current-assessment');
    
    // Templates
    const userMessageTemplate = document.getElementById('user-message-template');
    const botMessageTemplate = document.getElementById('bot-message-template');
    const errorMessageTemplate = document.getElementById('error-message-template');
    
    // Biến trạng thái
    let isLoading = false;
    let useAI = true;
    
    // Hàm xử lý localStorage
    function saveMessagesToLocalStorage(messages) {
        localStorage.setItem('chatMessages', JSON.stringify(messages));
    }
    
    function loadMessagesFromLocalStorage() {
        const messagesJson = localStorage.getItem('chatMessages');
        return messagesJson ? JSON.parse(messagesJson) : [];
    }
    
    function saveChatStateToLocalStorage(chatState) {
        localStorage.setItem('chatState', JSON.stringify(chatState));
    }
    
    function loadChatStateFromLocalStorage() {
        const stateJson = localStorage.getItem('chatState');
        return stateJson ? JSON.parse(stateJson) : null;
    }
    
    // Kiểm tra và hiển thị tin nhắn từ localStorage
    function loadChatHistory() {
        const messages = loadMessagesFromLocalStorage();
        
        if (messages && messages.length > 0) {
            // Hiển thị các tin nhắn đã lưu
            chatMessages.innerHTML = ''; // Xóa tin nhắn hiện tại nếu có
            messages.forEach(message => {
                addMessageToUI(message.content, message.role, message.id, message.timestamp);
            });
            return true;
        }
        return false;
    }
    
    // Kiểm tra và hiển thị lịch sử hoặc tin nhắn chào mừng
    function checkForWelcomeMessage() {
        const historyLoaded = loadChatHistory();
        
        if (!historyLoaded) {
            // Nếu không có lịch sử, lấy tin nhắn chào mừng từ server
            fetch('/api/restart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    preserveLocalMessages: false
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.welcomeMessage) {
                    // Lưu vào localStorage và hiển thị
                    const messages = [];
                    messages.push(data.welcomeMessage);
                    saveMessagesToLocalStorage(messages);
                    addMessageToUI(data.welcomeMessage.content, 'bot', data.welcomeMessage.id, data.welcomeMessage.timestamp);
                    
                    // Lưu trạng thái chat
                    if (data.chatState) {
                        saveChatStateToLocalStorage(data.chatState);
                    }
                    
                    // Cập nhật hiển thị assessment
                    if (data.chatState && data.chatState.state) {
                        updateCurrentAssessment(data.chatState.state);
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching welcome message:', error);
                const defaultMessage = {
                    content: 'Xin chào! Tôi là trợ lý sức khỏe tâm thần. Tôi có thể giúp gì cho bạn?',
                    role: 'bot',
                    id: 'welcome-default',
                    timestamp: getCurrentTime()
                };
                const messages = [defaultMessage];
                saveMessagesToLocalStorage(messages);
                addMessageToUI(defaultMessage.content, 'bot', defaultMessage.id, defaultMessage.timestamp);
            });
        }
    }
    
    // Hiển thị ngay khi trang tải
    checkForWelcomeMessage();
    
    // Sự kiện
    userInput.addEventListener('input', handleInputChange);
    userInput.addEventListener('keydown', handleKeyDown);
    chatForm.addEventListener('submit', handleSubmit);
    aiModeToggle.addEventListener('change', toggleAIMode);
    restartButton.addEventListener('click', restartChat);
    toggleInfoButton.addEventListener('click', toggleInfoSidebar);
    closeInfoButton.addEventListener('click', toggleInfoSidebar);
    
    /**
     * Xử lý khi người dùng nhập liệu
     */
    function handleInputChange() {
        // Tự động điều chỉnh chiều cao textarea
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
        
        // Vô hiệu hóa/kích hoạt nút gửi
        sendButton.disabled = userInput.value.trim() === '' || isLoading;
    }
    
    /**
     * Xử lý khi người dùng nhấn phím
     */
    function handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendButton.disabled) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    }
    
    /**
     * Xử lý khi người dùng gửi tin nhắn
     */
    function handleSubmit(e) {
        e.preventDefault();
        
        if (userInput.value.trim() === '' || isLoading) return;
        
        const message = userInput.value;
        
        // Hiển thị tin nhắn người dùng
        const messageId = 'msg-' + Date.now();
        const timestamp = getCurrentTime();
        
        // Thêm tin nhắn vào UI
        addMessageToUI(message, 'user', messageId, timestamp);
        
        // Thêm tin nhắn vào localStorage
        const messages = loadMessagesFromLocalStorage();
        messages.push({
            role: 'user',
            content: message,
            id: messageId,
            timestamp: timestamp
        });
        saveMessagesToLocalStorage(messages);
        
        // Xóa input và reset kích thước
        userInput.value = '';
        userInput.style.height = 'auto';
        sendButton.disabled = true;
        
        // Hiển thị hiệu ứng đang nhập
        showTypingIndicator();
        
        // Gọi API
        sendMessageToServer(message);
    }
    
    /**
     * Gửi tin nhắn đến server
     */
    function sendMessageToServer(message) {
        isLoading = true;
        updateChatModeIndicator();
        
        // Lấy lịch sử chat từ localStorage
        const messages = loadMessagesFromLocalStorage();
        // Chỉ lấy 15 tin nhắn gần nhất để tạo ngữ cảnh
        const recentMessages = messages.slice(-15);
        
        // Lấy trạng thái chat từ localStorage
        const chatState = loadChatStateFromLocalStorage();
        
        fetch('/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                useAI: useAI,
                messageHistory: recentMessages,
                chatState: chatState
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Ẩn hiệu ứng đang nhập
            hideTypingIndicator();
            
            // Hiển thị phản hồi từ bot
            if (data.error) {
                showErrorMessage(data.error);
            } else {
                // Thêm tin nhắn bot vào UI
                addMessageToUI(data.text, 'bot', data.id, data.timestamp);
                
                // Thêm tin nhắn bot vào localStorage
                const messages = loadMessagesFromLocalStorage();
                messages.push({
                    role: 'assistant',
                    content: data.text,
                    id: data.id,
                    timestamp: data.timestamp
                });
                saveMessagesToLocalStorage(messages);
                
                // Lưu trạng thái chat mới
                if (data.chatState) {
                    saveChatStateToLocalStorage(data.chatState);
                }
                
                // Cập nhật trạng thái đánh giá hiện tại nếu có
                if (data.state) {
                    updateCurrentAssessment(data.state);
                }
            }
        })
        .catch(error => {
            hideTypingIndicator();
            showErrorMessage(error.message);
        })
        .finally(() => {
            isLoading = false;
            updateChatModeIndicator();
        });
    }
    
    /**
     * Chuyển đổi chế độ AI/Logic
     */
    function toggleAIMode() {
        useAI = aiModeToggle.checked;
        
        fetch('/api/toggle_ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                useAI: useAI
            })
        })
        .catch(error => {
            console.error('Error toggling AI mode:', error);
        });
        
        updateChatModeIndicator();
    }
    
    /**
     * Cập nhật hiển thị chế độ chat hiện tại
     */
    function updateChatModeIndicator() {
        if (isLoading) {
            chatModeIndicator.textContent = "Trợ lý đang trả lời...";
            chatModeIndicator.classList.add('loading');
        } else {
            chatModeIndicator.textContent = useAI ? "Chế độ AI" : "Chế độ Logic";
            chatModeIndicator.classList.remove('loading');
        }
    }
    
    /**
     * Khởi động lại cuộc trò chuyện
     */
    function restartChat() {
        if (isLoading) return;
        
        // Xác nhận từ người dùng
        if (!confirm("Bạn có chắc chắn muốn bắt đầu lại cuộc trò chuyện? Tất cả lịch sử trò chuyện sẽ bị xóa.")) {
            return;
        }
        
        isLoading = true;
        
        fetch('/api/restart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                preserveLocalMessages: false
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Xóa lịch sử trong localStorage
                localStorage.removeItem('chatMessages');
                
                // Xóa tất cả tin nhắn trên UI
                chatMessages.innerHTML = '';
                
                // Hiển thị tin nhắn chào mừng
                if (data.welcomeMessage) {
                    // Lưu vào localStorage và hiển thị
                    const messages = [data.welcomeMessage];
                    saveMessagesToLocalStorage(messages);
                    addMessageToUI(data.welcomeMessage.content, 'bot', data.welcomeMessage.id, data.welcomeMessage.timestamp);
                }
                
                // Lưu trạng thái chat mới
                if (data.chatState) {
                    saveChatStateToLocalStorage(data.chatState);
                }
                
                // Reset current assessment
                currentAssessment.textContent = 'Trò chuyện';
            } else {
                alert('Không thể khởi động lại cuộc trò chuyện. Vui lòng thử lại sau.');
            }
        })
        .catch(error => {
            console.error('Error restarting chat:', error);
            alert('Đã xảy ra lỗi khi khởi động lại cuộc trò chuyện.');
        })
        .finally(() => {
            isLoading = false;
        });
    }
    
    /**
     * Hiện/ẩn sidebar thông tin
     */
    function toggleInfoSidebar() {
        infoSidebar.classList.toggle('hidden');
    }
    
    /**
     * Thêm tin nhắn vào UI
     */
    function addMessageToUI(content, role, id, timestamp) {
        let messageElement;
        
        if (role === 'user') {
            // Tạo tin nhắn người dùng
            messageElement = userMessageTemplate.content.cloneNode(true);
            messageElement.querySelector('p').textContent = content;
        } else {
            // Tạo tin nhắn bot
            messageElement = botMessageTemplate.content.cloneNode(true);
            const messageText = messageElement.querySelector('.message-text');
            
            // Xử lý Markdown nếu là tin nhắn bot
            messageText.innerHTML = renderMarkdown(content);
        }
        
        // Thêm timestamp
        messageElement.querySelector('.message-time').textContent = timestamp || getCurrentTime();
        
        // Thêm message vào container
        const messageDiv = messageElement.querySelector('.message');
        messageDiv.setAttribute('data-id', id);
        chatMessages.appendChild(messageDiv);
        
        // Cuộn xuống tin nhắn mới nhất
        scrollToBottom();
        
        // Đảm bảo rằng tin nhắn mới nhất hiển thị sau khi render
        setTimeout(scrollToBottom, 100);
    }
    
    /**
     * Chuyển đổi Markdown đơn giản sang HTML
     */
    function renderMarkdown(text) {
        if (!text) return '';
        
        let html = text;
        
        // Headers
        html = html.replace(/## (.*?)$/gm, '<h2>$1</h2>');
        html = html.replace(/### (.*?)$/gm, '<h3>$1</h3>');
        
        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Lists
        html = html.replace(/^\- (.*?)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*?<\/li>)\n(<li>.*?<\/li>)/gs, '$1$2');
        html = html.replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>');
        
        // Links
        html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
        
        // Paragraphs
        html = html.replace(/\n\n/g, '</p><p>');
        
        // Line breaks
        html = html.replace(/\n/g, '<br>');
        
        return '<p>' + html + '</p>';
    }
    
    /**
     * Hiển thị hiệu ứng đang nhập
     */
    function showTypingIndicator() {
        const typingElement = botMessageTemplate.content.cloneNode(true);
        typingElement.querySelector('.message-text').classList.add('hidden');
        typingElement.querySelector('.typing-indicator').classList.remove('hidden');
        
        const typingDiv = typingElement.querySelector('.message');
        typingDiv.setAttribute('data-id', 'typing-indicator');
        typingDiv.classList.add('typing');
        
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }
    
    /**
     * Ẩn hiệu ứng đang nhập
     */
    function hideTypingIndicator() {
        const typingDiv = document.querySelector('.message[data-id="typing-indicator"]');
        if (typingDiv) {
            typingDiv.remove();
        }
    }
    
    /**
     * Hiển thị tin nhắn lỗi
     */
    function showErrorMessage(errorMessage) {
        const errorElement = errorMessageTemplate.content.cloneNode(true);
        errorElement.querySelector('.error-description').textContent = errorMessage;
        
        const toggleButton = errorElement.querySelector('#toggle-ai-mode');
        toggleButton.textContent = useAI ? "Chuyển sang chế độ không AI" : "Chuyển sang chế độ AI";
        toggleButton.addEventListener('click', function() {
            aiModeToggle.checked = !aiModeToggle.checked;
            toggleAIMode();
            this.closest('.error-message').remove();
        });
        
        const errorDiv = errorElement.querySelector('.error-message');
        errorDiv.setAttribute('data-id', 'error-' + Date.now());
        
        chatMessages.appendChild(errorDiv);
        scrollToBottom();
    }
    
    /**
     * Cập nhật hiển thị đánh giá hiện tại
     */
    function updateCurrentAssessment(state) {
        let assessmentName = 'Trò chuyện';
        
        if (state === 'initial_screening') {
            assessmentName = 'Sàng lọc ban đầu';
        } else if (state === 'detailed_assessment' || state === 'additional_assessment') {
            assessmentName = 'Đánh giá chi tiết';
        } else if (state === 'suicide_assessment') {
            assessmentName = 'Đánh giá nguy cơ';
        } else if (state === 'summary') {
            assessmentName = 'Tóm tắt';
        } else if (state === 'resources') {
            assessmentName = 'Tài nguyên hỗ trợ';
        }
        
        currentAssessment.textContent = assessmentName;
    }
    
    /**
     * Cuộn xuống tin nhắn mới nhất
     */
    function scrollToBottom() {
        const chatMessages = document.getElementById('chat-messages');
        // Sử dụng smooth scrolling để tạo hiệu ứng mượt mà
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    /**
     * Lấy thời gian hiện tại
     */
    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    }
});