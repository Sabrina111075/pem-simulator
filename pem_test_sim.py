import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 設定頁面配置 (Set Page Config)
st.set_page_config(page_title="PEM Digital Twin Pro", layout="wide")

# 自定義 CSS：強化看板視覺與解決吃字問題
st.markdown("""
    <style>
    .metric-container {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #ececf1;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .metric-label {
        font-size: 14px;
        color: #6b7280;
        font-weight: 600;
        margin-bottom: 10px;
        min-height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.3;
    }
    .metric-value {
        font-size: 32px;
        color: #111827;
        font-weight: 700;
        font-family: 'Courier New', Courier, monospace;
    }
    .metric-delta {
        font-size: 13px;
        color: #10b981;
        margin-top: 8px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 側邊欄：控制面板 (Sidebar) ---
st.sidebar.header("Digital Twin Control / 數位孿生控制")

# 1. 改良後的滑桿：同步顯示百分比與溫度
st.sidebar.subheader("System Load & Temp / 負荷與溫度控制")
# 以負荷百分比為主要操作邏輯
load_p = st.sidebar.slider("System Load (%) / 系統負荷百分比", 0.0, 100.0, 50.0, step=0.1)
# 自動換算回 No.11 溫度基準 (35.1 ~ 41.3)
sim_t11 = 35.1 + (load_p / 100) * (41.3 - 35.1)
st.sidebar.caption(f"Target Temp Reference: {sim_t11:.1f}°C")

# 2. 數據導出
st.sidebar.divider()
st.sidebar.subheader("Data Management / 數據管理")

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

# 下載按鈕數據準備
t_range_all = np.linspace(35.1, 41.3, 50)
curve_data_full = [get_simulated_metrics(x) for x in t_range_all]
df_export = pd.DataFrame(curve_data_full, columns=['Power(KW)', 'Acc_Energy(KW)', 'Pressure(kg/cm2)', 'Flow(Lt/min)'])
st.sidebar.download_button("Export Simulation (CSV)", df_export.to_csv().encode('utf-8'), "pem_sim.csv", "text/csv")

# --- 主要內容區 (Main Display) ---
# 獲取台北即時時間
try:
    tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
except:
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")

st.title("PEM Hydrogen Production Digital Twin")

# --- Dashboard: 儀表板 (第一欄為即時更新時間) ---
st.subheader("Real-time Predictive Dashboard / 即時模擬預測看板")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Sync Time / <br>系統同步時間</div>
        <div class="metric-value">{time_str}</div>
        <div class="metric-delta" style="color:#6b7280;">Date: {date_str}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Predicted Pressure / <br>預測出口壓力</div>
        <div class="metric-value">{sim_press:.2f} <small style="font-size:14px;">kg/cm²</small></div>
        <div class="metric-delta">Δ {sim_press-1.13:.2f} (from base)</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Predicted Flow / <br>預測出口流量</div>
        <div class="metric-value">{sim_flow:.1f} <small style="font-size:14px;">Lt/min</small></div>
        <div class="metric-delta">Δ {sim_flow-476.0:.1f} (from base)</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Accumulated Energy / <br>電表累積功耗</div>
        <div class="metric-value">{sim_acc:.1f} <small style="font-size:14px;">KW</small></div>
        <div class="metric-delta">Load Status: {load_p:.1f} %</div>
    </div>""", unsafe_allow_html=True)

# --- 視覺化圖表 ---
st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.write(f"### Pressure & Flow Trend / 壓力與流量趨勢預測")
    df_curve = pd.DataFrame(curve_data_full, columns=['KW', 'AccKW', 'Pressure', 'Flow'], index=t_range_all)
    st.line_chart(df_curve[['Pressure', 'Flow']])

with col_b:
    st.write("### Power Characteristics (KW) / 功耗特性模擬")
    st.line_chart(df_curve[['KW']])

# --- 原始數據對照 ---
with st.expander("Reference Data Table (4/13 Page 2) / 原始數據參考表"):
    st.dataframe(pd.DataFrame({
        "Temp No.11": [35.1, 37.1, 38.5, 39.4, 40.0, 41.1, 41.3],
        "Power(KW)": [23.3, 23.1, 23.2, 23.2, 23.2, 23.2, 23.21],
        "Pressure": [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
        "Flow": [476.0, 402.7, 393.3, 399.7, 396.4, 408.8, 487.0]
    }), use_container_width=True)

if sim_press > 9.0:
    st.warning("🚨 [High Pressure Alert] System reaching 9.46 kg/cm² safety limit!")

st.caption(f"Status: Active Synchronized | System Load: {load_p:.1f}% | TAD-AGE Agent Framework")