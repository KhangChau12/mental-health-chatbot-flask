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
    
    // Cấu hình tiến trình cho mỗi state
    const progressConfig = {
        'greeting': {
            percentage: 0,
            label: 'Chào hỏi',
            includeInFlow: false
        },
        'collecting_issue': {
            percentage: 5,
            label: 'Thu thập thông tin',
            includeInFlow: true
        },
        'initial_screening': {
            percentage: 20,
            label: 'Sàng lọc ban đầu',
            includeInFlow: true,
            questionBased: true,
            totalQuestions: 10 // Số câu hỏi trong initial_screening
        },
        'detailed_assessment': {
            percentage: 50,
            label: 'Đánh giá chi tiết',
            includeInFlow: true,
            questionBased: true,
            assessmentMap: {
                'phq9': 9, // PHQ-9 có 9 câu hỏi + 1 câu phụ
                'gad7': 7, // GAD-7 có 7 câu hỏi + 1 câu phụ
                'dass21_stress': 7 // DASS-21 phần stress có 7 câu
            }
        },
        'additional_assessment': {
            percentage: 70,
            label: 'Đánh giá bổ sung',
            includeInFlow: true,
            questionBased: true
        },
        'suicide_assessment': {
            percentage: 85,
            label: 'Đánh giá nguy cơ',
            includeInFlow: true,
            questionBased: true,
            totalQuestions: 3 // Số câu hỏi trong suicide_assessment
        },
        'summary': {
            percentage: 90,
            label: 'Tóm tắt kết quả',
            includeInFlow: true
        },
        'resources': {
            percentage: 95,
            label: 'Tài nguyên hỗ trợ',
            includeInFlow: true
        },
        'disorder_info': {
            percentage: 98,
            label: 'Thông tin chi tiết',
            includeInFlow: true
        },
        'closing': {
            percentage: 100,
            label: 'Kết thúc',
            includeInFlow: true
        }
    };

    // Biến toàn cục để theo dõi tiến trình
    let currentProgress = {
        state: 'greeting',
        questionIndex: 0,
        totalQuestions: 0
    };
    
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
                    
                    // Cập nhật thanh tiến trình
                    if (data.chatState) {
                        updateProgressBar(data.chatState);
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
        } else {
            // Nếu đã tải lịch sử, cập nhật thanh tiến trình với state hiện tại
            updateProgressBar(loadChatStateFromLocalStorage());
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
                
                // Cập nhật thanh tiến trình
                if (data.chatState) {
                    updateProgressBar(data.chatState);
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
                
                // Cập nhật thanh tiến trình cho state mới
                if (data.chatState) {
                    updateProgressBar(data.chatState);
                }
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

    /**
     * Cập nhật thanh tiến trình
     */
    function updateProgressBar(chatState) {
        const progressFill = document.getElementById('roadmap-fill'); // Thay đổi ID thành 'roadmap-fill'
    
        // Kiểm tra tất cả các phần tử DOM trước khi sử dụng
        const assessmentPhase = document.getElementById('assessment-phase');
        const assessmentDetail = document.getElementById('assessment-detail');
        
        if (!chatState || !progressFill) return;
        
        // Lưu state trước đó để kiểm tra thay đổi
        const previousState = currentProgress.state;
        
        // Cập nhật state hiện tại
        currentProgress.state = chatState.state || 'greeting';
        
        // Reset và cập nhật chỉ số câu hỏi nếu state thay đổi
        if (previousState !== currentProgress.state) {
            currentProgress.questionIndex = 0;
            
            // Đặt tổng số câu hỏi dựa trên state hiện tại
            if (progressConfig[currentProgress.state] && progressConfig[currentProgress.state].questionBased) {
                if (progressConfig[currentProgress.state].assessmentMap && chatState.currentAssessment) {
                    currentProgress.totalQuestions = progressConfig[currentProgress.state].assessmentMap[chatState.currentAssessment] || 0;
                } else {
                    currentProgress.totalQuestions = progressConfig[currentProgress.state].totalQuestions || 0;
                }
            } else {
                currentProgress.totalQuestions = 0;
            }
        } else {
            // Cập nhật chỉ số câu hỏi nếu cùng state
            currentProgress.questionIndex = chatState.currentQuestionIndex || 0;
        }
        
        // Tính toán phần trăm tiến trình
        let percentage = progressConfig[currentProgress.state]?.percentage || 0;
        
        // Điều chỉnh phần trăm dựa trên tiến trình câu hỏi nếu là state dựa trên câu hỏi
        if (progressConfig[currentProgress.state]?.questionBased && currentProgress.totalQuestions > 0) {
            const basePercentage = progressConfig[currentProgress.state].percentage;
            const nextStatePercentage = getNextStatePercentage(currentProgress.state);
            const progressRange = nextStatePercentage - basePercentage;
            
            // Tính phần trăm dựa trên số câu hỏi đã hoàn thành
            const questionProgress = currentProgress.questionIndex / currentProgress.totalQuestions;
            percentage = basePercentage + (progressRange * questionProgress);
        }
        
        // Thêm hiệu ứng khi chuyển đổi state
        if (previousState !== currentProgress.state) {
            progressFill.classList.add('transitioning');
            setTimeout(() => {
                progressFill.classList.remove('transitioning');
            }, 1000);
        }
        
        // Cập nhật UI
        progressFill.style.width = `${percentage}%`;
        if (assessmentPhase) {
            assessmentPhase.textContent = progressConfig[currentProgress.state]?.label || 'Trò chuyện';
        }
        
        // Hiển thị thông tin câu hỏi nếu là state dựa trên câu hỏi (thêm kiểm tra null)
        const questionProgress = document.getElementById('question-progress');
        const progressValue = document.getElementById('progress-value');
        
        if (progressConfig[currentProgress.state]?.questionBased && currentProgress.totalQuestions > 0) {
            if (questionProgress) {
                questionProgress.textContent = `${currentProgress.questionIndex + 1}/${currentProgress.totalQuestions} câu hỏi`;
            }
            
            if (progressValue) {
                progressValue.style.width = `${(currentProgress.questionIndex / currentProgress.totalQuestions) * 100}%`;
            }
        }
    }

    /**
     * Hàm lấy phần trăm của state tiếp theo
     */
    function getNextStatePercentage(currentState) {
        const stateKeys = Object.keys(progressConfig);
        const currentIndex = stateKeys.indexOf(currentState);
        
        if (currentIndex !== -1 && currentIndex < stateKeys.length - 1) {
            return progressConfig[stateKeys[currentIndex + 1]].percentage;
        }
        
        return 100; // Nếu là state cuối cùng
    }

    // Thêm các hàm này vào global window object
    window.loadChatStateFromLocalStorage = loadChatStateFromLocalStorage;
    window.checkForWelcomeMessage = checkForWelcomeMessage;
    window.restartChat = restartChat;
    window.sendMessageToServer = sendMessageToServer;
});

