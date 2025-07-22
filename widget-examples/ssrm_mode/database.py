"""
Generic database management utilities for SSRM AgGrid application.
Supports multiple database types through configurable database connections.
"""

import sqlite3
from typing import Any, Dict, List, Protocol

from config import DatabaseConfig

try:
    import mysql.connector  # type: ignore[import]
    from mysql.connector import Error as MySQLError  # type: ignore[import]

    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


class DatabaseConnection(Protocol):
    """Protocol defining the interface for database connections"""

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        pass

    def execute_count_query(self, query: str) -> int:
        """Execute a COUNT query and return the result"""
        pass

    def get_table_columns(self, table_name: str) -> List[Dict[str, str]]:
        """Get column information for a table"""
        pass

    def get_table_count(self, table_name: str) -> int:
        """Get total row count for a table"""
        pass


class SQLiteConnection:
    """SQLite database connection implementation"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Get SQLite connection with proper configuration"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return conn

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                # Convert Row objects to dictionaries
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error executing query: {query}")
            print(f"Error: {str(e)}")
            raise

    def execute_count_query(self, query: str) -> int:
        """Execute a COUNT query and return the result"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()[0]
                return result if result is not None else 0
        except Exception as e:
            print(f"Error executing count query: {query}")
            print(f"Error: {str(e)}")
            raise

    def get_table_columns(self, table_name: str) -> List[Dict[str, str]]:
        """Get column information for a table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for row in cursor.fetchall():
                columns.append({"column_name": row[1], "column_type": row[2]})
            return columns

    def get_table_count(self, table_name: str) -> int:
        """Get total row count for a table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]


class MySQLConnection:
    """MySQL database connection implementation"""

    def __init__(self, connection_config: Dict[str, Any]):
        if not MYSQL_AVAILABLE:
            raise ImportError(
                "mysql-connector-python is required for MySQL connections"
            )
        self.connection_config = connection_config

    def get_connection(self):
        """Get MySQL connection with proper configuration"""
        try:
            connection = mysql.connector.connect(**self.connection_config)
            return connection
        except MySQLError as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        except MySQLError as e:
            print(f"Error executing query: {query}")
            print(f"Error: {str(e)}")
            raise

    def execute_count_query(self, query: str) -> int:
        """Execute a COUNT query and return the result"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            return result if result is not None else 0
        except MySQLError as e:
            print(f"Error executing count query: {query}")
            print(f"Error: {str(e)}")
            raise

    def get_table_columns(self, table_name: str) -> List[Dict[str, str]]:
        """Get column information for a table"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"DESCRIBE {table_name}")
            columns = []
            for row in cursor.fetchall():
                columns.append(
                    {"column_name": row["Field"], "column_type": row["Type"]}
                )
            cursor.close()
            connection.close()
            return columns
        except MySQLError as e:
            print(f"Error getting table columns: {e}")
            raise

    def get_table_count(self, table_name: str) -> int:
        """Get total row count for a table"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            result = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            return result
        except MySQLError as e:
            print(f"Error getting table count: {e}")
            raise


class DatabaseManager:
    """
    Generic Database Manager that works with different database types.
    """

    def __init__(self, config: DatabaseConfig):
        """
        Initialize database manager with configuration.

        Args:
            config: DatabaseConfig instance specifying database type and connection details
        """
        self.config = config
        self.connection = self._create_connection()

    def _create_connection(self) -> DatabaseConnection:
        """Create appropriate database connection based on config"""
        if self.config.database_type == "sqlite":
            return SQLiteConnection(self.config.connection_string)
        elif self.config.database_type == "mysql":
            return MySQLConnection(self.config.connection_string)
        elif self.config.database_type == "snowflake":
            # For future implementation - would require snowflake-connector-python
            raise NotImplementedError("Snowflake connection not yet implemented")
        else:
            raise ValueError(f"Unsupported database type: {self.config.database_type}")

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        return self.connection.execute_query(query)

    def execute_count_query(self, query: str) -> int:
        """Execute a COUNT query and return the result"""
        return self.connection.execute_count_query(query)

    def get_table_columns(self) -> List[Dict[str, str]]:
        """Get column information for the configured table"""
        return self.connection.get_table_columns(self.config.table_name)

    def get_table_count(self) -> int:
        """Get total row count for the configured table"""
        return self.connection.get_table_count(self.config.table_name)

    @property
    def table_name(self) -> str:
        """Get the configured table name"""
        return self.config.table_name

    @property
    def escape_char(self) -> str:
        """Get the SQL escape character for this database"""
        return self.config.escape_char
