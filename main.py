
from __future__ import annotations

from fastapi import FastAPI

from bot.client import DEFAULT_BASE_URL
from bot import __version__

app = FastAPI(
    title="Binance Futures Testnet Trading Bot",
    version=__version__,
    description="Health endpoint for the CLI-based Binance Futures Testnet trading bot.",
)


@app.get("/")
def home() -> dict:
    """Simple landing endpoint for Vercel deployment checks."""
    return {
        "status": "ok",
        "project": "Binance Futures Testnet Trading Bot",
        "message": "Deployment is working. Use cli.py locally to place MARKET and LIMIT testnet orders.",
        "cli_examples": [
            "python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001",
            "python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000",
        ],
        "default_base_url": DEFAULT_BASE_URL,
    }


@app.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}
