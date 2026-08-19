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


def calculate_ic_weights(df, lookback=252):
    data = df.tail(lookback + 60).copy()
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
            rolling_ic = (
                data[col]
                .rolling(60)
                .corr(data[f"ret_{h}d"])
                .dropna()
            )
            mean_ic = rolling_ic.mean() if len(rolling_ic) > 0 else 0.01
            std_ic = rolling_ic.std() if len(rolling_ic) > 0 else 1.0
            ic_dict[k] = mean_ic
            icir_dict[k] = mean_ic / (std_ic + 1e-6)

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
    """進階規則引擎：包含價量/籌碼背離預警與狀態說明"""
    divergence_type = "無背離"
    risk_level = "低"

    # 背離偵測邏輯
    if p > 30 and (v < -20 or c < -20):
        divergence_type = "高檔背離警報"
        risk_level = "高"
        status = "價強實弱 (背離風險)"
        msg = "價格創高或處於高點，但量能或籌碼未同步配合，需留意高檔拉回或主力出貨風險。"
    elif p < -30 and (v > 20 or c > 20):
        divergence_type = "低檔背離訊號"
        risk_level = "中"
        status = "低檔轉強 (築底訊號)"
        msg = "價格處於低檔，但籌碼或量能已先行回溫，可能為主力逢低佈局跡象。"
    elif p > 20 and v > 20 and c > 20:
        status = "強勢吸籌 / 三維一致"
        msg = "價格、量能與籌碼三維訊號高度一致偏多，多方結構完整。"
    elif c > 35 and p < 15:
        status = "籌碼沉澱卡位"
        msg = "價格尚未大漲，但籌碼面出現顯著買超，屬於進場卡位階段。"
    elif p < -20 and c < -20:
        status = "空方結構確認"
        msg = "價格與籌碼同步偏弱，多頭動能不足，建議觀望。"
    else:
        status = "區間震盪整理"
        msg = "三維指標相互抵銷，市場無明確單向趨勢，建議以區間視之。"

    return {
        "status": status,
        "msg": msg,
        "divergence": divergence_type,
        "risk": risk_level,
    }