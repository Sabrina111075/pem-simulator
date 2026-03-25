# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="TAD-AGE Diagnostic Expert", layout="wide")

st.title("🔬 TAD-AGE: PEM Hydrogen Stack Expert System")
st.markdown("---")

# --- 側邊欄與參數計算 (保持原樣) ---
st.sidebar.header("🕹️ 模擬參數配置")
with st.sidebar.expander("📊 模式 A：基準狀態", expanded=True):
    temp_a = st.slider("溫度 A (C)", 20, 100, 60, key="ta")
    v1_a = st.slider("歐姆係數 A", 5.0, 25.0, 13.5, key="va")
    hum_a = st.slider("溼度 A (%)", 0, 100, 80, key="ha")

with st.sidebar.expander("🧪 模式 B：測試狀態", expanded=True):
    temp_b = st.slider("溫度 B (C)", 20, 100, 80, key="tb")
    v1_b = st.slider("歐姆係數 B", 5.0, 25.0, 18.0, key="vb")
    hum_b = st.slider("溼度 B (%)", 0, 100, 50, key="hb")

def get_data(t, v, h):
    c = np.linspace(0.1, 2.2, 12)
    v_out = 2.6 - (v/10 * c) - (t/500) - ((100-h)/200.0)
    score = max(0, min(100, round(100 - (v - 13.5) * 8 - (t - 60) * 1.5 - (80 - h) * 0.5)))
    return c, v_out, score

c_a, v_a, s_a = get_data(temp_a, v1_a, hum_a)
c_b, v_b, s_b = get_data(temp_b, v1_b, hum_b)

# --- UI 佈局：並列圖表 ---
col1, col2 = st.columns(2)
def draw_plot(c, v, score, color, title):
    fig, ax = plt.subplots(figsize=(5, 3.5))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#1a1a1a')
    ax.plot(c, v, color=color, marker='o', linewidth=2)
    ax.set_title(f"{title}", color='white', fontsize=10)
    ax.set_ylim(0, 3)
    ax.grid(True, color='#333333', linestyle='--')
    ax.tick_params(colors='gray', labelsize=8)
    return fig

col1.pyplot(draw_plot(c_a, v_a, s_a, '#3498db', "Baseline IV Curve"))
col2.pyplot(draw_plot(c_b, v_b, s_b, '#e74c3c', "Testing IV Curve"))

# --- ✨ 新功能：動態診斷專家建議 ---
st.markdown("---")
st.subheader("🤖 TAD-AGE 自動診斷建議")

# 1. 動態警示燈邏輯
if s_b < 50:
    st.error(f"⚠️ 警告：測試組健康度極低 ({s_b}%)，電堆可能存在受損風險！")
elif s_b < s_a - 10:
    st.warning(f"🔔 提醒：性能較基準明顯衰退 (落差: {s_a - s_b}%)。")
else:
    st.success("✅ 狀態穩定：性能與基準相符或優於基準。")

# 2. 自動診斷文本生成
advice = []
if temp_b > 80: advice.append("- ⚠️ **溫度過高**：可能導致質子交換膜脫水，請檢查冷卻系統。")
if hum_b < 40: advice.append("- ⚠️ **濕度過低**：膜電阻(R-ohm)增加，IV 曲線斜率變陡。")
if v1_b > v1_a + 2: advice.append("- ⚠️ **歐姆損耗異常**：請檢查物理連接或膜電極(MEA)接觸。")

col_metric1, col_metric2 = st.columns(2)
with col_metric1:
    st.metric("Health Index A", f"{s_a}%")
with col_metric2:
    st.metric("Health Index B", f"{s_b}%", delta=f"{s_b - s_a}%")

if advice:
    st.info("**💡 診斷建議清單：**\n" + "\n".join(advice))
else:
    st.info("💡 目前參數配置在理想範圍內。")

# --- 數據導出 (保持原樣) ---
df_compare = pd.DataFrame({'Current (A)': c_a, 'Voltage_A (V)': v_a, 'Voltage_B (V)': v_b})
csv = df_compare.to_csv(index=False).encode('utf-8-sig')
st.download_button(label="📥 下載數據紀錄", data=csv, file_name="PEM_Expert_Data.csv", mime="text/csv")