// Terry the Tube - UI Controller
class UIController {
    constructor() {
        this.elements = new Map();
        this.cacheElements();
    }
    cacheElements() {
        const elementMap = {
            connectionIndicator: 'connectionIndicator',
            connectionText: 'connectionText',
            connectionDot: 'connectionDot',
            recordingIndicator: 'recordingIndicator',
            status: 'status',
            messages: 'messages',
            responseLoading: 'responseLoading',
            ttsLoading: 'ttsLoading',
            personalityOverlay: 'personalityOverlay',
            personalityDisplay: 'personalityDisplay',
            personalityDropdown: 'personalityDropdown',
            confirmPersonalityBtn: 'confirmPersonalityBtn',
            textChatContainer: 'textChatContainer',
            textChatInput: 'textChatInput',
            textChatSendBtn: 'textChatSendBtn',
            talkButton: 'talkButton'
        };
        for (const [key, id] of Object.entries(elementMap)) {
            const element = document.getElementById(id);
            if (element) {
                this.elements.set(id, element);
            }
        }
    }
    getElement(key) {
        return this.elements.get(key);
    }
    updateConnectionStatus() {
        var _a;
        const indicator = this.getElement('connectionIndicator');
        const text = this.getElement('connectionText');
        if (!indicator || !text)
            return;
        const connectionState = window.appState.get('connection');
        const { status, reconnectAttempts, maxReconnectAttempts } = connectionState;
        indicator.classList.remove('connected', 'connecting', 'disconnected');
        const statusConfig = {
            connected: {
                class: 'connected',
                text: 'Connected'
            },
            connecting: {
                class: 'connecting',
                text: `Connecting${reconnectAttempts > 0 ? ` (${reconnectAttempts}/${maxReconnectAttempts})` : '...'}`
            },
            disconnected: {
                class: 'disconnected',
                text: 'Disconnected'
            },
            error: {
                class: 'disconnected',
                text: 'Connection Error'
            }
        };
        const config = (_a = statusConfig[status]) !== null && _a !== void 0 ? _a : statusConfig.disconnected;
        indicator.classList.add(config.class);
        text.textContent = config.text;
    }
    updateRecordingState() {
        const indicator = this.getElement('recordingIndicator');
        const isRecording = window.appState.get('ui.recording');
        if (indicator) {
            indicator.style.setProperty('display', isRecording ? 'flex' : 'none');
        }
    }
    updateLoadingStates() {
        var _a, _b;
        const { generatingResponse, generatingAudio } = window.appState.get('ui.loadingStates');
        (_a = this.getElement('responseLoading')) === null || _a === void 0 ? void 0 : _a.classList.toggle('show', generatingResponse);
        (_b = this.getElement('ttsLoading')) === null || _b === void 0 ? void 0 : _b.classList.toggle('show', generatingAudio);
    }
    updateStatus() {
        const statusElement = this.getElement('status');
        const currentStatus = window.appState.get('data.currentStatus');
        if (statusElement && currentStatus) {
            const icon = this.getStatusIcon(currentStatus);
            statusElement.innerHTML = `<i class="${icon}"></i><span>${currentStatus}</span>`;
        }
    }
    updateMessages() {
        const messagesDiv = this.getElement('messages');
        if (!messagesDiv)
            return;
        const messages = window.appState.get('data.messages') || [];
        const lastCount = window.appState.get('ui.lastMessageCount');
        if (messages.length > lastCount) {
            for (let i = lastCount; i < messages.length; i++) {
                const msg = messages[i];
                const messageDiv = this.createMessageElement(msg, i);
                messagesDiv.appendChild(messageDiv);
            }
            window.appState.set('ui.lastMessageCount', messages.length);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        if (messages.length < lastCount) {
            messagesDiv.innerHTML = '';
            window.appState.set('ui.lastMessageCount', 0);
            messages.forEach((msg, index) => {
                const messageDiv = this.createMessageElement(msg, index);
                messagesDiv.appendChild(messageDiv);
            });
            window.appState.set('ui.lastMessageCount', messages.length);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        messages.forEach((msg, index) => {
            const messageDiv = document.querySelector(`[data-message-id="${index}"]`);
            if (messageDiv && msg.show_immediately && messageDiv.classList.contains('pending')) {
                messageDiv.classList.remove('pending');
                messageDiv.classList.add('show');
            }
        });
    }
    createMessageElement(msg, index) {
        const messageDiv = document.createElement('div');
        const initialClass = msg.show_immediately ? 'message show' : 'message pending';
        messageDiv.className = initialClass + ' ' + (msg.is_ai ? 'ai-message' : 'user-message');
        messageDiv.setAttribute('data-message-id', index.toString());
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = msg.message;
        const info = document.createElement('div');
        info.className = 'message-info';
        const userIcon = msg.is_ai ? 'fas fa-robot' : 'fas fa-user';
        info.innerHTML = `<i class="${userIcon}"></i><span class="timestamp">${msg.timestamp}</span><span>${msg.sender}</span>`;
        messageDiv.appendChild(bubble);
        messageDiv.appendChild(info);
        return messageDiv;
    }
    updatePersonalityState() {
        const overlay = this.getElement('personalityOverlay');
        const personalityDisplay = this.getElement('personalityDisplay');
        const overlayVisible = window.appState.get('ui.personalityOverlayVisible');
        const personalityInfo = window.appState.get('data.personalityInfo');
        
        if (overlayVisible) {
            // Only reset if overlay was previously hidden (newly shown)
            const wasHidden = overlay?.classList.contains('hidden');
            overlay?.classList.remove('hidden');
            
            // Only reset dropdown when overlay is newly shown, not on every update
            if (wasHidden) {
                this.resetPersonalitySelection();
            }
            
            if (personalityDisplay) {
                personalityDisplay.textContent = 'Your AI Bartender';
            }
        } else {
            // Hide overlay and show selected personality
            overlay?.classList.add('hidden');
            if (personalityDisplay && personalityInfo) {
                personalityDisplay.textContent = `${personalityInfo.short_name} Bartender`;
            }
        }
    }
    updateTextChatVisibility() {
        const textChatContainer = this.getElement('textChatContainer');
        const textChatEnabled = window.appState.get('ui.textChatEnabled');
        if (textChatContainer) {
            textChatContainer.style.display = textChatEnabled ? 'block' : 'none';
        }
    }
    resetPersonalitySelection() {
        const dropdown = this.getElement('personalityDropdown');
        const confirmBtn = this.getElement('confirmPersonalityBtn');
        if (dropdown)
            dropdown.value = '';
        if (confirmBtn) {
            confirmBtn.textContent = 'Start Your Beer Journey';
            confirmBtn.disabled = true;
        }
    }
    showError(message, type = 'error') {
        const currentErrors = window.appState.get('ui.errors') || [];
        const errorId = Date.now();
        const newError = {
            id: errorId,
            message,
            type,
            timestamp: new Date()
        };
        window.appState.set('ui.errors', [...currentErrors, newError]);
        this.createToast(newError);
        setTimeout(() => {
            this.removeError(errorId);
        }, 5000);
    }
    createToast(error) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${error.type}`;
        toast.setAttribute('data-error-id', error.id.toString());
        toast.innerHTML = `
            <i class="fas fa-${error.type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${error.message}</span>
            <button class="toast-close" onclick="window.uiController.removeError(${error.id})">
                <i class="fas fa-times"></i>
            </button>
        `;
        if (!document.querySelector('.toast-container')) {
            this.createToastContainer();
        }
        const container = document.querySelector('.toast-container');
        if (container) {
            container.appendChild(toast);
            setTimeout(() => toast.classList.add('show'), 10);
        }
    }
    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    removeError(errorId) {
        const currentErrors = window.appState.get('ui.errors') || [];
        const updatedErrors = currentErrors.filter(error => error.id !== errorId);
        window.appState.set('ui.errors', updatedErrors);
        const toast = document.querySelector(`[data-error-id="${errorId}"]`);
        if (toast) {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }
    }
    getStatusIcon(status) {
        if (status.includes('Recording'))
            return 'fas fa-microphone';
        if (status.includes('Processing'))
            return 'fas fa-cog fa-spin';
        if (status.includes('Speaking'))
            return 'fas fa-volume-up';
        if (status.includes('beer') || status.includes('Beer'))
            return 'fas fa-beer';
        return 'fas fa-check-circle';
    }
}
