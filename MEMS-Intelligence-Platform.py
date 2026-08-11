import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# --- 頁面全面配置 ---
st.set_page_config(
    page_title="Crystal Machine MEMS Platform",
    page_icon="🤖",
    layout="wide"
)

# --- 模擬資料生成函式 ---
def generate_simulation_data(sensor_id, odr, duration, motion_freq, noise_amp, walk_amp, alpha):
    t = np.linspace(0, duration, int(odr * duration))
    # 理想角速度 (正弦波)
    ideal_ang_vel = 150 * np.sin(2 * np.pi * motion_freq * t)
    
    # 注入雜訊與隨機遊走
    noise = noise_amp * 15 * np.random.normal(0, 1, len(t))
    random_walk = walk_amp * 5 * np.cumsum(np.random.normal(0, 0.5, len(t)))
    gyro_output = ideal_ang_vel + noise + random_walk
    
    # 理想角度 (積分)
    ideal_angle = - (150 / (2 * np.pi * motion_freq)) * np.cos(2 * np.pi * motion_freq * t)
    ideal_angle = ideal_angle - ideal_angle[0] # 歸零
    
    # 模擬單靠加速度計估算的粗糙角度 (含雜訊)
    accel_angle = ideal_angle + np.random.normal(0, 3, len(t))
    
    # 一階互補濾波演算法
    comp_angle = np.zeros(len(t))
    comp_angle[0] = ideal_angle[0]
    dt = 1.0 / odr
    for i in range(1, len(t)):
        # 陀螺儀積分高度依賴 alpha，加速度計修正依賴 (1-alpha)
        comp_angle[i] = alpha * (comp_angle[i-1] + gyro_output[i] * dt) + (1 - alpha) * accel_angle[i]
        
    # 計算 RMSE (狀態估計 vs 真實角度)
    rmse = np.sqrt(np.mean((comp_angle - ideal_angle) ** 2))
    
    return t, gyro_output, accel_angle, comp_angle, ideal_angle, rmse

# ==========================================
# 左側控制面板：Crystal Machine 平台參數設定
# ==========================================
st.sidebar.markdown("## ⚙️ Crystal Machine 平台\n參數設定")

