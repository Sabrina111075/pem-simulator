import random

def get_pogo_pin_definition():
    """
    符合 Crystal Machine 專利 Figure 5 定義之 12 Pin Pogo Pin 電氣接腳與並聯設計
    """
    return [
        {"Pin": 1, "訊號名稱": "VBUS", "電壓/狀態": "5V~20V 輸入正常", "專利功能說明": "電源輸入 (採雙接腳並聯提高負載能力)"},
        {"Pin": 2, "訊號名稱": "GND", "電壓/狀態": "0V 接地正常", "專利功能說明": "系統公共接地 (採雙接腳並聯降低迴路阻抗)"},
        {"Pin": 3, "訊號名稱": "3V3", "電壓/狀態": "3.3V / 穩定", "專利功能說明": "數位核心與外部感知模組供電 (Max 1A)"},
        {"Pin": 4, "訊號名稱": "SDA", "電壓/狀態": "I2C 數據線 正常", "專利功能說明": "I2C 串列資料傳輸線"},
        {"Pin": 5, "訊號名稱": "SCL", "電壓/狀態": "I2C 時鐘線 正常", "專利功能說明": "I2C 串列時鐘同步線"},
        {"Pin": 6, "訊號名稱": "TXD", "電壓/狀態": "UART Tx 空閒", "專利功能說明": "MCU 序列傳送端 (對接 ESP32-S3)"},
        {"Pin": 7, "訊號名稱": "RXD", "電壓/狀態": "UART Rx 接收中", "專利功能說明": "MCU 序列接收端 (對接 ESP32-S3)"},
        {"Pin": 8, "訊號名稱": "GPIO1", "電壓/狀態": "HIGH (中斷觸發)", "專利功能說明": "通用輸入輸出/熱插拔硬體中斷線"},
        {"Pin": 9, "訊號名稱": "GPIO2", "電壓/狀態": "LOW", "專利功能說明": "通用輸入輸出控制線"},
        {"Pin": 10, "訊號名稱": "USB_D+", "電壓/狀態": "未啟動", "專利功能說明": "USB 2.0 高速差動訊號 +"},
        {"Pin": 11, "訊號名稱": "USB_D-", "電壓/狀態": "未啟動", "專利功能說明": "USB 2.0 高速差動訊號 -"},
        {"Pin": 12, "訊號名稱": "ID", "電壓/狀態": "已讀取 1-Wire EEPROM", "專利功能說明": "模組 ID 識別碼與熱插拔自動驅動配置"}
    ]

