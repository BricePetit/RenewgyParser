#!/bin/bash
# Launcher Python with virtual environment for Renewgy Parser.
# Compatible: macOS and Linux.

# Stop on error.
set -e

echo "🐍 Renewgy Parser - Launcher Python avec Environnement Virtuel"
echo "================================================================="
echo ""

# Variables.
VENV_NAME="renewgy_parser_venv"
VENV_PATH="./$VENV_NAME"
PYTHON_CMD="python3"
PIP_CMD="pip"
PORT="5001"

# Function to detect the OS.
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍎 macOS détecté"
        return 0
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "🐧 Linux détecté"
        return 0
    else
        echo "❓ OS non reconnu: $OSTYPE"
        return 0
    fi
}

# Function to check Python installation.
check_python() {
    echo "🔍 Vérification de Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        echo "✅ $PYTHON_VERSION trouvé"
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1)
        echo "✅ $PYTHON_VERSION trouvé"
        PYTHON_CMD="python"
    else
        echo "❌ Python n'est pas installé ou pas dans le PATH"
        echo "   Veuillez installer Python 3.10+ depuis https://python.org"
        exit 1
    fi
}

# Function to check if the port is available.
check_port() {
    echo "🔍 Vérification du port $PORT..."
    if lsof -i :$PORT &> /dev/null; then
        echo "⚠️  Le port $PORT est déjà utilisé"
        echo "   Processus utilisant le port:"
        lsof -i :$PORT
        echo ""
        echo "   Voulez-vous continuer quand même ? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "❌ Annulation du lancement"
            exit 1
        fi
    else
        echo "✅ Port $PORT disponible"
    fi
}

# Function to set up the virtual environment.
setup_venv() {
    echo "🏗️  Configuration de l'environnement virtuel..."
    if [ -d "$VENV_PATH" ]; then
        echo "📁 Environnement virtuel existant trouvé: $VENV_PATH"
        # Test if the virtual environment is working.
        echo "🧪 Test de l'environnement virtuel..."
        source "$VENV_PATH/bin/activate" 2>/dev/null || {
            echo "❌ L'environnement virtuel est corrompu, recréation..."
            rm -rf "$VENV_PATH"
        }
        if [ -d "$VENV_PATH" ]; then
            # Test if the required packages are installed.
            if ! $PYTHON_CMD -c "import flask, pandas, openpyxl" 2>/dev/null; then
                echo "⚠️  Dépendances manquantes, réinstallation..."
                $PIP_CMD install -r requirements.txt
            else
                echo "✅ Environnement virtuel opérationnel"
                return 0
            fi
        fi
    fi

    if [ ! -d "$VENV_PATH" ]; then
        echo "🔨 Création de l'environnement virtuel: $VENV_NAME"
        $PYTHON_CMD -m venv "$VENV_PATH" || {
            echo "❌ Erreur lors de la création de l'environnement virtuel"
            echo "   Assurez-vous que python3-venv est installé:"
            echo "   Ubuntu/Debian: sudo apt install python3-venv"
            echo "   CentOS/RHEL: sudo yum install python3-venv"
            exit 1
        }
        echo "✅ Environnement virtuel créé"
    fi
    # Activate the virtual environment.
    echo "🔓 Activation de l'environnement virtuel..."
    source "$VENV_PATH/bin/activate"
    # Update pip to the latest version.
    echo "📦 Mise à jour de pip..."
    $PIP_CMD install --upgrade pip --quiet
    # Install the required packages.
    echo "📦 Installation des dépendances..."
    $PIP_CMD install -r requirements.txt || {
        echo "❌ Erreur lors de l'installation des dépendances"
        echo "   Vérifiez votre fichier requirements.txt"
        exit 1
    }
    echo "✅ Environnement virtuel prêt"
}

# Function to set up the necessary directories.
setup_directories() {
    echo "📁 Vérification des dossiers..."

    [ ! -d "excel_files" ] && {
        echo "📁 Création du dossier excel_files..."
        mkdir -p excel_files
    }

    [ ! -d "csv_files" ] && {
        echo "📁 Création du dossier csv_files..."
        mkdir -p csv_files
    }

    [ ! -d "templates" ] && {
        echo "📁 Création du dossier templates..."
        mkdir -p templates
    }

    echo "✅ Dossiers vérifiés"
}

# Function to check the EAN configuration.
check_config() {
    echo "⚙️  Vérification de la configuration..."

    if [ ! -f "ean_config.json" ]; then
        echo "⚠️  Fichier ean_config.json manquant"
        if [ -f "ean_config.example.json" ]; then
            echo "📋 Copie de ean_config.example.json vers ean_config.json"
            cp ean_config.example.json ean_config.json
            echo "⚠️  IMPORTANT: Veuillez adapter le fichier ean_config.json à vos besoins"
            echo "   Éditez le fichier avec vos codes EAN avant de continuer"
            echo ""
            echo "   Voulez-vous continuer avec la configuration d'exemple ? (y/N)"
            read -r response
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                echo "❌ Veuillez configurer ean_config.json et relancer"
                exit 1
            fi
        else
            echo "❌ Fichier ean_config.example.json introuvable"
            echo "   Créez un fichier ean_config.json avec vos mappings EAN"
            exit 1
        fi
    else
        echo "✅ Configuration ean_config.json trouvée"
    fi
}

# Function to launch the web interface.
launch_web() {
    echo ""
    echo "🚀 Lancement de l'interface web Renewgy Parser..."
    echo "🌍 Interface accessible sur: http://localhost:$PORT"
    echo "🛑 Appuyez sur Ctrl+C pour arrêter le serveur"
    echo ""
    echo "================================================="
    echo ""

    # Environment configuration for Flask.
    export FLASK_PORT="$PORT"
    export FLASK_HOST="127.0.0.1"

    # Launch the Flask application.
    $PYTHON_CMD renewgy_parser_gui.py || {
        echo ""
        echo "❌ Erreur lors du lancement de l'interface web"
        echo "   Vérifiez les logs ci-dessus pour plus de détails"
        exit 1
    }
}

# Cleanup function to deactivate the virtual environment and exit gracefully.
cleanup() {
    echo ""
    echo "🧹 Nettoyage..."
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate 2>/dev/null || true
    fi
    echo "👋 Au revoir !"
}

# Trap to ensure cleanup is called on exit or interruption.
trap cleanup EXIT INT TERM

# Main function to run the launcher.
main() {
    detect_os
    check_python
    check_port
    setup_directories
    check_config
    setup_venv
    launch_web
}

# Run the main function with all arguments passed to the script.
main "$@"
