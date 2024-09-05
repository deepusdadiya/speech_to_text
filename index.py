import streamlit as st
import requests
import asyncio
import websockets
from threading import Thread

st.set_page_config(page_title="Audio Transcription Service")

st.title("Audio Transcription Service")

st.header("Batch Transcription")
audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])

if st.button("Upload and Transcribe"):
    if audio_file is not None:
        with st.spinner('Transcribing...'):
            response = requests.post(
                "http://127.0.0.1:8000/transcribe/",
                files={"file": audio_file.getvalue()}
            )
        if response.status_code == 200:
            st.write("Transcription:")
            st.write(response.json().get("transcription", "No transcription available"))
        else:
            st.write("Error:", response.json().get("error", "Unknown error"))
    else:
        st.write("Please upload a file first.")


st.subheader("Batch Transcription Output")
batch_transcription_output = st.empty()


st.header("Real-Time Transcription")

start_button = st.button("Start Real-Time Transcription")
stop_button = st.button("Stop Real-Time Transcription")


st.subheader("Real-Time Transcription Output")
real_time_transcription_output = st.empty()


async def real_time_transcription():
    uri = 'ws://127.0.0.1:8000/ws/transcribe/'
    async with websockets.connect(uri) as socket:
        try:
            while True:
                message = await socket.recv()
                real_time_transcription_output.text(message)
        except websockets.ConnectionClosed:
            real_time_transcription_output.text("Connection closed.")
        except Exception as e:
            real_time_transcription_output.text(f"Error: {e}")

def start_websocket_loop():
    asyncio.run(real_time_transcription())

if start_button:
    if 'websocket_thread' not in st.session_state or not st.session_state.websocket_thread.is_alive():
        st.session_state.websocket_thread = Thread(target=start_websocket_loop)
        st.session_state.websocket_thread.start()
    st.write("Connected to server. Start speaking...")

if stop_button and 'websocket_thread' in st.session_state:
    st.session_state.websocket_thread.join(timeout=1)  
    st.write("Real-time transcription stopped.")