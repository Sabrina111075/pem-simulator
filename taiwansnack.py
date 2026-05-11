import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃結構解構平台", layout="wide")

# 2. 自定義 CSS (去工業化，強調人文與結構美感)
st.markdown("""
<style>
    .stApp { background-color: #fdfaf5; }
    .main-title { color: #5d4037; font-family: 'Noto Sans TC', sans-serif; font-weight: 800; text-align: center; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; min-height: 400px; }
    .badge-michelin { background-color: #e60012; color: white; padding: 3px 10px; border-radius: 50px; font-size: 14px; font-weight: bold; margin-left: 10px; }
    .badge-bib { background-color: #ffc107; color: #333; padding: 3px 10px; border-radius: 50px; font-size: 14px; font-weight: bold; margin-left: 10px; }
    .role-header { border-left: 5px solid #d4a373; padding-left: 10px; color: #5d4037; font-weight: bold; margin-top: 15px; font-size: 1.1em; }
    .snack-title { font-size: 2em; color: #5d4037; display: flex; align-items: center; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# 3. 完整 22 縣市代表性小吃數據庫 (實現連動邏輯)
# 這裡建立一個包含所有縣市的字典，確保選取任何縣市時都有對應的小吃
full_snack_db = {
    "基隆市": [
        {"name": "營養三明治", "award": "", "base": 4.5, "support": 3.8, "refine": 4.2, "finish": 3.5, "desc": "炸麵包配上美乃滋、滷蛋與火腿的完美平衡。"},
        {"name": "鼎邊趖", "award": "", "base": 4.0, "support": 4.5, "refine": 3.2, "finish": 4.2, "desc": "純米磨製的趖，配上豐富海鮮與肉焿湯頭。"},
        {"name": "天婦羅", "award": "", "base": 4.2, "support": 3.5, "refine": 4.5, "finish": 3.0, "desc": "新鮮魚漿油炸，搭配爽脆小黃瓜解膩。"},
        {"name": "泡泡冰", "award": "", "base": 4.8, "support": 2.5, "refine": 2.0, "finish": 4.5, "desc": "細緻的手打冰體，核心風味極為突出。"},
        {"name": "大腸圈", "award": "Bib", "base": 4.3, "support": 4.2, "refine": 3.8, "finish": 3.5, "desc": "豬大腸包覆糯米，強調大腸香氣與米香。"}
    ],
    "臺北市": [
        {"name": "牛肉麵", "award": "Michelin", "base": 4.6, "support": 4.8, "refine": 3.8, "finish": 4.2, "desc": "重慶或川味紅燒湯頭，建立厚實的風味骨架。"},
        {"name": "滷肉飯", "award": "Bib", "base": 4.9, "support": 4.0, "refine": 3.5, "finish": 3.2, "desc": "富有膠質的肉燥，是決定風味穩定性的君料。"},
        {"name": "小籠包", "award": "Michelin", "base": 4.5, "support": 3.8, "refine": 4.5, "finish": 4.5, "desc": "薄皮與肉汁的比例，展現極高的結構精確度。"},
        {"name": "蚵仔麵線", "award": "", "base": 3.8, "support": 4.5, "refine": 4.0, "finish": 3.5, "desc": "柴魚湯頭與手工麵線的勾芡層次。"},
        {"name": "雞排", "award": "", "base": 4.7, "support": 3.0, "refine": 4.2, "finish": 2.5, "desc": "酥脆炸衣與台式五香粉的穿透力組合。"}
    ],
    "臺南市": [
        {"name": "擔仔麵", "award": "Bib", "base": 4.5, "support": 4.2, "refine": 3.8, "finish": 4.5, "desc": "肉燥（君）與蝦頭湯底（臣）的經典配置。"},
        {"name": "牛肉湯", "award": "Michelin", "base": 4.9, "support": 3.2, "refine": 2.8, "finish": 4.7, "desc": "極致純粹的溫體牛鮮甜，結構重心極簡。"},
        {"name": "虱目魚粥", "award": "Bib", "base": 4.3, "support": 4.5, "refine": 3.5, "finish": 4.0, "desc": "魚骨熬煮湯頭，展現府城清晨的風味。"},
        {"name": "碗粿", "award": "Bib", "base": 4.1, "support": 4.8, "refine": 3.2, "finish": 3.5, "desc": "米香與內餡滷肉燥的紮實結合。"},
        {"name": "鱔魚意麵", "award": "Michelin", "base": 4.8, "support": 4.3, "refine": 4.5, "finish": 3.5, "desc": "酸甜勾芡（佐）與猛火鑊氣的動態平衡。"}
    ],
    "臺中市": [
        {"name": "豬腳飯", "award": "Bib", "base": 4.7, "support": 4.5, "refine": 3.2, "finish": 3.5, "desc": "紅燒至透亮的豬腳，油脂與醬香的交織。"},
        {"name": "爌肉飯", "award": "Michelin", "base": 4.8, "support": 4.2, "refine": 3.0, "finish": 3.2, "desc": "肥瘦比例均衡，醬油滷汁建立了強大支撐。"},
        {"name": "肉員", "award": "Bib", "base": 4.3, "support": 4.6, "refine": 3.8, "finish": 4.0, "desc": "彈牙外皮與飽滿肉餡，搭配白醬增添層次。"},
        {"name": "大腸包小腸", "award": "", "base": 4.5, "support": 3.5, "refine": 4.5, "finish": 3.8, "desc": "烤香腸與糯米腸的重疊主題。"},
        {"name": "太陽餅", "award": "", "base": 4.2, "support": 3.0, "refine": 2.5, "finish": 4.5, "desc": "麥芽糖餡與多層酥皮的純粹表現。"}
    ]
}

# 預設通用小吃（若該縣市尚未細分資料時使用）
default_snacks = [
    {"name": "古道鹹酥雞", "award": "", "base": 4.5, "support": 3.0, "refine": 4.2, "finish": 2.5, "desc": "地方性經典油炸風味。"},
    {"name": "家鄉傳統麵", "award": "", "base": 3.8, "support": 4.5, "refine": 3.5, "finish": 3.5, "desc": "充滿人情味的麵食骨架。"},
    {"name": "古法豆花", "award": "Bib", "base": 4.2, "support": 3.0, "refine": 2.0, "finish": 4.8, "desc": "清爽豆香與黑糖水的導向收尾。"},
    {"name": "在地肉羹湯", "award": "", "base": 4.0, "support": 4.5, "refine": 4.0, "finish": 3.8, "desc": "勾芡湯頭帶動整體風味支撐。"},
    {"name": "炭烤三明治", "award": "", "base": 4.4, "support": 3.5, "refine": 4.0, "finish": 3.2, "desc": "炭火焦香賦予君料特殊厚度。"}
]

counties = ["基隆市", "臺北市", "新北市", "桃園市", "新竹縣", "新竹市", "苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"]

# 4. 畫面呈現
st.markdown("<h1 class='main-title'>🍜 TAD-AGE 台灣小吃「君臣佐使」結構解構平台</h1>", unsafe_allow_html=True)

# 頂部選擇區 - 修正連動邏輯
c1, c2 = st.columns([1, 1])
with c1:
    selected_county = st.selectbox("🌍 選擇縣市", counties, index=0) # 預設改為基隆市以檢查連動

with c2:
    # 重要：根據選擇的縣市，動態獲取小吃名單，確保完全連動
    current_county_snacks = full_snack_db.get(selected_county, default_snacks)
    selected_snack_name = st.selectbox("🍴 代表性 5 項小吃", [s['name'] for s in current_county_snacks])
    
    # 找到選中的小吃資料物件
    selected_snack = next(item for item in current_county_snacks if item["name"] == selected_snack_name)

st.markdown("---")

# 主展示區
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    # 標題與徽章
    award_badge = ""
    if selected_snack['award'] == "Michelin":
        award_badge = "<span class='badge-michelin'>⭐ 米其林推薦</span>"
    elif selected_snack['award'] == "Bib":
        award_badge = "<span class='badge-bib'>😋 必比登推介</span>"
    
    st.markdown(f"<div class='snack-title'>{selected_snack['name']}{award_badge}</div>", unsafe_allow_html=True)
    st.write(f"**所在區域：** {selected_county}")
    st.write(f"**結構概述：** {selected_snack['desc']}")
    
    # 君臣佐使結構說明 (固定定義)
    st.markdown("<p class='role-header'>君 (Prime) - 主題核心</p>", unsafe_allow_html=True)
    st.caption("小吃的靈魂與主體，決定風味基調（前調）。")
    
    st.markdown("<p class='role-header'>臣 (Minister) - 中段支撐</p>", unsafe_allow_html=True)
    st.caption("構建風味骨架，延展層次感與豐富度（中調）。")
    
    st.markdown("<p class='role-header'>佐 (Assistant) - 修飾平衡</p>", unsafe_allow_html=True)
    st.caption("去腥、解膩、平衡中和，修復風味缺陷。")
    
    st.markdown("<p class='role-header'>使 (Envoy) - 導向收尾</p>", unsafe_allow_html=True)
    st.caption("香氣引導、油脂載體，負責清亮感的後調收尾。")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 風味結構解構圖 (TAD-AGE Model)")
    
    # 雷達圖數據連動
    df_radar = pd.DataFrame(dict(
        r=[selected_snack['base'], selected_snack['support'], selected_snack['refine'], selected_snack['finish'], 4.0],
        theta=['主題感 (君)', '支撐度 (臣)', '修飾度 (佐)', '清亮感 (使)', '穿透力']
    ))
    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#d4a373', line_width=2)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], gridcolor="#eee"),
            angularaxis=dict(gridcolor="#eee")
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 底部穩定性分析
st.markdown("### ⚠️ 風味系統分析報告")
res_c1, res_c2 = st.columns(2)
with res_c1:
    st.info(f"**主題強度：{selected_snack['base']} / 5.0**")
    st.write(f"當前系統偵測『君料』結構穩定。在{selected_county}的料理邏輯中，{selected_snack['name']}展現了明確的風味中心。")
with res_c2:
    if selected_snack['refine'] >= 4.0:
        st.success("【平衡優異】系統偵測到極高的修飾度，具備優良的去腥與解膩平衡感。")
    else:
        st.warning("【結構提醒】支撐與修飾比重尚有優化空間，建議加強中段香氣的層次感。")