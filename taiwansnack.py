import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 穩定讀取主資料庫
@st.cache_data
def load_master_db():
    try:
        # 直接讀取主表，這張表已經整合了大部分資訊
        df = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        df.columns = df.columns.str.strip() # 去除隱形空格
        return df
    except Exception as e:
        st.error(f"找不到主資料庫檔案: {e}")
        return None

df = load_master_db()

if df is not None:
    # 側邊欄過濾
    st.sidebar.header("📍 TAD-AGE 導航系統")
    counties = df['縣市'].unique()
    sel_county = st.sidebar.selectbox("選擇縣市", counties)
    
    # 取得該縣市小吃
    snack_list = df[df['縣市'] == sel_county]['小吃名稱'].unique()
    sel_snack = st.sidebar.selectbox("選擇小吃菜單", snack_list)
    
    # 抓取該筆資料行
    s = df[df['小吃名稱'] == sel_snack].iloc[0]

    # --- UI 呈現 ---
    col_t, col_b = st.columns([0.7, 0.3])
    
    with col_t:
        st.title(f"🍽️ {sel_snack}")
        st.write(f"**區域：** {sel_county} | **信心等級：** {s.get('資料信心等級', 'D')}")

    with col_b:
        # 修正 KeyError 的關鍵：使用 .get 並對應正確欄位名 Michelin_Status
        m_status = str(s.get('Michelin_Status', 'None'))
        
        if m_status != 'None' and m_status != 'nan':
            st.error(f"😋 {m_status}") # 必比登/米其林用紅色顯示
        else:
            st.info("🏠 在地風味精選")

    st.divider()

    # --- 雷達圖保護區 ---
    c1, c2 = st.columns([0.6, 0.4])
    with c1:
        # 定義五維維度
        categories = ['主題', '支撐', '修飾', '清亮', '收尾']
        # 強制轉為浮點數，預防亂碼或空值
        values = [pd.to_numeric(s.get(cat, 0), errors='coerce') for cat in categories]
        values = [0 if pd.isna(v) else v for v in values] # 處理 NaN
        
        fig = px.line_polar(pd.DataFrame(dict(r=values, theta=categories)), 
                           r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', fillcolor='rgba(255, 75, 75, 0.3)', line_color='#FF4B4B')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("📊 風味組成 (君臣佐使)")
        st.write(f"**君：** {s.get('君', '-')}")
        st.write(f"**臣：** {s.get('臣', '-')}")
        st.write(f"**佐：** {s.get('佐', '-')}")
        st.write(f"**使：** {s.get('使', '-')}")
        
        with st.expander("💡 研發配比與提醒"):
            st.caption("建議配比：")
            st.write(s.get('建議香氣配比', '暫無資料'))
            st.caption("修正提醒：")
            st.write(s.get('風味風險/修正提醒', '尚無備註'))