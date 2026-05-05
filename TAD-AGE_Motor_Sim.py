import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 頁面配置 ---
st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# --- 2. 供應商與規格大數據庫 ---
SUPPLIER_DB = [
    {"name": "匯川技術 (Inovance)", "type": "High-End", "target": ["OD220"], "sensors": ["Resolver", "Encoder"], "region": "CN"},
    {"name": "英威騰 (Invt)", "type": "High-End", "target": ["OD220"], "sensors": ["Resolver"], "region": "CN"},
    {"name": "精進電動 (JEE)", "type": "High-End", "target": ["OD220"], "sensors": ["Resolver"], "region": "CN"},
    {"name": "安乃達 (Ananda)", "type": "Mid-Range", "target": ["OD120", "OD140"], "sensors": ["Hall", "Encoder"], "region": "CN"},
    {"name": "天津松正 (Santroll)", "type": "Mid-Range", "target": ["OD120", "OD140"], "sensors": ["Hall"], "region": "CN"},
    {"name": "博世 (Bosch Mobility)", "type": "Global-Tier1", "target": ["OD220"], "sensors": ["Resolver"], "region": "DE"},
]

PLATFORMS = {
    "OD120": {
        "v": "60/72/96V", "p_peak": 14.8, "t_peak": 43, "max_rpm": 9000, 
        "cooling": "空冷", "desc": "輕量型電動機車/巡檢車",
        "bom_mcu": "MC-300-LV (15kW級)", "bom_harness": "35mm² 橙色高壓線", "bom_price": "USD 800 - 1,200",
        "certs": ["CE (EN15194)", "IP67", "UN ECE R85"]
    },
    "OD140": {
        "v": "72/96V", "p_peak": 30.0, "t_peak": 80, "max_rpm": 9000, 
        "cooling": "空冷", "desc": "高性能電動速克達/輕型三輪",
        "bom_mcu": "MC-500-LV (35kW級)", "bom_harness": "50mm² 橙色高壓線", "bom_price": "USD 1,500 - 2,200",
        "certs": ["ASIL-B", "IP67", "ECE R10 (EMC)"]
    },
    "OD220": {
        "v": "400/800V", "p_peak": 150.0, "t_peak": 350, "max_rpm": 15000, 
        "cooling": "水冷/油冷", "desc": "乘用轎車/重載 AGV/低空載人飛行器",
        "bom_mcu": "SiC-HV-Dual (160kW級)", "bom_harness": "95mm² 屏蔽高壓線", "bom_price": "USD 4,500 - 6,500",
        "certs": ["ASIL-D", "ISO 26262", "IP6k9k", "UN ECE R100"]
    }
}

# --- 3. 供應商推薦邏輯函式 ---
def get_recommended_suppliers(platform_name, sensor_type):
    return [s for s in SUPPLIER_DB if platform_name in s["target"] and sensor_type in s["sensors"]]

# --- 4. 側邊欄配置 (補齊前版功能) ---
st.sidebar.header("🚀 TAD-AGE 配置中心")
selected_platform = st.sidebar.selectbox("主要馬達平台 (Platform)", list(PLATFORMS.keys()), index=1) 
spec = PLATFORMS[selected_platform]

st.sidebar.markdown("---")
st.sidebar.subheader("🚗 車輛環境模擬")
weight = st.sidebar.slider("整車總重 (kg)", 100, 3000, 1300)
gear_ratio = st.sidebar.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
tire_radius = st.sidebar.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)

with st.sidebar.expander("🛣️ 路況與電池模擬", expanded=True):
    grade = st.sidebar.slider("模擬爬坡坡度 (%)", 0, 30, 15)
    battery_v = st.sidebar.number_input("電池系統電壓 (V)", value=400 if selected_platform == "OD220" else 72)
    batt_limit = st.sidebar.slider("電池持續電流限制 (A)", 50, 800, 350)

with st.sidebar.expander("🛠️ 控制器演算法與硬體", expanded=True):
    enable_fw = st.toggle("弱磁控制 (Field Weakening)", value=True)
    selected_sensor = st.selectbox("反饋感測器", options=["Hall", "Encoder", "Resolver"], index=2 if selected_platform == "OD220" else 0)
    selected_comm = st.multiselect("通訊協議", options=["CAN 2.0B", "UART", "J1939"], default=["CAN 2.0B"])

# --- 5. 主畫面：保留前版大圖面 UI ---
st.title(f"🏢 {selected_platform} 電車電機開發決策系統平台")

