"""
技術指標計算工具
包含 SMA, RSI, ATR 等常用指標
"""
import pandas as pd
import numpy as np


def calculate_sma(prices: pd.Series, window: int) -> pd.Series:
    """
    計算簡單移動平均 (Simple Moving Average)

    Args:
        prices: 價格序列
        window: 移動平均窗口

    Returns:
        SMA 序列
    """
    return prices.rolling(window=window).mean()


def calculate_ema(prices: pd.Series, window: int) -> pd.Series:
    """
    計算指數移動平均 (Exponential Moving Average)

    Args:
        prices: 價格序列
        window: 移動平均窗口

    Returns:
        EMA 序列
    """
    return prices.ewm(span=window, adjust=False).mean()


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    計算相對強弱指標 (Relative Strength Index)

    Args:
        prices: 價格序列
        period: RSI 週期 (預設 14)

    Returns:
        RSI 序列 (0-100)
    """
    # 計算價格變化
    delta = prices.diff()

    # 分離上漲和下跌
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # 計算平均漲跌幅
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # 計算 RS 和 RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    計算平均真實區間 (Average True Range)

    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        period: ATR 週期 (預設 14)

    Returns:
        ATR 序列
    """
    # 計算 True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # 計算 ATR (使用 EMA)
    atr = tr.ewm(span=period, adjust=False).mean()

    return atr


def calculate_bollinger_bands(prices: pd.Series, window: int = 20, num_std: float = 2.0):
    """
    計算布林通道 (Bollinger Bands)

    Args:
        prices: 價格序列
        window: 移動平均窗口 (預設 20)
        num_std: 標準差倍數 (預設 2.0)

    Returns:
        (upper_band, middle_band, lower_band) 三條線
    """
    middle_band = calculate_sma(prices, window)
    std = prices.rolling(window=window).std()

    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)

    return upper_band, middle_band, lower_band


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """
    計算 MACD (Moving Average Convergence Divergence)

    Args:
        prices: 價格序列
        fast: 快線週期 (預設 12)
        slow: 慢線週期 (預設 26)
        signal: 訊號線週期 (預設 9)

    Returns:
        (macd_line, signal_line, histogram)
    """
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)

    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                         k_period: int = 14, d_period: int = 3):
    """
    計算隨機指標 (Stochastic Oscillator)

    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        k_period: K 線週期 (預設 14)
        d_period: D 線週期 (預設 3)

    Returns:
        (k_line, d_line)
    """
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()

    k_line = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d_line = k_line.rolling(window=d_period).mean()

    return k_line, d_line


def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    計算能量潮指標 (On-Balance Volume)

    Args:
        close: 收盤價序列
        volume: 成交量序列

    Returns:
        OBV 序列
    """
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    return obv
