import streamlit as st
import plotly.express as px
import pandas as pd

# 頁面基本設定
st.set_page_config(page_title="TAD-AGE 台灣小吃開發平台", layout="wide")

st.title("🇹🇼 台灣小吃風味開發平台 (V3 核心架構版)")
st.write("目前載入模式：核心資料庫邏輯模擬 (不讀取外部 CSV，避免執行錯誤)")

# 1. 直接在程式碼中定義示範數據 (取自核心資料庫 docx 的範例)
mock_data = {
    "縣市": ["基隆市", "台北市", "台南市"],
    "代表小吃": ["鼎邊銼", "蚵仔煎", "擔仔麵"],
    "主題": [5, 5, 4],
    "支撐": [3, 4, 5],
    "修飾": [3, 3, 4],
    "清亮": [4, 3, 2],
    "收尾": [2, 2, 5],
    "信心等級": ["B", "A+", "A"]
}
df = pd.DataFrame(mock_data)

# 2. 側邊欄：選擇縣市
st.sidebar.header("地區導覽")
selected_county = st.sidebar.selectbox("選擇要探索的縣市", df["縣市"])

# 3. 畫面佈局
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"{selected_county} 風味特徵雷達圖")
    # 提取選中縣市的數據
    c_data = df[df["縣市"] == selected_county].iloc[0]
    
    # 建立雷達圖數據
    radar_df = pd.DataFrame(dict(
        r=[c_data['主題'], c_data['支撐'], c_data['修飾'], c_data['清亮'], c_data['收尾']],
        theta=['主題', '支撐', '修飾', '清亮', '收尾']
    ))
    
    fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#E63946')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("區域資料摘要")
    st.info(f"代表小吃：{c_data['代表小吃']}")
    st.metric("資料信心等級", c_data['信心等級'])
    
    # 基於文件中的五分制邏輯自動評語
    st.write("---")
    st.markdown("**TAD-AGE 風味洞察：**")
    if c_data['收尾'] >= 4:
        st.write("💡 此區域風味重點在於『留香』，收尾感強烈，適合研發厚重型產品。")
    if c_data['清亮'] >= 4:
        st.write("💡 此區域注重『前段提氣』，口感清爽，具有高度的解膩特質。")

st.divider()
st.caption("技術註記：此版本基於『台灣小吃核心資料庫.docx』手冊開發，用於驗證 UI 邏輯。")