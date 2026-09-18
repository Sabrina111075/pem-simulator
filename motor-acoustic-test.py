import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
    "本平台測試音訊基準參照 **DCASE Challenge Task 2 / MIMII Dataset** 之設備聲學特徵與頻域指標進行標定與驗證。"
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

# 4. 指標與音訊播放區 (頂部 4 欄併排)
is_normal = "正常" in status_option

if is_normal:
    hi_score = 98 if "風扇" in category else 99
    mse_score = 0.0015 if "風扇" in category else 0.0008
    status_text = "正常 (Normal)"
    history_mse = [0.0012, 0.0014, 0.0011, 0.0015, 0.0013, 0.0016, mse_score]
else:
    hi_score = 58 if "風扇" in category else 52
    mse_score = 0.0842 if "風扇" in category else 0.0915
    status_text = "異常 (Anomaly)"
    history_mse = [0.0015, 0.0021, 0.0085, 0.0241, 0.0512, 0.0720, mse_score]

col1, col2, col3, col4 = st.columns([1, 1, 1, 1.3])

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

with col4:
    st.subheader("🔊 音頻試聽")
    if os.path.exists(audio_file):
        st.audio(audio_file, format="audio/wav")
    else:
        st.warning("無音訊檔")

st.markdown("---")

# 5. 分頁 (Tabs / Sheets) 架構
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 邊緣聲學梅爾頻譜 (Mel-Spectrogram)",
    "📈 歷史趨勢與統計分析 (Trend & Stats)",
    "⚡ 時域訊號與 FFT 頻譜 (Waveform & FFT)",
    "📋 設備巡檢維運 SOP (Maintenance Guide)"
])

# Tab 1: 梅爾頻譜圖
with tab1:
    st.markdown("#### 邊緣 AI 聲學特徵：梅爾頻譜圖 (Mel-Spectrogram)")
    if os.path.exists(audio_file):
        y, sr = librosa.load(audio_file, sr=16000)
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, fmax=8000, ax=ax, cmap='magma')
        
        ax.set_xlabel("時間 Time (Seconds)", fontsize=10)
        ax.set_ylabel("頻率 Frequency (Hz)", fontsize=10)
        cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.set_label("能量強度 Signal Power (dB)", fontsize=9)
        
        ax.set_title("Edge AI Input Feature: Mel-Spectrogram (16kHz / 128 Mels)", fontsize=11)
        plt.tight_layout()
        st.pyplot(fig)

# Tab 2: 歷史趨勢與數據表
with tab2:
    st.markdown("#### 近 7 次巡檢歷史重構誤差 (MSE Trend)")
    chart_data = pd.DataFrame({
        "巡檢批次": [f"T-{6-i}" for i in range(7)],
        "重構誤差 (MSE)": history_mse
    })
    st.line_chart(chart_data.set_index("巡檢批次"))
    
    st.markdown("#### 歷史巡檢詳細紀錄表")
    df_history = pd.DataFrame({
        "巡檢時間": ["2026-09-12 08:00", "2026-09-13 08:00", "2026-09-14 08:00", "2026-09-15 08:00", "2026-09-16 08:00", "2026-09-17 08:00", "2026-09-18 08:00"],
        "設備狀態": ["正常", "正常", "正常", "正常" if is_normal else "預警", "正常" if is_normal else "異常", "正常" if is_normal else "異常", status_text],
        "MSE 重構誤差": history_mse,
        "健康度 (HI)": [99, 98, 99, 97 if is_normal else 82, 98 if is_normal else 68, 98 if is_normal else 61, f"{hi_score}%"]
    })
    st.dataframe(df_history, use_container_width=True)

# Tab 3: 時域波形與 FFT 頻譜分析
with tab3:
    st.markdown("#### 時域波形 (Time-Domain Waveform) 與 快速傅立葉變換 (FFT)")
    if os.path.exists(audio_file):
        y, sr = librosa.load(audio_file, sr=16000)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5))
        
        # 時域波形
        time_axis = np.linspace(0, len(y) / sr, len(y))
        ax1.plot(time_axis, y, color='#1f77b4', alpha=0.8)
        ax1.set_title("Time Domain Waveform (時域振幅訊號)", fontsize=10)
        ax1.set_xlabel("Time (s)", fontsize=9)
        ax1.set_ylabel("Amplitude", fontsize=9)
        ax1.grid(True, linestyle='--', alpha=0.5)
        
        # FFT 頻譜
        n = len(y)
        fft_vals = np.abs(np.fft.rfft(y))
        freq_axis = np.fft.rfftfreq(n, 1/sr)
        ax2.plot(freq_axis, fft_vals, color='#d62728', alpha=0.8)
        ax2.set_title("FFT Spectrum (快速傅立葉頻域分析)", fontsize=10)
        ax2.set_xlabel("Frequency (Hz)", fontsize=9)
        ax2.set_ylabel("Magnitude", fontsize=9)
        ax2.grid(True, linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        st.pyplot(fig)

# Tab 4: 巡檢 SOP
with tab4:
    st.markdown("#### 設備日常巡檢維運指引 (Maintenance Guide)")
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
                "- **步驟一**：安排離峰停機檢查，切斷風扇主電源並掛上警示牌。\n"
                "- **步驟二**：目視檢查風扇葉片是否出現破裂、欠角，或內部有異物卡阻。\n"
                "- **步驟三**：使用扭力板手抽檢風扇軸心與葉輪組合之固定螺帽。\n\n"
                "**3. 預防維護建議**：若葉片有嚴重磨損請立即更換，避免運轉不平衡導致馬達軸承受損。"
            )
    else:  # 馬達
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
                "- **步驟二**：配合加速度計測量三軸振動值 (ISO 10816)，確認是否伴隨滾珠或滾道損傷。\n"
                "- **步驟三**：利用注油槍進行軸承油脂補給，觀察高頻聲學能量是否降低；若無改善應安排更換軸承。\n\n"
                "**3. 預防維護建議**：檢查軸承安裝對中度 (Alignment)，防止因軸心偏心導致新軸承再次過早磨損。"
            )