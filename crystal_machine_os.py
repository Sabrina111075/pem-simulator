# -*- coding: utf-8 -*-
import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import core_engine

# 設置寬螢幕模式
st.set_page_config(layout="wide")

st.title("🔮 Crystal-machine 語意作業系統")
st.write("---")

# 載入核心數據與狀態空間
EKG = core_engine.build_enterprise_graph_from_excel()
EKG, alerts = core_engine.execute_reasoning(EKG)

highlight_nodes = set()
highlight_edges = set()

top_col1, top_col2 = st.columns([11, 10])

with top_col2:
    st.subheader("📋 智能語意問答 (S-Path-RAG)")
    target_id = st.selectbox(
        "請選擇要聚焦分析的銷貨訂單編號：",
        options=["O1001", "O1002", "O1003"],
        index=0
    )
    
    # 【安全高亮因果鏈演算法】
    if target_id in EKG:
        highlight_nodes.add(target_id)
        for predecessor in list(EKG.predecessors(target_id)):
            if predecessor in EKG:
                highlight_nodes.add(predecessor)
                highlight_edges.add((predecessor, target_id))
            
        descendants = nx.descendants(EKG, target_id)
        for d_node in descendants:
            if d_node in EKG:
                highlight_nodes.add(d_node)
        
        # 安全掃描關係連線
        for u, v, d in list(EKG.edges(data=True)):
            if u in EKG and v in EKG:
                if d.get("relation") == "triggers_alarm" and (v in highlight_nodes or u in highlight_nodes):
                    highlight_nodes.add(u)
                    highlight_nodes.add(v)
                    highlight_edges.add((u, v))

        for u, v in list(EKG.edges()):
            if u in highlight_nodes and v in highlight_nodes:
                highlight_edges.add((u, v))

# 🎯 將 Python set 轉換為純字串，方便直接傳遞給前端 JavaScript 判斷
js_highlight_nodes_string = ",".join([str(n) for n in highlight_nodes])

# 提取當前焦點鏈數據做成橫向圖例
current_customer = "無關聯"
current_order = f"{target_id}"
current_product = "無關聯"
current_materials = []
current_suppliers = []

for node in highlight_nodes:
    if node in EKG:
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

with top_col1:
    st.subheader("🚨 企業即時語意預警 (規則本體)")
    if alerts:
        for alert in alerts:
            if alert["level"] == "Danger":
                st.error(alert["msg"])
            elif alert["level"] == "Warning":
                st.warning(alert["msg"])
    else:
        st.success("✅ 目前系統動態運作健全，未偵測到任何超限 Alarm。")

    st.write("---")
    st.subheader("📊 供應鏈關鍵狀態指標")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric(label="📦 關鍵晶片 M002 庫存", value="10 顆", delta="-30 顆 (低於安全水位)", delta_color="inverse")
    with kpi_col2:
        st.metric(label="🏭 晶圓廠 S002 交期", value="18 天", delta="+3 天 (超出標準)", delta_color="inverse")
    with kpi_col3:
        st.metric(label="📋 受波及銷貨訂單", value="2 筆", delta="O1001, O1002", delta_color="off")

with top_col2:
    try:
        report = core_engine.path_reasoning_query(EKG, target_id)
        st.info(report)
    except Exception as e:
        st.warning(f"❌ 核心引擎推理提示：無法生成詳細報告。原因：{e}")
    st.success(f"🎯 目前下方圖譜已為您即時聚焦高亮 【 {target_id} 】 的因果依賴鏈。")

