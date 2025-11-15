"""
資料抓取工具
支援 FinMind 和 yfinance API
"""
import pandas as pd
import os
from datetime import datetime, timedelta


def fetch_stock_data(symbol: str, start_date: str = None, end_date: str = None,
                     source: str = 'finmind') -> pd.DataFrame:
    """
    抓取股票資料

    Args:
        symbol: 股票代碼
        start_date: 開始日期 (格式: 'YYYY-MM-DD')
        end_date: 結束日期 (格式: 'YYYY-MM-DD')
        source: 資料來源 ('finmind' 或 'yfinance')

    Returns:
        包含股價資料的 DataFrame
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    if start_date is None:
        # 預設抓取 5 年資料
        start_date = (datetime.now() - timedelta(days=365 * 5)).strftime('%Y-%m-%d')

    if source == 'finmind':
        return fetch_from_finmind(symbol, start_date, end_date)
    elif source == 'yfinance':
        return fetch_from_yfinance(symbol, start_date, end_date)
    else:
        raise ValueError(f"不支援的資料來源: {source}")


def fetch_from_finmind(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    從 FinMind API 抓取資料

    Args:
        symbol: 股票代碼
        start_date: 開始日期
        end_date: 結束日期

    Returns:
        DataFrame 包含 open, high, low, close, volume 欄位
    """
    try:
        from FinMind.data import DataLoader

        dl = DataLoader()

        # 抓取台股資料
        df = dl.taiwan_stock_daily(
            stock_id=symbol,
            start_date=start_date,
            end_date=end_date
        )

        if df is None or len(df) == 0:
            print(f"警告: {symbol} 無資料")
            return None

        # 重新命名欄位
        df = df.rename(columns={
            'date': 'date',
            'open': 'open',
            'max': 'high',
            'min': 'low',
            'close': 'close',
            'Trading_Volume': 'volume'
        })

        # 設定日期為索引
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')

        # 選取需要的欄位
        df = df[['open', 'high', 'low', 'close', 'volume']]

        return df

    except ImportError:
        print("請先安裝 FinMind: pip install FinMind")
        return None
    except Exception as e:
        print(f"抓取 {symbol} 資料失敗: {str(e)}")
        return None


def fetch_from_yfinance(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    從 yfinance API 抓取資料

    Args:
        symbol: 股票代碼 (需要加上 .TW 後綴，例如 '2330.TW')
        start_date: 開始日期
        end_date: 結束日期

    Returns:
        DataFrame 包含 open, high, low, close, volume 欄位
    """
    try:
        import yfinance as yf

        # 台股需要加上 .TW 後綴
        if not symbol.endswith('.TW') and not symbol.endswith('.TWO'):
            ticker = f"{symbol}.TW"
        else:
            ticker = symbol

        # 下載資料
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if df is None or len(df) == 0:
            print(f"警告: {symbol} 無資料")
            return None

        # 欄位名稱轉小寫
        df.columns = [col.lower() for col in df.columns]

        # 選取需要的欄位
        df = df[['open', 'high', 'low', 'close', 'volume']]

        return df

    except ImportError:
        print("請先安裝 yfinance: pip install yfinance")
        return None
    except Exception as e:
        print(f"抓取 {symbol} 資料失敗: {str(e)}")
        return None


def save_stock_data(symbol: str, df: pd.DataFrame, data_type: str = 'raw'):
    """
    儲存股票資料到 CSV

    Args:
        symbol: 股票代碼
        df: 資料 DataFrame
        data_type: 資料類型 ('raw' 或 'processed')
    """
    # 確保目錄存在
    data_dir = f'data/{data_type}'
    os.makedirs(data_dir, exist_ok=True)

    # 儲存檔案
    filename = f'{data_dir}/{symbol}_{data_type}.csv'
    df.to_csv(filename)

    print(f"資料已儲存至: {filename}")


def load_stock_data(symbol: str, data_type: str = 'raw') -> pd.DataFrame:
    """
    從 CSV 載入股票資料

    Args:
        symbol: 股票代碼
        data_type: 資料類型 ('raw' 或 'processed')

    Returns:
        DataFrame
    """
    filename = f'data/{data_type}/{symbol}_{data_type}.csv'

    if not os.path.exists(filename):
        print(f"檔案不存在: {filename}")
        return None

    df = pd.read_csv(filename, index_col=0, parse_dates=True)
    return df


def update_stock_data(symbol: str, source: str = 'finmind') -> pd.DataFrame:
    """
    更新股票資料 (增量更新)

    Args:
        symbol: 股票代碼
        source: 資料來源

    Returns:
        更新後的完整 DataFrame
    """
    # 嘗試載入現有資料
    existing_df = load_stock_data(symbol, data_type='raw')

    if existing_df is not None:
        # 從最後一天的隔天開始抓取
        last_date = existing_df.index[-1]
        start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"更新 {symbol} 從 {start_date} 開始...")
    else:
        # 沒有現有資料，抓取全部
        start_date = (datetime.now() - timedelta(days=365 * 5)).strftime('%Y-%m-%d')
        print(f"首次抓取 {symbol}...")

    # 抓取新資料
    new_df = fetch_stock_data(symbol, start_date=start_date, source=source)

    if new_df is None or len(new_df) == 0:
        print(f"{symbol} 沒有新資料")
        return existing_df

    # 合併資料
    if existing_df is not None:
        df = pd.concat([existing_df, new_df])
        df = df[~df.index.duplicated(keep='last')]  # 移除重複日期
    else:
        df = new_df

    # 儲存更新後的資料
    save_stock_data(symbol, df, data_type='raw')

    return df
