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
    "本平台測試音訊基準參照 **DCASE Challenge Task 2 / MIMII Dataset** (Fan, Motor, Pump, Valve, Slide Rail, Gearbox) 之設備聲學特徵與頻域指標進行標定與驗證。"
)

st.markdown("---")

# 3. 側邊欄控制台 - 擴充至 6 大工業設備類型
st.sidebar.header("⚙️ 設備與測試控制台")

category = st.sidebar.selectbox(
    "1. 選擇設備類別 (Category)",
    [
        "工業風扇 (Fan)", 
        "工業馬達 (Motor)", 
        "工業水泵 (Pump)", 
        "電磁閥門 (Valve)", 
        "線性滑軌 (Slide Rail)", 
        "工業齒輪箱 (Gearbox)"
    ]
)

if category == "工業風扇 (Fan)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "輕微不平衡/積塵 (Warning)", "葉片嚴重破損/異物 (Blade Fault)"]
    )
    if "正常" in status_option:
        audio_file = "samples/fan/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/fan/warning_01.wav" if os.path.exists("samples/fan/warning_01.wav") else "samples/fan/anomaly_blade_01.wav"
    else:
        audio_file = "samples/fan/anomaly_blade_01.wav"

elif category == "工業馬達 (Motor)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "輕微轉子偏心 (Warning)", "嚴重軸承磨損 (Bearing Fault)"]
    )
    if "正常" in status_option:
        audio_file = "samples/motor/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/motor/warning_01.wav" if os.path.exists("samples/motor/warning_01.wav") else "samples/motor/anomaly_bearing_01.wav"
    else:
        audio_file = "samples/motor/anomaly_bearing_01.wav"

elif category == "工業水泵 (Pump)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "流體輕微微氣蝕 (Warning)", "軸封嚴重磨損/空轉 (Pump Cavitation)"]
    )
    if "正常" in status_option:
        audio_file = "samples/pump/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/pump/warning_01.wav"
    else:
        audio_file = "samples/pump/anomaly_cavitation_01.wav"

elif category == "電磁閥門 (Valve)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "閥體輕微結垢/滯遲 (Warning)", "氣體/液體嚴重洩漏 (Valve Leakage)"]
    )
    if "正常" in status_option:
        audio_file = "samples/valve/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/valve/warning_01.wav"
    else:
        audio_file = "samples/valve/anomaly_leak_01.wav"

elif category == "線性滑軌 (Slide Rail)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "潤滑油脂不足 (Warning)", "軌道金屬剝落/刮傷 (Rail Scratch)"]
    )
    if "正常" in status_option:
        audio_file = "samples/slider/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/slider/warning_01.wav"
    else:
        audio_file = "samples/slider/anomaly_scratch_01.wav"

else:  # 工業齒輪箱 (Gearbox)
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "齒面輕微點蝕 (Warning)", "輪齒嚴重點蝕/缺角 (Gear Damage)"]
    )
    if "正常" in status_option:
        audio_file = "samples/gearbox/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/gearbox/warning_01.wav"
    else:
        audio_file = "samples/gearbox/anomaly_gear_01.wav"

st.sidebar.markdown("---")
st.sidebar.caption("🛡️ **驗證標準** : IEEE 1451.4 & DCASE MIMII Benchmark")

# 4. 判斷三級告警狀態 (綠 Normal / 黃 Warning / 紅 Fault)
if "正常" in status_option:
    alert_level = "GREEN"
    hi_score = 98
    mse_score = 0.0015
    status_text = "正常 (Normal)"
    history_mse = [0.0012, 0.0014, 0.0011, 0.0015, 0.0013, 0.0016, mse_score]

elif "Warning" in status_option:
    alert_level = "YELLOW"
    hi_score = 59
    mse_score = 0.0582
    status_text = "警告/預警 (Warning)"
    history_mse = [0.0015, 0.0021, 0.0085, 0.0241, 0.0380, 0.0490, mse_score]

