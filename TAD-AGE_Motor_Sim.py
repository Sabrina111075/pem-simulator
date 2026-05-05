import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 核心邏輯層：模擬與檢核算法
# ==========================================

def get_platform_specs(platform_type):
    """定義平台技術指標"""
    specs = {
        "OD120": {"p_peak": 14.8, "t_peak": 43, "rpm_max": 9000, "voltage": "60/72/96V", "cooling": "空冷"},
        "OD140": {"p_peak": 30.0, "t_peak": 80, "rpm_max": 9000, "voltage": "72/96V", "cooling": "空冷"},
        "OD220": {"p_peak": 150.0, "t_peak": 350, "rpm_max": 15000, "voltage": "400/800V", "cooling": "水冷/油冷"}
    }
    return specs.get(platform_type)

def check_compatibility(platform, sensor, voltage):
    """技術規格自動檢核"""
    alerts = []
    if platform == "OD220" and sensor != "Resolver":
        alerts.append("⚠️ OD220 建議配對 Resolver 以支援 15000rpm")
    if platform == "OD220" and voltage < 400:
        alerts.append("⚠️ OD220 為高壓平台，建議電壓 > 400V[cite: 1]")
    return alerts

# ==========================================
# 2. UI 介面層 (回歸 image_1d497d.png 佈局)
# ==========================================

st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# 側邊欄
with st.sidebar:
    st.subheader("🚀 TAD-AGE 配置中心")
    platform = st.selectbox("主要馬達平台 (Platform)", ["OD120", "OD140", "OD220"])
    
    st.markdown("---")
    st.subheader("🚗 車輛環境模擬")
    weight = st.slider("整車總重 (kg)", 500, 3000, 1300)
    gear_ratio = st.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
    tire_radius = st.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)
    slope = st.slider("模擬爬坡坡度 (%)", 0, 30, 15)
    
    with st.expander("⚙️ 控制器演算法與硬體", expanded=True):
        enable_fw = st.toggle("弱磁控制 (Field Weakening)", value=True)
        fw_gain = st.slider("弱磁擴速增益", 1.0, 1.5, 1.2) if enable_fw else 1.0
        sensor_type = st.selectbox("反饋感測器", ["Hall", "Encoder", "Resolver"])
        v_bus = st.number_input("電池系統電壓 (V)", value=72 if platform != "OD220" else 400)

# 主畫面標題與 KPI
st.title(f"🏢 {platform} 電車電機開發決策系統平台")
spec = get_platform_specs(platform)
rpm_limit = spec["rpm_max"] * fw_gain
v_max = (rpm_limit / gear_ratio) * (2 * np.pi * tire_radius) * 60 / 1000
t_wheel = spec["t_peak"] * gear_ratio
t_climb = (weight * 9.81 * np.sin(np.arctan(slope/100)) * tire_radius) / gear_ratio

c1, c2, c3, c4 = st.columns(4)
c1.metric("峰值功率", f"{spec['p_peak']} kW")
c2.metric("輪端扭矩", f"{t_wheel:.1f} Nm")
c3.metric("理論極速", f"{v_max:.1f} km/h", f"{((fw_gain-1)*100):+.0f}% 弱磁" if fw_gain > 1 else None)
c4.metric("爬坡需求扭矩", f"{t_climb:.1f} Nm", f"{(t_wheel - t_climb):.1f} 餘裕")

st.markdown("---")
# 圖表區
st.subheader("📈 系統效率區間與作業特性曲線")
rpm_range = np.linspace(0, rpm_limit, 100)
torque_curve = [spec['t_peak'] if r < spec['rpm_max'] else spec['t_peak'] * spec['rpm_max'] / r for r in rpm_range]
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(rpm_range, torque_curve, color='red', linewidth=3, label="Torque (Nm)")
ax.axhline(y=t_climb/gear_ratio, color='orange', linestyle='--', label=f"Climb Req ({slope}%)")
ax.fill_between(rpm_range, torque_curve, alpha=0.1, color='green')
ax.set_xlabel("Speed (RPM)")
ax.legend()
st.pyplot(fig)

st.markdown("---")

# ==========================================
# 3. 專業功能區：商務對接與標準詢價[cite: 1]
# ==========================================

tabs = st.tabs(["🔍 供應商自動推薦", "📋 系統 BOM", "🛡️ 認證與熱管理", "📊 標準詢價表", "✉️ 商務對接"])

with tabs[0]:
    vendor_map = {
        "OD120": "首選：安乃達 (Ananda)、天津松正 (Santroll)[cite: 1]",
        "OD140": "首選：安乃達 (Ananda)、天津松正 (Santroll)[cite: 1]",
        "OD220": "首選：匯川技術 (Inovance)、英威騰 (INVT)、精進電動 (JJE)[cite: 1]"
    }
    st.info(vendor_map[platform])
    alerts = check_compatibility(platform, sensor_type, v_bus)
    for a in alerts: st.warning(a)

with tabs[3]:
    st.write("### 📋 控制器開發橫向評估表 (樣機比測)")
    rfq_data = {
        "技術項目": ["電機型號", "母線電壓 (V)", "額定/峰值電流 (A)", "最高轉速 (rpm)", "感測器支援", "樣機交期", "NRE 費用"],
        "系統需求 (Spec)": [platform, f"{v_bus}V", "250/500A", f"{rpm_limit:.0f}", sensor_type, "4-6 週", "待定"],
        "供應商 A": ["", "", "", "", "", "", ""],
        "供應商 B": ["", "", "", "", "", "", ""]
    }
    st.table(pd.DataFrame(rfq_data))

with tabs[4]:
    st.write("### ✉️ 分級郵件模板 (正式版)")
    templates = {
        "OD120": f"主旨：【詢價】{spec['p_peak']}kW/72V 輕型電驅控制器開發 - TAD-AGE\n\n針對 OD120 平台開發，請求技術資料及樣機報價...",
        "OD140": f"主旨：【詢價】{spec['p_peak']}kW/96V 中功率控制器技術對接 - TAD-AGE\n\n針對 OD140 平台，需支援 FOC 弱磁控制與 CAN 2.0B...",
        "OD220": f"主旨：【詢價】{spec['p_peak']}kW 高壓主驅控制器開發需求 - TAD-AGE\n\n針對 OD220 高壓平台，要求支援 Resolver、J1939 及水冷散熱..."
    }
    st.code(templates[platform], language="markdown")

st.caption(f"TAD-AGE Framework | 整合模擬、風險診斷與供應鏈之工程決策系統[cite: 1]")