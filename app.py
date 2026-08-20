from datetime import datetime
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

# === 側邊欄：設定與資料來源資訊 ===
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
        "輸入股票或 ETF 代碼（例如 00878 或 2330）", value="2330"
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

start_analysis = st.sidebar.button("開始分析", type="primary")

# === 側邊欄：資料來源與系統聲明 ===
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 資料來源與系統說明")
st.sidebar.caption(
    "**行情數據源**：\n"
    "• 台灣證券交易所 (TWSE)\n"
    "• 證券櫃檯買賣中心 (TPEx)\n"
    "• API 介接：Yahoo Finance (延遲 15-20 分鐘)\n"
    "• *註：每日 14:30 盤後清算完成後為最準確之最終收盤數據。*"
)
st.sidebar.caption(
    "**三維模型維度**：\n"
    "• **Price**：趨勢強度與 20MA 乖離率\n"
    "• **Volume**：相對成交量與價量共振\n"
    "• **Chip**：價量動能累積 (Money Flow)\n"
    "• **Weights**：自適應 IC/ICIR 權重"
)
st.sidebar.caption(
    "⚠️ **免責聲明**：\n"
    "本系統數據與分析結果僅供學術研究與量化策略評估參考，不構成任何投資買賣建議。"
)

# === 主畫面邏輯 ===
if start_analysis:
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

                # 判斷盤中或最終收盤狀態
                latest_date = res.index[-1]
                latest_date_str = latest_date.strftime("%Y-%m-%d")
                now_hour = datetime.now().hour

                # 簡單判斷：若為今日且未滿 14:30，標示為盤中延遲
                if (
                    latest_date.date() == datetime.now().date()
                    and now_hour < 15
                ):
                    status_tag = (
                        f"<span style='color:orange;'>{latest_date_str} (盤中即時/暫存數據)</span>"
                    )
                else:
                    status_tag = f"<span style='color:green;'>{latest_date_str} (盤後最終數據)</span>"

                close_price = latest["Close"]
                price_change = close_price - prev["Close"]
                price_pct = (price_change / prev["Close"]) * 100

                vol_sheets = latest["Volume"] / 1000
                prev_vol_sheets = prev["Volume"] / 1000
                vol_change = vol_sheets - prev_vol_sheets

                diag = rule_engine(
                    latest["PScore"],
                    latest["VScore"],
                    latest["CScore"],
                    latest["PVCS_20D"],
                )

                st.success(f"【{ticker_input}】量化三維分析完成！")

                # === 區塊 1：行情數據與三維因子得分 ===
                st.markdown(
                    f"### 1. 市場行情與 P/V/C 得分 `(資料日期:` {status_tag} `)`",
                    unsafe_allow_html=True,
                )

                if "盤中即時" in status_tag:
                    st.warning(
                        "⚠️ 提示：目前時間尚在盤中/清算時間（14:30 前），Yahoo API 提供的成交量與價格為盤中暫存數據（具 15-20 分鐘延遲），完整成交張數將於 14:30 盤後作業完成後自動更新。"
                    )

                # 第一列：最新收盤價與成交量
                k1, k2, k3 = st.columns(3)
                k1.metric(
                    "最新價格/收盤價",
                    f"${close_price:.2f}",
                    delta=f"{price_change:+.2f} ({price_pct:+.2f}%)",
                )
                k2.metric(
                    "成交量 (目前估算)",
                    f"{vol_sheets:,.0f} 張",
                    delta=f"{vol_change:+,.0f} 張",
                )
                k3.metric(
                    "Confidence (指標可信度)",
                    f"{latest['Confidence']:.1f}%",
                    help="三維指標共振程度，數值越高代表方向越明確",
                )

                # 第二列：P / V / C 三維因子得分
                c1, c2, c3 = st.columns(3)
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

                # === 區塊 3：圖表分析 ===
                st.markdown("### 3. P / V / C 三維子指標歷史走勢 (近 60 日)")
                st.line_chart(
                    res[["PScore", "VScore", "CScore"]].tail(60)
                )

                st.markdown("---")

                st.markdown(
                    "### 4. 5D / 20D / 60D PVCS 綜合分數走勢比較 (近 60 日)"
                )
                st.line_chart(
                    res[["PVCS_5D", "PVCS_20D", "PVCS_60D"]].tail(60)
                )