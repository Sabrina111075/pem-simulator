import streamlit as st
import plotly.graph_objects as go

# 1. 設置頁面
st.set_page_config(page_title="TAD-AGE 台灣小吃 Formula 實作平台", layout="wide")

# 2. 核心資料庫 (加入 Michelin 狀態判定)
# status: 1 = 米其林/必比登推薦, 0 = 地方經典小吃
SNACK_LIBRARY = {
    "臺北市": {
        "牛肉麵": {"君": ["牛腱", "手工麵"], "臣": ["大骨中藥湯"], "佐": ["辣豆瓣", "酸菜"], "使": ["蔥花", "牛油"], "risk": "湯頭過於濃縮會產生苦澀感。", "michelin": 1},
        "滷肉飯": {"君": ["豬皮脂", "米飯"], "臣": ["陳年醬油"], "佐": ["紅蔥頭", "五香粉"], "使": ["醃蘿蔔"], "risk": "脂肉比例若低於3:7，口感會顯乾澀。", "michelin": 1},
        "蚵仔麵線": {"君": ["鮮蚵", "紅麵線"], "臣": ["柴魚勾芡湯"], "佐": ["蒜泥", "香菜"], "使": ["烏醋", "辣椒油"], "risk": "勾芡過厚會掩蓋鮮蚵的自然甜味。", "michelin": 0},
        "雞排": {"君": ["帶骨雞胸"], "臣": ["特調醃料"], "佐": ["椒鹽粉", "辣椒粉"], "使": ["九層塔"], "risk": "油溫低於180°C會導致麵皮含油量過高。", "michelin": 0},
        "生炒花枝": {"君": ["厚切花枝"], "臣": ["酸甜勾芡汁"], "佐": ["蒜末", "辣椒"], "使": ["烏醋"], "risk": "火候不足會導致花枝口感老韌。", "michelin": 0}
    },
    "臺南市": {
        "蝦仁飯": {"君": ["火燒蝦", "白米"], "臣": ["柴魚高湯"], "佐": ["蔥段", "蒜頭"], "使": ["豬油"], "risk": "醬汁過多會導致米飯濕軟，失去炭火香氣。", "michelin": 0},
        "牛肉湯": {"君": ["溫體牛肉"], "臣": ["牛骨蔬果湯"], "佐": ["薑絲"], "使": ["米酒"], "risk": "湯頭溫度低於90°C無法鎖住肉汁。", "michelin": 1},
        "擔仔麵": {"君": ["油麵", "鮮蝦"], "臣": ["肉燥", "蝦湯"], "佐": ["蒜泥", "五印醋"], "使": ["香菜"], "risk": "肉燥過鹹會壓過蝦湯的清甜。", "michelin": 1},
        "虱目魚粥": {"君": ["虱目魚肚/肉"], "臣": ["魚骨清湯"], "佐": ["薑絲", "油蔥酥"], "使": ["芹菜末"], "risk": "魚刺處理不淨將嚴重影響食用。", "michelin": 1},
        "碗粿": {"君": ["在來米漿"], "臣": ["鹹蛋黃", "瘦肉"], "佐": ["香菇"], "使": ["蒜泥醬油膏"], "risk": "米漿比例過稀會導致冷後塌陷。", "michelin": 0}
    },
    # 此處已對應資料庫邏輯，其餘縣市小吃依此類推...
}

# 3. CSS 注入 (強化推薦徽章)
st.markdown("""
    <style>
    .stApp { background-color: white; }
    .snack-header { display: flex; align-items: center; margin-bottom: 25px; }
    .snack-title { font-size: 38px; font-weight: 800; color: #1a1a1a; font-family: "Microsoft JhengHei"; }
    
    /* 顯眼化推薦徽章 */
    .michelin-active { 
        background: linear-gradient(135deg, #E60012 0%, #B3000E 100%);
        color: white; 
        padding: 5px 15px; 
        border-radius: 4px; 
        font-size: 14px; 
        font-weight: bold; 
        margin-left: 15px; 
        box-shadow: 0 4px 8px rgba(230, 0, 18, 0.3);
        border: 1px solid #FF4D4D;
        letter-spacing: 1px;
    }
    
    .formula-label { font-size: 15px; color: #888; font-weight: bold; margin-bottom: 6px; }
    .tag-group { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px; }
    .tag-item { background: #F2F2F2; color: #333; padding: 6px 14px; border-radius: 50px; font-size: 14px; font-weight: 500; }
    .risk-container { background-color: #FFF5F5; border-left: 6px solid #FF4B4B; padding: 20px; border-radius: 8px; margin-top: 40px; }
    .risk-title { color: #FF4B4B; font-weight: 900; font-size: 16px; margin-bottom: 5px; display: block; }
    .risk-content { color: #FF4B4B; font-size: 15px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# 4. 側邊欄
with st.sidebar:
    st.title("🎛️ TAD-AGE 控制中心")
    county_list = list(SNACK_LIBRARY.keys())
    sel_county = st.selectbox("🗺️ 選擇縣市", county_list, index=county_list.index("臺南市") if "臺南市" in county_list else 0)
    snack_list = list(SNACK_LIBRARY[sel_county].keys())
    sel_snack = st.selectbox(f"🍴 {sel_county} 小吃清單", snack_list)

# 5. 主畫面顯示
data = SNACK_LIBRARY[sel_county][sel_snack]
col_left, col_right = st.columns([1, 1.2])

with col_left:
    # 判斷是否顯示推薦徽章
    michelin_html = '<span class="michelin-active">MICHELIN ⭐ BIB GOURMAND</span>' if data.get("michelin") == 1 else ""
    
    st.markdown(f'''
        <div class="snack-header">
            <span class="snack-title">{sel_snack}</span>
            {michelin_html}
        </div>
    ''', unsafe_allow_html=True)
    
    for label, key in [("主食材 (君)", "君"), ("醬料/湯底 (臣)", "臣"), ("辛香料 (佐)", "佐"), ("收尾/油香 (使)", "使")]:
        st.markdown(f'<div class="formula-label">{label}</div>', unsafe_allow_html=True)
        tags = "".join([f'<div class="tag-item">{i}</div>' for i in data[key]])
        st.markdown(f'<div class="tag-group">{tags}</div>', unsafe_allow_html=True)
    
    st.markdown(f'''
        <div class="risk-container">
            <span class="risk-title">⚠️ 風味風險提醒 (Risk Alert)</span>
            <div class="risk-content">{data["risk"]}</div>
        </div>
    ''', unsafe_allow_html=True)

with col_right:
    st.markdown('<div style="text-align: center; font-weight: bold; color: #555; margin-bottom: 10px;">風味維度分析 (Flavour Radar)</div>', unsafe_allow_html=True)
    categories = ['滲透力', '支撐度', '修飾度', '清亮感', '厚度']
    r_values = [4.5, min(len(data['臣']) * 1.5, 5.0), min(len(data['佐']) * 1.5, 5.0), min(len(data['使']) * 2.5, 5.0), min(len(data['君']) * 2.0, 5.0)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=r_values + [r_values[0]], theta=categories + [categories[0]], fill='toself', fillcolor='rgba(211, 156, 107, 0.4)', line=dict(color='#D39C6B', width=3)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5]), angularaxis=dict(tickfont_size=14)), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=60, r=60, t=20, b=20), height=450)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})