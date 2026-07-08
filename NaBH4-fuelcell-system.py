import numpy as np
import pandas as pd
import time

class NaBH4_FuelCell_Twin:
    def __init__(self):
        # 物理與電化學常數
        self.R = 8.314        # 理想氣體常數 J/(mol*K)
        self.F = 96485        # 法拉第常數 C/mol
        
        # 燃料電池基本參數 (以 3 kW 堆疊為基準設計)
        self.A_cell = 200     # 電極有效面積 cm^2
        self.n_cells = 45     # 電池堆疊單元數
        self.i_0 = 0.005      # 交換電流密度 A/cm^2
        self.alpha_a = 0.5    # 陽極電荷轉移係數
        self.alpha_c = 0.5    # 陰極電荷轉移係數
        self.n_e = 2          # 每個氫分子反應轉移電子數 (H2 -> 2H+ + 2e-)
        self.E_eq = 1.229     # 平衡電位 V
        self.R_internal = 0.003 # 內部歐姆電阻 Ohm
        
    def simulate_hydrogen_generation(self, flow_rate, concentration, temp, prev_clogging_factor=0.0):
        """
        1. 動態產氫模組 (依據系統圖與計算公式)
        """
        # 基礎轉化率受溫度與觸媒狀態(結塊因子)影響
        base_eta = 0.90 if temp >= 25 and temp <= 35 else 0.82
        eta = base_eta * (1.0 - prev_clogging_factor) # 結塊會降低有效轉化率
        
        # 產氫量預測公式: 2.37 * Q * C * eta (Nm3/h)
        h2_flow_nm3 = 2.37 * flow_rate * (concentration / 100.0) * eta
        # 換算為質量流量 (kg/h), 1 Nm3 H2 約等於 0.0899 kg
        h2_flow_kg = h2_flow_nm3 * 0.0899
        # 換算為摩爾流量 (mol/s)
        h2_flow_mol_s = (h2_flow_kg * 1000 / 2.016) / 3600.0
        
        # 副產品 NaBO2 生成量 (1 mol NaBH4 產生 1 mol NaBO2 與 4 mol H2)
        nabo2_flow_mol_s = h2_flow_mol_s / 4.0
        nabo2_flow_kg_h = (nabo2_flow_mol_s * 65.8) * 3600.0 / 1000.0
        
        return {
            "h2_flow_nm3": h2_flow_nm3,
            "h2_flow_mol_s": h2_flow_mol_s,
            "nabo2_flow_kg_h": nabo2_flow_kg_h,
            "actual_eta": eta
        }

    def solve_butler_volmer_overpotential(self, i_cell, T_k):
        """
        2. 電化學核心: 透過巴特勒-福爾默方程式逆向求解過電位 (Activation Overpotential)
        i = i_0 * [exp(alpha_a*n*F*eta/RT) - exp(-alpha_c*n*F*eta/RT)]
        當過電位較大時，可採用簡化數值疊代求解
        """
        if i_cell <= 0:
            return 0.0
        
        # 使用牛頓法或二分法精準求解 Butler-Volmer 方程式中的 eta
        eta_guess = 0.05
        for _ in range(10):
            f_val = self.i_0 * (np.exp((self.alpha_a * self.n_e * self.F * eta_guess) / (self.R * T_k)) - \
                                np.exp((-self.alpha_c * self.n_e * self.F * eta_guess) / (self.R * T_k))) - i_cell
            # 微分項
            df_val = self.i_0 * ((self.alpha_a * self.n_e * self.F / (self.R * T_k)) * np.exp((self.alpha_a * self.n_e * self.F * eta_guess) / (self.R * T_k)) + \
                                 (self.alpha_c * self.n_e * self.F / (self.R * T_k)) * np.exp((-self.alpha_c * self.n_e * self.F * eta_guess) / (self.R * T_k)))
            eta_guess = eta_guess - f_val / df_val
        return max(0.0, eta_guess)

    def simulate_fuel_cell(self, h2_available_mol_s, target_power_w, temp_c):
        """
        3. 燃料電池發電模組
        """
        T_k = temp_c + 273.15
        # 根據目標功率估算所需電流 (假設單電池電壓約 0.7V)
        estimated_voltage = 0.7 * self.n_cells
        target_current = target_power_w / estimated_voltage if target_power_w > 0 else 0.0
        
        # 檢查氫氣供應量是否充足 (法拉第定律: I = 2 * F * n_H2)
        max_current_from_h2 = (h2_available_mol_s * self.n_e * self.F) / self.n_cells
        
        # 實際運作電流不能超過氫氣供應極限
        actual_current = min(target_current, max_current_from_h2 * 0.95) # 留 5% 緩衝避免氣體乾涸
        i_density = actual_current / self.A_cell # 電流密度 A/cm^2
        
        # 計算各項電壓損失
        eta_act = self.solve_butler_volmer_overpotential(i_density, T_k) # 活化極化損失 (Butler-Volmer)
        eta_ohmic = i_density * self.R_internal # 歐姆極化損失
        
        # 單電池電壓與堆疊總電壓
        v_cell = self.E_eq - eta_act - eta_ohmic
        v_stack = v_cell * self.n_cells
        actual_power = v_stack * actual_current
        
        h2_consumed_mol_s = (actual_current * self.n_cells) / (self.n_e * self.F)
        
        return {
            "current_a": actual_current,
            "v_cell_v": v_cell,
            "v_stack_v": v_stack,
            "output_power_w": actual_power,
            "h2_utilization": (h2_consumed_mol_s / h2_available_mol_s * 100) if h2_available_mol_s > 0 else 0
        }

