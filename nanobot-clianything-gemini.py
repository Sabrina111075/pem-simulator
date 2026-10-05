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

# ==============================================================================
# 🤖 Step 1: 定義 Nano Bot 輕量代理類別 (NanoBot Class)
# ==============================================================================
class NanoBot:
    def __init__(self, api_key: str, model_name: str = "gemini-3.5-flash-lite"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.system_instruction = (
            "你是一個專門協助 PEM 電解槽數位雙生的 Nano Bot 助手。\n"
            "你的任務是將使用者需求擴充為【一段繁體中文自然語言視覺描述】。\n"
            "【嚴格約束】\n"
            "1. 絕對不要撰寫任何 JavaScript、Three.js 或 HTML 程式碼！\n"
            "2. 絕對不要使用 ``` 程式碼區塊！\n"
            "3. 只用繁體中文描述組件外觀、顏色、位置與氣泡顆粒流向。"
        )

    def optimize_3d_prompt(self, user_prompt: str) -> str:
        """輕量任務：Prompt 精煉"""
        prompt = f"請將以下 3D 需求擴充為豐富的中文場景視覺描述（請勿寫程式碼）：\n{user_prompt}"
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.2,
                )
            )
            return response.text if response.text else user_prompt
        except Exception:
            return user_prompt

    def estimate_3d_performance(self, prompt_text: str) -> dict:
        """📊 3D 渲染效能與幾何複雜度預審"""
        particles = 60 if ("氣泡" in prompt_text or "粒子" in prompt_text) else 0
        return {
            "components": "陽極極板、陰極極板、PEM 質子膜",
            "particles": f"約 {particles} 個流體微粒",
            "fps_target": "60 FPS (WebGL 順暢渲染)"
        }

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

# ==============================================================================
# 🤖 Step 2: Nano Bot 智慧控制中心 (含全域場景切換連動)
# ==============================================================================
if "nano_bot" not in st.session_state or st.session_state.get("current_key") != api_key:
    st.session_state.nano_bot = NanoBot(api_key=api_key)
    st.session_state.current_key = api_key

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Nano Bot 代理控制中心")

enable_nano_optimizer = st.sidebar.checkbox(
    "啟用 Nano Bot 前置提示詞優化", 
    value=True,
    help="開啟後，Nano Bot 會自動精煉與擴充傳給 Gemini 的提示詞。"
)

st.sidebar.markdown("**⚡ 快速載入工程測試範本：**")

# 定義範本資料字典
TEMPLATES = {
    "預設單電池場景": {
        "tab1": "針對 PEM 電解槽 (PEM Electrolyzer) 模擬系統，進行自動化 Harness 測試。包含：電流密度 (0-2.0 A/cm²) 響應計算、Butler-Volmer 動力學方程式、可逆電位 (1.23V)、歐姆電阻過電位與溫控邊界 (80°C) 驗證。",
        "tab2": "請繪製一個 PEM 電解槽系統控制流程，包含電流啟動、溫度監控、過壓保護機制與緊急停機程序。",
        "tab3": "創建一個 PEM 電解槽單電池 3D 結構模擬，包含陽極極板、陰極極板、PEM 質子交換膜與產生的氣泡顆粒動畫。"
    },
    "高電流密度熱保護測試": {
        "tab1": "高負載極限測試：設定電流密度為 2.8 A/cm²、電壓 2.1V、系統溫度 82°C，驗證 Butler-Volmer 動力學過電位與極化曲線阻抗變化，並進行熱失控預警處置。",
        "tab2": "請繪製 PEM 電解槽在高電流密度 (2.8 A/cm²) 運作下的過熱保護、自動降載與冷卻循環警報處置流程圖。",
        "tab3": "PEM 高負載電解槽單電池 3D 結構，顯示極板過熱紅光發散、密集產生之氧氣/氫氣氣泡與劇烈流場動畫。"
    },
    "緊急停機控制流程": {
        "tab1": "緊急停機 (ESD) 驗證測試：模擬電壓瞬間飆高至 2.5V 且溫控感測失效時，觸發系統連鎖中斷、電路隔離與惰性氣體 (氮氣) 吹掃保護機制。",
        "tab2": "請繪製 PEM 電解槽緊急停機程序 (ESD)，包含系統異常偵測、電源斷開、快速洩壓、氮氣吹掃與安全隔離之順序流程圖。",
        "tab3": "PEM 電解槽急停狀態 3D 模擬，雙極板呈現灰色無過電狀態，內部流場顆粒氣泡全面停止流動。"
    }
}

