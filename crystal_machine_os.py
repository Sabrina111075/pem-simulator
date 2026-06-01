# -*- coding: utf-8 -*-
import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import core_engine

# =================================#########
# # 【核心防禦 1】必須是全檔案第一個 Streamlit 命令！
# =================================#########
st.set_page_config(layout="wide")

# 初始化全域受控的聚焦訂單
if "target_id" not in st.session_state:
    st.session_state.target_id = "O1001"

# 統一由全域受控的 Session State 賦值給當前 target_id 變數
target_id = st.session_state.target_id

st.title("🔮 Crystal-machine 語意作業系統")
st.write("---")

# ##########################################
# # 2. 載入核心數據
# ##########################################
EKG = core_engine.build_enterprise_graph_from_excel()
_, alerts = core_engine.execute_reasoning(EKG)

# ==========================================
# # 頂層核心變數控管
# ==========================================
highlight_nodes = set()
highlight_edges = set()

top_col1, top_col2 = st.columns([11, 10])

with top_col2:
    st.subheader("🤖 智能語意問答 (S-Path-RAG)")
    
    order_options = ["O1001", "O1002", "O1003"]
    
    # 確保當前 target_id 在選項中，防止防禦性溢出
    try:
        current_index = order_options.index(st.session_state.target_id)
    except ValueError:
        current_index = 0

    # ⭕ 完美連動解法：將 key 直接命名為 "target_id"
    # 當使用者切換選項時，Streamlit 會將新值寫入 st.session_state.target_id 並自動從頭重跑 app.py
    st.selectbox(
        "請選擇要聚焦分析的銷貨訂單編號：",
        options=order_options,
        index=current_index,
        key="target_id"
    )

# # 計算當前訂單的動態因果鏈（使用最新被選取的 target_id）
if target_id in EKG:
    highlight_nodes.add(target_id)
    for predecessor in EKG.predecessors(target_id):
        highlight_nodes.add(predecessor)
        highlight_edges.add((predecessor, target_id))
    
    descendants = nx.descendants(EKG, target_id)
    highlight_nodes.update(descendants)
    
    for u, v in EKG.edges():
        if u in highlight_nodes and v in highlight_nodes:
            highlight_edges.add((u, v))

# ==========================================
# # 【動態解析】提取當前聚焦鏈的真實對照數據
# ==========================================
current_customer = "無關聯"
current_order = f"{target_id}"
current_product = "無關聯"
current_materials = []
current_suppliers = []

for node in highlight_nodes:
    node_data = EKG.nodes[node]
    node_type = node_data.get("type")
    node_name = node_data.get("name", "")
    
    if node_type == "Customer":
        current_customer = f"{node} {node_name}"
    elif node_type == "Product":
        current_product = f"{node} {node_name}"
    elif node_type == "Material":
        current_materials.append(f"{node} {node_name}")
    elif node_type == "Supplier":
        current_suppliers.append(f"{node} {node_name}")

current_material_str = "、".join(current_materials) if current_materials else "無關聯"
current_supplier_str = "、".join(current_suppliers) if current_suppliers else "無關聯"

# ==========================================
# # 上半段左右並排：警報/指標 vs 智能報告
# ==========================================
with top_col1:
    st.subheader("🚨 企業即時語意預警 (規則本體)")
    for alert in alerts:
        if alert["level"] == "Danger":
            st.error(alert["msg"])
        elif alert["level"] == "Warning":
            st.warning(alert["msg"])
            
    st.write("---")
    
    st.subheader("📊 供應鏈關鍵狀態指標")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric(label="📦 關鍵晶片 M002 庫存", value="10 顆", delta="-30 顆 (低於安全水位)", delta_color="inverse")
    with kpi_col2:
        st.metric(label="🏭 晶圓廠 S002 交期", value="18 天", delta="+3 天 (超出標準)", delta_color="inverse")
    with kpi_col3:
        st.metric(label="📋 受波及銷貨訂單", value="2 筆", delta="O1001, O1002")

with top_col2:
    try:
        report = core_engine.path_reasoning_query(EKG, target_id)
        st.info(report)
    except Exception as e:
        st.warning(f"❌ 核心引擎推理提示：無法為 {target_id} 產生詳細文字報告。原因：{e}")
        
    st.success(f"🎯 目前下方圖譜已為您即時聚焦高亮 【 {target_id} 】 的因果依賴鏈。")

# ==========================================
# # 中段突破：獨立於欄位之外，撐滿 100% 左右對齊的大圖例
# ==========================================
st.write("---")
st.subheader(f"🖼️ 圖譜世界模型視覺圖例 (依據 {target_id} 動態對照)")

full_lg_col1, full_lg_col2, full_lg_col3, full_lg_col4, full_lg_col5 = st.columns(5)

