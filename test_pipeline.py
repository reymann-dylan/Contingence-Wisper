# test_pipeline.py
import time
from audio_engine import AudioEngine
from whisper_engine import WhisperEngine

# Instance Whisper avec déchargement après 15 secondes d'inactivité
whisper = WhisperEngine(default_model="large-v3-turbo", vram_unload_delay=15.0)

engine = None
audio_ready = False


def on_start():
    print("\n[Écoute] Parole détectée ! Enregistrement en cours...")


def on_silence():
    global audio_ready
    print("\n[Silence] Coupure automatique déclenchée !")
    audio_ready = True


def on_meter(level):
    bars = int(level * 25)
    print(f"\rMicro: [{'=' * bars}{' ' * (25 - bars)}]", end="", flush=True)


engine = AudioEngine(
    silence_timeout=5.0,
    on_speech_start=on_start,
    on_silence_stop=on_silence,
    on_audio_level=on_meter
)

print("=" * 60)
print("TEST DU PIPELINE AUDIO + WHISPER LAZY-LOADING")
print("1. Parle normalement dans le micro.")
print("2. Fais une pause de 5 secondes pour stopper.")
print("3. Observe le chargement VRAM, la transcription et la libération.")
print("=" * 60)

engine.start()

# Boucle d'attente de la fin de parole
while not audio_ready:
    time.sleep(0.05)

audio_data = engine.stop()
print(f"\nAudio capturé : {len(audio_data) / 16000:.1f} secondes.")

# Lancement de la transcription
texte = whisper.transcribe(audio_data)
print("\n" + "#" * 60)
print(f"RÉSULTAT : {texte}")
print("#" * 60)

print("\nAttente de 16 secondes sans activité pour constater la libération de la VRAM...")
time.sleep(16)
print("Test terminé.")