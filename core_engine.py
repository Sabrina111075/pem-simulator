import pandas as pd

# ==================== 基礎數據源定義 ====================
df_orders_1 = pd.DataFrame({
    "訂單編號": ["O1001"],
    "客戶名稱": ["台灣電子 A公司"],
    "需求產品": ["高階控制器 (P001)"],
    "交付狀態": ["❌ 預期延誤 (12天)"],
    "核心主因": ["上游物料缺料，供應商交期過長"]
})

df_materials_1 = pd.DataFrame({
    "物料代碼": ["M002"],
    "物料名稱": ["核心控制晶片"],
    "目前庫存": ["45 pcs"],
    "安全水位": ["150 pcs"],
    "狀態評級": ["⚠️ 庫存嚴重不足"]
})

df_suppliers_1 = pd.DataFrame({
    "供應商": ["S002 (大發晶圓廠)"],
    "採購單號": ["PO-2026-004"],
    "前置交期": ["正常 7 天 ➔ 突發 25 天"],
    "異常原因": ["產線突發氣泡缺陷，不良率暴增 8.5%"]
})

df_orders_2 = pd.DataFrame({
    "訂單編號": ["O1002"],
    "客戶名稱": ["凌雲科技"],
    "需求產品": ["標準驅動模組 (P002)"],
    "交付狀態": ["❌ 預期延誤 (5天)"],
    "核心主因": ["共用核心晶片 M002 被產線資源爭奪"]
})

df_materials_2 = pd.DataFrame({
    "物料代碼": ["M002"],
    "物料名稱": ["核心控制晶片"],
    "目前庫存": ["45 pcs"],
    "安全水位": ["150 pcs"],
    "狀態評級": ["⚠️ 庫存嚴重不足 (優先供 O1001)"]
})

df_suppliers_2 = pd.DataFrame({
    "供應商": ["S002 (大發晶圓廠)"],
    "採購單號": ["PO-2026-005"],
    "前置交期": ["等待交期回復中"],
    "異常原因": ["受大發晶圓廠不良率影響，排程整體順延"]
})


# ==================== 核心推理引擎 ====================
def infer_reasoning_chain(selected_order):
    # 安全檢查：防止選單元件傳入 None
    if not selected_order:
        return df_orders_1, df_materials_1, df_suppliers_1

    order_str = str(selected_order).strip()
    
    # 嚴格模糊包含匹配
    if "O1001" in order_str:
        return df_orders_1, df_materials_1, df_suppliers_1
        
    elif "O1002" in order_str:
        return df_orders_2, df_materials_2, df_suppliers_2
        
    else:
        # 【極致安全保底】: 不論走進哪個旁支，哪怕查無此訂單，也必須嚴格回傳 3 個 Dataframe
        return df_orders_1, df_materials_1, df_suppliers_1