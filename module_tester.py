import time
import json
import io
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
import streamlit as st

# 定義台灣標準時間 (UTC+8)
TAIWAN_TZ = timezone(timedelta(hours=8))

# ==========================================
# 1. 頁面基本配置與 CSS 樣式微調 (Streamlit UI)
# ==========================================
st.set_page_config(
    page_title="Crystal Machine | 供應鏈模組標準測試平台",
    page_icon="🤖",
    layout="wide"
)

# 注入輕量 CSS，修復左側邊欄底部被卡住問題
st.markdown("""
    <style>
        [data-testid="stSidebarUserContent"] {
            padding-bottom: 80px;
        }
    </style>
""", unsafe_allow_html=True)

# 兩級聯動資料結構：6 大類別 -> 具體模組對照表
CATEGORY_MODULE_MAP = {
    "📷 感測模組": {
        "RGBD_Camera_X1 (深度攝影機)": "RGBD_Camera_X1",
        "LiDAR_3D_P1 (3D光學雷達)": "LiDAR_3D_P1",
        "✏️ 自訂感測模組": "CUSTOM"
    },
    "🦾 馬達 / 關節": {
        "Joint_Motor_42 (關節伺服馬達)": "Joint_Motor_42",
        "Servo_Actuator_80 (高扭力致動器)": "Servo_Actuator_80",
        "✏️ 自訂馬達/關節": "CUSTOM"
    },
    "🖐️ 夾爪 / 靈巧手": {
        "Dexterous_Hand_G1 (靈巧手模組)": "Dexterous_Hand_G1",
        "Parallel_Gripper_V2 (二指平行夾爪)": "Parallel_Gripper_V2",
        "✏️ 自訂夾爪/靈巧手": "CUSTOM"
    },
    "🧠 AI 運算": {
        "Jetson_Orin_Nano (AI運算板)": "Jetson_Orin_Nano",
        "Edge_AI_Accelerator_A1 (邊緣加速卡)": "Edge_AI_Accelerator_A1",
        "✏️ 自訂AI運算單元": "CUSTOM"
    },
    "📡 控制 / 通訊": {
        "CAN_Bus_Gateway_C1 (CAN通訊網關)": "CAN_Bus_Gateway_C1",
        "EtherCAT_Master_E1 (EtherCAT控制器)": "EtherCAT_Master_E1",
        "✏️ 自訂控制/通訊模組": "CUSTOM"
    },
    "⚡ 電源 / BMS": {
        "BMS_Module_24V (24V電池管理)": "BMS_Module_24V",
        "Power_Board_48V (48V主電源板)": "Power_Board_48V",
        "✏️ 自訂電源模組": "CUSTOM"
    }
}

# ==========================================
# 2. 核心評分與數據處理類別 (KPI Engine)
# ==========================================
class SupplyChainModuleTester:
    def __init__(self, module_name, module_type):
        self.module_name = module_name
        self.module_type = module_type
        self.raw_data = None
        self.kpi_results = {}

    def generate_simulated_data(self, samples=100, noise_level=0.05):
        np.random.seed(int(time.time()))
        base_signal = np.sin(np.linspace(0, 4 * np.pi, samples)) * 10 + 24.0
        noise = np.random.normal(0, noise_level, samples)
        
        timestamps = [time.time() + i * 0.01 for i in range(samples)]
        voltage = base_signal + noise
        current = np.random.uniform(0.5, 2.5, samples)
        latency_ms = np.random.normal(15.0, 2.0, samples)

        self.raw_data = pd.DataFrame({
            'timestamp': timestamps,
            'voltage_v': voltage,
            'current_a': current,
            'latency_ms': latency_ms
        })
        return self.raw_data

    def calculate_kpi(self):
        if self.raw_data is None:
            return None

        df = self.raw_data
        
        avg_latency = df['latency_ms'].mean()
        score_latency = 15.0 if avg_latency < 10 else (12.0 if avg_latency < 20 else 8.0)

        std_voltage = df['voltage_v'].std()
        score_stability = 15.0 if std_voltage < 0.1 else (11.0 if std_voltage < 0.5 else 6.0)

        avg_power = (df['voltage_v'] * df['current_a']).mean()
        score_power = 10.0 if avg_power < 50.0 else 7.0
        score_integration = 10.0

        total_base_score = score_latency + score_stability + score_power + score_integration

        now_tw = datetime.now(TAIWAN_TZ).strftime("%Y-%m-%d %H:%M:%S (UTC+8)")

        self.kpi_results = {
            "platform": "Crystal Machine OS",
            "module_name": self.module_name,
            "module_type": self.module_type,
            "test_time": now_tw,
            "metrics": {
                "avg_latency_ms": round(float(avg_latency), 2),
                "voltage_std": round(float(std_voltage), 4),
                "avg_power_w": round(float(avg_power), 2)
            },
            "scores": {
                "latency_score": score_latency,
                "stability_score": score_stability,
                "power_score": score_power,
                "integration_score": score_integration,
                "total_base_score_50": total_base_score
            }
        }
        return self.kpi_results


