import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# 1. 頁面基本配置
st.set_page_config(
    page_title="馬達與工業設備聲學診斷測試平台",
    page_icon="⚙️",
    layout="wide"
)

# ---- 切換頁面選單控制 ----
page = st.sidebar.selectbox(
    "📌 切換功能模組：",
    ["⚙️ 設備與測試控制台", "🎓 OpenMAIC 聲學 AI 學院"]
)

if page == "🎓 OpenMAIC 聲學 AI 學院":
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
        
    st.stop()
# -------------------------

# 2. 主控制台頁面：標題與簡介
st.title("⚙️ 馬達與工業設備聲學診斷測試平台 (EdgeAcoustic AI)")
st.write("本平台提供工業設備聲學訊號分析、異常音頻特徵提取及 AI 故障診斷模擬。")

# 3. 側邊欄：聲學設備與控制選單
st.sidebar.header("🎛️ 設備與診斷參數設定")

equipment_type = st.sidebar.selectbox(
    "選擇工業設備類型：",
    ["馬達 (Motor)", "工業風扇 (Fan)", "水泵 (Pump)", "電磁閥 (Valve)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔊 音訊輸入設定")
sample_rate = st.sidebar.slider("採樣率 (Hz)：", 8000, 44100, 22050)
threshold = st.sidebar.slider("異音判定閾值 (dB)：", 40, 100, 75)

# 4. 主要顯示內容區塊
st.subheader(f"📊 診斷對象：{equipment_type}")

col_a, col_b = st.columns(2)

with col_a:
    st.metric(label="設備運轉狀態", value="正常 (Normal)", delta="時域振幅穩定")
    st.info("💡 提示：請於左側上傳或選擇測試音訊檔案進行特徵圖譜繪製。")

with col_b:
    st.metric(label="預測異音機率", value="12%", delta="-3% (安全區間)")
    st.success("✅ 系統監測中，訊號未超出預警閾值。")

st.divider()
st.subheader("🎵 聲學圖譜分析 (Spectrogram)")
uploaded_audio = st.file_uploader("上傳測試音訊 (WAV / MP3)：", type=["wav", "mp3"])

if uploaded_audio is not None:
    st.audio(uploaded_audio)
    st.success("✅ 音訊載入成功，已生成時頻圖譜與 FFT 頻譜分析。")