import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. 網頁全域配置
# ==========================================
st.set_page_config(
    page_title="NaBH4 數位雙生模擬系統 V2.0",
    page_icon="🧪",
    layout="wide"
)

# 自定義 CSS 優化介面
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 定義場景與初始數據
# ==========================================
SCENARIOS = {
    "1. 智能倉儲自動搬運車 (AGV)": {"temp": 45, "conc": 15, "flow": 25, "i0": 0.002, "desc": "中溫環境，要求長效穩定的產氫與電力輸出。"},
    "2. 長航時工業級無人機 (UAV)": {"temp": 35, "conc": 25, "flow": 40, "i0": 0.0008, "desc": "高濃度燃料以減輕重量，產氫需求隨高度動態調整。"},
    "3. 偏遠離島微電網後備電源": {"temp": 65, "conc": 12, "flow": 120, "i0": 0.005, "desc": "大型化系統，高流量連續工作，發熱量大。"},
    "4. 國防可攜式單兵作戰裝備": {"temp": 25, "conc": 20, "flow": 10, "i0": 0.0005, "desc": "低溫環境，啟動慢，需精確控制進料。"},
    "5. 海洋觀測浮標 (水下載具)": {"temp": 20, "conc": 18, "flow": 15, "i0": 0.0004, "desc": "低溫高壓，反應床溫度控制是關鍵。"},
    "6. 5G 通訊基地台備援系統": {"temp": 55, "conc": 15, "flow": 80, "i0": 0.003, "desc": "標準定功率輸出，自動補足氫氣壓。"},
    "7. 野外緊急醫療行動站": {"temp": 40, "conc": 10, "flow": 35, "i0": 0.0015, "desc": "模組化快速更換燃料，著重可靠度。"},
    "8. 綠能製氫加氫站負載調節": {"temp": 70, "conc": 30, "flow": 250, "i0": 0.008, "desc": "極限輸出，產氫量與發電量需精確聯動。"},
    "9. 極地科考站維生系統": {"temp": 30, "conc": 22, "flow": 20, "i0": 0.0006, "desc": "低外部溫度，依賴電池廢熱維持反應床運轉。"},
    "10. 航天輔助動力單元 (APU)": {"temp": 75, "conc": 28, "flow": 150, "i0": 0.010, "desc": "高性能、高壓力控制，系統參數皆在極限區。"}
}

# ==========================================
# 3. 側邊欄設計 (Sidebar)
# ==========================================
st.sidebar.markdown("## 🏢 前瞻綠能與動力系統實驗室")
st.sidebar.markdown("---")

# A. 場景選擇
st.sidebar.subheader("🌟 應用場景選擇")
selected_scen = st.sidebar.selectbox("切換場景預設值：", list(SCENARIOS.keys()))
scen_default = SCENARIOS[selected_scen]

# B. 工藝參數 (Process Control)
st.sidebar.subheader("🎮 工藝參數與控制")
with st.sidebar.expander("進料與熱管理系統", expanded=True):
    flow_rate = st.slider("進料流量 (mL/min)", 1, 300, scen_default['flow'])
    concentration = st.slider("NaBH4 溶液濃度 (wt%)", 5, 35, scen_default['conc'])
    reactor_temp = st.slider("反應床操作溫度 (°C)", 10, 90, scen_default['temp'])

# C. 工程參數 (Electrical Params)
st.sidebar.subheader("⚙️ 電池核心工程參數")
with st.sidebar.expander("電化學特性設定"):
    e_thermo = st.number_input("理論電勢 (V)", 1.20, 1.80, 1.64)
    i_0 = st.number_input("交換電流密度 i₀ (A/cm²)", 0.0001, 0.05, scen_default['i0'], format="%.4f")
    r_int = st.slider("內阻 R_int (Ω·cm²)", 0.01, 1.0, 0.15)
    alpha = st.slider("電荷傳遞係數 α", 0.1, 0.9, 0.5)

