import streamlit as st
import numpy as np
import pandas as pd
from scipy import signal

# ==========================================
# 1. MEMS Digital Library 欄位標準化雛形
# ==========================================
# 模擬從資料庫讀取元件規格參數 (以雜訊密度與零偏為主)
SENSOR_DB = {
    "BOSCH_BMI270": {
        "accel_noise_density": 0.00015,  # g/√Hz (簡化示意)
        "gyro_noise_density": 0.007,     # dps/√Hz
        "accel_bias": 0.02,              # g
        "gyro_bias": 0.1                 # dps
    },
    "TDK_ICM-42688-P": {
        "accel_noise_density": 0.00007,  # g/√Hz (規格較低噪)
        "gyro_noise_density": 0.0028,    # dps/√Hz
        "accel_bias": 0.01,              # g
        "gyro_bias": 0.05                # dps
    }
}

st.set_page_config(page_title="MEMS Simulation MVP", layout="wide")
st.title("🛸 MEMS Intelligence Platform - 極簡模擬平台 (MVP)")
st.caption("基於 Windows 7 本地開發驗證 ➔ GitHub / Streamlit 3.11 雲端部署架構")

# ==========================================
# 2. 側邊欄控制：選擇感測器與調整環境參數
# ==========================================
st.sidebar.header("🛠️ 平台參數設定")

# 選擇感測器型號
selected_sensor = st.sidebar.selectbox("選擇 MEMS 感測器元件", list(SENSOR_DB.keys()))
spec = SENSOR_DB[selected_sensor]

# 環境與模擬參數設定
st.sidebar.subheader("🌍 環境與時序設定")
fs = st.sidebar.slider("取樣頻率 ODR (Hz)", min_value=50, max_value=200, value=100, step=10)
duration = st.sidebar.slider("模擬時長 (秒)", min_value=2, max_value=10, value=5)
motion_freq = st.sidebar.slider("虛擬運動頻率 (Hz)", min_value=0.5, max_value=3.0, value=1.0, step=0.5)

# 誤差注入微調 (允許使用者手動放大誤差)
st.sidebar.subheader("⚠️ 誤差注入乘數")
noise_multiplier = st.sidebar.slider("雜訊放大倍率", min_value=1.0, max_value=10.0, value=1.0, step=0.5)
drift_multiplier = st.sidebar.slider("隨機遊走(漂移)放大倍率", min_value=0.0, max_value=5.0, value=1.0, step=0.5)

# 互補濾波器參數
st.sidebar.subheader("🧪 融合引擎參數")
alpha = st.sidebar.slider("互補濾波器權重 (Alpha)", min_value=0.80, max_value=0.99, value=0.96, step=0.01)

# ==========================================
# 3. 核心數學模型與資料流計算
# ==========================================
# 時間軸生成
t = np.linspace(0, duration, int(fs * duration), endpoint=False)
dt = 1.0 / fs

# A. 生成理想軌跡 (運動幾何模型)
# 假設平台在做局部的俯仰角 (Pitch) 正弦擺動
true_angle = 20.0 * np.sin(2 * np.pi * motion_freq * t)  # 理想角度 (度)

# 根據物理公式求出理想的角速度 (陀螺儀輸入) 與 加速度 (加速度計輸入)
# 角速度為角度的一階微分
true_gyro = 20.0 * (2 * np.pi * motion_freq) * np.cos(2 * np.pi * motion_freq * t) 
# 簡化加速度計模型：重力加速度 g 在傾斜角下的分量 (加上運動加速度的一階近似)
true_accel = np.sin(np.radians(true_angle)) 

# B. 動態模型與誤差注入 (Error Injection)
# 1. 陀螺儀誤差注入：零偏 + 白雜訊 + 隨機遊走(漂移)
gyro_white_noise = np.random.normal(0, spec["gyro_noise_density"] * np.sqrt(fs), len(t)) * noise_multiplier
gyro_drift = np.cumsum(np.random.normal(0, 0.01, len(t))) * drift_multiplier # 隨機遊走
sim_gyro = true_gyro + spec["gyro_bias"] + gyro_white_noise + gyro_drift

# 2. 加速度計誤差注入：零偏 + 白雜訊
accel_white_noise = np.random.normal(0, spec["accel_noise_density"] * np.sqrt(fs), len(t)) * noise_multiplier
sim_accel = true_accel + spec["accel_bias"] + accel_white_noise

# C. 融合引擎 (Sensor Fusion Engine) - 一階互補濾波器
# 透過加速度計估算角度： theta_accel = arcsin(ax)
# 為了避免雜訊干擾，使用 clip 限制邊界
est_angle_accel = np.degrees(np.arcsin(np.clip(sim_accel, -1.0, 1.0)))

est_angle = np.zeros(len(t))
est_angle[0] = est_angle_accel[0]  # 初始狀態

for k in range(1, len(t)):
    # 互補濾波公式： 高通(陀螺儀積分) + 低通(加速度計基準)
    est_angle[k] = alpha * (est_angle[k-1] + sim_gyro[k] * dt) + (1 - alpha) * est_angle_accel[k]

# ==========================================
# 4. Streamlit 前端數據看板呈現
# ==========================================
st.subheader(f"📊 {selected_sensor} 元件模擬與動態融合結果")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**1. 原始感測器輸出 (含注入誤差與雜訊)**")
    # 將資料包裝成 DataFrame 供圖表讀取
    sensor_df = pd.DataFrame({
        "時間(秒)": t,
        "陀螺儀輸出(dps)": sim_gyro,
        "理想角速度(dps)": true_gyro,
        "加速度計輸出(g)": sim_accel
    }).set_index("時間(秒)")
    
    st.line_chart(sensor_df[["陀螺儀輸出(dps)", "理想角速度(dps)"]])
    st.caption("💡 藍線（模擬輸出）圍繞著紅線（真實運動）波動，並隨著時間產生基線漂移（隨機遊走）。")

with col2:
    st.markdown("**2. 狀態估計與融合輸出 (姿態解算解碼)**")
    fusion_df = pd.DataFrame({
        "時間(秒)": t,
        "真實角度(度)": true_angle,
        "單靠加速度計估算(度)": est_angle_accel,
        "互補濾波融合角度(度)": est_angle
    }).set_index("時間(秒)")
    
    st.line_chart(fusion_df)
    st.caption("💡 綠線為融合後的角度。您可以試著調整側邊欄的 Alpha 值，觀察它是如何平衡陀螺儀的動態響應與加速度計的長期穩定。")

# 顯示當前元件的標準化資料架構 (Digital Library)
st.divider()
st.subheader("📋 平台底層標準化規格數據 (Digital Library View)")
st.json({
    "Sensor_ID": f"CrystalMachine_{selected_sensor}_V1.0",
    "Manufacturer": selected_sensor.split("_")[0],
    "Part_Number": selected_sensor.split("_")[1],
    "Configured_ODR_Hz": fs,
    "Injected_Error_Model": {
        "Static_Bias": {"Accel_g": spec["accel_bias"], "Gyro_dps": spec["gyro_bias"]},
        "Stochastic_Noise": {"Accel_ND": spec["accel_noise_density"], "Gyro_ND": spec["gyro_noise_density"]}
    },
    "Status": "Simulation Active"
})