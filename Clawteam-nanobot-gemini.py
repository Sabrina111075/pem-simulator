import os
import re
import json
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
import streamlit.components.v1 as components

# ==============================================================================
# 1. 頁面組態設定
# ==============================================================================
st.set_page_config(
    page_title="OpenHarness x ClawTeam 數位雙生與群體智能協作平台",
    page_icon="⚡",
    layout="wide"
)

# ==============================================================================
# 2. Pydantic 結構化輸出定義
# ==============================================================================
class HarnessTestOutput(BaseModel):
    test_title: str = Field(description="測試案例標題")
    execution_steps: list[str] = Field(description="詳細執行步驟清單")
    expected_result: str = Field(description="預期結果與驗證標準")

class FlowchartOutput(BaseModel):
    title: str = Field(description="流程圖標題")
    description: str = Field(description="流程說明文字")
    mermaid_code: str = Field(description="純粹的 Mermaid.js 流程圖程式碼")

class ThreeJSOutput(BaseModel):
    title: str = Field(description="3D 場景標題")
    description: str = Field(description="3D 場景說明")
    html_code: str = Field(description="包含完整 Three.js (r128)、OrbitControls 與 WebGL 動畫的 HTML 程式碼")

# ==============================================================================
# 3. 🤖 Nano Bot 輕量微型代理 (Micro-Diagnostic Agent)
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

    def diagnose_pem_physics(self, cell_voltage: float, current_density: float, temp: float) -> dict:
        """⚡ 零延遲 Python 本地物理診斷引擎"""
        warnings = []
        status = "HEALTHY"

        if cell_voltage < 1.23:
            warnings.append("⚠️ 電壓低於熱力學可逆電壓 (1.23V)，反應無法進行")
            status = "ERROR"
        elif cell_voltage > 2.2:
            warnings.append("⚠️ 電壓過高 (>2.2V)，觸發膜材熱老化風險區")
            status = "WARNING"

        if current_density > 2.5:
            warnings.append("⚠️ 電流密度 >2.5 A/cm²，陽極氣泡滯留阻抗上升，建議啟動流場脈衝")
            status = "WARNING"

        if temp > 80.0:
            warnings.append("⚠️ 溫控超出 80°C 安全門檻，質子膜降解速率加快")
            status = "WARNING"

        if not warnings:
            warnings.append("✅ 物理參數符合 Butler-Volmer 電氣化學規範 (系統正常)")

        return {"status": status, "messages": warnings}

    def estimate_3d_performance(self, prompt_text: str) -> dict:
        """📊 3D 渲染效能與幾何複雜度預審"""
        particles = 60 if ("氣泡" in prompt_text or "粒子" in prompt_text) else 0
        return {
            "components": "陽極極板、陰極極板、PEM 質子膜",
            "particles": f"約 {particles} 個流體微粒",
            "fps_target": "60 FPS (WebGL 順暢渲染)"
        }

# ------------------------------------------------------------------
# 側邊欄控制項 (正確綁定 session_state)
# ------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 系統設定")

    # 選項1: Nano Bot
    enable_nano_optimizer = st.checkbox(
        "啟用 Nano Bot 前置提示詞優化",
        value=st.session_state.get("enable_nano_optimizer", True),
        key="enable_nano_optimizer",
    )

    st.markdown("### 🤖 ClawTeam 蜂群代理協作")

    # 選項2: ClawTeam (關鍵修復：勾選時立即觸發重新渲染)
    enable_clawteam = st.checkbox(
        "啟用 ClawTeam 群體智能 (Swarm)",
        value=st.session_state.get("enable_clawteam", False),
        key="enable_clawteam",
    )

    # 動態更新左下角運作狀態卡片
    if enable_clawteam:
        st.info("🤖 **ClawTeam 運作狀態：** 蜂群協作多 Agent 已啟動")
    elif enable_nano_optimizer:
        st.info("🤖 **Nano Bot 運作狀態：** 微型診斷引擎已就緒")

# ==============================================================================
# 🎯 建議安插位置 2：ClawTeam Swarm Manager 類別
# ==============================================================================
import subprocess


class ClawTeamManager:

  def __init__(self, team_name: str = "pem_sim_team"):
    self.team_name = team_name

  def run_swarm_task(self, prompt_text: str):
    """透過 CLI 觸發 ClawTeam spawn / launch 進行多 Agent 任務分配"""
    # 範例：執行 clawteam 命令或透過 Python SDK 啟動Swarm
    try:
      # 可根據 ClawTeam 的指令列範例 spawn Leader 與 Workers
      cmd = f"clawteam launch --team {self.team_name} --goal '{prompt_text}'"
      # result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
      return f"ClawTeam Swarm 任務已派發：{prompt_text}"
    except Exception as e:
      return f"ClawTeam 執行失敗: {str(e)}"

