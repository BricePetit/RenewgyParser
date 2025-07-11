#!/usr/bin/env python3

"""
Renewgy Parser GUI - Web Interface with Integrated Parser.

Complete web interface with integrated parser (no external Docker dependency).
"""
__title__: str = "renewgy_parser_gui"
__version__: str = "2.0.0"
__version_info__ = (2, 0, 0)
__release_date__: str = "2025-01-11"
__author__: str = "Brice Petit"
__license__: str = "MIT"

# ----------------------------------------------------------------------------------------------- #
# ------------------------------------------- IMPORTS ------------------------------------------- #
# ----------------------------------------------------------------------------------------------- #

# Standard library imports.
from datetime import datetime
import logging
import os
from pathlib import Path
import platform
import re
import sys
from typing import Dict, Any, Union

# Add the current directory to the system path.
sys.path.append(os.path.dirname(__file__))

# Third party imports.
from flask import Flask, render_template, request, jsonify
import pandas as pd

# Local imports.
try:
    from renewgy_parser import (
        load_ean_mapping_from_file,
        parse_renewgy_excel_to_csv,
        process_multiple_files,
        ParserConfig
    )
    PARSER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Attention: Impossible d'importer le parser: {e}")
    PARSER_AVAILABLE = False

# ----------------------------------------------------------------------------------------------- #
# -------------------------------------- GLOBAL VARIABLES --------------------------------------- #
# ----------------------------------------------------------------------------------------------- #

app = Flask(__name__)

# Reduce log verbosity.
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Automatic configuration based on the OS.
SYSTEM: str = platform.system().lower()
WORK_DIR: str = '/app' if os.path.exists('/app') else os.getcwd()

# Working directories.
FOLDERS: Dict[str, str] = {
    'input': os.path.join(WORK_DIR, 'excel_files'),
    'output': os.path.join(WORK_DIR, 'csv_files'), 
    'config': WORK_DIR
}

# Create directories if they do not exist.
for folder in FOLDERS.values():
    os.makedirs(folder, exist_ok=True)

# ----------------------------------------------------------------------------------------------- #
# ---------------------------------------- ROUTE HANDLERS --------------------------------------- #
# ----------------------------------------------------------------------------------------------- #


@app.route('/')
def index() -> str:
    """
    Main page of the web interface.

    :return:    Rendered HTML template for the main page.
    """
    return render_template('index.html')


@app.route('/api/process', methods=['POST'])
def process_files() -> Union[tuple, Any]:
    """
    API endpoint to process files with the integrated parser.

    Handles both single file processing and batch processing modes.

    :return:    JSON response indicating success or error with HTTP status code.
    """
    try:
        if not PARSER_AVAILABLE:
            return jsonify({'error': 'Parser non disponible - vérifiez l\'installation'}), 500
        data = request.json
        mode = data.get('mode', 'single')
        # Validate required parameters based on mode.
        if mode == 'single':
            required_fields = ['source', 'destination', 'config']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Paramètre manquant: {field}'}), 400
        elif mode == 'batch':
            if not data.get('config'):
                return jsonify({'error': 'Paramètre manquant: config'}), 400
        else:
            return jsonify({'error': f'Mode invalide: {mode}'}), 400
        # Process files with the integrated parser.
        result = process_with_integrated_parser(data)
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Traitement terminé avec succès',
                'output': data.get('destination', 'Mode batch'),
                'details': result.get('details', '')
            })
        return jsonify({'error': result['error']}), 500
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500


