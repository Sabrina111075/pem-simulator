import numpy as np
import pandas as pd


def calculate_ic_weights(df, lookback=252):
    """根據個股過去 252 日歷史資料，動態計算 5D/20D/60D 的 IC、ICIR 與專屬權重"""
    data = df.tail(lookback + 60).copy()

    # 計算未來 Forward Returns (5D, 20D, 60D)
    for h in [5, 20, 60]:
        data[f"ret_{h}d"] = data["Close"].shift(-h) / data["Close"] - 1

    horizons = [5, 20, 60]
    horizon_weights = {}

    for h in horizons:
        ic_dict = {}
        icir_dict = {}

        for k, col in [
            ("P", "PScore"),
            ("V", "VScore"),
            ("C", "CScore"),
        ]:
            # 滾動計算每日 IC
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

        # 訊號強度 WeightSignal = |IC| * ICIR
        raw_signals = {
            k: max(0.001, abs(ic_dict[k]) * icir_dict[k])
            for k in ["P", "V", "C"]
        }
        total_signal = sum(raw_signals.values())

        # 原始比例分配
        w_p = raw_signals["P"] / total_signal
        w_v = raw_signals["V"] / total_signal
        w_c = raw_signals["C"] / total_signal

        # 加入上下限約束 Constraint
        w_p = np.clip(w_p, 0.20, 0.50)
        w_v = np.clip(w_v, 0.10, 0.40)
        w_c = np.clip(w_c, 0.25, 0.55)

        # 再次歸一化確保 sum = 1
        total_w = w_p + w_v + w_c
        horizon_weights[f"{h}D"] = {
            "w_p": w_p / total_w,
            "w_v": w_v / total_w,
            "w_c": w_c / total_w,
            "ic": ic_dict,
        }

    return horizon_weights


def compute_multi_horizon_pvcs(df):
    """計算包含 5D, 20D, 60D 的多時間尺度動態 PVCS"""
    # 1. 基礎指標計算 (維持原有 PScore, VScore, CScore)
    data = compute_pvcs(
        df
    )  # 呼叫之前寫好的基本 compute_pvcs 算出基礎 P/V/C 分數

    # 2. 個股歷史 IC/ICIR 動態權重校準
    weights = calculate_ic_weights(data)

    # 3. 計算三個 Horizon 的專屬 PVCS
    for h in ["5D", "20D", "60D"]:
        w = weights[h]
        data[f"PVCS_{h}"] = (
            w["w_p"] * data["PScore"]
            + w["w_v"] * data["VScore"]
            + w["w_c"] * data["CScore"]
        )

    # 4. Composite 綜合分數 (25% 5D + 50% 20D + 25% 60D)
    data["PVCS_Composite"] = (
        0.25 * data["PVCS_5D"]
        + 0.50 * data["PVCS_20D"]
        + 0.25 * data["PVCS_60D"]
    )

    return data, weights