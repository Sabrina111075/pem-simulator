import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃開發平台", layout="wide")

# 2. 安全讀取檔案函數 (防止路徑報錯)
def load_data():
    file_name = "snack_v3.xlsx - CountySummary.csv"
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        st.error(f"找不到檔案：{file_name}，請確認檔案放在同一個資料夾下。")
        return None

df_summary = load_data()

if df_summary is not None:
    st.title("🇹🇼 第一階段：地圖探索與風味統計")
    
    # 3. 側邊欄：選擇縣市
    st.sidebar.header("導覽設定")
    all_counties = df_summary['縣市'].unique()
    selected_county = st.sidebar.selectbox("切換探索縣市", all_counties)
    
    # 4. 主畫面佈局
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"{selected_county} 平均風味特徵")
        # 提取該縣市數據
        c_data = df_summary[df_summary['縣市'] == selected_county].iloc[0]
        
        # 建立雷達圖資料
        radar_df = pd.DataFrame(dict(
            r=[c_data['平均主題'], c_data['平均支撐'], c_data['平均修飾'], 
               c_data['平均清亮'], c_data['平均收尾']],
            theta=['主題', '支撐', '修飾', '清亮', '收尾']
        ))
        
        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', line_color='#E63946')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("數據洞察")
        st.write(f"在 **{selected_county}** 的資料集中：")
        st.metric("小吃總數", f"{c_data['小吃數']} 筆")
        st.write("---")
        # 根據數據給予自動化評語 (TAD-AGE 邏輯初探)
        if c_data['平均收尾'] > 3.5:
            st.success("💡 該地區風味偏向濃厚，收尾層次豐富。")
        if c_data['平均清亮'] > 3.0:
            st.info("💡 該地區注重前段提氣，口感較為清爽。")