# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE Hydrogen Diagnostic", layout="wide", page_icon="🔋")

# 全局樣式定義
tw_now = datetime.utcnow() + timedelta(hours=8)
# 為了解決豆腐字，圖表內部標籤主要使用英文，標題採中英雙語
font_style = {'color': '#ffffff', 'size': 11}
title_style = {'color': '#00d4ff', 'weight': 'bold', 'size': 14}

# CSS: 模仿截圖中的簡潔指標樣式
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #1c2128;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] { 
        font-size: 38px !important; 
        color: #00d4ff !important; 
        font-weight: 700 !important;
    }
    label[data-testid="stMetricLabel"] { 
        font-size: 18px !important; 
        color: #adb5bd !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 側邊欄：導覽與參數設定 (中英對照)
st.sidebar.title("🚀 Navigation / 導覽")
app_mode = st.sidebar.selectbox(
    "Select System / 選擇系統",
    ["PEM Hydrogen (氫能診斷)", "EV Performance (加速與扭矩)", "Energy Efficiency (能源效率分析)"]
)

if app_mode == "PEM Hydrogen (氫能診斷)":
    with st.sidebar:
        st.markdown("---")
        with st.expander("🟦 Baseline / 基準狀態", expanded=True):
            temp_a = st.slider("Temp / 溫度 (°C)", 40, 90, 60, key="ta")
            ohmic_a = st.slider("Ohmic / 歐姆係數", 10.0, 30.0, 13.5, key="oa")
            hum_a = st.slider("Humidity / 濕度 (%)", 20, 100, 80, key="ha")
        with st.expander("🟥 Testing / 測試狀態", expanded=True):
            temp_b = st.slider("Temp / 溫度 (°C)", 40, 90, 75, key="tb")
            ohmic_b = st.slider("Ohmic / 歐姆係數", 10.0, 30.0, 22.0, key="ob")
            hum_b = st.slider("Humidity / 濕度 (%)", 20, 100, 60, key="hb")

    # 3. 主畫面
    st.title("🔋 PEM Hydrogen Diagnostic System")
    st.caption(f"Analysis Time: {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # 物理模型計算
    current_density = np.linspace(0.01, 2.0, 50)
    def calc_v(temp, ohmic, hum):
        return 1.22 - (0.28 - temp/550) * np.log1p(current_density * 10) - (ohmic/1000 * current_density) * (1.2 - hum/100)

    v_a = calc_v(temp_a, ohmic_a, hum_a)
    v_b = calc_v(temp_b, ohmic_b, hum_b)

    # 圖表顯示 (解決豆腐字：標籤改為國際通用英文標記)
    col_fig1, col_fig2 = st.columns(2)
    
    with col_fig1:
        fig_a, ax_a = plt.subplots(dpi=130)
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(current_density, v_a, color='#00d4ff', linewidth=4)
        ax_a.set_title("Baseline IV Curve (基準)", fontdict=title_style, pad=20)
        ax_a.set_xlabel("Current Density (A/cm²)", fontdict=font_style)
        ax_a.set_ylabel("Cell Voltage (V)", fontdict=font_style)
        ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333', alpha=0.5, linestyle='--')
        st.pyplot(fig_a)

    with col_fig2:
        fig_b, ax_b = plt.subplots(dpi=130)
        fig_b.patch.set_facecolor('#0e1117'); ax_b.set_facecolor('#111111')
        ax_b.plot(current_density, v_b, color='#ff4b4b', linewidth=4)
        ax_b.set_title("Testing IV Curve (測試)", fontdict={'color': '#ff4b4b', 'weight': 'bold', 'size': 14}, pad=20)
        ax_b.set_xlabel("Current Density (A/cm²)", fontdict=font_style)
        ax_a.set_ylabel("Cell Voltage (V)", fontdict=font_style)
        ax_b.tick_params(colors='white'); ax_b.grid(True, color='#333', alpha=0.5, linestyle='--')
        st.pyplot(fig_b)

    # 4. 下方指標：簡化且清晰化 (仿截圖樣式)
    st.markdown("### 🔍 Diagnostic Metrics / 診斷指標")
    m1, m2, m3, m4 = st.columns(4)
    
    avg_a, avg_b = v_a.mean(), v_b.mean()
    v_drop = avg_a - avg_b
    health_idx = max(0, 100 - (v_drop / avg_a * 250)) 

    # 簡化顯示文字，中英對照並縮減長度
    m1.metric("Health 指數", f"{round(health_idx, 1)}%")
    m2.metric("Volt Drop 壓降", f"{round(v_drop, 3)} V")
    m3.metric("Baseline 基準", f"{round(avg_a, 2)} V")
    m4.metric("Status 狀態", "Healthy" if health_idx > 85 else "Action")

else:
    st.title("🛠️ System Module")
    st.info("切換至氫能診斷模式以查看完整介面。")