export class AppState {
    constructor() {
        this.state = {
            connection: {
                status: 'disconnected',
                ws: null,
                reconnectAttempts: 0,
                maxReconnectAttempts: 5,
                reconnectDelay: 1000,
                quality: 'unknown',
                lastPing: null
            },
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
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        this.listeners.get(key).add(callback);
        return () => {
            const callbacks = this.listeners.get(key);
            if (callbacks) {
                callbacks.delete(callback);
            }
        };
    }
    notify(key, newValue, oldValue) {
        const callbacks = this.listeners.get(key);
        if (callbacks) {
            callbacks.forEach(callback => callback(newValue, oldValue, key));
        }
    }
    get(path) {
        return this.getNestedValue(this.state, path);
    }
    set(path, value) {
        const oldValue = this.get(path);
        this.setNestedValue(this.state, path, value);
        this.notify(path, value, oldValue);
        this.scheduleRender(path);
    }
    update(updates) {
        const changes = Object.entries(updates).map(([path, value]) => {
            const oldValue = this.get(path);
            this.setNestedValue(this.state, path, value);
            return { path, value, oldValue };
        });
        changes.forEach(({ path, value, oldValue }) => {
            this.notify(path, value, oldValue);
            this.scheduleRender(path);
        });
    }
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    }
    setNestedValue(obj, path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        const target = keys.reduce((current, key) => {
            current[key] ?? (current[key] = {});
            return current[key];
        }, obj);
        target[lastKey] = value;
    }
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
    processRenderQueue() {
        const components = new Set([...this.renderQueue].map(path => path.split('.')[0]));
        components.forEach(component => this.renderComponent(component));
    }
    renderComponent(component) {
        const componentActions = {
            connection: () => window.uiController.updateConnectionStatus(),
            ui: () => {
                if (this.renderQueue.has('ui.recording')) {
                    window.uiController.updateRecordingState();
                }
                if (this.renderQueue.has('ui.loadingStates')) {
                    window.uiController.updateLoadingStates();
                }
            },
            data: () => {
                if (this.renderQueue.has('data.messages')) {
                    window.uiController.updateMessages();
                }
                if (this.renderQueue.has('data.currentStatus')) {
                    window.uiController.updateStatus();
                }
            }
        };
        componentActions[component]?.();
    }
}
