import os
import wave
import struct
import math

# 1. 建立資料夾結構
os.makedirs("samples/fan", exist_ok=True)

def create_dummy_wav(filename, freq=440, is_anomaly=False):
    sample_rate = 16000 # 16kHz 採樣率
    duration = 2.0      # 2 秒
    num_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)     # 單聲道
        wav_file.setsampwidth(2)     # 16-bit
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            # 正常風扇：平順的正弦波基音
            value = math.sin(2 * math.pi * freq * t)
            
            # 如果是異常，加入雜訊與衝擊聲 (模擬葉片破損)
            if is_anomaly:
                noise = (math.sin(2 * math.pi * 1200 * t) * 0.3) + (math.sin(2 * math.pi * 3000 * t) * 0.2)
                value = 0.6 * value + 0.4 * noise
                
            packed_value = struct.pack('h', int(value * 32767 * 0.5))
            wav_file.writeframes(packed_value)

# 2. 生成正常與異常音檔
create_dummy_wav("samples/fan/normal_01.wav", freq=200, is_anomaly=False)
create_dummy_wav("samples/fan/anomaly_blade_01.wav", freq=200, is_anomaly=True)

print("✅ 音檔生成完畢！已建立：")
print(" - samples/fan/normal_01.wav")
print(" - samples/fan/anomaly_blade_01.wav")