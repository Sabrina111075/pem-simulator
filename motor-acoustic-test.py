import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import librosa
import librosa.display
import pandas as pd
import io
import wave
import re
from datetime import datetime, timezone, timedelta

# 重設 Matplotlib 全局設定
plt.rcdefaults()

st.set_page_config(page_title="馬達與工業設備聲學診斷測試平台", layout="wide")

st.title("⚙️ 馬達與工業設備聲學診斷測試平台 (EdgeAcoustic AI)")
st.caption("邊緣運算前置驗證平台 | 支援 ESP32-S3 + Raspberry Pi 5 模擬測試")

# ---------------------------------------------------------
# 初始化歷史數據紀錄
# ---------------------------------------------------------
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['timestamp', 'health_index', 'mse_loss'])

# ---------------------------------------------------------
# 兩層式控制項
# ---------------------------------------------------------
st.sidebar.header("🎛️ 設備與測試控制台")

equipment_type = st.sidebar.selectbox(
    "1. 選擇設備類別 (Category)",
    [
        "⚡ 工業馬達 (Motor)",
        "🌊 工業幫浦 (Pump)", 
        "🌀 工業風扇 (Fan)", 
        "🎛️ 工業滑軌與閥門 (Slider/Valve)",
        "⚙️ 變速箱與齒輪 (Gearbox)",
        "🔬 測試模擬與自訂上傳"
    ]
)

# 狀態選單動態切換
if "Motor" in equipment_type or "馬達" in equipment_type:
    sound_condition = st.sidebar.selectbox(
        "2. 選擇馬達運轉狀態 (Motor Condition)",
        [
            "🟢 馬達 - 正常運轉 (Normal)",
            "🔴 馬達 - 軸承磨損異音 (Bearing Fault)",
            "🟡 馬達 - 轉子偏心/不平衡 (Unbalance Fault)"
        ]
    )
elif "Pump" in equipment_type or "幫浦" in equipment_type:
    sound_condition = st.sidebar.selectbox(
        "2. 選擇幫浦運轉狀態 (Pump Condition)",
        [
            "🟢 幫浦 - 正常運轉 (Normal)",
            "🔴 幫浦 - 洩漏/空蝕異常 (Leaking / Cavitation)",
            "🟡 幫浦 - 葉輪不平衡 (Impeller Unbalance)"
        ]
    )
elif "Fan" in equipment_type or "風扇" in equipment_type:
    sound_condition = st.sidebar.selectbox(
        "2. 選擇風扇運轉狀態 (Fan Condition)",
        [
            "🟢 風扇 - 正常運轉 (Normal)",
            "🔴 風扇 - 葉片損壞/積垢 (Blade Damage)",
            "🟡 風扇 - 軸承過熱摩擦 (Bearing Friction)"
        ]
    )
elif "Slider" in equipment_type or "滑軌" in equipment_type:
    sound_condition = st.sidebar.selectbox(
        "2. 選擇滑軌/閥門狀態 (Slider/Valve Condition)",
        [
            "🟢 滑軌 - 平順滑移 (Normal)",
            "🔴 滑軌 - 軌道異物卡阻/阻塞 (Rail Obstruction)",
            "🟡 閥門 - 內部高壓氣洩漏 (Pressure Leak)"
        ]
    )
