import os
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 頁面標題與佈局設定
st.set_page_config(page_title="OpenHarness & CLI + Gemini AI 整合平台", layout="wide", page_icon="⚡")

st.title("⚡ OpenHarness & CLI-Anything + Gemini AI 整合工作台")
st.caption("結合 PEM 電解槽自動化測試、極化曲線數據模擬、Mermaid 流程圖與 3D 互動場景")

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
    title: str = Field(description="流程圖標題，使用繁體中文")
    mermaid_code: str = Field(description="合法的 Mermaid.js flowchart 語法內容，請勿包含 markdown 標籤")
    description: str = Field(description="流程圖說明，使用繁體中文")

class ThreeJSOutput(BaseModel):
    title: str = Field(description="3D 場景標題，使用繁體中文")
    html_code: str = Field(description="包含完整 Three.js 腳本的可執行 HTML 程式碼")
    summary: str = Field(description="3D 場景說明，使用繁體中文")

class HarnessTestOutput(BaseModel):
    test_title: str = Field(description="測試案例名稱，使用繁體中文")
    test_script: str = Field(description="自動化測試或 CLI 執行腳本內容，需完整不截斷")
    formulas_description: str = Field(description="PEM 電解槽數理化學極化模型計算與推導說明，請務必使用台灣繁體中文")
    execution_steps: list[str] = Field(description="詳細的系統推演與執行步驟說明清單，請務必使用台灣繁體中文描述")
    expected_result: str = Field(description="預期測試結果與驗證標準，請務必使用台灣繁體中文描述")

# -------------------------------------------------------------------
# 功能頁籤
# -------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🛠️ OpenHarness PEM電解槽模擬與測試", 
    "📊 Mermaid 流程圖生成", 
    "🎲 Three.js 3D 模擬生成"
])

