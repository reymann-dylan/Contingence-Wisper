# main_test.py
import time
import sys
import threading
from audio_engine import AudioEngine
from whisper_engine import WhisperEngine
from system_handler import SystemHandler

print("\n[Initialisation] Chargement du modèle Whisper sur la RTX 5070...")
whisper = WhisperEngine(default_model="large-v3-turbo", vram_unload_delay=60.0)
# Préchargement immédiat
whisper.load_model()
print("[Initialisation] Modèle opérationnel en VRAM.\n")

system = SystemHandler(hotkey="<f8>")

# Machine à états : "IDLE", "RECORDING", "PROCESSING"
current_state = "IDLE"
state_lock = threading.Lock()
engine = None


def do_transcription(audio_data):
    global current_state
    try:
        if len(audio_data) < 8000:
            print("[Whisper] Audio trop court (< 0.5s), ignoré.")
            return

        print("[Traitement] Inférence en cours...")
        t0 = time.time()
        texte = whisper.transcribe(audio_data)
        elapsed = time.time() - t0

        if texte:
            print(f"[Succès en {elapsed:.2f}s] : {texte}")
            # Laisse 100ms au système d'exploitation pour stabiliser le focus
            time.sleep(0.1)
            system.paste_text(texte)
        else:
            print("[Whisper] Rien d'intelligible détecté.")
    except Exception as e:
        print(f"[Erreur transcription] : {e}")
    finally:
        with state_lock:
            current_state = "IDLE"
        print("[Prêt] Appuie sur F8 pour dicter...\n")


def trigger_stop_and_process():
    global current_state, engine
    with state_lock:
        if current_state != "RECORDING":
            return
        current_state = "PROCESSING"

    print("\n[Arrêt] Traitement audio lancé...")
    audio_data = engine.stop()
    threading.Thread(target=do_transcription, args=(audio_data,), daemon=True).start()


def on_silence_timeout():
    """Déclenché par le VAD après 5s de silence continu."""
    print("\n[Auto-Stop] 5 secondes de silence détectées.")
    trigger_stop_and_process()


def on_f8_pressed():
    global current_state, engine
    with state_lock:
        if current_state == "PROCESSING":
            print("[Info] Traitement en cours, veuillez patienter...")
            return

        if current_state == "IDLE":
            current_state = "RECORDING"
            print("\n" + "=" * 40)
            print("[● ENREGISTREMENT]")
            print("Parle dans ton micro... (F8 ou silence pour stopper)")
            print("=" * 40)
            engine = AudioEngine(
                silence_timeout=5.0,
                on_silence_stop=on_silence_timeout
            )
            engine.start()
            return

    # Si on était en RECORDING, on stoppe
    trigger_stop_and_process()


system.on_hotkey_pressed = on_f8_pressed
system.start_hotkey_listener()

print("=" * 60)
print("TEST OPÉRATIONNEL")
print("1. Ouvre le Bloc-notes et clique dedans.")
print("2. Appuie une seule fois sur F8.")
print("3. Parle, puis réappuie une seule fois sur F8.")
print("=" * 60 + "\n")

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nArrêt.")
    system.stop_hotkey_listener()
    sys.exit(0)