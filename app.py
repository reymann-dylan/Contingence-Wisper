# app.py
import os
import sys
import gc
import json
import ctypes
import subprocess
import threading
import time
import winsound
import math
import random
from datetime import datetime
from typing import Optional, List, Dict

if sys.platform == "win32":
    import winreg

import numpy as np
from PySide6.QtCore import Qt, QPoint, Signal, QObject, QRectF, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QIcon, QPixmap, QPainterPath
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel,
    QPushButton, QStackedWidget, QComboBox, QSpinBox, QCheckBox, QSlider,
    QLineEdit, QListWidget, QMenu, QSystemTrayIcon, QMessageBox, QFrame,
    QSizePolicy, QColorDialog, QScrollArea
)

from audio_engine import AudioEngine, get_input_devices
from system_handler import SystemHandler
from locales import t

APP_NAME = "CONTINGENCE | Wisper"
APP_ID = "galahad.contingence.wisper.v2"
REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_APP_NAME = "ContingenceWisper"
SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")


class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


THEME_PRESETS = {
    "gold": {
        "name": "Noir sombre or contingence",
        "accent": "#B58E3F",
        "accent_hover": "#D6A94D",
        "title_color": "#B58E3F",
        "sub_color": "#E2E8F0",
        "card_bg": "#111115",
        "card_border": "#212128",
        "section_line": "#191920",
        "input_bg": "#15151A",
        "input_border": "#282832",
        "btn_bg": "#18181E",
        "btn_border": "#282832",
        "btn_hover": "#22222B",
        "checkbox_border": "#B58E3F",
        "item_selected": "#282112"
    },
    "default": {
        "name": "Carbone & Graphite (Sobre)",
        "accent": "#94A3B8",
        "accent_hover": "#CBD5E1",
        "title_color": "#E2E8F0",
        "sub_color": "#94A3B8",
        "card_bg": "#111115",
        "card_border": "#202026",
        "section_line": "#18181F",
        "input_bg": "#15151A",
        "input_border": "#25252F",
        "btn_bg": "#17171E",
        "btn_border": "#25252F",
        "btn_hover": "#21212A",
        "checkbox_border": "#94A3B8",
        "item_selected": "#1F2330"
    }
}

# Liste de référence des langues supportées nativement par Whisper (Codes ISO)
WHISPER_ALL_LANGUAGES = [
    ("AUTO", "Détection Auto. (Native-à-Native)"),
    ("TRAD", "Traduction vers l'Anglais écrit"),
    ("FR", "Français (French)"),
    ("EN", "English (Anglais)"),
    ("ES", "Español (Spanish)"),
    ("DE", "Deutsch (German)"),
    ("IT", "Italiano (Italian)"),
    ("PT", "Português (Portuguese)"),
    ("JA", "日本語 (Japanese)"),
    ("ZH", "中文 (Chinese)"),
    ("RU", "Русский (Russian)"),
    ("AR", "العربية (Arabic)"),
    ("NL", "Nederlands (Dutch)"),
    ("PL", "Polski (Polish)"),
    ("KO", "한국어 (Korean)"),
    ("TR", "Türkçe (Turkish)"),
    ("UK", "Українська (Ukrainian)"),
    ("SV", "Svenska (Swedish)"),
    ("CS", "Čeština (Czech)"),
    ("EL", "Ελληνικά (Greek)"),
    ("DA", "Dansk (Danish)"),
    ("FI", "Suomi (Finnish)"),
    ("RO", "Română (Romanian)"),
    ("HU", "Magyar (Hungarian)"),
    ("VI", "Tiếng Việt (Vietnamese)"),
    ("TH", "ไทย (Thai)"),
    ("HI", "हिन्दी (Hindi)"),
    ("ID", "Bahasa Indonesia (Indonesian)")
]

DEFAULT_HUD_OPACITY = 90
DEFAULT_BG_COLOR = "#0F1017"
DEFAULT_WAVE_COLOR = "#B58E3F"
DEFAULT_MIC_COLOR = "#B58E3F"
DEFAULT_WAVE_STYLE = "waves"
DEFAULT_DIODE_STYLE = "ring"

GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000

MODELS_INFO = {
    "small": {"desc": "Ultra rapide (<0.5s), 1.0 Go VRAM"},
    "medium": {"desc": "Équilibré, 2.5 Go VRAM"},
    "large-v3-turbo": {"desc": "Qualité maximale, 3.0 Go VRAM"}
}

WAVE_STYLES = {
    "waves": "Vagues fluides multicouches (Siri)",
    "ripple": "Diffusion depuis le centre (Ripple)",
    "mirror": "Spectre symétrique (Moderne)",
    "bars": "Égaliseur dynamique"
}

CORNER_STYLES = {
    "pill": "Arrondi Pilule (Complet)",
    "rounded": "Coins Doux (10px)",
    "rect": "Coins Légers (4px)"
}

HUD_SIZES = {
    "standard": "Barre Standard (Complète)",
    "mini": "Barre Mini (Compromis)",
    "nano": "Barre Nano (Ultra-compacte)"
}

DIODE_STYLES = {
    "ring": "Diode anneau",
    "neon": "Halo néon",
    "dot": "Point pur"
}

SEASONAL_MODES = {
    "auto": "Automatique (selon le calendrier)",
    "christmas": "Noël (Flocons de neige)",
    "newyear": "Nouvel An (Feux d'artifice)",
    "halloween": "Halloween (Lucioles vertes subtiles)",
    "spring": "Printemps (Pétales de cerisier)",
    "disabled": "Désactivé"
}

if sys.platform == "win32":
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception:
        pass


def apply_win32_dark_frame(window: QWidget):
    if sys.platform == "win32":
        try:
            hwnd = int(window.winId())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            val = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(val), ctypes.sizeof(val))
            DWMWA_BORDER_COLOR = 34
            border_color = ctypes.c_int(0x00141418)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_BORDER_COLOR, ctypes.byref(border_color), ctypes.sizeof(border_color))
        except Exception:
            pass


def get_or_create_check_icon() -> str:
    target_dir = os.path.dirname(get_storage_path())
    icon_path = os.path.join(target_dir, "checkbox_tick.png")
    if not os.path.exists(icon_path):
        pix = QPixmap(14, 14)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#0A0A0E"), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin)
        p.setPen(pen)
        p.drawLine(3, 7, 6, 11)
        p.drawLine(6, 11, 11, 3)
        p.end()
        pix.save(icon_path, "PNG")
    return icon_path.replace("\\", "/")


def get_storage_path() -> str:
    app_data = os.environ.get("APPDATA")
    if app_data:
        base_dir = os.path.join(app_data, "ContingenceWisper")
    else:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "config.json")


def calculate_contrast_palette(bg_hex: str, auto_enabled: bool) -> Dict[str, str]:
    c = QColor(bg_hex)
    luminance = 0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()

    if auto_enabled and luminance > 145:
        return {
            "text": "#0F172A",
            "btn_bg": "rgba(0, 0, 0, 0.06)",
            "btn_hover": "rgba(0, 0, 0, 0.12)",
            "btn_border": "rgba(0, 0, 0, 0.14)",
            "icon_color": "#1E293B",
            "border_color": QColor(0, 0, 0, 45),
            "border_alpha": 45
        }
    else:
        return {
            "text": "#E2E8F0",
            "btn_bg": "rgba(255, 255, 255, 0.06)",
            "btn_hover": "rgba(255, 255, 255, 0.12)",
            "btn_border": "rgba(255, 255, 255, 0.10)",
            "icon_color": "#94A3B8",
            "border_color": QColor(255, 255, 255, 20),
            "border_alpha": 20
        }


def set_windows_autostart(enabled: bool) -> bool:
    if sys.platform != "win32":
        return False
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE)
        if enabled:
            if getattr(sys, "frozen", False):
                cmd = f'"{sys.executable}"'
            else:
                cmd = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
            winreg.SetValueEx(key, REG_APP_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, REG_APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def get_windows_autostart() -> bool:
    if sys.platform != "win32":
        return False
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ)
        try:
            val, _ = winreg.QueryValueEx(key, REG_APP_NAME)
            winreg.CloseKey(key)
            return bool(val)
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False


def play_audio_feedback(sound_name: str, enabled: bool, volume: float = 1.0):
    if not enabled or sys.platform != "win32" or volume <= 0.0:
        return

    wav_path = os.path.join(SOUNDS_DIR, f"{sound_name}.wav")
    if os.path.isfile(wav_path):
        try:
            winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        except Exception:
            pass

    def _beep():
        try:
            d_factor = max(0.3, volume)
            if sound_name == "start":
                winsound.Beep(900, int(45 * d_factor))
            elif sound_name == "stop":
                winsound.Beep(600, int(45 * d_factor))
            elif sound_name == "error":
                winsound.Beep(260, int(120 * d_factor))
            elif sound_name == "success":
                winsound.Beep(1150, int(45 * d_factor))
        except Exception:
            pass

    threading.Thread(target=_beep, daemon=True).start()


def load_app_icon() -> QIcon:
    for path in ("icon.ico", "icon.png", "assets/icon.png", "assets/icon.ico"):
        if os.path.exists(path):
            return QIcon(path)

    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor("#0F1017")))
    p.setPen(QPen(QColor("#B58E3F"), 2))
    p.drawRect(2, 2, 60, 60)
    p.setBrush(QBrush(QColor("#B58E3F")))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(26, 16, 12, 22))
    p.setPen(QPen(QColor("#E2E8F0"), 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap))
    p.setBrush(Qt.BrushStyle.NoBrush)
    arc_rect = QRectF(21, 24, 22, 18)
    p.drawArc(arc_rect, 0, -180 * 16)
    p.drawLine(32, 42, 32, 48)
    p.drawLine(26, 48, 38, 48)
    p.end()
    return QIcon(pix)


# ---------------------------------------------------------------------------
# Badge Lumineux d'État Multi-Styles
# ---------------------------------------------------------------------------
class StatusBadge(QWidget):
    def __init__(self, style_mode: str = DEFAULT_DIODE_STYLE):
        super().__init__()
        self.setFixedSize(18, 18)
        self.color_hex = "#10B981"
        self.style_mode = style_mode
        self.is_spinning = False
        self.angle = 0
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._timer = QTimer(self)
        self._timer.setInterval(35)
        self._timer.timeout.connect(self._rotate)

    def set_color(self, hex_val: str):
        self.color_hex = hex_val
        self.is_spinning = False
        self._timer.stop()
        self.update()

    def set_style_mode(self, mode: str):
        self.style_mode = mode
        self.update()

    def start_spinner(self, color_hex: str = "#B58E3F"):
        self.color_hex = color_hex
        self.is_spinning = True
        self._timer.start()

    def _rotate(self):
        self.angle = (self.angle + 24) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(self.color_hex)

        if self.is_spinning:
            p.translate(9, 9)
            p.rotate(self.angle)
            pen = QPen(c, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(QRectF(-7, -7, 14, 14), 0, 260 * 16)
            return

        if self.style_mode == "ring":
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(5.5, 5.5, 7, 7))
            pen = QPen(c, 1.4)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QRectF(2, 2, 14, 14))
        elif self.style_mode == "dot":
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(4.5, 4.5, 9, 9))
        else:  # neon
            halo = QColor(c)
            halo.setAlpha(45)
            p.setBrush(QBrush(halo))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(1, 1, 16, 16))
            p.setBrush(QBrush(c))
            p.drawEllipse(QRectF(4.5, 4.5, 9, 9))


