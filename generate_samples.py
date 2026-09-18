import os
import wave
import struct
import math
import random

# 建立資料夾結構
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
                # 正常風聲：低頻蜂鳴 (150 Hz) + 平緩氣流風噪
                value = 0.3 * math.sin(2 * math.pi * 150 * t) + 0.05 * (random.random() - 0.5)
                
            elif sound_type == "fan_anomaly":
                # 異常葉片：低頻風聲 + 劇烈高頻摩擦 (2800 Hz) + 規律的敲擊衝擊聲 (Impact)
                impact = 1.0 if (i % (sample_rate // 5)) < 300 else 0.0
                high_squeal = 0.6 * math.sin(2 * math.pi * 2800 * t) + 0.3 * (random.random() - 0.5)
                value = 0.2 * math.sin(2 * math.pi * 150 * t) + high_squeal + impact * 0.7
                
            # --- 工業馬達 (Motor) ---
            elif sound_type == "motor_normal":
                # 正常馬達：穩定的 60Hz 運轉基頻 + 120Hz 諧波
                value = 0.4 * math.sin(2 * math.pi * 60 * t) + 0.2 * math.sin(2 * math.pi * 120 * t)
                
            elif sound_type == "motor_anomaly":
                # 軸承損壞：馬達基頻 + 極為顯著的高頻金屬刮削異音 (3600 Hz ~ 4200 Hz)
                metal_grind = 0.6 * math.sin(2 * math.pi * 3600 * t) + 0.5 * math.sin(2 * math.pi * 4200 * t)
                value = 0.2 * math.sin(2 * math.pi * 60 * t) + metal_grind + 0.25 * (random.random() - 0.5)

            # 限制振幅防止爆音
            value = max(-1.0, min(1.0, value))
            packed_value = struct.pack('h', int(value * 32767 * 0.6))
            wav_file.writeframes(packed_value)

# 產生符合 DCASE 特徵的 4 個聲音檔
generate_wav("samples/fan/normal_01.wav", "fan_normal")
generate_wav("samples/fan/anomaly_blade_01.wav", "fan_anomaly")
generate_wav("samples/motor/normal_01.wav", "motor_normal")
generate_wav("samples/motor/anomaly_bearing_01.wav", "motor_anomaly")

print("✅ 所有 DCASE 測試音檔已在本地順利生成完畢！")