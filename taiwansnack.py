import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 確保資料讀取與欄位清理
@st.cache_data
def get_final_data():
    try:
        # 讀取主資料庫
        df = pd.read_csv('snack_v3.xlsx - CountySnackDB.csv')
        df.columns = df.columns.str.strip() # 去除標題空格
        return df
    except Exception as e:
        st.error(f"資料讀取錯誤: {e}")
        return None

df = get_final_data()

if df is not None:
    # 側邊欄過濾邏輯
    st.sidebar.header("📍 TAD-AGE 研發導航")
    counties = df['縣市'].unique()
    selected_county = st.sidebar.selectbox("選擇縣市", counties)
    county_df = df[df['縣市'] == selected_county]
    selected_snack = st.sidebar.selectbox("選擇小吃", county_df['小吃名稱'])
    
    # 取得選定資料列
    s = county_df[county_df['小吃名稱'] == selected_snack].iloc[0]

    # --- 頂部標題 ---
    st.title(f"🍽️ {selected_snack}")
    st.divider()

    # --- 雷達圖保護邏輯 ---
    left_col, right_col = st.columns([0.6, 0.4])
    
    with left_col:
        try:
            # 定義維度並強制轉換為數值
            categories = ['主題', '支撐', '修飾', '清亮', '收尾']
            values = []
            for c in categories:
                val = s.get(c, 0)
                # 預防資料是字串或空值
                try:
                    values.append(float(val))
                except:
                    values.append(0.0)
            
            radar_df = pd.DataFrame(dict(r=values, theta=categories))
            
            # 建立雷達圖
            fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
            fig.update_traces(fill='toself', fillcolor='rgba(255, 75, 75, 0.3)', line_color='#FF4B4B')
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                showlegend=False,
                margin=dict(l=40, r=40, t=40, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as radar_err:
            st.warning(f"雷達圖渲染中：{radar_err}")
            st.info("請確認 CSV 檔案中的評分欄位（主題、支撐等）是否為數字。")

    with right_col:
        st.subheader("🧪 風味配比與角色")
        st.write(f"**君 (核心)：** {s.get('君', '-')}")
        st.write(f"**臣 (支撐)：** {s.get('臣', '-')}")
        st.write(f"**佐 (平衡)：** {s.get('佐', '-')}")
        st.write(f"**使 (收尾)：** {s.get('使', '-')}")
        
        st.info(f"**配比建議：**\n\n{s.get('建議香氣配比', '暫無資料')}")

    # --- 底部風險提示 ---
    with st.expander("📝 研發風險與修正提醒"):
        st.write(s.get('風味風險/修正提醒', '尚無具體備註'))