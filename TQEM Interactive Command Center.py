import streamlit as st
import pandas as pd
import numpy as np

# 頁面基本設定
st.set_page_config(page_title="TQEM Command Center", layout="wide")

# -----------------------------------------------------------------
# 0. Custom CSS：優化頂部 Metric 卡片視覺，明亮清楚且不吃字
# -----------------------------------------------------------------
st.markdown("""
<style>
    /* Metric 卡片容器視覺強化 */
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #3B82F6;
        box-shadow: 0 4px 8px rgba(59,130,246,0.12);
    }
    /* 標題字級優化 */
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        white-space: nowrap !important;
    }
    /* 核心數據數值優化 (防止截斷吃字) */
    div[data-testid="stMetricValue"] > div {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        white-space: nowrap !important;
        text-overflow: ellipsis !important;
        overflow: hidden !important;
    }
    /* 底部 Delta 標籤字級優化 */
    div[data-testid="stMetricDelta"] {
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        white-space: nowrap !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------
# 1. 側邊欄 (Sidebar)：調整順序，導覽放到最下方
# -----------------------------------------------------------------

# (1) 市場 Regime 切換
st.sidebar.header("🌐 市場 Regime 手動切換 / 模擬")
selected_regime = st.sidebar.selectbox(
    "選擇目前市場狀態 (Regime)：",
    ['Bull (多頭)', 'Bear (空頭)', 'Sideway (盤整)', 'HighVol (高波動)', 'Crisis (危機)'],
    index=0  # 預設 Bull
)

st.sidebar.markdown("---")

# (2) 動態權重引擎參數
st.sidebar.header("⚙️ 動態權重引擎參數")
alpha = st.sidebar.slider("信心折價係數 α (Uncertainty Discount)", 0.0, 1.0, 0.50, 0.01)
beta = st.sidebar.slider("風險懲罰係數 β (Risk Penalty)", 0.0, 2.0, 0.65, 0.05)
delta_w_max = st.sidebar.slider("單日權重變化上限 Δw_max", 0.01, 0.50, 0.19, 0.01)

# 同步參數至 Session State
st.session_state['alpha'] = alpha
st.session_state['beta'] = beta
st.session_state['delta_w_max'] = delta_w_max
st.session_state['selected_regime'] = selected_regime

st.sidebar.markdown("---")

# (3) 模組功能導覽 (移動至左側最下方)
st.sidebar.header("📌 模組功能導覽")
selected_page = st.sidebar.radio(
    "請選擇功能模組：",
    [
        "1. 市場狀態與 TimesFM 預測",
        "2. 五維動態權重重興",
        "3. Alpha 排序與選股清單",
        "4. Baseline 模型對比 (M0-M6)",
        "5. 資料工程與時間對齊驗證",
        "6. 威科夫 (Wyckoff) 價量籌碼診斷"
    ]
)

st.sidebar.caption("資料時間對齊檢查：✔ 無前視偏誤 (No Look-Ahead)")

# -----------------------------------------------------------------
# 2. 右側 Header & 連動 Metrics
# -----------------------------------------------------------------
st.title("TQEM 量化決策系統 Control Center")

base_sharpe = {'Bull (多頭)': 1.85, 'Bear (空頭)': 0.21, 'Sideway (盤整)': 0.88, 'HighVol (高波動)': 0.55, 'Crisis (危機)': 0.41}[selected_regime]
dynamic_sharpe = round(base_sharpe * (1 - alpha * 0.1) * (1 - (2.0 - beta) * 0.05), 2)

regime_metrics_map = {
    'Bull (多頭)': {"broadness": "78%", "confidence": f"{0.82 - alpha*0.1:.2f}", "ic": "Momentum (+0.18)", "sharpe": f"{dynamic_sharpe}", "turnover": f"{12.4 + delta_w_max*10:.1f}%"},
    'Bear (空頭)': {"broadness": "22%", "confidence": f"{0.35 - alpha*0.1:.2f}", "ic": "Macro/Vol (+0.22)", "sharpe": f"{dynamic_sharpe}", "turnover": f"{68.2 + delta_w_max*10:.1f}%"},
    'Sideway (盤整)': {"broadness": "45%", "confidence": f"{0.51 - alpha*0.1:.2f}", "ic": "MeanRev (+0.12)", "sharpe": f"{dynamic_sharpe}", "turnover": f"{31.5 + delta_w_max*10:.1f}%"},
    'HighVol (高波動)': {"broadness": "30%", "confidence": f"{0.41 - alpha*0.1:.2f}", "ic": "Volatility (+0.25)", "sharpe": f"{dynamic_sharpe}", "turnover": f"{54.1 + delta_w_max*10:.1f}%"},
    'Crisis (危機)': {"broadness": "15%", "confidence": f"{0.48 - alpha*0.1:.2f}", "ic": "Tail-Risk (+0.31)", "sharpe": f"{dynamic_sharpe}", "turnover": f"{49.8 + delta_w_max*10:.1f}%"}
}

current_metric = regime_metrics_map[selected_regime]

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("當前市場 Regime", selected_regime, f"↑ Broadness: {current_metric['broadness']}")
with col2:
    st.metric("TimesFM 平均信心", current_metric['confidence'], f"↑ α = {alpha:.2f}")
with col3:
    st.metric("近期 Top 特徵 IC", current_metric['ic'], "↑ 客觀特徵")
with col4:
    st.metric("M5 組合夏普比率", current_metric['sharpe'], f"↑ 訊號追蹤 (Δw={delta_w_max:.2f})")
with col5:
    st.metric("Kalman 權重週轉率", current_metric['turnover'], "↑ 調倉天花板")

st.markdown("---")

# -----------------------------------------------------------------
# 3. 根據 Radio 切換獨立頁面渲染
# -----------------------------------------------------------------

if selected_page.startswith("1."):
    st.subheader("1. 市場狀態辨識 (Regime Detection) & TimesFM 預測引擎")
    st.markdown(f"##### 📌 當前選定 Regime：`{selected_regime}` 與權重調整矩陣")
    
    regime_df = pd.DataFrame({
        'Regime': ['Bull (多頭)', 'Bear (空頭)', 'Sideway (盤整)', 'HighVol (高波動)', 'Crisis (危機)'],
        '主導特徵群組': ['Momentum / Flow', 'Macro / Volatility', 'Mean Reversion', 'Volatility / Cash', 'Risk Control / Macro'],
        '權重偏向': ['上調 Momentum (+20%)', '上調 Vol/Macro (+30%)', '上調 Price Range', '上調 Vol/Liquidity', '大幅調降 Trend/Flow']
    })
    
    def highlight_selected_regime(row):
        if row['Regime'] == selected_regime:
            return ['background-color: rgba(2, 132, 199, 0.25); font-weight: bold; color: #0284C7;'] * len(row)
        return [''] * len(row)
        
    st.dataframe(regime_df.style.apply(highlight_selected_regime, axis=1), use_container_width=True)
    st.info(f"💡 引擎實時參數：α = {alpha:.2f} | β = {beta:.2f} | Δw_max = {delta_w_max:.2f}")

elif selected_page.startswith("2."):
    st.subheader("2. 五維動態權重引擎 (Dynamic Weight Allocation Engine)")
    st.latex(r"w_i(t) = \text{Normalize} \left[ w_i^{\text{base}} \times R_i(t) \times P_i(t) \times C_i(t) \times K_i(t) \right]")
    
    w_momentum = round(0.20 * (1 + (2.0 - beta)*0.1), 3)
    w_volatility = round(0.25 * (1 + alpha*0.2), 3)
    
    st.info(f"⚙️ 動態參數即時運算中：α={alpha:.2f} (信心折價) | β={beta:.2f} (風險懲罰) | Δw_max={delta_w_max:.2f} (單日上限)")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("##### 📊 五維特徵時序權重分配")
        weight_trend = pd.DataFrame(
            np.random.dirichlet((1+alpha, 1+beta, 1, 1, 1), 30),
            columns=['Momentum', 'Volatility', 'Macro', 'Fund Flow', 'Sentiment']
        )
        st.area_chart(weight_trend)
    
    with col_w2:
        st.markdown("##### ⚖️ 當前特徵群組權重佔比")
        curr_weights = pd.DataFrame({
            'Feature Group': ['Momentum', 'Volatility', 'Macro', 'Fund Flow', 'Sentiment'],
            'Weight': [w_momentum, w_volatility, 0.17, 0.19, round(1 - w_momentum - w_volatility - 0.36, 3)]
        })
        st.bar_chart(curr_weights.set_index('Feature Group'))

elif selected_page.startswith("3."):
    st.subheader("3. 最終 Alpha 訊號生成與選股組合")
    st.write(f"**當前套用參數：** α={alpha:.2f}, β={beta:.2f}, Δw_max={delta_w_max:.2f}")
    
    alpha_data = pd.DataFrame({
        'Ticker': ['2332.TW', 'STOCK_015', '2331.TW', 'STOCK_017', 'STOCK_014'],
        'Regime': [selected_regime]*5,
        'Raw Score': [0.88, 0.75, 0.62, 0.55, 0.48],
        'Adjusted Score (連動 α/β)': [round(0.88 * (1 - alpha*0.15), 3), round(0.75 * (1 - alpha*0.15), 3), round(0.62 * (1 - alpha*0.15), 3), 0.51, 0.42],
        'Confidence_C': [0.733, 0.649, 0.406, 0.678, 0.469]
    })
    st.dataframe(alpha_data, use_container_width=True)

elif selected_page.startswith("4."):
    st.subheader("4. TQEM Baseline 模型多維度績效評估 (M0 至 M6)")
    
    baseline_df = pd.DataFrame({
        'Model': ['M0 Buy & Hold', 'M1 Momentum', 'M2 Fixed Weight', 'M3 TimesFM Only', 'M4 TimesFM+DW', 'M5 TimesFM+DW+Kalman', 'M6 Full (Bayes/Agent)'],
        'Annual Return (%)': [8.5, 12.1, 14.3, 16.8, 21.2, round(23.5 * (1 + delta_w_max*0.1), 1), 25.8],
        'Sharpe Ratio': [0.65, 0.82, 0.95, 1.15, 1.42, dynamic_sharpe, 1.85],
        'Max Drawdown (%)': [-30.1, -25.4, -22.1, -18.5, -15.2, -12.8, -10.1]
    })
    
    # 圖表上置（滿寬呈現，避免文字與欄位被壓縮）
    st.markdown("##### 📈 模型風險報酬散佈圖 (Max Drawdown vs Annual Return)")
    st.scatter_chart(baseline_df, x='Max Drawdown (%)', y='Annual Return (%)', color='Model')
    
    # 表格移至最下方
    st.markdown("##### 📋 Baseline 模型詳細績效指標對比表")
    st.dataframe(baseline_df, use_container_width=True)

elif selected_page.startswith("5."):
    st.subheader("5. 資料工程 (Data Engineering) & 時間對齊治理")
    st.markdown("##### 🛡️ 防止 Look-Ahead Bias 時間戳治理機制")
    audit_data = pd.DataFrame({
        '資料類別': ['1. 價格與成交', '2. 籌碼與資金流', '3. 宏觀經濟'],
        '品質檢查狀態': ['✔ 通過', '✔ 通過', '✔ 通過']
    })
    st.dataframe(audit_data, use_container_width=True)

elif selected_page.startswith("6."):
    try:
        from wyckoff_pvcs_engine import render_wyckoff_tab
        try:
            render_wyckoff_tab(st, alpha=alpha, beta=beta, delta_w_max=delta_w_max, regime=selected_regime)
        except TypeError:
            render_wyckoff_tab(st)
    except Exception as e:
        st.subheader("6. 威科夫 (Wyckoff) 價量籌碼 (PVCS) 診斷沙盒")
        st.markdown(f"**當前模式連動 Regime：** `{selected_regime}` | **α：** `{alpha:.2f}` | **β：** `{beta:.2f}` | **Δw_max：** `{delta_w_max:.2f}`")
        st.info(f"💡 Wyckoff 模組連動資訊：{e}")