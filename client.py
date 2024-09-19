import asyncio
import websockets
import sounddevice as sd
import numpy as np

async def send_audio(uri):
    async with websockets.connect(uri) as websocket:
        loop = asyncio.get_event_loop()
        def callback(indata, frames, time, status):
            if status:
                print(status)
            asyncio.run_coroutine_threadsafe(websocket.send(indata.tobytes()), loop)
        with sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=callback):
            print("Start speaking...")
            while True:
                try:
                    message = await websocket.recv()
                    print("Transcription:", message)
                except websockets.ConnectionClosed:
                    print("Connection closed by server.")
                    break
                except Exception as e:
                    print(f"An error occurred: {e}")
                    break
                
                
asyncio.run(send_audio("ws://127.0.0.1:8000/ws/transcribe/"))