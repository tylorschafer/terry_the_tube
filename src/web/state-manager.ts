// Terry the Tube - Centralized State Management System

import { AppStateData, StateChangeListener, UnsubscribeFunction } from './types';

/**
 * Centralized state management system with reactive updates
 */
export class AppState {
    private state: AppStateData;
    private listeners: Map<string, Set<StateChangeListener>>;
    private renderQueue: Set<string>;
    private renderScheduled: boolean;

    constructor() {
        // Initialize with proper typing
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
    
    /**
     * Subscribe to state changes
     */
    subscribe(key: string, callback: StateChangeListener): UnsubscribeFunction {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        this.listeners.get(key)!.add(callback);
        
        // Return unsubscribe function
        return () => {
            const callbacks = this.listeners.get(key);
            if (callbacks) {
                callbacks.delete(callback);
            }
        };
    }
    
    /**
     * Notify listeners of state changes
     */
    private notify(key: string, newValue: any, oldValue: any): void {
        const callbacks = this.listeners.get(key);
        if (callbacks) {
            callbacks.forEach(callback => callback(newValue, oldValue, key));
        }
    }
    
    /**
     * Get state value by path
     */
    get(path: string): any {
        return this.getNestedValue(this.state, path);
    }
    
    /**
     * Set state value with change notification
     */
    set(path: string, value: any): void {
        const oldValue = this.get(path);
        this.setNestedValue(this.state, path, value);
        this.notify(path, value, oldValue);
        
        // Schedule render if needed
        this.scheduleRender(path);
    }
    
    /**
     * Update multiple state values atomically
     */
    update(updates: Record<string, any>): void {
        const changes = Object.entries(updates).map(([path, value]) => {
            const oldValue = this.get(path);
            this.setNestedValue(this.state, path, value);
            return { path, value, oldValue };
        });
        
        // Notify all changes using forEach with destructuring
        changes.forEach(({ path, value, oldValue }) => {
            this.notify(path, value, oldValue);
            this.scheduleRender(path);
        });
    }
    
    /**
     * Helper to get nested object values using optional chaining
     */
    private getNestedValue(obj: any, path: string): any {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    }
    
    /**
     * Helper to set nested object values using ES6+ features
     */
    private setNestedValue(obj: any, path: string, value: any): void {
        const keys = path.split('.');
        const lastKey = keys.pop()!;
        const target = keys.reduce((current, key) => {
            // Use logical nullish assignment
            current[key] ??= {};
            return current[key];
        }, obj);
        target[lastKey] = value;
    }
    
    /**
     * Schedule UI renders to avoid excessive DOM updates
     */
    private scheduleRender(path: string): void {
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
    
    /**
     * Process queued renders using Set and array methods
     */
    private processRenderQueue(): void {
        // Group renders by component for efficiency using Set and map
        const components = new Set(
            [...this.renderQueue].map(path => path.split('.')[0])
        );
        
        components.forEach(component => this.renderComponent(component));
    }
    
    /**
     * Render specific components using object map for cleaner code
     */
    private renderComponent(component: string): void {
        const componentActions: Record<string, () => void> = {
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