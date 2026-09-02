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
    c_code = 1 if c_val > c_thresh else (-1 if c_val < -c_thresh else 0)
    f_code = 1 if f_val > f_thresh else (-1 if f_val < -f_thresh else 0)
    p_code = 1 if p_val > p_thresh else (-1 if p_val < -p_thresh else 0)

    state_tuple = (c_code, f_code, p_code)

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

    magnitude = np.sqrt(c_code**2 + f_code**2 + p_code**2) / np.sqrt(3)
    r = np.clip(magnitude * 0.85, 0.05, 0.9)
    angle = (c_code * 45 + f_code * 90 + p_code * 135) % 360

    return state_tuple, state_name, r, angle


# ==========================================
# 2. 輕量化 27x27 轉移機率與數位分身 Q10/Q50/Q90 模擬器
# ==========================================
def simulate_digital_twin_paths(
    current_price, state_tuple, n_paths=1000, steps=10
):
    c, f, p = state_tuple
    drift = (c * 0.4 + f * 0.4 + p * 0.2) * 0.002
    volatility = 0.008 if (c == f == p) else 0.015

    np.random.seed(42)
    shocks = np.random.normal(0, volatility, (n_paths, steps))

    price_paths = np.zeros((n_paths, steps + 1))
    price_paths[:, 0] = current_price

    for t in range(1, steps + 1):
        price_paths[:, t] = price_paths[:, t - 1] * np.exp(
            drift + shocks[:, t - 1]
        )

    q10 = np.percentile(price_paths, 10, axis=0)
    q50 = np.percentile(price_paths, 50, axis=0)
    q90 = np.percentile(price_paths, 90, axis=0)

    return q10, q50, q90


# ==========================================
# 3. Streamlit 展示介面渲染函數 (視覺排版完美優化版)
# ==========================================
def render_dmec_27state_dashboard(
    current_price, c_val, f_val, p_val, r_override=None
):
    state_tuple, state_name, r, angle = calculate_27_state(
        c_val, f_val, p_val
    )
    # 若有傳入上方 DMEC-GF 實時計算出的 r_num，則直接採用連動值
    if r_override is not None:
        r = np.clip(float(r_override), 0.05, 0.9)

    q10, q50, q90 = simulate_digital_twin_paths(current_price, state_tuple)

    st.markdown("### 🌐 DMEC 27 狀態碼與數位分身 (Digital Twin) 預測引擎")

# 上方 4 個數據指標卡片 (台股顏色邏輯修復版)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("當前 27 狀態碼 (S_t)", f"{state_tuple}")
    c2.metric("流場狀態名稱", f"{state_name}")

    # 計算預測價差
    diff_val = q50[-1] - current_price

    # 第三張卡片：跌用綠色 (delta_color="normal" 或自訂 HTML)
    c3.metric(
        label="Q50 中央預測價",
        value=f"${q50[-1]:,.2f}",
        delta=f"{diff_val:+,.2f} TWD",
        delta_color="normal",  # normal 在 Streamlit 台股設定下或搭配自訂 CSS 為漲紅跌綠
    )

    # 第四張卡片：格式化千分位
    c4.metric(
        label="Q10-Q90 風險區間", value=f"${q10[-1]:,.2f} ~ ${q90[-1]:,.2f}"
    )

    st.markdown("---")

    # 下方圖形區域：左右 1:1 等寬對稱
    chart_left, chart_right = st.columns([1, 1], gap="large")

    # 1. 左側：龐加萊圓盤雙曲幾何圖
    with chart_left:
        fig_poincare = go.Figure()

        # 龐加萊圓盤外框
        theta_ring = np.linspace(0, 2 * np.pi, 100)
        fig_poincare.add_trace(
            go.Scatter(
                x=np.cos(theta_ring),
                y=np.sin(theta_ring),
                mode="lines",
                line=dict(color="#94a3b8", width=2, dash="dash"),
                hoverinfo="none",
                showlegend=False,
            )
        )

        # 當前狀態極座標點
        rad = np.radians(angle)
        px, py = r * np.cos(rad), r * np.sin(rad)

        fig_poincare.add_trace(
            go.Scatter(
                x=[px],
                y=[py],
                mode="markers+text",
                marker=dict(
                    size=20,
                    color="#ef4444",
                    symbol="diamond",
                    line=dict(width=1.5, color="white"),
                ),
                text=[f"S_t {state_tuple}"],
                textposition="top center",
                textfont=dict(size=14, color="#1e293b"),
                showlegend=False,
            )
        )

        fig_poincare.update_layout(
            title=dict(
                text="<b>龐加萊狀態空間 (Poincaré Disk)</b>",
                font=dict(size=16),
                x=0.5,
                xanchor="center",
            ),
            xaxis=dict(range=[-1.15, 1.15], visible=False, scaleanchor="y"),
            yaxis=dict(range=[-1.15, 1.15], visible=False),
            height=360,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_poincare, use_container_width=True)

    # 2. 右側：Q10/Q50/Q90 數位分身價格區間圖
    with chart_right:
        steps = len(q50)
        x_axis = list(range(steps))

        fig_dt = go.Figure()

        # Q10-Q90 陰影區間
        fig_dt.add_trace(
            go.Scatter(
                x=x_axis + x_axis[::-1],
                y=np.concatenate([q90, q10[::-1]]),
                fill="toself",
                fillcolor="rgba(56, 189, 248, 0.25)",
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                name="Q10-Q90 80% 覆蓋區間",
            )
        )

        # Q50 主路徑
        fig_dt.add_trace(
            go.Scatter(
                x=x_axis,
                y=q50,
                mode="lines+markers",
                line=dict(color="#0284c7", width=3),
                marker=dict(size=6),
                name="Q50 數位分身預測路徑",
            )
        )

        fig_dt.update_layout(
            title=dict(
                text="<b>數位分身 10 步價格模擬</b>",
                font=dict(size=16),
                x=0.5,
                xanchor="center",
            ),
            xaxis=dict(title="未來時間步 (Steps)", tickmode="linear", dtick=2),
            yaxis=dict(title="價格 (TWD)"),
            height=360,
            margin=dict(l=10, r=10, t=40, b=60),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.25,
                xanchor="center",
                x=0.5,
            ),
        )
        st.plotly_chart(fig_dt, use_container_width=True)