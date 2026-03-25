# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import io
import os

# --- 雲端版字體相容性設定 ---
# 由於雲端 Linux 伺服器沒有微軟正黑體，我們使用預設字體並關閉負號報錯
plt.rcParams['axes.unicode_minus'] = False 

st.set_page_config(page_title="TAD-AGE Dual-Compare", layout="wide")

st.title("📊 TAD-AGE: PEM Hydrogen Stack Diagnostic Simulator")
st.markdown("您可以鎖定一組基準數據，然後調整參數觀察 IV 曲線的偏移。")

# --- 側邊欄控制 ---
st.sidebar.header("PARAMETER SETTINGS / 參數設定")
temp = st.sidebar.slider("Temperature / 溫度 (C)", 20, 100, 60)
v1 = st.sidebar.slider("V1 Coeff / 歐姆係數", 5.0, 25.0, 13.5)
hum = st.sidebar.slider("Humidity / 溼度 (%)", 0, 100, 80)

# --- 比較功能邏輯 ---
if 'baseline' not in st.session_state:
    st.session_state.baseline = None

if st.sidebar.button("📍 Lock Baseline / 鎖定基準"):
    st.session_state.baseline = {'temp': temp, 'v1': v1, 'hum': hum}
    st.sidebar.success("Baseline Updated! / 基準已更新")

if st.sidebar.button("🔄 Reset / 重設"):
    st.session_state.baseline = None

# --- 計算函數 ---
def calculate_iv(t, v, h):
    currents = np.linspace(0.1, 2.2, 12)
    loss = (100 - h) / 200.0
    v_out = 2.6 - (v/10 * currents) - (t/500) - loss
    score = max(0, min(100, round(100 - (v - 13.5) * 8 - (t - 60) * 1.5 - (80 - h) * 0.5)))
    return currents, v_out, score

# 計算當前數據
c_now, v_now, s_now = calculate_iv(temp, v1, hum)

# --- 圖表繪製 ---
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#0e1117')
ax.set_facecolor('#1a1a1a')

# 繪製當前曲線 (實線)
ax.plot(c_now, v_now, color='#f39c12', marker='o', linewidth=3, label='Current / 當前')

# 如果有基準，繪製基準曲線 (虛線)
if st.session_state.baseline:
    b = st.session_state.baseline
    c_base, v_base, s_base = calculate_iv(b['temp'], b['v1'], b['hum'])
    ax.plot(c_base, v_base, color='#3498db', linestyle='--', marker='x', alpha=0.6, label='Baseline / 基準')
    offset = round(np.mean(v_base - v_now), 3)
    st.sidebar.metric("Voltage Offset / 電壓偏移", f"{offset} V", delta=-offset)

# 圖表標籤 (改為英文以確保雲端顯示正常)
ax.set_title(f"Comparison Result (Health: {s_now}%)", color='white', fontsize=16)
ax.set_xlabel("Current (A)", color='white')
ax.set_ylabel("Voltage (V)", color='white')
ax.legend()
ax.set_ylim(0, 3)
ax.grid(True, color='#333333', linestyle=':')
ax.tick_params(colors='white')

# 顯示介面
col1, col2 = st.columns([3, 1])
col1.pyplot(fig)

with col2:
    st.subheader("📊 Summary / 診斷摘要")
    st.metric("Health Index", f"{s_now}%")
    if st.session_state.baseline:
        st.write("**Baseline Params:**")
        st.caption(f"T: {st.session_state.baseline['temp']}C / H: {st.session_state.baseline['hum']}%")
    
    st.info("💡 Orange: Current / Blue: Baseline")