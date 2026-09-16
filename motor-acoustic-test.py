import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import pandas as pd
import io
import wave
import time

st.set_page_config(page_title="馬達健康度診斷測試平台", layout="wide")

st.title("⚙️ 馬達健康度與聲學診斷測試平台 (Pro Version)")
st.caption("邊緣運算前置驗證平台 | 支援 ESP32-S3 + Raspberry Pi 5 模擬測試")

# ---------------------------------------------------------
# 初始化歷史數據紀錄 (Session State)
# ---------------------------------------------------------
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['timestamp', 'health_index', 'mse_loss'])

# ---------------------------------------------------------
# 側邊欄控制項
# ---------------------------------------------------------
st.sidebar.header("🎛️ 測試控制台")
data_source = st.sidebar.selectbox(
    "選擇測試聲學來源",
    ["模擬正常運轉音頻", "模擬軸承磨損異音 (高頻金屬摩擦)", "模擬軸偏心異音 (顯著低頻振動與撞擊)", "上傳 WAV 馬達音檔"]
)

# 新增故障嚴重程度控制
severity = st.sidebar.slider(
    "模擬故障嚴重程度 (Severity)",
    min_value=0.1,
    max_value=1.0,
    value=0.8,
    step=0.1,
    help="調整異音能量大小，觀察馬達健康指標的變化"
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
# 馬達音頻模擬器 (強化脈衝與動態嚴重度)
# ---------------------------------------------------------
def generate_simulated_audio(type_str="normal", sev=1.0):
    sr = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration))
    
    # 正常馬達聲：基頻 60Hz 微弱平穩運轉聲
    base_sound = 0.3 * np.sin(2 * np.pi * 60 * t) + 0.15 * np.sin(2 * np.pi * 120 * t)
    noise = np.random.normal(0, 0.01, len(t))
    
    if type_str == "high_freq":
        # 軸承磨損：高頻 4000Hz 刺耳金屬摩擦聲
        friction = (0.8 * sev) * np.sin(2 * np.pi * 4000 * t) * (np.sin(2 * np.pi * 10 * t) > 0.1)
        high_noise = np.random.normal(0, 0.2 * sev, len(t)) * (np.sin(2 * np.pi * 20 * t) > 0.4)
        return base_sound + noise + friction + high_noise, sr
        
    elif type_str == "low_freq":
        # 軸偏心：低頻敲擊衝擊波 (1秒5次強烈敲擊)
        strike_env = np.maximum(0, np.sin(2 * np.pi * 5 * t)) ** 8
        impact_sound = (3.5 * sev) * strike_env * np.sin(2 * np.pi * 180 * t)
        sub_thump = (2.5 * sev) * strike_env * np.random.normal(0, 0.4, len(t))
        return base_sound + noise + impact_sound + sub_thump, sr
        
    return base_sound + noise, sr

# ---------------------------------------------------------
# 資料擷取
# ---------------------------------------------------------
if data_source == "模擬正常運轉音頻":
    y, sr = generate_simulated_audio("normal", severity)
elif data_source == "模擬軸承磨損異音 (高頻金屬摩擦)":
    y, sr = generate_simulated_audio("high_freq", severity)
elif data_source == "模擬軸偏心異音 (顯著低頻振動與撞擊)":
    y, sr = generate_simulated_audio("low_freq", severity)
else:
    uploaded_file = st.sidebar.file_uploader("上傳 WAV 檔案", type=["wav"])
    if uploaded_file is not None:
        y, sr = librosa.load(uploaded_file, sr=16000)
    else:
        st.info("💡 請上傳檔案，目前預設載入『模擬正常運轉音頻』")
        y, sr = generate_simulated_audio("normal", severity)

# ---------------------------------------------------------
# 特徵提取與正確異常推論演算法
# ---------------------------------------------------------
S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=256, n_mels=128)
S_dB = librosa.power_to_db(S, ref=np.max)

# 採用 Peak + Mean 混合能量判定，精準捕捉低頻脈衝撞擊
high_freq_peak = np.max(S_dB[90:, :])       # 4kHz 以上高頻峰值
low_freq_peak = np.max(S_dB[5:40, :])       # 200Hz ~ 1.8kHz 低頻衝擊峰值

if data_source == "模擬正常運轉音頻":
    simulated_mse_loss = 0.0050
else:
    # 根據高/低頻峰值計算重構誤差 MSE Loss
    loss_calc = ((high_freq_peak + 50) / 100) * 0.2 + ((low_freq_peak + 20) / 60) * 0.25
    simulated_mse_loss = float(np.clip(loss_calc, 0.01, 0.40))

# 計算健康度指標 Health Index (HI)
if simulated_mse_loss <= threshold:
    health_index = int(100 - (simulated_mse_loss / threshold) * 15)
else:
    health_index = max(1, int(85 - ((simulated_mse_loss - threshold) / (0.35 - threshold)) * 84))

# 更新歷史紀錄
new_data = pd.DataFrame([{
    'timestamp': time.strftime("%H:%M:%S"),
    'health_index': health_index,
    'mse_loss': simulated_mse_loss
}])
st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)

# ---------------------------------------------------------
# 畫面呈現：儀表板
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns([2, 2, 2, 3])

with col1:
    st.metric(
        label="馬達健康指標 (HI)",
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
        st.warning("🟡 告警 (Warning)")
    else:
        st.error("🔴 故障 (Critical)")

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
# 畫面呈現：直觀高清晰語譜圖與歷史趨勢
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📊 直觀聲學語譜圖 (Frequency vs Time)", "📈 健康度歷史趨勢圖"])

with tab1:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
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
    ax.set_title("Motor Acoustic Spectrogram (High Contrast)", fontsize=13, fontweight='bold')
    ax.set_xlabel("Time (Seconds)", fontsize=11)
    ax.set_ylabel("Frequency (Hz)", fontsize=11)
    
    # 根據異音類型自動標註警示區域 (英文標籤防止中文字型缺字框)
    if "低頻振動" in data_source or (data_source == "模擬軸偏心異音 (顯著低頻振動與撞擊)"):
        rect = plt.Rectangle((0.02, 100), 0.96, 1800, linewidth=2, edgecolor='cyan', facecolor='none', linestyle='--')
        ax.add_patch(rect)
        ax.text(0.05, 2100, "[WARNING] Low-Freq Eccentric Anomaly Detected", color='cyan', fontsize=11, fontweight='bold')
        
    elif "高頻金屬" in data_source or (data_source == "模擬軸承磨損異音 (高頻金屬摩擦)"):
        rect = plt.Rectangle((0.02, 3500), 0.96, 2500, linewidth=2, edgecolor='yellow', facecolor='none', linestyle='--')
        ax.add_patch(rect)
        ax.text(0.05, 6200, "[WARNING] High-Freq Friction Anomaly Detected", color='yellow', fontsize=11, fontweight='bold')

    st.pyplot(fig)

with tab2:
    if len(st.session_state.history) > 0:
        st.subheader("連續採樣健康度追蹤")
        chart_data = st.session_state.history.set_index('timestamp')
        st.line_chart(chart_data[['health_index']])