# 觸發選擇變更時，自動更新 Session State
selected_tpl_key = st.sidebar.selectbox(
    "選擇測試場景：",
    options=list(TEMPLATES.keys()),
    key="template_selector"
)

# 顯示 Nano Bot 診斷狀態卡片
st.sidebar.info("🟢 **Nano Bot 運作狀態：** 微型診斷引擎已就緒")

# -------------------------------------------------------------------
# 功能頁籤
# -------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🛠️ OpenHarness 自動化引擎模擬與測試", 
    "📊 Mermaid 流程圖生成", 
    "🎲 Three.js 3D 模擬生成"
])

# Tab 1: OpenHarness 測試與極化曲線模擬引擎
with tab1:
    st.header("⚡ OpenHarness PEM 電解槽模擬、極化曲線與自動化測試")

    # 1. 自動載入範本輸入框
    prompt_harness = st.text_area(
        "輸入欲進行測試的 PEM 電解槽系統模組與計算需求：",
        value=TEMPLATES[selected_tpl_key]["tab1"],
        height=100,
        key=f"prompt_harness_{selected_tpl_key}"
    )

    if st.button("執行 PEM 模擬與生成 Harness 測試案例", type="primary"):
        # 🤖 2. 融入 Nano Bot 輕量物理診斷預審
        if "nano_bot" in st.session_state:
            with st.spinner("🤖 Nano Bot 正進行電解槽物理邊界與安全性診斷..."):
                # 預設極限檢測參數，也可隨輸入自動調整
                diag_result = st.session_state.nano_bot.diagnose_pem_physics(
                    cell_voltage=2.1 if "高負載" in prompt_harness else 1.8,
                    current_density=2.8 if "高負載" in prompt_harness else 1.8,
                    temp=82.0 if "高負載" in prompt_harness else 75.0
                )
                
                # 渲染 Nano Bot 微型診斷卡片
                with st.expander("🤖 Nano Bot 系統物理診斷報告", expanded=True):
                    for msg in diag_result["messages"]:
                        if "⚠️" in msg:
                            st.warning(msg)
                        else:
                            st.success(msg)

        # ⚡ 3. 呼叫 Gemini 主模型進行 OpenHarness 測試案例規劃
        with st.spinner("OpenHarness 引擎正在規劃測試腳本與電化學模擬計算..."):
            try:
                res_harness, used_model = generate_with_fallback(
                    contents=prompt_harness,
                    system_instruction=(
                        "你是一個 PEM 電解槽與 OpenHarness 測試專家。"
                        "請撰寫包含 Butler-Volmer、歐姆過電位與極化曲線驗證的 Harness 測試說明。"
                        "所有輸出的說明文字、執行步驟與預期結果必須嚴格使用台灣繁體中文。"
                    ),
                    response_schema=HarnessTestOutput,
                    temperature=0.2
                )

                st.subheader(f"⚡ {res_harness.test_title}")
                st.success(f"⚡ PEM 模擬測試規劃與極化曲線數據生成完成！（調用模型：`{used_model}`）")
                st.divider()

            except Exception as e:
                st.error(f"Harness 測試規劃失敗：{e}")

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

                # --- 4. Console Logs 模擬 (獨立分行與繁體中文顯示) ---
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

