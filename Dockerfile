# Dockerfile pour Renewgy Parser - Projet Unifié

# 1. Base Image
FROM python:3.13-slim

# 2. Définir le répertoire de travail
WORKDIR /renewgy

# 3. Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Créer les dossiers de données
RUN mkdir -p excel_files csv_files templates

# 5. Copier les fichiers du projet unifié
COPY renewgy_parser.py renewgy_parser_gui.py ./
COPY templates/ ./templates/
COPY ean_config.json ./

# 6. Copier les dossiers de données s'ils existent
COPY excel_files/ ./excel_files/
COPY csv_files/ ./csv_files/

# 7. Exposer le port pour l'interface web
EXPOSE 5000

# 8. Par défaut, lancer l'interface web (peut être surchargé)
CMD ["python", "renewgy_parser_gui.py"]
