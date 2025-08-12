// Terry the Tube - Centralized UI Controller

class UIController {
    constructor() {
        this.elements = new Map();
        this.cacheElements();
    }
    
    // Cache DOM elements for performance using ES6+ features
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
        
        // Use for...of with destructuring and optional chaining
        for (const [key, id] of Object.entries(elementMap)) {
            const element = document.getElementById(id);
            element && this.elements.set(key, element);
        }
    }
    
    // Get cached element
    getElement(key) {
        return this.elements.get(key);
    }
    
    // Update connection status using modern JavaScript patterns
    updateConnectionStatus() {
        const indicator = this.getElement('connectionIndicator');
        const text = this.getElement('connectionText');
        
        if (!indicator || !text) return;
        
        const connectionState = appState.get('connection');
        const { status, reconnectAttempts, maxReconnectAttempts } = connectionState;
        
        // Remove all status classes using spread operator
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
        
        const config = statusConfig[status] ?? statusConfig.disconnected;
        indicator.classList.add(config.class);
        text.textContent = config.text;
    }
    
    // Update recording state using optional chaining
    updateRecordingState() {
        const indicator = this.getElement('recordingIndicator');
        const isRecording = appState.get('ui.recording');
        
        indicator?.style.setProperty('display', isRecording ? 'flex' : 'none');
    }
    
    // Update loading states using destructuring and optional chaining
    updateLoadingStates() {
        const { generatingResponse, generatingAudio } = appState.get('ui.loadingStates');
        
        this.getElement('responseLoading')?.classList.toggle('show', generatingResponse);
        this.getElement('ttsLoading')?.classList.toggle('show', generatingAudio);
    }
    
    // Update status display using template literals and optional chaining
    updateStatus() {
        const statusElement = this.getElement('status');
        const currentStatus = appState.get('data.currentStatus');
        
        if (statusElement && currentStatus) {
            const icon = this.getStatusIcon(currentStatus);
            statusElement.innerHTML = `<i class="${icon}"></i><span>${currentStatus}</span>`;
        }
    }
    
    // Update messages
    updateMessages() {
        const messagesDiv = this.getElement('messages');
        if (!messagesDiv) return;
        
        const messages = appState.get('data.messages') || [];
        const lastCount = appState.get('ui.lastMessageCount');
        
        // Only add new messages, don't rebuild entire list
        if (messages.length > lastCount) {
            for (let i = lastCount; i < messages.length; i++) {
                const msg = messages[i];
                const messageDiv = this.createMessageElement(msg, i);
                messagesDiv.appendChild(messageDiv);
            }
            
            appState.set('ui.lastMessageCount', messages.length);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        // Handle message clearing (when count goes down)
        if (messages.length < lastCount) {
            messagesDiv.innerHTML = '';
            appState.set('ui.lastMessageCount', 0);
            
            // Re-add all messages
            messages.forEach((msg, index) => {
                const messageDiv = this.createMessageElement(msg, index);
                messagesDiv.appendChild(messageDiv);
            });
            
            appState.set('ui.lastMessageCount', messages.length);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        // Check for messages that should now be visible
        messages.forEach((msg, index) => {
            const messageDiv = document.querySelector(`[data-message-id="${index}"]`);
            if (messageDiv && msg.show_immediately && messageDiv.classList.contains('pending')) {
                messageDiv.classList.remove('pending');
                messageDiv.classList.add('show');
            }
        });
    }
    
    // Create message element
    createMessageElement(msg, index) {
        const messageDiv = document.createElement('div');
        
        // Set initial visibility based on show_immediately flag
        const initialClass = msg.show_immediately ? 'message show' : 'message pending';
        messageDiv.className = initialClass + ' ' + (msg.is_ai ? 'ai-message' : 'user-message');
        messageDiv.setAttribute('data-message-id', index);
        
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
    
    // Update personality display and overlay
    updatePersonalityState() {
        const overlay = this.getElement('personalityOverlay');
        const personalityDisplay = this.getElement('personalityDisplay');
        
        const personalitySelected = appState.get('data.selectedPersonality');
        const personalityInfo = appState.get('data.personalityInfo');
        
        if (personalitySelected && personalityInfo) {
            // Hide overlay if personality is selected
            if (overlay) overlay.classList.add('hidden');
            // Update personality display
            if (personalityDisplay) {
                personalityDisplay.textContent = `${personalityInfo.short_name} Bartender`;
            }
        } else if (!personalitySelected) {
            // Show overlay if no personality selected
            if (overlay && overlay.classList.contains('hidden')) {
                overlay.classList.remove('hidden');
                this.resetPersonalitySelection();
            }
            // Reset personality display to default
            if (personalityDisplay) {
                personalityDisplay.textContent = 'Your AI Bartender';
            }
        }
    }
    
    // Update text chat visibility
    updateTextChatVisibility() {
        const textChatContainer = this.getElement('textChatContainer');
        const textChatEnabled = appState.get('ui.textChatEnabled');
        
        if (textChatContainer) {
            textChatContainer.style.display = textChatEnabled ? 'block' : 'none';
        }
    }
    
    // Reset personality selection UI
    resetPersonalitySelection() {
        const dropdown = this.getElement('personalityDropdown');
        const confirmBtn = this.getElement('confirmPersonalityBtn');
        
        if (dropdown) dropdown.value = '';
        if (confirmBtn) {
            confirmBtn.textContent = 'Start Your Beer Journey';
            confirmBtn.disabled = true;
        }
    }
    
    // Show error notification
    showError(message, type = 'error') {
        // Add to error state
        const currentErrors = appState.get('ui.errors') || [];
        const errorId = Date.now();
        const newError = { id: errorId, message, type, timestamp: new Date() };
        
        appState.set('ui.errors', [...currentErrors, newError]);
        
        // Create toast notification
        this.createToast(newError);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.removeError(errorId);
        }, 5000);
    }
    
    // Create toast notification
    createToast(error) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${error.type}`;
        toast.setAttribute('data-error-id', error.id);
        toast.innerHTML = `
            <i class="fas fa-${error.type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${error.message}</span>
            <button class="toast-close" onclick="uiController.removeError(${error.id})">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add toast styles if not already present
        if (!document.querySelector('.toast-container')) {
            this.createToastContainer();
        }
        
        const container = document.querySelector('.toast-container');
        if (container) {
            container.appendChild(toast);
            
            // Animate in
            setTimeout(() => toast.classList.add('show'), 10);
        }
    }
    
    // Create toast container
    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    // Remove error
    removeError(errorId) {
        const currentErrors = appState.get('ui.errors') || [];
        const updatedErrors = currentErrors.filter(error => error.id !== errorId);
        appState.set('ui.errors', updatedErrors);
        
        const toast = document.querySelector(`[data-error-id="${errorId}"]`);
        if (toast) {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }
    }
    
    // Get status icon
    getStatusIcon(status) {
        if (status.includes('Recording')) return 'fas fa-microphone';
        if (status.includes('Processing')) return 'fas fa-cog fa-spin';
        if (status.includes('Speaking')) return 'fas fa-volume-up';
        if (status.includes('beer') || status.includes('Beer')) return 'fas fa-beer';
        return 'fas fa-check-circle';
    }
}

// Export for use in main template
window.UIController = UIController;