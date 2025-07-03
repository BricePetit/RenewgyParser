"""
This module handles the conversion of Renewgy Excel files to standardized CSV format
with proper data validation, error handling, and logging capabilities.
"""
__title__: str = "renewgy_parser"
__version__: str = "1.0.0"
__author__: str = "Brice Petit"
__license__: str = "MIT"

# ----------------------------------------------------------------------------------------------- #
# ------------------------------------------- IMPORTS ------------------------------------------- #
# ----------------------------------------------------------------------------------------------- #

# Imports standard libraries.
import argparse
from datetime import datetime
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, NoReturn

# Imports third party libraries.
import pandas as pd

# Imports from src.


# ----------------------------------------------------------------------------------------------- #
# ------------------------------------ TYPE DEFINITIONS ----------------------------------------- #
# ----------------------------------------------------------------------------------------------- #

@dataclass
class EANMapping:
    """Data class for EAN mapping configuration."""
    source_id: str
    variable_id: str
    description: str = ""

@dataclass
class ParserConfig:
    """Configuration for the Renewgy parser."""
    sheet_index: int = 2
    header_row: int = 0
    header_col: int = 1
    data_start_row: int = 5
    timestamp_col: int = 0
    value_col: int = 2
    min_rows: int = 6
    min_cols: int = 3
    start_date: Optional[datetime] = None


# ----------------------------------------------------------------------------------------------- #
# -------------------------------------- GLOBAL VARIABLES --------------------------------------- #
# ----------------------------------------------------------------------------------------------- #

# Setup logging.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Column names for the CSV output.
CSV_COLUMN_NAMES: List[str] = [
    'date',
    'value',
    'meternumber',
    'source_id',
    'source_serialnumber',
    'source_ean',
    'source_name',
    'mapping_config',
    'variable_id'
]

# Default parser configuration.
DEFAULT_CONFIG = ParserConfig()

# ----------------------------------------------------------------------------------------------- #
# ------------------------------------------ FUNCTIONS ------------------------------------------ #
# ----------------------------------------------------------------------------------------------- #


