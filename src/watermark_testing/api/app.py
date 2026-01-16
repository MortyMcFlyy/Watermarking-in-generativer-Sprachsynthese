from contextlib import contextmanager
from flask import Flask, jsonify, request, send_file, render_template
import os
import sys
from pathlib import Path

# Füge den Parent-Ordner zum Path hinzu
sys.path.append(str(Path(__file__).parent.parent))

# Imports
from database.database import init_db, get_db
from database.repositories import UserRepository, AudioFileRepository
from services.audio_service import AudioService
from services.watermark_business_service import WatermarkBusinessService
from services.watermark_strategy import WatermarkStrategyFactory

# Flask App 
app = Flask(__name__)

# Upload-Ordner erstellen
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Datenbank initialisieren beim Start
init_db()

# ==========================================
# ROUTES
# ==========================================

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


# ==========================================
# SCHNITTSTELLE 1: Upload + DB-Speicherung
# ==========================================
@app.route('/upload', methods=['POST'])
def upload_audio():
    """
    Upload einer Audio-Datei.
    - Speichert Datei im Filesystem
    - Extrahiert Metadaten
    - Speichert Eintrag in DB via Repository
    """
    # Validierung
    if 'audio' not in request.files:
        return jsonify({'error': 'Keine Datei gefunden'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400
    
    try:
        # Business Logic via Service
        with get_db() as db:
            audio_repo = AudioFileRepository(db)
            business_service = WatermarkBusinessService(audio_repo)
            
            user_id = 1  # TODO: Aus Session holen
            
            result = business_service.upload_audio_workflow(
                file=file,
                upload_folder=UPLOAD_FOLDER,
                user_id=user_id
            )
        
        return jsonify({
            'message': 'Datei erfolgreich hochgeladen',
            'audio_id': result['audio_id'],
            'filename': result['filename'],
            'metadata': result['metadata']
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # TODO: Proper logging statt Exception-Details an Client
        return jsonify({'error': f'Interner Serverfehler: {str(e)}'}), 500


# ==========================================
# SCHNITTSTELLE 2: Watermark Embedding + DB-Update
# ==========================================
@app.route('/watermark/embed', methods=['POST'])
def embed():
    """
    Embed Watermark in Audio.
    - Upload + Watermarking (AudioSeal oder PerTh)
    - Speichert Original UND Watermarked in DB
    """
    # Validierung
    if 'audio' not in request.files:
        return jsonify({'error': 'Keine Datei gefunden'}), 400
    
    file = request.files['audio']
    method = request.form.get('method', 'audioseal')
    
    if file.filename == '':
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400
    
    # Methoden-Validierung
    available_methods = WatermarkStrategyFactory.available_methods()
    if method not in available_methods:
        return jsonify({
            'error': f'Ungültige Methode. Verfügbar: {", ".join(available_methods)}'
        }), 400
    
    try:
        # Business Logic via Service
        with get_db() as db:
            audio_repo = AudioFileRepository(db)
            business_service = WatermarkBusinessService(audio_repo)
            
            user_id = 1  # TODO: Aus Session holen
            
            output_path, metadata = business_service.embed_watermark_workflow(
                file=file,
                method=method,
                upload_folder=UPLOAD_FOLDER,
                user_id=user_id
            )
        
        # Datei zum Download senden
        return send_file(
            output_path,
            as_attachment=True,
            download_name=metadata['output_filename']
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # TODO: Proper logging
        return jsonify({'error': f'Interner Serverfehler: {str(e)}'}), 500


# ==========================================
# SCHNITTSTELLE 3: Watermark Detection + DB-Logging
# ==========================================
@app.route('/watermark/detect', methods=['POST'])
def detect():
    """
    Detect Watermark in Audio.
    - Upload + Detection (AudioSeal oder PerTh)
    - Speichert Detection-Ergebnis in DB
    """
    # Validierung
    if 'audio' not in request.files:
        return jsonify({'error': 'Keine Datei gefunden'}), 400
    
    file = request.files['audio']
    method = request.form.get('method', 'audioseal')
    
    if file.filename == '':
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400
    
    # Methoden-Validierung
    available_methods = WatermarkStrategyFactory.available_methods()
    if method not in available_methods:
        return jsonify({
            'error': f'Ungültige Methode. Verfügbar: {", ".join(available_methods)}'
        }), 400
    
    try:
        # Business Logic via Service
        with get_db() as db:
            audio_repo = AudioFileRepository(db)
            business_service = WatermarkBusinessService(audio_repo)
            
            user_id = 1  # TODO: Aus Session holen
            
            detection_result = business_service.detect_watermark_workflow(
                file=file,
                method=method,
                upload_folder=UPLOAD_FOLDER,
                user_id=user_id
            )
        
        return jsonify(detection_result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # TODO: Proper logging
        return jsonify({'error': f'Interner Serverfehler: {str(e)}'}), 500


# ==========================================
# SCHNITTSTELLE 4: File Download aus DB
# ==========================================
@app.route('/download/<int:audio_id>', methods=['GET'])
def download_audio(audio_id: int):
    """
    Download einer gespeicherten Audio-Datei.
    - Holt Datei-Info aus DB via Repository
    - Sendet Datei an Client
    """
    try:
        with get_db() as db:
            audio_repo = AudioFileRepository(db)
            
            # Datei aus DB holen
            audio_file = audio_repo.get_by_id(audio_id)
            
            if not audio_file:
                return jsonify({'error': 'Datei nicht gefunden'}), 404
            
            # Prüfen ob Datei existiert
            if not os.path.exists(audio_file.file_path):
                return jsonify({'error': 'Datei im Filesystem nicht gefunden'}), 404
            
            return send_file(
                audio_file.file_path,
                as_attachment=True,
                download_name=audio_file.filename
            )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# SCHNITTSTELLE 5: Liste aller Dateien eines Users
# ==========================================
@app.route('/files', methods=['GET'])
def list_user_files():
    """
    Gibt alle Audio-Dateien eines Users zurück.
    """
    try:
        with get_db() as db:
            audio_repo = AudioFileRepository(db)
            user_id = 1  # TODO: Aus Session
            
            files = audio_repo.get_by_user(user_id)
            
            return jsonify({
                'count': len(files),
                'files': [
                    {
                        'id': f.id,
                        'filename': f.filename,
                        'has_watermark': f.has_watermark,
                        'watermark_type': f.watermark_type,
                        'duration': f.duration,
                        'created_at': f.created_at.isoformat()
                    }
                    for f in files
                ]
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# App starten
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)