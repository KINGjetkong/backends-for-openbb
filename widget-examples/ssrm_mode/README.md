# SSRM AgGrid Demo Backend - Quickstart Guide

This guide will help you set up, customize, and run the Server-Side Row Model (SSRM) AgGrid backend service for any dataset and database.

This demo uses fake financial data for demonstration purposes and is useful when you have more than 200,000 rows and notice performance issues while using the service.

## 📋 Overview

This is a modular FastAPI backend that provides Server-Side Row Model functionality for AgGrid, supporting:

- **Multiple Database Types**: SQLite, MySQL, Snowflake (easily extensible)
- **Advanced AgGrid Features**: Sorting, filtering, pagination, grouping, aggregation
- **High Performance**: Optimized queries for large datasets
- **Demo Data**: Includes fake financial data for testing and demonstration

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Navigate to the project directory
cd ssrm_mode

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Generate Demo Data (Optional)

This demo comes with a script to generate fake financial data for testing:

```bash
# Generate demo database with 50,000 fake records
python create_demo_db.py
```

Alternatively, you can use your own dataset. The backend supports multiple database types:

- **SQLite**: Ideal for local development and small to medium datasets. Ensure your `.db` file is in the project directory or provide the correct path in the configuration.
- **MySQL**: Suitable for larger datasets and production environments. Configure your MySQL connection details in the application settings.
- **Snowflake**: Best for enterprise-level datasets and advanced analytics. Ensure your Snowflake credentials and configurations are correctly set up.

You can easily extend support for other databases by implementing the necessary connection and query logic in the backend code.

### 3. Start the Service

```bash
# Method 1: Direct Python execution
python main.py

# Method 2: Using uvicorn directly
uvicorn main:app --host 127.0.0.1 --port 8008 --reload

# Method 3: Custom host/port
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

### 4. Test the Service

The service will be available at `http://127.0.0.1:8008`

**Test endpoints:**
```bash
# Basic health check
curl http://127.0.0.1:8008/

# Get widget configuration
curl http://127.0.0.1:8008/widgets.json

# Test SSRM endpoint with sample data
curl -X POST http://127.0.0.1:8008/data-ssrm \
  -H "Content-Type: application/json" \
  -d '{
    "startRow": 0,
    "endRow": 10,
    "sortModel": [],
    "filterModel": {},
    "rowGroupCols": [],
    "groupKeys": []
  }'
```

### 5. Add/Edit the widgets.json

Set up your widgets in the widgets.json to work with OpenBB Workspace.

**Update `widgets.json`:**

```json
{
    "myDataSSRM": {
        "name": "My Custom Dataset",
        "description": "Custom data with SSRM functionality",
        "category": "my-category",
        "searchCategory": "data-ssrm",
        "type": "ssrm_table", 
        "endpoint": "data-ssrm",
        "gridData": {
            "w": 24,
            "h": 16
        }
    }
}

```
## 🔧 Customization for Different Databases

### Option 1: SQLite (Easiest)

**For new SQLite database:**

1. Replace `demo_data.db` with your database file
2. Update `main.py`:

```python
# Update the database manager initialization
db_manager = create_database_manager(
    database_type="sqlite",
    file_path=Path(__file__).parent / "your_database.db",  # Change this
    table_name="your_table_name",  # Change this
)
```


### Option 2: MySQL

**Setup MySQL connection:**

1. Ensure MySQL is installed and running
2. Update `main.py`:

```python
# Update the database manager initialization
db_manager = create_database_manager(
    database_type="mysql",
    connection_config={
        "host": "localhost",
        "database": "your_database",
        "user": "your_username", 
        "password": "your_password",
        "port": 3306
    },
    table_name="your_table_name",
)
```

3. Install additional MySQL dependencies if needed:
```bash
pip install mysql-connector-python
```

### Option 3: Other Databases (Snowflake, PostgreSQL, etc.)

**To add support for a new database type:**

1. **Extend `database.py`**: Add a new connection class (see `MySQLConnection` example)
2. **Update `config.py`**: Add configuration method for your database
3. **Update `helpers.py`**: Add factory method support

**Example for PostgreSQL:**

```python
# In database.py
class PostgreSQLConnection:
    def __init__(self, connection_config):
        import psycopg2
        self.config = connection_config
    
    def get_connection(self):
        return psycopg2.connect(**self.config)
    
    # Implement other required methods...

# In helpers.py - update create_database_manager()
elif database_type == "postgresql":
    return DatabaseManager(PostgreSQLConnection(connection_config), table_name, escape_char)
```
