import time
import json
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
import streamlit as st

# 定義台灣標準時間 (UTC+8)
TAIWAN_TZ = timezone(timedelta(hours=8))

# ==========================================
# 1. 頁面基本配置 (Streamlit UI)
# ==========================================
st.set_page_config(
    page_title="Crystal Machine | 供應鏈模組標準測試平台",
    page_icon="🤖",
    layout="wide"
)

# ==========================================
# 2. 核心評分與數據處理類別 (KPI Engine)
# ==========================================
class SupplyChainModuleTester:
    def __init__(self, module_name, module_type, vendor=""):
        self.module_name = module_name
        self.module_type = module_type
        self.vendor = vendor
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

        # 使用原生 UTC+8 時間
        now_tw = datetime.now(TAIWAN_TZ).strftime("%Y-%m-%d %H:%M:%S (UTC+8)")

        self.kpi_results = {
            "platform": "Crystal Machine OS",
            "module_name": self.module_name,
            "module_type": self.module_type,
            "vendor": self.vendor,
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
    # 側邊欄：開發平台品牌名稱與參數設定
    st.sidebar.markdown("## 💎 **Crystal Machine**")
    st.sidebar.caption("具身智能供應鏈測試平台 v1.0")
    st.sidebar.divider()
    
    st.sidebar.header("⚙️ 模組參數設定")
    module_name = st.sidebar.text_input("模組名稱 / 型號", "RGBD_Camera_X1")
    module_type = st.sidebar.selectbox("模組類別", ["感測模組", "夾爪/靈巧手", "馬達/關節", "控制/通訊", "AI運算", "電源/BMS"])
    vendor = st.sidebar.text_input("供應商名稱", "Crystal Tech")
    samples = st.sidebar.slider("採集點數 (Samples)", 50, 500, 150)

    # 主畫面標題與台灣標準時間 (UTC+8)
    st.title("🤖 供應鏈模組標準測試平台 (MVP)")
    
    tw_time_str = datetime.now(TAIWAN_TZ).strftime("%Y-%m-%d %H:%M:%S (Asia/Taipei)")
    st.markdown(f"**系統測試時間（台灣標準時間）：** `{tw_time_str}`")
    st.caption("具身智能 LingBot-VLA 2.0 前置：模組本體性能評估系統 (50分制)")
    st.divider()

    tester = SupplyChainModuleTester(module_name, module_type, vendor)

    # 觸發測試按鈕
    if st.button("🚀 開始模組自動化測試 (Run Test)", type="primary"):
        with st.spinner("正在進行模組資料採集與 KPI 計算..."):
            df = tester.generate_simulated_data(samples=samples)
            results = tester.calculate_kpi()

        st.success("測試完成！已生成模組本體評估數據。")

        # Key Metrics 顯示
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("平均延遲", f"{results['metrics']['avg_latency_ms']} ms")
        col2.metric("波形標準差 (雜訊)", f"{results['metrics']['voltage_std']}")
        col3.metric("平均功耗", f"{results['metrics']['avg_power_w']} W")
        col4.metric("本體總得分 (滿分50)", f"{results['scores']['total_base_score_50']} 分")

        st.divider()

        # 雙欄版面：圖表與 JSON 資料卡
        left_col, right_col = st.columns([3, 2])

        with left_col:
            st.subheader("📊 採集波形與實時數據")
            st.line_chart(df[['voltage_v', 'latency_ms']])

        with right_col:
            st.subheader("📋 標準模組 JSON 資料卡")
            st.json(results)
            
            json_str = json.dumps(results, ensure_ascii=False, indent=4)
            st.download_button(
                label="📥 下載 JSON 資料卡",
                data=json_str,
                file_name=f"CrystalMachine_DataCard_{module_name}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()