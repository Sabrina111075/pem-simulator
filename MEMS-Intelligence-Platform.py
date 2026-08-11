import streamlit as st
import numpy as np
import pandas as pd
from scipy import signal
import datetime

# ==========================================
# 1. MEMS Digital Library 欄位標準化資料庫
# ==========================================
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
        "accel_noise_density": 0.00007,  # g/√Hz
        "gyro_noise_density": 0.0028,    # dps/√Hz
        "accel_bias": 0.01,              # g
        "gyro_bias": 0.05,               # dps
        "range_accel": "±16g",
        "range_gyro": "±2000dps"
    },
    "ANALOG_DEVICES_ADIS16488": {
        "manufacturer": "Analog Devices",
        "level": "戰術級/工業級高精度診斷 (高成本)",
        "accel_noise_density": 0.000016, # g/√Hz
        "gyro_noise_density": 0.00015,   # dps/√Hz
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
    },
    "STM_LSM6DSV16X": {
        "manufacturer": "STMicroelectronics",
        "level": "消費級/智慧終端/邊緣 AI 核心級",
        "accel_noise_density": 0.000075, # g/√Hz
        "gyro_noise_density": 0.0038,    # dps/√Hz
        "accel_bias": 0.012,             # g
        "gyro_bias": 0.06,               # dps
        "range_accel": "±16g",
        "range_gyro": "±2000dps"
    },
    "HONEYWELL_HG4930": {
        "manufacturer": "Honeywell",
        "level": "導航級/高精導引/航太防衛級 (頂級管制元件)",
        "accel_noise_density": 0.000005, # g/√Hz
        "gyro_noise_density": 0.00004,   # dps/√Hz
        "accel_bias": 0.0002,            # g
        "gyro_bias": 0.001,              # dps
        "range_accel": "±20g",
        "range_gyro": "±400dps"
    }
}

st.set_page_config(page_title="Crystal Machine MEMS Platform", layout="wide")

# 內建時區指派台北標準時間
tz_taipei = datetime.timezone(datetime.timedelta(hours=8))
now_taipei = datetime.datetime.now(tz_taipei).strftime("%Y-%m-%d %H:%M:%S")

st.markdown("<h1 style='font-size: 28px; margin-bottom: 5px;'>🛸 MEMS Intelligence Platform - 微機電系統智慧平台</h1>", unsafe_allow_html=True)
st.caption(f"⏱️ 系統即時同步：{now_taipei} (台北標準時間 TST)")

# ==========================================
# 2. 側邊欄控制：選擇感測器與調整環境參數
# ==========================================
st.sidebar.header("🛠️ Crystal Machine 平台參數設定")

selected_sensor = st.sidebar.selectbox("選擇 MEMS 感測器元件", list(SENSOR_DB.keys()))
spec = SENSOR_DB[selected_sensor]

st.sidebar.subheader("🧪 融合引擎演算法切換")
fusion_mode = st.sidebar.radio(
    "選擇解算濾波演算法", 
    ["⚖️ 一階互補濾波 (Complementary Filter)", "📐 線性卡爾曼濾波 (Kalman Filter)"]
)

st.sidebar.subheader("🌍 環境與時序設定")
fs = st.sidebar.slider("取樣頻率 ODR (Hz)", min_value=50, max_value=200, value=100, step=10)
duration = st.sidebar.slider("模擬時長 (秒)", min_value=2, max_value=10, value=5)
motion_freq = st.sidebar.slider("虛擬運動頻率 (Hz)", min_value=0.5, max_value=3.0, value=1.0, step=0.5)

st.sidebar.subheader("⚠️ 誤差注入乘數")
noise_multiplier = st.sidebar.slider("雜訊放大倍率", min_value=1.0, max_value=10.0, value=1.0, step=0.5)
drift_multiplier = st.sidebar.slider("隨機遊走(漂移)放大倍率", min_value=0.0, max_value=5.0, value=1.0, step=0.5)

st.sidebar.subheader("🎛️ 演算法調諧參數")
if "一階互補濾波" in fusion_mode:
    alpha = st.sidebar.slider("互補濾波器權重 (Alpha)", min_value=0.80, max_value=0.99, value=0.96, step=0.01)
else:
    q_tune = st.sidebar.slider("過程噪聲調諧因子 (Q Tune)", min_value=0.001, max_value=1.0, value=0.01, step=0.005, format="%.3f")

# ==========================================
# 3. 核心數學模型與資料流計算
# ==========================================
t = np.linspace(0, duration, int(fs * duration), endpoint=False)
dt = 1.0 / fs

true_angle = 20.0 * np.sin(2 * np.pi * motion_freq * t)  
true_gyro = 20.0 * (2 * np.pi * motion_freq) * np.cos(2 * np.pi * motion_freq * t) 
true_accel = np.sin(np.radians(true_angle)) 

gyro_white_noise = np.random.normal(0, spec["gyro_noise_density"] * np.sqrt(fs), len(t)) * noise_multiplier
gyro_drift = np.cumsum(np.random.normal(0, 0.01, len(t))) * drift_multiplier
sim_gyro = true_gyro + spec["gyro_bias"] + gyro_white_noise + gyro_drift

accel_white_noise = np.random.normal(0, spec["accel_noise_density"] * np.sqrt(fs), len(t)) * noise_multiplier
sim_accel = true_accel + spec["accel_bias"] + accel_white_noise

est_angle_accel = np.degrees(np.arcsin(np.clip(sim_accel, -1.0, 1.0)))
est_angle = np.zeros(len(t))
est_angle[0] = est_angle_accel[0]

if "一階互補濾波" in fusion_mode:
    engine_name = "一階互補濾波"
    for k in range(1, len(t)):
        est_angle[k] = alpha * (est_angle[k-1] + sim_gyro[k] * dt) + (1 - alpha) * est_angle_accel[k]
