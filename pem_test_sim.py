import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 設定頁面配置
st.set_page_config(page_title="PEM Diagnostic Pro", layout="wide")

# --- 側邊欄：預測控制區 ---
st.sidebar.header("Simulation Control Panel / 模擬與預測面板")

# 1. 操作模式
mode = st.sidebar.selectbox("Operation Mode / 運作模式", ["Dual-Tube (雙管)", "Single-Tube (單管)"])

# 2. 核心模擬觸發器 (基於實測數據範圍 35.1°C ~ 41.3°C)
st.sidebar.subheader("Simulate Target Temp / 目標模擬溫度")
target_t = st.sidebar.slider("Electrolyzer Temp (°C) / 電解槽 No.11 溫度", 35.1, 41.3, 38.5, step=0.1)

# --- 數據模型：基於 4/13 實測數據 ---
raw_ref_data = {
    "No.": [1, 2, 3, 4, 5, 6, 7],
    "Temp_No11": [35.1, 37.1, 38.5, 39.4, 40.0, 41.1, 41.3],
    "Pressure_kg_cm2": [1.13, 2.01, 2.92, 3.98, 4.92, 7.88, 9.46],
    "Power_KW": [23.3, 23.1, 23.2, 23.2, 23.1, 23.1, 23.21],
    "Acc_KW": [111.2, 111.8, 113.1, 114.3, 115.1, 116.2, 117.0],
    "Flow_Lt_min": [476.0, 402.7, 393.5, 399.2, 396.8, 408.3, 487.0]
}
df_raw = pd.DataFrame(raw_ref_data)

# 預測演算法 (線性插值)
def get_predictions(temp):
    # 使用 numpy 的插值功能來獲得更精確的模擬
    xp = df_raw["Temp_No11"]
    res = {
        "pressure": np.interp(temp, xp, df_raw["Pressure_kg_cm2"]),
        "inst_kw": np.interp(temp, xp, df_raw["Power_KW"]),
        "acc_kw": np.interp(temp, xp, df_raw["Acc_KW"]),
        "flow": np.interp(temp, xp, df_raw["Flow_Lt_min"])
    }
    return res

pred = get_predictions(target_t)

# 3. 側邊欄快速查看表格
st.sidebar.divider()
st.sidebar.write("### Test Log Ref / 實測數據參考")
st.sidebar.dataframe(df_raw, hide_index=True)

# --- 主要顯示區 ---
# 獲取台北即時時間
try:
    tz = pytz.timezone('Asia/Taipei')
    now_str = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
except:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.title("PEM Hydrogen Production Digital Twin / PEM 產氫數位孿生模擬")
st.info(f"🕒 **Live Prediction Sync / 系統即時預測時間：** {now_str}")

# --- 優化一：大字級預測儀表板 ---
st.subheader("Real-time Prediction / 即時預測看板")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Predicted Pressure", f"{pred['pressure']:.2f} kg/cm²", delta=f"{pred['pressure']-1.13:.2f}")
m2.metric("Predicted Flow", f"{pred['flow']:.1f} Lt/min", delta=f"{pred['flow']-476.0:.1f}")
m3.metric("Inst. Power (KW)", f"{pred['inst_kw']:.2f} KW")
m4.metric("Accumulated KW", f"{pred['acc_kw']:.1f} KW")

# --- 優化二：視覺化物理連動曲線 ---
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.write("### Temp vs Pressure / 溫度-壓力連動預測")
    t_axis = np.linspace(35.1, 41.3, 20)
    press_curve = [get_predictions(x)['pressure'] for x in t_axis]
    st.line_chart(pd.DataFrame({"Pressure": press_curve}, index=t_axis))

with c2:
    st.write("### Temp vs Flow / 溫度-流量連動預測")
    flow_curve = [get_predictions(x)['flow'] for x in t_axis]
    st.line_chart(pd.DataFrame({"Flow": flow_curve}, index=t_axis))

# --- 警告邏輯 ---
if pred['pressure'] > 9.0:
    st.error("🚨 **System Alert:** Pressure is reaching 9.46 kg/cm² safety limit! / 系統壓力即將到達實測極限！")
elif pred['flow'] < 400:
    st.warning("⚠️ **Notice:** Low flow detected at mid-temperature range. / 注意：中溫區間流量略有下降。")

st.success("✅ Prediction Algorithm Ready / 預測演算法運行正常")