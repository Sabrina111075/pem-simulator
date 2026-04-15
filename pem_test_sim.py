import streamlit as st
import pandas as pd
import numpy as np

st.title("PEM 產氫測試模擬系統 (2026-04-13)")

# Sidebar 參數設定
with st.sidebar:
    mode = st.radio("選擇模式", ["單管制氫", "雙管制氫"])
    temp = st.slider("設定基準溫度 (°C)", 30.0, 50.0, 33.7)

# 模擬計算邏輯
if mode == "單管制氫":
    avg_sec_kg = 108.4 # 基於測試數據階段 7
else:
    avg_sec_kg = 95.0 # 基於雙管初期數據

# 生成模擬數據曲線
time_steps = np.arange(0, 1000, 10)
production = time_steps / avg_sec_kg

# 顯示圖表
chart_data = pd.DataFrame({
    '時間(秒)': time_steps,
    '預期產量(kg)': production
})
st.line_chart(chart_data.set_index('時間(秒)'))

# 診斷提醒
if mode == "雙管制氫" and max(production) > 9:
    st.warning("檢測到末期效率大幅下降（模擬實測數據之 174s/kg 異常現象）")