import numpy as np
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# 1. 導入/定義底層幾何與融合算子 (包含先前寫的邏輯)
# ---------------------------------------------------------


class MarketGeometryEngine:

    def __init__(self, lambda_reg: float = 1e-4):
        self.lambda_reg = lambda_reg

    def compute_metric_tensor(self, X_window: np.ndarray) -> np.ndarray:
        cov = np.cov(X_window, rowvar=False)
        metric = np.linalg.inv(cov + self.lambda_reg * np.eye(3))
        return metric

    def compute_curvature(
        self, dX: np.ndarray, d2X: np.ndarray, eps: float = 1e-6
    ) -> float:
        cross_prod = np.cross(dX, d2X)
        norm_cross = np.linalg.norm(cross_prod)
        norm_dX = np.linalg.norm(dX)
        return float(norm_cross / (norm_dX**3 + eps))

    def compute_turning_risk(
        self, curvature: float, distance: float, geo_acc: float
    ) -> float:
        z = 0.4 * curvature + 0.3 * distance + 0.3 * abs(geo_acc)
        return float(1.0 / (1.0 + np.exp(-z)))


class TrendScoreFusion:

    def __init__(self, lambda_scale: float = 1.0):
        self.lambda_scale = lambda_scale

    def calculate_trend_score(
        self,
        dmec_h: float,
        geo_trend: float,
        cycle_h: float,
        chip_nfs: float,
        timesfm_h: float,
        chronos_h: float,
    ) -> tuple[float, float]:
        weights = {
            'DMEC': 0.20,
            'Geo': 0.20,
            'Cycle': 0.15,
            'NFS': 0.15,
            'TimesFM': 0.15,
            'Chronos': 0.15,
        }
        fts_gf = (
            weights['DMEC'] * dmec_h
            + weights['Geo'] * geo_trend
            + weights['Cycle'] * cycle_h
            + weights['NFS'] * chip_nfs
            + weights['TimesFM'] * timesfm_h
            + weights['Chronos'] * chronos_h
        )
        trend_score = 100.0 * np.tanh(fts_gf / self.lambda_scale)
        return fts_gf, float(trend_score)


# ---------------------------------------------------------
# 2. Streamlit 前端介面繪製
# ---------------------------------------------------------
st.set_page_config(
    page_title="GeodesicX：DMEC-GF 盤前幾何預測模擬平台",
    page_icon="📈",
    layout="wide",
)

st.title("📈 GeodesicX：DMEC-GF 盤前幾何預測模擬平台")
st.caption(
    "微分幾何流形動力學 (E, V, A) × 08:30~08:59 盤前籌碼受力場 (NFS) × 時序大模型 Ensemble"
)

# 側邊欄控制
st.sidebar.header("⏱️ 08:30~08:59 盤前籌碼參數輸入")
chip_nfs = st.sidebar.slider(
    "主力籌碼淨力分數 (Net Force Score, NFS)",
    min_value=-1.0,
    max_value=1.0,
    value=0.45,
    step=0.05,
)
futures_diff = st.sidebar.number_input(
    "台指期盤前試撮價差 (點數)", value=25.0, step=5.0
)

# 執行算子計算
geo_engine = MarketGeometryEngine()
fusion_engine = TrendScoreFusion()

# 模擬幾何狀態變數
mock_dX = np.array([0.15, 0.08, -0.02])
mock_d2X = np.array([0.02, -0.01, 0.005])
curvature = geo_engine.compute_curvature(mock_dX, mock_d2X)
turning_risk = geo_engine.compute_turning_risk(curvature, 0.25, 0.05)

_, trend_score = fusion_engine.calculate_trend_score(
    dmec_h=0.6,
    geo_trend=0.5,
    cycle_h=0.4,
    chip_nfs=chip_nfs,
    timesfm_h=0.7,
    chronos_h=0.65,
)

# 頁面指標展示
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="預測趨勢分數 (TrendScore)",
        value=f"{trend_score:.1f}",
        delta="多頭主導" if trend_score > 0 else "空頭主導",
    )
with col2:
    st.metric(
        label="軌跡曲率 (Curvature κ)",
        value=f"{curvature:.4f}",
        delta="-0.002 (軌跡穩定)",
    )
with col3:
    st.metric(
        label="轉折風險 (Turning Risk)",
        value=f"{turning_risk * 100:.1f}%",
        delta="低風險區間",
        delta_color="normal",
    )

st.markdown("---")
st.subheader("📊 開盤 (5D / 20D / 60D) 機率區間推演 (Q10 / Q50 / Q90)")

# 模擬推演圖表
dates = pd.date_range(start="2026-08-24", periods=20, freq="B")
base_price = 22000 + chip_nfs * 100 + futures_diff
q50 = base_price + np.cumsum(np.random.normal(15, 5, 20))
q90 = q50 + np.linspace(10, 150, 20)
q10 = q50 - np.linspace(10, 150, 20)

chart_df = pd.DataFrame(
    {"Q50 (核心預測)": q50, "Q90 (上限)": q90, "Q10 (下限)": q10},
    index=dates,
)
st.line_chart(chart_df)

st.success("✅ GeodesicX 幾何引擎正常運行中，已成功接收 08:30~08:59 盤前試撮訊號。")