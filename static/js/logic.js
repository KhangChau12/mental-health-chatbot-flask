/**
 * Logic.js - Xử lý logic giao diện cho ứng dụng khảo sát thuần túy (poll-only)
 * Phiên bản tách biệt với chat.js để tập trung vào trải nghiệm poll
 */

document.addEventListener('DOMContentLoaded', function() {
    // Các element UI chính
    const viewResourcesButton = document.getElementById('view-resources-button');
    const welcomeContainer = document.getElementById('welcome-container');
    const pollContainer = document.getElementById('poll-container');
    const resultsContainer = document.getElementById('results-container');
    const resourcesContainer = document.getElementById('resources-container');
    const pollQuestion = document.getElementById('poll-question');
    const pollOptions = document.getElementById('poll-options');
    const pollProgress = document.getElementById('poll-progress');
    const pollProgressBar = document.getElementById('poll-progress-bar');
    const pollDetailBtn = document.getElementById('poll-detail-button');
    const pollDetailInput = document.getElementById('poll-detail-input');
    const pollSubmitBtn = document.getElementById('poll-submit-button');
    const resultsContent = document.getElementById('results-content');
    const resourcesContent = document.getElementById('resources-content');
    const restartButton = document.getElementById('restart-poll');
    const toggleInfoButton = document.getElementById('toggle-info');
    const closeInfoButton = document.getElementById('close-info');
    const infoSidebar = document.getElementById('info-sidebar');
    const currentAssessment = document.getElementById('current-assessment');
    const startAssessmentBtn = document.getElementById('start-assessment');
    const viewResourcesBtn = document.getElementById('view-resources-button');
    const restartSurveyBtn = document.getElementById('restart-survey-button');
    const doneBtn = document.getElementById('done-button');
    
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
    
    // Template cho lỗi
    const errorMessageTemplate = document.getElementById('error-message-template');
    
    // Biến trạng thái
    let isLoading = false;
    let currentPollOptions = [];
    let isDashboardExpanded = false;
    let currentAssessmentState = null;
    let pollHistory = [];
    
    // Event listeners
    if (startAssessmentBtn) {
        startAssessmentBtn.addEventListener('click', startAssessment);
    }
    
    if (pollDetailBtn) {
        pollDetailBtn.addEventListener('click', togglePollDetailInput);
    }
    
    if (pollSubmitBtn) {
        pollSubmitBtn.addEventListener('click', submitPollResponse);
    }
    
    if (viewResourcesBtn) {
        viewResourcesBtn.addEventListener('click', showResources);
    }
    
    if (restartSurveyBtn) {
        restartSurveyBtn.addEventListener('click', restartSurvey);
    }
    
    if (doneBtn) {
        doneBtn.addEventListener('click', completeSurvey);
    }
    
    if (restartButton) {
        restartButton.addEventListener('click', confirmRestartSurvey);
    }
    
    if (toggleInfoButton) {
        toggleInfoButton.addEventListener('click', toggleInfoSidebar);
    }
    
    if (closeInfoButton) {
        closeInfoButton.addEventListener('click', toggleInfoSidebar);
    }
    
    if (progressToggleBtn) {
        progressToggleBtn.addEventListener('click', toggleProgressDashboard);
    }
    
    /**
     * Bắt đầu khảo sát khi người dùng nhấn nút bắt đầu
     */
    function startAssessment() {
        if (isLoading) return;
        
        isLoading = true;
        
        // Gọi API để bắt đầu khảo sát
        fetch('/api/poll_flow', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'start'
            })
        })
        .then(response => response.json())
        .then(data => {
            isLoading = false;
            
            if (data.error) {
                showErrorMessage(data.error);
                return;
            }
            
            // Cập nhật currentAssessmentState
            currentAssessmentState = data.chatState;
            
            // Ẩn welcomeContainer, hiển thị pollContainer
            welcomeContainer.classList.add('hidden');
            pollContainer.classList.remove('hidden');
            
            // Cập nhật nội dung poll
            updatePollContent(
                data.question,
                data.options,
                {
                    current: (data.chatState?.currentQuestionIndex || 0) + 1,
                    total: data.chatState?.totalQuestions || 10
                }
            );
            
            // Cập nhật dashboard
            updateProgressDashboard(data.chatState);
            
            // Cập nhật tên assessment hiện tại
            updateCurrentAssessment(data.chatState.state);
        })
        .catch(error => {
            isLoading = false;
            console.error('Error starting assessment:', error);
            showErrorMessage("Không thể bắt đầu khảo sát. Vui lòng thử lại sau.");
        });
    }
    
    /**
     * Xử lý khi người dùng hiện/ẩn input chi tiết
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
            pollProgress.textContent = `${current}/${total}`;
            
            // Cập nhật thanh tiến trình
            if (pollProgressBar) {
                const percentage = (current / total) * 100;
                pollProgressBar.style.width = `${percentage}%`;
            }
        }
    }
    
    /**
     * Xử lý khi người dùng chọn tùy chọn
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
     * Gửi phản hồi từ poll
     */
    function submitPollResponse() {
        if (isLoading) return;
        
        // Lấy index của tùy chọn được chọn
        const selectedOption = pollOptions.querySelector('.poll-option-button.active');
        if (!selectedOption) {
            alert('Vui lòng chọn một tùy chọn');
            return;
        }
        
        const optionIndex = selectedOption.getAttribute('data-index');
        let response = optionIndex;
        
        // Thêm chi tiết nếu có
        const detailText = pollDetailInput && !pollDetailInput.classList.contains('hidden') ? 
                        pollDetailInput.value.trim() : '';
        
        // Lưu lại câu trả lời và chi tiết vào lịch sử
        pollHistory.push({
            question: pollQuestion.textContent,
            selectedOption: currentPollOptions[optionIndex],
            details: detailText,
            timestamp: new Date().toISOString()
        });
        
        // Đánh dấu đang tải
        isLoading = true;
        
        // Gọi API để gửi phản hồi
        fetch('/api/poll_flow', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'submit',
                response: response,
                details: detailText,
                chatState: currentAssessmentState
            })
        })
        .then(response => response.json())
        .then(data => {
            isLoading = false;
            
            if (data.error) {
                showErrorMessage(data.error);
                return;
            }
            
            // Cập nhật currentAssessmentState
            currentAssessmentState = data.chatState;
            
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
            
            // Xử lý trạng thái tiếp theo
            handleNextState(data);
        })
        .catch(error => {
            isLoading = false;
            console.error('Error submitting response:', error);
            showErrorMessage("Không thể gửi phản hồi. Vui lòng thử lại sau.");
        });
    }
    
    /**
     * Xử lý trạng thái tiếp theo dựa trên phản hồi từ server
     */
    function handleNextState(data) {
        // Cập nhật dashboard
        updateProgressDashboard(data.chatState);
        
        // Cập nhật tên assessment hiện tại
        if (data.chatState && data.chatState.state) {
            updateCurrentAssessment(data.chatState.state);
        }
        
        // Kiểm tra trạng thái results_preview
        if (data.chatState && data.chatState.state === 'results_preview') {
            // Ẩn pollContainer, hiển thị previewContainer
            pollContainer.classList.add('hidden');
            resultsContainer.classList.remove('hidden');
            
            // Cập nhật nội dung preview với HTML và biểu đồ
            if (resultsContent) {
                resultsContent.innerHTML = data.previewHtml || '';
                
                // Nếu có dữ liệu biểu đồ, khởi tạo biểu đồ
                if (data.chartData) {
                    // Thêm code để vẽ biểu đồ nếu cần
                }
            }
            
            // Hiển thị nút tiếp tục đặc biệt
            if (viewResourcesButton) {
                viewResourcesButton.textContent = "Tiếp tục với đánh giá chi tiết";
            }
            
            return;
        }
        
        // Kiểm tra xem có phải chuyển sang màn hình kết quả không
        if (data.showResults) {
            // Ẩn pollContainer, hiển thị resultsContainer
            pollContainer.classList.add('hidden');
            resultsContainer.classList.remove('hidden');
            
            // Cập nhật nội dung kết quả
            if (resultsContent) {
                resultsContent.innerHTML = data.resultsHtml || '';
            }
            
            // Đổi tên nút
            if (viewResourcesButton) {
                viewResourcesButton.textContent = "Xem Tài Nguyên Hỗ Trợ";
            }
            
            return;
        }
        
        // Kiểm tra xem có phải chuyển sang trang tài nguyên không
        if (data.showResources) {
            // Ẩn pollContainer/resultsContainer, hiển thị resourcesContainer
            pollContainer.classList.add('hidden');
            resultsContainer.classList.add('hidden');
            resourcesContainer.classList.remove('hidden');
            
            // Cập nhật nội dung tài nguyên
            if (resourcesContent) {
                resourcesContent.innerHTML = data.resourcesHtml || '';
            }
            
            return;
        }
        
        // Tiếp tục với câu hỏi tiếp theo nếu có
        if (data.question && data.options) {
            updatePollContent(
                data.question,
                data.options,
                {
                    current: (data.chatState?.currentQuestionIndex || 0) + 1,
                    total: data.chatState?.totalQuestions || 10
                }
            );
        }
    }
    
    /**
     * Hiển thị trang tài nguyên
     */
    function showResources() {
        if (isLoading) return;
        
        isLoading = true;
        
        // Kiểm tra trạng thái hiện tại
        const currentState = currentAssessmentState?.state || '';
        
        // Có API endpoint khác nhau cho mỗi trạng thái
        let apiEndpoint = '/api/poll_flow';
        let requestBody = {
            action: 'resources',
            chatState: currentAssessmentState
        };
        
        // Nếu đang ở trạng thái preview, gửi response tiếp tục
        if (currentState === 'results_preview') {
            requestBody = {
                action: 'submit',
                response: 'continue',
                details: '',
                chatState: currentAssessmentState
            };
        }
        
        fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        })
        .then(response => response.json())
        .then(data => {
            isLoading = false;
            
            if (data.error) {
                showErrorMessage(data.error);
                return;
            }
            
            // Cập nhật currentAssessmentState
            currentAssessmentState = data.chatState;
            
            // Kiểm tra xem đang chuyển từ preview sang assessment
            if (currentState === 'results_preview' && data.question) {
                // Ẩn resultsContainer, hiển thị pollContainer
                resultsContainer.classList.add('hidden');
                pollContainer.classList.remove('hidden');
                
                // Cập nhật nội dung poll
                updatePollContent(
                    data.question,
                    data.options,
                    {
                        current: (data.chatState?.currentQuestionIndex || 0) + 1,
                        total: data.chatState?.totalQuestions || 10
                    }
                );
            } else if (data.showResources) {
                // Ẩn resultsContainer, hiển thị resourcesContainer
                resultsContainer.classList.add('hidden');
                resourcesContainer.classList.remove('hidden');
                
                // Cập nhật nội dung tài nguyên
                if (resourcesContent) {
                    resourcesContent.innerHTML = data.resourcesHtml || '';
                }
            }
            
            // Cập nhật dashboard
            updateProgressDashboard(data.chatState);
        })
        .catch(error => {
            isLoading = false;
            console.error('Error fetching resources:', error);
            showErrorMessage("Không thể tải tài nguyên. Vui lòng thử lại sau.");
        });
    }
    
    /**
     * Khởi động lại khảo sát
     */
    function restartSurvey() {
        if (isLoading) return;
        
        confirmRestartSurvey();
    }
    
    /**
     * Xác nhận khởi động lại khảo sát
     */
    function confirmRestartSurvey() {
        if (isLoading) return;
        
        // Xác nhận từ người dùng
        if (!confirm("Bạn có chắc chắn muốn bắt đầu lại khảo sát? Tất cả dữ liệu sẽ bị xóa.")) {
            return;
        }
        
        isLoading = true;
        
        fetch('/api/poll_flow', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'restart'
            })
        })
        .then(response => response.json())
        .then(data => {
            isLoading = false;
            
            if (data.error) {
                showErrorMessage(data.error);
                return;
            }
            
            // Reset lịch sử
            pollHistory = [];
            
            // Cập nhật currentAssessmentState
            currentAssessmentState = data.chatState;
            
            // Ẩn tất cả các container trừ welcomeContainer
            pollContainer.classList.add('hidden');
            resultsContainer.classList.add('hidden');
            resourcesContainer.classList.add('hidden');
            welcomeContainer.classList.remove('hidden');
            
            // Cập nhật dashboard
            updateProgressDashboard(data.chatState);
            
            // Cập nhật tên assessment hiện tại
            updateCurrentAssessment('greeting');
        })
        .catch(error => {
            isLoading = false;
            console.error('Error restarting survey:', error);
            showErrorMessage("Không thể khởi động lại khảo sát. Vui lòng thử lại sau.");
        });
    }
    
    /**
     * Hoàn thành khảo sát
     */
    function completeSurvey() {
        alert("Cảm ơn bạn đã hoàn thành khảo sát. Chúc bạn một ngày tốt lành!");
        
        // Trở về welcome screen
        resourcesContainer.classList.add('hidden');
        welcomeContainer.classList.remove('hidden');
        
        // Reset lịch sử
        pollHistory = [];
        
        // Reset currentAssessmentState
        currentAssessmentState = null;
        
        // Cập nhật dashboard
        updateProgressDashboard({
            state: 'greeting',
            currentQuestionIndex: 0,
            totalQuestions: 0
        });
        
        // Cập nhật tên assessment hiện tại
        updateCurrentAssessment('greeting');
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
        let title = "Bắt đầu khảo sát";
        let detail = "Đánh giá sơ bộ";
        let detailText = "Hệ thống đang xử lý thông tin của bạn...";
        
        // Lấy thông tin câu hỏi từ chatState
        const currentQuestionIndex = chatState.currentQuestionIndex || 0;
        const totalQuestions = chatState.totalQuestions || 0;
        
        // Cập nhật thông tin dựa trên trạng thái
        switch (state) {
            case 'greeting':
                title = "Bắt đầu khảo sát";
                detail = "Chào mừng bạn đến với Khảo sát Sức khỏe Tâm thần";
                detailText = "Khảo sát này sẽ giúp đánh giá sơ bộ tình trạng sức khỏe tâm thần của bạn.";
                break;
                
            case 'initial_screening':
                title = "Sàng lọc Ban đầu";
                detail = "Đánh giá sơ bộ các triệu chứng";
                detailText = `Đang thực hiện đánh giá ${currentQuestionIndex + 1}/${totalQuestions || 10} câu hỏi.`;
                break;
            
            case 'detailed_assessment':
            case 'additional_assessment':
                if (assessmentId) {
                    if (assessmentId === 'phq9') {
                        title = "PHQ-9";
                        detail = "Đánh giá Trầm cảm";
                    } else if (assessmentId === 'gad7') {
                        title = "GAD-7";
                        detail = "Đánh giá Lo âu";
                    } else if (assessmentId === 'dass21_stress') {
                        title = "DASS-21";
                        detail = "Đánh giá Căng thẳng";
                    } else {
                        title = "Đánh giá Chi tiết";
                        detail = "Đánh giá chuyên sâu";
                    }
                    detailText = `Đang thực hiện đánh giá ${currentQuestionIndex + 1}/${totalQuestions || 10} câu hỏi.`;
                }
                break;
                
            case 'suicide_assessment':
                title = "Đánh giá Nguy cơ";
                detail = "Câu hỏi quan trọng";
                detailText = "Đang đánh giá mức độ nghiêm trọng để có thể hỗ trợ bạn tốt nhất.";
                break;
                
            case 'summary':
                title = "Tổng kết Kết quả";
                detail = "Tóm tắt đánh giá";
                detailText = "Kết quả đánh giá sơ bộ dựa trên câu trả lời của bạn.";
                break;
                
            case 'resources':
                title = "Tài nguyên Hỗ trợ";
                detail = "Thông tin và hỗ trợ";
                detailText = "Các tài nguyên phù hợp với nhu cầu của bạn.";
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
            questionProgress.textContent = "Đang xử lý";
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
            'initial_screening': 20,
            'detailed_assessment': 50,
            'additional_assessment': 60,
            'suicide_assessment': 70,
            'summary': 80,
            'resources': 100
        };
        
        // Lấy tiến trình cơ bản dựa trên trạng thái
        let baseProgress = phaseWeights[state] || 0;
        
        // Nếu đang trong giai đoạn câu hỏi, thêm tiến trình dựa trên chỉ số câu hỏi
        if (['initial_screening', 'detailed_assessment', 'additional_assessment', 'suicide_assessment'].includes(state)) {
            if (totalQuestions > 0) {
                // Tính tiến trình trong giai đoạn hiện tại
                const phaseProgress = phaseWeights[state];
                const nextPhaseProgress = state === 'suicide_assessment' ? 80 : 
                                        state === 'initial_screening' ? 50 : 70;
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
            'initial_screening': 'screening',
            'detailed_assessment': 'detailed',
            'additional_assessment': 'detailed',
            'suicide_assessment': 'detailed',
            'summary': 'review',
            'resources': 'support'
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
     * Cập nhật hiển thị tên đánh giá hiện tại
     */
    function updateCurrentAssessment(state) {
        let assessmentName = 'Bảng Khảo sát';
        
        if (state === 'initial_screening') {
            assessmentName = 'Sàng lọc Ban đầu';
        } else if (state === 'detailed_assessment' || state === 'additional_assessment') {
            assessmentName = 'Đánh giá Chi tiết';
        } else if (state === 'suicide_assessment') {
            assessmentName = 'Đánh giá Nguy cơ';
        } else if (state === 'summary') {
            assessmentName = 'Tổng kết Kết quả';
        } else if (state === 'resources') {
            assessmentName = 'Tài nguyên Hỗ trợ';
        } else if (state === 'results_preview') {
            assessmentName = 'Kết quả Sơ bộ';
        }
        
        if (currentAssessment) {
            currentAssessment.textContent = assessmentName;
        }
    }
    
    /**
     * Hiển thị tin nhắn lỗi
     */
    function showErrorMessage(errorMessage) {
        if (!errorMessageTemplate) return;
        
        // Hiển thị lỗi trong alert
        alert(`Lỗi: ${errorMessage}`);
    }
});