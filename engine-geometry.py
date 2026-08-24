import numpy as np

class MarketGeometryEngine:
    def __init__(self, lambda_reg: float = 1e-4):
        self.lambda_reg = lambda_reg

    def compute_metric_tensor(self, X_window: np.ndarray) -> np.ndarray:
        """
        計算局部度量張量 g_t = (Sigma_t + lambda * I)^(-1)
        X_window shape: (L, 3) -> 包含 (E, V, A) 序列
        """
        cov = np.cov(X_window, rowvar=False)
        metric = np.linalg.inv(cov + self.lambda_reg * np.eye(3))
        return metric

    def compute_distance(self, dX: np.ndarray, g_t: np.ndarray) -> float:
        """計算一步幾何距離 D_t = sqrt(dX^T * g_t * dX)"""
        return float(np.sqrt(np.dot(dX.T, np.dot(g_t, dX))))

    def compute_curvature(self, dX: np.ndarray, d2X: np.ndarray, eps: float = 1e-6) -> float:
        """
        計算三維路徑離散曲率 kappa_t = ||dX x d2X|| / (||dX||^3 + eps)[cite: 2]
        """
        cross_prod = np.cross(dX, d2X)
        norm_cross = np.linalg.norm(cross_prod)
        norm_dX = np.linalg.norm(dX)
        return float(norm_cross / (norm_dX**3 + eps))

    def compute_turning_risk(self, curvature: float, distance: float, geo_acc: float, alpha: list = [0.4, 0.3, 0.3]) -> float:
        """
        透過 Sigmoid 輸出 0~1 的轉折風險[cite: 2]
        """
        z = alpha[0] * curvature + alpha[1] * distance + alpha[2] * abs(geo_acc)
        return float(1.0 / (1.0 + np.exp(-z)))