import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 設定頁面配置
st.set_page_config(page_title="PEM Digital Twin Pro", layout="wide")

# --- 側邊欄優化 (Sidebar Optimization) ---
st.sidebar.header("Digital Twin Control / 數位孿生控制")

# 1. 模擬進度/負荷控制 (替代原本的溫度滑桿，更符合工業操作直覺)
st.sidebar.subheader("Simulation Scaling / 模擬負荷控制")
load_percent = st.sidebar.slider("System Load (%) / 系統負荷百分比", 0, 100, 50)

# 將負荷百分比映射回 4/13 的實測數據範圍 (35.1°C ~ 41.3°C)
sim_t11 = 35.1 + (load_percent / 100) * (41.3 - 35.1)

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

# 2. 新增：預測數據快速下載功能
st.sidebar.divider()
st.sidebar.subheader("Data Export / 數據導出")
t_range_all = np.linspace(35.1, 41.3, 50)
export_data = [get_simulated_metrics(x) for x in t_range_all]
df_export = pd.DataFrame(export_data, columns=['Power(KW)', 'Acc_Energy(KW)', 'Pressure(kg/cm2)', 'Flow(Lt/min)'])
st.sidebar.download_button(
    label="Download Predicted Data (CSV)",
    data=df_export.to_csv().encode('utf-8'),
    file_name='pem_predicted_data.csv',
    mime='text/csv',
)

# --- 主要內容區 ---
try:
    tz = pytz.timezone('Asia/Taipei')
    now_str = datetime.now(tz).strftime("%H:%M:%S")
    full_date = datetime.now(tz).strftime("%Y-%m-%d")
except:
    now_str = datetime.now().strftime("%H:%M:%S")
    full_date = datetime.now().strftime("%Y-%m-%d")

st.title("PEM Hydrogen Production Digital Twin")

# --- Dashboard 修改：第一欄改為系統同步時間，修正累積功耗顯示 ---
st.subheader("Real-time Predictive Dashboard / 即時模擬預測看板")
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    label="Sync Time / 系統同步時間", 
    value=now_str, 
    delta=full_date,
    delta_color="off"
)
c2.metric(
    label="Predicted Pressure / \n 預測出口壓力", 
    value=f"{sim_press:.2f} kg/cm²",
    delta=f"{sim_press-1.13:.2f}"
)
c3.metric(
    label="Predicted Flow / \n 預測出口流量", 
    value=f"{sim_flow:.1f} Lt/min",
    delta=f"{sim_flow-476.0:.1f}"
)
# 使用換行符號 \n 並縮短標籤長度確保不吃字
c4.metric(
    label="Accumulated Energy / \n 電表累積功耗", 
    value=f"{sim_acc:.1f} KW",
    help="Total accumulated power consumption in KW (電表數值累積功耗)"
)

# --- 視覺化圖表 ---
st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.write(f"### Pressure & Flow Trend (Load: {load_percent}%)")
    t_range = np.linspace(35.1, 41.3, 30)
    curve_data = [get_simulated_metrics(x) for x in t_range]
    df_curve = pd.DataFrame(curve_data, columns=['KW', 'AccKW', 'Pressure', 'Flow'], index=t_range)
    st.line_chart(df_curve[['Pressure', 'Flow']])

with col_b:
    st.write("### Power Characteristics (KW)")
    st.area_chart(df_curve[['KW']])

# --- 數據表格 ---
with st.expander("Reference Data Table (4/13 Page 2)"):
    st.dataframe(df_export, use_container_width=True)

if sim_press > 9.0:
    st.warning("🚨 [High Pressure Alert] System reaching 9.46 kg/cm² test limit.")

st.caption(f"Status: Synchronized | Simulation Load: {load_percent}% | Framework: TAD-AGE Agent")