---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范：正式 frontmatter 仅入正式目录，EXEMPT-ZONE-FM）：doc_type=feature_design · owner=ZephyrAlpha-Owner · status=draft · version=1.0.0 · date=2026-08-28 · topic=industry_graph_frontend · scope=产业链/供应链图谱前端可视化（迁入 design_memos 时此节翻回正式 frontmatter，ttl 翻回 permanent）。
>
> **暂存说明**：本稿暂存 `docs/_working/`。数据底座已由长城任务 INDUSTRY-GRAPH-001 建成（PostgreSQL depgraph 图谱域 ig_* 七表 + 58,029 条供应链边 + 686 条产业链 + 81M 字符语料），本文档为前端追加功能的施工依据。

# 产业链/供应链图谱 前端功能设计

## 1. 背景与定位

### 1.1 数据底座现状（2026-08-28 验收）

| 资产 | 规模 | 表 |
|---|---|---|
| 产业链 | 686 条 | `ig_chain` |
| 环节节点 | 2,911 个（上/中/下游/设备/材料等） | `ig_node` |
| 环节结构边 | 1,133 条 | `ig_edge` |
| 环节↔公司映射 | 11,075 条（0.85 互证 801 条 / 0.6 自动 10,274 条） | `ig_node_company` |
| 公司级供应链边 | 58,029 条（三证据源，1,980 条多源互证） | `ig_company_edge` |
| 公司年度指标 | 5 项 × 23.6 万条（客户集中度 HHI/Top1/Top5、客户稳定性、供应链韧性） | `ig_company_metric` |
| 源文档登记 | 1,970 份有效（含 OCR/提取状态、去重组） | `ig_document` |
| 语料 | 81M 字符，manifest.jsonl 就绪 | `E:\数据下载\产业链数据_P2语料` |

### 1.2 定位

- 接入现有 Panel 前端（`src/zephyr/frontend/dashboard/app_panel.py`，端口 5006），归属**研究**导航组，新增"图谱"页（或"产业链"页，命名施工时定）。
- 遵循 G1 深色定稿（页面 #1A1B1D / 卡片 #383838 / 图表 #2B2B2B）、A股红涨绿跌、ⓝ hover 注解收纳、减色原则。
- 数据访问只读：`get_depgraph_pg_connection(read_only=True)`，禁止写路径。
- 消灭黑箱原则：所有数字可追溯到 `ig_document` 源文档（证据链可见）。

## 2. 页面功能内容

### 2.1 视图一：产业链浏览器

| 区块 | 内容 | 数据源 |
|---|---|---|
| 链清单（左栏） | 686 条链可搜索/按 category 分组；显示环节-公司数排序 | `ig_chain` + 聚合 |
| 链详情（主区） | 流向图：原材料→上游→中游→下游（含设备/材料侧挂），每环节卡片列出映射公司（代码+角色+置信度色点：0.85 绿 / 0.6 灰） | `ig_node`/`ig_edge`/`ig_node_company` |
| 公司卡（点击弹出） | 该公司在该链的证据（来源文档标题）+ 跳转视图二 | `evidence_text`/`source_doc` |
| 版本年标 | 链的 version_year 展示，多版本链可切换年份 | `ig_chain.version_year` |

### 2.2 视图二：供应链 ego 网络

| 区块 | 内容 | 数据源 |
|---|---|---|
| 公司搜索框 | 输入代码/简称（stock_basic 补全） | ClickHouse `c1_market.stock_basic` |
| ego 网络图 | 中心为该公司；上方=供应商（from）、下方=客户（to）；边宽=weight（销售额占比/合作次数），边标=证据源徽标（483/匹配名单/J88，多源共现加粗） | `ig_company_edge` |
| 年份滑块 | 2001-2025 逐年回放关系变迁 | `ig_company_edge.year` |
| 非上市对手方 | to_symbol='' 的客户以名称节点展示（灰色，标注"非上市"） | `to_name` |
| 预警带 | top1_ratio>30% 时中心节点红边警示 + ⓘ 说明"大客户依赖" | `ig_company_metric` |

### 2.3 视图三：公司供应链指标卡

| 区块 | 内容 | 数据源 |
|---|---|---|
| 五项指标年度序列 | 客户 HHI、Top1、Top5、稳定性、韧性 2000-2025 折线（hover 读数） | `ig_company_metric` |
| 同业分位 | 指标在全 A 的年度分位数（实时聚合） | 同上 |
| 预警清单 | 最新年 top1>30% 的 704 家名单（可筛选行业） | 同上 |

