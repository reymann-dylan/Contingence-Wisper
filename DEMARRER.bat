@echo off
title CONTINGENCE - Wisper
cd /d "%~dp0"

:: 1. Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR : Python introuvable !
    pause
    exit /b
)

:: 2. Verifier l'environnement virtuel
if not exist ".venv" (
    echo Creation du .venv...
    python -m venv .venv
)

:: 3. Activation et installation silencieuse des dependances manquantes
call .venv\Scripts\activate.bat >nul 2>&1
python -m pip install --upgrade pip >nul 2>&1
python -m pip install faster-whisper PySide6 sounddevice numpy pynput pyperclip nvidia-cublas-cu12 nvidia-cudnn-cu12 >nul 2>&1

:: 4. Generer les sons WAV s'ils n'existent pas
if not exist "sounds\success.wav" (
    if exist "generate_sounds.py" (
        python generate_sounds.py >nul 2>&1
    )
)

:: 5. Lancement de l'application en mode fenêtré invisible (sans console)
start /B pythonw app.py
exit