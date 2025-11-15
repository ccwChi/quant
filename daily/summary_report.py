"""
每日摘要報告生成器
自動產生當日交易建議與市場分析報告
"""
import sys
import os
from datetime import datetime
import json

# 加入專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_text_report(signals_file: str, output_file: str = None):
    """
    生成文字格式報告

    Args:
        signals_file: 訊號 JSON 檔案路徑
        output_file: 輸出報告檔案路徑
    """
    if output_file is None:
        today = datetime.now().strftime('%Y%m%d')
        output_file = f'report_{today}.txt'

    # 讀取訊號資料
    with open(signals_file, 'r', encoding='utf-8') as f:
        signals = json.load(f)

    # 生成報告
    report = []
    report.append("=" * 60)
    report.append(f"每日交易建議報告")
    report.append(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 60)
    report.append("")

    # 統計
    buy_signals = [s for s in signals.keys() if signals[s]['recommendation'] == '買入']
    sell_signals = [s for s in signals.keys() if signals[s]['recommendation'] == '賣出']
    hold_signals = [s for s in signals.keys() if signals[s]['recommendation'] == '持有']

    report.append("📊 訊號統計")
    report.append(f"  買入訊號: {len(buy_signals)} 檔")
    report.append(f"  賣出訊號: {len(sell_signals)} 檔")
    report.append(f"  持有: {len(hold_signals)} 檔")
    report.append("")

    # 買入建議
    if buy_signals:
        report.append("🔥 買入建議")
        report.append("-" * 60)
        for symbol in buy_signals:
            data = signals[symbol]
            report.append(f"股票代號: {symbol}")
            report.append(f"  收盤價: {data['close']:.2f}")
            report.append(f"  動量訊號: {'買入' if data['momentum']['signal'] > 0 else '持有'}")
            report.append(f"    SMA20: {data['momentum']['SMA20']:.2f}")
            report.append(f"    SMA60: {data['momentum']['SMA60']:.2f}")
            report.append(f"  均值回歸訊號: {'買入' if data['mean_reversion']['signal'] > 0 else '持有'}")
            report.append(f"    RSI: {data['mean_reversion']['RSI']:.2f}")
            report.append("")

    # 賣出建議
    if sell_signals:
        report.append("⚠️  賣出建議")
        report.append("-" * 60)
        for symbol in sell_signals:
            data = signals[symbol]
            report.append(f"股票代號: {symbol}")
            report.append(f"  收盤價: {data['close']:.2f}")
            report.append(f"  動量訊號: {'賣出' if data['momentum']['signal'] < 0 else '持有'}")
            report.append(f"  均值回歸訊號: {'賣出' if data['mean_reversion']['signal'] < 0 else '持有'}")
            report.append(f"    RSI: {data['mean_reversion']['RSI']:.2f}")
            report.append("")

    # 持有部位
    if hold_signals:
        report.append("📌 持有部位")
        report.append("-" * 60)
        for symbol in hold_signals:
            data = signals[symbol]
            report.append(f"{symbol}: {data['close']:.2f} | RSI: {data['mean_reversion']['RSI']:.2f}")

    report.append("")
    report.append("=" * 60)
    report.append("⚠️  免責聲明: 本報告僅供參考，不構成投資建議")
    report.append("=" * 60)

    # 寫入檔案
    report_text = "\n".join(report)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)
    print(f"\n報告已儲存至: {output_file}")

    return report_text


def generate_html_report(signals_file: str, output_file: str = None):
    """
    生成 HTML 格式報告

    Args:
        signals_file: 訊號 JSON 檔案路徑
        output_file: 輸出 HTML 檔案路徑
    """
    if output_file is None:
        today = datetime.now().strftime('%Y%m%d')
        output_file = f'report_{today}.html'

    # 讀取訊號資料
    with open(signals_file, 'r', encoding='utf-8') as f:
        signals = json.load(f)

    html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日交易建議報告 - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        .summary {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .stock-card {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .buy {{ border-left: 4px solid #4CAF50; }}
        .sell {{ border-left: 4px solid #f44336; }}
        .hold {{ border-left: 4px solid #9E9E9E; }}
        .metric {{ display: inline-block; margin-right: 20px; }}
        .disclaimer {{ background: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 每日交易建議報告</h1>
        <p>生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="summary">
            <h2>訊號統計</h2>
"""

    buy_count = sum(1 for s in signals.values() if s['recommendation'] == '買入')
    sell_count = sum(1 for s in signals.values() if s['recommendation'] == '賣出')
    hold_count = sum(1 for s in signals.values() if s['recommendation'] == '持有')

    html += f"""
            <div class="metric">🔥 買入: {buy_count}</div>
            <div class="metric">⚠️ 賣出: {sell_count}</div>
            <div class="metric">📌 持有: {hold_count}</div>
        </div>
"""

    for symbol, data in signals.items():
        rec_class = data['recommendation']
        if rec_class == '買入':
            rec_class = 'buy'
        elif rec_class == '賣出':
            rec_class = 'sell'
        else:
            rec_class = 'hold'

        html += f"""
        <div class="stock-card {rec_class}">
            <h3>{symbol} - {data['recommendation']}</h3>
            <p><strong>收盤價:</strong> {data['close']:.2f}</p>
            <p><strong>動量指標:</strong> SMA20={data['momentum']['SMA20']:.2f}, SMA60={data['momentum']['SMA60']:.2f}</p>
            <p><strong>RSI:</strong> {data['mean_reversion']['RSI']:.2f}</p>
        </div>
"""

    html += """
        <div class="disclaimer">
            <strong>⚠️ 免責聲明:</strong> 本報告僅供參考，不構成投資建議。投資有風險，請謹慎評估。
        </div>
    </div>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML 報告已儲存至: {output_file}")


def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(description='生成每日摘要報告')
    parser.add_argument('signals_file', type=str, help='訊號 JSON 檔案路徑')
    parser.add_argument('--format', choices=['text', 'html', 'both'], default='text', help='報告格式')
    parser.add_argument('--output', type=str, help='輸出檔案路徑')

    args = parser.parse_args()

    if args.format in ['text', 'both']:
        generate_text_report(args.signals_file, args.output)

    if args.format in ['html', 'both']:
        output = args.output.replace('.txt', '.html') if args.output else None
        generate_html_report(args.signals_file, output)


if __name__ == '__main__':
    main()
