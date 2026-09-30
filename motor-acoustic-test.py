import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# 1. 頁面基本配置
st.set_page_config(
    page_title="馬達與工業設備聲學診斷測試平台",
    page_icon="⚙️",
    layout="wide"
)

# =========================================================
# 📌 [關鍵修正] 必須先定義 page 變數，下方 if 才不會噴 NameError
# =========================================================
page = st.sidebar.selectbox(
    "📌 切換功能模組：",
    ["⚙️ 設備與測試控制台", "🎓 OpenMAIC 聲學 AI 學院"]
)

use_mock = st.sidebar.checkbox("🛠️ 開啟 Mock 開發模式 (免 API 額度)", value=True)

if page == "🎓 OpenMAIC 聲學 AI 學院":
    import streamlit.components.v1 as components

    st.title("🎓 OpenMAIC 聲學 AI 學院 × 虛擬聲學診斷實驗室")
    st.caption("OpenMAIC Multi-Agent AI Interactive Classroom & Acoustic Diagnostic Lab")
    st.info("💡 本頁面採用單欄動態視圖：上方為 AI 導師講授區，下方為聲學診斷實作實驗室。")

# --------------------------------------------------
    # 區塊 1：OpenMAIC 聲學 AI 學院 (課程總結 + 穩定語音 + 動態互動)
    # --------------------------------------------------
    import json

    st.subheader("🎓 OpenMAIC 多智體互動 AI 學院")
    st.caption("OpenMAIC Multi-Agent AI Interactive Classroom & Course Hub")

    # 1. 建立結構化課程庫 (Domain Knowledge Base)
    course_database = {
        "lesson_1": {
            "title": "課程 1：梅爾頻譜圖 (Mel-Spectrogram) 基礎原理",
            "summary": [
                "**核心概念**：將時域聲學訊號轉為 2D 頻譜圖，並將 Y 軸頻率轉為符合人類聽覺特性的 Mel Scale。",
                "**關鍵優勢**：人耳對 1000Hz 以下的低頻極度敏感，梅爾標度能放大低頻特徵、壓制無效高頻雜訊。",
                "**工業應用**：適用於馬達運轉聲、泵浦氣蝕與軸承微弱撞擊音的早期特徵擷取。"
            ],
            "dialogue": [
                {"role": "professor", "avatar": "👨‍🏫", "name": "Prof. Acoustic (聲學總導師)", "content": "同學們好！歡迎來到課程 1。傳統 FFT 頻譜是線性頻率，但為什麼在工業 AI 診斷中，我們偏好使用梅爾標度（Mel Scale）？"},
                {"role": "student_a", "avatar": "🙋‍♂️", "name": "Student Alex (初學者)", "content": "教授，是因為人耳對低頻變化比較敏感，而梅爾標度正好看得比較清楚嗎？"},
                {"role": "professor", "avatar": "👨‍🏫", "name": "Prof. Acoustic (聲學總導師)", "content": "完全正確！梅爾標度做對數轉換後，能精準放大 1kHz 以下的關鍵頻段，這正是馬達轉速與軸承損傷特徵最密集的區域。"},
                {"role": "student_b", "avatar": "🙋‍♀️", "name": "Student Beth (AI 工程師)", "content": "補充一下！在將資料送入 CNN / DCASE 模型時，梅爾頻譜圖也能有效降低資料維度，大幅提升運算效率。"}
            ],
            "quiz": {
                "q": "問：為什麼梅爾頻譜圖比傳統線性 FFT 更適合用於馬達聲學 AI 診斷？",
                "options": ["A. 能放大人耳敏感的低頻特徵與轉速諧波", "B. 只能處理高頻聲音", "C. 檔案體積比較大"],
                "ans": "A. 能放大人耳敏感的低頻特徵與轉速諧波"
            }
        },
        "lesson_2": {
            "title": "課程 2：馬達與軸承異音特徵與 MIMII 數據集判讀",
            "summary": [
                "**軸承磨損 (Bearing Wear)**：在 4kHz~8kHz 高頻區段出現週期性衝擊脈衝 (Impact Pulses)。",
                "**馬達不平衡 (Unbalance)**：在旋轉基頻 (1X RPM) 及倍頻處出現異常高能量峰值。",
                "**氣蝕現象 (Cavitation)**：泵浦與液體設備常見的高頻連續寬頻連續噪音。"
            ],
            "dialogue": [
                {"role": "professor", "avatar": "👨‍🏫", "name": "Prof. Acoustic (聲學總導師)", "content": "在課程 2 中，我們探討 MIMII 工業數據集。當馬達發生軸承損壞時，頻譜圖會出現什麼特徵？"},
                {"role": "student_b", "avatar": "🙋‍♀️", "name": "Student Beth (AI 工程師)", "content": "報告教授，軸承初期損壞時，會在 4kHz 以上高頻區出現很明顯的頻繁衝擊波形！"},
                {"role": "student_a", "avatar": "🙋‍♂️️", "name": "Student Alex (初學者)", "content": "那如果只是馬達螺絲沒鎖緊呢？"},
                {"role": "professor", "avatar": "👨‍🏫", "name": "Prof. Acoustic (聲學總導師)", "content": "螺絲鬆動或不平衡，特徵會集中在低頻 1X/2X RPM 轉速頻率上，這兩者在頻譜圖上的區域截然不同。"}
            ],
            "quiz": {
                "q": "問：軸承早期損傷的聲學特徵通常出現在哪個頻段？",
                "options": ["A. 低頻轉速區 (10Hz-50Hz)", "B. 中高頻衝擊區 (4kHz-8kHz)", "C. 完全不會有特徵"],
                "ans": "B. 中高頻衝擊區 (4kHz-8kHz)"
            }
        }
    }

    # 選擇當前學習課程
    selected_lesson_key = st.selectbox(
        "📖 請選擇 OpenMAIC 學習課程主題：",
        options=list(course_database.keys()),
        format_func=lambda x: course_database[x]["title"]
    )

    current_lesson = course_database[selected_lesson_key]

    # --- 區塊 A：課程精華總結卡片 ---
    with st.expander("📌 點擊展開/收合：本課精華重點總結 (Course Summary)", expanded=True):
        for point in current_lesson["summary"]:
            st.markdown(f"• {point}")

    # --- 區塊 B：穩定語音導覽卡片 (原生 Web Speech 語音引擎) ---
    st.markdown("#### 🎙️ 本課重點語音導覽")
    
    # 清理朗讀文字（去除 Markdown 符號）
    raw_summary = "。".join([p.replace('*', '') for p in current_lesson['summary']])
    speech_text_js = json.dumps(f"歡迎來到{current_lesson['title']}。重點如下：{raw_summary}", ensure_ascii=False)

    tts_card_html = f"""
    <div style="background: linear-gradient(135deg, #e6f2ff 0%, #ffffff 100%); padding: 16px; border-radius: 10px; border-left: 5px solid #0056b3; box-shadow: 0 2px 4px rgba(0,0,0,0.08); margin-bottom: 20px;">
        <p style="margin: 0 0 10px 0; font-weight: bold; color: #0056b3; font-size: 15px;">🔊 點擊按鈕，由 AI 語音導師朗讀本課重點：</p>
        <div style="display: flex; gap: 10px;">
            <button onclick="playVoice()" style="background-color: #0056b3; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px;">
                ▶️ 播放本課重點語音
            </button>
            <button onclick="stopVoice()" style="background-color: #dc3545; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px;">
                ⏹️ 停止播放
            </button>
        </div>
    </div>

    <script>
    var speakText = {speech_text_js};
    
    function playVoice() {{
        window.speechSynthesis.cancel(); // 先清空先前佇列
        
        // 拆成短句子播放，避免長句遭中斷
        var sentences = speakText.split("。");
        sentences.forEach(function(seq) {{
            if (seq.trim().length > 0) {{
                var msg = new SpeechSynthesisUtterance(seq);
                msg.lang = 'zh-TW';
                msg.rate = 1.0;
                window.speechSynthesis.speak(msg);
            }}
        }});
    }}

    function stopVoice() {{
        window.speechSynthesis.cancel();
    }}
    </script>
    """
    st.components.v1.html(tts_card_html, height=120)

    # --- 區塊 C：OpenMAIC 多智體對話實況 ---
    st.markdown("#### 🎭 OpenMAIC 智體課堂對話實況")
    for msg in current_lesson["dialogue"]:
        with st.chat_message(msg["role"], avatar=msg["avatar"]):
            st.markdown(f"**{msg['name']}**")
            st.markdown(msg["content"])

    # --- 區塊 D：隨堂互動問答測驗 ---
    st.markdown("---")
    st.markdown("#### 🧪 隨堂觀念互動測驗")
    quiz = current_lesson["quiz"]
    user_ans = st.radio(quiz["q"], quiz["options"], key=selected_lesson_key)
    if st.button("提交答案", key=f"btn_{selected_lesson_key}"):
        if user_ans == quiz["ans"]:
            st.success("🎉 回答正確！代表您已掌握本課的核心觀念。")
        else:
            st.error(f"❌ 答錯囉！正確答案是：{quiz['ans']}")

