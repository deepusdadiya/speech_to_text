import websockets
import logging

async def listen_to_websocket(uri):
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    if message:
                        logging.info(f"Message received from WebSocket: {message}")
                    else:
                        logging.error("Empty message received from WebSocket.")
                        break

                except websockets.exceptions.ConnectionClosedOK as e:
                    logging.info("WebSocket closed normally.")
                    break  # Normal closure, no error
                except websockets.exceptions.ConnectionClosedError as e:
                    logging.error(f"WebSocket closed with error: {e.code} - {e.reason}")
                    break  # Exit on unexpected closure


    except websockets.exceptions.WebSocketException as e:
        logging.error(f"WebSocket error occurred: {e}")

async def main():
    uri = "ws://127.0.0.1:8000/ws/transcribe/"
    await listen_to_websocket(uri)