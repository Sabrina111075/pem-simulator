import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 核心數據配置 (依據總結規劃文件補齊)
# ==========================================

def get_platform_config(platform):
    configs = {
        "OD120": {
            "p_peak": 14.8, "t_peak": 43.0, "rpm_max": 9000, "v_bus": "60/72/96V", "current": "250A",
            "bom": ["Hairpin 扁線定子", "永磁轉子組件", "空冷鋁殼機殼", "單速減速器", "Hall 感測器"],
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
# 2. UI 佈局與側邊欄 (完整補齊缺失項)
# ==========================================

st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

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

conf = get_platform_config(platform)
fw_gain = 1.25 if enable_fw else 1.0
rpm_limit = conf["rpm_max"] * fw_gain

# 計算 KPI
t_wheel = conf["t_peak"] * gear_ratio
angle = np.arctan(slope / 100)
t_climb_req = (weight * 9.81 * np.sin(angle) * tire_radius) / gear_ratio
v_max = (rpm_limit / gear_ratio) * (2 * np.pi * tire_radius) * 60 / 1000

# 主畫面標題與指標
st.title(f"🏢 {platform} 電車電機開發決策系統平台")
c1, c2, c3, c4 = st.columns(4)
c1.metric("峰值功率", f"{conf['p_peak']} kW")
c2.metric("輪端扭矩", f"{t_wheel:.1f} Nm")
c3.metric("理論極速", f"{v_max:.1f} km/h")
c4.metric("熱管理方式", conf['thermal'].split(" /")[0])

st.markdown("---")

# ==========================================
# 3. 圖表優化：解決扁平問題，提升清晰度
# ==========================================

st.subheader("📈 系統效率區間與作業特性曲線")

rpm_range = np.linspace(0, rpm_limit * 1.1, 500)
torque_curve = [conf['t_peak'] if r < conf['rpm_max']*0.6 else conf['t_peak']*(conf['rpm_max']*0.6)/r for r in rpm_range]
power_curve = [(t * r * 2 * np.pi / 60) / 1000 for t, r in zip(torque_curve, rpm_range)]

# 提高 figsize 高度比例與 DPI
fig, ax1 = plt.subplots(figsize=(15, 7.5), dpi=130)

# --- 左軸：扭矩 ---
ax1.plot(rpm_range, torque_curve, color='red', linewidth=4, label="Torque (Nm)")
ax1.axhline(y=t_climb_req/gear_ratio, color='orange', linestyle='--', linewidth=2.5, label=f"Climb Req ({slope}%)")

# 優化關鍵：大幅提高 Y 軸上限，避免扁平感
ax1.set_ylim(0, conf['t_peak'] * 1.5) 
ax1.set_ylabel("Torque (Nm)", color='red', fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor='red')

# --- 右軸：功率 ---
ax2 = ax1.twinx()
ax2.plot(rpm_range, power_curve, color='blue', linestyle='-.', linewidth=3, label="Power (kW)")
# 同步提高功率軸上限
ax2.set_ylim(0, conf['p_peak'] * 1.5)
ax2.set_ylabel("Power (kW)", color='blue', fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor='blue')

# --- 效率背景 (漸層效果) ---
X, Y = np.meshgrid(np.linspace(0, rpm_limit*1.1, 100), np.linspace(0, conf['t_peak']*1.5, 100))
Z = 95 * np.exp(-((X - conf['rpm_max']*0.4)**2 / (rpm_limit**1.8) + (Y - conf['t_peak']*0.5)**2 / (conf['t_peak']**1.8)))
contour = ax1.contourf(X, Y, Z, levels=15, cmap='Greens', alpha=0.25)
cbar = fig.colorbar(contour, ax=ax2, pad=0.08)
cbar.set_label("Efficiency (%)", rotation=270, labelpad=15)

# 圖表細節優化
ax1.set_xlabel("Speed (RPM)", fontsize=12)
ax1.grid(True, which='both', linestyle=':', alpha=0.6)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=3, frameon=True, shadow=True)

st.pyplot(fig)

st.markdown("---")

# ==========================================
# 4. 專業功能分頁 (依據規劃文件補齊)
# ==========================================

tabs = st.tabs(["🔍 供應商自動推薦", "📋 系統 BOM", "🛡️ 認證與熱管理", "📊 標準詢價表", "✉️ 商務對接"])

with tabs[0]: # 供應商自動推薦
    st.markdown("### 🏆 推薦合作供應商方案")
    
    # 根據平台定義供應商數據
    vendor_data = {
        "OD120": [
            {"name": "安乃達 (Ananda)", "pos": "Mid-Range / 輕型電驅領導者", "tag": "成熟平台微調"},
            {"name": "天津松正 (Santroll)", "pos": "Mid-Range / 全場景解決方案", "tag": "扁線電機優勢"}
        ],
        "OD140": [
            {"name": "安乃達 (Ananda)", "pos": "Mid-Range / 高性能兩輪", "tag": "客製化能力強"},
            {"name": "天津松正 (Santroll)", "pos": "Mid-Range / 越野與警用", "tag": "多規格適配"}
        ],
        "OD220": [
            {"name": "匯川技術 (Inovance)", "pos": "High-End / 工業與乘用主驅", "tag": "ASIL-C 安全認證"},
            {"name": "英威騰 (INVT)", "pos": "High-End / 商用車解決方案", "tag": "高壓高功率經驗"}
        ]
    }
    
    current_vendors = vendor_data.get(platform, [])
    v_cols = st.columns(len(current_vendors))
    
    for i, v in enumerate(current_vendors):
        with v_cols[i]:
            # 使用自定義 HTML 模擬 image_100b5c.png 的視覺效果
            st.markdown(f"""
                <div style="
                    background-color: #1a73e8; 
                    color: white; 
                    padding: 15px; 
                    border-top-left-radius: 10px; 
                    border-top-right-radius: 10px;
                    font-size: 20px;
                    font-weight: bold;
                    text-align: center;
                ">
                    {v['name']}
                </div>
                <div style="
                    background-color: #e8f0fe; 
                    padding: 20px; 
                    border-bottom-left-radius: 10px; 
                    border-bottom-right-radius: 10px;
                    border: 1px solid #d2e3fc;
                    margin-bottom: 10px;
                ">
                    <p style="color: #185abc; font-weight: 500; margin-bottom: 5px;">📍 定位：{v['pos']}</p>
                    <p style="color: #666; font-size: 14px;">🏷️ 核心：{v['tag']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 對接按鈕
            if st.button(f"🚀 開始對接 {v['name'].split(' ')[0]}", key=f"v_btn_{i}"):
                st.success(f"已將 {platform} 技術矩陣發送至 {v['name']} 預約對接窗口")

    st.markdown("---")
    st.info(f"💡 **供應商開發策略：** 針對 **{platform}** 平台，優先尋找具備 **Hairpin (扁線)** 繞組與 **FOC** 算法能力的夥伴 。")

with tabs[1]: # 系統 BOM 分頁優化版
    st.markdown("### 🛠️ 核心系統零件組成 (Bill of Materials)")
    
    # 根據規劃文件定義各平台的詳細 BOM 資料
    bom_details = {
        "OD120": {
            "title": "OD120 輕型電驅系統核心件",
            "items": [
                {"part": "定子組件", "spec": "Hairpin 扁線繞組 / 24槽"},
                {"part": "轉子組件", "spec": "8極永磁轉子 (PM)"},
                {"part": "機殼結構", "spec": "高導熱鋁合金 / 自然空冷"},
                {"part": "減速機構", "spec": "整合式單速減速器"},
                {"part": "感測系統", "spec": "高精度 Hall 感測器"}
            ]
        },
        "OD140": {
            "title": "OD140 中功率電驅系統核心件",
            "items": [
                {"part": "定子組件", "spec": "強化型 Hairpin 扁線繞組"},
                {"part": "轉子組件", "spec": "高剩磁永磁體 / 矽鋼片"},
                {"part": "機殼結構", "spec": "壓鑄鋁合金 / 強制風冷"},
                {"part": "減速機構", "spec": "支援雙速減速器潛力"},
                {"part": "感測系統", "spec": "Hall + Encoder 雙備援"}
            ]
        },
        "OD220": {
            "title": "OD220 高壓主驅系統核心件",
            "items": [
                {"part": "定子組件", "spec": "800V 高壓扁線繞組"},
                {"part": "轉子組件", "spec": "內嵌式永磁 (IPM)"},
                {"part": "熱管系統", "spec": "一體化水冷夾層 / 噴油"},
                {"part": "接線盒", "spec": "整合型高壓互鎖 (HVIL)"},
                {"part": "感測系統", "spec": "Resolver 旋轉變壓器"}
            ]
        }
    }

    selected_bom = bom_details.get(platform)
    
    # --- 優化後的 CSS 樣式：確保高度對齊與層次感 ---
    st.markdown(f"""
        <div style="
            background-color: #1a73e8; 
            color: white; 
            padding: 15px 25px; 
            border-top-left-radius: 12px; 
            border-top-right-radius: 12px;
            font-size: 20px;
            font-weight: 600;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            📦 {selected_bom['title']}
        </div>
        <div style="
            background-color: #ffffff; 
            border: 1px solid #e0e0e0; 
            border-bottom-left-radius: 12px; 
            border-bottom-right-radius: 12px;
            padding: 10px 0px;
            min-height: 320px; /* 固定最小高度，解決對齊問題 */
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        ">
            {"".join([f'''
            <div style="
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                padding: 15px 30px; 
                border-bottom: { '1px solid #f8f9fa' if i < len(selected_bom['items'])-1 else 'none' };
            ">
                <span style="color: #5f6368; font-weight: 500; font-size: 16px;">{item['part']}</span>
                <span style="color: #202124; font-weight: 600; font-size: 16px; background: #f1f3f4; padding: 4px 12px; border-radius: 6px;">{item['spec']}</span>
            </div>
            ''' for i, item in enumerate(selected_bom['items'])])}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(f"💡 **技術對接提示：** 以上 BOM 為 {platform} 平台之標配，若需調整減速比或變更感測器類型，請於商務對接分頁中說明。")

with tabs[2]: # 認證 [cite: 92]
    st.write(f"**冷卻策略：** {conf['thermal']}")
    st.write("**關鍵安全機制：**")
    for s in conf['safety']: st.write(f"- {s}")

with tabs[3]: # 詢價表 [cite: 103]
    st.table(pd.DataFrame({
        "對比項": ["電機平台", "電壓等級", "需求電流", "最高轉速", "通訊/調參"],
        "系統規格": [platform, f"{v_bus}V", f"{i_limit}A", f"{rpm_limit:.0f} rpm", "CAN/上位機工具"]
    }))

with tabs[4]: # 郵件模板 [cite: 104]
    st.code(f"主旨：【詢價】TAD-AGE {platform} {conf['p_peak']}kW 控制器對接\n內容：要求支援 FOC、弱磁控制與回生煞車功能...", language="markdown")

st.caption("TAD-AGE Framework v2.5 | 整合模擬、風險診斷與供應鏈之工程決策系統")