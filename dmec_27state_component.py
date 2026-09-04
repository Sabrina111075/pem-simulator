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
    st.markdown("### ☒ DMEC 27 狀態碼與數位分身 (Digital Twin) 預測引擎"
    )
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

# --------------------------------------------------
    # 2. 龐加萊與數位分身雙圖表 (請注意此區塊行首皆有 4 個空白)
    # --------------------------------------------------
    g1, g2 = st.columns(2)

    with g1:
        st.write("**龐加萊狀態空間 (Poincaré Disk)**")
        st.plotly_chart(fig_p, use_container_width=True)

    with g2:
        st.write("**數位分身 10 步價格模擬**")

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