import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 頁面配置 ---
st.set_page_config(page_title="TAD-AGE 電車電機模擬器", layout="wide")

# --- 1. 初始化資料與規格 ---
# 資料來源：供應商開發與技術對接規劃資料
PLATFORMS = {
    "OD120": {"v": "60/72/96V", "p_peak": 14.8, "t_peak": 43, "max_rpm": 9000, "cooling": "空冷"},
    "OD140": {"v": "72/96V", "p_peak": 30.0, "t_peak": 80, "max_rpm": 9000, "cooling": "空冷"},
    "OD220": {"v": "400/800V", "p_peak": 150.0, "t_peak": 350, "max_rpm": 15000, "cooling": "水冷/油冷"}
}

# --- 2. 側邊欄配置中心 ---
st.sidebar.header("🚀 配置中心")

# 馬達平台選型器
selected_platform = st.sidebar.selectbox("主要馬達平台", list(PLATFORMS.keys()), index=1) # 預設 OD140
spec = PLATFORMS[selected_platform]

# 模擬環境參數
st.sidebar.markdown("---")
st.sidebar.subheader("🚗 車輛環境模擬")
weight = st.sidebar.slider("整車總重 (kg)", 100, 2000, 500)
gear_ratio = st.sidebar.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
tire_radius = st.sidebar.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)

# --- 3. 控制器演算法與硬體配置區塊 ---
st.sidebar.markdown("---")
with st.sidebar.expander("🛠️ 控制器演算法與硬體配置", expanded=True):
    st.subheader("核心演算法")
    st.info("已預設啟用：FOC & SVPWM")
    
    # 弱磁控制開關：影響高轉速表現
    enable_fw = st.toggle("弱磁控制 (Field Weakening)", value=True, help="進入恆功率區的關鍵演算法")
    enable_regen = st.toggle("回生煞車 (Regenerative Braking)", value=False)

    st.divider()
    
    st.subheader("硬體介面")
    # 根據選定平台動態推薦感測器
    sensor_options = ["Hall", "Encoder", "Resolver"]
    default_idx = 2 if selected_platform == "OD220" else 0
    selected_sensor = st.selectbox("反饋感測器類型", options=sensor_options, index=default_idx)
    
    # 通訊協議配置
    comm_protocols = ["CAN 2.0B", "UART"]
    if selected_platform == "OD220":
        comm_protocols.append("J1939 (高壓推薦)")
    selected_comm = st.multiselect("支援通訊協議", options=comm_protocols, default=["CAN 2.0B"])

# --- 4. 主畫面邏輯 ---
st.title(f"📈 {selected_platform} 作業特性曲線 ( TN 曲線 )")

# 高壓平台安全性提醒
if selected_platform == "OD220":
    st.warning("⚠️ **高壓技術對接提醒**：此平台必須配置「預充電路 (Pre-charge)」與「高壓互鎖 (HVIL)」功能。")

# 模擬計算邏輯
rpms = np.linspace(0, spec["max_rpm"], 100)
torques = []

# 額定轉速點計算 (假設約在 40% 的最大轉速)
base_rpm = spec["max_rpm"] * 0.4

for r in rpms:
    if r <= base_rpm:
        # 恆轉矩區
        t = spec["t_peak"]
    else:
        # 恆功率區 (受弱磁控制影響)
        if enable_fw:
            # 正常弱磁：扭矩隨轉速倒數下降
            t = spec["t_peak"] * (base_rpm / r)
        else:
            # 無弱磁：轉速超過後扭矩迅速崩潰
            t = spec["t_peak"] * np.exp(-0.002 * (r - base_rpm))
    torques.append(t)

# 繪圖
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(rpms, torques, color='red', linewidth=2, label="Torque (Nm)")
ax.fill_between(rpms, torques, color='red', alpha=0.1)
ax.set_xlabel("Speed (RPM)")
ax.set_ylabel("Torque (Nm)")
ax.set_ylim(0, spec["t_peak"] * 1.2)
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend()

st.pyplot(fig)

# --- 5. 數據總結與建議 ---
st.info(f"💡 **目前配置總結**：\n"
        f"*   平台：{selected_platform} | 電壓：{spec['v']} | 冷卻：{spec['cooling']}\n"
        f"*   控制器：FOC {'+ 弱磁' if enable_fw else ''} | 感測器：{selected_sensor}\n"
        f"*   通訊：{', '.join(selected_comm)}")

# 推薦供應商
st.subheader("🏢 推薦對接供應商")
if selected_platform == "OD220":
    st.success("**首選夥伴**：匯川技術 (Inovance)、英威騰 (INVT)、精進電動 (JJE)")
else:
    st.success("**首選夥伴**：安乃達 (Ananda)、天津松正 (Santroll)")

st.write("---")
st.caption("TAD-AGE Framework | 數位孿生決策支持系統")