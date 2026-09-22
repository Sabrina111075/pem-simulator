import os
import wave
import math
import struct
import random

output_dir = "samples/wind_field"
os.makedirs(output_dir, exist_ok=True)

def generate_field_sound(filename, mode):
    filepath = os.path.join(output_dir, filename)
    sample_rate = 16000
    duration = 2.0
    num_samples = int(sample_rate * duration)
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            if mode == "low_wind":
                # 低風速：平穩低頻馬達 + 輕微微風
                tone = math.sin(2 * math.pi * 80 * t) * 0.5
                noise = (random.random() * 2 - 1) * 0.05
                signal = tone + noise
                
            elif mode == "high_wind":
                # 高風速：強烈 1.5Hz 氣流切風週期聲 (Swish) + 高背景風噪
                swish_envelope = (math.sin(2 * math.pi * 1.5 * t) + 1) / 2 # 0~1 波動
                wind_noise = (random.random() * 2 - 1) * (0.2 + 0.5 * swish_envelope)
                tone = math.sin(2 * math.pi * 120 * t) * 0.2
                signal = tone + wind_noise
                
            elif mode == "fault_wind":
                # 強風故障：高風噪 + 刺耳高頻金屬刮削 (2400Hz) + 週期敲擊衝擊波
                swish_envelope = (math.sin(2 * math.pi * 1.5 * t) + 1) / 2
                wind_noise = (random.random() * 2 - 1) * 0.3
                metal_scrape = math.sin(2 * math.pi * 2400 * t) * 0.4 # 高頻異音
                impact = 0.6 if (i % 4000 < 200) else 0.0             # 衝擊叩擊聲
                signal = wind_noise + metal_scrape + impact
                
            sample = int(signal * 12000)
            sample = max(-32768, min(32767, sample))
            wav_file.writeframes(struct.pack('<h', sample))

print("正在重新生成特徵顯著的風場音訊...")
generate_field_sound("low_wind_normal.wav", "low_wind")
generate_field_sound("high_wind_normal.wav", "high_wind")
generate_field_sound("wind_fault.wav", "fault_wind")
print("✅ 完成！音效特徵已拉開差異。")