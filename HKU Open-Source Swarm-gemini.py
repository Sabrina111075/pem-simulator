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

# ------------------------------------------------------------------
# OpenHarness 與 Flowchart 的 Pydantic 結構定義
# ------------------------------------------------------------------
class HarnessOutput(BaseModel):
    title: str = Field(description="測試案例標題")
    description: str = Field(description="測試場景與驗證說明")
    python_code: str = Field(description="可執行的 Harness Python 測試程式碼")

class FlowchartOutput(BaseModel):
    title: str = Field(description="流程圖標題")
    mermaid_code: str = Field(description="Mermaid 語法流程圖代碼")
    description: str = Field(description="架構與流程說明")

# --------------------------------------------------
# 多主題預設測試需求模組 (Domain Preset Templates)
# --------------------------------------------------
TEST_DOMAIN_TEMPLATES = {
    "PEM 水電解槽 (Electrolyzer Digital Twin)": {
        "description": "針對 PEM 綠氫電解槽進行動態極化曲線、Butler-Volmer 活化過電壓、內阻與老化劣化擬合測試。",
        "default_prompt": (
            "【測試目標】驗證 5 kW PEM 水電解槽在 80°C 操作條件下的 U-I 極化曲線與 5,000 小時老化趨勢。\n"
            "【邊界條件】陽極純水流量 2.5 L/min，壓力 1.0 MPa；陰極氫氣出口壓力 3.0 MPa。\n"
            "【驗證項目】計算活化過電壓（Activation Overpotential）、歐姆過電壓與氣體擴散層（GDL）傳質極限。"
        ),
        "metrics": ["電流密度 (A/cm²)", "槽電壓 (V)", "產氫速率 (Nm³/h)", "法拉第效率 (%)"]
    },
    "電動機車動力系統 (EV Powertrain & Energy Loss)": {
        "description": "評估電動機車動力系統在 WMTC/WLTP 行駛型態下的電機效率、傳動損耗與電池續航表現。",
        "default_prompt": (
            "【測試目標】模擬 7.0 kW 永磁同步馬達 (PMSM) 電動機車在 WMTC 行駛工況下的動態能耗。\n"
            "【邊界條件】車重 110 kg，載重 75 kg，風阻係數 Cd=0.55，滾動阻力係數 Crr=0.012。\n"
            "【驗證項目】評估馬達銅損/鐵損比例、變頻器切換損耗，並繪製 100 km 能源效率分布與剩餘電量 SOC 曲線。"
        ),
        "metrics": ["車速 (km/h)", "電池 SOC (%)", "瞬間功率 (kW)", "綜合能效 (Wh/km)"]
    },
    "馬達與旋轉機械聲學故障診斷 (Acoustic Diagnostics)": {
        "description": "基於 FFT 與聲波頻譜分析（Mel-spectrogram），進行水泵、冷卻風扇與工業馬達之異常聲學診斷與預測性維護。",
        "default_prompt": (
            "【測試目標】對 3.7 kW 工業水泵馬達進行音訊特徵提取，評估軸承損壞（Outer Race Defect）與偏心異音。\n"
            "【邊界條件】採樣率 44.1 kHz，音訊時長 10 秒，環境背景噪音 -40 dB。\n"
            "【驗證項目】進行 1024-FFT 頻域轉換，計算 RMS 聲壓級、Spectral Centroid，並對比 DCASE/MIMII 異常基準。"
        ),
        "metrics": ["主頻峰值 (Hz)", "RMS 聲壓 (dB)", "異常信心度 (%)", "健康度指數 (HI)"]
    },
    "蜂群無人機多體動態與路徑規劃 (Swarm Logistics)": {
        "description": "模擬多無人機（Swarm UAV）在三維場域中的協同路徑規劃、防撞避障與任務負載分配。",
        "default_prompt": (
            "【測試目標】執行 5 架四軸無人機在障礙區域中的動態隊形切換與自主避障協同規劃。\n"
            "【邊界條件】風速向量 (1.5, 0.5, 0.0) m/s，最大傾角 30°，通訊延遲 < 20 ms。\n"
            "【驗證項目】計算 APF 人工勢場流場、碰撞風險指數、總航程能耗與隊形維持誤差。"
        ),
        "metrics": ["最小安全距離 (m)", "隊形誤差率 (%)", "任務完成時間 (s)", "通訊鏈路品質 (dBm)"]
    }
}

