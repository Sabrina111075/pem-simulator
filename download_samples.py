import os
import wave
import struct
import numpy as np

# 1. 統一標準音訊規格
sr = 16000          # 16kHz 邊緣運算標準採樣率
duration = 2.0      # 2 秒採樣
t = np.linspace(0, duration, int(sr * duration), endpoint=False)

def standardize_audio(audio, target_peak=0.85):
    """
    音訊標準化處理：
    1. RMS 響度平衡
    2. Peak Normalization 峰值防爆音 (固定 0.85 振幅，確保音量一致不忽大忽小)
    """
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val
    
    # 計算 RMS 平滑音量
    rms = np.sqrt(np.mean(audio**2))
    if rms > 0:
        audio = audio / rms * 0.25  # 統一平均能量
    
    # 再次確認不超過 Target Peak
    max_peak = np.max(np.abs(audio))
    if max_peak > target_peak:
        audio = (audio / max_peak) * target_peak
        
    return audio

def generate_highly_differentiated_audio(category, state):
    """
    state: 
      0 -> Normal (純淨平穩運轉音)
      1 -> Warning (具備極高辨識度之預警聲學特徵：拍頻/氣泡/摩擦/抖動)
      2 -> Fault (強烈金屬衝擊/爆裂/嚴重洩漏/斷齒)
    """
    np.random.seed(42 + state * 100)
    bg_noise = np.random.normal(0, 0.003, len(t))
    
    # ---------------- 1. 工業風扇 (Fan) ----------------
    if category == "fan":
        base = 0.5 * np.sin(2 * np.pi * 35 * t) + 0.15 * np.sin(2 * np.pi * 70 * t)
        if state == 1:
            # 輕微不平衡：強烈 4Hz 低頻擺動脈動 (Wobble Beat)
            wobble = (1.0 + 0.7 * np.sin(2 * np.pi * 4 * t)) # 強烈 4Hz 調變
            return standardize_audio(base * wobble + np.random.normal(0, 0.015, len(t)))
        elif state == 2:
            # 嚴重破損：強烈金屬卡阻與頻繁刮削聲
            clack = np.zeros_like(t)
            idx = np.arange(0, len(t), int(sr * 0.12))
            clack[idx] = 0.8
            clack_sound = np.convolve(clack, np.sin(2 * np.pi * 2200 * t[:150]) * np.exp(-np.linspace(0, 4, 150)), mode='same')
            return standardize_audio(base + clack_sound + np.random.normal(0, 0.12, len(t)))
        return standardize_audio(base + bg_noise)

    # ---------------- 2. 工業馬達 (Motor) ----------------
    elif category == "motor":
        base = 0.5 * np.sin(2 * np.pi * 50 * t) + 0.25 * np.sin(2 * np.pi * 100 * t)
        if state == 1:
            # 轉子偏心：7Hz 明顯電磁拍頻與顫音 (Electromagnetic Humming Beat)
            beat_mod = 1.0 + 0.65 * np.sin(2 * np.pi * 7 * t)
            sub_hum = 0.3 * np.sin(2 * np.pi * 150 * t) * beat_mod
            return standardize_audio((base + sub_hum) * beat_mod + np.random.normal(0, 0.01, len(t)))
        elif state == 2:
            # 嚴重軸承磨損：高頻刺耳哮聲與金屬磨損
            squeal = 0.7 * np.sin(2 * np.pi * 3600 * t) * (1 + 0.4 * np.sin(2 * np.pi * 12 * t))
            impacts = np.random.normal(0, 0.18, len(t))
            return standardize_audio(base + squeal + impacts)
        return standardize_audio(base + bg_noise)

    # ---------------- 3. 工業水泵 (Pump) ----------------
    elif category == "pump":
        base = 0.45 * np.sin(2 * np.pi * 40 * t) + 0.2 * np.sin(2 * np.pi * 80 * t)
        if state == 1:
            # 流體輕微氣蝕：顯著且綿密的中高頻氣泡破裂聲 (Bubbling Cavitation Noise)
            bubble_env = (np.sin(2 * np.pi * 12 * t) + 1.2) / 2.2
            bubbles = 0.35 * np.random.normal(0, 0.08, len(t)) * bubble_env * np.sin(2 * np.pi * 1600 * t)
            return standardize_audio(base + bubbles + np.random.normal(0, 0.02, len(t)))
        elif state == 2:
            # 軸封嚴重磨損/空轉：巨大金屬水錘爆裂聲
            blasts = np.zeros_like(t)
            b_idx = np.random.choice(len(t), size=45, replace=False)
            blasts[b_idx] = np.random.uniform(0.7, 1.0, size=45)
            blast_sound = np.convolve(blasts, np.sin(2 * np.pi * 3000 * t[:180]), mode='same')
            return standardize_audio(base * 0.4 + blast_sound + np.random.normal(0, 0.15, len(t)))
        return standardize_audio(base + bg_noise)

    # ---------------- 4. 電磁閥門 (Valve) ----------------
    elif category == "valve":
        base = 0.3 * np.sin(2 * np.pi * 100 * t)
        if state == 1:
            # 閥體輕微結垢：動作滯遲與明顯的高頻滑動摩擦氣音 (Sluggish Friction Hiss)
            friction_hiss = 0.4 * np.random.normal(0, 0.08, len(t)) * np.sin(2 * np.pi * 2400 * t)
            ticks = np.zeros_like(t)
            ticks[::int(sr*0.5)] = 0.5 # 每 0.5 秒一次卡阻咯噠聲
            return standardize_audio(base + friction_hiss + ticks + np.random.normal(0, 0.01, len(t)))
        elif state == 2:
            # 嚴重洩漏：強烈高壓噴射嘶嘶聲
            jet_leak = 0.8 * np.random.normal(0, 0.18, len(t)) * (np.sin(2 * np.pi * 5000 * t) + 1.5)
            return standardize_audio(base * 0.2 + jet_leak)
        return standardize_audio(base + bg_noise)

    # ---------------- 5. 線性滑軌 (Slider) ----------------
    elif category == "slider":
        slide_env = np.abs(np.sin(2 * np.pi * 0.5 * t)) # 來回行程包絡線
        base = 0.4 * slide_env * np.sin(2 * np.pi * 160 * t)
        if state == 1:
            # 潤滑油脂不足：顯著的高頻金屬乾摩擦嘶嘶聲 (Dry Metallic Friction)
            dry_friction = 0.45 * slide_env * np.random.normal(0, 0.09, len(t)) * np.sin(2 * np.pi * 2800 * t)
            return standardize_audio(base + dry_friction + np.random.normal(0, 0.015, len(t)))
        elif state == 2:
            # 軌道刮傷：刺耳刮削聲與連續衝擊
            screech = 0.85 * slide_env * np.random.normal(0, 0.2, len(t)) * np.sin(2 * np.pi * 6200 * t)
            return standardize_audio(base * 0.2 + screech)
        return standardize_audio(base + bg_noise)

    # ---------------- 6. 工業齒輪箱 (Gearbox) ----------------
    else:
        gmf = 0.5 * np.sin(2 * np.pi * 380 * t)
        if state == 1:
            # 齒面輕微點蝕：5Hz 週期性咬合邊頻與微弱點蝕聲
            pitting = 0.35 * np.sin(2 * np.pi * 380 * t) * np.sin(2 * np.pi * 5 * t)
            return standardize_audio(gmf + pitting + np.random.normal(0, 0.015, len(t)))
        elif state == 2:
            # 輪齒嚴重點蝕/缺角：劇烈齒輪敲擊衝擊音
            impact = 0.9 * (np.sin(2 * np.pi * 10 * t) ** 14) * np.sin(2 * np.pi * 2000 * t)
            return standardize_audio(gmf * 0.3 + impact + np.random.normal(0, 0.1, len(t)))
        return standardize_audio(gmf + bg_noise)

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
    save_wav_16bit(os.path.join(folder_path, "normal_01.wav"), generate_highly_differentiated_audio(cat, 0))
    
    # 2. 警告音訊 (Warning)
    save_wav_16bit(os.path.join(folder_path, "warning_01.wav"), generate_highly_differentiated_audio(cat, 1))
    
    # 3. 嚴重故障音訊 (Fault)
    fault_filename = f"anomaly_{'blade' if cat=='fan' else 'bearing' if cat=='motor' else 'cavitation' if cat=='pump' else 'leak' if cat=='valve' else 'scratch' if cat=='slider' else 'gear'}_01.wav"
    save_wav_16bit(os.path.join(folder_path, fault_filename), generate_highly_differentiated_audio(cat, 2))

print("✅ 已完成全平台 6 大設備【正常 vs 警告 vs 嚴重故障】聽感特徵重構與 RMS 響度標準化！")