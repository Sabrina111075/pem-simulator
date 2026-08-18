import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="TQEM Command Center", layout="wide")

# Title & Dashboard Metrics Header
st.title("TQEM 量化決策系統 Control Center")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("當前市場 Regime", "Crisis (危機)", "↑ Broadness: 15%")
with col2:
    st.metric("TimesFM 平均信心", "0.48", "↑ α = 0.2")
with col3:
    st.metric("近期 Top 特徵 IC", "Tail-Risk...", "↑ 客觀特徵 (不受...)")
with col4:
    st.metric("M5 組合夏普比率", "0.41", "↑ 訊號追蹤 (Δw=0....)")
with col5:
    st.metric("Kalman 權重週轉率", "49.8%", "↑ 調倉天花板 (Δw=...")

st.markdown("---")

# -----------------------------------------------------------------
# 1. 側邊欄選單
# -----------------------------------------------------------------
selected_page = st.sidebar.radio("📌 模組功能導覽", [
    "1. 市場狀態與 TimesFM 預測",
    "2. 五維動態權重重興",
    "3. Alpha 排序與選股清單",
    "4. Baseline 模型對比 (M0-M6)",
    "5. 資料工程與時間對齊驗證",
    "6. 威科夫 (Wyckoff) 價量籌碼診斷"
])

# -----------------------------------------------------------------
# 2. 條件路由渲染 (嚴格單一渲染，絕不混淆)
# -----------------------------------------------------------------

if selected_page.startswith("1."):
    st.subheader("1. 市場狀態辨識 (Regime Detection) & TimesFM 預測引擎")
    st.markdown("##### 🔍 當前五大 Regime 條件與權重調整矩陣")
    
    regime_df = pd.DataFrame({
        'Regime': ['Bull (多頭)', 'Bear (空頭)', 'Sideway (盤整)', 'HighVol (高波動)', 'Crisis (危機)'],
        '主導特徵群組': ['Momentum / Flow', 'Macro / Volatility', 'Mean Reversion', 'Volatility / Cash', 'Risk Control / Macro'],
        '權重偏向': ['上調 Momentum (+20%)', '上調 Vol/Macro (+30%)', '上調 Price Range', '上調 Vol/Liquidity', '大幅調降 Trend/Flow']
    })
    
    current_regime = 'Crisis (危機)'
    def highlight_selected_regime(row):
        if row['Regime'] == current_regime:
            return ['background-color: rgba(2, 132, 199, 0.25); font-weight: bold; color: #0284C7;'] * len(row)
        return [''] * len(row)
        
    st.dataframe(regime_df.style.apply(highlight_selected_regime, axis=1), use_container_width=True)
    st.info("💡 Regime 判定規則：根據 MA20-MA60 趨勢、市場廣度 (Breadth) 與 20日波動率 σ_20 自動判定。")
    
    st.markdown("---")
    st.markdown("##### 📈 個股 TimesFM 多時間尺度預測與不確定性 (Quantile Range)")
    
    col_sel, col_chart = st.columns([1, 2])
    with col_sel:
        ticker = st.selectbox("選擇預測個股：", ["2336.TW", "2331.TW", "2332.TW", "2335.TW", "STOCK_015"])
        st.write(f"**目前選取：** `{ticker}`")
        st.write("**不確定區間 U：** `3.63`")
        st.write("**模型信心 C_i：** `0.579`")
        
    with col_chart:
        chart_data = pd.DataFrame({
            'Time': ['Current', 'T+1D', 'T+5D', 'T+20D'],
            'Q50 Forecast': [0.0, 0.0, 6.2, 5.1],
            'Q10 Lower': [0.0, -0.5, 2.1, 0.2],
            'Q90 Upper': [0.0, 0.8, 8.5, 2.8]
        })
        st.line_chart(chart_data.set_index('Time')[['Q50 Forecast']])

elif selected_page.startswith("2."):
    st.subheader("2. 五維動態權重引擎 (Dynamic Weight Allocation Engine)")
    st.latex(r"w_i(t) = \text{Normalize} \left[ w_i^{\text{base}} \times R_i(t) \times P_i(t) \times C_i(t) \times K_i(t) \right]")
    st.write("五維動態權重演算法分析數據繪製區塊...")

elif selected_page.startswith("3."):
    st.subheader("3. 最終 Alpha 訊號生成與選股組合")
    st.write("Alpha 選股清單與綜合評分排序數據表...")

elif selected_page.startswith("4."):
    st.subheader("4. TQEM Baseline 模型多維度績效評估 (M0 至 M6)")
    st.write("M0 - M6 Baseline 模型對比圖表與 Sharpe Ratio / Max Drawdown 績效表...")

elif selected_page.startswith("5."):
    st.subheader("5. 資料工程 (Data Engineering) & 時間對齊治理")
    st.write("Look-Ahead Bias 時間戳治理與資料品質檢查報告...")

elif selected_page.startswith("6."):
    st.subheader("6. 威科夫 (Wyckoff) 價量籌碼 (PVCS) 診斷沙盒")
    try:
        from wyckoff_pvcs_engine import render_wyckoff_tab
        render_wyckoff_tab(st)
    except Exception as e:
        st.error(f"Wyckoff 模組載入失敗，請檢查 wyckoff_pvcs_engine.py 檔案是否存在：{e}")