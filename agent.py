import streamlit as st
from agent import OpenHarnessGeminiAgent

# 頁面基本配置
st.set_page_config(
    page_title="OpenHarness x Gemini 模擬平台",
    page_icon="🤖",
    layout="wide"
)

# 1. 自動從 Streamlit Secrets 讀取預設 API Key
default_api_key = ""
if "GEMINI_API_KEY" in st.secrets:
    default_api_key = st.secrets["GEMINI_API_KEY"]

# 側邊欄：系統設定
st.sidebar.title("⚙️ 系統設定")

# 2. 將預設值帶入文字輸入框
api_key = st.sidebar.text_input(
    "Gemini API Key",
    value=default_api_key,
    type="password",
    help="已自動讀取雲端 Secrets，亦可手動修改。"
)

model_name = st.sidebar.selectbox(
    "模型版本選擇",
    options=["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
    index=1
)

default_system_instruction = (
    "你是一個專門服務於 PEM 水分解與數位分身（Digital Twin）領域的高智商 AI 工程師。"
    "請精確解答並提供自動化 Python 分析代碼。"
)

system_instruction = st.sidebar.text_area(
    "System Instruction (系統指令)",
    value=default_system_instruction,
    height=150
)

# 主畫面標題
st.title("🤖 OpenHarness x Gemini 智能代理模擬平台")
st.caption("基於 OpenHarness 思想與 Gemini API 構建的輕量級 Agent 執行環境（整合沙盒執行器與自動 Self-Healing 修正）")

# 初始化對話紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示歷史對話
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "fig" in message and message["fig"] is not None:
            st.pyplot(message["fig"])
        if "execution_output" in message and message["execution_output"]:
            with st.expander("💻 沙盒控制台輸出 (Console Output)"):
                st.code(message["execution_output"], language="text")

# 對話輸入
if prompt := st.chat_input("請輸入測試指令（例：請模擬 PEM 電解槽在 60°C 與 80°C 下的 I-V 特性曲線並繪圖）..."):
    if not api_key:
        st.error("⚠️ 請先在側邊欄輸入 Gemini API Key！")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        agent = OpenHarnessGeminiAgent(api_key=api_key, model_name=model_name)
        
        with st.status("🚀 OpenHarness Agent 運作中...", expanded=True) as status:
            result = agent.run(prompt=prompt, system_instruction=system_instruction)
            
            with st.expander("🔍 OpenHarness 運作日誌 (點擊展開/收合)"):
                for log in result["logs"]:
                    st.text(log)
                    
            if result["status"] == "success":
                status.update(label="✅ Agent 任務執行完成！", state="complete", expanded=False)
            else:
                status.update(label="❌ Agent 執行過程發生錯誤", state="error", expanded=True)

        st.markdown(result["response"])
        
        if result["fig"] is not None:
            st.pyplot(result["fig"])
            
        if result["execution_output"]:
            with st.expander("💻 沙盒控制台輸出 (Console Output)"):
                st.code(result["execution_output"], language="text")
                
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "fig": result["fig"],
            "execution_output": result["execution_output"]
        })