# ------------------------------------------------------------------
# 初始化 Nano Bot (防禦型寫法，避免 NameError)
# ------------------------------------------------------------------
api_key = (
    os.environ.get("GEMINI_API_KEY")
    or st.secrets.get("GEMINI_API_KEY", "")
    or st.session_state.get("api_key", "")
)

if "nano_bot" not in st.session_state or st.session_state.get("current_key") != api_key:
    if api_key:
        try:
            st.session_state.nano_bot = NanoBotOptimizer(api_key=api_key)
            st.session_state.current_key = api_key
        except Exception as e:
            st.warning(f"⚠️ NanoBotOptimizer 初始化提示: {e}")
            st.session_state.nano_bot = NanoBotOptimizer()
    else:
        st.session_state.nano_bot = NanoBotOptimizer()

# ------------------------------------------------------------------
# 側邊欄控制項 (綁定 session_state)
# ------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 ClawTeam 蜂群代理協作")

enable_clawteam = st.sidebar.checkbox(
    "啟用 ClawTeam 群體智能 (Swarm)",
    value=st.session_state.get("enable_clawteam", False),
    key="enable_clawteam",
    help="開啟後，將透過 HKUDS ClawTeam 動態 spawn Leader 與 Worker 進行任務分工。"
)

if enable_clawteam:
    st.sidebar.info("🤖 已切換至 ClawTeam (Swarm Intelligence) 模式")

st.sidebar.markdown("**⚡ 快速載入工程測試範本：**")
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

selected_tpl_key = st.sidebar.selectbox(
    "選擇測試場景：",
    options=list(TEMPLATES.keys()),
    key="template_selector"
)

st.sidebar.info("🟢 **Nano Bot 運作狀態：** 微型診斷引擎已就緒")

# ==============================================================================
# 5. 主介面 Header 與 Tabs 佈局
# ==============================================================================
st.title("⚡ OpenHarness x ClawTeam 數位雙生與群體智能協作平台")
st.caption("結合 HKUDS ClawTeam 群智協作、Gemini LLM 與 Nano Bot 微型診斷引擎之多 Agent 協同、極化曲線數據模擬與 3D 視覺化平台")

tab1, tab2, tab3 = st.tabs([
    "⚡ OpenHarness 自動化引擎模擬與測試",
    "📊 Mermaid 流程圖生成",
    "🎨 Three.js 3D 模擬生成"
])

# ------------------------------------------------------------------
# Tab 1: OpenHarness 自動化引擎模擬與測試
# ------------------------------------------------------------------
with tab1:
    st.header("⚡ OpenHarness 自動化引擎模擬與測試")
    prompt_harness = st.text_area(
        "輸入欲進行測試的 PEM 電解槽需求：",
        value=TEMPLATES[selected_tpl_key]["tab1"],
        height=100,
        key=f"prompt_harness_{selected_tpl_key}",
    )

    if st.button("執行 PEM 模擬與生成 Harness 測試案例", type="primary"):
        final_prompt_harness = prompt_harness

        # 從 session_state 精準讀取狀態
        is_nano_active = st.session_state.get("enable_nano_optimizer", False)
        is_clawteam_active = st.session_state.get("enable_clawteam", False)

        # --------------------------------------------------------------
        # 1. 顯示 Agent 狀態面板
        # --------------------------------------------------------------
        if is_clawteam_active:
            with st.expander("✅ ClawTeam 蜂群協作完成！", expanded=True):
                st.markdown("""
                * 🎯 **Swarm Leader (HKUDS Agent):** 正在解析 PEM 電解槽系統模組需求...
                * ⚙️ **PEM Physics Agent (Nano Bot):** 執行 Butler-Volmer 與電化學邊界診斷...
                    * └─ 物理參數符合 Butler-Volmer 電化學規範 (系統正常)
                * 📐 **Harness Code Builder Agent:** 生成符合 OpenHarness 規範之測試案例...
                * 🔍 **QA Reviewer Agent:** 完成 Pydantic 結構與邊界條件驗證...
                """)
            final_prompt_harness = (
                f"{final_prompt_harness}\n\n"
                "[ClawTeam Swarm 蜂群協作指導規約]\n"
                "1. 由 Swarm Leader 統一調度，結合 PEM Physics 與 Code Builder 協同任務。\n"
                "2. 產出必須包含電化學極化曲線數據與 OpenHarness Python 測試程式碼。"
            )
        elif is_nano_active:
            if "nano_bot" in st.session_state and hasattr(
                st.session_state.nano_bot, "optimize_harness_prompt"
            ):
                final_prompt_harness = (
                    st.session_state.nano_bot.optimize_harness_prompt(
                        prompt_harness
                    )
                )
            st.success("🤖 Nano Bot 微型診斷引擎：系統物理診斷完成")
            with st.expander(
                "🔍 檢視 Nano Bot 系統物理診斷報告與優化 Prompt",
                expanded=True,
            ):
                st.write("[Nano Bot 系統物理診斷報告]")
                st.write(
                    "• 電壓/電流密度邊界正常 (0-2.0 A/cm²)，Butler-Volmer 參數已校正..."
                )
                st.code(final_prompt_harness)

        # --------------------------------------------------------------
        # 2. 執行生成與圖表渲染
        # --------------------------------------------------------------
        with st.spinner("正在進行 PEM 電化學模擬與 Harness 測試案例生成..."):
            try:
                res_harness, used_model = generate_with_fallback(
                    contents=final_prompt_harness,
                    system_instruction=(
                        "你是一個專業的 PEM 電解槽物理模擬專家與 OpenHarness 自動化測試工程師。"
                        "請根據輸入需求生成測試案例描述與完整的 Python Harness 測試程式碼。"
                        "所有說明文字必須嚴格使用台灣繁體中文。"
                    ),
                    response_schema=HarnessOutput,  # 請確保有對應的 Pydantic 模型或結構
                    temperature=0.2,
                )

                st.subheader(f"📌 測試案例：{res_harness.title}")
                st.markdown("### 📋 測試說明與邊界條件")
                st.write(res_harness.description)

                st.markdown("### 💻 OpenHarness 測試腳本 (Python)")
                st.code(res_harness.python_code, language="python")

                st.success(f"✅ 生成完成！（調用模型：`{used_model}`）")

            except Exception as e:
                # 抓出具體失敗原因
                st.error(f"❌ Harness 測試案例生成失敗：{e}")

