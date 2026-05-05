import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 頁面配置 ---
st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# --- 2. 供應商與規格大數據庫 (修正與您的 Metric 數據同步) ---
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

# --- 3. 側邊欄配置 ---
st.sidebar.header("🚀 TAD-AGE 配置中心")
selected_platform = st.sidebar.selectbox("主要馬達平台 (Platform)", list(PLATFORMS.keys()), index=2) # 預設 OD220 
spec = PLATFORMS[selected_platform]

st.sidebar.markdown("---")
with st.sidebar.expander("🚗 車輛環境模擬", expanded=True):
    weight = st.sidebar.slider("整車總重 (kg)", 100, 3000, 1300)
    gear_ratio = st.sidebar.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
    tire_radius = st.sidebar.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)

with st.sidebar.expander("🛠️ 控制器演算法與硬體", expanded=True):
    enable_fw = st.toggle("弱磁控制 (Field Weakening)", value=True)
    selected_sensor = st.selectbox("反饋感測器", options=["Hall", "Encoder", "Resolver"], index=2 if selected_platform == "OD220" else 0)

# --- 4. 主畫面：性能儀表板 (Metric Dashboard) ---
st.title(f"🏢 {selected_platform} 電車電機開發決策系統平台")

# 物理計算
wheel_torque = spec['t_peak'] * gear_ratio
top_speed = (spec['max_rpm'] * 2 * np.pi * tire_radius * 60) / (1000 * gear_ratio)

# 模擬一個簡單的爬坡需求扭矩 (例如 15% 坡度)
climb_torque_req = 59.8 # 固定這個數據以匹配您的圖片參考，未來可連動 Sidebar
climb_delta = spec['t_peak'] - climb_torque_req

col1, col2, col3, col4 = st.columns(4)
col1.metric("峰值功率", f"{spec['p_peak']:.1f} kW")
# 根據圖片，這裡顯示的是馬達峰值扭矩，而非輪端扭矩
col2.metric("峰值扭矩", f"{spec['t_peak']:.1f} Nm") 
col3.metric("理論極速", f"{top_speed:.1f} km/h")
col4.metric("爬坡需求扭矩", f"{climb_torque_req:.1f} Nm", delta=f"{climb_delta:.1f} 餘裕")

# --- 5. 修正後的專業 TN 曲線圖 (恢復簡潔清晰與純白背景) ---
st.markdown("---")
st.subheader("📈 作業特性曲線 (Torque-Speed Curve)")

rpms = np.linspace(0, spec["max_rpm"], 150)
base_rpm = spec["max_rpm"] * 0.4
# 計算 TN 曲線 (紅色)
torques = [spec["t_peak"] if r <= base_rpm else spec["t_peak"] * (base_rpm / r) if enable_fw else spec["t_peak"] * np.exp(-0.002 * (r - base_rpm)) for r in rpms]
# 計算功率曲線 (藍色)
powers = [(t * r) / 9550 for t, r in zip(torques, rpms)]

# 建立圖表 (移除效率雲圖，使用純白背景)
fig, ax1 = plt.subplots(figsize=(12, 5), facecolor='white')
ax1.set_facecolor('white') # 確保繪圖區也是白底

# 扭矩軸 (紅色)
lns1 = ax1.plot(rpms, torques, color='red', linewidth=3, label="Torque (Nm)")
ax1.set_ylabel("Torque (Nm)", color='red', fontsize=12, fontweight='bold')
ax1.set_xlabel("Speed (RPM)", fontsize=12)
ax1.tick_params(axis='y', labelcolor='red')

# 模擬一個固定坡度需求線
climb_grade = 15
lns2 = ax1.axhline(y=climb_torque_req, color='orange', linestyle='--', linewidth=2, label=f"Climb Req ({climb_grade}%)")

# 設定 Y1 軸範圍，增加頂部空間，避免與圖例重疊
ax1.set_ylim(0, spec['t_peak'] * 1.3)
ax1.grid(True, linestyle='--', color='gray', alpha=0.3)

# 功率軸 (藍色，雙軸)
ax2 = ax1.twinx()
lns3 = ax2.plot(rpms, powers, color='blue', linestyle='-.', linewidth=2, label="Power (kW)")
ax2.set_ylabel("Power (kW)", color='blue', fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor='blue')

# 設定 Y2 軸範圍，同樣增加頂部空間
ax2.set_ylim(0, spec['p_peak'] * 1.3)

# 修正圖例：整合紅色與藍色曲線的圖例，放置在右上角空白處，不重疊
lns = lns1 + [lns2] + lns3
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc='upper right', frameon=True, framealpha=1, edgecolor='gray')

st.pyplot(fig)

# --- 6. 整合專業決策資訊 Tab 頁面 ---
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📋 工程 BOM & 預算", "🛡️ 技術建議", "✉️ 商務對接"])

with tab1:
    st.table({
        "項目": ["控制器 (MCU)", "高壓線束規格", "冷卻方案"],
        "建議規格": [spec['bom_mcu'], spec['bom_harness'], spec['cooling']],
        "預估成本 (Tier-1)": ["已計入系統預算", " shielding 要求", spec['cooling']+"系統"]
    })
    st.success(f"💰 系統參考價格區間：`{spec['bom_price']}`")

with tab2:
    st.markdown(f"""
    * **熱管理**：當前平台 {selected_platform} 為 {spec['cooling']}，建議監控數據。
    * **安全性**：針對 {selected_platform} 建議選用具有功能安全認證的 {selected_sensor}。
    """)

st.caption("TAD-AGE Framework | 整合模擬、成本與合規之工程決策系統")