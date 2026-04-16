import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

# 1. 頁面基本配置 (Set Page Config)
st.set_page_config(page_title="PEM Digital Twin Pro", layout="wide")

# 2. 自定義 CSS：強化看板視覺、解決標籤吃字與對齊問題
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

# 3. 核心物理演算法 (基於 4/13 實測數據建模)
def get_simulated_metrics(t_input, mode):
    # 原始實測數據點 (以電解槽 No.11 溫度為變量)
    ref_points = {
        'temp': [35.1, 37.1, 38.5, 39.4, 40.0, 41.1, 41.3],
        'press': [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
        'flow': [476.0, 402.7, 393.3, 399.7, 396.4, 408.8, 487.0],
        'kw': [23.3, 23.1, 23.2, 23.2, 23.2, 23.2, 23.21],
        'acc_kw': [111.2, 111.8, 112.5, 113.8, 114.3, 116.1, 117.0]
    }
    
    # 進行線性插值計算
    p_press = np.interp(t_input, ref_points['temp'], ref_points['press'])
    p_flow = np.interp(t_input, ref_points['temp'], ref_points['flow'])
    p_kw = np.interp(t_input, ref_points['temp'], ref_points['kw'])
    p_acc = np.interp(t_input, ref_points['temp'], ref_points['acc_kw'])
    
    # 預測總產氫量 (H2 Yield) 計算邏輯
    # 單管平均耗時約 103s/kg, 雙管效率較高約 98s/kg
    base_eff = 103.0 if "Single" in mode else 98.0
    p_yield = (p_acc - 110.0) / (base_eff / 3600 * 23.1)
    
    # 雙管模式下的物理增量修正
    if "Dual" in mode:
        p_flow = p_flow * 1.85
        p_press = p_press * 1.05
        
    return p_kw, p_acc, p_press, p_flow, p_yield

# 4. 側邊控制面板 (Sidebar)
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
    "Electrolyzer Temp (°C) / 電解槽溫度(溫度 ℃)", 
    35.1, 41.3, 37.8, step=0.1
)

# 負荷百分比
load_p = (sim_t11 - 35.1) / (41.3 - 35.1) * 100
st.sidebar.metric("System Load / 系統負荷百分比", f"{load_p:.1f} %")

st.sidebar.divider()
st.sidebar.subheader("Data Export / 數據管理")

# --- 強化版 CSV 匯出邏輯：加入模擬時間與溫度 ---
tz = pytz.timezone('Asia/Taipei')
base_time = datetime.now(tz)
t_range_all = np.linspace(35.1, 41.3, 50) # 模擬 50 個數據點

export_rows = []
for i, t_val in enumerate(t_range_all):
    kw, acc, press, flow, hyield = get_simulated_metrics(t_val, op_mode)
    # 模擬時間軸：每點間隔 10 秒
    sim_ts = (base_time + timedelta(seconds=i*10)).strftime("%H:%M:%S")
    
    export_rows.append({
        "Sim Time (模擬時間)": sim_ts,
        "Temp No.11 (溫度 ℃)": round(t_val, 2),
        "Mode (模式)": op_mode,
        "Pressure (kg/cm2)": round(press, 2),
        "Flow (Lt/min)": round(flow, 1),
        "Power (KW)": round(kw, 2),
        "Yield (kg)": round(hyield, 3)
    })

df_export = pd.DataFrame(export_rows)
st.sidebar.download_button(
    label="Export CSV Report",
    data=df_export.to_csv(index=False).encode('utf-8-sig'), # 解決 Excel 中文亂碼
    file_name=f"PEM_Report_{op_mode}_{base_time.strftime('%H%M')}.csv",
    mime="text/csv"
)

# 5. 主內容區計算與時間獲取
sim_kw, sim_acc, sim_press, sim_flow, sim_yield = get_simulated_metrics(sim_t11, op_mode)

time_str = base_time.strftime("%H:%M:%S")
date_str = base_time.strftime("%Y-%m-%d")

st.title("PEM Hydrogen Production Digital Twin")
st.subheader("Real-time Predictive Dashboard / 即時模擬預測看板")

# 時間顯示 Banner
st.markdown(f'<div class="time-banner">🕒 System Sync Time / 系統同步時間：{date_str} {time_str} ({op_mode})</div>', unsafe_allow_html=True)

# 6. Dashboard 看板 (5 欄配置)
c1, c2, c3, c4, c5 = st.columns(5)

metrics_list = [
    ("Predicted Pressure / <br>氫氣出口壓力", f"{sim_press:.2f}", "kg/cm²", f"Δ {sim_press-1.13:.2f} vs Base"),
    ("Predicted Flow / <br>氫氣出口流量", f"{sim_flow:.1f}", "Lt/min", f"Δ {sim_flow-476.0:.1f}"),
    ("Instant Power / <br>電表數值功率", f"{sim_kw:.2f}", "KW", "Status: Sync"),
    ("Accumulated Energy / <br>電表累積功耗", f"{sim_acc:.1f}", "KW", f"Load: {load_p:.1f}%"),
    ("Total H2 Yield / <br>預測總產氫量", f"{sim_yield:.2f}", "kg", "Ref: 4/13 Log")
]

for i, col in enumerate([c1, c2, c3, c4, c5]):
    label, val, unit, delta = metrics_list[i]
    with col:
        st.markdown(f"""<div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val} <small style="font-size:14px;">{unit}</small></div>
            <div class="metric-delta">{delta}</div>
        </div>""", unsafe_allow_html=True)

# 7. 視覺化圖表 (修正：使用 Line Chart 取代 Area Chart)
st.divider()
col_left, col_right = st.columns(2)

t_axis = np.linspace(35.1, 41.3, 30)
sim_data_plot = [get_simulated_metrics(t, op_mode) for t in t_axis]
df_plot = pd.DataFrame(sim_data_plot, columns=['KW', 'Acc', 'Press', 'Flow', 'Yield'], index=t_axis)

with col_left:
    st.write("### Pressure & Yield Correlation / 壓力與產量趨勢")
    st.line_chart(df_plot[['Press', 'Yield']])

with col_right:
    st.write("### Power Characteristic (KW) / 功耗特性曲線")
    # 已改為折線圖，呈現清晰變動趨勢
    st.line_chart(df_plot['KW'])

st.caption("Status: Active | TAD-AGE Agent Framework | Source: 4/13 Hydrogen Production Test Record")