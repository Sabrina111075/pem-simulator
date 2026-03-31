# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE Hydrogen Dev-Mode", layout="wide", page_icon="🔋")

# 全局樣式優化
tw_now = datetime.utcnow() + timedelta(hours=8)
font_style = {'family': 'sans-serif', 'color': '#ffffff', 'size': 10}
title_style = {'family': 'sans-serif', 'color': '#00d4ff', 'weight': 'bold', 'size': 13}

# CSS: 強化指標顯示的視覺效果
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
    }
    label[data-testid="stMetricLabel"] { font-size: 16px !important; color: #8b949e !important; }
    div[data-testid="stMetricValue"] { font-size: 32px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 側邊欄導覽
st.sidebar.title("🚀 Navigation")
app_mode = st.sidebar.selectbox(
    "Select System",
    ["PEM Hydrogen (氫能診斷)", "EV Performance (加速與扭矩)", "Energy Efficiency (能源效率分析)", "Cold Chain (冷鏈物流)"]
)

# ==========================================
# Mode: PEM Hydrogen (精緻診斷版)
# ==========================================
if app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔋 PEM Hydrogen Diagnostic System")
    st.caption(f"V3 Architecture | Advanced Diagnostic Mode | {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # 配置左側參數控制區與右側圖表區
    ctrl_col, chart_col = st.columns([1, 3])

    with ctrl_col:
        st.subheader("🛠️ Control Panel")
        with st.container():
            st.markdown("### **Baseline / 基準**")
            temp_a = st.slider("Temperature A (°C)", 40, 90, 60, key="ta")
            ohmic_a = st.slider("Ohmic Coeff A", 10.0, 30.0, 13.5, key="oa")
            hum_a = st.slider("Humidity A (%)", 20, 100, 80, key="ha")
            
            st.markdown("---")
            st.markdown("### **Testing / 測試**")
            temp_b = st.slider("Temperature B (°C)", 40, 90, 75, key="tb")
            ohmic_b = st.slider("Ohmic Coeff B", 10.0, 30.0, 22.0, key="ob")
            hum_b = st.slider("Humidity B (%)", 20, 100, 60, key="hb")

    # 物理模型計算 (加入濕度與溫度補償因子)
    current_density = np.linspace(0.01, 2.0, 50)
    def calc_v(temp, ohmic, hum):
        # 簡易 PEM 模型：電壓 = 開路電壓 - 活化極化 - 歐姆極化
        return 1.22 - (0.25 - temp/600) * np.log1p(current_density * 10) - (ohmic/1000 * current_density) * (1.2 - hum/100)

    v_a = calc_v(temp_a, ohmic_a, hum_a)
    v_b = calc_v(temp_b, ohmic_b, hum_b)

    with chart_col:
        col_fig1, col_fig2 = st.columns(2)
        
        with col_fig1:
            fig_a, ax_a = plt.subplots(dpi=120)
            fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
            ax_a.plot(current_density, v_a, color='#00d4ff', linewidth=3, label='Baseline')
            ax_a.set_title("Baseline IV Characteristic", fontdict=title_style, pad=15)
            ax_a.set_xlabel("Current Density (A/cm²)", fontdict=font_style)
            ax_a.set_ylabel("Cell Voltage (V)", fontdict=font_style)
            ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333', alpha=0.5)
            st.pyplot(fig_a)

        with col_fig2:
            fig_b, ax_b = plt.subplots(dpi=120)
            fig_b.patch.set_facecolor('#0e1117'); ax_b.set_facecolor('#111111')
            ax_b.plot(current_density, v_b, color='#ff4b4b', linewidth=3, label='Testing')
            ax_b.set_title("Testing IV Characteristic", fontdict={'color': '#ff4b4b', 'weight': 'bold', 'size': 13}, pad=15)
            ax_b.set_xlabel("Current Density (A/cm²)", fontdict=font_style)
            ax_b.set_ylabel("Cell Voltage (V)", fontdict=font_style)
            ax_b.tick_params(colors='white'); ax_b.grid(True, color='#333', alpha=0.5)
            st.pyplot(fig_b)

    # 3. 下方指標區：優化清晰度
    st.markdown("### 🔍 Diagnostic Metrics / 診斷指標")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    avg_a = v_a.mean()
    avg_b = v_b.mean()
    v_drop = avg_a - avg_b
    health_idx = max(0, 100 - (v_drop / avg_a * 200)) # 加權顯示衰減

    m_col1.metric("Health Index", f"{round(health_idx, 1)}%", delta=f"{'Excellent' if health_idx > 90 else 'Check'}")
    m_col2.metric("Voltage Drop", f"{round(v_drop, 3)} V", delta=f"{round(v_drop/avg_a*100, 1)}%", delta_color="inverse")
    m_col3.metric("Ohmic Shift", f"{round(ohmic_b - ohmic_a, 1)}", delta="Increased" if ohmic_b > ohmic_a else "Stable")
    m_col4.metric("Status", "Degraded" if health_idx < 85 else "Healthy")

# ==========================================
# 其他模式保留 (簡化處理)
# ==========================================
else:
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Global Config")
    bike_mass = st.sidebar.slider("Total Mass (kg)", 100, 400, 180)
    
    st.title(f"🛠️ {app_mode} System")
    st.info("系統模組已就緒。")