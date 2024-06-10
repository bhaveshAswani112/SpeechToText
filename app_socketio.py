import logging
import io
from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
import faster_whisper

load_dotenv()

app_socketio = Flask("app_socketio")
socketio = SocketIO(app_socketio, cors_allowed_origins='*')

# Load the personal model
model_directory = "E:/Desktop/AI_Applications/convertedModel"
model = faster_whisper.WhisperModel(model_directory)
print("moadel loaded")

# Global buffer to collect audio data
audio_buffer = io.BytesIO()

def transcribe_audio(audio_bytes):
    logging.info("Transcribing audio")
    # Save audio bytes to a temporary file
    audio_buffer.write(audio_bytes)
    audio_buffer.seek(0)
    
    # Transcribe the audio buffer using the loaded model
    try:
        segments, _ = model.transcribe(audio_buffer)
        # Combine segments to get the full transcription
        transcription = " ".join([segment.text for segment in segments])
        logging.info(f"Transcription result: {transcription}")
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        transcription = ""
    
    # Clear the buffer after transcription
    audio_buffer.seek(0)
    audio_buffer.truncate(0)
    
    return transcription

@socketio.on('audio_stream')
def handle_audio_stream(data):
    logging.info("Received audio stream")
    try:
        # print("Me data hu" + data)
        print("I am above audio bytes.")
        print(type(data))
        audio_bytes = data["audio"] # Assuming 'data' contains raw audio bytes
        if isinstance(audio_bytes, str):
            audio_bytes = audio_bytes.encode('utf-8')
        # print(audio_bytes)
        print("I am below audio bytes")
        if audio_bytes:
            logging.info("Audio bytes received, starting transcription")
            transcription = transcribe_audio(audio_bytes)
            if transcription:
                logging.info(f"Transcription: {transcription}")
                socketio.emit('transcription_update', {'transcription': transcription})
            else:
                logging.warning("No transcription received")
        else:
            logging.warning("No audio bytes received")
    except Exception as e:
        logging.error(f"Error handling audio stream: {e}")

@socketio.on('toggle_transcription')
def handle_toggle_transcription(data):
    logging.info(f"Received toggle_transcription event with data: {data}")
    print(data)
    action = data["action"]
    
    if not action:
        logging.error("No action provided in toggle_transcription event")
        return

    if action == "start":
        logging.info("Starting transcription")
        # Perform any initialization if needed
    elif action == "stop":
        logging.info("Stopping transcription")
        # Perform any cleanup or shutdown tasks if needed
    else:
        logging.warning(f"Unknown action: {action}")

        # Perform any initialization if needed

@socketio.on('connect')
def server_connect():
    logging.info('Client connected')

@socketio.on('restart_transcription')
def restart_transcription():
    logging.info('Restarting transcription')
    # Perform any re-initialization if needed

if __name__ == '__main__':
    logging.info("Starting SocketIO server.")
    try:
        socketio.run(app_socketio, debug=True, allow_unsafe_werkzeug=True, port=5001)
    except Exception as e:
        logging.error(f"Failed to start server: {e}")