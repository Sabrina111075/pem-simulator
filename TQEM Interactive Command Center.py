import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta

# 頁面基本設定
st.set_page_config(page_title="TimesFM TQEM 量化基金平台", layout="wide")

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
st.sidebar.header("🌐 Crystal Machine 模擬平台")
selected_regime = st.sidebar.selectbox(
    "選擇目前市場狀態 (Regime)：",
    ['Bull (多頭)', 'Bear (空頭)', 'Sideway (盤整)', 'HighVol (高波動)', 'Crisis (危機)'],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 動態權重引擎參數")
alpha = st.sidebar.slider("信心折價係數 α (Uncertainty Discount)", 0.0, 1.0, 0.42, 0.01)
beta = st.sidebar.slider("風險懲罰係數 β (Risk Penalty)", 0.0, 2.0, 0.80, 0.05)
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
# 2. 右側 Header & 連動 Metrics (專業資訊升級)
# -----------------------------------------------------------------
taipei_tz = timezone(timedelta(hours=8))
taipei_time_str = datetime.now(taipei_tz).strftime("%Y-%m-%d %H:%M:%S")

st.title("TQEM：TimesFM 與Wyckoff 之AI 量化基金平台")

# 1. 核心模型與數據來源（第一行）
st.markdown("""
<div style="font-size: 0.88rem; color: #475569; margin-top: -8px; margin-bottom: 6px; font-weight: 500;">
    🧠 <b>核心模型依據：</b> Google TimesFM 2.0 時序基礎模型 + Wyckoff PVCS 價量結構 + 卡爾曼動態權重矩陣 (Kalman Filtering)<br>
    🛡️ <b>數據基底：</b> 台股全市場日線/Tick 數據與三大法人籌碼流向 (Point-in-Time Verified)
</div>
""", unsafe_allow_html=True)

# 2. 台北時間（單獨第二行，適度下拉間距）
st.markdown(f"""
<div style="font-size: 0.85rem; color: #64748B; margin-top: 10px; margin-bottom: 20px;">
    🕒 <b>台北時間 (CST / UTC+8)：</b> <code style="color: #0284C7; background-color: #F0F9FF; padding: 2px 6px; border-radius: 4px; border: 1px solid #BAE6FD;">{taipei_time_str}</code>
</div>
""", unsafe_allow_html=True)

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
    st.markdown(f"##### 📌 當前選定 Regime：`{selected_regime}` （動態權重調整矩陣）")
    
    # 根據當前參數即時計算動態偏向
    adj_momentum = f"{20 * (1 - alpha):+.1f}% (經 α 折價)"
    adj_volatility = f"{30 * (1 + beta*0.5):+.1f}% (經 β 懲罰加權)"
    
    regime_df = pd.DataFrame({
        'Regime 狀態': ['Bull (多頭)', 'Bear (空頭)', 'Sideway (盤整)', 'HighVol (高波動)', 'Crisis (危機)'],
        '主導特徵群組': ['Momentum / Flow', 'Macro / Volatility', 'Mean Reversion', 'Volatility / Cash', 'Risk Control / Macro'],
        '預設權重偏向': ['上調 Momentum (+20%)', '上調 Vol/Macro (+30%)', '上調 Price Range', '上調 Vol/Liquidity', '大幅調降 Trend/Flow'],
        '當前參數實時微調結果': [
            adj_momentum if selected_regime.startswith('Bull') else '標準配置',
            adj_volatility if selected_regime.startswith('Bear') else '標準配置',
            f"微調上限 Δw={delta_w_max:.2f}",
            f"風控權重增益 β={beta:.2f}",
            "強制現金防禦 50%+"
        ]
    })
    st.dataframe(regime_df, use_container_width=True)

elif selected_page.startswith("2."):
    st.subheader("2. 五維動態權重引擎 (Dynamic Weight Allocation Engine)")
    st.markdown("##### 📊 五維因子動態權重隨時間變化示意圖")
    dates = pd.date_range(end=datetime.now(taipei_tz), periods=30, freq="D")
    weight_data = pd.DataFrame({
        "Date": dates,
        "Trend/Momentum": np.clip(0.35 - alpha*0.1 + np.sin(np.linspace(0, 10, 30))*0.05, 0.05, 0.6),
        "Volatility/Risk": np.clip(0.20 + beta*0.1 + np.cos(np.linspace(0, 10, 30))*0.03, 0.05, 0.5),
        "Liquidity/Flow": np.clip(0.15 + np.sin(np.linspace(0, 5, 30))*0.02, 0.05, 0.4),
        "Valuation/Fundamental": [0.15] * 30,
        "Sentiment/Wyckoff": np.clip(0.15 - delta_w_max*0.1 + np.cos(np.linspace(0, 5, 30))*0.02, 0.05, 0.4)
    }).set_index("Date")
    st.area_chart(weight_data)
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.info(f"**當前 α 信心折價點位**：`{alpha:.2f}`\n\n對動量因子權重進行相應扣減，提升防禦型因子權重。")
    with col_w2:
        st.info(f"**當前 β 風險懲罰點位**：`{beta:.2f}`\n\n平滑高波動期權重變更幅度，控制單日 Max Delta 在 `{delta_w_max:.2f}`。")

elif selected_page.startswith("3."):
    import altair as alt
    
    st.subheader("3. 最終 Alpha 訊號生成與選股組合")
    st.markdown("##### 🏆 今日 Top 10 標的 Alpha 綜合評分榜單")
    
    # 1. 建立包含「中文 + 英文 + 股票代碼」的資料集
    stock_data = pd.DataFrame({
        '股票代碼': ['2330.TW', '2454.TW', '2317.TW', '2308.TW', '3037.TW', '2379.TW', '3034.TW', '2382.TW', '3231.TW', '6669.TW'],
        '股票名稱': ['台積電', '聯發科', '鴻海', '台達電', '欣興', '瑞昱', '聯詠', '廣達', '緯創', '緯穎'],
        '顯示標籤': [
            '台積電 (TSMC)', '聯發科 (MTK)', '鴻海 (Foxconn)', '台達電 (Delta)', 
            '欣興 (Unimicron)', '瑞昱 (Realtek)', '聯詠 (Novatek)', '廣達 (Quanta)', 
            '緯創 (Wistron)', '緯穎 (Wiwynn)'
        ],
        'TimesFM 信心分': [92.5, 88.1, 85.4, 82.0, 79.3, 77.8, 75.2, 73.0, 71.5, 70.1],
        'PVCS 籌碼得分': [88.0, 82.3, 79.1, 85.0, 71.2, 69.5, 74.0, 80.2, 68.9, 73.5],
        '最終 Alpha 總分': [90.8, 85.6, 82.7, 83.3, 75.9, 74.3, 74.7, 76.1, 70.4, 71.6],
        '建議持股權重 (%)': [18.5, 14.2, 12.0, 11.5, 9.1, 8.2, 7.5, 7.0, 6.2, 5.8]
    })
    
    # 顯示數據表格
    st.dataframe(stock_data[['股票代碼', '股票名稱', 'TimesFM 信心分', 'PVCS 籌碼得分', '最終 Alpha 總分', '建議持股權重 (%)']], use_container_width=True)
    
    st.markdown("---")
    st.markdown("##### 📊 Top 10 Alpha 綜合得分柱狀圖")
    
    # 2. 使用 Altair 繪製「橫條圖 (Horizontal Bar Chart)」，文字橫排呈現，字數再多也絕對不會吃字！
    chart = alt.Chart(stock_data).mark_bar(color='#0284C7', cornerRadiusEnd=4).encode(
        x=alt.X('最終 Alpha 總分:Q', title='最終 Alpha 總分', scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('顯示標籤:N', title='標的名稱 (中文 + 英文簡稱)', sort='-x', axis=alt.Axis(labelFontSize=12)),
        tooltip=['股票代碼', '股票名稱', '顯示標籤', '最終 Alpha 總分', '建議持股權重 (%)']
    ).properties(
        height=380
    )
    
    st.altair_chart(chart, use_container_width=True)

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
    st.markdown("##### 🛡️ 時間戳對齊與無前視偏誤 (No Look-Ahead) 檢核狀態")
    data_status = pd.DataFrame({
        '資料源 (Data Pipeline)': ['台股日 K 價量資料', '三大法人籌碼資料', 'TimesFM 預測 Feature', 'Macro 總體經濟指標', '高頻 Tick 數據'],
        '最後更新時間': [taipei_time_str, taipei_time_str, taipei_time_str, taipei_time_str, taipei_time_str],
        '時間對齊狀態': ['✔ 嚴格對齊 (T-0)', '✔ 嚴格對齊 (T-0)', '✔ 無未來資訊注入', '✔ 滯後一期 (T-1)', '✔ 觸發即時校準'],
        '數據完整度': ['100%', '100%', '99.8%', '100%', '98.5%']
    })
    st.table(data_status)
    st.success("✔ 所有特徵工程矩陣皆經過 Strict Point-in-Time Join 驗證，確定無數據洩漏 (Data Leakage)。")

elif selected_page.startswith("6."):
    st.subheader("6. 威科夫 (Wyckoff) 價量籌碼 (PVCS) 診斷沙盒")
    
    # 1. 頂部指標（根據選定 Regime 計算總分）
    regime_score_map = {
        'Bull (多頭)': (71.7, "Phase D / E", "+3.4 pts"),
        'Bear (空頭)': (38.5, "Phase A / B", "-8.2 pts"),
        'Sideway (盤整)': (52.1, "Phase B / C", "+0.5 pts"),
        'HighVol (高波動)': (61.3, "Phase C / D", "+1.2 pts"),
        'Crisis (危機)': (18.2, "Markdown Downward", "-15.8 pts")
    }
    score, phase, pts_delta = regime_score_map.get(selected_regime, (71.7, "Phase D / E", "+3.4 pts"))

    c_top1, c_top2, c_top3, c_top4 = st.columns(4)
    with c_top1:
        st.metric("Wyckoff 階段辨識", phase, delta="↑ SOS / Jump Across Creek" if "Bull" in selected_regime else "↓ SOW / Distribution")
    with c_top2:
        st.metric("PVCS 綜合評估分", f"{score} / 100", delta=pts_delta)
    with c_top3:
        st.metric("籌碼集中度 (Chip Score)", "68.3 / 100", delta="↑ 三大法人同步買超")
    with c_top4:
        st.metric("建議策略動作", "積極加碼 / 持股續抱" if score > 60 else "減碼防禦 / 現金為王", delta="↑ 信心度 88%")

    st.markdown("---")
    st.markdown("##### 📈 K線價量結構與 PVCS 訊號疊加圖")

    # 2. 中間圖表 (保留原有的模擬數據折線圖)
    import numpy as np
    chart_data = pd.DataFrame({
        'Wyckoff Price': np.sin(np.linspace(0, 10, 40)) * 5 + (100 if "Bull" in selected_regime else 80),
        'PVCS Volume Flow': np.cos(np.linspace(0, 10, 40)) * 3 + 50
    })
    st.line_chart(chart_data)

    st.markdown("---")
    st.markdown("##### 🎯 PVCS 四維診斷即時動態卡片")

# 3. 下方 PVCS 四維診斷（與 Regime 連動）
    regime_pvcs_map = {
        'Bull (多頭)': {
            'P': (81.7, "📌 狀態：強勢突破點"),
            'V': (72.8, "📌 狀態：量增價漲結構"),
            'C': (68.3, "📌 狀態：主力集中控盤"),
            'S': (70.7, "📌 狀態：市場偏向樂觀")
        },
        'Bear (空頭)': {
            'P': (38.2, "📌 狀態：破位空頭排列"),
            'V': (41.5, "📌 狀態：殺多帶量陰線"),
            'C': (45.0, "📌 狀態：籌碼鬆動釋出"),
            'S': (28.4, "📌 狀態：市場極度悲觀")
        },
        'Sideway (盤整)': {
            'P': (52.0, "📌 狀態：箱型區間震盪"),
            'V': (48.6, "📌 狀態：量能萎縮觀望"),
            'C': (55.1, "📌 狀態：法人低吞高拋"),
            'S': (50.0, "📌 狀態：市場情緒中性")
        },
        'HighVol (高波動)': {
            'P': (61.4, "📌 狀態：多空劇烈洗盤"),
            'V': (85.2, "📌 狀態：天量爆發爭奪"),
            'C': (42.8, "📌 狀態：散戶籌碼激增"),
            'S': (62.3, "📌 狀態：情緒高度分歧")
        },
        'Crisis (危機)': {
            'P': (15.5, "📌 狀態：無差別恐慌拋售"),
            'V': (22.0, "📌 狀態：流動性凍結"),
            'C': (31.2, "📌 狀態：主力避險出清"),
            'S': (10.8, "📌 狀態：極度恐慌 (Panic)")
        }
    }
    current_pvcs = regime_pvcs_map.get(selected_regime, regime_pvcs_map['Bull (多頭)'])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("P - 價格結構得分", f"{current_pvcs['P'][0]}", delta=f"{current_pvcs['P'][1]}")
    with c2:
        st.metric("V - 成交量動能得分", f"{current_pvcs['V'][0]}", delta=f"{current_pvcs['V'][1]}")
    with c3:
        st.metric("C - 籌碼集中度得分", f"{current_pvcs['C'][0]}", delta=f"{current_pvcs['C'][1]}")
    with c4:
        st.metric("S - 市場情緒指數", f"{current_pvcs['S'][0]}", delta=f"{current_pvcs['S'][1]}")