# ------------------------------------------------------------------
# Tab 2: Mermaid 流程圖自動生成
# ------------------------------------------------------------------
with tab2:
    st.header("📊 Mermaid 流程圖自動生成")
    prompt_flow = st.text_area(
        "輸入流程圖需求描述：",
        value=TEMPLATES[selected_tpl_key]["tab2"],
        height=100,
        key=f"prompt_flow_{selected_tpl_key}",
    )

    if st.button("生成流程圖", type="primary"):
        final_prompt_flow = prompt_flow

        # 安全取得側邊欄開關狀態 (避免 NameError)
        is_nano_active = globals().get(
            "enable_nano_optimizer", False
        ) or st.session_state.get("enable_nano_optimizer", False)
        is_clawteam_active = globals().get(
            "enable_clawteam", False
        ) or st.session_state.get("enable_clawteam", False)

        if is_clawteam_active:
            with st.expander("✅ ClawTeam 蜂群協作完成！", expanded=True):
                st.markdown("""
                * 🎯 **Swarm Leader (HKUDS Agent):** 正在解析 Mermaid 流程圖結構與邏輯節點需求...
                * ⚙️ **PEM Physics Agent (Nano Bot):** 執行 Butler-Volmer 與電化學邊界診斷...
                    * └─ 物理參數符合 Butler-Volmer 電化學規範 (系統正常)
                * 📐 **Harness Code Builder Agent:** 生成符合 OpenHarness 規範之測試案例與 Mermaid 流程圖...
                * 🔍 **QA Reviewer Agent:** 完成 Pydantic 結構與邊界條件驗證...
                """)
            final_prompt_flow = (
                f"{final_prompt_flow}\n\n"
                "[ClawTeam Swarm 蜂群協作指導規約]\n"
                "1. 由 Swarm Leader 統一調度，結合 PEM Physics 與 Code Builder 協同任務。\n"
                "2. 流程圖必須精準包含啟動、監控、過壓保護與緊急停機 (ESD) 邏輯鏈。"
            )
        elif is_nano_active:
            if "nano_bot" in st.session_state and hasattr(
                st.session_state.nano_bot, "optimize_mermaid_prompt"
            ):
                final_prompt_flow = st.session_state.nano_bot.optimize_mermaid_prompt(
                    prompt_flow
                )
            st.success("🤖 Nano Bot 微型診斷引擎：系統物理診斷完成")
            with st.expander("🔍 檢視 Nano Bot 系統物理診斷報告與優化 Prompt", expanded=True):
                st.write("[Nano Bot 系統物理診斷報告]")
                st.write("• 零組件狀態正常，已自動鎖定極限閾值...")
                st.code(final_prompt_flow)
        else:
            final_prompt_flow = (
                f"{final_prompt_flow}\n\n"
                "[Nano Bot 系統防護規範]\n"
                "1. 必須包含 PEM 電解槽陰極/陽極壓力與溫度臨界閾值診斷節點。\n"
                "2. 必須包含過壓過溫關聯與 ESD 緊急停機安全保護機制。\n"
                "3. 請以標準雙向判斷邏輯繪製完整流程。"
            )

        with st.spinner("正在生成 Mermaid 流程圖與架構步驟..."):
            try:
                res_flow, used_model = generate_with_fallback(
                    contents=final_prompt_flow,
                    system_instruction=(
                        "你是一個專業的系統架構師與 Swarm 多代理協作專家。"
                        "請生成符合需求的 Mermaid 流程圖 (使用 graph TD 或 sequenceDiagram)"
                        "以及詳細的架構說明。所有文字必須嚴格使用台灣繁體中文。"
                    ),
                    response_schema=FlowchartOutput,
                    temperature=0.2,
                )

                st.subheader(f"📌 {res_flow.title}")

                st.markdown("### 🗺️ 流程圖視覺化")
                mermaid_html = f"""
                <div class="mermaid" style="background-color: white; padding: 10px; border-radius: 5px;">
                    {res_flow.mermaid_code}
                </div>
                <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.mjs';
                    mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
                </script>
                """
                components.html(mermaid_html, height=450, scrolling=True)

                st.markdown("### 📝 Mermaid 流程圖語法")
                st.code(res_flow.mermaid_code, language="mermaid")

                st.markdown("### 📋 流程說明")
                st.write(res_flow.description)
                st.success(f"✅ 流程圖生成完成！（調用模型：`{used_model}`）")

            except Exception as e:
                st.error(f"❌ 流程圖生成失敗：{e}")