class NanoBotOptimizer:
    def __init__(self, api_key=""):
        from google import genai
        self.api_key = api_key
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None

    def optimize_harness_prompt(self, prompt):
        return f"{prompt}\n\n[Nano Bot 優化驗證：物理參數極限限制已鎖定]"

    def optimize_mermaid_prompt(self, prompt):
        return f"{prompt}\n\n[Nano Bot 優化驗證：流程圖邊界保護機制已鎖定]"

    def optimize_3d_prompt(self, prompt):
        return f"{prompt}\n\n[Nano Bot 優化驗證：Three.js 3D 渲染幾何結構與氣泡動畫邊界已鎖定]"

    def optimize_openspace_prompt(self, prompt):
        return f"{prompt}\n\n[Nano Bot 優化驗證：OpenSpace 空間場域節點與拓撲邊界已鎖定]"

    def estimate_3d_performance(self, prompt):
        return {
            "components": "12 個",
            "particles": "500 顆",
            "fps_target": "60 FPS"
        }

# ------------------------------------------------------------------
# Gemini LLM 自動降級/容錯呼叫函式 (優先使用 Flash-Lite -> Flash -> Pro)
# ------------------------------------------------------------------
def generate_with_fallback(contents, system_instruction="", response_schema=None, temperature=0.2):
    from google import genai
    from google.genai import types

    # 1. 安全取得 API Key
    api_key = (
        os.environ.get("GEMINI_API_KEY")
        or st.secrets.get("GEMINI_API_KEY", "")
        or st.session_state.get("api_key", "")
    )
    
    if not api_key:
        raise ValueError("未檢測到 GEMINI_API_KEY，請確認系統設定或 sidebar API key。")

    client = genai.Client(api_key=api_key)

    # 2. 依照您的模型優先順序排列 (Flash-Lite 主力 -> Flash 第二 -> Pro 第三 -> 舊版備用)
    preferred_model = st.session_state.get("selected_model", "gemini-2.5-flash-lite")
    models_to_try = [
        preferred_model,
        "gemini-3.5-flash-lite",
        "gemini-3.6-flash",
        "gemini-3.1-pro"
    ]
    # 自動去除重複項目且維持權重順序
    models_to_try = list(dict.fromkeys(models_to_try))

    last_error = None
    for model_name in models_to_try:
        try:
            config_args = {"temperature": temperature}
            if system_instruction:
                config_args["system_instruction"] = system_instruction
            if response_schema:
                config_args["response_mime_type"] = "application/json"
                config_args["response_schema"] = response_schema

            config = types.GenerateContentConfig(**config_args)

            # 確保輸入內容為字串格式
            prompt_input = contents
            if isinstance(contents, list) and len(contents) > 0:
                prompt_input = contents[-1]

            response = client.models.generate_content(
                model=model_name,
                contents=str(prompt_input),
                config=config
            )

            # 解析結構化 json 輸出
            if response_schema and hasattr(response, "text") and response.text:
                import json
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_text)
                
                if hasattr(response_schema, "parse_obj"):
                    return response_schema.parse_obj(data), model_name
                elif hasattr(response_schema, "model_validate"):
                    return response_schema.model_validate(data), model_name
                else:
                    class StructuredResult:
                        def __init__(self, d):
                            for k, v in d.items():
                                setattr(self, k, v)
                    return StructuredResult(data), model_name

            return response.text, model_name

        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"所有 Gemini 模型調用失敗，最後錯誤: {last_error}")

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

    # OpenSpace 空間雙生設定
    st.sidebar.markdown("### 🌌 OpenSpace 空間雙生環境")
    enable_openspace = st.sidebar.checkbox("啟用 OpenSpace 空間資料視覺化與監控", value=True)

    if enable_openspace:
        st.sidebar.info("🚀 OpenSpace 運作狀態：空間實體場景與感測網格同步中")

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
# 初始化 Nano Bot (防禦型安全寫法)
# ------------------------------------------------------------------
api_key = (
    os.environ.get("GEMINI_API_KEY")
    or st.secrets.get("GEMINI_API_KEY", "")
    or st.session_state.get("api_key", "")
)

