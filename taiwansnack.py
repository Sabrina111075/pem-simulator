import streamlit as st
import plotly.graph_objects as go

# 1. 設置頁面 (去框化基礎)
st.set_page_config(page_title="TAD-AGE 台灣小吃 Formula 實作平台", layout="wide")

# 2. 核心資料庫 (確保 22 縣市 Key 值完整)
SNACK_LIBRARY = {
    "臺北市": {
        "牛肉麵": {"君": ["牛腱", "手工麵"], "臣": ["大骨中藥湯"], "佐": ["辣豆瓣", "酸菜"], "使": ["蔥花", "牛油"], "risk": "湯頭過於濃縮會產生苦澀感。"},
        "滷肉飯": {"君": ["豬皮脂", "米飯"], "臣": ["陳年醬油"], "佐": ["紅蔥頭", "五香粉"], "使": ["醃蘿蔔"], "risk": "脂肉比例若低於3:7，口感會顯乾澀。"},
        "蚵仔麵線": {"君": ["鮮蚵", "紅麵線"], "臣": ["柴魚勾芡湯"], "佐": ["蒜泥", "香菜"], "使": ["烏醋", "辣椒油"], "risk": "勾芡過厚會掩蓋鮮蚵的自然甜味。"},
        "雞排": {"君": ["帶骨雞胸"], "臣": ["特調醃料"], "佐": ["椒鹽粉", "辣椒粉"], "使": ["九層塔"], "risk": "油溫低於180°C會導致麵皮含油量過高。"},
        "生炒花枝": {"君": ["厚切花枝"], "臣": ["酸甜勾芡汁"], "佐": ["蒜末", "辣椒"], "使": ["烏醋"], "risk": "火候不足會導致花枝口感老韌。"}
    },
    "臺南市": {
        "蝦仁飯": {"君": ["火燒蝦", "白米"], "臣": ["柴魚高湯"], "佐": ["蔥段", "蒜頭"], "使": ["豬油"], "risk": "醬汁過多會導致米飯濕軟，失去炭火香氣。"},
        "牛肉湯": {"君": ["溫體牛肉"], "臣": ["牛大骨蔬果湯"], "佐": ["薑絲"], "使": ["米酒"], "risk": "湯頭溫度低於90°C無法瞬間鎖住肉汁。"},
        "擔仔麵": {"君": ["油麵", "鮮蝦"], "臣": ["肉燥", "蝦湯"], "佐": ["蒜泥", "五印醋"], "使": ["香菜"], "risk": "肉燥過鹹會壓過蝦湯的清甜。"},
        "虱目魚粥": {"君": ["虱目魚肚/肉"], "臣": ["魚骨清湯"], "佐": ["薑絲", "油蔥酥"], "使": ["芹菜末"], "risk": "魚刺處理不淨將嚴重影響食用體驗。"},
        "碗粿": {"君": ["在來米漿"], "臣": ["鹹蛋黃", "瘦肉"], "佐": ["香菇"], "使": ["蒜泥醬油膏"], "risk": "米漿比例過稀會導致冷卻後中心塌陷。"}
    },
    # 其他縣市資料 (請保留您本地完整的 110 項字典...)
}

# 3. 強化的 CSS (修復紅字提醒與卡片視覺)
st.markdown("""
    <style>
    /* 全局背景透明 */
    .stApp { background-color: white; }
    
    /* 標題與徽章 */
    .snack-header { margin-bottom: 25px; }
    .snack-title { font-size: 36px; font-weight: 800; color: #1a1a1a; font-family: "Microsoft JhengHei"; }
    .michelin-badge { background: linear-gradient(45deg, #E60012, #ff4b4b); color: white; padding: 4px 12px; border-radius: 6px; font-size: 14px; font-weight: bold; margin-left: 10px; vertical-align: middle; }
    
    /* 君臣佐使標籤卡 */
    .formula-card { margin-bottom: 15px; }
    .formula-label { font-size: 15px; color: #888; font-weight: bold; margin-bottom: 6px; }
    .tag-group { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px; }
    .tag-item { background: #F2F2F2; color: #333; padding: 6px 14px; border-radius: 50px; font-size: 14px; font-weight: 500; }
    
    /* 紅色風險提醒區 - 強制顯示 */
    .risk-container { 
        background-color: #FFF5F5; 
        border-left: 6px solid #FF4B4B; 
        padding: 20px; 
        border-radius: 8px; 
        margin-top: 40px; 
        box-shadow: 0 2px 4px rgba(255, 75, 75, 0.1);
    }
    .risk-title { color: #FF4B4B; font-weight: 900; font-size: 16px; margin-bottom: 5px; display: block; }
    .risk-content { color: #FF4B4B; font-size: 15px; line-height: 1.5; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# 4. 側邊欄控制
with st.sidebar:
    st.title("🎛️ TAD-AGE 控制中心")
    county_list = list(SNACK_LIBRARY.keys())
    sel_county = st.selectbox("選擇縣市", county_list, index=county_list.index("臺南市") if "臺南市" in county_list else 0)
    snack_list = list(SNACK_LIBRARY[sel_county].keys())
    sel_snack = st.selectbox("選擇小吃項目", snack_list)

# 5. 主視覺區域
data = SNACK_LIBRARY[sel_county][sel_snack]

col_left, col_right = st.columns([1, 1.2])

with col_left:
    # 標題與標籤
    st.markdown(f'''
        <div class="snack-header">
            <span class="snack-title">{sel_snack}</span>
            <span class="michelin-badge">米其林 ⭐ 必比登</span>
        </div>
    ''', unsafe_allow_html=True)
    
    # 渲染四大維度
    for label, key in [("主食材 (君)", "君"), ("醬料/湯底 (臣)", "臣"), ("辛香料 (佐)", "佐"), ("收尾/油香 (使)", "使")]:
        st.markdown(f'<div class="formula-label">{label}</div>', unsafe_allow_html=True)
        tags = "".join([f'<div class="tag-item">{i}</div>' for i in data[key]])
        st.markdown(f'<div class="tag-group">{tags}</div>', unsafe_allow_html=True)
    
    # 風味風險提醒 (紅字底部區塊)
    st.markdown(f'''
        <div class="risk-container">
            <span class="risk-title">⚠️ 風味風險提醒 (Risk Alert)</span>
            <div class="risk-content">{data['risk']}</div>
        </div>
    ''', unsafe_allow_html=True)

with col_right:
    # 6. 風味雷達卡 (修復不顯示問題)
    st.markdown('<div style="text-align: center; font-weight: bold; color: #555; margin-bottom: 10px;">風味維度分析 (Flavour Radar)</div>', unsafe_allow_html=True)
    
    # 根據資料長度動態計算雷達圖數值
    categories = ['滲透力', '支撐度', '修飾度', '清亮感', '厚度']
    r_values = [
        4.5, # 滲透
        min(len(data['臣']) * 1.5, 5.0), # 支撐
        min(len(data['佐']) * 1.5, 5.0), # 修飾
        min(len(data['使']) * 2.5, 5.0), # 清亮
        min(len(data['君']) * 2.0, 5.0)  # 厚度
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r_values + [r_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(211, 156, 107, 0.4)',
        line=dict(color='#D39C6B', width=3),
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], gridcolor="#EEE"),
            angularaxis=dict(gridcolor="#EEE", tickfont_size=14)
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=60, t=20, b=20),
        height=450
    )
    
    # 使用 container 確保 Plotly 正常渲染
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# 頁尾
st.markdown("---")
st.caption("⚙️ TAD-AGE Universal Simulator | Formula-Driven Architecture")