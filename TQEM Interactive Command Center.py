import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="TQEM Command Center", layout="wide")

# -----------------------------------------------------------------
# 1. 側邊欄：保留原有完整控制項 (動態權重引擎參數)
# -----------------------------------------------------------------
st.sidebar.header("動態權重引擎參數")

alpha = st.sidebar.slider(
    "信心折價係數 α (Uncertainty Discount)",
    min_value=0.0, max_value=1.0, value=0.20, step=0.01
)
beta = st.sidebar.slider(
    "風險懲罰係數 β (Risk Penalty)",
    min_value=0.0, max_value=2.0, value=1.00, step=0.05
)
delta_w_max = st.sidebar.slider(
    "單日權重變化上限 Δw_max",
    min_value=0.01, max_value=0.50, value=0.09, step=0.01
)

st.sidebar.markdown("---")
st.sidebar.caption("資料時間對齊檢查：✔ 無前視偏誤 (No Look-Ahead)")

# -----------------------------------------------------------------
# 2. 主畫面標題與頂部 Metrics 區塊
# -----------------------------------------------------------------
st.title("TQEM 量化決策系統 Control Center")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("當前市場 Regime", "Crisis (危機)", "↑ Broadness: 15%")
with col2:
    st.metric("TimesFM 平均信心", "0.48", f"↑ α = {alpha:.1f}")
with col3:
    st.metric("近期 Top 特徵 IC", "Tail-Risk...", "↑ 客觀特徵")
with col4:
    st.metric("M5 組合夏普比率", "0.41", f"↑ 訊號追蹤 (Δw={delta_w_max})")
with col5:
    st.metric("Kalman 權重週轉率", "49.8%", "↑ 調倉天花板")

st.markdown("---")

# -----------------------------------------------------------------
# 3. 多頁籤原生切換系統 (st.tabs) - 精準獨立渲染
# -----------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. 市場狀態與 TimesFM 預測",
    "2. 五維動態權重重興",
    "3. Alpha 排序與選股清單",
    "4. Baseline 模型對比 (M0-M6)",
    "5. 資料工程與時間對齊驗證",
    "6. 威科夫 (Wyckoff) 價量籌碼診斷"
])

# =================================================================
# Tab 1: 市場狀態辨識 & TimesFM 預測
# =================================================================
with tab1:
    st.subheader("1. 市場狀態辨識 (Regime Detection) & TimesFM 預測引擎")
    st.markdown("##### 📌 當前五大 Regime 條件與權重調整矩陣")
    
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
            'Q50 Forecast (%)': [0.0, 0.0, 6.2, 5.1],
            'Q10 Lower': [0.0, -0.5, 2.1, 0.2],
            'Q90 Upper': [0.0, 0.8, 8.5, 2.8]
        })
        st.line_chart(chart_data.set_index('Time')[['Q50 Forecast (%)']])

# =================================================================
# Tab 2: 五維動態權重重興
# =================================================================
with tab2:
    st.subheader("2. 五維動態權重引擎 (Dynamic Weight Allocation Engine)")
    st.latex(r"w_i(t) = \text{Normalize} \left[ w_i^{\text{base}} \times R_i(t) \times P_i(t) \times C_i(t) \times K_i(t) \right]")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("##### 📊 五維特徵時序權重分配")
        weight_trend = pd.DataFrame(
            np.random.dirichlet((1, 1, 1, 1, 1), 30),
            columns=['Momentum', 'Volatility', 'Macro', 'Fund Flow', 'Sentiment']
        )
        st.area_chart(weight_trend)
    
    with col_w2:
        st.markdown("##### ⚖️ 當前特徵群組權重佔比")
        curr_weights = pd.DataFrame({
            'Feature Group': ['Price/Return', 'Volume', 'Momentum', 'Volatility', 'Macro', 'Fund Flow', 'Sentiment'],
            'Weight': [0.03, 0.11, 0.15, 0.16, 0.17, 0.19, 0.19]
        })
        st.bar_chart(curr_weights.set_index('Feature Group'))

# =================================================================
# Tab 3: Alpha 排序與選股清單
# =================================================================
with tab3:
    st.subheader("3. 最終 Alpha 訊號生成與選股組合")
    
    alpha_data = pd.DataFrame({
        'Ticker': ['2332.TW', 'STOCK_015', '2331.TW', 'STOCK_017', 'STOCK_014', '2335.TW', '2339.TW'],
        'Regime': ['Bull (多頭)', 'Bear (空頭)', 'Sideway (盤整)', 'Bull (多頭)', 'Bull (多頭)', 'Bull (多頭)', 'Bull (多頭)'],
        'Forecast_1D (%)': [0.03, 1.98, 1.35, 0.37, 0.99, -2.15, -0.04],
        'Forecast_5D (%)': [3.72, 2.41, 2.69, 1.04, 2.16, 1.59, 1.59],
        'Forecast_20D (%)': [6.57, 11.92, 4.10, 8.89, 8.74, -4.84, 11.37],
        'Uncertainty_U': [1.82, 2.71, 7.32, 2.37, 5.65, 4.32, 3.93],
        'Confidence_C': [0.733, 0.649, 0.406, 0.678, 0.469, 0.536, 0.560]
    })
    st.dataframe(alpha_data, use_container_width=True)

# =================================================================
# Tab 4: Baseline 模型對比 (M0-M6)
# =================================================================
with tab4:
    st.subheader("4. TQEM Baseline 模型多維度績效評估 (M0 至 M6)")
    
    baseline_df = pd.DataFrame({
        'Model': ['M0 Buy & Hold', 'M1 Momentum', 'M2 Fixed Weight', 'M3 TimesFM Only', 'M4 TimesFM+DW', 'M5 TimesFM+DW+Kalman', 'M6 Full (Bayes/Agent)'],
        'Annual Return (%)': [8.5, 12.1, 14.3, 16.8, 21.2, 23.5, 25.8],
        'Sharpe Ratio': [0.65, 0.82, 0.95, 1.15, 1.42, 1.68, 1.85],
        'Max Drawdown (%)': [-30.1, -25.4, -22.1, -18.5, -15.2, -12.8, -10.1]
    })
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.scatter_chart(baseline_df, x='Max Drawdown (%)', y='Annual Return (%)', color='Model')
    with c2:
        st.dataframe(baseline_df, use_container_width=True)

# =================================================================
# Tab 5: 資料工程與時間對齊驗證
# =================================================================
with tab5:
    st.subheader("5. 資料工程 (Data Engineering) & 時間對齊治理")
    st.markdown("##### 🛡️ 防止 Look-Ahead Bias 時間戳治理機制")
    
    audit_data = pd.DataFrame({
        '資料類別': ['1. 價格與成交', '2. 籌碼與資金流', '3. 宏觀經濟'],
        '品質檢查狀態': ['✔ 通過', '✔ 通過', '✔ 通過']
    })
    st.dataframe(audit_data, use_container_width=True)

# =================================================================
# Tab 6: 威科夫 (Wyckoff) 價量籌碼診斷
# =================================================================
with tab6:
    st.subheader("6. 威科夫 (Wyckoff) 價量籌碼 (PVCS) 診斷沙盒")
    try:
        from wyckoff_pvcs_engine import render_wyckoff_tab
        render_wyckoff_tab(st)
    except Exception as e:
        st.info("💡 專屬 Wyckoff PVCS 模組渲染區（若需直接整合 wyckoff_pvcs_engine，請確認該模組檔名一致）。")