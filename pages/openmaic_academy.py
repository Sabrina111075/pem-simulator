import streamlit as st
import streamlit.components.v1 as components

st.title("🎓 OpenMAIC 聲學 AI 學院 × 虛擬聲學診斷實驗室")
st.caption("結合 OpenMAIC 多智能體 AI 課堂與 Streamlit 邊緣聲學診斷模擬")

st.info("💡 本頁面將 OpenMAIC AI 課堂與現有馬達聲學測試平台進行整合。")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🤖 OpenMAIC AI 課堂 & 導師引導")
    components.iframe("https://openmaic.chat/", height=600, scrolling=True)

with col2:
    st.subheader("⚙️ 馬達與工業設備聲學診斷測試平台")
    components.iframe("https://motor-acoustic-test.streamlit.app", height=600, scrolling=True)

st.divider()
st.subheader("📥 學習與實驗成果回寫 (Governed Writeback)")
uploaded_file = st.file_uploader("上傳聲學巡檢報告 (JSON)：", type=['json'])

if uploaded_file is not None:
    st.success("✅ 巡檢報告已成功接收！正在將診斷數據回寫至 Knowledge Container...")
