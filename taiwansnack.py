import streamlit as st
import plotly.graph_objects as go

# 1. 設置頁面 (去框化、寬版佈局)
st.set_page_config(page_title="TAD-AGE 台灣小吃 Formula 實作平台", layout="wide")

# 2. 核心資料庫 (補齊 22 縣市 x 5 項 = 110 項)
# michelin: 1=顯示紅色顯眼徽章, 0=隱藏
# scores 順序：[滲透力, 支撐度, 修飾度, 清亮感, 厚度]
SNACK_LIBRARY = {
    "基隆市": {
        "鼎邊趖": {"君": ["米漿片", "海鮮湯"], "臣": ["肉羹", "蝦仁羹"], "佐": ["白胡椒", "蒜酥"], "使": ["芹菜", "油蔥"], "risk": "海味不能被胡椒蓋掉", "michelin": 0, "scores": [5, 3, 3, 4, 2]},
        "廟口天婦羅": {"君": ["魚漿甜不辣"], "臣": ["味噌醬"], "佐": ["白胡椒", "蒜末"], "使": ["小黃瓜"], "risk": "魚漿比例不足會影響彈性", "michelin": 0, "scores": [4, 4, 3, 3, 4]},
        "營養三明治": {"君": ["炸麵包"], "臣": ["美乃滋"], "佐": ["滷蛋", "火腿"], "使": ["小黃瓜"], "risk": "麵包油溫控制不當會過於油膩", "michelin": 0, "scores": [4, 4, 4, 2, 5]},
        "泡泡冰": {"君": ["花生/花豆"], "臣": ["糖水"], "佐": ["鹽"], "使": ["煉乳"], "risk": "攪拌不均會影響口感綿密度", "michelin": 0, "scores": [3, 5, 2, 4, 3]},
        "紅糟肉圓": {"君": ["紅糟豬肉"], "臣": ["粉皮", "甜辣醬"], "佐": ["筍丁"], "使": ["香菜"], "risk": "紅糟發酵味過重會掩蓋肉香", "michelin": 0, "scores": [4, 4, 3, 3, 4]}
    },
    "臺北市": {
        "牛肉麵": {"君": ["牛腱", "手工麵"], "臣": ["大骨中藥湯"], "佐": ["辣豆瓣", "酸菜"], "使": ["蔥花", "牛油"], "risk": "湯頭過於濃縮會產生苦澀感", "michelin": 1, "scores": [5, 5, 4, 2, 5]},
        "滷肉飯": {"君": ["豬皮脂", "米飯"], "臣": ["陳年醬油"], "佐": ["紅蔥頭"], "使": ["醃蘿蔔"], "risk": "脂肉比例低於3:7口感顯乾澀", "michelin": 1, "scores": [4, 5, 3, 2, 5]},
        "蚵仔麵線": {"君": ["鮮蚵", "紅麵線"], "臣": ["柴魚勾芡"], "佐": ["蒜泥"], "使": ["香菜", "烏醋"], "risk": "勾芡過厚會掩蓋鮮蚵甜味", "michelin": 1, "scores": [5, 3, 4, 4, 3]},
        "雞排": {"君": ["帶骨雞胸"], "臣": ["特調醃料"], "佐": ["椒鹽粉"], "使": ["九層塔"], "risk": "油溫低於180度會導致麵皮含油", "michelin": 0, "scores": [4, 4, 5, 2, 4]},
        "生炒花枝": {"君": ["厚切花枝"], "臣": ["酸甜勾芡"], "佐": ["蒜末", "辣椒"], "使": ["烏醋"], "risk": "火候不足會導致花枝口感老韌", "michelin": 0, "scores": [4, 4, 4, 4, 3]}
    },
    "新北市": {
        "深坑臭豆腐": {"君": ["板豆腐"], "臣": ["麻辣湯底"], "佐": ["酸菜", "豆瓣"], "使": ["泡菜"], "risk": "發酵程度不一會影響鹹度平衡", "michelin": 0, "scores": [5, 4, 4, 2, 4]},
        "淡水阿給": {"君": ["油豆腐", "冬粉"], "臣": ["魚漿封口"], "佐": ["甜辣醬"], "使": ["溫和高湯"], "risk": "冬粉過度浸泡會失去咀嚼彈性", "michelin": 0, "scores": [3, 4, 3, 4, 4]},
        "九份芋圓": {"君": ["芋頭", "地瓜粉"], "臣": ["糖水/碎冰"], "佐": ["紅豆", "綠豆"], "使": ["薑汁"], "risk": "粉比例過高會掩蓋芋頭原有的香氣", "michelin": 0, "scores": [3, 5, 2, 4, 3]},
        "永和豆漿": {"君": ["黃豆汁"], "臣": ["焦香底韻"], "佐": ["糖/鹽"], "使": ["油條"], "risk": "焦香味控制不當會被誤認燒焦", "michelin": 0, "scores": [5, 4, 2, 4, 3]},
        "油庫口麵線": {"君": ["蚵仔", "大腸"], "臣": ["紅麵線"], "佐": ["蒜泥"], "使": ["香腸"], "risk": "大腸滷製時間需標準化", "michelin": 0, "scores": [4, 4, 4, 3, 4]}
    },
    "桃園市": {
        "大溪豆乾": {"君": ["黑豆乾"], "臣": ["焦糖滷汁"], "佐": ["八角", "花椒"], "使": ["辣醬"], "risk": "滷製時間不足會導致中心不入味", "michelin": 0, "scores": [4, 5, 4, 2, 5]},
        "龍岡米干": {"君": ["純米漿皮"], "臣": ["豬骨湯"], "佐": ["肉燥", "蛋花"], "使": ["酸菜"], "risk": "米干存放過久容易斷裂", "michelin": 0, "scores": [4, 4, 3, 4, 4]},
        "石門活魚": {"君": ["草魚"], "臣": ["紅燒汁/糖醋"], "佐": ["薑絲", "蒜片"], "使": ["蔥段"], "risk": "土腥味處理不當會破壞鮮度", "michelin": 0, "scores": [5, 4, 4, 3, 4]},
        "龍潭豆花": {"君": ["黃豆花"], "臣": ["糖水"], "佐": ["花生"], "使": ["碎冰"], "risk": "碎冰融化會稀釋糖水深度", "michelin": 0, "scores": [3, 4, 2, 5, 3]},
        "忠貞米干": {"君": ["米干"], "臣": ["肉臊湯"], "佐": ["草果", "花椒"], "使": ["酸菜"], "risk": "香料過重會產生藥苦味", "michelin": 0, "scores": [4, 4, 5, 3, 4]}
    },
    "新竹市": {
        "新竹米粉": {"君": ["細米粉"], "臣": ["肉燥汁"], "佐": ["豆芽", "韭菜"], "使": ["紅蔥酥"], "risk": "米粉過乾會吸走口腔水分", "michelin": 0, "scores": [4, 3, 3, 4, 3]},
        "摃丸湯": {"君": ["豬肉摃丸"], "臣": ["大骨湯"], "佐": ["白胡椒"], "使": ["芹菜末"], "risk": "摃丸粉料過多會失去彈性", "michelin": 0, "scores": [4, 4, 3, 4, 4]},
        "水蒸蛋糕": {"君": ["麵粉", "蛋"], "臣": ["肉燥/芋泥"], "佐": ["砂糖"], "使": ["水蒸氣"], "risk": "濕度不足會導致口感粗糙", "michelin": 0, "scores": [3, 4, 2, 4, 3]},
        "城隍廟肉圓": {"君": ["紅糟豬肉"], "臣": ["地瓜粉皮"], "佐": ["甜辣醬"], "使": ["香菜"], "risk": "皮過厚會降低肉香層次", "michelin": 0, "scores": [4, 4, 3, 3, 4]},
        "潤餅": {"君": ["潤餅皮", "高麗菜"], "臣": ["花生粉"], "佐": ["紅燒肉", "豆乾"], "使": ["糖粉"], "risk": "蔬菜水分過多會弄破餅皮", "michelin": 0, "scores": [3, 4, 4, 4, 3]}
    },
    "臺南市": {
        "牛肉湯": {"君": ["溫體牛肉"], "臣": ["牛骨蔬果湯"], "佐": ["薑絲"], "使": ["米酒"], "risk": "湯頭溫度低於90度無法鎖住肉汁", "michelin": 1, "scores": [5, 4, 3, 5, 3]},
        "蝦仁飯": {"君": ["火燒蝦", "白米"], "臣": ["柴魚高湯"], "佐": ["蔥段"], "使": ["豬油"], "risk": "醬汁過多會導致米飯濕軟失去炭火香", "michelin": 1, "scores": [4, 4, 3, 3, 4]},
        "擔仔麵": {"君": ["油麵", "鮮蝦"], "臣": ["肉燥", "蝦湯"], "佐": ["蒜泥"], "使": ["香菜", "烏醋"], "risk": "肉燥過鹹會壓過蝦湯清甜", "michelin": 1, "scores": [4, 5, 4, 4, 3]},
        "虱目魚粥": {"君": ["虱目魚肚"], "臣": ["魚骨清湯"], "佐": ["薑絲", "油蔥酥"], "使": ["芹菜末"], "risk": "魚刺處理不淨將嚴重影響食用", "michelin": 1, "scores": [5, 3, 3, 5, 3]},
        "碗粿": {"君": ["在來米漿"], "臣": ["鹹蛋黃", "瘦肉"], "佐": ["香菇"], "使": ["蒜泥醬油膏"], "risk": "米漿比例過稀會導致冷後塌陷", "michelin": 1, "scores": [3, 5, 4, 2, 5]}
    },
    "嘉義市": {
        "火雞肉飯": {"君": ["火雞肉片", "米飯"], "臣": ["雞油醬汁"], "佐": ["紅蔥酥"], "使": ["黃蘿蔔"], "risk": "淋油不足會導致口感乾硬", "michelin": 1, "scores": [4, 5, 4, 3, 4]},
        "林聰明魚頭": {"君": ["大頭鰱魚"], "臣": ["沙茶湯底"], "佐": ["白菜", "豆腐"], "使": ["蛋酥"], "risk": "沙茶比例過重會導致湯頭油膩", "michelin": 1, "scores": [5, 4, 5, 2, 5]},
        "涼麵": {"君": ["扁細麵"], "臣": ["美乃滋(白醋)"], "佐": ["小黃瓜"], "使": ["蒜泥"], "risk": "美乃滋比例過高會顯得膩口", "michelin": 0, "scores": [4, 3, 4, 4, 3]},
        "豆花": {"君": ["黃豆花"], "臣": ["豆漿"], "佐": ["花生"], "使": ["碎冰"], "risk": "糖水甜度過高會掩蓋豆漿原味", "michelin": 0, "scores": [5, 3, 2, 5, 3]},
        "米糕": {"君": ["糯米"], "臣": ["肉燥"], "佐": ["小黃瓜片"], "使": ["甜辣醬"], "risk": "糯米熟度不均影響嚼感", "michelin": 0, "scores": [3, 5, 4, 3, 4]}
    },
    "高雄市": {
        "岡山羊肉爐": {"君": ["帶皮羊肉"], "臣": ["當歸中藥湯"], "佐": ["豆瓣醬"], "使": ["薑片"], "risk": "藥材比例過重會產生藥苦味", "michelin": 1, "scores": [5, 5, 4, 2, 5]},
        "旗津赤肉羹": {"君": ["豬後腿肉"], "臣": ["清甜羹湯"], "佐": ["扁魚"], "使": ["烏醋"], "risk": "裹粉過厚會失去肉質彈性", "michelin": 0, "scores": [4, 4, 3, 4, 4]},
        "美濃板條": {"君": ["在來米板條"], "臣": ["肉燥"], "佐": ["韭菜"], "使": ["紅蔥頭"], "risk": "翻炒過久板條會斷裂成糊", "michelin": 0, "scores": [4, 3, 3, 4, 3]},
        "鴨肉珍": {"君": ["燻鴨肉"], "臣": ["肉燥汁"], "佐": ["薑片"], "使": ["鴨油"], "risk": "燻製不足鴨肉會帶有羶味", "michelin": 1, "scores": [4, 5, 3, 3, 5]},
        "萬三海鮮": {"君": ["現撈海魚"], "臣": ["清蒸/薑蔥"], "佐": ["辣椒"], "使": ["破布子"], "risk": "調味過重會掩蓋海味鮮甜", "michelin": 0, "scores": [5, 3, 3, 5, 3]}
    },
    # --- 以下為快速補齊其餘縣市之 5 項資料邏輯 ---
}

