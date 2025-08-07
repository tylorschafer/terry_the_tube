"""
Web Server for Terry the Tube
HTTP server handling web interface requests
"""
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from .web_templates import get_main_html_template


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self._serve_main_page()
        elif self.path == '/status':
            self._serve_status()
        else:
            self._serve_404()
            
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/start_recording':
            self._handle_start_recording()
        elif self.path == '/stop_recording':
            self._handle_stop_recording()
        else:
            self._serve_404()
    
    def _serve_main_page(self):
        """Serve the main HTML page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = get_main_html_template()
        self.wfile.write(html.encode())
    
    def _serve_status(self):
        """Serve status JSON"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        data = {
            'status': self.server.web_interface.get_status(),
            'messages': self.server.web_interface.get_messages()
        }
        self.wfile.write(json.dumps(data).encode())
    
    def _handle_start_recording(self):
        """Handle start recording request"""
        if self.server.web_interface.message_callback:
            threading.Thread(
                target=self.server.web_interface.message_callback, 
                args=('start_recording',), 
                daemon=True
            ).start()
        self._send_ok_response()
    
    def _handle_stop_recording(self):
        """Handle stop recording request"""
        if self.server.web_interface.message_callback:
            threading.Thread(
                target=self.server.web_interface.message_callback, 
                args=('stop_recording',), 
                daemon=True
            ).start()
        self._send_ok_response()
    
    def _send_ok_response(self):
        """Send simple OK response"""
        self.send_response(200)
        self.end_headers()
    
    def _serve_404(self):
        """Serve 404 error"""
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass


def start_web_server(web_interface):
    """Start the web server"""
    server = HTTPServer((web_interface.host, web_interface.port), WebHandler)
    server.web_interface = web_interface
    print(f"Web interface started at: http://{web_interface.host}:{web_interface.port}")
    server.serve_forever()