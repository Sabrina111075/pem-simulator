# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面基礎配置
st.set_page_config(page_title="EV Performance Sim", layout="wide", page_icon="🛵")

# 時間定義
tw_now = datetime.utcnow() + timedelta(hours=8)

# 2. 側邊欄：動力參數設定
st.sidebar.title("⚙️ Vehicle Config / 參數設定")
bike_mass = st.sidebar.slider("Total Mass / 總重量 (kg)", 100, 500, 180)
motor_eff = st.sidebar.slider("Motor Efficiency / 馬達效率 (%)", 70, 100, 92)
max_torque = st.sidebar.slider("Max Torque / 最大扭矩 (Nm)", 20, 150, 45)

st.sidebar.markdown("---")
st.sidebar.header("🕹️ Real-time Control / 即時控制")
throttle = st.sidebar.slider("Throttle / 油門開度 (%)", 0, 100, 100)

# 3. 主畫面標題
st.title("⚡ Electric Motorcycle Performance Simulator")
st.caption(f"TAD-AGE Propulsion Lab | Analysis Time: {tw_now.strftime('%H:%M:%S')}")
st.markdown("---")

# 4. 物理模型計算
speed_kmh = np.linspace(0.1, 100, 100)
# 扭矩特性：低速恆扭矩，高速恆功率 (假設 45km/h 為轉折點)
current_torque = max_torque * (throttle / 100) * (motor_eff / 100)
torque_curve = [current_torque if v < 45 else current_torque * (45/v) for v in speed_kmh]

# 加速度計算 (F=ma, F=Torque/Radius)
wheel_radius = 0.28 
accel = [(t / wheel_radius / bike_mass) for t in torque_curve]

# 5. 繪圖區 (左右對照)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🟦 Torque Curve / 扭矩曲線")
    fig_t, ax_t = plt.subplots(dpi=120)
    fig_t.patch.set_facecolor('#0e1117'); ax_t.set_facecolor('#111111')
    ax_t.plot(speed_kmh, torque_curve, color='#00d4ff', linewidth=3)
    # 使用英文標籤避免豆腐字，視覺更專業
    ax_t.set_xlabel("Speed (km/h)", color='gray')
    ax_t.set_ylabel("Torque (Nm)", color='gray')
    ax_t.tick_params(colors='white')
    ax_t.grid(True, color='#333', alpha=0.5)
    st.pyplot(fig_t)

with col2:
    st.markdown("### 🟥 Acceleration / 加速趨勢")
    fig_a, ax_a = plt.subplots(dpi=120)
    fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
    ax_a.plot(speed_kmh, accel, color='#ff4b4b', linewidth=3)
    ax_a.set_xlabel("Speed (km/h)", color='gray')
    ax_a.set_ylabel("Accel (m/s²)", color='gray')
    ax_a.tick_params(colors='white')
    ax_a.grid(True, color='#333', alpha=0.5)
    st.pyplot(fig_a)

# 6. 下方性能摘要 (優化視覺與色彩)
st.markdown("---")
st.markdown("### 📊 Performance Summary / 性能摘要")

# 計算核心指標
top_accel = max(accel)
zero_to_fifty = (50 / 3.6) / top_accel if top_accel > 0 else 0
# 計算功率 (P = T * ω)
peak_power = (current_torque * 45) / 9.548 / 1000 # kW

m1, m2, m3 = st.columns(3)

with m1:
    st.metric(label="Top Accel / 最大加速度", value=f"{round(top_accel, 2)} m/s²")
with m2:
    # 使用綠色 delta 代表性能預估
    st.metric(label="0-50 km/h (Est.) / 加速預估", value=f"{round(zero_to_fifty, 2)} sec", delta="Optimized")
with m3:
    st.metric(label="Peak Power / 峰值功率", value=f"{round(peak_power, 2)} kW")

# 7. 補充說明
with st.expander("📝 Simulation Logic / 模擬邏輯說明"):
    st.write("""
    - **Torque / 扭矩**: 模擬馬達在額定轉速下保持恆扭矩，超過後進入恆功率區。
    - **Efficiency / 效率**: 綜合考量控制器與馬達的熱損耗。
    - **Dynamics / 動力學**: 基於牛頓第二運動定律 F = ma 進行即時計算。
    """)