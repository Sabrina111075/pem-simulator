# simulation_engine.py
import numpy as np

def calculate_torque_curve(peak_torque, peak_power, max_rpm):
    rpms = np.linspace(0, max_rpm, 100)
    base_rpm = (peak_power * 9550) / peak_torque
    torques = []
    for n in rpms:
        if n <= base_rpm:
            torques.append(peak_torque)
        else:
            t_at_n = (peak_power * 9550) / n
            torques.append(t_at_n)
    return rpms, torques

def calculate_gradeability(torque, vehicle_mass, gear_ratio, tire_radius):
    """
    計算最大爬坡度 (%)
    公式：坡度力 = (扭矩 * 減速比) / 輪胎半徑
    """
    # 簡化物理模型：忽略滾阻與風阻，計算極限靜態爬坡力
    force_wheels = (torque * gear_ratio) / tire_radius
    gravity = vehicle_mass * 9.81
    # sin(theta) = Force / Gravity
    if force_wheels / gravity >= 1:
        return 100.0
    sin_theta = force_wheels / gravity
    tan_theta = np.tan(np.arcsin(sin_theta))
    return round(tan_theta * 100, 1)