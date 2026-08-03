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

# 注入輕量 CSS，修復左側邊欄底部被卡住、無法拉到底的問題
st.markdown("""
    <style>
        [data-testid="stSidebarUserContent"] {
            padding-bottom: 80px;
        }
    </style>
""", unsafe_allow_html=True)

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
    # 側邊欄：開發平台品牌名稱與參數設定
    st.sidebar.markdown("## 💎 **Crystal Machine**")
    st.sidebar.caption("具身智能供應鏈測試平台 v1.0")
    st.sidebar.divider()
    
    st.sidebar.header("⚙️ 模組參數設定")
    module_name = st.sidebar.text_input("模組名稱 / 型號", "RGBD_Camera_X1")
    module_type = st.sidebar.selectbox("模組類別", ["感測模組", "夾爪/靈巧手", "馬達/關節", "控制/通訊", "AI運算", "電源/BMS"])
    samples = st.sidebar.slider("採集點數 (Samples)", 50, 500, 150)

    # 主畫面標題與台灣標準時間 (UTC+8)
    st.title("🤖 供應鏈模組標準測試平台 (MVP)")
    
    tw_time_str = datetime.now(TAIWAN_TZ).strftime("%Y-%m-%d %H:%M:%S (Asia/Taipei)")
    st.markdown(f"**系統測試時間（台灣標準時間）：** `{tw_time_str}`")
    st.caption("具身智能 LingBot-VLA 2.0 前置：模組本體性能評估系統 (50分制)")
    st.divider()

    tester = SupplyChainModuleTester(module_name, module_type)

    # 觸發測試按鈕
    if st.button("🚀 開始模組自動化測試 (Run Test)", type="primary"):
        with st.spinner("正在進行模組資料採集與 KPI 計算..."):
            df = tester.generate_simulated_data(samples=samples)
            results = tester.calculate_kpi()

        st.success("測試完成！已生成模組本體評估數據。")

        # Key Metrics 顯示區塊
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("平均延遲", f"{results['metrics']['avg_latency_ms']} ms")
        col2.metric("波形標準差 (雜訊)", f"{results['metrics']['voltage_std']}")
        col3.metric("平均功耗", f"{results['metrics']['avg_power_w']} W")
        col4.metric("本體總得分 (滿分50)", f"{results['scores']['total_base_score_50']} 分")

        st.divider()

        # 上層獨立區塊：採集波形與實時數據 (全寬高畫質呈現)
        st.subheader("📊 採集波形與實時數據")
        st.line_chart(df[['voltage_v', 'latency_ms']], use_container_width=True)

        st.divider()

        # 下層獨立區塊：標準模組數據卡與下載
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
        
        # 繪製乾淨大方的表格
        st.dataframe(summary_df, hide_index=True, use_container_width=True)
        
        # 轉換為帶 BOM 的 CSV/Excel 相容檔
        csv_data = summary_df.to_csv(index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="📥 下載 Excel / CSV 標準測試資料卡",
            data=csv_data,
            file_name=f"CrystalMachine_DataCard_{module_name}.csv",
            mime="text/csv",
            type="secondary"
        )

if __name__ == "__main__":
    main()