import streamlit as st
import streamlit.components.v1 as components

# 設定頁面標題與寬度
st.set_page_config(page_title="OpenMAIC 聲學 AI 學院", layout="wide")

st.title("🎓 OpenMAIC 聲學 AI 學院 × 虛擬聲學診斷實驗室")
st.caption("結合 OpenMAIC 多智能體 AI 課堂與 Streamlit 邊緣聲學診斷模擬 (EdgeAcoustic AI)")

# 說明區塊
st.info("💡 本頁面將 OpenMAIC 的多智能體 AI Teacher/TA 引導與您現有的馬達聲學測試平台進行整合，實現「觀念學習 → 模擬實驗 → 成果認證」三位一體教學。")

# 建立左右雙欄版面 (左欄：OpenMAIC AI 課堂 / 右欄：現有 Streamlit 聲學平台)
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🤖 OpenMAIC AI 課堂 & 導師引導")
    # 這裡填入您部署好的 OpenMAIC 網址 (或先用展示 placeholder 網址)
    openmaic_url = st.text_input("OpenMAIC 服務網址:", "https://openmaic.chat/") 
    
    # 使用 components.iframe 嵌入 OpenMAIC 畫面
    components.iframe(openmaic_url, height=650, scrolling=True)

with col2:
    st.subheader("⚙️ 馬達與工業設備聲學診斷測試平台 (Virtual Lab)")
    # 嵌入您現有的 Streamlit 聲學測試平台網址
    streamlit_lab_url = "https://motor-acoustic-test.streamlit.app"
    
    components.iframe(streamlit_lab_url, height=650, scrolling=True)

# 底部：JSON 報告回寫 (Governed Writeback) 示範區
st.divider()
st.subheader("📥 學習與實驗成果回寫 (Governed Writeback)")
uploaded_file = st.file_uploader("請上傳由右側平台下載的「聲學巡檢報告 (JSON)」以完成 OpenMAIC 課程單元認證：", type=['json'])

if uploaded_file is not None:
    st.success("✅ 巡檢報告已成功接收！正在將診斷數據 (HI, MSE) 回寫至聲學 Knowledge Container...")
```[cite: 1, 2, 4, 5]

---

### 🔗 第三步：在主程式（多頁選單）中將新頁面掛載進去

若您的 Streamlit 平台是用多頁面架構（Multi-page App）或主選單（例如 `motor-acoustic-test.py` 或 `pages/` 資料夾）[cite: 5]：

* **方法 A（推薦：Streamlit 官方多頁機制）**：
  在資料夾中新建一個名為 `pages` 的子資料夾[cite: 5]，然後把 `openmaic_academy.py` 放進 `pages/` 資料夾內[cite: 5]。Streamlit 就會自動在側邊欄產生頁面切換按鈕！
* **方法 B（單一檔案側邊欄切換）**：
  在主程式 `motor-acoustic-test.py` 的側邊欄選單中[cite: 5]，加上一個頁面選擇器（如 `st.sidebar.radio`），選到「OpenMAIC 聲學學院」時引入或執行這一段程式[cite: 1, 5]。

---

### 🚀 第四步：上傳 / Push 到 GitHub 並在 Streamlit Cloud 部署

1. 將新建的 `.py` 檔案儲存[cite: 5]。
2. 依照您平時上傳 Streamlit 的方式（使用 Git Commit/Push 到您的 GitHub 儲存庫）[cite: 5]。
3. 開啟 Streamlit Cloud 控制台，系統偵測到 Git 更新後就會自動重新部署[cite: 5]！

---

夥伴，您可以先嘗試建立這個 `openmaic_academy.py` 記事本檔案[cite: 5]，如果有遇到語法或選單掛載的問題，隨時告訴我，我來協助您調整程式碼！