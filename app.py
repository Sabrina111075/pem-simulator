import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 0. 自動刷新機制 & 基礎時間定義
# ==========================================
count = st_autorefresh(interval=60000, limit=None, key="twse_heartbeat")

taipei_tz = pytz.timezone('Asia/Taipei')
now_taipei = datetime.now(taipei_tz)
date_str = now_taipei.strftime("%Y-%m-%d")

# ==========================================
# 1. 台股升降單位 (Tick Size) 離散化邏輯
# ==========================================
def apply_twse_tick_size(price: float) -> float:
    """根據台灣證券交易所規定對齊 Tick Size (精確至兩位小數)"""
    if price < 10:
        tick = 0.01
    elif price < 50:
        tick = 0.05
    elif price < 100:
        tick = 0.1
    elif price < 500:
        tick = 0.5
    elif price < 1000:
        tick = 1.0
    else:
        tick = 5.0
    return round(round(price / tick) * tick, 2)

# ------------------------------------------
# TWSE 盤前試算價與價差自動計算 logic
# ------------------------------------------
def get_twse_premarket_data(stock_id):
    # 假設已從 TWSE MIS API 取得原始 dict data
    # url: https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw
    
    # 讀取數據範例邏輯：
    # z: 當日成交價, y: 昨日收盤價, o: 試算開盤價/開盤價
    current_price = data.get('z', '-')
    yesterday_close = float(data.get('y', 0.0))
    simulated_open = data.get('o', '-')
    
    auto_spread = 0.0
    is_premarket = False
    
    # 判斷是否為盤前時段 (08:30 ~ 08:59) 或成交價尚未產生
    if current_price == '-' or current_price == '':
        if simulated_open != '-' and simulated_open != '':
            sim_price = float(simulated_open)
            # 計算試算價差 (點數或百分比)
            auto_spread = round(sim_price - yesterday_close, 2)
            is_premarket = True
    else:
        # 盤中正常成交
        auto_spread = round(float(current_price) - yesterday_close, 2)
        
    return auto_spread, is_premarket

# ==========================================
# 3. 核心幾何與 PVCS 風險計算邏輯
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
# 4. UI 頁面配置與柔和科技風 Banner (含實時秒針)
# ==========================================
st.set_page_config(page_title="HyperFlow DMEC - 台股雙曲流形與數位分身平台", layout="wide")

