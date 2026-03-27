# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 1. Page Configuration / 頁面配置
st.set_page_config(page_title="TAD-AGE Multi-Sim Pro", layout="wide", page_icon="🌐")

# 2. Industrial Dark Theme CSS / 工業深色風美化
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetric"] {
        background-color: #1a1a1a; padding: 20px; border-radius: 12px; border: 2px solid #444;
    }
    [data-testid="stMetricLabel"] p { color: #FFFFFF !important; font-size: 16px !important; font-weight: bold; }
    [data-testid="stMetricValue"] div { color: #00d4ff !important; font-size: 28px !important; }
    </style>
    """, unsafe_allow_html=True)

tw_now = datetime.utcnow() + timedelta(hours=8)

# --- Navigation Sidebar / 側邊欄導覽 ---
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "Select System / 選擇模擬系統",
    ["PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"]
)

# ==========================================
# Mode A: PEM Hydrogen System / 氫能診斷系統
# ==========================================
if app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔬 PEM Hydrogen Diagnostic System / 氫能診斷系統")
    st.caption(f"Status: Running | Time (Taipei): {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    st.sidebar.header("🕹️ Control Panel / 參數設定")
    with st.sidebar.expander("📊 Mode A: Baseline / 基準狀態", expanded=True):
        temp_a = st.slider("Temperature / 溫度 A (°C)", 20, 100, 60)
        v1_a = st.slider("Ohmic Coeff / 歐姆係數 A", 5.0, 25.0, 13.5)
        hum_a = st.slider("Humidity / 溼度 A (%)", 0, 100, 80)
    
    with st.sidebar.expander("🧪 Mode B: Testing / 測試狀態", expanded=True):
        temp_b = st.slider("Temperature / 溫度 B (°C)", 20, 100, 80)
        v1_b = st.slider("Ohmic Coeff / 歐姆係數 B", 5.0, 25.0, 18.0)
        hum_b = st.slider("Humidity / 溼度 B (%)", 0, 100, 50)

    # PEM Logic / 氫能邏輯
    def get_pem_data(t, v, h):
        c_pts = np.linspace(0.1, 2.2, 12)
        v_pts = 2.6 - (v/10 * c_pts) - (t/500) - ((100-h)/200.0)
        score = max(0, min(100, round(100 - (v - 13.5) * 8 - (t - 60) * 1.5)))
        return c_pts, v_pts, score

    c_pts, v_a, s_a = get_pem_data(temp_a, v1_a, hum_a)
    _, v_b, s_b = get_pem_data(temp_b, v1_b, hum_b)

    # Plotting / 繪圖區 (使用英文避免方塊字)
    col1, col2 = st.columns(2)
    def draw_pem_plot(x, y, color, title):
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#0e1117'); ax.set_facecolor('#111111')
        ax.plot(x, y, color=color, marker='o', linewidth=3)
        ax.set_title(title, color='white', fontweight='bold', fontsize=14)
        ax.set_xlabel("Current (A)", color='white'); ax.set_ylabel("Voltage (V)", color='white')
        ax.tick_params(colors='white'); ax.set_ylim(0, 3); ax.grid(True, color='#444')
        return fig

    col1.pyplot(draw_pem_plot(c_pts, v_a, '#00d4ff', "Baseline IV Curve"))
    col2.pyplot(draw_pem_plot(c_pts, v_b, '#ff4b4b', "Testing IV Curve"))

    # Metrics / 指標區 (雙語)
    m1, m2, m3 = st.columns(3)
    m1.metric("Health Index A / 健康指數", f"{s_a}%")
    m2.metric("Health Index B / 健康指數", f"{s_b}%", delta=f"{s_b - s_a}%")
    m3.metric("Avg. Volt Drop / 平均壓降", f"{round(np.mean(v_a - v_b), 3)} V")

# ==========================================
# Mode B: Cold Chain Logistics / 冷鏈物流模擬
# ==========================================
else:
    st.title("❄️ Cold Chain Logistics Simulator / 冷鏈物流模擬")
    st.caption(f"TAD-AGE Viskovatov Engine | Time (Taipei): {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # Sidebar: Cargo Settings / 側邊欄物流參數 (雙語)
    st.sidebar.header("📦 Cargo Settings / 物流參數")
    cargo_options = {
        "Ultra-Low Frozen / 超低溫冷凍 (-25~-18°C)": (-25, -18),
        "Vaccine/Medicine / 醫藥疫苗 (2~8°C)": (2, 8),
        "Fresh Meat/Seafood / 生鮮海鮮 (0~4°C)": (0, 4),
        "Dairy/Eggs / 乳製品 (0~7°C)": (0, 7),
        "Floral/Flowers / 高級花卉 (8~12°C)": (8, 12),
        "Precision Chemicals / 精密化學品 (5~15°C)": (5, 15),
        "Chocolate/Confectionery / 巧克力 (15~18°C)": (15, 18)
    }
    cargo_type = st.sidebar.selectbox("Select Cargo / 選擇貨物類型", list(cargo_options.keys()))
    t_min, t_max = cargo_options[cargo_type]

    ambient_t = st.sidebar.slider("Ambient Temp / 環境溫度 (°C)", 20, 45, 32)
    door_open = st.sidebar.checkbox("Door Open Simulator / 開啟箱門模擬")

    # Simulation Logic / 模擬邏輯
    time_h = np.arange(0, 15, 1)
    k = 0.3 if not door_open else 0.9
    start_temp = t_min + 1
    obs = start_temp + k * (ambient_t - start_temp) * (1 - np.exp(-0.2 * time_h[:12])) + np.random.normal(0, 0.2, 12)
    
    # Viskovatov Trend Fitting / 趨勢擬合
    slope = (obs[-1] - obs[-3]) / 2
    pred = [obs[-1] + slope * i * 1.1 for i in range(1, 4)]
    full_temp = np.concatenate([obs, pred])

    # Plotting / 繪圖 (標題改英文避免亂碼)
    fig_cc, ax_cc = plt.subplots(figsize=(10, 4.5))
    fig_cc.patch.set_facecolor('#0e1117'); ax_cc.set_facecolor('#111111')
    ax_cc.axhspan(t_min, t_max, color='green', alpha=0.15, label='Safe Zone')
    ax_cc.plot(time_h[:12], obs, color='#00ffcc', linewidth=3, marker='o', label='Observed Data')
    ax_cc.plot(time_h[11:], full_temp[11:], color='#ffaa00', linestyle='--', linewidth=3, label='Viskovatov Prediction')
    
    ax_cc.set_title(f"Target Control: {cargo_type.split(' / ')[0]}", color='white', fontweight='bold', fontsize=14)
    ax_cc.set_ylabel("Temp (°C)", color='white'); ax_cc.set_xlabel("Time (Hours)", color='white')
    ax_cc.tick_params(colors='white'); ax_cc.grid(True, color='#333')
    ax_cc.legend(facecolor='#1a1a1a', labelcolor='white')
    st.pyplot(fig_cc)

    # Dashboard Metrics / 數據看板
    curr_t, next_t = round(obs[-1], 2), round(pred[-1], 2)
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Temp / 當前庫溫", f"{curr_t} °C")
    c2.metric("3H Prediction / 3H 預測", f"{next_t} °C", delta=f"{round(next_t-curr_t, 2)}°C")
    
    # Dual-Language Alerts / 雙語警告
    if next_t > t_max:
        st.warning(f"⚠️ **TAD-AGE Prediction**: Temp expected to exceed {t_max}°C in 3 hours!\n\n**預判警告**：預計 3 小時後將突破 {t_max}°C 門檻！")
    elif curr_t > t_max:
        st.error(f"🚨 **Breakdown Alert**: Current temp out of range!\n\n**即時警報**：當前溫度已超標！")
    else:
        st.success(f"✅ **Stable**: {cargo_type.split(' / ')[1]} control is normal.\n\n**穩定運作**：{cargo_type.split(' / ')[1]} 溫控正常。")

st.sidebar.markdown("---")
st.sidebar.info("TAD-AGE Multi-Sim v2.3 (Dual Language)")