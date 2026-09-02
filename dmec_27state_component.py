import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 1. 27 狀態碼映射與雙曲龐加萊圓盤座標轉換
# ==========================================
def calculate_27_state(
    c_val, f_val, p_val, c_thresh=1000, f_thresh=10.0, p_thresh=5.0
):
    """將連續變數 C, F, P 轉換為 +1, 0, -1 的 27 狀態碼，並計算雙曲龐加萊圓盤座標 (r, theta)"""
    # 軸位判定 (+1, 0, -1)
    c_code = 1 if c_val > c_thresh else (-1 if c_val < -c_thresh else 0)
    f_code = 1 if f_val > f_thresh else (-1 if f_val < -f_thresh else 0)
    p_code = 1 if p_val > p_thresh else (-1 if p_val < -p_thresh else 0)

    state_tuple = (c_code, f_code, p_code)

    # 27 狀態名稱地圖 (簡化版)
    state_names = {
        (1, 1, 1): "強勢同步 (+,+,+)",
        (1, 1, 0): "資金吸收 (+,+,0)",
        (1, 1, -1): "逆勢承接 (+,+,-)",
        (1, 0, 1): "籌碼先行 (+,0,+)",
        (1, 0, 0): "安靜累積 (+,0,0)",
        (1, 0, -1): "逆勢收籌 (+,0,-)",
        (0, 0, 0): "動態平衡 (0,0,0)",
        (-1, -1, 1): "強烈背離 (-,-,+)",
        (-1, -1, -1): "全面弱勢 (-,-,-)",
    }
    state_name = state_names.get(
        state_tuple, f"狀態碼 ({c_code},{f_code},{p_code})"
    )

    # 龐加萊極座標映射 (Poincaré Disk radius r, angle theta)
    # 距離中心點(0,0,0)越遠，代表極端狀態
    magnitude = np.sqrt(c_code**2 + f_code**2 + p_code**2) / np.sqrt(3)  # r in [0, 1)
    r = np.clip(
        magnitude * 0.85, 0.05, 0.9
    )  # 映射至龐加萊盤內部 (半徑限制 0.9 以內)

    # 角度 mapping (C: X軸, F: Y軸, P: Z軸映射角度)
    angle = (c_code * 45 + f_code * 90 + p_code * 135) % 360

    return state_tuple, state_name, r, angle


# ==========================================
# 2. 輕量化 27x27 轉移機率與數位分身 Q10/Q50/Q90 模擬器
# ==========================================
def simulate_digital_twin_paths(
    current_price, state_tuple, n_paths=1000, steps=10
):
    """模擬 Exchange Digital Twin 產生的 10,000 / 1,000 條未來價格路徑"""
    c, f, p = state_tuple

    # 漂移項 (Drift) 與 波動度 (Vol) 由 27 狀態決定
    drift = (c * 0.4 + f * 0.4 + p * 0.2) * 0.002
    volatility = 0.008 if (c == f == p) else 0.015  # 背離時波動較大

    np.random.seed(42)  # 固定隨機種子確保介面穩定
    dt = 1
    shocks = np.random.normal(0, volatility, (n_paths, steps))

    # 生成價格路徑
    price_paths = np.zeros((n_paths, steps + 1))
    price_paths[:, 0] = current_price

    for t in range(1, steps + 1):
        price_paths[:, t] = price_paths[:, t - 1] * np.exp(
            drift + shocks[:, t - 1]
        )

    # 計算 Q10, Q50, Q90 門檻區間
    q10 = np.percentile(price_paths, 10, axis=0)
    q50 = np.percentile(price_paths, 50, axis=0)
    q90 = np.percentile(price_paths, 90, axis=0)

    return q10, q50, q90, price_paths[:30, :]  # 傳回 30 條代表路徑畫圖


# ==========================================
# 3. Streamlit 展示介面渲染函數
# ==========================================
def render_dmec_27state_dashboard(current_price, c_val, f_val, p_val):
    st.subheader("🌐 DMEC 27 狀態碼與數位分身 (Digital Twin) 預測引擎")

    # 1. 計算狀態
    state_tuple, state_name, r, angle = calculate_27_state(
        c_val, f_val, p_val
    )
    q10, q50, q90, sample_paths = simulate_digital_twin_paths(
        current_price, state_tuple
    )

    # UI 第一列：PVCS 與 27 狀態碼升級顯示
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("當前 27 狀態碼 (S_t)", f"{state_tuple}")
    col2.metric("流場狀態名稱", f"{state_name}")
    col3.metric("Q50 中央預測價", f"${q50[-1]:.2f}", f"{q50[-1]-current_price:+.2f}")
    col4.metric(
        "Q10-Q90 風險區間", f"${q10[-1]:.2f} ~ ${q90[-1]:.2f}"
    )

    # UI 第二列：圖表呈現 (龐加萊圓盤狀態 + Q10/Q50/Q90 價格路徑圖)
    chart_col1, chart_col2 = st.columns([1, 1.5])

    with chart_col1:
        # 繪製雙曲龐加萊圓盤 (Poincaré Disk) 當前狀態點
        fig_poincare = go.Figure()

        # 畫邊界圓與幾何圓環
        theta_ring = np.linspace(0, 2 * np.pi, 100)
        fig_poincare.add_trace(
            go.Scatter(
                x=np.cos(theta_ring),
                y=np.sin(theta_ring),
                mode="lines",
                line=dict(color="gray", dash="dash"),
                showlegend=False,
            )
        )

        # 轉換當前極座標至 Cartesian
        rad = np.radians(angle)
        px, py = r * np.cos(rad), r * np.sin(rad)

        fig_poincare.add_trace(
            go.Scatter(
                x=[px],
                y=[py],
                mode="markers+text",
                marker=dict(size=16, color="red", symbol="diamond"),
                text=[f"S_t {state_tuple}"],
                textposition="top center",
                name="當前流場狀態",
            )
        )

        fig_poincare.update_layout(
            title="雙曲流形龐加萊狀態空間 (Poincaré Disk)",
            xaxis=dict(range=[-1.1, 1.1], visible=False),
            yaxis=dict(range=[-1.1, 1.1], visible=False),
            height=320,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_poincare, use_container_width=True)

    with chart_col2:
        # 繪製 Exchange Digital Twin 10,000 次模擬之 Q10/Q50/Q90 扇形圖
        steps = len(q50)
        x_axis = list(range(steps))

        fig_dt = go.Figure()

        # 畫 Q10-Q90 風險陰影區間
        fig_dt.add_trace(
            go.Scatter(
                x=x_axis + x_axis[::-1],
                y=np.concatenate([q90, q10[::-1]]),
                fill="toself",
                fillcolor="rgba(0, 176, 246, 0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                name="Q10-Q90 機率區間 (80% 覆蓋)",
            )
        )

        # 畫 Q50 中央路徑
        fig_dt.add_trace(
            go.Scatter(
                x=x_axis,
                y=q50,
                mode="lines+markers",
                line=dict(color="#00B0FF", width=3),
                name="Q50 數位分身撮合中央路徑",
            )
        )

        fig_dt.update_layout(
            title="數位分身 (Digital Twin) 未來 10 步價格路徑模擬 (Q10 / Q50 / Q90)",
            xaxis_title="未來時間步 (Steps)",
            yaxis_title="價格 (TWD)",
            height=320,
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(x=0.01, y=0.99),
        )
        st.plotly_chart(fig_dt, use_container_width=True)