/**
 * Quản lý tiến trình đánh giá nâng cao
 */
const ProgressManager = (function() {
    // Mapping của trạng thái đến các pha và thông tin chi tiết
    const stateMapping = {
        // Pha giới thiệu
        'greeting': {
            phase: 'intro',
            percentage: 10,
            title: 'Bắt đầu trò chuyện',
            subtitle: 'Chia sẻ cảm xúc của bạn với tôi',
            detailTitle: 'Giới thiệu',
            detailInfo: 'Chia sẻ với chúng tôi về cảm xúc và trải nghiệm của bạn gần đây.',
            icon: 'chat'
        },
        'collecting_issue': {
            phase: 'intro',
            percentage: 30,
            title: 'Thu thập thông tin',
            subtitle: 'Hiểu rõ hơn về trải nghiệm của bạn',
            detailTitle: 'Thu thập thông tin',
            detailInfo: 'Chúng tôi đang tìm hiểu về trạng thái hiện tại của bạn để chuẩn bị đánh giá.',
            icon: 'info'
        },
        
        // Pha sàng lọc
        'initial_screening': {
            phase: 'screening',
            percentage: 50,
            title: 'Sàng lọc sơ bộ',
            subtitle: 'Đánh giá nhanh các triệu chứng phổ biến',
            detailTitle: 'Sàng lọc ban đầu',
            detailInfo: 'Bước này giúp xác định các lĩnh vực cần đánh giá chi tiết hơn.',
            icon: 'search',
            questionBased: true
        },
        
        // Pha đánh giá chi tiết
        'detailed_assessment': {
            phase: 'detailed',
            percentage: 70,
            title: 'Đánh giá chuyên sâu',
            subtitle: 'Sử dụng bộ công cụ chuẩn',
            detailTitle: 'Đánh giá chi tiết',
            detailInfo: 'Sử dụng bộ câu hỏi được kiểm chứng để đánh giá chính xác hơn.',
            icon: 'clipboard',
            questionBased: true,
            assessmentMapping: {
                'phq9': { name: 'PHQ-9 (Trầm cảm)', icon: 'mood' },
                'gad7': { name: 'GAD-7 (Lo âu)', icon: 'heart' },
                'dass21_stress': { name: 'DASS-21 (Căng thẳng)', icon: 'alert' }
            }
        },
        'additional_assessment': {
            phase: 'detailed',
            percentage: 80,
            title: 'Đánh giá bổ sung',
            subtitle: 'Thu thập thông tin chi tiết hơn',
            detailTitle: 'Đánh giá bổ sung',
            detailInfo: 'Đánh giá sâu hơn về các triệu chứng được phát hiện.',
            icon: 'clipboard',
            questionBased: true
        },
        'suicide_assessment': {
            phase: 'detailed',
            percentage: 85,
            title: 'Đánh giá nguy cơ',
            subtitle: 'Đánh giá mức độ khẩn cấp',
            detailTitle: 'Đánh giá nguy cơ',
            detailInfo: 'Đánh giá mức độ ưu tiên và tính khẩn cấp của tình huống.',
            icon: 'alert',
            questionBased: true,
            priority: true
        },
        
        // Pha tổng kết
        'summary': {
            phase: 'review',
            percentage: 90,
            title: 'Tổng kết đánh giá',
            subtitle: 'Xem xét kết quả và đề xuất',
            detailTitle: 'Tổng kết kết quả',
            detailInfo: 'Chúng tôi đang tổng hợp kết quả và chuẩn bị các đề xuất phù hợp.',
            icon: 'results'
        },
        
        // Pha hỗ trợ
        'resources': {
            phase: 'support',
            percentage: 95,
            title: 'Tài nguyên hỗ trợ',
            subtitle: 'Cung cấp công cụ và thông tin',
            detailTitle: 'Tài nguyên hỗ trợ',
            detailInfo: 'Khám phá các tài nguyên và công cụ được thiết kế để hỗ trợ bạn.',
            icon: 'resources'
        },
        'disorder_info': {
            phase: 'support',
            percentage: 98,
            title: 'Thông tin chuyên sâu',
            subtitle: 'Tìm hiểu thêm về tình trạng',
            detailTitle: 'Thông tin chi tiết',
            detailInfo: 'Tìm hiểu thêm về các tình trạng và biện pháp quản lý có thể.',
            icon: 'info'
        },
        'closing': {
            phase: 'support',
            percentage: 100,
            title: 'Hoàn thành đánh giá',
            subtitle: 'Cảm ơn bạn đã tham gia',
            detailTitle: 'Kết thúc',
            detailInfo: 'Cảm ơn bạn đã hoàn thành quy trình đánh giá. Hãy xem xét các tài nguyên và đề xuất của chúng tôi.',
            icon: 'check'
        }
    };
    
    // Thứ tự các giai đoạn
    const phaseOrder = ['intro', 'screening', 'detailed', 'review', 'support'];
    
    // Cache các phần tử DOM
    let elements = {};
    
    // Lưu trạng thái hiện tại
    let currentState = {
        state: 'greeting',
        phase: 'intro',
        questionIndex: 0,
        totalQuestions: 0,
        previousPhase: null,
        assessmentType: null
    };
    
    // Các biểu tượng cho từng loại
    const icons = {
        'chat': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>',
        'info': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
        'search': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
        'clipboard': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>',
        'alert': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
        'results': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
        'resources': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>',
        'check': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
        'mood': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 15h8"></path><path d="M9 9h.01"></path><path d="M15 9h.01"></path></svg>',
        'heart': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>'
    };
    
    // Khởi tạo các tham chiếu phần tử DOM
    function initElements() {
        elements = {
            // Vòng phần trăm
            percentageIndicator: document.getElementById('percentage-indicator'),
            percentageText: document.getElementById('percentage-text'),
            
            // Thông tin trạng thái
            assessmentPhase: document.getElementById('assessment-phase'),
            assessmentDetail: document.getElementById('assessment-detail'),
            
            // Roadmap
            roadmapFill: document.getElementById('roadmap-fill'),
            checkpoints: document.querySelectorAll('.checkpoint-item'),
            
            // Chi tiết
            detailCard: document.getElementById('detail-card'),
            detailIcon: document.getElementById('detail-icon'),
            detailTitle: document.getElementById('detail-title'),
            questionProgress: document.getElementById('question-progress'),
            progressValue: document.getElementById('progress-value'),
            detailInfo: document.getElementById('detail-info')
        };
    }
    
    // Thiết lập các listener sự kiện
    function setupEventListeners() {
        // Hiệu ứng hover cho các checkpoint
        elements.checkpoints.forEach(checkpoint => {
            checkpoint.addEventListener('mouseenter', function() {
                if (!this.classList.contains('active') && !this.classList.contains('completed')) {
                    this.querySelector('.node-indicator').style.backgroundColor = 'rgba(var(--color-highlight), 0.1)';
                    this.querySelector('.node-icon').style.color = 'rgba(255, 255, 255, 0.8)';
                }
            });
            
            checkpoint.addEventListener('mouseleave', function() {
                if (!this.classList.contains('active') && !this.classList.contains('completed')) {
                    this.querySelector('.node-indicator').style.backgroundColor = 'rgb(43, 43, 43)';
                    this.querySelector('.node-icon').style.color = 'rgba(255, 255, 255, 0.5)';
                }
            });
        });
    }
    
    // Cập nhật UI dựa trên trạng thái
    function updateUI(chatState, animate = true) {
        if (!chatState || !chatState.state) return;
        
        // Lưu trạng thái trước để phát hiện thay đổi
        const previousPhase = currentState.phase;
        
        // Cập nhật trạng thái hiện tại
        const mapping = stateMapping[chatState.state];
        if (!mapping) return;
        
        currentState.state = chatState.state;
        currentState.phase = mapping.phase;
        currentState.questionIndex = chatState.currentQuestionIndex || 0;
        currentState.totalQuestions = chatState.totalQuestions || 0;
        
        if (chatState.currentAssessment && 
            mapping.assessmentMapping && 
            mapping.assessmentMapping[chatState.currentAssessment]) {
            currentState.assessmentType = chatState.currentAssessment;
        }
        
        // Cập nhật vòng phần trăm
        updatePercentageRing(mapping.percentage);
        
        // Cập nhật thông tin trạng thái
        elements.assessmentPhase.textContent = mapping.title;
        elements.assessmentDetail.textContent = mapping.subtitle;
        
        // Cập nhật roadmap
        updateRoadmap(mapping.phase, animate && previousPhase !== mapping.phase);
        
        // Cập nhật thẻ chi tiết
        updateDetailCard(chatState, mapping, animate);
    }
    
    // Cập nhật vòng phần trăm
    function updatePercentageRing(percentage) {
        const circumference = 2 * Math.PI * 15.9155;
        const dashoffset = ((100 - percentage) / 100) * circumference;
        
        // Đặt giá trị phần trăm
        elements.percentageText.textContent = `${Math.round(percentage)}%`;
        
        // Animation mượt cho vòng
        elements.percentageIndicator.style.transition = 'stroke-dasharray 0.8s ease-in-out';
        elements.percentageIndicator.setAttribute('stroke-dasharray', `${percentage}, 100`);
    }
    
    // Cập nhật thanh roadmap
    function updateRoadmap(currentPhase, animate) {
        const currentIndex = phaseOrder.indexOf(currentPhase);
        
        // Đặt chiều rộng cho thanh fill
        const percentage = (currentIndex / (phaseOrder.length - 1)) * 100;
        
        // Animation cho thanh tiến trình
        if (animate) {
            elements.roadmapFill.style.transition = 'width 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)';
        } else {
            elements.roadmapFill.style.transition = 'none';
        }
        elements.roadmapFill.style.width = `${percentage}%`;
        
        // Cập nhật trạng thái các checkpoint
        elements.checkpoints.forEach(checkpoint => {
            const phase = checkpoint.getAttribute('data-phase');
            const phaseIndex = phaseOrder.indexOf(phase);
            
            // Reset classes
            checkpoint.classList.remove('active', 'completed');
            
            // Đánh dấu các bước đã hoàn thành
            if (phaseIndex < currentIndex) {
                checkpoint.classList.add('completed');
            }
            // Đánh dấu bước hiện tại
            else if (phaseIndex === currentIndex) {
                checkpoint.classList.add('active');
                
                // Thêm hiệu ứng pulse nếu đang animate
                if (animate) {
                    const nodeIndicator = checkpoint.querySelector('.node-indicator');
                    nodeIndicator.classList.add('pulse-animation');
                    setTimeout(() => {
                        nodeIndicator.classList.remove('pulse-animation');
                    }, 2000);
                }
            }
        });
    }
    
    // Cập nhật thẻ chi tiết
    function updateDetailCard(chatState, mapping, animate) {
        // Tạo thông tin chi tiết về giai đoạn hiện tại
        let detailTitle = mapping.detailTitle;
        let detailInfo = mapping.detailInfo;
        let iconType = mapping.icon;
        
        // Hiệu chỉnh cho assessment cụ thể
        if (currentState.assessmentType && 
            mapping.assessmentMapping && 
            mapping.assessmentMapping[currentState.assessmentType]) {
                
            const assessmentInfo = mapping.assessmentMapping[currentState.assessmentType];
            detailTitle = assessmentInfo.name;
            iconType = assessmentInfo.icon || iconType;
        }
        
        // Thêm animation nếu yêu cầu
        if (animate) {
            elements.detailCard.classList.add('animate-fade-in');
            setTimeout(() => {
                elements.detailCard.classList.remove('animate-fade-in');
            }, 500);
        }
        
        // Cập nhật biểu tượng
        elements.detailIcon.innerHTML = icons[iconType] || icons['info'];
        
        // Đánh dấu các trạng thái ưu tiên cao
        if (mapping.priority) {
            elements.detailCard.style.borderColor = 'rgba(var(--color-highlight-secondary), 0.7)';
            elements.detailCard.style.boxShadow = '0 0 15px rgba(var(--color-highlight-secondary), 0.3)';
        } else {
            elements.detailCard.style.borderColor = 'rgba(var(--color-border), 0.7)';
            elements.detailCard.style.boxShadow = 'none';
        }
        
        // Cập nhật tiêu đề
        elements.detailTitle.textContent = detailTitle;
        
        // Cập nhật thông tin câu hỏi nếu là trạng thái dựa trên câu hỏi
        if (mapping.questionBased && currentState.totalQuestions > 0) {
            // Hiển thị thông tin câu hỏi
            elements.questionProgress.textContent = `${currentState.questionIndex + 1}/${currentState.totalQuestions} câu hỏi`;
            elements.questionProgress.parentElement.style.display = 'block';
            
            // Tính toán phần trăm hoàn thành
            const questionProgress = ((currentState.questionIndex + 1) / currentState.totalQuestions) * 100;
            elements.progressValue.style.width = `${questionProgress}%`;
        } else {
            // Ẩn thông tin câu hỏi
            elements.questionProgress.parentElement.style.display = 'none';
        }
        
        // Cập nhật thông tin chi tiết
        elements.detailInfo.textContent = detailInfo;
        
        // Thêm thông tin đánh giá nếu có
        if (chatState.scores && Object.keys(chatState.scores).length > 0) {
            let scoresHtml = '<div class="scores-summary" style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(var(--color-border), 0.5);">';
            scoresHtml += '<p style="font-weight: 500; margin-bottom: 0.5rem;">Kết quả đánh giá:</p>';
            scoresHtml += '<ul style="list-style: none; padding: 0; margin: 0;">';
            
            for (const [assessmentId, score] of Object.entries(chatState.scores)) {
                let assessmentName = assessmentId;
                if (assessmentId === 'phq9') assessmentName = 'PHQ-9 (Trầm cảm)';
                if (assessmentId === 'gad7') assessmentName = 'GAD-7 (Lo âu)';
                if (assessmentId === 'dass21_stress') assessmentName = 'DASS-21 (Căng thẳng)';
                
                let severity = '';
                if (chatState.severityLevels && chatState.severityLevels[assessmentId]) {
                    severity = chatState.severityLevels[assessmentId];
                    
                    // Chuyển đổi từ tiếng Anh sang tiếng Việt
                    if (severity === 'minimal') severity = 'Tối thiểu';
                    else if (severity === 'mild') severity = 'Nhẹ';
                    else if (severity === 'moderate') severity = 'Trung bình';
                    else if (severity === 'moderatelySevere') severity = 'Trung bình nặng';
                    else if (severity === 'severe') severity = 'Nặng';
                }
                
                scoresHtml += `<li style="margin-bottom: 0.25rem;"><span style="color: rgba(255,255,255,0.7);">${assessmentName}:</span> <strong>${score}</strong>${severity ? ` (${severity})` : ''}</li>`;
            }
            
            scoresHtml += '</ul></div>';
            
            if (mapping.phase === 'review' || mapping.phase === 'support') {
                elements.detailInfo.innerHTML += scoresHtml;
            }
        }
        
        // Kiểm tra cờ nguy cơ
        if (chatState.flags && chatState.flags.suicideRisk) {
            const warningEl = document.createElement('div');
            warningEl.className = 'warning-alert';
            warningEl.style.marginTop = '0.75rem';
            warningEl.style.padding = '0.5rem 0.75rem';
            warningEl.style.borderRadius = '4px';
            warningEl.style.backgroundColor = 'rgba(var(--color-highlight-secondary), 0.2)';
            warningEl.style.borderLeft = '3px solid rgb(var(--color-highlight-secondary))';
            
            warningEl.innerHTML = `
                <p style="margin: 0; font-weight: 500; color: rgb(var(--color-highlight-secondary));">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;">
                        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                    Cần hỗ trợ ngay lập tức
                </p>
            `;
            
            if (mapping.phase === 'review' || mapping.phase === 'support' || mapping.phase === 'detailed') {
                elements.detailInfo.appendChild(warningEl);
            }
        }
    }
    
    // Khởi tạo
    function init() {
        initElements();
        setupEventListeners();
    }
    
    // API công khai
    return {
        init: init,
        updateProgress: updateUI
    };
})();

