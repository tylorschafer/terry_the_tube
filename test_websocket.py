#!/usr/bin/env python3
"""
Simple test for WebSocket functionality without keyboard dependencies
"""
import time
import threading
from src.web.web_interface import WebInterface
from src.web.web_server import start_web_server

def test_websocket():
    """Test WebSocket server startup"""
    print("Creating WebInterface...")
    web_interface = WebInterface(
        message_callback=None,
        enable_text_chat=True,
        text_only_mode=False
    )
    
    print("Starting web server in background thread...")
    def run_server():
        try:
            start_web_server(web_interface)
        except KeyboardInterrupt:
            print("Server stopped by KeyboardInterrupt")
        except Exception as e:
            print(f"Server error: {e}")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait a bit for server to start
    print("Waiting for servers to start...")
    time.sleep(3)
    
    # Test state change notifications
    print("Testing state change notifications...")
    web_interface.set_status("Testing WebSocket updates")
    web_interface.add_message("Test", "Hello WebSocket!", is_ai=False)
    
    print("WebSocket test completed. Servers should be running.")
    print("You can now visit http://localhost:8080 to test the interface")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping test...")

if __name__ == "__main__":
    test_websocket()