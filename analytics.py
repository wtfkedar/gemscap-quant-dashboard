import pandas as pd
import statsmodels.api as sm

def prepare_df(rows):
    df = pd.DataFrame(rows, columns=["timestamp", "symbol", "price", "qty"])

    # ✅ FIX: handle mixed ISO timestamp formats safely
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="mixed",
        errors="coerce"
    )

    # Drop rows where timestamp parsing failed (very rare)
    df = df.dropna(subset=["timestamp"])

    return df

def hedge_ratio(y, x):
    y = y.reset_index(drop=True)
    x = x.reset_index(drop=True)

    x = sm.add_constant(x.values)
    model = sm.OLS(y.values, x).fit()
    return model.params[1]

def spread_and_hedge(df1, df2):
    h = hedge_ratio(df1["price"], df2["price"])
    spread = (
        df1["price"].reset_index(drop=True)
        - h * df2["price"].reset_index(drop=True)
    )
    return spread, h

def zscore(series, window):
    return (series - series.rolling(window).mean()) / series.rolling(window).std()

def resample_ohlc(df, timeframe):
    """
    timeframe: '1s', '1m', '5m'
    """
    rule_map = {
        "1s": "1s",
        "1m": "1min",
        "5m": "5min"
    }

    rule = rule_map[timeframe]

    df = df.set_index("timestamp")

    ohlc = (
        df["price"]
        .resample(rule)
        .ohlc()
    )

    volume = (
        df["qty"]
        .resample(rule)
        .sum()
        .rename("volume")
    )

    result = pd.concat([ohlc, volume], axis=1).dropna().reset_index()
    return result

def rolling_correlation(series1, series2, window):
    """
    Computes rolling correlation between two price series
    """
    return series1.rolling(window).corr(series2)
from statsmodels.tsa.stattools import adfuller

def adf_test(series):
    """
    Runs Augmented Dickey-Fuller test on a series
    Returns p-value
    """
    series = series.dropna()
    if len(series) < 20:
        return None

    result = adfuller(series)
    return result[1]  # p-value
