import os
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 頁面標題與佈局設定
st.set_page_config(page_title="CLI + Gemini 模擬器", layout="wide", page_icon="🚀")

st.title("🚀 CLI + Gemini 自動生成流程圖與 3D 模擬")
st.caption("結合 Gemini 2.5 結構化輸出與前端渲染技術")

# 檢查與取得 API Key (優先讀取 Secrets，若無則提供 Sidebar 輸入)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("輸入 Gemini API Key", type="password")

if not api_key:
    st.warning("請先在左側邊欄輸入你的 GEMINI_API_KEY，或於 Streamlit Secrets 中設定。")
    st.stop()

client = genai.Client(api_key=api_key)

# Pydantic 結構化輸出定義
class FlowchartOutput(BaseModel):
    title: str = Field(description="流程圖標題")
    mermaid_code: str = Field(description="合法的 Mermaid.js flowchart 語法內容，請勿包含 markdown 標籤")
    description: str = Field(description="流程圖說明")

class ThreeJSOutput(BaseModel):
    title: str = Field(description="3D 場景標題")
    html_code: str = Field(description="包含完整 Three.js 腳本的可執行 HTML 程式碼")
    summary: str = Field(description="3D 場景說明")

# 功能頁籤
tab1, tab2 = st.tabs(["📊 Mermaid 流程圖生成", "🎲 Three.js 3D 模擬生成"])

# Tab 1: 流程圖生成器
with tab1:
    st.header("Mermaid 流程圖自動生成")
    prompt_flow = st.text_area(
        "輸入流程圖需求描述：",
        value="請繪製一個使用者登入與雙重驗證 (2FA) 的流程，包含登入失敗重試與驗證碼發送。",
        height=100
    )
    
    if st.button("生成流程圖", type="primary"):
        with st.spinner("Gemini 正在規劃流程圖架構..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
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

# Tab 2: 3D 模擬生成器
with tab2:
    st.header("Three.js 3D 互動模擬生成")
    prompt_3d = st.text_area(
        "輸入 3D 場景需求描述：",
        value="創建一個太陽系 3D 模擬，包含中央發光的太陽、繞行的地球，並加入 OrbitControls 旋轉視角。",
        height=100
    )
    
    if st.button("生成 3D 場景", type="primary"):
        with st.spinner("Gemini 正在撰寫 Three.js 程式碼..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
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