import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TAD-AGE 台灣小吃開發平台", layout="wide")

# 定義核心資料庫 (君臣佐使食材 + 精簡步驟)
@st.cache_data
def load_optimized_db():
    # 這裡示範補齊幾個關鍵小吃，結構與碗粿一致
    snack_recipe_data = {
        "碗粿": {
            "ingredients": "舊在來米漿、滷肉燥汁、鹹蛋黃、香菇、瘦肉、火燒蝦、紅蔥頭",
            "structure": {"君": "米漿(含滷汁)", "臣": "肉塊/蛋黃", "佐": "火燒蝦", "使": "甜油膏"},
            "method": [
                "1. 在來米漿加入熱水與滷汁調成褐色糊狀。",
                "2. 碗底放入炒香的肉塊、香菇、蝦米與蛋黃。",
                "3. 填入米漿，大火蒸 25 分鐘。",
                "4. 熄火靜置冷卻至Q彈後，淋上蒜泥甜油膏。"
            ]
        },
        "鼎邊銼": {
            "ingredients": "在來米漿、肉羹、花枝羹、金針花、香菇、蝦米、芹菜、白胡椒",
            "structure": {"君": "米漿片", "臣": "雙羹(肉/花枝)", "佐": "海鮮底湯", "使": "芹菜胡椒"},
            "method": [
                "1. 將米漿沿大鍋邊緣澆淋，燙乾成片後撕下切塊。",
                "2. 以蝦米、香菇、金針熬製清甜高湯。",
                "3. 加入肉羹、花枝羹與米漿片同煮熟透。",
                "4. 撒上芹菜與白胡椒提味即可。"
            ]
        },
        "火雞肉飯": {
            "ingredients": "火雞肉、西螺米、紅蔥頭、豬油/雞油、陳年醬油、糖",
            "structure": {"君": "火雞肉絲", "臣": "白飯", "佐": "油蔥酥", "使": "特製雞油醬汁"},
            "method": [
                "1. 火雞肉燜熟後手撕成絲，保留肉汁。",
                "2. 以火雞油/豬油炸香紅蔥頭，製成油蔥酥。",
                "3. 將雞湯、醬油、糖熬成澆汁。",
                "4. 米飯鋪上肉絲，淋上雞油與醬汁，最後灑油蔥酥。"
            ]
        },
        "蚵仔煎": {
            "ingredients": "鮮蚵、雞蛋、地瓜粉水、小白菜、味噌、甜辣醬",
            "structure": {"君": "鮮蚵", "臣": "粉漿與雞蛋", "佐": "小白菜", "使": "味噌甜醬"},
            "method": [
                "1. 鮮蚵先下鍋煎至稍微縮水出鮮味。",
                "2. 倒入調好的地瓜粉漿並打入雞蛋。",
                "3. 放入小白菜，待粉漿邊緣焦酥後翻面。",
                "4. 淋上特製的味噌甜辣醬。"
            ]
        }
    }
    
    # 22 縣市清單 (全補齊)
    counties = ["基隆市", "台北市", "新北市", "桃園市", "新竹市", "新竹縣", "苗栗縣", "台中市", "彰化縣", "南投縣", "雲林縣", "嘉義市", "嘉義縣", "台南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "台東縣", "澎湖縣", "金門縣", "連江縣"]
    
    county_snack_map = {
        "基隆市": ["鼎邊銼", "天婦羅"],
        "台北市": ["蚵仔煎", "牛肉麵"],
        "台南市": ["碗粿", "蝦仁飯", "擔仔麵"],
        "嘉義市": ["火雞肉飯", "美乃滋涼麵"],
        # 其他縣市可依此邏輯快速擴充...
    }
    
    return counties, county_snack_map, snack_recipe_data

counties, county_map, recipes = load_optimized_db()

# --- Streamlit UI ---
st.title("🇹🇼 TAD-AGE 台灣小吃開發平台 (簡約實作版)")

st.sidebar.header("🧭 導覽中心")
sel_county = st.sidebar.selectbox("1. 選擇縣市", counties, index=13) # 預設台南

# 動態更新小吃選項
available_snacks = county_map.get(sel_county, ["資料擴充中..."])
sel_snack = st.sidebar.selectbox(f"2. {sel_county} 代表小吃", available_snacks)

# 右側主畫面
col_left, col_right = st.columns([1, 1])

with col_left:
    st.header(f"🍳 料理手札：{sel_snack}")
    
    if sel_snack in recipes:
        data = recipes[sel_snack]
        
        # 主要食材
        st.subheader("🛒 主要食材")
        st.write(data["ingredients"])
        
        # 君臣佐使
        st.subheader("🧪 風味結構")
        cols = st.columns(4)
        cols[0].metric("【君】", data["structure"]["君"])
        cols[1].metric("【臣】", data["structure"]["臣"])
        cols[2].metric("【佐】", data["structure"]["佐"])
        cols[3].metric("【使】", data["structure"]["使"])
        
        # 簡單料理方法
        st.subheader("📝 簡單料理方法")
        for step in data["method"]:
            st.markdown(step)
    else:
        st.info("該項小吃深度資料正在錄入中，請嘗試『碗粿』、『鼎邊銼』或『火雞肉飯』。")

with col_right:
    st.header("📊 風味平衡分析")
    # 這裡顯示雷達圖 (維持架構)
    radar_data = pd.DataFrame(dict(
        r=[4, 5, 3, 2, 4],
        theta=['主題', '支撐', '修飾', '清亮', '收尾']
    ))
    fig = px.line_polar(radar_data, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#E63946')
    st.plotly_chart(fig, use_container_width=True)