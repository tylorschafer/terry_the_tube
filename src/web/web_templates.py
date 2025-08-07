"""
HTML Templates for Terry the Tube Web Interface
"""


def get_main_html_template():
    """Get the main HTML template"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terry the Tube - Beer Dispenser</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: #2b2b2b; 
                color: white; 
                margin: 0; 
                padding: 20px;
            }
            .container { max-width: 1800px; margin: 0 auto; }
            .title { 
                text-align: center; 
                color: #ffa500; 
                font-size: 48px; 
                margin-bottom: 20px;
            }
            .status { 
                text-align: center; 
                margin-bottom: 20px; 
                font-size: 20px;
                color: #ccc;
            }
            .messages { 
                background: #1e1e1e; 
                height: 600px; 
                overflow-y: scroll; 
                padding: 15px; 
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .message { 
                margin-bottom: 19px; 
                line-height: 1.4;
                font-size: 30px;
            }
            .ai-message { color: #ffa500; }
            .user-message { color: #4CAF50; }
            .timestamp { font-size: 10px; opacity: 0.7; }
            .talk-button { 
                width: 100%; 
                height: 60px; 
                font-size: 16px; 
                background: #4CAF50; 
                color: white; 
                border: none; 
                border-radius: 5px;
                cursor: pointer;
                margin-bottom: 10px;
            }
            .talk-button:active { background: #ff4444; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="title">TERRY THE TUBE</div>
            <div class="status" id="status">Ready to serve beer!</div>
            <div class="messages" id="messages">
                <div class="message ai-message">
                    <span class="timestamp">[00:00:00]</span> <strong>Terry:</strong> Hey there! You looking for a beer or what?
                </div>
            </div>
            <button class="talk-button" id="talkButton" 
                    onmousedown="startRecording()" 
                    onmouseup="stopRecording()"
                    ontouchstart="startRecording()" 
                    ontouchend="stopRecording()">
                Hold Button to Talk
            </button>
        </div>
        
        <script>
            let recording = false;
            
            function startRecording() {
                if (!recording) {
                    recording = true;
                    document.getElementById('talkButton').textContent = 'Recording... (Release to stop)';
                    document.getElementById('talkButton').style.background = '#ff4444';
                    fetch('/start_recording', {method: 'POST'});
                }
            }
            
            function stopRecording() {
                if (recording) {
                    recording = false;
                    document.getElementById('talkButton').textContent = 'Hold Button to Talk';
                    document.getElementById('talkButton').style.background = '#4CAF50';
                    fetch('/stop_recording', {method: 'POST'});
                }
            }
            
            function updateInterface() {
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('status').textContent = data.status;
                        
                        const messagesDiv = document.getElementById('messages');
                        messagesDiv.innerHTML = '';
                        
                        data.messages.forEach(msg => {
                            const div = document.createElement('div');
                            div.className = 'message ' + (msg.is_ai ? 'ai-message' : 'user-message');
                            div.innerHTML = `<span class="timestamp">[${msg.timestamp}]</span> <strong>${msg.sender}:</strong> ${msg.message}`;
                            messagesDiv.appendChild(div);
                        });
                        
                        messagesDiv.scrollTop = messagesDiv.scrollHeight;
                    });
            }
            
            setInterval(updateInterface, 1000);
        </script>
    </body>
    </html>
    '''