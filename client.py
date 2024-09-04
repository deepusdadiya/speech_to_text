# import asyncio
# import websockets
# import sounddevice as sd
# import numpy as np
# import logging

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# async def send_audio(uri):
#     logging.info(f"Attempting to connect to WebSocket server at {uri}")
#     try:
#         async with websockets.connect(uri) as websocket:
#             logging.info("WebSocket connection established successfully.")
#             loop = asyncio.get_event_loop()

#             def callback(indata, frames, time, status):
#                 if status:
#                     logging.warning(f"Input stream status: {status}")
#                 audio_data = indata.flatten().astype(np.float32) / 32768.0
#                 asyncio.run_coroutine_threadsafe(websocket.send(audio_data.tobytes()), loop)

#             with sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=callback, blocksize=16000):
#                 logging.info("Audio stream opened. Start speaking...")
#                 while True:
#                     try:
#                         message = await websocket.recv()
#                         logging.info(f"Transcription received: {message}")
#                     except websockets.exceptions.ConnectionClosedOK:
#                         logging.info("Connection closed by server.")
#                         break
#                     except Exception as e:
#                         logging.error(f"An error occurred while receiving a message: {e}")
#                         break
#     except websockets.exceptions.InvalidStatusCode as e:
#         logging.error(f"WebSocket connection failed with status code: {e.status_code}")
#     except Exception as e:
#         logging.error(f"An unexpected error occurred: {e}")

# if __name__ == "__main__":
#     asyncio.run(send_audio("ws://127.0.0.1:8000/ws/transcribe/"))

import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)

async def test_websocket(uri):
    async with websockets.connect(uri) as websocket:
        logging.info("WebSocket connection established.")
        await websocket.send("Hello, server!")
        response = await websocket.recv()
        logging.info(f"Server response: {response}")

if __name__ == "__main__":
    asyncio.run(test_websocket("ws://127.0.0.1:8000/ws/test"))