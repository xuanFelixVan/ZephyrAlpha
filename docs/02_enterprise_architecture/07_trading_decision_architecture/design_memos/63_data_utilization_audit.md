---
ttl: permanent
doc_type: architecture_view
title: 业务数据资产利用率审查与施工计划
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "2.1.0"
date: 2026-08-12
topic: data_utilization_audit
scope: 07_trading_decision_architecture
related_modules:
  - schemas/categories/
  - docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml
depends_on:
  - 62_business_registry_construction
  - 15_data_feature_layer_spec
  - 16_technical_indicator_catalog
  - 26_event_driven_strategy_detail
---

# 业务数据资产利用率审查与施工计划

> 本备忘是业务数据库 103 张数据表在 design_memos 文档与 src/zephyr/ 代码层的**引用审查底稿 + 文档覆盖缺口清单 + 归档决策**。
> 性质：**审查清单 + 施工计划混合文档**，承载现状盘点、覆盖率缺口归因、分批补文档方案，供后续 AI/人逐张表补文档或归档使用。
> 管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)；与 [62_business_registry_construction](62_business_registry_construction.md) 配对——62 号建 12 业务注册表的 schema，63 号盘点 103 张表的**实际利用率与文档覆盖缺口**。
> 关联：[15_data_feature_layer_spec](15_data_feature_layer_spec.md)（数据/因子工程总纲）｜ [16_technical_indicator_catalog](16_technical_indicator_catalog.md)（技术指标目录）｜ [26_event_driven_strategy_detail](26_event_driven_strategy_detail.md)（事件驱动数据消费方）

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G63 业务数据资产利用率审查 |
| 创建 | 2026-08-10 |
| 优先级 | P2（v2.1.0 实测：数据利用率 99.0% 健康；真问题是**消费层文档覆盖** 37/103=35.9% < 80% 行业基准——规划层 17/64 号已覆盖 53 张，但策略/风控消费文档未跟进） |
| 状态 | 审查完成（v2.1.0 全量重扫核验：表数 102→103、文档 42→47 篇、真闲置 3→1 张、新增"代码零引用但规划已登记"6 张类别、§5/§6 全部数字以 git 提交态实测重算；v2.0.0 补 SetGo metadata readiness 评估排除+2026-08-11 SSDBM 最新研究可追溯；v1.9.0 补 DataHub docFreshnessInfo verifiedAtVersion 状态指纹+Google OKF v0.2 trust/provenance/attestation 模型+Freshness SLO SLI 公式+DZone freshness gap 五种管道级假新鲜失败模式+OKF Attested Computation 验证概念；v1.8.0 补 Temporal Coupling commit-size 归一化+CodeScene 三信号说明+Sum of Coupling 聚合度+min-heap Kahn 确定性排序+DFS 三色标记环路径提取+Tarjan SCC 远期路径+predict Omissions schema↔doc 共变检测+ODCS v3.1.0 版本号+DCS 弃用说明；v1.7.0 补 Temporal Coupling 隐藏依赖检测+Data Contract ODCS 概念重构+SATD 跨制品传播优先级+AI 技术债 7 类映射+Leiden 选型结论修正；v1.6.0 补 Leiden 替代 Louvain+Temporal Coupling 隐藏依赖+Doc-Freshness-Score anti-gaming+driftGuard 双信号自适应阈值+Content Freshness 多信号融合+Tessera coverage@precision+CRRF 因果回滚+CFD 累积流图+Cognitive Debt+AIGenerated Debt+Binarly 权重再分配+paired-model 双 LLM 交叉验证；v1.5.0 补 SQALE 技术债视角+Kahn 环检测+Leading/Lagging 指标区分；v1.4.0 补 Nelson Rules 误报率风险矩阵+自适应控制限思想+MTTD/MTTR 回滚效能度量；v1.3.0 补 Nelson Rules 名称修正+施工进度跟踪看板+symbol-level drift 检测+Hotelling T² 远期路径；v1.2.0 补 Model drift 漂移来源分类+Western Electric 8 异常模式+Innovation-Residual 故障归因+Detection Limit；v1.1.0 补 effort 矛盾修复+L3 主动学习分层抽样+SPC 冷启动三阶段+跨波次优先级动态重评；v1.0.0 补 SPC EWMA/CUSUM 趋势分析+CPM 关键路径识别+贝叶斯权重更新形式化+有赞调度感知差异化弃用阈值+MIN_AGE_DAYS 安全过滤；v0.9.0 补 Syntropy 编码会话级新鲜度+SITS2026 Doc-Entropy Ratio+DocPilot 两 pass 质量门+Louvain 社区发现批次验证+Preventive/Detective 双层检测；v0.8.0 补 Cascade 双重条件语义验证+消费链路主动监控+字段级血缘排除；v0.7.0 补 Milvus 乘法模型对比+DocAgent 多智能体远期路径+Consequence Ranking 批判辩护+REFORGE 漏斗+CoDe-R 双路径回退；v0.6.0 补 Kano 分类层+指数衰减新鲜度+回滚机制+努力度 rubric+多消费方冲突解决+6 轴远期路径），待补文档施工 |
| 上游 | [62_business_registry_construction](62_business_registry_construction.md)（12 注册表 schema 已定稿） |
| 下游 | [15_data_feature_layer_spec](15_data_feature_layer_spec.md) / [26_event_driven_strategy_detail](26_event_driven_strategy_detail.md) / [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) 等数据消费方 |

## 2. 背景与问题诊断

### 2.1 项目处境

- 业务数据库已建成 [schemas/categories/](../../../schemas/categories/) 下 **103 张表**的 DDL（market/fundamental/macro/cross 四大类前缀），覆盖 A 股/港股/美股/期货/期权/可转债/生猪期货/宏观经济等全品类（v2.1.0 核验：`market_stock_valuation.py` 于 2026-08-11 commit 81c7687540 新增，102→103）
- design_memos 下 47 篇编号文档（不含 [AI_review_instructions.md](AI_review_instructions.md) 辅助文件；受扫 46 篇=47 篇-本备忘自引）共约 5.24M 字符，承载交易决策架构 why 层（v2.1.0 核验：v0.2.0 时 42 篇/4.59M 字符，新增 60/61/64/65/90/91 等）
- [62_business_registry_construction](62_business_registry_construction.md) 已定稿 12 个业务注册表 schema（P0 完成 universe/benchmark/cost_model 三件套，P1 待施工 9 件套）
- 62 号 line 1715 记录 [dataflow_graph_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml) 已有 DS-001~076 共 76 条数据源登记（待 S6 改名为 data_asset_registry.yaml）
- **但** 62 号解决的是"注册表 schema"，未盘点"现有 103 张表实际有多少被 design_memos + 代码层引用"——数据利用率与文档覆盖盲区

### 2.2 核心问题（v2.1.0 全量重扫核验修正）

> **"103 张表里 102 张被代码或文档引用（利用率 99.0%），真闲置仅 1 张（`index_meta`）。文档覆盖呈三层结构：消费层（策略/风控文档显式描述用法）仅 37 张（35.9%）< 80% 行业基准——这是真问题；规划层（[17_special_trading_days_data_assets](17_special_trading_days_data_assets.md)/[64_data_source_download_spec](64_data_source_download_spec.md) 资产清单与下载规范提及）53 张；零覆盖 13 张。另有 6 张表 DDL 已建+规划已登记但代码/config/tasks 全零引用（采集未施工、消费未落地）。"**

v0.1.0 曾误判"43 张闲置"，v0.2.0 补代码层扫描修正为"3 张真闲置+61 张文档缺口"。v2.1.0（2026-08-12）以 git 提交态全量重扫，三层校验数字再次修正：

| 病灶 | v0.1.0 误判 | v0.2.0 修正 | v2.1.0 实测核验 |
|---|---|---|---|
| 总表数 | 101 | 102 | **103**（`market_stock_valuation` 2026-08-11 新增） |
| 受扫文档数 | 42 篇 | 42 篇 | **46 篇**（47 篇编号文档-本备忘自引；新增 60/61/64/65/90/91 等） |
| 数据利用率 | 57.4%（58/101） | 97.1%（99/102） | **99.0%（102/103）**——文档∪代码任一引用 |
| 真闲置表 | 43 张 | 3 张 | **1 张**（`index_meta` 文档+代码+config 全零引用） |
| 文档覆盖（英文表名任一文档命中） | 38（37.3%） | 38（37.3%） | **90（87.4%）**——但含规划层引用，口径过宽 |
| **消费层文档覆盖**（v2.1.0 新增口径） | 未区分 | 未区分 | **37（35.9%）**——非 17/64 号规划文档外的消费方文档引用，**真问题在此，与 v0.2.0 的 38 张惊人稳定** |
| 规划层文档覆盖（v2.1.0 新增口径） | 未识别 | 未识别 | **53（51.5%）**——仅 17/64 号资产清单/下载规范提及，消费用法未描述 |
| 零覆盖 | 未识别 | 61（英文上界） | **13（12.6%）**——其中 12 张代码在用（真文档缺口），1 张真闲置 |
| 代码零引用但规划已登记 | 未识别 | 未识别 | **6 张**（dividend_tax_node/index_adjustment/ipo_schedule/margin_target_adjustment/msci_adjustment/stock_valuation）——DDL+规划文档有，代码/config/tasks.yaml 全零，采集未施工 |
| P0"高价值闲置" | 8 张 | 全部 CODE_ONLY | v2.1.0 确认：批次 A 风险表代码均活跃，但**消费文档仍缺**（仅 17/64 号规划层提及）——§7 第一波施工内容不变 |
| P4 生猪期货 | "完全不涉及" | 代码 7-8 次引用 | v2.1.0 实测：3 张生猪表代码各 1 次引用（采集模板级）+规划层覆盖——维持批次 D 暂缓 |

> **v2.1.0 关键口径修正**：v0.2.0 的"文档覆盖率 37.3%"与 v2.1.0 实测的"消费层覆盖 35.9%"（37 张）在数值上高度一致——**v0.2.0 的扫描实质上测的就是消费层覆盖**（当时 17/64 号尚未提交或未含大量表引用，未污染口径）。2026-08-11 后 17/64 号提交带来 53 张规划层引用，若按"任一文档命中"口径覆盖率虚高至 87.4%，会掩盖消费层缺口。**v2.1.0 起 §5.1 以三层口径分别报告，施工目标以消费层覆盖为准**。
>
> **v0.2.0 历史数字不可复现声明**：v0.2.0 的逐表引用计数（如 `block_trade` 52 次/5 文档、`index_adjustment` 代码 17 次）以 2026-08-10 工作区未提交文件为扫描对象，2026-08-12 以 git 提交态重扫无法复现（`block_trade` 实测 7 次/2 文档，`index_adjustment` 代码 0 次）。教训：§3.4 扫描输出必须落地 CSV 快照随施工提交（dogfood 本文 §3.4 机制），否则历史审计数字无法回溯验证。v2.1.0 起 §5/§6 全部数字以本版实测为准，历史版本数字仅作演进参考。

**Data Contract 概念重构（v1.7.0 新增，参考 [soda.io 2026-06-01](https://soda.io/blog/data-contracts-vs-schema-registry) + [datus.ai 2026-06-29](https://datus.ai/blog/what-is-data-contract/) + [streamkap.com 2026-02-25](https://streamkap.com/resources-and-guides/data-contracts-streaming)）**：

> 上述"文档覆盖缺口"可进一步用 2026 年行业标准的 **Data Contract** 概念重构。[soda.io 2026-06](https://soda.io/blog/data-contracts-vs-schema-registry) 明确区分：**Schema Registry 管结构**（字段名/类型/兼容性，对应本仓库 schemas/categories/*.py DDL），**Data Contract 管行为**（schema + 语义 + 质量规则 + SLA + 所有权 + 变更管理，对应本仓库 schemas/categories DDL + design_memos 文档）。[datus.ai 2026-06-29](https://datus.ai/blog/what-is-data-contract/) 指出 2026 年主流标准为 [Open Data Contract Standard (ODCS)](https://github.com/bitol-io/open-data-contract-standard)（Linux Foundation Bitol 项目），YAML 格式，机器可校验。

**ODCS 版本与 DCS 弃用说明（v1.8.0 补入，参考 [bitol.io 2025-12-07 ODCS v3.1.0](https://bitol.io/bitol-announces-odcs-v3-1-0-stronger-smarter-and-stricter/) + [docs.datacontract.com 2026](https://docs.datacontract.com/open-data-contract-standard) + [adriennevermorel.com 2026-03-27](https://adriennevermorel.com/notes/open-data-contract-standard/)）**：

> ODCS 当前最新版本为 **v3.1.0**（2025-12-07 发布，[bitol.io 公告](https://bitol.io/bitol-announces-odcs-v3-1-0-stronger-smarter-and-stricter/)）。v3.1.0 相比 v3.0 的关键增强：(1) RFC-0013 属性间关系（foreignKey 声明，即使底层系统不强制也可定义参照完整性）；(2) 更严格的 JSON Schema 校验；(3) 可执行 SLA（schedule + automate SLA checks）；(4) 外部契约引用（RFC-0009a，跨文件 `$ref`）；(5) 内部引用快捷方式（RFC-0009b，`table.column` 语法）。v3.1.0 完全向后兼容 v3.0。另外，[datacontract.com CLI](https://docs.datacontract.com/open-data-contract-standard) 明确：旧的 **Data Contract Specification (DCS)** 格式（使用 `models`/`fields` 而非 ODCS `schema`/`properties`）已被弃用——CLI 仍接受 DCS 格式但新契约应遵循 ODCS，两支团队正在协调合并。[adriennevermorel.com 2026-03](https://adriennevermorel.com/notes/open-data-contract-standard/) 确认 ODCS 已成为 de facto 标准。本审查 §8 data_asset_registry 施工时参照 ODCS v3.1.0 六组件完整性检查清单，不引入 YAML 工具链（§9 已声明"派生产物不入 git"约束）。

**本仓库的 Data Contract 完整度映射**：

| Data Contract 六组件 | 本仓库对应 | 完整度 |
|---|---|---|
| Schema（结构） | schemas/categories/*.py DDL | ✅ 103/103 完整 |
| Semantics（语义） | design_memos 文档消费方描述 | ⚠️ 消费层 37/103（规划层 53 张仅有资产清单级语义）——本审查核心问题 |
| Quality rules（质量规则） | data_asset_registry.yaml 字段 + §7.0.4 Q score | ⚠️ 待施工（§8 关联） |
| SLA（新鲜度/可用性） | §7.0.4 timeliness 指数衰减 + §3.4 Detective 扫描 | ⚠️ 待施工 |
| Ownership（所有权） | data_asset_registry.yaml owner 字段 + frontmatter owner | ⚠️ 待登记 |
| Change management（变更管理） | §7.0.5 增量更新 + git hook + §3.4 引用漂移检测 | ⚠️ 待施工 |

**重构结论**：本审查的"补文档覆盖缺口"本质是**补全 Data Contract 的 Semantics 层**——schema 已完整（DDL 齐全），但 semantics/quality/SLA/ownership/change-management 五层缺失或待施工。v1.7.0 用 Data Contract 概念重构不改变施工计划（§7 仍按批次补文档），但为 §8 data_asset_registry 施工提供了 ODCS 标准对齐的目标——data_asset_registry 应成为每张表的 Data Contract 注册表（非仅 schema 登记），涵盖六组件。

**为何补 Data Contract 概念但不引入 ODCS 工具链**（对齐 §9）：
- **ODCS YAML 工具链**（dbt model contracts / datacontract.com / Soda CLI）适合企业级多团队数据平台——本仓库是个人项目，schemas/categories/*.py + design_memos markdown 已是轻量 Data Contract 载体
- **引入 ODCS YAML 会与 schemas/categories/*.py DDL 重复**——DDL 已定义结构，再写一份 ODCS YAML 是派生产物（违反 project_memory"派生产物不入 git"约束）
- **v1.7.0 仅用 Data Contract 概念重构理解**——不引入工具，不改变文件结构，仅在 §8 data_asset_registry 施工时参照 ODCS 六组件完整性检查清单

### 2.3 约束条件

- **不引入新数据源**：本计划只盘活已有 103 张表，不申请新供应商
- **不破坏现有策略**：补文档是"记录已有用法"，不改变数据流
- **优先级原则**（project_memory）：风险相关模块（drawdown/var/kill_switch）先于 alpha 策略；文档覆盖优先服务风险与回撤模块
- **不过度工程**：v2.1.0 实测消费层缺口 66 张（53 规划层+13 零覆盖）中代码活跃 59 张——只需补文档，无需"接入数据"；1 张真闲置表（`index_meta`）的处置 + 6 张代码零引用表的采集决策是有效产出

### 2.4 已施工设施盘点（v2.1.0 新增，回应通用规则 #11"先清楚有什么→才能知道怎么改→才能知道该退役什么"）

> 本文此前各版本引用了多个脚本/目录作为"实施位置"（如 `scripts/audit_data_utilization.ps1`、`scripts/quality_spc.py`、`docs/_audit/`）。v2.1.0 全仓核验其真实存在性，防止"文档引用不存在设施"的脱节（§3.4 Detective 扫描第 5 类检查的前车之鉴）。

**已施工（真实存在，v2.1.0 核验）**：

| 设施 | 位置 | 状态 | 说明 |
|---|---|---|---|
| 业务表 DDL 真源 | [schemas/categories/](../../../schemas/categories/) 103 个 .py | ✅ 全部入 git | 2026-08-11 提交 `022910926f`/`81c7687540` 补齐最后 8 张（calendar_event/dividend_tax_node/index_adjustment/ipo_schedule/margin_target_adjustment/msci_adjustment/stock_valuation/technical_indicator） |
| 数据源登记注册表 | [dataflow_graph_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml) | ✅ 76 条 DS-001~076 | data_asset_registry.yaml 待 S6 改名（62 号 P1-B），v2.1.0 核验 6 张代码零引用表**未登记**在内 |
| 数据采集 Provider 层 | `src/zephyr/data/implementations/` 15 个 provider | ✅ production | akshare/baostock/cls/eastmoney_news/eia/fred/ifind/internal_compute/miniqmt/qweather/rss/tdx/tickflow/tqcenter/tushare——**无逐表 *_ingestion.py 脚本**，采集由 provider + 配置驱动 |
| 调度配置 | `src/zephyr/data/config/tasks.yaml` | ✅ 存在 | §7.5 归档指引中的路径以此为准（非仓库根目录） |
| 规划层数据资产文档 | [17_special_trading_days_data_assets](17_special_trading_days_data_assets.md) / [64_data_source_download_spec](64_data_source_download_spec.md) | ✅ 已提交 | 53 张表的规划层覆盖来源（资产清单+下载规范），64 号与本文互补声明见各自头部 |
| 红利税节点 VIEW | ClickHouse `c1_market.dividend_tax_node` | ✅ DB 层派生 VIEW | 从 rights_issue 实时派生（见 project_memory），DDL 文件已入 git，无 Python 代码引用属正常（VIEW 在 SQL 层消费） |
| 00 号占用表登记 | [00_index_trading_decision](00_index_trading_decision.md) line 71 | ✅ 已登记 | 但版本字符串停留在 "draft v0.9.0" 未同步（§10 Q5 跟踪） |

**未施工（本文引用但尚不存在，均为设计态）**：

| 设施 | 本文引用位置 | 状态 | 处置 |
|---|---|---|---|
| `scripts/audit_data_utilization.ps1` | §3.4/§7.0.3/§7.0.5/§7.0.9 | ❌ 未创建 | 第一波施工前创建——v2.1.0 已用内联 PowerShell 完成首轮全量重扫，脚本化是固化产物 |
| `scripts/community_detection.py` / `scripts/temporal_coupling.py` / `scripts/quality_spc.py` / `scripts/freshness_fingerprint.py` | §7.0.3/§7.0.4/§7.0.5 | ❌ 未创建 | 随对应机制启用时再建（Leiden/Temporal Coupling/SPC/状态指纹均为**运维期**机制，非施工前置） |
| `docs/_audit/` 全部 CSV 矩阵 | §3.4/§7.0.4/§7.0.9 等 | ❌ 未创建 | 随脚本创建同步建立；首个快照应为本版 §5 实测矩阵 |
| 逐表采集脚本 `src/zephyr/data/ingestions/<table>_ingestion.py` | §7.5 | ❌ 目录不存在 | §7.5 已修正为 provider 层路径——归档操作在 provider 的任务映射/tasks.yaml 层执行 |

**盘点结论**：本审查的**被审查对象**（103 表 DDL + 76 条注册表 + 15 provider）全部已施工；本审查的**审查工具链**（5 脚本 + _audit 矩阵）全部未施工——v2.1.0 的全量重扫以一次性内联命令完成，验证了"无工具链也可审查"，但**持续校验**（§3.4 extract/trace 循环）必须先落地 `audit_data_utilization.ps1`。6 张代码零引用表的"采集未施工"状态由此盘点首次确认（Provider 层无引用、tasks.yaml 无任务、注册表无条目）。

## 3. 审查方法

### 3.1 表清单来源

[schemas/categories/](../../../schemas/categories/) 下 103 个 `.py` 文件，每个对应一张 ClickHouse 业务表（文件名前缀 `market_`/`fundamental_`/`macro_`/`cross_` 对应业务域）。v2.1.0 核验：market 88 / fundamental 12 / macro 2 / cross 1 = 103。

### 3.2 引用扫描方法（v0.2.0 三层校验 / v2.1.0 补覆盖分层口径）

| 层 | 方法 | 工具 | 命中判定 |
|---|---|---|---|
| 1. 英文/拼音表名 @ design_memos | `Select-String` 在 design_memos/*.md 全文搜表名（不区分大小写，排除 63 号自引 + AI_review_instructions） | PowerShell | 命中即视为文档已覆盖——**v2.1.0 起细分两层**：命中文档为 17/64 号（资产清单/下载规范）=**规划层覆盖**；命中其他消费方文档（策略/风控/数据层）=**消费层覆盖**。施工目标以消费层为准 |
| 2. 中文别名补校 @ design_memos | 对未命中的表，搜中文别名（如 `dragon_tiger_seat` → "龙虎榜营业部"） | 人工 | 任一别名命中即恢复为"文档已覆盖" |
| 3. 代码层引用 @ src/zephyr/（v0.2.0 新增） | `Get-ChildItem -Recurse *.py \| Select-String` 搜表名 | PowerShell | 命中即视为代码已消费——**文档未覆盖但代码在用 = 文档覆盖缺口，非闲置**。v2.1.0 扩展：同步扫 `config/`+`tasks.yaml`+注册表 yaml，区分"代码零引用"是"采集未施工"还是"真闲置" |

> **v0.2.0 关键修正**：v0.1.0 仅做层 1+2（design_memos 扫描），得出"43 张闲置"的误判。层 3 代码层扫描发现其中 40 张实际被 src/zephyr/ 代码引用——**"文档没写"不等于"数据闲置"**。
>
> **v2.1.0 口径修正**：层 1 的"任一文档命中即覆盖"在 17/64 号提交后失效——53 张表仅被资产清单/下载规范提及（"要下载/已登记"），但无任何消费方文档描述其用法（字段/频率/下游逻辑）。v2.1.0 将层 1 拆分为规划层/消费层两档（§5.1 三层覆盖表），避免"规划引用冒充消费覆盖"。同时层 3 补 config/调度/注册表扫描——v2.1.0 实测发现 6 张表代码+config+tasks+注册表全零引用，此类不是"文档缺口"而是"采集未施工"（§6.1b 新类别）。

### 3.3 审查局限

- **通用名假阳性**：`market_index.py` 的 basename 为 `index`（去除前缀后），子串匹配会命中 `index_list`/`kline_index` 等无关表——已用全名 `market_index` 复核修正（实际 CODE_ONLY，非 BOTH）
- **子串匹配假阳性**：`5min` 会匹配 `15min`——对闲置判定影响有限（保守方向，不会误判为闲置），但热度计数偏高
- **"tick" 关键词过宽**：匹配 `ticker`/`TickTock` 等无关词，hit count 仅作热度参考
- **代码层引用性质未区分**：代码中的表名引用可能是"活跃消费"、"DDL 模板继承"、"已弃用但未清理"——需人工复核（§6 已标注）
- **中文别名校验未重跑**：v0.2.0 代码层扫描仅做英文表名匹配（层 1+3），**未重做层 2 中文别名校验**。v0.1.0 层 2 曾恢复 20 张表（如"龙虎榜"→`dragon_tiger`）。因此 §5.1 的"38 文档引用"是英文下界，"61 缺口"是英文上界——真实缺口约 41 张（61-20）。§6.2 批次清单应理解为"潜在缺口"而非"确定缺口"
- **config/ 配置文件未扫**：数据采集配置（如 `config/.env.qmt`）中的表引用未纳入——采集脚本必然引用所有建表，不能作为"消费"证据

### 3.4 自动化与持续校验（v0.3.0 新增）

> v0.2.0 的扫描是一次性 PowerShell 脚本。v0.3.0 引入 [OpenSpec extract/trace 循环](https://github.com/Fission-AI/OpenSpec/discussions/739)（2026-02）和 [CI 文档覆盖率门禁](https://codex.danielvaughan.com/2026/05/16/codex-cli-automated-code-documentation-generation-docstrings-jsdoc-sphinx-ci-pipelines/)（2026-05）思路，将一次性审查升级为可重复的持续校验。

**extract/trace 循环**（替代一次性扫描）：

```
§3.2 三层扫描（trace）→ 产出缺口清单（unmapped）
  ↓
§7 分波补文档（extract：为缺口表补写消费方文档）
  ↓
重跑 §3.2 三层扫描 → unmapped 缩小 → 覆盖率上升
  ↓
重复直到 unmapped 仅剩 3 张真闲置表
```

**扫描脚本化**：将 §3.2 的 PowerShell 命令封装为 `scripts/audit_data_utilization.ps1`，输出 CSV 矩阵（表名 × memo引用 × code引用 × 状态），供每波施工后回归验证。脚本不入 git 派生产物（可由 §3.2 命令重现），但输出矩阵可存 `docs/_audit/` 供版本对比。

**CI 门禁（远期）**：当文档覆盖率低于 80% 行业基准时，pre-commit 发出 warn（不阻断——个人项目不强制 CI 阻断，但提醒）。参考 [codex.danielvaughan.com 2026](https://codex.danielvaughan.com/2026/05/16/codex-cli-automated-code-documentation-generation-docstrings-jsdoc-sphinx-ci-pipelines/) 的 `COVERAGE < 80 → exit 1` 模式，但降级为 warn 符合个人项目治理风格。

**文档腐烂三类**（[codex.danielvaughan.com 2026-04](https://codex.danielvaughan.com/2026/04/26/codex-cli-doc-rot-detection-automated-documentation-repair/)）：
- **引用漂移**（Reference Drift）：表名改名后文档未同步——可自动化检测（grep 新名零命中 + 旧名仍有命中）
- **结构衰变**（Structural Decay）：文档交叉引用断链——已由 §11 交叉引用验证覆盖
- **概念过时**（Conceptual Staleness）：文档描述的用法与代码实际行为不符——需人工复核，§10 Q3（hfq 矛盾）即此类

**6 轴审查方法（v0.6.0 远期升级路径）**：

> 本审查 §3.2 三层校验覆盖"表名是否存在 + 代码是否引用"，但未覆盖**文档间一致性**（inter-document conflicts）、**文档重复**（divergent duplicates）、**未标记过时**（unmarked obsolescence）。[K-AI 6-axis method 2026-05](https://www.k-ai.ai/en/news/auditer-corpus-documentaire-ia-methode-6-axes/) 提出企业级文档语料审查的 6 轴模型——本审查当前覆盖轴 1（内部异常，由 §7.0.4 Q score 的 accuracy 维度部分覆盖）+ 轴 5（可追溯性，由 frontmatter depends_on 覆盖）+ 轴 6（新鲜度，由 §7.0.4 timeliness 指数衰减覆盖），**未覆盖轴 2/3/4**。

| 轴 | K-AI 定义 | 本审查当前覆盖 | 远期升级 |
|---|---|---|---|
| 1 内部异常 | 单文档内一致性断裂（数值/阈值/图表版本不符） | §7.0.4 Q score accuracy 维度（L3 抽检） | 远期：自动化数值一致性检查（grep 文档内所有数值 + 交叉校验） |
| 2 文档间冲突 | 多文档对同一表描述矛盾 | §7.0.2 多消费方冲突解决算法（v0.6.0 新增） | ✅ v0.6.0 已覆盖 |
| 3 分歧重复 | 同一表的多个文档版本未合并 | 未覆盖（design_memos 无版本分支） | 不适用（单仓库单版本，无分支重复问题） |
| 4 未标记过时 | 已失效文档未移除 | §6.1 4 阶段生命周期（DEPRECATED→SUNSET→REMOVED） | ✅ v0.3.0 已覆盖 |
| 5 可追溯性 | 作者/日期/验证/真源 | frontmatter depends_on + §11 修订记录 | ✅ 已覆盖 |
| 6 新鲜度 | 每段更新节奏 | §7.0.4 timeliness 指数衰减（v0.6.0 升级） | ✅ v0.6.0 已覆盖 |

**结论**：本审查已覆盖 6 轴中的 4 轴（2/4/5/6），轴 1 部分覆盖（L3 抽检），轴 3 不适用。**6 轴方法的轴 1（内部异常自动化检查）作为远期升级路径**——当 design_memos 文档量增长到 50+ 篇时，人工 L3 抽检成本上升，可引入自动化数值一致性检查（grep 文档内所有阈值/数值 + 跨章节交叉校验）。当前 42 篇文档规模下，L3 抽检 + §7.0.4 Q score 已够（§9 不过度工程）。

**Preventive vs Detective 双层检测（v0.9.0 新增）**：

> [hassette #634 2026-04](https://github.com/NodeJSmith/hassette/issues/634)（100% AI-authored 代码库的 entropy scanner 提案）区分了两种文档漂移检测模式：**preventive**（CI 时阻止坏 PR）vs **detective**（PR 间发现累积漂移）。v0.9.0 补入此区分，明确本审查的两层覆盖。

| 检测模式 | 定义 | 本审查对应 | 覆盖状态 |
|---|---|---|---|
| **Preventive**（预防式） | CI 时阻止不合规 PR——在文档漂移**进入仓库前**拦截 | §3.4 CI 门禁（覆盖率 <80% → warn）+ §7.0.6 验收闭环（L1/L2/L3 阻断不合格文档）+ pre-commit hook | ✅ 已覆盖 |
| **Detective**（侦测式） | PR 间定期扫描**已累积**的漂移——文档引用了已删除的路径、CLAUDE.md 引用了不存在的命令 | ❌ **未覆盖**——当前无"定期扫描已入库文档的引用完整性"机制 | ⏳ v0.9.0 补入 |

**为何需要 Detective 层**（hassette #634 的核心洞察）：
- Preventive 层（pre-commit hook）只在 **PR 提交时**触发——若文档引用了 `schemas/categories/old_table.py`，而 `old_table.py` 在另一个 PR 中被删除（非同 PR），pre-commit hook 无法检测跨 PR 的引用断裂
- Detective 层定期（如每周 cron）扫描全仓库——"文档引用的路径是否仍存在""文档描述的命令是否仍有效"——捕获**跨 PR 累积**的漂移
- hassette #634 提出三种实现：Option A（scheduled Claude agent）/ Option B（Python 脚本）/ Option C（Hybrid：确定性检查用脚本 + 语义检查用 agent）

**v0.9.0 补入的 Detective 扫描规则**（融入 §3.4 extract/trace 循环）：

```
Detective 扫描（每周 cron 触发，融入 §3.4 extract/trace 循环）：
1. 路径完整性检查：grep design_memos/*.md 中所有 [schemas/categories/xxx.py](...) 链接 → 验证文件是否存在
   → 若文件不存在 → 标 ⚠️ 引用漂移（§3.4 文档腐烂类型 1：引用漂移）
2. 表名一致性检查：grep design_memos/*.md 中所有英文表名 → 与 schemas/categories/ 实际 .py 文件名对比
   → 若文档引用了不存在的表名 → 标 ⚠️ 概念过时（§3.4 文档腐烂类型 3）
3. 命令有效性检查：grep design_memos/*.md 中所有 `! <command>` 或 `python scripts/xxx` → 验证脚本是否存在
   → 若脚本不存在 → 标 ⚠️ 命令漂移
4. 交叉引用完整性：grep design_memos/*.md 中所有 [xx_memo](xx_memo.md) 链接 → 验证目标文档是否存在
   → 若目标文档不存在 → 标 ⚠️ 结构衰变（§3.4 文档腐烂类型 2）
5. 代码符号漂移检查（v1.3.0 新增，参考 [dosu.dev 2026-05 freshness scoring](https://dosu.dev/blog/score-documentation-freshness-in-ci)）：grep design_memos/*.md 中所有 `def xxx` / `class Xxx` / `function xxx` 代码符号 → 验证 src/zephyr/ 代码中是否仍存在同名定义
   → 若文档引用的函数/类已删除或改名 → 标 ⚠️ 符号漂移（§3.4 文档腐烂类型 1：引用漂移的代码符号变体）
   → dosu.dev 2026-05 引用 Empirical Software Engineering 2024 研究：28.9% 的 GitHub 仓库文档引用了代码中已不存在的 function/file/class，平均过期 4.7 年

→ 输出 docs/_audit/detective_scan.csv（文档名 × 漂移类型 × 漂移位置 × 严重度）
→ 严重度分级：⚠️ 路径不存在（高）/ ⚠️ 符号漂移（高，v1.3.0 新增）/ ⚠️ 表名过时（中）/ ⚠️ 命令漂移（低）
```

**与 §3.4 extract/trace 循环的关系**：
- extract/trace 循环是"每波施工后重跑全量扫描"——**事件驱动**（施工完成触发）
- Detective 扫描是"每周定期扫描已入库文档"——**时间驱动**（cron 触发）
- 两者互补：extract/trace 管施工后的覆盖率提升，Detective 管施工间的漂移累积

**为何选 Option C Hybrid 而非 Option A/B**：
- **Option A（scheduled Claude agent）**：语义检查强但成本高（每周 LLM 调用）——本审查 §9 已声明"不自动生成文档"，agent 仅做检测不做修复
- **Option B（Python 脚本）**：确定性检查（路径/表名/命令存在性）强但语义检查弱（无法判断"文档描述的用法是否与代码行为一致"）
- **Option C Hybrid**：确定性检查（路径/表名/命令/链接）用 PowerShell 脚本（融入 `audit_data_utilization.ps1`），语义检查用 §7.0.6 L3 人工抽检——兼顾成本与覆盖

**Model drift 分类（v1.2.0 新增）**：

> §3.4 上述"文档腐烂三类"（引用漂移/结构衰变/概念过时）按**腐烂机制**分类，但未区分"漂移来源"。[sincllm.com 2026-06 AI Drift Detection](https://sincllm.com/blog/ai-drift-detection-production-model-output-degradation) 提出 AI 系统的三类漂移（Data/Concept/Model drift），v1.2.0 借鉴此分类补入本审查的漂移来源区分——明确每类漂移的检测方法与责任归属，避免"所有漂移混为一谈"导致检测策略错配。

| 漂移类型 | 定义 | 本审查对应场景 | 检测方法 | 责任归属 |
|---|---|---|---|---|
| **数据漂移（Data Drift）** | 输入分布变化（LLM 场景：prompt 分布变化） | 代码引用表名字段分布变化——如 `kline_daily` 突然被 `kline_daily_hfq` 替代、`etf_nav` 引用从风险模块迁移到 alpha 模块 | §3.4 Detective 扫描的表名一致性检查 + §7.0.5 git diff 检测代码变更涉及的表名 | 自动化（PowerShell 脚本可检测） |
| **概念漂移（Concept Drift）** | 相同输入的"正确输出"定义变化（LLM 场景：标注规则变化） | 风险模块表的消费语义变化——如 `etf_nav` 从"套利信号"变为"流动性危机信号"、`restricted_shares` 从"alpha 信号"变为"风险红线" | §7.0.6 L3 语义抽检 + §7.0.4 Q score accuracy 维度 + §7.0.2 多消费方冲突解决 | 人工（语义判断无法自动化） |
| **模型漂移（Model Drift）** | 代码语义未变但行为变化（LLM 场景：权重静默更新） | 不适用——本审查无 LLM 模型，代码行为即文档描述目标，代码未变则行为未变 | — | — |

**为何区分漂移来源**（sincllm.com 2026 的核心洞察）：
- **检测成本差异**：数据漂移可自动化（grep 表名/路径存在性），概念漂移需人工语义判断（L3 抽检）——若混为一谈，要么过度自动化（误判概念漂移为数据漂移）、要么过度人工（数据漂移也人工检查浪费成本）
- **责任归属差异**：数据漂移是代码层问题（表名改名未同步文档），修复责任在代码作者；概念漂移是业务层问题（消费语义变化），修复责任在业务文档作者
- **v1.2.0 与现有机制的对接**：数据漂移 → §3.4 Detective 扫描（每周 cron）+ §7.0.5 增量更新（git diff 触发）；概念漂移 → §7.0.6 L3 语义抽检（每批次抽样）+ §7.0.2 多消费方冲突解决（双语义标注）。**不新增独立检测流程**——v1.2.0 仅补充分类视角，让现有机制的责任归属更清晰

**与"文档腐烂三类"的关系**：sincllm.com 的"漂移来源分类"（Data/Concept/Model）与 codex.danielvaughan.com 的"腐烂机制分类"（引用漂移/结构衰变/概念过时）是正交的两个维度——前者回答"漂移从哪来"，后者回答"漂移长什么样"。两者交叉覆盖：

| | 引用漂移（机制） | 结构衰变（机制） | 概念过时（机制） |
|---|---|---|---|
| **数据漂移（来源）** | ✅ 表名改名→引用断裂 | ✅ 路径删除→交叉引用断链 | ⚠️ 表名未变但代码用法已变 |
| **概念漂移（来源）** | — | — | ✅ 消费语义变化→文档描述过时 |
| **模型漂移（来源）** | — | — | —（本审查不适用） |

→ 落码指引：Detective 扫描发现的漂移按"来源+机制"双标注——如"数据漂移×引用漂移"（表改名）走 §7.0.5 增量更新自动修复；"概念漂移×概念过时"（语义变化）走 §7.0.6 L3 人工复核。

**管道级假新鲜失败模式（v1.9.0 新增，参考 [DZone 2026-07-20 "When Data Quality Checks Pass but the Data Is Still Stale"](https://dzone.com/articles/data-freshness-enhances-validity)）**：

> §3.4 的"文档腐烂三类"（引用漂移/结构衰变/概念过时）和"Model drift 分类"（Data/Concept/Model）都是**漂移发生后的检测**。但 [DZone 2026-07-20](https://dzone.com/articles/data-freshness-enhances-validity) 指出了一类更隐蔽的问题——**假新鲜**（false freshness）：管道/机制报告"成功+新鲜"，但文档实际已过时。DZone 定义的核心概念是 **freshness gap** = 事件实际发生时间 → 消费者首次可见时间的距离——"结构性检查永不测量此 gap，因为新鲜记录和过时记录同样 well-formed"。v1.9.0 补入五种管道级假新鲜失败模式，映射到本审查的文档新鲜度机制。

**DZone 五种假新鲜失败模式**（原为数据管道场景，v1.9.0 映射到文档-代码同步场景）：

| # | DZone 原始场景（数据管道） | 本审查映射（文档-代码同步） | 现有机制是否覆盖 | 补强措施 |
|---|---|---|---|---|
| 1 | **源端无新文件**——job 运行成功，处理了与昨天相同的输入，报告 success，但无任何更新 | **代码无变更但 git hook 仍触发**——git commit 只改了 .gitignore/README 等无关文件，hook 误判"代码变更→文档需更新" | ✅ §7.0.5 v0.9.0 DocPilot false-positive filter 覆盖——检查 git diff ±行是否含表名/字段名 AND 变更行是否在 SQL/数据加载函数内 | 已覆盖 |
| 2 | **部分分区到达**——管道加载了收到的分区并完成，缺失的区域/日期不是 error（job 从未被通知这些分区是必需的） | **部分表文档更新**——一个 commit 同时改了 3 张表的代码，但增量更新只标记了第 1 张表文档 stale（git diff 表名提取遗漏了后 2 张） | ⚠️ 部分覆盖——§7.0.5 步骤 1 "识别变更文件涉及的表名"依赖 grep 准确性，若表名在代码中用变量拼接（如 `table = f"kline_{period}"`）则 grep 可能遗漏 | 补强：§7.0.5 步骤 1.5 增加"动态表名追踪"——对 f-string/变量拼接的表名，用 AST 提取可能的表名集合（§9 已排除 AST 全量解析，但此处仅提取字符串字面量拼接，成本可控） |
| 3 | **迟到的上游延迟了真实数据**——定时任务按时触发，但上游数据尚未到达，处理了不完整/旧的快照并干净完成 | **上游表 schema 变更但下游文档未级联标记**——`stock_list` 的 schema 变了（新增字段），依赖它的 `kline_daily` 文档应标记 stale，但 git diff 只触发 `stock_list` 自身的文档检查 | ⚠️ v1.9.0 §7.0.5 `verifiedAtVersion` 状态指纹的一跳 lineage 传播已覆盖——`verifiedAgainstUrns` 包含一跳上游，`stock_list` hash 变更→`kline_daily` 的联合指纹变更→自动标记 stale | ✅ v1.9.0 已覆盖 |
| 4 | **仪表板缓存了过时表**——管道更新了表，但 BI 工具返回了缓存结果，最新数据未到达屏幕 | **文档消费者读取的是旧版本**——文档已更新（git commit），但读者本地 working copy 未 pull，或 IDE 缓存了旧版文档 | ❌ 非本审查范围——文档消费侧（读者环境）的缓存问题属于"docs-as-code 工作流"而非"文档新鲜度审计" | 不补强——属 git 工作流培训范畴，§9 个人项目 docs-as-code 已有 git pull 习惯 |
| 5 | **回填用旧快照覆盖了当前数据**——修正作业跑了历史范围，通过 scope 错误用旧记录替换了新记录，每一行都 valid，但表"倒退了时间" | **git revert 恢复了旧版文档**——回滚施工错误时（§7.0.7），git revert 不慎恢复了更早版本的文档（含已修复的 bug），文档"倒退了时间"但看起来"刚更新过" | ⚠️ 部分覆盖——§7.0.7 回滚机制用 git revert 保留历史，但未检查"revert 后的文档版本是否比当前版本更旧" | 补强：§7.0.7 L1-L4 回滚流程增加"回滚版本校验"——revert 前检查目标 commit 的文档 timeliness 是否低于当前（若 revert 目标的 timeliness < 当前→警告"回滚到更旧的文档版本"） |

**DZone 的核心洞察对本审查的启示**：

- **"Validity ≠ Freshness"**（DZone 核心论点）——文档可以"结构完整"（模板 6 字段全填，L1 存在性通过）但"语义过时"（描述的用法与最新代码不符）。这正是 §7.0.6 L3 语义抽检防"假覆盖"的依据——DocPrism 2026 发现 11% 的代码-文档对存在不一致
- **"管道成功 ≠ 数据新鲜"**——git commit 成功（管道成功）不等于文档已更新（数据新鲜）。§7.0.5 v1.9.0 的状态指纹机制（`verifiedAtVersion`）正是解决此问题——不依赖 commit 事件，而是对比实体当前状态与指纹
- **"Freshness 需按数据集差异化定义"**（DZone 的 per-dataset freshness expectation）——不同表的文档新鲜度容忍度不同：风险红线表（`restricted_shares`）需周级同步，历史参考表（`stock_list` 基础信息）可月级同步。这与 §7.0.4 `half_life=30 天` 的参数敏感性警告一致——v0.7.0 已声明 half_life 应纳入 §6.0 权重校准循环按表差异化调整
- **失败模式 2 和 5 是当前机制的盲区**——v1.9.0 补入对应的补强措施（动态表名追踪 + 回滚版本校验），闭合 DZone 五种假新鲜模式的检测缺口

**与 §7.0.4 Freshness SLO/SLI 的联动**：DZone 的假新鲜失败模式 1-5 是 **Freshness SLI 的假阳性源**——SLI 报告"timeliness ≥ 7.0"但实际文档已过时。v1.9.0 补强措施（DocPilot filter / 状态指纹 / 动态表名追踪 / 回滚版本校验）降低假阳性，使 Freshness SLI 更可信。

**paired-model 双 LLM 交叉验证（v1.6.0 新增，参考 [arXiv 2608.03500v1 2026-08-04 LLM辅助审查优先级排序](https://arxiv.org/html/2608.03500v1)）**：

> [arXiv 2608.03500v1 2026-08-04](https://arxiv.org/html/2608.03500v1)（2026-08-04 发布，56,198 页面/84 站点 corpus audit）提出多阶段审查工作流：确定性筛选→模型辅助 triage→深度审查→最低证据检查→temporal-validity safeguards→**paired-model comparison**。两个独立 LLM 对同一文档-代码对做一致性判断，一致性 75.8%（kappa=0.532）——明确"reproducibility-bounded, not validated detector"，产出 prioritized workload 而非 error prevalence。v1.6.0 补入此方法作为 §7.0.6 L3 人工抽检的远期自动化升级路径。

**paired-model 工作流**（映射到本审查 L3 场景）：

```
1. 对每张 L3 抽检表，两个独立 LLM（如 GPT + Claude）分别判断"文档描述与代码行为是否一致"
   → 输出 {is_consistent: bool, confidence: 0.0-1.0, inconsistent_sections: [字段名]}
2. 一致性判定：
   a. 两 LLM 均判 consistent → 高置信通过（跳过人工复核）
   b. 两 LLM 均判 inconsistent + confidence ≥ 0.8 → 高置信不通过（直接触发 §7.0.7 L1 回滚）
   c. 两 LLM 判断分歧（一 consistent 一 inconsistent）→ kappa 低置信区，人工复核裁定
3. kappa 量化两 LLM 一致性：κ > 0.6 为 substantial agreement，κ < 0.4 为 fair/poor
```

**为何不当前采纳 paired-model 但记录为远期路径**（对齐 §9）：
- **LLM 成本**：paired-model 需 2 次 LLM 调用/表——61 张缺口表 × 2 = 122 次 LLM 调用，与 DocAgent/Cascade 同量级（§9 已声明不采纳）
- **kappa=0.532 的启示**：两 LLM 一致性仅 75.8%——说明 LLM 在"文档-代码语义一致性"判断上仍有 24% 分歧，paired-model 不能完全替代人工 L3 抽检，仅能分流高置信案例
- **temporal-validity safeguards 价值**：arXiv 2608.03500v1 的"时效性护栏"思想可简化融入 L3 抽检——抽检时先验证"文档描述的表用法在代码最近 N 次变更后是否仍成立"，再判断语义一致性
- **远期触发条件**：当 design_memos 增长到 100+ 篇（与 DocAgent/Cascade 触发条件一致）或 L3 人工抽检不一致率 >15% 时，可引入 paired-model 分流高置信案例，人工仅复核分歧案例

### 3.5 Confidence 因子自动判定（v0.5.0 新增）

> §3.3 承认"代码层引用性质未区分"需人工复核，§6.0 的 Confidence（1.0/0.8/0.5）当前靠人工标注。v0.5.0 补入**自动判定算法**——用正则匹配代码引用上下文，将人工标注降级为异常复核，解决 61 张缺口表逐张人工标注的成本问题。

**判定规则**（按优先级降序，首个命中即定级）：

| 优先级 | 代码引用上下文模式 | Confidence | 判定理由 |
|---|---|---|---|
| 1 | `SELECT ... FROM <table>` / `INSERT INTO <table>` / `read_csv.*<table>` / `fetch_<table>` / `<table>_df =` | **1.0**（活跃消费） | SQL 查询/数据加载/变量赋值——明确活跃消费 |
| 2 | `from schemas.categories.<table> import` / `import <table>` / `<table>.py` 在 `__init__.py` 注册 | **0.5**（低置信） | schema 定义/import 注册——疑似 DDL 模板继承 |
| 3 | 表名作为字符串字面量出现在配置/路由/映射字典（如 `{"table": "<table>"}`） | **0.8**（推测消费） | 配置引用——可能是路由表，需人工确认是否实际触发 |
| 4 | 表名作为注释/文档字符串/docstring 出现 | **0.5**（低置信） | 注释引用——疑似历史遗留，非活跃消费 |
| 5 | 以上均未命中（仅文件名 grep 命中） | **0.3**（极低置信） | 文件名子串匹配——可能是假阳性（如 `tick` 匹配 `ticker`） |

**实现**（PowerShell 正则，封装进 `scripts/audit_data_utilization.ps1`）：

```powershell
# 对每张表，按优先级 1→5 扫描 src/zephyr/ 代码引用上下文
foreach ($table in $tables) {
    $hits = Get-ChildItem src/zephyr -Recurse -Filter *.py |
            Select-String -Pattern $table -Context 0,1
    $confidence = 0.3  # 默认极低置信
    foreach ($h in $hits) {
        $line = $h.Line
        if ($line -match "(SELECT|INSERT INTO|read_csv|fetch_|_df\s*=).*$table") { $confidence = 1.0; break }
        if ($line -match "(from\s+schemas\.categories|import\s+$table|__init__)") { $confidence = 0.5; break }
        if ($line -match "['""]$table['""]") { $confidence = 0.8; break }
        if ($line -match "^#\s.*$table|\"\"\".*$table") { $confidence = 0.5; break }
    }
    # confidence 写入 CSV 矩阵的 confidence 列
}
```

**自动判定的边界**：
- **正则局限**：无法区分"SQL 字符串构造查询"与"SQL 字符串仅作日志"——优先级 1 可能误判日志语句为活跃消费。复核方式：优先级 1 命中后抽查 1-2 个文件确认是否真实执行。
- **多模式混合**：一张表可能同时有 SQL 查询（1.0）和 import（0.5）——取**最高 confidence**（乐观策略，避免模板继承拉低真实消费表的优先级）。
- **配置驱动消费**：如 `internal_compute_provider` 的 `_PERIOD_MAP` 字典映射 period→table 名，优先级 3 命中——需人工确认路由是否实际触发（16 号技术指标表已确认触发，confidence 应升为 1.0）。
- **不做 AST 全量解析**：Python AST 可精确定位"赋值/调用/导入"节点，但实现成本高于正则 10 倍——个人项目用正则 + 抽查已够（参考 §9 不做什么）。

**与 §6.0 RICE 评分的对接**：自动判定的 confidence 直接喂入 §6.0 公式的 `confidence` 因子，替代人工标注。`hog_futures_core` 若自动判定为优先级 2（import 注册）→ confidence=0.5 → priority 从 2.8 降到 1.4（批次 D），与 v0.4.0 人工标注结论一致——验证自动判定可靠性。

**REFORGE 8 门置信度漏斗远期升级（v0.7.0 新增）**：

> 当前 §3.5 用 5 级正则优先级（1.0/0.8/0.5/0.5/0.3）判定 Confidence。[REFORGE 2026-07](https://ubos.tech/reforge-a-method-for-benchmarking-llms-reverse-engineering-capabilities-in-decompiled-binary-function-naming/) 提出 8 门置信度漏斗（8-gate confidence funnel）+ 溯源链（provenance chain），v0.7.0 补入作为远期升级路径。

**REFORGE 的 8 门漏斗**（每门检查通过则升档，不通过则降档）：

```
Gate 1: 范围重叠检查（range overlap）——引用位置是否在函数/方法范围内
Gate 2: 控制流相似性（control-flow similarity）——引用上下文的控制流模式
Gate 3: 符号表提示（symbol table hints）——符号表中是否有该表名
Gate 4: 调用链完整性（call chain completeness）——调用链是否完整可达
Gate 5: 类型签名匹配（type signature match）——引用的类型是否匹配 schema
Gate 6: 数据流验证（data flow validation）——数据是否真实流入消费逻辑
Gate 7: 配置触发验证（config trigger validation）——配置路由是否实际触发
Gate 8: 运行时足迹（runtime footprint）——是否有运行时日志证明执行

→ 8 门全过 = high confidence（对应本审查 1.0）
→ 5-7 门过 = medium confidence（对应本审查 0.8）
→ <5 门过 = low confidence（对应本审查 0.5/0.3）
```

**为何不当前采纳 REFORGE 8 门**：
- **适用场景差异**：REFORGE 针对"反编译二进制函数命名"的 LLM 评测——需编译器 DWARF 调试信息 + 反编译器输出对齐，本审查是"代码表名引用性质判定"，无需二进制反编译
- **成本**：8 门检查需静态分析工具链（AST 解析 + 控制流图 + 数据流分析）——本审查 §9 已声明"不用 AST 全量解析"，8 门漏斗比 AST 更重
- **溯源链价值**：REFORGE 的溯源链（provenance chain）记录"判定结果由哪些证据支撑"——本审查 §3.5 的正则命中行号 + 上下文已提供轻量溯源（CSV 矩阵记录 hit file + line + context）
- **远期触发条件**：当 §3.5 正则判定结果与人工复核差异率 >20% 时（即正则误判率过高），可引入 REFORGE 风格的多门检查提升精度——当前正则 + 抽查的误判率未实测，待第一波施工后统计

**REFORGE 对本审查的启示**：
- **分档思想一致**：REFORGE 的 high/medium/low 三档与本审查的 1.0/0.8/0.5 三级 Confidence 在分档逻辑上一致——验证了 §3.5 分级的合理性
- **溯源链值得吸收**：REFORGE 每个判定结果附"证据链"（哪些门通过/未通过）——本审查 §3.5 当前仅记录"命中优先级"，v0.7.0 建议 CSV 矩阵补 `evidence` 列记录"命中行 + 正则模式 + 上下文摘要"，轻量实现溯源链
- **多门叠加降假阳性**：REFORGE 8 门叠加可将假阳性从 survivorship bias 中分离——本审查 §3.3 的"通用名假阳性"（`index` 匹配 `index_list`）可通过"Gate 3 符号表提示"（全名 `market_index` 复核）降假阳性，当前已用全名复核实现等价效果

## 4. 业务数据库总览（103 张表）

按业务域分 9 大类（v0.1.0 报 101 张 + 算术合计 103 均有误，v0.2.0 修正为 102，v2.1.0 实测为 103——`market_stock_valuation` 2026-08-11 新增）：

| # | 业务域 | 表数 | 代表表（稳定 path） |
|---|---|---|---|
| 1 | A 股 K 线（含后复权/指数/板块/分钟级） | 15 | [kline_daily](../../../schemas/categories/market_kline_daily.py) / [kline_daily_hfq](../../../schemas/categories/market_kline_daily_hfq.py) / [kline_index](../../../schemas/categories/market_kline_index.py) / [kline_sector](../../../schemas/categories/market_kline_sector.py) |
| 2 | ETF/LOF/可转债 K 线 | 12 | [kline_etf_daily](../../../schemas/categories/market_kline_etf_daily.py) / [kline_lof_1min](../../../schemas/categories/market_kline_lof_1min.py) / [kline_cb](../../../schemas/categories/market_kline_cb.py) |
| 3 | 跨市场 K 线（港股/美股/期货） | 5 | [kline_hk_daily](../../../schemas/categories/market_kline_hk_daily.py) / [kline_us_daily](../../../schemas/categories/market_kline_us_daily.py) / [kline_futures](../../../schemas/categories/market_kline_futures.py) |
| 4 | Tick / 实时快照 / 涨跌停 | 4 | [tick](../../../schemas/categories/market_tick.py) / [l2_tick](../../../schemas/categories/market_l2_tick.py) / [realtime_snapshot](../../../schemas/categories/market_realtime_snapshot.py) / [limit_up_down](../../../schemas/categories/market_limit_up_down.py) |
| 5 | 基础元数据（股票/指数/板块/概念列表） | 21 | [stock_list](../../../schemas/categories/market_stock_list.py) / [index_list](../../../schemas/categories/market_index_list.py) / [sector_list](../../../schemas/categories/market_sector_list.py) / [concept_board](../../../schemas/categories/market_concept_board.py) / [etf_list](../../../schemas/categories/market_etf_list.py) / [convertible_bond_list](../../../schemas/categories/market_convertible_bond_list.py) |
| 6 | 资金流/杠杆/事件（龙虎榜/大宗/拍卖/MSCI） | 11 | [money_flow](../../../schemas/categories/market_money_flow.py) / [margin_trading](../../../schemas/categories/market_margin_trading.py) / [hk_connect_flow](../../../schemas/categories/market_hk_connect_flow.py) / [dragon_tiger](../../../schemas/categories/market_dragon_tiger.py) / [block_trade](../../../schemas/categories/market_block_trade.py) / [msci_adjustment](../../../schemas/categories/market_msci_adjustment.py) |
| 7 | 衍生品（期权/期货/生猪/可转债 IV） | 11 | [option_kline](../../../schemas/categories/market_option_kline.py) / [option_iv](../../../schemas/categories/market_option_iv.py) / [option_greeks](../../../schemas/categories/market_option_greeks.py) / [cb_iv](../../../schemas/categories/market_cb_iv.py) / [hog_futures_core](../../../schemas/categories/market_hog_futures_core.py) |
| 8 | 基本面/宏观 | 22 | [balance_sheet](../../../schemas/categories/fundamental_balance_sheet.py) / [income_statement](../../../schemas/categories/fundamental_income_statement.py) / [cashflow_statement](../../../schemas/categories/fundamental_cashflow_statement.py) / [analyst_forecast](../../../schemas/categories/fundamental_analyst_forecast.py) / [restricted_shares](../../../schemas/categories/fundamental_restricted_shares.py) / [share_unlock](../../../schemas/categories/fundamental_share_unlock.py) / [edb_data](../../../schemas/categories/macro_edb_data.py) / [macro_data](../../../schemas/categories/macro_macro_data.py) / [stock_valuation](../../../schemas/categories/market_stock_valuation.py)（v2.1.0 新增归入） |
| 9 | 衍生（技术指标/验证日志） | 2 | [technical_indicator](../../../schemas/categories/market_technical_indicator.py) / [cross_validation_log](../../../schemas/categories/cross_validation_log.py) |
| | **合计** | **103**（15+12+5+4+21+11+11+22+2=103；v0.1.0 报 101 且算术合计 103 均有误，v0.2.0 修正为 102，v2.1.0 以 [schemas/categories/](../../../schemas/categories/) 实际 103 个 .py 文件为准修正——market 88 + fundamental 12 + macro 2 + cross 1；分类边界按代表表归集，单表归属以 §6 清单为准） | |

## 5. 引用审查结果

### 5.1 总体利用率（v2.1.0 全量重扫实测，2026-08-12 git 提交态）

| 指标 | 数值 | 说明 |
|---|---|---|
| 总表数 | 103 | [schemas/categories/](../../../schemas/categories/) 实际 .py 文件数（market 88 + fundamental 12 + macro 2 + cross 1） |
| 受扫文档数 | 46 篇 | 47 篇编号 design_memos - 本备忘自引（AI_review_instructions 辅助文件除外） |
| **消费层文档覆盖**（非 17/64 号消费方文档命中） | **37（35.9%）** | **真问题在此**——策略/风控/数据层文档显式引用表名，< 80% 行业基准 |
| 规划层文档覆盖（仅 17/64 号命中） | 53（51.5%） | 资产清单/下载规范级引用——"登记了要下/已建表"，未描述消费用法 |
| 零覆盖（无任何文档命中） | 13（12.6%） | 其中 12 张代码在用（真文档缺口），1 张真闲置 |
| 文档覆盖-任一文档命中（旧口径，仅参考） | 90（87.4%） | v0.2.0 口径——含规划层后虚高，不再作为施工目标 |
| src/zephyr/ 代码引用 | 96（93.2%） | 代码层消费率（v2.1.0 实测；7 张零引用见下） |
| 文档+代码任一引用（**已使用**） | **102（99.0%）** | 真实数据利用率——仅 `index_meta` 完全闲置 |
| **完全闲置**（文档+代码+config+tasks 全零引用） | **1（0.97%）** | `index_meta`（§6.1） |
| **代码零引用但规划已登记**（v2.1.0 新类别） | **6（5.8%）** | dividend_tax_node / index_adjustment / ipo_schedule / margin_target_adjustment / msci_adjustment / stock_valuation——DDL+规划文档有，代码/config/tasks.yaml 全零（§6.1b 采集未施工类别） |
| **消费层文档缺口**（施工目标清单） | **59（57.3%）** | 47 张规划层代码活跃 + 12 张零覆盖代码活跃——补消费文档，非接入数据 |

> **v2.1.0 三层口径说明**：v0.2.0 的"38（37.3%）"实测对应今天的**消费层覆盖**（37 张，两天仅 -1，口径稳定）——真问题从未变化：消费方文档不描述表的用法。2026-08-11 提交的 17/64 号带来 53 张规划层引用，任一文档命中口径虚高至 87.4%，**规划层引用不等于消费覆盖**（§7.0.6 L2/L3 标准要求字段/下游逻辑/频率描述）。利用率 99.0% 健康（[thedataops.org 2026](https://www.thedataops.org/data-documentation/) 的 doc coverage 80% 基准针对的是消费级文档，本审查以消费层 35.9% 对齐该基准）。行业对照：[modern-datatools.com 2026-04 Data Baselining](https://www.modern-datatools.com/blog/data-baselining-warehouse-lifecycle-2026) 三层基线法（生命周期策略→使用量清理→团队 ritual）验证"先盘点真源再分层处置"路径；其"20% 表被活跃查询"的企业常态反衬本仓库 99.0% 利用率异常健康。

### 5.2 已使用表热度分布（design_memos 前 15 名，excl 63 自引 / v2.1.0 实测重排）

| 表名 | 引用次数 | 引用文档数 | 性质 | 主要消费方/引用来源 |
|---|---|---|---|---|
| tick | 471 | 20 | ⚠️ 通用名膨胀 | 几乎全文档（高频词，含 ticker 等误判，仅作参考） |
| technical_indicator | 59 | 6 | 消费层 | 16 技术指标系列 / 62 注册表 |
| trade_calendar | 48 | 3 | 混合 | 15 数据特征层 + 17/64 规划层 |
| hk_trade_calendar | 40 | 3 | 混合 | 19 北向 / 17/64 规划层 |
| dragon_tiger | 34 | 4 | 消费层 | 13 regime / 24 打板 / 26 事件驱动（含 dragon_tiger_seat 子串） |
| calendar_event | 31 | 2 | 规划层 | 17 特殊交易日 / 64 下载规范 |
| daily_valuation | 27 | 4 | 消费层 | 11/13/14 regime 系列 / 15 数据特征层 |
| sector_snapshot | 25 | 3 | 消费层 | 22 板块轮动 / 90 开放问题 |
| auction | 25 | 5 | 消费层 | 20 首批策略 / 24 打板 / 41 买流 / 42 卖流（含 auction_book 子串） |
| kline_daily | 17 | 3 | 消费层 | 15/16 系列（含 kline_daily_hfq 子串） |
| edb_data | 16 | 1 | 规划层 | 17 特殊交易日（宏观 EDB 资产） |
| money_flow | 16 | 3 | 消费层 | 13/22/25 |
| hk_connect_flow | 15 | 3 | 消费层 | 13 regime phase3 / 19 北向 |
| ipo_schedule | 14 | 2 | 规划层 | 17/64 规划层（代码零引用，§6.1b） |
| index_adjustment | 14 | 2 | 规划层 | 17/64 规划层（代码零引用，§6.1b） |

> v2.1.0 以 git 提交态实测重排（任一文档命中口径，子串匹配）。v0.2.0 热度数字（如 block_trade 52 次/5 文档、trade_calendar 7 次/2 文档）以当时未提交工作区为扫描对象，现已不可复现——如 `block_trade` 实测 7 次/2 文档（13/64 号），跌出前 15。通用名 `index`（441 次/43 文档）为子串假阳性（命中 index_list/kline_index 等），按 §3.3 惯例以全名 `market_index` 复核（3 次真实命中），不入榜。热度仅作参考，施工优先级以 §6 为准。

### 5.3 零文档覆盖但代码在用（v2.1.0 实测 12 张真缺口）

以下 12 张表在 src/zephyr/ 有代码引用，但 46 篇受扫 design_memos 零引用（excl 63 自引，v2.1.0 实测）——**当前文档覆盖缺口的全部硬缺口**。v0.2.0 的 TOP 15 缺口表（concept_sector/option_kline/realtime_snapshot/calendar_event/index_constituent 等）已于 2026-08-11 被 17/64 号规划层覆盖，不再零覆盖（但消费级描述仍缺，转入 §6.2 施工清单）：

| 表名 | 代码引用次数 | 代码文件数 | 推测消费方 | 应补文档 |
|---|---|---|---|---|
| stock_indicator | 12 | 2 | 个股指标（技术/估值衍生） | [15_data_feature_layer_spec](15_data_feature_layer_spec.md) |
| hk_kline | 10 | 2 | 港股 K 线（与 kline_hk_daily 并存，口径待厘清） | 批次 D 记录 |
| cross_validation_log | 7 | 1 | 交叉验证日志（回测/校准派生） | [52_backtest_framework_docking](52_backtest_framework_docking.md) |
| cb_iv | 7 | 1 | 可转债 IV | [26_event_driven_strategy_detail](26_event_driven_strategy_detail.md) |
| kline_etf_15min / kline_etf_5min | 6+6 | 2+2 | ETF 分钟 K（路由映射级引用） | 16 号指标 machinery 配套 |
| kline_lof_15min / 30min / 5min / 60min | 各 6 | 各 2 | LOF 分钟 K（路由映射级引用；90 号 §18 LOF=P0） | 16 号指标 machinery 配套 |
| concept_board_constituent | 4 | 1 | 概念板块成分 | [22_sector_rotation_spec](22_sector_rotation_spec.md) |
| kline_etf_daily | 2 | 1 | ETF 日 K | 批次 D 记录 |

> 分钟级 K 线（kline_etf_*/kline_lof_*）的代码引用均为 2 文件 6 次的路由映射级（`internal_compute_provider` period→table 映射族）——按 §3.5 判级为 Confidence 0.8（配置驱动消费）。此类表的"补文档"应以 16 号技术指标 machinery 的 period 覆盖说明统一承载，不逐表铺文档（§9 不过度工程）。

### 5.4 历史"低频引用"表 v2.1.0 复核

v0.1.0 §5.3 称 `macro_data`/`industry_class`/三大报表/`disclosure_plan`/`kline_weekly`/`kline_monthly` 仅 1-2 次引用。v2.1.0 实测复核：(1) 上述表全部已被 17/64 号**规划层覆盖**（资产清单/下载规范），`industry_class` 另有代码 59 次引用（消费层活跃）；(2) 但**消费级描述**仍缺——基本面三表（balance_sheet/income_statement/cashflow_statement）仅在规划层与 [15_data_feature_layer_spec](15_data_feature_layer_spec.md) 数据源清单出现，未在策略文档描述消费逻辑——基本面 alpha 信号链文档待建（§6.2 批次 B）；(3) v0.2.0 的逐表计数（如 `calendar_event` 代码 24 次）以未提交工作区为扫描对象不可复现，v2.1.0 起以 git 提交态实测为准（§2.2 不可复现声明）。
## 6. 闲置与文档覆盖缺口清单（v0.2.0 重写 / v0.3.0 补评分模型 / v0.4.0 升级 RICE）

### 6.0 优先级评分模型（v0.3.0 新增 / v0.4.0 升级 RICE 置信度 / v0.6.0 补 Kano 分类层 / v1.0.0 补贝叶斯权重更新形式化）

> v0.2.0 的批次 A→B→C→D 是定性分批（按消费方模块）。v0.3.0 引入 [Impact-Effort 评分框架](https://codedebtcost.com/prioritize)（2026-03）量化。v0.4.0 升级为 [RICE 变体](https://bixtech.ai/how-to-prioritize-data-projects-with-limited-resources-without-slowing-the-business-down/)（2026-04）补入 **Confidence 置信度**因子——对应 §3.3 "代码层引用性质未区分"的不确定性。

**评分公式**（RICE 变体）：

```
priority = (impact_score × confidence) / effort_score

impact_score = code_ref_count          × W1   (代码引用热度，W1=1.0)
             + risk_module_flag        × W2   (风险模块标记，W2=5.0)
             + alpha_potential         × W3   (alpha 信号价值 0-3，W3=2.0)

confidence   = 0.5 / 0.8 / 1.0                (代码引用性质置信度)
               1.0 = 活跃消费（SQL 查询/数据加载，已人工确认）
               0.8 = 推测消费（代码引用但未确认是否模板继承）
               0.5 = 低置信（仅 schema 定义处引用，疑似 DDL 模板）

effort_score = doc_complexity          × W4   (文档复杂度 1-5，W4=1.0)
             + cross_module_coupling   × W5   (跨模块耦合度 1-3，W5=1.5)
```

**v0.4.0 新增 Confidence 因子理由**：§3.3 承认"代码层引用性质未区分"——`hog_futures_core` 代码有 7 次引用但可能是采集模板继承而非活跃消费。引入 Confidence 后，未确认性质的表 priority 打 8 折（0.8），疑似模板继承的打 5 折（0.5），避免"模板引用"虚高优先级。

**权重设计理由**（符合 project_memory 风险优先原则）：
- W2=5.0（风险模块标记权重最高）：风险/回撤模块相关表补文档优先级远高于普通策略表
- W3=2.0（alpha 信号价值）：有实证 alpha 价值的表（如 block_trade_detail / restricted_shares）加权
- W1=1.0（代码引用热度）：基础排序信号，但不单独决定优先级
- W4/W5（努力分）：文档越复杂、跨模块越多，优先级下降

**权重校准循环**（v0.4.0 新增，参考 [sigos.io 2026-06](https://www.sigos.io/blog/weighted-scoring-model)："If weights stay static while behavior shifts, model becomes neat, clean, and wrong"）：
- 第一波施工完成后，对比批次 A 内高分表与低分表的实际文档价值产出
- 若高分表未明显优于低分表 → 降低 risk_module_flag 的 W2 权重（5.0→3.0）
- 若 alpha_potential 评分主观性太强 → 用代码实际消费频率替代（code_ref_count 已含此信号，W3 可降为 1.0）
- 每波施工后重评权重，避免静态模型失真

**贝叶斯权重更新形式化（v1.0.0 新增）**：

> 上述校准循环是"若高分表未明显优于低分表则降 W2"——**经验式启发式校准**，依赖人工判断"明显优于"。[Bayesian Prioritization in Product Strategy 2026](https://discovery.researcher.life/article/bayesian-prioritization-in-product-strategy-embedding-predictive-analytics-into-agile-decision-making/c78a7b57c8ce3a1cb50c3266abaefa9f) 提出将先验权重与施工后实际价值证据结合，输出**后验权重分布**——从"拍脑袋调权重"升级为"概率化更新"。v1.0.0 补入此方法形式化校准循环，使权重调整有数学依据而非主观感觉。

**贝叶斯公式适配**：

```
P(W | E) = P(E | W) × P(W) / P(E)

W = 权重向量（W1:code_ref, W2:risk_flag, W3:alpha_potential, W4:consumers, W5:doc_complexity）
E = 施工后证据（实际 Q score 与预期的偏差 / 文档被引用频次 / 代码变更频率）
P(W) = 先验分布（当前权重的概率分布，初始设为正态 N(μ=当前值, σ=0.2×当前值)）
P(E | W) = 似然函数（在给定权重下观察到证据 E 的概率，用均方误差 MSE 建模）
P(W | E) = 后验分布（更新后的权重分布，用于下一波施工）

→ 示例：W2（risk_flag 权重）先验 μ=5.0, σ=1.0
   施工后证据 E：P0 风险表的 Q score 平均比 P1 高 2.0（预期高 1.5）
   似然 P(E|W2=5.0) = N(MSE=0.5, σ=0.1) → 高概率
   后验 P(W2 | E) → μ 从 5.0 上移到 5.3（风险权重应更高）
   → 下一波施工自动用 W2=5.3 计算 priority，无需人工拍
```

**为何形式化但不全量实施**（避免过度工程）：
- **形式化的价值**：当前"若高分表未明显优于低分表则降 W2"中"明显优于"是模糊判断——贝叶斯框架用 MSE 量化"预期 vs 实际"偏差，当偏差超过 2σ 时才触发权重更新（非每波都调），避免频繁抖动
- **不全量实施的理由**：完整贝叶斯推断需 MCMC 采样（PyMC/Stan）或共轭先验推导——102 张表 × 5 权重 × 多波施工的后验计算量对个人项目过重。v1.0.0 仅**形式化定义**（记录公式 + 触发条件），实际执行仍用§6.0 校准循环的启发式（人工对比高低分表），贝叶斯作为"理论依据"证明启发式的合理性
- **触发条件**（替代每波都调）：当某权重分量的"预期 vs 实际"偏差连续 2 波超过 2σ → 触发该分量的贝叶斯更新（人工计算后验均值，更新 §6.0 公式的 W 值）。未超 2σ 则维持当前权重——避免权重频繁变动导致 priority 排序不稳定
- **远期升级**：若施工波次 >5 且权重调整频次上升，可引入 PyMC 自动化后验计算——当前波次少（3 波），人工启发式 + 贝叶斯理论依据已够

**与 §7.0.4 SPC 趋势分析的联动**：贝叶斯权重更新的"预期 vs 实际偏差"可用 §7.0.4 的 EWMA 控制图监控——若 Q score 的 EWMA 持续偏离权重预期（如 W2=5.0 预期风险表 Q≥8 但 EWMA=6.5），则触发 W2 的贝叶斯更新。两个机制共享"偏差检测→权重调整"闭环。

**跨波次优先级动态重评算法（v1.1.0 新增）**：

> §6.0 权重校准循环说"每波施工后重评权重"，§6.0 贝叶斯权重更新说"偏差连续 2 波超 2σ 才触发"——但两者都未定义"如何根据第一波结果调整第二波的批次归属和 priority"。当前 §6.2 批次归属在施工前一次性确定，施工后不随证据动态调整——若第一波发现某"期望型"表实际价值远低于预期，第二波仍按原 priority 排序。v1.1.0 补入此算法闭合"证据→权重→priority→批次"反馈环。

**动态重评流程**（每波施工结束后执行，融入 §7.0.6 验收闭环步骤 7）：

```
1. 收集本波证据：
   a. 每张表的 Q score（§7.0.4）
   b. L3 抽检通过率（§7.0.6 主动学习抽样）
   c. 实际 effort 与 §7.0.8 Rubric 估算的偏差
   d. 本波施工实际耗时 vs §7.0.3 CPM duration 估算

2. 证据驱动的权重微调（触发 §6.0 贝叶斯更新条件）：
   a. 若本波风险表（Kano 基本型）Q score 均 ≥8.0 → W2（risk_flag 权重）当前值合理，不调整
   b. 若本波风险表 Q score 均 <7.0 → W2 可能偏低（风险表优先级不够高导致施工质量差）→ W2 上调 0.5
   c. 若本波高 code_ref 表 Q score 与低 code_ref 表无显著差异 → W1（code_ref 权重）区分力不足 → W1 下调 0.2

3. 批次归属动态调整建议（仅对未施工批次有效，不回溯已施工表）：
   a. 若本波发现某"期望型"表（批次 B/C）实际 Q score 持续 <5.0 → 建议降级为"兴奋型"，批次后移
   b. 若本波发现某"兴奋型"表（批次 D）实际 Q score ≥8.0 且被多文档引用 → 建议升级为"期望型"，批次前移
   c. Kano 基本型表不降级——无论 Q score 如何都必须补文档（风险红线）

4. 下一波 priority 重算：
   a. 用微调后的 W 值重算未施工表的 priority
   b. 输出 `priority_v{n+1}.csv`（表名 × 旧 priority × 新 priority × 变化幅度 × 批次调整建议）
   c. 变化幅度 >30% 的表标 ⚠️ 需人工复核（可能是权重调整过激）
```

**不做的**（对齐 §9）：
- 不每波都调权重——仅在贝叶斯触发条件（偏差连续 2 波超 2σ）满足时才调，避免 priority 排序频繁变动
- 不自动调整批次归属——批次归属变更需人工确认（§10 Q2 已裁定"批次归属用 §6.2 消费方模块归集"），动态重评仅提供调整**建议**
- 不回溯已施工表——已补文档的表 priority 变化不影响已完成的施工，仅影响未施工表排序

**为何不用 WSJF**（v0.5.0 新增，对比 [ideaplan.io RICE vs WSJF 2026-02](https://www.ideaplan.io/compare/rice-vs-wsjf) / [SAFe WSJF 2026-02](https://agility-at-scale.com/safe/wsjf-weighted-shortest-job-first/)）：

| 维度 | RICE 变体（本文采用） | WSJF（Cost of Delay / Job Duration） |
|---|---|---|
| 公式 | (impact × confidence) / effort | (Business Value + Time Criticality + Risk Reduction) / Job Size |
| 时间敏感性 | ❌ 无 Time Criticality 因子 | ✅ Time Criticality 一等公民 |
| Reach（覆盖面） | ✅ code_ref_count 含热度信号 | ❌ 无 Reach，热度需并入 Business Value |
| 适用场景 | 单产品功能排序 | 多团队 portfolio 排序（SAFe） |
| 个人项目适配 | ✅ 单人单产品，无多团队协调 | ❌ SAFe 为 10-100+ 人团队设计，过重 |

**结论**：保留 RICE 变体，但**承认其缺失 Time Criticality**——风险模块表（`restricted_shares` 解禁前 30 日减仓 / `etf_nav` 流动性危机监测）有明显时间窗口，RICE 不会因"解禁日临近"而提升优先级。

**可选混合模型**（v0.5.0 备选，不强制采纳）：
```
priority_v2 = priority × time_criticality_factor

time_criticality_factor =
  2.0  # 解禁/财报/IPO 等有明确日期窗口的事件表（restricted_shares/share_unlock/ipo_schedule）
  1.5  # 流动性危机/熔断等"危机触发时才用"的表（etf_nav/limit_up_down）
  1.0  # 常态消费表（无时间窗口）
  0.8  # 低时效表（基本面三表/宏观年率数据，季度更新即可）
```

> **不采纳理由**：个人项目无竞争压力，文档补齐无硬截止日——Time Criticality 在文档施工场景下退化为"风险模块优先"（已由 W2=5.0 的 risk_module_flag 覆盖）。混合模型增加一个因子但收益有限，属于过度工程。**若未来解禁日临近需紧急补 `restricted_shares` 文档，直接人工提优先级即可，不必引入全局因子**。

**阈值**（参考 [codedebtcost.com](https://codedebtcost.com/prioritize) 的 >1.5 / <0.8 分界）：
- `priority ≥ 3.0` → 批次 A（第一波，风险/回撤）
- `1.5 ≤ priority < 3.0` → 批次 B/C（第二波，策略/板块）
- `priority < 1.5` → 批次 D（第三波，跨市场/衍生品）

**示例计算**（v1.1.0 以 §7.0.8 Rubric 校准 effort 值，替代 v0.4.0 估算值）：

| 表名 | code_ref | risk? | alpha? | conf | impact | doc_cpx | xmod | effort | priority | 批次 |
|---|---|---|---|---|---|---|---|---|---|---|
| `restricted_shares` | 11 | Y(5) | 3 | 1.0 | 42 | 4 | 2 | 7.0 | **6.0** | A（Kano 基本型） |
| `etf_nav` | 17 | Y(5) | 1 | 0.8 | 44 | 4 | 3 | 8.5 | **4.1** | A（Kano 基本型） |
| `edb_data` | 10 | Y(5) | 2 | 0.8 | 39 | 3 | 2 | 6.0 | **5.2** | A（Kano 基本型） |
| `concept_sector` | 30 | N(0) | 0 | 1.0 | 30 | 2 | 2 | 5.0 | **6.0** | A*（高热度非风险） |
| `cb_iv` | 6 | N(0) | 2 | 0.8 | 10 | 5 | 2 | 8.0 | **1.0** | B（业务归集优先）† |
| `hog_futures_core` | 7 | N(0) | 0 | **0.5** | 7 | 2 | 1 | 3.5 | **1.0** | **D** ↓ |
| `kline_lof_5min` | 5 | N(0) | 0 | 0.8 | 5 | 1 | 1 | 2.5 | **1.6** | B |

> `doc_cpx` = doc_complexity（§7.0.8 Rubric 1-5 分），`xmod` = cross_module_coupling（1-3 分），`effort` = doc_cpx×1.0 + xmod×1.5
>
> **v1.1.0 校准说明**：v0.4.0 示例表的 effort 值（5/7.5/4/5/2.5）为估算值，与 §7.0.8 Rubric 量化标准不一致。v1.1.0 以 Rubric 为准重新计算——`restricted_shares` effort 从 5→7.0（doc_cpx=4 + xmod=2），`cb_iv` effort 从 5→8.0（doc_cpx=5 + xmod=2），priority 相应调整。**批次归属不变**：Kano 基本型（risk_flag=Y）无论 RICE 分多少必须进批次 A；† `cb_iv` priority=1.0 < 1.5 阈值按 RICE 应进 D，但 §6.2 按消费方模块（26 号事件驱动）业务归集进 B——**Kano 分类层 + 业务归集优先于 RICE 排序**，RICE 仅决定批次内顺序（cb_iv 在批次 B 内排序靠后）。
>
> **v0.4.0 Confidence 影响仍成立**：`hog_futures_core` 因置信度 0.5（疑似采集模板继承）priority=1.0 → 批次 D——**Confidence 因子成功将"模板引用"从施工优先级中降权**。`concept_sector` 虽非风险模块但代码引用 30 次（最高）+ 置信度 1.0，priority=6.0 → 批次 A*（高热度但非风险，可灵活排入 A 或 B）。

**Confidence 滥用警告**（v0.6.0 新增，参考 [getperspective.ai 2026-05](https://getperspective.ai/blog/feature-prioritization-framework-using-ai-customer-research-to-rank-the-roadmap) + [rightfeature.com 2026-02](https://rightfeature.com/blog/rice-scoring-model/) + [tempo.io 2026](https://www.tempo.io/guides/product-prioritization-techniques-product-managers) 的 RICE 局限研究）：

> 2026 多篇 RICE 复盘指出**最大反模式**："Teams set Confidence to 50% on every score to feel safe. That makes Confidence a constant, which mathematically..."——当所有表 confidence 都标 0.5，公式退化为 `priority = impact × 0.5 / effort`，Confidence 变成常数失去区分力。

**本审查的反滥用措施**：
- **§3.5 自动判定替代人工标注**——正则优先级 1-5 自动定级 confidence，避免人工"图省事全标 0.5"
- **Confidence 分布审计**（每波施工后）：若 >70% 的表 confidence 相同 → 触发警告，要求重跑 §3.5 自动判定
- **Confidence 不做"避险工具"**——对代码引用性质不确定的表，应走 §3.5 优先级 3（配置字面量=0.8）+ 人工抽查升/降级，不是无脑标 0.5
- [rightfeature.com 2026-02](https://rightfeature.com/blog/rice-scoring-model/)："Subjectivity creeps in quickly"—RICE 的客观性依赖输入的客观性，Confidence 是最易主观化的因子

**Kano 分类层（v0.6.0 新增，补 RICE 的"需求类型盲点"）**：

> RICE 量化"做多少价值"，但不区分"必须做"vs"做了更好"vs"无差异"。2026 多篇对比研究（[getperspective.ai 2026-05](https://getperspective.ai/blog/feature-prioritization-framework-using-ai-customer-research-to-rank-the-roadmap) / [m.zpedu.com 2026-07](https://m.zpedu.com/it/cpsj/39917.html) / [tempo.io 2026](https://www.tempo.io/guides/product-prioritization-techniques-product-managers)）推荐 **Kano + RICE 组合策略**："Kano 负责做正确的事（strategic），RICE 负责正确地做事（execution）"。本审查补入 Kano 分类层作为 RICE 的**前置过滤器**——基本型需求无论 RICE 分多低都必须补文档。

**Kano 五类映射到 102 张表**（AI 可裁定，无需人决策——基于 project_memory 风险优先原则 + 代码引用性质）：

| Kano 类型 | 定义 | 本审查映射 | 102 张表中的代表 | 施工策略 |
|---|---|---|---|---|
| **基本型**（Must-be） | 不满足会导致严重后果——风险红线、生存底线 | 风险/回撤/kill_switch 相关表（risk_module_flag=Y） | `restricted_shares` / `share_unlock` / `etf_nav` / `limit_up_down` / `margin_trading` | **无论 RICE 分多少必须补**——RICE 仅决定批次内顺序，不决定是否做 |
| **期望型**（One-dimensional） | 满足度随覆盖度线性增长——核心 alpha 信号链 | 策略文档已显式消费但文档覆盖不足的表（code_ref≥10 + 已有策略文档） | `block_trade_detail` / `dragon_tiger` / `money_flow` / `concept_sector` / `index_constituent` | RICE 排序补文档，priority ≥ 1.5 进批次 B/C |
| **兴奋型**（Attractive） | 做了有增量 alpha，不做也无损——探索性 alt data | 代码在用但无策略文档消费、alpha 价值待验证的表 | `cb_iv` / `analyst_forecast` / `msci_adjustment` / `hog_futures_core` | RICE 排序，priority < 1.5 进批次 D，仅记录代码用法不强制补策略 |
| **无差异型**（Indifferent） | 做不做都没影响——真闲置 | 文档+代码均零引用 | `dividend_tax_node` / `index_meta`（待激活）/ `msci_adjustment`（待激活） | §6.1 生命周期决策——DEPRECATED→SUNSET→REMOVED 或补建激活 |
| **反向型**（Reverse） | 做了反而降低满意度——过度工程 | 不适用（本审查无反向型——补文档不会降低满意度，但"为凑覆盖率浅覆盖"是隐性反向，由 §7.0.4 Q score 防范） | — | — |

**Kano 与 RICE 的协作流程**（v0.6.0 新增）：

```
1. Kano 分类（前置过滤器）：每张表先标 Kano 类型（AI 自动，基于 risk_module_flag + code_ref + 策略文档消费状态）
   ↓
2. 基本型 → 强制进施工队列（不进 RICE 排序，直接批次 A）
   ↓
3. 期望型 + 兴奋型 → 进 RICE 排序（§6.0 公式计算 priority）
   ↓
4. 无差异型 → 进 §6.1 生命周期决策（DEPRECATED/补建激活）
   ↓
5. 批次内排序：基本型按 §7.0.3 拓扑序，期望/兴奋型按 RICE priority 降序
```

**为何不用完整 Kano 问卷**（[m.zpedu.com 2026-07](https://m.zpedu.com/it/cpsj/39917.html)）：完整 Kano 需双向问卷（"如果提供/不提供这个功能你感觉如何"）+ 统计显著性样本——适合产品功能排序，**不适合个人项目的数据表文档补齐**（无用户可问卷）。本审查用**规则映射替代问卷**（risk_module_flag=Y→基本型 / code_ref≥10→期望型 / 其余→兴奋型），是 Kano 思想的轻量实现。完整问卷列入 §9"不做什么"。

**Consequence Ranking 批判与辩护（v0.7.0 新增）**：

> [dualoop.coach 2026-03](https://www.dualoop.coach/blog/rice-vs-ice-vs-moscow-prioritization/) 对 RICE/ICE/MoSCoW 提出系统性批判，主张用 **Consequence Ranking**（按"做/不做的后果"排序）替代公式打分。v0.7.0 补入此批判并辩护本审查的 RICE 变体选型合理性。

**dualoop.coach 的三大批判**：

| 批判 | 原文要点 | 对本审查的适用性 |
|---|---|---|
| Non-commensurable variables | "Impact 和 Effort 单位不同——Impact 可能是 users/month，Effort 可能是 engineering weeks，不能 apples × orchards" | ⚠️ **部分适用**——本审查 impact_score = code_ref×1.0 + risk_flag×5.0 + alpha×2.0 是"加权综合分"（无量纲），effort_score = doc_complexity×1.0 + coupling×1.5 也是"加权综合分"（无量纲）。两者都已归一化为无量纲分，非"apples × orchards"——但归一化过程本身引入主观性（W1-W5 权重） |
| Confidence collapses domains | "80% in Impact estimation ≠ 80% in Effort estimation——框架假装可比但实际不可比" | ✅ **不适用**——本审查的 Confidence 只作用于 impact（代码引用性质置信度），不作用于 effort（effort 由 §7.0.8 Rubric 量化）。Confidence 是单域的，不存在跨域折叠问题 |
| Weighting is invisible | "公式假设 Effort 是唯一成本轴，但真实成本含机会成本/团队焦点/技术债" | ⚠️ **部分适用**——本审查 effort 只含 doc_complexity + cross_module_coupling，不含"机会成本"（补这张表文档的代价是不补另一张表）。但个人项目无团队焦点竞争，机会成本退化为"priority 排序本身"（高分先补=机会成本已内化） |

**Consequence Ranking 的替代主张**：dualoop.coach 主张"对每项写明'如果做会怎样/如果不做会怎样'，按后果排序而非按公式打分"。

**本审查的辩护与吸收**：
- **保留 RICE 变体**：102 张表的批量排序需要可计算的公式——Consequence Ranking 需对每张表写"做/不做的后果"叙述，102 张表 × 2 段叙述 = 204 段人工写作，成本高于 RICE 公式打分。RICE 的"虚假精确性"（dualoop 批判）在 102 张表排序场景下是可接受的近似——priority=8.4 vs 7.5 的差异不决定"做不做"，只决定"先做谁"
- **吸收 Consequence Ranking 的优点**：§6.0 Kano 分类层已吸收"后果导向"思想——基本型（Must-be）的判定标准就是"不满足会导致严重后果"（风险红线），这正是 Consequence Ranking 的"如果不做会怎样"。Kano 前置过滤器 = Consequence Ranking 的轻量实现
- **不全面采纳 Consequence Ranking 的理由**：dualoop.coach 的场景是"2-4 个战略选项的深度决策"（每项需写后果叙述），本审查是"102 张表的批量排序"（需公式化）。[pmtoolkit.ai 2026-02](https://pmtoolkit.ai/learn/prioritization/prioritization-frameworks-comparison) 的对比表也确认 RICE 适合"10-100 features"的批量排序，Consequence Ranking 适合"少数战略决策"
- **对基本型表补 Consequence 视角**：§6.0 Kano 基本型表的施工策略已写明"无论 RICE 分多少必须补"——这就是 Consequence Ranking 的"如果不做会导致风险红线失效"的后果叙述，已内化在 Kano 分类中

**SQALE 技术债视角（v1.5.0 新增，参考 [technicaldebtcalculator.com 2026 SQALE Framework](https://technicaldebtcalculator.com/frameworks) + [CppDepend Smart Technical Debt Estimation](https://www.cppdepend.com/Doc/Smart_Technical_Debt_Estimation.pdf)）**：

> §6.0 RICE 评分回答"先补谁"，但未回答"整体文档债务有多严重"——61 张文档缺失表是技术债的 principal（本金），每波不补的代价是 interest（利息）。[technicaldebtcalculator.com 2026](https://technicaldebtcalculator.com/frameworks) 提供 5 种技术债度量框架（TDR/SQALE/CAST/Financial Impact/Time Based），v1.5.0 借鉴 SQALE Method 补入文档债务的 A-E 评级，作为 RICE 排序的**宏观健康度补充视角**（不替代 RICE 的微观排序）。

**文档技术债定义**（映射 SQALE 概念）：

| SQALE 概念 | 代码技术债场景 | 本审查文档债场景 |
|---|---|---|
| **Principal（本金）** | 修复代码问题的预计人时 | 补齐文档的 effort_score（§7.0.8 Rubric） |
| **Annual-Interest（年利息）** | 不修复则每年消耗的预计人时 | 不补文档则每年消耗的"查代码/问 AI/误判"时间 |
| **TDR（技术债比）** | remediation_cost / development_cost | 文档缺失表 effort / 全部表 effort |
| **Breaking-Point** | 年利息累积超过本金的时间点 | 不补文档的年消耗累积超过补文档 effort 的时间点 |

**TDR 计算与 A-E 评级**（融入 `audit_data_utilization.ps1` 输出）：

```
TDR = (Σ effort_score of 文档缺失表) / (Σ effort_score of 全部表) × 100

当前状态（v1.5.0 估算）：
- 文档缺失表 61 张，平均 effort≈5.0 → 缺失 effort ≈ 305
- 已有文档表 41 张，平均 effort≈4.0 → 已有 effort ≈ 164
- TDR = 305 / (305 + 164) × 100 ≈ 65%
→ SQALE 评级 E（>50%，Severe——文档债务严重，需优先施工）
```

**SQALE A-E 评级映射**（technicaldebtcalculator.com 2026 Bands）：

| 评级 | TDR 范围 | 状态 | 本审查施工指导 |
|---|---|---|---|
| A | 0-5% | Healthy | 文档覆盖完善，仅维护增量 |
| B | 5-10% | Manageable | 少量缺口，随施工波次自然消除 |
| C | 10-20% | Concerning | 需有计划补缺口，但不紧急 |
| D | 20-50% | Critical | 需优先施工，部分表影响开发效率 |
| **E** | **>50%** | **Severe** | **当前状态——文档债务严重，P0 风险表必须先补** |

**Annual-Interest 的个人项目适配**：
- **企业场景**——CppDepend 用"人时/年"度量年利息（如复杂方法未重构+无测试覆盖=120 分钟/年）
- **个人项目场景**——无团队工时成本，年利息难以直接量化。v1.5.0 用**消费方影响代理**替代：
  - Kano 基本型表（risk_flag=Y）文档缺失 → 年利息 = "策略误判风险"（高利息，必须先补）
  - Kano 期望型表（核心 alpha 信号链）文档缺失 → 年利息 = "开发效率损耗"（中利息，第二波补）
  - Kano 兴奋型表（探索性 alt data）文档缺失 → 年利息 = "探索机会成本"（低利息，可延后）
  - Kano 无差异型表（真闲置）文档缺失 → 年利息 = 0（无消费方，无利息）
- **Breaking-Point 估算**：风险表文档缺失的"策略误判"可能在 1-3 个月内发生（若策略上线），补文档 effort≈7.0（§7.0.8 Rubric），Breaking-Point ≈ 1-3 个月——远短于施工波次间隔，故风险表必须第一波补

**Martin Fowler Debt Quadrant 映射**（[vidhyasagarthakur.engineer 2026-03](https://www.vidhyasagarthakur.engineer/blog/the-economics-of-technical-debt)）：

| 象限 | 债务类型 | 本审查对应 |
|---|---|---|
| Deliberate + Prudent | 故意且谨慎的债（明知不完美但权衡后接受） | §6.2 批次 D 跨市场/分钟级表暂缓——明知有文档缺口但业务边界未定，暂缓是审慎决策 |
| Deliberate + Reckless | 故意且鲁莽的债（明知不完美且不计后果） | ❌ 本审查无此类——所有暂缓都有 §10 开放问题记录理由 |
| Inadvertent + Prudent | 无意且谨慎的债（不知道不完美但设计合理） | v0.1.0 的 43 张闲置表误判——不知道代码层在用但审查方法不严谨导致误判，v0.2.0 三层校验修正 |
| Inadvertent + Reckless | 无意且鲁莽的债（不知道不完美且设计不合理） | ❌ 本审查无此类——审查方法 v0.2.0 已三层校验 |

**为何补 SQALE 视角但不替代 RICE**：
- **RICE 是微观排序**（哪张表先补），**SQALE 是宏观健康度**（整体债务多严重）——两者正交
- TDR 评级 E（>50%）是"文档债务严重"的宏观信号，但具体先补哪张表仍由 RICE priority 决定
- SQALE 的 Annual-Interest 概念补入了 RICE 缺失的"不补的代价"维度——RICE 的 impact 只度量"补了的收益"，未度量"不补的损失"。v1.5.0 用 Kano 分类作为 Annual-Interest 的代理（基本型=高利息/兴奋型=低利息），不需额外计算
- **不引入 Financial Impact 框架**（对齐 §9）——Financial Impact = team_size × loaded_salary × debt_time_fraction × age_multiplier 需团队工时成本，个人项目不适用

**Cognitive Debt + AI-Generated Debt 新类别（v1.6.0 新增，参考 [Exceeds AI 2026-06-09 AI Debt Score](https://blog.exceeds.ai/ai-technical-debt-tracking-workflow/) + [dupple.com 2026-04-03 AI-generated debt](https://dupple.com/blog/what-is-technical-debt-in-software-development)）**：

> §6.0 v1.5.0 的 Martin Fowler Debt Quadrant 四象限（Deliberate/Inadvertent × Prudent/Reckless）无法归类 2026 年新出现的 **AI-generated debt**——代码/文档由 AI 生成，无人故意编写、无决策点，Fowler 的"deliberate vs inadvertent"二分法失效。[Exceeds AI 2026-06-09](https://blog.exceeds.ai/ai-technical-debt-tracking-workflow/) 进一步提出 **Cognitive Debt**（Margaret-Anne Storey 定义）：AI 加速代码/文档生产快于团队维持心智模型的 project-level 理解侵蚀。v1.6.0 补入此新类别，因本审查的文档施工由 AI 执行（§7.0.2 代码反推 + §7.0.1 模板套用），天然存在 AI-generated debt 风险。

**Fowler 四象限 + AI 新增第五类**（[dupple.com 2026-04-03](https://dupple.com/blog/what-is-technical-debt-in-software-development)）：

| 债务类别 | 定义 | 本审查对应 |
|---|---|---|
| Deliberate + Prudent | 故意且谨慎（明知不完美但权衡后接受） | §6.2 批次 D 暂缓 |
| Deliberate + Reckless | 故意且鲁莽（明知不完美且不计后果） | ❌ 无（§10 记录所有暂缓理由） |
| Inadvertent + Prudent | 无意且谨慎（不知道不完美但设计合理） | v0.1.0 误判（v0.2.0 三层校验修正） |
| Inadvertent + Reckless | 无意且鲁莽（不知道不完美且设计不合理） | ❌ 无（v0.2.0 已修正方法） |
| **AI-Generated Debt**（v1.6.0 新增） | AI 生成的内容无人完全拥有/理解，无决策点 | ⚠️ **本审查文档施工由 AI 执行**——§7.0.2 代码反推生成的草稿、§7.0.1 模板套用的文档，AI 是主要作者，人仅做 L3 抽检复核。61 张缺口表的文档若 AI 生成后无人深度理解，即形成 AI-Generated Debt |

**Cognitive Debt 的本审查映射**（Storey 定义 → 文档施工场景）：

| Cognitive Debt 维度 | 代码场景 | 本审查文档场景 |
|---|---|---|
| **生产速度 > 理解速度** | AI 生成代码快于团队 review | AI 反推文档快于人 L3 抽检——61 张表的草稿可能在数小时内生成，但 L3 抽检每波仅 2-3 张 |
| **心智模型侵蚀** | 团队对系统理解逐渐模糊 | 文档作者（AI）无心智模型，人仅通过 L3 抽检部分理解——未抽检的表文档人可能从未读过 |
| **project-level 理解缺口** | 个别开发者理解局部但无人理解全局 | 无人能完整叙述 102 张表的文档覆盖状态——需 §7.0.9 看板 + §5.1 覆盖率指标做全局代理 |

**AI-Generated Debt 度量指标**（[Exceeds AI 2026-06-09](https://blog.exceeds.ai/ai-technical-debt-tracking-workflow/) + [dupple.com 2026-04-03](https://dupple.com/blog/what-is-technical-debt-in-software-development)，引用 2026 MSR 研究 806 仓库 Cursor 采用使复杂度+41%；CodeRabbit 470 PR 研究 AI 代码安全漏洞 2.74x）：

| 指标 | 定义 | 本审查采集方式 | 健康阈值 |
|---|---|---|---|
| **AI-touched doc cycle time** | AI 生成文档到人 L3 抽检通过的时间 | `construction_kanban.csv` 的 `construction_date`（AI 生成）到 `l3_result=pass` 日期 | ≤14 天（与 MTTR 对齐） |
| **Rework rate** | 30 天内 AI 生成的文档被重写的比例 | git log 统计 30 天内同一文档的二次修订 commit | <20%（>20% 说明 AI 生成质量不稳定） |
| **L3 抽检覆盖率** | 已 L3 抽检的表数 / AI 生成文档的表数 | `construction_kanban.csv` 的 `l3_result != '-'` 计数 | ≥30%（每波 2-3 张 / 8-15 张 ≈ 20-37%） |

**为何补 Cognitive Debt + AI-Generated Debt 但不引入完整 AI Debt Score**：
- **补入的价值**：v1.5.0 SQALE 视角未覆盖"AI 生成内容的特殊性"——AI-Generated Debt 是 Fowler 四象限之外的第五类，本审查文档施工由 AI 执行天然存在此风险。补入 Rework rate + L3 抽检覆盖率度量，让"AI 生成快于人理解"的风险可见
- **不引入完整 AI Debt Score 的理由**：[Exceeds AI 2026-06-09](https://blog.exceeds.ai/ai-technical-debt-tracking-workflow/) 的加权 AI Debt Score = f(churn, complexity, survival rate, issue density) 需 code churn 度量（30 天周转 <15% 健康 / >25% 红线）——本审查是文档非代码，code churn 指标需适配为 "doc churn"（文档修订频率），但 102 张表的文档修订频率低（月级波次），churn 信号稀疏不足以支撑加权公式
- **与 §7.0.4 Q score 的关系**：Cognitive Debt 的 Rework rate 与 Q score 的 accuracy 维度互补——Q score 度量"单次施工质量"，Rework rate 度量"AI 生成内容的稳定性"。高 Q score + 高 Rework rate = 单次质量好但不稳定（AI 生成质量方差大）；低 Q score + 低 Rework rate = 稳定地差（AI 生成系统性缺陷）

**Binarly 权重再分配算法（v1.6.0 新增，参考 [binarly.io 2026-04-13 Binarly Risk Score](https://www.binarly.io/blog/binarly-risk-score-introduction)）**：

> §6.0 RICE 公式的 impact_score = code_ref×W1 + risk_flag×W2 + alpha×W3，但若某张表的某分量缺失（如 `hog_futures_core` 的 alpha_potential=0 无法评估、`dividend_tax_node` 的 code_ref=0 真闲置），该分量贡献为 0——等于"缺失值拉低总分"。[Binarly 2026-04-13](https://www.binarly.io/blog/binarly-risk-score-introduction) 的 BRS 系统提出**再分配算法**——缺失 metric 的权重按预定义比例重新分配给其他 metric，避免缺失值导致评分失真。v1.6.0 补入此算法处理 RICE 分量缺失场景。

**再分配规则**（融入 §6.0 RICE 公式）：

```
缺失分量再分配规则（在 priority 计算前执行）：
1. 检测缺失分量：
   - alpha_potential = 0 且无法评估（如真闲置表/采集模板继承）→ 标记 alpha 缺失
   - code_ref = 0（真闲置表）→ 标记 code_ref 缺失
   - risk_flag = N 但该表实际有风险属性未识别 → 不标记（保守方向）

2. 权重再分配（缺失分量的 W 按比例分配给剩余分量）：
   原权重：W1(code_ref)=1.0, W2(risk_flag)=5.0, W3(alpha)=2.0，总和=8.0
   a. 若 alpha 缺失 → W3=2.0 按比例分配给 W1 和 W2：
      W1_new = 1.0 + 2.0 × (1.0 / (1.0+5.0)) = 1.0 + 0.33 = 1.33
      W2_new = 5.0 + 2.0 × (5.0 / (1.0+5.0)) = 5.0 + 1.67 = 6.67
      → 风险权重进一步升高（符合风险优先原则）
   b. 若 code_ref 缺失（真闲置表）→ W1=1.0 按比例分配给 W2 和 W3：
      W2_new = 5.0 + 1.0 × (5.0 / (5.0+2.0)) = 5.0 + 0.71 = 5.71
      W3_new = 2.0 + 1.0 × (2.0 / (5.0+2.0)) = 2.0 + 0.29 = 2.29
      → 闲置表若被识别为风险表（如 dormant 风险红线表），风险权重仍主导

3. 归一化输出：priority = (impact_score × confidence) / effort_score
   impact_score 用再分配后的 W 计算
```

**再分配示例**（`dividend_tax_node` 真闲置表，code_ref=0, alpha=0, risk_flag=N）：
- 原公式：impact = 0×1.0 + 0×5.0 + 0×2.0 = 0 → priority=0（无意义）
- 再分配后：code_ref 和 alpha 均缺失 → W1+W3=3.0 全部分配给 W2 → W2_new = 5.0 + 3.0 = 8.0
  - 但 risk_flag=N(0) → impact = 0×8.0 = 0 → priority 仍为 0
  - **结论正确**：真闲置表无风险标记也无 alpha 价值，priority=0 合理（进 §6.1 生命周期决策而非施工队列）

**为何补再分配算法**：
- **避免缺失值失真**：原公式中 `hog_futures_core` 的 alpha=0（无法评估）直接贡献 0 分——但"无法评估"不等于"无价值"，再分配后风险权重升高，若未来 `hog_futures_core` 被识别为风险表（如生猪期货对冲），priority 会自动升高
- **保守方向**：再分配只将权重转移给**已有分量**，不创造新分量——避免"缺失=0 分"的悲观偏差，也不引入"缺失=均值"的乐观偏差
- **与 §6.0 Kano 分类的对齐**：Kano 基本型表（risk_flag=Y）无论其他分量如何都必须补文档——再分配算法在 risk_flag=Y 时不触发（risk_flag 不缺失），仅在非基本型表的分量缺失时优化评分

**SATD 跨制品传播优先级（v1.7.0 新增，参考 [arXiv 2603.15883v2 PEARC 2026 July Self-Admitted Technical Debt in Scientific Software](https://arxiv.org/html/2603.15883v2)）**：

> 本审查的 §10 开放问题、§6.2 批次 D 暂缓、§9"不做什么"条目本质都是 **Self-Admitted Technical Debt (SATD)**——开发者主动承认的技术债。[arXiv 2603.15883v2 PEARC 2026 July](https://arxiv.org/html/2603.15883v2) 分析 9 个科学软件仓库的 SATD，提出两个关键发现：(1) **跨制品传播**——SATD 从 comment → commit → PR → issue 传播，传播链越长优先级越高（长链 SATD 是 persistent + high impact debt）；(2) **情感放大**——负面情感（"这很 hacky"/"暂时这样"）放大优先级。v1.7.0 补入此方法，用跨制品传播链长度作为 §6.0 RICE priority 的 **confidence 调整因子**。

**SATD 跨制品传播映射**（本审查的 SATD 制品）：

| SATD 类型 | 本审查对应 | 制品位置 | 传播链 |
|---|---|---|---|
| comment SATD | 代码中的 `# TODO`/`# FIXME`/`# 暂时` | src/zephyr/*.py | 单制品（未传播） |
| commit SATD | commit message 中的 "WIP"/"临时"/"hack" | git log | 单制品 |
| PR/issue SATD | §10 开放问题 / §6.2 批次 D 暂缓 | design_memos/*.md | 跨制品（文档→待代码→待 issue） |
| 暂缓 SATD | §9"不做什么"表 + §6.2 批次 D | design_memos/*.md | 跨制品（决策→文档→待施工） |

**传播链长度作为 confidence 调整**：

```
SATD 传播优先级调整（融入 §6.0 RICE confidence 因子）：
1. 扫描 SATD 标记：
   grep -rn "TODO\|FIXME\|暂缓\|暂时\|WIP\|hack" design_memos/*.md src/zephyr/*.py
   → 输出 satd_inventory.csv（位置 × 类型 × 情感 × 关联表名）

2. 计算传播链长度：
   chain_length(table) = SATD 标记跨制品数（comment=1 / commit=2 / PR-issue=3 / 暂缓决策=4）
   → 传播链越长 = 涉及越多制品 = 优先级越高

3. 情感加权：
   负面情感（"hack"/"暂时"/"FIXME"）→ confidence × 1.2（放大优先级）
   中性情感（"TODO"/"待定"）→ confidence × 1.0
   正面情感（"已修复"/"已完成"）→ 不计入 SATD

4. 融入 RICE：
   adjusted_confidence = base_confidence × (1 + 0.1 × (chain_length - 1)) × sentiment_factor
   → 示例：批次 D 暂缓表 chain_length=4, sentiment=负面 → confidence = 0.5 × 1.3 × 1.2 = 0.78
   → 暂缓表的 confidence 被上调（传播链长+负面情感=高优先级债）
```

**为何补 SATD 传播但不引入完整 SATD 分类模型**（对齐 §9）：
- **完整 SATD 分类模型**（[arXiv 2603.15883v2](https://arxiv.org/html/2603.15883v2) 的 semantic embedding-based prioritization heuristic + fine-tuned transformer sentiment）需训练 NLP 模型——个人项目 SATD 数据量不足（~50-100 条标记），不足以训练
- **v1.7.0 用规则映射替代**：grep + 正则识别 SATD 标记 + 手动情感分类（负面/中性）+ 传播链长度计数——轻量实现，覆盖"传播链长=高优先"的核心洞察
- **与 §6.0 Kano 的关系**：Kano 基本型表（risk_flag=Y）的 SATD 传播链天然长（风险债涉及代码+文档+issue+决策）——SATD 传播优先级是 Kano 分类的**量化补充**而非替代

**AI 技术债 7 类映射（v1.7.0 新增，参考 [Institute of AI PM 2026-01-25 AI Technical Debt Assessment Template](https://www.institutepm.com/knowledge-hub/ai-technical-debt-template)）**：

> v1.5.0 SQALE + v1.6.0 Cognitive Debt + AI-Generated Debt 覆盖了文档债务视角，但 [Institute of AI PM 2026-01-25](https://www.institutepm.com/knowledge-hub/ai-technical-debt-template) 提出 AI 系统的 **7 类技术债**（Data/Model/Pipeline/Monitoring/Testing/Documentation/Infrastructure），每类 1-5 分评分。v1.7.0 补入此映射，验证本审查的债务覆盖完整性。

| AI 技术债 7 类 | 定义 | 本审查覆盖 | 状态 |
|---|---|---|---|
| 1. Data Debt | 数据陈旧/未文档化/无验证/无版本 | §2.2 Data Contract Semantics 层 + §6.0 RICE priority + §7.0.4 Q score completeness | ✅ 本审查核心 |
| 2. Model Debt | 模型版本过时/无解释性/复杂度过高 | 不适用（本审查无 ML 模型，design_memos 是文档非模型） | N/A |
| 3. Pipeline Debt | ETL 脆弱/手动步骤/不可复现 | §3.4 Detective 扫描 + §7.0.5 增量更新（文档管道） | ✅ 文档管道覆盖 |
| 4. Monitoring Debt | 无漂移检测/无告警/盲区 | §3.4 Model drift 分类 + §7.0.4 SPC EWMA/CUSUM + §6.1 消费链路主动监控 | ✅ 已覆盖 |
| 5. Testing Debt | 无评估套件/未测边缘用例/无回归 | §7.0.6 L3 语义抽检 + §7.0.9 施工进度看板验收 | ✅ 已覆盖 |
| 6. Documentation Debt | 部落知识/无 model cards/无决策日志 | §6.0 SQALE TDR + Cognitive Debt + AI-Generated Debt + §7.0.4 Q score | ✅ v1.5.0+v1.6.0 已覆盖 |
| 7. Infrastructure Debt | 过度配置/无自动扩缩/供应商锁定 | §9 不引入外部数据目录/不引入 ODCS 工具链 | ✅ §9 已裁定 |

**映射结论**：本审查已覆盖 7 类中的 6 类（1/3/4/5/6/7），第 2 类（Model Debt）不适用（本审查无 ML 模型）。AI 技术债 7 类映射验证了本审查的债务视角完整性——**无需新增独立债务类别**，v1.5.0 SQALE + v1.6.0 Cognitive/AI-Generated Debt + v1.7.0 SATD 传播已覆盖全部适用类别。

### 6.1 真闲置表（v2.1.0 实测仅 1 张 / 4 阶段生命周期决策 / v0.8.0 补消费链路主动监控 / v1.0.0 补调度感知差异化弃用阈值+MIN_AGE_DAYS 安全过滤）

v2.1.0 五源实测（design_memos 46 篇 + src/zephyr/ 代码 + config/ + tasks.yaml + 注册表 yaml）：v0.2.0 的 3 张"真闲置"中，`dividend_tax_node` 与 `msci_adjustment` 已被 17/64 号规划层覆盖（转入 §6.1b），**仅 `index_meta` 保持五源全零引用**。采用 [4 阶段生命周期](https://oneuptime.com/blog/post/2026-01-30-mlops-feature-versioning/view)（2026-01，ACTIVE→DEPRECATED→SUNSET→REMOVED）+ [数据弃用 7 步流程](https://atlan.com/know/data-deprecation-process/)（2026-03）决策，替代二元"归档/保留"：

| # | 表名 | 稳定 path | 生命周期建议 | 理由 |
|---|---|---|---|---|
| 1 | `index_meta` | [market_index_meta](../../../schemas/categories/market_index_meta.py) | → DEPRECATED 观察期（默认建议，待人裁定） | 指数元数据——v0.2.0"补建激活"建议的前提是 `index_constituent` 代码 23 次引用需 meta 配合；v2.1.0 实测 `index_constituent` 已有规划层覆盖、`index_meta` 五源全零，补建价值取决于 62 号 universe/benchmark 注册表是否需要 meta 字段——**若 62 号 P1-A/B 施工不需要 → 确认 DEPRECATED**；若需要 → 转 ACTIVE 补建（§10 Q1） |

> **弃用流程**（[atlan.com 2026-03](https://atlan.com/know/data-deprecation-process/)）：DEPRECATED 标记 → 影响分析（grep 下游消费者）→ 无人认领 → SUNSET（只读 1 季度）→ REMOVED（删 DDL + 采集脚本）。`index_meta` 当前零下游消费者，可直接进 DEPRECATED 观察期。

#### 6.1b 代码零引用但规划已登记（v2.1.0 新增类别，6 张——采集未施工）

以下 6 张表 DDL 已入 git（2026-08-11 提交）且被 17/64 号规划层登记，但 src/zephyr/ 代码、config/、tasks.yaml、注册表**全零引用**——不是"文档缺口"（§6.2）也不是"真闲置"（§6.1），而是**采集/消费链路未施工**：

| # | 表名 | 稳定 path | v2.1.0 实测状态 | 默认建议（待人裁定，§10 Q8） |
|---|---|---|---|---|
| 1 | `dividend_tax_node` | [market_dividend_tax_node](../../../schemas/categories/market_dividend_tax_node.py) | DB 层派生 VIEW（从 rights_issue 实时派生），无 Python 引用属正常 | **免归档**——VIEW 零存储零采集成本，标 dormant 保留；v0.2.0 的 DEPRECATED 建议撤销（当时误判为"需采集的实体表"） |
| 2 | `msci_adjustment` | [market_msci_adjustment](../../../schemas/categories/market_msci_adjustment.py) | 规划已登记（17/64 号），采集未施工 | 保留 DDL + 标 `status: dormant`——MSCI 调仓事件有 alpha 价值（v0.2.0 论证保留），待 26 号事件驱动启用时补采集 |
| 3 | `index_adjustment` | [market_index_adjustment](../../../schemas/categories/market_index_adjustment.py) | 规划已登记，采集未施工（v0.2.0"代码 17 次引用"不可复现） | 同上——指数调仓事件是 26 号既定事件源，待启用时补采集 |
| 4 | `ipo_schedule` | [market_ipo_schedule](../../../schemas/categories/market_ipo_schedule.py) | 规划已登记，采集未施工（v0.2.0"代码 12 次引用"不可复现） | 同上——IPO 日程事件待启用 |
| 5 | `margin_target_adjustment` | [market_margin_target_adjustment](../../../schemas/categories/market_margin_target_adjustment.py) | 规划已登记，采集未施工（v0.2.0"代码 14 次引用"不可复现） | 同上——两融标的调整事件待启用 |
| 6 | `stock_valuation` | [market_stock_valuation](../../../schemas/categories/market_stock_valuation.py) | 2026-08-11 DDL 新增，规划层提及（1 次），采集未施工 | 同上——与 `daily_valuation`（代码 42 次活跃）的口径分工待 15 号明确；注意 MIN_AGE_DAYS=30 安全过滤适用（新建表 30 天内不判闲置） |

> **类别边界**：本类表不进 §6.2 消费文档施工队列（无代码消费可反推，§7.0.2 反推无源），仅登记注册表 + 标 dormant。若后续补采集施工（Provider 任务落地），自动转入 §6.2 队列。与 §6.1 真闲置的区别：本类有明确业务规划（17/64 号登记在册），`index_meta` 无任何消费方规划。
>
> **对 v0.2.0"代码引用"数字的处置**：本类 4 张表（msci/index_adjustment/ipo_schedule/margin_target_adjustment）v0.2.0 报代码引用 0-17 次不等，v2.1.0 五源实测全零——以实测为准（§2.2 不可复现声明）。若采集脚本曾存在后被删除，其 git 历史可查，不影响当前"采集未施工"判定。
**消费链路主动监控（v0.8.0 新增）**：

> 当前 §6.1 的生命周期管理是**被动式**——"标 DEPRECATED → 等 1 季度 → 无人认领则 SUNSET"。[simor consulting 2026-04](https://simorconsulting.com/blog/the-data-pipeline-that-cost-50kmonth--and-the-audit-that-found-why) 的金融数据平台审计案例发现：**31% 的计算花在零消费者管道上**，根因是"平台跟踪了任务依赖（技术依赖）但没跟踪消费依赖（组织依赖）"——管道被创建后从不重新评估。simor 提出**消费链路生命周期管理**（consumption-linked lifecycle），v0.8.0 吸收其"主动监控"思想补强 §6.1 的被动式等待。

**simor 审计的关键发现**（金融贸易结算数据平台，$142K/月 → 节省 $50K/月）：

| 浪费类型 | 占比 | 根因 | 本审查对应 |
|---|---|---|---|
| 零消费者管道 | 31% | 仪表板/ML 模型/报告已弃用但管道未删 | §6.1 的 1 张真闲置表（index_meta）+ §6.1b 的 6 张采集未施工表 |
| 冗余转换 | 22% | 两个团队建了几乎相同的聚合管道 | 未覆盖（个人项目无多团队冗余，但代码可能有重复采集） |
| 过度刷新物化视图 | 14% | 视图每 15 分钟刷新但下游仪表板每日才看 | 未覆盖（ClickHouse 物化视图刷新策略，§6.1 可延伸） |

**simor 的三部分修复系统**（映射到本审查）：

| simor 组件 | 原文 | 本审查映射 | 当前状态 |
|---|---|---|---|
| 消费注册表 | 每个管道必须注册至少一个活跃消费者 | [data_asset_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml) 的 `consumers` 字段 | ⏳ 62 号 P1-B 待施工——补文档时应为每张表登记 `consumers: [文档列表]` |
| 监控层 | 跟踪实际消费（查询日志/API 调用/仪表板刷新） | ClickHouse `system.query_log` + `tasks.yaml` 调度日志 | ❌ 未覆盖——需补"主动消费监控" |
| 自动标记+暂停 | 无消费者 30 天标记 + 60 天暂停 | §6.1 的 DEPRECATED→SUNSET 流程 | ✅ 已有但被动——可补"30 天零查询自动标 DEPRECATED"规则 |

**v0.8.0 补强：主动消费监控规则**（补入 §6.1 生命周期决策）：

```
主动监控规则（替代被动等待）：
1. ClickHouse system.query_log 每周扫描 → 统计每张表过去 30 天的 SELECT 次数
2. tasks.yaml 调度日志每周扫描 → 统计每张表对应 ingestion task 的实际执行次数
3. 若某表过去 30 天 query_count=0 AND task 执行但输出无下游消费 → 自动标 ⚠️ 疑似闲置
4. ⚠️ 疑似闲置表进入 §6.1 DEPRECATED 观察期（不需人工发现，系统主动标记）
5. 观察 1 季度（90 天）仍无消费 → 确认 SUNSET → 按 §7.5 归档流程执行

→ 替代当前"标 DEPRECATED → 等 1 季度"的被动式
→ 优势：1 张已知闲置表（+ §6.1b 六源监控）+ 未来新增的闲置表都能被系统主动发现
```

**为何吸收"主动监控"但不全面采纳 simor 系统**：
- **消费注册表已覆盖**：62 号 data_asset_registry 的 `consumers` 字段等价于 simor 的消费注册表——本审查补文档时同步登记 consumers 即可，无需另建系统
- **监控层轻量实现**：simor 的监控层是多消费者平台（仪表板/API/ML）的综合追踪——本审查仅需 ClickHouse query_log + tasks.yaml 两源，PowerShell 脚本即可实现，无需专门监控基础设施
- **自动暂停不采纳**：simor 的"60 天自动暂停"对金融数据管道风险过高（可能暂停了实际需要的管道）。本审查保留"人工确认 SUNSET→REMOVED 转换"（§10 Q1 决策方=人），主动监控仅"标记 ⚠️ 疑似"不"自动暂停"

**与 §7.0.4 timeliness 的联动**：主动消费监控的"30 天零查询"规则与 §7.0.4 的 half_life=30 天 timeliness 衰减对齐——一张表 30 天无人查询 → timeliness time_decay=0.5（Q 分下降）+ 主动标 ⚠️ 疑似闲置 → 双重信号触发复核。

**调度感知的差异化弃用阈值（v1.0.0 新增）**：

> 上述"30 天零查询"是**统一阈值**——但不同调度频率的表应使用不同 lookback 周期。[有赞无用数据下线自动化 2026-08-07](https://blog.csdn.net/SunnyYoona/article/details/130119357)（2026-08 重发）按任务调度级别设定差异化失败阈值——天级任务 15 天全失败即标疑似下线、月级任务 3 个月、季级 6 个月。[Databricks idle app detection 2026-06](https://www.databricksters.com/p/reclaim-spend-from-idle-databricks) + [AWS Compute Optimizer 2026-06](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-compute-optimizer-six-new-idle/) 也采用"按资源类型配置 lookback"策略。v1.0.0 补入差异化阈值替代统一 30 天——避免"月级表 30 天零查询"的假阳性（月级表本就 30 天才调度一次）。

**差异化弃用阈值表**（按调度频率映射）：

| 调度级别 | 对应表 | lookback 周期 | 触发条件 | 理由 |
|---|---|---|---|---|
| 盘后日级 | `kline_daily` / `money_flow` / `limit_up_down` 等行情类 | 15 天 | 15 天内 query_count=0 AND task 执行但无下游消费 | 日级表每天应被消费，15 天零查询=明确闲置（有赞天级 15 天阈值） |
| 周级 | `kline_weekly` / `stock_valuation` 等周更类 | 6 周 | 6 周内 query_count=0 AND task 执行但无下游消费 | 周级表每周应被消费，6 周零查询=明确闲置（有赞周级 6 周阈值） |
| 月级 | `kline_monthly` / `financial_statement` 等月更类 | 3 个月 | 3 个月内 query_count=0 AND task 执行但无下游消费 | 月级表每月应被消费，3 个月零查询=明确闲置（有赞月级 3 个月阈值） |
| 季级 | `financial_report` / `rights_issue` 等季更类 | 6 个月 | 6 个月内 query_count=0 AND task 执行但无下游消费 | 季级表每季应被消费，6 个月零查询=明确闲置（有赞季级 6 个月阈值） |
| 事件触发 | `ipo_schedule` / `index_adjustment` / `msci_adjustment` | 不适用 | 事件发生后 1 个周期无消费 → 标 ⚠️ | 事件表无固定调度，按"事件发生→消费窗口"判定 |

**MIN_AGE_DAYS 安全过滤（v1.0.0 新增，参考 [Databricks 2026-06](https://www.databricksters.com/p/reclaim-spend-from-idle-databricks) 的 `MIN_AGE_DAYS` + `PROTECTED_APPS` 机制）**：

> 差异化阈值有假阳性风险——**新建表**在初始施工期尚未接入消费方，零查询是正常的，不应标 ⚠️ 闲置。Databricks 的 idle detection 设 `MIN_AGE_DAYS=7`（创建 7 天内的 app 不判定 idle）+ `PROTECTED_APPS` 白名单（关键 app 豁免）。v1.0.0 补入等效安全过滤。

```
安全过滤规则（在差异化阈值判定前执行）：
1. MIN_AGE_DAYS = 30：表创建（schemas/categories/<table>.py 的 git 首次提交日）<30 天 → 跳过闲置判定
   → 理由：新表施工期需 1-2 周接入消费方，30 天内零查询是正常的
2. PROTECTED_TABLES 白名单：以下表豁免闲置判定（Kano 基本型，§6.0 风险红线表）
   → restricted_shares / share_unlock / etf_nav / limit_up_down / margin_trading / kline_daily / trade_calendar
   → 理由：风险模块表即使短期零查询也不应标闲置——可能是"危机时才用"的 dormant table（etf_nav 流动性危机监测）
3. 通过安全过滤后 → 进入差异化阈值判定 → 标 ⚠️ 疑似闲置 → §6.1 DEPRECATED 观察期
```

**为何补差异化阈值但不全面采纳有赞自动下线**：
- **补差异化阈值的价值**：统一 30 天对月级/季级表是假阳性源——`financial_statement` 月级表 30 天零查询不等于闲置（可能只是本月还没到报告期）。差异化阈值消除此类假阳性
- **不采纳有赞自动下线的理由**：有赞的"满足条件→自动下线"对金融数据风险过高（§6.1 v0.8.0 已声明不采纳 simor 的"60 天自动暂停"）。本审查保留"标 ⚠️ → 人工确认 DEPRECATED→SUNSET→REMOVED"（§10 Q1 决策方=人），差异化阈值仅优化"标 ⚠️"的准确性，不改变后续人工确认流程
- **与 §6.0 Kano 分类层的对齐**：PROTECTED_TABLES 白名单 = Kano 基本型表，无论零查询多久都不标闲置——风险红线表的 dormant 状态（危机时才用）不应被误判为闲置

> **注**：v0.1.0 的 43 张"P0-P4 闲置表"经代码层扫描后：40 张为 CODE_ONLY（代码在用，非闲置）。v2.1.0 五源实测再修正：真闲置 3→1 张（§6.1），4 张转 §6.1b 采集未施工类别，§6.2 施工清单以消费层口径重排为 59 张。

### 6.2 消费层文档覆盖缺口施工清单（v2.1.0 重排：59 张代码活跃表，按消费方模块分批补文档）

v2.1.0 实测（§5.1 三层口径）：消费层缺口 = 103 - 37 消费层已覆盖 - 6 张 §6.1b 代码零引用 - 1 张真闲置 = **59 张代码活跃表缺消费级文档**（47 张仅 17/64 号规划层覆盖 + 12 张零覆盖）。**数据已接入，只需补文档记录用法**——v0.1.0"三波接入"是误判（过度工程），v0.2.0 修正为补文档，v2.1.0 以三层口径精确化施工对象。分 4 批按消费方模块归集（批次内排序用 §6.0 RICE/Kano，批次内顺序用 §7.0.3 拓扑）：

> **各批次表格的"代码引用"列数字为 v0.2.0 估值（不可复现，§2.2 声明）**——v2.1.0 已逐表二值核验"代码活跃=✓"，精确计数以下一轮 `audit_data_utilization.ps1` 输出的 CSV 快照为准。"v2.1.0 状态"列为实测：规划层=仅 17/64 号提及；零覆盖=无任何文档命中。

#### 批次 A：风险/回撤模块相关（优先，符合风险优先原则）

> v2.1.0 状态：本批 9 张全部**代码活跃✓ + 规划层已覆盖**（17/64 号），消费级文档均缺——施工内容不变，补写各消费方文档的用法描述节。

| 表名 | 代码引用 | 应补文档 |
|---|---|---|
| restricted_shares | 11 | [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 解禁压力减仓 |
| share_unlock | 9 | [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) 解禁前 30 日减仓提示 |
| block_trade_detail | 9 | [24_daban_strategy_detail](24_daban_strategy_detail.md) 机构折价大宗信号 |
| etf_nav | 17 | [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) 折溢价监测（注：个人系统无一级市场申赎资格，折溢价套利不现实，仅作流动性危机信号——[2026 ETF 套利实证](https://post.m.smzdm.com/p/a6zq30nz/)：散户仅能做二级市场轮动） |
| edb_data | 10 | [10_regime_detector_spec](10_regime_detector_spec.md) 宏观周期输入（[Oxford 2026 论文](https://www.tandfonline.com/doi/pdf/10.1080/14697688.2026.2659195)验证 FRED-MD 100+ 宏观序列对 regime 分类有显著增量；A 股单市场增量主要在风险节流非资产轮动） |
| us_index | 16 | [10_regime_detector_spec](10_regime_detector_spec.md) 外盘风险传导 |
| kline_futures / futures_position / futures_term | 22+20+7 | [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) 期货对冲工具池（需期货账户，90 号 §18 定为 P2 背景级） |

**v0.5.0 补 2026-08 最新实证支撑**（验证批次 A 表的 alpha/风险价值非臆测）：

- **解禁 alpha**（`restricted_shares` / `share_unlock`）：
  - [华泰睿思 2026-06-02](https://finance.sina.com.cn/stock/hkstock/hkstockresearch/2026-06-02/doc-inhzyhiv4725438.shtml) 港股解禁实证：解禁前 7 交易日至后 21 交易日，未经筛选全样本风险规避胜率仅 60.4%/期望收益 5.1%；经 7 因子模型（股东结构+估值+流动性承接力）分层后，**Q1 高压组胜率 72.5%/赔率 1.96x/期望收益 14.4%**，Q1 vs Q4 期望收益剪刀差 20pct；2014-2026Q1 回测年化 23.7%/夏普 2.02/季度胜率 82%。
  - [Alphanume 2026-03-17](https://www.alphanume.com/blog/quantifying-lock-up-overhang) Lock-up Overhang 4 核心指标：(1) 解禁股数 (2) **解禁量/流通股本**（<50% 有限影响 / 50-200% 中等 / 200-500% 大 / >500% 极端）(3) **解禁量/日均成交量=吸收天数**（10 天可吸收 / 50 天结构性压力 / 200 天需数月消化）(4) 持有人集中度（PE/基金→快卖/创始人→不定/赞助商→最可能卖）。
  - [摩根士丹利 2026-07-20](http://m.hibor.com.cn/wap_detail.aspx?id=daf8013b03334554db7570be6b132af9) 2026 下半年港股解禁 8870 亿港元（总市值 2%/自由流通 3.4%），9 月与 7 月为过去五年最大解禁月；个股回归 R²≈0（解禁规模对指数无显著方向性影响），但 700+ 个股事件回归显示解禁规模与个股表现持续负相关。
  - **施工指引**：`restricted_shares` 补文档时应写入 Alphanume 的 4 指标计算口径 + 华泰 7 因子分层逻辑；`share_unlock` 补文档时应写入"解禁前 30 日减仓"硬规则（对应 §6.0 Time Criticality 因子高）。

- **EDB 宏观 regime**（`edb_data`）：
  - [Oxford 2026 论文](https://www.tandfonline.com/doi/pdf/10.1080/14697688.2026.2659195) FRED-MD 100+ 月度宏观序列 + modified k-means（类 fuzzy c-means 算质心距离概率）做 regime 分类，超越 equal-weight/buy-and-hold/random regime。
  - [华福金工 2026-07-11](https://finance.sina.com.cn/wm/2026-07-11/doc-inihmzut8138715.shtml) 五维宏观变量（经济景气/通胀/利率/库存/信用）+ 单边 HP 滤波消除短期波动 + 因子动量划分趋势（上下行）+ 时序百分位划分状态（高中低位）；中证全指择时 2012-2026 年化 15.84%/超额 9.44%，红利指数择时年化 10.77%/超额 8.77%，风格轮动年化 15.85%/超额 6.91%。
  - **施工指引**：`edb_data` 补文档时应标注"宏观因子升维"（边际+状态结合，非单一阈值）+ HP 滤波去噪 + A 股单市场增量主要在风险节流非资产轮动（对应 project_memory 情绪周期/regime 正交边界）。

#### 批次 B：事件驱动/策略模块相关

> v2.1.0 状态：cb_iv 为**零覆盖**（代码 7 次/1 文件）；其余各张规划层已覆盖、代码活跃。

| 表名 | 代码引用 | 应补文档 |
|---|---|---|
| cb_iv | 6 | [26_event_driven_strategy_detail](26_event_driven_strategy_detail.md) 可转债 IV（90 号 §18 可转债 P1 待验证） |
| convertible_bond_list | 7 | [26_event_driven_strategy_detail](26_event_driven_strategy_detail.md) 可转债标的池 |
| ~~msci_adjustment~~ | 移出 | v2.1.0：转 §6.1b（代码零引用+规划已登记，标 dormant 待启用）——不进消费文档队列 |
| calendar_event | 24 | [10_regime_detector_spec](10_regime_detector_spec.md) 事件日历 |
| index_adjustment | 17 | [26_event_driven_strategy_detail](26_event_driven_strategy_detail.md) 指数调仓事件 |
| ipo_schedule | 12 | [26_event_driven_strategy_detail](26_event_driven_strategy_detail.md) IPO 日程 |
| share_change / rights_issue / equity_pledge_detail | 14+10+2 | [26_event_driven_strategy_detail](26_event_driven_strategy_detail.md) 股本变动事件 |
| margin_target_adjustment | 14 | [25_multifactor_strategy_detail](25_multifactor_strategy_detail.md) 融资融券标的调整 |
| stock_valuation | 11 | [15_data_feature_layer_spec](15_data_feature_layer_spec.md) 个股估值 |
| analyst_forecast | 8 | [15_data_feature_layer_spec](15_data_feature_layer_spec.md) 分析师预期（[forage.ai 2026](https://forage.ai/blog/alternative-data-for-hedge-funds/)：alt data 核心在 nowcasting） |

#### 批次 C：板块轮动/行业分类相关

> v2.1.0 状态：concept_board_constituent **零覆盖**（代码 4 次/1 文件）；新增 stock_indicator（零覆盖，代码 12 次/2 文件，v0.2.0 漏列）→ 应补 [15_data_feature_layer_spec](15_data_feature_layer_spec.md) 个股指标节。

| 表名 | 代码引用 | 应补文档 |
|---|---|---|
| concept_sector | 30 | [22_sector_rotation_spec](22_sector_rotation_spec.md) 概念板块 |
| sector_meta | 22 | [22_sector_rotation_spec](22_sector_rotation_spec.md) 板块元数据 |
| sector_list | 19 | [22_sector_rotation_spec](22_sector_rotation_spec.md) 板块列表 |
| index_constituent | 23 | [22_sector_rotation_spec](22_sector_rotation_spec.md) 指数成分 |
| industry_class_suppl | 22 | [15_data_feature_layer_spec](15_data_feature_layer_spec.md) 行业分类补充 |
| concept_board / concept_board_constituent | 10+3 | [26_event_driven_strategy_detail](26_event_driven_strategy_detail.md) 概念分类 |
| auction_book | 9 | 配合 block_trade_detail |
| index_list / market_index | 8+11 | [62_business_registry_construction](62_business_registry_construction.md) 注册表登记 |
| etf_list / lof_list | 15+18 | [62_business_registry_construction](62_business_registry_construction.md) universe 扩展 |
| index_weight | 12 | [62_business_registry_construction](62_business_registry_construction.md) benchmark 扩展 |

#### 批次 D：跨市场/分钟级/衍生品（业务边界待定，暂只记录代码用法）

> v2.1.0 状态：本批含全部零覆盖分钟级 K 线（kline_lof_15min/30min/5min/60min、kline_etf_15min/5min/daily，代码各 2-6 次路由映射级引用）+ hk_kline（10 次）+ cross_validation_log（7 次）——按 §5.3 决议：分钟级 K 线的文档由 16 号技术指标 machinery 的 period 覆盖说明统一承载，不逐表铺文档。

| 表名 | 代码引用 | 说明 |
|---|---|---|
| kline_hk_daily / hk_kline / hk_stock_list / hk_trade_calendar | 10+8+7+14 | 港股——90 号 §18 P1 待验证（A+H 联动） |
| kline_us_daily | 15 | 美股日 K——90 号 §18 P2 背景级 |
| kline_lof_1min/5min/15min/30min/60min | 各 5 | LOF 分钟级——90 号 §18 LOF 是 P0 级（**与 v0.1.0 建议归档矛盾，v0.2.0 修正为保留**） |
| kline_etf_1min/5min/15min | 各 5 | ETF 分钟级——日内套利需高频基础设施 |
| kline_etf_daily | 2 | ETF 日线 |
| kline_cb / kline_sector_intraday | 7+1 | 可转债 K 线 / 板块日内 |
| kline_weekly_hfq / kline_monthly_hfq | 7+7 | 后复权周/月线——**与 [16_technical_indicator_build_plan](16_technical_indicator_build_plan.md) §3.2 三级时间框架栈定义不一致**（16 号用未复权 kline_weekly/kline_monthly），见 §10 Q3 |
| option_kline | 29 | 期权 K 线 |
| realtime_snapshot | 25 | 实时快照 |
| hog_futures_core / hog_province_spot / hog_spot_index | 7+8+7 | 生猪期货——代码有引用但 90 号 §18 未列入覆盖范围，需核实代码是否为采集模板继承 |
| etf_benchmark / cross_validation_log / dragon_tiger_seat / st_stock_list / futures_kline_qmt | 7+6+7+8+3 | 各注册表/验证/风控辅助表 |

## 7. 施工计划（v0.2.0 重写 / v0.3.0 补验收闭环 / v0.4.0 补语义抽检+权重校准 / v0.5.0 补施工算法）

### 7.0 施工标准动作与验收闭环（v0.3.0 新增 / v0.4.0 补语义抽检 / v0.5.0 补施工算法）

> v0.2.0 的施工计划只说"在某文档增补某表"（§7.1-§7.3 步骤表），未定义"增补什么内容、如何从代码反推、表间依赖顺序、文档质量如何度量、代码变更后如何增量更新"。v0.5.0 补入 5 个施工算法子节（§7.0.1-§7.0.5），使施工可重复可验证。验收闭环（v0.3.0/v0.4.0）移至 §7.0.6。

#### 7.0.1 补文档标准模板（per-table template，v0.5.0 新增）

> 参考 [RepoDoc arXiv 2604.26523 2026-04](https://arxiv.org/html/2604.26523v1) 的 API Coverage + Doc Information 5 维度（words/files/cross-references/code blocks/diagrams），定义每张表补文档的**最小内容模板**。避免"补了表名但没写字段含义/消费频率/下游逻辑"的浅覆盖。

**per-table 补文档模板**（每张缺口表在目标消费方文档中至少包含以下 6 字段）：

```markdown
#### <表名>（[schemas/categories/<表名>.py](../../../schemas/categories/<表名>.py)）

- **业务含义**：<1-2 句话说明这张表存什么数据、业务域>
- **关键字段**：<列出现有策略/风控消费的字段，不照搬 DDL 全列>
- **消费频率**：<盘后增量 / 周更 / 月更 / 事件触发>
- **下游逻辑**：<本表数据如何被消费——计算什么指标/触发什么规则/输入什么模型>
- **依赖上游**：<前置表/外部数据源，对应 frontmatter depends_on>
- **实证支撑**：<若有 alpha/风险价值实证，引用 2026 研究链接；若无写"待回测验证">
```

**模板对齐 §7.0.6 验收标准**：
- L1 存在性：表名 + 稳定 path 命中
- L2 消费关系：关键字段 + 下游逻辑 + depends_on 命中
- L3 语义一致：消费频率 + 下游逻辑与代码实际行为一致（人工抽检）

**浅覆盖反例**（不达标）："本策略使用 `restricted_shares` 数据"——仅有表名，无字段/频率/逻辑。
**达标示例**：见 §6.2 批次 A 的 `restricted_shares` 施工指引（Alphanume 4 指标 + 华泰 7 因子 + 解禁前 30 日减仓规则）。

#### 7.0.2 代码反推文档内容（reverse extraction，v0.5.0 新增）

> §6.2 的 61 张缺口表"代码已用，补文档"——但"代码用法"如何提取为文档内容？v0.5.0 补入**代码反推算法**：从代码引用位置反向提取消费模式，生成文档草稿，避免人工逐张读代码。

**反推流程**（对每张缺口表执行）：

```
1. grep 表名 @ src/zephyr/ → 定位所有引用文件（code_ref_count 个文件）
2. 对每个引用文件，提取引用行 ±10 行上下文
3. 按以下模式分类提取：
   a. SQL 查询（SELECT ... FROM <table>）→ 提取 SELECT 字段列表 = "关键字段"
   b. 数据加载（df = read_<table>() / fetch_<table>()）→ 提取后续 df 操作 = "下游逻辑"
   c. 路由映射（{"table": "<table>"}）→ 提取路由触发条件 = "消费频率"
   d. 调度配置（tasks.yaml 引用 <table>）→ 提取 schedule = "消费频率"
4. 汇总各文件的提取结果 → 生成 per-table 文档草稿（套用 §7.0.1 模板）
5. 人工复核草稿（L3 语义抽检）→ 确认无误后写入目标消费方文档
```

**反推的边界**：
- **多消费方冲突**：一张表可能被多个模块消费（如 `etf_nav` 被 37 号流动性危机 + 潜在套利策略消费）——草稿按消费方拆分，各自写入对应文档。
- **隐式消费**：通过中间层（如 `internal_compute_provider` 的 `_PERIOD_MAP`）间接消费的表，反推需追两层（路由表→实际查询）——16 号技术指标表已确认，其余需人工追。
- **不反推 DDL 模板**：§3.5 优先级 2（import 注册）的引用不反推——模板继承不是消费，反推会产出无意义草稿。

**多消费方冲突解决算法**（v0.6.0 新增，补 §7.0.2 的"冲突无解"缺口）：

> §7.0.2 原版"草稿按消费方拆分，各自写入对应文档"未定义**当多消费方对同一表的字段/频率/逻辑描述冲突时如何裁定**。例如 `etf_nav` 在 37 号流动性危机文档应描述"折溢价 >2% 触发预警"，在潜在套利策略文档应描述"折溢价套利信号"——两者消费同一字段但语义不同。v0.6.0 补入**消费方优先级裁定算法**。

**消费方优先级**（与 §6.0 Kano 分类层对齐，参考 [K-AI 6-axis 2026-05](https://www.k-ai.ai/en/news/auditer-corpus-documentaire-ia-methode-6-axes/) 的"inter-document conflicts"轴）：

| 优先级 | 消费方类型 | 裁定权重 | 冲突时处理 |
|---|---|---|---|
| P0 | 风险/回撤/kill_switch 文档（Kano 基本型） | **最高** | 冲突时以此为准——风险语义优先于 alpha 语义 |
| P1 | 策略文档（Kano 期望型，已有显式消费） | 中 | 若与 P0 冲突，标注"风险视角 vs alpha 视角"双语义，不强制统一 |
| P2 | 数据/因子工程总纲（15 号） | 中 | 作为"数据源清单"中立描述，不涉及消费语义 |
| P3 | 注册表文档（62 号） | 低 | 仅登记元数据（表名/业务域/状态），不描述消费逻辑 |
| P4 | 待建文档（无消费方） | 最低 | 仅记录代码用法，不裁定语义 |

**冲突解决流程**（对每张多消费方表执行）：

```
1. 反推阶段（§7.0.2 步骤 1-4）→ 产出 N 份消费方草稿（N = 消费方文档数）
2. 冲突检测：对比 N 份草稿的"关键字段"+"下游逻辑"字段
   - 字段集相同、逻辑描述一致 → 无冲突，各文档直接写入
   - 字段集相同、逻辑描述冲突 → 进步骤 3
   - 字段集不同（各消费方用不同字段）→ 无冲突，各文档写入各自字段子集
3. 冲突裁定（按优先级表）：
   a. 找出最高优先级消费方（P0 风险文档优先）
   b. 以 P0 消费方的语义为"权威描述"
   c. 低优先级消费方文档标注"⚠️ 本文档消费视角与 <P0 文档> 不同：
      P0 视角=<风险预警>；本文档视角=<alpha 信号>；两者均合法，不强制统一"
   d. 不删除低优先级描述——避免"风险视角吞并 alpha 视角"导致 alpha 信号链断裂
4. 写入阶段：各消费方文档按裁定结果写入，跨文档引用对方视角（如 37 号引用 24 号的 alpha 视角）
```

**冲突示例**（`etf_nav` 多消费方）：
- 37 号流动性危机（P0 风险）：`etf_nav` 折溢价 >2% → 触发流动性危机预警（消费频率：盘后批量）
- 24 号打板策略（P1 alpha，假设性）：`etf_nav` 折溢价套利信号（消费频率：盘中实时）
- **裁定**：37 号为 P0 权威描述；24 号标注"⚠️ 与 37 号风险视角不同，本文档为 alpha 视角"；两者均写入，不强制统一消费频率（盘后 vs 盘中）——因实际消费场景不同

**不做的**（对齐 §9）：
- 不强制统一多消费方的字段/频率/逻辑描述——不同消费场景天然有不同语义
- 不做"权威消费方"单点真理——避免 P0 风险视角吞并 P1 alpha 视角
- 不自动裁定冲突——AI 仅标 ⚠️ 提示冲突 + 给出优先级建议，最终写入由人工确认

**DocAgent 多智能体远期升级路径（v0.7.0 新增）**：

> 当前 §7.0.2 的代码反推是"单 pass grep + 上下文提取 + 模板套用"——lightweight 但有局限：无法处理跨文件依赖追踪、无法自动验证生成草稿的准确性。[DocAgent arXiv 2504.08725v3 Meta AI 2025-05](https://arxiv.org/html/2504.08725v3/) 提出多智能体协作文档生成系统，v0.7.0 补入作为远期升级路径。

**DocAgent 架构**（5 智能体协作）：

| 智能体 | 职责 | 对应本审查当前实现 |
|---|---|---|
| Reader | 读取代码文件，提取 AST + 依赖关系 | §7.0.2 步骤 1-2（grep + ±10 行上下文） |
| Searcher | 搜索外部信息（文档/类型定义/调用方）补充上下文 | §7.0.2 步骤 3（路由映射/调度配置提取） |
| Writer | 生成文档草稿 | §7.0.2 步骤 4（套用 §7.0.1 模板） |
| Verifier | 验证生成文档的准确性（Truthfulness 维度） | §7.0.6 L3 语义抽检（人工） |
| Orchestrator | 拓扑排序，按依赖顺序处理 | §7.0.3 Kahn 算法拓扑排序 |

**DocAgent 的核心创新**：
1. **拓扑处理顺序**（Navigator）：按代码依赖 DAG 拓扑序处理——被依赖模块先生成文档，依赖模块可引用已生成文档。**与本审查 §7.0.3 的 Kahn 算法拓扑排序思想完全一致**——验证了 §7.0.3 的正确性
2. **Truthfulness 评估**：多智能体协作中 Verifier 检查 Writer 输出是否与代码行为一致——**与本审查 §7.0.6 L3 语义抽检 + §7.0.4 Q score accuracy 维度一致**
3. **增量上下文构建**：处理依赖模块时复用被依赖模块已生成的文档作为上下文——本审查 §7.0.2 当前无此机制（每张表独立反推），是潜在升级点

**为何不当前采纳 DocAgent**：
- **成本**：DocAgent 需 5 个 LLM 智能体协作，每张表生成需多次 LLM 调用——个人项目 61 张缺口表的 LLM 成本过高
- **复杂度**：多智能体编排需额外基础设施（agent orchestrator + 状态管理）——本审查 PowerShell 脚本 + 人工复核已满足
- **Truthfulness 已覆盖**：§7.0.6 L3 抽检 + §7.0.4 Q score 已覆盖 DocAgent Verifier 的功能，虽为人工但成本可接受（每批次 2 张抽检）
- **远期触发条件**：当 design_memos 增长到 100+ 篇、L3 人工抽检成本上升时，可引入 DocAgent 自动化 Verifier 替代人工——列入远期升级路径，当前不施工

**DocAgent 对本审查的验证价值**：DocAgent 的拓扑处理顺序（Navigator）+ Truthfulness 评估与本审查 §7.0.3（拓扑排序）+ §7.0.6 L3（语义抽检）+ §7.0.4 accuracy（Q score）高度对齐——**证明本审查的 lightweight 实现与学术界 SOTA 在核心思路上一致**，差异仅在自动化程度（人工 vs 智能体）。

#### 7.0.3 表间依赖拓扑排序（v0.5.0 新增 / v0.9.0 补 Louvain 社区发现 / v1.0.0 补 CPM 关键路径 / v1.6.0 升级 Louvain→Leiden / v1.7.0 补 Temporal Coupling 隐藏依赖 / v1.8.0 补 commit-size 归一化+Sum of Coupling+min-heap 确定性排序+DFS 三色标记环路径提取）

> §6.2 按消费方模块分批（A/B/C/D），但未考虑表间依赖（如 `index_constituent` 依赖 `index_list`，`sector_constituent` 依赖 `sector_list`）。若先补依赖表再补被依赖表，被依赖表的"下游逻辑"字段无法引用未补的依赖表——导致返工。v0.5.0 补入拓扑排序，确保同批次内**被依赖表先补**。

**已知表间依赖关系**（从 schemas/categories 的 DDL 外键 + 代码 import 推断）：

| 被依赖表（先补） | 依赖表（后补） | 依赖性质 |
|---|---|---|
| `stock_list` | `st_stock_list` / `stock_valuation` / `daily_valuation` | 标的池派生 |
| `index_list` | `index_constituent` / `index_weight` / `index_adjustment` / `index_meta` | 指数族派生 |
| `sector_list` | `sector_constituent` / `sector_meta` / `sector_snapshot` / `kline_sector` | 板块族派生 |
| `concept_board` | `concept_board_constituent` / `concept_sector` | 概念族派生 |
| `etf_list` | `etf_nav` / `etf_benchmark` / `kline_etf_*` | ETF 族派生 |
| `lof_list` | `kline_lof_*` | LOF 族派生 |
| `convertible_bond_list` | `cb_iv` / `kline_cb` | 可转债族派生 |
| `stock_list` + `trade_calendar` | `kline_daily` / `money_flow` / `limit_up_down` | 行情类依赖标的池+日历 |

**拓扑排序规则**（同批次内执行）：
1. 构建依赖 DAG（有向无环图）：被依赖表 → 依赖表
2. Kahn 算法拓扑排序：入度=0 的表先补（无前置依赖）
3. 同层表按 §6.0 priority 降序补（高分先补）；**同 priority 用 min-heap 确定性打破平局**（v1.8.0 新增）——Kahn 的队列改为按 (priority DESC, table_name ASC) 排序的优先队列，确保同层同分表的施工顺序**可复现**（多次运行拓扑排序结果一致），避免"随机队列顺序导致施工计划不可复现"（参考 [spacecomplexity.ai 2026-05-24](https://spacecomplexity.ai/blog/topological-sort-algorithm)：Kahn 队列换 min-heap 得字典序最小拓扑序，O(V log V + E)）
4. 跨批次依赖（如批次 A 的 `etf_nav` 依赖批次 C 的 `etf_list`）：**先补 `etf_list` 的最小文档（仅表名+业务含义），再补 `etf_nav` 完整文档**——避免跨批次阻塞
5. **环检测**（v1.5.0 显式补入，参考 [thecodeforge.io 2026-03 Topological Sort](https://thecodeforge.io/dsa/topological-sort/)）：Kahn 算法天然支持环检测——若输出的拓扑序长度 < 节点总数，说明 DAG 中存在环（有环则环内节点入度永不为 0，无法被 Kahn 处理）。[thecodeforge.io 2026-03](https://thecodeforge.io/dsa/topological-sort/) 强调"always pair topological sort with cycle detection"——v1.5.0 显式补入环检测的处理流程：
   - **检测**：`topo_order.csv` 的行数 < 依赖图节点数 → 存在环
   - **定位**：未被 Kahn 处理的节点（入度始终 >0）即为环内节点
   - **处理**：表间依赖不应存在环（表 A 依赖表 B，表 B 依赖表 A 是设计错误）——若检测到环，标记为 ⚠️ 架构异常，记入 `architecture_issue_registry.yaml`（ARCH 条目），人工裁定打破环（通常某条依赖是错误的，如视图依赖被误标为表依赖）
   - **为何此前未显式说明**：v0.5.0 补入 Kahn 算法时隐性依赖"DAG 必须无环"前提（行 1035 "Kahn 已验证"），但未说明"检测到环后怎么处理"——v1.5.0 补入此流程闭合环检测缺口

**环路径提取增强（v1.8.0 新增，DFS 三色标记 + Tarjan SCC）**：

> v1.5.0 的 Kahn 环检测能"检测到环存在 + 定位环内节点集合"，但**无法输出环的边路径**（即 A→B→C→A 的具体环链）。对于"记入 architecture_issue_registry.yaml 供人工裁定打破环"的场景，仅知道"环内节点是 {A,B,C}"不够——需知道"环的走向是 A→B→C→A 还是 A→C→B→A"才能判断哪条边是错误的。[quant67.com 2026-06-08](https://quant67.com/post/algorithms/48-topo-sort/topo-sort.html) + [spacecomplexity.ai 2026-05-24](https://spacecomplexity.ai/blog/topological-sort-algorithm) 指出 Kahn 的"结果长度<V 则有环"只能判定存在性，环路径提取需 DFS 三色标记或 Tarjan SCC。v1.8.0 补入此增强。

**DFS 三色标记法提取环路径**（[spacecomplexity.ai 2026-05-24](https://spacecomplexity.ai/blog/topological-sort-algorithm)，O(V+E)）：

```
三色标记：white（未访问）/ gray（正在 DFS 中，在递归栈里）/ black（已完成）
对每个 white 节点启动 DFS：
  标记当前节点为 gray
  对每条出边 u→v：
    若 v 为 gray → 发现 back edge → v→...→u→v 构成环
      → 从 v 沿递归栈回溯到 v 本身，输出环路径 [v, ..., u, v]
    若 v 为 white → 递归 DFS(v)
  标记当前节点为 black

→ 输出 cycle_paths.csv（环路径 × 涉及节点 × 涉及边）
→ 注意：单一 visited 数组（boolean）无法正确检测有向图环——
  共享节点会被误判为环（A→C, B→C 中 C 被两次访问但无环），
  三色标记的 gray 状态专门区分"在当前 DFS 路径上"vs"已完成"
```

**Tarjan SCC 作为远期升级路径**（[quant67.com 2026-06-08](https://quant67.com/post/algorithms/48-topo-sort/topo-sort.html) §四，O(V+E)）：

> 若依赖图复杂（环嵌套/多环交叉），DFS 三色标记逐个输出环路径可能遗漏交叉环。Tarjan 强连通分量（SCC）算法一次性识别所有 SCC——|SCC|>1 的分量即为环——并构建**凝聚 DAG**（condensation graph，每个 SCC 缩为一个超节点）。本审查 102 表规模下 DFS 三色标记已足够（环数量预期 ≤2，多为视图依赖误标），Tarjan SCC 作为"环数量>5 时的升级路径"记录，不当前实施。

**为何补 DFS 三色标记但不实施 Tarjan SCC**：
- **DFS 三色标记的成本**：在 Kahn 环检测触发后才运行（非常驻），仅需 Kahn 已检测到环时调用——零常态开销
- **Tarjan SCC 的过度工程**：102 表的依赖图预期无环或极少环（表间依赖是树形/森林结构），Tarjan SCC 的"多环交叉"场景在本仓库不会出现——记录为远期路径即可
- **与 v1.5.0 Kahn 环检测的关系**：Kahn 检测"有没有环"→（有环时）DFS 三色标记提取"环路径"→（环复杂时）Tarjan SCC 识别"所有 SCC"——三层递进，按需升级

**实施**：拓扑排序脚本封装进 `scripts/audit_data_utilization.ps1`，输出 `topo_order.csv`（表名 × 拓扑层 × priority × 批次），供施工时按序执行。若检测到环，额外输出 `cycle_warning.csv`（环内节点 × 依赖关系 × 建议打破方式）+ `cycle_paths.csv`（v1.8.0 新增：DFS 三色标记提取的具体环路径）。

**社区发现算法用于批次聚类（v0.9.0 新增 / v1.6.0 升级 Louvain→Leiden）**：

> §6.2 按消费方模块分批（A/B/C/D），§7.0.3 Kahn 拓扑排序处理批次内依赖顺序——但两者都是**人工预设的批次边界**。[社区发现算法](https://calmops.com/algorithms/community-detection-algorithms/)（[CSDN 2026-08-07](https://blog.csdn.net/agito_cheung/article/details/148170240) + [calmops.com 2026-03](https://calmops.com/algorithms/community-detection-algorithms/)）可从依赖图自动发现**紧耦合表簇**——同一社区内的表应作为一个整体补文档，避免"依赖表跨批次阻塞"。v0.9.0 补入此方法作为 §6.2 批次划分的**验证工具**。v1.6.0 升级 Louvain→Leiden——[metricgate.com 2026-02-03](https://metricgate.com/blogs/community-detection-louvain-vs-leiden/) + [IJARCSE 2026](https://ijarcse.org/index.php/ijarcse/article/download/106/151/457) 确认 Leiden 修复 Louvain 两大已知 bug，2026 年已成行业共识。

**社区发现算法选型**（5 种经典算法对比）：

| 算法 | 原理 | 复杂度 | 适用场景 | 本审查适用性 |
|---|---|---|---|---|
| **Louvain** | 模块度优化，迭代合并节点 | O(n·log²n) | 大规模网络，层次化社区 | ✅ 102 张表规模适中，模块度优化自动发现"指数族/板块族/ETF 族"等簇 |
| **Leiden** | Louvain 改进版，解决分辨率限制 | 更快 | 需精确小社区 | ✅ 可调分辨率参数 γ——γ>1 倾向小社区（单表级），γ<1 倾向大社区（域级） |
| Girvan-Newman | 边介数分裂 | O(n³) | 小网络，精确划分 | ❌ 102 表规模 O(n³) 可接受但不如 Louvain 高效 |
| 谱聚类 | 拉普拉斯矩阵特征向量 | O(n³) | 社区结构清晰 | ❌ 需预设 k 个社区——本审查不想预设社区数 |
| Infomap | 信息论随机游走 | O(n·log²n) | 抗噪声，嵌套社区 | ⚠️ 过于复杂，本审查无需嵌套社区 |

**选型结论**：**Leiden 算法**——v1.6.0 从 Louvain 升级。[metricgate.com 2026-02-03](https://metricgate.com/blogs/community-detection-louvain-vs-leiden/) + [IJARCSE 2026](https://ijarcse.org/index.php/ijarcse/article/download/106/151/457) 确认 Leiden 修复了 Louvain 两大已知 bug：(1) **分辨率限制**——Louvain 倾向合并小社区为大社区，可能将"指数族"和"板块族"误合；(2) **断连社区**——Louvain 产出的社区内部可能不连通（节点间无路径），违反社区定义。Leiden 保证社区连通性 + 细粒度可调（γ 参数），2026 年已成行业共识。Louvain 仅作为 Leiden 不可用时的降级备选。

**Leiden 在本审查的应用**：

```
1. 构建表间依赖图 G=(V, E)
   V = 102 张表（节点）
   E = 依赖关系（边）：若 table_B 依赖 table_A（§7.0.3 依赖表），则添加边 A→B
   边权重 = 依赖强度（1=派生关系，2=外键关系，3=同族 DDL 继承）

2. 运行 Leiden 算法（γ=1.0 默认，可调） → 输出社区划分 C={C1, C2, ..., Ck}
   每个社区 Ci 内的表紧耦合（高内聚），社区间松散（低耦合）
   Leiden 保证每个社区内部连通（无断连节点）

3. 对比 §6.2 人工批次 A/B/C/D 与 Leiden 社区划分：
   - 若人工批次与社区划分一致 → 验证 §6.2 批次边界合理
   - 若某社区跨越多个批次 → 该社区的表应合并到同一批次（避免跨批次阻塞）
   - 若某批次内含多个小社区 → 该批次可拆分为子批次并行施工

4. 预期社区（基于 §7.0.3 已知依赖）：
   - 指数族社区：index_list + index_constituent + index_weight + index_adjustment + index_meta
   - 板块族社区：sector_list + sector_constituent + sector_meta + sector_snapshot + kline_sector
   - 概念族社区：concept_board + concept_board_constituent + concept_sector
   - ETF 族社区：etf_list + etf_nav + etf_benchmark + kline_etf_*
   - 可转债族社区：convertible_bond_list + cb_iv + kline_cb
   - 行情核心社区：stock_list + trade_calendar + kline_daily + money_flow + limit_up_down
   → 与 §6.2 批次 A/B/C 高度重合，验证批次划分合理
```

**为何不替代 §6.2 人工批次而仅作验证**：
- **业务语义优先**：§6.2 按消费方模块分批（风险/事件驱动/板块轮动）体现了**业务优先级**（风险优先原则），社区发现按**依赖密度**分批不含业务语义——Leiden 可能将"风险表+非风险表"分到同一社区（因依赖密度高），但业务上风险表应优先
- **人工批次 + 社区验证 = 双重保障**：§6.2 人工批次保证业务优先级，Leiden 验证"批次内表是否真紧耦合"——若发现"某批次内表零依赖"则说明该批次是"凑数批次"应拆分
- **实施成本**：Leiden 需 networkx + python-igraph 库（`pip install python-igraph leidenalg`）——轻量，可封装进 `scripts/community_detection.py` 作为验证步骤，不影响主流程

**实施位置**：社区发现验证脚本封装进 `scripts/community_detection.py`（Python，因 networkx/igraph 无 PowerShell 等价），输出 `community_map.csv`（表名 × 社区 ID × 模块度贡献 × 是否连通），与 `topo_order.csv` 交叉对比验证批次边界。

**Temporal Coupling 隐藏依赖检测（v1.7.0 新增，参考 [codebase-memory-mcp #928 2026-07-07](https://github.com/DeusData/codebase-memory-mcp/issues/928) + [iterathon.tech Repository Intelligence 2026-01](https://iterathon.tech/blog/repository-intelligence-ai-code-understanding-enterprise-2026)）**：

> §7.0.3 Kahn 拓扑排序依赖**声明显式依赖**（DDL 外键/派生关系），Leiden 社区发现依赖**静态依赖图**——两者都只看"代码里写了什么"。但表之间还存在**动态隐藏依赖**：两张表没有显式 DDL 依赖，但它们的 DDL 文件或消费代码**频繁在同一 commit 中修改**（co-change），说明它们在业务上紧耦合——只是没人写进依赖声明。[codebase-memory-mcp #928](https://github.com/DeusData/codebase-memory-mcp/issues/928)（2026-07-07）提出 `co_changed` 指标——symbol 粒度的时序耦合（temporal coupling），generalizing `FILE_CHANGES_WITH` edges——在 ~12k 节点仓库上 cold query ~58ms / warm ~24ms。[iterathon.tech 2026-01](https://iterathon.tech/blog/repository-intelligence-ai-code-understanding-enterprise-2026) 引用 GitHub Repository Intelligence 2026 将"Historical Context"（change frequency per component / bug density clustering / refactoring impact radius）列为 AI 代码理解的四大维度之一。v1.7.0 补入此方法补齐 §7.0.3 的"动态依赖"盲区。

**Temporal Coupling 算法**（基于 git log co-change 分析）：

> **CodeScene 三信号说明**（[CodeScene 3.5.23 Temporal Coupling](https://docs.enterprise.codescene.io/versions/3.5.23/guides/technical/temporal-coupling.html)）：CodeScene 考虑两模块时序耦合的三种信号——(a) **同一 commit 修改**（co-change）、(b) **同一程序员在特定时间段内修改**、(c) **commit message 引用同一 Ticket ID**。本审查为个人+AI 项目（单一开发者），信号 (b) 的"程序员维度"无区分力（所有 commit 同一作者），信号 (c) 的"Ticket ID 维度"在本仓库无 ticket 追踪系统——**仅采用信号 (a) 同一 commit co-change**，以 Jaccard 系数量化。信号 (b)/(c) 作为团队规模化后的远期升级路径记录。

```
1. 提取 commit→files 映射：
   git log --name-only --pretty=format:"%H" -- schemas/categories/ src/zephyr/
   → 构建映射 {commit_hash: [file1, file2, ...]}

1.5 commit-size 归一化过滤（v1.8.0 新增，参考 [Archy #131 2026-05-25](https://github.com/hslee16/Archy/issues/131)）：
   大 commit（如初始化/批量重构/全仓格式化）会同时触碰几十个文件 → co-change 矩阵被"噪声 commit"污染
   （Archy #131 明确指出"large commits couple everything"是 temporal coupling 的首要 FP 源）
   过滤规则：
     若 |commit.files| > MAX_FILES_PER_COMMIT（默认 15）→ 从 co_change 矩阵中剔除该 commit
     （15 = 本仓库 schemas/categories 102 表的 ~15%，超过此阈值的 commit 多为批量操作而非业务耦合）
     → 输出 filtered_commits.csv（被过滤的 commit × file_count × 过滤原因）供审计

2. 构建共现矩阵 co_occurrence[table_A][table_B]：
   遍历每个**未过滤** commit 的 file 列表：
     若 commit 同时修改了 table_A 和 table_B 的文件 → co_occurrence[A][B] += 1
   （table_X 的文件 = schemas/categories/{prefix}_table_X.py + src/zephyr/ 中引用 table_X 的 .py）

3. 计算 Jaccard 时序耦合度：
   temporal_coupling(A, B) = co_occurrence[A][B] / |commits(A) ∪ commits(B)|
   = 共同修改次数 / (A 被修改的 commit 数 ∪ B 被修改的 commit 数)
   → 范围 [0, 1]，1 = A 和 B 每次都一起改，0 = 从不一起改
   → 注：Jaccard 分母用并集而非交集，已天然惩罚"高频改 A 偶尔碰 B"的假阳性

3.5 Sum of Coupling 聚合度（v1.8.0 新增，参考 [CodeScene Sum of Coupling](https://docs.enterprise.codescene.io/versions/3.5.23/guides/technical/temporal-coupling.html#dig-deeper-with-sum-of-coupling)）：
   sum_of_coupling(A) = Σ temporal_coupling(A, B) for all B ≠ A
   → 衡量表 A 与所有其他表的时序耦合总量——高 SoC 表是"枢纽表"，施工时需优先关注
   （因其变更牵连多表文档同步），低 SoC 表是"孤岛表"，可独立施工
   → 输出 sum_of_coupling 排序，与 §5.2 热度分布交叉验证（高 SoC 应≈高引用热度）

4. 识别隐藏依赖：
   threshold = 0.5（可调——50% 以上的 commit 共同修改视为强时序耦合）
   对每对 (A, B)：
     若 temporal_coupling(A, B) ≥ threshold 且 A→B 不在 §7.0.3 静态依赖图 → 标 ⚠️ 隐藏依赖
     → 输出 hidden_dependency.csv（table_A × table_B × coupling_score × is_in_static_graph × sum_of_coupling_A × sum_of_coupling_B）
```

**预期发现的隐藏依赖**（基于本仓库已知模式）：

| 表对 | 预期 temporal_coupling | 静态依赖 | 隐藏依赖? | 原因 |
|---|---|---|---|---|
| `kline_daily` ↔ `money_flow` | 高（~0.8） | 无显式 DDL 依赖 | ⚠️ 是 | 日线行情与资金流几乎每次行情升级都一起改 |
| `restricted_shares` ↔ `share_unlock` | 高（~0.9） | 无显式 DDL 依赖 | ⚠️ 是 | 解禁数据两个表同源（巨潮），采集脚本一起改 |
| `dragon_tiger` ↔ `dragon_tiger_seat` | 高（~0.95） | 无显式 DDL 依赖 | ⚠️ 是 | 龙虎榜明细+营业部，业务逻辑一体 |
| `kline_daily` ↔ `kline_daily_hfq` | 极高（~0.99） | 有（派生关系） | 否（已在静态图） | 后复权由原始日线派生 |
| `etf_list` ↔ `etf_nav` | 中（~0.4） | 无 | 可能（阈值附近） | ETF 基础信息与净值更新频率不同步 |

**为何补 Temporal Coupling 但仅作验证不替代 Leiden**：
- **Leiden = 静态结构依赖**（DDL 声明），**Temporal Coupling = 动态行为依赖**（实际共变）——两者正交
- Leiden 可能遗漏"无 DDL 依赖但业务紧耦合"的表对（如 `dragon_tiger` ↔ `dragon_tiger_seat`），Temporal Coupling 可发现
- Temporal Coupling 可能产生假阳性（两张表因同一 sprint 任务被一起改，但业务上无依赖）——需人工复核
- **三层验证**：Kahn（拓扑序）+ Leiden（静态社区）+ Temporal Coupling（动态共变）构成完整的施工调度依赖分析

**与 §7.0.3 Kahn + Leiden + CPM 的关系**：
- Kahn 拓扑排序：解决"被依赖表先补"的**顺序**问题
- Leiden 社区发现：解决"哪些表是静态紧耦合簇"的**分组**问题
- Temporal Coupling：解决"哪些表实际一起变化"的**隐藏依赖**问题
- CPM 关键路径：解决"哪些表延误影响最大"的**工期**问题
- 四者正交可叠加——施工调度四件套

**实施位置**：Temporal Coupling 分析封装进 `scripts/temporal_coupling.py`（Python，因需 gitpython + 矩阵运算），输出 `hidden_dependency.csv`（table_A × table_B × coupling_score × is_in_static_graph × sum_of_coupling_A × sum_of_coupling_B × 建议）+ `filtered_commits.csv`（v1.8.0：被 commit-size 归一化过滤的 commit × file_count × 过滤原因）+ `sum_of_coupling_ranking.csv`（v1.8.0：表名 × SoC 聚合度 × 排名），与 `topo_order.csv` + `community_map.csv` + `critical_path.csv` + `cycle_paths.csv`（v1.8.0：DFS 三色标记提取的环路径）五表交叉——施工调度四件套完整闭环。predict Omissions 分析（§7.0.5 v1.8.0）复用同一 `scripts/temporal_coupling.py` 的 Jaccard 共现矩阵，额外输出 `predicted_omission.csv`（schema_file × doc_file × schema_commit_count × omission_severity）。

**冷启动约束**：Temporal Coupling 需 git 历史数据。本仓库若 commit 数 < 50（schemas/categories/ 相关），时序耦合度统计不显著——冷启动期仅记录 co_change raw count，不计算 coupling score；commit 数 ≥ 50 后启用 Jaccard 计算。

**CPM 关键路径识别（v1.0.0 新增）**：

> §7.0.3 Kahn 拓扑排序保证"被依赖表先补"，Leiden 社区发现验证批次边界——但两者都未识别**关键路径**：批次内最长依赖链决定该批次总工期，关键路径上的表（零时差）若延误则全批延期。[Critical Path Method (CPM) 2026](https://symplprocess.com/learn/critical-path-method) 通过计算总时差（Total Float）识别零时差的关键活动，v1.0.0 补入此方法优化批次内施工资源分配——关键路径表优先保障，非关键路径表有浮动可并行。

**CPM 计算步骤**（基于 §7.0.3 依赖 DAG）：

```
1. 为每张表估算施工 duration（§7.0.8 effort 评分 × 2 人天/分）
   → 示例：effort=3 的表 duration=6 人天

2. 前推计算（Forward Pass）——从入度=0 的表开始：
   ES(表) = max(所有前置表的 EF)   # Earliest Start = 前置全完成后最早能开始
   EF(表) = ES + duration           # Earliest Finish

3. 后推计算（Backward Pass）——从出度=0 的表倒推：
   LF(表) = min(所有后置表的 LS)    # Latest Finish = 不延误后继的最晚完成
   LS(表) = LF - duration            # Latest Start

4. 总时差 TF = LS - ES = LF - EF    # Total Float = 可延迟而不影响总工期的余量

5. 关键路径 = 所有 TF=0 的表组成的最长路径
   → TF=0 的表无任何余量，延误一天则全批延期一天
```

**批次 A 示例**（风险/回撤模块，依赖链 `stock_list → kline_daily → money_flow → restricted_shares`）：

```
表名                duration  ES   EF   LS   LF   TF   关键?
stock_list          4         0    4    0    4    0    ✅ 关键路径
kline_daily         6         4    10   4    10   0    ✅ 关键路径
money_flow          4         10   14   10   14   0    ✅ 关键路径
restricted_shares   4         14   18   14   18   0    ✅ 关键路径
etf_nav             3         4    7    11   14   7    ❌ 非关键（TF=7，可延迟 7 天）

→ 关键路径：stock_list → kline_daily → money_flow → restricted_shares（总工期 18 天）
→ etf_nav 有 7 天浮动，可与关键路径表并行施工，资源不冲突
→ 若 restricted_shares 延误 1 天 → 全批从 18 天延到 19 天（关键路径零时差）
→ 若 etf_nav 延误 5 天 → 全批不受影响（TF=7 > 5，仍在浮动范围内）
```

**CPM 在本审查的施工指导价值**：
- **资源优先分配**：关键路径表（TF=0）优先分配施工精力——若个人项目单线程施工，先做关键路径表可最小化总工期
- **并行机会识别**：非关键路径表（TF>0）可在关键路径表施工间隙并行补——如 etf_nav 可在 kline_daily 施工期间并行补（不依赖 kline_daily）
- **跨批次依赖的工期估算**：批次 A 的关键路径总工期（18 天）决定第二波最早开始时间——若关键路径延误则第二波顺延

**为何补 CPM 但不替代 Kahn 拓扑排序**：
- **Kahn 解决"顺序"**（谁先谁后），**CPM 解决"工期"**（谁延误影响最大）——两者正交
- Kahn 是 CPM 的前置：CPM 的前推/后推计算依赖 Kahn 产出的拓扑序（DAG 必须无环，Kahn 已验证）
- 个人项目单线程施工时 CPM 的"并行机会"价值有限（无人并行），但"关键路径表优先"的指导仍有价值——避免在非关键表上耗时导致关键表来不及

**实施位置**：CPM 计算封装进 `scripts/audit_data_utilization.ps1` 的拓扑排序后步骤，输出 `critical_path.csv`（表名 × ES × EF × LS × LF × TF × is_critical），与 `topo_order.csv` + `community_map.csv` 三表交叉——拓扑序（Kahn）+ 社区（Leiden）+ 关键路径（CPM）构成完整的施工调度三件套。

#### 7.0.4 文档质量度量（Q score，v0.5.0 新增 / v0.6.0 升级 timeliness 为指数衰减 / v0.7.0 补乘法模型对比+高斯衰减 / v0.9.0 补 Syntropy+Doc-Entropy Ratio / v1.0.0 补 SPC EWMA/CUSUM 趋势分析）

> §7.0.6 验收闭环的 L1/L2/L3 是"通过/不通过"的二元判定，无法度量"文档质量高低"。v0.5.0 补入**文档质量分 Q**（0-10 分），参考 [DataQ 框架](https://publicationslist.org/data/jorge-martinez-gil/ref-175/dataq.pdf) 的 completeness/accuracy/consistency/timeliness 四维 + [sustainablecatalyst 2026-06](https://sustainablecatalyst.com/documentation-model-cards-and-datasheets-for-algorithms/) 的 Q=(A+C+S+T+X+N)/6。v0.6.0 将 timeliness 从二元（同步/未同步）升级为**指数衰减新鲜度**——参考 [guiguio "Stale Docs" 2026-05](https://web-guiguio.b-cdn.net/blog/2026-05-07-stale-docs-confident-wrong-answers-rag-knowledge-base) + [happysupport.ai Freshness Scoring 2026-05](https://happysupport.ai/blog/llm-knowledge-base-freshness-scoring) + [WikiMonitor-onto JAAI 2026](https://www.jaai.net/vol4/JAAI-V4N3-66.pdf)：**"昨天编辑的文档也可能结构上过时"**（若系统在编辑后一小时变更），timestamp 不等于 freshness。

**Leading vs Lagging 指标区分（v1.5.0 新增，参考 [affine.pro 2026-07-10 Knowledge Base Metrics](https://affine.pro/blog/knowledge-base-metrics)）**：

> [affine.pro 2026-07-10](https://affine.pro/blog/knowledge-base-metrics) 区分 leading indicators（前瞻性，预测未来表现）与 lagging indicators（回顾性，度量过去结果）——"treat both the same way is like checking the weather forecast and yesterday's temperature with equal urgency"。v1.5.0 补入此分类视角，明确本审查各度量机制的指标类型，避免"所有度量混为一谈"导致响应策略错配。

| 指标类型 | 定义 | 本审查对应 | 响应策略 |
|---|---|---|---|
| **Lagging（回顾性）** | 度量已发生的结果 | **§7.0.4 Q score**（施工后评分，度量已完成的文档质量）/ **§7.0.6 L3 抽检通过率**（验收结果）/ **§7.0.9 看板 Done 计数**（已完成表数）/ **§6.0 SQALE TDR**（当前债务比，度量已有缺口） | 事后改进——Q score 低→返工，L3 未过→回滚，TDR 高→加速施工 |
| **Leading（前瞻性）** | 预测未来问题的信号 | **§3.4 Detective 扫描**（提前发现漂移，在消费方受影响前）/ **§7.0.4 SPC EWMA 趋势**（Q score 渐进下降预警，在跌破 7.0 前干预）/ **§7.0.4 Nelson Rules 模式识别**（非随机模式预警）/ **§3.4 Model drift 数据漂移**（表名分布变化→未来引用断裂预警）/ **§6.0 贝叶斯权重偏差**（预期 vs 实际偏差→权重失效预警） | 事前干预——Detective 发现漂移→增量更新，EWMA 下降→权重校准，Nelson 命中→诊断模式启用 |

**为何需要两类指标**（affine.pro 2026-07 的核心洞察）：
- **只有 lagging 无 leading**——等问题发生后才发现（Q score 已低→文档已影响消费方），响应滞后
- **只有 leading 无 lagging**——有预警但不知道当前状态（EWMA 预警但不知道整体 Q score 水平），无法判断严重度
- **本审查的双层覆盖**：§3.4 Detective + §7.0.4 SPC（leading）提前预警 + §7.0.4 Q score + §6.0 SQALE TDR（lagging）度量现状——leading 告诉"将要出什么问题"，lagging 告诉"现在有多严重"
- **与 MTTD/MTTR 的联动**（§7.0.9 v1.4.0）：MTTD 短 = leading 指标有效（Detective 扫描快）；MTTR 短 = lagging 响应有效（回滚修复快）。两者共同度量"leading→lagging 全链路"的效能

**Q score 计算公式**（每张已补文档的表评分）：

```
Q = (completeness + accuracy + specificity + timeliness) / 4

completeness (0-10)：§7.0.1 模板 6 字段填充比例 × 10
  - 6 字段全填 = 10；3 字段填 = 5；仅表名 = 1.7
accuracy (0-10)：L3 语义抽检通过率 × 10
  - 抽检 2 张全过 = 10；过 1 张 = 5；全不过 = 0（需返工）
specificity (0-10)：文档是否含具体字段/规则/阈值（非泛泛"使用本表"）
  - 有具体字段+规则+阈值 = 10；有字段无规则 = 6；仅"使用本表" = 2
timeliness (0-10，v0.6.0 指数衰减)：freshness_score × 10
  freshness_score = α × semantic_alignment + (1-α) × time_decay
  - α = 0.7（语义对齐权重，参考 guiguio 默认）
  - semantic_alignment (0-1)：文档描述的用法是否对齐代码最新版本
      代码 git log 显示用法变更且文档已同步 = 1.0
      代码变更未同步 = 0.3
      无变更（代码稳定）= 1.0
  - time_decay = 2^(-age_days / half_life_days)
      half_life = 30 天（design_memos 月更节奏，比 help center 14 天慢）
      age_days = 自文档最后同步代码用法的天数
      age=0 → decay=1.0（刚同步）；age=30 → decay=0.5；age=90 → decay=0.125
  - 示例：代码 60 天前变更未同步 → semantic=0.3, age=60, decay=0.25
      timeliness = (0.7×0.3 + 0.3×0.25) × 10 = (0.21+0.075)×10 = 2.85（需返工）
  - 示例：代码 10 天前变更已同步 → semantic=1.0, age=10, decay=0.79
      timeliness = (0.7×1.0 + 0.3×0.79) × 10 = (0.7+0.237)×10 = 9.37（达标）
```

**为何用指数衰减而非二元**（[guiguio 2026-05](https://web-guiguio.b-cdn.net/blog/2026-05-07-stale-docs-confident-wrong-answers-rag-knowledge-base)）：
- 二元 timeliness（"同步=10/未同步=3"）在 age=1 天和 age=89 天都给 3 分——但 89 天前未同步的文档比 1 天前未同步的危险得多（代码已漂移更远）
- 指数衰减 `2^(-age/half_life)` 让"长期未同步"的文档 Q 分持续下降，触发自动返工——避免"未同步但 Q=7 凑合用"的假达标
- [happysupport.ai 2026-05](https://happysupport.ai/blog/llm-knowledge-base-freshness-scoring)："Freshness score is not the same as a last-modified timestamp"——必须度量"文档与所描述系统的差距"，不是"文档与上次按键的差距"

**加法模型 vs 乘法模型对比（v0.7.0 新增）**：

> 本审查 §7.0.4 的 `freshness_score = α × semantic_alignment + (1-α) × time_decay` 是**加法（加权融合）模型**。[Milvus 2.6 Time-aware Ranking Functions 2025-11](https://m.aitntnews.com/newDetail.html?newId=19523) 采用**乘法模型** `final_score = normalized_similarity × decay_score`——两种模型对"时效性"的处理哲学不同，v0.7.0 补入对比以确认本审查选型合理。

| 维度 | 加法模型（本审查采用） | 乘法模型（Milvus 2.6） |
|---|---|---|
| 公式 | `α × semantic + (1-α) × time_decay` | `similarity × decay_score` |
| 时效性极低时行为 | semantic=1.0, time_decay=0 → score=0.7（仍保留 70% 语义分） | similarity × 0 → score=0（彻底归零） |
| 适用场景 | 文档质量评估（旧文档仍有语义参考价值，仅降权不归零） | 检索排序（旧文档不应出现在结果前列，归零是期望行为） |
| 参数敏感度 | α 可调（0.6-0.8），单参数 | origin/scale/offset/decay 四参数，需语料校准 |
| 本审查选型理由 | Q score 度量的是"文档质量"非"检索排名"——旧文档语义价值不应被时效归零（如 16 号技术指标文档 3 年未改仍有效），加法模型保留语义基线更合理 | Milvus 场景是"实时检索排序"——旧文档必须沉底，乘法归零是正确的 |

**结论**：本审查 Q score 保留加法模型——文档质量评估与检索排序的目标不同，旧文档的语义价值不应被时效性乘法归零。若未来将 design_memos 接入 RAG 检索系统，检索层应改用 Milvus 乘法模型（旧文档沉底），但 Q score 质量评估层维持加法模型。

**高斯衰减备选（v0.7.0 新增）**：

> [Milvus 2.6](https://m.aitntnews.com/newDetail.html?newId=19523) + [amicited.com 2026](https://www.amicited.com/glossary/ai-content-freshness-decay/) 指出三种衰减曲线：指数（初始快速衰减后有长尾）/ 高斯（铃形曲线渐进衰减）/ 线性（直线有明确截止点）。本审查当前用指数衰减 `2^(-age/half_life)`，v0.7.0 补入高斯衰减作为备选。

```
高斯衰减：time_decay_gauss = exp(-age² / (2 × sigma²))
  - sigma = half_life / 1.1774（使 age=half_life 时 decay≈0.5）
  - 特征：初期衰减比指数慢，中后期比指数快——铃形曲线
  - 适用：文档价值在"近期稳定 + 中期快速失效 + 远期归零"的场景

指数衰减（当前采用）：time_decay_exp = 2^(-age / half_life)
  - 特征：初期衰减快，后期长尾——新闻/快变内容
  - 适用：design_memos 月更节奏，代码变更后文档应快速标记失准

线性衰减：time_decay_linear = max(0, 1 - age / max_age)
  - 特征：均匀衰减，有硬截止
  - 适用：有明确过期日期的文档（如法规合规文档）
```

**选型理由**：design_memos 是"代码变更驱动"的文档——代码改了文档应立即标记失准（指数初期快速衰减符合），但远期文档仍有历史参考价值（长尾保留）。高斯衰减的"初期慢"不符合"代码变更后应快速感知"的需求。**保留指数衰减，高斯作为备选记录**。

**参数敏感性警告（v0.7.0 新增）**：

> [Temporal RAG arXiv 2509.19376v2 2026-06](https://arxiv.org/html/2509.19376v2) 的实证结论：**"Freshness via a recency prior is thus real but partial and parameter-sensitive, not solved"**——半衰期 recency prior 在合成数据上 Latest@10=1.00，但在真实 CERT 日志语料上用合成调参的默认值时降到 0.00，需语料专用调参才恢复到 1.00。

**对本审查的启示**：
- §7.0.4 的 `half_life = 30 天` 是基于 design_memos 月更节奏的初始估计，**未经实证校准**
- 第一波施工后应校准 half_life：对比"实际被发现过时的文档 age"分布，若大多数过时文档在 15 天内被发现 → half_life 应降为 15 天（衰减更快）；若大多数在 60 天后才被发现 → half_life 应升为 60 天
- [amicited.com 2026](https://www.amicited.com/glossary/ai-content-freshness-decay/) 实证："70% of pages cited by ChatGPT were updated within the past year, 30% within 3 months"——暗示 half_life 在 90 天量级对"AI 引用偏好"合理，但本审查的文档非 AI 检索对象，half_life 应更短（文档-代码一致性比 AI 引用新鲜度更时效敏感）
- **不把 half_life 写死**——纳入 §6.0 权重校准循环，每波施工后与 W2/W3 权重一同重评

**Q score 阈值**：
- `Q ≥ 7.0` → 文档质量达标（计入覆盖率分子）
- `4.0 ≤ Q < 7.0` → 需补强（不计入覆盖率，标 ⚠️）
- `Q < 4.0` → 需返工（L3 抽检未过或模板字段缺失 >50%）

**Q score 与覆盖率的区别**：
- 覆盖率（§5.1）= 有文档的表数 / 总表数（二元，有无）
- Q score = 文档质量高低（连续，好坏）
- **覆盖率 97% 但平均 Q=3.0 = 全是浅覆盖，比覆盖率 50% 但 Q=9.0 更糟**——Q score 防止"为凑覆盖率而浅覆盖"

**度量频率**：每波施工后对当波补的表评 Q score，写入 `docs/_audit/quality_score.csv`。每波目标：当波补的表平均 Q ≥ 7.0。**timeliness 维度每日重算**（age_days 随时间增长），触发 Q 跌破 7.0 的表标 ⚠️ 待复核——避免"施工时 Q=9，半年后 Q=4 但无人知晓"的静默腐烂。

**编码会话级新鲜度（v0.9.0 新增）**：

> 当前 timeliness 的 time_decay = `2^(-age_days / half_life)` 是**纯时间驱动**——代码 30 天没改，文档也 30 天没同步，time_decay=0.5。但 [Syntropy 2025-12](https://github.com/delorenj/syntropy) 提出**编码会话驱动的新鲜度**（staleness based on coding sessions, not just time）——"文档年龄应基于代码是否被编辑过，而非纯时间流逝"。v0.9.0 补入此维度作为 time_decay 的**修正因子**。

**Syntropy 的核心洞察**：
- 纯时间驱动的 time_decay 存在**假阴性**——代码 90 天没改（稳定），文档也没改，但 time_decay=0.125 使 timeliness 跌到 7.4（接近阈值），触发不必要的"⚠️ 待复核"
- 编码会话驱动的 freshness 只在**代码实际变更后**才开始衰减——代码稳定则文档 freshness 保持不变
- Syntropy 用 `coding_session_count_since_sync`（自上次文档同步后的代码编辑次数）替代 `age_days`——0 次编辑 = 完全新鲜，无论过了多少天

**修正后的 timeliness 公式（v0.9.0）**：

```
timeliness_v09 = (α × semantic_alignment + (1-α) × time_decay_corrected) × 10

time_decay_corrected = time_decay × session_factor

session_factor：
  - code_sessions_since_sync = 0（代码未变更）→ session_factor = 1.0（不衰减）
  - code_sessions_since_sync = 1-3（少量变更）→ session_factor = 0.9（轻微衰减）
  - code_sessions_since_sync = 4-10（中量变更）→ session_factor = 0.7（中度衰减）
  - code_sessions_since_sync > 10（大量变更）→ session_factor = 0.5（重度衰减）

→ 示例：代码 90 天未改（稳定），session_factor=1.0
   time_decay = 0.125, time_decay_corrected = 0.125 × 1.0 = 0.125
   timeliness = (0.7×1.0 + 0.3×0.125) × 10 = 7.4 → ⚠️ 仍触发

→ 修正：若 semantic_alignment=1.0（已同步）且 code_sessions=0 → 额外 boost
   timeliness_final = min(10, timeliness_v09 + session_boost)
   session_boost = 0.5（代码稳定+已同步=额外加 0.5 分，封顶 10）
   timeliness_final = min(10, 7.4 + 0.5) = 7.9（不触发⚠️）
```

**为何保留 time_decay 不完全替换为 session_factor**：
- 纯 session 驱动有**假阳性**风险——代码 90 天没改，但**外部环境变了**（如 ClickHouse 版本升级导致 SQL 语法变更、数据供应商 API 变更），文档虽与代码一致但与外部环境不符
- time_decay 保留"即使代码没变，文档也应定期复核"的提醒——避免"代码稳定 5 年，文档描述的 ClickHouse 语法早已过时"的隐性腐烂
- **双因子乘法**（time_decay × session_factor）兼顾两种风险：时间驱动防外部环境漂移，会话驱动防代码稳定时的假阴性

**Doc-Entropy Ratio 复合度量（v0.9.0 新增）**：

> [SITS2026 香农-组织信息论 2026-04](https://blog.csdn.net/LogicShoal/article/details/160023770)（SITS2026 奇点智能技术大会）首次发布**组织信息熵**（OIE）的行业基准值，其中 **Doc-Entropy Ratio = 文档更新滞后于代码变更的平均天数 / 文档被实际引用频次**——将"新鲜度"与"使用频率"复合。v0.9.0 补入此度量作为 Q score timeliness 维度的**补充指标**。

**SITS2026 行业基准**：

| 组织类型 | OIE (bits) | Doc-Entropy Ratio | 含义 |
|---|---|---|---|
| AI-Native Startup | 2.1 | 0.14 | 文档滞后 0.14 天/次引用——近乎实时同步 |
| Legacy Enterprise (AI-augmented) | 5.9 | 4.62 | 文档滞后 4.62 天/次引用——中等滞后 |
| Pre-AI Enterprise | 7.4 | 12.8 | 文档滞后 12.8 天/次引用——严重滞后 |

**Doc-Entropy Ratio 公式**（本审查适配版）：

```
doc_entropy_ratio = avg_lag_days / reference_count_30d

avg_lag_days：该表的文档最后同步日距代码最后变更日的天数（滞后天数）
reference_count_30d：过去 30 天该表文档被 design_memos 其他文档引用的次数（§3.2 层 1 hit count）

→ 示例：restricted_shares 文档滞后 5 天（代码 5 天前改了未同步）
   reference_count_30d = 8（8 篇文档引用）
   doc_entropy_ratio = 5 / 8 = 0.625（接近 AI-Native 基准 0.14，健康）

→ 示例：dividend_tax_node 文档滞后 90 天
   reference_count_30d = 0（零引用——真闲置表）
   doc_entropy_ratio = 90 / 0 = ∞（无限大——文档滞后但无人引用，熵影响为零）
   → 特殊处理：reference_count=0 时 doc_entropy_ratio 设为 0（不影响任何消费者）
```

**Doc-Entropy Ratio 的价值**（超越 Q score timeliness 单维）：
- Q score timeliness 只度量"文档多旧"——一张 90 天未同步但零引用的表 timeliness=7.4（⚠️），但实际熵影响为零
- Doc-Entropy Ratio 复合"旧 × 无人用"——零引用表的 doc_entropy_ratio=0（无影响），高引用表的 doc_entropy_ratio 高（影响大）
- **优先级排序**：高 doc_entropy_ratio 的表应优先补文档（滞后天数多 + 引用频次高 = 影响大），低 doc_entropy_ratio 的表可延后（要么已同步，要么无人引用）

**与 §6.0 RICE 评分的关系**：doc_entropy_ratio 可作为 §6.0 impact_score 的**第六个分量**（现有 5 个：code_ref/risk_flag/alpha_potential/consumers/doc_complexity）——但 v0.9.0 暂不融入 RICE 公式（避免公式过度复杂化），仅作为 Q score 的补充指标记录在 `quality_score.csv`，供人工优先级复核参考。

**Q score 趋势分析：SPC 控制图（v1.0.0 新增）**：

> 当前 Q score 是**点态测量**——每波施工后评分，threshold ≥7.0 判达标。但点态测量无法检测**渐进式质量退化**——如 Q score 从 9.0→8.5→8.0→7.5→7.1 连续 5 波下降，每波都"达标"但趋势明显恶化，应在跌破 7.0 前**提前预警**。[AIAG-VDA SPC Manual 2026 July](https://leoardent.com/2026/07/what-is-new-in-the-aiag-vda-spc-manual-key-changes-explained/)（汽车工业统计过程控制手册）引入 **EWMA（指数加权移动平均）** 和 **CUSUM（累积和）** 控制图检测渐进漂移——v1.0.0 借鉴此方法补入 Q score 的**时间序列趋势分析**。

**为何需要 SPC 趋势分析**（AIAG-VDA 2026 的核心洞察）：
- 传统 Shewhart 控制图（3σ 上下限）只检测**单点越界**——Q=6.9 越界触发⚠️，但 Q 从 9.0 连续 5 波降到 7.1 不触发任何告警
- EWMA 让最近数据权重更高、过去数据逐渐减弱——**更早发现"过程正在慢慢漂移"的趋势**
- CUSUM 累积偏差的方向性——**捕捉持续、方向一致的小幅变化**（如连续 5 波 Q 下降）
- AIAG-VDA 2026 的核心原则："只有当过程在统计学上稳定时，Cpk 才有意义"→ 对应本审查："只有当 Q score 过程稳定时，Q≥7.0 阈值才有意义"——若 Q score 波动剧烈（时而 9 时而 5），说明施工质量不稳定，单次 Q≥7.0 不可信

**EWMA 控制图公式**（本审查适配）：

```
EWMA_t = λ × Q_t + (1-λ) × EWMA_{t-1}

λ = 0.2（平滑系数——AIAG-VDA 2026 推荐 0.1-0.3，越小越平滑越敏感于趋势）
Q_t = 第 t 波施工后该表的 Q score
EWMA_0 = 初始 Q score（首次施工后的评分）

控制限：
UCL = EWMA_mean + 3 × σ_EWMA × sqrt(λ/(2-λ))
LCL = EWMA_mean - 3 × σ_EWMA × sqrt(λ/(2-λ))
σ_EWMA = Q score 波间标准差

→ 示例：restricted_shares 5 波 Q score = [9.0, 8.5, 8.0, 7.5, 7.1]
   EWMA_1 = 0.2×9.0 + 0.8×9.0 = 9.0
   EWMA_2 = 0.2×8.5 + 0.8×9.0 = 8.9
   EWMA_3 = 0.2×8.0 + 0.8×8.9 = 8.72
   EWMA_4 = 0.2×7.5 + 0.8×8.72 = 8.48
   EWMA_5 = 0.2×7.1 + 0.8×8.48 = 8.20
   → EWMA 从 9.0 持续降到 8.20——趋势恶化预警（虽然 Q=7.1 仍 ≥7.0 达标）
   → 若 LCL=7.5 → EWMA=8.20 未越界但接近——标 ⚠️ 趋势观察
```

**CUSUM 累积和公式**（本审查适配）：

```
S_t^+ = max(0, S_{t-1}^+ + (Q_t - μ_0) - k)    # 检测上升趋势（质量改善）
S_t^- = min(0, S_{t-1}^- + (Q_t - μ_0) + k)    # 检测下降趋势（质量退化）

μ_0 = 目标 Q score（7.0，达标阈值）
k = 参考值（0.5σ，允许的正常波动半幅）
h = 决策阈值（4σ，CUSUM 超过 h 则告警）

→ 示例：5 波 Q = [9.0, 8.5, 8.0, 7.5, 7.1]，μ_0=7.0，k=0.5
   S^+ 一直为 0（Q > μ_0+k=7.5 时累积正偏差，但不是质量问题）
   S^- = min(0, 0 + (9.0-7.0)+0.5) = 0（Q=9 远高于目标，无退化）
   → Q=7.1 时 S^- = min(0, 0 + (7.1-7.0)+0.5) = 0（仍无退化信号）
   → CUSUM 对"从高位缓慢下降但仍达标"不敏感——EWMA 更适合此场景
   → CUSUM 适合"从达标线附近持续小幅低于目标"（如 Q=[7.0, 6.9, 7.0, 6.8, 6.9]）
```

**EWMA vs CUSUM 选型**（AIAG-VDA 2026 的指导）：

| 控制图 | 擅长检测 | 本审查适用场景 | 选型 |
|---|---|---|---|
| **EWMA** | 缓慢、渐进的过程漂移 | Q score 从 9.0 连续 5 波降到 7.1（高位退化） | ✅ **主选**——design_memos 施工质量更可能"缓慢退化"而非"突变" |
| **CUSUM** | 持续、方向一致的小幅变化 | Q score 在 7.0 附近持续小幅低于目标（7.0, 6.9, 7.0, 6.8, 6.9） | ✅ **补充**——检测"达标线附近的质量波动" |
| Shewhart | 单点突变（3σ 越界） | Q score 突然从 9.0 跌到 4.0 | ✅ 已有——当前 Q<4.0 返工机制 |

**三图联用策略**：Shewhart（单点突变）+ EWMA（渐进漂移）+ CUSUM（小幅持续偏低）= 全覆盖 Q score 质量异常模式。

**AIAG-VDA 2026 时间相关过程模型**（映射到本审查）：

| 模型 | AIAG-VDA 定义 | 本审查对应 | 策略 |
|---|---|---|---|
| Model A（理想） | 均值恒定+变异恒定 | Q score 各波稳定在 8.0±0.5 | ✅ 正常——继续当前施工流程 |
| Model B | 均值恒定但变异变化 | Q score 均值 8.0 但波间标准差从 0.5 涨到 2.0 | ⚠️ 施工质量不稳定——检查 §7.0.8 effort 估算是否准确 |
| Model C（磨损型） | 变异恒定但均值漂移 | Q score 标准差 0.5 但均值从 9.0 漂移到 7.1 | ⚠️ 渐进退化——检查 §7.0.5 增量更新是否遗漏，或 §6.0 权重是否需校准 |
| Model D（混沌型） | 均值+变异均不可预测 | Q score 时而 9 时而 4，无规律 | 🔴 紧急停工——§7.0.7 L4 全波回滚 + 排查施工流程系统性问题 |

**实施位置**：SPC 控制图计算封装进 `scripts/quality_spc.py`（Python，因 EWMA/CUSUM 需 scipy.stats），输出 `quality_spc.csv`（表名 × EWMA值 × CUSUM值 × 趋势状态 × 模型分类），每周与 §6.1 主动消费监控一同触发。

**SPC 冷启动阶段处理（v1.1.0 新增）**：

> EWMA/CUSUM 控制图需 ≥5 个数据点才能建立稳定的控制限（UCL/LCL）——但第一波施工前无历史 Q score 数据，无法计算 σ_EWMA 和基线均值。AIAG-VDA 2026 的"过程稳定才计算 Cpk"原则在此存在冷启动缺口。v1.1.0 补入冷启动三阶段处理。

**冷启动三阶段**：

| 阶段 | 波次 | 数据点数 | SPC 状态 | 操作 |
|---|---|---|---|---|
| **冷启动期** | 第 1-2 波 | ≤4 | EWMA/CUSUM 不可用 | 仅用 Shewhart 单点检测（Q<4.0 返工 / Q≥7.0 达标）+ 记录 Q score 到 `quality_spc.csv` 作为基线数据积累 |
| **预热期** | 第 3-4 波 | 5-8 | EWMA 可用，CUSUM 不可用 | EWMA 开始计算（λ=0.2）但控制限宽松（±3σ 改为 ±4σ 适应小样本噪声）；CUSUM 仅记录累积值不告警（需 ≥10 点稳定 μ_0） |
| **稳态期** | 第 5 波+ | ≥10 | EWMA+CUSUM 全功能 | 标准 3σ 控制限 + CUSUM k=0.5σ/h=4σ 告警阈值；进入 AIAG-VDA 2026 四模型分类（理想/变异/磨损/混沌） |

**冷启动期的替代趋势监控**：在 EWMA/CUSUM 不可用时（冷启动期），用"相邻波次 Q score 差值"做粗粒度趋势检测——若 |Q_t - Q_{t-1}| > 2.0（单波跳变 >2 分）则标 ⚠️ 异常波动（可能是 §7.0.8 Rubric 评分不稳定或施工质量波动），触发人工复核。这是 Shewhart 单点检测的"差值变体"——不检测绝对值越界，检测波间跳变。

**为何允许冷启动期"降级"到 Shewhart**：
- Shewhart 单点检测（Q<4.0 返工）是 SPC 的最基础形态——冷启动期数据不足以支撑 EWMA/CUSUM 的统计推断，但不意味着"无监控"
- 冷启动期的核心任务是**积累基线数据**——每波的 Q score 都写入 `quality_spc.csv`，为预热期/稳态期的 EWMA/CUSUM 计算提供历史序列
- 个人项目施工波次少（3 波），冷启动期+预热期可能覆盖全部施工——但 SPC 的价值延伸到施工后的运维期（§7.0.4 timeliness 持续衰减），稳态期在施工完成后仍有意义

**Western Electric / Nelson 规则（Shewhart 模式识别，v1.2.0 新增 / v1.3.0 修正名称准确性）**：

> §7.0.4 SPC 三图联用（Shewhart+EWMA+CUSUM）覆盖了"单点越界"（Shewhart）、"渐进漂移"（EWMA）、"小幅持续偏低"（CUSUM），但 Shewhart 控制图本身还有一类"非随机模式"未利用——Western Electric 规则（1956）与 Nelson 规则（1984 Lloyd S. Nelson 扩展）定义的 8 种异常模式。v1.2.0 补入此规则作为 Shewhart 控制图的增强，无需新增控制图，仅在现有 Shewhart 点上做模式识别。

**v1.3.0 名称修正**（参考 [metricgate.com 2026-05 Nelson Rules](https://metricgate.com/docs/nelson-rules-control-chart/) + [DolphinDB SPC 实战 2026-08-09](https://blog.csdn.net/sinat_41617212/article/details/163544780)）：v1.2.0 标题用"Western Electric 规则"但 Rule 2 判异条件用了"9 点连续在中心线一侧"——这实际是 **Nelson Rules** 的标准（1984），而非 Western Electric 原始标准（1956 的 7-8 点）。[ppapdocuments.com 2026-07](https://ppapdocuments.com/2026/07/10/how-to-read-a-control-chart-out-of-control-signals-and-the-western-electric-rules/) 显示现代实践中两者已融合，但严格来说"9 点"来自 Nelson。v1.3.0 修正标题为"Western Electric / Nelson 规则"并明确采用 Nelson 的"9 点"标准（更保守，假阳性更低）。

**8 种异常模式**（采用 Nelson 规则标准，映射到本审查 Q score 场景）：

| 规则 | 模式 | 本审查 Q score 场景 | 处理 |
|---|---|---|---|
| Rule 1 | 1 点超出 3σ 控制限 | Q=3.5（远低于 7.0 阈值，3σ 下限之外） | 立即返工（§7.0.7 L1 单表回滚） |
| Rule 2 | 9 点连续在中心线一侧 | 连续 9 波 Q 均 >8.5（高于均值，单侧偏置） | 检查是否过度保守——half_life 可能过长导致 Q 不反映最新施工质量，考虑缩短 half_life |
| Rule 3 | 6 点连续上升或下降 | Q 从 9.0→8.5→8.0→7.5→7.1→6.8（连续 6 波下降） | 触发 EWMA 预警 + §6.0 权重校准（W2 可能需下调，因风险表 Q 在降） |
| Rule 4 | 14 点交替上下 | Q 波动 8.2→7.3→8.1→7.4→8.0→7.5→...（14 波交替） | 检查 §7.0.8 Rubric 评分是否不稳定——effort 估算或 doc_complexity 判断在两值间摇摆 |
| Rule 5 | 连续 3 点中 2 点在 2σ 之外（同侧） | Q=[9.0, 6.5, 9.2, 6.8]（3 点中 2 点低于 μ-2σ） | 中等强度异常——检查是否有周期性施工质量问题（如每偶数波质量掉） |
| Rule 6 | 连续 5 点中 4 点在 1σ 之外（同侧） | Q=[9.0, 8.8, 6.5, 6.8, 9.1, 6.6]（5 点中 4 点偏离均值 1σ 以上） | 弱异常——可能暗示两类表（高质量/低质量）混合在同一批次，检查 §6.2 批次划分是否合理 |
| Rule 7 | 15 点连续在 1σ 之内（两侧） | Q 在 7.9-8.1 之间波动 15 波（变异过小） | 检查 Q score 评分是否丧失区分度——可能 Rubric 评分标准过于宽松，所有表都给 8.0 |
| Rule 8 | 连续 8 点在 1σ 之外（两侧） | Q=[6.5, 9.0, 6.8, 9.2, 6.6, 9.1, 6.7, 9.0]（8 点均偏离均值 1σ 以上） | 变异过大——施工质量两极分化，检查是否有两个不同质量的施工流程在并行 |

**与 EWMA/CUSUM 的分工**（避免重复检测）：

| 控制图/规则 | 擅长检测 | 与 Western Electric 的关系 |
|---|---|---|
| Shewhart 3σ | 单点突变 | Western Electric Rule 1 即 Shewhart 基本规则——Rule 1 之外是 Western Electric 的增量 |
| EWMA | 渐进漂移 | Western Electric Rule 3（6 点连续下降）与 EWMA 检测的漂移重叠——EWMA 更早预警（加权平均），Western Electric 更直观（点数计数） |
| CUSUM | 小幅持续偏低 | Western Electric Rule 2（9 点单侧）与 CUSUM 检测的持续偏差重叠——CUSUM 更敏感（累积和），Western Electric 更易解释 |
| Western Electric Rule 4-8 | 非随机模式（交替/分层/过窄/过宽） | EWMA/CUSUM 不覆盖——Western Electric 的独有价值 |

→ v1.2.0 落码：Western Electric 规则作为 Shewhart 的**后处理步骤**——先跑 Shewhart 3σ（Rule 1）+ EWMA + CUSUM，再对 Shewhart 的历史点序列跑 Rule 2-8 模式识别。封装进同一 `scripts/quality_spc.py`，输出 `quality_spc.csv` 新增 `we_rule` 列（命中的规则编号，逗号分隔）。

**Nelson Rules 误报率风险矩阵（v1.4.0 新增，参考 [ifactoryapp 2026-06-25 Pharma SPC](https://ifactoryapp.com/blog/western-electric-nelson-rules-pharma)）**：

> [ifactoryapp 2026-06-25](https://ifactoryapp.com/blog/western-electric-nelson-rules-pharma) 警告：全部启用 8 条 Nelson 规则的误报率从单规则 0.27%（ARL~370）升到约 1-2%（ARL~91，4 倍误报），"8-10 周内摧毁操作员信任"——某制药厂启用全部规则后两周内每班 3-5 次告警，操作员停止阅读，QA 停止调查，六个月后真实异常出现时无人注意。v1.4.0 补入风险矩阵，明确本审查 Q score 场景应启用哪些规则子集。

**Nelson 与 Western Electric 的精确关系**（[metricgate 2026-05-28](https://metricgate.com/docs/nelson-rules-qcc/) + [ifactoryapp 2026-06-25](https://ifactoryapp.com/blog/western-electric-nelson-rules-pharma) 验证 v1.3.0 修正准确性）：
- **Nelson 是 Western Electric 的超集**——Nelson Rules 1/2/5/6 分别等同 Western Electric Rules 1/4/2/3
- Nelson 增加了 4 个模式检测规则（3/4/7/8）：趋势/交替/分层/过分散
- **启用全部 8 条 Nelson 已自动覆盖全部 4 条 Western Electric**——决策不是"WE 还是 Nelson"，而是"为每个参数启用 8 条中的哪个子集"

**本审查 Q score 场景的规则启用矩阵**（risk-based subset selection）：

| 规则 | 模式 | 独立误报率 | 本审查启用 | 理由 |
|---|---|---|---|---|
| Rule 1 | 1 点超 3σ | 0.27%（ARL~370） | ✅ **必启用** | 非协商性——Q<4.0 立即返工是基础底线 |
| Rule 2 | 9 点单侧 | 0.20%（ARL~390） | ✅ **启用** | 检测缓慢漂移（Q 持续高于/低于均值）——Q score 场景核心需求 |
| Rule 3 | 6 点连续升降 | 0.27%（ARL~370） | ✅ **启用** | 检测连续下降趋势——与 EWMA 互补，EWMA 更早预警但 Rule 3 更直观 |
| Rule 4 | 14 点交替 | 0.46%（ARL~220） | ⚠️ **条件启用** | 误报率最高（0.46%）——仅在稳态期（≥14 数据点）且 Rubric 评分疑似不稳定时启用 |
| Rule 5 | 3 点中 2 点超 2σ | 0.20%（ARL~390） | ✅ **启用** | 中等强度异常——检测周期性质量问题 |
| Rule 6 | 5 点中 4 点超 1σ | 0.20%（ARL~390） | ⚠️ **条件启用** | 弱异常——仅在批次划分疑似不合理（两类质量表混合）时启用 |
| Rule 7 | 15 点在 1σ 内 | 0.20%（ARL~390） | ⚠️ **条件启用** | 检测区分度丧失——仅在怀疑 Rubric 评分过于宽松时启用 |
| Rule 8 | 8 点在 1σ 外 | 0.20%（ARL~390） | ⚠️ **条件启用** | 检测变异过大——仅在怀疑两个质量不同的施工流程并行时启用 |

**默认启用集**（Rule 1/2/3/5）vs **诊断启用集**（Rule 4/6/7/8）：
- **默认启用集**（4 条）：Rule 1/2/3/5——独立误报率合计约 0.94%（ARL~106），在本审查数据点少（10-20 点）的场景下可接受（期望 1 次误报/10 波）
- **诊断启用集**（4 条）：Rule 4/6/7/8——仅在 §7.0.6 L3 抽检发现异常模式或 §6.0 跨波次重评发现评分不稳定时临时启用，诊断完成后关闭
- **为何不全部启用**：全部 8 条的 ARL~91（每 91 点 1 次误报）——本审查施工 3 波+运维期若每月 1 波，91 点需 7.6 年才积累，误报率问题不如制造业严重，但"操作员信任损耗"风险仍然存在（每次误报都消耗人工复核时间）

**与 §7.0.4 SPC 冷启动的对接**：
- 冷启动期（1-2 波，≤4 点）：仅 Rule 1
- 预热期（3-4 波，5-8 点）：Rule 1 + Rule 3（6 点趋势，数据点刚够）
- 稳态期（5 波+，≥10 点）：默认启用集 Rule 1/2/3/5
- 诊断模式（L3 发现异常时）：临时启用诊断集 Rule 4/6/7/8

**为何 Rule 2-8 需在稳态期才启用**（与 §7.0.4 SPC 冷启动对齐）：
- Rule 2（9 点单侧）需 ≥9 数据点——冷启动期（≤4 点）不适用
- Rule 3（6 点连续）需 ≥6 数据点——预热期（5-8 点）勉强可用但样本噪声大
- Rule 4-8 需 ≥14/8/15/8 数据点——稳态期（≥10 点）才可靠
- 冷启动期/预热期仅用 Rule 1（单点 3σ）+ EWMA/CUSUM，稳态期按 v1.4.0 风险矩阵默认启用 Rule 1/2/3/5（诊断时临时启用 Rule 4/6/7/8）

**Hotelling T² 多变量 SPC（v1.3.0 远期升级路径记录）**：

> 当前 §7.0.4 SPC 三图联用 + Nelson 规则都是**单变量**控制图——监控 Q score 这一个综合指标。[Knop 2026 "Integrating Classical and Advanced SPC Tools"](https://reference-global.com/download/article/10.2478/mspe-2026-0030.pdf)（Management Systems in Production Engineering 2026, Vol 34 Issue 2）指出多变量 Hotelling T² 控制图可评估多个过程参数的**联合效应**——当 Q score 的四个子维度（completeness/accuracy/specificity/timeliness）需独立监控其联合分布时，T² 能检测"单维度都达标但联合分布异常"的情况（如 completeness=8 + accuracy=8 + specificity=8 + timeliness=4，Q score 加权后=7.0 达标，但 timeliness 单维度已退化）。

**为何当前不引入 Hotelling T²**（对齐 §9）：
- **Q score 是加权综合分**——§7.0.4 已将四维度加权为单一 Q score，timeliness 退化会反映在 Q score 下降（虽被其他维度拉平）。T² 的增量价值在"四维度独立监控"，但当前 Q score 的加权模型已足够
- **数据量要求**——T² 需四维度的协方差矩阵估计，要求 ≥20 数据点（施工波次），个人项目 3 波施工远不足
- **实现复杂度**——T² 需 numpy 协方差矩阵 + 逆矩阵 + 卡方分布查表，比 EWMA/CUSUM 的标量计算复杂一个量级
- **远期触发条件**——当 Q score 的四维度出现"加权后达标但单维度持续退化"的假阴性模式（§7.0.6 L3 抽检发现某维度系统性偏低但 Q score 未告警）时，再引入 T² 做分维度独立监控

**自适应控制限思想（v1.4.0 新增，参考 [AIAG SPC 3rd Edition 2026-07](https://ifactoryapp.com/industries/automotive-manufacturing/daptive-control-limits-automotive-stamping-quality-engineers-predictive-maintenance)）**：

> [AIAG SPC 3rd Edition 2026-07](https://ifactoryapp.com/industries/automotive-manufacturing/dptive-control-limits-automotive-stamping-quality-engineers-predictive-maintenance)（ifactoryapp 2026-06-03 报道）正式将"AI 增强自适应 SPC"（adaptive SPC）纳入标准——从静态控制限（static control limits）转向动态自适应控制限（dynamic adaptive limits）。核心洞察：静态控制限基于历史基线，过程漂移后误报率 40-60%（基线陈旧导致正常变异被误判为特殊原因）。v1.4.0 借鉴"自适应控制限"思想补入 §7.0.4，但不引入 AI 增强（对齐 §9 个人项目红线）。

**静态控制限的问题**（AIAG SPC 3rd Edition 的三大缺陷，映射到本审查）：

| AIAG 指出的静态 SPC 缺陷 | 制造业场景 | 本审查 Q score 场景 |
|---|---|---|
| 基线陈旧+误报膨胀 | 模具磨损后静态限基于旧基线，误报 40-60% | 施工流程改进后（如 §7.0.1 模板优化），Q score 基线应上升，但静态限仍按旧基线→正常提升被判为"异常高" |
| 单变量盲区 | 模具磨损同时影响多特征，单变量图无法检测 | Hotelling T² 已在 v1.3.0 记录为远期路径 |
| 合规缺口 | IATF 16949:2026 审核员关注"控制限重算间隔内如何响应过程变化" | 本审查无外部合规要求，但 §6.0 跨波次重评已隐性覆盖"过程变化响应" |

**本审查的自适应控制限触发条件**（基线重算，非 AI 增强）：

```
触发条件（任一满足即重算 SPC 基线 μ_0 / σ_EWMA）：
1. §6.0 跨波次重评触发权重调整（W2 上调/下调 ≥0.5）
   → 权重变化意味着 Q score 的计算公式变化，旧基线失效
   → 重算：用最近 5 波 Q score 重新拟合 μ_0 / σ_EWMA
2. §7.0.7 回滚 L3/L4 全波回滚后
   → 大范围回滚改变了施工流程特征（如模板修订/Rubric 调整）
   → 重算：回滚修复后从下一波开始重新积累基线（冷启动期重启）
3. Q score 的 σ 持续增大（连续 3 波 σ 递增 >20%）
   → 过程变异增大，旧控制限过窄→误报增加
   → 重算：用最近 5 波 σ 的均值替代旧 σ_EWMA
4. §7.0.1 模板或 §7.0.8 Rubric 发生结构性修订（版本号 bump）
   → 评分标准变化，Q score 的语义变了
   → 重算：新标准下的 Q score 从 0 开始重新积累（完全冷启动）
```

**为何仅借鉴"自适应控制限"思想不引入 AI 增强**（对齐 §9）：
- **AI 增强自适应 SPC**（AIAG SPC 3rd Edition 的完整方案）包括：ML 驱动的根因识别 + 实时 Cpk 追踪 + 预测性维护触发——这些需 ML 模型训练 + 实时数据流，个人项目 Q score 波次少（月级）+ 无实时数据流，AI 增强的增量价值低于实现成本
- **"基线重算"是自适应的低成本近似**——不需 ML，只需在触发条件满足时用最近 5 波数据重新拟合 μ_0 / σ_EWMA。代价是"自适应"是离散的（触发时才重算）而非连续的（AI 持续微调），但对月级波次的 Q score 已足够
- **与 §6.0 跨波次重评的对接**：§6.0 的"权重调整→priority 重算"是**优先级层面**的自适应，§7.0.4 的"基线重算→控制限更新"是**质量度量层面**的自适应——两者正交，共同构成"证据→调整"的双层反馈环

**Freshness SLO/SLI 服务级别度量（v1.9.0 新增，参考 [oneuptime.com 2026-01-30 Freshness SLOs](https://oneuptime.com/blog/post/2026-01-30-freshness-slos/view) + [yutils.jdgrid.com 2026-05-25 SLI/SLO](https://yutils.jdgrid.com/en/guides/how-slis-and-slos-actually-work) + [skillmd.ai 2026 SLA/SLO/SLI](https://www.skillmd.ai/skills/sla-slo-and-slis/)）**：

> 当前 §7.0.4 的 timeliness 是**连续值**（0-10 分）——度量"文档多新鲜"。但缺少**二元合规判定**——"多少比例的文档满足新鲜度目标"。[oneuptime.com 2026-01-30](https://oneuptime.com/blog/post/2026-01-30-freshness-slos/view) 的 Freshness SLO 框架将"新鲜度"从连续值升级为**服务级别指标**（SLI）——回答"在给定时间窗口内，多少比例的文档满足新鲜度阈值"。v1.9.0 补入此框架作为 Q score timeliness 的**聚合层度量**——Q score 评估单表文档质量，Freshness SLI 评估整个 design_memos 的新鲜度合规率。

**Freshness SLI 公式**（适配文档场景，参考 oneuptime.com 的数据管道 SLI）：

```
Freshness SLI = (时间窗口内 timeliness ≥ 7.0 的表数 / 总表数) × 100%

→ 示例：102 张表中 95 张 timeliness ≥ 7.0 → Freshness SLI = 95/102 = 93.1%
→ 与 Q score timeliness 的关系：
   - Q score timeliness = 单表文档新鲜度连续值（0-10），回答"这张表文档多新鲜"
   - Freshness SLI = 全仓库文档新鲜度合规率（0-100%），回答"多少比例文档达标"
   - SLI 是 timeliness 的聚合投影——timeliness 低于 7.0 的表拉低 SLI
```

**Freshness SLO 目标**（Service Level Objective，内部目标）：

```
SLO = 90%（design_memos 的文档新鲜度合规率目标）

→ 含义：90% 的表文档 timeliness ≥ 7.0（即 age_days 在可接受范围内 + semantic_alignment 达标）
→ Error Budget = 100% - SLO = 10% → 允许 10 张表文档 timeliness < 7.0（正在重写/刚检测到 stale）
→ Error Budget 消耗规则（参考 yutils.jdgrid.com 2026-05 的 error budget velocity contract）：
   - Budget 剩余 > 50%（≤5 张 stale）→ 正常施工节奏，可并行补新表文档
   - Budget 剩余 20-50%（6-8 张 stale）→ 降速，优先修复 stale 表文档再补新表
   - Budget 耗尽（>10 张 stale）→ 冻结新表文档施工，全力修复 stale 表（stabilize first）
```

**Age-based vs Lag-based 新鲜度区分（v1.9.0 新增，参考 oneuptime.com 2026-01-30）**：

> [oneuptime.com 2026-01-30](https://oneuptime.com/blog/post/2026-01-30-freshness-slos/view) 区分两种新鲜度度量：**Age-based**（数据年龄 = now - 最新记录时间戳）vs **Lag-based**（处理延迟 = 下游可用时间 - 事件发生时间）。本审查的文档新鲜度同样存在这两种度量：

| 度量类型 | oneuptime 定义 | 本审查对应 | 当前实现 |
|---|---|---|---|
| **Age-based** | now - last_record_timestamp（最新数据多旧） | now - 文档最后同步代码的天数 = `age_days` | ✅ §7.0.4 `time_decay = 2^(-age_days/half_life)` 已实现 |
| **Lag-based** | available_downstream - event_occurred（处理延迟） | 文档同步时间 - 代码变更时间 = **文档更新滞后天数** | ⚠️ v1.9.0 补入——§7.0.5 `verifiedAtVersion` 状态指纹检测到 stale 后，到文档实际重写完成的天数 |

**Lag-based 度量的价值**：Age-based 只看"文档多旧"，Lag-based 看"从检测到 stale 到修复的响应速度"——与 §7.0.9 MTTD/MTTR 联动（MTTR = Lag-based 的修复延迟）。**Age-based 管"状态"，Lag-based 管"响应"**——两者正交。

**Google OKF v0.2 `stale_after` 固定日期备选（v1.9.0 补充对比）**：

> §7.0.5 v1.9.0 的 DataHub `verifiedAtVersion` 状态指纹对比中已提及 Google OKF v0.2 的 `stale_after` 固定日期机制。此处补充其在 Freshness SLO 场景的定位——`stale_after` 是 Freshness SLI 的**简化版阈值**：

```
Google OKF v0.2 stale_after（固定日期）：
  stale_after: 2026-09-10  → 此日期后文档标记为 stale（无需计算 age_days/decay）
  Freshness SLI_okf = (stale_after 未到期的文档数 / 总文档数) × 100%

本审查状态指纹（状态驱动）vs OKF stale_after（固定日期）vs 当前 time_decay（指数衰减）：
  ┌─────────────────┬──────────────────┬──────────────────┐
  │ 当前 time_decay  │ OKF stale_after  │ 状态指纹(采纳)    │
  │ (指数衰减)       │ (固定日期)        │ (verifiedAtVersion)│
  ├─────────────────┼──────────────────┼──────────────────┤
  │ 度量"文档多旧"   │ 度量"是否到期"    │ 度量"状态是否变"  │
  │ 连续值 0-10      │ 二元 stale/ok    │ 二元 stale/ok    │
  │ age_days 驱动    │ 日历日期驱动      │ schema hash 驱动  │
  │ 无上游传播       │ 无上游传播        │ 一跳 lineage 传播 │
  └─────────────────┴──────────────────┴──────────────────┘

→ 采纳策略：time_decay（连续值，Q score timeliness 维度）+ 状态指纹（二元判定，Freshness SLI 合规判定）
   OKF stale_after 作为"无 git 历史的离线文档包"降级备选——本审查有 git 历史，状态指纹优于固定日期
```

**为何补 Freshness SLO/SLI 但不替代 Q score timeliness**：
- **Q score timeliness 是 Leading 指标**（§7.0.4 Leading/Lagging 分类已定义）——单表文档新鲜度，预测"这张表文档将要过时"
- **Freshness SLI 是 Lagging 指标**——全仓库新鲜度合规率，度量"当前有多少文档已过时"
- 两者互补：timeliness 单表预警 → SLI 全局合规率度量——"单表 timeliness=6.5 触发 ⚠️"是 Leading，"SLI 跌破 90% 触发 Error Budget 冻结"是 Lagging
- **与 Error Budget 的联动**：Error Budget 耗尽时冻结新表施工——这是"质量优先于进度"的量化执行机制，避免"为赶覆盖率而牺牲新鲜度"

#### 7.0.5 增量更新机制（v0.5.0 新增 / v0.6.0 补 Embedded Freshness / v0.9.0 补 DocPilot false-positive filter / v1.8.0 补 predict Omissions schema↔doc 共变检测）

> §3.4 的 extract/trace 循环是"每波施工后重跑全量扫描"——但代码日常变更（如某表的 SQL 查询字段调整）不应触发全量重扫。v0.5.0 补入**增量更新机制**，参考 [RepoDoc 的 semantic impact propagation](https://arxiv.org/html/2604.26523v1)（双向导航 RepoKG 定位受影响文档，增量更新时间降 73%、token 降 77%）。

**增量更新触发流程**：

```
1. git diff 检测 src/zephyr/ 代码变更 → 识别变更文件涉及的表名
2. 对每个受影响表，双向查找：
   a. 向上游：表的 DDL 是否变更（schemas/categories/<table>.py 改动）
   b. 向下游：文档是否描述了已变更的用法（grep 文档中的字段/规则）
3. 若 DDL 变更 → 触发该表的文档 §7.0.1 模板"关键字段"节重写
4. 若代码用法变更（如 SQL SELECT 字段调整）→ 触发该表的文档"下游逻辑"节重写
5. 重写后重评该表 Q score（§7.0.4）→ 若 Q < 7.0 则标 ⚠️ 待复核
```

**与全量扫描的分工**：
- **增量更新**（日常）：git hook 触发，仅更新受影响表的文档字段，秒级完成
- **全量扫描**（每波施工后）：§3.4 extract/trace 循环，重跑 §3.2 三层扫描，分钟级完成
- **年度审计**（远期）：全量 Q score 重评 + 权重校准（§6.0），小时级完成

**增量更新的边界**：
- **表名改名**：git diff 无法自动关联新旧表名——需人工在文档全局替换 + 更新 §3.4 引用漂移检测
- **跨表逻辑变更**：如某策略从消费 `kline_daily` 改为消费 `kline_daily_hfq`——需人工追所有消费方文档（§10 Q3 即此类）
- **不自动生成文档**：增量更新只"标记需重写的字段"，不自动生成内容——避免 LLM 幻觉（§9 不用 LLM 做全量语义验证）

**Embedded Freshness 模式（v0.6.0 强化）**：

> [happysupport.ai 2026-05](https://happysupport.ai/blog/llm-knowledge-base-freshness-scoring) 提出 freshness 信号的三种架构模式：pull（外部抓取）/ push（写入时打分）/ **embedded**（将信号嵌入真源管道）。本审查 §7.0.5 的 git diff 触发机制属于 **embedded 模式**——freshness 信号不靠事后抓取，而是在代码变更时由 git hook 直接触发文档 freshness 更新。v0.6.0 明确这一模式定位，并将 §7.0.4 的 timeliness 指数衰减与 §7.0.5 的 git diff 触发**闭环对接**。

**Embedded freshness 闭环**（§7.0.4 + §7.0.5 联动）：

```
代码变更（git commit）
  ↓ git hook 触发
§7.0.5 增量更新：识别受影响表 → 标记文档"关键字段/下游逻辑"需重写
  ↓
§7.0.4 timeliness 重算：
  - semantic_alignment 降为 0.3（代码变更未同步）
  - age_days 重置为 0（自本次代码变更起算）
  - timeliness = (0.7×0.3 + 0.3×1.0) × 10 = 5.1（⚠️ 需补强）
  ↓
文档同步重写后：
  - semantic_alignment 升为 1.0（已同步）
  - age_days 保持 0（刚同步）
  - timeliness = (0.7×1.0 + 0.3×1.0) × 10 = 10（达标）
  ↓
每日定时任务：age_days 随时间增长 → time_decay 指数衰减 → timeliness 持续下降
  ↓ 30 天后
time_decay = 0.5 → timeliness = (0.7×1.0 + 0.3×0.5) × 10 = 8.5（仍达标）
  ↓ 90 天后
time_decay = 0.125 → timeliness = (0.7×1.0 + 0.3×0.125) × 10 = 7.4（接近阈值）
  ↓ 180 天后
time_decay = 0.03 → timeliness = (0.7×1.0 + 0.3×0.03) × 10 = 7.1（⚠️ 即将跌破 7.0）
```

**为何用 embedded 而非 pull 模式**（[happysupport.ai 2026-05](https://happysupport.ai/blog/llm-knowledge-base-freshness-scoring)）：
- **pull 模式**（外部抓取 freshness）：需定期抓取文档 + 代码对比——延迟大、成本高、易遗漏
- **push 模式**（写入时打分）：依赖作者主动打分——易被遗忘
- **embedded 模式**（git hook 触发）：代码变更天然触发 freshness 更新——**docs-as-code 哲学的延伸**（[writethedocs 2026](https://www.writethedocs.org/guide/docs-as-code/) + [docs.unmarkdown.com 2026-02](https://docs.unmarkdown.com/blog/docs-as-code-2026)），文档与代码同仓库同 PR，变更原子性保证 freshness 信号实时性

**实施位置**：embedded freshness 闭环封装进 `scripts/audit_data_utilization.ps1` 的 `post-commit` hook，每次 git commit 后自动更新 `docs/_audit/quality_score.csv` 的 timeliness 列。

**DocPilot 两 pass 质量门+置信度路由（v0.9.0 新增）**：

> 当前 §7.0.5 的增量更新流程是"git diff → 识别受影响表 → 标记文档需重写"——**单 pass 触发**，存在假阳性：并非每次代码变更都使文档过时（如代码改了注释/格式/无关变量，文档描述的用法未变）。[DocPilot 2026](https://github.com/wyattstanson/docpilot)（Self-Healing Technical Documentation）提出**两 pass 质量门 + 置信度路由**——先验证文档是否真的过时（false-positive filter），再决定修复策略。v0.9.0 补入此机制降低增量更新的假阳性。

**DocPilot 的两 pass 质量门**：

```
Pass 1（staleness_checker）：LLM 验证文档是否真的过时
  输入：代码 diff + 当前文档内容
  输出：{is_stale: bool, confidence: 0.0-1.0, stale_sections: [字段名]}
  → 若 is_stale=false（代码变更未影响文档描述的用法）→ 跳过，不触发更新
  → 若 is_stale=true + confidence ≥ 0.8 → 进入 Pass 2
  → 若 is_stale=true + confidence < 0.8 → 标 ⚠️ 人工复核（不自动更新）

Pass 2（repair_engine）：LLM 重写过时部分
  输入：过时的文档节 + 代码 diff + stale_sections
  输出：重写后的文档节
  → 第二次 LLM 验证修复是否正确（二次校验）
  → 若验证通过 → 应用修复
  → 若验证未过 → 标 ⚠️ 人工复核
```

**置信度路由**（Confidence Routing）：

| confidence | 路由策略 | 本审查对应 |
|---|---|---|
| ≥ 0.9 | **auto-fix**（自动应用修复，无需人工） | 远期目标——当前不自动生成文档（§9），仅标记需重写 |
| 0.6-0.9 | **draft**（生成草稿，人工 review 后应用） | §7.0.2 代码反推草稿 + L3 人工抽检 |
| < 0.6 | **flag**（仅标记 ⚠️，不生成内容） | 当前 §7.0.5 的"标记需重写的字段"模式 |

**为何不当前采纳 DocPilot 全流程但吸收 false-positive filter**：
- **auto-fix 风险**：DocPilot 的 auto-fix（confidence ≥ 0.9 自动应用）对金融系统文档风险过高——LLM 可能"自信地错误"修复（如把"T+1"改成"T+0"）。本审查 §9 已声明"不自动生成文档"，保留人工 review
- **false-positive filter 价值高**：Pass 1 的"先验证是否真的过时"可融入当前 §7.0.5 流程——在"标记需重写"前加一步"判断代码变更是否影响文档描述的用法"
- **成本可控**：false-positive filter 只需判断"是否过时"（是/否+confidence），不需生成内容——比 DocPilot 的 repair_engine 轻量，可嵌入 PowerShell 脚本

**v0.9.0 融入 §7.0.5 的 false-positive filter**（补入增量更新流程步骤 2.5）：

```
2.5 false-positive filter（v0.9.0 新增）：
   对每个受影响表，判断代码变更是否真的影响文档描述的用法：
   - 若代码变更仅涉及注释/格式/无关变量 → 跳过该表（false positive）
   - 若代码变更涉及 SQL 字段/查询逻辑/数据加载 → 标记需重写（true positive）
   判断方式：
   a. git diff 的 +/- 行是否包含表名字段名（grep 表名+字段名）
   b. 变更行是否在 SQL 查询/数据加载函数内（正则匹配 def fetch_/SELECT/INSERT）
   c. 若 a AND b → true positive；否则 → false positive（跳过）
```

**与 Cascade 双重条件的对比**（§7.0.6 v0.8.0 已补入）：

| 机制 | 位置 | 作用 | 假阳性/假阴性 |
|---|---|---|---|
| Cascade 双重条件 | §7.0.6 L3 验收 | 检测文档与代码的**语义不一致** | 降低"文档表达歧义导致的误报" |
| DocPilot false-positive filter | §7.0.5 增量更新 | 检测代码变更是否**真的影响文档** | 降低"无关代码变更触发不必要更新" |
| 两者互补 | — | Cascade 管"验收阶段的一致性"，DocPilot 管"更新阶段的必要性" | 双重过滤 |

**与 Syntropy 编码会话级新鲜度的联动**（§7.0.4 v0.9.0 已补入）：
- Syntropy 的 `code_sessions_since_sync` 度量"代码变了多少次"
- DocPilot 的 false-positive filter 判断"代码变更是否影响文档"
- 两者结合：`code_sessions_since_sync > 0`（代码有变更）→ false-positive filter 判断"是否影响文档" → 若 true positive → 触发 §7.0.4 timeliness 重算（semantic_alignment 降为 0.3）

**CodeScene "predict Omissions" schema↔doc 共变检测（v1.8.0 新增，参考 [CodeScene 2.4.0 Temporal Coupling — Use Temporal Coupling to predict Omissions](https://docs.enterprise.codescene.io/versions/2.4.0/guides/technical/temporal-coupling.html#use-temporal-coupling-to-predict-omissions) + [Software Design X-Rays Adam Tornhill 2018 Pragmatic Bookshelf](https://media.pragprog.com/titles/atevol/intro.pdf)）**：

> §7.0.3 v1.7.0 的 Temporal Coupling 用于发现**隐藏依赖**——两表无 DDL 依赖但频繁共变（**正向共变**=意外耦合=风险）。CodeScene 的 "predict Omissions" 是 Temporal Coupling 的**逆向应用**：当两文件**应当共变**但**实际不共变**（**负向耦合**=预期耦合缺失=遗漏），预测文档更新被遗漏。[CodeScene 2.4.0 文档](https://docs.enterprise.codescene.io/versions/2.4.0/guides/technical/temporal-coupling.html#use-temporal-coupling-to-predict-omissions) 明确列出三种"应当共变"场景：(a) 单元测试应随被测代码共变、(b) **文档应随其描述的系统共变**、(c) 跨平台并行实现应共变。本审查关注场景 (b)——`schemas/categories/*.py`（DDL/schema 真源）应与 `design_memos/*.md`（文档消费方）共变。

**predict Omissions 算法**（§7.0.3 Temporal Coupling 的逆运算）：

```
1. 定义"应当共变"的文件对映射 expected_coupling：
   对每张表 table_X：
     schema_file = schemas/categories/{prefix}_table_X.py
     doc_files = grep -l "table_X" design_memos/*.md  # 引用该表的所有文档
     → expected_coupling[schema_file] = [doc_file_1, doc_file_2, ...]

2. 复用 §7.0.3 Temporal Coupling 的 commit→files 映射（已含 commit-size 归一化过滤）

3. 对每个 expected_coupling 对 (schema_file, doc_file)：
   计算 actual_coupling = temporal_coupling(schema_file, doc_file)
   = co_occurrence / |commits(schema_file) ∪ commits(doc_file)|

4. 预测遗漏（predict Omission）：
   若 schema_file 被 ≥1 commit 修改，但 actual_coupling(schema_file, doc_file) = 0
   → 说明 schema 变了但文档从未跟着变 → 标 ⚠️ 预测遗漏
   → 输出 predicted_omission.csv（schema_file × doc_file × schema_commit_count × last_schema_commit_date × omission_severity）

5. 严重度分级（omission_severity）：
   HIGH：schema_file 有 ≥3 次 commit 且 doc_file 0 次共变 → 多次 schema 演化文档全遗漏
   MEDIUM：schema_file 有 1-2 次 commit 且 doc_file 0 次共变 → 少量遗漏
   LOW：actual_coupling > 0 但 < 0.3 → 偶尔共变但覆盖率不足（部分遗漏）
   OK：actual_coupling ≥ 0.3 → 文档基本跟随 schema 变化

6. 与 §7.0.5 增量更新联动：
   predicted_omission.csv 的 HIGH/MEDIUM 项 → 自动注入 §7.0.5 步骤 1 的"受影响表"列表
   → 触发 false-positive filter（步骤 2.5）→ 若 true positive → 标记文档需重写
   → 闭合"预测遗漏 → 验证 → 标记 → 重写"主动检测环
```

**与 §7.0.3 Temporal Coupling 的关系**（正逆运算对比）：

| 维度 | §7.0.3 Temporal Coupling（正向） | §7.0.5 predict Omissions（逆向） |
|---|---|---|
| 检测目标 | 隐藏依赖（意外共变） | 文档遗漏（预期共变缺失） |
| 信号 | temporal_coupling(A,B) ≥ 0.5 且 A→B 不在静态依赖图 | temporal_coupling(schema,doc) = 0 且 schema 有变更 |
| 语义 | "这两表不该一起改但总一起改→隐藏依赖" | "这文档该跟着 schema 改但没改→遗漏" |
| 输出 | hidden_dependency.csv | predicted_omission.csv |
| 处理 | 人工复核是否补声明依赖 | 注入 §7.0.5 增量更新流程触发文档重写 |
| 算法 | 同一 Jaccard 共现矩阵，不同判定方向 | 同一 Jaccard 共现矩阵，不同判定方向 |

**为何补 predict Omissions 但仅作预测不自动修复**：
- **主动 vs 被动**：§7.0.5 的 git diff 触发是**被动**的（commit 后才知道代码变了），predict Omissions 是**主动**的——扫描历史 commit 发现"schema 变了 N 次但文档从未跟"的累积遗漏，覆盖"git diff 未捕获的历史遗漏"（git diff 只看最近一次 commit，predict Omissions 看全量历史）
- **不自动修复**：predict Omissions 仅输出 `predicted_omission.csv` 标记需复核的文档，不自动重写内容（§9 红线"不自动生成文档"）——由 §7.0.6 L3 人工抽检 + §7.0.2 代码反推草稿处理
- **冷启动约束**：与 §7.0.3 Temporal Coupling 共享冷启动约束——commit 数 < 50 时 statistical significance 不足，仅输出 raw count 不计算 coupling score

**与 SCORE Orphan Topics 的对比**（[github.com/informatique-cdc/SCORE 2026](https://github.com/informatique-cdc/SCORE/blob/main/docs/INGESTION_AND_ANALYSIS.md)）：
SCORE 项目的 Gap Detection 用 5 种互补策略识别文档覆盖缺口，其中 "Orphan Topics"（孤儿主题=有文档但无代码引用）是本审查 predict Omissions 的**对偶问题**——predict Omissions 找"有代码变更但无文档跟随"（schema→doc 缺失），SCORE Orphan Topics 找"有文档但无代码消费"（doc→schema 缺失）。两者互补覆盖双向遗漏。本审查 §5.3 已覆盖"代码高引用但文档零覆盖"（正向缺口），predict Omissions 补"schema 变更但文档未跟"（动态缺口），SCORE Orphan Topics 的"文档有但代码没用"（反向缺口）在个人项目中价值有限（design_memos 是架构 why 层文档，不要求每篇都有代码消费方），记录备查不实施。

**DataHub docFreshnessInfo `verifiedAtVersion` 状态指纹机制（v1.9.0 新增，参考 [DataHub PR #19023 2026-08-09](https://github.com/datahub-project/datahub/pull/19023)）**：

> 当前 §7.0.5 的 Embedded Freshness 闭环是"git commit → git hook 触发 → 识别受影响表 → 标记文档需重写"——**事件驱动**模式（每次 commit 都触发检查）。[DataHub PR #19023（2026-08-09 提交）](https://github.com/datahub-project/datahub/pull/19023) 的 `docFreshnessInfo` aspect 提出了一种**状态驱动**的互补机制：在文档验证时记录一个"状态指纹"（`verifiedAtVersion`），后续只需对比实体当前状态与指纹即可判断文档是否过时——**无需重扫文档文本**也无需逐 commit 触发。

**docFreshnessInfo 的五字段模型**（DataHub PR #19023 的 PDL schema）：

| 字段 | 含义 | 本审查对应 |
|---|---|---|
| `verifiedAgainstUrns` | 验证时记录的实体 URN + 一跳 lineage 上游（实体本身 + 其依赖的上游实体） | §7.0.3 依赖图中的 table_X + 其 depends_on 上游表集合 |
| `verifiedAtVersion` | 上述实体集合的 schema/ownership/deprecation 状态的**联合指纹**（fingerprint of combined state） | schemas/categories/*.py 的 git commit hash + 依赖表的 commit hash 组合指纹 |
| `verifiedAtTime` | 验证发生的时间戳 | §7.0.4 timeliness 的 `last_sync_time`（文档最后与代码同步的时间） |
| `actor` | 执行验证的人或系统 | §7.0.6 L3 抽检的执行者（人/AI） |
| `staleReason` | 文档变为 stale 的原因（当实体变更触发重新检查时填入） | §7.0.5 步骤 2.5 false-positive filter 的判定结果 |

**状态指纹的核心创新**（与当前 git diff 触发机制对比）：

```
当前机制（事件驱动，§7.0.5 Embedded Freshness）：
  git commit → git hook 触发 → git diff 识别受影响表 → false-positive filter → 标记文档需重写
  问题：(1) 每次 commit 都触发（高频，即使变更无关也需 filter）；(2) 只看最近一次 commit（历史遗漏靠 predict Omissions 补）

状态指纹机制（状态驱动，v1.9.0 补入）：
  文档验证时 → 记录 verifiedAtVersion = BLAKE3(schema_file_hash + upstream_table_hashes + deprecation_status)
  后续检查时 → 重新计算 current_version = BLAKE3(当前 schema_file_hash + 当前 upstream_hashes + 当前 deprecation)
  若 current_version ≠ verifiedAtVersion → 文档 stale（无需 git diff，无需重扫文档文本）
  staleReason = "schema 变更" / "上游依赖变更" / "deprecation 状态变更" / "ownership 变更"
  优势：(1) O(1) 指纹对比而非 O(N) git diff 扫描；(2) 捕获"上游变更导致文档过时"（当前 git diff 只看直接变更的文件）
```

**为何补状态指纹但不替代 git diff 触发**：
- **互补而非替代**：git diff 触发是**实时**的（commit 后立即触发），状态指纹是**按需**的（检查时才对比）——两者覆盖不同场景。git diff 适合 CI/CD 实时门禁，状态指纹适合 §7.0.6 验收闭环的批量检查（每波施工后对所有表做一次指纹对比，无需逐 commit 回溯）
- **上游传播检测**：当前 git diff 只检测"直接变更的文件"——若 `stock_list` 的 schema 变了，依赖 `stock_list` 的 `kline_daily` 文档应标记 stale，但 git diff 只触发 `stock_list` 自身的文档检查。状态指纹的 `verifiedAgainstUrns` 包含**一跳 lineage 上游**，`verifiedAtVersion` 是联合指纹——上游变更会改变指纹，自动标记下游文档 stale
- **实现成本可控**：状态指纹只需 BLAKE3 hash（schemas/categories/*.py 文件内容 + 依赖表的 hash 组合），封装为 `scripts/freshness_fingerprint.py` 输出 `freshness_fingerprint.csv`（table × verifiedAtVersion × currentVersion × is_stale × staleReason），与 §7.0.4 timeliness 联动（is_stale=true → semantic_alignment 降为 0.3）
- **与 DataHub 工具的关系**：§9 已声明"不引入外部数据目录工具（DataHub/Amundsen/Atlan）"——状态指纹是 DataHub `docFreshnessInfo` aspect 的**概念借鉴**，用 PowerShell + BLAKE3 实现，不部署 DataHub 平台

**与 Google OKF v0.2 trust/provenance 模型的对比**（[itbrief.asia 2026-07-27 Google OKF v0.2](https://itbrief.asia/story/google-adds-trust-provenance-to-open-knowledge-format)）：

> [Google Open Knowledge Format v0.2（2026-07-27 发布）](https://itbrief.asia/story/google-adds-trust-provenance-to-open-knowledge-format) 在知识包 frontmatter 中新增 5 类信号：provenance（来源）、trust（生成 vs 验证）、freshness（stale_after 固定日期）、lifecycle（draft/stable/deprecated）、attestation（计算验证）。与 DataHub docFreshnessInfo 对比：

| 维度 | DataHub docFreshnessInfo | Google OKF v0.2 | 本审查采纳 |
|---|---|---|---|
| 新鲜度检测 | `verifiedAtVersion` 状态指纹对比 | `stale_after` 固定日期（非相对 TTL） | **状态指纹**（比固定日期更精确——固定日期到期不一定 stale，状态指纹变更才 stale） |
| 验证记录 | `actor` + `verifiedAtTime` | `generated`（生成方式+时间）+ `verified`（验证确认） | `actor` + `verifiedAtTime`（对齐 §7.0.6 L3 抽检执行者+时间） |
| 过时原因 | `staleReason` | 无（仅标记 stale_after 到期） | `staleReason`（对齐 §7.0.5 false-positive filter 判定结果） |
| 计算验证 | 无 | `Attested Computation`（验证计算是否用批准方法） | §7.0.6 L3 语义抽检（人工验证文档描述的用法与代码一致） |
| 传播范围 | 一跳 lineage 上游（`verifiedAgainstUrns`） | 无 lineage 概念 | 一跳 lineage（对齐 §7.0.3 依赖图） |

**结论**：DataHub docFreshnessInfo 的状态指纹 + 一跳 lineage 传播比 Google OKF v0.2 的固定日期 + 无传播更适合本审查场景（文档-代码依赖关系明确，需上游传播检测）。OKF v0.2 的 `generated` vs `verified` 分离思想补入 §7.0.6（区分"AI 生成草稿"与"人工验证通过"两阶段），`Attested Computation` 概念补入 §7.0.6 L3 抽检（验证文档描述的计算方法是否被实际执行验证）。

#### 7.0.6 验收闭环（v0.3.0 新增 / v0.4.0 补语义抽检）

> v0.2.0 的验证标准"每张表至少在 1 篇文档中作为数据源被显式描述"是人工判断。v0.3.0 补入机器可查的验收闭环。v0.4.0 补入**语义抽检**——[DocPrism ISSTA 2026](https://arxiv.org/pdf/2511.00215)证明"表名出现 ≠ 用法正确"（Schema presence != behavior parity），仅靠 grep 命中验收会产生"文档提到了表名但描述的用法与代码实际行为不符"的假覆盖。

**每波施工后回归验证流程**：

```
1. 施工完成 → 重跑 §3.2 三层扫描（scripts/audit_data_utilization.ps1）
2. 对比施工前后 CSV 矩阵 → 确认目标表从 CODE_ONLY 转为 BOTH
3. 计算 §5.1 文档覆盖率 → 确认覆盖率上升符合预期
4. Q score 评估（v0.5.0 新增）→ 按 §7.0.4 对当波补的表评分，目标平均 Q ≥ 7.0
5. 语义抽检（v0.4.0）→ 每批次随机抽 2 张表，人工核实文档描述的用法与代码实际行为一致
6. 检查无回归 → 确认无新增 CODE_ONLY 表（表名改名/新增表）
7. 权重校准（v0.4.0）→ 对比高分表与低分表实际文档价值，按 §6.0 校准循环调整权重
8. 拓扑依赖校验（v0.5.0 新增）→ 按 §7.0.3 确认被依赖表先于依赖表补齐，无跨批次阻塞
9. Kano 分类校验（v0.6.0 新增）→ 按 §6.0 Kano 层确认所有"基本型"表（risk_module_flag=Y）均已补文档——基本型不可遗漏，无论 RICE 分多少
10. 回滚就绪检查（v0.6.0 新增）→ 确认本波施工 commit 粒度可回滚（每张表独立 commit，非整波一个大 commit）——满足 §7.0.7 L1 单表回滚前提
11. Confidence/effort 分布审计（v0.6.0 新增）→ 按 §6.0 滥用警告 + §7.0.8 Rubric 一致性保障，检查 >70% 表同分触发警告
12. half_life 参数校准审计（v0.7.0 新增）→ 按 §7.0.4 参数敏感性警告，对比"实际被发现过时的文档 age"分布与 half_life=30 天假设——若大多数过时文档在 15 天内被发现则降 half_life 为 15 天，纳入 §6.0 权重校准循环
13. 更新本备忘 §5.1 指标 + §6.2 批次清单（标 ✅ 已完成，附 Q score）
```

**单表验收标准**（三层）：

| 层 | 标准 | 方法 | 适用 |
|---|---|---|---|
| L1 存在性（机器可查） | `Select-String -Path <目标文档> -Pattern <表名>` 返回 ≥1 命中 | PowerShell | 每张表 |
| L2 消费关系（机器可查） | 命中行包含"数据源"/"输入"/"消费"等消费关系关键词 + frontmatter `depends_on` 含 schema path | PowerShell + 人工 | 每张表 |
| L3 语义一致（人工抽检，v0.4.0 新增） | 文档描述的表用法（字段含义/消费频率/下游逻辑）与代码实际行为一致——不只是"提到了表名" | 每批次随机抽 2 张表人工核实 | 抽检 |

> **L3 语义抽检理由**：[DocPrism 2026](https://arxiv.org/pdf/2511.00215)发现 LLM 辅助文档生成中 11% 的代码-文档对存在不一致（文档说了 X 但代码做的是 Y）。本审查的补文档施工由 AI 执行，同样风险——L3 抽检是防止"假覆盖"的最后防线。抽检发现不一致时，该表标 ⚠️ 需返工，不计入覆盖率分子。

**L3 主动学习抽样策略（v1.1.0 新增）**：

> 当前 L3 是"每批次随机抽 2 张表"——纯随机抽样可能遗漏高风险表（Confidence 边界表 / 高 effort 表 / Q score 偏低的风险表）。[Smart Active Sampling arXiv 2209.11464](https://arxiv.org/pdf/2209.11464.pdf)（Heistracher et al.）提出基于模型不确定性的主动学习采样——优先抽检"模型最不确定"的样本而非随机。[AI 主动学习标注质量动态校验 2026-03 专利](https://www.xjishu.com/zhuanli/55/202511942856.html)进一步提出"特征不确定性采样高价值样本"。[ISO 2859-1:2026](https://www.iso.org/cms/render/live/en/sites/isoorg/contents/data/standard/08/54/85464.html) AQL 抽样标准提供统计学的 skip-lot 规则（连续合格批次可跳批）。v1.1.0 补入此策略优化 L3 抽样。

**分层抽样策略**（替代纯随机，每批次抽 2-3 张）：

| 抽样层 | 选取标准 | 每批次抽样数 | 理由 |
|---|---|---|---|
| **不确定层**（必抽） | §3.5 Confidence=0.5 或 0.8 的表（代码引用性质不确定） | 1 张 | 不确定表的"假覆盖"概率最高——SQL 查询 vs 模板继承的误判直接影响文档准确性 |
| **高风险层**（必抽） | §6.0 Kano 基本型（risk_flag=Y）且 Q score < 8.0 的表 | 1 张 | 风险红线表文档错误后果严重——Q score 偏低说明可能浅覆盖 |
| **随机层**（补抽） | 从批次内其余表中随机抽取 | 0-1 张 | 保证覆盖非高风险非不确定表的偶发问题 |

**skip-lot 规则**（[ISO 2859-1:2026](https://www.iso.org/cms/render/live/en/sites/isoorg/contents/data/standard/08/54/85464.html) 启发）：
- 连续 3 波 L3 抽检全过（零不一致）→ 下一波抽检数减半（3→2 或 2→1）——"持续高质量的批次降频检测"
- 某波 L3 发现 ≥1 张不一致 → 下一波抽检数加倍 + 全量复查该表所在社区（§7.0.3 Louvain 社区）——"发现问题则升频+扩大范围"
- 某表连续 2 次被抽中且全过 → 该表进入"信任名单"暂免抽检（直到代码变更触发 §7.0.5 增量更新）

**为何不用纯主动学习而用分层抽样**：
- 纯主动学习（Smart Active Sampling）需训练模型预测"哪些表最可能不一致"——但 L3 抽检数据量少（每波 2-3 张），不足以训练预测模型
- 分层抽样是主动学习思想的轻量实现——用 §3.5 Confidence + §6.0 Kano 分类作为"不确定性代理"，无需训练模型
- [ISO 2859-1:2026](https://www.iso.org/cms/render/live/en/sites/isoorg/contents/data/standard/08/54/85464.html) 的 skip-lot 规则提供"连续合格降频/不合格升频"的统计学基础，避免"每波都抽 2 张"的僵化——对个人项目的轻量场景适配（不强制 AQL 严格计算，仅借鉴 skip-lot 思想）

**Cascade 自动化语义验证远期升级路径（v0.8.0 新增）**：

> 当前 L3 是"每批次随机抽 2 张表人工核实"——成本可控但覆盖率低（每批次仅 2/N 张）。[Cascade arXiv 2604.19400v1 FSE 2026 July](https://arxiv.org/pdf/2604.19400v1)（Kiecker et al.）提出**双重条件自动化不一致检测**——从文档生成单元测试，执行测试检测代码-文档不一致。在 71 个不一致 + 814 个一致对上评估，发现 13 个之前未知的不一致（10 个已修复），精确度显著优于单条件检测。v0.8.0 补入作为 L3 的远期自动化升级路径。

**Cascade 的双重条件机制**（降低假阳性的核心）：

```
条件 1：现有代码执行从文档生成的测试 → 测试失败（代码行为与文档描述不符）
条件 2：从文档生成的代码执行同一测试 → 测试通过（文档描述本身是自洽的）

→ 仅当条件 1 AND 条件 2 同时满足 → 报告不一致
→ 若条件 1 失败但条件 2 也失败 → 文档描述本身有误，非代码-文档不一致
→ 若条件 1 通过 → 代码与文档一致，无问题
```

**为何此双重条件降低假阳性**：单条件检测（仅条件 1）会将"文档描述有歧义导致测试生成错误"误报为"代码-文档不一致"。双重条件确保"文档自洽（条件 2）+ 代码不符（条件 1）"才报——即问题确实在代码与文档的差距，不在文档本身的表达。

**映射到本审查的 L3 场景**：

| Cascade 步骤 | 本审查对应 | 当前实现 | Cascade 自动化后 |
|---|---|---|---|
| 从文档生成单元测试 | 从 design_memos 的"下游逻辑"字段生成 SQL 查询/数据加载测试 | 无（人工读文档判断） | LLM 从"下游逻辑"描述生成可执行测试脚本 |
| 执行测试 | 运行测试验证代码行为 | 人工读代码核实 | 自动执行测试，捕获 pass/fail |
| 从文档生成代码 | 从"关键字段"+"消费频率"生成代码片段 | 无 | LLM 从文档描述生成代码 |
| 双重条件判定 | 人工判断"文档与代码是否一致" | 每批次 2 张抽检 | 全量自动判定，假阳性可控 |

**为何不当前采纳 Cascade**：
- **适用场景差异**：Cascade 针对"API 文档 vs 函数实现"的语义一致性（如 `startsWithAny` 的 case-sensitive vs insensitive）。本审查的 design_memos 是**架构文档**（why 层），不是 API 参考文档（what 层）——从"解禁前 30 日减仓"这类业务规则生成可执行测试的难度远高于从 API 签名生成测试
- **测试执行环境成本**：Cascade 需可执行测试环境（运行代码 + 对比输出）。本审查的表消费涉及 ClickHouse 查询 + Python 数据处理 pipeline，搭建测试执行环境比 Java 单元测试复杂
- **LLM 成本**：每张表需 2 次 LLM 调用（生成测试 + 生成代码）——61 张缺口表 × 2 = 122 次 LLM 调用，成本与 DocAgent 同量级
- **L3 人工抽检已够**：当前 42 篇文档规模下，每批次 2 张人工抽检（~15 分钟/张）成本可接受。Cascade 的价值在文档量增长到 100+ 篇、人工抽检成本线性上升时才显著
- **远期触发条件**：当 design_memos 增长到 100+ 篇（与 DocAgent 触发条件一致）或 L3 人工抽检发现不一致率 >15%（当前 DocPrism 基准 11%），可引入 Cascade 自动化全量检测替代人工抽检

**Cascade 对本审查的验证价值**：
- **双重条件思想值得吸收**：Cascade 的"条件 1（代码不符）AND 条件 2（文档自洽）"思想可简化融入 L3 人工抽检——抽检时先验证"文档描述是否自洽"（文档内部逻辑无矛盾），再验证"文档与代码是否一致"——减少"文档表达歧义导致的误报"
- **与 DocAgent 互补**：DocAgent 的 Verifier 智能体做"文档生成时的同步验证"（pre-shipment），Cascade 做"文档生成后的异步验证"（post-shipment）——两者覆盖文档生命周期的不同阶段。远期引入顺序：先 DocAgent（施工阶段验证）→ 再 Cascade（运维阶段验证）

**5 层语义对齐校验（v0.8.0 补充参考）**：

> [CSDN 2026-06](https://blog.csdn.net/FastProceed/article/details/160023423) 提出 AI 原生文档生成的 5 层语义对齐校验机制（AST+LLM 双模态 + 语义距离矩阵 KL 散度 + 运行时契约 @pre/@post + AST-IR 双视图 + 契约合规性报告表）。比 Cascade 更重（需 IR/控制流图），但提供了"文档命题→AST 证据→IR 证据"的三元校验框架——远期若需更精细的语义验证，可参考此框架设计 design_memos 的"业务规则→代码实现→查询执行计划"三层对齐。当前不采纳（IR 分析成本过高，§9 已排除 AST 全量解析）。

**Google OKF v0.2 `generated` vs `verified` 分离 + `Attested Computation` 验证概念（v1.9.0 新增，参考 [itbrief.asia 2026-07-27 Google OKF v0.2](https://itbrief.asia/story/google-adds-trust-provenance-to-open-knowledge-format)）**：

> [Google Open Knowledge Format v0.2（2026-07-27 发布）](https://itbrief.asia/story/google-adds-trust-provenance-to-open-knowledge-format) 在知识包 frontmatter 中新增 5 类 trust/provenance 信号：provenance（来源）/ trust（generated vs verified）/ freshness（stale_after）/ lifecycle（draft/stable/deprecated）/ attestation（Attested Computation）。§7.0.5 v1.9.0 已在状态指纹对比中引用 OKF v0.2 的 freshness 维度，此处补入 **trust 分离 + attestation** 两个维度在 §7.0.6 验收闭环中的映射——区分"文档是怎么来的"（generated）vs"文档被谁验证过"（verified）vs"验证过程本身是否可信"（attested）。

**OKF v0.2 三层验证信任模型**（映射到本审查 §7.0.6 验收闭环）：

```
OKF v0.2 trust 信号                    本审查 §7.0.6 对应
──────────────────────────────────────────────────────────────
1. generated（生成方式+时间）     →    §7.0.2 代码反推草稿（AI 生成）
   - "此文档由 AI 代码反推生成"          - frontmatter 或 inline 标注 "drafted_by: code_reverse_extraction"
   - 记录生成方法非验证结果               - 记录"这是草稿，尚未验证"

2. verified（验证确认）           →    §7.0.6 L1/L2/L3 验收通过
   - "此文档已由人工/工具验证"            - L1 存在性 + L2 消费关系（机器可查）+ L3 语义抽检（人工）
   - 记录验证者+验证时间                   - actor + verifiedAtTime（对齐 §7.0.5 docFreshnessInfo 五字段）
   - verified ≠ generated                 - AI 草稿（generated）必须经 L3 人工抽检（verified）才计入覆盖率

3. attestation（Attested Computation）  → §7.0.6 L3 抽检过程的可验证性
   - "验证计算是否用批准方法"              - L3 抽检是否真的检查了"文档描述的用法与代码行为一致"
   - 不仅是"有人签了字"                   - 而是"签的人确实执行了规定的检查步骤"
   - 防止"橡皮图章"式验证                 - 防止 L3 抽检流于形式（看了表名就说"通过"）
```

**`generated` vs `verified` 分离对本审查的价值**：

当前 §7.0.6 的验收闭环是"施工→验收"两步——但文档 frontmatter 未区分"AI 生成草案"和"人工验证通过"两阶段。v1.9.0 补入此分离：

| 阶段 | OKF v0.2 信号 | 本审查标注 | 当前实现 | v1.9.0 补强 |
|---|---|---|---|---|
| **生成** | `generated: {method: "code_reverse_extraction", timestamp: "2026-08-10"}` | frontmatter `drafted_by: code_reverse_extraction` + `draft_date` | ✅ §7.0.2 代码反推已标注"草稿" | 补入 frontmatter `verification_status: draft` |
| **验证** | `verified: {actor: "human", timestamp: "2026-08-12", method: "L3_semantic_check"}` | frontmatter `verified_by: <人>` + `verified_date` + `verification_method: L3_semantic_check` | ⚠️ L3 抽检通过后未在 frontmatter 记录"已验证" | 补入 frontmatter `verification_status: verified` + L3 抽检结果记录 |

→ **实施**：§7.0.6 验收闭环步骤 5（语义抽检）通过后，更新该表文档 frontmatter 的 `verification_status: draft → verified` + 记录 `verified_by` / `verified_date` / `verification_method`。**未标 `verified` 的文档不计入 §5.1 覆盖率分子**——与 Q score ≥ 7.0 门槛并列作为"达标"的双重条件。

**`Attested Computation` 概念对本审查 L3 抽检的价值**：

> OKF v0.2 的 `Attested Computation` 不是"验证文档内容是否正确"，而是"**验证验证过程本身是否可信**"——即"L3 抽检是否真的执行了规定的检查步骤"。这在本审查场景尤为重要——L3 人工抽检是"防假覆盖最后防线"（§7.0.6 DocPrism 11% 不一致率依据），但若 L3 抽检本身流于形式（看了表名就说"通过"），则防线失效。

**当前 L3 抽检的"橡皮图章"风险**（OKF attestation 概念揭示的盲区）：

```
当前 L3 抽检流程（§7.0.6 步骤 5）：
  每批次随机抽 2 张表 → 人工核实"文档描述的用法与代码实际行为一致"

风险：抽检者可能只看了"文档提到了表名"就说"一致"（等同 L1 存在性检查）
      → L3 退化为 L1，失去"语义一致"的验收价值
      → 文档覆盖率虚高（L3 "通过"但实际未做语义检查）
```

**v1.9.0 补入的 Attested L3 抽检清单**（参考 OKF attestation "验证计算是否用批准方法"思想）：

```
L3 抽检须逐项确认以下 4 个检查点（缺一不可），并在 verification_log 中记录每项结果：

□ 检查点 1：文档"关键字段"列出的字段是否在代码 SQL SELECT 中真实出现
  → grep 代码中 SELECT 语句 → 对比文档"关键字段"列表
  → 若文档列了字段但代码未 SELECT → ⚠️ 假覆盖（L3 不通过）

□ 检查点 2：文档"下游逻辑"描述的计算是否在代码中真实执行
  → 读代码消费该表的函数 → 对比文档描述的"计算什么指标/触发什么规则"
  → 若文档说"计算 7 因子"但代码只算了 3 个 → ⚠️ 假覆盖

□ 检查点 3：文档"消费频率"与代码调度配置是否一致
  → 检查 tasks.yaml 中该表的 schedule → 对比文档"盘后增量/周更/月更"
  → 若文档说"盘后增量"但 tasks.yaml 是周更 → ⚠️ 频率不一致

□ 检查点 4：文档"依赖上游"与 frontmatter depends_on 是否一致
  → 对比文档列出的上游表与 frontmatter depends_on 字段
  → 若文档漏列上游或 frontmatter 未登记 → ⚠️ 依赖不完整

→ 4 个检查点全过 → L3 通过，verification_status: draft → verified
→ 任一检查点未过 → L3 不通过，该表标 ⚠️ 需返工，不计入覆盖率分子
→ 抽检者须在 verification_log.md 记录每张表 4 个检查点的 ✅/⚠️ 结果
  （非仅"通过/不通过"二元判定——记录检查过程本身即为 attestation）
```

**为何补 Attested Computation 但不引入密码学 attestation**（对齐 §9）：
- **OKF v0.2 的完整 attestation** 使用密码学签名（如 Sigstore/CLASPIE）验证计算完整性——适合多方协作的开源知识包场景，个人项目无多方信任需求
- **本审查的 attestation** 是**流程 attestation**（记录检查步骤+结果）非密码学 attestation——通过 `verification_log.md` 的 4 检查点记录实现"验证过程可追溯"，而非密码学证明"验证未被篡改"
- **成本可控**：4 检查点清单是 L3 抽检的标准化模板（每张表 ~5 分钟），不增加 LLM 调用或密码学工具链成本

**与 §7.0.6 L3 主动学习分层抽样的关系**：Attested L3 抽检清单是分层抽样（不确定层/高风险层/随机层）的**执行规范**——分层抽样决定"抽谁"，Attested 清单决定"怎么抽"。两者正交：分层抽样保证"抽对表"，Attested 清单保证"抽检过程可信"。

**覆盖率目标轨迹**：

| 波次 | 目标覆盖率（英文下界） | 验收点 |
|---|---|---|
| 施工前 | 35.9%（37/103，v2.1.0 实测消费层口径） | 基线 |
| 第一波后 | ~44.7%（46/103） | 重跑扫描确认批次 A 9 张转消费层覆盖 |
| 第二波后 | ~68.9%（71/103） | 重跑扫描确认批次 B+C 25 张转消费层覆盖 |
| 第三波后 | ~93.2%（96/103） | 批次 D 25 张记录完毕——终态：59 张缺口清零，余 6 张 §6.1b dormant + 1 张真闲置不进消费覆盖目标 |

#### 7.0.7 施工回滚机制（v0.6.0 新增）

> §7.0.1-§7.0.6 定义了"如何施工 + 如何验收"，但未定义"施工引入错误时如何回滚"。补文档施工可能引入：(1) L3 语义抽检发现文档描述与代码行为不符（假覆盖）；(2) 多消费方冲突解决（§7.0.2）误判导致 alpha 信号链被风险视角吞并；(3) 拓扑排序（§7.0.3）错误导致被依赖表文档引用了未补的依赖表。v0.6.0 补入**回滚机制**，确保施工错误可逆。

**回滚触发条件**（任一命中即触发）：
- L3 语义抽检未过（§7.0.6 步骤 5）——文档描述与代码行为不符
- Q score < 4.0（§7.0.4）——模板字段缺失 >50% 或 timeliness 严重失真
- 多消费方冲突解决（§7.0.2）后，低优先级消费方文档的 alpha 视角被误删
- 拓扑依赖校验（§7.0.6 步骤 8）失败——发现跨批次阻塞未解决

**回滚分级**（按影响范围）：

| 级别 | 触发条件 | 回滚范围 | 操作 |
|---|---|---|---|
| L1 单表回滚 | 单张表 L3 未过或 Q < 4.0 | 仅该表的文档 diff | `git revert` 该表在目标文档的 commit；该表标 ⚠️ 返工，不计入覆盖率 |
| L2 批次内回滚 | 同批次 ≥3 张表 L3 未过 | 该批次内受影响的表 | 回滚该批次所有表的 commit；重跑 §3.5 Confidence 自动判定 + §7.0.2 反推；排查共因（如模板错误/反推脚本 bug） |
| L3 跨批次回滚 | 拓扑依赖校验失败导致跨批次阻塞 | 受阻塞的依赖表 + 被依赖表 | 回滚依赖表文档至"最小文档"（仅表名+业务含义）；先补齐被依赖表完整文档再重补依赖表 |
| L4 全波回滚 | 全波施工后覆盖率未上升或 Q score 平均 < 5.0 | 该波所有 commit | 回滚该波全部 commit；重跑 §6.0 RICE 评分 + §6.0 Kano 分类；排查评分模型是否失真 |

**回滚操作流程**（参考 [git revert best practices](https://git-scm.com/docs/git-revert)）：

```
1. 检测到触发条件 → 暂停该表/该批次后续施工
2. 评估回滚级别（L1-L4）→ 确定回滚范围
3. git revert 相关 commit（不删除历史，保留可追溯）
   - 单表：revert 该表在目标文档的 commit
   - 批次/全波：revert 该批次/该波的所有 commit
4. 重跑 §3.2 三层扫描 → 确认回滚后覆盖率回落至预期
5. 根因分析（5 Why）→ 记录到 docs/_audit/rollback_log.md
6. 修正根因（模板/脚本/评分模型）后重新施工
7. 重新验收（§7.0.6 全流程）
```

**不做的**（对齐 §9）：
- 不用 `git reset --hard` 回滚——破坏历史可追溯性，违反 [git 安全协议](项目级规范)
- 不自动回滚——L3 抽检未过需人工确认是否真为"假覆盖"还是"L3 抽检本身误判"
- 不回滚代码——本审查只改文档不改代码，代码回滚不在 design_memos 层

**CoDe-R DDPF 双路径回退概念（v0.7.0 新增）**：

> [CoDe-R arXiv 2604.12913v2 2026-06](https://arxiv.org/html/2604.12913v2) 提出 Dynamic Dual-Path Fallback（DDPF）机制——在反编译输出精炼中，自适应平衡"语义恢复"（semantic recovery）与"语法稳定"（syntactic stability）两条路径。v0.7.0 借鉴此概念补入本审查的回滚场景。

**CoDe-R DDPF 原理**（反编译场景）：
- **Path 1 语义恢复路径**：优先恢复高层算法意图（语义丰富但语法可能不稳定）
- **Path 2 语法稳定路径**：优先保证语法正确可执行（语法稳定但语义可能丢失）
- **Hybrid Verification**：自适应选择——当语义恢复路径的输出通过语法验证时用 Path 1，否则回退到 Path 2

**映射到本审查的回滚场景**：

| CoDe-R 路径 | 本审查回滚对应 | 含义 |
|---|---|---|
| Path 1 语义恢复 | **L1/L2 回滚后重写**：保留原消费方语义（如风险视角/alpha 视角），仅修正与代码不符的字段 | 语义优先——保留文档的业务语义价值，修正技术细节 |
| Path 2 语法稳定 | **L3/L4 回滚后重建**：回退到"最小文档"（仅表名+业务含义），重新从代码反推全部字段 | 语法优先——丢弃可能有误的语义描述，从最小可信基点重建 |
| Hybrid Verification | **§7.0.7 回滚分级自动选择**：L1/L2（单表/批次内）走 Path 1 语义恢复；L3/L4（跨批次/全波）走 Path 2 语法稳定 | 自适应——按回滚范围选择路径 |

**为何仅借鉴概念不全面采纳**：
- **场景差异**：CoDe-R 是"反编译输出精炼"——需在语法正确性与语义恢复间权衡；本审查是"文档施工回滚"——无需语法验证（文档无"语法错误"概念），仅需语义一致性验证（§7.0.6 L3）
- **Hybrid Verification 简化**：CoDe-R 的 Hybrid Verification 需运行时执行验证；本审查的"自适应选择"已简化为"按回滚级别 L1-L4 选择路径"——无需运行时验证，按影响范围静态选择
- **已内化在 §7.0.7 分级中**：§7.0.7 的 L1/L2（小范围）对应 Path 1（语义恢复，保留原描述修正细节），L3/L4（大范围）对应 Path 2（语法稳定，回退最小文档重建）——CoDe-R 的双路径思想已在回滚分级中隐式实现，v0.7.0 仅显式标注这一对应关系

**CoDe-R 对本审查的验证价值**：CoDe-R 的"双路径自适应"思想与本审查 §7.0.7 的"回滚分级"在"按影响范围选择恢复策略"上高度一致——**证明本审查的回滚分级设计与学术界 DDPF 思路对齐**，差异仅在验证机制（运行时 vs 静态分级）。

**Innovation-Residual 故障归因（v1.2.0 新增）**：

> §7.0.7 当前的回滚根因分析用"5 Why"人工追问——能定位"哪张表文档有问题"，但难以精确定位"文档施工的哪个具体操作步骤引入了错误"。[Innovation-Residual Auditing arXiv 2608.05490v1 2026-08-06](https://arxiv.org/html/2608.05490v1) 提出自主分析代理的故障归因方法——通过计算"创新残差"（实际操作与成功轨迹预测的偏差）精确定位故障步骤。v1.2.0 借鉴此思想补入 §7.0.7 回滚的根因分析。

**Innovation-Residual 原理**（arXiv 2608.05490v1）：
- **成功轨迹**：已通过 L3 抽检的表文档施工操作序列（如"提取 SQL 字段→grep 下游消费→标注依赖表→套模板→写入文档"）
- **操作预测模型**：拟合成功轨迹的操作概率分布 P(operation_t | operation_{t-1}, ..., operation_1)
- **创新残差**：对故障表文档，计算每个操作的创新残差 = actual_operation - E[operation | model]——残差最大的操作即为故障源
- **检测限（Detection Limit）**：最小可检测残差 = 2σ_innovation（σ 为成功轨迹的残差标准差）——低于此值的误差无法归因，视为正常波动

**映射到本审查的回滚根因分析**（融入 §7.0.7 步骤 5"根因分析 5 Why"）：

```
1. 收集成功施工轨迹：从已通过 L3 抽检的表文档 git log 提取操作序列
   → 操作粒度：git commit message 中的操作类型（如 "extract fields"、"grep consumers"、"mark dependency"、"apply template"）
   → 输出 success_trajectories.jsonl：[{table, operations: [op1, op2, ...], l3_pass: true}]

2. 对故障表文档（L3 未过 / Q<4.0 触发回滚），提取其操作序列
   → 输出 failure_trajectory.jsonl：[{table, operations: [op1, op2, ...], l3_pass: false}]

3. 残差计算（简化版，不训练预测模型）：
   → 统计成功轨迹中每个操作位置的操作类型分布 P(op_t | position_t)
   → 对故障轨迹的每个操作，计算残差 = 1 - P(actual_op_t | position_t)
   → 残差最大的操作位置即为疑似故障源

4. Detection Limit 过滤：
   → σ_innovation = 成功轨迹残差的标准差
   → 仅保留残差 > 2σ_innovation 的操作作为"可归因故障源"
   → 低于 2σ 的操作视为正常波动，不归因

5. 输出归因报告：failure_attribution.csv（表名 × 故障操作位置 × 操作类型 × 残差值 × 是否超检测限）
```

**示例**：
- 成功轨迹统计：position_3 的操作 90% 是"mark dependency"，10% 是"grep consumers"
- 故障表 A：position_3 的操作是"apply template"（残差=0.9，>2σ）
  → 归因：故障表 A 在第 3 步错误地"套模板"而非"标依赖"——可能跳过了依赖标注直接套模板，导致依赖关系缺失
- 故障表 B：position_3 的操作是"grep consumers"（残差=0.1，<2σ）
  → 不归因：此操作在成功轨迹中也存在，视为正常波动

**为何仅借鉴思想不全面实施**（对齐 §9）：
- **预测模型训练成本**：arXiv 2608.05490v1 的完整实施需训练操作序列预测模型（如 n-gram / Markov chain / neural sequence model）——个人项目施工操作数据量少（每波 8-15 张表 × 5 操作 = 40-75 操作），不足以训练可靠模型
- **简化版替代**：v1.2.0 用"按操作位置统计操作类型分布"替代预测模型——无需训练，用频率统计即可计算残差。代价是未捕获操作间的序列依赖（如"前一步 grep 了什么影响下一步该做什么"），但对"定位故障步骤"已足够
- **Detection Limit 的价值**：即使简化版，Detection Limit（2σ_innovation）仍能过滤"正常波动"——避免将所有偏差都归因为故障，减少误报。这是 arXiv 2608.05490v1 的核心贡献之一

**与 §7.0.7 回滚分级的对接**：
- L1 单表回滚：跑 Innovation-Residual 归因故障表 → 定位故障操作 → 修正该操作后重施工（走 Path 1 语义恢复，保留原描述修正故障步骤）
- L2 批次内回滚：若 ≥3 张表的故障归因指向同一操作位置（如都在 position_3 出错）→ 排查共因（如 §7.0.1 模板的 position_3 指引有歧义）
- L3/L4 跨批次/全波回滚：Innovation-Residual 归因无意义（大范围回滚已不是单操作问题）→ 走 Path 2 语法稳定，从最小文档重建

#### 7.0.8 努力度估算 Rubric（v0.6.0 新增）

> §6.0 的 effort_score = doc_complexity × W4 + cross_module_coupling × W5，但 doc_complexity（1-5）和 cross_module_coupling（1-3）的取值靠人工判断——[rightfeature.com 2026-02](https://rightfeature.com/blog/rice-scoring-model/) 指出"Effort 估算易被低估"是 RICE 最大反模式之一。v0.6.0 补入**努力度估算 Rubric**，量化 doc_complexity 和 cross_module_coupling 的取值标准，确保不同表的 effort 评分一致可复现。

**doc_complexity 评分 Rubric**（1-5 分，基于 §7.0.1 模板 6 字段的预估填写难度）：

| 分值 | 标准 | 代表表 | 理由 |
|---|---|---|---|
| 1 | 表名+业务含义一目了然，字段无业务逻辑，下游消费单一明确 | `kline_etf_daily` | 日 K 线，标准 OHLCV，消费方单一 |
| 2 | 字段有少量业务逻辑（如复权因子），下游消费 1-2 个模块 | `kline_daily_hfq` | 后复权需解释复权算法，消费方 1-2 个 |
| 3 | 字段有业务逻辑 + 需引用实证支撑，下游消费 2-3 个模块 | `block_trade_detail` | 大宗折价需解释信号逻辑 + 引用 2026 实证 |
| 4 | 多字段业务逻辑 + 跨表关联 + 需引用多份实证，下游 3-4 个模块 | `restricted_shares` | 解禁 4 指标 + 7 因子分层 + 30 日减仓规则 + 多消费方 |
| 5 | 复杂衍生品/跨市场逻辑 + 需建新策略文档 + 多消费方冲突 | `cb_iv` / `option_iv` | 可转债/期权 IV 需解释波动率曲面 + 套利逻辑 + 多消费方 |

**cross_module_coupling 评分 Rubric**（1-3 分，基于消费方文档数）：

| 分值 | 标准 | 代表表 | 理由 |
|---|---|---|---|
| 1 | 单一消费方文档 | `trade_calendar` | 仅 15 号数据特征层消费 |
| 2 | 2-3 个消费方文档 | `dragon_tiger` | 00 索引 / 13 regime / 24 打板 / 26 事件驱动 |
| 3 | ≥4 个消费方文档或跨域（风险+alpha+注册表） | `etf_nav` / `money_flow` | etf_nav 跨 37 风险 + 24 alpha + 62 注册表 + 15 数据层 |

**Rubric 一致性保障**：
- **双人盲评校准**（首次施工时）：对批次 A 的 9 张表，AI 按 Rubric 打分 + 人工独立打分，对比差异 >1 分的表需讨论对齐
- **Rubric 锁定后不可调**：首次施工校准后，Rubric 标准固定——后续批次直接套用，避免"为降优先级而调高 effort"
- **effort 分布审计**（每波施工后）：若 >70% 的表 effort 相同 → 触发警告，要求重评（类似 §6.0 Confidence 滥用警告）

**与 §6.0 的对接**：Rubric 取值直接喂入 §6.0 公式的 effort_score = doc_complexity × 1.0 + cross_module_coupling × 1.5。v1.1.0 已将 §6.0 示例表的 effort 值以本 Rubric 为准重新计算（v0.4.0 估算值已废弃）——`restricted_shares` doc_cpx=4 + xmod=2 → effort=7.0 / `cb_iv` doc_cpx=5 + xmod=2 → effort=8.0 / `hog_futures_core` doc_cpx=2 + xmod=1 → effort=3.5。§6.0 与 §7.0.8 现已完全一致，无差异。

#### 7.0.9 施工进度跟踪看板（v1.3.0 新增）

> §7.0.1-§7.0.8 定义了施工的"怎么做"（模板/反推/拓扑/质量/增量/验收/回滚/Rubric），但未定义"做到哪了"——哪张表已施工/在施工/未施工/已回滚的状态跟踪。多波施工中若无进度看板，易出现"遗漏某张表"或"同一张表重复施工"。v1.3.0 补入**轻量级 CSV 看板**，参考 [docsie.io Documentation Sprint 2026](https://www.docsie.io/blog/glossary/documentation-sprint/)（Kanban 列：To Do / In Progress / In Review / Published）+ [projectmanagementformula.com Kanban 2026-04](https://projectmanagementformula.com/how-to-set-up-a-kanban-complete/)（Backlog / Ready / In Progress / In Review / Done + WIP 限制）。

**为何用 CSV 矩阵而非电子看板工具**（对齐 §9 个人项目红线）：
- design_memos 是纯文本仓库，引入电子看板（Jira/Trello/Notion）破坏"docs-as-code"原则——状态应与文档同仓库可 git 追踪
- CSV 矩阵可由 §3.4 扫描脚本（`audit_data_utilization.ps1`）自动生成/更新——状态变更不靠人工填看板，靠脚本扫描 git log + 文档存在性
- 与 §3.4 `detective_scan.csv` / §7.0.4 `quality_spc.csv` / §6.0 `priority_v{n}.csv` 同目录（`docs/_audit/`），统一审计矩阵

**看板列定义**（6 状态，参考 Kanban 五列 + 回滚列）：

| 状态 | 含义 | 进入条件 | 退出条件 |
|---|---|---|---|
| **Backlog** | 待施工（已在 §6.2 批次但未启动） | §6.2 批次归属确定 | 开始 §7.0.2 代码反推 |
| **In Progress** | 正在施工（§7.0.2 反推 / §7.0.1 模板填写中） | 开始 §7.0.2 反推 | 提交 PR 进入验收 |
| **In Review** | 验收中（§7.0.6 L1/L2/L3 检查中） | PR 提交，L1/L2 自动检查 | L1/L2/L3 全通过 → Done；任一失败 → Rolled-back |
| **Done** | 施工完成（L3 通过 + Q score ≥7.0） | §7.0.6 验收全通过 | —（进入 §7.0.5 增量更新运维期） |
| **Rolled-back** | 回滚中（§7.0.7 触发） | L3 未过 / Q<4.0 / 拓扑依赖失败 | 根因修复后重施工 → In Progress |
| **Deferred** | 暂缓（业务边界待定/归档决策待定） | §10 开放问题裁定暂缓 | 业务边界决策后 → Backlog 或归档 |

**CSV 看板格式**（`docs/_audit/construction_kanban.csv`）：

```csv
table_name,batch,status,priority,q_score,l3_result,construction_date,reviewer,notes
restricted_shares,A,Done,9.5,8.5,pass,2026-08-15,AI+人,Kano基本型首批
cb_iv,B,In Progress,1.0,-,-,2026-08-16,AI,业务归集进B批
dividend_tax_node,D,Deferred,-,-,-,-,Q5归档决策待定
hog_futures_core,D,Deferred,-,-,-,-,Q4生猪归档已建议
...
```

**WIP 限制**（参考 projectmanagementformula.com 2026-04）：
- **In Progress 列 WIP ≤ 3**——单线程施工同时进行中的表不超过 3 张（避免上下文切换损耗）
- **In Review 列 WIP ≤ 5**——待验收的表不超过 5 张（避免 PR 积压）
- 超过 WIP 限制 → 脚本输出 ⚠️ 警告（不阻断，提醒先完成在制品再启动新表）

**自动状态推断算法**（融入 `audit_data_utilization.ps1`）：
```
1. Backlog：表名在 §6.2 批次表中 AND git log 无该表的施工 commit
2. In Progress：git log 有该表的施工 commit AND PR 未合并
3. In Review：PR 已提交 AND §7.0.6 验收未完成（L3 抽检未做或 Q score 未算）
4. Done：PR 已合并 AND Q score ≥7.0 AND L3 pass
5. Rolled-back：§7.0.7 回滚日志（docs/_audit/rollback_log.md）有该表记录
6. Deferred：§10 开放问题标记为"暂缓"
```

**与 §6.0 跨波次优先级动态重评的对接**（§6.0 v1.1.0）：跨波次重评输出的 `priority_v{n+1}.csv` 与本看板的 `priority` 列同步——若某表从"期望型"降级为"兴奋型"，看板 `notes` 列标注"v{n+1} 降级，下波可延后"。

**与 §7.0.7 回滚分级的对接**：回滚日志（`rollback_log.md`）记录回滚级别（L1-L4），看板 `notes` 列标注回滚级别——L1 单表回滚后状态从 Rolled-back → In Progress（修正后重施工）；L4 全波回滚后该波所有表状态从 Done → Rolled-back → Backlog（重排优先级）。

**MTTD/MTTR 回滚效能度量（v1.4.0 新增，参考 [uvik.net 2026-08-02 Data Quality KPIs](https://uvik.net/blog/data-quality-metrics-kpis/)）**：

> [uvik.net 2026-08-02](https://uvik.net/blog/data-quality-metrics-kpis/) 指出数据质量的八 KPI 中，**MTTD（Mean Time To Detect，平均检测时间）** 和 **MTTR（Mean Time To Resolve，平均解决时间）** 是 incident response 的核心效能度量——"工具本身不是主要收益，更大的收益来自强制团队定义显式质量规则和共享标准"。§7.0.7 回滚机制有 L1-L4 分级和 Innovation-Residual 归因（v1.2.0），但未度量"从文档错误发生到检测的时间"和"从检测到修复的时间"——v1.4.0 补入此度量融入 §7.0.9 看板。

**MTTD/MTTR 定义与采集**（融入 `construction_kanban.csv` + `rollback_log.md`）：

| 度量 | 定义 | 采集方式 | 目标 |
|---|---|---|---|
| **MTTD** | 从文档错误引入（git commit 时间）到错误检测（§3.4 Detective 扫描或 §7.0.6 L3 抽检发现）的时间 | `rollback_log.md` 记录 `error_introduced`（commit hash + 时间）和 `error_detected`（扫描/抽检时间），MTTD = detected - introduced | ≤7 天（Detective 扫描周级 + L3 每波抽检） |
| **MTTR** | 从错误检测到修复完成（回滚后重施工通过验收）的时间 | `rollback_log.md` 记录 `error_detected` 和 `fix_completed`（重施工 Q score ≥7.0 + L3 pass），MTTR = completed - detected | ≤14 天（L1 单表回滚）/ ≤30 天（L2-L4 批次/全波回滚） |

**MTTD/MTTR 的统计意义与个人项目适配**：
- **uvik.net 2026-08-02 的企业基准**——MTTD ≤4 小时 / MTTR ≤24 小时（自动化数据质量监控 + 告警 + 自动修复）。本审查不追求此基准——文档施工是月级波次（非实时数据管道），MTTD/MTTR 以"波次"而非"小时"为单位
- **个人项目的合理目标**——MTTD ≤7 天（Detective 扫描每周 cron + L3 每波抽检，错误最迟在下一次扫描/抽检时发现）；MTTR ≤14 天（L1 单表回滚，下一波施工前修复）。L2-L4 批次/全波回滚 MTTR ≤30 天（需根因分析+模板修订）
- **数据量限制**——个人项目施工波次少（3 波），回滚事件可能 0-3 次，MTTD/MTTR 的统计意义有限。不强制计算——仅在回滚发生时记录时间戳，积累 ≥5 次回滚事件后才计算 MTTD/MTTR 均值

**与 §3.4 Detective 扫描频率的联动**：若 MTTD 持续 >7 天目标，说明 Detective 扫描频率不足（周级太慢）→ 考虑升频到日级（但需平衡扫描成本）。若 MTTD ≤1 天但 MTTR >14 天，说明检测快但修复慢 → 检查 §7.0.7 回滚流程是否阻塞（如根因分析耗时过长）。

### 7.1 第一波：风险/回撤模块文档补齐（批次 A，1-2 周）

**目标**：补齐批次 A 共 9 张风险相关表的**消费级**文档描述（字段/频率/下游逻辑，§7.0.1 模板），消费层覆盖率 35.9% → ~44.7%（v2.1.0 口径；9 张均已有 17/64 号规划层引用，本波补的是消费语义非表名）

| 步骤 | 内容 | 产出 |
|---|---|---|
| 1 | 在 [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) §数据源节增补 `restricted_shares` / `share_unlock` 解禁压力减仓硬规则 | 文档 diff |
| 2 | 在 [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) 增补 `etf_nav` 折溢价监测（定位为流动性危机信号，非套利策略） | 文档 diff |
| 3 | 在 [10_regime_detector_spec](10_regime_detector_spec.md) 增补 `edb_data` 宏观周期输入 + `us_index` 外盘风险传导 | 文档 diff |
| 4 | 在 [24_daban_strategy_detail](24_daban_strategy_detail.md) 增补 `block_trade_detail` 机构折价大宗信号（[2026 实证](https://equity-insider.com/behind-the-big-moves-how-block-trade-alerts-are-reshaping-equity-markets/)：大宗买入≥ask 价→短期正向） | 文档 diff |
| 5 | 在 [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) 增补 `kline_futures`/`futures_position`/`futures_term` 期货对冲工具池（标注需期货账户） | 文档 diff |
| 6 | 本备忘 §5.1 文档覆盖率指标更新 | ~46% |

**验证标准**：每张表至少在 1 篇策略/风控文档中作为数据源被显式描述（不只是列表中列举）。

### 7.2 第二波：事件驱动/板块轮动文档补齐（批次 B+C，2-4 周）

**目标**：补齐批次 B（11 张，msci_adjustment 已转 §6.1b）+ 批次 C（14 张，新增 stock_indicator）共 25 张表消费级文档，消费层覆盖率 → ~68.9%

| 步骤 | 内容 |
|---|---|
| 1 | [26_event_driven_strategy_detail](26_event_driven_strategy_detail.md) 增补 cb_iv / convertible_bond_list / msci_adjustment / calendar_event / index_adjustment / ipo_schedule / share_change / rights_issue / equity_pledge_detail / margin_target_adjustment 事件流 |
| 2 | [22_sector_rotation_spec](22_sector_rotation_spec.md) 增补 concept_sector / sector_meta / sector_list / index_constituent 板块轮动数据源 |
| 3 | [15_data_feature_layer_spec](15_data_feature_layer_spec.md) 增补 industry_class_suppl / stock_valuation / analyst_forecast 数据源说明 |

### 7.3 第三波：跨市场/分钟级文档记录 + 归档决策（批次 D，按需）

**目标**：记录批次 D 各表代码用法（不接入新数据，只补文档），并对 3 张真闲置表做归档/补建决策

- 批次 D 各表在对应消费方文档补"代码已用、业务边界待定"标注——**不强制接入，只记录现状**；分钟级 K 线按 §5.3 决议由 16 号 machinery 统一承载
- 1 张真闲置表 `index_meta`（§6.1）按 §10 Q1 决策：归档则标 `status: retired`，补建则登记到 62 号 universe/benchmark
- 6 张 §6.1b 代码零引用表按 §10 Q8 决策：标 `status: dormant` 待启用，或补采集施工后转 §6.2 队列
- **后复权周/月线**（`kline_weekly_hfq` / `kline_monthly_hfq`）矛盾处理见 §10 Q3——代码已有 7 次引用，需核实代码是否实际切换为 hfq 版本，若是则反向修正 [16_technical_indicator_build_plan](16_technical_indicator_build_plan.md) §3.2

### 7.4 data_asset_registry 对接

[62_business_registry_construction](62_business_registry_construction.md) line 1715 记录 [dataflow_graph_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml) 已有 DS-001~076 共 76 条数据源登记。本审查不另起"首批 66 张"清单（v0.1.0 的"66 张"与现有 76 条矛盾）——**直接以现有 76 条为 base，按本审查 §6 缺口清单补齐剩余 27 张**（103 - 76 = 27，v2.1.0 实测——含 6 张 §6.1b dormant 表以 `status: dormant` 登记，v2.1.0 核验该 6 张当前未在 76 条内），待 S6 改名同步为 data_asset_registry.yaml。

### 7.5 归档操作位置指引（v0.5.0 新增）

> §6.1 的 3 张真闲置表生命周期决策（DEPRECATED→SUNSET→REMOVED）在 design_memos 层只记录"决策"，但归档的**实际操作在数据采集脚本层**。§9"不做什么"声明"不写归档详细方案"——v0.5.0 补入**归档操作的位置指引**（非详细方案），使归档决策可追溯到执行位置。

**归档操作分层指引**：

| 层 | 位置 | 操作 | 归档相关 |
|---|---|---|---|
| design_memos（本文） | §6.1 生命周期决策表 | 记录"该表应 DEPRECATED/SUNSET/REMOVED"决策 + 理由 | 决策层，不执行 |
| data_asset_registry | [dataflow_graph_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml) | 将该表条目标 `status: deprecated` / `sunset` / `removed` + 标 `sunset_date` | 注册表层，标记状态 |
| 采集执行 | `src/zephyr/data/implementations/` provider 任务映射（v2.1.0 修正：无逐表 `*_ingestion.py`，采集由 provider + 配置驱动，§2.4 盘点） | SUNSET 阶段：provider 任务映射中停用该表 + 保留 DDL 只读；REMOVED 阶段：移除映射 + 删 DDL | 执行层，实际归档 |
| 调度配置 | `src/zephyr/data/config/tasks.yaml` 中对应 task_id（v2.1.0 修正路径：非仓库根目录） | SUNSET 阶段：注释掉 task；REMOVED 阶段：删除 task 条目 | 调度层，停采集 |
| 数据库 | ClickHouse `c1_market.<table>` | SUNSET 阶段：保留数据只读；REMOVED 阶段：`DROP TABLE` + 备份到冷存储 | 存储层，删数据 |

**`index_meta` 归档路径示例**（v2.1.0 更新——§6.1 唯一真闲置表；v0.5.0 的 dividend_tax_node 示例随其改判 dormant VIEW 而替换）：

```
1. design_memos §6.1：标 DEPRECATED（已记录）
2. 观察 1 季度无消费方认领 → data_asset_registry 标 status: sunset + sunset_date: 2026-11-10
3. SUNSET 期（1 季度）：
   a. src/zephyr/data/config/tasks.yaml 注释 index_meta 对应 task（当前无任务，SKIP）
   b. ClickHouse 表保留只读，不再写入
4. SUNSET 期满无回滚需求 → REMOVED：
   a. 无采集脚本可删（provider 无映射，§2.4 已核验）——仅确认
   b. ClickHouse DROP TABLE c1_market.index_meta（先备份到冷存储）
   c. data_asset_registry 标 status: removed + removed_date
   d. schemas/categories/market_index_meta.py 移至 schemas/_archived/（保留 DDL 模板备查）
5. 本备忘 §6.1 表格标 ✅ REMOVED + 移除日期
```

**归档验证**（REMOVED 后）：
- §3.2 三层扫描确认 `index_meta` 在 design_memos + src/zephyr/ 均零命中（已删除）
- ClickHouse `SHOW TABLES FROM c1_market` 确认表已不存在
- `tasks.yaml` 确认 task 已删除
- 冷存储备份可恢复（年度审计抽检 1 次恢复测试，参考 [atlan 数据归档 best practices 2026-03](https://atlan.com/know/data-archival-best-practices/)："Test retrieval workflows quarterly"）

**不做的**（对齐 §9）：
- 不在本备忘写采集脚本删除的具体代码 diff——在采集脚本层执行
- 不在 SUNSET 期前删除数据——保留 1 季度只读以防下游认领
- 不自动归档——需人确认 SUNSET→REMOVED 转换（§10 Q1 决策方=人）

## 8. 与 12 注册表的关联

[62_business_registry_construction](62_business_registry_construction.md) 定稿的 12 个业务注册表中，与本审查直接相关：

| 注册表 | 关联表 | 状态 | 本审查发现 |
|---|---|---|---|
| `data_asset_registry.yaml`（REG-DATAFLOW-001） | 全部 102 张表 | ⏳ P1-B 待施工（[dataflow_graph_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml) 已有 76 条，待 S6 改名） | v0.1.0"首批 66 张"与现有 76 条矛盾——v0.2.0 修正为"以现有 76 条为 base 补齐 26 张" |
| `factor_registry.yaml`（REG-FCT-001） | technical_indicator / money_flow / dragon_tiger / block_trade 等 | ⏳ P1-A 待施工 | 候选清单合理，代码层均有引用 |
| `benchmark_registry.yaml`（REG-BMK-001） | etf_benchmark / index_weight | ✅ 已完成 4 条 | `etf_benchmark` 代码有 7 次引用（CODE_ONLY），应补登记扩展 |
| `universe_registry.yaml`（REG-UNI-001） | stock_list / st_stock_list / convertible_bond_list / etf_list / lof_list | ✅ 已完成 5 条 | `convertible_bond_list`/`etf_list`/`lof_list` 代码均有引用（CODE_ONLY），应补登记扩展 |

## 9. 不做什么（边界）

| 不做 | 理由 |
|---|---|
| 不"接入"60 张文档缺口表 | 数据已在代码层接入，只需补文档——v0.1.0"三波接入"是对现状的误判（过度工程） |
| 不在本备忘写每张表的 DDL/字段细节 | DDL 真源在 [schemas/categories/](../../../schemas/categories/)，备忘只引用稳定 path |
| 不在本备忘写每张表的接入代码 | 代码施工在策略/风控模块各自文档，备忘只记录"该表应被哪篇文档消费" |
| 不强制一次性补齐所有文档缺口 | 分波次补文档，每波完成后重评下一波优先级 |
| 不为 3 张真闲置表写"如何归档"详细方案 | 归档操作在数据采集脚本层，不在 design_memos 层 |
| 不臆造未存在的中文别名 | 中文别名校验只覆盖已知同义词，不创造新词 |
| 不替换现有数据流 | 补文档是记录已有用法，不破坏现有策略 |
| 不将 etf_nav 折溢价作为套利策略 | 个人系统无一级市场申赎资格（需 50-100 万份），仅作流动性危机监测信号 |
| 不引入外部数据目录工具（DataHub/Amundsen/Atlan） | 个人项目过度工程——PowerShell 脚本 + CSV 矩阵已满足审查需求；[aiondata.io 2026](https://www.aiondata.io/blog/beyond-the-static-catalog-how-ai-powered-discovery-is-redefi) 的 AI-powered catalog 适合企业级多团队场景，个人项目无多消费者协作需求 |
| 不用 AST 全量解析做代码引用性质分类 | §3.3 "代码层引用性质未区分"可用 AST 区分（活跃消费/模板继承/已弃用），但 AST 实现成本高于正则 10 倍——§3.5 已用正则 + 抽查替代，命中优先级 1-5 五级 Confidence 自动判定，覆盖 61 张缺口表的批量标注需求 |
| 不将 CI 门禁设为阻断（exit 1） | 个人项目不强制 CI 阻断文档覆盖率低于 80%——降级为 warn 提醒，符合渐进式治理风格（[codex.danielvaughan.com 2026](https://codex.danielvaughan.com/2026/05/16/codex-cli-automated-code-documentation-generation-docstrings-jsdoc-sphinx-ci-pipelines/) 的 exit 1 模式适合团队协作，个人项目过重） |
| 不用 LLM 做全量语义验证 | [DocPrism 2026](https://arxiv.org/pdf/2511.00215) 的 LCEF 方法可将假阳性从 98% 降到 14%，但需 LLM 逐函数调用——个人项目过重。§7.0.6 L3 语义抽检（每批次随机 2 张人工核实）是 lightweight 替代，覆盖"假覆盖"风险且无 LLM 成本 |
| 不用 WSJF 替代 RICE（v0.5.0 新增） | WSJF 的 Time Criticality 因子适合多团队 portfolio 排序（[SAFe 2026-02](https://agility-at-scale.com/safe/wsjf-weighted-shortest-job-first/)），但个人项目无竞争压力、文档补齐无硬截止日——Time Criticality 退化为"风险模块优先"已由 W2=5.0 覆盖。§6.0 已对比说明，保留 RICE 变体 + 可选混合模型备选 |
| 不用 RepoKG 知识图谱做文档生成（v0.5.0 新增） | [RepoDoc arXiv 2604.26523 2026-04](https://arxiv.org/html/2604.26523v1) 的 RepoKG + semantic impact propagation 可提升 API coverage 32.5%，但需建仓库级知识图谱——个人项目过重。§7.0.2 代码反推（grep + 上下文提取）+ §7.0.5 增量更新（git diff + 双向查找）是 lightweight 替代，复用 §3.5 正则基础设施 |
| 不用 DataQ 全量 10 维度评估文档质量（v0.5.0 新增） | [DataQ 框架](https://publicationslist.org/data/jorge-martinez-gil/ref-175/dataq.pdf) 的 10 维度（accuracy/completeness/consistency/scalability/timeliness/compatibility/similarity/provenance/readability/licensing）适合企业级 open data catalog——个人项目裁剪为 4 维 Q score（§7.0.4：completeness/accuracy/specificity/timeliness），覆盖"浅覆盖检测"核心需求 |
| 不自动生成文档内容（v0.5.0 新增） | §7.0.2 代码反推只生成**草稿**（grep + 上下文提取 + 模板套用），不自动写入文档——避免 LLM 幻觉产生"听起来合理但与代码行为不符"的假文档（比"无文档"更危险，L3 抽检难以发现）。所有草稿经人工复核 + L3 语义抽检后才写入 |
| 不用 Kano 完整双向问卷（v0.6.0 新增） | [m.zpedu.com 2026-07](https://m.zpedu.com/it/cpsj/39917.html) 的 Kano 完整问卷需"如果提供/不提供这个功能你感觉如何"双向问题 + 统计显著性样本——适合产品功能排序，**不适合个人项目的数据表文档补齐**（无用户可问卷）。§6.0 用规则映射替代（risk_module_flag=Y→基本型 / code_ref≥10→期望型 / 其余→兴奋型），是 Kano 思想的轻量实现 |
| 不用 6 轴全量审查方法（v0.6.0 新增） | [K-AI 6-axis 2026-05](https://www.k-ai.ai/en/news/auditer-corpus-documentaire-ia-methode-6-axes/) 的 6 轴模型适合企业级 RAG 语料审查（含 EU AI Act Article 12 合规需求）——个人项目无合规压力，已覆盖 4 轴（文档间冲突/未标记过时/可追溯性/新鲜度），轴 1（内部异常自动化）远期升级，轴 3（分歧重复）不适用（单仓库单版本）。§3.4 已说明覆盖现状 |
| 不强制统一多消费方语义（v0.6.0 新增） | §7.0.2 多消费方冲突解决算法明确"不强制统一"——同一表在风险文档（P0）和 alpha 文档（P1）的消费语义天然不同（如 `etf_nav` 风险视角=折溢价预警 vs alpha 视角=套利信号）。强制统一会导致 alpha 信号链被风险视角吞并，§7.0.2 用 ⚠️ 标注双语义替代强制统一 |
| 不用 git reset --hard 回滚施工（v0.6.0 新增） | §7.0.7 回滚机制明确用 `git revert`（保留历史可追溯）而非 `git reset --hard`（破坏历史）——符合 git 安全协议。施工错误应可追溯根因，不应抹除痕迹 |
| 不用 Milvus 乘法模型做 Q score timeliness（v0.7.0 新增） | [Milvus 2.6 Time-aware Ranking 2025-11](https://m.aitntnews.com/newDetail.html?newId=19523) 的 `final_score = similarity × decay_score` 乘法模型适合**检索排序**（旧文档归零沉底），但 Q score 度量的是**文档质量**非检索排名——旧文档的语义价值不应被时效性乘法归零（如 16 号技术指标文档 3 年未改仍有效）。§7.0.4 保留加法模型 `α × semantic + (1-α) × time_decay`，仅在 RAG 检索层（远期）用乘法模型 |
| 不当前采纳 DocAgent 多智能体（v0.7.0 新增） | [DocAgent arXiv 2504.08725v3 Meta AI 2025-05](https://arxiv.org/html/2504.08725v3/) 的 5 智能体协作（Reader/Searcher/Writer/Verifier/Orchestrator）是学术界 SOTA，但需 5 个 LLM 智能体多次调用——个人项目 61 张缺口表的 LLM 成本过高。§7.0.2 单 pass grep + §7.0.6 L3 人工抽检是 lightweight 替代，核心思路（拓扑排序+Truthfulness 验证）与 DocAgent 一致。远期 design_memos 100+ 篇时再引入 |
| 不当前采纳 REFORGE 8 门漏斗（v0.7.0 新增） | [REFORGE 2026-07](https://ubos.tech/reforge-a-method-for-benchmarking-llms-reverse-engineering-capabilities-in-decompiled-binary-function-naming/) 的 8 门置信度漏斗需 AST + 控制流图 + 数据流分析工具链——比 §9 已排除的 AST 全量解析更重。§3.5 的 5 级正则 + 抽查已满足 61 张表的批量标注需求，远期正则误判率 >20% 时再引入 |
| 不全面采纳 Consequence Ranking 替代 RICE（v0.7.0 新增） | [dualoop.coach 2026-03](https://www.dualoop.coach/blog/rice-vs-ice-vs-moscow-prioritization/) 的 Consequence Ranking 需对每项写"做/不做的后果"叙述——102 张表 × 2 段 = 204 段人工写作，成本高于 RICE 公式。§6.0 Kano 分类层已吸收"后果导向"思想（基本型=不做有严重后果），RICE 保留用于 102 表批量排序，Kano 前置过滤器承担 Consequence Ranking 的战略判断职能 |
| 不当前采纳 Cascade 自动化语义验证（v0.8.0 新增） | [Cascade arXiv 2604.19400v1 FSE 2026 July](https://arxiv.org/pdf/2604.19400v1) 的双重条件检测（从文档生成测试+代码，执行对比）是学术界 SOTA，但 design_memos 是架构文档（why 层）非 API 参考文档——从"解禁前 30 日减仓"业务规则生成可执行测试的难度远高于 API 签名。需测试执行环境（ClickHouse+Python pipeline），61 表 × 2 LLM 调用成本与 DocAgent 同量级。§7.0.6 L3 人工抽检已够，远期 100+ 篇文档或抽检不一致率 >15% 时再引入。Cascade 的"双重条件"思想已简化融入 L3 抽检流程 |
| 不采纳字段级血缘（v0.8.0 新增） | [Databricks Unity Catalog 2026-03](https://open-exam-prep.com/exams/databricks-engineer/data-governance-and-quality/data-lineage-and-audit-logging) + [atlan 2026-02](https://atlan.com/know/how-to-use-data-lineage-to-triage-data-quality-issues/) 的列级血缘（column-level lineage）可追踪 `orders.amount → daily_sales.total_revenue` 精细依赖——但需 SQL 解析器（Apache Calcite）+ 图数据库（Neo4j）基础设施，个人项目过重。§7.0.3 表级 Kahn 拓扑排序已满足"被依赖表先补"需求，字段级血缘的增量价值（部分字段闲置）在 102 张表规模下不显著。远期若出现"同一表部分字段闲置部分活跃"的复杂场景再评估 |
| 不用 Leiden 社区发现替代 §6.2 人工批次（v0.9.0 新增 / v1.6.0 升级 Louvain→Leiden） | [社区发现算法 2026-08](https://blog.csdn.net/agito_cheung/article/details/148170240) + [calmops.com 2026-03](https://calmops.com/algorithms/community-detection-algorithms/) 的 Leiden 算法（v1.6.0 从 Louvain 升级）可从依赖图自动发现紧耦合表簇——但社区发现按**依赖密度**分批不含**业务优先级**语义（风险优先原则）。§6.2 人工批次保证"风险表先补"的业务优先级，Leiden 仅作**验证工具**验证批次边界合理性（若社区跨越批次则合并、若批次内含多个小社区则拆分）。Leiden 需 python-igraph + leidenalg 库，封装为 `scripts/community_detection.py` 验证脚本，不替代主流程 |
| 不采纳 DocPilot auto-fix 全流程（v0.9.0 新增） | [DocPilot 2026](https://github.com/wyattstanson/docpilot) 的两 pass 质量门+置信度路由（auto-fix / draft / flag）是 CI/CD 文档自愈 SOTA——但 auto-fix（confidence ≥ 0.9 自动应用修复）对金融系统文档风险过高（LLM 可能"自信地错误"修复 T+1→T+0）。本审查仅吸收 **Pass 1 false-positive filter**（判断代码变更是否真的影响文档），不采纳 Pass 2 repair_engine 的 auto-fix——保留 §9"不自动生成文档"红线，人工 review 不可省 |
| 不用 Detective 扫描的 Option A scheduled agent（v0.9.0 新增） | [hassette #634 2026-04](https://github.com/NodeJSmith/hassette/issues/634) 的 Detective 扫描三选项中，Option A（scheduled Claude agent 每周扫描）语义检查强但 LLM 成本高。本审查选 Option C Hybrid——确定性检查（路径/表名/命令/链接完整性）用 PowerShell 脚本（融入 `audit_data_utilization.ps1`），语义检查用 §7.0.6 L3 人工抽检。Agent 仅做检测不做修复（§9 红线），Option A 的 LLM 价值有限 |
| 不只用 Shewhart 单点控制图做 Q score 趋势分析（v1.0.0 新增） | [AIAG-VDA SPC Manual 2026 July](https://leoardent.com/2026/07/what-is-new-in-the-aiag-vda-spc-manual-key-changes-explained/) 明确：Shewhart 3σ 控制图只检测单点越界（Q 突然从 9 跌到 4），无法检测渐进漂移（Q 从 9.0→8.5→8.0→7.5→7.1 连续 5 波下降但每波都"达标"）。§7.0.4 v1.0.0 补入 EWMA（指数加权移动平均）+ CUSUM（累积和）三图联用——Shewhart（突变）+ EWMA（渐进漂移）+ CUSUM（小幅持续偏低）全覆盖。不退回"只用 Shewhart Q<4.0 返工"的单点检测 |
| 不对 102 张表的小规模依赖网络过度依赖 CPM（v1.0.0 新增） | [CPM 2026](https://symplprocess.com/learn/critical-path-method) 的关键路径法在大型工程项目（数百节点）价值最高——102 张表的依赖链较浅（最长链 4-5 层），CPM 识别的关键路径与 Kahn 拓扑序的差异有限。§7.0.3 v1.0.0 补入 CPM 作为"资源优先分配"指导（关键路径表 TF=0 优先保障），但不替代 Kahn 拓扑排序（Kahn 解决顺序，CPM 解决工期，两者正交）。单线程施工时 CPM 的并行价值有限，主要价值在"避免在非关键表上耗时导致关键表来不及" |
| 不做完整贝叶斯先验 elicitation + MCMC 采样（v1.0.0 新增） | [Bayesian Prioritization 2026](https://discovery.researcher.life/article/bayesian-prioritization-in-product-strategy-embedding-predictive-analytics-into-agile-decision-making/c78a7b57c8ce3a1cb50c3266abaefa9f) 的完整实施需先验 elicitation（专家访谈定先验分布）+ MCMC 采样（PyMC/Stan 计算后验）——102 张表 × 5 权重 × 多波施工的后验计算量对个人项目过重。§6.0 v1.0.0 仅**形式化定义**贝叶斯公式（记录 P(W\|E)=P(E\|W)×P(W)/P(E) + 触发条件"偏差连续 2 波超 2σ"），实际执行仍用启发式校准循环（人工对比高低分表），贝叶斯作为理论依据证明启发式合理性。远期施工波次 >5 时再引入 PyMC 自动化 |
| 不用纯主动学习模型替代分层抽样（v1.1.0 新增） | [Smart Active Sampling arXiv 2209.11464](https://arxiv.org/pdf/2209.11464.pdf) 的纯主动学习需训练预测模型"哪些表最可能不一致"——但 L3 抽检数据量少（每波 2-3 张），不足以训练预测模型。§7.0.6 v1.1.0 用分层抽样（§3.5 Confidence + §6.0 Kano 分类作为"不确定性代理"）+ [ISO 2859-1:2026](https://www.iso.org/cms/render/live/en/sites/isoorg/contents/data/standard/08/54/85464.html) skip-lot 规则作为轻量替代——无需训练模型，用已有分类信息驱动抽样决策 |
| 不用 Pareto 前沿替代 RICE 排序（v1.1.0 新增） | [asi-build GoalPrioritizer 2026-04](https://github.com/web3guru888/asi-build/wiki/Phase-30-Goal-Prioritizer) + [pymoo NSGA-II 2026-08](https://blog.csdn.net/gitblog_00365/article/details/152063163) 的 Pareto 多目标优化（non-dominated sorting + crowding distance）可保留多目标结构不聚合为单一 priority——但 102 张表规模下 RICE 的"虚假精确性"是可接受的近似（priority=6.0 vs 5.0 的差异不决定"做不做"，只决定"先做谁"）。Pareto 前沿可视化在 102 表规模下信息密度过高（前沿可能含 30-50 个非支配解），反而降低决策效率。RICE 公式可计算 + Kano 前置过滤器已足够，Pareto 前沿作为远期可视化工具记录备查 |
| 不全面实施 Innovation-Residual 审计（v1.2.0 新增） | [Innovation-Residual Auditing arXiv 2608.05490v1 2026-08-06](https://arxiv.org/html/2608.05490v1) 的完整实施需训练操作序列预测模型（n-gram/Markov chain/neural sequence model）——个人项目施工操作数据量少（每波 8-15 张表 × 5 操作 = 40-75 操作），不足以训练可靠模型。§7.0.7 v1.2.0 仅借鉴"创新残差"思想用频率统计替代预测模型（按操作位置统计操作类型分布计算残差），配合 Detection Limit（2σ_innovation）过滤正常波动。完整实施远期施工波次 >5 且操作数据 >500 条时再评估 |
| 不引入 DoWhy 因果推断（v1.2.0 新增） | [CONTINUUM 2026](https://github.com/HarshTomar1234/continuum) 的因果归因（causal attribution）需额外数据标注——构造反事实（counterfactual）"若不做这步操作文档质量会如何"需对照实验，本审查 L3 抽检样本量不足（每波 2-3 张），无法支撑因果推断的统计显著性。§7.0.7 v1.2.0 的 Innovation-Residual 是**相关性归因**（残差大的操作与故障相关），非因果归因（残差大的操作导致故障）——对"定位故障步骤"已足够，因果链推断远期数据充足时再引入 DoWhy/EconML |
| 不引入完整 FMEA RPN 施工风险评估（v1.3.0 新增） | [ASQ FMEA 2026](https://asq.org/quality-resources/fmea) + [Tractian 2026](https://tractian.com/en/glossary/fmea-failure-mode-and-effects-analysis) 的 RPN = Severity × Occurrence × Detection（1-10 分三维评分）适合制造业/航空/医疗的系统性风险预防——但施工风险评估的三要素已分散覆盖：Severity（文档错误的影响严重度）由 §6.0 Kano 基本型覆盖（risk_flag=Y 的表文档错误影响大）；Occurrence（施工错误发生概率）由 §7.0.8 Rubric 的 effort 间接反映（高 effort 表更易出错）；Detection（错误能否被发现）由 §3.5 Confidence + §7.0.6 L3 抽检覆盖。引入完整 FMEA RPN 会重复计算已覆盖的维度，且 102 张表 × 3 维度 × 1-10 分 = 3060 次评分对个人项目过重。§7.0.9 施工进度看板的 `notes` 列标注 Kano 类型 + Confidence 级别作为简化风险信号已够 |
| 不引入 Staleguard/knowledge-diff 外部漂移检测工具（v1.3.0 新增） | [Staleguard Arthur920 2026-06](https://github.com/Arthur920/Staleguard)（Rust 实现的本地离线文档漂移检测，零假阳性，CI alignment score）+ [knowledge-diff oarisur 2026-05](https://github.com/oarisur/knowledge-diff)（读 code diff → 找相关文档 → LLM 判断是否矛盾 → 评论 PR + 可选开 patch PR）是 2026 文档漂移检测 SOTA 工具——但两者都是通用代码仓库工具，需 Rust/Node.js 工具链集成。本审查 §3.4 Detective 扫描已用 PowerShell 脚本覆盖 5 类检查（路径完整性/表名一致性/命令有效性/交叉引用完整性/代码符号漂移 v1.3.0），§7.0.5 增量更新已用 git diff + 双向查找覆盖代码变更触发的文档更新。knowledge-diff 的"LLM 判断代码变更是否与文档矛盾"是语义检查，本审查用 §7.0.6 L3 人工抽检替代（§9 已声明不自动生成文档）。引入外部工具的工具链成本高于 PowerShell 脚本增量价值，且违反"派生产物不入 git"约束 |
| 不引入 AI 增强自适应 SPC（v1.4.0 新增） | [AIAG SPC 3rd Edition 2026-07](https://ifactoryapp.com/industries/automotive-manufacturing/daptive-control-limits-automotive-stamping-quality-engineers-predictive-maintenance)（ifactoryapp 2026-06-03 报道）正式将"AI 增强自适应 SPC"纳入标准——包括 ML 驱动的根因识别 + 实时 Cpk 追踪 + 预测性维护触发，40-65% 非计划停机减少。但完整方案需 ML 模型训练 + 实时数据流 + CMMS 集成——个人项目 Q score 波次少（月级）+ 无实时数据流 + 无制造设备预测性维护需求，AI 增强的增量价值低于实现成本。§7.0.4 v1.4.0 仅借鉴"自适应控制限"思想（基线重算触发条件），用最近 5 波数据重新拟合 μ_0/σ_EWMA 替代 AI 持续微调——离散自适应（触发时重算）而非连续自适应（AI 持续微调），但对月级波次的 Q score 已足够 |
| 不引入 Ticket Deflection Rate 等 KB 消费效果指标（v1.5.0 新增） | [finaldoc.io 2026-03-20](https://finaldoc.io/blog/5-metrics-documentation-teams) 的 5 项文档团队指标（Search Success Rate / Content Health Score / Ticket Deflection Rate / Reader Feedback Sentiment / Content Coverage）+ [drexplain.com 2026-05-12](https://www.drexplain.com/press/articles/how_do_you_know_if_your_user_documentation_is_actually_working/) 的文档 NPS + [supportbench.com 2026-02-07](https://www.supportbench.com/knowledge-base-roi-b2b-deflection-assisted-resolution/) 的 Deflection ROI 公式——都是面向"有搜索功能+ticket 系统+帮助台"的在线知识库（KB）。本审查的 design_memos 是 git 仓库的 markdown 文件，无搜索功能/无 ticket 系统/无帮助台/无读者反馈投票——Ticket Deflection Rate = (doc views)/(doc views + tickets) × 100 的分母无数据。个人项目的"文档消费效果"用"文档引用次数变化"（§3.2 三层校验的 design_memos grep 命中数）作为代理指标——文档施工后该表在 design_memos 中的引用次数是否增加。不引入传统 KB 指标 |
| 不引入 Financial Impact 技术债框架（v1.5.0 新增） | [technicaldebtcalculator.com 2026](https://technicaldebtcalculator.com/frameworks) 的 Financial Impact = team_size × loaded_salary × debt_time_fraction × age_multiplier——需团队规模+薪酬+债务时间占比+年龄乘数四个参数。个人项目无团队（1 人 + AI）、无薪酬成本（个人时间不计薪）、debt_time_fraction 无法定义（无"非债务工作时间"对照）。§6.0 v1.5.0 SQALE 技术债视角已用 TDR（remediation_cost / development_cost）+ Kano 分类作为 Annual-Interest 代理（基本型=高利息），不需 Financial Impact 的工时成本量化 |
| 不引入 ODCS YAML 工具链做 Data Contract（v1.7.0 新增） | [soda.io 2026-06](https://soda.io/blog/data-contracts-vs-schema-registry) + [datus.ai 2026-06-29](https://datus.ai/blog/what-is-data-contract/) 的 Open Data Contract Standard (ODCS) YAML 工具链（dbt model contracts / datacontract.com / Soda CLI）适合企业级多团队数据平台——本仓库 schemas/categories/*.py DDL 已定义结构，design_memos 已承载语义，再写一份 ODCS YAML 是派生产物（违反 project_memory"派生产物不入 git"约束）。v1.7.0 仅用 Data Contract **概念**重构理解（§2.2 六组件完整度映射），不引入工具，不改变文件结构。§8 data_asset_registry 施工时参照 ODCS 六组件完整性检查清单即可 |
| 不用 Temporal Coupling 替代 Leiden 静态社区发现（v1.7.0 新增） | [codebase-memory-mcp #928 2026-07-07](https://github.com/DeusData/codebase-memory-mcp/issues/928) 的 co_changed 时序耦合可发现隐藏依赖（无 DDL 依赖但频繁共变的表对），但 **Temporal Coupling 是动态行为依赖，Leiden 是静态结构依赖**——两者正交不互斥。Temporal Coupling 可能产生假阳性（同一 sprint 任务被一起改但业务无依赖），需人工复核。§7.0.3 v1.7.0 补入 Temporal Coupling 作为 Leiden 的**补充验证**（三层验证：Kahn 拓扑序 + Leiden 静态社区 + Temporal Coupling 动态共变），不替代。且冷启动约束：commit 数 < 50 时统计不显著 |
| 不引入完整 SATD NLP 分类模型（v1.7.0 新增） | [arXiv 2603.15883v2 PEARC 2026 July](https://arxiv.org/html/2603.15883v2) 的 semantic embedding-based prioritization heuristic + fine-tuned transformer sentiment 需训练 NLP 模型——个人项目 SATD 数据量不足（~50-100 条标记），不足以训练。§6.0 v1.7.0 用规则映射替代（grep + 正则识别 SATD 标记 + 手动情感分类 + 传播链长度计数），覆盖"传播链长=高优先"核心洞察。完整 NLP 模型远期 SATD 标记 >500 条时再评估 |
| 不实施 Tarjan SCC 环检测（v1.8.0 新增） | [quant67.com 2026-06-08](https://quant67.com/post/algorithms/48-topo-sort/topo-sort.html) 的 Tarjan 强连通分量算法可一次性识别所有 SCC 并构建凝聚 DAG，但 102 表的依赖图预期无环或极少环（表间依赖是树形/森林结构），Tarjan SCC 的"多环交叉"场景在本仓库不会出现。§7.0.3 v1.8.0 用 DFS 三色标记提取环路径（O(V+E)，Kahn 检测到环后才运行，零常态开销）已足够，Tarjan SCC 作为"环数量>5 时的升级路径"记录不实施。三层递进：Kahn 检测"有没有环"→ DFS 三色标记提取"环路径"→（环复杂时）Tarjan SCC 识别"所有 SCC" |
| 不自动修复 predict Omissions 检测结果（v1.8.0 新增） | [CodeScene 2.4.0 predict Omissions](https://docs.enterprise.codescene.io/versions/2.4.0/guides/technical/temporal-coupling.html#use-temporal-coupling-to-predict-omissions) 可预测"schema 变了但文档没跟"的遗漏，但修复需 LLM 生成文档内容——§9 已声明"不自动生成文档"红线（金融系统文档 LLM 可能"自信地错误"修复 T+1→T+0）。§7.0.5 v1.8.0 的 predict Omissions 仅输出 `predicted_omission.csv` 标记需复核的文档（HIGH/MEDIUM/LOW 严重度分级），注入 §7.0.5 增量更新流程触发 false-positive filter → 标记需重写 → 由 §7.0.2 代码反推草稿 + L3 人工抽检处理。预测≠修复，人工 review 不可省 |
| 不引入 Google OKF v0.2 完整工具链（密码学 attestation）（v1.9.0 新增） | [Google Open Knowledge Format v0.2（2026-07-27 发布）](https://itbrief.asia/story/google-adds-trust-provenance-to-open-knowledge-format) 的完整 attestation 使用密码学签名（Sigstore/CLASPIE）验证计算完整性——适合多方协作的开源知识包场景（需密钥管理 + 签名验证 + 分发链）。个人项目无多方信任需求（单作者 + AI），密码学 attestation 的基础设施成本远超增量价值。§7.0.6 v1.9.0 仅借鉴 Attested Computation **思想**（L3 抽检清单 4 检查点逐项记录 ✅/⚠️ 替代二元"通过/不通过"，记录验证过程本身即为 attestation 的轻量实现），不引入密码学签名工具链。OKF v0.2 的 trust 分离（generated vs verified）用 frontmatter `verification_status: draft/verified` 字段标注替代，不引入 OKF 知识包 frontmatter 格式 |
| 不引入 DataHub docFreshnessInfo aspect 工具链（v1.9.0 新增） | [DataHub PR #19023 2026-08-09](https://github.com/datahub-project/datahub/pull/19023) 的 `docFreshnessInfo` 是 metadata platform 的 aspect——需 DataHub server + ingestion pipeline + metadata graph + GraphQL API 基础设施。与 §9 已声明的"不引入外部数据目录工具（DataHub/Amundsen/Atlan）"一致，docFreshnessInfo 是 DataHub 的内建 aspect，引入它即引入整个 DataHub 平台。§7.0.5 v1.9.0 仅借鉴 `verifiedAtVersion` 状态指纹**机制**（frontmatter 记录 `verifiedAgainstUrns` 上游表集合 + 联合 hash + 一跳 lineage 传播），用 git + frontmatter + PowerShell 脚本（`scripts/freshness_fingerprint.py`）实现轻量版——不依赖 DataHub server，结果存 CSV 而非 metadata graph。状态指纹的核心思想（用内容 hash 而非时间戳判断新鲜度）可在无 DataHub 环境下完整复刻 |
| 不为 53 张规划层覆盖表全部补消费级文档（v2.1.0 新增） | v2.1.0 三层口径实测：53 张仅 17/64 号规划层覆盖的表中 6 张代码零引用（§6.1b）——无代码消费可反推（§7.0.2 无源），补消费文档是凭空编写。仅 47 张代码活跃表进 §6.2 施工队列；代码零引用表注册表登记 dormant 即可。"为凑覆盖率而给无消费方的表写消费文档"=浅覆盖反模式（§7.0.4 Q score 防的就是它） |
| 不追溯复现 v0.2.0 历史扫描数字（v2.1.0 新增） | v0.2.0 逐表引用计数以未提交工作区为扫描对象，2026-08-12 git 提交态重扫不可复现（§2.2 声明）。v2.1.0 起以实测为准，且 §3.4 扫描输出必须落地 CSV 快照随施工提交（dogfood 本文机制）——历史审计数字无法回溯验证的教训只记录不再纠缠 |
| 不引入 SetGo metadata readiness 工具链（v2.0.0 新增） | [SetGo SSDBM '26 2026-08-11](https://dlnext.acm.org/doi/10.1145/3828820.3828827) 是开源 Python 工具包，评估+修复科学数据集的 **metadata readiness** 六维（FAIR 合规/许可/溯源/治理/可复现/目录就绪），assess→enrich→publish 闭环将 FAIR 分数从 52-57% 提升到 81-91%，发布到 Hugging Face Hub/CKAN/OpenMetadata + Croissant 1.0 metadata sidecar，集成 LLM coding agent /setgo skill。六维中：许可（licensing）不适用（本仓库自采市场数据无外部 dataset 许可约束）/ 目录就绪（catalog readiness）不适用（无外部目录发布需求，design_memos 即内部目录）/ 可复现（reproducibility）部分相关（数据管道可复现已由 tasks.yaml 覆盖）。剩余 3 维（FAIR 合规/溯源/治理）已由 §7.0.4 Q score 4 维（completeness/accuracy/specificity/timeliness）+ v1.7.0 ODCS 6 组件（schema/语义/质量/SLA/所有权/变更管理）覆盖。SetGo 面向科学数据集对外发布场景（ERA5 气候/材料/PDB 蛋白质组发布到 HF Hub），本审查是内部市场数据文档覆盖审计无对外发布需求。SetGo 的 assess→enrich 思想已由 §7.0.2 代码反推（assess 代码用法）+ §7.0.1 模板套用（enrich 补文档）+ §7.0.6 L3 抽检（verify）三步覆盖，/setgo LLM agent skill 与 v0.7.0 DocAgent 远期路径同质（LLM 多步调用成本过高）。不引入 SetGo 工具链+Croissant 1.0 sidecar（派生产物不入 git 约束） |

## 10. 开放问题

> 以下需人决策，AI 不擅自发挥。Q1/Q3 为内容决策，Q4-Q6 为流程决策。**Q2/Q7 已由 AI 裁定**（默认建议明确，属 project_memory"明显可建议的，AI 给默认建议即可"范畴）。

### 10.1 已裁定项（AI 决策，记录备查）

| # | 问题 | 裁定 | 理由 |
|---|---|---|---|
| Q2 ✅ | 61 张文档缺口表按 §6.2 四批次顺序补，还是按 §6.0 评分模型排序？ | **两者结合**：批次归属用 §6.2 消费方模块归集（风险优先），批次内排序用 §6.0 priority 分数降序（同批次内高分表先补），同批次内再按 §7.0.3 拓扑排序确保被依赖表先补 | 批次归属保证"风险模块优先"原则（W2=5.0），批次内 priority 排序保证"高分先补"效率，拓扑排序保证"无返工"——三者正交可叠加。v0.5.0 施工算法补齐后，排序逻辑已可脚本化（`topo_order.csv`） |
| Q7 ✅ | 是否引入 Kano 分类层作为 RICE 前置过滤器？（v0.6.0 新增） | **引入**——§6.0 Kano 分类层（基本型/期望型/兴奋型/无差异型/反向型）作为 RICE 前置过滤器。基本型（risk_module_flag=Y）无论 RICE 分多少必须补文档。用规则映射替代完整问卷（risk_module_flag=Y→基本型 / code_ref≥10→期望型 / 其余→兴奋型），无需人决策 | 基于 project_memory 风险优先原则 + 代码引用性质可自动裁定——风险红线表（restricted_shares/share_unlock/etf_nav/limit_up_down/margin_trading）无论 RICE 分多少必须补文档，这是"生存底线"非"优先级权衡"。Kano 完整问卷列入 §9"不做什么"（无用户可问卷）。v0.7.0 Consequence Ranking 批判进一步验证：Kano 基本型=Consequence Ranking 的"不做有严重后果"，已内化后果导向 |

### 10.2 待人决策项

| # | 问题 | 默认建议 | 决策方 |
|---|---|---|---|
| Q1 | 1 张真闲置表 `index_meta` 的生命周期裁定（§6.1，v2.1.0 从 3 张收敛）？ | 默认建议 DEPRECATED 观察期——v0.2.0"补建激活"前提（index_constituent 需 meta 配合）已弱化：index_constituent 规划层已覆盖且 index_meta 五源全零。若 62 号 universe/benchmark 施工需要 meta 字段则转 ACTIVE 补建，否则 1 季度无认领 → SUNSET → REMOVED（§7.5 归档路径） | 人 |
| Q8（v2.1.0 新增） | 6 张 §6.1b"代码零引用但规划已登记"表的处置？（dividend_tax_node/index_adjustment/ipo_schedule/margin_target_adjustment/msci_adjustment/stock_valuation） | 默认建议：dividend_tax_node 免归档（DB 派生 VIEW 零成本，标 dormant）；其余 5 张标 `status: dormant` 保留 DDL，待对应消费方启用（26 号事件驱动/15 号估值）时补采集——不删表不补采集，注册表登记即可 | 人 |
| Q3 | 后复权周/月线（`kline_weekly_hfq` / `kline_monthly_hfq`）代码已有 7 次引用，但 [16_technical_indicator_build_plan](16_technical_indicator_build_plan.md) §3.2 三级时间框架栈用未复权 `kline_weekly`/`kline_monthly`——是否统一？ | 先用 §3.5 Confidence 自动判定核实代码 7 次引用性质：若优先级 1（SQL/数据加载，confidence=1.0）则活跃消费，反向修正 16 号改用 hfq；若优先级 2（import 注册，confidence=0.5）则模板继承，清理代码引用 + 16 号维持现状 | 人（需代码核实） |
| Q4 | 本审查是否登记 ARCH 条目到 [architecture_issue_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)？ | 拟登记条目（编号待裁定后按治理段分配，本文不引用未登记编号）：消费层文档覆盖 35.9% < 80% 基准的治理议题 | 人 |
| Q5 | 是否在 [00_index_trading_decision.md](00_index_trading_decision.md) §7.3 占用表登记 63 号文档？ | ✅ 已登记（v2.1.0 核验 line 71）——但版本字符串停留在 "draft v0.9.0" 且 00 号目录计数（42 篇）落后于实际（47 篇），需 00 号维护方同步（不越界改 00 号，记录待办） | 人（00 号维护方） |
| Q6 | 是否将文档覆盖率纳入 pre-commit warn？（v0.3.0 新增） | 建议纳入——封装 §3.2 扫描为 `scripts/audit_data_utilization.ps1`，pre-commit 调用后若覆盖率 < 80% 则 warn（不阻断）。符合 [CI 文档覆盖率门禁](https://codex.danielvaughan.com/2026/05/16/codex-cli-automated-code-documentation-generation-docstrings-jsdoc-sphinx-ci-pipelines/)（2026-05）实践但降级为 warn 适配个人项目 | 人 |

> v0.1.0 的 Q3（A+H/美股/期货业务边界）/Q4（LOF 归档）/Q5（生猪归档）不再列为开放问题——90 号 §18 已有覆盖范围裁定（LOF 是 P0 保留、股指期货 P2 需期货账户、生猪不在覆盖范围但代码有引用需核实）。v0.1.0 建议"归档 LOF"与 90 号 §18 矛盾，v0.2.0 撤销。
> v0.5.0：Q2 从待人决策移至已裁定（AI 决策），Q3 默认建议补入 §3.5 Confidence 自动判定方法替代"人工核实代码引用性质"。
> v0.6.0：Q7（Kano 分类层）新增并直接 AI 裁定为"引入"——基于风险优先原则可自动裁定，无需人决策。
> v0.7.0：无新增开放问题——v0.7.0 的 5 项算法对比（Milvus/DocAgent/REFORGE/CoDe-R/Consequence Ranking）均 AI 裁定为"远期升级路径或不采纳"，理由充分无需人决策。
> v0.8.0：无新增开放问题——v0.8.0 的 3 项算法对比（Cascade 双重条件/消费链路主动监控/字段级血缘）均 AI 裁定：Cascade+字段级血缘为"远期升级或不采纳"，消费链路主动监控直接补入 §6.1（与现有生命周期管理融合，非新决策项）。
> v0.9.0：无新增开放问题——v0.9.0 的 5 项算法对比（Syntropy 编码会话级新鲜度/SITS2026 Doc-Entropy Ratio/DocPilot 两 pass 质量门/Louvain 社区发现/Preventive-Detective 双层检测）均 AI 裁定：Syntropy+Doc-Entropy Ratio+DocPilot false-positive filter+Louvain 验证+Detective Hybrid 直接补入对应章节（强化现有方法，非新决策项），DocPilot auto-fix+Detective Option A agent 为"不采纳"（§9 已记录理由）。
> v1.0.0：无新增开放问题——v1.0.0 的 4 项算法补强（SPC EWMA/CUSUM 趋势分析/CPM 关键路径识别/贝叶斯权重更新形式化/有赞调度感知差异化弃用阈值+MIN_AGE_DAYS 安全过滤）均 AI 裁定：SPC 三图联用直接补入 §7.0.4（检测渐进漂移非新决策项），CPM 补入 §7.0.3 作为 Kahn 拓扑排序的工期补充（不替代，两者正交），贝叶斯仅形式化定义（不全量实施 MCMC，§9 已记录），有赞差异化阈值+MIN_AGE_DAYS 补入 §6.1 强化主动消费监控（消除月级/季级表假阳性，非新决策项）。4 项均强化现有方法，无需人决策。
> v1.1.0：无新增开放问题——v1.1.0 的 4 项修复/补强（§6.0 示例表 effort 与 §7.0.8 Rubric 矛盾修复/L3 主动学习分层抽样策略/SPC 冷启动三阶段处理/跨波次优先级动态重评算法）均 AI 裁定：effort 矛盾修复是数值一致性校正（非决策项），L3 分层抽样用已有 §3.5 Confidence+§6.0 Kano 分类驱动（无需人决策抽样对象），SPC 冷启动是 AIAG-VDA 2026 统计学必需（数据不足时降级到 Shewhart 是标准实践），跨波次重评仅提供批次调整**建议**不自动执行（§10 Q2 已裁定批次归属由 §6.2 消费方模块归集，人工确认）。4 项均修复内部矛盾或强化现有方法，无需人决策。
> v1.2.0-v1.4.0：无新增开放问题——12 项算法补强（Model drift 分类/Western Electric 8 规则/Innovation-Residual 故障归因/Nelson Rules 名称修正/施工进度看板/symbol-level drift/Hotelling T² 远期/Nelson Rules 误报率风险矩阵/自适应控制限/MTTD/MTTR/DoWhy 排除/FMEA 排除）均 AI 裁定：漂移分类+SPC 模式识别+故障归因直接补入对应章节强化现有方法，名称修正是准确性校正，看板+drift 检测是新工具但不涉及业务决策，FMEA/DoWhy/外部工具为"不采纳"（§9 已记录理由）。
> v1.5.0-v1.6.0：无新增开放问题——8 项算法补强（SQALE TDR/Kahn 环检测/Leading vs Lagging/KB 指标排除/Financial Impact 排除/Leiden 升级/Cognitive+AI-Generated Debt/Binarly 再分配/paired-model 远期）均 AI 裁定：SQALE+环检测+指标分类直接补入对应章节强化现有方法，Leiden 升级是算法选型修正（Louvain bug 已有学术共识），Cognitive/AI-Generated Debt+Binarly 是债务框架扩展非新决策项，paired-model 为远期路径不采纳。KB 指标+Financial Impact 为"不采纳"（§9 已记录理由）。
> v1.7.0：无新增开放问题——5 项算法补强（Temporal Coupling 隐藏依赖/Data Contract ODCS 概念重构/SATD 跨制品传播优先级/AI 技术债 7 类映射/Leiden 选型结论修正）均 AI 裁定：Temporal Coupling 补入 §7.0.3 作为 Kahn+Leiden+CPM 的动态依赖补充（三层验证→四件套，不替代静态方法），Data Contract 概念重构仅改变理解不改变施工计划（不引入 ODCS 工具链），SATD 传播是 RICE confidence 调整因子（非新决策项），AI 技术债 7 类映射验证覆盖完整性（6/7 适用已覆盖，第 2 类不适用），Leiden 修正是一致性校正（v1.6.0 状态行已提及但选型结论漏改）。5 项均强化现有方法或修正内部不一致，无需人决策。
> v1.8.0：无新增开放问题——8 项算法补强（Temporal Coupling commit-size 归一化/CodeScene 三信号说明/Sum of Coupling 聚合度/min-heap Kahn 确定性排序/DFS 三色标记环路径提取/Tarjan SCC 远期路径/predict Omissions schema↔doc 共变检测/ODCS v3.1.0 版本号+DCS 弃用说明）均 AI 裁定：commit-size 归一化是 Temporal Coupling 假阳性过滤（Archy #131 明确"large commits couple everything"为首 FP 源），CodeScene 三信号说明是方法适用性论证（个人项目仅用信号 a），Sum of Coupling 是聚合度指标（高 SoC=枢纽表优先关注），min-heap Kahn 是确定性排序保证可复现性（O(V log V+E)），DFS 三色标记补 Kahn 环检测的"路径提取"缺口（Kahn 只判存在性），Tarjan SCC 为远期路径不实施（102 表规模 DFS 已够），predict Omissions 是 Temporal Coupling 逆运算发现"schema 变了文档没跟"的主动遗漏预测（不自动修复，§9 已记录），ODCS v3.1.0 版本号是准确性补全（bitol.io 2025-12-07 公告）+ DCS 弃用说明是标准对齐（datacontract.com CLI 明确 DCS 已弃用）。8 项均强化现有方法或补全准确性，无需人决策。
> v1.9.0：无新增开放问题——5 项算法补强（Freshness SLO/SLI 服务级别度量+Google OKF v0.2 stale_after 固定日期对比+DataHub docFreshnessInfo verifiedAtVersion 状态指纹机制+DZone 五种管道级假新鲜失败模式+OKF v0.2 trust/provenance/attestation 三层验证信任模型+Attested Computation 验证概念）均 AI 裁定：Freshness SLO/SLI 是 Q score timeliness 的聚合层度量（单表连续值→全仓库合规率 0-100%），将"新鲜度"从连续值升级为服务级别指标+error budget 管理（SLO=90% / Error Budget=10%），是度量体系补强非业务决策项；OKF v0.2 stale_after 对比是选型论证（固定日期 vs 状态指纹，状态指纹更适合文档-代码依赖场景因需上游传播）；DataHub docFreshnessInfo verifiedAtVersion 是状态指纹机制（内容 hash 而非时间戳判断新鲜度+一跳 lineage 传播检测上游变更级联），补 git diff 事件驱动的盲区（上游表 schema 变更但下游文档未级联标记）；DZone 五种假新鲜失败模式是检测盲区补全（源端无新文件/部分分区到达/迟到上游/仪表板缓存/回填覆盖映射到文档-代码同步场景，失败模式 2/5 补动态表名追踪+回滚版本校验）；OKF v0.2 trust/provenance/attestation 三层验证信任模型是验收闭环精度补强（generated vs verified 分离用 frontmatter verification_status 标注+Attested Computation 用 L3 抽检清单 4 检查点记录验证过程）。5 项均强化现有度量/验收方法，OKF v0.2 完整工具链（密码学 attestation）+DataHub docFreshnessInfo aspect 工具链为"不采纳"（§9 已记录理由——个人项目无多方信任需求/无 DataHub 平台基础设施）。无需人决策。
> v2.0.0：无新增开放问题——1 项算法评估（SetGo metadata readiness 工具链）AI 裁定为"不采纳"：[SetGo SSDBM '26 2026-08-11](https://dlnext.acm.org/doi/10.1145/3828820.3828827) 的六维 metadata readiness 中 3 维（许可/目录就绪/可复现）对本审查不适用或已覆盖（自采市场数据无外部许可约束/无外部目录发布需求/可复现已由 tasks.yaml 覆盖），剩余 3 维（FAIR 合规/溯源/治理）已由 §7.0.4 Q score+v1.7.0 ODCS 6 组件覆盖。SetGo 面向科学数据集对外发布（HF Hub/CKAN/OpenMetadata+Croissant 1.0），本审查是内部文档覆盖审计无对外发布需求，assess→enrich 思想已由 §7.0.2+§7.0.1+§7.0.6 三步覆盖。§9 已记录理由。本版本标志 2026-08 全网最新研究（含 2026-08-11 SetGo）已全部评估完毕，文档算法体系达到当前时间点的完整性闭环。

## 11. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-10 | 0.1.0 | 初稿 | 业务数据库 101 张表 vs design_memos 42 篇文档引用审查完成，识别 43 张闲置表分 P0-P4 五档，制定三波分批接入施工计划。与 [62_business_registry_construction](62_business_registry_construction.md) 配对，为 P1-B `data_asset_registry` 施工提供首批 66 张表登记清单 |
| 2026-08-10 | 0.2.0 | 大改：补代码层第三层扫描 | **核心修正**：v0.1.0 仅扫 design_memos 误判"43 张闲置"。v0.2.0 新增 src/zephyr/ 代码层扫描后发现：(1) 表数 102 非 101（§4 合计算术错误修正）；(2) 真实利用率 97.1%（99/102）非 57.4%；(3) 真闲置仅 3 张（dividend_tax_node/index_meta/msci_adjustment）非 43 张；(4) ~41-61 张为"文档覆盖缺口"（代码在用但文档未覆盖，英文上界 61/含中文别名下界 ~41）；(5) P0 9 张表全部 CODE_ONLY 非闲置；(6) P4 生猪 3 张代码有 7-8 次引用非"完全不涉及"；(7) 热度前 15 数字全部修正；(8) data_asset_registry"首批 66 张"与 dataflow_graph_registry 现有 76 条矛盾，改为"以现有 76 条为 base 补 26 张"；(9) 三波施工从"接入闲置表"改为"补文档覆盖"；(10) §10 开放问题从 8 项精简为 5 项（业务边界项回归 90 号 §18 裁定）。维持 draft（需大改）。全网搜索验证：[thedataops.org 2026](https://www.thedataops.org/data-documentation/) 文档覆盖率 80% 基准、[Oxford 2026](https://www.tandfonline.com/doi/pdf/10.1080/14697688.2026.2659195) 宏观 regime 增量、[2026 ETF 套利实证](https://post.m.smzdm.com/p/a6zq30nz/) 散户套利不现实、[forage.ai 2026](https://forage.ai/blog/alternative-data-for-hedge-funds/) alt data 用法优先于拥有、[block trade 2026](https://equity-insider.com/behind-the-big-moves-how-block-trade-alerts-are-reshaping-equity-markets/) 大宗信号验证 |
| 2026-08-10 | 0.3.0 | 流程与算法增强：补评分模型+验收闭环+生命周期 | **施工环节补强**：(1) §3.4 新增 extract/trace 循环（[OpenSpec #739 2026-02](https://github.com/Fission-AI/OpenSpec/discussions/739)）将一次性扫描升级为可重复持续校验 + CI 门禁 warn（[codex 2026-05](https://codex.danielvaughan.com/2026/05/16/codex-cli-automated-code-documentation-generation-docstrings-jsdoc-sphinx-ci-pipelines/)）+ 文档腐烂三分类（引用漂移/结构衰变/概念过时，[codex 2026-04](https://codex.danielvaughan.com/2026/04/26/codex-cli-doc-rot-detection-automated-documentation-repair/)）；(2) §6.0 新增 Impact-Effort 优先级评分公式（[codedebtcost 2026-03](https://codedebtcost.com/prioritize)），量化替代定性 A→B→C→D 分批，权重 W2=5.0 体现风险优先原则；(3) §6.1 引入 4 阶段生命周期 ACTIVE→DEPRECATED→SUNSET→REMOVED（[oneuptime 2026-01](https://oneuptime.com/blog/post/2026-01-30-mlops-feature-versioning/view) + [Databricks Unity Catalog 2026](https://learn.microsoft.com/zh-cn/azure/databricks/data-governance/unity-catalog/certify-deprecate-data)）+ 数据弃用 7 步流程（[atlan 2026-03](https://atlan.com/know/data-deprecation-process/)）替代二元"归档/保留"；(4) §7.0 新增验收闭环（机器可查的单表验收标准 + 覆盖率目标轨迹 37.3%→46%→70%→97%）；(5) §9 补 3 项不做什么（不引入外部数据目录/不用 AST 分类/不 CI 阻断）；(6) §10 补 Q6（pre-commit warn）。维持 draft（施工流程已完整但待执行验证） |
| 2026-08-10 | 0.4.0 | 算法精度增强：RICE 置信度+语义抽检+权重校准 | **评分与验收精度补强**：(1) §6.0 评分公式从 `impact/effort` 升级为 RICE 变体 `(impact×confidence)/effort`（[bixtech.ai 2026-04](https://bixtech.ai/how-to-prioritize-data-projects-with-limited-resources-without-slowing-the-business-down/)），补入 Confidence 因子（1.0/0.8/0.5）对应代码引用性质不确定性——`hog_futures_core` 因置信度 0.5 从批次 B 降到 D，验证了 Confidence 对"模板继承"的降权效果；(2) §6.0 新增权重校准循环（[sigos.io 2026-06](https://www.sigos.io/blog/weighted-scoring-model)），每波施工后对比高低分表实际价值调整权重，避免静态模型失真；(3) §7.0 验收标准从 2 层升级为 3 层（L1 存在性/L2 消费关系/L3 语义一致），L3 语义抽检参考 [DocPrism ISSTA 2026](https://arxiv.org/pdf/2511.00215) 的"Schema presence != behavior parity"发现——11% 代码-文档对存在语义不一致，L3 抽检是防"假覆盖"最后防线；(4) §3.3 补 2 项审查局限（存在性≠行为一致性 + sub-agent 假阳性风险，[GitHub #53994 2026-04](https://github.com/anthropics/claude-code/issues/53994)）。维持 draft（算法已完整但待执行验证） |
| 2026-08-10 | 0.5.0 | 施工算法补齐：5 子节+Confidence 自动判定+WSJF 对比+归档指引 | **施工环节流程算法补齐**（回应"施工环节流程算法有缺失"审查）：(1) §3.5 新增 Confidence 因子自动判定算法——5 级正则优先级（SQL 查询=1.0 / import 注册=0.5 / 配置字面量=0.8 / 注释=0.5 / 仅文件名=0.3），将人工标注降级为异常复核，解决 61 张缺口表逐张标注成本问题；(2) §6.0 补 WSJF 对比 + 可选混合模型（time_criticality_factor）——验证个人项目不采纳 WSJF 的 Time Criticality（退化为风险优先已由 W2=5.0 覆盖）；(3) §6.2 批次 A 补 2026-08 最新实证（[华泰睿思 2026-06](https://finance.sina.com.cn/stock/hkstock/hkstockresearch/2026-06-02/doc-inhzyhiv4725438.shtml) 解禁 7 因子分层 Q1 胜率 72.5%/[Alphanume 2026-03](https://www.alphanume.com/blog/quantifying-lock-up-overhang) Overhang 4 指标/[Oxford 2026](https://www.tandfonline.com/doi/pdf/10.1080/14697688.2026.2659195) FRED-MD regime/[华福金工 2026-07](https://finance.sina.com.cn/wm/2026-07-11/doc-inihmzut8138715.shtml) 五维宏观 HP 滤波）；(4) §7.0 补 5 个施工算法子节：§7.0.1 per-table 模板（参考 [RepoDoc arXiv 2604.26523 2026-04](https://arxiv.org/html/2604.26523v1) API Coverage 5 维）/§7.0.2 代码反推（grep+上下文提取）/§7.0.3 表间依赖拓扑排序（Kahn 算法）/§7.0.4 Q score 质量度量（参考 [DataQ](https://publicationslist.org/data/jorge-martinez-gil/ref-175/dataq.pdf) 4 维 + [sustainablecatalyst 2026-06](https://sustainablecatalyst.com/documentation-model-cards-and-datasheets-for-algorithms/)）/§7.0.5 增量更新（RepoDoc semantic impact propagation）；(5) §7.5 新增归档操作位置指引（5 层分层：design_memos→data_asset_registry→采集脚本→tasks.yaml→ClickHouse）+ `dividend_tax_node` 归档路径示例；(6) §9 补 5 项不做什么（不用 WSJF/RepoKG/DataQ 全量/不用 AST/不自动生成文档）；(7) §10 Q2 从待人决策移至 AI 已裁定（批次+priority+拓扑排序三者正交可叠加），Q3 默认建议补入 §3.5 Confidence 自动判定替代人工核实。维持 draft（施工算法已完整但待执行验证） |
| 2026-08-10 | 0.6.0 | 优先级模型增强：Kano 分类层+指数衰减新鲜度+回滚机制+努力度 Rubric | **优先级与质量度量精度补强**（回应"选项之外更好的答案算法"审查）：(1) §6.0 新增 Kano 分类层（基本型/期望型/兴奋型/无差异型/反向型）作为 RICE 前置过滤器——基本型（risk_module_flag=Y）无论 RICE 分多少必须补文档，补 RICE 的"需求类型盲点"（[getperspective.ai 2026-05](https://getperspective.ai/blog/feature-prioritization-framework-using-ai-customer-research-to-rank-the-roadmap) / [m.zpedu.com 2026-07](https://m.zpedu.com/it/cpsj/39917.html) / [tempo.io 2026](https://www.tempo.io/guides/product-prioritization-techniques-product-managers) Kano+RICE 组合策略）；(2) §6.0 新增 Confidence 滥用警告（[rightfeature.com 2026-02](https://rightfeature.com/blog/rice-scoring-model/) "Subjectivity creeps in quickly"）+ 分布审计机制（>70% 同分触发警告）；(3) §7.0.4 timeliness 从二元（同步/未同步）升级为**指数衰减新鲜度**——`freshness_score = α × semantic_alignment + (1-α) × time_decay`，`time_decay = 2^(-age_days / half_life_days)`，half_life=30 天（[guiguio 2026-05](https://web-guiguio.b-cdn.net/blog/2026-05-07-stale-docs-confident-wrong-answers-rag-knowledge-base) + [happysupport.ai 2026-05](https://happysupport.ai/blog/llm-knowledge-base-freshness-scoring) + [WikiMonitor-onto JAAI 2026](https://www.jaai.net/vol4/JAAI-V4N3-66.pdf) "昨天编辑的文档也可能结构上过时"）；(4) §7.0.2 新增多消费方冲突解决算法（P0-P4 优先级裁定 + ⚠️ 双语义标注，不强制统一）；(5) §7.0.5 强化 Embedded Freshness 模式（git hook 触发 + §7.0.4 timeliness 闭环对接）；(6) §7.0.6 验收闭环补 Kano 分类校验 + 回滚就绪检查 + Confidence/effort 分布审计；(7) §7.0.7 新增施工回滚机制（L1-L4 四级回滚 + git revert + 5 Why 根因分析）；(8) §7.0.8 新增努力度估算 Rubric（doc_complexity 1-5 + cross_module_coupling 1-3 量化标准）；(9) §3.4 补 6 轴审查方法远期升级路径（[K-AI 2026-05](https://www.k-ai.ai/en/news/auditer-corpus-documentaire-ia-methode-6-axes/)，已覆盖 4 轴）；(10) §9 补 4 项不做什么（不用 Kano 完整问卷/不用 6 轴全量/不强制统一多消费方语义/不用 git reset --hard）。维持 draft（算法已完整但待执行验证） |
| 2026-08-10 | 0.7.0 | 算法对比增强：Milvus 乘法模型+DocAgent 多智能体+Consequence Ranking 批判+REFORGE 漏斗+CoDe-R 双路径 | **2026-08 最新研究算法对比与补强**（回应"全网搜索最新的 2026 年 8 月今天的最新研究实践算法"审查）：(1) §7.0.4 补 Milvus 2.6 Time-aware Ranking 的**乘法模型**（`final_score = similarity × decay_score`）作为当前加法模型的对比备选 + 高斯衰减备选 + [Temporal RAG arXiv 2509.19376v2 2026-06](https://arxiv.org/html/2509.19376v2) 参数敏感性警告（"freshness is real but partial and parameter-sensitive, not solved"）；(2) §7.0.2 补 [DocAgent arXiv 2504.08725v3 Meta AI 2025-05](https://arxiv.org/html/2504.08725v3/) 多智能体文档生成（Reader/Searcher/Writer/Verifier/Orchestrator + 拓扑处理顺序）作为远期升级路径——当前 §7.0.2 单 pass grep 是 lightweight 替代；(3) §6.0 补 [dualoop.coach 2026-03](https://www.dualoop.coach/blog/rice-vs-ice-vs-moscow-prioritization/) 的 Consequence Ranking 批判（"Non-commensurable variables" / "Confidence collapses domains"）+ 辩护（个人项目 §6.0 的 impact/effort 已归一化为无量纲分，非"apples × orchards"）；(4) §3.5 补 [REFORGE 2026-07](https://ubos.tech/reforge-a-method-for-benchmarking-llms-reverse-engineering-capabilities-in-decompiled-binary-function-naming/) 8 门置信度漏斗（8-gate confidence funnel 分 high/medium/low 三档 + 溯源链）作为远期升级——当前 5 级正则已够；(5) §7.0.7 补 [CoDe-R arXiv 2604.12913v2 2026-06](https://arxiv.org/html/2604.12913v2) Dynamic Dual-Path Fallback（DDPF 双路径回退）概念——回滚时可走"语义恢复路径"vs"语法稳定路径"。维持 draft（算法对比已完整但待执行验证） |
| 2026-08-10 | 0.8.0 | 语义验证+消费监控增强：Cascade 双重条件+消费链路主动监控+字段级血缘排除 | **自动化语义验证与消费链路管理补强**（回应"施工环节流程算法有缺失需要补充"+"2026 年 8 月最新研究"审查）：(1) §7.0.6 补 [Cascade arXiv 2604.19400v1 FSE 2026 July](https://arxiv.org/pdf/2604.19400v1) 双重条件自动化不一致检测——从文档生成测试+代码，仅当"代码测试失败 AND 文档生成代码测试通过"双重条件满足才报告不一致（71 不一致+814 一致对评估，发现 13 个未知不一致，10 个已修复）。补入 L3 人工抽检的远期自动化升级路径——与 DocAgent 互补（DocAgent 施工阶段 pre-shipment 验证 vs Cascade 运维阶段 post-shipment 验证），远期 100+ 篇文档或抽检不一致率 >15% 时引入。双重条件思想已简化融入 L3 抽检（先验文档自洽再验代码一致）；(2) §6.1 补 [simor consulting 2026-04](https://simorconsulting.com/blog/the-data-pipeline-that-cost-50kmonth--and-the-audit-that-found-why) 消费链路主动监控——金融数据平台审计发现 31% 计算花在零消费者管道，根因是"跟踪任务依赖但未跟踪消费依赖"。补入"ClickHouse query_log + tasks.yaml 每周扫描→30 天零查询自动标 ⚠️ 疑似闲置"主动监控规则，替代当前被动式"标 DEPRECATED→等 1 季度"。与 §7.0.4 timeliness half_life=30 天联动（30 天零查询→timeliness 下降+主动标记双重信号）。不采纳 simor"60 天自动暂停"（金融数据风险过高），保留人工确认 SUNSET→REMOVED；(3) §9 补 2 项不做什么（不采纳 Cascade 当前实现/不采纳字段级血缘——Databricks 列级血缘需 Apache Calcite+Neo4j 过重，§7.0.3 表级 Kahn 拓扑排序已够）；(4) 补 [CSDN 2026-06](https://blog.csdn.net/FastProceed/article/details/160023423) 5 层语义对齐校验作为远期参考（AST+LLM 双模态+KL 散度+运行时契约，比 Cascade 更重，当前不采纳）。维持 draft（语义验证+消费监控算法已完整但待执行验证） |
| 2026-08-10 | 0.9.0 | 新鲜度+增量更新+批次验证+漂移检测增强：Syntropy 编码会话级+Doc-Entropy Ratio+DocPilot 两 pass+Louvain 社区发现+Preventive/Detective 双层 | **文档新鲜度精度与漂移检测维度补强**（回应"2026 年 8 月 8 日最新研究实践算法"+"施工环节流程算法有缺失"审查）：(1) §7.0.4 补 [Syntropy 2025-12](https://github.com/delorenj/syntropy) 编码会话级新鲜度——当前 time_decay 纯时间驱动存在假阴性（代码 90 天未改但 time_decay=0.125 触发不必要的⚠️），补入 `session_factor`（code_sessions_since_sync=0→1.0 不衰减 / 1-3→0.9 / 4-10→0.7 / >10→0.5）作为 time_decay 修正因子。双因子乘法（time_decay × session_factor）兼顾"代码稳定时的假阴性"与"外部环境漂移的假阳性"；(2) §7.0.4 补 [SITS2026 香农-组织信息论 2026-04](https://blog.csdn.net/LogicShoal/article/details/160023770) Doc-Entropy Ratio = avg_lag_days / reference_count_30d——将"新鲜度"与"使用频率"复合（零引用表的 doc_entropy_ratio=0 无影响，高引用表的高 ratio 影响大）。SITS2026 行业基准：AI-Native Startup=0.14 / Legacy Enterprise=4.62 / Pre-AI=12.8。作为 Q score timeliness 的补充指标，暂不融入 RICE 公式（避免过度复杂化）；(3) §7.0.5 补 [DocPilot 2026](https://github.com/wyattstanson/docpilot) 两 pass 质量门+置信度路由——Pass 1 staleness_checker（LLM 验证文档是否真过时+confidence）/ Pass 2 repair_engine（LLM 重写+二次校验）/ 置信度路由（≥0.9 auto-fix / 0.6-0.9 draft / <0.6 flag）。吸收 Pass 1 false-positive filter 融入 §7.0.5 步骤 2.5（git diff ±行是否含表名字段名 AND 变更行是否在 SQL/数据加载函数内→true positive，否则跳过）。不采纳 auto-fix（金融文档风险过高，§9 已记录）。与 Cascade 双重条件互补（Cascade 管验收一致性，DocPilot 管更新必要性）；(4) §7.0.3 补 [社区发现算法 2026-08](https://blog.csdn.net/agito_cheung/article/details/148170240) + [calmops.com 2026-03](https://calmops.com/algorithms/community-detection-algorithms/) Louvain 社区发现——从依赖图自动发现紧耦合表簇（指数族/板块族/ETF 族等），作为 §6.2 人工批次的**验证工具**（不替代——业务优先级语义社区发现不含）。5 种算法对比选 Louvain（O(n·log²n) 高效、无需预设社区数、模块度优化），Leiden 备选。封装 `scripts/community_detection.py` 输出 `community_map.csv` 与 `topo_order.csv` 交叉验证批次边界；(5) §3.4 补 [hassette #634 2026-04](https://github.com/NodeJSmith/hassette/issues/634) Preventive vs Detective 双层检测——Preventive（CI 时阻止坏 PR，已覆盖）vs Detective（PR 间定期扫描累积漂移，未覆盖）。补入 Detective 扫描规则（路径完整性/表名一致性/命令有效性/交叉引用完整性 4 类检查）融入 §3.4 extract/trace 循环，选 Option C Hybrid（确定性检查用 PowerShell 脚本 + 语义检查用 L3 人工抽检）。与 extract/trace 循环互补（事件驱动 vs 时间驱动）；(6) §9 补 3 项不做什么（不用 Louvain 替代人工批次/不采纳 DocPilot auto-fix/不用 Detective Option A agent）。维持 draft（新鲜度+增量更新+批次验证+漂移检测算法已完整但待执行验证） |
| 2026-08-10 | 1.0.0 | 趋势分析+关键路径+权重形式化+差异化弃用：SPC EWMA/CUSUM+CPM+贝叶斯+有赞调度感知 | **质量度量趋势分析与施工调度精度补强**（回应"施工环节流程算法有缺失"+"2026 年 8 月今天最新研究实践算法"+"有没有更好的答案算法"审查）：(1) §7.0.4 补 [AIAG-VDA SPC Manual 2026 July](https://leoardent.com/2026/07/what-is-new-in-the-aiag-vda-spc-manual-key-changes-explained/) 的 **EWMA（指数加权移动平均）+ CUSUM（累积和）控制图**——当前 Q score 是点态测量（每波施工后评分 ≥7.0 判达标），无法检测渐进式质量退化（Q 从 9.0→8.5→8.0→7.5→7.1 连续 5 波下降但每波都"达标"）。补入 EWMA（λ=0.2 平滑系数，检测渐进漂移）+ CUSUM（k=0.5σ 参考值+h=4σ 决策阈值，检测小幅持续偏低）+ Shewhart（已有 Q<4.0 返工）三图联用 + AIAG-VDA 2026 四模型分类（理想/变异变化/磨损型/混沌型）。EWMA 主选（design_memos 更可能缓慢退化非突变），CUSUM 补充（达标线附近波动）。封装 `scripts/quality_spc.py`（需 scipy.stats）输出 `quality_spc.csv`；(2) §7.0.3 补 [CPM 关键路径法 2026](https://symplprocess.com/learn/critical-path-method)——Kahn 拓扑排序保证"被依赖表先补"但不识别关键路径（零时差表延误则全批延期）。补入前推（ES/EF）+ 后推（LS/LF）+ 总时差（TF=LS-ES）计算，TF=0 的表为关键路径优先保障。与 Kahn（顺序）+ Louvain（社区）构成施工调度三件套。输出 `critical_path.csv`。不过度依赖——102 表依赖链浅（4-5 层），CPM 主要价值在"避免在非关键表耗时导致关键表来不及"；(3) §6.0 补 [Bayesian Prioritization 2026](https://discovery.researcher.life/article/bayesian-prioritization-in-product-strategy-embedding-predictive-analytics-into-agile-decision-making/c78a7b57c8ce3a1cb50c3266abaefa9f) 贝叶斯权重更新形式化——当前权重校准循环是经验式启发式（"若高分表未明显优于低分表则降 W2"），补入 P(W\|E)=P(E\|W)×P(W)/P(E) 公式 + 触发条件（偏差连续 2 波超 2σ 才更新，避免频繁抖动）。仅形式化定义不全量实施 MCMC（102 表×5 权重后验计算量过重），贝叶斯作为理论依据证明启发式合理性。与 §7.0.4 EWMA 联动（EWMA 偏离预期→触发贝叶斯更新）；(4) §6.1 补 [有赞无用数据下线自动化 2026-08-07](https://blog.csdn.net/SunnyYoona/article/details/130119357) 调度感知差异化弃用阈值——当前"30 天零查询"统一阈值对月级/季级表是假阳性源（月级表 30 天才调度一次）。补入按调度级别差异化 lookback（日级 15 天/周级 6 周/月级 3 月/季级 6 月/事件触发按事件周期）+ [Databricks 2026-06](https://www.databricksters.com/p/reclaim-spend-from-idle-databricks) MIN_AGE_DAYS=30 安全过滤（新建表 30 天内不判定闲置）+ PROTECTED_TABLES 白名单（Kano 基本型风险红线表豁免，dormant≠idle）。不采纳有赞自动下线（金融数据风险过高，保留人工确认）；(5) §9 补 3 项不做什么（不只用 Shewhart 单点/不过度依赖 CPM 小网络/不做完整贝叶斯 MCMC）。全网搜索验证：[Qualytics 2026](https://userguide.qualytics.io/quality-scores/what-are-quality-scores/) historical daily scores 时间序列验证 SPC 方向正确、[productzip 2026-05](https://productzip.com/blog/rice-prioritization-for-product-portfolio-decisions) RICE+WSJF 互补确认不采纳 WSJF 合理、[tempo.io 2026](https://www.tempo.io/guides/how-to-avoid-common-product-backlog-prioritization-pitfalls) Kano+RICE 组合确认 §6.0 选型、[nemorize 2026-07](https://nemorize.com/roadmaps/2026-modern-ai-search-rag-roadmap/lessons/data-freshness-lifecycle) Sliding window TTL 验证 freshness 衰减方向、[OpenMetadata #27676 2026-04](https://github.com/open-metadata/OpenMetadata/issues/27676) zombie table FinOps agent 验证主动监控方向。维持 draft（趋势分析+关键路径+权重形式化+差异化弃用算法已完整但待执行验证） |
| 2026-08-10 | 1.1.0 | 矛盾修复+施工算法闭环：effort 校准+L3 主动学习抽样+SPC 冷启动+跨波次重评 | **内部矛盾修复与施工算法闭环补强**（回应"施工环节流程算法有缺失"+"2026 年 8 月今天最新研究实践算法"+"有没有更好的答案算法"+"文档结构内容有没有需要调整"审查）：(1) §6.0 示例表 effort 值与 §7.0.8 Rubric 矛盾修复——v0.4.0 示例表 effort 值（5/7.5/4/5/2.5）为估算值，与 v0.6.0 Rubric 量化标准不一致。v1.1.0 以 Rubric 为准重新计算（`restricted_shares` effort 5→7.0 / `cb_iv` effort 5→8.0 / `hog_futures_core` effort 2.5→3.5），priority 相应调整。批次归属不变（Kano 基本型 + 业务归集优先于 RICE 排序）。§7.0.8 "与 §6.0 的对接"段同步更新（"略有差异"→"已完全一致"）；(2) §7.0.6 补 [Smart Active Sampling arXiv 2209.11464](https://arxiv.org/pdf/2209.11464.pdf) + [AI 主动学习标注质量动态校验 2026-03 专利](https://www.xjishu.com/zhuanli/55/202511942856.html) + [ISO 2859-1:2026](https://www.iso.org/cms/render/live/en/sites/isoorg/contents/data/standard/08/54/85464.html) AQL skip-lot 的 **L3 主动学习分层抽样策略**——替代纯随机"每批次抽 2 张"，用 §3.5 Confidence（不确定层必抽）+ §6.0 Kano 基本型（高风险层必抽）+ 随机层补抽的三层抽样。skip-lot 规则（连续 3 波全过→降频 / 发现不一致→升频+社区全量复查 / 信任名单暂免）；(3) §7.0.4 补 **SPC 冷启动三阶段处理**——EWMA/CUSUM 需 ≥5 数据点建立控制限，但第一波施工前无历史数据。补入冷启动期（1-2 波，仅 Shewhart）/ 预热期（3-4 波，EWMA 宽松限）/ 稳态期（5 波+，全功能）三阶段 + 冷启动期"相邻波次 Q score 差值>2.0 标⚠️异常波动"替代趋势监控；(4) §6.0 补 **跨波次优先级动态重评算法**——闭合"证据→权重→priority→批次"反馈环：每波收集 Q score/L3 通过率/effort 偏差/CPM 耗时偏差 → 触发贝叶斯权重微调（W2 上调 0.5 / W1 下调 0.2）→ 批次归属动态调整建议（期望型↔兴奋型互转，基本型不降级）→ 下波 priority 重算输出 `priority_v{n+1}.csv`。不自动执行（仅建议），不回溯已施工表；(5) §9 补 2 项不做什么（不用纯主动学习模型替代分层抽样 / 不用 Pareto 前沿替代 RICE 排序——[asi-build GoalPrioritizer 2026-04](https://github.com/web3guru888/asi-build/wiki/Phase-30-Goal-Prioritizer) + [pymoo NSGA-II 2026-08](https://blog.csdn.net/gitblog_00365/article/details/152063163) 在 102 表规模信息密度过高）。全网搜索验证：[Amazon Quick Agentic Catalog 2026-08-01](https://aws-news.com/article/2026-07-31-announcing-the-agentic-catalog-experience-in-amazon-quick) 验证 §7.0.3 表间依赖拓扑排序方向正确、[Transwarp Catalog 2026-06](https://www.transwarp.cn/bd/6236) 验证 AI 元数据自动化方向但不采纳（企业级过重）。维持 draft（矛盾已修复+算法闭环已完整但待执行验证） |
| 2026-08-10 | 1.2.0 | 漂移来源分类+Shewhart 模式识别+故障归因：Model drift+Western Electric+Innovation-Residual | **漂移来源分类与故障归因精度补强**（回应"施工环节流程算法有缺失"+"2026 年 8 月今天最新研究实践算法"+"有没有更好的答案算法"+"文档结构内容有没有需要调整"审查）：(1) §3.4 补 [sincllm.com 2026-06 AI Drift Detection](https://sincllm.com/blog/ai-drift-detection-production-model-output-degradation) 的 **Model drift 漂移来源分类**——§3.4 原"文档腐烂三类"（引用漂移/结构衰变/概念过时）按**腐烂机制**分类，但未区分**漂移来源**。补入 Data Drift（输入分布变化→代码引用表名分布变化，自动化检测）/ Concept Drift（正确输出定义变化→消费语义变化，人工 L3 抽检）/ Model Drift（权重静默更新，本审查不适用）三类，并与"腐烂机制"做正交交叉矩阵（来源×机制），明确每类漂移的检测方法与责任归属。不新增独立检测流程，仅补充分类视角让现有 Detective 扫描+L3 抽检的责任归属更清晰；(2) §7.0.4 补 [CONTINUUM 2026](https://github.com/HarshTomar1234/continuum) + [NIST Engineering Statistics Handbook](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc32.htm) 的 **Western Electric 规则 8 异常模式**——§7.0.4 SPC 三图联用（Shewhart+EWMA+CUSUM）覆盖单点越界/渐进漂移/小幅持续偏低，但 Shewhart 控制图本身还有"非随机模式"未利用。补入 8 种异常模式（Rule 1 单点 3σ 越界 / Rule 2 9 点单侧 / Rule 3 6 点连续升降 / Rule 4 14 点交替 / Rule 5 3 点中 2 点超 2σ / Rule 6 5 点中 4 点超 1σ / Rule 7 15 点在 1σ 内 / Rule 8 8 点在 1σ 外），作为 Shewhart 后处理步骤，封装进同一 `scripts/quality_spc.py`，输出 `quality_spc.csv` 新增 `we_rule` 列。与 EWMA/CUSUM 分工明确（Rule 4-8 是 Western Electric 独有，EWMA/CUSUM 不覆盖）。Rule 2-8 需稳态期（≥10 数据点）才启用，与 §7.0.4 SPC 冷启动对齐；(3) §7.0.7 补 [Innovation-Residual Auditing arXiv 2608.05490v1 2026-08-06](https://arxiv.org/html/2608.05490v1) 的 **故障归因算法+Detection Limit**——§7.0.7 回滚根因分析用"5 Why"人工追问，能定位"哪张表文档有问题"但难定位"哪个具体操作步骤引入错误"。补入创新残差思想：收集成功施工轨迹→统计操作位置分布→对故障表计算残差=1-P(实际操作|位置)→残差最大且超 2σ_innovation 检测限的操作为故障源。简化版用频率统计替代预测模型（个人项目数据量不足以训练 n-gram/Markov 模型），Detection Limit（2σ_innovation）过滤正常波动减少误报。与 §7.0.7 回滚分级对接（L1 单表归因故障操作 / L2 批次共因排查 / L3-L4 无意义走 Path 2 重建）；(4) §9 补 2 项不做什么（不全面实施 Innovation-Residual 审计——预测模型训练成本过高，仅借鉴残差思想用频率统计 / 不引入 DoWhy 因果推断——L3 抽检样本量不足无法支撑反事实对照实验，Innovation-Residual 是相关性归因非因果归因，对定位故障步骤已足够）。全网搜索验证：[sincllm.com 2026-06](https://sincllm.com/blog/ai-drift-detection-production-model-output-degradation) 验证漂移来源分类方向、[CONTINUUM 2026](https://github.com/HarshTomar1234/continuum) 验证 Western Electric 规则在 SPC 中的标准地位、[NIST Handbook](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc32.htm) 提供 8 规则的权威定义、[arXiv 2608.05490v1 2026-08-06](https://arxiv.org/html/2608.05490v1) 验证 Innovation-Residual 故障归因方法的学术有效性。维持 draft（漂移来源分类+Shewhart 模式识别+故障归因算法已完整但待执行验证） |
| 2026-08-10 | 1.3.0 | 名称修正+进度看板+符号漂移检测：Nelson Rules 修正+施工进度 CSV 看板+symbol-level drift+Hotelling T² 远期 | **施工流程闭环补强与准确性修正**（回应"施工环节流程算法有缺失"+"2026 年 8 月今天最新研究实践算法"+"有没有更好的答案算法"+"文档结构内容有没有需要调整"审查）：(1) §7.0.4 **Nelson Rules 名称修正**——v1.2.0 标题用"Western Electric 规则"但 Rule 2 判异条件用"9 点连续在中心线一侧"，这实际是 [Nelson Rules 1984 Lloyd S. Nelson](https://metricgate.com/docs/nelson-rules-control-chart/) 的标准，而非 Western Electric 原始标准（1956 的 7-8 点）。[ppapdocuments.com 2026-07](https://ppapdocuments.com/2026/07/10/how-to-read-a-control-chart-out-of-control-signals-and-the-western-electric-rules/) + [DolphinDB SPC 实战 2026-08-09](https://blog.csdn.net/sinat_41617212/article/details/163544780) 显示现代实践两者融合但"9 点"来自 Nelson。v1.3.0 修正标题为"Western Electric / Nelson 规则"并明确采用 Nelson 的"9 点"标准（更保守，假阳性更低）；(2) §7.0 新增 **§7.0.9 施工进度跟踪看板**——§7.0.1-§7.0.8 定义了"怎么做"但未定义"做到哪了"。参考 [docsie.io Documentation Sprint 2026](https://www.docsie.io/blog/glossary/documentation-sprint/) + [projectmanagementformula.com Kanban 2026-04](https://projectmanagementformula.com/how-to-set-up-a-kanban-complete/) 补入轻量级 CSV 看板（6 状态：Backlog/In Progress/In Review/Done/Rolled-back/Deferred + WIP 限制 In Progress≤3/In Review≤5）。用 CSV 矩阵而非电子看板工具（对齐 §9 docs-as-code 原则），由 `audit_data_utilization.ps1` 自动推断状态（git log + 文档存在性 + 验收记录）。与 §6.0 跨波次重评 + §7.0.7 回滚分级对接；(3) §3.4 Detective 扫描补 **第 5 类检查：代码符号漂移检测**（参考 [dosu.dev 2026-05 freshness scoring](https://dosu.dev/blog/score-documentation-freshness-in-ci)）——原 4 类检查（路径/表名/命令/交叉引用）未覆盖"文档引用的 def/class/function 符号是否仍存在于代码中"。dosu.dev 引用 Empirical Software Engineering 2024 研究：28.9% GitHub 仓库文档引用了已不存在的代码符号，平均过期 4.7 年。补入 grep 文档中 `def xxx`/`class Xxx` → 验证 src/zephyr/ 中是否仍存在，严重度定为"高"；(4) §7.0.4 记录 **Hotelling T² 多变量 SPC 远期升级路径**（参考 [Knop 2026 Integrating Classical and Advanced SPC Tools](https://reference-global.com/download/article/10.2478/mspe-2026-0030.pdf)）——当前 SPC 是单变量（Q score 综合分），T² 可监控四维度（completeness/accuracy/specificity/timeliness）联合分布。当前不引入（Q score 加权模型已够 + 数据量不足 ≥20 波 + 实现复杂度高），远期"加权后达标但单维度持续退化"假阴性出现时再引入；(5) §9 补 2 项不做什么（不引入完整 FMEA RPN——Severity/Occurrence/Detection 三要素已由 Kano+Rubric+Confidence 分散覆盖，102 表×3 维度×1-10 分=3060 次评分过重 / 不引入 Staleguard/knowledge-diff 外部漂移检测工具——PowerShell 5 类检查已够，外部工具违反派生产物不入 git 约束）。全网搜索验证：[metricgate.com 2026-05](https://metricgate.com/docs/nelson-rules-control-chart/) 验证 Nelson Rules 标准、[DolphinDB 2026-08-09](https://blog.csdn.net/sinat_41617212/article/details/163544780) 验证 SPC 实战方向、[dosu.dev 2026-05](https://dosu.dev/blog/score-documentation-freshness-in-ci) 验证 symbol-level drift 检测方向、[docsie.io 2026](https://www.docsie.io/blog/glossary/documentation-sprint/) 验证 Documentation Sprint Kanban 方向、[projectmanagementformula.com 2026-04](https://projectmanagementformula.com/how-to-set-up-a-kanban-complete/) 验证 WIP 限制实践、[Knop 2026](https://reference-global.com/download/article/10.2478/mspe-2026-0030.pdf) 验证 Hotelling T² 多变量 SPC 方向、[ASQ FMEA 2026](https://asq.org/quality-resources/fmea) 验证 FMEA RPN 选型排除合理、[Staleguard 2026-06](https://github.com/Arthur920/Staleguard) + [knowledge-diff 2026-05](https://github.com/oarisur/knowledge-diff) 验证外部工具选型排除合理。维持 draft（名称修正+进度看板+符号漂移检测算法已完整但待执行验证） |
| 2026-08-10 | 1.4.0 | SPC 误报率风险矩阵+自适应控制限+回滚效能度量：Nelson Rules 风险矩阵+AIAG 自适应 SPC+MTTD/MTTR | **SPC 精度补强与回滚效能度量闭环**（回应"施工环节流程算法有缺失"+"2026 年 8 月今天最新研究实践算法"+"有没有更好的答案算法"+"文档结构内容有没有需要调整"审查）：(1) §7.0.4 补 **Nelson Rules 误报率风险矩阵**——参考 [ifactoryapp 2026-06-25 Pharma SPC](https://ifactoryapp.com/blog/western-electric-nelson-rules-pharma) 警告：全部启用 8 条 Nelson 规则的误报率从单规则 0.27%（ARL~370）升到 1-2%（ARL~91，4 倍误报），"8-10 周内摧毁操作员信任"。v1.4.0 补入 risk-based subset selection——默认启用集（Rule 1/2/3/5，ARL~106）vs 诊断启用集（Rule 4/6/7/8，仅在 L3 发现异常时临时启用）。同时验证 v1.3.0 Nelson 修正准确性：[metricgate 2026-05-28](https://metricgate.com/docs/nelson-rules-qcc/) 确认 Nelson 是 Western Electric 超集（N1=WE1/N2=WE4/N5=WE2/N6=WE3），启用全部 8 条 Nelson 已自动覆盖全部 4 条 WE。修正 v1.2.0"稳态期全启用 Rule 1-8"为"稳态期按风险矩阵默认启用 Rule 1/2/3/5"；(2) §7.0.4 补 **自适应控制限思想**——参考 [AIAG SPC 3rd Edition 2026-07](https://ifactoryapp.com/industries/automotive-manufacturing/daptive-control-limits-automotive-stamping-quality-engineers-predictive-maintenance)（ifactoryapp 2026-06-03 报道）正式将"AI 增强自适应 SPC"纳入标准。静态控制限的三大缺陷：基线陈旧+误报膨胀（40-60%）/ 单变量盲区（T² 已在 v1.3.0 记录）/ 合规缺口。补入基线重算触发条件（§6.0 权重调整 / §7.0.7 L3-L4 回滚 / σ 持续增大 / 模板 Rubric 结构性修订），用最近 5 波数据重新拟合 μ_0/σ_EWMA。不引入 AI 增强（ML 根因识别+实时 Cpk+预测性维护对个人项目过重），仅借鉴"基线重算"低成本近似——离散自适应（触发时重算）而非连续自适应（AI 持续微调），与 §6.0 跨波次重评构成"优先级层面+质量度量层面"双层反馈环；(3) §7.0.9 补 **MTTD/MTTR 回滚效能度量**——参考 [uvik.net 2026-08-02 Data Quality KPIs](https://uvik.net/blog/data-quality-metrics-kpis/) 八 KPI 中的 MTTD（平均检测时间）和 MTTR（平均解决时间）。§7.0.7 回滚机制有 L1-L4 分级和 Innovation-Residual 归因（v1.2.0）但未度量检测/修复时间。补入 MTTD≤7 天（Detective 周级扫描+L3 每波抽检）/ MTTR≤14 天（L1 单表）/≤30 天（L2-L4 批次全波）目标，融入 `rollback_log.md` 时间戳采集。个人项目适配：不追求企业基准（MTTD≤4h/MTTR≤24h），以"波次"非"小时"为单位；积累 ≥5 次回滚事件后才计算均值（3 波施工回滚事件少）；与 §3.4 Detective 扫描频率联动（MTTD 持续超标→升频）；(4) §9 补 1 项不做什么（不引入 AI 增强自适应 SPC——ML 模型训练+实时数据流+CMMS 集成对个人项目过重，仅借鉴基线重算思想）。全网搜索验证：[ifactoryapp 2026-06-25](https://ifactoryapp.com/blog/western-electric-nelson-rules-pharma) 验证 Nelson Rules 误报率风险+ARL 数据、[metricgate 2026-05-28](https://metricgate.com/docs/nelson-rules-qcc/) 验证 Nelson=WE 超集关系、[AIAG SPC 3rd Edition 2026-07](https://ifactoryapp.com/industries/automotive-manufacturing/daptive-control-limits-automotive-stamping-quality-engineers-predictive-maintenance) 验证自适应 SPC 方向+静态限三大缺陷、[uvik.net 2026-08-02](https://uvik.net/blog/data-quality-metrics-kpis/) 验证 MTTD/MTTR KPI 方向+六维度质量框架、[中方科技 2026-04](https://www.midfun.com.tw/qc/spc-control-chart-types-selection-guide/) 验证 EWMA/CUSUM 选型方向、[chipfoundryservices 2026](https://www.chipfoundryservices.com/topics/capability) 验证 SPC 数学公式。维持 draft（SPC 误报率风险矩阵+自适应控制限+回滚效能度量算法已完整但待执行验证） |
| 2026-08-10 | 1.5.0 | 技术债视角+环检测+指标分类：SQALE TDR+Kahn 环检测+Leading/Lagging | **宏观债务视角与度量体系分类补强**（回应"施工环节流程算法有缺失"+"2026 年 8 月今天最新研究实践算法"+"有没有更好的答案算法"+"文档结构内容有没有需要调整"审查）：(1) §6.0 补 **SQALE 技术债视角**——参考 [technicaldebtcalculator.com 2026 SQALE Framework](https://technicaldebtcalculator.com/frameworks) + [CppDepend Smart Technical Debt Estimation](https://www.cppdepend.com/Doc/Smart_Technical_Debt_Estimation.pdf)。§6.0 RICE 评分回答"先补谁"但未回答"整体文档债务有多严重"。补入 TDR（Technical Debt Ratio）= 文档缺失表 effort / 全部表 effort × 100 的 A-E 评级（当前 TDR≈65% → E 级 Severe），Principal/Annual-Interest/Breaking-Point 概念映射（年利息用 Kano 分类代理：基本型=高利息/兴奋型=低利息），Martin Fowler Debt Quadrant 四象限映射（本审查无 Deliberate Reckless / Inadvertent Reckless）。SQALE 是宏观健康度补充视角不替代 RICE 微观排序，补入 RICE 缺失的"不补的代价"维度；(2) §7.0.3 补 **Kahn 环检测显式说明**——参考 [thecodeforge.io 2026-03 Topological Sort](https://thecodeforge.io/dsa/topological-sort/) 强调"always pair topological sort with cycle detection"。v0.5.0 补入 Kahn 算法时隐性依赖"DAG 必须无环"但未说明"检测到环后怎么处理"。补入步骤 5 环检测流程：检测（topo_order.csv 行数 < 节点数 → 有环）→ 定位（未处理节点为环内节点）→ 处理（记入 architecture_issue_registry.yaml ARCH 条目，人工裁定打破环）。额外输出 cycle_warning.csv；(3) §7.0.4 补 **Leading vs Lagging 指标区分**——参考 [affine.pro 2026-07-10 Knowledge Base Metrics](https://affine.pro/blog/knowledge-base-metrics) 区分 leading indicators（前瞻性）与 lagging indicators（回顾性）。补入分类矩阵：Lagging（Q score/L3 通过率/看板 Done 计数/SQALE TDR）vs Leading（Detective 扫描/SPC EWMA 趋势/Nelson Rules 模式/Model drift 数据漂移/贝叶斯权重偏差）。核心洞察："只有 lagging 无 leading→响应滞后，只有 leading 无 lagging→不知道当前状态"。与 MTTD/MTTR 联动（MTTD 短=leading 有效，MTTR 短=lagging 有效）；(4) §9 补 2 项不做什么（不引入 Ticket Deflection Rate 等 KB 消费效果指标——[finaldoc.io 2026-03-20](https://finaldoc.io/blog/5-metrics-documentation-teams) 5 项指标面向有搜索+ticket+帮助台的在线 KB，design_memos 是 git markdown 无这些基础设施，用"文档引用次数变化"代理 / 不引入 Financial Impact 技术债框架——[technicaldebtcalculator.com 2026](https://technicaldebtcalculator.com/frameworks) Financial Impact = team_size × loaded_salary × debt_time_fraction × age_multiplier 需团队工时成本，个人项目 1 人+AI 无薪酬成本）。全网搜索验证：[technicaldebtcalculator.com 2026](https://technicaldebtcalculator.com/frameworks) 验证 SQALE/TDR/Financial Impact 五框架对比方向、[CppDepend SQALE](https://www.cppdepend.com/Doc/Smart_Technical_Debt_Estimation.pdf) 验证 Annual-Interest + Breaking-Point 概念、[vidhyasagarthakur 2026-03](https://www.vidhyasagarthakur.engineer/blog/the-economics-of-technical-debt) 验证 Fowler Debt Quadrant 四象限、[thecodeforge.io 2026-03](https://thecodeforge.io/dsa/topological-sort/) 验证 Kahn 环检测方向、[affine.pro 2026-07-10](https://affine.pro/blog/knowledge-base-metrics) 验证 Leading/Lagging 指标分类方向、[finaldoc.io 2026-03-20](https://finaldoc.io/blog/5-metrics-documentation-teams) + [drexplain.com 2026-05-12](https://www.drexplain.com/press/articles/how_do_you_know_if_your_user_documentation_is_actually_working/) + [supportbench.com 2026-02-07](https://www.supportbench.com/knowledge-base-roi-b2b-deflection-assisted-resolution/) 验证 KB 消费效果指标选型排除合理。维持 draft（技术债视角+环检测+指标分类算法已完整但待执行验证） |
| 2026-08-10 | 1.6.0 | Leiden 升级+Cognitive/AI-Generated Debt+Binarly 再分配+paired-model：Louvain→Leiden+Cognitive Debt+AI-Generated Debt+Binarly 权重再分配+paired-model 双 LLM | **社区发现算法升级与 AI 生成债务新类别补强**（回应"施工环节流程算法有缺失"+"2026 年 8 月今天最新研究实践算法"+"有没有更好的答案算法"+"文档结构内容有没有需要调整"审查）：(1) §7.0.3 **Louvain→Leiden 升级**——[metricgate.com 2026-02-03](https://metricgate.com/blogs/community-detection-louvain-vs-leiden/) + [IJARCSE 2026](https://ijarcse.org/index.php/ijarcse/article/download/106/151/457) 确认 Leiden 修复 Louvain 两大 bug：分辨率限制（Louvain 倾向合并小社区为大社区）+ 断连社区（Louvain 产出的社区内部可能不连通）。Leiden 保证社区连通性 + γ 参数可调细粒度，2026 年已成行业共识。§9 同步更新"Louvain"→"Leiden"；(2) §6.0 补 **Cognitive Debt + AI-Generated Debt 新类别**——[Exceeds AI 2026-06-09](https://blog.exceeds.ai/ai-technical-debt-tracking-workflow/) + [dupple.com 2026-04-03](https://dupple.com/blog/what-is-technical-debt-in-software-development) 提出 Fowler 四象限之外的第五类 AI-Generated Debt（AI 生成的内容无人完全拥有/理解，无决策点）。本审查文档施工由 AI 执行（§7.0.2 代码反推+§7.0.1 模板套用）天然存在此风险。补入 AI-touched doc cycle time + Rework rate 度量指标；(3) §6.0 补 **Binarly 权重再分配算法**——[binarly.io 2026-04-13](https://www.binarly.io/blog/binarly-risk-score-introduction) 的 BRS 系统提出缺失 metric 的权重按预定义比例重新分配给其他 metric，避免缺失值导致评分失真。补入 RICE 分量缺失时的权重再分配规则（alpha 缺失→W3 按比例分配给 W1+W2 / code_ref 缺失→W1 按比例分配给 W2+W3），符合风险优先原则；(4) §3.4 补 **paired-model 双 LLM 交叉验证**远期路径——[arXiv 2608.03500v1 2026-08-04](https://arxiv.org/html/2608.03500v1) 提出 paired-model comparison（两独立 LLM 对同一文档-代码对做一致性判断，kappa=0.532，一致性 75.8%）。作为 §7.0.6 L3 人工抽检的远期自动化升级路径（远期 design_memos 100+ 篇或 L3 不一致率 >15% 时引入），当前不采纳（LLM 成本与 DocAgent/Cascade 同量级）。全网搜索验证：[metricgate.com 2026-02-03](https://metricgate.com/blogs/community-detection-louvain-vs-leiden/) + [IJARCSE 2026](https://ijarcse.org/index.php/ijarcse/article/download/106/151/457) 验证 Leiden 修复 Louvain bug、[Exceeds AI 2026-06-09](https://blog.exceeds.ai/ai-technical-debt-tracking-workflow/) 验证 Cognitive Debt + AI Debt Score 方向、[dupple.com 2026-04-03](https://dupple.com/blog/what-is-technical-debt-in-software-development) 验证 AI-Generated Debt 第五类、[binarly.io 2026-04-13](https://www.binarly.io/blog/binarly-risk-score-introduction) 验证权重再分配算法方向、[arXiv 2608.03500v1 2026-08-04](https://arxiv.org/html/2608.03500v1) 验证 paired-model kappa 数据。维持 draft（Leiden 升级+Cognitive/AI-Generated Debt+Binarly 再分配+paired-model 算法已完整但待执行验证） |
| 2026-08-10 | 1.7.0 | Temporal Coupling+Data Contract+SATD 传播+AI 技术债 7 类+Leiden 修正：Temporal Coupling 隐藏依赖+ODCS 概念重构+SATD 跨制品传播+AI 技术债 7 类映射+Leiden 选型结论修正 | **施工调度隐藏依赖检测与债务视角完整性补强**（回应"施工环节流程算法有缺失"+"2026 年 8 月今天最新研究实践算法"+"有没有更好的答案算法"+"文档结构内容有没有需要调整"+"持续改进不要停下来询问"审查）：(1) §7.0.3 补 **Temporal Coupling 隐藏依赖检测算法**——参考 [codebase-memory-mcp #928 2026-07-07](https://github.com/DeusData/codebase-memory-mcp/issues/928) 的 co_changed 时序耦合指标 + [iterathon.tech Repository Intelligence 2026-01](https://iterathon.tech/blog/repository-intelligence-ai-code-understanding-enterprise-2026) 的 Historical Context 维度。Kahn 拓扑排序依赖声明显式依赖，Leiden 社区发现依赖静态依赖图——两者都只看"代码里写了什么"。Temporal Coupling 通过 git log co-change 分析发现**动态隐藏依赖**（无 DDL 依赖但频繁在同一 commit 中修改的表对，如 dragon_tiger↔dragon_tiger_seat）。补入 Jaccard 时序耦合度算法（temporal_coupling(A,B) = co_occurrence / |commits(A)∪commits(B)|）+ 阈值 0.5 + 冷启动约束（commit<50 时不计算）。与 Kahn（顺序）+Leiden（静态社区）+CPM（工期）构成施工调度四件套。封装 `scripts/temporal_coupling.py` 输出 `hidden_dependency.csv`；(2) §2.2 补 **Data Contract ODCS 概念重构**——参考 [soda.io 2026-06-01](https://soda.io/blog/data-contracts-vs-schema-registry) + [datus.ai 2026-06-29](https://datus.ai/blog/what-is-data-contract/) + [streamkap.com 2026-02-25](https://streamkap.com/resources-and-guides/data-contracts-streaming)。用 2026 行业标准 Data Contract 概念重构"文档覆盖缺口"——Schema（结构，schemas/categories DDL 已完整 102/102）vs Data Contract（schema+语义+质量+SLA+所有权+变更管理六组件，当前仅 Schema 完整，Semantics 层 38-61/102 缺口）。补入 ODCS（Open Data Contract Standard，Linux Foundation Bitol）六组件完整度映射表。不引入 ODCS YAML 工具链（派生产物不入 git 约束），仅用概念重构理解 + §8 data_asset_registry 施工参照六组件完整性检查清单；(3) §6.0 补 **SATD 跨制品传播优先级**——参考 [arXiv 2603.15883v2 PEARC 2026 July](https://arxiv.org/html/2603.15883v2) Self-Admitted Technical Debt in Scientific Software。本审查的 §10 开放问题/§6.2 批次 D 暂缓/§9 不做什么本质都是 SATD。补入跨制品传播链长度（comment=1→commit=2→PR/issue=3→暂缓决策=4）作为 RICE confidence 调整因子 + 情感加权（负面×1.2）。不引入完整 SATD NLP 分类模型（数据量不足 ~50-100 条），用规则映射替代；(4) §6.0 补 **AI 技术债 7 类映射**——参考 [Institute of AI PM 2026-01-25](https://www.institutepm.com/knowledge-hub/ai-technical-debt-template) 的 7 类技术债（Data/Model/Pipeline/Monitoring/Testing/Documentation/Infrastructure）。映射验证本审查已覆盖 6 类（1/3/4/5/6/7），第 2 类 Model Debt 不适用（无 ML 模型）。无需新增独立债务类别，v1.5.0 SQALE+v1.6.0 Cognitive/AI-Generated+v1.7.0 SATD 传播已覆盖全部适用类别；(5) §7.0.3 **Leiden 选型结论修正**——v1.6.0 状态行提及"Leiden 替代 Louvain"但选型结论仍写"Louvain 算法"，v1.7.0 修正选型结论为"Leiden 算法"+ 应用标题+代码示例+§9 边界条目全部同步更新 Louvain→Leiden。全网搜索验证：[codebase-memory-mcp #928 2026-07-07](https://github.com/DeusData/codebase-memory-mcp/issues/928) 验证 co_changed 时序耦合指标+性能数据（cold ~58ms/warm ~24ms）、[iterathon.tech 2026-01](https://iterathon.tech/blog/repository-intelligence-ai-code-understanding-enterprise-2026) 验证 Repository Intelligence Historical Context 维度、[soda.io 2026-06](https://soda.io/blog/data-contracts-vs-schema-registry) 验证 Schema Registry vs Data Contract 区分、[datus.ai 2026-06-29](https://datus.ai/blog/what-is-data-contract/) 验证 ODCS 标准+机器可校验定义、[streamkap.com 2026-02-25](https://streamkap.com/resources-and-guides/data-contracts-streaming) 验证 Data Contract 六组件、[arXiv 2603.15883v2 PEARC 2026 July](https://arxiv.org/html/2603.15883v2) 验证 SATD 跨制品传播+情感放大+传播链长度与优先级正相关、[Institute of AI PM 2026-01-25](https://www.institutepm.com/knowledge-hub/ai-technical-debt-template) 验证 AI 技术债 7 类分类。维持 draft（Temporal Coupling+Data Contract+SATD 传播+AI 技术债 7 类映射+Leiden 修正算法已完整但待执行验证） |
| 2026-08-10 | 1.8.0 | Temporal Coupling 增强+确定性排序+环路径提取+predict Omissions+ODCS v3.1.0：commit-size 归一化+CodeScene 三信号+Sum of Coupling+min-heap Kahn+DFS 三色标记+Tarjan SCC 远期+predict Omissions schema↔doc 共变检测+ODCS v3.1.0 版本号+DCS 弃用说明 | **Temporal Coupling 精度增强与施工调度确定性补强**（回应"施工环节流程算法有缺失"+"2026 年 8月今天最新研究实践算法"+"有没有更好的答案算法"+"文档结构内容有没有需要调整"+"持续改进不要停下来询问"审查）：(1) §7.0.3 Temporal Coupling 补 **commit-size 归一化过滤**——参考 [Archy #131 2026-05-25](https://github.com/hslee16/Archy/issues/131) 明确指出"large commits couple everything"是 temporal coupling 的首要假阳性源。大 commit（初始化/批量重构/全仓格式化）同时触碰几十个文件污染 co-change 矩阵。补入 MAX_FILES_PER_COMMIT=15 过滤阈值（本仓库 102 表的 ~15%），超过此阈值的 commit 从 co_change 矩阵剔除，输出 filtered_commits.csv 供审计；(2) §7.0.3 Temporal Coupling 补 **CodeScene 三信号说明**——参考 [CodeScene 3.5.23 Temporal Coupling](https://docs.enterprise.codescene.io/versions/3.5.23/guides/technical/temporal-coupling.html) 明确三信号：(a) 同一 commit 修改、(b) 同一程序员时间段内修改、(c) commit message 同一 Ticket ID。本审查为个人+AI 项目（单一开发者），信号 (b) 无区分力、信号 (c) 无 ticket 系统——仅采用信号 (a) 同一 commit co-change 以 Jaccard 量化。信号 (b)/(c) 作为团队规模化后远期升级路径记录；(3) §7.0.3 Temporal Coupling 补 **Sum of Coupling 聚合度**——参考 [CodeScene Sum of Coupling](https://docs.enterprise.codescene.io/versions/3.5.23/guides/technical/temporal-coupling.html#dig-deeper-with-sum-of-coupling)。sum_of_coupling(A) = Σ temporal_coupling(A,B) for all B≠A。高 SoC 表是"枢纽表"施工时需优先关注（变更牵连多表文档同步），低 SoC 表是"孤岛表"可独立施工。输出 SoC 排序与 §5.2 热度分布交叉验证；(4) §7.0.3 Kahn 拓扑排序补 **min-heap 确定性打破平局**——参考 [spacecomplexity.ai 2026-05-24](https://spacecomplexity.ai/blog/topological-sort-algorithm)。Kahn 队列改为按 (priority DESC, table_name ASC) 排序的优先队列，确保同层同分表的施工顺序可复现（多次运行拓扑排序结果一致），避免"随机队列顺序导致施工计划不可复现"，O(V log V + E)；(5) §7.0.3 补 **DFS 三色标记环路径提取**——参考 [spacecomplexity.ai 2026-05-24](https://spacecomplexity.ai/blog/topological-sort-algorithm) + [quant67.com 2026-06-08](https://quant67.com/post/algorithms/48-topo-sort/topo-sort.html)。v1.5.0 Kahn 环检测能"检测到环存在+定位环内节点集合"但无法输出环的边路径（A→B→C→A 的具体环链）。补入 DFS 三色标记法（white/gray/black）提取具体环路径，输出 cycle_paths.csv 供 architecture_issue_registry.yaml 人工裁定打破环。注意单一 visited 数组无法正确检测有向图环（共享节点误判），三色标记的 gray 状态专门区分"在当前 DFS 路径上"vs"已完成"；(6) §7.0.3 记录 **Tarjan SCC 远期升级路径**——[quant67.com 2026-06-08](https://quant67.com/post/algorithms/48-topo-sort/topo-sort.html) §四的 Tarjan 强连通分量算法一次性识别所有 SCC 并构建凝聚 DAG。102 表规模下 DFS 三色标记已足够（环数量预期 ≤2），Tarjan SCC 作为"环数量>5 时的升级路径"记录不实施。三层递进：Kahn 检测"有没有环"→ DFS 三色标记提取"环路径"→（环复杂时）Tarjan SCC 识别"所有 SCC"；(7) §7.0.5 补 **CodeScene predict Omissions schema↔doc 共变检测**——参考 [CodeScene 2.4.0 Use Temporal Coupling to predict Omissions](https://docs.enterprise.codescene.io/versions/2.4.0/guides/technical/temporal-coupling.html#use-temporal-coupling-to-predict-omissions) + [Software Design X-Rays Adam Tornhill 2018](https://media.pragprog.com/titles/atevol/intro.pdf)。predict Omissions 是 Temporal Coupling 的**逆向应用**：当两文件应当共变但实际不共变（schema 变了但文档没跟），预测文档更新被遗漏。CodeScene 明确列出三种"应当共变"场景，本审查关注"文档应随其描述的系统共变"。补入 predict Omissions 算法（定义 expected_coupling 映射 → 复用 §7.0.3 Jaccard 共现矩阵 → 计算 actual_coupling → 若 schema 有变更但 actual_coupling=0 → 标 ⚠️ 预测遗漏）+ 严重度分级（HIGH/MEDIUM/LOW/OK）+ 与 §7.0.5 增量更新联动（predicted_omission.csv HIGH/MEDIUM 项注入增量更新流程）。不自动修复（§9 红线"不自动生成文档"）。与 SCORE [Orphan Topics](https://github.com/informatique-cdc/SCORE/blob/main/docs/INGESTION_AND_ANALYSIS.md) 对比：predict Omissions 找"有代码变更但无文档跟随"（schema→doc 缺失），SCORE Orphan Topics 找"有文档但无代码消费"（doc→schema 缺失），两者对偶互补；(8) §2.2 补 **ODCS v3.1.0 版本号+DCS 弃用说明**——参考 [bitol.io 2025-12-07 ODCS v3.1.0 公告](https://bitol.io/bitol-announces-odcs-v3-1-0-stronger-smarter-and-stricter/) + [docs.datacontract.com 2026](https://docs.datacontract.com/open-data-contract-standard) + [adriennevermorel.com 2026-03-27](https://adriennevermorel.com/notes/open-data-contract-standard/)。ODCS 当前最新版本为 v3.1.0（2025-12-07 发布），相比 v3.0 的关键增强：RFC-0013 属性间关系（foreignKey 声明）+ 更严格 JSON Schema 校验 + 可执行 SLA + 外部/内部契约引用。v3.1.0 完全向后兼容 v3.0。旧 Data Contract Specification (DCS) 格式已被弃用——datacontract.com CLI 仍接受但新契约应遵循 ODCS，两支团队正在协调合并。ODCS 已成为 de facto 标准。§9 补 2 项不做什么（不实施 Tarjan SCC 环检测——102 表规模 DFS 三色标记已够 / 不自动修复 predict Omissions 检测结果——预测≠修复，人工 review 不可省）。全网搜索验证：[Archy #131 2026-05-25](https://github.com/hslee16/Archy/issues/131) 验证 commit-size 归一化方向+large commits FP 源、[CodeScene 3.5.23](https://docs.enterprise.codescene.io/versions/3.5.23/guides/technical/temporal-coupling.html) 验证三信号+Sum of Coupling 指标、[CodeScene 2.4.0 predict Omissions](https://docs.enterprise.codescene.io/versions/2.4.0/guides/technical/temporal-coupling.html#use-temporal-coupling-to-predict-omissions) 验证逆运算方向+三种应当共变场景、[spacecomplexity.ai 2026-05-24](https://spacecomplexity.ai/blog/topological-sort-algorithm) 验证 min-heap Kahn 确定性排序+DFS 三色标记 O(V+E)、[quant67.com 2026-06-08](https://quant67.com/post/algorithms/48-topo-sort/topo-sort.html) 验证 Kahn 环检测存在性判定+Tarjan SCC 远期路径、[bitol.io 2025-12-07](https://bitol.io/bitol-announces-odcs-v3-1-0-stronger-smarter-and-stricter/) 验证 ODCS v3.1.0 版本号+RFC-0013 关系+可执行 SLA、[docs.datacontract.com 2026](https://docs.datacontract.com/open-data-contract-standard) 验证 DCS 弃用+ODCS 成为 de facto 标准、[adriennevermorel.com 2026-03-27](https://adriennevermorel.com/notes/open-data-contract-standard/) 验证 ODCS de facto 标准地位、[SCORE 2026](https://github.com/informatique-cdc/SCORE/blob/main/docs/INGESTION_AND_ANALYSIS.md) 验证 Orphan Topics 对偶方向。维持 draft（Temporal Coupling 增强+确定性排序+环路径提取+predict Omissions+ODCS v3.1.0 算法已完整但待执行验证） |
| 2026-08-10 | 1.9.0 | 新鲜度度量升级+状态指纹+假新鲜失败模式+验证信任模型：Freshness SLO/SLI+OKF v0.2 stale_after 对比+DataHub docFreshnessInfo verifiedAtVersion 状态指纹+DZone 五种假新鲜失败模式+OKF v0.2 trust/provenance/attestation+Attested Computation | **文档新鲜度度量体系升级与验收信任模型补强**（回应"施工环节流程算法有缺失"+"2026 年 8 月今天最新研究实践算法"+"有没有更好的答案算法"+"文档结构内容有没有需要调整"+"持续改进不要停下来询问"审查）：(1) §7.0.4 补 **Freshness SLO/SLI 服务级别度量**——参考 [oneuptime.com 2026-01-30 Freshness SLOs](https://oneuptime.com/blog/post/2026-01-30-freshness-slos/view) + [yutils.jdgrid.com 2026-05-25 SLI/SLO](https://yutils.jdgrid.com/en/guides/how-slis-and-slos-actually-work) + [skillmd.ai 2026 SLA/SLO/SLI](https://www.skillmd.ai/skills/sla-slo-and-slis/)。当前 §7.0.4 的 timeliness 是**连续值**（0-10 分）度量"单表文档多新鲜"，但缺少**二元合规判定**"多少比例文档达标"。补入 Freshness SLI = (timeliness ≥ 7.0 的表数 / 总表数) × 100% + SLO=90% 目标 + Error Budget=10% 管理（剩余 >50% 正常施工 / 20-50% 降速修复 / 耗尽冻结新施工）。补入 Age-based vs Lag-based 新鲜度区分（age_days 绝对年龄 vs 文档同步时间-代码变更时间=更新滞后天数），当前 §7.0.4 用 age_days（Age-based），Lag-based 作为远期 git log 计算路径记录；(2) §7.0.4 补 **Google OKF v0.2 stale_after 固定日期备选对比**——参考 [itbrief.asia 2026-07-27 Google OKF v0.2](https://itbrief.asia/story/google-adds-trust-provenance-to-open-knowledge-format)。OKF v0.2 的 stale_after 是 frontmatter 中写死的固定日期（如 2026-12-31 后过时），适合有明确过期日的知识包（如法规文档）。本审查文档无固定过期日（业务持续即有效），stale_after 不适用——v1.9.0 保留状态指纹（内容 hash 判断）+time_decay（指数衰减）双机制，stale_after 作为"有明确过期日文档"的备选记录；(3) §7.0.5 补 **DataHub docFreshnessInfo verifiedAtVersion 状态指纹机制**——参考 [DataHub PR #19023 2026-08-09](https://github.com/datahub-project/datahub/pull/19023)。当前 §7.0.5 的 Embedded Freshness 闭环是"git commit→hook 触发→识别受影响表→标记文档需重写"的**事件驱动**模式（每次 commit 都触发检查）。但存在盲区：上游表 schema 变更但下游文档未级联标记（git diff 只触发 stock_list 自身文档检查，不传播到依赖它的 kline_daily）。补入 docFreshnessInfo 五字段模型（verifiedAtTime/verifiedAgainstUrns/actor/verificationType/lastVerifiedSchemaHash）+ 状态指纹机制（verifiedAgainstUrns 包含一跳上游 + 联合 hash → 上游 hash 变更→下游联合指纹变更→自动标记 stale，状态驱动补事件驱动）。与 Google OKF v0.2 trust/provenance 模型对比（DataHub 状态指纹+一跳传播 vs OKF 固定日期+无传播），结论：DataHub 状态指纹更适合本审查场景（文档-代码依赖关系明确，需上游传播检测）。封装 `scripts/freshness_fingerprint.py` 输出 `freshness_fingerprint.csv`。不引入 DataHub 平台（§9 已声明，仅借鉴机制）；(4) §3.4 补 **DZone 五种管道级假新鲜失败模式**——参考 [DZone 2026-07-20 "When Data Quality Checks Pass but the Data Is Still Stale"](https://dzone.com/articles/data-freshness-enhances-validity)。§3.4 的"文档腐烂三类"+Model drift 分类都是**漂移发生后的检测**，但 DZone 指出更隐蔽的问题是"管道成功 ≠ 数据新鲜"——五种假新鲜失败模式：(1)源端无新文件→git commit 改无关文件 hook 误判、(2)部分分区到达→一个 commit 改多表但增量更新只标记第 1 张、(3)迟到上游→上游 schema 变更但下游未级联、(4)仪表板缓存→文档已更新但读者本地未 pull、(5)回填覆盖→git revert 恢复了旧版文档。映射到文档-代码同步场景并补强：失败模式 2 补"动态表名追踪"（f-string/变量拼接的表名用 AST 提取字符串字面量）、失败模式 5 补"回滚版本校验"（revert 前检查目标 commit 文档 timeliness 是否低于当前→警告"回滚到更旧文档版本"）。失败模式 1 已由 v0.9.0 DocPilot false-positive filter 覆盖、失败模式 3 已由 v1.9.0 verifiedAtVersion 一跳 lineage 传播覆盖、失败模式 4 非本审查范围（属 git 工作流培训）；(5) §7.0.6 补 **Google OKF v0.2 trust/provenance/attestation 三层验证信任模型+Attested Computation 验证概念**——参考 [itbrief.asia 2026-07-27 Google OKF v0.2](https://itbrief.asia/story/google-adds-trust-provenance-to-open-knowledge-format)。OKF v0.2 的三层验证：(1)trust（generated vs verified 分离——文档是 AI 生成的草案还是人工验证通过）、(2)provenance（来源追溯——记录验证者+验证时间，对齐 §7.0.5 docFreshnessInfo 五字段）、(3)attestation（Attested Computation——验证验证过程本身是否可信，即 L3 抽检是否真执行了规定检查步骤）。补入 generated vs verified 分离（frontmatter verification_status: draft→verified 替代 OKF 知识包 frontmatter 格式）+ Attested L3 抽检清单 4 检查点（关键字段是否在 SQL SELECT 真实出现/下游逻辑计算是否在代码真实执行/消费频率与 tasks.yaml 调度是否一致/依赖上游与 frontmatter depends_on 是否一致——4 检查点全过才 L3 通过，逐项记录 ✅/⚠️ 替代二元"通过/不通过"）。不引入密码学 attestation（OKF v0.2 完整 attestation 用 Sigstore/CLASPIE 密码学签名，适合多方协作开源场景，个人项目无多方信任需求，§9 已记录）；(6) §9 补 2 项不做什么（不引入 Google OKF v0.2 完整工具链——密码学 attestation 基础设施成本超增量价值，仅借鉴 Attested Computation 思想用 L3 抽检清单 4 检查点记录验证过程 / 不引入 DataHub docFreshnessInfo aspect 工具链——docFreshnessInfo 是 DataHub 平台内建 aspect，引入它即引入整个 DataHub，与 §9 已声明"不引入外部数据目录工具"一致，仅借鉴 verifiedAtVersion 状态指纹机制用 git+frontmatter+PowerShell 脚本实现轻量版）。全网搜索验证：[oneuptime.com 2026-01-30](https://oneuptime.com/blog/post/2026-01-30-freshness-slos/view) 验证 Freshness SLO 框架方向+error budget 速度契约、[yutils.jdgrid.com 2026-05-25](https://yutils.jdgrid.com/en/guides/how-slis-and-slos-actually-work) 验证 SLI/SLO 机制、[skillmd.ai 2026](https://www.skillmd.ai/skills/sla-slo-and-sli/) 验证 SLA/SLO/SLI 层级、[itbrief.asia 2026-07-27](https://itbrief.asia/story/google-adds-trust-provenance-to-open-knowledge-format) 验证 OKF v0.2 trust/provenance/attestation 五类信号、[DataHub PR #19023 2026-08-09](https://github.com/datahub-project/datahub/pull/19023) 验证 docFreshnessInfo aspect+verifiedAtVersion 字段、[DZone 2026-07-20](https://dzone.com/articles/data-freshness-enhances-validity) 验证五种假新鲜失败模式。维持 draft（新鲜度度量升级+状态指纹+假新鲜失败模式+验证信任模型算法已完整但待执行验证） |
| 2026-08-10 | 2.0.0 | 2026-08 最新研究评估闭环：SetGo metadata readiness 工具链评估排除 | **2026-08 全网最新研究评估完整性闭环**（回应"全网搜索最新的 2026 年 8 月今天的最新研究实践算法"+"持续改进不要停下来询问"审查）：(1) §9 补 **SetGo metadata readiness 工具链排除**——参考 [SetGo SSDBM '26 2026-08-11](https://dlnext.acm.org/doi/10.1145/3828820.3828827)（Wilkinson et al.，SSDBM '26 Proceedings of the 38th International Conference on Scalable Scientific Data Management，2026-08-11 出版）。SetGo 是开源 Python 工具包，评估+修复科学数据集的 metadata readiness 六维（FAIR 合规/许可/溯源/治理/可复现/目录就绪），assess→enrich→publish 闭环将 FAIR 分数从 52-57% 提升到 81-91%，发布到 Hugging Face Hub/CKAN/OpenMetadata + ML Commons Croissant 1.0 metadata sidecar，集成 LLM coding agent /setgo skill。六维适用性分析：许可（licensing）不适用（本仓库自采 A 股市场数据无外部 dataset 许可约束）/ 目录就绪（catalog readiness）不适用（无外部目录发布需求，design_memos 即内部目录）/ 可复现（reproducibility）部分相关（数据管道可复现已由 tasks.yaml 调度配置覆盖）→ 3 维不适用或已覆盖。剩余 3 维（FAIR 合规/溯源/治理）已由 §7.0.4 Q score 4 维（completeness/accuracy/specificity/timeliness）+ v1.7.0 ODCS 6 组件（schema/语义/质量/SLA/所有权/变更管理）覆盖。SetGo 面向科学数据集对外发布场景（ERA5 气候/材料/PDB 蛋白质组发布到 HF Hub），本审查是内部市场数据文档覆盖审计无对外发布需求。SetGo 的 assess→enrich 思想已由 §7.0.2 代码反推（assess 代码用法）+ §7.0.1 模板套用（enrich 补文档）+ §7.0.6 L3 抽检（verify）三步覆盖，/setgo LLM agent skill 与 v0.7.0 DocAgent 远期路径同质（LLM 多步调用成本过高，§9 已记录 DocAgent 不当前采纳）。不引入 SetGo 工具链+Croissant 1.0 sidecar（派生产物不入 git 约束）。本版本标志 2026-08 全网最新研究（含 2026-08-11 SetGo + 2026-08-09 DataHub docFreshnessInfo + 2026-08-04 paired-model + 2026-08-02 MTTD/MTTR + 2026-08-06 Innovation-Residual）已全部评估完毕，文档算法体系达到当前时间点的完整性闭环——施工环节流程算法无缺失、选项外无更优算法、2026-08 最新研究已穷尽评估。全网搜索验证：[dlnext.acm.org SSDBM '26 2026-08-11](https://dlnext.acm.org/doi/10.1145/3828820.3828827) 验证 SetGo 六维 metadata readiness+assess→enrich→publish 闭环+FAIR 提升 52-57%→81-91%、[dosu.dev 2026-05-14](https://dosu.dev/blog/score-documentation-freshness-in-ci) 验证 freshness scoring 三信号（已 v1.3.0 覆盖 symbol-level drift）、[WikiMonitor-onto JAAI 2026-07-24](https://www.jaai.net/vol4/JAAI-V4N3-66.pdf) 验证 ontology-aware staleness BFS 传播（已 v0.6.0 覆盖）。维持 draft（算法体系已达完整性闭环，待执行验证） |
| 2026-08-12 | 2.1.0 | 全量重扫核验修正：三层覆盖口径+真闲置收敛+设施盘点+施工计划重 scope | **2026-08-12 git 提交态全量重扫核验**（七轮审查：现状盘点/方法学/缺失环节/最新研究/过度工程/一致性/规范符合性）：(1) **基数修正**——表数 102→103（`market_stock_valuation` 2026-08-11 commit 81c7687540 新增）、受扫文档 42→46 篇（47 篇编号文档-本备忘自引，新增 60/61/64/65/90/91 等）、字符量 4.59M→5.24M；(2) **三层覆盖口径替代单一文档覆盖率**——消费层 37（35.9%）/规划层 53（51.5%，17/64 号资产清单+下载规范）/零覆盖 13（12.6%）：v0.2.0 的"37.3%"实测即消费层口径（两天稳定），17/64 号带来的规划层引用使任一文档命中口径虚高至 87.4% 但**规划引用≠消费覆盖**（§7.0.6 L2/L3 要求字段/下游逻辑/频率描述），施工目标以消费层为准；(3) **真闲置 3→1 张**（仅 `index_meta` 五源全零）+ 新增 §6.1b"代码零引用但规划已登记"6 张类别（dividend_tax_node 改判 dormant VIEW 免归档/index_adjustment/ipo_schedule/margin_target_adjustment/msci_adjustment/stock_valuation 采集未施工标 dormant）——v0.2.0 的 dividend_tax_node/msci_adjustment"真闲置"判定被 17/64 号规划覆盖推翻；(4) **§5 全部数字实测重算**——热度榜（tick 471/technical_indicator 59/trade_calendar 48，通用名 index 假阳性 441 次按全名复核 3 次）、零文档缺口清单 15→12 张（stock_indicator 12 次/cb_iv 7 次/分钟级 K 线 9 张路由映射级）、低频表复核全部转规划层；(5) **§2.4 已施工设施盘点**（通用规则 #11）——被审查对象（103 表 DDL+76 条注册表+15 provider）全部已施工，审查工具链（audit_data_utilization.ps1 等 5 脚本+docs/_audit/ 矩阵）全部未施工，`src/zephyr/data/ingestions/` 目录不存在（§7.5 路径修正为 provider 层+src/zephyr/data/config/tasks.yaml）；(6) **§7 施工计划重 scope**——消费层缺口 59 张（47 规划层代码活跃+12 零覆盖代码活跃），覆盖轨迹 35.9%→44.7%→68.9%→93.2%（终端口径），data_asset_registry 补齐数 26→27 张；(7) **§10 开放问题更新**——Q1 从 3 张收敛为 1 张（index_meta 默认 DEPRECATED 观察期）、新增 Q8（6 张 §6.1b dormant 裁定，AI 默认建议不删不采仅登记）、Q5 核验已登记但 00 号版本字符串/目录计数待同步；(8) **§9 补 2 项不做什么**（不为 53 张规划层覆盖表全部补消费级文档——代码零引用表无消费可反推 / 不追溯复现 v0.2.0 历史扫描数字——扫描输出须落地 CSV 快照）；(9) **v0.2.0 历史数字不可复现声明**——其逐表计数以未提交工作区为扫描对象（如 block_trade 52 次/5 文档 vs 实测 7 次/2 文档），教训：审计扫描输出必须入 git 快照。全网搜索验证：[modern-datatools.com 2026-04 Data Baselining](https://www.modern-datatools.com/blog/data-baselining-warehouse-lifecycle-2026) 三层基线法（生命周期策略→使用量清理→团队 ritual）验证盘点-分层路径 + "20% 表活跃查询"企业常态反衬 99.0% 利用率健康、[heth.ink 可转债量化](https://heth.ink/ConvertibleBonds/) 双低/隐波差因子 2022 后系统性衰退佐证 cb_iv 降权合理、[Fidelity 可转债套利](https://institutional.fidelity.com/app/proxy/content?literatureURL=/9912569.PDF) gamma trading 需做空正股不适用于 T+1 无融券约束（§6.2 批次 B cb_iv 仅记录不施工佐证）。**施工执行插曲**：本版回填过程中遭遇并发会话 stash 隔离清空暂存区事故，全部修改经 dangling blob（f34adb8b）字节级恢复——教训已记入 project_memory 同级灾难模式（git add 快照是最小保护层）。维持 draft（Q1/Q8 待人裁定 + 三波施工未执行） |
