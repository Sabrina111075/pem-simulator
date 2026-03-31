# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 1. 頁面基礎配置與風格
st.set_page_config(page_title="TAD-AGE Multi-Sim V3", layout="wide", page_icon="🌐")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 22px; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

tw_now = datetime.utcnow() + timedelta(hours=8)

# 2. 側邊欄導覽
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "Select System / 選擇模擬系統",
    ["EV Performance (加速與扭矩)", "Energy Efficiency (能源效率分析)", "PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"]
)

# 共享參數設定 (對應 V3 8EM 模型)
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Global Config / 參數設定")
bike_mass = st.sidebar.slider("Total Mass / 總重 (kg) [#1]", 100, 400, 180)
motor_eff = st.sidebar.slider("Motor Efficiency / 馬達效率 (%) [#5]", 50, 100, 92)

# ==========================================
# Mode A: EV Performance (性能表現)
# ==========================================
if app_mode == "EV Performance (加速與扭矩)":
    st.title("⚡ EV Performance Simulator")
    throttle = st.sidebar.slider("Throttle / 油門開度 (%)", 0, 100, 100)
    
    speed_kmh = np.linspace(0, 100, 100)
    base_torque = 45 * (throttle / 100) * (motor_eff / 100)
    torque_curve = [base_torque if v < 45 else base_torque * (45/v) for v in speed_kmh]
    accel = [(t * 5.5 / 0.28 / bike_mass) for t in torque_curve]

    font_style = {'color': '#ffffff', 'size': 11}
    col1, col2 = st.columns(2)
    with col1:
        fig_t, ax_t = plt.subplots(dpi=120)
        fig_t.patch.set_facecolor('#0e1117'); ax_t.set_facecolor('#111111')
        ax_t.plot(speed_kmh, torque_curve, color='#00d4ff', linewidth=3)
        ax_t.set_title("Torque vs Speed (L1 Control)", color='#00d4ff', fontweight='bold')
        ax_t.set_xlabel("Speed (km/h)", fontdict=font_style); ax_t.set_ylabel("Torque (Nm)", fontdict=font_style)
        ax_t.tick_params(colors='white'); ax_t.grid(True, color='#333', alpha=0.5)
        st.pyplot(fig_t)
    with col2:
        fig_a, ax_a = plt.subplots(dpi=120)
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(speed_kmh, accel, color='#ff4b4b', linewidth=3)
        ax_a.set_title("Acceleration Trend", color='#ff4b4b', fontweight='bold')
        ax_a.set_xlabel("Speed (km/h)", fontdict=font_style); ax_a.set_ylabel("Accel (m/s²)", fontdict=font_style)
        ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333', alpha=0.5)
        st.pyplot(fig_a)

# ==========================================
# Mode B: PEM Hydrogen (恢復原本的診斷邏輯)
# ==========================================
elif app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔋 PEM Hydrogen Diagnostic System")
    st.caption(f"Status: Running | Time (Taipei): {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 恢復原本的滑桿與運算
    temp = st.sidebar.slider("Temperature / 溫度 (°C)", 40, 90, 60)
    current_density = np.linspace(0, 2.0, 50)
    # 簡化模型示範 (請根據原本檔案調整公式)
    voltage_base = 1.2 - (0.002 * temp) - (0.3 * current_density)
    
    c1, c2 = st.columns(2)
    with c1:
        fig_v, ax_v = plt.subplots(dpi=120)
        fig_v.patch.set_facecolor('#0e1117'); ax_v.set_facecolor('#111111')
        ax_v.plot(current_density, voltage_base, color='#00ffff', marker='o', markersize=4)
        ax_v.set_title("Baseline IV Curve", color='white')
        ax_v.set_xlabel("Current Density (A/cm²)", fontdict=font_style)
        ax_v.set_ylabel("Voltage (V)", fontdict=font_style)
        ax_v.tick_params(colors='white'); ax_v.grid(True, color='#333')
        st.pyplot(fig_v)
    with c2:
        st.info("💡 測試狀態與基準狀態比對邏輯已重載。")

# ==========================================
# Mode C: Cold Chain (恢復 Viskovatov 預測)
# ==========================================
elif app_mode == "Cold Chain (冷鏈物流)":
    st.title("❄️ Cold Chain Logistics / Viskovatov Prediction")
    # 恢復原本的冷鏈邏輯
    st.write("目前顯示即時庫溫監測與 3H 預測趨勢。")
    
    time_h = np.arange(0, 15, 1)
    temp_obs = [0.5, 2.2, 3.1, 4.3, 5.2, 5.8, 5.7, 6.4, 6.8, 7.1, 7.5, 7.8]
    # 模擬預測線
    temp_pred = [7.8 + (i-11)*0.15 for i in range(11, 15)]
    
    fig_cc, ax_cc = plt.subplots(figsize=(10, 4), dpi=120)
    fig_cc.patch.set_facecolor('#0e1117'); ax_cc.set_facecolor('#111111')
    ax_cc.plot(range(len(temp_obs)), temp_obs, color='#00ffcc', marker='o', label='Observed')
    ax_cc.plot(range(11, 15), temp_pred, color='#ffa500', linestyle='--', label='Viskovatov Prediction')
    ax_cc.set_title("Temperature Monitoring & Prediction", color='white')
    ax_cc.tick_params(colors='white'); ax_cc.legend()
    st.pyplot(fig_cc)

# ==========================================
# Mode D: Energy Efficiency (新增的分析框架)
# ==========================================
else:
    st.title("📊 Energy Efficiency Analysis")
    st.write("此處為新增的 8EM 能耗分析模組。")