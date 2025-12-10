import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# Run TTS
# ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# Text to speech list of amplitude values as output
wav = tts.tts(text="Hallo zusammen Wie geht es uns denn heute? Bock auf einen Kaffee?", speaker_wav="F:\\Uni\\8tes Semester\\Bachelorarbeit\\Bachelor_Arbeit\\einleitung.wav", language="de")
# Text to speech to a file
tts.tts_to_file(text="Hallo zusammen Wie geht es uns denn heute? Bock auf einen Kaffee?", speaker_wav="F:\\Uni\\8tes Semester\\Bachelorarbeit\\Bachelor_Arbeit\\einleitung.wav", language="de", file_path="output.wav")