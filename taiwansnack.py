import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃開發平台 V3.6", layout="wide")

# 2. 建立全台 22 縣市完整研發資料庫 (強化碗粿細節)
@st.cache_data
def load_enhanced_taiwan_db():
    # 22 縣市小吃清單
    snack_db = {
        "基隆市": ["鼎邊銼", "天婦羅", "營養三明治", "豆乾包", "泡泡冰"],
        "台北市": ["蚵仔煎", "牛肉麵", "滷肉飯", "刈包", "生煎包"],
        "新北市": ["阿給", "深坑臭豆腐", "九份芋圓", "金山鴨肉", "鶯歌壽司"],
        "桃園市": ["大溪豆乾", "龍岡米干", "石門活魚", "潤餅", "排骨飯"],
        "新竹市": ["貢丸湯", "米粉", "水蒸蛋糕", "潤餅", "肉圓"],
        "新竹縣": ["粄條", "仙草雞", "擂茶", "菜包", "柿餅"],
        "苗栗縣": ["水晶餃", "客家小炒", "麻糬", "薑絲大腸", "煨湯"],
        "台中市": ["太陽餅", "大腸包小腸", "炒麵", "台中肉員", "麻薏湯"],
        "彰化縣": ["肉圓", "爌肉飯", "貓鼠麵", "糯米炸", "蛤仔麵"],
        "南投縣": ["意麵", "肉圓", "竹筒飯", "扣仔嗲", "茶梅"],
        "雲林縣": ["鵝肉", "鴨肉飯", "圓仔冰", "當歸鴨", "肉羹"],
        "嘉義市": ["火雞肉飯", "美乃滋涼麵", "砂鍋魚頭", "豆花", "米糕"],
        "嘉義縣": ["民雄鵝肉", "奮起湖便當", "東石蚵仔", "苦茶油雞", "黑根"],
        "台南市": ["碗粿", "蝦仁飯", "擔仔麵", "牛肉湯", "鱔魚意麵"],
        "高雄市": ["鍋燒意麵", "海鮮粥", "旗魚黑輪", "鴨肉珍", "烤黑輪"],
        "屏東縣": ["萬巒豬腳", "肉粿", "黑鮪魚", "冷熱冰", "粄條"],
        "宜蘭縣": ["肉羹", "蔥油餅", "糕渣", "卜肉", "鴨賞"],
        "花蓮縣": ["液香扁食", "炸蛋蔥油餅", "公正包子", "麻糬", "周家蒸餃"],
        "台東縣": ["卑南肉包", "米苔目", "豬血湯", "地瓜酥", "池上便當"],
        "澎湖縣": ["仙人掌冰", "黑糖糕", "小管麵線", "金瓜米粉", "花枝丸"],
        "金門縣": ["廣東粥", "燒餅", "貢糖", "油條", "炒泡麵"],
        "連江縣": ["老酒麵線", "繼光餅", "紅糟肉", "魚麵", "鼎邊糊"]
    }
    
    # 核心配方與人性化料理法
    formula_detail = {
        "碗粿": {
            "君": "在來米漿 (混入肉燥汁)", 
            "臣": "鹹蛋黃、香菇、瘦肉塊", 
            "佐": "火燒蝦、紅蔥頭", 
            "使": "特製蒜泥甜油膏",
            "steps": [
                "1. **漿料調製**：選用舊在來米磨漿，加入冷水與滾水調成糊狀，關鍵是混入少量滷肉汁賦予米漿褐色與油香。",
                "2. **爆香內餡**：以豬油炒香紅蔥頭，加入香菇絲、肉塊與火燒蝦翻炒至香氣逸散。",
                "3. **裝碗定型**：將炒好的餡料與半顆鹹蛋黃放入碗中，填入米漿至八分滿。",
                "4. **蒸製工藝**：大火蒸約 20-25 分鐘。熄火後需『靜置冷卻』，米漿才會轉為Q彈。回溫後碗中微凹是正宗標誌。",
                "5. **風味收尾**：食用前淋上含蒜泥的偏甜油膏，平衡鹹香口感。"
            ]
        },
        "蝦仁飯": {
            "君": "火燒蝦仁", "臣": "高湯拌米飯", "佐": "柴魚醬油/青蔥", "使": "豬油",
            "steps": ["1. 蝦仁去腸泥與豬油爆炒", "2. 以柴魚湯底與白飯同煮吸飽湯汁", "3. 加入蝦仁合炒並撒上青蔥提亮"]
        }
    }
    
    # 縣市平均數值
    scores = {c: [4.5, 4.0, 3.5, 2.5, 4.0] for c in snack_db.keys()}
    scores["台南市"] = [5.0, 5.0, 4.5, 1.5, 5.0] # 強調支撐與收尾
    
    return snack_db, formula_detail, scores

snack_db, formula_db, score_db = load_enhanced_taiwan_db()

# --- UI 開始 ---
st.title("🇹🇼 TAD-AGE 台灣小吃研發平台 V3.6")

# 3. 左側選單
st.sidebar.header("🧭 導覽中心")
selected_county = st.sidebar.selectbox("1. 選擇縣市", list(snack_db.keys()), index=13) # 預設台南

available_snacks = snack_db.get(selected_county, [])
selected_snack = st.sidebar.selectbox(f"2. {selected_county} 代表小吃", available_snacks)

# 4. 右側主畫面
col_info, col_radar = st.columns([1.2, 1])

with col_info:
    st.header(f"🗂️ 風味模擬卡：{selected_snack}")
    
    # 取得具體食材與步驟
    recipe = formula_db.get(selected_snack, {
        "君": "在地主料", "臣": "結構配材", "佐": "調味層次", "使": "導向收尾",
        "steps": ["1. 準備食材", "2. 依照比例烹煮", "3. 加入調味", "4. 完成"]
    })
    
    # 顯示食材解構
    st.subheader("🧪 風味解構 (Structure)")
    st.info(f"""
    * **【君】核心主味：** `{recipe['君']}`
    * **【臣】中段支撐：** `{recipe['臣']}`
    * **【佐】修飾平衡：** `{recipe['佐']}`
    * **【使】風味導向：** `{recipe['使']}`
    """)
    
    # 顯示料理方法
    st.subheader("👨‍🍳 研發實作步驟 (Method)")
    for step in recipe['steps']:
        st.write(step)

with col_radar:
    st.header("📊 風味雷達圖")
    s_vals = score_db.get(selected_county, [4, 4, 3, 3, 3])
    
    radar_df = pd.DataFrame(dict(
        r=s_vals,
        theta=['主題', '支撐', '修飾', '清亮', '收尾']
    ))
    
    fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#E63946', fillcolor='rgba(230, 57, 70, 0.3)')
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("TAD-AGE System | 數據驅動之台灣文化保存模組")