import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# 設定頁面配置
st.set_page_config(
    page_title="馬達與工業設備聲學診斷測試平台", page_icon="⚙️", layout="wide"
)

# 1. 側邊欄：功能模組切換
page = st.sidebar.selectbox(
    "📌 切換功能模組：",
    ["⚙️️ 設備與測試控制台", "🎓 OpenMAIC 聲學 AI 學院"],
)

# ==============================================================================
# 🎓 功能模組 1：OpenMAIC 聲學 AI 學院 (三欄沉浸式互動教學)
# ==============================================================================
if page == "🎓 OpenMAIC 聲學 AI 學院":
  col_left, col_center, col_right = st.columns([1.2, 3, 1.8], gap="small")

  # --- 左欄：課程章節 ---
  with col_left:
    st.subheader("📚 課程導航")
    course_list = [
        "課程 1：梅爾頻譜圖 (Mel-Spectrogram) 基礎原理",
        "課程 2：聲學訊號處理與 FFT/STFT 頻譜分析",
        "課程 3：馬達與風扇聲學故障診斷",
        "課程 4：Edge AI 邊緣運算與輕量化模型部署",
        "課程 5：工業物聯網 (IIoT) 設備預測性維護 SOP",
    ]
    selected_course = st.radio("請選擇研討主題：", course_list, index=0)
    st.divider()
    st.caption("目前學習進度：1/5")

  # --- 中欄：主展示與模擬實驗台 ---
  with col_center:
    st.caption(f"目前研討場景：{selected_course}")
    st.title(f"🎓 {selected_course}")

    with st.expander(
        "📌 點擊展開/收合：本課精華重點總結 (Course Summary)", expanded=True
    ):
      st.markdown("""
            * **核心概念**：將時域聲學訊號轉為 2D 頻譜圖，並將 Y 軸頻率轉為符合人類聽覺特性的 Mel Scale。
            * **工業診斷應用**：捕捉馬達與軸承的高頻衝擊特徵，實現早期微弱故障特徵識別。
            """)

    with st.container(border=True):
      st.markdown("#### 🔬 聲學頻譜動態模擬視窗")
      sim_c1, sim_c2 = st.columns([1, 2])
      with sim_c1:
        st.slider("採樣率 (Hz)", 8000, 44100, 16000)
        st.slider("FFT 窗格大小 (N_FFT)", 256, 2048, 512)
        st.button("🚀 重新萃取特徵", use_container_width=True)
      with sim_c2:
        st.info("📈 [動態頻譜可視化區] STFT / Mel-Spectrogram 特徵圖譜展演")

    with st.container(border=True):
      st.markdown(
          "👩‍🏫 **Prof. Acoustic (聲學總導師)**："
          "歡迎來到本單元！請觀察右側對話區，多智體團隊已針對此主題準備好圓桌研討內容。"
      )

  # --- 右欄：OpenMAIC 圓桌研討 ---
  with col_right:
    tab_chat, tab_notes = st.tabs(["💬 智體圓桌研討", "📖 隨堂筆記"])

    with tab_chat:
      st.subheader("💬 OpenMAIC 多智體互動研討")
      user_q = st.text_input(
          "輸入您的研討疑問：",
          value=f"什麼是{selected_course.split('：')[-1]}？",
      )

      if user_q:
        st.caption("💬 4 人研討小組正在發表立場與觀點：")
        res_data = {
            "prof_reply": f"針對【{selected_course}】的核心原理，主要依賴時頻分析將一維聲壓轉為二維特徵圖，為物理場建模提供扎實基礎。",
            "beth_reply": f"在硬體落地方面，我們採用 INT8 量化與輕量化架構，能大幅降低記憶體佔用，順利部署於 STM32/ESP32 等邊緣晶片。",
            "alex_reply": f"從數據科學角度，我們針對 MIMII/DCASE 資料集提取高階特徵，能在高背景雜訊下維持 95% 以上偵測率。",
            "cathy_reply": f"從商業 ROI 考量，結合預測性維護 (PdM) 能有效降低非預期停機風險，提昇設備 OEE 並降低運維成本。",
        }
        agents = [
            (
                "👨‍🏫 [Prof. Acoustic] 聲學總導師",
                res_data["prof_reply"],
                "#eef2ff",
            ),
            (
                "👩‍💻 [Engineer Beth] AI 邊緣部署工程師",
                res_data["beth_reply"],
                "#f0fdf4",
            ),
            (
                "👨‍🔬 [Data Scientist Alex] 數據科學專家",
                res_data["alex_reply"],
                "#fff7ed",
            ),
            (
                "👩‍💼 [Product Manager Cathy] 工業產品經理",
                res_data["cathy_reply"],
                "#fdf2f8",
            ),
        ]
        for name, reply, bg_color in agents:
          st.markdown(
              f"""
                <div style="background-color: {bg_color}; padding: 10px 14px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #e2e8f0;">
                    <b style="color: #1e293b;">{name}</b><br/>
                    <span style="font-size: 14px; color: #334155;">{reply}</span>
                </div>
                """,
              unsafe_allow_html=True,
          )

    with tab_notes:
      st.text_area(
          "隨堂重點筆記：",
          "1. 時頻分析需注意 Window Size 對時間與頻率解析度的影響。\n2...",
          height=250,
      )

