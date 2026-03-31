# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 1. 頁面基礎配置與全局變數
# ==========================================
st.set_page_config(page_title="TAD-AGE Multi-Sim V3", layout="wide", page_icon="🌐")

# 定義時間 (解決 NameError: tw_now)
tw_now = datetime.utcnow() + timedelta(hours=8)

# 定義全局統一字體與圖表樣式
font_style = {'family': 'sans-serif', 'color': '#ffffff', 'size': 10}
title_style = {'family': 'sans-serif', 'color': '#00d4ff', 'weight': 'bold', 'size': 12}

# 自定義 CSS 優化介面
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 22px; color: #00d4ff; }
    .stSlider label { color: #ffffff !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 側邊欄導覽
# ==========================================
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "Select System / 選擇模擬系統",
    ["EV Performance (加速與扭矩)", "Energy Efficiency (能源效率分析)", "PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"]
)

# 全局共享參數 (對應 PDF 8EM 模型)
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Global Config / 基礎參數")
bike_mass = st.sidebar.slider("Total Mass / 總重 (kg) [#1]", 100, 400, 180)
motor_eff = st.sidebar.slider("Motor Efficiency / 馬達效率 (%) [#5]", 50, 100, 92)

# ==========================================
# Mode A: EV Performance (電動車性能模擬)
# ==========================================
if app_mode == "EV Performance (加速與扭矩)":
    st.title("⚡ EV Performance Simulator")
    st.caption(f"V3 Layer 1-2 | Focus: Torque Control | {tw_now.strftime('%H:%M:%S')}")
    
    throttle = st.sidebar.slider("Throttle / 油門開度 (%)", 0, 100, 100)
    
    # 物理模型：馬達特性
    speed_kmh = np.linspace(0, 100, 100)
    base_torque = 45 * (throttle / 100) * (motor_eff / 100)
    torque_curve = [base_torque if v < 45 else base_torque * (45/v) for v in speed_kmh]
    accel = [(t * 5.5 / 0.28 / bike_mass) for t in torque_curve]

    col1, col2 = st.columns(2)
    with col1:
        fig_t, ax_t = plt.subplots(dpi=120)
        fig_t.patch.set_facecolor('#0e1117'); ax_t.set_facecolor('#111111')
        ax_t.plot(speed_kmh, torque_curve, color='#00d4ff', linewidth=3, antialiased=True)
        ax_t.set_title("Torque vs Speed (Motor Control)", fontdict=title_style, pad=15)
        ax_t.set_xlabel("Speed (km/h)", fontdict=font_style); ax_t.set_ylabel("Torque (Nm)", fontdict=font_style)
        ax_t.tick_params(colors='white'); ax_t.grid(True, color='#333', alpha=0.5)
        st.pyplot(fig_t)
    with col2:
        fig_a, ax_a = plt.subplots(dpi=120)
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(speed_kmh, accel, color='#ff4b4b', linewidth=3, antialiased=True)
        ax_a.set_title("Acceleration Propelling Trend", fontdict={'color': '#ff4b4b', 'weight': 'bold', 'size': 12}, pad=15)
        ax_a.set_xlabel("Speed (km/h)", fontdict=font_style); ax_a.set_ylabel("Accel (m/s²)", fontdict=font_style)
        ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333', alpha=0.5)
        st.pyplot(fig_a)

# ==========================================
# Mode B: Energy Efficiency (能源效率分析)
# ==========================================
elif app_mode == "Energy Efficiency (能源效率分析)":
    st.title("📊 Energy Efficiency Analysis")
    st.caption("V3 Layer 6 | 8EM Energy Decomposition")
    
    labels = ['Air Drag [#2]', 'Rolling [#3]', 'Motor Loss [#5]', 'Thermal [#8]', 'Others']
    sizes = [25, 15, 10, 5, 45]
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99', '#c2c2f0']
    
    col1, col2 = st.columns(2)
    with col1:
        fig_pie, ax_p = plt.subplots(dpi=120)
        fig_pie.patch.set_facecolor('#0e1117')
        ax_p.pie(sizes, labels=labels, autopct='%1.1f%%', textprops={'color':"w", 'size': 9}, colors=colors)
        ax_p.set_title("8EM Consumption Breakdown", fontdict=title_style)
        st.pyplot(fig_pie)
    with col2:
        st.info("💡 此模組預計整合 PDF 第 6 頁之 BMS SoC 動態計算公式。")