# --------------------------------------------------
    # 區塊 E：OpenMAIC 多智體研討會學院 (進階 4 角色與男女語音互動)
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("#### 🎓 OpenMAIC 多智體互動研討會")

    import google.generativeai as genai
    from gtts import gTTS
    import io
    import json

    gemini_key = st.secrets.get("GEMINI_API_KEY", "")

    # 1. 擴充學習課程主題
    course_option = st.selectbox(
        "📚 請選擇您想研討的課程主題：",
        [
            "馬達與風扇聲學故障診斷 (Acoustic Fault Diagnosis)",
            "Edge AI 邊緣運算與輕量化模型部署 (Edge Deployment)",
            "聲學訊號處理與 FFT/STFT 頻譜分析 (Signal Processing)",
            "MEMS 感測器雜訊濾波與 Kalman Filter 應用 (Sensor Fusion)",
            "工業物聯網 (IIoT) 設備預測性維護 SOP (Predictive Maintenance)"
        ]
    )

    user_q = st.text_input(
        f"輸入您關於【{course_option.split(' (')[0]}】的研討疑問：",
        key="qa_input_box"
    )

    if user_q:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(f"**學員 (You)**：{user_q}")

    if not gemini_key and not use_mock:
        st.warning("⚠️ 未檢測到 API Key，請確保已在 Streamlit Secrets 中設定 `GEMINI_API_KEY`。")
    else:
        try:
            # 提示詞：要求4位具備不同立場的 Agent 進行多人研討
            prompt = f"""
你現在是 OpenMAIC 多智體互動研討會系統，當前主題為：「{course_option}」。
請針對學員提問：「{user_q}」，分別以 4 個不同角色的立場進行多人圓桌討論（每人發言約 60-90 字，彼此回應、補足或對照）：

1. Prof. Acoustic（男聲，聲學總導師）：著重於理論分析、物理原理與數學公式背後的意義。
2. Engineer Beth（女聲，AI 邊緣部署工程師）：著重於模型量化 (INT8/FP16)、C++ / TensorRT 實務與硬體資源限制。
3. Data Scientist Alex（男聲，數據科學專家）：著重於資料集處理 (MIMII/DCASE)、Mel 頻譜特徵提取與特徵工程。
4. Product Manager Cathy（女聲，工業產品經理）：著重於商業 ROI、預測性維護 SOP、現場落地可行性與客戶痛點。

請嚴格輸出 JSON 格式如下：
{{
  "prof_reply": "Prof. Acoustic 的回應",
  "beth_reply": "Engineer Beth 的回應",
  "alex_reply": "Data Scientist Alex 的回應",
  "cathy_reply": "Product Manager Cathy 的回應"
}}
"""

            # 💡 判斷：若開啟 Mock 模式則直接回傳假 JSON，不呼叫 API
            if use_mock:
                import time
                time.sleep(0.3) # 模擬 0.3 秒網路延遲
                res_text = """{
  "prof_reply": "【Mock 測試】Prof. Acoustic：從物理與頻譜角度來看，馬達與風扇故障會反映在 FFT 特徵峰值與諧波分量。",
  "beth_reply": "【Mock 測試】Engineer Beth：部署至 ESP32 或 Raspberry Pi 時需考慮模型量化 INT8 降低記憶體佔用。",
  "alex_reply": "【Mock 測試】Data Scientist Alex：建議提取 Mel 頻譜特徵後，結合 Autoencoder 進行無監督異常分數計算。",
  "cathy_reply": "【Mock 測試】Product Manager Cathy：此預測性維護方案能有效替工廠預防非預期停機，節省維護成本。"
}"""
            else:
                # 💡 關閉 Mock 模式時，才真正呼叫 Gemini API
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-3.8-flash')
                response = model.generate_content(prompt)
                res_text = response.text

                # 定義 4 位角色的頭像、名稱與語音設定 (透過不同語言代碼/地區區分男女聲感)
                agents_config = [
                    {
                        "key": "prof_reply",
                        "title": "[Prof. Acoustic] 聲學總導師 (理論與原理)",
                        "avatar": "👨‍🏫",
                        "lang": "zh-tw",     # 標準男聲偏向
                        "slow": False
                    },
                    {
                        "key": "beth_reply",
                        "title": "[Engineer Beth] AI 邊緣部署工程師 (硬體實務)",
                        "avatar": "👩‍💻",
                        "lang": "zh-CN",     # 切換不同發音庫以示區隔 (女聲感)
                        "slow": False
                    },
                    {
                        "key": "alex_reply",
                        "title": "[Data Scientist Alex] 數據科學專家 (訊號與特徵)",
                        "avatar": "👨‍🔬",
                        "lang": "zh-tw",     # 稍慢速度以塑造穩重男聲
                        "slow": True
                    },
                    {
                        "key": "cathy_reply",
                        "title": "[Product Manager Cathy] 工業產品經理 (場域落地與 ROI)",
                        "avatar": "👩‍💼",
                        "lang": "zh-CN",     # 節奏較快的女聲
                        "slow": False
                    }
                ]

                # 依次渲染 4 位智體的發言與專屬語音播放器
                for agent in agents_config:
                    reply_text = res_data.get(agent["key"], "")
                    if reply_text:
                        with st.chat_message(agent["key"], avatar=agent["avatar"]):
                            st.markdown(f"**{agent['title']}**：{reply_text}")
                            
                            # 生成專屬語音
                            tts = gTTS(text=reply_text, lang=agent["lang"], slow=agent["slow"])
                            fp = io.BytesIO()
                            tts.write_to_fp(fp)
                            st.audio(fp.getvalue(), format="audio/mp3")

            except Exception as e:
                st.error(f"❌ Gemini API 呼叫失敗：{str(e)}")

    st.markdown("---")

