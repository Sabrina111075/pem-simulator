import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 核心數據層：補足所有技術與供應商資料 [cite: 1, 29]
# ==========================================

def get_platform_config(platform):
    """
    獲取各平台的完整技術參數、BOM與認證需求 [cite: 29, 31, 37]
    """
    configs = {
        "OD120": {
            "p_peak": 14.8, "t_peak": 43, "rpm_max": 9000, "v_bus": "60/72/96V", "current": "250A",
            "bom": ["Hairpin 扁線定子", "永磁轉子組件", "空冷鋁殼機箱", "單速減速器", "Hall 感測器"],
            "safety": ["IP67 防水防塵", "CE 認證指標", "過流/過溫保護"],
            "thermal": "自然空冷 / 強制風冷",
            "vendors": "首選夥伴：安乃達 (Ananda)、天津松正 (Santroll) [cite: 14, 42]"
        },
        "OD140": {
            "p_peak": 30.0, "t_peak": 80, "rpm_max": 9000, "v_bus": "72/96V", "current": "350A",
            "bom": ["強化型 Hairpin 定子", "高剩磁永磁轉子", "一體化機殼", "雙速減速機構潛力", "Encoder 感測器"],
            "safety": ["IP67 保護級別", "EMC Class B", "回生煞車安全機制"],
            "thermal": "強制風冷",
            "vendors": "首選夥伴：安乃達 (Ananda)、天津松正 (Santroll) [cite: 14, 42]"
        },
        "OD220": {
            "p_peak": 150.0, "t_peak": 350, "rpm_max": 15000, "v_bus": "400/800V", "current": "500A",
            "bom": ["高壓扁線定子", "內嵌永磁 (IPM) 轉子", "水冷/油冷機殼", "高壓接線盒", "Resolver 旋變感測器"],
            "safety": ["ASIL-C 安全等級", "預充電路 (Pre-charge)", "高壓互鎖 (HVIL)", "J1939 協議"],
            "thermal": "循環水冷 / 噴油冷卻",
            "vendors": "首選夥伴：匯川技術 (Inovance)、英威騰 (INVT)、精進電動 (JJE) [cite: 15, 45]"
        }
    }
    return configs.get(platform)

# ==========================================
# 2. UI 介面層：優化佈局比例與圖表清晰度
# ==========================================

st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# --- 左側側邊欄：完整補齊缺失資料 ---
with st.sidebar:
    st.header("🚀 TAD-AGE 配置中心")
    platform = st.selectbox("主要馬達平台 (Platform)", ["OD120", "OD140", "OD220"])
    
    st.markdown("---")
    st.subheader("🚗 車輛環境模擬")
    weight = st.slider("整車總重 (kg)", 500, 3500, 1300)
    gear_ratio = st.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
    tire_radius = st.slider("輪胎半徑 (m)", 0.1, 0.6, 0.25)
    slope = st.slider("模擬爬坡坡度 (%)", 0, 35, 15)
    
    st.markdown("---")
    st.subheader("⚙️ 控制器進階配置")
    v_input = st.number_input("系統運作電壓 (V)", value=72 if platform != "OD220" else 400)
    sensor = st.selectbox("感測器類型", ["Hall", "Encoder", "Resolver"], 
                          index=2 if platform == "OD220" else 0)
    enable_fw = st.toggle("開啟弱磁控制 (Field Weakening)", value=True)
    fw_gain = st.slider("弱磁擴速增益", 1.0, 1.5, 1.25) if enable_fw else 1.0

# 載入平台完整規格 [cite: 29]
conf = get_platform_config(platform)

# --- 主畫面：標題與 KPI 指標 ---
st.title(f"🏢 {platform} 電車電機開發決策系統平台")

# 物理計算
rpm_max_eff = conf["rpm_max"] * fw_gain
v_max = (rpm_max_eff / gear_ratio) * (2 * np.pi * tire_radius) * 60 / 1000
t_wheel = conf["t_peak"] * gear_ratio
# 爬坡阻力計算
angle = np.arctan(slope / 100)
t_climb_req = (weight * 9.81 * np.sin(angle) * tire_radius) / gear_ratio

