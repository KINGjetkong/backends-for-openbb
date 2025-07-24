"""
Generic configuration file for SSRM AgGrid application.
Contains configurable settings that can be adapted to any database and table structure.
"""

from pathlib import Path

# Default Database Configuration (can be overridden)
DEFAULT_DATABASE_NAME = "demo_data.db"
DEFAULT_TABLE_NAME = "demo_data"

SQL_ESCAPE_CHAR = '"'


def get_database_path(custom_path: str = None) -> Path:
    """Get database path, allowing for custom override"""
    if custom_path:
        return Path(custom_path)
    return Path(__file__).parent / DEFAULT_DATABASE_NAME

# Aggregation functions supported
SUPPORTED_AGG_FUNCTIONS = ["sum", "avg", "count", "min", "max"]


class DatabaseConfig:
    """
    Database configuration class that can be customized for different environments.
    """

    def __init__(
        self,
        database_type: str = "sqlite",
        connection_string: str = None,
        table_name: str = DEFAULT_TABLE_NAME,
        escape_char: str = SQL_ESCAPE_CHAR,
    ):
        self.database_type = database_type
        self.connection_string = connection_string
        self.table_name = table_name
        self.escape_char = escape_char

    @classmethod
    def for_sqlite(cls, db_path: str = None, table_name: str = DEFAULT_TABLE_NAME):
        """Create configuration for SQLite database"""
        path = get_database_path(db_path)
        return cls(
            database_type="sqlite",
            connection_string=Path(path).resolve(),
            table_name=table_name,
            escape_char='"',
        )

    @classmethod
    def for_snowflake(cls, connection_string: str, table_name: str, schema: str = None):
        """Create configuration for Snowflake database"""
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        return cls(
            database_type="snowflake",
            connection_string=connection_string,
            table_name=full_table_name,
            escape_char='"',
        )

    @classmethod
    def for_mysql(
        cls,
        host: str,
        database: str,
        user: str,
        password: str,
        table_name: str = DEFAULT_TABLE_NAME,
        port: int = 3306,
    ):
        """Create configuration for MySQL database"""
        connection_config = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "port": port,
        }
        return cls(
            database_type="mysql",
            connection_string=connection_config,
            table_name=table_name,
            escape_char="`",
        )