# 2. 標題與簡介
st.title("⚙️ 馬達與工業設備聲學診斷測試平台 (EdgeAcoustic AI)")
st.caption("邊緣運算前置驗證平台 | 支援 ESP32-S3 + Raspberry Pi 5 模擬測試")

# 數據來源標註
st.info(
    "📊 **聲學基準數據來源 (Benchmark Dataset)**：\n"
    "本平台測試音訊基準參照 **DCASE Challenge Task 2 / MIMII Dataset** (Fan, Motor, Pump, Valve, Slide Rail, Gearbox) 之設備聲學特徵與頻域指標進行標定與驗證。"
)

st.markdown("---")

# 3. 側邊欄控制台 - 擴充至 6 大工業設備類型
st.sidebar.header("⚙️ 設備與測試控制台")

category = st.sidebar.selectbox(
    "1. 選擇設備類別 (Category)",
    [
        "工業風扇 (Fan)",
        "工業馬達 (Motor)",
        "工業水泵 (Pump)",
        "電磁閥門 (Valve)",
        "線性滑軌 (Slide Rail)",
        "工業齒輪箱 (Gearbox)",
        "風力發電機 - 齒輪箱 (Wind Turbine - Gearbox)",
        "風力發電機 - 發電機 (Wind Turbine - Generator)",
        "風力發電機 - 實測風場聲 (Wind Turbine Field Acoustics)",
        "電動車電池水冷泵浦 (EV Battery Cooling Pump)" 
    ]
)

if category == "工業風扇 (Fan)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "輕微不平衡/積塵 (Warning)", "葉片嚴重破損/異物 (Blade Fault)"]
    )
    if "正常" in status_option:
        audio_file = "samples/fan/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/fan/warning_01.wav" if os.path.exists("samples/fan/warning_01.wav") else "samples/fan/anomaly_blade_01.wav"
    else:
        audio_file = "samples/fan/anomaly_blade_01.wav"

