# -*- coding: utf-8 -*-
"""
app.py
TimesFM TQEM 量化基金評估與動態權重管理平台 (Streamlit Command Center)
已整合 Wyckoff & PVCS 價量籌碼診斷模組
"""

import streamlit as st
import pandas as pd
import numpy as np

# 安全載入 Wyckoff Engine 模組（避免模組未找到時崩潰）
try:
    from wyckoff_pvcs_engine import WyckoffPVCSEngine, render_wyckoff_tab
    WYCKOFF_AVAILABLE = True
except ImportError:
    WYCKOFF_AVAILABLE = False

# 1. 頁面組態設定
st.set_page_config(
    page_title="TimesFM TQEM 量化基金評估與動態權重管理平台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 側邊欄控制面板 (Sidebar Controls)
st.sidebar.title("TQEM 控制台面板")
st.sidebar.caption("TimesFM Quant Evaluation Model v1.0")

st.sidebar.subheader("當前市場狀態 (Market Regime)")
market_regime = st.sidebar.selectbox(
    "選擇 Regime",
    ["Crisis (危機)", "Bear (熊市)", "Sideways (盤整)", "Bull (牛市)"],
    index=0
)

st.sidebar.subheader("動態權重引擎參數")
alpha_discount = st.sidebar.slider("信心折價係數 α (Uncertainty Discount)", 0.0, 1.0, 0.85, 0.01)
beta_penalty = st.sidebar.slider("風險懲罰係數 β (Risk Penalty)", 0.5, 5.0, 2.00, 0.05)
dw_max = st.sidebar.slider("單日權重變化上限 Δw_max", 0.01, 0.50, 0.13, 0.01)

# 3. 主標題與頂部 KPI 儀表卡片
st.title("TimesFM TQEM 量化基金評估與動態權重管理平台")
st.caption("整合 Data Layer 治理、Regime 辨識、TimesFM 時間序列預測、五維動態權重與 Kalman 平滑之完整量化研究工作流")
st.info("🕒 台北時間 (TST) : 2026-08-18 11:21:40")

# 頂部 5 大指標卡片
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
with kpi_col1:
    st.metric("當前市場 Regime", market_regime.split()[0], "Broadness: 15%", delta_color="inverse")
with kpi_col2:
    st.metric("TimesFM 平均信心", "0.39", f"↑ α = {alpha_discount}")
with kpi_col3:
    st.metric("近期 Top 特徵 IC", "Tail-Risk (0...)", "↑ 客觀特徵 (不受風控參...)")
with kpi_col4:
    st.metric("M5 組合夏普比率", "0.47", "↑ 訊號追蹤 (Δw=0.13)")
with kpi_col5:
    st.metric("Kalman 權重週轉率", "90.9%", "↑ 調倉天花板 (Δw=0.13)")

st.divider()

# 4. 主分頁控制 (6 個 Tab)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 1. 市場狀態與 TimesFM 預測",
    "⚙️ 2. 五維動態權重與 Kalman 平滑",
    "🎯 3. Alpha 排序與選股清單",
    "📈 4. Baseline 模型對比 (M0-M6)",
    "🛡️ 5. 資料工程與時間對齊驗證",
    "🏛️ 6. 威科夫 (Wyckoff) 價量籌碼 (PVCS) 診斷"  # 新增的第 6 頁
])

# Tab 1 ~ 5 原有內容維護
with tab1:
    st.subheader("1. 市場狀態辨識與 TimesFM 序列預測")
    st.write("TimesFM 預測模型當前處於 High Uncertainty 區域，自動啟用平滑保護機制。")
    # 模擬簡單 K 線與 TimesFM 預測趨勢
    chart_df = pd.DataFrame({
        'Actual': np.sin(np.linspace(0, 10, 50)) + 10,
        'TimesFM Forecast': np.sin(np.linspace(0, 10, 50)) + 10.2
    })
    st.line_chart(chart_df)

with tab2:
    st.subheader("2. 五維動態權重重興與 Kalman 平滑矩陣")
    st.json({
        "Uncertainty_Discount_Alpha": alpha_discount,
        "Risk_Penalty_Beta": beta_penalty,
        "Max_Daily_Weight_Delta": dw_max,
        "Kalman_Gain": 0.142,
        "Smoothed_Weight_Vector": [0.25, 0.15, 0.30, 0.10, 0.20]
    })

with tab3:
    st.subheader("3. Alpha 排序與選股清單 (Ranked Stock Universe)")
    stock_data = pd.DataFrame({
        'Ticker': ['2330.TW (台積電)', '2317.TW (鴻海)', '2454.TW (聯發科)', '2382.TW (廣達)', '3231.TW (緯創)'],
        'TimesFM Score': [0.89, 0.76, 0.82, 0.65, 0.58],
        'Regime Adaptive Vol': ['Low', 'Medium', 'Low', 'High', 'High'],
        'Recommended Weight': ['28.5%', '18.2%', '22.1%', '14.0%', '17.2%']
    })
    st.dataframe(stock_data, use_container_width=True)

with tab4:
    st.subheader("4. Baseline 模型對比 (M0-M6)")
    st.info("M5 (TQEM + Kalman) 在當前 Crisis Regime 下的夏普比率 (0.47) 顯著優於 M0 Baseline (-0.12)。")

with tab5:
    st.subheader("5. 資料工程 (Data Engineering) & 時間對齊治理")
    st.markdown("#### 🛡️ 防止 Look-Ahead Bias 時間截治機制")
    
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        st.success("1. Event Time\n事件發生時間")
    with col_t2:
        st.info("2. Publish Time\n資訊公開時間")
    with col_t3:
        st.warning("3. Ingest Time\n系統接收時間")
    with col_t4:
        st.error("4. Effective Time\n可使用最早時間")

# Tab 6: 威科夫 & PVCS 診斷沙盒 (Safe Execution Container)
with tab6:
    if WYCKOFF_AVAILABLE:
        try:
            render_wyckoff_tab(st)
        except Exception as e:
            st.error(f"❌ 渲染 Wyckoff PVCS 模組時發生異常: {str(e)}")
            st.caption("請檢查 wyckoff_pvcs_engine.py 檔案內容是否完整。")
    else:
        st.error("⚠️ 未能載入 `wyckoff_pvcs_engine.py` 模組！")
        st.info("請確認 `wyckoff_pvcs_engine.py` 檔案已正確放置於 Streamlit 專案根目錄中。")