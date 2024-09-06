from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
import whisper
import numpy as np
import ssl
import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

ssl._create_default_https_context = ssl._create_unverified_context
model = whisper.load_model("base")

@app.websocket("/ws/transcribe/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = b""
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_buffer += data
            print(f"Received {len(data)} bytes of data.")  # Debugging
            audio_data = np.frombuffer(audio_buffer, dtype=np.int16)
            if audio_data.size == 0:
                raise ValueError("Converted audio data is empty. Ensure that the input data is correct.")
            audio_data = audio_data.astype(np.float32) / 32768.0
            if len(audio_data) > 16000: 
                print(f"Processing {len(audio_data)} samples of audio data.")  # Debugging
                result = model.transcribe(audio_data)
                detected_language = result["language"]
                print(f"Detected language: {detected_language}, Transcription: {result['text']}")
                if detected_language in ['en', 'hi']:
                    logging.debug(f"Sending transcription message")
                    await websocket.send_text(result["text"])
                else:
                    await websocket.send_text("Language not supported: " + detected_language)
                audio_buffer = b""
            else:
                print("Audio buffer too short, waiting for more data...")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()

@app.post("/transcribe/")
async def transcribe_file(file: UploadFile = File(...)):
    try:
        file_contents = await file.read()
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file_contents)
        result = model.transcribe(file_path)
        detected_language = result["language"]  
        os.remove(file_path)
        if detected_language in ['en', 'hi']:
            return {"transcription": result["text"]}
        else:
            return {"error": "Language not supported", "language": detected_language}
    except Exception as e:
        return {"error": str(e)}