# Matching Widget to MCP Tool - Reference Example

This project serves as a reference implementation for the [Matching widget to MCP tool](https://docs.openbb.co/pro/widgets/matching-widget-to-mcp-tool) documentation. It demonstrates how to configure widget citations that automatically appear when specific MCP tools are used.

## What This Example Demonstrates

When a specific MCP tool is invoked in OpenBB Copilot, this example shows how to:
- Configure corresponding widget citations through `widgets.json` 
- Automatically generate widget citations marked with `*` in the AI response
- Allow users to add the matching widget to their dashboard with the same parameters used by the MCP tool

## Project Components

- **`mcp_server.py`** - MCP server exposing the `get_company_revenue_data` tool (primary)
- **`main.py`** - OpenBB widget backend that can cite the MCP tool (secondary)
- **Widget-MCP Matching** - Configuration in `widgets.json` that creates the citation link

## Quick Start

### 1. Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Start Both Servers

```bash
# Terminal 1: Start the widget backend
python main.py

# Terminal 2: Start the MCP server  
python mcp_server.py
```

Verify both are running:
- Widget backend: http://localhost:8012/widgets.json
- MCP server: http://localhost:8014/mcp

## Backend for OpenBB (`main.py`)

The Backend for OpenBB provides a FastAPI server that serves an OpenBB Workspace widget for displaying company revenue data.

### Features

- **📅 Date Picker**: Select start date for revenue data (7-day range)
- **📊 Ticker Dropdown**: Select from major tech stocks (AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA)
- **💰 Revenue Metrics**: Daily revenue data with percentage changes and trends
- **Advanced Table Features**: Column definitions, formatting, sorting, filtering
- **Sparklines**: 7-day trend visualization with min/max highlighting
- **Color Coding**: Status indicators (Good/Warning/Critical)
- **Chart View**: Toggle between table and column chart views

### Integration with OpenBB Workspace

1. **Open OpenBB Workspace**
2. **Add Custom Backend**:
   - Go to Settings → Widgets
   - Add custom backend URL: `http://localhost:8012`
3. **Widget Discovery**:
   - The widget "Company Revenue Dashboard" should appear in the widgets menu
4. **Add to Dashboard**:
   - Drag the widget to your dashboard
   - Configure the parameters as needed

### Widget Configuration

The widget accepts these parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start_date` | Date | 7 days ago | Starting date for revenue data |
| `ticker` | Dropdown | "AAPL" | Company ticker symbol |

#### Available Tickers:
- **AAPL**: Apple Inc.
- **MSFT**: Microsoft Corp.
- **GOOGL**: Alphabet Inc.
- **AMZN**: Amazon.com Inc.
- **TSLA**: Tesla Inc.
- **META**: Meta Platforms Inc.
- **NVDA**: NVIDIA Corp.

## MCP Server (`mcp_server.py`)

The MCP Server provides a FastMCP server that exposes company revenue data as an MCP tool, making it accessible to AI assistants and other MCP-compatible clients.

### Features

- **🤖 MCP Tool**: `get_company_revenue_data` tool for AI assistants
- **📈 Revenue Analytics**: 7 days of revenue data with summary statistics
- **🔧 Flexible Parameters**: Ticker symbol and date range selection
- **🌐 HTTP Transport**: Accessible via HTTP at `/mcp` endpoint
- **🔗 CORS Support**: Properly configured for cross-origin requests

### MCP Tool Documentation

**Tool Name**: `get_company_revenue_data`

**Parameters**:
- `ticker` (string): Company ticker symbol (default: "AAPL")
  - Valid values: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA
- `start_date` (string, optional): Start date in YYYY-MM-DD format (defaults to 7 days ago)

**Returns**: JSON string with revenue data including:
- Company information (name, sector)
- 7 days of revenue data with trends
- Summary statistics (total revenue, average daily revenue)

### Integration with AI Assistants

For Claude Desktop integration, add to your `~/.claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "revenue-data": {
      "command": "python",
      "args": ["/path/to/your/project/mcp_server.py"]
    }
  }
}
```

## Complete Integration Example

This section walks through the exact steps to set up widget-to-MCP tool matching, following the same flow as the official documentation.

### How It Works

The primary workflow starts with MCP tools. When a specific MCP tool is invoked, OpenBB Workspace checks if there's a widget configured to cite that exact tool. If found:
1. A notification appears: "Matching widget found"
2. A widget citation is automatically generated and attached to the MCP tool response  
3. The citation allows users to add the corresponding widget to their dashboard

> **Important**: The widget's `mcp_server` and `tool_id` must match exactly with the existing MCP server configuration.

### Step 1: Connect MCP Server (Primary)

**The MCP server must be connected first**, as this is what drives the workflow. Connect your MCP server to OpenBB Workspace:

1. Go to **Settings → MCP Servers**
2. Add server with name: **"Financial Data"** 
3. Add server URL: `http://localhost:8014/mcp`

