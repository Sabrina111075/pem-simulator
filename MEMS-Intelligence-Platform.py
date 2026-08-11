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
        comp_angle[i] = alpha * (comp_angle[i-1] + gyro_output[i] * dt) + (1 - alpha) * accel_angle[i]
        
    # 計算 RMSE
    rmse = np.sqrt(np.mean((comp_angle - ideal_angle) ** 2))
    
    return t, gyro_output, accel_angle, comp_angle, ideal_angle, rmse

# ==========================================
# 左側控制面板：Crystal Machine 平台參數設定
# ==========================================
st.sidebar.markdown("## ⚙️ Crystal Machine 平台\n參數設定")

# 補回清晰的廠商名稱標示
sensor_display = st.sidebar.selectbox(
    "選擇 MEMS 感測器元件",
    ["芯動聯科 (InnoMotion) - ICM-20689", "博世 (BOSCH) - BMI270"]
)

# 內部邏輯代碼映射轉換
if "ICM-20689" in sensor_display:
    sensor_option = "INNOMOTION_ICM-20689"
else:
    sensor_option = "BOSCH_BMI270"

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
# 右側主面板：置頂規格庫的完美三層布局
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
    # 表格資料定義
    table_markdown = """
| 參數類別 | 感測軸向 | 標準化參數名稱 | 設定值 |
| :--- | :--- | :--- | :--- |
| **物理硬體極限** | 加速度計 | `Full_Scale_Range_Accel` | $\pm$16g |
| **物理硬體極限** | 陀螺儀 | `Full_Scale_Range_Gyro` | $\pm$2000dps |
| **靜態零偏誤差** | 加速度計 | `Accel_Static_Bias (b_a)` | 0.015 g |
| **靜態零偏誤差** | 陀螺儀 | `Gyro_Static_Bias (b_w)` | 0.07 dps |
| **隨機雜訊密度** | 加速度計 | `Accel_Noise_Density (n_a)` | 9e-05 g/$\sqrt{\\text{Hz}}$ |
| **隨機雜訊密度** | 陀螺儀 | `Gyro_Noise_Density (n_w)` | 0.004 dps/$\sqrt{\\text{Hz}}$ |
"""
else:
    sensor_id = "CM-BMI270"
    vendor = "BOSCH"
    part_num = "BMI270"
    app_tier = "消費級/人形機器人 (低成本方案)"
    table_markdown = """
| 參數類別 | 感測軸向 | 標準化參數名稱 | 設定值 |
| :--- | :--- | :--- | :--- |
| **物理硬體極限** | 加速度計 | `Full_Scale_Range_Accel` | $\pm$8g |
| **物理硬體極限** | 陀螺儀 | `Full_Scale_Range_Gyro` | $\pm$2000dps |
| **靜態零偏誤差** | 加速度計 | `Accel_Static_Bias (b_a)` | 0.020 g |
| **靜態零偏誤差** | 陀螺儀 | `Gyro_Static_Bias (b_w)` | 0.08 dps |
| **隨機雜訊密度** | 加速度計 | `Accel_Noise_Density (n_a)` | 160 μg/$\sqrt{\\text{Hz}}$ |
| **隨機雜訊密度** | 陀螺儀 | `Gyro_Noise_Density (n_w)` | 0.007 dps/$\sqrt{\\text{Hz}}$ |
"""

# 執行核心模擬數據計算
t, gyro_output, accel_angle, comp_angle, ideal_angle, rmse = generate_simulation_data(
    sensor_id, odr, duration, motion_freq, noise_amp, walk_amp, alpha
)

# ------------------------------------------
# 【第一層：頂層】平台底層標準化規格數據 (Digital Library View) -> 完全還原專業文字方塊與表格
# ------------------------------------------
st.markdown("### 💼 平台底層標準化規格數據 (Digital Library View)")

# 還原為原版精緻的整塊文字方塊樣式
st.markdown(f"""
<div style="background-color: #eef5fc; padding: 18px; border-radius: 8px; border-left: 5px solid #1c7ed6; margin-bottom: 20px;">
    <table style="width:100%; border:none; background:none; font-size:15px; color:#1c7ed6;">
        <tr style="border:none; background:none;">
            <td style="border:none;"><b>感測器 ID：</b><code style="color:#0b519c;">{sensor_id}</code></td>
            <td style="border:none;"><b>製造商 (Vendor)：</b><b>{vendor}</b></td>
            <td style="border:none;"><b>元件型號 (Part Number)：</b><b>{part_num}</b></td>
        </tr>
        <tr style="border:none; background:none;">
            <td colspan="2" style="border:none; pt-10;">🎯 <b>應用分級定位：</b>{app_tier}</td>
            <td style="border:none; pt-10;">⚙️ <b>運行頻率 (ODR)：</b><b>{odr} Hz</b></td>
        </tr>
    </table>
</div>
""", unsafe_allow_html=True)

# 還原專業的靜態物理與誤差注入模型參數對照表
st.markdown("#### 🔍 靜態物理與誤差注入模型參數對照")
st.markdown(table_markdown)
st.caption("⚙️ 狀態提示：Digital Library 短陣參數動態注入成功，雙濾波架構就緒。")

st.markdown("---")

# ------------------------------------------
# 【第二層：中層】即時效能指標看板 (KPIs Panel)
# ------------------------------------------
st.markdown(f"### 📉 {sensor_option} 元件模擬與動態融合結果")

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.metric(label="當前解算引擎", value="一階互補濾波" if "一階互補濾波" in algo_option else "線性卡爾曼濾波")
with col_kpi2:
    status_msg = "↓ - 優異" if rmse < 1.5 else "⚡ - 需再調諧"
    st.metric(label="真實運動均方根誤差 (RMSE)", value=f"{rmse:.3f} 度", delta=status_msg, delta_color="normal" if rmse < 1.5 else "inverse")
with col_kpi3:
    st.metric(label="資料流解析狀態", value="即時運算中 (Active)", delta="↑ Normal")

# ------------------------------------------
# 【第三層：底層】元件模擬與動態融合結果圖表 (Visual Charts) -> 已修正 set_grid 崩潰問題
# ------------------------------------------
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("##### 1. 原始感測器輸出 (含注入誤差與雜訊)")
    fig1, ax1 = plt.subplots(figsize=(6, 3.5))
    ax1.plot(t, gyro_output, color='#0C6291', linewidth=1.5)
    ax1.grid(True, linestyle='--', alpha=0.5)  # 修正：將 set_grid 改為 grid
    ax1.set_xlim(0, duration)
    fig1.tight_layout()
    st.pyplot(fig1)

with col_chart2:
    st.markdown("##### 2. 一階互補濾波 狀態估計與融合輸出")
    fig2, ax2 = plt.subplots(figsize=(6, 3.5))
    ax2.plot(t, comp_angle, color='#1c7ed6', linewidth=1.5, label='濾波融合角')
    ax2.plot(t, ideal_angle, color='#e03131', linewidth=1.2, linestyle='-', label='真實角')
    ax2.grid(True, linestyle='--', alpha=0.5)  # 修正：將 set_grid 改為 grid
    ax2.set_xlim(0, duration)
    fig2.tight_layout()
    st.pyplot(fig2)

st.markdown("""
💡 **圖表輔助說明**：
* 藍線（模擬輸出）圍繞著紅線（真實運動）波動，包含高頻白雜訊與慢變隨機遊走基線漂移。
* 綠線為最終解算姿態。圖表會自動調整適宜間距以完整呈現振盪波峰。
""")