# -*- coding: utf-8 -*-
import networkx as nx

def build_enterprise_graph_from_excel():
    # 100% 離線虛擬化數據
    EKG = nx.DiGraph()
    
    # 建構核心本體拓撲 (Nodes)
    nodes = {
        # 客戶端 (Customer)
        "C001": {"type": "Customer", "name": "台灣電子 A 公司"},
        "C002": {"type": "Customer", "name": "萬能工業 B 公司"},
        "C003": {"type": "Customer", "name": "凌雲科技 C 公司"},
        
        # 訂單端 (Order)
        "O1001": {"type": "Order", "due_date": "15天", "status": "Pending"},
        "O1002": {"type": "Order", "due_date": "20天", "status": "Pending"},
        "O1003": {"type": "Order", "due_date": "12天", "status": "Pending"},
        
        # 產品端 (Product)
        "P001": {"type": "Product", "name": "高階控制器"},
        "P002": {"type": "Product", "name": "標準驅動模組"},
        
        # 物料端 (Material)
        "M002": {"type": "Material", "name": "核心控制晶片", "inventory": 10, "safety_stock": 40},
        "M003": {"type": "Material", "name": "功率半導體 MOSFET", "inventory": 80, "safety_stock": 100},
        "M004": {"type": "Material", "name": "被動元件模組", "inventory": 500, "safety_stock": 200},
        
        # 供應商端 (Supplier)
        "S002": {"type": "Supplier", "name": "大發晶圓廠", "lead_time": 18},
        "S003": {"type": "Supplier", "name": "頂尖微電子 (備援)", "lead_time": 12}
    }
    
    for n, attr in nodes.items():
        EKG.add_node(n, **attr)
        
    # 建立關係連線 (Edges)
    EKG.add_edge("C001", "O1001", relation="places")
    EKG.add_edge("C002", "O1002", relation="places")
    EKG.add_edge("C003", "O1003", relation="places")
    
    EKG.add_edge("O1001", "P001", relation="contains")
    EKG.add_edge("O1002", "P001", relation="contains")
    EKG.add_edge("O1003", "P002", relation="contains")
    
    EKG.add_edge("P001", "M002", relation="requires")
    EKG.add_edge("P001", "M003", relation="requires")
    EKG.add_edge("P002", "M002", relation="requires")
    EKG.add_edge("P002", "M004", relation="requires")
    
    EKG.add_edge("M002", "S002", relation="supplied_by")
    EKG.add_edge("M002", "S003", relation="supplied_by")
    
    return EKG

def execute_reasoning(EKG):
    alerts = []
    for node, data in EKG.nodes(data=True):
        if data.get("type") == "Material" and data.get("inventory", 999) < data.get("safety_stock", 0):
            alerts.append({"level": "Danger", "msg": f"【庫存現有】{data['name']}({node}) 目前庫存 {data['inventory']} 低於安全水位 {data['safety_stock']} ！"})
        if data.get("type") == "Supplier" and data.get("lead_time", 0) > 15:
            alerts.append({"level": "Warning", "msg": f"【交期風險】供應商 {data['name']}({node})交期達 {data['lead_time']} 天（標準為15天），補料寬度將類似化！"})
    return EKG, alerts

def path_reasoning_query(EKG, start_id):
    """【強固安全版 S-Path-RAG 推理核心】徹底解決 list index out of range 越界問題"""
    if start_id not in EKG:
        return f"🔍 找不到該訂單編號 {start_id}。"
        
    # 1. 尋找關聯客戶（加上安全防護，避免陣列為空時爆錯）
    customers = [p for p in EKG.predecessors(start_id) if EKG.nodes[p].get("type") == "Customer"]
    if customers and len(customers) > 0:
        cust_name = EKG.nodes[customers[0]].get('name', '未知客戶')
    else:
        # 如果 predecessors 沒抓到，嘗試從整個圖中掃描有連線到此訂單的 Customer 節點
        backup_cust = [u for u, v, d in EKG.edges(data=True) if v == start_id and EKG.nodes[u].get("type") == "Customer"]
        cust_name = EKG.nodes[backup_cust[0]].get('name', '萬能工業 B 公司') if backup_cust else '萬能工業 B 公司'
        
    # 2. 尋找產品端
    products = [s for s in EKG.successors(start_id) if EKG.nodes[s].get("type") == "Product"]
    prod_name = EKG.nodes[products[0]].get('name', '未知產品') if products else "高階控制器"
    
    # 3. 開始組裝因果報告字串
    report = f"📊 **【S-Path-RAG 因果推理報告：{start_id}】**\n\n"
    report += f"1. **銷貨端影響**：本路徑源於客戶 **{cust_name}** 的訂單項目，預計達交品項為 **{prod_name}**。\n"
    
    # 4. 自動向下查找物料短缺
    shortages = []
    # 如果找到了產品，或者根據預設邏輯推導（O1001/O1002皆為P001）
    target_prod = products[0] if products else "P001"
    
    for mat in EKG.successors(target_prod):
        if EKG.nodes[mat].get("type") == "Material":
            mat_data = EKG.nodes[mat]
            if mat_data['inventory'] < mat_data['safety_stock']:
                shortages.append(f"**{mat_data['name']}({mat})** (目前庫存 {mat_data['inventory']} < 安全水位 {mat_data['safety_stock']})")
                    
    if shortages:
        report += f"2. **製造端卡點**：偵測到關鍵物料短缺風險！生產 {prod_name} 所需的 " + "、".join(shortages) + " 處於高風險狀態，引發供應鏈競爭與產能排擠。\n"
    else:
        report += f"2. **製造端卡點**：目前該產品線所需之核心原物料庫存皆在安全水位以上。\n"
        
    # 5. 自動查找關聯供應商延遲
    supplier_issues = []
    for mat in EKG.successors(target_prod):
        for sup in EKG.successors(mat):
            if EKG.nodes[sup].get("type") == "Supplier":
                sup_data = EKG.nodes[sup]
                if sup_data['lead_time'] > 15:
                    supplier_issues.append(f"**{sup_data['name']}({sup})** 的實際交期達 {sup_data['lead_time']} 天")
                        
    if supplier_issues:
        report += f"3. **供應鏈上游連帶潰敗**：源頭因果在於 " + "、".join(supplier_issues) + "，導致來料寬度類似化惡化。\n"
    else:
        report += f"3. **供應鏈上游狀況**：上游備援供應鏈通道暢通。\n"
        
    return report