with full_lg_col1:
    st.markdown(f"""
    <div style='padding:16px 12px; text-align:center; background-color:#97C2FC; border-radius:8px; color:black; min-height:120px; box-shadow: 2px 2px 6px #cccccc;'>
        <div style='font-size:15px; font-weight:bold; opacity:0.85; letter-spacing:1px;'>👤 客戶 (Customer)</div>
        <div style='font-size:18px; font-weight:900; margin-top:14px; line-height:1.4;'>{current_customer}</div>
    </div>
    """, unsafe_allow_html=True)

with full_lg_col2:
    st.markdown(f"""
    <div style='padding:16px 12px; text-align:center; background-color:#FB7E81; border-radius:8px; color:black; min-height:120px; box-shadow: 2px 2px 6px #cccccc;'>
        <div style='font-size:15px; font-weight:bold; opacity:0.85; letter-spacing:1px;'>📄 訂單 (Order)</div>
        <div style='font-size:20px; font-weight:900; margin-top:14px; line-height:1.4;'>{current_order}</div>
    </div>
    """, unsafe_allow_html=True)

with full_lg_col3:
    st.markdown(f"""
    <div style='padding:16px 12px; text-align:center; background-color:#FFD21E; border-radius:8px; color:black; min-height:120px; box-shadow: 2px 2px 6px #cccccc;'>
        <div style='font-size:15px; font-weight:bold; opacity:0.85; letter-spacing:1px;'>📦 產品 (Product)</div>
        <div style='font-size:18px; font-weight:900; margin-top:14px; line-height:1.4;'>{current_product}</div>
    </div>
    """, unsafe_allow_html=True)

with full_lg_col4:
    st.markdown(f"""
    <div style='padding:16px 12px; text-align:center; background-color:#91E3B7; border-radius:8px; color:black; min-height:120px; box-shadow: 2px 2px 6px #cccccc;'>
        <div style='font-size:15px; font-weight:bold; opacity:0.85; letter-spacing:1px;'>🔩 物料 (Material)</div>
        <div style='font-size:16px; font-weight:900; margin-top:12px; line-height:1.4;'>{current_material_str}</div>
    </div>
    """, unsafe_allow_html=True)

with full_lg_col5:
    st.markdown(f"""
    <div style='padding:16px 12px; text-align:center; background-color:#C2FABC; border-radius:8px; color:black; min-height:120px; box-shadow: 2px 2px 6px #cccccc;'>
        <div style='font-size:15px; font-weight:bold; opacity:0.85; letter-spacing:1px;'>🏭 供應商 (Supplier)</div>
        <div style='font-size:16px; font-weight:900; margin-top:12px; line-height:1.4;'>{current_supplier_str}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# ==========================================
# # 下半段：動態聯動高亮圖譜 (100% 全景寬螢幕)
# ==========================================
st.subheader(f"🌐 企業世界模型 (當前聚焦分析：{target_id})")

pv_net = Network(height="700px", width="100%", notebook=False, directed=True)

color_map = {
    "Customer": "#97C2FC",
    "Order": "#FB7E81",
    "Product": "#FFD21E",
    "Material": "#91E3B7",
    "Supplier": "#C2FABC"
}

# 繪製節點
for node, data in EKG.nodes(data=True):
    node_type = data.get("type", "Material")
    label = f"{node}\n({data.get('name', '')})" if "name" in data else node
    
    if node in highlight_nodes:
        color = color_map.get(node_type, "#97C2FC")
        size = 38
        border_width = 4
        font_config = {"size": 17, "face": "Microsoft JhengHei", "strokeWidth": 3, "strokeColor": "#ffffff"}
    else:
        color = "#E0E0E0"
        size = 25
        border_width = 1
        font_config = {"size": 12, "face": "Microsoft JhengHei", "color": "#A0A0A0"}
        
    pv_net.add_node(node, label=label, color=color, size=size, borderWidth=border_width, font=font_config)

# 繪製連線
for u, v, data in EKG.edges(data=True):
    if (u, v) in highlight_edges:
        edge_color = "#FF4500"
        edge_width = 4
        edge_label = data.get("relation", "")
        font_style = {"size": 13, "align": "top", "color": "#FF4500", "face": "Microsoft JhengHei"}
    else:
        edge_color = "#D3D3D3"
        edge_width = 1
        edge_label = ""
        font_style = {"size": 9, "align": "top", "color": "#D3D3D3"}
        
    pv_net.add_edge(u, v, label=edge_label, width=edge_width, color=edge_color, font=font_style)

# 物理排斥力設定
pv_net.set_options("""
var options = {
    "physics": {
        "barnesHut": { "gravitationalConstant": -12000, "centralGravity": 0.2, "springLength": 160, "springConstant": 0.05 },
        "minVelocity": 0.75
    },
    "edges": { "smooth": { "type": "cubicBezier", "forceDirection": "none" } }
}
""")

try:
    pv_net.save_graph("pyvis_graph.html")
    with open("pyvis_graph.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=730)
except Exception as e:
    st.error(f"❌ 圖譜渲染失敗：{e}")