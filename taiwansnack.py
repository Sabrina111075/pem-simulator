import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 強力讀取模式：確保欄位乾淨
@st.cache_data
def load_clean_data():
    try:
        # 直接讀取主資料庫
        df = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        # 移除欄位名稱前後可能存在的隱形成空格
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"檔案讀取失敗，請確認檔案名稱是否正確：{e}")
        return None

df = load_clean_data()

if df is not None:
    # --- 側邊欄導航 ---
    st.sidebar.header("📍 TAD-AGE 研發導航")
    counties = df['縣市'].unique()
    sel_county = st.sidebar.selectbox("選擇縣市", counties)
    
    # 根據縣市過濾小吃
    snack_list = df[df['縣市'] == sel_county]['小吃名稱'].unique()
    sel_snack = st.sidebar.selectbox("選擇小吃品項", snack_list)
    
    # 抓取該筆小吃的所有數據
    s = df[df['小吃名稱'] == sel_snack].iloc[0]

    # --- 畫面頭部：標題與標籤 ---
    col_t, col_b = st.columns([0.7, 0.3])
    with col_t:
        st.title(f"🍽️ {sel_snack}")
        st.caption(f"研發系統：TAD-AGE v3 | 縣市：{sel_county} | 信心：{s.get('資料信心等級', 'D')}")
    
    with col_b:
        # 修正 KeyError 的關鍵：對應正確的欄位名稱
        m_status = str(s.get('Michelin_Status', 'None'))
        if m_status != 'None' and m_status != 'nan' and m_status != '':
            st.error(f"😋 {m_status}") # 米其林紅標
        else:
            st.info("🏠 在地風味精選")

    st.divider()

    # --- 中間層：雷達圖與風味分析 ---
    c1, c2 = st.columns([0.6, 0.4])
    with c1:
        # 五分制維度 (強制轉數字，預防 CSV 雜訊)
        dims = ['主題', '支撐', '修飾', '清亮', '收尾']
        vals = []
        for d in dims:
            v = pd.to_numeric(s.get(d, 0), errors='coerce')
            vals.append(0.0 if pd.isna(v) else float(v))
        
        # 繪製雷達圖
        radar_df = pd.DataFrame(dict(r=vals, theta=dims))
        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', fillcolor='rgba(255, 75, 75, 0.3)', line_color='#FF4B4B')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🧪 君臣佐使配置")
        st.success(f"**君 (主體)：** {s.get('君', '-')}")
        st.write(f"**臣 (支撐)：** {s.get('臣', '-')}")
        st.write(f"**佐 (平衡)：** {s.get('佐', '-')}")
        st.write(f"**使 (收尾)：** {s.get('使', '-')}")
        
        with st.expander("📝 研發建議與提醒"):
            st.write(f"**建議配比：**\n{s.get('建議香氣配比', '尚無研究數據')}")
            st.caption("風味修正提醒：")
            st.write(s.get('風味風險/修正提醒', '無'))