import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 頁面配置 ---
st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# --- 2. 專業參數庫整合 ---
PLATFORMS = {
    "OD120": {
        "v": "60/72/96V", "p_peak": 14.8, "t_peak": 43, "max_rpm": 9000, 
        "cooling": "空冷", "desc": "輕量型電動機車/巡檢車",
        "bom_mcu": "MC-300-LV (15kW級)", "bom_harness": "35mm² 橙色高壓線", "bom_price": "USD 800 - 1,200",
        "certs": ["CE (EN15194)", "IP67", "UN ECE R85"],
        "suppliers": "安乃達、天津松正"
    },
    "OD140": {
        "v": "72/96V", "p_peak": 30.0, "t_peak": 80, "max_rpm": 9000, 
        "cooling": "空冷", "desc": "高性能電動速克達/輕型三輪",
        "bom_mcu": "MC-500-LV (35kW級)", "bom_harness": "50mm² 橙色高壓線", "bom_price": "USD 1,500 - 2,200",
        "certs": ["ASIL-B", "IP67", "ECE R10 (EMC)"],
        "suppliers": "安乃達、天津松正"
    },
    "OD220": {
        "v": "400/800V", "p_peak": 150.0, "t_peak": 350, "max_rpm": 15000, 
        "cooling": "水冷/油冷", "desc": "乘用轎車/重載 AGV/低空載人飛行器",
        "bom_mcu": "SiC-HV-Dual (160kW級)", "bom_harness": "95mm² 屏蔽高壓線", "bom_price": "USD 4,500 - 6,500",
        "certs": ["ASIL-D", "ISO 26262", "IP6k9k", "UN ECE R100"],
        "suppliers": "匯川技術、英威騰、精進電動"
    }
}

# --- 3. 側邊欄配置中心 ---
st.sidebar.header("🚀 TAD-AGE 配置中心")
selected_platform = st.sidebar.selectbox("主要馬達平台 (Platform)", list(PLATFORMS.keys()), index=2 if "OD220" in st.session_state.get("last_p", "") else 1) 
spec = PLATFORMS[selected_platform]

st.sidebar.markdown("---")
st.sidebar.subheader("🚗 車輛環境模擬")
weight = st.sidebar.slider("整車總重 (kg)", 100, 3000, 1300)
gear_ratio = st.sidebar.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
tire_radius = st.sidebar.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)

st.sidebar.markdown("---")
with st.sidebar.expander("🛣️ 路況與電池模擬", expanded=True):
    grade = st.sidebar.slider("模擬爬坡坡度 (%)", 0, 30, 15)
    battery_v = st.sidebar.number_input("電池系統電壓 (V)", value=400 if selected_platform == "OD220" else 72)
    batt_limit = st.sidebar.slider("電池持續電流限制 (A)", 50, 800, 350)

with st.sidebar.expander("🛠️ 控制器演算法與硬體", expanded=True):
    enable_fw = st.toggle("弱磁控制 (Field Weakening)", value=True)
    selected_sensor = st.selectbox("反饋感測器", options=["Hall", "Encoder", "Resolver"], index=0) # 預設選 Hall 來觸發測試
    selected_comm = st.multiselect("通訊協議", options=["CAN 2.0B", "UART", "J1939"], default=["CAN 2.0B"])

# --- 4. 主畫面：性能儀表板 ---
st.title(f"🏢 {selected_platform} 電車電機開發決策系統平台")

# 物理計算
wheel_torque = spec['t_peak'] * gear_ratio
top_speed = (spec['max_rpm'] * 2 * np.pi * tire_radius * 60) / (1000 * gear_ratio)
climb_torque_req = (weight * 9.8 * np.sin(np.arctan(grade/100)) * tire_radius) / gear_ratio

# --- 5. 技術風險診斷引擎 (Critical Risk Engine) ---
risk_alerts = []
if selected_platform == "OD220":
    if selected_sensor == "Hall":
        risk_alerts.append(("⚠️ 嚴峻風險：感測器適配度低", "OD220 高功率平台轉速達 15,000 RPM，Hall 感測器在高速下解析度不足且易受 EMC 干擾，強烈建議更換為 Resolver 以符合 ASIL-D 安全規範。"))
    if battery_v < 300:
        risk_alerts.append(("❗ 嚴重錯誤：電壓架構不匹配", f"OD220 屬於高壓平台，當前電池設定為 {battery_v}V 過低，將導致無法達到額定轉速與功率。"))
elif selected_platform == "OD140" and battery_v > 150:
    risk_alerts.append(("⚡ 注意：組件過電壓風險", "OD140 建議使用 72-96V 系統，當前設定電壓過高可能導致控制器電容或功率元件擊穿[cite: 1]。"))

# 顯示風險警示
for title, msg in risk_alerts:
    st.error(f"**{title}** \n\n {msg}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("峰值功率", f"{spec['p_peak']} kW")
col2.metric("輪端扭矩", f"{wheel_torque:.1f} Nm")
col3.metric("理論極速", f"{top_speed:.1f} km/h")
col4.metric("爬坡需求", f"{climb_torque_req:.1f} Nm", delta=f"{spec['t_peak'] - climb_torque_req:.1f} 餘裕")

# --- 6. TN 曲線與圖表 ---
st.markdown("---")
st.subheader("📈 系統效率區間與作業特性曲線")
rpms = np.linspace(0, spec["max_rpm"], 150)
torques = [spec["t_peak"] if r <= (spec["max_rpm"]*0.4) else spec["t_peak"]*(spec["max_rpm"]*0.4/r) for r in rpms]
fig, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(rpms, torques, color='red', linewidth=3)
ax1.axhline(y=climb_torque_req, color='orange', linestyle='--', label=f"{grade}% 爬坡需求")
ax1.set_xlabel("Speed (RPM)")
ax1.set_ylabel("Torque (Nm)")
st.pyplot(fig)

# --- 7. 標籤頁面 ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 工程 BOM", "🛡️ 認證與熱管理", "🎯 應用適配", "✉️ 商務對接"])

with tab2:
    st.subheader("🛡️ 安全與熱管理診斷")
    if selected_sensor == "Hall" and selected_platform == "OD220":
        st.warning("❌ 診斷結果：Hall 反饋無法通過 ISO 26262 ASIL-D 功能安全審核。[cite: 1]")
    else:
        st.success("✅ 診斷結果：感測器方案與平台等級匹配。[cite: 1]")
    st.info(f"熱管理：{spec['cooling']}模式，建議進水溫度 < 65°C[cite: 1]。")

with tab4:
    st.subheader("✉️ 供應商技術溝通建議")
    if "Hall" in selected_sensor and "OD220" in selected_platform:
        st.markdown("**💡 建議溝通點：** 詢問供應商該控制器是否支持 Resolver 軟解碼接口，以備後續方案變更。[cite: 1]")
    else:
        st.write("目前配置方案標準，可直接進行初步報價諮詢。")

st.caption("TAD-AGE Framework | 智能風險診斷引擎啟動中[cite: 1]")