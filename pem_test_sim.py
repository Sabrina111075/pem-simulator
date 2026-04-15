import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 設定頁面配置
st.set_page_config(page_title="PEM Digital Twin Pro", layout="wide")

# --- 側邊欄：預測與模擬控制 ---
st.sidebar.header("Digital Twin Control / 數位孿生控制")

# 1. 模式切換
mode = st.sidebar.selectbox("Test Scenario / 測試情境", ["Dual-Tube (雙管實測)", "Single-Tube (單管實測)"])

# 2. 核心模擬器
st.sidebar.subheader("Simulation Trigger / 模擬觸發器")
sim_t11 = st.sidebar.slider("Electrolyzer Temp (°C) / 電解槽溫度 No.11", 35.1, 41.3, 38.5, step=0.1)

# --- 物理連動演算法 ---
def get_simulated_metrics(t_input):
    ref_points = {
        'temp': [35.1, 37.1, 38.5, 39.4, 40.0, 41.1, 41.3],
        'kw': [23.3, 23.1, 23.2, 23.2, 23.2, 23.2, 23.21],
        'acc_kw': [111.2, 111.8, 112.5, 113.8, 114.3, 116.1, 117.0],
        'press': [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
        'flow': [476.0, 402.7, 393.3, 399.7, 396.4, 408.8, 487.0]
    }
    p_kw = np.interp(t_input, ref_points['temp'], ref_points['kw'])
    p_acc = np.interp(t_input, ref_points['temp'], ref_points['acc_kw'])
    p_press = np.interp(t_input, ref_points['temp'], ref_points['press'])
    p_flow = np.interp(t_input, ref_points['temp'], ref_points['flow'])
    return p_kw, p_acc, p_press, p_flow

sim_kw, sim_acc, sim_press, sim_flow = get_simulated_metrics(sim_t11)

# 3. 側邊欄預測結果 (優化排版避免吃字)
st.sidebar.divider()
with st.sidebar.container():
    st.write("### Predicted Results / 預測數值")
    st.write(f"⚡ **Power / 瞬時功率:** `{sim_kw:.2f} KW`")
    st.write(f"🔋 **Energy / 累積功耗:** `{sim_acc:.1f} KW`")
    st.write(f"🎈 **Pressure / 出口壓力:** `{sim_press:.2f} kg/cm²`")
    st.write(f"🌊 **Flow / 出口流量:** `{sim_flow:.1f} Lt/min`")

# --- 主要內容區 ---
try:
    tz = pytz.timezone('Asia/Taipei')
    now_str = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
except:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.title("PEM Hydrogen Production Digital Twin")

# 修正後的藍色資訊塊 (使用 Markdown 讓顯示更清晰)
st.info(f"""
#### 🕒 System Live Sync / 系統即時同步
- **Target Location / 目標位置:** PEM Electrolyzer System
- **Current Sync Time / 同步時間:** `{now_str}`
""")

# --- Dashboard 優化：改為 2x2 佈局避免文字擠壓 ---
st.subheader("Predictive Dashboard / 即時模擬預測看板")

# 第一列
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.metric(
        label="Predicted Pressure / 預測出口壓力 (kg/cm²)", 
        value=f"{sim_press:.2f}", 
        delta=f"{sim_press-1.13:.2f} (vs Initial)",
        help="Target pressure based on No.11 Temp"
    )
with row1_col2:
    st.metric(
        label="Predicted Flow / 預測出口流量 (Lt/min)", 
        value=f"{sim_flow:.1f}", 
        delta=f"{sim_flow-476.0:.1f} (vs Initial)",
        help="Target flow based on No.11 Temp"
    )

# 第二列
row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.metric(
        label="Instant Power / 電表瞬時功率 (KW)", 
        value=f"{sim_kw:.2f}", 
        help="Total power value at current state"
    )
with row2_col2:
    st.metric(
        label="Accumulated Energy / 電表累積功耗 (KW)", 
        value=f"{sim_acc:.1f}", 
        help="Total accumulated consumption"
    )

# --- 視覺化分析圖表 ---
st.divider()
col_a, col_b = st.columns(2)
with col_a:
    st.write("### Pressure & Flow Forecast / 壓力與流量趨勢")
    t_range = np.linspace(35.1, 41.3, 30)
    curve_data = [get_simulated_metrics(x) for x in t_range]
    df_curve = pd.DataFrame(curve_data, columns=['KW', 'AccKW', 'Pressure', 'Flow'], index=t_range)
    st.line_chart(df_curve[['Pressure', 'Flow']])

with col_b:
    st.write("### Power Characteristics / 功耗特性模擬")
    st.area_chart(df_curve[['KW']])

# --- 原始數據對照表 ---
with st.expander("Reference Data Table (4/13) / 查看原始實測數據參考"):
    st.dataframe(pd.DataFrame({
        "Temp No.11 (°C)": [35.1, 37.1, 38.5, 39.4, 40.0, 41.1, 41.3],
        "Power (KW)": [23.3, 23.1, 23.2, 23.2, 23.2, 23.2, 23.21],
        "Pressure (kg/cm²)": [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
        "Flow (Lt/min)": [476.0, 402.7, 393.3, 399.7, 396.4, 408.8, 487.0]
    }), use_container_width=True)

if sim_press > 9.0:
    st.warning("🚨 [High Pressure Alert] System reaching 9.46 kg/cm² test limit.")

st.caption("Algorithm: Linear Interpolation | Framework: TAD-AGE Agent")