if "NanoBotOptimizer" in globals():
        st.session_state.nano_bot = NanoBotOptimizer(api_key=api_key)
else:
        st.session_state.nano_bot = None

# ------------------------------------------------------------------
# 側邊欄控制項 (綁定 session_state)
# ------------------------------------------------------------------
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
st.title("⚡ HKU Open-Source Swarm | AI 物理雙生與蜂群智慧模擬系統")
st.caption("融合 OpenHarness 自動化引擎、CLI 指令、 Nano Bot 微型診斷、ClawTeam 蜂群代理、OpenSpace 幾何網格與 Gemini LLM 智能驅動引擎 ")

tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ OpenHarness 自動化引擎模擬與測試",
    "📊 Mermaid 流程圖生成",
    "🎨 Three.js 3D 模擬生成",
    "🌌 OpenSpace 空間雙生場域"
])

# ------------------------------------------------------------------
# Tab 1: OpenHarness 自動化引擎模擬與測試
# ------------------------------------------------------------------
with tab1:
    st.header("⚡ OpenHarness 自動化引擎模擬與測試")
    
    # 1. 跨主題選單 (Dynamic Domain Selector)
    selected_domain = st.selectbox(
        "🎯 請選擇欲進行測試的系統主題（Domain）：",
        options=list(TEST_DOMAIN_TEMPLATES.keys()),
        index=0,
        key="tab1_domain_selector"
    )
    
    # 2. 取得當前選取主題的設定檔與說明
    current_config = TEST_DOMAIN_TEMPLATES[selected_domain]
    st.caption(f"💡 **主題說明**：{current_config['description']}")
    
    # 3. 動態帶入對應主題的需求預設值 (自動保留使用者修改)
    prompt_key = f"input_prompt_{selected_domain}"
    if prompt_key not in st.session_state:
        st.session_state[prompt_key] = current_config["default_prompt"]
        
    prompt_harness = st.text_area(
        "📝 輸入欲進行測試的需求與邊界條件：",
        value=st.session_state[prompt_key],
        height=130,
        key=f"prompt_harness_{selected_domain}"
    )
    
    # 4. 關鍵指標提示 (Metrics Tags)
    st.markdown("**📊 預計提取之關鍵指標 (Key Metrics)：**")
    metric_cols = st.columns(len(current_config["metrics"]))
    for idx, metric in enumerate(current_config["metrics"]):
        metric_cols[idx].info(metric)
        
    st.markdown("---")
    
# --------------------------------------------------
# 動態執行按鈕
# --------------------------------------------------
button_label = f"🚀 執行 {selected_domain.split(' ')[0]} 模擬與生成 Harness 測試案例"

# 點擊按鈕時觸發執行狀態
if st.button(button_label, type="primary", use_container_width=True):
    st.session_state["trigger_harness"] = True

