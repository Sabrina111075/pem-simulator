import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 設定頁面語系與寬度
st.set_page_config(page_title="TAD-AGE 小吃結構解構模擬器", layout="wide")

# --- 1. 核心資料模型整合 (基於上傳檔案) ---
def load_framework_logic():
    # 整合 小吃10.csv 的角色定義
    roles = {
        "君 (Prime)": {"def": "主題核心：決定風味基調", "metrics": ["主題感", "前調"], "color": "#FF4B4B"},
        "臣 (Minister)": {"def": "中段支撐：撐起風味骨架", "metrics": ["支撐度", "中調"], "color": "#FFA15A"},
        "佐 (Assistant)": {"def": "修飾平衡：去腥解膩平衡", "metrics": ["修飾度", "平衡感"], "color": "#19D3F3"},
        "使 (Envoy)": {"def": "導向載體：引導與收尾", "metrics": ["清亮感", "後調"], "color": "#00CC96"}
    }
    
    # 整合 小吃55.csv 的材料與風險邏輯
    ingredients_db = {
        "白胡椒": {"role": "佐/使", "effect": "提氣、去腥、增加前段穿透", "risk": "過量會尖、粗"},
        "黑胡椒": {"role": "君/佐", "effect": "厚辛、暖辣、建立主題", "risk": "過量會壓主味"},
        "八角": {"role": "臣/佐", "effect": "滷香骨架、甜辛後段", "risk": "過量會藥味重"},
        "油蔥": {"role": "使/臣", "effect": "油香、香氣延展", "risk": "焦苦風險"},
        "香菜": {"role": "使", "effect": "清香收尾、解膩", "risk": "過多會蓋清湯"}
    }
    return roles, ingredients_db

roles_data, spice_db = load_framework_logic()

# --- 2. 側邊欄：參數輸入 (對應 小吃22.csv 模板) ---
st.sidebar.header("🛠️ 結構參數輸入 (TAD-AGE Model)")
snack_name = st.sidebar.text_input("小吃名稱", "台南胡椒餅 (模擬)")
base_score = st.sidebar.slider("核心主題強度 (君)", 0.0, 5.0, 4.5)
support_score = st.sidebar.slider("中段支撐強度 (臣)", 0.0, 5.0, 3.8)
refine_score = st.sidebar.slider("平衡修飾強度 (佐)", 0.0, 5.0, 2.5)
finish_score = st.sidebar.slider("清亮收尾強度 (使)", 0.0, 5.0, 3.0)

# --- 3. 主畫面佈局 ---
st.title(f"🍜 TAD-AGE: {snack_name} 風味結構解構系統")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎯 君臣佐使：權重與定義")
    # 顯示基於 小吃10.csv 的解構卡片
    for role, info in roles_data.items():
        with st.expander(f"{role} - {info['def']}"):
            st.write(f"**關鍵指標：** {', '.join(info['metrics'])}")
            if "君" in role: score = base_score
            elif "臣" in role: score = support_score
            elif "佐" in role: score = refine_score
            else: score = finish_score
            st.progress(score / 5.0)

with col2:
    st.subheader("📊 五維感官雷達圖 (Sensory Radar)")
    # 雷達圖邏輯
    df_radar = pd.DataFrame(dict(
        r=[base_score, support_score, refine_score, 4.0, finish_score], # 4.0為預設層次感
        theta=['主題感', '支撐度', '修飾度', '穿透力', '清亮感']))
    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#636EFA')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- 4. 風味時序譜系圖 (前、中、後調) ---
st.subheader("⏳ 風味時序譜系 (Time-Sequence Spectrum)")
time_data = {
    "階段": ["前調 (First Bite)", "中調 (Chewing)", "後調 (Aftertaste)"],
    "強度": [base_score, support_score, finish_score],
    "描述": ["主題衝擊", "風味骨架支撐", "香氣延展與收尾"]
}
df_time = pd.DataFrame(time_data)
fig_time = px.area(df_time, x="階段", y="強度", text="描述", 
                   title="風味動態演變曲線", color_discrete_sequence=['#FFA15A'])
st.plotly_chart(fig_time, use_container_width=True)

# --- 5. 自動化風險偵測系統 (基於 小吃55.csv) ---
st.subheader("⚠️ 風味風險預警 (Risk Analysis)")
r_col1, r_col2, r_col3 = st.columns(3)

# 邏輯判斷：若分數異常則觸發風險提示
with r_col1:
    if refine_score < 2.0:
        st.warning("【佐料不足】系統偵測：去腥或解膩能力較弱，可能存在油膩風險。")
    else:
        st.success("【平衡優良】修飾度足以覆蓋主料腥味。")

with r_col2:
    if base_score > 4.8:
        st.error("【君料過載】風險提醒：主題過於強烈，可能導致尖銳感 (參考：白胡椒風險)。")
    else:
        st.info("【主題穩定】風味中心明確。")

with r_col3:
    if finish_score > 4.5:
        st.warning("【使料溢出】收尾過重，可能蓋過清湯原味 (參考：香菜/芹菜效應)。")
    else:
        st.success("【收尾乾淨】後調導向清晰。")

# --- 6. 結構解構對照底表 ---
st.markdown("### 📋 結構解構邏輯矩陣")
st.table(pd.DataFrame({
    "解構角色": list(roles_data.keys()),
    "工程定義": [v["def"] for v in roles_data.values()],
    "模擬參數": [base_score, support_score, refine_score, finish_score],
    "建議對應材料": ["黑胡椒/肉類", "滷汁/八角", "薑/蒜/白胡椒", "油蔥/香菜"]
}))