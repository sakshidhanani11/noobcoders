# websocket_server.py
import asyncio
import websockets
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONNECTED_CLIENTS = set()

async def websocket_handler(websocket, path):
    """Handles WebSocket connections and messages."""
    CONNECTED_CLIENTS.add(websocket)
    logging.info(f"Client connected: {websocket.remote_address}. Total clients: {len(CONNECTED_CLIENTS)}")
    try:
        async for message in websocket:
            logging.info(f"Received message from client {websocket.remote_address}: {message}")
            # In this setup, clients don't send messages to the server for broadcasting.
            # They only receive. If you need client-to-client, add logic here.
    except websockets.exceptions.ConnectionClosedOK:
        logging.info(f"Client disconnected normally: {websocket.remote_address}")
    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Client disconnected with error: {websocket.remote_address} - {e}")
    finally:
        CONNECTED_CLIENTS.remove(websocket)
        logging.info(f"Client removed. Total clients: {len(CONNECTED_CLIENTS)}")

async def broadcast_message(message: dict):
    """Sends a JSON message to all connected WebSocket clients."""
    if not CONNECTED_CLIENTS:
        logging.warning("No WebSocket clients connected to broadcast message.")
        return

    message_json = json.dumps(message)
    # Send to all connected clients
    disconnected_clients = set()
    for websocket in CONNECTED_CLIENTS:
        try:
            await websocket.send(message_json)
            logging.info(f"Broadcasted to {websocket.remote_address}: {message['type']}")
        except websockets.exceptions.ConnectionClosed:
            logging.warning(f"Client {websocket.remote_address} found disconnected during broadcast.")
            disconnected_clients.add(websocket)
        except Exception as e:
            logging.error(f"Error broadcasting to {websocket.remote_address}: {e}")
            disconnected_clients.add(websocket)
    
    # Clean up disconnected clients
    for client in disconnected_clients:
        CONNECTED_CLIENTS.remove(client)
    logging.info(f"Broadcast complete. Remaining clients: {len(CONNECTED_CLIENTS)}")


class HTTPBroadcastHandler(BaseHTTPRequestHandler):
    """Handles HTTP POST requests to broadcast messages."""
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            message = json.loads(post_data.decode('utf-8'))
            logging.info(f"Received HTTP POST for broadcast: {message.get('type', 'unknown')}")
            
            # Schedule the broadcast in the asyncio event loop
            asyncio.run_coroutine_threadsafe(broadcast_message(message), asyncio.get_event_loop())
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Broadcast scheduled"}).encode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": "Invalid JSON"}).encode('utf-8'))
            logging.error("Invalid JSON received via HTTP POST.")
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            logging.error(f"Error handling HTTP POST: {e}")

def run_http_server(host, port):
    """Runs the HTTP server in a separate thread."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, HTTPBroadcastHandler)
    logging.info(f"HTTP Broadcast Server listening on http://{host}:{port}")
    httpd.serve_forever()

async def main():
    # Start WebSocket server
    ws_server = await websockets.serve(websocket_handler, "0.0.0.0", 8001)
    logging.info("WebSocket Server listening on ws://0.0.0.0:8001")

    # Start HTTP server in a separate thread
    http_thread = threading.Thread(target=run_http_server, args=("0.0.0.0", 8002))
    http_thread.daemon = True # Allow main program to exit even if thread is running
    http_thread.start()

    await ws_server.wait_closed()

if __name__ == "__main__":
    # Ensure there's an event loop for asyncio.run
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("WebSocket server stopped by user.")
    except Exception as e:
        logging.critical(f"WebSocket server crashed: {e}")