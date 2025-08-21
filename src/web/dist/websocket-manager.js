// Terry the Tube - WebSocket Connection Manager
/**
 * WebSocket connection manager with health monitoring and reconnection
 */
export class WebSocketManager {
    constructor() {
        this.healthCheckInterval = null;
    }
    /**
     * Enhanced WebSocket connection using modern JavaScript
     */
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const { hostname, port } = window.location;
        const wsUrl = `${protocol}//${hostname}:${parseInt(port) + 1}`;
        // Update state
        window.appState.update({
            'connection.status': 'connecting',
            'ui.loadingStates.connecting': true
        });
        try {
            const newWs = new WebSocket(wsUrl);
            window.appState.set('connection.ws', newWs);
            // Use arrow functions and destructuring for cleaner code
            newWs.onopen = () => {
                console.log('WebSocket connected successfully');
                window.appState.update({
                    'connection.status': 'connected',
                    'connection.reconnectAttempts': 0,
                    'connection.lastPing': Date.now(),
                    'ui.loadingStates.connecting': false
                });
                this.startHealthCheck();
                window.uiController.showError('Connected to server', 'info');
            };
            newWs.onmessage = ({ data }) => {
                try {
                    const message = JSON.parse(data);
                    this.handleMessage(message);
                    window.appState.set('connection.lastPing', Date.now());
                }
                catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                    window.uiController.showError('Received invalid message from server');
                }
            };
            newWs.onclose = ({ code, reason }) => {
                console.log('WebSocket disconnected:', code, reason);
                const wasConnected = window.appState.get('connection.status') === 'connected';
                window.appState.update({
                    'connection.status': 'disconnected',
                    'connection.ws': null,
                    'ui.loadingStates.connecting': false
                });
                this.stopHealthCheck();
                wasConnected && window.uiController.showError('Disconnected from server');
                this.scheduleReconnect();
            };
            newWs.onerror = (error) => {
                console.error('WebSocket error:', error);
                window.appState.update({
                    'connection.status': 'error',
                    'ui.loadingStates.connecting': false
                });
                window.uiController.showError('Connection error occurred');
            };
        }
        catch (error) {
            console.error('Failed to create WebSocket:', error);
            window.appState.update({
                'connection.status': 'error',
                'ui.loadingStates.connecting': false
            });
            window.uiController.showError(`Failed to establish connection: ${error.message}`);
        }
    }
    /**
     * Schedule reconnection with exponential backoff
     */
    scheduleReconnect() {
        const attempts = window.appState.get('connection.reconnectAttempts');
        const maxAttempts = window.appState.get('connection.maxReconnectAttempts');
        if (attempts < maxAttempts) {
            const newAttempts = attempts + 1;
            const delay = window.appState.get('connection.reconnectDelay') * Math.pow(1.5, newAttempts - 1);
            window.appState.set('connection.reconnectAttempts', newAttempts);
            console.log(`Scheduling reconnection attempt ${newAttempts}/${maxAttempts} in ${delay}ms`);
            setTimeout(() => {
                if (window.appState.get('connection.status') === 'disconnected') {
                    this.connect();
                }
            }, delay);
        }
        else {
            window.uiController.showError('Unable to reconnect - maximum attempts reached');
        }
    }
    /**
     * Connection health monitoring using modern JavaScript
     */
    startHealthCheck() {
        this.healthCheckInterval = window.setInterval(() => {
            const ws = window.appState.get('connection.ws');
            const lastPing = window.appState.get('connection.lastPing');
            const currentTime = Date.now();
            const timeSinceLastPing = currentTime - lastPing;
            if ((ws === null || ws === void 0 ? void 0 : ws.readyState) === WebSocket.OPEN) {
                // Check for stale connection
                if (timeSinceLastPing > 30000) {
                    console.warn('Connection seems stale, sending ping...');
                    this.sendMessage('ping');
                }
                // Determine connection quality using ternary operators
                const quality = timeSinceLastPing > 10000 ? 'poor'
                    : timeSinceLastPing > 5000 ? 'fair'
                        : 'good';
                window.appState.set('connection.quality', quality);
            }
        }, 5000);
    }
    /**
     * Stop health check interval
     */
    stopHealthCheck() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }
    }
    /**
     * Send WebSocket message
     */
    sendMessage(action, data = {}) {
        const ws = window.appState.get('connection.ws');
        if (!ws) {
            console.warn('WebSocket not initialized');
            window.uiController.showError('Not connected to server');
            return false;
        }
        if (ws.readyState === WebSocket.CONNECTING) {
            console.warn('WebSocket still connecting, queuing message...');
            window.uiController.showError('Still connecting, please try again');
            return false;
        }
        if (ws.readyState === WebSocket.OPEN) {
            try {
                const message = {
                    action: action,
                    data: data,
                    timestamp: Date.now()
                };
                ws.send(JSON.stringify(message));
                console.log('Sent WebSocket message:', action);
                return true;
            }
            catch (error) {
                console.error('Error sending WebSocket message:', error);
                window.uiController.showError(`Failed to send message: ${error.message}`);
                return false;
            }
        }
        else {
            console.warn('WebSocket not connected, cannot send message:', action);
            window.uiController.showError('Not connected to server');
            return false;
        }
    }
    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(message) {
        try {
            switch (message.type) {
                case 'state_update':
                    this.updateInterface(message.data);
                    break;
                case 'personalities_list':
                    window.appState.set('data.availablePersonalities', message.data.personalities || []);
                    window.populatePersonalityDropdown();
                    break;
                case 'pong':
                    // Response to ping - update connection quality
                    window.appState.set('connection.lastPing', Date.now());
                    break;
                case 'error':
                    window.uiController.showError(message.data.message || 'Server error occurred');
                    break;
                case 'info':
                    window.uiController.showError(message.data.message || 'Server notification', 'info');
                    break;
                default:
                    console.log('Unknown message type:', message.type, message);
            }
        }
        catch (error) {
            console.error('Error handling WebSocket message:', error);
            window.uiController.showError('Error processing server message');
        }
    }
    /**
     * Update interface from server data
     */
    updateInterface(data) {
        try {
            // Update all state from server data
            window.appState.update({
                'data.currentStatus': data.status || 'Ready to serve beer!',
                'data.messages': data.messages || [],
                'data.personalityInfo': data.personality || null,
                'data.selectedPersonality': data.personality_selected || null,
                'ui.textChatEnabled': data.text_chat_enabled || false,
                'ui.loadingStates.generatingResponse': data.generating_response || false,
                'ui.loadingStates.generatingAudio': data.generating_audio || false
            });
            // Update personality overlay state
            window.appState.set('ui.personalityOverlayVisible', !data.personality_selected);
            // Let the UI controller handle rendering
            window.uiController.updatePersonalityState();
            window.uiController.updateTextChatVisibility();
        }
        catch (error) {
            console.error('Error updating interface:', error);
            window.uiController.showError(`Failed to update interface: ${error.message}`);
        }
    }
}
