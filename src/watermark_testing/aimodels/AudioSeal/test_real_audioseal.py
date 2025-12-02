import torch
import librosa
from audioseal import AudioSeal



#Testklasse für AudioSeal
# nutzt torch um aus orig audio(wav) Torch tensor zu wandeln (mehrdimensionale array-ähnliche struktur)benötigt für AudioSeal
# nutzt librosa um audio datei umzuwanddeln und sample rate anzupasen (AudioSeal erwartet 16kHz)
# Watermark von audioseal hat generator zum einbetten und detector zum finden des watermarks


# Audio-Datei laden
audio_path = r"F:\Uni\8tes Semester\Bachelorarbeit\Bachelor_Arbeit\einleitung.wav"
wav, sr = librosa.load(audio_path, sr=16000)  # Lade mit 16kHz 

print(f"Original Sample Rate: {sr}")
print(f"Audio Shape: {wav.shape}")

# Konvertiere zu Torch Tensor (AudioSeal braucht das)
wav_tensor = torch.from_numpy(wav).unsqueeze(0).unsqueeze(0)  # [1, 1, samples]

print(f"Tensor Shape: {wav_tensor.shape}")


# Schritt 2: Generator laden
print("\n--- Loading Generator ---")
try:
    generator = AudioSeal.load_generator("audioseal_wm_16bits")
    print("✓ Generator loaded successfully")
except Exception as e:
    print(f"✗ Error loading generator: {e}")
    exit()

# Schritt 3: Watermark erzeugen
print("\n--- Generating Watermark ---")
watermark = generator.get_watermark(wav_tensor, sr)
print(f"Watermark Shape: {watermark.shape}")

# Schritt 4: Watermark zum Audio hinzufügen
watermarked_audio = wav_tensor + watermark
print("✓ Watermark added to audio")


#Original Audio:   [0.5, -0.3, 0.2, -0.1,   ...] -> 
#Watermark:      + [0.001, 0.0001, -0.0005, ...]
#                 ─────────────────────────────
#Watermarked:      [0.501, -0.2999, 0.1995, ...]

# Schritt 5: Detector laden
print("\n--- Loading Detector ---")
try:
    detector = AudioSeal.load_detector("audioseal_detector_16bits")
    print("✓ Detector loaded successfully")
except Exception as e:
    print(f"✗ Error loading detector: {e}")
    exit()

# Schritt 6: Watermark detektieren    
# 1.0 = 100% sicher, dass Watermark da ist 0.0 = 0% sicher
print("\n--- Detecting Watermark ---")
result, message = detector.detect_watermark(watermarked_audio, sr)
print(f"Detection Result (Probability): {result}")
print(f"Message (16 bits): {message}")

# Schritt 7: Low-level Detection
# Durchschnittliche Sicherheit über alle Frames
#Audio:     [0-1s]  [1-2s]  [2-3s]  [3-4s]  [4-5s]
#           ├─────┤├─────┤├─────┤├─────┤├─────┤
#Frames:    Frame1  Frame2  Frame3  Frame4  Frame5

#Detector für Frame1: "90% sicher, Watermark hier"
#Detector für Frame2: "95% sicher, Watermark hier"
#Detector für Frame3: "88% sicher, Watermark hier"
#...
print("\n--- Low-level Detection ---")
result_lowlevel, message_lowlevel = detector(watermarked_audio, sr)
print(f"Low-level Result Shape: {result_lowlevel.shape}")
print(f"Frame probabilities (should be > 0.5): {result_lowlevel[:, 1, :].mean()}")