import numpy as np
import pandas as pd


def calculate_zscore_tanh(series, window=20, lam=2.0):
    rolling_mean = series.rolling(window).mean()
    rolling_std = series.rolling(window).std()
    z_score = (series - rolling_mean) / (rolling_std + 1e-6)
    return 100 * np.tanh(z_score / lam)


def compute_pvcs(df, w_p=0.35, w_v=0.25, w_c=0.40):
    data = df.copy()

    # P Score
    ma20 = data["Close"].rolling(20).mean()
    magap = (data["Close"] - ma20) / ma20
    roc20 = data["Close"].pct_change(20)
    return3d = data["Close"].pct_change(3)
    p_raw = 0.4 * magap + 0.3 * roc20 + 0.3 * return3d
    data["PScore"] = calculate_zscore_tanh(p_raw)

    # V Score
    vma20 = data["Volume"].rolling(20).mean()
    rvol = data["Volume"] / vma20
    pv_momentum = np.sign(data["Close"].pct_change()) * rvol
    v_raw = 0.5 * rvol + 0.5 * pv_momentum
    data["VScore"] = calculate_zscore_tanh(v_raw)

    # C Score
    c_raw = (
        data["Close"].pct_change() * data["Volume"]
    ).rolling(5).sum() / data["Volume"].rolling(5).sum()
    data["CScore"] = calculate_zscore_tanh(c_raw)

    # PVCS Base
    data["PVCS"] = (
        w_p * data["PScore"] + w_v * data["VScore"] + w_c * data["CScore"]
    )
    dispersion = np.std(
        data[["PScore", "VScore", "CScore"]].values, axis=1
    )
    data["Confidence"] = np.clip(100 * (1 - dispersion / 100), 0, 100)

    return data


def calculate_ic_weights(df):
    """保護機制：自動自適應資料長度計算 IC/ICIR 與動態權重"""
    data = df.copy()

    for h in [5, 20, 60]:
        data[f"ret_{h}d"] = data["Close"].shift(-h) / data["Close"] - 1

    horizon_weights = {}

    for h in [5, 20, 60]:
        ic_dict = {}
        icir_dict = {}

        for k, col in [
            ("P", "PScore"),
            ("V", "VScore"),
            ("C", "CScore"),
        ]:
            # 計算 Pearson 相關係數，若長度不足則預設基礎值
            valid_data = data[[col, f"ret_{h}d"]].dropna()
            if len(valid_data) > 30:
                corr_val = valid_data[col].corr(valid_data[f"ret_{h}d"])
                mean_ic = corr_val if not np.isnan(corr_val) else 0.05
            else:
                mean_ic = 0.05

            ic_dict[k] = mean_ic
            icir_dict[k] = mean_ic / 0.1  # 預設估算 ICIR

        raw_signals = {
            k: max(0.001, abs(ic_dict[k]) * icir_dict[k])
            for k in ["P", "V", "C"]
        }
        total_signal = sum(raw_signals.values())

        w_p = np.clip(raw_signals["P"] / total_signal, 0.20, 0.50)
        w_v = np.clip(raw_signals["V"] / total_signal, 0.10, 0.40)
        w_c = np.clip(raw_signals["C"] / total_signal, 0.25, 0.55)

        total_w = w_p + w_v + w_c
        horizon_weights[f"{h}D"] = {
            "w_p": w_p / total_w,
            "w_v": w_v / total_w,
            "w_c": w_c / total_w,
            "ic": ic_dict,
        }

    return horizon_weights


def compute_multi_horizon_pvcs(df):
    data = compute_pvcs(df)
    weights = calculate_ic_weights(data)

    for h in ["5D", "20D", "60D"]:
        w = weights[h]
        data[f"PVCS_{h}"] = (
            w["w_p"] * data["PScore"]
            + w["w_v"] * data["VScore"]
            + w["w_c"] * data["CScore"]
        )

    data["PVCS_Composite"] = (
        0.25 * data["PVCS_5D"]
        + 0.50 * data["PVCS_20D"]
        + 0.25 * data["PVCS_60D"]
    )

    return data, weights


def rule_engine(p, v, c, pvcs_20d):
    if p > 20 and v > 20 and c > 20:
        status = "強勢吸籌 / 三維一致"
        msg = "價格、量能與籌碼三維訊號高度一致偏多，多方結構完整。"
    elif c > 35 and p < 15:
        status = "籌碼沉澱卡位"
        msg = "價格尚未大漲，但籌碼面出現顯著買超，屬於進場卡位階段。"
    elif p > 30 and (v < -20 or c < -20):
        status = "價強實弱 (背離風險)"
        msg = "價格處於高點但量能或籌碼未同步，留意拉回風險。"
    elif p < -20 and c < -20:
        status = "空方結構確認"
        msg = "價格與籌碼同步偏弱，建議觀望。"
    else:
        status = "區間震盪整理"
        msg = "三維指標相互抵銷，市場無明確單向趨勢。"

    return {"status": status, "msg": msg}