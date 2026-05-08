import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 核心數據配置
# ==========================================

def get_platform_config(platform):
    configs = {
        "OD120": {
            "p_peak": 14.8, "t_peak": 43.0, "rpm_max": 9000, "v_bus": 72, 
            "thermal": "自然空冷 / 強制風冷",
            "vendors": [
                {"name": "安乃達 (Ananda)", "pos": "Mid-Range / 輕型電驅領導者", "tag": "成熟平台微調"},
                {"name": "天津松正 (Santroll)", "pos": "Mid-Range / 全場景解決方案", "tag": "扁線電機優勢"}
            ],
            "bom_df": pd.DataFrame({
                "組件名稱": ["定子組件", "轉子組件", "機殼結構", "減速機構", "感測系統"],
                "技術規格": ["Hairpin 扁線 / 24槽", "8極永磁轉子", "自然空冷鋁殼", "單速減速器", "Hall 感測器"],
                "預算參考 (NTD)": ["$5,400", "$3,800", "$2,000", "$4,000", "$700"]
            }),
            "total_ntd": "NT$ 15,900",
            "certs": ["IP67 防水防塵", "CE 認證指標", "過流/過溫保護"]
        },
        "OD140": {
            "p_peak": 30.0, "t_peak": 80.0, "rpm_max": 9000, "v_bus": 72,
            "thermal": "強制風冷系統",
            "vendors": [
                {"name": "安乃達 (Ananda)", "pos": "Mid-Range / 高性能兩輪", "tag": "客製化能力強"},
                {"name": "天津松正 (Santroll)", "pos": "Mid-Range / 越野與警用", "tag": "多規格適配"}
            ],
            "bom_df": pd.DataFrame({
                "組件名稱": ["定子組件", "轉子組件", "機殼結構", "減速機構", "感測系統"],
                "技術規格": ["強化型 Hairpin", "高剩磁永磁體", "強制風冷機殼", "雙速潛力機構", "Encoder 感測器"],
                "預算參考 (NTD)": ["$11,200", "$8,100", "$3,300", "$6,700", "$2,000"]
            }),
            "total_ntd": "NT$ 31,300",
            "certs": ["IP67 保護級別", "EMC Class B", "回生煞車安全機制"]
        },
        "OD220": {
            "p_peak": 150.0, "t_peak": 350.0, "rpm_max": 15000, "v_bus": 400,
            "thermal": "循環水冷 / 噴油冷卻",
            "vendors": [
                {"name": "匯川技術 (Inovance)", "pos": "High-End / 乘用主驅", "tag": "ASIL-C 安全認證"},
                {"name": "英威騰 (INVT)", "pos": "High-End / 商用車方案", "tag": "高壓高功率經驗"}
            ],
            "bom_df": pd.DataFrame({
                "組件名稱": ["定子組件", "轉子組件", "冷卻系統", "接線模組", "感測系統"],
                "技術規格": ["800V 高壓扁線", "IPM 內嵌永磁", "循環水冷/噴油", "HVIL 高壓互鎖", "Resolver 旋變"],
                "預算參考 (NTD)": ["$38,000", "$27,000", "$12,500", "$5,400", "$4,200"]
            }),
            "total_ntd": "NT$ 87,100",
            "certs": ["ASIL-C 安全等級", "預充電路 (Pre-charge)", "高壓互鎖 (HVIL)"]
        }
    }
    return configs.get(platform)

