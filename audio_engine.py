# audio_engine.py
import os
import time
import urllib.request
from typing import Optional, List, Tuple

import numpy as np
import sounddevice as sd
import onnxruntime as ort

MODEL_URL = "https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx"
MODEL_PATH = "silero_vad.onnx"


def get_input_devices() -> List[Tuple[int, str]]:
    devices = [(-1, "Microphone par défaut (Windows)")]
    try:
        hostapis = sd.query_hostapis()
        dev_list = sd.query_devices()
        for idx, dev in enumerate(dev_list):
            if dev.get("max_input_channels", 0) > 0:
                api_idx = dev.get("hostapi", -1)
                api_name = f" ({hostapis[api_idx]['name']})" if 0 <= api_idx < len(hostapis) else ""
                clean_name = f"{dev.get('name', f'Périphérique {idx}')}{api_name}"
                devices.append((idx, clean_name))
    except Exception:
        pass
    return devices


class SileroVAD:
    def __init__(self, model_path: str = MODEL_PATH):
        if not os.path.exists(model_path):
            urllib.request.urlretrieve(MODEL_URL, model_path)

        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = 1
        self.session = ort.InferenceSession(model_path, sess_options=opts, providers=["CPUExecutionProvider"])
        self.reset_states()

    def reset_states(self):
        self._state = np.zeros((2, 1, 128), dtype=np.float32)
        self._context = np.zeros((1, 64), dtype=np.float32)

    def is_speech(self, chunk_512: np.ndarray, threshold: float = 0.40) -> bool:
        x = chunk_512.reshape(1, -1).astype(np.float32)
        model_input = np.concatenate([self._context, x], axis=1)

        ort_inputs = {
            "input": model_input,
            "state": self._state,
            "sr": np.array(16000, dtype=np.int64)
        }
        out, self._state = self.session.run(None, ort_inputs)
        self._context = model_input[:, -64:]
        return bool(out[0][0] > threshold)


class AudioEngine:
    def __init__(
        self,
        sample_rate: int = 16000,
        silence_timeout: float = 5.0,
        silence_auto_stop: bool = True,
        is_ptt_active_callback=None,
        on_silence_stop=None,
        on_audio_level=None,
        device: Optional[int] = None
    ):
        self.sample_rate = sample_rate
        self.silence_timeout = silence_timeout
        self.silence_auto_stop = silence_auto_stop
        self.is_ptt_active_callback = is_ptt_active_callback
        self.chunk_size = 512
        self.device = device if (device is not None and device >= 0) else None

        self.vad = SileroVAD()
        self.is_recording = False
        self.has_spoken = False
        self.silence_start_time = None

        self.audio_frames = []
        self.on_silence_stop = on_silence_stop
        self.on_audio_level = on_audio_level
        self.stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        if not self.is_recording:
            return

        chunk = indata[:, 0]
        self.audio_frames.append(chunk.copy())

        rms = float(np.sqrt(np.mean(chunk**2)))
        if self.on_audio_level:
            self.on_audio_level(min(rms * 12.0, 1.0))

        is_voice = self.vad.is_speech(chunk) and (rms > 0.004)
        now = time.time()

        # Si la touche Push-to-talk est physiquement maintenue : neutralisation absolue du silence
        if self.is_ptt_active_callback and self.is_ptt_active_callback():
            self.silence_start_time = None
            if is_voice:
                self.has_spoken = True
            return

        if is_voice:
            self.has_spoken = True
            self.silence_start_time = None
        else:
            if self.silence_auto_stop and self.has_spoken:
                if self.silence_start_time is None:
                    self.silence_start_time = now
                elif now - self.silence_start_time >= self.silence_timeout:
                    if self.on_silence_stop:
                        self.on_silence_stop()

    def start(self):
        self.audio_frames.clear()
        self.has_spoken = False
        self.silence_start_time = None
        self.vad.reset_states()
        self.is_recording = True

        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=self.chunk_size,
                device=self.device,
                callback=self._audio_callback
            )
            self.stream.start()
        except Exception:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=self.chunk_size,
                device=None,
                callback=self._audio_callback
            )
            self.stream.start()

    def stop(self) -> np.ndarray:
        self.is_recording = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        if not self.audio_frames:
            return np.array([], dtype=np.float32)

        return np.concatenate(self.audio_frames, axis=0)