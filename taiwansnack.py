import streamlit as st
import plotly.graph_objects as go

# --- 1. 完整資料庫：22 縣市 x 5 項代表小吃 (共 110 筆) ---
SNACK_DB = {
    "基隆市": {
        "營養三明治": {"star": 0, "bib": True, "flavor": [4,3,4,2,3], "desc": "高溫油炸麵包配上特調美乃滋"},
        "鼎邊趖": {"star": 0, "bib": False, "flavor": [3,4,3,4,2], "desc": "在鍋邊滾動形成的米漿皮"},
        "天婦羅": {"star": 0, "bib": False, "flavor": [4,4,3,2,3], "desc": "鮮魚漿手作，酥炸Q彈"},
        "泡泡冰": {"star": 0, "bib": False, "flavor": [5,2,2,4,4], "desc": "綿密細緻的傳統冰品"},
        "紅燒鰻魚羹": {"star": 0, "bib": True, "flavor": [5,4,4,2,4], "desc": "厚實鰻魚塊與濃郁湯頭"}
    },
    "台北市": {
        "牛肉麵": {"star": 1, "bib": False, "flavor": [5,5,4,3,4], "desc": "紅燒湯頭與軟嫩牛腱肉"},
        "滷肉飯": {"star": 0, "bib": True, "flavor": [5,4,3,2,4], "desc": "手切肥而不膩的滷肉"},
        "小籠包": {"star": 1, "bib": False, "flavor": [4,4,5,3,3], "desc": "皮薄多汁，內餡鮮甜"},
        "蚵仔麵線": {"star": 0, "bib": True, "flavor": [4,4,3,2,5], "desc": "柴魚高湯與特製大腸蚵仔"},
        "雞肉飯": {"star": 0, "bib": False, "flavor": [4,3,3,4,3], "desc": "鮮嫩雞肉片淋上雞油香"}
    },
    "新北市": {
        "深坑豆腐": {"star": 0, "bib": True, "flavor": [4,4,3,2,5], "desc": "獨特焦香味，層次分明"},
        "淡水阿給": {"star": 0, "bib": False, "flavor": [3,5,3,2,3], "desc": "油豆腐塞入粉絲與特製醬汁"},
        "九份芋圓": {"star": 0, "bib": False, "flavor": [5,3,2,4,3], "desc": "手作Q彈，濃濃芋頭香"},
        "油飯": {"star": 0, "bib": True, "flavor": [4,4,4,2,3], "desc": "麻油香與長糯米的完美結合"},
        "肉粽": {"star": 0, "bib": False, "flavor": [4,5,3,2,3], "desc": "南北口味各異，內餡豐富"}
    },
    "桃園市": {
        "大溪豆乾": {"star": 0, "bib": False, "flavor": [3,4,4,2,3], "desc": "陳年滷汁透心香"},
        "石門活魚": {"star": 0, "bib": False, "flavor": [5,4,3,3,4], "desc": "現撈鮮魚多吃法"},
        "龍岡米干": {"star": 0, "bib": True, "flavor": [4,4,3,3,5], "desc": "滇緬風味純米製麵"},
        "客家小炒": {"star": 0, "bib": False, "flavor": [5,4,4,2,3], "desc": "五花肉、豆乾、魷魚交織"},
        "花生糖": {"star": 0, "bib": False, "flavor": [5,2,2,3,3], "desc": "龍潭名產，香脆不沾牙"}
    },
    "新竹縣": {
        "仙草雞": {"star": 0, "bib": True, "flavor": [5,4,3,3,4], "desc": "在地仙草與土雞慢火燉煮"},
        "粄條": {"star": 0, "bib": False, "flavor": [4,3,4,2,3], "desc": "純米手作，口感紮實"},
        "擂茶": {"star": 0, "bib": False, "flavor": [5,4,3,2,5], "desc": "多種穀物研磨而成"},
        "菜包": {"star": 0, "bib": False, "flavor": [3,5,4,2,3], "desc": "客家大菜包，皮Q餡香"},
        "柿餅": {"star": 0, "bib": False, "flavor": [5,2,2,3,4], "desc": "天然風乾，清甜回甘"}
    },
    "新竹市": {
        "貢丸湯": {"star": 0, "bib": False, "flavor": [4,4,3,3,2], "desc": "紮實豬肉搥打，彈牙多汁"},
        "炒米粉": {"star": 0, "bib": False, "flavor": [4,3,4,3,3], "desc": "新竹風強催出的韌性米粉"},
        "潤餅": {"star": 0, "bib": True, "flavor": [3,4,5,3,4], "desc": "配料豐富，獨特花生粉"},
        "肉圓": {"star": 0, "bib": False, "flavor": [4,5,4,2,3], "desc": "紅糟肉餡，外皮Q軟"},
        "水蒸蛋糕": {"star": 0, "bib": False, "flavor": [3,2,2,4,4], "desc": "古法水蒸，濕潤清爽"}
    },
    "苗栗縣": {
        "水晶餃": {"star": 0, "bib": False, "flavor": [3,5,3,2,3], "desc": "皮Q餡香的客家特色"},
        "油蔥酥麵": {"star": 0, "bib": False, "flavor": [4,4,3,2,4], "desc": "自製油蔥香氣撲鼻"},
        "鹽焗雞": {"star": 0, "bib": False, "flavor": [5,3,2,3,4], "desc": "肉質鮮嫩，原汁原味"},
        "麻糬": {"star": 0, "bib": False, "flavor": [5,2,2,3,3], "desc": "傳統客家粢粑"},
        "酸菜鴨": {"star": 0, "bib": False, "flavor": [4,4,4,3,5], "desc": "自家醃漬酸菜，鮮甜開胃"}
    },
    "台中市": {
        "太陽餅": {"star": 0, "bib": False, "flavor": [5,3,3,4,4], "desc": "麥芽糖與千層酥皮"},
        "肉圓": {"star": 0, "bib": True, "flavor": [4,5,4,2,4], "desc": "淋上特製白醬與甜辣醬"},
        "麻薏湯": {"star": 0, "bib": False, "flavor": [3,3,4,5,4], "desc": "台中特有消暑聖品"},
        "大麵羹": {"star": 0, "bib": False, "flavor": [3,5,3,2,4], "desc": "特有鹼味粗麵條"},
        "鳳梨酥": {"star": 0, "bib": False, "flavor": [5,3,3,3,4], "desc": "金黃酥皮包裹冬瓜鳳梨餡"}
    },
    "彰化縣": {
        "爌肉飯": {"star": 0, "bib": True, "flavor": [5,5,3,2,4], "desc": "軟Q豬腳或爌肉搭配白飯"},
        "肉圓": {"star": 0, "bib": True, "flavor": [4,5,4,2,4], "desc": "低溫油泡，北斗或彰化派"},
        "貓鼠麵": {"star": 0, "bib": False, "flavor": [3,4,3,4,3], "desc": "清甜大骨蛤蜊湯頭"},
        "糯米炸": {"star": 0, "bib": False, "flavor": [5,2,2,3,3], "desc": "現炸Q軟沾花生粉"},
        "蛤仔麵": {"star": 0, "bib": False, "flavor": [4,4,3,5,4], "desc": "鮮甜蛤蜊肉鋪滿麵條"}
    },
    "南投縣": {
        "意麵": {"star": 0, "bib": False, "flavor": [3,4,3,3,3], "desc": "鹼水麵條搭配特製肉燥"},
        "肉圓": {"star": 0, "bib": False, "flavor": [4,5,4,2,3], "desc": "水里特色，吃完留皮加湯"},
        "扣仔嗲": {"star": 0, "bib": False, "flavor": [4,4,4,2,2], "desc": "現炸韭菜與肉餡炸餅"},
        "竹筒飯": {"star": 0, "bib": False, "flavor": [4,3,2,4,4], "desc": "帶有竹膜香氣的糯米"},
        "紹興米糕": {"star": 0, "bib": False, "flavor": [5,4,3,2,4], "desc": "埔里特色酒香米糕"}
    },
    "雲林縣": {
        "當歸鴨": {"star": 0, "bib": True, "flavor": [5,4,3,3,4], "desc": "中藥香氣與軟嫩鴨肉"},
        "鵝肉": {"star": 0, "bib": True, "flavor": [5,4,3,3,4], "desc": "產地直送，鮮甜多汁"},
        "肉羹": {"star": 0, "bib": False, "flavor": [4,4,4,2,3], "desc": "獨特醬油湯頭風味"},
        "魷魚嘴羹": {"star": 0, "bib": False, "flavor": [4,4,3,2,3], "desc": "嚼勁十足的魷魚嘴"},
        "咖啡": {"star": 0, "bib": False, "flavor": [5,3,4,5,5], "desc": "古坑產地特色風味"}
    },
    "嘉義縣": {
        "火雞肉飯": {"star": 0, "bib": True, "flavor": [5,4,3,3,3], "desc": "正宗火雞肉與雞油香"},
        "新港飴": {"star": 0, "bib": False, "flavor": [5,2,2,3,3], "desc": "傳統Q軟花生軟糖"},
        "鴨肉羹": {"star": 0, "bib": True, "flavor": [4,5,4,2,4], "desc": "鑊氣十足的濃郁羹湯"},
        "奮起湖便當": {"star": 0, "bib": False, "flavor": [4,4,3,2,3], "desc": "山區鐵路懷舊風味"},
        "苦茶油雞": {"star": 0, "bib": False, "flavor": [5,4,3,2,4], "desc": "溫潤苦茶油煸薑香"}
    },
    "嘉義市": {
        "美乃滋涼麵": {"star": 0, "bib": False, "flavor": [4,3,5,3,2], "desc": "獨門白醋配寬麵"},
        "砂鍋魚頭": {"star": 0, "bib": True, "flavor": [5,5,4,2,4], "desc": "濃郁沙茶與炸魚頭"},
        "豆花": {"star": 0, "bib": False, "flavor": [4,2,2,4,4], "desc": "搭配豆漿底的傳統美味"},
        "葡萄柚綠": {"star": 0, "bib": False, "flavor": [5,2,3,5,5], "desc": "滿滿果肉的特色飲品"},
        "火雞肉飯(市)": {"star": 0, "bib": False, "flavor": [5,4,3,3,3], "desc": "各家自有獨門配方"}
    },
    "台南市": {
        "牛肉湯": {"star": 0, "bib": True, "flavor": [5,3,2,4,5], "desc": "溫體牛現燙，鮮美甘甜"},
        "碗粿": {"star": 0, "bib": True, "flavor": [4,4,3,2,4], "desc": "中心包肉，口感紮實"},
        "鱔魚意麵": {"star": 0, "bib": True, "flavor": [5,4,5,3,4], "desc": "酸甜適口，鑊氣濃郁"},
        "擔仔麵": {"star": 0, "bib": False, "flavor": [3,4,4,3,3], "desc": "經典肉燥與一尾蝦"},
        "蝦捲": {"star": 0, "bib": False, "flavor": [4,4,3,3,3], "desc": "鮮蝦與網油炸出酥脆"}
    },
    "高雄市": {
        "鴨肉飯": {"star": 0, "bib": False, "flavor": [4,4,3,3,4], "desc": "煙燻鴨肉與特製滷汁"},
        "白糖粿": {"star": 0, "bib": False, "flavor": [5,2,2,3,3], "desc": "現炸糯米裹糖粉"},
        "岡山羊肉": {"star": 0, "bib": False, "flavor": [5,4,4,2,3], "desc": "豆瓣醬調味與新鮮羊肉"},
        "旗津海產": {"star": 0, "bib": False, "flavor": [5,3,3,4,4], "desc": "現捕海鮮，原味呈現"},
        "牛肉火鍋": {"star": 0, "bib": True, "flavor": [5,4,3,3,5], "desc": "南部鮮甜溫體牛火鍋"}
    },
    "屏東縣": {
        "萬丹紅豆餅": {"star": 0, "bib": False, "flavor": [5,3,2,4,3], "desc": "皮薄餡多，紅豆香濃"},
        "豬腳": {"star": 0, "bib": False, "flavor": [5,5,3,2,4], "desc": "萬巒特色，Q彈不膩"},
        "黑鮪魚": {"star": 0, "bib": False, "flavor": [5,3,2,4,5], "desc": "東港之寶，鮮甜入口即化"},
        "旗魚黑輪": {"star": 0, "bib": False, "flavor": [4,3,3,3,3], "desc": "魚漿包蛋，現炸美味"},
        "燒冷冰": {"star": 0, "bib": False, "flavor": [5,3,2,4,4], "desc": "熱配料與冷挫冰的衝擊"}
    },
    "宜蘭縣": {
        "肉羹": {"star": 0, "bib": False, "flavor": [4,4,4,2,3], "desc": "蒜味濃郁，湯頭勾芡"},
        "三星蔥餅": {"star": 0, "bib": False, "flavor": [5,4,3,2,2], "desc": "香氣爆發的三星蔥"},
        "卜肉": {"star": 0, "bib": False, "flavor": [4,4,3,3,3], "desc": "特製醃肉，酥炸脆香"},
        "糕渣": {"star": 0, "bib": False, "flavor": [3,4,5,2,4], "desc": "外冷內燙，雞湯結晶"},
        "鴨賞": {"star": 0, "bib": False, "flavor": [5,4,4,2,4], "desc": "古法煙燻，嚼勁十足"}
    },
    "花蓮縣": {
        "扁食": {"star": 0, "bib": False, "flavor": [4,3,3,3,3], "desc": "皮薄餡鮮，清爽湯頭"},
        "炸蛋蔥油餅": {"star": 0, "bib": False, "flavor": [5,4,3,2,2], "desc": "半熟蛋流出與酥脆餅皮"},
        "公正包子": {"star": 0, "bib": False, "flavor": [4,4,3,2,3], "desc": "麵皮帶甜，肉餡紮實"},
        "麻糬": {"star": 0, "bib": False, "flavor": [5,2,2,3,3], "desc": "花蓮名產，Q軟多種口味"},
        "剝皮辣椒": {"star": 0, "bib": False, "flavor": [5,3,4,4,5], "desc": "辛辣鮮甜，開胃聖品"}
    },
    "台東縣": {
        "米苔目": {"star": 0, "bib": False, "flavor": [3,4,4,2,3], "desc": "柴魚片灑滿，Q彈麵條"},
        "卑南包子": {"star": 0, "bib": False, "flavor": [4,4,3,2,3], "desc": "排隊名店，個頭碩大"},
        "豬血湯": {"star": 0, "bib": False, "flavor": [4,4,4,3,3], "desc": "大骨湯頭與新鮮豬血"},
        "地瓜酥": {"star": 0, "bib": False, "flavor": [5,2,2,3,4], "desc": "薄脆沾糖漿，停不下來"},
        "原住民石板烤肉": {"star": 0, "bib": False, "flavor": [5,4,3,2,4], "desc": "石板煎烤，香氣四溢"}
    },
    "澎湖縣": {
        "黑糖糕": {"star": 0, "bib": False, "flavor": [5,2,2,3,4], "desc": "鬆軟Q彈，黑糖香氣"},
        "仙人掌冰": {"star": 0, "bib": False, "flavor": [5,2,4,5,5], "desc": "獨特酸甜紫紅色冰品"},
        "小管麵線": {"star": 0, "bib": False, "flavor": [4,3,2,4,5], "desc": "產地鮮甜，小管清脆"},
        "土魠魚羹": {"star": 0, "bib": False, "flavor": [4,4,4,2,3], "desc": "魚塊鮮甜，羹湯適口"},
        "炸棗": {"star": 0, "bib": False, "flavor": [4,3,3,2,3], "desc": "喜慶點心，外酥內軟"}
    },
    "金門縣": {
        "廣東粥": {"star": 0, "bib": False, "flavor": [4,5,3,2,4], "desc": "煮到看不見米粒的糜粥"},
        "油條": {"star": 0, "bib": False, "flavor": [4,3,2,3,2], "desc": "紮實口感，粥品最佳拍檔"},
        "貢糖": {"star": 0, "bib": False, "flavor": [5,2,2,3,3], "desc": "花生香濃，酥脆可口"},
        "炒泡麵": {"star": 0, "bib": False, "flavor": [4,4,4,2,3], "desc": "軍旅回憶，配料豐富"},
        "蚵嗲": {"star": 0, "bib": False, "flavor": [4,4,3,2,2], "desc": "滿滿石蚵，現炸酥香"}
    },
    "連江縣": {
        "繼光餅": {"star": 0, "bib": False, "flavor": [4,4,2,2,3], "desc": "馬祖貝果，芝麻香氣"},
        "紅糟肉": {"star": 0, "bib": False, "flavor": [5,4,4,2,4], "desc": "紅糟醃漬，獨特酒香"},
        "魚麵": {"star": 0, "bib": False, "flavor": [4,4,3,3,4], "desc": "魚漿製麵，鮮味濃郁"},
        "老酒麵線": {"star": 0, "bib": False, "flavor": [5,4,3,3,5], "desc": "香醇老酒與麻油蛋"},
        "淡菜": {"star": 0, "bib": False, "flavor": [5,3,2,4,5], "desc": "馬祖特產，肥美多汁"}
    }
}

