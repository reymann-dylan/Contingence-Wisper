# locales.py
TRANSLATIONS = {
    "fr": {
        "app_subtitle": "Dictée Vocale Locale IA | Accélération GPU RTX",
        "tab_sys": "Système | Moteur",
        "tab_audio": "Raccourcis | Micro",
        "tab_style": "Interface | Style",
        "tab_lang": "Langues | Fonctionnement",
        "tab_hist": "Historique",
        "tab_about": "Mentions Légales",
        
        "sec_app_lang": "Langue du logiciel (Interface Language)",
        "lbl_app_lang": "Langue d'affichage :",
        "sec_boot": "Démarrage Automatique",
        "autostart_label": "Lancer automatiquement au démarrage de Windows",
        "sec_device": "Accélération GPU/CPU",
        "device_gpu": "Carte Graphique Dédiée (NVIDIA CUDA RTX - Recommandé)",
        "device_cpu": "Processeur Central (CPU - Compatibilité universelle, plus lent)",
        "sec_specs": "Spécifications & Stockage",
        "sec_model": "Modèle Whisper",
        "sec_maint": "Maintenance & Position",
        "btn_recenter": "Recentrer le widget",
        "btn_restart": "Redémarrer l'application",
        "btn_open_storage": "Ouvrir l'emplacement des données (%APPDATA%)",

        "sec_shortcuts": "Raccourcis & Push-to-talk",
        "lbl_main_hotkey": "Touche de dictée (Bascule) :",
        "chk_ptt": "Activer le mode maintien (Push-to-talk)",
        "chk_ptt_dedicated": "Utiliser une touche distincte pour le Push-to-talk",
        "lbl_ptt_dedicated": "Touche dédiée Push-to-talk :",
        "ptt_hint": "En Push-to-talk : le silence n'interrompt jamais l'enregistrement tant que la touche est maintenue.",
        "sec_mic": "Microphone & Détection de Silence",
        "lbl_audio_gain": "Gain d'entrée microphone :",
        "chk_silence": "Activer la coupure auto. après un silence (mode bascule)",
        "lbl_silence_delay": "Délai de silence avant coupure :",

        "sec_theme": "Thème de l'application",
        "lbl_palette": "Palette du configurateur :",
        "theme_gold": "Noir sombre or contingence",
        "theme_dark": "Carbone & Graphite (Sobre)",
        "sec_widget": "Widget Flottant",
        "chk_show_hud": "Afficher le widget flottant sur l'écran",
        "chk_key_minimal": "Mode minimaliste pour l'affichage de la touche (ex. Prêt | F8)",
        "lbl_hud_size": "Format de la barre :",
        "lbl_hud_corners": "Coins de la barre :",
        "lbl_diode_style": "Style de la diode d'état :",
        "lbl_hud_bg": "Fond personnalisé :",
        "lbl_hud_mic": "Couleur du micro :",
        "chk_auto_contrast": "Adapter automatiquement le contraste (texte & boutons)",
        "lbl_hud_opacity": "Opacité du fond :",
        "btn_pick_color": "Choisir la couleur...",
        "btn_reset": "Réinitialiser",
        "sec_wave": "Animation Vocale",
        "chk_wave": "Activer l'animation vocale réactive",
        "lbl_wave_style": "Forme de l'onde :",
        "lbl_wave_color": "Couleur de l'onde :",
        "sec_seasonal": "Effets Saisonniers",
        "lbl_seasonal": "Effets festifs dans le widget :",
        "seasonal_dates": "Périodes : 01-29 Déc | 30 Déc-02 Jan | 20 Mar-10 Avr | 20-31 Oct (0 Mo RAM)",
        "sec_notifs": "Retours & Notifications",
        "lbl_toast_dur": "Durée du message de résultat :",
        "chk_sounds": "Activer les retours sonores (bips / WAV)",
        "lbl_sound_vol": "Volume des retours sonores :",
        "btn_test_sound": "Tester",

        "sec_whisper_capabilities": "Logique de Dictée & Verrouillage de Langue",
        "whisper_explanation": (
            "<b>Principe de fonctionnement du sélecteur de langue sur la pilule :</b><br>"
            "- <b>Mode AUTO :</b> Whisper détecte automatiquement la langue que vous parlez "
            "et la retranscrit telle quelle (Français écrit si vous parlez Français, Anglais si vous parlez Anglais).<br>"
            "- <b>Code Langue Verrouillé (ex: EN, FR, ES...) :</b> Vous verrouillez la langue de sortie de Whisper. "
            "Peu importe ce que vous parlez, Whisper tentera de sortir du texte dans cette langue.<br>"
            "- <b>Traduction native :</b> Si vous verrouillez sur 'EN' et parlez Français, Whisper effectuera "
            "automatiquement la traduction vers l'anglais écrit."
        ),
        "sec_quick_lang": "Configuration des Slots de Langues Rapides",
        "lbl_quick_lang_desc": (
            "Définissez jusqu'à 5 codes de langues supportés par Whisper "
            "pour y accéder rapidement depuis le sélecteur du widget flottant :<br>"
            "- Utilisez <code>AUTO</code> pour le mode de retranscription native sans traduction.<br>"
            "- Utilisez les codes ISO standards (ex: FR, EN, ES, DE, IT, JA...).<br>"
            "Vous pouvez saisir manuellement n'importe quel code ISO supporté par le modèle Whisper."
        ),
        "btn_apply_slots": "Appliquer les langues au widget",

        "lbl_hist_max": "Entrées conservées :",
        "btn_copy_sel": "Copier la sélection",
        "btn_del_sel": "Supprimer l'entrée",
        "btn_clear_all": "Tout effacer",

        "sec_legal_title": "Mentions Légales & Propriété Intellectuelle",
        "legal_notice": (
            "<h2 style='color: #B58E3F; margin-bottom: 2px;'>CONTINGENCE | Wisper v1.0.0</h2>"
            "<p style='color: #94A3B8; font-size: 11px; margin-top: 0;'>Suite de dictée vocale locale et de traduction instantanée en temps réel.</p>"
            "<br>"
            "<b>Auteur & Développeur Principal :</b><br>"
            "- <b>Reymann Dylan</b><br>"
            "- Conception logicielle et architecture développées avec l'assistance de l'IA Google Gemini (Gemini 3.8).<br><br>"
            "<b>Licence d'Utilisation & Conditions Générales :</b><br>"
            "- <b>Usage Libre :</b> Cette application et son code source sont mis à disposition gratuitement et librement utilisables par tous pour un usage personnel et privé.<br>"
            "- <b>Attribution Obligatoire :</b> En cas de réutilisation, modification, adaptation ou redistribution de tout ou partie du projet, la mention explicite du nom de l'auteur original (<b>Reymann Dylan</b>) est strictement obligatoire dans le code et la documentation.<br>"
            "- <b>Interdiction Commerciale Stricte :</b> Toute exploitation commerciale, monétisation, vente ou intégration payante de ce projet ou de ses dérivés est rigoureusement interdite.<br><br>"
            "<b>Confidentialité & RGPD :</b><br>"
            "Traitement 100 % local et autonome. Aucun enregistrement audio, aucune donnée biométrique "
            "ni aucun texte transcrit ne transitent par Internet ou des serveurs tiers.<br><br>"
            "<b>Composants Tiers :</b><br>"
            "- Faster-Whisper (Systran - MIT/Apache 2.0)<br>"
            "- Whisper Model (OpenAI - MIT)<br>"
            "- Silero VAD (Snakers4)<br>"
            "- PySide6 (The Qt Company - LGPLv3)"
        ),

        "state_ready": "Prêt",
        "state_listening": "Écoute",
        "state_processing": "Transcription...",
        "press_key": "Appuyez sur",
        "toast_copied": "Copié !",
        "toast_empty": "Historique vide",
        "toastShort": "Trop court",
        "toastShort_ nano": "✓",
        "toast Short": "Trop court",
        "toast_short": "Trop court",
        "toast_inaudible": "Inaudible",
        "toast Short_nano": "✓",
        "menu_copy": "Copier la dernière transcription",
        "menu_size": "Taille du widget",
        "menu_hide": "Masquer le widget",
        "menu_recenter": "Recentrer le widget",
        "menu_settings": "Paramètres",
        "menu_restart": "Redémarrer",
        "menu_quit": "Quitter"
    },
    "en": {
        "app_subtitle": "Local AI Voice Dictation | RTX GPU Acceleration",
        "tab_sys": "System | Engine",
        "tab_audio": "Shortcuts | Mic",
        "tab_style": "Interface | Style",
        "tab_lang": "Languages | Operation",
        "tab_hist": "History",
        "tab_about": "Legal Notices",

        "sec_app_lang": "Interface Language",
        "lbl_app_lang": "Display language:",
        "sec_boot": "Automatic Startup",
        "autostart_label": "Launch automatically on Windows startup",
        "sec_device": "GPU/CPU Acceleration",
        "device_gpu": "Dedicated Graphics Card (NVIDIA CUDA RTX - Recommended)",
        "device_cpu": "Central Processor (CPU - Universal compatibility, slower)",
        "sec_specs": "Specifications & Storage",
        "sec_model": "Whisper Model",
        "sec_maint": "Maintenance & Position",
        "btn_recenter": "Recenter widget",
        "btn_restart": "Restart application",
        "btn_open_storage": "Open data location (%APPDATA%)",

        "sec_shortcuts": "Shortcuts & Push-to-talk",
        "lbl_main_hotkey": "Dictation hotkey (Toggle):",
        "chk_ptt": "Enable hold-to-talk mode (Push-to-talk)",
        "chk_ptt_dedicated": "Use a dedicated key for Push-to-talk",
        "lbl_ptt_dedicated": "Dedicated Push-to-talk key:",
        "ptt_hint": "In Push-to-talk: silence never interrupts recording while the key is held.",
        "sec_mic": "Microphone & Silence Detection",
        "lbl_audio_gain": "Microphone input gain:",
        "chk_silence": "Enable auto-stop after silence (Toggle mode)",
        "lbl_silence_delay": "Silence duration before stop:",

        "sec_theme": "Application Theme",
        "lbl_palette": "Configurator palette:",
        "theme_gold": "Dark gold contingence",
        "theme_dark": "Carbon & Graphite (Sleek)",
        "sec_widget": "Floating Widget",
        "chk_show_hud": "Show floating widget on screen",
        "chk_key_minimal": "Minimalist key display mode (e.g. Ready | F8)",
        "lbl_hud_size": "Bar format:",
        "lbl_hud_corners": "Bar corners:",
        "lbl_diode_style": "Status diode style:",
        "lbl_hud_bg": "Custom background:",
        "lbl_hud_mic": "Microphone color:",
        "chk_auto_contrast": "Automatically adjust contrast (text & buttons)",
        "lbl_hud_opacity": "Background opacity:",
        "btn_pick_color": "Choose color...",
        "btn_reset": "Reset",
        "sec_wave": "Voice Animation",
        "chk_wave": "Enable reactive voice animation",
        "lbl_wave_style": "Wave style:",
        "lbl_wave_color": "Wave color:",
        "sec_seasonal": "Seasonal Effects",
        "lbl_seasonal": "Festive effects in widget:",
        "seasonal_dates": "Periods: Dec 01-29 | Dec 30-Jan 02 | Mar 20-Apr 10 | Oct 20-31 (0 MB RAM)",
        "sec_notifs": "Feedback & Notifications",
        "lbl_toast_dur": "Result message duration:",
        "chk_sounds": "Enable audio feedback (beeps / WAV)",
        "lbl_sound_vol": "Feedback audio volume:",
        "btn_test_sound": "Test",

        "sec_whisper_capabilities": "Dictation Logic & Language Locking",
        "whisper_explanation": (
            "<b>How the language selector on the pill works:</b><br>"
            "- <b>AUTO Mode:</b> Whisper automatically detects the language you speak "
            "and transcribes it as is (French text if you speak French, English if you speak English).<br>"
            "- <b>Locked Language Code (e.g., EN, FR, ES...):</b> You lock Whisper's output language. "
            "Whatever you speak, Whisper will attempt to output text in that language.<br>"
            "- <b>Native Translation:</b> If you lock to 'EN' and speak French, Whisper will automatically "
            "perform the translation to written English."
        ),
        "sec_quick_lang": "Quick Language Slots Configuration",
        "lbl_quick_lang_desc": (
            "Define up to 5 language codes supported by Whisper "
            "for quick access from the floating widget selector:<br>"
            "- Use <code>AUTO</code> for native transcription mode without translation.<br>"
            "- Use standard ISO codes (e.g., FR, EN, ES, DE, IT, JA...).<br>"
            "You can manually enter any ISO code supported by the Whisper model."
        ),
        "btn_apply_slots": "Apply languages to widget",

        "lbl_hist_max": "Saved entries:",
        "btn_copy_sel": "Copy selection",
        "btn_del_sel": "Delete entry",
        "btn_clear_all": "Clear all",

        "sec_legal_title": "Legal Notices & Intellectual Property",
        "legal_notice": (
            "<h2 style='color: #B58E3F; margin-bottom: 2px;'>CONTINGENCE | Wisper v1.0.0</h2>"
            "<p style='color: #94A3B8; font-size: 11px; margin-top: 0;'>Local AI voice dictation and real-time instant translation suite.</p>"
            "<br>"
            "<b>Lead Creator & Developer:</b><br>"
            "- <b>Reymann Dylan</b><br>"
            "- Software design and architecture co-developed with Google Gemini AI (Gemini 3.8).<br><br>"
            "<b>License Terms:</b><br>"
            "- <b>Free Usage:</b> This project is freely available for personal, non-commercial use by everyone.<br>"
            "- <b>Attribution Required:</b> Any modification, derivative work or redistribution must explicitly credit <b>Reymann Dylan</b> as the original creator.<br>"
            "- <b>Non-Commercial:</b> Any commercial use, sale, or paid distribution is strictly prohibited.<br><br>"
            "<b>Privacy & Offline Guarantee:</b><br>"
            "100% offline processing. No voice data or transcription ever leaves your local system.<br><br>"
            "<b>Open-Source Libraries:</b><br>"
            "- Faster-Whisper (Systran - MIT/Apache 2.0)<br>"
            "- Whisper Model (OpenAI - MIT)<br>"
            "- Silero VAD (Snakers4)<br>"
            "- PySide6 (The Qt Company - LGPLv3)"
        ),

        "state_ready": "Ready",
        "state_listening": "Listening",
        "state_processing": "Transcribing...",
        "press_key": "Press",
        "toast_copied": "Copied!",
        "toast_empty": "Empty history",
        "toastShort": "Too short",
        "toastShort_ nano": "✓",
        "toast Short": "Too short",
        "toast_short": "Too short",
        "toast_inaudible": "Inaudible",
        "toast Short_nano": "✓",
        "menu_copy": "Copy last transcription",
        "menu_size": "Widget size",
        "menu_hide": "Hide widget",
        "menu_recenter": "Recenter widget",
        "menu_settings": "Settings",
        "menu_restart": "Restart",
        "menu_quit": "Quit"
    }
}

def t(key: str, lang: str = "fr") -> str:
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["fr"])
    return lang_dict.get(key, key)