@echo off
REM Launcher Docker - Renewgy Parser.
REM Compatible: Windows

setlocal enabledelayedexpansion

echo 🐳 Renewgy Parser - Launcher Docker
echo ====================================
echo.

REM Variables.
set IMAGE_NAME=renewgy-parser
set CONTAINER_NAME=renewgy-web-interface
set PORT_HOST=5001
set PORT_CONTAINER=5000

REM Function to detect Windows version.
echo 🪟 Windows détecté
ver
echo.

REM Function to check Docker installation.
echo 🔍 Vérification de Docker...

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker n'est pas installé
    echo    Installez Docker Desktop depuis: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker n'est pas démarré ou accessible
    echo    Démarrez Docker Desktop
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('docker --version 2^>^&1') do set DOCKER_VERSION=%%i
echo ✅ !DOCKER_VERSION! détecté et fonctionnel

REM Function to check Docker Compose installation.
echo 🔍 Vérification de Docker Compose...

docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    set COMPOSE_CMD=docker-compose
    for /f "tokens=*" %%i in ('docker-compose --version 2^>^&1') do set COMPOSE_VERSION=%%i
    echo ✅ !COMPOSE_VERSION! détecté
) else (
    docker compose version >nul 2>&1
    if %errorlevel% equ 0 (
        set COMPOSE_CMD=docker compose
        for /f "tokens=*" %%i in ('docker compose version 2^>^&1') do set COMPOSE_VERSION=%%i
        echo ✅ !COMPOSE_VERSION! détecté
    ) else (
        echo ⚠️  Docker Compose non trouvé, utilisation de docker run
        set COMPOSE_CMD=
    )
)

REM Function to check if the port is available.
echo 🔍 Vérification du port %PORT_HOST%...
netstat -an | findstr ":%PORT_HOST% " >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Le port %PORT_HOST% est déjà utilisé
    echo    Processus utilisant le port:
    netstat -ano | findstr ":%PORT_HOST% "
    echo.
    set /p response="   Voulez-vous arrêter le processus et continuer ? (y/N): "
    if /i "!response!"=="y" (
        REM Try to stop the container if it exists.
        docker stop %CONTAINER_NAME% >nul 2>&1
        docker rm %CONTAINER_NAME% >nul 2>&1
        timeout /t 2 >nul
    ) else (
        echo ❌ Annulation du lancement
        pause
        exit /b 1
    )
) else (
    echo ✅ Port %PORT_HOST% disponible
)

REM Function to set up directories.
echo 📁 Vérification des dossiers...

if not exist "excel_files" (
    echo 📁 Création du dossier excel_files...
    mkdir excel_files
)

if not exist "csv_files" (
    echo 📁 Création du dossier csv_files...
    mkdir csv_files
)

echo ✅ Dossiers vérifiés

REM Function to check the EAN configuration.
echo ⚙️  Vérification de la configuration...

if not exist "ean_config.json" (
    echo ⚠️  Fichier ean_config.json manquant
    if exist "ean_config.example.json" (
        echo 📋 Copie de ean_config.example.json vers ean_config.json
        copy ean_config.example.json ean_config.json >nul
        echo ⚠️  IMPORTANT: Veuillez adapter le fichier ean_config.json à vos besoins
        echo    Éditez le fichier avec vos codes EAN avant de continuer
        echo.
        set /p response="   Voulez-vous continuer avec la configuration d'exemple ? (y/N): "
        if /i not "!response!"=="y" (
            echo ❌ Veuillez configurer ean_config.json et relancer
            pause
            exit /b 1
        )
    ) else (
        echo ❌ Fichier ean_config.example.json introuvable
        echo    Créez un fichier ean_config.json avec vos mappings EAN
        pause
        exit /b 1
    )
) else (
    echo ✅ Configuration ean_config.json trouvée
)

REM Fonction pour construire l'image Docker si nécessaire
echo 🔍 Vérification de l'image Docker...

docker image inspect %IMAGE_NAME% >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Image %IMAGE_NAME% trouvée

    REM Note: Dockerfile modification verification is complex in batch mode.
    REM We simply propose to rebuild.
    set /p rebuild="   Voulez-vous reconstruire l'image ? (y/N): "
    if /i "!rebuild!"=="y" (
        goto build_image
    )
) else (
    echo 🔨 Image %IMAGE_NAME% non trouvée, construction en cours...
    goto build_image
)
goto check_existing_container

:build_image
echo 🔨 Construction de l'image Docker %IMAGE_NAME%...

docker build -t %IMAGE_NAME% .
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de la construction de l'image Docker
    echo    Vérifiez votre Dockerfile et les dépendances
    pause
    exit /b 1
)

echo ✅ Image Docker %IMAGE_NAME% construite avec succès

:check_existing_container
REM Function to stop and remove existing container.
docker ps -q -f name=%CONTAINER_NAME% | findstr . >nul 2>&1
if %errorlevel% equ 0 (
    echo ⏹️  Arrêt du conteneur existant %CONTAINER_NAME%...
    docker stop %CONTAINER_NAME%
)

docker ps -aq -f name=%CONTAINER_NAME% | findstr . >nul 2>&1
if %errorlevel% equ 0 (
    echo 🗑️  Suppression du conteneur existant %CONTAINER_NAME%...
    docker rm %CONTAINER_NAME%
)

REM Function to launch the web interface.
if defined COMPOSE_CMD (
    if exist "docker-compose.yml" (
        goto launch_compose
    )
)
goto launch_docker

:launch_compose
echo 🚀 Lancement avec Docker Compose...
echo 🌍 Interface accessible sur: http://localhost:%PORT_HOST%
echo 🛑 Appuyez sur Ctrl+C pour arrêter le serveur
echo.
echo =================================================
echo.

%COMPOSE_CMD% up renewgy-web-interface
goto end

:launch_docker
echo 🚀 Lancement avec Docker run...
echo 🌍 Interface accessible sur: http://localhost:%PORT_HOST%
echo 🛑 Appuyez sur Ctrl+C pour arrêter le serveur
echo.
echo =================================================
echo.

docker run -it --rm ^
    --name %CONTAINER_NAME% ^
    -p %PORT_HOST%:%PORT_CONTAINER% ^
    -v "%CD%\excel_files:/renewgy/excel_files" ^
    -v "%CD%\csv_files:/renewgy/csv_files" ^
    -v "%CD%\ean_config.json:/renewgy/ean_config.json" ^
    %IMAGE_NAME%

:end
echo.
echo 🧹 Nettoyage...

REM Arrêter le conteneur s'il existe
docker stop %CONTAINER_NAME% >nul 2>&1

REM Supprimer le conteneur s'il existe
docker rm %CONTAINER_NAME% >nul 2>&1

REM Nettoyage Docker Compose si disponible
if defined COMPOSE_CMD (
    if exist "docker-compose.yml" (
        %COMPOSE_CMD% down --remove-orphans >nul 2>&1
    )
)

echo 👋 Au revoir !
pause
