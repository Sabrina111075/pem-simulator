import streamlit as st
import plotly.graph_objects as go

# --- 1. 完整資料庫 (22 縣市框架) ---
# 這裡先預填部分內容，你可以隨時修改數值
SNACK_DB = {
    "基隆市": {"營養三明治": {"star": 0, "bib": True, "flavor": [4,3,4,2,3], "desc": "高溫油炸麵包配上濃郁美乃滋"}},
    "台北市": {"牛肉麵": {"star": 1, "bib": False, "flavor": [5,5,4,3,4], "desc": "長時間熬煮紅燒湯頭，肉質軟嫩"}},
    "新北市": {"深坑豆腐": {"star": 0, "bib": True, "flavor": [4,4,3,2,5], "desc": "獨特焦香味，層次分明"}},
    "桃園市": {"大溪豆乾": {"star": 0, "bib": False, "flavor": [3,4,4,2,3], "desc": "陳年滷汁透心香"}},
    "新竹縣": {
        "仙草雞": {"star": 0, "bib": True, "flavor": [5,4,3,3,4], "desc": "在地仙草與土雞慢火燉煮"},
        "粄條": {"star": 0, "bib": False, "flavor": [4,3,4,2,3], "desc": "純米手作，口感紮實"},
        "擂茶": {"star": 0, "bib": False, "flavor": [5,4,3,2,5], "desc": "多種穀物研磨而成"}
    },
    "新竹市": {"貢丸湯": {"star": 0, "bib": False, "flavor": [4,4,3,3,2], "desc": "紮實豬肉搥打，彈牙多汁"}},
    "苗栗縣": {"水晶餃": {"star": 0, "bib": False, "flavor": [3,5,3,2,3], "desc": "皮Q餡香的客家特色"}},
    "台中市": {"太陽餅": {"star": 0, "bib": False, "flavor": [5,3,3,4,4], "desc": "麥芽糖內餡與千層酥皮"}},
    "彰化縣": {"肉圓": {"star": 0, "bib": True, "flavor": [4,5,4,2,4], "desc": "低溫油泡，外皮Q彈"}},
    "南投縣": {"意麵": {"star": 0, "bib": False, "flavor": [3,4,3,3,3], "desc": "鹼水麵條搭配特製肉燥"}},
    "雲林縣": {"鵝肉": {"star": 0, "bib": True, "flavor": [5,4,3,3,4], "desc": "原味多汁，鮮甜可口"}},
    "嘉義縣": {"火雞肉飯": {"star": 0, "bib": True, "flavor": [5,4,3,3,3], "desc": "火雞肉絲與香噴噴雞油"}},
    "嘉義市": {"美乃滋涼麵": {"star": 0, "bib": False, "flavor": [4,3,5,3,2], "desc": "嘉義獨有的白醋風味"}},
    "台南市": {"牛肉湯": {"star": 0, "bib": True, "flavor": [5,3,2,4,5], "desc": "產地直送，現燙鮮甜"}},
    "高雄市": {"鴨肉飯": {"star": 0, "bib": False, "flavor": [4,4,3,3,4], "desc": "煙燻鴨肉與滷汁的完美結合"}},
    "屏東縣": {"萬丹紅豆餅": {"star": 0, "bib": False, "flavor": [5,3,2,4,3], "desc": "皮薄餡多，紅豆飽滿"}},
    "宜蘭縣": {"肉羹": {"star": 0, "bib": False, "flavor": [4,4,4,2,3], "desc": "蒜味濃郁，勾芡滑順"}},
    "花蓮縣": {"扁食": {"star": 0, "bib": False, "flavor": [4,3,3,3,3], "desc": "皮薄如蟬翼，肉餡鮮香"}},
    "台東縣": {"米苔目": {"star": 0, "bib": False, "flavor": [3,4,4,2,3], "desc": "柴魚片點綴的台式風味"}},
    "澎湖縣": {"黑糖糕": {"star": 0, "bib": False, "flavor": [5,2,2,3,4], "desc": "鬆軟Q彈，黑糖香氣持久"}},
    "金門縣": {"廣東粥": {"star": 0, "bib": False, "flavor": [4,5,3,2,4], "desc": "煮到看不見米粒的糜粥"}},
    "連江縣": {"繼光餅": {"star": 0, "bib": False, "flavor": [4,4,2,2,3], "desc": "馬祖貝果，芝麻香氣誘人"}}
}

# --- 2. 介面設定 ---
st.set_page_config(page_title="TAD-AGE 平台 V3", layout="wide")

# 套用精緻 CSS 樣式
st.markdown("""
    <style>
    .michelin-tag { background-color: #E60012; color: white; padding: 3px 12px; border-radius: 20px; font-weight: bold; font-size: 14px; }
    .bib-tag { background-color: #F0F2F6; color: #1E1E1E; padding: 3px 12px; border-radius: 20px; border: 1px solid #CCC; font-weight: bold; font-size: 14px; }
    .sidebar-text { font-size: 1.1rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 側邊導覽 ---
with st.sidebar:
    st.title("🧭 導覽中心")
    selected_city = st.selectbox("1. 選擇縣市", list(SNACK_DB.keys()), index=4) # 預設新竹縣
    
    snack_list = list(SNACK_DB[selected_city].keys())
    
    def snack_formatter(name):
        info = SNACK_DB[selected_city][name]
        icon = " ⭐" if info["star"] > 0 else (" 😋" if info["bib"] else "")
        return f"{name}{icon}"
        
    selected_snack = st.selectbox("2. 代表小吃", snack_list, format_func=snack_formatter)
    data = SNACK_DB[selected_city][selected_snack]

# --- 4. 主畫面佈局 ---
st.title("🍜 TAD-AGE 台灣小吃風味平台 V3")

# 顯示標題與標籤
col_title, col_tags = st.columns([2, 3])
with col_title:
    st.subheader(f"風味模擬卡：{selected_snack}")

with col_tags:
    st.write("") # 調整垂直對齊
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
        st.info(f"針對「{selected_snack}」的傳統作法，需注重火候控管與投料順序。")

with col2:
    # 雷達圖
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
        margin=dict(l=50, r=50, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)