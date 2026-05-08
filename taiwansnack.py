import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 強力讀取模式
@st.cache_data
def get_safe_data():
    try:
        # 直接讀取主表，這張表已經包含君臣佐使與米其林狀態
        df = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        df.columns = df.columns.str.strip() # 移除標題前後的空格
        return df
    except Exception as e:
        st.error(f"檔案讀取失敗: {e}")
        return None

df = get_safe_data()

if df is not None:
    # --- 側邊欄過濾 ---
    st.sidebar.header("📍 TAD-AGE 研發導航")
    counties = df['縣市'].unique()
    selected_county = st.sidebar.selectbox("選擇縣市", counties)
    
    # 根據縣市過濾小吃
    county_df = df[df['縣市'] == selected_county]
    selected_snack = st.sidebar.selectbox("選擇小吃", county_df['小吃名稱'])
    
    # 提取當前小吃的整列資料
    s = county_df[county_df['小吃名稱'] == selected_snack].iloc[0]

    # --- 標題與米其林標籤 ---
    col_t, col_b = st.columns([0.7, 0.3])
    with col_t:
        st.title(f"🍽️ {selected_snack}")
        st.write(f"**區域：** {selected_county} | **信心等級：** {s.get('資料信心等級', 'D')}")
    
    with col_b:
        # 關鍵修正：將 '等級' 改為 'Michelin_Status'
        m_status = str(s.get('Michelin_Status', 'None'))
        if m_status != 'None' and m_status != 'nan' and m_status != '':
            st.error(f"😋 {m_status}") # 顯示為紅色的米其林標籤
        else:
            st.info("🏠 在地風味精選")

    st.divider()

    # --- 雷達圖與風味分析 ---
    left_c, right_c = st.columns([0.6, 0.4])
    
    with left_c:
        # 五分制維度 (強制轉數字，預防報錯)
        dims = ['主題', '支撐', '修飾', '清亮', '收尾']
        vals = []
        for d in dims:
            v = pd.to_numeric(s.get(d, 0), errors='coerce')
            vals.append(0.0 if pd.isna(v) else float(v))
        
        radar_df = pd.DataFrame(dict(r=vals, theta=dims))
        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', fillcolor='rgba(255, 75, 75, 0.3)', line_color='#FF4B4B')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right_c:
        st.subheader("🧪 君臣佐使配置")
        st.success(f"**君 (主體)：** {s.get('君', '-')}")
        st.write(f"**臣 (支撐)：** {s.get('臣', '-')}")
        st.write(f"**佐 (修飾)：** {s.get('佐', '-')}")
        st.write(f"**使 (收尾)：** {s.get('使', '-')}")
        
        with st.expander("📝 建議配比與提醒"):
            st.write(s.get('建議香氣配比', '尚無研究數據'))
            st.caption("修正提醒：")
            st.write(s.get('風味風險/修正提醒', '無'))