elif "Gearbox" in equipment_type or "齒輪" in equipment_type:
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
    step=0.1
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
    
    base_hum = 0.2 * np.sin(2 * np.pi * 60 * t) + 0.08 * np.sin(2 * np.pi * 120 * t)
    
    if "Motor" in category or "馬達" in category:
        if "Normal" in condition or "正常" in condition:
            return base_hum + np.random.normal(0, 0.005, len(t)), sr
        elif "Bearing" in condition or "軸承磨損" in condition:
            high_squeal = (2.8 * sev) * np.sin(2 * np.pi * 4200 * t)
            pulses = (1.5 * sev) * (np.maximum(0, np.sin(2 * np.pi * 12 * t)) ** 10) * np.sin(2 * np.pi * 2500 * t)
            return base_hum + high_squeal + pulses, sr
        elif "Unbalance" in condition or "偏心" in condition:
            eccentric_vibe = (3.2 * sev) * np.sin(2 * np.pi * 30 * t) * np.sin(2 * np.pi * 180 * t)
            return base_hum + eccentric_vibe, sr

    elif "Pump" in category or "幫浦" in category:
        if "Normal" in condition or "正常" in condition:
            return base_hum + np.random.normal(0, 0.005, len(t)), sr
        elif "Cavitation" in condition or "洩漏" in condition:
            high_bursts = (3.0 * sev) * np.sin(2 * np.pi * 4800 * t) * (np.random.rand(len(t)) > 0.75)
            hiss_noise = (1.5 * sev) * np.random.normal(0, 0.3, len(t))
            return base_hum + high_bursts + hiss_noise, sr
        elif "Impeller" in condition or "葉輪" in condition:
            impeller_pulse = (3.5 * sev) * (np.maximum(0, np.sin(2 * np.pi * 4 * t)) ** 6) * np.sin(2 * np.pi * 200 * t)
            return base_hum + impeller_pulse, sr

    elif "Fan" in category or "風扇" in category:
        fan_blade = 0.25 * np.sin(2 * np.pi * 150 * t)
        if "Normal" in condition or "正常" in condition:
            return fan_blade + np.random.normal(0, 0.005, len(t)), sr
        elif "Blade" in condition or "葉片" in condition:
            blade_thump = (2.5 * sev) * np.sin(2 * np.pi * 5 * t) * np.sin(2 * np.pi * 350 * t)
            return fan_blade + blade_thump, sr
        elif "Bearing" in condition or "軸承" in condition:
            squeal = (2.8 * sev) * np.sin(2 * np.pi * 4500 * t)
            return fan_blade + squeal, sr

    elif "Slider" in category or "滑軌" in category:
        slide = 0.15 * np.sin(2 * np.pi * 80 * t)
        if "Normal" in condition or "平順" in condition:
            return slide + np.random.normal(0, 0.005, len(t)), sr
        elif "Obstruction" in condition or "異物" in condition:
            clack = (3.0 * sev) * (np.random.rand(len(t)) > 0.90) * np.sin(2 * np.pi * 1500 * t)
            return slide + clack, sr
        elif "Pressure Leak" in condition or "洩漏" in condition:
            hiss = (2.5 * sev) * np.random.normal(0, 0.35, len(t))
            return slide + hiss, sr

    elif "Gearbox" in category or "齒輪" in category:
        gear = 0.2 * np.sin(2 * np.pi * 800 * t)
        if "Normal" in condition or "正常" in condition:
            return gear + np.random.normal(0, 0.005, len(t)), sr
        elif "Gear Damage" in condition or "崩角" in condition:
            impact = (3.0 * sev) * (np.maximum(0, np.sin(2 * np.pi * 8 * t)) ** 12) * np.sin(2 * np.pi * 2800 * t)
            return gear + impact, sr
        elif "Lubrication" in condition or "潤滑" in condition:
            dry_friction = (2.2 * sev) * np.sin(2 * np.pi * 4000 * t) * (np.random.rand(len(t)) > 0.3)
            return gear + dry_friction, sr

    return base_hum + np.random.normal(0, 0.005, len(t)), sr

# ---------------------------------------------------------
# 音訊診斷與指標計算
# ---------------------------------------------------------
if "上傳 WAV" in sound_condition:
    uploaded_file = st.sidebar.file_uploader("上傳 WAV 音檔", type=["wav"])
    if uploaded_file is not None:
        y, sr = librosa.load(uploaded_file, sr=16000)
    else:
        st.info("💡 請上傳檔案，預設載入『馬達正常運轉』")
        y, sr = generate_equipment_audio("⚡ 工業馬達 (Motor)", "正常運轉", severity)
else:
    y, sr = generate_equipment_audio(equipment_type, sound_condition, severity)

S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=256, n_mels=128)
S_dB = librosa.power_to_db(S, ref=np.max)

high_freq_peak = np.max(S_dB[70:, :])
low_freq_peak = np.max(S_dB[5:45, :])

is_normal_state = ("🟢" in sound_condition) or ("Normal" in sound_condition) or ("模擬正常" in sound_condition)

if is_normal_state:
    simulated_mse_loss = 0.0015
    health_index = 98
else:
    loss_calc = 0.095 + ((high_freq_peak + 50) / 70) * 0.12 + (severity * 0.15)
    simulated_mse_loss = float(np.clip(loss_calc, 0.0900, 0.4800))
    health_index = max(1, int(52 - ((simulated_mse_loss - threshold) / (0.48 - threshold)) * 50))

