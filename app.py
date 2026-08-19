# 在 app.py 點擊「開始分析」後的渲染邏輯中替換為：

res, weights = compute_multi_horizon_pvcs(df)
latest = res.iloc[-1]

st.success("分析完成！個股專屬動態權重校準完畢。")

# --- 區塊 A：多時間尺度 PVCS 矩陣 ---
st.subheader("多時間尺度分析 (Multi-Horizon Analysis)")
m1, m2, m3, m4 = st.columns(4)

m1.metric("5D (短線衝刺)", f"{latest['PVCS_5D']:.1f}")
m2.metric(
    "20D (主波段)",
    f"{latest['PVCS_20D']:.1f}",
    delta="預設主尺度",
)
m3.metric("60D (中線結構)", f"{latest['PVCS_60D']:.1f}")
m4.metric(
    "Composite 綜合總分", f"{latest['PVCS_Composite']:.1f}"
)

st.markdown("---")

# --- 區塊 B：個股 20D 主尺度動態權重拆解 ---
st.subheader("20D 主尺度個股校準權重 (Stock-Specific Weights)")
w_20 = weights["20D"]

c1, c2, c3 = st.columns(3)
c1.metric(
    "Price 權重",
    f"{w_20['w_p']*100:.1f}%",
    f"IC: {w_20['ic']['P']:.3f}",
)
c2.metric(
    "Volume 權重",
    f"{w_20['w_v']*100:.1f}%",
    f"IC: {w_20['ic']['V']:.3f}",
)
c3.metric(
    "Chip 權重",
    f"{w_20['w_c']*100:.1f}%",
    f"IC: {w_20['ic']['C']:.3f}",
)

# 顯示權重佔比條 (Progress bar)
st.caption("價 / 量 / 籌碼 動態權重分配占比：")
st.progress(float(w_20["w_p"]))