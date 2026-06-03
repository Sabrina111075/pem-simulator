import streamlit as st
import pandas as pd
import time

# ==============================================================================
# 1. 網頁基本配置 & 全域 CSS 樣式
# ==============================================================================
st.set_page_config(
    page_title="Crystal-Machine: 企業語意作業系統",
    page_icon="🔮",
    layout="wide"
)

current_time = time.strftime("%H:%M:%S", time.localtime())

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
    "O1001 (台灣電子 A 公司)": {
        "order_id": "O1001",
        "status_type": "danger",
        "alert_msg": "關鍵庫存 M002 庫存嚴重不足！供應商交期間歇，已引發最左端 O1001 骨牌效應斷鏈風險！",
        "pdca_status": "⚠️ **【PDCA 心跳警報】偵測到企業語意鏈邊界異常！自動啟動 S-Path 治理程序...**",
        "pdca_logs": f"☁️ 心跳訊號定時循環觸發 ( {current_time} ) ：【C-Check】🚨 偵測到 M002 爆發點 -> 【A-Action】觸發 O1001 骨牌效應修改防禦機制。\n\n📂 Heartbeat 訊號定時循環觸發 ( 14:46:38 ) : [P-Plan] 持續觀察拓撲 -> [D-Do] 更新狀態圖層 -> [C-Check] 偵測邊界異常。",
        
        "n1_txt": "🟦 節點 [1/5]：客戶層面 (Customer Layer)\n   [名稱] 台灣電子 A 公司 \n   [狀態] 良好 (已下單)",
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
    options=["請選擇訂單...", "O1001 (台灣電子 A 公司)", "O1002 (凌雲科技)"],
    index=1
)

st.write("---")
data = DYNAMIC_UI_DATA[selected_order]

# 🚀 區塊一：動態心跳與邊界診斷
st.markdown(f"### 🚨 即時預警與治理因果推理路徑 (更新時間: {current_time})")
render_heartbeat_panel(data["status_type"])

# 利用 st.empty() 強制當場覆寫，雙重防護
alert_text_placeholder = st.empty()
alert_text_placeholder.markdown(f"**🧐 語意鏈邊界診斷：** {data['alert_msg']}")
st.write("---")

# 🚀 區塊二：微觀知識圖譜路徑追蹤
st.markdown("<h3 style='font-weight:bold; color:#0f172a; margin-bottom:10px;'>🌐 目前知識圖譜路徑追蹤</h3>", unsafe_allow_html=True)
graph_text_block = f"""
📌 當前檢索語意對象：{data['order_id']}
=========================================

{data['n1_txt']}
   ⬇️ (下單關係鏈結)

{data['n2_txt']}
   ⬇️ (需求產品鏈結)

{data['n3_txt']}
   ⬇️ (消耗關鍵料鏈結)

{data['n4_txt']}
   ⬇️ (上游供應鏈結)

{data['n5_txt']}
"""
st.text_area(label="", value=graph_text_block.strip(), height=450, disabled=True, key=f"v_graph_{data['order_id']}")
st.write("---")

# 🚀 區塊三：S-Path 推薦狀態表格
if selected_order != "請選擇訂單...":
    st.markdown("### 📋 S-Path 推薦訂單段狀態表格")
    st.dataframe(data["table_df"])
    st.write("---")

# 🚀 區塊四：PDCA 日誌
st.markdown("### ⚙️ PDCA-心率監測與治理日誌")

pdca_status_placeholder = st.empty()
pdca_status_placeholder.markdown(data["pdca_status"])

st.markdown("<h5 style='font-weight:bold; color:#334155; margin-top:15px; margin-bottom:5px;'>📝 系統自動化自動修改架構日誌 (PDCA日誌) ：</h5>", unsafe_allow_html=True)
st.text_area(label="", value=data["pdca_logs"], height=130, disabled=True, key=f"v_logs_{data['order_id']}")