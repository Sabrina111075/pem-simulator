import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. 核心幾何與風險計算邏輯
# ==========================================
class HyperbolicStateEngine:
    def __init__(self, lambda_reg=1e-5):
        self.lambda_reg = lambda_reg

    def compute_kinematics(self, data_series: np.ndarray) -> pd.DataFrame:
        E = data_series - np.mean(data_series)
        V = np.gradient(E)
        A = np.gradient(V)
        return pd.DataFrame({'E': E, 'V': V, 'A': A})

    def map_to_poincare_disk(self, df_kinematics: pd.DataFrame):
        X = df_kinematics[['E', 'V', 'A']].values
        N, D = X.shape
        cov_matrix = np.cov(X.T) + self.lambda_reg * np.eye(D)
        inv_cov = np.linalg.inv(cov_matrix)
        
        mahalanobis_dists = np.sqrt(np.sum((X @ inv_cov) * X, axis=1))
        r = np.tanh(mahalanobis_dists / 2.0)
        theta = np.arctan2(df_kinematics['V'].values, df_kinematics['E'].values)
        
        u = r * np.cos(theta)
        v = r * np.sin(theta)
        
        res_df = df_kinematics.copy()
        res_df['Mahalanobis_D'] = mahalanobis_dists
        res_df['Poincare_r'] = r
        res_df['Poincare_u'] = u
        res_df['Poincare_v'] = v
        return res_df

class CurvatureRiskEngine:
    @staticmethod
    def compute_trajectory_curvature(df_geo: pd.DataFrame) -> pd.DataFrame:
        u = df_geo['Poincare_u'].to_numpy()
        v = df_geo['Poincare_v'].to_numpy()
        
        du = np.gradient(u)
        dv = np.gradient(v)
        d2u = np.gradient(du)
        d2v = np.gradient(dv)
        
        path_length = np.cumsum(np.sqrt(du**2 + dv**2))
        
        numerator = np.abs(du * d2v - dv * d2u)
        denominator = (du**2 + dv**2)**(1.5) + 1e-8
        curvature = numerator / denominator
        
        z_kappa = (curvature - np.mean(curvature)) / (np.std(curvature) + 1e-8)
        curvature_intensity = np.tanh(np.abs(z_kappa))
        
        r = df_geo['Poincare_r'].to_numpy()
        turning_risk = 1.0 / (1.0 + np.exp(-(1.5 * r + 2.0 * curvature_intensity - 1.5)))
        
        res_df = df_geo.copy()
        res_df['Path_Length_L'] = path_length
        res_df['Curvature_kappa'] = curvature
        res_df['Curvature_Intensity'] = curvature_intensity
        res_df['Turning_Risk'] = turning_risk
        return res_df

# ==========================================
# 2. Streamlit UI 頁面配置與控制項
# ==========================================
st.set_page_config(page_title="幾何狀態與數位分身 Dashboard", layout="wide")

st.title("🛡️ 幾何狀態監控與閉環數位分身 Dashboard")
st.caption("基於 Poincaré 雙曲幾何與軌跡曲率之系統狀態動態評估面板")

# ------------------------------------------
# 側邊欄控制項 (加入 08:30~08:59 盤前籌碼區間)
# ------------------------------------------
st.sidebar.header("📊 08:30~08:59 盤前籌碼與大盤觀察")

premarket_gap = st.sidebar.slider("盤前試撮 / 夜盤價差 (點/%)", -150, 150, 25, 5)
major_buyer_intent = st.sidebar.select_slider(
    "主力籌碼意向 (Major Intent)",
    options=["極度偏空", "偏空", "中立", "偏多", "極度偏多"],
    value="偏多"
)
premarket_vol = st.sidebar.slider("盤前預估量放量程度", 0.5, 3.0, 1.2, 0.1)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 幾何與數位分身參數")
noise_level = st.sidebar.slider("訊號雜訊強度 (Noise)", 0.0, 0.5, 0.15, 0.05)
tolerance = st.sidebar.slider("閉環預警殘差閾值 (Tolerance)", 0.05, 0.5, 0.2, 0.05)

# 將籌碼意向轉換為數值權重
intent_map = {"極度偏空": -1.5, "偏空": -0.7, "中立": 0.0, "偏多": 0.7, "極度偏多": 1.5}
intent_val = intent_map[major_buyer_intent]

# 生成受盤前籌碼影響的動態模擬數據流
time_steps = 120
t = np.linspace(0, 12, time_steps)
bias_offset = (premarket_gap / 100.0) + intent_val
raw_signal = (np.sin(t) + bias_offset) * premarket_vol + noise_level * np.random.normal(size=time_steps)

# 執行引擎計算
geo_engine = HyperbolicStateEngine()
risk_engine = CurvatureRiskEngine()

df_kinematics = geo_engine.compute_kinematics(raw_signal)
df_geo = geo_engine.map_to_poincare_disk(df_kinematics)
df_res = risk_engine.compute_trajectory_curvature(df_geo)

