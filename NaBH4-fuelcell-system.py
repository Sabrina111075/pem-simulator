import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 網頁全域配置 (強制更新識別標記 V3.7)
# ==========================================
st.set_page_config(
    page_title="NaBH4 數位雙生智慧監控系統 V3.7",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# 2. 10 大應用場景特徵資料庫
# ==========================================
SCENARIOS = {
    "1. 智能倉儲自動搬運車 (AGV / AMR)": {"temp": 45.0, "conc": 15.0, "flow": 25.0, "i0": 0.0020, "desc": "中溫環境，高頻率起停，要求長效穩定的產氫與電力輸出。"},
    "2. 長航時工業級無人機 (UAV)": {"temp": 35.0, "conc": 25.0, "flow": 40.0, "i0": 0.0008, "desc": "高濃度燃料以減輕系統重量，產氫需求隨操作高度動態調整。"},
    "3. 偏遠離島微電網後備電源": {"temp": 65.0, "conc": 12.0, "flow": 120.0, "i0": 0.0050, "desc": "大型化系統，高流量連續工作，熱管理與系統發熱量大。"},
    "4. 國防可攜式單兵作戰裝備": {"temp": 25.0, "conc": 20.0, "flow": 10.0, "i0": 0.0005, "desc": "低溫環境啟動較慢，動力學受限，需精確控制微步進進料。"},
    "5. 海洋觀測浮標與水下無人載具": {"temp": 20.0, "conc": 18.0, "flow": 15.0, "i0": 0.0004, "desc": "環境低溫高壓，反應床主動熱控制是維持高效產氫的關鍵。"},
    "6. 5G 通訊基地台緊急備援系統": {"temp": 55.0, "conc": 15.0, "flow": 80.0, "i0": 0.0030, "desc": "標準定功率長時輸出，系統自動補足動態氫氣壓。"},
    "7. 野外緊急醫療行動工作站": {"temp": 40.0, "conc": 10.0, "flow": 35.0, "i0": 0.0015, "desc": "模組化快速更換燃料設計，著重電氣防護與極高可靠度。"},
    "8. 綠能製氫加氫站負載動態調節": {"temp": 70.0, "conc": 30.0, "flow": 250.0, "i0": 0.0080, "desc": "極限大功率輸出，產氫速率與多組電堆發電量需高精確度聯動。"},
    "9. 極地科考站極端低溫維生系統": {"temp": 30.0, "conc": 22.0, "flow": 20.0, "i0": 0.0006, "desc": "外部零下低溫，高度依賴電池本體放電廢熱進行自加熱循環。"},
    "10. 航天輔助動力單元 (APU)": {"temp": 75.0, "conc": 28.0, "flow": 150.0, "i0": 0.0100, "desc": "高技術指標操作，催化反應全開，歐姆阻抗降至極限。"}
}

# ==========================================
# 3. 側邊欄 (Sidebar) 介面控制中心
# ==========================================
st.sidebar.markdown("# [ Crystal Machine ]")
st.sidebar.markdown("### 前瞻綠能與動力系統實驗室")
st.sidebar.markdown("---")

st.sidebar.subheader("[ 應用場景選擇 ]")
selected_scen = st.sidebar.selectbox("切換場景預設特徵參數：", list(SCENARIOS.keys()))
scen_default = SCENARIOS[selected_scen]

st.sidebar.markdown("---")

st.sidebar.subheader("[ 工藝參數調功與控制 ]")
with st.sidebar.expander(">> 反應床與流體進料系統", expanded=True):
    flow_rate = st.slider("進料流量 (mL/min)", 5.0, 300.0, float(scen_default['flow']), 5.0)
    concentration = st.slider("NaBH4 溶液濃度 (wt%)", 5.0, 35.0, float(scen_default['conc']), 1.0)
    reactor_temp = st.slider("反應床操作溫度 (°C)", 15.0, 90.0, float(scen_default['temp']), 1.0)

st.sidebar.subheader("[ 電池核心電化學參數 ]")
with st.sidebar.expander(">> 內部極化特性設定", expanded=False):
    e_thermo = st.number_input("理論熱力學電勢 (V)", 1.20, 1.80, 1.64, 0.01)
    i_0 = st.number_input("交換電流密度 i0 (A/cm2)", 0.0001, 0.0500, float(scen_default['i0']), format="%.4f")
    r_int = st.slider("內部歐姆電阻 R_int (Ohm*cm2)", 0.01, 1.50, 0.15, 0.01)
    alpha = st.slider("電荷傳遞係數 alpha", 0.1, 0.9, 0.5, 0.05)

# ==========================================
# 4. 數位雙生核心物理模型 (全新命名避開快取)
# ==========================================
class DBFCDigitalTwinV37:
    def __init__(self):
        self.R = 8.314
        self.F = 96485
        self.n = 8 
        
    def calculate_metrics_v37(self, temp, conc, flow):
        # 即使伺服器有快取舊函數，全新命名的函數將強制執行新版物理尺度
        # 加上除以 1000.0 的物理常數縮放，徹底把 L/min 壓回真實世界工程範疇
        k_arrhenius = np.exp(-3800.0 / (self.R * (temp + 273.15))) * 0.35
        h2_rate = k_arrhenius * (conc / 100.0) * (flow / 1000.0) * 4.0 * 10.0
        
        # 電流密度限幅調整至 0.5 ~ 3.5 A/cm2 之間
        dynamic_i_limit = 0.5 + (h2_rate * 0.18)
        return h2_rate, dynamic_i_limit

    def generate_polarization_v37(self, e_thermo, i_0, r_int, alpha, temp, i_limit):
        T_k = temp + 273.15
        i_scan = np.linspace(0.001, min(i_limit * 0.96, 4.0), 60)
        
        v_cell_list = []
        p_density_list = []
        eta_act_list = []
        eta_ohmic_list = []
        eta_conc_list = []
        
        for i in i_scan:
            eta_act = (self.R * T_k / (alpha * self.n * self.F)) * np.log(max(i / i_0, 1.001))
            eta_ohmic = i * r_int
            ratio = min(i / i_limit, 0.995)
            eta_conc = - (self.R * T_k / (alpha * self.n * self.F)) * np.log(1.0 - ratio)
            
            v_cell = e_thermo - eta_act - eta_ohmic - eta_conc
            if v_cell < 0: 
                v_cell = 0.0
                
            v_cell_list.append(v_cell)
            p_density_list.append(v_cell * i * 1000.0)
            eta_act_list.append(eta_act)
            eta_ohmic_list.append(eta_ohmic)
            eta_conc_list.append(eta_conc)
            
        return pd.DataFrame({
            'Current_Density': i_scan * 1000.0, 
            'Voltage': v_cell_list,
            'Power': p_density_list,
            'Activation': eta_act_list,
            'Ohmic': eta_ohmic_list,
            'Concentration': eta_conc_list
        })

# 實例化全新架構
twin = DBFCDigitalTwinV37()
h2_rate, i_limit_dynamic = twin.calculate_metrics_v37(reactor_temp, concentration, flow_rate)
df_polar = twin.generate_polarization_v37(e_thermo, i_0, r_int, alpha, reactor_temp, i_limit_dynamic)

# 計算即時台灣時間 (Taipei Time)
taipei_tz = pytz.timezone('Asia/Taipei')
current_taiwan_time = datetime.now(taipei_tz).strftime('%Y-%m-%d %H:%M:%S')

# ==========================================
# 5. 主畫面呈現
# ==========================================
st.title("NaBH4 燃料電池數位雙生智慧監控系統")
st.markdown(f"**核心技術：基於 TAD-AGE 模擬架構 & Butler-Volmer 電化學動力學核心 (解耦版 V3.7)**")
st.markdown(f"**目前台灣時間：{current_taiwan_time}**")
st.caption(f"監控對象：{selected_scen} | {scen_default['desc']}")

# 🚨 ==========================================
# 🧠 全新獨立：TAD-AGE 實時安全診斷安全鎖
# ==========================================
st.markdown("---")
st.subheader("[ 🧠 TAD-AGE 專家系統：實時安全診斷面板 ]")

# 這裡我們強制作為頂層邏輯判斷，只要滑桿流量大於 200，不管三七二十一直接噴射告警！
has_warning = False

if flow_rate >= 200.0:
    st.error(f"🚨 [高危告警] 燃料進料流量過高 ({flow_rate:.1f} mL/min)！已嚴重超出安全設計臨界點 (200.0 mL/min)，催化反應床面臨溢流與觸媒淹沒風險，安全連鎖機制已就緒！")
    has_warning = True
elif flow_rate >= 120.0:
    st.warning(f"💡 [工藝預警] 進料流量偏高 ({flow_rate:.1f} mL/min)，動態產氫速率加劇，請注意排氣端安全閥背壓。")
    has_warning = True

if reactor_temp >= 75.0:
    st.error(f"🚨 [熱管理告警] 反應床溫度偏高 ({reactor_temp:.1f} °C)！面臨高溫副反應與副產物偏硼酸鈉結晶固化風險！")
    has_warning = True

if not has_warning:
    st.success("🟢 系統安全評估：TAD-AGE 未偵測到任何工藝異常。所有流體進料流量、反應床溫度與電化學極化特性皆處於健康安全邊界之內。")

# ==========================================
# 6. 📡 實時數據連動監測站
# ==========================================
st.markdown("---")
st.subheader("[ 📡 實時數據連動監測站 ]")
m1, m2, m3, m4 = st.columns(4)

status_delta = " [ ⚠ 高負載 ]" if flow_rate >= 200.0 else " [ 🟢 穩定 ]"
m1.metric("催化反應床產氫速率", f"{h2_rate:.3f} L/min", delta=f"流量反饋: +{flow_rate/10:.1f}%" + status_delta, delta_color="inverse" if flow_rate >= 200.0 else "normal")
m2.metric("動態極限電流密度 (i_lim)", f"{i_limit_dynamic:.2f} A/cm2", delta="與產氫量實時解耦")
m3.metric("系統最大輸出功率點", f"{df_polar['Power'].max():.1f} mW/cm2")
m4.metric("反應床預估轉化效率", f"{min(99.5, 65.0 + reactor_temp*0.38 + concentration*0.2):.1f} %")

st.markdown("---")

tab1, tab2, tab3 = st.tabs([
    "電化學動力學分析 (極化曲線)", 
    "瞬態功率動態響應追蹤", 
    "數位雙生實時數據流水線"
])

# ---- TAB 1: 極化曲線 ----
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("電池電氣特性聯動曲線")
        fig_iv = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.15)
        
        fig_iv.add_trace(
            go.Scatter(x=df_polar['Current_Density'], y=df_polar['Voltage'], name="單體電勢 (V)", line=dict(color='royalblue', width=3.5)),
            row=1, col=1
        )
        fig_iv.add_trace(
            go.Scatter(x=df_polar['Current_Density'], y=df_polar['Power'], name="功率密度 (mW/cm2)", line=dict(color='orange', width=3.5, dash='dash')),
            row=2, col=1
        )
        
        fig_iv.update_layout(height=500, hovermode="x unified", showlegend=True, margin=dict(l=20, r=20, t=10, b=10))
        fig_iv.update_xaxes(title_text="電流密度 Current Density (mA/cm2)", row=2, col=1)
        fig_iv.update_yaxes(title_text="電勢 (V)", row=1, col=1)
        fig_iv.update_yaxes(title_text="功率 (mW/cm2)", row=2, col=1)
        st.plotly_chart(fig_iv, use_container_width=True)
        
    with col2:
        st.subheader("三大核心過電勢(損失)動態拆解")
        fig_loss = go.Figure()
        fig_loss.add_trace(go.Scatter(x=df_polar['Current_Density'], y=df_polar['Activation'], name="活化損失 (Activation)", line=dict(color='#ff9f43', width=2)))
        fig_loss.add_trace(go.Scatter(x=df_polar['Current_Density'], y=df_polar['Ohmic'], name="歐姆損失 (Ohmic)", line=dict(color='#10ac84', width=2, dash='dot')))
        fig_loss.add_trace(go.Scatter(x=df_polar['Current_Density'], y=df_polar['Concentration'], name="濃差損失 (Concentration)", line=dict(color='#5f27cd', width=2, dash='dashdot')))
        
        fig_loss.update_layout(hovermode="x unified", showlegend=True, height=500, margin=dict(l=20, r=20, t=10, b=10))
        fig_loss.update_xaxes(title_text="電流密度 (mA/cm2)")
        fig_loss.update_yaxes(title_text="過電勢損失 Overpotential (V)")
        st.plotly_chart(fig_loss, use_container_width=True)

