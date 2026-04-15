import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 1. 頁面基本配置
st.set_page_config(page_title="PEM Digital Twin Pro", layout="wide")

# 2. 自定義 CSS：優化卡片佈局與字體
st.markdown("""
    <style>
    .metric-container {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-label {
        font-size: 14px;
        color: #475569;
        font-weight: 600;
        margin-bottom: 8px;
        min-height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.2;
    }
    .metric-value {
        font-size: 28px;
        color: #0f172a;
        font-weight: 700;
    }
    .metric-delta {
        font-size: 12px;
        color: #10b981;
        margin-top: 5px;
        font-weight: 500;
    }
    .time-banner {
        font-size: 16px;
        color: #3b82f6;
        margin-top: -10px;
        margin-bottom: 20px;
        font-weight: 600;
        border-left: 5px solid #3b82f6;
        padding: 8px 15px;
        background-color: #eff6ff;
        border-radius: 0 8px 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 物理連動演算法 (根據 4/13 實測數據優化)
def get_simulated_metrics(t_input, mode):
    # 原始實測數據點 (No.11 溫度)
    ref_points = {
        'temp': [35.1, 37.1, 38.5, 39.4, 40.0, 40.5, 41.0, 41.1, 41.2, 41.3],
        'press': [1.13, 2.01, 2.92, 3.98, 4.92, 5.96, 6.92, 7.88, 8.64, 9.46],
        'flow': [476.0, 402.7, 393.0, 399.1, 396.2, 393.8, 439.4, 408.1, 454.3, 487.0],
        'kw': [23.3, 23.1, 23.1, 23.1, 23.1, 23.1, 23.1, 23.18, 23.19, 23.21],
        'acc_kw': [111.2, 111.8, 112.3, 113.0, 113.7, 114.4, 115.1, 115.8, 116.4, 117.0]
    }
    
    p_press = np.interp(t_input, ref_points['temp'], ref_points['press'])
    p_flow = np.interp(t_input, ref_points['temp'], ref_points['flow'])
    p_kw = np.interp(t_input, ref_points['temp'], ref_points['kw'])
    p_acc = np.interp(t_input, ref_points['temp'], ref_points['acc_kw'])
    
    # 預測總產氫量 (H2 Yield) 邏輯
    # 單管平均耗時約 103s/kg，雙管平均約 98s/kg
    base_sec_per_kg = 103.0 if "Single" in mode else 98.0
    # 模擬產量：利用累積功耗與效率比推算 (簡化建模)
    p_yield = (p_acc - 110.0) / (base_sec_per_kg / 3600 * 23.1) 
    
    if "Dual" in mode:
        p_flow = p_flow * 1.85
        p_press = p_press * 1.05
        
    return p_kw, p_acc, p_press, p_flow, p_yield

# 4. 側邊欄：控制面板
st.sidebar.header("Digital Twin Control / 數位孿生控制")

op_mode = st.sidebar.selectbox(
    "Operation Mode / 操作模式",
    ["Single-Tube (單管製氫)", "Dual-Tube (雙管製氫)"]
)

st.sidebar.divider()

st.sidebar.subheader("Simulation Trigger / 模擬觸發器")
sim_t11 = st.sidebar.slider(
    "Electrolyzer Temp (°C) / 電解槽溫度 No.11", 
    35.1, 41.3, 37.8, step=0.1
)

load_p = (sim_t11 - 35.1) / (41.3 - 35.1) * 100
st.sidebar.metric("System Load / 系統負荷百分比", f"{load_p:.1f} %")

st.sidebar.divider()
st.sidebar.subheader("Data Export / 數據管理")
if st.sidebar.button("Generate Report (CSV)"):
    st.sidebar.success("Report Ready for Download")

# 5. 主要內容區計算
sim_kw, sim_acc, sim_press, sim_flow, sim_yield = get_simulated_metrics(sim_t11, op_mode)

# 台北即時時間
tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tz)
time_str = now.strftime("%H:%M:%S")
date_str = now.strftime("%Y-%m-%d")

st.title("PEM Hydrogen Production Digital Twin")
st.subheader("Real-time Predictive Dashboard / 即時模擬預測看板")
st.markdown(f'<div class="time-banner">🕒 System Sync Time / 系統同步時間：{date_str} {time_str} ({op_mode})</div>', unsafe_allow_html=True)

# 6. 看板指標列 (增加到 5 欄)
cols = st.columns(5)

metrics = [
    ("Predicted Pressure / <br>預測出口壓力", f"{sim_press:.2f}", "kg/cm²", f"Δ {sim_press-1.13:.2f} vs Base"),
    ("Predicted Flow / <br>預測出口流量", f"{sim_flow:.1f}", "Lt/min", f"Δ {sim_flow-476.0:.1f}"),
    ("Instant Power / <br>電表瞬時功率", f"{sim_kw:.2f}", "KW", "Status: Stable"),
    ("Accumulated Energy / <br>電表累積功耗", f"{sim_acc:.1f}", "KW", f"Load: {load_p:.1f}%"),
    ("Total H2 Yield / <br>預測總產氫量", f"{sim_yield:.2f}", "kg", "Based on 4/13 Log")
]

for i, (label, val, unit, delta) in enumerate(metrics):
    with cols[i]:
        st.markdown(f"""<div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val} <small style="font-size:14px;">{unit}</small></div>
            <div class="metric-delta">{delta}</div>
        </div>""", unsafe_allow_html=True)

# 7. 趨勢圖表
st.divider()
c_left, c_right = st.columns(2)
t_range = np.linspace(35.1, 41.3, 20)
plot_data = [get_simulated_metrics(t, op_mode) for t in t_range]
df_plot = pd.DataFrame(plot_data, columns=['KW', 'Acc', 'Press', 'Flow', 'Yield'], index=t_range)

with c_left:
    st.write("### Pressure & Yield Trend / 壓力與產量連動預測")
    st.line_chart(df_plot[['Press', 'Yield']])

with c_right:
    st.write("### Flow Characteristic / 出口流量特性曲線")
    st.area_chart(df_plot['Flow'])

st.caption(f"TAD-AGE Agent Framework | Data Source: 2026-04-13 Test Log")