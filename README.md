# Trading Bot Project

This repository contains a modular, end‑to‑end options trading system designed
for **Operator Mode**.  The project ingests market data, computes signals,
scores trade setups, generates order files, and creates an execution script
that places trades through your broker (Alpaca or IBKR) with operator
approval.  All actions are logged for audit and future review.

## Folder Structure

```
trading_bot_project/
├── scripts/
│   ├── data_ingestion.py      # Fetches price, flow, macro, news and calendar data
│   ├── signal_stacker.py      # Computes momentum and flow strength signals
│   ├── execute_orders.py      # Reads orders CSV, prompts for approval, sends trades
├── data/
│   └── orders_2025-07-19.csv  # Example order file generated from trade ideas
├── logs/
│   └── session_2025-07-19.md  # Session log for audit and review
├── config/
│   ├── risk_config.yaml       # Risk parameters (ATR window, position limits, no‑trade windows)
│   └── .env.example           # Sample environment variables for API keys and broker creds
└── README.md                  # You are here
```

## Prerequisites

* Python 3.9+
* Install dependencies:
  ```bash
  pip install pandas yfinance alpaca-trade-api
  ```
* Copy `config/.env.example` to `.env` in the project root and fill in your API keys:
  * `POLYGON_API_KEY`, `FRED_API_KEY`, `NEWSAPI_KEY`, `OPTIONDATA_TOKEN` for data
  * `APCA_API_KEY_ID`, `APCA_API_SECRET_KEY`, `APCA_API_BASE_URL` for Alpaca (or configure IBKR credentials as needed)

## Workflow

1. **Ingest Data** (optional)

   Use the functions in `scripts/data_ingestion.py` to fetch price data, options flow,
   macro series and news.  These functions return pandas DataFrames and can be
   extended to call real APIs.

2. **Stack Signals** (optional)

   Import `stack_signals` from `scripts/signal_stacker.py` and pass the price and
   flow DataFrames to compute momentum and flow strength.  You can expand this
   to include volatility regime detection and other signals.

3. **Prepare Orders CSV**

   The example `data/orders_2025-07-19.csv` contains eight option legs for four
   trade ideas.  When generating your own orders, follow the same column
   structure: `Symbol,Expiry,Strike,OptionType,Action,Quantity`.

4. **Execute Trades**

   Run the execution script with your account equity and risk parameters.  If
   broker credentials are present in the environment, orders will be sent
   automatically after your approval; otherwise the script prints them for
   manual entry.

   ```bash
   # Example: Execute orders with a $100k account, skipping no‑trade windows
   python scripts/execute_orders.py \
       --csv data/orders_2025-07-19.csv \
       --equity 100000 \
       --max_risk_per_trade 0.02 \
       --max_daily_risk 0.05 \
       --no_trade_start 2025-07-29 \
       --no_trade_end 2025-07-30
   ```

   The script will display each order and ask for a `y/n` approval.  Risk
   constraints from `config/risk_config.yaml` can be incorporated into your
   strategy.

5. **Audit & Review**

   After each session, append your execution results (fills, timestamps,
   rationale) to a log file in the `logs/` directory.  Use the provided
   `session_2025-07-19.md` as a template for future logs.

## Notes

* The current code stubs do not make real network calls.  You must implement
  data ingestion functions using your API keys.
* Options symbol formatting for Alpaca uses a simplified OCC template; verify
  the format before live trading.
* Always test with a paper trading account before deploying to live capital.

Happy trading!
