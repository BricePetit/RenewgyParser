#!/bin/bash
# Launcher Docker - Renewgy Parser.
# Compatible: macOS and Linux.


# Stop on error.
set -e

echo "🐳 Renewgy Parser - Launcher Docker"
echo "===================================="
echo ""

# Variables.
IMAGE_NAME="renewgy-parser"
CONTAINER_NAME="renewgy-web-interface"
PORT_HOST="5001"
PORT_CONTAINER="5000"

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

# Function to check Docker installation.
check_docker() {
    echo "🔍 Vérification de Docker..."
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker n'est pas installé"
        echo "   Installez Docker depuis: https://docs.docker.com/get-docker/"
        exit 1
    fi
    if ! docker info &> /dev/null; then
        echo "❌ Docker n'est pas démarré ou accessible"
        echo "   Démarrez Docker Desktop ou le service Docker"
        exit 1
    fi
    DOCKER_VERSION=$(docker --version)
    echo "✅ $DOCKER_VERSION détecté et fonctionnel"
}

# Function to check Docker Compose installation.
check_docker_compose() {
    echo "🔍 Vérification de Docker Compose..."
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
        COMPOSE_VERSION=$(docker-compose --version)
        echo "✅ $COMPOSE_VERSION détecté"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
        COMPOSE_VERSION=$(docker compose version)
        echo "✅ $COMPOSE_VERSION détecté"
    else
        echo "⚠️  Docker Compose non trouvé, utilisation de docker run"
        COMPOSE_CMD=""
    fi
}

# Function to check if the port is available.
check_port() {
    echo "🔍 Vérification du port $PORT_HOST..."
    if lsof -i :$PORT_HOST &> /dev/null; then
        echo "⚠️  Le port $PORT_HOST est déjà utilisé"
        echo "   Processus utilisant le port:"
        lsof -i :$PORT_HOST
        echo ""
        echo "   Voulez-vous arrêter le processus et continuer ? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            # Try to stop the container if it exists.
            docker stop $CONTAINER_NAME 2>/dev/null || true
            docker rm $CONTAINER_NAME 2>/dev/null || true
            sleep 2
        else
            echo "❌ Annulation du lancement"
            exit 1
        fi
    else
        echo "✅ Port $PORT_HOST disponible"
    fi
}

# Function to set up directories.
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

# Function to build the Docker image.
build_image() {
    echo "🔍 Vérification de l'image Docker..."

    if docker image inspect $IMAGE_NAME &> /dev/null; then
        echo "✅ Image $IMAGE_NAME trouvée"

        # Check if Dockerfile is newer than the image.
        if [ "Dockerfile" -nt "$(docker image inspect $IMAGE_NAME --format='{{.Created}}')" ] 2>/dev/null; then
            echo "⚠️  Dockerfile modifié récemment"
            echo "   Voulez-vous reconstruire l'image ? (y/N)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                build_docker_image
            fi
        fi
    else
        echo "🔨 Image $IMAGE_NAME non trouvée, construction en cours..."
        build_docker_image
    fi
}

# Function to build the Docker image.
build_docker_image() {
    echo "🔨 Construction de l'image Docker $IMAGE_NAME..."

    if ! docker build -t $IMAGE_NAME . ; then
        echo "❌ Erreur lors de la construction de l'image Docker"
        echo "   Vérifiez votre Dockerfile et les dépendances"
        exit 1
    fi

    echo "✅ Image Docker $IMAGE_NAME construite avec succès"
}

# Function to stop and remove existing container.
stop_existing_container() {
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        echo "⏹️  Arrêt du conteneur existant $CONTAINER_NAME..."
        docker stop $CONTAINER_NAME
    fi

    if docker ps -aq -f name=$CONTAINER_NAME | grep -q .; then
        echo "🗑️  Suppression du conteneur existant $CONTAINER_NAME..."
        docker rm $CONTAINER_NAME
    fi
}

# Function to launch with Docker Compose.
launch_with_compose() {
    echo "🚀 Lancement avec Docker Compose..."

    if [ ! -f "docker-compose.yml" ]; then
        echo "❌ Fichier docker-compose.yml non trouvé"
        return 1
    fi

    echo "🌍 Interface accessible sur: http://localhost:$PORT_HOST"
    echo "🛑 Appuyez sur Ctrl+C pour arrêter le serveur"
    echo ""
    echo "================================================="
    echo ""

    # Launch with interruption management and automatic deletion.
    $COMPOSE_CMD up renewgy-web-interface
    local exit_code=$?
    
    # If normal exit (Ctrl+C), do not fallback to docker run.
    if [ $exit_code -eq 130 ] || [ $exit_code -eq 2 ]; then
        echo ""
        echo "🛑 Arrêt demandé par l'utilisateur"
        return 130
    fi

    return $exit_code
}

# Function to launch with Docker run.
launch_with_docker() {
    echo "🚀 Lancement avec Docker run..."

    stop_existing_container

    echo "🌍 Interface accessible sur: http://localhost:$PORT_HOST"
    echo "🛑 Appuyez sur Ctrl+C pour arrêter le serveur"
    echo ""
    echo "================================================="
    echo ""

    docker run -it --rm \
        --name $CONTAINER_NAME \
        -p $PORT_HOST:$PORT_CONTAINER \
        -v "$(pwd)/excel_files:/renewgy/excel_files" \
        -v "$(pwd)/csv_files:/renewgy/csv_files" \
        -v "$(pwd)/ean_config.json:/renewgy/ean_config.json" \
        $IMAGE_NAME
}

# Function to launch the web interface.
launch_web() {
    if [ -n "$COMPOSE_CMD" ] && [ -f "docker-compose.yml" ]; then
        launch_with_compose
        local compose_exit_code=$?

        # If Ctrl+C with Docker Compose, do not fallback to docker run.
        if [ $compose_exit_code -eq 130 ] || [ $compose_exit_code -eq 2 ]; then
            echo "🛑 Arrêt du launcher Docker (code: $compose_exit_code)"
            exit 0
        elif [ $compose_exit_code -ne 0 ]; then
            echo "⚠️  Docker Compose a échoué (code: $compose_exit_code), tentative avec docker run..."
            launch_with_docker
        fi
    else
        launch_with_docker
    fi
}

# Cleanup function to stop and remove the container.
cleanup() {
    echo ""
    echo "🧹 Nettoyage..."

    # Stop and remove the container if it exists.
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        echo "⏹️  Arrêt du conteneur $CONTAINER_NAME..."
        docker stop $CONTAINER_NAME 2>/dev/null || true
    fi

    if docker ps -aq -f name=$CONTAINER_NAME | grep -q .; then
        echo "🗑️  Suppression du conteneur $CONTAINER_NAME..."
        docker rm $CONTAINER_NAME 2>/dev/null || true
    fi

    # Cleanup Docker Compose if used.
    if [ -n "$COMPOSE_CMD" ] && [ -f "docker-compose.yml" ]; then
        echo "🧹 Nettoyage Docker Compose..."
        $COMPOSE_CMD down --remove-orphans 2>/dev/null || true
    fi

    echo "👋 Au revoir !"
}

# Trap to ensure cleanup is called on exit or interruption.
trap cleanup EXIT INT TERM

# Main function to run the launcher.
main() {
    detect_os
    check_docker
    check_docker_compose
    check_port
    setup_directories
    check_config
    build_image
    launch_web
}

# Run the main function with all arguments.
main "$@"
