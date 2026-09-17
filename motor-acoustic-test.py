import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import librosa
import librosa.display
import pandas as pd
import io
import wave
from datetime import datetime, timezone, timedelta

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

# 第一層：選擇設備類別 (擴充 DCASE 範例類別)
equipment_type = st.sidebar.selectbox(
    "1. 選擇設備類別 (Category)",
    [
        "🌊 工業幫浦 (Pump)", 
        "🌀 工業風扇 (Fan)", 
        "🎛️ 工業滑軌與閥門 (Slider/Valve)",
        "⚙️ 變速箱與齒輪 (Gearbox)",
        "🔬 測試模擬與自訂上傳"
    ]
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
elif "滑軌與閥門" in equipment_type:
    sound_condition = st.sidebar.selectbox(
        "2. 選擇滑軌/閥門狀態 (Slider/Valve Condition)",
        [
            "🟢 滑軌 - 平順滑移 (Normal)",
            "🔴 滑軌 - 軌道異物卡阻/阻塞 (Rail Obstruction)",
            "🟡 閥門 - 內部高壓氣洩漏 (Pressure Leak)"
        ]
    )
elif "變速箱與齒輪" in equipment_type:
    sound_condition = st.sidebar.selectbox(
        "2. 選擇齒輪狀態 (Gearbox Condition)",
        [
            "🟢 齒輪 - 正常咬合運轉 (Normal)",
            "🔴 齒輪 - 齒面崩角/嚴重磨損 (Gear Damage)",
            "🟡 齒輪 - 缺乏潤滑乾摩擦 (Lack of Lubrication)"
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
# 設備聲學模擬引擎 (擴充 DCASE 聲學模型)
# ---------------------------------------------------------
def generate_equipment_audio(category, condition, sev=1.0):
    sr = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration))
    
    base_hum = 0.25 * np.sin(2 * np.pi * 60 * t) + 0.1 * np.sin(2 * np.pi * 120 * t)
    
    if "工業幫浦" in category:
        if "Normal" in condition or "正常運轉" in condition:
            return base_hum + np.random.normal(0, 0.015, len(t)), sr
        elif "Cavitation" in condition or "洩漏/空蝕" in condition:
            high_bursts = (2.5 * sev) * np.sin(2 * np.pi * 4500 * t) * (np.random.rand(len(t)) > 0.80)
            hiss_noise = (1.2 * sev) * np.random.normal(0, 0.25, len(t)) * (np.sin(2 * np.pi * 15 * t) > -0.2)
            return base_hum + high_bursts + hiss_noise, sr
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

    elif "滑軌與閥門" in category:
        slide_sound = 0.2 * np.sin(2 * np.pi * 80 * t)
        if "Normal" in condition or "平順" in condition:
            return slide_sound + np.random.normal(0, 0.01, len(t)), sr
        elif "Obstruction" in condition or "異物卡阻" in condition:
            clack = (2.2 * sev) * (np.random.rand(len(t)) > 0.92) * np.sin(2 * np.pi * 1200 * t)
            return slide_sound + clack, sr
        elif "Pressure Leak" in condition or "氣洩漏" in condition:
            hiss = (2.0 * sev) * np.random.normal(0, 0.3, len(t))
            return slide_sound + hiss, sr

    elif "變速箱與齒輪" in category:
        gear_mesh = 0.3 * np.sin(2 * np.pi * 800 * t)
        if "Normal" in condition or "正常" in condition:
            return gear_mesh + np.random.normal(0, 0.01, len(t)), sr
        elif "Gear Damage" in condition or "齒面崩角" in condition:
            impact = (2.5 * sev) * (np.maximum(0, np.sin(2 * np.pi * 8 * t)) ** 12) * np.sin(2 * np.pi * 2500 * t)
            return gear_mesh + impact, sr
        elif "Lubrication" in condition or "缺乏潤滑" in condition:
            dry_friction = (1.8 * sev) * np.sin(2 * np.pi * 3800 * t) * (np.random.rand(len(t)) > 0.4)
            return gear_mesh + dry_friction, sr

    if "高頻金屬" in condition:
        return base_hum + (1.5 * sev) * np.sin(2 * np.pi * 4000 * t), sr
    elif "軸偏心" in condition:
        impact = (3.5 * sev) * (np.maximum(0, np.sin(2 * np.pi * 3 * t)) ** 8) * np.sin(2 * np.pi * 180 * t)
        return base_hum + impact, sr

    return base_hum + np.random.normal(0, 0.015, len(t)), sr

# ---------------------------------------------------------
# 音訊載入與診斷計算
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

# 精確獲取台灣時間 (UTC+8)
tz_taiwan = timezone(timedelta(hours=8))
taiwan_time = datetime.now(tz_taiwan).strftime("%H:%M:%S")

new_data = pd.DataFrame([{
    'timestamp': taiwan_time,
    'health_index': health_index,
    'mse_loss': simulated_mse_loss
}])
st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)

