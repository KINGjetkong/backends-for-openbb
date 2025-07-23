"""
Generic SSRM AgGrid Data Models

This file contains all the essential data models needed for the Server-Side Row Model (SSRM)
AgGrid functionality with any database table structure.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# AgGrid Options Model
class AgGridOptions(BaseModel):
    """
    AgGrid options configuration for server-side processing.
    Provides utilities for checking grouping state and calculating pagination.
    """

    startRow: Optional[int] = 0
    endRow: Optional[int] = 500
    sortModel: Optional[list] = []
    filterModel: Optional[dict] = {}
    groupKeys: Optional[list] = []
    rowGroupCols: Optional[list] = []
    valueCols: Optional[list] = []
    pivotCols: Optional[list] = []
    pivotMode: Optional[bool] = False

    def is_doing_grouping(self) -> bool:
        """Check if grouping is being performed"""
        return len(self.rowGroupCols or []) > len(self.groupKeys or [])

    def get_row_group_column(self):
        """Get the current row group column for hierarchical grouping"""
        if self.rowGroupCols and len(self.rowGroupCols) >= len(self.groupKeys or []):
            return self.rowGroupCols[len(self.groupKeys or [])]
        return None

    def page_size(self) -> int:
        """Calculate page size from start and end rows"""
        if self.startRow > self.endRow:
            return 0
        return self.endRow - self.startRow


# AgRows Model - Bridge between AgGrid and SQL Query Builder
class AgRows(BaseModel):
    """
    Bridge model between AgGrid configuration and SQL query building.
    Contains the base query and options needed for server-side processing.
    """

    model_config = {"arbitrary_types_allowed": True}

    query: str  # Base SQL query
    options: AgGridOptions  # AgGrid configuration options
    # SQL escape character for column names (default for most databases)
    escape: str = '"'


# Generic response models
class SSRMResponse(BaseModel):
    """Response model for SSRM requests"""

    rowData: List[Dict[str, Any]]  # The actual data rows
    lastRow: Optional[int] = None  # Last row index (-1 if no more rows)


class ColumnInfo(BaseModel):
    """Model for database column information"""

    column_name: str
    column_type: str


class TableInfo(BaseModel):
    """Model for database table information"""

    table_name: str
    total_rows: int
    columns: List[ColumnInfo]
