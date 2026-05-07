import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 頁面基礎設定
st.set_page_config(page_title="TAD-AGE 台灣小吃研發平台", layout="wide")

# 自定義 CSS 提升質感
st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    .spice-card {
        background-color: #fffdfa;
        border-left: 5px solid #ffb74d;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 強大資料讀取函數 (支援多重編碼與路徑)
@st.cache_data
def load_all_data():
    # --- 讀取小吃主資料庫 ---
    df_snack = None
    snack_files = ['data.csv', 'data.csv.csv', 'data.csv.txt']
    for f in snack_files:
        if os.path.exists(f):
            try:
                df_snack = pd.read_csv(f, encoding='utf-8')
                break
            except:
                try:
                    df_snack = pd.read_csv(f, encoding='cp950')
                    break
                except:
                    continue

    # --- 讀取材料香料聯動庫 ---
    df_spice = None
    spice_files = ['材料香料.csv', './材料香料.csv', '材料香料.csv.csv']
    for sf in spice_files:
        if os.path.exists(sf):
            try:
                # 優先嘗試台灣 Excel 常用的 cp950 編碼預防亂碼
                df_spice = pd.read_csv(sf, encoding='cp950')
                break
            except:
                try:
                    df_spice = pd.read_csv(sf, encoding='utf-8')
                    break
                except:
                    continue
                    
    return df_snack, df_spice

df, df_spice = load_all_data()

# 3. 主介面邏輯
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

    # --- 第一層：核心結構與雷達圖 ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"🥣 {selected_snack} - 風味結構卡")
        
        # 顯示評分指標
        m1, m2, m3 = st.columns(3)
        m1.metric("主題辨識度", f"{item['主題']}/5")
        m2.metric("中段支撐", f"{item['支撐']}/5")
        m3.metric("前段清亮", f"{item['清亮']}/5")

        # 君臣佐使配方細節
        st.write(f"🧬 **【君】主體：** {item['君']}")
        st.write(f"🛡️ **【臣】支撐：** {item['臣']}")
        st.write(f"🎨 **【佐】修飾：** {item['佐']}")
        st.write(f"🚀 **【使】導向：** {item['使']}")
        
        st.success(f"📌 **建議香氣配比：** \n{item['建議香氣配比']}")

    with col2:
        st.subheader("📊 五維風味雷達模型")
        radar_df = pd.DataFrame(dict(
            r=[item['主題'], item['支撐'], item['修飾'], item['清亮'], item['收尾']],
            theta=['主題(君)', '支撐(臣)', '修飾(佐)', '清亮(使/前)', '收尾(使/後)']
        ))
        
        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True, range_r=[0,5])
        fig.update_traces(fill='toself', line_color='#E64A19', fillcolor='rgba(230, 74, 25, 0.3)')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # --- 第二層：材料深度聯動解析 ---
    st.markdown("---")
    st.subheader("🧪 核心材料/香料深度解析 (聯動系統)")
    
    if df_spice is not None:
        # 抓取小吃配方中的「辛香料」欄位文字
        current_spices_str = str(item['辛香料'])
        
        # 比對聯動庫中的材料名稱
        matched_spices = df_spice[df_spice['材料/香料'].apply(lambda x: str(x) in current_spices_str and str(x) != 'nan')]
        
        if not matched_spices.empty:
            for index, spice in matched_spices.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="spice-card">
                        <h4>🔍 材料解析：{spice['材料/香料']} ({spice['常見角色']})</h4>
                        <p><b>主要作用：</b> {spice['主要作用']}</p>
                        <p><b>適用類型：</b> {spice['適用小吃類型']}</p>
                        <p style="color:#d32f2f;"><b>使用風險：</b> {spice['風險']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(f"💡 該小吃配方「{current_spices_str}」尚未在材料庫中匹配到對應資料。")
    else:
        st.error("❌ 系統偵測到『材料香料.csv』存在，但內容讀取失敗（可能是編碼問題）。請嘗試將 CSV 另存為 UTF-8 格式。")

    # --- 第三層：風險提示 ---
    st.divider()
    st.warning(f"⚠️ **研發風險提示：** {item['風味風險/修正提醒']}")
    st.caption("© 2026 Sabrina's TAD-AGE System | 數據驅動風味開發平台")

else:
    st.error("❌ 無法載入主資料庫 (data.csv)。請確認檔案已上傳至 GitHub 根目錄。")