tz_taiwan = timezone(timedelta(hours=8))
taiwan_time = datetime.now(tz_taiwan).strftime("%H:%M:%S")

new_data = pd.DataFrame([{
    'timestamp': taiwan_time,
    'health_index': health_index,
    'mse_loss': simulated_mse_loss
}])
st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)

# ---------------------------------------------------------
# 畫面呈現
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
# 全時設備維運與故障排除建議卡片 (優化版 SOP)
# ---------------------------------------------------------
st.markdown("---")

if health_index >= 85:
    st.success("### 🛠️ 設備日常巡檢維運指引 (Routine Maintenance Guide)")
    st.markdown("""
    * **運轉狀態評估**：當前聲學特徵穩定，訊號重構誤差 (MSE) 處於安全基準線以下。
    * **日常巡檢建議**：
      1. **外觀與溫度**：定期量測馬達/設備外殼溫升，確認風路與散熱片無積塵遮蔽。
      2. **振動與緊固**：檢查基座螺絲與地腳螺栓是否緊固，無異常共振情況。
      3. **定期保養**：維持既定保養週期，建議每 2000 小時進行一次聲學基準線比對。
    """)
else:
    if health_index < 60:
        st.error("### 🚨 系統緊急排除與維修建議 (Critical Maintenance Actions)")
    else:
        st.warning("### ⚠️ 設備預防性維護建議 (Warning & Preventive Actions)")
    
    if "軸承" in sound_condition or "Bearing" in sound_condition:
        st.markdown("""
        * **診斷分析**：高頻區段（>3500 Hz）聲波能量異常，屬於典型的**軸承滾珠磨損或缺油摩擦特徵**。
        * **標準處置流程（SOP）**：
          1. **步驟 1（處置）**：使用高壓注油槍**補充 ISO VG 輕質潤滑黃油**，並觀察高頻異音是否平緩。
          2. **步驟 2（停機檢修）**：若補油後 MSE 誤差未下降，請排定停機，使用拉拔器拆卸並**更換前後軸承組**。
        * **現場安全提示**：檢修前請確保執行 LOTO ( lockout/tagout ) 上鎖掛牌程序。
        """)
    elif "偏心" in sound_condition or "Unbalance" in sound_condition:
        st.markdown("""
        * **診斷分析**：低頻區段（<200 Hz）顯著週期性脈衝，反映**轉子動不平衡或聯軸器中心偏移**。
        * **標準處置流程（SOP）**：
          1. **步驟 1（檢測）**：使用雷射對心儀重新對齊馬達與負載端軸心（公差控制於 0.05 mm 內）。
          2. **步驟 2（校正）**：檢查底座防震墊片與對點螺絲，必要時進行現場**動平衡加重校正**。
        """)
    elif "葉片" in sound_condition or "Blade" in sound_condition:
        st.markdown("""
        * **診斷分析**：風切頻率伴隨中頻撞擊聲，主因為**風扇葉片積垢或結構龜裂**。
        * **標準處置流程（SOP）**：
          1. **步驟 1（清創）**：停機並使用高壓空氣槍**清理葉片表面附著油污與粉塵**。
          2. **步驟 2（更換）**：檢查葉片根部是否有應力裂痕，如有損壞請**整體更換風扇葉輪組**。
        """)
    elif "空蝕" in sound_condition or "洩漏" in sound_condition or "Cavitation" in sound_condition:
        st.markdown("""
        * **診斷分析**：高頻爆裂雜訊（Bubble Bursts），為**管路氣蝕或流體高壓洩漏**特徵。
        * **標準處置流程（SOP）**：
          1. **步驟 1（流體檢查）**：檢查進水端閥門開度與入口壓力，避免泵浦產生氣蝕現象。
          2. **步驟 2（密封處置）**：使用超音波漏氣偵測器尋找洩漏點，並**更換老化 O 型密封環與法蘭墊片**。
        """)
    elif "卡阻" in sound_condition or "Obstruction" in sound_condition:
        st.markdown("""
        * **診斷分析**：滑軌運轉出現非週期性脈衝衝擊音，為**軌道異物卡阻或鋼珠破損**。
        * **標準處置流程（SOP）**：
          1. **步驟 1（清潔）**：停止滑台運轉，清理滑軌溝槽內的切削屑與金屬異物。
          2. **步驟 2（滑塊檢修）**：檢查線性滑塊刮油片與內部鋼珠鏈，補充鋰基潤滑脂。
        """)
    elif "崩角" in sound_condition or "Gear Damage" in sound_condition:
        st.markdown("""
        * **診斷分析**：齒輪咬合頻率倍頻強度劇增，顯示**齒面有崩角、點蝕或嚴重剝落**。
        * **標準處置流程（SOP）**：
          1. **步驟 1（油品檢查）**：抽取齒輪油樣品，檢查是否有金屬磨屑，並**清除磁性排油螺栓金屬粉末**。
          2. **步驟 2（開箱更換）**：開啟齒輪箱上蓋檢視齒面，建議更換受損齒輪對並重新調整咬合間隙。
        """)
    elif "潤滑" in sound_condition or "Lubrication" in sound_condition:
        st.markdown("""
        * **診斷分析**：寬頻乾摩擦聲響，顯示**齒輪/軸承介面潤滑油膜破裂**。
        * **標準處置流程（SOP）**：
          1. **步驟 1（補油）**：檢查齒輪箱油位計，補充極壓（EP）工業齒輪油至標準油位。
          2. **步驟 2（油質監測）**：檢測油溫是否過高，並檢查潤滑油幫浦循環壓力是否正常。
        """)
    else:
        st.markdown("""
        * **診斷分析**：聲學特徵偏離基準線，重構誤差超越安全門檻。
        * **標準處置流程（SOP）**：
          1. **步驟 1**：進行現場複測，確認麥克風感測器安裝位置與固緊狀態。
          2. **步驟 2**：使用手持式震動分析儀輔查量測，確認設備機械結構無鬆動。
        """)

