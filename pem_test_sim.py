import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 設定頁面配置
st.set_page_config(page_title="PEM Diagnostic Pro", layout="wide")

# --- 側邊欄：控制面板 ---
st.sidebar.header("Control Panel / 控制與預測面板")

# 1. 模式選擇
mode = st.sidebar.selectbox("Operation Mode / 運作模式", ["Dual-Tube (雙管)", "Single-Tube (單管)"])

# 2. 預測模擬觸發器 (基於 4/13 數據)
st.sidebar.subheader("Predictive Simulator / 預測模擬")
input_temp = st.sidebar.slider("Current Cell Temp (°C) / 當前電解槽溫度", 33.5, 42.0, 37.0, step=0.1)

# 根據 4/13 數據表進行線性回歸近似預測 (Linear Approximation)
# 溫度與各參數的對應關係 (以 No.11 槽位為基準)
# 33.5C -> 1.13kg/cm2, 23.3KW, 476 Lt/min
# 41.3C -> 9.46kg/cm2, 23.21KW, 487 Lt/min
def predict_metrics(temp):
    ratio = (temp - 33.5) / (41.3 - 33.5)
    ratio = max(0, min(1, ratio)) # 限制在 0-1 之間
    
    pred_pressure = 1.13 + (9.46 - 1.13) * ratio
    pred_kw = 23.3 - (23.3 - 23.21) * ratio # 隨溫度升高功耗微幅下降
    pred_flow = 476.0 + (487.0 - 476.0) * ratio
    pred_total_kw = 111.2 + (117.0 - 111.2) * ratio
    
    return pred_kw, pred_total_kw, pred_pressure, pred_flow

p_kw, p_total_kw, p_press, p_flow = predict_metrics(input_temp)

# 顯示預測結果於側邊欄
st.sidebar.info(f"""
**Predictive Results / 模擬預測結果:**
* 電表總值: `{p_kw:.2f} KW`
* 累積功耗: `{p_total_kw:.1f} KW`
* 出口壓力: `{p_press:.2f} kg/cm²`
* 出口流量: `{p_flow:.1f} Lt/min`
""")

# 3. 實測數據參考表 (4/13 原表)
with st.sidebar.expander("View Raw Test Data / 查看 4/13 實測數據"):
    raw_ref = {
        "Temp(°C)": [33.5, 35.1, 37.1, 39.4, 40.0, 41.1, 41.3],
        "Press(kg/cm2)": [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
        "Flow(Lt/min)": [476, 402, 393, 399, 396, 408, 487]
    }
    st.table(pd.DataFrame(raw_ref))

# --- 主要內容區 ---
try:
    tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
except:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.title("PEM Hydrogen Production Digital Twin")
st.markdown(f"**Current System Time / 系統即時時間：** `{now}`")

# 效能看板
st.subheader("Real-time Prediction Dashboard / 即時預測看板")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Predicted Pressure / 預測壓力", f"{p_press:.2f} kg/cm²")
k2.metric("Predicted Flow / 預測流量", f"{p_flow:.1f} Lt/min")
k3.metric("Inst. Power / 瞬時功耗", f"{p_kw:.2f} KW")
k4.metric("Accumulated / 累積功耗", f"{p_total_kw:.1f} KW")

# 圖表展示：模擬壓力與流量趨勢
st.divider()
t_axis = np.linspace(33.5, 42.0, 20)
press_curve = [predict_metrics(x)[2] for x in t_axis]
flow_curve = [predict_metrics(x)[3] for x in t_axis]

c1, c2 = st.columns(2)
with c1:
    st.write("### Temperature vs Pressure / 溫度-壓力曲線")
    st.line_chart(pd.DataFrame({"Pressure": press_curve}, index=t_axis))
with c2:
    st.write("### Temperature vs Flow / 溫度-流量曲線")
    st.line_chart(pd.DataFrame({"Flow": flow_curve}, index=t_axis))

if p_press > 8.0:
    st.warning("⚠️ High Pressure Warning: System nearing 9.46 kg/cm² limit. / 高壓警告：系統接近實測極限壓力。")

st.caption("Based on 4/13 Testing Log | Powered by TAD-AGE Framework")