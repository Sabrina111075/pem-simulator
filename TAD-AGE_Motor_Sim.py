import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 核心數據層：根據規劃文件補齊所有缺失資料
# ==========================================

def get_complete_platform_data(platform):
    """
    整合電機平台核心規格、BOM、安全認證與供應商矩陣 [cite: 28, 29, 39]
    """
    data = {
        "OD120": {
            "p_peak": 14.8, "t_peak": 43, "rpm_max": 9000, "v_bus": "60/72/96V",
            "bom": ["Hairpin 扁線定子", "永磁轉子組件", "空冷鋁殼機箱", "單速/雙速減速器", "Hall 感測器"],
            "safety": ["IP67 防水防塵", "CE 認證指標", "過流/過溫保護"],
            "thermal": "自然空冷 / 強制風冷 [cite: 29]",
            "current": "250A",
            "vendors": "首選：安乃達 (Ananda)、天津松正 (Santroll) [cite: 42]"
        },
        "OD140": {
            "p_peak": 30.0, "t_peak": 80, "rpm_max": 9000, "v_bus": "72/96V",
            "bom": ["強化型 Hairpin 定子", "高剩磁永磁轉子", "一體化空冷機殼", "雙速減速機構潛力", "Hall/Encoder感測器"],
            "safety": ["IP67 保護級別", "EMC Class B", "回生煞車安全機制 [cite: 32]"],
            "thermal": "強制風冷 [cite: 29]",
            "current": "350A",
            "vendors": "首選：安乃達 (Ananda)、天津松正 (Santroll) [cite: 42]"
        },
        "OD220": {
            "p_peak": 150.0, "t_peak": 350, "rpm_max": 15000, "v_bus": "400/800V",
            "bom": ["高壓扁線定子 ", "內嵌永磁 (IPM) 轉子", "水冷/油冷夾層機殼", "高壓接線盒", "Resolver 旋變感測器"],
            "safety": ["ASIL-C 安全等級", "預充電路 (Pre-charge) ", "高壓互鎖 (HVIL) ", "J1939 協議支援"],
            "thermal": "循環水冷 / 噴油冷卻 [cite: 29]",
            "current": "500A",
            "vendors": "首選：匯川技術 (Inovance)、英威騰 (INVT)、精進電動 (JJE) [cite: 45]"
        }
    }
    return data.get(platform)

# ==========================================
# 2. UI 介面層：恢復漂亮清晰的大圖表佈局
# ==========================================

st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# 側邊欄參數設定 (保持完整)
with st.sidebar:
    st.subheader("🚀 TAD-AGE 配置中心")
    platform = st.selectbox("主要馬達平台 (Platform)", ["OD120", "OD140", "OD220"])
    st.markdown("---")
    st.subheader("🚗 車輛環境模擬")
    weight = st.slider("整車總重 (kg)", 500, 3000, 1300)
    gear_ratio = st.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
    tire_radius = st.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)
    slope = st.slider("模擬爬坡坡度 (%)", 0, 30, 15)

# 載入選定平台的完整數據
sys = get_complete_platform_data(platform)

# 頂部 KPI 指標
st.title(f"🏢 {platform} 電車電機開發決策系統平台")
rpm_limit = sys["rpm_max"]
v_max = (rpm_limit / gear_ratio) * (2 * np.pi * tire_radius) * 60 / 1000
t_wheel = sys["t_peak"] * gear_ratio
t_climb = (weight * 9.81 * np.sin(np.arctan(slope/100)) * tire_radius) / gear_ratio

c1, c2, c3, c4 = st.columns(4)
c1.metric("峰值功率", f"{sys['p_peak']} kW")
c2.metric("輪端扭矩", f"{t_wheel:.1f} Nm")
c3.metric("理論極速", f"{v_max:.1f} km/h")
c4.metric("熱管理方式", sys['thermal'].split(" [")[0])

st.markdown("---")

# 恢復大面積清晰圖表
st.subheader("📈 系統效率區間與作業特性曲線")
rpm_range = np.linspace(0, rpm_limit * 1.1, 100)
# 模擬特性曲線 (恆扭矩 + 恆功率)
torque_curve = [sys['t_peak'] if r < rpm_limit*0.6 else sys['t_peak']*(rpm_limit*0.6)/r for r in rpm_range]

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(rpm_range, torque_curve, color='red', linewidth=3, label="Torque (Nm)")
ax.axhline(y=t_climb/gear_ratio, color='orange', linestyle='--', label=f"Climb Req ({slope}%)")
ax.fill_between(rpm_range, torque_curve, alpha=0.15, color='green', label="Efficiency Zone")
ax.set_xlabel("Speed (RPM)")
ax.set_ylabel("Torque (Nm)")
ax.grid(True, alpha=0.3)
ax.legend()
st.pyplot(fig)

st.markdown("---")

# ==========================================
# 3. 專業功能區：完整補齊缺失分頁內容
# ==========================================

tabs = st.tabs(["🔍 供應商自動推薦", "📋 系統 BOM", "🛡️ 認證與熱管理", "📊 標準詢價表", "✉️ 商務對接"])

with tabs[0]: # 供應商推薦 (補齊)
    st.write(f"### 🤝 {platform} 平台推薦對接夥伴 [cite: 39]")
    st.success(sys['vendors'])
    st.info("💡 建議策略：優先對接具備扁線電機解決方案之供應商，並要求提供上位機調參工具 [cite: 36, 55] 。")

with tabs[1]: # 系統 BOM (補齊)
    st.write(f"### 📋 {platform} 核心系統零件組成 (BOM) ")
    bom_df = pd.DataFrame({
        "零件類別": ["定子組件", "轉子組件", "冷卻結構", "減速機構", "反饋感測器"],
        "規格描述": sys['bom']
    })
    st.table(bom_df)

with tabs[2]: # 認證與熱管理 (補齊)
    st.write(f"### 🛡️ 技術認證與安全保護需求 ")
    col_l, col_r = st.columns(2)
    with col_l:
        st.info(f"**熱管理策略：** {sys['thermal']}")
        st.write("符合標準：ISO 26262, IP67 防水防塵要求")
    with col_r:
        st.write("**關鍵安全保護機制：**")
        for s in sys['safety']: st.write(f"- {s}")

with tabs[3]: # 標準詢價表 (補齊對比項)
    st.write("### 📊 控制器開發橫向評估表 (樣機比測) ")
    rfq_data = {
        "橫向評估對比項": ["電機型號", "母線電壓 (V)", "峰值電流 (A)", "最高轉速 (rpm)", "感測器類型", "樣機交期", "NRE 費用"],
        "系統需求 (Spec)": [platform, sys['v_bus'], sys['current'], f"{rpm_limit}", "Resolver" if platform=="OD220" else "Hall/Encoder", "4-6 週", "待定"],
        "供應商 A": ["-", "-", "-", "-", "-", "-", "-"],
        "供應商 B": ["-", "-", "-", "-", "-", "-", "-"]
    }
    st.table(pd.DataFrame(rfq_data))

with tabs[4]: # 商務對接 (補齊模板)
    st.write("### ✉️ 分級郵件模板 (正式詢價版) [cite: 49]")
    template = f"主旨：【詢價】{platform} {sys['p_peak']}kW 電機控制器開發技術對接\n\n內容：針對 {platform} 平台，要求支援 FOC 控制算法與 {sys['thermal'].split(' [')[0]} 散熱技術。請提供初步報價及樣機交期..."
    st.code(template, language="markdown")

st.caption("TAD-AGE Framework | 整合模擬、風險診斷與供應鏈之工程決策系統 [cite: 1]")