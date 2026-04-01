# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面配置與精準時間 (UTC+8)
st.set_page_config(page_title="TAD-AGE Energy Lab", layout="wide", page_icon="⚡")
tw_now = datetime.utcnow() + timedelta(hours=8)

# 2. 側邊欄：新增「地形」與「回充」控制
st.sidebar.title("🚀 Control Center / 控制中心")

with st.sidebar.expander("🌍 Environment & Grade / 環境與坡度", expanded=True):
    slope_deg = st.sidebar.slider("Road Slope / 行駛坡度 (%)", -15.0, 15.0, 0.0) # 支援下坡負值
    rolling_res = st.sidebar.slider("Rolling / 滾動阻力", 0.01, 0.05, 0.015)

with st.sidebar.expander("🔄 Regeneration / 動能回收系統", expanded=True):
    regen_on = st.sidebar.toggle("Enable Regen / 啟動回充", value=True)
    regen_strength = st.sidebar.slider("Regen Strength / 回充強度 (%)", 0, 100, 30)

with st.sidebar.expander("🔋 Power System / 動力配置", expanded=False):
    bike_mass = st.sidebar.slider("Total Mass / 總重量 (kg)", 100, 500, 180)
    max_torque = st.sidebar.slider("Motor Torque / 馬達扭矩 (Nm)", 20, 150, 60)
    batt_voltage = st.sidebar.slider("System Voltage / 系統電壓 (V)", 48, 96, 72)
    gear_ratio = st.sidebar.slider("Gear Ratio / 齒輪比", 1.0, 15.0, 7.5)

# 3. 進階物理模型計算
speed_kmh = np.linspace(0.1, 110, 100)
speed_ms = speed_kmh / 3.6
theta = np.arctan(slope_deg / 100) # 將坡度百分比轉為弧度

# 阻力計算：包含重力分量 (坡度影響)
gravity_force = bike_mass * 9.8 * np.sin(theta) 
rolling_force = bike_mass * 9.8 * np.cos(theta) * rolling_res
air_drag = 0.5 * 1.225 * (speed_ms**2) * 0.45 * 0.6
total_resistance = air_drag + rolling_force + gravity_force

# 扭矩與回充邏輯
base_speed = 40 * (batt_voltage / 72)
wheel_torque = max_torque * gear_ratio * 0.9 # 固定 90% 綜合效率
torque_curve = [wheel_torque if v < base_speed else wheel_torque * (base_speed/v) for v in speed_kmh]

# 計算淨加速度
accel = [( (t / 0.28) - r ) / bike_mass for t, r in zip(torque_curve, total_resistance)]

# 計算回充功率 (當阻力為負或需要減速時)
# 下坡且啟動回充時，將重力分量轉化為電能
potential_regen = 0
if regen_on and slope_deg < 0:
    potential_regen = abs(gravity_force * speed_ms.mean()) * (regen_strength / 100)

# 4. 主畫面 UI
st.title("⚡ Electric Motorcycle Propulsion Simulator")
st.subheader("電動機車動力模擬系統 - 高階能耗版")
st.caption(f"TAD-AGE Engine V3.8 | {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")

# 5. 數據看板：加入坡度警告與回充提示
m1, m2, m3, m4 = st.columns(4)
current_accel = max(accel)
net_power = (max(torque_curve) / gear_ratio * 4000 / 9550)

m1.metric("Current Accel / 即時加速", f"{round(current_accel, 2)} m/s²")
m2.metric("Grade Resistance / 坡度阻力", f"{round(gravity_force, 1)} N", 
          delta="Climbing" if slope_deg > 0 else "Downhill", delta_color="inverse")
m3.metric("Regen Power / 回充功率", f"{round(potential_regen/1000, 2)} kW" if potential_regen > 0 else "0 kW")
m4.metric("System Status / 系統狀態", "Charging" if potential_regen > 0 else "Discharging")

# 6. 圖表呈現
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🟦 Torque vs Resistance / 扭矩與阻力對照")
    fig_t, ax_t = plt.subplots(dpi=130)
    fig_t.patch.set_facecolor('#0e1117'); ax_t.set_facecolor('#111111')
    ax_t.plot(speed_kmh, torque_curve, color='#00d4ff', label='Motor Torque', linewidth=3)
    ax_t.axhline(y=gravity_force + rolling_force, color='#ffaa00', linestyle='--', label='Base Resistance')
    ax_t.set_xlabel("Speed (km/h)", color='gray'); ax_t.tick_params(colors='white')
    ax_t.legend(); ax_t.grid(True, color='#333', alpha=0.3)
    st.pyplot(fig_t)

with col2:
    st.markdown("### 🟥 Dynamic Accel / 動態加速度曲線")
    fig_a, ax_a = plt.subplots(dpi=130)
    fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
    ax_a.plot(speed_kmh, accel, color='#ff4b4b', linewidth=4)
    ax_a.axhline(y=0, color='white', linestyle='-', alpha=0.5) # 零加速度線
    ax_a.set_xlabel("Speed (km/h)", color='gray'); ax_a.tick_params(colors='white')
    ax_a.grid(True, color='#333', alpha=0.3)
    st.pyplot(fig_a)