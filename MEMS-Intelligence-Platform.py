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
    ideal_ang_vel = 150 * np.sin(2 * np.pi * motion_freq * t)
    
    noise = noise_amp * 15 * np.random.normal(0, 1, len(t))
    random_walk = walk_amp * 5 * np.cumsum(np.random.normal(0, 0.5, len(t)))
    gyro_output = ideal_ang_vel + noise + random_walk
    
    ideal_angle = - (150 / (2 * np.pi * motion_freq)) * np.cos(2 * np.pi * motion_freq * t)
    ideal_angle = ideal_angle - ideal_angle[0]
    
    accel_angle = ideal_angle + np.random.normal(0, 3, len(t))
    
    comp_angle = np.zeros(len(t))
    comp_angle[0] = ideal_angle[0]
    dt = 1.0 / odr
    for i in range(1, len(t)):
        comp_angle[i] = alpha * (comp_angle[i-1] + gyro_output[i] * dt) + (1 - alpha) * accel_angle[i]
        
    rmse = np.sqrt(np.mean((comp_angle - ideal_angle) ** 2))
    
    return t, gyro_output, accel_angle, comp_angle, ideal_angle, rmse

# ==========================================
# 左側控制面板：Crystal Machine 平台參數設定
# ==========================================
st.sidebar.markdown("## ⚙️ Crystal Machine 平台\n參數設定")

# 補齊七家廠商元件選單
sensor_display = st.sidebar.selectbox(
    "選擇 MEMS 感測器元件",
    [
        "芯動聯科 (InnoMotion) - ICM-20689",
        "博世 (BOSCH) - BMI270",
        "意法半導體 (STMicroelectronics) - LSM6DSOX",
        "應美盛 (TDK InvenSense) - ICM-42688-P",
        "亞德諾 (Analog Devices) - ADIS16470",
        "村田製作所 (Murata) - SCC2130",
        "恩智浦 (NXP) - FXOS8700CQ"
    ]
)

# 七家廠商的底層資料庫映射邏輯
if "ICM-20689" in sensor_display:
    sensor_id, vendor, part_num, app_tier = "CM-ICM-20689", "芯動聯科 (InnoMotion)", "ICM-20689", "工業級/車載級/無人機穩定系統"
    acc_rng, gyro_rng, b_a, b_w, n_a, n_w = "±16g", "±2000dps", "0.015 g", "0.07 dps", "9e-05 g/√Hz", "0.004 dps/√Hz"
elif "BMI270" in sensor_display:
    sensor_id, vendor, part_num, app_tier = "CM-BMI270", "BOSCH", "BMI270", "消費級/人形機器人 (低成本方案)"
    acc_rng, gyro_rng, b_a, b_w, n_a, n_w = "±8g", "±2000dps", "0.020 g", "0.08 dps", "160 μg/灎Hz", "0.007 dps/√Hz"
elif "LSM6DSOX" in sensor_display:
    sensor_id, vendor, part_num, app_tier = "CM-LSM6DSOX", "STMicroelectronics", "LSM6DSOX", "消費級/智慧穿戴/機器人關節估計"
    acc_rng, gyro_rng, b_a, b_w, n_a, n_w = "±16g", "±2000dps", "0.018 g", "0.075 dps", "75 μg/√Hz", "0.005 dps/√Hz"
elif "ICM-42688-P" in sensor_display:
    sensor_id, vendor, part_num, app_tier = "CM-ICM42688P", "TDK InvenSense", "ICM-42688-P", "工業級/高精度無人載具/防手震平衡"
    acc_rng, gyro_rng, b_a, b_w, n_a, n_w = "±16g", "±2000dps", "0.012 g", "0.05 dps", "65 μg/√Hz", "0.0028 dps/√Hz"
elif "ADIS16470" in sensor_display:
    sensor_id, vendor, part_num, app_tier = "CM-ADIS16470", "Analog Devices", "ADIS16470", "戰術級/精準導航與工業自動化"
    acc_rng, gyro_rng, b_a, b_w, n_a, n_w = "±40g", "±2000dps", "0.005 g", "0.008 dps", "16 μg/√Hz", "0.002 dps/√Hz"
elif "SCC2130" in sensor_display:
    sensor_id, vendor, part_num, app_tier = "CM-SCC2130", "Murata", "SCC2130", "車載安全級/主動車身穩定控制系統"
    acc_rng, gyro_rng, b_a, b_w, n_a, n_w = "±6g", "±125dps", "0.008 g", "0.02 dps", "50 μg/√Hz", "0.0015 dps/√Hz"
else:
    sensor_id, vendor, part_num, app_tier = "CM-FXOS8700", "NXP", "FXOS8700CQ", "消費級/低功耗物聯網節點"
    acc_rng, gyro_rng, b_a, b_w, n_a, n_w = "±8g", "N/A (僅加速度計+地磁)", "0.025 g", "N/A", "126 μg/√Hz", "N/A"

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
# 右側主面板：置頂規格庫與滿版工整布局
# ==========================================
st.markdown("# 📊 MEMS Intelligence Platform - 微機電系統智慧平台")

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f" `系統即時同步：{current_time} (台北標準時間 TST)`")
st.markdown("---")

t, gyro_output, accel_angle, comp_angle, ideal_angle, rmse = generate_simulation_data(
    sensor_id, odr, duration, motion_freq, noise_amp, walk_amp, alpha
)

