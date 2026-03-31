# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面基礎配置
st.set_page_config(page_title="TAD-AGE Hydrogen Diagnostic", layout="wide", page_icon="🔋")

# 全局樣式與時間定義
tw_now = datetime.utcnow() + timedelta(hours=8)
font_style = {'color': '#ffffff', 'size': 10}
title_style = {'color': '#00d4ff', 'weight': 'bold', 'size': 13}

# CSS: 強化診斷指標卡片與字體清晰度
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #1c2128;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
    }
    label[data-testid="stMetricLabel"] { 
        font-size: 18px !important; 
        color: #adb5bd !important; 
    }
    div[data-testid="stMetricValue"] { 
        font-size: 36px !important; 
        color: #00d4ff !important; 
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 側邊欄：導覽與參數設定
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

    # 圖表顯示 (解決豆腐字：內部標籤改為英文，標題中英並行)
    col_fig1, col_fig2 = st.columns(2)
    
    with col_fig1:
        fig_a, ax_a = plt.subplots(dpi=130)
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(current_density, v_a, color='#00d4ff', linewidth=4)
        ax_a.set_title("Baseline IV Curve (基準狀態)", fontdict=title_style, pad=20)
        ax_a.set_xlabel("Current Density (A/cm²)", fontdict=font_style)
        ax_a.set_ylabel("Cell Voltage (V)", fontdict=font_style)
        ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333', alpha=0.5, linestyle='--')
        st.pyplot(fig_a)

    with col_fig2:
        fig_b, ax_b = plt.subplots(dpi=130)
        fig_b.patch.set_facecolor('#0e1117'); ax_b.set_facecolor('#111111')
        ax_b.plot(current_density, v_b, color='#ff4b4b', linewidth=4)
        ax_b.set_title("Testing IV Curve (測試狀態)", fontdict={'color': '#ff4b4b', 'weight': 'bold', 'size': 13}, pad=20)
        ax_b.set_xlabel("Current Density (A/cm²)", fontdict=font_style)
        ax_b.set_ylabel("Cell Voltage (V)", fontdict=font_style)
        ax_b.tick_params(colors='white'); ax_b.grid(True, color='#333', alpha=0.5, linestyle='--')
        st.pyplot(fig_b)

    # 4. 下方指標：簡化為 Health Index A/B 與 Avg. Volt Drop
    st.markdown("### 🔍 Diagnostic Metrics / 診斷指標")
    m1, m2, m3 = st.columns(3)
    
    avg_a, avg_b = v_a.mean(), v_b.mean()
    v_drop = avg_a - avg_b
    # 計算健康指數 (以平均電壓為基準)
    hi_a = 100.0
    hi_b = max(0, 100 - (v_drop / avg_a * 250)) 

    m1.metric("Health Index A / 健康指數 A", f"{round(hi_a, 1)}%")
    m2.metric("Health Index B / 健康指數 B", f"{round(hi_b, 1)}%", delta=f"-{round(100-hi_b, 1)}%", delta_color="inverse")
    m3.metric("Avg. Volt Drop / 平均壓降", f"{round(v_drop, 3)} V")

else:
    st.title("🛠️ System Module")
    st.info("切換至氫能診斷模式以查看完整介面。")