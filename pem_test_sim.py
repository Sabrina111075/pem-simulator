import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 設定頁面配置 (Set Page Config)
st.set_page_config(page_title="PEM Digital Twin Pro", layout="wide")

# 強制修正 Metric 標籤吃字的 CSS 樣式
st.markdown("""
    <style>
    [data-testid="stMetricLabel"] {
        white-space: normal;
        height: auto;
        min-height: 50px;
        line-height: 1.2;
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- 側邊欄：控制面板 (Sidebar) ---
st.sidebar.header("Digital Twin Control / 數位孿生控制")

# 1. 找回溫度滑桿，並結合負荷概念
st.sidebar.subheader("Simulation Trigger / 模擬觸發器")
sim_t11 = st.sidebar.slider("Electrolyzer Temp (°C) / 電解槽溫度 No.11", 35.1, 41.3, 38.5, step=0.1)

# 計算負荷百分比作為顯示參考
load_p = (sim_t11 - 35.1) / (41.3 - 35.1) * 100

# 2. 數據導出功能 (Data Export)
st.sidebar.divider()
st.sidebar.subheader("Data Export / 數據導出")

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

# 下載按鈕邏輯
t_range_all = np.linspace(35.1, 41.3, 50)
export_data = [get_simulated_metrics(x) for x in t_range_all]
df_export = pd.DataFrame(export_data, columns=['Power(KW)', 'Acc_Energy(KW)', 'Pressure(kg/cm2)', 'Flow(Lt/min)'])
st.sidebar.download_button(
    label="Download Predicted Data (CSV)",
    data=df_export.to_csv().encode('utf-8'),
    file_name='pem_predicted_data.csv',
    mime='text/csv',
)

# --- 主要內容區 (Main Display) ---
try:
    tz = pytz.timezone('Asia/Taipei')
    now_str = datetime.now(tz).strftime("%H:%M:%S")
    full_date = datetime.now(tz).strftime("%Y-%m-%d")
except:
    now_str = datetime.now().strftime("%H:%M:%S")
    full_date = datetime.now().strftime("%Y-%m-%d")

st.title("PEM Hydrogen Production Digital Twin")

# --- Dashboard: 第一欄為系統同步時間，修正吃字 ---
st.subheader("Real-time Predictive Dashboard / 即時模擬預測看板")
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    label="Sync Time / 系統同步時間", 
    value=now_str, 
    delta=f"Date: {full_date}",
    delta_color="off"
)
c2.metric(
    label="Predicted Pressure / 預測出口壓力", 
    value=f"{sim_press:.2f} kg/cm²", 
    delta=f"{sim_press-1.13:.2f} vs Init",
    help="氫氣出口壓力 (Pressure)"
)
c3.metric(
    label="Predicted Flow / 預測出口流量", 
    value=f"{sim_flow:.1f} Lt/min", 
    delta=f"{sim_flow-476.0:.1f} vs Init",
    help="氫氣出口流量 (Flow)"
)
c4.metric(
    label="Accumulated Energy / 電表累積功耗", 
    value=f"{sim_acc:.1f} KW",
    help="電表累積功耗 (Total Accumulated Power Consumption)"
)

# --- 視覺化圖表 (找回中英文並行標題與波形圖) ---
st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.write(f"### Pressure & Flow Trend / 壓力與流量趨勢預測")
    # 生成曲線數據
    t_range = np.linspace(35.1, 41.3, 30)
    curve_data = [get_simulated_metrics(x) for x in t_range]
    df_curve = pd.DataFrame(curve_data, columns=['KW', 'AccKW', 'Pressure', 'Flow'], index=t_range)
    # 畫出壓力與流量
    st.line_chart(df_curve[['Pressure', 'Flow']])

with col_b:
    st.write("### Power Characteristics (KW) / 功耗特性模擬")
    # 將功耗以波形線條圖呈現，而非單一色塊
    st.line_chart(df_curve[['KW']])

# --- 數據表格 ---
with st.expander("Reference Data Table (4/13 Page 2) / 原始數據參考表"):
    st.dataframe(df_export, use_container_width=True)

if sim_press > 9.0:
    st.warning("🚨 [High Pressure Alert] System reaching 9.46 kg/cm² test limit. / 高壓警報：系統接近實測壓力極限。")

st.caption(f"Status: Synchronized | Simulation Load: {load_p:.1f}% | Framework: TAD-AGE Agent")