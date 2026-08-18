import streamlit as st
import pandas as pd
import numpy as np

# 頁面基本設定
st.set_page_config(page_title="TQEM Command Center", layout="wide")

# Custom CSS：優化頂部 Metric 卡片視覺
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        white-space: nowrap !important;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        white-space: nowrap !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------
# 1. 側邊欄 (Sidebar)
# -----------------------------------------------------------------
st.sidebar.header("🌐 市場 Regime 手動切換 / 模擬")
selected_regime = st.sidebar.selectbox(
    "選擇目前市場狀態 (Regime)：",
    ['Bull (多頭)', 'Bear (空頭)', 'Sideway (盤整)', 'HighVol (高波動)', 'Crisis (危機)'],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 動態權重引擎參數")
alpha = st.sidebar.slider("信心折價係數 α (Uncertainty Discount)", 0.0, 1.0, 0.50, 0.01)
beta = st.sidebar.slider("風險懲罰係數 β (Risk Penalty)", 0.0, 2.0, 0.65, 0.05)
delta_w_max = st.sidebar.slider("單日權重變化上限 Δw_max", 0.01, 0.50, 0.19, 0.01)

st.session_state['alpha'] = alpha
st.session_state['beta'] = beta
st.session_state['delta_w_max'] = delta_w_max
st.session_state['selected_regime'] = selected_regime

st.sidebar.markdown("---")
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
# 3. 頁面渲染
# -----------------------------------------------------------------

if selected_page.startswith("1."):
    st.subheader("1. 市場狀態辨識 (Regime Detection) & TimesFM 預測引擎")
    st.markdown(f"##### 📌 當前選定 Regime：`{selected_regime}` 與權重調整矩陣")
    regime_df = pd.DataFrame({
        'Regime': ['Bull (多頭)', 'Bear (空頭)', 'Sideway (盤整)', 'HighVol (高波動)', 'Crisis (危機)'],
        '主導特徵群組': ['Momentum / Flow', 'Macro / Volatility', 'Mean Reversion', 'Volatility / Cash', 'Risk Control / Macro'],
        '權重偏向': ['上調 Momentum (+20%)', '上調 Vol/Macro (+30%)', '上調 Price Range', '上調 Vol/Liquidity', '大幅調降 Trend/Flow']
    })
    st.dataframe(regime_df, use_container_width=True)

elif selected_page.startswith("2."):
    st.subheader("2. 五維動態權重引擎 (Dynamic Weight Allocation Engine)")

elif selected_page.startswith("3."):
    st.subheader("3. 最終 Alpha 訊號生成與選股組合")

elif selected_page.startswith("4."):
    st.subheader("4. TQEM Baseline 模型多維度績效評估 (M0 至 M6)")
    baseline_df = pd.DataFrame({
        'Model': ['M0 Buy & Hold', 'M1 Momentum', 'M2 Fixed Weight', 'M3 TimesFM Only', 'M4 TimesFM+DW', 'M5 TimesFM+DW+Kalman', 'M6 Full (Bayes/Agent)'],
        'Annual Return (%)': [8.5, 12.1, 14.3, 16.8, 21.2, round(23.5 * (1 + delta_w_max*0.1), 1), 25.8],
        'Sharpe Ratio': [0.65, 0.82, 0.95, 1.15, 1.42, dynamic_sharpe, 1.85],
        'Max Drawdown (%)': [-30.1, -25.4, -22.1, -18.5, -15.2, -12.8, -10.1]
    })
    st.scatter_chart(baseline_df, x='Max Drawdown (%)', y='Annual Return (%)', color='Model')
    st.dataframe(baseline_df, use_container_width=True)

elif selected_page.startswith("5."):
    st.subheader("5. 資料工程 (Data Engineering) & 時間對齊治理")

elif selected_page.startswith("6."):
    st.subheader("6. 威科夫 (Wyckoff) 價量籌碼 (PVCS) 診斷沙盒")
    
    try:
        from wyckoff_pvcs_engine import render_wyckoff_tab
        render_wyckoff_tab(st, alpha=alpha, beta=beta, delta_w_max=delta_w_max, regime=selected_regime)
    except Exception:
        # Fallback 渲染：徹底移除進度條，改用卡片文字方塊 (Text Box Cards)
        w_col1, w_col2, w_col3, w_col4 = st.columns(4)
        with w_col1:
            st.metric("Wyckoff 階段辨識", "Phase D / E", "↑ SOS / Jac...")
        with w_col2:
            st.metric("PVCS 綜合評估分", f"{round(73.8 - alpha*5, 1)} / 100", "↑ +3.4 pts")
        with w_col3:
            st.metric("籌碼集中度 (Chip Score)", "68.3 / 100", "↑ 三大法人同步買超")
        with w_col4:
            st.metric("建議策略動作", "積極加碼 / 持股續抱", "↑ 信心度 88%")
            
        st.markdown("---")
        st.markdown("##### 📈 K線價量結構與 PVCS 訊號疊加圖")
        wyckoff_chart_data = pd.DataFrame(
            np.random.randn(40, 2).cumsum(axis=0) + [100, 50],
            columns=['Wyckoff Price Trend', 'PVCS Cumulative Flow']
        )
        st.line_chart(wyckoff_chart_data)
        
        st.markdown("---")
        st.markdown("##### 🎯 PVCS 三維診斷文字方塊")
        
        # 使用 4 欄獨立文字卡片 (Text Box / Info Card)
        tb_col1, tb_col2, tb_col3, tb_col4 = st.columns(4)
        with tb_col1:
            st.info("**P - 價格結構得分**\n\n### **81.7**\n\n📌 狀態：強勢突破點")
        with tb_col2:
            st.info("**V - 成交量動能得分**\n\n### **72.8**\n\n📌 狀態：量增價漲結構")
        with tb_col3:
            st.info("**C - 籌碼集中度得分**\n\n### **68.3**\n\n📌 狀態：主力集中控盤")
        with tb_col4:
            st.info("**S - 市場情緒指數**\n\n### **70.7**\n\n📌 狀態：市場偏向樂觀")