else:
    alert_level = "RED"
    hi_score = 38
    mse_score = 0.0915
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
        st.warning("無音訊檔 (使用模擬數據)")

st.markdown("---")

# 6. 設備日常巡檢維運指引 (全設備動態適配)
st.subheader("📋 設備日常巡檢維運指引 (Routine Maintenance Guide)")

if alert_level == "GREEN":
    st.info(
        f"✅ **{category} 運轉狀態：優良 (Normal)**\n\n"
        "- **聲學特徵**：音訊能量分佈均勻，並無高頻異常衝擊或頻率偏移。\n"
        "- **日常維護建議**：依據標準 SOP 進行月度巡檢，保持設備表面清潔與良好散熱環境。"
    )

elif alert_level == "YELLOW":
    guide_details = {
        "工業風扇 (Fan)": ("風扇輕微不平衡 / 積塵", "低頻段出現微幅諧波能量抬升", "1. 安排維護日清理扇葉積塵。\n2. 檢查外殼防護網是否產生共振。\n3. 紀錄運轉異音持續觀察。"),
        "工業馬達 (Motor)": ("馬達轉子輕微偏心", "60Hz 轉速基頻能量略微升高", "1. 檢查底座螺絲是否鬆動。\n2. 使用雷射對中儀檢查軸心對中。\n3. 納入每週重點觀察清單。"),
        "工業水泵 (Pump)": ("流體輕微微氣蝕 (Warning)", "中高頻水流噪聲出現不規則脈衝", "1. 檢查入口管路壓力與閥門開度。\n2. 確認是否有流體氣泡混入現象。\n3. 調整進水流量避免持續微氣蝕。"),
        "電磁閥門 (Valve)": ("閥體輕微結垢 / 切換滯遲", "閥門開啟/關閉聲學時序偏移", "1. 檢查閥體控制電壓與氣源壓力。\n2. 檢視內部是否有結晶或沉積物。\n3. 規劃於例行保養時清洗閥芯。"),
        "線性滑軌 (Slide Rail)": ("滑塊潤滑油脂不足", "滑塊移動時出現輕微乾摩擦高頻聲", "1. 使用注油槍補充指定規格潤滑膏。\n2. 手動滑動確認摩擦阻力是否降低。\n3. 清除軌道兩側多餘粉塵。"),
        "工業齒輪箱 (Gearbox)": ("齒面輕微點蝕", "齒輪囓合頻率 (GMF) 兩側出現微弱邊頻帶", "1. 抽樣檢測齒輪箱潤滑油品質與鐵粉含量。\n2. 觀察高負載運轉時之溫度變化。\n3. 記錄聲學數據並維持正常保養。")
    }
    title_str, diag_str, sop_str = guide_details.get(category, ("設備輕微異常", "特徵值微幅上升", "1. 加強巡檢紀錄。"))
    st.warning(
        f"⚠️ **預警診斷：{title_str}**\n\n"
        f"**1. 聲學診斷結果**：{diag_str}，MSE 誤差進入警戒範圍 ({mse_score})，健康指標 HI 降至 {hi_score}%。\n\n"
        f"**2. 即時處置 SOP**：\n{sop_str}\n\n"
        f"**3. 預防維護建議**：安排計畫性停機保養，避免小瑕疵擴大為重大故障。"
    )

