import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃開發平台 V3", layout="wide")

# 2. 擴充資料庫：加入詳細料理步驟 (依據核心資料庫邏輯)
@st.cache_data
def load_full_service_db():
    # 22 縣市與小吃清單 (維持先前補齊的狀態)
    county_mapping = {
        "基隆市": ["鼎邊銼", "天婦羅", "營養三明治", "泡泡冰", "豆乾包"],
        "台北市": ["蚵仔煎", "刈包", "牛肉麵", "滷肉飯", "生煎包"],
        "台南市": ["擔仔麵", "牛肉湯", "碗粿", "鱔魚意麵", "虱目魚粥"],
        "彰化縣": ["肉圓", "爌肉飯", "貓鼠麵", "糯米炸", "蛤仔麵"],
        # ... 其他縣市維持前版定義
    }
    
    # 詳細研發實作步驟 (範例)
    cooking_steps = {
        "鼎邊銼": ["1. 準備在來米漿，沿大鍋邊緣澆淋成片", "2. 待米漿乾後撕下切塊備用", "3. 熬製海鮮高湯，加入乾蝦仁、香菇提鮮", "4. 加入肉羹、花枝羹與米漿片同煮", "5. 出鍋前撒上蒜酥、芹菜與白胡椒"],
        "蚵仔煎": ["1. 調製地瓜粉水（關鍵比例影響Q度）", "2. 平底鍋熱油，放入鮮蚵煎至五分熟", "3. 倒入粉漿並打入雞蛋，放上小白菜", "4. 待底部焦脆後翻面煎熟", "5. 淋上特製甜辣醬（使）完成風味"],
        "擔仔麵": ["1. 以鮮蝦頭熬煮清甜湯底", "2. 麵條快速川燙維持Q彈", "3. 淋上長時間慢滷的精華肉燥（佐）", "4. 放入一尾鮮蝦與少許蒜泥", "5. 滴入烏醋並撒上香菜提亮風味"],
        "肉圓": ["1. 準備肉餡，以五香粉與筍丁拌勻（臣）", "2. 模具抹油放入地瓜粉漿與肉餡再包覆", "3. 蒸熟後靜置冷卻增加韌性", "4. 放入低溫油鍋慢慢『泡』熟而非猛炸", "5. 淋上甜米醬與香菜導向收尾"]
    }
    
    # 米其林榮譽資料
    michelin_db = {
        "蚵仔煎": {"status": "街頭小吃推薦", "note": "傳統圓環風味，粉漿與火侯的極致工藝。"},
        "刈包": {"status": "必比登推薦", "note": "肥瘦比例可選，酸菜與花生粉達成完美修飾。"},
        "擔仔麵": {"status": "必比登推薦", "note": "百年的蝦頭湯底傳統，香氣穿透力極強。"}
    }
    
    # 縣市平均數值
    counties = list(county_mapping.keys())
    summary_data = pd.DataFrame({
        "縣市": counties,
        "主題": [4.6, 5.0, 5.0, 4.8], # 簡化示範
        "支撐": [3.2, 4.0, 5.0, 4.0],
        "修飾": [2.4, 3.4, 4.2, 3.2],
        "清亮": [3.4, 2.2, 2.0, 2.2],
        "收尾": [2.0, 4.0, 5.0, 3.4]
    })
    
    return summary_data, county_mapping, michelin_db, cooking_steps

df_summary, snack_db, michelin_db, cooking_db = load_full_service_db()

# --- UI 開始 ---
st.title("🇹🇼 TAD-AGE 台灣小吃開發平台 (研發實作版)")

# 3. 左側側邊欄
st.sidebar.header("🧭 導覽中心")
selected_county = st.sidebar.selectbox("1. 選擇縣市", df_summary["縣市"])

available_snacks = snack_db.get(selected_county, ["資料待補"])
display_names = [f"{s} (Bib)" if s in michelin_db else s for s in available_snacks]
selected_display_name = st.sidebar.selectbox(f"2. {selected_county} 代表小吃", display_names)
selected_snack = selected_display_name.replace(" (Bib)", "")

st.sidebar.divider()
st.sidebar.info("💡 研發建議：按照右側步驟實作時，可對照雷達圖調整香料比例。")

# 4. 右側主畫面佈局
col_info, col_radar = st.columns([1, 1.2])

with col_info:
    st.header(f"🗂️ 風味模擬卡：{selected_snack}")
    
    # 米其林標記
    if selected_snack in michelin_db:
        st.warning(f"🏆 **{michelin_db[selected_snack]['status']}** | {michelin_db[selected_snack]['note']}")
    
    # A. 君臣佐使結構
    st.subheader("🧪 風味解構 (Structure)")
    st.markdown(f"""
    - **【君】核心**：主體食材開發
    - **【臣】骨架**：中段飽滿感支撐
    - **【佐】修飾**：解膩與平衡層次
    - **【使】導向**：氣味穿透與收尾
    """)
    
    # B. 新增：研發實作步驟
    st.subheader("👨‍🍳 研發實作步驟 (Method)")
    steps = cooking_db.get(selected_snack, ["1. 準備食材", "2. 根據風味分數進行調味", "3. 執行傳統工藝步驟", "4. 完成裝盤並添加收尾香料"])
    for step in steps:
        st.write(step)

with col_radar:
    st.header("📊 風味雷達圖 (縣市基準)")
    # 取得當前縣市數值
    try:
        c_data = df_summary[df_summary["縣市"] == selected_county].iloc[0]
        radar_df = pd.DataFrame(dict(
            r=[c_data['主題'], c_data['支撐'], c_data['修飾'], c_data['清亮'], c_data['收尾']],
            theta=['主題', '支撐', '修飾', '清亮', '收尾']
        ))
        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', line_color='#E63946', fillcolor='rgba(230, 57, 70, 0.3)')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("暫無該縣市數據")

st.divider()
st.caption("TAD-AGE System: 結合《核心資料庫》與《米其林指南》之全方位研發工具")