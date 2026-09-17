import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import librosa
import librosa.display
import pandas as pd
import io
import wave
from datetime import datetime
import timezonefinder
import pytz

# 重設 Matplotlib 全局設定，徹底清除中文字體殘留
plt.rcdefaults()

st.set_page_config(page_title="馬達與工業設備聲學診斷測試平台", layout="wide")

st.title("⚙️ 馬達與工業設備聲學診斷測試平台 (DCASE Pro)")
st.caption("邊緣運算前置驗證平台 | 支援 ESP32-S3 + Raspberry Pi 5 模擬測試")

# ---------------------------------------------------------
# 初始化歷史數據紀錄 (Session State)
# ---------------------------------------------------------
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['timestamp', 'health_index', 'mse_loss'])

# ---------------------------------------------------------
# 兩層式兩段落側邊欄控制項 (DCASE 架構)
# ---------------------------------------------------------
st.sidebar.header("🎛️ 設備與測試控制台")

# 第一層：選擇設備類別
equipment_type = st.sidebar.selectbox(
    "1. 選擇設備類別 (Category)",
    ["🌊 工業幫浦 (Pump)", "🌀 工業風扇 (Fan) [階段二]", "🔬 測試模擬與自訂上傳"]
)

# 第二層：根據設備動態切換狀態選單
if "工業幫浦" in equipment_type:
    sound_condition = st.sidebar.selectbox(
        "2. 選擇幫浦運轉狀態 (Pump Condition)",
        [
            "🟢 幫浦 - 正常運轉 (Normal)",
            "🔴 幫浦 - 洩漏/空蝕異常 (Leaking / Cavitation)",
            "🟡 幫浦 - 葉輪不平衡 (Impeller Unbalance)"
        ]
    )
elif "工業風扇" in equipment_type:
    sound_condition = st.sidebar.selectbox(
        "2. 選擇風扇運轉狀態 (Fan Condition)",
        [
            "🟢 風扇 - 正常運轉 (Normal)",
            "🔴 風扇 - 葉片損壞/積垢 (Blade Damage)",
            "🟡 風扇 - 軸承過熱摩擦 (Bearing Friction)"
        ]
    )
else:
    sound_condition = st.sidebar.selectbox(
        "2. 選擇模擬音源類型",
        [
            "模擬正常運轉音頻", 
            "模擬軸承磨損異音 (高頻金屬摩擦)", 
            "模擬軸偏心異音 (顯著低頻振動與撞擊)", 
            "上傳 WAV 音檔"
        ]
    )

severity = st.sidebar.slider(
    "模擬故障嚴重程度 (Severity)",
    min_value=0.1,
    max_value=1.0,
    value=0.8,
    step=0.1,
    help="調整異音能量大小，觀察健康指標變化"
)

threshold = st.sidebar.slider(
    "異常判定門檻 (MSE Threshold)",
    min_value=0.01,
    max_value=0.20,
    value=0.05,
    step=0.01
)

st.sidebar.markdown("---")
if st.sidebar.button("🧹 清除歷史記錄"):
    st.session_state.history = pd.DataFrame(columns=['timestamp', 'health_index', 'mse_loss'])
    st.rerun()

