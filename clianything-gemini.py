#!/usr/bin/env python3
import os
import sys
import argparse
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 檢查 GEMINI_API_KEY 環境變數
if not os.environ.get("GEMINI_API_KEY"):
    print("[Error] 請先設定 GEMINI_API_KEY 環境變數！")
    print("例如：export GEMINI_API_KEY='your_api_key_here'")
    sys.exit(1)

client = genai.Client()

# -------------------------------------------------------------------
# 定義結構化輸出格式 (Pydantic Schema)
# -------------------------------------------------------------------

class FlowchartOutput(BaseModel):
    title: str = Field(description="流程圖標題")
    mermaid_code: str = Field(description="合法的 Mermaid.js flowchart 語法內容，請勿包含 markdown 標籤或 ``` 符號")
    description: str = Field(description="流程圖的簡短說明")

class ThreeJSOutput(BaseModel):
    title: str = Field(description="3D 場景標題")
    html_code: str = Field(description="包含完整 Three.js 腳本的可直接運行 HTML 程式碼")
    summary: str = Field(description="3D 場景的亮點說明")

# -------------------------------------------------------------------
# 核心生成邏輯
# -------------------------------------------------------------------

def generate_flowchart(prompt: str, output_file: str):
    """叫用 Gemini API 生成 Mermaid 流程圖並包裝為 HTML"""
    print(f"[1/2] 正在分析需求並生成流程圖：'{prompt}'...")
    
    system_instruction = (
        "你是一個頂級的系統架構師與流程圖專家。"
        "請根據使用者的需求生成標準的 Mermaid.js (flowchart TD 或 LR) 程式碼。"
        "確保節點語法正確，並且結構清晰易讀。"
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=FlowchartOutput,
                temperature=0.2,
            ),
        )

        result: FlowchartOutput = response.parsed
        
        # 包裝成包含 Mermaid.js CDN 的網頁範本
        html_template = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="utf-8">
    <title>{result.title}</title>
    <script src="[https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js](https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js)"></script>
    <script>mermaid.initialize({{startOnLoad:true, theme: 'default'}});</script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 2rem; background: #f8f9fa; color: #333; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        h1 {{ margin-top: 0; color: #1a73e8; }}
        .desc {{ color: #5f6368; margin-bottom: 2rem; line-height: 1.5; }}
        .mermaid {{ display: flex; justify-content: center; margin-top: 1rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{result.title}</h1>
        <p class="desc">{result.description}</p>
        <div class="mermaid">
{result.mermaid_code}
        </div>
    </div>
</body>
</html>"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_template)
        
        print(f"[2/2] ✅ 流程圖已成功生成並存至：{output_file}")
        print("\n--- [Mermaid 語法預覽] ---")
        print(result.mermaid_code)
        print("---------------------------\n")

    except Exception as e:
        print(f"[Error] 生成流程圖失敗：{e}")


def generate_3d_scene(prompt: str, output_file: str):
    """叫用 Gemini API 生成 Three.js 3D 模擬 HTML 檔"""
    print(f"[1/2] 正在建構 3D 模擬場景：'{prompt}'...")
    
    system_instruction = (
        "你是一個 Three.js 3D 互動專家。"
        "根據使用者需求，編寫一個完整且可直接運行的單一 HTML 檔案。"
        "必須包含："
        "1. CDN 引入 Three.js 與 OrbitControls。"
        "2. 動態視窗 resize 監聽、燈光（環境光 + 平行光）、陰影與動畫循環 (requestAnimationFrame)。"
        "3. 適合主題的幾何體與材質設定，呈現生動且符合需求的 3D 模擬畫面。"
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=ThreeJSOutput,
                temperature=0.4,
            ),
        )

        result: ThreeJSOutput = response.parsed

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.html_code)
        
        print(f"[2/2] ✅ 3D 模擬場景已成功生成並存至：{output_file}")
        print(f"📌 場景說明：{result.summary}\n")

    except Exception as e:
        print(f"[Error] 生成 3D 場景失敗：{e}")

# -------------------------------------------------------------------
# CLI 命令列入口設定
# -------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="CLI-Anything + Gemini：自動化生成流程圖與 3D 模擬頁面")
    subparsers = parser.add_subparsers(dest="command", required=True, help="請選擇要執行的指令")

    # 子命令 1: 生成流程圖
    flow_parser = subparsers.add_parser("flowchart", help="生成 Mermaid 流程圖 HTML")
    flow_parser.add_argument("-p", "--prompt", required=True, help="流程圖的需求描述")
    flow_parser.add_argument("-o", "--output", default="flowchart.html", help="輸出 HTML 檔名 (預設: flowchart.html)")

    # 子命令 2: 生成 3D 模擬
    three_parser = subparsers.add_parser("3d", help="生成 Three.js 3D 模擬 HTML")
    three_parser.add_argument("-p", "--prompt", required=True, help="3D 場景的需求描述")
    three_parser.add_argument("-o", "--output", default="scene3d.html", help="輸出 HTML 檔名 (預設: scene3d.html)")

    args = parser.parse_args()

    if args.command == "flowchart":
        generate_flowchart(args.prompt, args.output)
    elif args.command == "3d":
        generate_3d_scene(args.prompt, args.output)

if __name__ == "__main__":
    main()