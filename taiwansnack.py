import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃結構解構平台", layout="wide")

# 2. 自定義 CSS
st.markdown("""
<style>
    .stApp { background-color: #fdfaf5; }
    .main-title { color: #5d4037; font-family: 'Noto Sans TC', sans-serif; font-weight: 800; text-align: center; }
    .card { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; min-height: 450px; }
    .badge-michelin { background-color: #e60012; color: white; padding: 4px 12px; border-radius: 50px; font-size: 14px; font-weight: bold; margin-left: 10px; border: 1px solid #c00000; }
    .badge-bib { background-color: #ffc107; color: #333; padding: 4px 12px; border-radius: 50px; font-size: 14px; font-weight: bold; margin-left: 10px; border: 1px solid #e0a800; }
    .role-header { border-left: 5px solid #d4a373; padding-left: 10px; color: #5d4037; font-weight: bold; margin-top: 18px; font-size: 1.1em; }
    .snack-title { font-size: 2.2em; color: #5d4037; display: flex; align-items: center; margin-bottom: 10px; font-weight: 900; }
    .report-box { background-color: #f8f9fa; border-radius: 8px; padding: 15px; border-left: 5px solid #6c757d; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. 22 縣市資料庫 (補齊分析與概述資料)
# 確保每個資料條目都具備 desc 與分析所需的數值
full_snack_db = {
    "基隆市": [
        {"name": "營養三明治", "award": "", "base": 4.5, "support": 3.8, "refine": 4.2, "finish": 3.5, "desc": "炸麵包的酥脆(君)搭配美乃滋(使)與滷蛋、火腿(臣)的經典層次。"},
        {"name": "鼎邊趖", "award": "", "base": 4.0, "support": 4.5, "refine": 3.2, "finish": 4.2, "desc": "純米磨製的趖與鮮甜海鮮湯底構成強大的風味支撐。"},
        {"name": "天婦羅", "award": "", "base": 4.2, "support": 3.5, "refine": 4.5, "finish": 3.0, "desc": "鮮魚漿的彈性主題，輔以酸甜小黃瓜作為修飾解膩。"},
        {"name": "泡泡冰", "award": "", "base": 4.8, "support": 2.5, "refine": 2.0, "finish": 4.5, "desc": "以細緻手打冰體為主題核心，風味極其純粹明確。"},
        {"name": "大腸圈", "award": "Bib", "base": 4.3, "support": 4.2, "refine": 3.8, "finish": 3.5, "desc": "糯米與大腸的紮實結合，呈現基隆傳統的飽足感風味。"}
    ],
    "臺北市": [
        {"name": "牛肉麵", "award": "Michelin", "base": 4.6, "support": 4.8, "refine": 3.8, "finish": 4.2, "desc": "以紅燒厚重湯頭為臣料骨架，支撐鮮嫩牛肉的主題感。"},
        {"name": "滷肉飯", "award": "Bib", "base": 4.9, "support": 4.0, "refine": 3.5, "finish": 3.2, "desc": "富有膠質的切丁肉燥，是整道料理的風味與視覺靈魂。"},
        {"name": "小籠包", "award": "Michelin", "base": 4.5, "support": 3.8, "refine": 4.5, "finish": 4.5, "desc": "極致的皮餡比例，肉汁導向整體的鮮甜收尾。"},
        {"name": "蚵仔麵線", "award": "", "base": 3.8, "support": 4.5, "refine": 4.0, "finish": 3.5, "desc": "柴魚湯頭與手工麵線的濃厚勾芡，形成了穩定的支撐結構。"},
        {"name": "雞排", "award": "", "base": 4.7, "support": 3.0, "refine": 4.2, "finish": 2.5, "desc": "酥脆炸衣與台式五香粉的穿透力，是街頭風味的代表。"}
    ],
    "臺南市": [
        {"name": "擔仔麵", "award": "Bib", "base": 4.5, "support": 4.2, "refine": 3.8, "finish": 4.5, "desc": "經典的肉燥(君)與蝦頭湯底(臣)交織出的府城韻味。"},
        {"name": "牛肉湯", "award": "Michelin", "base": 4.9, "support": 3.2, "refine": 2.8, "finish": 4.7, "desc": "僅以鮮甜溫體牛為主體，結構極簡卻具備極強的穿透力。"},
        {"name": "虱目魚粥", "award": "Bib", "base": 4.3, "support": 4.5, "refine": 3.5, "finish": 4.0, "desc": "鮮美魚骨湯頭與魚肉、魚皮的層次，結構均衡穩定。"},
        {"name": "碗粿", "award": "Bib", "base": 4.1, "support": 4.8, "refine": 3.2, "finish": 3.5, "desc": "在來米香與滷肉內餡的紮實咬勁，展現府城老店實力。"},
        {"name": "鱔魚意麵", "award": "Michelin", "base": 4.8, "support": 4.3, "refine": 4.5, "finish": 3.5, "desc": "猛火炒出的鑊氣搭配酸甜勾芡，結構動態且平衡。"}
    ]
}

# 通用預設小吃資料庫
default_snacks = [
    {"name": "在地代表小吃 A", "award": "", "base": 4.2, "support": 4.0, "refine": 3.5, "finish": 3.8, "desc": "本縣市深具地方特色的傳統風味組合。"},
    {"name": "在地代表小吃 B", "award": "Bib", "base": 4.5, "support": 3.8, "refine": 3.2, "finish": 4.0, "desc": "經過時間洗鍊的經典配方，風味穩定且具層次。"},
    {"name": "傳統麵食/飯食", "award": "", "base": 4.0, "support": 4.5, "refine": 3.5, "finish": 3.5, "desc": "以飽足感為主體，配以紮實的湯底支撐。"},
    {"name": "特色湯羹類", "award": "", "base": 4.3, "support": 4.2, "refine": 3.8, "finish": 3.2, "desc": "勾芡技術與主料鮮味的結合。"},
    {"name": "傳統甜點/冷飲", "award": "Michelin", "base": 4.4, "support": 3.0, "refine": 2.5, "finish": 4.8, "desc": "以純粹原味為核心，展現清亮乾淨的收尾。"}
]

counties = ["基隆市", "臺北市", "新北市", "桃園市", "新竹縣", "新竹市", "苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"]

# 4. 畫面呈現
st.markdown("<h1 class='main-title'>🍜 TAD-AGE 台灣小吃「君臣佐使」結構解構平台</h1>", unsafe_allow_html=True)

# 頂部選擇區
c1, c2 = st.columns([1, 1])
with c1:
    selected_county = st.selectbox("🌍 選擇縣市", counties, index=0)

with c2:
    # 確保連動
    current_list = full_snack_db.get(selected_county, default_snacks)
    selected_snack_name = st.selectbox("🍴 代表性 5 項小吃", [s['name'] for s in current_list])
    selected_snack = next(item for item in current_list if item["name"] == selected_snack_name)

st.markdown("---")

# 主展示區
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    # 標題與徽章
    award_html = ""
    if selected_snack['award'] == "Michelin":
        award_html = "<span class='badge-michelin'>⭐ 米其林推薦</span>"
    elif selected_snack['award'] == "Bib":
        award_html = "<span class='badge-bib'>😋 必比登推介</span>"
    
    st.markdown(f"<div class='snack-title'>{selected_snack['name']}{award_html}</div>", unsafe_allow_html=True)
    st.write(f"**📍 區域：** {selected_county}")
    
    # 修正重點：確保「結構概述」欄位有內容
    st.markdown("<div class='report-box'>", unsafe_allow_html=True)
    st.markdown(f"**【結構概述】**<br>{selected_snack['desc']}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
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
    st.subheader("📊 風味結構分析圖 (TAD-AGE Analysis)")
    
    # 雷達圖
    df_radar = pd.DataFrame(dict(
        r=[selected_snack['base'], selected_snack['support'], selected_snack['refine'], selected_snack['finish'], 4.0],
        theta=['主題感 (君)', '支撐度 (臣)', '修飾度 (佐)', '清亮感 (使)', '穿透力']
    ))
    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#d4a373', line_width=3)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], gridcolor="#eee", tickfont=dict(size=10)),
            angularaxis=dict(gridcolor="#eee", tickfont=dict(size=12))
        ),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 底部報告區 (確保連動且無白框)
st.markdown("### 📋 TAD-AGE 風味系統報告")
res_c1, res_c2 = st.columns(2)
with res_c1:
    st.markdown("<div style='background-color: #fff; padding: 15px; border-radius: 10px; border: 1px solid #eee;'>", unsafe_allow_html=True)
    st.info(f"**穩定性分析：主題強度 {selected_snack['base']}**")
    st.write(f"系統偵測顯示，{selected_snack['name']} 的風味中心極為明確。在君、臣關係中，主題感表現優異。")
    st.markdown("</div>", unsafe_allow_html=True)

with res_c2:
    st.markdown("<div style='background-color: #fff; padding: 15px; border-radius: 10px; border: 1px solid #eee;'>", unsafe_allow_html=True)
    if selected_snack['refine'] >= 4.0:
        st.success("**平衡評估：優良**")
        st.write(f"當前配置中，『佐』料的修飾度極高，展現了細膩的去腥與解膩效果，結構非常完整。")
    else:
        st.warning("**平衡評估：觀察中**")
        st.write(f"目前『佐』與『使』的比例適中，建議維持現有的油香載體比重以保持餘韻。")
    st.markdown("</div>", unsafe_allow_html=True)