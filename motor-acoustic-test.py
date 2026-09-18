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
        [
            "正常 (Normal)", 
            "輕微不平衡/積塵 (Warning)", 
            "葉片嚴重破損/異物 (Blade Fault)"
        ]
    )
    if "正常" in status_option:
        audio_file = "samples/fan/normal_01.wav"
    else:
        audio_file = "samples/fan/anomaly_blade_01.wav"

else:  # 工業馬達
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        [
            "正常 (Normal)", 
            "輕微轉子偏心 (Warning)", 
            "嚴重軸承磨損 (Bearing Fault)"
        ]
    )
    if "正常" in status_option:
        audio_file = "samples/motor/normal_01.wav"
    else:
        audio_file = "samples/motor/anomaly_bearing_01.wav"

st.sidebar.markdown("---")
st.sidebar.caption("🔬 **驗證標準**：IEEE 1451.4 & DCASE MIMII Benchmark")

# 4. 判斷三級告警狀態 (綠 Normal / 黃 Warning / 紅 Fault)
if "正常" in status_option:
    alert_level = "GREEN"  # 正常
    hi_score = 98 if "風扇" in category else 99
    mse_score = 0.0015 if "風扇" in category else 0.0008
    status_text = "正常 (Normal)"
    history_mse = [0.0012, 0.0014, 0.0011, 0.0015, 0.0013, 0.0016, mse_score]

elif "Warning" in status_option:
    alert_level = "YELLOW" # 預警/警告
    hi_score = 59
    mse_score = 0.0582
    status_text = "警告/預警 (Warning)"
    history_mse = [0.0015, 0.0021, 0.0085, 0.0241, 0.0380, 0.0490, mse_score]

else:
    alert_level = "RED"    # 嚴重故障
    hi_score = 42 if "風扇" in category else 35
    mse_score = 0.0842 if "風扇" in category else 0.0915
    status_text = "嚴重故障 (Fault/Danger)"
    history_mse = [0.0015, 0.0021, 0.0085, 0.0241, 0.0512, 0.0720, mse_score]

# 5. 指標與音訊播放區 (頂部 4 欄併排)
col1, col2, col3, col4 = st.columns([1, 1, 1, 1.3])

with col1:
    st.caption("設備健康指標 (HI)")
    st.markdown(f"<h1 style='margin:0; padding:0; font-size: 2.2rem;'>{hi_score} %</h1>", unsafe_allow_html=True)
    
    if alert_level == "GREEN":
        st.markdown("<span style='color:#15803d; background-color:#dcfce7; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:0.85rem;'>↑ 良好</span>", unsafe_allow_html=True)
    elif alert_level == "YELLOW":
        st.markdown("<span style='color:#b45309; background-color:#fef3c7; border: 1px solid #fde68a; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:0.85rem;'>⚠️ 警告</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span style='color:#b91c1c; background-color:#fee2e2; border: 1px solid #fca5a5; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:0.85rem;'>❌ 故障</span>", unsafe_allow_html=True)

with col2:
    st.metric(label="重構誤差 (MSE)", value=f"{mse_score}", delta="門檻: 0.05", delta_color="off")

with col3:
    st.subheader("診斷狀態")
    if alert_level == "GREEN":
        st.success(f"✔️ {status_text}")
    elif alert_level == "YELLOW":
        st.warning(f"⚠️ {status_text}")
    else:
        st.error(f"🚨 {status_text}")

with col4:
    st.subheader("🔊 音頻試聽")
    if os.path.exists(audio_file):
        st.audio(audio_file, format="audio/wav")
    else:
        st.warning("無音訊檔")

st.markdown("---")

# 6. 設備日常巡檢維運指引 (同步採用相對應顏色與層級)
st.subheader("📋 設備日常巡檢維運指引 (Routine Maintenance Guide)")

