import streamlit as st
import pandas as pd
import numpy as np

def render_wyckoff_tab(st, alpha=0.5, beta=0.65, delta_w_max=0.19, regime="Bull (多頭)"):
    # 讀取 Session State 確保連動
    regime = st.session_state.get('selected_regime', regime)
    alpha = st.session_state.get('alpha', alpha)
    
    # 1. 四大卡片 Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Wyckoff 階段辨識", "Phase D / E", "↑ SOS / Jac...")
    with col2:
        st.metric("PVCS 綜合評估分", f"{round(73.8 - alpha*5, 1)} / 100", "↑ +3.4 pts")
    with col3:
        st.metric("籌碼集中度 (Chip Score)", "68.3 / 100", "↑ 三大法人同步買超")
    with col4:
        st.metric("建議策略動作", "積極加碼 / 持股續抱", "↑ 信心度 88%")

    st.markdown("---")

    # 2. K線價量結構與 PVCS 訊號疊加圖
    st.markdown("##### 📈 K線價量結構與 PVCS 訊號疊加圖")
    chart_data = pd.DataFrame(
        np.random.randn(40, 2).cumsum(axis=0) + [100, 50],
        columns=['Wyckoff Price', 'PVCS Volume Flow']
    )
    st.line_chart(chart_data)

    st.markdown("---")

    # 3. PVCS 三維診斷指標 (改為 4 欄文字指標卡片)
    st.markdown("##### 🎯 PVCS 三維診斷數據")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("P - 價格結構得分", "81.7", "強勢突破")
    with m_col2:
        st.metric("V - 成交量動能得分", "72.8", "量增價漲")
    with m_col3:
        st.metric("C - 籌碼集中度得分", "68.3", "主力控盤")
    with m_col4:
        st.metric("S - 市場情緒指數", "70.7", "偏向樂觀")