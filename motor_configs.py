# motor_configs.py

# 定義電機平台數據，這就是模擬器的 TAD (Table-Driven) 基因庫
MOTOR_PLATFORMS = {
    "OD120": {
        "type": "PM",
        "peak_torque": 43,
        "peak_power": 14.8,
        "max_rpm": 9000,
        "voltage_range": [60, 72, 96],
        "cooling": "Air",
        "vendors": ["天津松正 (Santroll)", "安乃達 (Ananda)"]
    },
    "OD140": {
        "type": "PM",
        "peak_torque": 80,
        "peak_power": 30.0,
        "max_rpm": 9000,
        "voltage_range": [72, 96],
        "cooling": "Air",
        "vendors": ["天津松正 (Santroll)", "安乃達 (Ananda)"]
    },
    "OD220": {
        "type": "IPM",
        "peak_torque": 350,
        "peak_power": 150.0,
        "max_rpm": 15000,
        "voltage_range": [300, 400, 800],
        "cooling": "Water / Oil",
        "vendors": ["匯川技術 (Inovance)", "英威騰 (INVT)", "精進電動 (JJE)"]
    }
}