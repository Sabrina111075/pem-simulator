import pandas as pd
import streamlit as st
import yfinance as yf
from pvcs_engine import compute_multi_horizon_pvcs, rule_engine

st.set_page_config(page_title="PVCS 台股三維分析網", layout="wide")

st.title("PVCS 台股價 × 量 × 籌碼三維分析")
st.caption("盤後研究版 | 依據個股資料自動計算三維分數與狀態預警")

# 側邊欄設定
st.sidebar.header("分析設定")
ticker_input = st.sidebar.text_input("股票代碼 (台股請加 .TW)", value="2330.TW")
history_days = st.sidebar.selectbox("資料回溯期間", ["約 400 日", "約 200 日"])

if st.sidebar.button("開始分析", type="primary"):
    with st.spinner("讀取市場資料並進行多時間尺度與個股權重校準..."):
        # 抓取資料
        df = yf.download(ticker_input, period="2y")

        if df.empty:
            st.error("找不到該股票資料，請確認代碼（例如 2330.TW 或 2603.TW）")
        else:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # 計算多時間尺度與個股校準權重
            res, weights = compute_multi_horizon_pvcs(df)
            latest = res.iloc[-1]

            status, msg = rule_engine(
                latest["PScore"],
                latest["VScore"],
                latest["CScore"],
                latest["PVCS_20D"],
            )

            st.success("分析完成！個股專屬動態權重校準完畢。")

            # --- 區塊 A：核心 Metrics ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(
                "20D PVCS (主波段)",
                f"{latest['PVCS_20D']:.1f} / 100",
            )
            col2.metric("決策信心度", f"{latest['Confidence']:.0f}%")
            col3.metric("當前市場狀態", status)
            col4.metric("最新收盤價", f"{latest['Close']:.1f}")

            st.info(f"**狀態判讀：** {msg}")

            # --- 區塊 B：多時間尺度 PVCS 矩陣 ---
            st.subheader("多時間尺度分析 (Multi-Horizon Matrix)")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("5D (短線衝刺)", f"{latest['PVCS_5D']:.1f}")
            m2.metric(
                "20D (主要波段)",
                f"{latest['PVCS_20D']:.1f}",
                delta="主研究尺度",
            )
            m3.metric("60D (中線結構)", f"{latest['PVCS_60D']:.1f}")
            m4.metric(
                "Composite 綜合分數",
                f"{latest['PVCS_Composite']:.1f}",
            )

            st.markdown("---")

            # --- 區塊 C：個股 20D 主尺度動態權重拆解 ---
            st.subheader(
                "20D 主尺度個股校準權重 (Stock-Specific Weights)"
            )
            w_20 = weights["20D"]

            c1, c2, c3 = st.columns(3)
            c1.metric(
                "Price 權重",
                f"{w_20['w_p']*100:.1f}%",
                f"IC: {w_20['ic']['P']:.3f}",
            )
            c2.metric(
                "Volume 權重",
                f"{w_20['w_v']*100:.1f}%",
                f"IC: {w_20['ic']['V']:.3f}",
            )
            c3.metric(
                "Chip 權重",
                f"{w_20['w_c']*100:.1f}%",
                f"IC: {w_20['ic']['C']:.3f}",
            )

            st.caption("價 / 量 / 籌碼 動態權重分配占比：")
            st.progress(float(w_20["w_p"]))

            # --- 歷史 K 線與 PVCS 走勢圖 ---
            st.subheader("近期 PVCS 與股價走勢圖")
            st.line_chart(res[["Close", "PVCS_20D"]].tail(100))