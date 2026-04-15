import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# 設定頁面配置 (Set page config)
st.set_page_config(page_title="PEM Simulation System", layout="wide")

# --- 側邊欄設定 (Sidebar Controls) ---
st.sidebar.header("Simulation Control Panel / 模擬控制面板")

# 1. 產氫模式選擇 (Mode Selection)
mode = st.sidebar.selectbox(
    "Hydrogen Production Mode / 產氫模式",
    ["Dual-Tube (雙管制氫)", "Single-Tube (單管制氫)"]
)

# 2. 物理參數調整 (Physical Parameters)
st.sidebar.subheader("System Parameters / 系統參數")
base_temp = st.sidebar.slider("Ambient Temperature (°C) / 環境基準溫度", 25.0, 45.0, 33.7)
target_pressure = st.sidebar.slider("Target Back Pressure (kg/cm²) / 目標背壓", 1.0, 15.0, 9.46)

# 3. 設備健康診斷 (Health & Aging)
st.sidebar.subheader("Health Monitoring / 健康監控模擬")
aging_factor = st.sidebar.slider(
    "Membrane Aging Factor / 質子交換膜老化係數", 
    1.0, 2.0, 1.0
)

# 4. 側邊欄實測數據表格 (Test Data Reference Table)
st.sidebar.subheader("Test Data Ref / 實測數據參考")
raw_data = {
    "Stage/階段": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "Single (s/kg)": [95.0, 100.0, 102.7, 107.1, 103.8, 105.6, 108.4, None, None, None],
    "Dual (s/kg)": [95.0, 82.0, 95.0, 99.0, 107.0, 110.0, 109.0, 108.0, 85.0, 174.0]
}
df_raw = pd.DataFrame(raw_data)
st.sidebar.dataframe(df_raw, hide_index=True)
st.sidebar.caption("Source: 2026-04-13 Testing Log")

# --- 主要內容區 (Main Display) ---
# 獲取台北即時時間
try:
    taipei_tz = pytz.timezone('Asia/Taipei')
    now_str = datetime.now(taipei_tz).strftime("%Y-%m-%d %H:%M:%S")
except:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.title("PEM Hydrogen Production Digital Twin / PEM 產氫數位孿生模擬")
st.info(f"🕒 **Current System Time / 系統即時時間：** {now_str}")

# 模擬計算邏輯 (Simulation Logic)
time_steps = np.arange(0, 1020, 20)

def run_simulation(steps, mode_str, aging):
    kg_list, temp_list, press_list = [], [], []
    current_kg = 0
    for t in steps:
        if "Single" in mode_str:
            eff = 108.4 * aging
        else:
            # 模擬 4/13 雙管數據：產量超過 9kg 後效率降至 174s/kg
            eff = (95.0 if current_kg < 9.0 else 174.0) * aging
        
        step_prod = 20 / eff
        current_kg += step_prod
        sim_temp = base_temp + (t / 1000) * 7.4 
        sim_press = 1.13 + (t / 1000) * (target_pressure - 1.13)
        
        kg_list.append(current_kg)
        temp_list.append(sim_temp)
        press_list.append(sim_press)
    return kg_list, temp_list, press_list

prod_data, temp_data, press_data = run_simulation(time_steps, mode, aging_factor)

# --- 數據圖表呈現 ---
c1, c2 = st.columns(2)
with c1:
    st.write("### Accumulated Hydrogen (kg) / 累積產氫量")
    st.line_chart(pd.DataFrame({"Production(kg)": prod_data}, index=time_steps))

with c2:
    st.write("### Temperature & Pressure / 溫度與壓力趨勢")
    st.line_chart(pd.DataFrame({"Temp(°C)": temp_data, "Pressure(kg/cm²)": press_data}, index=time_steps))

# --- 效能指標與警告 ---
st.divider()
m1, m2, m3 = st.columns(3)
final_kg = prod_data[-1]
m1.metric("Final Production / 最終產量", f"{final_kg:.2f} kg")
m2.metric("Avg Efficiency / 平均效率", f"{1000/final_kg:.1f} s/kg" if final_kg > 0 else "0")
m3.metric("Peak Pressure / 峰值壓力", f"{max(press_data):.2f} kg/cm²")

if "Dual" in mode and final_kg > 9.0:
    st.warning("⚠️ [Alert] Abnormal Production Latency at Stage 10 (174s/kg) / 偵測到第十階段高耗時異常")

st.success("✅ System Initialized via TAD-AGE Framework / 系統已透過 TAD-AGE 框架完成初始化")