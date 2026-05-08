import streamlit as st
import pandas as pd

# 1. 資料載入 (增加對編碼與空白的防禦)
@st.cache_data
def get_clean_data():
    try:
        # 讀取主資料庫
        df = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        # 清理所有欄位名稱前後的空白字元
        df.columns = df.columns.str.strip()
        # 確保小吃名稱與縣市沒有多餘空白
        df['縣市'] = df['縣市'].astype(str).str.strip()
        df['小吃名稱'] = df['小吃名稱'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"讀取 CSV 失敗: {e}")
        return None

df = get_clean_data()

if df is not None:
    # --- 側邊欄控制 ---
    st.sidebar.header("📍 研發導航")
    counties = df['縣市'].unique()
    selected_county = st.sidebar.selectbox("選擇縣市", counties)
    
    # 過濾該縣市小吃
    county_df = df[df['縣市'] == selected_county]
    selected_snack = st.sidebar.selectbox("選擇小吃", county_df['小吃名稱'])
    
    # 取得當前小吃的所有資訊
    s = county_df[county_df['小吃名稱'] == selected_snack].iloc[0]

    # --- 畫面主體 ---
    col_title, col_badge = st.columns([0.7, 0.3])
    
    with col_title:
        st.title(f"{selected_snack}")
        st.write(f"**開發架構：** {s.get('君', '未定義')} (君) / {s.get('臣', '未定義')} (臣)")

    with col_badge:
        # 直接從 CountySnackDB 的 Michelin_Status 判斷
        status = str(s.get('Michelin_Status', 'None'))
        if status != 'None' and status != 'nan':
            # 這裡可以根據您的資料內容微調判斷邏輯
            st.markdown(
                f'<div style="background-color: #FF4B4B; color: white; padding: 8px; border-radius: 5px; text-align: center; font-weight: bold;">'
                f'😋 {status}'
                f'</div>', unsafe_allow_html=True
            )

    st.divider()

    # --- 風味評分卡 (五分制) ---
    st.subheader("📊 風味開發模型")
    m1, m2, m3, m4, m5 = st.columns(5)
    
    # 使用 .get 確保如果欄位名稱微標不符，也不會報錯導致白畫面
    m1.metric("主題", f"{s.get('主題', 0)}")
    m2.metric("支撐", f"{s.get('支撐', 0)}")
    m3.metric("修飾", f"{s.get('修飾', 0)}")
    m4.metric("清亮", f"{s.get('清亮', 0)}")
    m5.metric("收尾", f"{s.get('收尾', 0)}")

    # --- 研發備註 ---
    with st.expander("📝 研發風險與修正提醒"):
        st.info(s.get('風味風險/修正提醒', '尚無備註'))
        
    # 如果想看原始資料欄位(Debug 用，正常後可刪除)
    # st.write("目前可用欄位：", list(df.columns))