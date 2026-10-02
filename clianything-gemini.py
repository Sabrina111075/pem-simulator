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

# -------------------------------------------------------------------
# 邊欄設定：模型選擇與 API Key 輸入
# -------------------------------------------------------------------
st.sidebar.header("⚙️ 系統設定")

# 優先讀取 Streamlit Secrets 或環境變數
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif os.environ.get("GEMINI_API_KEY"):
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("輸入 Gemini API Key", type="password")

if not api_key:
    st.warning("請先在 Streamlit Secrets 設定 GEMINI_API_KEY，或於左側邊欄輸入金鑰。")
    st.stop()

# 模型選擇選單 (以 3.5-flash-lite 為優先)
selected_model_option = st.sidebar.selectbox(
    "選擇偏好的 Gemini 模型：",
    options=[
        "gemini-3.5-flash-lite (最快回應)",
        "gemini-3.6-flash (全方位)",
        "gemini-3.1-pro (進階推論)",
        "自動備援 (Auto Fallback)"
    ],
    index=0
)

# 解析選定的模型名稱
if "3.5-flash-lite" in selected_model_option:
    MODEL_CANDIDATES = ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.1-pro"]
elif "3.6-flash" in selected_model_option:
    MODEL_CANDIDATES = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.1-pro"]
elif "3.1-pro" in selected_model_option:
    MODEL_CANDIDATES = ["gemini-3.1-pro", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
else:
    MODEL_CANDIDATES = ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.1-pro"]

client = genai.Client(api_key=api_key)

def generate_with_fallback(contents, system_instruction, response_schema, temperature=0.2):
    """具備模型調用與自動備援機制的生成函式"""
    last_error = None
    for model_name in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=temperature,
                ),
            )
            return response.parsed, model_name
        except Exception as e:
            last_error = e
            continue
    raise RuntimeError(f"模型呼叫失敗，錯誤訊息：{last_error}")

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
    test_script: str = Field(description="自動化測試或 CLI 執行腳本內容，需完整不截斷")
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
                res_harness, used_model = generate_with_fallback(
                    contents=prompt_harness,
                    system_instruction="你是一個資深系統測試工程師與 OpenHarness 架構專家。請根據需求設計完整的測試腳本與驗證邏輯。",
                    response_schema=HarnessTestOutput,
                    temperature=0.2
                )
                
                st.subheader(f"📋 {res_harness.test_title}")
                st.success(f"✅ 測試腳本規劃完成！（成功調用模型：`{used_model}`）")
                
                st.markdown("**自動化 Harness 執行腳本：**")
                # terminal 風格 CSS，解決換行與截斷問題
                cmd_html = f"""
                <div style="background-color: #0e1117; color: #39ff14; padding: 16px; border-radius: 8px; font-family: 'Courier New', Courier, monospace; font-size: 14px; line-height: 1.6; white-space: pre-wrap; word-break: break-all; border: 1px solid #30363d; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);">
{res_harness.test_script}
                </div>
                """
                st.markdown(cmd_html, unsafe_allow_html=True)
                
                st.markdown("<br><b>驗證點與預期結果：</b>", unsafe_allow_html=True)
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
                res, used_model = generate_with_fallback(
                    contents=prompt_flow,
                    system_instruction="你是一個頂級系統架構師，請根據需求生成標準、結構清晰的 Mermaid.js flowchart (TD 或 LR) 語法。",
                    response_schema=FlowchartOutput,
                    temperature=0.2
                )
                
                st.subheader(res.title)
                st.caption(f"使用模型：`{used_model}`")
                st.write(res.description)
                
                # Mermaid 放大、置中與可互動縮放模組
                html_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
                    <style>
                        body {{ margin: 0; padding: 0; background: #fafafa; font-family: sans-serif; overflow: hidden; }}
                        #container {{ width: 100vw; height: 620px; border: 1px solid #dcdcdc; border-radius: 8px; background: #ffffff; display: flex; justify-content: center; align-items: center; position: relative; }}
                        .mermaid {{ width: 100%; height: 100%; text-align: center; }}
                        .hint {{ position: absolute; top: 12px; right: 16px; font-size: 13px; color: #555; background: rgba(240,240,240,0.9); padding: 6px 12px; border-radius: 6px; z-index: 10; border: 1px solid #ccc; pointer-events: none; }}
                    </style>
                </head>
                <body>
                    <div id="container">
                        <div class="hint">🔍 滑鼠滾輪可放大/縮小，按住左鍵拖拽平移</div>
                        <div class="mermaid">
                        {res.mermaid_code}
                        </div>
                    </div>
                    <script>
                        mermaid.initialize({{
                            startOnLoad: true,
                            theme: 'default',
                            flowchart: {{ useMaxWidth: false, htmlLabels: true, curve: 'basis' }}
                        }});
                        
                        setTimeout(() => {{
                            const svg = document.querySelector("#container svg");
                            if (svg) {{
                                svg.style.maxWidth = "none";
                                svg.style.height = "100%";
                                svg.style.width = "100%";
                                const panZoom = svgPanZoom(svg, {{
                                    zoomEnabled: true,
                                    controlIconsEnabled: true,
                                    fit: true,
                                    center: true,
                                    minZoom: 0.8,
                                    maxZoom: 6,
                                    zoomScaleSensitivity: 0.2
                                }});
                                panZoom.zoom(1.25);
                                panZoom.center();
                            }}
                        }}, 700);
                    </script>
                </body>
                </html>
                """
                components.html(html_code, height=650)
                
                with st.expander("檢視原始 Mermaid 語法"):
                    st.code(res.mermaid_code, language="mermaid")
                    
            except Exception as e:
                st.error(f"生成失敗：{e}")

# Tab 3: 3D 模擬生成器
with tab3:
    st.header("🎲 Three.js 3D 互動模擬生成")
    prompt_3d = st.text_area(
        "輸入 3D 場景需求描述：",
        value="創建一個太陽系 3D 模擬，包含中央發光的太陽、繞行的地球，並加入 OrbitControls 旋轉視角與明顯的自轉/公轉動畫。",
        height=100
    )
    
    if st.button("生成 3D 場景", type="primary"):
        with st.spinner("Gemini 正在撰寫 Three.js 程式碼..."):
            try:
                res_3d, used_model = generate_with_fallback(
                    contents=prompt_3d,
                    system_instruction=(
                        "你是一個 Three.js 3D 專家。"
                        "請生成一個包含 CDN 引入 (Three.js + OrbitControls)、點光源/環境光、高質感材質、明顯的 requestAnimationFrame 動態旋轉動畫，"
                        "以及滿版 Canvas 的單一完整 HTML 檔案。"
                    ),
                    response_schema=ThreeJSOutput,
                    temperature=0.4
                )
                
                st.subheader(res_3d.title)
                st.caption(f"使用模型：`{used_model}`")
                st.write(res_3d.summary)
                
                # 渲染 3D HTML
                components.html(res_3d.html_code, height=550)
                st.caption("💡 **3D 操作說明**：按住滑鼠左鍵可拖拽旋轉視角，滑鼠滾輪拉近/拉遠，按住右鍵拖拽可平移畫面。")
                
            except Exception as e:
                st.error(f"生成失敗：{e}")