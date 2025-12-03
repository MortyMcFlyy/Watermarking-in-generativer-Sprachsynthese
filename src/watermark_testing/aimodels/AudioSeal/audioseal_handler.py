import torch
import librosa
from audioseal import AudioSeal


def prepare_audio(audio_path):
    #laut github 16kHz, aber hier 44.1kHz um bessere Kompatibilität zu gewährleisten scheint immernoch zu funktionieren
    wav, sr = librosa.load(audio_path, sr=44100)
    wav_tensor = torch.from_numpy(wav).unsqueeze(0).unsqueeze(0)
    return wav_tensor, sr


def detect_watermark(audio_tensor, sample_rate):
    detector = AudioSeal.load_detector("audioseal_detector_16bits")
    result, message = detector.detect_watermark(audio_tensor, sample_rate)
    return result, message


def embed_watermark(audio_tensor, sample_rate):
    generator = AudioSeal.load_generator("audioseal_wm_16bits")
    watermark = generator.get_watermark(audio_tensor, sample_rate)
    watermarked_audio = audio_tensor + watermark
    return watermarked_audio


def save_audio(audio_tensor, sample_rate, output_path):
    import soundfile as sf
    audio_np = audio_tensor.squeeze().detach().cpu().numpy()
    
    try:
        sf.write(output_path, audio_np, sample_rate)
        print(f"✓ Audio gespeichert: {output_path}")
    except Exception as e:
        print(f"✗ Fehler beim Speichern: {e}")


def main():
    """Hauptmenü für AudioSeal Watermark-Testing"""
    
    print("\n" + "="*50)
    print("   AudioSeal Watermark Testing Tool")
    print("="*50)
    print("\nWas möchtest du machen?")
    print("1 - Watermark einbetten")
    print("2 - Watermark detektieren")
    print("3 - Beides (einbetten + detektieren)")
    print("0 - Beenden")
    print("="*50)
    
    choice = input("\nWähle eine Option (0-3): ").strip()
    
    if choice == "1":
        print("\n--- Option 1: Watermark einbetten ---")
        audio_path = input("Gib den Pfad zur Audio-Datei ein: ").strip()
        audio_tensor, sr = prepare_audio(audio_path)
        watermarked_audio = embed_watermark(audio_tensor, sr)
        output_path = input("Wo soll die Datei gespeichert werden? (z.B. watermarked.wav): ").strip()
        save_audio(watermarked_audio, sr, output_path)
        print("✅ Fertig!")
        
    elif choice == "2":
        print("\n--- Option 2: Watermark detektieren ---")
        audio_path = input("Gib den Pfad zur Audio-Datei ein: ").strip()
        audio_tensor, sr = prepare_audio(audio_path)
        result, message = detect_watermark(audio_tensor, sr)
        print(f"\n📊 Detektions-Ergebnisse:")
        print(f"   Konfidenz: {result:.2%}")
        print(f"   Nachricht (16 Bits): {message}")
        print("✅ Fertig!")
        
    elif choice == "3":
        print("\n--- Option 3: Einbetten + Detektieren ---")
        audio_path = input("Gib den Pfad zur Audio-Datei ein: ").strip()
        audio_tensor, sr = prepare_audio(audio_path)
        watermarked_audio = embed_watermark(audio_tensor, sr)
        result, message = detect_watermark(watermarked_audio, sr)
        print(f"\n📊 Detektions-Ergebnisse:")
        print(f"   Konfidenz: {result:.2%}")
        print(f"   Nachricht (16 Bits): {message}")
        print("✅ Fertig!")
        
    elif choice == "0":
        print("👋 Auf Wiedersehen!")
        return
        
    else:
        print("❌ Ungültige Eingabe! Bitte 0-3 eingeben.")
        main()


if __name__ == "__main__":
    main()