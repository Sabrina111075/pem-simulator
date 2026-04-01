# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta # 導入 timedelta 進行時區修正

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE EV Propulsion", layout="wide", page_icon="🛵")

# --- 時間修正邏輯 ---
# 獲取 UTC 時間並轉換為台灣時間 (UTC+8)
utc_now = datetime.utcnow()
tw_now = utc_now + timedelta(hours=8)
current_time_str = tw_now.strftime('%Y-%m-%d %H:%M:%S')
# ------------------

# CSS: 強化數據卡片視覺
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #1c2128;
        border-left: 5px solid #00d4ff;
        padding: 15px;
        border-radius: 5px;
    }
    div[data-testid="stMetricValue"] { font-size: 32px !important; color: #00d4ff !important; font-weight: 700; }
    label[data-testid="stMetricLabel"] { font-size: 16px !important; color: #adb5bd !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 側邊欄：完整中英對照儀表板
st.sidebar.title("🚀 Control Center / 控制中心")

with st.sidebar.expander("🚲 Vehicle Specs / 車輛規格", expanded=True):
    bike_mass = st.sidebar.slider("Total Mass / 總重量 (kg)", 100, 500, 180)
    wheel_radius = st.sidebar.slider("Wheel Radius / 輪胎半徑 (m)", 0.2, 0.4, 0.28)

with st.sidebar.expander("🔋 Battery & Motor / 電能與馬達", expanded=True):
    max_torque = st.sidebar.slider("Motor Torque / 馬達扭矩 (Nm)", 20, 150, 60)
    motor_eff = st.sidebar.slider("Efficiency / 馬達效率 (%)", 70, 100, 92)
    batt_voltage = st.sidebar.slider("System Voltage / 系統電壓 (V)", 48, 96, 72)

with st.sidebar.expander("⚙️ Drivetrain / 傳動系統設計", expanded=True):
    gear_ratio = st.sidebar.slider("Gear Ratio / 齒輪比", 1.0, 15.0, 7.5)
    transmission_loss = st.sidebar.slider("Trans. Loss / 傳動損耗 (%)", 0, 15, 5)

with st.sidebar.expander("🌬️ Environment / 環境阻力因子", expanded=False):
    cd_factor = st.sidebar.slider("Air Drag / 風阻係數 (Cd)", 0.1, 1.2, 0.45)
    rolling_res = st.sidebar.slider("Rolling / 滾動阻力", 0.01, 0.05, 0.015)

st.sidebar.markdown("---")
throttle = st.sidebar.select_slider("Throttle / 油門控制 (%)", options=[0, 20, 40, 60, 80, 100], value=100)

# 3. 物理模型計算
speed_kmh = np.linspace(0.1, 110, 100)
speed_ms = speed_kmh / 3.6
base_speed = 40 * (batt_voltage / 72) 
effective_eff = (motor_eff / 100) * (1 - transmission_loss / 100)
wheel_torque = max_torque * gear_ratio * (throttle / 100) * effective_eff
current_torque_curve = [wheel_torque if v < base_speed else wheel_torque * (base_speed/v) for v in speed_kmh]

air_drag = 0.5 * 1.225 * (speed_ms**2) * cd_factor * 0.6 
rolling_drag = bike_mass * 9.8 * rolling_res
total_resistance = air_drag + rolling_drag

accel = [( (t / wheel_radius) - r ) / bike_mass for t, r in zip(current_torque_curve, total_resistance)]
accel = [max(0, a) for a in accel]

# 4. 主畫面標題 (使用正確的台灣時間)
st.title("⚡ Electric Motorcycle Propulsion Simulator")
st.subheader("電動機車動力模擬系統") 
# 在這裡顯示修正後的正確時間
st.caption(f"TAD-AGE Propulsion Lab | V3.6 Professional | Analysis Time: {current_time_str}")
st.markdown("---")

# 5. 繪圖區
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🟦 Torque Output / 輪軸扭矩輸出")
    fig_t, ax_t = plt.subplots(dpi=130)
    fig_t.patch.set_facecolor('#0e1117'); ax_t.set_facecolor('#111111')
    ax_t.plot(speed_kmh, current_torque_curve, color='#00d4ff', linewidth=4)
    ax_t.set_xlabel("Speed (km/h)", color='gray')
    ax_t.set_ylabel("Torque (Nm)", color='gray')
    ax_t.tick_params(colors='white'); ax_t.grid(True, color='#333', alpha=0.3)
    st.pyplot(fig_t)

with col2:
    st.markdown("### 🟥 Acceleration Trend / 加速度趨勢")
    fig_a, ax_a = plt.subplots(dpi=130)
    fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
    ax_a.plot(speed_kmh, accel, color='#ff4b4b', linewidth=4)
    ax_a.set_xlabel("Speed (km/h)", color='gray')
    ax_a.set_ylabel("Accel (m/s²)", color='gray')
    ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333', alpha=0.3)
    st.pyplot(fig_a)

# 6. 性能數據摘要
st.markdown("---")
st.markdown("### 📊 Performance Summary / 性能數據摘要")
m1, m2, m3, m4 = st.columns(4)

top_accel = max(accel)
est_power = (wheel_torque / gear_ratio * (base_speed * 100) / 9550) 
wh_per_km = (est_power * 1000 / 45) if throttle > 0 else 0 

m1.metric("Top Accel / 最大加速度", f"{round(top_accel, 2)} m/s²")
m2.metric("Peak Power / 峰值功率", f"{round(est_power, 1)} kW")
m3.metric("Energy / 預估能耗", f"{round(wh_per_km, 1)} Wh/km")
m4.metric("Status / 系統狀態", "Performance / 性能導向" if top_accel > 2.0 else "Efficiency / 節能導向")