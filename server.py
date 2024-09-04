from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
import whisper
import numpy as np
import ssl
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

ssl._create_default_https_context = ssl._create_unverified_context
model = whisper.load_model("base")

@app.websocket("/ws/transcribe/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = []
    try:
        while True:
            data = await websocket.receive_bytes()
            print(f"Received {len(data)} bytes")
            audio_buffer.append(data)
            try:
                audio_bytes = b"".join(audio_buffer)
                audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
                
                if len(audio_data) > 16000:
                    result = model.transcribe(audio_data)
                    detected_language = result["language"]
                    if detected_language in ['en', 'hi']:
                        await websocket.send_text(result["text"])
                    else:
                        await websocket.send_text("Language not supported: " + detected_language)
                    audio_buffer = []
                else:
                    print("Audio buffer too short, waiting for more data...")
            except Exception as e:
                print(f"Error processing audio: {e}")
                await websocket.send_text(f"Error processing audio: {e}")
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
        
        # Use Whisper to transcribe the file
        result = model.transcribe(file_path)
        detected_language = result["language"]
        
        # Clean up temporary file
        os.remove(file_path)
        
        if detected_language in ['en', 'hi']:
            return {"transcription": result["text"]}
        else:
            return {"error": "Language not supported", "language": detected_language}
    except Exception as e:
        return {"error": str(e)}