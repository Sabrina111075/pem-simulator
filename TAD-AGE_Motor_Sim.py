import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. 核心邏輯層：控制器檢核與模擬算法
# ==========================================

def check_controller_compatibility(platform, sensor_type, voltage):
    """根據文件 進行供應商技術規格檢核"""
    alerts = []
    recommendation = ""
    
    if platform == "OD220":
        # OD220 必須支援 Resolver 與高壓保護
        if sensor_type != "Resolver":
            alerts.append("⚠️ 警告：OD220 高功平台必須配對 Resolver (旋變) 以支援 15000rpm")
        if voltage < 400:
            alerts.append("⚠️ 電壓警報：OD220 為高壓平台，建議母線電壓 400V~800V[cite: 1]")
        alerts.append("ℹ️ 技術需求：需具備 Pre-charge (預充) 與 HVIL (高壓互鎖)[cite: 1]")
        recommendation = "💡 推薦對接：匯川技術 (Inovance)、英威騰 (INVT)[cite: 1]"
        
    elif platform in ["OD120", "OD140"]:
        # 低壓平台支援 Hall 或 Encoder[cite: 1]
        if sensor_type == "Resolver":
            alerts.append("ℹ️ 成本建議：OD120/140 建議選用 Hall 或 Encoder 即可[cite: 1]")
        recommendation = "💡 推薦對接：安乃達 (Ananda)、天津松正 (Santroll)[cite: 1]"
            
    return alerts, recommendation

def simulate_motor_performance(v_bus, gear_ratio, tire_radius, weight, slope, platform_type, fw_gain):
    """模擬電機性能與弱磁擴速效果[cite: 1]"""
    # 根據平台定義基礎參數[cite: 1]
    specs = {
        "OD120": {"peak_p": 14.8, "peak_t": 43, "max_rpm": 9000},
        "OD140": {"peak_p": 30.0, "peak_t": 80, "max_rpm": 9000},
        "OD220": {"peak_p": 150.0, "peak_t": 350, "max_rpm": 15000}
    }
    
    base_spec = specs[platform_type]
    
    # 考慮弱磁控制對最高轉速的提升[cite: 1]
    actual_max_rpm = base_spec["max_rpm"] * fw_gain
    
    # 理論極速計算 (km/h)
    top_speed = (actual_max_rpm / gear_ratio) * (2 * np.pi * tire_radius) * 60 / 1000
    
    # 輪端扭矩 (Nm)
    wheel_torque = base_spec["peak_t"] * gear_ratio
    
    # 爬坡需求扭矩 (Nm)
    # F = mg*sin(theta) + Cr*mg*cos(theta)
    angle = np.arctan(slope / 100)
    gravity_force = weight * 9.81 * np.sin(angle)
    climb_req_torque = (gravity_force * tire_radius) / gear_ratio
    
    return base_spec["peak_p"], wheel_torque, top_speed, climb_req_torque, base_spec["peak_t"], actual_max_rpm

# ==========================================
# 2. Streamlit UI 介面層
# ==========================================

st.set_page_config(page_title="TAD-AGE 電車電機開發決策系統", layout="wide")

# 標題區
st.header(f"🏢 OD 系列 電車電機開發決策系統平台")

# 側邊欄配置
with st.sidebar:
    st.subheader("🚀 TAD-AGE 配置中心")
    platform = st.selectbox("主要馬達平台 (Platform)", ["OD120", "OD140", "OD220"])
    
    st.markdown("---")
    st.subheader("🛠️ 控制器進階配置")
    sensor_type = st.selectbox("感測器類型", ["Hall", "Encoder", "Resolver"], 
                               index=2 if platform == "OD220" else 0)
    v_bus = st.number_input("母線電壓 (V)", value=400 if platform == "OD220" else 72)
    
    # 弱磁控制開關[cite: 1]
    enable_fw = st.toggle("開啟弱磁控制 (Flux Weakening)", value=True)
    fw_gain = st.slider("弱磁擴速增益 (Flux Gain)", 1.0, 1.5, 1.25) if enable_fw else 1.0
    
    st.markdown("---")
    st.subheader("🚗 車輛環境模擬")
    weight = st.slider("整車總重 (kg)", 500, 3000, 1300)
    gear_ratio = st.slider("齒輪比 (Gear Ratio)", 1.0, 15.0, 8.0)
    tire_radius = st.slider("輪胎半徑 (m)", 0.1, 0.5, 0.25)
    slope = st.slider("模擬爬坡坡度 (%)", 0, 30, 15)

# 執行計算
p_peak, t_wheel, v_max, t_climb_req, t_motor_peak, rpm_limit = simulate_motor_performance(
    v_bus, gear_ratio, tire_radius, weight, slope, platform, fw_gain
)

# 顯示關鍵指標 (KPI)
col1, col2, col3, col4 = st.columns(4)
col1.metric("峰值功率", f"{p_peak} kW")
col2.metric("輪端扭矩", f"{t_wheel:.1f} Nm")
col3.metric("理論極速", f"{v_max:.1f} km/h", f"{((fw_gain-1)*100):+.1f}% (弱磁)" if fw_gain > 1 else None)
col4.metric("爬坡需求扭矩", f"{t_climb_req:.1f} Nm", f"{(t_wheel - t_climb_req):.1f} 餘裕", delta_color="normal")

st.markdown("---")

# ==========================================
# 3. 整合規劃文件的檢核結果與供應商推薦[cite: 1]
# ==========================================

alerts, rec_vendor = check_controller_compatibility(platform, sensor_type, v_bus)

c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📈 系統效率區間與作業特性曲線")
    # 模擬特性曲線數據
    rpm_range = np.linspace(0, rpm_limit, 100)
    torque_curve = [t_motor_peak if r < (rpm_limit/fw_gain) else t_motor_peak * (rpm_limit/fw_gain) / r for r in rpm_range]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(rpm_range, torque_torque_curve := torque_curve, color='red', linewidth=3, label="Torque (Nm)")
    ax.axhline(y=t_climb_req/gear_ratio, color='orange', linestyle='--', label=f"Climb Req ({slope}%)")
    ax.set_xlabel("Motor Speed (RPM)")
    ax.set_ylabel("Torque (Nm)")
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with c2:
    st.subheader("🔍 技術對接與供應商")
    
    # 顯示匹配檢核警報[cite: 1]
    if alerts:
        for a in alerts:
            st.warning(a)
    else:
        st.success("✅ 控制器技術規格初步匹配成功[cite: 1]")
        
    st.info(rec_vendor)
    
    # 快速工具區[cite: 1]
    with st.expander("📝 獲取詢價郵件模板"):
        st.code(f"主旨：關於 {platform} 平台控制器開發詢價\n內容：需支援 FOC 弱磁控制、CAN2.0B、{sensor_type} 感測器...")

st.caption(f"最後更新：2026-05-05 | 框架版本：TAD-AGE v2.1 | 基於：{platform} 控制器技術對接規劃資料[cite: 1]")