# ---------------------------------------------------------
# 設備聲學模擬引擎
# ---------------------------------------------------------
def generate_equipment_audio(category, condition, sev=1.0):
    sr = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration))
    
    base_hum = 0.25 * np.sin(2 * np.pi * 60 * t) + 0.1 * np.sin(2 * np.pi * 120 * t)
    
    if "工業幫浦" in category:
        if "Normal" in condition or "正常運轉" in condition:
            water_flow = np.random.normal(0, 0.015, len(t))
            return base_hum + water_flow, sr
            
        elif "Cavitation" in condition or "洩漏/空蝕" in condition:
            high_bursts = (2.5 * sev) * np.sin(2 * np.pi * 4500 * t) * (np.random.rand(len(t)) > 0.80)
            hiss_noise = (1.2 * sev) * np.random.normal(0, 0.25, len(t)) * (np.sin(2 * np.pi * 15 * t) > -0.2)
            low_thump = (1.5 * sev) * np.sin(2 * np.pi * 120 * t) * (np.random.rand(len(t)) > 0.85)
            return base_hum + high_bursts + hiss_noise + low_thump, sr
            
        elif "Impeller" in condition or "葉輪不平衡" in condition:
            impeller_pulse = (3.0 * sev) * (np.maximum(0, np.sin(2 * np.pi * 4 * t)) ** 6) * np.sin(2 * np.pi * 200 * t)
            return base_hum + impeller_pulse, sr

    elif "工業風扇" in category:
        fan_blade_sound = 0.3 * np.sin(2 * np.pi * 150 * t)
        if "Normal" in condition or "正常運轉" in condition:
            return fan_blade_sound + np.random.normal(0, 0.01, len(t)), sr
        elif "Blade" in condition or "葉片損壞" in condition:
            blade_thump = (1.8 * sev) * np.sin(2 * np.pi * 5 * t) * np.sin(2 * np.pi * 350 * t)
            return fan_blade_sound + blade_thump, sr
        elif "Bearing" in condition or "軸承過熱" in condition:
            squeal = (2.0 * sev) * np.sin(2 * np.pi * 4200 * t)
            return fan_blade_sound + squeal, sr

    if "高頻金屬" in condition:
        friction = (1.5 * sev) * np.sin(2 * np.pi * 4000 * t)
        return base_hum + friction, sr
    elif "軸偏心" in condition:
        strike_env = np.maximum(0, np.sin(2 * np.pi * 3 * t)) ** 8
        impact = (3.5 * sev) * strike_env * np.sin(2 * np.pi * 180 * t)
        return base_hum + impact, sr

    return base_hum + np.random.normal(0, 0.015, len(t)), sr

# ---------------------------------------------------------
# 音訊載入與處理
# ---------------------------------------------------------
if "上傳 WAV" in sound_condition:
    uploaded_file = st.sidebar.file_uploader("上傳 WAV 音檔", type=["wav"])
    if uploaded_file is not None:
        y, sr = librosa.load(uploaded_file, sr=16000)
    else:
        st.info("💡 請上傳檔案，目前預設載入『幫浦正常運轉』")
        y, sr = generate_equipment_audio("🌊 工業幫浦 (Pump)", "正常運轉", severity)
else:
    y, sr = generate_equipment_audio(equipment_type, sound_condition, severity)

# ---------------------------------------------------------
# 特徵提取與診斷計算
# ---------------------------------------------------------
S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=256, n_mels=128)
S_dB = librosa.power_to_db(S, ref=np.max)

high_freq_peak = np.max(S_dB[70:, :])
low_freq_peak = np.max(S_dB[5:45, :])

is_normal_state = ("🟢" in sound_condition) or ("模擬正常" in sound_condition)

if is_normal_state:
    simulated_mse_loss = 0.0050
else:
    loss_calc = ((high_freq_peak + 50) / 70) * 0.18 + ((low_freq_peak + 20) / 50) * 0.22 + (severity * 0.1)
    simulated_mse_loss = float(np.clip(loss_calc, 0.065, 0.450))

if simulated_mse_loss <= threshold:
    health_index = int(100 - (simulated_mse_loss / threshold) * 15)
else:
    health_index = max(1, int(85 - ((simulated_mse_loss - threshold) / (0.45 - threshold)) * 84))

# 取得台灣時間 (Asia/Taipei UTC+8)
taiwan_tz = pytz.timezone('Asia/Taipei')
taiwan_time = datetime.now(taiwan_tz).strftime("%H:%M:%S")

new_data = pd.DataFrame([{
    'timestamp': taiwan_time,
    'health_index': health_index,
    'mse_loss': simulated_mse_loss
}])
st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)

# ---------------------------------------------------------
# 儀表板畫面呈現 (更新符合國人用語之診斷狀態)
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns([2, 2, 2, 3])

