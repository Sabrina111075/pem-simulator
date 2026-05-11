import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃結構解構平台", layout="wide")

# 2. 自定義 CSS (拿掉工業化風格，改為較為人文與清晰的視覺)
st.markdown("""
<style>
    .stApp { background-color: #fdfaf5; }
    .main-title { color: #5d4037; font-family: 'Noto Sans TC', sans-serif; font-weight: 800; text-align: center; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .badge-michelin { background-color: #e60012; color: white; padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: bold; }
    .badge-bib { background-color: #ffc107; color: #333; padding: 3px 10px; border-radius: 50px; font-size: 12px; font-weight: bold; }
    .role-header { border-left: 5px solid #d4a373; padding-left: 10px; color: #5d4037; font-weight: bold; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

# 3. 22縣市與5項小吃數據資料庫 (包含米其林資訊)
county_data = {
    "臺南市": [
        {"name": "擔仔麵", "award": "Bib", "base": 4.5, "support": 4.2, "refine": 3.5, "finish": 4.0},
        {"name": "牛肉湯", "award": "Michelin", "base": 4.8, "support": 3.5, "refine": 2.5, "finish": 4.5},
        {"name": "虱目魚粥", "award": "Bib", "base": 4.2, "support": 4.0, "refine": 3.0, "finish": 3.8},
        {"name": "碗粿", "award": "Bib", "base": 4.0, "support": 4.5, "refine": 3.2, "finish": 3.5},
        {"name": "鱔魚意麵", "award": "Michelin", "base": 4.7, "support": 4.3, "refine": 4.0, "finish": 3.2}
    ],
    "臺北市": [
        {"name": "牛肉麵", "award": "Michelin", "base": 4.6, "support": 4.5, "refine": 3.8, "finish": 4.0},
        {"name": "滷肉飯", "award": "Bib", "base": 4.8, "support": 4.2, "refine": 3.5, "finish": 3.0},
        {"name": "小籠包", "award": "Michelin", "base": 4.5, "support": 4.0, "refine": 4.5, "finish": 4.2},
        {"name": "蚵仔麵線", "award": "", "base": 3.8, "support": 4.2, "refine": 3.5, "finish": 3.5},
        {"name": "雞排", "award": "", "base": 4.5, "support": 3.0, "refine": 4.0, "finish": 2.5}
    ],
    "臺中市": [
        {"name": "豬腳飯", "award": "Bib", "base": 4.7, "support": 4.5, "refine": 3.0, "finish": 3.2},
        {"name": "爌肉飯", "award": "Michelin", "base": 4.8, "support": 4.2, "refine": 2.8, "finish": 3.0},
        {"name": "肉員", "award": "Bib", "base": 4.2, "support": 4.5, "refine": 3.5, "finish": 3.8},
        {"name": "大腸包小腸", "award": "", "base": 4.5, "support": 3.5, "refine": 4.0, "finish": 3.5},
        {"name": "太陽餅", "award": "", "base": 4.0, "support": 3.2, "refine": 2.5, "finish": 4.0}
    ]
}

# 輔助：22縣市清單
counties = ["基隆市", "臺北市", "新北市", "桃園市", "新竹縣", "新竹市", "苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"]

# 4. 畫面呈現
st.markdown("<h1 class='main-title'>🍜 TAD-AGE 台灣小吃「君臣佐使」結構解構平台</h1>", unsafe_allow_html=True)

# 頂部選擇區
c1, c2 = st.columns([1, 2])
with c1:
    selected_county = st.selectbox("🌍 選擇縣市", counties, index=13) # 預設臺南
with c2:
    # 根據縣市取得小吃列表，若無資料則顯示預設
    snacks_list = county_data.get(selected_county, county_data["臺南市"])
    selected_snack_name = st.selectbox("🍴 代表性 5 項小吃", [s['name'] for s in snacks_list])
    selected_snack = next(item for item in snacks_list if item["name"] == selected_snack_name)

st.markdown("---")

# 主展示區
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    # 徽章處理
    badge = ""
    if selected_snack['award'] == "Michelin":
        badge = "<span class='badge-michelin'>⭐ 米其林推薦</span>"
    elif selected_snack['award'] == "Bib":
        badge = "<span class='badge-bib'>😋 必比登推介</span>"
    
    st.markdown(f"<h2>{selected_snack['name']} {badge}</h2>", unsafe_allow_html=True)
    st.write(f"當前縣市：{selected_county}")
    
    # 結構定義描述
    st.markdown("<p class='role-header'>君 (Prime) - 主題核心</p>", unsafe_allow_html=True)
    st.write("決定小吃的靈魂與風味基調。")
    st.markdown("<p class='role-header'>臣 (Minister) - 中段支撐</p>", unsafe_allow_html=True)
    st.write("構建風味骨架，延展口感層次。")
    st.markdown("<p class='role-header'>佐 (Assistant) - 修飾平衡</p>", unsafe_allow_html=True)
    st.write("去腥、解膩，平衡主次層次。")
    st.markdown("<p class='role-header'>使 (Envoy) - 導向收尾</p>", unsafe_allow_html=True)
    st.write("引導香氣導向，負責清亮感收尾。")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 風味解構雷達圖")
    # 雷達圖數據
    df_radar = pd.DataFrame(dict(
        r=[selected_snack['base'], selected_snack['support'], selected_snack['refine'], selected_snack['finish'], 4.0],
        theta=['主題感 (君)', '支撐度 (臣)', '修飾度 (佐)', '清亮感 (使)', '穿透力']
    ))
    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#d4a373')
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 底部風險預警
st.markdown("### ⚠️ 風味系統穩定性分析")
rf_col1, rf_col2 = st.columns(2)
with rf_col1:
    st.success(f"【系統穩定】{selected_snack['name']} 之『君』料強度達 {selected_snack['base']}，結構中心明確。")
with rf_col2:
    if selected_snack['refine'] < 3.0:
        st.warning("【平衡提醒】佐料比重較低，建議注意食材原味去腥處理。")
    else:
        st.info("【層次和諧】風味修飾與收尾具備優良穿透力。")