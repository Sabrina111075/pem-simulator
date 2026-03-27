# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 確保網頁以 UTF-8 處理
import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE Multi-Sim", layout="wide", page_icon="🌐")

# 2. 深度美化 CSS
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

# 時區設定
tw_time = datetime.utcnow() + timedelta(hours=8)

# --- 側邊欄：切換系統 ---
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "Select System / 選擇模擬系統",
    ["PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"]
)

# ==========================================
# 模式 A: PEM 氫能診斷系統
# ==========================================
if app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔬 PEM Hydrogen Diagnostic System / 氫能診斷系統")
    st.caption(f"Status: Running (台北時間): {tw_time.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # 側邊欄參數設定
    st.sidebar.header("🕹️ Control Panel / 參數設定")
    with st.sidebar.expander("📊 Mode A: Baseline / 基準狀態", expanded=True):
        temp_a = st.slider("Temp / 溫度 A (°C)", 20, 100, 60)
        v1_a = st.slider("Ohmic / 歐姆係數 A", 5.0, 25.0, 13.5)
        hum_a = st.slider("Humidity / 溼度 A (%)", 0, 100, 80)
    
    with st.sidebar.expander("🧪 Mode B: Testing / 測試狀態", expanded=True):
        temp_b = st.slider("Temp / 溫度 B (°C)", 20, 100, 80)
        v1_b = st.slider("Ohmic / 歐姆係數 B", 5.0, 25.0, 18.0)
        hum_b = st.slider("Humidity / 溼度 B (%)", 0, 100, 50)

    # 模擬數據
    c = np.linspace(0.1, 2.2, 12)
    v_a = 2.6 - (v1_a/10 * c) - (temp_a/500) - ((100-hum_a)/200.0)
    v_b = 2.6 - (v1_b/10 * c) - (temp_b/500) - ((100-hum_b)/200.0)
    
    col1, col2 = st.columns(2)
    def draw_plot(x, y, title, color):
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#0e1117'); ax.set_facecolor('#111111')
        ax.plot(x, y, color=color, marker='o', linewidth=2)
        ax.set_title(title, color='white'); ax.set_xlabel("Current", color='white'); ax.set_ylabel("Voltage", color='white')
        ax.tick_params(colors='white'); ax.grid(True, color='#444')
        return fig

    col1.pyplot(draw_plot(c, v_a, "Baseline IV", '#00d4ff'))
    col2.pyplot(draw_plot(c, v_b, "Testing IV", '#ff4b4b'))

# ==========================================
# 模式 B: Cold Chain 冷鏈物流模擬
# ==========================================
else:
    st.title("❄️ Cold Chain Logistics Simulator / 冷鏈物流模擬")
    st.caption(f"Status: Monitoring (台北時間): {tw_time.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    st.sidebar.header("📦 Cold Chain Params / 冷鏈參數")
    ambient_t = st.sidebar.slider("Ambient Temp / 環境溫度 (°C)", 25, 45, 32)
    door_open = st.sidebar.checkbox("Door Open Simulator / 開啟箱門模擬")

    # 模擬邏輯
    time_steps = np.arange(0, 12, 1)
    heat_leak = 0.3 * (ambient_t - 5)
    if door_open: heat_leak *= 4
    temp_curve = 5 + heat_leak * (1 - np.exp(-0.2 * time_steps))

    fig_cc, ax_cc = plt.subplots(figsize=(10, 4))
    fig_cc.patch.set_facecolor('#0e1117'); ax_cc.set_facecolor('#111111')
    ax_cc.plot(time_steps, temp_curve, color='#00ffcc', linewidth=3, marker='s')
    ax_cc.axhline(8, color='#ff4b4b', linestyle='--')
    ax_cc.set_title("Temperature Profile", color='white')
    ax_cc.tick_params(colors='white'); ax_cc.grid(True, color='#333')
    st.pyplot(fig_cc)

    st.metric("Current Temp / 當前溫度", f"{round(temp_curve[-1], 2)} °C")