# ==========================================
# 2. UI 介面配置
# ==========================================
st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# CSS 樣式
st.markdown("""
    <style>
    .vendor-card-header {
        background-color: #1a73e8; color: white; padding: 15px; 
        border-top-left-radius: 10px; border-top-right-radius: 10px;
        font-size: 20px; font-weight: bold; text-align: center;
    }
    .vendor-card-body {
        background-color: #e8f0fe; padding: 20px; 
        border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;
        border: 1px solid #d2e3fc; margin-bottom: 10px; min-height: 120px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 左側側邊欄 ---
with st.sidebar:
    st.header("🚀 TAD-AGE 配置中心")
    platform = st.selectbox("主要馬達平台 (Platform)", ["OD120", "OD140", "OD220"])
    
    st.markdown("---")
    st.subheader("🚗 車輛環境模擬")
    weight = st.slider("整車總重 (kg)", 0, 500, 150)
    gear_ratio = st.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
    tire_radius = st.slider("輪胎半徑 (m)", 0.05, 0.6, 0.25)
    slope = st.slider("模擬爬坡坡度 (%)", 0, 35, 15)
    
    st.markdown("---")
    st.subheader("🔌 反饋感測器")
    sensor_type = st.selectbox("感測器類型 (Feedback)", ["Hall Sensor", "Encoder", "Resolver"])
    
    st.markdown("---")
    st.subheader("🔋 電池與控制器")
    conf = get_platform_config(platform)
    v_bus = st.number_input("電池系統電壓 (V)", value=conf["v_bus"])
    i_limit = st.slider("電池持續電流限制 (A)", 50, 600, 350)
    enable_fw = st.toggle("開啟弱磁控制 (Field Weakening)", value=True)

# ==========================================
# 3. 計算與指標連動
# ==========================================
fw_gain = 1.25 if enable_fw else 1.0
rpm_limit = conf["rpm_max"] * fw_gain

# 計算各項指標
t_wheel_max = conf["t_peak"] * gear_ratio
v_max_theory = (rpm_limit / gear_ratio) * (2 * np.pi * tire_radius) * 60 / 1000

# 載重爬坡需求
angle = np.arctan(slope / 100)
t_req_wheel = weight * 9.81 * np.sin(angle) * tire_radius 
t_climb_req_motor = t_req_wheel / gear_ratio

# --- 主畫面指標 (五個大指標) ---
st.title(f"🏢 {platform} 電車電機開發決策系統平台")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("平台峰值功率", f"{conf['p_peak']} kW")
m2.metric("最大輪端扭矩", f"{t_wheel_max:.1f} Nm")
m3.metric("爬坡需求扭矩", f"{t_req_wheel:.1f} Nm", delta=f"電機 {t_climb_req_motor:.1f} Nm", delta_color="inverse")
m4.metric("系統理論極速", f"{v_max_theory:.1f} km/h")
m5.metric("熱管理方式 [cite: 84]", conf['thermal'].split(" /")[0])

st.markdown("---")

# ==========================================
# 4. 圖表區塊
# ==========================================
st.subheader("📈 系統效率區間與作業特性曲線")
rpm_range = np.linspace(0, rpm_limit * 1.1, 500)
torque_curve = [conf['t_peak'] if r < conf['rpm_max']*0.6 else conf['t_peak']*(conf['rpm_max']*0.6)/r for r in rpm_range]
power_curve = [(t * r * 2 * np.pi / 60) / 1000 for t, r in zip(torque_curve, rpm_range)]

fig, ax1 = plt.subplots(figsize=(15, 7.5), dpi=100)

# 左軸：扭矩
ax1.plot(rpm_range, torque_curve, color='red', linewidth=4, label="Torque (Nm)")
ax1.axhline(y=t_climb_req_motor, color='orange', linestyle='--', linewidth=2, label=f"Climb Req ({weight}kg)")
ax1.set_ylim(0, conf['t_peak'] * 1.5)
ax1.set_ylabel("Torque (Nm)", color='red', fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor='red')

# 右軸：功率
ax2 = ax1.twinx()
ax2.plot(rpm_range, power_curve, color='blue', linestyle='-.', linewidth=3, label="Power (kW)")
ax2.set_ylim(0, conf['p_peak'] * 1.5)
ax2.set_ylabel("Power (kW)", color='blue', fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor='blue')

# 效率漸層
X, Y = np.meshgrid(np.linspace(0, rpm_limit*1.1, 100), np.linspace(0, conf['t_peak']*1.5, 100))
Z = 95 * np.exp(-((X - conf['rpm_max']*0.4)**2 / (rpm_limit**1.8) + (Y - conf['t_peak']*0.5)**2 / (conf['t_peak']**1.8)))
ax1.contourf(X, Y, Z, levels=15, cmap='Greens', alpha=0.2)

ax1.set_xlabel("Speed (RPM)", fontsize=12)
ax1.grid(True, linestyle=':', alpha=0.5)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3)

st.pyplot(fig)
st.markdown("---")

# ==========================================
# 5. 分頁功能整合
# ==========================================
tabs = st.tabs(["🔍 供應商推薦", "📋 系統 BOM (TWD)", "🛡️ 認證與熱管理", "✉️ 商務對接"])

with tabs[0]: # 供應商
    v_cols = st.columns(len(conf["vendors"]))
    for i, v in enumerate(conf["vendors"]):
        with v_cols[i]:
            st.markdown(f'<div class="vendor-card-header">{v["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="vendor-card-body">
                <p style="color: #185abc; font-weight: 600;">定位：{v['pos']}</p>
                <p style="color: #666; font-size: 14px;">優勢：{v['tag']}</p>
            </div>""", unsafe_allow_html=True)
            st.button(f"🚀 開始對接 {v['name'].split(' ')[0]}", key=f"v_btn_{i}")

with tabs[1]: # BOM 表格
    st.table(conf["bom_df"])
    st.markdown(f"""
        <div style="background-color: #f1f3f4; padding: 20px; border-radius: 10px; border-left: 5px solid #1a73e8; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 18px; font-weight: bold; color: #202124;">預算系統總成本參考 (BOM Total)</span>
            <span style="font-size: 24px; font-weight: 800; color: #d93025;">{conf['total_ntd']}</span>
        </div>
    """, unsafe_allow_html=True)

with tabs[2]: # 認證
    c_a, c_b = st.columns(2)
    with c_a: st.info(f"**🌡️ 熱管理策略**\n\n{conf['thermal']}")
    with c_b: st.success(f"**🛡️ 安全認證**\n\n" + "\n".join([f"- {c}" for c in conf["certs"]]))

with tabs[3]: # 郵件
    st.code(f"主旨：【詢價】TAD-AGE {platform} 電機系統\n載重：{weight}kg\n坡度：{slope}%\n感測器：{sensor_type}", language="markdown")

st.caption(f"TAD-AGE Framework v2.8 | 5項指標 & 感測器配置優化版")