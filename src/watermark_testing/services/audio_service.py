import os
import librosa
from typing import Tuple, Optional
from pathlib import Path

class AudioService:
    """Business Logic für Audio-Verarbeitung"""
    
    @staticmethod
    def get_audio_metadata(file_path: str) -> dict:
        """Extrahiert Metadaten aus Audio-Datei"""
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
        """Speichert hochgeladene Datei und gibt Pfad zurück"""
        filename = file.filename
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename, filepath