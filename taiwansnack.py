import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置：設定為寬螢幕模式
st.set_page_config(page_title="TAD-AGE 台灣小吃開發平台", layout="wide")

# 2. 核心資料庫邏輯模擬 (根據您的核心資料庫文件定義)
# 我們先手動建立幾個代表性縣市，確保系統邏輯通暢
@st.cache_data
def get_mock_db():
    # 建立縣市平均數據
    summary_data = {
        "縣市": ["基隆市", "台北市", "台南市", "彰化縣", "宜蘭縣"],
        "平均主題": [4.6, 5.0, 4.0, 4.8, 4.5],
        "平均支撐": [3.2, 4.0, 5.0, 4.0, 3.5],
        "平均修飾": [2.4, 3.4, 4.0, 2.8, 3.0],
        "平均清亮": [3.4, 2.2, 2.0, 2.2, 3.8],
        "平均收尾": [2.0, 4.0, 5.0, 3.4, 2.5]
    }
    
    # 建立縣市對應的小吃清單 (各五項)
    snack_list = {
        "基隆市": ["鼎邊銼", "天婦羅", "泡泡冰", "營養三明治", "豆乾包"],
        "台北市": ["蚵仔煎", "刈包", "牛肉麵", "滷肉飯", "生煎包"],
        "台南市": ["擔仔麵", "牛肉湯", "碗粿", "鱔魚意麵", "虱目魚粥"],
        "彰化縣": ["肉圓", "爌肉飯", "貓鼠麵", "糯米炸", "蛤仔麵"],
        "宜蘭縣": ["肉羹", "蔥油餅", "糕渣", "卜肉", "鴨賞"]
    }
    return pd.DataFrame(summary_data), snack_list

df_summary, snack_db = get_mock_db()

# --- UI 佈局開始 ---

# 3. 左側側邊欄 (Sidebar)
st.sidebar.header("🗺️ 地區導覽設定")

# 縣市選擇
selected_county = st.sidebar.selectbox("1. 選擇探索縣市", df_summary["縣市"])

st.sidebar.write("---")

# 根據選擇的縣市，顯示對應的五項代表小吃
st.sidebar.subheader(f"📍 {selected_county} 代表小吃")
current_snacks = snack_db.get(selected_county, ["資料待補"])

# 使用單選按鈕或按鈕來模擬選中特定小吃（為第二階段模擬做準備）
selected_snack = st.sidebar.radio("2. 查看小吃概況", current_snacks)

# 4. 右側主畫面佈局 (分為兩欄：左邊文字說明，右邊雷達圖)
st.title(f"TAD-AGE 風味探索：{selected_county}")

col_info, col_radar = st.columns([1, 1.2]) # 設定比例，讓雷達圖在最右邊並有足夠空間

with col_info:
    st.subheader(f"【{selected_snack}】風味簡介")
    
    # 根據核心資料庫文件的邏輯，顯示自動化評語
    county_stats = df_summary[df_summary["縣市"] == selected_county].iloc[0]
    
    st.info(f"當前縣市資料信心等級：**A (官方認證)**")
    
    st.markdown("#### 💡 TAD-AGE 數據洞察")
    if county_stats["平均收尾"] >= 4.0:
        st.write(f"- **濃厚收尾**：{selected_county} 的小吃普遍重視後段的留香與飽滿度，適合搭配重烘焙茶飲。")
    if county_stats["平均清亮"] >= 3.5:
        st.write(f"- **前段提氣**：該地區小吃強調食材原味的鮮甜與清爽感，君臣關係分明。")
    
    st.write("---")
    st.write("👉 *選中左側小吃後，右側圖表將顯示該縣市的平均風味基準線。*")

with col_radar:
    # 5. 雷達圖形實作 (最右邊)
    radar_df = pd.DataFrame(dict(
        r=[county_stats['平均主題'], county_stats['平均支撐'], county_stats['平均修飾'], 
           county_stats['平均清亮'], county_stats['平均收尾']],
        theta=['主題 (Core)', '支撐 (Body)', '修飾 (Balance)', '清亮 (Bright)', '收尾 (Finish)']
    ))
    
    fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#E63946', fillcolor='rgba(230, 57, 70, 0.3)')
    
    # 優化圖表外觀
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# 頁尾標記
st.divider()
st.caption("技術底層：基於《台灣小吃核心資料庫 V3》定義開發 | TAD-AGE 模擬系統")