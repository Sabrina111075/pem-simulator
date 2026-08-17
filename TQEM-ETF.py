"""
TQEM-ETF.py - Streamlit 主畫面 (自動觸發優化版)
"""
import streamlit as st
import pandas as pd
import numpy as np

from tqem_core import TQEMPipeline
from etf_skills import SKILL_MAP

st.set_page_config(page_title="台灣 ETF TimesFM + TQEM 預測系統", layout="wide")

@st.cache_resource
def load_tqem_pipeline(category_name: str):
    skill_cls = SKILL_MAP.get(category_name)
    skill_instance = skill_cls()
    return TQEMPipeline(feature_skill_module=skill_instance)

@st.cache_data
def load_dummy_data():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
    df = pd.DataFrame({
        'date': dates,
        'close': np.linspace(100, 150, 100) + np.random.normal(0, 2, 100),
        'nav': np.linspace(100, 150, 100) + np.random.normal(0, 1.8, 100)
    })
    return df

st.title("📊 台灣 ETF TimesFM + TQEM 智慧預測與決策平台")
st.caption("結合 TimesFM 時間序列預測、Dynamic Weight 動態權重與 Kalman 平滑風控引擎")

# 側邊欄選單
st.sidebar.header("標的選擇")
selected_category = st.sidebar.selectbox(
    "請選擇 ETF 類別：",
    list(SKILL_MAP.keys())
)

# 自動執行運算與呈現
pipeline = load_tqem_pipeline(selected_category)
df_data = load_dummy_data()

with st.spinner(f"正在為【{selected_category.split('：')[1]}】進行自動運算與 Kalman 平滑..."):
    result = pipeline.run_inference(df_data)

# 結果展示區
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("分析指標")
    st.metric("偵測市場狀態 (Regime)", result["regime"])
    st.metric("最終 Alpha 訊號強度", f"{result['alpha_signal']:.4f}")

with col2:
    st.subheader("Kalman 平滑前後的特徵動態權重")
    df_weights = pd.DataFrame({
        "原始動態權重": result["weights_raw"],
        "Kalman 平滑權重": result["weights_smoothed"]
    })
    st.dataframe(df_weights, use_container_width=True)
    st.bar_chart(df_weights)