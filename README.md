# Renewgy Excel to CSV Parser

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Docker](https://img.shields.io/badge/docker-supported-blue.svg)
![macOS](https://img.shields.io/badge/macOS-compatible-000000?logo=apple&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-compatible-FCC624?logo=linux&logoColor=black)
![Windows](https://img.shields.io/badge/Windows-compatible-0078D6?logo=windows&logoColor=white)

Un parser **ultra-robuste** et **intelligent** pour convertir les fichiers Excel de Renewgy en format CSV standardisé. Solution enterprise avec **détection automatique avancée**, **gestion complète des EAN bi-horaires** et **interface moderne** conçue pour l'efficacité, la simplicité d'utilisation et l'intégration transparente dans des workflows de traitement de données.

## ✨ Caractéristiques principales

- **🧠 Intelligence automatique** : Détection dynamique des colonnes, structure et format des fichiers Excel
- **⚡ Gestion EAN bi-horaires** : Support automatique des tarifs peak/off-peak avec génération de fichiers séparés
- **🎯 Sélection du type de puissance** : Choix entre consommation active, inductive ou capacitive
- **📝 Noms de fichiers intelligents** : Génération automatique avec suffixes (`_active`, `_inductive`, `_capacitive`, `_peak`, `_offpeak`)
- **🔄 Workflow universel simplifié** : Dossiers d'entrée et de sortie fixes (`excel_files/` → `csv_files/`)
- **🌐 Compatibilité multiplateforme** : Fonctionne sur macOS, Linux et Windows
- **🚀 Launchers intelligents** : Automatisation complète de l'installation et du déploiement
- **💻 Interface web moderne** : Design ergonomique avec feedback en temps réel
- **📦 Traitement par lots intelligent** : Personnalisation individuelle par fichier (nom, date, feuille, type de puissance)
- **🔧 Double mode d'utilisation** : Interface web conviviale ou CLI pour l'automatisation
- **⚙️ Configuration zéro** : Workflow entièrement automatisé avec détection intelligente
- **🛡️ Robustesse enterprise** : Validation rigoureuse, gestion d'erreurs et logging professionnel
- **🐳 Prêt pour la production** : Support Docker avec launcher automatique

## 🔧 Fonctionnalités détaillées

### 🎯 Sélection intelligente du type de puissance

- **Types supportés** : Active, Inductive (réactive), Capacitive (réactive)
- **Détection automatique** : Reconnaissance des colonnes de puissance dans les fichiers Excel
- **Noms de fichiers automatiques** : Suffixes `_active`, `_inductive`, `_capacitive` pour éviter l'écrasement
- **Interface utilisateur** : Sélection dynamique avec mise à jour automatique du nom de fichier

### ⚡ Gestion avancée des EAN bi-horaires

- **Détection automatique** : Reconnaissance des EAN avec tarification peak/off-peak
- **Configuration flexible** : Règles horaires personnalisables via `ean_config.json`
- **Génération de fichiers séparés** : Automatiquement `_peak.csv` et `_offpeak.csv`
- **Règles horaires par défaut** :
  - **Peak** : 07h00-22h00 (lundi-vendredi uniquement)
  - **Off-peak** : 22h00-07h00 (lundi-vendredi) + tout le weekend

### 🧠 Détection automatique intelligente

- **Structure dynamique** : Détection automatique des en-têtes et début des données
- **Colonnes flexibles** : Reconnaissance automatique des colonnes timestamp et valeurs
- **Validation robuste** : Vérification de l'intégrité des données et de la structure
- **Formats multiples** : Support de diverses structures de fichiers Excel Renewgy

### 📊 Traitement et conversion

- **Conversion Excel vers CSV** : Traitement automatique avec validation complète
- **Filtrage par date personnalisable** : Traitement des données à partir d'une date spécifique
- **Sélection de feuille** : Configuration de l'index de feuille Excel à traiter
- **Mapping EAN configurable** : Support des fichiers de configuration externes sécurisés
- **Logging multi-niveaux** : Verbose, normal, quiet selon vos besoins

### 🎨 Interface utilisateur avancée

- **Interface responsive** : Fonctionne sur desktop, tablette et mobile
- **Mode single et batch** : Traitement d'un fichier ou par lots
- **Personnalisation en temps réel** : Options par fichier avec prévisualisation
- **Feedback instantané** : Messages d'état et indicateurs de progression
- **Gestion d'erreurs intelligente** : Rapports détaillés avec solutions suggérées

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
- **Type de puissance** : Sélection entre Active, Inductive ou Capacitive
- **Nom de sortie intelligent** : Génération automatique avec suffixe selon le type (`_active`, `_inductive`, `_capacitive`)
- **EAN bi-horaires** : Génération automatique de deux fichiers `_peak.csv` et `_offpeak.csv`
- **Filtrage par date** : Traitement à partir d'une date spécifique
- **Configuration de feuille** : Sélection de l'index de feuille Excel
- **Options avancées** : Accès complet aux paramètres de configuration

**Mode Batch (Traitement par lots) :**

- **Traitement multiple** : Affichage et traitement de tous les fichiers Excel
- **Personnalisation individuelle** :
  - **Type de puissance** : Choix par fichier avec mise à jour du nom
  - **Nom de sortie** : Génération automatique avec suffixes intelligents
  - **Date de début** : Filtrage personnalisé par fichier
  - **Index de feuille** : Configuration spécifique par fichier
- **Gestion EAN bi-horaires** : Traitement automatique avec fichiers séparés
- **Traitement simultané** : Processus unifié pour tous les fichiers sélectionnés

**Fonctionnalités communes :**

- **Monitoring en temps réel** : Suivi détaillé du traitement
- **Interface responsive** : Compatible desktop, tablette et mobile
- **Feedback instantané** : Messages d'état et indicateurs de progression
- **Gestion d'erreurs** : Rapports détaillés avec solutions suggérées

### 💻 Interface en Ligne de Commande

Pour l'intégration dans des scripts ou l'automatisation avancée. Toutes les nouvelles fonctionnalités sont disponibles via CLI.

#### Traitement d'un fichier unique

```bash
# Traitement basique avec type de puissance active (défaut).
python renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json

# Sélection du type de puissance (active, inductive, capacitive).
python renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --power-type inductive

# Le nom de fichier sera automatiquement suffixé : output_inductive.csv
# Pour les EAN bi-horaires : output_inductive_peak.csv et output_inductive_offpeak.csv

# Avec filtrage par date.
python renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --start-date 2023-01-01 --power-type capacitive

# Avec logging verbose.
python renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --verbose --power-type active
```

#### Traitement par lots

```bash
# Traitement de tous les fichiers Excel avec type de puissance par défaut.
python renewgy_parser.py --batch-input ./excel_files --batch-output ./csv_files --config ean_config.json

# Avec type de puissance spécifique pour tous les fichiers.
python renewgy_parser.py --batch-input ./excel_files --batch-output ./csv_files --config ean_config.json --power-type inductive

# Avec filtrage par date.
python renewgy_parser.py --batch-input ./excel_files --batch-output ./csv_files --config ean_config.json --start-date 2023-06-01 --power-type capacitive

# Avec pattern personnalisé.
python renewgy_parser.py --batch-input ./excel_files --batch-output ./csv_files --config ean_config.json --pattern "*specific*" --power-type active
```

#### Configuration et options avancées

```bash
# Type de puissance avec fichier de configuration EAN personnalisé.
python renewgy_parser.py --input input.xlsx --output output.csv --config mon_config.json --power-type inductive

# Spécification de l'index de la feuille Excel avec type de puissance.
python renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --sheet-index 0 --power-type capacitive

# Combinaison de plusieurs options avec nouvelles fonctionnalités.
python renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --sheet-index 1 --start-date 2023-01-01 --power-type active --verbose
```

#### Exemples de gestion automatique des noms de fichiers

```bash
# Fichier standard avec puissance active.
# Input: data.xlsx → Output: data_active.csv
python renewgy_parser.py --input data.xlsx --output data.csv --config ean_config.json --power-type active

# EAN bi-horaire avec puissance inductive.
# Input: ean_bihoraire.xlsx → Output: ean_bihoraire_inductive_peak.csv + ean_bihoraire_inductive_offpeak.csv
python renewgy_parser.py --input ean_bihoraire.xlsx --output ean_bihoraire.csv --config ean_config.json --power-type inductive

# Traitement par lots avec suffixes automatiques.
# Tous les fichiers auront le suffixe _capacitive, et les EAN bi-horaires auront _peak/_offpeak en plus
python renewgy_parser.py --batch-input ./excel_files --batch-output ./csv_files --config ean_config.json --power-type capacitive
```

### Arguments disponibles

```bash
python renewgy_parser.py --help
```

| Argument | Description | Obligatoire | Valeurs possibles |
|----------|-------------|-------------|-------------------|
| `--input` | Fichier Excel d'entrée | Oui (mode fichier unique) | Chemin vers fichier .xlsx |
| `--output` | Fichier CSV de sortie | Oui (mode fichier unique) | Chemin vers fichier .csv |
| `--batch-input` | Dossier d'entrée pour le traitement par lots | Oui (mode batch) | Chemin vers dossier |
| `--batch-output` | Dossier de sortie pour le traitement par lots | Oui (mode batch) | Chemin vers dossier |
| `--config` | Fichier de configuration EAN | **Toujours obligatoire** | Chemin vers fichier .json |
| `--power-type` | Type de puissance à traiter | Non | `active`, `inductive`, `capacitive` (défaut: `active`) |
| `--sheet-index` | Index de la feuille Excel | Non | Entier (défaut: 2) |
| `--pattern` | Pattern de fichiers pour le mode batch | Non | Pattern glob (ex: `*specific*`) |
| `--start-date` | Date de début au format YYYY-MM-DD | Non | Date ISO (ex: `2023-01-01`) |
| `--verbose` | Affichage détaillé | Non | Flag (pas de valeur) |
| `--quiet` | Affichage minimal | Non | Flag (pas de valeur) |

**Nouvelles fonctionnalités** :

- **`--power-type`** : Définit le type de puissance et génère automatiquement le suffixe approprié
- **Gestion EAN bi-horaires** : Détection automatique, génération de fichiers `_peak` et `_offpeak`
- **Noms intelligents** : Suffixe automatique selon le type de puissance pour éviter l'écrasement

## ⚙️ Configuration

### Fichier de configuration EAN (Obligatoire)

**Important** : Un fichier de configuration EAN est **obligatoire** pour utiliser ce parser. Aucun mapping par défaut n'est inclus pour des raisons de sécurité.

**Étape obligatoire** : Créez un fichier `ean_config.json` dans le répertoire racine :

```json
{
  "example_ean_standard": {
    "source_id": "123456",
    "variable_id": "789012",
    "description": "Example standard EAN mapping"
  },
  "example_ean_bihoraire_peak": {
    "source_id": "987654",
    "variable_id": "321098", 
    "description": "Example bi-hourly EAN mapping (peak hours)"
  },
  "example_ean_bihoraire_offpeak": {
    "source_id": "987654",
    "variable_id": "321099",
    "description": "Example bi-hourly EAN mapping (off-peak hours)"
  }
}
```

**Nouvelles fonctionnalités de configuration** :

- **`is_bihoraire`** : Définit si l'EAN utilise la tarification bi-horaire (peak/off-peak)
- **`peak_hours`** : Configuration des heures de pointe par jour de la semaine (optionnel)
- **Génération automatique** : Si `is_bihoraire: true`, génère automatiquement deux fichiers CSV
- **Heures par défaut** : Si `peak_hours` n'est pas spécifié, utilise les règles standard belges

**Règles horaires par défaut pour les EAN bi-horaires** :

- **Peak** : 07h00-22h00 (lundi-vendredi uniquement)
- **Off-peak** : 22h00-07h00 (lundi-vendredi) + tout le weekend (samedi et dimanche complets)

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

### Nomenclature des fichiers de sortie

Le parser génère automatiquement des noms de fichiers intelligents selon le contexte :

#### EAN standard (tarif unique)

- **Puissance active** : `fichier_active.csv`
- **Puissance inductive** : `fichier_inductive.csv`
- **Puissance capacitive** : `fichier_capacitive.csv`

#### EAN bi-horaires (tarification peak/off-peak)

- **Puissance active** : `fichier_active_peak.csv` + `fichier_active_offpeak.csv`
- **Puissance inductive** : `fichier_inductive_peak.csv` + `fichier_inductive_offpeak.csv`
- **Puissance capacitive** : `fichier_capacitive_peak.csv` + `fichier_capacitive_offpeak.csv`

### Structure des fichiers CSV

Le fichier CSV généré contient les colonnes suivantes :

| Colonne | Description |
|---------|-------------|
| `date` | Timestamp de la mesure |
| `value` | Valeur mesurée (selon le type de puissance sélectionné) |
| `meternumber` | Numéro EAN du compteur |
| `source_id` | Identifiant source du mapping |
| `source_serialnumber` | Numéro de série (vide par défaut) |
| `source_ean` | EAN source (vide par défaut) |
| `source_name` | Nom source (vide par défaut) |
| `mapping_config` | Configuration mapping (vide par défaut) |
| `variable_id` | Identifiant variable du mapping |

### Exemples de données

**EAN standard (puissance active)** :

```csv
date,value,meternumber,source_id,source_serialnumber,source_ean,source_name,mapping_config,variable_id
2023-01-01 00:00:00,1.25,541448965000143475,123456,,,,,789012
2023-01-01 00:15:00,1.30,541448965000143475,123456,,,,,789012
```

**EAN bi-horaire (puissance inductive, fichier peak)** :

```csv
date,value,meternumber,source_id,source_serialnumber,source_ean,source_name,mapping_config,variable_id
2023-01-01 07:00:00,0.85,987654321000000123,987654,,,,,321098
2023-01-01 07:15:00,0.92,987654321000000123,987654,,,,,321098
```

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

### Exemple 1 : Traitement simple avec puissance active

```bash
python renewgy_parser.py --input data.xlsx --output output.csv --config ean_config.json --power-type active
# Résultat : output_active.csv (ou output_active_peak.csv + output_active_offpeak.csv si EAN bi-horaire)
```

### Exemple 2 : Traitement avec puissance inductive et filtrage par date

```bash
python renewgy_parser.py --input data.xlsx --output output.csv --config ean_config.json --power-type inductive --start-date 2023-01-01
# Résultat : output_inductive.csv avec données à partir du 1er janvier 2023
```

### Exemple 3 : Traitement par lots avec puissance capacitive

```bash
python renewgy_parser.py --batch-input ./excel_files --batch-output ./csv_files --config ./ean_config.json --power-type capacitive --start-date 2023-06-01 --verbose
# Résultat : Tous les fichiers Excel traités avec suffixe _capacitive
```

### Exemple 4 : EAN bi-horaire avec puissance inductive

```bash
python renewgy_parser.py --input ean_bihoraire.xlsx --output ean_bihoraire.csv --config ean_config.json --power-type inductive
# Résultat automatique : 
# - ean_bihoraire_inductive_peak.csv (données heures pleines)
# - ean_bihoraire_inductive_offpeak.csv (données heures creuses)
```

### Exemple 5 : Interface web avec Docker

```bash
# Lancement automatique avec configuration complète
./launcher_docker.sh

# Ou manuellement
docker run --rm -v $(pwd)/excel_files:/renewgy/excel_files -v $(pwd)/csv_files:/renewgy/csv_files -v $(pwd)/ean_config.json:/renewgy/ean_config.json -p 5001:5000 renewgy-parser
# Interface accessible sur http://localhost:5001
```

### Exemple 6 : Traitement automatisé en production

```bash
# Script de traitement quotidien avec toutes les nouvelles fonctionnalités
python renewgy_parser.py \
  --batch-input /data/excel_files \
  --batch-output /data/csv_files \
  --config /config/ean_config.json \
  --power-type active \
  --start-date $(date -d "yesterday" +%Y-%m-%d) \
  --verbose
# Traite automatiquement tous les nouveaux fichiers avec les données d'hier
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
   - Pour les EAN bi-horaires, ajoutez `"is_bihoraire": true` dans la configuration

4. **Erreur "Power type column not found"**
   - Vérifiez que le type de puissance sélectionné existe dans votre fichier Excel
   - Les colonnes acceptées : `Active Energy`, `Inductive Energy`, `Capacitive Energy`
   - Utilisez `--verbose` pour voir les colonnes détectées

5. **Problème avec les EAN bi-horaires**
   - Vérifiez la configuration `"is_bihoraire": true` dans `ean_config.json`
   - Les règles horaires par défaut sont appliquées si `peak_hours` n'est pas spécifié
   - Deux fichiers sont générés automatiquement : `_peak.csv` et `_offpeak.csv`

6. **Interface web ne démarre pas**
   - Vérifiez que le port 5001 n'est pas utilisé
   - Utilisez les launchers automatiques selon votre plateforme :
     - **macOS/Linux** : `./launcher_python.sh` ou `./launcher_docker.sh`
     - **Windows** : `launcher_python.bat` ou `launcher_docker.bat`

7. **Erreur "Port already in use" avec Docker**
   - Le port 5001 est configuré par défaut (au lieu de 5000 pour éviter les conflits avec AirPlay sur macOS)
   - Si le port 5001 est occupé, modifiez le port dans `docker-compose.yml`
   - Puis accédez à <http://localhost:5002>

8. **Problème d'environnement virtuel**
   - Le launcher Python gère automatiquement l'environnement virtuel
   - En cas de problème, supprimez le dossier `renewgy_parser_venv/` et relancez :
     - **macOS/Linux** : `./launcher_python.sh`
     - **Windows** : `launcher_python.bat`

9. **Fichiers de sortie non générés**
   - Vérifiez les permissions d'écriture dans le dossier `csv_files/`
   - Pour les EAN bi-horaires, vérifiez que les données contiennent bien des heures de pointe et creuses
   - Utilisez `--verbose` pour voir le détail du traitement

10. **Détection automatique échoue**
    - La détection se base sur des mots-clés standard dans les en-têtes
    - Si votre fichier Excel a une structure non-standard, contactez le support
    - Utilisez `--verbose` pour voir les colonnes et structures détectées

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

### v2.0.0 - Édition Intelligence & Robustesse (Juillet 2025)

**🚀 Nouvelles fonctionnalités majeures :**

- **🎯 Sélection du type de puissance** : Choix entre Active, Inductive et Capacitive
- **⚡ Gestion complète des EAN bi-horaires** : Support automatique peak/off-peak avec fichiers séparés
- **🧠 Détection automatique intelligente** : Colonnes, structure et format détectés dynamiquement
- **📝 Noms de fichiers intelligents** : Suffixes automatiques selon le type de puissance et le mode horaire
- **🔄 Interface web améliorée** : Sélection dynamique avec feedback en temps réel

**🛡️ Améliorations de robustesse :**

- **Détection dynamique** des en-têtes et début des données
- **Validation robuste** de la structure des fichiers Excel
- **Gestion d'erreurs avancée** avec messages détaillés
- **Logging professionnel** avec niveaux configurables

**💻 Interface utilisateur :**

- **Mode batch amélioré** : Configuration individuelle par fichier
- **Mise à jour automatique** des noms lors du changement de type de puissance
- **Feedback instantané** pour toutes les opérations
- **Interface responsive** optimisée

**🔧 Technique :**

- **Type hints complets** et documentation professionnelle
- **Code modulaire** et maintenable
- **Tests CLI et web** validés pour tous les cas d'usage
- **Configuration flexible** pour les règles horaires personnalisées

### v1.0.0 - Version Initiale

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
