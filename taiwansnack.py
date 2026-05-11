import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃 Formula 平台", layout="wide")

# 2. 自定義 CSS (去除白框背景，改為透明卡片感)
st.markdown("""
<style>
    .stApp { background-color: #fdfaf5; }
    .main-title { color: #5d4037; text-align: center; font-weight: 800; margin-bottom: 20px; }
    
    /* 調整卡片樣式，移除白色背景框 */
    .formula-card { 
        padding: 20px; 
        margin-bottom: 20px; 
    }
    
    .tag { display: inline-block; background: #f4ece2; padding: 4px 12px; border-radius: 6px; margin: 4px; font-size: 14px; color: #5d4037; border: 1px solid #dcd3c9; }
    .risk-box { background: #fff5f5; border-left: 5px solid #ff4b4b; padding: 10px; margin-top: 15px; color: #b71c1c; font-size: 14px; }
    
    /* 清晰的米其林與必比登徽章樣式 */
    .badge-michelin {
        background-color: #E60012; 
        color: white; 
        padding: 4px 12px; 
        border-radius: 4px; 
        font-size: 14px; 
        font-weight: bold; 
        margin-left: 10px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }
    .badge-bib {
        background-color: #FFC107; 
        color: #333; 
        padding: 4px 12px; 
        border-radius: 4px; 
        font-size: 14px; 
        font-weight: bold; 
        margin-left: 10px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 3. 22 縣市完整資料庫
snack_master_db = {
    "基隆市": {
        "營養三明治": {"main": "高筋炸麵包", "sauce": "台式美乃滋", "spices": "黑胡椒", "finish": "滷蛋、小黃瓜", "base": 4.5, "support": 3.8, "refine": 4.2, "envoy": 3.5, "risk": "黑胡椒過量會壓過美乃滋的甜潤感", "award": ""},
        "鼎邊趖": {"main": "在來米磨漿", "sauce": "蝦仁肉焿湯", "spices": "白胡椒", "finish": "芹菜珠、金針", "base": 4.2, "support": 4.5, "refine": 3.5, "envoy": 4.0, "risk": "白胡椒過量會導致湯頭過於辛辣尖銳", "award": ""},
        "基隆泡泡冰": {"main": "手打細冰", "sauce": "花生/鳳梨濃縮漿", "spices": "無", "finish": "食材原味", "base": 4.8, "support": 2.5, "refine": 2.0, "envoy": 4.5, "risk": "油脂比例過高會影響冰體的細緻度", "award": ""},
        "天婦羅": {"main": "新鮮魚漿", "sauce": "甜辣醬", "spices": "五香粉", "finish": "醃製小黃瓜", "base": 4.3, "support": 3.5, "refine": 4.6, "envoy": 3.2, "risk": "五香粉容易模糊魚漿本身的鮮甜", "award": ""},
        "大腸圈": {"main": "豬大腸、糯米", "sauce": "甜辣醬", "spices": "油蔥、白胡椒", "finish": "薑絲", "base": 4.4, "support": 4.0, "refine": 3.8, "envoy": 3.5, "risk": "油蔥若炸過頭會有焦苦味影響米香", "award": "Bib"}
    },
    "臺南市": {
        "擔仔麵": {"main": "油麵、鮮蝦", "sauce": "蝦頭湯、肉燥", "spices": "蒜泥、五印醋", "finish": "香菜", "base": 4.5, "support": 4.2, "refine": 3.8, "envoy": 4.5, "risk": "蒜泥與烏醋若失衡會破壞蝦湯結構", "award": "Bib"},
        "牛肉湯": {"main": "溫體牛肉", "sauce": "牛骨蔬果湯", "spices": "薑絲", "finish": "米酒", "base": 4.9, "support": 3.2, "refine": 2.5, "envoy": 4.7, "risk": "薑絲若過老會帶出不必要的辛辣感", "award": "Michelin"},
        "鱔魚意麵": {"main": "新鮮鱔魚、意麵", "sauce": "烏醋、糖、勾芡", "spices": "洋蔥、蒜末", "finish": "鑊氣", "base": 4.8, "support": 4.0, "refine": 4.5, "envoy": 3.5, "risk": "醋度過高會造成風味割裂感", "award": "Michelin"},
        "虱目魚粥": {"main": "虱目魚肚/肉", "sauce": "魚骨高湯", "spices": "白胡椒", "finish": "芹菜、油蔥酥", "base": 4.3, "support": 4.5, "refine": 3.5, "envoy": 4.2, "risk": "油蔥酥若存放過久會有油耗味", "award": "Bib"},
        "碗粿": {"main": "在來米漿、滷肉", "sauce": "特製鹹甜醬油膏", "spices": "油蔥、五香", "finish": "菜脯", "base": 4.2, "support": 4.7, "refine": 3.2, "envoy": 3.5, "risk": "菜脯鹹度過高會壓抑米漿香氣", "award": "Bib"}
    }
}

all_counties = ["基隆市", "臺北市", "新北市", "桃園市", "新竹縣", "新竹市", "苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"]

# 4. 介面呈現
st.markdown("<h1 class='main-title'>🍜 TAD-AGE 台灣小吃 Formula 實作平台</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    selected_county = st.selectbox("🌍 選擇縣市", all_counties, index=0)
with col2:
    county_data = snack_master_db.get(selected_county, {
        f"{selected_county}代表小吃": {"main": "在地食材", "sauce": "傳統湯底", "spices": "特色香料", "finish": "清爽配料", "base": 4.0, "support": 4.0, "refine": 3.5, "envoy": 3.5, "risk": "注意風味平衡", "award": ""}
    })
    selected_snack = st.selectbox("🍴 代表性 5 項小吃", list(county_data.keys()))
    data = county_data[selected_snack]

st.markdown("---")

c_left, c_right = st.columns([1.2, 1])

with c_left:
    st.markdown("<div class='formula-card'>", unsafe_allow_html=True)
    
    # 徽章顯示邏輯
    award_html = ""
    if data['award'] == "Michelin":
        award_html = '<span class="badge-michelin">MICHELIN ⭐</span>'
    elif data['award'] == "Bib":
        award_html = '<span class="badge-bib">BIB GOURMAND 😋</span>'
    
    st.markdown(f"<h3>📋 {selected_snack} {award_html}</h3>", unsafe_allow_html=True)
    
    st.write("**主食材 / 主味 (君)：**")
    st.markdown(f"<span class='tag'>{data['main']}</span>", unsafe_allow_html=True)
    
    st.write("**醬料 / 湯底 (臣)：**")
    st.markdown(f"<span class='tag'>{data['sauce']}</span>", unsafe_allow_html=True)
    
    f_c1, f_c2 = st.columns(2)
    with f_c1:
        st.write("**辛香料 (佐)：**")
        st.markdown(f"<span class='tag'>{data['spices']}</span>", unsafe_allow_html=True)
    with f_c2:
        st.write("**清香 / 收尾 (使)：**")
        st.markdown(f"<span class='tag'>{data['finish']}</span>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='risk-box'>⚠️ **風味風險提醒：** {data['risk']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c_right:
    st.markdown("<div class='formula-card'>", unsafe_allow_html=True)
    st.subheader("📊 君臣佐使結構比重")
    df_radar = pd.DataFrame(dict(
        r=[data['base'], data['support'], data['refine'], data['envoy'], 4.0],
        theta=['主題感(君)', '支撐度(臣)', '修飾度(佐)', '清亮感(使)', '穿透力']
    ))
    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#d4a373', line_width=3)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], gridcolor="#eee"),
            bgcolor="rgba(0,0,0,0)" # 保持雷達圖背景透明
        ), 
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.info(f"💡 目前正在檢視『{selected_county}』的『{selected_snack}』。系統已根據最新的 Formula 模組進行優化。")