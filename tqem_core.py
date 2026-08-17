"""
tqem_core.py
TQEM Common Core Pipeline for ETF Analysis Platform
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple


class DynamicWeightEngine:
    """
    動態權重引擎：依據 Regime, 近期 IC/HitRate, TimesFM Confidence 與 Risk Penalty 每日更新
    Formula: w_i(t) = Normalize[ w_base * R_i(t) * P_i(t) * C_i(t) * K_i(t) ]
    """
    def __init__(self, base_weights: Dict[str, float]):
        self.base_weights = base_weights

    def calculate_weights(
        self, 
        regime_factor: Dict[str, float], 
        perf_factor: Dict[str, float], 
        confidence_factor: Dict[str, float], 
        risk_penalty: Dict[str, float]
    ) -> Dict[str, float]:
        
        raw_weights = {}
        for feature, w_base in self.base_weights.items():
            r = regime_factor.get(feature, 1.0)
            p = perf_factor.get(feature, 1.0)
            c = confidence_factor.get(feature, 1.0)
            k = risk_penalty.get(feature, 1.0)
            
            raw_weights[feature] = w_base * r * p * c * k
            
        total_w = sum(raw_weights.values())
        if total_w == 0:
            return self.base_weights
            
        # Normalize to sum up to 1.0
        normalized_weights = {k: v / total_w for k, v in raw_weights.items()}
        return normalized_weights


class KalmanWeightSmoother:
    """
    卡爾曼濾波器：用於平滑動態權重，降低訊號噪聲與換手率 (Turnover)
    """
    def __init__(self, process_noise: float = 1e-4, measurement_noise: float = 1e-2):
        self.q = process_noise  # 過程雜訊 covariance
        self.r = measurement_noise  # 量測雜訊 covariance
        self.x = None  # 狀態估計 (平滑後的權重)
        self.p = 1.0   # 估計誤差 covariance

    def smooth(self, z: np.ndarray) -> np.ndarray:
        """
        z: 原始動態權重向量 (1D array)
        """
        if self.x is None:
            self.x = z
            return self.x

        # 預測更新
        x_pred = self.x
        p_pred = self.p + self.q

        # 量測更新 (Kalman Gain)
        k_gain = p_pred / (p_pred + self.r)
        self.x = x_pred + k_gain * (z - x_pred)
        self.p = (1 - k_gain) * p_pred

        # 再確保權重總和為 1.0
        self.x = self.x / np.sum(self.x)
        return self.x


class TQEMPipeline:
    """
    TQEM 整合推論主控管線
    """
    def __init__(self, feature_skill_module: Any):
        """
        傳入特定的 ETF Feature Skill (例如 TQEMLargeCapSkill, TQEMDividendSkill)
        """
        self.skill = feature_skill_module
        self.weight_engine = DynamicWeightEngine(base_weights=self.skill.get_base_weights())
        self.kalman = KalmanWeightSmoother()

    def run_inference(self, df_data: pd.DataFrame) -> Dict[str, Any]:
        # 1. 特徵工程 (呼叫專屬 Skill)
        features = self.skill.extract_features(df_data)
        
        # 2. Regime 偵測
        regime = self.skill.detect_regime(df_data)
        
        # 3. 模擬/呼叫 TimesFM 進行多時間尺度預測 (Point & Quantile)
        forecasts = self.skill.run_timesfm_forecast(features)
        
        # 4. 計算動態權重
        regime_factor, perf_factor, conf_factor, risk_penalty = self.skill.get_weight_factors(regime, forecasts)
        raw_weights = self.weight_engine.calculate_weights(regime_factor, perf_factor, conf_factor, risk_penalty)
        
        # 5. Kalman 平滑
        w_vector = np.array(list(raw_weights.values()))
        smoothed_w_vector = self.kalman.smooth(w_vector)
        smoothed_weights = dict(zip(raw_weights.keys(), smoothed_w_vector))
        
        # 6. 生成 Alpha 訊號與評估
        alpha_signal = self.skill.generate_alpha(forecasts, smoothed_weights)
        
        return {
            "regime": regime,
            "forecasts": forecasts,
            "weights_raw": raw_weights,
            "weights_smoothed": smoothed_weights,
            "alpha_signal": alpha_signal
        }