k1, k2, k3, k4 = st.columns(4)
k1.metric("峰值功率", f"{conf['p_peak']} kW")
k2.metric("輪端扭矩", f"{t_wheel:.1f} Nm")
k3.metric("理論極速", f"{v_max:.1f} km/h", f"{(fw_gain-1)*100:+.0f}% 弱磁" if fw_gain > 1 else None)
k4.metric("爬坡需求扭矩", f"{t_climb_req:.1f} Nm", f"{(t_wheel - t_climb_req):.1f} 餘裕")

st.markdown("---")

# --- 右側主圖表：加大、加寬、更清晰 ---
st.subheader("📈 系統效率區間與作業特性曲線")
# 增加採樣點讓曲線更平滑
rpm_range = np.linspace(0, rpm_max_eff * 1.1, 200)
torque_curve = [conf['t_peak'] if r < conf['rpm_max']*0.6 else conf['t_peak']*(conf['rpm_max']*0.6)/r for r in rpm_range]

# 設定圖表尺寸 (figsize 加大) 與 DPI (清晰度)
fig, ax = plt.subplots(figsize=(14, 5), dpi=100) 
ax.plot(rpm_range, torque_curve, color='#FF0000', linewidth=3.5, label="Motor Torque (Nm)")
ax.axhline(y=t_climb_req/gear_ratio, color='#FFA500', linestyle='--', linewidth=2, label=f"Climb Resistance ({slope}%)")

# 繪製效率區間背景
ax.fill_between(rpm_range, torque_curve, alpha=0.15, color='#2ECC71', label="High Efficiency Zone (>90%)")

ax.set_xlabel("Motor Speed (RPM)", fontsize=11)
ax.set_ylabel("Torque (Nm)", fontsize=11)
ax.grid(True, which='both', linestyle='--', alpha=0.4)
ax.legend(loc='upper right', frameon=True, shadow=True)
st.pyplot(fig)

st.markdown("---")

# --- 專業分頁區：補齊所有缺失資料 ---
tabs = st.tabs(["🔍 供應商自動推薦", "📋 系統 BOM", "🛡️ 認證與熱管理", "📊 標準詢價表", "✉️ 商務對接"])

with tabs[0]:
    st.write("### 🤝 推薦技術對接夥伴")
    st.success(conf['vendors'])
    st.info("💡 策略建議：採購前應要求供應商提供對應馬達之效率映射圖 (Efficiency Map) 與上位機調參工具 [cite: 36, 53] 。")

with tabs[1]:
    st.write(f"### 📋 {platform} 系統核心零件組成 (BOM)")
    st.table(pd.DataFrame({
        "零件類別": ["定子 (Stator)", "轉子 (Rotor)", "冷卻結構", "減速機", "反饋感測器"],
        "技術規格": conf['bom']
    }))

with tabs[2]:
    st.write("### 🛡️ 認證指標與熱管理策略 ")
    cl1, cl2 = st.columns(2)
    with cl1:
        st.info(f"**冷卻方式：** {conf['thermal']}")
        st.write("**防護等級：** IP67 / IP6K9K")
    with cl2:
        st.write("**系統安全機制：**")
        for s in conf['safety']: st.write(f"- {s}")

with tabs[3]:
    st.write("### 📊 控制器開發橫向評估表 (樣機比測) ")
    st.table(pd.DataFrame({
        "對比項目": ["電機型號", "母線電壓", "峰值電流", "最高轉速", "感測器支援", "樣機交期", "NRE費用"],
        "系統需求 (Spec)": [platform, conf['v_bus'], conf['current'], f"{conf['rpm_max']} rpm", sensor, "4-6 週", "待定"]
    }))

with tabs[4]:
    st.write("### ✉️ 分級郵件模板 (正式版) [cite: 49]")
    mail_subject = f"主旨：【詢價】TAD-AGE {platform} 平台電機控制器開發技術對接"
    mail_body = f"針對 {platform} 平台（{conf['p_peak']}kW），需支援 FOC 控制、弱磁擴速及 {conf['thermal']}。請提供規格書與樣機報價。"
    st.code(f"{mail_subject}\n\n{mail_body}", language="markdown")

st.caption("TAD-AGE Framework v2.2 | 整合模擬、風險診斷與供應鏈之工程決策系統 [cite: 26, 55]")