import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃研發平台 V3", layout="wide")

# 2. 建立全台 22 縣市完整研發資料庫 (內含食材對應)
@st.cache_data
def load_comprehensive_taiwan_db():
    # 22 縣市小吃清單 (補齊所有缺失)
    snack_db = {
        "基隆市": ["鼎邊銼", "天婦羅", "營養三明治", "豆乾包", "泡泡冰"],
        "台北市": ["蚵仔煎", "牛肉麵", "滷肉飯", "刈包", "生煎包"],
        "新北市": ["阿給", "深坑臭豆腐", "九份芋圓", "金山鴨肉", "鶯歌壽司"],
        "桃園市": ["大溪豆乾", "龍岡米干", "石門活魚", "潤餅", "排骨飯"],
        "新竹市": ["貢丸湯", "米粉", "水蒸蛋糕", "潤餅", "肉圓"],
        "新竹縣": ["粄條", "仙草雞", "擂茶", "菜包", "柿餅"],
        "苗栗縣": ["水晶餃", "客家小炒", "麻糬", "薑絲大腸", "煨湯"],
        "台中市": ["太陽餅", "大腸包小腸", "炒麵", "台中肉員", "麻薏湯"],
        "彰化縣": ["肉圓", "爌肉飯", "貓鼠麵", "糯米炸", "蛤仔麵"],
        "南投縣": ["意麵", "肉圓", "竹筒飯", "扣仔嗲", "茶梅"],
        "雲林縣": ["鵝肉", "鴨肉飯", "圓仔冰", "當歸鴨", "肉羹"],
        "嘉義市": ["火雞肉飯", "美乃滋涼麵", "砂鍋魚頭", "豆花", "米糕"],
        "嘉義縣": ["民雄鵝肉", "奮起湖便當", "東石蚵仔", "苦茶油雞", "黑根"],
        "台南市": ["蝦仁飯", "擔仔麵", "牛肉湯", "碗粿", "鱔魚意麵"],
        "高雄市": ["鍋燒意麵", "海鮮粥", "旗魚黑輪", "鴨肉珍", "烤黑輪"],
        "屏東縣": ["萬巒豬腳", "肉粿", "黑鮪魚", "冷熱冰", "粄條"],
        "宜蘭縣": ["肉羹", "蔥油餅", "糕渣", "卜肉", "鴨賞"],
        "花蓮縣": ["液香扁食", "炸蛋蔥油餅", "公正包子", "麻糬", "周家蒸餃"],
        "台東縣": ["卑南肉包", "米苔目", "豬血湯", "地瓜酥", "池上便當"],
        "澎湖縣": ["仙人掌冰", "黑糖糕", "小管麵線", "金瓜米粉", "花枝丸"],
        "金門縣": ["廣東粥", "燒餅", "貢糖", "油條", "炒泡麵"],
        "連江縣": ["老酒麵線", "繼光餅", "紅糟肉", "魚麵", "鼎邊糊"]
    }
    
    # 核心配方資料庫 (食材對應)
    formula_detail = {
        "蝦仁飯": {"君": "火燒蝦仁", "臣": "鰹魚高湯/米飯", "佐": "柴魚醬油/青蔥", "使": "豬油/糖"},
        "鼎邊銼": {"君": "海鮮高湯", "臣": "米漿片/肉羹", "佐": "白胡椒/蒜酥", "使": "芹菜/油蔥"},
        "蚵仔煎": {"君": "鮮蚵", "臣": "雞蛋/地瓜粉水", "佐": "小白菜/蒜泥", "使": "特製甜辣醬"},
        "肉圓": {"君": "豬肉內餡", "臣": "地瓜粉外皮", "佐": "筍丁/五香粉", "使": "白醬/甜辣醬"},
        "火雞肉飯": {"君": "火雞肉絲", "臣": "白飯", "佐": "油蔥酥/醬油", "使": "火雞油"},
        "老酒麵線": {"君": "馬祖老酒", "臣": "細麵線/荷包蛋", "佐": "老薑/紅糟", "使": "麻油"},
        "萬巒豬腳": {"君": "豬後蹄", "臣": "中藥滷汁", "佐": "特製蒜蓉醬", "使": "滷油香氣"}
    }
    
    # 模擬 22 縣市風味分數
    counties = list(snack_db.keys())
    scores = {c: [4.5, 3.8, 3.2, 2.8, 3.5] for c in counties} # 預設分數
    scores["台南市"] = [5.0, 4.5, 4.0, 2.0, 5.0] # 甜度與收尾強
    scores["台北市"] = [5.0, 4.0, 3.4, 2.2, 4.0]
    
    return snack_db, formula_detail, scores

snack_db, formula_db, score_db = load_comprehensive_taiwan_db()

# --- UI 開始 ---
st.title("🇹🇼 TAD-AGE 台灣小吃研發平台 V3.5")

# 3. 左側側邊欄
st.sidebar.header("🧭 導覽中心")
selected_county = st.sidebar.selectbox("1. 選擇縣市", list(snack_db.keys()))

available_snacks = snack_db.get(selected_county, [])
selected_snack = st.sidebar.selectbox(f"2. {selected_county} 代表小吃", available_snacks)

st.sidebar.divider()
st.sidebar.success(f"已加載 {selected_county} 的 5 項核心小吃數據。")

# 4. 右側主畫面
col_info, col_radar = st.columns([1, 1.2])

with col_info:
    st.header(f"🗂️ 風味模擬卡：{selected_snack}")
    
    # 取得食材對應資料
    recipe = formula_db.get(selected_snack, {"君": "在地主料", "臣": "結構配材", "佐": "調味層次", "使": "導向收尾"})
    
    st.subheader("🧪 風味解構 (Structure)")
    # 此處將食材名稱與君臣佐使結合
    st.markdown(f"""
    * **【君】核心主味：** `{recipe['君']}` (主題識別)
    * **【臣】中段支撐：** `{recipe['臣']}` (飽滿骨架)
    * **【佐】修飾平衡：** `{recipe['佐']}` (層次優化)
    * **【使】風味導向：** `{recipe['使']}` (導向收尾)
    """)
    
    with st.expander("👨‍🍳 研發實作步驟 (Method)", expanded=True):
        st.write(f"1. 處理主食材 **{recipe['君']}**，確保鮮度與風味完整。")
        st.write(f"2. 以 **{recipe['臣']}** 建立厚度，維持口感穩定。")
        st.write(f"3. 加入 **{recipe['佐']}** 進行去腥與提鮮。")
        st.write(f"4. 最後由 **{recipe['使']}** 決定風味走向，確保收尾留香。")

with col_radar:
    st.header("📊 風味雷達圖 (縣市基準)")
    # 取得縣市分數
    s_vals = score_db.get(selected_county, [4, 4, 3, 3, 3])
    
    radar_df = pd.DataFrame(dict(
        r=s_vals,
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
st.caption("技術底層：TAD-AGE Engine | 全台 22 縣市小吃模組已補齊")