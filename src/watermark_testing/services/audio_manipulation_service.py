import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from typing import Tuple, Dict
import os


class AudioManipulationService:
    """
    Service für Audio-Manipulationen zum Robustness-Testing von Watermarks.
    """
    
    @staticmethod
    def add_noise(audio_path: str, output_path: str, snr_db: float = 20) -> Dict:
        """
        Fügt additives weißes Rauschen hinzu.
        
        Args:
            audio_path: Pfad zur Original-Datei
            output_path: Pfad für Output
            snr_db: Signal-to-Noise Ratio in dB (höher = weniger Rauschen)
        
        Returns:
            Dict mit Metadaten
        """
        # Audio laden
        audio, sr = librosa.load(audio_path, sr=None)
        
        # Signal-Power berechnen
        signal_power = np.mean(audio ** 2)
        
        # Noise-Power aus SNR berechnen
        snr_linear = 10 ** (snr_db / 10)
        noise_power = signal_power / snr_linear
        
        # Rauschen generieren
        noise = np.random.normal(0, np.sqrt(noise_power), audio.shape)
        
        # Rauschen hinzufügen
        noisy_audio = audio + noise
        
        # Clipping vermeiden
        noisy_audio = np.clip(noisy_audio, -1.0, 1.0)
        
        # Speichern
        sf.write(output_path, noisy_audio, sr)
        
        return {
            'sample_rate': sr,
            'duration': len(audio) / sr,
            'parameters': {'snr_db': snr_db}
        }
    
    @staticmethod
    def apply_compression(audio_path: str, output_path: str, bitrate: int = 128) -> Dict:
        """
        Komprimiert Audio als MP3.
        
        Args:
            audio_path: Pfad zur Original-Datei
            output_path: Pfad für Output (sollte .mp3 sein)
            bitrate: Bitrate in kbps
        
        Returns:
            Dict mit Metadaten
        """
        # Nutze pydub für MP3-Encoding
        from pydub import AudioSegment
        
        audio = AudioSegment.from_file(audio_path)
        audio.export(output_path, format="mp3", bitrate=f"{bitrate}k")
        
        # Metadaten
        audio_reloaded, sr = librosa.load(output_path, sr=None)
        
        return {
            'sample_rate': sr,
            'duration': len(audio_reloaded) / sr,
            'parameters': {'bitrate_kbps': bitrate}
        }
    
    @staticmethod
    def apply_gain(audio_path: str, output_path: str, gain_db: float = 0) -> Dict:
        """
        Ändert die Lautstärke.
        
        Args:
            audio_path: Pfad zur Original-Datei
            output_path: Pfad für Output
            gain_db: Gain in dB (negativ = leiser, positiv = lauter)
        
        Returns:
            Dict mit Metadaten
        """
        audio, sr = librosa.load(audio_path, sr=None)
        
        # dB zu linear
        gain_linear = 10 ** (gain_db / 20)
        
        # Gain anwenden
        gained_audio = audio * gain_linear
        
        # Clipping vermeiden
        gained_audio = np.clip(gained_audio, -1.0, 1.0)
        
        sf.write(output_path, gained_audio, sr)
        
        return {
            'sample_rate': sr,
            'duration': len(audio) / sr,
            'parameters': {'gain_db': gain_db}
        }
    
    @staticmethod
    def resample_audio(audio_path: str, output_path: str, target_sr: int = 16000) -> Dict:
        """
        Resampled Audio auf neue Sample-Rate.
        
        Args:
            audio_path: Pfad zur Original-Datei
            output_path: Pfad für Output
            target_sr: Ziel Sample-Rate in Hz
        
        Returns:
            Dict mit Metadaten
        """
        audio, original_sr = librosa.load(audio_path, sr=None)
        
        # Resample
        resampled = librosa.resample(audio, orig_sr=original_sr, target_sr=target_sr)
        
        sf.write(output_path, resampled, target_sr)
        
        return {
            'sample_rate': target_sr,
            'duration': len(resampled) / target_sr,
            'parameters': {
                'original_sr': original_sr,
                'target_sr': target_sr
            }
        }
    
    @staticmethod
    def apply_lowpass(audio_path: str, output_path: str, cutoff: float = 3000) -> Dict:
        """
        Wendet Lowpass-Filter an (entfernt hohe Frequenzen).
        
        Args:
            audio_path: Pfad zur Original-Datei
            output_path: Pfad für Output
            cutoff: Cutoff-Frequenz in Hz
        
        Returns:
            Dict mit Metadaten
        """
        audio, sr = librosa.load(audio_path, sr=None)
        
        # Butterworth Lowpass Filter
        nyquist = sr / 2
        normalized_cutoff = cutoff / nyquist
        b, a = signal.butter(5, normalized_cutoff, btype='low')
        
        filtered = signal.filtfilt(b, a, audio)
        
        sf.write(output_path, filtered, sr)
        
        return {
            'sample_rate': sr,
            'duration': len(audio) / sr,
            'parameters': {'cutoff_hz': cutoff}
        }
    
    @staticmethod
    def apply_highpass(audio_path: str, output_path: str, cutoff: float = 300) -> Dict:
        """
        Wendet Highpass-Filter an (entfernt tiefe Frequenzen).
        
        Args:
            audio_path: Pfad zur Original-Datei
            output_path: Pfad für Output
            cutoff: Cutoff-Frequenz in Hz
        
        Returns:
            Dict mit Metadaten
        """
        audio, sr = librosa.load(audio_path, sr=None)
        
        # Butterworth Highpass Filter
        nyquist = sr / 2
        normalized_cutoff = cutoff / nyquist
        b, a = signal.butter(5, normalized_cutoff, btype='high')
        
        filtered = signal.filtfilt(b, a, audio)
        
        sf.write(output_path, filtered, sr)
        
        return {
            'sample_rate': sr,
            'duration': len(audio) / sr,
            'parameters': {'cutoff_hz': cutoff}
        }
    
    @staticmethod
    def time_stretch(audio_path: str, output_path: str, rate: float = 1.0) -> Dict:
        """
        Ändert Tempo ohne Pitch zu ändern.
        
        Args:
            audio_path: Pfad zur Original-Datei
            output_path: Pfad für Output
            rate: Stretch-Rate (0.5 = halb so schnell, 2.0 = doppelt so schnell)
        
        Returns:
            Dict mit Metadaten
        """
        audio, sr = librosa.load(audio_path, sr=None)
        
        # Time-Stretch
        stretched = librosa.effects.time_stretch(audio, rate=rate)
        
        sf.write(output_path, stretched, sr)
        
        return {
            'sample_rate': sr,
            'duration': len(stretched) / sr,
            'parameters': {'rate': rate}
        }
    
    @staticmethod
    def pitch_shift(audio_path: str, output_path: str, n_steps: float = 0) -> Dict:
        """
        Ändert Pitch ohne Tempo zu ändern.
        
        Args:
            audio_path: Pfad zur Original-Datei
            output_path: Pfad für Output
            n_steps: Anzahl Halbtöne (float für Mikrotöne)
    
        Returns:
            Dict mit Metadaten
        """
        try:
            # Versuch 1: pyrubberband (beste Qualität)
            import pyrubberband as pyrb
            audio, sr = librosa.load(audio_path, sr=None)
            shifted = pyrb.pitch_shift(audio, sr, n_steps)
            
        except ImportError:
            # Fallback: librosa mit besten Parametern
            print("⚠️ pyrubberband nicht installiert - nutze librosa (schlechtere Qualität)")
            audio, sr = librosa.load(audio_path, sr=None)
            shifted = librosa.effects.pitch_shift(
                audio, 
                sr=sr, 
                n_steps=n_steps,
                bins_per_octave=36,
                n_fft=4096,
                hop_length=512,
                res_type='kaiser_best'
            )
    
        sf.write(output_path, shifted, sr)
        
        return {
            'sample_rate': sr,
            'duration': len(audio) / sr,
            'parameters': {'n_steps': n_steps}
        }
    
    @staticmethod
    def apply_manipulation(manipulation_type: str, audio_path: str, 
                          output_path: str, parameters: dict) -> Dict:
        """
        Allgemeine Methode zum Anwenden einer Manipulation.
        
        Args:
            manipulation_type: Typ der Manipulation
            audio_path: Input-Pfad
            output_path: Output-Pfad
            parameters: Dict mit Parametern
        
        Returns:
            Dict mit Metadaten
        """
        manipulation_map = {
            'noise': lambda: AudioManipulationService.add_noise(
                audio_path, output_path, float(parameters.get('snr', 20))
            ),
            'compression': lambda: AudioManipulationService.apply_compression(
                audio_path, output_path, int(parameters.get('bitrate', 128))
            ),
            'gain': lambda: AudioManipulationService.apply_gain(
                audio_path, output_path, float(parameters.get('gain_db', 0))
            ),
            'resample': lambda: AudioManipulationService.resample_audio(
                audio_path, output_path, int(parameters.get('sample_rate', 16000))
            ),
            'lowpass': lambda: AudioManipulationService.apply_lowpass(
                audio_path, output_path, float(parameters.get('cutoff', 3000))
            ),
            'highpass': lambda: AudioManipulationService.apply_highpass(
                audio_path, output_path, float(parameters.get('cutoff', 300))
            ),
            'timestretch': lambda: AudioManipulationService.time_stretch(
                audio_path, output_path, float(parameters.get('rate', 1.0))
            ),
            'pitchshift': lambda: AudioManipulationService.pitch_shift(
                audio_path, output_path, float(parameters.get('steps', 0))  # float statt int!
            ),
        }
        
        if manipulation_type not in manipulation_map:
            raise ValueError(f"Unknown manipulation type: {manipulation_type}")
        
        return manipulation_map[manipulation_type]()