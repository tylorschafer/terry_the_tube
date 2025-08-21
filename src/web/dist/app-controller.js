// Terry the Tube - Main Application Controller
class AppController {
    constructor() {
        this.pollingManager = new PollingManager();
        this.initialized = false;
    }
    init() {
        if (this.initialized)
            return;
        console.log('Initializing Terry the Tube web interface...');
        try {
            this.initializeStateListeners();
            this.setupEventListeners();
            this.pollingManager.start();
            this.loadPersonalities();
            window.appState.update({
                'data.currentStatus': 'Ready to serve beer!',
                'ui.personalityOverlayVisible': true,
                'ui.textChatEnabled': true
            });
            this.initialized = true;
            console.log('App initialization complete');
        }
        catch (error) {
            console.error('Error during app initialization:', error);
            window.uiController.showError(`Failed to initialize application: ${error.message}`);
        }
    }
    initializeStateListeners() {
        const stateListeners = {
            'connection.status': () => window.uiController.updateConnectionStatus(),
            'ui.recording': () => window.uiController.updateRecordingState(),
            'ui.loadingStates': () => window.uiController.updateLoadingStates(),
            'data.currentStatus': () => window.uiController.updateStatus(),
            'data.messages': () => window.uiController.updateMessages(),
            'ui.textChatEnabled': () => window.uiController.updateTextChatVisibility(),
            'ui.personalityOverlayVisible': () => window.uiController.updatePersonalityState()
        };
        Object.entries(stateListeners).forEach(([key, handler]) => {
            window.appState.subscribe(key, handler);
        });
        console.log('State listeners initialized');
    }
    setupEventListeners() {
        const setupMethods = [
            this.setupTextChatListeners,
            this.setupPersonalityListeners,
            this.setupErrorBoundaries
        ];
        setupMethods.forEach(method => method.call(this));
    }
    setupTextChatListeners() {
        const input = window.uiController.getElement('textChatInput');
        const sendBtn = window.uiController.getElement('textChatSendBtn');
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
    setupPersonalityListeners() {
        const confirmBtn = window.uiController.getElement('confirmPersonalityBtn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => this.confirmPersonalitySelection());
        }
    }
    setupErrorBoundaries() {
        const errorHandlers = {
            error: ({ error }) => {
                console.error('Global error:', error);
                window.uiController.showError('An unexpected error occurred. Please refresh the page.');
            },
            unhandledrejection: ({ reason }) => {
                console.error('Unhandled promise rejection:', reason);
                window.uiController.showError('A network error occurred. Please check your connection.');
            }
        };
        Object.entries(errorHandlers).forEach(([event, handler]) => {
            window.addEventListener(event, handler);
        });
    }
    startRecording() {
        const isRecording = window.appState.get('ui.recording');
        const connectionStatus = window.appState.get('connection.status');
        if (connectionStatus !== 'connected') {
            window.uiController.showError('Cannot record - not connected to server');
            return;
        }
        if (isRecording)
            return;
        try {
            window.appState.set('ui.recording', true);
            const success = this.pollingManager.sendMessage('start_recording');
            if (success) {
                console.log('Recording started');
            }
            else {
                window.appState.set('ui.recording', false);
            }
        }
        catch (error) {
            console.error('Error starting recording:', error);
            window.uiController.showError(`Failed to start recording: ${error.message}`);
            window.appState.set('ui.recording', false);
        }
    }
    stopRecording() {
        const currentRecording = window.appState.get('ui.recording');
        if (currentRecording) {
            try {
                window.appState.set('ui.recording', false);
                if (this.pollingManager.sendMessage('stop_recording')) {
                    console.log('Recording stopped');
                    window.appState.set('ui.loadingStates.generatingResponse', true);
                }
                else {
                    window.appState.set('ui.recording', true);
                }
            }
            catch (error) {
                console.error('Error stopping recording:', error);
                window.uiController.showError(`Failed to stop recording: ${error.message}`);
                window.appState.set('ui.recording', true);
            }
        }
    }
    sendTextMessage() {
        const input = window.uiController.getElement('textChatInput');
        const sendBtn = window.uiController.getElement('textChatSendBtn');
        if (!input || !sendBtn) {
            window.uiController.showError('Text chat interface not available');
            return;
        }
        const message = input.value.trim();
        if (!message)
            return;
        window.appState.set('ui.loadingStates.sendingMessage', true);
        input.disabled = true;
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        try {
            if (this.pollingManager.sendMessage('send_text_message', { message: message })) {
                input.value = '';
            }
            else {
                window.uiController.showError('Failed to send message - not connected to server');
                window.appState.set('ui.loadingStates.sendingMessage', false);
            }
        }
        catch (error) {
            window.uiController.showError(`Error sending message: ${error.message}`);
            window.appState.set('ui.loadingStates.sendingMessage', false);
        }
        finally {
            setTimeout(() => {
                input.disabled = false;
                sendBtn.disabled = false;
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
                input.focus();
                window.appState.set('ui.loadingStates.sendingMessage', false);
            }, 500);
        }
    }
    loadPersonalities() {
        // Personalities are loaded automatically by polling manager
        console.log('Personalities will be loaded by polling manager');
    }
    populatePersonalityDropdown() {
        const dropdown = window.uiController.getElement('personalityDropdown');
        if (!dropdown)
            return;
        const availablePersonalities = window.appState.get('data.availablePersonalities') || [];
        dropdown.innerHTML = '<option value="">Choose a personality...</option>';
        availablePersonalities.forEach((personality) => {
            const option = document.createElement('option');
            option.value = personality.key;
            option.textContent = personality.name;
            dropdown.appendChild(option);
        });
        dropdown.addEventListener('change', function () {
            const confirmBtn = window.uiController.getElement('confirmPersonalityBtn');
            if (this.value) {
                if (confirmBtn)
                    confirmBtn.disabled = false;
                window.appState.set('data.selectedPersonality', this.value);
            }
            else {
                if (confirmBtn)
                    confirmBtn.disabled = true;
                window.appState.set('data.selectedPersonality', null);
            }
        });
    }
    confirmPersonalitySelection() {
        const selectedPersonality = window.appState.get('data.selectedPersonality');
        const connectionStatus = window.appState.get('connection.status');
        if (!selectedPersonality) {
            window.uiController.showError('Please select a personality first');
            return;
        }
        if (connectionStatus !== 'connected') {
            window.uiController.showError('Cannot set personality - not connected to server');
            return;
        }
        const confirmBtn = window.uiController.getElement('confirmPersonalityBtn');
        const overlay = window.uiController.getElement('personalityOverlay');
        try {
            if (confirmBtn) {
                confirmBtn.textContent = 'Starting...';
                confirmBtn.disabled = true;
            }
            if (this.pollingManager.sendMessage('select_personality', { personality: selectedPersonality })) {
                overlay?.classList.add('hidden');
                window.appState.set('ui.personalityOverlayVisible', false);
            }
            else {
                overlay?.classList.remove('hidden');
                if (confirmBtn) {
                    confirmBtn.textContent = 'Try Again';
                    confirmBtn.disabled = false;
                }
                window.appState.set('ui.personalityOverlayVisible', true);
            }
        }
        catch (error) {
            console.error('Error setting personality:', error);
            window.uiController.showError(`Failed to set personality: ${error.message}`);
            overlay?.classList.remove('hidden');
            if (confirmBtn) {
                confirmBtn.textContent = 'Try Again';
                confirmBtn.disabled = false;
            }
            window.appState.set('ui.personalityOverlayVisible', true);
        }
    }
}