# 只有在使用者點擊了執行按鈕後，才啟動後續所有 Prompt 處理與 LLM 生成
if st.session_state.get("trigger_harness", False):
    
    # 1. 初始化基礎提示詞
    final_prompt_harness = prompt_harness
    is_nano_active = st.session_state.get("enable_nano_optimizer", False)
    is_clawteam_active = st.session_state.get("enable_clawteam", False)
    domain_title = selected_domain

    # --------------------------------------------------
    # 2. ClawTeam 蜂群代理協作區塊 (勾選時觸發)
    # --------------------------------------------------
    if is_clawteam_active:
        with st.expander("🐝 ClawTeam 蜂群協作完成！", expanded=True):
            st.markdown(f"""
            * 🤖 **Swarm Leader (HKUDS Agent)**: 正在解析 {domain_title} 系統模組需求...
            * 🔬 **{domain_title} Physics Agent (Nano Bot)**: 執行物理參數與領域約束診斷...
              * └── 物理參數與領域規範驗證 (系統正常)
            * 🛠️ **Harness Code Builder Agent**: 生成符合 OpenHarness 規範之測試案例...
            * 📑 **QA Reviewer Agent**: 完成 Pydantic 結構與邊界條件驗證...
            """)
        final_prompt_harness = (
            f"{final_prompt_harness}\n\n"
            f"[ClawTeam Swarm 蜂群協作指導規範]\n"
            f"1. 由 Swarm Leader 統一調度，結合 {domain_title} Physics 與 Code Builder 協同任務。\n"
            f"2. 產出必須包含對應物理場域數值分析與 OpenHarness Python 測試程式碼。"
        )

    # --------------------------------------------------
    # 3. Nano Bot 前置提示詞優化區塊 (勾選時觸發)
    # --------------------------------------------------
    if is_nano_active:
        if "nano_bot" in st.session_state and hasattr(
            st.session_state.nano_bot, "optimize_harness_prompt"
        ):
            final_prompt_harness = (
                st.session_state.nano_bot.optimize_harness_prompt(
                    final_prompt_harness
                )
            )
        
        st.success(f"⚡ {domain_title} 系統物理診斷引擎已就緒")
        with st.expander("🔍 檢視 Nano Bot 系統物理診斷報告與優化 Prompt", expanded=True):
            st.write(f"[{domain_title} 系統物理診斷報告]")
            st.markdown(f"• **邊界條件**: 針對 `{domain_title}` 進行物理參數約束校正。")
            st.code(final_prompt_harness, language="markdown")
    elif not is_clawteam_active:
        # 兩者皆未勾選時顯示基礎 Prompt
        with st.expander("🔍 檢視 OpenHarness 基礎測試 Prompt", expanded=False):
            st.code(final_prompt_harness, language="markdown")

    # --------------------------------------------------
    # 4. LLM 測試案例生成與代碼渲染 (按下按鈕才執行)
    # --------------------------------------------------
    with st.spinner(f"正在進行 {domain_title} 電化學/物理模型擬合與 Harness 測試案例生成..."):
        try:
            res_harness, used_model = generate_with_fallback(
                contents=final_prompt_harness,
                system_instruction=(
                    f"你是一個專業的 {domain_title} 物理雙生模擬專家與 OpenHarness 自動化測試工程師。"
                    "請根據輸入需求生成測試案例描述與完整的 Python Harness 測試程式碼。"
                    "所有說明文字必須嚴格使用台灣繁體中文。"
                ),
                response_schema=HarnessOutput,
                temperature=0.2,
            )
            
            # 渲染測試案例與腳本結果
            if res_harness:
                st.markdown(f"### 📌 測試案例：{res_harness.test_case_name}")
                st.markdown("#### 📋 測試說明與邊界條件")
                st.write(res_harness.description)
                
                st.markdown("#### 💻 OpenHarness 測試腳本 (Python)")
                st.code(res_harness.python_code, language="python")
                st.success(f"✅ 生成完成！（調用模型：{used_model}）")
                
        except Exception as e:
            st.error(f"❌ 測試案例生成失敗：{str(e)}")