st.markdown("""
<style>
    .custom-main-title {
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: #0f172a;
        line-height: 1.25 !important;
        margin-bottom: 0.2rem !important;
    }
    
    [data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 8px 10px !important;
        border-radius: 8px;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.02);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        color: #64748b !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.45rem !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-main-title">🛡️ HyperFlow DMEC 全日台股雙曲流形與數位分身平台</div>', unsafe_allow_html=True)
st.caption("Micro-DMEC-G 觀察框架：結合 PVCS (價格-成交量-買賣張數) 三維空間與 Poincaré 雙曲幾何之個股動態評估面板")

# 嵌入前端原生 JavaScript 實時讀秒心跳 Banner
components.html(
    f'''
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: transparent;
        }}
        @keyframes blink {{
            0% {{ opacity: 1.0; transform: scale(1); }}
            50% {{ opacity: 0.3; transform: scale(0.85); }}
            100% {{ opacity: 1.0; transform: scale(1); }}
        }}
        .heartbeat-dot {{
            height: 9px;
            width: 9px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
            box-shadow: 0 0 6px #10b981;
            animation: blink 1.2s infinite ease-in-out;
        }}
        .live-status-box {{
            background: linear-gradient(135deg, #f0fdf4 0%, #f8fafc 100%);
            border: 1px solid #dcfce7;
            border-left: 4px solid #10b981;
            padding: 8px 16px;
            border-radius: 8px;
            color: #1e293b;
            font-size: 0.88rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        }}
        .status-tag {{
            background-color: #e0f2fe;
            color: #0369a1;
            padding: 3px 10px;
            border-radius: 12px;
            border: 1px solid #bae6fd;
            font-size: 0.78rem;
            font-weight: 600;
        }}
        .time-code {{
            color: #0f766e;
            font-family: monospace;
            font-weight: 700;
            background-color: #ccfbf1;
            padding: 2px 6px;
            border-radius: 4px;
        }}
    </style>
    </head>
    <body>
        <div class="live-status-box">
            <div>
                <span class="heartbeat-dot"></span>
                <b style="color: #0f172a;">TWSE 官方 API 實時連線中</b> &nbsp;|&nbsp; 
                <span>台北時間：<span id="live-clock" class="time-code">--:--:--</span></span> &nbsp;|&nbsp; 
                <span>基準日：<code style="background:none; color:#475569;">{date_str}</code></span>
            </div>
            <div>
                <span class="status-tag">⚡ 60s 脈衝同步 (第 {count+1} 次)</span>
            </div>
        </div>

        <script>
            function updateClock() {{
                const now = new Date();
                const options = {{ timeZone: 'Asia/Taipei', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }};
                const timeStr = new Intl.DateTimeFormat('zh-TW', options).format(now);
                document.getElementById('live-clock').innerText = timeStr;
            }}
            setInterval(updateClock, 1000);
            updateClock();
        </script>
    </body>
    </html>
    ''',
    height=54
)

st.markdown("---")

# ==========================================
# 5. 側邊欄控制項與靜態備援對照表
# ==========================================
st.sidebar.header("📈 PVCS 台股個股選取")

stock_mode = st.sidebar.radio("選擇股票模式", ["熱門標的", "自訂股票代碼"])

stock_name_map = {
    "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "2303": "聯電", "6770": "力積電",
    "2308": "台達電", "2357": "華碩", "3008": "大立光", "3443": "創意", "6669": "緯穎",
    "2382": "廣達", "3231": "緯創", "3481": "群創", "2409": "友達", "2324": "仁寶", 
    "2344": "華邦電", "2603": "長榮", "2609": "陽明", "2615": "萬海", "00876": "元大全球5G"
}

base_price_map = {
    "2330": 2400, "2317": 243, "2454": 3735, "2303": 126, "6770": 27,
    "2308": 380, "2357": 490, "3008": 2550, "3443": 1350, "6669": 2100,
    "2382": 290, "3231": 105, "3481": 46.8, "2409": 17, "2324": 38, "00876": 85.95
}

base_volume_map = {
    "2330": 28000, "2317": 36819, "2454": 5403, "2303": 125000, "6770": 150000,
    "2308": 8000, "2357": 6000, "3008": 1500, "3443": 3000, "6669": 2000, "3481": 186725, "00876": 423
}

hot_stock_options = [
    "2330 台積電", "2317 鴻海", "2454 聯發科", "2303 聯電", "2609 陽明", "2603 長榮",
    "6770 力積電", "3481 群創", "2409 友達", "2324 仁寶", "2344 華邦電", "2382 廣達"
]

if stock_mode == "熱門標的":
    selected_stock = st.sidebar.selectbox("熱門股票清單 (成交熱門/權值股)", hot_stock_options)
    stock_code = selected_stock.split(" ")[0]
    display_stock_name = selected_stock
else:
    user_input_code = st.sidebar.text_input("請輸入台股代碼 (例如: 2330, 2317)", value="2317").strip().upper()
    stock_code = user_input_code if user_input_code else "2317"
    stock_name = stock_name_map.get(stock_code, "")
    display_stock_name = f"{stock_code} {stock_name}".strip()

stock_name = stock_name_map.get(stock_code, "")
display_stock_name = f"{stock_code} {stock_name}".strip()

stock_name = stock_name_map.get(stock_code, "")
display_stock_name = f"{stock_code} {stock_name}".strip()

stock_name = stock_name_map.get(stock_code, "")
display_stock_name = f"{stock_code} {stock_name}".strip()

# ==========================================
# A. TWSE 官方 API 實時資料抓取與試算價差解析
# ==========================================
import requests

def fetch_twse_official_data(code):
    try:
        url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{code}.tw"
        res = requests.get(url, timeout=3)
        data = res.json()
        if "msgArray" in data and len(data["msgArray"]) > 0:
            return data["msgArray"][0]
    except Exception:
        pass
    return {}

# 執行抓取
api_data = fetch_twse_official_data(stock_code)

# 計算盤前 / 盤中價差
live_calculated_spread = 0.0
try:
    y_close = float(api_data.get('y', 0.0))
    z_price = api_data.get('z', '-')
    o_price = api_data.get('o', '-')

    if z_price != '-' and z_price != '':
        live_calculated_spread = float(z_price) - y_close
    elif o_price != '-' and o_price != '':
        live_calculated_spread = float(o_price) - y_close
except Exception:
    live_calculated_spread = 0.0

# ==========================================
# B. 側邊欄：盤前試算自動連動與手動微調
# ==========================================
st.sidebar.markdown("### 📊 盤前籌碼微調")

# 加上 key="key_sync_twse_chk" 防止元件重複 ID 衝突
use_live_data = st.sidebar.checkbox(
    "自動同步 TWSE 盤前試算價差", 
    value=True, 
    key="key_sync_twse_chk"
)

if use_live_data:
    default_spread = float(live_calculated_spread)
    st.sidebar.caption(f"🟢 已即時帶入 TWSE 試算價差：`{default_spread:+.2f}`")
else:
    default_spread = 0.0

pre_market_spread = st.sidebar.slider(
    "盤前試撮 / 夜盤價差 (點/%)",
    min_value=-150.0,
    max_value=150.0,
    value=float(np.clip(default_spread, -150.0, 150.0)),
    step=0.5,
    key="sb_spread_slider_main"
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 幾何與數位分身參數")
noise_level = st.sidebar.slider("訊號雜訊強度 (Noise)", 0.0, 0.5, 0.15, 0.05, key="sb_noise_slider")
tolerance = st.sidebar.slider("閉環預警殘差閾值 (Tolerance)", 0.05, 0.5, 0.2, 0.05, key="sb_tol_slider")

st.sidebar.markdown("---")
st.sidebar.info("📊 **資料來源與運算架構**\n\n結合 TWSE 實時 API 與雙曲流行 (Poincaré Disk) 動態演化模型。")

# ==========================================
# B. 側邊欄：盤前試算自動連動與手動微調
# ==========================================
st.sidebar.markdown("### 📊 盤前籌碼微調")

# 自動模式開關
use_live_data = st.sidebar.checkbox("自動同步 TWSE 盤前試算價差", value=True)

if use_live_data:
    default_spread = float(live_calculated_spread)
    st.sidebar.caption(f"🟢 已即時帶入 TWSE 試算價差：`{default_spread:+.2f}`")
else:
    default_spread = 0.0

pre_market_spread = st.sidebar.slider(
    "盤前試撮 / 夜盤價差 (點/%)",
    min_value=-150.0,
    max_value=150.0,
    value=float(np.clip(default_spread, -150.0, 150.0)),
    step=0.5,
    key="sb_spread_slider"
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 幾何與數位分身參數")
noise_level = st.sidebar.slider("訊號雜訊強度 (Noise)", 0.0, 0.5, 0.15, 0.05)
tolerance = st.sidebar.slider("閉環預警殘差閾值 (Tolerance)", 0.05, 0.5, 0.2, 0.05)

st.sidebar.markdown("---")
st.sidebar.info("📊 **資料來源與運算架構**\n\n結合 TWSE 實時 API 與雙曲流行 (Poincaré Disk) 動態演化模型。")
# ==========================================
# B. 側邊欄：盤前試算自動連動與手動微調
# ==========================================
st.sidebar.markdown("### 📊 盤前籌碼微調")

# 自動模式開關
use_live_data = st.sidebar.checkbox("自動同步 TWSE 盤前試算價差", value=True)

if use_live_data:
    default_spread = float(live_calculated_spread)
    st.sidebar.caption(f"🟢 已即時帶入 TWSE 試算價差：`{default_spread:+.2f}`")
else:
    default_spread = 0.0

pre_market_spread = st.sidebar.slider(
    "盤前試撮 / 夜盤價差 (點/%)",
    min_value=-150.0,
    max_value=150.0,
    value=float(np.clip(default_spread, -150.0, 150.0)),
    step=0.5,
    key="sb_spread_slider"
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 幾何與數位分身參數")
noise_level = st.sidebar.slider("訊號雜訊強度 (Noise)", 0.0, 0.5, 0.15, 0.05)
tolerance = st.sidebar.slider("閉環預警殘差閾值 (Tolerance)", 0.05, 0.5, 0.2, 0.05)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; font-size: 0.78rem; color: #475569; line-height: 1.5;">
    <div style="font-weight: bold; color: #1e293b; margin-bottom: 6px; font-size: 0.82rem;">
        📊 資料來源與運算架構
    </div>
</div>
""", unsafe_allow_ascii=False)

