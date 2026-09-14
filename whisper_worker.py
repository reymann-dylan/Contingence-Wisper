# whisper_worker.py
import sys
import os
import json
import time

# Injection automatique des DLLs CUDA NVIDIA sous Windows
if sys.platform == "win32":
    try:
        import site
        for sp in site.getsitepackages():
            for sub in ("nvidia/cublas/bin", "nvidia/cudnn/bin", "nvidia/cublas/lib", "nvidia/cudnn/lib"):
                p = os.path.join(sp, sub.replace("/", os.sep))
                if os.path.isdir(p):
                    os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")
                    if hasattr(os, "add_dll_directory"):
                        try:
                            os.add_dll_directory(p)
                        except Exception:
                            pass
    except Exception:
        pass

import numpy as np

def run_transcription():
    if len(sys.argv) < 3:
        return

    model_name = sys.argv[1]
    audio_path = sys.argv[2]
    compute_device = sys.argv[3].lower() if len(sys.argv) > 3 else "cuda"
    
    # target_lang peut être "AUTO" ou un code ISO (FR, EN, ES...)
    target_lang = sys.argv[4].strip().upper() if len(sys.argv) > 4 else "AUTO"

    if not os.path.exists(audio_path):
        return

    try:
        from faster_whisper import WhisperModel
    except Exception as e:
        with open("temp_result.json", "w", encoding="utf-8") as f:
            json.dump({"text": "", "error": f"ImportError: {str(e)}"}, f)
        return

    try:
        audio_data = np.load(audio_path)
        duration = len(audio_data) / 16000.0
        start_time = time.time()

        device = "cuda" if compute_device == "cuda" else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"

        try:
            model = WhisperModel(model_name, device=device, compute_type=compute_type)
            device_used = device
        except Exception as e_cuda:
            print(f"[Worker] Repli CPU : {e_cuda}", file=sys.stderr)
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
            device_used = "cpu"

        # --- LOGIQUE SIMPLIFIÉE ---
        # target_lang provient directement de la combo du widget
        
        if target_lang == "AUTO":
            # Mode Transcription Native (détecte et écrit dans la même langue)
            task = "transcribe"
            lang_param = None
        else:
            # Mode Verrouillé (FR, EN, ES, etc.) : Force Whisper à sortir dans cette langue.
            # Si target_lang="EN" et qu'on parle français, Whisper traduit nativement vers l'anglais.
            task = "transcribe"
            lang_param = target_lang.lower()

        segments, info = model.transcribe(
            audio_data,
            beam_size=5,
            task=task,
            language=lang_param,
            temperature=0.0,
            vad_filter=False
        )

        text_parts = [seg.text.strip() for seg in segments if seg.text]
        text = " ".join(text_parts).strip()
        elapsed = time.time() - start_time

        result = {
            "text": text,
            "elapsed": elapsed,
            "duration": duration,
            "language": info.language if info else target_lang,
            "device_used": device_used
        }

    except Exception as e:
        print(f"[Worker Error] {e}", file=sys.stderr)
        result = {
            "text": "",
            "elapsed": 0.0,
            "duration": 0.0,
            "error": str(e)
        }

    with open("temp_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

if __name__ == "__main__":
    run_transcription()