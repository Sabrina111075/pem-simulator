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
    1.0, 2.0, 1.0, 
    help="1.0 = Healthy (健康), >1.2 = Degradation (效能降解)"
)

# 4. 顯示目前系統時間 (System Time)
try:
    taipei_tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(taipei_tz).strftime("%Y-%m-%d %H:%M:%S")
except:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.sidebar.info(f"System Time / 系統時間 (Taipei):\n{now}")

# --- 主要內容區 (Main Display) ---
st.title("PEM Hydrogen Production Digital Twin / PEM 產氫數位孿生模擬")
st.write(f"**Baseline Data Reference:** 2026-04-13 Testing Log")

# 模擬計算邏輯 (Simulation Logic based on 4/13 data)
# 數據特徵：單管 ~108s/kg, 雙管初期 ~95s/kg, 雙管末期 ~174s/kg
time_steps = np.arange(0, 1020, 20)

def run_simulation(steps, mode_str, aging):
    kg_list = []
    temp_list = []
    press_list = []
    current_kg = 0
    
    for t in steps:
        # 效率模擬 (Efficiency Logic)
        if "Single" in mode_str:
            eff = 108.4 * aging
        else:
            # 模擬 4/13 數據中的異常：產量接近 9kg 後效率大幅下降
            eff = (95.0 if current_kg < 9.0 else 174.0) * aging
        
        # 計算此步產量
        step_prod = 20 / eff
        current_kg += step_prod
        
        # 溫度與壓力隨時間演進 (Temp & Pressure trends)
        sim_temp = base_temp + (t / 1000) * 7.4  # 模擬 33.7 -> 41.1 的升溫
        sim_press = 1.13 + (t / 1000) * (target_pressure - 1.13)
        
        kg_list.append(current_kg)
        temp_list.append(sim_temp)
        press_list.append(sim_press)
    
    return kg_list, temp_list, press_list

prod_data, temp_data, press_data = run_simulation(time_steps, mode, aging_factor)

# --- 數據圖表呈現 (Visualizations) ---
c1, c2 = st.columns(2)

with c1:
    st.write("### Accumulated Hydrogen (kg) / 累積產氫量")
    chart_prod = pd.DataFrame({"Time(s)": time_steps, "Production(kg)": prod_data})
    st.line_chart(chart_prod.set_index("Time(s)"))

with c2:
    st.write("### Temperature & Pressure / 溫度與壓力趨勢")
    chart_env = pd.DataFrame({
        "Time(s)": time_steps, 
        "Temp(°C)": temp_data, 
        "Pressure(kg/cm²)": press_data
    })
    st.line_chart(chart_env.set_index("Time(s)"))

# --- 診斷指標 (Diagnostics) ---
st.divider()
st.write("### Real-time Performance Indicators / 即時效能指標")

m1, m2, m3 = st.columns(3)
final_kg = prod_data[-1]
avg_eff = 1000 / final_kg if final_kg > 0 else 0

m1.metric("Final Production / 最終產量", f"{final_kg:.2f} kg")
m2.metric("Avg Efficiency / 平均效率", f"{avg_eff:.1f} s/kg")
m3.metric("Peak Pressure / 峰值壓力", f"{max(press_data):.2f} kg/cm²")

# 狀態警告邏輯 (Status Alerts)
if "Dual" in mode and final_kg > 9.0:
    st.warning("⚠️ [Alert] High Latency Stage 10 Detected / 偵測到第十階段高耗時異常 (174s/kg)")

if aging_factor > 1.2:
    st.error("🚨 [System] Membrane Degradation Detected / 設備健康告警：膜老化效能下降")
else:
    st.success("✅ [Status] System Operating Normally / 系統運行狀態正常")

st.caption("Developed for PEM Diagnosis | 基於 TAD-AGE 框架開發")