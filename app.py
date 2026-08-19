import pandas as pd
import streamlit as st
import yfinance as yf
from pvcs_engine import compute_multi_horizon_pvcs, rule_engine

st.set_page_config(page_title="PVCS 台股三維分析網", layout="wide")

st.title("PVCS 台股價 × 量 × 籌碼三維分析")
st.caption(
    "盤後研究版 | 基於 5D / 20D / 60D 多時間尺度與個股專屬動態權重分析"
)

# 側邊欄：簡化介面，移除令人困惑的歷史範圍，專注於個股分析
st.sidebar.header("分析設定")
ticker_input = st.sidebar.text_input("股票代碼 (台股請加 .TW)", value="2330.TW")

# 預設後台自動抓取 1 年資料用於 IC/ICIR 權重校準
history_period = "1y"

if st.sidebar.button("開始分析", type="primary"):
    with st.spinner(f"正在計算 {ticker_input} 之 5D/20D/60D 權重與 PVCS..."):
        df = yf.download(ticker_input, period=history_period)

        if df.empty:
            st.error("找不到該股票資料，請確認代碼（例如 2330.TW 或 2603.TW）")
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
                "20D 波段分數", f"{latest['PVCS_20D']:.1f}", help="主要研究尺度"
            )
            m3.metric("60D 中線分數", f"{latest['PVCS_60D']:.1f}")
            m4.metric("Composite 綜合總分", f"{latest['PVCS_Composite']:.1f}")

            st.info(
                f"**當前 20D 市場狀態：** {diag['status']}（{diag['msg']}）"
            )
            st.markdown("---")

            # === 區塊 2：5D, 20D, 60D 權重比例分析 ===
            st.markdown("### 2. 各時間尺度 (5D / 20D / 60D) 之 P/V/C 權重比例")

            # 建立 5D, 20D, 60D 權重對比表格
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