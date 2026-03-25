# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd  # 新增：用於數據處理
from datetime import datetime

# 頁面配置
st.set_page_config(page_title="TAD-AGE Pro + Export", layout="wide")

st.title("🔬 TAD-AGE: PEM Hydrogen Stack Professional Dashboard")
st.markdown("---")

# --- 側邊欄：雙組參數輸入 ---
st.sidebar.header("🕹️ 模擬參數配置")

with st.sidebar.expander("📊 模式 A：基準狀態 (Baseline)", expanded=True):
    temp_a = st.slider("溫度 A (C)", 20, 100, 60, key="ta")
    v1_a = st.slider("歐姆係數 A", 5.0, 25.0, 13.5, key="va")
    hum_a = st.slider("溼度 A (%)", 0, 100, 80, key="ha")

with st.sidebar.expander("🧪 模式 B：測試狀態 (Testing)", expanded=True):
    temp_b = st.slider("溫度 B (C)", 20, 100, 80, key="tb")
    v1_b = st.slider("歐姆係數 B", 5.0, 25.0, 18.0, key="vb")
    hum_b = st.slider("溼度 B (%)", 0, 100, 50, key="hb")

# --- 計算引擎 ---
def get_data(t, v, h):
    c = np.linspace(0.1, 2.2, 12)
    v_out = 2.6 - (v/10 * c) - (t/500) - ((100-h)/200.0)
    score = max(0, min(100, round(100 - (v - 13.5) * 8 - (t - 60) * 1.5 - (80 - h) * 0.5)))
    return c, v_out, score

c_a, v_a, s_a = get_data(temp_a, v1_a, hum_a)
c_b, v_b, s_b = get_data(temp_b, v1_b, hum_b)

# --- 繪圖函數 ---
def draw_plot(c, v, score, color, title):
    fig, ax = plt.subplots(figsize=(5, 3.5))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#1a1a1a')
    ax.plot(c, v, color=color, marker='o', linewidth=2)
    ax.set_title(f"{title} (Health: {score}%)", color='white', fontsize=10)
    ax.set_ylim(0, 3)
    ax.grid(True, color='#333333', linestyle='--')
    ax.tick_params(colors='gray', labelsize=8)
    return fig

# --- UI 佈局：並列圖表 ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("📍 Mode A Performance")
    st.pyplot(draw_plot(c_a, v_a, s_a, '#3498db', "Baseline Status"))
    st.metric("Health Index A", f"{s_a}%")

with col2:
    st.subheader("🚀 Mode B Performance")
    st.pyplot(draw_plot(c_b, v_b, s_b, '#e74c3c', "Testing Status"))
    st.metric("Health Index B", f"{s_b}%", delta=f"{s_b - s_a}%")

# --- ✨ 新功能：數據導出區 ---
st.markdown("---")
st.subheader("📂 數據導出 (Data Export)")

# 建立 DataFrame
df_compare = pd.DataFrame({
    'Current (A)': c_a,
    'Voltage_A (V)': v_a,
    'Voltage_B (V)': v_b,
    'Difference (V)': v_a - v_b
})

# 下載按鈕邏輯
csv = df_compare.to_csv(index=False).encode('utf-8-sig') # 加上 sig 確保 Excel 開啟中文不亂碼
timestamp = datetime.now().strftime("%Y%m%d_%H%M")

st.download_button(
    label="📥 下載對比數據 (CSV Format)",
    data=csv,
    file_name=f"PEM_Diagnostic_{timestamp}.csv",
    mime="text/csv",
)

st.table(df_compare.head(5)) # 預覽前五筆數據