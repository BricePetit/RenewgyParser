"""
Renewgy Parser - Excel to CSV Converter.

This module handles the conversion of Renewgy Excel files to standardized CSV format
with support for bi-hourly EAN splitting, dynamic column detection, and proper data validation.
"""
__title__: str = "renewgy_parser"
__version__: str = "2.0.0"
__version_info__ = (2, 0, 0)
__release_date__: str = "2025-01-11"
__author__: str = "Brice Petit"
__license__: str = "MIT"

# ----------------------------------------------------------------------------------------------- #
# ------------------------------------------- IMPORTS ------------------------------------------- #
# ----------------------------------------------------------------------------------------------- #

# Standard library imports.
import argparse
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple, Union, NoReturn, Any

# Third party imports.
import pandas as pd

# ----------------------------------------------------------------------------------------------- #
# ------------------------------------ TYPE DEFINITIONS ----------------------------------------- #
# ----------------------------------------------------------------------------------------------- #


@dataclass
class EANMapping:
    """
    Data class for EAN mapping configuration.
    
    :param source_id:   Identifier for the data source.
    :param variable_id: Variable identifier in the target system.
    :param description: Human-readable description of the EAN.
    """
    source_id: str
    variable_id: str
    description: str = ""


@dataclass
class ParserConfig:
    """
    Configuration parameters for the Renewgy parser.
    
    :param sheet_index:     Excel sheet index to process (0-based).
    :param header_row:      Row index for header detection.
    :param header_col:      Column index for header detection.
    :param data_start_row:  Default row index where data starts.
    :param timestamp_col:   Default column index for timestamps.
    :param value_col:       Default column index for values.
    :param min_rows:        Minimum required rows for validation.
    :param min_cols:        Minimum required columns for validation.
    :param start_date:      Optional start date filter.
    """
    sheet_index: int = 0
    header_row: int = 0
    header_col: int = 1
    data_start_row: int = 4
    timestamp_col: int = 0
    value_col: int = 2
    min_rows: int = 6
    min_cols: int = 3
    start_date: Optional[datetime] = None


# ----------------------------------------------------------------------------------------------- #
# -------------------------------------- GLOBAL VARIABLES --------------------------------------- #
# ----------------------------------------------------------------------------------------------- #

# Setup logging configuration.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Column names for the standardized CSV output.
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

# Default parser configuration instance.
DEFAULT_CONFIG = ParserConfig()

# ----------------------------------------------------------------------------------------------- #
# ---------------------------------------- CORE FUNCTIONS --------------------------------------- #
# ----------------------------------------------------------------------------------------------- #


