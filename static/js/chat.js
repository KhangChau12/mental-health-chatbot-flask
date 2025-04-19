/**
 * Chat.js - Xử lý logic giao diện cho ứng dụng chatbot kết hợp chat tự nhiên và poll
 * Phiên bản cải tiến với giao diện poll và dashboard tiến trình
 */

document.addEventListener('DOMContentLoaded', function() {
    // Các element UI chính
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
    const pollContainer = document.getElementById('poll-container');
    const pollQuestion = document.getElementById('poll-question');
    const pollOptions = document.getElementById('poll-options');
    const pollProgress = document.getElementById('poll-progress');
    const pollDetailBtn = document.getElementById('poll-detail-button');
    const pollDetailInput = document.getElementById('poll-detail-input');
    const pollSubmitBtn = document.getElementById('poll-submit-button');
    
    // Các element dashboard tiến trình
    const progressDashboard = document.querySelector('.progress-dashboard');
    const progressToggleBtn = document.getElementById('toggle-progress');
    const roadmapFill = document.getElementById('roadmap-fill');
    const percentageIndicator = document.getElementById('percentage-indicator');
    const percentageText = document.getElementById('percentage-text');
    const assessmentPhase = document.getElementById('assessment-phase');
    const assessmentDetail = document.getElementById('assessment-detail');
    const questionProgress = document.getElementById('question-progress');
    const progressValueBar = document.getElementById('progress-value');
    const detailInfo = document.getElementById('detail-info');
    const detailTitle = document.getElementById('detail-title');
    const detailIcon = document.getElementById('detail-icon');
    const checkpointItems = document.querySelectorAll('.checkpoint-item');
    
    // Templates
    const userMessageTemplate = document.getElementById('user-message-template');
    const botMessageTemplate = document.getElementById('bot-message-template');
    const errorMessageTemplate = document.getElementById('error-message-template');
    
    // Biến trạng thái
    let isLoading = false;
    let useAI = true;
    let interfaceMode = 'chat';  // 'chat' hoặc 'poll'
    let currentPollOptions = [];
    let isDashboardExpanded = false;
    
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
                        
                        // Cập nhật chế độ giao diện
                        updateInterfaceMode(data.chatState.interfaceMode || 'chat');
                    }
                    
                    // Cập nhật hiển thị assessment
                    if (data.chatState && data.chatState.state) {
                        updateCurrentAssessment(data.chatState.state);
                    }
                    
                    // Cập nhật thanh tiến trình
                    if (data.chatState) {
                        updateProgressDashboard(data.chatState);
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
            // Nếu đã tải lịch sử, cập nhật thanh tiến trình và chế độ giao diện với state hiện tại
            const savedState = loadChatStateFromLocalStorage();
            if (savedState) {
                updateProgressDashboard(savedState);
                updateInterfaceMode(savedState.interfaceMode || 'chat');
            }
        }
    }
    
    // Hiển thị ngay khi trang tải
    checkForWelcomeMessage();
    
    // Sự kiện
    userInput.addEventListener('input', handleInputChange);
    userInput.addEventListener('keydown', handleKeyDown);
    chatForm.addEventListener('submit', handleSubmit);
    restartButton.addEventListener('click', restartChat);
    toggleInfoButton.addEventListener('click', toggleInfoSidebar);
    closeInfoButton.addEventListener('click', toggleInfoSidebar);
    
    // Xử lý sự kiện cho dashboard tiến trình
    if (progressToggleBtn) {
        progressToggleBtn.addEventListener('click', toggleProgressDashboard);
    }
    
    // Sự kiện cho giao diện poll nếu có
    if (pollDetailBtn) {
        pollDetailBtn.addEventListener('click', togglePollDetailInput);
    }
    if (pollSubmitBtn) {
        pollSubmitBtn.addEventListener('click', submitPollResponse);
    }
    
    /**
     * Cập nhật chế độ giao diện (chat/poll)
     */
    function updateInterfaceMode(mode) {
        interfaceMode = mode;
        
        // Cập nhật hiển thị UI
        if (mode === 'poll') {
            // Hiển thị giao diện poll, ẩn chat input
            if (pollContainer) pollContainer.classList.remove('hidden');
            if (chatForm) chatForm.classList.add('hidden');
        } else {
            // Hiển thị giao diện chat, ẩn poll
            if (pollContainer) pollContainer.classList.add('hidden');
            if (chatForm) chatForm.classList.remove('hidden');
        }
    }
    
    /**
     * Cập nhật nội dung poll
     */
    function updatePollContent(question, options, progress) {
        if (!pollContainer || !pollQuestion || !pollOptions) return;
        
        // Lưu tùy chọn hiện tại
        currentPollOptions = options || [];
        
        // Cập nhật nội dung câu hỏi
        pollQuestion.textContent = question || '';
        
        // Xóa các tùy chọn cũ
        pollOptions.innerHTML = '';
        
        // Thêm các tùy chọn mới
        if (options && options.length > 0) {
            options.forEach((option, index) => {
                const optionBtn = document.createElement('button');
                optionBtn.className = 'poll-option-button';
                optionBtn.textContent = option;
                optionBtn.setAttribute('data-index', index);
                optionBtn.addEventListener('click', function() {
                    selectPollOption(index);
                });
                pollOptions.appendChild(optionBtn);
            });
        }
        
        // Cập nhật thanh tiến trình nếu có
        if (pollProgress && progress) {
            const { current, total } = progress;
            pollProgress.textContent = `Câu hỏi ${current}/${total}`;
            
            // Cập nhật thanh tiến trình nếu sử dụng
            const progressBar = document.getElementById('poll-progress-bar');
            if (progressBar) {
                const percentage = (current / total) * 100;
                progressBar.style.width = `${percentage}%`;
            }
        }
    }
    
    /**
     * Xử lý khi người dùng chọn tùy chọn trong poll
     */
    function selectPollOption(index) {
        // Loại bỏ lớp active từ tất cả các nút
        const optionButtons = pollOptions.querySelectorAll('.poll-option-button');
        optionButtons.forEach(btn => btn.classList.remove('active'));
        
        // Thêm lớp active cho nút được chọn
        const selectedButton = pollOptions.querySelector(`[data-index="${index}"]`);
        if (selectedButton) {
            selectedButton.classList.add('active');
        }
        
        // Hiển thị nút submit
        if (pollSubmitBtn) {
            pollSubmitBtn.classList.remove('hidden');
        }
    }
    
    /**
     * Hiện/ẩn input chi tiết trong poll
     */
    function togglePollDetailInput() {
        if (!pollDetailInput) return;
        
        if (pollDetailInput.classList.contains('hidden')) {
            pollDetailInput.classList.remove('hidden');
            pollDetailBtn.textContent = 'Ẩn chi tiết';
        } else {
            pollDetailInput.classList.add('hidden');
            pollDetailBtn.textContent = 'Thêm chi tiết';
        }
    }
    
    /**
     * Gửi phản hồi từ poll
     */
    function submitPollResponse() {
        // Lấy index của tùy chọn được chọn
        const selectedOption = pollOptions.querySelector('.poll-option-button.active');
        if (!selectedOption) {
            alert('Vui lòng chọn một tùy chọn');
            return;
        }
        
        const optionIndex = selectedOption.getAttribute('data-index');
        let response = optionIndex;
        
        // Thêm chi tiết nếu có
        if (pollDetailInput && !pollDetailInput.classList.contains('hidden') && pollDetailInput.value.trim()) {
            response += ` - ${pollDetailInput.value.trim()}`;
        }
        
        // Hiển thị tin nhắn người dùng
        const selectedText = currentPollOptions[optionIndex];
        const displayMessage = selectedText + (pollDetailInput && pollDetailInput.value.trim() ? ` (${pollDetailInput.value.trim()})` : '');
        
        // Hiển thị tin nhắn người dùng
        const messageId = 'msg-' + Date.now();
        const timestamp = getCurrentTime();
        
        // Thêm tin nhắn vào UI
        addMessageToUI(displayMessage, 'user', messageId, timestamp);
        
        // Thêm tin nhắn vào localStorage
        const messages = loadMessagesFromLocalStorage();
        messages.push({
            role: 'user',
            content: displayMessage,
            id: messageId,
            timestamp: timestamp
        });
        saveMessagesToLocalStorage(messages);
        
        // Reset poll UI
        pollOptions.querySelectorAll('.poll-option-button').forEach(btn => {
            btn.classList.remove('active');
        });
        if (pollDetailInput) {
            pollDetailInput.value = '';
            pollDetailInput.classList.add('hidden');
        }
        if (pollDetailBtn) {
            pollDetailBtn.textContent = 'Thêm chi tiết';
        }
        if (pollSubmitBtn) {
            pollSubmitBtn.classList.add('hidden');
        }
        
        // Hiển thị hiệu ứng đang nhập
        showTypingIndicator();
        
        // Gửi phản hồi poll đến server
        sendPollResponseToServer(response);
    }
    
    /**
     * Gửi phản hồi poll đến server
     */
    function sendPollResponseToServer(response) {
        isLoading = true;
        updateChatModeIndicator();
        
        // Lấy lịch sử chat từ localStorage
        const messages = loadMessagesFromLocalStorage();
        
        // Gửi nhiều hơn nhưng không gửi tất cả để tránh quá tải
        const maxMessages = 40; // Tăng từ 15 lên 40
        const recentMessages = messages.length <= maxMessages ? 
                            messages : 
                            messages.slice(-maxMessages);
        
        // Lấy trạng thái chat từ localStorage
        const chatState = loadChatStateFromLocalStorage();
        
        fetch('/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: response,
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
            
            // Xử lý phản hồi của server
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
                
                // Cập nhật trạng thái đánh giá hiện tại
                if (data.state) {
                    updateCurrentAssessment(data.state);
                }
                
                // Cập nhật thanh tiến trình
                if (data.chatState) {
                    updateProgressDashboard(data.chatState);
                }
                
                // Cập nhật chế độ giao diện
                if (data.chatState && data.chatState.interfaceMode) {
                    updateInterfaceMode(data.chatState.interfaceMode);
                }
                
                // Cập nhật nội dung poll nếu cần
                if (data.pollOptions && interfaceMode === 'poll') {
                    updatePollContent(
                        data.botMessage, 
                        data.pollOptions, 
                        {
                            current: (data.chatState?.currentQuestionIndex || 0) + 1,
                            total: data.chatState?.totalQuestions || 10
                        }
                    );
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
        
        // Gửi nhiều hơn nhưng không gửi tất cả để tránh quá tải
        const maxMessages = 40; // Tăng từ 15 lên 40
        const recentMessages = messages.length <= maxMessages ? 
                              messages : 
                              messages.slice(-maxMessages);
        
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
                
                // Cập nhật trạng thái đánh giá hiện tại
                if (data.state) {
                    updateCurrentAssessment(data.state);
                }
                
                // Cập nhật thanh tiến trình
                if (data.chatState) {
                    updateProgressDashboard(data.chatState);
                }
                
                // Cập nhật chế độ giao diện
                if (data.chatState && data.chatState.interfaceMode) {
                    updateInterfaceMode(data.chatState.interfaceMode);
                }
                
                // Cập nhật nội dung poll nếu cần
                if (data.pollOptions && interfaceMode === 'poll') {
                    updatePollContent(
                        data.botMessage, 
                        data.pollOptions, 
                        {
                            current: (data.chatState?.currentQuestionIndex || 0) + 1,
                            total: data.chatState?.totalQuestions || 10
                        }
                    );
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
                updateCurrentAssessment('greeting');
                
                // Cập nhật thanh tiến trình cho state mới
                if (data.chatState) {
                    updateProgressDashboard(data.chatState);
                }
                
                // Cập nhật chế độ giao diện
                updateInterfaceMode('chat');
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
     * Xử lý hiện/ẩn dashboard tiến trình
     */
    function toggleProgressDashboard() {
        isDashboardExpanded = !isDashboardExpanded;
        
        if (progressDashboard) {
            progressDashboard.classList.toggle('expanded', isDashboardExpanded);
        }
        
        if (progressToggleBtn) {
            progressToggleBtn.classList.toggle('expanded', isDashboardExpanded);
        }
    }
    
    /**
     * Cập nhật dashboard tiến trình
     */
    function updateProgressDashboard(chatState) {
        if (!progressDashboard || !roadmapFill || !percentageIndicator || !percentageText) return;
        
        // Xác định trạng thái hiện tại
        const state = chatState.state || 'greeting';
        const assessmentId = chatState.currentAssessment;
        const questionIndex = chatState.currentQuestionIndex || 0;
        const totalQuestions = chatState.totalQuestions || 0;
        
        // Cập nhật tiêu đề và mô tả
        updateAssessmentInfo(state, assessmentId, chatState);
        
        // Cập nhật tiến trình câu hỏi
        updateQuestionProgress(questionIndex, totalQuestions);
        
        // Cập nhật tiến trình tổng thể
        const overallProgress = calculateOverallProgress(state, questionIndex, totalQuestions);
        updateOverallProgressIndicator(overallProgress);
        
        // Cập nhật roadmap
        updateRoadmapPhase(state);
    }

    /**
     * Cập nhật thông tin đánh giá hiện tại
     */
    function updateAssessmentInfo(state, assessmentId, chatState) {
        if (!assessmentPhase || !assessmentDetail || !detailTitle || !detailIcon || !detailInfo) return;
        
        // Thông tin mặc định
        let title = "Bắt đầu trò chuyện";
        let detail = "Chúng tôi sẽ hỗ trợ bạn";
        let detailText = "Hệ thống đang xử lý thông tin của bạn...";
        
        // Lấy thông tin câu hỏi từ chatState
        const currentQuestionIndex = chatState.currentQuestionIndex || 0;
        const totalQuestions = chatState.totalQuestions || 0;
        
        // Cập nhật thông tin dựa trên trạng thái
        switch (state) {
            case 'greeting':
                title = "Bắt đầu trò chuyện";
                detail = "Chào mừng bạn đến với Trợ lý Sức khỏe Tâm thần";
                detailText = "Hãy chia sẻ lý do bạn tìm đến dịch vụ này.";
                break;
                
            case 'collecting_issue':
                title = "Thu thập thông tin";
                detail = "Chia sẻ vấn đề của bạn";
                detailText = "Hãy chia sẻ những gì bạn đang trải qua để chúng tôi có thể hiểu rõ hơn.";
                break;
                
            case 'natural_conversation':
                title = "Trò chuyện tự nhiên";
                detail = "Đánh giá sơ bộ";
                detailText = "Chúng tôi đang tìm hiểu về trải nghiệm của bạn thông qua cuộc trò chuyện tự nhiên.";
                break;
                
            case 'poll_interaction':
            case 'initial_screening':
            case 'detailed_assessment':
            case 'additional_assessment':
                if (assessmentId && chatState.assessmentDetails) {
                    title = chatState.assessmentDetails.name || "Đánh giá";
                    detail = chatState.assessmentDetails.description || "Trả lời các câu hỏi đánh giá";
                }
                detailText = `Đang thực hiện đánh giá ${currentQuestionIndex + 1}/${totalQuestions || 10} câu hỏi.`;
                break;
                
            case 'suicide_assessment':
                title = "Đánh giá nguy cơ";
                detail = "Câu hỏi quan trọng";
                detailText = "Chúng tôi đang đánh giá mức độ nghiêm trọng để có thể hỗ trợ bạn tốt nhất.";
                break;
                
            case 'summary':
                title = "Tổng kết kết quả";
                detail = "Tóm tắt đánh giá";
                detailText = "Chúng tôi đang tổng hợp kết quả từ các đánh giá đã thực hiện.";
                break;
                
            case 'resources':
                title = "Tài nguyên hỗ trợ";
                detail = "Các nguồn tham khảo";
                detailText = "Chúng tôi đang cung cấp các tài nguyên phù hợp với nhu cầu của bạn.";
                break;
                
            case 'disorder_info':
                title = "Thông tin chi tiết";
                detail = "Hiểu rõ hơn về tình trạng";
                detailText = "Chúng tôi đang cung cấp thông tin chi tiết về các triệu chứng bạn đang trải qua.";
                break;
                
            case 'closing':
                title = "Kết thúc cuộc trò chuyện";
                detail = "Cảm ơn bạn đã trò chuyện";
                detailText = "Cảm ơn bạn đã sử dụng Trợ lý Sức khỏe Tâm thần. Bạn có thể quay lại bất cứ lúc nào.";
                break;
                
            default:
                title = "Đang xử lý";
                detail = "Xin vui lòng đợi";
                detailText = "Hệ thống đang xử lý thông tin...";
        }
        
        // Cập nhật UI
        assessmentPhase.textContent = title;
        assessmentDetail.textContent = detail;
        detailTitle.textContent = title;
        detailInfo.textContent = detailText;
    }

    /**
     * Cập nhật tiến trình câu hỏi
     */
    function updateQuestionProgress(currentIndex, totalQuestions) {
        if (!questionProgress || !progressValueBar) return;
        
        // Nếu không có tổng số câu hỏi, không hiển thị
        if (!totalQuestions) {
            questionProgress.textContent = "Đang trò chuyện";
            progressValueBar.style.width = "0%";
            return;
        }
        
        // Cập nhật text và thanh tiến trình
        questionProgress.textContent = `${currentIndex + 1}/${totalQuestions} câu hỏi`;
        
        const progressPercent = ((currentIndex + 1) / totalQuestions) * 100;
        progressValueBar.style.width = `${progressPercent}%`;
    }

    /**
     * Tính toán tiến trình tổng thể
     */
    function calculateOverallProgress(state, currentQuestionIndex, totalQuestions) {
        // Xác định trọng số của mỗi giai đoạn
        const phaseWeights = {
            'greeting': 0,
            'collecting_issue': 5,
            'natural_conversation': 15,
            'poll_interaction': 40,
            'initial_screening': 40,
            'detailed_assessment': 50,
            'additional_assessment': 60,
            'suicide_assessment': 70,
            'summary': 80,
            'resources': 90,
            'disorder_info': 95,
            'closing': 100
        };
        
        // Lấy tiến trình cơ bản dựa trên trạng thái
        let baseProgress = phaseWeights[state] || 0;
        
        // Nếu đang trong giai đoạn câu hỏi, thêm tiến trình dựa trên chỉ số câu hỏi
        if (['poll_interaction', 'initial_screening', 'detailed_assessment', 'additional_assessment', 'suicide_assessment'].includes(state)) {
            if (totalQuestions > 0) {
                // Tính tiến trình trong giai đoạn hiện tại
                const phaseProgress = phaseWeights[state];
                const nextPhaseProgress = state === 'suicide_assessment' ? 80 : 70;
                const progressRange = nextPhaseProgress - phaseProgress;
                
                // Thêm tiến trình dựa trên số câu hỏi đã trả lời
                const questionProgress = (currentQuestionIndex / totalQuestions) * progressRange;
                baseProgress += questionProgress;
            }
        }
        
        return Math.min(Math.round(baseProgress), 100);
    }

    /**
     * Cập nhật hiển thị tiến trình tổng thể
     */
    function updateOverallProgressIndicator(progressPercent) {
        if (!percentageIndicator || !percentageText) return;
        
        // Cập nhật text và hiệu ứng
        percentageText.textContent = `${progressPercent}%`;
        
        // Cập nhật đường tròn tiến trình
        const circumference = 2 * Math.PI * 15.9155; // Dựa trên giá trị trong SVG
        const dashOffset = circumference - (progressPercent / 100) * circumference;
        percentageIndicator.style.strokeDasharray = `${progressPercent}, 100`;
    }

    /**
     * Cập nhật giai đoạn trong roadmap
     */
    function updateRoadmapPhase(state) {
        if (!checkpointItems || !roadmapFill) return;
        
        // Mapping các trạng thái vào các giai đoạn trong roadmap
        const phaseMapping = {
            'greeting': 'intro',
            'collecting_issue': 'intro',
            'natural_conversation': 'screening',
            'poll_interaction': 'detailed',
            'initial_screening': 'screening',
            'detailed_assessment': 'detailed',
            'additional_assessment': 'detailed',
            'suicide_assessment': 'detailed',
            'summary': 'review',
            'resources': 'support',
            'disorder_info': 'support',
            'closing': 'support'
        };
        
        // Xác định phase hiện tại
        const currentPhase = phaseMapping[state] || 'intro';
        
        // Mapping phases to percentage for roadmap-fill
        const phaseProgressMapping = {
            'intro': 0,
            'screening': 25,
            'detailed': 50,
            'review': 75,
            'support': 100
        };
        
        // Cập nhật roadmap fill
        const fillPercent = phaseProgressMapping[currentPhase] || 0;
        roadmapFill.style.width = `${fillPercent}%`;
        
        // Cập nhật trạng thái của các checkpoint
        checkpointItems.forEach(item => {
            const phase = item.getAttribute('data-phase');
            if (!phase) return;
            
            // Xóa tất cả các trạng thái hiện tại
            item.classList.remove('active', 'completed');
            
            // Xác định trạng thái mới
            if (phase === currentPhase) {
                item.classList.add('active');
            } else if (phaseProgressMapping[phase] < phaseProgressMapping[currentPhase]) {
                item.classList.add('completed');
            }
        });
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
        
        const retryButton = errorElement.querySelector('#retry-button');
        retryButton.textContent = "Chuyển sang phiên bản Poll";
        retryButton.addEventListener('click', function() {
            // Chuyển hướng sang phiên bản poll
            window.location.href = '/logic';
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
        } else if (state === 'poll_interaction') {
            assessmentName = 'Đánh giá chuyên sâu';
        } else if (state === 'natural_conversation') {
            assessmentName = 'Trò chuyện đánh giá';
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

    function switchToPollMode() {
        chatMessages.classList.add('hidden');
        pollContainer.classList.remove('hidden');
        chatInputContainer.classList.add('hidden');
    }
    
    function switchToChatMode() {
        chatMessages.classList.remove('hidden');
        pollContainer.classList.add('hidden');
        chatInputContainer.classList.remove('hidden');
    }
});