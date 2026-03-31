# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE Multi-Sim V3", layout="wide", page_icon="🌐")

# 全局字體優化 (解決 NameError)
font_style = {'family': 'sans-serif', 'color': '#ffffff', 'size': 10}
title_style = {'family': 'sans-serif', 'color': '#00d4ff', 'weight': 'bold', 'size': 12}

tw_now = datetime.utcnow() + timedelta(hours=8)

# 2. 側邊欄導覽
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "Select System / 選擇模擬系統",
    ["EV Performance (加速與扭矩)", "Energy Efficiency (能源效率分析)", "PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"]
)

# ==========================================
# Mode C: PEM Hydrogen (恢復基準與測試雙狀態)
# ==========================================
if app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔋 PEM Hydrogen Diagnostic System")
    st.caption(f"V3 Architecture | Status: Running | {tw_now.strftime('%H:%M:%S')}")
    
    # 恢復「基準狀態」與「測試狀態」參數設定
    with st.sidebar:
        st.markdown("---")
        with st.expander("📊 Mode A: Baseline / 基準狀態", expanded=True):
            temp_a = st.slider("Temperature A / 溫度 (°C)", 40, 90, 60, key="ta")
            ohmic_a = st.slider("Ohmic Coeff A / 歐姆係數", 10.0, 20.0, 13.5, key="oa")
            hum_a = st.slider("Humidity A / 濕度 (%)", 20, 100, 80, key="ha")

        with st.expander("🧪 Mode B: Testing / 測試狀態", expanded=True):
            temp_b = st.slider("Temperature B / 溫度 (°C)", 40, 90, 75, key="tb")
            ohmic_b = st.slider("Ohmic Coeff B / 歐姆係數", 10.0, 20.0, 15.2, key="ob")
            hum_b = st.slider("Humidity B / 濕度 (%)", 20, 100, 60, key="hb")

    current_density = np.linspace(0, 2.0, 50)
    # 恢復 IV 曲線物理邏輯
    v_a = 1.2 - (ohmic_a/1000 * current_density) - 0.2 * np.log1p(current_density * 10)
    v_b = 1.2 - (ohmic_b/1000 * current_density) - 0.2 * np.log1p(current_density * 10)

    col1, col2 = st.columns(2)
    with col1:
        fig_a, ax_a = plt.subplots(dpi=120)
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(current_density, v_a, color='#00d4ff', marker='o', markersize=3, label='Baseline')
        ax_a.set_title("Baseline IV Curve", fontdict=title_style); ax_a.legend()
        ax_a.set_xlabel("Current Density (A/cm²)", fontdict=font_style); ax_a.set_ylabel("Voltage (V)", fontdict=font_style)
        ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333', alpha=0.5)
        st.pyplot(fig_a)
    with col2:
        fig_b, ax_b = plt.subplots(dpi=120)
        fig_b.patch.set_facecolor('#0e1117'); ax_b.set_facecolor('#111111')
        ax_b.plot(current_density, v_b, color='#ff4b4b', marker='s', markersize=3, label='Testing')
        ax_b.set_title("Testing IV Curve", fontdict=title_style); ax_b.legend()
        ax_b.set_xlabel("Current Density (A/cm²)", fontdict=font_style); ax_b.set_ylabel("Voltage (V)", fontdict=font_style)
        ax_b.tick_params(colors='white'); ax_b.grid(True, color='#333', alpha=0.5)
        st.pyplot(fig_b)

# ==========================================
# Mode D: Cold Chain (恢復七大貨品參數)
# ==========================================
elif app_mode == "Cold Chain (冷鏈物流)":
    st.title("❄️ Cold Chain Logistics Management")
    
    # 恢復七大貨品選擇與對應係數
    cargo_type = st.sidebar.selectbox(
        "Cargo Type / 貨品種類",
        ["Flower (花卉)", "Medicine (醫藥)", "Seafood (海鮮)", "Fruit (水果)", "Meat (肉類)", "Frozen (冷凍品)", "Chemical (化學品)"]
    )
    
    # 對應 Viskovatov 預測係數
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

    # 模擬庫溫監測數據
    time_h = np.arange(0, 12, 1)
    base_temp = config['temp']
    obs_temp = base_temp + np.random.normal(0, 0.5, 12)
    
    fig_cc, ax_cc = plt.subplots(figsize=(10, 4), dpi=120)
    fig_cc.patch.set_facecolor('#0e1117'); ax_cc.set_facecolor('#111111')
    ax_cc.plot(time_h, obs_temp, color='#00ffcc', marker='o', label=f'Real-time {cargo_type}')
    ax_cc.axhline(y=config['limit'], color='red', linestyle='--', label='Warning Limit')
    ax_cc.set_title(f"Temperature Trend: {cargo_type}", fontdict=title_style)
    ax_cc.tick_params(colors='white'); ax_cc.legend()
    st.pyplot(fig_cc)

# ==========================================
# 其他模式 (EV & Efficiency) 保留
# ==========================================
else:
    st.title("🛠️ System Module Under Construction")
    st.info("EV Performance 與能源效率模組已在 V3 架構中就緒。")