st.write("---")
st.subheader(f"🌐 圖譜世界模型視覺圖例 (依據 {target_id} 動態對照)")
full_lg_col1, full_lg_col2, full_lg_col3, full_lg_col4, full_lg_col5 = st.columns(5)
full_lg_col1.markdown(f"<div style='padding:16px 12px; text-align:center; background-color:#97C2FC; border-radius:8px; color:black; min-height:120px; box-shadow: 2px 2px 6px #cccccc;'><div style='font-size:15px; font-weight:bold; opacity:0.85; letter-spacing:1px;'>👤 客戶 (Customer)</div><div style='font-size:18px; font-weight:900; margin-top:14px; line-height:1.4;'>{current_customer}</div></div>", unsafe_allow_html=True)
full_lg_col2.markdown(f"<div style='padding:16px 12px; text-align:center; background-color:#FB7E81; border-radius:8px; color:black; min-height:120px; box-shadow: 2px 2px 6px #cccccc;'><div style='font-size:15px; font-weight:bold; opacity:0.85; letter-spacing:1px;'>📄 訂單 (Order)</div><div style='font-size:20px; font-weight:900; margin-top:14px; line-height:1.4;'>{current_order}</div></div>", unsafe_allow_html=True)
full_lg_col3.markdown(f"<div style='padding:16px 12px; text-align:center; background-color:#FFD21E; border-radius:8px; color:black; min-height:120px; box-shadow: 2px 2px 6px #cccccc;'><div style='font-size:15px; font-weight:bold; opacity:0.85; letter-spacing:1px;'>🎁 產品 (Product)</div><div style='font-size:18px; font-weight:900; margin-top:14px; line-height:1.4;'>{current_product}</div></div>", unsafe_allow_html=True)
full_lg_col4.markdown(f"<div style='padding:16px 12px; text-align:center; background-color:#91E3B7; border-radius:8px; color:black; min-height:120px; box-shadow: 2px 2px 6px #cccccc;'><div style='font-size:15px; font-weight:bold; opacity:0.85; letter-spacing:1px;'>🔑 物料 (Material)</div><div style='font-size:16px; font-weight:900; margin-top:12px; line-height:1.4;'>{current_material_str}</div></div>", unsafe_allow_html=True)
full_lg_col5.markdown(f"<div style='padding:16px 12px; text-align:center; background-color:#C2FABC; border-radius:8px; color:black; min-height:120px; box-shadow: 2px 2px 6px #cccccc;'><div style='font-size:15px; font-weight:bold; opacity:0.85; letter-spacing:1px;'>🏭 供應商 (Supplier)</div><div style='font-size:16px; font-weight:900; margin-top:12px; line-height:1.4;'>{current_supplier_str}</div></div>", unsafe_allow_html=True)

st.write("---")
st.subheader(f"🗺️ 企業世界模型 (當前聚焦分析：{target_id})")

pv_net = Network(height="700px", width="100%", notebook=False, directed=True)

color_map = {
    "Customer": "#97C2FC", "Order": "#FB7E81", "Product": "#FFD21E",
    "Material": "#91E3B7", "Supplier": "#C2FABC", "Alarm": "#FF4500"
}

# 繪製節點 (精細化尺寸比例校正)
for node, data in EKG.nodes(data=True):
    node_type = data.get("type", "Material")
    
    if node_type == "Alarm":
        label = "⚠️ 異常心跳警報"
        title = data.get("name", node)
    else:
        label = f"{node}\n({data.get('name')})" if "name" in data else node
        title = f"類型: {node_type}\n代號: {node}"

    if node in highlight_nodes:
        color = color_map.get(node_type, "#97C2FC")
        # 💥 優化點：顯著放大高亮警報節點 (55)，一般焦點節點維持 35
        size = 55 if node_type == "Alarm" else 35
        border_width = 3.5 if node_type == "Alarm" else 2.5
        font_config = {"size": 15, "face": "Microsoft JhengHei", "strokeWidth": 3, "strokeColor": "#ffffff"}
        if node_type == "Alarm":
            font_config["color"] = "#FF4500"
            font_config["size"] = 16
    else:
        # 💥 優化點：大幅弱化、淡化非高亮節點，縮小至 14，且使用 rgba 透明度
        color = "rgba(225, 225, 225, 0.35)"
        size = 14
        border_width = 1
        font_config = {"size": 9, "face": "Microsoft JhengHei", "color": "rgba(180, 180, 180, 0.4)"}
        
    pv_net.add_node(node, label=label, title=title, color=color, size=size, borderWidth=border_width, font=font_config)

