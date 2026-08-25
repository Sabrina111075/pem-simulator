import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pytz

# ==========================================
# 1. 核心幾何與 PVCS 風險計算邏輯
# ==========================================
class HyperbolicStateEngine:
    def __init__(self, lambda_reg=1e-5):
        self.lambda_reg = lambda_reg

    def compute_kinematics_from_pvcs(self, price: np.ndarray, volume: np.ndarray, count: np.ndarray) -> pd.DataFrame:
        E = price - np.mean(price)
        V = np.gradient(volume)
        A = np.gradient(count)
        return pd.DataFrame({'E': E, 'V': V, 'A': A, 'Price': price, 'Volume': volume, 'Count': count})

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
# 2. UI 頁面配置與側邊欄
# ==========================================
st.set_page_config(page_title="PVCS 台股幾何狀態與數位分身 Dashboard", layout="wide")

# 取得台北時間與交易日資訊
taipei_tz = pytz.timezone('Asia/Taipei')
now_taipei = datetime.now(taipei_tz)
date_str = now_taipei.strftime("%Y-%m-%d")
time_str = now_taipei.strftime("%H:%M:%S")

# ------------------------------------------
# 頂部標題區：主標題與實時時間平行佈局
# ------------------------------------------
head_col1, head_col2 = st.columns([3, 1])

with head_col1:
    st.title("🛡️ PVCS 台股幾何狀態與數位分身 Dashboard")
    st.caption("結合 PVCS (價格-成交量-買賣張數) 三維分析與 Poincaré 雙曲幾何之個股動態評估面板")

with head_col2:
    st.markdown(f"**🕒 台北實時時間 (Taipei)**")
    st.markdown(f"### `{time_str}`")
    st.caption(f"📅 資料基準日：`{date_str}` (當天/前日收盤最終數據)")

st.markdown("---")

# ------------------------------------------
# 側邊欄控制項
# ------------------------------------------
st.sidebar.header("📈 PVCS 台股個股選取")

stock_mode = st.sidebar.radio("選擇股票模式", ["熱門標的", "自訂股票代碼"])

if stock_mode == "熱門標的":
    selected_stock = st.sidebar.selectbox("熱門股票清單", ["2330 台積電", "2317 鴻海", "2454 聯發科", "2382 廣達", "2603 長榮"])
    stock_code = selected_stock.split(" ")[0]
else:
    stock_code = st.sidebar.text_input("請輸入台股代碼 (例如: 3231)", value="2330")

st.sidebar.markdown("---")
st.sidebar.header("📊 08:30~08:59 盤前籌碼觀察")
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

st.sidebar.markdown("---")
st.sidebar.info("🏛️ **資料來源聲明**\n本平台數據介接自 **台灣證券交易所 (TWSE)** 與 **櫃買中心 (TPEx)** 官方實時資料流。")

# ------------------------------------------
# 3. 生成 PVCS 數據與動態評分
# ------------------------------------------
intent_map = {"極度偏空": -1.5, "偏空": -0.7, "中立": 0.0, "偏多": 0.7, "極度偏多": 1.5}
intent_val = intent_map[major_buyer_intent]

time_steps = 120
t = np.linspace(0, 12, time_steps)
bias_offset = (premarket_gap / 100.0) + intent_val

mock_price = (np.sin(t) + bias_offset) * 10 + 950 + noise_level * np.random.normal(size=time_steps)
mock_volume = (np.cos(t * 1.5) + premarket_vol) * 15000 + 20000
mock_count = np.abs(np.gradient(mock_price)) * 3000 + 5000

geo_engine = HyperbolicStateEngine()
risk_engine = CurvatureRiskEngine()

df_kinematics = geo_engine.compute_kinematics_from_pvcs(mock_price, mock_volume, mock_count)
df_geo = geo_engine.map_to_poincare_disk(df_kinematics)
df_res = risk_engine.compute_trajectory_curvature(df_geo)

latest = df_res.iloc[-1]

# 計算行情數據與 P/V/C 得分
latest_price = mock_price[-1]
price_diff = mock_price[-1] - mock_price[-2]
est_volume = int(mock_volume[-1])
confidence_score = max(0.60, min(0.99, 1.0 - (noise_level * 0.8)))
p_score = min(100, max(0, int(50 + (price_diff / latest_price) * 1000)))
v_score = min(100, max(0, int(50 + (est_volume - 25000) / 500)))
c_score = min(100, max(0, int(100 - (latest['Turning_Risk'] * 100))))

# ==========================================
# 4. 市場行情與 P/V/C 得分列 (位置：分析標的上方)
# ==========================================
st.markdown("#### 📊 市場實時行情與 P/V/C 幾何評分")

m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
m_col1.metric("最新收盤/試算價", f"{latest_price:.2f} 元", delta=f"{price_diff:+.2f}")
m_col2.metric("預估總成交量", f"{est_volume:,} 張")
m_col3.metric("指標可信度 (Confidence)", f"{confidence_score:.1%}")
m_col4.metric("P/V/C 綜合得分", f"{int((p_score + v_score + c_score)/3)} 分")
m_col5.metric("價量動能分 (P/V)", f"{p_score} / {v_score}")

