"""
HTML Templates for Terry the Tube Web Interface
"""


def get_main_html_template(text_only_mode=False):
    """Get the main HTML template with optional text-only mode"""
    
    # Conditionally include recording elements
    recording_button_html = ""
    recording_indicator_html = ""
    recording_js = ""
    
    if not text_only_mode:
        recording_button_html = '''
            <div class="controls">
                <button class="talk-button" id="talkButton" 
                        onmousedown="startRecording()" 
                        onmouseup="stopRecording()"
                        ontouchstart="startRecording()" 
                        ontouchend="stopRecording()">
                    <i class="fas fa-microphone"></i>
                    <span>Hold to Talk</span>
                </button>
            </div>
        '''
        
        recording_indicator_html = '''
        <div class="recording-indicator" id="recordingIndicator">
            <div class="recording-dot"></div>
            <span>Recording...</span>
        </div>
        '''
        
        recording_js = '''
            function startRecording() {
                const currentRecording = appState.get('ui.recording');
                const connectionStatus = appState.get('connection.status');
                
                if (connectionStatus !== 'connected') {
                    uiController.showError('Cannot record - not connected to server');
                    return;
                }
                
                if (!currentRecording) {
                    try {
                        appState.set('ui.recording', true);
                        
                        if (sendWebSocketMessage('start_recording')) {
                            console.log('Recording started');
                        } else {
                            // Rollback state if send failed
                            appState.set('ui.recording', false);
                        }
                    } catch (error) {
                        console.error('Error starting recording:', error);
                        uiController.showError('Failed to start recording: ' + error.message);
                        appState.set('ui.recording', false);
                    }
                }
            }
            
            function stopRecording() {
                const currentRecording = appState.get('ui.recording');
                
                if (currentRecording) {
                    try {
                        appState.set('ui.recording', false);
                        
                        if (sendWebSocketMessage('stop_recording')) {
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
        '''
    
    template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Terry the Tube - AI Beer Dispenser</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            :root {
                --bg-primary: #0a0a0b;
                --bg-secondary: #1a1a1f;
                --bg-tertiary: #252530;
                --accent-beer: #ffa500;
                --accent-green: #00d4aa;
                --accent-red: #ff5757;
                --text-primary: #ffffff;
                --text-secondary: #b4b4b8;
                --text-muted: #777780;
                --border: #333340;
                --shadow: rgba(0, 0, 0, 0.5);
                --glow-beer: rgba(255, 165, 0, 0.3);
                --glow-green: rgba(0, 212, 170, 0.3);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            .personality-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 2000;
                opacity: 1;
                transition: opacity 0.3s ease;
            }
            
            .personality-overlay.hidden {
                opacity: 0;
                pointer-events: none;
            }
            
            .personality-modal {
                background: var(--bg-secondary);
                border: 2px solid var(--accent-beer);
                border-radius: 24px;
                padding: 3rem;
                max-width: 600px;
                width: 90%;
                text-align: center;
                box-shadow: 0 20px 60px var(--shadow);
                position: relative;
                animation: modalSlideIn 0.4s ease-out;
            }
            
            @keyframes modalSlideIn {
                from {
                    opacity: 0;
                    transform: translateY(-50px) scale(0.9);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }
            
            .personality-modal h2 {
                font-size: 2rem;
                margin-bottom: 1rem;
                background: linear-gradient(45deg, var(--accent-beer), #ffcc44);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .personality-modal p {
                color: var(--text-secondary);
                margin-bottom: 2rem;
                font-size: 1.1rem;
                line-height: 1.5;
            }
            
            .personality-dropdown {
                width: 100%;
                padding: 1rem;
                font-size: 1.1rem;
                background: var(--bg-tertiary);
                color: var(--text-primary);
                border: 2px solid var(--border);
                border-radius: 12px;
                margin-bottom: 2rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .personality-dropdown:hover,
            .personality-dropdown:focus {
                border-color: var(--accent-beer);
                box-shadow: 0 0 20px var(--glow-beer);
                outline: none;
            }
            
            .personality-dropdown option {
                background: var(--bg-tertiary);
                color: var(--text-primary);
                padding: 0.5rem;
            }
            
            .confirm-btn {
                width: 100%;
                height: 60px;
                font-size: 1.2rem;
                font-weight: 600;
                background: linear-gradient(45deg, var(--accent-beer), #cc8800);
                color: var(--bg-primary);
                border: none;
                border-radius: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .confirm-btn:hover {
                background: linear-gradient(45deg, #cc8800, var(--accent-beer));
                transform: translateY(-2px);
                box-shadow: 0 8px 30px var(--glow-beer);
            }
            
            .confirm-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            
            body {
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
                background: linear-gradient(135deg, var(--bg-primary) 0%, #1a1a2e 100%);
                color: var(--text-primary);
                min-height: 100vh;
                overflow-x: hidden;
            }
            
            .background-pattern {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 50%, var(--glow-beer) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, var(--glow-green) 0%, transparent 50%),
                    radial-gradient(circle at 40% 80%, rgba(255, 87, 87, 0.1) 0%, transparent 50%);
                z-index: -1;
                animation: pulse 4s ease-in-out infinite alternate;
            }
            
            @keyframes pulse {
                from { opacity: 0.3; }
                to { opacity: 0.6; }
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            .header {
                text-align: center;
                margin-bottom: 3rem;
                position: relative;
            }
            
            .title {
                font-size: clamp(2.5rem, 6vw, 4rem);
                font-weight: 900;
                background: linear-gradient(45deg, var(--accent-beer), #ffcc44);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-shadow: 0 0 30px var(--glow-beer);
                margin-bottom: 1rem;
                letter-spacing: 0.1em;
            }
            
            .subtitle {
                font-size: 1.2rem;
                color: var(--text-secondary);
                font-weight: 300;
                margin-bottom: 2rem;
            }
            
            .status-card {
                background: var(--bg-secondary);
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 1.5rem;
                margin-bottom: 2rem;
                text-align: center;
                box-shadow: 0 8px 32px var(--shadow);
                backdrop-filter: blur(10px);
                position: relative;
                overflow: hidden;
            }
            
            .status-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
                animation: shimmer 3s ease-in-out infinite;
            }
            
            @keyframes shimmer {
                0% { left: -100%; }
                100% { left: 100%; }
            }
            
            .status {
                font-size: 1.3rem;
                font-weight: 600;
                color: var(--accent-green);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            }
            
            .status i {
                font-size: 1.5rem;
            }
            
            .chat-container {
                flex: 1;
                background: var(--bg-secondary);
                border-radius: 24px;
                border: 1px solid var(--border);
                overflow: hidden;
                box-shadow: 0 20px 60px var(--shadow);
                backdrop-filter: blur(20px);
                margin-bottom: 2rem;
                display: flex;
                flex-direction: column;
            }
            
            .chat-header {
                background: var(--bg-tertiary);
                padding: 1.5rem;
                border-bottom: 1px solid var(--border);
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .chat-avatar {
                width: 50px;
                height: 50px;
                background: linear-gradient(45deg, var(--accent-beer), #ffcc44);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                font-weight: bold;
                color: var(--bg-primary);
            }
            
            .chat-info h3 {
                font-size: 1.2rem;
                margin-bottom: 0.25rem;
            }
            
            .chat-info p {
                color: var(--text-muted);
                font-size: 0.9rem;
            }
            
            .messages {
                flex: 1;
                padding: 1.5rem;
                overflow-y: auto;
                max-height: 500px;
                scrollbar-width: thin;
                scrollbar-color: var(--accent-beer) var(--bg-tertiary);
            }
            
            .messages::-webkit-scrollbar {
                width: 8px;
            }
            
            .messages::-webkit-scrollbar-track {
                background: var(--bg-tertiary);
                border-radius: 4px;
            }
            
            .messages::-webkit-scrollbar-thumb {
                background: var(--accent-beer);
                border-radius: 4px;
            }
            
            .message {
                margin-bottom: 1.5rem;
                display: flex;
                flex-direction: column;
                animation: fadeIn 0.3s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .message-bubble {
                max-width: 80%;
                padding: 1rem 1.5rem;
                border-radius: 20px;
                font-size: 1rem;
                line-height: 1.5;
                position: relative;
            }
            
            .ai-message .message-bubble {
                background: linear-gradient(135deg, var(--accent-beer), #cc8800);
                color: var(--bg-primary);
                align-self: flex-start;
                border-bottom-left-radius: 8px;
                box-shadow: 0 4px 20px var(--glow-beer);
            }
            
            .user-message .message-bubble {
                background: linear-gradient(135deg, var(--accent-green), #00a085);
                color: var(--text-primary);
                align-self: flex-end;
                border-bottom-right-radius: 8px;
                box-shadow: 0 4px 20px var(--glow-green);
            }
            
            .message-info {
                font-size: 0.8rem;
                color: var(--text-muted);
                margin-top: 0.5rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .ai-message .message-info {
                align-self: flex-start;
            }
            
            .user-message .message-info {
                align-self: flex-end;
            }
            
            .controls {
                background: var(--bg-secondary);
                padding: 2rem;
                border-radius: 20px;
                border: 1px solid var(--border);
                box-shadow: 0 8px 32px var(--shadow);
                backdrop-filter: blur(10px);
            }
            
            .talk-button {
                width: 100%;
                height: 80px;
                font-size: 1.2rem;
                font-weight: 600;
                background: linear-gradient(45deg, var(--accent-green), #00b894);
                color: var(--text-primary);
                border: none;
                border-radius: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 8px 30px var(--glow-green);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 1rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                position: relative;
                overflow: hidden;
            }
            
            .talk-button::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                transition: all 0.5s ease;
            }
            
            .talk-button:hover::before {
                width: 300px;
                height: 300px;
            }
            
            .talk-button:active {
                background: linear-gradient(45deg, var(--accent-red), #d63031);
                box-shadow: 0 8px 30px rgba(255, 87, 87, 0.4);
                transform: translateY(2px);
            }
            
            .talk-button i {
                font-size: 1.5rem;
                z-index: 1;
            }
            
            .talk-button span {
                z-index: 1;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 1rem;
                }
                
                .title {
                    font-size: 2.5rem;
                }
                
                .message-bubble {
                    max-width: 90%;
                    font-size: 0.9rem;
                }
                
                .talk-button {
                    height: 70px;
                    font-size: 1rem;
                }
                
                .chat-container {
                    margin-bottom: 1rem;
                }
            }
            
            .recording-indicator {
                position: fixed;
                top: 2rem;
                right: 2rem;
                background: var(--accent-red);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 25px;
                font-weight: 600;
                display: none;
                align-items: center;
                gap: 0.5rem;
                z-index: 1000;
                box-shadow: 0 4px 20px rgba(255, 87, 87, 0.4);
            }
            
            .connection-indicator {
                position: fixed;
                top: 2rem;
                left: 2rem;
                padding: 0.5rem 1rem;
                border-radius: 25px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                z-index: 1000;
                font-size: 0.85rem;
                transition: all 0.3s ease;
            }
            
            .connection-indicator.connected {
                background: var(--accent-green);
                color: white;
                box-shadow: 0 4px 20px var(--glow-green);
            }
            
            .connection-indicator.connecting {
                background: var(--accent-beer);
                color: var(--bg-primary);
                box-shadow: 0 4px 20px var(--glow-beer);
                animation: pulse 2s ease-in-out infinite;
            }
            
            .connection-indicator.disconnected {
                background: var(--accent-red);
                color: white;
                box-shadow: 0 4px 20px rgba(255, 87, 87, 0.4);
            }
            
            .recording-dot {
                width: 8px;
                height: 8px;
                background: white;
                border-radius: 50%;
                animation: blink 1s infinite;
            }
            
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0.3; }
            }
            
            .tts-loading,
            .response-loading {
                display: none;
                padding: 1rem;
                text-align: center;
                background: var(--bg-tertiary);
                border-radius: 16px;
                margin: 1rem 0;
                border: 1px solid var(--border);
                animation: fadeIn 0.3s ease-out;
            }
            
            .tts-loading.show,
            .response-loading.show {
                display: block;
            }
            
            .spinner {
                display: inline-block;
                width: 24px;
                height: 24px;
                border: 3px solid var(--border);
                border-top: 3px solid var(--accent-beer);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 0.5rem;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .tts-loading-text,
            .response-loading-text {
                color: var(--text-secondary);
                font-size: 0.9rem;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            }
            
            .message.pending {
                opacity: 0;
                transform: translateY(10px);
                transition: all 0.3s ease-out;
            }
            
            .message.show {
                opacity: 1;
                transform: translateY(0);
            }
            
            /* Text Chat Styles */
            .text-chat-container {
                margin-top: 1rem;
                animation: fadeIn 0.3s ease-out;
            }
            
            .text-chat-input-group {
                display: flex;
                gap: 0.5rem;
                align-items: stretch;
            }
            
            .text-chat-input {
                flex: 1;
                padding: 1rem;
                font-size: 1rem;
                background: var(--bg-tertiary);
                color: var(--text-primary);
                border: 2px solid var(--border);
                border-radius: 12px;
                outline: none;
                transition: all 0.3s ease;
            }
            
            .text-chat-input::placeholder {
                color: var(--text-muted);
            }
            
            .text-chat-input:focus {
                border-color: var(--accent-green);
                box-shadow: 0 0 20px var(--glow-green);
            }
            
            .text-chat-send-btn {
                width: 60px;
                height: 60px;
                background: linear-gradient(45deg, var(--accent-green), #00b894);
                color: var(--text-primary);
                border: none;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
            }
            
            .text-chat-send-btn:hover {
                background: linear-gradient(45deg, #00b894, var(--accent-green));
                transform: translateY(-2px);
                box-shadow: 0 8px 25px var(--glow-green);
            }
            
            .text-chat-send-btn:active {
                transform: translateY(0);
            }
            
            .text-chat-send-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
        </style>
    </head>
    <body>
        <div class="background-pattern"></div>
        {recording_indicator_html}
        
        <!-- Connection Status Indicator -->
        <div class="connection-indicator disconnected" id="connectionIndicator">
            <div class="recording-dot" id="connectionDot"></div>
            <span id="connectionText">Disconnected</span>
        </div>
        
        <!-- Personality Selection Overlay -->
        <div class="personality-overlay" id="personalityOverlay">
            <div class="personality-modal">
                <h2>Select Terry's Personality</h2>
                <p>Choose how Terry will interact with you today. Each personality offers a unique beer-dispensing experience!</p>
                
                <select class="personality-dropdown" id="personalityDropdown">
                    <option value="">Loading personalities...</option>
                </select>
                
                <button class="confirm-btn" id="confirmPersonalityBtn" disabled>
                    Start Your Beer Journey
                </button>
            </div>
        </div>
        
        <div class="container">
            <div class="header">
                <h1 class="title">TERRY THE TUBE</h1>
                <p class="subtitle">Your AI Beer Dispenser</p>
            </div>
            
            <div class="status-card">
                <div class="status" id="status">
                    <i class="fas fa-beer"></i>
                    <span>Ready to serve beer!</span>
                </div>
            </div>
            
            <div class="chat-container">
                <div class="chat-header">
                    <div class="chat-avatar">T</div>
                    <div class="chat-info">
                        <h3>Terry</h3>
                        <p id="personalityDisplay">Your AI Bartender</p>
                    </div>
                </div>
                <div class="messages" id="messages">
                    <!-- Messages will be added dynamically -->
                </div>
                <div class="response-loading" id="responseLoading">
                    <div class="response-loading-text">
                        <div class="spinner"></div>
                        <span>Generating response...</span>
                    </div>
                </div>
                <div class="tts-loading" id="ttsLoading">
                    <div class="tts-loading-text">
                        <div class="spinner"></div>
                        <span>Generating voice...</span>
                    </div>
                </div>
                <div class="tts-loading" id="responseLoading">
                    <div class="tts-loading-text">
                        <div class="spinner"></div>
                        <span>Generating response...</span>
                    </div>
                </div>
            </div>
            
            <div class="controls">
                <button class="talk-button" id="talkButton" 
                        onmousedown="startRecording()" 
                        onmouseup="stopRecording()"
                        ontouchstart="startRecording()" 
                        ontouchend="stopRecording()">
                    <i class="fas fa-microphone"></i>
                    <span>Hold to Talk</span>
                </button>
                
                <!-- Text Chat Interface -->
                <div class="text-chat-container" id="textChatContainer" style="display: none;">
                    <div class="text-chat-input-group">
                        <input type="text" 
                               class="text-chat-input" 
                               id="textChatInput" 
                               placeholder="Type your message here..."
                               maxlength="500">
                        <button class="text-chat-send-btn" id="textChatSendBtn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
            
            {recording_button_html}
        </div>
        
        <script>
            // Centralized State Management System
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
            
            // Global state instance
            const appState = new AppState();
            
            // Centralized UI Controller
            class UIController {
                constructor() {
                    this.elements = new Map();
                    this.cacheElements();
                }
                
                // Cache DOM elements for performance
                cacheElements() {
                    const elementMap = {
                        connectionIndicator: 'connectionIndicator',
                        connectionText: 'connectionText',
                        connectionDot: 'connectionDot',
                        recordingIndicator: 'recordingIndicator',
                        status: 'status',
                        messages: 'messages',
                        responseLoading: 'responseLoading',
                        ttsLoading: 'ttsLoading',
                        personalityOverlay: 'personalityOverlay',
                        personalityDisplay: 'personalityDisplay',
                        personalityDropdown: 'personalityDropdown',
                        confirmPersonalityBtn: 'confirmPersonalityBtn',
                        textChatContainer: 'textChatContainer',
                        textChatInput: 'textChatInput',
                        textChatSendBtn: 'textChatSendBtn',
                        talkButton: 'talkButton'
                    };
                    
                    Object.entries(elementMap).forEach(([key, id]) => {
                        const element = document.getElementById(id);
                        if (element) {
                            this.elements.set(key, element);
                        }
                    });
                }
                
                // Get cached element
                getElement(key) {
                    return this.elements.get(key);
                }
                
                // Update connection status
                updateConnectionStatus() {
                    const indicator = this.getElement('connectionIndicator');
                    const text = this.getElement('connectionText');
                    
                    if (!indicator || !text) return;
                    
                    const connectionState = appState.get('connection');
                    
                    // Remove all status classes
                    indicator.classList.remove('connected', 'connecting', 'disconnected');
                    
                    switch (connectionState.status) {
                        case 'connected':
                            indicator.classList.add('connected');
                            text.textContent = 'Connected';
                            break;
                        case 'connecting':
                            indicator.classList.add('connecting');
                            const attempts = connectionState.reconnectAttempts;
                            const maxAttempts = connectionState.maxReconnectAttempts;
                            text.textContent = `Connecting${attempts > 0 ? ` (${attempts}/${maxAttempts})` : '...'}`;
                            break;
                        case 'disconnected':
                            indicator.classList.add('disconnected');
                            text.textContent = 'Disconnected';
                            break;
                        case 'error':
                            indicator.classList.add('disconnected');
                            text.textContent = 'Connection Error';
                            break;
                        default:
                            indicator.classList.add('disconnected');
                            text.textContent = 'Unknown';
                    }
                }
                
                // Update recording state
                updateRecordingState() {
                    const indicator = this.getElement('recordingIndicator');
                    const isRecording = appState.get('ui.recording');
                    
                    if (indicator) {
                        indicator.style.display = isRecording ? 'flex' : 'none';
                    }
                }
                
                // Update loading states
                updateLoadingStates() {
                    const loadingStates = appState.get('ui.loadingStates');
                    
                    const responseLoading = this.getElement('responseLoading');
                    if (responseLoading) {
                        responseLoading.classList.toggle('show', loadingStates.generatingResponse);
                    }
                    
                    const ttsLoading = this.getElement('ttsLoading');
                    if (ttsLoading) {
                        ttsLoading.classList.toggle('show', loadingStates.generatingAudio);
                    }
                }
                
                // Update status display
                updateStatus() {
                    const statusElement = this.getElement('status');
                    const currentStatus = appState.get('data.currentStatus');
                    
                    if (statusElement && currentStatus) {
                        const icon = this.getStatusIcon(currentStatus);
                        statusElement.innerHTML = `<i class="${icon}"></i><span>${currentStatus}</span>`;
                    }
                }
                
                // Update messages
                updateMessages() {
                    const messagesDiv = this.getElement('messages');
                    if (!messagesDiv) return;
                    
                    const messages = appState.get('data.messages') || [];
                    const lastCount = appState.get('ui.lastMessageCount');
                    
                    // Only add new messages, don't rebuild entire list
                    if (messages.length > lastCount) {
                        for (let i = lastCount; i < messages.length; i++) {
                            const msg = messages[i];
                            const messageDiv = this.createMessageElement(msg, i);
                            messagesDiv.appendChild(messageDiv);
                        }
                        
                        appState.set('ui.lastMessageCount', messages.length);
                        messagesDiv.scrollTop = messagesDiv.scrollHeight;
                    }
                    
                    // Handle message clearing (when count goes down)
                    if (messages.length < lastCount) {
                        messagesDiv.innerHTML = '';
                        appState.set('ui.lastMessageCount', 0);
                        
                        // Re-add all messages
                        messages.forEach((msg, index) => {
                            const messageDiv = this.createMessageElement(msg, index);
                            messagesDiv.appendChild(messageDiv);
                        });
                        
                        appState.set('ui.lastMessageCount', messages.length);
                        messagesDiv.scrollTop = messagesDiv.scrollHeight;
                    }
                    
                    // Check for messages that should now be visible
                    messages.forEach((msg, index) => {
                        const messageDiv = document.querySelector(`[data-message-id="${index}"]`);
                        if (messageDiv && msg.show_immediately && messageDiv.classList.contains('pending')) {
                            messageDiv.classList.remove('pending');
                            messageDiv.classList.add('show');
                        }
                    });
                }
                
                // Create message element
                createMessageElement(msg, index) {
                    const messageDiv = document.createElement('div');
                    
                    // Set initial visibility based on show_immediately flag
                    const initialClass = msg.show_immediately ? 'message show' : 'message pending';
                    messageDiv.className = initialClass + ' ' + (msg.is_ai ? 'ai-message' : 'user-message');
                    messageDiv.setAttribute('data-message-id', index);
                    
                    const bubble = document.createElement('div');
                    bubble.className = 'message-bubble';
                    bubble.textContent = msg.message;
                    
                    const info = document.createElement('div');
                    info.className = 'message-info';
                    const userIcon = msg.is_ai ? 'fas fa-robot' : 'fas fa-user';
                    info.innerHTML = `<i class="${userIcon}"></i><span class="timestamp">${msg.timestamp}</span><span>${msg.sender}</span>`;
                    
                    messageDiv.appendChild(bubble);
                    messageDiv.appendChild(info);
                    
                    return messageDiv;
                }
                
                // Update personality display and overlay
                updatePersonalityState() {
                    const overlay = this.getElement('personalityOverlay');
                    const personalityDisplay = this.getElement('personalityDisplay');
                    
                    const personalitySelected = appState.get('data.selectedPersonality');
                    const personalityInfo = appState.get('data.personalityInfo');
                    
                    if (personalitySelected && personalityInfo) {
                        // Hide overlay if personality is selected
                        if (overlay) overlay.classList.add('hidden');
                        // Update personality display
                        if (personalityDisplay) {
                            personalityDisplay.textContent = `${personalityInfo.short_name} Bartender`;
                        }
                    } else if (!personalitySelected) {
                        // Show overlay if no personality selected
                        if (overlay && overlay.classList.contains('hidden')) {
                            overlay.classList.remove('hidden');
                            this.resetPersonalitySelection();
                        }
                        // Reset personality display to default
                        if (personalityDisplay) {
                            personalityDisplay.textContent = 'Your AI Bartender';
                        }
                    }
                }
                
                // Update text chat visibility
                updateTextChatVisibility() {
                    const textChatContainer = this.getElement('textChatContainer');
                    const textChatEnabled = appState.get('ui.textChatEnabled');
                    
                    if (textChatContainer) {
                        textChatContainer.style.display = textChatEnabled ? 'block' : 'none';
                    }
                }
                
                // Reset personality selection UI
                resetPersonalitySelection() {
                    const dropdown = this.getElement('personalityDropdown');
                    const confirmBtn = this.getElement('confirmPersonalityBtn');
                    
                    if (dropdown) dropdown.value = '';
                    if (confirmBtn) {
                        confirmBtn.textContent = 'Start Your Beer Journey';
                        confirmBtn.disabled = true;
                    }
                }
                
                // Show error notification
                showError(message, type = 'error') {
                    // Add to error state
                    const currentErrors = appState.get('ui.errors') || [];
                    const errorId = Date.now();
                    const newError = { id: errorId, message, type, timestamp: new Date() };
                    
                    appState.set('ui.errors', [...currentErrors, newError]);
                    
                    // Create toast notification
                    this.createToast(newError);
                    
                    // Auto-remove after 5 seconds
                    setTimeout(() => {
                        this.removeError(errorId);
                    }, 5000);
                }
                
                // Create toast notification
                createToast(error) {
                    const toast = document.createElement('div');
                    toast.className = `toast toast-${error.type}`;
                    toast.setAttribute('data-error-id', error.id);
                    toast.innerHTML = `
                        <i class="fas fa-${error.type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
                        <span>${error.message}</span>
                        <button class="toast-close" onclick="uiController.removeError(${error.id})">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                    
                    // Add toast styles if not already present
                    if (!document.querySelector('.toast-container')) {
                        this.createToastContainer();
                    }
                    
                    const container = document.querySelector('.toast-container');
                    if (container) {
                        container.appendChild(toast);
                        
                        // Animate in
                        setTimeout(() => toast.classList.add('show'), 10);
                    }
                }
                
                // Create toast container
                createToastContainer() {
                    const container = document.createElement('div');
                    container.className = 'toast-container';
                    document.body.appendChild(container);
                    
                    // Add toast styles
                    const style = document.createElement('style');
                    style.textContent = `
                        .toast-container {
                            position: fixed;
                            top: 1rem;
                            right: 1rem;
                            z-index: 9999;
                            display: flex;
                            flex-direction: column;
                            gap: 0.5rem;
                        }
                        
                        .toast {
                            background: var(--bg-secondary);
                            border: 2px solid var(--border);
                            border-radius: 12px;
                            padding: 1rem;
                            min-width: 300px;
                            display: flex;
                            align-items: center;
                            gap: 0.75rem;
                            box-shadow: 0 8px 32px var(--shadow);
                            transform: translateX(100%);
                            opacity: 0;
                            transition: all 0.3s ease;
                        }
                        
                        .toast.show {
                            transform: translateX(0);
                            opacity: 1;
                        }
                        
                        .toast-error {
                            border-color: var(--accent-red);
                            color: var(--accent-red);
                        }
                        
                        .toast-info {
                            border-color: var(--accent-green);
                            color: var(--accent-green);
                        }
                        
                        .toast-close {
                            background: none;
                            border: none;
                            color: var(--text-muted);
                            cursor: pointer;
                            margin-left: auto;
                            padding: 0.25rem;
                            border-radius: 4px;
                            transition: all 0.2s ease;
                        }
                        
                        .toast-close:hover {
                            background: var(--bg-tertiary);
                            color: var(--text-primary);
                        }
                    `;
                    document.head.appendChild(style);
                }
                
                // Remove error
                removeError(errorId) {
                    const currentErrors = appState.get('ui.errors') || [];
                    const updatedErrors = currentErrors.filter(error => error.id !== errorId);
                    appState.set('ui.errors', updatedErrors);
                    
                    const toast = document.querySelector(`[data-error-id="${errorId}"]`);
                    if (toast) {
                        toast.classList.remove('show');
                        setTimeout(() => toast.remove(), 300);
                    }
                }
                
                // Get status icon
                getStatusIcon(status) {
                    if (status.includes('Recording')) return 'fas fa-microphone';
                    if (status.includes('Processing')) return 'fas fa-cog fa-spin';
                    if (status.includes('Speaking')) return 'fas fa-volume-up';
                    if (status.includes('beer') || status.includes('Beer')) return 'fas fa-beer';
                    return 'fas fa-check-circle';
                }
            }
            
            // Global UI controller instance
            const uiController = new UIController();
            
            // Initialize state change listeners for UI updates
            function initializeStateListeners() {
                // Listen for connection status changes
                appState.subscribe('connection.status', () => {
                    uiController.updateConnectionStatus();
                });
                
                // Listen for recording state changes  
                appState.subscribe('ui.recording', () => {
                    uiController.updateRecordingState();
                });
                
                // Listen for loading state changes
                appState.subscribe('ui.loadingStates', () => {
                    uiController.updateLoadingStates();
                });
                
                // Listen for status changes
                appState.subscribe('data.currentStatus', () => {
                    uiController.updateStatus();
                });
                
                // Listen for message changes
                appState.subscribe('data.messages', () => {
                    uiController.updateMessages();
                });
                
                // Listen for text chat enable/disable
                appState.subscribe('ui.textChatEnabled', () => {
                    uiController.updateTextChatVisibility();
                });
                
                console.log('State listeners initialized');
            }
            
            {recording_js}
            
            function sendTextMessage() {
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
                    if (sendWebSocketMessage('send_text_message', { message: message })) {
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
            
            // Enhanced WebSocket connection and messaging
            function connectWebSocket() {
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
                    
                    newWs.onopen = function(event) {
                        console.log('WebSocket connected successfully');
                        appState.update({
                            'connection.status': 'connected',
                            'connection.reconnectAttempts': 0,
                            'connection.lastPing': Date.now(),
                            'ui.loadingStates.connecting': false
                        });
                        
                        // Start connection health monitoring
                        startConnectionHealthCheck();
                        
                        uiController.showError('Connected to server', 'info');
                    };
                    
                    newWs.onmessage = function(event) {
                        try {
                            const message = JSON.parse(event.data);
                            handleWebSocketMessage(message);
                            
                            // Update last ping time
                            appState.set('connection.lastPing', Date.now());
                        } catch (error) {
                            console.error('Error parsing WebSocket message:', error);
                            uiController.showError('Received invalid message from server');
                        }
                    };
                    
                    newWs.onclose = function(event) {
                        console.log('WebSocket disconnected:', event.code, event.reason);
                        const wasConnected = appState.get('connection.status') === 'connected';
                        
                        appState.update({
                            'connection.status': 'disconnected',
                            'connection.ws': null,
                            'ui.loadingStates.connecting': false
                        });
                        
                        if (wasConnected) {
                            uiController.showError('Disconnected from server');
                        }
                        
                        // Attempt to reconnect with exponential backoff
                        const attempts = appState.get('connection.reconnectAttempts');
                        const maxAttempts = appState.get('connection.maxReconnectAttempts');
                        
                        if (attempts < maxAttempts) {
                            const newAttempts = attempts + 1;
                            const delay = appState.get('connection.reconnectDelay') * Math.pow(1.5, newAttempts - 1);
                            
                            appState.set('connection.reconnectAttempts', newAttempts);
                            
                            console.log(`Scheduling reconnection attempt ${newAttempts}/${maxAttempts} in ${delay}ms`);
                            setTimeout(() => {
                                if (appState.get('connection.status') === 'disconnected') {
                                    connectWebSocket();
                                }
                            }, delay);
                        } else {
                            uiController.showError('Unable to reconnect - maximum attempts reached');
                        }
                    };
                    
                    newWs.onerror = function(error) {
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
            
            // Connection health monitoring
            function startConnectionHealthCheck() {
                setInterval(() => {
                    const ws = appState.get('connection.ws');
                    const lastPing = appState.get('connection.lastPing');
                    const currentTime = Date.now();
                    
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        // Check if we haven't received any messages in the last 30 seconds
                        if (currentTime - lastPing > 30000) {
                            console.warn('Connection seems stale, sending ping...');
                            sendWebSocketMessage('ping');
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
            
            function sendWebSocketMessage(action, data = {}) {
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
            
            function handleWebSocketMessage(message) {
                try {
                    switch (message.type) {
                        case 'state_update':
                            updateInterface(message.data);
                            break;
                        case 'personalities_list':
                            appState.set('data.availablePersonalities', message.data.personalities || []);
                            populatePersonalityDropdown();
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
            
            // Load personalities on page load
            function loadPersonalities() {
                sendWebSocketMessage('get_personalities');
            }
            
            function populatePersonalityDropdown() {
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
            
            function confirmPersonalitySelection() {
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
                    
                    if (sendWebSocketMessage('select_personality', { personality: selectedPersonality })) {
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
            
            
            function updateInterface(data) {
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
            
            function getStatusIcon(status) {
                if (status.includes('Recording')) return 'fas fa-microphone';
                if (status.includes('Processing')) return 'fas fa-cog fa-spin';
                if (status.includes('Speaking')) return 'fas fa-volume-up';
                if (status.includes('beer') || status.includes('Beer')) return 'fas fa-beer';
                return 'fas fa-check-circle';
            }
            
            
            function setupTextChatListeners() {
                const input = document.getElementById('textChatInput');
                const sendBtn = document.getElementById('textChatSendBtn');
                
                // Send on button click
                sendBtn.addEventListener('click', sendTextMessage);
                
                // Send on Enter key press
                input.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendTextMessage();
                    }
                });
            }
            
            // Add event listener for confirm button
            document.getElementById('confirmPersonalityBtn').addEventListener('click', confirmPersonalitySelection);
            
            
            // Initialize application on page load
            function initializeApp() {
                console.log('Initializing Terry the Tube web interface...');
                
                try {
                    // Initialize state listeners first
                    initializeStateListeners();
                    
                    // Setup UI event listeners
                    setupTextChatListeners();
                    
                    // Connect to WebSocket server
                    connectWebSocket();
                    
                    // Load available personalities
                    loadPersonalities();
                    
                    // Set initial UI state
                    appState.update({
                        'data.currentStatus': 'Ready to serve beer!',
                        'ui.personalityOverlayVisible': true,
                        'ui.textChatEnabled': false
                    });
                    
                    console.log('App initialization complete');
                    
                } catch (error) {
                    console.error('Error during app initialization:', error);
                    uiController.showError('Failed to initialize application: ' + error.message);
                }
            }
            
            // Add error boundary for the entire app
            window.addEventListener('error', function(event) {
                console.error('Global error:', event.error);
                uiController.showError('An unexpected error occurred. Please refresh the page.');
            });
            
            window.addEventListener('unhandledrejection', function(event) {
                console.error('Unhandled promise rejection:', event.reason);
                uiController.showError('A network error occurred. Please check your connection.');
            });
            
            // Initialize when DOM is loaded
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initializeApp);
            } else {
                initializeApp();
            }
        </script>
    </body>
    </html>
    '''
    
    # Replace placeholders with actual content
    template = template.replace('{recording_indicator_html}', recording_indicator_html)
    template = template.replace('{recording_button_html}', recording_button_html)
    template = template.replace('{recording_js}', recording_js)
    
    return template