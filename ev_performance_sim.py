# ==========================================
# Mode C: PEM Hydrogen (恢復雙曲線重疊與完整參數)
# ==========================================
elif app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔋 PEM Hydrogen Diagnostic System")
    st.caption(f"V3 Architecture | Performance Comparison | {tw_now.strftime('%H:%M:%S')}")
    
    # 恢復完整參數設定 (基準與測試)
    with st.sidebar:
        st.markdown("---")
        with st.expander("📊 Mode A: Baseline / 基準狀態", expanded=True):
            temp_a = st.slider("Temperature A (°C)", 40, 90, 60, key="ta")
            ohmic_a = st.slider("Ohmic Coeff A", 10.0, 30.0, 13.5, key="oa")
            hum_a = st.slider("Humidity A (%)", 20, 100, 80, key="ha")

        with st.expander("🧪 Mode B: Testing / 測試狀態", expanded=True):
            temp_b = st.slider("Temperature B (°C)", 40, 90, 75, key="tb")
            ohmic_b = st.slider("Ohmic Coeff B", 10.0, 30.0, 22.0, key="ob")
            hum_b = st.slider("Humidity B (%)", 20, 100, 60, key="hb")

    # 物理模型計算
    current_density = np.linspace(0.01, 2.0, 50)
    # 計算基準線 V_a
    v_a = 1.2 - (ohmic_a/1000 * current_density) - (0.3 - temp_a/500) * np.log1p(current_density * 10)
    # 計算測試線 V_b
    v_b = 1.2 - (ohmic_b/1000 * current_density) - (0.3 - temp_b/500) * np.log1p(current_density * 10)

    # 繪圖區：將兩條線畫在一起
    fig_pem, ax_pem = plt.subplots(figsize=(10, 5), dpi=120)
    fig_pem.patch.set_facecolor('#0e1117')
    ax_pem.set_facecolor('#111111')

    # 畫出基準線 (藍色實線)
    ax_pem.plot(current_density, v_a, color='#00d4ff', linewidth=3, label='Baseline Status (基準)', antialiased=True)
    # 畫出測試線 (紅色虛線)
    ax_pem.plot(current_density, v_b, color='#ff4b4b', linewidth=3, linestyle='--', label='Testing Status (測試)', antialiased=True)

    # 圖表美化
    ax_pem.set_title("IV Characteristic Curve Comparison", fontdict=title_style, pad=20)
    ax_pem.set_xlabel("Current Density (A/cm²)", fontdict=font_style, labelpad=10)
    ax_pem.set_ylabel("Cell Voltage (V)", fontdict=font_style, labelpad=10)
    
    ax_pem.tick_params(colors='white', labelsize=9)
    ax_pem.grid(True, color='#333', linestyle=':', alpha=0.6)
    ax_pem.legend(facecolor='#1a1a1a', edgecolor='#444', labelcolor='white')
    ax_pem.set_ylim(0, 1.3)
    
    st.pyplot(fig_pem)

    # 診斷結果顯示
    loss = (v_a.mean() - v_b.mean()) / v_a.mean() * 100
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Voltage (A)", f"{round(v_a.mean(), 2)} V")
    c2.metric("Avg Voltage (B)", f"{round(v_b.mean(), 2)} V", delta=f"-{round(loss, 1)}%")
    c3.metric("Diagnostic Result", "Normal" if loss < 10 else "Degraded", delta_color="inverse")