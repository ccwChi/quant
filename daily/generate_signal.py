"""
每日訊號生成腳本
根據最新資料產生買賣訊號
"""
import sys
import os
from datetime import datetime
import json

# 加入專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.fetch import load_stock_data
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy


def generate_signals(symbols: list = None, output_file: str = None):
    """
    為多支股票生成交易訊號

    Args:
        symbols: 股票代碼列表
        output_file: 輸出 JSON 檔案路徑
    """
    if symbols is None:
        symbols = ['2330', '0050', '0056', '2317', '2454']

    if output_file is None:
        today = datetime.now().strftime('%Y%m%d')
        output_file = f'signals_{today}.json'

    print(f"=== 開始生成交易訊號 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

    # 初始化策略
    momentum = MomentumStrategy(short_window=20, long_window=60)
    mean_reversion = MeanReversionStrategy(rsi_period=14, rsi_oversold=30, rsi_overbought=70)

    all_signals = {}

    for symbol in symbols:
        try:
            print(f"分析 {symbol}...")

            # 載入資料
            df = load_stock_data(symbol)

            if df is None or len(df) < 100:
                print(f"✗ {symbol} 資料不足")
                continue

            # 使用兩種策略分析
            df_momentum = momentum.generate_signals(df)
            df_mean_rev = mean_reversion.generate_signals(df)

            # 取得最新訊號
            latest_idx = -1

            momentum_signal = df_momentum['signal'].iloc[latest_idx]
            momentum_position = df_momentum['position'].iloc[latest_idx]

            mean_rev_signal = df_mean_rev['signal'].iloc[latest_idx]
            mean_rev_rsi = df_mean_rev['RSI'].iloc[latest_idx]

            # 組合訊號
            combined_signal = "持有"
            if momentum_signal > 0 or mean_rev_signal > 0:
                combined_signal = "買入"
            elif momentum_signal < 0 or mean_rev_signal < 0:
                combined_signal = "賣出"

            # 儲存訊號
            all_signals[symbol] = {
                'date': df.index[latest_idx].strftime('%Y-%m-%d'),
                'close': float(df['close'].iloc[latest_idx]),
                'momentum': {
                    'signal': int(momentum_signal),
                    'position': int(momentum_position),
                    'SMA20': float(df_momentum['SMA20'].iloc[latest_idx]),
                    'SMA60': float(df_momentum['SMA60'].iloc[latest_idx])
                },
                'mean_reversion': {
                    'signal': int(mean_rev_signal),
                    'RSI': float(mean_rev_rsi)
                },
                'recommendation': combined_signal
            }

            print(f"✓ {symbol} | 建議: {combined_signal} | 收盤: {all_signals[symbol]['close']:.2f}")

        except Exception as e:
            print(f"✗ {symbol} 錯誤: {str(e)}")

        print()

    # 儲存到 JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_signals, f, indent=2, ensure_ascii=False)

    print(f"=== 訊號已儲存至: {output_file} ===")

    return all_signals


def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(description='生成每日交易訊號')
    parser.add_argument('--symbols', nargs='+', help='股票代碼列表')
    parser.add_argument('--output', type=str, help='輸出 JSON 檔案路徑')

    args = parser.parse_args()

    generate_signals(symbols=args.symbols, output_file=args.output)


if __name__ == '__main__':
    main()
