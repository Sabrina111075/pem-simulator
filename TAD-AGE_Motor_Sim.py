import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 頁面配置 ---
st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# --- 2. 初始化資料與專業參數庫 ---
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

# --- 5. TN 曲線與動態效率熱圖繪製 ---
st.markdown("---")
st.subheader("📈 效率區間分析 (Efficiency Mapping)")

rpms = np.linspace(0, spec["max_rpm"], 150)
torques = []
powers = []
base_rpm = spec["max_rpm"] * 0.4

for r in rpms:
    t = spec["t_peak"] if r <= base_rpm else spec["t_peak"] * (base_rpm / r) if enable_fw else spec["t_peak"] * np.exp(-0.002 * (r - base_rpm))
    torques.append(t)
    powers.append((t * r) / 9550)

# 模擬效率熱圖數據
R, T = np.meshgrid(rpms, np.linspace(0, spec["t_peak"] + 50, 100))
# 模擬一個甜點區在 40-70% 轉速與扭矩位置
Z = 95 - ( (R - spec['max_rpm']*0.5)**2 / (spec['max_rpm']*200) + (T - spec['t_peak']*0.6)**2 / 100 )
Z = np.clip(Z, 70, 97)

fig, ax1 = plt.subplots(figsize=(10, 5))
# 繪製效率熱圖
cp = ax1.contourf(R, T, Z, levels=15, cmap='Greens', alpha=0.3)
cbar = fig.colorbar(cp)
cbar.set_label('System Efficiency (%)')

# 繪製扭矩與功率曲線
ax1.plot(rpms, torques, color='red', linewidth=3, label="Torque (Nm)")
ax1.set_ylabel("Torque (Nm)", color='red')
ax2 = ax1.twinx()
ax2.plot(rpms, powers, color='blue', linestyle='--', linewidth=2, label="Power (kW)")
ax2.set_ylabel("Power (kW)", color='blue')

ax1.set_ylim(0, spec['t_peak'] + 50)
ax1.set_xlabel("Speed (RPM)")
st.pyplot(fig)
st.caption("註：背景綠色區塊越深代表效率越高 (Sweet Spot)。")

# --- 6. 工程決策資訊：BOM 表與認證清單 ---
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📋 工程 BOM 清單", "🛡️ 國際認證檢核", "✉️ 供應商詢價"])

with tab1:
    st.subheader(f"系統初步 BOM 清單 (主要組件)")
    bom_data = {
        "組件名稱": ["馬達本體", "控制器 (MCU)", "高壓線束", "感測器單元", "冷卻方案"],
        "規格/型號": [f"{selected_platform} Platform", spec['bom_mcu'], spec['bom_harness'], selected_sensor, spec['cooling']],
        "估計成本 (單套)": ["諮詢供應商", "計入總預算", "計入總預算", "選配項目", "系統整合"]
    }
    st.table(bom_data)
    st.write(f"💰 **整套動力系統預算預估**：`{spec['bom_price']}` (Tier-1 參考價)")

with tab2:
    st.subheader("🛡️ 產品合規性與認證需求")
    cols = st.columns(len(spec['certs']))
    for idx, cert in enumerate(spec['certs']):
        cols[idx].info(f"**{cert}**")
    
    st.markdown("""
    **認證說明：**
    *   **ISO 26262**: 功能安全標準，{0} 建議達 ASIL-{1} 等級。
    *   **IP6k9k**: 針對高壓沖洗環境的防護認證，適用於重型車輛。
    *   **UN ECE R100**: 電動車高壓安全標準，進入歐盟市場之強制規範。
    """.format(selected_platform, "D" if selected_platform == "OD220" else "B"))

with tab3:
    email_body = f"針對【{selected_platform}】開發需求，尋求 {spec['bom_mcu']} 及相關線束之 RFI 技術資料與報價。"
    st.code(email_body, language="text")

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

st.caption("TAD-AGE Framework | 整合模擬、成本與合規之工程決策系統")