import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 設置頁面標題
st.set_page_config(page_title="TAD-AGE 台灣小吃研發平台", layout="wide")

# 2. 單一數據源載入 (只讀取 CountySnackDB)
@st.cache_data
def load_data():
    try:
        # 直接讀取主資料表
        df = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        df.columns = df.columns.str.strip() # 移除標題空格
        return df
    except Exception as e:
        st.error(f"❌ 找不到關鍵檔案：CountySnackDB.csv。請確認檔案已上傳至目錄中。")
        return None

df = load_data()

if df is not None:
    # --- 側邊欄：導航控制 ---
    st.sidebar.header("📍 研發導航系統")
    counties = df['縣市'].unique()
    sel_county = st.sidebar.selectbox("第一步：選擇縣市", counties)
    
    # 過濾該縣市的小吃清單
    snack_options = df[df['縣市'] == sel_county]['小吃名稱'].unique()
    sel_snack = st.sidebar.selectbox("第二步：選擇研發品項", snack_options)
    
    # 提取該品項的數據列
    s = df[df['小吃名稱'] == sel_snack].iloc[0]

    # --- 主畫面：頭部標籤 ---
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.title(f"🍽️ {sel_snack}")
        st.caption(f"數據架構：TAD-AGE v3 | 縣市：{sel_county} | 信心等級：{s.get('資料信心等級', 'D')}")
    
    with col2:
        # 解決 KeyError 的關鍵：使用 .get 並對應正確欄位 Michelin_Status
        status = str(s.get('Michelin_Status', 'None'))
        if status != 'None' and status != 'nan' and status != '':
            st.error(f"😋 {status}") # 米其林紅標
        else:
            st.info("🏠 在地風味精選")

    st.divider()

    # --- 中間層：雷達圖與風味分析 ---
    left_col, right_col = st.columns([0.6, 0.4])
    
    with left_col:
        st.subheader("📊 風味五維模型")
        # 定義維度並確保轉換為數字，避免繪圖報錯
        dims = ['主題', '支撐', '修飾', '清亮', '收尾']
        vals = []
        for d in dims:
            raw_val = s.get(d, 0)
            try:
                # 強制轉換，如果失敗就給 0
                num_val = pd.to_numeric(raw_val, errors='coerce')
                vals.append(0.0 if pd.isna(num_val) else float(num_val))
            except:
                vals.append(0.0)
        
        # 繪製雷達圖
        radar_df = pd.DataFrame(dict(r=vals, theta=dims))
        fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', fillcolor='rgba(255, 75, 75, 0.3)', line_color='#FF4B4B')
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("🧪 君臣佐使配置")
        # 使用卡片式顯示
        st.success(f"**君 (主體)：** {s.get('君', '-')}")
        st.write(f"**臣 (支撐)：** {s.get('臣', '-')}")
        st.write(f"**佐 (修飾)：** {s.get('佐', '-')}")
        st.write(f"**使 (收尾)：** {s.get('使', '-')}")
        
        with st.expander("📝 建議香氣配比與提醒"):
            st.write(s.get('建議香氣配比', '尚無研究數據'))
            st.caption("修正提醒：")
            st.write(s.get('風味風險/修正提醒', '無'))

    # --- 底部：原始數據驗證 (僅供開發時查看，成功後可刪除) ---
    if st.checkbox("🔍 檢查原始數據欄位"):
        st.write(s)