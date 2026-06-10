import streamlit as st
import time
import numpy as np
import hardware_config as hc
from datetime import datetime, timezone, timedelta

# =====================================================================
# 1. 網頁全域基本配置（嚴格相容 Windows 7 + Python 3.11）
# =====================================================================
st.set_page_config(
    page_title="Crystal Machine 蜂巢式 AI 生態系主控台",
    page_icon="🔮",
    layout="wide"
)

# =====================================================================
# 2. 自訂網頁 CSS 樣式（打造明亮白底舒適工業風、立體六角形蜂巢卡片）
# =====================================================================
st.markdown("""
<style>
    /* 強制右側主面板為舒適、清爽的明亮白底 */
    html, body, [data-testid='stAppViewContainer'], [data-testid='stHeader'] {
        background-color: #f8fafc !important;
        color: #1e293b !important;
    }
    
    /* 確保所有標準文字在白底下一樣清晰 */
    p, span, label, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
    }
    
    /* 左側側邊欄企業名稱加大明亮優化 */
    .brand-title {
        color: #0ea5e9 !important;
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-weight: 800 !important;
        font-size: 28px !important;
        margin-bottom: 0px;
        padding-bottom: 0px;
        letter-spacing: 0.5px;
    }
    
    /* 主面板大標題與時間佈局容器 */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        border-left: 6px solid #0ea5e9;
        padding-left: 12px;
        margin-bottom: 20px;
    }
    
    .hex-header-text {
        color: #0284c7 !important;
        font-weight: bold !important;
        font-family: 'Segoe UI', system-ui, sans-serif;
        margin: 0 !important;
        padding: 0 !important;
        font-size: 2.2rem !important;
    }
    
    /* 工業風即時時間標籤 */
    .live-clock {
        font-family: 'Courier New', Courier, monospace;
        background-color: #f1f5f9;
        color: #0369a1 !important;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
        border: 1px solid #e2e8f0;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* 六角蜂巢容器與完美比例正六角形卡片 */
    .honeycomb-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 15px 0;
    }
    
    .honeycomb-card {
        width: 150px;
        height: 150px;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #bae6fd;
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.08);
        transition: all 0.25s ease-in-out;
    }
    
    .honeycomb-card:hover {
        transform: translateY(-4px) scale(1.04);
        background: linear-gradient(135deg, #e0f2fe 0%, #ccfbf1 100%);
        border-color: #7dd3fc;
        box-shadow: 0 8px 20px rgba(14, 165, 233, 0.15);
    }
    
    .honeycomb-title {
        color: #0369a1 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        margin-bottom: 6px;
        border-bottom: 1px solid #bae6fd;
        padding-bottom: 4px;
        width: 80%;
    }
    
    .honeycomb-desc {
        color: #334155 !important;
        font-size: 11px !important;
        line-height: 1.3;
        font-weight: 500;
    }
    
    .status-empty {
        color: #94a3b8 !important;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 3. 側邊欄 UI 設計與 10 大產品線選單
# =====================================================================
st.sidebar.markdown("<p class='brand-title'>* Crystal Machine</p>", unsafe_allow_html=True)
st.sidebar.caption("工業級蜂巢式邊緣 AI 控制中樞模擬平台")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

selected_volume = st.sidebar.selectbox(
    "SYS CATALOGUE:",
    [
        "Vol. 1：基礎移動平台與移動機器人",
        "Vol. 2：環境感知與氣象監測",
        "Vol. 3：智慧農業與精準種植",
        "Vol. 4：智慧建築與空間管理",
        "Vol. 5：工業自動化與機器視覺",
        "Vol. 6：智慧醫療與臨床健康照護",
        "Vol. 7：綠能管理與氫能製氫模擬",
        "Vol. 8：電動載具與馬達動力診斷",
        "Vol. 9：無人機 (UAV) 與空中安防",
        "Vol. 10：智慧物流與冷鏈追蹤"
    ]
)

st.sidebar.markdown("---")
page_mode = st.sidebar.radio(
    "SYS MODE:", 
    ["📊 LIVE MONITOR", "🔌 12 PIN DOCK", "🧠 DEEPSEEK CORE"]
)

# =====================================================================
# 4. 獲取硬體底層配置與台北時區時間（相容 Python 3.11 標準庫）
# =====================================================================
try:
    hw_config = hc.get_catalog_config(selected_volume)
    pin_defines = hc.get_pogo_pin_definition()
except Exception:
    hw_config = {}

# 強制鎖定台灣台北時區 (UTC+8)，確保部署上雲端後右上角時間絕不偏移
tz_taiwan = timezone(timedelta(hours=8))
current_timestamp = datetime.now(tz_taiwan).strftime("SYS RUNTIME: %Y-%m-%d %H:%M:%S")

# =====================================================================
# 5. 六角形蜂巢元件渲染函式
# =====================================================================
def render_honeycomb_cell(slot_name, slot_value):
    if "未配置" in str(slot_value):
        display_text = f"<span class='status-empty'>{slot_value}</span>"
    else:
        display_text = str(slot_value).replace(" (", "<br><span style='color:#059669; font-weight:bold;'>").replace(")", "</span>")
    
    return f"""
    <div class='honeycomb-container'>
        <div class='honeycomb-card'>
            <div class='honeycomb-title'>{slot_name}</div>
            <div class='honeycomb-desc'>{display_text}</div>
        </div>
    </div>
    """

# =====================================================================
# 6. 頁面切換邏輯
# =====================================================================

# --- 頁面 1：實時設備看板 ---
if page_mode == "📊 LIVE MONITOR":
    st.markdown(f"""
    <div class='header-container'>
        <div class='hex-header-text'>{selected_volume}</div>
        <div class='live-clock'>{current_timestamp}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("外殼機構：六角形蜂巢式鋁合金外殼 (對角距離約 115mm / 厚度 32mm) | 核心運算：Raspberry Pi 5 + ESP32-S3")
    st.markdown("---")
    
    st.markdown("### 📡 邊緣端多感測器即時資料鏈 (預留串列通訊接口)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="目前移動時速 (km/h)", value="22")
    with col2:
        st.metric(label="馬達輪轂轉速 (RPM)", value="120")
    with col3:
        st.metric(label="LiDAR 障礙物探測距離 (m)", value="13")
        
    st.markdown("---")
    st.markdown("### 六角蜂巢外殼磁吸 Dock 狀態 (N52 強力磁鐵定位)")
    st.caption("當前領域模組之 A/B/C/D 生態幾何拓撲結構自動偵測：")
    
    h_col1, h_col2, h_col3, h_col4 = st.columns(4)
    with h_col1:
        st.markdown(render_honeycomb_cell("A1 模組", "已就緒 (24-bit ADC)"), unsafe_allow_html=True)
    with h_col2:
        st.markdown(render_honeycomb_cell("B2 模組", "已就緒 (IMU 網路)"), unsafe_allow_html=True)
    with h_col3:
        st.markdown(render_honeycomb_cell("C3 模組", "未配置"), unsafe_allow_html=True)
    with h_col4:
        st.markdown(render_honeycomb_cell("D4 模組", "已就緒 (溫控偵測)"), unsafe_allow_html=True)

# --- 頁面 2：12 PIN DOCK 介面 ---
elif page_mode == "🔌 12 PIN DOCK":
    st.markdown(f"""
    <div class='header-container'>
        <div class='hex-header-text'>POGO PIN 實體接口組態</div>
        <div class='live-clock'>{current_timestamp}</div>
    </div>
    """, unsafe_allow_html=True)
    st.info("硬體底層 12-Pin 彈簧針物理硬體映射配置檢視中...")

# --- 頁面 3：DEEPSEEK CORE 大模型推理 ---
elif page_mode == "🧠 DEEPSEEK CORE":
    st.markdown(f"""
    <div class='header-container'>
        <div class='hex-header-text'>🤖 DEEPSEEK CORE 本地推理核心</div>
        <div class='live-clock'>{current_timestamp}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("`硬體環境：Raspberry Pi 5 (16GB) 邊緣神經網路層` — 本地離線計算，數據完全留存地端保護隱私。")
    
    if "chat_response" not in st.session_state:
        st.session_state.chat_response = ""
        
    user_query = st.text_input("輸入您對當前工業/生理數據的臨床疑問：", placeholder="例如：若馬達轉速與溫升曲線異常，應調校何種 Skill Agent 策略？")
    
    # 動態安全鎖定 key，防止 Win7 前端組件暫存卡死
    btn_key = f"ds_submit_{len(user_query)}"
    
    if st.button("送出至 Edge AI 進行推理", type="primary", key=btn_key):
        if user_query:
            with st.spinner("🧠 樹莓派 5 邊緣神經網路引擎計算中... 請稍候"):
                time.sleep(1.5)
                st.session_state.chat_response = f"【DeepSeek Edge AI 本地回覆】\n針對您的提問：「{user_query}」\n系統已成功調配 TAD-AGE 框架下對應的 Skill Card。當前模擬環境運作正常，建議維持當前採樣率，並持續追蹤硬體底層 POGO PIN 的訊號反饋。"
        else:
            st.warning("⚠️ 請輸入您的疑問後再點擊送出。")
            
    if st.session_state.chat_response:
        st.markdown("---")
        st.markdown("### 📋 邊緣推理結果：")
        st.success(st.session_state.chat_response)