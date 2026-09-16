import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

# 設定網頁標題與寬頁面
st.set_page_config(page_title="馬達健康度診斷測試平台", layout="wide")

st.title("⚙️ 馬達健康度與聲學診斷測試平台")
st.caption("邊緣運算前置驗證平台 | 支援 ESP32-S3 + Raspberry Pi 5 模擬測試")

# ---------------------------------------------------------
# 側邊欄控制項
# ---------------------------------------------------------
st.sidebar.header("🎛️ 測試控制台")
data_source = st.sidebar.selectbox(
    "選擇測試聲學來源",
    ["模擬正常運轉音頻", "模擬軸承磨損異音", "上傳 WAV 馬達音檔"]
)

threshold = st.sidebar.slider(
    "異常判定門檻 (MSE Threshold)",
    min_value=0.01,
    max_value=0.20,
    value=0.05,
    step=0.01,
    help="當重構誤差高於此數值時，系統將判定為異常"
)

# ---------------------------------------------------------
# 馬達音頻模擬器 (正弦波諧波 + 高頻雜訊)
# ---------------------------------------------------------
def generate_simulated_audio(anomaly=False):
    sr = 16000
    duration = 1.0  # 1秒採樣
    t = np.linspace(0, duration, int(sr * duration))
    
    # 正常馬達聲：50Hz 基頻 + 100Hz 諧波 + 低背景雜訊
    base_sound = 0.5 * np.sin(2 * np.pi * 50 * t) + 0.3 * np.sin(2 * np.pi * 100 * t)
    noise = np.random.normal(0, 0.05, len(t))
    
    if anomaly:
        # 異常馬達聲：加入 3500Hz 高頻摩擦與衝擊脈衝
        friction_noise = 0.4 * np.sin(2 * np.pi * 3500 * t) * (np.sin(2 * np.pi * 10 * t) > 0.5)
        return base_sound + noise + friction_noise, sr
    return base_sound + noise, sr

# ---------------------------------------------------------
# 資料擷取與語譜圖轉換
# ---------------------------------------------------------
if data_source == "模擬正常運轉音頻":
    y, sr = generate_simulated_audio(anomaly=False)
elif data_source == "模擬軸承磨損異音":
    y, sr = generate_simulated_audio(anomaly=True)
else:
    uploaded_file = st.sidebar.file_uploader("請上傳 WAV 格式馬達聲音檔", type=["wav"])
    if uploaded_file is not None:
        y, sr = librosa.load(uploaded_file, sr=16000)
    else:
        st.info("💡 未上傳檔案，預設載入『模擬正常運轉音頻』")
        y, sr = generate_simulated_audio(anomaly=False)

# 計算 Mel 語譜圖 (Mel-Spectrogram)
S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=512, n_mels=64)
S_dB = librosa.power_to_db(S, ref=np.max)

# 模擬 Autoencoder 計算高頻重構誤差 (MSE Loss)
high_freq_energy = np.mean(S_dB[40:, :])  # 取 3kHz 以上高頻區段
simulated_mse_loss = float(np.clip((high_freq_energy + 40) / 200, 0.005, 0.30))

# 計算健康度指標 (Health Index, 0~100%)
if simulated_mse_loss <= threshold:
    health_index = int(100 - (simulated_mse_loss / threshold) * 15)
else:
    health_index = max(0, int(85 - ((simulated_mse_loss - threshold) / threshold) * 60))

# ---------------------------------------------------------
# 畫面呈現區域
# ---------------------------------------------------------
# 1. 頂部狀態數據列
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="馬達健康指標 (Health Index)",
        value=f"{health_index} %",
        delta="狀態良好" if health_index >= 85 else ("需要關注" if health_index >= 60 else "高風險警報"),
        delta_color="normal" if health_index >= 85 else "inverse"
    )

with col2:
    st.metric(
        label="異常重構誤差 (MSE Loss)",
        value=f"{simulated_mse_loss:.4f}",
        delta=f"門檻值: {threshold:.2f}",
        delta_color="inverse" if simulated_mse_loss > threshold else "normal"
    )

with col3:
    st.subheader("即時狀態判定")
    if health_index >= 85:
        st.success("🟢 正常運轉 (Normal)")
    elif health_index >= 60:
        st.warning("🟡 預防維護告警 (Warning)")
    else:
        st.error("🔴 嚴重異音/故障 (Critical)")

st.markdown("---")

# 2. 聲學語譜圖視覺化
st.subheader("📊 馬達聲學語譜圖 (Mel-Spectrogram)")
st.caption("橫軸為時間、縱軸為頻率 (Hz)。黃綠色亮區代表該頻段能量強烈，高頻頻域突變通常代表摩擦或敲擊異音。")

fig, ax = plt.subplots(figsize=(10, 3.8))
img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, ax=ax, cmap='viridis')
fig.colorbar(img, ax=ax, format='%+2.0f dB')
ax.set_title("Mel-Spectrogram Analysis", fontsize=12)
st.pyplot(fig)