# ==============================================================================
# ⚙️ 功能模組 2：設備與測試控制台 (支援 samples/ 音訊檔 + SOP 建議 + 聲學顯著區隔)
# ==============================================================================
else:
  import os
  import glob
  import matplotlib
  import matplotlib.pyplot as plt
  import numpy as np
  import streamlit as st
  from scipy.io import wavfile

  # 設定中文字體避免方塊亂碼
  plt.rcParams['font.sans-serif'] = [
      'Microsoft JhengHei',
      'DFKai-SB',
      'SimHei',
      'Arial',
  ]
  plt.rcParams['axes.unicode_minus'] = False

  st.title('⚙️ 馬達與工業設備聲學診斷測試平台 (EdgeAcoustic AI)')
  st.caption('邊緣運算前置驗證平台 | 支援 ESP32-S3 + Raspberry Pi 5 模擬測試')

  st.info(
      '📊 **聲學基準數據來源 (Benchmark Dataset)**：本平台測試音訊基準參照 DCASE Challenge Task'
      ' 2 / MIMII Dataset (Fan, Motor, Pump, Valve, Slide Rail, Gearbox)'
      ' 之設備聲學特徵與頻域指標進行標定與驗證。'
  )

  # 側邊欄控制台選項
  st.sidebar.header('⚙️ 設備與測試控制台')
  category = st.sidebar.selectbox(
      '1. 選擇設備類別 (Category)',
      [
          '工業風扇 (Fan)',
          '工業馬達 (Motor)',
          '工業水泵 (Pump)',
          '電磁閥門 (Valve)',
          '線性滑軌 (Slide Rail)',
          '工業齒輪箱 (Gearbox)',
          '風力發電機 - 齒輪箱 (Wind Turbine - Gearbox)',
          '風力發電機 - 發電機 (Wind Turbine - Generator)',
          '風力發電機 - 實測風場聲 (Wind Turbine Field Acoustics)',
          '電動車電池水冷泵浦 (EV Battery Cooling Pump)',
      ],
  )

  status_option = st.sidebar.selectbox(
      '2. 選擇測試狀態/故障型態',
      [
          '正常 (Normal)',
          '異常 - 軸承磨損 (Abnormal - Bearing Wear)',
          '異常 - 不平衡 (Abnormal - Unbalance)',
          '異常 - 異物卡阻 (Abnormal - Blockage)',
      ],
  )

  is_normal = '正常' in status_option

  # --- Top 狀態指標列 ---
  k1, k2, k3, k4 = st.columns([1, 1, 1, 1.8])

  if is_normal:
    k1.metric('設備健康指標 (HI)', '96 %', '↑ 良好')
    k2.metric('重構誤差 (MSE)', '0.0015', '↑ 門檻: 0.05')
    with k3:
      st.success('### 診斷狀態\n✅ 正常 (Normal)')
  elif '軸承磨損' in status_option:
    k1.metric('設備健康指標 (HI)', '38 %', '🚨 嚴重離線')
    k2.metric('重構誤差 (MSE)', '0.1980', '🚨 高頻衝擊超標')
    with k3:
      st.error('### 診斷狀態\n🚨 軸承磨損')
  elif '不平衡' in status_option:
    k1.metric('設備健康指標 (HI)', '52 %', '⚠️ 需進行校正')
    k2.metric('重構誤差 (MSE)', '0.1240', '⚠️ 1X轉速振幅過大')
    with k3:
      st.warning('### 診斷狀態\n⚠️ 轉子不平衡')
  else:  # 異物卡阻
    k1.metric('設備健康指標 (HI)', '25 %', '🚨 建議劃定停機')
    k2.metric('重構誤差 (MSE)', '0.2850', '🚨 紊流與異常碰撞')
    with k3:
      st.error('### 診斷狀態\n🚨 異物卡阻')

  # --- 音訊讀取與真實 samples/ 對接機制 ---
  fs = 16000
  signal = None
  audio_source_label = '數學聲學模型生成'

  # 關鍵字對應字典
  dev_kw = (
      'fan'
      if '風扇' in category
      else (
          'pump'
          if '水泵' in category or '泵浦' in category
          else (
              'gearbox'
              if '齒輪' in category
              else 'motor' if '馬達' in category else 'slider'
          )
      )
  )
  status_kw = (
      'normal'
      if is_normal
      else (
          'bearing'
          if '軸承' in status_option
          else 'unbalance' if '不平衡' in status_option else 'clog'
      )
  )

  # 搜尋 samples/ 目錄下是否有符合關鍵字的 wav/mp3 檔案
  samples_dir = 'samples'
  found_file = None
  if os.path.exists(samples_dir):
    all_files = glob.glob(os.path.join(samples_dir, '*.*'))
    for fpath in all_files:
      fname = os.path.basename(fpath).lower()
      if dev_kw in fname and status_kw in fname:
        found_file = fpath
        break
    if not found_file:
      # 退而求其次，只匹配狀態或設備
      for fpath in all_files:
        fname = os.path.basename(fpath).lower()
        if status_kw in fname:
          found_file = fpath
          break

  if found_file:
    try:
      fs_read, data_read = wavfile.read(found_file)
      fs = fs_read
      if data_read.ndim > 1:
        data_read = data_read[:, 0]
      signal = data_read.astype(np.float32)
      signal = signal / (np.max(np.abs(signal)) + 1e-6)
      audio_source_label = f'真實音檔 ({os.path.basename(found_file)})'
    except Exception as e:
      signal = None

  # 若無實體 Samples，採用高度區隔化的數學合成演算法
  if signal is None:
    duration = 2.5
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)

    # 設備基頻設定
    base_f = (
        45
        if '風扇' in category
        else (
            90
            if '水泵' in category or '泵浦' in category
            else (
                180
                if '齒輪' in category
                else 300 if '滑軌' in category else 120
            )
        )
    )

    if is_normal:
      # 正常音：純淨低頻運轉音，幾乎無白雜訊
      signal = 0.4 * np.sin(2 * np.pi * base_f * t) + 0.15 * np.sin(
          2 * np.pi * base_f * 2 * t
      )
      signal += 0.01 * np.random.normal(size=t.shape)
    else:
      # 異常音：依據型態拉開極大聲學差異
      if '軸承磨損' in status_option:
        # 高頻刺耳衝擊聲 (3500Hz 尖銳金屬摩擦 + 18Hz 週期性打擊)
        high_squeal = 0.5 * np.sin(2 * np.pi * 3500 * t)
        pulses = (
            np.maximum(0, np.sin(2 * np.pi * 18 * t)) ** 10
        ) * np.random.normal(0, 0.9, size=t.shape)
        signal = (
            0.3 * np.sin(2 * np.pi * base_f * t) + high_squeal + pulses
        )  # 聲響極度刺耳
      elif '不平衡' in status_option:
        # 重低音強烈調幅包絡 (擺動重音)
        am = 1.0 + 0.9 * np.sin(2 * np.pi * 6 * t)
        signal = 0.8 * np.sin(2 * np.pi * (base_f / 2) * t) * am + 0.1 * np.random.normal(
            size=t.shape
        )
      else:  # 異物卡阻
        # 爆衝金屬聲與亂流
        clicks = np.zeros_like(t)
        pts = np.random.choice(len(t), size=60, replace=False)
        clicks[pts] = np.random.uniform(1.5, 3.0, size=60)
        signal = (
            0.2 * np.sin(2 * np.pi * base_f * t)
            + clicks
            + np.random.normal(0, 0.3, size=t.shape)
        )

    signal = signal / (np.max(np.abs(signal)) + 1e-6)

  with k4:
    st.markdown(f'### 🔊 測試音頻試聽 ({audio_source_label})')
    st.audio(signal, sample_rate=fs)

  st.divider()

  # --- 聲學分析圖表 (時域 / 頻域 / 梅爾頻譜) ---
  st.subheader(f'📈 【{category}】 聲學特徵即時分析圖表')

  tab_time, tab_fft, tab_mel = st.tabs([
      '🌊 時域波形圖 (Waveform)',
      '📊 快速傅立葉變換 (FFT Spectrum)',
      '🖼️ 梅爾頻譜圖 (Mel-Spectrogram)',
  ])

  t_axis = np.linspace(0, len(signal) / fs, len(signal))

  with tab_time:
    fig_time, ax_time = plt.subplots(figsize=(10, 3.2))
    n_show = min(int(fs * 0.25), len(signal))
    ax_time.plot(t_axis[:n_show], signal[:n_show], color='#2563eb', lw=1)
    ax_time.set_title(
        f'{category} - 波形圖 (Time Domain) [{status_option}]', fontsize=11
    )
    ax_time.set_xlabel('時間 (Time / s)')
    ax_time.set_ylabel('振幅 (Amplitude)')
    ax_time.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig_time)

  with tab_fft:
    fig_fft, ax_fft = plt.subplots(figsize=(10, 3.2))
    fft_vals = np.abs(np.fft.rfft(signal))
    fft_freqs = np.fft.rfftfreq(len(signal), 1 / fs)
    ax_fft.plot(fft_freqs, fft_vals, color='#059669', lw=1)
    ax_fft.set_xlim(0, fs / 2)
    ax_fft.set_title(
        f'{category} - FFT 頻譜圖 (FFT Spectrum) [{status_option}]',
        fontsize=11,
    )
    ax_fft.set_xlabel('頻率 (Frequency / Hz)')
    ax_fft.set_ylabel('能量強度 (Magnitude)')
    ax_fft.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig_fft)

  with tab_mel:
    fig_mel, ax_mel = plt.subplots(figsize=(10, 3.2))
    Pxx, freqs, bins, im = ax_mel.specgram(
        signal, NFFT=512, Fs=fs, noverlap=256, cmap='magma'
    )
    ax_mel.set_title(
        f'{category} - 梅爾頻譜圖 (Mel-Spectrogram) [{status_option}]',
        fontsize=11,
    )
    ax_mel.set_xlabel('時間 (Time / s)')
    ax_mel.set_ylabel('頻率 (Frequency / Hz)')
    fig_mel.colorbar(im, ax=ax_mel, format='%+2.0f dB')
    st.pyplot(fig_mel)

  st.divider()

  # --- 設備異常排除建議 SOP 模組 (補回功能) ---
  st.subheader('📋 設備異常排除與維護建議 SOP')

  if is_normal:
    st.success("""
        **✅ 設備運行狀態：優良 (Normal)**
        - **維護建議**：無需立即處置，保持例行巡檢。
        - **建議保養週期**：依照原廠規範於 1,000 運轉小時後進行潤滑油脂補充。
        - **監控重點**：持續記錄 1X/2X 轉速諧波能量變動趨勢。
        """)
  elif '軸承磨損' in status_option:
    st.error("""
        **🚨 故障類型：軸承磨損 (Bearing Wear - BPFO/BPFI High Frequency Impact)**
        - **緊急程度**：高 (建議 48 小時內規劃停機檢修)
        - **可能原因**：潤滑油乾涸劣化、外圈滾道點蝕剝落、安裝偏心過大。
        - **標準處置 SOP**：
          1. 使用振規/聲學探針確認軸承座高頻 (2kHz-5kHz) 衝擊峰值。
          2. 檢查潤滑油品是否含有金屬磨屑，必要時重新加注 ISO VG68 潤滑油。
          3. 若高頻特徵持續增加，請準備備品並更換同型號深溝球/滾子軸承。
        """)
  elif '不平衡' in status_option:
    st.warning("""
        **⚠️ 故障類型：轉子不平衡 (Rotor Unbalance - 1X Rotational Frequency Dominant)**
        - **緊急程度**：中 (建議於本週保養時排程校正)
        - **可能原因**：葉片/轉子附著異物、平衡塊脫落、軸心熱彎曲變形。
        - **標準處置 SOP**：
          1. 停機清潔風扇葉片或轉子表面積垢。
          2. 使用動平衡儀進行現場單面/雙面動平衡校正 (Dynamic Balancing)。
          3. 檢查基座螺栓是否鬆動並重新以扭力板手締緊。
        """)
  else:  # 異物卡阻
    st.error("""
        **🚨 故障類型：管道/腔體異物卡阻 (Blockage / Cavitation / Impact Noise)**
        - **緊急程度**：極高 (請立即切斷電源並停機檢查)
        - **可能原因**：管道進氣/進水閥門阻塞、泵浦腔體產生氣蝕、機械組件外來異物侵入。
        - **標準處置 SOP**：
          1. 立即啟動緊急停機程序，避免電機過載燒毀。
          2. 拆卸進出口管路與濾網，清除卡阻之雜物或沉澱物。
          3. 檢查流體壓力與流量是否恢復正常水準。
        """)

  # 歸一化音量，避免破音
  signal = signal / np.max(np.abs(signal))

  with k4:
    st.markdown('### 🔊 測試音頻模擬試聽')
    st.audio(signal, sample_rate=fs)

  st.divider()

  # --- 繪製專業聲學分析圖表 ---
  st.subheader(f'📈 【{category}】 聲學特徵即時分析圖表')

  tab_time, tab_fft, tab_mel = st.tabs([
      '🌊 時域波形圖 (Waveform)',
      '📊 快速傅立葉變換 (FFT Spectrum)',
      '🖼️ 梅爾頻譜圖 (Mel-Spectrogram)',
  ])

  # 1. 時域波形圖
  with tab_time:
    fig_time, ax_time = plt.subplots(figsize=(10, 3.5))
    ax_time.plot(t[:3200], signal[:3200], color='#2563eb', lw=1)
    ax_time.set_title(
        f'{category} - Waveform [{status_option}] (First 0.2s)', fontsize=11
    )
    ax_time.set_xlabel('Time (s)')
    ax_time.set_ylabel('Amplitude')
    ax_time.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig_time)

  # 2. FFT 頻譜圖
  with tab_fft:
    fig_fft, ax_fft = plt.subplots(figsize=(10, 3.5))
    fft_vals = np.abs(np.fft.rfft(signal))
    fft_freqs = np.fft.rfftfreq(len(signal), 1 / fs)
    ax_fft.plot(fft_freqs[:3500], fft_vals[:3500], color='#059669', lw=1)
    ax_fft.set_title(
        f'{category} - FFT Spectrum [{status_option}]', fontsize=11
    )
    ax_fft.set_xlabel('Frequency (Hz)')
    ax_fft.set_ylabel('Magnitude')
    ax_fft.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig_fft)

  # 3. 梅爾頻譜圖 (STFT)
  with tab_mel:
    fig_mel, ax_mel = plt.subplots(figsize=(10, 3.5))
    Pxx, freqs, bins, im = ax_mel.specgram(
        signal, NFFT=512, Fs=fs, noverlap=256, cmap='magma'
    )
    ax_mel.set_title(
        f'{category} - Mel-Spectrogram [{status_option}]', fontsize=11
    )
    ax_mel.set_xlabel('Time (s)')
    ax_mel.set_ylabel('Frequency (Hz)')
    fig_mel.colorbar(im, ax=ax_mel, format='%+2.0f dB')
    st.pyplot(fig_mel)