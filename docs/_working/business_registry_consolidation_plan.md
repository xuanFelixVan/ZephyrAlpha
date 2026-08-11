# 业务注册表体系施工方案（临时工作文档）

> **状态**：临时工作文档 / 讨论载体 / 待裁定
> **位置**：`docs/_working/`（临时区，定稿后正式条目迁入 `docs/01_policies_and_standards/_registry/catalogs/`）
> **创建**：2026-08-10
> **性质**：本文件是讨论载体，不是正式 design memo。设计定稿后，本文件可删除或归档，正式注册表 YAML 落盘到 catalogs/。

---

## 1. 背景与问题诊断

### 1.1 已有基础设施（好消息）

项目已建成成熟的注册表治理体系，核心是 [registry_of_registries.yaml](file:///d:/ZephyrAlpha/docs/registry_of_registries.yaml)——"注册表的注册表"，自述为：

> 所有子注册表的中央汇聚点。任何 AI 或人类需要了解"项目有哪些登记表、在哪、管什么"时，以此为唯一入口。

已具备：
- **3 层 52 个注册表**（tier0 核心源码级 12 / tier1 治理政策级 28 / tier2 数据运行时级 12）
- **AI 使用指南**：discover / create / delete / validate 四流程
- **一致性校验脚本**：`audit_registration.py` / `check_g6_ctr_compliance.py` / `generate_registry_master_index.py`
- **自动派生索引**：[registry_master_index.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml)

### 1.2 核心矛盾（问题）

52 个注册表管到了 gate/script/module/blueprint/error_code/术语表/目录/依赖/攻击场景/状态机，**唯独最核心的业务资产——因子、策略、指标、算法、风控限额——一个都没登记进统一入口**。

对照 8 项业务清单：

| 业务清单 | 在 registry_of_registries 登记？ | 真实状态 |
|---|---|---|
| ①数据源+数据集目录 | 🟧 部分（dataflow_graph_registry.yaml 管数据集，不管数据源供应商） | 数据集有，数据源散落 |
| ②字段字典 | ❌ 未登记 | 散在代码 contracts/，无总表 |
| ③技术指标清单 | ❌ 未登记 | 16号骨架 draft + 代码，游离 |
| ④因子库 | ❌ 未登记 | 代码 + 15/25号文档散落，0 注册表 |
| ⑤策略库 | ❌ 未登记 | 20/24/25/26/27号文档 + 代码，0 注册表 |
| ⑥回测/实验注册表 | ❌ 未登记 | 51号 + 代码，游离 |
| ⑦风控限额表 | ❌ 未登记 | 代码 + config，游离 |
| ⑧执行算法库 | ❌ 未登记 | 40号 + 代码，游离 |

**根因**：业务核心清单全部游离在注册表体系之外。AI 答不出"有多少因子/策略"的根因不是没数据，是没登记。

### 1.3 统一入口不够显化（关键问题）

> 用户原话："有一个统一的查询入口，但是你并不知道，这就存在很大的问题——它不够显化。"

`registry_of_registries.yaml` 存在但**未被强显化**：
- AGENTS.md 未在冷启动必读段强制引用
- 新 AI session onboarding 无"必须读 registry_of_registries"检查
- 07_trading_decision_architecture/00_index 等业务总索引未反向链接
- 结果：AI 不知道入口存在 → 不查 → 业务清单游离 → 信息不可达

**显化是本次施工的第一优先级**，与建注册表本身同等重要。

---

## 2. 目标

### 2.1 总目标
1. **一次建全** 8 个业务注册表（因子/策略/技术指标/执行算法/风控限额/数据源+数据集/字段字典/图形形态库）
2. **统一入口显化**：让所有未来 AI 进项目就知道 registry_of_registries.yaml 是唯一查询入口
3. **真源唯一**：每个业务资产有且仅有一个注册表作为 SSoT，消除散落与重复
4. **全项目对齐**：所有相关文档/代码/AGENTS.md 反向引用注册表

### 2.2 验收标准
- [ ] 7 个业务注册表 YAML 落盘到 `catalogs/`，并在 registry_of_registries.yaml 登记
- [ ] `audit_registration.py` 扫描通过，无 broken/pending
- [ ] AGENTS.md 冷启动段强引用 registry_of_registries.yaml
- [ ] 新 AI session 能在 1 跳内从 AGENTS.md 找到任一业务清单
- [ ] 16号技术指标文档与 technical_indicator_registry.yaml 真源对齐（文档派生自注册表或退役）
- [ ] dataflow_graph_registry.yaml 扩展 sources 段（待裁定确认后）

---

## 3. 待裁定设计问题（核心讨论区）

> 以下为初步分析，**待用户确认后定稿**。每项标注【初步建议】与【待确认】。

### 3.1 粒度：策略/因子记到什么层级

**机构实践**：
- WorldQuant：`alpha`（单个信号表达式）→ `strategy`（alpha 组合）
- AQR：`strategy` → `sub-strategy`（如 Trend → Time-Series Momentum / Cross-Sectional Momentum）
- Two Sigma：`strategy` → `sub-strategy` → `signal`
- 判据：**共享 sleeve（账本/资金池/风控）= 同一 strategy 下的 sub-strategy；独立 sleeve = 独立 strategy**

**打板连板 vs 趋势低吸案例分析**：
- 策略层：打板是一个独立 sleeve（小账本），连板/趋势是 sleeve 内模式切换（20号 v1.4.1 已定义自适应切换）→ **1 strategy + 2 sub-strategies**（非 2 个独立 strategy）
- 因子层：连板因子（梯队结构 alpha）vs 趋势因子（动量 alpha）来源完全不同 → **2 个独立 factor**

**【初步建议】**：
- 策略注册表支持 `strategy_id` + `parent_strategy_id` 层级字段。打板=1条 strategy，连板/趋势=2条 sub-strategy（parent 指向打板）。查表能看到 3 条，也能按 parent 聚合成 1 条。
- 因子注册表每个独立 alpha 一个 `factor_id`，连板因子/趋势因子=2 条独立记录。
- 满足"越细越好"+"能聚合"双需求。

**【待确认】**：层级字段命名（parent_strategy_id vs strategy_group_id）、sub-strategy 的英文术语（sub-strategy / variant / mode 三选一，倾向 sub-strategy 对标 AQR）。

### 3.2 数据源 vs 数据集：合并还是分开

**机构实践**：OpenLineage/Marquez 模型里 `Source`（外部数据源）/ `Dataset`（数据集）/ `Job`（作业）是**一个模型内的三类实体**，不是三个独立注册表。

**现状**：dataflow_graph_registry.yaml 已有 `datasets:` + `jobs:` 段（对标 OpenLineage），但缺 `sources:` 段（数据源供应商：miniQMT/AkShare/TDX 的连接/频率/SLA/成本/合规）。

**【初步建议】**：**合并**。扩展 dataflow_graph_registry.yaml 新增 `sources:` 段，与 datasets/jobs 并列。理由：
- 真源唯一（避免数据集在 A、数据源在 B 的对账问题）
- 对标 OpenLineage 三实体一模型
- datasets 段已通过 produced_by_job 建立关联，sources 段通过 `provides_datasets` 关联到 datasets
- 符合用户"真源唯一责任唯一"原则

**【待确认】**：
- 是否改名 `dataflow_graph_registry.yaml` → `data_registry.yaml`（定位从"数据流图"扩展为"数据全景"）？倾向改名以反映扩展后的职责。
- sources 段 schema：source_id / provider_name / connection_type / frequency / sla / cost / compliance / provides_datasets[]

### 3.3 存储格式：YAML vs 数据库

**机构实践**（规模决定）：
| 规模 | 实践 | 代表 |
|---|---|---|
| alpha/因子 < 几百 | YAML + git | 小团队、开源 Kedro |
| alpha/因子 > 几千 | 数据库 | WorldQuant/Two Sigma/AQR |
| 实验追踪 | 数据库 | MLflow（SQLite/PG/MySQL） |
| 特征存储 | DB 后端 + YAML config | Feast |
| 普遍模式 | **DB + YAML 双轨**：结构化元数据进 DB，配置/小清单用 YAML | 机构标准 |

**项目现状与先例**：
- 已有 PostgreSQL（depgraph 9122 节点 + 路径全景图已在 PG）→ 大规模用 DB 项目已实践
- 52 个注册表是 YAML → 小规模治理清单用 YAML 已成体系
- 当前因子 ~15+ 模块、策略 5 候选 3 首批 → **小规模**

**【初步建议】**：**分阶段**
- **现阶段（因子<500 / 实验<5000）**：YAML 真源 + git 追踪。理由：AI 友好（读写 YAML 比 SQL 容易）、git diff 可审计、与现有 52 注册表体系一致、无额外 DB 运维
- **设计预留 DB 迁移**：schema 字段按 DB 表结构设计（每条记录有 id/created_at/updated_at/version/status），未来可一键迁移到 PG
- **迁移触发阈值**：因子>500 或 实验>5000 时迁 PG，YAML 降级为"导出快照"
- **混合模式**：结构化元数据（编号/状态/关系）YAML 入 git；大规模时序数据（IC 历史/回测结果/每日快照）进 ClickHouse/PG 不入 git（Feast/MLflow 模式）

**【待确认】**：迁移阈值具体数值、是否现在就为因子/策略注册表预留 PG 表 DDL 草案。

### 3.4 技术指标清单：注册表 vs 文档

**用户裁定**："按第一性原理长远规划，建好了注册表就不用保留文档。"

**【建议执行】**：
- 新建 `technical_indicator_registry.yaml` 作为 SSoT（指标编号/公式/参数/输入输出列/状态/代码位置）
- 16号文档 (`16_technical_indicator_catalog.md`) 的 §2 清单数据迁入注册表
- 16号文档降级为"why 层说明"（设计原则/双模式计算/宽表存储理由）或整体退役
- 倾向：保留 16号文档作为 why 层（设计原则需要叙述），§2 清单数据迁注册表，文档不再维护表格只引用注册表

**【待确认】**：16号文档是保留为 why 层还是整体退役。

### 3.5 显化策略：如何让统一入口被所有 AI 知道

**问题**：registry_of_registries.yaml 存在但 AI 不知道 → 等于不存在。

**【初步建议】** 多重显化：
1. **AGENTS.md 冷启动段**：在 AI 必读区加强引用"业务资产查询必读 registry_of_registries.yaml"（受 AGENTS.md ≤3000 行硬约束，需等量退役或精简）
2. **反向链接**：07_trading_decision_architecture/00_index、system_charter、各 design memo 在引用业务资产处加 registry 链接
3. **onboarding 检查**：新 AI session 启动检查清单加"已读 registry_of_registries.yaml"项
4. **pre-commit hook**：新增/修改业务资产代码时检查是否在注册表登记
5. **CapabilityLookup 扩展**：项目已有 `src/zephyr/governance/capability_lookup.py`，扩展其扫描范围覆盖 7 个新注册表

**【待确认】**：AGENTS.md 等量退役哪些内容腾出空间；onboarding 检查落地形式。

---

## 4. 施工方案（待设计定稿后细化）

### 4.1 十二个业务注册表清单

| # | 注册表 | 真源文件 | 形态 | 优先级 |
|---|---|---|---|---|
| 1 | 因子库 | `catalogs/factor_registry.yaml` | 新建 YAML | P0 |
| 2 | 策略库 | `catalogs/strategy_registry.yaml` | 新建 YAML | P0 |
| 3 | 技术指标清单 | `catalogs/technical_indicator_registry.yaml` | 新建 YAML（16号§2迁入） | P0 |
| 4 | 股票池 | `catalogs/universe_registry.yaml` | 新建 YAML（回测必需） | P0 |
| 5 | 基准 | `catalogs/benchmark_registry.yaml` | 新建 YAML（回测必需） | P0 |
| 6 | 交易成本模型 | `catalogs/cost_model_registry.yaml` | 新建 YAML（回测必需） | P0 |
| 7 | 执行算法库 | `catalogs/execution_algo_registry.yaml` | 新建 YAML（40号提取） | P1 |
| 8 | 风控限额表 | `catalogs/risk_limit_registry.yaml` | 新建 YAML（代码+config提取） | P1 |
| 9 | 数据源+数据集 | 改名 `catalogs/data_asset_registry.yaml`（原 dataflow_graph，加 sources 段） | 改名扩展 | P1 |
| 10 | 图形形态库 | `catalogs/chart_pattern_registry.yaml` | 新建 YAML（8大类） | P1 |
| 11 | 字段字典 | `catalogs/field_dictionary.yaml` | 新建 YAML（代码 contracts 提取） | P2 |
| 12 | 实验/回测目录 | `catalogs/experiment_registry.yaml` | 新建 YAML（等51号落定施工） | P2 |

### 4.2 阶段划分（初拟）

**Phase 0：设计定稿**（当前阶段，本文档讨论）
- 待裁定问题 3.1-3.5 全部确认
- 每个注册表 schema 草案定稿

**Phase 1：P0 三注册表施工**（因子/策略/技术指标）
- 新建 3 个 YAML + 填充数据（从代码/文档反查）
- registry_of_registries.yaml 登记 3 条
- 显化整改（AGENTS.md + 反向链接）
- audit_registration.py 校验通过

**Phase 2：P1 三注册表施工**（执行算法/风控限额/数据源扩展）
- 新建 2 个 YAML + 扩展 dataflow
- 登记 + 显化 + 校验

**Phase 3：P2 + 收尾**（字段字典 + 全项目对齐）
- 字段字典 YAML
- 全项目反向引用扫描
- 16号文档处置
- 验收

### 4.3 schema 设计原则（所有注册表通用）

- 每条记录：`<entity>_id`（唯一编号）/ `name` / `name_zh` / `status` / `version` / `created_at` / `updated_at` / `owner` / `module_id`（关联 depgraph）/ `doc_ref`（关联 design memo）/ `code_path`
- DB 迁移预留：字段命名 snake_case、有主键、有时间戳、有状态机
- 与现有 52 注册表 frontmatter 字段对齐（frontmatter_field_registry.yaml 已定义 40 字段）
- 真源唯一：每个实体只在一个注册表登记，其他地方只引用 `<entity>_id`

### 4.4 数据填充策略（半派生）

- **手写真源**：编号/状态/alpha来源/文档链接/业务语义 → 入 git
- **脚本反查补全**：代码位置/模块号/构建状态/依赖关系 → 从 depgraph + 代码扫描自动补全
- **派生产物不入 git**：生成的可读 md 总表不入 git（符合硬约束）

---

## 5. 风险与约束

| 风险/约束 | 应对 |
|---|---|
| AGENTS.md ≤3000 行硬约束 | 显化内容需等量退役或精简，不能简单追加 |
| 派生产物禁止入 git | 总表 md 派生不入 git，YAML 真源入 git |
| 新增模块须登记 ARCH | 7 个注册表新建须在 architecture_issue_registry.yaml 登记 ARCH 条目 |
| 注册表创建须生成 creation_token | 遵循 capability_canonical_file_registry.yaml 既有流程 |
| 过度工程风险 | 远期可选（模型注册表/事件告警/复盘登记）不建，聚焦 7 个必备 |
| 16号文档处于骨架先行纪律 | 处置需遵循骨架→active 升级流程，不能直接删 |

---

## 6. 调研报告与裁定结果

> 调研日期：2026-08-10。证据来源：项目内文档全扫 + 外部机构实践（WorldQuant/AQR/Two Sigma/Feast/MLflow/OpenLineage/QuantConnect/qlib/DAMA-DMBOK/AGENTS.md 标准）。
> 立场：客观专业架构师，第一性原理 + 长远战略，针对 100% AI 开发场景。

### 裁定 1：sub-strategy 术语 → 采用 `variant`（弃 sub-strategy）

**项目内证据**：
- 现有注册表层级实践：`architecture_issue_registry.yaml` 用 `category:` 分组；`functional_domain_registry.yaml` 的 `parent_domain` 经 D38 裁定"仅作分组属性，不表示层级子域"——项目对层级字段持谨慎态度
- `strategy_registry.py` 代码层存在（src/zephyr/governance/strategies/），但 strategy_registry.yaml 注册表不存在

**机构实践**：
- AQR 不用 sub-strategy，用 "capabilities"；Two Sigma 用扁平化 "research asset"；QuantConnect 用 "AlphaModel"
- sub-strategy 在对冲基金行业偶见（multi-manager pod 模型），**非系统化量化机构标准术语**
- variant/mode 更贴合"同一策略的不同实现版本或运行模式"

**第一性原理分析**：
- sub-strategy 暗示"子策略"有独立治理负担（独立状态/版本/风控），但打板连板/趋势低吸共享一个 sleeve（小账本），是 sleeve 内模式切换，不是独立子策略
- `variant` 直观表达"实现变体"，自描述性强；100% AI 开发下术语要"看名知义"
- 因子层每个独立 alpha 天然独立（alpha 来源不同），不需要 variant 字段——factor_id 唯一即可

**裁定结果**：
- 策略注册表采用 `variant` 字段（不用 sub-strategy）。打板 = 1 strategy，连板/趋势 = 2 variants（variant_id=connection_led / trend_low_absorb，parent 指向打板 strategy_id）
- 因子注册表每个独立 alpha 一个 `factor_id`，不用 variant（连板因子/趋势因子=2 条独立记录）
- 不强制层级（借鉴 D38 裁定精神），variant 是可选分组属性

---

### 裁定 2：数据源合并 → 扩展 dataflow_graph_registry.yaml 加 sources 段，不改名

**项目内证据**：
- dataflow_graph_registry.yaml 已有 `datasets:` + `jobs:` 段（对标 OpenLineage），含 DS-001 tick / DS-002 ohlc_bar 等，有 pit_policy/contract_ref/module_id
- 缺 `sources:` 段（数据源供应商：miniQMT/AkShare/TDX 连接/频率/SLA/成本/合规散在 15号文档 + config/.env.qmt）
- 现有命名"数据流图注册表"，description 明确"与 depgraph 正交，表达数据流向"

**机构实践**：
- OpenLineage/Marquez：**单一统一模型** Source/Dataset/Job + namespace 区分类型，不为每类资产建独立模型
- Source 实体管"命名空间+连接信息"，Dataset 管"数据内容"，Job 管"产生/消费"
- 关联：Job → 产生/消费 → Dataset → 属于 → Source

**第一性原理分析**：
- 数据源/数据集/作业是数据生命周期的三个环节（源→集→流），分三个注册表会产生"数据集在 A、数据源在 B"的对账负担，破坏真源唯一
- OpenLineage 已验证三实体一模型可行，是行业标准
- 改名 data_registry.yaml 会丢失"流"的动态语义，且引发全项目引用更新（治理成本高）

**裁定结果**：
- 扩展 dataflow_graph_registry.yaml 新增 `sources:` 段，**不新建 data_source_registry.yaml**，**不改名**
- sources 段 schema：`source_id` / `provider_name` / `connection_type` / `frequency` / `sla` / `cost` / `compliance` / `provides_datasets[]`
- 在 description 补充"含数据源(sources)/数据集(datasets)/作业(jobs)三实体，对标 OpenLineage"
- 7 个注册表实际 = 6 新建 + 1 扩展

---

### 裁定 3：YAML vs DB → 现阶段 YAML 真源 + DB 预留，迁移阈值因子>500/实验>5000

**项目内证据**：
- 项目已有双轨先例：depgraph（9122 节点）+ 路径全景图在 PostgreSQL；52 个注册表是 YAML
- 当前因子 ~15+ 模块、策略 5 候选 3 首批——**小规模，远低于迁移阈值**
- AGENTS.md §11.0.2 已有"YAML 真源 vs DB 真源分类铁律"

**机构实践**：
- Feast：YAML/Python 存定义 + SQLRegistry 存运行时；迁移触发=多并发写/多 feature view materialization
- MLflow：代码配置 + DB backend；迁移阈值 ~100 runs / >1 人 / 跨环境
- 主流迁移临界点：~500 条目 / ~100 实验 / 多并发写 / 跨条目查询
- 双轨分工：YAML 存"定义/启动配置"（静态、可 git diff），DB 存"运行时元数据/状态"（动态、可查询）

**第一性原理分析**：
- 100% AI 开发场景，YAML 对 AI 更友好（读写/git diff/可审计/无需 SQL 运维）；DB 增加 AI 复杂度
- 但大规模必须 DB（查询/并发/版本/历史）——这是客观规律
- 现阶段小规模 + 无并发写 + AI 友好 → YAML 是正确选择
- 设计必须预留 DB 迁移路径（schema 按 DB 表设计），避免未来迁移推倒重来

**裁定结果**：
- **现阶段 YAML 真源入 git**，schema 按 DB 表设计（每条记录有 `id` / `created_at` / `updated_at` / `version` / `status`）
- **迁移阈值**：因子 >500 或 实验 >5000 或 出现并发写需求时迁 PostgreSQL（复用 depgraph PG 实例）
- 迁移后 YAML 降级为"导出快照"（定期生成不入 git）
- 混合模式：结构化元数据（编号/状态/关系）YAML 入 git；大规模时序数据（IC 历史/回测结果/每日快照）进 ClickHouse/PG 不入 git

---

### 裁定 4：16号文档 → 降级为 why 层，§2 清单迁注册表

**项目内证据**：
- 16号 draft v0.1.0 骨架：§2 清单冻结（40 指标/5 类/~55 输出列），§3-§6 待填（算法实现规范/双模式计算/宽表存储/A股约束）
- §2 是结构化数据（表格），§3-§6 是叙述性 why（设计原则/理由）

**机构实践**：
- QuantConnect `QuantConnect.Indicators` 命名空间 ~100+ 指标类 + 独立文档对应
- backtrader `backtrader.indicators` ~50+ 指标 + 文档
- qlib Alpha158/360 表达式引擎 + 文档说明
- 共性：**代码库组织 + 独立文档对应，两者不合一也不完全废弃文档**

**第一性原理分析**：
- 技术指标有两个维度：
  - "是什么"（清单/公式/参数/输入输出列）= 结构化数据 → 进注册表（可查/可校验/可派生）
  - "为什么这么设计"（纯自实现不引 TA-Lib/双模式计算/宽表存储/A股约束）= 叙述性 why → 留文档
- 用户原则"建好注册表就不用保留文档"针对的是"表格数据重复维护"，why 层叙述不是表格，保留有价值
- 100% AI 施工时需要理解 why（为什么纯自实现、为什么宽表存储），文档是 AI 施工的上下文

**裁定结果**：
- 新建 `technical_indicator_registry.yaml` 作 SSoT（指标编号/公式/参数/输入输出列/状态/代码位置）
- 16号 §2 清单数据迁入注册表
- 16号文档**保留为 why 层**（设计原则/双模式计算/宽表存储/A股约束理由），§2 改为引用注册表，不再维护表格
- 16号升级为 active（脱离骨架态），定位明确为"技术指标设计 why 层"
- **不整体退役**——why 层有独立价值

---

### 裁定 5：AGENTS.md 显化 → 不需等量退役，在 RULE-REGISTRY 段强化

**项目内证据**：
- AGENTS.md = **1248 行**（硬约束 ≤3000 行，**有 ~1750 行空间，无需退役**）
- L135 已有 `## RULE-REGISTRY：第四件事（ARCH-053 AI 可发现性，2026-07-06）`
- L137 已引用 registry_of_registries.yaml："查项目所有 registry：MUST 先读 registry_of_registries.yaml（ROOR）"
- 但 RULE-REGISTRY 是通用"注册表发现"规则，**未专门强调业务资产（因子/策略/指标/算法/风控）查询**

**机构实践**：
- AGENTS.md 是跨工具统一标准（Linux Foundation，60000+ repos，被 Codex/Cursor/Copilot/Gemini CLI/Aider/Windsurf/Zed 原生读取）
- 约定文件名 + 自动加载是 AI-native 项目基础
- 文档需"自描述"——开头说明这是什么、谁该读

**第一性原理分析**：
- 问题诊断修正：不是"没引用"（L137 已引用），而是"不够突出业务资产"
- 已有 RULE-REGISTRY 通用规则，缺的是"业务资产查询"的专门指引
- AGENTS.md 有充足空间（1248/3000），强化而非重写，不需退役

**裁定结果**：
- **不需等量退役**
- 在 RULE-REGISTRY 段（L135-150）内增加"业务资产查询"子段，列出 7 个业务注册表名称 + 一句话用途 + 查询入口（registry_of_registries.yaml）
- 在 §3 核心系统"因子信号域"段（L359）补 factor_registry 引用
- 在 §11.0 真源方向决策表（L1096）补业务资产查询行
- 强化方式：把"查因子/策略/指标先读 registry_of_registries.yaml → 跳转 factor_registry/strategy_registry/..."作为显式流程写入

---

### 裁定 6：onboarding 落地形式 → 三重保险（AGENTS.md + session_log + capability_lookup）

**项目内证据**：
- `ai_session_registry.yaml` + `session_log_schema.yaml` 存在（session 管理机制已有）
- `capability_lookup.py` 存在（src/zephyr/governance/，扫描 capability_canonical_file_registry，有 CLI）
- 缺：session_log 无"必读注册表"检查项；capability_lookup 扫描范围不含 7 个新业务注册表

**机构实践**：
- AI 编程工具统一模式：约定文件名 + 自动加载 + 支持 import（Cursor .cursor/rules、Claude Code CLAUDE.md + memory、Windsurf rules）
- vibe coding 社区：AI discoverability 是核心，文档要"写给 AI 读"
- 多重保险优于单一手段

**第一性原理分析**：
- 100% AI 开发下，onboarding 要多重保险——任何单一手段都可能失效（AI 没读文档/没跑检查/工具没扫描）
- 文档指引（AGENTS.md）+ 流程检查（session_log）+ 工具支持（capability_lookup）三重互补
- 复用现有机制，不新建

**裁定结果**：三重落地
1. **AGENTS.md RULE-REGISTRY 段强引用**（裁定 5）
2. **session_log_schema.yaml 加"必读注册表"检查项**：新 AI session 启动时声明已读 registry_of_registries + 7 业务注册表（轻量声明，非阻断）
3. **capability_lookup.py 扩展扫描范围**覆盖 7 个新注册表（已有扫描机制，加 7 个 source 即可，CLI 自动可查）
- 不新建 hook（避免过度工程），靠现有 session_log + capability_lookup 机制

---

### 裁定 7：施工顺序 → P0→P1→P2 三阶段确认，alpha 地基优先

**项目内证据**：
- project_memory："回撤 Protocol 施工优先级：风险相关模块先于策略模块施工至 production"
- 骨架先行里程碑（00_index v2.3.0）
- 当前最缺：因子库 + 策略库（0 注册表）

**机构实践**：
- WorldQuant：alpha 先通过相关性/回测筛选再投产
- Citadel：pod 级风控隔离先于策略上线
- Feast：registry must be configured first（真相源先建）
- MLflow：tracking 先于 model registry
- 共性：**风险优先 + 真相源先行**

**第一性原理分析**：
- 因子/策略/技术指标是 alpha 地基——下游组合/风控/执行都依赖它，最缺最该先建
- 执行算法/风控限额/数据源是交易与风控支撑——依赖 alpha 地基
- 字段字典是数据治理——依赖前面注册表的字段稳定后才有意义
- **注意**：注册表施工顺序 ≠ 模块施工顺序。project_memory 的"风控模块先于策略模块"是模块实现顺序；注册表是"登记"，风控注册表（P1）登记风控限额，风控模块实现是另一条线，两者不冲突

**裁定结果**：P0→P1→P2 三阶段确认
- **P0**：factor_registry / strategy_registry / technical_indicator_registry（alpha 地基，最缺，下游依赖最多）
- **P1**：execution_algo_registry / risk_limit_registry / dataflow sources 段扩展（交易风控支撑）
- **P2**：field_dictionary（数据治理，依赖前面字段稳定）

---

### 裁定 8：字段字典范围 → 仅数据字段，不合并 frontmatter_field_registry

**项目内证据**：
- `frontmatter_field_registry.yaml` = 53 个文档元数据字段（module_id/title/doc_type/status/version/date/owner...）
- 它管"文档长什么样"（frontmatter 治理），**不是数据字段字典**
- 项目无数据字段字典（数据字段定义散在代码 contracts/market_data.py 等）

**机构实践**：
- DAMA-DMBOK：数据字段字典是元数据管理核心，记 field_name/business_definition/data_type/unit/allowed_values/source_system/steward/quality_rules
- dbt `schema.yml`：code-native 数据字段字典
- Collibra/Alation/Amundsen/DataHub：数据字段字典与数据血缘/质量/资产目录集成
- **主流分离**：数据字段字典（管数据层）vs 文档元数据（管文档层），不合一

**第一性原理分析**：
- 数据字段（如 close/open/volume/turnover 的 type/unit/source/复权口径/PIT属性）管"数据内容"
- 文档元数据（frontmatter）管"文档治理"（版本/状态/归属）
- 两者 schema 不同：数据字段需要质量规则/单位/来源；文档元数据需要版本控制/状态机
- 合并会破坏单一职责，导致 schema 混乱

**裁定结果**：
- `field_dictionary.yaml` **仅管数据字段**（行情/因子/特征/输出字段的 type/unit/source/复权口径/PIT属性/quality_rules）
- **不合并** frontmatter_field_registry.yaml（它继续管文档元数据，职责清晰，独立演化）
- 两者独立，各管各的层

---

## 6.x 裁定汇总表

| # | 裁定问题 | 裁定结果 | 关键依据 |
|---|---|---|---|
| 1 | sub-strategy 术语 | 采用 `variant`（弃 sub-strategy） | AQR/Two Sigma 非标准术语；variant 自描述；D38 谨慎层级精神 |
| 2 | 数据源合并 | **扩展并改名为 data_asset_registry.yaml** | 名实相符治本；AI 自描述降长期识别成本；DAMA-DMBOK 标准术语；改名成本<长期成本 |
| 3 | YAML vs DB | 现阶段 YAML + DB 预留，阈值因子>500/实验>5000 | Feast/MLflow 双轨；项目 depgraph PG 先例；AI 友好 |
| 4 | 16号文档 | 降级为 why 层，§2 迁注册表，不退役 | 结构化数据 vs 叙述 why 分离；QuantConnect 代码+文档对应 |
| 5 | AGENTS.md 显化 | 不需退役，RULE-REGISTRY 段强化 | AGENTS.md 1248/3000 有空间；L137 已引用需突出业务资产 |
| 6 | onboarding 形式 | 三重保险（AGENTS.md+session_log+capability_lookup） | 多重互补；复用现有机制；不新建 hook |
| 7 | 施工顺序 | P0→P1→P2 三阶段确认 | alpha 地基优先；注册表顺序≠模块顺序 |
| 8 | 字段字典范围 | 仅数据字段，不合并 frontmatter | DAMA-DMBOK/dbt 主流分离；单一职责 |

---

## 6.y 长远地基复审（2026-08-10）

> 应用户要求复审：确认 8 项裁定均从第一性原理长远地基出发，非图眼前方便。把地基打好优先于眼前省事。

| # | 裁定 | 长远地基复审 | 结论 |
|---|---|---|---|
| 1 | variant 术语 | sub-strategy 语义不符（共享 sleeve 却暗示独立治理）；variant 可扩展（未来 v2 变体）；AQR/QuantConnect 主流不会过时；长远 AI 自描述 | ✅ 长远 |
| 2 | 改名 data_asset_registry | 名实相符是长远治本；AI 自描述消除长期识别摩擦；改名一次性成本可控（reconciler+migration）；这正是用户最初困惑的根因 | ✅ 长远（修订） |
| 3 | YAML + DB 预留 | 非"图眼前方便"——schema 按 DB 表设计预留迁移路径，不锁定 YAML；阈值明确（因子>500/实验>5000）到点即迁；现在因子太少用 DB 是过度工程 | ✅ 长远 |
| 4 | 16号 why 层 | 结构化数据进 SSoT 注册表 + why 叙述留文档，是单一职责分离；设计 rationale（为什么纯自实现/宽表存储）长远 AI 施工必需；不是"保留冗余文档" | ✅ 长远 |
| 5 | AGENTS.md 强化 | AGENTS.md 是 Linux Foundation 跨工具标准（60000+ repos），长远通用；复用既有 RULE-REGISTRY 段非重写；1248/3000 有空间 | ✅ 长远 |
| 6 | 三重保险 onboarding | 复用现有 session_log + capability_lookup，不新建 hook（避免过度工程）；三重互补长远可扩展；单一手段易失效 | ✅ 长远 |
| 7 | P0→P1→P2 | alpha 地基优先（下游组合/风控/执行都依赖）；字段字典最后（依赖字段稳定才定型）；注册表顺序≠模块顺序，不冲突风控优先 | ✅ 长远 |
| 8 | 字段字典仅数据字段 | 数据字段 vs 文档元数据单一职责分离；DAMA-DMBOK/dbt 主流；合并破坏 SRP 长远混乱 | ✅ 长远 |

**复审结论**：8 项裁定均通过长远地基复审。唯一修订：裁定 2 从"不改名"修订为"改名为 data_asset_registry.yaml"（长远成本裁定，治本优于治标）。其余 7 项维持原裁定，均为长远地基方案。

**复审原则确认**：
- 每项裁定都问过"10 年后这个决策还成立吗？"——8 项均通过
- 不为眼前省事牺牲长远清晰（裁定 2 改名、裁定 4 保留 why 层、裁定 8 分离均体现此原则）
- 不为长远完美过度工程现在（裁定 3 现阶段 YAML、裁定 6 不新建 hook 均体现此原则）
- 地基阶段宁可付一次性成本换长期零摩擦

---

## 7. 下一步

§6 裁定全部通过长远地基复审（裁定 2 修订为改名）。进入 §8 schema 草案设计。

---

## 8. 七个业务注册表 Schema 草案

> 设计原则（所有注册表通用，对齐项目既有风格）：
> 1. **frontmatter 头部**对齐 [frontmatter_field_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml)（53 字段标准）：module_id / title / doc_type / status / version / created / last_updated + registry_id / name / description / owner / tier
> 2. **entry_schema 按 DB 表设计**预留迁移：每条记录有 `id`(PK) / `created_at` / `updated_at` / `version` / `status`，未来可一键迁 PG
> 3. **编号格式**：`{PREFIX}-{DOMAIN}-{NNN}`（对齐 module_id_registry allocation_rules）
> 4. **关联字段**：`module_id` 关联 depgraph / `doc_ref` 关联 design memo / `code_path` 关联代码
> 5. **状态机**对齐 [module_lifecycle_status_vocabulary.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/module_lifecycle_status_vocabulary.yaml)：candidate / experimental / active / deprecated / retired
> 6. **性能指标字段**（IC/Sharpe/容量等）运行时可空，未来进 DB 时序存储
> 7. **variant 字段**（裁定 1）：策略层用 `variant_of` 可选分组，不强制层级
> 8. **半派生**：手写真源（编号/状态/语义）入 git，脚本反查补全（code_path/module_id/依赖）

### 8.1 P0-1：factor_registry.yaml（因子库）

```yaml
# frontmatter 头部（对齐 frontmatter_field_registry）
module_id: REG-FCT-001
ttl: permanent
title: 因子登记表
doc_type: register
registry_id: REG-FCT-001
name: Factor Registry
name_zh: 因子登记表
description: >-
  alpha 因子唯一真源（SSoT）。结构化登记所有因子（编号/公式/参数/IC/状态/代码位置/所属策略）。
  治本"因子散落代码+文档答不出数量"痛点。对标 WorldQuant Alpha Bank / qlib Alpha158。
  与 technical_indicator_registry 正交：技术指标=OHLCV计算，因子=alpha来源。
owner: MOD-GOV-029
tier: tier_1_governance
status: active
version: 1.0.0
created: '2026-08-10'
last_updated: '2026-08-10'

unique_key:
- factor_id

entry_schema:
  factor_id: str               # FCT-{CLASS}-{NNN}，如 FCT-MOM-001
  name: str                     # 英文名
  name_zh: str                  # 中文名
  aliases: list[str]            # 别名防重复登记
  factor_class: enum            # value/momentum/quality/volatility/size/event/intraday/technical/sentiment
  formula: str                  # 表达式/公式（qlib 表达式或自然语言）
  params: obj                   # 参数字典（如 {window: 20}）
  inputs: list[str]             # 输入字段（引用 field_dictionary，如 [close, volume]）
  outputs: list[str]            # 输出列名
  alpha_source: str             # alpha 来源一句话描述（为什么有 alpha）
  frequency: enum               # daily/intraday/tick
  universe: str                 # 适用股票池（如 CSI300/全A/打板池）
  neutralization: str           # 中性化方式（industry/size/market/none）
  pit_policy: str               # PIT 处理（对齐 data_asset_registry datasets.pit_policy）
  # 关联
  module_id: str                # depgraph 模块号（D_FACTOR 域 MOD-L02-xxx）
  doc_ref: str                  # design memo（如 25_multifactor_strategy_detail.md §3.1）
  code_path: str                # 代码位置（如 src/zephyr/factor/momentum_factor.py:L45）
  belongs_to_strategies: list[str]  # 被哪些策略使用（strategy_id 列表）
  variant_of: str               # 可选：如果是某因子变体，指向 parent factor_id
  # 生命周期（对齐 module_lifecycle_status_vocabulary）
  status: enum                  # candidate/experimental/active/deprecated/retired
  version: str                  # 语义化版本
  created_at: date
  updated_at: date
  owner: str
  # 性能指标（运行时可空，未来进 DB 时序存储）
  ic: float                     # information coefficient
  ir: float                     # information ratio
  decay_halflife: int           # IC 衰减半衰期（天）
  turnover: float               # 换手率
  capacity: float               # 容量（亿元）
  last_evaluated_at: date       # 最近评估日期
```

### 8.2 P0-2：strategy_registry.yaml（策略库）

```yaml
module_id: REG-STR-001
ttl: permanent
title: 策略登记表
doc_type: register
registry_id: REG-STR-001
name: Strategy Registry
name_zh: 策略登记表
description: >-
  交易策略唯一真源（SSoT）。登记所有策略（编号/sleeve/alpha来源/状态/生命周期/文档/代码）。
  治本"策略散落5篇文档答不出数量"痛点。对标 AQR capabilities / QuantConnect AlphaModel。
  variant 字段表达同 sleeve 内模式切换（裁定 1），不强制 sub-strategy 层级。
owner: MOD-GOV-029
tier: tier_1_governance
status: active
version: 1.0.0
created: '2026-08-10'
last_updated: '2026-08-10'

unique_key:
- strategy_id

entry_schema:
  strategy_id: str              # STR-{CLASS}-{NNN}，如 STR-DABAN-001
  name: str
  name_zh: str
  aliases: list[str]
  strategy_class: enum          # daban/multifactor/event_driven/sector_rotation/sentiment_cycle/value_reversal/momentum_trend
  sleeve: str                   # 所属 sleeve（小账本，如 daban_sleeve/multifactor_sleeve）
  alpha_sources: list[str]      # 使用的 factor_id 列表（关联 factor_registry）
  # variant 机制（裁定 1）
  variant_of: str               # 可选：如果是某策略的 variant，指向 parent strategy_id
  variants: list[obj]           # 可选：该策略的 variant 列表 [{variant_id, name, params}]
  # 逻辑
  entry_logic: str              # 进场逻辑（一句话或引用 doc_ref §）
  exit_logic: str               # 出场逻辑
  position_sizing: str          # 仓位方法（如 Kelly/固定比例/风险预算）
  risk_rules: list[str]         # 风控规则引用（关联 risk_limit_registry）
  holding_period: str           # 持仓周期（如 T+1/波段/趋势）
  # 关联
  module_id: str                # depgraph 模块号
  doc_ref: str                  # design memo（如 24_daban_strategy_detail.md）
  code_path: str                # 代码位置（如 src/zephyr/governance/strategies/）
  # 生命周期
  lifecycle_status: enum        # candidate/backtest/sim/paper/live/monitoring/retired
  status: enum                  # active/deprecated/retired（治理状态）
  version: str
  created_at: date
  updated_at: date
  go_live_date: date            # 上线日期（可空）
  retired_date: date            # 退役日期（可空）
  owner: str
  # 性能（运行时可空）
  sharpe: float
  max_drawdown: float
  annual_return: float
  capacity: float
  turnover: float
  last_evaluated_at: date
```

### 8.3 P0-3：technical_indicator_registry.yaml（技术指标清单）

```yaml
module_id: REG-IND-001
ttl: permanent
title: 技术指标登记表
doc_type: register
registry_id: REG-IND-001
name: Technical Indicator Registry
name_zh: 技术指标登记表
description: >-
  技术指标唯一真源（SSoT）。登记所有纯 OHLCV 计算指标（编号/公式/参数/输入输出列/状态/代码）。
  16号文档 §2 清单迁入此注册表，16号降级为 why 层（设计原则/双模式/宽表存储理由）。
  与 factor_registry 正交：技术指标=计算工具，因子=alpha来源。对标 QuantConnect Indicators/backtrader.indicators。
owner: MOD-GOV-029
tier: tier_1_governance
status: active
version: 1.0.0
created: '2026-08-10'
last_updated: '2026-08-10'

unique_key:
- indicator_id

entry_schema:
  indicator_id: str             # IND-{CLASS}-{NNN}，如 IND-TREND-001
  name: str
  name_zh: str
  aliases: list[str]
  indicator_class: enum         # trend/momentum/volatility/volume/structure（5类对齐16号§2）
  formula: str                  # 公式（数学表达式）
  params: obj                   # 参数字典（如 {period: 14}）
  inputs: list[str]             # 输入字段（OHLCV 子集，引用 field_dictionary）
  outputs: list[str]            # 输出列名
  computation_mode: enum        # vectorized/streaming/both（双模式，16号 why 层说明）
  # 关联
  module_id: str                # depgraph 模块号
  doc_ref: str                  # 16_technical_indicator_catalog.md §2
  code_path: str                # src/zephyr/factor/technical_indicators/xxx.py:Lnn
  used_by_factors: list[str]    # 被哪些因子引用（factor_id 列表，反向关联）
  # 生命周期
  status: enum                  # active/deprecated/retired
  version: str
  created_at: date
  updated_at: date
  owner: str
```

### 8.4 P1-1：execution_algo_registry.yaml（执行算法库）

```yaml
module_id: REG-EXA-001
# frontmatter 头部同上模式
registry_id: REG-EXA-001
name: Execution Algorithm Registry
name_zh: 执行算法登记表
description: >-
  执行算法唯一真源（SSoT）。从 40号文档提取 6 种算法（TWAP/VWAP/IS/AC/POV/Adaptive）。
  登记编号/参数/适用场景/状态/代码。对标 OpenLineage Job 实体的 algo 维度。
tier: tier_1_governance

unique_key: [execution_algo_id]
entry_schema:
  execution_algo_id: str        # EXA-{NAME}-{NNN}，如 EXA-TWAP-001
  name / name_zh / aliases
  algo_class: enum              # twap/vwap/implementation_shortfall/aggressive/percent_of_volume/adaptive
  formula: str                  # 算法逻辑
  params: obj                   # 参数（如 {slicing: time, bucket: 5min}）
  applicable_scenario: str      # 适用场景（大单/小单/流动性差/急单）
  market_impact_model: str      # 冲击模型（引用 40号 propagator/Barzykin）
  module_id / doc_ref (40号) / code_path (src/zephyr/ex_sor/)
  status / version / created_at / updated_at / owner
```

### 8.5 P1-2：risk_limit_registry.yaml（风控限额表）

```yaml
module_id: REG-RLM-001
registry_id: REG-RLM-001
name: Risk Limit Registry
name_zh: 风控限额登记表
description: >-
  风控限额唯一真源（SSoT）。从代码 risk_limits.py + config/risk_register.yaml 提取。
  登记 9 种限额类型/阈值/消耗追踪/状态。对标 Citadel pod risk budget。
tier: tier_1_governance

unique_key: [risk_limit_id]
entry_schema:
  risk_limit_id: str            # RLM-{TYPE}-{NNN}
  name / name_zh
  limit_type: enum              # position/concentration/drawdown/var/es/leverage/turnover/kill_switch/firm_risk
  scope: enum                   # strategy/sleeve/portfolio/firm
  threshold_value: float        # 阈值
  threshold_unit: str           # 单位（%/元/σ）
  consumption_tracking: str     # 消耗追踪方式（引用代码）
  breach_action: enum           # warn/skip/fix-in-place/halt（对齐 reconciler 约束）
  module_id / doc_ref (35/36/37号) / code_path (src/zephyr/risk/)
  status / version / created_at / updated_at / owner
  current_consumption: float    # 运行时消耗（可空，未来进 DB）
```

### 8.6 P1-3：data_asset_registry.yaml（数据资产注册表，改名扩展）

```yaml
module_id: REG-DAT-001  # 原 dataflow_graph_registry module_id 保留
registry_id: REG-DAT-001
name: Data Asset Registry
name_zh: 数据资产登记表
description: >-
  数据资产唯一真源（SSoT）。含三实体：sources（数据源供应商）/ datasets（数据集）/ jobs（作业），
  对标 OpenLineage Source/Dataset/Job 单一统一模型。原 dataflow_graph_registry.yaml 改名扩展。
  治本"数据源散落+数据集在 dataflow 不含供应商"痛点。
tier: tier_2_data_runtime
migration_from: dataflow_graph_registry.yaml  # migration_registry 登记改名

unique_key:
  sources: [source_id]
  datasets: [dataset_id]
  jobs: [job_id]

sources:                        # 新增段（数据源供应商）
  - source_id: str              # SRC-{PROVIDER}-{NNN}，如 SRC-QMT-001
    provider_name: str          # miniQMT/AkShare/TDX/Wind
    connection_type: str        # api/sdk/file/db
    frequency: str              # tick/1min/day
    sla: str                    # 可用性/延迟 SLA
    cost: str                   # 成本（免费/付费/按量）
    compliance: str             # 合规（数据使用许可）
    provides_datasets: list[str]  # 提供的 dataset_id 列表
    env_config: str             # 配置引用（如 config/.env.qmt）
    status / created_at / updated_at

datasets:                       # 沿用原 dataflow_graph_registry datasets 段
  - dataset_id: str             # DS-{NAME}-{NNN}，如 DS-TICK-001
    name / schema / frequency / pit_policy / contract_ref / module_id
    produced_by_source: str     # 属于哪个 source（关联 sources）
    produced_by_jobs: list[str]
    consumed_by_jobs: list[str]
    status / created_at / updated_at

jobs:                           # 沿用原 jobs 段
  - job_id: str                 # JOB-{NAME}-{NNN}
    name / schedule / consumes / produces / module_id / code_path
    status / created_at / updated_at
```

### 8.7 P2：field_dictionary.yaml（字段字典）

```yaml
module_id: REG-FLD-001
registry_id: REG-FLD-001
name: Field Dictionary
name_zh: 数据字段字典
description: >-
  数据字段唯一真源（SSoT）。仅管数据层字段（行情/因子/特征/输出的 type/unit/source/复权口径/PIT）。
  不合并 frontmatter_field_registry（文档元数据，职责分离，裁定 8）。对标 DAMA-DMBOK / dbt schema.yml。
tier: tier_2_data_runtime

unique_key: [field_id]
entry_schema:
  field_id: str                 # FLD-{DOMAIN}-{NNN}
  field_name: str               # 字段名（如 close）
  name_zh: str                  # 中文名（如 收盘价）
  business_definition: str      # 业务定义
  data_type: str                # int/float/str/datetime/bool
  unit: str                     # 单位（元/股/%）
  allowed_values: list[str]     # 枚举值（如适用）
  source_system: str            # 来源系统（关联 data_asset_registry source_id）
  adjust_method: str            # 复权口径（前复权/后复权/不复权）
  pit_property: str             # PIT 属性（point_in_time/look_ahead_risk）
  quality_rules: list[str]      # 质量规则（非空/范围/一致性）
  steward: str                  # 字段负责人
  status / version / created_at / updated_at
```

### 8.7b P1-4：chart_pattern_registry.yaml（图形形态库，2026-08-10 新增第 8 注册表）

```yaml
module_id: REG-PAT-001
registry_id: REG-PAT-001
name: Chart Pattern Registry
name_zh: 图形形态登记表
description: >-
  图形形态识别算法唯一真源（SSoT）。登记所有图形技术分析形态识别算法。
  与 technical_indicator_registry 正交：指标=数值计算（连续值），形态=模式识别（离散事件）。
  被 factor_registry 引用（形态因子 factor_class=pattern，引用识别算法）。
  对标 TA-Lib CDLPATTERN（61种K线形态）+ 缠论体系 + 艾略特波浪 + Edwards&Magee 经典图表。
  关系链：chart_pattern_registry（识别算法）→ factor_registry（形态因子）→ strategy_registry。
  与 technical_indicator_registry → factor_registry → strategy_registry 完全对称。
  pattern_class 8 大类覆盖图形技术分析全谱系。
tier: tier_1_governance

unique_key: [pattern_id]
entry_schema:
  pattern_id: str               # PAT-{CLASS}-{NNN}，如 PAT-CHANLUN-001
  name: str
  name_zh: str
  aliases: list[str]
  pattern_class: enum           # 8 大类（见下），覆盖图形技术分析全谱系
  # pattern_class 8 类：
  # 1. candlestick_pattern: 蜡烛图/K线组合（TA-Lib 61种，单根/两根/三根/多根）
  #    单根: 锤子线/上吊线/射击之星/倒锤子/十字星/长腿十字/蜻蜓十字/墓碑十字/陀螺/纸伞
  #    两根: 看涨吞没/看跌吞没/乌云盖顶/刺透形态/看涨孕线/看跌孕线/十字孕线/镊形顶底/内含线/外包线
  #    三根: 晨星/暮星/红三兵/黑三兵/三只乌鸦/弃婴/三内升降/三外升降
  #    多根: 上升三法/下降三法/塔形顶底
  # 2. chart_pattern: 经典图表形态（Edwards&Magee 体系）
  #    反转: W底(双底)/M头(双顶)/三重顶底/头肩顶底/圆弧顶底/V型反转/岛形反转
  #    持续: 旗形/三角旗/三角形(对称上升下降)/楔形/矩形/菱形/杯柄形
  # 3. chanlun: 缠论独立体系（分型→笔→线段→中枢→走势层级结构）
  #    顶分型/底分型/笔/线段/中枢/走势类型(趋势盘整)/背驰(趋势盘整)/一二三买卖点
  # 4. elliott_wave: 波浪理论（主观性极高）
  #    推动浪1-5/调整浪abc/延长浪/失败浪/锯齿形/平台形/三角形/复杂组合WXY
  # 5. trendline_channel: 趋势线与通道
  #    上升下降水平趋势线/上升下降水平通道/颈线
  # 6. support_resistance: 支撑阻力位与缺口
  #    阻力位/支撑位/关键价位(整数关口历史高低点)/突破缺口/测量缺口/衰竭缺口/普通缺口
  # 7. fibonacci: 斐波那契工具
  #    回测位(23.6/38.2/50/61.8/78.6%)/扩展位(61.8/100/161.8/261.8/423.6%)/扇形/弧形/时间区间
  # 8. structure: 价格结构
  #    箱体矩形震荡区/平台盘整区/密集成交区
  pattern_subtype: str          # 子类细分（如 反转/持续、单根/两根/三根、推动浪/调整浪）
  recognition_algorithm: str    # 识别算法（因算法不唯一，MUST记录用哪种）
  algorithm_variant: str        # 算法变种（峰谷法/回归法/模板匹配法/分形法/规则法）
  params: obj                   # 参数（如 {lookback: 20, threshold: 0.03}）
  inputs: list[str]             # 输入（OHLCV/分时数据，引用 field_dictionary）
  outputs: obj                  # 形态事件 {present: bool, start_pos: int, end_pos: int, confidence: float}
  subjectivity: enum            # high/medium/low —— 波浪=high, 缠论分型=medium, 蜡烛图=low, 斐波那契=low
  timeframe: enum               # intraday/daily/weekly（形态在不同周期有效性不同）
  # 关联
  module_id: str                # depgraph 蓝图模块号
  doc_ref: str                  # 文档引用
  code_path: str                # 代码位置
  used_by_factors: list[str]    # 被哪些因子引用（factor_id 列表，反向关联）
  variant_of: str               # 可选：形态变体（如 复合W底 variant_of W底）
  # 生命周期
  status: enum                  # candidate/experimental/active/deprecated/retired
  version: str
  created_at: date
  updated_at: date
  owner: str
  # 性能（可空，未来进 DB）
  hit_rate: float               # 命中率（形态识别后 N 日收益方向正确率）
  false_positive_rate: float    # 误报率
  last_evaluated_at: date
```

**设计要点**：
- `recognition_algorithm` + `algorithm_variant` 双字段：图形形态算法不唯一（W 底有峰谷法/回归法/模板匹配法），必须记录用哪种——这是与技术指标库最大的 schema 差异
- `outputs` 是 obj 不是 list[str]：形态输出是事件结构（存在/位置/置信度），不是数值列
- `subjectivity` 字段：诚实标注主观性，波浪=high 标 experimental，分型=low 可 active
- 波浪理论特殊处理：登记但 subjectivity=high + status=experimental，不作 MVP baseline，需人工辅助识别

**MVP 范围控制**：图形形态几十种，但不一次性建全。P1 阶段先从代码反查项目实际用到的形态（src/zephyr/factor/technical_indicators/ + src/zephyr/signal_ashare/ 打板链），只登记实际用到或明确规划的。符合"过度工程纠偏"原则——建库结构完整，内容按需填充。

### 8.7c P2-2：experiment_registry.yaml（实验/回测目录，2026-08-10 新增第 9 注册表）

> ⚠️ 2026-08-10 紧急补充：用户"马上要回测"，调研发现 universe/benchmark/cost_model 三个回测必需输入**全部缺失**（见 §8.7d-f）。这 3 个提到 P0，与 factor/strategy/indicator 同级。experiment_registry 仍 P2（等 51 号）。

### 8.7d P0-4：universe_registry.yaml（股票池注册表，回测必需，2026-08-10 新增第 10 注册表）

```yaml
module_id: REG-UNI-001
registry_id: REG-UNI-001
name: Universe Registry
name_zh: 股票池登记表
description: >-
  股票池/标的池唯一真源（SSoT）。登记所有可交易股票池（CSI300/CSI800/全A/打板池/事件池）。
  回测必需输入：每次回测 MUST 指定 universe_id。
  支持 static（固定成分股）/ dynamic（每日生成，如打板连板梯队）/ rule_based（规则过滤，如剔ST/低流动性）。
  对标 MSCI Index Universe / Bloomberg Universe Management。
  治本"回测不知道在哪些股票上跑"硬缺口。
tier: tier_2_data_runtime

unique_key: [universe_id]
entry_schema:
  universe_id: str               # UNI-{TYPE}-{NNN}，如 UNI-INDEX-001
  name: str
  name_zh: str
  aliases: list[str]
  universe_type: enum            # static / dynamic / rule_based
  construction_rule: str         # 构造规则（如"沪深300成分股" / "当日连板梯队" / "全A剔除ST退市低流动性"）
  base_universe: str             # 基础池（如全A，rule_based 在此基础上过滤）
  filter_rules: list[str]        # 过滤规则（剔除ST/退市风险/上市<60天/日均成交额<1000万）
  rebalance_frequency: enum      # daily/weekly/monthly/quarterly/none（static）
  component_count: int           # 成分股数量（摘要）
  components_ref: str            # 成分股列表位置（DB/文件，因成分股可能数千个不入注册表）
  # 关联
  used_by_strategies: list[str]  # 被哪些策略使用（strategy_id 列表）
  data_source: str               # 成分股数据来源（关联 data_asset_registry source_id）
  module_id: str                 # depgraph 蓝图模块号
  doc_ref: str                   # 文档引用
  code_path: str                 # 代码位置
  # 生命周期
  status: enum                   # candidate/experimental/active/deprecated/retired
  version: str                   # 版本（成分股调整）
  created_at: date
  updated_at: date
  owner: str
```

### 8.7e P0-5：benchmark_registry.yaml（基准注册表，回测必需，2026-08-10 新增第 11 注册表）

```yaml
module_id: REG-BMK-001
registry_id: REG-BMK-001
name: Benchmark Registry
name_zh: 基准登记表
description: >-
  交易基准唯一真源（SSoT）。登记所有回测/归因对比基准（CSI300/CSI500/自定义等权/绝对收益）。
  回测必需输入：每次回测 MUST 指定 benchmark_id 计算超额收益/相对收益。
  与 universe_registry 关联：benchmark 通常基于某 universe 加权。
  治本"回测无法计算超额收益"硬缺口。engine_base.py 现仅 benchmark_symbol 字符串，需结构化。
tier: tier_2_data_runtime

unique_key: [benchmark_id]
entry_schema:
  benchmark_id: str              # BMK-{TYPE}-{NNN}，如 BMK-INDEX-001
  name: str
  name_zh: str
  aliases: list[str]
  benchmark_type: enum           # index / custom_equal / custom_cap / absolute / peer_strategy
  underlying_universe: str       # 基于哪个 universe（关联 universe_id）
  weight_method: enum            # cap_weighted / equal_weighted / price_weighted / custom
  data_source: str               # 基准行情数据来源（关联 data_asset_registry source_id）
  # 关联
  used_by_strategies: list[str]  # 被哪些策略用作基准
  module_id: str
  doc_ref: str
  code_path: str
  # 生命周期
  status: enum                   # candidate/experimental/active/deprecated/retired
  version: str
  created_at: date
  updated_at: date
  owner: str
  # 性能（可空，未来进 DB 时序存储）
  annual_return: float
  sharpe: float
  max_drawdown: float
  last_evaluated_at: date
```

### 8.7f P0-6：cost_model_registry.yaml（交易成本模型注册表，回测必需，2026-08-10 新增第 12 注册表）

```yaml
module_id: REG-CST-001
registry_id: REG-CST-001
name: Cost Model Registry
name_zh: 交易成本模型登记表
description: >-
  交易成本模型唯一真源（SSoT）。登记所有回测/执行成本模型（佣金/印花税/过户费/滑点/冲击成本）。
  回测必需输入：每次回测 MUST 指定 cost_model_id 扣除交易成本，否则结果严重失真。
  A 股成本结构：佣金(万2.5-3) + 印花税(卖出千1) + 过户费(沪市万0.1) + 滑点 + 冲击成本。
  高频策略成本可能吃掉全部 alpha，回测不扣成本=自欺欺人。
  治本"回测不扣成本结果失真"硬缺口。注意：现有 cost_estimator.py 是 AI token 成本，非交易成本。
tier: tier_2_data_runtime

unique_key: [cost_model_id]
entry_schema:
  cost_model_id: str             # CST-{TYPE}-{NNN}，如 CST-ASTOCK-001
  name: str
  name_zh: str
  aliases: list[str]
  cost_model_type: enum          # astock_standard / conservative / aggressive / zero_cost（回测对比用）
  components: obj                # 成本组件（结构化）
    # commission: 佣金 {rate: 0.00025, min: 5元, mode: both_sides}
    # stamp_duty: 印花税 {rate: 0.001, side: sell_only}
    # transfer_fee: 过户费 {rate: 0.00001, market: sh_only}
    # slippage: 滑点 {model: fixed/linear/quadratic, params: {ticks: 1}}
    # market_impact: 冲击成本 {model: square_root/linear, params: {coefficient: 0.1}}
  slippage_model: str            # 滑点模型（fixed/linear/square_root/alphasim）
  impact_model: str              # 冲击模型（引用 40号 propagator/Barzykin）
  # 关联
  used_by_strategies: list[str]
  module_id: str
  doc_ref: str                   # 40号 execution_broker
  code_path: str
  # 生命周期
  status: enum                   # candidate/experimental/active/deprecated/retired
  version: str
  created_at: date
  updated_at: date
  owner: str
```

```yaml
module_id: REG-EXP-001
registry_id: REG-EXP-001
name: Experiment Registry
name_zh: 实验登记表
description: >-
  回测/实验元信息唯一真源（SSoT）。登记每次回测/实验的元信息（编号/算法/参数摘要/日期/结论/状态），
  作为"日志目录"指向日志详情。治本"每个技术/算法回测日志散落无法回溯优化"痛点。
  两层分离：本注册表只管元信息（静态，量中等），日志详情（逐笔/指标时序/完整结果）进 DB/文件不入注册表。
  对标 MLflow Experiment Registry / Neptune.ai / Comet.ml。
  施工依赖：等 51号 MLflow 退役方案落定后立即施工，避免返工。
tier: tier_2_data_runtime

unique_key: [experiment_id]
entry_schema:
  experiment_id: str            # EXP-{TYPE}-{NNN}，如 EXP-BACKTEST-001
  name: str
  name_zh: str
  experiment_type: enum         # backtest/factor_eval/strategy_eval/param_search/walk_forward/regime_validation
  # 关联被测对象
  target_type: enum             # factor/strategy/indicator/pattern/risk_rule/execution_algo
  target_id: str                # 被测对象 id（factor_id/strategy_id/indicator_id/...）
  # 实验信息
  params_summary: obj           # 参数摘要（如 {window: 20, threshold: 0.03, period: 2024-01~2026-06}）
  data_period: str              # 回测数据区间
  universe: str                 # 股票池
  # 结果摘要（详情进 DB）
  result_summary: obj           # 结果摘要（如 {sharpe: 1.2, max_dd: 0.15, ic: 0.05}）
  conclusion: str               # 结论一句话（如 "IC 衰减快，需缩短持仓周期"）
  is_overfit: bool              # 是否判定过拟合
  # 日志详情位置（不入注册表，指向 DB/文件）
  log_location: str             # 日志详情位置（如 db://experiments/EXP-BACKTEST-001 或 /logs/xxx.json）
  artifact_path: str            # 产物路径（图表/报告）
  # 生命周期
  status: enum                  # running/completed/failed/archived
  created_at: date
  completed_at: date
  owner: str
  # 迭代关联
  parent_experiment_id: str     # 可选：基于哪个实验迭代（参数优化链）
  tags: list[str]               # 标签（如 "phase2_validation" "regime_bull"）
```

**设计要点**：
- **两层分离**：本注册表只管元信息（静态目录），日志详情（逐笔/时序）进 DB——注册表不塞运行时大量数据
- **`log_location` 指向详情**：注册表是"目录"，指向 DB/文件里的日志详情，符合"日志目录"定位
- **`parent_experiment_id`**：支持迭代链（参数优化 A→B→C），可追溯优化历程
- **`is_overfit` + `conclusion`**：回测结论结构化，便于 AI 检索"某因子历史回测结论"
- **施工时机**：等 51号 MLflow 退役落定后立即施工。若 51 号近期不落定，可先建 schema 框架 + 手填元信息，日志详情对接等 51 号

### 8.8 六个待确认点调研裁定（2026-08-10）

> 调研证据：module_id 命名真源 `validate_module_id_naming.py` + 20号策略清单 + 15号因子体系 + migration_registry 状态 + D38 裁定 + 代码层 evaluation.py。

#### 裁定 S1：编号前缀 → 符合项目既有模式，无需调整

**项目内证据**：
- `validate_module_id_naming.py` 定义三类编号：`module_id`=MOD-{DOMAIN}-NNN（蓝图模块）/ `submodule_id`=D-{DOMAIN}-NNN / `domain_id`=D_{DOMAIN}
- 现有注册表 `registry_id` 格式统一为 `REG-{NAME}-{NNN}`（REG-ARCH-ISSUE-001 / REG-CAND-001 / REG-DATAFLOW-001 / REG-FUNC-DOMAIN-001 等）
- 现有注册表 entry id 格式为 `{PREFIX}-{DOMAIN}-{NNN}`（CAND-XXX-001 / D-FACTOR-001 / #ARCH-XXX-001 / TEST-XXX-001）

**裁定**：
- **registry_id** 用 `REG-{NAME}-{NNN}`：REG-FCT-001 / REG-STR-001 / REG-IND-001 / REG-EXA-001 / REG-RLM-001 / REG-FLD-001（data_asset 保留原 REG-DATAFLOW-001，见 S6）
- **entry id** 用 `{PREFIX}-{DOMAIN}-{NNN}`：FCT-{CLASS}-NNN / STR-{CLASS}-NNN / IND-{CLASS}-NNN / EXA-{NAME}-NNN / RLM-{TYPE}-NNN / SRC-{PROVIDER}-NNN / DS-{NAME}-NNN / JOB-{NAME}-NNN / FLD-{DOMAIN}-NNN
- **schema 里 `module_id` 字段**引用 depgraph 蓝图模块号（MOD- 前缀，如 MOD-L02-xxx），不是自编——修正 §8.1-8.7 草案里 module_id 注释的歧义
- ✅ 符合项目既有模式，无需调整

#### 裁定 S2：factor_class 枚举 → Barra 风格 6 类 + 项目特殊 4 类 = 10 类

**项目内证据**：
- 15号文档是"数据与特征层规范"（why 层 + 数据源/PIT/质量），**无明确因子分类枚举**——因子分类不是 15号职责
- 25号多因子策略文档使用因子评估（IC/衰减/换手）但未定义分类枚举
- 代码层 `src/zephyr/factor/` 有 value_factor / momentum_factor / intraday_snapshot_factors 等，反映项目实际因子类

**机构实践**：Barra 风格因子模型 = value/quality/momentum/volatility/size/liquidity（6 类，MSCI Barra 标准，业界共识）

**第一性原理分析**：
- 因子分类要覆盖"alpha 来源维度"——Barra 6 类覆盖传统风格因子，项目特殊类覆盖 A 股特色
- A 股特色：event（事件驱动，并购/业绩/政策）/ intraday（日内/打板，A 股 T+1 + 涨跌停特色）/ technical（技术指标衍生因子）/ sentiment（情绪/舆情，游资接力情绪）
- 10 类既对标国际标准（Barra）又覆盖 A 股特色，不过度也不遗漏

**裁定**：factor_class 枚举 = `value / quality / momentum / volatility / size / liquidity / event / intraday / technical / sentiment`（10 类）
- Barra 6 类（value/quality/momentum/volatility/size/liquidity）+ A 股特色 4 类（event/intraday/technical/sentiment）
- 修正 §8.1 草案枚举（原 9 类缺 liquidity，补上）

#### 裁定 S3：strategy_class 枚举 → 6 类（20号 5 策略 + sector_rotation）

**项目内证据**：
- 20号 §2.1 候选清单明确：**价值反转 / 动量趋势 / 事件驱动 / 打板 / 多因子**（5 个，去掉主升龙头，新增多因子）
- 首批 3 = 打板 + 多因子 + 事件驱动
- 27号二批 = 价值反转 / 动量趋势（draft 暂缓，G11）
- 22号 `sector_rotation_spec.md` 是独立 spec（行业轮动）→ 可作独立 strategy_class
- 28号 `sentiment_cycle_trading.md` v1.10.0 定位"sleeve 内 alpha 择时"（project_memory 明确"情绪周期=sleeve 内机制，非独立策略"）→ **不作 strategy_class**

**第一性原理分析**：
- strategy_class 要与 sleeve 划分对齐——每个 strategy_class 对应一个潜在 sleeve（独立账本/风控/资金）
- sentiment_cycle 是打板 sleeve 内机制（情绪周期 4+1 阶段定位），不是独立 sleeve，不应作 strategy_class
- sector_rotation 有独立 spec + 独立 alpha 来源（行业轮动动量）→ 可作独立 strategy_class

**裁定**：strategy_class 枚举 = `daban / multifactor / event_driven / value_reversal / momentum_trend / sector_rotation`（6 类）
- 修正 §8.2 草案枚举（原 7 类含 sentiment_cycle，去掉；sector_rotation 保留）

#### 裁定 S4：variant 单向 → 只留 `variant_of`，删除 `variants` 列表字段

**项目内证据**：
- D38 裁定（architecture_issue_registry.yaml）：`parent_domain` "仅作分组属性，不表示层级子域"——项目对层级字段持谨慎态度
- 启示：variant_of 是分组属性，不是层级树

**第一性原理分析**：
- 双向引用（variant_of + variants 列表）有维护负担：parent 改名/增删 variant 时要同步更新 variants 列表，易漂移
- 单向（只 variant_of 指向 parent）足够——查"某 strategy 的所有 variants"用 `WHERE variant_of = X` 查询聚合，与 DB 迁移后 SQL 查询一致
- 单向符合 D38 精神（分组非层级）+ 真源唯一（只存一处）+ DB 友好（查询聚合）

**裁定**：variant 只保留 `variant_of` 单向字段，删除 §8.2 草案的 `variants: list[obj]` 字段
- 打板(strategy) 的连板/趋势 variants 各自一条记录，variant_of 指向打板 strategy_id
- 查"打板的所有 variants" = 查 `variant_of = STR-DABAN-001` 的记录

#### 裁定 S5：性能指标字段 → 现在就列（用户已表态 + 代码已实现 + 地基一次性规划）

**项目内证据**：
- 代码层 `src/zephyr/factor/core/evaluation/evaluation.py` + `src/zephyr/shared/contracts/core/performance_metrics.py` 已实现 IC/IR/Sharpe/容量/换手率
- 25号文档已有因子评估记录格式（IC/衰减半衰期/换手率）
- 27号 draft 也要求"alpha 信号预研方向含 IC/IR 设定"

**用户表态**："性能指标我们不是反正都要造吗？早点造和晚点造有什么区别？那就现在规划到一起。"

**第一性原理分析**：
- 字段 schema 是地基——地基阶段一次性规划好，避免后续"因子上线后发现要加 IC 字段→迁移 schema→改代码→改 DB"的连锁成本
- 早列晚列都要列，早列 = 地基一次成型，晚列 = 后续迁移加字段成本更高
- 运行时可空（candidate/experimental 态无数据），不增加当前负担
- 未来进 DB 时序存储时，这些字段天然映射 DB 列

**裁定**：性能指标字段**现在就列**，运行时可空
- factor_registry: ic / ir / decay_halflife / turnover / capacity / last_evaluated_at
- strategy_registry: sharpe / max_drawdown / annual_return / capacity / turnover / last_evaluated_at
- risk_limit_registry: current_consumption
- ✅ 符合用户表态 + 代码已实现 + 地基一次性规划原则

#### 裁定 S6：data_asset_registry 改名 → 文件名+title 改，registry_id/module_id 全保留，ruling_registry 登记改名

**项目内证据**：
- `migration_registry.yaml` 状态 = **deprecated / frozen**（注释明确"已冻结不再新增条目；禁止新增条目；功能与 depgraph edges 表重叠"）
- migration_registry 不能登记改名（frozen）
- 项目有 `ruling_registry.yaml`（裁定登记机制，REG-RULING-001）可登记改名裁定
- 原 dataflow_graph_registry 的 registry_id = REG-DATAFLOW-001

**第一性原理分析**：
- 改名要最小化 churn——标识符（registry_id/module_id）是稳定锚点，全项目引用，改名引发连锁更新
- 文件名 + title 是人类/AI 可读层，改名提升识别度（裁定 2 的初衷）
- 只改可读层（文件名/title/description），保留标识符层（registry_id/module_id），改名成本最低 + 识别度提升最大化
- migration_registry frozen → 改名登记走 ruling_registry（裁定登记机制，符合项目治理流程）

**裁定**：
- **文件名改**：dataflow_graph_registry.yaml → data_asset_registry.yaml
- **title 改**：数据流图注册表 → 数据资产登记表
- **description 扩展**：加"含 sources/datasets/jobs 三实体，对标 OpenLineage"
- **registry_id 保留**：REG-DATAFLOW-001（稳定标识符不改，全项目引用不断）
- **module_id 保留**：原蓝图 module_id 不变
- **改名登记**：ruling_registry 登记一条裁定（旧文件名→新文件名映射 + 理由），不走 migration_registry（frozen）
- 修正 §8.6 草案的 `module_id: REG-DAT-001`（混淆 module_id 与 registry_id）→ 保留原 REG-DATAFLOW-001 作 registry_id，module_id 字段引用原蓝图 MOD- 号

---

### 8.9 Schema 定稿修正汇总

根据 S1-S6 裁定，§8.1-8.7 草案修正点：

| 注册表 | 修正项 | 修正内容 |
|---|---|---|
| §8.1 factor_registry | factor_class 枚举 | 补 `liquidity`，定稿 10 类（value/quality/momentum/volatility/size/liquidity/event/intraday/technical/sentiment） |
| §8.1 factor_registry | module_id 注释 | 澄清引用 depgraph MOD- 前缀蓝图号，非自编 |
| §8.2 strategy_registry | strategy_class 枚举 | 删 `sentiment_cycle`，定稿 6 类（daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation） |
| §8.2 strategy_registry | variants 字段 | 删除 `variants: list[obj]`，只留 `variant_of` 单向 |
| §8.6 data_asset_registry | module_id/registry_id | registry_id 保留 REG-DATAFLOW-001，module_id 保留原蓝图号，只改文件名+title |
| §8.6 data_asset_registry | 改名登记 | 走 ruling_registry（migration_registry frozen） |
| 全部 | 性能指标字段 | 确认现在就列，运行时可空 |

**Schema 定稿状态**：S1-S6 全部裁定完成，§8.1-8.7 + 8.9 修正构成 schema 定稿。可启动 P0 施工。
