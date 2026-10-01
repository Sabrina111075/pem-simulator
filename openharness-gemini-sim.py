import streamlit as st
from agent import OpenHarnessGeminiAgent

st.set_page_config(
    page_title="OpenHarness + Gemini 模擬平台",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 OpenHarness x Gemini 智能代理模擬平台")
st.caption("基於 OpenHarness 思想與 Gemini 2.0 API 構建的輕量級 Agent 執行環境")

# 側邊欄配置
with st.sidebar:
    st.header("⚙️ 系統設定")
    api_key = st.text_input("Gemini API Key", type="password", help="請輸入您的 Google AI Studio API Key")
    
    model_choice = st.selectbox(
        "模型版本選擇",
        ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash"],
        index=0,
        help="預設使用 Gemini 2.0 Flash，兼具速度與高額度配額"
    )
    
    system_prompt = st.text_area(
        "System Instruction (系統指令)",
        value="你是一個運作在 OpenHarness 模擬平台上的高智商助手，請簡潔且精確地回答問題。",
        height=120
    )

# 主要對話與模擬區域
prompt = st.chat_input("請輸入測試指令或任務...")

if prompt:
    if not api_key:
        st.error("⚠️ 請先在左側邊欄輸入 Gemini API Key！")
    else:
        # 建立 Agent 實例
        agent = OpenHarnessGeminiAgent(api_key=api_key, model_name=model_choice)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("💬 Agent 執行結果")
            with st.spinner("OpenHarness 正在協同 Gemini 推理中..."):
                result = agent.run(prompt=prompt, system_instruction=system_prompt)
                
                if result["status"] == "success":
                    st.success("執行成功！")
                    st.markdown(result["response"])
                else:
                    st.error(result["response"])

        with col2:
            st.subheader("🔍 OpenHarness 運作日誌")
            st.info("追蹤 Agent 思考與 Harness 機制的底層日誌：")
            for log in result["logs"]:
                st.code(log, language="text")