import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# --- 頁面配置 ---
st.set_page_config(page_title="PEM電解槽數據模擬系統", layout="wide")

# --- 自定義 CSS (解決吃字與卡片設計) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* 防止卡片標題吃字 */
    div[data-testid="stMetricLabel"] > div {
        overflow: visible !important;
        white-space: normal !important;
        font-weight: bold !important;
        color: #333 !important;
    }
    /* 右上角即時時間樣式 */
    .time-container {
        text-align: right;
        font-family: 'Courier New', Courier, monospace;
        color: #555;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 側邊欄：控制參數 ---
with st.sidebar:
    st.header("⚙️ 模擬參數設置")
    temperature = st.slider("電解槽工作溫度 (°C)", min_value=20, max_value=90, value=60)
    pressure = st.slider("工作壓力 (bar)", min_value=1.0, max_value=30.0, value=1.0)
    current_density_max = st.number_input("最高電流密度 (A/cm²)", value=2.0)
    st.info("調整上方參數以觀察極化曲線變化。")

# --- 標題區域與即時時間 ---
col_title, col_time = st.columns([3, 1])

with col_title:
    st.title("🔋 PEM電解槽數據模擬系統")

with col_time:
    # 顯示目前系統時間
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f'<div class="time-container">最後更新時間：<br><b>{now}</b></div>', unsafe_allow_html=True)

# --- 核心邏輯：Butler-Volmer 電化學模型 ---
def simulate_pem(temp, press, j_max):
    # 簡單模擬參數
    T_kelvin = temp + 273.15
    j = np.linspace(0.01, j_max, 100)
    
    # 1. 可逆電壓 (Nernst)
    E_rev = 1.229 - 0.0009 * (temp - 25)
    
    # 2. 活化過電位 (Activation Overpotential - Butler-Volmer 簡化版)
    alpha = 0.5
    R = 8.314
    F = 96485
    n = 2
    i0 = 1e-3 * np.exp(0.01 * (temp - 25)) # 交換電流密度隨溫度變化
    eta_act = (R * T_kelvin / (alpha * n * F)) * np.arcsinh(j / (2 * i0))
    
    # 3. 歐姆過電位 (Ohmic Overpotential)
    R_ohm = 0.15 - 0.001 * (temp - 25) # 模擬膜電阻隨溫度下降
    eta_ohm = j * R_ohm
    
    # 總電壓
    V = E_rev + eta_act + eta_ohm
    
    return pd.DataFrame({'Current Density (A/cm²)': j, 'Voltage (V)': V})

# --- 執行模擬 ---
df_sim = simulate_pem(temperature, pressure, current_density_max)

# --- 數據展示 UI ---
st.divider()

# 第一列：KPI 卡片
c1, c2, c3, c4 = st.columns(4)
latest_v = df_sim['Voltage (V)'].iloc[-1]
c1.metric("當前設定溫度", f"{temperature} °C")
c2.metric("預測最高電壓", f"{latest_v:.3f} V")
c3.metric("電阻係數 (估算)", f"{0.15 - 0.001 * (temperature - 25):.3f} Ω·cm²")
c4.metric("系統狀態", "穩定運行", delta="Normal")

# 第二列：視覺化圖表
st.subheader("📈 極化曲線 (Polarization Curve)")
st.line_chart(df_sim.set_index('Current Density (A/cm²)'))

# 第三列：原始數據與導出
with st.expander("查看原始模擬數據表"):
    st.dataframe(df_sim, use_container_width=True)
    csv = df_sim.to_csv(index=False).encode('utf-8')
    st.download_button("下載模擬數據 (CSV)", csv, "pem_simulation.csv", "text/csv")

st.caption("TAD-AGE Agent 系統自動生成 - 基於 Viskovatov 與 Butler-Volmer 模型建置")