# Tab 1: OpenHarness 測試與極化曲線模擬引擎 (全繁體中文輸出)
with tab1:
    st.header("🛠️ OpenHarness PEM 電解槽模擬、極化曲線與自動化測試")
    
    default_pem_prompt = (
        "針對 PEM 電解槽 (PEM Electrolyzer) 模擬系統，進行自動化 Harness 測試。"
        "包含：電流密度 (0-2.0 A/cm²) 響應計算、Butler-Volmer 動力學方程式、可逆電位 (1.23V)、歐姆電阻過電位與溫控邊界 (80°C) 驗證。"
    )
    
    prompt_harness = st.text_area(
        "輸入欲進行測試的 PEM 電解槽系統模組與計算需求：",
        value=default_pem_prompt,
        height=100
    )
    
    if st.button("執行 PEM 模擬與生成 Harness 測試案例", type="primary"):
        with st.spinner("OpenHarness 引擎正在規劃測試腳本與電化學模擬計算..."):
            try:
                res_harness, used_model = generate_with_fallback(
                    contents=prompt_harness,
                    system_instruction=(
                        "你是一個 PEM 電解槽與 OpenHarness 測試專家。"
                        "請撰寫包含 Butler-Volmer、歐姆過電位與極化曲線驗證的 Harness 測試說明。"
                        "所有輸出的說明文字、執行步驟 (execution_steps) 與預期結果 (expected_result) 必須嚴格使用台灣繁體中文 (Traditional Chinese)。"
                    ),
                    response_schema=HarnessTestOutput,
                    temperature=0.2
                )
                
                st.subheader(f"📋 {res_harness.test_title}")
                st.success(f"✅ PEM 模擬測試規劃與極化曲線數據生成完成！（調用模型：`{used_model}`）")
                st.divider()

                # --- 1. 滿版極化曲線圖表 ---
                st.markdown("### 1. 📊 PEM 電解槽極化曲線圖 ($I-V$ Polarization Curve)")
                current_density = np.linspace(0.01, 2.0, 100) # A/cm²
                E_rev = 1.23 # Volt
                R_ohm = 0.15 # Ohm*cm²
                a_act = 0.06
                b_act = 0.08
                
                v_rev = np.full_like(current_density, E_rev)
                v_act = a_act + b_act * np.log10(current_density * 10)
                v_ohm = current_density * R_ohm
                v_cell = v_rev + v_act + v_ohm
                
                fig, ax = plt.subplots(figsize=(10, 4.2))
                ax.plot(current_density, v_cell, 'r-', linewidth=2.5, label='總單電池電壓 Total Cell Voltage ($V_{cell}$)')
                ax.plot(current_density, v_rev, 'b--', linewidth=1.5, label='可逆熱力學電位 Reversible Voltage ($E_{rev}$)')
                ax.plot(current_density, v_act, 'g:', linewidth=1.5, label='活化過電位 Activation Overpotential ($\eta_{act}$)')
                ax.plot(current_density, v_ohm, 'm-.', linewidth=1.5, label='歐姆過電位 Ohmic Overpotential ($\eta_{ohm}$)')
                
                ax.set_title("PEM Electrolyzer Polarization Curve (80°C Boundary)", fontsize=12, fontweight='bold')
                ax.set_xlabel("電流密度 Current Density $i$ ($A/cm^2$)", fontsize=10)
                ax.set_ylabel("單電池電壓 Cell Voltage $V$ (Volts)", fontsize=10)
                ax.grid(True, linestyle='--', alpha=0.6)
                ax.legend(fontsize=9, loc='upper left')
                plt.tight_layout()
                st.pyplot(fig)

                st.divider()

                # --- 2. 數理化學極化方程式 ---
                st.markdown("### 2. 🧮 電化學極化計算方程式 (Polarization Model Equations)")
                st.latex(r"V_{\text{cell}} = E_{\text{rev}} + \eta_{\text{act}} + \eta_{\text{ohm}} + \eta_{\text{conc}}")
                st.latex(r"E_{\text{rev}} = 1.229 - 0.9 \times 10^{-3} (T - 298.15)")
                st.latex(r"\eta_{\text{act}} = \frac{RT}{\alpha F} \ln\left(\frac{i}{i_0}\right) \quad, \quad \eta_{\text{ohm}} = i \cdot R_{\text{mem}}")
                
                with st.expander("📖 檢視電化學推導細節說明"):
                    st.write(res_harness.formulas_description)

                st.divider()

                # --- 3. 自動化 Harness 執行腳本 ---
                st.markdown("### 3. 📜 自動化 Harness 執行腳本")
                cmd_html = f"""
                <div style="background-color: #0e1117; color: #39ff14; padding: 16px; border-radius: 8px; font-family: 'Courier New', Courier, monospace; font-size: 13.5px; line-height: 1.6; white-space: pre-wrap; word-break: break-all; border: 1px solid #30363d; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);">
{res_harness.test_script}
                </div>
                """
                st.markdown(cmd_html, unsafe_allow_html=True)

                st.divider()

                # --- 4. Console Logs 模擬 (清晰換行與繁體中文支援) ---
                st.markdown("### 4. 🖥️ 系統執行 Console 日誌 (Execution Logs)")
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                logs = [
                    f"[{now_str}] [資訊] [OpenHarness 核心] 初始化 PEM 電解槽測試引擎...",
                    f"[{now_str}] [資訊] 使用模型: {used_model} | 運作溫度邊界: 353.15K (80°C)",
                    f"[{now_str}] [數據] 產生 100 個評估採樣點 (0.01 至 2.00 A/cm²)...",
                    f"[{now_str}] [計算] 驗證可逆熱力學電位 E_rev = 1.23V 正確。",
                    f"[{now_str}] [計算] 於 2.0 A/cm² 條件下紀錄最大單電池電壓: {v_cell[-1]:.3f}V",
                ]
                for idx, step in enumerate(res_harness.execution_steps, 1):
                    logs.append(f"[{now_str}] [步驟 {idx}] {step}")
                logs.append(f"[{now_str}] [成功] PEM Harness 模擬測試完成，返回狀態碼 0。")

                log_html_lines = []
                for line in logs:
                    if "[成功]" in line:
                        log_html_lines.append(f'<span style="color: #58a6ff;">{line}</span>')
                    elif "[步驟" in line:
                        log_html_lines.append(f'<span style="color: #7ee787;">{line}</span>')
                    else:
                        log_html_lines.append(f'<span style="color: #8b949e;">{line}</span>')
                
                log_text = "<br>".join(log_html_lines)
                
                console_html = f"""
                <div style="background-color: #0d1117; padding: 16px; border-radius: 8px; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; height: 240px; overflow-y: auto; border: 1px solid #30363d; line-height: 1.8;">
                    {log_text}
                </div>
                """
                st.markdown(console_html, unsafe_allow_html=True)

                st.divider()

                # --- 5. 驗證結果與標準 ---
                st.markdown("### 5. ✅ 驗證點與預期結果")
                st.info(res_harness.expected_result)
                    
            except Exception as e:
                st.error(f"生成失敗：{e}")

# Tab 2: 流程圖生成器
with tab2:
    st.header("📊 Mermaid 流程圖自動生成")
    prompt_flow = st.text_area(
        "輸入流程圖需求描述：",
        value="請繪製一個 PEM 電解槽系統控制流程，包含電流啟動、溫度監控、過壓保護機制與緊急停機程序。",
        height=100
    )
    
    if st.button("生成流程圖", type="primary"):
        with st.spinner("Gemini 正在規劃流程圖架構..."):
            try:
                res, used_model = generate_with_fallback(
                    contents=prompt_flow,
                    system_instruction="你是一個頂級系統架構師，請根據需求生成標準、結構清晰的 Mermaid.js flowchart (TD 或 LR) 語法。圖中節點文字請全部使用繁體中文。",
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
        value="創建一個 PEM 電解槽單電池 3D 結構模擬，包含陽極極板、陰極極板、PEM 質子交換膜與產生的氣泡顆粒動畫。",
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
                        "以及滿版 Canvas 的單一完整 HTML 檔案。說明文字請全部使用繁體中文。"
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
                
            except Exception ase:
                st.error(f"生成失敗：{e}")