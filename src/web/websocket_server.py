"""
WebSocket Server for Terry the Tube
Provides real-time communication between frontend and backend
"""
import asyncio
import json
import threading
import websockets
from typing import Set, Dict, Any
import logging

# Configure logging for websockets
logging.getLogger('websockets').setLevel(logging.WARNING)


class WebSocketManager:
    def __init__(self, web_interface):
        self.web_interface = web_interface
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None
        self.loop = None
        
    async def register_client(self, websocket):
        """Register a new client connection"""
        self.clients.add(websocket)
        print(f"WebSocket client connected. Total clients: {len(self.clients)}")
        
        # Send current state to new client
        try:
            await self.send_state_update(websocket)
        except Exception as e:
            print(f"Error sending initial state to client: {e}")
        
    async def unregister_client(self, websocket):
        """Unregister a client connection"""
        self.clients.discard(websocket)
        print(f"WebSocket client disconnected. Total clients: {len(self.clients)}")
        
    async def send_state_update(self, websocket=None):
        """Send current state to client(s)"""
        if not self.clients and not websocket:
            return
            
        state = {
            'type': 'state_update',
            'data': {
                'status': self.web_interface.get_status(),
                'messages': self.web_interface.get_messages(),
                'personality': self.web_interface.get_personality_info(),
                'personality_selected': self.web_interface.is_personality_selected(),
                'generating_audio': self.web_interface.is_generating_audio(),
                'generating_response': self.web_interface.is_generating_response(),
                'text_chat_enabled': self.web_interface.is_text_chat_enabled()
            }
        }
        
        message = json.dumps(state)
        
        if websocket:
            # Send to specific client
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                pass
        else:
            # Broadcast to all clients
            await self.broadcast(message)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
            
        # Remove disconnected clients
        disconnected = set()
        for client in self.clients.copy():
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Clean up disconnected clients
        self.clients -= disconnected
    
    async def handle_message(self, websocket, message: str):
        """Handle incoming message from client"""
        try:
            data = json.loads(message)
            action = data.get('action')
            payload = data.get('data', {})
            
            # Handle different actions
            if action == 'start_recording':
                self.web_interface.handle_action('start_recording')
            elif action == 'stop_recording':
                self.web_interface.handle_action('stop_recording')
            elif action == 'send_text_message':
                self.web_interface.handle_action('send_text_message', payload)
            elif action == 'select_personality':
                self.web_interface.handle_action('change_personality', payload)
            elif action == 'get_personalities':
                # Send personalities list
                from src.personalities import get_personality_names
                personalities = get_personality_names()
                response = {
                    'type': 'personalities_list',
                    'data': {
                        'personalities': [{'key': key, 'name': name} for key, name in personalities]
                    }
                }
                await websocket.send(json.dumps(response))
            else:
                print(f"Unknown WebSocket action: {action}")
                
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {message}")
        except Exception as e:
            print(f"Error handling WebSocket message: {e}")
    
    async def client_handler(self, websocket, path):
        """Handle individual client connection"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    def notify_state_change(self):
        """Call this when state changes to notify all clients"""
        if self.loop and not self.loop.is_closed():
            try:
                asyncio.run_coroutine_threadsafe(self.send_state_update(), self.loop)
            except Exception as e:
                print(f"Error scheduling state update: {e}")
    
    def start_server(self, host='localhost', port=8081):
        """Start the WebSocket server in a separate thread"""
        def run_server():
            try:
                # Set event loop policy for macOS compatibility
                import sys
                if sys.platform == 'darwin':
                    import asyncio
                    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
                
                # Create a new event loop for this thread
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                print(f"Event loop created for WebSocket server thread")
            except Exception as e:
                print(f"Error setting up event loop: {e}")
                return
                
            try:
                # Start the server
                self.server = self.loop.run_until_complete(
                    websockets.serve(
                        self.client_handler,
                        host,
                        port,
                        ping_interval=20,
                        ping_timeout=10
                    )
                )
                print(f"WebSocket server started at: ws://{host}:{port}")
                
                # Run the event loop
                self.loop.run_forever()
                
            except Exception as e:
                print(f"WebSocket server error: {e}")
            finally:
                if self.server:
                    self.server.close()
                    self.loop.run_until_complete(self.server.wait_closed())
                self.loop.close()
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        return thread
    
    def stop_server(self):
        """Stop the WebSocket server"""
        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self.loop.stop)