import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 頁面配置 ---
st.set_page_config(page_title="TAD-AGE 電車電機模擬系統", layout="wide")

# --- 2. 初始化資料與規格 (根據供應商規劃資料) ---
PLATFORMS = {
    "OD120": {
        "v": "60/72/96V", "p_peak": 14.8, "t_peak": 43, "max_rpm": 9000, 
        "cooling": "空冷", "desc": "輕量型電動機車/巡檢車"
    },
    "OD140": {
        "v": "72/96V", "p_peak": 30.0, "t_peak": 80, "max_rpm": 9000, 
        "cooling": "空冷", "desc": "高性能電動速克達/輕型三輪"
    },
    "OD220": {
        "v": "400/800V", "p_peak": 150.0, "t_peak": 350, "max_rpm": 15000, 
        "cooling": "水冷/油冷", "desc": "乘用轎車/重載 AGV/低空載人飛行器"
    }
}

# --- 3. 側邊欄配置中心 ---
st.sidebar.header("🚀 TAD-AGE 配置中心")

# 馬達平台選型
selected_platform = st.sidebar.selectbox("主要馬達平台 (Platform)", list(PLATFORMS.keys()), index=1) 
spec = PLATFORMS[selected_platform]

# 模擬環境參數
st.sidebar.markdown("---")
st.sidebar.subheader("🚗 車輛環境模擬")
weight = st.sidebar.slider("整車總重 (kg)", 100, 3000, 500)
gear_ratio = st.sidebar.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
tire_radius = st.sidebar.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)

# 控制器配置區塊
st.sidebar.markdown("---")
with st.sidebar.expander("🛠️ 控制器演算法與硬體", expanded=True):
    st.subheader("核心演算法")
    st.info("預設啟用：FOC & SVPWM")
    enable_fw = st.toggle("弱磁控制 (Field Weakening)", value=True)
    enable_regen = st.toggle("回生煞車 (Regenerative)", value=False)

    st.divider()
    st.subheader("硬體介面")
    sensor_options = ["Hall", "Encoder", "Resolver"]
    default_sensor_idx = 2 if selected_platform == "OD220" else 0
    selected_sensor = st.selectbox("反饋感測器", options=sensor_options, index=default_sensor_idx)
    
    comm_protocols = ["CAN 2.0B", "UART"]
    if selected_platform == "OD220":
        comm_protocols.append("J1939 (高壓推薦)")
    selected_comm = st.multiselect("通訊協議", options=comm_protocols, default=["CAN 2.0B"])

# --- 4. 主畫面：性能儀表板 (KPI Dashboard) ---
st.title(f"📊 {selected_platform} 數位孿生性能分析")

# 物理計算
wheel_torque = spec['t_peak'] * gear_ratio
# 極速計算: RPM * 2*pi * R * 60 / (1000 * GearRatio)
top_speed = (spec['max_rpm'] * 2 * np.pi * tire_radius * 60) / (1000 * gear_ratio)
# 峰值功率 (kW)
calc_power = spec['p_peak']

col1, col2, col3, col4 = st.columns(4)
col1.metric("峰值功率", f"{calc_power} kW")
col2.metric("輪端扭矩", f"{wheel_torque:.1f} Nm", help="經過齒輪比放大後的實際輸出")
col3.metric("理論極速", f"{top_speed:.1f} km/h", delta=f"{'符合法規' if top_speed < 120 else '高性能'}")
col4.metric("冷卻系統", spec['cooling'])

# --- 5. TN 曲線繪製 ---
st.markdown("---")
st.subheader("📈 作業特性曲線 (Torque-Speed Curve)")

if selected_platform == "OD220":
    st.warning("⚠️ **高壓安全警告**：系統檢測到高壓平台，必須配置預充電路 (Pre-charge) 與高壓互鎖 (HVIL)。")

# 計算曲線數據
rpms = np.linspace(0, spec["max_rpm"], 100)
torques = []
powers = []
base_rpm = spec["max_rpm"] * 0.4

for r in rpms:
    # 扭矩計算
    if r <= base_rpm:
        t = spec["t_peak"]
    else:
        t = spec["t_peak"] * (base_rpm / r) if enable_fw else spec["t_peak"] * np.exp(-0.002 * (r - base_rpm))
    torques.append(t)
    # 功率計算 P = T * n / 9550
    powers.append((t * r) / 9550)

fig, ax1 = plt.subplots(figsize=(10, 4))

# 扭矩軸
ax1.plot(rpms, torques, color='red', linewidth=3, label="Torque (Nm)")
ax1.set_xlabel("Speed (RPM)")
ax1.set_ylabel("Torque (Nm)", color='red')
ax1.tick_params(axis='y', labelcolor='red')
ax1.fill_between(rpms, torques, color='red', alpha=0.1)

# 功率軸
ax2 = ax1.twinx()
ax2.plot(rpms, powers, color='blue', linestyle='--', linewidth=2, label="Power (kW)")
ax2.set_ylabel("Power (kW)", color='blue')
ax2.tick_params(axis='y', labelcolor='blue')

ax1.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig)

# --- 6. 專業選型分析 ---
col_a, col_b = st.columns(2)

with col_a:
    st.info("💡 **熱管理專家建議**")
    if "空冷" in spec['cooling']:
        st.write(f"當前為「空冷」配置。在額定功率超過 30 分鐘時，建議加裝導風罩，並確保控制器的 PWM 頻率設定在 8-12kHz 以降低開關損。")
    else:
        st.write(f"當前為「水/油冷」配置。請確保冷卻液流量 > 8L/min，進水溫度維持在 65°C 以下，以發揮 {spec['p_peak']}kW 的持續性能。")

with col_b:
    st.success("🎯 **應用場景適配度**")
    st.write(f"**推薦場景**：{spec['desc']}")
    st.write(f"**系統適配度評分**：{'⭐⭐⭐⭐⭐' if top_speed > 40 else '⭐⭐⭐'}")

# --- 7. 自動化商務對接 ---
st.markdown("---")
st.header("✉️ 供應商開發對接工具")
target_suppliers = "匯川技術、英威騰、精進電動" if selected_platform == "OD220" else "安乃達、天津松正"

with st.expander("📝 生成 RFI/RFQ 詢價信模板"):
    email_body = f"""您好，
我們目前正在進行【{selected_platform}】動力平台的開發，規格如下：
1. 馬達規格：峰值功率 {spec['p_peak']}kW / 峰值扭矩 {spec['t_peak']}Nm
2. 控制器要求：FOC + SVPWM {'+ 弱磁' if enable_fw else ''}
3. 回饋與通訊：{selected_sensor} / {', '.join(selected_comm)}
4. 預計應用：{spec['desc']}
希望能獲取貴司相關控制器的產品手冊與報價。"""
    st.code(email_body, language="text")

st.caption("TAD-AGE Framework | 工業級數位孿生系統")