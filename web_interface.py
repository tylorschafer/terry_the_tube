import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from queue import Queue

class WebInterface:
    def __init__(self, message_callback=None):
        self.message_callback = message_callback
        self.messages = []
        self.status = "Ready to serve beer!"
        self.port = 8080
        
    def add_message(self, sender, message, is_ai=False):
        """Add a message to display"""
        timestamp = time.strftime("%H:%M:%S")
        self.messages.append({
            'sender': sender,
            'message': message,
            'is_ai': is_ai,
            'timestamp': timestamp
        })
        
    def set_status(self, status):
        """Update status"""
        self.status = status

class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''
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
            self.wfile.write(html.encode())
            
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            data = {
                'status': self.server.web_interface.status,
                'messages': self.server.web_interface.messages
            }
            self.wfile.write(json.dumps(data).encode())
            
    def do_POST(self):
        if self.path == '/start_recording':
            if self.server.web_interface.message_callback:
                threading.Thread(
                    target=self.server.web_interface.message_callback, 
                    args=('start_recording',), 
                    daemon=True
                ).start()
            
        elif self.path == '/stop_recording':
            if self.server.web_interface.message_callback:
                threading.Thread(
                    target=self.server.web_interface.message_callback, 
                    args=('stop_recording',), 
                    daemon=True
                ).start()
            
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress log messages

def start_web_server(web_interface):
    """Start the web server"""
    server = HTTPServer(('localhost', web_interface.port), WebHandler)
    server.web_interface = web_interface
    print(f"Web interface started at: http://localhost:{web_interface.port}")
    server.serve_forever()

if __name__ == "__main__":
    # Test the web interface
    def dummy_callback(action):
        print(f"Web Action: {action}")
    
    web_interface = WebInterface(dummy_callback)
    start_web_server(web_interface)