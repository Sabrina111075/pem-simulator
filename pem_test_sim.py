import streamlit as st
from datetime import datetime
import pytz

# 設定語系
lang = st.sidebar.radio("Language / 語言", ["English", "繁體中文"])

# 獲取台北時間
taipei_tz = pytz.timezone('Asia/Taipei')
now = datetime.now(taipei_tz).strftime("%Y-%m-%d %H:%M:%S")

if lang == "English":
    st.title("PEM Hydrogen Production Simulation (2026-04-13)")
    st.write(f"**Current Status:** Running | **Time:** {now}")
else:
    st.title("PEM 產氫測試模擬系統")
    st.write(f"**目前狀態：** 運行中 | **台北時間：** {now}")