def load_ean_mapping_from_file(config_path: Path) -> Dict[str, EANMapping]:
    """
    Load EAN mapping configuration from JSON file.

    :param config_path:         Path to the JSON configuration file.

    :return:                    Dictionary of EAN mappings keyed by EAN identifier.

    :raises FileNotFoundError:  If config file doesn't exist.
    :raises ValueError:         If config file format is invalid.
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


def validate_excel_structure(excel_df: pd.DataFrame, config: ParserConfig) -> None:
    """
    Validate the structure of the Excel DataFrame for processing.

    :param excel_df:    The loaded Excel DataFrame to validate.
    :param config:      Parser configuration with validation parameters.

    :raises ValueError: If the structure is invalid for processing.
    """
    if excel_df.shape[0] < config.min_rows:
        raise ValueError(
            f"Excel file has insufficient rows: {excel_df.shape[0]} < {config.min_rows}. "
            f"This sheet might be empty or contain summary data only."
        )
    if excel_df.shape[1] < config.min_cols:
        non_empty_cols = excel_df.dropna(axis=1, how='all').shape[1]
        raise ValueError(
            f"Excel file has insufficient columns: {excel_df.shape[1]} < {config.min_cols}. "
            f"Non-empty columns: {non_empty_cols}. "
            f"This sheet might be a summary/pivot table. Try a different sheet index."
        )
    # Check if critical cells are not empty.
    if pd.isna(excel_df.iloc[config.header_row, config.header_col]):
        raise ValueError(
            f"EAN header cell is empty at position ({config.header_row},{config.header_col}). "
            f"This might not be a data sheet or the sheet structure is different."
        )


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


def find_consumption_column(excel_df: pd.DataFrame, consumption_type: str) -> int:
    """
    Find the column index for the specified consumption type.
    Dynamically detects the header row by looking for "Role description".
    
    :param excel_df:            The loaded Excel DataFrame.
    :param consumption_type:    The consumption type to search for.
    
    :return:                    Column index.
    
    :raises ValueError:         If the consumption type is not found.
    """
    # Check if we have enough rows.
    if len(excel_df) < 2:
        raise ValueError("Excel file doesn't have enough rows to search for consumption type")
    # Find the row containing "Role description" (case insensitive).
    header_row_index = None
    # Check first 5 rows.
    for row_idx in range(min(5, len(excel_df))):
        row = excel_df.iloc[row_idx]
        for cell_value in row:
            if pd.notna(cell_value) and "role description" in str(cell_value).lower():
                header_row_index = row_idx
                logger.info("Found header row at index %s (row %s)", row_idx, row_idx + 1)
                break
        if header_row_index is not None:
            break
    if header_row_index is None:
        raise ValueError("Could not find header row containing 'Role description'")
    # Search for the consumption type in the found header row.
    header_row = excel_df.iloc[header_row_index]
    for col_idx, cell_value in enumerate(header_row):
        if pd.notna(cell_value) and str(cell_value).strip() == consumption_type:
            logger.info(
                "Found '%s' at column %s (row %s)", consumption_type, col_idx, header_row_index + 1
            )
            return col_idx
    # If not found, show available options from the header row.
    available_types = [
        str(cell).strip() for cell in header_row 
        if pd.notna(cell) and str(cell).strip().startswith("MEASURED")
    ]
    raise ValueError(
        f"Consumption type '{consumption_type}' not found in header row {header_row_index + 1}. "
        f"Available types: {available_types}"
    )


def extract_data_from_excel(
    excel_df: pd.DataFrame, config: ParserConfig,
    consumption_type: str = "MEASURED ACTIVE CONSUMPTION"
) -> Tuple[pd.Series, pd.Series]:
    """
    Extract timestamps and values from Excel file using dynamic column detection.
    
    :param excel_df:            The loaded Excel DataFrame.
    :param config:              Parser configuration.
    :param consumption_type:    The consumption type to search for.

    :return:                    Tuple of (timestamps, values).

    :raises ValueError:         If data extraction fails.
    """
    try:
        # Find the consumption column dynamically.
        value_col = find_consumption_column(excel_df, consumption_type)
        # Find the timestamp column dynamically.
        timestamp_col = find_timestamp_column(excel_df)
        # Find the data start row dynamically.
        data_start_row = find_data_start_row(excel_df)
        # Extract timestamps.
        timestamps = (
            excel_df.iloc[data_start_row:, timestamp_col].reset_index(drop=True)
        )
        # Extract values from the dynamically found column.
        values = excel_df.iloc[data_start_row:, value_col]
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
    config: Optional[ParserConfig] = None,
    consumption_type: str = "MEASURED ACTIVE CONSUMPTION"
) -> NoReturn:
    """
    Parses the Renewgy Excel file and converts it to a CSV file.
    Automatically generates two CSV files (peak and offpeak) for bi-hourly EANs.

    :param file_path:           Path to the input Excel file.
    :param output_csv_path:     Path to the output CSV file.
    :param ean_mapping:         EAN mapping dictionary (required).
    :param config:              Parser configuration (uses default if None).
    :param consumption_type:    Type of consumption to extract.

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
        # Check if this EAN has peak/offpeak variants.
        if has_peak_offpeak_variants(ean, ean_mapping):
            logger.info("EAN '%s' has peak/offpeak variants - generating two CSV files", ean)
            # Extract data.
            timestamps, values = extract_data_from_excel(excel_df, config, consumption_type)
            logger.info("Extracted %s data points", len(values))
            # Split data by period.
            (peak_timestamps, peak_values), (offpeak_timestamps, offpeak_values) = (
                split_data_by_period(timestamps, values)
            )
            logger.info(
                "Split data: %s peak points, %s offpeak points", len(peak_values),
                len(offpeak_values)
            )
            # Get mappings for peak and offpeak.
            peak_mapping = find_ean_mapping(ean, ean_mapping, is_peak=True)
            offpeak_mapping = find_ean_mapping(ean, ean_mapping, is_peak=False)
            # Ensure output directory exists.
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Generate peak CSV.
            if len(peak_values) > 0:
                peak_csv_data = create_output_dataframe(
                    peak_timestamps, peak_values, ean, peak_mapping
                )
                peak_output_path = (
                    output_path.parent / f"{output_path.stem}_peak{output_path.suffix}"
                )
                peak_csv_data.to_csv(peak_output_path, index=False, encoding='utf-8-sig')
                logger.info("Successfully saved peak CSV to: %s", peak_output_path)
            else:
                logger.warning("No peak data found for EAN %s", ean)
            # Generate offpeak CSV.
            if len(offpeak_values) > 0:
                offpeak_csv_data = create_output_dataframe(
                    offpeak_timestamps, offpeak_values, ean, offpeak_mapping
                )
                offpeak_output_path = (
                    output_path.parent / f"{output_path.stem}_offpeak{output_path.suffix}"
                )
                offpeak_csv_data.to_csv(offpeak_output_path, index=False, encoding='utf-8-sig')
                logger.info("Successfully saved offpeak CSV to: %s", offpeak_output_path)
            else:
                logger.warning("No offpeak data found for EAN %s", ean)   
        else:
            # Standard processing for non-bi-hourly EANs.
            logger.info("EAN '%s' is a standard (non-bi-hourly) EAN", ean)
            # Find mapping using the new function (for better error messages).
            mapping = find_ean_mapping(ean, ean_mapping)
            logger.info("Found mapping: %s", mapping.description)
            # Extract data.
            timestamps, values = extract_data_from_excel(excel_df, config, consumption_type)
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
    config: Optional[ParserConfig] = None,
    consumption_type: str = "MEASURED ACTIVE CONSUMPTION"
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
            parse_renewgy_excel_to_csv(
                input_file, output_file, ean_mapping, config, consumption_type
            )
            results[input_file.name] = "SUCCESS"
            logger.info("Processed: %s", input_file.name)
        except Exception as exc:
            results[input_file.name] = f"ERROR: {str(exc)}"
            logger.error("Failed: %s - %s", input_file.name, exc)
    return results


