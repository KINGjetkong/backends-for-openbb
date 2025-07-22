import json
from pathlib import Path
from typing import Annotated

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from helpers import create_database_manager, perform_ssrm_query

# Import our custom models and helper functions
from models import AgGridOptions, AgRows

# Initialize FastAPI application
app = FastAPI(
    title="Generic SSRM AgGrid API",
    description="Server-Side Row Model API for AgGrid with modular database support",
    version="1.0.0",
)

# CORS configuration for web frontend integration
origins = ["http://localhost:1420", "https://pro.openbb.dev", "https://pro.openbb.co"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize database manager
# Note: Ensure you have 'tpv_data.db' file in the same directory or provide correct path
db_manager = create_database_manager(
    database_type="sqlite",
    file_path=Path(__file__).parent / "tpv_data.db",
    table_name="tpv_data",
)


@app.get("/")
def get_root():
    return {
        "name": "Generic SSRM AgGrid API",
        "version": "1.0.0",
        "description": "Server-Side Row Model API for AgGrid with modular database support",
    }


@app.post("/data-ssrm")
async def get_data_ssrm(
    ag_options: Annotated[AgGridOptions, Body(...)] = AgGridOptions(),
):
    """
    Main Server-Side Row Model endpoint for AgGrid data requests.

    This is the core endpoint that handles all AgGrid SSRM functionality including:

    **Pagination**:
    - Processes startRow/endRow to return specific data pages
    - Optimizes query performance for large datasets

    **Filtering**:
    - Text filters: contains, equals, startsWith, endsWith, notContains
    - Number filters: equals, greaterThan, lessThan, inRange
    - Set filters: multiple value selection

    **Sorting**:
    - Multi-column sorting with ASC/DESC directions
    - Maintains sort state across grouping operations

    **Grouping**:
    - Row grouping with COUNT aggregation
    - Hierarchical grouping support
    - Dynamic GROUP BY query generation

    Args:
        request (SSRMRequest): AgGrid SSRM request containing:
            - startRow/endRow: Pagination boundaries
            - sortModel: Array of sort configurations
            - filterModel: Object with filter configurations
            - rowGroupCols: Grouping column configurations
            - groupKeys: Current group expansion state
            - valueCols: Aggregation column configurations

    Returns:
        dict: SSRM response containing:
            - data: Array of formatted data rows
            - rows: Total row count for pagination
            - debug_info: Query execution information

    Raises:
        HTTPException: 500 error if database query fails

    Example Request:
        ```json
        {
            "startRow": 0,
            "endRow": 100,
            "sortModel": [{"colId": "firm", "sort": "asc"}],
            "filterModel": {
                "firm": {
                    "filterType": "text",
                    "type": "contains",
                    "filter": "Goldman"
                }
            },
            "rowGroupCols": [{"id": "sector", "field": "sector"}]
        }
        ```

    Example Response:
        ```json
        {
            "data": [...],
            "rows": 1534,
            "debug_info": {
                "has_grouping": true,
                "filter_count": 1,
                "sort_count": 1
            }
        }
        ```
    """
    try:
        # Convert SSRM request to AgGrid options

        # Create AgRows configuration with base query
        base_query = f"SELECT * FROM {db_manager.table_name}"
        ag_rows = AgRows(
            query=base_query, options=ag_options, escape=db_manager.escape_char
        )

        # Execute the SSRM query using our helper function
        total_count, formatted_results = await perform_ssrm_query(db_manager, ag_rows)

        print("✅ Query executed successfully:")
        print(f"   📊 Total rows found: {total_count}")
        print(f"   📄 Returned rows: {len(formatted_results)}")

        # Results are already formatted and cleaned by our modular system
        clean_results = formatted_results

        # Prepare response with debug information
        # Must contain data + rows - debug_info is optional
        response = {
            "rowData": clean_results,
            "rowCount": total_count,
            "debug_info": {
                "has_grouping": bool(ag_options.rowGroupCols),
                "group_columns": len(ag_options.rowGroupCols or []),
                "active_filters": len(ag_options.filterModel or {}),
                "sort_columns": len(ag_options.sortModel or []),
                "is_pivot_mode": ag_options.pivotMode or False,
                "page_size": ag_options.page_size(),
                "current_page": (ag_options.startRow or 0) // ag_options.page_size()
                + 1,
            },
        }

        return response

    except Exception as e:
        error_msg = f"Error processing SSRM request: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Terminal Pro"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8008, reload=True, log_level="info")
