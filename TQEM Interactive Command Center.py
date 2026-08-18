import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pytz  # 引入時區處理套件

# -----------------------------------------------------------------------------
# 頁面配置 (Page Configuration)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TQEM-100 TimesFM 量化基金評估與動態權重控制台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 樣式 (優化標題、KPI 指標卡與即時時間樣式)
st.markdown("""
<style>
    /* 主標題字體加大 */
    .main-header {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: #0F172A;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }
    /* 子標題與時間容器 */
    .sub-header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 1.8rem;
        gap: 10px;
    }
    .sub-header-text {
        font-size: 1.1rem;
        color: #64748B;
    }
    .live-time-badge {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.95rem;
        font-weight: 600;
        border: 1px solid #BAE6FD;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    /* 頂部 KPI 指標卡優化 (防吃字與增強顯眼度) */
    [data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        white-space: nowrap !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }
    
    /* Tab 標籤樣式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #F1F5F9;
        border-radius: 8px 8px 0px 0px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284C7;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 時區與時間動態計算 (台北時區)
# -----------------------------------------------------------------------------
taipei_tz = pytz.timezone('Asia/Taipei')
current_time_taipei = datetime.now(taipei_tz).strftime('%Y-%m-%d %H:%M:%S')

# -----------------------------------------------------------------------------
# 模擬數據生成器 (Mock Data Generator)
# -----------------------------------------------------------------------------
@st.cache_data
def load_mock_data():
    dates = pd.date_range(end=datetime.today(), periods=180, freq='B')
    np.random.seed(42)
    
    features = ['Price/Return', 'Volume', 'Momentum', 'Volatility', 'Macro', 'Fund Flow', 'Sentiment']
    
    # 模擬歷史動態權重數據
    raw_weights = np.random.dirichlet(np.ones(7), size=len(dates))
    df_raw_weights = pd.DataFrame(raw_weights, index=dates, columns=features)
    
    df_kalman_weights = df_raw_weights.rolling(window=5, min_periods=1).mean()
    df_kalman_weights = df_kalman_weights.div(df_kalman_weights.sum(axis=1), axis=0)
    
    # 模擬個股 Forecast & Uncertainty
    stock_list = [f"{2330 + i}.TW" for i in range(10)] + [f"STOCK_{i:03d}" for i in range(11, 101)]
    df_stocks = pd.DataFrame({
        'Ticker': stock_list[:20],
        'Regime': np.random.choice(['Bull (多頭)', 'Bear (空頭)', 'Sideway (盤整)', 'HighVol (高波動)', 'Crisis (危機)'], size=20, p=[0.4, 0.2, 0.2, 0.1, 0.1]),
        'Forecast_1D (%)': np.round(np.random.normal(0.3, 1.2, 20), 2),
        'Forecast_5D (%)': np.round(np.random.normal(1.1, 2.5, 20), 2),
        'Forecast_20D (%)': np.round(np.random.normal(3.5, 5.0, 20), 2),
        'Q10 (%)': np.round(np.random.normal(-1.5, 1.0, 20), 2),
        'Q90 (%)': np.round(np.random.normal(2.5, 1.5, 20), 2),
    })
    df_stocks['Uncertainty_U'] = np.round(df_stocks['Q90 (%)'] - df_stocks['Q10 (%)'], 2)
    df_stocks['Confidence_C'] = np.round(1 / (1 + 0.2 * df_stocks['Uncertainty_U']), 3)
    df_stocks['Alpha_Score'] = np.round(df_stocks['Forecast_5D (%)'] * 0.6 + np.random.normal(0, 0.5, 20), 3)
    df_stocks = df_stocks.sort_values(by='Alpha_Score', ascending=False).reset_index(drop=True)
    
    # Baseline 模型比較數據
    df_models = pd.DataFrame({
        'Model': ['M0 Buy & Hold', 'M1 Momentum', 'M2 Fixed Weight', 'M3 TimesFM Only', 'M4 TimesFM+DW', 'M5 TimesFM+DW+Kalman', 'M6 Full (Bayes/Agent)'],
        'Annual Return (%)': [8.5, 12.1, 14.3, 16.8, 21.2, 23.5, 25.8],
        'Sharpe Ratio': [0.65, 0.82, 0.95, 1.15, 1.42, 1.68, 1.85],
        'Max Drawdown (%)': [-28.4, -22.1, -19.5, -16.2, -12.8, -9.5, -8.2],
        'ICIR': [0.21, 0.38, 0.45, 0.62, 0.85, 1.02, 1.18],
        'Weight Turnover (%)': [0.0, 15.2, 0.0, 18.5, 24.1, 8.2, 7.5]
    })
    
    return dates, features, df_raw_weights, df_kalman_weights, df_stocks, df_models

dates, features, df_raw_weights, df_kalman_weights, df_stocks, df_models = load_mock_data()

# -----------------------------------------------------------------------------
# 側邊欄 (Sidebar Control)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/chart-line.png", width=60)
    st.title("TQEM 控制台面板")
    st.caption("TimesFM Quant Evaluation Model v1.0")
    st.markdown("---")
    
    current_regime = st.selectbox(
        "當前市場狀態 (Market Regime)",
        ['Bull (多頭)', 'Bear (空頭)', 'Sideway (盤整)', 'HighVol (高波動)', 'Crisis (危機)'],
        index=4  # 對應截圖中的 Crisis (危機)
    )
    
    st.markdown("### 動態權重引擎參數")
    alpha_param = st.slider("信心折價係數 α (Uncertainty Discount)", 0.0, 1.0, 0.2, 0.05)
    beta_param = st.slider("風險懲罰係數 β (Risk Penalty)", 0.5, 3.0, 1.0, 0.1)
    delta_w_max = st.slider("單日權重變化上限 Δw_max", 0.01, 0.20, 0.09, 0.01)
    
    st.markdown("---")
    # 💡 依據要求：此處已移除原本的「資料更新時間」
    st.caption("資料時間對齊檢查：✅ 無前視偏誤 (No Look-Ahead)")

# -----------------------------------------------------------------------------
# 主頁面 Header & 核心動態連動指標
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">TimesFM TQEM 量化基金評估與動態權重管理平台</div>', unsafe_allow_html=True)

# 💡 依據要求：在標題下方整併子標題與台北時區實時時間
st.markdown(f"""
<div class="sub-header-container">
    <div class="sub-header-text">整合 Data Layer 治理、Regime 辨識、TimesFM 時間序列預測、五維動態權重與 Kalman 平滑之完整量化研究工作流</div>
    <div class="live-time-badge">🕒 台北時間 (TST)：{current_time_taipei}</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 頂部關鍵指標 (融入 alpha 與 Regime 雙重動態機制)
# -----------------------------------------------------------------------------
regime_stats = {
    'Bull (多頭)':    {'base_conf': 0.88, 'base_sharpe': 2.15, 'base_turnover': 6.5,  'ic': 'Momentum (0.16)', 'broadness': '68%'},
    'Bear (空頭)':    {'base_conf': 0.72, 'base_sharpe': 1.12, 'base_turnover': 12.4, 'ic': 'Macro (0.14)',    'broadness': '32%'},
    'Sideway (盤整)': {'base_conf': 0.78, 'base_sharpe': 1.45, 'base_turnover': 9.1,  'ic': 'Volatility (0.11)','broadness': '48%'},
    'HighVol (高波動)':{'base_conf': 0.65, 'base_sharpe': 0.98, 'base_turnover': 18.2, 'ic': 'Cash/Risk (0.18)','broadness': '25%'},
    'Crisis (危機)':   {'base_conf': 0.52, 'base_sharpe': 0.42, 'base_turnover': 24.5, 'ic': 'Tail-Risk (0.22)','broadness': '15%'}
}

stats = regime_stats.get(current_regime, regime_stats['Bull (多頭)'])

# 根據 alpha_param 計算動態變化
dynamic_confidence = round(stats['base_conf'] / (1 + 0.5 * alpha_param), 2)
# alpha 提高 -> 風控提升 -> 夏普比率稍微優化；週轉率隨權重重構增加
dynamic_sharpe = round(stats['base_sharpe'] * (1 + 0.15 * alpha_param), 2)
dynamic_turnover = round(stats['base_turnover'] * (1 + 0.25 * alpha_param), 1)

# 渲染 5 大 KPI 卡片
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.metric("當前市場 Regime", f"{current_regime}", delta=f"Broadness: {stats['broadness']}")
with kpi2:
    st.metric("TimesFM 平均信心", f"{dynamic_confidence}", delta=f"α = {alpha_param}")
with kpi3:
    st.metric("近期 Top 特徵 IC", stats['ic'], delta="客觀特徵 (不受 α 影響)")
with kpi4:
    st.metric("M5 組合夏普比率", f"{dynamic_sharpe}", delta=f"風控校正 (α={alpha_param})")
with kpi5:
    st.metric("Kalman 權重週轉率", f"{dynamic_turnover}%", delta=f"調倉反應 (α={alpha_param})")

st.markdown("---")

# -----------------------------------------------------------------------------
# 分頁標籤 (Main Tabs)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 1. 市場狀態與 TimesFM 預測", 
    "⚖️ 2. 五維動態權重與 Kalman 平滑", 
    "🎯 3. Alpha 排序與選股清單", 
    "📈 4. Baseline 模型對比 (M0-M6)", 
    "🛡️ 5. 資料工程與時間對齊驗證"
])

