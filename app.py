from flask import Flask, request, jsonify, send_file
from gtts import gTTS
import os
import speech_recognition as sr
import io
from pydub import AudioSegment

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()
    text = data.get('text')
    tts = gTTS(text=text, lang='en')
    audio_io = io.BytesIO()
    tts.save(audio_io)
    audio_io.seek(0)
    return send_file(audio_io, mimetype='audio/mpeg')

@app.route('/stt', methods=['POST'])
def stt():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    recognizer = sr.Recognizer()
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
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
