"""
回測評估指標
計算 MDD (最大回撤), 勝率, CAGR 等指標
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


def calculate_max_drawdown(portfolio_value: pd.Series) -> float:
    """
    計算最大回撤 (Maximum Drawdown)

    Args:
        portfolio_value: 投資組合價值時間序列

    Returns:
        最大回撤百分比 (負數)
    """
    cummax = portfolio_value.cummax()
    drawdown = (portfolio_value - cummax) / cummax
    max_drawdown = drawdown.min()

    return max_drawdown


def calculate_cagr(portfolio_value: pd.Series, years: float = None) -> float:
    """
    計算年化報酬率 (CAGR - Compound Annual Growth Rate)

    Args:
        portfolio_value: 投資組合價值時間序列
        years: 投資年數 (如果為 None，會自動計算)

    Returns:
        年化報酬率百分比
    """
    if years is None:
        # 假設每個數據點是一天
        years = len(portfolio_value) / 252  # 252 個交易日

    initial_value = portfolio_value.iloc[0]
    final_value = portfolio_value.iloc[-1]

    if initial_value <= 0 or years <= 0:
        return 0.0

    cagr = (pow(final_value / initial_value, 1 / years) - 1) * 100

    return cagr


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    計算夏普比率 (Sharpe Ratio)

    Args:
        returns: 報酬率時間序列
        risk_free_rate: 無風險利率 (年化，預設 2%)

    Returns:
        夏普比率
    """
    # 計算超額報酬
    excess_returns = returns - (risk_free_rate / 252)

    if excess_returns.std() == 0:
        return 0.0

    sharpe = np.sqrt(252) * (excess_returns.mean() / excess_returns.std())

    return sharpe


def calculate_win_rate(signals: pd.Series, returns: pd.Series) -> Dict[str, Any]:
    """
    計算勝率和交易統計

    Args:
        signals: 交易訊號序列
        returns: 報酬率時間序列

    Returns:
        包含勝率、交易次數等資訊的字典
    """
    # 找出所有交易點
    trades = signals[signals != 0]

    if len(trades) == 0:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0
        }

    # 計算每筆交易的報酬
    trade_returns = []
    position = 0

    for i in range(len(signals)):
        if signals.iloc[i] > 0:  # 買入
            position = i
        elif signals.iloc[i] < 0 and position > 0:  # 賣出
            # 計算這段持有期間的報酬
            trade_return = returns.iloc[position:i+1].sum()
            trade_returns.append(trade_return)
            position = 0

    if len(trade_returns) == 0:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0
        }

    winning_trades = sum(1 for r in trade_returns if r > 0)
    losing_trades = sum(1 for r in trade_returns if r <= 0)
    win_rate = (winning_trades / len(trade_returns)) * 100

    return {
        'total_trades': len(trade_returns),
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate
    }


def calculate_metrics(portfolio_value: pd.Series, returns: pd.Series,
                      initial_capital: float) -> Dict[str, Any]:
    """
    計算所有評估指標

    Args:
        portfolio_value: 投資組合價值時間序列
        returns: 報酬率時間序列
        initial_capital: 初始資金

    Returns:
        包含所有指標的字典
    """
    final_value = portfolio_value.iloc[-1]
    total_return = ((final_value - initial_capital) / initial_capital) * 100

    metrics = {
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return': total_return,
        'max_drawdown': calculate_max_drawdown(portfolio_value) * 100,
        'cagr': calculate_cagr(portfolio_value),
        'sharpe_ratio': calculate_sharpe_ratio(returns),
        'volatility': returns.std() * np.sqrt(252) * 100,  # 年化波動率
    }

    return metrics
