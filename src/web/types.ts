// Terry the Tube - TypeScript Type Definitions

// Event handler types (moved up to avoid forward reference issues)
export type StateChangeListener = (newValue: any, oldValue: any, key: string) => void;
export type UnsubscribeFunction = () => void;

// Forward declarations for classes (to avoid circular imports)
interface AppStateInterface {
    get(path: string): any;
    set(path: string, value: any): void;
    update(updates: Record<string, any>): void;
    subscribe(key: string, callback: StateChangeListener): UnsubscribeFunction;
}

interface UIControllerInterface {
    updateConnectionStatus(): void;
    updateRecordingState(): void;
    updateLoadingStates(): void;
    updateStatus(): void;
    updateMessages(): void;
    updatePersonalityState(): void;
    updateTextChatVisibility(): void;
    showError(message: string, type?: 'error' | 'info'): void;
    removeError(errorId: number): void;
    getElement(key: ElementKey): HTMLElement | undefined;
    resetPersonalitySelection(): void;
}

interface WebSocketManagerInterface {
    connect(): void;
    sendMessage(action: string, data?: Record<string, any>): boolean;
}

interface AppControllerInterface {
    init(): void;
    startRecording(): void;
    stopRecording(): void;
    sendTextMessage(): void;
    loadPersonalities(): void;
    populatePersonalityDropdown(): void;
    confirmPersonalitySelection(): void;
}

// Global window extensions
declare global {
    interface Window {
        startRecording: () => void;
        stopRecording: () => void;
        populatePersonalityDropdown: () => void;
        appState: AppStateInterface;
        uiController: UIControllerInterface;
        appController: AppControllerInterface;
    }
}

// Connection related types
export interface ConnectionState {
    status: 'connected' | 'connecting' | 'disconnected' | 'error';
    ws: WebSocket | null;
    reconnectAttempts: number;
    maxReconnectAttempts: number;
    reconnectDelay: number;
    quality: 'good' | 'fair' | 'poor' | 'unknown';
    lastPing: number | null;
}

// UI state types
export interface LoadingStates {
    connecting: boolean;
    generatingResponse: boolean;
    generatingAudio: boolean;
    sendingMessage: boolean;
}

export interface ErrorInfo {
    id: number;
    message: string;
    type: 'error' | 'info';
    timestamp: Date;
}

export interface UIState {
    recording: boolean;
    textChatEnabled: boolean;
    personalityOverlayVisible: boolean;
    lastMessageCount: number;
    lastStatus: string;
    errors: ErrorInfo[];
    loadingStates: LoadingStates;
}

// Message types
export interface Message {
    sender: string;
    message: string;
    is_ai: boolean;
    timestamp: string;
    show_immediately: boolean;
}

// Personality types
export interface PersonalityInfo {
    key: string;
    name: string;
    short_name?: string;
}

// App data types
export interface AppData {
    availablePersonalities: PersonalityInfo[];
    selectedPersonality: string | null;
    messages: Message[];
    currentStatus: string;
    personalityInfo: PersonalityInfo | null;
}

// Complete app state
export interface AppStateData {
    connection: ConnectionState;
    ui: UIState;
    data: AppData;
}

// WebSocket message types
export interface WebSocketMessage {
    type: 'state_update' | 'personalities_list' | 'pong' | 'error' | 'info';
    data: any;
    timestamp?: number;
}

export interface StateUpdateData {
    status?: string;
    messages?: Message[];
    personality?: PersonalityInfo;
    personality_selected?: boolean;
    text_chat_enabled?: boolean;
    generating_response?: boolean;
    generating_audio?: boolean;
}


// DOM element cache types
export type ElementKey = 
    | 'connectionIndicator' 
    | 'connectionText' 
    | 'connectionDot'
    | 'recordingIndicator' 
    | 'status' 
    | 'messages' 
    | 'responseLoading'
    | 'ttsLoading' 
    | 'personalityOverlay' 
    | 'personalityDisplay' 
    | 'personalityDropdown'
    | 'confirmPersonalityBtn' 
    | 'textChatContainer' 
    | 'textChatInput' 
    | 'textChatSendBtn'
    | 'talkButton';

// Action types for message callback
export type ActionType = 
    | 'start_recording' 
    | 'stop_recording' 
    | 'send_text_message' 
    | 'change_personality';

export interface ActionData {
    message?: string;
    personality?: string;
    [key: string]: any;
}

// Export statement for module resolution
export {};