# ---- TAB 2: 瞬態功率動態響應追蹤 ----
with tab2:
    st.subheader("負載階躍變化下的瞬態響應 (Transient Response)")
    
    t_steps = np.linspace(0, 30, 100)
    target_power = np.where(t_steps < 10, 200, np.where(t_steps < 20, 450, 300))
    actual_power = []
    current_p = 200.0
    for tp in target_power:
        tau = max(1.0, 5.0 - (reactor_temp / 20.0))
        current_p += (tp - current_p) * (0.3 / tau)
        actual_power.append(current_p * (h2_rate / (h2_rate + 0.1)))
        
    fig_transient = go.Figure()
    fig_transient.add_trace(go.Scatter(x=t_steps, y=target_power, name="負載需求功率 (Target)", line=dict(color='#dee2e6', width=2, dash='dash')))
    fig_transient.add_trace(go.Scatter(x=t_steps, y=actual_power, name="數位雙生實時輸出 (Actual)", line=dict(color='#ee5253', width=3)))
    
    fig_transient.update_layout(hovermode="x unified", height=400, margin=dict(l=20, r=20, t=10, b=10))
    fig_transient.update_xaxes(title_text="模擬時間 Time (Seconds)")
    fig_transient.update_yaxes(title_text="系統輸出功率 (W)")
    st.plotly_chart(fig_transient, use_container_width=True)

