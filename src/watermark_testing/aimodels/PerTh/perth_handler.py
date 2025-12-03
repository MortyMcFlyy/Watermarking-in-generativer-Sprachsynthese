import perth
import librosa
import soundfile as sf
from perth.utils import calculate_audio_metrics, plot_audio_comparison
from perth.perth_net.perth_net_implicit.perth_watermarker import PerthImplicitWatermarker


def apply_watermark(input_path, output_path):
    """Load audio file, apply watermark, and save"""
    # Load audio file
    wav, sr = librosa.load(input_path, sr=None)

    # Initialize watermarker
    watermarker = PerthImplicitWatermarker()

    # Apply watermark
    watermarked_audio = watermarker.apply_watermark(wav, watermark=None, sample_rate=sr)

    # Save watermarked audio
    sf.write(output_path, watermarked_audio, sr)
    print(f"✓ Watermarked audio saved to: {output_path}")


def extract_watermark(input_path):
    """Load watermarked audio and extract watermark"""
    # Load the watermarked audio
    watermarked_audio, sr = librosa.load(input_path, sr=None)

    # Initialize watermarker (same as used for embedding)
    watermarker = PerthImplicitWatermarker()

    # Extract watermark
    watermark = watermarker.get_watermark(watermarked_audio, sample_rate=sr)
    print(f"Extracted watermark: {watermark}")
    return watermark


def evaluate_watermark(original_path, watermarked_path):
    """Evaluate quality metrics between original and watermarked audio"""
    # Load original and watermarked audio
    original, sr = librosa.load(original_path, sr=None)
    watermarked, _ = librosa.load(watermarked_path, sr=None)

    # Calculate quality metrics
    metrics = calculate_audio_metrics(original, watermarked)
    print(f"\n📊 Quality Metrics:")
    print(f"   SNR: {metrics['snr']:.2f} dB")
    print(f"   PSNR: {metrics['psnr']:.2f} dB")

    # Visualize differences
    plot_audio_comparison(original, watermarked, sr, output_path="comparison.png")
    print(f"✓ Comparison plot saved to: comparison.png")


def main():
    """Hauptmenü für PerTh Watermark-Testing"""
    
    print("\n" + "="*50)
    print("   PerTh Watermark Testing Tool")
    print("="*50)
    print("\nWas möchtest du machen?")
    print("1 - Watermark einbetten")
    print("2 - Watermark extrahieren")
    print("3 - Audio-Qualität evaluieren")
    print("4 - Alles (einbetten + extrahieren + evaluieren)")
    print("0 - Beenden")
    print("="*50)
    
    choice = input("\nWähle eine Option (0-4): ").strip()
    
    if choice == "1":
        print("\n--- Option 1: Watermark einbetten ---")
        input_path = input("Gib den Pfad zur Audio-Datei ein: ").strip()
        output_path = input("Wo soll die Datei gespeichert werden? (z.B. watermarked.wav): ").strip()
        apply_watermark(input_path, output_path)
        print("✅ Fertig!")
        
    elif choice == "2":
        print("\n--- Option 2: Watermark extrahieren ---")
        input_path = input("Gib den Pfad zur watermarkten Audio-Datei ein: ").strip()
        extract_watermark(input_path)
        print("✅ Fertig!")
        
    elif choice == "3":
        print("\n--- Option 3: Audio-Qualität evaluieren ---")
        original_path = input("Gib den Pfad zur Original-Datei ein: ").strip()
        watermarked_path = input("Gib den Pfad zur watermarkten Datei ein: ").strip()
        evaluate_watermark(original_path, watermarked_path)
        print("✅ Fertig!")
        
    elif choice == "4":
        print("\n--- Option 4: Alles (einbetten + extrahieren + evaluieren) ---")
        input_path = input("Gib den Pfad zur Audio-Datei ein: ").strip()
        output_path = input("Wo soll die watermarkte Datei gespeichert werden? (z.B. watermarked.wav): ").strip()
        
        # Watermark einbetten
        print("\n🔧 Watermark wird eingebettet...")
        apply_watermark(input_path, output_path)
        
        # Watermark extrahieren
        print("\n🔍 Watermark wird extrahiert...")
        extract_watermark(output_path)
        
        # Evaluieren
        print("\n📊 Audio-Qualität wird evaluiert...")
        evaluate_watermark(input_path, output_path)
        
        print("✅ Fertig!")
        
    elif choice == "0":
        print("👋 Auf Wiedersehen!")
        return
        
    else:
        print("❌ Ungültige Eingabe! Bitte 0-4 eingeben.")
        main()


if __name__ == "__main__":
    main()