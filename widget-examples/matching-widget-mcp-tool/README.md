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