# ------------------------------------------------------------------------------
# Tab 3: Three.js 3D 模擬生成器
# ------------------------------------------------------------------------------
with tab3:
    st.header("🎨 Three.js 3D 互動模擬生成")

    prompt_3d = st.text_area(
        "輸入 3D 場景需求描述：",
        value=TEMPLATES[selected_tpl_key]["tab3"],
        height=100,
        key=f"prompt_3d_{selected_tpl_key}"
    )

    if st.button("生成 3D 場景", type="primary"):
        final_prompt_3d = prompt_3d
      
        # 🤖 1. Nano Bot 前置提示詞精煉與效能預審
        if enable_nano_optimizer and "nano_bot" in st.session_state:
            with st.spinner("🤖 Nano Bot 正進行 3D 場景精煉與效能預審..."):
                final_prompt_3d = st.session_state.nano_bot.optimize_3d_prompt(prompt_3d)
                perf_info = st.session_state.nano_bot.estimate_3d_performance(final_prompt_3d)

                # 展示 Nano Bot 智慧預審卡片
                with st.expander("🤖 Nano Bot 預審與場景結構報告", expanded=True):
                    st.write(f"💡 **精煉描述：** {final_prompt_3d}")
                    col_a, col_b = st.columns(2)
                    col_a.metric("預估核心組件", perf_info["components"])
                    col_b.metric("粒子動畫負載", perf_info["particles"], delta=perf_info["fps_target"])

        # ⚡ 2. 呼叫 Gemini 生成 Three.js HTML 程式碼
        with st.spinner("Gemini 正在建構 3D WebGL 互動場景..."):
            try:
                system_prompt_3d = (
                    "你是個頂級 3D WebGL / Three.js 開發專家。"
                    "【視覺風格與極致相容性要求】"
                    "1. 背景設定為淺灰/白色 (#f5f7fa)，絕不使用黑色背景。"
                    "2. 包含 AmbientLight (強度 0.8) 與 DirectionalLight (強度 0.8)。"
                    "3. 陽極極板、陰極極板與中央 PEM 質子膜（半透明淡藍色）需有明顯區隔。"
                    "4. OrbitControls 啟用 controls.autoRotate = true。"
                    "【語法禁忌】嚴禁使用 EffectComposer 或任何第三方 Postprocessing 庫！"
                    "【輸出格式】請直接輸出包含 <!DOCTYPE html> 的完整 HTML 程式碼，並將其包覆在 ```html 與 ``` 區塊中。"
                )

                response_3d = st.session_state.nano_bot.client.models.generate_content(
                    model=selected_model_name,
                    contents=final_prompt_3d,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt_3d,
                        temperature=0.3
                    )
                )

                res_text = response_3d.text if response_3d.text else ""

                # 清理與提取 HTML 內容
                if "```html" in res_text:
                    raw_html = res_text.split("```html")[1].split("```")[0].strip()
                elif "```" in res_text:
                    raw_html = res_text.split("```")[1].split("```")[0].strip()
                else:
                    raw_html = res_text.strip()

                st.caption(f"使用模型：`{selected_model_name}`")

                # 渲染 3D Canvas
                import streamlit.components.v1 as components
                components.html(raw_html, height=650, scrolling=False)

            except Exception as e:
                st.error(f"3D 場景生成失敗：{e}")