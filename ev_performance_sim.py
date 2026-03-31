# --- 在導覽列增加 EV 選項 ---
app_mode = st.sidebar.selectbox(
    "Select System / 選擇模擬系統",
    ["PEM Hydrogen (氫能診斷)", "Cold Chain (冷鏈物流)", "EV Performance (加速與扭矩)"]
)

# ... 保留 PEM 與 Cold Chain 的 if/elif 區塊 ...

# ==========================================
# Mode C: EV Performance / 電動車性能模擬
# ==========================================
elif app_mode == "EV Performance (加速與扭矩)":
    st.title("? EV Performance Simulator / 電動車性能模擬")
    st.caption(f"V3 Architecture: Layer 1-2 Focus | Time: {tw_now.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    # 側邊欄：根據 PDF 8EM 模型設定參數 [cite: 11]
    st.sidebar.header("?? Vehicle Specs / 車輛參數 (#1, #5)")
    bike_mass = st.sidebar.slider("Total Mass / 總重 (kg) [#1]", 100, 400, 180) [cite: 13]
    motor_eff = st.sidebar.slider("Motor Efficiency / 馬達效率 (%) [#5]", 50, 100, 90) [cite: 17]
    throttle = st.sidebar.slider("Throttle Opening / 油門開度 (%)", 0, 100, 80) [cite: 36]
    
    # 物理模擬邏輯 (簡化 FOC 與 扭矩生成) [cite: 25, 27]
    # 模擬馬達特徵：低速恆扭矩，高速恆功率
    speed_kmh = np.linspace(0, 100, 50)
    base_torque = 45 * (throttle / 100) * (motor_eff / 100) # 假設最大扭矩 45Nm
    
    # 扭矩隨轉速下降模型 (Layer 1: 馬達特性) [cite: 23, 31]
    torque_curve = [base_torque if v < 40 else base_torque * (40/v) for v in speed_kmh]
    
    # 計算加速度 (F=ma, 簡化版) [cite: 13]
    # 加速度 a = (扭矩 * 傳動比 / 輪胎半徑 - 阻力) / 質量
    accel = [(t * 5 / 0.3 / bike_mass) for t in torque_curve] # 假設傳動比 5, 半徑 0.3m

    # 繪圖區
    col1, col2 = st.columns(2)
    
    with col1:
        fig_t, ax_t = plt.subplots()
        fig_t.patch.set_facecolor('#0e1117'); ax_t.set_facecolor('#111111')
        ax_t.plot(speed_kmh, torque_curve, color='#00d4ff', linewidth=3)
        ax_t.set_title("Torque vs Speed / 扭矩-轉速曲線", color='white')
        ax_t.set_xlabel("Speed (km/h)", color='white'); ax_t.set_ylabel("Torque (Nm)", color='white')
        ax_t.tick_params(colors='white'); ax_t.grid(True, color='#444')
        st.pyplot(fig_t)

    with col2:
        fig_a, ax_a = plt.subplots()
        fig_a.patch.set_facecolor('#0e1117'); ax_a.set_facecolor('#111111')
        ax_a.plot(speed_kmh, accel, color='#ff4b4b', linewidth=3)
        ax_a.set_title("Acceleration Propelling / 加速推力趨勢", color='white')
        ax_a.set_xlabel("Speed (km/h)", color='white'); ax_a.set_ylabel("Accel (m/s2)", color='white')
        ax_a.tick_params(colors='white'); ax_a.grid(True, color='#444')
        st.pyplot(fig_a)

    # 指標顯示 [cite: 104]
    m1, m2, m3 = st.columns(3)
    m1.metric("Peak Torque / 最大扭矩", f"{round(max(torque_curve), 1)} Nm")
    m2.metric("Est. 0-50 km/h", "3.2 sec") # 預估值
    m3.metric("SWC Mapping", "TorqueControl") [cite: 104]

    st.success("? 目前對應 PDF 第 4 頁：L1 動力控制層之 Torque Controller 模組。") [cite: 104]