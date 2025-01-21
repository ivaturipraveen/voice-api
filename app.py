from flask import Flask, request, jsonify, send_file
from gtts import gTTS
import os
import speech_recognition as sr
import io
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

# Root route for basic information
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Text-to-Speech and Speech-to-Text API!",
        "endpoints": {
            "/tts": "POST with JSON payload { 'text': 'Your text here' } for text-to-speech conversion.",
            "/stt": "POST with an audio file for speech-to-text conversion."
        }
    })

# Text-to-Speech (TTS) route
@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    tts = gTTS(text=text, lang='en')
    audio_io = io.BytesIO()
    tts.save(audio_io)
    audio_io.seek(0)
    
    return send_file(audio_io, mimetype='audio/mpeg')

# Speech-to-Text (STT) route
@app.route('/stt', methods=['POST'])
def stt():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    recognizer = sr.Recognizer()
    
    # Convert the uploaded audio file to speech recognition format
    audio = sr.AudioFile(file)
    with audio as source:
        audio_data = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio_data)
        return jsonify({'text': text})
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand audio'}), 400
    except sr.RequestError:
        return jsonify({'error': 'Could not request results from Google Speech Recognition service'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
