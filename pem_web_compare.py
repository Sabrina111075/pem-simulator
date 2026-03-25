# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

# 1. 頁面基礎配置
st.set_page_config(page_title="TAD-AGE Pro Expert", layout="wide", page_icon="🔬")

# 2. 自定義 CSS：強化深色背景與卡片對比
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; color: #00d4ff; }
    .stMetric { background-color: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔬 TAD-AGE | PEM Hydrogen Diagnostic System")
st.caption(f"系統狀態：運行中 | 目前時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.markdown("---")

# 3. 側邊欄控制台
st.sidebar.header("🕹️ 控制台 / Control Panel")

with st.sidebar.expander("📊 Mode A: Baseline (基準)", expanded=True):
    temp_a = st.slider("溫度 A (C)", 20, 100, 60, key="ta")
    v1_a = st.slider("歐姆係數 A", 5.0, 25.0, 13.5, key="va")
    hum_a = st.slider("溼度 A (%)", 0, 100, 80, key="ha")

with st.sidebar.expander("🧪 Mode B: Testing (測試)", expanded=True):
    temp_b = st.slider("溫度 B (C)", 20, 100, 80, key="tb")
    v1_b = st.slider("歐姆係數 B", 5.0, 25.0, 18.0, key="vb")
    hum_b = st.slider("溼度 B (%)", 0, 100, 50, key="hb")

# 4. 核心計算引擎 (模擬 PEM 物理特性)
def get_data(t, v, h):
    c = np.linspace(0.1, 2.2, 12)
    # 簡單物理模擬公式
    v_out = 2.6 - (v/10 * c) - (t/500) - ((100-h)/200.0)
    # 健康分數邏輯
    score = max(0, min(100, round(100 - (v - 13.5) * 8 - (t - 60) * 1.5 - (80 - h) * 0.5)))
    return c, v_out, score

c_a, v_a, s_a = get_data(temp_a, v1_a, hum_a)
c_b, v_b, s_b = get_data(temp_b, v1_b, hum_b)

# 5. 繪圖區 (視覺強化：高對比度文字)
def draw_plot(c, v, score, color, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#0e1117') 
    ax.set_facecolor('#111111')
    
    # 強化曲線
    ax.plot(c, v, color=color, marker='o', markersize=6, linewidth=3)
    
    # 標題與標籤強化 (純白加粗)
    ax.set_title(title, color='#FFFFFF', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Current (A)", color='#FFFFFF', fontsize=11, fontweight='bold')
    ax.set_ylabel("Voltage (V)", color='#FFFFFF', fontsize=11, fontweight='bold')
    
    # 座標軸數字強化 (亮灰加粗)
    ax.tick_params(colors='#F0F0F0', labelsize=10)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')

    ax.set_ylim(0, 3)
    ax.grid(True, color='#444444', linestyle=':', alpha=0.7)
    
    # 邊框強化
    for spine in ax.spines.values():
        spine.set_color('#666666')
        spine.set_linewidth(1.5)
        
    return fig

# 6. UI 佈局：並列圖表與數據指標
col1, col2 = st.columns(2)
col1.pyplot(draw_plot(c_a, v_a, s_a, '#00d4ff', "📍 Baseline Performance"))
col2.pyplot(draw_plot(c_b, v_b, s_b, '#ff4b4b', "🚀 Testing Performance"))

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Health Index A", f"{s_a}%")
with m2:
    st.metric("Health Index B", f"{s_b}%", delta=f"{s_b - s_a}%")
with m3:
    # 計算平均壓降落差
    v_diff = round(np.mean(v_a - v_b), 3)
    st.metric("Avg. Voltage Drop", f"{v_diff} V")

# 7. 🤖 TAD-AGE 自動診斷建議
st.markdown("---")
st.subheader("🤖 Expert Diagnostics / 專家診斷系統")

if s_b < 50:
    st.error(f"🔴 CRITICAL: 健康度極低 ({s_b}%)，檢測到電堆性能嚴重衰減。")
elif s_b < s_a - 15:
    st.warning(f"🟡 WARNING: 性能顯著低於基準狀態 (落差: {s_a - s_b}%)。")
else:
    st.success("🟢 NORMAL: 測試狀態穩定，符合運行指標。")

advice = []
if temp_b > 85: 
    advice.append("🌡️ **高溫預警**：操作溫度過高可能導致膜乾涸 (Membrane Drying)，請檢查冷卻系統。")
if hum_b < 40: 
    advice.append("💧 **低濕度警報**：濕度不足會增加歐姆極化損耗，建議調整進氣加濕。")
if v1_b > v1_a + 3: 
    advice.append("⚡ **電阻異常**：歐姆係數過高，請檢查硬體物理連接或緊固力。")

if advice:
    for item in advice:
        st.info(item)
else:
    st.info("✨ 目前所有物理參數均處於理想運行區間。")

# 8. 📂 數據導出功能
st.sidebar.markdown("---")
df_exp = pd.DataFrame({
    'Current_A': c_a, 
    'Volt_A': v_a, 
    'Volt_B': v_b, 
    'Diff': v_a - v_b
})
csv = df_exp.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button(
    label="📥 下載診斷報表 (.csv)", 
    data=csv, 
    file_name=f"PEM_Report_{datetime.now().strftime('%m%d_%H%M')}.csv", 
    mime="text/csv"
)