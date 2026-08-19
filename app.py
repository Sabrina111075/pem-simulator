import pandas as pd
import streamlit as st
import yfinance as yf
from pvcs_engine import compute_multi_horizon_pvcs, rule_engine

st.set_page_config(
    page_title="PVCS 台股三維分析網", layout="wide", initial_sidebar_state="expanded"
)

st.title("PVCS 台股價 × 量 × 籌碼三維分析")
st.caption("盤後研究版 v0.2 | 個股自適應動態權重與多時間尺度 (5D/20D/60D) 預測系統")

# 側邊欄
st.sidebar.header("分析設定")
ticker_input = st.sidebar.text_input("股票代碼 (台股請加 .TW)", value="2330.TW")
history_period = st.sidebar.selectbox("歷史回溯範圍", ["2y", "1y", "5y"], index=0)

if st.sidebar.button("開始分析", type="primary"):
    with st.spinner(f"正在分析 {ticker_input} 並進行個股權重校準..."):
        df = yf.download(ticker_input, period=history_period)

        if df.empty:
            st.error("找不到該股票資料，請確認代碼（例如 2330.TW 或 2603.TW）")
        else:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # 計算多時間尺度與權重
            res, weights = compute_multi_horizon_pvcs(df)
            latest = res.iloc[-1]

            diag = rule_engine(
                latest["PScore"],
                latest["VScore"],
                latest["CScore"],
                latest["PVCS_20D"],
            )

            st.success(f"【{ticker_input}】分析完成！個股專屬 IC/ICIR 校準成功。")

            # === 區塊 1：當前總覽卡片 ===
            st.markdown("### 1. 核心綜合診斷 (Executive Summary)")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("20D PVCS (主要波段)", f"{latest['PVCS_20D']:.1f} / 100")
            col2.metric("決策信心度", f"{latest['Confidence']:.0f}%")
            col3.metric("當前市場狀態", diag["status"])
            col4.metric("背離預警風險", diag["divergence"], delta=f"風險等級: {diag['risk']}")

            st.info(f"**診斷解讀：** {diag['msg']}")

            # === 區塊 2：多時間尺度矩陣 ===
            st.markdown("### 2. 多時間尺度矩陣 (Multi-Horizon Analysis)")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("5D 短線衝刺", f"{latest['PVCS_5D']:.1f}")
            m2.metric("20D 主要波段", f"{latest['PVCS_20D']:.1f}", help="模型核心參考尺度")
            m3.metric("60D 中線趨勢", f"{latest['PVCS_60D']:.1f}")
            m4.metric("Composite 綜合分數", f"{latest['PVCS_Composite']:.1f}")

            st.markdown("---")

            # === 區塊 3：個股專屬 20D 動態權重 ===
            st.markdown("### 3. 個股專屬動態權重分配 (252D IC/ICIR 校準)")
            w_20 = weights["20D"]

            c1, c2, c3 = st.columns(3)
            c1.metric(
                "Price 價格權重",
                f"{w_20['w_p']*100:.1f}%",
                f"IC: {w_20['ic']['P']:.3f}",
                help="反映價格動能強度",
            )
            c2.metric(
                "Volume 量能權重",
                f"{w_20['w_v']*100:.1f}%",
                f"IC: {w_20['ic']['V']:.3f}",
                help="反映成交量推升力道",
            )
            c3.metric(
                "Chip 籌碼權重",
                f"{w_20['w_c']*100:.1f}%",
                f"IC: {w_20['ic']['C']:.3f}",
                help="反映主力/籌碼集中的影響力",
            )

            # 視覺化權重比重
            st.write("**P / V / C 權重占比圖：**")
            w_df = pd.DataFrame(
                {
                    "維度": ["Price (價)", "Volume (量)", "Chip (籌碼)"],
                    "權重占比 (%)": [
                        w_20["w_p"] * 100,
                        w_20["w_v"] * 100,
                        w_20["w_c"] * 100,
                    ],
                }
            ).set_index("維度")
            st.bar_chart(w_df)

            # === 區塊 4：歷史走勢與 PVCS 軌跡 ===
            st.markdown("### 4. 近 100 日 PVCS 與股價走勢對照")
            chart_data = res[["Close", "PVCS_20D", "PVCS_5D"]].tail(100)
            st.line_chart(chart_data)