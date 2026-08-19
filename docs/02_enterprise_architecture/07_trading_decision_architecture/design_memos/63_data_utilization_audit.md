---
ttl: permanent
doc_type: architecture_view
title: 业务数据资产利用率审查与施工计划
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "2.1.2"
date: 2026-08-15
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

## 结案报告（AI-NIGHT-001 复核 2026-08-19）

> **实际开发**：审查本体已完工——v2.1.0（2026-08-12 git 提交态）全量重扫定案：103 表利用率 99.0%、真闲置 1 张（index_meta）、消费层文档覆盖 37/103=35.9%（真问题）、规划层 53 张、零覆盖 13 张、代码零引用但规划已登记 6 张。配套注册表侧：data_asset_registry.yaml 已由 62 号施工线建成并扩充至约 199 条（2026-08-19 实证在位），本篇 §7.4"以 76 条为 base 补齐 27 张"的计划已由 62 号批次超额闭环。
>
> **最终成果**（2026-08-19 实证）：三层覆盖口径（消费层/规划层/零覆盖）成为数据文档治理的测量基线；§6.2 四批次施工清单 + §7 施工算法（模板/反推/拓扑/Q score/增量更新/验收闭环）齐备可执行；被审查对象（103 表 DDL + 注册表 + 15 provider）全部在位。
>
> **未做事项及原因**：
> - 三波补文档施工全部未执行（第一波批次 A 9 张风险表→35/37/10/24 号文档、第二波批次 B+C 25 张→26/22/15 号、第三波批次 D 记录）——2026-08-19 实证：35/37/10/24 号文档对 restricted_shares/share_unlock/etf_nav/edb_data/block_trade_detail 零引用，消费层覆盖仍 35.9%。属"计划就绪、施工未派单"（无批次归属）；裁定=未来工程-小型（纯文档施工，可按 §6.2 批次拆 3 个小批）。
> - 审查工具链 scripts/audit_data_utilization.ps1 + docs/_audit/ CSV 快照——未创建（§2.4 盘点自评"全部未施工"）；是持续校验（§3.4 extract/trace 循环）的前置。裁定=未来工程-小型。
> - community_detection.py / temporal_coupling.py / quality_spc.py / freshness_fingerprint.py（Leiden/Temporal Coupling/SPC/状态指纹）——运维期机制，触发条件（第一波施工启动+多波数据积累）未到；裁定=过度工程（当前阶段，重评条件随第一波启动激活）。
> - Q1 index_meta 生命周期 / Q8 六张 dormant 表处置 / Q3 hfq 统一 / Q4 ARCH 登记 / Q6 pre-commit warn——§10.2 待人决策项，未拍板；裁定=待 Owner（默认建议已在档）。
> - §9"不做什么"全表（DataHub/ODCS 工具链/AST 全量解析/LLM 全量语义验证等）——已逐项裁定拒绝，不施工；裁定=过度工程（不再逐条列出）。

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
| 状态 | 审查完成（v2.1.0 全量重扫核验：表数 102→103、文档 42→47 篇、真闲置 3→1 张、新增"代码零引用但规划已登记"6 张类别、§5/§6 全部数字以 git 提交态实测重算；v0.1.0-v2.0.0 各版本算法补强演进见 §11 修订记录），待补文档施工 |
| 上游 | [62_business_registry_construction](62_business_registry_construction.md)（12 注册表 schema 已定稿） |
| 下游 | [15_data_feature_layer_spec](15_data_feature_layer_spec.md) / [26_event_driven_strategy_detail](26_event_driven_strategy_detail.md) / [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md) 等数据消费方 |

## 2. 背景与问题诊断

### 2.1 项目处境

- 业务数据库已建成 [schemas/categories/](../../../../schemas/categories/) 下 **103 张表**的 DDL（market/fundamental/macro/cross 四大类前缀），覆盖 A 股/港股/美股/期货/期权/可转债/生猪期货/宏观经济等全品类（v2.1.0 核验：`market_stock_valuation.py` 于 2026-08-11 commit 81c7687540 新增，102→103）
- design_memos 下 47 篇编号文档（不含 [AI_review_instructions.md](AI_review_instructions.md) 辅助文件；受扫 46 篇=47 篇-本备忘自引）共约 5.24M 字符，承载交易决策架构 why 层
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
| 代码零引用但规划已登记 | 未识别 | 未识别 | **6 张**（dividend_tax_node/index_adjustment/ipo_schedule/margin_target_adjustment/msci_adjustment/stock_valuation）——DDL+规划文档有，代码/`src/zephyr/data/config/tasks.yaml` 全零，采集未施工 |
| P0"高价值闲置" | 8 张 | 全部 CODE_ONLY | v2.1.0 确认：批次 A 风险表代码均活跃，但**消费文档仍缺**（仅 17/64 号规划层提及）——§7 第一波施工内容不变 |
| P4 生猪期货 | "完全不涉及" | 代码 7-8 次引用 | v2.1.0 实测：3 张生猪表代码各 1 次引用（采集模板级）+规划层覆盖——维持批次 D 暂缓 |

> **v2.1.0 关键口径修正**：v0.2.0 的"文档覆盖率 37.3%"与 v2.1.0 实测的"消费层覆盖 35.9%"（37 张）在数值上高度一致——**v0.2.0 的扫描实质上测的就是消费层覆盖**（当时 17/64 号尚未提交或未含大量表引用，未污染口径）。2026-08-11 后 17/64 号提交带来 53 张规划层引用，若按"任一文档命中"口径覆盖率虚高至 87.4%，会掩盖消费层缺口。**v2.1.0 起 §5.1 以三层口径分别报告，施工目标以消费层覆盖为准**。
>
> **v0.2.0 历史数字不可复现声明**：v0.2.0 的逐表引用计数（如 `block_trade` 52 次/5 文档、`index_adjustment` 代码 17 次）以 2026-08-10 工作区未提交文件为扫描对象，2026-08-12 以 git 提交态重扫无法复现（`block_trade` 实测 7 次/2 文档，`index_adjustment` 代码 0 次）。教训：§3.4 扫描输出必须落地 CSV 快照随施工提交（dogfood 本文 §3.4 机制），否则历史审计数字无法回溯验证。v2.1.0 起 §5/§6 全部数字以本版实测为准，历史版本数字仅作演进参考。

