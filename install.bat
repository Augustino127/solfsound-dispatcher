@echo off
REM Installation script for SolfSound Dispatcher (Windows)

echo ================================================================
echo.
echo            🎵 SolfSound Dispatcher Installer 🎵
echo.
echo ================================================================
echo.

REM Check Python
echo 🔍 Vérification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo Veuillez installer Python 3.8 ou supérieur depuis python.org
    pause
    exit /b 1
)
echo ✅ Python détecté
echo.

REM Check FFmpeg
echo 🔍 Vérification de FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  FFmpeg n'est pas installé ou pas dans le PATH
    echo.
    echo Pour installer FFmpeg:
    echo   1. Téléchargez depuis https://ffmpeg.org/download.html
    echo   2. Ajoutez le dossier bin de FFmpeg au PATH système
    echo.
    pause
)
echo.

REM Create virtual environment
echo 📦 Création de l'environnement virtuel...
python -m venv venv
if errorlevel 1 (
    echo ❌ Échec de la création de l'environnement virtuel
    pause
    exit /b 1
)
echo ✅ Environnement virtuel créé
echo.

REM Activate virtual environment
echo 🔄 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Mise à jour de pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo 📥 Installation des dépendances (cela peut prendre quelques minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Échec de l'installation des dépendances
    pause
    exit /b 1
)
echo.

REM Install SolfSound
echo 🎵 Installation de SolfSound Dispatcher...
pip install -e .
if errorlevel 1 (
    echo ❌ Échec de l'installation de SolfSound
    pause
    exit /b 1
)
echo.

echo ================================================================
echo.
echo         ✅ Installation Terminée avec Succès! ✅
echo.
echo ================================================================
echo.
echo Pour utiliser SolfSound Dispatcher:
echo.
echo 1. Ligne de commande (CLI):
echo    venv\Scripts\activate
echo    solfsound --help
echo.
echo 2. Interface Web:
echo    python run_web.py
echo.
echo 3. Application Desktop:
echo    python run_desktop.py
echo.
echo 📖 Consultez le README.md pour plus d'informations
echo.
pause
