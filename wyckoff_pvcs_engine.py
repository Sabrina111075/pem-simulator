import streamlit as st
import pandas as pd
import numpy as np

def render_wyckoff_tab(st, alpha=0.5, beta=0.65, delta_w_max=0.19, regime="Bull (多頭)"):
    # 讀取 Session State 確保連動
    regime = st.session_state.get('selected_regime', regime)
    alpha = st.session_state.get('alpha', alpha)
    
    # 1. 四大卡片 Metrics (直列卡片樣式)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Wyckoff 階段辨識", "Phase D / E", "↑ SOS (Sign of Strength) / Jac...")
    with col2:
        st.metric("PVCS 綜合評估分", f"{round(73.8 - alpha*5, 1)} / 100", "↑ +3.4 pts")
    with col3:
        st.metric("籌碼集中度 (Chip Score)", "68.3 / 100", "↑ 三大法人同步買超")
    with col4:
        st.metric("建議策略動作", "積極加碼 / 持股續抱", "↑ 信心度 88%")

    st.markdown("---")

    # 2. K線價量結構與 PVCS 訊號疊加圖 (全寬上置)
    st.markdown("##### 📈 K線價量結構與 PVCS 訊號疊加圖")
    chart_data = pd.DataFrame(
        np.random.randn(40, 2).cumsum(axis=0) + [100, 50],
        columns=['Wyckoff Price', 'PVCS Volume Flow']
    )
    st.line_chart(chart_data)

    st.markdown("---")

    # 3. PVCS 三維診斷雷達 (移至最下方全寬呈現)
    st.markdown("##### 🎯 PVCS 三維診斷雷達")
    p_score = 81.7
    v_score = 72.8
    c_score = 68.3
    s_score = 70.7

    r_col1, r_col2 = st.columns([1, 3])
    with r_col1:
        st.caption(f"P - 價格結構得分: **{p_score}**")
        st.progress(p_score / 100)
        st.caption(f"V - 成交量動能得分: **{v_score}**")
        st.progress(v_score / 100)
    with r_col2:
        st.caption(f"C - 籌碼集中度得分: **{c_score}**")
        st.progress(c_score / 100)
        st.caption(f"S - 市場情緒指數: **{s_score}**")
        st.progress(s_score / 100)