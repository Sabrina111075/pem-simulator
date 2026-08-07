# ==========================================
# 1. MEMS Digital Library 欄位標準化資料庫 (大幅擴充版)
# ==========================================
# 納入全球主流 IMU 元件規格參數，支援消費級、工業級與高精度導航級型號
SENSOR_DB = {
    "BOSCH_BMI270": {
        "manufacturer": "BOSCH",
        "level": "消費級/人形機器人 (低成本方案)",
        "accel_noise_density": 0.00016,  # g/√Hz
        "gyro_noise_density": 0.007,     # dps/√Hz
        "accel_bias": 0.02,              # g
        "gyro_bias": 0.1,                # dps
        "range_accel": "±16g",
        "range_gyro": "±2000dps"
    },
    "TDK_ICM-42688-P": {
        "manufacturer": "TDK InvenSense",
        "level": "消費級/人形機器人 (高精準配置)",
        "accel_noise_density": 0.00007,  # g/√Hz (低噪)
        "gyro_noise_density": 0.0028,    # dps/√Hz
        "accel_bias": 0.01,              # g
        "gyro_bias": 0.05,               # dps
        "range_accel": "±16g",
        "range_gyro": "±2000dps"
    },
    "ANALOG_DEVICES_ADIS16488": {
        "manufacturer": "Analog Devices",
        "level": "戰術級/工業級高精度診斷 (高成本)",
        "accel_noise_density": 0.000016, # g/√Hz (極低噪)
        "gyro_noise_density": 0.00015,   # dps/√Hz (超高穩定度)
        "accel_bias": 0.002,             # g
        "gyro_bias": 0.008,              # dps
        "range_accel": "±40g",
        "range_gyro": "±2000dps"
    },
    "INNOMOTION_ICM-20689": {
        "manufacturer": "芯動聯科 (InnoMotion)",
        "level": "工業級/車載級/無人機穩定系統",
        "accel_noise_density": 0.00009,  # g/√Hz
        "gyro_noise_density": 0.004,     # dps/√Hz
        "accel_bias": 0.015,             # g
        "gyro_bias": 0.07,               # dps
        "range_accel": "±16g",
        "range_gyro": "±2000dps"
    },
    "QST_QMI8658C": {
        "manufacturer": "啟明創感 (QST)",
        "level": "消費級/物聯網/低成本模組化設計",
        "accel_noise_density": 0.00022,  # g/√Hz
        "gyro_noise_density": 0.012,     # dps/√Hz
        "accel_bias": 0.03,              # g
        "gyro_bias": 0.15,               # dps
        "range_accel": "±16g",
        "range_gyro": "±2000dps"
    }
}