import numpy as np
import plotly.graph_objects as go
import streamlit as st


# 1. 27 狀態碼判斷函數
def calculate_27_state(
    c_val, f_val, p_val, c_thresh=0.1, f_thresh=0.1, p_thresh=0.05
):
    c_code = 1 if c_val > c_thresh else (-1 if c_val < -c_thresh else 0)
    f_code = 1 if f_val > f_thresh else (-1 if f_val < -f_thresh else 0)
    p_code = 1 if p_val > p_thresh else (-1 if p_val < -p_thresh else 0)

    state_tuple = (c_code, f_code, p_code)
    state_names = {
        (1, 1, 1): "極度牛市 (1,1,1)",
        (0, 0, 0): "動態平衡 (0,0,0)",
        (-1, -1, -1): "極度熊市 (-1,-1,-1)",
    }
    name = state_names.get(state_tuple, f"狀態碼 {state_tuple}")
    return state_tuple, name


# 2. 數位分身 10 步價格路徑模擬
def simulate_digital_twin_paths(
    current_price, state_tuple, steps=10, n_sims=500
):
    c, f, p = state_tuple
    drift = (c * 0.4 + f * 0.4 + p * 0.2) * 0.005
    vol = 0.015

    dt = 1
    paths = np.zeros((n_sims, steps + 1))
    paths[:, 0] = current_price

    for t in range(1, steps + 1):
        z = np.random.standard_normal(n_sims)
        paths[:, t] = paths[:, t - 1] * np.exp(
            (drift - 0.5 * vol**2) * dt + vol * np.sqrt(dt) * z
        )

    q10 = np.percentile(paths, 10, axis=0)
    q50 = np.percentile(paths, 50, axis=0)
    q90 = np.percentile(paths, 90, axis=0)

    return q10, q50, q90


# 3. Streamlit 模組主渲染函數
def render_dmec_27state_dashboard(
    current_price=100.0, c_val=0.0, f_val=0.0, p_val=0.0, r_override=None
):
    # 確保價格非零與型態正確
    try:
        base_price = float(current_price)
        if base_price <= 0:
            base_price = 100.0
    except Exception:
        base_price = 100.0

    state_tuple, state_name = calculate_27_state(c_val, f_val, p_val)
    q10, q50, q90 = simulate_digital_twin_paths(base_price, state_tuple)

    pred_q50 = q50[-1]
    diff_val = pred_q50 - base_price

    # 頂部 4 個 Metric 卡片渲染
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("當前 27 狀態碼 (S_t)", f"{state_tuple}")
    with col2:
        st.metric("流場狀態名稱", f"{state_name}")
    with col3:
        st.metric(
            "Q50 中央預測價",
            f"${pred_q50:,.2f}",
            delta=f"{diff_val:+.2f} TWD",
        )
    with col4:
        st.metric(
            "Q10-Q90 風險區間",
            f"{q10[-1]:.2f} ~ {q90[-1]:.2f}",
        )

    # 下方雙圖表（Poincaré Disk 與 10 步模擬路徑）
    g1, g2 = st.columns(2)

    with g1:
        st.write("**龐加萊狀態空間 (Poincaré Disk)**")
        r_val = r_override if r_override is not None else 0.35
        theta = np.pi / 4 if sum(state_tuple) >= 0 else 5 * np.pi / 4

        fig_p = go.Figure()
        # 繪製外圓邊界
        t_arr = np.linspace(0, 2 * np.pi, 100)
        fig_p.add_trace(
            go.Scatter(
                x=np.cos(t_arr),
                y=np.sin(t_arr),
                mode="lines",
                line=dict(dash="dash", color="gray"),
                showlegend=False,
            )
        )
        # 繪製狀態點
        fig_p.add_trace(
            go.Scatter(
                x=[r_val * np.cos(theta)],
                y=[r_val * np.sin(theta)],
                mode="markers+text",
                text=[f"S_t {state_tuple}"],
                textposition="top center",
                marker=dict(size=14, color="red", symbol="diamond"),
                showlegend=False,
            )
        )
        fig_p.update_layout(
            xaxis=dict(range=[-1.1, 1.1], visible=False),
            yaxis=dict(range=[-1.1, 1.1], visible=False),
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_p, use_container_width=True)

    with g2:
        st.write("**數位分身 10 步價格模擬**")
        steps = np.arange(11)
        fig_s = go.Figure()

        # 90% 覆蓋區間
        fig_s.add_trace(
            go.Scatter(
                x=np.concatenate([steps, steps[::-1]]),
                y=np.concatenate([q90, q10[::-1]]),
                fill="toself",
                fillcolor="rgba(135, 206, 250, 0.3)",
                line=dict(color="rgba(255,255,255,0)"),
                name="Q10-Q90 80% 覆蓋區間",
            )
        )

        # Q50 路徑
        fig_s.add_trace(
            go.Scatter(
                x=steps,
                y=q50,
                mode="lines+markers",
                line=dict(color="#008080", width=3),
                name="Q50 數位分身預測路徑",
            )
        )

        fig_s.update_layout(
            xaxis_title="未來時間步 (Steps)",
            yaxis_title="價格 (TWD)",
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5
            ),
        )
        st.plotly_chart(fig_s, use_container_width=True)