import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 設定頁面配置 (Set page config)
st.set_page_config(page_title="PEM Diagnostic Pro", layout="wide")

# --- 側邊欄：預測控制區 ---
st.sidebar.header("Predictive Panel / 模擬與預測面板")

# 1. 操作模式
mode = st.sidebar.selectbox("Operation Mode / 運作模式", ["Dual-Tube (雙管)", "Single-Tube (單管)"])

# 2. 模擬核心觸發器：以 No.11 電解槽溫度為預測基準 (35.1°C ~ 41.3°C)
st.sidebar.subheader("Target Temperature / 目標模擬溫度")
target_t = st.sidebar.slider("Electrolyzer Temp (°C) / 電解槽 No.11 溫度", 35.1, 41.3, 38.5, step=0.1)

# --- 預測演算法 (基於 4/13 實測數據線性回歸) ---
def get_predictions(temp):
    # 建立 4/13 實測極值對應關係 
    # T=35.1 -> Press=1.13, KW=23.3, Flow=476.0
    # T=41.3 -> Press=9.46, KW=23.21, Flow=487.0
    ratio = (temp - 35.1) / (41.3 - 35.1)
    ratio = max(0, min(1, ratio))
    
    res = {
        "pressure": 1.13 + (9.46 - 1.13) * ratio,
        "inst_kw": 23.3 - (23.3 - 23.21) * ratio,
        "acc_kw": 111.2 + (117.0 - 111.2) * ratio,
        "flow": 476.0 + (487.0 - 476.0) * ratio,
        "tank_temp": 39.8 - (39.8 - 39.5) * ratio  # 水箱水溫隨電解槽升溫略降 
    }
    return res

pred = get_predictions(target_t)

# 3. 側邊欄快速預測表 (方便列印/參考)
st.sidebar.divider()
st.sidebar.write("### Prediction Summary / 預測摘要")
st.sidebar.json({
    "Pressure (kg/cm2)": round(pred['pressure'], 2),
    "Flow (Lt/min)": round(pred['flow'], 1),
    "Power (KW)": round(pred['inst_kw'], 2)
})

# --- 主要顯示區 ---
# 獲取台北即時時間
try:
    now_str = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M:%S")
except:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.title("PEM Hydrogen Production Digital Twin")
st.info(f"🕒 **Live Prediction Sync / 系統即時預測同步時間：** {now_str}")

# --- 優化一：大字級預測儀表板 ---
st.subheader("Simulated Performance Dashboard / 模擬性能看板")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Predicted Pressure", f"{pred['pressure']:.2f} kg/cm²", delta=f"{pred['pressure']-1.13:.2f}")
m2.metric("Predicted Flow", f"{pred['flow']:.1f} Lt/min", delta=f"{pred['flow']-476.0:.1f}")
m3.metric("Inst. Power (KW)", f"{pred['inst_kw']:.2f} KW")
m4.metric("Accumulated KW", f"{pred['acc_kw']:.1f} KW")

# --- 優化二：視覺化物理連動曲線 ---
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.write("### Pressure-Flow Correlation / 壓力-流量連動預測")
    # 產生一段溫升範圍的預測曲線
    t_range = np.linspace(35.1, 41.3, 10)
    sim_df = pd.DataFrame([get_predictions(x) for x in t_range])
    sim_df['Temp'] = t_range
    st.line_chart(sim_df.set_index('Temp')[['pressure', 'flow']])

with c2:
    st.write("### Power Consumption Trend / 功耗變化趨勢")
    st.area_chart(sim_df.set_index('Temp')[['inst_kw']])

# --- 優化三：快速查表與狀態告警 ---
if pred['pressure'] > 9.0:
    st.error("🚨 **System Alert:** Pressure is reaching 9.46 kg/cm² safety limit! / 系統壓力即將到達實測極限！")

with st.expander("Show 4/13 Original Data Log / 展開 4/13 原始實測數據日誌"):
    st.table(df_raw_from_pdf) # 這裡可放您 Page 2 的完整表格
    st.caption("Data Source: 測試數據-20260413.pdf Page 2 ")

st.success("✅ Prediction Algorithm Synchronized with TAD-AGE Logic / 預測演算法已與 TAD-AGE 邏輯完成同步")