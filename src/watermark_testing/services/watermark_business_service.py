import os
from typing import Tuple, Dict, Any
from database.repositories import AudioFileRepository
from services.audio_service import AudioService
from services.watermark_strategy import WatermarkStrategyFactory


class WatermarkBusinessService:
    """
    Business Logic Layer für Watermarking-Workflows.
    Orchestriert den kompletten Ablauf von Upload bis DB-Speicherung.
    
    Verantwortlichkeiten:
    - Workflow-Orchestrierung
    - Koordination zwischen Services und Repositories
    - Transaktionale Konsistenz
    """
    
    def __init__(self, audio_repo: AudioFileRepository):
        """
        Args:
            audio_repo: Repository für AudioFile-Datenbankzugriffe
        """
        self.audio_repo = audio_repo
    
    def embed_watermark_workflow(
        self, 
        file, 
        method: str, 
        upload_folder: str, 
        user_id: int
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Kompletter Workflow für Watermark-Embedding:
        1. Original-Datei speichern
        2. Watermark einbetten
        3. Beide Dateien in Datenbank registrieren
        
        Args:
            file: Hochgeladene Datei (Werkzeug FileStorage)
            method: Watermarking-Methode ('audioseal' oder 'perth')
            upload_folder: Ordner für gespeicherte Dateien
            user_id: ID des Users
            
        Returns:
            Tuple: (output_path, metadata_dict)
            - output_path: Pfad zur watermarked Datei
            - metadata_dict: Metadaten inkl. DB-IDs
            
        Raises:
            ValueError: Bei ungültiger Methode oder Datei-Problemen
        """
        # 1. Strategy holen (wirft ValueError bei ungültiger Methode)
        strategy = WatermarkStrategyFactory.get_strategy(method)
        
        # 2. Original-Datei speichern
        filename, input_path = AudioService.save_uploaded_file(file, upload_folder)
        original_metadata = AudioService.get_audio_metadata(input_path)
        
        # 3. Output-Pfad vorbereiten
        output_filename = f"watermarked_{method}_{filename}"
        output_path = os.path.join(upload_folder, output_filename)
        
        # 4. Watermark einbetten
        strategy.embed(input_path, output_path)
        
        # 5. Metadaten der watermarked Datei extrahieren
        watermarked_metadata = AudioService.get_audio_metadata(output_path)
        
        # 6. Original in DB speichern
        original_file = self.audio_repo.create(
            user_id=user_id,
            filename=filename,
            file_path=input_path,
            file_size=original_metadata['file_size'],
            sample_rate=original_metadata['sample_rate'],
            duration=original_metadata['duration'],
            has_watermark=False,
            watermark_type=None
        )
        
        # 7. Watermarked in DB speichern
        watermarked_file = self.audio_repo.create(
            user_id=user_id,
            filename=output_filename,
            file_path=output_path,
            file_size=watermarked_metadata['file_size'],
            sample_rate=watermarked_metadata['sample_rate'],
            duration=watermarked_metadata['duration'],
            has_watermark=True,
            watermark_type=strategy.name
        )
        
        return output_path, {
            'original_id': original_file.id,
            'watermarked_id': watermarked_file.id,
            'output_filename': output_filename,
            'method': strategy.name
        }
    
    def detect_watermark_workflow(
        self, 
        file, 
        method: str, 
        upload_folder: str, 
        user_id: int
    ) -> Dict[str, Any]:
        """
        Kompletter Workflow für Watermark-Detection:
        1. Datei speichern
        2. Watermark detektieren
        3. Datei mit Detection-Ergebnis in DB registrieren
        
        Args:
            file: Hochgeladene Datei (Werkzeug FileStorage)
            method: Watermarking-Methode ('audioseal' oder 'perth')
            upload_folder: Ordner für gespeicherte Dateien
            user_id: ID des Users
            
        Returns:
            dict: Detection-Ergebnis inkl. DB-ID und Metadaten
            
        Raises:
            ValueError: Bei ungültiger Methode oder Datei-Problemen
        """
        # 1. Strategy holen
        strategy = WatermarkStrategyFactory.get_strategy(method)
        
        # 2. Datei speichern
        filename, input_path = AudioService.save_uploaded_file(file, upload_folder)
        metadata = AudioService.get_audio_metadata(input_path)
        
        # 3. Detection durchführen
        detection_result = strategy.detect(input_path)
        
        # 4. In DB speichern mit Detection-Info
        audio_file = self.audio_repo.create(
            user_id=user_id,
            filename=filename,
            file_path=input_path,
            file_size=metadata['file_size'],
            sample_rate=metadata['sample_rate'],
            duration=metadata['duration'],
            has_watermark=detection_result['detected'],
            watermark_type=detection_result['watermark_type'] if detection_result['detected'] else None
        )
        
        # 5. Ergebnis zusammenstellen
        detection_result['audio_id'] = audio_file.id
        detection_result['filename'] = filename
        detection_result['method'] = strategy.name
        
        return detection_result
    
    def upload_audio_workflow(
        self,
        file,
        upload_folder: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Einfacher Upload-Workflow ohne Watermarking:
        1. Datei speichern
        2. Metadaten extrahieren
        3. In DB registrieren
        
        Args:
            file: Hochgeladene Datei
            upload_folder: Ordner für gespeicherte Dateien
            user_id: ID des Users
            
        Returns:
            dict: Metadaten und DB-ID
        """
        # 1. Datei speichern
        filename, filepath = AudioService.save_uploaded_file(file, upload_folder)
        
        # 2. Metadaten extrahieren
        metadata = AudioService.get_audio_metadata(filepath)
        
        # 3. In DB speichern
        audio_file = self.audio_repo.create(
            user_id=user_id,
            filename=filename,
            file_path=filepath,
            file_size=metadata['file_size'],
            sample_rate=metadata['sample_rate'],
            duration=metadata['duration'],
            has_watermark=False,
            watermark_type=None
        )
        
        return {
            'audio_id': audio_file.id,
            'filename': filename,
            'metadata': metadata
        }