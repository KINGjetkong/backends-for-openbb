"""
Simplified SSRM AgGrid Helper Functions

This file contains the main helper functions that tie together all the modular components:
- Database management through DatabaseManager
- Query building through QueryBuilder
- Data formatting through formatters
- All configured through DatabaseConfig
"""

from pathlib import Path
from typing import Any, Dict, List, Literal, Tuple, overload

from config import DatabaseConfig
from database import DatabaseManager
from formatters import format_query_results
from models import AgRows
from query_builder import QueryBuilder


async def perform_ssrm_query(
    db_manager: DatabaseManager, ag_rows: AgRows
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Execute SSRM query using the modular components.

    This is the main function that:
    1. Creates a query builder from AgGrid configuration
    2. Builds both main and count queries
    3. Executes queries
    4. Returns total count and formatted results

    Args:
        db_manager: Database manager instance
        ag_rows: AgGrid configuration and base query

    Returns:
        Tuple[int, List[Dict[str, Any]]]: (total_count, formatted_results)

    Raises:
        Exception: If query execution fails
    """
    try:
        # Create query builder with database-specific settings
        query_builder = QueryBuilder(
            ag_rows=ag_rows,
            table_name=db_manager.table_name,
            escape_char=db_manager.escape_char,
        )

        # Build queries
        main_query = query_builder.build_query()
        count_query = query_builder.build_count_query()

        print(f"Executing count query: {count_query}")
        print(f"Executing main query: {main_query}")

        # Execute count query first
        total_count = db_manager.execute_count_query(count_query)

        # Execute main query
        results = db_manager.execute_query(main_query)

        # Format results for JSON response
        is_grouped = ag_rows.options.is_doing_grouping()
        formatted_results = format_query_results(results, is_grouped)

        return total_count, formatted_results

    except Exception as e:
        print(f"Error in perform_ssrm_query: {e}")
        raise


@overload
def create_database_manager(
    database_type: Literal["sqlite"],
    file_path: Path | str,
    table_name: str,
    **kwargs,
) -> DatabaseManager: ...


@overload
def create_database_manager(
    database_type: Literal["snowflake", "mysql"],
    connection_string: str = None,
    **mysql_params,
) -> DatabaseManager: ...


def create_database_manager(
    database_type: Literal["sqlite", "snowflake", "mysql"] = "sqlite",
    file_path: Path | str = None,
    connection_string: str = None,
    table_name: str = "data",
    schema: str = None,
    **mysql_params,
) -> DatabaseManager:
    """
    Create a database manager with the specified configuration.

    Args:
        database_type: Type of database ('sqlite', 'snowflake', 'mysql')
        connection_string: Database connection string (for SQLite and Snowflake)
        table_name: Name of the table to query
        schema: Schema name (for databases that support it)
        **mysql_params: MySQL connection parameters (host, database, user, password, port)

    Returns:
        DatabaseManager: Configured database manager

    Examples:
        # SQLite
        db_manager = create_database_manager("sqlite", "data.db", "my_table")

        # MySQL
        db_manager = create_database_manager(
            "mysql",
            table_name="my_table",
            host="localhost",
            database="mydb",
            user="user",
            password="pass"
        )
    """
    if database_type == "sqlite":
        config = DatabaseConfig.for_sqlite(db_path=file_path, table_name=table_name)
    elif database_type == "mysql":
        # Extract MySQL parameters
        host = mysql_params.get("host", "localhost")
        database = mysql_params.get("database")
        user = mysql_params.get("user")
        password = mysql_params.get("password")
        port = mysql_params.get("port", 3306)

        if not all([host, database, user, password]):
            raise ValueError(
                "MySQL requires host, database, user, and password parameters"
            )

        config = DatabaseConfig.for_mysql(
            host=host,
            database=database,
            user=user,
            password=password,
            table_name=table_name,
            port=port,
        )
    elif database_type == "snowflake":
        config = DatabaseConfig.for_snowflake(
            connection_string=connection_string, table_name=table_name, schema=schema
        )
    else:
        raise ValueError(f"Unsupported database type: {database_type}")

    return DatabaseManager(config)
