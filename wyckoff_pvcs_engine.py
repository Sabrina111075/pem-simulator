import streamlit as st
import pandas as pd
import numpy as np

def render_wyckoff_tab(st, alpha=0.5, beta=0.65, delta_w_max=0.19, regime="Bull (多頭)"):
    regime = st.session_state.get('selected_regime', regime)
    alpha = st.session_state.get('alpha', alpha)
    
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

    st.markdown("##### 📈 K線價量結構與 PVCS 訊號疊加圖")
    chart_data = pd.DataFrame(
        np.random.randn(40, 2).cumsum(axis=0) + [100, 50],
        columns=['Wyckoff Price', 'PVCS Volume Flow']
    )
    st.line_chart(chart_data)

    st.markdown("---")

    st.markdown("##### 🎯 PVCS 三維診斷文字方塊")
    
    tb_col1, tb_col2, tb_col3, tb_col4 = st.columns(4)
    with tb_col1:
        st.info("**P - 價格結構得分**\n\n### **81.7**\n\n📌 狀態：強勢突破點")
    with tb_col2:
        st.info("**V - 成交量動能得分**\n\n### **72.8**\n\n📌 狀態：量增價漲結構")
    with tb_col3:
        st.info("**C - 籌碼集中度得分**\n\n### **68.3**\n\n📌 狀態：主力集中控盤")
    with tb_col4:
        st.info("**S - 市場情緒指數**\n\n### **70.7**\n\n📌 狀態：市場偏向樂觀")