# -----------------------------------------------------------------------------
# Tab 1: 市場狀態與 TimesFM 預測
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("市場狀態辨識 (Regime Detection) & TimesFM 預測引擎")
    
    st.markdown("##### 📌 當前五大 Regime 條件與權重調整矩陣")
    regime_df = pd.DataFrame({
        'Regime': ['Bull (多頭)', 'Bear (空頭)', 'Sideway (盤整)', 'HighVol (高波動)', 'Crisis (危機)'],
        '主導特徵群組': ['Momentum / Flow', 'Macro / Volatility', 'Mean Reversion', 'Volatility / Cash', 'Risk Control / Macro'],
        '權重偏向': ['上調 Momentum (+20%)', '上調 Vol/Macro (+30%)', '上調 Price Range', '上調 Vol/Liquidity', '大幅調降 Trend/Flow']
    })
    
    def highlight_selected_regime(row):
        if row['Regime'] == current_regime:
            return ['background-color: rgba(2, 132, 199, 0.25); font-weight: bold; color: #0284C7;'] * len(row)
        return [''] * len(row)
        
    st.dataframe(regime_df.style.apply(highlight_selected_regime, axis=1), hide_index=True, use_container_width=True)
    st.info("💡 **Regime 判定規則**：根據 MA20-MA60 趨勢、市場廣度 (Breadth) 與 20日波動率 $\sigma_{20}$ 自動判定。")
    
    st.markdown("---")
    
    st.markdown("##### 📈 個股 TimesFM 多時間尺度預測與不確定性 (Quantile Range)")
    
    c_select, c_chart = st.columns([1, 3])
    with c_select:
        selected_ticker = st.selectbox("選擇預測個股：", df_stocks['Ticker'].tolist(), index=0)
        stock_row = df_stocks[df_stocks['Ticker'] == selected_ticker].iloc[0]
        st.write(f"**目前選取**：`{selected_ticker}`")
        st.write(f"**不確定區間 U**：`{stock_row['Uncertainty_U']}`")
        st.write(f"**模型信心 C_i**：`{stock_row['Confidence_C']}`")

    with c_chart:
        horizons = ['Current', 'T+1D', 'T+5D', 'T+20D']
        q50_vals = [0, stock_row['Forecast_1D (%)'], stock_row['Forecast_5D (%)'], stock_row['Forecast_20D (%)']]
        q10_vals = [0, stock_row['Q10 (%)']*0.3, stock_row['Q10 (%)']*0.6, stock_row['Q10 (%)']]
        q90_vals = [0, stock_row['Q90 (%)']*0.3, stock_row['Q90 (%)']*0.6, stock_row['Q90 (%)']]
        
        fig_fan = go.Figure()
        fig_fan.add_trace(go.Scatter(x=horizons, y=q90_vals, mode='lines', line=dict(width=0), name='Q90 (上界)'))
        fig_fan.add_trace(go.Scatter(x=horizons, y=q10_vals, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(2, 132, 199, 0.2)', name='Uncertainty Interval (Q90-Q10)'))
        fig_fan.add_trace(go.Scatter(x=horizons, y=q50_vals, mode='lines+markers', line=dict(color='#0284C7', width=3), name='Q50 Forecast (中位數)'))
        
        fig_fan.update_layout(
            title=f"{selected_ticker} TimesFM 預測走勢與 Quantile 不確定性區間 (U = {stock_row['Uncertainty_U']})",
            yaxis_title="預期報酬率 (%)",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_fan, use_container_width=True)

# -----------------------------------------------------------------------------
# 後續的分頁 (Tab 2 - Tab 5) 保持原樣
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("五維動態權重引擎 (Dynamic Weight Allocation Engine)")
    st.latex(r"w_i(t) = \text{Normalize}\left[ w_i^{\text{base}} \times R_i(t) \times P_i(t) \times C_i(t) \times K_i(t) \right]")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        fig_area = px.area(df_kalman_weights, x=df_kalman_weights.index, y=features, title="Kalman 平滑後之 7 大特徵群組歷史動態權重趨勢", labels={'value': '權重比例', 'index': '日期'}, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_area.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_area, use_container_width=True)
        
    with col_w2:
        latest_raw = df_raw_weights.iloc[-1].copy()
        if "Bear" in current_regime or "Crisis" in current_regime:
            latest_raw['Macro'] += 0.15; latest_raw['Volatility'] += 0.1; latest_raw['Momentum'] -= 0.15
        latest_raw = latest_raw / latest_raw.sum()
        latest_kalman = latest_raw.rolling(window=3, min_periods=1).mean()
        latest_kalman = latest_kalman / latest_kalman.sum()
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=features, y=latest_raw, name='原始計算權重 (Raw Weight)', marker_color='#CBD5E1'))
        fig_bar.add_trace(go.Bar(x=features, y=latest_kalman, name='Kalman 平滑權重 (Filtered)', marker_color='#0284C7'))
        fig_bar.update_layout(title=f"當日特徵權重調整狀況 ({current_regime} 情境)", barmode='group', yaxis_title="權重比重", height=380, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    st.subheader("最終 Alpha 訊號生成與選股組合 (Portfolio Optimization Input)")
    st.latex(r"\text{Alpha}_{\text{final}}(i,t) = \beta_1 \cdot \text{Alpha}_{\text{feature}}(i,t) + \beta_2 \cdot \text{Forecast}_{\text{TimesFM}}(i,t)")
    formatted_df = df_stocks.copy()
    def highlight_alpha(val): return f"color: {'#DC2626' if val < 0 else '#16A34A'}; font-weight: bold;"
    st.dataframe(formatted_df.style.map(highlight_alpha, subset=['Alpha_Score', 'Forecast_5D (%)']), use_container_width=True, height=400)

with tab4:
    st.subheader("TQEM Baseline 模型多維度績效評估 (M0 至 M6)")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        fig_scatter = px.scatter(df_models, x='Max Drawdown (%)', y='Annual Return (%)', size='Sharpe Ratio', color='Model', text='Model', title="風報比分析：年化報酬率 vs 最大回撤", color_discrete_sequence=px.colors.qualitative.Bold)
        fig_scatter.update_traces(textposition='top center').update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_scatter, use_container_width=True)
    with col_m2:
        st.dataframe(df_models, hide_index=True, use_container_width=True, height=350)

