# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_dynamic_libs

block_cipher = None

ct2_bins = collect_dynamic_libs('ctranslate2')
ort_bins = collect_dynamic_libs('onnxruntime')
sd_bins = collect_dynamic_libs('sounddevice')

cuda_bins = []
try:
    cuda_bins += collect_dynamic_libs('nvidia.cublas')
    cuda_bins += collect_dynamic_libs('nvidia.cudnn')
except Exception:
    pass

datas = [
    ('sounds', 'sounds'),
    ('locales.py', '.')
]

# 1. Moteur Whisper isole
a_worker = Analysis(
    ['whisper_worker.py'],
    pathex=[],
    binaries=ct2_bins + ort_bins + cuda_bins,
    datas=[],
    hiddenimports=['faster_whisper', 'ctranslate2', 'onnxruntime', 'numpy'],
    excludes=['PySide6', 'matplotlib', 'tkinter'],
    cipher=block_cipher,
    noarchive=False,
)
pyz_worker = PYZ(a_worker.pure, a_worker.zipped_data, cipher=block_cipher)
exe_worker = EXE(
    pyz_worker,
    a_worker.scripts,
    [],
    exclude_binaries=True,
    name='whisper_worker',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

# 2. Interface principale
a_app = Analysis(
    ['app.py'],
    pathex=[],
    binaries=sd_bins,
    datas=datas,
    hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32', 'pyperclip'],
    excludes=['tkinter'],
    cipher=block_cipher,
    noarchive=False,
)
pyz_app = PYZ(a_app.pure, a_app.zipped_data, cipher=block_cipher)
exe_app = EXE(
    pyz_app,
    a_app.scripts,
    [],
    exclude_binaries=True,
    name='CONTINGENCE_Wisper',
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon='icon.ico' if os.path.exists('icon.ico') else None
)

# 3. Assemblage
coll = COLLECT(
    exe_app,
    a_app.binaries,
    a_app.zipfiles,
    a_app.datas,
    exe_worker,
    a_worker.binaries,
    a_worker.zipfiles,
    a_worker.datas,
    strip=False,
    upx=False,
    name='CONTINGENCE_Wisper'
)