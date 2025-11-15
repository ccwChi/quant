"""
基礎策略類別
所有策略都應該繼承這個類別
"""
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class BaseStrategy(ABC):
    """所有策略的基底類別"""

    def __init__(self, name: str, params: Dict[str, Any] = None):
        """
        初始化策略

        Args:
            name: 策略名稱
            params: 策略參數字典
        """
        self.name = name
        self.params = params or {}

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易訊號

        Args:
            data: 包含價格資料的 DataFrame (必須有 'close' 欄位)

        Returns:
            DataFrame 加上 'signal' 欄位 (1=買入, -1=賣出, 0=持有)
        """
        pass

    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        計算技術指標

        Args:
            data: 原始價格資料

        Returns:
            DataFrame 加上計算的指標欄位
        """
        pass

    def get_params(self) -> Dict[str, Any]:
        """取得策略參數"""
        return self.params

    def set_params(self, params: Dict[str, Any]):
        """更新策略參數"""
        self.params.update(params)

    def __repr__(self):
        return f"{self.name}(params={self.params})"
