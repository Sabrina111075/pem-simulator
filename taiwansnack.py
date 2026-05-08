import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. 超強防禦資料讀取 ---
@st.cache_data
def load_and_fix_data():
    try:
        df = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        df.columns = df.columns.str.strip()
        
        # 強制轉換評分欄位為數字，出錯就變 0
        score_cols = ['主題', '支撐', '修飾', '清亮', '收尾']
        for col in score_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"❌ 讀取 CSV 失敗，請確認檔案名稱與格式: {e}")
        return None

df = load_and_fix_data()

if df is not None:
    # 側邊欄與資料選取 (略，維持原本邏輯)
    st.sidebar.header("📍 研發導航")
    counties = df['縣市'].unique()
    sel_county = st.sidebar.selectbox("選擇縣市", counties)
    sel_snack = st.sidebar.selectbox("選擇小吃", df[df['縣市']==sel_county]['小吃名稱'])
    s = df[df['小吃名稱'] == sel_snack].iloc[0]

    # --- 2. 顯示標題與標籤 (安全模式) ---
    st.title(f"🍽️ {sel_snack}")
    
    # --- 3. 雷達圖 (加入 try-except 保護) ---
    try:
        categories = ['主題', '支撐', '修飾', '清亮', '收尾']
        values = [float(s[c]) for c in categories]
        
        fig = px.line_polar(pd.DataFrame(dict(r=values, theta=categories)), 
                           r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', fillcolor='rgba(255, 75, 75, 0.3)')
        st.plotly_chart(fig, use_container_width=True)
    except Exception as chart_err:
        st.warning(f"⚠️ 雷達圖目前無法顯示，可能是數據格式問題：{chart_err}")

    # --- 4. 顯示數值 (使用 metric) ---
    cols = st.columns(5)
    for i, cat in enumerate(['主題', '支撐', '修飾', '清亮', '收尾']):
        cols[i].metric(cat, s.get(cat, 0))

else:
    st.info("💡 請確保 snack_v3 相關的 CSV 檔案已上傳至正確目錄。")