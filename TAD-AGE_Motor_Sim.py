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
selected_platform = st.sidebar.selectbox("主要馬達平台 (Platform)", list(PLATFORMS.keys()), index=1) 
spec = PLATFORMS[selected_platform]

st.sidebar.markdown("---")
st.sidebar.subheader("🚗 車輛環境模擬")
weight = st.sidebar.slider("整車總重 (kg)", 100, 3000, 1300)
gear_ratio = st.sidebar.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
tire_radius = st.sidebar.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)

with st.sidebar.expander("🛠️ 控制器演算法與硬體", expanded=False):
    enable_fw = st.toggle("弱磁控制 (Field Weakening)", value=True)
    selected_sensor = st.selectbox("反饋感測器", options=["Hall", "Encoder", "Resolver"], index=2 if selected_platform == "OD220" else 0)
    selected_comm = st.multiselect("通訊協議", options=["CAN 2.0B", "UART", "J1939"], default=["CAN 2.0B"])

# --- 4. 主畫面：性能儀表板 ---
st.title(f"🏢 {selected_platform} 數位孿生工程決策平台")

col1, col2, col3, col4 = st.columns(4)
wheel_torque = spec['t_peak'] * gear_ratio
top_speed = (spec['max_rpm'] * 2 * np.pi * tire_radius * 60) / (1000 * gear_ratio)

col1.metric("峰值功率", f"{spec['p_peak']} kW")
col2.metric("輪端扭矩", f"{wheel_torque:.1f} Nm")
col3.metric("理論極速", f"{top_speed:.1f} km/h")
col4.metric("冷卻需求", spec['cooling'])

# --- 5. TN 曲線與效率熱圖繪製 ---
st.markdown("---")
st.subheader("📈 系統效率區間與作業特性曲線")

rpms = np.linspace(0, spec["max_rpm"], 150)
torques = []
powers = []
base_rpm = spec["max_rpm"] * 0.4

for r in rpms:
    t = spec["t_peak"] if r <= base_rpm else spec["t_peak"] * (base_rpm / r) if enable_fw else spec["t_peak"] * np.exp(-0.002 * (r - base_rpm))
    torques.append(t)
    powers.append((t * r) / 9550)

# 模擬效率熱圖
R, T = np.meshgrid(rpms, np.linspace(0, spec["t_peak"] + 50, 100))
Z = 95 - ( (R - spec['max_rpm']*0.5)**2 / (spec['max_rpm']*200) + (T - spec['t_peak']*0.6)**2 / 100 )
Z = np.clip(Z, 70, 97)

fig, ax1 = plt.subplots(figsize=(10, 5))
cp = ax1.contourf(R, T, Z, levels=15, cmap='Greens', alpha=0.3)
fig.colorbar(cp).set_label('System Efficiency (%)')

ax1.plot(rpms, torques, color='red', linewidth=3, label="Torque (Nm)")
ax1.set_ylabel("Torque (Nm)", color='red')
ax2 = ax1.twinx()
ax2.plot(rpms, powers, color='blue', linestyle='--', linewidth=2, label="Power (kW)")
ax2.set_ylabel("Power (kW)", color='blue')
ax1.set_xlabel("Speed (RPM)")
st.pyplot(fig)
st.caption("註：綠色深淺代表系統綜合效率區間 (Sweet Spot)")

# --- 6. 整合專業決策資訊 Tab 頁面[cite: 1] ---
st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs(["📋 工程 BOM & 預算", "🛡️ 認證與熱管理", "🎯 應用適配度", "✉️ 商務對接"])

with tab1:
    st.subheader("系統初步 BOM 清單預估")
    bom_data = {
        "組件名稱": ["馬達本體", "控制器 (MCU)", "高壓線束", "感測器單元", "冷卻方案"],
        "規格/型號": [f"{selected_platform} Platform", spec['bom_mcu'], spec['bom_harness'], selected_sensor, spec['cooling']],
        "備註": ["標準件", "支持 FOC/弱磁", "屏蔽抗干擾", "位置回饋", "系統集成"]
    }
    st.table(bom_data)
    st.success(f"💰 **動力總成參考預算 (Tier-1)**：`{spec['bom_price']}`[cite: 1]")

with tab2:
    col_thermal, col_cert = st.columns(2)
    with col_thermal:
        st.subheader("🌡️ 熱管理建議")
        if "空冷" in spec['cooling']:
            st.info("當前採用空冷配置。建議 PWM 頻率設定為 8-10kHz，並確保通風道無遮擋以維持額定輸出[cite: 1]。")
        else:
            st.info(f"當前採用水/油冷配置。請確保流量 > 8L/min，進水溫度維持在 65°C 以下以發揮 {spec['p_peak']}kW 持續性能[cite: 1]。")
    
    with col_cert:
        st.subheader("🛡️ 國際認證檢核")
        for cert in spec['certs']:
            st.write(f"✅ {cert}")
        if selected_platform == "OD220":
            st.warning("高壓平台建議通過 ISO 26262 ASIL-D 功能安全認證[cite: 1]。")

with tab3:
    st.subheader("🎯 應用場景適配度分析")
    st.write(f"**建議應用領域**：{spec['desc']}[cite: 1]")
    score = "⭐⭐⭐⭐⭐" if top_speed > 100 else "⭐⭐⭐⭐"
    st.write(f"**TAD-AGE 系統評價**：{score}")
    st.progress(min(top_speed/200, 1.0))

with tab4:
    st.subheader("✉️ 自動化供應商開發信")
    st.write(f"**建議聯繫對象**：{spec['suppliers']}[cite: 1]")
    email_content = f"""您好，
我們目前正在開發【{selected_platform}】動力平台，初步參數已由 TAD-AGE 系統生成：
- 峰值需求：{spec['p_peak']}kW / {spec['t_peak']}Nm
- 控制要求：FOC 弱磁 / {selected_sensor} 感測
- 目標市場認證：{', '.join(spec['certs'])}

希望能獲取貴司 {spec['bom_mcu']} 級別控制器的相關技術手冊與報價報價。"""
    st.code(email_content, language="text")

st.caption("TAD-AGE Framework | 整合模擬、成本與合規之工程決策系統[cite: 1]")