elif category == "工業馬達 (Motor)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "輕微轉子偏心 (Warning)", "嚴重軸承磨損 (Bearing Fault)"]
    )
    if "正常" in status_option:
        audio_file = "samples/motor/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/motor/warning_01.wav" if os.path.exists("samples/motor/warning_01.wav") else "samples/motor/anomaly_bearing_01.wav"
    else:
        audio_file = "samples/motor/anomaly_bearing_01.wav"

elif category == "工業水泵 (Pump)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "流體輕微微氣蝕 (Warning)", "軸封嚴重磨損/空轉 (Pump Cavitation)"]
    )
    if "正常" in status_option:
        audio_file = "samples/pump/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/pump/warning_01.wav"
    else:
        audio_file = "samples/pump/anomaly_cavitation_01.wav"

elif category == "電磁閥門 (Valve)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "閥體輕微結垢/滯遲 (Warning)", "氣體/液體嚴重洩漏 (Valve Leakage)"]
    )
    if "正常" in status_option:
        audio_file = "samples/valve/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/valve/warning_01.wav"
    else:
        audio_file = "samples/valve/anomaly_leak_01.wav"

elif category == "線性滑軌 (Slide Rail)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "潤滑油脂不足 (Warning)", "軌道金屬剝落/刮傷 (Rail Scratch)"]
    )
    if "正常" in status_option:
        audio_file = "samples/slider/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/slider/warning_01.wav"
    else:
        audio_file = "samples/slider/anomaly_scratch_01.wav"

# 1. 工業齒輪箱 (原本的項目，請確認上方有這行 elif)
elif category == "工業齒輪箱 (Gearbox)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "齒面輕微點蝕 (Warning)", "輪齒嚴重點蝕/缺角 (Gear Damage)"]
    )
    if "正常" in status_option:
        audio_file = "samples/gearbox/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/gearbox/warning_01.wav"
    else:
        audio_file = "samples/gearbox/anomaly_gear_01.wav"

elif category == "風力發電機 - 齒輪箱 (Wind Turbine - Gearbox)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "齒輪箱咬合微幅偏心 (Warning)", "齒輪面嚴重磨損/缺失 (Gear Fault)"]
    )
    if "正常" in status_option:
        audio_file = "samples/gearbox/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/gearbox/warning_01.wav" if os.path.exists("samples/gearbox/warning_01.wav") else "samples/gearbox/anomaly_gear_01.wav"
    else:
        audio_file = "samples/gearbox/anomaly_gear_01.wav"

elif category == "風力發電機 - 發電機 (Wind Turbine - Generator)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常 (Normal)", "轉子不平衡/異音 (Warning)", "軸承嚴重損傷 (Bearing Fault)"]
    )
    if "正常" in status_option:
        audio_file = "samples/motor/normal_01.wav"
    elif "Warning" in status_option:
        audio_file = "samples/motor/warning_01.wav" if os.path.exists("samples/motor/warning_01.wav") else "samples/motor/anomaly_bearing_01.wav"
    else:
        audio_file = "samples/motor/anomaly_bearing_01.wav"

elif category == "風力發電機 - 實測風場聲 (Wind Turbine Field Acoustics)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["低風速正常運轉 (Low Wind - Normal)", "高風速氣流切風聲 (High Wind - Swish)", "強風噪下傳動異常 (Fault under Wind Noise)"]
    )
    if "低風速" in status_option:
        audio_file = "samples/wind_field/low_wind_normal.wav" if os.path.exists("samples/wind_field/low_wind_normal.wav") else "samples/fan/normal_01.wav"
    elif "高風速" in status_option:
        audio_file = "samples/wind_field/high_wind_normal.wav" if os.path.exists("samples/wind_field/high_wind_normal.wav") else "samples/fan/warning_01.wav"
    else:
        audio_file = "samples/wind_field/wind_fault.wav" if os.path.exists("samples/wind_field/wind_fault.wav") else "samples/fan/anomaly_blade_01.wav"

elif category == "電動車電池水冷泵浦 (EV Battery Cooling Pump)":
    status_option = st.sidebar.selectbox(
        "2. 選擇測試狀態/故障型態",
        ["正常運轉狀態 (Normal)", "泵浦軸承磨損 (Bearing Fault)", "液體空蝕異常 (Cavitation Fault)", "轉子卡死/堵塞 (Rotor Lock)"]
    )
    if "正常" in status_option:
        audio_file = "samples/cooling_pump/normal_01.wav" if os.path.exists("samples/cooling_pump/normal_01.wav") else "samples/pump/normal_01.wav"
    elif "軸承" in status_option:
        audio_file = "samples/cooling_pump/bearing_fault.wav" if os.path.exists("samples/cooling_pump/bearing_fault.wav") else "samples/pump/anomaly_bearing_01.wav"
    elif "空蝕" in status_option:
        audio_file = "samples/cooling_pump/cavitation_fault.wav" if os.path.exists("samples/cooling_pump/cavitation_fault.wav") else "samples/pump/anomaly_cavitation_01.wav"
    else:
        audio_file = "samples/cooling_pump/rotor_lock.wav" if os.path.exists("samples/cooling_pump/rotor_lock.wav") else "samples/pump/anomaly_rotor_01.wav"

