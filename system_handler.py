# system_handler.py
import sys
import time
import ctypes
from typing import Callable, List, Dict, Optional
import pyperclip
from pynput import keyboard

NUMPAD_VK_MAP = {
    96: "numpad_0", 97: "numpad_1", 98: "numpad_2", 99: "numpad_3", 100: "numpad_4",
    101: "numpad_5", 102: "numpad_6", 103: "numpad_7", 104: "numpad_8", 105: "numpad_9",
    106: "numpad_*", 107: "numpad_+", 109: "numpad_-", 110: "numpad_.", 111: "numpad_/"
}

DISPLAY_NAMES = {
    "numpad_0": "NUMPAD 0", "numpad_1": "NUMPAD 1", "numpad_2": "NUMPAD 2",
    "numpad_3": "NUMPAD 3", "numpad_4": "NUMPAD 4", "numpad_5": "NUMPAD 5",
    "numpad_6": "NUMPAD 6", "numpad_7": "NUMPAD 7", "numpad_8": "NUMPAD 8",
    "numpad_9": "NUMPAD 9", "numpad_.": "NUMPAD .", "numpad_+": "NUMPAD +",
    "numpad_-": "NUMPAD -", "numpad_*": "NUMPAD *", "numpad_/": "NUMPAD /",
    "space": "ESPACE", "enter": "ENTRÉE", "backspace": "RETOUR",
    "caps_lock": "VERR MAJ", "tab": "TAB"
}


def key_name_to_vk(name: str) -> Optional[int]:
    """Convertit un identifiant de touche en code de touche virtuelle (Virtual Key) Windows."""
    name = name.lower().strip()
    if name.startswith("f") and name[1:].isdigit():
        num = int(name[1:])
        if 1 <= num <= 24:
            return 0x70 + (num - 1)  # VK_F1 = 0x70
    if name.startswith("numpad_") and name[7:].isdigit():
        return 0x60 + int(name[7:])  # VK_NUMPAD0 = 0x60

    special = {
        "space": 0x20, "enter": 0x0D, "tab": 0x09, "backspace": 0x08,
        "caps_lock": 0x14, "shift": 0x10, "ctrl": 0x11, "alt": 0x12,
        "numpad_.": 0x6E, "numpad_+": 0x6B, "numpad_-": 0x6D,
        "numpad_*": 0x6A, "numpad_/": 0x6F, "esc": 0x1B, "escape": 0x1B
    }
    if name in special:
        return special[name]

    if len(name) == 1 and sys.platform == "win32":
        res = ctypes.windll.user32.VkKeyScanW(ord(name))
        if res != -1:
            return res & 0xFF
    return None


class SystemHandler:
    def __init__(
        self,
        default_hotkey: str = "f8",
        ptt_hotkey: str = "f7",
        on_hotkey_down: Callable = None,
        on_hotkey_up: Callable = None,
        on_ptt_down: Callable = None,
        on_ptt_up: Callable = None,
        max_history: int = 15
    ):
        self.hotkey_key = default_hotkey.lower()
        self.ptt_key = ptt_hotkey.lower()

        self.hotkey_vk = key_name_to_vk(self.hotkey_key)
        self.ptt_vk = key_name_to_vk(self.ptt_key)

        self.on_hotkey_down = on_hotkey_down
        self.on_hotkey_up = on_hotkey_up
        self.on_ptt_down = on_ptt_down
        self.on_ptt_up = on_ptt_up

        self.history: List[Dict[str, str]] = []
        self.max_history = max_history

        self._kb_controller = keyboard.Controller()
        self._listener = None
        self._is_capturing = False
        self._capture_target = "main"
        self._capture_callback = None
        self._held_keys = set()

    def is_key_down(self, vk: Optional[int]) -> bool:
        """Interrogation matérielle directe au niveau de l'OS via Win32 GetAsyncKeyState."""
        if sys.platform == "win32" and vk:
            return bool(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000)
        return False

    def is_hotkey_physically_down(self) -> bool:
        return self.is_key_down(self.hotkey_vk)

    def is_ptt_physically_down(self) -> bool:
        return self.is_key_down(self.ptt_vk)

    def _normalize_key(self, key) -> str:
        if hasattr(key, "vk") and key.vk in NUMPAD_VK_MAP:
            return NUMPAD_VK_MAP[key.vk]
        if hasattr(key, "name") and key.name:
            return key.name.lower()
        if hasattr(key, "char") and key.char:
            return key.char.lower()

        raw = str(key).replace("'", "").replace("<", "").replace(">", "").strip().lower()
        if raw.isdigit() and int(raw) in NUMPAD_VK_MAP:
            return NUMPAD_VK_MAP[int(raw)]
        return raw

    def get_friendly_name(self, key_str: str = None) -> str:
        k = (key_str or self.hotkey_key).lower()
        if k in DISPLAY_NAMES:
            return DISPLAY_NAMES[k]
        return k.upper()

    def _on_press(self, key):
        key_str = self._normalize_key(key)
        vk = getattr(key, 'vk', None) or (key.value.vk if hasattr(key, 'value') and hasattr(key.value, 'vk') else None)

        if self._is_capturing:
            if self._capture_target == "main":
                self.hotkey_key = key_str
                self.hotkey_vk = vk or key_name_to_vk(key_str)
            else:
                self.ptt_key = key_str
                self.ptt_vk = vk or key_name_to_vk(key_str)

            self._is_capturing = False
            if self._capture_callback:
                self._capture_callback(self.get_friendly_name(key_str))
            return

        if key_str in self._held_keys:
            return
        self._held_keys.add(key_str)

        if key_str == self.hotkey_key:
            if vk:
                self.hotkey_vk = vk
            if self.on_hotkey_down:
                self.on_hotkey_down()
        elif key_str == self.ptt_key:
            if vk:
                self.ptt_vk = vk
            if self.on_ptt_down:
                self.on_ptt_down()

    def _on_release(self, key):
        key_str = self._normalize_key(key)
        self._held_keys.discard(key_str)

        if key_str == self.hotkey_key and self.on_hotkey_up:
            self.on_hotkey_up()
        elif key_str == self.ptt_key and self.on_ptt_up:
            self.on_ptt_up()

    def start_hotkey_listener(self):
        if self._listener is None:
            self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
            self._listener.daemon = True
            self._listener.start()

    def stop_hotkey_listener(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

    def capture_next_key(self, target: str, callback: Callable[[str], None]):
        self._capture_target = target
        self._capture_callback = callback
        self._is_capturing = True

    def set_max_history(self, new_limit: int):
        self.max_history = new_limit
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]

    def add_to_history(self, text: str):
        if not text.strip():
            return
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "text": text.strip()
        }
        self.history.insert(0, entry)
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]

    def delete_history_entry(self, index: int) -> bool:
        if 0 <= index < len(self.history):
            self.history.pop(index)
            return True
        return False

    def clear_all_history(self):
        self.history.clear()

    def paste_text(self, text: str):
        if not text.strip():
            return
        self.add_to_history(text)

        pyperclip.copy(text)
        time.sleep(0.05)
        self._kb_controller.press(keyboard.Key.ctrl)
        self._kb_controller.press('v')
        self._kb_controller.release('v')
        self._kb_controller.release(keyboard.Key.ctrl)

    def get_history(self) -> List[Dict[str, str]]:
        return self.history