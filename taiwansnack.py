import streamlit as st
import plotly.graph_objects as go

# 1. 設置頁面 (去框化、寬版佈局)
st.set_page_config(page_title="TAD-AGE 台灣小吃 Formula 實作平台", layout="wide")

# 2. 核心資料庫
SNACK_LIBRARY = {
    "基隆市": {
        "鼎邊趖": {"君": ["米漿片", "海鮮湯"], "臣": ["肉羹", "蝦仁羹"], "佐": ["白胡椒", "蒜酥"], "使": ["芹菜", "油蔥"], "risk": "海味不能被胡椒蓋掉", "michelin": 0, "scores": [5, 3, 3, 4, 2]},
        "廟口天婦羅": {"君": ["魚漿甜不辣"], "臣": ["味噌醬"], "佐": ["白胡椒", "蒜末"], "使": ["小黃瓜"], "risk": "魚漿比例不足會影響彈性", "michelin": 0, "scores": [4, 4, 3, 3, 4]}
    },
    "臺北市": {
        "牛肉麵": {"君": ["牛腱", "手工麵"], "臣": ["大骨中藥湯"], "佐": ["辣豆瓣", "酸菜"], "使": ["蔥花", "牛油"], "risk": "湯頭過於濃縮會產生苦澀感", "michelin": 1, "scores": [5, 5, 4, 2, 5]},
        "小籠包": {"君": ["手工薄皮", "黑豬肉"], "臣": ["皮凍高湯"], "佐": ["薑絲"], "使": ["醋"], "risk": "提拿皮破會流失核心湯汁", "michelin": 2, "scores": [5, 4, 5, 4, 4]}
    },
    "新北市": {
        "深坑臭豆腐": {"君": ["手工豆腐"], "臣": ["鹽滷水"], "佐": ["辣醬"], "使": ["泡菜"], "risk": "豆香味若被辣味完全掩蓋則失去特色", "michelin": 0, "scores": [4, 5, 3, 3, 4]},
        "淡水阿給": {"君": ["油豆腐"], "臣": ["冬粉"], "佐": ["魚漿"], "使": ["甜辣醬"], "risk": "封口魚漿不密會導致冬粉流出", "michelin": 0, "scores": [3, 4, 4, 4, 3]}
    },
    "臺中市": {
        "排骨酥麵": {"君": ["醃製排骨酥"], "臣": ["油蔥湯底"], "佐": ["冬瓜"], "使": ["芹菜末"], "risk": "排骨酥炸衣過厚會影響吸湯。", "michelin": 1, "scores": [5, 4, 4, 3, 4]}
    },
    "臺南市": {
        "牛肉湯": {"君": ["溫體牛肉"], "臣": ["牛骨蔬果湯"], "佐": ["薑絲"], "使": ["米酒"], "risk": "湯頭溫度低於90°C無法鎖住肉汁。", "michelin": 1, "scores": [5, 4, 3, 3, 5]}
    }
} # 確保最後這裡只有一個大括號關閉全庫

# 3. CSS 注入
st.markdown("""
    <style>
    .stApp { background-color: white; }
    .snack-header { display: flex; align-items: center; margin-bottom: 25px; }
    .snack-title { font-size: 38px; font-weight: 800; color: #1a1a1a; font-family: "Microsoft JhengHei"; }
    
    /* 必比登：紅色樣式 */
    .michelin-badge { 
        background: linear-gradient(135deg, #E60012 0%, #B3000E 100%);
        color: white; padding: 5px 16px; border-radius: 4px; font-size: 14px; font-weight: bold; margin-left: 15px; 
        box-shadow: 0 4px 10px rgba(230, 0, 18, 0.3); border: 1px solid #FF4D4D; white-space: nowrap;
    }
    
    /* 米其林星級：金色樣式 */
    .michelin-star {
        background: linear-gradient(135deg, #FFD700 0%, #D4AF37 100%);
        color: #000; padding: 5px 16px; border-radius: 4px; font-size: 14px; font-weight: bold; margin-left: 15px; 
        box-shadow: 0 4px 10px rgba(212, 175, 55, 0.4); border: 1px solid #B8860B; white-space: nowrap;
    }

    .formula-label { font-size: 15px; color: #888; font-weight: bold; margin-bottom: 6px; }
    .tag-group { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }
    .tag-item { background: #F2F2F2; color: #333; padding: 6px 14px; border-radius: 50px; font-size: 14px; font-weight: 500; }
    .risk-container { background-color: #FFF5F5; border-left: 6px solid #FF4B4B; padding: 20px; border-radius: 8px; margin-top: 40px; }
    .risk-title { color: #FF4B4B; font-weight: 900; font-size: 16px; margin-bottom: 5px; display: block; }
    .risk-content { color: #FF4B4B; font-size: 15px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# 改進後的徽章邏輯
michelin_val = data.get("michelin", 0)
if michelin_val == 2:
    # 使用金色類別
    michelin_tag = f'<span class="michelin-star">MICHELIN ⭐ STAR</span>'
elif michelin_val == 1:
    # 使用紅色類別
    michelin_tag = f'<span class="michelin-badge">BIB GOURMAND 😋</span>'
else:
    michelin_tag = ""

st.markdown(f'<div class="snack-header"><span class="snack-title">{sel_snack}</span>{michelin_tag}</div>', unsafe_allow_html=True)

# 4. 側邊欄：22 縣市、代表性小吃選單
with st.sidebar:
    st.title("🎛️ 台灣各縣市代表性小吃")
    county_list = sorted(list(SNACK_LIBRARY.keys())) # 確保順序美觀
    sel_county = st.selectbox("🗺️ 選擇縣市 ", county_list, index=county_list.index("臺南市") if "臺南市" in county_list else 0)
    snack_list = list(SNACK_LIBRARY[sel_county].keys())
    sel_snack = st.selectbox(f"🍴 {sel_county} 代表性小吃", snack_list)


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