// Khởi tạo khi trang đã tải
document.addEventListener('DOMContentLoaded', function() {
    // Khởi tạo quản lý tiến trình
    ProgressManager.init();
    initProgressDashboardToggle();
    
    // Thay thế các hàm cập nhật tiến trình trong các hàm chính của chat.js
    
    // Trong hàm checkForWelcomeMessage
    const originalCheckForWelcomeMessage = checkForWelcomeMessage;
    window.checkForWelcomeMessage = function() {
        const result = originalCheckForWelcomeMessage();
        
        // Cập nhật thanh tiến trình với trạng thái hiện tại
        ProgressManager.updateProgress(loadChatStateFromLocalStorage());
        
        return result;
    };
    
    // Thay thế trong sendMessageToServer
    const originalSendMessageToServer = sendMessageToServer;
    window.sendMessageToServer = function(message) {
        // Gọi hàm gốc
        originalSendMessageToServer(message);
        
        // Monitor fetch responses để cập nhật tiến trình
        const originalFetch = window.fetch;
        window.fetch = function() {
            return originalFetch.apply(this, arguments)
                .then(response => {
                    if (arguments[0].includes('/api/send_message')) {
                        response.clone().json().then(data => {
                            if (data.chatState) {
                                // Cập nhật tiến trình với animation
                                ProgressManager.updateProgress(data.chatState, true);
                            }
                        }).catch(() => {});
                    }
                    return response;
                });
        };
    };
    
    // Thay thế trong restartChat
    const originalRestartChat = restartChat;
    window.restartChat = function() {
        // Gọi hàm gốc
        originalRestartChat();
        
        // Monitor fetch response
        const originalFetch = window.fetch;
        window.fetch = function() {
            return originalFetch.apply(this, arguments)
                .then(response => {
                    if (arguments[0].includes('/api/restart')) {
                        response.clone().json().then(data => {
                            if (data.chatState) {
                                // Reset tiến trình không animation
                                ProgressManager.updateProgress(data.chatState, false);
                            }
                        }).catch(() => {});
                    }
                    return response;
                });
        };
    };
});

