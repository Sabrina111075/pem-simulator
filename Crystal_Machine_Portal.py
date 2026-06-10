import streamlit as st
import time

# --- 網頁全域設定 ---
st.set_page_config(
    page_title="Crystal Machine - 蜂巢式 Edge AI 照護中樞主控台",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 注入 CSS 樣式（科技感深色主題與蜂巢視覺優化） ---
st.markdown("""
<style>
    .reportview-container { background: #0E1117; }
    .main-title {
        font-size: 40px; font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00FFCC, #0099FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 30px;
    }
    .node-box {
        background-color: #1A1F2C;
        border: 2px solid #00FFCC;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.2);
        transition: transform 0.3s;
    }
    .node-box:hover { transform: scale(1.05); }
    .core-box {
        background-color: #241435;
        border: 3px solid #FF007F;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(255, 0, 127, 0.4);
    }
    .data-card {
        background-color: #121620;
        border-left: 5px solid #0099FF;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_index=True)

# --- 側邊欄控制與 Mock Data 設定 ---
st.sidebar.title("🛸 蜂巢中樞控制台")
st.sidebar.markdown("---")

selected_vol = st.sidebar.selectbox(
    "選擇監測設備批次 (Device Volume)",
    ["Vol. 1 (心血管監測)", "Vol. 2 (呼吸道感知)", "Vol. 3 (高齡防跌落)", "Vol. 4 (睡眠呼吸暫停)", "Vol. 5 (工業氣體感知)"]
)

# 根據選擇的 Volume 載入對應數據
if "Vol. 1" in selected_vol:
    health_metrics = {"數據 A (心率)": "78 bpm", "數據 B (血氧)": "98 %", "數據 C (血壓)": "122/80 mmHg"}
    status_text = "當前長者生理訊號穩定，邊緣端模型評估為低風險。"
elif "Vol. 2" in selected_vol:
    health_metrics = {"數據 A (呼吸率)": "18 bpm", "數據 B (呼吸音異常度)": "2 %", "數據 C (肺活量模擬)": "3500 ml"}
    status_text = "呼吸音感知正常，無明顯喘鳴音或咳嗽頻率異常。"
elif "Vol. 3" in selected_vol:
    health_metrics = {"數據 A (IMU 震幅)": "0.12 g", "數據 B (步態不穩度)": "5 %", "數據 C (空間高度層)": "地表 0 cm"}
    status_text = "步態軌跡符合正常範圍，雷達與加速度計未偵測到突發性高度掉落。"
elif "Vol. 4" in selected_vol:
    health_metrics = {"數據 A (翻身次數)": "4 次/時", "數據 B (打鼾分貝)": "42 dB", "數據 C (深眠比例)": "45 %"}
    status_text = "睡眠品質良好，未觸發 OSA (睡眠呼吸中止) 邊緣防禦警告。"
else:
    health_metrics = {"數據 A (一氧化碳)": "2 ppm", "數據 B (硫化氫)": "0 ppm", "數據 C (環境溫度)": "26.4 ℃"}
    status_text = "照護環境空氣品質良好，未偵測到任何工業級危險氣體洩漏。"

st.sidebar.markdown("---")
st.sidebar.info("🤖 **系統架構提示**：\n本系統採用 Raspberry Pi 5 作為中央大模型推理核心，四周透過 12-Pin Pogo Pin 磁吸介面熱插拔串接 ESP32-S3 感測子模組。未來接上序列通訊 (Serial) 即可將虛擬數據無縫切換為實體硬體流。")

# --- 主畫面標題 ---
st.markdown("<div class='main-title'>Crystal Machine 蜂巢式 AI Sensor Hub 主控台</div>", unsafe_allow_index=True)

# --- 核心視覺效果：重新改回原來的「蜂巢式六角硬體拓撲圖」 ---
st.subheader("🌐 蜂巢式硬體拓撲拓撲架構 (Hardware Topology)")
st.markdown("下方呈現 Crystal Machine 專利五之**中央運算核心與六向模組 Dock** 部署狀態，各模組均支援熱插拔自動識別：")

# 第一排模組 (左上、右上)
row1_col1, row1_col2, row1_col3, row1_col4 = st.columns([1, 2, 2, 1])
with row1_col2:
    st.markdown("""<div class='node-box'>🟢 <b>C1: Camera / LiDAR</b><br><span style='color:#00FFCC;font-size:12px;'>視覺空間防跌模組 (Active)</span></div>""", unsafe_allow_index=True)
with row1_col3:
    st.markdown("""<div class='node-box'>🟢 <b>B1: LoRa / 5G</b><br><span style='color:#00FFCC;font-size:12px;'>遠距微弱訊號傳輸 (Ready)</span></div>""", unsafe_allow_index=True)

st.markdown("<br>", unsafe_allow_index=True)

# 第二排模組 (正左、正中央核心、正右)
row2_col1, row2_col2, row2_col3 = st.columns([2, 3, 2])
with row2_col1:
    st.markdown("""<div class='node-box' style='margin-top: 20px;'>🟢 <b>A1: 環境感測器</b><br><span style='color:#00FFCC;font-size:12px;'>氣體/溫濕度多合一</span></div>""", unsafe_allow_index=True)
with row2_col2:
    st.markdown("""<div class='core-box'>🧠 <b>CENTRAL AI CORE</b><br><span style='color:#FF007F; font-weight:bold; font-size:16px;'>Raspberry Pi 5 (8GB)</span><br><span style='color:#ccc;font-size:12px;'>DeepSeek 7B 離線推演中樞</span></div>""", unsafe_allow_index=True)
with row2_col3:
    st.markdown("""<div class='node-box' style='margin-top: 20px;'>🟢 <b>B2: Wi-Fi / UWB</b><br><span style='color:#00FFCC;font-size:12px;'>高精準雷達微動人體感知</span></div>""", unsafe_allow_index=True)

st.markdown("<br>", unsafe_allow_index=True)

# 第三排模組 (左下、右下)
row3_col1, row3_col2, row3_col3, row3_col4 = st.columns([1, 2, 2, 1])
with row3_col2:
    st.markdown("""<div class='node-box'>🟢 <b>A2: IMU / GPS</b><br><span style='color:#00FFCC;font-size:12px;'>九軸姿態步態分析儀</span></div>""", unsafe_allow_index=True)
with row3_col3:
    st.markdown("""<div class='node-box'>🟢 <b>D1: Battery / Power</b><br><span style='color:#00FFCC;font-size:12px;'>UPS 模組安全不斷電系統</span></div>""", unsafe_allow_index=True)

st.markdown("---")

# --- 數據展示與大模型對話區塊 ---
left_panel, right_panel = st.columns([1, 1])

with left_panel:
    st.subheader(f"📊 實時監測數據看板 ({selected_vol.split(' ')[0]})")
    for metric_name, val in health_metrics.items():
        st.markdown(f"""
        <div class='data-card'>
            <span style='color:#888; font-size:14px;'>{metric_name}</span><br>
            <span style='font-size:24px; font-weight:bold; color:#0099FF;'>{val}</span>
        </div>
        """, unsafe_allow_index=True)
    
    st.info(f"💡 **狀態解讀**：{status_text}")

with right_panel:
    st.subheader("🧠 DEEPSEEK CORE 本地推理區區塊")
    st.markdown("透過樹莓派 5 邊緣運算層直接調用 DeepSeek 離線大模型，完全保護病患隱私。請輸入護理人員的提問：")
    
    # 確保 session state 初始化，防止報錯
    if "chat_response" not in st.session_state:
        st.session_state.chat_response = ""
    if "loading" not in st.session_state:
        st.session_state.loading = False

    user_query = st.text_input("輸入您對生理數據的臨床疑問：", placeholder="例如：若長者心率驟降至50且IMU震幅異常，應觸發何種通報流程？")
    
    if st.button("送出至 Edge AI 進行推理", type="primary"):
        if user_query:
            st.session_state.loading = True
            with st.spinner("樹莓派 5 邊緣神經網路引擎計算中..."):
                time.sleep(1.5)  # 模擬本地硬體推理延遲
                st.session_state.chat_response = f"【DeepSeek Edge AI 本地回覆】\n針對您詢問的問題：「{user_query}」\n基於當前系統載入的 Skill Card (醫療 Agent 知識庫)，當偵測到此複合型異常時，中央核心會立即下達指令給 B1 通訊模組，跳過雲端直接透過 LoRa 發射緊急廣播求救訊號，並同步啟動 C1 相機進行即時姿態辨識，判斷是否倒地。此決策完全於本地端 30ms 內完成。"
            st.session_state.loading = False
        else:
            st.warning("請先輸入您的問題後再點擊送出。")

    # 顯示回應區塊
    if st.session_state.chat_response:
        st.markdown("### 🤖 邊緣推理結果：")
        st.success(st.session_state.chat_response)