# 物理計算
wheel_torque = spec['t_peak'] * gear_ratio
top_speed = (spec['max_rpm'] * 2 * np.pi * tire_radius * 60) / (1000 * gear_ratio)
climb_torque_req = (weight * 9.8 * np.sin(np.arctan(grade/100)) * tire_radius) / gear_ratio

# 技術風險診斷警告
if selected_platform == "OD220" and selected_sensor == "Hall":
    st.error("⚠️ **技術對接風險**：OD220 高壓平台不建議搭配 Hall 感測器，將導致 ASIL 認證失敗。")

# 大圖面四指標
col1, col2, col3, col4 = st.columns(4)
col1.metric("峰值功率", f"{spec['p_peak']} kW")
col2.metric("輪端扭矩", f"{wheel_torque:.1f} Nm")
col3.metric("理論極速", f"{top_speed:.1f} km/h", delta="高性能" if top_speed > 100 else None)
col4.metric("爬坡需求扭矩", f"{climb_torque_req:.1f} Nm", delta=f"{spec['t_peak'] - climb_torque_req:.1f} 餘裕")

# --- 6. 專業 TN 曲線圖 ---
st.markdown("---")
st.subheader("📈 系統效率區間與作業特性曲線")

rpms = np.linspace(0, spec["max_rpm"], 150)
torques = [spec["t_peak"] if r <= (spec["max_rpm"]*0.4) else spec["t_peak"]*(spec["max_rpm"]*0.4/r) for r in rpms]
powers = [(t * r) / 9550 for t, r in zip(torques, rpms)]

# 效率熱圖背景計算
R, T = np.meshgrid(rpms, np.linspace(0, spec["t_peak"] + 50, 100))
Z = 95 - ( (R - spec['max_rpm']*0.5)**2 / (spec['max_rpm']*200) + (T - spec['t_peak']*0.6)**2 / 100 )
Z = np.clip(Z, 70, 97)

fig, ax1 = plt.subplots(figsize=(12, 5))
cp = ax1.contourf(R, T, Z, levels=15, cmap='Greens', alpha=0.3)
fig.colorbar(cp).set_label('Efficiency (%)')

ax1.plot(rpms, torques, color='red', linewidth=4, label="Torque (Nm)")
ax1.axhline(y=climb_torque_req, color='orange', linestyle='--', label=f"{grade}% 爬坡需求")
ax1.set_ylabel("Torque (Nm)", color='red', fontsize=12)
ax1.set_xlabel("Speed (RPM)", fontsize=12)

ax2 = ax1.twinx()
ax2.plot(rpms, powers, color='blue', linestyle='--', linewidth=2, label="Power (kW)")
ax2.set_ylabel("Power (kW)", color='blue', fontsize=12)
ax1.legend(loc='upper right')

st.pyplot(fig)

# --- 7. 下方專業模塊：供應商推薦與決策資訊 ---
st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs(["🔍 供應商自動推薦", "📋 系統 BOM", "🛡️ 認證與熱管理", "✉️ 商務對接"])

with tab1:
    recs = get_recommended_suppliers(selected_platform, selected_sensor)
    if not recs:
        st.warning("❌ 當前組合無匹配供應商，請考慮升級感測器方案。")
    else:
        st.subheader("推薦合作供應商")
        cols = st.columns(len(recs))
        for i, s in enumerate(recs):
            with cols[i]:
                st.info(f"**{s['name']}**")
                st.write(f"等級：{s['type']}")
                if st.button(f"選擇對接 {s['name']}", key=f"rec_{i}"):
                    st.session_state.contact = s['name']

with tab2:
    st.table({
        "組件": ["馬達本體", "控制器 (MCU)", "線束規格", "感測器方案"],
        "規格": [f"{selected_platform} Platform", spec['bom_mcu'], spec['bom_harness'], selected_sensor],
        "成本預估": ["系統核心", "計入總預算", "屏蔽要求", "技術對接"]
    })
    st.success(f"💰 預計系統總成本區間：{spec['bom_price']}")

with tab3:
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("🌡️ 熱管理建議")
        st.info(f"配置：{spec['cooling']}。建議 {'流量 > 8L/min' if '水' in spec['cooling'] else 'PWM 8-12kHz'}。")
    with c_right:
        st.subheader("🛡️ 國際認證檢核")
        for cert in spec['certs']: st.write(f"✅ {cert}")

with tab4:
    target = st.session_state.get('contact', '未選擇')
    st.write(f"**對接對象：** {target}")
    st.code(f"針對 {selected_platform} 平台開發，請求 {spec['bom_mcu']} 之技術資料...[電池電壓: {battery_v}V]", language="text")

st.caption("TAD-AGE Framework | 整合模擬、風險診斷與供應鏈之工程決策系統")