import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. 網頁全域配置與主題設定
# ==========================================
st.set_page_config(
    page_title="NaBH4 硼氫化鈉燃料電池系統模擬平台",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 核心物理化學數學模型類別
# ==========================================
class NaBH4FuelCellSystem:
    def __init__(self):
        # 基礎通用物理常數
        self.R = 8.314462    # 理想氣體常數 (J/(mol·K))
        self.F = 96485.332   # 法拉第常數 (C/mol)
        self.n = 8           # NaBH4 完全氧化反應轉移電子數 (8電子反應)
        
    def solve_butler_volmer_overpotential(self, i_density, T_k, i_0, alpha=0.5):
        """
        使用二分法(Bisection Method)精準求解非線性 Butler-Volmer 方程式中的活化超電勢 (eta_act)
        方程式: i = i_0 * ( exp(alpha * n * F * eta / (R * T)) - exp(-(1 - alpha) * n * F * eta / (R * T)) )
        """
        if i_density <= 0:
            return 0.0
            
        # 定義殘差函數
        def residual(eta):
            term_ano = np.exp((alpha * self.n * self.F * eta) / (self.R * T_k))
            term_cat = np.exp(-((1 - alpha) * self.n * self.F * eta) / (self.R * T_k))
            return i_0 * (term_ano - term_cat) - i_density
            
        # 二分法尋根
        low, high = 0.0, 2.0
        for _ in range(100):
            mid = (low + high) / 2.0
            res = residual(mid)
            if abs(res) < 1e-6:
                return mid
            if res > 0:
                high = mid
            else:
                low = mid
        return (low + high) / 2.0

    def simulate_polarization_curve(self, params):
        """
        生成完整的極化曲線數據
        """
        current_densities = np.linspace(0.001, params['max_i'], 100)
        v_cell_list = []
        eta_act_list = []
        eta_ohmic_list = []
        eta_conc_list = []
        power_density_list = []
        
        T_k = params['temperature'] + 273.15
        
        for i_den in current_densities:
            # 1. 熱力學平衡電勢 (Nernst 修正估算)
            E_0 = params['E_thermo'] - 0.0006 * (params['temperature'] - 25.0)
            
            # 2. 活化損失 (Butler-Volmer 求解)
            eta_act = self.solve_butler_volmer_overpotential(i_den, T_k, params['i_0'], params['alpha'])
            
            # 3. 歐姆損失
            eta_ohmic = i_den * params['r_internal']
            
            # 4. 濃差損失
            if i_den >= params['i_limit']:
                eta_conc = 0.5  # 超過極限電流時強制飽和防崩潰
            else:
                eta_conc = - (self.R * T_k / (params['alpha'] * self.n * self.F)) * np.log(1 - (i_den / params['i_limit']))
                
            # 5. 實際單體電勢
            v_cell = E_0 - eta_act - eta_ohmic - eta_conc
            if v_cell < 0:
                v_cell = 0.0
                
            power_density = v_cell * i_den
            
            v_cell_list.append(v_cell)
            eta_act_list.append(eta_act)
            eta_ohmic_list.append(eta_ohmic)
            eta_conc_list.append(eta_conc)
            power_density_list.append(power_density)
            
        return pd.DataFrame({
            'Current_Density': current_densities * 1000, # 轉換為 mA/cm²
            'Cell_Voltage': v_cell_list,
            'Activation_Loss': eta_act_list,
            'Ohmic_Loss': eta_ohmic_list,
            'Concentration_Loss': eta_conc_list,
            'Power_Density': np.array(power_density_list) * 1000 # 轉換為 mW/cm²
        })

# ==========================================
# 3. 側邊欄 (Sidebar) 介面設計
# ==========================================
st.sidebar.markdown("### 🏢 前瞻綠能與動力系統實驗室")
st.sidebar.markdown("---")
st.sidebar.header("⚙️ 系統核心工程參數設定")

# 初始化物理模型
model = NaBH4FuelCellSystem()

# 基礎工程參數調整區
E_thermo = st.sidebar.slider("熱力學理論電勢 (V)", 1.20, 1.64, 1.64, 0.01)
temperature = st.sidebar.slider("系統工作溫度 (°C)", 20.0, 80.0, 60.0, 1.0)
i_0 = st.sidebar.number_input("交換電流密度 i₀ (A/cm²)", min_value=1e-6, max_value=1e-1, value=1e-3, format="%.6f")
alpha = st.sidebar.slider("電荷傳遞係數 α", 0.1, 0.9, 0.5, 0.05)
r_internal = st.sidebar.number_input("內部歐姆電阻 R_int (Ω·cm²)", min_value=0.01, max_value=2.00, value=0.15, step=0.01)
i_limit = st.sidebar.slider("極限擴散電流密度 i_lim (A/cm²)", 0.5, 3.0, 1.5, 0.1)
max_i = st.sidebar.slider("模擬最大掃描電流密度 (A/cm²)", 0.4, 2.8, 1.4, 0.1)

# ==========================================
# 4. 主畫面 - 10 大應用場景快速切換
# ==========================================
st.title("🧪 NaBH₄ Direct Fuel Cell (DBFC) 數位雙生模擬平台")
st.markdown("本系統整合 **TAD-AGE** 架構，精準預估動態反應速率、活化過電勢與極化特性曲線。")

st.subheader("🌐 選擇特定部署與應用場景 (Scenarios)")

# 10 大應用場景字典定義
scenarios = {
    "1. 智能倉儲自動搬運車 (AGV / AMR)": {"temperature": 45.0, "i_0": 0.002, "r_internal": 0.12, "i_limit": 1.6, "desc": "高頻率起停、室內恆溫，著重在中低電流密度的長期歐姆穩定性。"},
    "2. 長航時工業級無人機 (UAV)": {"temperature": 35.0, "i_0": 0.0008, "r_internal": 0.18, "i_limit": 1.2, "desc": "高空低氣壓、散熱快，要求極高功率重量比，操作區間偏向高功率輸出點。"},
    "3. 偏遠離島微電網後備電源": {"temperature": 65.0, "i_0": 0.005, "r_internal": 0.10, "i_limit": 1.8, "desc": "高溫高溫濕環境，燃料利用率最大化，適合做高效率的基載電力調度。"},
    "4. 國防可攜式單兵作戰裝備": {"temperature": 25.0, "i_0": 0.0005, "r_internal": 0.25, "i_limit": 0.8, "desc": "環境惡劣且多變，工作溫度低導致動力學較慢，主要確保基本通訊電力。"},
    "5. 海洋觀測浮標與水下無人載具": {"temperature": 20.0, "i_0": 0.0004, "r_internal": 0.22, "i_limit": 0.9, "desc": "低溫高壓環境，封閉系統。硼氫化鈉能量密度高，極適合水下無空氣燃料電池運作。"},
    "6. 5G 通訊基地台緊急備援系統": {"temperature": 55.0, "i_0": 0.003, "r_internal": 0.11, "i_limit": 1.7, "desc": "著重長達數十小時的連續定電壓輸出，熱管理系統須保持在高效區。"},
    "7. 野外緊急醫療行動工作站": {"temperature": 40.0, "i_0": 0.0015, "r_internal": 0.14, "i_limit": 1.4, "desc": "模組化快速啟動設計，平衡活化損失與噪音控制。"},
    "8. 綠能製氫加氫站負載動態調節": {"temperature": 70.0, "i_0": 0.008, "r_internal": 0.08, "i_limit": 2.2, "desc": "高溫運作，動力學極佳。用於平抑再生能源電網的劇烈波動。"},
    "9. 極地科考站極端低溫維生系統": {"temperature": 30.0, "i_0": 0.0006, "r_internal": 0.28, "i_limit": 0.9, "desc": "外部零下環境，依賴電池本體放電產生的廢熱進行自加熱自保溫。"},
    "10. 航天輔助動力單元 (APU)": {"temperature": 75.0, "i_0": 0.010, "r_internal": 0.07, "i_limit": 2.5, "desc": "高技術指標場景，催化劑活性全開，歐姆阻抗降至最低，追求極致性能。"}
}

selected_scenario_name = st.selectbox("請選擇應用場景以載入預設特徵參數：", list(scenarios.keys()))
scenario_data = scenarios[selected_scenario_name]

# 提供場景參數一鍵套用覆蓋按鈕
if st.button(f"🚀 一鍵套用「{selected_scenario_name}」特徵參數"):
    temperature = scenario_data["temperature"]
    i_0 = scenario_data["i_0"]
    r_internal = scenario_data["r_internal"]
    i_limit = scenario_data["i_limit"]
    st.success(f"已成功同步載入：{selected_scenario_name} 的工程邊界條件！")

st.info(f"💡 **當前場景情境說明：** {scenario_data['desc']}")

# ==========================================
# 5. 執行數值模擬計算
# ==========================================
current_params = {
    'E_thermo': E_thermo,
    'temperature': temperature,
    'i_0': i_0,
    'alpha': alpha,
    'r_internal': r_internal,
    'i_limit': i_limit,
    'max_i': max_i
}

sim_results = model.simulate_polarization_curve(current_params)

# ==========================================
# 6. 數據視覺化圖表呈現 (Plotly)
# ==========================================
st.markdown("---")
st.subheader("📊 模擬數據整合可視化面板")

col1, col2 = st.columns(2)

with col1:
    # 畫出極化與功率密度曲線
    fig_polar = go.Figure()
    fig_polar.add_trace(go.Scatter(x=sim_results['Current_Density'], y=sim_results['Cell_Voltage'],
                        mode='lines', name='單體電勢 (V)', line=dict(color='royalblue', width=3)))
    fig_polar.add_trace(go.Scatter(x=sim_results['Current_Density'], y=sim_results['Power_Density'],
                        mode='lines', name='功率密度 (mW/cm²)', line=dict(color='firebrick', width=3), yaxis='y2'))
    
    fig_polar.update_layout(
        title='⚡ DBFC 極化曲線與功率密度曲線 (Polarization & Power Density)',
        xaxis=dict(title='電流密度 Current Density (mA/cm²)'),
        yaxis=dict(title='單體電勢 Voltage (V)', titlefont=dict(color='royalblue'), tickfont=dict(color='royalblue')),
        yaxis2=dict(title='功率密度 Power Density (mW/cm²)', titlefont=dict(color='firebrick'), tickfont=dict(color='firebrick'), anchor='x', overlaying='y', side='right'),
        legend=dict(x=0.05, y=0.1),
        hovermode="x unified"
    )
    st.plotly_chart(fig_polar, use_container_width=True)

with col2:
    # 畫出各項過電勢損失分佈圖
    fig_loss = go.Figure()
    fig_loss.add_trace(go.Scatter(x=sim_results['Current_Density'], y=sim_results['Activation_Loss'],
                        mode='lines', name='活化損失 (Activation)', line=dict(dash='dash', color='orange')))
    fig_loss.add_trace(go.Scatter(x=sim_results['Current_Density'], y=sim_results['Ohmic_Loss'],
                        mode='lines', name='歐姆損失 (Ohmic)', line=dict(dash='dot', color='green')))
    fig_loss.add_trace(go.Scatter(x=sim_results['Current_Density'], y=sim_results['Concentration_Loss'],
                        mode='lines', name='濃差損失 (Concentration)', line=dict(dash='dashdot', color='purple')))
    
    fig_loss.update_layout(
        title='📉 三大核心過電勢(損失)動態解析',
        xaxis=dict(title='電流密度 Current Density (mA/cm²)'),
        yaxis=dict(title='過電勢 Overpotential Loss (V)'),
        legend=dict(x=0.05, y=0.9),
        hovermode="x unified"
    )
    st.plotly_chart(fig_loss, use_container_width=True)

# ==========================================
# 7. 數據總結報告區
# ==========================================
max_power_idx = sim_results['Power_Density'].idxmax()
max_power_row = sim_results.iloc[max_power_idx]

st.markdown("---")
st.subheader("🏁 系統操作最優效能特徵總結")
m_col1, m_col2, m_col3 = st.columns(3)

m_col1.metric("최대 功率輸出點", f"{max_power_row['Power_Density']:.2f} mW/cm²")
m_col2.metric("最優操作電流密度", f"{max_power_row['Current_Density']:.1f} mA/cm²")
m_col3.metric("最優操作電勢點", f"{max_power_row['Cell_Voltage']:.3f} V")