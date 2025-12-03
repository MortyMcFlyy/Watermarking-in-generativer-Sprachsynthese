import perth
import librosa
import soundfile as sf
from perth.utils import calculate_audio_metrics, plot_audio_comparison


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
    watermark = watermarker.get_watermark(watermarked_audio, sample_rate=sr)
    print(f"Extracted watermark: {watermark}")



def evaluate_watermark():
    # Load original and watermarked audio
    original, sr = librosa.load("input.wav", sr=None)
    watermarked, _ = librosa.load("output.wav", sr=None)

    # Calculate quality metrics
    metrics = calculate_audio_metrics(original, watermarked)
    print(f"SNR: {metrics['snr']:.2f} dB")
    print(f"PSNR: {metrics['psnr']:.2f} dB")

    # Visualize differences
    plot_audio_comparison(original, watermarked, sr, output_path="comparison.png")