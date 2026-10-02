import os
import re
import sys
import io
import traceback
import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ==========================================
# 1. 頁面基本配置
# ==========================================
st.set_page_config(
    page_title="OpenHarness x Gemini 智能代理模擬平台",
    page_icon="🤖",
    layout="wide"
)

# 設定 Matplotlib 中文字體與負號顯示
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 2. 讀取 API Key
# ==========================================
SECRET_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# ==========================================
# 3. 側邊欄設定
# ==========================================
with st.sidebar:
    st.header("⚙️ 系統設定")
    
    api_key_input = st.text_input(
        "Gemini API Key",
        value=SECRET_API_KEY,
        type="password",
        help="已自動載入固定的 API Key"
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
        value=(
            "你是一個專門服務於 PEM 水分解與數位分身（Digital Twin）領域的高智商 AI 工程師。"
            "請精確解答並提供自動化 Python 分析代碼。"
            "注意事項：\n"
            "1. 必須引入所有需要的模組（如 import numpy as np, import matplotlib.pyplot as plt）。\n"
            "2. 避免在 f-string 中混用複雜的 LaTeX 大括號（如 f'${R_p}$' 改寫為 'R_p = ' + str(R_p_val)）。\n"
            "3. 程式碼最後呼叫 plt.show()。"
        ),
        height=180
    )

# ==========================================
# 4. 主畫面 UI
# ==========================================
st.title("🤖 OpenHarness x Gemini 智能代理模擬平台")
st.caption("基於 OpenHarness 思想與 Gemini API 構建的輕量級 Agent 執行環境（整合自動沙盒圖表渲染器）")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "harness_logs" not in st.session_state:
    st.session_state.harness_logs = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 5. OpenHarness 增強型沙盒執行器
# ==========================================
def execute_python_code(code_str):
    """在受控沙盒環境中執行 Python 程式碼並捕獲 Matplotlib 圖表與報錯"""
    st.session_state.harness_logs.append("[OpenHarness Sandbox] 提取 Python 代碼區塊成功...")
    st.session_state.harness_logs.append("[OpenHarness Sandbox] 啟動內嵌沙盒編譯執行環境...")
    
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    
    plt.close('all')
    
    # 預載常用的科學計算庫
    exec_globals = {
        'plt': plt,
        'np': np,
        'pd': pd,
        'st': st
    }
    
    # 嘗試動態載入 scipy (若有安裝)
    try:
        import scipy
        exec_globals['scipy'] = scipy
    except ImportError:
        pass

    try:
        exec(code_str, exec_globals)
        fig = plt.gcf()
        st.session_state.harness_logs.append("[OpenHarness Sandbox] 程式碼執行完畢，圖表成功捕獲！")
        return redirected_output.getvalue(), fig, None
    except Exception as e:
        error_detail = traceback.format_exc()
        st.session_state.harness_logs.append(f"[OpenHarness Error] 沙盒執行異常: {str(e)}")
        return redirected_output.getvalue(), None, error_detail
    finally:
        sys.stdout = old_stdout

# ==========================================
# 6. 對話與執行核心
# ==========================================
user_prompt = st.chat_input("請輸入測試指令（例：請模擬 PEM 電解槽在 60°C 與 80°C 下的 I-V 特性曲線並繪圖）...")

if user_prompt:
    effective_api_key = api_key_input.strip() or SECRET_API_KEY.strip()
    if not effective_api_key:
        st.error("❌ 請先提供有效的 Gemini API Key！")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    st.session_state.harness_logs.append(f"[OpenHarness] 接收用戶指令: '{user_prompt}'")

    with st.chat_message("assistant"):
        st.subheader("💭 Agent 思考與分析結果")
        
        try:
            genai.configure(api_key=effective_api_key)
            model = genai.GenerativeModel(
                model_name=model_choice,
                system_instruction=system_instruction_input
            )
            
            response = model.generate_content(user_prompt)
            result_text = response.text
            
            st.markdown(result_text)
            
            # 自動抓取程式碼區塊
            code_blocks = re.findall(r"```python\n(.*?)```", result_text, re.DOTALL)
            if code_blocks:
                st.subheader("📊 OpenHarness 沙盒自動渲染圖表")
                for idx, code in enumerate(code_blocks):
                    with st.status(f"🚀 沙盒正在執行第 {idx+1} 段 Python 模擬代碼...", expanded=True) as status:
                        output, fig, error_detail = execute_python_code(code)
                        
                        if fig and len(fig.get_axes()) > 0:
                            st.pyplot(fig)
                            status.update(label="✅ 圖表模擬渲染成功！", state="complete")
                        elif error_detail:
                            st.error("❌ 沙盒執行錯誤細節：")
                            st.code(error_detail, language="python")
                            status.update(label="❌ 執行失敗（請查看下方錯誤記錄）", state="error")
                        else:
                            status.update(label="ℹ️ 程式碼執行完成（無產出視覺化圖表）", state="complete")
                            
                        if output:
                            st.text("程式 Console 輸出：")
                            st.code(output)

            st.session_state.messages.append({"role": "assistant", "content": result_text})

        except Exception as e:
            st.error(f"❌ 執行失敗：{str(e)}")
            st.session_state.harness_logs.append(f"[OpenHarness Error] {str(e)}")

# ==========================================
# 7. 運作日誌摺疊選單
# ==========================================
with st.expander("🔍 OpenHarness 運作日誌 (點擊展開/收合)", expanded=False):
    st.write("追蹤 Agent 思考、沙盒代碼捕獲與 Harness 執行日誌：")
    if st.session_state.harness_logs:
        log_content = "\n".join(st.session_state.harness_logs)
        st.code(log_content, language="bash")
    else:
        st.info("尚無執行日誌，請在上方輸入指令進行測試。")