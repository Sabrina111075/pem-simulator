import streamlit as st
import pandas as pd
import plotly.express as px

# --- 第一步：數據載入與欄位對齊 ---
@st.cache_data
def load_data():
    try:
        # 直接讀取您上傳的主表
        df = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        df.columns = df.columns.str.strip() # 去除標題隱形空格
        return df
    except Exception as e:
        st.error(f"檔案讀取失敗，請確認 CountySnackDB.csv 是否存在。")
        return None

df = load_data()

if df is not None:
    # --- 第二步：選單設計 ---
    st.sidebar.header("📍 TAD-AGE 研發導航")
    counties = df['縣市'].unique()
    sel_county = st.sidebar.selectbox("1. 選擇縣市", counties)
    
    # 根據縣市過濾
    county_snacks = df[df['縣市'] == sel_county]
    sel_snack = st.sidebar.selectbox("2. 選擇小吃", county_snacks['小吃名稱'])
    
    # 取得當前小吃資料列
    s = county_snacks[county_snacks['小吃名稱'] == sel_snack].iloc[0]

    # --- 第三步：標籤視覺 (米其林) ---
    col_t, col_b = st.columns([0.7, 0.3])
    
    with col_t:
        st.title(f"🍽️ {sel_snack}")
        st.write(f"系統架構：TAD-AGE | 縣市：{sel_county}")

    with col_b:
        # 關鍵修正：對應 Michelin_Status 欄位，找不到就顯示在地精選
        m_status = str(s.get('Michelin_Status', 'None'))
        if m_status != 'None' and m_status != 'nan' and m_status != '':
            st.error(f"😋 {m_status}") # 紅色勳章
        else:
            st.info("🏠 在地風味精選") # 藍色/灰色標籤

    st.divider()

    # --- 第四步：雷達圖繪製 (強健模式) ---
    left_col, right_col = st.columns([0.6, 0.4])
    
    with left_col:
        # 定義維度並強制轉換為數字
        dims = ['主題', '支撐', '修飾', '清亮', '收尾']
        vals = []
        for d in dims:
            try:
                # 使用 pd.to_numeric 處理空值或字串
                v = pd.to_numeric(s.get(d, 0), errors='coerce')
                vals.append(0.0 if pd.isna(v) else float(v))
            except:
                vals.append(0.0)
        
        # 繪圖
        radar_df = pd.DataFrame(dict(r=vals, theta=dims))
        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', fillcolor='rgba(255, 75, 75, 0.3)', line_color='#FF4B4B')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("🧪 君臣佐使配置")
        st.markdown(f"- **君 (主體)：** {s.get('君', '-')}")
        st.markdown(f"- **臣 (支撐)：** {s.get('臣', '-')}")
        st.markdown(f"- **佐 (修飾)：** {s.get('佐', '-')}")
        st.markdown(f"- **使 (收尾)：** {s.get('使', '-')}")
        
        with st.expander("📝 建議香氣配比與提醒"):
            st.write(s.get('建議香氣配比', '尚無研究數據'))
            st.caption("修正提醒：")
            st.write(s.get('風味風險/修正提醒', '無'))

# 底部 Debug 資訊 (畫面穩定了可以刪除)
if st.checkbox("顯示原始資料欄位 (Debug)"):
    st.write(list(df.columns))