"""
通用回測引擎
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from strategies.base_strategy import BaseStrategy


class Backtester:
    """回測引擎"""

    def __init__(self, initial_capital: float = 100000, commission: float = 0.001425):
        """
        初始化回測引擎

        Args:
            initial_capital: 初始資金 (預設 10 萬)
            commission: 手續費率 (預設 0.1425%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.results = None

    def run(self, strategy: BaseStrategy, data: pd.DataFrame) -> pd.DataFrame:
        """
        執行回測

        Args:
            strategy: 策略實例
            data: 價格資料 (必須包含 'close' 欄位)

        Returns:
            包含回測結果的 DataFrame
        """
        # 使用策略生成訊號
        df = strategy.generate_signals(data.copy())

        # 計算持倉
        df['holdings'] = 0
        df['cash'] = self.initial_capital
        df['total'] = self.initial_capital

        cash = self.initial_capital
        position = 0

        for i in range(1, len(df)):
            signal = df.iloc[i]['signal']
            price = df.iloc[i]['close']

            # 買入訊號
            if signal > 0 and position == 0:
                # 全部資金買入 (扣除手續費)
                shares_to_buy = int((cash * (1 - self.commission)) / price)
                cost = shares_to_buy * price
                commission_cost = cost * self.commission

                position = shares_to_buy
                cash -= (cost + commission_cost)

            # 賣出訊號
            elif signal < 0 and position > 0:
                # 賣出全部持股 (扣除手續費)
                revenue = position * price
                commission_cost = revenue * self.commission

                cash += (revenue - commission_cost)
                position = 0

            # 更新持倉價值
            df.loc[df.index[i], 'holdings'] = position * price
            df.loc[df.index[i], 'cash'] = cash
            df.loc[df.index[i], 'total'] = cash + (position * price)

        self.results = df
        return df

    def get_portfolio_value(self) -> pd.Series:
        """取得投資組合總價值時間序列"""
        if self.results is None:
            raise ValueError("請先執行回測 (run method)")
        return self.results['total']

    def get_returns(self) -> pd.Series:
        """取得報酬率時間序列"""
        portfolio_value = self.get_portfolio_value()
        returns = portfolio_value.pct_change()
        return returns

    def summary(self) -> Dict[str, Any]:
        """
        產生回測摘要

        Returns:
            包含各種績效指標的字典
        """
        if self.results is None:
            raise ValueError("請先執行回測 (run method)")

        from backtest.evaluation import calculate_metrics

        portfolio_value = self.get_portfolio_value()
        returns = self.get_returns()

        metrics = calculate_metrics(portfolio_value, returns, self.initial_capital)

        return metrics
