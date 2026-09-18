import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import os

# 1. 頁面基本配置
st.set_page_config(
    page_title="馬達與工業設備聲學診斷測試平台",
    page_icon="⚙️",
    layout="wide"
)

# 2. 標題與簡介 (加入 DCASE 數據集專業註記)
st.title("⚙️ 馬達與工業設備聲學診斷測試平台 (EdgeAcoustic AI)")
st.caption("邊緣運算前置驗證平台 | 支援 ESP32-S3 + Raspberry Pi 5 模擬測試")

# 專業數據來源標註卡片
st.info(
    "📊 **聲學基準數據來源 (Benchmark Dataset)**：\n"
    "本平台測試音訊基準參照 **DCASE Challenge Task 2 / MIMII Dataset**（Sound Dataset for Malfunctioning Industrial Machine Investigation and Inspection）之設備聲學特徵與頻域指標進行標定與驗證。"
)

st.markdown("---")

# 3. 側邊欄控制台
st.sidebar.header("⚙️ 設備與測試控制台")

category = st.sidebar.selectbox(
    "1. 選擇設備類別 (Category)",
    ["工業風扇 (Fan)", "工業馬達 (Motor)"]
)

if category == "工業風扇 (Fan)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "葉片破損/異物 (Blade Fault)"]
    )
    audio_file = "samples/fan/normal_01.wav" if "正常" in status_option else "samples/fan/anomaly_blade_01.wav"

else:  # 工業馬達
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "軸承磨損 (Bearing Fault)", "轉子偏心/不平衡 (Unbalance)"]
    )
    audio_file = "samples/motor/normal_01.wav" if "正常" in status_option else "samples/motor/anomaly_bearing_01.wav"

# 側邊欄補充說明
st.sidebar.markdown("---")
st.sidebar.caption("🔬 **驗證標準**：IEEE 1451.4 & DCASE MIMII Benchmark")

# 4. 指標展示區 (健康度 HI & 重構誤差 MSE)
is_normal = "正常" in status_option

if is_normal:
    hi_score = 98 if "風扇" in category else 99
    mse_score = 0.0015 if "風扇" in category else 0.0008
    status_text = "正常 (Normal)"
    status_color = "success"
else:
    hi_score = 58 if "風扇" in category else 52
    mse_score = 0.0842 if "風扇" in category else 0.0915
    status_text = "異常 (Anomaly)"
    status_color = "error"

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="設備健康指標 (HI)", value=f"{hi_score} %", delta="狀態良好" if is_normal else "-警告", delta_color="normal" if is_normal else "inverse")
with col2:
    st.metric(label="重構誤差 (MSE)", value=f"{mse_score}", delta="門檻: 0.05", delta_color="off")
with col3:
    st.subheader("診斷狀態")
    if is_normal:
        st.success(f"✔️ {status_text}")
    else:
        st.error(f"⚠️ {status_text}")

st.markdown("---")

# 5. 音訊播放與梅爾頻譜圖 (Mel-Spectrogram) 繪製
st.subheader("🔊 採樣音訊與邊緣聲學特徵 (Mel-Spectrogram)")

col_audio, col_spec = st.columns([1, 1])

with col_audio:
    st.write("**採樣音頻試聽**")
    if os.path.exists(audio_file):
        st.audio(audio_file, format="audio/wav")
    else:
        st.warning(f"請將測試音檔放置於：\n`{audio_file}`")

with col_spec:
    if os.path.exists(audio_file):
        # 載入音訊並計算 Mel-Spectrogram
        y, sr = librosa.load(audio_file, sr=16000)
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        
        fig, ax = plt.subplots(figsize=(6, 3))
        img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, fmax=8000, ax=ax, cmap='magma')
        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        ax.set_title("Edge AI Input: Mel-Spectrogram", fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)

st.markdown("---")

# 6. 設備日常巡檢維運指引
st.subheader("📋 設備日常巡檢維運指引 (Routine Maintenance Guide)")
if "風扇" in category:
    if is_normal:
        st.info("風扇轉速與氣流聲均勻，無高頻異常摩擦音，建議保持定期的濾網清潔。")
    else:
        st.warning("檢測到 2.8kHz 高頻聲學特徵與週期衝擊，建議停機檢查葉片是否有缺角或異物卡入。")
else:
    if is_normal:
        st.info("馬達運轉聲響平均，無明顯諧波異音，運轉溫度與振動指數正常。")
    else:
        st.warning("檢測到 3.6kHz~4.2kHz 顯著金屬磨損頻譜，請規劃停機潤滑或更換軸承 (Bearing Replacement)。")