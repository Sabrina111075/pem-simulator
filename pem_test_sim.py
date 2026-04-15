import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 1. 頁面基本配置
st.set_page_config(page_title="PEM Digital Twin Pro", layout="wide")

# 2. 自定義 CSS：強化視覺效果並解決標籤遮擋問題
st.markdown("""
    <style>
    .metric-container {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
    }
    .metric-label {
        font-size: 13px;
        color: #475569;
        font-weight: 600;
        margin-bottom: 8px;
        min-height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.2;
    }
    .metric-value {
        font-size: 24px;
        color: #0f172a;
        font-weight: 700;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .metric-delta {
        font-size: 11px;
        color: #10b981;
        margin-top: 5px;
        font-weight: 500;
    }
    .time-banner {
        font-size: 16px;
        color: #3b82f6;
        margin-top: -10px;
        margin-bottom: 25px;
        font-weight: 600;
        border-left: 5px solid #3b82f6;
        padding: 10px 15px;
        background-color: #eff6ff;
        border-radius: 0 8px 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 物理連動演算法 (根據 4/13 實測數據建模)
def get_simulated_metrics(t_input, mode):
    # 參考數據點：No.11 溫度對應之各項數值
    ref_points = {
        'temp': [35.1, 37.1, 38.5, 39.4, 40.0, 41.1, 41.3],
        'press': [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
        'flow': [476.0, 402.7, 393.3, 399.7, 396.4, 408.8, 487.0],
        'kw': [23.3, 23.1, 23.2, 23.2, 23.2, 23.2, 23.21],
        'acc_kw': [111.2, 111.8, 112.5, 113.8, 114.3, 116.1, 117.0]
    }
    
    # 進行線性插值
    p_press = np.interp(t_input, ref_points['temp'], ref_points['press'])
    p_flow = np.interp(t_input, ref_points['temp'], ref_points['flow'])
    p_kw = np.interp(t_input, ref_points['temp'], ref_points['kw'])
    p_acc = np.interp(t_input, ref_points['temp'], ref_points['acc_kw'])
    
    # 預測產氫量預估 (H2 Yield)
    # 根據實測：單管 103s/kg, 雙管 98s/kg
    efficiency = 103.0 if "Single" in mode else 98.0
    # 基礎產量推算公式
    p_yield = (p_acc - 110.0) / (efficiency / 3600 * 23.1)
    
    # 雙管模式下的物理增量修正
    if "Dual" in mode:
        p_flow = p_flow * 1.85
        p_press = p_press * 1.05
        
    return p_kw, p_acc, p_press, p_flow, p_yield

# 4. 側邊欄：控制面板
st.sidebar.header("Digital Twin Control / 數位孿生控制")

# 操作模式選擇
op_mode = st.sidebar.selectbox(
    "Operation Mode / 操作模式",
    ["Single-Tube (單管製氫)", "Dual-Tube (雙管製氫)"]
)

st.sidebar.divider()

# 模擬觸發：溫度滑桿
st.sidebar.subheader("Simulation Trigger / 模擬觸發器")
sim_t11 = st.sidebar.slider(
    "Electrolyzer Temp (°C) / 電解槽溫度 No.11", 
    35.1, 41.3, 37.8, step=0.1
)

# 系統負荷百分比
load_p = (sim_t11 - 35.1) / (41.3 - 35.1) * 100
st.sidebar.metric("System Load / 系統負荷百分比", f"{load_p:.1f} %")

st.sidebar.divider()
st.sidebar.subheader("Data Export / 數據管理")
t_range_all = np.linspace(35.1, 41.3, 50)
full_sim = [get_simulated_metrics(x, op_mode) for x in t_range_all]
df_export = pd.DataFrame(full_sim, columns=['Power(KW)', 'Acc_Energy(KW)', 'Pressure(kg/cm2)', 'Flow(Lt/min)', 'Yield(kg)'])
st.sidebar.download_button("Export CSV Report", df_export.to_csv().encode('utf-8'), f"pem_sim_{op_mode}.csv", "text/csv")

# 5. 主內容區：數據計算與時間獲取
sim_kw, sim_acc, sim_press, sim_flow, sim_yield = get_simulated_metrics(sim_t11, op_mode)

# 台北即時時間
try:
    tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tz)
except:
    now = datetime.now()

time_str = now.strftime("%H:%M:%S")
date_str = now.strftime("%Y-%m-%d")

st.title("PEM Hydrogen Production Digital Twin")
st.subheader("Real-time Predictive Dashboard / 即時模擬預測看板")

# 時間橫幅
st.markdown(f'<div class="time-banner">🕒 System Sync Time / 系統同步時間：{date_str} {time_str} ({op_mode})</div>', unsafe_allow_html=True)

# 6. Dashboard 看板 (5 欄配置)
c1, c2, c3, c4, c5 = st.columns(5)

config = [
    ("Predicted Pressure / <br>預測出口壓力", f"{sim_press:.2f}", "kg/cm²", f"Δ {sim_press-1.13:.2f} vs Base"),
    ("Predicted Flow / <br>預測出口流量", f"{sim_flow:.1f}", "Lt/min", f"Δ {sim_flow-476.0:.1f}"),
    ("Instant Power / <br>電表瞬時功率", f"{sim_kw:.2f}", "KW", "Status: Synchronized"),
    ("Accumulated Energy / <br>電表累積功耗", f"{sim_acc:.1f}", "KW", f"Load: {load_p:.1f}%"),
    ("Total H2 Yield / <br>預測總產氫量", f"{sim_yield:.2f}", "kg", "Ref: 4/13 Log")
]

for i, col in enumerate([c1, c2, c3, c4, c5]):
    label, val, unit, delta = config[i]
    with col:
        st.markdown(f"""<div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val} <small style="font-size:14px;">{unit}</small></div>
            <div class="metric-delta">{delta}</div>
        </div>""", unsafe_allow_html=True)

# 7. 趨勢圖表區 (修正：使用 Line Chart 取代 Area Chart 消除藍色色塊)
st.divider()
col_a, col_b = st.columns(2)

t_axis = np.linspace(35.1, 41.3, 30)
sim_data = [get_simulated_metrics(t, op_mode) for t in t_axis]
df_plot = pd.DataFrame(sim_data, columns=['KW', 'Acc', 'Press', 'Flow', 'Yield'], index=t_axis)

with col_a:
    st.write("### Pressure & Yield Correlation / 壓力與產產量趨勢")
    st.line_chart(df_plot[['Press', 'Yield']])

with col_b:
    st.write("### Power Characteristic (KW) / 功耗特性曲線")
    # 此處已改為 line_chart，呈現清晰的折線
    st.line_chart(df_plot['KW'])

st.caption("Status: Active | TAD-AGE Agent Framework | Source: 4/13 Hydrogen Production Test Record")