"""
etf_skills.py
10 大類 ETF 專用特徵群、Regime 與預測目標定義技能模組
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any


class BaseETFSkill(ABC):
    @abstractmethod
    def get_base_weights(self) -> Dict[str, float]:
        pass

    @abstractmethod
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def detect_regime(self, df: pd.DataFrame) -> str:
        pass

    @abstractmethod
    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]:
        pass

    @abstractmethod
    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]:
        pass

    @abstractmethod
    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        pass


class TQEMLargeCapSkill(BaseETFSkill):
    """
    第1類：大型市值型／大型權值型 ETF (如 0050, 006208)
    關鍵特徵：Index, NAV/Premium, Liquidity, Global, Concentration
    預測目標：ETF Return, Volatility, Premium/Discount, Tracking Difference
    """
    def get_base_weights(self) -> Dict[str, float]:
        return {
            "price_trend": 0.25,
            "global_market": 0.15,
            "flow_capital": 0.15,
            "nav_premium": 0.15,
            "liquidity": 0.10,
            "concentration": 0.10,
            "macro_fx": 0.10
        }

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        # 計算 8 大 Feature Groups 邏輯
        df['return_5d'] = df['close'].pct_change(5)
        df['nav_discount'] = (df['close'] - df['nav']) / df['nav']
        return df

    def detect_regime(self, df: pd.DataFrame) -> str:
        # 市場狀態識別 (Bull / Bear / HighVol)
        vol = df['close'].pct_change().std() * np.sqrt(252)
        if vol > 0.25:
            return "HighVol"
        return "Bull" if df['close'].iloc[-1] > df['close'].rolling(50).mean().iloc[-1] else "Bear"

    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]:
        # 多目標預測 (Return, Volatility, Premium/Discount, Tracking Difference)
        return {
            "target_return": 0.012,        # 未來 5 日預期報酬
            "target_volatility": 0.15,     # 預期波動度
            "target_premium_gap": -0.001,  # 折溢價縮小預測
            "target_tracking_diff": 0.0002 # 預期追蹤誤差
        }

    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]:
        # 根據 Regime 動態調整權重
        regime_factor = {k: 1.0 for k in self.get_base_weights()}
        if regime == "HighVol":
            regime_factor["liquidity"] = 1.5
            regime_factor["concentration"] = 0.5
            
        perf_factor = {k: 1.0 for k in self.get_base_weights()}
        conf_factor = {k: 1.0 for k in self.get_base_weights()}
        risk_penalty = {k: 1.0 for k in self.get_base_weights()}
        
        return regime_factor, perf_factor, conf_factor, risk_penalty

    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        # 計算最終 Alpha 買賣訊號 (-1.0 ~ 1.0)
        alpha = forecasts["target_return"] * 100 * weights["price_trend"]
        return float(np.clip(alpha, -1.0, 1.0))


class TQEMDividendSkill(BaseETFSkill):
    """
    第2類：高股息／收益型 ETF (如 0056, 00878, 00919)
    關鍵特徵：Dividend, Earnings, Quality, Valuation, Fill Days
    預測目標：ETF Return, Volatility, Dividend Yield, Fill Days, Dividend Stability
    """
    def get_base_weights(self) -> Dict[str, float]:
        return {
            "dividend_yield": 0.30,
            "earnings_growth": 0.20,
            "quality_roe": 0.15,
            "valuation": 0.15,
            "fill_days_history": 0.10,
            "macro_rates": 0.10
        }

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        # 特徵工程（如填息天數計算、股息率計算）
        return df

    def detect_regime(self, df: pd.DataFrame) -> str:
        return "RateRising"  # 升息環境/降息環境/景氣衰退

    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]:
        return {
            "target_return": 0.008,
            "target_yield": 0.068,           # 預期殖利率 6.8%
            "target_fill_days": 12.0,        # 預期填息天數
            "target_dividend_stability": 0.9 # 配息穩定度得分
        }

    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]:
        regime_factor = {k: 1.0 for k in self.get_base_weights()}
        if regime == "RateRising":
            regime_factor["macro_rates"] = 1.4
            regime_factor["quality_roe"] = 1.2
            
        return regime_factor, {}, {}, {}

    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        # 高股息特有 Alpha 邏輯：考慮殖利率與填息天數
        yield_score = forecasts["target_yield"] * 10
        fill_penalty = 1.0 / forecasts["target_fill_days"]
        alpha = (yield_score + fill_penalty) * weights["dividend_yield"]
        return float(np.clip(alpha, -1.0, 1.0))