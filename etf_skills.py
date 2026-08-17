"""
etf_skills.py
台灣 1~10 大類別 ETF 專用特徵群、Regime 與預測目標定義技能庫
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


# 1. 大型市值型 (0050, 006208)
class TQEMLargeCapSkill(BaseETFSkill):
    def get_base_weights(self) -> Dict[str, float]:
        return {"price_trend": 0.25, "global_market": 0.15, "flow_capital": 0.15, "nav_premium": 0.15, "liquidity": 0.10, "concentration": 0.10, "macro_fx": 0.10}
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame: return df
    def detect_regime(self, df: pd.DataFrame) -> str: return "HighVol"
    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]: return {"target_return": 0.012, "target_volatility": 0.15}
    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]:
        return ({k: 1.2 if k == "liquidity" else 1.0 for k in self.get_base_weights()}, {}, {}, {})
    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        return float(np.clip(forecasts["target_return"] * 25, -1.0, 1.0))


# 2. 高股息/收益型 (0056, 00878, 00919)
class TQEMDividendSkill(BaseETFSkill):
    def get_base_weights(self) -> Dict[str, float]:
        return {"dividend_yield": 0.30, "earnings_growth": 0.20, "quality_roe": 0.15, "valuation": 0.15, "fill_days": 0.10, "macro_rates": 0.10}
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame: return df
    def detect_regime(self, df: pd.DataFrame) -> str: return "RateRising"
    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]: return {"target_return": 0.008, "target_yield": 0.068}
    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]:
        return ({k: 1.3 if k == "dividend_yield" else 1.0 for k in self.get_base_weights()}, {}, {}, {})
    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        return float(np.clip(forecasts["target_yield"] * 12, -1.0, 1.0))


# 3. 產業/主題型 (00830, 00881, 半導體/AI)
class TQEMThematicSkill(BaseETFSkill):
    def get_base_weights(self) -> Dict[str, float]:
        return {"tech_momentum": 0.30, "supply_chain": 0.25, "sector_capex": 0.15, "earnings_surprise": 0.15, "global_peers": 0.15}
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame: return df
    def detect_regime(self, df: pd.DataFrame) -> str: return "TechExpansion"
    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]: return {"target_return": 0.025, "target_volatility": 0.22}
    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]: return ({}, {}, {}, {})
    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        return float(np.clip(forecasts["target_return"] * 30, -1.0, 1.0))


# 4. 債券型 (00679B, 00720B, 美債/公司債)
class TQEMBondSkill(BaseETFSkill):
    def get_base_weights(self) -> Dict[str, float]:
        return {"yield_curve": 0.30, "fed_policy": 0.25, "credit_spread": 0.20, "duration_risk": 0.15, "fx_hedging": 0.10}
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame: return df
    def detect_regime(self, df: pd.DataFrame) -> str: return "FedPivotEase"
    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]: return {"target_return": 0.005, "yield_change": -0.0015}
    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]: return ({}, {}, {}, {})
    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        return float(np.clip(-forecasts["yield_change"] * 100, -1.0, 1.0))


# 5. 海外跨國型 (00646, 00757, 美股/陸股/日股)
class TQEMOverseasSkill(BaseETFSkill):
    def get_base_weights(self) -> Dict[str, float]:
        return {"fx_rate": 0.25, "global_macro": 0.25, "overseas_index": 0.20, "local_liquidity": 0.15, "geopolitical": 0.15}
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame: return df
    def detect_regime(self, df: pd.DataFrame) -> str: return "DollarStrong"
    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]: return {"target_return": 0.015, "fx_impact": 0.004}
    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]: return ({}, {}, {}, {})
    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        return float(np.clip((forecasts["target_return"] + forecasts["fx_impact"]) * 20, -1.0, 1.0))


# 6. 槓桿/反向型 (00631L, 00632R)
class TQEMLeveragedInverseSkill(BaseETFSkill):
    def get_base_weights(self) -> Dict[str, float]:
        return {"underlying_momentum": 0.35, "volatility_drag": 0.25, "futures_basis": 0.20, "path_decay": 0.20}
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame: return df
    def detect_regime(self, df: pd.DataFrame) -> str: return "HighVolDecay"
    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]: return {"target_return": -0.01, "vol_drag_penalty": 0.005}
    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]: return ({}, {}, {}, {})
    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        return float(np.clip(forecasts["target_return"] * 15, -1.0, 1.0))


# 7. 商品/原物料型 (00635U, 00642U, 黃金/石油)
class TQEMCommoditySkill(BaseETFSkill):
    def get_base_weights(self) -> Dict[str, float]:
        return {"futures_roll_yield": 0.30, "inflation_expectation": 0.25, "usd_index": 0.20, "supply_demand_gap": 0.25}
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame: return df
    def detect_regime(self, df: pd.DataFrame) -> str: return "InflationRise"
    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]: return {"target_return": 0.018, "roll_yield": -0.002}
    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]: return ({}, {}, {}, {})
    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        return float(np.clip(forecasts["target_return"] * 20, -1.0, 1.0))


# 8. 主動型 ETF (Active Managed)
class TQEMActiveSkill(BaseETFSkill):
    def get_base_weights(self) -> Dict[str, float]:
        return {"manager_alpha": 0.30, "holding_turnover": 0.20, "factor_exposure": 0.20, "nav_momentum": 0.15, "market_sentiment": 0.15}
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame: return df
    def detect_regime(self, df: pd.DataFrame) -> str: return "FactorRotation"
    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]: return {"target_return": 0.014, "manager_skill_score": 0.85}
    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]: return ({}, {}, {}, {})
    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        return float(np.clip(forecasts["target_return"] * 22, -1.0, 1.0))


# 9. 組合/Multi-Asset 型
class TQEMMultiAssetSkill(BaseETFSkill):
    def get_base_weights(self) -> Dict[str, float]:
        return {"asset_correlation": 0.30, "risk_parity_weight": 0.25, "rebalance_effect": 0.25, "macro_cycle": 0.20}
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame: return df
    def detect_regime(self, df: pd.DataFrame) -> str: return "LateCycle"
    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]: return {"target_return": 0.007, "portfolio_vol": 0.08}
    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]: return ({}, {}, {}, {})
    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        return float(np.clip(forecasts["target_return"] * 20, -1.0, 1.0))


# 10. 聰明 Beta / 多因子型 (Smart Beta)
class TQEMSmartBetaSkill(BaseETFSkill):
    def get_base_weights(self) -> Dict[str, float]:
        return {"value_factor": 0.20, "momentum_factor": 0.20, "quality_factor": 0.20, "low_vol_factor": 0.20, "size_factor": 0.20}
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame: return df
    def detect_regime(self, df: pd.DataFrame) -> str: return "QualityTilt"
    def run_timesfm_forecast(self, features: pd.DataFrame) -> Dict[str, float]: return {"target_return": 0.011, "factor_ic": 0.08}
    def get_weight_factors(self, regime: str, forecasts: Dict[str, float]) -> Tuple[Dict, Dict, Dict, Dict]: return ({}, {}, {}, {})
    def generate_alpha(self, forecasts: Dict[str, float], weights: Dict[str, float]) -> float:
        return float(np.clip(forecasts["target_return"] * 25, -1.0, 1.0))


# 工廠映射表
SKILL_MAP = {
    "第1類：大型市值型 (如 0050, 006208)": TQEMLargeCapSkill,
    "第2類：高股息/收益型 (如 0056, 00878, 00919)": TQEMDividendSkill,
    "第3類：產業/主題型 (如 00830, 00881)": TQEMThematicSkill,
    "第4類：債券/固定收益型 (如 00679B, 00720B)": TQEMBondSkill,
    "第5類：海外/跨國型 (如 00646, 00757)": TQEMOverseasSkill,
    "第6類：槓桿/反向型 (如 00631L, 00632R)": TQEMLeveragedInverseSkill,
    "第7類：商品/原物料型 (如 00635U, 00642U)": TQEMCommoditySkill,
    "第8類：主動管理型 (Active ETF)": TQEMActiveSkill,
    "第9類：多重資產/組合型 (Multi-Asset)": TQEMMultiAssetSkill,
    "第10類：聰明 Beta/多因子型 (Smart Beta)": TQEMSmartBetaSkill,
}