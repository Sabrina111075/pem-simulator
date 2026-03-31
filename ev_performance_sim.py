# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE Multi-Sim V3", layout="wide", page_icon="🌐")

# 全局變數與樣式
tw_now = datetime.utcnow() + timedelta(hours=8)
font_style = {'family': 'sans-serif', 'color': '#ffffff', 'size': 10}
title_style = {'family': 'sans-serif', 'color': '#00d4ff', 'weight': 'bold', 'size': 12}

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# 2. 側邊欄導覽
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "Select System / 選擇模擬系統",
    ["EV Performance (加速與扭矩)", "Energy Efficiency (能源效率分析)", "PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"]
)

# ==========================================
# Mode C: PEM Hydrogen (優化版診斷介面)
# ==========================================
if app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔋 PEM Hydrogen Diagnostic System")
    st.caption(f"V3 Architecture | Dual-State Analysis | {tw_now.strftime('%H:%M:%S')}")
    
    # 側邊欄：僅顯示氫能相關參數 (隱藏 Global Config)
    with st.sidebar:
        st.markdown("---")
        with st.expander("📊 Mode A: Baseline / 基準狀態", expanded=True):
            ohmic_a = st.slider("Ohmic Coeff A", 10.0, 30.0, 13.5, key="oa")
            act_a = st.slider("Activation A", 0.1, 0.5, 0.25, key="aa")
        with st.expander("🧪 Mode B: Testing / 測試狀態", expanded=True):
            ohmic_b = st.slider("Ohmic Coeff B", 10.0, 30.0, 22.0, key="ob")
            act_b = st.slider("Activation B", 0.1, 0.5, 0.35, key="ab")

    # 物理模型計算
    current_density = np.linspace(0.01, 2.0, 50)
    v_a = 1.2 - (ohmic_a/1000 * current_density) - act_a * np.log1p(current_density * 10)
    v_b = 1.2 - (ohmic_b/1000 * current_density) - act_b * np.log1p(current_density * 10)

    # 繪圖區：雙圖表顯示
    col1, col2 = st.columns(2)
    
    with col1:
        fig_a, ax_a = plt.subplots(dpi=120)
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(current_density, v_a, color='#00d4ff', linewidth=3, label='Baseline')
        ax_a.set_title("Baseline IV Curve", fontdict=title_style, pad=15)
        ax_a.set_xlabel("Current Density (A/cm²)", fontdict=font_style)
        ax_a.set_ylabel("Voltage (V)", fontdict=font_style)
        ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333', alpha=0.5)
        st.pyplot(fig_a)

    with col2:
        fig_b, ax_b = plt.subplots(dpi=120)
        fig_b.patch.set_facecolor('#0e1117'); ax_b.set_facecolor('#111111')
        ax_b.plot(current_density, v_b, color='#ff4b4b', linewidth=3, label='Testing')
        ax_b.set_title("Testing IV Curve", fontdict=title_style, pad=15)
        ax_b.set_xlabel("Current Density (A/cm²)", fontdict=font_style)
        ax_b.set_ylabel("Voltage (V)", fontdict=font_style)
        ax_b.tick_params(colors='white'); ax_b.grid(True, color='#333', alpha=0.5)
        st.pyplot(fig_b)

    # 診斷指標區
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    
    # 計算健康指數與電壓降
    v_drop = v_a.mean() - v_b.mean()
    health_idx = max(0, 100 - (v_drop / v_a.mean() * 100))
    
    m1.metric("Health Index", f"{round(health_idx, 1)}%")
    m2.metric("Voltage Drop", f"{round(v_drop, 3)} V", delta=f"{round(v_drop/v_a.mean()*100, 1)}%", delta_color="inverse")
    m3.metric("Baseline Avg", f"{round(v_a.mean(), 2)} V")
    m4.metric("Testing Avg", f"{round(v_b.mean(), 2)} V")

# ==========================================
# 其他模式 (僅在需要時顯示 Global Config)
# ==========================================
else:
    # 在非氫能模式下才顯示 Global Config
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Global Config")
    bike_mass = st.sidebar.slider("Total Mass (kg)", 100, 400, 180)
    motor_eff = st.sidebar.slider("Motor Efficiency (%)", 50, 100, 92)

    if app_mode == "EV Performance (加速與扭矩)":
        st.title("⚡ EV Performance Simulator")
        st.write("此處顯示 EV 性能圖表...")
    
    elif app_mode == "Energy Efficiency (能源效率分析)":
        st.title("📊 Energy Efficiency Analysis")
        st.write("此處顯示能耗分析...")
        
    else: # Cold Chain
        st.title("❄️ Cold Chain Logistics")
        st.write("此處顯示冷鏈監控...")