function initProgressDashboardToggle() {
    const toggleButton = document.getElementById('toggle-progress');
    const progressDashboard = document.querySelector('.progress-dashboard');
    
    // Exit if elements don't exist
    if (!toggleButton || !progressDashboard) return;
    
    // Initial state is collapsed
    let isExpanded = false;
    
    // Function to toggle dashboard visibility
    function toggleDashboard() {
        isExpanded = !isExpanded;
        
        if (isExpanded) {
            progressDashboard.classList.add('expanded');
            toggleButton.classList.add('expanded');
            toggleButton.setAttribute('title', 'Ẩn bảng tiến trình');
        } else {
            progressDashboard.classList.remove('expanded');
            toggleButton.classList.remove('expanded');
            toggleButton.setAttribute('title', 'Hiển thị bảng tiến trình');
        }
        
        // Store preference in localStorage
        localStorage.setItem('progressDashboardExpanded', isExpanded);
        
        // If expanded, scroll to make sure it's visible
        if (isExpanded) {
            setTimeout(() => {
                progressDashboard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        }
    }
    
    // Attach click event
    toggleButton.addEventListener('click', toggleDashboard);
    
    // Check if there's a saved preference
    const savedPreference = localStorage.getItem('progressDashboardExpanded');
    
    // Only auto-expand if explicitly saved as true
    if (savedPreference === 'true') {
        toggleDashboard();
    }
    
    // Modify the ProgressManager.updateProgress function to show dashboard on important updates
    if (window.ProgressManager && window.ProgressManager.updateProgress) {
        const originalUpdateProgress = window.ProgressManager.updateProgress;
        
        window.ProgressManager.updateProgress = function(chatState, animate) {
            // Call the original function
            originalUpdateProgress(chatState, animate);
            
            // Auto-expand on important state changes 
            if (chatState && chatState.state) {
                const importantStates = ['summary', 'suicide_assessment'];
                if (importantStates.includes(chatState.state) && !isExpanded) {
                    toggleDashboard();
                }
            }
        };
    }
}