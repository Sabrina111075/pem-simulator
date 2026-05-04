# --- 6. 自動化商務對接：一鍵生成詢價郵件 ---
st.markdown("---")
st.header("✉️ 供應商開發對接工具")

# 根據當前選擇動態抓取建議供應商
target_suppliers = "匯川技術、英威騰、精進電動" if selected_platform == "OD220" else "安乃達、天津松正"

with st.expander("📝 自動生成標準詢價信 (RFI/RFQ Template)", expanded=False):
    st.write(f"建議發送對象：**{target_suppliers}**")
    
    # 郵件內容邏輯
    email_subject = f"詢價：{selected_platform}平台_{spec['p_peak']}kW電機控制器開發需求"
    email_body = f"""
您好，

我們目前正在進行【{selected_platform}】動力平台的開發規劃，經評估貴司在該領域的產品實力，希望能針對以下規格進行初步技術對接與樣機詢價：

1. 應用場景：電動車驅動系統 (平台等級：{selected_platform})
2. 馬達規格：峰值功率 {spec['p_peak']}kW / 峰值扭矩 {spec['t_peak']}Nm / 最高轉速 {spec['max_rpm']}rpm
3. 控制器要求：
   - 核心演算法：FOC + SVPWM {'+ 弱磁控制' if enable_fw else ''}
   - 母線電壓：{spec['v']}
   - 冷卻方式：{spec['cooling']}
   - 感測器介面：{selected_sensor}
   - 通訊協議：{', '.join(selected_comm)}
   - 安全要求：{'需支援預充電路與 HVIL' if selected_platform == "OD220" else '標準保護機制'}

請貴司協助評估是否有現成樣機可供測試，或需進行 NRE 客製化開發，並請提供初步報價與交期。

期待您的回覆。
"""
    
    # 使用 st.code 方便使用者一鍵複製
    st.subheader("郵件主旨：")
    st.code(email_subject, language="text")
    
    st.subheader("郵件正文：")
    st.code(email_body, language="text")
    
    st.info("💡 **專業建議**：發送郵件時，建議同步附上目前的 TN 模擬曲線圖表，能有效縮短供應商內部評估時間 。")