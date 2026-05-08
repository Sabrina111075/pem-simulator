import streamlit as st
import pandas as pd

# --- 1. 後端資料載入與同步 (加強錯誤檢查) ---
def safe_load_data():
    try:
        # 讀取檔案 (請確保檔名與您上傳的一致)
        df_db = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        df_michelin = pd.read_csv('snack_v3.xlsx - MichelinLayer.csv')
        df_scores = pd.read_csv('snack_v3.xlsx - ScoreModel.csv')
        
        # 清洗欄位空白
        for df in [df_db, df_michelin, df_scores]:
            df.columns = df.columns.str.strip()
            if '小吃名稱' in df.columns:
                df['小吃名稱'] = df['小吃名稱'].str.strip()

        # 進行合併
        # 加上 validate="1:1" 確保資料不會因為重複而膨脹
        master = pd.merge(df_db, df_michelin[['小吃名稱', '等級']].drop_duplicates(), on='小吃名稱', how='left')
        master = pd.merge(master, df_scores.drop_duplicates(), on='小吃名稱', how='left')
        
        # 填充缺失值，避免評分變成 NaN 導致雷達圖報錯
        master['等級'] = master['等級'].fillna('一般推薦')
        master = master.fillna(0) # 沒評分的部分先給 0
        
        return master
    except Exception as e:
        st.error(f"資料載入失敗，錯誤訊息: {e}")
        return None

# --- 2. 前端顯示邏輯 (確保元件一定會渲染) ---
master_data = safe_load_data()

if master_data is not None:
    # 側邊欄選擇
    st.sidebar.header("研發標的選擇")
    all_counties = master_data['縣市'].unique()
    selected_county = st.sidebar.selectbox("1. 選擇目標縣市", all_counties)
    
    # 根據縣市過濾小吃
    county_snacks = master_data[master_data['縣市'] == selected_county]
    selected_snack_name = st.sidebar.selectbox("2. 選擇小吃菜單", county_snacks['小吃名稱'])
    
    # 取得選定小吃的整行資料
    snack_info = county_snacks[county_snacks['小吃名稱'] == selected_snack_name].iloc[0]

    # --- UI 渲染 ---
    title_col, badge_col = st.columns([0.7, 0.3])
    
    with title_col:
        st.title(f"🍽️ {selected_snack_name}")
        st.write(f"系統架構：TAD-AGE | 研發人員：Sabrina")

    with badge_col:
        # 根據 '等級' 欄位顯示標籤
        level = snack_info['等級']
        if "Bib" in str(level):
            st.warning("😋 必比登推介")
        elif "Selected" in str(level) or "入選" in str(level):
            st.info("⭐ 米其林入選")

    # 顯示評分卡 (確保數值存在)
    col1, col2, col3 = st.columns(3)
    col1.metric("主題發音度", f"{int(snack_info.get('主題發音度', 0))}/5")
    col2.metric("中段支撐", f"{int(snack_info.get('中段支撐', 0))}/5")
    col3.metric("前段清亮", f"{int(snack_info.get('前段清亮', 0))}/5")

else:
    st.warning("請檢查 CSV 檔案路徑與欄位名稱是否正確。")