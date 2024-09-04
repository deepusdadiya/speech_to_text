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
    audio_buffer = b""

    try:
        while True:
            data = await websocket.receive_bytes()
            audio_buffer += data

            try:
                # Logging the received bytes
                print(f"Received {len(data)} bytes of data.")

                # Assuming incoming audio is in int16 format
                audio_data = np.frombuffer(audio_buffer, dtype=np.int16)

                # Check if audio_data is empty after conversion
                if audio_data.size == 0:
                    raise ValueError("Converted audio data is empty. Ensure that the input data is correct.")

                # Convert to float32 as Whisper expects normalized audio
                audio_data = audio_data.astype(np.float32) / 32768.0

                if len(audio_data) > 16000:  # 1 second of audio at 16kHz
                    # Process audio buffer with Whisper
                    result = model.transcribe(audio_data)
                    detected_language = result["language"]
                    if detected_language in ['en', 'hi']:
                        await websocket.send_text(result["text"])
                    else:
                        await websocket.send_text("Language not supported: " + detected_language)
                    audio_buffer = b""  # Reset buffer after processing
                else:
                    print("Audio buffer too short, waiting for more data...")
            except Exception as e:
                print(f"Error processing audio: {e}")
                await websocket.send_text(f"Error processing audio: {e}")
                audio_buffer = b""  # Clear the buffer in case of error
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