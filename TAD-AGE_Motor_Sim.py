import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 核心數據層：根據規劃文件補齊所有數據
# ==========================================

def get_platform_config(platform):
    configs = {
        "OD120": {
            "p_peak": 14.8, "t_peak": 43.0, "rpm_max": 9000, "v_bus": "60/72/96V", "current": "250A",
            "bom": ["Hairpin 扁線定子", "永磁轉子組件", "空冷鋁殼機箱", "單速減速器", "Hall 感測器"],
            "safety": ["IP67 防水防塵", "CE 認證指標", "過流/過溫保護"],
            "thermal": "自然空冷 / 強制風冷",
            "vendors": "首選夥伴：安乃達 (Ananda)、天津松正 (Santroll)"
        },
        "OD140": {
            "p_peak": 30.0, "t_peak": 80.0, "rpm_max": 9000, "v_bus": "72/96V", "current": "350A",
            "bom": ["強化型 Hairpin 定子", "高剩磁永磁轉子", "一體化機殼", "雙速減速機構", "Encoder 感測器"],
            "safety": ["IP67 保護級別", "EMC Class B", "回生煞車安全機制"],
            "thermal": "強制風冷",
            "vendors": "首選夥伴：安乃達 (Ananda)、天津松正 (Santroll)"
        },
        "OD220": {
            "p_peak": 150.0, "t_peak": 350.0, "rpm_max": 15000, "v_bus": "400/800V", "current": "500A",
            "bom": ["高壓扁線定子", "內嵌永磁 (IPM) 轉子", "水冷/油冷機殼", "高壓接線盒", "Resolver 旋變感測器"],
            "safety": ["ASIL-C 安全等級", "預充電路 (Pre-charge)", "高壓互鎖 (HVIL)", "J1939 協議"],
            "thermal": "循環水冷 / 噴油冷卻",
            "vendors": "首選夥伴：匯川技術 (Inovance)、英威騰 (INVT)、精進電動 (JJE)"
        }
    }
    return configs.get(platform)

# ==========================================
# 2. UI 介面層：恢復左側完整配置與右側專業圖表
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
    st.subheader("🔋 電池系統配置")
    v_bus = st.number_input("電池系統電壓 (V)", value=72 if platform != "OD220" else 400)
    i_limit = st.slider("電池持續電流限制 (A)", 50, 600, 350)
    
    st.markdown("---")
    st.subheader("⚙️ 控制器演算法與硬體")
    enable_fw = st.toggle("開啟弱磁控制 (Field Weakening)", value=True)
    sensor = st.selectbox("反饋感測器", ["Hall", "Encoder", "Resolver"], 
                          index=2 if platform == "OD220" else 0)
    protocol = st.multiselect("通訊協議", ["CAN 2.0B", "RS485", "J1939"], default=["CAN 2.0B"])

# 載入數據與計算
conf = get_platform_config(platform)
fw_gain = 1.25 if enable_fw else 1.0
rpm_limit = conf["rpm_max"] * fw_gain
v_max = (rpm_limit / gear_ratio) * (2 * np.pi * tire_radius) * 60 / 1000
t_wheel = conf["t_peak"] * gear_ratio
angle = np.arctan(slope / 100)
t_climb_req = (weight * 9.81 * np.sin(angle) * tire_radius) / gear_ratio

# 主畫面 KPI
st.title(f"🏢 {platform} 電車電機開發決策系統平台")
c1, c2, c3, c4 = st.columns(4)
c1.metric("峰值功率", f"{conf['p_peak']} kW")
c2.metric("輪端扭矩", f"{t_wheel:.1f} Nm")
c3.metric("理論極速", f"{v_max:.1f} km/h")
c4.metric("爬坡需求扭矩", f"{t_climb_req:.1f} Nm", f"{(t_wheel - t_climb_req):.1f} 餘裕")

st.markdown("---")

