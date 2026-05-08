import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃全台研發平台", layout="wide")

# 2. 深度研發資料庫 (已針對重點縣市進行實作級優化)
@st.cache_data
def load_pro_snack_db():
    # 22 縣市與小吃清單 (補齊全台)
    counties = [
        "基隆市", "台北市", "新北市", "桃園市", "新竹市", "新竹縣", "苗栗縣", "台中市", "彰化縣", "南投縣",
        "雲林縣", "嘉義市", "嘉義縣", "台南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "台東縣", "澎湖縣",
        "金門縣", "連江縣"
    ]
    
    snack_mapping = {
        "基隆市": ["鼎邊銼", "天婦羅", "營養三明治", "豆乾包", "泡泡冰"],
        "台北市": ["蚵仔煎", "牛肉麵", "滷肉飯", "刈包", "生煎包"],
        "嘉義市": ["火雞肉飯", "美乃滋涼麵", "砂鍋魚頭", "豆花", "米糕"],
        "台南市": ["碗粿", "蝦仁飯", "擔仔麵", "牛肉湯", "鱔魚意麵"],
        "彰化縣": ["肉圓", "爌肉飯", "貓鼠麵", "糯米炸", "蛤仔麵"],
        "連江縣": ["老酒麵線", "繼光餅", "紅糟肉", "魚麵", "鼎邊糊"]
        # 其他縣市以此類推...
    }

    # 深度實作資料 (君臣佐使 + 人性化步驟)
    detail_db = {
        "碗粿": {
            "君": "舊在來米漿 (混入肉燥汁)", "臣": "鹹蛋黃、香菇、瘦肉塊", "佐": "火燒蝦、紅蔥頭", "使": "蒜泥甜油膏",
            "steps": ["1. **磨漿**：選用舊米磨漿，加入熱水與滷汁調成褐色糊狀。", "2. **炒餡**：豬油爆香紅蔥頭與火燒蝦，加入香菇肉塊。", "3. **炊蒸**：碗底放餡填漿，大火蒸25分鐘。", "4. **靜置**：冷卻回溫是Q彈關鍵，表面微凹為正宗。"]
        },
        "鼎邊銼": {
            "君": "現磨在來米漿片", "臣": "肉羹、花枝羹", "佐": "金針、香菇、蝦米", "使": "芹菜、油蔥酥、白胡椒",
            "steps": ["1. **燙麵皮**：米漿沿大鍋邊緣澆淋，受熱成片後撕下。", "2. **熬湯**：以蝦米、香菇熬出清甜海鮮底湯。", "3. **合煮**：放入米漿片與雙羹，快速燙熟保持口感。", "4. **提香**：最後撒上芹菜與大量白胡椒提氣。"]
        },
        "火雞肉飯": {
            "君": "本地火雞肉絲/片", "臣": "西螺米飯", "佐": "手工炸油蔥酥", "使": "煉製火雞油、陳年醬油",
            "steps": ["1. **燜肉**：火雞慢火燜熟，保留肉汁並手撕成絲。", "2. **煉油**：以火雞脂肪慢火煉製純油，加入紅蔥頭酥。", "3. **調醬**：醬油與少許冰糖、雞湯熬成鹹甜適中的澆頭。", "4. **組合**：米飯需粒粒分明，依序淋油、醬、肉。"]
        },
        "蚵仔煎": {
            "君": "鮮蚵 (東石/布袋)", "臣": "雞蛋、地瓜粉/太白粉漿", "佐": "小白菜、茼蒿", "使": "味噌甜辣醬",
            "steps": ["1. **煎蚵**：平底鍋下油，先將鮮蚵煎至縮水釋放鮮味。", "2. **勾芡**：倒入比例精確的粉漿，打入雞蛋增加支撐。", "3. **包覆**：放入青菜，待粉漿邊緣焦脆後翻面。", "4. **淋醬**：搭配偏紅的甜辣醬，平衡油膩感。"]
        }
    }
    
    return counties, snack_mapping, detail_db

counties, snack_mapping, detail_db = load_pro_snack_db()

# --- UI 開始 ---
st.title("🇹🇼 TAD-AGE 台灣小吃全台研發平台 V4.0")

# 3. 側邊欄
st.sidebar.header("🧭 導覽中心")
selected_county = st.sidebar.selectbox("1. 選擇縣市", counties, index=counties.index("台南市"))

available_snacks = snack_mapping.get(selected_county, ["資料開發中"])
selected_snack = st.sidebar.selectbox(f"2. {selected_county} 代表小吃", available_snacks)

# 4. 主畫面佈局
col_info, col_radar = st.columns([1.2, 1])

with col_info:
    st.header(f"🗂️ 風味模擬卡：{selected_snack}")
    
    # 取得資料，若無則顯示預設
    data = detail_db.get(selected_snack, {
        "君": "主食材", "臣": "支撐配料", "佐": "調味層次", "使": "收尾引導",
        "steps": ["1. 準備食材", "2. 依照傳統工藝處理", "3. 進行風味調度", "4. 擺盤完成"]
    })
    
    st.subheader("🧪 風味解構 (Structure)")
    st.info(f"""
    * **【君】核心主味：** `{data['君']}`
    * **【臣】中段支撐：** `{data['臣']}`
    * **【佐】修飾平衡：** `{data['佐']}`
    * **【使】風味導向：** `{data['使']}`
    """)
    
    st.subheader("👨‍🍳 研發實作步驟 (Method)")
    for step in data['steps']:
        st.markdown(step)

with col_radar:
    st.header("📊 風味雷達圖")
    # 模擬數值 (實際開發可串接 CountySummary.csv)
    radar_df = pd.DataFrame(dict(
        r=[4.5, 4.0, 3.5, 2.5, 4.0],
        theta=['主題', '支撐', '修飾', '清亮', '收尾']
    ))
    fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#E63946', fillcolor='rgba(230, 57, 70, 0.3)')
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.info("💡 **我們還需要收集什麼資料？**\n為了讓剩下的小吃也達到這種深度，我們需要：\n1. **《核心工藝清單》**：各小吃的具體烹飪溫度、時間或特定手法。\n2. **《精準食材表》**：例如特定品種的米、特定來源的醬油。\n3. **《風味異常提醒》**：研發時常見的失敗點（例如：火候過大導致苦味）。")