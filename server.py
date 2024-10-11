import sys
sys.path.append('/Users/deep2.usdadiya/Desktop/Speech to text/speech_to_text/deep/lib/python3.11/site-packages')
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
import whisper
import numpy as np
import ssl
import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
import torch
from fastapi.responses import JSONResponse
import tempfile
from pydub import AudioSegment
import uvicorn

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

device = torch.device("cpu")
torch.set_num_threads(4)

model = whisper.load_model("large", device=device)


# @app.websocket("/ws/transcribe/")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     audio_buffer = b""
#     try:
#         while True:
#             data = await websocket.receive_bytes()
#             audio_buffer += data
#             print(f"Received {len(data)} bytes of data.")  
#             audio_data = np.frombuffer(audio_buffer, dtype=np.int16)
#             if audio_data.size == 0:
#                 raise ValueError("Converted audio data is empty. Ensure that the input data is correct.")
#             audio_data = audio_data.astype(np.float32) / 32768.0
#             if len(audio_data) > 16000: 
#                 print(f"Processing {len(audio_data)} samples of audio data.")  
#                 result = model.transcribe(audio_data)
#                 detected_language = result["language"]
#                 print(f"Detected language: {detected_language}, Transcription: {result['text']}")
#                 if detected_language in ['en', 'hi']:
#                     logging.debug(f"Sending transcription message")
#                     await websocket.send_text(result["text"])
#                 elif detected_language == 'nn':
#                     logging.debug("Mapped 'nn' (Norwegian) to 'en' (English).")
#                     await websocket.send_text(result["text"])
#                 else:
#                     await websocket.send_text("Language not supported: " + detected_language)
#                 audio_buffer = b""
#             else:
#                 print("Audio buffer too short, waiting for more data...")
#     except WebSocketDisconnect:
#         print("Client disconnected")
#     except Exception as e:
#         print(f"Error: {e}")
#         await websocket.close()


# @app.post("/transcribe/")
# async def transcribe_audio(file: UploadFile = File(...)):
#     # # Check if the uploaded file is an audio file
#     if not file.content_type.startswith("audio/"):
#         return JSONResponse(content={"error": "File type not supported. Please upload an audio file."}, status_code=400)

#     # Create a temporary file to save the uploaded audio
#     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#         try:
#             # Save the uploaded audio to the temporary file
#             temp_file.write(await file.read())
#             temp_file_path = temp_file.name

#             # Use Whisper to transcribe the audio
#             audio = whisper.load_audio(temp_file_path)
#             audio = whisper.pad_or_trim(audio)

#             # Make a prediction
#             result = model.transcribe(audio)

#             # Return the transcribed text
#             return JSONResponse(content={"transcription": result["text"]})

#         except Exception as e:
#             return JSONResponse(content={"error": str(e)}, status_code=500)
#         finally:
#             # Clean up the temporary file
#             if os.path.exists(temp_file_path):
#                 os.remove(temp_file_path)

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import re

def generic_romanize_hindi(text):
    """
    Romanizes the Hindi text using a generic approach with minimal hardcoding.
    """
    # Step 1: Transliterate from Devanagari to WX notation, which is simpler and closer to Hinglish
    transliterated_text = transliterate(text, sanscript.DEVANAGARI, sanscript.WX)

    # Step 2: Post-process transliterated text for common phonetic simplifications
    transliterated_text = apply_phonetic_simplifications(transliterated_text)

    # Step 3: Normalize output (optional based on desired formatting)
    transliterated_text = transliterated_text.lower()  # Convert to lowercase for easier reading
    
    return transliterated_text

def apply_phonetic_simplifications(text):
    """
    Applies generic phonetic simplifications to improve the natural feel of transliterations.
    """
    # Remove nasal sounds (these are often marked with M in WX notation, remove them for readability)
    text = re.sub(r'M', '', text)

    # Simplify common vowel patterns
    text = re.sub(r'aa', 'a', text)   # Shorten long vowels
    text = re.sub(r'ii', 'i', text)   # Shorten long vowels (example: "kii" -> "ki")
    text = re.sub(r'uu', 'u', text)   # Shorten long vowels (example: "huu" -> "hu")

    # Replace capitalized vowel markers (which can represent emphasis or stress in certain schemes)
    text = re.sub(r'[AI]', 'a', text)
    
    return text


@app.websocket("/ws/transcribe/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = b""
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_buffer += data
            print(f"Received {len(data)} bytes of data.")  
            audio_data = np.frombuffer(audio_buffer, dtype=np.int16)
            if audio_data.size == 0:
                raise ValueError("Converted audio data is empty. Ensure that the input data is correct.")
            audio_data = audio_data.astype(np.float32) / 32768.0
            if len(audio_data) > 16000: 
                print(f"Processing {len(audio_data)} samples of audio data.")  
                result = model.transcribe(audio_data)
                detected_language = result["language"]
                transcription_text = result["text"]
                print(f"Detected language: {detected_language}, Transcription: {transcription_text}")

                if detected_language == 'hi':  # If language is Hindi
                    # Generic Romanize the transcription
                    transcription_text = generic_romanize_hindi(transcription_text)
                
                if detected_language in ['en', 'hi']:
                    logging.debug(f"Sending transcription message")
                    await websocket.send_text(transcription_text)
                elif detected_language == 'nn':
                    logging.debug("Mapped 'nn' (Norwegian) to 'en' (English).")
                    await websocket.send_text(transcription_text)
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
async def transcribe_audio(file: UploadFile = File(...)):
    # # Check if the uploaded file is an audio file
    if not file.content_type.startswith("audio/"):
        return JSONResponse(content={"error": "File type not supported. Please upload an audio file."}, status_code=400)

    # Create a temporary file to save the uploaded audio
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            # Save the uploaded audio to the temporary file
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

            # Use Whisper to transcribe the audio
            audio = whisper.load_audio(temp_file_path)
            audio = whisper.pad_or_trim(audio)

            # Make a prediction
            result = model.transcribe(audio)
            detected_language = result["language"]
            transcription_text = result["text"]

            # If the detected language is Hindi, generic romanize the transcription
            if detected_language == 'hi':
                transcription_text = generic_romanize_hindi(transcription_text)

            # Return the transcribed (and possibly romanized) text
            return JSONResponse(content={"transcription": transcription_text})

        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8500)