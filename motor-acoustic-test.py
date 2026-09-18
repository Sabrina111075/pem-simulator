import os
import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# 1. 頁面配置
st.set_page_config(page_title="馬達與工業設備聲學診斷測試平台", layout="wide")

# 2. 設備與異音類別對映字典
SAMPLE_DATA = {
    "工業風扇 (Fan)": {
        "正常 (Normal)": {
            "file": "samples/fan/normal_01.wav", 
            "hi": 98, 
            "mse": 0.0015, 
            "status": "正常 (Normal)",
            "guide": "當前聲學特徵穩定，訊號重構誤差 (MSE) 處於安全基準線以下。\n1. 外觀與溫度：定期量測風扇外殼溫升，確認風路與散熱片無積塵遮蔽。"
        },
        "葉片破損/異物 (Blade Fault)": {
            "file": "samples/fan/anomaly_blade_01.wav", 
            "hi": 58, 
            "mse": 0.0842, 
            "status": "異常 (Anomaly)",
            "guide": "檢測到高頻異常震動與風切聲，重構誤差超標。\n1. 停機檢查：確認風扇葉片是否有碎裂、變形或異物纏繞。\n2. 轉子平衡：檢查動平衡狀況，避免軸承二次損壞。"
        }
    },
    "工業馬達 (Motor)": {
        "正常 (Normal)": {
            "file": "samples/motor/normal_01.wav", 
            "hi": 99, 
            "mse": 0.0008, 
            "status": "正常 (Normal)",
            "guide": "馬達運轉聲響平均，無明顯諧波異音。\n1. 潤滑維護：按時補充指定規格之潤滑油脂。"
        },
        "軸承損壞 (Bearing Wear)": {
            "file": "samples/motor/anomaly_bearing_01.wav", 
            "hi": 42, 
            "mse": 0.1250, 
            "status": "異常 (Anomaly)",
            "guide": "頻譜顯示顯著特徵頻率峰值，判定為軸承軌道剝落或磨損。\n1. 緊急排修：安排計畫性停機更換軸承。\n2. 對心檢查：重新校正馬達與負載側之聯軸器對心。"
        }
    }
}

# 3. 側邊欄：選單控制
st.sidebar.title("⚙️ 設備與測試控制台")
category = st.sidebar.selectbox("1. 選擇設備類別 (Category)", list(SAMPLE_DATA.keys()))
fault_type = st.sidebar.selectbox("2. 選擇測試狀態/故障型態", list(SAMPLE_DATA[category].keys()))

current_sample = SAMPLE_DATA[category][fault_type]

# 4. 主畫面標題與邊緣運算標籤
st.title("⚙️ 馬達與工業設備聲學診斷測試平台 (EdgeAcoustic AI)")
st.caption("邊緣運算前置驗證平台 | 支援 ESP32-S3 + Raspberry Pi 5 模擬測試")

# 5. 指標卡片
col1, col2, col3 = st.columns([1, 1, 1.5])
col1.metric("設備健康指標 (HI)", f"{current_sample['hi']} %", delta="狀態良好" if current_sample['hi'] > 80 else "-警告", delta_color="normal" if current_sample['hi'] > 80 else "inverse")
col2.metric("重構誤差 (MSE)", f"{current_sample['mse']:.4f}", delta="門檻: 0.05", delta_color="inverse")

with col3:
    st.write("**診斷狀態**")
    if current_sample['status'] == "正常 (Normal)":
        st.success(f"✔ {current_sample['status']}")
    else:
        st.error(f"⚠️ {current_sample['status']}")

st.divider()

# 6. 音訊試聽與 Mel-Spectrogram 頻譜視覺化
st.write("### 🔊 採樣音訊與邊緣聲學特徵 (Mel-Spectrogram)")

col_audio, col_spec = st.columns([1, 2])

audio_path = current_sample['file']

with col_audio:
    st.write("**採樣音頻試聽**")
    if os.path.exists(audio_path):
        with open(audio_path, 'rb') as audio_file:
            st.audio(audio_file.read(), format='audio/wav')
    else:
        st.warning(f"請將測試音檔放置於：`{audio_path}`")

with col_spec:
    if os.path.exists(audio_path):
        # 讀取音檔並計算 Mel 頻譜
        y, sr = librosa.load(audio_path, sr=16000)
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        
        # 繪製 Matplotlib 圖表
        fig, ax = plt.subplots(figsize=(7, 2.5))
        img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, fmax=8000, ax=ax, cmap='magma')
        fig.colorbar(img, ax=ax, format='%+2.0f dB')
        ax.set_title("Edge AI Input: Mel-Spectrogram", fontsize=10)
        ax.set_xlabel("Time (s)", fontsize=8)
        ax.set_ylabel("Hz", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("音檔載入後將自動繪製梅爾頻譜圖 (Mel-Spectrogram)")

# 7. 維運指引
st.subheader("📋 設備日常巡檢維運指引 (Routine Maintenance Guide)")
st.info(current_sample['guide'])