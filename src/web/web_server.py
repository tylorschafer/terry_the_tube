import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from .web_templates import get_main_html_template
from .websocket_server import WebSocketManager
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.personalities import get_personality_names


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self._serve_main_page()
        elif self.path == '/status':
            self._serve_status()
        elif self.path == '/personalities':
            self._serve_personalities()
        else:
            self._serve_404()
            
    def do_POST(self):
        if self.path == '/start_recording':
            self._handle_start_recording()
        elif self.path == '/stop_recording':
            self._handle_stop_recording()
        elif self.path == '/send_text_message':
            self._handle_send_text_message()
        elif self.path == '/select_personality':
            self._handle_select_personality()
        else:
            self._serve_404()
    
    def _serve_main_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Check if we're in text-only mode
        text_only_mode = hasattr(self.server, 'web_interface') and self.server.web_interface.is_text_only_mode()
        
        html = get_main_html_template(text_only_mode=text_only_mode)
        self.wfile.write(html.encode())
    
    def _serve_status(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        data = {
            'status': self.server.web_interface.get_status(),
            'messages': self.server.web_interface.get_messages(),
            'personality': self.server.web_interface.get_personality_info(),
            'personality_selected': self.server.web_interface.is_personality_selected(),
            'generating_audio': self.server.web_interface.is_generating_audio(),
            'generating_response': self.server.web_interface.is_generating_response(),
            'text_chat_enabled': self.server.web_interface.is_text_chat_enabled()
        }
        self.wfile.write(json.dumps(data).encode())
    
    def _handle_start_recording(self):
        if self.server.web_interface.message_callback:
            threading.Thread(
                target=self.server.web_interface.message_callback, 
                args=('start_recording',), 
                daemon=True
            ).start()
        self._send_ok_response()
    
    def _handle_stop_recording(self):
        if self.server.web_interface.message_callback:
            threading.Thread(
                target=self.server.web_interface.message_callback, 
                args=('stop_recording',), 
                daemon=True
            ).start()
        self._send_ok_response()
    
    def _handle_send_text_message(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'message' in data and self.server.web_interface.message_callback:
                threading.Thread(
                    target=self.server.web_interface.message_callback,
                    args=('send_text_message', data),
                    daemon=True
                ).start()
                self._send_ok_response()
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing message parameter")
                
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
    
    def _serve_personalities(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        personalities = get_personality_names()
        data = {'personalities': [{'key': key, 'name': name} for key, name in personalities]}
        self.wfile.write(json.dumps(data).encode())
    
    def _handle_select_personality(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'personality' in data:
                self.server.web_interface.handle_action('change_personality', data)
                self._send_ok_response()
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing personality parameter")
                
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
    
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
    # Start WebSocket server
    websocket_manager = WebSocketManager(web_interface)
    web_interface.set_websocket_manager(websocket_manager)
    websocket_thread = websocket_manager.start_server(
        host=web_interface.host, 
        port=web_interface.port + 1  # Use next port for WebSocket
    )
    
    # Start HTTP server
    server = HTTPServer((web_interface.host, web_interface.port), WebHandler)
    server.web_interface = web_interface
    print(f"Web interface started at: http://{web_interface.host}:{web_interface.port}")
    print(f"WebSocket server started at: ws://{web_interface.host}:{web_interface.port + 1}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        websocket_manager.stop_server()
        server.server_close()