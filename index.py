import streamlit as st
import requests
import asyncio
import websockets

st.set_page_config(page_title="Audio Transcription Service")

st.title("Audio Transcription Service")

# Batch Transcription Section
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

# Real-Time Transcription Section
st.header("Real-Time Transcription")

start_button = st.button("Start Real-Time Transcription")
stop_button = st.button("Stop Real-Time Transcription")

st.subheader("Real-Time Transcription Output")
real_time_transcription_output = st.empty()

# WebSocket connection URL
WS_URL = "ws://127.0.0.1:8000/ws/transcribe/"

# Initialize session state if not already
if 'real_time_transcription' not in st.session_state:
    st.session_state['real_time_transcription'] = "Waiting for real-time transcription..."
if 'websocket_connected' not in st.session_state:
    st.session_state.websocket_connected = False

async def real_time_transcription():
    async with websockets.connect(WS_URL) as websocket:
        while st.session_state.websocket_connected:
            try:
                message = await websocket.recv()
                st.session_state['real_time_transcription'] = message
                # Debug output to check if messages are being received
                print(f"Received message: {message}")
            except Exception as e:
                st.session_state['real_time_transcription'] = f"Error: {e}"
            await asyncio.sleep(1)  # Sleep to prevent excessive CPU usage

# Manage WebSocket connection
def manage_websocket_connection():
    if st.session_state.websocket_connected:
        asyncio.run(real_time_transcription())

# Start WebSocket transcription
if start_button and not st.session_state.websocket_connected:
    st.session_state.websocket_connected = True
    st.write("Real-time transcription started.")
    manage_websocket_connection()

# Stop WebSocket transcription
if stop_button and st.session_state.websocket_connected:
    st.session_state.websocket_connected = False
    st.write("Real-time transcription stopped.")

# Display real-time transcription
real_time_transcription_output.text(st.session_state['real_time_transcription'])