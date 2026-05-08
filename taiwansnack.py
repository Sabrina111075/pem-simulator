import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面基礎設置
st.set_page_config(page_title="TAD-AGE 台灣小吃研發平台", layout="wide")

# 2. 穩定載入主資料表 (CountySnackDB)
@st.cache_data
def load_master_data():
    try:
        # 直接讀取主資料表，這張表已經包含了君臣佐使與評分
        df = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        df.columns = df.columns.str.strip() # 移除標題空格
        return df
    except Exception as e:
        st.error(f"❌ 讀取資料失敗，請確認 CountySnackDB.csv 是否存在。錯誤: {e}")
        return None

df = load_master_data()

if df is not None:
    # --- 側邊欄：導航控制 ---
    st.sidebar.header("📍 研發導航系統")
    counties = df['縣市'].unique()
    sel_county = st.sidebar.selectbox("1. 選擇縣市", counties)
    
    # 根據縣市過濾
    snack_options = df[df['縣市'] == sel_county]['小吃名稱'].unique()
    sel_snack = st.sidebar.selectbox("2. 選擇研發品項", snack_options)
    
    # 提取該品項數據列
    s = df[df['小吃名稱'] == sel_snack].iloc[0]

    # --- 主畫面：頭部資訊 ---
    col_t, col_b = st.columns([0.7, 0.3])
    with col_t:
        st.title(f"🍽️ {sel_snack}")
        st.caption(f"TAD-AGE v3 研發架構 | 縣市：{sel_county} | 資料信心：{s.get('資料信心等級', 'D')}")
    
    with col_b:
        # 核心修正：對齊 Michelin_Status 欄位，找不到就給 None
        m_status = str(s.get('Michelin_Status', 'None'))
        if m_status != 'None' and m_status != 'nan' and m_status != '':
            st.error(f"😋 {m_status}") # 顯示為紅標，代表高品質驗證
        else:
            st.info("🏠 在地風味精選")

    st.divider()

    # --- 中間層：雷達圖與風味角色 ---
    left_c, right_c = st.columns([0.6, 0.4])
    
    with left_c:
        # 繪製五維風味雷達圖
        dims = ['主題', '支撐', '修飾', '清亮', '收尾']
        vals = []
        for d in dims:
            # 強制轉換為數字，失敗則給 0，確保雷達圖不崩潰變紅
            v = pd.to_numeric(s.get(d, 0), errors='coerce')
            vals.append(0.0 if pd.isna(v) else float(v))
        
        radar_df = pd.DataFrame(dict(r=vals, theta=dims))
        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', fillcolor='rgba(255, 75, 75, 0.3)', line_color='#FF4B4B')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right_c:
        st.subheader("🧪 君臣佐使配置")
        # 角色顯示
        st.success(f"**君 (主味)：** {s.get('君', '-')}")
        st.write(f"**臣 (支撐)：** {s.get('臣', '-')}")
        st.write(f"**佐 (修飾)：** {s.get('佐', '-')}")
        st.write(f"**使 (引導)：** {s.get('使', '-')}")
        
        with st.expander("📝 建議配比與提醒"):
            st.write(f"**配比模型：**\n{s.get('建議香氣配比', '暫無資料')}")
            st.caption("風味修正建議：")
            st.write(s.get('風味風險/修正提醒', '無'))