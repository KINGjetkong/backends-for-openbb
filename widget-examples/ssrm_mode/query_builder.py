"""
Generic SQL Query Builder for AgGrid Server-Side Row Model.
Works with any database table structure without hardcoded field mappings.
"""

from typing import Any, Dict, Optional

from config import SUPPORTED_AGG_FUNCTIONS
from models import AgRows


class QueryBuilder:
    """
    Generic Query Builder for AgGrid SSRM that works with any table structure.
    Builds SQL queries based on AgGrid configuration without hardcoded mappings.
    """

    def __init__(self, ag_rows: AgRows, table_name: str, escape_char: str = '"'):
        """
        Initialize query builder.

        Args:
            ag_rows: AgRows object containing query and options
            table_name: Name of the database table to query
            escape_char: SQL escape character for column names
        """
        self.ag_rows = ag_rows
        self.table_name = table_name
        self.escape_char = escape_char

    def escape_column(self, column_name: str) -> str:
        """Escape a column name for SQL safety"""
        return f"{self.escape_char}{column_name}{self.escape_char}"

    def create_select_sql(self) -> str:
        """
        Create the SELECT portion of the SQL query.
        Handles both regular queries and group queries with aggregation.

        Returns:
            str: SELECT SQL clause
        """
        if not self.ag_rows.options.is_doing_grouping():
            # Regular query - use the base query or select all columns
            if self.ag_rows.query and not self.ag_rows.query.strip().lower().startswith(
                "select"
            ):
                return f"SELECT * FROM {self.table_name}"
            return self.ag_rows.query or f"SELECT * FROM {self.table_name}"
        else:
            # Group query - select group columns and aggregated values
            group_col = self.ag_rows.options.get_row_group_column()
            if not group_col:
                return f"SELECT * FROM {self.table_name}"

            group_col_id = group_col.get("id", group_col.get("field", ""))

            # Start with group column
            cols_to_select = [self.escape_column(group_col_id)]

            # Add aggregations for value columns
            for value_col in self.ag_rows.options.valueCols:
                agg_func = value_col.get("aggFunc", "sum")
                agg_field = value_col.get("field", value_col.get("id", ""))

                # Validate aggregation function
                if agg_func not in SUPPORTED_AGG_FUNCTIONS:
                    agg_func = "sum"

                # Build aggregation SQL
                agg_col_name = f"{agg_func}({self.escape_column(agg_field)})"
                cols_to_select.append(
                    f"{agg_col_name} as {self.escape_column(agg_field)}"
                )

            # If no value columns provided, add a count to make it a proper aggregated query
            if len(self.ag_rows.options.valueCols) == 0:
                cols_to_select.append('count(*) as "count"')

            # Build complete SELECT clause
            select_sql = f'SELECT {", ".join(cols_to_select)} FROM {self.table_name}'
            return select_sql

    def create_where_sql(self) -> str:
        """
        Create WHERE clause from AgGrid filter model and group keys.

        This method handles two types of WHERE conditions:
        1. Group Keys: When groups are expanded, filter data to show only the selected group
        2. Filter Model: Explicit filters applied by users

        Supports various filter types including:
        - Text filters: contains, equals, startsWith, endsWith
        - Number filters: equals, greaterThan, lessThan, inRange
        - Set filters: in/not in lists

        Returns:
            str: WHERE SQL clause
        """
        where_parts = []

        # Handle group keys - add WHERE conditions for expanded groups
        if self.ag_rows.options.groupKeys:
            for index, key in enumerate(self.ag_rows.options.groupKeys):
                # Make sure we don't go out of bounds
                if index < len(self.ag_rows.options.rowGroupCols):
                    row_group_col = self.ag_rows.options.rowGroupCols[index]
                    col_field = row_group_col.get("field", row_group_col.get("id", ""))

                    # Properly escape the key value to prevent SQL injection
                    escaped_key = key.replace("'", "''")  # Escape single quotes
                    escaped_col = self.escape_column(col_field)
                    where_condition = f"{escaped_col} = '{escaped_key}'"
                    where_parts.append(where_condition)

        # Handle filter model - explicit user filters
        if self.ag_rows.options.filterModel:
            for field_name, filter_config in self.ag_rows.options.filterModel.items():
                filter_type = filter_config.get("filterType", "text")

                if filter_type == "text":
                    where_clause = self._build_text_filter(field_name, filter_config)
                    if where_clause:
                        where_parts.append(where_clause)

                elif filter_type == "number":
                    where_clause = self._build_number_filter(field_name, filter_config)
                    if where_clause:
                        where_parts.append(where_clause)

                elif filter_type == "set":
                    where_clause = self._build_set_filter(field_name, filter_config)
                    if where_clause:
                        where_parts.append(where_clause)

        if where_parts:
            where_clause = f" WHERE {' AND '.join(where_parts)}"
            return where_clause

        return ""

    def _build_text_filter(
        self, field_name: str, filter_config: Dict[str, Any]
    ) -> Optional[str]:
        """Build WHERE clause for text filters"""
        condition_type = filter_config.get("type", "contains")
        filter_value = filter_config.get("filter", "")

        if not filter_value:
            return None

        escaped_field = self.escape_column(field_name)
        escaped_value = filter_value.replace("'", "''")  # Escape single quotes

        if condition_type == "contains":
            return f"{escaped_field} LIKE '%{escaped_value}%'"
        elif condition_type == "equals":
            return f"{escaped_field} = '{escaped_value}'"
        elif condition_type == "startsWith":
            return f"{escaped_field} LIKE '{escaped_value}%'"
        elif condition_type == "endsWith":
            return f"{escaped_field} LIKE '%{escaped_value}'"
        elif condition_type == "notContains":
            return f"{escaped_field} NOT LIKE '%{escaped_value}%'"

        return None

    def _build_number_filter(
        self, field_name: str, filter_config: Dict[str, Any]
    ) -> Optional[str]:
        """Build WHERE clause for number filters"""
        condition_type = filter_config.get("type", "equals")
        filter_value = filter_config.get("filter", 0)

        escaped_field = self.escape_column(field_name)

        if condition_type == "equals":
            return f"{escaped_field} = {filter_value}"
        elif condition_type == "greaterThan":
            return f"{escaped_field} > {filter_value}"
        elif condition_type == "lessThan":
            return f"{escaped_field} < {filter_value}"
        elif condition_type == "greaterThanOrEqual":
            return f"{escaped_field} >= {filter_value}"
        elif condition_type == "lessThanOrEqual":
            return f"{escaped_field} <= {filter_value}"
        elif condition_type == "inRange":
            filter_to = filter_config.get("filterTo", filter_value)
            return f"{escaped_field} BETWEEN {filter_value} AND {filter_to}"

        return None

    def _build_set_filter(
        self, field_name: str, filter_config: Dict[str, Any]
    ) -> Optional[str]:
        """Build WHERE clause for set filters"""
        values = filter_config.get("values", [])
        if not values:
            return None

        escaped_field = self.escape_column(field_name)
        escaped_values = "', '".join(str(v).replace("'", "''") for v in values)
        return f"{escaped_field} IN ('{escaped_values}')"

    def create_group_by_sql(self) -> str:
        """
        Create GROUP BY clause for grouped queries.

        Returns:
            str: GROUP BY SQL clause
        """
        if not self.ag_rows.options.is_doing_grouping():
            return ""

        group_col = self.ag_rows.options.get_row_group_column()
        if not group_col:
            return ""

        group_col_id = group_col.get("id", group_col.get("field", ""))
        return f" GROUP BY {self.escape_column(group_col_id)}"

    def create_order_by_sql(self) -> str:
        """
        Create ORDER BY clause from AgGrid sort model.

        Supports multi-column sorting with ASC/DESC directions.
        For grouped queries, allows sorting by group columns and aggregated value columns.

        Returns:
            str: ORDER BY SQL clause
        """
        if not self.ag_rows.options.sortModel:
            return ""

        sort_parts = []

        if self.ag_rows.options.is_doing_grouping():
            # For grouped queries, get allowed sort columns
            allowed_sort_cols = set()

            # Add group column(s)
            group_col_ids = (
                [
                    group_col.get("id", group_col.get("field", ""))
                    for group_col in self.ag_rows.options.rowGroupCols[
                        : len(self.ag_rows.options.groupKeys) + 1
                    ]
                ]
                if self.ag_rows.options.rowGroupCols
                else []
            )
            allowed_sort_cols.update(group_col_ids)

            # Add value columns (aggregated columns)
            value_col_ids = (
                [
                    value_col.get("field", value_col.get("id", ""))
                    for value_col in self.ag_rows.options.valueCols
                ]
                if self.ag_rows.options.valueCols
                else []
            )
            allowed_sort_cols.update(value_col_ids)

            # Apply sort only for allowed columns
            for item in self.ag_rows.options.sortModel:
                col_id = item.get("colId", "")
                sort_direction = item.get("sort", "asc").upper()

                if col_id in allowed_sort_cols:
                    sort_parts.append(f"{self.escape_column(col_id)} {sort_direction}")
        else:
            # For non-grouped queries, allow sorting by any column
            for item in self.ag_rows.options.sortModel:
                col_id = item.get("colId", "")
                sort_direction = item.get("sort", "asc").upper()
                sort_parts.append(f"{self.escape_column(col_id)} {sort_direction}")

        if sort_parts:
            return f" ORDER BY {', '.join(sort_parts)}"
        return ""

    def create_limit_sql(self) -> str:
        """
        Create LIMIT clause for pagination.

        Returns:
            str: LIMIT SQL clause with OFFSET
        """
        if self.ag_rows.options.startRow == 0 and self.ag_rows.options.endRow == 0:
            return ""

        final_limit = self.ag_rows.options.page_size()
        return f" LIMIT {final_limit} OFFSET {self.ag_rows.options.startRow}"

    def build_query(self) -> str:
        """
        Build complete SQL query combining all clauses.

        Returns:
            str: Complete SQL query
        """
        try:
            query = (
                f"{self.create_select_sql()}"
                f"{self.create_where_sql()}"
                f"{self.create_group_by_sql()}"
                f"{self.create_order_by_sql()}"
                f"{self.create_limit_sql()}"
            )

            return query.strip()
        except Exception as e:
            import traceback

            traceback.print_exc()
            raise

    def build_count_query(self) -> str:
        """
        Build COUNT query for total row calculation.

        Returns:
            str: COUNT SQL query
        """
        try:
            if self.ag_rows.options.is_doing_grouping():
                # For grouped queries, count distinct groups
                group_col = self.ag_rows.options.get_row_group_column()
                if group_col:
                    group_col_id = group_col.get("id", group_col.get("field", ""))
                    return f"SELECT COUNT(DISTINCT {self.escape_column(group_col_id)}) FROM {self.table_name}{self.create_where_sql()}"

            # Regular count query
            return f"SELECT COUNT(*) FROM {self.table_name}{self.create_where_sql()}"
        except Exception as e:
            raise
