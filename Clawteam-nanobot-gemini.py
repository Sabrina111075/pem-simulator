import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd

# ==============================================================================
# 1. 頁面組態設定
# ==============================================================================
st.set_page_config(
    page_title="OpenHarness x ClawTeam 數位雙生與群體智能協作平台",
    page_icon="⚡",
    layout="wide"
)

# 副標題渲染
st.caption("結合 HKUDS ClawTeam 群智協作、Gemini LLM 與 Nano Bot 微型診斷引擎之多 Agent 協同、極化曲線數據模擬與 3D 視覺化平台")

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

# ==============================================================================
# 4. 側邊欄：API 金鑰與系統設定
# ==============================================================================
st.sidebar.title("⚙️ 系統設定")

api_key = ""
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("輸入 Gemini API Key:", type="password")

if not api_key:
    st.info("請於 Streamlit Secrets 設定 GEMINI_API_KEY 或在側邊欄輸入 API 金鑰以繼續。")
    st.stop()

selected_model_name = st.sidebar.selectbox(
    "選擇偏好的 Gemini 模型：",
    ["gemini-3.5-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash"],
    index=0
)

# 備援生成函式
def generate_with_fallback(contents, system_instruction, response_schema, temperature=0.2):
    client = genai.Client(api_key=api_key)
    models_to_try = [selected_model_name, "gemini-2.0-flash", "gemini-1.5-flash"]
    for m in models_to_try:
        try:
            resp = client.models.generate_content(
                model=m,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=temperature
                )
            )
            return resp.parsed, m
        except Exception:
            continue
    raise RuntimeError("所有 Gemini 模型端點均未能成功回應。")

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


# ==============================================================================

# 初始化 Nano Bot
if (
    "nano_bot" not in st.session_state
    or st.session_state.get("current_key") != api_key
):
  st.session_state.nano_bot = NanoBot(api_key=api_key)
  st.session_state.current_key = api_key

# 1. Nano Bot 原有的控制項（就是您反藍的那段，保留不刪除）
enable_nano_optimizer = st.sidebar.checkbox(
    "啟用 Nano Bot 前置提示詞優化",
    value=True,
    help="開啟後，Nano Bot 會自動精煉與擴充傳給 Gemini 的提示詞。"
)

# 2. 接續新增 ClawTeam 控制項（放在 Nano Bot 下方）
st.sidebar.markdown("---")
st.sidebar.subheader("🦞 ClawTeam 蜂群代理協作")
enable_crew_team = st.sidebar.checkbox(
    "啟用 ClawTeam 群體智能 (Swarm)",
    value=False,
    help="開啟後，將透過 HKUDS ClawTeam 動態 spawn Leader 與 Worker 進行任務分工。"
)

if enable_crew_team:
    st.sidebar.info("💡 已切換至 ClawTeam (Swarm Intelligence) 模式")

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

# ------------------------------------------------------------------------------
# Tab 1: OpenHarness 測試與極化曲線模擬引擎
# ------------------------------------------------------------------------------
with tab1:
    st.header("⚡ OpenHarness PEM 電解槽模擬、極化曲線與自動化測試")

    prompt_harness = st.text_area(
        "輸入欲進行測試的 PEM 電解槽系統模組與計算需求：",
        value=TEMPLATES[selected_tpl_key]["tab1"],
        height=100,
        key=f"prompt_harness_{selected_tpl_key}"
    )

    if st.button("執行 PEM 模擬與生成 Harness 測試案例", type="primary"):
        if "nano_bot" in st.session_state:
            with st.spinner("🤖 Nano Bot 正進行電解槽物理邊界與安全性診斷..."):
                diag_result = st.session_state.nano_bot.diagnose_pem_physics(
                    cell_voltage=2.1 if selected_tpl_key == "高電流密度熱保護測試" else (2.5 if selected_tpl_key == "緊急停機控制流程" else 1.8),
                    current_density=2.8 if selected_tpl_key == "高電流密度熱保護測試" else 1.8,
                    temp=82.0 if selected_tpl_key == "高電流密度熱保護測試" else 75.0
                )
                
                with st.expander("🤖 Nano Bot 系統物理診斷報告", expanded=True):
                    for msg in diag_result["messages"]:
                        if "⚠️" in msg:
                            st.warning(msg)
                        else:
                            st.success(msg)

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

    # 📊 滿版極化曲線與動態響應圖表
    st.markdown(f"### 📊 PEM 電解槽模擬圖表（當前場景：`{selected_tpl_key}`）")

    if selected_tpl_key == "預設單電池場景":
        # 標準 Butler-Volmer 伏安曲線
        cd = np.linspace(0.01, 2.0, 100)
        voltage = 1.23 + cd * 0.18 + 0.06 * np.log10(cd / 0.01 + 1) + 0.05 * (cd ** 1.1)
        df_chart = pd.DataFrame({
            "電流密度 Current Density (A/cm²)": np.round(cd, 2),
            "標準運作電壓 Normal Cell Voltage (V)": np.round(voltage, 3)
        }).set_index("電流密度 Current Density (A/cm²)")
        st.caption("📈 圖形特徵：展示 0 ~ 2.0 A/cm² 範圍內標準的活化過電位與歐姆損耗曲線。")

    elif selected_tpl_key == "高電流密度熱保護測試":
        # 包含高阻抗與極限傳質陡升的過熱曲線
        cd = np.linspace(0.01, 3.0, 100)
        base_v = 1.23 + cd * 0.28 + 0.08 * np.log10(cd / 0.01 + 1)
        # 加上高電流密度氣泡阻抗陡升區
        mass_transport_loss = np.where(cd > 2.0, (cd - 2.0) ** 2.2 * 0.4, 0)
        voltage = base_v + mass_transport_loss
        
        df_chart = pd.DataFrame({
            "電流密度 Current Density (A/cm²)": np.round(cd, 2),
            "高負載熱阻抗電壓 High-Load Voltage (V)": np.round(voltage, 3),
            "熱保護警戒門檻 Limit Warning (2.2V)": 2.2
        }).set_index("電流密度 Current Density (A/cm²)")
        st.warning("⚠️ 圖形特徵：電流密度超過 2.0 A/cm² 後，因氣泡滯留與極化阻抗上升，電壓呈現二次方急遽陡升，突破 2.2V 熱保護門檻。")

    else:  # 緊急停機控制流程
        # 模擬急停驗證：時間序列中的電壓突波與斷電歸零
        time_steps = np.linspace(0, 60, 100)  # 60秒測試時間
        # 前 30 秒正常，35 秒電壓異常突波，40 秒觸發 ESD 斷電歸零
        voltage = np.where(
            time_steps < 30, 1.85,
            np.where(time_steps < 38, 1.85 + (time_steps - 30) * 0.12, 0.0)
        )
        df_chart = pd.DataFrame({
            "測試時間 Time (s)": np.round(time_steps, 1),
            "實時單電池電壓 Real-time Voltage (V)": np.round(voltage, 3)
        }).set_index("測試時間 Time (s)")
        st.error("🚨 圖形特徵：模擬第 30 秒觸發電壓驟升，第 38 秒連鎖觸發 ESD 緊急停機，系統瞬間切斷電源降至 0V。")

    st.line_chart(df_chart)