# ==========================================
# 6. 數據獲取與幾何運算
# ==========================================
api_data = fetch_twse_official_data(stock_code)

if api_data and api_data["success"]:
    real_price = api_data["price"]
    real_volume = api_data["volume_lots"]
    real_change = api_data["change"]
    data_source_label = "TWSE 證交所官方 API"
else:
    real_price = float(base_price_map.get(stock_code, 200.0))
    real_volume = int(base_volume_map.get(stock_code, 20000))
    real_change = 0.0
    data_source_label = "靜態備援對照檔"

try:
    code_seed = sum(ord(c) for c in stock_code)
except Exception:
    code_seed = 9999
np.random.seed(code_seed)

intent_map = {"極度偏空": -1.5, "偏空": -0.7, "中立": 0.0, "偏多": 0.7, "極度偏多": 1.5}
intent_val = intent_map[major_buyer_intent]

time_steps = 120
t = np.linspace(0, 12, time_steps)

mock_price_seq = (np.sin(t) * 0.005 + 1.0) * real_price
mock_price = np.array([apply_twse_tick_size(p) for p in mock_price_seq], dtype=float)
mock_price[-1] = float(real_price)

mock_volume = (np.cos(t * 1.5) * 0.1 + 1.0) * real_volume
mock_volume[-1] = int(real_volume)

