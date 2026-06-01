"""Command line interface for the Binance Futures Testnet trading bot."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv

from bot.client import (
    DEFAULT_BASE_URL,
    BinanceAPIError,
    BinanceFuturesClient,
    BinanceNetworkError,
    MissingCredentialsError,
)
from bot.logging_config import setup_logging
from bot.orders import build_order_request, order_to_params, place_order
from bot.validators import ValidationError, VALID_ORDER_TYPES, VALID_SIDES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Place MARKET and LIMIT orders on Binance Futures Testnet (USDT-M).",
    )
    parser.add_argument("--symbol", help="Trading symbol, for example BTCUSDT")
    parser.add_argument("--side", choices=sorted(VALID_SIDES), help="Order side: BUY or SELL")
    parser.add_argument("--type", choices=sorted(VALID_ORDER_TYPES), help="Order type: MARKET or LIMIT")
    parser.add_argument("--quantity", help="Order quantity, for example 0.001")
    parser.add_argument("--price", help="Limit price. Required only for LIMIT orders")
    parser.add_argument("--time-in-force", default="GTC", help="Time in force for LIMIT orders: GTC, IOC, or FOK")
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override Binance Futures Testnet base URL. Defaults to env or assignment URL.",
    )
    parser.add_argument("--log-file", default="logs/trading_bot.log", help="Path to log file")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for missing values interactively instead of passing all CLI arguments.",
    )
    return parser.parse_args()


def prompt_missing(args: argparse.Namespace) -> argparse.Namespace:
    """Ask for missing CLI values in a friendly prompt flow."""
    if not args.symbol:
        args.symbol = input("Symbol (example BTCUSDT): ").strip()
    if not args.side:
        args.side = input("Side (BUY/SELL): ").strip().upper()
    if not args.type:
        args.type = input("Order type (MARKET/LIMIT): ").strip().upper()
    if not args.quantity:
        args.quantity = input("Quantity (example 0.001): ").strip()
    if str(args.type).upper() == "LIMIT" and not args.price:
        args.price = input("Limit price: ").strip()
    return args


def print_order_summary(params: dict[str, Any]) -> None:
    print("\nOrder Request Summary")
    print("---------------------")
    for key in ["symbol", "side", "type", "quantity", "price", "timeInForce", "newOrderRespType"]:
        if key in params and params[key] not in (None, ""):
            print(f"{key}: {params[key]}")


def print_order_response(response: dict[str, Any]) -> None:
    print("\nOrder Response Details")
    print("----------------------")
    fields = [
        "orderId",
        "clientOrderId",
        "symbol",
        "side",
        "type",
        "status",
        "executedQty",
        "avgPrice",
        "cumQuote",
        "price",
        "origQty",
        "updateTime",
    ]
    for field in fields:
        if field in response:
            print(f"{field}: {response[field]}")


def main() -> int:
    load_dotenv()
    args = parse_args()

    if args.interactive:
        args = prompt_missing(args)

    logger = setup_logging(args.log_file)

    try:
        order = build_order_request(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            time_in_force=args.time_in_force,
        )
        params = order_to_params(order)
        print_order_summary(params)

        base_url = args.base_url or os.getenv("BINANCE_FUTURES_BASE_URL", DEFAULT_BASE_URL)
        client = BinanceFuturesClient(
            api_key=os.getenv("BINANCE_API_KEY", ""),
            api_secret=os.getenv("BINANCE_API_SECRET", ""),
            base_url=base_url,
            logger=logger,
        )

        try:
            response = place_order(client, order)
        finally:
            client.close()

        print_order_response(response)
        print("\nSUCCESS: Order request completed on Binance Futures Testnet.")
        print(f"Log file: {args.log_file}")
        return 0

    except ValidationError as exc:
        logger.error("VALIDATION_ERROR %s", exc)
        print(f"\nFAILED: Invalid input - {exc}", file=sys.stderr)
        return 1
    except MissingCredentialsError as exc:
        logger.error("MISSING_CREDENTIALS %s", exc)
        print(f"\nFAILED: {exc}", file=sys.stderr)
        return 1
    except BinanceAPIError as exc:
        logger.error("BINANCE_API_EXCEPTION %s", exc)
        print(f"\nFAILED: {exc}", file=sys.stderr)
        return 1
    except BinanceNetworkError as exc:
        logger.error("NETWORK_EXCEPTION %s", exc)
        print(f"\nFAILED: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        logger.warning("USER_CANCELLED")
        print("\nCancelled by user.", file=sys.stderr)
        return 130
    except Exception as exc:  # defensive catch for unexpected errors
        logger.exception("UNEXPECTED_ERROR %s", exc)
        print(f"\nFAILED: Unexpected error - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
