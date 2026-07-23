---
module_id: INDEX-CODE-WIKI
title: "ZephyrAlpha Code Wiki 与数据库架构审查 · 索引"
doc_type: index
rule_form: declarative
status: active
version: 1.0.0
date: 2026-07-23
owner: ZephyrAlpha-Owner
ttl: permanent
language: zh
created_by: agent
---

# ZephyrAlpha Code Wiki 与数据库架构审查

> 生成日期：2026-07-22（2026-07-23 重建，原目录曾被并发会话工作区清理误删后由原子代理完整重写）
> 生成方式：多代理并行静态审查 + 数据库只读实测（ClickHouse 26.6.1.1193 实测连通）
> 审查假设：**当前数据库仅用于回测**（实盘交易后续再开发），实盘就绪度仅作未来方向提示。
> 本目录全部文档为**只读审查产物**，未修改任何项目代码。

## 一、Code Wiki（项目理解文档）

| 文件 | 内容 |
|------|------|
| [00_overview.md](00_overview.md) | 项目定位、整体分层架构（mermaid）、核心系统与入口、完整运行方式（CLI / integrator / Panel / Docker） |
| [01_repository_layout.md](01_repository_layout.md) | 仓库布局与 43 包 / 2474 个 py 文件全模块清单（职责、关键类与函数、规模），含疑似孤儿/重复/命名异常模块清单 |
| [02_data_layer.md](02_data_layer.md) | 数据库架构全景：ClickHouse（101 表实测）/ PostgreSQL depgraph（46 表）/ governance.db（38 表）分工矩阵、完整表清单、读写路径与治理规则 |
| [03_data_sources_and_downloaders.md](03_data_sources_and_downloaders.md) | 数据源集成与下载机制：实测 128 任务（121 活跃）/ 10 Provider / 13 档调度，断点续传、熔断、质量门、去重、回填全链路 |
| [04_trading_domains.md](04_trading_domains.md) | 交易与策略 24 域：factor→signal→pf→ex→risk→reporting 链路、各域入口与关键类、域间数据流图 |
| [05_governance_and_infra.md](05_governance_and_infra.md) | 治理与基础设施：GitCommitGateway/session_worktree 提交链、~78 个 commit gates、38 个 reconcilers、depgraph 双态、32 个 registry、SSoT 铁律 |
| [06_dependencies.md](06_dependencies.md) | 依赖关系图谱：外部依赖分组解读、跨模块依赖三表（124 条）、depgraph 实测（63 域 / 2728 模块）、3 张关键链路 mermaid 图 |

## 二、数据库专业审查（机构级标准，回测场景）

| 文件 | 内容 |
|------|------|
| [audit_01_schema_review.md](audit_01_schema_review.md) | 101 张 ClickHouse 表逐表 schema 审查：字段类型、排序键/分区键、引擎与去重语义、时区/复权/元数据字段，逐表 ✅/⚠️/❌ 评分 + P0-P2 问题清单 |
| [audit_02_pipeline_review.md](audit_02_pipeline_review.md) | 数据下载与集成管线审查：10 项机制评分、数据覆盖缺口表（含实测 25 FAILED 任务、数据空洞）、P0-P2 问题清单 |
| [audit_03_checklist_and_verdict.md](audit_03_checklist_and_verdict.md) | 完整审查清单（10 大类 64 检查项）+ 逐条打分 + 总评 **81.3%（B+）** + 四阶段改进路线图 |

## 三、外部设计文档落地比对

| 文件 | 内容 |
|------|------|
| [ext_01_depgraph_docs_review.md](ext_01_depgraph_docs_review.md) | `D:\临时工作区\依赖图` 31 份域文档 + yaml/csv 的数据库设计提取与落地核验：26 项规格 = 0 完全落地 / 15 部分落地 / 11 未落地 |
| [ext_02_arch_docs_review.md](ext_02_arch_docs_review.md) | `D:\临时工作区\架构图` 数据架构.md v6.0 等的设计提取与落地核验：DuckDB 选型已被项目正式推翻改 ClickHouse（决策正确），最大缺口 = Feature Store |

## 四、头号发现速览（详见各审查文档）

**回测可信度头号缺陷（P0）**

1. **幸存者偏差**：stock_list 5,534 只全部为在市股，无退市股——策略层有 survivorship_policy 声明但数据层未兑现（audit_03 P0-1）。
2. **质量门有壳无芯**：`data/quality_gate.py` 仅 27 行 re-export 壳、写入路径零消费方，`quality_flag` 恒为默认值 1，脏数据可直进回测（audit_02）。
3. **tick 数据空洞**：2026-06 起 tick 日均行数较前月低约 90%，缺口未补；昨日（07-21）tick_data 0 行（audit_02/03）。
4. **option_iv_surface 排序键缺 option_type**：call/put 互相覆盖静默丢数据（audit_01 P0）。
5. **18 张元数据缓变维表无时点版本** → 回测前视偏差通道；财报无 point-in-time 快照（audit_01/02）。

**外部文档结论**：两个文件夹中的数据库设计**并未全部落地**——存储引擎（ClickHouse）已落地且超出文档设计，但 Feature Store（P0 缺口）、Redis 热层、数据血缘（OpenLineage）、数据质量 SLA 分级、D-DATA-ENG 数据工程域（`src/zephyr/data_eng/` 为空目录）等高价值设计均未落地。文档中也不存在比项目现有实现"全面更优"的数据库架构——项目治理体系远超外部设计，业务数据治理落后于外部设计。

**强项（达机构级）**：管线容错 94%、治理血缘 93%、安全 92%；断点续传/攒批写入/WAL/周末回填经真实事故迭代成熟；#ARCH-CH-020（tick_data 排序键缺 price）已修复并实测确认。
