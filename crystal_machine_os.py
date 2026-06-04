import streamlit as st
import time
import pandas as pd  
import json
from datetime import datetime, timedelta, timezone

# ==============================================================================
# # 1. 網頁基本配置 & 全域 CSS 樣式
# ==============================================================================
st.set_page_config(
    page_title="Crystal-Machine: 企業語意作業系統",
    page_icon="🔮",
    layout="wide"
)

# 💡 3. 防止 Google 翻譯自作聰明
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# 💡 4. 網頁自我監測：每 1800 秒 網頁原生的動態重新整理
st.markdown('<meta http-equiv="refresh" content="1800">', unsafe_allow_html=True)

from datetime import datetime, timedelta, timezone

# 💡 強制鎖定台灣時區 (GMT+8)，解決雲端 Linux 伺服器的 8 小時時差
tz_taiwan = timezone(timedelta(hours=8))
current_time = datetime.now(tz_taiwan).strftime("%H:%M:%S")

st.markdown("""
<style>
    .reportview-container { 
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important; 
    }
    .dataframe { 
        width: 100% !important; 
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    .stTextArea textarea:disabled {
        opacity: 1 !important;
        -webkit-text-fill-color: currentcolor !important; 
    }
    .stTextArea textarea {
        border-radius: 10px !important;
        font-family: 'Consolas', 'Courier New', monospace !important;
        font-size: 15px !important; 
        line-height: 1.6 !important;
        padding: 18px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04) !important;
    }
    /* 圖譜區塊：高對比蔚藍底 */
    .stTextArea:nth-of-type(1) textarea {
        background-color: #e0f2fe !important;    
        color: #034494 !important;               
        border: 2px solid #38bdf8 !important;     
        font-weight: 600 !important;
    }
    /* 日誌區塊：護眼暖陽黃底 */
    .stTextArea:nth-of-type(2) textarea {
        background-color: #fefcbf !important;    
        color: #1e293b !important;               
        border: 2px solid #fef08a !important;     
        border-left: 6px solid #eab308 !important; 
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. 核心功能：動態 Heartbeat 脈搏面板渲染器
# ==============================================================================
def render_heartbeat_panel(status_type):
    if status_type == "danger":
        theme_color = "#ef4444"
        bg_color = "#fef2f2"
        text_color = "#991b1b"
        pulse_speed = "0.8s"
        status_text = "⚠️ 系統狀態：異常警告 (CRITICAL ALERT)"
    elif status_type == "normal":
        theme_color = "#10b981"
        bg_color = "#ecfdf5"
        text_color = "#166534"
        pulse_speed = "1.6s"
        status_text = "🟢 系統狀態：一切正常 (SYSTEM HEALTHY)"
    else:
        theme_color = "#94a3b8"
        bg_color = "#f8fafc"
        text_color = "#475569"
        pulse_speed = "3s"
        status_text = "ℹ️ 系統狀態：等待指令"

    html_code = f"""
    <div style="
        background-color: {bg_color}; 
        border-left: 6px solid {theme_color};
        padding: 16px; 
        border-radius: 8px; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        justify-content: space-between;
    ">
        <div>
            <div style="font-size: 18px; font-weight: 800; color: {text_color}; margin-bottom: 4px;">
                {status_text}
            </div>
            <div style="font-size: 13px; color: #64748b; font-weight: 500;">
                HEARTBEAT MONITORING PATHWAY // CORE OS LAYER ACTIVE
            </div>
        </div>
        
        <div style="display: flex; align-items: center; gap: 12px; margin-right: 10px;">
            <span style="font-size: 12px; font-weight: 700; color: {theme_color}; font-family: monospace;">
                PULSE RATE
            </span>
            <div class="pulse-container" style="position: relative; width: 24px; height: 24px;">
                <div class="pulse-core" style="width: 14px; height: 14px; background-color: {theme_color}; border-radius: 50%; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 2;"></div>
                <div class="pulse-ring" style="width: 24px; height: 24px; border: 3px solid {theme_color}; border-radius: 50%; position: absolute; top: 0; left: 0; box-sizing: border-box; animation: heartbeat {pulse_speed} infinite ease-in-out; z-index: 1;"></div>
            </div>
        </div>
    </div>

    <style>
        @keyframes heartbeat {{
            0% {{ transform: scale(0.4); opacity: 1; }}
            80% {{ transform: scale(1.2); opacity: 0; }}
            100% {{ transform: scale(1.2); opacity: 0; }}
        }}
    </style>
    """
    st.components.v1.html(html_code, height=95)

# ==============================================================================
# 3. 靜態集中式資料字典 (【徹底校正】修正 O1002 內的 alert_msg 錯置 Bug)
# ==============================================================================
DYNAMIC_UI_DATA = {
    "O1001 (台灣電子公司)": {
        "order_id": "O1001",
        "status_type": "danger",
        "alert_msg": "關鍵庫存 M002 庫存嚴重不足！供應商交期間歇，已引發最左端 O1001 骨牌效應斷鏈風險！",
        "pdca_status": "⚠️ **【PDCA 心跳警報】偵測到企業語意鏈邊界異常！自動啟動 S-Path 治理程序...**",
        "pdca_logs": f"☁️ 心跳訊號定時循環觸發 ( {current_time} ) ：【C-Check】🚨 偵測到 M002 爆發點 -> 【A-Action】觸發 O1001 骨牌效應修改防禦機制。\n\n📂 Heartbeat 訊號定時循環觸發 ( 14:46:38 ) : [P-Plan] 持續觀察拓撲 -> [D-Do] 更新狀態圖層 -> [C-Check] 偵測邊界異常。",
        
        "n1_txt": "🟦 節點 [1/5]：客戶層面 (Customer Layer)\n   [名稱] 台灣電子公司 \n   [狀態] 良好 (已下單)",
        "n2_txt": "📦 節點 [2/5]：訂單層面 (Order Layer) \n   [單號] O1001 \n   [狀態] ⚠️ 多米諾骨牌效應普遍存在風險",
        "n3_txt": "🏷️ 節點 [3/5]：產品展示層面 (Product Layer) \n   [品名] 高階控制模組 \n   [狀態] ❌ 受下游缺料波及",
        "n4_txt": "🧩 節點 [4/5]：關鍵物料層 (Material Layer) \n   [料號] M002 核心晶片 \n   [狀態] 🚨 庫存嚴重不足 (交期嚴重)",
        "n5_txt": "🏭 節點 [5/5]：供應商層面 (Supplier Layer) \n   [廠商] 大發晶圓廠 \n   [狀態] ⚠️ 供應商緊急照會 / 產能吃緊",
        
        "table_df": pd.DataFrame({
            "節點類型": ["客戶", "訂單", "產品展示", "關鍵庫存", "供應商"],
            "名稱/編號": ["台灣 A 公司", "O1001", "高階控制模組", "M002 核心晶片", "大發晶圓廠"],
            "狀態說明": ["好的 (已下單)", "多米諾骨牌效應普遍存在風險", "受下游缺料波及", "庫存嚴重不足", "供應商緊急照會"],
            "S-Path 建議行動": ["發送夜間預警通知", "啟動備用調度程序", "調整生產排程優先權", "尋找替代現貨料源", "與供應商緊急照會"]
        })
    },
    "O1002 (凌雲科技)": {
        "order_id": "O1002",
        "status_type": "normal",
        # 🌟【這裡終於改對了！】徹底消滅陰魂不散的 O1001 斷鏈風險字眼
        "alert_msg": "該訂單關聯語意節點皆處於健康邊界，安全存量充足，無潛在斷鏈風險。",
        "pdca_status": "✅ **【PDCA 心跳正常】語意網絡因果完整，結構強韌，目前無斷裂風險。**",
        "pdca_logs": f"☁️ 心跳訊號定時循環觸發 ( {current_time} ) ：【C-Check】🟢 檢測全域變數 -> 【A-Action】狀態良好，無需介入變動。\n\n📂 Heartbeat 訊號定時循環觸發 ( 15:02:11 ) : [P-Plan] 全域路徑監控中 -> [D-Do] 語意鏈路一切穩定 -> [C-Check] 健康邊界覆蓋完成。",
        
        "n1_txt": "🟦 節點 [1/5]：客戶層面 (Customer Layer)\n   [名稱] 凌雲科技 \n   [狀態] 良好 (已下單)",
        "n2_txt": "📦 節點 [2/5]：訂單層面 (Order Layer) \n   [單號] O1002 \n   [狀態] 🟢 正常 (依序處理中)",
        "n3_txt": "🏷️ 節點 [3/5]：產品展示層面 (Product Layer) \n   [品名] 標準型感測器 \n   [狀態] 🟢 庫存充足",
        "n4_txt": "🧩 節點 [4/5] : 關鍵物料層 (Material Layer) \n   [料號] M005 感測元件 \n   [狀態] 🟢 供應鏈穩定",
        "n5_txt": "🏭 節點 [5/5]：供應商層面 (Supplier Layer) \n   [廠商] 日新電子 \n   [狀態] 🟢 正常供貨",
        
        "table_df": pd.DataFrame({
            "節點類型": ["客戶", "訂單", "產品展示", "關鍵庫存", "供應商"],
            "名稱/編號": ["凌雲科技", "O1002", "標準型感測器", "M005 感測元件", "日新電子"],
            "狀態說明": ["好的 (已下單)", "正常 (依序處理中)", "庫存充足", "供應鏈穩定", "正常供貨"],
            "S-Path 建議行動": ["標準自動化追蹤", "維持既定排程", "無需額外干預", "定期追蹤庫存", "自動維護夥伴關係"]
        })
    },
    "請選擇訂單...": {
        "order_id": "---",
        "status_type": "idle",
        "alert_msg": "請選擇一張訂單以開始進行因果治理推理。",
        "pdca_status": "ℹ️ 系統等待指令中...",
        "pdca_logs": "📋 系統處於閒置狀態。請選擇上方的語意數據鏈進行檢索。",
        "n1_txt": "🟦 節點 [1/5]：客戶層面 (Customer Layer)\n   [名稱] 等待載入... \n   [狀態] ---",
        "n2_txt": "📦 節點 [2/5]：訂單層面 (Order Layer)\n   [單號] --- \n   [狀態] 等待載入...",
        "n3_txt": "🏷️ 節點 [3/5] : 產品展示層面 (Product Layer)\n   [品名] --- \n   [狀態] 等待載入...",
        "n4_txt": "🧩 節點 [4/5]：關鍵物料層 (Material Layer)\n   [料號] --- \n   [狀態] 等待載入...",
        "n5_txt": "🏭 節點 [5/5]：供應商層面 (Supplier Layer)\n   [廠商] --- \n   [狀態] 等待載入...",
        "table_df": pd.DataFrame(columns=["節點類型", "名稱/編號", "狀態說明", "S-Path 建議行動"])
    }
}

# ==============================================================================
# 4. 控制台介面
# ==============================================================================
st.title("🔮 Crystal-Machine: 企業語意作業系統")
st.subheader("🗂 語意資料鏈搜尋控制台")

selected_order = st.selectbox(
    "💡 請選擇渴望回溯推理的目標順序：",
    options=["請選擇訂單...", "O1001 (台灣電子公司)", "O1002 (凌雲科技)"],
    index=1
)

st.write("---")
data = DYNAMIC_UI_DATA[selected_order]

# 🚀 區塊一：動態心跳與邊界診斷
st.markdown(f"### 🚨 即時監控與治理因果推理路徑 (更新時間: {current_time})")
render_heartbeat_panel(data["status_type"])

# 利用 st.empty() 強制當場覆寫，雙重防護
alert_text_placeholder = st.empty()
alert_text_placeholder.markdown(f"**🧐 語意鏈邊界診斷：** {data['alert_msg']}")
st.write("---")

# ==============================================================================
# # 區域二：S-Path-RAG 微觀知識圖譜路徑追蹤 (語法相容、空值防禦與視覺減壓完全版)
# ==============================================================================
import pandas as pd

st.markdown("<h3 style='font-weight:bold; color:#0f172a; margin-bottom:15px;'>🔮 S-Path-RAG 微觀知識圖譜路徑追蹤</h3>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 💡 1. 核心防禦：如果 data 根本沒有載入成功，直接友善提示並攔截，絕不往下走噴錯！
# ------------------------------------------------------------------------------
if not isinstance(data, dict) or not data:
    st.markdown("""
        <div style="background-color:#f1f5f9; padding:15px; border-left:5px solid #64748b; border-radius:4px; color:#334155;">
            💡 請在上方選單選擇有效的企業訂單，以利系統動態檢索微觀知識圖譜。
        </div>
    """, unsafe_allow_html=True)
else:
    # --------------------------------------------------------------------------
    # 💡 2. 安全變數提取 (使用 .get 徹底消滅 KeyError，大字串內不允許出現引號中括號)
    # --------------------------------------------------------------------------
    current_order_id = str(data.get('order_id', '未載入單號'))
    n1_content = str(data.get('n1_txt', '常態數據檢索中...'))
    n2_content = str(data.get('n2_txt', '常態數據檢索中...'))
    n3_content = str(data.get('n3_txt', '常態數據檢索中...'))
    n4_content = str(data.get('n4_txt', '常態數據檢索中...'))
    n5_content = str(data.get('n5_txt', '')) 

    # 3. 頂部加入 RAG 檢索效能指標
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(label="⚡ 知識圖譜推理延遲", value="38 ms", delta="-4 ms")
    with col_m2:
        is_anomaly = "嚴重" in n4_content or "不足" in n4_content
        conf_score = "91.2%" if is_anomaly else "98.5%"
        st.metric(label="🎯 語意向量置信度", value=conf_score, delta="-7.3%" if is_anomaly else "0.2%")
    with col_m3:
        st.metric(label="⛓️ 關聯拓撲節點數", value="14 Nodes")

    st.markdown("---")
    st.markdown(f"**📋 當前檢索語意對象：** `{current_order_id}`")

    # --------------------------------------------------------------------------
    # 💡 4. 專家卡片渲染 (全面採用客製化 HTML 減壓藍色外框，極致相容，不使用 st.info)
    # --------------------------------------------------------------------------
    
    # 節點 1
    st.markdown(f"#### 🔗 1. 下單關係鏈結 (Order Linkage)")
    st.markdown(f"""
        <div style="background-color:#e0f2fe; padding:15px; border-left:5px solid #0284c7; border-radius:4px; margin-bottom:15px; color:#0f172a; line-height:1.6;">
            <strong>🔍 推理路徑細節：</strong><br>{n1_content}
        </div>
    """, unsafe_allow_html=True)

    # 節點 2 (加入口語化連帶風險提示，深橘色字)
    st.markdown(f"#### 🔗 2. 需求產品鏈結 (Product Demand Linkage)")
    if "風險" in n2_content or "連帶" in n2_content or "影響" in n2_content:
        st.markdown(f"""
            <div style="background-color:#e0f2fe; padding:15px; border-left:5px solid #0284c7; border-radius:4px; margin-bottom:15px; color:#0f172a; line-height:1.6;">
                <strong>🔍 推理路徑細節：</strong><br>{n2_content}<br><br>
                <span style='color:#d97706; font-weight:bold;'>⚠️ 狀況提示：受上游缺料波及，引發連帶生產風險。</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="background-color:#e0f2fe; padding:15px; border-left:5px solid #0284c7; border-radius:4px; margin-bottom:15px; color:#0f172a; line-height:1.6;">
                <strong>🔍 推理路徑細節：</strong><br>{n2_content}
            </div>
        """, unsafe_allow_html=True)

    # 節點 3
    st.markdown(f"#### 🔗 3. 消耗關聯料鏈結 (Material Consumption Linkage)")
    st.markdown(f"""
        <div style="background-color:#e0f2fe; padding:15px; border-left:5px solid #0284c7; border-radius:4px; margin-bottom:15px; color:#0f172a; line-height:1.6;">
            <strong>🔍 推理路徑細節：</strong><br>{n3_content}
        </div>
    """, unsafe_allow_html=True)

    # 節點 4 (核心根因，精準紅色粗體字提示)
    if "嚴重" in n4_content or "不足" in n4_content:
        st.markdown(f"#### 🔗 4. 上游供應鏈結 (Upstream Supply Linkage) <span style='color:#dc2626; font-weight:bold;'>[核心根因]</span>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background-color:#e0f2fe; padding:15px; border-left:5px solid #0284c7; border-radius:4px; margin-bottom:15px; color:#0f172a; line-height:1.6;">
                <strong>🔍 推理路徑細節：</strong><br>{n4_content}<br><br>
                <span style='color:#dc2626; font-weight:bold;'>🚨 核心異常：檢測到晶片庫存嚴重不足，此為本次卡料的源頭問題！</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"#### 🔗 4. 上游供應鏈結 (Upstream Supply Linkage)")
        st.markdown(f"""
            <div style="background-color:#e0f2fe; padding:15px; border-left:5px solid #0284c7; border-radius:4px; margin-bottom:15px; color:#0f172a; line-height:1.6;">
                <strong>🔍 推理路徑細節：</strong><br>{n4_content}
            </div>
        """, unsafe_allow_html=True)

    # 節點 5
    if n5_content:
        st.markdown(f"#### 🏢 5. 外部供應商調度協同 (Decision Linkage)")
        if "緊急" in n5_content or "吃緊" in n5_content:
            st.markdown(f"""
                <div style="background-color:#e0f2fe; padding:15px; border-left:5px solid #0284c7; border-radius:4px; margin-bottom:15px; color:#0f172a; line-height:1.6;">
                    <strong>🔍 推理路徑細節：</strong><br>{n5_content}<br><br>
                    <span style='color:#d97706; font-weight:bold;'>🔄 應變機制：系統已自動聯絡外部廠商，啟動緊急追料調度。</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color:#e0f2fe; padding:15px; border-left:5px solid #0284c7; border-radius:4px; margin-bottom:15px; color:#0f172a; line-height:1.6;">
                    <strong>🔍 推理路徑細節：</strong><br>{n5_content}
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-weight:bold; color:#1e293b; margin-bottom:12px;'>📋 S-Path 推薦訂單段狀態表格</h4>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 💡 5. 表格數據與口語化字眼解析 (彻底消除多米諾字眼)
    # --------------------------------------------------------------------------
    if "風險" in n1_content or "風險" in n2_content:
        t2_status = "🟠 預警"
        t2_desc = "受上游缺料波及，引發連帶生產風險"
        t2_action = "啟動備用調度程序"
        t3_desc = "受上游缺料波及預警"
    else:
        t2_status = "🟢 正常"
        t2_desc = "訂單狀態穩定，傳遞鏈正常"
        t2_action = "常態維持自動化追蹤"
        t3_desc = "動態生產滿足率 100%"

    if "嚴重" in n4_content or "不足" in n4_content:
        t4_status = "🔴 異常"
        t4_style = "color: #dc2626; font-weight: bold;"
        t4_action = "尋找替代現貨料源"
    else:
        t4_status = "🟢 正常"
        t4_style = "color: #059669;"
        t4_action = "按原排程常態收料"

    if n5_content and ("緊急" in n5_content or "吃緊" in n5_content):
        t5_status = "🟠 預警"
        t5_desc = "供應商產能吃緊，已發起緊急追料"
        t5_action = "與供應商緊急照會並追蹤"
    else:
        t5_status = "🟢 正常"
        t5_desc = "外部供應商產能與交期反饋正常"
        t5_action = "維持一般協同觀測"

    t4_clean_txt = n4_content.split(']')[-1] if ']' in n4_content else n4_content

    # 6. HTML 斑馬紋大表格渲染 (純變數填充，絕不報錯)
    html_table = f"""
    <table style="width:100%; border-collapse: collapse; font-family: sans-serif; margin-bottom: 20px;">
        <thead>
            <tr style="background-color: #f1f5f9; border-bottom: 2px solid #cbd5e1; text-align: left;">
                <th style="padding: 10px; font-weight: bold; color: #334155;">警示</th>
                <th style="padding: 10px; font-weight: bold; color: #334155;">節點類型</th>
                <th style="padding: 10px; font-weight: bold; color: #334155;">名稱/編號</th>
                <th style="padding: 10px; font-weight: bold; color: #334155;">狀態說明</th>
                <th style="padding: 10px; font-weight: bold; color: #334155;">S-Path 建議行動</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 10px;">🟢 正常</td>
                <td style="padding: 10px;">客戶</td>
                <td style="padding: 10px;">台灣A公司</td>
                <td style="padding: 10px;">好的 (已下單)</td>
                <td style="padding: 10px;">發送夜間預警通知</td>
            </tr>
            <tr style="background-color: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 10px;">{t2_status}</td>
                <td style="padding: 10px;">訂單</td>
                <td style="padding: 10px; font-weight: bold;">{current_order_id}</td>
                <td style="padding: 10px;">{t2_desc}</td>
                <td style="padding: 10px;">{t2_action}</td>
            </tr>
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 10px;">{t2_status}</td>
                <td style="padding: 10px;">產品展示</td>
                <td style="padding: 10px;">高階控制模組</td>
                <td style="padding: 10px;">{t3_desc}</td>
                <td style="padding: 10px;">{t2_action}</td>
            </tr>
            <tr style="background-color: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 10px;">{t4_status}</td>
                <td style="padding: 10px;">關鍵庫存</td>
                <td style="padding: 10px;">M002 核心晶片</td>
                <td style="padding: 10px; {t4_style}">{t4_clean_txt}</td>
                <td style="padding: 10px; font-weight: bold;">{t4_action}</td>
            </tr>
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 10px;">{t5_status}</td>
                <td style="padding: 10px;">供應商</td>
                <td style="padding: 10px;">大發晶圓廠</td>
                <td style="padding: 10px;">{t5_desc}</td>
                <td style="padding: 10px;">{t5_action}</td>
            </tr>
        </tbody>
    </table>
    """

    st.markdown(html_table, unsafe_allow_html=True)
    st.markdown("---")

# 🚀 區塊四：PDCA 日誌
st.markdown("### ⚙️ PDCA-心率監測與治理日誌")

pdca_status_placeholder = st.empty()
pdca_status_placeholder.markdown(data["pdca_status"])

st.markdown("<h5 style='font-weight:bold; color:#334155; margin-top:15px; margin-bottom:5px;'>📝 系統自動化自動修改架構日誌 (PDCA日誌) ：</h5>", unsafe_allow_html=True)
st.text_area(label="", value=data["pdca_logs"], height=130, disabled=True, key=f"v_logs_{data['order_id']}")