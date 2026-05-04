import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 頁面配置 (必須放在最前面) ---
st.set_page_config(page_title="TAD-AGE 電車電機模擬器", layout="wide")

# --- 2. 初始化資料與規格 (根據) ---
PLATFORMS = {
    "OD120": {"v": "60/72/96V", "p_peak": 14.8, "t_peak": 43, "max_rpm": 9000, "cooling": "空冷"},
    "OD140": {"v": "72/96V", "p_peak": 30.0, "t_peak": 80, "max_rpm": 9000, "cooling": "空冷"},
    "OD220": {"v": "400/800V", "p_peak": 150.0, "t_peak": 350, "max_rpm": 15000, "cooling": "水冷/油冷"}
}

# --- 3. 側邊欄配置中心 ---
st.sidebar.header("🚀 配置中心")

# 馬達平台選型器
selected_platform = st.sidebar.selectbox("主要馬達平台", list(PLATFORMS.keys()), index=1) 
spec = PLATFORMS[selected_platform]

# 模擬環境參數
st.sidebar.markdown("---")
st.sidebar.subheader("🚗 車輛環境模擬")
weight = st.sidebar.slider("整車總重 (kg)", 100, 2000, 500)
gear_ratio = st.sidebar.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
tire_radius = st.sidebar.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)

# 控制器演算法與硬體配置區塊[cite: 1]
st.sidebar.markdown("---")
with st.sidebar.expander("🛠️ 控制器演算法與硬體配置", expanded=True):
    st.subheader("核心演算法")
    st.info("已預設啟用：FOC & SVPWM")[cite: 1]
    
    enable_fw = st.toggle("弱磁控制 (Field Weakening)", value=True)[cite: 1]
    enable_regen = st.toggle("回生煞車 (Regenerative Braking)", value=False)[cite: 1]

    st.divider()
    
    st.subheader("硬體介面")
    sensor_options = ["Hall", "Encoder", "Resolver"]
    default_idx = 2 if selected_platform == "OD220" else 0
    selected_sensor = st.selectbox("反饋感測器類型", options=sensor_options, index=default_idx)[cite: 1]
    
    comm_protocols = ["CAN 2.0B", "UART"]
    if selected_platform == "OD220":
        comm_protocols.append("J1939 (高壓推薦)")[cite: 1]
    selected_comm = st.multiselect("支援通訊協議", options=comm_protocols, default=["CAN 2.0B"])[cite: 1]

# --- 4. 主畫面：TN 曲線圖表 ---
st.title(f"📈 {selected_platform} 作業特性曲線 ( TN 曲線 )")

if selected_platform == "OD220":
    st.warning("⚠️ **高壓技術對接提醒**：此平台必須配置「預充電路 (Pre-charge)」與「高壓互鎖 (HVIL)」功能。")[cite: 1]

# 模擬計算邏輯
rpms = np.linspace(0, spec["max_rpm"], 100)
torques = []
base_rpm = spec["max_rpm"] * 0.4

for r in rpms:
    if r <= base_rpm:
        t = spec["t_peak"]
    else:
        if enable_fw:
            t = spec["t_peak"] * (base_rpm / r)
        else:
            t = spec["t_peak"] * np.exp(-0.002 * (r - base_rpm))
    torques.append(t)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(rpms, torques, color='red', linewidth=2, label="Torque (Nm)")
ax.fill_between(rpms, torques, color='red', alpha=0.1)
ax.set_xlabel("Speed (RPM)")
ax.set_ylabel("Torque (Nm)")
ax.grid(True, linestyle='--', alpha=0.6)
st.pyplot(fig)

# --- 5. 數據總結 ---
st.info(f"💡 **目前配置總結**：\n"
        f"*   平台：{selected_platform} | 電壓：{spec['v']} | 冷卻：{spec['cooling']}\n"
        f"*   控制器：FOC {'+ 弱磁' if enable_fw else ''} | 感測器：{selected_sensor}\n"
        f"*   通訊：{', '.join(selected_comm)}")[cite: 1]

# --- 6. 自動化商務對接：詢價郵件生成[cite: 1] ---
st.markdown("---")
st.header("✉️ 供應商開發對接工具")

target_suppliers = "匯川技術、英威騰、精進電動" if selected_platform == "OD220" else "安乃達、天津松正"[cite: 1]

with st.expander("📝 查看自動生成之標準詢價信 (RFI/RFQ Template)", expanded=False):
    st.write(f"建議發送對象：**{target_suppliers}**")[cite: 1]
    
    email_subject = f"詢價：{selected_platform}平台_{spec['p_peak']}kW電機控制器開發需求"
    email_body = f"""您好，

我們目前正在進行【{selected_platform}】動力平台的開發規劃，希望能針對以下規格進行技術對接：

1. 應用場景：電動車驅動系統 (平台等級：{selected_platform})
2. 馬達規格：峰值功率 {spec['p_peak']}kW / 峰值扭矩 {spec['t_peak']}Nm / 最高轉速 {spec['max_rpm']}rpm
3. 控制器要求：
   - 核心演算法：FOC + SVPWM {'+ 弱磁控制' if enable_fw else ''}
   - 母線電壓：{spec['v']}
   - 冷卻方式：{spec['cooling']}
   - 感測器介面：{selected_sensor}
   - 通訊協議：{', '.join(selected_comm)}
   - 安全要求：{'需支援預充電路與 HVIL' if selected_platform == "OD220" else '標準保護機制'}

期待您的回覆。"""
    
    st.subheader("郵件主旨：")
    st.code(email_subject, language="text")
    st.subheader("郵件正文：")
    st.code(email_body, language="text")

st.write("---")
st.caption("TAD-AGE Framework | 數位孿生決策支持系統")