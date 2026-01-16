from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np
import torch


class WatermarkStrategy(ABC):
    """
    Abstrakte Basisklasse für alle Watermarking-Methoden.
    Implementiert das Strategy Pattern für austauschbare Watermarking-Algorithmen.
    """
    
    @abstractmethod
    def embed(self, input_path: str, output_path: str) -> str:
        """
        Bettet Watermark in Audio-Datei ein.
        
        Args:
            input_path: Pfad zur Original-Audio-Datei
            output_path: Pfad für die Watermarked-Audio-Datei
            
        Returns:
            output_path: Pfad zur gespeicherten watermarked Datei
        """
        pass
    
    @abstractmethod
    def detect(self, input_path: str) -> Dict[str, Any]:
        """
        Detektiert Watermark in Audio-Datei.
        
        Args:
            input_path: Pfad zur Audio-Datei
            
        Returns:
            dict mit Keys: 'detected' (bool), 'watermark_type' (str), weitere methoden-spezifische Daten
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name der Watermarking-Methode"""
        pass


class AudioSealStrategy(WatermarkStrategy):
    """
    Implementierung für AudioSeal Watermarking.
    Verwendet PyTorch-basiertes Modell mit Confidence Score.
    """
    
    @property
    def name(self) -> str:
        return "AudioSeal"
    
    def embed(self, input_path: str, output_path: str) -> str:
        from aimodels.AudioSeal.audioseal_handler import prepare_audio, embed_watermark, save_audio
        
        # 1. Audio vorbereiten
        audio_tensor, sr = prepare_audio(input_path)
        
        # 2. Watermark einbetten
        watermarked_audio = embed_watermark(audio_tensor, sr)
        
        # 3. Speichern
        save_audio(watermarked_audio, sr, output_path)
        
        return output_path
    
    def detect(self, input_path: str) -> Dict[str, Any]:
        from aimodels.AudioSeal.audioseal_handler import prepare_audio, detect_watermark
        
        # 1. Audio vorbereiten
        audio_tensor, sr = prepare_audio(input_path)
        
        # 2. Detection durchführen
        confidence, message = detect_watermark(audio_tensor, sr)
        
        # 3. Tensor zu Python-Typen konvertieren
        if hasattr(confidence, 'cpu'):
            confidence = float(confidence.cpu().detach().numpy())
        else:
            confidence = float(confidence)
        
        if hasattr(message, 'cpu'):
            message = message.cpu().detach().numpy().tolist()
        
        # 4. Confidence in Prozent
        confidence_percent = confidence * 100
        detected = bool(confidence_percent >= 50)  # Threshold: 50%
        
        return {
            'detected': detected,
            'confidence': confidence_percent,
            'message': message,
            'watermark_type': self.name
        }


class PerthStrategy(WatermarkStrategy):
    """
    Implementierung für PerTh Watermarking.
    Verwendet librosa-basiertes Implicit Watermarking.
    """
    
    @property
    def name(self) -> str:
        return "PerTh"
    
    def embed(self, input_path: str, output_path: str) -> str:
        from aimodels.PerTh.perth_handler import embed_perth_watermark
        
        # Watermark einbetten und speichern
        embed_perth_watermark(input_path, output_path)
        
        return output_path
    
    def detect(self, input_path: str) -> Dict[str, Any]:
        from aimodels.PerTh.perth_handler import detect_perth_watermark
        
        # Detection durchführen
        watermark, detected = detect_perth_watermark(input_path)
        
        result = {
            'detected': bool(detected),
            'watermark_type': self.name
        }
        
        # Watermark-Daten hinzufügen falls vorhanden
        if watermark is not None:
            if isinstance(watermark, np.ndarray):
                result['watermark'] = watermark.tolist()
            else:
                result['watermark'] = watermark
        
        return result


class WatermarkStrategyFactory:
    """
    Factory zur Erstellung der richtigen Watermarking-Strategy.
    Ermöglicht dynamisches Hinzufügen neuer Methoden.
    """
    
    _strategies = {
        'audioseal': AudioSealStrategy,
        'perth': PerthStrategy
    }
    
    @classmethod
    def get_strategy(cls, method: str) -> WatermarkStrategy:
        """
        Gibt die passende Strategy-Instanz für die gewählte Methode zurück.
        
        Args:
            method: Name der Methode ('audioseal' oder 'perth')
            
        Returns:
            WatermarkStrategy-Instanz
            
        Raises:
            ValueError: Wenn die Methode unbekannt ist
        """
        method_lower = method.lower()
        strategy_class = cls._strategies.get(method_lower)
        
        if not strategy_class:
            available = ', '.join(cls._strategies.keys())
            raise ValueError(f"Unbekannte Watermarking-Methode: '{method}'. Verfügbar: {available}")
        
        return strategy_class()
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """
        Registriert eine neue Watermarking-Strategy.
        Ermöglicht Erweiterung ohne Code-Änderung (Open/Closed Principle).
        
        Args:
            name: Name der Methode (z.B. 'wavmark')
            strategy_class: Klasse die WatermarkStrategy implementiert
        """
        if not issubclass(strategy_class, WatermarkStrategy):
            raise TypeError(f"{strategy_class} muss WatermarkStrategy implementieren")
        
        cls._strategies[name.lower()] = strategy_class
    
    @classmethod
    def available_methods(cls) -> list:
        """Gibt Liste aller verfügbaren Methoden zurück"""
        return list(cls._strategies.keys())