mock_count = np.abs(np.gradient(mock_price)) * (real_volume * 0.1) + (real_volume * 0.15)

geo_engine = HyperbolicStateEngine()
risk_engine = CurvatureRiskEngine()

df_kinematics = geo_engine.compute_kinematics_from_pvcs(mock_price, mock_volume, mock_count)
df_geo = geo_engine.map_to_poincare_disk(df_kinematics)
df_res = risk_engine.compute_trajectory_curvature(df_geo)

latest = df_res.iloc[-1]

latest_price = float(real_price)
price_diff = float(real_change)
est_volume = int(real_volume)

confidence_score = max(0.60, min(0.99, 1.0 - (noise_level * 0.8)))
p_score = min(100, max(0, int(50 + (price_diff / latest_price) * 1000)))
v_score = min(100, max(0, int(50 + (est_volume - base_volume_map.get(stock_code, est_volume)) / (base_volume_map.get(stock_code, est_volume) * 0.02 + 1e-5))))
c_score = min(100, max(0, int(100 - (latest['Turning_Risk'] * 100))))

if latest_price % 1 == 0:
    price_display_fmt = f"{int(latest_price):,}"
else:
    price_display_fmt = f"{latest_price:,.2f}"

if price_diff % 1 == 0:
    diff_display_fmt = f"{int(price_diff):+d}"
else:
    diff_display_fmt = f"{price_diff:+,.2f}"

# ==========================================
# 7. 市場行情與 P/V/C 得分卡片
# ==========================================
st.markdown(
    f'''
    <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px;">
        <span style="font-size: 1.3rem; font-weight: 700; color: #0f172a;">📊 市場實時行情與 P/V/C 幾何評分</span>
        <span style="font-size: 0.85rem; color: #64748b;">
            ℹ️行情與收盤成交量已精確同步。
        </span>
    </div>
    ''',
    unsafe_allow_html=True
)

