import streamlit as st
import requests
import asyncio
import websockets

# Set up the Streamlit page
st.set_page_config(page_title="Audio Transcription Service")

st.title("Audio Transcription Service")

# Section 1: Batch Processing Input
st.header("Batch Transcription")
audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])

if st.button("Upload and Transcribe"):
    if audio_file is not None:
        # Send the file to the FastAPI server
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

# Section 2: Batch Processing Output
st.subheader("Batch Transcription Output")
batch_transcription_output = st.empty()

# Section 3: Real-Time Processing Input
st.header("Real-Time Transcription")

start_button = st.button("Start Real-Time Transcription")
stop_button = st.button("Stop Real-Time Transcription")

# Section 4: Real-Time Processing Output
st.subheader("Real-Time Transcription Output")
real_time_transcription_output = st.empty()

# WebSocket connection for real-time transcription
socket = None

async def real_time_transcription():
    global socket
    socket = await websockets.connect('ws://127.0.0.1:8000/ws/transcribe/')
    await socket.send("Start speaking...")

    try:
        async for message in socket:
            real_time_transcription_output.text(message)
    except websockets.ConnectionClosed:
        real_time_transcription_output.text("Connection closed.")

if start_button:
    st.write("Connected to server. Start speaking...")
    asyncio.run(real_time_transcription())

if stop_button and socket:
    asyncio.run(socket.close())
    real_time_transcription_output.text("Real-time transcription stopped.")