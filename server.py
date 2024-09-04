# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
# from fastapi.staticfiles import StaticFiles
# from whisper import load_model, transcribe
# import numpy as np
# import io
# import os
# import ssl
# import logging
# import audiofile
# from loguru import logger
# import sys
# from fastapi.middleware.cors import CORSMiddleware


# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust as necessary
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# app.mount("/static", StaticFiles(directory="static"), name="static")
# BUFFER_SIZE = 1024 * 1024
# ssl._create_default_https_context = ssl._create_unverified_context
# model = load_model("base")

# logger.add("server_log.log", rotation="1 MB")
# logger.add(sys.stdout, level="INFO")

# def is_valid_audio_format(audio_data):
#     try:
#         audio_file = io.BytesIO(audio_data)
#         with audiofile.SoundFile(audio_file) as sf:
#             sample_rate = sf.samplerate
#             num_channels = sf.channels
#             duration = sf.frames / sf.samplerate
#             ACCEPTABLE_SAMPLE_RATES = [8000, 16000, 44100, 48000]
#             ACCEPTABLE_NUM_CHANNELS = [1, 2]  # Mono or Stereo
#             MAX_DURATION = 600  # Maximum duration in seconds (10 minutes)
            
#             if sample_rate not in ACCEPTABLE_SAMPLE_RATES:
#                 return False
#             if num_channels not in ACCEPTABLE_NUM_CHANNELS:
#                 return False
#             if duration > MAX_DURATION:
#                 return False
#             return True
#     except Exception as e:
#         print(f"Error in audio validation: {str(e)}")
#         return False


# def safe_transcribe(model, audio):
#     try:
#         result = model.transcribe(audio)
#         logits = result.get("logits", None)
        
#         if logits is not None and np.isnan(logits).any():
#             raise ValueError("Received NaN values in logits.")
        
#         return result
#     except Exception as e:
#         return {"error": str(e)}

# @app.websocket("/transcribe")
# async def websocket_endpoint(websocket: WebSocket):
#     logger.info("Received connection request.")
#     try:
#         await websocket.accept()
#         logger.info("WebSocket connection accepted.")
#         audio_data = b""
        
#         while True:
#             try:
#                 data = await websocket.receive_bytes()
#                 logger.info(f"Received data of length {len(data)} bytes.")
#                 audio_data += data
                
#                 if len(audio_data) >= BUFFER_SIZE:
#                     if not is_valid_audio_format(audio_data):
#                         await websocket.send_text("Invalid audio format.")
#                         audio_data = b""  # Reset buffer
#                         continue
                    
#                     audio_np = np.frombuffer(audio_data, dtype=np.float32)
#                     if len(audio_np) > 0:
#                         audio = io.BytesIO(audio_data)
#                         try:
#                             result = safe_transcribe(model, audio)
#                             if "error" in result:
#                                 await websocket.send_text(f"Transcription error: {result['error']}")
#                             else:
#                                 await websocket.send_text(result["text"])
#                                 logger.info(f"Transcription result: {result}")
#                         except Exception as e:
#                             await websocket.send_text(f"Transcription error: {str(e)}")
#                     audio_data = b""  # Reset buffer
#             except WebSocketDisconnect:
#                 logging.info("WebSocket connection closed")
#                 break
#             except Exception as e:
#                 await websocket.send_text(f"Error during processing: {str(e)}")
#                 logging.error(f"Error during processing: {str(e)}")
#     except HTTPException as e:
#         logger.error(f"HTTP Exception: {e.detail}")
#         raise e
#     except Exception as e:
#         logger.error(f"Error occurred: {e}")
#         await websocket.close()

# @app.post("/transcribe/")
# async def transcribe_file(file: UploadFile = File(...)):
#     try:
#         file_contents = await file.read()
#         file_path = f"temp_{file.filename}"
#         with open(file_path, "wb") as f:
#             f.write(file_contents)
        
#         result = model.transcribe(file_path)
#         detected_language = result["language"]
#         os.remove(file_path)
        
#         if detected_language in ['en', 'hi']:
#             return {"transcription": result["text"]}
#         else:
#             return {"error": "Language not supported", "language": detected_language}
#     except Exception as e:
#         return {"error": str(e)}


from fastapi import FastAPI, WebSocket
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.websocket("/ws/test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logging.info("WebSocket connection accepted.")
    while True:
        try:
            data = await websocket.receive_text()
            logging.info(f"Received message: {data}")
            await websocket.send_text(f"Message received: {data}")
        except Exception as e:
            logging.error(f"Error: {e}")
            await websocket.close()
            break