### 2.4 视图四：语料与问答（依赖 RAG 检索层，并行施工）

| 区块 | 内容 | 数据源 |
|---|---|---|
| 文档浏览器 | 1,970 份文档登记表（类型/年份/机构/提取状态），点击看提取文本 | `ig_document` + 语料文件 |
| 语义问答框 | 自然语言提问 → top-k 语料块 + 来源引用（RAG 检索层提供） | 向量索引（施工中文 task B） |

### 2.5 视图五：QMT 文件桥健康监控（2026-08-27 已建于旧仪表盘，本设计原样迁入）

> **迁入说明**：本视图已在旧仪表盘（app_panel.py "QMT桥健康" Tab）建成并验证（commits `b907bfbe` 健康API / `a8209eb3dd` 面板组件 / `8f164400f4` 启动器自动装配，44/44 相关单测绿）。新仪表盘施工时**整体迁移组件与接线模式**，无需重新设计；数据端零施工（纯消费 ex_core 健康端点）。

| 区块 | 内容 | 数据源 |
|---|---|---|
| 总状态横幅 | 文件桥整体三级状态（ok 绿● / degraded 黄▲ / down 红■）+ 检查时刻 | `QmtFileBridgeAssembly.health_check()` 聚合端点 |
| 组件卡片网格 | broker_sim/broker_real（导出延迟/在途挂单/持仓数/可用资金）、queue_qmt_*（待发/已发/失败）、quote_sim/quote_real（行情文件延迟/新鲜度）；down/degraded 时 detail 直给排障原因 | 同上 `components` 子表 |
| 周期刷新 | 3 秒 `pn.state.add_periodic_callback`（全库首例，与柜台同步间隔对齐） | — |
| 空态降级 | assembly 未注入/异常 → "未装配"卡片（fail-closed，不炸面板） | — |

**组件资产**（直接迁移）：
- 组件：`src/zephyr/frontend/dashboard/components/qmt_bridge_health.py`（ComponentHealth/QmtBridgeHealthData + fetch fail-closed + render 三级映射）
- 健康端点：`QmtFileBridgeQuoteProvider.health_check()`、`check_broker_health()`、`LocalOrderQueue.health_check()`、`Assembly.health_check()`
- 蓝图：`docs/03_modules/_domain_frontend/blueprint_qmt_bridge_health.md`（阈值归属后端、3 秒刷新裁定、fail-closed 约定）
- 接线模式：启动器自动装配 `qmt_auto_assemble`（默认仅模拟环境，实盘留开关）

**阈值语义**（后端真源，前端只读不另立）：行情新鲜=10s、导出新鲜=60s、degraded 窗口=300s；午休/收盘后行情不新鲜属预期降级而非故障。

## 3. 分期施工

| 期 | 范围 | 验收 |
|---|---|---|
| MVP（P1） | 视图一 + 视图二（静态查询，无年份动画） | 光伏链可浏览环节与公司；宁德时代 ego 网可见德方纳米等真实供应商 |
| P2 | 视图三 + 年份滑块 + 预警清单 | 704 家依赖型公司清单可筛 |
| P3 | 视图四（语料浏览器 + RAG 问答） | 提问"硅料环节有哪些公司"可返回带引用的答案 |
| 并行 | 视图五（QMT 桥健康监控） | 旧仪表盘已验收（2026-08-27）；新仪表盘迁移后模拟环境 broker/quote 绿卡可见 |

## 4. 技术约束

- 前端组件复用现有 Panel 组件库；网络图用 Plotly `scatter`+`annotations` 或 `networkx` 布局，**不引入新 JS 框架**（避免 Electron/Tauri 打包复杂化，符合桌面化取向）。
- 所有查询走只读角色；聚合 SQL 落 `src/zephyr/frontend/` 对应数据访问层，禁止裸 SQL 散点。
- 空状态规范（G4）：无数据链/无关系公司显示统一骨架，0 值一律 N/A。
- 版权边界：源文档与语料仅内部研究用，前端不提供原文下载按钮，仅预览片段。

## 5. 与量化主线的衔接

- 视图二/三 是**供应链 lead-lag 传导因子**（回测施工中文 task A）的可视化载体：因子持仓可叠加显示在 ego 网络节点上。
- 环节映射（0.85 互证子集）是**主题联动监控**的原料：同环节股票异动联动提示。
- 大客户依赖预警（top1>30%）后续接入风控引擎 risk_limit 候选规则。
