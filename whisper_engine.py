# whisper_engine.py
import os
import sys
import gc
import time
import threading
from typing import Optional
import numpy as np

# Résolution des DLLs CUDA 12 dans l'environnement virtuel Windows
if sys.platform == "win32":
    venv_base = sys.prefix
    nvidia_base = os.path.join(venv_base, "Lib", "site-packages", "nvidia")
    
    if os.path.isdir(nvidia_base):
        for root, dirs, files in os.walk(nvidia_base):
            if any(f.lower().endswith(".dll") for f in files):
                try:
                    os.add_dll_directory(root)
                except Exception:
                    pass
                os.environ["PATH"] = root + os.pathsep + os.environ["PATH"]

from faster_whisper import WhisperModel

MODELS_CONFIG = {
    "small": {
        "id": "small",
        "vram": "~1.0 Go",
        "description": "Ultra rapide, empreinte minimale. Idéal sur batterie.",
        "compute_type": "float16"
    },
    "medium": {
        "id": "medium",
        "vram": "~2.5 Go",
        "description": "Équilibré. Très précis en français courant.",
        "compute_type": "float16"
    },
    "large-v3-turbo": {
        "id": "large-v3-turbo",
        "vram": "~3.0 Go",
        "description": "Qualité maximale. Comprend chuchotements, argot et syntaxe.",
        "compute_type": "float16"
    }
}


class WhisperEngine:
    def __init__(self, default_model: str = "large-v3-turbo", vram_unload_delay: float = 30.0):
        self.selected_model_name = default_model
        self.vram_unload_delay = vram_unload_delay
        
        self.model = None
        self._lock = threading.Lock()
        self._unload_timer: Optional[threading.Timer] = None
        
        self.device = "cuda"
        self.compute_type = "float16"

    def _cancel_unload_timer(self):
        if self._unload_timer is not None:
            self._unload_timer.cancel()
            self._unload_timer = None

    def _schedule_unload(self):
        self._cancel_unload_timer()
        if self.vram_unload_delay > 0:
            self._unload_timer = threading.Timer(self.vram_unload_delay, self.unload_model)
            self._unload_timer.daemon = True
            self._unload_timer.start()

    def load_model(self):
        with self._lock:
            self._cancel_unload_timer()
            
            if self.model is None:
                print(f"[Whisper] Chargement en VRAM du modèle '{self.selected_model_name}'...")
                start_t = time.time()
                
                try:
                    self.model = WhisperModel(
                        self.selected_model_name,
                        device=self.device,
                        compute_type=self.compute_type,
                        cpu_threads=4
                    )
                except Exception as e:
                    print(f"[Whisper] Échec CUDA ({e}). Bascule automatique sur CPU.")
                    self.device = "cpu"
                    self.compute_type = "int8"
                    self.model = WhisperModel(
                        self.selected_model_name,
                        device="cpu",
                        compute_type="int8",
                        cpu_threads=4
                    )

                print(f"[Whisper] Modèle prêt en {time.time() - start_t:.2f}s ({self.device.upper()}).")

    def unload_model(self):
        with self._lock:
            if self.model is not None:
                print("[Whisper] Inactivité : Libération de la VRAM.")
                del self.model
                self.model = None
                gc.collect()

    def set_model(self, model_name: str):
        if model_name not in MODELS_CONFIG:
            raise ValueError(f"Modèle inconnu : {model_name}")
        
        if self.selected_model_name != model_name:
            self.unload_model()
            self.selected_model_name = model_name
            print(f"[Whisper] Modèle configuré sur '{model_name}'.")

    def transcribe(self, audio_data: np.ndarray, language: str = "fr") -> str:
        if len(audio_data) == 0:
            return ""

        self.load_model()

        start_t = time.time()
        print("[Whisper] Début du traitement audio...")

        segments, _ = self.model.transcribe(
            audio_data,
            language=language,
            beam_size=5,
            vad_filter=False,
            initial_prompt="Bonjour, bienvenue. Voici une transcription claire en français."
        )

        text_segments = [s.text.strip() for s in segments]
        full_text = " ".join(text_segments).strip()

        duration = len(audio_data) / 16000.0
        elapsed = time.time() - start_t
        print(f"[Whisper] {duration:.1f}s d'audio traitées en {elapsed:.2f}s.")

        self._schedule_unload()
        return full_text