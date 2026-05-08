import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 讀取並清理資料
@st.cache_data
def get_final_data():
    df = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
    df.columns = df.columns.str.strip()
    return df

df = get_final_data()

if df is not None:
    # --- 側邊欄過濾 ---
    st.sidebar.header("📍 TAD-AGE 研發導航")
    counties = df['縣市'].unique()
    selected_county = st.sidebar.selectbox("選擇縣市", counties)
    county_df = df[df['縣市'] == selected_county]
    selected_snack = st.sidebar.selectbox("選擇小吃", county_df['小吃名稱'])
    s = county_df[county_df['小吃名稱'] == selected_snack].iloc[0]

    # --- 頂部標題與動態標籤 ---
    col_t, col_b = st.columns([0.7, 0.3])
    with col_t:
        st.title(f"{selected_snack}")
        st.write(f"**風味核心 (君)：** {s.get('君', '未定義')}")
    
    with col_b:
        status = str(s.get('Michelin_Status', 'None'))
        if status != 'None' and status != 'nan':
            color = "#FF4B4B" # 米其林紅
            label = f"😋 {status}"
        else:
            color = "#6D6D6D" # 專業灰色
            label = "🏠 在地風味精選"
        
        st.markdown(
            f'<div style="background-color: {color}; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 2px solid white; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">'
            f'{label}</div>', unsafe_allow_html=True
        )

    st.divider()

    # --- 雷達圖與數據卡片 ---
    left_col, right_col = st.columns([0.5, 0.5])
    
    with left_col:
        # 準備雷達圖數據
        categories = ['主題', '支撐', '修飾', '清亮', '收尾']
        values = [s.get(c, 0) for c in categories]
        
        radar_df = pd.DataFrame(dict(r=values, theta=categories))
        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', line_color='#FF4B4B')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("📊 風味維度分析")
        for cat in categories:
            val = s.get(cat, 0)
            st.write(f"**{cat}**")
            st.progress(int(val) * 20) # 轉成百分比顯示進度條

    # --- 君臣佐使詳細說明 ---
    st.subheader("🧪 研發配方卡 (Formula Card)")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("君 (主體)", s.get('君', '-'))
    f2.metric("臣 (支撐)", s.get('臣', '-'))
    f3.metric("佐 (平衡)", s.get('佐', '-'))
    f4.metric("使 (收尾)", s.get('使', '-'))

    with st.expander("📝 研發風險與修正提醒"):
        st.write(s.get('風味風險/修正提醒', '尚無具體備註'))