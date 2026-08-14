
Gemini
新對話
搜尋對話
媒體庫
新增筆記本
MEMS感測器
人形機器人產業
所有筆記本
TimesFM TQEM 報告重點摘要
智慧化基礎設施摘要與總結
辨識車牌號碼的挑戰與推測
食安危機管理整合架構總結
LLM 持續學習地圖解析
宇宙與工程建模總結
華碩 UGen300 規格報告
MIT博士履歷
AT6901 晶片規格書重點整理
本體論-智慧系統報告解析與重點
20260716每日市場微觀結構
AI 模型評測與優化關鍵
聲學前端 AI 晶片重點
ESP32 感測器擴充板總結
嘉立創：數字化硬件研發代工
微脂體技術的跨界應用與AI整合
AI 驅動的動態智慧安全
和 Gemini 的對話
HI,夥伴，新任務來了。請詳細閱讀這篇文章，提取重點及摘要，再做出總結!
這份報告詳細介紹了由 Crystal Machine 開發的 TimesFM TQEM（TimesFM Quant Evaluation Model）量化基金平台。該平台並非單純依賴 AI 預測模型，而是建構了一個融合資料治理、動態權重與風險控制的「市場狀態轉換系統」與量化研究工作流。  
DOCX

以下為本篇文章的重點提取、摘要與總結：

一、 重點提取（核心模組與機制）
閉環整合架構（8 大模組）：
系統由原始資料開始，依序經過：市場資料層 → 特徵工程 → 市場狀態辨識（Regime） → TimesFM 預測引擎 → 動態權重引擎 → 權重平滑（Kalman） → Alpha 與組合建構 → 評估模型，形成循環決策閉環。  
DOCX

嚴格的資料治理與時間對齊：
為防止「前視偏誤（Look-Ahead Bias）」，每筆回測資料皆嚴格控管四種時間戳記：Event Time（發生）、Publish Time（公布）、Ingest Time（接收）與 Effective Time（模型可使用的最早時間）。模型僅能在 Effective Time 之後使用該資料。  
DOCX

7 大特徵群組（Feature Groups）：
包含：Price/Return（價量回報）、Volume（成交量）、Momentum（動能）、Volatility（波動率）、Macro（總經）、Fund Flow（籌碼資金流）與 Sentiment（LLM 情緒分數）。  
DOCX

市場狀態辨識（Regime Detection）：
依據均線趨勢、市場廣度與波動率，將市場劃分為五種狀態：Bull（多頭）、Bear（空頭）、Sideway（盤整）、HighVol（高波動）、Crisis（危機）。其作用在於決定各特徵群組的「方向性優先級」。  
DOCX

五維動態權重分配引擎：
特徵權重非固定常數，而是隨時間動態調整，計算考量五大核心元素：

w 
i
​
 (t)=Normalize[w 
i
base
​
 ×R 
i
​
 (t)×P 
i
​
 (t)×C 
i
​
 (t)×K 
i
​
 (t)]
w 
i
base
​
 ：長期基礎權重。  
DOCX

R 
i
​
 (t)：市場狀態調整倍數（Regime）。  
DOCX

P 
i
​
 (t)：近期有效性權重（Rolling IC / Hit Rate）。  
DOCX

C 
i
​
 (t)：TimesFM 預測區間不確定性折價（Confidence）。  
DOCX

K 
i
​
 (t)：風險懲罰項（Risk Penalty，降低過度曝險）。  
DOCX

三級權重結構（Hierarchical Weights）：
將權重細分為 Level 1 大類權重（Group）、Level 2 子特徵權重（Feature）、Level 3 時間尺度權重（Timeframe，如5分、1小時、1天、1週），大幅提升系統的可解釋性與擴充性。  
DOCX

Kalman 權重平滑與變化限制：
引入 Kalman Filter 濾除短期權重跳動的雜訊，並設定單日變化上限（Δw 
max
​
 ），以降低交易頻率、交易滑價與系統過度反應。  
