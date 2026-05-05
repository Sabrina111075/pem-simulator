import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 核心數據層 (維持不變)
# ==========================================

def get_platform_config(platform):
    configs = {
        "OD120": {
            "p_peak": 14.8, "t_peak": 43, "rpm_max": 9000, "v_bus": "60/72/96V", "current": "250A",
            "bom": ["Hairpin 扁線定子", "永磁轉子組件", "空冷鋁殼機箱", "單速減速器", "Hall 感測器"],
            "safety": ["IP67 防水防塵", "CE 認證指標", "過流/過溫保護"],
            "thermal": "自然空冷 / 強制風冷",
            "vendors": "首選夥伴：安乃達 (Ananda)、天津松正 (Santroll)"
        },
        "OD140": {
            "p_peak": 30.0, "t_peak": 80, "rpm_max": 9000, "v_bus": "72/96V", "current": "350A",
            "bom": ["強化型 Hairpin 定子", "高剩磁永磁轉子", "一體化機殼", "雙速減速機構潛力", "Encoder 感測器"],
            "safety": ["IP67 保護級別", "EMC Class B", "回生煞車安全機制"],
            "thermal": "強制風冷",
            "vendors": "首選夥伴：安乃達 (Ananda)、天津松正 (Santroll)"
        },
        "OD220": {
            "p_peak": 150.0, "t_peak": 350, "rpm_max": 15000, "v_bus": "400/800V", "current": "500A",
            "bom": ["高壓扁線定子", "內嵌永磁 (IPM) 轉子", "水冷/油冷機殼", "高壓接線盒", "Resolver 旋變感測器"],
            "safety": ["ASIL-C 安全等級", "預充電路 (Pre-charge)", "高壓互鎖 (HVIL)", "J1939 協議"],
            "thermal": "循環水冷 / 噴油冷卻",
            "vendors": "首選夥伴：匯川技術 (Inovance)、英威騰 (INVT)、精進電動 (JJE)"
        }
    }
    return configs.get(platform)

# ==========================================
# 2. UI 介面層：鎖定圖表優化
# ==========================================

st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# 左側側邊欄 (資料已補齊)
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
    sensor = st.selectbox("感測器類型 [cite: 89, 90]", ["Hall", "Encoder", "Resolver"], 
                          index=2 if platform == "OD220" else 0)
    enable_fw = st.toggle("開啟弱磁控制 (Field Weakening) [cite: 87]", value=True)
    fw_gain = st.slider("弱磁擴速增益", 1.0, 1.5, 1.25) if enable_fw else 1.0

conf = get_platform_config(platform)
st.title(f"🏢 {platform} 電車電機開發決策系統平台")

# KPI 指標 (維持不變)
rpm_max_eff = conf["rpm_max"] * fw_gain
v_max = (rpm_max_eff / gear_ratio) * (2 * np.pi * tire_radius) * 60 / 1000
t_wheel = conf["t_peak"] * gear_ratio
angle = np.arctan(slope / 100)
t_climb_req = (weight * 9.81 * np.sin(angle) * tire_radius) / gear_ratio

k1, k2, k3, k4 = st.columns(4)
k1.metric("峰值功率 [cite: 84]", f"{conf['p_peak']} kW")
k2.metric("輪端扭矩", f"{t_wheel:.1f} Nm")
k3.metric("理論極速", f"{v_max:.1f} km/h")
k4.metric("熱管理方式 [cite: 84]", conf['thermal'].split(" /")[0])

st.markdown("---")

# --- 修正重點：右側圖表加大、清晰化 ---
st.subheader("📈 系統效率區間與作業特性曲線")

# 增加數據點密度確保曲線平滑且清晰
rpm_range = np.linspace(0, rpm_max_eff * 1.1, 300)
torque_curve = [conf['t_peak'] if r < conf['rpm_max']*0.6 else conf['t_peak']*(conf['rpm_max']*0.6)/r for r in rpm_range]

# 設定更大的畫布尺寸 (15x5) 並提高 DPI (120) 以提升解析度
fig, ax = plt.subplots(figsize=(15, 5), dpi=120) 

# 繪製扭矩線條
ax.plot(rpm_range, torque_curve, color='red', linewidth=4, label="Torque (Nm)")
# 繪製爬坡需求線
ax.axhline(y=t_climb_req/gear_ratio, color='orange', linestyle='--', linewidth=2.5, label=f"Climb Req ({slope}%)")

# 填充背景 (模仿原圖效率區間)
ax.fill_between(rpm_range, torque_curve, alpha=0.1, color='green', label="Efficiency Zone")

# 優化座標軸與網格
ax.set_xlabel("Motor Speed (RPM)", fontsize=12)
ax.set_ylabel("Torque (Nm)", fontsize=12)
ax.set_xlim(0, rpm_max_eff * 1.1)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc='upper right', frameon=True)

# 顯示圖表
st.pyplot(fig)

st.markdown("---")

# --- 專業分頁區 (資料維持補齊狀態) ---
tabs = st.tabs(["🔍 供應商自動推薦", "📋 系統 BOM", "🛡️ 認證與熱管理", "📊 標準詢價表", "✉️ 商務對接"])

with tabs[0]:
    st.success(f"**{conf['vendors']} [cite: 97, 100]**")
    st.info("💡 策略：尋找成熟平台進行微調，確保支援 FOC 與弱磁控制 [cite: 96, 87]。")

with tabs[1]:
    st.table(pd.DataFrame({"零件類別": ["定子", "轉子", "冷卻", "減速機", "感測器"], "規格描述": conf['bom']}))

with tabs[2]:
    st.write(f"**熱管理：** {conf['thermal']} [cite: 84]")
    st.write("**安全機制：**")
    for s in conf['safety']: st.write(f"- {s} [cite: 92]")

with tabs[3]: # 標準詢價表 [cite: 103]
    st.table(pd.DataFrame({
        "對比項目": ["電機型號", "母線電壓", "峰值電流", "最高轉速", "感測器支援"],
        "系統規格": [platform, conf['v_bus'], conf['current'], f"{conf['rpm_max']}", sensor]
    }))

with tabs[4]: # 分級郵件模板 [cite: 104]
    st.code(f"主旨：【詢價】{platform} {conf['p_peak']}kW 控制器開發\n\n內容：需支援 CAN 2.0B 與調參工具 [cite: 91]。", language="markdown")

st.caption("TAD-AGE Framework v2.3 | 基於 OD 系列控制器技術對接規劃資料整合 [cite: 81, 110]")