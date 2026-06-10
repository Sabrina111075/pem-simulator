import streamlit as st
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

# 注入客製化工業風 CSS 與 蜂巢圖專用樣式
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
    /* 蜂巢圖視覺優化 */
    .honeycomb-container {
        background-color: #0F2537;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #00A8CC;
        text-align: center;
        margin-bottom: 20px;
    }
    .honeycomb-title {
        color: #00A8CC;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 15px;
    }
    .node-active {
        background-color: #00A8CC;
        color: #0F2537;
        font-weight: bold;
        padding: 12px;
        border-radius: 6px;
        border: 2px solid #ffffff;
        text-align: center;
    }
    .node-center {
        background-color: #1F4E5B;
        color: #ffffff;
        font-weight: bold;
        padding: 15px;
        border-radius: 6px;
        border: 2px solid #00A8CC;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. 核心時間同步模組 (SYS RUNTIME AUTOMATION)
# ==============================================================================
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

vol_title = product_vol.split(" ")[1] + " " + product_vol.split(" ")[2]

# 頂部抬頭與時間同步卡片 (2:1 排版)
header_col, time_col = st.columns([2, 1])
with header_col:
    st.title("⬢ Edge AI 控制中樞模擬平台")
    st.subheader(f"當前系統動態加載：{product_vol}")
with time_col:
    st.write("") 
    st.markdown(f"""
    <div class="sys-time-card">
        ⏰ SYS RUNTIME : {formatted_time}<br>
        <span style="font-size: 0.8rem; color: #b3dbf2;">TIMEZONE: ASIA/TAIPEI (UTC+8)</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==============================================================================
# ✨ 核心加回：漂亮的六角型蜂巢拓撲形狀顯示 (HONEYCOMB HARDWARE TOPOLOGY)
# ==============================================================================
st.markdown('<div class="honeycomb-container">', unsafe_allow_html=True)
st.markdown(f'<div class="honeycomb-title">⬢ 蜂巢式拓撲硬體互連架構即時映射 (對角 115mm 工業鋁合金外殼)</div>', unsafe_allow_html=True)

# 建立 3 行網格來模擬六角形拓撲結構
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2, row2_col3 = st.columns([1, 1.2, 1])
row3_col1, row3_col2 = st.columns(2)

with row1_col1:
    st.markdown('<div class="node-active">⬢ C1 視覺雷達模組<br><span style="font-size:0.75rem;">(Camera / LiDAR)</span></div>', unsafe_allow_html=True)
with row1_col2:
    st.markdown('<div class="node-active">⬢ B1 遠程通訊模組<br><span style="font-size:0.75rem;">(LoRa / 5G)</span></div>', unsafe_allow_html=True)

with row2_col1:
    # 這裡會根據左側下拉選單，動態點亮目前的 A1 模組型態！
    st.markdown(f'<div class="node-active" style="border: 2px solid #FFD700;">⬢ A1 當前加載模組<br><span style="font-size:0.75rem; color:#0F2537; font-weight:bold;">({vol_title})</span></div>', unsafe_allow_html=True)
with row2_col2:
    st.markdown('<div class="node-center">🧠 樹莓派 5 核心<br><span style="font-size:0.8rem; color:#00A8CC;">(DeepSeek AI Core)</span></div>', unsafe_allow_html=True)
with row2_col3:
    st.markdown('<div class="node-active">⬢ B2 短距通訊模組<br><span style="font-size:0.75rem;">(Wi-Fi 6 / UWB)</span></div>', unsafe_allow_html=True)

with row3_col1:
    st.markdown('<div class="node-active">⬢ A2 姿態定位模組<br><span style="font-size:0.75rem;">(IMU / GPS)</span></div>', unsafe_allow_html=True)
with row3_col2:
    st.markdown('<div class="node-active">⬢ D1 智慧電源模組<br><span style="font-size:0.75rem;">(BMS Battery)</span></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# ==============================================================================
# 5. 三大單元分頁渲染 (SYS MODE ROUTER)
# ==============================================================================

# ------------------------------------------------------------------------------
# 單元 A: LIVE MONITOR (實時設備看板)
# ------------------------------------------------------------------------------
if sys_mode == "📊 LIVE MONITOR (實時設備看板)":
    st.markdown(f"### 📊 邊緣感測器資料鏈 — {vol_title}")
    st.info(f"💡 核心映射說明：目前主控台已切換至【{product_vol}】，此處實時渲染 Raspberry Pi 5 經 12 Pin 磁吸介面傳輸之高精度數據流。")
    
    col1, col2, col3 = st.columns(3)
    if "Vol. 6" in product_vol:
        with col1:
            st.metric(label="🫀 即時心率 (Heart Rate)", value=f"{random.randint(72, 78)} BPM", delta="正常範圍")
        with col2:
            st.metric(label="🩸 血氧飽和度 (SpO2)", value=f"{random.randint(97, 99)} %", delta="優良")
        with col3:
            st.metric(label="🌡️ 核心體溫 (Core Temperature)", value=f"{round(random.uniform(36.4, 36.8), 1)} °C", delta="無發熱")
    elif "Vol. 5" in product_vol:
        with col1:
            st.metric(label="💨 一氧化碳濃度 (CO)", value=f"{random.randint(12, 18)} ppm", delta="安全綠燈")
        with col2:
            st.metric(label="🧪 硫化氫氣體 (H2S)", value=f"{round(random.uniform(0.1, 0.4), 2)} ppm", delta="無超標")
        with col3:
            st.metric(label="🌡️ 環境溫度 (Temp)", value=f"{round(random.uniform(24.5, 25.2), 1)} °C", delta="常溫")
    else:
        with col1:
            st.metric(label="⚡ 模組通道 A 電壓", value=f"{round(random.uniform(3.2, 3.4), 2)} V", delta="穩壓輸出")
        with col2:
            st.metric(label="🔄 數據吞吐量 (Throughput)", value=f"{random.randint(920, 960)} kbps", delta="無丟包")
        with col3:
            st.metric(label="📉 底層信噪比 (SNR)", value=f"{random.randint(42, 46)} dB", delta="訊號極佳")
        
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
    
    st.success(f"⬢ 物理狀態：磁吸成功 (Magnetic Dock Engaged) — 控制中樞已為 【{product_vol}】 配發硬體線路與暫存器定址。")
    
    pin_data = {
        "Pin 編號": [f"Pin {i}" for i in range(1, 13)],
        "分配功能 (Function)": ["VCC (5V)", "GND", "UART_TX", "UART_RX", "I2C_SCL", "I2C_SDA", "SPI_CS", "SPI_CLK", "MISO", "MOSI", "ID_DETECT (模組識別)", "INT_LINE (中斷)"],
        "電氣狀態 (Status)": ["CONNECTED", "CONNECTED", "ACTIVE", "ACTIVE", "IDLE", "IDLE", "NONE", "NONE", "NONE", "NONE", f"HIGH ({product_vol.split(' ')[1]} Identified)", "LOW"]
    }
    df_pins = pd.DataFrame(pin_data)
    st.table(df_pins)

# ------------------------------------------------------------------------------
# 單元 C: DEEPSEEK CORE (地端 AI 專家) -> 徹底根除 ID 衝突報錯
# ------------------------------------------------------------------------------
elif sys_mode == "🧠 DEEPSEEK CORE (地端 AI 專家)":
    st.markdown("### 🧠 DeepSeek 離線大模型地端專家對話終端")
    st.warning("🔒 隱私計算安全標準：歷史紀錄高強度加密，推理完全於地端 Raspberry Pi 5 本地端全權執行，數據絕不上傳外網雲端。")
    
    st.markdown("#### 📑 已依據型錄自動加載專屬 Agent 技能卡")
    st.caption(f"✓ 已就緒：{vol_title} 核心控制 Prompt 專家卡片")
    
    # 關鍵修正：透過為 form 顯式加上唯一的 key，以及為 submit_button 加上獨一無二的 key 來絕殺 DuplicateWidgetID 錯誤
    with st.form(key="deepseek_chat_form"):
        user_input = st.text_input("💬 請輸入對健康醫療或邊緣端硬體狀態的諮詢：", placeholder="例如：心率突發 110 BPM 且血氧降至 94% 時的處置 SOP？", key="ds_user_input")
        submit_btn = st.form_submit_with_button(label="調用地端算力推理 (Run Edge Inference)", key="ds_submit_btn")
        
    if submit_btn and user_input:
        st.write("---")
        st.markdown("**🧠 DeepSeek 邊緣核心推理回覆：**")
        with st.spinner("樹莓派 5 本地端算力加載推理中..."):
            st.markdown(f"""
            依據加載之 **{vol_title} 專家知識庫** 規範，針對您輸入的「*{user_input}*」提供邊緣端整合診斷：
            1. **狀態判定：** 系統檢測到當前運作單元為 `{product_vol}`，已將 12 Pin Dock 之中斷腳位 (Pin 12) 優先權限拉至最高。
            2. **地端處置建議：** 邊緣端硬體模組狀態一切正常，針對輸入之指標異常，建議立即啟動二級安全供電防線，並在本地快取區留存快閃日誌。
            3. **本地日誌安全：** 本次諮詢與推理數據已完全加密留存於 Raspberry Pi 5 本地端 eMMC/SD 安全防線內，未外流至任何公有雲。
            """)