def load_ean_mapping_from_file(config_path: Path) -> Dict[str, EANMapping]:
    """
    Load EAN mapping from external JSON file.

    :param config_path:         Path to the JSON configuration file.

    :return:                    Dictionary of EAN mappings.
    
    :raises FileNotFoundError:  If config file doesn't exist.
    :raises ValueError:         If config file is invalid.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                ean: EANMapping(
                    source_id=mapping['source_id'],
                    variable_id=mapping['variable_id'],
                    description=mapping.get('description', '')
                )
                for ean, mapping in data.items()
            }
    except (json.JSONDecodeError, KeyError) as exc:
        raise ValueError(f"Invalid configuration file format: {exc}") from exc


def validate_excel_structure(excel_df: pd.DataFrame, config: ParserConfig) -> NoReturn:
    """
    Validate the structure of the Excel DataFrame.

    :param excel_df:    The loaded Excel DataFrame.
    :param config:      Parser configuration.

    :raises ValueError: If the structure is invalid.
    """
    if excel_df.shape[0] < config.min_rows:
        raise ValueError(
            f"Excel file has insufficient rows: {excel_df.shape[0]} < {config.min_rows}"
        )

    if excel_df.shape[1] < config.min_cols:
        raise ValueError(
            f"Excel file has insufficient columns: {excel_df.shape[1]} < {config.min_cols}"
        )

    # Check if critical cells are not empty.
    if pd.isna(excel_df.iloc[config.header_row, config.header_col]):
        raise ValueError("EAN header cell is empty")


def extract_ean_from_excel(excel_df: pd.DataFrame, config: ParserConfig) -> str:
    """
    Extract EAN from Excel file.

    :param excel_df:    The loaded Excel DataFrame.
    :param config:      Parser configuration.

    :return:            Extracted EAN string.

    :raises ValueError: If EAN cannot be extracted.
    """
    try:
        ean_raw = excel_df.iloc[config.header_row, config.header_col]
        if pd.isna(ean_raw) or '_' not in str(ean_raw):
            raise ValueError(
                f"Invalid EAN format in cell ({config.header_row},{config.header_col})"
            )

        ean = str(ean_raw).split('_', maxsplit=1)[0].strip()

        if not ean:
            raise ValueError("EAN is empty after extraction")

        return ean

    except Exception as exc:
        raise ValueError(f"Failed to extract EAN: {exc}") from exc


def extract_data_from_excel(
    excel_df: pd.DataFrame, config: ParserConfig
) -> Tuple[pd.Series, pd.Series]:
    """
    Extract timestamps and values from Excel file.
    
    :param excel_df:    The loaded Excel DataFrame.
    :param config:      Parser configuration.

    :return:            Tuple of (timestamps, values).

    :raises ValueError: If data extraction fails.
    """
    try:
        # Extract timestamps.
        timestamps = (
            excel_df.iloc[config.data_start_row:, config.timestamp_col].reset_index(drop=True)
        )

        # Extract values.
        values = excel_df.iloc[config.data_start_row:, config.value_col]

        # Convert to float and handle errors.
        values = pd.to_numeric(values, errors='coerce').astype(float)
        values = values.reset_index(drop=True)

        # Filter data based on start_date if provided.
        if config.start_date is not None:
            # Convert timestamps to datetime for comparison.
            timestamps_dt = pd.to_datetime(timestamps, errors='coerce')

            # Find indices where timestamp is >= start_date.
            valid_indices = timestamps_dt >= config.start_date

            # Filter both series.
            timestamps = timestamps[valid_indices].reset_index(drop=True)
            values = values[valid_indices].reset_index(drop=True)

            logger.info(
                "Filtered data from %s onwards: %s rows remaining", 
                config.start_date.strftime('%Y-%m-%d'), len(timestamps)
            )

        # Check for NaN values.
        nan_count = values.isna().sum()
        if nan_count > 0:
            logger.warning("Found %s NaN values in data - these will be preserved", nan_count)

        if len(timestamps) != len(values):
            raise ValueError(
                f"Timestamps and values length mismatch: {len(timestamps)} vs {len(values)}"
            )

        return timestamps, values

    except Exception as exc:
        raise ValueError(f"Failed to extract data from Excel: {exc}") from exc


def create_output_dataframe(
    timestamps: pd.Series, values: pd.Series, ean: str, mapping: EANMapping
) -> pd.DataFrame:
    """
    Create the output CSV DataFrame.
    
    :param timestamps:  Time series data.
    :param values:      Value series data.
    :param ean:         EAN identifier.
    :param mapping:     EAN mapping configuration.

    :return:            Formatted DataFrame ready for CSV export.
    """
    return pd.DataFrame({
        'date': timestamps,
        'value': values,
        'meternumber': ean,
        'source_id': mapping.source_id,
        'source_serialnumber': '',
        'source_ean': '',
        'source_name': '',
        'mapping_config': '',
        'variable_id': mapping.variable_id
    }, columns=CSV_COLUMN_NAMES)


def parse_renewgy_excel_to_csv(
    file_path: Union[str, Path],
    output_csv_path: Union[str, Path],
    ean_mapping: Dict[str, EANMapping],
    config: Optional[ParserConfig] = None
) -> NoReturn:
    """
    Parses the Renewgy Excel file and converts it to a CSV file.

    :param file_path:           Path to the input Excel file.
    :param output_csv_path:     Path to the output CSV file.
    :param ean_mapping:         EAN mapping dictionary (required).
    :param config:              Parser configuration (uses default if None).

    :raises FileNotFoundError:  If the input Excel file doesn't exist.
    :raises KeyError:           If the EAN is not found in the mapping dictionary.
    :raises ValueError:         If the Excel file format is invalid.
    """
    # Use defaults if not provided.
    if config is None:
        config = DEFAULT_CONFIG

    # Convert paths to Path objects.
    input_path = Path(file_path)
    output_path = Path(output_csv_path)

    logger.info("Processing file: %s", input_path)

    try:
        # Read the Excel file.
        excel_df = pd.read_excel(input_path, sheet_name=config.sheet_index)
        logger.info("Loaded Excel file with shape: %s", excel_df.shape)

        # Validate structure.
        validate_excel_structure(excel_df, config)

        # Extract EAN.
        ean = extract_ean_from_excel(excel_df, config)
        logger.info("Extracted EAN: %s", ean)

        # Validate EAN exists in mapping.
        if ean not in ean_mapping:
            # Show first 5 for reference.
            available_eans = list(ean_mapping.keys())[:5]
            raise KeyError(
                f"EAN '{ean}' not found in mapping dictionary. "
                f"Available EANs include: {available_eans}..."
            )

        mapping = ean_mapping[ean]
        logger.info("Found mapping: %s", mapping.description)

        # Extract data.
        timestamps, values = extract_data_from_excel(excel_df, config)
        logger.info("Extracted %s data points", len(values))

        # Create output DataFrame.
        csv_data = create_output_dataframe(timestamps, values, ean, mapping)

        # Ensure output directory exists.
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to CSV.
        csv_data.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info("Successfully saved CSV to: %s", output_path)

    except FileNotFoundError as exc:
        logger.error("Input file not found: %s", input_path)
        raise FileNotFoundError(f"Input file not found: {input_path}") from exc
    except KeyError as exc:
        logger.error("EAN mapping error: %s", exc)
        raise KeyError(f"EAN not found in mapping: {exc}") from exc
    except ValueError as exc:
        logger.error("Data validation error: %s", exc)
        raise ValueError(f"Invalid data format: {exc}") from exc
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        raise ValueError(f"Error processing Excel file: {str(exc)}") from exc


def process_multiple_files(
    input_dir: Path,
    output_dir: Path,
    ean_mapping: Dict[str, EANMapping],
    pattern: str = "*.xlsx",
    config: Optional[ParserConfig] = None
) -> Dict[str, str]:
    """
    Process multiple Excel files in a directory.

    :param input_dir:   Directory containing input Excel files.
    :param output_dir:  Directory for output CSV files.
    :param ean_mapping: EAN mapping dictionary (required).
    :param pattern:     File pattern to match (default: *.xlsx).
    :param config:      Parser configuration.

    :return:            Dictionary of processing results {filename: status}.

    :raises Exception:  When failing to process files.
    """
    results = {}

    # If using default Excel pattern, search for both lowercase and uppercase extensions.
    if pattern == "*.xlsx":
        input_files = list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.XLSX"))
        # Remove duplicates while preserving order?
        seen = set()
        input_files = [f for f in input_files if not (f in seen or seen.add(f))]
        logger.info("Searching for Excel files with extensions: .xlsx and .XLSX")
    else:
        input_files = list(input_dir.glob(pattern))
        logger.info("Searching for files with pattern: %s", pattern)

    if not input_files:
        if pattern == "*.xlsx":
            logger.warning("No Excel files found (.xlsx or .XLSX) in %s", input_dir)
        else:
            logger.warning("No files found matching pattern '%s' in %s", pattern, input_dir)
        return results

    logger.info("Found %s files to process", len(input_files))

    for input_file in input_files:
        output_file = output_dir / f"{input_file.stem}.csv"

        try:
            parse_renewgy_excel_to_csv(input_file, output_file, ean_mapping, config)
            results[input_file.name] = "SUCCESS"
            logger.info("Processed: %s", input_file.name)
        except Exception as exc:
            results[input_file.name] = f"ERROR: {str(exc)}"
            logger.error("Failed: %s - %s", input_file.name, exc)

    return results


def main() -> NoReturn:
    """
    Main function to execute the script with enhanced CLI capabilities.
    """
    parser = argparse.ArgumentParser(
        description="Advanced Renewgy Excel to CSV Parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file.
  python renewgy_parser.py --input input.xlsx --output output.csv --config config.json
  
  # Process multiple files with batch mode.
  python renewgy_parser.py --batch-input ./input_dir --batch-output ./output_dir --config config.json
  
  # Process data from a specific date onwards.
  python renewgy_parser.py --input input.xlsx --output output.csv --config config.json --start-date 2023-01-01
  
  # Enable verbose logging.
  python renewgy_parser.py --input input.xlsx --output output.csv --config config.json --verbose
        """
    )

    # Main operation modes.
    parser.add_argument(
        "--input", 
        type=str,
        help="Path to the input Excel file (single file mode)"
    )
    parser.add_argument(
        "--output", 
        type=str,
        help="Path to the output CSV file (single file mode)"
    )
    parser.add_argument(
        "--batch-input", 
        type=str,
        help="Directory containing input Excel files (batch mode)"
    )
    parser.add_argument(
        "--batch-output", 
        type=str,
        help="Directory for output CSV files (batch mode)"
    )

    # Configuration options.
    parser.add_argument(
        "--config", 
        type=str,
        help="Path to JSON configuration file for EAN mappings (required)"
    )
    parser.add_argument(
        "--sheet-index", 
        type=int,
        default=2,
        help="Excel sheet index to process (default: 2)"
    )
    parser.add_argument(
        "--pattern", 
        type=str,
        default="*.xlsx",
        help="File pattern for batch processing (default: *.xlsx - automatically includes .XLSX)"
    )
    parser.add_argument(
        "--start-date", 
        type=str,
        help="Start date for data processing (format: YYYY-MM-DD). "
        "Only process data from this date onwards"
    )

    # Logging options.
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Suppress all output except errors"
    )

    # Parse arguments.
    args = parser.parse_args()

    # Configure logging level.
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    # Validate arguments.
    if not args.config:
        parser.error("--config is required")

    if args.input and not args.output:
        parser.error("--output is required when --input is specified")

    if args.batch_input and not args.batch_output:
        parser.error("--batch-output is required when --batch-input is specified")

    # Ensure we have either single file mode OR batch mode, not both or neither.
    single_mode = bool(args.input and args.output)
    batch_mode = bool(args.batch_input and args.batch_output)

    if not single_mode and not batch_mode:
        parser.error("Must specify either (--input --output) or (--batch-input --batch-output)")

    if single_mode and batch_mode:
        parser.error("Cannot use both single file mode and batch mode simultaneously")

    try:
        # Parse date arguments.
        start_date = None
        if args.start_date:
            try:
                start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
            except ValueError:
                logger.error("Invalid start date format. Use YYYY-MM-DD")
                sys.exit(1)

        # Load configuration.
        config = ParserConfig(sheet_index=args.sheet_index, start_date=start_date)

        # Load EAN mapping from config file (required).
        config_path = Path(args.config)
        try:
            ean_mapping = load_ean_mapping_from_file(config_path)
            logger.info("Loaded EAN mapping from %s", config_path)
        except (FileNotFoundError, ValueError) as exc:
            logger.error("Failed to load configuration: %s", exc)
            sys.exit(1)

        if start_date:
            logger.info("Processing data from %s onwards", start_date.strftime('%Y-%m-%d'))

        # Execute based on mode.
        if args.batch_input:
            # Batch processing mode.
            input_dir = Path(args.batch_input)
            output_dir = Path(args.batch_output)

            if not input_dir.exists():
                logger.error("Input directory not found: %s", input_dir)
                sys.exit(1)

            logger.info("Starting batch processing...")
            logger.info("Input directory: %s", input_dir)
            logger.info("Output directory: %s", output_dir)

            results = process_multiple_files(
                input_dir, output_dir, ean_mapping, args.pattern, config
            )

            # Summary.
            total_files = len(results)
            successful = sum(1 for status in results.values() if status == "SUCCESS")
            failed = total_files - successful

            logger.info("="*50)
            logger.info("BATCH PROCESSING SUMMARY")
            logger.info("="*50)
            logger.info("Total files: %d", total_files)
            logger.info("Successful: %d", successful)
            logger.info("Failed: %d", failed)

            if failed > 0:
                logger.info("\nFailed files:")
                for filename, status in results.items():
                    if status != "SUCCESS":
                        logger.info("  %s: %s", filename, status)

            sys.exit(0 if failed == 0 else 1)

        else:
            # Single file processing mode.
            input_path = Path(args.input)
            output_path = Path(args.output)

            if not input_path.exists():
                logger.error("Input file not found: %s", input_path)
                sys.exit(1)

            parse_renewgy_excel_to_csv(input_path, output_path, ean_mapping, config)
            logger.info("Processing completed successfully!")

    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as exc:
        logger.error("Fatal error: %s", exc)
        if args.verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
