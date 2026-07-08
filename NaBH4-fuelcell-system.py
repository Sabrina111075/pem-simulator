import streamlit as st
import numpy as np
import pandas as pd
import datetime
import pytz  # 用於精準鎖定台灣時區

# --- 頁面基本配置 ---
st.set_page_config(page_title="NaBH4 氫燃料電池數位雙生系統", layout="wide")

# --- 1. 標題優化（移除豆腐字）與台灣即時時間 ---
# 使用 LaTeX 語法 $NaBH_4$ 代替下標字，根絕方塊字問題
st.markdown("# 🧪 $NaBH_4$ 即時產氫與燃料電池發電數位雙生模擬系統")

# 獲取並顯示即時台灣時間
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.datetime.now(tw_tz).strftime('%Y年%m月%d日 %H:%M:%S')
st.caption(f"📊 基於 TAD-AGE 模擬架構 ＆ Butler-Volmer 電化學動力學核心 | **目前台灣時間 (即時)：{now_tw}**")
st.write("---")

class NaBH4_FuelCell_Twin:
    def __init__(self):
        self.R = 8.314        # J/(mol*K)
        self.F = 96485        # C/mol
        self.A_cell = 200     # cm^2
        self.n_cells = 45     # 45芯電堆
        self.i_0 = 0.005      # A/cm^2
        self.alpha_a = 0.5
        self.alpha_c = 0.5
        self.n_e = 2
        self.E_eq = 1.229     # V
        self.R_internal = 0.003 # Ohm
        
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

# --- 2. 側邊控制欄優化（縮短下拉選單長度，根絕視窗遮擋） ---
st.sidebar.header("🎛️ 工藝參數調功與控制")
flow_rate = st.sidebar.slider("進料流量 Q (L/h)", 1.0, 10.0, 5.0, 0.5)
concentration = st.sidebar.slider("NaBH₄ 溶液濃度 (wt%)", 5.0, 25.0, 20.0, 1.0)
temperature = st.sidebar.slider("反應床操作溫度 (°C)", 10.0, 50.0, 30.0, 1.0)

st.sidebar.write("---")
st.sidebar.header("🎯 模擬應用場景負載")

# 精簡選單文字，讓下拉清單能完全被側邊欄包容
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

# 利用 info 容器在下方動態顯示對應場景的詳細工業細節與功率
if "1. 無人機" in scenario:
    # UAV/Robot 等級: 起飛爬升、巡航、懸停降落 [功率範圍: 200W - 2kW]
    base_load = [400, 1500, 1500, 1200, 1100, 1100, 1100, 1200, 800, 400]
elif "2. 通訊基地台" in scenario:
    # Station 等級: 斷電瞬間湧浪電流、日間尖峰、夜間離峰 [功率範圍: 3kW - 10kW]
    base_load = [3000, 3500, 3200, 3000, 2800, 2500, 2500, 2800, 3000, 3000]
elif "3. 災害救援" in scenario:
    # Field Box 等級: 抽水泵啟動、全載照明、衛星通訊調度 [功率範圍: 1kW - 3kW]
    base_load = [500, 3000, 3000, 2500, 2000, 2000, 1500, 1200, 800, 500]
elif "4. 軍用 / 野外" in scenario:
    # Field Box 等級: 野戰通訊、雷達小站、低紅外線低噪運行 [功率範圍: 1kW - 3kW]
    base_load = [1000, 1200, 2000, 2000, 1800, 1500, 1500, 1200, 1000, 1000]
elif "5. 船舶 / 海上" in scenario:
    # Station 等級: 海上浮標、資料站、小型無人船交替負載 [功率範圍: 3kW - 10kW]
    base_load = [2000, 4000, 5000, 5000, 4500, 3500, 3000, 2500, 2000, 2000]
elif "6. 冷鏈物流" in scenario:
    # Portable 等級: 疫苗/血液運輸、移動式冷凍櫃壓縮機間歇啟動 [功率範圍: 500W - 1kW]
    base_load = [200, 800, 800, 400, 400, 800, 400, 400, 200, 200]
elif "7. 偏遠地區" in scenario:
    # Station 等級: 空雨天/夜間備援、與太陽能互補之高功率發電 [功率範圍: 3kW - 10kW]
    base_load = [5000, 8000, 10000, 10000, 9000, 8000, 6000, 4000, 3000, 2000]
elif "8. 小型載具" in scenario:
    # Vehicle Assist 等級: 電動機車增程、無人搬運車爬坡加速 [功率範圍: 1kW - 5kW]
    base_load = [1000, 3000, 4000, 4000, 3500, 2500, 2000, 1500, 1000, 500]
elif "9. 教育 / 展示" in scenario:
    # Demo 等級: 大學實驗室、能源展示館之定額安全負載 [功率範圍: 50W - 200W]
    base_load = [50, 100, 150, 150, 150, 120, 100, 100, 80, 50]
else:
    # 10. 國防秘密掩體: 長時備援、突發通訊負載 [功率範圍: 3kW - 10kW]
    base_load = [4000, 4500, 6000, 6000, 5500, 5000, 4500, 4000, 4000, 4000]

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
    st.metric("燃料電池最大輸出功率", f"{df_res['電堆輸出(W)'].max() / 1000:.2f} kW", f"對應場景：{scenario_key.split('：')[0]}")
with m3:
    st.metric("末端副產品結塊風險因子", f"{df_res['觸媒床結塊率(%)'].max()}%", "偏硼酸鈉累積" if df_res['觸媒床結塊率(%)'].max() > 10 else "安全")

if df_res['觸媒床結塊率(%)'].max() > 10:
    st.error("🚨 [系統警報] 副產品 NaBO₂ 累積速率過快，觸媒床結塊風險偏高！請確認自動化調功或啟動反沖洗液排液模組！")

st.subheader("📊 瞬態功率動態響應追蹤 (Load Profile)")
chart_data = df_res[["秒數(s)", "負載需求(W)", "電堆輸出(W)"]].set_index("秒數(s)")
st.line_chart(chart_data)

st.subheader("📋 數位雙生實時數據流水線 (Data Pipeline)")
st.dataframe(df_res, use_container_width=True)