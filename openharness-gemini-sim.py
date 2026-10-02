import streamlit as st
from agent import OpenHarnessGeminiAgent

st.set_page_config(
    page_title="OpenHarness + Gemini 模擬平台",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 OpenHarness x Gemini 智能代理模擬平台")
st.caption("基於 OpenHarness 思想與 Gemini API 構建的輕量級 Agent 執行環境（整合沙盒執行器）")

# 側邊欄配置
with st.sidebar:
    st.header("⚙️ 系統設定")
    api_key = st.text_input("Gemini API Key", type="password", help="AQ.Ab8RN6JDcsOVBjuxZv_JNkw5Ks2xXU-7_HS-XkFngIUtiiSnLQ")
    
    model_choice = st.selectbox(
        "模型版本選擇",
        [
            "gemini-3.5-flash-lite",
            "gemini-3.6-flash",
            "gemini-3.1-pro"
        ],
        index=0
    )
    
    system_prompt = st.text_area(
        "System Instruction (系統指令)",
        value="你是一個專門服務於 PEM 水分解與數位分身（Digital Twin）領域的高智商 AI 工程師。請精確解答並提供自動化 Python 分析代碼。",
        height=120
    )

# 主要對話與模擬區域
prompt = st.chat_input("請輸入測試指令（例：請模擬 PEM 電解槽在 60°C 與 80°C 下的 I-V 特性曲線並繪圖）...")

if prompt:
    if not api_key:
        st.error("⚠️ 請先在左側邊欄輸入 Gemini API Key！")
    else:
        agent = OpenHarnessGeminiAgent(api_key=api_key, model_name=model_choice)
        
        with st.spinner("OpenHarness 沙盒啟動中，協同 Gemini 推理與執行代碼..."):
            result = agent.run(prompt=prompt, system_instruction=system_prompt)
            
            st.subheader("💬 Agent 思考與分析結果")
            if result["status"] == "success":
                st.success("任務執行完成！")
                st.markdown(result["response"])
                
                # 如果沙盒成功繪製出圖表，直接呈現於前端！
                if result.get("fig"):
                    st.subheader("📊 OpenHarness 沙盒即時渲染圖表")
                    st.pyplot(result["fig"])
                
                if result.get("execution_output"):
                    with st.expander("💻 沙盒控制台輸出 (Console Output)"):
                        st.code(result["execution_output"])
            else:
                st.error(result["response"])
            
            st.divider()
            
            with st.expander("🔍 OpenHarness 運作日誌 (點擊展開/收合)", expanded=True):
                st.info("追蹤 Agent 思考、沙盒代碼捕獲與 Harness 執行層日誌：")
                log_text = "\n".join(result["logs"])
                st.code(log_text, language="text", line_numbers=True)