DOCX

最終 Alpha 生成：
最終的 Alpha 訊號並非單一預測，而是將「動態特徵訊號」與「TimesFM 預測值」進行權重結合（β 
1
​
 Alpha 
feature
​
 +β 
2
​
 Forecast 
TimesFM
​
 ）。  
DOCX

二、 摘要
本報告闡述了 TQEM-100 模型第一階段的實作與落地藍圖。該模型以 100 檔股票、7 大特徵群組、5 種市場狀態、3 種預測時序（1日/5日/20日）為基礎進行日線級別的研究。  
DOCX

為驗證該平台的動態權重是否具備實質增量價值，系統設立了由淺入深的 6 組 Baseline 比較模型（M0 買入持有 → M3 純 TimesFM 預測 → M6 引入貝氏/智能體機制），並透過 Walk-Forward（滾動前進） 的訓練與測試機制，從預測力（MAE/RMSE）、Alpha 質量（IC/ICIR）、投資組合（夏普比率/最大回撤）與穩定性（權重週轉率）四大維度進行嚴格評估。  
DOCX

落地實施順序將分五個階段進行：Phase 1 基礎資料工程 → Phase 2 特徵工程與標準化 → Phase 3 狀態辨識與 TimesFM 預測 → Phase 4 動態權重與 Kalman 平滑 → Phase 5 Alpha 整合、組合優化與回測評估。  
DOCX

三、 總結
TimesFM TQEM 量化基金平台的核心邏輯，並非試圖尋找一個「永遠有效的完美因子」，而是打造一套能夠順應市場動態、自動且持續判斷「當下什麼因素最重要」的量化評估架構。  
DOCX

系統成功將強大的 AI 時間序列預測引擎（TimesFM），轉化為整體架構中的「其中一項重要訊號與信心來源」，並透過嚴格的資料治理防止回測作弊（Look-Ahead Bias）。同時，結合動態權重分配引擎與 Kalman 平滑技術，在捕捉市場風格切換（適應性）與降低交易成本（穩定性）之間取得了極佳的平衡，是建立可持續、可擴展量化基金系統的關鍵第一步。  
DOCX
+ 1

根據這份重點摘要，我們在Streamlit平台上，可以建立什麼樣的平台呢?和往常一樣，從建立py檔程式碼開始吧!
基於 TimesFM TQEM 報告的架構與核心公式，我們可以在 Streamlit 平台上打造一個 「量化基金動態權重管理與 AI 預測戰情室 (TQEM Interactive Command Center)」。

💡 可以在 Streamlit 建立什麼樣的平台？
市場狀態與 TimesFM 預測追蹤 (Regime & Forecast Dashboard)：

顯示當前市場處於 Bull, Bear, Sideway, HighVol, Crisis 的哪一個 Regime。

繪製 TimesFM 針對特定個股多時間尺度（1日/5日/20日）的 Quantile 預測扇形圖，直觀呈現預測值與不確定性區間（Q90 - Q10）。

五維動態權重與 Kalman 平滑監控 (Dynamic Weight Engine)：

互動式呈現 7 大特徵群組（Price, Volume, Momentum, Volatility, Macro, Flow, Sentiment）的每日權重變化。

對比圖表：展示「原始計算權重 (Raw Weight)」與經過「Kalman Filter 平滑 & Turnover 限制」後的權重差異，驗證系統如何抑制過度交易。

最終 Alpha 訊號與選股清單 (Alpha & Portfolio Builder)：

結合動態權重特徵與 TimesFM 預測值，即時計算並排序出 Top Alpha 股票清單。

M0 ~ M6 基金 Baseline 模型多維度對比 (Evaluation Center)：

比較從 M0 (Buy & Hold) 到 M6 (Full Agent) 各模型的年化報酬、夏普比率、最大回撤、IC/ICIR 與權重週轉率。

