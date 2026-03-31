# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 頁面配置
st.set_page_config(page_title="TAD-AGE EV Dev-Mode", layout="wide", page_icon="⚡")

# 工業深色風 CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetric"] {
        background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

tw_now = datetime.utcnow() + timedelta(hours=8)

# --- 側邊欄導覽 ---
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "Select System / 選擇模擬系統",
    ["EV Performance (加速與扭矩)", "PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"]
)

# ==========================================
# Mode A: EV Performance / 電動車性能模擬 (新功能)
# ==========================================
if app_mode == "EV Performance (加速與扭矩)":
    st.title("⚡ EV Performance Simulator / 電動車性能模擬")
    st.caption(f"V3 Architecture: Layer 1-2 Focus | Time: {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # 側邊欄：根據 PDF 8EM 模型設定參數
    st.sidebar.header("⚙️ Performance Specs (#1, #5)")
    bike_mass = st.sidebar.slider("Total Mass / 總重 (kg) [#1]", 100, 400, 180)
    motor_eff = st.sidebar.slider("Motor Efficiency / 馬達效率 (%) [#5]", 50, 100, 92)
    throttle = st.sidebar.slider("Throttle Opening / 油門開度 (%)", 0, 100, 100)
    
    # 物理模擬：馬達特性 (Layer 1: Torque Generation)
    speed_kmh = np.linspace(0, 100, 100)
    # 模擬馬達特性：45km/h 以下恆扭矩，以上恆功率
    base_torque = 45 * (throttle / 100) * (motor_eff / 100)
    torque_curve = [base_torque if v < 45 else base_torque * (45/v) for v in speed_kmh]
    
    # 計算推力與加速度 (F = T * ratio / radius)
    force = [t * 5.5 / 0.28 for t in torque_curve] # 假設傳動比 5.5, 輪胎半徑 0.28m
    accel = [f / bike_mass for f in force]

    # 繪圖區
    col1, col2 = st.columns(2)
    
    with col1:
        fig_t, ax_t = plt.subplots()
        fig_t.patch.set_facecolor('#0e1117'); ax_t.set_facecolor('#111111')
        ax_t.plot(speed_kmh, torque_curve, color='#00d4ff', linewidth=3)
        ax_t.set_title("Torque vs Speed (L1 Motor Control)", color='white', fontweight='bold')
        ax_t.set_xlabel("Speed (km/h)", color='white'); ax_t.set_ylabel("Torque (Nm)", color='white')
        ax_t.tick_params(colors='white'); ax_t.grid(True, color='#333')
        st.pyplot(fig_t)

    with col2:
        fig_a, ax_a = plt.subplots()
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(speed_kmh, accel, color='#ff4b4b', linewidth=3)
        ax_a.set_title("Acceleration Propelling Trend", color='white', fontweight='bold')
        ax_a.set_xlabel("Speed (km/h)", color='white'); ax_a.set_ylabel("Accel (m/s²)", color='white')
        ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333')
        st.pyplot(fig_a)

    # 指標顯示 (雙語)
    m1, m2, m3 = st.columns(3)
    m1.metric("Peak Torque / 最大扭矩", f"{round(max(torque_curve), 1)} Nm")
    m2.metric("SWC Mapping", "TorqueControl")
    m3.metric("AUTOSAR Layer", "Layer 1 (MCU)")

    st.info("💡 此模擬對應 AUTOSAR SWC: TorqueControl 與 RTE: TorqueReq 映射")

# ==========================================
# Mode B: PEM Hydrogen / 氫能診斷 (原有功能空間)
# ==========================================
elif app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔋 PEM Hydrogen Diagnostic / 氫能診斷")
    st.write("此處保留原本 PEM 診斷邏輯。妳可以隨時將舊代碼貼回此處。")

# ==========================================
# Mode C: Cold Chain / 冷鏈物流 (原有功能空間)
# ==========================================
else:
    st.title("❄️ Cold Chain Logistics / 冷鏈物流")
    st.write("此處保留原本冷鏈物流邏輯。妳可以隨時將舊代碼貼回此處。")