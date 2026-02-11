# Unified OpenBB Backend - 35+ Trading Tools

A FastAPI backend that integrates 35+ trading tools into OpenBB Workspace as widgets.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the backend
python main.py
```

Backend will start at `http://127.0.0.1:5055`

## Connect to OpenBB Workspace

1. Open OpenBB Workspace
2. Go to **Apps** → **Connect Backend**
3. Enter:
   - **Name**: `Unified Trading Backend`
   - **Endpoint URL**: `http://127.0.0.1:5055`
4. Click **Test and Add**

## Available Widgets

### Market Data
- **Market Overview** - Real-time indices and stocks
- **Stock Quote** - Detailed quote for any symbol
- **Historical Prices** - 30-day price charts

### Options
- **Options Chain** - Full options chain
- **Options Flow Scanner** - Unusual activity detector
- **Greeks Dashboard** - Options greeks analysis

### AI Tools
- **AI Sentiment Analysis** - Market sentiment
- **AI Trade Signals** - AI-generated signals
- **Price Prediction** - ML price predictions

### Portfolio
- **Portfolio Summary** - P&L overview
- **Risk Metrics** - Risk analysis

### Technical
- **Technical Analysis** - Key indicators
- **Support & Resistance** - Price levels

### Research
- **Company News** - Latest news
- **Earnings Calendar** - Upcoming earnings

### Crypto
- **Crypto Prices** - Top cryptocurrencies

### Economy
- **Economic Calendar** - Economic events

## Integrated Tools (35+)

| Tool | Category | Status |
|------|----------|--------|
| GamestonkTerminal/OpenBB | Platform | ✅ |
| Options Dataset (53M) | Data | ✅ |
| AI Trade Predictor | AI | ✅ |
| 0DTE Options Bot | Trading | ✅ |
| Greeks Dashboard | Options | ✅ |
| ChartScan AI | Technical | ✅ |
| DeepSeek Trading Bot | AI | ✅ |
| Prime Flow AI | Options | ✅ |
| Probability Engine | Analysis | ✅ |
| QuantConnect/Lean | Backtest | ✅ |
| Freqtrade | Crypto | ✅ |
| Trader Copilot | AI | ✅ |

## API Documentation

Once running, visit: `http://127.0.0.1:5055/docs`

## License

MIT
