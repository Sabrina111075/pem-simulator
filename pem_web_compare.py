# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import io
import os

# --- 字體設定 ---
def get_font():
    path = "C:\\Windows\\Fonts\\msjh.ttc"
    return font_manager.FontProperties(fname=path) if os.path.exists(path) else font_manager.FontProperties()

CH_FONT = get_font()

st.set_page_config(page_title="TAD-AGE Dual-Compare", layout="wide")

st.title("📊 TAD-AGE: PEM 氫能對比診斷模擬器")
st.markdown("您可以鎖定一組基準數據，然後調整參數觀察 IV 曲線的偏移。")

# --- 側邊欄控制 ---
st.sidebar.header("PARAMETER SETTINGS / 參數設定")
temp = st.sidebar.slider("溫度 Temperature (C)", 20, 100, 60)
v1 = st.sidebar.slider("歐姆係數 V1 Coeff", 5.0, 25.0, 13.5)
hum = st.sidebar.slider("溼度 Humidity (%)", 0, 100, 80)

# --- 比較功能邏輯 ---
if 'baseline' not in st.session_state:
    st.session_state.baseline = None

if st.sidebar.button("📍 鎖定為基準數據 (Lock Baseline)"):
    st.session_state.baseline = {'temp': temp, 'v1': v1, 'hum': hum}
    st.sidebar.success("基準已更新！")

if st.sidebar.button("🔄 重設基準 (Reset)"):
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
    # 計算電壓降偏移 (以中間電流點為例)
    offset = round(np.mean(v_base - v_now), 3)
    st.sidebar.metric("Voltage Offset / 電壓偏移", f"{offset} V", delta=-offset)

# 圖表美化
ax.set_title(f"Comparison Result / 對比結果 (Health: {s_now}%)", color='white', fontproperties=CH_FONT, fontsize=16)
ax.set_xlabel("Current / 電流 (A)", color='white', fontproperties=CH_FONT)
ax.set_ylabel("Voltage / 電壓 (V)", color='white', fontproperties=CH_FONT)
ax.legend(prop=CH_FONT)
ax.set_ylim(0, 3)
ax.grid(True, color='#333333', linestyle=':')
ax.tick_params(colors='white')

# 顯示介面
col1, col2 = st.columns([3, 1])
col1.pyplot(fig)

with col2:
    st.subheader("📊 診斷摘要")
    st.metric("當前健康度", f"{s_now}%")
    if st.session_state.baseline:
        st.write("**基準參數：**")
        st.caption(f"Temp: {st.session_state.baseline['temp']}°C / Hum: {st.session_state.baseline['hum']}%")
    
    st.info("💡 藍色虛線代表您的基準線，橘色實線隨調整即時變動。")