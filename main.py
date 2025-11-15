"""
主程式進入點
提供統一的介面執行各種功能
"""
import argparse
import sys
from datetime import datetime

from utils.fetch import fetch_stock_data, save_stock_data, load_stock_data
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from backtest.backtester import Backtester
from ai.optimize_strategy import StrategyOptimizer


def fetch_data(symbols: list, source: str = 'yfinance'):
    """
    抓取股票資料

    Args:
        symbols: 股票代碼列表
        source: 資料來源 ('finmind' 或 'yfinance')
    """
    print(f"\n=== 開始抓取資料 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

    for symbol in symbols:
        try:
            print(f"正在抓取 {symbol}...")
            df = fetch_stock_data(symbol, source=source)

            if df is not None:
                save_stock_data(symbol, df, data_type='raw')
                print(f"✓ {symbol} 完成 | 資料筆數: {len(df)}")
            else:
                print(f"✗ {symbol} 失敗")

        except Exception as e:
            print(f"✗ {symbol} 錯誤: {str(e)}")

        print()


def run_backtest(symbol: str, strategy_name: str = 'momentum'):
    """
    執行回測

    Args:
        symbol: 股票代碼
        strategy_name: 策略名稱 ('momentum' 或 'mean_reversion')
    """
    print(f"\n=== 執行回測: {symbol} - {strategy_name} ===\n")

    # 載入資料
    df = load_stock_data(symbol, data_type='raw')

    if df is None:
        print(f"錯誤: 找不到 {symbol} 的資料，請先執行 fetch 指令")
        return

    # 選擇策略
    if strategy_name == 'momentum':
        strategy = MomentumStrategy(short_window=20, long_window=60)
    elif strategy_name == 'mean_reversion':
        strategy = MeanReversionStrategy(rsi_period=14, rsi_oversold=30, rsi_overbought=70)
    else:
        print(f"錯誤: 不支援的策略 {strategy_name}")
        return

    # 執行回測
    backtester = Backtester(initial_capital=100000, commission=0.001425)
    results = backtester.run(strategy, df)

    # 顯示結果
    metrics = backtester.summary()

    print("\n=== 回測結果 ===")
    print(f"策略: {strategy.name}")
    print(f"參數: {strategy.get_params()}")
    print(f"\n績效指標:")
    print(f"  初始資金: {metrics['initial_capital']:,.0f}")
    print(f"  最終價值: {metrics['final_value']:,.0f}")
    print(f"  總報酬率: {metrics['total_return']:.2f}%")
    print(f"  年化報酬率 (CAGR): {metrics['cagr']:.2f}%")
    print(f"  最大回撤 (MDD): {metrics['max_drawdown']:.2f}%")
    print(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
    print(f"  年化波動率: {metrics['volatility']:.2f}%")


def optimize_strategy(symbol: str, strategy_name: str = 'momentum'):
    """
    優化策略參數

    Args:
        symbol: 股票代碼
        strategy_name: 策略名稱 ('momentum' 或 'mean_reversion')
    """
    print(f"\n=== 優化策略: {symbol} - {strategy_name} ===\n")

    # 載入資料
    df = load_stock_data(symbol, data_type='raw')

    if df is None:
        print(f"錯誤: 找不到 {symbol} 的資料，請先執行 fetch 指令")
        return

    # 建立優化器
    optimizer = StrategyOptimizer(df, initial_capital=100000)

    # 定義參數網格
    if strategy_name == 'momentum':
        strategy_class = MomentumStrategy
        param_grid = {
            'short_window': [10, 20, 30],
            'long_window': [50, 60, 70]
        }
    elif strategy_name == 'mean_reversion':
        strategy_class = MeanReversionStrategy
        param_grid = {
            'rsi_period': [10, 14, 20],
            'rsi_oversold': [25, 30, 35],
            'rsi_overbought': [65, 70, 75],
            'atr_period': [14],
            'atr_multiplier': [2.0]
        }
    else:
        print(f"錯誤: 不支援的策略 {strategy_name}")
        return

    # 執行優化
    results = optimizer.grid_search(strategy_class, param_grid)

    # 顯示最佳結果
    best = results[0]
    print("\n=== 最佳參數組合 ===")
    print(f"參數: {best['parameters']}")
    print(f"\n績效指標:")
    for key, value in best['metrics'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    # 儲存結果
    output_file = f"optimization_{symbol}_{strategy_name}_{datetime.now().strftime('%Y%m%d')}.json"
    optimizer.export_results(output_file)

    # 生成 GPT prompt
    print("\n=== GPT 優化建議 ===")
    print(optimizer.generate_gpt_prompt())


def run_daily_routine(symbols: list = None):
    """
    執行每日例行作業

    Args:
        symbols: 股票代碼列表
    """
    if symbols is None:
        symbols = ['2330', '0050', '0056', '2317', '2454']

    print(f"\n=== 每日例行作業 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

    # 1. 抓取今日資料
    print("步驟 1: 抓取最新資料")
    from daily.fetch_today import fetch_today_data
    fetch_today_data(symbols)

    # 2. 生成交易訊號
    print("\n步驟 2: 生成交易訊號")
    from daily.generate_signal import generate_signals
    signals_file = f"signals_{datetime.now().strftime('%Y%m%d')}.json"
    generate_signals(symbols, output_file=signals_file)

    # 3. 產生報告
    print("\n步驟 3: 產生摘要報告")
    from daily.summary_report import generate_text_report, generate_html_report
    generate_text_report(signals_file)
    generate_html_report(signals_file)

    print("\n=== 每日例行作業完成 ===")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='Python 量化交易系統',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 抓取資料
  python main.py fetch --symbols 2330 0050

  # 執行回測
  python main.py backtest --symbol 2330 --strategy momentum

  # 優化策略參數
  python main.py optimize --symbol 2330 --strategy momentum

  # 執行每日例行作業
  python main.py daily --symbols 2330 0050 0056
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用指令')

    # fetch 指令
    fetch_parser = subparsers.add_parser('fetch', help='抓取股票資料')
    fetch_parser.add_argument('--symbols', nargs='+', required=True, help='股票代碼列表')
    fetch_parser.add_argument('--source', default='yfinance', choices=['finmind', 'yfinance'],
                             help='資料來源 (預設: yfinance)')

    # backtest 指令
    backtest_parser = subparsers.add_parser('backtest', help='執行回測')
    backtest_parser.add_argument('--symbol', required=True, help='股票代碼')
    backtest_parser.add_argument('--strategy', default='momentum',
                                choices=['momentum', 'mean_reversion'],
                                help='策略名稱 (預設: momentum)')

    # optimize 指令
    optimize_parser = subparsers.add_parser('optimize', help='優化策略參數')
    optimize_parser.add_argument('--symbol', required=True, help='股票代碼')
    optimize_parser.add_argument('--strategy', default='momentum',
                                choices=['momentum', 'mean_reversion'],
                                help='策略名稱 (預設: momentum)')

    # daily 指令
    daily_parser = subparsers.add_parser('daily', help='執行每日例行作業')
    daily_parser.add_argument('--symbols', nargs='+', help='股票代碼列表')

    args = parser.parse_args()

    # 執行對應指令
    if args.command == 'fetch':
        fetch_data(args.symbols, args.source)

    elif args.command == 'backtest':
        run_backtest(args.symbol, args.strategy)

    elif args.command == 'optimize':
        optimize_strategy(args.symbol, args.strategy)

    elif args.command == 'daily':
        run_daily_routine(args.symbols)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
