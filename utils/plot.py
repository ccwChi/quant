"""
繪圖工具
用於視覺化股價、指標和回測結果
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def plot_price_with_indicators(df: pd.DataFrame, indicators: list = None, title: str = None):
    """
    繪製股價與技術指標

    Args:
        df: 包含股價和指標的 DataFrame
        indicators: 要繪製的指標欄位名稱列表
        title: 圖表標題
    """
    if indicators is None:
        indicators = []

    fig, ax = plt.subplots(figsize=(14, 7))

    # 繪製收盤價
    ax.plot(df.index, df['close'], label='收盤價', linewidth=2, color='black')

    # 繪製指標
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    for i, indicator in enumerate(indicators):
        if indicator in df.columns:
            color = colors[i % len(colors)]
            ax.plot(df.index, df[indicator], label=indicator, linewidth=1.5,
                   linestyle='--', color=color, alpha=0.7)

    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('價格', fontsize=12)
    ax.set_title(title or '股價與技術指標', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_backtest_results(df: pd.DataFrame, title: str = None):
    """
    繪製回測結果

    Args:
        df: 回測結果 DataFrame (包含 total, signal 等欄位)
        title: 圖表標題
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # 上圖: 股價與買賣點
    ax1.plot(df.index, df['close'], label='收盤價', linewidth=2, color='black')

    # 標記買入點
    buy_signals = df[df['signal'] > 0]
    ax1.scatter(buy_signals.index, buy_signals['close'], marker='^',
               color='green', s=100, label='買入', zorder=5)

    # 標記賣出點
    sell_signals = df[df['signal'] < 0]
    ax1.scatter(sell_signals.index, sell_signals['close'], marker='v',
               color='red', s=100, label='賣出', zorder=5)

    ax1.set_ylabel('股價', fontsize=12)
    ax1.set_title(title or '回測結果', fontsize=14, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # 下圖: 投資組合價值
    if 'total' in df.columns:
        ax2.plot(df.index, df['total'], label='投資組合價值',
                linewidth=2, color='blue')
        ax2.fill_between(df.index, df['total'], alpha=0.3)

    ax2.set_xlabel('日期', fontsize=12)
    ax2.set_ylabel('投資組合價值', fontsize=12)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_rsi(df: pd.DataFrame, title: str = None):
    """
    繪製 RSI 指標

    Args:
        df: 包含 RSI 欄位的 DataFrame
        title: 圖表標題
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # 上圖: 股價
    ax1.plot(df.index, df['close'], label='收盤價', linewidth=2, color='black')
    ax1.set_ylabel('股價', fontsize=12)
    ax1.set_title(title or 'RSI 指標分析', fontsize=14, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # 下圖: RSI
    ax2.plot(df.index, df['RSI'], label='RSI', linewidth=2, color='purple')
    ax2.axhline(y=70, color='r', linestyle='--', label='超買 (70)', alpha=0.7)
    ax2.axhline(y=30, color='g', linestyle='--', label='超賣 (30)', alpha=0.7)
    ax2.fill_between(df.index, 30, 70, alpha=0.1, color='gray')

    ax2.set_xlabel('日期', fontsize=12)
    ax2.set_ylabel('RSI', fontsize=12)
    ax2.set_ylim(0, 100)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_returns_distribution(returns: pd.Series, title: str = None):
    """
    繪製報酬率分佈圖

    Args:
        returns: 報酬率序列
        title: 圖表標題
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # 繪製直方圖
    ax.hist(returns.dropna(), bins=50, alpha=0.7, color='skyblue', edgecolor='black')

    # 標記平均值
    mean_return = returns.mean()
    ax.axvline(mean_return, color='red', linestyle='--', linewidth=2,
              label=f'平均報酬率: {mean_return:.4f}')

    ax.set_xlabel('報酬率', fontsize=12)
    ax.set_ylabel('次數', fontsize=12)
    ax.set_title(title or '報酬率分佈', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.show()


def plot_drawdown(portfolio_value: pd.Series, title: str = None):
    """
    繪製回撤圖

    Args:
        portfolio_value: 投資組合價值序列
        title: 圖表標題
    """
    # 計算回撤
    cummax = portfolio_value.cummax()
    drawdown = (portfolio_value - cummax) / cummax * 100

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # 上圖: 投資組合價值
    ax1.plot(portfolio_value.index, portfolio_value, label='投資組合價值',
            linewidth=2, color='blue')
    ax1.plot(cummax.index, cummax, label='歷史最高', linewidth=1,
            linestyle='--', color='green', alpha=0.7)

    ax1.set_ylabel('價值', fontsize=12)
    ax1.set_title(title or '回撤分析', fontsize=14, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # 下圖: 回撤百分比
    ax2.fill_between(drawdown.index, drawdown, 0, alpha=0.5, color='red')
    ax2.plot(drawdown.index, drawdown, linewidth=1, color='darkred')

    max_dd = drawdown.min()
    ax2.axhline(y=max_dd, color='black', linestyle='--', linewidth=1,
               label=f'最大回撤: {max_dd:.2f}%')

    ax2.set_xlabel('日期', fontsize=12)
    ax2.set_ylabel('回撤 (%)', fontsize=12)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