with tab5:
    st.subheader("資料工程 (Data Engineering) & 時間對齊治理")
    st.markdown("#### 🛡️ 防止 Look-Ahead Bias 時間戳治理機制")
    time_col1, time_col2, time_col3, time_col4 = st.columns(4)
    with time_col1: st.markdown("<div style='background-color:#F8FAFC; border:1px solid #E2E8F0; padding:10px; border-radius:8px;'><b>1. Event Time</b><br><small>事件發生時間</small></div>", unsafe_allow_html=True)
    with time_col2: st.markdown("<div style='background-color:#F8FAFC; border:1px solid #E2E8F0; padding:10px; border-radius:8px;'><b>2. Publish Time</b><br><small>資訊公開時間</small></div>", unsafe_allow_html=True)
    with time_col3: st.markdown("<div style='background-color:#F8FAFC; border:1px solid #E2E8F0; padding:10px; border-radius:8px;'><b>3. Ingest Time</b><br><small>系統接收時間</small></div>", unsafe_allow_html=True)
    with time_col4: st.markdown("<div style='background-color:#F8FAFC; border:1px solid #E2E8F0; padding:10px; border-radius:8px;'><b>4. Effective Time</b><br><small>可使用最早時間</small></div>", unsafe_allow_html=True)
    st.markdown("---")
    data_layer_df = pd.DataFrame({'資料類別': ['1. 價格與成交', '2. 籌碼與資金流', '3. 宏觀經濟'], '品質檢查狀態': ['✅ 通過', '✅ 通過', '✅ 通過']})
    st.dataframe(data_layer_df, hide_index=True, use_container_width=True)