// Terry the Tube - Centralized State Management System

class AppState {
    constructor() {
        this.state = {
            // Connection state
            connection: {
                status: 'disconnected',
                ws: null,
                reconnectAttempts: 0,
                maxReconnectAttempts: 5,
                reconnectDelay: 1000,
                quality: 'unknown',
                lastPing: null
            },
            
            // UI state
            ui: {
                recording: false,
                textChatEnabled: false,
                personalityOverlayVisible: true,
                lastMessageCount: 0,
                lastStatus: '',
                errors: [],
                loadingStates: {
                    connecting: false,
                    generatingResponse: false,
                    generatingAudio: false,
                    sendingMessage: false
                }
            },
            
            // App data
            data: {
                availablePersonalities: [],
                selectedPersonality: null,
                messages: [],
                currentStatus: 'Ready to serve beer!',
                personalityInfo: null
            }
        };
        
        this.listeners = new Map();
        this.renderQueue = new Set();
        this.renderScheduled = false;
    }
    
    // Subscribe to state changes
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        this.listeners.get(key).add(callback);
        
        // Return unsubscribe function
        return () => {
            const callbacks = this.listeners.get(key);
            if (callbacks) {
                callbacks.delete(callback);
            }
        };
    }
    
    // Notify listeners of state changes
    notify(key, newValue, oldValue) {
        const callbacks = this.listeners.get(key);
        if (callbacks) {
            callbacks.forEach(callback => callback(newValue, oldValue, key));
        }
    }
    
    // Get state value
    get(path) {
        return this.getNestedValue(this.state, path);
    }
    
    // Set state value with change notification
    set(path, value) {
        const oldValue = this.get(path);
        this.setNestedValue(this.state, path, value);
        this.notify(path, value, oldValue);
        
        // Schedule render if needed
        this.scheduleRender(path);
    }
    
    // Update multiple state values atomically
    update(updates) {
        const changes = [];
        
        Object.entries(updates).forEach(([path, value]) => {
            const oldValue = this.get(path);
            this.setNestedValue(this.state, path, value);
            changes.push({ path, value, oldValue });
        });
        
        // Notify all changes
        changes.forEach(({ path, value, oldValue }) => {
            this.notify(path, value, oldValue);
            this.scheduleRender(path);
        });
    }
    
    // Helper to get nested object values
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    }
    
    // Helper to set nested object values
    setNestedValue(obj, path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        const target = keys.reduce((current, key) => {
            if (!current[key]) current[key] = {};
            return current[key];
        }, obj);
        target[lastKey] = value;
    }
    
    // Schedule UI renders to avoid excessive DOM updates
    scheduleRender(path) {
        this.renderQueue.add(path);
        
        if (!this.renderScheduled) {
            this.renderScheduled = true;
            requestAnimationFrame(() => {
                this.processRenderQueue();
                this.renderQueue.clear();
                this.renderScheduled = false;
            });
        }
    }
    
    // Process queued renders
    processRenderQueue() {
        // Group renders by component for efficiency
        const components = new Set();
        
        this.renderQueue.forEach(path => {
            const component = path.split('.')[0];
            components.add(component);
        });
        
        components.forEach(component => {
            this.renderComponent(component);
        });
    }
    
    // Render specific components
    renderComponent(component) {
        switch (component) {
            case 'connection':
                uiController.updateConnectionStatus();
                break;
            case 'ui':
                if (this.renderQueue.has('ui.recording')) {
                    uiController.updateRecordingState();
                }
                if (this.renderQueue.has('ui.loadingStates')) {
                    uiController.updateLoadingStates();
                }
                break;
            case 'data':
                if (this.renderQueue.has('data.messages')) {
                    uiController.updateMessages();
                }
                if (this.renderQueue.has('data.currentStatus')) {
                    uiController.updateStatus();
                }
                break;
        }
    }
}

// Export for use in main template
window.AppState = AppState;