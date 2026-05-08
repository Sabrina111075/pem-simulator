import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃研發平台", layout="wide")

# 2. 模擬核心資料庫 (依據您的 docx 文件定義)
@st.cache_data
def get_extended_db():
    # 縣市平均風味數據
    summary_data = {
        "縣市": ["基隆市", "台北市", "台南市", "彰化縣"],
        "主題": [4.6, 5.0, 4.0, 4.8],
        "支撐": [3.2, 4.0, 5.0, 4.0],
        "修飾": [2.4, 3.4, 4.0, 2.8],
        "清亮": [3.4, 2.2, 2.0, 2.2],
        "收尾": [2.0, 4.0, 5.0, 3.4]
    }
    
    # 核心小吃詳細配方 (君臣佐使炮製)
    formula_db = {
        "鼎邊銼": {
            "君": "海鮮高湯 (鮮味核心)",
            "臣": "米漿片、肉羹 (口感支撐)",
            "佐": "白胡椒、蒜酥 (去腥提味)",
            "使": "芹菜、油蔥 (香氣導向)",
            "炮製": "米漿沿鍋邊翻滾成片，高湯需加入蝦乾、香菇慢火熬製，確保海味清亮。"
        },
        "蚵仔煎": {
            "君": "鮮蚵 (主題鮮味)",
            "臣": "雞蛋、粉漿 (軟Q骨架)",
            "佐": "小白菜、蒜泥 (平衡解膩)",
            "使": "甜辣醬 (風味收尾)",
            "炮製": "高溫煎盤使粉漿邊緣焦脆，蚵仔需飽滿不縮水，醬汁需具備甜、鹹、酸平衡。"
        },
        "擔仔麵": {
            "君": "鮮蝦頭高湯 (靈魂主題)",
            "臣": "油麵、鮮蝦 (實體支撐)",
            "佐": "肉燥、蒜泥 (厚重補強)",
            "使": "香菜、烏醋 (解膩導向)",
            "炮製": "肉燥需長時間慢滷出膠質，麵條川燙時間嚴格控制，最後淋上少許烏醋提氣。"
        },
        "肉圓": {
            "君": "豬肉內餡 (扎實核心)",
            "臣": "地瓜粉外皮 (Q彈支撐)",
            "佐": "筍丁、五香粉 (層次修飾)",
            "使": "白醬/甜辣醬 (載體收尾)",
            "炮製": "採『低溫油炸』使皮Q而不韌，醬汁需分層次加入，確保第一口到最後一口風味一致。"
        }
    }
    
    # 縣市與小吃對應關係
    county_mapping = {
        "基隆市": ["鼎邊銼", "天婦羅", "營養三明治"],
        "台北市": ["蚵仔煎", "牛肉麵", "滷肉飯"],
        "台南市": ["擔仔麵", "牛肉湯", "碗粿"],
        "彰化縣": ["肉圓", "爌肉飯", "貓鼠麵"]
    }
    
    return pd.DataFrame(summary_data), formula_db, county_mapping

df_summary, formula_db, county_mapping = get_extended_db()

# --- UI 介面實作 ---

# 3. 左側側邊欄 (Sidebar)
st.sidebar.header("🗺️ 研發篩選器")

# 第一層：選擇縣市
selected_county = st.sidebar.selectbox("1. 選擇縣市", df_summary["縣市"])

# 第二層：選擇該縣市的代表小吃 (下拉式選項)
available_snacks = county_mapping.get(selected_county, ["資料待補"])
selected_snack = st.sidebar.selectbox(f"2. {selected_county} 代表小吃", available_snacks)

st.sidebar.divider()
st.sidebar.caption("TAD-AGE System v3.0")

# 4. 右側主畫面
st.title(f"小吃研發模擬：{selected_snack}")

col_detail, col_radar = st.columns([1, 1.2])

with col_detail:
    st.subheader("🧪 風味結構解構 (Formula Card)")
    
    # 取得小吃配方資料
    recipe = formula_db.get(selected_snack, {
        "君": "待補充", "臣": "待補充", "佐": "待補充", "使": "待補充", "炮製": "資料庫更新中..."
    })
    
    # 運用 HTML 樣式美化君臣佐使顯示
    st.markdown(f"""
    * **【君】主題核心：** {recipe['君']}
    * **【臣】中段支撐：** {recipe['臣']}
    * **【佐】修飾平衡：** {recipe['佐']}
    * **【使】導向收尾：** {recipe['使']}
    """)
    
    with st.expander("👨‍🍳 炮製料理方法 (Process)", expanded=True):
        st.write(recipe['炮製'])

with col_radar:
    # 5. 右側雷達圖：顯示縣市風味基準線
    st.subheader(f"📊 {selected_county} 風味基準")
    
    county_stats = df_summary[df_summary["縣市"] == selected_county].iloc[0]
    
    radar_df = pd.DataFrame(dict(
        r=[county_stats['平均主題'], county_stats['平均支撐'], county_stats['平均修飾'], 
           county_stats['平均清亮'], county_stats['平均收尾']],
        theta=['主題', '支撐', '修飾', '清亮', '收尾']
    ))
    
    fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#E63946', fillcolor='rgba(230, 57, 70, 0.3)')
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.info("💡 研發筆記：此平台的結構能協助開發者快速掌握『風味骨架』，並根據區域特徵調整配方。")