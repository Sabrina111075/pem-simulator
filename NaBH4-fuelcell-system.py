import streamlit as st
import numpy as np
import pandas as pd
import datetime
import pytz

# --- 頁面基本配置與側邊欄寬度/捲軸優化 (CSS 注入) ---
st.set_page_config(page_title="NaBH4 氫燃料電池數位雙生系統", layout="wide")

# 透過 CSS 擴大側邊欄寬度，並優化滾動條操作流暢度
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        min-width: 360px;
        max-width: 360px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 1. 頂部企業品牌與台灣即時時間 ---
st.markdown("# 🧪 $NaBH_4$ 硼氫化鈉產氫與燃料電池發電數位模擬系統")

tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.datetime.now(tw_tz).strftime('%Y年%m月%d日 %H:%M:%S')
st.caption(f"📊 基於 TAD-AGE 模擬架構 ＆ Butler-Volmer 電化學動力學核心 | **目前台灣時間 (即時)：{now_tw}**")
st.write("---")

class NaBH4_FuelCell_Twin:
    def __init__(self):
        self.R = 8.314        
        self.F = 96485        
        self.A_cell = 200     
        self.n_cells = 45     
        self.i_0 = 0.005      
        self.alpha_a = 0.5
        self.alpha_c = 0.5
        self.n_e = 2
        self.E_eq = 1.229     
        self.R_internal = 0.003 
        
    def simulate_hydrogen_generation(self, flow_rate, concentration, temp, prev_clogging_factor=0.0):
        base_eta = 0.90 if 25 <= temp <= 35 else 0.82
        eta = base_eta * (1.0 - prev_clogging_factor)
        
        h2_flow_nm3 = 2.37 * flow_rate * (concentration / 100.0) * eta
        h2_flow_kg = h2_flow_nm3 * 0.0899
        h2_flow_mol_s = (h2_flow_kg * 1000 / 2.016) / 3600.0
        
        nabo2_flow_mol_s = h2_flow_mol_s / 4.0
        nabo2_flow_kg_h = (nabo2_flow_mol_s * 65.8) * 3600.0 / 1000.0
        
        return {
            "h2_flow_nm3": h2_flow_nm3,
            "h2_flow_mol_s": h2_flow_mol_s,
            "nabo2_flow_kg_h": nabo2_flow_kg_h,
            "actual_eta": eta
        }

    def solve_butler_volmer_overpotential(self, i_density, T_k):
        if i_density <= 0:
            return 0.0
        eta_guess = 0.05
        for _ in range(10):
            f_val = self.i_0 * (np.exp((self.alpha_a * self.n_e * self.F * eta_guess) / (self.R * T_k)) - \
                                np.exp((-self.alpha_c * self.n_e * self.F * eta_guess) / (self.R * T_k))) - i_density
            df_val = self.i_0 * ((self.alpha_a * self.n_e * self.F / (self.R * T_k)) * np.exp((self.alpha_a * self.n_e * self.F * eta_guess) / (self.R * T_k)) + \
                                 (self.alpha_c * self.n_e * self.F / (self.R * T_k)) * np.exp((-self.alpha_c * self.n_e * self.F * eta_guess) / (self.R * T_k)))
            eta_guess = eta_guess - f_val / df_val
        return max(0.0, eta_guess)

    def simulate_fuel_cell(self, h2_available_mol_s, target_power_w, temp_c):
        T_k = temp_c + 273.15
        estimated_voltage = 0.7 * self.n_cells
        target_current = target_power_w / estimated_voltage if target_power_w > 0 else 0.0
        max_current_from_h2 = (h2_available_mol_s * self.n_e * self.F) / self.n_cells
        
        actual_current = min(target_current, max_current_from_h2 * 0.95)
        i_density = actual_current / self.A_cell
        
        eta_act = self.solve_butler_volmer_overpotential(i_density, T_k)
        eta_ohmic = i_density * self.R_internal
        
        v_cell = self.E_eq - eta_act - eta_ohmic
        v_stack = v_cell * self.n_cells
        actual_power = v_stack * actual_current
        
        return {
            "current_a": actual_current,
            "v_cell_v": v_cell,
            "v_stack_v": v_stack,
            "output_power_w": actual_power
        }

