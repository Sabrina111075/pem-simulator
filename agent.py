import google.generativeai as genai
import sys
import io
import re

class OpenHarnessGeminiAgent:
    def __init__(self, api_key: str, model_name: str = "gemini-3.6-flash"):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        
    def _execute_code(self, code: str, logs: list):
        """在沙盒環境中執行 Python 程式碼並回傳結果與圖表"""
        import numpy as np
        import matplotlib.pyplot as plt
        
        # 設置沙盒的全域變數，預載常用的科學計算庫
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
            plt.close('all')  # 清空之前的畫布
            exec(code, sandbox_globals)
            sys.stdout = old_stdout
            execution_output = redirected_output.getvalue()
            
            # 優先抓取 explicit 的 fig，若沒有則抓取當前 Matplotlib 的圖表
            fig = sandbox_globals.get("fig", None)
            if fig is None:
                fig = plt.gcf()
                
            return True, fig, execution_output, ""
        except Exception as exec_err:
            sys.stdout = old_stdout
            err_msg = str(exec_err)
            return False, None, redirected_output.getvalue(), err_msg

    def run(self, prompt: str, system_instruction: str = "", max_retries: int = 2) -> dict:
        logs = []
        logs.append("[OpenHarness Core] 初始化 Agent 沙盒環境...")
        logs.append(f"[OpenHarness Core] 掛載推理引擎: {self.model_name}")
        
        enhanced_system_instruction = system_instruction + (
            "\n【Harness 執行指令】如果你需要進行數據分析或繪製圖表："
            "\n1. 必須在程式碼開頭包含所有必要的 import 語句（如 import numpy as np, import matplotlib.pyplot as plt）。"
            "\n2. 確保所有繪圖的 x 與 y 陣列長度嚴格一致！如果 y 是常數（例如參考電壓），請使用 np.full_like(x, value) 或 np.ones_like(x) * value 延伸成相同維度的陣列。"
            "\n3. 將完整的 Python 程式碼包在 ```python ... ``` 區塊中。"
        )
        
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=enhanced_system_instruction
            )
            
            chat = model.start_chat(history=[])
            logs.append("[OpenHarness Pipeline] 正在傳送任務至 Gemini API...")
            
            response = chat.send_message(prompt)
            text_response = response.text
            logs.append("[OpenHarness Pipeline] 收到 Agent 思考邏輯與回應。")
            
            code_match = re.search(r"```python\s*(.*?)\s*```", text_response, re.DOTALL)
            fig = None
            execution_output = ""
            
            if code_match:
                code = code_match.group(1)
                logs.append("[OpenHarness Sandbox] 檢測到 Python 執行代碼，啟動自動化沙盒...")
                
                # 初次執行
                success, fig, execution_output, error_msg = self._execute_code(code, logs)
                
                # --- 自動修復機制 (Self-Healing Loop) ---
                retry_count = 0
                while not success and retry_count < max_retries:
                    retry_count += 1
                    logs.append(f"[OpenHarness Self-Healing] 偵測到執行異常: '{error_msg}'")
                    logs.append(f"[OpenHarness Self-Healing] 觸發 Agent 自修復迴圈 (第 {retry_count}/{max_retries} 次重試)...")
                    
                    fix_prompt = (
                        f"剛才執行的 Python 代碼出現錯誤：\n`{error_msg}`\n\n"
                        f"請修正程式碼。特別注意：如果錯誤是 shape 或維度不匹配 (如 shapes (300,) and (1,))，"
                        f"請確保繪圖時 x 與 y 陣列維度相同（例如對純量使用 np.full_like(x, val)）。\n"
                        f"請僅輸出修正後的完整 ```python ... ``` 區塊。"
                    )
                    
                    fix_response = chat.send_message(fix_prompt)
                    text_response += f"\n\n--- 🔧 Agent 自動自我修正 (第 {retry_count} 次) ---\n" + fix_response.text
                    
                    new_code_match = re.search(r"```python\s*(.*?)\s*```", fix_response.text, re.DOTALL)
                    if new_code_match:
                        code = new_code_match.group(1)
                        success, fig, execution_output, error_msg = self._execute_code(code, logs)
                    else:
                        break
                
                if success:
                    logs.append("[OpenHarness Sandbox] 程式碼執行成功！數據與圖表已順利捕獲！")
                else:
                    logs.append(f"[OpenHarness Sandbox Error] 達最大重試次數，執行仍失敗: {error_msg}")
                    execution_output = f"代碼執行異常: {error_msg}"
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