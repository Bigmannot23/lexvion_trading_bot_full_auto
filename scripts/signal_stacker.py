"""
Signal stacking module for the trading bot.

This module combines raw data into actionable signals.  The stub computes
simple momentum and placeholder flow strength metrics.  Users can extend this
module to include dark pool data, macro surprises, sentiment, etc.
"""
import pandas as pd


def compute_momentum(price_df: pd.DataFrame, short_window: int = 5, long_window: int = 20) -> float:
    """
    Compute a simple momentum signal as the ratio of short-term to long-term moving averages.
    Returns a scalar value >1 for bullish momentum and <1 for bearish.
    """
    if len(price_df) < long_window:
        return 1.0
    short_ma = price_df['close'].tail(short_window).mean()
    long_ma = price_df['close'].tail(long_window).mean()
    return short_ma / long_ma


def compute_flow_strength(flow_df: pd.DataFrame) -> float:
    """
    Compute a flow strength metric based on net notional of bullish vs bearish option orders.
    If the DataFrame is empty, returns 0.
    """
    if flow_df.empty:
        return 0.0
    bullish = flow_df[flow_df['direction'] == 'BUY']['notional'].sum()
    bearish = flow_df[flow_df['direction'] == 'SELL']['notional'].sum()
    total = bullish + bearish
    return (bullish - bearish) / total if total != 0 else 0.0


def stack_signals(price_df: pd.DataFrame, flow_df: pd.DataFrame) -> dict:
    """
    Combine momentum and flow strength into a readiness score.  Additional signals can
    be added to this dictionary as needed.
    """
    momentum = compute_momentum(price_df)
    flow_strength = compute_flow_strength(flow_df)
    readiness = momentum + flow_strength  # simplistic example
    return {
        'momentum': momentum,
        'flow_strength': flow_strength,
        'readiness': readiness
    }