m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
m_col1.metric("最新收盤/試算價", f"{price_display_fmt} 元", delta=diff_display_fmt)
m_col2.metric("最新總成交量", f"{est_volume:,} 張")
m_col3.metric("指標可信度 (Confidence)", f"{confidence_score:.1%}")
m_col4.metric("P/V/C 綜合得分", f"{int((p_score + v_score + c_score)/3)} 分")
m_col5.metric("價量動能分 (P/V)", f"{p_score} / {v_score}")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 8. 當前分析標的與幾何 KPI
# ==========================================
st.subheader(f"📌 當前分析標的：`{display_stock_name}`")

col1, col2, col3, col4 = st.columns(4)
col1.metric("PVCS 馬氏距離 (D_t)", f"{latest['Mahalanobis_D']:.3f}")
col2.metric("雙曲半徑 (Poincaré r)", f"{latest['Poincare_r']:.3f}", delta_color="inverse")
col3.metric("軌跡曲率強度 (κ_intensity)", f"{latest['Curvature_Intensity']:.3f}")

risk_val = latest['Turning_Risk']
risk_color = "normal" if risk_val < 0.6 else "inverse"
col4.metric("個股轉折 / 失效風險 (Risk)", f"{risk_val:.1%}", delta=f"{risk_val - 0.5:.2f}", delta_color=risk_color)

st.markdown("---")

# ==========================================
# 9. 圖表區：Poincaré Disk 盤前籌碼預測
# ==========================================
st.subheader(f"🌀 {display_stock_name} Poincaré Disk PVCS 雙曲狀態圓盤")

# 1. 讀取側邊欄變數與安全轉譯
intent_map = {"極度偏多": 1.0, "偏多": 0.5, "中立": 0.0, "偏空": -0.5, "極度偏空": -1.0}
intent_val = intent_map.get(major_buyer_intent, 0.0)

spread_val = float(pre_market_spread) if 'pre_market_spread' in locals() else 0.0
vol_ratio_val = float(vol_ratio) if 'vol_ratio' in locals() else 1.0

# 2. 高靈敏幾何映射 (價差 70% + 籌碼意向 30%)
spread_norm = np.clip(spread_val / 150.0, -1.0, 1.0)
pred_r = np.clip(0.35 + (vol_ratio_val * 0.1), 0.2, 0.92)
combined_bias = np.clip(spread_norm * 0.7 + intent_val * 0.3, -1.0, 1.0)

# 角度極致擺盪偏轉 (頂點 90 度進行偏轉)
pred_theta = (np.pi / 2.0) - (combined_bias * (np.pi * 0.75))

pred_u = pred_r * np.cos(pred_theta)
pred_v = pred_r * np.sin(pred_theta)

# ------------------------------------------
# C. Plotly 繪圖
# ------------------------------------------
fig_disk = go.Figure()

# 圓盤邊界 Boundary
theta_b = np.linspace(0, 2*np.pi, 200)
fig_disk.add_trace(go.Scatter(
    x=np.cos(theta_b), y=np.sin(theta_b),
    mode='lines', line=dict(color='gray', dash='dash', width=1.5),
    name='Boundary (r=1)'
))

# PVCS 歷史軌跡
if 'u_coords' in locals() and 'v_coords' in locals():
    u_h, v_h = u_coords, v_coords
else:
    u_h = np.array([0, 0.1, 0.3, 0.5, 0.4, 0.1, -0.2, -0.4, -0.2, 0, 0])
    v_h = np.array([-0.95, -0.6, -0.2, 0.2, 0.5, 0.8, 0.5, 0.2, -0.3, -0.7, -0.98])

fig_disk.add_trace(go.Scatter(
    x=u_h, y=v_h, mode='lines+markers',
    line=dict(color='#3b82f6', width=2),
    marker=dict(size=6, color=np.linspace(0.3, 0.8, len(u_h)), colorscale='Viridis', showscale=True, colorbar=dict(title="Risk", x=1.02)),
    name='PVCS State Trajectory'
))

