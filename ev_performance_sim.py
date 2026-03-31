# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面基礎配置
st.set_page_config(page_title="TAD-AGE Hydrogen Diagnostic", layout="wide", page_icon="🔋")

# 全局樣式與時間定義
tw_now = datetime.utcnow() + timedelta(hours=8)
font_style = {'family': 'sans-serif', 'color': '#ffffff', 'size': 11}
title_style = {'family': 'sans-serif', 'color': '#00d4ff', 'weight': 'bold', 'size': 14}

# CSS: 強化診斷指標卡片與字體清晰度
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #1c2128;
        border: 2px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    label[data-testid="stMetricLabel"] { 
        font-size: 20px !important; 
        color: #adb5bd !important; 
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] { 
        font-size: 42px !important; 
        color: #00d4ff !important; 
        font-weight: 800 !important;
    }
    div[data-testid="stMetricDelta"] { font-size: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 側邊欄：導覽與參數設定
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "Select Simulation / 選擇模擬系統",
    ["PEM Hydrogen (氫能診斷)", "EV Performance (加速與扭矩)", "Energy Efficiency (能源效率分析)", "Cold Chain (冷鏈物流)"]
)

if app_mode == "PEM Hydrogen (氫能診斷)":
    with st.sidebar:
        st.markdown("---")
        st.header("📊 Diagnostic Setup / 診斷設定")
        
        with st.expander("🟦 Mode A: Baseline / 基準狀態", expanded=True):
            temp_a = st.slider("Temp A / 溫度 (°C)", 40, 90, 60, key="ta")
            ohmic_a = st.slider("Ohmic A / 歐姆係數", 10.0, 30.0, 13.5, key="oa")
            hum_a = st.slider("Humidity A / 濕度 (%)", 20, 100, 80, key="ha")
            
        with st.expander("🟥 Mode B: Testing / 測試狀態", expanded=True):
            temp_b = st.slider("Temp B / 溫度 (°C)", 40, 90, 75, key="tb")
            ohmic_b = st.slider("Ohmic B / 歐姆係數", 10.0, 30.0, 22.0, key="ob")
            hum_b = st.slider("Humidity B / 濕度 (%)", 20, 100, 60, key="hb")

    # 3. 主畫面顯示
    st.title("🔋 PEM Hydrogen Diagnostic System")
    st.subheader("氫能燃料電池診斷系統 (中英對照版)")
    st.caption(f"Analysis Time / 分析時間: {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # 物理模型計算
    current_density = np.linspace(0.01, 2.0, 50)
    def calc_v(temp, ohmic, hum):
        # 包含溫度與濕度影響的簡化極化曲線模型
        return 1.22 - (0.28 - temp/550) * np.log1p(current_density * 10) - (ohmic/1000 * current_density) * (1.2 - hum/100)

    v_a = calc_v(temp_a, ohmic_a, hum_a)
    v_b = calc_v(temp_b, ohmic_b, hum_b)

    # 雙圖表大尺寸顯示
    col_fig1, col_fig2 = st.columns(2)
    
    with col_fig1:
        fig_a, ax_a = plt.subplots(dpi=130)
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(current_density, v_a, color='#00d4ff', linewidth=4)
        ax_a.set_title("Baseline IV Curve / 基準狀態曲線", fontdict=title_style, pad=20)
        ax_a.set_xlabel("Current Density / 電流密度 (A/cm²)", fontdict=font_style)
        ax_a.set_ylabel("Cell Voltage / 電池電壓 (V)", fontdict=font_style)
        ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333', alpha=0.5, linestyle='--')
        st.pyplot(fig_a)

    with col_fig2:
        fig_b, ax_b = plt.subplots(dpi=130)
        fig_b.patch.set_facecolor('#0e1117'); ax_b.set_facecolor('#111111')
        ax_b.plot(current_density, v_b, color='#ff4b4b', linewidth=4)
        ax_b.set_title("Testing IV Curve / 測試狀態曲線", fontdict={'color': '#ff4b4b', 'weight': 'bold', 'size': 14}, pad=20)
        ax_b.set_xlabel("Current Density / 電流密度 (A/cm²)", fontdict=font_style)
        ax_b.set_ylabel("Cell Voltage / 電池電壓 (V)", fontdict=font_style)
        ax_b.tick_params(colors='white'); ax_b.grid(True, color='#333', alpha=0.5, linestyle='--')
        st.pyplot(fig_b)

    # 4. 下方診斷指標：字體極大化與中英對照
    st.markdown("### 🔍 Diagnostic Metrics / 診斷數據指標")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    avg_a, avg_b = v_a.mean(), v_b.mean()
    v_drop = avg_a - avg_b
    health_idx = max(0, 100 - (v_drop / avg_a * 250)) 

    m_col1.metric("Health Index / 健康指數", f"{round(health_idx, 1)}%", 
                  delta="Excellent" if health_idx > 90 else "Warning")
    
    m_col2.metric("Voltage Drop / 電壓降", f"{round(v_drop, 3)} V", 
                  delta=f"{round(v_drop/avg_a*100, 1)}%", delta_color="inverse")
    
    m_col3.metric("Baseline Avg / 基準平均", f"{round(avg_a, 2)} V")
    
    m_col4.metric("System Status / 系統狀態", "Healthy / 良好" if health_idx > 85 else "Action / 需檢修")

# ==========================================
# 其他模式介面 (基礎框架)
# ==========================================
else:
    st.title(f"🛠️ {app_mode}")
    st.info("System integration in progress / 系統整合中...")