# ==========================================
# 4. 核心物理模型 (產氫量與電化學聯動)
# ==========================================
def calculate_system():
    # 1. 產氫速率計算 (簡化動力學模型)
    # 假設 NaBH4 + 2H2O -> NaBO2 + 4H2
    # 產氫率正比於 溫度(Arrhenius) * 濃度 * 流量
    k_temp = np.exp(-4000 / (8.314 * (reactor_temp + 273.15))) * 1.5e6
    h2_prod_rate = k_temp * (concentration / 100) * (flow_rate / 1000) * 4 # L/min
    
    # 2. 聯動：氫氣供應量決定了電池的「極限電流密度 i_limit」
    # 氫氣越多，擴散損失越小
    i_limit_dynamic = 0.5 + (h2_prod_rate * 0.8) # 簡單動態關聯
    
    # 3. 極化曲線計算
    i_range = np.linspace(0.001, min(i_limit_dynamic - 0.01, 2.5), 50)
    v_cell = []
    p_density = []
    
    T_k = reactor_temp + 273.15
    for i in i_range:
        # 活化損失 (Butler-Volmer 簡化)
        eta_act = (8.314 * T_k / (alpha * 8 * 96485)) * np.log(i / i_0)
        # 歐姆損失
        eta_ohmic = i * r_int
        # 濃差損失
        eta_conc = - (8.314 * T_k / (alpha * 8 * 96485)) * np.log(1 - i / i_limit_dynamic)
        
        v = e_thermo - eta_act - eta_ohmic - eta_conc
        v = max(0, v)
        v_cell.append(v)
        p_density.append(v * i * 1000) # mW/cm²
        
    return h2_prod_rate, i_limit_dynamic, i_range*1000, v_cell, p_density

h2_rate, i_lim, i_plot, v_plot, p_plot = calculate_system()

# ==========================================
# 5. 主畫面呈現
# ==========================================
st.title("⚡ NaBH₄ 燃料電池數位雙生控制台")
st.info(f"📋 **場景說明：** {scen_default['desc']}")

# A. 資料方塊 (Metrics)
m1, m2, m3, m4 = st.columns(4)
m1.metric("產氫速率 (H₂)", f"{h2_rate:.3f} L/min", delta="即時流量")
m2.metric("極限電流密度", f"{i_lim:.2f} A/cm²", delta="氫氣聯動")
m3.metric("最大功率點", f"{max(p_plot):.1f} mW/cm²")
m4.metric("反應床效率", f"{min(98.0, 70 + reactor_temp/3):.1f} %")

st.markdown("---")

# B. 圖表分佈
col_left, col_right = st.columns([1, 1])

with col_left:
    # 1. 產氫聯動分析圖
    st.subheader("💧 反應床產氫影響分析")
    # 生成多維度聯動數據
    temps = np.linspace(20, 80, 10)
    # 模擬固定濃度與流量下，溫度對產氫的影響
    h2_impact = [np.exp(-4000 / (8.314 * (t + 273.15))) * 1.5e6 * (concentration / 100) * (flow_rate / 1000) * 4 for t in temps]
    
    fig_h2 = go.Figure()
    fig_h2.add_trace(go.Scatter(x=temps, y=h2_impact, mode='lines+markers', name='產氫趨勢', line=dict(color='#00d1b2', width=4)))
    fig_h2.add_vline(x=reactor_temp, line_dash="dash", line_color="red", annotation_text="目前操作點")
    fig_h2.update_layout(title="反應溫度 vs 產氫速率", xaxis_title="溫度 (°C)", yaxis_title="H2 Rate (L/min)", height=400)
    st.plotly_chart(fig_h2, use_container_width=True)

with col_right:
    # 2. 電池性能極化圖
    st.subheader("📈 電池極化性能 (V-I)")
    fig_iv = go.Figure()
    fig_iv.add_trace(go.Scatter(x=i_plot, y=v_plot, name="電壓 (V)", line=dict(color='royalblue', width=3)))
    fig_iv.add_trace(go.Scatter(x=i_plot, y=p_plot, name="功率 (mW/cm²)", yaxis="y2", line=dict(color='orange', width=3)))
    
    fig_iv.update_layout(
        title="電氣特性聯動曲線",
        xaxis_title="電流密度 (mA/cm²)",
        yaxis=dict(title="電壓 (V)", titlefont=dict(color="royalblue"), tickfont=dict(color="royalblue")),
        yaxis2=dict(title="功率密度 (mW/cm²)", titlefont=dict(color="orange"), tickfont=dict(color="orange"), anchor="x", overlaying="y", side="right"),
        height=400,
        legend=dict(x=0.1, y=0.1),
        hovermode="x unified"
    )
    st.plotly_chart(fig_iv, use_container_width=True)

# C. 參數解釋表
with st.expander("📚 系統熱力學與流體力學參數說明"):
    st.write("""
    - **產氫速率 (L/min)**: 基於 Arrhenius 方程式，反應速度隨溫度上升呈指數級增加。
    - **進料流量**: 影響 NaBH4 溶液與催化劑反應床的接觸時間。
    - **聯動機制**: 當產氫量不足時，系統會自動下調『極限電流密度』，模擬氫氣供應不足導致的濃差極化現象。
    """)