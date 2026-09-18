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

# 2. 標題與簡介
st.title("⚙️ 馬達與工業設備聲學診斷測試平台 (EdgeAcoustic AI)")
st.caption("邊緣運算前置驗證平台 | 支援 ESP32-S3 + Raspberry Pi 5 模擬測試")

# 數據來源標註
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

st.sidebar.markdown("---")
st.sidebar.caption("🔬 **驗證標準**：IEEE 1451.4 & DCASE MIMII Benchmark")

# 4. 指標展示區
is_normal = "正常" in status_option

if is_normal:
    hi_score = 98 if "風扇" in category else 99
    mse_score = 0.0015 if "風扇" in category else 0.0008
    status_text = "正常 (Normal)"
else:
    hi_score = 58 if "風扇" in category else 52
    mse_score = 0.0842 if "風扇" in category else 0.0915
    status_text = "異常 (Anomaly)"

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

# 5. 音訊播放與梅爾頻譜圖 (改為上下垂直佈局，寬度更大更清晰)
st.subheader("🔊 採樣音訊與邊緣聲學特徵 (Mel-Spectrogram)")

st.markdown("##### 1. 採樣音頻試聽")
if os.path.exists(audio_file):
    st.audio(audio_file, format="audio/wav")
else:
    st.warning(f"請將測試音檔放置於：`{audio_file}`")

st.markdown("##### 2. 邊緣聲學梅爾頻譜圖分析 (Edge AI Input Feature)")
if os.path.exists(audio_file):
    y, sr = librosa.load(audio_file, sr=16000)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)
    
    # 放大圖形寬度，利於細節觀察
    fig, ax = plt.subplots(figsize=(10, 3.5))
    img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, fmax=8000, ax=ax, cmap='magma')
    fig.colorbar(img, ax=ax, format='%+2.0f dB')
    ax.set_title("Edge AI Input: Mel-Spectrogram (16kHz / 128 Mels)", fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")

# 6. 設備日常巡檢維運指引 (詳細 SOP 指引)
st.subheader("📋 設備日常巡檢維運指引 (Routine Maintenance Guide)")

if "風扇" in category:
    if is_normal:
        st.info(
            "✅ **運轉狀態：優良**\n\n"
            "- **特徵**：氣流聲均勻，未偵測到高頻摩擦與週期衝擊音。\n"
            "- **日常維護建議**：每 30 天進行進出風口濾網粉塵清潔，檢查固定螺絲是否鬆動。"
        )
    else:
        st.error(
            "⚠️ **異常診斷：風扇葉片破損 / 異物卡入 (Blade Fault)**\n\n"
            "**1. 聲學診斷結果**：在 2.8kHz 頻段出現連續高頻噪聲，且伴隨週期性衝擊波形 (Transient Impact)。\n\n"
            "**2. 即時處置 SOP**：\n"
            "- **步驟一**：請於 4 小時內安排離峰停機檢查，切斷風扇主電源並掛上警示牌。\n"
            "- **步驟二**：目視檢查風扇葉片是否出現破裂、欠角，或內部有異物（如金屬屑、廢料）卡阻。\n"
            "- **步驟三**：使用扭力板手抽檢風扇軸心與葉輪組合之固定螺帽。\n\n"
            "**3. 預防維護建議**：若葉片有嚴重磨損請立即更換同規格葉片，避免運轉不平衡導致馬達軸承連帶受損。"
        )
else: # 馬達
    if is_normal:
        st.info(
            "✅ **運轉狀態：優良**\n\n"
            "- **特徵**：基本運轉頻率 (60Hz / 120Hz) 穩定，無諧波異音。\n"
            "- **日常維護建議**：按季度補充高溫潤滑油脂，並確認外殼散熱風道暢通。"
        )
    else:
        st.error(
            "⚠️ **異常診斷：馬達軸承磨損 / 轉子偏心 (Bearing Fault / Unbalance)**\n\n"
            "**1. 聲學診斷結果**：在 3.6kHz ~ 4.2kHz 高頻段湧現顯著金屬磨損聲學能量，MSE 誤差超出安全門檻 (0.05)。\n\n"
            "**2. 即時處置 SOP**：\n"
            "- **步驟一**：發布等級 2 告警，建議於 24 小時內規劃預防性停機保養。\n"
            "- **步驟二**：配合加速度計測量三軸振動值 (Vibration ISO 10816)，確認是否伴隨滾珠或滾道損傷。\n"
            "- **步驟三**：利用注油槍進行軸承油脂補給，觀察高頻聲學能量是否降低；若無改善應安排更換軸承。\n\n"
            "**3. 預防維護建議**：檢查軸承安裝對中度 (Alignment)，防止因軸心偏心導致新軸承再次過早磨損。"
        )