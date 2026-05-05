import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 頁面配置 ---
st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# --- 2. 擴充版供應商與規格資料庫 ---
SUPPLIER_DB = [
    {"name": "匯川技術 (Inovance)", "type": "High-End", "target": ["OD220"], "sensors": ["Resolver", "Encoder"], "region": "CN"},
    {"name": "英威騰 (Invt)", "type": "High-End", "target": ["OD220"], "sensors": ["Resolver"], "region": "CN"},
    {"name": "精進電動 (JEE)", "type": "High-End", "target": ["OD220"], "sensors": ["Resolver"], "region": "CN"},
    {"name": "安乃達 (Ananda)", "type": "Mid-Range", "target": ["OD120", "OD140"], "sensors": ["Hall", "Encoder"], "region": "CN"},
    {"name": "天津松正 (Santroll)", "type": "Mid-Range", "target": ["OD120", "OD140"], "sensors": ["Hall"], "region": "CN"},
    {"name": "博世 (Bosch Mobility)", "type": "Global-Tier1", "target": ["OD220"], "sensors": ["Resolver"], "region": "DE"},
]

PLATFORMS = {
    "OD120": {"v_req": "Low", "p_peak": 14.8, "t_peak": 43, "max_rpm": 9000, "cooling": "空冷", "price_lv": "Mid-Range"},
    "OD140": {"v_req": "Low", "p_peak": 30.0, "t_peak": 80, "max_rpm": 9000, "cooling": "空冷", "price_lv": "Mid-Range"},
    "OD220": {"v_req": "High", "p_peak": 150.0, "t_peak": 350, "max_rpm": 15000, "cooling": "水冷/油冷", "price_lv": "High-End"}
}

# --- 3. 供應商自動篩選邏輯函式 ---
def get_recommended_suppliers(platform_name, sensor_type):
    """根據馬達平台與感測器類型自動篩選建議供應商"""
    recommendations = []
    for s in SUPPLIER_DB:
        # 條件 1: 平台匹配 (OD220 找高壓供應商, OD120/140 找中低壓)
        platform_match = platform_name in s["target"]
        # 條件 2: 感測器支援匹配 (例如選 Hall 時，排除只做高階 Resolver 的供應商)
        sensor_match = sensor_type in s["sensors"]
        
        if platform_match and sensor_match:
            recommendations.append(s)
    return recommendations

# --- 4. 側邊欄配置 ---
st.sidebar.header("🚀 TAD-AGE 配置中心")
selected_p = st.sidebar.selectbox("主要馬達平台", list(PLATFORMS.keys()), index=2)
spec = PLATFORMS[selected_p]

with st.sidebar.expander("環境與硬體設定", expanded=True):
    weight = st.sidebar.slider("整車總重 (kg)", 100, 3000, 1300)
    gear_ratio = st.sidebar.slider("齒輪比", 1.0, 15.0, 8.0)
    tire_radius = st.sidebar.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)
    selected_sensor = st.sidebar.selectbox("反饋感測器", ["Resolver", "Hall", "Encoder"])

# --- 5. 主畫面標題與風險診斷 ---
st.title(f"🏢 {selected_p} 電車電機開發決策系統平台")

# 專業風險診斷
if selected_p == "OD220" and selected_sensor == "Hall":
    st.error("⚠️ **技術對接風險**：OD220 屬於高轉速高壓平台，選用 Hall 感測器將導致 ASIL-D 認證失效與高速震動風險。")

# --- 6. 核心計算與圖表 ---
wheel_torque = spec['t_peak'] * gear_ratio
top_speed = (spec['max_rpm'] * 2 * np.pi * tire_radius * 60) / (1000 * gear_ratio)

col1, col2, col3 = st.columns(3)
col1.metric("峰值功率", f"{spec['p_peak']} kW")
col2.metric("輪端扭矩", f"{wheel_torque:.1f} Nm")
col3.metric("理論極速", f"{top_speed:.1f} km/h")

# TN 曲線簡化繪製
rpms = np.linspace(0, spec["max_rpm"], 100)
torques = [spec["t_peak"] if r <= spec["max_rpm"]*0.4 else spec["t_peak"]*(spec["max_rpm"]*0.4/r) for r in rpms]
fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(rpms, torques, color='red', lw=2)
ax.set_ylabel("Torque (Nm)")
st.pyplot(fig)

# --- 7. 下一步：供應商自動篩選器介面 ---
st.markdown("---")
st.subheader("🔍 供應商自動推薦系統")

# 呼叫篩選函式
recommended_list = get_recommended_suppliers(selected_p, selected_sensor)

if not recommended_list:
    st.warning("❌ 目前配置組合 (平台 + 感測器) 查無推薦供應商，請檢查選型相容性。")
else:
    cols = st.columns(len(recommended_list))
    for idx, supplier in enumerate(recommended_list):
        with cols[idx]:
            st.info(f"**{supplier['name']}**")
            st.write(f"定位：`{supplier['type']}`")
            st.write(f"總部：{supplier['region']}")
            if st.button(f"生成對接信內容", key=f"btn_{idx}"):
                st.session_state.target_mail = supplier['name']

# --- 8. 修正後的資料頁面 (Tabs) ---
st.markdown("---")
t1, t2, t3 = st.tabs(["📋 系統 BOM", "🛡️ 技術建議", "✉️ 自動化對接"])

with t1:
    st.write(f"基於 **{selected_p}** 平台的建議配置清單：")
    st.table({
        "項目": ["控制器 (MCU)", "線束規格", "感測器方案"],
        "建議": [f"{spec['price_lv']} 級別", "高壓屏蔽線" if spec['v_req']=="High" else "標準線束", selected_sensor]
    })

with t2:
    st.markdown(f"""
    *   **熱管理**：當前為 {spec['cooling']}，建議監控數據。
    *   **安全性**：{selected_p} 建議搭配 {selected_sensor} 進行功能安全評估。
    """)

with t3:
    if 'target_mail' in st.session_state:
        st.success(f"已準備好與 **{st.session_state.target_mail}** 的溝通信件模板：")
        st.code(f"您好，我們正在開發 {selected_p} 平台，需要支援 {selected_sensor} 的控制器方案...")
    else:
        st.write("請點擊上方供應商卡片中的按鈕來生成信件。")

st.caption("TAD-AGE Framework | 智能供應商媒合引擎已啟動")