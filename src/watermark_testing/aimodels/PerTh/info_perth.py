import perth
import librosa
import soundfile as sf
from perth.utils import calculate_audio_metrics, plot_audio_comparison



#Testklasse für das watermarking mit PerTh
# Original Audio → [Encoder] → Watermarked Audio → [Decoder] → Watermark Detection
# Vereinfacht:
# 1. Audio → STFT (Short-Time Fourier Transform) → Spektrogramm
# 2. Spektrogramm + Watermark → Neural Network → Modifiziertes Spektrogramm
# 3. Modifiziertes Spektrogramm → Inverse STFT → Watermarked Audio

#PerTh arbeitet im Frequenzbereich, nicht direkt mit dem Zeitsignal:
#Detection gibt Confidence Score zurück (0.0 (nix drin)  - 1.0( eindeutiges Watermark drin) )


def apply_watermark():
    #Load audio file
    wav, sr = librosa.load("input.wav", sr=None)

    # Initialize watermarker
    watermarker = perth.PerthImplicitWatermarker()

    # Apply watermark
    watermarked_audio = watermarker.apply_watermark(wav, watermark=None, sample_rate=sr)

    # Save watermarked audio
    sf.write("output.wav", watermarked_audio, sr)



def extract_watermark():
    # Load the watermarked audio
    watermarked_audio, sr = librosa.load("output.wav", sr=None)

    # Initialize watermarker (same as used for embedding)
    watermarker = perth.PerthImplicitWatermarker()

    # Extract watermark
    # wird zwar im github so genannt, aber es ist eigentlich die Erkennung des watermarks ohne dass es entfernt wird
    watermark = watermarker.get_watermark(watermarked_audio, sample_rate=sr)
    print(f"Extracted watermark: {watermark}")



def evaluate_watermark():
    # Load original and watermarked audio
    original, sr = librosa.load("input.wav", sr=None)
    watermarked, _ = librosa.load("output.wav", sr=None)

    # Calculate quality metrics
    metrics = calculate_audio_metrics(original, watermarked)
    #gibt einen error aufgrund unterscheidlicher Längen der Audiodateien(kann ja nicht? Issue im github gemeldet)
    print(f"SNR: {metrics['snr']:.2f} dB")
    print(f"PSNR: {metrics['psnr']:.2f} dB")

    # Visualize differences
    plot_audio_comparison(original, watermarked, sr, output_path="comparison.png")