def find_data_start_row(excel_df: pd.DataFrame) -> int:
    """
    Find the row index where data starts.
    Looks for the row containing "Profile description" and returns the next row.
    
    :param excel_df:    The loaded Excel DataFrame.
    
    :return:            Row index where data starts.
    
    :raises ValueError: If data start row cannot be determined.
    """
    # Look for "Profile description" in the first few rows.
    # Check first 6 rows.
    for row_idx in range(min(6, len(excel_df))):
        row = excel_df.iloc[row_idx]
        for cell_value in row:
            if pd.notna(cell_value) and "profile description" in str(cell_value).lower():
                data_start_row = row_idx + 1  # Data starts on the next row
                logger.info(
                    "Found data start at row %s (after profile description at row %s)",
                    data_start_row + 1, row_idx + 1
                )
                return data_start_row
    # Fallback to default if not found.
    logger.warning("Could not find 'Profile description', using default data start row 4")
    return 4


def is_peak_hour(timestamp: pd.Timestamp) -> bool:
    """
    Determine if a timestamp is during peak hours.
    Peak hours:     7h-22h Monday to Friday
    Offpeak hours:  22h-7h Monday to Friday + all weekend

    :param timestamp:   The timestamp to check

    :return:            True if peak hour, False if offpeak
    """
    # Convert to datetime if it's not already.
    if isinstance(timestamp, str):
        timestamp = pd.to_datetime(timestamp)
    # Monday is 0, Sunday is 6.
    weekday = timestamp.weekday()
    hour = timestamp.hour
    # Weekend is always offpeak. Saturday (5) or Sunday (6).
    if weekday >= 5:
        return False
    # Weekday: peak is 7h-22h (7 <= hour < 22).
    return 7 <= hour < 22


