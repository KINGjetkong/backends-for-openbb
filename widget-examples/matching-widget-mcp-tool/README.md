# Matching Widget to MCP Tool - Reference Example

Reference implementation for widget citations when MCP tools are used. Start both servers:

```bash
# Start the MCP server  
python mcp_server.py

# Start the widget backend
python main.py
```

## 1. Connecting MCP Server

Go to **Settings → MCP Servers** and add:
- **Server name**: "Financial Data"
- **Server URL**: `http://localhost:8014/mcp`

![MCP Server Connection](https://openbb-cms.directus.app/assets/6d66dcf3-98c0-4150-aace-035a063df35a.png)

Verify the tool is available:

![MCP Tool Available](https://openbb-cms.directus.app/assets/643af141-6b8c-4828-b7dc-2242560d71f8.png)

## 2. Connecting OpenBB Widget

Go to **Settings → Widgets** and add:
- **Backend name**: Any name
- **Backend URL**: `http://localhost:8012`

![Widget Backend Connection](https://openbb-cms.directus.app/assets/77a2c0d8-3a9b-47a7-933e-85e7131ef954.png)

The widget includes MCP tool reference in `widgets.json`:

```python
"mcp_tool": {
    "mcp_server": "Financial Data",           # Must match MCP server name exactly
    "tool_id": "get_company_revenue_data"     # Must match MCP tool name exactly  
}
```

![Widget with MCP Configuration](https://openbb-cms.directus.app/assets/1603ad32-6bd2-43bc-a4cc-553cb4163c34.png)

## 3. Matching Widget Outcome

Ask the Copilot: *"Use the financial data MCP tool and get company revenue data for AAPL"*

**Toast notification appears:**

![Matching Widget Found](https://openbb-cms.directus.app/assets/655482de-3d2b-426c-8315-dbb579c78f16.png)

**Widget citation with `*` in response:**

![Widget Citation](https://openbb-cms.directus.app/assets/d2c50edb-43e2-4771-9125-b31117501a61.png)

**Hover to add widget to dashboard:**

![Add to Dashboard](https://openbb-cms.directus.app/assets/a719abc4-9b2f-41c7-b1a8-dd84fc707b77.png)

**Interactive widget with same parameters:**

![Interactive Widget](https://openbb-cms.directus.app/assets/6f0df91c-195f-48c4-9fbe-13ed589245a9.png)

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