# ---------------------------------------------------------------------------
# Visualiseur d'Ondes Vocales (Vagues fluides par défaut)
# ---------------------------------------------------------------------------
class SoundWaveWidget(QWidget):
    def __init__(self, style_mode: str = DEFAULT_WAVE_STYLE, color_hex: str = DEFAULT_WAVE_COLOR):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(24)
        self.style_mode = style_mode
        self.color_hex = color_hex
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.num_bars = 20
        self.current_heights = [0.06] * self.num_bars
        self.target_heights = [0.06] * self.num_bars
        self.smoothed_level = 0.0
        self.target_level = 0.0
        self.phase = 0.0

        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(25)
        self._anim_timer.timeout.connect(self._animate_step)

    def set_style_mode(self, mode: str):
        if mode in WAVE_STYLES:
            self.style_mode = mode
            self.update()

    def set_wave_color(self, hex_color: str):
        self.color_hex = hex_color
        self.update()

    def start_animation(self):
        self.reset()
        self._anim_timer.start()

    def stop_animation(self):
        self._anim_timer.stop()
        self.reset()

    def set_level(self, raw_val: float):
        boosted = min(1.0, math.pow(raw_val, 0.65) * 2.8)
        self.target_level = boosted
        center = (self.num_bars - 1) / 2.0

        for i in range(self.num_bars):
            dist = abs(i - center) / max(center, 1.0)
            bell_curve = max(0.12, 1.0 - math.pow(dist, 1.3) * 0.82)
            spread = 0.85 + 0.3 * math.sin(i * 1.7 + time.time() * 7.5)
            self.target_heights[i] = min(1.0, max(0.06, boosted * bell_curve * spread))

    def _animate_step(self):
        self.phase += 0.22
        self.smoothed_level += (self.target_level - self.smoothed_level) * 0.25

        for i in range(self.num_bars):
            cur = self.current_heights[i]
            tgt = self.target_heights[i]
            if tgt > cur:
                self.current_heights[i] = cur + (tgt - cur) * 0.45
            else:
                self.current_heights[i] = cur + (tgt - cur) * 0.12

        self.update()

    def reset(self):
        self.current_heights = [0.06] * self.num_bars
        self.target_heights = [0.06] * self.num_bars
        self.smoothed_level = 0.0
        self.target_level = 0.0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h_total = self.height()
        center_y = h_total / 2.0
        base_color = QColor(self.color_hex)

        if self.style_mode == "waves":
            max_amp = (h_total - 4) / 2.0 * max(0.18, self.smoothed_level)
            num_pts = 36

            c_bg = QColor(base_color)
            c_bg.setAlpha(85)
            pen_bg = QPen(c_bg, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(pen_bg)
            p.setBrush(Qt.BrushStyle.NoBrush)

            path_bg = QPainterPath()
            for i in range(num_pts):
                x = (w / (num_pts - 1)) * i
                nx = (x / w) * 2.0 - 1.0
                envelope = max(0.0, 1.0 - nx * nx)
                y = center_y + math.sin(nx * 5.0 - self.phase * 1.2) * (max_amp * 0.75 * envelope)
                if i == 0:
                    path_bg.moveTo(x, y)
                else:
                    path_bg.lineTo(x, y)
            p.drawPath(path_bg)

            pen_fg = QPen(base_color, 2.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(pen_fg)
            path_fg = QPainterPath()
            for i in range(num_pts):
                x = (w / (num_pts - 1)) * i
                nx = (x / w) * 2.0 - 1.0
                envelope = max(0.0, 1.0 - nx * nx)
                y = center_y + math.sin(nx * 4.2 + self.phase) * (max_amp * envelope)
                if i == 0:
                    path_fg.moveTo(x, y)
                else:
                    path_fg.lineTo(x, y)
            p.drawPath(path_fg)

        elif self.style_mode == "ripple":
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(base_color))
            bar_w = 3
            spacing = 3
            total_w = self.num_bars * (bar_w + spacing) - spacing
            start_x = max(0, (w - total_w) // 2)
            center_idx = (self.num_bars - 1) / 2.0

            for i in range(self.num_bars):
                dist = abs(i - center_idx)
                wave_prop = math.sin(dist * 1.1 - self.phase * 1.5)
                amp = max(0.1, (wave_prop * 0.5 + 0.5) * self.smoothed_level)
                bar_h = max(2.5, amp * (center_y - 2))
                x = start_x + i * (bar_w + spacing)
                p.drawRect(QRectF(x, center_y - bar_h, bar_w, bar_h * 2.0))

        elif self.style_mode == "mirror":
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(base_color))
            bar_w = 3
            spacing = 3
            total_w = self.num_bars * (bar_w + spacing) - spacing
            start_x = max(0, (w - total_w) // 2)

            for i in range(self.num_bars):
                bar_h = max(2.0, self.current_heights[i] * (center_y - 2))
                x = start_x + i * (bar_w + spacing)
                p.drawRect(QRectF(x, center_y - bar_h, bar_w, bar_h * 2.0))

        elif self.style_mode == "bars":
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(base_color))
            bar_w = 3
            spacing = 3
            total_w = self.num_bars * (bar_w + spacing) - spacing
            start_x = max(0, (w - total_w) // 2)
            max_h = h_total - 4

            for i in range(self.num_bars):
                bar_h = max(3.0, self.current_heights[i] * max_h)
                x = start_x + i * (bar_w + spacing)
                y = h_total - bar_h - 2
                p.drawRect(QRectF(x, y, bar_w, bar_h))


# ---------------------------------------------------------------------------
# Signaux
# ---------------------------------------------------------------------------
class AppSignals(QObject):
    state_changed = Signal(str, str)
    audio_level = Signal(float)
    flash_message = Signal(str, str, float)
    trigger_error = Signal()
    history_updated = Signal()
    key_reassigned = Signal(str)
    hud_style_changed = Signal()


# ---------------------------------------------------------------------------
# HUD Flottant avec Menu Déroulant de Langue
# ---------------------------------------------------------------------------
class FloatingHUD(QWidget):
    def __init__(self, signals: AppSignals, controller):
        super().__init__()
        self.signals = signals
        self.controller = controller

        self.state = "READY"
        self._is_dragging = False
        self._drag_pos = QPoint()
        self.is_error = False

        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(self._clear_toast)
        self._is_showing_toast = False

        self.particles: List[Dict] = []
        self.rockets: List[Dict] = []
        self.sparks: List[Dict] = []
        self._next_spawn_delay = 0

        self._particle_timer = QTimer(self)
        self._particle_timer.setInterval(30)
        self._particle_timer.timeout.connect(self._update_seasonal_fx)

        # Fenêtre sans bords, toujours au-dessus, pas de focus initial
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._init_ui()
        self.apply_size_mode()
        self.refresh_quick_languages()

        self.signals.state_changed.connect(self.set_state)
        self.signals.audio_level.connect(self.wave.set_level)
        self.signals.flash_message.connect(self.show_toast)
        self.signals.trigger_error.connect(self.flash_error)
        self.signals.key_reassigned.connect(self.update_key_label)
        self.signals.hud_style_changed.connect(self.apply_size_mode)

    # Empêcher la capture des touches clavier par le widget
    def keyPressEvent(self, event):
        event.ignore()

    def nativeEvent(self, eventType, message):
        if sys.platform == "win32":
            try:
                import ctypes.wintypes
                msg = ctypes.wintypes.MSG.from_address(int(message))
                # WM_CHOOSEFONT ou interaction combo: ne pas voler le focus
                if msg.message == 0x0021: # WM_MOUSEACTIVATE
                    return True, 3 # MA_NOACTIVATE
            except Exception:
                pass
        return super().nativeEvent(eventType, message)

    def showEvent(self, event):
        super().showEvent(event)
        if sys.platform == "win32":
            hwnd = int(self.winId())
            # Forcer WS_EX_NOACTIVATE après création
            cur = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, cur | WS_EX_NOACTIVATE)
        self._refresh_particle_state()

    def _get_idle_text(self) -> str:
        key_str = self.controller.system.get_friendly_name()
        ready_word = t("state_ready", self.controller.app_lang)
        press_word = t("press_key", self.controller.app_lang)
        if self.controller.key_display_minimal:
            return f"{ready_word} | {key_str}"
        return f"{ready_word} | {press_word} {key_str}"

    def _get_active_season(self) -> Optional[str]:
        mode = self.controller.seasonal_mode
        if mode in ("christmas", "newyear", "halloween", "spring", "disabled"):
            return None if mode == "disabled" else mode

        now = datetime.now()
        m, d = now.month, now.day
        if m == 12 and 1 <= d <= 29:
            return "christmas"
        if (m == 12 and d >= 30) or (m == 1 and d <= 2):
            return "newyear"
        if m == 10 and 20 <= d <= 31:
            return "halloween"
        if (m == 3 and d >= 20) or (m == 4 and d <= 10):
            return "spring"
        return None

    def _refresh_particle_state(self):
        season = self._get_active_season()
        if season and self.isVisible():
            self.particles.clear()
            self.rockets.clear()
            self.sparks.clear()

            w = max(self.width(), 120)
            h = max(self.height(), 40)

            if season == "christmas":
                for _ in range(16):
                    self.particles.append({
                        "x": random.uniform(4, w - 4),
                        "y": random.uniform(0, h),
                        "vx": random.uniform(-0.35, 0.35),
                        "vy": random.uniform(0.5, 1.1),
                        "size": random.uniform(1.8, 3.0),
                        "alpha": random.randint(110, 210),
                        "type": "snow"
                    })
            elif season == "spring":
                for _ in range(12):
                    self.particles.append({
                        "x": random.uniform(4, w - 4),
                        "y": random.uniform(0, h),
                        "vx": random.uniform(0.3, 0.9),
                        "vy": random.uniform(0.4, 0.8),
                        "angle": random.uniform(0, 360),
                        "alpha": random.randint(120, 200),
                        "type": "sakura"
                    })
            elif season == "halloween":
                for _ in range(12):
                    self.particles.append({
                        "x": random.uniform(2, w - 4),
                        "y": random.uniform(6, h - 6),
                        "vx": random.uniform(0.25, 0.55),
                        "vy": random.uniform(-0.20, 0.20),
                        "phase": random.uniform(0, 2 * math.pi),
                        "size": random.uniform(1.0, 1.8),
                        "alpha": random.randint(30, 95),
                        "type": "firefly"
                    })

            if not self._particle_timer.isActive():
                self._particle_timer.start()
        else:
            self._particle_timer.stop()
            self.particles.clear()
            self.rockets.clear()
            self.sparks.clear()
            self.update()

    def _update_seasonal_fx(self):
        season = self._get_active_season()
        if not season or not self.isVisible():
            self._particle_timer.stop()
            self.particles.clear()
            self.rockets.clear()
            self.sparks.clear()
            self.update()
            return

        w, h = self.width(), self.height()

        if season in ("christmas", "spring", "halloween"):
            for pt in self.particles:
                if pt["type"] == "snow":
                    pt["y"] += pt["vy"]
                    pt["x"] += pt["vx"] + math.sin(pt["y"] * 0.1) * 0.2
                    if pt["y"] > h - 4:
                        pt["y"] = random.uniform(0, 3)
                        pt["x"] = random.uniform(4, w - 4)
                elif pt["type"] == "sakura":
                    pt["y"] += pt["vy"]
                    pt["x"] += pt["vx"] + math.sin(pt["y"] * 0.15) * 0.4
                    pt["angle"] += 1.5
                    if pt["y"] > h - 3 or pt["x"] > w - 3:
                        pt["y"] = random.uniform(0, 3)
                        pt["x"] = random.uniform(0, w * 0.5)
                elif pt["type"] == "firefly":
                    pt["phase"] += 0.04
                    pt["x"] += pt["vx"] + math.cos(pt["phase"] * 0.5) * 0.10
                    pt["y"] += pt["vy"] + math.sin(pt["phase"]) * 0.15
                    pt["alpha"] = int(50 + 45 * math.sin(pt["phase"]))
                    if pt["x"] > w + 4:
                        pt["x"] = -4
                        pt["y"] = random.uniform(6, h - 6)
                    if pt["y"] < 3:
                        pt["y"] = h - 5
                    elif pt["y"] > h - 3:
                        pt["y"] = 5

        elif season == "newyear":
            self._next_spawn_delay -= 1
            if self._next_spawn_delay <= 0:
                self._next_spawn_delay = random.randint(18, 38)
                self.rockets.append({
                    "x": random.uniform(20, w - 20),
                    "y": h - 2,
                    "vx": random.uniform(-0.4, 0.4),
                    "vy": random.uniform(-3.8, -2.8),
                    "target_y": random.uniform(h * 0.2, h * 0.55),
                    "color": random.choice(["#B58E3F", "#F43F5E", "#38BDF8", "#4ADE80", "#FB923C", "#E879F9"])
                })

            alive_rockets = []
            for r in self.rockets:
                r["x"] += r["vx"]
                r["y"] += r["vy"]
                r["vy"] += 0.04
                if r["y"] <= r["target_y"] or r["vy"] >= -0.3:
                    spark_count = random.randint(14, 20)
                    for _ in range(spark_count):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(0.7, 2.4)
                        self.sparks.append({
                            "x": r["x"],
                            "y": r["y"],
                            "vx": math.cos(angle) * speed,
                            "vy": math.sin(angle) * speed,
                            "color": r["color"],
                            "alpha": 255,
                            "decay": random.uniform(5.5, 9.0),
                            "size": random.uniform(1.6, 2.4)
                        })
                else:
                    alive_rockets.append(r)
            self.rockets = alive_rockets

            alive_sparks = []
            for s in self.sparks:
                s["x"] += s["vx"]
                s["y"] += s["vy"]
                s["vx"] *= 0.94
                s["vy"] = (s["vy"] * 0.94) + 0.05
                s["alpha"] -= s["decay"]
                if s["alpha"] > 0 and 0 <= s["x"] <= w and 0 <= s["y"] <= h:
                    alive_sparks.append(s)
            self.sparks = alive_sparks

        self.update()

    def _init_ui(self):
        self.layout_main = QHBoxLayout(self)
        self.layout_main.setContentsMargins(10, 0, 8, 0)
        self.layout_main.setSpacing(6)

        self.badge = StatusBadge(style_mode=self.controller.diode_style)

        self.label = QLabel(self._get_idle_text())
        self.label.setFont(QFont("Segoe UI Variable Display", 9, QFont.Weight.Medium))
        self.label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.label.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.wave = SoundWaveWidget(
            style_mode=self.controller.wave_style,
            color_hex=self.controller.wave_color
        )
        self.wave.setVisible(False)

        # Menu déroulant de langue compact (ComboBox)
        self.combo_hud_lang = NoScrollComboBox()
        self.combo_hud_lang.setFixedSize(56, 30)
        self.combo_hud_lang.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.combo_hud_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.combo_hud_lang.currentIndexChanged.connect(self._on_hud_lang_changed)

        self.btn_copy = QPushButton()
        self.btn_copy.setFixedSize(26, 26)
        self.btn_copy.setIconSize(QSize(15, 15))
        self.btn_copy.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.setToolTip(t("menu_copy", self.controller.app_lang))
        self.btn_copy.clicked.connect(self.controller.copy_last_transcription)

        self.btn_action = QPushButton()
        self.btn_action.setFixedSize(30, 30)
        self.btn_action.setIconSize(QSize(22, 22))
        self.btn_action.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.clicked.connect(self.controller.toggle_recording)

        self.btn_settings = QPushButton()
        self.btn_settings.setFixedSize(24, 24)
        self.btn_settings.setIconSize(QSize(16, 16))
        self.btn_settings.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setStyleSheet("background: transparent; border: none;")
        self.btn_settings.clicked.connect(self.controller.open_settings)

        self.layout_main.addWidget(self.badge)
        self.layout_main.addWidget(self.label)
        self.layout_main.addWidget(self.wave, stretch=1)
        self.layout_main.addWidget(self.combo_hud_lang)
        self.layout_main.addWidget(self.btn_copy)
        self.layout_main.addWidget(self.btn_action)
        self.layout_main.addWidget(self.btn_settings)

    def _on_hud_lang_changed(self):
        new_lang = self.combo_hud_lang.currentText()
        if new_lang:
            self.controller.target_lang = new_lang
            self.controller.save_config()

    def refresh_quick_languages(self):
        self.combo_hud_lang.blockSignals(True)
        self.combo_hud_lang.clear()
        for slot_code in self.controller.quick_lang_slots:
            if slot_code:
                self.combo_hud_lang.addItem(slot_code)

        # Centrage du texte pour chaque élément
        for i in range(self.combo_hud_lang.count()):
            self.combo_hud_lang.setItemData(i, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)

        idx = self.combo_hud_lang.findText(self.controller.target_lang)
        if idx >= 0:
            self.combo_hud_lang.setCurrentIndex(idx)
        elif self.combo_hud_lang.count() > 0:
            self.combo_hud_lang.setCurrentIndex(0)
            self.controller.target_lang = self.combo_hud_lang.currentText()

        self.combo_hud_lang.blockSignals(False)
        
        # Restaurer la sélection précédente si possible
        idx = self.combo_hud_lang.findText(self.controller.target_lang)
        if idx >= 0:
            self.combo_hud_lang.setCurrentIndex(idx)
        elif self.combo_hud_lang.count() > 0:
            self.combo_hud_lang.setCurrentIndex(0)
            self.controller.target_lang = self.combo_hud_lang.currentText()
        
        # Mettre à jour les tooltips des items
        for i in range(self.combo_hud_lang.count()):
            full_name = self.combo_hud_lang.itemData(i)
            self.combo_hud_lang.setItemData(i, full_name, Qt.ItemDataRole.ToolTipRole)
            
        self.combo_hud_lang.blockSignals(False)

    def apply_size_mode(self):
        size_mode = self.controller.hud_size
        if size_mode == "nano":
            self.setFixedSize(145, 44)
            self.label.setVisible(False)
            self.wave.setVisible(False)
            self.combo_hud_lang.setVisible(False)
            self.btn_copy.setVisible(True)
        elif size_mode == "mini":
            self.setFixedSize(360, 48)
            self.combo_hud_lang.setVisible(True)
            self.btn_copy.setVisible(True)
            self.label.setVisible(self.state != "RECORDING")
            self.wave.setVisible(self.state == "RECORDING" and self.controller.wave_enabled)
        else: # standard
            self.setFixedSize(460, 52)
            self.combo_hud_lang.setVisible(True)
            self.btn_copy.setVisible(True)
            self.label.setVisible(True)
            self.wave.setVisible(self.state == "RECORDING" and self.controller.wave_enabled)

        self.badge.set_style_mode(self.controller.diode_style)
        self.wave.set_style_mode(self.controller.wave_style)
        self.wave.set_wave_color(self.controller.wave_color)
        if self.state == "READY" and not self._is_showing_toast:
            self.label.setText(self._get_idle_text())
        self._refresh_particle_state()
        self._update_graphics()
        self.update()

    def update_key_label(self, name: str):
        if not self._is_showing_toast and self.state == "READY":
            self.label.setText(self._get_idle_text())

    def show_toast(self, text: str, dot_color: str, duration: float):
        self._is_showing_toast = True
        self.wave.setVisible(False)
        self.wave.stop_animation()
        if self.controller.hud_size != "nano":
            self.label.setVisible(True)
            self.label.setText(text)
        self.badge.set_color(dot_color)
        self._toast_timer.start(int(duration * 1000))

    def _clear_toast(self):
        self._is_showing_toast = False
        self.set_state(self.state, "")

    def flash_error(self):
        self.is_error = True
        self.update()

        # Animation de vibration (shake)
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(220)
        cur = self.pos()
        anim.setKeyValueAt(0.0, cur)
        anim.setKeyValueAt(0.2, cur + QPoint(-7, 0))
        anim.setKeyValueAt(0.4, cur + QPoint(7, 0))
        anim.setKeyValueAt(0.6, cur + QPoint(-4, 0))
        anim.setKeyValueAt(0.8, cur + QPoint(4, 0))
        anim.setKeyValueAt(1.0, cur)
        anim.start()
        self._anim = anim # Conserver référence

        QTimer.singleShot(600, self._clear_error_state)

    def _clear_error_state(self):
        self.is_error = False
        self.update()

    def set_state(self, state: str, message: str):
        self.state = state

        if state in ("RECORDING", "PROCESSING"):
            if self._is_showing_toast:
                self._toast_timer.stop()
                self._is_showing_toast = False
        elif self._is_showing_toast:
            return

        size_mode = self.controller.hud_size

        if state == "READY":
            if size_mode != "nano":
                self.label.setVisible(True)
                self.label.setText(self._get_idle_text())
            self.wave.setVisible(False)
            self.wave.stop_animation()
            self.badge.set_color("#10B981")
            self.btn_action.setEnabled(True)
            self.combo_hud_lang.setEnabled(True)

        elif state == "RECORDING":
            if size_mode == "mini":
                self.label.setVisible(False)
            elif size_mode == "standard":
                self.label.setVisible(True)
                self.label.setText(t("state_listening", self.controller.app_lang))

            if size_mode != "nano" and self.controller.wave_enabled:
                self.wave.setVisible(True)
                self.wave.start_animation()
            self.badge.set_color("#EF4444")
            self.btn_action.setEnabled(True)
            self.combo_hud_lang.setEnabled(False)

        elif state == "PROCESSING":
            if size_mode != "nano":
                self.label.setVisible(True)
                self.label.setText(message or t("state_processing", self.controller.app_lang))
            self.wave.setVisible(False)
            self.wave.stop_animation()
            self.badge.start_spinner("#B58E3F")
            self.btn_action.setEnabled(False)
            self.combo_hud_lang.setEnabled(False)

        self._update_graphics()

    def _update_graphics(self):
        pal = calculate_contrast_palette(self.controller.hud_bg_color, self.controller.auto_contrast)

        self.label.setStyleSheet(f"color: {pal['text']}; background: transparent;")

        hud_elem_style = f"""
            background-color: {pal['btn_bg']};
            border: 1px solid {pal['btn_border']};
            color: {pal['text']};
            font-size: 11px;
            font-weight: bold;
        """
        self.btn_copy.setStyleSheet(f"QPushButton {{ {hud_elem_style} border-radius: 4px; }} QPushButton:hover {{ background-color: {pal['btn_hover']}; }}")

# Menu déroulant minimaliste : aucun carré, aucune flèche
        self.combo_hud_lang.setStyleSheet(f"""
            QComboBox {{
                background-color: {pal['btn_bg']};
                border: 1px solid {pal['btn_border']};
                color: {pal['text']};
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
                padding: 0px;
            }}
            QComboBox:hover {{
                background-color: {pal['btn_hover']};
            }}
            QComboBox:disabled {{
                opacity: 0.5;
                color: {pal['icon_color']};
            }}
            QComboBox::drop-down {{
                width: 0px;
                border: none;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0px;
                height: 0px;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.controller.hud_bg_color};
                border: 1px solid {pal['btn_border']};
                color: {pal['text']};
                selection-background-color: {pal['btn_hover']};
                selection-color: #FFFFFF;
                outline: none;
                padding: 4px;
            }}
        """)

        pix_c = QPixmap(16, 16)
        pix_c.fill(Qt.GlobalColor.transparent)
        pc = QPainter(pix_c)
        pc.setRenderHint(QPainter.RenderHint.Antialiasing)
        pc.setPen(QPen(QColor(pal['icon_color']), 1.4))
        pc.setBrush(Qt.BrushStyle.NoBrush)
        pc.drawRect(QRectF(4.5, 1.5, 9.5, 10.5))
        pc.setBrush(QBrush(QColor(self.controller.hud_bg_color)))
        pc.drawRect(QRectF(1.5, 4.5, 9.5, 10.5))
        pc.end()
        self.btn_copy.setIcon(QIcon(pix_c))

        pix_a = QPixmap(30, 30)
        pix_a.fill(Qt.GlobalColor.transparent)
        pa = QPainter(pix_a)
        pa.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.state == "RECORDING":
            self.btn_action.setStyleSheet("QPushButton { background-color: #EF4444; border-radius: 15px; }")
            pa.setBrush(QBrush(QColor("#FFFFFF")))
            pa.setPen(Qt.PenStyle.NoPen)
            pa.drawRect(QRectF(9, 9, 12, 12))
        else:
            self.btn_action.setStyleSheet(f"""
                QPushButton {{
                    background-color: {pal['btn_bg']};
                    border: 1px solid {pal['btn_border']};
                    border-radius: 15px;
                }}
                QPushButton:hover {{
                    background-color: {pal['btn_hover']};
                }}
            """)
            mic_c = QColor(self.controller.mic_color)
            pa.setBrush(QBrush(mic_c))
            pa.setPen(Qt.PenStyle.NoPen)
            pa.drawRect(QRectF(11.5, 5.5, 7, 12))
            pa.setPen(QPen(mic_c, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            pa.drawArc(QRectF(8.5, 10, 13, 10), 0, -180 * 16)
            pa.drawLine(15, 20, 15, 24)
            pa.drawLine(11, 24, 19, 24)
        pa.end()
        self.btn_action.setIcon(QIcon(pix_a))

        pix_s = QPixmap(20, 20)
        pix_s.fill(Qt.GlobalColor.transparent)
        ps = QPainter(pix_s)
        ps.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen_s = QPen(QColor(pal['icon_color']), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        ps.setPen(pen_s)
        ps.setBrush(Qt.BrushStyle.NoBrush)
        ps.drawLine(3, 6, 17, 6)
        ps.setBrush(QBrush(QColor(self.controller.hud_bg_color)))
        ps.drawEllipse(QRectF(5, 4, 4, 4))
        ps.setBrush(Qt.BrushStyle.NoBrush)
        ps.drawLine(3, 14, 17, 14)
        ps.setBrush(QBrush(QColor(self.controller.hud_bg_color)))
        ps.drawEllipse(QRectF(11, 12, 4, 4))
        ps.end()
        self.btn_settings.setIcon(QIcon(pix_s))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        radius = 25
        if self.controller.corner_style == "rounded":
            radius = 10
        elif self.controller.corner_style == "rect":
            radius = 2

        alpha = int((self.controller.hud_opacity / 100.0) * 255)
        base_bg = QColor(self.controller.hud_bg_color)
        pal = calculate_contrast_palette(self.controller.hud_bg_color, self.controller.auto_contrast)

        clip_path = QPainterPath()
        clip_path.addRoundedRect(self.rect().adjusted(1, 1, -1, -1), radius, radius)

        if self.is_error:
            painter.setBrush(QBrush(QColor(45, 15, 20, alpha)))
            painter.setPen(QPen(QColor(239, 68, 68, 90), 1))
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), radius, radius)
        else:
            base_bg.setAlpha(alpha)
            painter.setBrush(QBrush(base_bg))
            painter.setPen(QPen(pal["border_color"], 1))
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), radius, radius)

        season = self._get_active_season()
        if season:
            painter.save()
            painter.setClipPath(clip_path)

            if season == "christmas":
                painter.setPen(Qt.PenStyle.NoPen)
                for flake in self.particles:
                    painter.setBrush(QBrush(QColor(240, 245, 255, flake["alpha"])))
                    painter.drawEllipse(QPoint(int(flake["x"]), int(flake["y"])), int(flake["size"]), int(flake["size"]))

            elif season == "spring":
                painter.setPen(Qt.PenStyle.NoPen)
                for p in self.particles:
                    painter.save()
                    painter.translate(p["x"], p["y"])
                    painter.rotate(p["angle"])
                    painter.setBrush(QBrush(QColor(255, 183, 197, p["alpha"])))
                    painter.drawEllipse(QRectF(-2.5, -1.5, 5, 3))
                    painter.restore()

            elif season == "halloween":
                painter.setPen(Qt.PenStyle.NoPen)
                for pt in self.particles:
                    # Lumière verte saccadée subtile
                    a = max(10, min(110, pt.get("alpha", 60)))
                    core_c = QColor(74, 222, 128, a)
                    halo_c = QColor(34, 197, 94, int(a * 0.18))
                    painter.setBrush(QBrush(halo_c))
                    painter.drawEllipse(QPoint(int(pt["x"]), int(pt["y"])), int(pt["size"] * 1.6), int(pt["size"] * 1.6))
                    painter.setBrush(QBrush(core_c))
                    painter.drawEllipse(QPoint(int(pt["x"]), int(pt["y"])), int(pt["size"]), int(pt["size"]))

            elif season == "newyear":
                for r in self.rockets:
                    c = QColor(r["color"])
                    c.setAlpha(200)
                    painter.setPen(QPen(c, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                    painter.drawLine(int(r["x"]), int(r["y"]), int(r["x"] - r["vx"] * 3), int(r["y"] - r["vy"] * 3))

                painter.setPen(Qt.PenStyle.NoPen)
                for s in self.sparks:
                    c = QColor(s["color"])
                    c.setAlpha(int(max(0, min(255, s["alpha"]))))
                    painter.setBrush(QBrush(c))
                    painter.drawEllipse(QPoint(int(s["x"]), int(s["y"])), int(s["size"]), int(s["size"]))

            painter.restore()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        self.controller.save_config()

    def contextMenuEvent(self, event):
        lang = self.controller.app_lang
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #121216; color: #E2E8F0; border: 1px solid #262632; padding: 4px; border-radius: 0px; }
            QMenu::item { padding: 6px 18px; border-radius: 0px; }
            QMenu::item:selected { background-color: #1E1E26; }
        """)
        a_copy = menu.addAction(t("menu_copy", lang))

        menu_size = menu.addMenu(t("menu_size", lang))
        a_standard = menu_size.addAction("Standard")
        a_mini = menu_size.addAction("Mini")
        a_nano = menu_size.addAction("Nano")

        a_hide = menu.addAction(t("menu_hide", lang))
        a_reset = menu.addAction(t("menu_recenter", lang))
        menu.addSeparator()
        a_settings = menu.addAction(t("menu_settings", lang))
        a_restart = menu.addAction(t("menu_restart", lang))
        menu.addSeparator()
        a_quit = menu.addAction(t("menu_quit", lang))

        act = menu.exec(event.globalPos())
        if act == a_copy:
            self.controller.copy_last_transcription()
        elif act == a_standard:
            self.controller.set_hud_size("standard")
        elif act == a_mini:
            self.controller.set_hud_size("mini")
        elif act == a_nano:
            self.controller.set_hud_size("nano")
        elif act == a_hide:
            self.controller.toggle_hud(False)
        elif act == a_reset:
            self.controller.reset_hud_position()
        elif act == a_settings:
            self.controller.open_settings()
        elif act == a_restart:
            self.controller.restart_app()
        elif act == a_quit:
            QApplication.quit()


# ---------------------------------------------------------------------------
# Fenêtre des Paramètres Géométrique (Sans Bords Ronds)
# ---------------------------------------------------------------------------
class SettingsDialog(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(load_app_icon())
        self.setFixedSize(650, 790)
        self.nav_buttons = []
        self.apply_theme_style()
        self._init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        apply_win32_dark_frame(self)

    def apply_theme_style(self):
        preset = THEME_PRESETS.get(self.controller.theme_mode) or THEME_PRESETS.get("gold", {})
        accent = preset.get("accent", "#B58E3F")
        accent_hover = preset.get("accent_hover", "#D6A94D")
        card_bg = preset.get("card_bg", "#111115")
        card_border = preset.get("card_border", "#212128")
        input_bg = preset.get("input_bg", "#15151A")
        input_border = preset.get("input_border", "#282832")
        btn_bg = preset.get("btn_bg", "#18181E")
        btn_border = preset.get("btn_border", "#282832")
        btn_hover = preset.get("btn_hover", "#22222B")
        item_sel = preset.get("item_selected", "#282112")
        checkbox_border = preset.get("checkbox_border", "#B58E3F")
        check_icon_path = get_or_create_check_icon()

        self.setStyleSheet(f"""
            QWidget {{
                background-color: #0C0C0F;
                color: #E2E8F0;
                font-family: 'Segoe UI Variable Text', sans-serif;
                font-size: 13px;
            }}

            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}

            QFrame#SectionCard {{
                background-color: {card_bg};
                border: 1px solid {card_border};
                border-radius: 0px;
            }}
            QFrame#HighlightedCard {{
                background-color: rgba(181, 142, 63, 0.08);
                border: 1px solid rgba(181, 142, 63, 0.35);
                border-radius: 0px;
            }}
            QLabel#SectionTitle {{
                color: {accent};
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 0.8px;
                background: transparent;
            }}
            QLabel {{ background: transparent; }}

            QComboBox, QSpinBox, QLineEdit {{
                background-color: {input_bg};
                border: 1px solid {input_border};
                border-radius: 0px;
                padding: 5px 10px;
                min-height: 25px;
                color: #FFFFFF;
            }}
            QComboBox:hover, QSpinBox:hover, QLineEdit:hover {{
                border-color: {accent};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 22px;
                border: none;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                width: 0px;
                height: 0px;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {accent};
                margin-right: 2px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #111115;
                border: 1px solid {card_border};
                selection-background-color: {item_sel};
                selection-color: #FFFFFF;
                color: #E2E8F0;
                padding: 4px;
                outline: none;
            }}

            QPushButton {{
                background-color: {btn_bg};
                border: 1px solid {btn_border};
                border-radius: 0px;
                padding: 6px 14px;
                min-height: 24px;
                color: #FFFFFF;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
                border-color: #383845;
            }}

            QPushButton[nav="tab"] {{
                background-color: #141418;
                border: 1px solid #202026;
                border-radius: 0px;
                padding: 8px 12px;
                color: #8E94A5;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton[nav="tab"]:hover {{
                background-color: #1C1C22;
                color: #FFFFFF;
                border-color: #2D2D36;
            }}
            QPushButton[nav="active"] {{
                background-color: #17171E;
                border: 1px solid {accent};
                border-radius: 0px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 12px;
            }}

            QPushButton#RedButton {{
                background-color: #241113;
                border: 1px solid #54171B;
                border-radius: 0px;
                color: #FCA5A5;
                font-weight: bold;
            }}
            QPushButton#RedButton:hover {{
                background-color: #351418;
                border-color: #EF4444;
                color: #FFFFFF;
            }}

            QSlider {{ background: transparent; }}
            QSlider::groove:horizontal {{
                height: 4px;
                background: #1F1F26;
                border-radius: 0px;
            }}
            QSlider::sub-page:horizontal {{
                background: {accent};
                border-radius: 0px;
            }}
            QSlider::handle:horizontal {{
                background: #FFFFFF;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 0px;
                border: 1px solid {accent_hover};
            }}

            QListWidget {{
                background-color: #0E0E12;
                border: 1px solid {card_border};
                border-radius: 0px;
                padding: 4px;
                outline: none;
            }}
            QListWidget::item {{
                background-color: #131318;
                border: 1px solid transparent;
                border-radius: 0px;
                padding: 7px 9px;
                margin-bottom: 2px;
                color: #E2E8F0;
                font-size: 12px;
                outline: none;
            }}
            QListWidget::item:hover {{
                background-color: #1A1A22;
                border-color: #2A2A35;
            }}
            QListWidget::item:selected {{
                background-color: {item_sel};
                border: 1px solid {accent};
                color: #FFFFFF;
            }}

            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 7px;
                margin: 0px;
                border-radius: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #202028;
                min-height: 24px;
                border-radius: 0px;
            }}
            QScrollBar::handle:vertical:hover {{ background: #30303D; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            QScrollBar::corner {{ background: transparent; }}

            QCheckBox {{
                background: transparent;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border: 1px solid {checkbox_border};
                border-radius: 0px;
                background-color: {input_bg};
            }}
            QCheckBox::indicator:hover {{
                border-color: {accent_hover};
            }}
            QCheckBox::indicator:checked {{
                background-color: {accent};
                border-color: {accent};
                image: url("{check_icon_path}");
            }}
        """)

    def _create_clean_section(self, title: str, layout_content, is_highlighted: bool = False) -> QFrame:
        card = QFrame()
        card.setObjectName("HighlightedCard" if is_highlighted else "SectionCard")
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(14, 12, 14, 14)
        vbox.setSpacing(12)

        lbl_t = QLabel(title.upper())
        lbl_t.setObjectName("SectionTitle")
        vbox.addWidget(lbl_t)

        preset = THEME_PRESETS.get(self.controller.theme_mode) or THEME_PRESETS.get("gold", {})
        line_color = "rgba(181, 142, 63, 0.35)" if is_highlighted else preset.get("section_line", "#191920")

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {line_color}; max-height: 1px;")
        vbox.addWidget(divider)

        vbox.addLayout(layout_content)
        return card

    def _wrap_in_scroll(self, content_widget: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(content_widget)
        return scroll

    def _set_active_tab(self, idx: int):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("nav", "active" if i == idx else "tab")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 16)
        root.setSpacing(10)

        lang = self.controller.app_lang
        preset = THEME_PRESETS.get(self.controller.theme_mode) or THEME_PRESETS.get("gold", {})

        # Header de la fenêtre
        header = QHBoxLayout()
        header.setContentsMargins(4, 0, 4, 4)
        header.setSpacing(12)

        lbl_logo = QLabel()
        lbl_logo.setPixmap(load_app_icon().pixmap(36, 36))

        v_brand = QVBoxLayout()
        v_brand.setSpacing(2)
        self.lbl_title = QLabel(APP_NAME)
        self.lbl_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {preset.get('title_color', '#B58E3F')};")

        self.lbl_sub = QLabel(t("app_subtitle", lang))
        self.lbl_sub.setStyleSheet("font-size: 11px; color: #E2E8F0;")
        v_brand.addWidget(self.lbl_title)
        v_brand.addWidget(self.lbl_sub)

        header.addWidget(lbl_logo)
        header.addLayout(v_brand)
        header.addStretch()
        root.addLayout(header)

        # Navigation par onglets (Grid)
        nav_grid = QGridLayout()
        nav_grid.setSpacing(5)
        tab_names = [
            t("tab_sys", lang),
            t("tab_audio", lang),
            t("tab_style", lang),
            t("tab_lang", lang),
            t("tab_hist", lang),
            t("tab_about", lang)
        ]
        self.nav_buttons = []
        for i, name in enumerate(tab_names):
            btn = QPushButton(name)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            row = i // 3
            col = i % 3
            btn.clicked.connect(lambda _, idx=i: self._set_active_tab(idx))
            nav_grid.addWidget(btn, row, col)
            self.nav_buttons.append(btn)

        root.addLayout(nav_grid)

        # Stacked Widget pour le contenu des onglets
        self.stack = QStackedWidget()

        # =============================================================
        # Page 1 : Système | Moteur (Langue & Autostart en tête)
        # =============================================================
        t_sys_content = QWidget()
        l_sys = QVBoxLayout(t_sys_content)
        l_sys.setSpacing(12)
        l_sys.setContentsMargins(4, 8, 4, 8)

        # Langue de l'interface
        l_app_l = QVBoxLayout()
        h_al = QHBoxLayout()
        lbl_al = QLabel(t("lbl_app_lang", lang))
        lbl_al.setFixedWidth(175)
        h_al.addWidget(lbl_al)
        self.combo_app_lang = NoScrollComboBox()
        self.combo_app_lang.addItem("Français (French)", "fr")
        self.combo_app_lang.addItem("English (Anglais)", "en")
        idx_al = self.combo_app_lang.findData(self.controller.app_lang)
        if idx_al >= 0:
            self.combo_app_lang.setCurrentIndex(idx_al)
        self.combo_app_lang.currentIndexChanged.connect(self._on_app_lang_change)
        h_al.addWidget(self.combo_app_lang)
        l_app_l.addLayout(h_al)
        l_sys.addWidget(self._create_clean_section(t("sec_app_lang", lang), l_app_l))

        # Démarrage automatique
        l_boot = QVBoxLayout()
        self.chk_autostart = QCheckBox(t("autostart_label", lang))
        self.chk_autostart.setChecked(get_windows_autostart())
        self.chk_autostart.toggled.connect(self._on_autostart_toggled)
        l_boot.addWidget(self.chk_autostart)
        l_sys.addWidget(self._create_clean_section(t("sec_boot", lang), l_boot, is_highlighted=True))

        # Accélération matérielle
        l_dev_mode = QVBoxLayout()
        self.combo_compute_device = NoScrollComboBox()
        self.combo_compute_device.addItem(t("device_gpu", lang), "cuda")
        self.combo_compute_device.addItem(t("device_cpu", lang), "cpu")
        idx_dev = self.combo_compute_device.findData(self.controller.compute_device)
        if idx_dev >= 0:
            self.combo_compute_device.setCurrentIndex(idx_dev)
        self.combo_compute_device.currentIndexChanged.connect(self._on_compute_device_change)
        l_dev_mode.addWidget(self.combo_compute_device)
        l_sys.addWidget(self._create_clean_section(t("sec_device", lang), l_dev_mode))

        # Sélection du modèle Whisper
        l_m = QVBoxLayout()
        self.combo_model = NoScrollComboBox()
        self.combo_model.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_model.setMinimumContentsLength(20)
        self.combo_model.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for k, v in MODELS_INFO.items():
            self.combo_model.addItem(f"{k.upper()} ({v['desc']})", k)
        idx = self.combo_model.findData(self.controller.selected_model)
        if idx >= 0:
            self.combo_model.setCurrentIndex(idx)
        self.combo_model.currentIndexChanged.connect(self._on_model_change)
        l_m.addWidget(self.combo_model)
        l_sys.addWidget(self._create_clean_section(t("sec_model", lang), l_m))

        # Spécifications et stockage
        l_spec = QVBoxLayout()
        l_spec.setSpacing(6)
        lbl_spec1 = QLabel("• <b>Moteur :</b> Faster-Whisper (CTranslate2 • CUDA 12 FP16 / CPU int8)")
        lbl_spec2 = QLabel("• <b>Mémoire :</b> ~80 Mo RAM au repos (Sous-processus isolé)")
        lbl_spec3 = QLabel(f"• <b>Stockage :</b> {os.path.dirname(self.controller.config_filepath)}")
        lbl_spec1.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        lbl_spec2.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        lbl_spec3.setStyleSheet("color: #94A3B8; font-size: 11px;")
        lbl_spec3.setWordWrap(True)
        l_spec.addWidget(lbl_spec1)
        l_spec.addWidget(lbl_spec2)
        l_spec.addWidget(lbl_spec3)

        btn_open_storage = QPushButton(t("btn_open_storage", lang))
        btn_open_storage.clicked.connect(self._open_appdata_folder)
        l_spec.addWidget(btn_open_storage)
        l_sys.addWidget(self._create_clean_section(t("sec_specs", lang), l_spec))

        # Maintenance
        l_acts = QHBoxLayout()
        btn_recenter = QPushButton(t("btn_recenter", lang))
        btn_recenter.clicked.connect(self.controller.reset_hud_position)

        btn_restart = QPushButton(t("btn_restart", lang))
        btn_restart.setObjectName("RedButton")
        btn_restart.clicked.connect(self.controller.restart_app)

        l_acts.addWidget(btn_recenter)
        l_acts.addWidget(btn_restart)
        l_sys.addWidget(self._create_clean_section(t("sec_maint", lang), l_acts))

        l_sys.addStretch()
        self.stack.addWidget(self._wrap_in_scroll(t_sys_content))

        # =============================================================
        # Page 2 : Raccourcis | Micro
        # =============================================================
        t_audio_content = QWidget()
        l_audio = QVBoxLayout(t_audio_content)
        l_audio.setSpacing(12)
        l_audio.setContentsMargins(4, 8, 4, 8)

        l_k = QVBoxLayout()
        l_k.setSpacing(8)
        
        # Touche principale
        h_main_k = QHBoxLayout()
        lbl_k1 = QLabel(t("lbl_main_hotkey", lang))
        lbl_k1.setFixedWidth(175)
        h_main_k.addWidget(lbl_k1)
        self.btn_capture = QPushButton(f"{self.controller.system.get_friendly_name()}")
        self.btn_capture.clicked.connect(lambda: self._start_capture("main"))
        h_main_k.addWidget(self.btn_capture)
        l_k.addLayout(h_main_k)

        # Mode maintien (PTT)
        self.chk_ptt = QCheckBox(t("chk_ptt", lang))
        self.chk_ptt.setChecked(self.controller.ptt_enabled)
        self.chk_ptt.toggled.connect(self._on_ptt_toggle)
        l_k.addWidget(self.chk_ptt)

        self.chk_ptt_dedicated = QCheckBox(t("chk_ptt_dedicated", lang))
        self.chk_ptt_dedicated.setChecked(self.controller.ptt_dedicated)
        self.chk_ptt_dedicated.setEnabled(self.controller.ptt_enabled)
        self.chk_ptt_dedicated.toggled.connect(self._on_ptt_dedicated_toggle)
        l_k.addWidget(self.chk_ptt_dedicated)

        # Touche dédiée PTT
        self.w_ptt_key = QWidget()
        h_ptt_k = QHBoxLayout(self.w_ptt_key)
        h_ptt_k.setContentsMargins(0, 0, 0, 0)
        lbl_k2 = QLabel(t("lbl_ptt_dedicated", lang))
        lbl_k2.setFixedWidth(175)
        h_ptt_k.addWidget(lbl_k2)
        self.btn_capture_ptt = QPushButton(f"{self.controller.system.get_friendly_name(self.controller.system.ptt_key)}")
        self.btn_capture_ptt.clicked.connect(lambda: self._start_capture("ptt"))
        h_ptt_k.addWidget(self.btn_capture_ptt)
        self.w_ptt_key.setVisible(self.controller.ptt_enabled and self.controller.ptt_dedicated)
        l_k.addWidget(self.w_ptt_key)

        lbl_ptt_hint = QLabel(f"<i>{t('ptt_hint', lang)}</i>")
        lbl_ptt_hint.setStyleSheet("color: #94A3B8; font-size: 11px;")
        lbl_ptt_hint.setWordWrap(True)
        l_k.addWidget(lbl_ptt_hint)

        l_audio.addWidget(self._create_clean_section(t("sec_shortcuts", lang), l_k))

        l_dev = QVBoxLayout()
        l_dev.setSpacing(8)
        
        # Choix du microphone
        self.combo_mic = NoScrollComboBox()
        self.combo_mic.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_mic.setMinimumContentsLength(20)
        self.combo_mic.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.refresh_audio_devices()
        self.combo_mic.currentIndexChanged.connect(self._on_mic_change)
        l_dev.addWidget(self.combo_mic)

        # Gain audio
        h_gain = QHBoxLayout()
        lbl_gain = QLabel(t("lbl_audio_gain", lang))
        lbl_gain.setFixedWidth(175)
        h_gain.addWidget(lbl_gain)
        self.slider_gain = QSlider(Qt.Orientation.Horizontal)
        self.slider_gain.setRange(0, 200)
        self.slider_gain.setValue(int(self.controller.audio_gain * 100))
        self.lbl_gain_val = QLabel(f"{int(self.controller.audio_gain * 100)}%")
        self.lbl_gain_val.setFixedWidth(40)
        self.slider_gain.valueChanged.connect(self._on_gain_changed)
        h_gain.addWidget(self.slider_gain)
        h_gain.addWidget(self.lbl_gain_val)
        l_dev.addLayout(h_gain)

        # Coupure silence auto
        self.chk_silence_auto = QCheckBox(t("chk_silence", lang))
        self.chk_silence_auto.setChecked(self.controller.silence_auto_stop)
        self.chk_silence_auto.toggled.connect(self._on_silence_toggle)
        l_dev.addWidget(self.chk_silence_auto)

        h_sil = QHBoxLayout()
        lbl_s1 = QLabel(t("lbl_silence_delay", lang))
        lbl_s1.setFixedWidth(175)
        h_sil.addWidget(lbl_s1)
        self.spin_silence = QSpinBox()
        self.spin_silence.setRange(3, 30)
        self.spin_silence.setSuffix(" s")
        self.spin_silence.setValue(int(self.controller.silence_timeout))
        self.spin_silence.setEnabled(self.controller.silence_auto_stop)
        self.spin_silence.valueChanged.connect(self._on_silence_changed)
        h_sil.addWidget(self.spin_silence)
        l_dev.addLayout(h_sil)
        l_audio.addWidget(self._create_clean_section(t("sec_mic", lang), l_dev))

        l_audio.addStretch()
        self.stack.addWidget(self._wrap_in_scroll(t_audio_content))

        # =============================================================
        # Page 3 : Interface | Style
        # =============================================================
        t_ui_content = QWidget()
        l_ui = QVBoxLayout(t_ui_content)
        l_ui.setSpacing(14)
        l_ui.setContentsMargins(4, 8, 4, 8)

        # Thème du configurateur
        l_th = QVBoxLayout()
        h_theme = QHBoxLayout()
        lbl_th = QLabel(t("lbl_palette", lang))
        lbl_th.setFixedWidth(175)
        h_theme.addWidget(lbl_th)
        self.combo_theme = NoScrollComboBox()
        self.combo_theme.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_theme.setMinimumContentsLength(20)
        self.combo_theme.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for k, v in THEME_PRESETS.items():
            display_name = t("theme_gold" if k == "gold" else "theme_dark", lang)
            self.combo_theme.addItem(display_name, k)
        idx_th = self.combo_theme.findData(self.controller.theme_mode)
        if idx_th >= 0:
            self.combo_theme.setCurrentIndex(idx_th)
        self.combo_theme.currentIndexChanged.connect(self._on_theme_preset_change)
        h_theme.addWidget(self.combo_theme)
        l_th.addLayout(h_theme)
        l_ui.addWidget(self._create_clean_section(t("sec_theme", lang), l_th))

        # Widget flottant
        l_w = QVBoxLayout()
        l_w.setSpacing(10)

        self.chk_show_hud = QCheckBox(t("chk_show_hud", lang))
        self.chk_show_hud.setChecked(self.controller.hud.isVisible())
        self.chk_show_hud.toggled.connect(self.controller.toggle_hud)
        l_w.addWidget(self.chk_show_hud)

        self.chk_key_minimal = QCheckBox(t("chk_key_minimal", lang))
        self.chk_key_minimal.setChecked(self.controller.key_display_minimal)
        self.chk_key_minimal.toggled.connect(self._on_key_minimal_toggle)
        l_w.addWidget(self.chk_key_minimal)

        h_sz = QHBoxLayout()
        lbl_w1 = QLabel(t("lbl_hud_size", lang))
        lbl_w1.setFixedWidth(175)
        h_sz.addWidget(lbl_w1)
        self.combo_size = NoScrollComboBox()
        self.combo_size.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_size.setMinimumContentsLength(20)
        self.combo_size.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for k, v in HUD_SIZES.items():
            self.combo_size.addItem(v, k)
        idx_size = self.combo_size.findData(self.controller.hud_size)
        if idx_size >= 0:
            self.combo_size.setCurrentIndex(idx_size)
        self.combo_size.currentIndexChanged.connect(self._on_size_change)
        h_sz.addWidget(self.combo_size)
        l_w.addLayout(h_sz)

        h_cr = QHBoxLayout()
        lbl_w2 = QLabel(t("lbl_hud_corners", lang))
        lbl_w2.setFixedWidth(175)
        h_cr.addWidget(lbl_w2)
        self.combo_corner = NoScrollComboBox()
        self.combo_corner.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_corner.setMinimumContentsLength(20)
        self.combo_corner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for k, v in CORNER_STYLES.items():
            self.combo_corner.addItem(v, k)
        idx_c = self.combo_corner.findData(self.controller.corner_style)
        if idx_c >= 0:
            self.combo_corner.setCurrentIndex(idx_c)
        self.combo_corner.currentIndexChanged.connect(self._on_corner_change)
        h_cr.addWidget(self.combo_corner)
        l_w.addLayout(h_cr)

        h_diode = QHBoxLayout()
        lbl_dio = QLabel(t("lbl_diode_style", lang))
        lbl_dio.setFixedWidth(175)
        h_diode.addWidget(lbl_dio)
        self.combo_diode = NoScrollComboBox()
        self.combo_diode.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_diode.setMinimumContentsLength(20)
        self.combo_diode.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for k, v in DIODE_STYLES.items():
            self.combo_diode.addItem(v, k)
        idx_dio = self.combo_diode.findData(self.controller.diode_style)
        if idx_dio >= 0:
            self.combo_diode.setCurrentIndex(idx_dio)
        self.combo_diode.currentIndexChanged.connect(self._on_diode_style_change)
        h_diode.addWidget(self.combo_diode)
        l_w.addLayout(h_diode)

        h_bg = QHBoxLayout()
        lbl_w3 = QLabel(t("lbl_hud_bg", lang))
        lbl_w3.setFixedWidth(175)
        h_bg.addWidget(lbl_w3)
        self.preview_bg_color = QFrame()
        self.preview_bg_color.setFixedSize(22, 22)
        self._update_bg_preview()
        self.btn_bg_color = QPushButton(t("btn_pick_color", lang))
        self.btn_bg_color.clicked.connect(self._pick_bg_color)
        self.btn_reset_bg = QPushButton(t("btn_reset", lang))
        self.btn_reset_bg.clicked.connect(self._reset_bg_color)
        h_bg.addWidget(self.preview_bg_color)
        h_bg.addWidget(self.btn_bg_color)
        h_bg.addWidget(self.btn_reset_bg)
        l_w.addLayout(h_bg)

        h_mic = QHBoxLayout()
        lbl_mic = QLabel(t("lbl_hud_mic", lang))
        lbl_mic.setFixedWidth(175)
        h_mic.addWidget(lbl_mic)
        self.preview_mic_color = QFrame()
        self.preview_mic_color.setFixedSize(22, 22)
        self._update_mic_preview()
        self.btn_mic_color = QPushButton(t("btn_pick_color", lang))
        self.btn_mic_color.clicked.connect(self._pick_mic_color)
        self.btn_reset_mic = QPushButton(t("btn_reset", lang))
        self.btn_reset_mic.clicked.connect(self._reset_mic_color)
        h_mic.addWidget(self.preview_mic_color)
        h_mic.addWidget(self.btn_mic_color)
        h_mic.addWidget(self.btn_reset_mic)
        l_w.addLayout(h_mic)

        self.chk_auto_contrast = QCheckBox(t("chk_auto_contrast", lang))
        self.chk_auto_contrast.setChecked(self.controller.auto_contrast)
        self.chk_auto_contrast.toggled.connect(self._on_auto_contrast_toggle)
        l_w.addWidget(self.chk_auto_contrast)

        h_op = QHBoxLayout()
        lbl_w4 = QLabel(t("lbl_hud_opacity", lang))
        lbl_w4.setFixedWidth(175)
        h_op.addWidget(lbl_w4)
        self.slider_opac = QSlider(Qt.Orientation.Horizontal)
        self.slider_opac.setRange(40, 100)
        self.slider_opac.setValue(int(self.controller.hud_opacity))
        self.lbl_opac = QLabel(f"{self.controller.hud_opacity}%")
        self.lbl_opac.setFixedWidth(36)
        self.slider_opac.valueChanged.connect(self._on_opacity_change)
        h_op.addWidget(self.slider_opac)
        h_op.addWidget(self.lbl_opac)
        l_w.addLayout(h_op)
        l_ui.addWidget(self._create_clean_section(t("sec_widget", lang), l_w))

        # Animation vocale
        l_wv = QVBoxLayout()
        l_wv.setSpacing(10)

        self.chk_wave_en = QCheckBox(t("chk_wave", lang))
        self.chk_wave_en.setChecked(self.controller.wave_enabled)
        self.chk_wave_en.toggled.connect(self._on_wave_enabled_toggle)
        l_wv.addWidget(self.chk_wave_en)

        h_ws = QHBoxLayout()
        lbl_v1 = QLabel(t("lbl_wave_style", lang))
        lbl_v1.setFixedWidth(175)
        h_ws.addWidget(lbl_v1)
        self.combo_wave_style = NoScrollComboBox()
        self.combo_wave_style.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_wave_style.setMinimumContentsLength(20)
        self.combo_wave_style.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for k, v in WAVE_STYLES.items():
            self.combo_wave_style.addItem(v, k)
        idx_ws = self.combo_wave_style.findData(self.controller.wave_style)
        if idx_ws >= 0:
            self.combo_wave_style.setCurrentIndex(idx_ws)
        self.combo_wave_style.currentIndexChanged.connect(self._on_wave_style_change)
        h_ws.addWidget(self.combo_wave_style)
        l_wv.addLayout(h_ws)

        h_wc = QHBoxLayout()
        lbl_v2 = QLabel(t("lbl_wave_color", lang))
        lbl_v2.setFixedWidth(175)
        h_wc.addWidget(lbl_v2)
        self.preview_wave_color = QFrame()
        self.preview_wave_color.setFixedSize(22, 22)
        self._update_wave_preview()
        self.btn_wave_color = QPushButton(t("btn_pick_color", lang))
        self.btn_wave_color.clicked.connect(self._pick_wave_color)
        self.btn_reset_wave = QPushButton(t("btn_reset", lang))
        self.btn_reset_wave.clicked.connect(self._reset_wave_color)
        h_wc.addWidget(self.preview_wave_color)
        h_wc.addWidget(self.btn_wave_color)
        h_wc.addWidget(self.btn_reset_wave)
        l_wv.addLayout(h_wc)
        l_ui.addWidget(self._create_clean_section(t("sec_wave", lang), l_wv))

        # Effets saisonniers
        l_seas = QVBoxLayout()
        l_seas.setSpacing(6)
        h_sm = QHBoxLayout()
        lbl_s = QLabel(t("lbl_seasonal", lang))
        lbl_s.setFixedWidth(175)
        h_sm.addWidget(lbl_s)
        self.combo_season = NoScrollComboBox()
        self.combo_season.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_season.setMinimumContentsLength(20)
        self.combo_season.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for k, v in SEASONAL_MODES.items():
            self.combo_season.addItem(v, k)
        idx_sm = self.combo_season.findData(self.controller.seasonal_mode)
        if idx_sm >= 0:
            self.combo_season.setCurrentIndex(idx_sm)
        self.combo_season.currentIndexChanged.connect(self._on_seasonal_change)
        h_sm.addWidget(self.combo_season)
        l_seas.addLayout(h_sm)

        lbl_seas_desc = QLabel(f"<i>{t('seasonal_dates', lang)}</i>")
        lbl_seas_desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
        lbl_seas_desc.setWordWrap(True)
        l_seas.addWidget(lbl_seas_desc)
        l_ui.addWidget(self._create_clean_section(t("sec_seasonal", lang), l_seas))

        # Notifications et sons
        l_notif = QVBoxLayout()
        l_notif.setSpacing(8)
        h_tst = QHBoxLayout()
        lbl_n1 = QLabel(t("lbl_toast_dur", lang))
        lbl_n1.setFixedWidth(175)
        h_tst.addWidget(lbl_n1)
        self.spin_toast = QSpinBox()
        self.spin_toast.setRange(1, 10)
        self.spin_toast.setSuffix(" s")
        self.spin_toast.setValue(int(self.controller.toast_duration))
        self.spin_toast.valueChanged.connect(self._on_toast_change)
        h_tst.addWidget(self.spin_toast)
        l_notif.addLayout(h_tst)

        self.chk_sound = QCheckBox(t("chk_sounds", lang))
        self.chk_sound.setChecked(self.controller.sound_feedback)
        self.chk_sound.toggled.connect(self._on_sound_toggled)
        l_notif.addWidget(self.chk_sound)

        h_vol = QHBoxLayout()
        lbl_vol = QLabel(t("lbl_sound_vol", lang))
        lbl_vol.setFixedWidth(175)
        h_vol.addWidget(lbl_vol)

        self.slider_sound_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_sound_vol.setRange(0, 100)
        self.slider_sound_vol.setValue(int(self.controller.sound_volume * 100))
        self.lbl_sound_vol = QLabel(f"{int(self.controller.sound_volume * 100)}%")
        self.lbl_sound_vol.setFixedWidth(38)
        self.slider_sound_vol.valueChanged.connect(self._on_sound_volume_changed)

        self.btn_test_sound = QPushButton(t("btn_test_sound", lang))
        self.btn_test_sound.setFixedWidth(65)
        self.btn_test_sound.clicked.connect(self._test_sound_volume)

        h_vol.addWidget(self.slider_sound_vol)
        h_vol.addWidget(self.lbl_sound_vol)
        h_vol.addWidget(self.btn_test_sound)
        l_notif.addLayout(h_vol)

        l_ui.addWidget(self._create_clean_section(t("sec_notifs", lang), l_notif))

        l_ui.addStretch()
        self.stack.addWidget(self._wrap_in_scroll(t_ui_content))

        # =============================================================
        # Page 4 : Langues | Traduction
        # =============================================================
        t_lang_content = QWidget()
        l_lang = QVBoxLayout(t_lang_content)
        l_lang.setSpacing(14)
        l_lang.setContentsMargins(4, 8, 4, 8)

        # Explications Whisper
        l_exp = QVBoxLayout()
        lbl_cap = QLabel(t("whisper_explanation", lang))
        lbl_cap.setStyleSheet("color: #CBD5E1; font-size: 12px; line-height: 1.5;")
        lbl_cap.setWordWrap(True)
        lbl_cap.setOpenExternalLinks(True)
        l_exp.addWidget(lbl_cap)
        l_lang.addWidget(self._create_clean_section(t("sec_whisper_capabilities", lang), l_exp))

        # Configuration des 5 Slots rapides
        l_slots = QVBoxLayout()
        l_slots.setSpacing(10)
        
        lbl_sd = QLabel(t("lbl_quick_lang_desc", lang))
        lbl_sd.setStyleSheet("color: #94A3B8; font-size: 11px; line-height: 1.5;")
        lbl_sd.setWordWrap(True)
        l_slots.addWidget(lbl_sd)

        grid_slots = QGridLayout()
        grid_slots.setSpacing(8)
        self.slot_edits = []
        for i in range(5):
            lbl = QLabel(f"Slot {i+1} :")
            lbl.setStyleSheet("color: #E2E8F0; font-weight: bold;")
            edit = QLineEdit()
            edit.setPlaceholderText("ex: FR")
            edit.setMaxLength(10) # AUTO ou codes ISO
            edit.setText(self.controller.quick_lang_slots[i])
            grid_slots.addWidget(lbl, i, 0)
            grid_slots.addWidget(edit, i, 1)
            self.slot_edits.append(edit)
        l_slots.addLayout(grid_slots)

        btn_apply = QPushButton(t("btn_apply_slots", lang))
        btn_apply.clicked.connect(self._apply_quick_slots)
        l_slots.addWidget(btn_apply)

        l_lang.addWidget(self._create_clean_section(t("sec_quick_lang", lang), l_slots))

        l_lang.addStretch()
        self.stack.addWidget(self._wrap_in_scroll(t_lang_content))

        # =============================================================
        # Page 5 : Historique
        # =============================================================
        t_hist_content = QWidget()
        l_hist = QVBoxLayout(t_hist_content)
        l_hist.setSpacing(10)
        l_hist.setContentsMargins(4, 8, 4, 8)

        # Nombre max d'entrées
        h_hist_cfg = QHBoxLayout()
        lbl_h1 = QLabel(t("lbl_hist_max", lang))
        lbl_h1.setFixedWidth(175)
        h_hist_cfg.addWidget(lbl_h1)
        self.spin_hist_max = QSpinBox()
        self.spin_hist_max.setRange(5, 50)
        self.spin_hist_max.setValue(self.controller.system.max_history)
        self.spin_hist_max.valueChanged.connect(self._on_hist_limit_changed)
        h_hist_cfg.addWidget(self.spin_hist_max)
        l_hist.addLayout(h_hist_cfg)

        # Liste de l'historique
        self.list_hist = QListWidget()
        self.list_hist.setWordWrap(True)
        self.list_hist.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.list_hist.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        l_hist.addWidget(self.list_hist)

        # Boutons d'action
        h_hist_btns = QHBoxLayout()
        btn_copy = QPushButton(t("btn_copy_sel", lang))
        btn_copy.clicked.connect(self._copy_history_item)
        btn_del = QPushButton(t("btn_del_sel", lang))
        btn_del.clicked.connect(self._delete_selected_history)
        btn_clear = QPushButton(t("btn_clear_all", lang))
        btn_clear.setStyleSheet("QPushButton { background-color: #241113; border: 1px solid #54171B; color: #FCA5A5; border-radius: 0px; } QPushButton:hover { background-color: #351418; }")
        btn_clear.clicked.connect(self._clear_all_history)

        h_hist_btns.addWidget(btn_copy)
        h_hist_btns.addWidget(btn_del)
        h_hist_btns.addWidget(btn_clear)
        l_hist.addLayout(h_hist_btns)

        self.stack.addWidget(t_hist_content)

        # =============================================================
        # Page 6 : Mentions Légales
        # =============================================================
        t_about_content = QWidget()
        l_about = QVBoxLayout(t_about_content)
        l_about.setSpacing(12)
        l_about.setContentsMargins(14, 14, 14, 14)

        lbl_legal = QLabel(t("legal_notice", lang))
        lbl_legal.setStyleSheet("color: #E2E8F0; font-size: 12px; line-height: 1.5; background: transparent;")
        lbl_legal.setWordWrap(True)
        l_about.addWidget(lbl_legal)
        l_about.addStretch()

        self.stack.addWidget(self._wrap_in_scroll(t_about_content))

        root.addWidget(self.stack)

        self._set_active_tab(0) # Activer premier onglet
        self.controller.signals.history_updated.connect(self.refresh_history)

    # --- Slots de réaction pour l'UI ---

    def _on_gain_changed(self, val: int):
        self.controller.audio_gain = val / 100.0
        self.lbl_gain_val.setText(f"{val}%")
        self.controller.save_config()

    def _on_sound_volume_changed(self, val: int):
        self.controller.sound_volume = val / 100.0
        self.lbl_sound_vol.setText(f"{val}%")
        self.controller.save_config()

    def _test_sound_volume(self):
        play_audio_feedback("success", True, self.controller.sound_volume)

    def _open_appdata_folder(self):
        folder = os.path.dirname(self.controller.config_filepath)
        if os.path.exists(folder):
            if sys.platform == "win32":
                os.startfile(folder)
            else:
                subprocess.Popen(["explorer", folder])

    def _update_bg_preview(self):
        self.preview_bg_color.setStyleSheet(f"background-color: {self.controller.hud_bg_color}; border: 1px solid #282832; border-radius: 0px;")

    def _update_wave_preview(self):
        self.preview_wave_color.setStyleSheet(f"background-color: {self.controller.wave_color}; border: 1px solid #282832; border-radius: 0px;")

    def _update_mic_preview(self):
        self.preview_mic_color.setStyleSheet(f"background-color: {self.controller.mic_color}; border: 1px solid #282832; border-radius: 0px;")

    def _on_theme_preset_change(self):
        preset_key = self.combo_theme.currentData()
        self.controller.theme_mode = preset_key
        # Forcer le rafraîchissement complet du style de la fenêtre
        self.apply_theme_style()
        
        # Mettre à jour la couleur du titre spécifiquement
        preset = THEME_PRESETS.get(preset_key) or THEME_PRESETS.get("gold", {})
        self.lbl_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {preset.get('title_color', '#B58E3F')};")
        self.controller.save_config()

    def _on_compute_device_change(self):
        self.controller.compute_device = self.combo_compute_device.currentData()
        self.controller.save_config()

    def _on_app_lang_change(self):
        new_lang = self.combo_app_lang.currentData()
        if new_lang != self.controller.app_lang:
            self.controller.app_lang = new_lang
            self.controller.save_config()
            # Redémarrer requis pour recharger locales
            self.controller.restart_app()

    def _on_key_minimal_toggle(self, checked: bool):
        self.controller.key_display_minimal = checked
        self.controller.save_config()
        self.controller.hud.apply_size_mode()

    def _on_diode_style_change(self):
        new_style = self.combo_diode.currentData()
        self.controller.diode_style = new_style
        self.controller.save_config()
        self.controller.hud.apply_size_mode()

    def _pick_bg_color(self):
        cur = QColor(self.controller.hud_bg_color)
        c = QColorDialog.getColor(cur, self, t("btn_pick_color", self.controller.app_lang))
        if c.isValid():
            self.controller.hud_bg_color = c.name()
            self._update_bg_preview()
            self.controller.save_config()
            self.controller.hud.apply_size_mode()

    def _reset_bg_color(self):
        self.controller.hud_bg_color = DEFAULT_BG_COLOR
        self.controller.hud_opacity = DEFAULT_HUD_OPACITY
        self.slider_opac.setValue(DEFAULT_HUD_OPACITY)
        self.lbl_opac.setText(f"{DEFAULT_HUD_OPACITY}%")
        self._update_bg_preview()
        self.controller.save_config()
        self.controller.hud.apply_size_mode()

    def _pick_wave_color(self):
        cur = QColor(self.controller.wave_color)
        c = QColorDialog.getColor(cur, self, t("btn_pick_color", self.controller.app_lang))
        if c.isValid():
            self.controller.wave_color = c.name()
            self._update_wave_preview()
            self.controller.save_config()
            self.controller.signals.hud_style_changed.emit()

    def _reset_wave_color(self):
        self.controller.wave_color = DEFAULT_WAVE_COLOR
        self._update_wave_preview()
        self.controller.save_config()
        self.controller.signals.hud_style_changed.emit()

    def _pick_mic_color(self):
        cur = QColor(self.controller.mic_color)
        c = QColorDialog.getColor(cur, self, t("btn_pick_color", self.controller.app_lang))
        if c.isValid():
            self.controller.mic_color = c.name()
            self._update_mic_preview()
            self.controller.save_config()
            self.controller.hud._update_graphics()

    def _reset_mic_color(self):
        self.controller.mic_color = DEFAULT_MIC_COLOR
        self._update_mic_preview()
        self.controller.save_config()
        self.controller.hud._update_graphics()

    def _on_seasonal_change(self):
        self.controller.seasonal_mode = self.combo_season.currentData()
        self.controller.save_config()
        self.controller.hud._refresh_particle_state()

    def _on_auto_contrast_toggle(self, checked: bool):
        self.controller.auto_contrast = checked
        self.controller.save_config()
        self.controller.hud.apply_size_mode()

    def _on_silence_toggle(self, checked: bool):
        self.controller.silence_auto_stop = checked
        self.spin_silence.setEnabled(checked)
        self.controller.save_config()

    def _on_ptt_toggle(self, checked: bool):
        self.controller.ptt_enabled = checked
        self.chk_ptt_dedicated.setEnabled(checked)
        self.w_ptt_key.setVisible(checked and self.controller.ptt_dedicated)
        self.controller.save_config()

    def _on_ptt_dedicated_toggle(self, checked: bool):
        self.controller.ptt_dedicated = checked
        self.w_ptt_key.setVisible(self.controller.ptt_enabled and checked)
        self.controller.save_config()

    def _on_autostart_toggled(self, checked: bool):
        ok = set_windows_autostart(checked)
        if not ok:
            # Revenir en arrière si échec registre
            self.chk_autostart.blockSignals(True)
            self.chk_autostart.setChecked(not checked)
            self.chk_autostart.blockSignals(False)
            QMessageBox.warning(self, "Erreur", "Impossible de modifier la clé de registre Windows.")

    def _on_size_change(self):
        new_size = self.combo_size.currentData()
        self.controller.set_hud_size(new_size)

    def _on_corner_change(self):
        self.controller.corner_style = self.combo_corner.currentData()
        self.controller.save_config()
        # Appliquer directement au widget
        self.controller.hud.update()

    def _on_opacity_change(self, val: int):
        self.controller.hud_opacity = val
        self.lbl_opac.setText(f"{val}%")
        self.controller.save_config()
        # Appliquer directement l'opacité au fond du widget
        self.controller.hud.update()

    def _on_wave_enabled_toggle(self, checked: bool):
        self.controller.wave_enabled = checked
        self.controller.save_config()
        self.controller.signals.hud_style_changed.emit()

    def _on_wave_style_change(self):
        self.controller.wave_style = self.combo_wave_style.currentData()
        self.controller.save_config()
        self.controller.signals.hud_style_changed.emit()

    def _on_toast_change(self, v: int):
        self.controller.toast_duration = float(v)
        self.controller.save_config()

    def _on_sound_toggled(self, checked: bool):
        self.controller.sound_feedback = checked
        self.controller.save_config()

    def refresh_audio_devices(self):
        self.combo_mic.blockSignals(True)
        self.combo_mic.clear()
        devices = get_input_devices()
        for idx, name in devices:
            self.combo_mic.addItem(name, idx)
        cur_idx = self.combo_mic.findData(self.controller.audio_device)
        self.combo_mic.setCurrentIndex(cur_idx if cur_idx >= 0 else 0)
        self.combo_mic.blockSignals(False)

    def _on_mic_change(self):
        self.controller.audio_device = self.combo_mic.currentData()
        self.controller.save_config()
        self.controller.signals.flash_message.emit("Microphone mis à jour", "#10B981", 2.0)

    def _on_silence_changed(self, v: int):
        self.controller.silence_timeout = float(v)
        self.controller.save_config()

    def _apply_quick_slots(self):
        # Récupérer et valider les codes saisis
        new_slots = []
        for edit in self.slot_edits:
            code = edit.text().strip().upper()
            if not code:
                # Slot vide autorisé, Whisper worker gérera (None/AUTO par défaut)
                new_slots.append("")
                continue
            
            # Valider contre la liste de référence (ou laisser libre si valide code ISO)
            is_valid = False
            for ref_code, _ in WHISPER_ALL_LANGUAGES:
                if code == ref_code:
                    is_valid = True
                    break
            
            if is_valid or len(code) <= 3: # Basique validation code ISO
                new_slots.append(code)
            else:
                QMessageBox.warning(self, "Code Invalide", f"Le code langue '{code}' semble incorrect.\nUtilisez 'AUTO', 'TRAD' ou un code ISO standard (FR, EN...).")
                edit.setFocus()
                return

        # Sauvegarder et rafraîchir le widget
        self.controller.quick_lang_slots = new_slots
        self.controller.save_config()
        self.controller.hud.refresh_quick_languages()
        self.controller.signals.flash_message.emit("Langues rapides appliquées", "#10B981", 2.0)

    def _on_hist_limit_changed(self, new_val: int):
        current_len = len(self.controller.system.history)
        if new_val < current_len:
            ret = QMessageBox.question(
                self,
                "Réduire l'historique",
                f"L'historique compte {current_len} entrées.\n"
                f"Réduire la limite à {new_val} supprimera les plus anciennes.\n\nConfirmer ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if ret != QMessageBox.StandardButton.Yes:
                self.spin_hist_max.blockSignals(True)
                self.spin_hist_max.setValue(self.controller.system.max_history)
                self.spin_hist_max.blockSignals(False)
                return

        self.controller.system.set_max_history(new_val)
        self.controller.save_config()
        self.refresh_history()

    def _start_capture(self, target: str):
        btn = self.btn_capture if target == "main" else self.btn_capture_ptt
        btn.setText("Appuyez sur une touche...")
        btn.setStyleSheet("background-color: #B58E3F; color: #0A0A0E; font-weight: bold; border: 1px solid #B58E3F; border-radius: 0px;")
        self.controller.system.capture_next_key(target, lambda name: self._on_captured(target, name))

    def _on_captured(self, target: str, friendly_name: str):
        btn = self.btn_capture if target == "main" else self.btn_capture_ptt
        btn.setText(friendly_name)
        btn.setStyleSheet("")
        if target == "main":
            self.controller.signals.key_reassigned.emit(friendly_name)
        self.controller.save_config()

    def _on_model_change(self):
        self.controller.selected_model = self.combo_model.currentData()
        self.controller.save_config()
        # Message d'avertissement (le modèle changera au prochain redémarrage ou transcription si dynamique)
        self.controller.signals.flash_message.emit("Modèle mis à jour", "#B58E3F", 2.0)

    def refresh_history(self):
        self.list_hist.clear()
        # Inverser pour voir le plus récent en haut
        for i, item in enumerate(self.controller.system.get_history()):
            num = i + 1
            self.list_hist.addItem(f"#{num} • [{item['time']}]\n{item['text']}")

    def _copy_history_item(self):
        it = self.list_hist.currentItem()
        if it:
            import pyperclip
            # Extraire juste le texte après le premier saut de ligne
            pyperclip.copy(it.text().split("\n", 1)[-1])

    def _delete_selected_history(self):
        row = self.list_hist.currentRow()
        if row >= 0:
            self.controller.system.delete_history_entry(row)
            self.controller.save_config()
            self.refresh_history()

    def _clear_all_history(self):
        if not self.controller.system.history:
            return
        ret = QMessageBox.question(
            self,
            "Effacer l'historique",
            "Voulez-vous supprimer définitivement tout l'historique ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            self.controller.system.clear_all_history()
            self.controller.save_config()
            self.refresh_history()


# ---------------------------------------------------------------------------
# Contrôleur Principal
# ---------------------------------------------------------------------------
class ApplicationController:
    def __init__(self):
        self.signals = AppSignals()
        self.state = "READY"
        self._lock = threading.RLock()
        self.engine: Optional[AudioEngine] = None
        self.target_hwnd = None
        self.last_transcription = ""

        # Gestion PTT / Hold
        self.main_key_down_time = 0.0
        self.recording_started_by_hold = False

        # Chargement Configuration
        self.config_filepath = get_storage_path()
        cfg = self.load_config()

        # Raccourcis
        hotkey = cfg.get("hotkey", "f8")
        ptt_hotkey = cfg.get("ptt_hotkey", "f7")
        self.ptt_enabled = bool(cfg.get("ptt_enabled", True))
        self.ptt_dedicated = bool(cfg.get("ptt_dedicated", False))

        # Moteur & Langue
        max_hist = cfg.get("max_history", 15)
        saved_history = cfg.get("history_items", [])
        self.selected_model = cfg.get("model", "large-v3-turbo")
        self.compute_device = cfg.get("compute_device", "cuda")
        self.app_lang = cfg.get("app_lang", "fr") # Langue UI
        
        # Slots Langues Rapides (Pilule ComboBox)
        self.quick_lang_slots = cfg.get("quick_lang_slots", ["AUTO", "FR", "EN", "DE", "ES"])
        # Langue cible active actuellement (stockée par code ISO, ex: FR)
        self.target_lang = cfg.get("target_lang", "AUTO")

        # Style UI
        self.theme_mode = cfg.get("theme_mode", "gold")
        self.hud_size = cfg.get("hud_size", "standard")
        self.corner_style = cfg.get("corner_style", "pill")
        self.hud_opacity = int(cfg.get("hud_opacity", DEFAULT_HUD_OPACITY))
        self.hud_bg_color = cfg.get("hud_bg_color", DEFAULT_BG_COLOR)
        self.mic_color = cfg.get("mic_color", DEFAULT_MIC_COLOR)
        self.auto_contrast = bool(cfg.get("auto_contrast", True))
        self.key_display_minimal = bool(cfg.get("key_display_minimal", False))
        self.audio_gain = float(cfg.get("audio_gain", 1.0))
        self.sound_volume = float(cfg.get("sound_volume", 1.0))
        self.wave_style = cfg.get("wave_style", DEFAULT_WAVE_STYLE)
        self.wave_color = cfg.get("wave_color", DEFAULT_WAVE_COLOR)
        self.wave_enabled = bool(cfg.get("wave_enabled", True))
        self.diode_style = cfg.get("diode_style", DEFAULT_DIODE_STYLE)
        self.seasonal_mode = cfg.get("seasonal_mode", "auto")
        self.silence_timeout = float(cfg.get("silence_timeout", 5.0))
        self.silence_auto_stop = bool(cfg.get("silence_auto_stop", True))
        self.sound_feedback = bool(cfg.get("sound_feedback", True))
        self.toast_duration = float(cfg.get("toast_duration", 3.0))
        self.audio_device = int(cfg.get("audio_device", -1)) # -1 = par défaut système
        self.hud_visible = bool(cfg.get("hud_visible", True))

        # Initialisation composants
        self.system = SystemHandler(
            default_hotkey=hotkey,
            ptt_hotkey=ptt_hotkey,
            on_hotkey_down=self._on_main_key_down,
            on_hotkey_up=self._on_main_key_up,
            on_ptt_down=self._on_dedicated_ptt_down,
            on_ptt_up=self._on_dedicated_ptt_up,
            max_history=max_hist
        )
        if isinstance(saved_history, list):
            # Charger historique, s'assurer de ne pas dépasser limite
            self.system.history = saved_history[:max_hist]

        self.hud = FloatingHUD(self.signals, self)
        self.settings_window = SettingsDialog(self)

        # Restaurer position HUD
        if "pos_x" in cfg and "pos_y" in cfg:
            self.hud.move(int(cfg["pos_x"]), int(cfg["pos_y"]))
        else:
            self.reset_hud_position()

        self._init_tray()
        self.system.start_hotkey_listener()

        if self.hud_visible:
            self.hud.show()
        else:
            self.hud.hide()

    def set_hud_size(self, size_mode: str):
        """Change la taille du HUD et sauvegarde."""
        self.hud_size = size_mode
        self.save_config()
        self.signals.hud_style_changed.emit()
        # Mettre à jour la combo dans les paramètres si ouverte
        if hasattr(self, 'settings_window') and hasattr(self.settings_window, 'combo_size'):
            idx = self.settings_window.combo_size.findData(size_mode)
            if idx >= 0:
                self.settings_window.combo_size.blockSignals(True)
                self.settings_window.combo_size.setCurrentIndex(idx)
                self.settings_window.combo_size.blockSignals(False)

    def _is_ptt_currently_active(self) -> bool:
        """Vérifie si une touche PTT est physiquement maintenue."""
        if self.ptt_enabled and self.ptt_dedicated:
            return self.system.is_ptt_physically_down()
        if self.ptt_enabled and not self.ptt_dedicated:
            return self.system.is_hotkey_physically_down()
        # Si PTT désactivé mais enregistrement lancé par maintien hotkey
        if self.recording_started_by_hold and self.system.is_hotkey_physically_down():
            return True
        return False

    # --- Gestion des touches (Logique complexe Push-to-talk / Bascule) ---

    def _on_main_key_down(self):
        """Action sur appui touche principale."""
        try:
            self.main_key_down_time = time.time()
            should_stop = False
            should_start = False

            with self._lock:
                if self.state == "PROCESSING":
                    return # Ignorer si occupé
                
                if self.state == "RECORDING":
                    # Mode Bascule : on appuie pour arrêter
                    self.recording_started_by_hold = False
                    should_stop = True
                elif self.state == "READY":
                    # Potentiel début d'enregistrement ( PT T ou Maintien)
                    self.recording_started_by_hold = True
                    should_start = True

            if should_stop:
                self._stop_and_process()
            elif should_start:
                self._start_recording_internal()
        except Exception as e:
            print(f"[Hotkey Down Error] {e}")

    def _on_main_key_up(self):
        """Action sur relâchement touche principale."""
        try:
            held_duration = time.time() - self.main_key_down_time
            should_stop = False

            with self._lock:
                if self.state == "RECORDING" and self.recording_started_by_hold:
                    # L'enregistrement a été lancé par ce "down"
                    if self.ptt_enabled and not self.ptt_dedicated:
                        # Mode PTT sur touche unique : relâchement = arrêt si maintenu assez longtemps
                        if held_duration >= 0.35: # Seuil pour différencier clic de maintien
                            should_stop = True
                    # Dans tous les cas, ce n'est plus considéré comme un maintien
                    self.recording_started_by_hold = False

            if should_stop:
                self._stop_and_process()
        except Exception as e:
            print(f"[Hotkey Up Error] {e}")

    def _on_dedicated_ptt_down(self):
        """Action sur appui touche PTT dédiée."""
        try:
            if not self.ptt_enabled or not self.ptt_dedicated:
                return
            
            should_start = False
            with self._lock:
                if self.state == "READY":
                    should_start = True
            
            if should_start:
                self._start_recording_internal()
        except Exception as e:
            print(f"[Dedicated PTT Down Error] {e}")

    def _on_dedicated_ptt_up(self):
        """Action sur relâchement touche PTT dédiée."""
        try:
            if not self.ptt_enabled or not self.ptt_dedicated:
                return
                
            should_stop = False
            with self._lock:
                if self.state == "RECORDING":
                    should_stop = True
            
            if should_stop:
                self._stop_and_process()
        except Exception as e:
            print(f"[Dedicated PTT Up Error] {e}")

    # --- Zone de Notification (Tray) ---

    def _init_tray(self):
        self.tray = QSystemTrayIcon(load_app_icon())
        self.tray.setToolTip(APP_NAME)

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background-color: #111115; color: #E2E8F0; border: 1px solid #282832; padding: 4px; border-radius: 0px; }
            QMenu::item { padding: 6px 18px; border-radius: 0px; }
            QMenu::item:selected { background-color: #1E1E26; }
        """)

        lang = self.app_lang
        a_toggle = menu.addAction(t("menu_hide", lang))
        a_toggle.triggered.connect(lambda: self.toggle_hud(not self.hud.isVisible()))

        a_settings = menu.addAction(t("menu_settings", lang))
        a_settings.triggered.connect(self.open_settings)

        a_recenter = menu.addAction(t("menu_recenter", lang))
        a_recenter.triggered.connect(self.reset_hud_position)

        a_restart = menu.addAction(t("menu_restart", lang))
        a_restart.triggered.connect(self.restart_app)

        menu.addSeparator()
        a_quit = menu.addAction(t("menu_quit", lang))
        a_quit.triggered.connect(QApplication.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_settings()

    # --- Actions Globales ---

    def restart_app(self):
        """Sauvegarde et redémarre proprement l'application."""
        if self.engine and self.engine.is_recording:
            try:
                self.engine.stop()
            except Exception:
                pass
        self.system.stop_hotkey_listener()
        self.tray.hide()
        self.save_config()

        # Relancer processus
        subprocess.Popen([sys.executable] + sys.argv)
        QApplication.quit()
        sys.exit(0)

    def copy_last_transcription(self):
        """Copie le dernier texte ou la dernière entrée d'historique."""
        if self.last_transcription:
            import pyperclip
            pyperclip.copy(self.last_transcription)
            self.signals.flash_message.emit(t("toast_copied", self.app_lang), "#10B981", 1.8)
        else:
            hist = self.system.get_history()
            if hist:
                import pyperclip
                self.last_transcription = hist[0]['text']
                pyperclip.copy(self.last_transcription)
                self.signals.flash_message.emit(t("toast_copied", self.app_lang), "#10B981", 1.8)
            else:
                self.signals.flash_message.emit(t("toast_empty", self.app_lang), "#B58E3F", 1.8)

    # --- Sauvegarde / Chargement ---

    def load_config(self) -> dict:
        if os.path.exists(self.config_filepath):
            try:
                with open(self.config_filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        """Sauvegarde l'état actuel dans config.json."""
        pos = self.hud.pos()
        data = {
            "hotkey": self.system.hotkey_key,
            "ptt_hotkey": self.system.ptt_key,
            "ptt_enabled": self.ptt_enabled,
            "ptt_dedicated": self.ptt_dedicated,
            "max_history": self.system.max_history,
            "history_items": self.system.get_history(), # Liste d'objets dict
            "model": self.selected_model,
            "compute_device": self.compute_device,
            "app_lang": self.app_lang,
            "quick_lang_slots": self.quick_lang_slots,
            "target_lang": self.target_lang,
            "theme_mode": self.theme_mode,
            "hud_size": self.hud_size,
            "corner_style": self.corner_style,
            "hud_opacity": self.hud_opacity,
            "hud_bg_color": self.hud_bg_color,
            "mic_color": self.mic_color,
            "auto_contrast": self.auto_contrast,
            "key_display_minimal": self.key_display_minimal,
            "audio_gain": self.audio_gain,
            "sound_volume": self.sound_volume,
            "wave_style": self.wave_style,
            "wave_color": self.wave_color,
            "wave_enabled": self.wave_enabled,
            "diode_style": self.diode_style,
            "seasonal_mode": self.seasonal_mode,
            "silence_timeout": self.silence_timeout,
            "silence_auto_stop": self.silence_auto_stop,
            "sound_feedback": self.sound_feedback,
            "toast_duration": self.toast_duration,
            "audio_device": self.audio_device,
            "hud_visible": self.hud.isVisible(),
            "pos_x": pos.x(),
            "pos_y": pos.y()
        }
        try:
            with open(self.config_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def reset_hud_position(self):
        """Replace la barre en haut au centre."""
        screen = QApplication.primaryScreen().geometry()
        self.hud.move((screen.width() - self.hud.width()) // 2, 35)
        self.save_config()

    def toggle_hud(self, visible: bool):
        if visible:
            self.hud.show()
        else:
            self.hud.hide()
        # Mettre à jour checkbox si ouverte
        if hasattr(self, 'settings_window') and hasattr(self.settings_window, 'chk_show_hud'):
            self.settings_window.chk_show_hud.blockSignals(True)
            self.settings_window.chk_show_hud.setChecked(visible)
            self.settings_window.chk_show_hud.blockSignals(False)
        self.save_config()

    def open_settings(self):
        """Ouvre ou active la fenêtre des paramètres."""
        self.settings_window.refresh_history()
        self.settings_window.refresh_audio_devices()
        # Sync état checkbox HUD avant affichage
        if hasattr(self.settings_window, 'chk_show_hud'):
            self.settings_window.chk_show_hud.blockSignals(True)
            self.settings_window.chk_show_hud.setChecked(self.hud.isVisible())
            self.settings_window.chk_show_hud.blockSignals(False)
        self.settings_window.show()
        self.settings_window.activateWindow()

    # --- Logique d'Enregistrement et Transcription ---

    def toggle_recording(self):
        """Bascule manuel (PTT désactivé) ou arrêt forcé."""
        should_stop = False
        should_start = False
        with self._lock:
            if self.state == "PROCESSING":
                return
            if self.state == "READY":
                should_start = True
            elif self.state == "RECORDING":
                should_stop = True

        if should_start:
            self._start_recording_internal()
        elif should_stop:
            self._stop_and_process()

    def _start_recording_internal(self):
        """Lance l'acquisition audio."""
        with self._lock:
            if self.state != "READY": return
            
            # Capturer HWND fenêtre active sous Windows pour focus après
            if sys.platform == "win32":
                self.target_hwnd = ctypes.windll.user32.GetForegroundWindow()

            self.state = "RECORDING"
            self.signals.state_changed.emit("RECORDING", "")
            play_audio_feedback("start", self.sound_feedback, self.sound_volume)

            # Initialiser moteur audio
            self.engine = AudioEngine(
                sample_rate=16000,
                silence_timeout=self.silence_timeout,
                silence_auto_stop=self.silence_auto_stop,
                is_ptt_active_callback=self._is_ptt_currently_active,
                on_silence_stop=self._on_auto_silence,
                on_audio_level=self.signals.audio_level.emit,
                device=self.audio_device if self.audio_device != -1 else None
            )
            self.engine.start()

    def _on_auto_silence(self):
        """callback moteur : silence détecté."""
        # Sécurité : ne pas couper si PTT maintenu
        if self._is_ptt_currently_active():
            return
        self._stop_and_process()

    def _stop_and_process(self):
        """Arrête l'acquisition et lance le worker de transcription."""
        with self._lock:
            if self.state != "RECORDING": return
            self.state = "PROCESSING"
            self.signals.state_changed.emit("PROCESSING", t("state_processing", self.app_lang))
            play_audio_feedback("stop", self.sound_feedback, self.sound_volume)

            if self.engine is not None:
                audio_data = self.engine.stop()
            else:
                audio_data = np.array([], dtype=np.float32)

        # Lancer transcription dans thread séparé
        threading.Thread(target=self._transcribe_worker, args=(audio_data,), daemon=True).start()

    def _transcribe_worker(self, audio_data):
        """Thread de transcription : appelle whisper_worker.exe."""
        temp_audio = "temp_audio.npy"
        temp_result = "temp_result.json"
        try:
            # Vérification basique données
            if len(audio_data) < 8000: # < 0.5s à 16kHz
                play_audio_feedback("error", self.sound_feedback, self.sound_volume)
                self.signals.trigger_error.emit()
                self.signals.flash_message.emit(t("toast_short", self.app_lang), "#B58E3F", 1.8 if self.hud_size == "nano" else 2.2)
                return

            # Appliquer Gain
            if self.audio_gain != 1.0:
                audio_data = np.clip(audio_data * self.audio_gain, -1.0, 1.0)

            # Sauvegarder audio temporaire
            np.save(temp_audio, audio_data)

            # Préparer environnement worker
            sub_env = os.environ.copy()
            sub_env["PYTHONIOENCODING"] = "utf-8"

            # Lire langue cible combo HUD
            current_target_lang = self.target_lang.strip().upper() if self.target_lang else "AUTO"

            # Construction commande (frozen ou script)
            if getattr(sys, "frozen", False):
                worker_bin = os.path.join(os.path.dirname(sys.executable), "whisper_worker.exe")
                cmd = [worker_bin, self.selected_model, temp_audio, self.compute_device, current_target_lang]
            else:
                cmd = [sys.executable, "whisper_worker.py", self.selected_model, temp_audio, self.compute_device, current_target_lang]

            # Exécuter worker
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=sub_env
            )

            # Lire résultat JSON
            text = ""
            duration = len(audio_data) / 16000.0
            elapsed = 0.0

            if os.path.exists(temp_result):
                try:
                    with open(temp_result, "r", encoding="utf-8") as f:
                        res = json.load(f)
                        text = res.get("text", "")
                        elapsed = res.get("elapsed", 0.0)
                        duration = res.get("duration", duration)
                        if "error" in res:
                            print(f"[Whisper Worker Error] {res['error']}")
                except Exception:
                    pass

            # Traitement résultat
            if text:
                self.last_transcription = text
                
                # Restaurer focus si possible
                if sys.platform == "win32" and self.target_hwnd:
                    if ctypes.windll.user32.IsWindow(self.target_hwnd):
                        ctypes.windll.user32.SetForegroundWindow(self.target_hwnd)
                        time.sleep(0.06) # Petit délai pour Windows

                # Injecter texte
                self.system.paste_text(text)
                self.signals.history_updated.emit()
                play_audio_feedback("success", self.sound_feedback, self.sound_volume)

                # Toast Info
                if self.hud_size in ("standard", "mini"):
                    toast_msg = f"{duration:.1f}s en {elapsed:.2f}s"
                else:
                    toast_msg = f"✓ {elapsed:.1f}s"

                self.signals.flash_message.emit(
                    toast_msg,
                    "#10B981",
                    self.toast_duration
                )
            else:
                # Vide ou erreur VAD
                play_audio_feedback("error", self.sound_feedback, self.sound_volume)
                self.signals.trigger_error.emit()
                self.signals.flash_message.emit(t("toast_inaudible", self.app_lang), "#8E94A5", 1.8)

        except Exception as e:
            play_audio_feedback("error", self.sound_feedback, self.sound_volume)
            self.signals.trigger_error.emit()
            self.signals.flash_message.emit(f"Erreur : {str(e)[:20]}", "#EF4444", 2.2)
        finally:
            # Nettoyage fichiers temporaires
            for p in (temp_audio, temp_result):
                if os.path.exists(p):
                    try: os.remove(p)
                    except Exception: pass

            # Retour état prêt
            with self._lock:
                self.state = "READY"
                self.signals.state_changed.emit("READY", "")
            self.save_config()


if __name__ == "__main__":
    # Point d'entrée principal de l'application
    app = QApplication(sys.argv)
    
    # Configuration globale Qt
    app.setWindowIcon(load_app_icon())
    app.setQuitOnLastWindowClosed(False) # Garder tray actif si settings fermés

    # Lancer contrôleur
    controller = ApplicationController()
    
    # Boucle événementielle
    sys.exit(app.exec())