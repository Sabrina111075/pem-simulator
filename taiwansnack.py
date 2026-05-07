import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 頁面基礎設定
st.set_page_config(page_title="TAD-AGE 台灣小吃研發平台", layout="wide")

# 自定義 CSS 讓介面更專業
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 自動偵測編碼並讀取資料
@st.cache_data
def load_all_data():
    df_snack = None
    # 嘗試讀取小吃主資料
    for f in ['data.csv', 'data.csv.csv', 'data.csv.txt']:
        if os.path.exists(f):
            try:
                df_snack = pd.read_csv(f, encoding='utf-8')
            except:
                df_snack = pd.read_csv(f, encoding='cp950')
            break
            
    # 嘗試讀取材料香料庫 (處理中文亂碼)
    df_spice = None
    spice_file = '材料香料.csv'
    if os.path.exists(spice_file):
        try:
            df_spice = pd.read_csv(spice_file, encoding='utf-8')
        except:
            try:
                df_spice = pd.read_csv(spice_file, encoding='cp950')
            except:
                st.error("⚠️ 材料香料庫編碼錯誤，請確認存檔格式為 CSV (UTF-8)")
                
    return df_snack, df_spice

df, df_spice = load_all_data()

# 3. 介面邏輯
if df is not None:
    st.title("🇹🇼 台灣小吃風味開發決策平台")
    st.caption("系統架構：TAD-AGE (Table-Driven + AI-Generated Environment) | 研發者：Sabrina")
    st.markdown("---")

    # 側邊欄設定
    st.sidebar.header("📍 研發標的選擇")
    county = st.sidebar.selectbox("1. 選擇目標縣市", df['縣市'].unique())
    snack_options = df[df['縣市'] == county]['小吃名稱'].unique()
    selected_snack = st.sidebar.selectbox("2. 選擇小吃菜單", snack_options)

    # 取得當前小吃詳細資料
    item = df[(df['縣市'] == county) & (df['小吃名稱'] == selected_snack)].iloc[0]

    # --- 佈局：上方核心資訊 ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"🥣 {selected_snack} - 風味結構卡")
        
        # 顯示評分指標
        m1, m2, m3 = st.columns(3)
        m1.metric("主題辨識度", f"{item['主題']}/5")
        m2.metric("中段支撐", f"{item['支撐']}/5")
        m3.metric("前段清亮", f"{item['清亮']}/5")

        # 君臣佐使細節
        with st.container():
            st.write(f"🧬 **【君】主體：** {item['君']}")
            st.write(f"🛡️ **【臣】支撐：** {item['臣']}")
            st.write(f"🎨 **【佐】修飾：** {item['佐']}")
            st.write(f"🚀 **【使】導向：** {item['使']}")
        
        st.success(f"📌 **建議香氣配比：** \n{item['建議香氣配比']}")

    with col2:
        st.subheader("📊 風味維度雷達模型")
        # 準備雷達圖數據
        radar_df = pd.DataFrame(dict(
            r=[item['主題'], item['支撐'], item['修飾'], item['清亮'], item['收尾']],
            theta=['主題(君)', '支撐(臣)', '修飾(佐)', '清亮(使/前)', '收尾(使/後)']
        ))
        
        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True, range_r=[0,5])
        fig.update_traces(fill='toself', line_color='#E64A19', fillcolor='rgba(230, 74, 25, 0.3)')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # --- 自動聯動：材料深度解析 ---
    st.markdown("---")
    st.subheader("🧪 核心材料/香料深度解析 (聯動)")
    
    if df_spice is not None:
        # 抓取小吃資料庫中的「辛香料」欄位文字
        current_spices = str(item['辛香料'])
        
        # 檢查材料庫中哪些材料出現在小吃配方中
        matched_spices = df_spice[df_spice['材料/香料'].apply(lambda x: str(x) in current_spices)]
        
        if not matched_spices.empty:
            for index, spice in matched_spices.iterrows():
                with st.expander(f"🔍 材料解析：{spice['材料/香料']} ({spice['常見角色']})", expanded=True):
                    sc1, sc2, sc3 = st.columns(3)
                    sc1.markdown(f"**主要作用：** \n{spice['主要作用']}")
                    sc2.markdown(f"**適用類型：** \n{spice['適用小吃類型']}")
                    # 風險欄位標紅處理
                    sc3.markdown(f"**使用風險：** \n<span style='color:#d32f2f'>{spice['風險']}</span>", unsafe_allow_html=True)
        else:
            st.info("💡 該小吃之核心辛香料尚未收錄於「材料香料.csv」中。")
    else:
        st.error("❌ 找不到聯動庫 (材料香料.csv)，請檢查檔案是否已上傳至 GitHub。")

    # 底部提醒
    st.divider()
    st.warning(f"⚠️ **研發風險提示：** {item['風味風險/修正提醒']}")
    st.caption("© 2026 Sabrina's TAD-AGE System | 數據驅動風味開發")

else:
    st.error("❌ 無法載入主資料庫，請檢查 data.csv 是否正確存在。")