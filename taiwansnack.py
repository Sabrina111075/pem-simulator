import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃 Formula 實作平台", layout="wide")

# 2. 自定義 CSS (完全移除白框，強化透明感與徽章)
st.markdown("""
<style>
    .stApp { background-color: #fdfaf5; }
    .main-title { color: #5d4037; text-align: center; font-weight: 800; margin-bottom: 20px; }
    .formula-container { background: transparent; padding: 0px; }
    .tag { display: inline-block; background: #f4ece2; padding: 4px 12px; border-radius: 6px; margin: 4px; font-size: 14px; color: #5d4037; border: 1px solid #dcd3c9; }
    .risk-box { background: #fff5f5; border-left: 5px solid #ff4b4b; padding: 15px; margin-top: 15px; color: #b71c1c; font-size: 14px; border-radius: 4px; }
    .michelin-star { background-color: #E60012; color: white; padding: 4px 12px; border-radius: 4px; font-size: 13px; font-weight: bold; margin-left: 10px; vertical-align: middle; }
    .bib-gourmand { background-color: #FFC107; color: #333; padding: 4px 12px; border-radius: 4px; font-size: 13px; font-weight: bold; margin-left: 10px; vertical-align: middle; }
</style>
""", unsafe_allow_html=True)

# 3. 讀取並清洗資料
@st.cache_data
def load_and_clean_data():
    try:
        df = pd.read_csv("小吃核心資料庫.csv")
        # 關鍵修正：移除所有欄位名稱與內容的前後空白
        df.columns = df.columns.str.strip()
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except Exception as e:
        st.error(f"讀取 CSV 出錯: {e}")
        return pd.DataFrame()

df = load_and_clean_data()

if not df.empty:
    st.markdown("<h1 class='main-title'>🍜 TAD-AGE 台灣小吃 Formula 實作平台</h1>", unsafe_allow_html=True)

    # 4. 縣市與小吃選單連動
    counties = df['縣市'].unique().tolist()
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        sel_county = st.selectbox("🌍 選擇縣市", counties)
    
    with col_sel2:
        # 根據縣市精準過濾
        filtered_df = df[df['縣市'] == sel_county]
        snack_list = filtered_df['小吃名稱'].tolist()
        sel_snack = st.selectbox("🍴 代表性小吃 (110項完整連動)", snack_list)
        
        # 提取該項小吃的完整數據
        s = filtered_df[filtered_df['小吃名稱'] == sel_snack].iloc[0]

    st.markdown("---")

    # 5. 畫面呈現
    c_left, c_right = st.columns([1.3, 1])

    with c_left:
        # 徽章判斷
        award_val = str(s.get('Michelin_Status', 'None'))
        award_html = ""
        if "Michelin" in award_val or "⭐" in award_val:
            award_html = '<span class="michelin-star">MICHELIN ⭐</span>'
        elif "Bib" in award_val or "必比登" in award_val:
            award_html = '<span class="bib-gourmand">BIB GOURMAND 😋</span>'

        st.markdown(f"<h3>📋 {sel_snack} {award_html}</h3>", unsafe_allow_html=True)
        
        # 配方組成 (對應 小吃22.csv 結構)
        st.write("**主食材 / 主味 (君)：**")
        st.markdown(f"<span class='tag'>{s['主食材/主味']}</span>", unsafe_allow_html=True)
        
        st.write("**醬料 / 湯底 (臣)：**")
        st.markdown(f"<span class='tag'>{s['醬料/湯底']}</span>", unsafe_allow_html=True)
        
        f_c1, f_c2 = st.columns(2)
        with f_c1:
            st.write("**辛香料 (佐)：**")
            st.markdown(f"<span class='tag'>{s['辛香料']}</span>", unsafe_allow_html=True)
        with f_c2:
            st.write("**清香 / 收尾 (使)：**")
            st.markdown(f"<span class='tag'>{s['清香/收尾']}</span>", unsafe_allow_html=True)
        
        # 風險提醒 (對應 小吃55.csv 結構)
        st.markdown(f"""
            <div class='risk-box'>
                <strong>⚠️ 風味風險 / 修正提醒：</strong><br>
                {s['風味風險/修正提醒']}
            </div>
        """, unsafe_allow_html=True)

    with c_right:
        st.subheader("📊 君臣佐使結構分析")
        
        # 雷達圖數據 (對應資料庫：主題、支撐、修飾、清亮、收尾)
        radar_df = pd.DataFrame(dict(
            r=[s['主題'], s['支撐'], s['修飾'], s['清亮'], s['收尾']],
            theta=['主題感(君)', '支撐度(臣)', '修飾度(佐)', '清亮感(使)', '收尾穿透']
        ))
        
        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', line_color='#d4a373', line_width=3)
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5], gridcolor="#eee")),
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"🧪 **建議香氣配比：**")
        st.caption(s['建議香氣配比'])

else:
    st.warning("⚠️ 請確認『小吃核心資料庫.csv』是否已正確上傳且欄位名稱無誤。")