import streamlit as st  # 修正：確認將 streamlit 正確導入為 st
import datetime
import pandas as pd
import random

# ==============================================================================
# 1. 系統全域配置 (PAGE & STYLE CONFIG)
# ==============================================================================
st.set_page_config(
    page_title="Crystal Machine 企業語意作業系統",
    page_icon="⬢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入客製化工業風 CSS 樣式
st.markdown("""
<style>
    .main-header {
        font-family: 'Courier New', monospace;
        color: #1F4E5B;
        font-weight: bold;
    }
    .stMetric {
        background-color: #F4F7F6;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #00A8CC;
    }
    .sys-time-card {
        background-color: #1F4E5B;
        color: #ffffff;
        padding: 8px 12px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. 核心時間同步模組 (SYS RUNTIME AUTOMATION)
# ==============================================================================
# 抓取雲端 Linux 伺服器時間並透過 timedelta 強制校正為台灣標準時間 (UTC+8)
current_tw_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
formatted_time = current_tw_time.strftime("%Y-%m-%d %H:%M:%S")

# ==============================================================================
# 3. 左側導覽控制面板 (SIDEBAR CONFIGURATION)
# ==============================================================================
st.sidebar.markdown("# ⬢ Crystal Machine")
st.sidebar.markdown("### 企業語意作業系統 `V2.0` (Raspberry Pi 5 核心)")
st.sidebar.divider()

# 專利型錄分卷切換 (Vol.1 - Vol.10)
product_vol = st.sidebar.selectbox(
    "📂 選擇型錄分卷 (PRODUCT VOLUME)",
    [
        "Vol. 1 行動機器人模組 (Mobile Robotics)",
        "Vol. 2 農業自動化感測器 (Agri-Tech Sensors)",
        "Vol. 3 車聯網 V2X 終端 (Automotive Telematics)",
        "Vol. 4 智慧物流冷鏈追蹤 (Smart Cold-Chain)",
        "Vol. 5 工業環境有毒氣體監測 (Industrial Gas Detection)",
        "Vol. 6 智慧健康醫療門戶 (Active Healthcare Central)",
        "Vol. 7 環境微氣候雷達 (Microclimate Radar)",
        "Vol. 8 軌道交通結構安全 (Railway Safety)",
        "Vol. 9 倉儲自動化防撞視覺 (Warehouse Anti-collision)",
        "Vol. 10 綠能儲能電池管理 (BMS Storage)"
    ],
    index=5 # 預設載入開會要展示的 Vol. 6 智慧健康醫療門戶
)

st.sidebar.divider()

# 三大專利技術展示切換
sys_mode = st.sidebar.radio(
    "🛠️ 選擇主控面板單元 (SYS MODE)",
    [
        "📊 LIVE MONITOR (實時設備看板)",
        "🔌 12 PIN DOCK (磁吸接口後台)",
        "🧠 DEEPSEEK CORE (地端 AI 專家)"
    ]
)

st.sidebar.divider()
st.sidebar.caption("硬體核心：Raspberry Pi 5 (16GB)")
st.sidebar.caption("通訊架構：ESP32-S3 + 24-bit ADC (AT6901)")
st.sidebar.caption("部署分支：`cloud-deploy` (獨立隔離區)")

# ==============================================================================
# 4. 右側主面板看板 (MAIN PANEL RENDERER)
# ==============================================================================

# 頂部抬頭與時間同步卡片 (2:1 排版)
header_col, time_col = st.columns([2, 1])
with header_col:
    st.title("⬢ Edge AI 控制中樞模擬平台")
    st.subheader(f"當前加載：{product_vol.split(' ')[0]} {product_vol.split(' ')[1]}")
with time_col:
    st.write("") # 調整排版間距
    st.markdown(f"""
    <div class="sys-time-card">
        ⏰ SYS RUNTIME : {formatted_time}<br>
        <span style="font-size: 0.8rem; color: #b3dbf2;">TIMEZONE: ASIA/TAIPEI (UTC+8)</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ------------------------------------------------------------------------------
# 單元 A: LIVE MONITOR (實時設備看板)
# ------------------------------------------------------------------------------
if sys_mode == "📊 LIVE MONITOR (實時設備看板)":
    st.markdown("### 📊 邊緣多感測器資料鏈 (Data Pipeline)")
    st.info("💡 核心映射說明：此處實時加載 Raspberry Pi 5 經實體 USB Hub 串接之 ESP32-S3 與 24-bit ADC (AT6901) 高精度資料流。")
    
    # 生產虛擬即時健康數據
    col_bpm, col_spo2, col_temp = st.columns(3)
    with col_bpm:
        st.metric(label="🫀 即時心率 (Heart Rate)", value=f"{random.randint(72, 78)} BPM", delta="正常範圍")
    with col_spo2:
        st.metric(label="🩸 血氧飽和度 (SpO2)", value=f"{random.randint(97, 99)} %", delta="優良")
    with col_temp:
        st.metric(label="🌡️ 核心體溫 (Core Temperature)", value=f"{round(random.uniform(36.4, 36.8), 1)} °C", delta="無發熱")
        
    st.write("")
    st.markdown("#### 🔄 24-bit 高精度信號即時特徵波形圖")
    chart_data = pd.DataFrame(
        [random.uniform(0.5, 1.5) for _ in range(50)],
        columns=['ADC Raw Signal (V)']
    )
    st.line_chart(chart_data)

# ------------------------------------------------------------------------------
# 單元 B: 12 PIN DOCK (磁吸接口後台)
# ------------------------------------------------------------------------------
elif sys_mode == "🔌 12 PIN DOCK (磁吸接口後台)":
    st.markdown("### 🔌 12 Pin Pogo Pin 彈簧式互連介面狀態")
    st.info("💡 專利結構對齊：模擬六角形鋁合金機殼（對角 115mm / 厚度 32mm）內部 N52 強力磁鐵盲插定位與 A/B/C/D 模組拓撲識別。")
    
    st.success("⬢ 物理狀態：模組已吸附成功 (Magnetic Dock Engaged) — 偵測到 D1 電源管理模組及 A1 環境醫療感測器。")
    
    # 渲染 12 Pin 腳位狀態分配表
    pin_data = {
        "Pin 編號": [f"Pin {i}" for i in range(1, 13)],
        "分配功能 (Function)": ["VCC (5V)", "GND", "UART_TX", "UART_RX", "I2C_SCL", "I2C_SDA", "SPI_CS", "SPI_CLK", "MISO", "MOSI", "ID_DETECT (模組識別)", "INT_LINE (中斷)"],
        "電氣狀態 (Status)": ["CONNECTED", "CONNECTED", "ACTIVE", "ACTIVE", "IDLE", "IDLE", "NONE", "NONE", "NONE", "NONE", "HIGH (A1 Module Identified)", "LOW"]
    }
    df_pins = pd.DataFrame(pin_data)
    st.table(df_pins)

# ------------------------------------------------------------------------------
# 單元 C: DEEPSEEK CORE (地端 AI 專家)
# ------------------------------------------------------------------------------
elif sys_mode == "🧠 DEEPSEEK CORE (地端 AI 專家)":
    st.markdown("### 🧠 DeepSeek 離線大模型地端專家對話終端")
    st.warning("🔒 隱私計算安全標準：歷史紀錄高強度加密，推理完全於地端 Raspberry Pi 5 本地端全權執行，數據絕不上傳外網雲端。")
    
    st.markdown("#### 📑 已加載專屬 Agent 技能卡 (Skill Card)")
    st.caption("✓ 臨床運動控制與健康照護提示詞   ✓ 生理指標異常自動診斷提示詞")
    
    with st.form("ai_expert_form"):
        user_input = st.text_input("💬 請輸入對健康醫療或邊緣端硬體狀態的諮詢：", placeholder="例如：心率突發 110 BPM 且血氧降至 94% 時的處置 SOP？")
        submit_btn = st.form_submit_with_button("調用地端算力推理 (Run Edge Inference)")
        
    if submit_btn and user_input:
        st.write("---")
        st.markdown("**🧠 DeepSeek 邊緣核心推理回覆：**")
        with st.spinner("樹莓派 5 本地端算力加載推理中..."):
            st.markdown(f"""
            依據加載之 **Vol.6 臨床照護技能卡** 規範，針對您輸入的「*{user_input}*」提供診斷策略：
            1. **警報觸發：** 系統已自動將 12 Pin Dock 之中斷腳位 (Pin 12) 拉高，優先權限設定為緊急。
            2. **地端診斷：** 當心率突發性上升且血氧飽和度低於 95% 時，可能伴隨急性缺氧風險。邊緣端建議立即通知現場醫護人員，並同步啟動氧氣模組供電。
            3. **本地日誌：** 本次異常數據已加密留存於 Raspberry Pi 5 的本地 eMMC/SD 安全防線內。
            """)