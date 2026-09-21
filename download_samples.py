import os
import wave
import struct
import numpy as np

# 1. 統一標準音訊規格
sr = 16000          # 16kHz 邊緣運算標準採樣率
duration = 2.0      # 2 秒採樣
t = np.linspace(0, duration, int(sr * duration), endpoint=False)

def normalize_audio(audio, target_peak=0.9):
    """ 音訊響度標準化 (Peak Normalization) """
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        return (audio / max_val) * target_peak
    return audio

def generate_enhanced_audio(category, state):
    """
    state: 
      0 -> Normal (極純淨低頻基音)
      1 -> Warning (中頻節律性脈動/輕微擾流)
      2 -> Fault (強烈高頻金屬衝擊/爆裂/刮削聲，聽感極為顯著)
    """
    np.random.seed(42 + state * 100)
    bg_noise = np.random.normal(0, 0.005, len(t)) # 極輕微背景底噪
    
    # ---------------- 1. 工業風扇 (Fan) ----------------
    if category == "fan":
        base = 0.4 * np.sin(2 * np.pi * 30 * t) + 0.1 * np.sin(2 * np.pi * 60 * t) # 低頻風噪
        if state == 1:
            # 輕微不平衡：1Hz 低頻規律嗡嗡聲調變
            mod = 1.0 + 0.5 * np.sin(2 * np.pi * 2 * t)
            return normalize_audio(base * mod + bg_noise * 3)
        elif state == 2:
            # 葉片破損/異物：強烈金屬卡阻與高頻喀啦衝擊聲
            clack = np.zeros_like(t)
            idx = np.arange(0, len(t), int(sr * 0.15)) # 每 0.15 秒強烈撞擊一次
            clack[idx] = 0.8
            clack_sound = np.convolve(clack, np.sin(2 * np.pi * 2500 * t[:150]) * np.exp(-np.linspace(0, 5, 150)), mode='same')
            return normalize_audio(base + clack_sound + np.random.normal(0, 0.15, len(t)))
        return normalize_audio(base + bg_noise)

    # ---------------- 2. 工業馬達 (Motor) ----------------
    elif category == "motor":
        base = 0.4 * np.sin(2 * np.pi * 50 * t) + 0.2 * np.sin(2 * np.pi * 100 * t) # 馬達電磁基頻
        if state == 1:
            # 轉子偏心：低頻嗡嗡拍頻 (Beat Frequency)
            beat = 0.3 * np.sin(2 * np.pi * 54 * t)
            return normalize_audio(base + beat + bg_noise * 2)
        elif state == 2:
            # 嚴重軸承磨損：強烈刺耳金屬摩擦與尖銳爆音 (Bearing Squeal)
            squeal = 0.6 * np.sin(2 * np.pi * 3800 * t) * (1 + 0.5 * np.sin(2 * np.pi * 10 * t))
            impacts = np.random.normal(0, 0.2, len(t))
            return normalize_audio(base + squeal + impacts)
        return normalize_audio(base + bg_noise)

    # ---------------- 3. 工業水泵 (Pump) ----------------
    elif category == "pump":
        base = 0.35 * np.sin(2 * np.pi * 45 * t) + 0.15 * np.sin(2 * np.pi * 90 * t)
        if state == 1:
            # 輕微氣蝕：微弱氣泡破裂咕嚕聲
            bubbles = 0.15 * np.random.normal(0, 0.05, len(t)) * (np.sin(2 * np.pi * 800 * t) + 1)
            return normalize_audio(base + bubbles + bg_noise * 2)
        elif state == 2:
            # 嚴重氣蝕/空轉：巨大金屬水錘與高壓空化炸裂聲 (Cavitation Blast)
            blasts = np.zeros_like(t)
            b_idx = np.random.choice(len(t), size=50, replace=False)
            blasts[b_idx] = np.random.uniform(0.6, 1.0, size=50)
            blast_sound = np.convolve(blasts, np.sin(2 * np.pi * 3200 * t[:200]), mode='same')
            return normalize_audio(base * 0.5 + blast_sound + np.random.normal(0, 0.2, len(t)))
        return normalize_audio(base + bg_noise)

    # ---------------- 4. 電磁閥門 (Valve) ----------------
    elif category == "valve":
        base = 0.2 * np.sin(2 * np.pi * 120 * t)
        if state == 1:
            # 輕微結垢：動作遲緩與微弱氣音
            hiss = 0.15 * np.random.normal(0, 0.03, len(t)) * np.sin(2 * np.pi * 1500 * t)
            return normalize_audio(base + hiss + bg_noise * 2)
        elif state == 2:
            # 嚴重洩漏：高壓氣流強烈嘶嘶噴射聲 (High-Pressure Jet Leak)
            jet_leak = 0.7 * np.random.normal(0, 0.15, len(t)) * (np.sin(2 * np.pi * 5500 * t) + 1.5)
            return normalize_audio(base * 0.2 + jet_leak)
        return normalize_audio(base + bg_noise)

    # ---------------- 5. 線性滑軌 (Slider) ----------------
    elif category == "slider":
        slide_env = np.abs(np.sin(2 * np.pi * 0.5 * t)) # 滑塊來回運轉包絡線
        base = 0.3 * slide_env * np.sin(2 * np.pi * 180 * t)
        if state == 1:
            # 潤滑不足：中頻乾摩擦嗡嗡聲
            dry_friction = 0.2 * slide_env * np.sin(2 * np.pi * 1200 * t)
            return normalize_audio(base + dry_friction + bg_noise * 2)
        elif state == 2:
            # 軌道刮傷：極度刺耳之金屬刺刮衝擊 (Metal Screech & Scratch)
            screech = 0.8 * slide_env * np.random.normal(0, 0.2, len(t)) * np.sin(2 * np.pi * 6500 * t)
            return normalize_audio(base * 0.3 + screech)
        return normalize_audio(base + bg_noise)

    # ---------------- 6. 工業齒輪箱 (Gearbox) ----------------
    else:
        gmf = 0.4 * np.sin(2 * np.pi * 400 * t) # 齒輪囓合頻率 (GMF)
        if state == 1:
            # 輕微點蝕：週期性微弱邊頻調變
            sideband = 0.2 * np.sin(2 * np.pi * 400 * t) * np.sin(2 * np.pi * 20 * t)
            return normalize_audio(gmf + sideband + bg_noise * 2)
        elif state == 2:
            # 嚴重斷齒：週期性劇烈金屬敲擊砰砰聲 (Severe Tooth Impact)
            impact = 0.9 * (np.sin(2 * np.pi * 10 * t) ** 16) * np.sin(2 * np.pi * 2200 * t)
            return normalize_audio(gmf * 0.4 + impact + np.random.normal(0, 0.1, len(t)))
        return normalize_audio(gmf + bg_noise)

