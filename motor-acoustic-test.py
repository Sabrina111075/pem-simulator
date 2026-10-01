import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# 頁面配置
st.set_page_config(
    page_title="馬達與工業設備聲學診斷測試平台", page_icon="⚙️", layout="wide"
)

# 1. 側邊欄選單
page = st.sidebar.selectbox(
    "📌 切換功能模組：",
    ["⚙️ 設備與測試控制台", "🎓 OpenMAIC 聲學 AI 學院"],
)

# ==============================================================================
# 🎓 OpenMAIC 聲學 AI 學院
# ==============================================================================
if page == "🎓 OpenMAIC 聲學 AI 學院":
  col_left, col_center, col_right = st.columns([1.2, 3, 1.8], gap="small")

  # --- 左欄：課程導航 ---
  with col_left:
    st.subheader("📚 課程導航")
    course_list = [
        "課程 1：梅爾頻譜圖 (Mel-Spectrogram) 基礎原理",
        "課程 2：聲學訊號處理與 FFT/STFT 頻譜分析",
        "課程 3：馬達與風扇聲學故障診斷",
        "課程 4：Edge AI 邊緣運算與輕量化模型部署",
        "課程 5：工業物聯網 (IIoT) 設備預測性維護 SOP",
    ]
    selected_course = st.radio("請選擇研討主題：", course_list, index=0)
    st.divider()
    st.caption("目前學習進度：1/5")

  # --- 中欄：主展示與模擬實驗台 ---
  with col_center:
    st.caption(f"目前研討場景：{selected_course}")
    st.title(f"🎓 {selected_course}")

    with st.expander(
        "📌 點擊展開/收合：本課精華重點總結 (Course Summary)", expanded=True
    ):
      st.markdown("""
            * **核心概念**：將時域聲學訊號轉為 2D 頻譜圖，並將 Y 軸頻率轉為符合人類聽覺特性的 Mel Scale。
            * **工業診斷應用**：捕捉馬達與軸承的高頻衝擊特徵，實現早期微弱故障特徵識別。
            """)

    with st.container(border=True):
      st.markdown("#### 🔬 聲學頻譜動態模擬視窗")
      sim_c1, sim_c2 = st.columns([1, 2])
      with sim_c1:
        st.slider("採樣率 (Hz)", 8000, 44100, 16000)
        st.slider("FFT 窗格大小 (N_FFT)", 256, 2048, 512)
        st.button("🚀 重新萃取特徵", use_container_width=True)
      with sim_c2:
        st.info("📈 [動態頻譜可視化區] STFT / Mel-Spectrogram 特徵圖譜展演")

    with st.container(border=True):
      st.markdown(
          "👩‍🏫 **Prof. Acoustic (聲學總導師)**："
          "歡迎來到本單元！請觀察右側對話區，多智體團隊已針對此主題準備好圓桌研討內容。"
      )

  # --- 右欄：OpenMAIC 4 人智體圓桌研討區 ---
  with col_right:
    tab_chat, tab_notes = st.tabs(["💬 智體圓桌研討", "📖 隨堂筆記"])

    with tab_chat:
      st.subheader("💬 OpenMAIC 多智體互動研討")
      user_q = st.text_input(
          "輸入您的研討疑問：",
          value=f"什麼是{selected_course.split('：')[-1]}？",
      )

      if user_q:
        st.caption("💬 4 人研討小組正在發表立場與觀點：")
        res_data = {
            "prof_reply": f"針對【{selected_course}】的核心原理，主要依賴時頻分析將一維聲壓轉為二維特徵圖，為物理場建模提供扎實基礎。",
            "beth_reply": f"在硬體落地方面，我們採用 INT8 量化與輕量化架構，能大幅降低記憶體佔用，順利部署於 STM32/ESP32 等邊緣晶片。",
            "alex_reply": f"從數據科學角度，我們針對 MIMII/DCASE 資料集提取高階特徵，能在高背景雜訊下維持 95% 以上偵測率。",
            "cathy_reply": f"從商業 ROI 考量，結合預測性維護 (PdM) 能有效降低非預期停機風險，提昇設備 OEE 並降低運維成本。",
        }
        agents = [
            (
                "👨‍🏫 [Prof. Acoustic] 聲學總導師",
                res_data["prof_reply"],
                "#eef2ff",
            ),
            (
                "👩‍💻 [Engineer Beth] AI 邊緣部署工程師",
                res_data["beth_reply"],
                "#f0fdf4",
            ),
            (
                "👨‍‍🔬 [Data Scientist Alex] 數據科學專家",
                res_data["alex_reply"],
                "#fff7ed",
            ),
            (
                "👩‍💼 [Product Manager Cathy] 工業產品經理",
                res_data["cathy_reply"],
                "#fdf2f8",
            ),
        ]
        for name, reply, bg_color in agents:
          st.markdown(
              f"""
                <div style="background-color: {bg_color}; padding: 10px 14px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #e2e8f0;">
                    <b style="color: #1e293b;">{name}</b><br/>
                    <span style="font-size: 14px; color: #334155;">{reply}</span>
                </div>
                """,
              unsafe_allow_html=True,
          )

    with tab_notes:
      st.text_area(
          "隨堂重點筆記：",
          "1. 時頻分析需注意 Window Size 對時間與頻率解析度的影響。\n2...",
          height=250,
      )

# ==============================================================================
# ⚙️ 設備與測試控制台 (包含原本所有波形圖與頻譜圖繪製程式碼)
# ==============================================================================
else:
  # ⚠️ 請把您原本檔名為 motor-acoustic-test.py 裡面，
  # 從 `# 2. 標題與簡介` 開始直到檔案最底部的所有程式碼，
  # 全部貼在 else: 裡面 (並全選按 Tab 鍵縮排 4 個空格)！

  # 1. 標題與簡介
  st.title(
      "⚙️ 馬達與工業設備聲學診斷測試平台 (EdgeAcoustic AI)"
  )
  st.caption("邊緣運算前置驗證平台 | 支援 ESP32-S3 + Raspberry Pi 5 模擬測試")

  # 2. 側邊欄：6 大工業設備選單與狀態
  st.sidebar.header("⚙️ 設備與測試控制台")
  category = st.sidebar.selectbox(
      "1. 選擇設備類別 (Category)",
      [
          "工業風扇 (Fan)",
          "工業馬達 (Motor)",
          "工業水泵 (Pump)",
          "電磁閥門 (Valve)",
          "線性滑軌 (Slide Rail)",
          "工業齒輪箱 (Gearbox)",
          "風力發電機 - 齒輪箱 (Wind Turbine - Gearbox)",
          "風力發電機 - 發電機 (Wind Turbine - Generator)",
          "風力發電機 - 實測風場聲 (Wind Turbine Field Acoustics)",
          "電動車電池水冷泵浦 (EV Battery Cooling Pump)",
      ],
  )
  status_option = st.sidebar.selectbox(
      "2. 選擇測試狀態/故障型態", ["正常 (Normal)", "異常 (Abnormal)"]
  )

  # 3. 這裡接您原本的音訊生成/播放 (st.audio) 與 Matplotlib/Plotly 繪圖邏輯 (st.pyplot / st.plotly_chart)
  # (包含波形圖、FFT 頻譜、梅爾頻譜圖等)