"""
均值回歸策略 (Mean Reversion Strategy)
使用 RSI 和 ATR 指標
"""
import pandas as pd
from .base_strategy import BaseStrategy
from utils.indicators import calculate_rsi, calculate_atr


class MeanReversionStrategy(BaseStrategy):
    """均值回歸策略"""

    def __init__(self, rsi_period: int = 14, rsi_oversold: int = 30,
                 rsi_overbought: int = 70, atr_period: int = 14,
                 atr_multiplier: float = 2.0):
        """
        初始化均值回歸策略

        Args:
            rsi_period: RSI 計算週期 (預設 14)
            rsi_oversold: RSI 超賣水平 (預設 30)
            rsi_overbought: RSI 超買水平 (預設 70)
            atr_period: ATR 計算週期 (預設 14)
            atr_multiplier: ATR 倍數用於設定停損 (預設 2.0)
        """
        params = {
            'rsi_period': rsi_period,
            'rsi_oversold': rsi_oversold,
            'rsi_overbought': rsi_overbought,
            'atr_period': atr_period,
            'atr_multiplier': atr_multiplier
        }
        super().__init__(name='MeanReversion', params=params)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        計算 RSI 和 ATR 指標

        Args:
            data: 必須包含 'close', 'high', 'low' 欄位

        Returns:
            DataFrame 加上 'RSI' 和 'ATR' 欄位
        """
        df = data.copy()

        rsi_period = self.params['rsi_period']
        atr_period = self.params['atr_period']

        df['RSI'] = calculate_rsi(df['close'], rsi_period)
        df['ATR'] = calculate_atr(df['high'], df['low'], df['close'], atr_period)

        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易訊號

        當 RSI < 超賣水平時買入 (認為會反彈)
        當 RSI > 超買水平時賣出 (認為會回落)

        Args:
            data: 價格資料

        Returns:
            DataFrame 加上 'signal', 'position', 'stop_loss' 欄位
        """
        df = self.calculate_indicators(data)

        rsi_oversold = self.params['rsi_oversold']
        rsi_overbought = self.params['rsi_overbought']
        atr_multiplier = self.params['atr_multiplier']

        # 初始化欄位
        df['signal'] = 0
        df['position'] = 0

        # 超賣時買入
        df.loc[df['RSI'] < rsi_oversold, 'signal'] = 1

        # 超買時賣出
        df.loc[df['RSI'] > rsi_overbought, 'signal'] = -1

        # 計算停損位 (使用 ATR)
        df['stop_loss'] = df['close'] - (df['ATR'] * atr_multiplier)

        return df
