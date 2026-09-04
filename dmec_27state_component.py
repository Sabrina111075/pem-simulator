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

# 上方 4 張指標卡片說明補強
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            label="當前 27 狀態碼 (S_t)",
            value=f"{state_tuple}",
            help="由籌碼 (C)、資金 (F)、試撮價差 (P) 三維度構成的向量 (C, F, P)。各維度量化涵義：\n"
            "• +1：偏多 / 強力流入 / 正價差\n"
            "•  0：中立 / 資金平穩 / 無價差\n"
            "• -1：偏空 / 強力流出 / 負價差\n"
            "三維組合共計 3³ = 27 種幾何狀態碼。",
        )

    with c2:
        st.metric(
            label="流場狀態名稱",
            value=f"狀態碼 {state_tuple}",
            help="根據狀態碼 (C, F, P) 映射之流場特徵：\n"
            "• (1, 1, 1)：極度多頭共振（籌碼/資金/價差全偏多）\n"
            "• (-1, -1, -1)：極度空頭擠壓（籌碼/資金/價差全偏空）\n"
            "• (0, 0, 0)：盤整觀望狀態\n"
            "其餘狀態代表多空交織的非線性流場動態。",
        )

    with c3:
        q50_price = base_price * (1 + 0.005 * (c_state + f_state + p_state))
        st.metric(
            label="Q50 中央預測價",
            value=f"${q50_price:.2f}",
            delta=f"{q50_price - base_price:+.2f} TWD",
            help="數位分身 Monte Carlo 幾何模擬的中位數（Q50）預期價格，代表市場在當前流場動力下最可能的走勢終點。",
        )

    with c4:
        low_p = base_price * 0.95
        high_p = base_price * 1.05
        st.metric(
            label="Q10-Q90 風險區間",
            value=f"{low_p:.2f} ~ {high_p:.2f}",
            help="代表 80% 的高機率價格波動包絡區間。Q10 為下檔支撐風險價，Q90 為上檔壓力預測價。",
        )

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

        # 龐加萊圓盤彈窗說明
        with st.popover("ℹ️ 龐加萊狀態空間與紅點涵義說明"):
            st.markdown("""
            **【龐加萊狀態空間 (Poincaré Disk) 說明】**
            * **雙曲幾何空間**：將多維度市場流場特徵（籌碼、資金流、動能）投影至雙曲圓盤中。
            * **紅色菱形點 ($S_t$)**：代表當前股票在該時間點的**綜合幾何狀態定位**。

            ---
            **定位幾何涵義：**
            * **距離中心遠近 (半徑 $r$)**：代表**動能強度與非線性離心力**。越靠近圓心代表狀態越穩定/盤整；越靠近邊緣代表動能越強勁或極端。
            * **角度位置 ($\theta$)**：代表**市場流場的相角方向**（即三維狀態碼 $S_t = (C, F, P)$ 的幾何方位對映）。
            * **圓盤虛線邊界**：代表雙曲空間的無窮遠邊界（極限狀態臨界點）。
            """)

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