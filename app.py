"""
app.py - Streamlit 應用程式主入口檔
"""
import streamlit as st
import pandas as pd
import numpy as np

# 1. 從我們建立的兩個檔案導入模組
from tqem_core import TQEMPipeline
from etf_skills import TQEMLargeCapSkill, TQEMDividendSkill

# 設定頁面標題與配置
st.set_page_config(page_title="台灣 ETF TimesFM + TQEM 預測平台", layout="wide")

# 2. 步驟 C：使用 @st.cache_resource 避免重複初始化引擎
@st.cache_resource
def load_tqem_pipeline(etf_type: str):
    if etf_type == "第1類：大型市值型 (如 0050, 006208)":
        skill = TQEMLargeCapSkill()
    else:
        skill = TQEMDividendSkill()
    return TQEMPipeline(feature_skill_module=skill)

# ----------------- UI 介面繪製 -----------------
st.title("📊 台灣 ETF TimesFM + TQEM 智慧預測與決策平台")
st.caption("結合 TimesFM 時間序列預測、Dynamic Weight 動態權重與 Kalman 平滑風控引擎")

# 側邊欄選擇 ETF 類別
st.sidebar.header("標的選擇")
selected_category = st.sidebar.selectbox(
    "請選擇 ETF 類別：",
    [
        "第1類：大型市值型 (如 0050, 006208)",
        "第2類：高股息/收益型 (如 0056, 00878, 00919)"
    ]
)

# 載入 Pipeline
pipeline = load_tqem_pipeline(selected_category)

# 模擬測試數據（實務上可串接 API 或上傳 CSV）
@st.cache_data
def load_dummy_data():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
    df = pd.DataFrame({
        'date': dates,
        'close': np.linspace(100, 150, 100) + np.random.normal(0, 2, 100),
        'nav': np.linspace(100, 150, 100) + np.random.normal(0, 1.8, 100)
    })
    return df

df_data = load_dummy_data()

# 執行 TQEM 推論
if st.button("🚀 執行 TQEM 預測與權重計算"):
    with st.spinner("正在進行 Regime 偵測、TimesFM 預測與 Kalman 平滑..."):
        result = pipeline.run_inference(df_data)

    st.success("計算完成！")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("偵測市場狀態 (Regime)", result["regime"])
        st.metric("最終 Alpha 訊號強度", f"{result['alpha_signal']:.4f}")

    with col2:
        st.subheader("Kalman 平滑前後的特徵動態權重")
        df_weights = pd.DataFrame({
            "原始動態權重": result["weights_raw"],
            "Kalman 平滑權重": result["weights_smoothed"]
        })
        st.dataframe(df_weights)
        st.bar_chart(df_weights)