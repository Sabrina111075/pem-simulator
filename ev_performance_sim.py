import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# 設定頁面
st.set_page_config(page_title="TAD-AGE EV Performance", layout="wide")

# 側邊欄導覽
st.sidebar.title("🚀 Navigation / 系統導覽")
app_mode = st.sidebar.selectbox(
    "Select System / 選擇模擬系統",
    ["EV Performance (加速與扭矩)", "PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)"]
)

# --- 根據 PDF V3 架構實作的新模組 ---
if app_mode == "EV Performance (加速與扭矩)":
    st.title("⚡ EV Performance Simulator / 電動車性能模擬")
    st.caption("基於 V3 控制架構 - Layer 1 & 2")
    
    # 側邊欄參數 (對應 PDF 8EM 模型)
    st.sidebar.header("⚙️ Vehicle Specs (#1, #5)")
    bike_mass = st.sidebar.slider("Total Mass / 總重 (kg) [#1]", 100, 400, 180)
    motor_eff = st.sidebar.slider("Motor Efficiency / 馬達效率 (%) [#5]", 50, 100, 92)
    throttle = st.sidebar.slider("Throttle Opening / 油門開度 (%)", 0, 100, 100)

    # 模擬馬達扭矩特性 (Layer 1: 扭矩生成)
    speed_kmh = np.linspace(0, 100, 100)
    # 低速時維持恆扭矩，超過特定速度後功率受限
    base_torque = 45 * (throttle / 100) * (motor_eff / 100)
    torque_curve = [base_torque if v < 45 else base_torque * (45/v) for v in speed_kmh]
    
    # 顯示圖表
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(speed_kmh, torque_curve, color='#00d4ff', linewidth=3, label="Torque (Nm)")
    ax.set_title("Torque vs Speed Curve (V3 L1 Motor Control)", color='white')
    ax.set_xlabel("Speed (km/h)")
    ax.set_ylabel("Torque (Nm)")
    ax.grid(True, alpha=0.3)
    
    # 設定圖表深色風格以符合現有網頁
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#1e2130')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    
    st.pyplot(fig)

    # 關鍵指標對應 AUTOSAR SWC
    c1, c2, c3 = st.columns(3)
    c1.metric("Peak Torque", f"{round(max(torque_curve), 1)} Nm")
    c2.metric("SWC Mapping", "TorqueControl")
    c3.metric("8EM Ref", "#1, #5, #8")

# --- 保留原本功能的佔位符 (妳之後可以把舊代碼貼過來) ---
elif app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔋 PEM Hydrogen Diagnostic / 氫能診斷")
    st.info("此處為原有功能，已在測試版中保留邏輯空間。")

elif app_mode == "Cold Chain (冷鏈物流)":
    st.title("❄️ Cold Chain Logistics / 冷鏈物流")
    st.info("此處為原有功能，已在測試版中保留邏輯空間。")