import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 設定頁面 (Set Page)
st.set_page_config(page_title="PEM Digital Twin Pro", layout="wide")

# --- 側邊欄：預測與模擬控制 (Sidebar) ---
st.sidebar.header("Digital Twin Control / 數位孿生控制")

# 1. 模式切換
mode = st.sidebar.selectbox("Test Scenario / 測試情境", ["Dual-Tube (雙管實測)", "Single-Tube (單管實測)"])

# 2. 核心模擬器：溫度驅動預測 (Core Simulator)
st.sidebar.subheader("Simulation Trigger / 模擬觸發器")
# 根據 4/13 數據，No.11 電解槽溫度是最穩定的參考點
sim_t11 = st.sidebar.slider("Electrolyzer Temp (°C) / 電解槽溫度 No.11", 35.1, 41.3, 38.5, step=0.1)

# --- 物理連動演算法 (Physics-Linked Algorithm) ---
# 基於 4/13 表格數據的線性內插法
def get_simulated_metrics(t_input):
    # 實測基準點 (T_No.11, 電錶KW, 累積KW, 壓力, 流量)
    ref_points = {
        'temp': [35.1, 37.1, 38.5, 39.4, 40.0, 41.1, 41.3],
        'kw': [23.3, 23.1, 23.2, 23.2, 23.2, 23.2, 23.21],
        'acc_kw': [111.2, 111.8, 112.5, 113.8, 114.3, 116.1, 117.0],
        'press': [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
        'flow': [476.0, 402.7, 393.3, 399.7, 396.4, 408.8, 487.0]
    }
    
    # 使用 numpy 進行線性內插預測
    p_kw = np.interp(t_input, ref_points['temp'], ref_points['kw'])
    p_acc = np.interp(t_input, ref_points['temp'], ref_points['acc_kw'])
    p_press = np.interp(t_input, ref_points['temp'], ref_points['press'])
    p_flow = np.interp(t_input, ref_points['temp'], ref_points['flow'])
    
    return p_kw, p_acc, p_press, p_flow

sim_kw, sim_acc, sim_press, sim_flow = get_simulated_metrics(sim_t11)

# 3. 側邊欄即時數值顯示
st.sidebar.divider()
st.sidebar.success(f"""
**Simulated Results / 預測數值:**
* ⚡ 瞬時功率: `{sim_kw:.2f} KW`
* 🔋 累積功耗: `{sim_acc:.1f} KW`
* 🎈 出口壓力: `{sim_press:.2f} kg/cm²`
* 🌊 出口流量: `{sim_flow:.1f} Lt/min`
""")

# --- 主要內容區 (Main Display) ---
try:
    now_str = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M:%S")
except:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.title("PEM Hydrogen Production Digital Twin")
st.info(f"🕒 **System Live Sync / 系統即時同步時間：** {now_str}")

# --- 儀表板區域 ---
st.subheader("Real-time Predictive Dashboard / 即時模擬預測看板")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Predicted Pressure", f"{sim_press:.2f} kg/cm²", help="氫氣出口壓力")
c2.metric("Predicted Flow", f"{sim_flow:.1f} Lt/min", help="氫氣出口流量")
c3.metric("Instant Power", f"{sim_kw:.2f} KW", help="電錶數值總值")
c4.metric("Accumulated Energy", f"{sim_acc:.1f} KW", help="電錶累積功耗")

# --- 視覺化圖表 ---
st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.write("### Pressure & Flow Forecast / 壓力與流量預測曲線")
    t_range = np.linspace(35.1, 41.3, 20)
    curve_data = [get_simulated_metrics(x) for x in t_range]
    df_curve = pd.DataFrame(curve_data, columns=['KW', 'AccKW', 'Pressure', 'Flow'], index=t_range)
    st.line_chart(df_curve[['Pressure', 'Flow']])

with col_b:
    st.write("### Energy Consumption Profile / 功耗特徵模擬")
    st.area_chart(df_curve[['KW']])

# --- 數據表格參考 ---
with st.expander("Reference Data Table / 原始實測數據參考 (4/13 Page 2)"):
    st.table(pd.DataFrame({
        "Temp(No.11)": [35.1, 37.1, 38.5, 39.4, 40.0, 41.1, 41.3],
        "KW": [23.3, 23.1, 23.2, 23.2, 23.2, 23.2, 23.21],
        "Pressure": [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
        "Flow": [476.0, 402.7, 393.3, 399.7, 396.4, 408.8, 487.0]
    }))

if sim_press > 9.0:
    st.warning("🚨 [High Pressure Alert] System reaching test limit of 9.46 kg/cm².")

st.caption("Algorithm: Linear Interpolation based on 2026-04-13 Test Data | TAD-AGE Framework")