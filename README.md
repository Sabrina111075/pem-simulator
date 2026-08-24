# GeodesicX：DMEC-GF 盤前幾何預測模擬平台

> **GeodesicX** 是一個結合 **微分幾何流形動力學 (Differential Geometry Manifold Dynamics)** 與 **時間序列 Foundation Models (TimesFM, Chronos-2, Moirai2, Lag-Llama)** 的次世代開盤前幾何預測與試撮模擬系統。

---

## 📌 系統核心理念

傳統模型常將市場價格視為單一純量時間序列，忽略了市場高維狀態間的耦合與結構性轉折。**GeodesicX** 將市場抽象化為高維狀態空間中的 **Market State Manifold ($\mathcal{M}$)**，並透過以下四層架構實現高精度的開盤預測：

1. **幾何狀態引擎 (DMEC-GF Engine)**：計算均衡偏離 $(E, V, A)$、局部度量張量 $g_{ij}$、幾何距離 $D_t$ 與軌跡曲率 $\kappa_t$，精準量化市場轉折風險 (Turning Risk)。
2. **盤前受力場模擬 (Pre-Market Force Field)**：在 08:30~08:59 區間引入盤前主力籌碼、試撮量能與期貨溢價作為外部受力向量 $u_t$。
3. **多模型路徑預測 (Multi-Model Forecasting Ensemble)**：結合 TimesFM (核心路徑)、Chronos-2 (多變量外生變數)、Moirai2 (狀態/Covariates) 與 Lag-Llama (機率分位數 Q10/Q50/Q90)。
4. **頂層語義與解釋層 (LLM Explanation Layer)**：透過 DeepSeek / Qwen 解釋多模型結果衝突，並結合事件與新聞生成盤前報告。

---

## 📐 核心數學骨架 (Mathematical Framework)

* **市場狀態座標**：$X_t = [E_t, V_t, A_t]^T \in \mathcal{M}$
* **馬氏幾何度量張量**：$g_t = (\Sigma_t + \lambda I)^{-1}$
* **結構性移動距離**：$D_t = \sqrt{\Delta X_t^T g_t \Delta X_t}$
* **市場受力方程**：$\frac{D\dot{X}}{Dt} = B u_t$ （$u_t$ 包含盤前籌碼 $NFS_t$、Macro、Sector 等）
* **測地線積分演化**：$\hat{X}_{t+H} = \text{GeodesicFlow}(X_t, \dot{X}_t, g_t, u_t)$
* **標準化趨勢分數**：$\text{TrendScore}_H = 100 \cdot \tanh\left(\frac{FTS_H^{GF}}{\lambda}\right) \in [-100, 100]$

---

## ⏱️ 08:30 ~ 08:59 盤前模擬工作流程

```text
[08:30 前] 讀取歷史日線與昨日結算資料 -> 計算 (E, V, A) 與局部度量張量 g_ij
   │
[08:30 - 08:59] 即時訂閱台指期、主力試撮與盤前籌碼 -> 算出一步外力分數 NFS_t
   │
 盤前受力推演 -> 求解測地線方程 (Geodesic Flow)
   ├── 傳入 Chronos-2 / Moirai2 做多變量外生變數推演
   └── 計算 Ensemble TrendScore、TurningRisk 與 Q10/Q50/Q90 價格機率區間
   │
 開盤驗證 -> 記錄極值偏差與滾動校正 Ensemble 權重 (Rolling Backtest)