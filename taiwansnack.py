import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 頁面配置
st.set_page_config(page_title="TAD-AGE 台灣小吃 Formula 實作平台", layout="wide")

# 2. 移除白框與強化徽章視覺
st.markdown("""
<style>
    .stApp { background-color: #fdfaf5; }
    .main-title { color: #5d4037; text-align: center; font-weight: 800; margin-bottom: 20px; }
    .formula-card { padding: 10px; background: transparent; }
    .tag { display: inline-block; background: #f4ece2; padding: 4px 12px; border-radius: 6px; margin: 4px; font-size: 14px; color: #5d4037; border: 1px solid #dcd3c9; }
    .risk-box { background: #fff5f5; border-left: 5px solid #ff4b4b; padding: 15px; margin-top: 15px; color: #b71c1c; font-size: 14px; border-radius: 4px; }
    .michelin-star { background-color: #E60012; color: white; padding: 4px 12px; border-radius: 4px; font-size: 13px; font-weight: bold; margin-left: 10px; vertical-align: middle; }
    .bib-gourmand { background-color: #FFC107; color: #333; padding: 4px 12px; border-radius: 4px; font-size: 13px; font-weight: bold; margin-left: 10px; vertical-align: middle; }
</style>
""", unsafe_allow_html=True)

# 3. 讀取資料庫
@st.cache_data
def load_data():
    try:
        # 強制讀取並去除可能的空白字元
        df = pd.read_csv("小吃核心資料庫.csv")
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

df_master = load_data()

if not df_master.empty:
    st.markdown("<h1 class='main-title'>🍜 TAD-AGE 台灣小吃 Formula 實作平台</h1>", unsafe_allow_html=True)

    # 4. 縣市與小吃連動邏輯
    all_counties = df_master['縣市'].unique().tolist()
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        sel_county = st.selectbox("🌍 選擇縣市", all_counties)
    
    # 這裡是最關鍵的修正：確保選單根據縣市過濾
    with col_sel2:
        filtered_df = df_master[df_master['縣市'] == sel_county]
        snack_list = filtered_df['小吃名稱'].tolist()
        sel_snack_name = st.selectbox("🍴 代表性小吃", snack_list)
        
        # 取得該列所有資料
        s = filtered_df[filtered_df['小吃名稱'] == sel_snack_name].iloc[0]

    st.markdown("---")

    # 5. 畫面呈現
    c_left, c_right = st.columns([1.3, 1])

    with c_left:
        # 徽章顯示
        award_type = str(s.get('Michelin_Status', 'None'))
        award_html = ""
        if "Michelin" in award_type or "⭐" in award_type:
            award_html = '<span class="michelin-star">MICHELIN ⭐</span>'
        elif "Bib" in award_type or "必比登" in award_type:
            award_html = '<span class="bib-gourmand">BIB GOURMAND 😋</span>'

        st.markdown(f"<h3>📋 {sel_snack_name} {award_html}</h3>", unsafe_allow_html=True)
        
        # 直接對接 CSV 欄位名稱
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
        
        st.markdown(f"""
            <div class='risk-box'>
                <strong>⚠️ 風味風險/修正提醒：</strong><br>
                {s['風味風險/修正提醒']}
            </div>
        """, unsafe_allow_html=True)

    with c_right:
        st.subheader("📊 君臣佐使結構比重")
        
        # 依照您的 CSV 欄位繪製雷達圖
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
    st.error("找不到『小吃核心資料庫.csv』，請確認檔案名稱與路徑是否正確。")