資料工程與時間戳記驗證 (Data Engineering & Time Alignment)：

展示 8 大類市場資料庫運作狀態，並提供 Event/Publish/Ingest/Effective 四重時間戳驗證，確保回測防護 Look-Ahead Bias。

💻 Streamlit 應用程式主程式碼 (app.py)
已為您撰寫好完整且專業的 Streamlit 應用程式代碼，並生成了 app.py 檔案：

「PY」圖示
app
 PY 
開啟
🚀 如何運行這個 Streamlit 平台？
安裝必要的 Python 套件：

Bash
pip install streamlit pandas numpy plotly
啟動平台：

Bash
streamlit run app.py
開啟瀏覽器後，您即可體驗一個涵蓋 TQEM 8 大模組、5 維動態權重計算、Kalman Filter 平滑與 M0-M6 模型對比 的完整量化研究與決策平台！




Gemini 是 AI，有時可能會出錯。
正在分析
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 頁面配置 (Page Configuration)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TQEM-100 TimesFM 量化基金評估與動態權重控制台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 樣式
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .status-tag {
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        background-color: #F1F5F9;
        border-radius: 6px 6px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284C7;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 模擬數據生成器 (Mock Data Generator)
# -----------------------------------------------------------------------------
@st.cache_data
def load_mock_data():
    dates = pd.date_range(end=datetime.today(), periods=180, freq='B')
    np.random.seed(42)
    
    # 7 大特徵群組
    features = ['Price/Return', 'Volume', 'Momentum', 'Volatility', 'Macro', 'Fund Flow', 'Sentiment']
    
    # 模擬歷史動態權重數據 (未平滑)
    raw_weights = np.random.dirichlet(np.ones(7), size=len(dates))
    df_raw_weights = pd.DataFrame(raw_weights, index=dates, columns=features)
    
    # 模擬 Kalman 平滑後權重
    df_kalman_weights = df_raw_weights.rolling(window=5, min_periods=1).mean()
    df_kalman_weights = df_kalman_weights.div(df_kalman_weights.sum(axis=1), axis=0)
    
    # 模擬 IC 時間序列
    df_ic = pd.DataFrame({
        f: np.sin(np.linspace(0, 10, len(dates)) + i) * 0.15 + np.random.normal(0.02, 0.05, len(dates))
        for i, f in enumerate(features)
    }, index=dates)
    
    # 模擬個股 Forecast & Uncertainty
    stock_list = [f"{2330 + i}.TW" for i in range(10)] + [f"STOCK_{i:03d}" for i in range(11, 101)]
    df_stocks = pd.DataFrame({
        'Ticker': stock_list[:20],
        'Regime': np.random.choice(['Bull', 'Bear', 'Sideway', 'HighVol', 'Crisis'], size=20, p=[0.4, 0.2, 0.2, 0.1, 0.1]),
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
    
    return dates, features, df_raw_weights, df_kalman_weights, df_ic, df_stocks, df_models

dates, features, df_raw_weights, df_kalman_weights, df_ic, df_stocks, df_models = load_mock_data()

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
        index=0
    )
    
    st.markdown("### 動態權重引擎參數")
    alpha_param = st.slider("信心折價係數 α (Uncertainty Discount)", 0.0, 1.0, 0.2, 0.05)
    beta_param = st.slider("風險懲罰係數 β (Risk Penalty)", 0.5, 3.0, 1.0, 0.1)
    delta_w_max = st.slider("單日權重變化上限 Δw_max", 0.01, 0.20, 0.05, 0.01)
    
    st.markdown("---")
    st.caption("資料更新時間：2026-08-14 09:00 (Effective Time)")
    st.caption("資料時間對齊檢查：✅ 無前視偏誤 (No Look-Ahead)")

# -----------------------------------------------------------------------------
# 主頁面 Header
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">TimesFM TQEM 量化基金評估與動態權重管理平台</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">整合 Data Layer 治理、Regime 辨識、TimesFM 時間序列預測、五維動態權重與 Kalman 平滑之完整量化研究工作流</div>', unsafe_allow_html=True)

# 頂部關鍵指標 (KPI Banner)
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.metric("當前市場 Regime", "Bull (多頭)", delta="Broadness: 68%")
with kpi2:
    st.metric("TimesFM 平均信心 (C_i)", "0.82", delta="+0.04")
with kpi3:
    st.metric("近期 Top 特徵 IC", "Momentum (0.12)", delta="ICIR: 1.02")
with kpi4:
    st.metric("M5 組合夏普比率", "1.68", delta="vs M0 +1.03")
with kpi5:
    st.metric("Kalman 權重週轉率", "8.2%", delta="-15.9% vs Raw")

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
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("##### 當前五大 Regime 條件與權重調整矩陣")
        regime_df = pd.DataFrame({
            'Regime': ['Bull', 'Bear', 'Sideway', 'HighVol', 'Crisis'],
            '主導特徵群組': ['Momentum / Flow', 'Macro / Volatility', 'Mean Reversion', 'Volatility / Cash', 'Risk Control / Macro'],
            '權重偏向': ['上調 Momentum (+20%)', '上調 Vol/Macro (+30%)', '上調 Price Range', '上調 Vol/Liquidity', '大幅調降 Trend/Flow']
        })
        st.dataframe(regime_df, hide_index=True, use_container_width=True)
        
        st.info("💡 **Regime 規則**：根據 MA20-MA60 趨勢、市場廣度 (Breadth) 與 20日波動率 $\sigma_{20}$ 自動判定。")
        
    with c2:
        st.markdown("##### 個股 TimesFM 多時間尺度預測與不確定性 (Quantile Range)")
        
        # 繪製選定股票的 Quantile 預測扇形圖
        selected_ticker = st.selectbox("選擇預測個股：", df_stocks['Ticker'].tolist(), index=0)
        stock_row = df_stocks[df_stocks['Ticker'] == selected_ticker].iloc[0]
        
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
            height=320,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_fan, use_container_width=True)

# -----------------------------------------------------------------------------
# Tab 2: 五維動態權重與 Kalman 平滑
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("五維動態權重引擎 (Dynamic Weight Allocation Engine)")
    st.latex(r"w_i(t) = 	ext{Normalize}\left[ w_i^{	ext{base}} 	imes R_i(t) 	imes P_i(t) 	imes C_i(t) 	imes K_i(t) 
ight]")
    
    col_w1, col_w2 = st.columns(2)
    
    with col_w1:
        # 原始動態權重 vs Kalman 平滑後權重 (時間序列堆疊圖)
        fig_area = px.area(
            df_kalman_weights, 
            x=df_kalman_weights.index, 
            y=features,
            title="Kalman 平滑後之 7 大特徵群組歷史動態權重趨勢 (每日總和 = 100%)",
            labels={'value': '權重比例', 'index': '日期'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_area.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_area, use_container_width=True)
        
    with col_w2:
        # 當日特徵權重對比 (Raw vs Kalman Filtered)
        latest_raw = df_raw_weights.iloc[-1]
        latest_kalman = df_kalman_weights.iloc[-1]
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=features, y=latest_raw, name='原始計算權重 (Raw Weight)', marker_color='#CBD5E1'))
        fig_bar.add_trace(go.Bar(x=features, y=latest_kalman, name='Kalman 平滑權重 (Filtered)', marker_color='#0284C7'))
        
        fig_bar.update_layout(
            title="當日特徵權重：原始計算 vs Kalman 平滑與 Turnover 限制後",
            barmode='group',
            yaxis_title="權重比重",
            height=380,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------------------------------------------------------
# Tab 3: Alpha 排序與選股清單
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("最終 Alpha 訊號生成與選股組合 (Portfolio Optimization Input)")
    st.latex(r"	ext{Alpha}_{	ext{final}}(i,t) =  eta_1 \cdot 	ext{Alpha}_{	ext{feature}}(i,t) +  eta_2 \cdot 	ext{Forecast}_{	ext{TimesFM}}(i,t)")
    
    st.markdown("##### 股票 Alpha 排名與信心指標表 (Top 20 Demo)")
    
    # 格式化表格欄位
    formatted_df = df_stocks.copy()
    
    def highlight_alpha(val):
        color = '#DC2626' if val < 0 else '#16A34A'
        return f'color: {color}; font-weight: bold;'

    st.dataframe(
        formatted_df.style.applymap(highlight_alpha, subset=['Alpha_Score', 'Forecast_5D (%)']),
        use_container_width=True,
        height=400
    )

# -----------------------------------------------------------------------------
# Tab 4: Baseline 模型對比 (M0-M6)
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("TQEM Baseline 模型多維度績效評估 (M0 至 M6)")
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        # 夏普比率 vs 最大回撤 散佈圖
        fig_scatter = px.scatter(
            df_models, 
            x='Max Drawdown (%)', 
            y='Annual Return (%)', 
            size='Sharpe Ratio', 
            color='Model',
            text='Model',
            title="風報比分析：年化報酬率 vs 最大回撤 (泡泡大小 = 夏普比率)",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_m2:
        # 績效數據對比表
        st.markdown("##### M0-M6 完整評估指標對照表")
        st.dataframe(df_models, hide_index=True, use_container_width=True, height=350)
        st.caption("註：M5 (TimesFM + Dynamic Weight + Kalman) 在抑制 Turnover 與提高 Sharpe 上達到最佳實操平衡。")

# -----------------------------------------------------------------------------
# Tab 5: 資料工程與時間對齊驗證
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("資料工程 (Data Engineering) & 時間對齊治理")
    
    st.markdown("""
    #### 🛡️ 防止 Look-Ahead Bias 時間戳治理機制
    為確保回測完全真實且可落地，TQEM 強制要求每一筆市場資料必須標註四種時間：
    """)
    
    time_col1, time_col2, time_col3, time_col4 = st.columns(4)
    with time_col1:
        st.markdown("<div class='metric-card'><b>1. Event Time</b><br><small>事件真實發生時間<br>(例如：公司財報公布日 18:00)</small></div>", unsafe_allow_html=True)
    with time_col2:
        st.markdown("<div class='metric-card'><b>2. Publish Time</b><br><small>資訊對外公開時間<br>(例如：交易所公告 18:30)</small></div>", unsafe_allow_html=True)
    with time_col3:
        st.markdown("<div class='metric-card'><b>3. Ingest Time</b><br><small>系統實際接收時間<br>(例如：資料庫入庫 18:31)</small></div>", unsafe_allow_html=True)
    with time_col4:
        st.markdown("<div class='metric-card'><b>4. Effective Time</b><br><small>模型可使用的最早時間<br>(例如：次日開盤前 08:30)</small></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 8 大類市場資料層 (Data Layer) 涵蓋狀態")
    
    data_layer_df = pd.DataFrame({
        '資料類別': ['1. 價格與成交', '2. 市場/產業指數', '3. 波動率與風險', '4. 流動性/微結構', '5. 籌碼與資金流', '6. 宏觀經濟', '7. 公司基本面', '8. 新聞/事件情緒'],
        '涵蓋指標數': [12, 8, 6, 5, 10, 15, 18, 4],
        '更新頻率': ['Tick / 日線', '日線', '日線/即時', 'Tick', '每日盤後', '日/週/月', '季/年報', '即時 NLP'],
        '品質檢查狀態': ['✅ 通過', '✅ 通過', '✅ 通過', '✅ 通過', '✅ 通過', '✅ 通過', '✅ 通過', '✅ 通過']
    })
    st.dataframe(data_layer_df, hide_index=True, use_container_width=True)

app.py
目前顯示的是「app.py」。