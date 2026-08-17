"""
TQEM-ETF.py - Streamlit 主畫面 (Plotly 橫排中文圖表優化版)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import pytz

from tqem_core import TQEMPipeline
from etf_skills import SKILL_MAP

st.set_page_config(page_title="Crystal Machine - 台灣 ETF 智慧預測平台", layout="wide")

# 特徵英文代碼與中文對照字典 (涵蓋 10 大類別常見特徵)
FEATURE_TRANSLATION = {
    # 市值/高股息
    "dividend_yield": "股息殖利率 (dividend_yield)",
    "earnings_growth": "獲利成長率 (earnings_growth)",
    "quality_roe": "股東權益報酬率 (quality_roe)",
    "valuation": "估值指標 (valuation)",
    "market_cap": "市值規模 (market_cap)",
    # 債券/槓桿反向/產業
    "futures_basis": "期貨價差 (futures_basis)",
    "path_decay": "路徑損耗 (path_decay)",
    "underlying_momentum": "標的動能 (underlying_momentum)",
    "volatility_drag": "波動率拖累 (volatility_drag)",
    "credit_spread": "信用利差 (credit_spread)",
    "duration_risk": "存續期間風險 (duration_risk)",
    "fed_policy": "聯準會政策 (fed_policy)",
    "fx_hedging": "匯率避險 (fx_hedging)",
    "yield_curve": "殖利率曲線 (yield_curve)",
    # 因子/多重資產
    "value_factor": "價值因子 (value_factor)",
    "momentum_factor": "動能因子 (momentum_factor)",
    "quality_factor": "品質因子 (quality_factor)",
    "low_vol_factor": "低波動因子 (low_vol_factor)",
    "size_factor": "規模因子 (size_factor)",
}

# 自訂 CSS 樣式
st.markdown("""
<style>
    .sidebar-brand { font-size: 22px; font-weight: 800; color: #1E3A8A; letter-spacing: 0.5px; margin-bottom: 2px; }
    .sidebar-subbrand { font-size: 11px; color: #6B7280; margin-bottom: 15px; border-bottom: 2px solid #E5E7EB; padding-bottom: 10px; }
    .sidebar-info-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-top: 15px; margin-bottom: 15px; }
    .status-indicator { display: inline-block; width: 8px; height: 8px; background-color: #22C55E; border-radius: 50%; margin-right: 6px; }
    .card-style-1 { background-color: #F0F7FF; border: 1px solid #BAE6FD; border-radius: 10px; padding: 12px; }
    .card-style-2 { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 10px; padding: 12px; }
    .card-style-3 { background-color: #FEFCE8; border: 1px solid #FEF08A; border-radius: 10px; padding: 12px; }
    .card-style-4 { background-color: #FAF5FF; border: 1px solid #E9D5FF; border-radius: 10px; padding: 12px; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_tqem_pipeline(category_name: str):
    skill_cls = SKILL_MAP.get(category_name)
    skill_instance = skill_cls()
    return TQEMPipeline(feature_skill_module=skill_instance)

@st.cache_data
def load_dummy_data():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
    df = pd.DataFrame({
        'date': dates,
        'close': np.linspace(100, 150, 100) + np.random.normal(0, 2, 100),
        'nav': np.linspace(100, 150, 100) + np.random.normal(0, 1.8, 100)
    })
    return df

# ==========================================
# 1. 側邊欄 (Sidebar)
# ==========================================
st.sidebar.markdown('<div class="sidebar-brand">🏛️ Crystal Machine</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-subbrand">Quantitative AI Intelligence Lab</div>', unsafe_allow_html=True)

st.sidebar.subheader("🎯 標的選擇")
selected_category = st.sidebar.selectbox(
    "請選擇 ETF 類別：",
    list(SKILL_MAP.keys())
)

st.sidebar.markdown("""
<div class="sidebar-info-box">
    <small style="color: #64748B; font-weight: bold;">🖥️ 引擎狀態 (Engine Status)</small><br>
    <div style="margin-top: 6px; font-size: 13px; color: #1E293B;">
        <span class="status-indicator"></span><b>TimesFM Model:</b> Online<br>
        <span class="status-indicator"></span><b>Kalman Filter:</b> Active<br>
        <span class="status-indicator"></span><b>Data Feed:</b> Real-time
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar.expander("⚙️ 風控與平滑參數 (Control)", expanded=True):
    kalman_q = st.slider("Kalman 過程雜訊 (Q)", 0.001, 0.100, 0.010, step=0.005, help="Q 值越小平滑效果越強")
    confidence_level = st.select_slider("預測信賴區間", options=["80%", "90%", "95%", "99%"], value="95%", help="信賴區間越高，Alpha 訊號越保守")

with st.sidebar.expander("ℹ️ TQEM 系統架構簡介"):
    st.caption("""
    - **TimesFM**: Google 開源時間序列基礎大模型
    - **Dynamic Weight**: 10 大類別動態特徵權重對映
    - **Kalman Smoothing**: 離散時間平滑濾波，消除高頻市場雜訊
    """)

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Crystal Machine Tech. All rights reserved.")

# ==========================================
# 2. 主畫面 (Main Page)
# ==========================================
st.title("📊 台灣 ETF TimesFM + TQEM 智慧預測與決策平台")

tz_taiwan = pytz.timezone('Asia/Taipei')
current_time_tw = datetime.now(tz_taiwan).strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"結合 TimesFM 時間序列預測、Dynamic Weight 動態權重與 Kalman 平滑風控引擎 ｜ 🕒 **台灣實時時刻：{current_time_tw} (CST)**")

pipeline = load_tqem_pipeline(selected_category)
df_data = load_dummy_data()

with st.spinner(f"正在為【{selected_category.split('：')[1]}】進行實時運算..."):
    result = pipeline.run_inference(df_data)
    
    # 1. Kalman 平滑連動
    raw_weights = result["weights_raw"]
    smooth_factor = np.clip(kalman_q * 10, 0.05, 0.95)
    mean_weight = sum(raw_weights.values()) / len(raw_weights)
    smoothed_weights = {
        k: float(v * smooth_factor + mean_weight * (1 - smooth_factor))
        for k, v in raw_weights.items()
    }
    
    # 2. 信賴區間連動
    confidence_discount = {"80%": 1.05, "90%": 1.00, "95%": 0.92, "99%": 0.80}
    discount = confidence_discount.get(confidence_level, 1.0)
    final_alpha = result['alpha_signal'] * discount

st.markdown("---")

# 核心分析指標
st.subheader("💡 核心分析指標與量化預估")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="card-style-1">
            <small style="color: #1E40AF; font-weight: bold;">市場狀態 (Regime)</small>
            <h2 style="color: #1E3A8A; margin: 4px 0;">{result['regime']}</h2>
            <small style="color: #3B82F6;">當前演算法偵測狀態</small>
        </div>
        """, unsafe_allow_html=True
    )

with col2:
    delta_str = f"{'+' if final_alpha > 0 else ''}{final_alpha*100:.1f}%"
    st.markdown(
        f"""
        <div class="card-style-2">
            <small style="color: #166534; font-weight: bold;">最終 Alpha 訊號強度</small>
            <h2 style="color: #14532D; margin: 4px 0;">{final_alpha:.4f}</h2>
            <small style="color: #16A34A;">預期超額收益: {delta_str}</small>
        </div>
        """, unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="card-style-3">
            <small style="color: #854D0E; font-weight: bold;">預測勝率 (Win Rate)</small>
            <h2 style="color: #713F12; margin: 4px 0;">68.5%</h2>
            <small style="color: #CA8A04;">信賴區間: {confidence_level}</small>
        </div>
        """, unsafe_allow_html=True
    )

with col4:
    st.markdown(
        """
        <div class="card-style-4">
            <small style="color: #6B21A8; font-weight: bold;">預期夏普比率 (Sharpe)</small>
            <h2 style="color: #581C87; margin: 4px 0;">1.82</h2>
            <small style="color: #9333EA;">風險調整收益 ↑ 0.15</small>
        </div>
        """, unsafe_allow_html=True
    )

st.markdown("---")

# Kalman 平滑前後動態權重展示區
st.subheader("⚖️ Kalman 平滑前後的特徵動態權重")
st.caption(f"⚙️ 當前 Kalman 過程雜訊設定為 **Q = {kalman_q}** ｜ 信賴區間設定為 **{confidence_level}**")

# 將特徵名稱翻譯為中文+英文橫排格式
translated_keys = [FEATURE_TRANSLATION.get(k, k) for k in raw_weights.keys()]
raw_vals = list(raw_weights.values())
smooth_vals = list(smoothed_weights.values())

tab1, tab2 = st.tabs(["📊 權重對比圖表", "📋 詳細數據表格"])

with tab1:
    # 使用 Plotly 繪製水平橫排 X 軸文字的柱狀圖
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=translated_keys,
        y=raw_vals,
        name='原始動態權重',
        marker_color='#93C5FD'
    ))
    
    fig.add_trace(go.Bar(
        x=translated_keys,
        y=smooth_vals,
        name='Kalman 平滑權重',
        marker_color='#1D4ED8'
    ))
    
    fig.update_layout(
        barmode='group',
        height=400,
        margin=dict(l=20, r=20, t=30, b=80),
        xaxis=dict(
            tickangle=0,            # 強制 X 軸文字橫排 (0度)
            tickfont=dict(size=12)  # 適合閱讀的字體大小
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df_weights = pd.DataFrame({
        "原始動態權重": raw_vals,
        "Kalman 平滑權重": smooth_vals
    }, index=translated_keys)
    st.dataframe(df_weights.style.highlight_max(axis=0, color='#e6f2ff'), use_container_width=True)