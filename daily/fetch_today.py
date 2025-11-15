"""
每日資料抓取腳本
自動抓取最新的股價資料
"""
import sys
import os
from datetime import datetime

# 加入專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.fetch import fetch_stock_data, update_stock_data


def fetch_today_data(symbols: list = None):
    """
    抓取今日資料

    Args:
        symbols: 股票代碼列表 (預設抓取常用股票)
    """
    if symbols is None:
        # 預設抓取的股票
        symbols = ['2330', '0050', '0056', '2317', '2454']

    print(f"=== 開始抓取今日資料 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n")

    for symbol in symbols:
        try:
            print(f"正在抓取 {symbol}...")

            # 更新資料 (會自動處理增量更新)
            df = update_stock_data(symbol)

            if df is not None and len(df) > 0:
                latest_date = df.index[-1].strftime('%Y-%m-%d')
                latest_close = df['close'].iloc[-1]
                print(f"✓ {symbol} 完成 | 最新日期: {latest_date} | 收盤價: {latest_close:.2f}")
            else:
                print(f"✗ {symbol} 無新資料")

        except Exception as e:
            print(f"✗ {symbol} 錯誤: {str(e)}")

        print()

    print("=== 資料抓取完成 ===")


def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(description='抓取今日股價資料')
    parser.add_argument('--symbols', nargs='+', help='股票代碼列表')

    args = parser.parse_args()

    fetch_today_data(symbols=args.symbols)


if __name__ == '__main__':
    main()
