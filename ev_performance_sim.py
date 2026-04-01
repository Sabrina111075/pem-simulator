# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面配置與時間 (UTC+8)
st.set_page_config(page_title="TAD-AGE Propulsion Pro", layout="wide", page_icon="⚙️")
tw_now = datetime.utcnow() + timedelta(hours=8)

# --- [視覺強化核心：自定義 CSS] ---
st.markdown("""
    <style>
    /* 強化 Metric 卡片容器 */
    div[data-testid="stMetric"] {
        background-color: #161b22; /* 深灰藍背景 */
        border: 1px solid #30363d; /* 細緻邊框 */
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    /* 標籤字體：更清晰的灰白色 */
    label[data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #8b949e !important;
        text-transform: uppercase; /* 小標大寫化提升專業感 */
    }
    /* 數值字體：鮮艷的電感藍與加粗 */
    div[data-testid="stMetricValue"] {
        font-size: 38px !important;
        font-weight: 800 !important;
        color: #58a6ff !important; /* 精準專業藍 */
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    /* 狀態字體特定強化 (例如 Climbing/Descending) */
    [data-testid="stMetric"] span {
        font-family: 'Courier New', Courier, monospace; /* 狀態文字使用等寬字型增加工程味 */
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 側邊欄 (維持全功能)
st.sidebar.title("🚀 Control Center / 控制中心")
with st.sidebar.expander("🚲 Vehicle Specs / 車輛規格", expanded=True):
    bike_mass = st.sidebar.slider("Total Mass / 總重量 (kg)", 100, 500, 180)
    wheel_radius = st.sidebar.slider("Wheel Radius / 輪胎半徑 (m)", 0.2, 0.4, 0.28)
with st.sidebar.expander("🔋 Power System / 動力配置", expanded=True):
    max_torque = st.sidebar.slider("Motor Torque / 馬達扭矩 (Nm)", 20, 150, 60)
    motor_eff = st.sidebar.slider("Motor Eff. / 馬達效率 (%)", 70, 100, 92)
    batt_voltage = st.sidebar.slider("System Voltage / 系統電壓 (V)", 48, 96, 72)
with st.sidebar.expander("⚙️ Drivetrain / 傳動損耗", expanded=True):
    gear_ratio = st.sidebar.slider("Gear Ratio / 齒輪比", 1.0, 15.0, 7.5)
    transmission_loss = st.sidebar.slider("Trans. Loss / 傳動損耗 (%)", 0, 15, 5)
with st.sidebar.expander("🌍 Environment & Grade / 地形環境", expanded=True):
    slope_deg = st.sidebar.slider("Road Slope / 行駛坡度 (%)", -15.0, 15.0, 0.0)
    cd_factor = st.sidebar.slider("Air Drag / 風阻係數 (Cd)", 0.1, 1.2, 0.45)
    rolling_res = st.sidebar.slider("Rolling / 滾動阻力", 0.01, 0.05, 0.015)

# 3. 物理計算 (維持 V4.0 邏輯)
speed_kmh = np.linspace(0.1, 110, 100)
speed_ms = speed_kmh / 3.6
theta = np.arctan(slope_deg / 100)
total_efficiency = (motor_eff / 100) * (1 - transmission_loss / 100)
gravity_force = bike_mass * 9.8 * np.sin(theta)
rolling_force = bike_mass * 9.8 * np.cos(theta) * rolling_res
air_drag = 0.5 * 1.225 * (speed_ms**2) * cd_factor * 0.6
total_resistance = air_drag + rolling_force + gravity_force
base_speed = 40 * (batt_voltage / 72)
wheel_torque_peak = max_torque * gear_ratio * total_efficiency
torque_curve = [wheel_torque_peak if v < base_speed else wheel_torque_peak * (base_speed/v) for v in speed_kmh]
accel = [( (t / wheel_radius) - r ) / bike_mass for t, r in zip(torque_curve, total_resistance)]

# 4. 主畫面呈現
st.title("⚡ Electric Motorcycle Propulsion Simulator")
st.subheader("電動機車動力模擬系統 - 工程全功能版")
st.caption(f"TAD-AGE Engine V4.0 | Analysis Time: {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# 5. [強化後的數據看板]
m1, m2, m3, m4 = st.columns(4)

# 根據狀態決定 Delta 顏色與文字
status_text = "Climbing" if slope_deg > 0 else ("Descending" if slope_deg < 0 else "Flat Road")
status_delta = f"{slope_deg}%"

m1.metric("Max Accel / 最大加速度", f"{round(max(accel), 2)} m/s²")
m2.metric("Grade Force / 坡度阻力", f"{round(gravity_force, 1)} N")
m3.metric("System Eff. / 綜合效率", f"{round(total_efficiency*100, 1)} %")
m4.metric("System Status / 系統狀態", status_text, delta=status_delta, delta_color="normal")

st.markdown("---")
# (下方繪圖部分維持不變...)