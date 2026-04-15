import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 設定頁面配置 (Set Page Config)
st.set_page_config(page_title="PEM Digital Twin Pro", layout="wide")

# --- 側邊欄：預測與模擬控制 (Sidebar) ---
st.sidebar.header("Digital Twin Control / 數位孿生控制")

# 1. 模式切換
mode = st.sidebar.selectbox("Test Scenario / 測試情境", ["Dual-Tube (雙管實測)", "Single-Tube (單管實測)"])

# 2. 核心模擬器：溫度驅動預測 (Core Simulator)
st.sidebar.subheader("Simulation Trigger / 模擬觸發器")
# 根據 4/13 數據表 Page 2 的 No.11 溫度範圍
sim_t11 = st.sidebar.slider("Electrolyzer Temp (°C) / 電解槽溫度 No.11", 35.1, 41.3, 38.5, step=0.1)

# --- 物理連動演算法 (Physics-Linked Algorithm) ---
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

# 3. 側邊欄預測數值摘要
st.sidebar.divider()
st.sidebar.success(f"""
**Predictive Results / 預測數值:**
* ⚡ 瞬時功率 (Power): `{sim_kw:.2f} KW`
* 🔋 累積功耗 (Acc. Energy): `{sim_acc:.1f} KW`
* 🎈 出口壓力 (Pressure): `{sim_press:.2f} kg/cm²`
* 🌊 出口流量 (Flow): `{sim_flow:.1f} Lt/min`
""")

# --- 主要內容區 (Main Display) ---
try:
    tz = pytz.timezone('Asia/Taipei')
    now_str = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
except:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.title("PEM Hydrogen Production Digital Twin")
st.info(f"🕒 **System Live Sync / 系統即時同步時間：** {now_str}")

# --- 中英文並行看板 (Bilingual Dashboard) ---
st.subheader("Real-time Predictive Dashboard / 即時模擬預測看板")
c1, c2, c3, c4 = st.columns(4)

c1.metric(label="Predicted Pressure / 預測出口壓力", value=f"{sim_press:.2f} kg/cm²", delta=f"{sim_press-1.13:.2f}")
c2.metric(label="Predicted Flow / 預測出口流量", value=f"{sim_flow:.1f} Lt/min", delta=f"{sim_flow-476.0:.1f}")
c3.metric(label="Instant Power / 電表瞬時功率", value=f"{sim_kw:.2f} KW")
c4.metric(label="Accumulated Energy / 電表累積功耗", value=f"{sim_acc:.1f} KW")

# --- 視覺化分析圖表 (Visual Charts) ---
st.divider()
col_a, col_b = st.columns(2)

# 準備圖表數據
t_range = np.linspace(35.1, 41.3, 30)
curve_data = [get_simulated_metrics(x) for x in t_range]
df_curve = pd.DataFrame(curve_data, columns=['KW', 'AccKW', 'Pressure', 'Flow'], index=t_range)
df_curve.index.name = 'Temperature (°C)'

with col_a:
    st.write("### Pressure & Flow Trend / 壓力與流量趨勢預測")
    # 顯示壓力與流量的趨勢
    st.line_chart(df_curve[['Pressure', 'Flow']])

with col_b:
    st.write("### Power Characteristics (KW) / 功耗特性模擬")
    # 修正：改用 line_chart 避免藍色方塊，呈現精細的 KW 變化
    st.line_chart(df_curve[['KW']])

# --- 原始數據對照表 (Reference Table) ---
with st.expander("Reference Data Table (4/13 Page 2) / 查看原始實測數據參考表"):
    ref_df = pd.DataFrame({
        "Temp No.11 (°C)": [35.1, 37.1, 38.5, 39.4, 40.0, 41.1, 41.3],
        "Power (KW)": [23.3, 23.1, 23.2, 23.2, 23.2, 23.2, 23.21],
        "Acc. Power (KW)": [111.2, 111.8, 112.5, 113.8, 114.3, 116.1, 117.0],
        "Pressure (kg/cm²)": [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
        "Flow (Lt/min)": [476.0, 402.7, 393.3, 399.7, 396.4, 408.8, 487.0]
    })
    st.dataframe(ref_df, use_container_width=True)

if sim_press > 9.0:
    st.warning("🚨 [High Pressure Alert / 高壓警告] System reaching 9.46 kg/cm² test limit.")

st.caption("Algorithm: Linear Interpolation | Based on 2026-04-13 Test Data")