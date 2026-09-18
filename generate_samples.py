import os
import wave
import struct
import math
import random

# 1. 建立資料夾結構
os.makedirs("samples/fan", exist_ok=True)
os.makedirs("samples/motor", exist_ok=True)

def generate_wav(filename, sound_type):
    sample_rate = 16000
    duration = 2.0
    num_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)     # 單聲道
        wav_file.setsampwidth(2)     # 16-bit PCM
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            value = 0.0
            
            # --- 工業風扇 (Fan) ---
            if sound_type == "fan_normal":
                # 平緩穩定的低頻風切聲 (150 Hz + 低頻白雜訊)
                value = 0.4 * math.sin(2 * math.pi * 150 * t) + 0.1 * (random.random() - 0.5)
                
            elif sound_type == "fan_anomaly":
                # 葉片損壞：低頻風聲 + 劇烈高頻尖銳聲 + 每秒 4 次的卡噠衝擊聲 (Impact)
                impact = 1.0 if (i % (sample_rate // 4)) < 200 else 0.0
                high_noise = 0.5 * math.sin(2 * math.pi * 2400 * t) + 0.3 * (random.random() - 0.5)
                value = 0.3 * math.sin(2 * math.pi * 150 * t) + high_noise + impact * 0.8
                
            # --- 工業馬達 (Motor) ---
            elif sound_type == "motor_normal":
                # 正常馬達：穩定的 60Hz 電源頻率 + 120Hz 雙倍頻嗡嗡聲
                value = 0.5 * math.sin(2 * math.pi * 60 * t) + 0.3 * math.sin(2 * math.pi * 120 * t)
                
            elif sound_type == "motor_anomaly":
                # 軸承損壞：馬達運轉聲 + 顯著的高頻金屬刮削金屬磨損聲 (3500 Hz ~ 4500 Hz)
                metal_grind = 0.6 * math.sin(2 * math.pi * 3800 * t) + 0.4 * math.sin(2 * math.pi * 4200 * t)
                value = 0.3 * math.sin(2 * math.pi * 60 * t) + metal_grind + 0.2 * (random.random() - 0.5)

            # 限制振幅範圍防止爆音
            value = max(-1.0, min(1.0, value))
            packed_value = struct.pack('h', int(value * 32767 * 0.6))
            wav_file.writeframes(packed_value)

# 2. 生成所有測試音檔
generate_wav("samples/fan/normal_01.wav", "fan_normal")
generate_wav("samples/fan/anomaly_blade_01.wav", "fan_anomaly")
generate_wav("samples/motor/normal_01.wav", "motor_normal")
generate_wav("samples/motor/anomaly_bearing_01.wav", "motor_anomaly")

print("✅ 所有音檔生成成功！")
print(" - samples/fan/normal_01.wav")
print(" - samples/fan/anomaly_blade_01.wav")
print(" - samples/motor/normal_01.wav")
print(" - samples/motor/anomaly_bearing_01.wav")