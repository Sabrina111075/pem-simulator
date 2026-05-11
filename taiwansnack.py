import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃 Formula 平台", layout="wide")

# 2. 自定義 CSS (移除大白框，改用卡片與清單式佈局)
st.markdown("""
<style>
    .stApp { background-color: #fdfaf5; }
    .formula-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #e6e0d8; margin-bottom: 20px; }
    .section-title { color: #5d4037; font-size: 1.2em; font-weight: 800; border-bottom: 2px solid #d4a373; padding-bottom: 5px; margin-bottom: 15px; }
    .ingredient-tag { display: inline-block; background-color: #f4ece2; color: #5d4037; padding: 5px 12px; border-radius: 5px; margin: 5px; font-size: 0.9em; border: 1px solid #dcd3c9; }
    .badge-michelin { background-color: #e60012; color: white; padding: 2px 10px; border-radius: 50px; font-size: 12px; font-weight: bold; }
    .badge-bib { background-color: #ffc107; color: #333; padding: 2px 10px; border-radius: 50px; font-size: 12px; font-weight: bold; }
    .risk-text { color: #b71c1c; font-size: 0.85em; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# 3. 數據整合 (將 CSV 邏輯整合進資料庫)
# 模擬從 小吃22.csv 與 小吃55.csv 提取出的實體數據
snack_library = {
    "臺南市": {
        "擔仔麵": {
            "award": "Bib", "base": 4.5, "support": 4.2, "refine": 3.8, "finish": 4.5,
            "main": "油麵、鮮蝦", "spices": "蒜泥、白胡椒", "sauce": "肉燥、蝦頭湯、五印醋",
            "oil": "豬油、紅蔥頭", "garnish": "香菜、豆芽菜",
            "formula": {"君": "特製肉燥", "臣": "蝦頭清湯", "佐": "蒜泥與烏醋", "使": "香菜香氣"},
            "risks": {"白胡椒": "過量會尖、粗", "油蔥": "焦苦風險", "香菜": "過多會蓋清湯"}
        },
        "牛肉湯": {
            "award": "Michelin", "base": 4.9, "support": 3.0, "refine": 2.5, "finish": 4.2,
            "main": "溫體牛肉", "spices": "薑絲", "sauce": "牛大骨湯",
            "oil": "牛肉本身脂香", "garnish": "米酒 (提味)",
            "formula": {"君": "鮮牛肉", "臣": "大骨湯底", "佐": "薑絲去腥", "使": "米酒提鮮"},
            "risks": {"薑": "過量會辛辣刺口"}
        }
    },
    "基隆市": {
        "營養三明治": {
            "award": "", "base": 4.3, "support": 4.0, "refine": 4.5, "finish": 3.5,
            "main": "高筋炸麵包", "spices": "黑胡椒 (火腿用)", "sauce": "台式甜味美乃滋",
            "oil": "炸油", "garnish": "小黃瓜、滷蛋、番茄",
            "formula": {"君": "炸麵包", "臣": "滷蛋火腿", "佐": "小黃瓜解膩", "使": "美乃滋"},
            "risks": {"黑胡椒": "過量會壓主味"}
        }
    }
}

counties = ["基隆市", "臺北市", "新北市", "桃園市", "新竹縣", "新竹市", "苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"]

# 4. UI 介面
st.title("🍜 TAD-AGE 台灣小吃 Formula 料理研究平台")

c1, c2 = st.columns(2)
with c1:
    sel_county = st.selectbox("📍 選擇縣市", counties, index=13) # 預設台南
with c2:
    available_snacks = snack_library.get(sel_county, {"預設小吃": {"base":3, "support":3, "refine":3, "finish":3, "main":"待補充", "spices":"待補充", "sauce":"待補充", "oil":"待補充", "garnish":"待補充", "formula":{}, "risks":{}}})
    sel_snack_name = st.selectbox("🍴 選擇小吃 (讀取配方檔案...)", list(available_snacks.keys()))
    data = available_snacks[sel_snack_name]

st.markdown("---")

# 主畫面：料理 Formula 卡片
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown(f"<div class='formula-card'>", unsafe_allow_html=True)
    # 標題與徽章
    badge = f"<span class='badge-bib'>😋 Bib</span>" if data.get('award')=="Bib" else (f"<span class='badge-michelin'>⭐ Michelin</span>" if data.get('award')=="Michelin" else "")
    st.markdown(f"<h3>{sel_snack_name} {badge}</h3>", unsafe_allow_html=True)
    
    # 料理組成 (小吃22 檔案內容)
    st.markdown("<div class='section-title'>📦 料理組成元素 (Formula Card)</div>", unsafe_allow_html=True)
    f_c1, f_c2 = st.columns(2)
    with f_c1:
        st.write("**主食材 (君):**")
        st.markdown(f"<span class='ingredient-tag'>{data['main']}</span>", unsafe_allow_html=True)
        st.write("**醬料/湯底 (臣):**")
        st.markdown(f"<span class='ingredient-tag'>{data['sauce']}</span>", unsafe_allow_html=True)
    with f_c2:
        st.write("**辛香料 (佐):**")
        st.markdown(f"<span class='ingredient-tag'>{data['spices']}</span>", unsafe_allow_html=True)
        st.write("**清香/收尾 (使):**")
        st.markdown(f"<span class='ingredient-tag'>{data['garnish']}</span>", unsafe_allow_html=True)

    # 香料風險 (小吃55 檔案內容)
    if data['risks']:
        st.markdown("<div class='section-title'>⚠️ 香料應用風險與修正</div>", unsafe_allow_html=True)
        for s, risk in data['risks'].items():
            st.markdown(f"**{s}**: <span class='risk-text'>{risk}</span>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='formula-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊 君臣佐使結構比重</div>", unsafe_allow_html=True)
    
    df_radar = pd.DataFrame(dict(
        r=[data['base'], data['support'], data['refine'], data['finish'], 4.0],
        theta=['主題感 (君)', '支撐度 (臣)', '修飾度 (佐)', '清亮感 (使)', '穿透力']
    ))
    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#d4a373')
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), margin=dict(l=30,r=30,t=30,b=30))
    st.plotly_chart(fig, use_container_width=True)
    
    # 結構說明
    if data['formula']:
        for role, desc in data['formula'].items():
            st.markdown(f"**{role}** : {desc}")
    st.markdown("</div>", unsafe_allow_html=True)

# 底部修正提醒
st.info(f"💡 **料理建議：** 根據系統分析，『{sel_snack_name}』的主題強度為 {data['base']}。若要提升層次，建議優化『{list(data['formula'].keys())[1]}』的厚度。")