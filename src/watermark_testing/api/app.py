from flask import Flask, jsonify, request, send_file, render_template
import os
import sys
from pathlib import Path

# Füge den Parent-Ordner zum Path hinzu
sys.path.append(str(Path(__file__).parent.parent))

from aimodels.AudioSeal.audioseal_handler import prepare_audio, embed_watermark, save_audio

# Flask App mit Templates-Ordner
app = Flask(__name__, template_folder='../templates')

# Upload-Ordner erstellen
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Frontend anzeigen
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

# Neuer Endpoint: Audio-Datei hochladen

#testen mit:
#curl -X POST -F "audio=@F:\Uni\8tes Semester\Bachelorarbeit\Bachelor_Arbeit\einleitung.wav" 
# http://localhost:5000/upload
@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'Keine Datei gefunden'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    return jsonify({
        'message': 'Datei erfolgreich hochgeladen',
        'filename': file.filename,
        'path': filepath
    }), 200

# App starten
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)