# ==========================================
# 3. Streamlit 網頁主渲染區塊
# ==========================================
def main():
    st.sidebar.markdown("## 💎 **Crystal Machine**")
    st.sidebar.caption("具身智能供應鏈測試平台 v1.0")
    st.sidebar.divider()
    
    st.sidebar.header("⚙️ 模組參數設定")
    
    # 兩級聯動區塊 1：選擇 6 大類別
    selected_category = st.sidebar.selectbox(
        "1. 選擇模組類別 (Category)",
        list(CATEGORY_MODULE_MAP.keys())
    )
    
    # 清理類別名稱（移除圖示），用於資料寫入
    clean_category_type = selected_category.split(" ")[1] if " " in selected_category else selected_category

    # 兩級聯動區塊 2：根據類別動態載入該類別的模組
    available_modules = CATEGORY_MODULE_MAP[selected_category]
    selected_module_label = st.sidebar.selectbox(
        "2. 選擇測試模組 (Module)",
        list(available_modules.keys())
    )
    
    # 判斷是否選擇自訂
    module_code = available_modules[selected_module_label]
    if module_code == "CUSTOM":
        module_name = st.sidebar.text_input("輸入自訂模組名稱 / 型號", "Custom_Device_01")
    else:
        module_name = module_code
        st.sidebar.info(f"**選定型號：** `{module_name}`\n\n**所屬類別：** `{clean_category_type}`")

    module_type = clean_category_type
    samples = st.sidebar.slider("採集點數 (Samples)", 50, 500, 150)

    # 主畫面標題與台灣標準時間 (UTC+8)
    st.title("🤖 供應鏈模組標準測試平台 (MVP)")
    
    tw_time_str = datetime.now(TAIWAN_TZ).strftime("%Y-%m-%d %H:%M:%S (Asia/Taipei)")
    st.markdown(f"**系統測試時間（台灣標準時間）：** `{tw_time_str}`")
    st.caption("具身智能 LingBot-VLA 2.0 前置：模組本體性能評估系統 (50分制)")
    st.divider()

    tester = SupplyChainModuleTester(module_name, module_type)

    if st.button("🚀 開始模組自動化測試 (Run Test)", type="primary"):
        with st.spinner(f"正在對 [{module_name}] 進行數據採集與分析..."):
            df = tester.generate_simulated_data(samples=samples)
            results = tester.calculate_kpi()

        st.success(f"測試完成！已生成 [{module_name}] 模組本體評估數據。")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("平均延遲", f"{results['metrics']['avg_latency_ms']} ms")
        col2.metric("波形標準差 (雜訊)", f"{results['metrics']['voltage_std']}")
        col3.metric("平均功耗", f"{results['metrics']['avg_power_w']} W")
        col4.metric("本體總得分 (滿分50)", f"{results['scores']['total_base_score_50']} 分")

        st.divider()

        # 上層獨立區塊：波形圖
        st.subheader("📊 採集波形與實時數據")
        st.line_chart(df[['voltage_v', 'latency_ms']], use_container_width=True)

        st.divider()

        # 下層獨立區塊：數據表與下載
        st.subheader("📋 標準模組數據卡 (Excel格式)")
        
        flat_data = {
            "項目 (Item)": [
                "開發平台 (Platform)",
                "模組名稱 (Module Name)",
                "模組類別 (Module Type)",
                "測試時間 (Test Time)",
                "平均延遲 (Avg Latency)",
                "波形雜訊/標準差 (Voltage Std)",
                "平均功耗 (Avg Power)",
                "延遲得分 (Latency Score)",
                "穩定度得分 (Stability Score)",
                "功耗得分 (Power Score)",
                "系統整合得分 (Integration Score)",
                "本體總得分 (Total Score / 50)"
            ],
            "數值 (Value)": [
                results["platform"],
                results["module_name"],
                results["module_type"],
                results["test_time"],
                f"{results['metrics']['avg_latency_ms']} ms",
                results['metrics']['voltage_std'],
                f"{results['metrics']['avg_power_w']} W",
                f"{results['scores']['latency_score']} / 15",
                f"{results['scores']['stability_score']} / 15",
                f"{results['scores']['power_score']} / 10",
                f"{results['scores']['integration_score']} / 10",
                f"{results['scores']['total_base_score_50']} / 50"
            ]
        }
        summary_df = pd.DataFrame(flat_data)
        
        st.dataframe(summary_df, hide_index=True, use_container_width=True)
        
        csv_data = summary_df.to_csv(index=False, encoding='utf-8-sig')
        
        st.download_button(
            label=f"📥 下載 [{module_name}] 標準測試資料卡 (Excel/CSV)",
            data=csv_data,
            file_name=f"CrystalMachine_DataCard_{module_name}.csv",
            mime="text/csv",
            type="secondary"
        )

if __name__ == "__main__":
    main()