# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE Propulsion Pro", layout="wide", page_icon="⚙️")
tw_now = datetime.utcnow() + timedelta(hours=8)

# --- [CSS 視覺強化] ---
st.markdown("""
    <style>
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    label[data-testid="stMetricLabel"] { font-size: 14px !important; color: #8b949e !important; text-transform: uppercase; }
    div[data-testid="stMetricValue"] { font-size: 30px !important; color: #58a6ff !important; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. 側邊欄 (維持 V4.3 設置)
st.sidebar.title("🚀 Control Center")
throttle = st.sidebar.select_slider("⚡ Throttle / 油門度 (%)", options=[0, 20, 40, 60, 80, 100], value=100)

with st.sidebar.expander("🚲 Vehicle Specs", expanded=True):
    bike_mass = st.sidebar.slider("Total Mass (kg)", 100, 500, 180)
    wheel_radius = st.sidebar.slider("Wheel Radius (m)", 0.2, 0.4, 0.28)
with st.sidebar.expander("🔋 Power System", expanded=True):
    max_torque = st.sidebar.slider("Motor Torque (Nm)", 20, 150, 60)
    motor_eff = st.sidebar.slider("Motor Eff. (%)", 70, 100, 92)
    batt_voltage = st.sidebar.slider("System Voltage (V)", 48, 96, 72)
with st.sidebar.expander("🔄 Regeneration", expanded=True):
    regen_on = st.sidebar.toggle("Enable Regen", value=True)
    regen_strength = st.sidebar.slider("Regen Strength (%)", 0, 100, 30)
with st.sidebar.expander("⚙️ Drivetrain", expanded=False):
    gear_ratio = st.sidebar.slider("Gear Ratio", 1.0, 15.0, 7.5)
    transmission_loss = st.sidebar.slider("Trans. Loss (%)", 0, 15, 6)
with st.sidebar.expander("🌍 Environment & Grade", expanded=True):
    slope_deg = st.sidebar.slider("Road Slope (%)", -15.0, 15.0, 2.41)
    cd_factor = st.sidebar.slider("Air Drag (Cd)", 0.1, 1.2, 0.45)
    rolling_res = st.sidebar.slider("Rolling Resistance", 0.01, 0.05, 0.01)

# --- 物理核心計算 ---
speed_kmh = np.linspace(0.1, 110, 100)
speed_ms = speed_kmh / 3.6
theta = np.arctan(slope_deg / 100)
total_efficiency = (motor_eff / 100) * (1 - transmission_loss / 100)

# 阻力項
gravity_force = bike_mass * 9.8 * np.sin(theta)
rolling_force = bike_mass * 9.8 * np.cos(theta) * rolling_res
air_drag = 0.5 * 1.225 * (speed_ms**2) * cd_factor * 0.6
total_resistance = air_drag + rolling_force + gravity_force

# 輸出項
base_speed = 40 * (batt_voltage / 72)
wheel_torque_peak = max_torque * gear_ratio * (throttle / 100) * total_efficiency
torque_curve = [wheel_torque_peak if v < base_speed else wheel_torque_peak * (base_speed/v) for v in speed_kmh]
accel = [( (t / wheel_radius) - r ) / bike_mass for t, r in zip(torque_curve, total_resistance)]

# 系統狀態邏輯
if slope_deg > 0:
    sys_status = "Climbing"
    status_color = "normal"
elif slope_deg < 0:
    sys_status = "Descending"
    status_color = "inverse"
else:
    sys_status = "Flat Road"
    status_color = "off"

# 3. 主畫面標題
st.title("⚡ Electric Motorcycle Propulsion Simulator")
st.caption(f"TAD-AGE Engine V4.4 | {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# 4. 圖表呈現區
col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    st.markdown("### 🟦 Torque vs Resistance / 扭矩與阻力")
    fig_t, ax_t = plt.subplots(dpi=130); fig_t.patch.set_facecolor('#0e1117'); ax_t.set_facecolor('#111111')
    ax_t.plot(speed_kmh, torque_curve, color='#00d4ff', label='Wheel Torque (Nm)', linewidth=4)
    ax_t.axhline(y=gravity_force + rolling_force, color='#ffaa00', linestyle='--', label='Static Resistance (N)')
    ax_t.set_xlabel("Speed (km/h)", color='gray'); ax_t.tick_params(colors='white'); ax_t.legend(); st.pyplot(fig_t)

with col_chart2:
    st.markdown("### 🟥 Acceleration Curve / 加速度曲線")
    fig_a, ax_a = plt.subplots(dpi=130); fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
    ax_a.plot(speed_kmh, accel, color='#ff4b4b', linewidth=4)
    ax_a.axhline(y=0, color='white', linestyle='-', alpha=0.5)
    ax_a.set_xlabel("Speed (km/h)", color='gray'); ax_a.tick_params(colors='white'); st.pyplot(fig_a)

st.markdown("---")

# 5. 強化診斷指標 (Metrics) - 補回坡度阻力與系統狀態
potential_regen = abs(gravity_force * speed_ms.mean()) * (regen_strength / 100) if (regen_on and slope_deg < 0) else 0

row1_1, row1_2, row1_3 = st.columns(3)
row1_1.metric("Max Accel / 最大加速", f"{round(max(accel), 2)} m/s²")
row1_2.metric("Grade Force / 坡度阻力", f"{round(gravity_force, 1)} N", delta=f"{slope_deg}%", delta_color=status_color)
row1_3.metric("Regen Power / 回充功率", f"{round(potential_regen/1000, 2)} kW")

row2_1, row2_2, row2_3 = st.columns(3)
row2_1.metric("System Eff. / 綜合效率", f"{round(total_efficiency*100, 1)} %")
row2_2.metric("Throttle / 油門狀態", f"{throttle}%")
row2_3.metric("System Status / 系統狀態", sys_status)