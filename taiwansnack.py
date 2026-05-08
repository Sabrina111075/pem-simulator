import streamlit as st
import pandas as pd

def load_data_with_auto_detect():
    try:
        # 讀取檔案
        df_db = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        df_michelin = pd.read_csv('snack_v3.xlsx - MichelinLayer.csv')
        df_scores = pd.read_csv('snack_v3.xlsx - ScoreModel.csv')
        
        # 強制清理所有欄位名稱的空格
        for df in [df_db, df_michelin, df_scores]:
            df.columns = df.columns.str.strip()

        # --- 自動偵測關鍵欄位名稱 ---
        # 尋找包含「縣市」或「City」字眼的欄位
        county_col = [c for c in df_db.columns if '縣市' in c or 'City' in c]
        county_col = county_col[0] if county_col else df_db.columns[0]
        
        # 尋找包含「小吃」或「Name」字眼的欄位
        snack_col = [c for c in df_db.columns if '小吃' in c or 'Name' in c]
        snack_col = snack_col[0] if snack_col else df_db.columns[1]

        # 為了後續處理方便，我們統一重新命名這兩個核心欄位
        df_db = df_db.rename(columns={county_col: '縣市', snack_col: '小吃名稱'})
        df_michelin = df_michelin.rename(columns={
            [c for c in df_michelin.columns if '小吃' in c][0]: '小吃名稱',
            [c for c in df_michelin.columns if '等級' in c][0]: '等級'
        })
        df_scores = df_scores.rename(columns={[c for c in df_scores.columns if '小吃' in c][0]: '小吃名稱'})

        # --- 進行安全合併 ---
        # 1. 先合必比登等級
        master = pd.merge(df_db, df_michelin[['小吃名稱', '等級']].drop_duplicates(), on='小吃名稱', how='left')
        # 2. 再合評分模型
        master = pd.merge(master, df_scores.drop_duplicates(), on='小吃名稱', how='left')
        
        # 填充空值
        master['等級'] = master['等級'].fillna('一般推薦')
        master = master.fillna(0)
        
        return master
    except Exception as e:
        st.error(f"偵測到欄位異常: {e}")
        # 印出目前抓到的欄位名稱，方便除錯
        if 'df_db' in locals(): st.write("資料庫欄位有:", df_db.columns.tolist())
        return None

# --- 執行並渲染 UI ---
data = load_data_with_auto_detect()

if data is not None:
    # 側邊欄過濾
    st.sidebar.header("研發標的選擇")
    counties = data['縣市'].unique()
    sel_county = st.sidebar.selectbox("1. 選擇目標縣市", counties)
    
    # 顯示該縣市清單
    snacks = data[data['縣市'] == sel_county]
    sel_snack = st.sidebar.selectbox("2. 選擇小吃菜單", snacks['小吃名稱'])
    
    # 抓取該筆資料
    row = snacks[snacks['小吃名稱'] == sel_snack].iloc[0]

    # 畫面渲染區
    col_t, col_b = st.columns([0.7, 0.3])
    with col_t:
        st.title(f"🍽️ {sel_snack}")
        st.caption("TAD-AGE 台灣小吃風味開發決策平台")
    
    with col_b:
        # 動態標籤顯示
        lvl = str(row['等級'])
        if "Bib" in lvl or "必比登" in lvl:
            st.error("😋 Bib Gourmand")
        elif "Selected" in lvl or "入選" in lvl:
            st.info("⭐ Michelin Selected")

    st.divider()
    
    # 數值卡片
    c1, c2, c3 = st.columns(3)
    # 這裡的欄位名稱請對應您 ScoreModel 裡的正確標題
    c1.metric("主題發音度", f"{row.get('主題發音度', 0)}/5")
    c2.metric("中段支撐", f"{row.get('中段支撐', 0)}/5")
    c3.metric("前段清亮", f"{row.get('前段清亮', 0)}/5")