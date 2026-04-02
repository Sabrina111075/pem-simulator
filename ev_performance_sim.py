# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面配置 / Page Config
st.set_page_config(page_title="TAD-AGE Propulsion Pro", layout="wide", page_icon="⚙️")
tw_now = datetime.utcnow() + timedelta(hours=8)

# --- [CSS 視覺強化] ---
st.markdown("""
    <style>
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    label[data-testid="stMetricLabel"] { font-size: 14px !important; color: #8b949e !important; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; color: #58a6ff !important; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. 側邊欄 / Sidebar (中英雙語)
st.sidebar.title("🚀 Control Center / 控制中心")

# 油門控制 / Throttle
throttle = st.sidebar.select_slider("⚡ Throttle / 油門度 (%)", options=[0, 20, 40, 60, 80, 100], value=100)

with st.sidebar.expander("🚲 Vehicle Specs / 車輛規格", expanded=True):
    bike_mass = st.sidebar.slider("Total Mass / 總重量 (kg)", 100, 500, 180)
    wheel_radius = st.sidebar.slider("Wheel Radius / 輪胎半徑 (m)", 0.2, 0.4, 0.28)

with st.sidebar.expander("🔋 Power System / 動力配置", expanded=True):
    max_torque = st.sidebar.slider("Motor Torque / 馬達扭矩 (Nm)", 20, 150, 60)
    motor_eff = st.sidebar.slider("Motor Eff. / 馬達效率 (%)", 70, 100, 92)
    batt_voltage = st.sidebar.slider("System Voltage / 系統電壓 (V)", 48, 96, 72)

with st.sidebar.expander("🔄 Regeneration / 動能回充系統", expanded=True):
    regen_on = st.sidebar.toggle("Enable Regen / 啟動回充", value=True)
    regen_strength = st.sidebar.slider("Regen Strength / 回充強度 (%)", 0, 100, 30)

with st.sidebar.expander("⚙️ Drivetrain / 傳動損耗", expanded=False):
    gear_ratio = st.sidebar.slider("Gear Ratio / 齒輪比", 1.0, 15.0, 7.5)
    transmission_loss = st.sidebar.slider("Trans. Loss / 傳動損耗 (%)", 0, 15, 6)

with st.sidebar.expander("🌍 Environment & Grade / 地形環境", expanded=True):
    slope_deg = st.sidebar.slider("Road Slope / 行駛坡度 (%)", -15.0, 15.0, 0.0)
    cd_factor = st.sidebar.slider("Air Drag / 風阻係數 (Cd)", 0.1, 1.2, 0.45)
    rolling_res = st.sidebar.slider("Rolling / 滾動阻力", 0.01, 0.05, 0.015)

# --- 物理核心計算 (Core Logic) ---
speed_kmh = np.linspace(0.1, 110, 100)
speed_ms = speed_kmh / 3.6
theta = np.arctan(slope_deg / 100)
total_efficiency = (motor_eff / 100) * (1 - transmission_loss / 100)
gravity_force = bike_mass * 9.8 * np.sin(theta)
rolling_force = bike_mass * 9.8 * np.cos(theta) * rolling_res
air_drag = 0.5 * 1.225 * (speed_ms**2) * cd_factor * 0.6
total_resistance = air_drag + rolling_force + gravity_force
base_speed = 40 * (batt_voltage / 72)
wheel_torque_peak = max_torque * gear_ratio * (throttle / 100) * total_efficiency
torque_curve = [wheel_torque_peak if v < base_speed else wheel_torque_peak * (base_speed/v) for v in speed_kmh]
accel = [( (t / wheel_radius) - r ) / bike_mass for t, r in zip(torque_curve, total_resistance)]

# 系統狀態 / System Status
if slope_deg > 0: sys_status = "Climbing / 上坡中"
elif slope_deg < 0: sys_status = "Descending / 下坡中"
else: sys_status = "Flat Road / 平路"

# 3. 主畫面 / Main Page
st.title("⚡ Electric Motorcycle Propulsion Simulator")
st.subheader("電動機車動力模擬系統 - 工程整合版")
st.caption(f"TAD-AGE Engine V5.0 | Analysis Time: {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# 4. 圖表呈現 / Plots
col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    st.markdown("### 🟦 Torque vs Resistance / 扭矩與阻力對照")
    fig_t, ax_t = plt.subplots(dpi=130); fig_t.patch.set_facecolor('#0e1117'); ax_t.set_facecolor('#111111')
    ax_t.plot(speed_kmh, torque_curve, color='#00d4ff', label='Wheel Torque / 輪軸扭矩', linewidth=4)
    ax_t.axhline(y=gravity_force + rolling_force, color='#ffaa00', linestyle='--', label='Resistance / 靜態阻力')
    ax_t.set_xlabel("Speed / 時速 (km/h)", color='gray'); ax_t.set_ylabel("Force / 力量 (N)", color='gray')
    ax_t.tick_params(colors='white'); ax_t.legend(); st.pyplot(fig_t)

with col_chart2:
    st.markdown("### 🟥 Dynamic Accel / 動態加速度曲線")
    fig_a, ax_a = plt.subplots(dpi=130); fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
    ax_a.plot(speed_kmh, accel, color='#ff4b4b', label='Acceleration / 加速度', linewidth=4)
    ax_a.axhline(y=0, color='white', linestyle='-', alpha=0.5)
    ax_a.set_xlabel("Speed / 時速 (km/h)", color='gray'); ax_a.set_ylabel("Accel / 加速度 (m/s²)", color='gray')
    ax_a.tick_params(colors='white'); st.pyplot(fig_a)

st.markdown("---")

# 5. 診斷指標 / Metrics
potential_regen = abs(gravity_force * speed_ms.mean()) * (regen_strength / 100) if (regen_on and slope_deg < 0) else 0

row1_1, row1_2, row1_3 = st.columns(3)
row1_1.metric("Max Accel / 最大加速", f"{round(max(accel), 2)} m/s²")
row1_2.metric("Grade Force / 坡度阻力", f"{round(gravity_force, 1)} N", delta=f"{slope_deg}%")
row1_3.metric("Regen Power / 回充功率", f"{round(potential_regen/1000, 2)} kW")

row2_1, row2_2, row2_3 = st.columns(3)
row2_1.metric("System Eff. / 綜合效率", f"{round(total_efficiency*100, 1)} %")
row2_2.metric("Throttle / 油門狀態", f"{throttle}%")
row2_3.metric("System Status / 系統狀態", sys_status)