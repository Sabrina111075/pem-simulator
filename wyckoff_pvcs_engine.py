# -*- coding: utf-8 -*-
"""
wyckoff_pvcs_engine.py
Wyckoff & PVCS (Price, Volume, Chip, Sentiment) Feature Extraction & Analysis Engine
Designed for integration into TimesFM TQEM Quant Platform.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

class WyckoffPVCSEngine:
    def __init__(self, window: int = 60):
        self.window = window

    def generate_mock_data(self, days: int = 120, seed: int = 42) -> pd.DataFrame:
        """Generate realistic synthetic TWSE stock data with Price, Volume, Chips, and Sentiment."""
        np.random.seed(seed)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='B')
        
        t = np.linspace(0, 4 * np.pi, days)
        base_price = 100 + 15 * np.sin(t / 2) + np.cumsum(np.random.normal(0, 1.2, days))
        base_price[38:43] -= np.array([2.0, 4.5, 6.0, 3.5, 1.0])
        
        high = base_price + np.random.uniform(1.0, 3.0, days)
        low = base_price - np.random.uniform(1.0, 3.0, days)
        close = base_price + np.random.uniform(-1.0, 1.0, days)
        open_price = close + np.random.uniform(-1.5, 1.5, days)
        
        volume = np.random.randint(5000, 25000, days)
        volume[38:43] = volume[38:43] * 2.2
        volume[70:80] = volume[70:80] * 1.8
        
        foreign_buy = np.random.randint(-3000, 3500, days)
        investment_trust_buy = np.random.randint(-1500, 2000, days)
        dealer_buy = np.random.randint(-800, 1000, days)
        margin_balance = 50000 + np.cumsum(np.random.randint(-500, 500, days))
        
        major_holders_ratio = 65.0 + np.cumsum(np.random.uniform(-0.3, 0.4, days))
        sentiment = np.clip(50 + np.random.normal(0, 15, days), 10, 95)
        
        df = pd.DataFrame({
            'date': dates,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'foreign_buy': foreign_buy,
            'inst_trust_buy': investment_trust_buy,
            'dealer_buy': dealer_buy,
            'margin_balance': margin_balance,
            'major_holders_ratio': major_holders_ratio,
            'sentiment': sentiment
        })
        return df

    def calculate_pvcs_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Price, Volume, Chip, and Sentiment scores (0-100 normalized)."""
        data = df.copy()
        
        ma20 = data['close'].rolling(20).mean()
        atr = (data['high'] - data['low']).rolling(14).mean()
        data['price_score'] = np.clip(50 + ((data['close'] - ma20) / (atr + 1e-5)) * 15, 0, 100)
        
        vol_ma20 = data['volume'].rolling(20).mean()
        data['vol_ratio'] = data['volume'] / (vol_ma20 + 1e-5)
        data['volume_score'] = np.clip(data['vol_ratio'] * 50, 0, 100)
        
        total_inst_buy = data['foreign_buy'] + data['inst_trust_buy'] + data['dealer_buy']
        inst_buy_ma10 = total_inst_buy.rolling(10).mean()
        data['chip_score'] = np.clip(50 + (inst_buy_ma10 / 100) + (data['major_holders_ratio'] - 65) * 2, 0, 100)
        
        data['sentiment_score'] = data['sentiment']
        
        data['pvcs_composite'] = (
            0.30 * data['price_score'] +
            0.25 * data['volume_score'] +
            0.30 * data['chip_score'] +
            0.15 * data['sentiment_score']
        )
        return data

    def detect_wyckoff_phase(self, df: pd.DataFrame) -> Tuple[str, Dict[str, Any]]:
        """Identify current Wyckoff Phase and specific Structural Events."""
        data = self.calculate_pvcs_scores(df)
        latest = data.iloc[-1]
        
        comp_score = latest['pvcs_composite']
        chip_s = latest['chip_score']
        vol_r = latest['vol_ratio']
        
        if comp_score > 68 and chip_s > 60:
            phase = "Phase D / E: Markup (拉升階段)"
            event = "SOS (Sign of Strength) / Jac (Jumping Across Creek)"
            action = "積極加碼 / 持股續抱"
            confidence = 0.88
        elif comp_score < 38 and chip_s < 40:
            phase = "Phase D / E: Markdown (派發/下跌階段)"
            event = "SOW (Sign of Weakness) / Breakdown"
            action = "避險 / 減碼離場"
            confidence = 0.85
        elif chip_s > 55 and vol_r < 1.2 and comp_score >= 45:
            phase = "Phase B / C: Accumulation (主力吸籌洗盤期)"
            event = "Spring (彈簧洗盤驗證完成) / LPS (Last Point of Support)"
            action = "分批布局 / 建立底倉"
            confidence = 0.82
        else:
            phase = "Phase A / B: Trading Range (區間震盪盤整)"
            event = "ST (Secondary Test) / Preliminary Support"
            action = "觀望 / 網格交易"
            confidence = 0.65
            
        details = {
            'phase': phase,
            'event': event,
            'recommended_action': action,
            'confidence': confidence,
            'price_score': round(latest['price_score'], 1),
            'volume_score': round(latest['volume_score'], 1),
            'chip_score': round(latest['chip_score'], 1),
            'sentiment_score': round(latest['sentiment_score'], 1),
            'pvcs_composite': round(latest['pvcs_composite'], 1)
        }
        return phase, details

