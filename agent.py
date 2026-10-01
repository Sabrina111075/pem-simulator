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
        
        # 強化系統提示，約束 AI 格式
        enhanced_system_instruction = system_instruction + (
            "\n【Harness 執行指令】如果你需要進行數據分析或繪製圖表："
            "\n1. 必須在程式碼開頭包含所有必要的 import 語句（例如 import numpy as np, import matplotlib.pyplot as plt）。"
            "\n2. 將完整的 Python 程式碼包在 ```python ... ``` 區塊中。"
            "\n3. 請使用 matplotlib 繪圖，並確保最後呼叫 plt.show() 或建立 fig 物件。"
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
            
            # 提取程式碼
            code_match = re.search(r"```python\s*(.*?)\s*```", text_response, re.DOTALL)
            fig = None
            execution_output = ""
            
            if code_match:
                code = code_match.group(1)
                logs.append("[OpenHarness Sandbox] 檢測到 Python 執行代碼，啟動自動化沙盒...")
                
                # 1. 預先引入常用的庫，防止 AI 漏寫 import 導致 NameError
                import numpy as np
                import matplotlib.pyplot as plt
                
                # 2. 構建沙盒變數空間 (Global Scope)
                sandbox_globals = {
                    "__builtins__": __builtins__,
                    "np": np,
                    "numpy": np,
                    "plt": plt,
                    "matplotlib": plt
                }
                
                old_stdout = sys.stdout
                redirected_output = io.StringIO()
                sys.stdout = redirected_output
                
                try:
                    # 在安全的沙盒環境中執行程式碼
                    exec(code, sandbox_globals)
                    sys.stdout = old_stdout
                    execution_output = redirected_output.getvalue()
                    
                    # 抓取圖表：優先抓取 explicit 的 fig，若沒有則抓取當前 Matplotlib 的圖表
                    fig = sandbox_globals.get("fig", None)
                    if fig is None:
                        fig = plt.gcf()  # 抓取當前 figure
                        
                    logs.append("[OpenHarness Sandbox] 程式碼執行成功！數據與圖表已順利捕獲！")
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