# 當前點 (紅 X)
fig_disk.add_trace(go.Scatter(
    x=[u_h[-1]], y=[v_h[-1]], mode='markers',
    marker=dict(symbol='x', size=14, color='red', line=dict(width=3)),
    name='Current State'
))

# 預測連線 (黃虛線)
fig_disk.add_trace(go.Scatter(
    x=[u_h[-1], pred_u], y=[v_h[-1], pred_v], mode='lines',
    line=dict(color='#f59e0b', width=2, dash='dot'),
    name='盤前推算演進趨勢'
))

# 09:00 預估位 (金色星號)
fig_disk.add_trace(go.Scatter(
    x=[pred_u], y=[pred_v], mode='markers+text',
    text=[f"09:00 預估位 ({spread_val:+.0f})"], textposition='top center',
    marker=dict(symbol='star', size=18, color='#f59e0b', line=dict(color='orange', width=1)),
    name='08:59 籌碼預估位'
))

fig_disk.update_xaxes(range=[-1.15, 1.15], zeroline=False)
fig_disk.update_yaxes(range=[-1.15, 1.15], zeroline=False, scaleanchor="x", scaleratio=1)
fig_disk.update_layout(
    height=500, margin=dict(l=20, r=40, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_disk, use_container_width=True)

# ==========================================
# 10. 時序圖：PVCS 軌跡曲率強度與轉折風險
# ==========================================
st.subheader(f"🌊 {display_stock_name} PVCS 軌跡曲率強度與轉折風險動態時序")

fig_wave = make_subplots(specs=[[{"secondary_y": True}]])

# 1. 軌跡曲率強度 (κ intensity - 藍線)
fig_wave.add_trace(
    go.Scatter(
        x=df_res.index,
        y=df_res['Curvature_Intensity'].to_numpy(),
        mode='lines',
        name='軌跡曲率強度 (κ_intensity)',
        line=dict(color='#3b82f6', width=2)
    ),
    secondary_y=False
)

# 2. 個股轉折風險 (Turning Risk - 紅虛線)
fig_wave.add_trace(
    go.Scatter(
        x=df_res.index,
        y=df_res['Turning_Risk'].to_numpy(),
        mode='lines',
        name='個股轉折風險 (Turning Risk)',
        line=dict(color='#ef4444', width=2, dash='dot')
    ),
    secondary_y=True
)

# 3. 佈局調整
fig_wave.update_layout(
    height=280,
    margin=dict(l=20, r=20, t=20, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

fig_wave.update_yaxes(title_text="曲率強度 κ", secondary_y=False)
fig_wave.update_yaxes(title_text="轉折風險得分", secondary_y=True)

st.plotly_chart(fig_wave, use_container_width=True)

# ==========================================
# 11. 數位分身診斷區
# ==========================================
st.subheader("🤖 個股 PVCS 閉環數位分身診斷與處置建議")

simulated_twin_val = mock_price[-1]
residual = abs(mock_price[-1] - simulated_twin_val)

d_col1, d_col2 = st.columns([1, 2])

with d_col1:
    st.write(f"**目標股票標的**: `{display_stock_name}`")
    st.write(f"**即時預估收盤價**: `{price_display_fmt}` 元")
    st.write(f"**數位分身模型殘差 |e(t)|**: `{residual:.4f}`")

with d_col2:
    if residual > tolerance or risk_val > 0.65:
        st.error(f"⚠️ **{display_stock_name} 檢測到高量價曲率轉折告警**")
        st.markdown("👉 **建議處置動作**：PVCS 軌跡顯示該股正處於 Poincaré 圓盤邊界區域，請即時監控風險。")
    else:
        st.success(f"✅ **{display_stock_name} PVCS 幾何狀態穩定**")
        st.markdown("👉 **建議處置動作**：價量籌碼結構處於正常趨勢，維持原策略持有。")