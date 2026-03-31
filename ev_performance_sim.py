# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE Hydrogen Diagnostic", layout="wide", page_icon="🔋")

# 全局變數
tw_now = datetime.utcnow() + timedelta(hours=8)
title_style = {'color': '#00d4ff', 'weight': 'bold', 'size': 14}
red_title_style = {'color': '#ff4b4b', 'weight': 'bold', 'size': 14}

# CSS: 強化指標卡片
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #1c2128;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
    }
    label[data-testid="stMetricLabel"] { font-size: 18px !important; color: #adb5bd !important; }
    div[data-testid="stMetricValue"] { font-size: 40px !important; color: #00d4ff !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 側邊欄參數
st.sidebar.title("🚀 Navigation")
app_mode = st.sidebar.selectbox("Select System", ["PEM Hydrogen (氫能診斷)"])

if app_mode == "PEM Hydrogen (氫能診斷)":
    with st.sidebar:
        st.markdown("---")
        with st.expander("🟦 Baseline / 基準狀態", expanded=True):
            temp_a = st.slider("Temp A", 40, 90, 60, key="ta")
            ohmic_a = st.slider("Ohmic A", 10.0, 30.0, 13.5, key="oa")
            hum_a = st.slider("Humidity A", 20, 100, 80, key="ha")
        with st.expander("🟥 Testing / 測試狀態", expanded=True):
            temp_b = st.slider("Temp B", 40, 90, 75, key="tb")
            ohmic_b = st.slider("Ohmic B", 10.0, 30.0, 22.0, key="ob")
            hum_b = st.slider("Humidity B", 20, 100, 60, key="hb")

    # 3. 主畫面
    st.title("🔋 PEM Hydrogen Diagnostic System")
    st.caption(f"Analysis Time: {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # 物理模型
    current_density = np.linspace(0.01, 2.0, 50)
    def calc_v(temp, ohmic, hum):
        return 1.22 - (0.28 - temp/550) * np.log1p(current_density * 10) - (ohmic/1000 * current_density) * (1.2 - hum/100)

    v_a = calc_v(temp_a, ohmic_a, hum_a)
    v_b = calc_v(temp_b, ohmic_b, hum_b)

    # 4. 圖表區：刪除所有可能產生豆腐字的內部標籤
    col_fig1, col_fig2 = st.columns(2)
    
    with col_fig1:
        fig_a, ax_a = plt.subplots(dpi=130)
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(current_density, v_a, color='#00d4ff', linewidth=4)
        ax_a.set_title("Baseline IV Characteristic (基準)", fontdict=title_style, pad=20)
        # 刪除標籤以去除豆腐字
        ax_a.set_xlabel(""); ax_a.set_ylabel("") 
        ax_a.tick_params(colors='white'); ax_a.grid(True, color='#333', alpha=0.5, linestyle='--')
        st.pyplot(fig_a)

    with col_fig2:
        fig_b, ax_b = plt.subplots(dpi=130)
        fig_b.patch.set_facecolor('#0e1117'); ax_b.set_facecolor('#111111')
        ax_b.plot(current_density, v_b, color='#ff4b4b', linewidth=4)
        ax_b.set_title("Testing IV Characteristic (測試)", fontdict=red_title_style, pad=20)
        # 刪除標籤以去除豆腐字
        ax_b.set_xlabel(""); ax_b.set_ylabel("")
        ax_b.tick_params(colors='white'); ax_b.grid(True, color='#333', alpha=0.5, linestyle='--')
        st.pyplot(fig_b)

    # 5. 指標區：簡化指標 + 下降紅字警示
    st.markdown("### 🔍 Diagnostic Metrics / 診斷指標")
    m1, m2, m3 = st.columns(3)
    
    avg_a, avg_b = v_a.mean(), v_b.mean()
    v_drop = avg_a - avg_b
    hi_a = 100.0
    hi_b = max(0, 100 - (v_drop / avg_a * 250)) 

    # 指標 A
    m1.metric("Health Index A / 健康指數 A", f"{round(hi_a, 1)}%")
    
    # 指標 B：delta_color="inverse" 會讓下降百分比顯示為紅字
    m2.metric(
        label="Health Index B / 健康指數 B", 
        value=f"{round(hi_b, 1)}%", 
        delta=f"-{round(100-hi_b, 1)}%", 
        delta_color="inverse"
    )
    
    # 指標 C
    m3.metric("Avg. Volt Drop / 平均壓降", f"{round(v_drop, 3)} V")