def get_catalog_config(volume_name):
    """
    將 10 大產品型錄(Vol.1 - Vol.10)封裝進 A/B/C/D 四大類模組生態系
    """
    config = {}
    
    if "Vol. 1" in volume_name:
        config = {
            "slots": {"A1": "🔴 未配置", "A2": "🟢 已連接 (ID: A-202 高精度IMU)", "B1": "🔴 未配置", "B2": "🟢 已連接 (ID: B-101 Wi-Fi)", "C1": "🟢 已連接 (ID: C-302 固態LiDAR)", "D1": "🟢 供電中 (ID: D-401 動力電池)"},
            "skills": "🤖 載入 Skill Card：【運動控制與路徑規劃 Agent 服務】",
            "metrics": {"m1": (random.randint(20, 30), "目前移動時速 (km/h)"), "m2": (random.randint(110, 120), "馬達輪轂轉速 (RPM)"), "m3": (random.randint(5, 15), "LiDAR 障礙物探測距離 (m)")}
        }
    elif "Vol. 2" in volume_name:
        config = {
            "slots": {"A1": "🟢 已連接 (ID: A-01 氣壓計)", "A2": "🔴 未配置", "B1": "🟢 已連接 (ID: B-202 5G模組)", "B2": "🔴 未配置", "C1": "🔴 未配置", "D1": "🟢 供電中 (ID: D-401 標準電源)"},
            "skills": "🌦️ 載入 Skill Card：【邊緣端微氣象環境預測模型】",
            "metrics": {"m1": (random.randint(1008, 1013), "大氣壓力 (hPa)"), "m2": (random.randint(60, 75), "環境相對濕度 (%)"), "m3": (round(random.uniform(25.0, 28.5), 1), "大氣環境溫度 (°C)")}
        }
    elif "Vol. 3" in volume_name:
        config = {
            "slots": {"A1": "🟢 已連接 (ID: A-05 土壤NPK)", "A2": "🔴 未配置", "B1": "🟢 已連接 (ID: B-205 LoRa網關)", "B2": "🔴 未配置", "C1": "🟢 已連接 (ID: C-110 縮時定焦相機)", "D1": "🟢 供電中 (ID: D-402 太陽能管理)"},
            "skills": "🌾 載入 Skill Card：【精準農業與作物病蟲害 AI 影像辨識演算法】",
            "metrics": {"m1": (random.randint(15, 25), "土壤含水量 (%)"), "m2": (random.randint(200, 250), "土壤氮磷鉀總量 (mg/kg)"), "m3": (random.randint(4000, 5000), "環境光照強度 (Lux)")}
        }
    elif "Vol. 4" in volume_name:
        config = {
            "slots": {"A1": "🟢 已連接 (ID: A-09 CO2感測器)", "A2": "🔴 未配置", "B1": "🔴 未配置", "B2": "🟢 已連接 (ID: B-101 Wi-Fi)", "C1": "🟢 已連接 (ID: C-201 人流監測相機)", "D1": "🟢 供電中 (ID: D-401 標準電源)"},
            "skills": "🏢 載入 Skill Card：【智慧建築空間節能與動態人流調度演算法】",
            "metrics": {"m1": (random.randint(450, 600), "室內二氧化碳濃度 (ppm)"), "m2": (random.randint(12, 45), "當前空間人流總數 (人)"), "m3": (random.randint(22, 24), "區域空調設定目標值 (°C)")}
        }
    elif "Vol. 5" in volume_name:
        config = {
            "slots": {"A1": "🔴 未配置", "A2": "🔴 未配置", "B1": "🟢 已連接 (ID: B-201 千兆乙太網)", "B2": "🔴 未配置", "C1": "🟢 已連接 (ID: C-501 工業高幀相機)", "D1": "🟢 供電中 (ID: D-405 外接DC電源)"},
            "skills": "🏭 載入 Skill Card：【工業 AOI 瑕疵檢測與邊緣視覺神經網路】",
            "metrics": {"m1": (round(random.uniform(99.4, 99.9), 2), "AI 即時瑕疵檢測良率 (%)"), "m2": (random.randint(1200, 1500), "生產流水線流速 (pcs/h)"), "m3": (random.randint(12, 18), "Edge GPU 核心運行溫度 (°C)")}
        }
    elif "Vol. 6" in volume_name:
        config = {
            "slots": {"A1": "🟢 已連接 (ID: A-102 生理感測器)", "A2": "🟢 已連接 (ID: A-105 跌倒IMU)", "B1": "🟢 已連接 (ID: B-201 5G/LoRa中樞)", "B2": "🟢 已連接 (ID: B-102 藍牙閘道器)", "C1": "🟡 尋找設備中 (預留熱插拔)", "D1": "🟢 供電中 (ID: D-401 醫療UPS)"},
            "skills": "🏥 載入 Skill Card：【地端 DeepSeek 臨床健康照護與生理異常診斷提示詞】",
            "metrics": {"m1": (random.randint(72, 79), "❤️ 即時心率 (BPM)"), "m2": (random.randint(95, 99), "🩸 血氧飽和度 (SpO2 %)"), "m3": (round(random.uniform(36.2, 37.3), 1), "🌡️ 當前核心體溫 (°C)")}
        }
    elif "Vol. 7" in volume_name:
        config = {
            "slots": {"A1": "🟢 已連接 (ID: A-80 電化學動態分析)", "A2": "🔴 未配置", "B1": "🟢 已連接 (ID: B-202 5G通訊)", "B2": "🔴 未配置", "C1": "🔴 未配置", "D1": "🟢 供電中 (ID: D-409 大功率大電流模組)"},
            "skills": "🔋 載入 Skill Card：【PEM 電解槽 Butler-Volmer 極化曲線數位雙生模擬模型】",
            "metrics": {"m1": (round(random.uniform(1.7, 1.9), 2), "電解槽單體活化電壓 (V)"), "m2": (random.randint(450, 500), "實時產氫流量速度 (L/h)"), "m3": (random.randint(75, 82), "質子交換膜當前工作溫度 (°C)")}
        }
    elif "Vol. 8" in volume_name:
        config = {
            "slots": {"A1": "🟢 已連接 (ID: A-91 高頻震動感測)", "A2": "🔴 未配置", "B1": "🟢 已連接 (ID: B-105 車載CAN-Bus)", "B2": "🔴 未配置", "C1": "🔴 未配置", "D1": "🟢 供電中 (ID: D-401 車載電源轉換)"},
            "skills": "🛵 載入 Skill Card：【BMW i3 馬達異常診斷與 Burg 訊號特徵老化預測】",
            "metrics": {"m1": (random.randint(3200, 3500), "電動機轉子旋轉轉速 (RPM)"), "m2": (random.randint(65, 78), "功率逆變器 IGBT 溫度 (°C)"), "m3": (round(random.uniform(0.02, 0.08), 3), "前後軸承高頻震動加速度 (g)")}
        }
    elif "Vol. 9" in volume_name:
        config = {
            "slots": {"A1": "🔴 未配置", "A2": "🟢 已連接 (ID: A-12 高精度九軸IMU)", "B1": "🟢 已連接 (ID: B-401 高頻圖傳)", "B2": "🔴 未配置", "C1": "🟢 已連接 (ID: C-09 紅外熱像儀)", "D1": "🟢 供電中 (ID: D-412 高倍率動力電池)"},
            "skills": "🛸 載入 Skill Card：【無人機邊緣安防與地端多目標追蹤與避障 Agent】",
            "metrics": {"m1": (random.randint(85, 120), "雷達相對飛行高度 (m)"), "m2": (random.randint(88, 94), "動力電池剩餘電量百分比 (%)"), "m3": (random.randint(0, 3), "地面熱源異常鎖定目標數")}
        }
    elif "Vol. 10" in volume_name:
        config = {
            "slots": {"A1": "🟢 已連接 (ID: A-33 溫度紀錄計)", "A2": "🔴 未配置", "B1": "🟢 已連接 (ID: B-201 全球5G數據端)", "B2": "🔴 未配置", "C1": "🔴 未配置", "D1": "🟢 供電中 (ID: D-401 車載線路供電)"},
            "skills": "📦 載入 Skill Card：【冷鏈物流物資動態追蹤與邊緣軌跡最佳化調度演算法】",
            "metrics": {"m1": (round(random.uniform(-22.0, -18.0), 1), "高真空冷凍貨艙即時溫度 (°C)"), "m2": (random.randint(85, 90), "密閉車廂內相對濕度 (%)"), "m3": (random.randint(1, 5), "預計抵達下一物流轉運節點時間 (h)")}
        }
        
    return config