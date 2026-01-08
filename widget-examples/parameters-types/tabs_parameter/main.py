import json
import random
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

origins = [
    "https://pro.openbb.co",
    "https://excel.openbb.co",
    "http://localhost:1420",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_PATH = Path(__file__).parent.resolve()

# Sample companies for mock data
COMPANIES = [
    {"symbol": "AAPL", "company": "Apple Inc."},
    {"symbol": "MSFT", "company": "Microsoft Corp."},
    {"symbol": "GOOGL", "company": "Alphabet Inc."},
    {"symbol": "AMZN", "company": "Amazon.com Inc."},
    {"symbol": "NVDA", "company": "NVIDIA Corp."},
    {"symbol": "META", "company": "Meta Platforms Inc."},
    {"symbol": "TSLA", "company": "Tesla Inc."},
    {"symbol": "JPM", "company": "JPMorgan Chase & Co."},
]


def generate_random_data(category: str):
    """Generate random mock data based on category - each category has DIFFERENT columns."""
    data = []

    for company in COMPANIES:
        row = {
            "symbol": company["symbol"],
            "company": company["company"],
        }

        if category == "liquidity":
            # Liquidity ratios - specific columns for this tab
            row["current_ratio"] = round(random.uniform(0.5, 4.0), 2)
            row["quick_ratio"] = round(random.uniform(0.3, 3.5), 2)
            row["cash_ratio"] = round(random.uniform(0.1, 2.0), 2)
            row["working_capital_m"] = round(random.uniform(-5000, 50000), 0)

        elif category == "efficiency":
            # Efficiency ratios - DIFFERENT columns than liquidity
            row["asset_turnover"] = round(random.uniform(0.3, 2.0), 2)
            row["inventory_turnover"] = round(random.uniform(2.0, 50.0), 1)
            row["receivables_turnover"] = round(random.uniform(3.0, 20.0), 1)
            row["days_sales_outstanding"] = round(random.uniform(20, 90), 0)
            row["days_inventory"] = round(random.uniform(10, 180), 0)

        elif category == "profitability":
            # Profitability ratios - DIFFERENT columns
            row["gross_margin_pct"] = round(random.uniform(20, 80), 1)
            row["operating_margin_pct"] = round(random.uniform(5, 50), 1)
            row["net_margin_pct"] = round(random.uniform(2, 40), 1)
            row["roe_pct"] = round(random.uniform(5, 150), 1)
            row["roa_pct"] = round(random.uniform(2, 30), 1)
            row["roic_pct"] = round(random.uniform(5, 50), 1)

        elif category == "leverage":
            # Leverage ratios - DIFFERENT columns
            row["debt_to_equity"] = round(random.uniform(0.1, 3.0), 2)
            row["debt_to_assets"] = round(random.uniform(0.05, 0.6), 2)
            row["interest_coverage"] = round(random.uniform(2.0, 200.0), 1)
            row["debt_to_ebitda"] = round(random.uniform(0.5, 8.0), 2)

        data.append(row)

    return data


@app.get("/")
def read_root():
    return {"Info": "Tabs Parameter Example for OpenBB Custom Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


@app.get("/financial_ratios_dynamic")
def get_financial_ratios_dynamic(category: str = "liquidity"):
    """
    Get financial ratios with DIFFERENT columns per category.
    The table columns will change when switching tabs.
    Data is randomly generated to demonstrate the feature.
    """
    return generate_random_data(category)


@app.get("/financial_ratios_static")
def get_financial_ratios_static(category: str = "liquidity"):
    """
    Same columns for all tabs - only data values change.
    This is useful when you want consistent columns across tabs.
    """
    data = []
    for company in COMPANIES:
        row = {
            "symbol": company["symbol"],
            "company": company["company"],
            "category": category,
            "metric_1": round(random.uniform(0.5, 100), 2),
            "metric_2": round(random.uniform(0.5, 100), 2),
            "metric_3": round(random.uniform(0.5, 100), 2),
        }
        data.append(row)
    return data


@app.get("/comparison_with_period")
def get_comparison_with_period(category: str = "liquidity", period: str = "annual"):
    """
    Example showing tabs combined with other parameters.
    'category' is controlled by tabs, 'period' is a regular dropdown.
    Columns change based on selected tab.
    """
    data = generate_random_data(category)

    # Add period info to each row
    for row in data:
        row["period"] = period
        row["fiscal_year"] = 2024 if period == "annual" else "Q4 2024"

    return data
