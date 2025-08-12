// Terry the Tube - Main Application Controller

class AppController {
    constructor() {
        this.wsManager = new WebSocketManager();
        this.initialized = false;
    }
    
    // Initialize application
    init() {
        if (this.initialized) return;
        
        console.log('Initializing Terry the Tube web interface...');
        
        try {
            // Initialize state listeners first
            this.initializeStateListeners();
            
            // Setup UI event listeners
            this.setupEventListeners();
            
            // Connect to WebSocket server
            this.wsManager.connect();
            
            // Load available personalities
            this.loadPersonalities();
            
            // Set initial UI state
            appState.update({
                'data.currentStatus': 'Ready to serve beer!',
                'ui.personalityOverlayVisible': true,
                'ui.textChatEnabled': false
            });
            
            this.initialized = true;
            console.log('App initialization complete');
            
        } catch (error) {
            console.error('Error during app initialization:', error);
            uiController.showError('Failed to initialize application: ' + error.message);
        }
    }
    
    // Initialize state change listeners using modern object mapping
    initializeStateListeners() {
        const stateListeners = {
            'connection.status': () => uiController.updateConnectionStatus(),
            'ui.recording': () => uiController.updateRecordingState(),
            'ui.loadingStates': () => uiController.updateLoadingStates(),
            'data.currentStatus': () => uiController.updateStatus(),
            'data.messages': () => uiController.updateMessages(),
            'ui.textChatEnabled': () => uiController.updateTextChatVisibility()
        };
        
        // Use Object.entries with destructuring
        Object.entries(stateListeners).forEach(([key, handler]) => {
            appState.subscribe(key, handler);
        });
        
        console.log('State listeners initialized');
    }
    
    // Setup UI event listeners using array method
    setupEventListeners() {
        const setupMethods = [
            this.setupTextChatListeners,
            this.setupPersonalityListeners,
            this.setupErrorBoundaries
        ];
        
        setupMethods.forEach(method => method.call(this));
    }
    
