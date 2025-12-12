from flask import Flask, jsonify, request, send_file, render_template
import os
import sys
from pathlib import Path

# Füge den Parent-Ordner zum Path hinzu
sys.path.append(str(Path(__file__).parent.parent))

from aimodels.AudioSeal.audioseal_handler import prepare_audio, embed_watermark, detect_watermark, save_audio
from database.database import init_db, SessionLocal
from database.repositories import UserRepository, AudioFileRepository
from services.audio_service import AudioService

# Flask App 
app = Flask(__name__)

# Upload-Ordner erstellen
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Datenbank initialisieren beim Start
init_db()

# ==========================================
# Dependency Injection - DB Session
# ==========================================
def get_db_session():
    """Context Manager für DB-Sessions"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

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
    Upload einer Audio-Datei
    - Speichert Datei im Filesystem
    - Extrahiert Metadaten
    - Speichert Eintrag in DB via Repository
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'Keine Datei gefunden'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400
    
    try:
        # 1. Datei speichern (Service Layer)
        filename, filepath = AudioService.save_uploaded_file(file, UPLOAD_FOLDER)
        
        # 2. Metadaten extrahieren (Service Layer)
        metadata = AudioService.get_audio_metadata(filepath)
        
        # 3. DB-Session holen
        db = get_db_session()
        audio_repo = AudioFileRepository(db)
        
        # TODO: Aktuell ohne User - später mit Session/Auth
        # Für jetzt: Dummy User ID = 1 (muss vorher existieren!)
        user_id = 1  # WICHTIG: User muss in DB existieren
        
        # 4. In Datenbank speichern (Repository Layer)
        audio_file = audio_repo.create(
            user_id=user_id,
            filename=filename,
            file_path=filepath,
            file_size=metadata['file_size'],
            sample_rate=metadata['sample_rate'],
            duration=metadata['duration'],
            has_watermark=False,
            watermark_type=None
        )
        
        return jsonify({
            'message': 'Datei erfolgreich hochgeladen',
            'audio_id': audio_file.id,
            'filename': filename,
            'metadata': metadata
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# SCHNITTSTELLE 2: Watermark Embedding + DB-Update
# ==========================================
@app.route('/watermark/embed', methods=['POST'])
def embed():
    """
    Embed Watermark in Audio
    - Upload + Watermarking
    - Speichert Original UND Watermarked in DB
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'Keine Datei gefunden'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400
    
    try:
        # 1. Original-Datei speichern
        filename, input_path = AudioService.save_uploaded_file(file, UPLOAD_FOLDER)
        original_metadata = AudioService.get_audio_metadata(input_path)
        
        # 2. Watermark einbetten
        audio_tensor, sr = prepare_audio(input_path)
        watermarked_audio = embed_watermark(audio_tensor, sr)
        
        output_filename = f"watermarked_{filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        save_audio(watermarked_audio, sr, output_path)
        
        watermarked_metadata = AudioService.get_audio_metadata(output_path)
        
        # 3. Beide Dateien in DB speichern
        db = get_db_session()
        audio_repo = AudioFileRepository(db)
        user_id = 1  # TODO: Aus Session holen
        
        # Original speichern
        original_file = audio_repo.create(
            user_id=user_id,
            filename=filename,
            file_path=input_path,
            file_size=original_metadata['file_size'],
            sample_rate=original_metadata['sample_rate'],
            duration=original_metadata['duration'],
            has_watermark=False,
            watermark_type=None
        )
        
        # Watermarked speichern
        watermarked_file = audio_repo.create(
            user_id=user_id,
            filename=output_filename,
            file_path=output_path,
            file_size=watermarked_metadata['file_size'],
            sample_rate=watermarked_metadata['sample_rate'],
            duration=watermarked_metadata['duration'],
            has_watermark=True,
            watermark_type='AudioSeal'
        )
        
        return send_file(output_path, as_attachment=True, download_name=output_filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# SCHNITTSTELLE 3: Watermark Detection + DB-Logging
# ==========================================
@app.route('/watermark/detect', methods=['POST'])
def detect():
    """
    Detect Watermark in Audio
    - Upload + Detection
    - Speichert Detection-Ergebnis in DB
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'Keine Datei gefunden'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400
    
    try:
        # 1. Datei speichern
        filename, input_path = AudioService.save_uploaded_file(file, UPLOAD_FOLDER)
        metadata = AudioService.get_audio_metadata(input_path)
        
        # 2. Detection durchführen
        audio_tensor, sr = prepare_audio(input_path)
        confidence, message = detect_watermark(audio_tensor, sr)
        
        # Tensor zu Float konvertieren
        if hasattr(confidence, 'cpu'):
            confidence = float(confidence.cpu().detach().numpy())
        else:
            confidence = float(confidence)
        
        if hasattr(message, 'cpu'):
            message = message.cpu().detach().numpy().tolist()
        
        confidence_percent = confidence * 100
        detected = confidence_percent >= 50
        
        # 3. In DB speichern mit Detection-Info
        db = get_db_session()
        audio_repo = AudioFileRepository(db)
        user_id = 1  # TODO: Aus Session
        
        audio_file = audio_repo.create(
            user_id=user_id,
            filename=filename,
            file_path=input_path,
            file_size=metadata['file_size'],
            sample_rate=metadata['sample_rate'],
            duration=metadata['duration'],
            has_watermark=detected,
            watermark_type='AudioSeal' if detected else None
        )
        
        return jsonify({
            'detected': detected,
            'confidence': confidence_percent,
            'message': message,
            'filename': filename,
            'audio_id': audio_file.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# SCHNITTSTELLE 4: File Download aus DB
# ==========================================
@app.route('/download/<int:audio_id>', methods=['GET'])
def download_audio(audio_id: int):
    """
    Download einer gespeicherten Audio-Datei
    - Holt Datei-Info aus DB via Repository
    - Sendet Datei an Client
    """
    try:
        db = get_db_session()
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
    Gibt alle Audio-Dateien eines Users zurück
    """
    try:
        db = get_db_session()
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