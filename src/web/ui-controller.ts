// Terry the Tube - Centralized UI Controller

import { ElementKey, Message, ErrorInfo } from './types';

/**
 * Centralized UI controller for DOM manipulation and rendering
 */
export class UIController {
    private elements: Map<ElementKey, HTMLElement>;

    constructor() {
        this.elements = new Map();
        this.cacheElements();
    }
    
    /**
     * Cache DOM elements for performance using ES6+ features
     */
    private cacheElements(): void {
        const elementMap: Record<string, ElementKey> = {
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
            const element = document.getElementById(id as string);
            if (element) {
                this.elements.set(id, element);
            }
        }
    }
    
    /**
     * Get cached DOM element
     */
    getElement(key: ElementKey): HTMLElement | undefined {
        return this.elements.get(key);
    }
    
    /**
     * Update connection status using modern JavaScript patterns
     */
    updateConnectionStatus(): void {
        const indicator = this.getElement('connectionIndicator');
        const text = this.getElement('connectionText');
        
        if (!indicator || !text) return;
        
        const connectionState = window.appState.get('connection');
        const { status, reconnectAttempts, maxReconnectAttempts } = connectionState;
        
        // Remove all status classes using spread operator
        indicator.classList.remove('connected', 'connecting', 'disconnected');
        
        const statusConfig: Record<string, { class: string; text: string }> = {
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
    
    /**
     * Update recording state using optional chaining
     */
    updateRecordingState(): void {
        const indicator = this.getElement('recordingIndicator');
        const isRecording = window.appState.get('ui.recording');
        
        if (indicator) {
            (indicator as HTMLElement).style.setProperty('display', isRecording ? 'flex' : 'none');
        }
    }
    
    /**
     * Update loading states using destructuring and optional chaining
     */
    updateLoadingStates(): void {
        const { generatingResponse, generatingAudio } = window.appState.get('ui.loadingStates');
        
        this.getElement('responseLoading')?.classList.toggle('show', generatingResponse);
        this.getElement('ttsLoading')?.classList.toggle('show', generatingAudio);
    }
    
    /**
     * Update status display using template literals and optional chaining
     */
    updateStatus(): void {
        const statusElement = this.getElement('status');
        const currentStatus = window.appState.get('data.currentStatus');
        
        if (statusElement && currentStatus) {
            const icon = this.getStatusIcon(currentStatus);
            statusElement.innerHTML = `<i class="${icon}"></i><span>${currentStatus}</span>`;
        }
    }
    
    /**
     * Update messages display
     */
    updateMessages(): void {
        const messagesDiv = this.getElement('messages');
        if (!messagesDiv) return;
        
        const messages: Message[] = window.appState.get('data.messages') || [];
        const lastCount = window.appState.get('ui.lastMessageCount');
        
        // Only add new messages, don't rebuild entire list
        if (messages.length > lastCount) {
            for (let i = lastCount; i < messages.length; i++) {
                const msg = messages[i];
                const messageDiv = this.createMessageElement(msg, i);
                messagesDiv.appendChild(messageDiv);
            }
            
            window.appState.set('ui.lastMessageCount', messages.length);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        // Handle message clearing (when count goes down)
        if (messages.length < lastCount) {
            messagesDiv.innerHTML = '';
            window.appState.set('ui.lastMessageCount', 0);
            
            // Re-add all messages
            messages.forEach((msg, index) => {
                const messageDiv = this.createMessageElement(msg, index);
                messagesDiv.appendChild(messageDiv);
            });
            
            window.appState.set('ui.lastMessageCount', messages.length);
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
    
    /**
     * Create message element
     */
    private createMessageElement(msg: Message, index: number): HTMLDivElement {
        const messageDiv = document.createElement('div');
        
        // Set initial visibility based on show_immediately flag
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
    
    /**
     * Update personality display and overlay
     */
    updatePersonalityState(): void {
        const overlay = this.getElement('personalityOverlay');
        const personalityDisplay = this.getElement('personalityDisplay');
        
        const personalitySelected = window.appState.get('data.selectedPersonality');
        const personalityInfo = window.appState.get('data.personalityInfo');
        
        if (personalitySelected && personalityInfo) {
            // Hide overlay if personality is selected
            overlay?.classList.add('hidden');
            // Update personality display
            if (personalityDisplay) {
                personalityDisplay.textContent = `${personalityInfo.short_name} Bartender`;
            }
        } else if (!personalitySelected) {
            // Show overlay if no personality selected
            if (overlay?.classList.contains('hidden')) {
                overlay.classList.remove('hidden');
                this.resetPersonalitySelection();
            }
            // Reset personality display to default
            if (personalityDisplay) {
                personalityDisplay.textContent = 'Your AI Bartender';
            }
        }
    }
    
    /**
     * Update text chat visibility
     */
    updateTextChatVisibility(): void {
        const textChatContainer = this.getElement('textChatContainer');
        const textChatEnabled = window.appState.get('ui.textChatEnabled');
        
        if (textChatContainer) {
            (textChatContainer as HTMLElement).style.display = textChatEnabled ? 'block' : 'none';
        }
    }
    
    /**
     * Reset personality selection UI
     */
    resetPersonalitySelection(): void {
        const dropdown = this.getElement('personalityDropdown') as HTMLSelectElement;
        const confirmBtn = this.getElement('confirmPersonalityBtn') as HTMLButtonElement;
        
        if (dropdown) dropdown.value = '';
        if (confirmBtn) {
            confirmBtn.textContent = 'Start Your Beer Journey';
            confirmBtn.disabled = true;
        }
    }
    
    /**
     * Show error notification with toast
     */
    showError(message: string, type: 'error' | 'info' = 'error'): void {
        // Add to error state
        const currentErrors: ErrorInfo[] = window.appState.get('ui.errors') || [];
        const errorId = Date.now();
        const newError: ErrorInfo = { 
            id: errorId, 
            message, 
            type, 
            timestamp: new Date() 
        };
        
        window.appState.set('ui.errors', [...currentErrors, newError]);
        
        // Create toast notification
        this.createToast(newError);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.removeError(errorId);
        }, 5000);
    }
    
    /**
     * Create toast notification
     */
    private createToast(error: ErrorInfo): void {
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
    
    /**
     * Create toast container if it doesn't exist
     */
    private createToastContainer(): void {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    /**
     * Remove error notification
     */
    removeError(errorId: number): void {
        const currentErrors: ErrorInfo[] = window.appState.get('ui.errors') || [];
        const updatedErrors = currentErrors.filter(error => error.id !== errorId);
        window.appState.set('ui.errors', updatedErrors);
        
        const toast = document.querySelector(`[data-error-id="${errorId}"]`);
        if (toast) {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }
    }
    
    /**
     * Get status icon class name
     */
    private getStatusIcon(status: string): string {
        if (status.includes('Recording')) return 'fas fa-microphone';
        if (status.includes('Processing')) return 'fas fa-cog fa-spin';
        if (status.includes('Speaking')) return 'fas fa-volume-up';
        if (status.includes('beer') || status.includes('Beer')) return 'fas fa-beer';
        return 'fas fa-check-circle';
    }
}