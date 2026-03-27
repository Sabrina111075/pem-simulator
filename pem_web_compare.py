# -*- coding: utf-8 -*-
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 1. 頁面基礎配置
st.set_page_config(page_title="PEM Diagnostic Pro", layout="wide", page_icon="🔬")

# 2. 自定義 CSS：強化深色背景與雙語指標清晰度
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetric"] {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #444;
    }
    [data-testid="stMetricLabel"] p {
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricValue"] div {
        color: #00d4ff !important;
        font-size: 28px !important;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 修正時間為台北時區 (UTC+8)
tw_time = datetime.utcnow() + timedelta(hours=8)

# 移除「泰德時代」，僅保留核心標題與時區
st.title("🔬 PEM Hydrogen Diagnostic System / 氫能診斷系統")
st.caption(f"Status: Running (台北時間): {tw_time.strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# 3. 側邊欄控制台 (雙語並陳)
st.sidebar.header("🕹️ Control Panel / 參數設定")

with st.sidebar.expander("📊 Mode A: Baseline / 基準狀態", expanded=True):
    temp_a = st.slider("Temperature / 溫度 A (°C)", 20, 100, 60, key="ta")
    v1_a = st.slider("Ohmic Coeff / 歐姆係數 A", 5.0, 25.0, 13.5, key="va")
    hum_a = st.slider("Humidity / 溼度 A (%)", 0, 100, 80, key="ha")

with st.sidebar.expander("🧪 Mode B: Testing / 測試狀態", expanded=True):
    temp_b = st.slider("Temperature / 溫度 B (°C)", 20, 100, 80, key="tb")
    v1_b = st.slider("Ohmic Coeff / 歐姆係數 B", 5.0, 25.0, 18.0, key="vb")
    hum_b = st.slider("Humidity / 溼度 B (%)", 0, 100, 50, key="hb")

# 4. 核心計算
def get_data(t, v, h):
    c = np.linspace(0.1, 2.2, 12)
    v_out = 2.6 - (v/10 * c) - (t/500) - ((100-h)/200.0)
    score = max(0, min(100, round(100 - (v - 13.5) * 8 - (t - 60) * 1.5 - (80 - h) * 0.5)))
    return c, v_out, score

c_a, v_a, s_a = get_data(temp_a, v1_a, hum_a)
c_b, v_b, s_b = get_data(temp_b, v1_b, hum_b)

# 5. 繪圖區 (雙語座標軸)
def draw_plot(c, v, color, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#0e1117') 
    ax.set_facecolor('#111111')
    ax.plot(c, v, color=color, marker='o', markersize=6, linewidth=3)
    
    # 圖表標題與標籤 (採用雙語)
    ax.set_title(title, color='#FFFFFF', fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Current / 電流 (A)", color='#FFFFFF', fontsize=10, fontweight='bold')
    ax.set_ylabel("Voltage / 電壓 (V)", color='#FFFFFF', fontsize=10, fontweight='bold')
    
    ax.tick_params(colors='#F0F0F0', labelsize=9)
    ax.set_ylim(0, 3)
    ax.grid(True, color='#444444', linestyle=':', alpha=0.7)
    for spine in ax.spines.values():
        spine.set_color('#666666')
    return fig

# 6. UI 佈局
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📍 Baseline / 基準曲線")
    st.pyplot(draw_plot(c_a, v_a, '#00d4ff', "Baseline IV Curve"))

with col2:
    st.markdown("### 🚀 Testing / 測試曲線")
    st.pyplot(draw_plot(c_b, v_b, '#ff4b4b', "Testing IV Curve"))

# 數據指標區 (雙語並陳)
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Health Index A / 健康指標 A", f"{s_a}%")
with m2:
    st.metric("Health Index B / 健康指標 B", f"{s_b}%", delta=f"{s_b - s_a}%")
with m3:
    v_diff = round(np.mean(v_a - v_b), 3)
    st.metric("Avg. Volt Drop / 平均壓降", f"{v_diff} V")

# 7. 專家診斷 (雙語)
st.markdown("---")
st.subheader("🤖 Expert Diagnostics / 專家診斷建議")

if s_b < 50:
    st.error(f"🔴 CRITICAL / 嚴重警告: Health Score too low ({s_b}%).")
elif s_b < s_a - 15:
    st.warning(f"🟡 WARNING / 注意: Performance degradation detected.")
else:
    st.success("🟢 NORMAL / 狀態良好: System operating within limits.")

advice = []
if temp_b > 85: 
    advice.append(f"🌡️ **Overheat / 溫度過高**: {temp_b}°C may cause dehydration.")
if hum_b < 40: 
    advice.append(f"💧 **Low Humidity / 溼度不足**: {hum_b}% may increase resistance.")
if v1_b > v1_a + 3: 
    advice.append("⚡ **Resistance / 電阻異常**: Check stack compression force.")

if advice:
    for item in advice: st.info(item)
else:
    st.info("✨ All parameters within safe window / 目前參數均正常。")

# 8. 數據導出 (雙語表頭)
st.sidebar.markdown("---")
df_exp = pd.DataFrame({
    'Current(A)/電流': c_a, 
    'Volt_A(V)/基準': v_a, 
    'Volt_B(V)/測試': v_b, 
    'Diff(V)/壓降': v_a - v_b
})
csv = df_exp.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button(
    "📥 Download CSV Report / 導出報表", 
    csv, 
    f"PEM_Report_{tw_time.strftime('%m%d_%H%M')}.csv", 
    "text/csv"
)