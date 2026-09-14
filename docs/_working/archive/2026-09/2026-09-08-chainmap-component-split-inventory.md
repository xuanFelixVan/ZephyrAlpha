---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：报告/清单/记录类（既成事实记载，无待办）。处置=**软归档**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 2 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：软归档。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）




# 产业地图（chainmap）组件拆分清单 v1

> task_bound 临时文档（不入持久记忆）。触发：frontend_component_split_sop Step 1；上游=construction_workflow_sop Step 3.5 后端盘点。
> Owner 已裁定总体方案（2026-09-08 讨论）：三层缩放大图（L1 星系聚合→L2 链层列式→L3 公司面板 MVP 版）+ 左侧族→链导航 + 全局搜索。
> MVP 边界（Owner 认可）：L1 星系 + 导航 + 搜索 + 点族进 L2 + 环节公司面板；公司详情卡完整版/跨链徽章跳转/行情接入 = 二期。

## 〇、后端盘点留痕（TRAE-086 §truth_source_wiring 四步）

1. **取数清单**：
   - L1 星系：链→族聚类映射、族节点（链数/环节连接度/公司数）、族间边（跨链连接强度）、全量链清单（导航树用）；刷新节奏=数据扩建期日级，TTL 缓存 10min 足够
   - L2 链层：簇内链→环节（tier 分桶）、环节间结构边、环节公司计数
   - 环节公司面板：node→公司（symbol/名称/角色/置信度），上限 200 行
   - 搜索：链名/环节名 ILIKE + symbol 前缀落位 + 公司名（ig_company_edge 名称映射，覆盖不全如实标注）
2. **后端三查**：①api_server.py 现有 /api/ 端点——无任何 chainmap/ig_* 端点（现有=CH 行情族+battle_map+tdm+services 族）；②登记层——ig_* 七表真源在 depgraph PostgreSQL（scripts/industry_graph/apply_industry_graph_ddl.py DDL-as-Code），asset_inventory 仅登记上游语料资产；③其他端点/同功能模块——components/industry_graph.py（panel 语料浏览 Tab）不提供图谱几何数据，无重复真源。**结论：没有 → 先建后端端点**（三分支决策第③支）。
3. **三分支决策**：后端新建 4 端点（本 SOP Step 3），真源=ig_* 七表（get_depgraph_pg_connection 默认 depgraph_reader 只读角色，零写副作用）；前端零图计算、零演示数据（空态+状态提示+15s 自动重试，演示诚实纪律收紧口径）。
4. **接线验收**：ACC-F-CHAINMAP-GALAXY / -NAV / -SEARCH / -CLUSTER 四单 + tests/frontend/test_dashboard_smoke.py。

## 一、组件清单（按数据源边界+单一功能判据）

| # | 模块 id | 文件 | 功能语义 | 数据源 | 交互 | 验收单 |
|---|---|---|---|---|---|---|
| 1 | chainmap-galaxy | features/chainmap/chainmap-galaxy.js | L1 星系层：族节点+族间边画布，力导向（坐标 localStorage 缓存固化），滚轮缩放/拖动/双击重置，点族→进 L2 | /api/chainmap-galaxy | 缩放/平移/hover 高亮/点击 | ACC-F-CHAINMAP-GALAXY |
| 2 | chainmap-nav | features/chainmap/chainmap-nav.js | 左侧导航树：族→链两级，计数徽章；点族=进 L2，点链=进 L2 并聚焦该链 | /api/chainmap-galaxy（自取，后端 TTL 缓存） | 点击/展开 | ACC-F-CHAINMAP-NAV |
| 3 | chainmap-search | features/chainmap/chainmap-search.js | 顶部全局搜索：链/环节/代码/公司名 → 定位跳转 | /api/chainmap-search | 输入/下拉/Enter | ACC-F-CHAINMAP-SEARCH |
| 4 | chainmap-cluster | features/chainmap/chainmap-cluster.js | L2 链层：上中下游列式布局+环节卡片+结构边 SVG；环节点→右侧公司面板 | /api/chainmap-cluster + /api/chainmap-node | 列式浏览/点环节 | ACC-F-CHAINMAP-CLUSTER |

模块通信：仅 ZK.bus（`cm:open-cluster`/`cm:goto-chain`/`cm:view`）；画布容器各自持有（#cm-canvas-galaxy / #cm-canvas-cluster），显隐由各模块响应 `cm:view` 自控，互不摸对方 DOM；面包屑 #cm-crumb 与状态条 #cm-meta 为页面级共享槽位（pages/ 片段所有）。

## 二、API 契约（api_server.py 新增，真源 ig_* 七表）

| 端点 | 入参 | 出参核心 | 缓存 |
|---|---|---|---|
| GET /api/chainmap-galaxy | - | clusters[{id,name,n_chains,n_nodes,n_companies}] + links[{s,t,w}] + chains[{chain_id,name,cluster,n_companies}] | 进程内 TTL 600s |
| GET /api/chainmap-cluster | cid | cluster + chains[{chain_id,name,nodes[{node_id,name,tier,col,n_companies}],edges[[from,to]]}] | 进程内 TTL 600s |
| GET /api/chainmap-node | node_id | node{name,chain,tier} + companies[{symbol,name,role,confidence}] ≤200 | 不缓存（点查） |
| GET /api/chainmap-search | q | chains[]/nodes[]/symbols[] 各限 10-20 | 不缓存 |

聚类算法：链级加权图（ig_edge 跨链结构边 + ig_company_edge 去重公司边经 ig_node_company 投影到链对）→ 确定性加权标签传播 → 小簇并入最强邻居 → 控制在 ≤48 簇；族名=簇内连接度最高链名。纯 Python 无新依赖。

## 三、边界与二期

- 个股落位查询/供应链指标（原占位页演示表）：由 L2 环节公司面板+搜索承接，演示表删除
- 二期：公司详情卡（链上坐标/上下游前五/跨链徽章跳转/市值行情复用 CH）、语义聚类布局、L1 层 LLM 族名
- 页面边界声明保留（vs 板块页：横向分类 vs 纵向传导）
