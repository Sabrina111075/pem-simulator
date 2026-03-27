 # -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 1. 頁面配置與深色美化
st.set_page_config(page_title="TAD-AGE Dual-System Platform", layout="wide", page_icon="??")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetric"] {
        background-color: #1a1a1a; padding: 20px; border-radius: 12px; border: 2px solid #444;
    }
    [data-testid="stMetricLabel"] p { color: #FFFFFF !important; font-size: 16px !important; font-weight: bold !important; }
    [data-testid="stMetricValue"] div { color: #00d4ff !important; font-size: 28px !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# 修正為台北時區 (UTC+8)
tw_now = datetime.utcnow() + timedelta(hours=8)

# 2. 側邊欄：導覽切換
st.sidebar.title("?? Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "Select System / 選擇模擬系統",
    ["PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"]
)

# ==========================================
# 模式一：PEM 氫能診斷系統
# ==========================================
if app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("?? PEM Hydrogen Diagnostic System / 氫能診斷系統")
    st.caption(f"Status: Running / 系統運行中 (台北時間): {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # 參數設定
    st.sidebar.header("??? Control Panel / 參數設定")
    with st.sidebar.expander("?? Mode A: Baseline / 基準狀態", expanded=True):
        temp_a = st.slider("Temp / 溫度 A (°C)", 20, 100, 60)
        v1_a = st.slider("Ohmic / 歐姆係數 A", 5.0, 25.0, 13.5)
    
    with st.sidebar.expander("?? Mode B: Testing / 測試狀態", expanded=True):
        temp_b = st.slider("Temp / 溫度 B (°C)", 20, 100, 80)
        v1_b = st.slider("Ohmic / 歐姆係數 B", 5.0, 25.0, 18.0)

    # 氫能計算邏輯
    c = np.linspace(0.1, 2.2, 12)
    v_a = 2.6 - (v1_a/10 * c) - (temp_a/500)
    v_b = 2.6 - (v1_b/10 * c) - (temp_b/500)
    s_a = max(0, min(100, round(100 - (v1_a - 13.5) * 8)))
    s_b = max(0, min(100, round(100 - (v1_b - 13.5) * 8)))

    # 繪圖
    col1, col2 = st.columns(2)
    def quick_plot(x, y, title, color):
        fig, ax = plt.subplots(figsize=(6, 3.5))
        fig.patch.set_facecolor('#0e1117'); ax.set_facecolor('#111111')
        ax.plot(x, y, color=color, marker='o', linewidth=2)
        ax.set_title(title, color='white', fontweight='bold')
        ax.set_xlabel("Current / 電流 (A)", color='white'); ax.set_ylabel("Voltage / 電壓 (V)", color='white')
        ax.tick_params(colors='white'); ax.grid(True, color='#444', linestyle=':')
        return fig

    col1.pyplot(quick_plot(c, v_a, "Baseline IV Curve", '#00d4ff'))
    col2.pyplot(quick_plot(c, v_b, "Testing IV Curve", '#ff4b4b'))

    # 指標
    m1, m2, m3 = st.columns(3)
    m1.metric("Health Index A / 健康指標 A", f"{s_a}%")
    m2.metric("Health Index B / 健康指標 B", f"{s_b}%", delta=f"{s_b - s_a}%")
    m3.metric("Avg. Volt Drop / 平均壓降", f"{round(np.mean(v_a - v_b), 3)} V")

# ==========================================
# 模式二：Cold Chain 冷鏈物流模擬
# ==========================================
else:
    st.title("?? Cold Chain Logistics Simulator / 冷鏈物流模擬")
    st.caption(f"Status: Monitoring / 監測中 (台北時間): {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # 冷鏈專用參數
    st.sidebar.header("?? Cold Chain Params / 冷鏈參數")
    ambient_t = st.sidebar.slider("Ambient Temp / 環境溫度 (°C)", 20, 45, 30)
    insulation = st.sidebar.select_slider("Insulation / 隔熱等級", options=["Low", "Medium", "High"], value="Medium")
    door_open = st.sidebar.checkbox("Door Open / 開啟箱門模擬")

    # 模擬冷鏈熱動力學曲線
    time_h = np.linspace(0, 10, 50)
    k = {"Low": 0.5, "Medium": 0.3, "High": 0.1}[insulation]
    heat_gain = k * (ambient_t - 5) 
    if door_open: heat_gain *= 4  # 開門時熱交換率劇增
    
    # 溫度曲線模擬 (簡化模型)
    temp_profile = 5 + heat_gain * (1 - np.exp(-0.2 * time_h)) + np.random.normal(0, 0.2, 50)

    # 繪製冷鏈趨勢圖
    fig_cc, ax_cc = plt.subplots(figsize=(12, 4))
    fig_cc.patch.set_facecolor('#0e1117'); ax_cc.set_facecolor('#111111')
    ax_cc.plot(time_h, temp_profile, color='#00ffcc', linewidth=3, label="Box Temp")
    ax_cc.axhline(8, color='#ff4b4b', linestyle='--', label="Alert Limit (8°C)")
    ax_cc.fill_between(time_h, 2, 8, color='#00ffcc', alpha=0.1, label="Safe Zone (2-8°C)")
    
    ax_cc.set_title("Temperature Trend / 溫度時序變動圖", color='white', fontweight='bold')
    ax_cc.set_xlabel("Time / 運輸時間 (Hours)", color='white'); ax_cc.set_ylabel("Temp / 溫度 (°C)", color='white')
    ax_cc.legend(); ax_cc.tick_params(colors='white'); ax_cc.grid(True, color='#333')
    st.pyplot(fig_cc)

    # 冷鏈指標
    c1, c2, c3 = st.columns(3)
    curr_t = round(temp_profile[-1], 2)
    c1.metric("Current Temp / 當前庫溫", f"{curr_t} °C")
    c2.metric("Stability / 穩定性評分", "Excellent" if curr_t < 7 else "Risk", delta="-12% Risk" if curr_t > 8 else "Stable")
    c3.metric("Heat Leak / 熱損耗率", f"{round(heat_gain, 2)} °C/h")

    if curr_t > 8:
        st.error(f"?? ALERT / 斷鏈警告：當前溫度 ({curr_t}°C) 已超出疫苗安全範圍 (8°C)！")
    else:
        st.success("?? NORMAL / 運作正常：溫度維持在安全區間。")