@app.route('/api/status')
def get_status() -> Union[tuple, Any]:
    """
    Get the status of the parser and system.

    :return:    JSON response with system information, parser availability, and folder paths.
    """
    try:
        config_exists = os.path.exists(os.path.join(FOLDERS['config'], 'ean_config.json'))
        return jsonify({
            'system': SYSTEM,
            'parser_available': PARSER_AVAILABLE,
            'config_exists': config_exists,
            'folders': FOLDERS
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files')
def list_files() -> Union[tuple, Any]:
    """
    List available files in the input and output directories.

    :return:    JSON response with lists of Excel and CSV files.
    """
    try:
        excel_files = []
        csv_files = []
        # List Excel files in input directory.
        input_dir = Path(FOLDERS['input'])
        if input_dir.exists():
            for ext in ['*.xlsx', '*.XLSX', '*.xls', '*.XLS']:
                excel_files.extend([f.name for f in input_dir.glob(ext)])
        # List CSV files in output directory.
        output_dir = Path(FOLDERS['output'])
        if output_dir.exists():
            csv_files = [f.name for f in output_dir.glob('*.csv')]
        return jsonify({
            'excel_files': sorted(excel_files),
            'csv_files': sorted(csv_files),
            'folders': FOLDERS
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ----------------------------------------------------------------------------------------------- #
# ---------------------------------------- UTILITY FUNCTIONS ------------------------------------ #
# ----------------------------------------------------------------------------------------------- #


def has_peak_offpeak_variants(ean: str, ean_mapping: Dict[str, Any]) -> bool:
    """
    Check if an EAN has peak/offpeak variants in the mapping.

    :param ean:         The base EAN identifier.
    :param ean_mapping: EAN mapping dictionary.

    :return:            True if the EAN has both peak and offpeak variants.
    """
    peak_key = f"{ean}_peak"
    offpeak_key = f"{ean}_offpeak"
    return peak_key in ean_mapping and offpeak_key in ean_mapping


def extract_ean_from_filename(filename: str) -> str:
    """
    Extract EAN from filename using regex pattern matching.

    :param filename:    The filename to extract EAN from.

    :return:            Extracted EAN or empty string if not found.
    """
    # Look for 18-digit pattern that represents an EAN.
    match = re.search(r'\d{18}', filename)
    return match.group(0) if match else ""


def process_with_integrated_parser(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process files with the integrated Renewgy parser.

    :param data:    JSON data containing parameters for processing.

    :return:        Dictionary with success status and details or error message.
    """
    try:
        mode = data.get('mode', 'single')
        config_path = Path(FOLDERS['config']) / 'ean_config.json'
        # Load EAN configuration.
        try:
            ean_mapping = load_ean_mapping_from_file(config_path)
        except FileNotFoundError:
            return {
                'success': False, 
                'error': f'Fichier de configuration EAN non trouvé: {config_path}\\n'
                        'Créez ce fichier à partir de ean_config.example.json'
            }
        except Exception as e:
            return {'success': False, 'error': f'Erreur de configuration EAN: {str(e)}'}
        # Setup parser configuration.
        config = ParserConfig()
        # Parse start date if provided.
        if data.get('startDate'):
            try:
                config.start_date = datetime.strptime(data['startDate'], '%Y-%m-%d')
            except ValueError:
                return {'success': False, 'error': 'Format de date invalide (utilisez YYYY-MM-DD)'}
        # Parse sheet index if provided.
        if data.get('sheetIndex'):
            try:
                config.sheet_index = int(data['sheetIndex'])
            except ValueError:
                return {'success': False, 'error': 'Index de feuille invalide'}
        consumption_type = data.get('consumptionType', 'MEASURED ACTIVE CONSUMPTION')
        # Route to appropriate processing mode.
        return (
            _process_single_file(data, ean_mapping, config, consumption_type)
            if mode == 'single' else
            _process_batch_files(data, ean_mapping, config, consumption_type)
        )
    except Exception as e:
        return {'success': False, 'error': f'Erreur générale: {str(e)}'}


def _process_single_file(
    data: Dict[str, Any], ean_mapping: Dict[str, Any],  config: ParserConfig, consumption_type: str
) -> Dict[str, Any]:
    """
    Process a single Excel file.

    :param data:                Request data containing file paths.
    :param ean_mapping:         EAN mapping dictionary.
    :param config:              Parser configuration.
    :param consumption_type:    Type of consumption to extract.

    :return:                    Processing result dictionary.
    """
    input_path = Path(FOLDERS['input']) / data['source']
    output_path = Path(FOLDERS['output']) / data['destination']

    if not input_path.exists():
        return {'success': False, 'error': f'Fichier source non trouvé: {input_path}'}
    # Check if this is a bi-hourly EAN.
    ean = extract_ean_from_filename(data['source'])
    is_bi_hourly = has_peak_offpeak_variants(ean, ean_mapping) if ean else False
    try:
        # Process the Excel file.
        parse_renewgy_excel_to_csv(input_path, output_path, ean_mapping, config, consumption_type)
        # Verify output files were created and count rows.
        return (
            _verify_bi_hourly_output(output_path)
            if is_bi_hourly else
            _verify_standard_output(output_path)
        )
    except Exception as e:
        return {'success': False, 'error': f'Erreur de traitement: {str(e)}'}


def _verify_bi_hourly_output(output_path: Path) -> Dict[str, Any]:
    """
    Verify bi-hourly output files were created and count rows.

    :param output_path: Base output path.
    :return:            Verification result dictionary.
    """
    peak_output_path = output_path.parent / f"{output_path.stem}_peak{output_path.suffix}"
    offpeak_output_path = output_path.parent / f"{output_path.stem}_offpeak{output_path.suffix}"
    if peak_output_path.exists() and offpeak_output_path.exists():
        try:
            peak_df = pd.read_csv(peak_output_path)
            offpeak_df = pd.read_csv(offpeak_output_path)
            peak_rows = len(peak_df)
            offpeak_rows = len(offpeak_df)
        except Exception:
            peak_rows = offpeak_rows = "?"
        return {
            'success': True,
            'details': (
                f'Fichier traité (EAN bi-horaire): {peak_rows} lignes peak '
                f'vers {peak_output_path.name}, {offpeak_rows} lignes offpeak '
                f'vers {offpeak_output_path.name}'
            )
        }
    missing_files = []
    if not peak_output_path.exists():
        missing_files.append("peak")
    if not offpeak_output_path.exists():
        missing_files.append("offpeak")
    return {'success': False, 'error': f'Fichiers de sortie manquants: {", ".join(missing_files)}'}


def _verify_standard_output(output_path: Path) -> Dict[str, Any]:
    """
    Verify standard output file was created and count rows.

    :param output_path: Output file path.

    :return:            Verification result dictionary.
    """
    if output_path.exists():
        try:
            result_df = pd.read_csv(output_path)
            rows_count = len(result_df)
        except Exception:
            rows_count = "?"
        return {
            'success': True,
            'details': f'Fichier traité: {rows_count} lignes exportées vers {output_path.name}'
        }
    return {'success': False, 'error': 'Le fichier de sortie n\'a pas été créé'}


def _process_batch_files(
    data: Dict[str, Any], ean_mapping: Dict[str, Any], config: ParserConfig, consumption_type: str
) -> Dict[str, Any]:
    """
    Process multiple files in batch mode.

    :param data:                Request data containing batch parameters.
    :param ean_mapping:         EAN mapping dictionary.
    :param config:              Parser configuration.
    :param consumption_type:    Type of consumption to extract.

    :return:                    Batch processing result dictionary.
    """
    input_dir = Path(FOLDERS['input'])
    output_dir = Path(FOLDERS['output'])

    if not input_dir.exists():
        return {'success': False, 'error': f'Dossier source non trouvé: {input_dir}'}

    try:
        # Check for custom parameters.
        custom_filenames = data.get('batchOutputFiles', {})
        custom_dates = data.get('batchStartDates', {})
        custom_sheet_indexes = data.get('batchSheetIndexes', {})
        # Choose processing method based on customization.
        if custom_filenames or custom_dates or custom_sheet_indexes:
            processed_files = process_batch_with_custom_names(
                input_dir, output_dir, ean_mapping, custom_filenames, config, 
                custom_dates, custom_sheet_indexes, consumption_type
            )
        else:
            processed_files = process_multiple_files(
                input_dir, output_dir, ean_mapping, "*.xlsx", config, consumption_type
            )
        if processed_files:
            success_count = sum(1 for status in processed_files.values() if status == "SUCCESS")
            total_count = len(processed_files)
            return {
                'success': True,
                'details': f'Traitement batch terminé: {success_count}/{total_count} '
                'fichiers traités avec succès'
            }
        return {'success': False, 'error': 'Aucun fichier Excel trouvé à traiter'}
    except Exception as e:
        return {'success': False, 'error': f'Erreur de traitement batch: {str(e)}'}


def process_batch_with_custom_names(
    input_dir: Path, output_dir: Path, ean_mapping: Dict[str, Any],
    custom_filenames: Dict[str, str], config: ParserConfig, custom_dates: Dict[str, str] = None,
    custom_sheet_indexes: Dict[str, str] = None,
    consumption_type: str = "MEASURED ACTIVE CONSUMPTION"
) -> Dict[str, str]:
    """
    Process multiple files with custom output names, start dates, and sheet indexes.

    :param input_dir:               Directory containing input Excel files.
    :param output_dir:              Directory to save output CSV files.
    :param ean_mapping:             EAN mapping dictionary.
    :param custom_filenames:        Dictionary mapping input filenames to custom output names.
    :param config:                  Parser configuration object.
    :param custom_dates:            Optional dictionary mapping input filenames to custom start
                                    dates.
    :param custom_sheet_indexes:    Optional dictionary mapping input filenames to custom sheet
                                    indexes.
    :param consumption_type:        Optional type of consumption to extract.

    :return:                        Dictionary with filenames as keys and processing status as
                                    values.
    """
    results = {}
    # Find all Excel files in input directory.
    input_files = []
    for pattern in ["*.xlsx", "*.XLSX", "*.xls", "*.XLS"]:
        input_files.extend(list(input_dir.glob(pattern)))
    # Remove duplicates.
    input_files = list(set(input_files))
    if not input_files:
        return results

    for input_file in input_files:
        input_filename = input_file.name
        # Determine output filename.
        if input_filename in custom_filenames and custom_filenames[input_filename].strip():
            output_filename = custom_filenames[input_filename].strip()
            if not output_filename.lower().endswith('.csv'):
                output_filename += '.csv'
        else:
            output_filename = f"{input_file.stem}.csv"

        output_file = output_dir / output_filename
        # Create file-specific configuration.
        file_config = ParserConfig()
        # Default to global setting.
        file_config.sheet_index = config.sheet_index
        # Default to global setting.
        file_config.start_date = config.start_date
        # Apply custom sheet index if provided.
        if custom_sheet_indexes and input_filename in custom_sheet_indexes:
            try:
                file_config.sheet_index = int(custom_sheet_indexes[input_filename])
            except ValueError:
                # Keep default on error.
                pass
        # Apply custom start date if provided.
        if custom_dates and input_filename in custom_dates:
            try:
                file_config.start_date = datetime.strptime(custom_dates[input_filename], '%Y-%m-%d')
            except ValueError:
                # Keep default on error.
                pass
        # Process the file.
        try:
            parse_renewgy_excel_to_csv(
                input_file, output_file, ean_mapping, file_config, consumption_type
            )
            results[input_filename] = "SUCCESS"
        except Exception as e:
            results[input_filename] = f"ERROR: {str(e)}"
    return results


# ----------------------------------------------------------------------------------------------- #
# ------------------------------------------ MAIN BLOCK ----------------------------------------- #
# ----------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    print("🌐 Lancement de l'interface web Renewgy Parser Intégrée")
    print(f"🖥️ Système détecté: {SYSTEM}")
    print(f"📁 Dossier de travail: {WORK_DIR}")

    if PARSER_AVAILABLE:
        print("✅ Parser Renewgy intégré disponible")
    else:
        print("❌ Parser Renewgy non disponible - fonctionnalité limitée")

    print("📱 Ouvrez http://localhost:5001 dans votre navigateur")

    # Flask application configuration.
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    HOST = '0.0.0.0'
    port = int(os.getenv('FLASK_PORT', '5001'))

    app.run(host=HOST, port=port, debug=debug, threaded=True)
