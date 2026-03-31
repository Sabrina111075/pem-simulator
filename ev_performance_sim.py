# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 1. 頁面基礎配置
st.set_page_config(page_title="TAD-AGE EV Performance & Energy", layout="wide", page_icon="⚡")

# 自定義 CSS 優化字體與容器
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #00d4ff; }
    .stSlider label { color: #ffffff !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

tw_now = datetime.utcnow() + timedelta(hours=8)

# 2. 側邊欄導覽
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "Select System / 選擇模擬系統",
    ["EV Performance (加速與扭矩)", "Energy Efficiency (能源效率分析)", "PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"]
)

# 3. 共享參數設定 (對應 PDF 8EM 能耗模型)
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Vehicle Config / 車輛參數")
bike_mass = st.sidebar.slider("Total Mass / 總重 (kg) [#1]", 100, 400, 180)
motor_eff = st.sidebar.slider("Motor Efficiency / 馬達效率 (%) [#5]", 50, 100, 92)
batt_cap = st.sidebar.slider("Battery Capacity / 電池容量 (Ah) [#4]", 20, 100, 40)

# ==========================================
# Mode A: EV Performance (性能表現展示)
# ==========================================
if app_mode == "EV Performance (加速與扭矩)":
    st.title("⚡ EV Performance Simulator / 電動車性能模擬")
    st.caption(f"V3 Layer 1-2 Focus | Torque Control Logic | {tw_now.strftime('%H:%M:%S')}")
    
    throttle = st.sidebar.slider("Throttle / 油門開度 (%)", 0, 100, 100)
    
    # 物理模型：馬達特性 (恆扭矩與恆功率區間)
    speed_kmh = np.linspace(0, 100, 100)
    base_torque = 45 * (throttle / 100) * (motor_eff / 100)
    torque_curve = [base_torque if v < 45 else base_torque * (45/v) for v in speed_kmh]
    accel = [(t * 5.5 / 0.28 / bike_mass) for t in torque_curve]

    # 優化後的繪圖區
    font_style = {'color': '#ffffff', 'size': 11}
    title_style = {'color': '#00d4ff', 'weight': 'bold', 'size': 13}
    
    col1, col2 = st.columns(2)
    with col1:
        fig_t, ax_t = plt.subplots(dpi=120) # 提升解析度
        fig_t.patch.set_facecolor('#0e1117'); ax_t.set_facecolor('#111111')
        ax_t.plot(speed_kmh, torque_curve, color='#00d4ff', linewidth=3, antialiased=True)
        ax_t.set_title("Torque vs Speed (L1 Motor Control)", fontdict=title_style, pad=15)
        ax_t.set_xlabel("Speed (km/h)", fontdict=font_style, labelpad=10)
        ax_t.set_ylabel("Torque (Nm)", fontdict=font_style, labelpad=10)
        ax_t.tick_params(colors='white', labelsize=9)
        ax_t.grid(True, color='#333', linestyle='--', alpha=0.5)
        st.pyplot(fig_t)

    with col2:
        fig_a, ax_a = plt.subplots(dpi=120)
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(speed_kmh, accel, color='#ff4b4b', linewidth=3, antialiased=True)
        ax_a.set_title("Acceleration Propelling Trend", fontdict={'color': '#ff4b4b', 'weight': 'bold', 'size': 13}, pad=15)
        ax_a.set_xlabel("Speed (km/h)", fontdict=font_style, labelpad=10)
        ax_a.set_ylabel("Accel (m/s²)", fontdict=font_style, labelpad=10)
        ax_a.tick_params(colors='white', labelsize=9)
        ax_a.grid(True, color='#333', linestyle='--', alpha=0.5)
        st.pyplot(fig_a)

    st.success(f"✅ 對應 AUTOSAR SWC: TorqueControl | Peak: {round(max(torque_curve),1)} Nm")

# ==========================================
# Mode B: Energy Efficiency (能源效率分析)
# ==========================================
elif app_mode == "Energy Efficiency (能源效率分析)":
    st.title("📊 Energy Efficiency Analysis / 能源效率與能耗分解")
    st.caption("V3 Layer 3 & 6 | 8EM Energy Decomposition")
    
    # 模擬 8EM 能耗比例數據
    labels = ['Air Drag [#2]', 'Rolling [#3]', 'Motor Loss [#5]', 'Thermal [#8]', 'Others']
    sizes = [25, 15, 10, 5, 45] # 預設分配
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99', '#c2c2f0']
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("8EM Energy Consumption / 能耗分解")
        fig_pie, ax_p = plt.subplots(dpi=120)
        fig_pie.patch.set_facecolor('#0e1117')
        ax_p.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
                 textprops={'color':"w"}, colors=colors, wedgeprops={'edgecolor': '#333'})
        ax_p.axis('equal') 
        st.pyplot(fig_pie)
        
    with c2:
        st.subheader("Battery SoC Trend / 電量趨勢 [#4]")
        # 模擬 SoC 下降曲線
        time_steps = np.arange(0, 60, 1)
        soc_level = 100 - (time_steps * 0.5) # 簡化線性消耗
        fig_soc, ax_s = plt.subplots(dpi=120)
        fig_soc.patch.set_facecolor('#0e1117'); ax_s.set_facecolor('#111111')
        ax_s.plot(time_steps, soc_level, color='#00ff00', linewidth=2)
        ax_s.set_ylim(0, 105); ax_s.set_xlabel("Time (min)"); ax_s.set_ylabel("SoC (%)")
        ax_s.tick_params(colors='white'); ax_s.grid(True, color='#333')
        st.pyplot(fig_soc)

    st.info("💡 此模組對應 V3 Layer 6: 8EM 能耗分解與 Layer 3: BMS SoC 計算")

# ==========================================
# 其他模式保留區 (PEM & Cold Chain)
# ==========================================
elif app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔋 PEM Hydrogen Diagnostic")
    st.info("請將原有的 PEM 診斷代碼貼於此處，邏輯結構已保留。")

else:
    st.title("❄️ Cold Chain Logistics")
    st.info("請將原有的冷鏈物流代碼貼於此處，邏輯結構已保留。")