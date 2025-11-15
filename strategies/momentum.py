"""
動量策略 (Momentum Strategy)
使用 SMA20 / SMA60 進行趨勢追蹤
"""
import pandas as pd
from .base_strategy import BaseStrategy
from utils.indicators import calculate_sma


class MomentumStrategy(BaseStrategy):
    """動量/趨勢追蹤策略"""

    def __init__(self, short_window: int = 20, long_window: int = 60):
        """
        初始化動量策略

        Args:
            short_window: 短期移動平均窗口 (預設 20)
            long_window: 長期移動平均窗口 (預設 60)
        """
        params = {
            'short_window': short_window,
            'long_window': long_window
        }
        super().__init__(name='Momentum', params=params)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        計算 SMA20 和 SMA60

        Args:
            data: 必須包含 'close' 欄位

        Returns:
            DataFrame 加上 'SMA20' 和 'SMA60' 欄位
        """
        df = data.copy()

        short_window = self.params['short_window']
        long_window = self.params['long_window']

        df[f'SMA{short_window}'] = calculate_sma(df['close'], short_window)
        df[f'SMA{long_window}'] = calculate_sma(df['close'], long_window)

        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易訊號

        當 SMA20 上穿 SMA60 時買入 (Golden Cross)
        當 SMA20 下穿 SMA60 時賣出 (Death Cross)

        Args:
            data: 價格資料

        Returns:
            DataFrame 加上 'signal' 和 'position' 欄位
        """
        df = self.calculate_indicators(data)

        short_window = self.params['short_window']
        long_window = self.params['long_window']

        # 初始化訊號欄位
        df['signal'] = 0
        df['position'] = 0

        # 當短期均線 > 長期均線時，為多頭趨勢 (持有)
        df.loc[df[f'SMA{short_window}'] > df[f'SMA{long_window}'], 'position'] = 1

        # 計算交易訊號 (position 的變化)
        df['signal'] = df['position'].diff()

        return df
