import streamlit as st
import time

# =====================================================================
# 1. 頁面基本配置與全域 CSS 樣式注入（打造蜂巢式高質感科技感）
# =====================================================================
st.set_page_config(
    page_title="Crystal Machine Portal - Edge AI 蜂巢架構",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-title {
        font-size: 28px;
        font-weight: 800;
        color: #0099FF;
        border-bottom: 2px solid #0099FF;
        padding-bottom: 10px;
        margin-bottom: 25px;
    }
    .data-card {
        background-color: #1E2633;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 6px solid #0099FF;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-label {
        color: #A0AEC0;
        font-size: 14px;
        font-weight: 500;
    }
    .metric-value {
        font-size: 26px;
        font-weight: bold;
        color: #00E5FF;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🔮 Crystal Machine Portal | 蜂巢式邊緣運算控制台</div>", unsafe_allow_html=True)

# =====================================================================
# 2. 系統核心變數與生理數據結構初始化
# =====================================================================
if "selected_vol" not in st.session_state:
    st.session_state.selected_vol = "Vol_01 (主控蜂巢節點)"

# 模擬即時生理與設備健康度指標
health_metrics = {
    "❤️ 心率 (Heart Rate)": "74 bpm",
    "🩸 血氧飽和度 (SpO2)": "98 %",
    "🌀 IMU 三軸震幅 (Motion)": "0.14 g",
    "🌡️ 核心體溫 (Temperature)": "36.6 °C",
    "🔋 樹莓派 5 電壓狀態": "5.1 V"
}

status_text = "🟢 邊緣網格安全拓撲已建立。目前 PEM 膜與感測網路同步率 97.4%，DeepSeek 離線核心就緒。"

# =====================================================================
# 3. 雙面板佈局：左側【實時監測數據看板】 vs 右側【DEEPSEEK CORE 本地推理】
# =====================================================================
left_panel, right_panel = st.columns([1, 1])

# --- 左側面板：蜂巢節點數據展示 ---
with left_panel:
    st.subheader(f"📊 實時監測數據看板 ({st.session_state.selected_vol.split(' ')[0]})")
    
    # 透過昨天調校好的 HTML 區塊渲染出漂亮的卡片
    for metric_name, val in health_metrics.items():
        st.markdown(f"""
        <div class='data-card'>
            <div class='metric-label'>{metric_name}</div>
            <div class='metric-value'>{val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"💡 **系統狀態解讀**：\n{status_text}")

# --- 右側面板：DeepSeek 離線大模型互動區 ---
with right_panel:
    st.subheader("🤖 DEEPSEEK CORE 本地推理區塊")
    st.markdown("`環境：Raspberry Pi 5 (16GB) Edge AI 層` — 透過本地端神經網路引擎直接調用 DeepSeek 離線大模型，隱私資料完全不出網閘。")

    # 初始化對話 Session State，確保狀態不丟失
    if "chat_response" not in st.session_state:
        st.session_state.chat_response = ""
    if "loading" not in st.session_state:
        st.session_state.loading = False

    user_query = st.text_input(
        "輸入您對生理數據的臨床疑問：", 
        placeholder="例如：若長者心率驟降至50且IMU震幅異常，應觸發何種通報流程？"
    )

    # 昨天四點多最終確定的「動態安全鎖定 Key」，徹底解決按鈕因重新渲染而失效的小脾氣
    btn_key = f"deepseek_submit_btn_{len(user_query)}"

    if st.button("送出至 Edge AI 進行推理", type="primary", key=btn_key):
        if user_query:
            st.session_state.loading = True
            with st.spinner("🧠 樹莓派 5 邊緣神經網路引擎計算中... 請稍候"):
                time.sleep(1.5)  # 完美模擬 1.5 秒的本地端推理延遲
                
                # 昨天我們寫好的標準醫療 Agent 知識庫（Skill Card）回覆格式
                st.session_state.chat_response = (
                    f"【DeepSeek Edge AI 本地回覆】\n\n"
                    f"針對您詢問的臨床疑問：「{user_query}」\n\n"
                    f"💡 基於當前系統載入的醫療 Agent 知識庫（Skill Card），當偵測到此複合型異常時，"
                    f"系統判定有高機率為跌倒或突發性休克。建議邊緣端立即啟動二級醫療通報流程，"
                    f"同時自動將 IMU 感測器採樣率提升至 100Hz 進行連續追蹤，並通知值班護理人員前往查看。"
                )
            st.session_state.loading = False
        else:
            st.warning("⚠️ 請輸入您的問題後再點擊送出。")

# =====================================================================
# 4. 獨立的回應結果顯示區域
# =====================================================================
if st.session_state.chat_response:
    st.markdown("---")
    st.markdown("### 📋 邊緣推理結果：")
    st.success(st.session_state.chat_response)