import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 1. 頁面基本配置
st.set_page_config(page_title="PEM Digital Twin Pro", layout="wide")

# 2. 自定義 CSS：強化視覺效果並解決標籤吃字問題
st.markdown("""
    <style>
    .metric-container {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-label {
        font-size: 15px;
        color: #475569;
        font-weight: 600;
        margin-bottom: 10px;
        min-height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.3;
    }
    .metric-value {
        font-size: 30px;
        color: #0f172a;
        font-weight: 700;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .metric-delta {
        font-size: 13px;
        color: #10b981;
        margin-top: 8px;
        font-weight: 500;
    }
    .time-banner {
        font-size: 18px;
        color: #3b82f6;
        margin-top: -12px;
        margin-bottom: 25px;
        font-weight: 600;
        border-left: 5px solid #3b82f6;
        padding-left: 15px;
        background-color: #eff6ff;
        padding-top: 10px;
        padding-bottom: 10px;
        border-radius: 0 8px 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 物理連動演算法 (基於 4/13 實測數據)
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

# 4. 側邊欄：控制面板
st.sidebar.header("Digital Twin Control / 數位孿生控制")

# 左側：電解槽溫度滑桿
st.sidebar.subheader("Simulation Trigger / 模擬觸發器")
sim_t11 = st.sidebar.slider(
    "Electrolyzer Temp (°C) / 電解槽溫度 No.11", 
    35.1, 41.3, 38.5, step=0.1
)

# 同步顯示計算出的負荷百分比
load_p = (sim_t11 - 35.1) / (41.3 - 35.1) * 100
st.sidebar.metric("System Load / 系統負荷百分比", f"{load_p:.1f} %")

st.sidebar.divider()
st.sidebar.subheader("Data Export / 數據管理")
t_range_all = np.linspace(35.1, 41.3, 50)
full_sim_data = [get_simulated_metrics(x) for x in t_range_all]
df_export = pd.DataFrame(full_sim_data, columns=['Power(KW)', 'Acc_Energy(KW)', 'Pressure(kg/cm2)', 'Flow(Lt/min)'])
st.sidebar.download_button("Export Simulation (CSV)", df_export.to_csv().encode('utf-8'), "pem_simulation.csv", "text/csv")

# 5. 主要內容區
sim_kw, sim_acc, sim_press, sim_flow = get_simulated_metrics(sim_t11)

# 獲取台北即時時間
try:
    tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tz)
except:
    now = datetime.now()

time_str = now.strftime("%H:%M:%S")
date_str = now.strftime("%Y-%m-%d")

st.title("PEM Hydrogen Production Digital Twin")

# 6. Dashboard 標題與即時時間 (右側主要顯示區)
st.subheader("Real-time Predictive Dashboard / 即時模擬預測看板")
st.markdown(f'<div class="time-banner">🕒 System Sync Time / 系統同步時間：{date_str} {time_str}</div>', unsafe_allow_html=True)

# 看板指標列
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Predicted Pressure / <br>預測出口壓力</div>
        <div class="metric-value">{sim_press:.2f} <small style="font-size:14px;">kg/cm²</small></div>
        <div class="metric-delta">Δ {sim_press-1.13:.2f} vs Base</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Predicted Flow / <br>預測出口流量</div>
        <div class="metric-value">{sim_flow:.1f} <small style="font-size:14px;">Lt/min</small></div>
        <div class="metric-delta">Δ {sim_flow-476.0:.1f} vs Base</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Instant Power / <br>電表瞬時功率</div>
        <div class="metric-value">{sim_kw:.2f} <small style="font-size:14px;">KW</small></div>
        <div class="metric-delta">Status: Synchronized</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""<div class="metric-container">
        <div class="metric-label">Accumulated Energy / <br>電表累積功耗</div>
        <div class="metric-value">{sim_acc:.1f} <small style="font-size:14px;">KW</small></div>
        <div class="metric-delta">System Load: {load_p:.1f} %</div>
    </div>""", unsafe_allow_html=True)

# 7. 視覺化圖表
st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.write(f"### Pressure & Flow Trend / 壓力與流量趨勢預測")
    df_curve = pd.DataFrame(full_sim_data, columns=['KW', 'AccKW', 'Pressure', 'Flow'], index=t_range_all)
    st.line_chart(df_curve[['Pressure', 'Flow']])

with col_b:
    st.write("### Power Characteristics (KW) / 功耗特性模擬")
    st.line_chart(df_curve[['KW']])

# 8. 原始數據表格
with st.expander("Reference Data Table (4/13 Page 2)"):
    st.dataframe(pd.DataFrame({
        "Temp No.11": [35.1, 37.1, 38.5, 39.4, 40.0, 41.1, 41.3],
        "Power (KW)": [23.3, 23.1, 23.2, 23.2, 23.2, 23.2, 23.21],
        "Pressure (kg/cm²)": [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
        "Flow (Lt/min)": [476.0, 402.7, 393.3, 399.7, 396.4, 408.8, 487.0]
    }), use_container_width=True)

if sim_press > 9.0:
    st.warning("🚨 [High Pressure Alert] System reaching safety limit!")

st.caption(f"Status: Active Synchronized | Framework: TAD-AGE Agent")