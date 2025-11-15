"""
回測模組
包含回測引擎和評估指標
"""
from .backtester import Backtester
from .evaluation import (
    calculate_max_drawdown,
    calculate_cagr,
    calculate_sharpe_ratio,
    calculate_win_rate,
    calculate_metrics
)

__all__ = [
    'Backtester',
    'calculate_max_drawdown',
    'calculate_cagr',
    'calculate_sharpe_ratio',
    'calculate_win_rate',
    'calculate_metrics'
]
