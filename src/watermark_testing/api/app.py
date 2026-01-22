from contextlib import contextmanager
from flask import Flask, jsonify, request, send_file, render_template
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Füge den Parent-Ordner zum Path hinzu
sys.path.append(str(Path(__file__).parent.parent))

# Imports
from database.database import init_db, get_db
from database.repositories import UserRepository, AudioFileRepository, ManipulatedAudioFileRepository
from services.audio_service import AudioService
from services.watermark_business_service import WatermarkBusinessService
from services.watermark_strategy import WatermarkStrategyFactory
from services.audio_manipulation_service import AudioManipulationService
import json
import uuid


# Flask App 
app = Flask(__name__)
CORS(app)

# Upload-Ordner erstellen
UPLOAD_FOLDER = '/app/uploads'
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


# ==========================================
# SCHNITTSTELLE 6: Datei löschen
# ==========================================
@app.route('/files/<int:audio_id>', methods=['DELETE'])
def delete_audio_file(audio_id: int):
    """
    Löscht eine Audio-Datei.
    - Löscht Datei aus Filesystem
    - Löscht Eintrag aus DB via Repository
    """
    try:
        with get_db() as db:
            audio_repo = AudioFileRepository(db)
            
            # Datei aus DB holen
            audio_file = audio_repo.get_by_id(audio_id)
            
            if not audio_file:
                return jsonify({'error': 'Datei nicht gefunden'}), 404
            
            # TODO: User-Berechtigung prüfen
            # if audio_file.user_id != current_user_id:
            #     return jsonify({'error': 'Keine Berechtigung'}), 403
            
            # Datei aus Filesystem löschen (falls vorhanden)
            if os.path.exists(audio_file.file_path):
                try:
                    os.remove(audio_file.file_path)
                except Exception as e:
                    print(f"Warnung: Konnte Datei nicht löschen: {e}")
            
            # Eintrag aus DB löschen via Repository
            audio_repo.delete(audio_id)
            
            return jsonify({
                'message': 'Datei erfolgreich gelöscht',
                'deleted_id': audio_id
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# SCHNITTSTELLE 7: Audio Manipulation
# ==========================================
@app.route('/manipulation/apply', methods=['POST'])
def apply_manipulation():
    """
    Wendet eine Manipulation auf eine Audio-Datei an.
    - Upload + Manipulation
    - Speichert manipulierte Datei in DB
    """
    # Validierung
    if 'audio' not in request.files:
        return jsonify({'error': 'Keine Datei gefunden'}), 400
    
    file = request.files['audio']
    manipulation_type = request.form.get('manipulation_type')
    parameters_json = request.form.get('parameters', '{}')
    
    if file.filename == '':
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400
    
    if not manipulation_type:
        return jsonify({'error': 'Manipulation-Typ fehlt'}), 400
    
    try:
        # Parameter parsen
        parameters = json.loads(parameters_json)
        
        # Temporäre Datei speichern
        AudioService.validate_audio_file(file)
        temp_filename = f"temp_{uuid.uuid4().hex}_{file.filename}"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(temp_path)
        
        # Output-Dateiname
        output_filename = f"manipulated_{manipulation_type}_{file.filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        # Manipulation anwenden
        metadata = AudioManipulationService.apply_manipulation(
            manipulation_type=manipulation_type,
            audio_path=temp_path,
            output_path=output_path,
            parameters=parameters
        )
        
        # Metadaten ergänzen
        file_size = os.path.getsize(output_path)
        
        # In Datenbank speichern
        with get_db() as db:
            manipulated_repo = ManipulatedAudioFileRepository(db)
            user_id = 1  # TODO: Aus Session
            
            manipulated_audio = manipulated_repo.create(
                user_id=user_id,
                filename=output_filename,
                file_path=output_path,
                file_size=file_size,
                sample_rate=metadata['sample_rate'],
                duration=metadata['duration'],
                manipulation_type=manipulation_type,
                manipulation_parameters=parameters
            )
        
        # Temp-Datei löschen
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Manipulierte Datei zum Download senden
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Interner Serverfehler: {str(e)}'}), 500


# ==========================================
# SCHNITTSTELLE 8: Liste aller manipulierten Dateien
# ==========================================
@app.route('/manipulation/list', methods=['GET'])
def list_manipulated_files():
    """
    Gibt alle manipulierten Audio-Dateien eines Users zurück.
    """
    try:
        with get_db() as db:
            manipulated_repo = ManipulatedAudioFileRepository(db)
            user_id = 1  # TODO: Aus Session
            
            files = manipulated_repo.get_by_user(user_id)
            
            return jsonify({
                'count': len(files),
                'files': [
                    {
                        'id': f.id,
                        'filename': f.filename,
                        'file_size': f.file_size,
                        'duration': f.duration,
                        'manipulation_type': f.manipulation_type,
                        'parameters': json.loads(f.manipulation_parameters),
                        'created_at': f.created_at.isoformat()
                    }
                    for f in files
                ]
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# App starten
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    #Localhost sonst 0.0.0.0 für Docker