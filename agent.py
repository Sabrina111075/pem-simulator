import google.generativeai as genai
import sys
import io
import re

class OpenHarnessGeminiAgent:
    def __init__(self, api_key: str, model_name: str = "gemini-3.5-flash-lite"):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        
    def run(self, prompt: str, system_instruction: str = "") -> dict:
        logs = []
        logs.append("[OpenHarness Core] 初始化 Agent 沙盒環境...")
        logs.append(f"[OpenHarness Core] 掛載推理引擎: {self.model_name}")
        
        # 加上讓 Agent 能夠輸出 Python 代碼的提示強迫
        enhanced_system_instruction = system_instruction + (
            "\n【Harness 執行指令】如果你需要進行數學計算、擬合曲線或繪製圖表，"
            "請將 Python 程式碼包在 ```python ... ``` 區塊中。"
            "請使用 matplotlib 或 plotly 繪圖，並將圖表物件賦值給名為 `fig` 的變數。"
        )
        
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=enhanced_system_instruction
            )
            
            logs.append("[OpenHarness Pipeline] 正在傳送任務至 Gemini API...")
            response = model.generate_content(prompt)
            text_response = response.text
            logs.append("[OpenHarness Pipeline] 收到 Agent 思考邏輯與回應。")
            
            # 檢查回應中是否有可執行的 Python 程式碼
            code_match = re.search(r"```python\s*(.*?)\s*```", text_response, re.DOTALL)
            fig = None
            execution_output = ""
            
            if code_match:
                code = code_match.group(1)
                logs.append("[OpenHarness Sandbox] 檢測到 Python 執行代碼，啟動自動化沙盒...")
                
                # 建立安全的執行環境
                local_scope = {}
                old_stdout = sys.stdout
                redirected_output = io.StringIO()
                sys.stdout = redirected_output
                
                try:
                    exec(code, {"__builtins__": __builtins__}, local_scope)
                    sys.stdout = old_stdout
                    execution_output = redirected_output.getvalue()
                    fig = local_scope.get("fig", None)
                    logs.append("[OpenHarness Sandbox] 程式碼執行成功！數據與圖表已捕獲。")
                except Exception as exec_err:
                    sys.stdout = old_stdout
                    logs.append(f"[OpenHarness Sandbox Error] 執行代碼失敗: {str(exec_err)}")
                    execution_output = f"代碼執行異常: {str(exec_err)}"
            else:
                logs.append("[OpenHarness Sandbox] 未檢測到代碼區塊，純文字輸出。")
                
            return {
                "status": "success",
                "response": text_response,
                "fig": fig,
                "execution_output": execution_output,
                "logs": logs
            }
            
        except Exception as e:
            logs.append(f"[OpenHarness Error] 異常: {str(e)}")
            return {
                "status": "error",
                "response": f"❌ 執行失敗：{str(e)}",
                "fig": None,
                "execution_output": "",
                "logs": logs
            }