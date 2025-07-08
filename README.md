# Renewgy Excel to CSV Parser

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Docker](https://img.shields.io/badge/docker-supported-blue.svg)
![macOS](https://img.shields.io/badge/macOS-compatible-000000?logo=apple&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-compatible-FCC624?logo=linux&logoColor=black)
![Windows](https://img.shields.io/badge/Windows-compatible-0078D6?logo=windows&logoColor=white)

Un parser robuste et moderne pour convertir les fichiers Excel de Renewgy en format CSV standardisé. Solution enterprise conçue pour l'efficacité, la simplicité d'utilisation et l'intégration transparente dans des workflows de traitement de données.

## ✨ Caractéristiques principales

- **Workflow universel simplifié** : Dossiers d'entrée et de sortie fixes (`excel_files/` → `csv_files/`)
- **Compatibilité multiplateforme** : Fonctionne sur macOS, Linux et Windows
- **Launchers intelligents** : Automatisation complète de l'installation et du déploiement
- **Interface web moderne** : Design ergonomique sans complexité technique  
- **Traitement par lots intelligent** : Personnalisation individuelle par fichier (nom, date, feuille)
- **Double mode d'utilisation** : Interface web conviviale ou CLI pour l'automatisation
- **Configuration zéro** : Workflow entièrement automatisé
- **Robustesse enterprise** : Validation rigoureuse, gestion d'erreurs et logging professionnel
- **Prêt pour la production** : Support Docker avec launcher automatique

## 🔧 Fonctionnalités détaillées

- **Conversion Excel vers CSV** : Traitement automatique des fichiers Excel Renewgy
- **Validation des données** : Vérification de la structure et de l'intégrité des données
- **Filtrage par date personnalisable** : Traitement des données à partir d'une date spécifique
- **Sélection de feuille** : Configuration de l'index de feuille Excel à traiter
- **Mapping EAN configurable** : Support des fichiers de configuration externes sécurisés
- **Logging multi-niveaux** : Verbose, normal, quiet selon vos besoins
- **Personnalisation avancée** : Options par fichier en mode batch
- **Interface responsive** : Fonctionne sur desktop, tablette et mobile

## 📋 Prérequis

- **Python 3.10+** (recommandé : 3.11 ou plus récent)
- **Dépendances Python** : `pandas`, `openpyxl`, `flask` (installées automatiquement)
- **Fichier de configuration EAN** obligatoire (voir [Configuration](#️-configuration))

### Dépendances Python

```txt
pandas>=1.5.0
openpyxl>=3.0.0
flask>=2.0.0
```

## 🚀 Installation Ultra-Simplifiée

### Launchers Automatiques (Recommandé)

Les launchers gèrent automatiquement l'installation complète et le lancement sur **macOS**, **Linux** et **Windows** :

1. **Clonez le projet** :

    ```bash
    git clone https://github.com/BricePetit/RenewgyParser.git
    cd RenewgyParser
    ```

2. **Créez votre fichier de configuration EAN** (voir [Configuration](#️-configuration))

3. **Lancez directement selon votre plateforme** :

**macOS / Linux :**

```bash
# Interface web avec Docker (recommandé).
./launcher_docker.sh

# Interface web locale avec environnement virtuel Python.
./launcher_python.sh
```

**Windows :**

```batch
REM Interface web avec Docker (recommandé).
launcher_docker.bat

REM Interface web locale avec environnement virtuel Python.
launcher_python.bat
```

Les launchers s'occupent automatiquement de :

- Vérification et installation des dépendances
- Configuration d'environnement (virtuel Python ou Docker)
- Création des dossiers requis
- Validation de la configuration
- Démarrage de l'interface web

### Installation Manuelle

Pour un contrôle manuel ou l'intégration dans des workflows existants :

#### Option A : Installation locale

```bash
pip install -r requirements.txt
python renewgy_parser_gui.py
```

#### Option B : Docker manuel

```bash
# Construction de l'image.
docker build -t renewgy-parser .

# Lancement.
docker-compose up renewgy-web-interface
```

## 📖 Utilisation

**Important** : Un fichier de configuration EAN est **obligatoire** pour toutes les opérations.

### 🌐 Interface Web (Recommandé)

Architecture simplifiée avec dossiers prédéfinis :

- **Dossier d'entrée** : `excel_files/`
- **Dossier de sortie** : `csv_files/`
- **Workflow** : Déposez vos fichiers Excel → Traitez via l'interface → Récupérez les CSV

#### Lancement avec Launchers

**macOS / Linux :**

```bash
# Docker (recommandé) - Configuration automatique complète.
./launcher_docker.sh

# Python local - Environnement virtuel automatique.
./launcher_python.sh
```

**Windows :**

```batch
REM Docker (recommandé) - Configuration automatique complète.
launcher_docker.bat

REM Python local - Environnement virtuel automatique.
launcher_python.bat
```

**Interface accessible sur <http://localhost:5001>**

#### Lancement Manuel

**Local :**

```bash
python renewgy_parser_gui.py
```

**Docker :**

```bash
# Avec Docker Compose (Simple).
docker-compose up renewgy-web-interface

# Avec Docker directement.
docker run -it --rm -p 5001:5000 \
  -v "$(pwd)/excel_files:/renewgy/excel_files" \
  -v "$(pwd)/csv_files:/renewgy/csv_files" \
  -v "$(pwd)/ean_config.json:/renewgy/ean_config.json" \
  renewgy-parser
```

#### Fonctionnalités de l'interface web

**Mode Single (Fichier unique) :**

- **Sélection de fichier** : Choix parmi les fichiers disponibles dans `excel_files/`
- **Nom de sortie personnalisable** : Génération automatique avec possibilité d'édition
- **Filtrage par date** : Traitement à partir d'une date spécifique
- **Configuration de feuille** : Sélection de l'index de feuille Excel
- **Options avancées** : Accès complet aux paramètres de configuration

**Mode Batch (Traitement par lots) :**

- **Traitement multiple** : Affichage et traitement de tous les fichiers Excel
- **Personnalisation individuelle** :
  - **Nom de sortie** : Éditable pour chaque fichier
  - **Date de début** : Filtrage personnalisé par fichier
  - **Index de feuille** : Configuration spécifique par fichier
- **Traitement simultané** : Processus unifié pour tous les fichiers sélectionnés

**Fonctionnalités communes :**

- **Monitoring en temps réel** : Suivi détaillé du traitement
- **Interface responsive** : Compatible desktop, tablette et mobile
- **Feedback instantané** : Messages d'état et indicateurs de progression
- **Gestion d'erreurs** : Rapports détaillés avec solutions suggérées

### 💻 Interface en Ligne de Commande

Pour l'intégration dans des scripts ou l'automatisation avancée.

#### Traitement d'un fichier unique

```bash
# Traitement basique.
python src/renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json

# Avec filtrage par date.
python src/renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --start-date 2023-01-01

# Avec logging verbose.
python src/renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --verbose
```

#### Traitement par lots

```bash
# Traitement de tous les fichiers Excel dans un répertoire.
python src/renewgy_parser.py --batch-input ./excel_files --batch-output ./csv_files --config ean_config.json

# Avec filtrage par date.
python src/renewgy_parser.py --batch-input ./excel_files --batch-output ./csv_files --config ean_config.json --start-date 2023-06-01

# Avec pattern personnalisé.
python src/renewgy_parser.py --batch-input ./excel_files --batch-output ./csv_files --config ean_config.json --pattern "*specific*"
```

#### Configuration et options avancées

```bash
# Utilisation d'un fichier de configuration EAN personnalisé (obligatoire).
python src/renewgy_parser.py --input input.xlsx --output output.csv --config mon_config.json

# Spécification de l'index de la feuille Excel.
python src/renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --sheet-index 0

# Combinaison de plusieurs options.
python src/renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --sheet-index 1 --start-date 2023-01-01 --verbose
```

### Arguments disponibles

```bash
python src/renewgy_parser.py --help
```

| Argument | Description | Obligatoire |
|----------|-------------|-------------|
| `--input` | Fichier Excel d'entrée | Oui (mode fichier unique) |
| `--output` | Fichier CSV de sortie | Oui (mode fichier unique) |
| `--batch-input` | Dossier d'entrée pour le traitement par lots | Oui (mode batch) |
| `--batch-output` | Dossier de sortie pour le traitement par lots | Oui (mode batch) |
| `--config` | Fichier de configuration EAN | **Toujours obligatoire** |
| `--sheet-index` | Index de la feuille Excel (défaut: 2) | Non |
| `--pattern` | Pattern de fichiers pour le mode batch | Non |
| `--start-date` | Date de début au format YYYY-MM-DD | Non |
| `--verbose` | Affichage détaillé | Non |
| `--quiet` | Affichage minimal | Non |

## ⚙️ Configuration

### Fichier de configuration EAN (Obligatoire)

**Important** : Un fichier de configuration EAN est **obligatoire** pour utiliser ce parser. Aucun mapping par défaut n'est inclus pour des raisons de sécurité.

**Étape obligatoire** : Créez un fichier `ean_config.json` dans le répertoire racine :

```json
{
  "example_ean_123456789": {
    "source_id": "123456",
    "variable_id": "789012",
    "description": "Example EAN mapping"
  },
  "another_ean_987654321": {
    "source_id": "987654",
    "variable_id": "321098",
    "description": "Another example EAN mapping"
  }
}
```

**Sécurité** : Ne jamais committer ce fichier dans votre repository. Il est automatiquement ignoré par `.gitignore`.

**Aide** : Un fichier exemple `ean_config.example.json` est fourni pour vous aider à créer votre configuration.

### Paramètres de configuration

Le parser utilise une configuration par défaut qui peut être ajustée :

- **sheet_index** : Index de la feuille Excel (défaut: 2)
- **header_row** : Ligne contenant l'en-tête EAN (défaut: 0)
- **header_col** : Colonne contenant l'en-tête EAN (défaut: 1)
- **data_start_row** : Première ligne des données (défaut: 5)
- **timestamp_col** : Colonne des timestamps (défaut: 0)
- **value_col** : Colonne des valeurs (défaut: 2)
- **min_rows** : Nombre de lignes minimales pour parser (défaut: 6)
- **min_cols** : Nombre de colonnes minimales pour parser (défaut: 3)
- **start_date** : Date de départ (Optionnel: 2025-01-01)

## 📊 Format de sortie CSV

Le fichier CSV généré contient les colonnes suivantes :

| Colonne | Description |
|---------|-------------|
| `date` | Timestamp de la mesure |
| `value` | Valeur mesurée |
| `meternumber` | Numéro EAN du compteur |
| `source_id` | Identifiant source du mapping |
| `source_serialnumber` | Numéro de série (vide par défaut) |
| `source_ean` | EAN source (vide par défaut) |
| `source_name` | Nom source (vide par défaut) |
| `mapping_config` | Configuration mapping (vide par défaut) |
| `variable_id` | Identifiant variable du mapping |

## 📁 Structure du projet

```txt
RenewgyParser/
├── csv_files/                     # Dossier de sortie (fixe).
│   └── .gitignore                 # Fichiers à ignorer par Git.
├── excel_files/                   # Dossier d'entrée (fixe).
│   └── .gitignore                 # Fichiers à ignorer par Git.
├── templates/
│   └── index.html                 # Template web interface.
├── .gitignore                     # Fichiers à ignorer par Git.
├── docker-compose.yml             # Services Docker.
├── Dockerfile                     # Configuration Docker.
├── ean_config.example.json        # Exemple de configuration EAN.
├── ean_config.json                # Configuration EAN (à créer).
├── launcher_docker.bat            # Launcher Docker (Windows).
├── launcher_docker.sh             # Launcher Docker (macOS/Linux).
├── launcher_python.bat            # Launcher Python (Windows).
├── launcher_python.sh             # Launcher Python (macOS/Linux).
├── LICENSE                        # Licence du projet.
├── README.md                      # Cette documentation.
├── renewgy_parser.py              # Parser CLI principal.
├── renewgy_parser_gui.py          # Interface web Flask.
└── requirements.txt               # Dépendances Python.
```

## 📝 Exemples d'utilisation

### Exemple 1 : Traitement simple

```bash
python src/renewgy_parser.py --input data.xlsx --output output.csv --config ean_config.json
```

### Exemple 2 : Traitement avec filtrage par date

```bash
python src/renewgy_parser.py --input data.xlsx --output output.csv --config ean_config.json --start-date 2023-01-01
```

### Exemple 3 : Traitement par lots avec configuration

```bash
python src/renewgy_parser.py --batch-input ./excel_files --batch-output ./csv_files --config ./ean_config.json --start-date 2023-06-01 --verbose
```

### Exemple 4 : Utilisation Docker complète

```bash
docker run --rm -v $(pwd)/excel_files:/parser/excel_files -v $(pwd)/csv_files:/parser/csv_files -v $(pwd):/parser/config renewgy-parser --batch-input /parser/excel_files --batch-output /parser/csv_files --config /parser/config/ean_config.json --start-date 2023-01-01
```

## 🔧 Dépannage

### Problèmes courants

1. **Erreur "Config file not found"**
   - Vérifiez que `ean_config.json` existe et est accessible
   - Utilisez un chemin absolu si nécessaire

2. **Erreur "No valid Excel files found"**
   - Vérifiez que vos fichiers ont l'extension `.xlsx` ou `.XLSX`
   - Placez vos fichiers dans le dossier `excel_files/`
   - Utilisez `--pattern` pour spécifier un pattern personnalisé

3. **Erreur "EAN not found in config"**
   - Ajoutez le mapping EAN manquant dans votre fichier de configuration
   - Vérifiez l'orthographe exacte de l'EAN

4. **Interface web ne démarre pas**
   - Vérifiez que le port 5001 n'est pas utilisé
   - Utilisez les launchers automatiques selon votre plateforme :
     - **macOS/Linux** : `./launcher_python.sh` ou `./launcher_docker.sh`
     - **Windows** : `launcher_python.bat` ou `launcher_docker.bat`

5. **Erreur "Port already in use" avec Docker**
   - Le port 5001 est configuré par défaut (au lieu de 5000 pour éviter les conflits avec AirPlay sur macOS)
   - Si le port 5001 est occupé, modifiez le port dans `docker-compose.yml`
   - Puis accédez à <http://localhost:5002>

6. **Problème d'environnement virtuel**
   - Le launcher Python gère automatiquement l'environnement virtuel
   - En cas de problème, supprimez le dossier `renewgy_parser_venv/` et relancez :
     - **macOS/Linux** : `./launcher_python.sh`
     - **Windows** : `launcher_python.bat`

### Logs et débogage

**macOS / Linux :**

```bash
# Affichage détaillé avec les launchers.
./launcher_python.sh   # Les logs sont automatiquement affichés.
./launcher_docker.sh   # Les logs Docker sont affichés.

# Affichage détaillé en mode CLI.
python src/renewgy_parser.py --verbose --input file.xlsx --output file.csv --config ean_config.json

# Logs Docker manuels.
docker-compose logs renewgy-web-interface
```

**Windows :**

```batch
REM Affichage détaillé avec les launchers.
launcher_python.bat   REM Les logs sont automatiquement affichés.
launcher_docker.bat   REM Les logs Docker sont affichés.

REM Affichage détaillé en mode CLI.
python src/renewgy_parser.py --verbose --input file.xlsx --output file.csv --config ean_config.json

REM Logs Docker manuels.
docker-compose logs renewgy-web-interface
```

## ⚠️ Gestion des erreurs

Le parser gère plusieurs types d'erreurs :

- **Fichiers manquants** : Vérification de l'existence des fichiers d'entrée
- **Structure Excel invalide** : Validation de la structure attendue
- **EAN non trouvé** : Vérification de l'existence dans le mapping
- **Données invalides** : Validation des types de données
- **Erreurs de format de date** : Validation des dates d'entrée

## 📋 Logging

Le parser utilise un système de logging configurable :

- **INFO** : Messages d'information (défaut)
- **DEBUG** : Messages détaillés (avec --verbose)
- **ERROR** : Erreurs uniquement (avec --quiet)
- **WARNING** : Avertissements

Format des logs :

```txt
2025-07-08 10:30:45 - renewgy_parser - INFO - Processing file: data.xlsx
2025-07-08 10:30:46 - renewgy_parser - INFO - Extracted EAN: 541448965000143475
2025-07-08 10:30:47 - renewgy_parser - INFO - Extracted 1000 data points
```

## 📅 Filtrage par date

Une fonctionnalité clé du parser est la possibilité de filtrer les données par date de début :

```bash
# Traiter uniquement les données à partir du 1er janvier 2023.
python src/renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --start-date 2023-01-01
```

Cette fonctionnalité est particulièrement utile pour :

- Éviter de traiter des données déjà présentes dans votre base de données
- Synchroniser les nouvelles données depuis la dernière mise à jour
- Optimiser les performances en ne traitant que les données nécessaires

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commitez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🔒 Sécurité

**Important** : Ne commitez jamais vos fichiers de configuration EAN ou vos données sensibles. Utilisez `.gitignore` pour exclure :

```gitignore
# Fichiers de configuration sensibles
ean_config.json
config/
*.env

# Données
excel_files/
csv_files/
*.xlsx
*.csv

# Environnement virtuel Python
renewgy_parser_venv/
```

## 📞 Support

Pour toute question ou problème :

1. Consultez cette documentation
2. Vérifiez les [problèmes courants](#problèmes-courants)
3. Ouvrez une issue sur [GitHub](https://github.com/BricePetit/RenewgyParser/issues)

## 📈 Changelog

### v1.0.0

- Parser initial avec support Excel vers CSV
- Validation des données et gestion d'erreurs
- Support du filtrage par date
- Traitement par lots
- Configuration EAN externe
- Support Docker
- Interface web moderne
- Workflow universel simplifié
- Launchers automatiques Python et Docker

---

## Auteur

**Brice Petit**  
Université Libre de Bruxelles (ULB)

Ce projet a été développé dans le cadre d'un projet de recherche PhD à l'Université Libre de Bruxelles (ULB).

- GitHub: [BricePetit](https://github.com/BricePetit)
- Projet: [RenewgyParser](https://github.com/BricePetit/RenewgyParser)
