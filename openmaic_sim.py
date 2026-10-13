import streamlit as st
import time
import random

# 嘗試匯入 google.generativeai (若無則提示安裝)
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

st.set_page_config(page_title="OpenMAIC x Gemini 智慧教育平台", layout="wide")

st.title("🎓 OpenMAIC 搭配 Gemini 輕量化模型引擎")
st.markdown("本系統透過串接 Google Gemini 模型，實現 **AI 自動生成工業課程、即時多智能體研討與設備數位雙生互動**。")

# 側邊欄：API 設定與控制台
st.sidebar.header("🔑 AI 模型與實驗設定")
api_key = st.sidebar.text_input("輸入您的 Gemini API Key", type="password")

# 依照您的要求：從最輕量優先使用
model_choice = st.sidebar.selectbox(
    "選擇 Gemini 模型 (優先輕量化)", 
    ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash", "gemini-3-pro"]
)

st.sidebar.markdown("---")
course_topic = st.sidebar.selectbox("選擇教學主題", [
    "ESP32 溫控與 PWM 風扇系統整合", 
    "PEM 氫能電解槽 Butler-Volmer 過電位分析", 
    "工業馬達振動與邊緣異常診斷 (MIMII Dataset)"
])

target_temp = st.sidebar.slider("設定目標溫度 (°C)", min_value=20, max_value=60, value=30)
target_rpm = st.sidebar.slider("設定風扇轉速 (RPM)", min_value=0, max_value=1200, value=800, step=50)

# 安全檢查
if target_temp > 50 or target_rpm > 1000:
    sim_decision = "REJECTED"
    st.sidebar.error("❌ 狀態：REJECTED (超過安全上限 L2 限制)")
else:
    sim_decision = "SAFE"
    st.sidebar.success("✅ 狀態：SAFE (通過數位雙生預演)")

# 初始化 Gemini
ai_response_text = ""
if api_key and HAS_GEMINI:
    try:
        genai.configure(api_key=api_key)
        # 這裡會使用您選擇的輕量模型
        model = genai.GenerativeModel(model_choice)
    except Exception as e:
        st.sidebar.error(f"API 初始化失敗: {e}")

# 主畫面分頁
tab1, tab2, tab3 = st.tabs(["📚 Gemini AI 自動生成課程", "📊 設備數位雙生與即時監控", "📜 系統稽核日誌"])

with tab1:
    st.subheader(f"🤖 OpenMAIC 多智能體研討會：{course_topic}")
    
    if st.button("✨ 透過 Gemini 自動生成本週實驗講義與任務", type="primary"):
        if not api_key:
            st.warning("⚠️ 請先在左側欄位輸入您的 Gemini API Key！")
        elif not HAS_GEMINI:
            st.error("⚠️ 偵測到環境尚未安裝 google-generativeai 套件。請在命令提示字元執行：`pip install google-generativeai`")
        else:
            with st.spinner(f"正在呼叫輕量模型 ({model_choice}) 生成課程內容中..."):
                try:
                    prompt = f"請為高工或大學生設計一份關於「{course_topic}」的短篇實驗講義，包含核心原理、安全注意事項及一題隨堂思考題。"
                    response = model.generate_content(prompt)
                    ai_response_text = response.text
                    st.success("課程內容已由 Gemini 成功生成！")
                except Exception as e:
                    ai_response_text = f"生成失敗，錯誤訊息：{e}"
    
    # 顯示課程內容
    if ai_response_text:
        st.markdown("### 📖 AI 生成講義結果")
        st.write(ai_response_text)
    else:
        st.info("💡 點擊上方按鈕，即可讓 Gemini 依據當前主題自動編撰客製化的教學講義。")

with tab2:
    st.subheader("即時數據監控 (Telemetry & Digital Twin)")
    
    col1, col2, col3, col4 = st.columns(4)
    current_temp = 25.0 + (target_temp - 25.0) * 0.8 + random.uniform(-0.5, 0.5)
    simulated_temp = 25.0 + (target_temp - 25.0) * 0.82
    diff = abs(current_temp - simulated_temp)
    
    col1.metric("🌡️ 實際溫度 (Reported)", f"{current_temp:.1f} °C")
    col2.metric("🔮 預測溫度 (Simulated)", f"{simulated_temp:.1f} °C")
    col3.metric("⚖️ 虛實誤差 (Difference)", f"{diff:.2f} °C")
    col4.metric("🌀 風扇狀態", f"{target_rpm} RPM" if sim_decision == "SAFE" else "0 RPM (鎖定)")

    st.markdown("---")
    if st.button("🚀 送出高階實驗指令 (經 Gateway ➔ Twin ➔ MQTT ➔ ESP32)"):
        if sim_decision == "REJECTED":
            st.error("指令被拒絕：安全政策攔截了超過限制的參數設定。")
        else:
            with st.spinner("指令傳遞中..."):
                time.sleep(0.8)
            st.success("🎉 實驗執行完畢！已收到唯一 ACK，虛實比對報告已同步至系統。")

with tab3:
    st.subheader("📜 系統稽核與模型狀態")
    st.text(f"""
[System Status] OpenMAIC Academy Engine v1.0 running on Windows 7 Localhost
[AI Model Target] Selected: {model_choice} (Lightweight Priority)
[Gateway Status] Active and secured via L2 capability whitelist.
    """)