def find_ean_mapping(
    ean: str, ean_mapping: Dict[str, EANMapping], is_peak: bool = None
) -> EANMapping:
    """
    Find the appropriate EAN mapping for the given EAN.
    If the EAN has peak/offpeak variants, return the appropriate one.
    If is_peak is None, return the simple EAN mapping (for non-bi-hourly EANs).
    
    :param ean:         The base EAN identifier.
    :param ean_mapping: EAN mapping dictionary.
    :param is_peak:     True for peak hours, False for offpeak, None for simple EAN.

    :return:            The appropriate EAN mapping.

    :raises KeyError:   If no suitable mapping is found.
    """
    # First check if we're looking for a specific peak/offpeak variant.
    if is_peak is not None:
        suffix = "_peak" if is_peak else "_offpeak"
        variant_key = f"{ean}{suffix}"
        if variant_key in ean_mapping:
            return ean_mapping[variant_key]
    # Check if the simple EAN exists.
    if ean in ean_mapping:
        return ean_mapping[ean]
    # If we couldn't find a direct match and is_peak was specified,
    # check if this EAN has any peak/offpeak variants.
    peak_key = f"{ean}_peak"
    offpeak_key = f"{ean}_offpeak"
    if peak_key in ean_mapping or offpeak_key in ean_mapping:
        if is_peak is None:
            raise KeyError(
                f"EAN '{ean}' has peak/offpeak variants but no period specified. "
                f"This EAN requires bi-hourly processing."
            )
        # We were looking for a specific variant but didn't find it.
        missing_variant = "peak" if is_peak else "offpeak"
        raise KeyError(
            f"EAN '{ean}' has bi-hourly variants but '{missing_variant}' mapping not found"
        )
    # No mapping found at all.
    available_eans = [k for k in ean_mapping.keys() if k.startswith(ean)]
    if available_eans:
        raise KeyError(
            f"EAN '{ean}' not found. Similar EANs available: {available_eans}"
        )
    available_eans = list(ean_mapping.keys())[:5]
    raise KeyError(
        f"EAN '{ean}' not found in mapping dictionary. "
        f"Available EANs include: {available_eans}..."
    )


def has_peak_offpeak_variants(ean: str, ean_mapping: Dict[str, EANMapping]) -> bool:
    """
    Check if an EAN has peak/offpeak variants in the mapping.
    
    :param ean:         The base EAN identifier.
    :param ean_mapping: EAN mapping dictionary

    :return:            True if the EAN has both peak and offpeak variants
    """
    peak_key = f"{ean}_peak"
    offpeak_key = f"{ean}_offpeak"
    return peak_key in ean_mapping and offpeak_key in ean_mapping


def split_data_by_period(
    timestamps: pd.Series, values: pd.Series
) -> Tuple[Tuple[pd.Series, pd.Series], Tuple[pd.Series, pd.Series]]:
    """
    Split timestamps and values into peak and offpeak periods.

    :param timestamps:  Series of timestamps
    :param values:      Series of values

    :return: Tuple of ((peak_timestamps, peak_values), (offpeak_timestamps, offpeak_values))
    """
    # Convert timestamps to datetime.
    timestamps_dt = pd.to_datetime(timestamps)
    # Create boolean mask for peak hours
    peak_mask = timestamps_dt.apply(is_peak_hour)
    # Split data.
    peak_timestamps = timestamps[peak_mask].reset_index(drop=True)
    peak_values = values[peak_mask].reset_index(drop=True)
    offpeak_timestamps = timestamps[~peak_mask].reset_index(drop=True)
    offpeak_values = values[~peak_mask].reset_index(drop=True)
    return (peak_timestamps, peak_values), (offpeak_timestamps, offpeak_values)


