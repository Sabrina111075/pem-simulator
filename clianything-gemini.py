import os
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 頁面標題與佈局設定
st.set_page_config(page_title="OpenHarness & CLI + Gemini AI 整合平台", layout="wide", page_icon="⚡")

st.title("⚡ OpenHarness & CLI-Anything + Gemini AI 整合工作台")
st.caption("結合系統自動化測試、Mermaid 流程圖繪製與 Three.js 3D 互動模擬")

# 優先讀取 Streamlit Secrets 或環境變數
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif os.environ.get("GEMINI_API_KEY"):
    api_key = os.environ.get("GEMINI_API_KEY")

# 如果 Secrets 沒設定，才在左側顯示手動輸入框作為備用
if not api_key:
    api_key = st.sidebar.text_input("輸入 Gemini API Key", type="password")

if not api_key:
    st.warning("請先在 Streamlit Secrets 設定 GEMINI_API_KEY，或於左側邊欄輸入金鑰。")
    st.stop()

client = genai.Client(api_key=api_key)

# 設定採用的 Gemini 模型名稱
MODEL_NAME = "gemini-2.5-flash"

# -------------------------------------------------------------------
# Pydantic 結構化輸出定義
# -------------------------------------------------------------------

class FlowchartOutput(BaseModel):
    title: str = Field(description="流程圖標題")
    mermaid_code: str = Field(description="合法的 Mermaid.js flowchart 語法內容，請勿包含 markdown 標籤")
    description: str = Field(description="流程圖說明")

class ThreeJSOutput(BaseModel):
    title: str = Field(description="3D 場景標題")
    html_code: str = Field(description="包含完整 Three.js 腳本的可執行 HTML 程式碼")
    summary: str = Field(description="3D 場景說明")

class HarnessTestOutput(BaseModel):
    test_title: str = Field(description="測試案例名稱")
    test_script: str = Field(description="自動化測試或 CLI 執行腳本內容")
    expected_result: str = Field(description="預期測試結果與驗證標準")

# -------------------------------------------------------------------
# 功能頁籤
# -------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🛠️ OpenHarness 自動化測試引擎", 
    "📊 Mermaid 流程圖生成", 
    "🎲 Three.js 3D 模擬生成"
])

# Tab 1: OpenHarness 測試引擎
with tab1:
    st.header("🛠️ OpenHarness 系統測試與 Harness 腳本生成")
    prompt_harness = st.text_area(
        "輸入欲進行測試的系統模組或功能需求：",
        value="針對 PEM 電解槽模擬系統，設計一套涵蓋電流密度輸入、電壓響應計算與溫度邊界條件的自動化 Harness 測試腳本。",
        height=100
    )
    
    if st.button("生成 OpenHarness 測試案例", type="primary"):
        with st.spinner("OpenHarness 引擎正在規劃測試腳本..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt_harness,
                    config=types.GenerateContentConfig(
                        system_instruction="你是一個資深系統測試工程師與 OpenHarness 架構專家。請根據需求設計完整的測試腳本與驗證邏輯。",
                        response_mime_type="application/json",
                        response_schema=HarnessTestOutput,
                        temperature=0.2,
                    ),
                )
                res_harness: HarnessTestOutput = response.parsed
                
                st.subheader(f"📋 {res_harness.test_title}")
                st.success("✅ 測試腳本規劃完成！")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("**自動化 Harness 執行腳本：**")
                    st.code(res_harness.test_script, language="python")
                with col2:
                    st.markdown("**驗證點與預期結果：**")
                    st.info(res_harness.expected_result)
                    
            except Exception as e:
                st.error(f"生成失敗：{e}")

# Tab 2: 流程圖生成器
with tab2:
    st.header("📊 Mermaid 流程圖自動生成")
    prompt_flow = st.text_area(
        "輸入流程圖需求描述：",
        value="請繪製一個使用者登入與雙重驗證 (2FA) 的流程，包含登入失敗重試與驗證碼發送。",
        height=100
    )
    
    if st.button("生成流程圖", type="primary"):
        with st.spinner("Gemini 正在規劃流程圖架構..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt_flow,
                    config=types.GenerateContentConfig(
                        system_instruction="你是一個頂級系統架構師，請根據需求生成標準的 Mermaid.js flowchart (TD或LR) 語法。",
                        response_mime_type="application/json",
                        response_schema=FlowchartOutput,
                        temperature=0.2,
                    ),
                )
                res: FlowchartOutput = response.parsed
                
                st.subheader(res.title)
                st.write(res.description)
                
                # HTML 渲染 Mermaid
                html_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    <script>mermaid.initialize({{startOnLoad:true, theme:'default'}});</script>
                </head>
                <body style="background:transparent; display:flex; justify-content:center;">
                    <div class="mermaid">
                    {res.mermaid_code}
                    </div>
                </body>
                </html>
                """
                components.html(html_code, height=450, scrolling=True)
                
                with st.expander("檢視原始 Mermaid 語法"):
                    st.code(res.mermaid_code, language="mermaid")
                    
            except Exception as e:
                st.error(f"生成失敗：{e}")

# Tab 3: 3D 模擬生成器
with tab3:
    st.header("🎲 Three.js 3D 互動模擬生成")
    prompt_3d = st.text_area(
        "輸入 3D 場景需求描述：",
        value="創建一個太陽系 3D 模擬，包含中央發光的太陽、繞行的地球，並加入 OrbitControls 旋轉視角。",
        height=100
    )
    
    if st.button("生成 3D 場景", type="primary"):
        with st.spinner("Gemini 正在撰寫 Three.js 程式碼..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt_3d,
                    config=types.GenerateContentConfig(
                        system_instruction="你是一個 Three.js 3D 專家。請生成一個包含 CDN 引入、燈光、軌道控制與動畫循環的完整單一 HTML 檔案。",
                        response_mime_type="application/json",
                        response_schema=ThreeJSOutput,
                        temperature=0.4,
                    ),
                )
                res_3d: ThreeJSOutput = response.parsed
                
                st.subheader(res_3d.title)
                st.write(res_3d.summary)
                
                # 渲染 3D HTML
                components.html(res_3d.html_code, height=550)
                
            except Exception as e:
                st.error(f"生成失敗：{e}")