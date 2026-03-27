# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 1. 頁面基礎配置
st.set_page_config(page_title="TAD-AGE Multi-Sim Pro", layout="wide", page_icon="🌐")

# 2. 工業深色風 CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetric"] {
        background-color: #1a1a1a; padding: 20px; border-radius: 12px; border: 2px solid #444;
    }
    [data-testid="stMetricLabel"] p { color: #FFFFFF !important; font-size: 16px !important; }
    [data-testid="stMetricValue"] div { color: #00d4ff !important; font-size: 28px !important; }
    </style>
    """, unsafe_allow_html=True)

tw_now = datetime.utcnow() + timedelta(hours=8)

# --- 側邊欄：切換系統 ---
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "選擇模擬系統 / Select System",
    ["PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"]
)

# ==========================================
# 模式 A：PEM 氫能診斷系統
# ==========================================
if app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔬 PEM Hydrogen Diagnostic System / 氫能診斷系統")
    st.caption(f"Status: Running (台北時間): {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    st.sidebar.header("🕹️ Control Panel / 參數設定")
    with st.sidebar.expander("📊 Mode A: Baseline / 基準狀態", expanded=True):
        temp_a = st.slider("Temp / 溫度 A (°C)", 20, 100, 60)
        v1_a = st.slider("Ohmic / 歐姆係數 A", 5.0, 25.0, 13.5)
        hum_a = st.slider("Humidity / 溼度 A (%)", 0, 100, 80)
    
    with st.sidebar.expander("🧪 Mode B: Testing / 測試狀態", expanded=True):
        temp_b = st.slider("Temp / 溫度 B (°C)", 20, 100, 80)
        v1_b = st.slider("Ohmic / 歐姆係數 B", 5.0, 25.0, 18.0)
        hum_b = st.slider("Humidity / 溼度 B (%)", 0, 100, 50)

    # IV 曲線邏輯
    def get_pem_data(t, v, h):
        c_pts = np.linspace(0.1, 2.2, 12)
        v_pts = 2.6 - (v/10 * c_pts) - (t/500) - ((100-h)/200.0)
        score = max(0, min(100, round(100 - (v - 13.5) * 8 - (t - 60) * 1.5)))
        return c_pts, v_pts, score

    c_pts, v_a, s_a = get_pem_data(temp_a, v1_a, hum_a)
    _, v_b, s_b = get_pem_data(temp_b, v1_b, hum_b)

    col1, col2 = st.columns(2)
    def draw_pem_plot(x, y, color, title):
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#0e1117'); ax.set_facecolor('#111111')
        ax.plot(x, y, color=color, marker='o', linewidth=3)
        ax.set_title(title, color='white', fontweight='bold')
        ax.set_xlabel("Current (A)", color='white'); ax.set_ylabel("Voltage (V)", color='white')
        ax.tick_params(colors='white'); ax.set_ylim(0, 3); ax.grid(True, color='#444')
        return fig

    col1.pyplot(draw_pem_plot(c_pts, v_a, '#00d4ff', "Baseline IV Curve"))
    col2.pyplot(draw_pem_plot(c_pts, v_b, '#ff4b4b', "Testing IV Curve"))

    m1, m2, m3 = st.columns(3)
    m1.metric("Health Index A", f"{s_a}%")
    m2.metric("Health Index B", f"{s_b}%", delta=f"{s_b - s_a}%")
    m3.metric("Avg. Volt Drop", f"{round(np.mean(v_a - v_b), 3)} V")

# ==========================================
# 模式 B：Cold Chain 冷鏈物流 (擴充品項版)
# ==========================================
else:
    st.title("❄️ Cold Chain Logistics Simulator / 冷鏈物流模擬")
    st.caption(f"TAD-AGE Viskovatov Engine Active | 台北時間: {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # 側邊欄：多品項物流參數
    st.sidebar.header("📦 物流參數設定")
    cargo_type = st.sidebar.selectbox(
        "貨物類型 / Cargo Type",
        [
            "超低溫冷凍 (-18 ~ -25°C)", 
            "醫藥品/疫苗 (2 ~ 8°C)", 
            "生鮮肉類/海鮮 (0 ~ 4°C)", 
            "乳製品/蛋類 (0 ~ 7°C)",
            "高級花卉 (8 ~ 12°C)",
            "工業精密化學品 (5 ~ 15°C)",
            "巧克力/恆溫倉 (15 ~ 18°C)"
        ]
    )
    
    thresholds = {
        "超低溫冷凍 (-18 ~ -25°C)": (-25, -18),
        "醫藥品/疫苗 (2 ~ 8°C)": (2, 8),
        "生鮮肉類/海鮮 (0 ~ 4°C)": (0, 4),
        "乳製品/蛋類 (0 ~ 7°C)": (0, 7),
        "高級花卉 (8 ~ 12°C)": (8, 12),
        "工業精密化學品 (5 ~ 15°C)": (5, 15),
        "巧克力/恆溫倉 (15 ~ 18°C)": (15, 18)
    }
    t_min, t_max = thresholds[cargo_type]

    ambient_t = st.sidebar.slider("環境溫度 (°C)", 20, 45, 32)
    door_open = st.sidebar.checkbox("開啟箱門模擬")

    # 模擬數據與 Viskovatov 預測 (處理負溫情況)
    time_h = np.arange(0, 15, 1)
    k = 0.3 if not door_open else 0.9
    start_temp = t_min + 1
    obs = start_temp + k * (ambient_t - start_temp) * (1 - np.exp(-0.2 * time_h[:12])) + np.random.normal(0, 0.2, 12)
    
    # Viskovatov 趨勢擬合
    slope = (obs[-1] - obs[-3]) / 2
    pred = [obs[-1] + slope * i * 1.1 for i in range(1, 4)]
    full_temp = np.concatenate([obs, pred])

    # 繪圖
    fig_cc, ax_cc = plt.subplots(figsize=(10, 4.5))
    fig_cc.patch.set_facecolor('#0e1117'); ax_cc.set_facecolor('#111111')
    ax_cc.axhspan(t_min, t_max, color='green', alpha=0.1, label='Safe Zone')
    ax_cc.plot(time_h[:12], obs, color='#00ffcc', linewidth=3, marker='o', label='Observed')
    ax_cc.plot(time_h[11:], full_temp[11:], color='#ffaa00', linestyle='--', linewidth=3, label='Viskovatov Prediction')
    
    ax_cc.set_title(f"Target: {cargo_type}", color='white', fontweight='bold')
    ax_cc.set_ylabel("Temperature (°C)", color='white'); ax_cc.tick_params(colors='white')
    ax_cc.legend(facecolor='#1a1a1a', labelcolor='white'); ax_cc.grid(True, color='#333')
    st.pyplot(fig_cc)

    # 預警指標
    curr_t, next_t = round(obs[-1], 2), round(pred[-1], 2)
    c1, c2, c3 = st.columns(3)
    c1.metric("當前庫溫", f"{curr_t} °C")
    c2.metric("3H 預測", f"{next_t} °C", delta=f"{round(next_t-curr_t, 2)}°C")
    
    if next_t > t_max:
        st.warning(f"⚠️ **TAD-AGE 預判**：預計 3 小時後將突破 {t_max}°C 門檻！")
    elif curr_t > t_max:
        st.error(f"🚨 **斷鏈警報**：當前溫度已超標！")
    else:
        st.success(f"✅ {cargo_type} 溫控運作正常。")

st.sidebar.markdown("---")
st.sidebar.info("TAD-AGE Multi-Sim v2.2")