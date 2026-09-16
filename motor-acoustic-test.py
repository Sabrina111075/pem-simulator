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
# 馬達音頻模擬器 (強化版異音特徵)
# ---------------------------------------------------------
def generate_simulated_audio(type_str="normal"):
    sr = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration))
    
    # 正常馬達聲：基頻 50Hz + 諧波 100Hz + 極低 background noise
    base_sound = 0.4 * np.sin(2 * np.pi * 50 * t) + 0.2 * np.sin(2 * np.pi * 100 * t)
    noise = np.random.normal(0, 0.02, len(t))
    
    if type_str == "high_freq":
        # 軸承磨損：強烈高頻 3800Hz 刺耳摩擦聲與隨機噪聲脈衝
        friction = 0.6 * np.sin(2 * np.pi * 3800 * t) * (np.sin(2 * np.pi * 8 * t) > 0.3)
        high_noise = np.random.normal(0, 0.15, len(t)) * (np.sin(2 * np.pi * 15 * t) > 0.5)
        return base_sound + noise + friction + high_noise, sr
        
    elif type_str == "low_freq":
        # 軸偏心：顯著的低頻敲擊衝擊波 (15Hz 週期脈衝 + 150Hz 偏心諧波衝擊)
        impulse_env = np.maximum(0, np.sin(2 * np.pi * 15 * t)) ** 4  # 尖銳衝擊包絡線
        eccentric_impact = 1.2 * impulse_env * np.sin(2 * np.pi * 150 * t)
        return base_sound + noise + eccentric_impact, sr
        
    return base_sound + noise, sr

# ---------------------------------------------------------
# 資料擷取
# ---------------------------------------------------------
if data_source == "模擬正常運轉音頻":
    y, sr = generate_simulated_audio("normal")
elif data_source == "模擬軸承磨損異音 (高頻金屬摩擦)":
    y, sr = generate_simulated_audio("high_freq")
elif data_source == "模擬軸偏心異音 (顯著低頻振動與撞擊)":
    y, sr = generate_simulated_audio("low_freq")
else:
    uploaded_file = st.sidebar.file_uploader("上傳 WAV 檔案", type=["wav"])
    if uploaded_file is not None:
        y, sr = librosa.load(uploaded_file, sr=16000)
    else:
        st.info("💡 請上傳檔案，目前預設載入『模擬正常運轉音頻』")
        y, sr = generate_simulated_audio("normal")

# ---------------------------------------------------------
# 特徵提取與模擬推論
# ---------------------------------------------------------
S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=256, n_mels=128)
S_dB = librosa.power_to_db(S, ref=np.max)

# 分析低頻與高頻異常區段能量
high_freq_energy = np.mean(S_dB[80:, :])  # 3kHz 以上
low_freq_energy = np.mean(S_dB[10:40, :])  # 200Hz ~ 1kHz 敲擊帶

simulated_mse_loss = float(np.clip((high_freq_energy + 45) / 120 + (low_freq_energy + 20) / 100, 0.005, 0.35))

if simulated_mse_loss <= threshold:
    health_index = int(100 - (simulated_mse_loss / threshold) * 15)
else:
    health_index = max(0, int(85 - ((simulated_mse_loss - threshold) / threshold) * 60))

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
        label="異常重構誤差 (MSE)",
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
# 畫面呈現：高清晰語譜圖與歷史趨勢
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📊 高對比聲學語譜圖 (Mel-Spectrogram)", "📈 健康度歷史趨勢圖"])

with tab1:
    fig, ax = plt.subplots(figsize=(12, 4.5))
    # 使用 magma 色階，並設定 vmin=-60dB 放大色階動態範圍
    img = librosa.display.specshow(
        S_dB, 
        x_axis='time', 
        y_axis='mel', 
        sr=sr, 
        fmax=8000,
        ax=ax, 
        cmap='magma',
        vmin=-60,
        vmax=0
    )
    fig.colorbar(img, ax=ax, format='%+2.0f dB')
    ax.set_title("Enhanced Mel-Spectrogram (Magma Palette)", fontsize=13, fontweight='bold')
    ax.set_xlabel("Time (s)", fontsize=11)
    ax.set_ylabel("Frequency (Hz)", fontsize=11)
    st.pyplot(fig)

with tab2:
    if len(st.session_state.history) > 0:
        st.subheader("連續採樣健康度追蹤")
        chart_data = st.session_state.history.set_index('timestamp')
        st.line_chart(chart_data[['health_index']])