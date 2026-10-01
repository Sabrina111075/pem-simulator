import os
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_random_exponential

class OpenHarnessGeminiAgent:
    def __init__(self, api_key: str, model_name: str = "gemini-3.8-flash"):
        """
        初始化 Harness 代理器
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)
        self.execution_logs = []

    def _log(self, message: str):
        """Harness 內部透明日誌追蹤"""
        self.execution_logs.append(message)

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(5))
    def run(self, prompt: str, system_instruction: str = "你是一個運作在 OpenHarness 模擬平台上的智能 Agent。") -> dict:
        """
        帶有自動指數退避重試（防止 429 限制）的 Agent 執行核心
        """
        self.execution_logs.clear()
        self._log(f"[Harness Initialized] 模型: {self.model_name}")
        self._log(f"[Input Prompt] {prompt}")

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            )
            
            self._log("[API Call] 送出請求至 Gemini API...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            self._log("[API Response] 成功接收回應")
            
            return {
                "status": "success",
                "response": response.text,
                "logs": self.execution_logs
            }

        except Exception as e:
            self._log(f"[Harness Error] 發生異常: {str(e)}")
            return {
                "status": "error",
                "response": f"執行失敗: {str(e)}",
                "logs": self.execution_logs
            }