else:
    engine_name = "線性卡爾曼濾波"
    Q_angle = q_tune
    Q_gyro_bias = 0.003 * drift_multiplier
    R_angle = (spec["accel_noise_density"] * np.sqrt(fs) * noise_multiplier) ** 2

    x = np.array([est_angle_accel[0], spec["gyro_bias"]]).reshape(2, 1)
    P = np.eye(2) * 0.1

    A = np.array([[1.0, -dt],
                  [0.0, 1.0]])
    H = np.array([[1.0, 0.0]])
    
    Q = np.array([[Q_angle, 0.0],
                  [0.0, Q_gyro_bias]])
    R = np.array([[R_angle]])

    for k in range(1, len(t)):
        u = sim_gyro[k]
        x = np.dot(A, x)
        x[0, 0] += u * dt
        P = np.dot(np.dot(A, P), A.T) + Q
        
        z = est_angle_accel[k]
        y = z - np.dot(H, x)  
        S = np.dot(np.dot(H, P), H.T) + R
        K = np.dot(P, H.T) / S  
        
        x = x + K * y
        P = np.dot((np.eye(2) - np.dot(K, H)), P)
        
        est_angle[k] = x[0, 0]

rmse = np.sqrt(np.mean((est_angle - true_angle) ** 2))

# ==========================================
# 4. Streamlit 前端數據看板呈現
# ==========================================
st.subheader(f"📊 {selected_sensor} 元件模擬與動態融合結果")

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("當前解算引擎", engine_name)
kpi2.metric("真實運動均方根誤差 (RMSE)", f"{rmse:.3f} 度", delta=f"{'- 優異' if rmse < 1.5 else '- 雜訊發散'}", delta_color="inverse")
kpi3.metric("資料流解析狀態", "即時演算中 (Active)", delta="Normal")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**1. 原始感測器輸出 (含注入誤差與雜訊)**")
    sensor_df = pd.DataFrame({
        "時間(秒)": t,
        "陀螺儀輸出(dps)": sim_gyro,
        "理想角速度(dps)": true_gyro,
    }).set_index("時間(秒)")
    st.line_chart(sensor_df)
    st.caption("💡 藍線（模擬輸出）圍繞著紅線（真實運動）波動，包含高頻白雜訊與慢變隨機遊走基線漂移。")

with col2:
    st.markdown(f"**2. {engine_name} 狀態估計與融合輸出**")
    fusion_df = pd.DataFrame({
        "時間(秒)": t,
        "真實角度(度)": true_angle,
        "單靠加速度計估算(度)": est_angle_accel,
        "濾波融合解算角度(度)": est_angle
    }).set_index("時間(秒)")
    
    # 修正點：移除導致出錯的 y_select 參數，回歸原生安全的 line_chart 渲染
    st.line_chart(fusion_df)
    st.caption("💡 綠線為最終解算姿態。圖表會自動調整適宜間距以完整呈現振盪波峰。")

# ==========================================
# 5. 優化後的規格看板呈現 (Digital Library View)
# ==========================================
st.divider()
st.subheader("📋 平台底層標準化規格數據 (Digital Library View)")

with st.container(border=True):
    m_col1, m_col2, m_col3 = st.columns([1, 1.5, 1])
    m_col1.markdown(f"**感測器 ID**<br><span style='font-size: 20px; font-weight: bold; color: #1E3A8A;'>CM-{selected_sensor.split('_')[-1]}</span>", unsafe_allow_html=True)
    m_col2.markdown(f"**製造商 (Vendor)**<br><span style='font-size: 20px; font-weight: bold; color: #1E3A8A;'>{spec['manufacturer']}</span>", unsafe_allow_html=True)
    m_col3.markdown(f"**元件型號 (Part Number)**<br><span style='font-size: 20px; font-weight: bold; color: #1E3A8A;'>{selected_sensor.split('_')[-1]}</span>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    m_col4, m_col5 = st.columns([2.5, 1])
    m_col4.markdown(f"""
    <div style='background-color: #E0F2FE; padding: 10px 15px; border-radius: 6px; border-left: 5px solid #0284C7;'>
        <span style='color: #0369A1; font-weight: bold;'>🎯 應用分級定位：</span>
        <span style='color: #0C4A6E;'>{spec['level']}</span>
    </div>
    """, unsafe_allow_html=True)
    m_col5.markdown(f"**運行頻率 (ODR)**<br><span style='font-size: 20px; font-weight: bold; color: #1E3A8A;'>{fs} Hz</span>", unsafe_allow_html=True)

st.markdown("### 🔍 靜態物理與誤差注入模型參數對照")
spec_data = {
    "參數類別": ["物理硬體極限", "物理硬體極限", "靜態零偏誤差", "靜態零偏誤差", "隨機雜訊密度", "隨機雜訊密度"],
    "感測軸向": ["加速度計", "陀螺儀", "加速度計", "陀螺儀", "加速度計", "陀螺儀"],
    "標準化參數名稱": ["Full_Scale_Range_Accel", "Full_Scale_Range_Gyro", "Accel_Static_Bias (b_a)", "Gyro_Static_Bias (b_w)", "Accel_Noise_Density (n_a)", "Gyro_Noise_Density (n_w)"],
    "設定值": [spec["range_accel"], spec["range_gyro"], f"{spec['accel_bias']} g", f"{spec['gyro_bias']} dps", f"{spec['accel_noise_density']} g/√Hz", f"{spec['gyro_noise_density']} dps/√Hz"]
}
st.table(pd.DataFrame(spec_data))
st.caption("⚙️ 狀態提示：Digital Library 矩陣參數動態注入成功，雙濾波架構就緒。")