# -------------------------------------------------------------------
# 提示框請加在 elif 區塊結束後的這個位置
# -------------------------------------------------------------------
if "實測風場聲" in category:
    st.warning(
        "⚠️ **戶外環境風噪提示 (Field Acoustics)**：\n"
        "此數據集來自 IEEE DataPort / Zenodo 戶外實測風場，包含不同風速（4m/s ~ 12m/s）下的強烈氣流切風聲 (Swish Noise)。\n"
        "邊緣 AI 模型將自動啟用前置高通/帶通濾波器 (Bandpass Filter)，以進行背景風噪與內部結構異音的解耦分析。"
    )

if "水冷泵浦" in category:
    st.warning(
        "⚠️ **車載與冷卻運轉環境提示 (Cooling System Acoustics)**：\n"
        "此數據集基準參照 MIMII Dataset (Pump)。車載運轉環境下，邊緣 AI 模型將自動啟用前置 500Hz - 8kHz 帶通濾波器 (Bandpass Filter)，"
        "以濾除低頻結構共振與車體馬達嗡鳴聲。"
    )

st.sidebar.markdown("---")
st.sidebar.caption("📋 **驗證標準**：IEEE 1451.4 & DCASE MIMII Benchmark")

# ----------------------------------------------------
# 4. 判斷三級告警狀態 (綠 Normal / 黃 Warning / 紅 Fault)
# ----------------------------------------------------
if "正常" in status_option or "低風速" in status_option:
    alert_level = "GREEN"
    hi_score = 96
    mse_score = 0.0015
    status_text = "正常 (Normal)"
    history_mse = [0.0012, 0.0014, 0.0011, 0.0015, 0.0013, 0.0016, mse_score]

elif "軸承" in status_option or "Warning" in status_option or "高風速" in status_option:
    alert_level = "YELLOW"
    hi_score = 68
    mse_score = 0.0285
    status_text = "警告 (Warning - 初期異常/需關注)"
    history_mse = [0.0015, 0.0030, 0.0080, 0.0150, 0.0210, 0.0250, mse_score]

elif "空蝕" in status_option:
    alert_level = "RED"
    hi_score = 45
    mse_score = 0.0720
    status_text = "嚴重警告 (Warning - 水流空蝕/氣泡爆裂)"
    history_mse = [0.0020, 0.0050, 0.0180, 0.0350, 0.0520, 0.0650, mse_score]

elif "卡死" in status_option or "堵塞" in status_option:
    # 🔴 水泵轉子卡死：特徵為持續性低頻電磁嗡電聲 (Humming Noise)
    alert_level = "RED"
    hi_score = 18
    mse_score = 0.1450
    status_text = "嚴重故障 (Critical Fault - 轉子卡死/低頻嗡鳴)"
    history_mse = [0.0050, 0.0200, 0.0500, 0.0800, 0.1100, 0.1300, mse_score]

else:
    # 🔴 其他強風/傳動嚴重故障
    alert_level = "RED"
    hi_score = 38
    mse_score = 0.0915
    status_text = "嚴重故障 (Fault/Danger - 強風傳動異常)"
    history_mse = [0.0015, 0.0030, 0.0120, 0.0450, 0.0780, 0.0890, mse_score]

# 5. 指標與音訊播放區 (頂部 4 欄併排)
col1, col2, col3, col4 = st.columns([1, 1, 1, 1.3])

with col1:
    st.caption("設備健康指標 (HI)")
    st.markdown(f"<h1 style='margin:0; padding:0; font-size: 2.2rem;'>{hi_score} %</h1>", unsafe_allow_html=True)
    
    if alert_level == "GREEN":
        st.markdown("<span style='color:#15803d; background-color:#dcfce7; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:0.85rem;'>↑ 良好</span>", unsafe_allow_html=True)
    elif alert_level == "YELLOW":
        st.markdown("<span style='color:#b45309; background-color:#fef3c7; border: 1px solid #fde68a; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:0.85rem;'>⚠️ 警告</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span style='color:#b91c1c; background-color:#fee2e2; border: 1px solid #fca5a5; padding:2px 8px; border-radius:4px; font-weight:bold; font-size:0.85rem;'>❌ 故障</span>", unsafe_allow_html=True)

with col2:
    st.metric(label="重構誤差 (MSE)", value=f"{mse_score}", delta="門檻: 0.05", delta_color="off")

with col3:
    st.subheader("診斷狀態")
    if alert_level == "GREEN":
        st.success(f"✔️ {status_text}")
    elif alert_level == "YELLOW":
        st.warning(f"⚠️ {status_text}")
    else:
        st.error(f"🚨 {status_text}")

with col4:
    st.subheader("🔊 音頻試聽")
    if os.path.exists(audio_file):
        st.audio(audio_file, format="audio/wav")
    else:
        st.warning("無音訊檔 (使用模擬數據)")

st.markdown("---")

# ----------------------------------------------------
# 6. 設備日常巡檢維運指引 (全設備動態適配)
# ----------------------------------------------------
st.subheader("📋 設備日常巡檢維運指引 (Routine Maintenance Guide)")

