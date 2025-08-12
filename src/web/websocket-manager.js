// Terry the Tube - WebSocket Connection Manager

class WebSocketManager {
    constructor() {
        this.healthCheckInterval = null;
    }
    
    // Enhanced WebSocket connection and messaging
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.hostname}:${parseInt(window.location.port) + 1}`;
        
        // Update state
        appState.update({
            'connection.status': 'connecting',
            'ui.loadingStates.connecting': true
        });
        
        try {
            const newWs = new WebSocket(wsUrl);
            appState.set('connection.ws', newWs);
            
            newWs.onopen = (event) => {
                console.log('WebSocket connected successfully');
                appState.update({
                    'connection.status': 'connected',
                    'connection.reconnectAttempts': 0,
                    'connection.lastPing': Date.now(),
                    'ui.loadingStates.connecting': false
                });
                
                // Start connection health monitoring
                this.startHealthCheck();
                
                uiController.showError('Connected to server', 'info');
            };
            
            newWs.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                    
                    // Update last ping time
                    appState.set('connection.lastPing', Date.now());
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                    uiController.showError('Received invalid message from server');
                }
            };
            
            newWs.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason);
                const wasConnected = appState.get('connection.status') === 'connected';
                
                appState.update({
                    'connection.status': 'disconnected',
                    'connection.ws': null,
                    'ui.loadingStates.connecting': false
                });
                
                this.stopHealthCheck();
                
                if (wasConnected) {
                    uiController.showError('Disconnected from server');
                }
                
                // Attempt to reconnect with exponential backoff
                this.scheduleReconnect();
            };
            
            newWs.onerror = (error) => {
                console.error('WebSocket error:', error);
                appState.update({
                    'connection.status': 'error',
                    'ui.loadingStates.connecting': false
                });
                uiController.showError('Connection error occurred');
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            appState.update({
                'connection.status': 'error',
                'ui.loadingStates.connecting': false
            });
            uiController.showError('Failed to establish connection: ' + error.message);
        }
    }
    
    // Schedule reconnection with exponential backoff
    scheduleReconnect() {
        const attempts = appState.get('connection.reconnectAttempts');
        const maxAttempts = appState.get('connection.maxReconnectAttempts');
        
        if (attempts < maxAttempts) {
            const newAttempts = attempts + 1;
            const delay = appState.get('connection.reconnectDelay') * Math.pow(1.5, newAttempts - 1);
            
            appState.set('connection.reconnectAttempts', newAttempts);
            
            console.log(`Scheduling reconnection attempt ${newAttempts}/${maxAttempts} in ${delay}ms`);
            setTimeout(() => {
                if (appState.get('connection.status') === 'disconnected') {
                    this.connect();
                }
            }, delay);
        } else {
            uiController.showError('Unable to reconnect - maximum attempts reached');
        }
    }
    
    // Connection health monitoring
    startHealthCheck() {
        this.healthCheckInterval = setInterval(() => {
            const ws = appState.get('connection.ws');
            const lastPing = appState.get('connection.lastPing');
            const currentTime = Date.now();
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                // Check if we haven't received any messages in the last 30 seconds
                if (currentTime - lastPing > 30000) {
                    console.warn('Connection seems stale, sending ping...');
                    this.sendMessage('ping');
                }
                
                // Update connection quality based on response times
                const timeSinceLastPing = currentTime - lastPing;
                let quality = 'good';
                if (timeSinceLastPing > 10000) quality = 'poor';
                else if (timeSinceLastPing > 5000) quality = 'fair';
                
                appState.set('connection.quality', quality);
            }
        }, 5000); // Check every 5 seconds
    }
    
    // Stop health check
    stopHealthCheck() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }
    }
    
    // Send WebSocket message
    sendMessage(action, data = {}) {
        const ws = appState.get('connection.ws');
        
        if (!ws) {
            console.warn('WebSocket not initialized');
            uiController.showError('Not connected to server');
            return false;
        }
        
        if (ws.readyState === WebSocket.CONNECTING) {
            console.warn('WebSocket still connecting, queuing message...');
            // Could implement message queuing here
            uiController.showError('Still connecting, please try again');
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
            } catch (error) {
                console.error('Error sending WebSocket message:', error);
                uiController.showError('Failed to send message: ' + error.message);
                return false;
            }
        } else {
            console.warn('WebSocket not connected, cannot send message:', action);
            uiController.showError('Not connected to server');
            return false;
        }
    }
    
    // Handle incoming messages
    handleMessage(message) {
        try {
            switch (message.type) {
                case 'state_update':
                    this.updateInterface(message.data);
                    break;
                case 'personalities_list':
                    appState.set('data.availablePersonalities', message.data.personalities || []);
                    window.populatePersonalityDropdown();
                    break;
                case 'pong':
                    // Response to ping - update connection quality
                    appState.set('connection.lastPing', Date.now());
                    break;
                case 'error':
                    uiController.showError(message.data.message || 'Server error occurred');
                    break;
                case 'info':
                    uiController.showError(message.data.message || 'Server notification', 'info');
                    break;
                default:
                    console.log('Unknown message type:', message.type, message);
            }
        } catch (error) {
            console.error('Error handling WebSocket message:', error);
            uiController.showError('Error processing server message');
        }
    }
    
    // Update interface from server data
    updateInterface(data) {
        try {
            // Update all state from server data
            appState.update({
                'data.currentStatus': data.status || 'Ready to serve beer!',
                'data.messages': data.messages || [],
                'data.personalityInfo': data.personality || null,
                'data.selectedPersonality': data.personality_selected || null,
                'ui.textChatEnabled': data.text_chat_enabled || false,
                'ui.loadingStates.generatingResponse': data.generating_response || false,
                'ui.loadingStates.generatingAudio': data.generating_audio || false
            });
            
            // Update personality overlay state
            appState.set('ui.personalityOverlayVisible', !data.personality_selected);
            
            // Let the UI controller handle rendering
            uiController.updatePersonalityState();
            uiController.updateTextChatVisibility();
            
        } catch (error) {
            console.error('Error updating interface:', error);
            uiController.showError('Failed to update interface: ' + error.message);
        }
    }
}

// Export for use in main template
window.WebSocketManager = WebSocketManager;