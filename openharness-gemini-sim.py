import os
import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 頁面基本配置與樣式
# ==========================================
st.set_page_config(
    page_title="OpenHarness x Gemini 智能代理模擬平台",
    page_icon="🤖",
    layout="wide"
)

# ==========================================
# 2. 讀取 API Key (優先從 Secrets，備用環境變數)
# ==========================================
# 支援在 Streamlit Cloud Secrets 設定：GEMINI_API_KEY = "AIzaSy..."
SECRET_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# ==========================================
# 3. 側邊欄：系統設定
# ==========================================
with st.sidebar:
    st.header("⚙️ 系統設定")
    
    # 填入 Secrets 中的 Key，或允許使用者輸入
    api_key_input = st.text_input(
        "AIzaSyDfIAeAuF89St4fozh4-Q1exM2GUZpfN1M",
        value=SECRET_API_KEY,
        type="password",
        help="已自動載入固定的 API Key，亦可手動調整"
    )
    
    model_choice = st.selectbox(
        "模型版本選擇",
        options=[
            "gemini-3.5-flash-lite",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ],
        index=0
    )
    
    system_instruction_input = st.text_area(
        "System Instruction (系統指令)",
        value="你是一個專門服務於 PEM 水分解與數位分身（Digital Twin）領域的高智商 AI 工程師。請精確解答並提供自動化 Python 分析代碼。",
        height=140
    )

# ==========================================
# 4. 主畫面 UI
# ==========================================
st.title("🤖 OpenHarness x Gemini 智能代理模擬平台")
st.caption("基於 OpenHarness 思想與 Gemini API 構建的輕量級 Agent 執行環境（整合沙盒執行器）")

# 初始化對話紀錄與 OpenHarness 日誌
if "messages" not in st.session_state:
    st.session_state.messages = []
if "harness_logs" not in st.session_state:
    st.session_state.harness_logs = []

# 顯示歷史對話
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 5. Agent 思考與執行核心邏輯 (修正 401 驗證)
# ==========================================
user_prompt = st.chat_input("請輸入測試指令（例：請模擬 PEM 電解槽在 60°C 與 80°C 下的 I-V 特性曲線並繪圖）...")

if user_prompt:
    # 檢查是否具備 API Key
    effective_api_key = api_key_input.strip() or SECRET_API_KEY.strip()
    
    if not effective_api_key:
        st.error("❌ 請先提供有效的 Gemini API Key！")
        st.stop()
        
    # 顯示使用者輸入
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 記錄 OpenHarness 監控日誌
    st.session_state.harness_logs.append(f"[OpenHarness] 接收用戶指令: '{user_prompt}'")
    st.session_state.harness_logs.append(f"[Harness Context] 載入模型配置: {model_choice}")

    # 執行 Gemini AI 推理
    with st.chat_message("assistant"):
        st.subheader("💭 Agent 思考與分析結果")
        response_placeholder = st.empty()
        
        try:
            # 🔑 關鍵修復點：正確配置 Google SDK，解決 401 ACCESS_TOKEN_TYPE_UNSUPPORTED 錯誤
            genai.configure(api_key=effective_api_key)
            
            # 初始化 GenerativeModel 並傳入系統指令
            model = genai.GenerativeModel(
                model_name=model_choice,
                system_instruction=system_instruction_input
            )
            
            st.session_state.harness_logs.append("[OpenHarness Sandbox] 建立隔離執行緒與上下文...")
            
            # 發送請求給 Gemini
            response = model.generate_content(user_prompt)
            
            # 輸出 AI 回應
            result_text = response.text
            response_placeholder.markdown(result_text)
            
            # 寫入歷史訊息與日誌
            st.session_state.messages.append({"role": "assistant", "content": result_text})
            st.session_state.harness_logs.append("[OpenHarness Sandbox] 任務順利執行完成，結果捕獲成功。")

        except Exception as e:
            error_msg = f"❌ 執行失敗：{str(e)}"
            st.error(error_msg)
            st.session_state.harness_logs.append(f"[OpenHarness Error] {str(e)}")

# ==========================================
# 6. OpenHarness 運作日誌摺疊選單
# ==========================================
with st.expander("🔍 OpenHarness 運作日誌 (點擊展開/收合)", expanded=False):
    st.write("追蹤 Agent 思考、沙盒代碼捕獲與 Harness 執行日誌：")
    if st.session_state.harness_logs:
        log_content = "\n".join(st.session_state.harness_logs)
        st.code(log_content, language="bash")
    else:
        st.info("尚無執行日誌，請在上方輸入指令進行測試。")