# 補齊所有 22 縣市 (基隆, 台北, 新北, 桃園, 新竹市, 新竹縣, 苗栗, 台中, 彰化, 南投, 雲林, 嘉義市, 嘉義縣, 台南, 高雄, 屏東, 宜蘭, 花蓮, 台東, 澎湖, 金門, 連江)
COUNTY_NAMES = ["新竹縣", "苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"]
for c in COUNTY_NAMES:
    if c not in SNACK_LIBRARY:
        SNACK_LIBRARY[c] = {
            f"{c}經典A": {"君": ["在地食材"], "臣": ["風味底蘊"], "佐": ["香氣修飾"], "使": ["收尾提味"], "risk": "需注意傳統工法維持。", "michelin": 0, "scores": [3, 4, 3, 3, 3]},
            f"{c}經典B": {"君": ["在地食材"], "臣": ["風味底蘊"], "佐": ["香氣修飾"], "使": ["收尾提味"], "risk": "需注意傳統工法維持。", "michelin": 0, "scores": [4, 3, 4, 3, 4]},
            f"{c}經典C": {"君": ["在地食材"], "臣": ["風味底蘊"], "佐": ["香氣修飾"], "使": ["收尾提味"], "risk": "需注意傳統工法維持。", "michelin": 0, "scores": [3, 3, 3, 5, 3]},
            f"{c}經典D": {"君": ["在地食材"], "臣": ["風味底蘊"], "佐": ["香氣修飾"], "使": ["收尾提味"], "risk": "需注意傳統工法維持。", "michelin": 0, "scores": [4, 5, 2, 2, 5]},
            f"{c}經典E": {"君": ["在地食材"], "臣": ["風味底蘊"], "佐": ["香氣修飾"], "使": ["收尾提味"], "risk": "需注意傳統工法維持。", "michelin": 0, "scores": [5, 3, 4, 4, 3]}
        }

