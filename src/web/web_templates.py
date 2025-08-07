"""
HTML Templates for Terry the Tube Web Interface
"""


def get_main_html_template():
    """Get the main HTML template"""
    return '''
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
        </style>
    </head>
    <body>
        <div class="background-pattern"></div>
        <div class="recording-indicator" id="recordingIndicator">
            <div class="recording-dot"></div>
            <span>Recording...</span>
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
                <p class="subtitle">Your Sarcastic AI Beer Dispenser</p>
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
            </div>
        </div>
        
        <script>
            let recording = false;
            let availablePersonalities = [];
            let selectedPersonality = null;
            
            function startRecording() {
                if (!recording) {
                    recording = true;
                    const button = document.getElementById('talkButton');
                    const indicator = document.getElementById('recordingIndicator');
                    
                    button.innerHTML = '<i class="fas fa-stop"></i><span>Release to Stop</span>';
                    indicator.style.display = 'flex';
                    
                    fetch('/start_recording', {method: 'POST'});
                }
            }
            
            function stopRecording() {
                if (recording) {
                    recording = false;
                    const button = document.getElementById('talkButton');
                    const indicator = document.getElementById('recordingIndicator');
                    
                    button.innerHTML = '<i class="fas fa-microphone"></i><span>Hold to Talk</span>';
                    indicator.style.display = 'none';
                    
                    fetch('/stop_recording', {method: 'POST'});
                }
            }
            
            let lastMessageCount = 0;
            let lastStatus = '';
            
            // Load personalities on page load
            function loadPersonalities() {
                fetch('/personalities')
                    .then(response => response.json())
                    .then(data => {
                        availablePersonalities = data.personalities;
                        populatePersonalityDropdown();
                    })
                    .catch(error => console.log('Failed to load personalities:', error));
            }
            
            function populatePersonalityDropdown() {
                const dropdown = document.getElementById('personalityDropdown');
                dropdown.innerHTML = '<option value="">Choose a personality...</option>';
                
                availablePersonalities.forEach(personality => {
                    const option = document.createElement('option');
                    option.value = personality.key;
                    option.textContent = personality.name;
                    dropdown.appendChild(option);
                });
                
                dropdown.addEventListener('change', function() {
                    const confirmBtn = document.getElementById('confirmPersonalityBtn');
                    if (this.value) {
                        confirmBtn.disabled = false;
                        selectedPersonality = this.value;
                    } else {
                        confirmBtn.disabled = true;
                        selectedPersonality = null;
                    }
                });
            }
            
            function confirmPersonalitySelection() {
                if (!selectedPersonality) return;
                
                const confirmBtn = document.getElementById('confirmPersonalityBtn');
                confirmBtn.textContent = 'Starting...';
                confirmBtn.disabled = true;
                
                fetch('/select_personality', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        personality: selectedPersonality
                    })
                })
                .then(response => {
                    if (response.ok) {
                        document.getElementById('personalityOverlay').classList.add('hidden');
                    } else {
                        throw new Error('Failed to set personality');
                    }
                })
                .catch(error => {
                    console.log('Error setting personality:', error);
                    confirmBtn.textContent = 'Try Again';
                    confirmBtn.disabled = false;
                });
            }
            
            function resetPersonalitySelection() {
                // Reset dropdown selection
                const dropdown = document.getElementById('personalityDropdown');
                dropdown.value = '';
                
                // Reset button state
                const confirmBtn = document.getElementById('confirmPersonalityBtn');
                confirmBtn.textContent = 'Start Your Beer Journey';
                confirmBtn.disabled = true;
                
                // Reset selected personality
                selectedPersonality = null;
            }
            
            function updateInterface() {
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        // Only update status if it changed
                        if (data.status !== lastStatus) {
                            const statusElement = document.getElementById('status');
                            const icon = getStatusIcon(data.status);
                            statusElement.innerHTML = `<i class="${icon}"></i><span>${data.status}</span>`;
                            lastStatus = data.status;
                        }
                        
                        // Only update messages if new ones were added
                        if (data.messages.length > lastMessageCount) {
                            const messagesDiv = document.getElementById('messages');
                            
                            // Only add new messages, don't rebuild entire list
                            for (let i = lastMessageCount; i < data.messages.length; i++) {
                                const msg = data.messages[i];
                                const messageDiv = document.createElement('div');
                                messageDiv.className = 'message ' + (msg.is_ai ? 'ai-message' : 'user-message');
                                
                                const bubble = document.createElement('div');
                                bubble.className = 'message-bubble';
                                bubble.textContent = msg.message;
                                
                                const info = document.createElement('div');
                                info.className = 'message-info';
                                const userIcon = msg.is_ai ? 'fas fa-robot' : 'fas fa-user';
                                info.innerHTML = `<i class="${userIcon}"></i><span class="timestamp">${msg.timestamp}</span><span>${msg.sender}</span>`;
                                
                                messageDiv.appendChild(bubble);
                                messageDiv.appendChild(info);
                                messagesDiv.appendChild(messageDiv);
                            }
                            
                            lastMessageCount = data.messages.length;
                            messagesDiv.scrollTop = messagesDiv.scrollHeight;
                        }
                        
                        // Handle message clearing (when count goes down)
                        if (data.messages.length < lastMessageCount) {
                            const messagesDiv = document.getElementById('messages');
                            messagesDiv.innerHTML = '';
                            lastMessageCount = 0;
                            
                            // Re-add all messages
                            data.messages.forEach(msg => {
                                const messageDiv = document.createElement('div');
                                messageDiv.className = 'message ' + (msg.is_ai ? 'ai-message' : 'user-message');
                                
                                const bubble = document.createElement('div');
                                bubble.className = 'message-bubble';
                                bubble.textContent = msg.message;
                                
                                const info = document.createElement('div');
                                info.className = 'message-info';
                                const userIcon = msg.is_ai ? 'fas fa-robot' : 'fas fa-user';
                                info.innerHTML = `<i class="${userIcon}"></i><span class="timestamp">${msg.timestamp}</span><span>${msg.sender}</span>`;
                                
                                messageDiv.appendChild(bubble);
                                messageDiv.appendChild(info);
                                messagesDiv.appendChild(messageDiv);
                            });
                            
                            lastMessageCount = data.messages.length;
                            messagesDiv.scrollTop = messagesDiv.scrollHeight;
                        }
                        
                        // Handle personality display and overlay visibility
                        const overlay = document.getElementById('personalityOverlay');
                        const personalityDisplay = document.getElementById('personalityDisplay');
                        
                        if (data.personality_selected && data.personality) {
                            // Hide overlay if personality is selected
                            overlay.classList.add('hidden');
                            // Update personality display
                            personalityDisplay.textContent = `${data.personality.short_name} Bartender`;
                        } else if (!data.personality_selected) {
                            // Show overlay if no personality selected
                            overlay.classList.remove('hidden');
                            // Reset dropdown and button for new cycle
                            resetPersonalitySelection();
                            // Reset personality display to default
                            personalityDisplay.textContent = 'Your AI Bartender';
                        }
                    })
                    .catch(error => console.log('Status update failed:', error));
            }
            
            function getStatusIcon(status) {
                if (status.includes('Recording')) return 'fas fa-microphone';
                if (status.includes('Processing')) return 'fas fa-cog fa-spin';
                if (status.includes('Speaking')) return 'fas fa-volume-up';
                if (status.includes('beer') || status.includes('Beer')) return 'fas fa-beer';
                return 'fas fa-check-circle';
            }
            
            // Add event listener for confirm button
            document.getElementById('confirmPersonalityBtn').addEventListener('click', confirmPersonalitySelection);
            
            // Initialize on page load
            loadPersonalities();
            setInterval(updateInterface, 1000);
            updateInterface();
        </script>
    </body>
    </html>
    '''