with col1:
    st.metric(
        label="設備健康指標 (HI)",
        value=f"{health_index} %",
        delta="狀態良好" if health_index >= 85 else ("需要關注" if health_index >= 60 else "高風險警報"),
        delta_color="normal" if health_index >= 85 else "inverse"
    )

with col2:
    st.metric(
        label="重構誤差 (MSE)",
        value=f"{simulated_mse_loss:.4f}",
        delta=f"門檻: {threshold:.2f}",
        delta_color="inverse" if simulated_mse_loss > threshold else "normal"
    )

with col3:
    st.subheader("診斷狀態")
    if health_index >= 85:
        st.success("🟢 正常 (Normal)")
    elif health_index >= 60:
        st.warning("⚠️ 警告 (Warning)")
    else:
        st.error("🚨 異常/故障 (Critical)")

with col4:
    st.subheader("🔊 採樣音頻試聽")
    y_norm = np.int16(y / np.max(np.abs(y)) * 32767)
    virtual_file = io.BytesIO()
    with wave.open(virtual_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(y_norm.tobytes())
    st.audio(virtual_file.getvalue(), format="audio/wav")

st.markdown("---")

# ---------------------------------------------------------
# 語譜圖呈現與說明卡片
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📊 直觀聲學語譜圖 (Frequency vs Time)", "📈 健康度歷史趨勢圖"])

with tab1:
    font_prop = FontProperties(family='DejaVu Sans', size=11, weight='bold')
    title_font = FontProperties(family='DejaVu Sans', size=13, weight='bold')
    
    fig, ax = plt.subplots(figsize=(12, 4.8))
    
    img = librosa.display.specshow(
        S_dB, 
        x_axis='time', 
        y_axis='linear', 
        sr=sr, 
        fmax=8000,
        ax=ax, 
        cmap='inferno',
        vmin=-55,
        vmax=0
    )
    
    fig.colorbar(img, ax=ax, format='%+2.0f dB')
    
    ax.set_title(f"Acoustic Spectrogram - {equipment_type}", fontproperties=title_font)
    ax.set_xlabel("Time (Seconds)", fontproperties=font_prop)
    ax.set_ylabel("Frequency (Hz)", fontproperties=font_prop)
    
    if "Cavitation" in sound_condition or "洩漏/空蝕" in sound_condition or "高頻" in sound_condition or "軸承" in sound_condition:
        rect = plt.Rectangle((0.02, 3200), 1.95, 4300, linewidth=2, edgecolor='yellow', facecolor='none', linestyle='--')
        ax.add_patch(rect)
        ax.text(0.05, 6200, "[CRITICAL] Cavitation & Leakage Anomaly Detected", color='yellow', fontproperties=font_prop)
    elif "Impeller" in sound_condition or "不平衡" in sound_condition or "低頻" in sound_condition or "Blade" in sound_condition:
        rect = plt.Rectangle((0.02, 100), 1.95, 1800, linewidth=2, edgecolor='cyan', facecolor='none', linestyle='--')
        ax.add_patch(rect)
        ax.text(0.05, 2100, "[WARNING] Low-Freq Anomaly Detected", color='cyan', fontproperties=font_prop)

    st.pyplot(fig)
    
    st.info("""
    💡 **圖表閱讀說明**：
    * **縱軸 Frequency (Hz)**：聲音頻率。幫浦空蝕/洩漏異音會出現顯著的 `3200 Hz ~ 7500 Hz` 高頻爆裂聲；葉輪不平衡則落在 `2000 Hz 以下`。
    * **右側能量條 (dB)**：代表聲音強弱。
      * 🟨 **黃亮色 / 0 dB**：代表出現強烈的異音衝擊與空蝕氣泡爆破（能量極高）。
      * ⬛ **純黑色 / -50 dB**：代表完全靜音或微弱背景音。
    """)

with tab2:
    if len(st.session_state.history) > 0:
        st.subheader("連續採樣健康度追蹤 (台灣時間 Asia/Taipei)")
        chart_data = st.session_state.history.set_index('timestamp')
        st.line_chart(chart_data[['health_index']])