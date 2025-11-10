#!/bin/bash
# Installation script for SolfSound Dispatcher (Linux/macOS)

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║           🎵 SolfSound Dispatcher Installer 🎵               ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez installer Python 3.8 ou supérieur."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION détecté"

# Check FFmpeg
echo ""
echo "🔍 Vérification de FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg n'est pas installé."
    echo ""
    echo "Pour installer FFmpeg:"
    echo "  - Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  - macOS: brew install ffmpeg"
    echo "  - Fedora: sudo dnf install ffmpeg"
    echo ""
    read -p "Voulez-vous continuer sans FFmpeg? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ FFmpeg est installé"
fi

# Create virtual environment
echo ""
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Échec de la création de l'environnement virtuel"
    exit 1
fi
echo "✅ Environnement virtuel créé"

# Activate virtual environment
echo ""
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Mise à jour de pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installation des dépendances (cela peut prendre quelques minutes)..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation des dépendances"
    exit 1
fi

# Install SolfSound
echo ""
echo "🎵 Installation de SolfSound Dispatcher..."
pip install -e .
if [ $? -ne 0 ]; then
    echo "❌ Échec de l'installation de SolfSound"
    exit 1
fi

# Create desktop shortcut (optional)
echo ""
read -p "Voulez-vous créer des raccourcis de lancement? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    chmod +x run_desktop.py
    chmod +x run_web.py
    echo "✅ Raccourcis créés"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         ✅ Installation Terminée avec Succès! ✅             ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Pour utiliser SolfSound Dispatcher:"
echo ""
echo "1. Ligne de commande (CLI):"
echo "   source venv/bin/activate"
echo "   solfsound --help"
echo ""
echo "2. Interface Web:"
echo "   ./run_web.py"
echo "   ou: python run_web.py"
echo ""
echo "3. Application Desktop:"
echo "   ./run_desktop.py"
echo "   ou: python run_desktop.py"
echo ""
echo "📖 Consultez le README.md pour plus d'informations"
echo ""
