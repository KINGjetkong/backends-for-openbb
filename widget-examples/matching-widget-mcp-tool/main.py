"""
AgGrid Widget Demo for OpenBB Workspace.

This module provides a FastAPI application with an AgGrid table widget
that demonstrates dynamic data generation based on user parameters.
"""

# Import required libraries
import asyncio
import random
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize empty dictionary for widgets
WIDGETS = {}

# Decorator that registers a widget configuration in the WIDGETS dictionary
def register_widget(widget_config):
    """
    Decorator that registers a widget configuration in the WIDGETS dictionary.

    Args:
        widget_config (dict): The widget configuration to add to the WIDGETS
            dictionary. This should follow the same structure as other entries
            in WIDGETS.

    Returns:
        function: The decorated function.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Call the original function
            return await func(*args, **kwargs)
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Call the original function
            return func(*args, **kwargs)
        # Extract the endpoint from the widget_config
        endpoint = widget_config.get("endpoint")
        if endpoint:
            # Add an id field to the widget_config if not already present
            if "widgetId" not in widget_config:
                widget_config["widgetId"] = endpoint

            # Use id as the key to allow multiple widgets per endpoint
            widget_id = widget_config["widgetId"]
            WIDGETS[widget_id] = widget_config

        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator

# Initialize FastAPI application with metadata
app = FastAPI(
    title="AgGrid Widget Demo",
    description="Demo backend with AgGrid table widget for OpenBB Workspace",
    version="0.0.1"
)

# Define allowed origins for CORS (Cross-Origin Resource Sharing)
origins = [
    "https://pro.openbb.co",
    "https://pro.openbb.dev",
    "http://localhost:1420"
]

# Configure CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

ROOT_PATH = Path(__file__).parent.resolve()

@app.get("/")
def read_root():
    """Root endpoint that returns basic information about the API"""
    return {"Info": "AgGrid Widget Demo API"}

# Endpoint that returns the registered widgets configuration
@app.get("/widgets.json")
def get_widgets():
    """Returns the configuration of all registered widgets"""
    return WIDGETS

# Revenue Data Widget with ticker selection and date range
@register_widget({
    "name": "Company Revenue Dashboard",
    "description": "Revenue metrics dashboard with ticker selection and date range filtering",
    "type": "table",
    "endpoint": "revenue_mockup_data",
    "gridData": {"w": 24, "h": 12},
    "mcp_tool": {
      "mcp_server": "Financial Data",
      "tool_id": "get_company_revenue_data"
    },
    "params": [
        {
            "paramName": "start_date",
            "description": "Select the start date for revenue data",
            "value": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "label": "Start Date",
            "type": "date"
        },
        {
            "paramName": "ticker",
            "description": "Select company ticker symbol",
            "value": "AAPL",
            "label": "Ticker Symbol",
            "type": "text",
            "multiSelect": False,
            "options": [
                {"value": "AAPL", "label": "Apple Inc. (AAPL)"},
                {"value": "MSFT", "label": "Microsoft Corp. (MSFT)"},
                {"value": "GOOGL", "label": "Alphabet Inc. (GOOGL)"},
                {"value": "AMZN", "label": "Amazon.com Inc. (AMZN)"},
                {"value": "TSLA", "label": "Tesla Inc. (TSLA)"},
                {"value": "META", "label": "Meta Platforms Inc. (META)"},
                {"value": "NVDA", "label": "NVIDIA Corp. (NVDA)"}
            ]
        }
    ],
    "data": {
        "table": {
            "enableCharts": True,
            "showAll": False,
            "chartView": {
                "enabled": True,
                "chartType": "column"
            },
            "columnsDefs": [
                {
                    "field": "date",
                    "headerName": "Date",
                    "cellDataType": "dateString",
                    "width": 120,
                    "pinned": "left",
                    "chartDataType": "category"
                },
                {
                    "field": "company",
                    "headerName": "Company",
                    "cellDataType": "text",
                    "width": 150,
                    "renderFn": "titleCase"
                },
                {
                    "field": "metric_name",
                    "headerName": "Metric",
                    "cellDataType": "text",
                    "width": 150
                },
                {
                    "field": "value",
                    "headerName": "Value",
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "width": 120,
                    "chartDataType": "series"
                },
                {
                    "field": "change",
                    "headerName": "Revenue Change %",
                    "cellDataType": "text",
                    "renderFn": "greenRed",
                    "width": 140,
                    "pinned": "right"
                },
                {
                    "field": "trend",
                    "headerName": "7-Day Trend",
                    "width": 150,
                    "sparkline": {
                        "type": "line",
                        "options": {
                            "stroke": "#2563eb",
                            "strokeWidth": 2,
                            "markers": {
                                "enabled": True,
                                "size": 2
                            },
                            "pointsOfInterest": {
                                "maximum": {
                                    "fill": "#22c55e",
                                    "stroke": "#16a34a",
                                    "size": 4
                                },
                                "minimum": {
                                    "fill": "#ef4444",
                                    "stroke": "#dc2626",
                                    "size": 4
                                }
                            }
                        }
                    }
                },
                {
                    "field": "status",
                    "headerName": "Status",
                    "cellDataType": "text",
                    "width": 100,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {
                                "condition": "eq",
                                "value": "Good",
                                "color": "green",
                                "fill": False
                            },
                            {
                                "condition": "eq",
                                "value": "Warning",
                                "color": "#FFA500",
                                "fill": False
                            },
                            {
                                "condition": "eq",
                                "value": "Critical",
                                "color": "red",
                                "fill": False
                            }
                        ]
                    }
                }
            ]
        }
    }
})
def _get_ticker_info():
    """Return company information for ticker symbols."""
    return {
        "AAPL": {"name": "Apple Inc.", "sector": "Technology"},
        "MSFT": {"name": "Microsoft Corp.", "sector": "Technology"},
        "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology"},
        "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
        "TSLA": {"name": "Tesla Inc.", "sector": "Consumer Discretionary"},
        "META": {"name": "Meta Platforms Inc.", "sector": "Technology"},
        "NVDA": {"name": "NVIDIA Corp.", "sector": "Technology"}
    }


def _generate_revenue_data(start_dt, ticker, day_offset):
    """Generate revenue data for a specific ticker on a specific day."""
    current_date = (start_dt + timedelta(days=day_offset)).strftime("%Y-%m-%d")
    
    # Use the date and ticker to seed randomness for consistency
    seed_value = hash(f"{current_date}{ticker}")
    random.seed(seed_value)
    
    # Get company info
    ticker_info = _get_ticker_info()
    company_info = ticker_info.get(ticker, {"name": "Unknown Company", "sector": "Unknown"})
    
    # Generate base revenue value based on ticker (some companies are larger)
    ticker_multipliers = {
        "AAPL": 100, "MSFT": 80, "GOOGL": 70, "AMZN": 90,
        "TSLA": 30, "META": 60, "NVDA": 25
    }
    base_multiplier = ticker_multipliers.get(ticker, 50)
    
    # Generate revenue value with daily variation
    base_revenue = base_multiplier * 1000000 * (1 + day_offset * 0.02)  # Growth over time
    daily_revenue = int(base_revenue * (0.9 + random.random() * 0.2))
    
    # Generate change percentage (more realistic range)
    change = -8 + random.random() * 16
    
    # Generate trend data (7 points for sparkline)
    trend_base = daily_revenue
    trend = [int(trend_base * (0.95 + random.random() * 0.1)) for _ in range(7)]
    
    # Determine status based on change
    if change > 3:
        status = "Good"
    elif change < -3:
        status = "Critical"
    else:
        status = "Warning"
    
    return {
        "date": current_date,
        "company": company_info["name"],
        "metric_name": "Daily Revenue",
        "value": daily_revenue,
        "change": f"{round(change, 2)}%",
        "trend": trend,
        "status": status
    }


@app.get("/revenue_mockup_data")
def revenue_mockup_data(
    start_date: str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
    ticker: str = "AAPL"
):
    """
    Generate revenue data for the selected ticker symbol.

    The data changes based on:
    - start_date: Determines the date range for the revenue data
    - ticker: The company ticker symbol to generate data for
    """
    # Parse the start date
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        start_dt = datetime.now() - timedelta(days=7)
    
    # Validate ticker
    valid_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]
    if ticker not in valid_tickers:
        ticker = "AAPL"  # Default fallback
    
    # Generate revenue data for 7 days
    revenue_data = []
    for day_offset in range(7):
        daily_data = _generate_revenue_data(start_dt, ticker, day_offset)
        revenue_data.append(daily_data)
    
    # Sort by date for better display
    revenue_data.sort(key=lambda x: x["date"])
    
    return revenue_data

# Run the application
if __name__ == "__main__":
    import uvicorn
    print("Starting AgGrid Widget Demo server...")
    print("Visit http://localhost:8012/widgets.json to see registered widgets")
    print("The widget endpoint is available at http://localhost:8012/revenue_mockup_data")
    uvicorn.run(app, host="0.0.0.0", port=8012)