# 🚗 優先判斷：電動車電池水冷泵浦專用指引
if "水冷泵浦" in category or "EV" in category:
    if alert_level == "GREEN":
        st.info(
            f"🟢 **{category} 運轉狀態：優良 (Normal)**\n\n"
            "**1. 聲學診斷結果**：聲學特徵正常，水冷泵浦運轉平順，冷卻液循環效率良好。\n\n"
            "**2. 即時處置 SOP**：無需處理，可安心駕駛或進行快充。\n\n"
            "**3. 預防維護建議**：依原廠規範，定期保養時檢查車載冷卻液位與品質。"
        )
    elif alert_level == "YELLOW":
        st.warning(
            f"🟡 **預警診斷：水冷泵浦初期軸承磨損 (Bearing Fault)**\n\n"
            f"**1. 聲學診斷結果**：偵測到泵浦運轉出現微弱高頻金屬摩擦聲脈衝，冷卻系統暫時維持運作，MSE 誤差進入警戒範圍 ({mse_score})，健康指標 HI 降至 {hi_score}%。\n\n"
            "**2. 即時處置 SOP**：\n"
            "1. 暫時無需立即停車，車輛可繼續行駛，但建議暫時避免高功率快充（超充）。\n"
            "2. 請於近期安排回原廠或維修廠，透過診斷電腦讀取泵浦轉速與電流。\n\n"
            "**3. 預防維護建議**：建議於下次例行保養時預防性更換水泵軸承或總成，防止故障擴大。"
        )
    else:  # RED 故障
        if "空蝕" in status_option:
            fault_title = "水冷管路空蝕 / 氣泡爆裂 (Cavitation Fault)"
            diag_detail = "偵測到管路出現流體空蝕氣泡爆裂聲，可能代表冷卻液不足或管路滲漏，致使散熱效率下降"
            sop_detail = "1. 建議順暢行駛、避免急加速與高速行駛。\n2. 如需充電請優先選擇慢充（AC），並密切注意儀表板電池溫度。"
        else:
            fault_title = "水冷泵浦轉子卡死 / 堵塞 (Rotor Lock)"
            diag_detail = "偵測到強烈低頻電磁嗡鳴聲，泵浦轉子已卡死，電池組已失去主動水冷散熱能力"
            sop_detail = "1. 請尋找安全地點靠邊停車，切換至 P 檔並關閉車輛電源。\n2. 切勿嘗試進行高功率快充，以防電池過熱啟動保護機制或引發熱失控風險。"

        st.error(
            f"🔴 **嚴重警告：{fault_title}**\n\n"
            f"**1. 聲學診斷結果**：{diag_detail}，MSE 重構誤差嚴重超標 ({mse_score})，健康指標 HI 掉至 {hi_score}%。\n\n"
            f"**2. 即時處置 SOP**：\n{sop_detail}\n\n"
            f"**3. 預防維護建議**：請聯繫道路救援或原廠拖吊服務，安排回廠檢測與更換水冷泵浦總成。"
        )

# 🏭 保留：其他工業設備指引 (字典查表)
else:
    if alert_level == "GREEN":
        st.info(
            f"🟢 **{category} 運轉狀態：優良 (Normal)**\n\n"
            "**聲學特徵**：音訊能量分布均勻，並無高頻異常衝擊或頻率偏移。\n"
            "**日常維護建議**：依據標準 SOP 進行月度巡檢，保持設備表面清潔與良好散熱環境。"
        )
    elif alert_level == "YELLOW":
        guide_details = {
            "工業風扇 (Fan)": ("風扇輕微不平衡 / 積塵", "低頻段出現微幅諧波能量抬升", "1. 安排維護日清理扇葉積塵。\n2. 檢查外殼防護網是否產生共振。\n3. 紀錄運轉異音持續觀察。"),
            "工業馬達 (Motor)": ("馬達轉子輕微偏心", "60Hz 轉速基頻能量略微升高", "1. 檢查底座螺絲是否鬆動。\n2. 使用雷射對中儀檢查軸心對中。\n3. 納入每週重點觀察清單。"),
            "工業水泵 (Pump)": ("流體輕微微氣蝕 (Warning)", "中高頻水流噪聲出現不規則脈衝", "1. 檢查入口管路壓力與閥門開度。\n2. 確認是否有流體氣泡混入現象。\n3. 調整進水流量避免持續微氣蝕。"),
            "電磁閥門 (Valve)": ("閥門輕微結垢 / 切換滯遲", "閥門開啟關閉聲學時序偏移", "1. 檢查閥體控制電壓與氣源壓力。\n2. 檢視內部是否有結晶或沉積物。\n3. 規劃於例行保養時清洗閥芯。"),
            "線性滑軌 (Slide Rail)": ("滑塊潤滑油膜不足", "滑塊移動時出現輕微乾燥摩擦高頻聲", "1. 使用油槍補充指定規格潤滑膏。\n2. 手動滑動確認摩擦阻力是否降低。\n3. 清除軌道兩側多餘粉塵。"),
            "工業齒輪箱 (Gearbox)": ("齒面輕微微點蝕", "齒輪齧合頻率 (GMF) 兩側出現微弱旁帶", "1. 抽樣檢測齒輪箱潤滑油品質與鐵粉含量。\n2. 觀察高負載運轉時之溫度變化。\n3. 記錄聲學數據並維持定檢。")
        }
        title_str, diag_str, sop_str = guide_details.get(category, ("設備輕微異常", "特徵值微幅上升", "1. 加強巡檢紀錄。"))
        st.warning(
            f"🟡 **預警診斷：{title_str}**\n\n"
            f"**1. 聲學診斷結果**：{diag_str}，MSE 誤差進入警戒範圍 ({mse_score})，健康指標 HI 降至 {hi_score}%。\n\n"
            f"**2. 即時處置 SOP**：\n{sop_str}\n\n"
            f"**3. 預防維護建議**：安排計畫性停機保養，避免小瑕疵擴大為重大故障。"
        )
    else:
        guide_details_red = {
            "工業風扇 (Fan)": ("風扇葉片嚴重破損 / 異物卡入", "2.8kHz 頻段出現強烈高頻噪聲與週期衝擊", "1. 即刻安排停機並切斷主電源。\n2. 目視檢查葉片是否缺角或有異物。\n3. 更換受損扇葉防止震動損毀軸承。"),
            "工業馬達 (Motor)": ("馬達軸承嚴重磨損 (Bearing Fault)", "3.6kHz~4.2kHz 湧現強烈金屬磨損衝擊波", "1. 發布 Level 1 緊迫告警，12 小時內停機。\n2. 配合加速度計確認軸承損傷點。\n3. 備料並安排更換軸承與校正。"),
            "工業水泵 (Pump)": ("水泵嚴重氣蝕 / 軸封破損", "出現強烈氣蝕空化爆裂聲與振動流壓異常", "1. 立即停止水泵運轉，防止泵體葉輪毀損。\n2. 檢查進水管線是否堵塞或嚴重負壓。\n3. 檢視軸封洩漏狀況並更換新品。"),
            "電磁閥門 (Valve)": ("閥門嚴重洩漏 / 內部結構損壞", "持續性高頻流體噴射聲 (Air Leakage)", "1. 關閉隔離閥並進行系統降壓。\n2. 使用氣體洩漏偵測器確定洩漏點。\n3. 更換閥芯密封圈或整體閥門。"),
            "線性滑軌 (Slide Rail)": ("軌道金屬剝落 / 滑軌刮傷", "滑塊移動時發出劇烈撞擊與金屬刮削聲", "1. 暫停自動化機構運轉。\n2. 檢查軌道表面是否有深層刮痕與鋼珠破裂。\n3. 更換受損滑塊與導軌。"),
            "工業齒輪箱 (Gearbox)": ("齒輪嚴重斷齒 / 斷裂損壞", "齒輪齧合週期產生劇烈衝擊峰值 (Impact Peak)", "1. 切斷馬達驅動電源，停止傳動系統。\n2. 排空齒輪油並檢查底部是否有金屬碎片。\n3. 拆解齒輪箱更換受損齒輪對。")
        }
        title_str, diag_str, sop_str = guide_details_red.get(category, ("設備嚴重故障", "特徵值高度異常", "1. 立即停機檢修。"))
        st.error(
            f"🔴 **嚴重警告：{title_str}**\n\n"
            f"**1. 聲學診斷結果**：{diag_str}，MSE 重構誤差嚴重超標 ({mse_score})，健康指標 HI 掉至 {hi_score}%。\n\n"
            f"**2. 即時處置 SOP**：\n{sop_str}\n\n"
            f"**3. 預防維護建議**：完成檢修與零件更換後，重新進行全頻段聲學基準校正。"
        )