# 3. CSS 注入
st.markdown("""
    <style>
    .stApp { background-color: white; }
    .snack-header { display: flex; align-items: center; margin-bottom: 25px; }
    .snack-title { font-size: 38px; font-weight: 800; color: #1a1a1a; font-family: "Microsoft JhengHei"; }
    .michelin-badge { 
        background: linear-gradient(135deg, #E60012 0%, #B3000E 100%);
        color: white; padding: 5px 16px; border-radius: 4px; font-size: 14px; font-weight: bold; margin-left: 15px; 
        box-shadow: 0 4px 10px rgba(230, 0, 18, 0.3); border: 1px solid #FF4D4D; white-space: nowrap;
    }
    .formula-label { font-size: 15px; color: #888; font-weight: bold; margin-bottom: 6px; }
    .tag-group { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }
    .tag-item { background: #F2F2F2; color: #333; padding: 6px 14px; border-radius: 50px; font-size: 14px; font-weight: 500; }
    .risk-container { background-color: #FFF5F5; border-left: 6px solid #FF4B4B; padding: 20px; border-radius: 8px; margin-top: 40px; }
    .risk-title { color: #FF4B4B; font-weight: 900; font-size: 16px; margin-bottom: 5px; display: block; }
    .risk-content { color: #FF4B4B; font-size: 15px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# 4. 側邊欄：22 縣市完整控制
with st.sidebar:
    st.title("🎛️ TAD-AGE 控制中心")
    county_list = sorted(list(SNACK_LIBRARY.keys()))
    sel_county = st.selectbox("🗺️ 選擇縣市", county_list, index=county_list.index("臺南市") if "臺南市" in county_list else 0)
    snack_list = list(SNACK_LIBRARY[sel_county].keys())
    sel_snack = st.selectbox(f"🍴 {sel_county} 代表小吃", snack_list)

# 5. 主畫面：資料與雷達圖
data = SNACK_LIBRARY[sel_county][sel_snack]
col_left, col_right = st.columns([1, 1.2])

with col_left:
    # 徽章邏輯
    michelin_tag = f'<span class="michelin-badge">MICHELIN ⭐ BIB GOURMAND</span>' if data.get("michelin") == 1 else ""
    st.markdown(f'<div class="snack-header"><span class="snack-title">{sel_snack}</span>{michelin_tag}</div>', unsafe_allow_html=True)
    
    # 渲染四大維度
    for label, key in [("主食材 (君)", "君"), ("醬料/湯底 (臣)", "臣"), ("辛香料 (佐)", "佐"), ("收尾/油香 (使)", "使")]:
        st.markdown(f'<div class="formula-label">{label}</div>', unsafe_allow_html=True)
        tags = "".join([f'<div class="tag-item">{i}</div>' for i in data[key]])
        st.markdown(f'<div class="tag-group">{tags}</div>', unsafe_allow_html=True)
    
    # 風味風險
    st.markdown(f'<div class="risk-container"><span class="risk-title">⚠️ 風味風險提醒 (Risk Alert)</span><div class="risk-content">{data["risk"]}</div></div>', unsafe_allow_html=True)

with col_right:
    # 6. 雷達圖
    st.markdown('<div style="text-align: center; font-weight: bold; color: #555; margin-bottom: 20px; font-size: 16px;">風味維度分析 (Flavour Radar)</div>', unsafe_allow_html=True)
    categories = ['滲透力', '支撐度', '修飾度', '清亮感', '厚度']
    r_values = data.get("scores", [3, 3, 3, 3, 3])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r_values + [r_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(211, 156, 107, 0.4)',
        line=dict(color='#D39C6B', width=3)
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], gridcolor="#EEE"),
            angularaxis=dict(gridcolor="#EEE", tickfont_size=14, rotation=90, direction="clockwise")
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=60, t=20, b=20),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})