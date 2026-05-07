import streamlit as st
import os

st.set_page_config(page_title="台灣小吃料理分析平台", layout="wide")

# 初始化「目前選中的小吃」狀態，預設為 None
if 'selected_snack' not in st.session_state:
    st.session_state.selected_snack = None

# --- 資料讀取函數 ---
def load_data():
    file_name = 'data.csv'
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='cp950') as f:
            lines = f.readlines()
        # 解析資料 (略過標題，並拆分欄位)
        return [line.strip().split(',') for line in lines[1:] if line.strip()]
    return []

raw_data = load_data()

# --- 側邊欄：縣市選擇 ---
with st.sidebar:
    st.header("🔍 篩選與導覽")
    
    # 提取不重複的縣市清單
    cities = sorted(list(set([item[0] for item in raw_data])))
    cities.insert(0, "全部縣市")
    
    selected_city = st.selectbox("請選擇縣市：", cities)
    
    st.write("---")
    if st.button("回首頁 / 清除選取"):
        st.session_state.selected_snack = None
        st.rerun()
    
    st.caption("開發者：Sabrina")

# --- 主畫面邏輯 ---
st.title("🍜 台灣小吃料理分析平台")

# 如果還沒點選特定小吃：顯示名單模式
if st.session_state.selected_snack is None:
    # 根據選取的縣市過濾資料
    if selected_city == "全部縣市":
        display_list = raw_data
    else:
        display_list = [d for d in raw_data if d[0] == selected_city]

    st.subheader(f"📍 {selected_city} 的道地名點 (共 {len(display_list)} 筆)")
    
    # 使用網格排版顯示小吃清單
    for item in display_list:
        with st.expander(f"🍴 {item[2]} ({item[3]})"):
            st.write(f"**主要食材：** {item[3]}")
            # 點擊按鈕進入詳細頁面
            if st.button(f"查看「{item[2]}」料理方法", key=item[2]):
                st.session_state.selected_snack = item
                st.rerun()

# 如果已經點選特定小吃：顯示詳細料理模式
else:
    snack = st.session_state.selected_snack
    
    # 回上一步的按鈕
    if st.button("⬅ 返回名單"):
        st.session_state.selected_snack = None
        st.rerun()
    
    st.divider()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.header(f"【{snack[2]}】")
        st.write(f"🏙️ **地區：** {snack[0]}")
        st.write(f"🥚 **主要食材：** {snack[3]}")
        
    with col2:
        st.subheader("👨‍🍳 料理方法與建議")
        method = snack[4] if len(snack) > 4 else "資料整理中..."
        st.info(method)