latest = df_res.iloc[-1]

# ==========================================
# 3. 頂部 KPI 儀表卡片
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("馬氏幾何距離 (D_t)", f"{latest['Mahalanobis_D']:.3f}")
col2.metric("雙曲半徑 (Poincaré r)", f"{latest['Poincare_r']:.3f}", delta_color="inverse")
col3.metric("軌跡曲率強度 (κ_intensity)", f"{latest['Curvature_Intensity']:.3f}")

risk_val = latest['Turning_Risk']
risk_color = "normal" if risk_val < 0.6 else "inverse"
col4.metric("轉折 / 失效風險 (Risk)", f"{risk_val:.1%}", delta=f"{risk_val - 0.5:.2f}", delta_color=risk_color)

st.markdown("---")

# ==========================================
# 4. 主圖表繪製 (Poincaré Disk + 時序圖)
# ==========================================
left_chart, right_chart = st.columns([1, 1])

with left_chart:
    st.subheader("🌀 Poincaré Disk 雙曲狀態圓盤")
    
    fig_disk = go.Figure()

    # 繪製單位圓 (Boundary r=1)
    theta_grid = np.linspace(0, 2*np.pi, 100)
    fig_disk.add_trace(go.Scatter(
        x=np.cos(theta_grid), y=np.sin(theta_grid),
        mode='lines', line=dict(color='gray', dash='dash'),
        name='Boundary (r=1)'
    ))

    # 繪製軌跡線 (使用 .to_numpy() 確保傳輸型別穩定)
    fig_disk.add_trace(go.Scatter(
        x=df_res['Poincare_u'].to_numpy(), 
        y=df_res['Poincare_v'].to_numpy(),
        mode='lines+markers',
        marker=dict(
            size=6, 
            color=df_res['Turning_Risk'].to_numpy(), 
            colorscale='Viridis', 
            showscale=True, 
            colorbar=dict(title="Risk")
        ),
        name='State Trajectory'
    ))

    # 標示最新狀態點
    fig_disk.add_trace(go.Scatter(
        x=[float(latest['Poincare_u'])], 
        y=[float(latest['Poincare_v'])],
        mode='markers', 
        marker=dict(size=14, color='red', symbol='x'),
        name='Current State'
    ))

    fig_disk.update_layout(
        xaxis=dict(range=[-1.1, 1.1], constrain='domain'),
        yaxis=dict(range=[-1.1, 1.1], scaleanchor="x", scaleratio=1),
        width=500, height=500,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_disk, use_container_width=True)

with right_chart:
    st.subheader("📈 狀態運動學與曲率變化")
    
    fig_time = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=("偏離 (E) & 速度 (V)", "軌跡曲率 (κ) & 風險"))

    # 偏離與速度
    fig_time.add_trace(go.Scatter(y=df_res['E'].to_numpy(), name="E (Dev)"), row=1, col=1)
    fig_time.add_trace(go.Scatter(y=df_res['V'].to_numpy(), name="V (Vel)"), row=1, col=1)

    # 曲率與風險
    fig_time.add_trace(go.Scatter(y=df_res['Curvature_kappa'].to_numpy(), name="Curvature (κ)", line=dict(color='orange')), row=2, col=1)
    fig_time.add_trace(go.Scatter(y=df_res['Turning_Risk'].to_numpy(), name="Risk Score", line=dict(color='red', dash='dot')), row=2, col=1)

    fig_time.update_layout(height=500, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_time, use_container_width=True)

# ==========================================
# 5. 閉環數位分身診斷區
# ==========================================
st.subheader("🤖 盤前籌碼評估與閉環處置建議")

# 模擬數位分身與實體殘差
simulated_twin_val = raw_signal[-1] + np.random.uniform(-0.3, 0.3)
residual = abs(raw_signal[-1] - simulated_twin_val)

d_col1, d_col2 = st.columns([1, 2])

with d_col1:
    st.write(f"**盤前價差權重**: `{bias_offset:+.2f}`")
    st.write(f"**主力籌碼設定**: `{major_buyer_intent}`")
    st.write(f"**模型殘差 |e(t)|**: `{residual:.4f}`")

with d_col2:
    if residual > tolerance or risk_val > 0.65:
        st.error("⚠️ **盤前狀態異常 / 轉折偏離告警**")
        if risk_val > 0.65:
            st.markdown("👉 **建議處置動作**：盤前試撮與主力意向顯示市場軌跡曲率偏高，預警開盤後可能發生劇烈轉折 (Regime Change)，建議降低開盤避險槓桿。")
        else:
            st.markdown("👉 **建議處置動作**：殘差高於預期，建議對盤前開盤模型進行線上參數 recalibration。")
    else:
        st.success("✅ **盤前開盤幾何狀態穩定**")
        st.markdown("👉 **建議處置動作**：開盤動能與主力方向一致，維持當前開盤策略部署。")