def save_wav_16bit(filename, audio_data):
    """ 導出標準 PCM 16-bit WAV 格式 """
    scaled = (audio_data * 32767).astype(np.int16)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)   # 單聲道
        wav_file.setsampwidth(2)   # 16-bit
        wav_file.setframerate(sr)  # 16000Hz
        for sample in scaled:
            wav_file.writeframes(struct.pack('<h', sample))

# 執行 6 大設備 3 階標準化音訊生成
categories = ["fan", "motor", "pump", "valve", "slider", "gearbox"]

for cat in categories:
    folder_path = os.path.join("samples", cat)
    os.makedirs(folder_path, exist_ok=True)
    
    # 1. 正常音訊 (Normal)
    save_wav_16bit(os.path.join(folder_path, "normal_01.wav"), generate_enhanced_audio(cat, 0))
    
    # 2. 警告音訊 (Warning)
    save_wav_16bit(os.path.join(folder_path, "warning_01.wav"), generate_enhanced_audio(cat, 1))
    
    # 3. 嚴重故障音訊 (Fault)
    fault_filename = f"anomaly_{'blade' if cat=='fan' else 'bearing' if cat=='motor' else 'cavitation' if cat=='pump' else 'leak' if cat=='valve' else 'scratch' if cat=='slider' else 'gear'}_01.wav"
    save_wav_16bit(os.path.join(folder_path, fault_filename), generate_enhanced_audio(cat, 2))

print("🎉 已完成全平台 6 大設備音訊之【標準化處理】與【聲學特徵顯著度倍增】！")