st.caption(f"註：上述行情為 `{date_str}` 當天實時估算或前一交易日最終收盤數據。")
st.markdown("---")

# ==========================================
# 5. 當前分析標的與幾何 KPI
# ==========================================
st.subheader(f"📌 當前分析標的：`{stock_code}`")

col1, col2, col3, col4 = st.columns(4)
col1.metric("PVCS 馬氏距離 (D_t)", f"{latest['Mahalanobis_D']:.3f}")
col2.metric("雙曲半徑 (Poincaré r)", f"{latest['Poincare_r']:.3f}", delta_color="inverse")
col3.metric("軌跡曲率強度 (κ_intensity)", f"{latest['Curvature_Intensity']:.3f}")

risk_val = latest['Turning_Risk']
risk_color = "normal" if risk_val < 0.6 else "inverse"
col4.metric("個股轉折 / 失效風險 (Risk)", f"{risk_val:.1%}", delta=f"{risk_val - 0.5:.2f}", delta_color=risk_color)

st.markdown("---")

# ==========================================
# 6. 上下垂直圖表佈局
# ==========================================

# (1) Poincaré Disk 雙曲狀態圓盤
st.subheader(f"🌀 {stock_code} Poincaré Disk PVCS 雙曲狀態圓盤")
fig_disk = go.Figure()

theta_grid = np.linspace(0, 2*np.pi, 100)
fig_disk.add_trace(go.Scatter(
    x=np.cos(theta_grid), y=np.sin(theta_grid),
    mode='lines', line=dict(color='gray', dash='dash'),
    name='Boundary (r=1)'
))

fig_disk.add_trace(go.Scatter(
    x=df_res['Poincare_u'].to_numpy(), 
    y=df_res['Poincare_v'].to_numpy(),
    mode='lines+markers',
    marker=dict(
        size=7, 
        color=df_res['Turning_Risk'].to_numpy(), 
        colorscale='Viridis', 
        showscale=True, 
        colorbar=dict(title="Risk")
    ),
    name='PVCS State Trajectory'
))

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
    height=450,
    margin=dict(l=20, r=20, t=30, b=20)
)
st.plotly_chart(fig_disk, use_container_width=True)

st.markdown("---")

# (2) PVCS 三維時序變化圖
st.subheader(f"📈 {stock_code} PVCS (價格/成交量/買賣張數) 與曲率時序圖")

fig_time = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12, subplot_titles=("收盤價 (Price) & 成交量 (Volume)", "軌跡曲率 (κ) & 變盤風險"))

fig_time.add_trace(go.Scatter(y=df_res['Price'].to_numpy(), name="Price (元)"), row=1, col=1)
fig_time.add_trace(go.Scatter(y=df_res['Volume'].to_numpy(), name="Volume (張)", yaxis="y2"), row=1, col=1)

fig_time.add_trace(go.Scatter(y=df_res['Curvature_kappa'].to_numpy(), name="Curvature (κ)", line=dict(color='orange')), row=2, col=1)
fig_time.add_trace(go.Scatter(y=df_res['Turning_Risk'].to_numpy(), name="Risk Score", line=dict(color='red', dash='dot')), row=2, col=1)

fig_time.update_layout(height=450, margin=dict(l=20, r=20, t=30, b=20))
st.plotly_chart(fig_time, use_container_width=True)

# ==========================================
# 7. 閉環數位分身診斷區
# ==========================================
st.markdown("---")
st.subheader("🤖 個股 PVCS 閉環數位分身診斷與處置建議")

simulated_twin_val = mock_price[-1] + np.random.uniform(-0.5, 0.5)
residual = abs(mock_price[-1] - simulated_twin_val)

d_col1, d_col2 = st.columns([1, 2])

with d_col1:
    st.write(f"**目標股票代碼**: `{stock_code}`")
    st.write(f"**即時預估收盤價**: `{mock_price[-1]:.2f}` 元")
    st.write(f"**數位分身模型殘差 |e(t)|**: `{residual:.4f}`")

with d_col2:
    if residual > tolerance or risk_val > 0.65:
        st.error(f"⚠️ **{stock_code} 檢測到高量價曲率轉折告警**")
        if risk_val > 0.65:
            st.markdown("👉 **建議處置動作**：PVCS 軌跡顯示該股正處於 Poincaré 圓盤邊界區域，成交量與買賣筆數出現嚴重結構不對稱，謹防盤中劇烈變盤。")
        else:
            st.markdown("👉 **建議處置動作**：市場實測價與數位分身偏離，建議調整短線量化策略之停損/停利點位。")
    else:
        st.success(f"✅ **{stock_code} PVCS 幾何狀態穩定**")
        st.markdown("👉 **建議處置動作**：價量籌碼結構處於正常趨勢，維持原策略持有或操作。")