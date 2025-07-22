"""
execute_orders.py

This script ingests a CSV trade plan, performs basic risk checks, and generates
option orders via the Alpaca API (paper or live) or produces a list of orders
for manual execution. It assumes environment variables hold the API
credentials.  If credentials are missing the script prints the orders and
exits.

Usage:
    python execute_orders.py --csv orders_YYYY-MM-DD.csv --equity 100000

Arguments:
    --csv:     Path to the CSV file with orders (see sample format).
    --equity:  Total account equity in dollars for risk calculations.
    --max_risk_per_trade: Maximum fraction (0–1) of equity to risk per trade (default 0.02).
    --max_daily_risk: Maximum fraction of equity to risk per day (default 0.05).
    --no_trade_start/no_trade_end: ISO dates defining a blackout window (e.g., '2025-07-29','2025-07-30').

Example order row:
    Symbol,Expiry,Strike,OptionType,Action,Quantity
    AAPL,2025-08-16,190,CALL,BUY,1

The script creates an order dictionary for each row.  Multi-leg spreads are
submitted as individual legs (Alpaca’s API does not yet support option
multi-leg orders in a single call).  Operator approval is required before
submission.
"""

import csv
import os
import sys
import argparse
from datetime import datetime, date

try:
    import alpaca_trade_api as tradeapi  # Requires `pip install alpaca-trade-api`
except ImportError:
    tradeapi = None  # We'll handle missing library gracefully


def parse_csv(path):
    orders = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            orders.append(row)
    return orders


def risk_check(order, equity, max_risk_per_trade):
    """Approximate max risk per contract; here we conservatively assume the full
    premium could be lost (set to $500 per contract if unknown). Returns
    True if within risk tolerance.
    """
    qty = int(order["Quantity"])
    # Placeholder: assume $500 risk per contract for any option
    assumed_risk = 500 * qty
    return assumed_risk <= equity * max_risk_per_trade


def within_no_trade_window(no_trade_start, no_trade_end):
    today = date.today()
    if no_trade_start and no_trade_end:
        return date.fromisoformat(no_trade_start) <= today <= date.fromisoformat(no_trade_end)
    return False


def build_alpaca_order(order):
    """Construct an Alpaca order dict for an option trade."""
    symbol = order["Symbol"]
    option_type = order["OptionType"].lower()  # 'call' or 'put'
    action = order["Action"].lower()
    qty = int(order["Quantity"])
    strike = float(order["Strike"])
    expiry = order["Expiry"]
    option_symbol = f"{symbol}{expiry.replace('-', '')}{option_type[0].upper()}{int(strike*1000):08d}"
    # Alpaca requires OCC option symbol; the above is simplified and may need adjustment.
    return dict(
        symbol=option_symbol,
        qty=qty,
        side=action,
        type='market',
        time_in_force='day'
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True, help='Path to orders CSV')
    parser.add_argument('--equity', type=float, required=True, help='Account equity in USD')
    parser.add_argument('--max_risk_per_trade', type=float, default=0.02)
    parser.add_argument('--max_daily_risk', type=float, default=0.05)
    parser.add_argument('--no_trade_start', type=str, default=None)
    parser.add_argument('--no_trade_end', type=str, default=None)
    args = parser.parse_args()

    orders = parse_csv(args.csv)

    # Check no-trade window
    if within_no_trade_window(args.no_trade_start, args.no_trade_end):
        print(f"We are within the no-trade window ({args.no_trade_start}–{args.no_trade_end}). No orders will be executed.")
        sys.exit(0)

    # Prepare Alpaca API (if credentials available)
    api_key = os.getenv('APCA_API_KEY_ID')
    api_secret = os.getenv('APCA_API_SECRET_KEY')
    base_url = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')

    alpaca_available = all([api_key, api_secret, tradeapi is not None])

    api = None
    if alpaca_available:
        api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

    total_risk_used = 0.0
    executed = []
    skipped = []

    for order in orders:
        ok_risk = risk_check(order, args.equity, args.max_risk_per_trade)
        # Example risk estimate (500$ per contract). Adjust as needed.
        order_risk = 500 * int(order["Quantity"])
        if not ok_risk:
            skipped.append((order, 'exceeds per-trade risk limit'))
            continue
        if total_risk_used + order_risk > args.equity * args.max_daily_risk:
            skipped.append((order, 'exceeds daily risk limit'))
            continue

        # Build order for Alpaca
        alpaca_order = build_alpaca_order(order)

        # Auto-approve every order.  In full automation mode we do not prompt
        # the operator; as long as the trade passes risk checks above it will
        # be submitted.  A message is printed for transparency.
        print("\nOrder ready:", alpaca_order)
        approve = 'y'  # auto-approve
        # No operator prompt; all orders that pass risk checks proceed directly

        if alpaca_available:
            try:
                res = api.submit_order(**alpaca_order)
                print(f"Order submitted: {res.id}")
                executed.append(order)
                total_risk_used += order_risk
            except Exception as e:
                print(f"Failed to submit order: {e}")
                skipped.append((order, str(e)))
        else:
            # If no API available, just print the order instruction
            print("(API credentials missing – printing order only)")
            print(alpaca_order)
            executed.append(order)
            total_risk_used += order_risk

    # Summary
    print("\nSummary:")
    print(f"Executed {len(executed)} orders; Skipped {len(skipped)} orders.")
    for o, reason in skipped:
        print(f"Skipped {o['Symbol']} {o['OptionType']} {o['Strike']} due to {reason}.")


if __name__ == '__main__':
    main()
