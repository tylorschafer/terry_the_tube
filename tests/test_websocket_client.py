#!/usr/bin/env python3
"""
Simple WebSocket client test
"""
import asyncio
import websockets
import json

async def test_websocket_client():
    uri = "ws://localhost:8081"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")
            
            # Send a test message
            test_message = {
                "action": "get_personalities",
                "data": {}
            }
            await websocket.send(json.dumps(test_message))
            print("Sent get_personalities request")
            
            # Wait for response
            response = await websocket.recv()
            print(f"Received: {response}")
            
    except Exception as e:
        print(f"WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_client())