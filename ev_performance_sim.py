# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面基礎配置
st.set_page_config(page_title="TAD-AGE Hydrogen Diagnostic", layout="wide", page_icon="🔋")

# 全局樣式定義
tw_now = datetime.utcnow() + timedelta(hours=8)
font_style = {'family': 'sans-serif', 'color': '#ffffff', 'size': 11}
title_style = {'family': 'sans-serif', 'color': '#00d4ff', 'weight': 'bold', 'size': 14}

# CSS: 極大化指標清晰度與卡片質感
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    /* 指標卡片容器 */
    div[data-testid="stMetric"] {
        background-color: #1c2128;
        border: 2px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    /* 指標標籤字體 */
    label[data-testid="stMetricLabel"] { 
        font-size: 18px !important; 
        color: #adb5bd !important; 
        font-weight: 600 !important;
    }
    /* 指標數值字體 (放大且變亮) */
    div[data-testid="stMetricValue"] { 
        font-size: 40px !important; 
        color: #00d4ff !important; 
        font-weight: 800 !important;
    }
    /* 修正趨勢標記大小 */
    div[data-testid="stMetricDelta"] { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 側邊欄導覽與參數設定
st.sidebar.title("🚀 System Navigation")
app_mode = st.sidebar.selectbox(
    "Select Simulation",
    ["PEM Hydrogen (氫能診斷)", "EV Performance (加速與扭矩)", "Energy Efficiency (能源效率分析)", "Cold Chain (冷鏈物流)"]
)

# 當模式為氫能診斷時，將 A/B 參數放入側邊欄
if app_mode == "PEM Hydrogen (氫能診斷)":
    with st.sidebar:
        st.markdown("---")
        st.header("📊 Diagnostic Setup")
        with st.expander("🟦 Mode A: Baseline (基準)", expanded=True):
            temp_a = st.slider("Temp A (°C)", 40, 90, 60, key="ta")
            ohmic_a = st.slider("Ohmic A", 10.0, 30.0, 13.5, key="oa")
            hum_a = st.slider("Humidity A (%)", 20, 100, 80, key="ha")
            
        with st.expander("🟥 Mode B: Testing (測試)", expanded=True):
            temp_b = st.slider("Temp B (°C)", 40, 90, 75, key="tb")
            ohmic_b = st.slider("Ohmic B", 10.0, 30.0, 22.0, key="ob")
            hum_b = st.slider("Humidity B (%)", 20, 100, 60, key="hb")

    # 3. 主畫面：氫能診斷邏輯
    st.title("🔋 PEM Hydrogen Diagnostic System")
    st.caption(f"Real-time Analysis Mode | {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # 物理模型計算
    current_density = np.linspace(0.01, 2.0, 50)
    def calc_v(temp, ohmic, hum):
        return 1.22 - (0.28 - temp/550) * np.log1p(current_density * 10) - (ohmic/1000 * current_density) * (1.2 - hum/100)

    v_a = calc_v(temp_a, ohmic_a, hum_a)
    v_b = calc_v(temp_b, ohmic_b, hum_b)

    # 圖表區：兩張大圖並列
    col_fig1, col_fig2 = st.columns(2)
    
    with col_fig1:
        fig_a, ax_a = plt.subplots(dpi=130) # 稍微提高 DPI 增加清晰度
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(current_density, v_a, color='#00d4ff', linewidth=4, label='Baseline')
        ax_a.set_title("Baseline IV Characteristic", fontdict=title_style, pad=20)
        ax_a.set_xlabel("Current Density (A/cm²)", fontdict=font_style)
        ax_a.set_ylabel("Cell Voltage (V)", fontdict=font_style)
        ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333', alpha=0.5, linestyle='--')
        st.pyplot(fig_a)

    with col_fig2:
        fig_b, ax_b = plt.subplots(dpi=130)
        fig_b.patch.set_facecolor('#0e1117'); ax_b.set_facecolor('#111111')
        ax_b.plot(current_density, v_b, color='#ff4b4b', linewidth=4, label='Testing')
        ax_b.set_title("Testing IV Characteristic", fontdict={'color': '#ff4b4b', 'weight': 'bold', 'size': 14}, pad=20)
        ax_b.set_xlabel("Current Density (A/cm²)", fontdict=font_style)
        ax_b.set_ylabel("Cell Voltage (V)", fontdict=font_style)
        ax_b.tick_params(colors='white'); ax_b.grid(True, color='#333', alpha=0.5, linestyle='--')
        st.pyplot(fig_b)

    # 4. 下方指標區：字體放大與清晰化
    st.markdown("### 🔍 Diagnostic Metrics")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    avg_a, avg_b = v_a.mean(), v_b.mean()
    v_drop = avg_a - avg_b
    health_idx = max(0, 100 - (v_drop / avg_a * 250)) # 放大衰減感官

    m_col1.metric("Health Index", f"{round(health_idx, 1)}%", delta=f"{'Healthy' if health_idx > 80 else 'Warning'}")
    m_col2.metric("Voltage Drop", f"{round(v_drop, 3)} V", delta=f"{round(v_drop/avg_a*100, 1)}%", delta_color="inverse")
    m_col3.metric("Baseline Avg", f"{round(avg_a, 2)} V")
    m_col4.metric("Status", "Operational" if health_idx > 85 else "Action Required")

# ==========================================
# 其他模式預留
# ==========================================
else:
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Config")
    st.sidebar.slider("Global Parameter", 0, 100, 50)
    st.title(f"🛠️ {app_mode} System")
    st.info("Module content is loaded under this architecture.")