# Binance Futures Testnet Trading Bot

A small Python 3 CLI application for placing **MARKET** and **LIMIT** orders on **Binance Futures Testnet USDT-M**.

This project was built for the Python Developer application task. It uses direct REST API calls with `httpx`, HMAC-SHA256 signing, input validation, structured files, error handling, and file logging.

## Features

- Places Binance Futures Testnet USDT-M orders using `POST /fapi/v1/order`
- Supports:
  - `MARKET`
  - `LIMIT`
  - `BUY`
  - `SELL`
- CLI validation for:
  - symbol
  - side
  - order type
  - quantity
  - limit price
- Clean terminal output:
  - request summary
  - response details
  - success/failure message
- Logs API requests, responses, validation errors, API errors, and network errors
- Enhanced CLI UX with optional `--interactive` prompt mode

## Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py            # Binance REST client wrapper
    orders.py            # Order model and placement logic
    validators.py        # Input validation
    logging_config.py    # File logger setup
  logs/
    market_order_sample.log
    limit_order_sample.log
  cli.py                 # CLI entry point
  main.py                # Vercel/FastAPI web entry point
  pyproject.toml         # Python/Vercel project metadata
  README.md
  requirements.txt
  .env.example
```

## Vercel Deployment Note

This project is mainly a CLI trading bot. Vercel expects a Python web application entrypoint, so this repository includes `main.py` with a small FastAPI `app`.

Use Vercel only to verify/deploy the project page and health endpoint:

```bash
vercel
```

After deployment, open:

```text
/
/health
```

Actual order placement should be run from the CLI on your local machine or VM because the assignment requires command-line input/output and log-file submission.

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

## Requirements

- Python 3.10+
- Binance Futures Testnet account
- Binance Futures Testnet API key and secret

## Setup

### 1. Clone or unzip the project

```bash
cd trading_bot
```

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Copy the example file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then edit `.env`:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
BINANCE_FUTURES_BASE_URL=https://testnet.binancefuture.com
```

> Do not commit your real `.env` file or API secret to GitHub.

## Important Testnet URL Note

The assignment requires this base URL:

```text
https://testnet.binancefuture.com
```

So the app defaults to that URL.

If your Binance Futures Testnet account redirects to a newer demo endpoint and your evaluator permits it, you can change `.env` to:

```env
BINANCE_FUTURES_BASE_URL=https://demo-fapi.binance.com
```

## How to Run

### MARKET order example

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### LIMIT order example

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000
```

### Interactive mode

```bash
python cli.py --interactive
```

The app will ask for symbol, side, order type, quantity, and price if needed.

## Output Example

```text
Order Request Summary
---------------------
symbol: BTCUSDT
side: BUY
type: MARKET
quantity: 0.001
newOrderRespType: RESULT

Order Response Details
----------------------
orderId: 123456789
clientOrderId: abc123
symbol: BTCUSDT
side: BUY
type: MARKET
status: FILLED
executedQty: 0.001
avgPrice: 65000.00

SUCCESS: Order request completed on Binance Futures Testnet.
Log file: logs/trading_bot.log
```

## Logging

Default log file:

```text
logs/trading_bot.log
```

The logger records:

- sanitized API request parameters
- API response status and body
- Binance API errors
- network errors
- validation errors
- unexpected exceptions

Sample log files are included:

```text
logs/market_order_sample.log
logs/limit_order_sample.log
```

These sample logs show the expected format. For final submission, run at least one MARKET order and one LIMIT order with your own testnet API credentials so `logs/trading_bot.log` contains real successful order logs.

## Common Errors

### `Invalid Api-Key ID` or error `-2015`

Possible causes:

- using production Binance keys instead of Futures Testnet keys
- wrong testnet base URL
- API key not activated
- old/deleted key
- key copied with extra spaces

### `price is required for LIMIT orders`

LIMIT orders must include `--price`:

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000
```

### `This task is for USDT-M Futures`

Use symbols ending in `USDT`, for example:

```text
BTCUSDT
ETHUSDT
BNBUSDT
```

## Assumptions

- The app is for Binance Futures Testnet only, not production trading.
- API credentials are provided through `.env`.
- Default position mode is one-way mode, so `positionSide` is not sent.
- `newOrderRespType=RESULT` is used to get useful order response details, especially for MARKET orders.
- LIMIT examples may remain in `NEW` status if the price is far from market price.

## Security Notes

- Never commit `.env` or API secrets.
- Use only testnet keys.
- Keep API permissions limited to what is needed for the test.
- This is a simplified hiring-task bot, not a production trading system.