# --- 2. 側邊控制欄與 10 大完整佈置場景 ---
st.sidebar.header("🎛️ 工藝參數調功與控制")
flow_rate = st.sidebar.slider("進料流量 Q (L/h)", 1.0, 10.0, 5.0, 0.5)
concentration = st.sidebar.slider("NaBH₄ 溶液濃度 (wt%)", 5.0, 25.0, 20.0, 1.0)
temperature = st.sidebar.slider("反應床操作溫度 (°C)", 10.0, 50.0, 30.0, 1.0)

st.sidebar.write("---")
st.sidebar.header("🎯 模擬應用場景負載")

scenario_key = st.sidebar.selectbox("請選擇系統佈署場景", [
    "場景 01：無人機 / 機器人長時間供電",
    "場景 02：通訊基地台備援電源",
    "場景 03：災害救援移動式電源箱",
    "場景 04：軍用 / 野外任務低噪音電源",
    "場景 05：船舶 / 海上設備供電",
    "場景 06：冷鏈物流 / 醫療冷藏箱備援",
    "場景 07：偏遠地區微電網備援",
    "場景 08：小型載具增程器",
    "場景 09：教育 / 展示 / 研究平台",
    "場景 10：國防秘密掩體 / 長時備援"
])

# 精準硬編碼 10 個獨立分支，絕不漏掉任何一個
if "01" in scenario_key:
    st.sidebar.info("📋 **等級**: UAV/Robot\n\n⚡ **額定功率**: 1.5 kW\n\n✈️ **特點**: 長航時無人機、巡檢機器人")
    base_load = [400, 1500, 1500, 1200, 1100, 1100, 1100, 1200, 800, 400]
elif "02" in scenario_key:
    st.sidebar.info("📋 **等級**: Station\n\n⚡ **額定功率**: 3.0 kW\n\n📶 **特點**: 基地台、斷電瞬間湧浪、尖離峰模擬")
    base_load = [3000, 3500, 3200, 3000, 2800, 2500, 2500, 2800, 3000, 3000]
elif "03" in scenario_key:
    st.sidebar.info("📋 **等級**: Field Box\n\n⚡ **額定功率**: 3.0 kW\n\n🚑 **特點**: 救災抽水泵啟動、全載照明、衛星通訊")
    base_load = [500, 3000, 3000, 2500, 2000, 2000, 1500, 1200, 800, 500]
elif "04" in scenario_key:
    st.sidebar.info("📋 **等級**: Field Box\n\n⚡ **額定功率**: 2.0 kW\n\n🪖 **特點**: 野戰通訊、低紅外線、低噪隱蔽運行")
    base_load = [1000, 1200, 2000, 2000, 1800, 1500, 1500, 1200, 1000, 1000]
elif "05" in scenario_key:
    st.sidebar.info("📋 **等級**: Station\n\n⚡ **額定功率**: 5.0 kW\n\n⚓ **特點**: 海上浮標、資料觀測站、交替負載")
    base_load = [2000, 4000, 5000, 5000, 4500, 3500, 3000, 2500, 2000, 2000]
elif "06" in scenario_key:
    st.sidebar.info("📋 **等級**: Portable\n\n⚡ **額定功率**: 800 W\n\n❄️ **特點**: 疫苗/血液運輸、醫療冷藏壓縮機間歇啟動")
    base_load = [200, 800, 800, 400, 400, 800, 400, 400, 200, 200]
elif "07" in scenario_key:
    st.sidebar.info("📋 **等級**: Station\n\n⚡ **額定功率**: 10.0 kW\n\n☀️ **特點**: 與太陽能互補之高功率夜間微電網備援")
    base_load = [5000, 8000, 10000, 10000, 9000, 8000, 6000, 4000, 3000, 2000]
elif "08" in scenario_key:
    st.sidebar.info("📋 **等級**: Vehicle Assist\n\n⚡ **額定功率**: 4.0 kW\n\n🛵 **特點**: 電動機車增程、無人搬運車(AGV)爬坡加速")
    base_load = [1000, 3000, 4000, 4000, 3500, 2500, 2000, 1500, 1000, 500]
elif "09" in scenario_key:
    st.sidebar.info("📋 **等級**: Demo\n\n⚡ **額定功率**: 150 W\n\n🎓 **特點**: 大學實驗室、能源展示館定額安全負載")
    base_load = [50, 100, 150, 150, 150, 120, 100, 100, 80, 50]