    // Setup text chat event listeners
    setupTextChatListeners() {
        const input = uiController.getElement('textChatInput');
        const sendBtn = uiController.getElement('textChatSendBtn');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendTextMessage());
        }
        
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendTextMessage();
                }
            });
        }
    }
    
    // Setup personality selection listeners
    setupPersonalityListeners() {
        const confirmBtn = uiController.getElement('confirmPersonalityBtn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => this.confirmPersonalitySelection());
        }
    }
    
    // Setup global error boundaries using modern event handling
    setupErrorBoundaries() {
        const errorHandlers = {
            error: ({ error }) => {
                console.error('Global error:', error);
                uiController.showError('An unexpected error occurred. Please refresh the page.');
            },
            unhandledrejection: ({ reason }) => {
                console.error('Unhandled promise rejection:', reason);
                uiController.showError('A network error occurred. Please check your connection.');
            }
        };
        
        Object.entries(errorHandlers).forEach(([event, handler]) => {
            window.addEventListener(event, handler);
        });
    }
    
    // Recording functions using modern error handling
    startRecording() {
        const isRecording = appState.get('ui.recording');
        const connectionStatus = appState.get('connection.status');
        
        // Early return pattern with guard clauses
        if (connectionStatus !== 'connected') {
            uiController.showError('Cannot record - not connected to server');
            return;
        }
        
        if (isRecording) return;
        
        try {
            appState.set('ui.recording', true);
            
            const success = this.wsManager.sendMessage('start_recording');
            if (success) {
                console.log('Recording started');
            } else {
                appState.set('ui.recording', false); // Rollback on failure
            }
        } catch (error) {
            console.error('Error starting recording:', error);
            uiController.showError(`Failed to start recording: ${error.message}`);
            appState.set('ui.recording', false);
        }
    }
    
    stopRecording() {
        const currentRecording = appState.get('ui.recording');
        
        if (currentRecording) {
            try {
                appState.set('ui.recording', false);
                
                if (this.wsManager.sendMessage('stop_recording')) {
                    console.log('Recording stopped');
                    appState.set('ui.loadingStates.generatingResponse', true);
                } else {
                    // Rollback state if send failed
                    appState.set('ui.recording', true);
                }
            } catch (error) {
                console.error('Error stopping recording:', error);
                uiController.showError('Failed to stop recording: ' + error.message);
                appState.set('ui.recording', true);
            }
        }
    }
    
    // Send text message
    sendTextMessage() {
        const input = uiController.getElement('textChatInput');
        const sendBtn = uiController.getElement('textChatSendBtn');
        
        if (!input || !sendBtn) {
            uiController.showError('Text chat interface not available');
            return;
        }
        
        const message = input.value.trim();
        if (!message) return;
        
        // Set loading state
        appState.set('ui.loadingStates.sendingMessage', true);
        input.disabled = true;
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        try {
            if (this.wsManager.sendMessage('send_text_message', { message: message })) {
                input.value = ''; // Clear input on success
                // Loading state will be cleared when we receive response
            } else {
                uiController.showError('Failed to send message - not connected to server');
                // Clear loading state on error
                appState.set('ui.loadingStates.sendingMessage', false);
            }
        } catch (error) {
            uiController.showError('Error sending message: ' + error.message);
            appState.set('ui.loadingStates.sendingMessage', false);
        } finally {
            // Re-enable input and button after a short delay
            setTimeout(() => {
                input.disabled = false;
                sendBtn.disabled = false;
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
                input.focus();
                appState.set('ui.loadingStates.sendingMessage', false);
            }, 500);
        }
    }
    
    // Load personalities
    loadPersonalities() {
        this.wsManager.sendMessage('get_personalities');
    }
    
    // Populate personality dropdown
    populatePersonalityDropdown() {
        const dropdown = uiController.getElement('personalityDropdown');
        if (!dropdown) return;
        
        const availablePersonalities = appState.get('data.availablePersonalities') || [];
        
        dropdown.innerHTML = '<option value="">Choose a personality...</option>';
        
        availablePersonalities.forEach(personality => {
            const option = document.createElement('option');
            option.value = personality.key;
            option.textContent = personality.name;
            dropdown.appendChild(option);
        });
        
        dropdown.addEventListener('change', function() {
            const confirmBtn = uiController.getElement('confirmPersonalityBtn');
            if (this.value) {
                if (confirmBtn) confirmBtn.disabled = false;
                appState.set('data.selectedPersonality', this.value);
            } else {
                if (confirmBtn) confirmBtn.disabled = true;
                appState.set('data.selectedPersonality', null);
            }
        });
    }
    
    // Confirm personality selection
    confirmPersonalitySelection() {
        const selectedPersonality = appState.get('data.selectedPersonality');
        const connectionStatus = appState.get('connection.status');
        
        if (!selectedPersonality) {
            uiController.showError('Please select a personality first');
            return;
        }
        
        if (connectionStatus !== 'connected') {
            uiController.showError('Cannot set personality - not connected to server');
            return;
        }
        
        const confirmBtn = uiController.getElement('confirmPersonalityBtn');
        const overlay = uiController.getElement('personalityOverlay');
        
        try {
            if (confirmBtn) {
                confirmBtn.textContent = 'Starting...';
                confirmBtn.disabled = true;
            }
            
            if (this.wsManager.sendMessage('select_personality', { personality: selectedPersonality })) {
                // Hide overlay immediately when button is clicked
                if (overlay) overlay.classList.add('hidden');
                appState.set('ui.personalityOverlayVisible', false);
            } else {
                // Show overlay again if WebSocket send failed
                if (overlay) overlay.classList.remove('hidden');
                if (confirmBtn) {
                    confirmBtn.textContent = 'Try Again';
                    confirmBtn.disabled = false;
                }
                appState.set('ui.personalityOverlayVisible', true);
            }
        } catch (error) {
            console.error('Error setting personality:', error);
            uiController.showError('Failed to set personality: ' + error.message);
            
            if (overlay) overlay.classList.remove('hidden');
            if (confirmBtn) {
                confirmBtn.textContent = 'Try Again';
                confirmBtn.disabled = false;
            }
            appState.set('ui.personalityOverlayVisible', true);
        }
    }
}

// Export for use in main template
window.AppController = AppController;