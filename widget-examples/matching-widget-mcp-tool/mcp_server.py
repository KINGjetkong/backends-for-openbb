"""
FastMCP Server for Revenue Data Tool.

This MCP server provides a tool for retrieving company revenue data,
accessible via HTTP at localhost:8014/mcp endpoint.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

# Import the revenue data functions from main.py
from main import _get_ticker_info, _generate_revenue_data

# Initialize FastMCP server
mcp = FastMCP("Revenue Data MCP Server")

# Get the Starlette app and add CORS middleware
app = mcp.streamable_http_app()

# Add CORS middleware with proper header exposure for MCP session management
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this more restrictively in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["mcp-session-id", "mcp-protocol-version"],  # Allow client to read session ID
    max_age=86400,
)


@mcp.tool()
def get_company_revenue_data(
    ticker: str = "AAPL",
    start_date: Optional[str] = None
) -> str:
    """
    Get company revenue data for a specific ticker symbol.
    
    Returns 7 days of revenue data including daily revenue, percentage change,
    trend data, and status for the selected company.
    
    Args:
        ticker: Company ticker symbol (AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA)
        start_date: Start date in YYYY-MM-DD format (defaults to 7 days ago)
    
    Returns:
        JSON string containing revenue data for the company
    """
    # Parse the start date or use default
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            start_dt = datetime.now() - timedelta(days=7)
    else:
        start_dt = datetime.now() - timedelta(days=7)
    
    # Validate ticker
    valid_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]
    if ticker not in valid_tickers:
        return json.dumps({
            "error": f"Invalid ticker '{ticker}'. Valid tickers: {', '.join(valid_tickers)}"
        })
    
    # Generate revenue data for 7 days
    revenue_data = []
    for day_offset in range(7):
        daily_data = _generate_revenue_data(start_dt, ticker, day_offset)
        revenue_data.append(daily_data)
    
    # Sort by date for better display
    revenue_data.sort(key=lambda x: x["date"])
    
    # Get company info for context
    ticker_info = _get_ticker_info()
    company_info = ticker_info.get(ticker, {"name": "Unknown Company", "sector": "Unknown"})
    
    # Format response
    response = {
        "ticker": ticker,
        "company_name": company_info["name"],
        "sector": company_info["sector"],
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "end_date": (start_dt + timedelta(days=6)).strftime("%Y-%m-%d"),
        "data": revenue_data,
        "summary": {
            "total_days": len(revenue_data),
            "avg_daily_revenue": sum(item["value"] for item in revenue_data) / len(revenue_data),
            "total_revenue": sum(item["value"] for item in revenue_data)
        }
    }
    
    return json.dumps(response, indent=2)


if __name__ == "__main__":
    # Use PORT environment variable
    port = int(os.environ.get("PORT", 8014))
    
    print("Starting FastMCP Revenue Data server...")
    print(f"MCP server will be available at: http://localhost:{port}/mcp")
    print("Tool available: get_company_revenue_data")

    # Run the MCP server with HTTP transport using uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all interfaces for containerized deployment
        port=port,
        log_level="debug"
    )