st.markdown("---")

# 7. 專業圖表分頁 (Tabs)
tab1, tab2, tab3 = st.tabs([
    "📊 邊緣聲學梅爾頻譜 (Mel-Spectrogram)",
    "📈 歷史趨勢與統計分析 (Trend & Stats)",
    "⚡ 時域訊號與 FFT 頻譜 (Waveform & FFT)"
])

# Tab 1: 梅爾頻譜圖
with tab1:
    st.markdown("#### 邊緣 AI 聲學特徵分析 (Edge AI Feature)")
    st.caption("📊 **圖表指引**：橫軸 (X-axis) 表示時間 [秒]，縱軸 (Y-axis) 表示梅爾對數頻率 [Hz]，顏色深淺表示能量強度 (dB)。")

    if os.path.exists(audio_file):
        y, sr = librosa.load(audio_file, sr=16000)
    else:
        sr = 16000
        duration = 2.0
        t = np.linspace(0, duration, int(sr * duration))
        if alert_level == "GREEN":
            y = 0.1 * np.sin(2 * np.pi * 60 * t) + 0.02 * np.random.randn(len(t))
        elif alert_level == "YELLOW":
            y = 0.2 * np.sin(2 * np.pi * 60 * t) + 0.1 * np.sin(2 * np.pi * 300 * t) + 0.05 * np.random.randn(len(t))
        else:
            y = 0.3 * np.sin(2 * np.pi * 60 * t) + 0.3 * np.sin(2 * np.pi * 3800 * t) + 0.15 * np.random.randn(len(t))

    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)

    fig, ax = plt.subplots(figsize=(10, 4))
    img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, fmax=8000, ax=ax, cmap='magma')

    ax.set_xlabel("Time (s)", fontsize=10)
    ax.set_ylabel("Frequency (Hz)", fontsize=10)
    cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
    cbar.set_label("Power (dB)", fontsize=9)

    status_en_map = {
        "正常 (Normal)": "Normal",
        "輕微不平衡/積塵 (Warning)": "Warning - Imbalance",
        "葉片嚴重破損/異物 (Blade Fault)": "Fault - Blade Damage",
        "輕微轉子偏心 (Warning)": "Warning - Eccentricity",
        "嚴重軸承磨損 (Bearing Fault)": "Fault - Bearing Wear",
        "流體輕微微氣蝕 (Warning)": "Warning - Cavitation",
        "軸封嚴重磨損/空轉 (Pump Cavitation)": "Fault - Severe Cavitation",
        "閥體輕微結垢/滯遲 (Warning)": "Warning - Sluggish",
        "氣體/液體嚴重洩漏 (Valve Leakage)": "Fault - Leakage",
        "潤滑油脂不足 (Warning)": "Warning - Low Lube",
        "軌道金屬剝落/刮傷 (Rail Scratch)": "Fault - Rail Scratch",
        "齒面輕微點蝕 (Warning)": "Warning - Pitting",
        "輪齒嚴重點蝕/缺角 (Gear Damage)": "Fault - Tooth Damage"
    }

    category_en = category.split("(")[-1].replace(")", "").strip()
    status_en = status_en_map.get(status_option, "Normal")

    # 若非正常狀態，在頻譜圖上繪製黃色/紅色高頻異常框選
    if "Warning" in status_en:
        ax.axhspan(1500, 4000, color='yellow', alpha=0.25, linestyle='--', linewidth=1.5)
        ax.text(0.1, 2200, " Warning Anomaly Region", color='yellow', fontsize=9, fontweight='bold')
    elif "Fault" in status_en:
        ax.axhspan(2000, 7500, color='red', alpha=0.25, linestyle='--', linewidth=1.5)
        ax.text(0.1, 3500, " Severe Impact / Friction Region", color='red', fontsize=9, fontweight='bold')

    ax.set_title(f"Edge AI Feature: Mel-Spectrogram ({category_en} - {status_en})", fontsize=12, pad=10)

    plt.tight_layout()
    st.pyplot(fig)

