import streamlit as st
import time
import numpy as np
import hardware_config as hc
from datetime import datetime

# 1. 網頁全域基本配置
st.set_page_config(
    page_title="Crystal Machine 蜂巢式 AI 生態系主控台",
    page_icon="*",
    layout="wide"
)

# 2. 自訂網頁 CSS 樣式
st.markdown("""
    <style>
    /* 強制右側主面板為舒適、清爽的明亮白底 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
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
    
    .step-box { 
        border: 1px dashed #cbd5e1; 
        padding: 14px; 
        border-radius: 8px; 
        background-color: #ffffff; 
        text-align: center; 
        font-size: 13px;
        color: #334155 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.01);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄 UI 設計
st.sidebar.markdown("<p class='brand-title'>* Crystal Machine</p>", unsafe_allow_html=True)
st.sidebar.caption("工業級蜂巢式邊緣 AI 控制中樞模擬平台")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# 下拉選單：完整導入10大產品線
selected_volume = st.sidebar.selectbox(
    "SYS CATALOGUE:",
    [
        "Vol. 1 : 基礎移動平台與移動機器人",
        "Vol. 2 : 環境感知與氣象監測",
        "Vol. 3 : 智慧農業與精準種植",
        "Vol. 4 : 智慧建築與空間管理",
        "Vol. 5 : 工業自動化與機器視覺",
        "Vol. 6 : 智慧醫療與臨床健康照護",
        "Vol. 7 : 綠能管理與氫能製氫模擬",
        "Vol. 8 : 電動載具與馬達動力診斷",
        "Vol. 9 : 無人機 (UAV) 與空中安防",
        "Vol. 10 : 智慧物流與冷鏈追蹤"
    ]
)

st.sidebar.markdown("---")
page_mode = st.sidebar.radio("SYS MODE:", ["📊 LIVE MONITOR", "🔌 12 PIN DOCK", "🤖 DEEPSEEK CORE"])

# 獲取硬體底層配置
hw_config = hc.get_catalog_config(selected_volume)
pin_defines = hc.get_pogo_pin_definition()

# 取得當前系統即時時間 (純ASCII安全格式)
current_timestamp = datetime.now().strftime("SYS RUNTIME: %Y-%m-%d %H:%M:%S")

def render_honeycomb_cell(slot_name, slot_value):
    if "未配置" in slot_value:
        display_text = f"<span class='status-empty'>{slot_value}</span>"
    else:
        display_text = slot_value.replace(" (", "<br><span style='color:#059669; font-weight:bold;'>").replace(")", "</span>")
    
    return f"""
        <div class='honeycomb-container'>
            <div class='honeycomb-card'>
                <div class='honeycomb-title'>{slot_name}</div>
                <div class='honeycomb-desc'>{display_text}</div>
            </div>
        </div>
    """

# 功能頁面 1：實時設備看板
if page_mode == "📊 LIVE MONITOR":
    st.markdown(f"""
        <div class='header-container'>
            <div class='hex-header-text'>{selected_volume}</div>
            <div class='live-clock'>{current_timestamp}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.caption("外殼機構：六角形蜂巢式鋁合金外殼 (對角距離約 115mm / 厚度 32mm) | 核心運算：Raspberry Pi 5 + ESP32-S3")
    st.markdown("---")
    
    st.subheader("📡 邊緣端多感測器即時資料鏈 (預留串列通訊接口)")
    col1, col2, col3 = st.columns(3)
    m_keys = list(hw_config["metrics"].keys())
    
    with col1:
        val, unit = hw_config["metrics"][m_keys[0]]
        st.metric(label=unit, value=val)
    with col2:
        val, unit = hw_config["metrics"][m_keys[1]]
        st.metric(label=unit, value=val)
    with col3:
        val, unit = hw_config["metrics"][m_keys[2]]
        st.metric(label=unit, value=val)
        
    st.markdown("---")
    
    st.subheader("六角蜂巢外殼磁吸 Dock 狀態 (N52 強力磁鐵定位)")
    st.caption("當前領域模組之 A/B/C/D 生態系幾何拓撲結構自動偵測：")
    
    col_a1, col_a2, col_b1, col_b2, col_c1, col_d1 = st.columns(6)
    
    with col_a1:
        st.markdown(render_honeycomb_cell("A1 感測插槽", hw_config['slots']['A1']), unsafe_allow_html=True)
    with col_a2:
        st.markdown(render_honeycomb_cell("A2 感測插槽", hw_config['slots']['A2']), unsafe_allow_html=True)
    with col_b1:
        st.markdown(render_honeycomb_cell("B1 通訊插槽", hw_config['slots']['B1']), unsafe_allow_html=True)
    with col_b2:
        st.markdown(render_honeycomb_cell("B2 通訊插槽", hw_config['slots']['B2']), unsafe_allow_html=True)
    with col_c1:
        st.markdown(render_honeycomb_cell("C1 視覺雷達", hw_config['slots']['C1']), unsafe_allow_html=True)
    with col_d1:
        st.markdown(render_honeycomb_cell("D1 電源管理", hw_config['slots']['D1']), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("邊緣訊號即時波形特徵模擬")
    chart_data = np.random.randn(25, 1) + hw_config["metrics"][m_keys[0]][0]
    st.line_chart(chart_data)

# 功能頁面 2：12 Pin 磁吸 Dock 電氣監測
elif page_mode == "🔌 12 PIN DOCK":
    st.markdown(f"""
        <div class='header-container'>
            <div class='hex-header-text'>12 Pin Pogo Pin 彈簧互連介面電氣監測</div>
            <div class='live-clock'>{current_timestamp}</div>
        </div>
    """, unsafe_allow_html=True)
    st.caption("符合專利 Figure 5 定義之接腳電氣狀態，主板與擴充模組之通訊與供電訊號實時監控")
    st.markdown("---")
    
    st.subheader("專利自動辨識方法：熱插拔狀態鏈狀態 (Figure 7 流程還原)")
    col_st1, col_st2, col_st3, col_st4 = st.columns(4)
    with col_st1:
        st.markdown("<div class='step-box'><b>① 機器機械對齊</b><br>六角斜面與定位扣導向</div>", unsafe_allow_html=True)
    with col_st2:
        st.markdown("<div class='step-box'><b>② 磁鐵自動吸附</b><br>N52 強力磁鐵導正盲插</div>", unsafe_allow_html=True)
    with col_st3:
        st.markdown("<div class='step-box'><b>③ Pogo Pin 電氣接觸</b><br>12接腳彈簧下壓導通</div>", unsafe_allow_html=True)
    with col_st4:
        st.markdown("<div class='step-box' style='border:2px solid #0284c7; background-color:#f0f9ff;'><b>④ 辨識啟動驅動</b><br><span style='color:#0369a1;'>🆔 讀取 EEPROM 啟動服務</span></div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader("彈簧式 Pogo Pin 實時通道狀態")
    st.table(pin_defines)

# 功能頁面 3：DeepSeek 地端 AI 專家 (採用通用相容元件)
elif page_mode == "🤖 DEEPSEEK CORE":
    st.markdown(f"""
        <div class='header-container'>
            <div class='hex-header-text'>DeepSeek 離線地端大模型專家諮詢</div>
            <div class='live-clock'>{current_timestamp}</div>
        </div>
    """, unsafe_allow_html=True)
    st.subheader(f"💡 狀態：{hw_config['skills']}")
    st.caption("技術特色：能力（Skill Card）與設備（Sensor Card）相互分離，於 Orange Pi 本地端執行邊緣推理，資料完全不出在地端")
    st.markdown("---")
    
    chat_key = f"msg_history_{selected_volume}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = (
            "【AI 專家】: 您好！我是部署在 Crystal Machine 中的地端 DeepSeek 專家。目前系統已成功與對應的感測數據鏈路對接。請問有什麼我可以協助您的？"
        )

    # 用舊版支援的大文字框來格式化輸出完整的對話歷史
    st.text_area(
        label="🤖 通訊終端歷史紀錄 (邊緣端加密通道)",
        value=st.session_state[chat_key],
        height=300,
        disabled=True
    )
    
    # 使用相容性極高的 st.form 處理輸入，避免回車即時重新整理的衝突
    with st.form(key="chat_input_form", clear_on_submit=True):
        user_input = st.text_input("請輸入您的工業診斷提問或設備連線疑問：", key="user_text_field")
        submit_button = st.form_submit_button(label="🚀 送出提問")
        
    if submit_button and user_input:
        # 更新歷史紀錄文字
        updated_history = st.session_state[chat_key] + f"\n\n【您】: {user_input}"
        
        # 模擬推理進度條
        with st.spinner("DeepSeek 地端核心模型推理中..."):
            time.sleep(0.8)
            response = (
                f"【地端推理核心回傳】\n"
                f"在 {selected_volume.split('：')[0]} 的架構下，系統已成功調用地端模型與專屬 Agent 技能卡。結合當前蜂巢 Dock 讀取到的感測特徵值，我們無需外部網絡即可直接在邊緣端完成高精度推論，兼顧低延遲與數據隱私安全性。"
            )
            updated_history += f"\n\n🤖 {response}"
            
        # 儲存回 session_state 並重新整理網頁畫面
        st.session_state[chat_key] = updated_history
        st.experimental_rerun()