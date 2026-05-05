import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 核心邏輯層：控制器檢核與模擬算法
# ==========================================

def check_controller_compatibility(platform, sensor_type, voltage):
    """根據規劃文件進行技術規格檢核"""
    alerts = []
    recommendation = ""
    
    if platform == "OD220":
        if sensor_type != "Resolver":
            alerts.append("⚠️ OD220 平台建議配對 Resolver (旋變)[cite: 1]")
        if voltage < 400:
            alerts.append("⚠️ 電壓警告：OD220 建議使用 400V 以上高壓系統[cite: 1]")
        recommendation = "💡 推薦對接：匯川技術 (Inovance)、英威騰 (INVT)、精進電動 (JJE)[cite: 1]"
    elif platform in ["OD120", "OD140"]:
        if sensor_type == "Resolver":
            alerts.append("ℹ️ 成本優化：OD120/140 選用 Hall 或 Encoder 即可[cite: 1]")
        recommendation = "💡 推薦對接：安乃達 (Ananda)、天津松正 (Santroll)[cite: 1]"
            
    return alerts, recommendation

def simulate_motor_performance(platform_type, weight, gear_ratio, tire_radius, slope):
    """維持穩定運行的動態物理模擬邏輯"""
    specs = {
        "OD120": {"peak_p": 14.8, "peak_t": 43, "max_rpm": 9000},
        "OD140": {"peak_p": 30.0, "peak_t": 80, "max_rpm": 9000},
        "OD220": {"peak_p": 150.0, "peak_t": 350, "max_rpm": 15000}
    }
    base_spec = specs[platform_type]
    
    # 輪端扭矩 (Nm)
    wheel_torque = base_spec["peak_t"] * gear_ratio
    # 理論極速 (km/h)
    top_speed = (base_spec["max_rpm"] / gear_ratio) * (2 * np.pi * tire_radius) * 60 / 1000
    # 爬坡需求扭矩 (Nm)
    angle = np.arctan(slope / 100)
    climb_req_torque = (weight * 9.81 * np.sin(angle) * tire_radius) / gear_ratio
    
    return base_spec["peak_p"], wheel_torque, top_speed, climb_req_torque, base_spec["peak_t"], base_spec["max_rpm"]

# ==========================================
# 2. Streamlit UI 介面層 (完全回歸 image_1d497d.png 佈局)
# ==========================================

st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# 側邊欄：完整保留原始所有參數
with st.sidebar:
    st.subheader("🚀 TAD-AGE 配置中心")
    platform = st.selectbox("主要馬達平台 (Platform)", ["OD120", "OD140", "OD220"])
    
    st.markdown("---")
    st.subheader("🚗 車輛環境模擬")
    weight = st.slider("整車總重 (kg)", 500, 3000, 1300)
    gear_ratio = st.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
    tire_radius = st.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)
    
    with st.expander("📂 路況與電池模擬", expanded=False):
        slope = st.slider("模擬爬坡坡度 (%)", 0, 30, 15)
        v_bus = st.number_input("母線電壓 (V)", value=72 if platform != "OD220" else 400)
        sensor_type = st.selectbox("感測器類型", ["Hall", "Encoder", "Resolver"], index=0)

# 標題區
st.title(f"🏢 {platform} 電車電機開發決策系統平台")

# 計算數據
p_peak, t_wheel, v_max, t_climb_req, t_motor_peak, rpm_limit = simulate_motor_performance(
    platform, weight, gear_ratio, tire_radius, slope
)

# 顯示 KPI 指標卡
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("峰值功率", f"{p_peak} kW")
kpi2.metric("輪端扭矩", f"{t_wheel:.1f} Nm")
kpi3.metric("理論極速", f"{v_max:.1f} km/h")
kpi4.metric("爬坡需求扭矩", f"{t_climb_req:.1f} Nm", f"{(t_wheel - t_climb_req):.1f} 餘裕")

st.markdown("---")

# 主圖表區
st.subheader("📈 系統效率區間與作業特性曲線")
rpm_range = np.linspace(0, rpm_limit * 1.1, 100)
torque_curve = [t_motor_peak if r < rpm_limit else t_motor_peak * rpm_limit / r for r in rpm_range]
power_curve = [(t * r * 2 * np.pi / 60) / 1000 for t, r in zip(torque_curve, rpm_range)]

fig, ax1 = plt.subplots(figsize=(12, 5))
ax2 = ax1.twinx()

ax1.plot(rpm_range, torque_curve, color='red', linewidth=3, label="Torque (Nm)")
ax1.axhline(y=t_climb_req/gear_ratio, color='orange', linestyle='--', label=f"Climb Req ({slope}%)")
ax2.plot(rpm_range, power_curve, color='blue', linestyle='-.', linewidth=2, label="Power (kW)")

ax1.set_xlabel("Motor Speed (RPM)")
ax1.set_ylabel("Torque (Nm)")
ax2.set_ylabel("Power (kW)")
ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3)
ax1.grid(True, alpha=0.3)
st.pyplot(fig)

st.markdown("---")

# 商務對接與技術檢核區 (放置於下方)
st.subheader("🤝 商務與技術對接")
alerts, rec_vendor = check_controller_compatibility(platform, sensor_type, v_bus)

col_info, col_action = st.columns([2, 1])

with col_info:
    if alerts:
        for a in alerts:
            st.warning(a)
    else:
        st.success(f"✅ 控制器技術規格初步匹配成功[cite: 1]")
    
    st.info(f"📍 {rec_vendor}")

with col_action:
    if st.button("📝 生成詢價郵件模板"):
        st.code(f"主旨：{platform} 電機控制器開發技術對接\n內容：需支援 FOC、{sensor_type}、CAN 通訊協議...")

st.caption(f"最後更新：2026-05-05 | 框架版本：TAD-AGE v2.0 | 基於：{platform} 控制器技術對接規劃資料[cite: 1]")