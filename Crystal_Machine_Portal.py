import streamlit as st
import time

# --- 1. 頁面基本配置 ---
st.set_page_config(page_title="Crystal Machine Portal", layout="wide")

# --- 2. 模擬所需的資料結構（確保變數都存在） ---
# 這裡建立預設資料，避免 NameError 找不到變數
if "selected_vol" not in locals() and "selected_vol" not in globals():
    selected_vol = "Vol_01 (預設主機)"

health_metrics = {
    "心率 (Heart Rate)": "72 bpm",
    "血氧 (SpO2)": "98 %",
    "IMU 震幅 (Motion)": "0.12 g",
    "體溫 (Temperature)": "36.5 °C"
}

status_text = "目前數據穩定，邊緣端健康度 95%。持續監測中。"

# --- 3. 數據展示與大模型對話區塊（排版區） ---
left_panel, right_panel = st.columns([1, 1])

with left_panel:
    st.subheader(f"📊 實時監測數據看板({selected_vol.split(' ')[0]})")
    for metric_name, val in health_metrics.items():
        st.markdown(f"""
        <div class='data-card' style='background-color:#f9f9f9; padding:10px; border-radius:5px; margin-bottom:10px; border-left:5px solid #0099FF;'>
            <span style='color:#888; font-size:14px;'>{metric_name}</span><br>
            <span style='font-size:24px; font-weight:bold; color:#0099FF;'>{val}</span>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"💡 **狀態解讀**：{status_text}")

with right_panel:
    st.subheader("🤖 DEEPSEEK CORE 本地推理區塊")
    st.markdown("透過樹莓派 5 邊緣運算層直接調用 DeepSeek 離線大模型，完全保護病患隱私。請輸入護理人員的提問：")

    # 確保 session state 初始化
    if "chat_response" not in st.session_state:
        st.session_state.chat_response = ""
    if "loading" not in st.session_state:
        st.session_state.loading = False

    user_query = st.text_input("輸入您對生理數據的臨床疑問：", placeholder="例如：若長者心率驟降至50且IMU震幅異常，應觸發何種通報流程？")

    # 動態 key 綁定，防止前端組件衝突
    btn_key = f"deepseek_submit_btn_{len(user_query)}"

    if st.button("送出至 Edge AI 進行推理", type="primary", key=btn_key):
        if user_query:
            st.session_state.loading = True
            with st.spinner("樹莓派 5 邊緣神經網路引擎計算中..."):
                time.sleep(1.5)  # 模擬本地硬體推理延遲
                st.session_state.chat_response = f"【DeepSeek Edge AI 本地回覆】\n針對您詢問的問題：「{user_query}」\n基於當前系統載入的 Skill Card（醫療 Agent 知識庫），當偵測到此複合型異常時，建議立即啟動二級醫療通報，並透過邊緣端即時調校感測器採樣率。"
            st.session_state.loading = False
        else:
            st.warning("請輸入您的問題後再點擊送出。")

# --- 4. 顯示回應區域 ---
if st.session_state.chat_response:
    st.markdown("### 📋 邊緣推理結果：")
    st.success(st.session_state.chat_response)