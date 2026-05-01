import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from motor_configs import MOTOR_PLATFORMS
from simulation_engine import calculate_torque_curve, calculate_gradeability

# 1. 頁面基礎設定
st.set_page_config(page_title="TAD-AGE 電動車電機模擬器")

# 2. 側邊欄控制
st.sidebar.header("🚀 配置中心")
motor_options = list(MOTOR_PLATFORMS.keys())

# 使用 key 確保元件獨立，並加上 on_change 強制刷新頁面
selected_id = st.sidebar.selectbox(
    "主要馬達平台", 
    motor_options, 
    key="motor_selector_final"
)

# 核心數據：直接從當前選單抓取
target_spec = MOTOR_PLATFORMS[selected_id]

st.sidebar.markdown("---")
st.sidebar.header("🚗 車輛環境模擬")
v_mass = st.sidebar.slider("整車總重 (kg)", 100, 2000, 500)
v_ratio = st.sidebar.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
v_tire = st.sidebar.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)

# 3. 主介面顯示區
st.title("⚡ TAD-AGE 電力驅動系統使用模擬器")
st.markdown("---")

# --- 重點：所有顯示文字都直接引用 selected_id 變數 ---
st.header(f"📊 即時模擬結果：{selected_id}")

# 執行物理計算
max_grade = calculate_gradeability(target_spec['peak_torque'], v_mass, v_ratio, v_tire)

# 顯示指標卡
c1, c2, c3, c4 = st.columns(4)
c1.metric("峰值扭矩", f"{target_spec['peak_torque']} Nm")
c2.metric("預估最大爬坡度", f"{max_grade}%")
c3.metric("最高轉速", f"{target_spec['max_rpm']} rpm")
c4.metric("系統功率", f"{target_spec['peak_power']} kW")

st.markdown("---")
# 這裡的 subheader 必須也包含變數
st.subheader(f"📈 {selected_id} 作業特性曲線 ( TN 曲線 )")

# 繪製圖表
rpms, torques = calculate_torque_curve(
    target_spec['peak_torque'], 
    target_spec['peak_power'], 
    target_spec['max_rpm']
)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(rpms, torques, color="#FF4B4B", linewidth=3, label="Torque (Nm)")
ax.fill_between(rpms, torques, color="#FF4B4B", alpha=0.1)

# 固定 Y 軸範圍，這樣切換時「視覺感」才會正確
ax.set_ylim(0, 450) 
ax.set_xlabel("Speed (RPM)")
ax.set_ylabel("Torque (Nm)")
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)

# 底部提示文字也加入變數驗證
st.info(f"💡 當前馬達平台：{selected_id} | 載重：{v_mass}kg | 齒輪比：{v_ratio}")
