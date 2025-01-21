from flask import Flask, request, jsonify, send_file, make_response
from gtts import gTTS
import os
import speech_recognition as sr
import io
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})

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
@app.route('/tts', methods=['POST', 'OPTIONS'])
def tts():
    if request.method == 'OPTIONS':
        return make_response('', 204)

    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        text = data['text']
        if not isinstance(text, str) or not text.strip():
            return jsonify({'error': 'Invalid text provided'}), 400

        # Create a BytesIO object to store the audio
        audio_io = io.BytesIO()
        
        # Generate the audio file
        tts = gTTS(text=text.strip(), lang='en', slow=False)
        tts.write_to_fp(audio_io)
        
        # Seek to the beginning of the BytesIO object
        audio_io.seek(0)
        
        # Create the response
        response = make_response(send_file(
            audio_io,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='speech.mp3'
        ))
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Content-Type'] = 'audio/mpeg'
        
        return response

    except Exception as e:
        print(f"Error in TTS conversion: {str(e)}")
        return jsonify({'error': f'TTS conversion failed: {str(e)}'}), 500

# Speech-to-Text (STT) route
@app.route('/stt', methods=['POST'])
def stt():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    recognizer = sr.Recognizer()
    
    try:
        # Convert the uploaded audio file to speech recognition format
        audio = sr.AudioFile(file)
        with audio as source:
            audio_data = recognizer.record(source)
        
        text = recognizer.recognize_google(audio_data)
        return jsonify({'text': text})
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand audio'}), 400
    except sr.RequestError:
        return jsonify({'error': 'Could not request results from Google Speech Recognition service'}), 500
    except Exception as e:
        return jsonify({'error': f'STT conversion failed: {str(e)}'}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
