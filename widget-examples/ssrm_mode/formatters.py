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

    return data


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

    # For other row types, try to convert to dict
    try:
        return dict(row)
    except Exception:
        return {"data": row}


def format_query_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
        formatted_row = {}

        for key, value in row.items():
            # Get the value safely and clean it
            cleaned_value = clean_json_data(value)
            formatted_row[key] = cleaned_value

        formatted_results.append(formatted_row)

    return formatted_results
