import pandas as pd
import plotly.express as px

# 讀取您上傳的彙總資料
df_summary = pd.read_csv('snack_v3.xlsx - CountySummary.csv')

def get_county_radar(county_name):
    # 提取特定縣市的風味分數
    row = df_summary[df_summary['縣市'] == county_name].iloc[0]
    
    # 對應您的五分制模型
    categories = ['主題', '支撐', '修飾', '清亮', '收尾']
    scores = [row['平均主題'], row['平均支撐'], row['平均修飾'], row['平均清亮'], row['平均收尾']]
    
    fig = px.line_polar(r=scores, theta=categories, line_close=True)
    fig.update_traces(fill='toself')
    return fig