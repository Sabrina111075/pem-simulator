import time
import json
import numpy as np
import pandas as pd
from datetime import datetime

# ==========================================
# 1. 核心評分與數據處理類別 (KPI Engine)
# ==========================================
class SupplyChainModuleTester:
    """
    供應鏈模組標準測試平台 - 輕量版 KPI 評分引擎
    負責計算模組本體基本性能 (滿分 50 分)
    """
    def __init__(self, module_name, module_type, vendor=""):
        self.module_name = module_name
        self.module_type = module_type
        self.vendor = vendor
        self.raw_data = None
        self.kpi_results = {}

    def generate_simulated_data(self, samples=100, noise_level=0.05):
        """
        模擬測試資料（適合無實體硬體連線時測試 UI 與邏輯）
        """
        np.random.seed(int(time.time()))
        base_signal = np.sin(np.linspace(0, 4 * np.pi, samples)) * 10 + 24.0  # 模擬 24V 基準訊號
        noise = np.random.normal(0, noise_level, samples)
        
        # 模擬採集到的電壓、電流與延遲數據
        timestamps = [time.time() + i * 0.01 for i in range(samples)]
        voltage = base_signal + noise
        current = np.random.uniform(0.5, 2.5, samples)
        latency_ms = np.random.normal(15.0, 2.0, samples) # 平均延遲 15ms

        self.raw_data = pd.DataFrame({
            'timestamp': timestamps,
            'voltage_v': voltage,
            'current_a': current,
            'latency_ms': latency_ms
        })
        return self.raw_data

    def calculate_kpi(self):
        """
        計算模組本體性能指標與評分（50分制）
        """
        if self.raw_data is None:
            raise ValueError("尚未匯入或產生任何測試數據！")

        df = self.raw_data
        
        # 1. 延遲指標 (15分)
        avg_latency = df['latency_ms'].mean()
        if avg_latency < 10:
            score_latency = 15.0
        elif avg_latency < 20:
            score_latency = 12.0
        else:
            score_latency = 8.0

        # 2. 訊號穩定性/標準差指標 (15分)
        std_voltage = df['voltage_v'].std()
        if std_voltage < 0.1:
            score_stability = 15.0
        elif std_voltage < 0.5:
            score_stability = 11.0
        else:
            score_stability = 6.0

        # 3. 平均功耗 P = V * I (10分)
        avg_power = (df['voltage_v'] * df['current_a']).mean()
        score_power = 10.0 if avg_power < 50.0 else 7.0

        # 4. 基礎整合與合規性 (10分 - 預設滿分，後續可改為勾選項)
        score_integration = 10.0

        total_base_score = score_latency + score_stability + score_power + score_integration

        self.kpi_results = {
            "module_name": self.module_name,
            "module_type": self.module_type,
            "vendor": self.vendor,
            "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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

    def export_data_card_json(self, filename=None):
        """匯出為標準模組 JSON 資料卡"""
        if not self.kpi_results:
            self.calculate_kpi()
        
        if filename is None:
            filename = f"DataCard_{self.module_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.kpi_results, f, ensure_ascii=False, indent=4)
        
        print(f"已成功匯出標準資料卡：{filename}")
        return filename


# ==========================================
# 2. 本地測試 & 未來 Streamlit 整合入口
# ==========================================
def run_local_cli_test():
    """
    當前在 Local 環境下運行的 CLI 測試流程
    """
    print("=== 供應鏈模組標準測試平台 (Local MVP) ===")
    
    # 建立模組測試實例
    tester = SupplyChainModuleTester(
        module_name="RGBD_Camera_X1", 
        module_type="感測模組", 
        vendor="Crystal Tech"
    )

    print("\n1. 正在模擬採集感測器數據...")
    df = tester.generate_simulated_data(samples=200)
    print(f"   採集完成，共 {len(df)} 筆數據。數據預覽：")
    print(df.head(3))

    print("\n2. 正在計算 50 分制模組本體 KPI...")
    results = tester.calculate_kpi()
    
    print("\n3. 評估結果摘要：")
    print(f"   - 模組名稱: {results['module_name']}")
    print(f"   - 平均延遲: {results['metrics']['avg_latency_ms']} ms")
    print(f"   - 訊號波幅標準差: {results['metrics']['voltage_std']}")
    print(f"   - 平均功耗: {results['metrics']['avg_power_w']} W")
    print(f"   - 模組本體總得分: {results['scores']['total_base_score_50']} / 50 分")

    print("\n4. 匯出標準 JSON 資料卡...")
    tester.export_data_card_json("local_test_datacard.json")


if __name__ == "__main__":
    # 在本地執行 py 檔時會執行這個測試
    run_local_cli_test()