# --- 執行場景動態模擬測試 ---
if __name__ == "__main__":
    twin = NaBH4_FuelCell_Twin()
    
    # 設置場景：災害救援移動式電源箱 (動態負載模擬 10 秒)
    print("【TAD-AGE 數位雙生模擬啟動：3kW 行動備援電源箱場景】\n")
    
    # 輸入控制參數 (對應製氫端與環境)
    flow_rate = 5.0        # L/h (實務黃金進料量)
    concentration = 20.0  # 20 wt%
    temperature = 30.0    # 30°C 最佳操作溫度
    clogging_factor = 0.0 # 初始無結晶堵塞
    
    # 動態需求負載 (瓦特) - 模擬負載突波
    load_profiles = [500, 1200, 2000, 3000, 3200, 3000, 1500, 800, 500, 500]
    
    history = []
    
    for t, target_w in enumerate(load_profiles):
        # 1. 產生氫氣
        h2_res = twin.simulate_hydrogen_generation(flow_rate, concentration, temperature, clogging_factor)
        
        # 2. 導入燃料電池發電
        fc_res = twin.simulate_fuel_cell(h2_res["h2_flow_mol_s"], target_w, temperature)
        
        # 3. 副產品累積與反饋模擬 (若結晶累積，會導致下一個時步的 clogging_factor 上升)
        # 實務中，若及時排液未做好，NaBO2 濃度過高會引發結晶堵塞
        if h2_res["nabo2_flow_kg_h"] > 0.4:
            clogging_factor += 0.015 # 模擬未及時沖洗反應床的催化劑衰減
            
        print(f"時間節點 {t+1}s | 目標需求: {target_w}W")
        print(f"  -> 即時產氫: {h2_res['h2_flow_nm3']:.3f} Nm3/h | 轉化率: {h2_res['actual_eta']*100:.1f}%")
        print(f"  -> 燃料電池輸出: {fc_res['output_power_w']/1000:.2f} kW | 電池堆電壓: {fc_res['v_stack_v']:.1f} V | 電流: {fc_res['current_a']:.1f} A")
        print(f"  -> 副產品 NaBO2 速率: {h2_res['nabo2_flow_kg_h']:.3f} kg/h | 觸媒床結塊因子: {clogging_factor*100:.1f}%")
        
        if fc_res['output_power_w'] < target_w * 0.95:
            print("  ⚠️ [警報] 產氫量供應不足或電池達到極限，輸出功率受限！")
        if clogging_factor > 0.1:
            print("  🚨 [維護提示] 副產品偏硼酸鈉累積過多，請啟動反沖洗液與排液模組！")
        print("-" * 70)
        time.sleep(0.5)