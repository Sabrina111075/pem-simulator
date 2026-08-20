import pandas as pd
import streamlit as st
import yfinance as yf
from pvcs_engine import compute_multi_horizon_pvcs, rule_engine

st.set_page_config(
    page_title="PVCS 台股三維分析網",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("PVCS 台股價 × 量 × 籌碼三維分析")
st.caption(
    "盤後研究版 | 基於 5D / 20D / 60D 多時間尺度與個股專屬動態權重分析"
)

# === 側邊欄：進階股票選擇機制 ===
st.sidebar.header("分析設定")

stock_dict = {
    "2330.TW (台積電)": "2330.TW",
    "2317.TW (鴻海)": "2317.TW",
    "2454.TW (聯發科)": "2454.TW",
    "2603.TW (長榮)": "2603.TW",
    "3231.TW (緯創)": "3231.TW",
    "2382.TW (廣達)": "2382.TW",
    "00878.TW (國泰永續高股息)": "00878.TW",
    "0050.TW (元大台灣50)": "0050.TW",
    "自訂輸入代碼": "CUSTOM",
}

selected_option = st.sidebar.selectbox(
    "選擇熱門個股/ETF 或自訂", list(stock_dict.keys())
)

if stock_dict[selected_option] == "CUSTOM":
    user_input = st.sidebar.text_input(
        "輸入股票或 ETF 代碼（例如 00878 或 2330）", value="8446"
    )
    raw_ticker = user_input.strip().upper()

    if raw_ticker and not (
        raw_ticker.endswith(".TW") or raw_ticker.endswith(".TWO")
    ):
        ticker_input = f"{raw_ticker}.TW"
    else:
        ticker_input = raw_ticker
else:
    ticker_input = stock_dict[selected_option]

if st.sidebar.button("開始分析", type="primary"):
    if not ticker_input:
        st.error("請輸入有效的股票代碼！")
    else:
        with st.spinner(
            f"正在抓取 {ticker_input} 並計算 P/V/C 與 5D/20D/60D 權重..."
        ):
            df = yf.download(ticker_input, period="2y")

            if df.empty and ticker_input.endswith(".TW"):
                alt_ticker = ticker_input.replace(".TW", ".TWO")
                df = yf.download(alt_ticker, period="2y")
                if not df.empty:
                    ticker_input = alt_ticker

            if df.empty or len(df) < 60:
                st.error(
                    f"找不到代碼 【{ticker_input}】 的歷史資料，請確認代碼是否正確。"
                )
            else:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                # 執行 PVCS 運算
                res, weights = compute_multi_horizon_pvcs(df)
                latest = res.iloc[-1]
                prev = res.iloc[-2]

                diag = rule_engine(
                    latest["PScore"],
                    latest["VScore"],
                    latest["CScore"],
                    latest["PVCS_20D"],
                )

                st.success(f"【{ticker_input}】量化三維分析完成！")

                # === 區塊 1：三維核心指標 (Price / Volume / Chip) ===
                st.markdown("### 1. P/V/C 三維獨立因子得分 (最新數據)")
                c1, c2, c3, c4 = st.columns(4)

                p_delta = latest["PScore"] - prev["PScore"]
                v_delta = latest["VScore"] - prev["VScore"]
                c_delta = latest["CScore"] - prev["CScore"]

                c1.metric(
                    "Price (價動量得分)",
                    f"{latest['PScore']:.1f}",
                    delta=f"{p_delta:+.1f}",
                    help="評估趨勢強度與均線乖離",
                )
                c2.metric(
                    "Volume (量能強度得分)",
                    f"{latest['VScore']:.1f}",
                    delta=f"{v_delta:+.1f}",
                    help="評估相對成交量與價量配合度",
                )
                c3.metric(
                    "Chip (籌碼動向得分)",
                    f"{latest['CScore']:.1f}",
                    delta=f"{c_delta:+.1f}",
                    help="基於價量流向模擬之籌碼沉澱指標",
                )
                c4.metric(
                    "Confidence (指標可信度)",
                    f"{latest['Confidence']:.1f}%",
                    help="三維指標共振程度，數值越高代表方向越明確",
                )

                st.info(
                    f"**當前 20D 市場狀態：** {diag['status']}（{diag['msg']}）"
                )
                st.markdown("---")

                # === 區塊 2：5D / 20D / 60D 時間尺度與動態權重 ===
                st.markdown(
                    "### 2. 各時間尺度 (5D / 20D / 60D) 之 P/V/C 權重與得分"
                )

                weight_data = []
                for h in ["5D", "20D", "60D"]:
                    w = weights[h]
                    weight_data.append(
                        {
                            "時間尺度": h,
                            "Price (價) 權重": f"{w['w_p']*100:.1f}%",
                            "Volume (量) 權重": f"{w['w_v']*100:.1f}%",
                            "Chip (籌碼) 權重": f"{w['w_c']*100:.1f}%",
                            "該尺度 PVCS 總分": f"{latest[f'PVCS_{h}']:.1f}",
                        }
                    )

                w_df = pd.DataFrame(weight_data).set_index("時間尺度")
                st.table(w_df)

                st.markdown("---")

                # === 區塊 3：圖表分析 (分兩欄呈現) ===
                col_left, col_right = st.columns(2)

                with col_left:
                    st.markdown("### 3A. P / V / C 三維子指標歷史走勢")
                    st.line_chart(
                        res[["PScore", "VScore", "CScore"]].tail(60)
                    )

                with col_right:
                    st.markdown("### 3B. 5D / 20D / 60D PVCS 綜合分數走勢")
                    st.line_chart(
                        res[["PVCS_5D", "PVCS_20D", "PVCS_60D"]].tail(60)
                    )