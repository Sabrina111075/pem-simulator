# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

# 頁面配置
st.set_page_config(page_title="TAD-AGE Pro Expert", layout="wide", page_icon="🔬")

# 自定義 CSS 美化
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🔬 TAD-AGE | PEM Hydrogen Diagnostic System")
st.caption(f"系統狀態：運行中 | 登錄時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.markdown("---")

# --- 側邊欄 ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1835/1835262.png", width=80) # 加入一個小圖示
st.sidebar.header("🕹️ 控制台 / Control Panel")

with st.sidebar.expander("📊 Mode A: Baseline (基準)", expanded=True):
    temp_a = st.slider("溫度 A (C)", 20, 100, 60, key="ta")
    v1_a = st.slider("歐姆係數 A", 5.0, 25.0, 13.5, key="va")
    hum_a = st.slider("溼度 A (%)", 0, 100, 80, key="ha")

with st.sidebar.expander("🧪 Mode B: Testing (測試)", expanded=True):
    temp_b = st.slider("溫度 B (C)", 20, 100, 80, key="tb")
    v1_b = st.slider("歐姆係數 B", 5.0, 25.0, 18.0, key="vb")
    hum_b = st.slider("溼度 B (%)", 0, 100, 50, key="hb")

# --- 核心計算 ---
def get_data(t, v, h):
    c = np.linspace(0.1, 2.2, 12)
    v_out = 2.6 - (v/10 * c) - (t/500) - ((100-h)/200.0)
    score = max(0, min(100, round(100 - (v - 13.5) * 8 - (t - 60) * 1.5 - (80 - h) * 0.5)))
    return c, v_out, score

c_a, v_a, s_a = get_data(temp_a, v1_a, hum_a)
c_b, v_b, s_b = get_data(temp_b, v1_b, hum_b)

# --- 繪圖區 ---
def draw_plot(c, v, score, color, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#111111')
    ax.plot(c, v, color=color, marker='o', markersize=4, linewidth=2, label='Current Data')
    ax.set_title(title, color='white', fontsize=12, pad=15)
    ax.set_ylim(0, 3)
    ax.grid(True, color='#222222', linestyle='--')
    ax.tick_params(colors='#888888', labelsize=9)
    for spine in ax.spines.values(): spine.set_color('#333')
    return fig

col1, col2 = st.columns(2)
col1.pyplot(draw_plot(c_a, v_a, s_a, '#00d4ff', "📍 Baseline Stack Performance"))
col2.pyplot(draw_plot(c_b, v_b, s_b, '#ff4b4b', "🚀 Current Testing Performance"))

# --- 數據摘要 ---
m1, m2, m3 = st.columns(3)
m1.metric("Health Score A", f"{s_a}%")
m2.metric("Health Score B", f"{s_b}%", delta=f"{s_b - s_a}%")
m3.metric("Avg. Voltage Drop", f"{round(np.mean(v_a - v_b), 3)} V")

# --- 診斷專家區 ---
st.markdown("---")
st.subheader("🤖 TAD-AGE Expert Diagnostics")

if s_b < 50:
    st.error(f"🔴 CRITICAL: 健康度極低 ({s_b}%)，請立即停止測試並檢查硬體。")
elif s_b < s_a - 15:
    st.warning(f"🟡 WARNING: 性能顯著衰退，請參考下方建議進行調整。")
else:
    st.success("🟢 NORMAL: 運作狀態良好。")

# 自動建議邏輯
advice = []
if temp_b > 85: advice.append("🌡️ **熱管理預警**：操作溫度過高，請檢查冷卻循環。")
if hum_b < 40: advice.append("💧 **溼度不足**：膜電阻增加導致斜率變大，建議增加背壓或加溼。")
if v1_b > v1_a + 3: advice.append("⚡ **接觸電阻警告**：歐姆極化損耗異常，請檢查電堆壓緊力。")

if advice:
    for item in advice: st.info(item)
else:
    st.info("✨ 目前參數均在安全運行窗口內。")

# --- 導出 ---
df_exp = pd.DataFrame({'Ampere': c_a, 'Volt_A': v_a, 'Volt_B': v_b})
csv = df_exp.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button("📥 導出診斷報表 (.csv)", csv, f"TAD_AGE_{datetime.now().strftime('%m%d')}.csv", "text/csv")