# 繪製連線
for u, v, data in EKG.edges(data=True):
    relation_label = data.get("relation", "")
    if (u, v) in highlight_edges:
        edge_color = "#FF4500" if relation_label == "triggers_alarm" else "#FB7E81"
        edge_width = 4.0 if relation_label == "triggers_alarm" else 3.0
        font_style = {"size": 12, "align": "top", "color": edge_color, "face": "Microsoft JhengHei"}
    else:
        # 💥 優化點：連非焦點連線也進行淡化
        edge_color = "rgba(230, 230, 230, 0.25)"
        edge_width = 0.8
        font_style = {"size": 0, "align": "top", "color": "rgba(0,0,0,0)"}
        
    pv_net.add_edge(u, v, label=relation_label, width=edge_width, color=edge_color, font=font_style)

# 設置物理引擎 (稍微拉開間距，給予大圓圈發揮空間)
pv_net.set_options("""
var options = {
  "physics": {
    "barnesHut": { "gravitationalConstant": -2600, "centralGravity": 0.12, "springLength": 200, "springConstant": 0.03, "damping": 0.28, "avoidOverlap": 1 },
    "minVelocity": 0.75
  },
  "edges": { "smooth": { "type": "discrete", "forceDirection": "none" } }
}
""")

try:
    pv_net.save_graph("pyvis_graph.html")
    with open("pyvis_graph.html", "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # 💥 【 Canvas 特效增強】加大警報圈半徑，加強脈搏擴散震盪幅度和粗細
    heartbeat_css_js = f"""
    <script>
        function startHeartbeatEngine() {{
            if (typeof network !== 'undefined' && network !== null) {{
                var pulseDirection = 1;
                var pulseScale = 0;
                
                var rawHighLights = "{js_highlight_nodes_string}";
                var activeHighLights = rawHighLights ? rawHighLights.split(",") : [];
                
                network.on("beforeDrawing", function (ctx) {{
                    // 💥 調整脈搏起伏範圍，讓擴散圈動能更明顯 (0 到 14 區間震盪)
                    pulseScale += 0.22 * pulseDirection;
                    if (pulseScale > 14 || pulseScale < 0) {{ pulseDirection *= -1; }}
                    
                    var allPositions = network.getPositions();
                    
                    for (var nodeId in allPositions) {{
                        if (nodeId.indexOf("ALARM_") === 0 && activeHighLights.includes(nodeId)) {{
                            var pos = allPositions[nodeId];
                            if (pos) {{
                                // 第一圈核心脈搏：線條加粗，顏色更飽和
                                ctx.strokeStyle = 'rgba(255, 69, 0, 0.8)';
                                ctx.lineWidth = 3.5;
                                ctx.beginPath();
                                // 基底半徑隨節點加大調整為 38
                                ctx.arc(pos.x, pos.y, 38 + pulseScale, 0, 2 * Math.PI);
                                ctx.stroke();
                                
                                // 第二圈外圍餘波：漣漪擴散更遠
                                ctx.strokeStyle = 'rgba(255, 140, 0, 0.35)';
                                ctx.lineWidth = 1.8;
                                ctx.beginPath();
                                ctx.arc(pos.x, pos.y, 44 + (pulseScale * 1.4), 0, 2 * Math.PI);
                                ctx.stroke();
                            }}
                        }}
                    }}
                }});
                
                setInterval(function() {{ 
                    try {{ network.redraw(); }} catch(e){{}} 
                }}, 35); // 稍微加快重繪頻率 (35ms)，讓呼吸感更緊湊真實
                
                console.log("💓 強烈視覺化心跳引擎已就緒。");
            }} else {{
                setTimeout(startHeartbeatEngine, 150);
            }}
        }}
        window.addEventListener('load', startHeartbeatEngine);
        setTimeout(startHeartbeatEngine, 400);
    </script>
    """
    html_content = html_content.replace("</body>", heartbeat_css_js + "</body>")
    components.html(html_content, height=750)
except Exception as e:
    st.error(f"❌ 圖譜渲染失敗：{e}")