# Renewgy Excel to CSV file

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Un parser robuste pour convertir les fichiers Excel de Renewgy en format CSV standardisé avec validation des données, gestion d'erreurs et capacités de logging avancées.

## 🚀 Fonctionnalités

- **Conversion Excel vers CSV** : Traitement automatique des fichiers Excel Renewgy
- **Validation des données** : Vérification de la structure et de l'intégrité des données
- **Filtrage par date** : Traitement des données à partir d'une date spécifique
- **Traitement par lots** : Traitement de plusieurs fichiers simultanément
- **Mapping EAN configurable** : Support des fichiers de configuration externes
- **Logging avancé** : Niveaux de logging configurables (verbose, normal, quiet)
- **Gestion d'erreurs robuste** : Traitement des erreurs avec rapports détaillés
- **Support Docker** : Déploiement containerisé disponible

## 📋 Prérequis

- Python 3.10 ou plus récent
- pandas
- openpyxl (pour la lecture des fichiers Excel)
- **Fichier de configuration EAN obligatoire** (voir Configuration)

## 🔧 Installation

### Installation locale

1. Clonez le repository :

```bash
git clone https://github.com/votre-username/renewgy-parser.git
cd renewgy-parser
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

### Installation avec Docker

1. Construisez l'image Docker :

```bash
docker build -t renewgy-parser .
```

## 📖 Utilisation

⚠️ **Important** : Toutes les commandes ci-dessous nécessitent l'argument `--config` avec un fichier de configuration EAN valide. Consultez la section [Configuration](#%EF%B8%8F-configuration) pour créer votre fichier de configuration.

### Utilisation locale

#### Traitement d'un fichier unique

```bash
# Traitement basique (nécessite un fichier de configuration).
python src/renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json

# Avec filtrage par date.
python src/renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --start-date 2023-01-01

# Avec logging verbose.
python src/renewgy_parser.py --input input.xlsx --output output.csv --config ean_config.json --verbose
```

#### Traitement par lots

```bash
# Traitement de tous les fichiers Excel dans un répertoire.
# Note: détecte automatiquement les fichiers .xlsx et .XLSX.
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

### Utilisation avec Docker

#### Traitement d'un fichier unique

```bash
# Monter les répertoires et exécuter le parser (config obligatoire).
docker run --rm -v $(pwd)/excel_files:/parser/input -v $(pwd)/csv_files:/parser/output -v $(pwd):/parser/config renewgy-parser --input /parser/input/fichier.xlsx --output /parser/output/fichier.csv --config /parser/config/ean_config.json
```

#### Traitement par lots

```bash
# Traitement de tous les fichiers Excel (config obligatoire).
docker run --rm -v $(pwd)/excel_files:/parser/input -v $(pwd)/csv_files:/parser/output -v $(pwd):/parser/config renewgy-parser --batch-input /parser/input --batch-output /parser/output --config /parser/config/ean_config.json
```

#### Avec options avancées

```bash
# Utilisation avec filtrage par date et logging verbose.
docker run --rm -v $(pwd)/excel_files:/parser/input -v $(pwd)/csv_files:/parser/output -v $(pwd):/parser/config renewgy-parser --batch-input /parser/input --batch-output /parser/output --config /parser/config/ean_config.json --start-date 2023-01-01 --verbose
```

## ⚙️ Configuration

### Fichier de configuration EAN (Obligatoire)

**Important** : Un fichier de configuration EAN est **obligatoire** pour utiliser ce parser. Aucun mapping par défaut n'est inclus pour des raisons de sécurité.

🔧 **Étape obligatoire** : Avant d'utiliser le parser, vous devez créer un fichier `ean_config.json` dans le répertoire racine du projet.

Créez un fichier `ean_config.json` pour définir vos mappings EAN :

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

⚠️ **Sécurité** : Ne jamais committer ce fichier dans votre repository. Il est automatiquement ignoré par `.gitignore`.

💡 **Aide** : Un fichier exemple `ean_config.example.json` est fourni pour vous aider à créer votre configuration.

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

