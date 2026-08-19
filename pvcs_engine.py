import numpy as np
import pandas as pd


def calculate_zscore_tanh(series, window=20, lam=2.0):
    """Z-score + tanh 軟性壓縮至 [-100, +100]"""
    rolling_mean = series.rolling(window).mean()
    rolling_std = series.rolling(window).std()
    z_score = (series - rolling_mean) / (rolling_std + 1e-6)
    score = 100 * np.tanh(z_score / lam)
    return score


def compute_pvcs(df, w_p=0.35, w_v=0.25, w_c=0.40):
    """計算 Price, Volume, Chip 與 PVCS 綜合分數

    註：Chip 部分在沒有付費籌碼 API 時，可用內盤/外盤估算或三大法人模擬替代
    """
    data = df.copy()

    # --- 1. Price Score (P) ---
    ma20 = data["Close"].rolling(20).mean()
    magap = (data["Close"] - ma20) / ma20
    roc20 = data["Close"].pct_change(20)
    return3d = data["Close"].pct_change(3)

    p_raw = 0.4 * magap + 0.3 * roc20 + 0.3 * return3d
    data["PScore"] = calculate_zscore_tanh(p_raw)

    # --- 2. Volume Score (V) ---
    vma20 = data["Volume"].rolling(20).mean()
    rvol = data["Volume"] / vma20
    # 簡易量價動能
    pv_momentum = np.sign(data["Close"].pct_change()) * rvol

    v_raw = 0.5 * rvol + 0.5 * pv_momentum
    data["VScore"] = calculate_zscore_tanh(v_raw)

    # --- 3. Chip Score (C) [範例以量價關係模擬籌碼力道] ---
    # 若有真實籌碼資料可更換為外資/投信買賣超
    c_raw = (
        data["Close"].pct_change() * data["Volume"]
    ).rolling(5).sum() / data["Volume"].rolling(5).sum()
    data["CScore"] = calculate_zscore_tanh(c_raw)

    # --- 4. PVCS 綜合分數與信心度 ---
    data["PVCS"] = (
        w_p * data["PScore"] + w_v * data["VScore"] + w_c * data["CScore"]
    )

    # 計算三維一致性 (Agreement) 帶出 Confidence
    dispersion = np.std(
        data[["PScore", "VScore", "CScore"]].values, axis=1
    )
    data["Confidence"] = np.clip(100 * (1 - dispersion / 100), 0, 100)

    return data


def rule_engine(p, v, c, pvcs):
    """規則引擎：輸出市場狀態"""
    if p > 30 and v > 30 and c > 30:
        return "強勢吸籌 / 三維一致偏多", "多方結構完整，量能與籌碼同步配合。"
    elif c > 40 and p < 10:
        return "籌碼累積階段", "價格尚未發動，但籌碼已有主力卡位跡象。"
    elif p > 50 and (v < -20 or c < -20):
        return "價量籌碼背離預警", "價格創高但籌碼或量能未跟上，需注意高檔拉回風險。"
    elif p < -30 and c < -30:
        return "空方趨勢確認", "價格與籌碼同步弱勢，建議觀望。"
    else:
        return "區間震盪整理", "三維訊號分歧，市場處於盤整狀態。"