# --- 右側圖表：完全恢復 image_10ec3a.png 的專業樣式 ---
st.subheader("📈 系統效率區間與作業特性曲線")

rpm_range = np.linspace(0, rpm_limit * 1.05, 500)
# 扭矩特性計算
torque_curve = [conf['t_peak'] if r < conf['rpm_max']*0.6 else conf['t_peak']*(conf['rpm_max']*0.6)/r for r in rpm_range]
# 功率特性計算 (P = T * w)
power_curve = [(t * r * 2 * np.pi / 60) / 1000 for t, r in zip(torque_curve, rpm_range)]

# 建立雙 Y 軸圖表
fig, ax1 = plt.subplots(figsize=(15, 6), dpi=120)

# 1. 繪製左軸：Torque (紅色實線)
ax1.plot(rpm_range, torque_curve, color='red', linewidth=3.5, label="Torque (Nm)")
ax1.axhline(y=t_climb_req/gear_ratio, color='orange', linestyle='--', linewidth=2, label=f"Climb Req ({slope}%)")
ax1.set_xlabel("Speed (RPM)", fontsize=11)
ax1.set_ylabel("Torque (Nm)", color='red', fontsize=11, fontweight='bold')
ax1.tick_params(axis='y', labelcolor='red')
ax1.set_ylim(0, conf['t_peak'] * 1.3)

# 2. 繪製右軸：Power (藍色虛點線)
ax2 = ax1.twinx()
ax2.plot(rpm_range, power_curve, color='blue', linestyle='-.', linewidth=2.5, label="Power (kW)")
ax2.set_ylabel("Power (kW)", color='blue', fontsize=11, fontweight='bold')
ax2.tick_params(axis='y', labelcolor='blue')
ax2.set_ylim(0, conf['p_peak'] * 1.3)

# 3. 繪製效率區間 (漸層綠色效果)
X, Y = np.meshgrid(np.linspace(0, rpm_limit, 100), np.linspace(0, conf['t_peak'], 100))
Z = np.exp(-((X - conf['rpm_max']*0.5)**2 / (rpm_limit**2) + (Y - conf['t_peak']*0.5)**2 / (conf['t_peak']**2)))
ax1.contourf(X, Y, Z, levels=10, cmap='Greens', alpha=0.3)

# 合併圖例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', frameon=True, shadow=True)

ax1.grid(True, linestyle=':', alpha=0.5)
st.pyplot(fig)

st.markdown("---")

# --- 專業分頁區 ---
tabs = st.tabs(["🔍 供應商自動推薦", "📋 系統 BOM", "🛡️ 認證與熱管理", "📊 標準詢價表", "✉️ 商務對接"])

with tabs[0]:
    st.success(f"**{conf['vendors']}**")
    st.info("💡 建議：OD220 應優先對接具備 ASIL-C 認證經驗的供應商 [cite: 92, 100]。")

with tabs[1]:
    st.table(pd.DataFrame({"項目": ["定子", "轉子", "冷卻", "減速機", "感測器"], "規格": conf['bom']}))

with tabs[2]:
    st.info(f"**冷卻策略：** {conf['thermal']}")
    for s in conf['safety']: st.write(f"- {s} [cite: 92]")

with tabs[3]:
    st.table(pd.DataFrame({
        "對比項": ["平台型號", "母線電壓", "峰值電流", "最高轉速", "通訊方式"],
        "系統需求": [platform, f"{v_bus}V", f"{i_limit}A", f"{rpm_limit:.0f} rpm", "/".join(protocol)]
    }))

with tabs[4]:
    st.code(f"主旨：【詢價】{platform} {conf['p_peak']}kW 電機控制器開發\n內容：需支援 FOC、弱磁控制與 {protocol[0]} 通訊 [cite: 104]。", language="markdown")

st.caption("TAD-AGE Framework v2.4 | 基於 OD 系列參數與供應商矩陣整合 [cite: 110]")