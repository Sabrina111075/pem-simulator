import streamlit as st
import numpy as np
import pandas as pd
from scipy import signal

# ==========================================
# 1. MEMS Digital Library 欄位標準化資料庫 (大幅擴充版)
# ==========================================
# 納入全球主流 IMU 元件規格參數，支援消費級、工業級與高精度導航級型號
SENSOR_DB = {
    "BOSCH_BMI270": {
        "manufacturer": "BOSCH",
        "level": "消費級/人形機器人 (低成本方案)",
        "accel_noise_density": 0.00016,  # g/√Hz
        "gyro_noise_density": 0.007,     # dps/√Hz
        "accel_bias": 0.02,              # g
        "gyro_bias": 0.1,                # dps
        "range_accel": "±16g",
        "range_gyro": "±2000dps"
    },
    "TDK_ICM-42688-P": {
        "manufacturer": "TDK InvenSense",
        "level": "消費級/人形機器人 (高精準配置)",
        "accel_noise_density": 0.00007,  # g/√Hz (低噪)
        "gyro_noise_density": 0.0028,    # dps/√Hz
        "accel_bias": 0.01,              # g
        "gyro_bias": 0.05,               # dps
        "range_accel": "±16g",
        "range_gyro": "±2000dps"
    },
    "ANALOG_DEVICES_ADIS16488": {
        "manufacturer": "Analog Devices",
        "level": "戰術級/工業級高精度診斷 (高成本)",
        "accel_noise_density": 0.000016, # g/√Hz (極低噪)
        "gyro_noise_density": 0.00015,   # dps/√Hz (超高穩定度)
        "accel_bias": 0.002,             # g
        "gyro_bias": 0.008,              # dps
        "range_accel": "±40g",
        "range_gyro": "±2000dps"
    },
    "INNOMOTION_ICM-20689": {
        "manufacturer": "芯動聯科 (InnoMotion)",
        "level": "工業級/車載級/無人機穩定系統",
        "accel_noise_density": 0.00009,  # g/√Hz
        "gyro_noise_density": 0.004,     # dps/√Hz
        "accel_bias": 0.015,             # g
        "gyro_bias": 0.07,               # dps
        "range_accel": "±16g",
        "range_gyro": "±2000dps"
    },
    "QST_QMI8658C": {
        "manufacturer": "啟明創感 (QST)",
        "level": "消費級/物聯網/低成本模組化設計",
        "accel_noise_density": 0.00022,  # g/√Hz
        "gyro_noise_density": 0.012,     # dps/√Hz
        "accel_bias": 0.03,              # g
        "gyro_bias": 0.15,               # dps
        "range_accel": "±16g",
        "range_gyro": "±2000dps"
    }
}

st.set_page_config(page_title="Crystal Machine MEMS Platform", layout="wide")
st.title("🛸 Crystal Machine MEMS Intelligence Platform - 模擬平台")
st.caption("基於 Windows 7 本地開發驗證 ➔ GitHub / Streamlit 3.11 雲端部署架構")

# ==========================================
# 2. 側邊欄控制：選擇感測器與調整環境參數
# ==========================================
st.sidebar.header("🛠️ Crystal Machine 平台參數設定")

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
true_angle = 20.0 * np.sin(2 * np.pi * motion_freq * t)  # 理想角度 (度)
true_gyro = 20.0 * (2 * np.pi * motion_freq) * np.cos(2 * np.pi * motion_freq * t) 
true_accel = np.sin(np.radians(true_angle)) 

# B. 動態模型與誤差注入 (Error Injection)
gyro_white_noise = np.random.normal(0, spec["gyro_noise_density"] * np.sqrt(fs), len(t)) * noise_multiplier
gyro_drift = np.cumsum(np.random.normal(0, 0.01, len(t))) * drift_multiplier
sim_gyro = true_gyro + spec["gyro_bias"] + gyro_white_noise + gyro_drift

accel_white_noise = np.random.normal(0, spec["accel_noise_density"] * np.sqrt(fs), len(t)) * noise_multiplier
sim_accel = true_accel + spec["accel_bias"] + accel_white_noise