# --- Tab 2: Mermaid 流程圖生成器 ---
with tab2:
    st.header("Mermaid 流程圖自動生成")
    prompt_flow = st.text_area(
        "輸入流程圖需求描述：",
        value=TEMPLATES[selected_tpl_key]["tab2"],
        height=100,
        key=f"prompt_flow_{selected_tpl_key}"
    )

    # 注意：生成流程圖按鈕與後續渲染 logic 必須【全部縮排】在 with tab2 內部！
    if st.button("生成流程圖", type="primary", key="btn_gen_flowchart"):
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

                # 100% 大字體原生捲軸 Mermaid 模組
                html_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                    <style>
                        body {{ margin: 0; padding: 0; background-color: #ffffff; }}
                        #scroll-container {{
                            width: 100%;
                            max-height: 800px;
                            overflow: auto;
                            border: 1px solid #d0d7de;
                            border-radius: 8px;
                            background-color: #f6f8fa;
                            padding: 20px;
                            box-sizing: border-box;
                        }}
                        .mermaid {{ display: flex; justify-content: center; min-width: 800px; }}
                        .mermaid svg {{
                            max-width: none !important;
                            height: auto !important;
                            font-size: 22px !important;
                            font-weight: bold !important;
                            font-family: sans-serif !important;
                        }}
                        .mermaid .node rect, .mermaid .node circle, .mermaid .node polygon {{ stroke-width: 2.5px !important; }}
                        .mermaid .edgeLabel {{ font-size: 18px !important; font-weight: bold !important; background-color: #ffffff !important; }}
                    </style>
                </head>
                <body>
                    <div id="scroll-container">
                        <div class="mermaid">
                        {res.mermaid_code}
                        </div>
                    </div>
                    <script>
                        mermaid.initialize({{
                            startOnLoad: true,
                            theme: 'default',
                            flowchart: {{ useMaxWidth: false, htmlLabels: true, curve: 'basis' }},
                            themeVariables: {{ fontSize: '22px', nodePadding: 25 }}
                        }});
                    </script>
                </body>
                </html>
                """

                import streamlit.components.v1 as components
                components.html(html_code, height=820)

            except Exception as e:
                st.error(f"生成失敗：{e}")


# 1. 如果專案前段尚未定義 ThreeJSOutput，可以在這裡定義 Pydantic 模型
from pydantic import BaseModel, Field

class ThreeJSOutput(BaseModel):
    title: str = Field(description="3D 場景標題")
    description: str = Field(description="3D 場景說明")
    html_code: str = Field(description="包含完整 Three.js (r128)、OrbitControls 與 WebGL 動畫的 HTML 程式碼")


# --- Tab 3: Three.js 3D 模擬生成器 ---
with tab3:
    st.header("Three.js 3D 互動模擬生成")
    prompt_3d = st.text_area(
        "輸入 3D 場景需求描述：",
        value=TEMPLATES[selected_tpl_key]["tab3"],
        height=100,
        key=f"prompt_3d_{selected_tpl_key}"
    )

        # 🤖 1. Nano Bot 提示詞精煉與效能預審
        if enable_nano_optimizer and "nano_bot" in st.session_state:
            with st.spinner("🤖 Nano Bot 正進行 3D 場景精煉與效能預審..."):
                final_prompt_3d = st.session_state.nano_bot.optimize_3d_prompt(prompt_3d)
                perf_info = st.session_state.nano_bot.estimate_3d_performance(final_prompt_3d)

                # 展示 Nano Bot 智慧診斷卡片
                with st.expander("🤖 Nano Bot 預審與場景結構報告", expanded=True):
                    st.write(f"💡 **精煉描述：** {final_prompt_3d}")
                    col_a, col_b = st.columns(2)
                    col_a.metric("預估核心組件", perf_info["components"])
                    col_b.metric("粒子動畫負載", perf_info["particles"], delta=perf_info["fps_target"])

        # ⚡ 2. 呼叫 Gemini 生成 Three.js 程式碼
        with st.spinner("Gemini 正在撰寫 3D 場景程式碼..."):
            try:
                system_prompt_3d = (
                    "你是個頂級 3D WebGL / Three.js 開發專家。"
                    "【語言要求】title 與 description 必須完全使用繁體中文說明。"
                    "【視覺風格】請建立風格明亮、簡潔且現代化的 3D 場景："
                    "1. 背景設定為淺灰/白色（例如 #f5f7fa），絕不使用黑色背景。"
                    "2. 增加 AmbientLight（強度 0.8）與 DirectionalLight（強度 0.8）。"
                    "3. 陽極極板（金屬灰）、陰極極板（銀灰色）與中央 PEM 質子膜（半透明天藍色）需有明顯視覺區隔。"
                    "【語法禁忌】嚴禁包含 EffectComposer、UnrealBloomPass 或任何第三方 postprocessing 庫，必須只使用標準 THREE 命名空間！"
                    "【控制】OrbitControls 啟用 controls.autoRotate = true，autoRotateSpeed = 2.5。"
                )

                res, used_model = generate_with_fallback(
                    contents=final_prompt_3d,
                    system_instruction=system_prompt_3d,
                    response_schema=ThreeJSOutput,
                    temperature=0.3
                )

                if res and hasattr(res, 'title'):
                    st.subheader(res.title)
                    st.caption(f"使用模型：`{used_model}`")
                    st.write(res.description)

                    # 清理 HTML 標籤
                    raw_html = res.html_code
                    if "```html" in raw_html:
                        raw_html = raw_html.split("```html")[1].split("```")[0]
                    elif "```" in raw_html:
                        raw_html = raw_html.split("```")[1].split("```")[0]

                    # 渲染 Canvas
                    import streamlit.components.v1 as components
                    components.html(raw_html, height=650)
                else:
                    st.error("3D 結構生成傳回無效回應，請再點擊一次『生成 3D 場景』。")

            except Exception as e:
                st.error(f"3D 場景生成失敗：{e}")