if "風扇" in category:
    if alert_level == "GREEN":
        st.info(
            "✅ **運轉狀態：優良 (Normal)**\n\n"
            "- **特徵**：氣流聲均勻，未偵測到高頻摩擦與週期衝擊音。\n"
            "- **日常維護建議**：每 30 天進行進出風口濾網粉塵清潔，檢查固定螺絲是否鬆動。"
        )
    elif alert_level == "YELLOW":
        st.warning(
            "⚠️ **預警診斷：風扇輕微不平衡 / 扇葉積塵 (Warning)**\n\n"
            "**1. 聲學診斷結果**：在低頻段出現微幅諧波能量抬升，MSE 誤差輕微超出門檻 (0.0582)，健康指標 HI 降至 59%。\n\n"
            "**2. 即時處置 SOP**：\n"
            "- **步驟一**：安排下班時間或定期維護日進行風扇外觀檢查。\n"
            "- **步驟二**：清理扇葉表面附著之灰塵油脂，確認是否因積塵造成質量分佈不均。\n"
            "- **步驟三**：檢查外殼防護網是否產生共振異音。\n\n"
            "**3. 預防維護建議**：持續觀察下期 MSE 數據變化，暫無需急迫停機。"
        )
    else: # RED
        st.error(
            "🚨 **嚴重告警：風扇葉片嚴重破損 / 異物卡入 (Blade Fault)**\n\n"
            "**1. 聲學診斷結果**：在 2.8kHz 頻段出現強烈高頻噪聲與週期衝擊波，MSE 誤差高度異常 (0.0842)，健康指標 HI 降至 42%。\n\n"
            "**2. 即時處置 SOP**：\n"
            "- **步驟一**：請即刻安排停機檢查，切斷風扇主電源並掛上警示標籤。\n"
            "- **步驟二**：目視檢查風扇葉片是否出現缺角、裂痕，或內部有異物卡阻。\n"
            "- **步驟三**：使用扭力板手緊固風扇軸心與葉輪組合之螺帽。\n\n"
            "**3. 預防維護建議**：更換受損扇葉，避免長期運轉造成馬達軸心彎曲。"
        )
else:  # 馬達
    if alert_level == "GREEN":
        st.info(
            "✅ **運轉狀態：優良 (Normal)**\n\n"
            "- **特徵**：基本運轉頻率 (60Hz / 120Hz) 穩定，無諧波異音。\n"
            "- **日常維護建議**：按季度補充高溫潤滑油脂，並確認外殼散熱風道暢通。"
        )
    elif alert_level == "YELLOW":
        st.warning(
            "⚠️ **預警診斷：馬達轉子輕微偏心 / 動不平衡 (Warning)**\n\n"
            "**1. 聲學診斷結果**：60Hz 轉速基頻能量略微升高，MSE 誤差進入警戒範圍 (0.0582)，健康指標 HI 降至 59%。\n\n"
            "**2. 即時處置 SOP**：\n"
            "- **步驟一**：檢查馬達底座螺絲 (Foot Bolts) 是否有些許鬆動。\n"
            "- **步驟二**：使用雷射對中儀檢查馬達與負載軸心對中狀態。\n"
            "- **步驟三**：紀錄當前振動與聲學數值，納入每週追蹤清單。\n\n"
            "**3. 預防維護建議**：規劃於下次例行停機時重新進行動平衡校正 (Dynamic Balancing)。"
        )
    else: # RED
        st.error(
            "🚨 **嚴重告警：馬達軸承嚴重磨損 (Bearing Fault / Danger)**\n\n"
            "**1. 聲學診斷結果**：3.6kHz ~ 4.2kHz 高頻段湧現強烈金屬磨損聲，MSE 重構誤差嚴重超標 (0.0915)，健康指標 HI 掉至 35%。\n\n"
            "**2. 即時處置 SOP**：\n"
            "- **步驟一**：發布 Level 1 緊迫告警，建議 12 小時內進行預防性停機。\n"
            "- **步驟二**：配合加速度計檢測滾道 (BPFO/BPFI) 損傷狀況。\n"
            "- **步驟三**：補充油脂若無效，應立即備料並安排更換新軸承。\n\n"
            "**3. 預防維護建議**：更換軸承後需重新校正軸心對中度與預緊力，避免二次損壞。"
        )

st.markdown("---")