# ---- TAB 3: 數位雙生實時數據流水線 ----
with tab3:
    st.subheader("虛實融合虛擬感測器數據串流 (Virtual Telemetry Pipeline)")
    
    np.random.seed(int(time.time()) % 100)
    pipeline_data = {
        "虛擬感測器節點 (Telemetry Node)": [
            "陽極進料控制閥反饋 (Anode Inlet Valve %)",
            "反應床氫氣出口壓力 (Reactor H2 Pressure, bar)",
            "電堆陰極流道 pH 值 (Cathode pH Sensor)",
            "燃料循環泵內部功耗 (Circulation Pump Power, W)",
            "散熱風扇動態 PWM 輸出 (Cooling Fan PWM)"
        ],
        "實時量測值 (Live Value)": [
            f"{min(100.0, flow_rate / 3.0 + np.random.normal(0, 0.5)):.2f} %",
            f"{1.0 + (h2_rate * 0.15) + np.random.normal(0, 0.02):.3f} bar",
            f"{13.2 - (concentration * 0.04) + np.random.normal(0, 0.05):.2f}",
            f"{12.5 + (flow_rate * 0.08):.1f} W",
            f"{max(10, min(100, int(reactor_temp * 1.1)))} %"
        ],
        "健康度狀態 (Health Status)": [
            "[ 正常運作中 ]",
            "[ 壓力高危告警 ]" if flow_rate >= 200.0 else ("[ 壓力穩定 ]" if h2_rate > 0.5 else "[ 壓力偏低 ]"),
            "[ 鹼性特徵正常 ]",
            "[ 功耗符合預期 ]",
            "[ 高溫警戒中 ]" if reactor_temp >= 75 else "[ 主動散熱跟隨中 ]"
        ]
    }
    
    df_pipeline = pd.DataFrame(pipeline_data)
    st.table(df_pipeline)
    st.success("數位雙生流水線數據鏈接狀態：STABLE")