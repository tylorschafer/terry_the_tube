import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.personalities import get_personality_names


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self._serve_main_page()
        elif self.path == '/api/state':
            self._serve_api_state()
        elif self.path == '/api/personalities':
            self._serve_api_personalities()
        else:
            self._serve_404()
            
    def do_POST(self):
        if self.path == '/api/action':
            self._handle_api_action()
        else:
            self._serve_404()
    
    def _serve_main_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Use the web interface's HTML template method
        html = self.server.web_interface.get_html_template()
        self.wfile.write(html.encode())
    
    def _serve_api_state(self):
        """Serve complete application state for polling"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        state = {
            'status': self.server.web_interface.get_status(),
            'messages': self.server.web_interface.get_messages(),
            'personality': self.server.web_interface.get_personality_info(),
            'personality_selected': self.server.web_interface.is_personality_selected(),
            'generating_audio': self.server.web_interface.is_generating_audio(),
            'generating_response': self.server.web_interface.is_generating_response(),
            'text_chat_enabled': self.server.web_interface.is_text_chat_enabled(),
            'text_only_mode': self.server.web_interface.is_text_only_mode()
        }
        self.wfile.write(json.dumps(state).encode())
    
    def _serve_api_personalities(self):
        """Serve available personalities list"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        personalities = get_personality_names()
        data = {
            'personalities': [{'key': key, 'name': name} for key, name in personalities]
        }
        self.wfile.write(json.dumps(data).encode())
    
    def _handle_api_action(self):
        """Handle all actions through single API endpoint"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            action = data.get('action')
            payload = data.get('data', {})
            
            # Handle different actions
            if action == 'start_recording':
                self.server.web_interface.handle_action('start_recording')
            elif action == 'stop_recording':
                self.server.web_interface.handle_action('stop_recording')
            elif action == 'send_text_message':
                self.server.web_interface.handle_action('send_text_message', payload)
            elif action == 'select_personality':
                self.server.web_interface.handle_action('change_personality', payload)
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'Unknown action: {action}'}).encode())
                return
                
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def _send_ok_response(self):
        self.send_response(200)
        self.end_headers()
    
    def _serve_404(self):
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")
    
    def log_message(self, format, *args):
        pass


def start_web_server(web_interface):
    # Start HTTP server with REST API endpoints
    server = HTTPServer((web_interface.host, web_interface.port), WebHandler)
    server.web_interface = web_interface
    print(f"Web interface started at: http://{web_interface.host}:{web_interface.port}")
    print(f"API endpoints available at: http://{web_interface.host}:{web_interface.port}/api/")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()