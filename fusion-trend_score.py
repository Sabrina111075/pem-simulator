import numpy as np

class TrendScoreFusion:
    def __init__(self, lambda_scale: float = 1.0):
        self.lambda_scale = lambda_scale

    def calculate_trend_score(
        self, 
        dmec_h: float, 
        geo_trend: float, 
        cycle_h: float, 
        chip_nfs: float,  # 08:30~08:59 主力/籌碼面算出的 Net Force Score[cite: 2]
        timesfm_h: float, 
        chronos_h: float,
        weights: dict = None
    ) -> tuple[float, float]:
        """
        計算 FTS_H^{GF} 與 Standardized TrendScore (-100 ~ 100)[cite: 2]
        """
        if weights is None:
            # 預設權重配置 (可動態回測微調)
            weights = {
                'DMEC': 0.20, 'Geo': 0.20, 'Cycle': 0.15, 
                'NFS': 0.15, 'TimesFM': 0.15, 'Chronos': 0.15
            }

        # 融合公式[cite: 2]
        fts_gf = (
            weights['DMEC'] * dmec_h +
            weights['Geo'] * geo_trend +
            weights['Cycle'] * cycle_h +
            weights['NFS'] * chip_nfs +
            weights['TimesFM'] * timesfm_h +
            weights['Chronos'] * chronos_h
        )

        # 映射至 [-100, 100][cite: 2]
        trend_score = 100.0 * np.tanh(fts_gf / self.lambda_scale)
        return fts_gf, float(trend_score)