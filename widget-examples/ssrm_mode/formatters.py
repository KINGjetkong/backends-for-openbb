"""
Generic data formatting utilities for SSRM AgGrid application.
Handles data conversion without hardcoded field mappings.
"""

import math
from typing import Any, Dict, List


def clean_json_data(data):
    """
    Clean data to ensure JSON compliance by replacing NaN and infinity values.

    Recursively processes nested dictionaries and lists to replace non-JSON-compliant
    numeric values with None.

    Args:
        data: Data structure to clean (dict, list, or primitive)

    Returns:
        Cleaned data structure safe for JSON serialization
    """
    if isinstance(data, dict):
        return {k: clean_json_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_json_data(item) for item in data]
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return None
        return data
    else:
        return data


def safe_get_value(row: Dict[str, Any], key: str) -> Any:
    """
    Safely get value from row dictionary, handling None values.

    Args:
        row: Dictionary containing row data
        key: Key to retrieve from the dictionary

    Returns:
        The value if it exists and is not None, otherwise None
    """
    value = row.get(key)
    if value is None:
        return None
    return value


def convert_database_row_to_dict(row: Any) -> Dict[str, Any]:
    """
    Convert database row to dictionary format.

    Args:
        row: Database row object (could be sqlite3.Row, dict, etc.)

    Returns:
        Dict[str, Any]: Row data as dictionary
    """
    if hasattr(row, "keys"):  # sqlite3.Row or similar
        return dict(row)
    elif isinstance(row, dict):
        return row
    else:
        # For other row types, try to convert to dict
        try:
            return dict(row)
        except Exception:
            return {"data": row}


def format_grouped_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a grouped/aggregated database row for API response.

    For grouped queries, this ensures the row is properly formatted
    without any specific field mapping assumptions.

    Args:
        row: Database row from aggregated query as dictionary

    Returns:
        Dict[str, Any]: Formatted row ready for JSON response
    """
    formatted_row = {}

    for key, value in row.items():
        # Clean the value for JSON compliance
        cleaned_value = clean_json_data(value)
        formatted_row[key] = cleaned_value

    return formatted_row


def format_regular_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a regular database row for API response.

    Args:
        row: Database row as dictionary

    Returns:
        Dict[str, Any]: Formatted row ready for JSON response
    """
    formatted_row = {}

    for key, value in row.items():
        # Get the value safely and clean it
        safe_value = safe_get_value(row, key)
        cleaned_value = clean_json_data(safe_value)
        formatted_row[key] = cleaned_value

    return formatted_row


def format_query_results(
    results: List[Dict[str, Any]], is_grouped: bool = False
) -> List[Dict[str, Any]]:
    """
    Format query results for API response.

    Args:
        results: List of database rows as dictionaries
        is_grouped: Whether the results are from a grouped query

    Returns:
        List[Dict[str, Any]]: Formatted results ready for JSON response
    """
    formatted_results = []

    for row in results:
        if is_grouped:
            formatted_row = format_grouped_row(row)
        else:
            formatted_row = format_regular_row(row)

        formatted_results.append(formatted_row)

    return formatted_results