# 7. 專業圖表分頁 (Tabs)
tab1, tab2, tab3 = st.tabs([
    "📊 邊緣聲學梅爾頻譜 (Mel-Spectrogram)",
    "📈 歷史趨勢與統計分析 (Trend & Stats)",
    "⚡ 時域訊號與 FFT 頻譜 (Waveform & FFT)"
])

# Tab 1: 梅爾頻譜圖
with tab1:
    st.markdown("#### 邊緣 AI 聲學特徵分析 (Edge AI Acoustic Feature)")
    st.caption("💡 **圖表指引**：橫軸 (X-axis) 表示時間 [秒]，縱軸 (Y-axis) 表示梅爾對數頻率 [Hz]，顏色深淺表示能量強度 (dB)。")
    
    if os.path.exists(audio_file):
        y, sr = librosa.load(audio_file, sr=16000)
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, fmax=8000, ax=ax, cmap='magma')
        
        ax.set_xlabel("Time (s)", fontsize=10)
        ax.set_ylabel("Frequency (Hz)", fontsize=10)
        cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.set_label("Power (dB)", fontsize=9)
        
        ax.set_title("Edge AI Feature: Mel-Spectrogram (16kHz Sample)", fontsize=11)
        plt.tight_layout()
        st.pyplot(fig)

# Tab 2: 歷史趨勢與數據表
with tab2:
    st.markdown("#### 近 7 次巡檢歷史重構誤差 (MSE Trend)")
    chart_data = pd.DataFrame({
        "Batch": [f"T-{6-i}" for i in range(7)],
        "MSE Loss": history_mse
    })
    st.line_chart(chart_data.set_index("Batch"))
    
    st.markdown("#### 歷史巡檢詳細紀錄表 (Inspection Records)")
    df_history = pd.DataFrame({
        "巡檢時間": ["2026-09-12 08:00", "2026-09-13 08:00", "2026-09-14 08:00", "2026-09-15 08:00", "2026-09-16 08:00", "2026-09-17 08:00", "2026-09-18 08:00"],
        "設備狀態": ["正常", "正常", "正常", "正常" if alert_level=="GREEN" else "預警", "正常" if alert_level=="GREEN" else status_text, "正常" if alert_level=="GREEN" else status_text, status_text],
        "MSE 重構誤差": history_mse,
        "健康度 (HI)": [99, 98, 99, 97 if alert_level=="GREEN" else 82, 98 if alert_level=="GREEN" else 68, 98 if alert_level=="GREEN" else 61, f"{hi_score}%"]
    })
    st.dataframe(df_history, use_container_width=True)

# Tab 3: 時域波形與 FFT 頻譜
with tab3:
    st.markdown("#### 時域波形 (Waveform) 與 快速傅立葉變換 (FFT Spectrum)")
    
    st.markdown(
        "- **上方時域圖 (Time Domain)**：`X 軸: 時間 Time (s)` | `Y 軸: 振幅 Amplitude`\n"
        "- **下方頻域圖 (FFT Spectrum)**：`X 軸: 頻率 Frequency (Hz)` | `Y 軸: 聲訊強度 Magnitude`"
    )
    
    if os.path.exists(audio_file):
        y, sr = librosa.load(audio_file, sr=16000)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5))
        
        # 上圖：時域波形
        time_axis = np.linspace(0, len(y) / sr, len(y))
        ax1.plot(time_axis, y, color='#1f77b4', alpha=0.8)
        ax1.set_title("Time-Domain Signal (Waveform)", fontsize=10)
        ax1.set_xlabel("Time (s)", fontsize=9)
        ax1.set_ylabel("Amplitude", fontsize=9)
        ax1.grid(True, linestyle='--', alpha=0.5)
        
        # 下圖：FFT 頻譜
        n = len(y)
        fft_vals = np.abs(np.fft.rfft(y))
        freq_axis = np.fft.rfftfreq(n, 1/sr)
        ax2.plot(freq_axis, fft_vals, color='#d62728', alpha=0.8)
        ax2.set_title("Frequency Domain Spectrum (FFT Analysis)", fontsize=10)
        ax2.set_xlabel("Frequency (Hz)", fontsize=9)
        ax2.set_ylabel("Magnitude", fontsize=9)
        ax2.grid(True, linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        st.pyplot(fig)