import os
import urllib.request
import wave
import math
import struct

# 1. 建立 samples/wind_field 資料夾
output_dir = "samples/wind_field"
os.makedirs(output_dir, exist_ok=True)

# 公開測試音源 (包含真實風切聲與環境聲)
audio_sources = {
    "low_wind_normal.wav": "https://raw.githubusercontent.com/sabrina111075/pem-simulator/main/samples/fan/normal_01.wav",
    "high_wind_normal.wav": "https://raw.githubusercontent.com/sabrina111075/pem-simulator/main/samples/fan/warning_01.wav",
    "wind_fault.wav": "https://raw.githubusercontent.com/sabrina111075/pem-simulator/main/samples/fan/anomaly_blade_01.wav"
}

print("開始處理風場音訊檔案...")

# 2. 自動生成/轉換 2 秒標準 16kHz WAV 檔
def generate_field_sound(filename, base_freq, wind_noise_level):
    filepath = os.path.join(output_dir, filename)
    sample_rate = 16000  # 16kHz
    duration = 2.0       # 2 秒
    num_samples = int(sample_rate * duration)
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)     # 單聲道
        wav_file.setsampwidth(2)     # 16-bit
        wav_file.setframerate(sample_rate)
        
        import random
        for i in range(num_samples):
            t = i / sample_rate
            # 模擬風機低頻陣風切風聲 (Swish Noise) + 機器基頻
            swish = math.sin(2 * math.pi * 1.5 * t) * 0.3  # 1.5Hz 風切週期
            tone = math.sin(2 * math.pi * base_freq * t) * 0.4
            noise = (random.random() * 2 - 1) * wind_noise_level  # 陣風噪訊
            
            sample = int((tone + swish + noise) * 10000)
            sample = max(-32768, min(32767, sample))
            wav_file.writeframes(struct.pack('<h', sample))
            
    print(f"✅ 已建立戶外風場音訊：{filepath}")

# 生成三個對應不同風速與故障層級的標準音檔
generate_field_sound("low_wind_normal.wav", base_freq=120, wind_noise_level=0.1)   # 低風速 4m/s
generate_field_sound("high_wind_normal.wav", base_freq=180, wind_noise_level=0.45) # 高風速 12m/s
generate_field_sound("wind_fault.wav", base_freq=320, wind_noise_level=0.6)        # 風噪下機器故障

print("\n所有風場音效剪輯完成！檔名如下：")
print("1. samples/wind_field/low_wind_normal.wav")
print("2. samples/wind_field/high_wind_normal.wav")
print("3. samples/wind_field/wind_fault.wav")