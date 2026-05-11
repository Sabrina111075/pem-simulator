import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃 Formula 實作平台", layout="wide")

# 2. 自定義 CSS (移除白框，強化專業徽章視覺)
st.markdown("""
<style>
    .stApp { background-color: #fdfaf5; }
    .main-title { color: #5d4037; text-align: center; font-weight: 800; margin-bottom: 20px; }
    
    /* 移除背景框 */
    .formula-section { padding: 5px; background: transparent; }
    
    .tag { display: inline-block; background: #f4ece2; padding: 4px 12px; border-radius: 6px; margin: 4px; font-size: 14px; color: #5d4037; border: 1px solid #dcd3c9; }
    .risk-box { background: #fff5f5; border-left: 5px solid #ff4b4b; padding: 15px; margin-top: 15px; color: #b71c1c; font-size: 14px; border-radius: 4px; }
    
    /* 專業徽章 */
    .michelin-star {
        background-color: #E60012; color: white; padding: 4px 12px; border-radius: 4px; 
        font-size: 13px; font-weight: bold; margin-left: 10px; vertical-align: middle;
    }
    .bib-gourmand {
        background-color: #FFC107; color: #333; padding: 4px 12px; border-radius: 4px; 
        font-size: 13px; font-weight: bold; margin-left: 10px; vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)

# 3. 讀取核心資料庫 (小吃核心資料庫.csv)
@st.cache_data
def load_data():
    # 讀取您上傳的 CSV 檔案
    df = pd.read_csv("小吃核心資料庫.csv")
    return df

df_master = load_data()

# 4. 側邊或頂部選擇邏輯
st.markdown("<h1 class='main-title'>🍜 TAD-AGE 台灣小吃 Formula 實作平台</h1>", unsafe_allow_html=True)

all_counties = df_master['縣市'].unique().tolist()

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    sel_county = st.selectbox("🌍 選擇縣市", all_counties)
with col_sel2:
    county_snacks = df_master[df_master['縣市'] == sel_county]
    sel_snack_name = st.selectbox("🍴 代表性小吃 (資料庫連動中)", county_snacks['小吃名稱'].tolist())
    # 取得該小吃的完整列資料
    snack_info = county_snacks[county_snacks['小吃名稱'] == sel_snack_name].iloc[0]

st.markdown("---")

# 5. 畫面呈現：料理 Formula 與 結構分析
c_left, c_right = st.columns([1.3, 1])

with c_left:
    st.markdown("<div class='formula-section'>", unsafe_allow_html=True)
    
    # 徽章邏輯
    award_html = ""
    m_status = str(snack_info.get('Michelin_Status', 'None'))
    if "Michelin" in m_status or "⭐" in m_status:
        award_html = '<span class="michelin-star">MICHELIN ⭐</span>'
    elif "Bib" in m_status or "必比登" in m_status:
        award_html = '<span class="bib-gourmand">BIB GOURMAND 😋</span>'
    
    st.markdown(f"<h3>📋 {sel_snack_name} {award_html}</h3>", unsafe_allow_html=True)
    
    # 從 CSV 欄位對接食材資訊
    st.write("**主食材 / 主味 (君)：**")
    st.markdown(f"<span class='tag'>{snack_info['主食材/主味']}</span>", unsafe_allow_html=True)
    
    st.write("**醬料 / 湯底 (臣)：**")
    st.markdown(f"<span class='tag'>{snack_info['醬料/湯底']}</span>", unsafe_allow_html=True)
    
    f_c1, f_c2 = st.columns(2)
    with f_c1:
        st.write("**辛香料 (佐)：**")
        st.markdown(f"<span class='tag'>{snack_info['辛香料']}</span>", unsafe_allow_html=True)
    with f_c2:
        st.write("**清香 / 收尾 (使)：**")
        st.markdown(f"<span class='tag'>{snack_info['清香/收尾']}</span>", unsafe_allow_html=True)
    
    # 風味風險提醒 (直接連動資料庫)
    st.markdown(f"""
        <div class='risk-box'>
            <strong>⚠️ 風味風險/修正提醒：</strong><br>
            {snack_info['風味風險/修正提醒']}
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c_right:
    st.markdown("<div class='formula-section'>", unsafe_allow_html=True)
    st.subheader("📊 君臣佐使結構比重")
    
    # 雷達圖數據連動 (使用 CSV 中的 主題, 支撐, 修飾, 清亮 等欄位)
    df_radar = pd.DataFrame(dict(
        r=[
            snack_info['主題'], 
            snack_info['支撐'], 
            snack_info['修飾'], 
            snack_info['清亮'], 
            snack_info['收尾']
        ],
        theta=['主題感(君)', '支撐度(臣)', '修飾度(佐)', '清亮感(使)', '收尾穿透力']
    ))
    
    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#d4a373', line_width=3)
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5], gridcolor="#eee")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=50, t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 顯示建議香氣配比文字
    st.write(f"**🧪 建議香氣配比：**")
    st.caption(snack_info['建議香氣配比'])
    st.markdown("</div>", unsafe_allow_html=True)

# 6. 底部連動腳註
st.caption(f"數據來源：{snack_info['來源名稱']} | 資料信心等級：{snack_info['資料信心等級']}")