st.markdown("---")

# ---------------------------------------------------------
# 語譜圖與歷史趨勢圖
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📊 直觀聲學語譜圖 (Frequency vs Time)", "📈 健康度歷史趨勢圖"])

with tab1:
    font_prop = FontProperties(family='DejaVu Sans', size=11, weight='bold')
    title_font = FontProperties(family='DejaVu Sans', size=13, weight='bold')
    
    clean_title = re.sub(r'[^\x00-\x7F]+', '', equipment_type).strip()
    
    fig, ax = plt.subplots(figsize=(12, 4.8))
    img = librosa.display.specshow(S_dB, x_axis='time', y_axis='linear', sr=sr, fmax=8000, ax=ax, cmap='viridis', vmin=-55, vmax=0)
    cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
    cbar.ax.set_ylabel("Energy Level (dB)", fontproperties=font_prop)
    
    ax.set_title(f"Acoustic Spectrogram - {clean_title}", fontproperties=title_font)
    ax.set_xlabel("Time (Seconds)", fontproperties=font_prop)
    ax.set_ylabel("Frequency (Hz)", fontproperties=font_prop)
    
    if health_index < 85:
        rect = plt.Rectangle((0.02, 1000), 1.95, 6500, linewidth=2, edgecolor='red', facecolor='none', linestyle='--')
        ax.add_patch(rect)
        ax.text(0.05, 7000, "[ANOMALY DETECTED] Maintenance Recommended", color='yellow', fontproperties=font_prop)

    st.pyplot(fig)
    
    st.info("""
    💡 **聲學語譜圖 (Spectrogram) 操作指南與軸線說明：**
    * **橫軸 X 軸 (Time)**：聲音的時間軸（秒）。
    * **縱軸 Y 軸 (Frequency)**：音頻頻率（Hz）。低頻區（如 < 500 Hz）反映轉速與偏心震動；高頻區（如 > 3000 Hz）反映金屬摩擦、軸承磨損與高壓氣流洩漏。
    * **顏色強度 (Energy Level)**：採用 **Viridis 柔和視覺色階**。**深藍/紫黑** 代表無聲音背景；**亮黃/綠色亮線** 代表強烈異常聲音頻率點。
    """)

with tab2:
    if len(st.session_state.history) > 0:
        st.subheader("連續採樣健康度追蹤 (台灣時間 UTC+8)")
        recent_history = st.session_state.history.tail(30)
        chart_data = recent_history.set_index('timestamp')
        st.line_chart(chart_data[['health_index']])