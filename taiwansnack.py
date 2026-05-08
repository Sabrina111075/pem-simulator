import streamlit as st

def display_snack_dashboard(selected_snack_data):
    # 1. 取得後端邏輯算出的榮譽類型與評分
    honor_type = selected_snack_data['Honor_Type']
    snack_name = selected_snack_data['小吃名稱']
    rating_scores = {
        "主題": selected_snack_data['主題發音度'],
        "支撐": selected_snack_data['中段支撐'],
        "前段": selected_snack_data['前段清亮']
        # 可根據 ScoreModel 擴充更多維度
    }

    # 2. 標題區塊：根據榮譽等級動態渲染
    title_col1, title_col2 = st.columns([0.7, 0.3])
    
    with title_col1:
        st.title(f"🍴 {snack_name} - 風味結構開發")
        st.caption(f"系統架構：TAD-AGE | 研發人員：Sabrina")

    with title_col2:
        # 動態顯示米其林標章
        if honor_type == "必比登推介":
            st.markdown(
                '<div style="background-color: #ff4b4b; color: white; padding: 10px; border-radius: 10px; text-align: center;">'
                '<strong>😋 Bib Gourmand</strong><br>必比登推介'
                '</div>', unsafe_allow_html=True
            )
        elif honor_type == "米其林入選":
            st.markdown(
                '<div style="background-color: #1e1e1e; color: #f9d71c; padding: 10px; border-radius: 10px; border: 1px solid #f9d71c; text-align: center;">'
                '<strong>⭐ Michelin Selected</strong><br>米其林入選'
                '</div>', unsafe_allow_html=True
            )

    st.divider()

    # 3. 風味結構卡 (加上視覺強化)
    st.subheader("📋 風味結構卡")
    
    # 如果是榮譽項目，卡片區塊給予淡淡的底色區隔
    bg_color = "#fff9e6" if honor_type != "一般推薦" else "#ffffff"
    
    cols = st.columns(len(rating_scores))
    for i, (label, score) in enumerate(rating_scores.items()):
        with cols[i]:
            st.markdown(
                f'<div style="background-color: {bg_color}; border: 1px solid #ddd; padding: 20px; border-radius: 10px; text-align: center;">'
                f'<small>{label}</small><br>'
                f'<span style="font-size: 24px; font-weight: bold;">{score}/5</span>'
                '</div>', unsafe_allow_html=True
            )

    # 4. 側邊欄過濾功能
    with st.sidebar:
        st.header("🔍 研發標的過濾")
        target_level = st.multiselect(
            "選擇榮譽等級",
            options=["一般推薦", "必比登推介", "米其林入選"],
            default=["一般推薦", "必比登推介", "米其林入選"]
        )