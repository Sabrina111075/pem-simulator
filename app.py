import pandas as pd
import streamlit as st
import yfinance as yf
from pvcs_engine import compute_multi_horizon_pvcs, rule_engine

st.set_page_config(page_title="PVCS 台股三維分析網", layout="wide")

st.title("PVCS 台股價 × 量 × 籌碼三維分析")
st.caption(
    "盤後研究版 | 基於 5D / 20D / 60D 多時間尺度與個股專屬動態權重分析"
)

# === 側邊欄：進階股票選擇機制 ===
st.sidebar.header("分析設定")

# 1. 常用熱門個股選單
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

# 2. 判斷是否為手動輸入並處理代碼格式
if stock_dict[selected_option] == "CUSTOM":
    user_input = st.sidebar.text_input(
        "輸入股票或 ETF 代碼（例如 00878 或 2330）", value="00878"
    )
    raw_ticker = user_input.strip().upper()

    # 自動幫使用者補上 .TW (若無指定 .TWO 或 .TW)
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
            f"正在抓取 {ticker_input} 並計算 5D/20D/60D 權重..."
        ):
            df = yf.download(ticker_input, period="2y")

            # 備用機制：若 .TW 抓不到，嘗試 .TWO (上櫃股票)
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

                # 計算 5D, 20D, 60D 多時間尺度與專屬權重
                res, weights = compute_multi_horizon_pvcs(df)
                latest = res.iloc[-1]

                diag = rule_engine(
                    latest["PScore"],
                    latest["VScore"],
                    latest["CScore"],
                    latest["PVCS_20D"],
                )

                st.success(f"【{ticker_input}】分析完成！")

                # === 區塊 1：5D / 20D / 60D 時間尺度矩陣 ===
                st.markdown("### 1. 多時間尺度 PVCS 矩陣 (5D / 20D / 60D)")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("5D 短線分數", f"{latest['PVCS_5D']:.1f}")
                m2.metric(
                    "20D 波段分數",
                    f"{latest['PVCS_20D']:.1f}",
                    help="主要研究尺度",
                )
                m3.metric("60D 中線分數", f"{latest['PVCS_60D']:.1f}")
                m4.metric(
                    "Composite 綜合總分", f"{latest['PVCS_Composite']:.1f}"
                )

                st.info(
                    f"**當前 20D 市場狀態：** {diag['status']}（{diag['msg']}）"
                )
                st.markdown("---")

                # === 區塊 2：5D, 20D, 60D 權重比例分析 ===
                st.markdown(
                    "### 2. 各時間尺度 (5D / 20D / 60D) 之 P/V/C 權重比例分析"
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
                            "PVCS 得分": f"{latest[f'PVCS_{h}']:.1f}",
                        }
                    )

                w_df = pd.DataFrame(weight_data).set_index("時間尺度")
                st.table(w_df)

                # === 區塊 3：近期 PVCS 走勢圖 ===
                st.markdown("### 3. 近期 5D / 20D / 60D PVCS 走勢比較")
                st.line_chart(
                    res[["PVCS_5D", "PVCS_20D", "PVCS_60D"]].tail(60)
                )