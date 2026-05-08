import pandas as pd

def load_and_sync_data():
    # 1. 載入各個分頁 (假設已轉為 CSV 或直接讀取 Excel)
    df_db = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
    df_michelin = pd.read_csv('snack_v3.xlsx - MichelinLayer.csv')
    df_scores = pd.read_csv('snack_v3.xlsx - ScoreModel.csv')
    df_formula = pd.read_csv('snack_v3.xlsx - FormulaCard_Template.csv')

    # 2. 資料清洗 (去除空白字元，確保 Key 值對齊)
    for df in [df_db, df_michelin, df_scores, df_formula]:
        df.columns = df.columns.str.strip()
        if '小吃名稱' in df.columns:
            df['小吃名稱'] = df['小吃名稱'].str.strip()

    # 3. 核心關聯邏輯：將榮譽標籤與評分併入主資料庫
    # 我們使用 '小吃名稱' 作為 Key，進行 Left Join
    master_df = pd.merge(df_db, df_michelin[['小吃名稱', '等級', '年份']], on='小吃名稱', how='left')
    master_df = pd.merge(master_df, df_scores, on='小吃名稱', how='left')

    # 4. 邏輯判斷：標註推薦類型 (用於前端顯示標籤)
    def categorize_honor(row):
        if pd.isna(row['等級']):
            return "一般推薦"
        elif "Bib" in str(row['等級']):
            return "必比登推介"
        elif "Selected" in str(row['等級']) or "入選" in str(row['等級']):
            return "米其林入選"
        return "星級餐廳"

    master_df['Honor_Type'] = master_df.apply(categorize_honor, axis=1)
    
    return master_df, df_formula

# 執行載入
master_data, formula_template = load_and_sync_data()