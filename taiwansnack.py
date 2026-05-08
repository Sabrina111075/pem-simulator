import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面設定
st.set_page_config(page_title="TAD-AGE 台灣小吃風味平台", layout="wide")
st.title("🇹🇼 台灣小吃風味開發平台 - 地圖探索層")

# 2. 模擬讀取 CountySummary.csv (實際開發時改為 pd.read_csv)
# 這裡先示範核心邏輯
@st.cache_data
def load_summary():
    # 讀取您的 CountySummary.csv 資料
    df = pd.read_csv('snack_v3.xlsx - CountySummary.csv')
    return df

df_summary = load_summary()

# 3. 側邊欄：縣市選擇
st.sidebar.header("地區導覽")
selected_county = st.sidebar.selectbox("選擇要探索的縣市", df_summary['縣市'].unique())

# 4. 主畫面佈局
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"{selected_county} 風味統計")
    # 提取該縣市的風味數值
    county_data = df_summary[df_summary['縣市'] == selected_county].iloc[0]
    
    # 準備雷達圖數據
    radar_df = pd.DataFrame(dict(
        r=[county_data['平均主題'], county_data['平均支撐'], county_data['平均修飾'], 
           county_data['平均清亮'], county_data['平均收尾']],
        theta=['主題', '支撐', '修飾', '清亮', '收尾']
    ))
    
    fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader(f"{selected_county} 代表小吃")
    # 此處未來將串接 CountySnackDB.csv 顯示 Top 5
    st.info(f"正在載入 {selected_county} 的 5 項經典小吃資料...")
    # 示範顯示清單
    st.write("1. 代表小吃 A (信心等級：A)")
    st.write("2. 代表小吃 B (信心等級：B)")
    st.write("3. 代表小吃 C (信心等級：A)")

# 5. 下一步預告
st.divider()
if st.button("進入【風味卡模擬】階段"):
    st.success("即將解構該縣市小吃的『君臣佐使』配方...")