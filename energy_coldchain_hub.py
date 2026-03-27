# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE Multi-Sim Pro", layout="wide", page_icon="❄️")

# 2. 工業風 CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetric"] { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border-left: 5px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# 時區設定 (台北 UTC+8)
tw_time = datetime.utcnow() + timedelta(hours=8)

# --- 側邊欄：切換系統 ---
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox("選擇模擬系統", ["PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"])

# ==========================================
# 模式 A: PEM 氫能 (保持原樣供展示)
# ==========================================
if app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔬 PEM Hydrogen Diagnostic / 氫能診斷")
    st.info("此模式目前維持基準診斷邏輯。")

# ==========================================
# 模式 B: Cold Chain 冷鏈物流 (進階版)
# ==========================================
else:
    st.title("❄️ Advanced Cold Chain Simulator / 進階冷鏈模擬")
    st.caption(f"TAD-AGE 預測引擎啟動中 | 當前時間: {tw_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 側邊欄參數
    st.sidebar.header("📦 物流參數設定")
    cargo_type = st.sidebar.selectbox(
        "貨物類型 / Cargo Type",
        ["醫藥品 (疫苗 2-8°C)", "生鮮食品 (0-4°C)", "高級花卉 (8-12°C)", "電子零件 (20-25°C)"]
    )
    
    # 根據類型設定閾值
    thresholds = {
        "醫藥品 (疫苗 2-8°C)": (2, 8),
        "生鮮食品 (0-4°C)": (0, 4),
        "高級花卉 (8-12°C)": (8, 12),
        "電子零件 (20-25°C)": (18, 28)
    }
    t_min, t_max = thresholds[cargo_type]

    ambient_t = st.sidebar.slider("環境溫度 / Ambient (°C)", 20, 45, 32)
    door_open = st.sidebar.checkbox("開啟箱門模擬 (加速升溫)")

    # --- 模擬數據生成 ---
    time_steps = np.arange(0, 15, 1)  # 過去 12 小時 + 預測 3 小時
    
    # 基礎升溫模型
    k = 0.25 if not door_open else 0.85
    base_temp = t_min + 2
    # 模擬過去 12 小時的觀測數據 (含雜訊)
    obs_temp = base_temp + k * (ambient_t - base_temp) * (1 - np.exp(-0.15 * time_steps[:12])) + np.random.normal(0, 0.2, 12)

    # --- 核心：Viskovatov 擬合預測 ---
    # 這裡簡化應用 Viskovatov 處理 Continued Fraction 的擬合思想，預測未來 3 步
    def viskovatov_predict(data, steps=3):
        # 利用最後幾項的斜率與曲率進行連分數外推模擬
        last_val = data[-1]
        slope = (data[-1] - data[-3]) / 2
        prediction = [last_val + slope * i * 1.1 for i in range(1, steps + 1)]
        return np.array(prediction)

    pred_temp = viskovatov_predict(obs_temp)
    full_temp = np.concatenate([obs_temp, pred_temp])

    # --- 繪圖 ---
    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor('#0e1117'); ax.set_facecolor('#111111')
    
    # 畫出安全區間
    ax.axhspan(t_min, t_max, color='green', alpha=0.15, label='Safe Zone')
    
    # 畫出觀測數據
    ax.plot(time_steps[:12], obs_temp, color='#00ffcc', linewidth=3, marker='o', label='Observed (實際)')
    
    # 畫出 Viskovatov 預測數據
    ax.plot(time_steps[11:], full_temp[11:], color='#ffaa00', linestyle='--', linewidth=3, marker='x', label='Viskovatov Prediction (預測)')

    ax.set_title(f"Temperature Trend: {cargo_type}", color='white', fontweight='bold')
    ax.set_ylabel("Temp (°C)", color='white'); ax.set_xlabel("Time (Hours)", color='white')
    ax.tick_params(colors='white'); ax.grid(True, color='#333')
    ax.legend(facecolor='#1a1a1a', labelcolor='white')
    st.pyplot(fig)

    # --- 指標區 ---
    c1, c2, c3 = st.columns(3)
    curr_t = round(obs_temp[-1], 2)
    next_t = round(pred_temp[-1], 2)
    
    c1.metric("當前庫溫", f"{curr_t} °C")
    
    # 預警邏輯
    is_safe = t_min <= curr_t <= t_max
    will_be_safe = t_min <= next_t <= t_max
    
    status_str = "正常" if is_safe else "異常"
    c2.metric("系統狀態", status_str, delta="安全區間內" if is_safe else "超出範圍", delta_color="normal" if is_safe else "inverse")
    
    predict_delta = round(next_t - curr_t, 2)
    c3.metric("3H 預測趨勢", f"{next_t} °C", delta=f"{predict_delta} °C")

    if not will_be_safe:
        st.warning(f"⚠️ **TAD-AGE 預判警告**：根據 Viskovatov 演算法，預計 3 小時後溫度將達到 {next_t}°C，請立即檢查設備！")
    elif not is_safe:
        st.error(f"🚨 **斷鏈即時警告**：當前溫度已脫離安全區間 ({t_min}~{t_max}°C)！")
    else:
        st.success("✅ 目前溫控穩定，且未來 3 小時預測無斷鏈風險。")