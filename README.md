# Python 量化交易系統

基於 Python 的量化交易策略開發、回測與自動化系統。

## 功能特色

- 多種交易策略實作（動量、均值回歸）
- 完整的回測系統
- AI 輔助參數優化
- 每日自動化運行
- 豐富的技術指標庫
- 視覺化分析工具

## 專案架構

```
quant/
│
├── data/                    # 歷史資料與快取
│   ├── raw/                 # 原始資料 (CSV)
│   └── processed/           # 加工後資料
│
├── strategies/              # 交易策略
│   ├── base_strategy.py     # 基礎策略類別
│   ├── momentum.py          # 動量策略
│   └── mean_reversion.py    # 均值回歸策略
│
├── backtest/                # 回測系統
│   ├── backtester.py        # 回測引擎
│   └── evaluation.py        # 評估指標
│
├── ai/                      # AI 優化工具
│   ├── optimize_strategy.py # 策略優化器
│   └── prompts/             # Prompt 模板
│
├── daily/                   # 每日自動化
│   ├── fetch_today.py       # 抓取資料
│   ├── generate_signal.py   # 產生訊號
│   └── summary_report.py    # 生成報告
│
├── utils/                   # 工具模組
│   ├── indicators.py        # 技術指標
│   ├── fetch.py             # 資料抓取
│   └── plot.py              # 繪圖工具
│
├── notebooks/               # Jupyter Notebooks
│   ├── momentum_explore.ipynb
│   └── mean_reversion_explore.ipynb
│
└── main.py                  # 主程式進入點
```

## 安裝步驟

### 1. 建立虛擬環境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 2. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 3. 設定資料來源

專案支援兩種資料來源：

- **yfinance** (免費，無需註冊)
- **FinMind** (需註冊取得 API Token)

## 快速開始

### 1. 抓取股票資料

```bash
# 使用 yfinance
python main.py fetch --symbols 2330 0050 --source yfinance

# 使用 FinMind
python main.py fetch --symbols 2330 0050 --source finmind
```

### 2. 執行回測

```bash
# 測試動量策略
python main.py backtest --symbol 2330 --strategy momentum

# 測試均值回歸策略
python main.py backtest --symbol 0050 --strategy mean_reversion
```

### 3. 優化策略參數

```bash
python main.py optimize --symbol 2330 --strategy momentum
```

### 4. 執行每日例行作業

```bash
python main.py daily --symbols 2330 0050 0056
```

## 策略說明

### 動量策略 (Momentum Strategy)

使用 SMA20 和 SMA60 進行趨勢追蹤：
- 當短期均線上穿長期均線時買入 (Golden Cross)
- 當短期均線下穿長期均線時賣出 (Death Cross)

**適用場景**：趨勢明顯的市場

### 均值回歸策略 (Mean Reversion Strategy)

使用 RSI 和 ATR 指標：
- 當 RSI < 30 (超賣) 時買入
- 當 RSI > 70 (超買) 時賣出
- 使用 ATR 設定停損位

**適用場景**：震盪盤整的市場

## 評估指標

- **總報酬率**：總體獲利百分比
- **年化報酬率 (CAGR)**：複合年增長率
- **最大回撤 (MDD)**：最大資產縮水幅度
- **夏普比率**：風險調整後報酬
- **勝率**：獲利交易佔比
- **波動率**：年化標準差

## Jupyter Notebooks

提供互動式探索環境：

```bash
jupyter notebook
```

開啟以下 Notebooks：
- `notebooks/momentum_explore.ipynb` - 動量策略探索
- `notebooks/mean_reversion_explore.ipynb` - 均值回歸策略探索

## 進階使用

### 自訂策略

繼承 `BaseStrategy` 類別並實作以下方法：

```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def calculate_indicators(self, data):
        # 計算技術指標
        pass

    def generate_signals(self, data):
        # 生成交易訊號
        pass
```

### 新增技術指標

在 `utils/indicators.py` 中新增函數：

```python
def calculate_my_indicator(prices, period):
    # 實作指標邏輯
    pass
```

## 注意事項

⚠️ **免責聲明**

本專案僅供學習與研究用途，不構成投資建議。
實際交易前請謹慎評估風險，作者不對任何投資損失負責。

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 聯絡方式

如有問題或建議，歡迎開 Issue 討論。