elif "10" in scenario_key:
    st.sidebar.info("📋 **等級**: Station\n\n⚡ **額定功率**: 6.0 kW\n\n🛡️ **特點**: 國防秘密掩體長時備援、突發防衛通訊負載")
    base_load = [4000, 4500, 6000, 6000, 5500, 5000, 4500, 4000, 4000, 4000]
else:
    base_load = [500, 500, 500, 500, 500, 500, 500, 500, 500, 500]

# --- 3. 模擬計算核心執行 ---
twin = NaBH4_FuelCell_Twin()
clogging_factor = 0.0
results = []

for t, target_w in enumerate(base_load):
    h2_res = twin.simulate_hydrogen_generation(flow_rate, concentration, temperature, clogging_factor)
    fc_res = twin.simulate_fuel_cell(h2_res["h2_flow_mol_s"], target_w, temperature)
    
    if h2_res["nabo2_flow_kg_h"] > 0.4:
        clogging_factor += 0.012  
        
    results.append({
        "秒數(s)": t + 1,
        "負載需求(W)": target_w,
        "即時產氫量(Nm3/h)": round(h2_res["h2_flow_nm3"], 3),
        "電堆輸出(W)": round(fc_res["output_power_w"], 1),
        "電堆電壓(V)": round(fc_res["v_stack_v"], 1),
        "操作電流(A)": round(fc_res["current_a"], 1),
        "NaBO2生成速率(kg/h)": round(h2_res["nabo2_flow_kg_h"], 3),
        "觸媒床結塊率(%)": round(clogging_factor * 100, 1)
    })

df_res = pd.DataFrame(results)

# --- 4. 數據儀表板呈現 ---
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("當前穩定產氫量", f"{df_res['即時產氫量(Nm3/h)'].max()} Nm³/h", "Fe-Co-Ni 催化")
with m2:
    st.metric("燃料電池最大輸出功率", f"{df_res['電堆輸出(W)'].max() / 1000:.2f} kW", f"對應：{scenario_key.split('：')[0]}")
with m3:
    st.metric("末端副產品結塊風險因子", f"{df_res['觸媒床結塊率(%)'].max()}%", "偏硼酸鈉累積" if df_res['觸媒床結塊率(%)'].max() > 10 else "安全")

if df_res['觸媒床結塊率(%)'].max() > 10:
    st.error("🚨 [系統警報] 副產品 NaBO₂ 累積速率過快，觸媒床結塊風險偏高！請確認自動化調功或啟動反沖洗液排液模組！")

st.write("---")

# --- 5. 權威性架構：專業 Tab 分頁排版 ---
tab1, tab2, tab3 = st.tabs(["📊 瞬態功率動態響應追蹤", "🔬 電化學動力學分析 (極化曲線)", "📋 數位雙生實時數據流水線"])

with tab1:
    st.subheader("瞬態功率動態響應追蹤 (Load Profile)")
    chart_data = df_res[["秒數(s)", "負載需求(W)", "電堆輸出(W)"]].set_index("秒數(s)")
    st.line_chart(chart_data)

with tab2:
    st.subheader("燃料電池單電池極化曲線 (Polarization Curve)")
    st.markdown("此圖表基於 **巴特勒-福爾默方程式** 計算，展現了當前操作條件下，電流密度增加時的**活化極化與歐姆極化電壓降損失**：")
    
    # 動態生成一整條極化曲線供研究分析
    i_sweep = np.linspace(0.001, 1.2, 50)
    v_sweep = []
    for i_d in i_sweep:
        e_act = twin.solve_butler_volmer_overpotential(i_d, temperature + 273.15)
        e_ohm = i_d * twin.R_internal
        v_sweep.append(twin.E_eq - e_act - e_ohm)
        
    df_polar = pd.DataFrame({
        "電流密度 (A/cm²)": i_sweep,
        "單電池電壓 (V)": v_sweep
    }).set_index("電流密度 (A/cm²)")
    
    st.line_chart(df_polar)
    st.caption("💡 權威電化學指標：當電壓維持在 0.6V - 0.7V 區間時，燃料電池堆擁有最佳的商用發電效率效率。")

with tab3:
    st.subheader("數位雙生實時數據流水線 (Data Pipeline)")
    st.dataframe(df_res, use_container_width=True)