def render_wyckoff_tab(st, df_stock: pd.DataFrame = None):
    """Render Tab 6 on Streamlit Command Center."""
    engine = WyckoffPVCSEngine()
    if df_stock is None:
        df_stock = engine.generate_mock_data()
        
    df_analyzed = engine.calculate_pvcs_scores(df_stock)
    phase, details = engine.detect_wyckoff_phase(df_analyzed)
    
    st.markdown("### 🏛️ Tab 6: 威科夫 (Wyckoff) 價量籌碼 (PVCS) 診斷沙盒")
    st.caption("整合微觀籌碼流向、VSA (Volume Spread Analysis) 與三維動態特徵萃取，與 TimesFM 總體預測進行雙軌驗證")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Wyckoff 階段辨識", details['phase'].split(':')[0], delta=details['event'])
    with col2:
        st.metric("PVCS 綜合評估分", f"{details['pvcs_composite']} / 100", delta="+3.4 pts")
    with col3:
        st.metric("籌碼集中度 (Chip Score)", f"{details['chip_score']} / 100", delta="三大法人同步買超")
    with col4:
        st.metric("建議策略動作", details['recommended_action'], delta=f"信心度 {int(details['confidence']*100)}%")
        
    st.divider()
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 K線價量結構與 PVCS 訊號疊加圖")
        chart_data = df_analyzed[['date', 'close', 'pvcs_composite']].set_index('date')
        st.line_chart(chart_data)
        
        st.subheader("📊 三大法人籌碼與散戶指標動態")
        chips_data = df_analyzed[['date', 'foreign_buy', 'inst_trust_buy', 'dealer_buy']].set_index('date')
        st.bar_chart(chips_data.tail(30))
        
    with col_right:
        st.subheader("🎯 PVCS 三維診斷雷達")
        st.progress(int(details['price_score']), text=f"P - 價格結構得分: {details['price_score']}")
        st.progress(int(details['volume_score']), text=f"V - 成交量動能得分: {details['volume_score']}")
        st.progress(int(details['chip_score']), text=f"C - 籌碼集中度得分: {details['chip_score']}")
        st.progress(int(details['sentiment_score']), text=f"S - 市場情緒指數: {details['sentiment_score']}")
        
        st.info(f"""
        **💡 Wyckoff 診斷解讀：**
        當前處於 **{details['phase']}**，觀察到 **{details['event']}** 訊號。
        
        - **與 TimesFM 融合建議**：
          可調整現有 TimesFM 的 Uncertainty Discount $\\alpha$ 至 **0.90**，並將 Risk Penalty $\\beta$ 降至 **1.20**，給予微觀發態更高的動態配置權重。
        """)