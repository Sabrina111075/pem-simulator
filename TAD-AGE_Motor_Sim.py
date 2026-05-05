import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 核心數據層：根據規劃文件補齊資料 
# ==========================================

def get_full_system_data(platform):
    """補齊系統 BOM、認證與熱管理的核心數據 [cite: 29, 35, 37]"""
    data = {
        "OD120": {
            "p_peak": 14.8, "t_peak": 43, "rpm_max": 9000, "v_bus": "72V",
            "bom": ["Hairpin 扁線定子", "永磁轉子組件", "空冷鋁殼機箱", "單速/雙速減速器", "Hall 感測器"],
            "safety": ["IP67 防水防塵", "CE 認證指標", "過流/過溫保護"],
            "thermal": "自然空冷 / 強制風冷 [cite: 29]",
            "current": "250A"
        },
        "OD140": {
            "p_peak": 30.0, "t_peak": 80, "rpm_max": 9000, "v_bus": "96V",
            "bom": ["強化型 Hairpin 定子", "高剩磁永磁轉子", "一體化空冷機殼", "雙速減速機構潛力", "Hall/Encoder感測器"],
            "safety": ["IP67 保護級別", "EMC Class B", "回生煞車安全機制"],
            "thermal": "強制風冷 [cite: 29]",
            "current": "350A"
        },
        "OD220": {
            "p_peak": 150.0, "t_peak": 350, "rpm_max": 15000, "v_bus": "400/800V",
            "bom": ["高壓扁線定子", "內嵌永磁 (IPM) 轉子", "水冷/油冷夾層機殼", "高壓接線盒", "Resolver 旋變感測器"],
            "safety": ["ASIL-C 安全等級", "預充電路 (Pre-charge)", "高壓互鎖 (HVIL)", "J1939 協議支援"],
            "thermal": "循環水冷 / 噴油冷卻 ",
            "current": "500A"
        }
    }
    return data.get(platform)

# ==========================================
# 2. UI 介面層 (回歸穩定版佈局)
# ==========================================

st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

with st.sidebar:
    st.subheader("🚀 TAD-AGE 配置中心")
    platform = st.selectbox("主要馬達平台 (Platform)", ["OD120", "OD140", "OD220"])
    st.markdown("---")
    st.subheader("🚗 車輛環境模擬")
    weight = st.slider("整車總重 (kg)", 500, 3000, 1300)
    gear_ratio = st.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
    tire_radius = st.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)
    slope = st.slider("模擬爬坡坡度 (%)", 0, 30, 15)

# 獲取完整數據
sys_data = get_full_system_data(platform)

# KPI 顯示區
st.title(f"🏢 {platform} 電車電機開發決策系統平台")
c1, c2, c3, c4 = st.columns(4)
c1.metric("峰值功率", f"{sys_data['p_peak']} kW")
c2.metric("輪端扭矩", f"{sys_data['t_peak']*gear_ratio:.1f} Nm")
c3.metric("理論極速", f"{(sys_data['rpm_max']/gear_ratio)*2*np.pi*tire_radius*60/1000:.1f} km/h")
c4.metric("熱管理方式", sys_data['thermal'])

st.markdown("---")

# ==========================================
# 3. 功能分頁區：補齊缺失資料 [cite: 48, 49]
# ==========================================

tabs = st.tabs(["🔍 供應商自動推薦", "📋 系統 BOM", "🛡️ 認證與熱管理", "📊 標準詢價表", "✉️ 商務對接"])

with tabs[1]: # 系統 BOM
    st.write(f"### 📋 {platform} 核心系統零件組成 (BOM)")
    bom_df = pd.DataFrame({"零件類別": ["定子組件", "轉子組件", "冷卻結構", "減速機構", "反饋感測器"], "規格描述": sys_data['bom']})
    st.table(bom_df)

with tabs[2]: # 認證與熱管理
    st.write(f"### 🛡️ 認證與安全保護需求 ")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.info(f"**熱管理策略：** {sys_data['thermal']}")
        st.write("符合標準：ISO 26262, IP67 ")
    with col_s2:
        st.write("**關鍵安全機制：**")
        for s in sys_data['safety']: st.write(f"- {s}")

with tabs[3]: # 標準詢價表 
    st.write("### 📊 控制器開發橫向評估表 (樣機比測) ")
    rfq_data = {
        "技術項目": ["電機型號", "母線電壓 (V)", "峰值電流 (A)", "最高轉速 (rpm)", "感測器支援", "樣機交期", "NRE 費用"],
        "系統需求 (Spec)": [platform, sys_data['v_bus'], sys_data['current'], f"{sys_data['rpm_max']}", "Resolver" if platform=="OD220" else "Hall", "4-6 週", "待定 "],
        "供應商 A (松正)": ["-", "-", "-", "-", "-", "-", "-"],
        "供應商 B (安乃達/匯川)": ["-", "-", "-", "-", "-", "-", "-"]
    }
    st.table(pd.DataFrame(rfq_data))

with tabs[4]: # 商務對接 [cite: 49]
    st.write("### ✉️ 分級郵件模板 (正式版) [cite: 49]")
    email_text = f"主旨：【詢價】{platform} {sys_data['p_peak']}kW 電機控制器技術對接\n\n內容：針對 {platform} 平台，需支援 FOC 與 {sys_data['thermal']} 散熱技術..."
    st.code(email_text, language="markdown")

st.caption("TAD-AGE Framework | 整合模擬、風險診斷與供應鏈之工程決策系統 ")