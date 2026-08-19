import streamlit as st
import yfinance as yf
from pvcs_engine import compute_pvcs, rule_engine

st.set_page_config(page_title="PVCS 台股三維分析網", layout="wide")

st.title("PVCS 台股價 × 量 × 籌碼三維分析")
st.caption("盤後研究版 | 依據個股資料自動計算三維分數與狀態預警")

# 側邊欄設定
st.sidebar.header("分析設定")
ticker_input = st.sidebar.text_input("股票代碼 (台股請加 .TW)", value="2330.TW")
history_days = st.sidebar.selectbox("資料回溯期間", ["約 400 日", "約 200 日"])

if st.sidebar.button("開始分析", type="primary"):
    with st.spinner("讀取市場資料並計算 PVCS..."):
        # 抓取資料
        df = yf.download(ticker_input, period="2y")

        if df.empty:
            st.error("找不到該股票資料，請確認代碼（例如 2330.TW 或 2603.TW）")
        else:
            # 處理 MultiIndex 欄位 (yfinance 特性)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # 計算 PVCS
            res = compute_pvcs(df)
            latest = res.iloc[-1]

            status, msg = rule_engine(
                latest["PScore"],
                latest["VScore"],
                latest["CScore"],
                latest["PVCS"],
            )

            # --- UI 呈現 ---
            st.success("分析完成！")

            # 區塊 A：核心 Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("PVCS 綜合分數", f"{latest['PVCS']:.1f} / 100")
            col2.metric("決策信心度", f"{latest['Confidence']:.0f}%")
            col3.metric("當前市場狀態", status)
            col4.metric("最新收盤價", f"{latest['Close']:.1f}")

            st.info(f"**狀態判讀：** {msg}")

            # 區塊 B：三維分數拆解
            st.subheader("三維結構拆解 (Price × Volume × Chip)")
            c1, c2, c3 = st.columns(3)
            c1.metric(
                "Price Score (價格)",
                f"{latest['PScore']:.1f}",
                help="權重 35%",
            )
            c2.metric(
                "Volume Score (量能)",
                f"{latest['VScore']:.1f}",
                help="權重 25%",
            )
            c3.metric(
                "Chip Score (籌碼)",
                f"{latest['CScore']:.1f}",
                help="權重 40%",
            )

            # 歷史 K 線與 PVCS 趨勢圖
            st.subheader("近期 PVCS 走勢圖")
            st.line_chart(res[["Close", "PVCS"]].tail(100))