import os
import wave
import struct
import numpy as np

sr = 16000
duration = 2.0
t = np.linspace(0, duration, int(sr * duration), endpoint=False)

def generate_audio(category, state):
    # state: 0 -> Normal (正常), 1 -> Warning (黃色警告), 2 -> Fault (紅色嚴重故障)
    np.random.seed(42 + state * 100)
    noise = np.random.normal(0, 0.02, len(t))
    
    if category == "pump":
        base = 0.15 * np.sin(2 * np.pi * 50 * t) + 0.08 * np.sin(2 * np.pi * 100 * t)
        if state == 1: # 警告：輕微氣蝕與低頻擾流
            cavitation = 0.08 * np.sin(2 * np.pi * 1800 * t) * np.random.normal(0, 0.05, len(t))
            return base + cavitation + noise * 1.2
        elif state == 2: # 故障：強烈空化爆裂衝擊
            impacts = np.zeros_like(t)
            impact_idx = np.random.choice(len(t), size=40, replace=False)
            impacts[impact_idx] = np.random.uniform(0.4, 0.8, size=40)
            cavitation = np.convolve(impacts, np.sin(2 * np.pi * 3500 * t[:200]), mode='same')
            return base + cavitation + noise * 3.0
        return base + noise

    elif category == "valve":
        base = 0.1 * np.sin(2 * np.pi * 120 * t)
        if state == 1: # 警告：閥體微幅結垢/低頻滯遲氣流
            hiss = 0.08 * np.sin(2 * np.pi * 2200 * t) + 0.05 * np.random.normal(0, 0.04, len(t))
            return base + hiss + noise
        elif state == 2: # 故障：高壓氣體嚴重噴射洩漏聲
            leak_hiss = 0.35 * np.random.normal(0, 0.12, len(t)) * (np.sin(2 * np.pi * 5000 * t) + 1.2)
            return base + leak_hiss + noise * 2.0
        return base + noise

    elif category == "slider":
        slide_env = np.abs(np.sin(2 * np.pi * 0.5 * t))
        base = 0.12 * slide_env * np.sin(2 * np.pi * 200 * t)
        if state == 1: # 警告：缺油乾摩擦音
            friction = 0.1 * slide_env * np.sin(2 * np.pi * 2800 * t)
            return base + friction + noise * 1.2
        elif state == 2: # 故障：軌道金屬劇烈刮削與金屬撞擊
            scratch = 0.38 * slide_env * np.random.normal(0, 0.15, len(t)) * np.sin(2 * np.pi * 6000 * t)
            return base + scratch + noise * 2.5
        return base + noise

    elif category == "gearbox":
        gmf = 0.15 * np.sin(2 * np.pi * 480 * t) + 0.08 * np.sin(2 * np.pi * 960 * t)
        if state == 1: # 警告：輕微微幅點蝕邊頻帶
            sideband = 0.08 * np.sin(2 * np.pi * 540 * t)
            return gmf + sideband + noise * 1.2
        elif state == 2: # 故障：斷齒劇烈衝擊峰值
            mod = 0.45 * (np.sin(2 * np.pi * 15 * t) ** 10) * np.sin(2 * np.pi * 2400 * t)
            return gmf + mod + noise * 2.8
        return gmf + noise

    return noise

def save_wav(filename, audio_data):
    max_val = np.max(np.abs(audio_data))
    scaled = (audio_data / max_val * 32767).astype(np.int16) if max_val > 0 else audio_data.astype(np.int16)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sr)
        for sample in scaled:
            wav_file.writeframes(struct.pack('<h', sample))

categories = ["pump", "valve", "slider", "gearbox"]

for cat in categories:
    folder_path = os.path.join("samples", cat)
    os.makedirs(folder_path, exist_ok=True)
    
    # 產生 3 種明確區隔的音效
    save_wav(os.path.join(folder_path, "normal_01.wav"), generate_audio(cat, 0))
    save_wav(os.path.join(folder_path, "warning_01.wav"), generate_audio(cat, 1))
    
    fault_name = f"anomaly_{'cavitation' if cat=='pump' else 'leak' if cat=='valve' else 'scratch' if cat=='slider' else 'gear'}_01.wav"
    save_wav(os.path.join(folder_path, fault_name), generate_audio(cat, 2))

print("✅ 已重新生成精確區分【正常 / 警告 / 嚴重故障】的 3 階音訊檔！")