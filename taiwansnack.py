import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 穩定讀取資料庫
@st.cache_data
def load_data():
    try:
        # 讀取主資料表
        df = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        # 自動清理欄位名稱前後的空白
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"找不到資料檔案，請確認檔名是否正確。錯誤資訊: {e}")
        return None

df = load_data()

if df is not None:
    # 側邊欄過濾
    st.sidebar.header("📍 研發導航系統")
    counties = df['縣市'].unique()
    sel_county = st.sidebar.selectbox("選擇縣市", counties)
    
    snack_list = df[df['縣市'] == sel_county]['小吃名稱'].unique()
    sel_snack = st.sidebar.selectbox("選擇小吃", snack_list)
    
    # 抓取該筆資料
    s = df[df['小吃名稱'] == sel_snack].iloc[0]

    # --- UI 呈現區 ---
    col_t, col_b = st.columns([0.7, 0.3])
    
    with col_t:
        st.title(f"🍽️ {sel_snack}")
        st.caption(f"TAD-AGE 研發架構 | 數據信心等級：{s.get('資料信心等級', 'D')}")

    with col_b:
        # 核心修正：對應正確的 Michelin_Status 欄位
        m_status = str(s.get('Michelin_Status', 'None'))
        if m_status != 'None' and m_status != 'nan':
            st.error(f"😋 {m_status}") # 米其林紅標
        else:
            st.info("🏠 在地風味精選")

    st.divider()

    # --- 雷達圖與風味分析 ---
    c1, c2 = st.columns([0.6, 0.4])
    with c1:
        # 定義維度並確保數值化
        categories = ['主題', '支撐', '修飾', '清亮', '收尾']
        values = []
        for cat in categories:
            val = s.get(cat, 0)
            # 轉換為浮點數，若失敗則給 0
            try:
                values.append(float(val))
            except:
                values.append(0.0)
        
        fig = px.line_polar(pd.DataFrame(dict(r=values, theta=categories)), 
                           r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', fillcolor='rgba(255, 75, 75, 0.3)', line_color='#FF4B4B')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("📊 風味組成 (君臣佐使)")
        st.markdown(f"- **君：** {s.get('君', '-')}")
        st.markdown(f"- **臣：** {s.get('臣', '-')}")
        st.markdown(f"- **佐：** {s.get('佐', '-')}")
        st.markdown(f"- **使：** {s.get('使', '-')}")
        
        with st.expander("📝 建議配比與提醒"):
            st.write(s.get('建議香氣配比', '尚無資料'))
            st.caption("修正提醒：")
            st.write(s.get('風味風險/修正提醒', '無'))