# ==========================================
# Mode C: PEM Hydrogen (恢復雙曲線重疊診斷)
# ==========================================
elif app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔋 PEM Hydrogen Diagnostic System")
    st.caption(f"Status: Running | Comparison Mode | {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    with st.sidebar:
        st.markdown("---")
        with st.expander("📊 Mode A: Baseline / 基準狀態", expanded=True):
            ohmic_a = st.slider("Ohmic Coeff A", 10.0, 30.0, 13.5, key="oa")
            act_a = st.slider("Activation A", 0.1, 0.5, 0.25, key="aa")
        with st.expander("🧪 Mode B: Testing / 測試狀態", expanded=True):
            ohmic_b = st.slider("Ohmic Coeff B", 10.0, 30.0, 22.0, key="ob")
            act_b = st.slider("Activation B", 0.1, 0.5, 0.35, key="ab")

    current_density = np.linspace(0.01, 2.0, 50)
    v_a = 1.2 - (ohmic_a/1000 * current_density) - act_a * np.log1p(current_density * 10)
    v_b = 1.2 - (ohmic_b/1000 * current_density) - act_b * np.log1p(current_density * 10)

    fig_pem, ax_pem = plt.subplots(figsize=(10, 5), dpi=120)
    fig_pem.patch.set_facecolor('#0e1117'); ax_pem.set_facecolor('#111111')
    
    ax_pem.plot(current_density, v_a, color='#00d4ff', linewidth=3, label='Baseline (基準)', antialiased=True)
    ax_pem.plot(current_density, v_b, color='#ff4b4b', linewidth=3, linestyle='--', label='Testing (測試)', antialiased=True)

    ax_pem.set_title("IV Characteristic Curve Comparison", fontdict=title_style, pad=20)
    ax_pem.set_xlabel("Current Density (A/cm²)", fontdict=font_style); ax_pem.set_ylabel("Voltage (V)", fontdict=font_style)
    ax_pem.tick_params(colors='white'); ax_pem.grid(True, color='#333', linestyle=':', alpha=0.6)
    ax_pem.legend(facecolor='#1a1a1a', edgecolor='#444', labelcolor='white')
    ax_pem.set_ylim(0, 1.3)
    st.pyplot(fig_pem)

# ==========================================
# Mode D: Cold Chain (恢復七大貨品與預測)
# ==========================================
else:
    st.title("❄️ Cold Chain Logistics Management")
    
    cargo_type = st.sidebar.selectbox(
        "Cargo Type / 貨品種類",
        ["Flower (花卉)", "Medicine (醫藥)", "Seafood (海鮮)", "Fruit (水果)", "Meat (肉類)", "Frozen (冷凍品)", "Chemical (化學品)"]
    )
    
    cargo_configs = {
        "Flower (花卉)": {"temp": 8, "limit": 12},
        "Medicine (醫藥)": {"temp": 4, "limit": 8},
        "Seafood (海鮮)": {"temp": -2, "limit": 2},
        "Fruit (水果)": {"temp": 5, "limit": 10},
        "Meat (肉類)": {"temp": 0, "limit": 4},
        "Frozen (冷凍品)": {"temp": -18, "limit": -15},
        "Chemical (化學品)": {"temp": 15, "limit": 25}
    }
    
    config = cargo_configs[cargo_type]
    st.sidebar.info(f"Target: {config['temp']}°C | Limit: {config['limit']}°C")

    time_h = np.arange(0, 12, 1)
    obs_temp = config['temp'] + np.random.normal(0, 0.4, 12)
    
    fig_cc, ax_cc = plt.subplots(figsize=(10, 4), dpi=120)
    fig_cc.patch.set_facecolor('#0e1117'); ax_cc.set_facecolor('#111111')
    ax_cc.plot(time_h, obs_temp, color='#00ffcc', marker='o', label=f'Real-time {cargo_type}')
    ax_cc.axhline(y=config['limit'], color='#ff4b4b', linestyle='--', label='Warning Limit')
    ax_cc.set_title(f"Temperature Monitoring: {cargo_type}", fontdict=title_style)
    ax_cc.set_xlabel("Time (Hours)", fontdict=font_style); ax_cc.set_ylabel("Temp (°C)", fontdict=font_style)
    ax_cc.tick_params(colors='white'); ax_cc.legend()
    st.pyplot(fig_cc)