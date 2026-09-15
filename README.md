<div align="center">

```text
 ██████╗ ██████╗ ███╗   ██╗████████╗██╗███╗   ██╗ ██████╗ ███████╗███╗   ██╗ ██████╗███████╗ 
██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔════╝ 
██║     ██║   ██║██╔██╗ ██║   ██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██╔██╗ ██║██║     █████╗   
██║     ██║   ██║██║╚██╗██║   ██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║╚██╗██║██║     ██╔══╝   
╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║██║ ╚████║╚██████╔╝███████╗██║ ╚████║╚██████╗███████╗ 
 ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚══════╝ 
                                                                                             
                                               ██╗    ██╗██╗███████╗██████╗ ███████╗██████╗ 
                                               ██║    ██║██║██╔════╝██╔══██╗██╔════╝██╔══██╗
                                               ██║ █╗ ██║██║███████╗██████╔╝█████╗  ██████╔╝
                                               ██║███╗██║██║╚════██║██╔═══╝ ██╔══╝  ██╔══██╗
                                               ╚███╔███╔╝██║███████║██║     ███████╗██║  ██║
                                                     ╚══╝╚══╝ ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝            
```

# CONTINGENCE | Wisper

**Suite de dictée vocale et de traduction locale instantanée accélérée par GPU NVIDIA RTX.**

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt-green?style=for-the-badge&logo=qt&logoColor=white)](https://www.qt.io/)
[![Faster-Whisper](https://img.shields.io/badge/Engine-Faster--Whisper-orange?style=for-the-badge)](https://github.com/SYSTRAN/faster-whisper)
[![CUDA](https://img.shields.io/badge/Acceleration-NVIDIA%20CUDA%2012-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-toolkit)
[![License](https://img.shields.io/badge/License-Attribution%20Non--Commercial-red?style=for-the-badge)](LICENSE)

</div>

---

## Vue d'ensemble

**CONTINGENCE | Wisper** est une solution de transcription et traduction vocale de qualité studio conçue pour Windows. Elle transforme instantanément votre voix en texte directement injecté au niveau du curseur dans n'importe quelle application (navigateur, traitement de texte, terminal, messageries).

Le traitement est **100 % local** : aucun fichier audio ne transite par des serveurs tiers ou des API cloud, garantissant une confidentialité totale (RGPD native).

---

## Points Clés

- **Inférence Locale Ultra-Rapide :** Propulsé par `Faster-Whisper` (CTranslate2) avec support FP16 CUDA natif et fallback CPU automatique (int8).
- **Architecture Asynchrone Isolée :** Séparation étanche entre l'interface utilisateur (`PySide6`) et le moteur d'inférence (`whisper_worker.py`).
- **HUD Flottant Sans Bords :** Widget compact au design géométrique sobre, repositionnable à l'écran, avec visualiseur d'ondes vocales réactif en temps réel.
- **Raccourcis & Push-to-Talk :** Mode bascule classique (on/off) et mode Push-to-Talk (maintien de touche) avec réassignation des raccourcis à la volée.
- **Gestion Avancée des Langues :**
  - **Mode AUTO :** Retranscription native-à-native sans altération.
  - **Mode Verrouillé (FR, EN, ES, DE...) :** Force Whisper à sortir dans la langue sélectionnée (traduction automatique vers l'anglais si configuré sur `EN`).
  - **5 Slots configurables :** Personnalisation des raccourcis de langue directement sur le widget.
- **Sound Design Premium :** Retours sonores discrets générés par synthèse FM avec enveloppes douces (dossier `sounds/`).

---

## Architecture du Projet

```text
ContingenceWisper/
│
├── app.py               # Interface graphique PySide6, HUD flottant & panneau de configuration
├── whisper_worker.py    # Moteur d'inférence Faster-Whisper exécuté en sous-processus isolé
├── audio_engine.py      # Capture audio microphone (sounddevice) et détection de silence VAD
├── system_handler.py    # Écoute système des touches globales (pynput) et simulation d'écriture
├── locales.py           # Dictionnaire bilingue (Français / Anglais)
├── generate_sounds.py   # Script de génération synthétique des retours sonores WAV
├── build.spec           # Fichier de configuration PyInstaller multi-binaire
├── requirements.txt     # Dépendances Python requises
├── LICENSE              # Licence d'utilisation
└── sounds/              # Retours sonores WAV générés (start, stop, success, error)
```

---
## Instalation (.exe)

Pour windows !
Télécharger l’installateur de l'app en v1.0.0 (a droit sur github) :

---
## Installation & Lancement depuis les Sources

### 1. Prérequis
- Windows 10 / 11 (64-bit)
- Python 3.10, 3.11 ou 3.12
- Carte graphique NVIDIA RTX / GTX recommandée (fonctionne également sur CPU)

### 2. Cloner le Dépôt
```bash
git clone [https://github.com/](https://github.com/)<VotrePseudo>/Contingence-Wisper.git
cd Contingence-Wisper
```

### 3. Environnement Virtuel & Dépendances
```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Générer les Retours Sonores (première utilisation)
```powershell
python generate_sounds.py
```

### 5. Lancer l'Application
```powershell
python app.py
```

---


## Crédits & Propriété Intellectuelle

- **Auteur & Concepteur Principal :** Reymann Dylan
- **Assistance Architecture Logicielle :** Google Gemini (Gemini 3.8)
- **Modèles & Moteurs :**
  - [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) (Systran)
  - [OpenAI Whisper](https://github.com/openai/whisper) (OpenAI)
  - [PySide6 / Qt](https://wiki.qt.io/Qt_for_Python) (The Qt Company)
