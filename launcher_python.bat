@echo off
REM Launcher Python with virtual environment for Renewgy Parser.
REM Compatible: Windows

setlocal enabledelayedexpansion

echo 🐍 Renewgy Parser - Launcher Python avec Environnement Virtuel
echo =================================================================
echo.

REM Variables.
set VENV_NAME=renewgy_parser_venv
set VENV_PATH=.\%VENV_NAME%
set PYTHON_CMD=python
set PIP_CMD=pip
set PORT=5001

REM Function to detect Windows version.
echo 🪟 Windows détecté
ver
echo.

REM Function to check Python installation.
echo 🔍 Vérification de Python...

REM Try 'py' launcher first (recommended on Windows).
py --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('py --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python !PYTHON_VERSION! trouvé via 'py' launcher
    set PYTHON_CMD=py
    goto python_found
)

REM Try 'python' command.
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python !PYTHON_VERSION! trouvé via 'python' command
    set PYTHON_CMD=python
    goto python_found
)

REM Try 'python3' command.
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python !PYTHON_VERSION! trouvé via 'python3' command
    set PYTHON_CMD=python3
    goto python_found
)

REM No Python found.
echo ❌ Python n'est pas installé ou pas accessible
echo.
echo 💡 Solutions possibles:
echo    1. Installez Python 3.10+ depuis https://python.org
echo    2. Assurez-vous que Python est dans le PATH système
echo    3. Redémarrez votre terminal après installation
echo.
pause
exit /b 1

:python_found
echo 🎯 Utilisation de: %PYTHON_CMD% (version %PYTHON_VERSION%)
echo.

REM Function to check if the port is available.
echo 🔍 Vérification du port %PORT%...
netstat -an | findstr ":%PORT% " >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Le port %PORT% est déjà utilisé
    echo    Processus utilisant le port:
    netstat -ano | findstr ":%PORT% "
    echo.
    set /p response="   Voulez-vous continuer quand même ? (y/N): "
    if /i not "!response!"=="y" (
        echo ❌ Annulation du lancement
        pause
        exit /b 1
    )
) else (
    echo ✅ Port %PORT% disponible
)

REM Function to set up the virtual environment.
echo.
echo 🏗️  Configuration de l'environnement virtuel...

if exist "%VENV_PATH%" (
    echo 📁 Environnement virtuel existant trouvé: %VENV_PATH%
    echo.
    set /p recreate_response="❓ Voulez-vous recréer l'environnement virtuel ? (y/N): "
    if /i "!recreate_response!"=="y" (
        echo 🗑️  Suppression de l'ancien environnement virtuel...
        rmdir /s /q "%VENV_PATH%" 2>nul
        if %errorlevel% neq 0 (
            echo ⚠️  Impossible de supprimer complètement l'ancien environnement
            echo    Certains fichiers peuvent être en cours d'utilisation
        )
        goto create_venv
    )
    
    REM Test if the virtual environment is working.
    echo 🧪 Test de l'environnement virtuel existant...
    call "%VENV_PATH%\Scripts\activate.bat" 2>nul
    if %errorlevel% neq 0 (
        echo ❌ L'environnement virtuel est corrompu, recréation automatique...
        rmdir /s /q "%VENV_PATH%" 2>nul
        goto create_venv
    )
    
    REM Test if the required packages are installed.
    echo 🔍 Vérification des dépendances...
    %PYTHON_CMD% -c "import flask, pandas, openpyxl" 2>nul
    if %errorlevel% neq 0 (
        echo ⚠️  Dépendances manquantes, réinstallation...
        %PYTHON_CMD% -m pip install -r requirements.txt --quiet
        if %errorlevel% neq 0 (
            echo ❌ Erreur lors de l'installation des dépendances
            echo    Essayez de recréer l'environnement virtuel
            pause
            exit /b 1
        )
        echo ✅ Dépendances réinstallées
    ) else (
        echo ✅ Environnement virtuel opérationnel
    )
    goto setup_dirs
)

:create_venv
echo 🔨 Création de l'environnement virtuel: %VENV_NAME%
%PYTHON_CMD% -m venv "%VENV_PATH%"
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de la création de l'environnement virtuel
    echo    Assurez-vous que Python est correctement installé
    pause
    exit /b 1
)
echo ✅ Environnement virtuel créé

REM Activate the virtual environment.
echo 🔓 Activation de l'environnement virtuel...
call "%VENV_PATH%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'activation de l'environnement virtuel
    pause
    exit /b 1
)

REM Update pip to the latest version.
echo 📦 Mise à jour de pip...
%PYTHON_CMD% -m pip install --upgrade pip --quiet

REM Install the required packages.
echo 📦 Installation des dépendances...
if not exist "requirements.txt" (
    echo ❌ Fichier requirements.txt introuvable
    pause
    exit /b 1
)

%PYTHON_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'installation des dépendances
    echo    Vérifiez votre fichier requirements.txt
    pause
    exit /b 1
)

echo ✅ Environnement virtuel prêt

:setup_dirs
REM Function to set up the necessary directories.
echo 📁 Vérification des dossiers...

if not exist "excel_files" (
    echo 📁 Création du dossier excel_files...
    mkdir excel_files
)

if not exist "csv_files" (
    echo 📁 Création du dossier csv_files...
    mkdir csv_files
)

if not exist "templates" (
    echo 📁 Création du dossier templates...
    mkdir templates
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

REM Function to launch the web interface.
echo.
echo 🚀 Lancement de l'interface web Renewgy Parser...
echo 🌍 Interface accessible sur: http://localhost:%PORT%
echo 🛑 Appuyez sur Ctrl+C pour arrêter le serveur
echo.
echo =================================================
echo.

REM Environment configuration for Flask.
set FLASK_PORT=%PORT%
set FLASK_HOST=127.0.0.1

REM Launch the Flask application.
%PYTHON_CMD% renewgy_parser_gui.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Erreur lors du lancement de l'interface web
    echo    Vérifiez les logs ci-dessus pour plus de détails
    pause
    exit /b 1
)

echo.
echo 🧹 Nettoyage...
if defined VIRTUAL_ENV (
    call deactivate 2>nul
)
echo 👋 Au revoir !
pause
