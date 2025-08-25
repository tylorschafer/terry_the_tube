// Terry the Tube - Main Application Controller

import { WebSocketManager } from './websocket-manager';

/**
 * Main application controller coordinating all components
 */
export class AppController {
    private wsManager: WebSocketManager;
    private initialized: boolean;

    constructor() {
        this.wsManager = new WebSocketManager();
        this.initialized = false;
    }
    
    /**
     * Initialize application
     */
    init(): void {
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
            window.appState.update({
                'data.currentStatus': 'Ready to serve beer!',
                'ui.personalityOverlayVisible': true,
                'ui.textChatEnabled': true
            });
            
            this.initialized = true;
            console.log('App initialization complete');
            
        } catch (error) {
            console.error('Error during app initialization:', error);
            window.uiController.showError(`Failed to initialize application: ${(error as Error).message}`);
        }
    }
    
    /**
     * Initialize state change listeners using modern object mapping
     */
    private initializeStateListeners(): void {
        const stateListeners: Record<string, () => void> = {
            'connection.status': () => window.uiController.updateConnectionStatus(),
            'ui.recording': () => window.uiController.updateRecordingState(),
            'ui.loadingStates': () => window.uiController.updateLoadingStates(),
            'data.currentStatus': () => window.uiController.updateStatus(),
            'data.messages': () => window.uiController.updateMessages(),
            'ui.textChatEnabled': () => window.uiController.updateTextChatVisibility()
        };
        
        // Use Object.entries with destructuring
        Object.entries(stateListeners).forEach(([key, handler]) => {
            window.appState.subscribe(key, handler);
        });
        
        console.log('State listeners initialized');
    }
    
    /**
     * Setup UI event listeners using array method
     */
    private setupEventListeners(): void {
        const setupMethods = [
            this.setupTextChatListeners,
            this.setupPersonalityListeners,
            this.setupErrorBoundaries
        ];
        
        setupMethods.forEach(method => method.call(this));
    }
    
    /**
     * Setup text chat event listeners
     */
    private setupTextChatListeners(): void {
        const input = window.uiController.getElement('textChatInput') as HTMLInputElement;
        const sendBtn = window.uiController.getElement('textChatSendBtn');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendTextMessage());
        }
        
        if (input) {
            input.addEventListener('keypress', (e: KeyboardEvent) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendTextMessage();
                }
            });
        }
    }
    
    /**
     * Setup personality selection listeners
     */
    private setupPersonalityListeners(): void {
        const confirmBtn = window.uiController.getElement('confirmPersonalityBtn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => this.confirmPersonalitySelection());
        }
    }
    
    /**
     * Setup global error boundaries using modern event handling
     */
    private setupErrorBoundaries(): void {
        const errorHandlers: Record<string, (event: any) => void> = {
            error: ({ error }: ErrorEvent) => {
                console.error('Global error:', error);
                window.uiController.showError('An unexpected error occurred. Please refresh the page.');
            },
            unhandledrejection: ({ reason }: PromiseRejectionEvent) => {
                console.error('Unhandled promise rejection:', reason);
                window.uiController.showError('A network error occurred. Please check your connection.');
            }
        };
        
        Object.entries(errorHandlers).forEach(([event, handler]) => {
            window.addEventListener(event, handler);
        });
    }
    
    /**
     * Recording functions using modern error handling
     */
    startRecording(): void {
        const isRecording = window.appState.get('ui.recording');
        const connectionStatus = window.appState.get('connection.status');
        
        // Early return pattern with guard clauses
        if (connectionStatus !== 'connected') {
            window.uiController.showError('Cannot record - not connected to server');
            return;
        }
        
        if (isRecording) return;
        
        try {
            window.appState.set('ui.recording', true);
            
            const success = this.wsManager.sendMessage('start_recording');
            if (success) {
                console.log('Recording started');
            } else {
                window.appState.set('ui.recording', false); // Rollback on failure
            }
        } catch (error) {
            console.error('Error starting recording:', error);
            window.uiController.showError(`Failed to start recording: ${(error as Error).message}`);
            window.appState.set('ui.recording', false);
        }
    }
    
    /**
     * Stop recording with error handling
     */
    stopRecording(): void {
        const currentRecording = window.appState.get('ui.recording');
        
        if (currentRecording) {
            try {
                window.appState.set('ui.recording', false);
                
                if (this.wsManager.sendMessage('stop_recording')) {
                    console.log('Recording stopped');
                    window.appState.set('ui.loadingStates.generatingResponse', true);
                } else {
                    // Rollback state if send failed
                    window.appState.set('ui.recording', true);
                }
            } catch (error) {
                console.error('Error stopping recording:', error);
                window.uiController.showError(`Failed to stop recording: ${(error as Error).message}`);
                window.appState.set('ui.recording', true);
            }
        }
    }
    
    /**
     * Send text message
     */
    sendTextMessage(): void {
        const input = window.uiController.getElement('textChatInput') as HTMLInputElement;
        const sendBtn = window.uiController.getElement('textChatSendBtn') as HTMLButtonElement;
        
        if (!input || !sendBtn) {
            window.uiController.showError('Text chat interface not available');
            return;
        }
        
        const message = input.value.trim();
        if (!message) return;
        
        // Set loading state
        window.appState.set('ui.loadingStates.sendingMessage', true);
        input.disabled = true;
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        try {
            if (this.wsManager.sendMessage('send_text_message', { message: message })) {
                input.value = ''; // Clear input on success
                // Loading state will be cleared when we receive response
            } else {
                window.uiController.showError('Failed to send message - not connected to server');
                // Clear loading state on error
                window.appState.set('ui.loadingStates.sendingMessage', false);
            }
        } catch (error) {
            window.uiController.showError(`Error sending message: ${(error as Error).message}`);
            window.appState.set('ui.loadingStates.sendingMessage', false);
        } finally {
            // Re-enable input and button after a short delay
            setTimeout(() => {
                input.disabled = false;
                sendBtn.disabled = false;
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
                input.focus();
                window.appState.set('ui.loadingStates.sendingMessage', false);
            }, 500);
        }
    }
    
    /**
     * Load available personalities
     */
    loadPersonalities(): void {
        this.wsManager.sendMessage('get_personalities');
    }
    
    /**
     * Populate personality dropdown
     */
    populatePersonalityDropdown(): void {
        const dropdown = window.uiController.getElement('personalityDropdown') as HTMLSelectElement;
        if (!dropdown) return;
        
        const availablePersonalities = window.appState.get('data.availablePersonalities') || [];
        
        dropdown.innerHTML = '<option value="">Choose a personality...</option>';
        
        availablePersonalities.forEach((personality: any) => {
            const option = document.createElement('option');
            option.value = personality.key;
            option.textContent = personality.name;
            dropdown.appendChild(option);
        });
        
        dropdown.addEventListener('change', function() {
            const confirmBtn = window.uiController.getElement('confirmPersonalityBtn') as HTMLButtonElement;
            if (this.value) {
                if (confirmBtn) confirmBtn.disabled = false;
                window.appState.set('data.selectedPersonality', this.value);
            } else {
                if (confirmBtn) confirmBtn.disabled = true;
                window.appState.set('data.selectedPersonality', null);
            }
        });
    }
    
    /**
     * Confirm personality selection
     */
    confirmPersonalitySelection(): void {
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
        
        const confirmBtn = window.uiController.getElement('confirmPersonalityBtn') as HTMLButtonElement;
        const overlay = window.uiController.getElement('personalityOverlay');
        
        try {
            if (confirmBtn) {
                confirmBtn.textContent = 'Starting...';
                confirmBtn.disabled = true;
            }
            
            if (this.wsManager.sendMessage('select_personality', { personality: selectedPersonality })) {
                // Hide overlay immediately when button is clicked
                overlay?.classList.add('hidden');
                window.appState.set('ui.personalityOverlayVisible', false);
            } else {
                // Show overlay again if WebSocket send failed
                overlay?.classList.remove('hidden');
                if (confirmBtn) {
                    confirmBtn.textContent = 'Try Again';
                    confirmBtn.disabled = false;
                }
                window.appState.set('ui.personalityOverlayVisible', true);
            }
        } catch (error) {
            console.error('Error setting personality:', error);
            window.uiController.showError(`Failed to set personality: ${(error as Error).message}`);
            
            overlay?.classList.remove('hidden');
            if (confirmBtn) {
                confirmBtn.textContent = 'Try Again';
                confirmBtn.disabled = false;
            }
            window.appState.set('ui.personalityOverlayVisible', true);
        }
    }
}