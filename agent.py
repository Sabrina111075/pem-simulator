import google.generativeai as genai

class OpenHarnessGeminiAgent:
    def __init__(self, api_key: str, model_name: str = "gemini-3.5-flash-lite"):
        """
        初始化 OpenHarness Gemini Agent 模擬環境
        """
        self.api_key = api_key
        self.model_name = model_name
        
        # 設定 Google Generative AI API Key
        genai.configure(api_key=self.api_key)
        
    def run(self, prompt: str, system_instruction: str = "") -> dict:
        """
        執行 Harness 模擬流程，包含日誌記錄與 API 呼叫
        """
        logs = []
        logs.append("[OpenHarness Core] 初始化 Agent 環境...")
        logs.append(f"[OpenHarness Core] 掛載模型: {self.model_name}")
        logs.append("[OpenHarness Core] 正在建立連線與檢查安全權限...")
        
        try:
            # 建立模型實例
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction if system_instruction else None
            )
            
            logs.append("[OpenHarness Pipeline] 正在傳送請求給 Gemini API...")
            
            response = model.generate_content(prompt)
            
            logs.append("[OpenHarness Pipeline] 成功接收來自 Gemini 的回應！")
            logs.append("[OpenHarness Core] 任務完成，解構代理環境。")
            
            return {
                "status": "success",
                "response": response.text,
                "logs": logs
            }
            
        except Exception as e:
            logs.append(f"[OpenHarness Error] 執行過程發生異常: {str(e)}")
            return {
                "status": "error",
                "response": f"❌ 執行失敗：{str(e)}",
                "logs": logs
            }