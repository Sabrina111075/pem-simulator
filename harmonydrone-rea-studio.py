import time
import random
import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from gtts import gTTS

# 頁面基本設定
st.set_page_config(
    page_title="HarmonyDrone REA Studio",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 標題與簡介
st.title("🚁 HarmonyDrone REA Studio")
st.markdown("### 鴻蒙無人機系統 × AI 逆向工程工具（REA）分散式數位孿生實驗室")
st.markdown("---")

# 側邊欄控制台
st.sidebar.header("🛠️ 實驗控制與設定")
drone_mode = st.sidebar.selectbox(
    "選擇無人機運行模式",
    ["鴻蒙分散式協同飛行", "REA 自動化逆向分析", "資安漏洞自動掃描"]
)

sim_speed = st.sidebar.slider("模擬運算速度 (Hz)", 1, 10, 5)
ai_model_choice = st.sidebar.selectbox(
    "後端 AI 分析引擎",
    ["Gemini 3.5 Flash-Lite", "Gemini 3.6 Flash", "DeepSeek-V3"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 提示：本系統將鴻蒙分散式軟匯流排概念與 REA AI 逆向代理技術結合，適合初學者進行視覺化探索。")

# 主畫面多頁籤
tab1, tab2, tab3 = st.tabs(["🌐 分散式飛行與終端聯動", "🔍 REA 逆向與代碼分析", "💬 AI 導師與互動問答"])

with tab1:
    st.subheader("📡 鴻蒙超級終端：跨裝置無人機即時狀態")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="控制終端 (Controller)", value="HarmonyOS Phone", delta="連線正常")
    with col2:
        st.metric(label="監控終端 (Monitor)", value="HarmonyOS Smart Screen", delta="畫面流轉中")
    with col3:
        st.metric(label="運算核心 (Edge Compute)", value="HarmonyOS NEXT Kernel", delta="穩定 (5ms)")

    st.markdown("#### 📍 無人機 3D 動態飛行軌跡模擬")
    
    # 產生具備時間序列 (Frame) 的 3D 動態軌跡數據
    frames_count = 40
    t_vals = np.linspace(0, 10, frames_count)
    
    records = []
    for frame_idx, t in enumerate(t_vals):
        # 繪製歷史累積軌跡
        t_sub = t_vals[:frame_idx+1]
        x_sub = np.sin(t_sub) * 10
        y_sub = np.cos(t_sub) * 10
        z_sub = np.linspace(1, 20, len(t_sub))
        
        for i in range(len(t_sub)):
            records.append({
                "Frame": frame_idx,
                "Time": round(t_sub[i], 2),
                "X": x_sub[i],
                "Y": y_sub[i],
                "Z": z_sub[i]
            })
            
    df_anim = pd.DataFrame(records)
    
    # 建立具有動態 Play 按鈕的 Plotly 3D 動畫圖表
    fig_anim = px.scatter_3d(
        df_anim,
        x="X", y="Y", z="Z",
        animation_frame="Frame",
        color="Z",
        range_x=[-12, 12], range_y=[-12, 12], range_z=[0, 25],
        title="HarmonyDrone 3D Dynamic Flight Trajectory (Play/Pause Support)"
    )
    
    # 調整動畫流暢度
    fig_anim.update_layout(
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="高度 Z (m)"
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )
    
    st.plotly_chart(fig_anim, use_container_width=True)

with tab2:
    st.subheader("🔍 REA (Reverse Engineering Agent) 逆向分析控制台")
    st.markdown("自動解構鴻蒙原生套件（`.hap`）與方舟位元組碼（Ark Bytecode）之安全審查結果。")
    
    target_module = st.selectbox(
        "選擇要分析的模組代碼",
        ["drone_flight_control.hap (飛行控制)", "distributed_camera.hap (分散式鏡頭)", "mavlink_bridge.hap (通訊協定)"]
    )
    
    if st.button("🚀 啟動 REA 自動逆向分析"):
        with st.spinner(f"正在調用 {ai_model_choice} 與 REA 代理分析 {target_module}..."):
            time.sleep(1.5)
        
        st.success("✅ 分析完成！以下為 REA 產出的安全與架構報告：")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("##### 📌 代碼結構摘要")
            st.code("""
// ArkTS / NAPI 接口分析
public class DroneController {
    @DistributedBus
    public void syncFlightState() {
        // 透過鴻蒙分散式軟匯流排同步姿態
    }
}
            """, language="typescript")
        
        with col_b:
            st.markdown("##### 🛡️ 資安與權限風險評級")
            st.metric(label="安全評分 (Security Score)", value="92 / 100", delta="低風險")
            st.write("- **敏感 API 調用**：`ohos.permission.CAMERA` (已授權)")
            st.write("- **跨裝置通訊加密**：AES-256 (符合標準)")
            st.write("- **未授權端點漏洞**：無檢出")

with tab3:
    st.subheader("🎓 鴻蒙與 REA 互動小學堂")
    st.markdown("在這裡您可以隨時詢問關於鴻蒙系統或 AI 逆向工程的問題，系統將為您生成文字解答並同步進行**語音朗讀**。")
    
    user_query = st.text_input("請輸入您的問題（例如：「什麼是分散式軟匯流排？」或「REA 是怎麼運作的？」）")
    if user_query:
        answer_text = (
            f"這是一個非常好的問題！在鴻蒙系統中，分散式軟匯流排就像是一條無形的連接線，讓不同硬體（如手機與無人機）能夠像使用同一個硬體般流暢溝通。"
            f"而 REA（Reverse Engineering Agent）則像是一個聰明的 AI 偵探，能自動幫我們把這些分散式程式碼與 .hap 套件拆解並讀懂，確保系統安全無虞。"
        )
        
        st.info(f"💡 【AI 講師回答】針對您的問題「{user_query}」：")
        st.write(answer_text)
        
        # 產生語音 TTS 音訊
        try:
            with st.spinner("🔊 正在合成 AI 講師語音..."):
                tts = gTTS(text=answer_text, lang='zh-tw')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                st.audio(fp, format='audio/mp3', start_time=0)
        except Exception as e:
            st.warning("⚠️ 語音合成失敗，請檢查網路連線。")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>HarmonyDrone REA Studio v1.1 | Built with Streamlit & Gemini API</p>", unsafe_allow_html=True)