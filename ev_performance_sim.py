# ==========================================
# Mode C: PEM Hydrogen (恢復雙曲線重疊對比)
# ==========================================
elif app_mode == "PEM Hydrogen (氫能診斷)":
    st.title("🔋 PEM Hydrogen Diagnostic System")
    st.caption(f"V3 Architecture | Performance Comparison | {tw_now.strftime('%H:%M:%S')}")
    
    # 側邊欄參數設定
    with st.sidebar:
        st.markdown("---")
        with st.expander("📊 Mode A: Baseline / 基準狀態", expanded=True):
            ohmic_a = st.slider("Ohmic Coeff A", 10.0, 30.0, 13.5, key="oa")
            act_a = st.slider("Activation A", 0.1, 0.5, 0.25, key="aa")

        with st.expander("🧪 Mode B: Testing / 測試狀態", expanded=True):
            ohmic_b = st.slider("Ohmic Coeff B", 10.0, 30.0, 22.0, key="ob")
            act_b = st.slider("Activation B", 0.1, 0.5, 0.35, key="ab")

    # 計算物理模型
    current_density = np.linspace(0.01, 2.0, 50)
    # 這裡使用標準 PEM 物理公式：V = E - V_ohmic - V_activation
    v_a = 1.2 - (ohmic_a/1000 * current_density) - act_a * np.log1p(current_density * 10)
    v_b = 1.2 - (ohmic_b/1000 * current_density) - act_b * np.log1p(current_density * 10)

    # 繪圖區：恢復為單一圖表雙曲線
    fig_pem, ax_pem = plt.subplots(figsize=(10, 5), dpi=120)
    fig_pem.patch.set_facecolor('#0e1117')
    ax_pem.set_facecolor('#111111')

    # 畫出基準線 (藍色)
    ax_pem.plot(current_density, v_a, color='#00d4ff', linewidth=3, label='Baseline Status (基準)', antialiased=True)
    # 畫出測試線 (紅色)
    ax_pem.plot(current_density, v_b, color='#ff4b4b', linewidth=3, linestyle='--', label='Testing Status (測試)', antialiased=True)

    # 優化字體與標籤 (恢復 image_135ddb.png 風格)
    ax_pem.set_title("IV Characteristic Curve Comparison", fontdict=title_style, pad=20)
    ax_pem.set_xlabel("Current Density (A/cm²)", fontdict=font_style, labelpad=10)
    ax_pem.set_ylabel("Cell Voltage (V)", fontdict=font_style, labelpad=10)
    
    ax_pem.tick_params(colors='white', labelsize=9)
    ax_pem.grid(True, color='#333', linestyle=':', alpha=0.6)
    ax_pem.legend(facecolor='#1a1a1a', edgecolor='#444', labelcolor='white')
    
    # 設定 Y 軸範圍確保呈現效果
    ax_pem.set_ylim(0, 1.3)
    
    st.pyplot(fig_pem)

    # 顯示分析指標
    idx_a = (v_a[0] - v_a[-1]) / v_a[0] * 100
    idx_b = (v_b[0] - v_b[-1]) / v_b[0] * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Health Index (A)", f"{round(100-idx_a, 1)}%", delta=None)
    col2.metric("Health Index (B)", f"{round(100-idx_b, 1)}%", delta=f"-{round(idx_b-idx_a, 1)}%", delta_color="inverse")
    col3.metric("SWC Status", "BMS_Health")