def find_timestamp_column(excel_df: pd.DataFrame) -> int:
    """
    Find the column index that contains timestamps/dates.
    Looks in the header row for "Date" or similar, and validates with actual data.
    
    :param excel_df:        The loaded Excel DataFrame.
    
    :return:                Column index for timestamps.
    
    :raises ValueError:     If timestamp column cannot be found.
    """
    # Find the header row first.
    header_row_index = None
    for row_idx in range(min(5, len(excel_df))):
        row = excel_df.iloc[row_idx]
        for cell_value in row:
            if pd.notna(cell_value) and "role description" in str(cell_value).lower():
                header_row_index = row_idx
                break
        if header_row_index is not None:
            break
    if header_row_index is None:
        logger.warning("Could not find header row, using heuristic approach")
        # Fallback: look for the column that contains date-like strings.
        data_start_row = find_data_start_row(excel_df)
        # Check first 4 columns.
        for col_idx in range(min(4, excel_df.shape[1])):
            sample_values = excel_df.iloc[data_start_row:data_start_row+3, col_idx]
            date_like_count = 0
            for val in sample_values:
                if pd.notna(val):
                    val_str = str(val)
                    # Check if it looks like a date (contains year pattern or datetime).
                    if (
                        '2024' in val_str or '2023' in val_str or '2025' in val_str or 
                        '2022' in val_str or '-' in val_str or ':' in val_str
                    ):
                        date_like_count += 1
            # At least 2 out of 3 samples look like dates.
            if date_like_count >= 2:
                logger.info("Found timestamp column at index %s using heuristic", col_idx)
                return col_idx
        # Final fallback.
        logger.warning("Could not detect timestamp column, using column 0")
        return 0
    # Search for "Date" in the header row.
    header_row = excel_df.iloc[header_row_index]
    for col_idx, cell_value in enumerate(header_row):
        if pd.notna(cell_value) and "date" in str(cell_value).lower():
            logger.info(
                "Found timestamp column 'Date' at index %s (row %s)", col_idx, header_row_index + 1
            )
            return col_idx

    # If "Date" not found, look for timestamp-like data in the actual data rows.
    data_start_row = find_data_start_row(excel_df)
    # Check first 4 columns.
    for col_idx in range(min(4, excel_df.shape[1])):
        sample_values = excel_df.iloc[data_start_row:data_start_row+5, col_idx]
        date_like_count = 0
        for val in sample_values:
            if pd.notna(val):
                val_str = str(val)
                # Check if it looks like a date/datetime.
                if ('2024' in val_str or '2023' in val_str or '2025' in val_str or 
                    '2022' in val_str or ':' in val_str):
                    try:
                        # Try to parse as datetime.
                        pd.to_datetime(val_str)
                        date_like_count += 1
                    except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime) as exc:
                        # Expected errors when the string is not a valid date.
                        logger.debug("Invalid date format for value '%s': %s", val_str, exc)
                        continue
        if date_like_count >= 3:  # At least 3 out of 5 samples are valid dates.
            logger.info("Found timestamp column at index %s using data analysis", col_idx)
            return col_idx
    # If still not found, look for the column just before the consumption data.
    # This is usually the pattern: [Timestamps] [Consumption] [Other...].
    try:
        consumption_col = find_consumption_column(excel_df, "MEASURED ACTIVE CONSUMPTION")
        if consumption_col > 0:
            timestamp_col = consumption_col - 1
            logger.info(
                "Inferred timestamp column at index %s (one column before consumption)",
                timestamp_col
            )
            return timestamp_col
    except (ValueError, KeyError) as exc:
        # If we can't find the consumption column, continue with other methods.
        logger.debug("Could not infer timestamp column from consumption column: %s", exc)
    # Final fallback - check column 0 for timestamps.
    data_start_row = find_data_start_row(excel_df)
    if data_start_row < len(excel_df):
        sample_val = excel_df.iloc[data_start_row, 0]
        if pd.notna(sample_val):
            val_str = str(sample_val)
            if ('2024' in val_str or '2023' in val_str or '2025' in val_str or 
                '2022' in val_str or ':' in val_str):
                logger.info("Using column 0 as timestamp column (detected date pattern)")
                return 0
    # Final fallback.
    logger.warning("Could not detect timestamp column reliably, using column 0")
    return 0

# ----------------------------------------------------------------------------------------------- #
# ------------------------------------------ MAIN FUNCTION -------------------------------------- #
# ----------------------------------------------------------------------------------------------- #


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
