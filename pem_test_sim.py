import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 設定頁面配置 (Set Page Config)
st.set_page_config(page_title="PEM Digital Twin Pro", layout="wide")

# 自定義 CSS：徹底解決標籤吃字與美化看板
st.markdown("""
    <style>
    .metric-container {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 16px;
        color: #64748b;
        font-weight: bold;
        margin-bottom: 8px;
        min-height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.2;
    }
    .metric-value {
        font-size: 28px;
        color: #1e293b;
        font-weight: 800;
    }
    .metric-delta {
        font-size: 14px;
        color: #3b82f6;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 側邊欄：控制面板 (Sidebar) ---
st.sidebar.header("Digital Twin Control / 數位孿生控制")

# 1. 恢復溫度滑桿 (No.11)
st.sidebar.subheader("Simulation Trigger / 模擬觸發器")
sim_t11 = st.sidebar.slider("Electrolyzer Temp (°C) / 電解槽溫度 No.11", 35.1, 41.3, 38.5, step=0.1)

# 計算負荷百分比作為顯示參考 (Calculation Load)
load_p = (sim_t11 - 35.1) / (41.3 - 35.1) * 100

# 2. 數據導出功能
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

# 生成導出數據
t_range_all = np.linspace(35.1, 41.3, 50)
curve_data_full = [get_simulated_metrics(x) for x in t_range_all]
df_export = pd.DataFrame(curve_data_full, columns=['Power(KW)', 'Acc_Energy(KW)', 'Pressure(kg/cm2)', 'Flow(Lt/min)'])
st.sidebar.download_button("Download Predicted Data (CSV)", df_export.to_csv().encode('utf-8'), "pem_data.csv", "text/csv")

# --- 主要內容區 (Main Display) ---
try:
    tz = pytz.timezone('Asia/Taipei')
    now_str = datetime.now(tz).strftime("%H:%M:%S")
    full_date = datetime.now(tz).strftime("%Y-%m-%d")
except:
    now_str = datetime.now().strftime("%H:%M:%S")
    full_date = datetime.now().strftime("%Y-%m-%d")

st.title("PEM Hydrogen Production Digital Twin")

# --- Dashboard: 自定義看板 (解決吃字並落實中英文並行) ---
st.subheader("Real-time Predictive Dashboard / 即時模擬預測看板")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Sync Time / <br>系統同步時間</div>
        <div class="metric-value">{now_str}</div>
        <div class="metric-delta">Date: {full_date}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Predicted Pressure / <br>預測出口壓力</div>
        <div class="metric-value">{sim_press:.2f} <small>kg/cm²</small></div>
        <div class="metric-delta">Δ {sim_press-1.13:.2f} vs Init</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Predicted Flow / <br>預測出口流量</div>
        <div class="metric-value">{sim_flow:.1f} <small>Lt/min</small></div>
        <div class="metric-delta">Δ {sim_flow-476.0:.1f} vs Init</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Accumulated Energy / <br>電表累積功耗</div>
        <div class="metric-value">{sim_acc:.1f} <small>KW</small></div>
        <div class="metric-delta">System Load: {load_p:.1f}%</div>
    </div>""", unsafe_allow_html=True)

# --- 視覺化圖表 (找回連續波形圖與中英文標題) ---
st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.write(f"### Pressure & Flow Trend / 壓力與流量趨勢預測")
    df_curve = pd.DataFrame(curve_data_full, columns=['KW', 'AccKW', 'Pressure', 'Flow'], index=t_range_all)
    st.line_chart(df_curve[['Pressure', 'Flow']])

with col_b:
    st.write("### Power Characteristics (KW) / 功耗特性模擬")
    # 確保顯示的是連續線條波形圖
    st.line_chart(df_curve[['KW']])

# --- 原始數據表格 ---
with st.expander("Reference Data Table (4/13 Page 2) / 原始數據參考表"):
    st.dataframe(ref_df := pd.DataFrame({
        "Temp No.11": [35.1, 37.1, 38.5, 39.4, 40.0, 41.1, 41.3],
        "Power(KW)": [23.3, 23.1, 23.2, 23.2, 23.2, 23.2, 23.21],
        "Pressure": [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
        "Flow": [476.0, 402.7, 393.3, 399.7, 396.4, 408.8, 487.0]
    }), use_container_width=True)

if sim_press > 9.0:
    st.warning("🚨 [High Pressure Alert] System reaching 9.46 kg/cm² test limit. / 高壓警報：系統接近實測壓力極限。")

st.caption(f"Status: Synchronized | Framework: TAD-AGE Agent")