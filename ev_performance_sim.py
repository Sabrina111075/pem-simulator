# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面基礎配置
st.set_page_config(page_title="EV Performance Sim", layout="wide", page_icon="🛵")

# 時間定義
tw_now = datetime.utcnow() + timedelta(hours=8)

# 2. 側邊欄：動力參數設定 (專注於電動機車)
st.sidebar.title("⚙️ Vehicle Config / 車輛配置")
bike_mass = st.sidebar.slider("Total Mass / 總重量 (kg)", 100, 400, 180, help="包含騎士與車重")
motor_eff = st.sidebar.slider("Motor Efficiency / 馬達效率 (%)", 70, 100, 92)
max_torque = st.sidebar.slider("Max Torque / 最大扭矩 (Nm)", 20, 100, 45)

st.sidebar.markdown("---")
st.sidebar.header("🕹️ Real-time Control")
throttle = st.sidebar.slider("Throttle / 油門開度 (%)", 0, 100, 100)

# 3. 主畫面標題
st.title("⚡ Electric Motorcycle Performance Simulator")
st.caption(f"TAD-AGE Propulsion Lab | Local Time: {tw_now.strftime('%H:%M:%S')}")
st.markdown("---")

# 4. 物理模型計算 (加速與扭矩曲線)
speed_kmh = np.linspace(0.1, 100, 100)
# 扭矩特性：低速恆扭矩，高速恆功率
current_torque = max_torque * (throttle / 100) * (motor_eff / 100)
torque_curve = [current_torque if v < 45 else current_torque * (45/v) for v in speed_kmh]

# 加速度計算 (F=ma, F=Torque/Radius)
wheel_radius = 0.28 # 假設 12 吋胎
accel = [(t / wheel_radius / bike_mass) for t in torque_curve]

# 5. 繪圖區 (左右對照)
col1, col2 = st.columns(2)

with col1:
    fig_t, ax_t = plt.subplots(dpi=120)
    fig_t.patch.set_facecolor('#0e1117')
    ax_t.set_facecolor('#111111')
    ax_t.plot(speed_kmh, torque_curve, color='#00d4ff', linewidth=3)
    ax_t.set_title("Torque vs Speed (Nm)", color='#00d4ff', weight='bold')
    ax_t.tick_params(colors='white')
    ax_t.grid(True, color='#333', alpha=0.5)
    st.pyplot(fig_t)

with col2:
    fig_a, ax_a = plt.subplots(dpi=120)
    fig_a.patch.set_facecolor('#0e1117')
    ax_a.set_facecolor('#111111')
    ax_a.plot(speed_kmh, accel, color='#ff4b4b', linewidth=3)
    ax_a.set_title("Acceleration Trend (m/s²)", color='#ff4b4b', weight='bold')
    ax_a.tick_params(colors='white')
    ax_a.grid(True, color='#333', alpha=0.5)
    st.pyplot(fig_a)

# 6. 下方性能摘要
st.markdown("### 📊 Performance Summary / 性能摘要")
m1, m2, m3 = st.columns(3)

m1.metric("Top Acceleration", f"{round(max(accel), 2)} m/s²")
m2.metric("Estimated 0-50 km/h", f"{round(50/3.6/max(accel), 2)} sec", delta="Estimated")
m3.metric("Current Power Output", f"{round(current_torque * 45 / 9.548 / 1000, 2)} kW")