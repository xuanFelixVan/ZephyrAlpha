---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范：正式 frontmatter 仅入正式目录，EXEMPT-ZONE-FM）：doc_type=feature_design · owner=ZephyrAlpha-Owner · status=draft · version=1.1.0 · date=2026-08-28 · topic=industry_graph_frontend · scope=产业链/供应链图谱前端可视化（迁入 design_memos 时此节翻回正式 frontmatter，ttl 翻回 permanent）。
>
> **暂存说明**：本稿暂存 `docs/_working/`。数据底座已由长城任务 INDUSTRY-GRAPH-001 建成（PostgreSQL depgraph 图谱域 ig_* 七表 + 58,029 条供应链边 + 686 条产业链 + 81M 字符语料），本文档为前端追加功能的施工依据。
>
> **v1.1.0 定位更新（2026-08-28 Owner 裁定）**：本文档全部内容**并入新仪表盘设计**，后续统一在新仪表盘施工；§6 记录的已落地功能（旧仪表盘 app_panel 图谱语料 Tab + 主题联动监控脚本）视为先行验证，新仪表盘施工时按其结论取舍迁移。
>
> **结案审查（2026-08-28 复核）**：未结案（数据底座已完工，前端视图待施工）
> - 已实证：`scripts/industry_graph/` 16 脚本在码（DDL/RAG 索引/theme_linkage_monitor/backtest_supply_leadlag/p0-p3 管线全族）；ig_* 七表规模与本稿 §1.1 一致。
> - 未结案项：视图一/二/三未施工，按 v1.1.0 裁定并入新仪表盘统一施工；本稿保留为施工依据。

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

- 视图二/三 是**供应链 lead-lag 传导因子**的可视化载体（2026-08-28 回测已**证伪**：月度 IC=-0.029/周度 IC=-0.012，不进因子框架，仅留脚本 `scripts/industry_graph/backtest_supply_leadlag.py` 可复现；前视自检 1 条 MEDIUM 经复核为面板数据误报）。
- 环节映射（0.85 互证子集）是**主题联动监控**的原料：同环节股票异动联动提示。
- 大客户依赖预警（top1>30%）后续接入风控引擎 risk_limit 候选规则。

## 6. 已落地功能（2026-08-28，旧仪表盘 app_panel，先行验证）

> 以下功能已施工完成并验证，**并入新仪表盘设计时按本节结论取舍**。

### 6.1 图谱语料 Tab（旧仪表盘第 13 个 Tab，已上线）

- 组件 `src/zephyr/frontend/dashboard/components/industry_graph.py`，app_panel 注册"图谱语料"Tab。
- 四区块：KPI 卡（文档 2110 / 全景图 PDF / 研报 / 图谱 / 已提取文本）、文档浏览器（静态表前 200 条 + 文档 ID 输入预览提取文本）、RAG 语料问答、主题联动日报表。
- RAG 检索层（task B 已建成）：76,112 语料块 × bge-small-zh 512 维本地向量（`E:\数据下载\产业链数据_P2语料\chunks.sqlite` + `embeddings.npy`），问答实证命中"光伏硅料四大天王"原文；脚本 `scripts/industry_graph/rag_build_index.py` / `rag_query.py`。

### 6.2 主题联动监控（日报级 MVP，已产出）

- 脚本 `scripts/industry_graph/theme_linkage_monitor.py`：0.85 互证子集（24 链 / 523 家）× 最新完整交易日行情 → 每链涨家占比、均涨幅、**联动强度**（20 日平均成对相关性）、领涨股；CSV 落 `.runtime/industry_graph/theme_linkage_daily.csv` 供前端读取。
- 实证（2026-08-25）：可控核聚变 100% 上涨/联动 0.61；光模块链联动 0.85 齐跌——高联动主题齐涨齐跌，监控有效。
- 后续可接 QMT 盘中升级为实时版、接定时任务每日产出。

### 6.3 施工教训（新仪表盘必须规避）

| 坑 | 现象 | 规避方案 |
|---|---|---|
| 大 Tabulator 全量渲染 | 2,000+ 行带 header_filters 的 Tabulator 在 dynamic Tab 激活时主线程永久卡死 | 大表一律静态表/服务端分页；交互表格限制单页行数 |
| 后台线程加载 torch 模型 | 与 Bokeh 事件循环并发有致死锁风险 | 模型加载放首次用户触发时同步执行（约 30 秒，之后秒回） |
| 行情"最新日"入库中途 | max(trade_date) 当日仅个位数股票有数据，全表统计归零 | 覆盖率 <80% 峰值时自动回退上一完整交易日 |
| kline_daily 重复行 | 同 (symbol, trade_date) 多数据源重复导致 reindex 报错 | 拉数后 drop_duplicates(symbol, trade_date) |
| 浏览器子代理验证 | 其截图存档跨会话污染，出现别应用残留帧，内容描述不可信 | 前端验收以探针数据 + Python 层验证为准，关键页 Owner 肉眼复核 |

### 6.4 新仪表盘待施工（本文档 §2 四视图）

- 视图一 产业链浏览器、视图二 供应链 ego 网络、视图三 公司指标卡：未施工，待新仪表盘统一实施。
- 视图四 语料问答：已在旧仪表盘验证（§6.1），新仪表盘按 §6.3 教训迁移（静态表分页 + 触发式模型加载）。
