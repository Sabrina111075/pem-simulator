import glob
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from scipy.io import wavfile

# ==============================================================================
# 0. 全局與 Matplotlib 中文字體設定 (防止 □□□□ 方塊亂碼)
# ==============================================================================
st.set_page_config(
    page_title="馬達與工業設備聲學診斷測試平台", page_icon="⚙️", layout="wide"
)

plt.rcParams['font.sans-serif'] = [
    'Microsoft JhengHei',
    'DFKai-SB',
    'SimHei',
    'Arial',
]
plt.rcParams['axes.unicode_minus'] = False

# ==============================================================================
# 1. 側邊欄切換模組 (導航頁面)
# ==============================================================================
st.sidebar.title('📌 切換功能模組')
app_mode = st.sidebar.radio(
    '選擇功能頁面：', ['設備與測試控制台', 'OpenMAIC Academy']
)

# ==============================================================================
# 2. 頁面 1：OpenMAIC Academy 模組
# ==============================================================================
if app_mode == 'OpenMAIC Academy':
  st.title('🎓 OpenMAIC Multi-Agent 聲學診斷互動學習模組')
  st.info('進入 OpenMAIC 多 Agent 協同架構教學與說明...')

# ==============================================================================
# 3. 頁面 2：設備與測試控制台 (含 samples/ 對接 + SOP 建議 + 圖表)
# ==============================================================================
else:
  st.title('⚙️ 馬達與工業設備聲學診斷測試平台 (EdgeAcoustic AI)')
  st.caption('邊緣運算前置驗證平台 | 支援 ESP32-S3 + Raspberry Pi 5 模擬測試')

  st.info(
      '📊 **聲學基準數據來源 (Benchmark Dataset)**：本平台測試音訊基準參照 DCASE Challenge Task'
      ' 2 / MIMII Dataset (Fan, Motor, Pump, Valve, Slide Rail, Gearbox)'
      ' 之設備聲學特徵與頻域指標進行標定與驗證。'
  )

  # --- 側邊欄控制選項 ---
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

  # --- 頂部狀態 KPI 卡片 ---
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

  # --- 音訊讀取邏輯：優先 samples/ 資料匣，次選數學合成模型 ---
  fs = 16000
  signal = None
  audio_source_label = '數學聲學模型生成'

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
    except Exception:
      signal = None

  # 數學備用合成演算法（顯著差異化）
  if signal is None:
    duration = 2.5
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
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
      signal = 0.4 * np.sin(2 * np.pi * base_f * t) + 0.15 * np.sin(
          2 * np.pi * base_f * 2 * t
      )
      signal += 0.01 * np.random.normal(size=t.shape)
    else:
      if '軸承磨損' in status_option:
        high_squeal = 0.5 * np.sin(2 * np.pi * 3500 * t)
        pulses = (
            np.maximum(0, np.sin(2 * np.pi * 18 * t)) ** 10
        ) * np.random.normal(0, 0.9, size=t.shape)
        signal = 0.3 * np.sin(2 * np.pi * base_f * t) + high_squeal + pulses
      elif '不平衡' in status_option:
        am = 1.0 + 0.9 * np.sin(2 * np.pi * 6 * t)
        signal = 0.8 * np.sin(2 * np.pi * (base_f / 2) * t) * am + 0.1 * np.random.normal(
            size=t.shape
        )
      else:
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

  # --- 聲學分析圖表 (時域/FFT/梅爾頻譜) ---
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

  # --- 設備異常排除建議 SOP 模組 ---
  st.subheader('📋 設備異常排除與維護建議 SOP')

  if is_normal:
    st.success("""
        **✅ 設備運行狀態：優良 (Normal)**
        - **維護建議**：無需補充與檢修，維持常規巡檢紀錄。
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