![MCP Server Connection](https://openbb-cms.directus.app/assets/6d66dcf3-98c0-4150-aace-035a063df35a.png)

*The MCP server name "Financial Data" must match exactly with the widget configuration.*

Verify the tool is available:

![MCP Tool Available](https://openbb-cms.directus.app/assets/643af141-6b8c-4828-b7dc-2242560d71f8.png)

*Confirm "get_company_revenue_data" tool is listed and matches the widget `tool_id`.*

### Step 2: Configure Widget to Cite the MCP Tool

**Now that the MCP server exists**, configure a widget to automatically cite it when the tool is used. The widget configuration in `main.py` includes the citation metadata:

```python
"mcp_tool": {
    "mcp_server": "Financial Data",           # References the existing MCP server name
    "tool_id": "get_company_revenue_data"     # References the existing MCP tool name  
}
```

Connect the widget backend:

1. Go to **Settings → Widgets**
2. Add backend name: Any name (e.g., "Revenue Data Backend")
3. Add backend URL: `http://localhost:8012`

![Widget Backend Connection](https://openbb-cms.directus.app/assets/77a2c0d8-3a9b-47a7-933e-85e7131ef954.png)

*The backend name can be anything, but the URL must point to your widget server.*

The widget will appear with the MCP tool configuration:

![Widget with MCP Configuration](https://openbb-cms.directus.app/assets/1603ad32-6bd2-43bc-a4cc-553cb4163c34.png)

*The `mcp_tool` property configures this widget to automatically cite the existing MCP tool.*

### Step 3: Experience the Citation

Now test the MCP-to-widget citation flow:

1. **Use the MCP Tool**: Ask the Copilot to use the existing MCP tool:
   > "Use the financial data MCP tool and get company revenue data for AAPL"

2. **Automatic Citation Detection**: A toast appears when the widget citation is found:

![Matching Widget Found](https://openbb-cms.directus.app/assets/655482de-3d2b-426c-8315-dbb579c78f16.png)

3. **View the Citation**: The response includes a widget citation with `*`:

![Widget Citation](https://openbb-cms.directus.app/assets/d2c50edb-43e2-4771-9125-b31117501a61.png)

*The asterisk indicates this is a matching widget citation.*

4. **Add to Dashboard**: Hover over the citation to add the widget:

![Add to Dashboard](https://openbb-cms.directus.app/assets/a719abc4-9b2f-41c7-b1a8-dd84fc707b77.png)

5. **Interactive Widget**: The widget appears with the same parameters:

![Interactive Widget](https://openbb-cms.directus.app/assets/6f0df91c-195f-48c4-9fbe-13ed589245a9.png)

*Now you can interact with parameters, charting, and all OpenBB widget features.*

## Data Generation Strategy

The widget uses a **deterministic data generation** approach:

1. **Consistency**: Same parameters always produce identical data
2. **Seeded Randomness**: Uses hash of (date + company + category) as seed
3. **Dynamic Range**: Generates 7 days × 5 companies = 35 data points
4. **Realistic Values**: Base values scaled by company size and time progression

### Example Data Flow:
```
Input: start_date="2024-01-01", company_prefix="Finance", data_category="operational"
↓
Output: 35 rows with companies like "Finance Corp", "Finance Systems" 
        showing Production, Efficiency, etc. metrics from Jan 1-7
```

## Technical Details

### Project Structure
```
matching-widget-mcp-tool/
├── main.py           # OpenBB Widget FastAPI application
├── mcp_server.py     # HTTP API server for revenue data
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

### Key Components

#### 1. Widget Registration
```python
@register_widget({
    "name": "Company Revenue Dashboard",
    "type": "table",
    "endpoint": "dynamic_aggrid_table",
    "params": [...],
    "data": {"table": {"columnsDefs": [...]}}
})
```

#### 2. Data Generation Functions
- `_get_ticker_info()`: Returns company information for ticker symbols
- `_generate_revenue_data()`: Creates revenue data for single company/day
- `dynamic_aggrid_table()`: Main endpoint handling parameters

#### 3. HTTP API Components
- `FastAPI`: Web framework for REST endpoints
- `get_company_revenue_data()`: GET endpoint function
- `post_company_revenue_data()`: POST endpoint function
- `RevenueDataRequest`: Pydantic model for validation

#### 4. AgGrid Configuration
- **Column Definitions**: Data types, formatting, rendering functions
- **Sparklines**: Trend visualization with styling options
- **Chart Integration**: Seamless table-to-chart conversion

### CORS Configuration

The application is configured to work with OpenBB Workspace domains:
- `https://pro.openbb.co`
- `https://pro.openbb.dev`
- `http://localhost:1420` (local development)

## Customization

### Adding New Metrics Categories

1. **Update metrics map** in `_get_metrics_map()`:
```python
"custom_category": ["Metric1", "Metric2", "Metric3"]
```

2. **Add dropdown option** in widget parameters:
```python
{"value": "custom_category", "label": "Custom Category"}
```

### Modifying Data Generation

- **Change time range**: Modify the `range(7)` loop
- **Add companies**: Extend `company_suffixes` list
- **Adjust values**: Modify `base_value` calculation
- **New status logic**: Update status determination rules

### Styling Customization

- **Colors**: Modify `renderFnParams.colorRules`
- **Sparklines**: Adjust `sparkline.options`
- **Grid Layout**: Change `gridData` dimensions

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Change port in main.py or kill existing process
   lsof -ti:8000 | xargs kill -9
   ```

2. **CORS Errors**:
   - Ensure OpenBB Workspace domain is in `origins` list
   - Check that server is accessible from workspace

3. **Widget Not Appearing**:
   - Verify `/widgets.json` endpoint returns data
   - Check OpenBB Workspace backend configuration
   - Confirm server is running and accessible

### Development Tips

- **Live Reload**: Server runs with `reload=True` for development
- **Debug Data**: Visit endpoint URLs directly to inspect JSON output
- **Parameter Testing**: Use query parameters in browser: `?start_date=2024-01-01&company_prefix=Test&data_category=hr`

## Dependencies

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Pydantic**: Data validation and serialization
- **Standard Library**: `datetime`, `random`, `functools`, `asyncio`, `pathlib`

## License

This is a demonstration project for OpenBB Workspace widget development.

## Support

For questions about:
- **OpenBB Workspace**: Visit [OpenBB Documentation](https://docs.openbb.co/)
- **Widget Development**: Check [OpenBB Widget Docs](https://docs.openbb.co/pro/widgets)
- **This Implementation**: Review the code comments and examples in `main.py`