# ---------------------------------------------------------
# 儀表板畫面呈現
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

# ---------------------------------------------------------
# 智慧維修與故障排除建議卡片 (根據診斷狀態動態觸發)
# ---------------------------------------------------------
if health_index < 85:
    st.markdown("---")
    if health_index < 60:
        st.error("### 🚨 系統緊急排除與維修建議 (Critical Maintenance Actions)")
    else:
        st.warning("### ⚠️ 設備預防性維護建議 (Warning & Preventive Actions)")
    
    # 根據不同設備與故障類型給出實用建議
    if "葉片損壞" in sound_condition:
        st.write("🛠️ **建議動作**：偵測到風扇葉片不平衡或嚴重積垢。請停機檢查並**清理葉片表面粉塵**，若葉片有結構龜裂或破損，**建議更換風扇葉片組**。")
    elif "軸承過熱" in sound_condition or "高頻金屬" in sound_condition:
        st.write("🛠️ **建議動作**：高頻摩擦音顯著，代表軸承缺油或滾珠磨損。請立即**補充黃油潤滑劑**；若補油後高頻異音未消除，請預約停機**更換馬達軸承**。")
    elif "洩漏/空蝕" in sound_condition:
        st.write("🛠️ **建議動作**：管路出現氣蝕（Cavitation）或高壓洩漏。請**檢查進水閥門開度**以排除負壓，並**清潔進水口過濾網與馬達阻塞頭**。")
    elif "葉輪不平衡" in sound_condition or "軸偏心" in sound_condition:
        st.write("🛠️ **建議動作**：低頻震動能量偏高。請檢查**聯軸器是否偏心**、底座螺絲是否鬆動，並**重新進行馬達動平衡校正**。")
    elif "異物卡阻" in sound_condition:
        st.write("🛠️ **建議動作**：滑軌衝擊聲異常。請立即**清理滑軌溝槽異物與屑料**，並檢查線性滑塊鋼珠是否破損。")
    elif "氣洩漏" in sound_condition:
        st.write("🛠️ **建議動作**：氣壓閥門顯著洩漏。請使用肥皂水進行**接頭鎖緊檢測**，並**更換老化的 O 型密封環**。")
    elif "齒面崩角" in sound_condition:
        st.write("🛠️ **建議動作**：齒輪咬合週期性衝擊音。請開啟齒輪箱檢查**齒面是否有崩角或斷齒**，必要時**更換受損齒輪對**。")
    elif "缺乏潤滑" in sound_condition:
        st.write("🛠️ **建議動作**：齒輪乾摩擦音。請檢查**齒輪箱齒輪油位**，並**補充或更換高黏度齒輪潤滑油**。")
    else:
        st.write("🛠️ **建議動作**：聲學訊號超出安全門檻。建議維修人員攜帶手持式震動分析儀進行現場複測，並檢查設備固定螺絲。")

st.markdown("---")

# ---------------------------------------------------------
# 語譜圖與歷史趨勢圖
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📊 直觀聲學語譜圖 (Frequency vs Time)", "📈 健康度歷史趨勢圖"])

with tab1:
    font_prop = FontProperties(family='DejaVu Sans', size=11, weight='bold')
    title_font = FontProperties(family='DejaVu Sans', size=13, weight='bold')
    
    fig, ax = plt.subplots(figsize=(12, 4.8))
    img = librosa.display.specshow(S_dB, x_axis='time', y_axis='linear', sr=sr, fmax=8000, ax=ax, cmap='inferno', vmin=-55, vmax=0)
    fig.colorbar(img, ax=ax, format='%+2.0f dB')
    
    ax.set_title(f"Acoustic Spectrogram - {equipment_type}", fontproperties=title_font)
    ax.set_xlabel("Time (Seconds)", fontproperties=font_prop)
    ax.set_ylabel("Frequency (Hz)", fontproperties=font_prop)
    
    if health_index < 85:
        rect = plt.Rectangle((0.02, 1000), 1.95, 6500, linewidth=2, edgecolor='red', facecolor='none', linestyle='--')
        ax.add_patch(rect)
        ax.text(0.05, 7000, "[ANOMALY DETECTED] Maintenance Recommended", color='yellow', fontproperties=font_prop)

    st.pyplot(fig)

with tab2:
    if len(st.session_state.history) > 0:
        st.subheader("連續採樣健康度追蹤 (台灣時間 UTC+8)")
        recent_history = st.session_state.history.tail(30)
        chart_data = recent_history.set_index('timestamp')
        st.line_chart(chart_data[['health_index']])