# C. 融合引擎 (Sensor Fusion Engine)
est_angle_accel = np.degrees(np.arcsin(np.clip(sim_accel, -1.0, 1.0)))
est_angle = np.zeros(len(t))
est_angle[0] = est_angle_accel[0]

for k in range(1, len(t)):
    est_angle[k] = alpha * (est_angle[k-1] + sim_gyro[k] * dt) + (1 - alpha) * est_angle_accel[k]

# ==========================================
# 4. Streamlit 前端數據看板呈現
# ==========================================
st.subheader(f"📊 {selected_sensor} 元件模擬與動態融合結果")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**1. 原始感測器輸出 (含注入誤差與雜訊)**")
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

# ==========================================
# 5. 優化後的規格看板呈現 (修飾擁擠版，增加柔和色塊)
# ==========================================
st.divider()
st.subheader("📋 平台底層標準化規格數據 (Digital Library View)")

# 使用帶有柔和灰色/藍色邊框背景的 container
with st.container(border=True):
    m_col1, m_col2, m_col3 = st.columns([1, 1.5, 1])
    
    # 將資訊合理分配，給予足夠的橫向擴展空間，避免文字縮寫
    m_col1.markdown(f"**感測器 ID**<br><span style='font-size: 20px; font-weight: bold; color: #1E3A8A;'>CM-{selected_sensor.split('_')[-1]}</span>", unsafe_allow_html=True)
    m_col2.markdown(f"**製造商 (Vendor)**<br><span style='font-size: 20px; font-weight: bold; color: #1E3A8A;'>{spec['manufacturer']}</span>", unsafe_allow_html=True)
    m_col3.markdown(f"**元件型號 (Part Number)**<br><span style='font-size: 20px; font-weight: bold; color: #1E3A8A;'>{selected_sensor.split('_')[-1]}</span>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    m_col4, m_col5 = st.columns([2.5, 1])
    # 使用柔和的淺綠色底色方塊來強調應用分級
    m_col4.markdown(f"""
    <div style='background-color: #E0F2FE; padding: 10px 15px; border-radius: 6px; border-left: 5px solid #0284C7;'>
        <span style='color: #0369A1; font-weight: bold;'>🎯 應用分級定位：</span>
        <span style='color: #0C4A6E;'>{spec['level']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    m_col5.markdown(f"**運行頻率 (ODR)**<br><span style='font-size: 20px; font-weight: bold; color: #1E3A8A;'>{fs} Hz</span>", unsafe_allow_html=True)

# B. 將複雜的模型參數整理成 scannable 的對照表格
st.markdown("### 🔍 靜態物理與誤差注入模型參數對照")

spec_data = {
    "參數類別": [
        "物理硬體極限 (Hardware Limits)", "物理硬體極限 (Hardware Limits)", 
        "靜態零偏誤差 (Static Bias)", "靜態零偏誤差 (Static Bias)", 
        "隨機雜訊密度 (Stochastic Noise)", "隨機雜訊密度 (Stochastic Noise)"
    ],
    "感測軸向": [
        "加速度計 (Accelerometer)", "陀螺儀 (Gyroscope)", 
        "加速度計 (Accelerometer)", "陀螺儀 (Gyroscope)", 
        "加速度計 (Accelerometer)", "陀螺儀 (Gyroscope)"
    ],
    "標準化參數名稱": [
        "Full_Scale_Range_Accel", "Full_Scale_Range_Gyro", 
        "Accel_Static_Bias (b_a)", "Gyro_Static_Bias (b_w)", 
        "Accel_Noise_Density (n_a)", "Gyro_Noise_Density (n_w)"
    ],
    "設定值": [
        spec["range_accel"], spec["range_gyro"], 
        f"{spec['accel_bias']} g", f"{spec['gyro_bias']} dps", 
        f"{spec['accel_noise_density']} g/√Hz", f"{spec['gyro_noise_density']} dps/√Hz"
    ]
}

df_spec = pd.DataFrame(spec_data)
st.table(df_spec)
st.caption("⚙️ 狀態提示：Digital Library 封裝解析成功，模擬器正在即時注入上述物理誤差。")