"""
AI 策略優化工具
使用 GPT 自動調整策略參數
"""
import json
from typing import Dict, Any, List
from strategies.base_strategy import BaseStrategy
from backtest.backtester import Backtester
import pandas as pd


class StrategyOptimizer:
    """策略優化器 (用於 AI 輔助)"""

    def __init__(self, data: pd.DataFrame, initial_capital: float = 100000):
        """
        初始化優化器

        Args:
            data: 歷史價格資料
            initial_capital: 初始資金
        """
        self.data = data
        self.initial_capital = initial_capital
        self.optimization_history = []

    def evaluate_strategy(self, strategy: BaseStrategy) -> Dict[str, Any]:
        """
        評估單一策略

        Args:
            strategy: 策略實例

        Returns:
            評估結果字典
        """
        backtester = Backtester(initial_capital=self.initial_capital)
        backtester.run(strategy, self.data)
        metrics = backtester.summary()

        result = {
            'strategy_name': strategy.name,
            'parameters': strategy.get_params(),
            'metrics': metrics
        }

        self.optimization_history.append(result)
        return result

    def grid_search(self, strategy_class, param_grid: Dict[str, List]) -> List[Dict[str, Any]]:
        """
        網格搜尋最佳參數

        Args:
            strategy_class: 策略類別
            param_grid: 參數網格，例如 {'short_window': [10, 20, 30], 'long_window': [50, 60, 70]}

        Returns:
            所有測試結果的列表
        """
        from itertools import product

        # 生成所有參數組合
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(product(*param_values))

        results = []

        for combination in param_combinations:
            params = dict(zip(param_names, combination))

            # 創建策略實例
            strategy = strategy_class(**params)

            # 評估策略
            result = self.evaluate_strategy(strategy)
            results.append(result)

            print(f"測試參數: {params}")
            print(f"總報酬: {result['metrics']['total_return']:.2f}%")
            print(f"最大回撤: {result['metrics']['max_drawdown']:.2f}%")
            print(f"夏普比率: {result['metrics']['sharpe_ratio']:.2f}")
            print("-" * 50)

        # 根據夏普比率排序
        results.sort(key=lambda x: x['metrics']['sharpe_ratio'], reverse=True)

        return results

    def get_best_result(self) -> Dict[str, Any]:
        """取得最佳結果"""
        if not self.optimization_history:
            raise ValueError("尚未執行任何優化")

        best = max(self.optimization_history,
                   key=lambda x: x['metrics']['sharpe_ratio'])
        return best

    def export_results(self, filename: str):
        """
        匯出優化結果到 JSON

        Args:
            filename: 輸出檔案名稱
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_history, f, indent=2, ensure_ascii=False)

        print(f"結果已匯出至: {filename}")

    def generate_gpt_prompt(self) -> str:
        """
        生成給 GPT 的優化提示

        Returns:
            Prompt 字串
        """
        if not self.optimization_history:
            return "尚未有優化歷史記錄"

        best = self.get_best_result()

        prompt = f"""
我正在優化一個量化交易策略，目前最佳參數如下：

策略: {best['strategy_name']}
參數: {json.dumps(best['parameters'], indent=2, ensure_ascii=False)}

績效指標:
- 總報酬率: {best['metrics']['total_return']:.2f}%
- 最大回撤: {best['metrics']['max_drawdown']:.2f}%
- 夏普比率: {best['metrics']['sharpe_ratio']:.2f}
- 年化報酬率: {best['metrics']['cagr']:.2f}%

請根據這些結果，建議下一步應該如何調整參數以改善策略表現。
考慮因素:
1. 降低最大回撤
2. 提高夏普比率
3. 維持穩定的報酬

請提供 3-5 組新的參數組合供測試。
"""
        return prompt
