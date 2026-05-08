import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 資料庫建立：整合 22 縣市與米其林/必比登標註
# 建議未來可將此部分移至 data/snacks.py
SNACK_DB = {
    "新竹縣": {
        "仙草雞": {
            "michelin_star": 0,
            "bib_gourmand": True,
            "desc": "在地嚴選主料，搭配傳統炮製方法",
            "flavor": {"主題": 4, "支撐": 5, "修飾": 3, "清亮": 3, "收尾": 4}
        },
        "粄條": {
            "michelin_star": 0,
            "bib_gourmand": False,
            "desc": "傳統純米製作，口感Q彈",
            "flavor": {"主題": 4, "支撐": 3, "修飾": 4, "清亮": 2, "收尾": 3}
        },
        "擂茶": {"michelin_star": 0, "bib_gourmand": False, "desc": "客家傳統飲品", "flavor": {"主題": 5, "支撐": 4, "修飾": 3, "清亮": 2, "收尾": 5}}
    },
    # 你可以依此格式繼續加入其他 21 個縣市
}

# --- UI 介面開始 ---
st.set_page_config(page_title="TAD-AGE 台灣小吃風味平台", layout="wide")

# 側邊導覽中心
with st.sidebar:
    st.header("🧭 導覽中心")
    
    # 1. 選擇縣市
    all_cities = list(SNACK_DB.keys())
    selected_city = st.selectbox("1. 選擇縣市", all_cities if all_cities else ["請載入資料"])
    
    # 2. 選擇代表小吃 (動態加上獎項圖示)
    if selected_city in SNACK_DB:
        snack_options = SNACK_DB[selected_city]
        
        # 建立選單顯示名稱：若有獎項則加上圖示
        def get_label(name):
            info = snack_options[name]
            label = name
            if info["michelin_star"] > 0: label += f" ⭐{info['michelin_star']}"
            if info["bib_gourmand"]: label += " 😋"
            return label

        selected_snack_name = st.selectbox("2. 代表小吃", list(snack_options.keys()), format_func=get_label)
        snack_info = snack_options[selected_snack_name]
    else:
        st.error("找不到縣市資料")

# 主畫面標題
st.title("🍜 TAD-AGE 台灣小吃風味平台 V3")

if selected_city and selected_snack_name:
    col1, col2 = st.columns([1, 1])

    with col1:
        # 顯示小吃標題與獎項標籤
        award_html = ""
        if snack_info["michelin_star"] > 0:
            award_html += f'<span style="background-color: #E60012; color: white; padding: 2px 8px; border-radius: 4px; margin-right: 5px;">米其林 {snack_info["michelin_star"]} 星</span>'
        if snack_info["bib_gourmand"]:
            award_html += '<span style="background-color: #FFB300; color: black; padding: 2px 8px; border-radius: 4px;">必比登推介 😋</span>'
        
        st.markdown(f"### 風味模擬卡：{selected_snack_name} {award_html}", unsafe_allow_html=True)
        
        st.markdown("#### 🧱 結構解構")
        f = snack_info["flavor"]
        st.write(f"* **【君】核心主味**：{snack_info['desc']}")
        st.write(f"* **【臣】中段支撐**：骨架食材 (強度: {f['支撐']})")
        st.write(f"* **【佐】修飾平衡**：提升層次 (強度: {f['修飾']})")
        st.write(f"* **【使】風味導向**：收尾留香 (強度: {f['收尾']})")

        with st.expander("🍳 核心工藝 (炮製方法)", expanded=True):
            st.info(f"針對『{selected_snack_name}』的傳統作法，需注重『火候控管』與『投料順序』。")

    with col2:
        st.markdown("#### 📊 風味雷達圖")
        
        # 雷達圖繪製邏輯
        categories = list(snack_info["flavor"].keys())
        values = list(snack_info["flavor"].values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=selected_snack_name,
            line_color='#E64A19'
        ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("請從左側選單選擇縣市與小吃以開始模擬。")