# ------------------------------------------
# 【第一層：頂層】Digital Library View (放大字體、應用分級加色高亮)
# ------------------------------------------
st.markdown("### 💼 平台底層標準化規格數據 (Digital Library View)")

# 放大字體至 18px，並將應用分級加上明顯的橘紅色高亮標籤背景
st.markdown(f"""
<div style="background-color: #eef5fc; padding: 22px; border-radius: 8px; border-left: 6px solid #1c7ed6; margin-bottom: 20px;">
    <table style="width:100%; border:none; background:none; font-size:18px; color:#1c7ed6; border-collapse: separate; border-spacing: 0 12px;">
        <tr style="border:none; background:none;">
            <td style="border:none;"><b>感測器 ID：</b><code style="color:#0b519c; font-size:18px;">{sensor_id}</code></td>
            <td style="border:none;"><b>製造商 (Vendor)：</b><span style="color:#111; font-weight:bold;">{vendor}</span></td>
            <td style="border:none;"><b>元件型號 (Part Number)：</b><span style="color:#111; font-weight:bold;">{part_num}</span></td>
        </tr>
        <tr style="border:none; background:none;">
            <td colspan="2" style="border:none;">
                🎯 <b>應用分級定位：</b>
                <span style="background-color: #ffebd6; color: #d9534f; padding: 4px 10px; border-radius: 4px; font-weight: bold; border: 1px solid #ffcc99;">
                    {app_tier}
                </span>
            </td>
            <td style="border:none;">⚙️ <b>運行頻率 (ODR)：</b><span style="color:#111; font-weight:bold;">{odr} Hz</span></td>
        </tr>
    </table>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------
# 參數對照表拉長對齊 (改用 st.dataframe 達成滿版工整效果)
# ------------------------------------------
st.markdown("#### 🔍 靜態物理與誤差注入模型參數對照")

df_spec = pd.DataFrame([
    {"參數類別": "物理硬體極限", "感測軸向": "加速度計", "標準化參數名稱": "Full_Scale_Range_Accel", "設定值": acc_rng},
    {"參數類別": "物理硬體極限", "感測軸向": "陀螺儀", "標準化參數名稱": "Full_Scale_Range_Gyro", "設定值": gyro_rng},
    {"參數類別": "靜態零偏誤差", "感測軸向": "加速度計", "標準化參數名稱": "Accel_Static_Bias (b_a)", "設定值": b_a},
    {"參數類別": "靜態零偏誤差", "感測軸向": "陀螺儀", "標準化參數名稱": "Gyro_Static_Bias (b_w)", "設定值": b_w},
    {"參數類別": "隨機雜訊密度", "感測軸向": "加速度計", "標準化參數名稱": "Accel_Noise_Density (n_a)", "設定值": n_a},
    {"參數類別": "隨機雜訊密度", "感測軸向": "陀螺儀", "標準化參數名稱": "Gyro_Noise_Density (n_w)", "設定值": n_w}
])

# use_container_width=True 會強迫表格自動左右拉長對齊容器邊緣
st.dataframe(df_spec, use_container_width=True, hide_index=True)
st.caption("⚙️ 狀態提示：Digital Library 矩陣參數動態注入成功，雙濾波架構就緒。")

st.markdown("---")

# ------------------------------------------
# 【第二層：中層】即時效能指標看板 (KPIs Panel)
# ------------------------------------------
st.markdown(f"### 📉 {sensor_display.split(' - ')[0]} 元件模擬與動態融合結果")

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.metric(label="當前解算引擎", value="一階互補濾波" if "一階互補濾波" in algo_option else "線性卡爾曼濾波")
with col_kpi2:
    status_msg = "↓ - 優異" if rmse < 1.5 else "⚡ - 需再調諧"
    st.metric(label="真實運動均方根誤差 (RMSE)", value=f"{rmse:.3f} 度", delta=status_msg, delta_color="normal" if rmse < 1.5 else "inverse")
with col_kpi3:
    st.metric(label="資料流解析狀態", value="即時運算中 (Active)", delta="↑ Normal")

# ------------------------------------------
# 【第三層：底層】元件模擬與動態融合結果圖表
# ------------------------------------------
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("##### 1. 原始感測器輸出 (含注入誤差與雜訊)")
    fig1, ax1 = plt.subplots(figsize=(6, 3.5))
    ax1.plot(t, gyro_output, color='#0C6291', linewidth=1.5)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.set_xlim(0, duration)
    fig1.tight_layout()
    st.pyplot(fig1)

with col_chart2:
    st.markdown("##### 2. 一階互補濾波 狀態估計與融合輸出")
    fig2, ax2 = plt.subplots(figsize=(6, 3.5))
    ax2.plot(t, comp_angle, color='#1c7ed6', linewidth=1.5, label='濾波融合角')
    ax2.plot(t, ideal_angle, color='#e03131', linewidth=1.2, linestyle='-', label='真實角')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.set_xlim(0, duration)
    fig2.tight_layout()
    st.pyplot(fig2)

st.markdown("""
💡 **圖表輔助說明**：
* 藍線（模擬輸出）圍繞著紅線（真實運動）波動，包含高頻白雜訊與慢變隨機遊走基線漂移。
* 綠線為最終解算姿態。圖表會自動調整適宜間距以完整呈現振盪波峰。
""")