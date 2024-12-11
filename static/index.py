import streamlit as st
import requests
import asyncio
import websockets
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(page_title="Audio Transcription Service")

st.title("Audio Transcription Service")

st.header("Batch Transcription")
audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])


if st.button("Upload and Transcribe"):
    logging.debug("Upload and Transcribe button clicked.")
    if audio_file is not None:
        with st.spinner('Transcribing...'):
            logging.debug("Audio file uploaded. Sending POST request for transcription.")
            response = requests.post("http://127.0.0.1:8500/transcribe/",files={"file": audio_file.getvalue()})
            logging.debug(f"Response received: {response.status_code}")
        if response.status_code == 200:
            st.write("Transcription:")
            st.write(response.json().get("transcription", "No transcription available"))
            logging.debug(f"Transcription result: {response.json().get('transcription')}")
        else:
            st.write("Error:", response.json().get("error", "Unknown error"))
            logging.error(f"Error during transcription: {response.json().get('error')}")
    else:
        st.write("Please upload a file first.")
        logging.warning("No audio file uploaded before transcription.")

st.subheader("Batch Transcription Output")
batch_transcription_output = st.empty()

st.header("Real-Time Transcription")

start_button = st.button("Start Real-Time Transcription")
stop_button = st.button("Stop Real-Time Transcription")

st.subheader("Real-Time Transcription Output")
real_time_transcription_output = st.empty()

WS_URL = "ws://127.0.0.1:8500/ws/transcribe/"

if 'real_time_transcription' not in st.session_state:
    st.session_state['real_time_transcription'] = "Waiting for real-time transcription..."
if 'websocket_connected' not in st.session_state:
    st.session_state.websocket_connected = False


async def send_audio_data(websocket):
    try:
        logging.debug("Sending audio data.")
        with open('sample-0.mp3', 'rb') as audio:  
            data = audio.read(1024) 
            while data and st.session_state.websocket_connected:
                await websocket.send(data)
                logging.debug("Sent audio chunk over WebSocket.")
                data = audio.read(1024)
                await asyncio.sleep(0.1)  
    except Exception as e:
        logging.error(f"Error while sending audio data: {e}")


async def real_time_transcription():
    logging.debug("Attempting to connect to WebSocket.")
    async with websockets.connect(WS_URL) as websocket:
        logging.info("WebSocket connection established.")
        await send_audio_data(websocket)
        
        while st.session_state.websocket_connected:
            logging.info("Listening for transcription from WebSocket.")
            try:
                message = await websocket.recv()
                if message:
                    logging.debug(f"Message received from WebSocket: {message}")
                    if message.strip():  # Check if the message is not just whitespace
                        st.session_state['real_time_transcription'] = message
                        real_time_transcription_output.text(st.session_state['real_time_transcription'])
                    else:
                        logging.warning("Received an empty or whitespace message from WebSocket.")
                else:
                    logging.error("Received an empty message from WebSocket.")
            except Exception as e:
                logging.error(f"Error during WebSocket message handling: {e}")
                st.session_state['real_time_transcription'] = f"Error: {e}"
            await asyncio.sleep(1)


def run_asyncio_task():
    logging.debug("Running asyncio task for real-time transcription.")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(real_time_transcription())
    logging.debug("Asyncio task completed.")

if start_button and not st.session_state.websocket_connected:
    logging.debug("Start button clicked. Starting WebSocket transcription.")
    st.session_state.websocket_connected = True
    st.write("Real-time transcription started.")
    run_asyncio_task()

if stop_button and st.session_state.websocket_connected:
    logging.debug("Stop button clicked. Stopping WebSocket transcription.")
    st.session_state.websocket_connected = False
    st.write("Real-time transcription stopped.")


real_time_transcription_output.text(st.session_state['real_time_transcription'])


logging.debug("End of script.")