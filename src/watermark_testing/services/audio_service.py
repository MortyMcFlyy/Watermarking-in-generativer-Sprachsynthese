import os
import librosa
from typing import Tuple
from pathlib import Path


class AudioService:
    """
    Service für Audio-Datei-Verarbeitung.
    Verantwortlich für Metadaten-Extraktion und File-Management.
    """
    
    # Erlaubte Audio-Formate (Input-Validierung)
    ALLOWED_EXTENSIONS = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    # Maximale Dateigröße (in Bytes) - 100MB
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    @staticmethod
    def validate_audio_file(file) -> None:
        """
        Validiert hochgeladene Audio-Datei.
        
        Args:
            file: Werkzeug FileStorage Objekt
            
        Raises:
            ValueError: Bei ungültigem Format oder zu großer Datei
        """
        # Dateiname prüfen
        if not file.filename:
            raise ValueError("Dateiname ist leer")
        
        # Extension prüfen
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in AudioService.ALLOWED_EXTENSIONS:
            allowed = ', '.join(AudioService.ALLOWED_EXTENSIONS)
            raise ValueError(f"Ungültiges Dateiformat '{file_ext}'. Erlaubt: {allowed}")
        
        # Größe prüfen (wenn verfügbar)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Zurück zum Anfang
        
        if file_size > AudioService.MAX_FILE_SIZE:
            max_mb = AudioService.MAX_FILE_SIZE / (1024 * 1024)
            raise ValueError(f"Datei zu groß ({file_size / (1024 * 1024):.1f}MB). Maximum: {max_mb}MB")
    
    @staticmethod
    def get_audio_metadata(file_path: str) -> dict:
        """
        Extrahiert Metadaten aus Audio-Datei.
        
        Args:
            file_path: Pfad zur Audio-Datei
            
        Returns:
            dict mit Keys: sample_rate, duration, file_size
            
        Raises:
            ValueError: Bei Fehler beim Lesen der Datei
        """
        try:
            # Audio laden
            audio_data, sample_rate = librosa.load(file_path, sr=None)
            duration = librosa.get_duration(y=audio_data, sr=sample_rate)
            file_size = os.path.getsize(file_path)
            
            return {
                'sample_rate': int(sample_rate),
                'duration': float(duration),
                'file_size': int(file_size)
            }
        except Exception as e:
            raise ValueError(f"Fehler beim Lesen der Audio-Metadaten: {str(e)}")
    
    @staticmethod
    def save_uploaded_file(file, upload_folder: str) -> Tuple[str, str]:
        """
        Speichert hochgeladene Datei und gibt Pfad zurück.
        
        Args:
            file: Werkzeug FileStorage Objekt
            upload_folder: Zielordner
            
        Returns:
            Tuple (filename, filepath)
            
        Raises:
            ValueError: Bei Validierungsfehlern
        """
        # Validierung
        AudioService.validate_audio_file(file)
        
        # Sichere Dateinamen (Path-Traversal verhindern)
        filename = os.path.basename(file.filename)
        
        # Pfad erstellen
        filepath = os.path.join(upload_folder, filename)
        
        # Speichern
        file.save(filepath)
        
        return filename, filepath