**Data Contract 概念重构（v1.7.0 新增 / v1.8.0 补 ODCS v3.1.0）**：上述"文档覆盖缺口"可用 2026 年行业标准的 **Data Contract** 概念重构——[soda.io 2026-06](https://soda.io/blog/data-contracts-vs-schema-registry) 明确区分 **Schema Registry 管结构**（对应 schemas/categories/*.py DDL）、**Data Contract 管行为**（schema+语义+质量规则+SLA+所有权+变更管理，对应 DDL+design_memos 文档）；主流标准为 [ODCS](https://github.com/bitol-io/open-data-contract-standard)（Linux Foundation Bitol），当前最新 **v3.1.0**（2025-12-07，[bitol.io 公告](https://bitol.io/bitol-announces-odcs-v3-1-0-stronger-smarter-and-stricter/)，向后兼容 v3.0；原 DCS 格式不再使用）。

**本仓库的 Data Contract 完整度映射**：

| Data Contract 六组件 | 本仓库对应 | 完整度 |
|---|---|---|
| Schema（结构） | schemas/categories/*.py DDL | ✅ 103/103 完整 |
| Semantics（语义） | design_memos 文档消费方描述 | ⚠️ 消费层 37/103（规划层 53 张仅有资产清单级语义）——本审查核心问题 |
| Quality rules（质量规则） | data_asset_registry.yaml 字段 + §7.0.4 Q score | ⚠️ 待施工（§8 关联） |
| SLA（新鲜度/可用性） | §7.0.4 timeliness 指数衰减 + §3.4 Detective 扫描 | ⚠️ 待施工 |
| Ownership（所有权） | data_asset_registry.yaml owner 字段 + frontmatter owner | ⚠️ 待登记 |
| Change management（变更管理） | §7.0.5 增量更新 + git hook + §3.4 引用漂移检测 | ⚠️ 待施工 |

**重构结论**：本审查的"补文档覆盖缺口"本质是**补全 Data Contract 的 Semantics 层**——schema 已完整（DDL 齐全），但 semantics/quality/SLA/ownership/change-management 五层缺失或待施工。概念重构不改变施工计划（§7 仍按批次补文档），但为 §8 data_asset_registry 施工提供 ODCS 六组件对齐目标。仅用概念不引入 ODCS YAML 工具链（个人项目，DDL+markdown 已是轻量载体，YAML 属派生产物违反"派生产物不入 git"约束，§9 已裁定）。

### 2.3 约束条件

- **不引入新数据源**：本计划只盘活已有 103 张表，不申请新供应商
- **不破坏现有策略**：补文档是"记录已有用法"，不改变数据流
- **优先级原则**（project_memory）：风险相关模块（drawdown/var/kill_switch）先于 alpha 策略；文档覆盖优先服务风险与回撤模块
- **不过度工程**：v2.1.0 实测消费层缺口 66 张（53 规划层+13 零覆盖）中代码活跃 59 张——只需补文档，无需"接入数据"；1 张真闲置表（`index_meta`）的处置 + 6 张代码零引用表的采集决策是有效产出

### 2.4 已施工设施盘点（v2.1.0 新增，回应通用规则 #11"先清楚有什么→才能知道怎么改→才能知道该退役什么"）

> 本文此前各版本引用了多个脚本/目录作为"实施位置"。v2.1.0 全仓核验其真实存在性，防止"文档引用不存在设施"的脱节。

**已施工（真实存在，v2.1.0 核验）**：

| 设施 | 位置 | 状态 | 说明 |
|---|---|---|---|
| 业务表 DDL 真源 | [schemas/categories/](../../../../schemas/categories/) 103 个 .py | ✅ 全部入 git | 2026-08-11 提交 `022910926f`/`81c7687540` 补齐最后 8 张（calendar_event/dividend_tax_node/index_adjustment/ipo_schedule/margin_target_adjustment/msci_adjustment/stock_valuation/technical_indicator） |
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

[schemas/categories/](../../../../schemas/categories/) 下 103 个 `.py` 文件，每个对应一张 ClickHouse 业务表（文件名前缀 `market_`/`fundamental_`/`macro_`/`cross_` 对应业务域）。v2.1.0 核验：market 88 / fundamental 12 / macro 2 / cross 1 = 103。

### 3.2 引用扫描方法（v0.2.0 三层校验 / v2.1.0 补覆盖分层口径）

| 层 | 方法 | 工具 | 命中判定 |
|---|---|---|---|
| 1. 英文/拼音表名 @ design_memos | `Select-String` 在 design_memos/*.md 全文搜表名（不区分大小写，排除 63 号自引 + AI_review_instructions） | PowerShell | 命中即视为文档已覆盖——**v2.1.0 起细分两层**：命中文档为 17/64 号（资产清单/下载规范）=**规划层覆盖**；命中其他消费方文档（策略/风控/数据层）=**消费层覆盖**。施工目标以消费层为准 |
| 2. 中文别名补校 @ design_memos | 对未命中的表，搜中文别名（如 `dragon_tiger_seat` → "龙虎榜营业部"） | 人工 | 任一别名命中即恢复为"文档已覆盖" |
| 3. 代码层引用 @ src/zephyr/（v0.2.0 新增） | `Get-ChildItem -Recurse *.py \| Select-String` 搜表名 | PowerShell | 命中即视为代码已消费——**文档未覆盖但代码在用 = 文档覆盖缺口，非闲置**。v2.1.0 扩展：同步扫 `config/`+`tasks.yaml`+注册表 yaml，区分"代码零引用"是"采集未施工"还是"真闲置" |

> **v0.2.0 关键修正**：v0.1.0 仅做层 1+2 得出"43 张闲置"误判；层 3 代码层扫描发现其中 40 张实际被代码引用——**"文档没写"不等于"数据闲置"**。
>
> **v2.1.0 口径修正**：层 1 的"任一文档命中即覆盖"在 17/64 号提交后失效——53 张表仅被资产清单/下载规范提及但无消费方文档描述用法。v2.1.0 将层 1 拆分为规划层/消费层两档（§5.1），避免"规划引用冒充消费覆盖"；层 3 补 config/调度/注册表扫描，实测发现 6 张表五源全零引用，属"采集未施工"（§6.1b）而非"文档缺口"。

### 3.3 审查局限

- **通用名假阳性**：`market_index.py` 的 basename 为 `index`（去除前缀后），子串匹配会命中 `index_list`/`kline_index` 等无关表——已用全名 `market_index` 复核修正（实际 CODE_ONLY，非 BOTH）
- **子串匹配假阳性**：`5min` 会匹配 `15min`——对闲置判定影响有限（保守方向），但热度计数偏高
- **"tick" 关键词过宽**：匹配 `ticker`/`TickTock` 等无关词，hit count 仅作热度参考
- **代码层引用性质未区分**：代码中的表名引用可能是"活跃消费"、"DDL 模板继承"、"已弃用但未清理"——需人工复核（§6 已标注）
- **中文别名校验未重跑**：v0.2.0 代码层扫描仅做英文表名匹配，未重做层 2 中文别名校验（v0.1.0 层 2 曾恢复 20 张表）——真实缺口约 41 张（61-20）；§6.2 批次清单应理解为"潜在缺口"而非"确定缺口"
- **config/ 配置文件未扫**：数据采集配置（如 `config/.env.qmt`）中的表引用未纳入——采集脚本必然引用所有建表，不能作为"消费"证据

### 3.4 自动化与持续校验（v0.3.0 新增）

> v0.3.0 引入 [OpenSpec extract/trace 循环](https://github.com/Fission-AI/OpenSpec/discussions/739)（2026-02）和 [CI 文档覆盖率门禁](https://codex.danielvaughan.com/2026/05/16/codex-cli-automated-code-documentation-generation-docstrings-jsdoc-sphinx-ci-pipelines/)（2026-05）思路，将一次性审查升级为可重复的持续校验。

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

**CI 门禁（远期）**：当文档覆盖率低于 80% 行业基准时，pre-commit 发出 warn（不阻断——个人项目不强制 CI 阻断，但提醒）。

**文档腐烂三类**（[codex.danielvaughan.com 2026-04](https://codex.danielvaughan.com/2026/04/26/codex-cli-doc-rot-detection-automated-documentation-repair/)）：
- **引用漂移**（Reference Drift）：表名改名后文档未同步——可自动化检测（grep 新名零命中 + 旧名仍有命中）
- **结构衰变**（Structural Decay）：文档交叉引用断链——已由 §11 交叉引用验证覆盖
- **概念过时**（Conceptual Staleness）：文档描述的用法与代码实际行为不符——需人工复核，§10 Q3（hfq 矛盾）即此类

**Preventive vs Detective 双层检测（v0.9.0 新增，参考 [hassette #634 2026-04](https://github.com/NodeJSmith/hassette/issues/634)）**：

| 检测模式 | 定义 | 本审查对应 | 覆盖状态 |
|---|---|---|---|
| **Preventive**（预防式） | CI 时阻止不合规 PR——在文档漂移**进入仓库前**拦截 | §3.4 CI 门禁（覆盖率 <80% → warn）+ §7.0.6 验收闭环（L1/L2/L3 阻断不合格文档）+ pre-commit hook | ✅ 已覆盖 |
| **Detective**（侦测式） | PR 间定期扫描**已累积**的漂移——文档引用了已删除的路径/命令 | 下方 Detective 扫描规则（5 类检查，每周 cron） | ⏳ v0.9.0 补入 |

为何需要 Detective 层：Preventive 只在 PR 提交时触发——若文档引用的文件在**另一个 PR** 中被删除，pre-commit 无法检测跨 PR 的引用断裂；Detective 定期扫描捕获**跨 PR 累积**的漂移。实现选型 **Option C Hybrid**（hassette 三选项之一）：确定性检查（路径/表名/命令/链接存在性）用 PowerShell 脚本融入 `audit_data_utilization.ps1`，语义检查用 §7.0.6 L3 人工抽检——不选 Option A scheduled agent（LLM 成本高且 §9 已声明 agent 仅检测不修复），不选 Option B 纯脚本（语义检查弱）。两者互补：extract/trace 管施工后的覆盖率提升（事件驱动），Detective 管施工间的漂移累积（时间驱动）。

**Detective 扫描规则**（融入 §3.4 extract/trace 循环）：

```
Detective 扫描（每周 cron 触发）：
1. 路径完整性检查：grep design_memos/*.md 中所有 [schemas/categories/xxx.py](...) 链接 → 验证文件是否存在
   → 若文件不存在 → 标 ⚠️ 引用漂移（文档腐烂类型 1）
2. 表名一致性检查：grep 所有英文表名 → 与 schemas/categories/ 实际 .py 文件名对比
   → 若引用了不存在的表名 → 标 ⚠️ 概念过时（类型 3）
3. 命令有效性检查：grep 所有 `! <command>` 或 `python scripts/xxx` → 验证脚本是否存在
   → 若脚本不存在 → 标 ⚠️ 命令漂移
4. 交叉引用完整性：grep 所有 [xx_memo](xx_memo.md) 链接 → 验证目标文档是否存在
   → 若不存在 → 标 ⚠️ 结构衰变（类型 2）
5. 代码符号漂移检查（v1.3.0 新增，参考 [dosu.dev 2026-05](https://dosu.dev/blog/score-documentation-freshness-in-ci)）：grep 所有 `def xxx` / `class Xxx` 代码符号 → 验证 src/zephyr/ 中是否仍存在同名定义
   → 若已删除或改名 → 标 ⚠️ 符号漂移（引用漂移的代码符号变体）
   → dosu.dev 引用 Empirical Software Engineering 2024：28.9% 的 GitHub 仓库文档引用了代码中已不存在的 function/file/class，平均过期 4.7 年

→ 输出 docs/_audit/detective_scan.csv（文档名 × 漂移类型 × 漂移位置 × 严重度）
→ 严重度分级：⚠️ 路径不存在（高）/ ⚠️ 符号漂移（高）/ ⚠️ 表名过时（中）/ ⚠️ 命令漂移（低）
```

**Model drift 漂移来源分类（v1.2.0 新增，参考 [sincllm.com 2026-06](https://sincllm.com/blog/ai-drift-detection-production-model-output-degradation)）**：上述"腐烂三类"按**机制**分类，此处补**来源**分类，两者正交（来源×机制交叉标注落码——"数据漂移×引用漂移"走 §7.0.5 增量更新自动修复，"概念漂移×概念过时"走 §7.0.6 L3 人工复核）：

| 漂移类型 | 定义 | 本审查对应场景 | 检测方法 | 责任归属 |
|---|---|---|---|---|
| **数据漂移（Data Drift）** | 输入分布变化 | 代码引用表名字段分布变化——如 `kline_daily` 突然被 `kline_daily_hfq` 替代 | §3.4 Detective 扫描表名一致性检查 + §7.0.5 git diff 检测 | 自动化 |
| **概念漂移（Concept Drift）** | 相同输入的"正确输出"定义变化 | 风险模块表的消费语义变化——如 `etf_nav` 从"套利信号"变为"流动性危机信号" | §7.0.6 L3 语义抽检 + §7.0.4 Q score accuracy + §7.0.2 冲突解决 | 人工 |
| **模型漂移（Model Drift）** | 代码语义未变但行为变化 | 不适用——本审查无 LLM 模型，代码未变则行为未变 | — | — |

**管道级假新鲜失败模式（v1.9.0 新增，参考 [DZone 2026-07-20](https://dzone.com/articles/data-freshness-enhances-validity)）**：DZone 指出 **freshness gap**（事件发生→消费者可见的距离）是结构性检查永不测量的盲区——"管道成功 ≠ 数据新鲜"。五种假新鲜模式映射到文档-代码同步场景：

| # | DZone 原始场景（数据管道） | 本审查映射（文档-代码同步） | 覆盖状态/补强措施 |
|---|---|---|---|
| 1 | 源端无新文件——job 成功但处理了与昨天相同的输入 | git commit 只改无关文件，hook 误判"代码变更→文档需更新" | ✅ §7.0.5 DocPilot false-positive filter 已覆盖 |
| 2 | 部分分区到达——缺失分区不是 error | 一个 commit 改 3 张表代码，但增量更新只标记了第 1 张表文档 stale（git diff 表名提取遗漏） | ⚠️ **补强：§7.0.5 步骤 1.5 动态表名追踪**——对 f-string/变量拼接的表名用 AST 提取字符串字面量拼接（成本可控，非全量 AST） |
| 3 | 迟到的上游延迟了真实数据 | 上游表 schema 变更但下游文档未级联标记（git diff 只触发上游自身检查） | ✅ §7.0.5 `verifiedAtVersion` 一跳 lineage 传播已覆盖 |
| 4 | 仪表板缓存了过时表 | 文档已更新但读者本地 working copy 未 pull | ❌ 非本审查范围——属 git 工作流习惯，不补强 |
| 5 | 回填用旧快照覆盖了当前数据 | git revert 不慎恢复了更早版本的文档（含已修复的 bug），文档"倒退了时间" | ⚠️ **补强：§7.0.7 回滚版本校验**——revert 前检查目标 commit 的文档 timeliness 是否低于当前，更低则警告"回滚到更旧的文档版本" |

核心启示："Validity ≠ Freshness"——文档结构完整不等于语义未过时，这是 §7.0.6 L3 语义抽检防"假覆盖"的依据；Freshness 需按表差异化（风险红线表周级同步、历史参考表月级），与 §7.0.4 half_life 参数敏感性一致。失败模式 1-5 是 Freshness SLI 的假阳性源，上述补强使其更可信。

**paired-model 双 LLM 交叉验证（v1.6.0 新增，参考 [arXiv 2608.03500v1 2026-08-04](https://arxiv.org/html/2608.03500v1)）**：两独立 LLM 对同一文档-代码对做一致性判断（一致性 75.8%，kappa=0.532），作为 §7.0.6 L3 人工抽检的**远期自动化升级路径**——当前不采纳（59 张表×2 次 LLM 调用成本过高；kappa 仅 0.532 不能完全替代人工；远期触发条件：design_memos 100+ 篇或 L3 人工抽检不一致率 >15%）。其 temporal-validity safeguards 思想可简化融入 L3 抽检：先验证"文档描述的表用法在代码最近 N 次变更后是否仍成立"再判断语义一致性。

**6 轴审查方法（v0.6.0 远期升级路径）**：[K-AI 6-axis 2026-05](https://www.k-ai.ai/en/news/auditer-corpus-documentaire-ia-methode-6-axes/) 的企业级文档语料审查 6 轴模型——本审查 §3.2 三层校验覆盖"表名存在+代码引用"，但未覆盖文档间一致性/重复/未标记过时，6 轴映射如下：

| 轴 | K-AI 定义 | 本审查当前覆盖 | 状态 |
|---|---|---|---|
| 1 内部异常 | 单文档内一致性断裂（数值/阈值/版本不符） | §7.0.4 Q score accuracy 维度（L3 抽检） | ⏳ 远期升级——文档 50+ 篇时引入自动化数值一致性检查（grep 文档内所有阈值+跨章节交叉校验），当前 L3 抽检+Q score 已够 |
| 2 文档间冲突 | 多文档对同一表描述矛盾 | §7.0.2 多消费方冲突解决算法 | ✅ 已覆盖 |
| 3 分歧重复 | 同一表的多个文档版本未合并 | 不适用（design_memos 单仓库单版本，无分支重复） | N/A |
| 4 未标记过时 | 已失效文档未移除 | §6.1 4 阶段生命周期（DEPRECATED→SUNSET→REMOVED） | ✅ 已覆盖 |
| 5 可追溯性 | 作者/日期/验证/真源 | frontmatter depends_on + §11 修订记录 | ✅ 已覆盖 |
| 6 新鲜度 | 每段更新节奏 | §7.0.4 timeliness 指数衰减 | ✅ 已覆盖 |

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

**实现**：PowerShell 正则逐表按优先级 1→5 扫描 src/zephyr/ 代码引用上下文（`Select-String -Context 0,1`），confidence 写入 CSV 矩阵，封装进 `scripts/audit_data_utilization.ps1`。

**自动判定的边界**：
- **正则局限**：无法区分"SQL 字符串构造查询"与"SQL 字符串仅作日志"——优先级 1 命中后抽查 1-2 个文件确认是否真实执行。
- **多模式混合**：一张表可能同时有 SQL 查询（1.0）和 import（0.5）——取**最高 confidence**（乐观策略，避免模板继承拉低真实消费表的优先级）。
- **配置驱动消费**：如 `internal_compute_provider` 的 `_PERIOD_MAP` 字典映射 period→table 名，优先级 3 命中——需人工确认路由是否实际触发（16 号技术指标表已确认触发，confidence 应升为 1.0）。
- **不做 AST 全量解析**：实现成本高于正则 10 倍——个人项目用正则 + 抽查已够（§9）。

**与 §6.0 RICE 评分的对接**：自动判定的 confidence 直接喂入 §6.0 公式的 `confidence` 因子，替代人工标注。`hog_futures_core` 若自动判定为优先级 2（import 注册）→ confidence=0.5 → priority 从 2.8 降到 1.4（批次 D），与 v0.4.0 人工标注结论一致——验证自动判定可靠性。

**REFORGE 8 门置信度漏斗远期升级（v0.7.0 新增）**：[REFORGE 2026-07](https://ubos.tech/reforge-a-method-for-benchmarking-llms-reverse-engineering-capabilities-in-decompiled-binary-function-naming/) 的 8-gate confidence funnel + 溯源链——不当前采纳（针对反编译二进制场景，需 AST+控制流图+数据流分析，比 §9 已排除的 AST 全量解析更重；§3.5 正则命中行号+上下文已提供轻量溯源）。其分档思想（high/medium/low）与本审查 1.0/0.8/0.5 一致验证了分级合理性；远期触发条件：正则判定与人工复核差异率 >20% 时引入多门检查。

## 4. 业务数据库总览（103 张表）

按业务域分 9 大类（v0.1.0 报 101 张 + 算术合计 103 均有误，v0.2.0 修正为 102，v2.1.0 实测为 103——`market_stock_valuation` 2026-08-11 新增）：

| # | 业务域 | 表数 | 代表表（稳定 path） |
|---|---|---|---|
| 1 | A 股 K 线（含后复权/指数/板块/分钟级） | 15 | [kline_daily](../../../../schemas/categories/market_kline_daily.py) / [kline_daily_hfq](../../../../schemas/categories/market_kline_daily_hfq.py) / [kline_index](../../../../schemas/categories/market_kline_index.py) / [kline_sector](../../../../schemas/categories/market_kline_sector.py) |
| 2 | ETF/LOF/可转债 K 线 | 12 | [kline_etf_daily](../../../../schemas/categories/market_kline_etf_daily.py) / [kline_lof_1min](../../../../schemas/categories/market_kline_lof_1min.py) / [kline_cb](../../../../schemas/categories/market_kline_cb.py) |
| 3 | 跨市场 K 线（港股/美股/期货） | 5 | [kline_hk_daily](../../../../schemas/categories/market_kline_hk_daily.py) / [kline_us_daily](../../../../schemas/categories/market_kline_us_daily.py) / [kline_futures](../../../../schemas/categories/market_kline_futures.py) |
| 4 | Tick / 实时快照 / 涨跌停 | 4 | [tick](../../../../schemas/categories/market_tick.py) / [l2_tick](../../../../schemas/categories/market_l2_tick.py) / [realtime_snapshot](../../../../schemas/categories/market_realtime_snapshot.py) / [limit_up_down](../../../../schemas/categories/market_limit_up_down.py) |
| 5 | 基础元数据（股票/指数/板块/概念列表） | 21 | [stock_list](../../../../schemas/categories/market_stock_list.py) / [index_list](../../../../schemas/categories/market_index_list.py) / [sector_list](../../../../schemas/categories/market_sector_list.py) / [concept_board](../../../../schemas/categories/market_concept_board.py) / [etf_list](../../../../schemas/categories/market_etf_list.py) / [convertible_bond_list](../../../../schemas/categories/market_convertible_bond_list.py) |
| 6 | 资金流/杠杆/事件（龙虎榜/大宗/拍卖/MSCI） | 11 | [money_flow](../../../../schemas/categories/market_money_flow.py) / [margin_trading](../../../../schemas/categories/market_margin_trading.py) / [hk_connect_flow](../../../../schemas/categories/market_hk_connect_flow.py) / [dragon_tiger](../../../../schemas/categories/market_dragon_tiger.py) / [block_trade](../../../../schemas/categories/market_block_trade.py) / [msci_adjustment](../../../../schemas/categories/market_msci_adjustment.py) |
| 7 | 衍生品（期权/期货/生猪/可转债 IV） | 11 | [option_kline](../../../../schemas/categories/market_option_kline.py) / [option_iv](../../../../schemas/categories/market_option_iv.py) / [option_greeks](../../../../schemas/categories/market_option_greeks.py) / [cb_iv](../../../../schemas/categories/market_cb_iv.py) / [hog_futures_core](../../../../schemas/categories/market_hog_futures_core.py) |
| 8 | 基本面/宏观 | 22 | [balance_sheet](../../../../schemas/categories/fundamental_balance_sheet.py) / [income_statement](../../../../schemas/categories/fundamental_income_statement.py) / [cashflow_statement](../../../../schemas/categories/fundamental_cashflow_statement.py) / [analyst_forecast](../../../../schemas/categories/fundamental_analyst_forecast.py) / [restricted_shares](../../../../schemas/categories/fundamental_restricted_shares.py) / [share_unlock](../../../../schemas/categories/fundamental_share_unlock.py) / [edb_data](../../../../schemas/categories/macro_edb_data.py) / [macro_data](../../../../schemas/categories/macro_macro_data.py) / [stock_valuation](../../../../schemas/categories/market_stock_valuation.py)（v2.1.0 新增归入） |
| 9 | 衍生（技术指标/验证日志） | 2 | [technical_indicator](../../../../schemas/categories/market_technical_indicator.py) / [cross_validation_log](../../../../schemas/categories/cross_validation_log.py) |
| | **合计** | **103**（15+12+5+4+21+11+11+22+2=103；v0.1.0 报 101 且算术合计 103 均有误，v0.2.0 修正为 102，v2.1.0 以 [schemas/categories/](../../../../schemas/categories/) 实际 103 个 .py 文件为准修正——market 88 + fundamental 12 + macro 2 + cross 1；分类边界按代表表归集，单表归属以 §6 清单为准） | |

## 5. 引用审查结果

### 5.1 总体利用率（v2.1.0 全量重扫实测，2026-08-12 git 提交态）

| 指标 | 数值 | 说明 |
|---|---|---|
| 总表数 | 103 | [schemas/categories/](../../../../schemas/categories/) 实际 .py 文件数（market 88 + fundamental 12 + macro 2 + cross 1） |
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

> **v2.1.0 三层口径说明**：v0.2.0 的"38（37.3%）"实测即**消费层覆盖**（37 张，口径稳定——见 §2.2 口径修正）——真问题从未变化：消费方文档不描述表的用法；**规划层引用不等于消费覆盖**（§7.0.6 L2/L3 标准要求字段/下游逻辑/频率描述）。利用率 99.0% 健康——[thedataops.org 2026](https://www.thedataops.org/data-documentation/) 的 doc coverage 80% 基准针对消费级文档，本审查以消费层 35.9% 对齐该基准；行业对照 [modern-datatools.com 2026-04 Data Baselining](https://www.modern-datatools.com/blog/data-baselining-warehouse-lifecycle-2026) 三层基线法验证"先盘点真源再分层处置"路径，其"20% 表被活跃查询"企业常态反衬本仓库 99.0% 利用率异常健康。

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

> v2.1.0 以 git 提交态实测重排（任一文档命中口径，子串匹配）。v0.2.0 热度数字以未提交工作区为扫描对象不可复现（§2.2 声明）——如 `block_trade` 实测 7 次/2 文档（13/64 号），跌出前 15。通用名 `index`（441 次/43 文档）为子串假阳性，按 §3.3 惯例以全名 `market_index` 复核（3 次真实命中），不入榜。热度仅作参考，施工优先级以 §6 为准。

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

v0.1.0 §5.3 称 `macro_data`/`industry_class`/三大报表/`disclosure_plan`/`kline_weekly`/`kline_monthly` 仅 1-2 次引用。v2.1.0 实测复核：(1) 上述表全部已被 17/64 号**规划层覆盖**，`industry_class` 另有代码 59 次引用（消费层活跃）；(2) 但**消费级描述**仍缺——基本面三表（balance_sheet/income_statement/cashflow_statement）仅在规划层与 [15_data_feature_layer_spec](15_data_feature_layer_spec.md) 数据源清单出现，未在策略文档描述消费逻辑——基本面 alpha 信号链文档待建（§6.2 批次 B）；(3) v0.2.0 逐表计数以未提交工作区为扫描对象不可复现，v2.1.0 起以 git 提交态实测为准（§2.2 不可复现声明）。

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

**权重校准循环**（v0.4.0 新增，参考 [sigos.io 2026-06](https://www.sigos.io/blog/weighted-scoring-model)）：每波施工后对比高分表与低分表的实际文档价值产出——高分表未明显优于低分表 → 降 W2（5.0→3.0）；alpha_potential 主观性太强 → W3 降为 1.0（code_ref_count 已含此信号）。每波重评，避免静态模型失真。

**贝叶斯权重更新形式化（v1.0.0 新增）**：校准循环从"拍脑袋调权重"升级为概率化更新——`P(W|E) = P(E|W)×P(W)/P(E)`，先验 N(μ=当前值, σ=0.2×当前值)，似然用 MSE 建模，触发条件：**某权重分量的"预期 vs 实际"偏差连续 2 波超过 2σ** 才更新（非每波都调，避免 priority 排序抖动）。仅形式化定义不全量实施 MCMC（102 表×5 权重后验计算量过重，实际执行仍用启发式校准循环，贝叶斯作为理论依据）。与 §7.0.4 EWMA 联动：Q score 的 EWMA 持续偏离权重预期则触发对应权重的贝叶斯更新。

**跨波次优先级动态重评算法（v1.1.0 新增，融入 §7.0.6 验收闭环步骤 7）**：每波施工结束后执行——(1) 收集证据（各表 Q score / L3 抽检通过率 / 实际 effort 与 §7.0.8 Rubric 偏差 / 实际耗时 vs §7.0.3 CPM 估算）；(2) 证据驱动权重微调（风险表 Q 均 <7.0 → W2 上调 0.5；高低 code_ref 表 Q 无显著差异 → W1 下调 0.2）；(3) 批次归属动态调整**建议**（仅对未施工批次：期望型 Q 持续 <5.0 → 建议降级兴奋型批次后移；兴奋型 Q ≥8.0 且多文档引用 → 建议升级期望型批次前移；Kano 基本型不降级）；(4) 用微调后 W 重算未施工表 priority，输出 `priority_v{n+1}.csv`，变化幅度 >30% 的表标 ⚠️ 人工复核。**不做的**：不每波都调权重（仅贝叶斯触发条件满足时）、不自动调整批次归属（仅建议，§10 Q2 已裁定归集方式）、不回溯已施工表。

**为何不用 WSJF**（v0.5.0 新增）：[SAFe WSJF 2026-02](https://agility-at-scale.com/safe/wsjf-weighted-shortest-job-first/) 的 Time Criticality 为 10-100+ 人多团队 portfolio 排序设计，个人项目过重——RICE 变体保留，但**承认其缺失 Time Criticality**：风险模块表（`restricted_shares` 解禁前 30 日减仓）有时间窗口，RICE 不会因"解禁日临近"而提升优先级。可选混合模型 `priority_v2 = priority × time_criticality_factor`（事件表 2.0 / 危机触发表 1.5 / 常态 1.0 / 低时效 0.8）**不采纳**——Time Criticality 在文档施工场景退化为"风险模块优先"（已由 W2=5.0 覆盖），若解禁日临近需紧急补 `restricted_shares` 文档，直接人工提优先级即可。

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
> **v1.1.0 校准说明**：v0.4.0 示例表的 effort 值为估算值，与 §7.0.8 Rubric 量化标准不一致；v1.1.0 以 Rubric 为准重新计算，priority 相应调整。**批次归属不变**：Kano 基本型（risk_flag=Y）无论 RICE 分多少必须进批次 A；† `cb_iv` priority=1.0 < 1.5 阈值按 RICE 应进 D，但 §6.2 按消费方模块（26 号事件驱动）业务归集进 B——**Kano 分类层 + 业务归集优先于 RICE 排序**，RICE 仅决定批次内顺序。
>
> **v0.4.0 Confidence 影响仍成立**：`hog_futures_core` 因置信度 0.5（疑似采集模板继承）priority=1.0 → 批次 D——**Confidence 因子成功将"模板引用"从施工优先级中降权**。`concept_sector` 虽非风险模块但代码引用 30 次（最高）+ 置信度 1.0，priority=6.0 → 批次 A*（高热度但非风险，可灵活排入 A 或 B）。

**Confidence 滥用警告**（v0.6.0 新增）：2026 多篇 RICE 复盘指出最大反模式是"所有表 confidence 都标 0.5 图省事"——Confidence 变成常数失去区分力。反滥用措施：§3.5 自动判定替代人工标注；**Confidence 分布审计**（每波施工后 >70% 的表同分 → 触发警告重跑 §3.5）；对性质不确定的表走 §3.5 优先级 3（0.8）+ 人工抽查升/降级，不无脑标 0.5。

**Kano 分类层（v0.6.0 新增，补 RICE 的"需求类型盲点"）**：RICE 量化"做多少价值"，但不区分"必须做"vs"做了更好"。Kano + RICE 组合策略——**Kano 负责做正确的事（strategic），RICE 负责正确地做事（execution）**，Kano 作为 RICE 的**前置过滤器**：基本型需求无论 RICE 分多低都必须补文档。

**Kano 五类映射到 103 张表**（AI 可裁定，无需人决策——基于 project_memory 风险优先原则 + 代码引用性质）：

| Kano 类型 | 定义 | 本审查映射 | 103 张表中的代表 | 施工策略 |
|---|---|---|---|---|
| **基本型**（Must-be） | 不满足会导致严重后果——风险红线、生存底线 | 风险/回撤/kill_switch 相关表（risk_module_flag=Y） | `restricted_shares` / `share_unlock` / `etf_nav` / `limit_up_down` / `margin_trading` | **无论 RICE 分多少必须补**——RICE 仅决定批次内顺序，不决定是否做 |
| **期望型**（One-dimensional） | 满足度随覆盖度线性增长——核心 alpha 信号链 | 策略文档已显式消费但文档覆盖不足的表（code_ref≥10 + 已有策略文档） | `block_trade_detail` / `dragon_tiger` / `money_flow` / `concept_sector` / `index_constituent` | RICE 排序补文档，priority ≥ 1.5 进批次 B/C |
| **兴奋型**（Attractive） | 做了有增量 alpha，不做也无损——探索性 alt data | 代码在用但无策略文档消费、alpha 价值待验证的表 | `cb_iv` / `analyst_forecast` / `msci_adjustment` / `hog_futures_core` | RICE 排序，priority < 1.5 进批次 D，仅记录代码用法不强制补策略 |
| **无差异型**（Indifferent） | 做不做都没影响——真闲置 | 文档+代码均零引用 | `dividend_tax_node` / `index_meta`（待激活）/ `msci_adjustment`（待激活） | §6.1 生命周期决策——DEPRECATED→SUNSET→REMOVED 或补建激活 |
| **反向型**（Reverse） | 做了反而降低满意度——过度工程 | 不适用（本审查无反向型——补文档不会降低满意度，但"为凑覆盖率浅覆盖"是隐性反向，由 §7.0.4 Q score 防范） | — | — |

**Kano 与 RICE 的协作流程**：

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

**为何不用完整 Kano 问卷**：完整 Kano 需双向问卷+统计显著性样本，适合产品功能排序，不适合个人项目数据表文档补齐（无用户可问卷）——用**规则映射替代问卷**（risk_module_flag=Y→基本型 / code_ref≥10→期望型 / 其余→兴奋型），是 Kano 思想的轻量实现。

**Consequence Ranking 批判与辩护（v0.7.0 新增）**：[dualoop.coach 2026-03](https://www.dualoop.coach/blog/rice-vs-ice-vs-moscow-prioritization/) 对 RICE/ICE/MoSCoW 提出系统性批判，主张用 **Consequence Ranking**（按"做/不做的后果"排序）替代公式打分：

| 批判 | 原文要点 | 对本审查的适用性 |
|---|---|---|
| Non-commensurable variables | Impact 和 Effort 单位不同，不能 apples × orchards | ⚠️ 部分适用——本审查 impact/effort 均已归一化为无量纲加权综合分，非"apples × orchards"，但归一化过程（W1-W5 权重）本身引入主观性 |
| Confidence collapses domains | 80% in Impact ≠ 80% in Effort，框架假装可比 | ✅ 不适用——本审查 Confidence 只作用于 impact（代码引用性质置信度），不作用于 effort（§7.0.8 Rubric 量化），单域无跨域折叠 |
| Weighting is invisible | 真实成本含机会成本/团队焦点/技术债，不止 Effort | ⚠️ 部分适用——effort 只含 doc_complexity+coupling 不含机会成本；但个人项目无团队焦点竞争，机会成本退化为"priority 排序本身"（高分先补=已内化） |

辩护与吸收：103 张表批量排序需可计算公式——Consequence Ranking 需对每张表写"做/不做的后果"叙述（103×2=206 段人工写作，成本更高），RICE 的"虚假精确性"在批量排序场景是可接受近似（priority=8.4 vs 7.5 的差异不决定"做不做"，只决定"先做谁"）；**Kano 分类层已吸收"后果导向"思想**——基本型="不做有严重后果"（风险红线），即 Consequence Ranking 的轻量实现；dualoop 的场景是"2-4 个战略选项深度决策"，本审查是"103 张表批量排序"，[pmtoolkit.ai 2026-02](https://pmtoolkit.ai/learn/prioritization/prioritization-frameworks-comparison) 确认 RICE 适合"10-100 features"批量排序。

**SQALE 技术债视角（v1.5.0 新增，参考 [technicaldebtcalculator.com 2026](https://technicaldebtcalculator.com/frameworks)）**：RICE 回答"先补谁"（微观排序），SQALE 回答"整体文档债务有多严重"（宏观健康度，两者正交不替代）。**TDR = (Σ effort of 文档缺失表) / (Σ effort of 全部表) × 100**——当前估算：缺失 59 张×avg effort 5.0≈295，已有 44 张×avg 4.0≈176，**TDR≈63%**。

**SQALE A-E 评级映射**（technicaldebtcalculator.com 2026 Bands）：

| 评级 | TDR 范围 | 状态 | 本审查施工指导 |
|---|---|---|---|
| A | 0-5% | Healthy | 文档覆盖完善，仅维护增量 |
| B | 5-10% | Manageable | 少量缺口，随施工波次自然消除 |
| C | 10-20% | Concerning | 需有计划补缺口，但不紧急 |
| D | 20-50% | Critical | 需优先施工，部分表影响开发效率 |
| **E** | **>50%** | **Severe** | **当前状态（TDR≈63%）——文档债务严重，P0 风险表必须先补** |

Annual-Interest（不补的年消耗）用 Kano 分类代理：基本型=高利息"策略误判风险"（风险表 Breaking-Point≈1-3 个月，远短于施工波次间隔，必须第一波补）/期望型=中利息"开发效率损耗"/兴奋型=低利息"探索机会成本"/无差异型=0。Fowler 四象限映射：批次 D 暂缓=Deliberate+Prudent；v0.1.0 误判=Inadvertent+Prudent（v0.2.0 已修正）；无 Reckless 两类。SQALE 的 Annual-Interest 补入了 RICE 缺失的"不补的代价"维度。不引入 Financial Impact 框架（需团队工时成本，个人项目不适用，§9）。

**Cognitive Debt + AI-Generated Debt 新类别（v1.6.0 新增，参考 [Exceeds AI 2026-06-09](https://blog.exceeds.ai/ai-technical-debt-tracking-workflow/) + [dupple.com 2026-04-03](https://dupple.com/blog/what-is-technical-debt-in-software-development)）**：Fowler 四象限无法归类 **AI-Generated Debt**（AI 生成内容无人完全拥有/理解，无决策点）——本审查文档施工由 AI 执行（§7.0.2 反推+§7.0.1 模板），天然存在此风险。**Cognitive Debt**（Margaret-Anne Storey）：AI 反推文档快于人 L3 抽检（59 张草稿数小时可生成，L3 每波仅 2-3 张），生产速度>理解速度导致未抽检的表文档人可能从未读过，无人能完整叙述 103 张表的覆盖状态（需 §7.0.9 看板+§5.1 指标做全局代理）。

**AI-Generated Debt 度量指标**（融入看板采集）：

| 指标 | 定义 | 采集方式 | 健康阈值 |
|---|---|---|---|
| **AI-touched doc cycle time** | AI 生成文档到人 L3 抽检通过的时间 | `construction_kanban.csv` 的 construction_date 到 l3_result=pass 日期 | ≤14 天（与 MTTR 对齐） |
| **Rework rate** | 30 天内 AI 生成的文档被重写的比例 | git log 统计 30 天内同一文档的二次修订 commit | <20%（>20% 说明 AI 生成质量不稳定） |
| **L3 抽检覆盖率** | 已 L3 抽检的表数 / AI 生成文档的表数 | `construction_kanban.csv` 的 l3_result != '-' 计数 | ≥30% |

与 §7.0.4 Q score 互补：Q score 度量"单次施工质量"，Rework rate 度量"AI 生成内容稳定性"（高 Q+高 Rework=单次好但不稳定；低 Q+低 Rework=稳定地差）。不引入完整 AI Debt Score（doc churn 信号稀疏不足以支撑加权公式）。

**Binarly 权重再分配算法（v1.6.0 新增，参考 [binarly.io 2026-04-13](https://www.binarly.io/blog/binarly-risk-score-introduction)）**：RICE 某分量缺失（如 alpha 无法评估、code_ref=0）时，缺失分量的 W 按比例再分配给剩余分量，避免"缺失=0 分"拉低总分——alpha 缺失：W1_new=1.33, W2_new=6.67（风险权重进一步升高，符合风险优先）；code_ref 缺失：W2_new=5.71, W3_new=2.29。`dividend_tax_node` 示例：code_ref+alpha 均缺失 → W1+W3=3.0 全给 W2=8.0，但 risk_flag=N(0) → priority 仍为 0，**结论正确**（真闲置表进 §6.1 而非施工队列）。risk_flag=Y（Kano 基本型）时不触发再分配。

**SATD 跨制品传播优先级（v1.7.0 新增，参考 [arXiv 2603.15883v2 PEARC 2026](https://arxiv.org/html/2603.15883v2)）**：§10 开放问题、§6.2 批次 D 暂缓、§9"不做什么"本质都是 **SATD**（Self-Admitted Technical Debt）。传播链长度作为 RICE confidence 调整因子：`adjusted_confidence = base_confidence × (1 + 0.1 × (chain_length - 1)) × sentiment_factor`（comment=1/commit=2/PR-issue=3/暂缓决策=4；负面情感×1.2，中性×1.0）——暂缓表（chain_length=4+负面）confidence 被上调（传播链长=高优先级债）。用 grep+正则规则映射替代完整 NLP 分类模型（数据量不足，§9）；Kano 基本型表的 SATD 传播链天然长，SATD 是 Kano 的量化补充。

**AI 技术债 7 类映射（v1.7.0 新增，参考 [Institute of AI PM 2026-01-25](https://www.institutepm.com/knowledge-hub/ai-technical-debt-template)）**：

| AI 技术债 7 类 | 定义 | 本审查覆盖 | 状态 |
|---|---|---|---|
| 1. Data Debt | 数据陈旧/未文档化/无验证/无版本 | §2.2 Data Contract Semantics 层 + §6.0 RICE + §7.0.4 Q score completeness | ✅ 本审查核心 |
| 2. Model Debt | 模型版本过时/无解释性/复杂度过高 | 不适用（本审查无 ML 模型，design_memos 是文档非模型） | N/A |
| 3. Pipeline Debt | ETL 脆弱/手动步骤/不可复现 | §3.4 Detective 扫描 + §7.0.5 增量更新（文档管道） | ✅ 已覆盖 |
| 4. Monitoring Debt | 无漂移检测/无告警/盲区 | §3.4 Model drift 分类 + §7.0.4 SPC + §6.1 消费链路主动监控 | ✅ 已覆盖 |
| 5. Testing Debt | 无评估套件/未测边缘用例/无回归 | §7.0.6 L3 语义抽检 + §7.0.9 看板验收 | ✅ 已覆盖 |
| 6. Documentation Debt | 部落知识/无决策日志 | §6.0 SQALE TDR + Cognitive Debt + AI-Generated Debt + Q score | ✅ 已覆盖 |
| 7. Infrastructure Debt | 过度配置/供应商锁定 | §9 不引入外部数据目录/不引入 ODCS 工具链 | ✅ §9 已裁定 |

**映射结论**：已覆盖 7 类中的 6 类（1/3/4/5/6/7），第 2 类不适用——**无需新增独立债务类别**，v1.5.0 SQALE + v1.6.0 Cognitive/AI-Generated Debt + v1.7.0 SATD 传播已覆盖全部适用类别。

### 6.1 真闲置表（v2.1.0 实测仅 1 张 / 4 阶段生命周期决策 / v0.8.0 补消费链路主动监控 / v1.0.0 补调度感知差异化弃用阈值+MIN_AGE_DAYS 安全过滤）

v2.1.0 五源实测（design_memos 46 篇 + src/zephyr/ 代码 + config/ + tasks.yaml + 注册表 yaml）：v0.2.0 的 3 张"真闲置"中，`dividend_tax_node` 与 `msci_adjustment` 已被 17/64 号规划层覆盖（转入 §6.1b），**仅 `index_meta` 保持五源全零引用**。采用 [4 阶段生命周期](https://oneuptime.com/blog/post/2026-01-30-mlops-feature-versioning/view)（2026-01，ACTIVE→DEPRECATED→SUNSET→REMOVED）+ [数据弃用 7 步流程](https://atlan.com/know/data-deprecation-process/)（2026-03）决策，替代二元"归档/保留"：

| # | 表名 | 稳定 path | 生命周期建议 | 理由 |
|---|---|---|---|---|
| 1 | `index_meta` | [market_index_meta](../../../../schemas/categories/market_index_meta.py) | → DEPRECATED 观察期（默认建议，待人裁定） | 指数元数据——v0.2.0"补建激活"建议的前提是 `index_constituent` 代码 23 次引用需 meta 配合；v2.1.0 实测 `index_constituent` 已有规划层覆盖、`index_meta` 五源全零，补建价值取决于 62 号 universe/benchmark 注册表是否需要 meta 字段——**若 62 号 P1-A/B 施工不需要 → 确认 DEPRECATED**；若需要 → 转 ACTIVE 补建（§10 Q1） |

> **弃用流程**（[atlan.com 2026-03](https://atlan.com/know/data-deprecation-process/)）：DEPRECATED 标记 → 影响分析（grep 下游消费者）→ 无人认领 → SUNSET（只读 1 季度）→ REMOVED（删 DDL + 采集脚本）。`index_meta` 当前零下游消费者，可直接进 DEPRECATED 观察期。

#### 6.1b 代码零引用但规划已登记（v2.1.0 新增类别，6 张——采集未施工）

以下 6 张表 DDL 已入 git（2026-08-11 提交）且被 17/64 号规划层登记，但 src/zephyr/ 代码、config/、tasks.yaml、注册表**全零引用**——不是"文档缺口"（§6.2）也不是"真闲置"（§6.1），而是**采集/消费链路未施工**：

| # | 表名 | 稳定 path | v2.1.0 实测状态 | 默认建议（待人裁定，§10 Q8） |
|---|---|---|---|---|
| 1 | `dividend_tax_node` | [market_dividend_tax_node](../../../../schemas/categories/market_dividend_tax_node.py) | DB 层派生 VIEW（从 rights_issue 实时派生），无 Python 引用属正常 | **免归档**——VIEW 零存储零采集成本，标 dormant 保留；v0.2.0 的 DEPRECATED 建议撤销（当时误判为"需采集的实体表"） |
| 2 | `msci_adjustment` | [market_msci_adjustment](../../../../schemas/categories/market_msci_adjustment.py) | 规划已登记（17/64 号），采集未施工 | 保留 DDL + 标 `status: dormant`——MSCI 调仓事件有 alpha 价值（v0.2.0 论证保留），待 26 号事件驱动启用时补采集 |
| 3 | `index_adjustment` | [market_index_adjustment](../../../../schemas/categories/market_index_adjustment.py) | 规划已登记，采集未施工（v0.2.0"代码 17 次引用"不可复现） | 同上——指数调仓事件是 26 号既定事件源，待启用时补采集 |
| 4 | `ipo_schedule` | [market_ipo_schedule](../../../../schemas/categories/market_ipo_schedule.py) | 规划已登记，采集未施工（v0.2.0"代码 12 次引用"不可复现） | 同上——IPO 日程事件待启用 |
| 5 | `margin_target_adjustment` | [market_margin_target_adjustment](../../../../schemas/categories/market_margin_target_adjustment.py) | 规划已登记，采集未施工（v0.2.0"代码 14 次引用"不可复现） | 同上——两融标的调整事件待启用 |
| 6 | `stock_valuation` | [market_stock_valuation](../../../../schemas/categories/market_stock_valuation.py) | 2026-08-11 DDL 新增，规划层提及（1 次），采集未施工 | 同上——与 `daily_valuation`（代码 42 次活跃）的口径分工待 15 号明确；注意 MIN_AGE_DAYS=30 安全过滤适用（新建表 30 天内不判闲置） |

> **类别边界**：本类表不进 §6.2 消费文档施工队列（无代码消费可反推，§7.0.2 反推无源），仅登记注册表 + 标 dormant。若后续补采集施工（Provider 任务落地），自动转入 §6.2 队列。与 §6.1 真闲置的区别：本类有明确业务规划（17/64 号登记在册），`index_meta` 无任何消费方规划。
>
> **对 v0.2.0"代码引用"数字的处置**：本类 4 张表（msci/index_adjustment/ipo_schedule/margin_target_adjustment）v0.2.0 报代码引用 0-17 次不等，v2.1.0 五源实测全零——以实测为准（§2.2 不可复现声明）。若采集脚本曾存在后被删除，其 git 历史可查，不影响当前"采集未施工"判定。

**消费链路主动监控（v0.8.0 新增，参考 [simor consulting 2026-04](https://simorconsulting.com/blog/the-data-pipeline-that-cost-50kmonth--and-the-audit-that-found-why)）**：simor 金融数据平台审计发现 **31% 计算花在零消费者管道上**——根因是"跟踪任务依赖但未跟踪消费依赖"（管道被创建后从不重新评估）。其三部分修复系统映射：

| simor 组件 | 原文 | 本审查映射 | 当前状态 |
|---|---|---|---|
| 消费注册表 | 每个管道必须注册至少一个活跃消费者 | data_asset_registry 的 `consumers` 字段 | ⏳ 62 号 P1-B 待施工——补文档时为每张表登记 `consumers: [文档列表]` |
| 监控层 | 跟踪实际消费（查询日志/API 调用/仪表板刷新） | ClickHouse `system.query_log` + `tasks.yaml` 调度日志 | ⏳ v0.8.0 补入下方主动监控规则（两源 PowerShell 脚本即可，无需专门监控基础设施） |
| 自动标记+暂停 | 无消费者 30 天标记 + 60 天暂停 | §6.1 的 DEPRECATED→SUNSET 流程 | ✅ 已有但被动——补"30 天零查询自动标 ⚠️"规则；**不采纳"60 天自动暂停"**（金融数据风险过高，保留人工确认 SUNSET→REMOVED，§10 Q1 决策方=人） |

**v0.8.0 补强：主动消费监控规则**（补入 §6.1 生命周期决策）：

```
主动监控规则（替代被动等待）：
1. ClickHouse system.query_log 每周扫描 → 统计每张表过去 30 天的 SELECT 次数
2. tasks.yaml 调度日志每周扫描 → 统计每张表对应 ingestion task 的实际执行次数
3. 若某表过去 30 天 query_count=0 AND task 执行但输出无下游消费 → 自动标 ⚠️ 疑似闲置
4. ⚠️ 疑似闲置表进入 §6.1 DEPRECATED 观察期（不需人工发现，系统主动标记）
5. 观察 1 季度（90 天）仍无消费 → 确认 SUNSET → 按 §7.5 归档流程执行
```

与 §7.0.4 timeliness 联动：30 天零查询 → timeliness time_decay=0.5（Q 分下降）+ 主动标 ⚠️ 疑似闲置 → 双重信号触发复核。

**调度感知的差异化弃用阈值（v1.0.0 新增，参考 [有赞无用数据下线自动化 2026-08-07](https://blog.csdn.net/SunnyYoona/article/details/130119357)）**：统一"30 天零查询"阈值对月级/季级表是假阳性源（月级表本就 30 天才调度一次）——按调度级别差异化 lookback：

| 调度级别 | 对应表 | lookback 周期 | 触发条件 | 理由 |
|---|---|---|---|---|
| 盘后日级 | `kline_daily` / `money_flow` / `limit_up_down` 等行情类 | 15 天 | 15 天内 query_count=0 AND task 执行但无下游消费 | 日级表每天应被消费，15 天零查询=明确闲置（有赞天级 15 天阈值） |
| 周级 | `kline_weekly` / `stock_valuation` 等周更类 | 6 周 | 6 周内 query_count=0 AND task 执行但无下游消费 | 周级表每周应被消费，6 周零查询=明确闲置（有赞周级 6 周阈值） |
| 月级 | `kline_monthly` / `financial_statement` 等月更类 | 3 个月 | 3 个月内 query_count=0 AND task 执行但无下游消费 | 月级表每月应被消费，3 个月零查询=明确闲置（有赞月级 3 个月阈值） |
| 季级 | `financial_report` / `rights_issue` 等季更类 | 6 个月 | 6 个月内 query_count=0 AND task 执行但无下游消费 | 季级表每季应被消费，6 个月零查询=明确闲置（有赞季级 6 个月阈值） |
| 事件触发 | `ipo_schedule` / `index_adjustment` / `msci_adjustment` | 不适用 | 事件发生后 1 个周期无消费 → 标 ⚠️ | 事件表无固定调度，按"事件发生→消费窗口"判定 |

**MIN_AGE_DAYS 安全过滤（v1.0.0 新增，参考 [Databricks 2026-06](https://www.databricksters.com/p/reclaim-spend-from-idle-databricks)）**：差异化阈值判定前执行安全过滤——(1) **MIN_AGE_DAYS=30**：表创建（git 首次提交日）<30 天 → 跳过闲置判定（新表施工期零查询正常）；(2) **PROTECTED_TABLES 白名单**（Kano 基本型风险红线表豁免：restricted_shares / share_unlock / etf_nav / limit_up_down / margin_trading / kline_daily / trade_calendar——"危机时才用"的 dormant table 不应误判为闲置）；(3) 通过过滤后进入差异化阈值判定 → 标 ⚠️ 疑似闲置 → §6.1 DEPRECATED 观察期。不采纳有赞自动下线（金融数据风险过高，保留"标 ⚠️ → 人工确认"流程）。

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

> v0.5.0 补入 5 个施工算法子节（§7.0.1-§7.0.5），使施工可重复可验证。验收闭环（v0.3.0/v0.4.0）移至 §7.0.6。

#### 7.0.1 补文档标准模板（per-table template，v0.5.0 新增）

> 参考 [RepoDoc arXiv 2604.26523 2026-04](https://arxiv.org/html/2604.26523v1) 的 API Coverage + Doc Information 5 维度，定义每张表补文档的**最小内容模板**。避免"补了表名但没写字段含义/消费频率/下游逻辑"的浅覆盖。

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

> §6.2 的缺口表"代码已用，补文档"——但"代码用法"如何提取为文档内容？v0.5.0 补入**代码反推算法**：从代码引用位置反向提取消费模式，生成文档草稿，避免人工逐张读代码。

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

**多消费方冲突解决算法**（v0.6.0 新增，补 §7.0.2 的"冲突无解"缺口）：当多消费方对同一表的字段/频率/逻辑描述冲突时（如 `etf_nav` 在 37 号应描述"折溢价 >2% 触发预警"、在潜在套利策略应描述"折溢价套利信号"——同一字段不同语义），按消费方优先级裁定：

| 优先级 | 消费方类型 | 裁定权重 | 冲突时处理 |
|---|---|---|---|
| P0 | 风险/回撤/kill_switch 文档（Kano 基本型） | **最高** | 冲突时以此为准——风险语义优先于 alpha 语义 |
| P1 | 策略文档（Kano 期望型，已有显式消费） | 中 | 若与 P0 冲突，标注"风险视角 vs alpha 视角"双语义，不强制统一 |
| P2 | 数据/因子工程总纲（15 号） | 中 | 作为"数据源清单"中立描述，不涉及消费语义 |
| P3 | 注册表文档（62 号） | 低 | 仅登记元数据（表名/业务域/状态），不描述消费逻辑 |
| P4 | 待建文档（无消费方） | 最低 | 仅记录代码用法，不裁定语义 |

**冲突解决流程**：(1) 反推产出 N 份消费方草稿；(2) 冲突检测——字段集相同且逻辑一致→各文档直接写入；字段集不同→各文档写入各自字段子集；字段集相同但逻辑冲突→进步骤 3；(3) 以最高优先级消费方（P0 风险文档）语义为"权威描述"，低优先级文档标注"⚠️ 本文档消费视角与 <P0 文档> 不同：P0 视角=<风险预警>；本文档视角=<alpha 信号>；两者均合法，不强制统一"——**不删除低优先级描述**（避免风险视角吞并 alpha 视角导致信号链断裂）；(4) 各文档按裁定结果写入并跨文档引用对方视角。示例（`etf_nav`）：37 号 P0"折溢价 >2% 盘后批量预警"为权威描述；24 号 P1（假设性）"折溢价套利信号盘中实时"标 ⚠️ 双语义，两者均写入。**不做的**：不强制统一多消费方描述（不同消费场景天然不同语义）；不做"权威消费方"单点真理；不自动裁定（AI 仅标 ⚠️+给优先级建议，最终写入人工确认）。

**DocAgent 多智能体远期升级路径（v0.7.0 新增）**：[DocAgent arXiv 2504.08725v3 Meta AI 2025-05](https://arxiv.org/html/2504.08725v3/) 的 5 智能体协作文档生成系统：

| 智能体 | 职责 | 对应本审查当前实现 |
|---|---|---|
| Reader | 读取代码文件，提取 AST + 依赖关系 | §7.0.2 步骤 1-2（grep + ±10 行上下文） |
| Searcher | 搜索外部信息补充上下文 | §7.0.2 步骤 3（路由映射/调度配置提取） |
| Writer | 生成文档草稿 | §7.0.2 步骤 4（套用 §7.0.1 模板） |
| Verifier | 验证生成文档的准确性（Truthfulness） | §7.0.6 L3 语义抽检（人工）+ §7.0.4 Q score accuracy |
| Orchestrator | 拓扑排序，按依赖顺序处理 | §7.0.3 Kahn 算法拓扑排序 |

其拓扑处理顺序（Navigator）与 Truthfulness 评估和本审查高度对齐，**证明 lightweight 实现与学术 SOTA 核心思路一致**，差异仅在自动化程度。不当前采纳（5 智能体×59 张表 LLM 成本过高；多智能体编排需额外基础设施）；远期触发条件：design_memos 100+ 篇、L3 人工抽检成本上升时引入自动化 Verifier。其"增量上下文构建"（处理依赖模块时复用被依赖模块已生成文档作为上下文）是 §7.0.2 当前"每张表独立反推"的潜在升级点。

#### 7.0.3 表间依赖拓扑排序（v0.5.0 新增 / v0.9.0 补 Louvain 社区发现 / v1.0.0 补 CPM 关键路径 / v1.6.0 升级 Louvain→Leiden / v1.7.0 补 Temporal Coupling 隐藏依赖 / v1.8.0 补 commit-size 归一化+Sum of Coupling+min-heap 确定性排序+DFS 三色标记环路径提取）

> §6.2 按消费方模块分批，但未考虑表间依赖（如 `index_constituent` 依赖 `index_list`）。若先补依赖表再补被依赖表，被依赖表的"下游逻辑"字段无法引用未补的依赖表——导致返工。v0.5.0 补入拓扑排序，确保同批次内**被依赖表先补**。

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
3. 同层表按 §6.0 priority 降序补（高分先补）；**同 priority 用 min-heap 确定性打破平局**（v1.8.0 新增）——Kahn 队列改为按 (priority DESC, table_name ASC) 排序的优先队列，确保施工顺序**可复现**（参考 [spacecomplexity.ai 2026-05-24](https://spacecomplexity.ai/blog/topological-sort-algorithm)，O(V log V + E)）
4. 跨批次依赖（如批次 A 的 `etf_nav` 依赖批次 C 的 `etf_list`）：**先补 `etf_list` 的最小文档（仅表名+业务含义），再补 `etf_nav` 完整文档**——避免跨批次阻塞
5. **环检测**（v1.5.0 显式补入）：Kahn 天然支持环检测——`topo_order.csv` 行数 < 依赖图节点数 → 存在环；未被处理的入度>0 节点即环内节点。表间依赖不应存在环——检测到则标记 ⚠️ 架构异常，记入 `architecture_issue_registry.yaml`（ARCH 条目），人工裁定打破环（通常某条依赖是误标，如视图依赖误标为表依赖）

**环路径提取增强（v1.8.0 新增）**：Kahn 只能判定环存在性+定位环内节点集合，无法输出环的边路径（A→B→C→A 的具体环链）——v1.8.0 补 **DFS 三色标记法**（white/gray/black；gray 专区分"在当前 DFS 路径上"vs"已完成"，单一 visited 数组会把共享节点误判为环），O(V+E)，Kahn 检测到环后才运行（零常态开销），输出 `cycle_paths.csv` 供人工裁定。**Tarjan SCC 作为远期路径**（环数量>5 或环嵌套时升级，一次性识别所有 SCC+凝聚 DAG；102 表依赖图为树形/森林结构预期环 ≤2，当前不实施）。三层递进：Kahn 检测"有没有环"→ DFS 三色标记提取"环路径"→（环复杂时）Tarjan SCC 识别"所有 SCC"。

**实施**：拓扑排序脚本封装进 `scripts/audit_data_utilization.ps1`，输出 `topo_order.csv`（表名 × 拓扑层 × priority × 批次）；检测到环时额外输出 `cycle_warning.csv` + `cycle_paths.csv`。

**Leiden 社区发现用于批次聚类验证（v0.9.0 新增 / v1.6.0 升级 Louvain→Leiden）**：§6.2 人工批次+§7.0.3 Kahn 都是**人工预设的批次边界**——社区发现可从依赖图自动发现**紧耦合表簇**（同一社区应作为一个整体补文档，避免跨批次阻塞）。选型 **Leiden**（[metricgate.com 2026-02-03](https://metricgate.com/blogs/community-detection-louvain-vs-leiden/) 确认其修复 Louvain 两大 bug：分辨率限制——倾向误合小社区；断连社区——社区内部可能不连通；γ 参数可调细粒度，2026 年已成行业共识；Louvain 为降级备选；Girvan-Newman/谱聚类 O(n³) 或需预设 k，Infomap 过复杂，均不适用）。应用流程：构建表间依赖图 G=(V,E)（边权重：1=派生/2=外键/3=同族 DDL 继承）→ 运行 Leiden（γ=1.0）→ 对比人工批次 A/B/C/D 与社区划分——一致则验证批次边界合理；某社区跨批次→应合并到同批次；某批次含多个小社区→可拆子批次并行。预期社区（指数族/板块族/概念族/ETF 族/可转债族/行情核心）与批次 A/B/C 高度重合。**为何不替代人工批次仅作验证**：社区发现按依赖密度分批不含**业务优先级**语义（风险优先原则）——人工批次保证"风险表先补"，Leiden 验证"批次内表是否真紧耦合"（发现"批次内表零依赖"说明是凑数批次应拆分）。实施：`scripts/community_detection.py`（需 `pip install python-igraph leidenalg`），输出 `community_map.csv` 与 `topo_order.csv` 交叉验证。

**Temporal Coupling 隐藏依赖检测（v1.7.0 新增 / v1.8.0 增强，参考 [codebase-memory-mcp #928 2026-07-07](https://github.com/DeusData/codebase-memory-mcp/issues/928)）**：Kahn 依赖**声明显式依赖**、Leiden 依赖**静态依赖图**——两者只看"代码里写了什么"。Temporal Coupling 通过 git log co-change 分析发现**动态隐藏依赖**（无 DDL 依赖但频繁在同一 commit 中修改的表对）：

```
1. 提取 commit→files 映射：git log --name-only -- schemas/categories/ src/zephyr/
1.5 commit-size 归一化过滤（v1.8.0，参考 [Archy #131](https://github.com/hslee16/Archy/issues/131)——"large commits couple everything"是首要假阳性源）：
    若 |commit.files| > MAX_FILES_PER_COMMIT=15（本仓库 103 表的 ~15%）→ 剔除该 commit，输出 filtered_commits.csv 供审计
2. 构建共现矩阵 co_occurrence[A][B]（commit 同时修改 A 和 B 的文件 → +1）
3. Jaccard 时序耦合度：temporal_coupling(A,B) = co_occurrence[A][B] / |commits(A) ∪ commits(B)|
   （分母用并集已天然惩罚"高频改 A 偶尔碰 B"的假阳性；CodeScene 三信号中仅采用信号 (a) 同一 commit co-change——
    个人+AI 项目信号 (b) 程序员维度无区分力、信号 (c) 无 ticket 系统）
3.5 Sum of Coupling 聚合度（v1.8.0）：sum_of_coupling(A) = Σ temporal_coupling(A,B) for all B≠A
    → 高 SoC=枢纽表（变更牵连多表文档同步，施工优先关注），低 SoC=孤岛表（可独立施工），与 §5.2 热度交叉验证
4. 识别隐藏依赖：temporal_coupling(A,B) ≥ 0.5 且 A→B 不在静态依赖图 → 标 ⚠️ 隐藏依赖
   → 输出 hidden_dependency.csv（table_A × table_B × coupling_score × is_in_static_graph × SoC_A × SoC_B）
```

预期发现的隐藏依赖：`kline_daily`↔`money_flow`（~0.8）、`restricted_shares`↔`share_unlock`（~0.9，同源采集一起改）、`dragon_tiger`↔`dragon_tiger_seat`（~0.95）；`kline_daily`↔`kline_daily_hfq`（~0.99 但已在静态图）。**与 Kahn/Leiden/CPM 的关系**：Kahn 解决顺序、Leiden 解决静态分组、Temporal Coupling 解决动态隐藏依赖、CPM 解决工期——四者正交可叠加（施工调度四件套）。Temporal Coupling 可能产生假阳性（同一 sprint 任务一起改但业务无依赖）需人工复核，仅作验证不替代 Leiden。实施：`scripts/temporal_coupling.py`。**冷启动约束**：schemas/categories/ 相关 commit 数 < 50 时统计不显著——仅记录 co_change raw count，不计算 coupling score。

**CPM 关键路径识别（v1.0.0 新增，参考 [CPM 2026](https://symplprocess.com/learn/critical-path-method)）**：Kahn 保证"被依赖表先补"但不识别**关键路径**——批次内最长依赖链决定总工期，TF=0 的表延误则全批延期。计算步骤：估算 duration（§7.0.8 effort × 2 人天/分）→ 前推 ES/EF（ES=max（前置 EF)，EF=ES+duration）→ 后推 LS/LF（LF=min（后置 LS)，LS=LF-duration）→ 总时差 TF=LS-ES=LF-EF → TF=0 的表组成关键路径。

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
```

施工指导：**关键路径表（TF=0）优先分配施工精力**（单线程施工先做关键路径最小化总工期）；非关键路径表可在间隙并行补；跨批次关键路径工期决定下一波最早开始时间。与 Kahn 正交（Kahn 解决顺序、CPM 解决工期，Kahn 是 CPM 前置——CPM 的前推/后推依赖 Kahn 产出的无环拓扑序）。实施：封装进 `scripts/audit_data_utilization.ps1` 拓扑排序后步骤，输出 `critical_path.csv`（表名 × ES × EF × LS × LF × TF × is_critical）。

#### 7.0.4 文档质量度量（Q score，v0.5.0 新增 / v0.6.0 升级 timeliness 为指数衰减 / v0.7.0 补乘法模型对比+高斯衰减 / v0.9.0 补 Syntropy+Doc-Entropy Ratio / v1.0.0 补 SPC EWMA/CUSUM 趋势分析）

> §7.0.6 验收闭环的 L1/L2/L3 是"通过/不通过"的二元判定，无法度量"文档质量高低"。v0.5.0 补入**文档质量分 Q**（0-10 分），参考 [DataQ 框架](https://publicationslist.org/data/jorge-martinez-gil/ref-175/dataq.pdf) 四维 + [sustainablecatalyst 2026-06](https://sustainablecatalyst.com/documentation-model-cards-and-datasheets-for-algorithms/)。v0.6.0 将 timeliness 升级为**指数衰减新鲜度**——"昨天编辑的文档也可能结构上过时"（若系统在编辑后一小时变更），timestamp 不等于 freshness。

**Leading vs Lagging 指标区分（v1.5.0 新增，参考 [affine.pro 2026-07-10](https://affine.pro/blog/knowledge-base-metrics)）**：Lagging（回顾性，度量现状）=Q score / L3 通过率 / 看板 Done 计数 / §6.0 SQALE TDR；Leading（前瞻性，预警未来）=§3.4 Detective 扫描 / SPC EWMA 趋势 / Nelson Rules 模式 / Model drift 数据漂移 / §6.0 贝叶斯权重偏差。只有 lagging→响应滞后，只有 leading→不知当前严重度；与 MTTD/MTTR 联动（MTTD 短=leading 有效，MTTR 短=lagging 有效）。

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
      timeliness = (0.7×0.3 + 0.3×0.25) × 10 = 2.85（需返工）
  - 示例：代码 10 天前变更已同步 → semantic=1.0, age=10, decay=0.79
      timeliness = (0.7×1.0 + 0.3×0.79) × 10 = 9.37（达标）
```

**为何用指数衰减而非二元**：二元 timeliness 在 age=1 天和 age=89 天同分——但 89 天前未同步的文档危险得多（代码已漂移更远）；指数衰减让"长期未同步"的 Q 分持续下降触发自动返工，避免"未同步但 Q=7 凑合用"的假达标。

**加法模型 vs 乘法模型对比（v0.7.0 新增）**：本审查 `α × semantic + (1-α) × time_decay` 是**加法模型**；[Milvus 2.6 Time-aware Ranking 2025-11](https://m.aitntnews.com/newDetail.html?newId=19523) 用**乘法模型** `similarity × decay_score`（时效性极低时彻底归零）——乘法适合**检索排序**（旧文档沉底），加法适合**文档质量评估**（旧文档语义价值不应被时效归零，如 16 号指标文档 3 年未改仍有效）。**Q score 保留加法模型**；若未来接入 RAG 检索系统，检索层改用乘法模型。**高斯衰减备选**（铃形曲线，初期衰减比指数慢）不符合"代码变更后应快速感知"的需求——保留指数衰减，高斯/线性作为备选记录。

**参数敏感性警告（v0.7.0 新增，参考 [Temporal RAG arXiv 2509.19376v2 2026-06](https://arxiv.org/html/2509.19376v2)）**："Freshness via a recency prior is real but partial and **parameter-sensitive**, not solved"——`half_life = 30 天` 是基于月更节奏的初始估计**未经实证校准**。第一波施工后应校准：对比"实际被发现过时的文档 age"分布（多数 15 天内被发现 → half_life 降为 15；多数 60 天后 → 升为 60），纳入 §6.0 权重校准循环每波重评。

**Q score 阈值**：
- `Q ≥ 7.0` → 文档质量达标（计入覆盖率分子）
- `4.0 ≤ Q < 7.0` → 需补强（不计入覆盖率，标 ⚠️）
- `Q < 4.0` → 需返工（L3 抽检未过或模板字段缺失 >50%）

**Q score 与覆盖率的区别**：覆盖率=有文档的表数/总表数（二元，有无）；Q score=文档质量高低（连续，好坏）——**覆盖率 97% 但平均 Q=3.0 = 全是浅覆盖，比覆盖率 50% 但 Q=9.0 更糟**，Q score 防止"为凑覆盖率而浅覆盖"。

**度量频率**：每波施工后对当波补的表评 Q score，写入 `docs/_audit/quality_score.csv`，当波目标平均 Q ≥ 7.0。**timeliness 维度每日重算**（age_days 随时间增长），Q 跌破 7.0 的表标 ⚠️ 待复核——避免"施工时 Q=9，半年后 Q=4 但无人知晓"的静默腐烂。

**Syntropy 编码会话级新鲜度（v0.9.0 新增，参考 [Syntropy 2025-12](https://github.com/delorenj/syntropy)）**：纯时间驱动的 time_decay 存在**假阴性**——代码 90 天没改（稳定），文档也没改，time_decay=0.125 触发不必要的 ⚠️。补入 `session_factor` 修正因子：

```
time_decay_corrected = time_decay × session_factor
session_factor：code_sessions_since_sync = 0（代码未变更）→ 1.0（不衰减）
              1-3（少量变更）→ 0.9 / 4-10（中量）→ 0.7 / >10（大量）→ 0.5
额外 boost：semantic_alignment=1.0（已同步）且 code_sessions=0 → timeliness_final = min(10, timeliness + 0.5)
```

保留 time_decay 不完全替换为 session_factor：纯 session 驱动有假阳性（代码没变但外部环境变了——ClickHouse 版本升级/供应商 API 变更）——**双因子乘法**兼顾：时间驱动防外部环境漂移，会话驱动防代码稳定时的假阴性。

**Doc-Entropy Ratio 复合度量（v0.9.0 新增，参考 [SITS2026 2026-04](https://blog.csdn.net/LogicShoal/article/details/160023770)）**：`doc_entropy_ratio = avg_lag_days / reference_count_30d`（滞后天数/30 天被引用次数）——将"新鲜度"与"使用频率"复合。行业基准：AI-Native=0.14 / Legacy=4.62 / Pre-AI=12.8。特殊处理：reference_count=0（零引用表）时 ratio 设为 0（滞后但无人引用，熵影响为零）。价值：Q score timeliness 只度量"文档多旧"，Doc-Entropy 复合"旧 × 无人用"——高 ratio 的表优先补（滞后多+引用高=影响大）。暂不融入 RICE 公式（避免过度复杂化），仅作为补充指标记录在 `quality_score.csv` 供人工优先级复核。

**Q score 趋势分析：SPC 控制图（v1.0.0 新增，参考 [AIAG-VDA SPC Manual 2026 July](https://leoardent.com/2026/07/what-is-new-in-the-aiag-vda-spc-manual-key-changes-explained/)）**：点态测量无法检测**渐进式质量退化**（Q 从 9.0→8.5→8.0→7.5→7.1 连续 5 波下降，每波都"达标"但趋势恶化）。三图联用：

```
EWMA_t = λ × Q_t + (1-λ) × EWMA_{t-1}    # λ=0.2（AIAG-VDA 推荐 0.1-0.3）
控制限：UCL/LCL = EWMA_mean ± 3 × σ_EWMA × sqrt(λ/(2-λ))
→ 示例：5 波 Q=[9.0, 8.5, 8.0, 7.5, 7.1] → EWMA 从 9.0 持续降到 8.20——趋势恶化预警（虽 Q=7.1 仍达标）

CUSUM：S_t^± 累积偏差，μ_0=7.0，k=0.5σ（参考值），h=4σ（决策阈值）
→ 适合"达标线附近持续小幅偏低"（如 Q=[7.0, 6.9, 7.0, 6.8, 6.9]），对高位缓降不如 EWMA 敏感
```

**EWMA vs CUSUM 选型**：EWMA 主选（design_memos 更可能缓慢退化非突变）；CUSUM 补充（达标线附近波动）；Shewhart 已有（Q<4.0 单点突变返工）。**三图联用 = 全覆盖质量异常模式**。AIAG-VDA 四模型分类映射：Model A（均值+变异恒定）→正常；Model B（均值恒定变异变化）→检查 §7.0.8 effort 估算；Model C 磨损型（均值漂移）→检查 §7.0.5 增量更新遗漏或 §6.0 权重校准；Model D 混沌型→🔴 紧急停工，§7.0.7 L4 全波回滚。实施：`scripts/quality_spc.py`（需 scipy.stats）输出 `quality_spc.csv`，每周与 §6.1 主动消费监控一同触发。

**SPC 冷启动阶段处理（v1.1.0 新增）**：EWMA/CUSUM 需 ≥5 个数据点建立稳定控制限——冷启动三阶段：

| 阶段 | 波次 | 数据点数 | SPC 状态 | 操作 |
|---|---|---|---|---|
| **冷启动期** | 第 1-2 波 | ≤4 | EWMA/CUSUM 不可用 | 仅用 Shewhart 单点检测（Q<4.0 返工 / Q≥7.0 达标）+ 记录 Q score 作为基线数据积累 |
| **预热期** | 第 3-4 波 | 5-8 | EWMA 可用，CUSUM 不可用 | EWMA 开始计算（λ=0.2）但控制限宽松（±4σ）；CUSUM 仅记录累积值不告警 |
| **稳态期** | 第 5 波+ | ≥10 | EWMA+CUSUM 全功能 | 标准 3σ 控制限 + CUSUM k=0.5σ/h=4σ；进入四模型分类 |

冷启动期替代趋势监控：相邻波次 Q score 差值 |Q_t - Q_{t-1}| > 2.0 → 标 ⚠️ 异常波动（Rubric 评分不稳定或施工质量波动），触发人工复核。SPC 价值延伸到施工后的运维期（timeliness 持续衰减），稳态期在施工完成后仍有意义。

**Western Electric / Nelson 规则（v1.2.0 新增 / v1.3.0 修正名称）**：Shewhart 控制图的 8 种非随机异常模式（v1.3.0 修正：Rule 2 的"9 点连续单侧"是 [Nelson Rules 1984](https://metricgate.com/docs/nelson-rules-control-chart/) 标准而非 Western Electric 1956 的 7-8 点，采用 Nelson 更保守标准）：

| 规则 | 模式 | 本审查 Q score 场景 | 处理 |
|---|---|---|---|
| Rule 1 | 1 点超出 3σ 控制限 | Q=3.5（远低于 7.0 阈值） | 立即返工（§7.0.7 L1 单表回滚） |
| Rule 2 | 9 点连续在中心线一侧 | 连续 9 波 Q 均 >8.5（单侧偏置） | 检查是否过度保守——half_life 可能过长，考虑缩短 |
| Rule 3 | 6 点连续上升或下降 | Q 从 9.0→8.5→8.0→7.5→7.1→6.8（连续 6 波下降） | 触发 EWMA 预警 + §6.0 权重校准 |
| Rule 4 | 14 点交替上下 | Q 波动 8.2→7.3→8.1→7.4→...（14 波交替） | 检查 §7.0.8 Rubric 评分是否不稳定 |
| Rule 5 | 连续 3 点中 2 点在 2σ 之外（同侧） | Q=[9.0, 6.5, 9.2, 6.8] | 中等强度异常——检查周期性施工质量问题 |
| Rule 6 | 连续 5 点中 4 点在 1σ 之外（同侧） | Q=[9.0, 8.8, 6.5, 6.8, 9.1, 6.6] | 弱异常——可能两类表混合在同批次，检查 §6.2 批次划分 |
| Rule 7 | 15 点连续在 1σ 之内（两侧） | Q 在 7.9-8.1 波动 15 波（变异过小） | 检查评分是否丧失区分度（Rubric 过宽松） |
| Rule 8 | 连续 8 点在 1σ 之外（两侧） | Q=[6.5, 9.0, 6.8, 9.2, ...]（变异过大） | 施工质量两极分化，检查是否两个质量流程并行 |

落码：Western Electric/Nelson 规则作为 Shewhart 的**后处理步骤**——先跑 Shewhart 3σ（Rule 1）+ EWMA + CUSUM，再对 Shewhart 历史点序列跑 Rule 2-8 模式识别（Rule 4-8 是 Nelson 独有，EWMA/CUSUM 不覆盖）。封装进同一 `scripts/quality_spc.py`，`quality_spc.csv` 新增 `we_rule` 列。

**Nelson Rules 误报率风险矩阵（v1.4.0 新增，参考 [ifactoryapp 2026-06-25 Pharma SPC](https://ifactoryapp.com/blog/western-electric-nelson-rules-pharma)）**：全部启用 8 条规则误报率从单规则 0.27%（ARL~370）升到 1-2%（ARL~91，4 倍误报，"8-10 周内摧毁操作员信任"——某制药厂全启用后两周内每班 3-5 次告警，操作员停止阅读，六个月后真实异常无人注意）。risk-based subset selection：

| 规则 | 独立误报率 | 本审查启用 | 理由 |
|---|---|---|---|
| Rule 1（1 点超 3σ） | 0.27% | ✅ **必启用** | 非协商性——Q<4.0 立即返工是基础底线 |
| Rule 2（9 点单侧） | 0.20% | ✅ **启用** | 检测缓慢漂移——Q score 场景核心需求 |
| Rule 3（6 点连续升降） | 0.27% | ✅ **启用** | 检测连续下降趋势——与 EWMA 互补（EWMA 更早，Rule 3 更直观） |
| Rule 4（14 点交替） | 0.46% | ⚠️ **条件启用** | 误报率最高——仅稳态期（≥14 点）且 Rubric 评分疑似不稳定时启用 |
| Rule 5（3 点中 2 点超 2σ） | 0.20% | ✅ **启用** | 中等强度异常——检测周期性质量问题 |
| Rule 6（5 点中 4 点超 1σ） | 0.20% | ⚠️ **条件启用** | 弱异常——仅批次划分疑似不合理时启用 |
| Rule 7（15 点在 1σ 内） | 0.20% | ⚠️ **条件启用** | 检测区分度丧失——仅怀疑 Rubric 过宽松时启用 |
| Rule 8（8 点在 1σ 外） | 0.20% | ⚠️ **条件启用** | 检测变异过大——仅怀疑两个质量流程并行时启用 |

**默认启用集 Rule 1/2/3/5**（合计误报 ~0.94%，ARL~106，本审查 10-20 数据点场景期望 1 次误报/10 波，可接受）；**诊断启用集 Rule 4/6/7/8**（仅 L3 抽检发现异常或 §6.0 跨波次重评发现评分不稳定时临时启用，诊断完关闭——每次误报都消耗人工复核时间，防"操作员信任损耗"）。与冷启动对接：冷启动期仅 Rule 1；预热期 Rule 1+3（6 点趋势数据刚够）；稳态期默认集 Rule 1/2/3/5。Nelson 是 Western Electric 超集（N1=WE1/N2=WE4/N5=WE2/N6=WE3），启用 Nelson 全集已自动覆盖 WE——决策不是"WE 还是 Nelson"，而是"启用 8 条中的哪个子集"。

**Hotelling T² 多变量 SPC（v1.3.0 远期升级路径记录）**：当前 SPC 是单变量（Q score 综合分）——T² 可监控四维度联合分布，检测"加权后达标但单维度持续退化"（如 timeliness=4 被其他维度拉平到 Q=7.0）。当前不引入（加权模型已够+T² 需 ≥20 数据点+实现复杂一个量级）；远期触发条件：L3 抽检发现某维度系统性偏低但 Q score 未告警时引入。

**自适应控制限思想（v1.4.0 新增，参考 [AIAG SPC 3rd Edition 2026-07](https://ifactoryapp.com/industries/automotive-manufacturing/dptive-control-limits-automotive-stamping-quality-engineers-predictive-maintenance)）**：静态控制限基于历史基线，过程漂移后误报率 40-60%——补入**基线重算触发条件**（任一满足即用最近 5 波 Q score 重新拟合 μ_0/σ_EWMA）：①§6.0 跨波次重评触发权重调整 ≥0.5（Q score 公式变化旧基线失效）；②§7.0.7 L3/L4 全波回滚后（施工流程特征变化，冷启动重启）；③σ 连续 3 波递增 >20%（旧控制限过窄误报增加）；④§7.0.1 模板或 §7.0.8 Rubric 结构性修订（评分语义变化，完全冷启动）。不引入 AI 增强自适应 SPC（ML 根因识别+实时 Cpk 对个人项目过重）——离散自适应（触发时重算）对月级波次已够；与 §6.0 跨波次重评构成"优先级层面+质量度量层面"双层反馈环。

**Freshness SLO/SLI 服务级别度量（v1.9.0 新增，参考 [oneuptime.com 2026-01-30](https://oneuptime.com/blog/post/2026-01-30-freshness-slos/view)）**：Q score timeliness 是单表连续值（Leading），补入全仓库合规率聚合层（Lagging）：

```
Freshness SLI = (时间窗口内 timeliness ≥ 7.0 的表数 / 总表数) × 100%
SLO = 90%（design_memos 文档新鲜度合规率目标）
Error Budget = 10%（允许 10 张表 timeliness < 7.0）
Error Budget 消耗规则：
  - 剩余 > 50%（≤5 张 stale）→ 正常施工节奏
  - 剩余 20-50%（6-8 张 stale）→ 降速，优先修复 stale 表文档再补新表
  - 耗尽（>10 张 stale）→ 冻结新表文档施工，全力修复 stale 表（stabilize first）
```

**Age-based vs Lag-based 区分**：Age-based（now - 文档最后同步天数 = age_days）已由 time_decay 实现；Lag-based（文档同步时间 - 代码变更时间 = 更新滞后天数）与 §7.0.9 MTTR 联动（MTTR=Lag-based 修复延迟）——Age 管"状态"，Lag 管"响应"。**Google OKF v0.2 `stale_after` 固定日期**是简化版阈值（日历到期即 stale）——本审查有 git 历史，状态指纹（内容 hash）优于固定日期，stale_after 仅作"无 git 历史离线文档包"降级备选。采纳策略：time_decay（连续值，Q score timeliness 维度）+ 状态指纹（二元判定，Freshness SLI 合规判定）。Error Budget 耗尽冻结新施工是"质量优先于进度"的量化执行机制。

#### 7.0.5 增量更新机制（v0.5.0 新增 / v0.6.0 补 Embedded Freshness / v0.9.0 补 DocPilot false-positive filter / v1.8.0 补 predict Omissions schema↔doc 共变检测）

> §3.4 的 extract/trace 循环是"每波施工后重跑全量扫描"——但代码日常变更不应触发全量重扫。v0.5.0 补入**增量更新机制**，参考 [RepoDoc 的 semantic impact propagation](https://arxiv.org/html/2604.26523v1)（增量更新时间降 73%）。

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

**与全量扫描的分工**：增量更新（日常，git hook 触发，秒级）；全量扫描（每波施工后，§3.4 extract/trace，分钟级）；年度审计（远期，全量 Q score 重评+权重校准，小时级）。

**增量更新的边界**：
- **表名改名**：git diff 无法自动关联新旧表名——需人工在文档全局替换 + 更新 §3.4 引用漂移检测
- **跨表逻辑变更**：如某策略从消费 `kline_daily` 改为消费 `kline_daily_hfq`——需人工追所有消费方文档（§10 Q3 即此类）
- **不自动生成文档**：增量更新只"标记需重写的字段"，不自动生成内容——避免 LLM 幻觉（§9）

**Embedded Freshness 模式（v0.6.0 强化）**：freshness 信号三种架构模式（pull/push/**embedded**）——本审查 git diff 触发属 **embedded 模式**（代码变更时由 git hook 直接触发文档 freshness 更新，docs-as-code 哲学延伸：文档与代码同仓库同 PR，变更原子性保证信号实时性）。**闭环对接**：代码变更 → git hook → §7.0.5 标记受影响表 → §7.0.4 timeliness 重算（semantic_alignment 降 0.3、age_days 重置 0 → timeliness=5.1 ⚠️）→ 文档同步重写后（semantic=1.0 → timeliness=10）→ 每日 age_days 增长 → time_decay 指数衰减（30 天后 8.5 仍达标 / 90 天后 7.4 接近阈值 / 180 天后 7.1 ⚠️）。实施：封装进 `scripts/audit_data_utilization.ps1` 的 `post-commit` hook。

**DocPilot false-positive filter（v0.9.0 新增，参考 [DocPilot 2026](https://github.com/wyattstanson/docpilot)）**：并非每次代码变更都使文档过时（改注释/格式/无关变量）——补入两 pass 质量门的 **Pass 1 假阳性过滤**（不采纳 Pass 2 repair_engine 的 auto-fix：金融文档 LLM 可能"自信地错误"修复，§9 红线保留人工 review）。融入 §7.0.5 步骤 2.5：

```
2.5 false-positive filter（v0.9.0 新增）：
   对每个受影响表，判断代码变更是否真的影响文档描述的用法：
   a. git diff 的 +/- 行是否包含表名字段名（grep 表名+字段名）
   b. 变更行是否在 SQL 查询/数据加载函数内（正则匹配 def fetch_/SELECT/INSERT）
   c. 若 a AND b → true positive（标记需重写）；否则 → false positive（跳过）
```

与 §7.0.6 Cascade 双重条件互补：Cascade 管"验收阶段的一致性"，DocPilot 管"更新阶段的必要性"——双重过滤。与 Syntropy 联动：`code_sessions_since_sync > 0` → filter 判断是否影响文档 → true positive → 触发 §7.0.4 timeliness 重算。

**CodeScene "predict Omissions" schema↔doc 共变检测（v1.8.0 新增，参考 [CodeScene 2.4.0](https://docs.enterprise.codescene.io/versions/2.4.0/guides/technical/temporal-coupling.html#use-temporal-coupling-to-predict-omissions)）**：§7.0.3 Temporal Coupling 的**逆向应用**——正向找"意外共变=隐藏依赖"，逆向找"应当共变但实际不共变=文档遗漏"（schema 变了但文档从未跟）：

```
1. 定义 expected_coupling：对每张表 schema_file = schemas/categories/{prefix}_table_X.py，
   doc_files = grep -l "table_X" design_memos/*.md
2. 复用 §7.0.3 commit→files 映射（已含 commit-size 归一化过滤）
3. actual_coupling = temporal_coupling(schema_file, doc_file)
4. 预测遗漏：schema_file 被 ≥1 commit 修改但 actual_coupling = 0 → 标 ⚠️ 预测遗漏
   → 输出 predicted_omission.csv（schema_file × doc_file × schema_commit_count × omission_severity）
5. 严重度分级：HIGH（schema ≥3 次 commit 且 doc 0 次共变）/ MEDIUM（1-2 次 commit 且 0 共变）/
   LOW（0 < actual_coupling < 0.3，部分遗漏）/ OK（≥ 0.3）
6. 与增量更新联动：HIGH/MEDIUM 项自动注入 §7.0.5 步骤 1 的"受影响表"列表
   → false-positive filter → true positive → 标记文档需重写（闭合"预测→验证→标记→重写"主动检测环）
```

与 git diff 触发互补：git diff 是**被动**（只看最近一次 commit），predict Omissions 是**主动**（扫全量历史发现累积遗漏）。不自动修复（§9 红线"不自动生成文档"）——由 §7.0.6 L3 + §7.0.2 反推草稿处理。共享冷启动约束（commit <50 仅输出 raw count）。与 SCORE Orphan Topics 对偶：predict Omissions 找"有代码变更但无文档跟随"（schema→doc），Orphan Topics 找"有文档但无代码消费"（doc→schema）——后者在个人项目价值有限（design_memos 是 why 层，不要求每篇都有代码消费方），记录备查不实施。

**DataHub docFreshnessInfo `verifiedAtVersion` 状态指纹机制（v1.9.0 新增，参考 [DataHub PR #19023 2026-08-09](https://github.com/datahub-project/datahub/pull/19023)）**：当前 git diff 触发是**事件驱动**（每次 commit 触发+只看最近 commit），补入**状态驱动**互补机制：

```
文档验证时 → 记录 verifiedAtVersion = BLAKE3(schema_file_hash + upstream_table_hashes + deprecation_status)
后续检查时 → 重新计算 current_version = BLAKE3(当前 hash 组合)
若 current_version ≠ verifiedAtVersion → 文档 stale（无需 git diff，无需重扫文档文本）
staleReason = "schema 变更" / "上游依赖变更" / "deprecation 状态变更" / "ownership 变更"
五字段：verifiedAgainstUrns（实体+一跳 lineage 上游，对齐 §7.0.3 依赖图）/ verifiedAtVersion（联合指纹）/
       verifiedAtTime（对齐 §7.0.4 last_sync_time）/ actor（对齐 §7.0.6 L3 执行者）/ staleReason（对齐步骤 2.5 判定）
```

优势：O(1) 指纹对比而非 O(N) git diff 扫描；**上游传播检测**——`stock_list` schema 变更 → 依赖它的 `kline_daily` 联合指纹变更 → 自动标记 stale（git diff 只触发 `stock_list` 自身检查）。互补而非替代：git diff 实时（CI 门禁），状态指纹按需（§7.0.6 验收闭环批量检查）。实施：`scripts/freshness_fingerprint.py` 输出 `freshness_fingerprint.csv`（is_stale=true → §7.0.4 semantic_alignment 降 0.3）；概念借鉴用 git+frontmatter+脚本实现，不部署 DataHub 平台（§9）。与 Google OKF v0.2 对比：状态指纹+一跳传播 vs 固定日期+无传播——本审查文档-代码依赖明确需上游传播，**采纳 DataHub 状态指纹**；OKF 的 generated vs verified 分离与 Attested Computation 思想补入 §7.0.6。

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

> **L3 语义抽检理由**：[DocPrism 2026](https://arxiv.org/pdf/2511.00215)发现 LLM 辅助文档生成中 11% 的代码-文档对存在不一致。本审查的补文档施工由 AI 执行，同样风险——L3 抽检是防止"假覆盖"的最后防线。抽检发现不一致时，该表标 ⚠️ 需返工，不计入覆盖率分子。

**L3 主动学习抽样策略（v1.1.0 新增，参考 [Smart Active Sampling arXiv 2209.11464](https://arxiv.org/pdf/2209.11464.pdf) + [ISO 2859-1:2026](https://www.iso.org/cms/render/live/en/sites/isoorg/contents/data/standard/08/54/85464.html)）**：分层抽样替代纯随机（用 §3.5 Confidence + §6.0 Kano 作为"不确定性代理"，无需训练预测模型）：

| 抽样层 | 选取标准 | 每批次抽样数 | 理由 |
|---|---|---|---|
| **不确定层**（必抽） | §3.5 Confidence=0.5 或 0.8 的表（代码引用性质不确定） | 1 张 | 不确定表的"假覆盖"概率最高——SQL 查询 vs 模板继承的误判直接影响文档准确性 |
| **高风险层**（必抽） | §6.0 Kano 基本型（risk_flag=Y）且 Q score < 8.0 的表 | 1 张 | 风险红线表文档错误后果严重——Q score 偏低说明可能浅覆盖 |
| **随机层**（补抽） | 从批次内其余表中随机抽取 | 0-1 张 | 保证覆盖非高风险非不确定表的偶发问题 |

**skip-lot 规则**（ISO 2859-1 启发）：
- 连续 3 波 L3 抽检全过（零不一致）→ 下一波抽检数减半（3→2 或 2→1）——"持续高质量的批次降频检测"
- 某波 L3 发现 ≥1 张不一致 → 下一波抽检数加倍 + 全量复查该表所在社区（§7.0.3 Leiden 社区）——"发现问题则升频+扩大范围"
- 某表连续 2 次被抽中且全过 → 该表进入"信任名单"暂免抽检（直到代码变更触发 §7.0.5 增量更新）

**Cascade 自动化语义验证远期升级路径（v0.8.0 新增）**：[Cascade arXiv 2604.19400v1 FSE 2026](https://arxiv.org/pdf/2604.19400v1) 的**双重条件**不一致检测（条件 1：代码执行文档生成的测试→失败；条件 2：文档生成的代码执行同一测试→通过；仅当两者同时满足才报不一致——排除"文档表达歧义导致测试生成错误"的误报）。不当前采纳：design_memos 是架构文档（why 层）非 API 参考文档，从"解禁前 30 日减仓"业务规则生成可执行测试难度远高于 API 签名；需 ClickHouse+Python 测试环境；59 表×2 LLM 调用成本与 DocAgent 同量级；L3 人工抽检成本可接受。远期触发条件：100+ 篇文档或 L3 不一致率 >15%（DocPrism 基准 11%）。**双重条件思想已简化融入 L3 抽检**：先验证"文档描述是否自洽"再验证"文档与代码是否一致"。与 DocAgent 互补（pre-shipment vs post-shipment 验证），远期引入顺序：先 DocAgent 后 Cascade。[CSDN 2026-06 5 层语义对齐校验](https://blog.csdn.net/FastProceed/article/details/160023423)（AST+LLM 双模态+IR）更重，当前不采纳（§9 已排除 AST 全量解析）。

**Google OKF v0.2 `generated` vs `verified` 分离 + `Attested Computation`（v1.9.0 新增，参考 [itbrief.asia 2026-07-27](https://itbrief.asia/story/google-adds-trust-provenance-to-open-knowledge-format)）**：OKF v0.2 三层验证信任模型映射到验收闭环——区分"文档是怎么来的"（generated）vs"文档被谁验证过"（verified）vs"验证过程本身是否可信"（attested）：

| 阶段 | OKF v0.2 信号 | 本审查标注 | 实现 |
|---|---|---|---|
| **生成** | `generated: {method, timestamp}` | frontmatter `drafted_by: code_reverse_extraction` + `draft_date` | §7.0.2 代码反推草稿 + `verification_status: draft` |
| **验证** | `verified: {actor, timestamp, method}` | frontmatter `verified_by` / `verified_date` / `verification_method: L3_semantic_check` | §7.0.6 L1/L2/L3 验收通过后 `verification_status: draft → verified` |
| **attestation** | `Attested Computation`（验证计算是否用批准方法） | 下方 Attested L3 抽检清单 4 检查点逐项记录 | 记录验证过程本身（非密码学签名） |

**未标 `verified` 的文档不计入 §5.1 覆盖率分子**（与 Q ≥ 7.0 并列双重达标条件）。attestation 防的是 L3 抽检流于形式——"看了表名就说通过"使 L3 退化为 L1，防线失效（DocPrism 11% 不一致率依据）。

**Attested L3 抽检清单**（4 检查点缺一不可，结果记入 verification_log.md——记录检查过程本身即为 attestation 的轻量实现，不引入 OKF 密码学签名）：

```
□ 检查点 1：文档"关键字段"列出的字段是否在代码 SQL SELECT 中真实出现
  → grep 代码 SELECT 语句对比文档字段列表；文档列了但代码未 SELECT → ⚠️ 假覆盖
□ 检查点 2：文档"下游逻辑"描述的计算是否在代码中真实执行
  → 读代码消费函数对比文档描述；文档说"计算 7 因子"但代码只算 3 个 → ⚠️ 假覆盖
□ 检查点 3：文档"消费频率"与代码调度配置是否一致
  → 检查 tasks.yaml schedule 对比文档"盘后增量/周更/月更"；不一致 → ⚠️ 频率不一致
□ 检查点 4：文档"依赖上游"与 frontmatter depends_on 是否一致
  → 对比文档上游表与 frontmatter；漏列或未登记 → ⚠️ 依赖不完整

→ 4 个检查点全过 → L3 通过，verification_status: draft → verified
→ 任一未过 → L3 不通过，该表标 ⚠️ 需返工，不计入覆盖率分子
→ 抽检者须在 verification_log.md 记录每张表 4 个检查点的 ✅/⚠️ 结果（非仅二元判定）
```

与分层抽样的关系：分层抽样决定"抽谁"，Attested 清单决定"怎么抽"——两者正交。

**覆盖率目标轨迹**：

| 波次 | 目标覆盖率（英文下界） | 验收点 |
|---|---|---|
| 施工前 | 35.9%（37/103，v2.1.0 实测消费层口径） | 基线 |
| 第一波后 | ~44.7%（46/103） | 重跑扫描确认批次 A 9 张转消费层覆盖 |
| 第二波后 | ~68.9%（71/103） | 重跑扫描确认批次 B+C 25 张转消费层覆盖 |
| 第三波后 | ~93.2%（96/103） | 批次 D 25 张记录完毕——终态：59 张缺口清零，余 6 张 §6.1b dormant + 1 张真闲置不进消费覆盖目标 |

#### 7.0.7 施工回滚机制（v0.6.0 新增）

> 补文档施工可能引入错误（L3 未过的假覆盖/冲突解决误判吞并 alpha 视角/拓扑错误引用未补依赖表）——v0.6.0 补入**回滚机制**，确保施工错误可逆。

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
4. 重跑 §3.2 三层扫描 → 确认回滚后覆盖率回落至预期
5. 根因分析（5 Why）→ 记录到 docs/_audit/rollback_log.md
6. 修正根因（模板/脚本/评分模型）后重新施工
7. 重新验收（§7.0.6 全流程）
```

**不做的**（对齐 §9）：
- 不用 `git reset --hard` 回滚——破坏历史可追溯性，违反 git 安全协议
- 不自动回滚——L3 抽检未过需人工确认是否真为"假覆盖"还是"L3 抽检本身误判"
- 不回滚代码——本审查只改文档不改代码，代码回滚不在 design_memos 层

**v1.9.0 补回滚版本校验**（DZone 假新鲜模式 5）：revert 前检查目标 commit 的文档 timeliness 是否低于当前——若 revert 目标更旧 → 警告"回滚到更旧的文档版本"（防止 revert 不慎恢复含已修复 bug 的旧版文档，文档"倒退时间"但看起来"刚更新过"）。

**CoDe-R DDPF 双路径回退概念（v0.7.0 新增）**：[CoDe-R arXiv 2604.12913v2 2026-06](https://arxiv.org/html/2604.12913v2) 的 Dynamic Dual-Path Fallback——映射到回滚场景：**Path 1 语义恢复**（L1/L2 小范围回滚后重写：保留原消费方语义，仅修正与代码不符的字段）vs **Path 2 语法稳定**（L3/L4 大范围回滚后重建：回退"最小文档"从可信基点重建）——§7.0.7 分级已隐式实现此对应（按影响范围静态选择路径，无需 CoDe-R 的运行时验证），证明回滚分级设计与学术 DDPF 思路对齐。

**Innovation-Residual 故障归因（v1.2.0 新增，参考 [arXiv 2608.05490v1 2026-08-06](https://arxiv.org/html/2608.05490v1)）**："5 Why"能定位"哪张表有问题"但难定位"哪个操作步骤引入错误"——补入创新残差思想：收集已通过 L3 的成功施工轨迹的操作序列 → 按操作位置统计操作类型分布 P(op_t|position_t) → 对故障表计算残差 = 1 - P(actual_op_t|position_t) → **残差最大且超 Detection Limit（2σ_innovation）的操作位置即疑似故障源**（低于 2σ 视为正常波动不归因，减少误报）。简化版用频率统计替代预测模型（个人项目操作数据量不足以训练 n-gram/Markov 模型）。与回滚分级对接：L1 单表归因故障操作→修正后重施工（Path 1）；L2 若 ≥3 张表故障指向同一操作位置→排查共因（如模板指引歧义）；L3/L4 无意义（大范围回滚非单操作问题）→ Path 2 重建。输出 `failure_attribution.csv`。

#### 7.0.8 努力度估算 Rubric（v0.6.0 新增）

> §6.0 的 effort_score = doc_complexity × W4 + cross_module_coupling × W5，但取值靠人工判断——"Effort 估算易被低估"是 RICE 最大反模式之一。v0.6.0 补入**努力度估算 Rubric**，量化取值标准，确保不同表的 effort 评分一致可复现。

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

> §7.0.1-§7.0.8 定义了"怎么做"，但未定义"做到哪了"——多波施工中若无进度看板，易出现"遗漏某张表"或"同一张表重复施工"。v1.3.0 补入**轻量级 CSV 看板**，参考 [docsie.io Documentation Sprint 2026](https://www.docsie.io/blog/glossary/documentation-sprint/) + [projectmanagementformula.com Kanban 2026-04](https://projectmanagementformula.com/how-to-set-up-a-kanban-complete/)（WIP 限制）。

**为何用 CSV 矩阵而非电子看板工具**（对齐 §9 个人项目红线）：design_memos 是纯文本仓库，电子看板破坏 docs-as-code 原则——状态应与文档同仓库可 git 追踪；CSV 可由 `audit_data_utilization.ps1` 自动生成/更新（扫描 git log + 文档存在性，不靠人工填）；与 `detective_scan.csv`/`quality_spc.csv`/`priority_v{n}.csv` 同目录（`docs/_audit/`）统一审计矩阵。

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

**WIP 限制**：
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

**与 §6.0 跨波次优先级动态重评的对接**：`priority_v{n+1}.csv` 与看板 `priority` 列同步——若某表从"期望型"降级为"兴奋型"，看板 `notes` 列标注"v{n+1} 降级，下波可延后"。

**与 §7.0.7 回滚分级的对接**：回滚日志记录回滚级别（L1-L4），看板 `notes` 列标注——L1 单表回滚后状态 Rolled-back → In Progress；L4 全波回滚后该波所有表 Done → Rolled-back → Backlog（重排优先级）。

**MTTD/MTTR 回滚效能度量（v1.4.0 新增，参考 [uvik.net 2026-08-02](https://uvik.net/blog/data-quality-metrics-kpis/)）**：

| 度量 | 定义 | 采集方式 | 目标 |
|---|---|---|---|
| **MTTD** | 从文档错误引入（git commit 时间）到错误检测（§3.4 Detective 扫描或 §7.0.6 L3 抽检发现）的时间 | `rollback_log.md` 记录 `error_introduced` 和 `error_detected`，MTTD = detected - introduced | ≤7 天（Detective 扫描周级 + L3 每波抽检） |
| **MTTR** | 从错误检测到修复完成（回滚后重施工通过验收）的时间 | `rollback_log.md` 记录 `error_detected` 和 `fix_completed`（重施工 Q ≥7.0 + L3 pass），MTTR = completed - detected | ≤14 天（L1 单表回滚）/ ≤30 天（L2-L4 批次/全波回滚） |

个人项目适配：不追求企业基准（MTTD ≤4h/MTTR ≤24h——文档施工是月级波次非实时管道，以"波次"非"小时"为单位）；施工波次少回滚事件可能 0-3 次，**积累 ≥5 次回滚事件后才计算 MTTD/MTTR 均值**（此前仅记录时间戳）。与 §3.4 联动：MTTD 持续 >7 天 → Detective 扫描升频日级；MTTD ≤1 天但 MTTR >14 天 → 检查 §7.0.7 回滚流程是否阻塞。

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

> §6.1 的真闲置表生命周期决策（DEPRECATED→SUNSET→REMOVED）在 design_memos 层只记录"决策"，但归档的**实际操作在数据采集脚本层**。§9"不做什么"声明"不写归档详细方案"——v0.5.0 补入**归档操作的位置指引**（非详细方案），使归档决策可追溯到执行位置。

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
| 不在本备忘写每张表的 DDL/字段细节 | DDL 真源在 [schemas/categories/](../../../../schemas/categories/)，备忘只引用稳定 path |
| 不在本备忘写每张表的接入代码 | 代码施工在策略/风控模块各自文档，备忘只记录"该表应被哪篇文档消费" |
| 不强制一次性补齐所有文档缺口 | 分波次补文档，每波完成后重评下一波优先级 |
| 不为 3 张真闲置表写"如何归档"详细方案 | 归档操作在数据采集脚本层，不在 design_memos 层 |
| 不臆造未存在的中文别名 | 中文别名校验只覆盖已知同义词，不创造新词 |
| 不替换现有数据流 | 补文档是记录已有用法，不破坏现有策略 |
| 不将 etf_nav 折溢价作为套利策略 | 个人系统无一级市场申赎资格（需 50-100 万份），仅作流动性危机监测信号 |
| 不引入外部数据目录工具（DataHub/Amundsen/Atlan） | 个人项目过度工程——PowerShell 脚本 + CSV 矩阵已满足审查需求；AI-powered catalog 适合企业级多团队场景 |
| 不用 AST 全量解析做代码引用性质分类 | AST 实现成本高于正则 10 倍——§3.5 已用正则 + 抽查替代（5 级 Confidence 自动判定），覆盖 59 张缺口表的批量标注需求 |
| 不将 CI 门禁设为阻断（exit 1） | 个人项目不强制 CI 阻断文档覆盖率低于 80%——降级为 warn 提醒，符合渐进式治理风格 |
| 不用 LLM 做全量语义验证 | [DocPrism 2026](https://arxiv.org/pdf/2511.00215) 的 LCEF 需 LLM 逐函数调用——个人项目过重。§7.0.6 L3 语义抽检是 lightweight 替代，覆盖"假覆盖"风险且无 LLM 成本 |
| 不用 WSJF 替代 RICE（v0.5.0 新增） | WSJF 的 Time Criticality 适合多团队 portfolio 排序；个人项目无硬截止日——Time Criticality 退化为"风险模块优先"已由 W2=5.0 覆盖 |
| 不用 RepoKG 知识图谱做文档生成（v0.5.0 新增） | [RepoDoc arXiv 2604.26523](https://arxiv.org/html/2604.26523v1) 的 RepoKG 需建仓库级知识图谱——个人项目过重。§7.0.2 代码反推 + §7.0.5 增量更新是 lightweight 替代 |
| 不用 DataQ 全量 10 维度评估文档质量（v0.5.0 新增） | [DataQ 框架](https://publicationslist.org/data/jorge-martinez-gil/ref-175/dataq.pdf) 10 维度适合企业级 open data catalog——个人项目裁剪为 4 维 Q score（§7.0.4）覆盖"浅覆盖检测"核心需求 |
| 不自动生成文档内容（v0.5.0 新增） | §7.0.2 代码反推只生成**草稿**，不自动写入文档——避免 LLM 幻觉产生"听起来合理但与代码行为不符"的假文档（比"无文档"更危险）。所有草稿经人工复核 + L3 抽检后才写入 |
| 不用 Kano 完整双向问卷（v0.6.0 新增） | 完整问卷需统计显著性样本——个人项目无用户可问卷。§6.0 用规则映射替代（risk_module_flag=Y→基本型 / code_ref≥10→期望型 / 其余→兴奋型） |
| 不用 6 轴全量审查方法（v0.6.0 新增） | [K-AI 6-axis 2026-05](https://www.k-ai.ai/en/news/auditer-corpus-documentaire-ia-methode-6-axes/) 适合企业级 RAG 语料审查——个人项目无合规压力，已覆盖 4 轴，轴 1 远期升级，轴 3 不适用（§3.4） |
| 不强制统一多消费方语义（v0.6.0 新增） | 同一表在风险文档（P0）和 alpha 文档（P1）的消费语义天然不同——强制统一会导致 alpha 信号链被风险视角吞并，§7.0.2 用 ⚠️ 双语义标注替代 |
| 不用 git reset --hard 回滚施工（v0.6.0 新增） | §7.0.7 用 `git revert`（保留历史可追溯）——施工错误应可追溯根因，不应抹除痕迹 |
| 不用 Milvus 乘法模型做 Q score timeliness（v0.7.0 新增） | 乘法模型适合**检索排序**（旧文档归零沉底），Q score 度量**文档质量**——旧文档语义价值不应被时效归零。§7.0.4 保留加法模型，RAG 检索层（远期）再用乘法 |
| 不当前采纳 DocAgent 多智能体（v0.7.0 新增） | 5 智能体×59 张表 LLM 成本过高——§7.0.2 单 pass grep + §7.0.6 L3 人工抽检是 lightweight 替代，核心思路（拓扑排序+Truthfulness）与 DocAgent 一致。远期 100+ 篇时再引入 |
| 不当前采纳 REFORGE 8 门漏斗（v0.7.0 新增） | 需 AST + 控制流图 + 数据流分析工具链——比 AST 全量解析更重。§3.5 的 5 级正则 + 抽查已够，远期正则误判率 >20% 时再引入 |
| 不全面采纳 Consequence Ranking 替代 RICE（v0.7.0 新增） | 103 张表×2 段后果叙述成本高于 RICE 公式——§6.0 Kano 分类层已吸收"后果导向"（基本型=不做有严重后果），Kano 前置过滤器承担战略判断职能 |
| 不当前采纳 Cascade 自动化语义验证（v0.8.0 新增） | design_memos 是架构文档（why 层）非 API 参考文档——从业务规则生成可执行测试难度高+测试环境成本高。§7.0.6 L3 人工抽检已够，远期 100+ 篇或不一致率 >15% 时再引入；"双重条件"思想已融入 L3 |
| 不采纳字段级血缘（v0.8.0 新增） | 列级血缘需 SQL 解析器（Apache Calcite）+ 图数据库（Neo4j）——个人项目过重。§7.0.3 表级 Kahn 拓扑已满足"被依赖表先补"，字段级血缘增量价值在 103 表规模不显著 |
| 不用 Leiden 社区发现替代 §6.2 人工批次（v0.9.0 新增 / v1.6.0 升级 Louvain→Leiden） | 社区发现按依赖密度分批不含业务优先级语义（风险优先原则）——§6.2 人工批次保证"风险表先补"，Leiden 仅作验证工具（封装 `scripts/community_detection.py`） |
| 不采纳 DocPilot auto-fix 全流程（v0.9.0 新增） | auto-fix 对金融系统文档风险过高（LLM 可能"自信地错误"修复 T+1→T+0）——仅吸收 Pass 1 false-positive filter，保留"不自动生成文档"红线，人工 review 不可省 |
| 不用 Detective 扫描的 Option A scheduled agent（v0.9.0 新增） | Option A（scheduled Claude agent）LLM 成本高——选 Option C Hybrid：确定性检查用 PowerShell 脚本，语义检查用 §7.0.6 L3 人工抽检 |
| 不只用 Shewhart 单点控制图做 Q score 趋势分析（v1.0.0 新增） | Shewhart 只检测单点越界，无法检测渐进漂移（Q 连续 5 波下降但每波都"达标"）——§7.0.4 补 EWMA+CUSUM 三图联用全覆盖 |
| 不对 103 张表的小规模依赖网络过度依赖 CPM（v1.0.0 新增） | 依赖链浅（最长 4-5 层），CPM 与 Kahn 拓扑序差异有限——CPM 作"资源优先分配"指导（TF=0 优先保障），不替代 Kahn（顺序 vs 工期，正交） |
| 不做完整贝叶斯先验 elicitation + MCMC 采样（v1.0.0 新增） | 103 表×5 权重×多波后验计算量过重——§6.0 仅形式化定义公式+触发条件（偏差连续 2 波超 2σ），实际执行仍用启发式校准循环，远期波次 >5 再引入 PyMC |
| 不用纯主动学习模型替代分层抽样（v1.1.0 新增） | L3 抽检数据量少（每波 2-3 张）不足以训练预测模型——§7.0.6 用分层抽样（Confidence+Kano 作不确定性代理）+ skip-lot 规则作轻量替代 |
| 不用 Pareto 前沿替代 RICE 排序（v1.1.0 新增） | 103 表规模下 RICE 的"虚假精确性"是可接受近似（priority 差异只决定"先做谁"）；Pareto 前沿 30-50 个非支配解信息密度过高反降决策效率——作远期可视化工具备查 |
| 不全面实施 Innovation-Residual 审计（v1.2.0 新增） | 完整实施需训练操作序列预测模型——个人项目操作数据量不足。§7.0.7 仅借鉴残差思想用频率统计+Detection Limit（2σ）过滤正常波动，远期操作数据 >500 条再评估 |
| 不引入 DoWhy 因果推断（v1.2.0 新增） | 因果归因需反事实对照实验——L3 抽检样本量不足。Innovation-Residual 是相关性归因（非因果），对"定位故障步骤"已足够，远期数据充足再引入 |
| 不引入完整 FMEA RPN 施工风险评估（v1.3.0 新增） | Severity/Occurrence/Detection 三要素已由 Kano+Rubric+Confidence 分散覆盖——103 表×3 维度×1-10 分=3060 次评分过重，看板 notes 列标 Kano+Confidence 已够 |
| 不引入 Staleguard/knowledge-diff 外部漂移检测工具（v1.3.0 新增） | 两者需 Rust/Node.js 工具链集成——§3.4 Detective 扫描 PowerShell 5 类检查+§7.0.5 增量更新已覆盖，knowledge-diff 的语义判断由 L3 人工抽检替代；违反"派生产物不入 git"约束 |
| 不引入 AI 增强自适应 SPC（v1.4.0 新增） | 需 ML 模型训练+实时数据流+CMMS 集成——个人项目月级波次无实时数据流。§7.0.4 仅借鉴"基线重算"思想（触发时用最近 5 波重拟合 μ_0/σ_EWMA），离散自适应已够 |
| 不引入 Ticket Deflection Rate 等 KB 消费效果指标（v1.5.0 新增） | 该类指标面向有搜索+ticket+帮助台的在线 KB——design_memos 是 git markdown 无此基础设施。用"文档引用次数变化"（§3.2 grep 命中数）作代理指标 |
| 不引入 Financial Impact 技术债框架（v1.5.0 新增） | 需团队规模+薪酬+债务时间占比参数——个人项目 1 人+AI 无薪酬成本。§6.0 SQALE TDR+Kano 分类作 Annual-Interest 代理已够 |
| 不引入 ODCS YAML 工具链做 Data Contract（v1.7.0 新增） | schemas/categories/*.py DDL 已定义结构、design_memos 已承载语义——再写 ODCS YAML 是派生产物（违反"派生产物不入 git"）。仅用概念重构理解（§2.2 六组件映射），§8 施工参照六组件清单 |
| 不用 Temporal Coupling 替代 Leiden 静态社区发现（v1.7.0 新增） | Temporal Coupling 是动态行为依赖，Leiden 是静态结构依赖——正交不互斥。Temporal Coupling 有假阳性需人工复核，作 Leiden 的补充验证（三层验证→四件套）；commit <50 时统计不显著 |
| 不引入完整 SATD NLP 分类模型（v1.7.0 新增） | 需训练 NLP 模型——个人项目 SATD 数据量不足（~50-100 条）。§6.0 用规则映射（grep+传播链长度+情感加权）覆盖"传播链长=高优先"核心洞察，远期 >500 条再评估 |
| 不实施 Tarjan SCC 环检测（v1.8.0 新增） | 103 表依赖图预期无环或极少环（树形/森林结构）——DFS 三色标记（O(V+E)，Kahn 检测到环后才运行）已足够，Tarjan SCC 作"环数量>5 时的升级路径"记录 |
| 不自动修复 predict Omissions 检测结果（v1.8.0 新增） | 修复需 LLM 生成文档内容——§9 红线"不自动生成文档"。predict Omissions 仅输出 predicted_omission.csv 标记复核，注入 §7.0.5 增量更新流程由 §7.0.2 草稿+L3 抽检处理。预测≠修复 |
| 不引入 Google OKF v0.2 完整工具链（密码学 attestation）（v1.9.0 新增） | 密码学签名（Sigstore/CLASPIE）适合多方协作开源知识包——个人项目单作者+AI 无多方信任需求。仅借鉴 Attested Computation 思想（L3 抽检 4 检查点逐项记录）+trust 分离（frontmatter verification_status 标注） |
| 不引入 DataHub docFreshnessInfo aspect 工具链（v1.9.0 新增） | docFreshnessInfo 是 DataHub 平台内建 aspect，引入它即引入整个 DataHub（与"不引入外部数据目录工具"一致）——仅借鉴 verifiedAtVersion 状态指纹机制，用 git+frontmatter+脚本实现轻量版 |
| 不为 53 张规划层覆盖表全部补消费级文档（v2.1.0 新增） | 53 张中 6 张代码零引用（§6.1b）——无代码消费可反推（§7.0.2 无源），补消费文档是凭空编写。仅 47 张代码活跃表进 §6.2 队列；代码零引用表注册表登记 dormant 即可。"为凑覆盖率而给无消费方的表写消费文档"=浅覆盖反模式 |
| 不追溯复现 v0.2.0 历史扫描数字（v2.1.0 新增） | v0.2.0 逐表计数以未提交工作区为扫描对象，git 提交态重扫不可复现（§2.2 声明）——v2.1.0 起以实测为准，§3.4 扫描输出必须落地 CSV 快照随施工提交 |
| 不引入 SetGo metadata readiness 工具链（v2.0.0 新增） | [SetGo SSDBM '26 2026-08-11](https://dlnext.acm.org/doi/10.1145/3828820.3828827) 六维中：许可/目录就绪不适用（自采数据无外部许可约束、无对外发布需求）/可复现已由 tasks.yaml 覆盖；其余 3 维（FAIR/溯源/治理）已由 Q score 4 维+ODCS 6 组件覆盖。assess→enrich 思想已由 §7.0.2+§7.0.1+§7.0.6 三步覆盖；/setgo LLM skill 与 DocAgent 远期路径同质。不引入 SetGo+Croissant sidecar（派生产物约束） |

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
> v0.5.0-v2.0.0 各版本算法补强（含 Q2/Q7 裁定、SPC/CPM/贝叶斯/Leiden/Temporal Coupling/Data Contract/Freshness SLO/OKF/DataHub 指纹/SetGo 排除等）均 AI 裁定或评估为"强化现有方法/不采纳"，无新增开放问题——逐项理由见对应章节与 §9 边界表。

## 11. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-10 | 0.1.0 | 初稿 | 业务数据库 101 张表 vs design_memos 42 篇文档引用审查完成，识别 43 张闲置表分 P0-P4 五档，制定三波分批接入施工计划。与 [62_business_registry_construction](62_business_registry_construction.md) 配对，为 P1-B `data_asset_registry` 施工提供首批 66 张表登记清单 |
| 2026-08-10 | 0.2.0 | 大改：补代码层第三层扫描 | **核心修正**：v0.1.0 仅扫 design_memos 误判"43 张闲置"。v0.2.0 新增 src/zephyr/ 代码层扫描后发现：(1) 表数 102 非 101（§4 合计算术错误修正）；(2) 真实利用率 97.1%（99/102）非 57.4%；(3) 真闲置仅 3 张（dividend_tax_node/index_meta/msci_adjustment）非 43 张；(4) ~41-61 张为"文档覆盖缺口"（代码在用但文档未覆盖，英文上界 61/含中文别名下界 ~41）；(5) P0 9 张表全部 CODE_ONLY 非闲置；(6) P4 生猪 3 张代码有 7-8 次引用非"完全不涉及"；(7) 热度前 15 数字全部修正；(8) data_asset_registry"首批 66 张"与 dataflow_graph_registry 现有 76 条矛盾，改为"以现有 76 条为 base 补 26 张"；(9) 三波施工从"接入闲置表"改为"补文档覆盖"；(10) §10 开放问题从 8 项精简为 5 项（业务边界项回归 90 号 §18 裁定）。维持 draft（需大改） |
| 2026-08-10 | 0.3.0 | 流程与算法增强：补评分模型+验收闭环+生命周期 | (1) §3.4 新增 extract/trace 循环（[OpenSpec #739 2026-02](https://github.com/Fission-AI/OpenSpec/discussions/739)）+ CI 门禁 warn + 文档腐烂三分类；(2) §6.0 新增 Impact-Effort 优先级评分公式（[codedebtcost 2026-03](https://codedebtcost.com/prioritize)），W2=5.0 体现风险优先；(3) §6.1 引入 4 阶段生命周期 ACTIVE→DEPRECATED→SUNSET→REMOVED + 数据弃用 7 步流程；(4) §7.0 新增验收闭环（机器可查单表验收标准 + 覆盖率目标轨迹 37.3%→46%→70%→97%）；(5) §9 补 3 项；(6) §10 补 Q6。维持 draft |
| 2026-08-10 | 0.4.0 | 算法精度增强：RICE 置信度+语义抽检+权重校准 | (1) §6.0 升级为 RICE 变体 `(impact×confidence)/effort`（[bixtech.ai 2026-04](https://bixtech.ai/how-to-prioritize-data-projects-with-limited-resources-without-slowing-the-business-down/)），Confidence 因子（1.0/0.8/0.5）——`hog_futures_core` 置信度 0.5 从批次 B 降到 D 验证降权效果；(2) §6.0 权重校准循环（[sigos.io 2026-06](https://www.sigos.io/blog/weighted-scoring-model)）；(3) §7.0 验收标准升级 3 层（L1/L2/L3），L3 语义抽检参考 [DocPrism ISSTA 2026](https://arxiv.org/pdf/2511.00215)（11% 代码-文档对语义不一致）；(4) §3.3 补 2 项审查局限。维持 draft |
| 2026-08-10 | 0.5.0 | 施工算法补齐：5 子节+Confidence 自动判定+WSJF 对比+归档指引 | (1) §3.5 Confidence 自动判定算法（5 级正则优先级）；(2) §6.0 WSJF 对比+可选混合模型（不采纳）；(3) §6.2 批次 A 补 2026-08 实证（华泰解禁 7 因子/Alphanume 4 指标/Oxford FRED-MD/华福五维宏观）；(4) §7.0 补 5 子节：§7.0.1 模板/§7.0.2 代码反推/§7.0.3 Kahn 拓扑/§7.0.4 Q score/§7.0.5 增量更新；(5) §7.5 归档操作位置指引（5 层分层）；(6) §9 补 5 项；(7) §10 Q2 移 AI 已裁定，Q3 补 §3.5 自动判定。维持 draft |
| 2026-08-10 | 0.6.0 | 优先级模型增强：Kano 分类层+指数衰减新鲜度+回滚机制+努力度 Rubric | (1) §6.0 Kano 分类层（基本型无论 RICE 分必须补）作 RICE 前置过滤器；(2) §6.0 Confidence 滥用警告+分布审计；(3) §7.0.4 timeliness 升级指数衰减（`2^(-age/half_life)`，half_life=30 天）；(4) §7.0.2 多消费方冲突解决算法（P0-P4 优先级+⚠️ 双语义标注）；(5) §7.0.5 Embedded Freshness 闭环；(6) §7.0.6 补 Kano 校验+回滚就绪+分布审计；(7) §7.0.7 回滚机制（L1-L4+git revert+5 Why）；(8) §7.0.8 effort Rubric；(9) §3.4 补 6 轴远期路径（已覆盖 4 轴）；(10) §9 补 4 项。维持 draft |
| 2026-08-10 | 0.7.0 | 算法对比增强：Milvus 乘法模型+DocAgent+Consequence Ranking+REFORGE+CoDe-R | (1) §7.0.4 Milvus 乘法模型对比（保留加法模型）+高斯衰减备选+参数敏感性警告（[Temporal RAG 2026-06](https://arxiv.org/html/2509.19376v2)）；(2) §7.0.2 DocAgent 多智能体远期路径（[arXiv 2504.08725v3](https://arxiv.org/html/2504.08725v3/)）；(3) §6.0 Consequence Ranking 批判与辩护（[dualoop.coach 2026-03](https://www.dualoop.coach/blog/rice-vs-ice-vs-moscow-prioritization/)）；(4) §3.5 REFORGE 8 门漏斗远期路径；(5) §7.0.7 CoDe-R DDPF 双路径概念。维持 draft |
| 2026-08-10 | 0.8.0 | 语义验证+消费监控增强：Cascade 双重条件+消费链路主动监控+字段级血缘排除 | (1) §7.0.6 Cascade 双重条件自动化不一致检测（[arXiv 2604.19400v1 FSE 2026](https://arxiv.org/pdf/2604.19400v1)）远期路径，双重条件思想融入 L3；(2) §6.1 消费链路主动监控（[simor 2026-04](https://simorconsulting.com/blog/the-data-pipeline-that-cost-50kmonth--and-the-audit-that-found-why)：31% 计算花在零消费者管道）——30 天零查询自动标 ⚠️ 疑似闲置，与 timeliness half_life 联动；不采纳自动暂停；(3) §9 补 2 项（Cascade 当前不采纳/字段级血缘排除）；(4) 5 层语义对齐校验远期参考。维持 draft |
| 2026-08-10 | 0.9.0 | 新鲜度+增量更新+批次验证+漂移检测增强：Syntropy+Doc-Entropy Ratio+DocPilot+Louvain+Preventive/Detective | (1) §7.0.4 Syntropy 编码会话级新鲜度（session_factor 修正 time_decay，双因子乘法）；(2) §7.0.4 Doc-Entropy Ratio（avg_lag/reference_count，SITS2026 基准）；(3) §7.0.5 DocPilot 两 pass 质量门——吸收 Pass 1 false-positive filter（步骤 2.5），不采纳 auto-fix；(4) §7.0.3 Louvain 社区发现批次验证工具（5 算法对比选型，Leiden 备选）；(5) §3.4 Preventive/Detective 双层检测（[hassette #634](https://github.com/NodeJSmith/hassette/issues/634)）——Detective 扫描 4 类检查融入 extract/trace，选 Option C Hybrid；(6) §9 补 3 项。维持 draft |
| 2026-08-10 | 1.0.0 | 趋势分析+关键路径+权重形式化+差异化弃用：SPC EWMA/CUSUM+CPM+贝叶斯+有赞调度感知 | (1) §7.0.4 SPC EWMA（λ=0.2）+CUSUM（k=0.5σ/h=4σ）+Shewhart 三图联用+AIAG-VDA 四模型分类（`scripts/quality_spc.py`）；(2) §7.0.3 CPM 关键路径（TF=0 优先保障，`critical_path.csv`）；(3) §6.0 贝叶斯权重更新形式化（仅定义公式+触发条件"偏差连续 2 波超 2σ"，不实施 MCMC）；(4) §6.1 有赞调度感知差异化弃用阈值（日 15 天/周 6 周/月 3 月/季 6 月）+MIN_AGE_DAYS=30+PROTECTED_TABLES 白名单；(5) §9 补 3 项。维持 draft |
| 2026-08-10 | 1.1.0 | 矛盾修复+施工算法闭环：effort 校准+L3 主动学习抽样+SPC 冷启动+跨波次重评 | (1) §6.0 示例表 effort 以 §7.0.8 Rubric 重算（restricted_shares 5→7.0/cb_iv 5→8.0/hog 2.5→3.5），矛盾修复；(2) §7.0.6 L3 主动学习分层抽样（不确定层/高风险层必抽+skip-lot 规则）；(3) §7.0.4 SPC 冷启动三阶段（冷启动仅 Shewhart/预热 EWMA 宽松限/稳态全功能）；(4) §6.0 跨波次优先级动态重评算法（证据→权重→priority→批次建议，不自动执行）；(5) §9 补 2 项（纯主动学习/Pareto 前沿排除）。维持 draft |
| 2026-08-10 | 1.2.0 | 漂移来源分类+Shewhart 模式识别+故障归因：Model drift+Western Electric+Innovation-Residual | (1) §3.4 Model drift 漂移来源分类（Data/Concept/Model drift），与腐烂机制正交交叉（来源×机制双标注）；(2) §7.0.4 Western Electric 8 异常模式（Shewhart 后处理，`we_rule` 列）；(3) §7.0.7 Innovation-Residual 故障归因+Detection Limit（2σ_innovation），简化版频率统计；(4) §9 补 2 项（Innovation-Residual 不全实施/DoWhy 排除）。维持 draft |
| 2026-08-10 | 1.3.0 | 名称修正+进度看板+符号漂移检测：Nelson Rules 修正+CSV 看板+symbol-level drift+Hotelling T² 远期 | (1) §7.0.4 Nelson Rules 名称修正（"9 点单侧"是 Nelson 1984 非 WE 1956）；(2) §7.0.9 施工进度 CSV 看板（6 状态+WIP 限制+自动状态推断）；(3) §3.4 Detective 第 5 类检查：代码符号漂移（[dosu.dev 2026-05](https://dosu.dev/blog/score-documentation-freshness-in-ci)：28.9% 仓库文档引用已不存在符号）；(4) §7.0.4 Hotelling T² 远期路径记录；(5) §9 补 2 项（FMEA RPN/Staleguard 等外部工具排除）。维持 draft |
| 2026-08-10 | 1.4.0 | SPC 误报率风险矩阵+自适应控制限+回滚效能度量：Nelson 风险矩阵+AIAG 自适应 SPC+MTTD/MTTR | (1) §7.0.4 Nelson Rules 误报率风险矩阵（默认集 Rule 1/2/3/5 vs 诊断集 4/6/7/8，[ifactoryapp 2026-06](https://ifactoryapp.com/blog/western-electric-nelson-rules-pharma) ARL 数据）；验证 Nelson=WE 超集；(2) §7.0.4 自适应控制限（基线重算 4 触发条件，不引入 AI 增强）；(3) §7.0.9 MTTD ≤7 天/MTTR ≤14-30 天回滚效能度量（≥5 次事件后计算均值）；(4) §9 补 1 项（AI 增强自适应 SPC 排除）。维持 draft |
| 2026-08-10 | 1.5.0 | 技术债视角+环检测+指标分类：SQALE TDR+Kahn 环检测+Leading/Lagging | (1) §6.0 SQALE 技术债视角（TDR≈63%→E 级 Severe；Kano 作 Annual-Interest 代理；Fowler 四象限映射）；(2) §7.0.3 Kahn 环检测显式流程（检测→定位→记 ARCH 条目人工裁定，`cycle_warning.csv`）；(3) §7.0.4 Leading vs Lagging 指标分类（与 MTTD/MTTR 联动）；(4) §9 补 2 项（KB 消费指标/Financial Impact 排除）。维持 draft |
| 2026-08-10 | 1.6.0 | Leiden 升级+Cognitive/AI-Generated Debt+Binarly 再分配+paired-model | (1) §7.0.3 Louvain→Leiden 升级（修复分辨率限制+断连社区两 bug，[metricgate 2026-02](https://metricgate.com/blogs/community-detection-louvain-vs-leiden/)）；(2) §6.0 Cognitive Debt+AI-Generated Debt 第五类（AI 施工天然风险；cycle time/Rework rate/L3 覆盖率三指标）；(3) §6.0 Binarly 权重再分配（缺失分量 W 按比例再分配）；(4) §3.4 paired-model 双 LLM 远期路径（kappa=0.532，当前不采纳）。维持 draft |
| 2026-08-10 | 1.7.0 | Temporal Coupling+Data Contract+SATD 传播+AI 技术债 7 类+Leiden 修正 | (1) §7.0.3 Temporal Coupling 隐藏依赖（Jaccard co-change，阈值 0.5，冷启动 commit<50；施工调度四件套）；(2) §2.2 Data Contract ODCS 概念重构（六组件完整度映射，Semantics 层缺口=本审查核心；不引入 YAML 工具链）；(3) §6.0 SATD 跨制品传播优先级（chain_length×情感加权调 confidence）；(4) §6.0 AI 技术债 7 类映射（覆盖 6/7，Model Debt 不适用）；(5) §7.0.3 Leiden 选型结论修正（全文 Louvain→Leiden 同步）。维持 draft |
| 2026-08-10 | 1.8.0 | Temporal Coupling 增强+确定性排序+环路径提取+predict Omissions+ODCS v3.1.0 | (1) Temporal Coupling commit-size 归一化（MAX_FILES_PER_COMMIT=15，[Archy #131](https://github.com/hslee16/Archy/issues/131)）；(2) CodeScene 三信号说明（仅用信号 a co-change）；(3) Sum of Coupling 聚合度（枢纽表识别）；(4) Kahn min-heap 确定性排序（(priority DESC, name ASC)，可复现）；(5) DFS 三色标记环路径提取（`cycle_paths.csv`）；(6) Tarjan SCC 远期路径（环>5 时升级）；(7) §7.0.5 predict Omissions schema↔doc 共变检测（Temporal Coupling 逆运算，HIGH/MEDIUM/LOW 分级，注入增量更新流程；不自动修复）；(8) §2.2 ODCS v3.1.0 版本号+DCS 弃用说明；(9) §9 补 2 项。维持 draft |
| 2026-08-10 | 1.9.0 | 新鲜度度量升级+状态指纹+假新鲜失败模式+验证信任模型：Freshness SLO/SLI+OKF v0.2+DataHub verifiedAtVersion+DZone 五模式+Attested Computation | (1) §7.0.4 Freshness SLI（timeliness≥7.0 表数/总表数）+SLO=90%+Error Budget 消耗规则；Age-based vs Lag-based 区分；(2) §7.0.4 OKF v0.2 stale_after 固定日期对比（保留状态指纹+time_decay 双机制）；(3) §7.0.5 DataHub docFreshnessInfo verifiedAtVersion 状态指纹（BLAKE3 联合 hash+一跳 lineage 传播，补 git diff 上游级联盲区；`scripts/freshness_fingerprint.py`）；(4) §3.4 DZone 五种假新鲜失败模式（模式 2 补动态表名追踪/模式 5 补回滚版本校验）；(5) §7.0.6 OKF generated vs verified 分离（frontmatter verification_status）+Attested L3 抽检清单 4 检查点（未 verified 不计入覆盖率）；(6) §9 补 2 项（OKF 密码学 attestation/DataHub 工具链排除）。维持 draft |
| 2026-08-10 | 2.0.0 | 2026-08 最新研究评估闭环：SetGo metadata readiness 工具链评估排除 | §9 补 SetGo 排除——[SetGo SSDBM '26 2026-08-11](https://dlnext.acm.org/doi/10.1145/3828820.3828827) 六维 metadata readiness 中 3 维不适用或已覆盖（许可/目录就绪/可复现），其余 3 维由 Q score+ODCS 6 组件覆盖；面向科学数据集对外发布，本审查无此需求；assess→enrich 思想已由 §7.0.2+§7.0.1+§7.0.6 覆盖。本版本标志 2026-08 全网最新研究已全部评估完毕，算法体系达完整性闭环。维持 draft |
| 2026-08-12 | 2.1.0 | 全量重扫核验修正：三层覆盖口径+真闲置收敛+设施盘点+施工计划重 scope | **2026-08-12 git 提交态全量重扫核验**：(1) 基数修正——表数 102→103（`market_stock_valuation` 新增）、受扫文档 42→46 篇、字符量 4.59M→5.24M；(2) 三层覆盖口径——消费层 37（35.9%）/规划层 53（51.5%）/零覆盖 13（12.6%），v0.2.0 的"37.3%"实测即消费层口径，任一文档命中口径虚高 87.4% 废弃，施工目标以消费层为准；(3) 真闲置 3→1 张（仅 `index_meta`）+新增 §6.1b"代码零引用但规划已登记"6 张（dividend_tax_node 改判 dormant VIEW 免归档）；(4) §5 全部数字实测重算（热度榜/零文档缺口 15→12 张/低频表复核）；(5) §2.4 已施工设施盘点——被审查对象全部已施工，审查工具链全部未施工，`src/zephyr/data/ingestions/` 不存在（§7.5 路径修正）；(6) §7 施工计划重 scope——消费层缺口 59 张，覆盖轨迹 35.9%→44.7%→68.9%→93.2%，registry 补齐 26→27 张；(7) §10 Q1 收敛 1 张+新增 Q8；(8) §9 补 2 项；(9) v0.2.0 历史数字不可复现声明（扫描输出须入 git 快照）。全网验证：[modern-datatools.com 2026-04](https://www.modern-datatools.com/blog/data-baselining-warehouse-lifecycle-2026) 三层基线法+"20% 表活跃"企业常态反衬 99.0% 健康。**施工执行插曲**：回填过程遭遇并发会话 stash 隔离清空暂存区事故，全部修改经 dangling blob（f34adb8b）字节级恢复——教训记入 project_memory（git add 快照是最小保护层）。维持 draft（Q1/Q8 待人裁定 + 三波施工未执行） |
| 2026-08-14 | 2.1.1 | 压缩精简 | 压缩精简：噪音去除+施工细节梳理，零信息丢失审查通过（AI-DOCS-001）——2703 行→1390 行（51.4%）；章节标题与编号一字不动；101 表盘点清单/五档分级、三波接入计划与验收标准、闲置表清单、每张表处置裁定全部完整保留；折叠审计方法论过程叙述与已完成阶段性总结（结论+日期保留）；frontmatter version patch+1、date 同步 |
| 2026-08-15 | 2.1.2 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-04）——§5.1 三层口径说明与 §2.2 口径修正重复段并指（17/64 号 53 张/87.4% 虚高论证保留在 §2.2 单处）；§5.2 热度表注不可复现声明并指 §2.2 | 8 类扫描 2 处均为类别 3（重复信息）；18 项口径表/利用率表/批次清单/算法参数零丢失 |
