import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃開發平台 V3", layout="wide")

# 2. 建立全台資料庫 (加入米其林評比邏輯)
@st.cache_data
def load_michelin_db():
    counties = ["基隆市", "台北市", "新北市", "桃園市", "新竹市", "台中市", "彰化縣", "台南市", "高雄市", "宜蘭縣"] # 範例列出部分
    
    # 縣市與小吃對應
    county_mapping = {
        "基隆市": ["鼎邊銼", "天婦羅", "營養三明治", "泡泡冰", "豆乾包"],
        "台北市": ["蚵仔煎", "刈包", "牛肉麵", "滷肉飯", "生煎包"],
        "台中市": ["大腸包小腸", "肉員", "台中肉員", "焢肉飯", "麻薏湯"],
        "台南市": ["擔仔麵", "牛肉湯", "碗粿", "鱔魚意麵", "虱目魚粥"],
        "彰化縣": ["肉圓", "爌肉飯", "貓鼠麵", "糯米炸", "蛤仔麵"],
    }
    
    # 米其林榮譽資料庫 (根據 snack_v3.xlsx 邏輯)
    michelin_data = {
        "蚵仔煎": {"status": "街頭小吃推薦", "note": "圓環邊蚵仔煎：蚵仔鮮味與粉漿焦香的完美比例。"},
        "刈包": {"status": "必比登推薦", "note": "源芳刈包：五花肉滷製入味，酸菜與花生粉比例均衡。"},
        "牛肉麵": {"status": "必比登推薦", "note": "牛訓練有素的湯頭，藥材與肉香層次分明。"},
        "擔仔麵": {"status": "必比登推薦", "note": "度小月/小公園：鮮蝦頭熬湯，肉燥香氣沉穩。"},
        "肉圓": {"status": "街頭小吃推薦", "note": "彰化阿三/北門口：皮脆肉實，醬汁層次分明。"},
        "鼎邊銼": {"status": "在地標竿", "note": "基隆廟口代表性風味，湯頭鮮甜清亮。"}
    }
    
    # 縣市平均數值
    summary_data = pd.DataFrame({
        "縣市": counties,
        "主題": [4.6, 5.0, 4.6, 5.0, 4.8, 5.0, 4.8, 5.0, 4.5, 4.4],
        "支撐": [3.2, 4.0, 3.4, 3.8, 3.6, 3.6, 4.0, 5.0, 4.2, 3.6],
        "修飾": [2.4, 3.4, 2.4, 3.4, 2.8, 2.8, 2.8, 4.2, 3.8, 3.2],
        "清亮": [3.4, 2.2, 2.6, 2.0, 3.6, 2.2, 2.2, 2.0, 3.0, 3.8],
        "收尾": [2.0, 4.0, 3.0, 3.8, 2.6, 3.4, 3.4, 5.0, 4.5, 2.5]
    })
    
    return summary_data, county_mapping, michelin_data

df_summary, snack_db, michelin_db = load_michelin_db()

# --- UI 開始 ---
st.title("🇹🇼 TAD-AGE 台灣小吃風味平台 (米其林整合版)")

# 3. 左側側邊欄
st.sidebar.header("🧭 導覽中心")
selected_county = st.sidebar.selectbox("1. 選擇縣市", df_summary["縣市"])

# 動態更新小吃選單，並在選單內標註米其林狀態
available_snacks = snack_db.get(selected_county, ["資料待補"])
display_names = []
for s in available_snacks:
    status = michelin_db.get(s, {}).get("status", "")
    if "必比登" in status:
        display_names.append(f"{s} (Bib Gourmand)")
    elif "街頭小吃" in status:
        display_names.append(f"{s} (Street Food)")
    else:
        display_names.append(s)

selected_display_name = st.sidebar.selectbox(f"2. {selected_county} 代表小吃", display_names)
# 還原原始小吃名稱以利查詢
selected_snack = selected_display_name.split(" (")[0]

st.sidebar.divider()
st.sidebar.info("已開啟米其林 (Michelin Layer) 資料連動。")

# 4. 右側主畫面
col_info, col_radar = st.columns([1, 1.2])

with col_info:
    st.header(f"🗂️ 風味模擬卡：{selected_snack}")
    
    # 檢查是否有米其林榮譽
    honor = michelin_db.get(selected_snack)
    if honor:
        st.warning(f"🏆 **{honor['status']}**")
        st.caption(f"推薦語：{honor['note']}")
    
    st.subheader("🧪 結構解構 (Formula Card)")
    # 此處可對應君臣佐使邏輯
    st.markdown(f"""
    - **【君】核心主味**：{selected_snack} 靈魂食材
    - **【臣】中段支撐**：骨架配料與口感
    - **【佐】修飾平衡**：去腥與層次調味
    - **【使】風味導向**：導向收尾之關鍵
    """)
    
    with st.expander("👨‍🍳 核心工藝 (炮製方法)", expanded=True):
        st.write(f"依據 {selected_county} 的傳統工藝，此項小吃需特別注意風味的『過橋差』銜接。")

with col_radar:
    st.header("📊 風味雷達圖 (縣市基準)")
    c_data = df_summary[df_summary["縣市"] == selected_county].iloc[0]
    
    radar_df = pd.DataFrame(dict(
        r=[c_data['主題'], c_data['支撐'], c_data['修飾'], c_data['清亮'], c_data['收尾']],
        theta=['主題', '支撐', '修飾', '清亮', '收尾']
    ))
    
    fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#E63946', fillcolor='rgba(230, 57, 70, 0.3)')
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.write("技術註記：米其林資料已鎖定為 2025-2026 年度版本。")