# ---------------- DCASE / MIMII 基準聲學特徵指標卡片 ----------------
    st.markdown("##### 📊 DCASE / MIMII 基準聲學特徵 (Benchmark Acoustic Metrics)")
    
    rms_val = float(np.sqrt(np.mean(y**2)))
    cent_val = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    zcr_val = float(np.mean(librosa.feature.zero_crossing_rate(y=y)))

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric(
        "時域均方根能量 (RMS Energy)", 
        f"{rms_val:.4f}", 
        delta="DCASE 標準能量" if alert_level == "GREEN" else "振幅衝擊偏高", 
        delta_color="normal" if alert_level == "GREEN" else "inverse"
    )
    m_col2.metric(
        "頻譜中心 (Spectral Centroid)", 
        f"{int(cent_val)} Hz", 
        delta="MIMII 基頻區間" if cent_val < 1800 else "高頻異音轉移", 
        delta_color="normal" if cent_val < 1800 else "inverse"
    )
    m_col3.metric(
        "過零率 (Zero Crossing Rate)", 
        f"{zcr_val:.4f}", 
        delta="平滑運轉特徵" if zcr_val < 0.06 else "衝擊/摩擦特徵", 
        delta_color="normal" if zcr_val < 0.06 else "inverse"
    )

# Tab 2: 歷史趨勢與數據表
with tab2:
    st.markdown("#### 近 7 次巡檢歷史重構誤差 (MSE Trend)")
    chart_data = pd.DataFrame({
        "Batch": [f"T-{6-i}" for i in range(7)],
        "MSE Loss": history_mse
    })
    st.line_chart(chart_data.set_index("Batch"))

    st.markdown("#### 歷史巡檢詳細紀錄表 (Inspection Records)")
    
    # 計算歷史健康度 (純數字)
    history_hi = [int(max(0, min(100, 100 - (m * 680)))) for m in history_mse]

    # 動態產生對應的狀態標籤 (統一簡短格式)
    history_status = []
    for m in history_mse:
        if m < 0.005:
            history_status.append("正常")
        elif m < 0.05:
            history_status.append("預警 / 風噪干擾" if "實測風場聲" in category else "預警")
        else:
            history_status.append("嚴重故障")

    # 產生日期序列 (T-6 至 今日)
    from datetime import datetime, timedelta
    base_date = datetime.now() - timedelta(days=6)
    dates = [(base_date + timedelta(days=i)).strftime("%Y-%m-%d 08:00") for i in range(7)]

    df_history = pd.DataFrame({
        "巡檢時間": dates,
        "設備狀態": history_status,
        "MSE 重構誤差": [round(m, 4) for m in history_mse],
        "健康度 (HI)": history_hi
    })

    # 顯示表格 (隱藏左側數字索引)
    st.dataframe(df_history, use_container_width=True, hide_index=True)

# Tab 3: 時域波形與 FFT 頻譜
with tab3:
    st.markdown("#### 時域波形 (Waveform) 與 快速傅立葉變換 (FFT Spectrum)")
    st.markdown(
        "- **上方時域圖 (Time Domain)**：`X 軸: 時間 Time (s)` | `Y 軸: 振幅 Amplitude`\n"
        "- **下方頻域圖 (FFT Spectrum)**：`X 軸: 頻率 Frequency (Hz)` | `Y 軸: 聲訊強度 Magnitude`"
    )
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5))
    
    time_axis = np.linspace(0, len(y) / sr, len(y))
    ax1.plot(time_axis, y, color='#1f77b4', alpha=0.8)
    ax1.set_title("Time-Domain Signal (Waveform)", fontsize=10)
    ax1.set_xlabel("Time (s)", fontsize=9)
    ax1.set_ylabel("Amplitude", fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    n = len(y)
    fft_vals = np.abs(np.fft.rfft(y))
    freq_axis = np.fft.rfftfreq(n, 1/sr)
    ax2.plot(freq_axis, fft_vals, color='#d62728', alpha=0.8)
    ax2.set_title("Frequency Domain Spectrum (FFT Analysis)", fontsize=10)
    ax2.set_xlabel("Frequency (Hz)", fontsize=9)
    ax2.set_ylabel("Magnitude", fontsize=9)
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    st.pyplot(fig)

# 側邊欄匯出報告按鈕
import json
report_data = {
    "device_category": category,
    "status_option": status_option,
    "mse_score": mse_score,
    "health_index": f"{hi_score}%",
    "alert_level": alert_level
}
st.sidebar.download_button(
    label="📥 下載聲學巡檢報告 (JSON)",
    data=json.dumps(report_data, ensure_ascii=False, indent=2),
    file_name=f"acoustic_report_{category_en}.json",
    mime="application/json"
)