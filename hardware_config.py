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
# 2. 自訂網頁 CSS 樣式（工業風明亮白底、立體蜂巢卡片與專業面板容器）
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
    
    /* 12 PIN POGO DOCK 專用立體表格樣式 */
    .dock-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        background-color: #ffffff;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-radius: 6px;
        overflow: hidden;
    }
    .dock-table th {
        background-color: #0ea5e9;
        color: white !important;
        padding: 12px;
        font-weight: bold;
        text-align: left;
    }
    .dock-table td {
        padding: 12px;
        border-bottom: 1px solid #e2e8f0;
        color: #334155 !important;
        font-size: 14px;
    }
    .dock-table tr:hover {
        background-color: #f0f9ff;
    }
    .pin-badge {
        background-color: #e0f2fe;
        color: #0369a1 !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-family: monospace;
    }
    
    /* 六角蜂巢容器與完美比例正六角形卡片 */
    .honeycomb-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px 0;
    }
    
    .honeycomb-card {
        width: 145px;
        height: 145px;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #bae6fd;
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 12px;
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
        font-size: 13px !important;
        margin-bottom: 4px;
        border-bottom: 1px solid #bae6fd;
        padding-bottom: 2px;
        width: 80%;
    }
    
    .honeycomb-desc {
        color: #334155 !important;
        font-size: 11px !important;
        line-height: 1.2;
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
# 4. 核心數據鏈配置與台北時區時間 (完全整合 hardware_config)
# =====================================================================
try:
    hw_config = hc.get_catalog_config(selected_volume)
    pin_defines = hc.get_pogo_pin_definition()
except Exception:
    # 彈性預設安全防護，避免 hardware_config 讀取異常掛點
    hw_config = {"health_metrics": {"設備通訊狀態": "Online"}, "status_text": "底層組態讀取異常"}
    pin_defines = {f"PIN {i}": "GPIO / 未載入" for i in range(1, 13)}

# 強制鎖定台灣台北時區 (UTC+8)，確保數據時間戳絕對精準
tz_taiwan = timezone(timedelta(hours=8))
current_timestamp = datetime.now(tz_taiwan).strftime("SYS RUNTIME: %Y-%m-%d %H:%M:%S")

# 六角形蜂巢元件渲染函式
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
# 5. 獨立分頁路由切換邏輯 (徹底解決頁面空白與未載入問題)
# =====================================================================

# --- 【模式一：實時設備看板】 ---
if page_mode == "📊 LIVE MONITOR":
    st.markdown(f"""
    <div class='header-container'>
        <div class='hex-header-text'>{selected_volume}</div>
        <div class='live-clock'>{current_timestamp}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("外殼機構：六角形蜂巢式鋁合金外殼 (對角距離約 115mm / 厚度 32mm) | 核心運算：Raspberry Pi 5 + ESP32-S3")
    st.markdown("---")
    
    # 動態取得當前型錄感測器數據
    health_metrics = hw_config.get("health_metrics", {})
    status_text = hw_config.get("status_text", "系統就緒")
    
    st.markdown("### 📡 邊緣端多感測器即時資料鏈 (預留串列通訊接口)")
    if health_metrics:
        m_cols = st.columns(len(health_metrics))
        for idx, (m_label, m_val) in enumerate(health_metrics.items()):
            with m_cols[idx]:
                st.metric(label=m_label, value=m_val)
    else:
        st.warning("⚠️ 當前型錄未配置實時資料鏈指標。")
        
    st.info(f"🔮 **狀態解讀** : {status_text}")
    st.markdown("---")
    
    # 渲染六角蜂巢外殼磁吸 Dock 拓撲狀態
    st.markdown("### 六角蜂巢外殼磁吸 Dock 狀態 (N52 強力磁鐵定位)")
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns(6)
    with h_col1: st.markdown(render_honeycomb_cell("A1 模組", "已就緒 (24-bit ADC)"), unsafe_allow_html=True)
    with h_col2: st.markdown(render_honeycomb_cell("B2 模組", "已就緒 (IMU 網路)"), unsafe_allow_html=True)
    with h_col3: st.markdown(render_honeycomb_cell("C3 模組", "未配置"), unsafe_allow_html=True)
    with h_col4: st.markdown(render_honeycomb_cell("D4 模組", "已就緒 (溫控偵測)"), unsafe_allow_html=True)
    with h_col5: st.markdown(render_honeycomb_cell("E5 模組", "已就緒 (CAN 匯流排)"), unsafe_allow_html=True)
    with h_col6: st.markdown(render_honeycomb_cell("F6 模組", "未配置"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📈 邊緣端高頻採樣訊號實時波形監測 (24-bit ADC / 100Hz)")
    t = np.linspace(0, 4 * np.pi, 100)
    wave_data = np.sin(t) * 1.5 + np.random.normal(0, 0.08, 100)
    wave_data_2 = np.cos(t) * 1.0 + np.random.normal(0, 0.04, 100)
    st.line_chart(np.vstack((wave_data, wave_data_2)).T)


# --- 【模式二：12 PIN DOCK 介面 (🔥 完美載入實體接口數據)】 ---
elif page_mode == "🔌 12 PIN DOCK":
    st.markdown(f"""
    <div class='header-container'>
        <div class='hex-header-text'>POGO PIN 實體接口組態</div>
        <div class='live-clock'>{current_timestamp}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔌 底層 12-Pin 彈簧針物理硬體映射配置表")
    st.caption(f"目前正為首頁選定的【{selected_volume}】載入對應之底層暫存器與硬體腳位組態：")
    
    # 建立動態 HTML 表格，將讀取自 hardware_config 的 pin_defines 渲染出來
    table_rows = ""
    for pin_num, definition in pin_defines.items():
        table_rows += f"""
        <tr>
            <td><span class='pin-badge'>{pin_num}</span></td>
            <td><b>{definition}</b></td>
            <td>物理彈簧針連接 (Pogo Pin)</td>
            <td><span style='color:#059669;'>● Active</span></td>
        </tr>
        """
        
    html_table = f"""
    <table class='dock-table'>
        <thead>
            <tr>
                <th>硬體腳位 (Pin Number)</th>
                <th>當前功能映射 (Function Mapping)</th>
                <th>物理介面類型 (Interface Type)</th>
                <th>訊號狀態 (Signal Status)</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)


# --- 【模式三：DEEPSEEK CORE 大模型推理 (🔥 完美獨立區塊)】 ---
elif page_mode == "🧠 DEEPSEEK CORE":
    st.markdown(f"""
    <div class='header-container'>
        <div class='hex-header-text'>🧠 DEEPSEEK CORE 本地推理核心</div>
        <div class='live-clock'>{current_timestamp}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"#### 🤖 邊緣神經網路計算層 (樹莓派 5 16GB RAM)")
    st.markdown(f"透過樹莓派 5 邊緣運算層直接調用 DeepSeek 離線大模型，完全保護工業現場與臨床病患隱私。當前系統已成功加載 **{selected_volume}** 的對應邊緣端自動化控制診斷知識庫。")
    st.markdown("---")
    
    # 初始化 session state
    if "chat_response" not in st.session_state:
        st.session_state.chat_response = ""
        
    user_query = st.text_input(
        "輸入您對當前工業/生態數據的臨床疑問：", 
        placeholder="例如：若此領域數據曲線異常，應調校何種 Skill Agent 策略？"
    )
    
    if st.button("送出至 Edge AI 進行推理", type="primary"):
        if user_query:
            with st.spinner("🧠 樹莓派 5 邊緣神經網路引擎計算中... 請稍候"):
                time.sleep(1.2)  # 模擬本地推理延遲
                st.session_state.chat_response = f"【DeepSeek Edge AI 本地回覆】\n針對您在「{selected_volume}」中所提問的問題：「{user_query}」\n系統已自動匹配並調配 TAD-AGE 框架下對應的 Skill Card 知識庫進行比對。當前邊緣採樣鏈回傳正常，建議維持高頻監測，並持續觀測硬體底層 12 PIN DOCK 的訊號反饋。"
        else:
            st.warning("⚠️ 請輸入您的疑問後再點擊送出。")
            
    if st.session_state.chat_response:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📋 邊緣推理結果：")
        st.success(st.session_state.chat_response)