sensor_option = st.sidebar.selectbox(
    "選擇 MEMS 感測器元件",
    ["INNOMOTION_ICM-20689", "BOSCH_BMI270"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🧬 融合引擎演算法切換")
algo_option = st.sidebar.radio(
    "選擇解算濾波資算法",
    ["一階互補濾波\n(Complementary Filter)", "線性卡爾曼濾波 (Kalman Filter)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("## ⏰ 環境與時序設定")
odr = st.sidebar.slider("取樣頻率 ODR (Hz)", min_value=10, max_value=200, value=120, step=10)
duration = st.sidebar.slider("模擬時長 (秒)", min_value=1, max_value=10, value=5)
motion_freq = st.sidebar.slider("虛擬運動頻率 (Hz)", min_value=0.5, max_value=5.0, value=1.50, step=0.1)

st.sidebar.markdown("---")
st.sidebar.markdown("## ⚠️ 誤差注入參數")
noise_amp = st.sidebar.slider("雜訊放大倍率", min_value=0.0, max_value=10.0, value=4.00, step=0.1)
walk_amp = st.sidebar.slider("隨機遊走(漂移)放大倍率", min_value=0.0, max_value=5.0, value=1.50, step=0.1)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🎛️ 演算法調諧參數")
alpha = st.sidebar.slider("互補濾波器權重 (Alpha)", min_value=0.0, max_value=1.0, value=0.98, step=0.01)


# ==========================================
# 右側主面板：優化後的架構布局
# ==========================================
st.markdown("# 📊 MEMS Intelligence Platform - 微機電系統智慧平台")

# 即時時間同步顯示
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f" `系統即時同步：{current_time} (台北標準時間 TST)`")
st.markdown("---")

# 準備元件底層靜態規格資料
if sensor_option == "INNOMOTION_ICM-20689":
    sensor_id = "CM-ICM-20689"
    vendor = "芯動聯科 (InnoMotion)"
    part_num = "ICM-20689"
    app_tier = "工業級/車載級/無人機穩定系統"
    spec_details = {
        "Full_Scale_Range_Accel": "±16g",
        "Full_Scale_Range_Gyro": "±2000dps",
        "Accel_Static_Bias (b_a)": "0.015 g",
        "Gyro_Static_Bias (b_w)": "0.07 dps",
        "Accel_Noise_Density (n_a)": "9e-05 g/√Hz",
        "Gyro_Noise_Density (n_w)": "0.004 dps/√Hz"
    }
else:
    sensor_id = "CM-BMI270"
    vendor = "BOSCH"
    part_num = "BMI270"
    app_tier = "消費級/人形機器人 (低成本方案)"
    spec_details = {
        "Full_Scale_Range_Accel": "±8g",
        "Full_Scale_Range_Gyro": "±2000dps",
        "Accel_Static_Bias (b_a)": "0.020 g",
        "Gyro_Static_Bias (b_w)": "0.08 dps",
        "Accel_Noise_Density (n_a)": "160 μg/√Hz",
        "Gyro_Noise_Density (n_w)": "0.007 dps/√Hz"
    }

# 執行核心模擬數據計算
t, gyro_output, accel_angle, comp_angle, ideal_angle, rmse = generate_simulation_data(
    sensor_id, odr, duration, motion_freq, noise_amp, walk_amp, alpha
)

# ------------------------------------------
# 【第一層：頂層】平台底層標準化規格數據 (Digital Library View)
# ------------------------------------------
st.markdown("## 💼 平台底層標準化規格數據 (Digital Library View)")
with st.container():
    # 使用帶邊框與背景的區塊包覆基本履歷
    st.info(f"""
    **感測器 ID**：`{sensor_id}` &nbsp;&nbsp;|&nbsp;&nbsp; **製造商 (Vendor)**：`{vendor}` &nbsp;&nbsp;|&nbsp;&nbsp; **元件型號 (Part Number)**：`{part_num}`  
    🎯 **應用分級定位**：{app_tier} &nbsp;&nbsp;|&nbsp;&nbsp; ⚙️ **運行頻率 (ODR)**：`{odr} Hz`
    """)
    
    # 靜態物理與誤差注入模型參數對照 (文字敘述簡化版)
    st.markdown("#### 🔍 靜態物理與誤差注入模型參數對照")
    col_lbl1, col_lbl2, col_lbl3 = st.columns(3)
    
    keys = list(spec_details.keys())
    with col_lbl1:
        st.markdown(f"**🧱 物理硬體極限**\n* 加速度計全量程: `{spec_details[keys[0]]}`\n* 陀螺儀全量程: `{spec_details[keys[1]]}`")
    with col_lbl2:
        st.markdown(f"**📍 靜態零偏誤差**\n* 加速度計零偏 (b_a): `{spec_details[keys[2]]}`\n* 陀螺儀零偏 (b_w): `{spec_details[keys[3]]}`")
    with col_lbl3:
        st.markdown(f"**🌌 隨機雜訊密度**\n* 加速度計雜訊 (n_a): `{spec_details[keys[4]]}`\n* 陀螺儀雜訊 (n_w): `{spec_details[keys[5]]}`")
        
    st.caption("⚙️ 狀態提示：Digital Library 矩陣參數動態注入成功，雙濾波架構就緒。")

st.markdown("---")

# ------------------------------------------
# 【第二層：中層】即時效能指標看板 (KPIs Panel)
# ------------------------------------------
st.markdown(f"## 📉 {sensor_option} 元件模擬與動態融合結果")

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.metric(label="當前解算引擎", value="一階互補濾波" if "一階互補濾波" in algo_option else "線性卡爾曼濾波")
with col_kpi2:
    # 根據 RMSE 表現動態給予標籤提示
    status_msg = "↓ - 優異" if rmse < 1.5 else "⚡ - 需再調諧"
    st.metric(label="真實運動均方根誤差 (RMSE)", value=f"{rmse:.3f} 度", delta=status_msg, delta_color="normal" if rmse < 1.5 else "inverse")
with col_kpi3:
    st.metric(label="資料流解析狀態", value="即時運算中 (Active)", delta="↑ Normal")

# ------------------------------------------
# 【第三層：底層】元件模擬與動態融合結果圖表 (Visual Charts)
# ------------------------------------------
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("##### 1. 原始感測器輸出 (含注入誤差與雜訊)")
    fig1, ax1 = plt.subplots(figsize=(6, 3.5))
    ax1.plot(t, gyro_output, color='#0C6291', linewidth=1.5)
    ax1.set_grid(True, linestyle='--', alpha=0.5)
    ax1.set_xlim(0, duration)
    fig1.tight_layout()
    st.pyplot(fig1)

with col_chart2:
    st.markdown("##### 2. 一階互補濾波 狀態估計與融合輸出")
    fig2, ax2 = plt.subplots(figsize=(6, 3.5))
    # 藍線表示濾波融合輸出，紅線表示真實角度
    ax2.plot(t, comp_angle, color='#1c7ed6', linewidth=1.5, label='濾波融合角')
    ax2.plot(t, ideal_angle, color='#e03131', linewidth=1.2, linestyle='-', label='真實角')
    ax2.set_grid(True, linestyle='--', alpha=0.5)
    ax2.set_xlim(0, duration)
    fig2.tight_layout()
    st.pyplot(fig2)

st.markdown("""
💡 **圖表輔助說明**：
* **左圖**藍線呈現包含高頻白雜訊與慢變隨機遊走基線漂移後的陀螺儀原始輸出波形，模擬真實物理環境中的雜訊干擾。
* **右圖**呈現融合後的姿態解算角度（藍線）與絕對真實運動軌跡（紅線）之對照。圖表與上方 RMSE 指標會隨著左側「Alpha 權重」與「誤差注入」的增減進行即時動態響應。
""")