## 🔍 Options de ligne de commande

### Arguments principaux

- `--input` : Fichier Excel d'entrée (mode fichier unique)
- `--output` : Fichier CSV de sortie (mode fichier unique)
- `--batch-input` : Répertoire contenant les fichiers Excel (mode batch)
- `--batch-output` : Répertoire de sortie des fichiers CSV (mode batch)
- `--config` : **OBLIGATOIRE** - Chemin vers le fichier de configuration JSON

### Options de configuration

- `--sheet-index` : Index de la feuille Excel à traiter (défaut: 2)
- `--pattern` : Pattern de fichiers pour le mode batch (défaut: *.xlsx - détecte automatiquement .xlsx et .XLSX)
- `--start-date` : Date de début pour le filtrage (format: YYYY-MM-DD)

### Options de logging

- `--verbose` : Active le logging détaillé
- `--quiet` : Supprime tous les messages sauf les erreurs

## 🐳 Docker

### Dockerfile

Le projet inclut un Dockerfile pour faciliter le déploiement :

```dockerfile
FROM python:3.13-slim

WORKDIR /parser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY ean_config.json .

ENTRYPOINT ["python", "src/renewgy_parser.py"]
```

### Docker Compose (optionnel)

Pour une utilisation plus complexe, vous pouvez créer un `docker-compose.yml` :

```yaml
version: '3.8'

services:
  renewgy-parser:
    build: .
    volumes:
      - ./excel_files:/parser/input
      - ./csv_files:/parser/output
      - ./config:/parser/config
    command: --batch-input /parser/input --batch-output /parser/output --config /parser/config/ean_config.json
```

## 🔧 Structure du projet

```
renewgy-parser/
├── src/
│   └── renewgy_parser.py          # Parser principal
├── excel_files/                   # Fichiers Excel d'entrée
├── csv_files/                     # Fichiers CSV de sortie
├── Dockerfile                     # Configuration Docker
├── requirements.txt               # Dépendances Python
├── ean_config.example.json        # Exemple de configuration EAN
├── ean_config.json                # Configuration EAN (à créer)
├── .gitignore                     # Fichiers à ignorer par Git
└── README.md                      # Ce fichier
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
python src/renewgy_parser.py --batch-input ./input_files --batch-output ./output_files --config ./my_ean_config.json --start-date 2023-06-01 --verbose
```

### Exemple 4 : Utilisation Docker complète

```bash
docker run --rm -v $(pwd)/data:/parser/data -v $(pwd):/parser/config renewgy-parser --batch-input /parser/data/input --batch-output /parser/data/output --config /parser/config/ean_config.json --start-date 2023-01-01
```

## 🚨 Gestion des erreurs

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

```
2025-07-03 10:30:45 - renewgy_parser - INFO - Processing file: data.xlsx
2025-07-03 10:30:46 - renewgy_parser - INFO - Extracted EAN: 541448965000143475
2025-07-03 10:30:47 - renewgy_parser - INFO - Extracted 1000 data points
```

## 🔄 Filtrage par date

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

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commitez vos changements (`git commit -am 'Ajout d'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

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
```

## 📞 Support

Pour toute question ou problème :

1. Consultez la documentation
2. Vérifiez les issues existantes
3. Créez une nouvelle issue avec :
   - Description détaillée du problème
   - Étapes pour reproduire
   - Logs d'erreur
   - Environnement (Python, OS, etc.)

## 🔄 Changelog

### v1.0.0

- Parser initial avec support Excel vers CSV
- Validation des données et gestion d'erreurs
- Support du filtrage par date
- Traitement par lots
- Configuration EAN externe
- Support Docker

---

**Note** : Ce parser a été développé spécifiquement pour les fichiers Excel Renewgy. Assurez-vous que vos fichiers respectent le format attendu avant traitement.

## 👨‍💻 Développeur

**Brice Petit** - *Développeur principal* - [GitHub](https://github.com/BricePetit)

Ce projet a été développé dans le cadre d'un projet de recherche PhD à l'Université Libre de Bruxelles (ULB).