# --- 2. 介面與 CSS 樣式 ---
st.set_page_config(page_title="TAD-AGE 平台 V3", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #1E1E1E; margin-bottom: 20px; }
    .michelin-tag { background-color: #E60012; color: white; padding: 4px 15px; border-radius: 20px; font-weight: bold; }
    .bib-tag { background-color: #F0F2F6; color: #1E1E1E; padding: 4px 15px; border-radius: 20px; border: 1px solid #CCC; font-weight: bold; }
    .stSelectbox label { font-size: 1.1rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 側邊導覽 ---
with st.sidebar:
    st.header("🧭 導覽中心")
    selected_city = st.selectbox("1. 選擇縣市", list(SNACK_DB.keys()), index=4) # 預設新竹縣
    
    snack_list = list(SNACK_DB[selected_city].keys())
    
    def snack_formatter(name):
        info = SNACK_DB[selected_city][name]
        icon = " ⭐" if info["star"] > 0 else (" 😋" if info["bib"] else "")
        return f"{name}{icon}"
        
    selected_snack = st.selectbox("2. 代表小吃", snack_list, format_func=snack_formatter)
    data = SNACK_DB[selected_city][selected_snack]

# --- 4. 主畫面渲染 ---
st.markdown(f'<div class="main-title">🍜 TAD-AGE 台灣小吃風味平台 V3</div>', unsafe_allow_html=True)

# 顯示標題與獲獎標籤
col_title, col_tags = st.columns([1, 1])
with col_title:
    st.subheader(f"風味模擬卡：{selected_snack}")

with col_tags:
    st.write("") # 垂直間距
    tags_html = ""
    if data["star"] > 0:
        tags_html += f'<span class="michelin-tag">MICHELIN ⭐ {data["star"]}</span> '
    if data["bib"]:
        tags_html += '<span class="bib-tag">Bib Gourmand 😋</span>'
    st.markdown(tags_html, unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns([4, 6])

with col1:
    st.markdown("### 🧱 結構解構")
    st.markdown(f"**【君】核心主味**：{data['desc']}")
    st.markdown(f"**【臣】中段支撐**：骨架食材 (強度: {data['flavor'][1]})")
    st.markdown(f"**【佐】修飾平衡**：提升層次 (強度: {data['flavor'][2]})")
    st.markdown(f"**【使】風味導向**：收尾留香 (強度: {data['flavor'][4]})")
    
    with st.expander("🍳 核心工藝 (炮製方法)", expanded=True):
        st.info(f"針對『{selected_snack}』的傳統作法，需注重火候控管與投料順序。建議依據該地區的【清亮】與【收尾】比值進行微調。")

with col2:
    # 雷達圖繪製
    categories = ['主題 (Theme)', '支撐 (Body)', '修飾 (Balance)', '清亮 (Bright)', '收尾 (Finish)']
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=data['flavor'] + [data['flavor'][0]],
        theta=categories + [categories[0]],
        fill='toself',
        line_color='#E64A19',
        fillcolor='rgba(230, 74, 25, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False,
        height=450,
        margin=dict(l=60, r=60, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# 頁尾統計資訊
st.sidebar.markdown("---")
st.sidebar.caption(f"已載入全台 22 縣市共 {len(SNACK_DB) * 5} 筆小吃資料。")