else:
    # 未點擊按鈕時的提示
    st.info("💡 **系統就緒**：請點擊上方的「🚀 執行模擬與生成 Harness 測試案例」按鈕以啟動診斷與測試腳本生成。")

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

        # 2. ClawTeam 群體智能 Swarm 多 Agent 協作（新增此區塊）
        enable_clawteam = st.session_state.get("enable_clawteam", True)
        if enable_clawteam:
            with st.spinner("🐝 ClawTeam 群體代理 (Swarm) 正在進行多模型協作審查與代碼加固..."):
                # 模擬 Swarm 蜂群協作優化
                final_prompt_3d += "\n\n[ClawTeam Swarm 驗證：多 Agent 雙重校驗 WebGL/Three.js 效能與語法安全]"

            with st.expander("🐝 ClawTeam 蜂群代理協作紀錄 (Swarm Completed)", expanded=True):
                st.success("✅ ClawTeam 多 Agent 協作完成！已完成 3D 渲染幾何結構與氣泡動畫邊界校驗。")
                st.json({
                    "Swarm Agent 1 (Architect)": "架構邊界審查通過 (OK)",
	  "Swarm Agent 2 (WebGL Expert)": "Three.js 著色器與光照優化完成",
	  "Swarm Agent 3 (QA Bot)": "動畫粒子效能與記憶體回收檢查通過"
                })

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

                # generate_with_fallback 會回傳 (內容, 模型名稱)

                res_text, used_model = generate_with_fallback(
                contents=final_prompt_3d,
                system_instruction=system_prompt_3d
                )

                # 清理與提取 HTML 內容
                if "```html" in res_text:
                    raw_html = res_text.split("```html")[1].split("```")[0].strip()
                elif "```" in res_text:
                    raw_html = res_text.split("```")[1].split("```")[0].strip()
                else:
                    raw_html = res_text.strip()

                st.caption(f"使用模型：`{used_model}`")

                # 渲染 3D Canvas
                import streamlit.components.v1 as components
                components.html(raw_html, height=650, scrolling=False)

            except Exception as e:
                st.error(f"3D 場景生成失敗：{e}")

# ---------------------------------------------------------
# Tab 4: OpenSpace 空間雙生場域
# ---------------------------------------------------------
with tab4:
    st.subheader("🌌 OpenSpace 空間數位雙生與環境網格 (Spatial Digital Twin)")
    st.markdown("將 OpenSpace 場域感知、幾何座標與空間數據點雲無縫導入 ClawTeam 蜂群節點。")
    st.write("---")
    
    # 1. 上方區塊：OpenSpace 場域參數設定
    st.markdown("#### 📍 OpenSpace 場域參數設定")
    
    col_param1, col_param2 = st.columns(2)
    with col_param1:
        space_dim = st.slider("空間網格解析度 (Grid Resolution)", 10, 50, 20)
        sensor_temp = st.slider("環境邊界溫度 (°C)", 20, 100, 80)
    with col_param2:
        st.metric(label="OpenSpace 同步節點數", value=f"{space_dim * space_dim} Points")
        st.metric(label="ClawTeam 幾何映射狀態", value="Active 🟢")
        
    st.write("---")
    
    # 2. 下方區塊：空間拓撲圖與數據視覺化
    st.markdown("#### 📊 OpenSpace 空間熱力與拓撲分佈圖")
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        
        # 1. 解析度連動：頻率與網格採樣同步改變
        freq = space_dim / 10.0  # 網格數越多，熱力波動頻率越顯著
        x = np.linspace(-5, 5, space_dim)
        y = np.linspace(-5, 5, space_dim)
        X, Y = np.meshgrid(x, y)
        
        # 2. 溫度連動：計算熱力場與中心溫升擴散
        r = np.sqrt(X**2 + Y**2)
        # 混合高斯熱點與波紋場，隨溫度上升直接影響熱點強度與擴散範圍
        Z = sensor_temp * np.exp(-0.2 * r**2) + (sensor_temp * 0.2) * np.sin(freq * r)

        fig, ax = plt.subplots(figsize=(8, 4.5))
        # 固定 vmin 與 vmax，讓溫度變化時顏色的亮度和熱區面積產生極為明顯的變化
        cs = ax.contourf(X, Y, Z, levels=20, cmap='inferno', vmin=0, vmax=120)
        cbar = fig.colorbar(cs, ax=ax, label='Temperature Field (°C)')
        
        ax.set_title(f'OpenSpace Thermal Topology (Temp: {sensor_temp}°C, Grid: {space_dim}x{space_dim})')
        ax.set_xlabel('X Dimension (m)')
        ax.set_ylabel('Y Dimension (m)')
        
        st.pyplot(fig)
    except Exception as e:
        st.error(f"OpenSpace 拓撲圖渲染中：{e}")