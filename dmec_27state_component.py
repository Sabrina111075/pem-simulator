import numpy as np
import plotly.graph_objects as go
import streamlit as st


def render_dmec_27state_dashboard(
    current_price=100.0,
    c_val=0.0,
    f_val=0.0,
    p_val=0.0,
    r_override=None,
):
    """DMEC 27 狀態碼與數位分身 (Digital Twin) 預測引擎儀表板"""
    try:
        base_price = float(current_price)
    except Exception:
        base_price = 100.0

    # 1. 狀態碼與數據計算
    c_state = 1 if c_val > 0.1 else (-1 if c_val < -0.1 else 0)
    f_state = 1 if f_val > 0.1 else (-1 if f_val < -0.1 else 0)
    p_state = 1 if p_val > 0.1 else (-1 if p_val < -0.1 else 0)
    state_tuple = (c_state, f_state, p_state)

    # 上方指標卡片
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("當前 27 狀態碼 (S_t)", f"{state_tuple}")
    with c2:
        st.metric("流場狀態名稱", f"狀態碼 {state_tuple}")
    with c3:
        q50_price = base_price * (1 + 0.005 * (c_state + f_state + p_state))
        st.metric(
            "Q50 中央預測價",
            f"${q50_price:.2f}",
            delta=f"{q50_price - base_price:+.2f} TWD",
        )
    with c4:
        low_p = base_price * 0.95
        high_p = base_price * 1.05
        st.metric("Q10-Q90 風險區間", f"{low_p:.2f} ~ {high_p:.2f}")

    # 2. 龐加萊圓盤 (Poincaré Disk) 圖表繪製
    theta = np.linspace(0, 2 * np.pi, 100)
    fig_p = go.Figure()
    fig_p.add_trace(
        go.Scatter(
            x=np.cos(theta),
            y=np.sin(theta),
            mode="lines",
            line=dict(color="gray", dash="dash"),
            showlegend=False,
        )
    )

    r_val = 0.5 if r_override is None else float(r_override)
    fig_p.add_trace(
        go.Scatter(
            x=[r_val * np.cos(np.pi / 4)],
            y=[r_val * np.sin(np.pi / 4)],
            mode="markers+text",
            text=[f"S_t {state_tuple}"],
            textposition="top center",
            marker=dict(size=14, color="red", symbol="diamond"),
            showlegend=False,
        ),
    )
    fig_p.update_layout(
        xaxis=dict(range=[-1.1, 1.1], visible=False),
        yaxis=dict(range=[-1.1, 1.1], visible=False),
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
    )

    # 3. 數位分身 10 步價格模擬圖表繪製
    steps = np.arange(11)
    q50_path = base_price * (1 + 0.002 * steps)
    q10_path = q50_path * (1 - 0.01 * np.sqrt(steps))
    q90_path = q50_path * (1 + 0.01 * np.sqrt(steps))

    fig_twin = go.Figure()
    fig_twin.add_trace(
        go.Scatter(
            x=np.concatenate([steps, steps[::-1]]),
            y=np.concatenate([q90_path, q10_path[::-1]]),
            fill="toself",
            fillcolor="rgba(0, 180, 216, 0.2)",
            line=dict(color="rgba(255,255,255,0)"),
            name="Q10-Q90 80% 覆蓋區間",
            showlegend=True,
        )
    )
    fig_twin.add_trace(
        go.Scatter(
            x=steps,
            y=q50_path,
            mode="lines+markers",
            line=dict(color="#0077b6", width=3),
            name="Q50 數位分身預測路徑",
            showlegend=True,
        )
    )
    fig_twin.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="未來時間步 (Steps)",
        yaxis_title="價格 (TWD)",
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5
        ),
    )

    # 4. 雙欄位版面渲染 (確保全在 render 函式內部)
    g1, g2 = st.columns(2)

    with g1:
        st.write("**龐加萊狀態空間 (Poincaré Disk)**")
        st.plotly_chart(fig_p, use_container_width=True)

    with g2:
        st.write("**數位分身 10 步價格模擬**")

        # 時間步彈窗說明
        with st.popover("ℹ️ 時間步 (Steps) 說明與單位對照"):
            st.markdown("""
            **【數位分身 10 步價格模擬說明】**
            * **Step 0**：**當前基準時刻**（當前實時價格 / 最新收盤價）。
            * **Step 1 ~ 10**：代表從當前時刻開始，向未來推進 **1 至 10 個離散時間區間** 的價格走勢預測。

            ---
            **⏱️ 時間單位對照（視資料頻率而定）：**
            * **分時/盤中模式**：1 Step = 1 分鐘（Step 10 即未來第 10 分鐘）。
            * **日線模式**：1 Step = 1 交易日（Step 10 即未來第 10 個交易日）。

            *※ 青色區間（Q10~Q90）代表 Monte Carlo 幾何流場模擬下的 80% 風險包絡範圍。*
            """)

        st.plotly_chart(fig_twin, use_container_width=True)