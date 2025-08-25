// Terry the Tube - Simple Polling Manager (replaces WebSocket)
class PollingManager {
    constructor() {
        this.pollInterval = null;
        this.pollRate = 1000; // Poll every 1 second
        this.connected = false;
    }

    start() {
        console.log('Starting polling manager...');
        this.connected = true;
        window.appState.set('connection.status', 'connected');
        
        // Load personalities immediately
        this.loadPersonalities();
        
        // Start polling for state updates
        this.pollInterval = setInterval(() => {
            this.pollState();
        }, this.pollRate);
        
        console.log('Polling manager started');
    }

    stop() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
        this.connected = false;
        window.appState.set('connection.status', 'disconnected');
        console.log('Polling manager stopped');
    }

    async pollState() {
        try {
            const response = await fetch('/api/state');
            if (response.ok) {
                const state = await response.json();
                
                // Update app state with server data
                window.appState.update({
                    'data.currentStatus': state.status,
                    'data.messages': state.messages,
                    'data.personalityInfo': state.personality,
                    'ui.loadingStates.generatingResponse': state.generating_response,
                    'ui.loadingStates.generatingAudio': state.generating_audio,
                    'ui.textChatEnabled': state.text_chat_enabled || false,
                    'ui.textOnlyMode': state.text_only_mode || false,
                    'ui.personalityOverlayVisible': !state.personality_selected
                });
                
                // Update connection status if not already connected
                if (!this.connected) {
                    this.connected = true;
                    window.appState.set('connection.status', 'connected');
                }
            } else {
                console.error('Failed to poll state:', response.status);
                if (this.connected) {
                    this.connected = false;
                    window.appState.set('connection.status', 'disconnected');
                }
            }
        } catch (error) {
            console.error('Error polling state:', error);
            if (this.connected) {
                this.connected = false;
                window.appState.set('connection.status', 'disconnected');
            }
        }
    }

    async loadPersonalities() {
        try {
            const response = await fetch('/api/personalities');
            if (response.ok) {
                const data = await response.json();
                window.appState.set('data.availablePersonalities', data.personalities);
                console.log('Personalities loaded:', data.personalities);
            } else {
                console.error('Failed to load personalities:', response.status);
            }
        } catch (error) {
            console.error('Error loading personalities:', error);
        }
    }

    async sendAction(action, data = {}) {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: action,
                    data: data
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log(`Action ${action} successful:`, result);
                
                // Immediately poll for state update after action
                setTimeout(() => this.pollState(), 100);
                
                return true;
            } else {
                console.error(`Action ${action} failed:`, response.status);
                return false;
            }
        } catch (error) {
            console.error(`Error sending action ${action}:`, error);
            return false;
        }
    }

    // Public methods that match WebSocket interface
    sendMessage(action, data = {}) {
        return this.sendAction(action, data);
    }
}