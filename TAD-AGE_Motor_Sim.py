import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 佈局與樣式配置
# ==========================================
st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# 套用自定義 CSS 以模擬圖片中的供應商卡片樣式
st.markdown("""
    <style>
    .vendor-card {
        background-color: #e8f0fe;
        border-radius: 10px;
        padding: 20px;
        text-align: left;
        color: #1a73e8;
        font-weight: bold;
        font-size: 22px;
        margin-bottom: 5px;
    }
    .vendor-pos {
        color: #666;
        font-size: 16px;
        margin-bottom: 15px;
        margin-left: 5px;
    }
    .stButton > button {
        background-color: white;
        color: #444;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 5px 20px;
        font-size: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 核心數據層 (依據規劃文件補齊)
# ==========================================
def get_platform_config(platform):
    configs = {
        "OD120": {"p_peak": 14.8, "t_peak": 43.0, "rpm_max": 9000, "v_bus": 72, "vendors": ["安乃達 (Ananda)", "天津松正 (Santroll)"], "thermal": "自然空冷"},
        "OD140": {"p_peak": 30.0, "t_peak": 80.0, "rpm_max": 9000, "v_bus": 72, "vendors": ["安乃達 (Ananda)", "天津松正 (Santroll)"], "thermal": "強制風冷"},
        "OD220": {"p_peak": 150.0, "t_peak": 350.0, "rpm_max": 15000, "v_bus": 400, "vendors": ["匯川技術 (Inovance)", "英威騰 (INVT)"], "thermal": "循環水冷 / 油冷"}
    }
    return configs.get(platform)

# --- 左側側邊欄：完整配置中心 ---
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
    st.subheader("🔋 電池與控制器")
    v_bus = st.number_input("電池系統電壓 (V)", value=get_platform_config(platform)["v_bus"])
    i_limit = st.slider("電池持續電流限制 (A)", 50, 600, 350)
    enable_fw = st.toggle("開啟弱磁控制 (Field Weakening)", value=True)

conf = get_platform_config(platform)
rpm_limit = conf["rpm_max"] * (1.25 if enable_fw else 1.0)
t_wheel = conf["t_peak"] * gear_ratio
angle = np.arctan(slope / 100)
t_climb_req = (weight * 9.81 * np.sin(angle) * tire_radius) / gear_ratio

# 主畫面
st.title(f"🏢 {platform} 電車電機開發決策系統平台")
c1, c2, c3, c4 = st.columns(4)
c1.metric("峰值功率", f"{conf['p_peak']} kW")
c2.metric("輪端扭矩", f"{t_wheel:.1f} Nm")
c3.metric("理論極速", f"{(rpm_limit/gear_ratio)*(2*np.pi*tire_radius)*0.06:.1f} km/h")
c4.metric("熱管理方式", conf['thermal'])

st.markdown("---")

# ==========================================
# 3. 圖表優化：維持挺拔比例，解決扁平感
# ==========================================
st.subheader("📈 系統效率區間與作業特性曲線")
rpm_range = np.linspace(0, rpm_limit * 1.1, 500)
torque_curve = [conf['t_peak'] if r < conf['rpm_max']*0.6 else conf['t_peak']*(conf['rpm_max']*0.6)/r for r in rpm_range]
power_curve = [(t * r * 2 * np.pi / 60) / 1000 for t, r in zip(torque_curve, rpm_range)]

fig, ax1 = plt.subplots(figsize=(15, 7.5), dpi=120)
# 提高 Y 軸上限至 1.5 倍，確保曲線不會貼頂
ax1.plot(rpm_range, torque_curve, color='red', linewidth=4, label="Torque (Nm)")
ax1.set_ylim(0, conf['t_peak'] * 1.5)
ax1.set_ylabel("Torque (Nm)", color='red', fontsize=12, fontweight='bold')

ax2 = ax1.twinx()
ax2.plot(rpm_range, power_curve, color='blue', linestyle='-.', linewidth=3, label="Power (kW)")
ax2.set_ylim(0, conf['p_peak'] * 1.5)
ax2.set_ylabel("Power (kW)", color='blue', fontsize=12, fontweight='bold')

# 效率漸層
X, Y = np.meshgrid(np.linspace(0, rpm_limit*1.1, 100), np.linspace(0, conf['t_peak']*1.5, 100))
Z = 95 * np.exp(-((X - conf['rpm_max']*0.4)**2 / (rpm_limit**1.8) + (Y - conf['t_peak']*0.5)**2 / (conf['t_peak']**1.8)))
ax1.contourf(X, Y, Z, levels=15, cmap='Greens', alpha=0.25)
ax1.grid(True, linestyle=':', alpha=0.5)
st.pyplot(fig)

st.markdown("---")

# ==========================================
# 4. 供應商推薦分頁：完全參照 image_107fde.png 修正
# ==========================================
tabs = st.tabs(["🔍 供應商自動推薦", "📋 系統 BOM", "📊 標準詢價表", "✉️ 商務對接"])

with tabs[0]:
    st.subheader("推薦合作供應商")
    v_cols = st.columns(2)
    
    for i, v_name in enumerate(conf["vendors"]):
        with v_cols[i]:
            # 供應商卡片 (淺藍底)
            st.markdown(f'<div class="vendor-card">{v_name}</div>', unsafe_allow_html=True)
            # 定位文字
            st.markdown(f'<div class="vendor-pos">定位：Mid-Range</div>', unsafe_allow_html=True)
            # 選擇對接按鈕 (白底圓角)
            st.button(f"選擇對接 {v_name.split(' ')[0]}", key=f"btn_{i}")

with tabs[1]:
    st.info(f"電機平台：{platform} | 核心採用 Hairpin 扁線繞組設計 [cite: 83]")
    st.table(pd.DataFrame({"項目": ["定子", "轉子", "冷卻"], "規格": ["高密度扁線", "內嵌式永磁", conf["thermal"]]}))

with tabs[2]:
    st.table(pd.DataFrame({
        "技術指標": ["母線電壓", "通訊協議", "算法支援"],
        "需求內容": [f"{v_bus}V", "CAN 2.0B", "FOC + 弱磁控制 [cite: 87]"]
    }))

st.caption("TAD-AGE Framework | 整合模擬與供應鏈之工程決策系統 [cite: 110]")