else: # RED
    guide_details_red = {
        "工業風扇 (Fan)": ("風扇葉片嚴重破損 / 異物卡入", "2.8kHz 頻段出現強烈高頻噪聲與週期衝擊", "1. 即刻安排停機並切斷主電源。\n2. 目視檢查葉片是否缺角或有異物。\n3. 更換受損扇葉防止軸心彎曲。"),
        "工業馬達 (Motor)": ("馬達軸承嚴重磨損 (Bearing Fault)", "3.6kHz~4.2kHz 湧現強烈金屬磨損衝擊波", "1. 發布 Level 1 緊迫告警，12 小時內停機。\n2. 配合加速度計確認軸承損傷點。\n3. 備料並安排更換新軸承。"),
        "工業水泵 (Pump)": ("水泵嚴重氣蝕 / 軸封破損", "出現強烈氣蝕空化爆裂聲與振動流壓異常", "1. 立即停止水泵運轉，防止泵體葉輪毀損。\n2. 檢查進水管線是否堵塞或嚴重負壓。\n3. 檢視軸封處是否發生嚴重漏液。"),
        "電磁閥門 (Valve)": ("閥門嚴重洩漏 / 內部結構損壞", "持續性高頻流體噴射聲 (Air Leakage)", "1. 關閉隔離閥並進行系統降壓。\n2. 使用氣體洩漏偵測器確定洩漏點。\n3. 更換閥芯密封圈或整體閥體。"),
        "線性滑軌 (Slide Rail)": ("軌道金屬剝落 / 滑軌刮傷", "滑塊移動時發出劇烈撞擊與金屬刮削聲", "1. 暫停自動化機構運轉。\n2. 檢查軌道表面是否有深層刮痕與鋼珠破裂。\n3. 更換受損滑塊與導軌。"),
        "工業齒輪箱 (Gearbox)": ("齒輪嚴重斷齒 / 斷裂損壞", "齒輪囓合週期產生劇烈衝擊峰值 (Impact Peak)", "1. 切斷馬達驅動電源，停止傳動系統。\n2. 排空齒輪油並檢查底部是否有金屬碎片。\n3. 打開檢視孔，評估齒輪更換或大修。")
    }
    title_str, diag_str, sop_str = guide_details_red.get(category, ("設備嚴重故障", "特徵值高度異常", "1. 立即停機檢修。"))
    st.error(
        f"🚨 **嚴重告警：{title_str}**\n\n"
        f"**1. 聲學診斷結果**：{diag_str}，MSE 重構誤差嚴重超標 ({mse_score})，健康指標 HI 掉至 {hi_score}%。\n\n"
        f"**2. 即時處置 SOP**：\n{sop_str}\n\n"
        f"**3. 預防維護建議**：完成檢修與零件更換後，重新進行全頻段聲學基準校正。"
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
    st.markdown("#### 邊緣 AI 聲學特徵分析 (Edge AI Feature)")
    st.caption("💡 **圖表指引**：橫軸 (X-axis) 表示時間 [秒]，縱軸 (Y-axis) 表示梅爾對數頻率 [Hz]，顏色深淺表示能量強度 (dB)。")
    
    if os.path.exists(audio_file):
        y, sr = librosa.load(audio_file, sr=16000)
    else:
        # 當音訊檔不存在時，自動生成高擬真模擬聲學波形
        sr = 16000
        duration = 2.0
        t = np.linspace(0, duration, int(sr * duration))
        if alert_level == "GREEN":
            y = 0.1 * np.sin(2 * np.pi * 60 * t) + 0.02 * np.random.randn(len(t))
        elif alert_level == "YELLOW":
            y = 0.2 * np.sin(2 * np.pi * 60 * t) + 0.1 * np.sin(2 * np.pi * 300 * t) + 0.05 * np.random.randn(len(t))
        else:
            y = 0.3 * np.sin(2 * np.pi * 60 * t) + 0.3 * np.sin(2 * np.pi * 3800 * t) + 0.15 * np.random.randn(len(t))

    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, fmax=8000, ax=ax, cmap='magma')
    
    ax.set_xlabel("Time (s)", fontsize=10)
    ax.set_ylabel("Frequency (Hz)", fontsize=10)
    cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
    cbar.set_label("Power (dB)", fontsize=9)
    ax.set_title(f"Edge AI Feature: Mel-Spectrogram ({category})", fontsize=11)
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
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5))
    
    time_axis = np.linspace(0, len(y) / sr, len(y))
    ax1.plot(time_axis, y, color='#1f77b4', alpha=0.8)
    ax1.set_title("Time-Domain Signal (Waveform)", fontsize=10)
    ax1.set_xlabel("Time (s)", fontsize=9)
    ax1.set_ylabel("Amplitude", fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.5)
    
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