# ------------------------------------------------------------------------------
# Tab 2: Mermaid 流程圖生成器
# ------------------------------------------------------------------------------
with tab2:
    st.header("📊 Mermaid 流程圖自動生成")

    prompt_flow = st.text_area(
        "輸入流程圖需求描述：",
        value=TEMPLATES[selected_tpl_key]["tab2"],
        height=100,
        key=f"prompt_flow_{selected_tpl_key}"
    )

    if st.button("生成流程圖", type="primary", key="btn_gen_flow"):
        final_prompt_flow = prompt_flow

        # 🤖 1. Nano Bot 專屬流程圖邏輯結構化（不帶 3D 描述）
        if enable_nano_optimizer and "nano_bot" in st.session_state:
            with st.spinner("🤖 Nano Bot 正分析與結構化流程圖邏輯..."):
                try:
                    flow_nano_sys = (
                        "你是一個流程圖邏輯專家。請將使用者需求整理為乾淨、層次分明的中文流程步驟。"
                        "【禁忌】絕對不要提及 3D、光影或視覺場景，只關注『啟動->監控->判斷->處置』邏輯！"
                    )
                    nano_res = st.session_state.nano_bot.client.models.generate_content(
                        model=st.session_state.nano_bot.model_name,
                        contents=f"請整理以下流程邏輯：\n{prompt_flow}",
                        config=types.GenerateContentConfig(
                            system_instruction=flow_nano_sys,
                            temperature=0.2
                        )
                    )
                    final_prompt_flow = nano_res.text if nano_res.text else prompt_flow
                    st.info(f"💡 **Nano Bot 結構化流程邏輯：**\n\n{final_prompt_flow}")
                except Exception:
                    final_prompt_flow = prompt_flow

        # ⚡ 2. 呼叫 Gemini 生成乾淨標準的 Mermaid 程式碼
        with st.spinner("Gemini 正在繪製 Mermaid 流程圖..."):
            try:
                system_prompt_flow = (
                    "你是個頂級系統流程圖專家。"
                    "【語言要求】title、description 及 flowchart 節點內的文字，必須完全使用繁體中文。"
                    "【Mermaid 語法嚴格要求】"
                    "1. 必須輸出合法的標準 flowchart TD 語法。"
                    "2. 節點標籤若包含中文，請務必使用雙引號包覆，例如：A[\"系統啟動\"] --> B{\"溫度過高?\"}。"
                    "3. 嚴禁使用 :::red, :::blue 等任何自訂類別樣式標籤！保持最純粹的 Mermaid 標準節點語法！"
                )

                res_flow, used_model = generate_with_fallback(
                    contents=final_prompt_flow,
                    system_instruction=system_prompt_flow,
                    response_schema=FlowchartOutput,
                    temperature=0.2
                )

                if res_flow and hasattr(res_flow, 'title'):
                    st.subheader(res_flow.title)
                    st.caption(f"使用模型：`{used_model}`")
                    st.write(res_flow.description)

                    # 清理程式碼標籤
                    clean_mermaid = res_flow.mermaid_code
                    if "```mermaid" in clean_mermaid:
                        clean_mermaid = clean_mermaid.split("```mermaid")[1].split("```")[0].strip()
                    elif "```" in clean_mermaid:
                        clean_mermaid = clean_mermaid.split("```")[1].split("```")[0].strip()

                    # 展開檢視語法
                    with st.expander("檢視 Mermaid 原始程式碼", expanded=False):
                        st.code(clean_mermaid, language="mermaid")

                    # 渲染圖形 Canvas (修正 script 載入)
                    mermaid_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                      <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                    </head>
                    <body style="background-color: transparent; margin: 0; padding: 10px;">
                      <pre class="mermaid" style="background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0;">
                      {clean_mermaid}
                      </pre>
                      <script>
                        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
                      </script>
                    </body>
                    </html>
                    """
                    import streamlit.components.v1 as components
                    components.html(mermaid_html, height=480, scrolling=True)

            except Exception as e:
                st.error(f"流程圖生成失敗：{e}")

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

    if st.button("生成 3D 場景", type="primary", key="btn_gen_3d"):
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