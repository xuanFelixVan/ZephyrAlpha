---
ttl: permanent
doc_type: architecture_view
title: 业务资产注册表体系施工总案
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.32.0"
date: 2026-08-10
topic: business_registry_construction
scope: 07_trading_decision_architecture
---

# 业务资产注册表体系施工总案

> 本备忘是 12 个业务资产注册表（因子/策略/技术指标/图形形态/股票池/基准/成本模型/执行算法/风控限额/数据资产/字段字典/实验）的**施工总案 + 审查底稿 + 调查索引**。
> 性质：**施工执行文档**，承载 schema 定稿、P0/P1/P2 阶段进度、裁定依据、数据来源映射，供 AI 与人类审查/升级/调查使用。
> 管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)；架构裁定见 [#ARCH-BREG-001](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)。
> 关联：[15_data_feature_layer_spec](15_data_feature_layer_spec.md)（因子工程总纲）｜ [20_first_batch_strategies](20_first_batch_strategies.md)（策略清单）｜ [16_technical_indicator_catalog](16_technical_indicator_catalog.md)（技术指标 why 层）｜ [52_backtest_framework_docking](52_backtest_framework_docking.md)（回测对接）

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G62 业务资产注册表体系 |
| 架构议题 | #ARCH-BREG-001 |
| 临时工作文档 | [business_registry_consolidation_plan.md](../../../_working/business_registry_consolidation_plan.md)（施工方案+调研报告+裁定+schema 草案） |
| 真源入口 | [registry_of_registries.yaml](../../../registry_of_registries.yaml) tier_2 业务资产段 |
| 创建 | 2026-08-10 |
| 状态 | P0 已完成 3/12；P1 待施工 7/12；P2 待施工 2/12 |

## 2. 背景与问题诊断

项目已建成 3 层 52 个注册表治理体系（gate/script/module/blueprint/error_code/术语表/目录/依赖/攻击场景/状态机），**唯独最核心的业务资产——因子、策略、指标、算法、风控限额、股票池、基准、成本模型——全部游离于统一入口外**。

| 业务清单 | 旧行政状态 | 病根 |
|---|---|---|
| 因子库 | ❌ 0 注册表，散落代码 + 15/25 号文档 | 答不出"有多少因子" |
| 策略库 | ❌ 0 注册表，散落 20/24/25/26/27 号文档 | 答不出"有多少策略" |
| 技术指标清单 | ❌ 16 号骨架 draft + 代码，游离 | 非正式 SSoT |
| 股票池 | ❌ 散落各策略文档 | 回测不知道在哪些股票上跑 |
| 基准 | ❌ engine_base.py 仅 benchmark_symbol 裸字符串 | 回测无法计算超额收益 |
| 成本模型 | ❌ 散落 52 号 §G1，无结构化 | 回测不扣成本结果失真 |
| 执行算法 | ❌ 散落 40 号 | 6 种算法无登记 |
| 风控限额 | ❌ 散落代码 + config | 9 种限额无登记 |
| 数据源 | ❌ 散落 15 号 + config/.env | 供应商无登记 |
| 字段字典 | ❌ 散落代码 contracts/ | 数据字段无总表 |
| 图形形态 | ❌ 0 登记的技术分析形态 | W底/缠论/波浪无算法记录 |
| 实验/回测目录 | ❌ 散落 51 号 + 代码 | 回测日志无法回溯 |

**治本**：建 12 个业务资产注册表，分 P0/P1/P2 三阶段施工，全部登记 registry_of_registries.yaml，AGENTS.md 显化查询入口。

## 3. 12 个注册表总览

| # | 注册表 | registry_id | 真源文件 | tier | 优先级 | 状态 | 条目数 |
|---|---|---|---|---|---|---|---|
| 1 | 股票池 | REG-UNI-001 | `catalogs/universe_registry.yaml` | tier_2 | P0 | ✅ 已完成 | 5 |
| 2 | 基准 | REG-BMK-001 | `catalogs/benchmark_registry.yaml` | tier_2 | P0 | ✅ 已完成 | 4 |
| 3 | 交易成本模型 | REG-CST-001 | `catalogs/cost_model_registry.yaml` | tier_2 | P0 | ✅ 已完成 | 3 |
| 4 | 因子库 | REG-FCT-001 | `catalogs/factor_registry.yaml` | tier_1 | P1-A | 🔄 Step1-3 部分 | 111 |
| 5 | 策略库 | REG-STR-001 | `catalogs/strategy_registry.yaml` | tier_1 | P1-A | 🔄 Step1-3 部分 | 59 |
| 6 | 技术指标 | REG-IND-001 | `catalogs/technical_indicator_registry.yaml` | tier_1 | P1-A | ⏳ 待施工 | — |
| 7 | 执行算法 | REG-EXA-001 | `catalogs/execution_algo_registry.yaml` | tier_1 | P1-B | ⏳ 待施工 | — |
| 8 | 风控限额 | REG-RLM-001 | `catalogs/risk_limit_registry.yaml` | tier_1 | P1-B | 🔄 Step1-3 部分 | 42 |
| 9 | 数据资产 | REG-DATAFLOW-001 | `catalogs/data_asset_registry.yaml`（改名扩展） | tier_2 | P1-B | ⏳ 待施工 | — |
| 10 | 图形形态 | REG-PAT-001 | `catalogs/chart_pattern_registry.yaml` | tier_1 | P1-B | ⏳ 待施工 | — |
| 11 | 字段字典 | REG-FLD-001 | `catalogs/field_dictionary.yaml` | tier_2 | P2 | ⏳ 待施工 | — |
| 12 | 实验/回测目录 | REG-EXP-001 | `catalogs/experiment_registry.yaml` | tier_2 | P2 | ⏳ 待施工 | — |

> 路径前缀：`docs/01_policies_and_standards/_registry/`
> 优先级原则（project_memory）：回测三件套（universe/benchmark/cost_model）> 被测对象三件套（factor/strategy/indicator）> 交易/风控/数据/图形 > 字段字典/实验

## 4. 通用 Schema 设计原则（12 表共用）

1. **frontmatter 头部**对齐 [frontmatter_field_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml)：`module_id` / `ttl` / `schema_version` / `registry_id` / `name` / `name_zh` / `description` / `owner` / `tier` / `status` / `version` / `created` / `last_updated` / `related_arch` / `unique_key`
2. **entry_schema 按 DB 表设计**预留迁移：每条记录有 `id`(PK) / `created_at` / `updated_at` / `version` / `status`，未来可一键迁 PG
3. **编号格式**：`registry_id` = `REG-{NAME}-{NNN}`；`entry id` = `{PREFIX}-{DOMAIN}-{NNN}`（对齐 module_id_registry allocation_rules）
4. **关联字段**：`module_id` 关联 depgraph 蓝图号（MOD- 前缀）/ `doc_ref` 关联 design memo / `code_path` 关联代码
5. **状态机**对齐 [module_lifecycle_status_vocabulary.yaml](../../../01_policies_and_standards/_registry/vocabularies/module_lifecycle_status_vocabulary.yaml)：`candidate / experimental / active / deprecated / retired`
6. **性能指标字段**（IC/Sharpe/容量等）运行时可空，未来进 DB 时序存储
7. **variant 字段**：策略/形态层用 `variant_of` 可选分组（单向引用，不强制层级）
8. **半派生**：手写真源（编号/状态/语义）入 git，脚本反查补全（code_path/module_id/依赖）
9. **版本字段**（v1.2.0 新增，对标 Feast Feature View Versioning 2026-03-31）：每条 entry 含 `version` 字段记录 schema-significant 变更；schema/UDF 改动触发版本快照，metadata-only 改动（description/tags/TTL）原地更新不建版本。Feast 用 `@v<N>` 语法支持多版本在线服务（`enable_online_feature_view_versioning` flag），个人项目 YAML 阶段用 git diff 替代，但 schema 预留 `version` 字段以备未来 DB 迁移后启用 `version_pin`（回滚到历史版本）能力。**版本策略选项**（v1.4.0 新增，对标 [apxml Feature Versioning Strategies 2026](https://apxml.com/courses/feature-stores-for-ml/chapter-5-governance-security-mlops/feature-versioning-strategies)）：① Semantic Versioning（MAJOR.MINOR.PATCH，当前采用，Feast 模式，直观但需自律）；② Immutable Version（UUID/content hash，**最强 reproducibility 保证**——任何变更生成全新版本 ID，旧版本永久不变，apxml 评价"provides the strongest guarantee of reproducibility"，缺点是版本 proliferation 需 GC；[Atlan 2026-03](https://atlan.com/know/ai-model-versioning-best-practices/) 强化此原则："Every model version should be immutable once registered. Overwriting artifacts in place destroys the audit trail and makes rollback impossible."——immutability 镜像 Git commit 模型，每个版本是可引用/比较/恢复的 snapshot，支撑 regulatory 审计要求）；③ Timestamped（时间戳版本，简单但无语义）；④ Branch-based（git 分支模式，适合协作）。**个人项目选择**：YAML 阶段用 ① Semantic（git commit hash 天然提供 ② Immutable 的 reproducibility 保证，无需额外 content hash）；DB 迁移后若需审计级 reproducibility 可升级 ② Immutable（content hash 作 version 值，entry 任何字段变更触发新 hash）。schema 的 `version` 字段兼容两种策略（填 "v2" 语义版 或 "a1b2c3" content hash 均可）。**版本可复现性三要素**（v1.6.0 新增，对标 [beefed.ai 2026 Feature Registry](https://beefed.ai/en/feature-registry-governance-best-practices) + MLflow bundling）：仅有 `version` 字段不足以保证复现——成熟 registry 要求 entry 同时绑定 ① `code_commit`（产生该 entry 的代码 commit hash，§4.7 E5b 检查）+ ② 数据血缘三要素 `source_uri`（数据来自哪个 source/dataset）/ `transform_script_hash`（转换脚本哈希，因子=计算公式代码 hash）/ `labeler_id`（标签生成器标识，strategy=信号逻辑标识）+ ③ `materialization_ts`（物化时间戳，feature 值计算时刻）。MLflow 称此为 "bundling"——model artifact + code version + data version + environment 打包为可复现单元。个人项目 YAML 阶段：`code_commit` 用 git blame 天然提供（E5b 可选检查），`source_uri`/`transform_script_hash`/`labeler_id` 通过 `code_path` + `doc_ref` 间接覆盖（代码 hash = git commit），`materialization_ts` = `updated_at`。DB 迁移后升级为显式四字段绑定（factor/strategy schema 已预留 `code_commit` 字段，data_asset_registry 三实体覆盖 source_uri 血缘）。**SHA256 manifest 选项**（v1.10.0 新增，对标 [OmniBioAI ModelHub 2026-08-08](https://github.com/OmniBioAI/omnibioai-model-registry) + [Ollama content-addressable storage](https://deepwiki.com/ollama/ollama/4.2-model-registry-and-layers) + [model-secure 2026-03](https://www.npmjs.com/package/model-secure)）：当 entry 需 **bit-level reproducibility**（审计级/监管级可复现性）时，在 `code_commit` 之外追加 `content_hash` 字段——对 entry 关联的全部产物（code_path 源码 + formula 表达式 + params + inputs/outputs 声明）计算 SHA256，生成 `sha256sums.txt` manifest。OmniBioAI ModelHub（2026-08-08 最新）明确："Every model package includes a SHA256 manifest (sha256sums.txt) that hashes the package contents (excluding itself). This enables **bit-level reproducibility, tamper detection, and trustworthy deployment in regulated environments**."；Ollama 用 Docker 启发的 content-addressable storage——Layer = immutable content blob identified by SHA256 digest，Integrity（content validation against expected digest）/ Immutability（once written, layers never modified）/ Deduplication（identical content stored once）三原则；model-secure 进一步用 ECDSA P-256 对 manifest 签名（NIST FIPS 186-5），实现 tamper detection + provenance。**个人项目选择**：YAML 阶段 git commit hash 天然提供 content 追溯（§4 原则9 已述），**无需额外 SHA256 manifest**——git blob 即 content-addressable storage（每个 commit 是 tree 的 SHA1）。DB 迁移后若需监管级 reproducibility（如 EU AI Act 2026-08-02 高风险 AI 系统审计要求），可升级为显式 `content_hash` 字段（对 entry 产物算 SHA256，与 `code_commit` 并列），schema 预留此字段位置（factor/strategy 的 `code_commit` 注释已含"DB 阶段 MUST"）。**注意防过度工程**：[ManifoldKit #1934 2026-06](https://github.com/roryford/ManifoldKit/issues/1934) 对 SHA256 blob store 的对抗审查结论"over-engineered for single-user on-device app"——个人单用户项目用 git commit hash 足够，SHA256 manifest 是 DB+监管阶段的可选项非必选项。
10. **衰减检测字段**（v1.2.0 新增，对标 Alexander & Fabozzi 2026 MRP + Vibe-Trading 2026-07 衰减状态机）：strategy/factor entry 预留 `decay_detection_method` / `last_decay_scan_at` / `decay_state` 字段。Vibe-Trading 衰减状态机：`created → benching → active → monitoring → decayed → disabled`，恢复条件 IC ratio > 0.7
11. **Schema 演进兼容性**（v1.3.0 新增，对标 Confluent Schema Registry + datalakehouse 2026-02）：schema 变更默认走 **Additive-Only**（只增不删/不重命名，新字段有默认值=BACKWARD 兼容，直接部署）；breaking 变更（删/改/重命名）走 **Expand-Contract** 3 阶段（Expand 共存→Migrate 迁移→Contract 清理）。`schema_version` 区分兼容（1.0→1.1）vs breaking（1.x→2.0）。详见 §4.11 EVOLVE_SCHEMA 算法
12. **变更与退役治理**（v1.3.0 新增，对标 theFactory 2026-07 + Feast Versioning）：entry 变更按 `change_type` 分类——metadata 原地更新 / schema_sig+code_ref 触发版本快照 / status 走退役流程（详见 §4.9 EVOLVE_ENTRY）。退役 3 阶段 active→deprecated（90天宽限，最少30天）→retired（无活跃引用）→物理删除（退役满1年+ARCH审批），详见 §4.10 RETIRE_ENTRY。retired 记录保留审计追溯，不默认删除

### 4.4 算法体系导航图（v1.10.0 新增，v1.11.0 更新为 12 算法 + 7 阶段，v1.13.0 补横切查询升级为 13 算法）

§4.5-§4.16 共 12 个生命周期施工算法 + §4.18 DIFF_ENTRY 横切查询算法（共 13 算法），但 v1.9.0 及之前**无全局导航图**——读者面对算法不知先看哪个、何时调用哪个、它们如何串联成完整生命周期。本导航图解决"算法顺序问题"，给出 13 算法的调用关系图 + 触发时机 + 输入输出依赖。v1.11.0 新增第 7 阶段"迁"（MIGRATE_REGISTRY），完整覆盖"建→上→改→测→应/回→退→迁"全生命周期；v1.13.0 新增横切查询 DIFF_ENTRY（版本差异，任意阶段可调用的只读查询，非状态变更）。

> 📌 **§4 结构说明**（v1.21.0 新增，辅助导航）：§4 含两类内容——① **算法定义**（§4.4 导航图 / §4.5-§4.16 生命周期算法 / §4.18 横切查询 / §4.20 监管变更 / §4 原则 1-12）是施工 MUST 读；② **研究对标**（§4.17 第一轮 / §4.19 第二轮 / §4.21-§4.28 第三至十轮）是审查底稿，记录每轮全网搜索的"比现有方法更好"发现，供调查溯源。读者优先读 ① 算法定义，② 研究对标按需查阅。研究对标随版本累积增长，新增轮次应精简（≤50 行/轮，仅记已落地项+1-2 项 Phase 1.5+ 评估）。

**12 生命周期算法按阶段分组 + 1 横切查询算法**（建→上→改→测→应/回→退→迁 + 横切查询）：

```
┌─────────────────────────────────────────────────────────────────────┐
│                    entry 生命周期完整闭环                              │
│                                                                     │
│  阶段1 建    │ CONSTRUCT_REGISTRY(§4.5)                              │
│  (新建注册表) │ ├─ Step4 调 DEPENDENCY_RESOLVE.construct_order(§4.15)│
│              │ ├─ Step6 调 AUDIT_REGISTRY(§4.7) E1-E20               │
│              │ └─ 输出: candidate/experimental 态 entry               │
│              ▼                                                      │
│  阶段2 上    │ PROMOTE_ENTRY(§4.13) ← 9 门禁(G1-G9)                  │
│  (上线晋升)  │ ├─ 渐进式部署: shadow→canary→full(§4.13 v1.10.0)     │
│              │ ├─ G4 检查 baseline 完整性(E12 前提)                  │
│              │ └─ 输出: active/live 态 + baseline 保存                │
│              ▼                                                      │
│  阶段3 改    │ EVOLVE_ENTRY(§4.9)                                    │
│  (日常变更)  │ ├─ metadata/schema_sig/code_ref/status 分类           │
│              │ ├─ status→active delegate §4.13; →deprecated §4.10   │
│              │ ├─ breaking 变更 delegate §4.11 EVOLVE_SCHEMA         │
│              │ └─ Step4 依赖方影响用 §4.15 transitive_deps           │
│              ▼                                                      │
│  阶段4 测    │ DECAY_SCAN(§4.8)                                      │
│  (衰减检测)  │ ├─ MVP: profit_factor + z_score(跨维度)              │
│              │ ├─ Phase1.5+: cusum_ph_bocpe 2/3投票(鲁棒CUSUM)      │
│              │ └─ 输出: decay_signal{严重度, decay_cause}             │
│              ▼                                                      │
│  阶段5 应/回 │ ADAPT_STRATEGY(§4.12) 或 ROLLBACK_ENTRY(§4.14)       │
│  (适应/回滚) │ ├─ ADAPT: Step0 baseline校验→Step1.5 原因分类→       │
│              │ │   crowding/overfitting/tech→退役; regime/depletion→refit│
│              │ └─ ROLLBACK: 实盘异常回退已知良好版本(7天冷却防flip-flop)│
│              ▼                                                      │
│  阶段6 退    │ RETIRE_ENTRY(§4.10)                                   │
│  (退役)      │ ├─ active→deprecated(90天宽限)→retired(无活跃引用)  │
│              │ ├─ 级联响应用 §4.15 transitive_deps 查传递依赖        │
│              │ └─ retired 保留审计，物理删除需满1年+ARCH审批          │
│              ▼                                                      │
│  阶段7 迁    │ MIGRATE_REGISTRY(§4.16) ← 触发: entry>500/exp>5000   │
│  (YAML→DB)   │ ├─ R1-R7 七阶段渐进式(YAML SSoT→PG SSoT)            │
│  v1.11.0新增 │ ├─ R4/R7 双 gate(完整性验证+迁移后审计)              │
│              │ ├─ 按 §4.15 construct_order 逆序迁移(被依赖方后迁)   │
│              │ └─ R6 不可逆: 28天清洁期+git快照+R7审计三条件        │
└─────────────────────────────────────────────────────────────────────┘

横切关注点（任意阶段可调用）:
  AUDIT_REGISTRY(§4.7)     — E1-E20 一致性审计，CONSTRUCT/EVOLVE/RETIRE/MIGRATE 内嵌调用（v1.18.0 E14 回测数据偏差/v1.19.0 E15 LLM 前瞻偏差+v1.32.0 A股Tradability Mask/v1.20.0 E16 因子冗余+v1.32.0 归因稳定性DASH/v1.21.0 E17 因果验证声明/v1.22.0 E18 LAP 前瞻污染检测+E19 因子构造偏差审计 LIB/v1.23.0 E20 RMT 去噪因子相关性矩阵审计）
  EVOLVE_SCHEMA(§4.11)     — schema 本身演进，breaking 变更走 Expand-Contract
  DEPENDENCY_RESOLVE(§4.15)— 依赖解析，CONSTRUCT(拓扑序)/RETIRE(级联)/EVOLVE_SCHEMA(影响范围)/MIGRATE(迁移顺序)
  DIFF_ENTRY(§4.18)        — 版本差异查询，EVOLVE_ENTRY(版本对比)/PROMOTE_ENTRY(候选vs基线)/EVOLVE_SCHEMA(兼容性判定)调用

跨文档职责边界（避免在本文档过度工程，引用而非新建算法）:
  RUN_BACKTEST            — 回测执行（产生 backtest_result，PROMOTE_ENTRY G1 输入）→ [52_backtest_framework_docking](52_backtest_framework_docking.md)
  ATTRIBUTION             — 归因分析（Brinson/factor-based，PROMOTE_ENTRY G6 benchmark_id 用途）→ 54 号 performance_attribution_report
  本文档仅登记 experiment_registry 的 backtest_bias_checks + attribution_result 字段（§7.2 v1.18.0），不重复 52/54 号执行逻辑
```

**算法调用矩阵**（何时调哪个）：

| 触发场景 | 调用算法 | 输入 | 输出 |
|---|---|---|---|
| 新建注册表/批量补 entry | §4.5 CONSTRUCT_REGISTRY | schema + data_sources | 落盘 YAML + 登记 |
| 一致性审计（施工后/定期） | §4.7 AUDIT_REGISTRY | registry_id | E1-E20 报告 |
| entry 参数/公式/code 变更 | §4.9 EVOLVE_ENTRY | change_set | 版本快照+依赖通知 |
| schema 字段增删改 | §4.11 EVOLVE_SCHEMA | old/new schema | 兼容性判定+迁移计划 |
| candidate→active 上线 | §4.13 PROMOTE_ENTRY | backtest_result | 9 门禁+baseline 保存 |
| 实盘异常需回退 | §4.14 ROLLBACK_ENTRY | rollback_request | 版本回退+仓位处置 |
| 检测到 alpha 衰减 | §4.8 DECAY_SCAN → §4.12 ADAPT_STRATEGY | strategy_id | 衰减态+适应决策 |
| 衰减确认持续/结构断裂 | §4.10 RETIRE_ENTRY | reason | deprecated→retired |
| 确定施工顺序/查级联/算影响 | §4.15 DEPENDENCY_RESOLVE | operation+entry_id | 拓扑序/依赖链/影响范围 |
| entry>500/exp>5000 触发 DB 迁移 | §4.16 MIGRATE_REGISTRY | registry_id | R1-R7 迁移+PG 成为 SSoT |
| 对比两版本/PR review/兼容性判定 | §4.18 DIFF_ENTRY | entry_id + version_a/b | 变更分类+semver bump+影响依赖 |

**关键依赖关系**：
- §4.13 PROMOTE_ENTRY 的 G4 门禁依赖 §4.7 E12 baseline 完整性检查
- §4.14 ROLLBACK_ENTRY Step6 依赖 §4.13 PROMOTE_ENTRY 保存的 baseline（回滚后重置 baseline）
- §4.12 ADAPT_STRATEGY Step0 依赖 §4.7 E12 + §4.13 G4 保存的 baseline
- §4.10 RETIRE_ENTRY 级联响应依赖 §4.15 DEPENDENCY_RESOLVE.transitive_deps
- §4.9 EVOLVE_ENTRY breaking 分支 delegate §4.11 EVOLVE_SCHEMA
- §4.5 CONSTRUCT_REGISTRY Step6 内嵌 §4.7 AUDIT_REGISTRY；Step4 内嵌 §4.15 construct_order
- §4.8 DECAY_SCAN 输出 decay_signal 是 §4.12 ADAPT_STRATEGY 的输入
- §4.16 MIGRATE_REGISTRY R1 迁移顺序依赖 §4.15 construct_order 的逆序（被依赖方后迁）；R7 审计 gate 复用 §4.7 AUDIT_REGISTRY
- §4.16 MIGRATE_REGISTRY R5 双写期间写操作复用 §4.9 EVOLVE_ENTRY / §4.10 RETIRE_ENTRY / §4.13 PROMOTE_ENTRY 的写入路径
- §4.18 DIFF_ENTRY Step5 依赖 §4.15 DEPENDENCY_RESOLVE.transitive_deps（breaking 变更时查受影响依赖方）；§4.11 EVOLVE_SCHEMA Step2 兼容性判定可 delegate §4.18 的 semver_delta 输出

> 💡 **导航图使用方式**：施工新注册表从 §4.5 起（先查 §4.15 construct_order 确定本表在拓扑序的位置）；entry 建成后审计走 §4.7；日常运维按"改→测→应/回→退"阶段选算法；entry 量增长触发阈值后走 §4.16 迁移到 DB；版本对比/PR review/兼容性判定走 §4.18 DIFF_ENTRY。本导航图是 13 算法的"目录页"，每个算法内部有完整伪代码 + 对标来源 + 个人项目适用性说明。

### 4.5 施工流程算法（每注册表通用 8 步，v1.2.0 新增）

12 个注册表统一遵循以下 8 步施工算法，确保 schema-代码-文档三方一致性。**这是 v1.1.x 缺失的施工环节流程算法**——v1.1.x 只给了 schema 和数据来源，未给可执行施工步骤，导致 P1 七注册表施工无标准流程可循。

```
算法 CONSTRUCT_REGISTRY(registry_id, schema, sources):
  输入: registry_id（如 REG-FCT-001）, entry_schema, data_sources{docs, code, existing_yaml}
  输出: 落盘 YAML + registry_of_registries 登记 + AGENTS.md 显化 + ARCH 进度更新

  Step 1【真源反查】
    for each source in data_sources:
      grep/excerpt 提取候选 entry 清单（编号/名称/分类/参数）
    去重合并 → candidate_entries[]

  Step 2【编号分配】
    for each entry in candidate_entries:
      按 {PREFIX}-{DOMAIN}-{NNN} 规则分配 entry_id
      冲突检测：grep 现有 YAML 确认无重号
      登记 variant_of 单向引用（不建反向 variants 列表，裁定 S4）

  Step 3【schema 填充】
    for each entry:
      填充 frontmatter 14 字段（§4 原则 1）+ entry_schema 全字段
      code_path 用稳定 path（禁止 node_id/edge_id）
      module_id 关联 depgraph MOD- 前缀
      doc_ref 关联 design memo §节号
      性能指标字段（IC/Sharpe 等）运行时留 null

  Step 4【交叉引用校验】（见 §4.6 矩阵）
    for each FK field (used_by_strategies/alpha_sources/risk_rules/...):
      反向验证被引用方存在 → 不存在则标 dangling，记入待定问题

  Step 5【半派生补全】（裁定 8）
    脚本反查补全 code_path/module_id/依赖关系（手写不擅长的字段）
    手写真源（编号/状态/语义）入 git，脚本产物不入 git

  Step 6【一致性审计】（见 §4.7 算法 E1-E20）
    运行 AUDIT_REGISTRY(registry_id)：
      - E1 frontmatter 14 字段齐全
      - E2 entry_id 编号格式合规 + 无重号
      - E3 status 对齐 module_lifecycle_status_vocabulary（candidate/experimental/active/deprecated/retired）
      - E4 FK 引用无 dangling（允许 forward-ref 到未施工注册表，标 pending）
      - E5 schema-代码漂移：entry.code_path 实际存在 + 符号匹配
      - E5b commit 绑定检查（code_commit 格式，DB 阶段强制，v1.4.0）
      - E6 编号-代码对齐：entry_count 声明 vs 实际一致
      - E7 裁定落实检查（如 S6 ruling_registry 登记）
      - E8 循环引用检测（variant_of/parent_experiment_id 链防环，v1.3.0）
      - E9 日期逻辑检查（created_at ≤ updated_at ≤ retired_date，v1.3.0）
      - E10 必填字段空值检查（核心字段非空，性能字段可空，v1.3.0）
      - E11 数据质量监控登记检查（factor/strategy 的 data_quality_policy，v1.4.0）
      - E12 baseline 保存完整性检查（live+ 策略的 baseline 字段齐全，v1.5.0）
      - E13 语义漂移检查（semantic_contract/null_semantics/default_fill_policy，v1.10.0）

  Step 7【治理同步】
    registry_of_registries.yaml 登记新 registry（tier/entry_count/status）
    AGENTS.md RULE-REGISTRY 段显化速查入口
    architecture_issue_registry.yaml #ARCH-BREG-001 更新进度
    若涉及改名（如 data_asset）→ ruling_registry.yaml 登记（S6 约束）

  Step 8【循环审查】
    重新通读全文 + 反查代码/注册表，再查一轮
    连续 1 轮零改动 → 施工完成
    否则回到 Step 3 修正
```

**施工顺序约束**（裁定 7）：P0（universe/benchmark/cost_model）→ P1-A（factor/strategy/indicator）→ P1-B（execution/risk/data/pattern）→ P2（field_dict/experiment）。回测必需输入优先 > 被测对象 > 交易/风控/数据/图形 > 治理/实验。

### 4.6 交叉引用矩阵（12 表间 FK 关系，v1.2.0 新增）

12 注册表通过 FK 字段相互引用，形成业务资产关系图。**v1.1.x 各 schema 散落 FK 字段但无全局矩阵**，施工时易遗漏反向引用校验。本矩阵明确每条 FK 的引用方→被引用方→基数。

| 引用方（FK 所在） | FK 字段 | 被引用方 | 基数 | 说明 |
|---|---|---|---|---|
| universe | used_by_strategies | strategy | 1:N | 池被哪些策略使用 |
| universe | data_source | data_asset.source_id | N:1 | 池数据来源 |
| benchmark | underlying_universe | universe | N:1 | 基准基于哪个池 |
| benchmark | data_source | data_asset.source_id | N:1 | 基准数据来源 |
| benchmark | used_by_strategies | strategy | 1:N | 基准被哪些策略对标 |
| cost_model | used_by_strategies | strategy | 1:N | 成本模型被哪些策略使用 |
| factor | universe | universe | N:1 | 因子适用池 |
| factor | belongs_to_strategies | strategy | 1:N | 因子被哪些策略使用 |
| factor | inputs | field_dictionary | N:N | 因子输入字段（forward-ref P2） |
| factor | variant_of | factor | N:1 | 因子变体（单向，self-ref） |
| factor | used_by_factors | technical_indicator | 1:N | 指标被哪些因子引用（反向） |
| strategy | alpha_sources | factor | N:N | 策略用哪些因子 |
| strategy | risk_rules | risk_limit | N:N | 策略受哪些限额约束 |
| strategy | variant_of | strategy | N:1 | 策略变体（单向，self-ref） |
| strategy | benchmark_id（v1.2.0 新增） | benchmark | N:1 | 策略对标基准 |
| technical_indicator | used_by_factors | factor | 1:N | 指标被哪些因子引用 |
| technical_indicator | inputs | field_dictionary | N:N | 指标输入字段（forward-ref P2） |
| execution_algo | cost_model_ref（v1.2.0 新增） | cost_model | N:1 | 算法用哪个成本模型 |
| risk_limit | scope_strategy（v1.2.0 新增） | strategy | N:1 | 限额作用于哪个策略（scope=strategy 时） |
| data_asset | provides_datasets | data_asset.datasets | 1:N | source 提供 datasets（self-ref 三实体） |
| data_asset | produced_by_jobs | data_asset.jobs | N:N | dataset 由哪些 job 产出（self-ref） |
| chart_pattern | used_by_factors | factor | 1:N | 形态被哪些因子引用 |
| chart_pattern | variant_of | chart_pattern | N:1 | 形态变体（单向，self-ref） |
| experiment | target_id | factor/strategy/indicator/pattern/risk_rule/execution_algo | N:1 | 实验测什么 |
| experiment | universe | universe | N:1 | 实验在哪个池上跑 |
| experiment | parent_experiment_id | experiment | N:1 | 迭代链（self-ref） |
| field_dictionary | source_system | data_asset.source_id | N:1 | 字段来自哪个数据源 |

**FK 完整性规则**：
- 强 FK（同 tier 已施工）：MUST 反向验证存在，dangling = 硬错误
- 弱 FK（跨 tier forward-ref 未施工）：允许 pending，登记到 §9.4 验收清单，被引用方施工后回填
- self-ref（variant_of / parent_experiment_id）：单向引用，禁止反向同步（裁定 S4 精神）

### 4.7 验证审计算法（半派生反查 + 一致性检查，v1.2.0 新增）

```
算法 AUDIT_REGISTRY(registry_id):
  输入: registry_id
  输出: audit_report{errors[], warnings[], pending[]}

  E1【frontmatter 完整性】
    required = {module_id, ttl, schema_version, registry_id, name, name_zh,
                description, owner, tier, status, version, created, last_updated,
                related_arch, unique_key}
    missing = required - frontmatter.keys()
    if missing: errors.append("frontmatter 缺字段: " + missing)

  E2【entry_id 编号合规】
    pattern = r"^{PREFIX}-{DOMAIN}-\d{3}$"  # 按 §4 原则 3
    for entry in entries:
      if not re.match(pattern, entry.id): errors.append("编号格式错: " + entry.id)
    duplicates = find_duplicates([e.id for e in entries])
    if duplicates: errors.append("重号: " + duplicates)

  E3【status 状态机合规】
    valid_status = {candidate, experimental, active, deprecated, retired}
    for entry in entries:
      if entry.status not in valid_status: errors.append("非法 status: " + entry.status)

  E4【FK 引用完整性】（按 §4.6 矩阵）
    for each FK in cross_ref_matrix[registry_id]:
      for entry in entries:
        ref_id = entry[FK.field]
        if ref_id is None: continue
        target_registry = FK.target
        if target_registry 已施工:
          if ref_id not in target_registry.entries:
            errors.append("dangling FK: " + entry.id + "." + FK.field + " -> " + ref_id)
        else:
          pending.append("forward-ref 未施工: " + entry.id + "." + FK.field + " -> " + ref_id)

  E5【schema-代码漂移检测】
    for entry in entries:
      if entry.code_path:
        if not file_exists(entry.code_path):
          errors.append("code_path 不存在: " + entry.id + " -> " + entry.code_path)
        else:
          # Select-String 核对实码符号（v2.6.0 教训：不能仅凭审计快照）
          if entry.symbol and not grep(entry.code_path, entry.symbol):
            warnings.append("符号未在 code_path 找到: " + entry.id + "." + entry.symbol)

  E5b【commit 绑定检查】（v1.4.0 新增，对标 [beefed.ai Feature Registry 2026](https://beefed.ai/en/feature-registry-governance-best-practices) compute_git）
    # beefed.ai: registry 应记录 "git://repo/path/to/feature.py@<commit>"
    # 确保可复现——code_path + commit 双绑定，非仅 path
    # YAML 阶段：git blame 天然提供 commit 追溯（code_commit 可选）
    # DB 阶段：code_commit 字段 MUST 非空（审计级 reproducibility，对标 §4 原则 9 Immutable Version）
    for entry in entries:
      if entry.code_commit:  # 可选字段，有值时验证格式
        if not re.match(r"^[0-9a-f]{7,40}$", entry.code_commit):
          warnings.append("code_commit 格式非 git hash: " + entry.id + "." + entry.code_commit)
      elif db_stage:  # DB 阶段强制
        warnings.append("DB 阶段缺 code_commit: " + entry.id + "（reproducibility 要求 path+commit 双绑定）")

  E6【编号-代码对齐】（v1.1.0 教训：DS 计数、factor 路径、indicator 第5类漂移）
    declared_count = frontmatter.entry_count
    actual_count = len(entries)
    if declared_count != actual_count:
      errors.append("entry_count 漂移: declared=" + declared_count + " actual=" + actual_count)

  E7【裁定落实检查】
    # S6: data_asset 改名须 ruling_registry 登记
    if registry_id == "REG-DATAFLOW-001":
      if not grep(ruling_registry, "data_asset|dataflow_graph|REG-DATAFLOW"):
        errors.append("S6 裁定未落实: ruling_registry 未登记改名")

  E8【循环引用检测】（v1.3.0 新增，variant_of / parent_experiment_id 链防环）
    # variant_of 单向引用链不可成环：A→B→C→A 会死循环查询
    for entry in entries:
      if entry.variant_of:
        chain = [entry.id]
        cursor = entry.variant_of
        while cursor is not None:
          if cursor in chain:
            errors.append("循环引用: " + " -> ".join(chain) + " -> " + cursor)
            break
          chain.append(cursor)
          parent = find_entry(cursor)
          cursor = parent.variant_of if parent else None
    # parent_experiment_id 同理（迭代链不可成环）

  E9【日期逻辑检查】（v1.3.0 新增）
    for entry in entries:
      if entry.created_at and entry.updated_at:
        if entry.created_at > entry.updated_at:
          errors.append("日期倒置: " + entry.id + " created_at > updated_at")
      # strategy 退役日期检查
      if hasattr(entry, 'go_live_date') and hasattr(entry, 'retired_date'):
        if entry.go_live_date and entry.retired_date:
          if entry.go_live_date > entry.retired_date:
            errors.append("日期倒置: " + entry.id + " go_live_date > retired_date")
      # last_evaluated_at 不可早于 created_at
      if hasattr(entry, 'last_evaluated_at') and entry.last_evaluated_at and entry.created_at:
        if entry.last_evaluated_at < entry.created_at:
          warnings.append("last_evaluated_at 早于 created_at: " + entry.id)

  E10【必填字段空值检查】（v1.3.0 新增，区分 nullable vs required）
    # 性能指标字段允许 null（§4 原则 6），但核心字段不允许
    core_fields = {id, name, name_zh, status, version, module_id, code_path}
    for entry in entries:
      for f in core_fields:
        if entry.get(f) is None or entry.get(f) == "":
          # code_path 对纯文档型 entry（如 field_dictionary 部分）可豁免
          if f == "code_path" and registry_id in {"REG-FLD-001"}:
            continue
          errors.append("必填字段空: " + entry.id + "." + f)

  E11【数据质量监控登记检查】（v1.4.0 新增，v1.6.0 修正缩进 + 补三种静默失败模式框架；对标 [metricgate 2026-04](https://metricgate.com/blogs/model-monitoring-metrics-guide/) + [apxml 2026](https://apxml.com/zh/courses/feature-stores-for-ml/chapter-3-data-consistency-quality/monitoring-feature-distribution) + [RisingWave 2026-04](https://risingwave.com/blog/feature-pipeline-observability-freshness-monitoring/)）
    # 数据质量是因子/策略健康度的另一维度，与衰减检测（§4.8）互补：
    #   衰减 = 策略级 alpha 退化（输出端，§4.8 DECAY_SCAN）
    #   数据质量 = 因子输入端退化（null_rate/drift/range，本检查）
    # metricgate 4 层监控：L1 Data Quality → L2 Data Drift → L3 Prediction Drift → L4 Performance
    # 原则"alert on earliest layer"——数据质量先于性能下降
    #
    # RisingWave 2026-04 三种静默失败模式框架（v1.6.0 新增，feature pipeline 静默失败的本质）：
    #   失败模式 1 Freshness Lag（新鲜度滞后）：pipeline 运行但输出特征停止更新，infra 监控全绿
    #     → 对应 data_quality_policy 的 freshness 检查（特征最后更新时间戳 staleness > SLA）
    #   失败模式 2 Data Incompleteness（数据不完整）：记录被丢弃/schema 变更/join 丢行，null_rate 静默攀升
    #     → 对应 data_quality_policy 的 null_rate 检查（>2x baseline 告警，RisingWave: 2% 噪声 vs 15% 管道断裂）
    #   失败模式 3 Distribution Drift（分布漂移）：pipeline 正常但特征值分布偏移，模型用失效模式预测
    #     → 对应 data_quality_policy 的 drift_method 检查（PSI/KS，apxml: PSI>0.2 主要漂移）
    #   三种模式都"静默"——infra 监控无法捕获，需 data-aware 监控（本 E11 检查即此）
    for entry in entries:
      if registry_id in {"REG-FCT-001", "REG-STR-001"}:  # factor/strategy 需数据质量监控
        if not entry.get("data_quality_policy"):
          warnings.append("未声明 data_quality_policy: " + entry.id +
                          "（建议登记 null_rate/drift/freshness 检测策略，对标 metricgate L1-L2 + RisingWave 三种静默失败模式）")
        else:
          policy = entry.data_quality_policy
          # 失败模式 2: null_rate 监控（RisingWave 2026-04: null rate > 2x baseline 告警）
          if "null_rate" not in policy:
            warnings.append("data_quality_policy 缺 null_rate: " + entry.id +
                            "（RisingWave 失败模式 2 Data Incompleteness）")
          # 失败模式 3: drift 监控（apxml 2026: PSI/KS，PSI<0.1 稳定 / 0.1-0.25 轻微 / >0.2 主要漂移）
          if "drift_method" not in policy:
            warnings.append("data_quality_policy 缺 drift_method: " + entry.id +
                            "（RisingWave 失败模式 3 Distribution Drift，建议 psi 或 ks，PSI>0.2 标主要漂移）")
          # 失败模式 1: freshness 监控（v1.6.0 新增，RisingWave: staleness > SLA 告警）
          if "freshness" not in policy:
            warnings.append("data_quality_policy 缺 freshness: " + entry.id +
                            "（RisingWave 失败模式 1 Freshness Lag，建议登记 SLA 阈值如 daily 特征 staleness>300s 告警）")

  E12【baseline 保存完整性检查】（v1.5.0 新增，v1.6.0 修正缩进——原 v1.5.0 误嵌套在 E11 else 块内导致无 policy 时跳过 E12 且 return 错位；对标 [LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/) + [Pomegra 2026 Edge Decay](https://pomegra.io/learn/library/track-e-trading-risk/active-trading/chapter-04-trading-edges/edge-decay-and-adaptation)）
    # LuxAlgo 2026-08-03 明确："Without that baseline, it is difficult to distinguish
    # normal variance from a genuine change in the edge"
    # baseline MUST 在策略 deployment 时保存，是 §4.8 DECAY_SCAN + §4.12 ADAPT_STRATEGY 的前提
    # E11 查输入端数据质量，E12 查 baseline 完整性（衰减检测的前提条件）
    # 仅对 lifecycle_status >= live 的 strategy 检查（candidate/backtest 阶段无 baseline 需求）
    if registry_id == "REG-STR-001":
      for entry in entries:
        if entry.lifecycle_status in {"live", "monitoring", "decayed"}:
          # baseline 扩展字段（§6.1.2 v1.5.0 新增）
          baseline_fields = {baseline_sharpe, baseline_expectancy,
                             baseline_win_rate, baseline_profit_factor,
                             baseline_max_drawdown, baseline_trade_frequency}
          missing_baseline = [f for f in baseline_fields
                              if entry.get(f) is None]
          if missing_baseline:
            warnings.append("live/monitoring/decayed 策略缺 baseline 字段: " + entry.id +
                            " " + missing_baseline +
                            "（衰减检测前提，LuxAlgo 2026-08-03 要求 deployment 时保存完整 baseline）")
          # decay_threshold 必填（§4.8 DECAY_SCAN 恢复判定基准）
          if not entry.get("decay_threshold"):
            warnings.append("缺 decay_threshold: " + entry.id +
                            "（§4.8 DECAY_SCAN 恢复判定基准，默认 0.7）")

  E13【语义漂移检查】（v1.10.0 新增，对标 [oracles.cloud 2026-01 Data Contracts](https://oracles.cloud/implementing-data-contracts-a-developer-guide-to-fixing-silo/) + [neojn 2026-05 Feature Store Drift](https://www.neojn.com/ko/insights/articles/feature-store-drift-monitoring-ml) + [aiopsschool 2026-02 Data Drift Monitoring](https://aiopsschool.com/blog/data-drift-monitoring/)）
    # oracles.cloud 2026-01 明确漂移分 3 类，E11 只覆盖前 2 类，缺第 3 类 semantic drift：
    #   ① Schema drift（结构漂移）—— 新增/删除/改类型字段，§4.11 EVOLVE_SCHEMA + E10 已覆盖
    #   ② Statistical/data drift（统计漂移）—— 分布漂移/null_rate 攀升，E11 已覆盖（PSI/KS/null_rate）
    #   ③ Semantic drift（语义漂移）—— "same field but meaning changes"，最难检测
    #      例：currency unit 变了（元→分）、复权口径变了（前复权→不复权）、
    #          timestamp 时区变了（UTC→Local）、null 语义变了（缺失→零值）、
    #          categorical 编码变了（int code→string）。字段名/类型/分布都没变，但"意思"变了。
    # neojn 2026-05: "The insidious quality of feature store drift is that nothing crashes;
    #   the system continues serving predictions, just quietly wrong ones."
    #   语义漂移是最隐蔽的——schema 检查通过、分布检查通过，但模型用失效语义预测。
    #
    # 检测方法（oracles.cloud + neojn 共识）：
    #   a. data_contract 字段：entry 应声明字段的 business_definition + unit + adjust_method
    #      （field_dictionary schema §7.1 已有 business_definition/unit/adjust_method/pit_property）
    #   b. 定期 reconciliation jobs（neojn: "the unglamorous practice that catches the bugs
    #      statistical monitoring misses"）—— 从原始事件日志重算特征，对比在线服务返回值
    #   c. null 语义一致性（neojn: "A missing credit utilization ratio is fundamentally
    #      different from a zero utilization ratio"）—— 缺失≠零值，混淆会反转风险信号
    #   d. 默认填充策略审计（neojn: "substitute zero for missing numeric fields is harmless
    #      for additive counters but catastrophic for ratio features"）
    #
    # 本检查聚焦 factor/strategy 的输入字段语义一致性（与 E11 统计漂移互补）：
    for entry in entries:
      if registry_id in {"REG-FCT-001", "REG-STR-001"}:
        policy = entry.get("data_quality_policy", {})
        # 检查 a: data_quality_policy 应声明 semantic_contract（字段语义契约）
        if "semantic_contract" not in policy:
          warnings.append("data_quality_policy 缺 semantic_contract: " + entry.id +
                          "（oracles.cloud 第3类 semantic drift：同字段含义变化，如复权口径/币种/时区/null语义。" +
                          "建议登记关键字段的 unit/adjust_method/null_semantics，对标 neojn 2026-05 reconciliation）")
        else:
          contract = policy.semantic_contract
          # 检查 c: null_semantics 声明（缺失≠零值，neojn 强调）
          if "null_semantics" not in contract:
            warnings.append("semantic_contract 缺 null_semantics: " + entry.id +
                            "（neojn 2026-05: missing≠zero，缺失比率因子≠零利用率，混淆反转风险信号）")
          # 检查 d: default_fill_policy 审计（零填充对比率类因子有害）
          if contract.get("default_fill_policy") == "zero" and "ratio" in str(entry.get("formula", "")).lower():
            warnings.append("default_fill_policy=zero 对 ratio 类因子有害: " + entry.id +
                            "（neojn 2026-05: zero fill harmless for counters but catastrophic for ratios）")
        # 检查 b: reconciliation 配置（neojn: 定期对账作业捕获统计监控遗漏的 bug）
        if "reconciliation" not in policy:
          # reconciliation 非必填（成本较高），仅建议
          pass  # 不告警，仅在文档建议 Phase 1.5+ 启用

  E14【回测数据偏差检查】（v1.18.0 新增，对标 [digitalninjasystems 2026-05-28](https://digitalninjasystems.wpcomstaging.com/2026/05/28/why-your-backtest-results-might-be-misleading-and-how-to-fix-it/) + [thedatascientist 2026-06-10](https://thedatascientist.com/the-data-leakage-traps-hiding-in-financial-market-data-and-how-to-build-a-leak-free-dataset/) + [dev.to 2026-07-06](https://dev.to/tradevodata/survivorship-bias-vs-lookahead-bias-the-two-silent-backtest-killers-pmm) + [preprints.org 2026-06-04](https://www.preprints.org/manuscript/202606.0436) + [LobeHub 2026-07-31](https://lobehub.com/skills/brainbytes-dev-everything-claude-trading-data-quality)）
    # E11 查特征统计漂移（分布/null_rate），E13 查语义漂移（字段含义），E14 查**数据源头偏差**——
    #   回测数据本身是否含生存偏差/前瞻偏差，这是比特征漂移更根本的"数据是否可信"问题。
    # preprints.org 2026-06 三分类偏差 taxonomy：
    #   ① universe-membership contamination（生存偏差）——仅含存活至今日的公司，排除破产/退市/并购
    #      US equity 策略年化收益高估 1-3%，小市值/价值策略更严重
    #   ② price-data forward leakage（前瞻偏差）——使用决策时未可知信息（如财报按财报期而非公布日期对齐）
    #      mean-reversion 策略收益虚增 40-60%
    #   ③ stop-exit sequencing violations（止损退出时序错误）——止损/止盈在当日收盘价而非次日开盘执行
    # digitalninjasystems 2026-05: "Most backtests that look spectacular fail because they were tuned to noise"
    # thedatascientist 2026-06: 前瞻偏差是"silent killer"——schema 检查通过、分布检查通过，但回测用了未来信息
    #
    # 本检查聚焦三个维度：
    #   a. experiment_registry 的回测 entry 是否声明 backtest_bias_checks（v1.18.0 §7.2 新增字段）
    #   b. data_asset_registry 的 dataset 是否声明 survivorship_free / pit_available（v1.18.0 §6.2.3 新增字段）
    #   c. universe_registry 的 universe entry 是否声明 pit_constituent_construction / delisted_handling（v1.24.0 新增）
    # 仅做"声明完整性"检查（非重新检测偏差——偏差检测属于 52 号回测框架职责，本表只管元数据登记）
    if registry_id == "REG-EXP-001":  # experiment_registry
      for entry in entries:
        if entry.experiment_type in {"backtest", "walk_forward", "param_search"}:
          bias = entry.get("backtest_bias_checks")
          if not bias:
            warnings.append("回测实验缺 backtest_bias_checks: " + entry.id +
                            "（preprints.org 2026-06 三分类偏差：survivorship/lookahead/stop-exit。" +
                            "未声明=未做偏差治理，回测结果可信度存疑）")
          else:
            # 检查三分类是否都声明（passed/failed/unknown，unknown 也算声明——诚实记录"未检查"）
            for bias_type in {"survivorship", "lookahead", "stop_exit"}:
              if bias_type not in bias:
                warnings.append("backtest_bias_checks 缺 " + bias_type + ": " + entry.id +
                                "（preprints.org 2026-06 三分类之一，未声明=该类偏差未评估）")
    if registry_id == "REG-DATAFLOW-001":  # data_asset_registry
      for ds in datasets:
        # 行情类 dataset（price/quote）须声明生存偏差状态
        if "price" in str(ds.get("name", "")).lower() or "quote" in str(ds.get("name", "")).lower():
          if ds.get("survivorship_free") is None:
            warnings.append("行情 dataset 缺 survivorship_free 声明: " + ds.dataset_id +
                            "（digitalninjasystems 2026-05: 生存偏差使 US equity 年化高估 1-3%。" +
                            "AKShare 日线=unknown，商业源 Norgate/Compustat=true）")
        # 财报类 dataset 须声明 PIT 可用性 + 公布滞后
        if "fundamental" in str(ds.get("name", "")).lower() or "earnings" in str(ds.get("name", "")).lower():
          if ds.get("pit_available") is None:
            warnings.append("财报 dataset 缺 pit_available 声明: " + ds.dataset_id +
                            "（thedatascientist 2026-06: 前瞻偏差是 silent killer，财报须按公布日期非财报期对齐）")
          if ds.get("earnings_lag_days") is None:
            warnings.append("财报 dataset 缺 earnings_lag_days: " + ds.dataset_id +
                            "（财报公布平均滞后天数，用于 PIT 对齐校验）")

  E15【LLM 前瞻偏差检查 + A 股 Tradability Mask 检查】（v1.19.0 新增，v1.32.0 扩展 A 股涨跌停板上游污染检查，对标 [Look-Ahead-Bench arXiv:2601.13770 2026-01](https://arxiv.org/pdf/2601.13770) + [KTD-FIN arXiv:2605.28359 2026](https://arxiv.org/pdf/2605.28359) + [CSDN 2026-08-09 LLM 驱动量化](https://blog.csdn.net/tingyunye/article/details/155138329) + [arXiv:2507.07107v2 2026-05 Mask-First Design](https://arxiv.org/abs/2507.07107)）
    # E14 查传统回测偏差（survivorship/lookahead/stop_exit），E15 查 LLM 时代第四类偏差——
    #   memorization leakage（记忆泄漏）：LLM 训练语料含回测期未来信息，模型凭记忆而非预测给信号
    # CSDN 2026-08-09 §5.2: "用 2023 年的 GPT-4 去测试 2020 年的策略，效果一定好到爆炸——
    #   因为 GPT-4 在训练时已经读过 2020 年的新闻了，它知道未来发生了什么"
    # Look-Ahead-Bench 2026-01: 标准 LLM（Llama 3.1/DeepSeek 3.2）显著前瞻偏差（alpha decay 严重），
    #   Pitinf 模型（专为金融设计的 PiT LLM）随规模增大泛化能力提升
    # KTD-FIN 2026 4-level masking: bright/stock-blind/date-blind/blinded 四级脱敏协议，
    #   最强攻击者 top-5 ticker 恢复率仅 10.2%，联合成功率 1.5%——证明 blinded 条件有效缓解泄漏
    #
    # 本检查聚焦三个维度（仅查声明完整性，不重做检测——LLM 前瞻偏差检测属 52 号回测框架职责）：
    #   a. data_asset_registry 的 dataset 是否声明 llm_training_cutoff（LLM 训练截止日期）
    #   b. data_asset_registry 的 dataset 是否声明 lookahead_test_method（前瞻偏差测试方法）
    #   c. experiment_registry 的回测 entry 是否声明 llm_lookahead_check_result（LLM 前瞻偏差检测结果）
    # 适用范围：仅对 LLM-driven 实验/数据集检查；非 LLM 实验 applicable=false 跳过
    if registry_id == "REG-DATAFLOW-001":  # data_asset_registry
      for ds in datasets:
        # 仅对 LLM-relevant dataset 检查（news/llm_embedding/llm_signal 等关键字）
        ds_name = str(ds.get("name", "")).lower()
        is_llm_relevant = any(k in ds_name for k in {"news", "llm", "embedding", "nlp", "sentiment_text", "report_text"})
        if is_llm_relevant:
          if ds.get("llm_training_cutoff") is None:
            warnings.append("LLM-relevant dataset 缺 llm_training_cutoff: " + ds.dataset_id +
                            "（Look-Ahead-Bench 2026-01: LLM 训练截止日期决定回测期是否落入训练窗口。" +
                            "回测期 < 训练截止日期 = 高前瞻偏差风险，模型可能凭记忆而非预测给信号。" +
                            "MVP 未用 LLM 时可填 N/A，Phase 2+ MUST 声明）")
          if ds.get("lookahead_test_method") is None:
            warnings.append("LLM-relevant dataset 缺 lookahead_test_method: " + ds.dataset_id +
                            "（KTD-FIN 2026 4-level masking: bright/stock-blind/date-blind/blinded。" +
                            "MVP 未用 LLM 时可填 N/A，Phase 2+ 评估 LLM agent 时 MUST 至少跑 blinded 级）")
    if registry_id == "REG-EXP-001":  # experiment_registry
      for entry in entries:
        # 仅对 LLM-driven 回测实验检查（target_type=strategy 且 tags 含 llm/meta_labeling_llm 等）
        tags = entry.get("tags", []) or []
        is_llm_driven = ("llm" in str(tags).lower() or
                         "llm_generated" in str(tags).lower() or
                         entry.get("target_type") == "strategy" and
                         any("llm" in str(t).lower() for t in tags))
        if is_llm_driven and entry.experiment_type in {"backtest", "walk_forward", "param_search"}:
          llm_check = entry.get("llm_lookahead_check_result")
          if not llm_check:
            warnings.append("LLM-driven 回测实验缺 llm_lookahead_check_result: " + entry.id +
                            "（Look-Ahead-Bench 2026-01: LLM 回测 MUST 评估记忆泄漏。" +
                            "未声明=未做 LLM 前瞻偏差治理，回测结果可能虚高。" +
                            "MVP 未用 LLM 时可填 {applicable: false, reason: ...}，Phase 2+ MUST 评估）")
          else:
            # 检查 applicable 字段（true 时须有 masking_level + alpha_decay 测试结果）
            if llm_check.get("applicable", True):
              if "masking_level" not in llm_check:
                warnings.append("llm_lookahead_check_result 缺 masking_level: " + entry.id +
                                "（KTD-FIN 2026 4-level: bright/stock-blind/date-blind/blinded，" +
                                "MUST 至少跑 blinded 级才算完整 LLM 前瞻偏差评估）")
              if "alpha_decay" not in llm_check:
                warnings.append("llm_lookahead_check_result 缺 alpha_decay: " + entry.id +
                                "（Look-Ahead-Bench 2026: alpha decay 跨 regime 测量是区分" +
                                "真预测能力 vs 记忆回放的关键指标）")
    # v1.32.0 新增：A 股 Tradability Mask 检查（对标 arXiv:2507.07107v2 Mask-First Design）
    # A 股 ±10%/±20% 涨跌停板使部分收盘价不可执行——标准实现先读价格再过滤行，
    # 污染通过 MA/correlation/rank 静默传播（upstream contamination），实证虚增 IC 18% + 降低 Sharpe 0.44
    # 这是特殊的 look-ahead bias（使用不可执行的价格仿佛可执行），与 LLM memorization leakage 同类
    # A 股因子计算实验 MUST 声明 tradability_mask_policy
    if registry_id == "REG-EXP-001":  # experiment_registry
      for entry in entries:
        # 仅对 A 股因子计算实验检查（market=ashare 且涉及因子计算）
        market = str(entry.get("market", "")).lower()
        tags = entry.get("tags", []) or []
        is_ashare_factor = ("ashare" in market or "a_share" in market or
                            "ashare" in str(tags).lower())
        if is_ashare_factor and entry.experiment_type in {"backtest", "walk_forward", "param_search"}:
          tmp = entry.get("tradability_mask_policy")
          if tmp is None:
            warnings.append("A 股因子实验缺 tradability_mask_policy: " + entry.id +
                            "（arXiv:2507.07107v2: 涨跌停板上游污染虚增 IC 18%+降低 Sharpe 0.44。" +
                            "MUST 填 mask_first（数据加载时构造掩码贯穿算子），" +
                            "row_filter（事后行删除）不足，none=未处理 warning highlight）")
          elif tmp == "none":
            warnings.append("tradability_mask_policy=none: " + entry.id +
                            "（arXiv:2507.07107v2: 未处理涨跌停板上游污染，" +
                            "回测结果可能虚高 IC 18%，MUST 实现 mask_first）")

  E16【因子冗余/相关性检查 + 归因稳定性检查】（v1.20.0 新增，v1.32.0 扩展归因稳定性，对标 [EntroPy 2026-05 redundancy.py](https://github.com/HeroBlast10/EntroPy/blob/main/docs/PRODUCTION_FACTOR_RESEARCH_UPGRADE_2026_05.md) + [factordbms Orthogonality Analysis](https://pypi.org/project/factordbms/) + [CSDN 2026-07-13 因子去冗余](https://wenku.csdn.net/answer/2k1vuaoqxxap) + [QuantGPT Self-Correlation](https://skillsllm.com/skill/quantgpt) + [DASH arXiv:2605.21492 2026-05](https://arxiv.org/abs/2605.21492)）
    # E1-E15 查单因子属性（编号/状态/版本/血缘/漂移/偏差），E16 查**因子间关系 + 归因稳定性**——
    #   因子库整体多样性。多个高相关因子=伪多样化，组合实际风险被低估。
    # EntroPy 2026-05 redundancy.py 三维度：
    #   ① effective signal correlation（因子值截面相关性）
    #   ② factor long-short return correlation（因子收益时序相关性）
    #   ③ exposure-vector cosine similarity（暴露向量余弦相似度）
    # factordbms 三阶段：Global Correlation Check → Clustering → Selection
    # CSDN 2026-07: "若两个因子相关性过高（如>0.7），则它们提供的信息重叠"
    # 选择逻辑：逐步增量检验，优先保留 3-5 个互补因子，residual alpha Sharpe 太弱→剔除
    #
    # 本检查聚焦两个维度（仅查声明完整性，不重做相关性计算——相关性计算属 15 号因子工程职责）：
    #   a. factor_registry 的 entry 是否声明 correlation_group（相关性分组）
    #   b. factor_registry 的 entry 是否声明 redundancy_status（冗余状态）
    # 同 correlation_group 的因子 = 高相关簇，MUST 有一个 independent + 其余 redundant/orthogonal
    if registry_id == "REG-FCT-001":  # factor_registry
      for entry in entries:
        if entry.get("correlation_group") is None:
          warnings.append("因子缺 correlation_group: " + entry.id +
                          "（EntroPy 2026-05: 因子间相关性是组合层面关键属性。" +
                          "同组因子高相关=伪多样化，组合风险被低估。" +
                          "MVP 可按因子 10 分类粗分，Phase 1.5+ 接入三维度检测后精细化）")
        if entry.get("redundancy_status") is None:
          warnings.append("因子缺 redundancy_status: " + entry.id +
                          "（independent=独立信号/redundant=与他因子冗余/orthogonal=正交。" +
                          "同 correlation_group 内 MUST 至少 1 个 independent，其余标 redundant/orthogonal）")
      # 跨因子检查：同 correlation_group 内 MUST 至少 1 个 independent
      groups = {}
      for entry in entries:
        g = entry.get("correlation_group")
        if g:
          groups.setdefault(g, []).append(entry)
      for g, members in groups.items():
        if len(members) > 1:
          has_independent = any(m.get("redundancy_status") == "independent" for m in members)
          if not has_independent:
            warnings.append("correlation_group " + str(g) + " 内无 independent 因子（" +
                            str(len(members)) + " 个因子全为 redundant/orthogonal/未声明）：" +
                            "（同组 MUST 至少 1 个 independent 作为代表信号，其余为冗余/正交）")
    # v1.32.0 新增：归因稳定性检查（对标 DASH 不可能性定理 arXiv:2605.21492）
    # DASH Lean 4 机器验证：collinearity 下 SHAP 排名结构性不稳定——
    #   faithfulness + stability + completeness 三者不可兼得，68% 公开数据集出现归因翻转
    # correlation_group 非空的因子（即存在 collinear 同组因子）SHOULD 声明 attribution_stability
    # flip_rate>20% = 归因不稳定 warning highlight（冗余方向判断本身可能不可靠）
    if registry_id == "REG-FCT-001":  # factor_registry
      for entry in entries:
        cg = entry.get("correlation_group")
        if cg is not None:
          as_obj = entry.get("attribution_stability")
          if as_obj is None:
            warnings.append("correlation_group 非空因子缺 attribution_stability: " + entry.id +
                            "（DASH arXiv:2605.21492: collinearity 下 SHAP 排名结构性不稳定，" +
                            "68% 数据集出现归因翻转。MVP 填 {method: none}，" +
                            "Phase 1.5+ ML 因子 SHOULD 启用 DASH M≥5 跨模型聚合）")
          else:
            flip_rate = as_obj.get("flip_rate")
            if flip_rate is not None and flip_rate > 0.20:
              warnings.append("attribution_stability flip_rate>20%: " + entry.id +
                              " flip_rate=" + str(flip_rate) +
                              "（DASH: 归因不稳定，冗余方向判断可能不可靠，" +
                              "MUST 人工裁定冗余方向，SHOULD 增加 model_count 至 ≥25）")

  E17【因果验证 + 设定结构检查】（v1.21.0 新增，v1.31.0 扩展设定结构，对标 [causal-quant v0.4.1 2026-07-09](https://github.com/meacreatio/causal-quant) + [CIR-ACTIVA arXiv:2608.03715 2026-08-04](https://arxiv.org/abs/2608.03715) + [CFA Institute 2025 Factor Mirage López de Prado](https://rpc.cfainstitute.org/research/foundation/2025/causality-factor-investing)）
    # E1-E16 查统计属性（编号/状态/版本/血缘/漂移/偏差/冗余），E17 查**因果属性 + 设定结构**——
    #   因子背后的经济因果逻辑。相关性≠因果性，回测可能因混淆变量/luck/选择偏差虚高。
    # causal-quant（de Prado 2023/2026 + Bailey 2014/2017 协议实现）：
    #   钉住回测撒谎的三种方式——luck（运气）/confounding（混淆）/selection across everything you tried
    #   声明因果图 DAG → 运行证伪测试电池 → 量化报告 H-score（存活"搜索+选择"的 edge 比例）
    # CIR-ACTIVA：摊销干预预测框架，回答"若某序列被外部冲击，系统如何响应"
    # v1.31.0 Factor Mirage 扩展（López de Prado & Zoonekynd CFA Institute 2025/2026）：
    #   collider（碰撞变量）比 confounder 更危险——含 collider 的错误设定模型展现更高 R²+更低 p-value，
    #   计量教规主动偏好这类错误模型，系数符号可翻转（+0.08→−0.04）。
    #   仅声明 causal_graph 不够，MUST 显式枚举排除的 confounder 和纳入的 collider。
    # 因果验证 gate 的时机：注册时（非上线时）——注册即声明因果图，避免事后合理化
    #
    # 本检查聚焦声明完整性（不重做因果计算——因果推断属 15 号因子工程职责）：
    #   factor_registry 的 entry 是否声明 causal_graph（因果图/经济逻辑描述）
    #   v1.31.0 扩展：price-derived 因子 SHOULD 声明 causal_structure（confounders/colliders）
    if registry_id == "REG-FCT-001":  # factor_registry
      for entry in entries:
        if entry.get("causal_graph") is None:
          warnings.append("因子缺 causal_graph: " + entry.id +
                          "（causal-quant 2026-07: 因子注册时 MUST 声明因果图/经济逻辑。" +
                          "相关性≠因果性，回测可能因混淆变量/luck/选择偏差虚高。" +
                          "MVP 可填自然语言描述（如'高 ROE→持续盈利能力→股价上涨'），" +
                          "Phase 1.5+ 接入 causal-quant 证伪电池后补 H-score）")
        # v1.31.0 新增：causal_structure 设定结构检查（Factor Mirage collider/confounder）
        cs = entry.get("causal_structure")
        if cs is None:
          warnings.append("price-derived 因子缺 causal_structure: " + entry.id +
                          "（CFA Institute 2025 Factor Mirage: collider 比 confounder 更危险，" +
                          "含 collider 模型更高 R²+更低 p-value，系数符号可翻转。" +
                          "MVP 用自然语言填 confounders/colliders，collider 非空=设定风险标志）")
        elif cs.get("colliders"):  # collider 非空 = warning highlight
          warnings.append("⚠️ 因子 " + entry.id + " causal_structure.colliders 非空: " +
                          str(cs.get("colliders")) +
                          "（Factor Mirage 风险：collider 变量被因子和收益共同影响，" +
                          "更强关联无法货币化=海市蜃楼。MUST 审视是否应移除该控制变量）")

  E18【LLM 前瞻污染检测 LAP + Temporal Leakage 测量】（v1.22.0 新增，v1.31.0 扩展 Temporal Leakage，对标 [arXiv:2512.23847v2 2026-06-12 LAP](https://arxiv.org/html/2512.23847v2) + [FinCAD arXiv:2605.24564 2026-05-23](https://arxiv.org/pdf/2605.24564) + [MemGuard-Alpha arXiv:2603.26797](https://arxiv.org/pdf/2603.26797) + [arXiv:2608.02985v1 2026-08-04 Temporal Leakage Measurement](https://arxiv.org/abs/2608.02985)）
    # E15 查数据侧防御（KTD-FIN masking），E18 查**模型侧诊断 + 测量**——LLM 权重内已记忆未来结果，
    #   数据管道审计看不见。LAP（Lookahead Propensity）= P(up)+P(down)，用"日期-only 召回查询"
    #   （只给 firm+ticker+日期，无 headline/transcript）估计 LLM 内化未来结果的概率。
    #   LAP 在训练期内显著为正，越过 cutoff 后坍塌至近零。
    #   污染检验回归：Y_{t+1} = β₁μ̂_t + β₂LAP + β₃(LAP×μ̂_t)，β₃>0 即前瞻偏差污染指征。
    # FinCAD: 推理时 Context-Aware Decoding 改编——对抗式搜索记忆激活 prior，logit 层减去，
    #   in-sample 记忆日回测收益降 67.1%，OOS 与 baseline 差 <$8K。
    # MemGuard-Alpha CMMD: 利用多 LLM 训练 cutoff 差异分离记忆驱动 vs 推理驱动信号，
    #   CMMD Sharpe 4.11 vs 未过滤 2.76（+49%），干净信号日均 14.48bps vs 污染 2.13bps（7 倍差）。
    # v1.31.0 Temporal Leakage 扩展（arXiv:2608.02985v1 Zeyu Zhang 2026-08-04）：
    #   标准 pre/post-cutoff 检查 uninformative——recency 模仿 leakage，被动回测数学不可分离。
    #   detection（LAP/E15）回答"是否泄漏"，measurement 回答"泄漏多少"——
    #   matched clean control 全局测量+leakage-adjusted score，boundary detection 边界定位。
    #   "Backtests need not be discarded; they need one defensible reference."
    #
    # 本检查聚焦声明完整性（不重做 LAP/Temporal Leakage 计算——属 LLM 推理层职责）：
    #   experiment_registry 的 LLM-driven 回测 entry 是否声明 lap_check_result
    #   v1.31.0 扩展：LLM-driven 回测 entry MAY 声明 temporal_leakage_measurement
    if registry_id == "REG-EXP-001":  # experiment_registry
      for entry in entries:
        tags = entry.get("tags", []) or []
        is_llm_driven = ("llm" in str(tags).lower() or
                         "llm_generated" in str(tags).lower())
        if is_llm_driven and entry.experiment_type in {"backtest", "walk_forward"}:
          lap_check = entry.get("lap_check_result")
          if not lap_check:
            warnings.append("LLM-driven 回测实验缺 lap_check_result: " + entry.id +
                            "（LAP arXiv:2512.23847: LLM 可能凭记忆而非预测给信号。" +
                            "MVP 未用 LLM 时可填 {applicable: false}，" +
                            "Phase 2+ MUST 跑 LAP×LLM 交互项回归，β₃>0=前瞻污染）")
          # v1.31.0 新增：temporal_leakage_measurement 测量声明检查（warning 级，MVP 不阻断）
          tlm = entry.get("temporal_leakage_measurement")
          if tlm is None:
            warnings.append("LLM-driven 回测实验缺 temporal_leakage_measurement: " + entry.id +
                            "（arXiv:2608.02985 2026-08: 标准 pre/post-cutoff 检查 uninformative，" +
                            "recency 模仿 leakage 被动回测不可分离。MVP 无 LLM 回测填 none，" +
                            "Phase 1.5+ origin=llm_generated 实验 SHOULD 启用 matched_control 测量泄漏剂量）")
          elif tlm.get("method") == "matched_control" and tlm.get("leakage_score", 0) > 0:
            warnings.append("LLM 回测实验 " + entry.id + " temporal_leakage_measurement.leakage_score=" +
                            str(tlm.get("leakage_score")) + " > 0（检测到泄漏剂量，" +
                            "MUST 审视 leakage-adjusted score 是否仍支持结论）")

  E19【因子构造偏差审计 LIB】（v1.22.0 新增，对标 [arXiv:2604.07880 2026-04-09 企业债因子动物园](https://arxiv.org/html/2604.07880v1) + [Open Bond Asset Pricing](https://openbondassetpricing.com/)）
    # E1-E18 查注册表属性，E19 查**因子构造方法学偏差**——企业债因子动物园复制危机揭示两个偏差：
    #   ① Latent Implementation Bias (LIB)：TRACE 交易价含测量误差，同一噪声价格进入信号和收益分母，
    #      相关误差被误认为 premium。A 股类比：复权价/成交量既是因子输入又是收益计算分母。
    #   ② ex-post 收益过滤嵌入未来信息（look-ahead bias）：去极值/去流动性差样本用了全期统计量。
    # Dickerson-Robotti-Rossetti 纠正两偏差后 108 个企业债因子多数不再显著。
    # 少数存活因子主要是 credit-spread-based value 信号。
    #
    # 本检查聚焦两个维度（仅查声明完整性，不重做偏差计算）：
    #   a. factor_registry 的 entry 是否声明 lib_audit（构造偏差审计结果）
    #   b. factor_registry 的 entry 是否声明 ex_post_filter_audit（ex-post 过滤审计）
    if registry_id == "REG-FCT-001":  # factor_registry
      for entry in entries:
        # 仅对 price/volume 衍生因子检查（基本面因子无 LIB 风险）
        inputs = str(entry.get("inputs", [])).lower()
        is_price_derived = any(k in inputs for k in {"close", "vwap", "price", "volume", "amount", "open", "high", "low"})
        if is_price_derived:
          if entry.get("lib_audit") is None:
            warnings.append("price-derived 因子缺 lib_audit: " + entry.id +
                            "（arXiv:2604.07880 企业债因子动物园: 信号与收益共用噪声数据源=Latent Implementation Bias。" +
                            "A 股复权价/成交量既是因子输入又是收益分母，相关误差被误认为 premium。" +
                            "MVP 可填 {checked: false, reason: 'manual_factor'}，Phase 1.5+ MUST 审计信号-收益数据源独立性）")
          if entry.get("ex_post_filter_audit") is None:
            warnings.append("因子缺 ex_post_filter_audit: " + entry.id +
                            "（arXiv:2604.07880: ex-post 去极值/去流动性差样本用全期统计量=嵌入未来信息。" +
                            "MVP 可填 {checked: false}，Phase 1.5+ MUST 审计过滤是否用 walk-forward 统计量）")

  # E20【RMT 去噪因子相关性矩阵审计】（v1.23.0 新增，对标 [arXiv:2507.17211v2 2026-08-07 EFS](https://arxiv.org/html/2507.17211v2) + [arXiv:2601.07687v4 2026-08-02 物理信息奇异值学习](https://arxiv.org/html/2601.07687v4) + [Marchenko-Pastur 1967](https://en.wikipedia.org/wiki/Marchenko%E2%80%93Pastur_distribution)）
  # E16 查因子冗余声明（correlation_group/redundancy_status），E20 查**冗余检测的方法学质量**——
  #   因子相关性矩阵在 N_factors 较大/T_observations 有限时含大量噪声特征值。
  #   Marchenko-Pastur 律给出纯噪声特征值上界 λ+ = σ²(1+√q)²（q=N/T），
  #   落在 [λ-, λ+] 区间内的特征值是噪声而非信号，MUST 用 RMT 去噪（clipping/shrinkage）后
  #   再计算冗余指标，否则噪声驱动的伪相关被误判为因子冗余。
  # EFS (arXiv:2507.17211v2 2026-08) 证明 RMT 去噪 + 正则化 QP 在美股/港股/A股三市场
  #   均优于未去噪基线，且无额外调参成本。
  # 物理信息奇异值学习 (arXiv:2601.07687v4 2026-08) 进一步：标准 RMT 假设平稳+有界谱，
  #   真实收益违反此假设（依赖漂移+宏观共同模），Phase 2+ 用神经网络估计器替代解析收缩。
  #
  # 本检查聚焦声明完整性（不重做 RMT 计算——去噪属因子组合层职责）：
  #   factor_registry 的 redundancy_status=independent/redundant 的 entry 是否声明 rmt_denoised
  if registry_id == "REG-FCT-001":  # factor_registry
    for entry in entries:
      redundancy = entry.get("redundancy_status")
      if redundancy in {"independent", "redundant", "orthogonal"}:
        rmt = entry.get("rmt_denoised")
        if rmt is None:
          warnings.append("声明 redundancy_status 的因子缺 rmt_denoised: " + entry.id +
                          "（arXiv:2507.17211v2 EFS: 因子相关性矩阵含 Marchenko-Pastur 噪声特征值，" +
                          "未去噪的伪相关被误判为冗余。q=N_factors/T_obs>0.1 时 MUST 去噪。" +
                          "MVP 可填 {applicable: false, reason: 'low_factor_count'}，" +
                          "Phase 1.5+ 因子数>20 时 MUST 启用 RMT clipping 去噪）")

  return audit_report
```

**审计方法论教训**（project_memory）：文档-代码漂移检测 MUST 用 Select-String 核对实码符号，不能仅凭上一版审计快照（40 号 v2.6.0 教训：5 项 gap 实现于 v2.5.0 之后但文档未回填）。本算法 E5/E6 强制实码核对。

### 4.8 生命周期管理流程（10 阶段 + 衰减检测，v1.2.0 新增）

对标 2026 Strategy Lifecycle Management 主流 10 阶段模型（[Linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/) ｜ [DeepTradeX 2026](https://deeptradex.zendesk.com/hc/en-us/articles/16820285969295-Strategy-Lifecycle-Management-Great-Trading-Strategies-Are-Managed-Not-Just-Built)），比传统 5-6 阶段更精细，新增 Decay Detection 和 Decommissioning 独立阶段。strategy_registry 的 `lifecycle_status` 7 态映射此 10 阶段：

| # | 10 阶段（2026 主流） | lifecycle_status 映射 | 关键活动 | 衰减检测要点 |
|---|---|---|---|---|
| 1 | Idea Generation | candidate | 信号发现 vs 信号幻觉（经济理性/行为解释/跨市场合理性） | — |
| 2 | Strategy Design | candidate | 入场/出场/仓位/风险规则转译为可测规则 | — |
| 3 | Backtesting | backtest | 历史数据评估 + 参数稳健性（非精度）+ 跨 regime 多样性 | — |
| 4 | Validation | backtest→sim | OOS + walk-forward + 试图证伪（非证明有效）+ 交易成本整合 | — |
| 5 | Pre-Deployment | sim→paper | 滑点/延迟/流动性/执行建模/资金规模测试（reality filter） | — |
| 6 | Deployment | paper→live | 渐进部署（减仓+监控窗+基准对比），deployment=probation 非 confirmation | reality gap 监控（回测≠实盘） |
| 7 | Scaling | live | 流动性/容量/换手/市场结构相关性的非线性压力 | 市场冲击增加、alpha 压缩 |
| 8 | Maturity | live→monitoring | 稳定收益+已知风险+集成资金配置（最欺骗阶段：crowding 暗中积聚） | rolling Sharpe 退化、回撤频率增加 |
| 9 | **Decay Detection** | monitoring→decayed | **Alexander & Fabozzi 2026 MRP**（Minimum Regime Performance）跨 regime 持久性 + 相关性失稳 + 执行成本漂移 | 早期恶化检测（非崩溃检测）→ 受控去风险 |
| 10 | **Decommissioning** | decayed→retired | 退役非"亏钱时"而是"失去统计有效性时"：性能低于阈值/风险调整恶化/结构断裂。资金重分配，情绪移除 | 文档化 lessons learned |

**衰减检测算法**（对标 Alexander & Fabozzi 2026 MRP + Vibe-Trading 2026-07 DecayEvaluator）：

```
算法 DECAY_SCAN(strategy_id):
  # Vibe-Trading 衰减状态机: created → benching → active → monitoring → decayed → disabled
  # 恢复条件: IC ratio > 0.7

  state = strategy.lifecycle_state
  recent_ic = compute_ic(strategy_id, window=recent_60d)
  baseline_ic = compute_ic(strategy_id, window=benchmark_period)

  # MRP: Minimum Regime Performance (Alexander & Fabozzi 2026)
  regime_perfs = compute_perf_per_regime(strategy_id, regimes=current_regimes)
  mrp = min(regime_perfs)  # 跨 regime 最低表现

  ic_ratio = recent_ic / baseline_ic if baseline_ic != 0 else 0

  if state == "monitoring":
    if ic_ratio < 0.7 or mrp < decay_threshold:
      transition(strategy_id, "decayed")
      alert("衰减确认: " + strategy_id + " ic_ratio=" + ic_ratio)
    elif ic_ratio > 0.85 and mrp > stable_threshold:
      transition(strategy_id, "active")  # 恢复
  elif state == "decayed":
    if ic_ratio > 0.7:  # Vibe-Trading 恢复条件
      transition(strategy_id, "monitoring")
    elif sustained_underperformance(strategy_id, period="2y"):
      transition(strategy_id, "retired")  # Decommissioning
```

**多检测器集成（v1.3.0 新增，对标 2026-02 mathandmarkets + quantt.ca）**：上述 DECAY_SCAN 基础版用 IC ratio + MRP 单一指标。2026 年 2 月 [mathandmarkets](https://mathandmarkets.com/p/detecting-decay-in-real-time-when) 与 [quantt.ca](https://quantt.ca/papers/Intraday%20Volatility.pdf) 研究明确："没有单一测试完美解决衰减检测，需组合"。`decay_detection_method` 字段（§6.1.2 strategy schema）支持以下方法，推荐**2/3 投票机制**（quantt.ca 2026-02：三检测器独立判断 + 多数表决，消除单检测器偏差）：

```
算法 DECAY_SCAN_MULTI(strategy_id):
  # 三检测器集成（v1.3.0，对标 quantt.ca 2026-02 2/3 voting）
  # 每检测器独立返回 alarm=True/False，2/3 命中触发 decayed 转换

  returns = get_daily_returns(strategy_id, window=recent_250d)

  # 检测器 1: CUSUM（workhorse，对标 mathandmarkets 2026-02）
  #   S⁺ₜ = max(0, S⁺ₜ₋₁ + (μ₀ - xₜ) - k)，k=0.5σ，alarm when S⁺ₜ > h=4σ
  #   优势：小偏移累积敏感，~50天检测延迟；μ₀ 用 OOS walkforward 期均值
  s_cusum = 0; k = 0.5 * std(returns); h = 4 * std(returns)
  for xₜ in returns[-60:]:  # 近 60 交易日
    s_cusum = max(0, s_cusum + (mu0 - xₜ) - k)
    if s_cusum > h: cusum_alarm = True; break

  # 检测器 2: Page-Hinkley（对突变敏感，CUSUM 变体）
  #   Uₜ = Σᵢ(xᵢ - mₜ - δ)，PHₜ = max(U)，δ=0.01*std，alarm when Uₜ - min(U) > threshold
  #   优势：快速反应剧烈衰减（如政策突变导致 alpha 断崖）
  running_mean = cumulative_mean(returns)
  U = cumulative_sum(returns - running_mean - 0.01*std(returns))
  if (U[-1] - min(U)) > ph_threshold: ph_alarm = True

  # 检测器 3: BOCPE/BOCPD（Bayesian Online Change Point Detection，v1.10.0 增强）
  #   Adams & MacKay 2007 算法——维护 run length（距上次变点的时间长度）的概率分布
  #   非二元检测：估计"每个时间点发生变点的概率"（continuous），非"是否发生变点"（binary）
  #   双重更新：① growth probability（当前 regime 延续）+ ② changepoint probability（新 regime 开始）
  #   优势：① 显式建模不确定性，输出概率非二元；② 同时检测 mean + variance 漂移（CUSUM 仅 mean）；
  #         ③ 不需预设 μ₀ 基线（CUSUM 的关键局限）；④ 输出 run length 分布可估计变点位置
  #   弱点：计算成本高 O(N²)（run length 0..N 全维护），需先验 hazard rate；
  #         重尾数据需 Student-t likelihood（非高斯，否则与 CUSUM 同病）
  #   对标：mathandmarkets 2026-02 Part 81 Test 3 + arXiv:2307.02375 Tsaknaki-Lillo-Mazzarisi
  #         （BOCPD 检测 order flow regime shifts，NASDAQ 实证，score-driven 变体处理时序相关）
  #         + Tugbars/BOCPD-Ultra（生产级 C 实现，~0.19µs latency，AVX2 优化，Normal-Gamma 共轭）
  #   A 股适用性：Student-t likelihood 处理重尾（γ₄>6），hazard_rate=1/250（年均 1 次变点先验）
  bocpe_prob = bocpd_adams_mackay(returns, hazard_rate=1/250,
                                   likelihood="student_t",  # 重尾鲁棒（v1.6.0 GSA-LLR 同理）
                                   max_runlength=250)
  if bocpe_prob > 0.5: bocpe_alarm = True

  # 2/3 投票（quantt.ca 2026-02 模式）
  votes = [cusum_alarm, ph_alarm, bocpe_alarm]
  if sum(votes) >= 2:
    transition(strategy_id, "decayed")
    alert("衰减确认(2/3投票): " + strategy_id + " votes=" + votes)

    # 步骤 5：变点归因（v1.27.0 新增，对标 ARM arXiv:2608.01691v1 2026-08-03）
    #   检测到变点后 MUST 归因到具体因子坐标，而非全量降权
    #   ARM（Attribution by Rank Maxima）用 max-over-splits rank statistic 评分每个坐标
    #   3 个有限样本保证：per-coordinate validity + FWER control（Westfall-Young 置换）+ FDR control（e-BH）
    #   标准做法（在估计变点 τ̂ 处做 per-coordinate 两样本检验）无效——FWER>0.66
    #   归因结果写入 decay_detection_method 字段（格式 {detector: "cusum_ph_bocpe", attribution: "arm"}）
    #   Phase 2+ 因子数>20 时 MUST 启用（精准降权，减少误杀有效因子）
    if factor_count > 20:  # Phase 2+ 启用条件
      attributed_factors = arm_attribution(returns_matrix, changepoint=estimated_cp)
      for factor_id, attribution_score in attributed_factors:
        if attribution_score > arm_threshold:
          downweight(factor_id, ratio=attribution_score)  # 精准降权非全量降权
  elif sum(votes) == 1:
    transition(strategy_id, "monitoring")  # 单检测器告警=预警，降级监控
```

**各检测器权衡**（mathandmarkets 2026-02）：

| 检测器 | 擅长 | 弱点 | 参数 | 个人项目适用性 |
|---|---|---|---|---|
| CUSUM | 渐变漂移（crowding 慢腐蚀） | 需指定 μ₀ 基线（OOS 期均值） | k=0.5σ, h=4σ | ✅ MVP 首选（workhorse） |
| Page-Hinkley | 突变（政策/黑天鹅导致 alpha 断崖） | 对噪声敏感，误报率高 | δ=0.01σ, threshold 经验值 | ✅ 补充（CUSUM 盲区） |
| BOCPE | 概率输出，不确定性量化 | 计算成本高，需先验 | hazard_rate=1/250 | ⚠️ Phase 1.5+（MVP 可选） |
| MRP（基础版） | 跨 regime 持久性 | 需 regime 分类器 | decay_threshold | ✅ 已在基础 DECAY_SCAN |
| IC ratio（基础版） | 简单直观 | 滞后，单指标 | 0.7 阈值 | ✅ 已在基础 DECAY_SCAN |
| profit_factor（v1.4.0 新增） | 基于 trades 的盈亏比稳定性 | 需 trade 级数据（非 returns 序列） | 回测 PF 70% 阈值，30 consecutive trades | ✅ MVP 补充（[PineForge 2026-05](https://getpineforge.com/blog/detect-strategy-decay-trading-bot)） |
| z_score（v1.4.0 新增） | 实盘 returns vs 回测分布的 Z 偏移 | 需回测分布基准 | rolling avg Z < -1.65（5% 显著） | ✅ MVP 补充（PineForge 2026-05） |

**检测器维度互补说明**（v1.4.0 新增）：CUSUM/PH/BOCPE 三检测器都基于 **returns 序列**（日收益时间序列），是"收益维度"检测。profit_factor 基于 **trades 序列**（单笔盈亏比），z_score 基于 **分布偏移**（实盘 vs 回测分布距离），两者是不同维度的检测器。多检测器集成不限于 returns 维度内组合，跨维度组合（returns + trades + distribution）覆盖更全面。`decay_detection_method` enum（§6.1.2 strategy schema）扩展为：`rolling_ic`/`mrp`/`cusum`/`cusum_ph_bocpe`/`profit_factor`/`z_score`/`none`。MVP 推荐组合：`profit_factor` + `z_score`（PineForge 实用派，计算简单无需 μ₀ 基线）；Phase 1.5+ 升级 `cusum_ph_bocpe`（mathandmarkets 严谨派，检测延迟更短）。

**A 股收益分布重尾性与鲁棒 CUSUM（v1.6.0 新增，对标 [arXiv:2605.23419 GSA-LLR 2026-05-22](https://arxiv.org/abs/2605.23419) + [robcp R 包 2026-01](https://www.stats.bris.ac.uk/R/web/packages/robcp/) + [AIMS Mathematics 2026-05](https://aimspress.com/article/doi/10.3934/math.2026542)）**：上述 CUSUM/PH 检测器均基于**高斯假设**（仅用前两阶矩 mean/variance），但 **A 股日收益分布是尖峰重尾的**（excess kurtosis γ₄ > 6，涨跌停板制度加剧尾部聚集）。[arXiv:2605.23419](https://arxiv.org/abs/2605.23419) 实证：经典高斯 CUSUM 在重尾数据（γ₄>20）上产生 **100% 误报**——"small relative change-point" regime 下信号能量变化不大但分布形状（偏度/峰度）变化显著，线性 CUSUM 丢弃高阶统计量而失效。该论文提出 **GSA-LLR**（Generalized Stochastic Approximation of Log-Likelihood Ratio）：用广义随机基（多项式/对数/分数幂）近似 LLR，利用 up to 3s 阶矩，Kunchenko 概率误差界（KU-PE）控制误报率无需经验调参。**基选择规则**（按 excess kurtosis γ₄ 自动选择）：
- 多项式基 `{x^i}`：γ₄ < 6（准高斯，快速衰减尾）
- **分数幂基 `{sgn(x)|x|^α}`：6 ≤ γ₄ < 20（中度重尾，**A 股日收益落此区间**，数值稳定性优于多项式）
- 对数基 `{x, ln|x|, x·ln|x|}`：γ₄ ≥ 20（重尾如 Pareto/log-normal）

**对 Phase 1.5+ 升级路径的影响**：Phase 1.5+ 升级到 `cusum_ph_bocpe` 时，CUSUM 分量**不应**直接用经典高斯 CUSUM，而应考虑鲁棒变体：① GSA-LLR CUSUM（arXiv:2605.23419，分数幂基，A 股适用）；② Huberized CUSUM（[robcp R 包 2026-01](https://www.stats.bris.ac.uk/R/web/packages/robcp/)，Huber M-estimator 降权极端值，重尾鲁棒）；③ coordinatewise truncated CUSUM + block self-normalization（[AIMS Mathematics 2026-05](https://aimspress.com/article/doi/10.3934/math.2026542)，β-mixing 依赖下有限样本保证）。MVP 阶段用 `profit_factor`/`z_score` 不受此问题影响（非 returns 序列检测器），这也是 MVP 选择它们的额外理由——**绕过 A 股重尾分布对 CUSUM 的适用性挑战**。

> 🎯 **2026 衰减检测最佳实践（v1.3.0 新增，v1.4.0 补充跨维度检测器）**：[mathandmarkets 2026-02-22](https://mathandmarkets.com/p/detecting-decay-in-real-time-when) 系统对比 CUSUM / Page-Hinkley / Bayesian / rolling Sharpe 四测试，结论"no single test solves this perfectly, every approach trades off detection speed against false alarm rate"。[quantt.ca 2026-02](https://quantt.ca/papers/Intraday%20Volatility.pdf) 论文实证三检测器集成 + 2/3 投票优于任何单一检测器。[algotrading.space 2026-04](https://www.algotrading.space/blog/market-regime-detection-indicators) 补充 KS test（分布形状）+ Wasserstein distance（分布移动幅度）作为分布族检测器。[Tugbars Finance-Kill-Switch](https://github.com/Tugbars/Finance-Kill-Switch) 开源库集成 Hawkes（级联）+ Lee-Mykland（跳跃）+ CUSUM（漂移）三检测器用于 Kill Switch 场景——本项目 risk_limit_registry 的 kill_switch 限额可参考此组合。[PineForge 2026-05-18](https://getpineforge.com/blog/detect-strategy-decay-trading-bot) 补充实用派三指标：rolling profit factor（回测 PF 70% 阈值）、z-score（实盘 vs 回测分布）、live drawdown > 1.2x backtest max_dd——计算简单，无需 μ₀ 基线，适合 MVP 阶段检测器起步。
>
> **个人项目 MVP 决策**（v1.4.0 更新，v1.6.0 补 A 股重尾分布考量）：MVP 阶段用 `profit_factor` + `z_score`（PineForge 实用派，计算简单无需 μ₀ 基线，trade 级 + 分布级双维度，**且绕过 A 股重尾分布对经典高斯 CUSUM 的适用性挑战**——见上文"鲁棒 CUSUM"段）；Phase 1.5+ 实盘 6-12 月数据积累后升级到 `cusum_ph_bocpe`（mathandmarkets 严谨派，returns 级三检测器 2/3 投票，检测延迟更短），**但 CUSUM 分量须用鲁棒变体**（GSA-LLR 分数幂基 / Huberized / truncated+self-normalized，非经典高斯 CUSUM，因 A 股收益 γ₄>6 重尾）。`decay_detection_method` 字段 MVP 填 `profit_factor`/`z_score`，Phase 1.5+ 填 `cusum`/`cusum_ph_bocpe`（注：Phase 1.5+ 实施时需先测 A 股收益 excess kurtosis 实际值，按基选择规则选 GSA-LLR 基函数）。schema 已预留无需改动。检测到衰减后走 §4.12 ADAPT_STRATEGY（适应）→ §4.10 RETIRE_ENTRY（退役）完整三环节流程。

**经验数据**（[Maven Securities](https://breakingalpha.io/insights/alpha-decay-detection-purchased-trading-strategies)）：alpha 衰减年均 US 5.6% / EU 9.9%；68% 策略 18-24 月需修改/退役。个人项目据此设定 `decay_threshold` 初值：ic_ratio < 0.7 触发 decayed，sustained 2 年低于阈值触发 retired。

**参数漂移 vs 正常回撤识别困境**（v1.10.0 新增，对标 [eastmoney 2026-07-18 构建可进化的交易系统（十一）](https://caifuhao.eastmoney.com/news/20260718161836142430820) + [CSDN 2026-08-09 Alpha Decay：策略失灵是宿命](https://blog.csdn.net/2601_95872481/article/details/162839541)）：A股中文源对衰减检测的核心洞察——系统"不是在瞬间崩溃的，而是在不知不觉中腐烂"。**参数漂移**指策略依赖的市场特征本身（流动性分布/参与者组成/信息传递速度/制度安排）在时间推移中发生缓慢持久变化，而非价格方向或波动率突变。关键困境："策略逻辑所锚定的世界，在策略还沿着旧地图行进时，已经慢慢移动到了别处"——每一笔亏损都可被解释为正常回撤，每一段低迷都可归因于市场暂时不对路，直到监控数据终于显示明确异常时市场结构已变。**识别两难**：胜率 40% 趋势策略连续亏损 5-6 笔在统计上正常，延长到 8-10 笔在足够长历史里也曾出现——当参数漂移已发生但未确认时，这些亏损到底"属于正常分布尾部，还是结构性变化前兆？两者在发生时几乎无法区分"。统计检验需积累足够样本，而中长线策略积累样本所需时间往往足够参数漂移完成破坏性工作。

**CSDN 2026-08-09 A 股特色补充**（v1.10.0 新增，最新中文源）：该文从 A 股视角系统阐述"策略失灵不是 bug，是宿命"——① **四大根因**：市场自适应（人学习/模仿/反向）+ 市场结构变化（散户→机构/T+1→T+0 ETF/注册制/量化 30%+/北向万亿/退市严格执行）+ 行情风格切换（价值 vs 成长/大盘 vs 小盘）+ 过拟合；② **AI 不是解药**："AI 学的是历史模式，依然受限于过去不代表未来；AI 训练数据里如果有过拟合，结果只会更隐蔽地过拟合；AI 学到的规律如果被大家用，一样会被市场套利掉"——这印证了本项目 §6.2.4 chart_pattern 的"Simplicity Wins"原则（简单模型优于复杂模型）和 §7.2 honest-backtest Layer 7 对抗验证的必要性；③ **StrategyLifecycle 架构模式**（该文提出的数据类设计）：`rolling_monitor`（滚动表现监控→连续差自动降权/下线）+ `multi_strategy`（多策略并行，无"皇冠策略"，任一失灵不瘫痪系统）+ `candidate_pipeline`（持续新策略候选池，定期晋级）+ `regime_switch`（内置风格切换识别）+ 显式暂停规则（`pause_if_underperform_months`: 连续 N 月跑输基准→暂停 / `pause_if_drawdown_breach`: 回撤超历史最大→暂停 / `alert_if_ic_drops`: IC 大幅下降→警报）；④ **核心原则**："系统健康不在于任何时候都赚，而在于失灵了能识别、能切换、能恢复"。**对本项目 §4.8 DECAY_SCAN 的启示**：① 参数漂移是 decay_cause=regime 的子类（市场结构慢变化），§4.12 ADAPT_STRATEGY Step1.5 的 regime→refit 决策适用，但 refit 前须确认新 regime 已稳定 ≥60 天（Step1.5 已含此约束）；② 参数漂移的"不知不觉"特性印证了 §4.8 多检测器集成的必要性——单一 rolling Sharpe 滞后（等明确异常时结构已变），CUSUM 小偏移累积敏感（~50 天检测延迟）更适合捕获慢漂移；③ CSDN 的 `pause_if_underperform_months`/`pause_if_drawdown_breach`/`alert_if_ic_drops` 三暂停规则映射到本项目的 §4.12 ADAPT_STRATEGY Level 2（减仓）+ §4.14 ROLLBACK_ENTRY 触发条件——`pause_if_drawdown_breach` = ROLLBACK_ENTRY 触发源 ② drawdown_breach，`alert_if_ic_drops` = DECAY_SCAN ic_ratio<0.7 预警；④ A 股特色：涨跌停制度/T+1/游资接力结构使参与者组成变化比成熟市场更剧烈，参数漂移速度可能快于 Maven Securities 的 US/EU 经验数据，`decay_scan_frequency` 建议 active/live 态 monthly 而非 quarterly。

**v1.5.0 经验数据补充**（[smartfinancedata 2026](https://www.smartfinancedata.com/is-your-trading-edge-fading-signs-of-historical-edge-decay/) 127 策略追踪 + [Pomegra 2026](https://pomegra.io/learn/library/track-e-trading-risk/active-trading/chapter-04-trading-edges/edge-decay-and-adaptation)）：

| 统计维度 | smartfinancedata 2026（127 策略） | Pomegra 2026（零售市场） | 个人项目校准 |
|---|---|---|---|
| 1 年内失败率 | **67%**（85/127） | — | MVP 阶段单策略预期 12 月内可能衰减 |
| 18 月内失败率 | **83%** | — | decay_threshold 检测窗口 ≤ 18 月 |
| 中位半衰期 | **11.2 月**（performance 50% 衰减） | 2-5 年（零售 IDX） | A 股个人系统介于两者间，按 12-18 月预期 |
| 3 年仍盈利 | **8%**（10/127） | — | 长期存活策略是例外非默认 |
| 正常年度衰减 | — | 2-5%（win rate） | <10% 视为噪声波动 |
| 有意义衰减 | — | 10-15% | 触发 §4.12 ADAPT_STRATEGY Level 2 |
| 严重衰减 | — | 25%+ 或负 expectancy | 触发 Level 3 refit 或 Level 5 退役 |
| 监控频率 | — | **monthly/quarterly** | `last_decay_scan_at` 检查周期 ≤ 30 天 |

**衰减原因分类（Five Horsemen of Edge Decay，v1.5.0 新增，对标 [smartfinancedata 2026](https://www.smartfinancedata.com/is-your-trading-edge-fading-signs-of-historical-edge-decay/)）**：检测到衰减后，**先分类原因再决定 refit 还是退役**——不同原因对适应响应的成败有决定性影响。127 策略失败原因分布：

| # | 衰减原因 | 占比 | 适应有效性 | 决策建议 |
|---|---|---|---|---|
| 1 | **Crowding**（竞争发现/羊群涌入） | 41% | ❌ refit 无效（结构性消除，非参数漂移） | Level 5 退役（或切换到未被拥挤的 variant） |
| 2 | **Regime Change**（市场结构变化） | 28% | ✅ refit 可能有效（新 regime 下重新拟合参数） | Level 3 refit（若新 regime 稳定） |
| 3 | **Overfitting**（原策略本就 curve-fitted） | 18% | ❌ refit 无效（refit=再过拟合） | Level 5 退役（PBO/DSR 复检确认） |
| 4 | **Technology Evolution**（执行速度/价差压缩） | 9% | ❌ refit 无效（基础设施层变化） | Level 5 退役（或降级到更长 holding_period） |
| 5 | **Depletion**（不效率耗尽，如套利空间消失） | 4% | ⚠️ refit 部分有效（寻找新 variant） | Level 3 refit 失败则 Level 5 |

**分类对算法的影响**（v1.5.0 关键补充）：§4.12 ADAPT_STRATEGY Step 1 原仅用 severity（warning/critical）分级，v1.5.0 新增 **Step 1.5 衰减原因分类驱动决策**——先诊断 decay_cause（crowding/regime/overfitting/tech/depletion），再决定 refit 还是退役。**Rule**：decay_cause ∈ {crowding, overfitting, tech} → 跳过 Level 3 refit 直接 Level 5 退役（refit 无效或有害）；decay_cause ∈ {regime, depletion} → 走 Level 3 refit（可能有效）。strategy schema 新增 `decay_cause` 字段（§6.1.2 v1.5.0）。

**监控频率指导**（v1.5.0 新增，对标 [Pomegra 2026](https://pomegra.io/learn/library/track-e-trading-risk/active-trading/chapter-04-trading-edges/edge-decay-and-adaptation) + [LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/)）：`last_decay_scan_at` 检查周期建议——active/live 态 **monthly**（月度扫描），monitoring 态 **weekly**（预警后加密），decayed 态 **daily**（退役决策前密集监控）。`decay_scan_frequency` 字段补入 strategy schema（§6.1.2 v1.5.0）。LuxAlgo 2026-08-03 强调"30-50 trades early diagnostic, 100+ trades confirmation"——高频策略用 trade-count 窗口，低频策略用 3-6 月 calendar 窗口。

### 4.9 变更管理算法（EVOLVE_ENTRY，v1.3.0 新增）

CONSTRUCT_REGISTRY（§4.5）解决"新建注册表"，但 entry 建成后**修改**是更高频操作——参数调整、状态变更、code_path 迁移、schema 字段补全都触发变更。**v1.2.x 缺变更管理算法**，导致 entry 修改无标准流程，易漏版本快照/漏通知依赖方/漏审计。

```
算法 EVOLVE_ENTRY(registry_id, entry_id, change_set, change_type):
  输入: entry_id, change_set{field: new_value}, change_type{metadata|schema_sig|code_ref|status}
  输出: 版本快照（若需）+ 依赖方通知 + 审计日志

  entry = load_entry(registry_id, entry_id)
  old_version = entry.version

  Step 1【变更分类】（决定是否触发版本快照）
    # 对标 Feast Feature View Versioning（§4 原则 9）
    if change_type == "metadata":
      # description/tags/TTL/owner 等元数据变更 → 原地更新，不建版本
      is_version_significant = False
    elif change_type == "schema_sig":
      # formula/params/inputs/outputs/factor_class 等 schema-significant 变更 → 版本快照
      is_version_significant = True
    elif change_type == "code_ref":
      # code_path/module_id 变更 → 版本快照（实现迁移影响复现性）
      is_version_significant = True
    elif change_type == "status":
      # status 转换（candidate→active→deprecated→retired）
      # candidate/experimental→active → 见 §4.13 PROMOTE_ENTRY（v1.8.0 新增 8 门禁，v1.20.0 扩为 9 门禁含 G9 容量检验）
      # active→deprecated→retired → 见 §4.10 RETIRE_ENTRY
      if new_status in {"active", "live"}:
        delegate to PROMOTE_ENTRY(§4.13)
      elif new_status in {"deprecated", "retired"}:
        delegate to RETIRE_ENTRY(§4.10)
      return

  Step 2【版本快照】（若 schema-significant）
    if is_version_significant:
      # git 即天然版本历史（YAML 阶段），DB 阶段用 version_pin 回滚（§11）
      entry.version = bump_version(old_version)  # v1→v2
      # 记录 changelog：old_value → new_value，变更原因，变更人/agent
      entry.changelog.append({date, old_version, new_version, reason, change_set})

  Step 3【应用变更】
    for field, new_value in change_set:
      entry[field] = new_value
    entry.updated_at = today

  Step 4【依赖方影响分析】（按 §4.6 交叉引用矩阵反向查找）
    dependents = find_reverse_refs(registry_id, entry_id)
    # 如 factor 修改 → 查 belongs_to_strategies 的所有 strategy
    # 如 cost_model 修改 → 查 used_by_strategies 的所有 strategy
    for dep in dependents:
      notify(dep.owner, "依赖项变更: " + entry_id + " → " + dep.id +
             " 影响字段: " + affected_fields)

  Step 5【一致性审计】（调用 §4.7 AUDIT_REGISTRY 的 E4/E5/E8）
    audit = AUDIT_REGISTRY(registry_id)
    if audit.errors: halt and report  # 变更引入 dangling FK 或循环引用

  Step 6【治理同步】
    # 若 entry_count 不变则无需改 registry_of_registries
    # 若涉及 status 变更走 §4.10
    git commit("EVOLVE " + entry_id + " v" + old_version + "→v" + entry.version)
```

**变更分类清单**（对标 Feast 2026-03-31 + Confluent Schema Registry 兼容性模式）：

| 变更类型 | 示例 | 触发版本快照 | 通知依赖方 |
|---|---|---|---|
| metadata | description/tags/TTL/owner 更新 | ❌ 原地 | ❌ |
| schema_sig | formula/params/inputs/outputs/class 变更 | ✅ v→v+1 | ✅ |
| code_ref | code_path/module_id 迁移 | ✅ v→v+1 | ✅ |
| status | candidate→active / active→deprecated | 走 §4.10 | ✅ |
| additive | 新增可选字段（如补 benchmark_id） | ❌ 原地（向后兼容） | ❌ 可选 |
| breaking | 删除/重命名必填字段、改类型 | ✅ v→v+1 + 走 §4.11 演进 | ✅ 必须 |

### 4.10 退役算法（RETIRE_ENTRY，v1.3.0 新增）

entry 退役是状态机的关键转换，**v1.2.x 缺退役流程算法**。对标 [theFactory Schema Registry 2026-07](https://github.com/kherrera6219/theFactory/blob/main/docs/SCHEMA_REGISTRY_AND_VERSIONING.md) 的 Deprecation & Retirement 规则（90天宽限，最少30天），以及 §4.8 生命周期第10阶段 Decommissioning。

```
算法 RETIRE_ENTRY(registry_id, entry_id, reason):
  输入: entry_id, reason{decay/performance_obsolete/replaced_by/structural_break}
  输出: status: active→deprecated→retired 转换 + 宽限期 + 依赖方迁移

  entry = load_entry(registry_id, entry_id)

  # 阶段 1: active → deprecated（标记退役宽限期开始）
  if entry.status == "active":
    entry.status = "deprecated"
    entry.deprecated_at = today
    entry.deprecation_reason = reason
    entry.retire_after = today + 90 days  # theFactory 标准：90天宽限，最少30天

    # 依赖方预警 + 级联响应定义（v1.7.0 增强，对标 Apicurio Registry 生命周期最佳实践）
    # 原v1.3.0仅alert通知，未定义依赖方应做什么→级联响应缺口
    dependents = find_reverse_refs(registry_id, entry_id)
    for dep in dependents:
      alert(dep.owner, entry_id + " 已 deprecated，宽限至 " + entry.retire_after +
            " 请迁移至替代项或移除引用")
      # 级联响应（按依赖方类型分派）：
      if dep.registry_id == "REG-STR-001":  # strategy 依赖 factor/cost_model/benchmark
        # 策略依赖因子退役 → 标记需人工审查，不自动退役（策略可能有多因子冗余）
        dep.review_required = True
        dep.review_reason = "依赖项 " + entry_id + " deprecated"
        if entry.replaced_by:  # 有替代项 → 建议迁移
          notify(dep.owner, "建议迁移 " + entry_id + " → " + entry.replaced_by +
                 " 后走 §4.9 EVOLVE_ENTRY schema_sig 变更")
        else:  # 无替代项 → 策略可能需退役或重构
          notify(dep.owner, "无替代项，评估策略是否走 §4.10 RETIRE_ENTRY 或 §4.12 ADAPT_STRATEGY")
      elif dep.registry_id == "REG-FCT-001":  # factor 依赖 technical_indicator/chart_pattern
        # 因子依赖底层指标退役 → 因子自动进入 review（指标不可用则因子失效）
        dep.review_required = True
        if entry.replaced_by:
          notify(dep.owner, "迁移指标引用 " + entry_id + " → " + entry.replaced_by)
      # 审计日志：级联响应记录
      audit_log.append({date, event: "cascade_alert", source: entry_id, target: dep.id, response: dep.review_required})
    return

  # 阶段 2: deprecated → retired（宽限期结束 + 无活跃引用）
  if entry.status == "deprecated":
    if today < entry.retire_after:
      halt("宽限期未满: " + entry.retire_after)
    active_refs = find_active_reverse_refs(registry_id, entry_id)
    if active_refs:  # 仍有活跃引用
      halt("仍有活跃依赖: " + active_refs + " 不可退役")
    entry.status = "retired"
    entry.retired_at = today
    # retired 不删除 entry（审计可追溯），仅标记不可用
    # strategy 的 retired_date 字段同步（§6.1.2 schema）

  # 阶段 3: retired → 物理删除（极少，需 ARCH 审批）
  if entry.status == "retired" and request_physical_delete:
    if today - entry.retired_at < 365 days:
      halt("退役未满1年，不可物理删除")
    require ARCH approval
    delete entry  # 极端情况，默认保留 retired 记录
```

**退役触发条件**（对标 §4.8 第9-10阶段 + Maven Securities 经验数据）：
- `decay`：DECAY_SCAN 确认衰减，IC ratio < 0.7 持续 2 年（sustained_underperformance）
- `performance_obsolete`：Sharpe 低于阈值 / max_drawdown 超限 / 风险调整收益恶化
- `replaced_by`：被 variant 或新策略替代（variant_of 指向新 parent）
- `structural_break`：市场结构断裂（如 A 股新规使策略前提失效）

**退役宽限期规则**（theFactory 2026-07 标准）：
- 标准 90 天，最少 30 天
- 宽限期内 entry 标 deprecated 但仍可用（允许依赖方平滑迁移）
- 宽限期满 + 无活跃引用 → retired
- retired 记录保留（审计追溯），不物理删除（除非退役满1年 + ARCH 审批）

### 4.11 Schema 演进算法（EVOLVE_SCHEMA，v1.3.0 新增）

注册表 schema 本身会演进（如 v1.2.0 给 factor 补了 lookback_period/benchmark_id 字段）。**v1.2.x 缺 schema 演进算法**，导致 schema 变更时已有 entry 数据如何迁移无标准流程。对标 [Confluent Schema Registry](https://www.wickedsmartdata.com/articles/schema-evolution-strategies-for-production-data-pipelines-handling-breaking-changes-without-downtime) 的 BACKWARD/FORWARD/FULL 兼容性模式 + [Additive-Only / Expand-Contract](https://blog.datalakehouse.help/posts/2026-02-debp-schema-evolution/) 模式。

```
算法 EVOLVE_SCHEMA(registry_id, old_schema, new_schema):
  输入: old_schema{fields}, new_schema{fields}
  输出: 兼容性判定 + 迁移计划 + 已有 entry 数据迁移

  Step 1【变更分类】（breaking vs non-breaking）
    added = new_schema.fields - old_schema.fields          # 新增字段
    removed = old_schema.fields - new_schema.fields        # 删除字段
    modified = fields with type/constraint change          # 类型/约束变更
    renamed = detect rename patterns (old→new + similar)   # 重命名

    breaking = removed + modified + renamed + new_required_fields
    non_breaking = added_optional_fields + metadata_only

  Step 2【兼容性模式判定】（Confluent Schema Registry 标准）
    # BACKWARD: 新 schema 能读旧数据（新增字段有默认值）→ 安全部署
    # FORWARD: 旧 schema 能读新数据（删除字段消费者不依赖）→ 需协调
    # FULL: 双向兼容 → 最安全
    if non_breaking and not breaking:
      compatibility = "BACKWARD"  # 新增可选字段有默认值=向后兼容
    elif breaking:
      compatibility = "NONE"  # 需 Expand-Contract 模式协调

  Step 3【迁移策略选择】
    if compatibility == "BACKWARD":
      # Additive-Only 模式（datalakehouse 2026-02 推荐默认）
      # 只增不删/不重命名，新字段填默认值
      for entry in registry.entries:
        for field in added:
          entry[field] = new_schema[field].default  # 如 lookback_period 默认 20
      # schema_version bump（如 1.0→1.1），entry.version 不变（非 schema-significant）

    elif compatibility == "NONE":
      # Expand-Contract 模式（3阶段，datalakehouse 2026-02）
      # Phase Expand: 新增 v2 字段，保留 v1 字段，两者共存
      # Phase Migrate: 逐条迁移 entry 数据 v1→v2
      # Phase Contract: v1 字段全部迁移后删除 v1 字段
      # 期间 v1/v2 entry 共存，消费者按 version 字段选择解析逻辑

  Step 4【已有 entry 数据迁移】
    for entry in registry.entries:
      apply_migration(entry, old_schema, new_schema, migration_plan)
      # 迁移后审计：E10 必填字段检查（新 schema 的 required 字段都有值）
      audit = AUDIT_REGISTRY(registry_id)
      if audit.errors: halt and report

  Step 5【版本与治理同步】
    registry.schema_version = bump(old_schema_version)  # 1.0→1.1（兼容）/ 2.0（breaking）
    if breaking:
      registry_of_registries 更新 schema_version + 变更说明
      AGENTS.md 速查入口同步
    # breaking 变更登记 ARCH（architecture_issue_registry）
```

**兼容性模式清单**（Confluent Schema Registry + jsonic 2026-05 标准）：

| 模式 | 含义 | 适用场景 | 部署方式 |
|---|---|---|---|
| BACKWARD | 新 schema 能读旧数据 | 新增可选字段（有默认值） | 直接部署，无需协调 |
| FORWARD | 旧 schema 能读新数据 | 删除字段（消费者不依赖） | 需协调消费者 |
| FULL | 双向兼容 | 严格治理 | 最安全，限制最多 |
| NONE | 不兼容 | breaking 变更 | 需 Expand-Contract |

**Breaking vs Non-breaking 分类**（datalakehouse 2026-02 + jsonic 2026-05）：

| 变更 | Breaking? | 示例 |
|---|---|---|
| 新增可选字段（有默认值） | ❌ 否 | factor 补 lookback_period（默认20） |
| 放宽约束（INT→BIGINT） | ❌ 否 | capacity float→double |
| 加文档/metadata | ❌ 否 | description 更新 |
| 删除字段 | ✅ 是 | 删除 factor.legacy_code |
| 重命名字段 | ✅ 是 | user_id→customer_id |
| 改字段类型 | ✅ 是 | amount string→float |
| 新增必填字段 | ✅ 是 | 新增 region required |
| 收紧约束 | ✅ 是 | nullable→non-nullable |

> 🎯 **2026 Schema 演进最佳实践（v1.3.0 新增）**：[wickedsmartdata 2026-07](https://www.wickedsmartdata.com/articles/schema-evolution-strategies-for-production-data-pipelines-handling-breaking-changes-without-downtime) 系统阐述 Confluent Schema Registry 的 BACKWARD/FORWARD/FULL 兼容性模式 + Expand-Contract 模式。[datalakehouse 2026-02](https://blog.datalakehouse.help/posts/2026-02-debp-schema-evolution/) 强调"treat your schema like an API"——Additive-Only 是最简单可靠策略（只增不删，deprecated 列保留90天后删）。[theFactory 2026-07](https://github.com/kherrera6219/theFactory/blob/main/docs/SCHEMA_REGISTRY_AND_VERSIONING.md) 定义 v1→v1 原地（兼容）/ v1→v2 新文件（breaking）的语义版本约束。[jsonic 2026-05](https://jsonic.io/guides/json-schema-migration) 补充 Upcasters（永久运行，旧版本→新版本转换器）+ property-based testing（10K 随机 v1 payload 验证 upcaster <1秒）。
>
> **对本项目 12 注册表的启示**：v1.2.0 的 schema 增强（补 lookback_period/benchmark_id/warmup_period 等）全部是 **Additive-Only**（新增可选字段有默认值），属 BACKWARD 兼容，已安全应用无需迁移。未来若需 breaking 变更（如 factor_class 10 类重分类），走 Expand-Contract 3 阶段。schema_version 字段区分兼容（1.0→1.1）vs breaking（1.x→2.0）。YAML 阶段 git diff 天然提供 schema 变更历史，DB 阶段用 schema_version + entry.version 双版本追踪。
>
> **Schema 文件级版本管理补充**（v1.4.0 新增，对标 theFactory 2026-07-03）：theFactory 采用"文件名含主版本号"规则——`mission_charter.v1.json` → `mission_charter.v2.json`，v1→v1 原地（BACKWARD 兼容新增可选字段），v1→v2 新文件（breaking 变更：重命名/删除/改类型/新增必填）。这与 §4.11 的 schema_version bump 互补：**YAML 阶段**（当前）单文件 + schema_version 字段 + git diff 足够；**DB 阶段**（迁移后）若需严格治理，可升级为文件级版本管理——breaking 变更不原地改 v1，而新建 v2 schema 文件，v1/v2 共存期间消费者按 version 字段选择解析逻辑（Expand-Contract Phase Expand）。个人项目 MVP 用 schema_version 字段足够，文件级版本管理是 DB 阶段可选项。

> 🔗 **契约测试（Contract Testing）补充**（v1.10.0 新增，对标 [dataopsschool 2026-02-16 Schema Evolution](https://dataopsschool.com/blog/schema-evolution/) + [thedatagovernor 2026-05-16 Data Product Governance](https://thedatagovernor.com/data-product-management-governance/)）：dataopsschool 2026-02 明确区分 **Schema Evolution**（变更流程）vs **Contract Testing**（消费者期望验证）vs **Schema Registry**（存储）三个概念——EVOLVE_SCHEMA 算法覆盖第 1 个（变更流程）和第 3 个（YAML 即 registry），但**缺第 2 个契约测试**。契约测试 = consumer-driven contracts，验证 schema 变更不破坏消费者：消费者声明"我依赖 factor.momentum 的 inputs 字段"，schema 变更删除/改 inputs 时，契约测试自动 fail 阻断部署。thedatagovernor 2026-05 强化此原则："your schema is your API contract. Changes need to follow clear rules."（schema 即 API 契约，变更须遵循明确规则）。**对本项目的启示**：12 注册表的 FK 关系（§4.6 矩阵）本质就是隐式契约——factor.inputs → field_dictionary，strategy.alpha_sources → factor_registry。契约测试可映射为 §4.7 AUDIT_REGISTRY 的 E4（FK 引用完整性）+ §4.9 EVOLVE_ENTRY Step 4（依赖方影响分析）——schema 变更时自动检查所有反向引用方是否受影响。**MVP 阶段**：契约测试通过 E4 + Step4 隐式覆盖（YAML 阶段 grep 即契约验证），无需额外工具。**DB 阶段**：可升级为显式 consumer-driven contract tests（如 Pact 框架），每个消费者声明依赖字段，schema 变更触发 contract test suite 自动跑。这是 Schema Evolution 治理的第三层（变更流程 + 存储 + 契约验证）完整闭环。

### 4.12 衰减后适应算法（ADAPT_STRATEGY，v1.4.0 新增，v1.5.0 增强）

§4.8 DECAY_SCAN（检测衰减）+ §4.10 RETIRE_ENTRY（退役）构成「检测→退役」两环节，但**缺中间环节——检测到衰减后、退役前，如何尝试适应/修复策略**。直接退役过于激进：68% 策略 18-24 月需修改而非退役（Maven Securities 经验），适应成功可延长策略寿命。但适应本身有过拟合风险——**adaptation 和 overfitting 是同一数学操作，区别仅在跟踪真实偏移还是追逐噪声**（[mathandmarkets Part 82, 2026-02-24](https://mathandmarkets.com/p/can-a-strategy-evolve-the-math-of)）。

本算法对标 mathandmarkets Part 82 的 5 级响应等级 + refit window 最优化理论，填补施工环节流程算法缺口。**v1.5.0 增强**：对标 [LuxAlgo 2026-08-03 "Edge Decay: Reoptimize or throw out your strategy"](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/) 补充经验驱动的三选一决策矩阵（Reoptimize/Pause/Retire）+ 6 类 review triggers + baseline 保存要求；对标 [smartfinancedata 2026](https://www.smartfinancedata.com/is-your-trading-edge-fading-signs-of-historical-edge-decay/) 补衰减原因分类驱动决策（Five Horsemen，§4.8）。

```
算法 ADAPT_STRATEGY(strategy_id, decay_signal):
  输入: strategy_id, decay_signal{来源: cusum/ph/bocpe/ic_ratio/mrp/profit_factor/z_score,
                                   严重度: warning/critical, decay_cause: crowding/regime/overfitting/tech/depletion/unknown}
  输出: 适应决策（refit/调参/减仓/退役）+ OOS 验证 + version 快照（若参数变更）

  strategy = load_strategy(strategy_id)
  current_level = strategy.adaptation_level  # 1-5

  Step 0【baseline 完整性校验】（v1.5.0 新增，对标 LuxAlgo 2026-08-03）
    # LuxAlgo 2026-08-03: "Without that baseline, it is difficult to distinguish
    # normal variance from a genuine change in the edge"
    # baseline MUST 在策略 deployment（lifecycle_status: paper→live）时保存
    # §4.7 E12 审计检查此完整性，本 Step 0 运行时再校验
    baseline_required = {baseline_sharpe, baseline_expectancy, baseline_win_rate,
                         baseline_profit_factor, baseline_max_drawdown,
                         baseline_trade_frequency}
    missing = [f for f in baseline_required if strategy.get(f) is None]
    if missing:
      halt("baseline 不完整，缺字段: " + missing +
           "（衰减检测无法区分正常波动 vs 真实衰减，LuxAlgo 2026-08-03 要求）")
    # decay_threshold 必填（§4.8 DECAY_SCAN 恢复判定基准）
    if strategy.decay_threshold is None:
      strategy.decay_threshold = 0.7  # Vibe-Trading 默认值

  Step 1【响应分级】（mathandmarkets Part 82 五级响应）
    # Level 1: 静默监控（默认态，无操作）
    # Level 2: 减仓（decay_signal=warning，降低仓位 30-50% 控制下行）
    # Level 3: 季度 refit（参数漂移确认，下次定期窗口重新拟合）
    # Level 4: 在线学习（持续适应，高风险——需严格 OOS 验证）
    # Level 5: 退役（适应失败，走 §4.10 RETIRE_ENTRY）

    if decay_signal.严重度 == "warning" and current_level == 1:
      new_level = 2  # 减仓
    elif decay_signal.严重度 == "critical" and current_level <= 2:
      new_level = 3  # 触发 refit（待 Step 1.5 原因分类裁决）
    # Level 4 在线学习需 ARCH 审批（过拟合风险高），不自动升级

  Step 1.5【衰减原因分类驱动决策】（v1.5.0 新增，对标 smartfinancedata 2026 Five Horsemen）
    # §4.8 衰减原因分类表：crowding(41%)/regime(28%)/overfitting(18%)/tech(9%)/depletion(4%)
    # 不同原因对 refit 适应性有决定性影响——盲目 refit 可能无效或有害
    # decay_signal.decay_cause 由 §4.8 DECAY_SCAN 诊断或人工标注

    if decay_signal.decay_cause in {"crowding", "overfitting", "tech"}:
      # 这三类原因 refit 无效或有害：
      #   crowding = 结构性消除（羊群涌入），refit 改参数救不了结构性死亡
      #   overfitting = 原策略本就 curve-fitted，refit=再过拟合（PBO/DSR 复检确认）
      #   tech = 执行速度/价差压缩等基础设施层变化，参数层 refit 无效
      new_level = 5  # 跳过 Level 3 refit，直接退役
      strategy.decay_cause = decay_signal.decay_cause  # 记录原因供退役追溯
      RETIRE_ENTRY(strategy.registry, strategy.id,
                   reason="decay_cause=" + decay_signal.decay_cause)
      alert("衰减原因 " + decay_signal.decay_cause + " refit 无效，直接退役: " + strategy_id)
      return  # 不进入 Step 2-5 refit 流程

    elif decay_signal.decay_cause in {"regime", "depletion"}:
      # 这两类原因 refit 可能有效：
      #   regime = 新 regime 下重新拟合参数（若新 regime 稳定）
      #   depletion = 寻找新 variant（部分有效）
      strategy.decay_cause = decay_signal.decay_cause
      # regime 类需额外检查：新 regime 是否稳定（至少 60 天）才值得 refit
      if decay_signal.decay_cause == "regime":
        regime_stable_days = days_since_regime_change(strategy_id)
        if regime_stable_days < 60:
          halt("新 regime 未稳定（" + regime_stable_days + " < 60 天），refit 过早，维持 Level 2 减仓监控")
      # 仅 new_level==3（critical）才走 Step 2 refit；new_level==2（warning）维持减仓
      if new_level != 3:
        return  # warning 级别维持减仓监控，不 refit

    else:  # unknown 或未诊断
      # decay_cause 未诊断时，保守走 refit 流程（Step 2-5 的 OOS 验证会兜底）
      strategy.decay_cause = "unknown"
      if new_level != 3:
        return  # warning 级别维持减仓监控，不 refit


  Step 2【refit window 最优化】（Level 3 触发时，mathandmarkets Part 82）
    # 参数 μ 漂移率 δ/日，噪声 σ，最优 refit window:
    #   Bias² = (δ·w/2)²          ← 窗口越长偏差越大
    #   Variance = σ²/w           ← 窗口越长方差越小
    #   MSE = Bias² + Variance
    #   w* = (2σ²/δ²)^(1/3)       ← MSE 最小化
    # 实证：σ=1%/日, δ=0.01%/日 → w* ≈ 126 天（6月），印证"季度 refit"经验法则
    sigma = std(strategy.returns)
    delta = estimate_param_drift(strategy_id)  # 历史参数漂移率
    w_star = (2 * sigma**2 / delta**2) ** (1/3) if delta > 0 else 252
    # w* 上限 252（1年），下限 21（1月），避免极端值

  Step 3【refit 执行 + 过拟合防护】（对标 nexusfi 2026-06 + trendsandbreakouts 2026-05）
    # 3a. Walk-Forward 优化（purge/embargo 防泄漏）
    train_window = w_star; test_window = w_star / 4  # 1:4 train:test 比
    embargo = strategy.max_lookback  # 标签重叠窗口须 purge
    params_candidates = grid_search(strategy_id, train_window, embargo)

    # 3b. 参数稳定性区域检验（非"最优"参数）
    # nexusfi 2026-06: "needle peak = curve-fitting, plateau = robust"
    # trendsandbreakouts 2026-05: Sharpe 曲面平滑+顶部形成高原=稳定
    # Soloviov 2026-06 控制实验量化验证（v1.6.0 补）：选 smoothed surrogate argmax
    #   而非 raw argmax，OOS Sharpe 平均 +0.12(1D)/+0.31(2D)，随参数维度单调递增。
    #   但 plateau 几何指标 standalone 过拟合检测 AUC 弱——是"选择原则"非"独立检测"，
    #   须与 Step 3c DSR 校正 + Step 4 OOS 验证并用（Soloviov: "alongside, not instead of"）
    stability_region = find_plateau(params_candidates, sharpe_threshold=0.8*max_sharpe)
    if stability_region is None:  # 无稳定区域，参数是 needle peak
      return ADAPT_FAIL("参数不稳定（needle peak），refit 不可靠，建议 Level 5 退役")
    new_params = centroid(stability_region)  # 取稳定区域中心，非最高点（Soloviov 验证的 plateau centroid 选择原则）

    # 3c. 优化偏差校正（nexusfi 2026-06: N 次试验最大值膨胀 σ×√(2·ln N)）
    n_trials = len(params_candidates)
    inflation = sigma * sqrt(2 * log(n_trials))  # 10000 试验≈4.3σ 膨胀
    # DSR 校正（§7.2 PBO/DSR 检测联动）
    dsr = deflated_sharpe(observed_sharpe, n_trials, n_eff=effective_independent_trials)

  Step 4【OOS 验证】（adaptation vs overfitting 判定，mathandmarkets Part 82 核心）
    # 适应成功 = OOS Sharpe 改善；适应失败 = OOS 无改善（追逐噪声）
    oos_result = walk_forward_oos(strategy_id, new_params, test_window)
    if oos_result.sharpe > strategy.baseline_sharpe * 0.85:  # 恢复条件 IC ratio>0.7 精神
      # 适应成功：应用新参数，version 快照
      strategy.params = new_params
      strategy.adaptation_level = 2  # 回降到减仓监控
      EVOLVE_ENTRY(strategy.registry, strategy.id,
                   {params: new_params, adaptation_level: 2}, "schema_sig")
      alert("适应成功: " + strategy_id + " OOS Sharpe=" + oos_result.sharpe)
    else:
      # 适应失败：升级 Level 5 退役
      strategy.adaptation_level = 5
      RETIRE_ENTRY(strategy.registry, strategy.id, reason="decay")
      alert("适应失败: " + strategy_id + " 走退役流程")

  Step 5【适应频率约束】（防过度适应→过拟合）
    # mathandmarkets Part 82: 持续在线学习（Level 4）过拟合风险极高
    # 个人项目约束：Level 3 refit 最多季度 1 次，Level 4 需 ARCH 审批
    if strategy.last_refit_at and (today - strategy.last_refit_at) < 60 days:
      halt("refit 间隔 < 60 天，拒绝连续适应（防过拟合）")
    strategy.last_refit_at = today
```

**适应 vs 过拟合权衡表**（mathandmarkets Part 82 五级响应）：

| Level | 响应 | 触发条件 | 过拟合风险 | 个人项目适用 |
|---|---|---|---|---|
| 1 | 静默监控 | 默认态 | 无 | ✅ 默认 |
| 2 | 减仓 30-50% | decay_signal=warning（单检测器） | 无 | ✅ MVP |
| 3 | 季度 refit | decay_signal=critical（2/3 投票） | 中（需 OOS 验证） | ✅ Phase 1.5+ |
| 4 | 在线学习 | 持续 decay + ARCH 审批 | **高**（adaptation=overfitting） | ⚠️ 远期（需严格门禁） |
| 5 | 退役 | refit 失败 / sustained 2 年衰减 | 无 | ✅ §4.10 RETIRE_ENTRY |

> 🎯 **2026 适应vs过拟合最佳实践（v1.4.0 新增）**：[mathandmarkets Part 82, 2026-02-24](https://mathandmarkets.com/p/can-a-strategy-evolve-the-math-of) 系统论证"adaptation 和 overfitting 是同一数学操作"——区别仅在跟踪真实偏移（δ）还是追逐噪声（σ）。最优 refit window `w* = (2σ²/δ²)^(1/3) ≈ 126 天`，印证"季度 refit"经验法则。五级响应从静态→周期 refit→滚动窗口→在线学习→全 ML 重训，响应越快过拟合风险越高。[nexusfi 2026-06-01](https://nexusfi.com/a/automation/strategy-optimization) 补充"parameter stability regions"——选稳定高原中心非最高点（needle peak=curve-fitting）+ purge/embargo 防标签泄漏 + 优化偏差 `σ×√(2·ln N)`（10000 试验≈4.3σ 膨胀）。[trendsandbreakouts 2026-05-12](https://trendsandbreakouts.com/walk-forward-analysis) 强调 Walk-Forward 三阶段（IS/WF/OOS）+ 平滑 Sharpe 曲面判稳定。[arXiv:2602.10785, 2026-02-11](https://arxiv.org/abs/2602.10785) 提出 double OOS + Robust Sharpe Ratio + 81 组合 walk-forward window lengths 实证。
>
> **个人项目 MVP 决策**：MVP 阶段只做 Level 1-2（监控+减仓），Level 3 refit 延后到 Phase 1.5+（实盘 6-12 月衰减数据积累后）。Level 4 在线学习对个人项目属过度工程（adaptation=overfitting 风险高 + 需持续 OOS 验证基础设施），远期不采纳。Level 5 退役走 §4.10。`adaptation_level` + `last_refit_at` 字段需补入 strategy_registry schema（见 §6.1.2 v1.4.0 更新）。**关键约束**：refit 间隔 ≥60 天，防连续适应过拟合。

**三选一经验决策矩阵（v1.5.0 新增，对标 [LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/)）**：上述五级响应是数学驱动（severity + refit window + OOS 验证），LuxAlgo 2026-08-03 提供互补的**经验驱动**三选一决策矩阵——基于市场结构性原因而非纯统计指标决定 Reoptimize / Pause / Retire。与 Step 1.5 衰减原因分类（Five Horsemen）联动：

| 决策 | 对应 Level | 核心判据（LuxAlgo 2026-08-03） | 与 Five Horsemen 联动 |
|---|---|---|---|
| **Reoptimize**（重新优化） | Level 3 refit | ① 核心假设仍 fit 市场 ② OOS 扣成本后仍正 ③ 邻近参数产生类似结果（非孤立 optimum，plateau 非 needle peak） | regime / depletion 衰减原因 |
| **Pause / Cut Size**（暂停/减仓） | Level 2 减仓 | ① 证据 mixed ② expectancy 近 \$0 ③ drawdown 超正常但仍在 defensible risk range（1.5-2x prior max） | unknown / 早期 regime（<60 天未稳定） |
| **Retire**（退役） | Level 5 退役 | ① OOS expectancy 转负 ② walk-forward 持续失败 ③ realistic 成本侵蚀 edge ④ 原市场前提不再成立 | crowding / overfitting / tech 衰减原因 |

**review triggers 经验清单（v1.5.0 新增，对标 [LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/)）**：上述算法的 `decay_signal` 输入由 §4.8 DECAY_SCAN 统计检测器（CUSUM/PH/BOCPE/profit_factor/z_score）产生。LuxAlgo 2026-08-03 补充**经验驱动的 6 类 review triggers**——这些是业务指标层面的预警，与统计检测器互补（统计检测器告诉你"有异常"，review triggers 告诉你"是哪类异常"）。建议在 §4.8 DECAY_SCAN 中同时监控：

| # | review trigger | 阈值（LuxAlgo 2026-08-03） | 对应 decay_cause 诊断 | 触发 Level |
|---|---|---|---|---|
| 1 | rolling expectancy 趋向 \$0 或负 | expectancy < baseline × 0.3 | overfitting / depletion | Level 3-5 |
| 2 | drawdown drift | current_dd > 1.5-2x prior max_dd | regime / unknown | Level 2-3 |
| 3 | win rate 连续窗口下降 | 下降 10-15pp across consecutive windows | regime / crowding | Level 2-3 |
| 4 | profit factor 弱化 | 从 1.5-2.0 滑向 1.0（扣成本后） | crowding / tech | Level 3-5 |
| 5 | cost pressure | 滑点/价差/佣金/冲击侵蚀 gross edge | tech | Level 5（tech 类直接退役） |
| 6 | regime mismatch | trend/volatility/liquidity/range 不再匹配 setup | regime | Level 3（若新 regime 稳定） |

> 🎯 **2026-08 最新适应决策实践（v1.5.0 新增）**：[LuxAlgo 2026-08-03 "Edge Decay: Reoptimize or throw out your strategy"](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/) 核心论点"do not fix a bad strategy with hope; test whether the edge still exists, then reoptimize, pause, or shut it down based on evidence"——与 mathandmarkets Part 82 的数学驱动五级响应互补。LuxAlgo 强调：① review triggers 是"review triggers, not universal shutdown rules"——需按策略 trade frequency/payoff/market/leverage 校准；② baseline 保存是衰减检测前提（Step 0）；③ rolling trade windows 用 30-50 trades early diagnostic + 100+ trades confirmation。[Pomegra 2026](https://pomegra.io/learn/library/track-e-trading-risk/active-trading/chapter-04-trading-edges/edge-decay-and-adaptation) 补充：profit factor < 1.2-1.3 标边缘侵蚀（比 win rate 更可靠），slow decay（2-3%/年）vs sudden decay（周内崩溃）需不同响应速度。[smartfinancedata 2026](https://www.smartfinancedata.com/is-your-trading-edge-fading-signs-of-historical-edge-decay/) 127 策略实证：中位半衰期 11.2 月，67% 一年内失败，Five Horsemen 分类（crowding 41%/regime 28%/overfitting 18%/tech 9%/depletion 4%）驱动 Step 1.5 原因分类决策。
>
> **v1.5.0 算法增强总结**：Step 0（baseline 校验）+ Step 1.5（衰减原因分类驱动决策）+ 三选一经验决策矩阵 + 6 类 review triggers 清单，使 ADAPT_STRATEGY 从纯数学驱动（v1.4.0）升级为**数学+经验双驱动**（v1.5.0）。数学驱动回答"有没有衰减"（统计检测器），经验驱动回答"为什么衰减+该怎么响应"（原因分类+决策矩阵）。两者互补不替代——统计检测器先报警，review triggers 诊断原因，决策矩阵选响应级别。

### 4.13 上线晋升算法（PROMOTE_ENTRY，v1.8.0 新增）

§4.9 EVOLVE_ENTRY Step 1 引用 `PROMOTE_ENTRY` 但**v1.7.0 及之前未定义**——candidate→active（实盘上线）是最关键的状态转换（真金白银），却无正式算法。对标 [opennash 2026-06-22 生产就绪 7 门禁](https://opennash.com/blog/ai-workflow-passfail-criteria-the-production-readiness/)（"Treat these as gates, not a weighted average — a workflow that aces six gates and has no audit trail is a workflow that will eventually do something you cannot explain"）+ [MLflow 2026-05-16 MLOps Pipeline 自动化](https://mlflow.org/articles/mlops-pipeline-automation-best-practices-in-2026/)（"Gates prevent costly failures — automated validation gates stop bad models from reaching production"）+ [thirstysprout 2026-07-05 生产就绪 10 点](https://www.thirstysprout.com/post/production-readiness-checklist)（"Treat production readiness as a release gate with explicit sign-off"）+ [CSDN 量化投顾 Feature Store 2025-10](https://adg.csdn.net/696f554c437a6b40336a08a0.html)（"新因子上线必须经过可配置审批流程"）。

```
算法 PROMOTE_ENTRY(registry_id, entry_id, promotion_request):
  输入: entry_id（MUST 为 strategy），promotion_request{backtest_result, oos_period, reviewer}
  输出: status: candidate/experimental→active 转换 + baseline 保存 + 审计日志
  约束: 仅 strategy_registry 适用（factor/indicator 无实盘上线语义）

  entry = load_entry(registry_id, entry_id)
  if entry.status not in {"candidate", "experimental"}:
    halt("非 candidate/experimental 状态不可晋升: " + entry.status)
  if registry_id != "REG-STR-001":
    halt("PROMOTE_ENTRY 仅适用于 strategy_registry")

  gates_passed = []
  gates_failed = []

  # ── Gate 1: 回测验证门 ──
  # 对标 opennash Gate 1 Eval coverage + Gate 2 Edge-case pass rate
  # v1.17.0 修复：字符串拼接须 str() 转换（伪代码规范，Python 中 "text" + float 会 TypeError）
  bt = promotion_request.backtest_result
  if bt.oos_sharpe < 0.5:  # 最低门槛
    gates_failed.append("G1_oos_sharpe_below_threshold: " + str(bt.oos_sharpe))
  if bt.oos_max_drawdown > 0.15:  # 最大回撤红线
    gates_failed.append("G1_max_drawdown_exceeds_limit: " + str(bt.oos_max_drawdown))
  if bt.oos_period_months < 3:  # 至少 3 个月 OOS
    gates_failed.append("G1_oos_period_too_short: " + str(bt.oos_period_months) + " months")
  # v1.14.0 新增：min_trl_years 交叉校验（§7.2 experiment_registry schema v1.11.0 字段未引用——一致性修复）
  # Bailey & López de Prado 2014：回答"需多少年数据才能信任此 Sharpe"，MBL=0.5×(Z_α×σ_ann/SR_ann)²
  # 实盘 track record < min_trl_years → Sharpe 不足以排除噪声，MUST 继续 probation 而非确认
  if entry.min_trl_years and bt.oos_period_years < entry.min_trl_years:
    gates_failed.append("G1_oos_below_min_trl: " + str(bt.oos_period_years) + "y < " + str(entry.min_trl_years) + "y (Sharpe 不足以排除噪声，需更长 OOS)")
  if not gates_failed: gates_passed.append("G1_backtest")

  # ── Gate 2: 过拟合检查门 ──
  # 对标 MLflow model evaluation gate + §7.2 PBO/DSR/PSR/MinBTL/MTC/CPCV 六方法
  # ⚠️ PBO null=0.5 误读警示（v1.26.0 新增，对标 marketmaker.cc 2026-07-01 + arXiv PBO 论文）：
  #   PBO 的零假设是 0.5 不是 1——PBO≈0.5 = 完全过拟合 = 硬币翻转（in-sample winner 在 OOS 落入下半区概率=0.5）
  #   PBO≈0 = 选择可信（in-sample winner 可靠地保持 OOS winner）；PBO≈1 = 反转（in-sample winner 系统性 OOS loser）
  #   常见误读：把 PBO<0.5 当作"部分过拟合"——错。0.5 就是"完全随机"的基线，只有显著低于 0.5 才有泛化能力
  #   本门禁 PBO>0.2 阈值含义：仅当 PBO 显著低于 0.5（<0.2）才视为通过，0.2-0.5 区间仍阻断（泛化能力不足）
  if bt.is_overfit == True:
    gates_failed.append("G2_is_overfit_true")
  if bt.pbo_value and bt.pbo_value > 0.2:
    gates_failed.append("G2_pbo_above_0.2: " + str(bt.pbo_value))
  if bt.dsr_value and bt.dsr_value < 1.0:
    gates_failed.append("G2_dsr_below_1.0: " + str(bt.dsr_value))
  # v1.6.0 plateau_score 检查（Soloviov：选择原则，plateau_score > 0 为稳定参数区域）
  if bt.plateau_score is not None and bt.plateau_score < 0:
    gates_failed.append("G2_needle_peak_params_unstable")
  # v1.14.0 新增：MTC 多重检验校正（§7.2 回测过拟合第5方法 v1.12.0——一致性修复）
  # 当策略是 N 个同时检验的候选之一时，族错误率控制下须仍显著（White's RC/Hansen SPA/Romano-Wolf/MCS/BH-FDR）
  # bt.mtc_method 为空=未做多策略同时检验（单策略独立验证），跳过 MTC 检查
  if bt.mtc_method and bt.mtc_survived == False:
    gates_failed.append("G2_mtc_failed: " + bt.mtc_method + " 修正后未通过族错误率控制（多策略同时检验场景）")
  # v1.16.0 新增：CPCV 组合净化交叉验证（§7.2 回测过拟合第6方法——López de Prado 核心方法）
  # CPCV 生成 C(N,k) 条 OOS equity curve 分布而非 walk-forward 单条——变异过大=策略对切法敏感=过拟合
  # bt.cpcv_oos_sharpe_mean 为空=MVP 阶段未跑完整 CPCV（仅 PurgedKFold），跳过 CPCV 检查
  # v1.17.0 修复：mean<=0 须直接 FAIL（OOS 平均 Sharpe 为负/零=策略本身无效），原逻辑仅跳过变异检查是 bug
  if bt.cpcv_oos_sharpe_mean is not None:
    # catastrophic-veto：任何切分中最差 MaxDD 超红线 = 一票否决（AlgoXpert 2026-03）
    if bt.cpcv_worst_max_dd is not None and bt.cpcv_worst_max_dd > 0.15:
      gates_failed.append("G2_cpcv_catastrophic_veto: worst_max_dd " + str(bt.cpcv_worst_max_dd) + " > 0.15（任何切分回撤超红线=一票否决）")
    # mean<=0 直接 FAIL（OOS 平均 Sharpe 非正=策略在多数切分中亏损，不可部署）
    if bt.cpcv_oos_sharpe_mean <= 0:
      gates_failed.append("G2_cpcv_mean_nonpositive: mean " + str(bt.cpcv_oos_sharpe_mean) + " <= 0（OOS 平均 Sharpe 非正=策略在多数切分中亏损）")
    # 变异过大检查：std/mean > 0.5 = 策略对切法敏感 = 过拟合征兆（仅 mean>0 时检查，避免除零）
    elif bt.cpcv_oos_sharpe_std is not None and bt.cpcv_oos_sharpe_std / bt.cpcv_oos_sharpe_mean > 0.5:
      cv = bt.cpcv_oos_sharpe_std / bt.cpcv_oos_sharpe_mean
      gates_failed.append("G2_cpcv_variance_too_high: std/mean " + str(round(cv, 3)) + " > 0.5（策略对切法敏感=过拟合）")
  # v1.21.0 新增：有效 trial 数鲁棒性带（对标 Soloviov 2026-07 "How Many Backtest Winners Survive Deflation?"）
  # DSR 失败模式：用原始 trial count 在相关搜索中错误拒绝真实 edge（真实 Sharpe 3.92 被判 0.748<0.95）
  # 根因：有效 trial 数不是单一数值——5 个标准估计器在同 trial 矩阵上相差两个数量级（1.6 到 370）
  # 修复：① trial 间相关（如参数网格）时禁用裸 DSR，MUST 用 bootstrap-based 测试（White Reality Check/Hansen SPA）
  #       ② MUST 报告≥5 种有效 trial 数估计器的区间（robustness band）而非单值
  #       ③ deflated benchmark SR₀≈1.63（年化）=噪声天花板，策略 MUST 跨越此线
  # bt.trial_correlated=True 表示 trial 间有相关性（参数网格/同源变体），裸 DSR 不可信
  if bt.trial_correlated == True and bt.bootstrap_test_passed is None:
    gates_failed.append("G2_correlated_trials_no_bootstrap: trial 间相关但未跑 bootstrap 测试" +
                        "（Soloviov 2026-07: 相关搜索场景裸 DSR 错误拒绝真实 edge，" +
                        "MUST 用 White Reality Check/Hansen SPA 联合重采样）")
  if bt.effective_trial_count_band is None and bt.n_trials and bt.n_trials > 10:
    # n_trials>10 时有效 trial 数估计才有意义，MUST 报告区间而非单值
    warnings.append("G2_no_trial_count_band: n_trials=" + str(bt.n_trials) +
                    " 但未报告 effective_trial_count_band（≥5 估计器区间）。" +
                    "Soloviov 2026-07: 5 个估计器相差两个数量级，单值不可信")
  # v1.28.0 新增：PF ratio 一线实证阈值（对标 dibi8 2026-05-25 Backtest OVERFIT 5 patterns）
  # PF=盈利和/亏损和，计算极简无需 PBO/DSR 的 CSCV/bootstrap，是统计方法前的快速筛
  # dibi8 实证：moss-trade-bot Train PF 2.08→OOS PF 0.94，ratio 2.21=textbook overfit
  # ratio>2.0=阻断（textbook overfit）；1.5-2.0=warning（suspect）；<1.5=通过
  if bt.train_pf and bt.oos_pf and bt.oos_pf > 0:
    pf_ratio = bt.train_pf / bt.oos_pf
    if pf_ratio > 2.0:
      gates_failed.append("G2_pf_ratio_textbook_overfit: " + str(round(pf_ratio, 2)) +
                          "（Train PF " + str(bt.train_pf) + " / OOS PF " + str(bt.oos_pf) +
                          " > 2.0=textbook overfit，dibi8 2026-05: IS-OOS 发散）")
    elif pf_ratio > 1.5:
      warnings.append("G2_pf_ratio_suspect: " + str(round(pf_ratio, 2)) +
                      "（>1.5=suspect，dibi8 2026-05: 检查是否 walk-forward divergence 模式）")
  # v1.28.0 新增：最小交易数阈值（对标 dibi8 2026-05-25）
  # 低于此数统计不显著——directional 300 笔/mean_reversion 500 笔/优化过 1000+ 笔
  # 防止"30 笔交易就声称 edge"的小样本谬误（warning 级，不阻断但记录样本不足）
  min_trades = 500 if entry.strategy_type == "mean_reversion" else 300
  if bt.oos_trade_count and bt.oos_trade_count < min_trades:
    warnings.append("G2_oos_trade_count_below_min: " + str(bt.oos_trade_count) +
                    " < " + str(min_trades) + "（dibi8 2026-05: 样本不足，统计不显著，" +
                    "建议 viability_verdict=inconclusive 继续积累数据）")
  # v1.32.0 新增：参数稳定性区域检查（对标 AlgoXpert IS-WFA-OOS Protocol arXiv:2603.09219v1）
  # 选高原不选尖峰——cliff_detected=true 表示参数空间存在悬崖（小扰动导致性能崩溃=过拟合信号）
  # 与 plateau_score 检查互补：plateau_score 查标量分数，parameter_stability_region 查结构化区域分析
  # warning 级不阻断——MVP 阶段参数少（single_optimum 可接受），Phase 1.5+ 参数搜索 MUST 启用 stability_plateau
  psr = bt.parameter_stability_region
  if psr is not None:
    if psr.get("cliff_detected") == True:
      warnings.append("G2_param_cliff_detected: 参数空间检测到悬崖（AlgoXpert 2026-03: " +
                      "小扰动导致性能崩溃=过拟合信号，应优先 stability_plateau 而非 single_optimum）")
    if psr.get("selection_method") == "single_optimum" and entry.lifecycle_status in {"paper", "live"}:
      warnings.append("G2_single_optimum_in_production: paper/live 阶段仍用 single_optimum " +
                      "（AlgoXpert 2026-03: 生产阶段 SHOULD 启用 stability_plateau 避免悬崖敏感性）")
  if not gates_failed: gates_passed.append("G2_overfitting_check")

  # ── Gate 3: 风控限额分配门 ──
  # 策略上线 MUST 有风控限额 + Kill Switch 配置（风险优先原则）
  if not entry.risk_limit_id:
    gates_failed.append("G3_no_risk_limit_assigned")
  if not entry.kill_switch_config:
    gates_failed.append("G3_no_kill_switch_configured")
  if not gates_failed: gates_passed.append("G3_risk_limit")

  # ── Gate 4: Baseline 保存门 ──
  # §4.7 E12 前提：live+ 策略 MUST 有完整 baseline 字段
  baseline_fields = {baseline_sharpe, baseline_expectancy, baseline_win_rate,
                     baseline_profit_factor, baseline_max_drawdown, baseline_trade_frequency}
  missing = [f for f in baseline_fields if entry.get(f) is None]
  if missing:
    gates_failed.append("G4_missing_baseline_fields: " + missing)
  if not entry.decay_threshold:
    gates_failed.append("G4_no_decay_threshold")
  if not gates_failed: gates_passed.append("G4_baseline_saved")

  # ── Gate 5: 代码冻结门 ──
  # §4 原则9 版本可复现性三要素：code_commit MUST 绑定
  if not entry.code_commit:
    gates_failed.append("G5_no_code_commit_pinned")
  if not gates_failed: gates_passed.append("G5_code_frozen")

  # ── Gate 6: 基准分配门 ──
  # 策略 MUST 有 benchmark_id 用于归因（§6.1.2 schema）
  if not entry.benchmark_id:
    gates_failed.append("G6_no_benchmark_assigned")
  if not gates_failed: gates_passed.append("G6_benchmark")

  # ── Gate 7: 衰减监控设置门 ──
  # §4.8 DECAY_SCAN 前提：MUST 配置衰减检测方法+阈值+频率
  if not entry.decay_detection_method:
    gates_failed.append("G7_no_decay_detection_method")
  if not entry.decay_scan_frequency:
    gates_failed.append("G7_no_decay_scan_frequency")
  if not gates_failed: gates_passed.append("G7_decay_monitoring")

  # ── Gate 8: 人工签批门 ──
  # 对标 KRI Governance（§6.2.2）：阈值设定者≠受益者，上线 MUST 人工签批
  # 对标 opennash Gate 3 Human approval rules + thirstysprout "explicit sign-off"
  if not promotion_request.reviewer or promotion_request.reviewer == entry.owner:
    gates_failed.append("G8_no_independent_reviewer (owner 不能自批上线)")
  if not gates_failed: gates_passed.append("G8_human_signoff")

  # ── Gate 9: 容量检验门（v1.20.0 新增，对标 breakingalpha 2026-01 + linitics 2026-04 + EntroPy 2026-05） ──
  # breakingalpha 2026-01: "Capacity is not a secondary consideration; it is the primary filter
  #   through which all performance claims must be evaluated"
  # linitics 2026-04: "Capacity is not estimated by backtest. It is constrained by market structure."
  #   Backtests assume: Instant fills, Infinite liquidity, Fixed spreads, No impact
  # Square-Root Market Impact Model: Impact = σ × k × √(Q / ADV)
  #   平方根关系：交易 4% 日成交量成本约为交易 1% 的 2 倍——非线性冲击创造自然容量上限
  # 参与率红线：Participation Rate = Order Size / Market Volume，机构约束 ≤ 5%-10% ADV
  # EntroPy 2026-05: 10% ADV 容量估计作为 deployability hard filter
  # G1-G8 不问"这个 Sharpe 在多少资金下成立"——G9 填补"回测通过≠实盘可部署"盲区
  if not entry.capacity_aum_limit:
    gates_failed.append("G9_no_capacity_aum_limit (未声明策略资金容量上限。" +
                        "breakingalpha 2026-01: capacity 是 primary filter，" +
                        "未声明=不知道策略能承载多少资金，实盘放大资金可能因 market impact 失效)")
  else:
    # 检查回测假设的资金是否超容量上限
    bt_assumed_aum = bt.get("assumed_aum", 0) or 0
    if bt_assumed_aum > entry.capacity_aum_limit:
      gates_failed.append("G9_backtest_aum_exceeds_capacity: 回测假设资金 " + str(bt_assumed_aum) +
                          " > 容量上限 " + str(entry.capacity_aum_limit) +
                          "（回测在超容量资金下跑=结果不可信，market impact 已吃掉 alpha）")
  if not entry.participation_rate_limit:
    gates_failed.append("G9_no_participation_rate_limit (未声明参与率上限。" +
                        "linitics 2026-04: 机构约束 ≤5-10% ADV，超限导致冲击增加/被识别/逆向价格运动)")
  else:
    # 参与率红线检查：回测最大参与率不得超限
    bt_max_participation = bt.get("max_participation_rate", 0) or 0
    if bt_max_participation > entry.participation_rate_limit:
      gates_failed.append("G9_participation_rate_exceeded: 回测最大参与率 " +
                          str(round(bt_max_participation, 4)) + " > 上限 " +
                          str(entry.participation_rate_limit) +
                          "（超参与率红线=market impact 非线性爆发，回测成本低估）")
  if not entry.market_impact_model:
    gates_failed.append("G9_no_market_impact_model (未声明市场冲击模型。" +
                        "square_root=业界共识平方根模型/linear=线性近似/none=MVP小资金忽略。" +
                        "MVP 阶段小资金可填 none，资金增长后 MUST 升级 square_root)")
  if not gates_failed: gates_passed.append("G9_capacity_check")

  # ── 门禁裁决 ──
  # opennash: "Treat as gates, not weighted average" — 任何一门失败则阻断
  # ⚠️ v1.28.0 三值裁决增强（对标 arXiv:2607.20093 Joint Falsification 三重门框架）：
  #   二元 pass/fail 的缺陷："统计不显著"≠"证伪"——G2 因 PBO/DSR/PF ratio 不通过而 BLOCKED 的策略，
  #   可能是样本不足（INCONCLUSIVE）而非真无 edge（REFUTED）。
  #   INCONCLUSIVE → 继续 Shadow/Canary 积累样本（不放弃，不重申，静默积累）
  #   REFUTED → 走 §4.10 RETIRE_ENTRY 放弃（CI 排除声明效应，真无 edge）
  #   SUPPORTED → 全门通过，PROMOTE_ENTRY 全量上线
  #   区分依据：bt.oos_period_years < entry.min_trl_years（样本不足）→ INCONCLUSIVE 而非 REFUTED
  if gates_failed:
    # v1.28.0：统计门（G1/G2）失败且样本不足 → INCONCLUSIVE（继续 probation）而非 REFUTED（放弃）
    stat_gates_failed = [g for g in gates_failed if g.startswith("G1_") or g.startswith("G2_")]
    non_stat_gates_failed = [g for g in gates_failed if not (g.startswith("G1_") or g.startswith("G2_"))]
    is_sample_insufficient = (entry.min_trl_years and
                              bt.oos_period_years and
                              bt.oos_period_years < entry.min_trl_years)
    if non_stat_gates_failed:
      # 非统计门（G3-G9 风控/容量/签批等）失败 → 直接 REFUTED/BLOCKED（与样本无关，须修复）
      return PROMOTE_BLOCKED(gates_passed, gates_failed,
                             "上线被阻断（非统计门失败），修复失败门禁后重新申请。" +
                             "门禁非加权平均——任何一门失败即阻断。")
    elif is_sample_insufficient:
      # 仅统计门失败 + 样本不足 → INCONCLUSIVE（继续 probation 积累数据，不放弃）
      return PROMOTE_INCONCLUSIVE(gates_passed, gates_failed,
                                  "统计门未通过但样本不足（OOS " + str(bt.oos_period_years) +
                                  "y < MinBTL " + str(entry.min_trl_years) + "y），" +
                                  "viability_verdict=inconclusive——继续 Shadow/Canary 积累数据，" +
                                  "MinBTL 达标后重新裁决。非放弃：Joint Falsification 三值逻辑" +
                                  "（arXiv:2607.20093）区分'样本不足'与'真无 edge'。")
    else:
      # 统计门失败 + 样本充分 → REFUTED（真无 edge，走 RETIRE_ENTRY 放弃）
      return PROMOTE_REFUTED(gates_passed, gates_failed,
                             "统计门未通过且样本充分（OOS≥MinBTL），viability_verdict=refuted——" +
                             "置信区间排除声明效应，真无 edge，建议走 §4.10 RETIRE_ENTRY 放弃，" +
                             "勿反复重申（Joint Falsification arXiv:2607.20093）。")

  # ── 全部通过：执行晋升 ──
  entry.status = "active"
  entry.promoted_at = today
  entry.promoted_by = promotion_request.reviewer
  entry.lifecycle_status = "live"  # §4.8 生命周期第 4 阶段

  # 审计日志（opennash Gate 6 Audit trail: "Every run logs inputs, tool calls, and outputs"）
  audit_log.append({
    date: today, event: "PROMOTE_ENTRY", entry_id: entry_id,
    gates_passed: gates_passed, reviewer: promotion_request.reviewer,
    backtest_summary: bt.summary, oos_period: bt.oos_period_months
  })

  # 启动衰减监控（§4.8 DECAY_SCAN 按 decay_scan_frequency 开始扫描）
  schedule_decay_scan(entry_id, entry.decay_scan_frequency)

  # 通知依赖方（策略上线可能影响 portfolio 分配）
  notify_portfolios_using(entry_id, "策略已上线: " + entry_id)

  return PROMOTE_SUCCESS(entry_id, gates_passed)
```

**门禁清单**（9 门，对标 opennash 7-gate + MLflow validation gate + KRI governance 签批原则 + breakingalpha capacity）：

| 门 | 检查内容 | 失败条件 | 对标 |
|---|---|---|---|
| G1 回测验证 | OOS Sharpe/回撤/周期/min_trl_years | Sharpe<0.5 或 DD>15% 或 OOS<3月 或 OOS<min_trl_years（v1.14.0） | opennash Gate 1-2 + §7.2 MinBTL v1.11.0 |
| G2 过拟合检查 | PBO/DSR/PSR/plateau/MTC/CPCV/PF-ratio/min-trades/param-stability-region | is_overfit 或 PBO>0.2 或 DSR<1.0 或 needle peak 或 MTC 未通过（v1.14.0）或 CPCV catastrophic-veto/worst_max_dd>0.15 或 std/mean>0.5（v1.16.0，切法敏感性）或 PF ratio>2.0（v1.28.0）或 min_trades 不达（v1.28.0）；v1.32.0 warning 扩展：cliff_detected=true 或 paper/live 阶段 single_optimum | MLflow model eval gate + §7.2 六方法 |
| G3 风控限额 | risk_limit_id + kill_switch | 未分配风控限额或未配 Kill Switch | 风险优先原则 |
| G4 Baseline 保存 | 6 baseline 字段 + decay_threshold | 缺任意 baseline 字段 | §4.7 E12 前提 |
| G5 代码冻结 | code_commit 绑定 | 未 pin commit hash | §4 原则9 可复现性三要素 |
| G6 基准分配 | benchmark_id | 未分配基准 | §6.1.2 schema |
| G7 衰减监控 | detection_method + threshold + frequency | 未配置衰减监控 | §4.8 DECAY_SCAN 前提 |
| G8 人工签批 | 独立 reviewer（≠owner） | owner 自批或无 reviewer | KRI Governance 分离职责 |
| G9 容量检验（v1.20.0） | capacity_aum_limit + participation_rate_limit + market_impact_model | 未声明容量上限/参与率上限/冲击模型，或回测假设资金超容量，或回测最大参与率超限 | breakingalpha 2026-01 + linitics 2026-04 + EntroPy 2026-05 |

> ⚠️ **个人项目适用性**（避免过度工程）：9 门对个人+100%AI 项目映射为 **AI 自检 7 门 + 人工 1 门 + 容量 1 门**——Gate 1-7 由 AI agent 自动检查（回测结果/过拟合指标/风控配置/baseline/commit/benchmark/衰减设置），Gate 8 人工签批是唯一硬人工门（上线真金白银 MUST 人确认），Gate 9 容量检验 MVP 阶段 market_impact_model 可填 none（小资金忽略冲击）但 capacity_aum_limit + participation_rate_limit MUST 声明（资金增长后的硬指标）。MVP 阶段 Gate 2 过拟合检查可降级为 `is_overfit != True`（PBO/DSR Phase 1.5+ 补），但 Gate 3（风控+Kill Switch）和 Gate 8（人工签批）**不可降级**——这是实盘生存底线。

> 💡 **PROMOTE_ENTRY 与现有算法的关系**：PROMOTE_ENTRY 填补 §4.9 EVOLVE_ENTRY 引用的缺口——EVOLVE_ENTRY Step 1 `status` 变更分支 delegate 到 PROMOTE_ENTRY（candidate→active）或 RETIRE_ENTRY（active→deprecated）。完整生命周期闭环：CONSTRUCT_REGISTRY（建）→ PROMOTE_ENTRY（**上线**✨）→ EVOLVE_ENTRY（改）→ DECAY_SCAN（测）→ ADAPT_STRATEGY（适应）→ RETIRE_ENTRY（退）。此前 v1.7.0 及之前缺 PROMOTE_ENTRY，导致 candidate→active 转换无标准流程。

**渐进式部署：Shadow → Canary → Full（v1.10.0 新增）**：上述 9 门禁全过后即 `lifecycle_status=live`，但"门禁通过"≠"实盘验证通过"——回测/OOS 通过的策略实盘仍可能因 reality gap（滑点/延迟/流动性/执行建模差异）失效。2026 主流量化框架已形成 **shadow mode → canary split → full promotion** 三阶段渐进式部署共识，作为 PROMOTE_ENTRY 门禁通过后的"实盘 probation 期"（§4.8 生命周期第6阶段 Deployment="probation 非 confirmation"）。对标 [nexus-trade-engine #162 2026-04](https://github.com/SevFle/nexus-trade-engine/issues/162)（shadow+canary 数据模型 + 统计显著性检验）+ [metricgate 2026-04 Shadow vs Canary](https://metricgate.com/blogs/shadow-deployment-vs-canary/)（配对观测 vs 独立样本方差对比）+ [frontierledger 2026 Canary Trading Models](https://frontierledger.ai/infrastructure-mlops/canary-deployment-strategies-for-trading-models)（1-5% 资金渐进 5%→20%→50%→100%）+ [NautilusTrader 2026-08-09 影子模式沙箱](https://blog.csdn.net/sinat_28461591/article/details/151354636)（"只做决策不下单"虚拟订单对齐）。

| 阶段 | 模式 | 资金风险 | 机制 | 统计特性 | 通过条件 |
|---|---|---|---|---|---|
| ① Shadow | 影子模式 | **零** | 新版本订阅同一行情+信号，**只记录决策不发单**（PaperBrokerShim），对比 paper-trade 输出 vs live 实盘输出 | **配对观测**——两版本见相同输入，shared noise 抵消，方差 SE_shadow = √(σ²_new/N + σ²_old/N − 2ρσ_newσ_old/N)，ρ≈0.7-0.9 时方差骤降（metricgate 2026-04） | signal overlap > 80% + divergence log 无致命分歧，跑 1-3 天 |
| ② Canary | 金丝雀分流 | **小**（1-5% 资金） | 资金 90/10（或 95/5）分两个 sub-portfolio，新旧版本**各自真实交易**，N 天后对比 KPI 决定 promote/rollback | **独立样本**——两臂流量不相交，SE_canary = √(σ²_new/(cN) + σ²_old/((1−c)N))，c=0.05/ρ=0.8 时方差约 shadow 的 50x（metricgate） | paired t-test on daily returns 达 80% power + canary Sharpe ≥ baseline×0.85 + DD 未超限 |
| ③ Full | 全量上线 | 全量 | canary 通过后 5%→20%→50%→100% 渐进 ramp-up（frontierledger 2026），每档监控 1-2 周 | — | 全量后启动 §4.8 DECAY_SCAN 按 decay_scan_frequency 扫描 |

**shadow vs canary 统计学权衡**（metricgate 2026-04 核心洞察）：shadow 模式衡量"模型输出差异"（new 版本打分是否不同），**never 用户响应**——适合验证 rewrite/参数微调（预期行为"identical or better"）；canary 模式衡量"真实交易结果差异"（new 版本实盘是否赚更多）——适合验证有行为变化的改动（最终都需 canary 确认）。shadow 方差低（配对，ρ 抵消）、收敛快（小时-天级）、零资金风险，是"first-day testing default"；canary 方差高（独立）、收敛慢（天-周级）、有小资金风险，是"behavioral confirmation"。**正确顺序**：shadow 先（catch integration bugs + 输出层 regression）→ canary 后（catch behavioral regression + 实盘 reality gap）。

**自动回滚触发**（对标 [ai-trader #32 2026-02](https://github.com/cct08311github/ai-trader/issues/32) 2 小时自动回滚 + frontierledger automated rollback triggers）：canary 阶段若触发以下任一条件 → 自动 delegate §4.14 ROLLBACK_ENTRY 回退到 control 版本：① canary Sharpe < baseline×0.5（急剧退化）；② canary max_drawdown > baseline_max_dd×1.5（回撤超限，对标 LuxAlgo review trigger 2）；③ signal divergence > 30%（新旧版本决策严重分歧，疑似 integration bug）；④ Kill Switch 触发（risk breaker trip）。shadow 阶段无资金风险，不触发回滚，仅记录 divergence log 供审查。

> ⚠️ **个人项目适用性**（避免过度工程）：三阶段对个人+100%AI 项目映射为 **shadow（AI 自跑 paper）→ canary（人工确认小资金）→ full**——① shadow 模式个人项目**最易实现**：miniQMT 支持模拟盘，新版本跑模拟盘对比实盘输出即可（NautilusTrader 2026-08 推荐的"影子模式沙箱"），零资金风险，AI agent 自动对比 signal overlap + divergence log；② canary 模式需人工确认资金分配（Gate 8 签批精神延伸），MVP 阶段可简化为"小仓位试跑 1-2 周"而非严格 90/10 分流；③ full 模式即正常 PROMOTE_ENTRY 后的 live 态。**关键约束**：shadow→canary 升级需人工确认（shadow divergence log 审查），canary→full 升级需 paired t-test 达 80% power（避免小样本误判）。MVP 阶段若策略交易频率低（<10 笔/月），canary 统计显著性检验可能需 3-6 月才达 power——此时降级为"shadow 长跑 + 人工判断"，不强制 canary。
>
> 💡 **渐进式部署与 §4.14 ROLLBACK_ENTRY 的关系**：shadow/canary 是"上线前的 probation"，ROLLBACK_ENTRY 是"上线后的安全网"。canary 阶段自动回滚触发条件直接复用 §4.14 的触发源清单（decay_signal/drawdown_breach/manual），形成"上线前 shadow/canary 筛选 + 上线后 ROLLBACK 兜底"双层防护。canary 失败回退到 control ≠ ROLLBACK_ENTRY（control 仍是 live 态，未降级 monitoring），仅是"取消 canary 分流，全量维持 control"。

**Blue-Green 部署替代模式**（v1.10.0 新增，对标 [beefed.ai 2026 Canary/Blue-Green/Shadow 对比](https://beefed.ai/en/canary-blue-green-shadow-deployments)）：上述 shadow→canary→full 是渐进式三阶段，但**高策略上线需即时回滚能力**时可采用 Blue-Green 模式——保持两个完整环境（blue=当前 live 版本，green=新版本），green 环境验证通过后**原子切换**流量（router flip），回滚=再 flip 回 blue。beefed.ai 2026 对比：Blue-Green blast radius 极低（原子切换，无部分流量暴露）、infra cost 高（双环境）、business-signal visibility 完整（切换后全量可见）。**适用场景**：策略重大重构（如从规则版迁移到 ML 版）、参数空间剧变（非微调而是重设计）、regime 切换后批量策略升级。**个人项目适用性**：miniQMT 单账户不易实现双环境，但可用"配置切换"模拟——green=新参数配置文件，blue=旧参数配置文件，切换=加载不同配置，回滚=切回旧配置。MVP 阶段 shadow→canary→full 为主，Blue-Green 作为高风险上线的备选模式。

### 4.14 回滚算法（ROLLBACK_ENTRY，v1.9.0 新增）

§4.13 PROMOTE_ENTRY 解决"上线"，但**上线后发现问题如何回滚**是更关键的安全网——真金白银已入市，回滚速度决定损失规模。**v1.8.0 及之前缺回滚算法**，导致策略上线后表现异常时无标准回退流程，只能紧急手动处理（易出错+无审计）。对标 [Feast Feature View Versioning 2026-03-31](https://feast.dev/blog/feature-view-versioning/)（"roll back to the previous version" + audit trail 是版本化的核心动机）+ [sohilladhani 2026-06-17](https://sohilladhani.com/blog/post/2026-06-17-model-versioning-and-rollback/)（"Rollback is a metadata change, not file transfer—both models are already stored"）+ [DataScienceVerse 2026-01-23](https://www.datascienceverse.com/model-rollback-strategies-for-mlops-a-practical-guide-to-safe-automated-ci-cd-and-rapid-recovery/)（5 种回滚模式：manual/automated/canary/blue-green/feature-flag）+ [kriv.ai 2026](https://www.kriv.ai/articles/model-drift-monitoring-safe-retrain-canary-release-rollback)（"Rollback: Automated or approved promotion back to a previous model version if SLOs are breached"）+ [ml-canary-deploy 2026-06-20](https://github.com/Emart29/ml-canary-deploy)（`AUTO_ROLLBACK_ENABLED` + `MAX_ERROR_RATE_DELTA` 自动回滚参数）+ [asleekgeek 2026](https://asleekgeek.com/articles/model-registry-patterns)（"Promotion gate requires **a rollback plan is documented**"）。

```
算法 ROLLBACK_ENTRY(registry_id, entry_id, rollback_request):
  输入: entry_id（MUST 为 strategy，active/live 态）, rollback_request{reason, target_version, trigger_source, reviewer}
  输出: version 回退 + 仓位处置 + 衰减监控重置 + 审计日志
  约束: 仅 strategy_registry 的 active/live 态可回滚；回滚 ≠ 退役（§4.10），是临时回退到已知良好版本

  entry = load_entry(registry_id, entry_id)
  if entry.status != "active" or entry.lifecycle_status not in {"live", "monitoring"}:
    halt("非 active/live 态不可回滚: " + entry.status + "/" + entry.lifecycle_status)
  if registry_id != "REG-STR-001":
    halt("ROLLBACK_ENTRY 仅适用于 strategy_registry")

  # ── Step 1: 回滚触发判定 ──
  # 对标 kriv.ai 2026: "SLOs breached" + ml-canary-deploy: AUTO_ROLLBACK_ENABLED
  # 三类触发源（任一即可触发回滚申请）：
  #   ① 衰减检测器告警（§4.8 DECAY_SCAN: ic_ratio < 0.7 / profit_factor < 0.7 / z_score < -1.65）
  #   ② 回撤超限（current_drawdown > 1.5x baseline_max_drawdown，对标 LuxAlgo review trigger 2）
  #   ③ 人工判定（实盘观察发现回测未覆盖的异常模式，如政策突变/黑天鹅）
  trigger = rollback_request.trigger_source  # decay_signal / drawdown_breach / manual
  if trigger not in {"decay_signal", "drawdown_breach", "manual"}:
    halt("非法触发源: " + trigger)

  # ── Step 2: 回滚目标版本选择 ──
  # 对标 sohilladhani 2026-06: "both models are already stored, rollback is metadata change"
  # 对标 Feast 2026-03: version_pin 回滚到历史版本
  target_version = rollback_request.target_version
  if target_version is None:
    # 默认回退到上一个已知良好版本（PROMOTE_ENTRY 时的 baseline 版本）
    target_version = entry.baseline_version or entry.version - 1
  # 验证目标版本存在且可用（未退役）
  target_entry = load_version(registry_id, entry_id, target_version)
  if target_entry is None or target_entry.status == "retired":
    halt("回滚目标版本不可用: v" + target_version)

  # ── Step 3: 回滚频率约束（防 flip-flop）──
  # 对标 DataScienceVerse 2026-01: "avoid flip-flopping between versions"
  # 对标 light-trace 2026-03: "rollback strategies are only useful if they actually work"
  if entry.last_rollback_at and (today - entry.last_rollback_at) < 7 days:
    halt("回滚间隔 < 7 天，拒绝连续回滚（防 flip-flop）。若问题持续请走 §4.10 RETIRE_ENTRY 退役")
  # 单策略 30 天内最多回滚 2 次（超限强制退役审查）
  rollback_count_30d = count_rollbacks(entry_id, window=30 days)
  if rollback_count_30d >= 2:
    alert("30 天内回滚 ≥2 次，强制走 §4.10 RETIRE_ENTRY 退役审查: " + entry_id)
    delegate to RETIRE_ENTRY(registry_id, entry_id, reason="repeated_rollback")
    return

  # ── Step 4: 仓位处置（风险优先）──
  # 回滚≠立即清仓，而是"降级到安全状态"：
  #   ① 立即停止新开仓（仅允许平已有仓位）
  #   ② 现有仓位按 risk_rules 的减仓规则处理（非一键清仓，避免冲击成本）
  #   ③ Kill Switch 触发时例外（走 §6.2.2 kill_switch 的 halt 流程）
  entry.new_position_blocked = True  # 阻止新开仓
  # 现有仓位处理交给 risk_manager 按常规减仓规则（非回滚算法职责）
  alert("策略 " + entry_id + " 已回滚，阻止新开仓，现有仓位按减仓规则处理")

  # ── Step 5: 版本回退执行 ──
  # 对标 sohilladhani: "update the registry entry to point to target version, metadata change"
  # 对标 Atlan 2026-03 immutability: 不覆盖当前版本，而是 version_pin 指向历史版本
  entry.version_pin = target_version  # 指向回滚目标版本
  entry.active_version = target_version
  entry.lifecycle_status = "monitoring"  # 回滚后降级到 monitoring 态（非 live）
  entry.last_rollback_at = today
  entry.rollback_count = (entry.rollback_count or 0) + 1
  entry.rollback_reason = rollback_request.reason

  # ── Step 6: 衰减监控重置 ──
  # 回滚后需重新建立 baseline（回滚版本可能有自己的 baseline）
  # 对标 LuxAlgo 2026-08-03: baseline 保存是衰减检测前提
  if target_entry.baseline_sharpe:
    entry.baseline_sharpe = target_entry.baseline_sharpe
    entry.baseline_expectancy = target_entry.baseline_expectancy
    entry.baseline_win_rate = target_entry.baseline_win_rate
    entry.baseline_profit_factor = target_entry.baseline_profit_factor
    entry.baseline_max_drawdown = target_entry.baseline_max_drawdown
    entry.baseline_trade_frequency = target_entry.baseline_trade_frequency
  else:
    warning("回滚目标版本缺 baseline，回滚后需重新走 §4.13 PROMOTE_ENTRY G4 baseline 保存门")
  # 重启衰减监控（§4.8 DECAY_SCAN）
  schedule_decay_scan(entry_id, entry.decay_scan_frequency or "weekly")

  # ── Step 7: 审计日志 + 通知 ──
  # 对标 ml-canary-deploy: AUTO_ROLLBACK 记录 + asleekgeek: rollback plan documented
  audit_log.append({
    date: today, event: "ROLLBACK_ENTRY", entry_id: entry_id,
    from_version: entry.version, to_version: target_version,
    trigger: trigger, reason: rollback_request.reason,
    reviewer: rollback_request.reviewer,
    position_action: "new_position_blocked"
  })
  notify_portfolios_using(entry_id, "策略已回滚 v" + entry.version + "→v" + target_version +
                          " 触发: " + trigger + " 新开仓已阻止")

  # ── Step 8: 回滚后审查（7 天观察期）──
  # 回滚后 7 天观察期：若回滚版本表现正常 → 可重新申请 PROMOTE_ENTRY 升回 live
  # 若回滚版本仍异常 → 走 §4.10 RETIRE_ENTRY 退役
  schedule_review(entry_id, after=7 days, action="""

	回滚后审查：若回滚版本 7 天内表现正常（无衰减告警+回撤正常）→ 可重新申请 PROMOTE_ENTRY 升回 live；若仍异常 → RETIRE_ENTRY 退役
  """)

  return ROLLBACK_SUCCESS(entry_id, entry.version, target_version, trigger)
```

**回滚 vs 退役边界**（关键区分，避免混淆）：

| 维度 | ROLLBACK_ENTRY（§4.14） | RETIRE_ENTRY（§4.10） |
|---|---|---|
| 触发 | 实盘异常（衰减/回撤/人工） | 衰减确认持续 2 年 / 结构断裂 / 适应失败 |
| 目标 | 回退到已知良好版本，继续运行 | 永久退出，资金重分配 |
| 仓位 | 阻止新开仓，现有仓位按减仓规则 | 资金重分配，清仓退役 |
| 状态 | active→monitoring（降级观察） | active→deprecated→retired |
| 可逆 | ✅ 可重新 PROMOTE_ENTRY 升回 | ❌ retired 不可逆（需新建 entry） |
| 频率 | 7 天冷却 + 30 天 ≤2 次 | 90 天宽限 + 1 年保留 |

**回滚触发条件清单**（对标 [LuxAlgo 2026-08-03 review triggers](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/) + §4.8 DECAY_SCAN）：

| # | 触发条件 | 阈值 | 对应回滚触发源 |
|---|---|---|---|
| 1 | IC ratio 跌破阈值 | ic_ratio < 0.7（§4.8 DECAY_SCAN） | decay_signal |
| 2 | profit_factor 跌破阈值 | PF < 0.7 × baseline（§4.8 profit_factor 检测器） | decay_signal |
| 3 | z_score 分布偏移 | z_score < -1.65（5% 显著，§4.8 z_score 检测器） | decay_signal |
| 4 | 回撤超限 | current_dd > 1.5× baseline_max_dd（LuxAlgo trigger 2） | drawdown_breach |
| 5 | 连续亏损 | 连续 N 笔亏损（N = baseline_trade_frequency × 3） | drawdown_breach |
| 6 | 人工判定 | 实盘观察发现回测未覆盖的异常模式 | manual |

> ⚠️ **个人项目适用性**（避免过度工程）：回滚对个人+100%AI 项目映射为 **AI 监控告警 + 人工触发回滚**——AI agent 自动监控上述 6 类触发条件，触发时告警人工确认后执行回滚（Gate 8 人工签批精神延伸：回滚也 MUST 人工确认，非自动执行）。MVP 阶段回滚频率约束（7 天冷却 + 30 天 ≤2 次）可简化为"人工判断频率"，但**仓位处置（阻止新开仓）不可省略**——这是回滚的安全底线。自动回滚（ml-canary-deploy 的 `AUTO_ROLLBACK_ENABLED` 模式）对个人项目风险过高（flip-flop + 实盘异常可能误判），远期也不采纳。

> 💡 **ROLLBACK_ENTRY 与现有算法的关系**：ROLLBACK_ENTRY 填补 PROMOTE_ENTRY 的逆向缺口——PROMOTE（上）→ DECAY_SCAN（测）→ **ROLLBACK（回退）**✨ 或 ADAPT（适应）→ RETIRE（退）。回滚是"临时回退到已知良好版本继续运行"，退役是"永久退出"。回滚后 7 天观察期决定：恢复正常→重新 PROMOTE，仍异常→RETIRE。完整生命周期闭环（v1.9.0）：CONSTRUCT（建）→ PROMOTE（上线）→ EVOLVE（改）→ DECAY_SCAN（测）→ ROLLBACK（**回退**✨）或 ADAPT（适应）→ RETIRE（退）。

### 4.15 依赖解析算法（DEPENDENCY_RESOLVE，v1.9.0 新增）

§4.6 交叉引用矩阵登记了 26 条 FK 关系，但**缺依赖解析算法**——施工时需确定 12 表的拓扑顺序（哪些表必须先建），entry 退役时需查传递依赖（RETIRE_ENTRY 只查直接依赖，不查间接依赖链），schema 演进时需算影响范围（哪些表受 breaking 变更波及）。对标 [kindatechnical 2026-03 Service Dependency Graphs](https://kindatechnical.com/continuous-integration-continuous-deployment/service-dependency-graphs-and-deploy-ordering.html)（Kahn's algorithm 拓扑排序 + deploy ordering）+ [technetexperts 2026-02 Dynamic DAG](https://www.technetexperts.com/dynamic-dag-data-dependency/)（`R(B) ∩ W(A) ≠ ∅` 依赖推断）+ [axonops schema registry 2026-03](https://github.com/axonops/axonops-schema-registry/issues/290)（cross-context copy with dependency graph + `Registry.GetDependencyGraph()`）。

```
算法 DEPENDENCY_RESOLVE(operation, registry_id, entry_id):
  输入: operation{construct_order / transitive_deps / impact_scope}, registry_id, entry_id
  输出: 拓扑序（construct_order）/ 传递依赖链（transitive_deps）/ 影响范围（impact_scope）

  # ── 构建 12 表 FK 有向图 ──
  # 节点 = registry_id，边 = FK 引用（引用方 → 被引用方 = 依赖方向）
  # 对标 technetexperts: R(B) ∩ W(A) ≠ ∅ → B 依赖 A
  # §4.6 矩阵的 26 条 FK 转为有向边：
  #   universe.used_by_strategies → strategy  意为 strategy 依赖 universe（strategy→universe 边）
  #   factor.belongs_to_strategies → strategy  意为 strategy 依赖 factor（strategy→factor 边）
  #   注意：FK 字段名 "used_by_X" 是反向引用，实际依赖方向是 X 依赖本表
  graph = build_fk_graph(§4.6 cross_ref_matrix)

  # ── 操作 1: construct_order（施工拓扑序）──
  if operation == "construct_order":
    # 对标 kindatechnical: Kahn's algorithm
    # 拓扑序 = 被依赖方先建，依赖方后建
    # P0（universe/benchmark/cost_model）无依赖 → 先建
    # P1-A（factor/strategy/indicator）依赖 P0 → 中建
    # P1-B（execution/risk/data/pattern）依赖 P1-A → 后建
    # P2（field_dict/experiment）依赖 P1 → 最后建
    topo_order = kahn_topological_sort(graph)
    # 验证无环（E8 已查 entry 级 variant_of 环，此处查 registry 级 FK 环）
    if has_cycle(graph):
      halt("12 表 FK 存在循环依赖，需修复 §4.6 矩阵")
    return topo_order  # 如 [universe, benchmark, cost_model, factor, indicator, strategy, ...]

  # ── 操作 2: transitive_deps（传递依赖链，RETIRE_ENTRY 级联用）──
  if operation == "transitive_deps":
    # §4.10 RETIRE_ENTRY 的 find_reverse_refs 只查直接依赖
    # 本操作递归查传递依赖链（A 退役 → B 依赖 A → C 依赖 B → C 也受影响）
    # 对标 axonops: GetDependencyGraph() bidirectional traversal
    direct_deps = find_reverse_refs(registry_id, entry_id)  # 直接依赖
    all_deps = set(direct_deps)
    frontier = direct_deps
    while frontier:
      next_frontier = []
      for dep in frontier:
        indirect = find_reverse_refs(dep.registry_id, dep.entry_id)
        for ind in indirect:
          if ind not in all_deps:
            all_deps.add(ind)
            next_frontier.append(ind)
      frontier = next_frontier
    # 返回完整依赖链（直接 + 间接）
    return all_deps  # RETIRE_ENTRY 级联响应须通知全部传递依赖方

  # ── 操作 3: impact_scope（影响范围，EVOLVE_SCHEMA breaking 变更用）──
  if operation == "impact_scope":
    # §4.11 EVOLVE_SCHEMA breaking 变更时，需知道哪些表受影响
    # 对标 kindatechnical: "deploying in the wrong order can cause cascading failures"
    # 正向查询：本表 schema 变更 → 哪些表的 FK 引用了本表 → 影响范围
    forward_deps = find_forward_refs(registry_id, entry_id)
    all_impacted = set(forward_deps)
    # 递归查传递影响（本表变 → 依赖本表的表变 → 依赖它们的表也变）
    frontier = forward_deps
    while frontier:
      next_frontier = []
      for dep in frontier:
        indirect = find_forward_refs(dep.registry_id, dep.entry_id)
        for ind in indirect:
          if ind not in all_impacted:
            all_impacted.add(ind)
            next_frontier.append(ind)
      frontier = next_frontier
    return all_impacted  # EVOLVE_SCHEMA Expand-Contract 迁移须覆盖全部影响范围
```

**12 表施工拓扑序**（Kahn 算法结果，验证 §3 优先级合理性）：

```
Layer 0（无依赖，先建）: universe, benchmark, cost_model
  ↑ universe 无 FK 依赖
  ↑ benchmark.underlying_universe → universe（弱 FK，可 forward-ref）
  ↑ cost_model 无 FK 依赖

Layer 1（依赖 Layer 0）: field_dictionary, data_asset
  ↑ field_dictionary.source_system → data_asset.source_id
  ↑ data_asset 三实体 self-ref

Layer 2（依赖 Layer 0-1）: technical_indicator, chart_pattern
  ↑ technical_indicator.inputs → field_dictionary
  ↑ chart_pattern 无强 FK（可独立建）

Layer 3（依赖 Layer 0-2）: factor
  ↑ factor.universe → universe
  ↑ factor.benchmark_id → benchmark
  ↑ factor.inputs → field_dictionary
  ↑ factor 依赖 technical_indicator/chart_pattern（used_by_factors 反向）

Layer 4（依赖 Layer 0-3）: execution_algo, risk_limit
  ↑ execution_algo.cost_model_ref → cost_model
  ↑ risk_limit.scope_strategy → strategy（弱 FK，可 forward-ref）

Layer 5（依赖 Layer 0-4）: strategy
  ↑ strategy.alpha_sources → factor
  ↑ strategy.risk_rules → risk_limit
  ↑ strategy.benchmark_id → benchmark

Layer 6（依赖全部）: experiment
  ↑ experiment.target_id → factor/strategy/indicator/pattern/risk_rule/execution_algo
  ↑ experiment.universe → universe
  ↑ experiment.benchmark_id → benchmark
  ↑ experiment.cost_model_ref → cost_model
  ↑ experiment.parent_experiment_id → experiment（self-ref）
```

> 📊 **拓扑序 vs §3 优先级的对应关系**：Kahn 算法计算的拓扑序与 §3 裁定 7 的 P0→P1-A→P1-B→P2 施工顺序**一致**——P0（Layer 0）→ P1-A（Layer 2-3-5 被测对象）→ P1-B（Layer 4 交易/风控/数据/图形，Layer 1 字段字典/数据资产可提前）→ P2（Layer 6 实验）。**这从图论角度验证了 §3 施工顺序的合理性**——回测必需输入（P0）无依赖先建，被测对象（P1-A）依赖 P0，交易/风控（P1-B）依赖 P1-A，实验/治理（P2）依赖全部。

> 💡 **DEPENDENCY_RESOLVE 与现有算法的关系**：本算法是 12 表 FK 矩阵（§4.6）的**算法层补全**——§4.6 给了数据（26 条 FK），本算法给了操作（拓扑排序/传递依赖/影响范围）。施工时用 `construct_order` 确定建表顺序（对标 Kahn 拓扑排序），退役时用 `transitive_deps` 查完整级联链（补全 §4.10 RETIRE_ENTRY 的直接依赖查询），schema 演进时用 `impact_scope` 算 breaking 变更影响范围（补全 §4.11 EVOLVE_SCHEMA 的迁移范围）。E8 循环引用检测（entry 级 variant_of）+ 本算法（registry 级 FK 环检测）形成双层防环。

### 4.16 YAML→DB 迁移算法（MIGRATE_REGISTRY，v1.11.0 新增）

§11 描述了 YAML→DB 迁移路径（触发条件 + 混合模式 + 窄表存储），但**无施工算法**——12 注册表从 YAML 迁移到 PG 是高风险操作（数据丢失/双源不一致/迁移中断），需分阶段渐进式迁移确保零数据丢失 + 可回滚。对标 [quantified-uncertainty/longterm-wiki #2076 2026-03-11](https://github.com/quantified-uncertainty/longterm-wiki/issues/2076) R1-R6 六阶段 YAML→PG 迁移 playbook（resources 表已验证的成熟模式，records 表复用）+ [mvpfactory.io 2026-04-29 Expand-Contract vs Blue-Green](https://mvpfactory.io/blog/zero-downtime-postgresql-schema-migrations-expand-contract-vs-blue-green)（零停机 schema 迁移双模式）+ [youngju.dev 2026-06-16 Schema Migration Tools](https://www.youngju.dev/blog/database/2026-06-16-schema-migration-tools-comparison.en)（Flyway/Liquibase/Alembic/Atlas 对比，checksums 完整性 + advisory locks 并发安全）。

```
算法 MIGRATE_REGISTRY(registry_id):
  输入: registry_id（如 REG-FCT-001），触发条件已满足（factor>500 / experiment>5000 / 并发写需求）
  输出: registry 从 YAML-only 迁移到 PG-primary + YAML-snapshot，零数据丢失
  约束: 逐表迁移（非12表同时），每表走完 R1-R6 才迁下一表；按 §4.15 construct_order 的逆序迁移（experiment→strategy→...→universe，被依赖方后迁）

  # ── R1: PG 表结构创建（Schema as Code）──
  # 对标 youngju.dev: Atlas declarative schema + golang-migrate versioned up/down
  # 对标 §4 原则2: entry_schema 按 DB 表设计预留迁移（id/created_at/updated_at/version/status）
  pg_table = "registry_" + registry_id.lower()  # 如 registry_factor
  create_pg_table(pg_table, columns_from_entry_schema)
  # MUST 含 unique_key 约束 + created_at/updated_at 索引
  # schema_version 字段记录迁移时点的 schema 版本
  # 迁移脚本入 git（如 migrations/001_registry_factor_up.sql + _down.sql），对标 Flyway versioned migration

  # ── R2: PG 数据导入 + YAML fallback（双源共存）──
  # 对标 longterm-wiki R2: build-data reads PG with YAML fallback
  # YAML 仍是 SSoT，PG 是镜像（read-through cache 语义）
  yaml_entries = load_yaml(registry_id)
  for entry in yaml_entries:
    upsert_pg(pg_table, entry)  # 幂等写入（ON CONFLICT DO UPDATE）
  # 验证：PG 行数 == YAML entry_count（E6 编号-代码对齐的 DB 版）
  pg_count = count_pg(pg_table)
  yaml_count = len(yaml_entries)
  if pg_count != yaml_count:
    halt("R2 数据导入不一致: PG=" + pg_count + " YAML=" + yaml_count)
  # loader 改为 PG-first + YAML-fallback（PG 不可用时降级读 YAML）
  update_loader(registry_id, mode="pg_first_yaml_fallback")

  # ── R3: CLI 读取 PG-first（YAML 降级为 fallback）──
  # 对标 longterm-wiki R3: CLI reads PG-first
  # 所有读操作（查询/审计/依赖解析）优先读 PG，PG 不可用才降级 YAML
  # 此阶段 YAML 仍是写入 SSoT，PG 是只读镜像
  update_all_readers(registry_id, mode="pg_first")
  # 观察 1-2 周稳定性（PG 读取无异常 + 性能可接受）

  # ── R4: 数据完整性验证（gate，非阶段）──
  # 对标 longterm-wiki Phase 1 prerequisite check
  # 在 R3→R5 之间强制验证：PG 数据 == YAML 数据（bit-level 或 semantic-level）
  for entry in load_yaml(registry_id):
    pg_entry = load_pg(pg_table, entry.id)
    if not deep_equal(entry, pg_entry, ignore=["updated_at"]):
      halt("R4 数据漂移: YAML entry " + entry.id + " ≠ PG 版本")
  # 额外检查：FK 引用完整性（E4 的 DB 版）+ unique_key 唯一性
  run_db_constraints_check(pg_table)
  # R4 通过才进入 R5（写入切换）

  # ── R5: 双写模式（PG 成为写入 SSoT，YAML 同步降级）──
  # 对标 longterm-wiki R5: Dual-write on changes
  # 所有写操作（EVOLVE_ENTRY/RETIRE_ENTRY/PROMOTE_ENTRY）同时写 PG + YAML
  # PG 是权威源，YAML 是同步镜像（fire-and-forget PG sync, YAML 仍保持同步）
  update_all_writers(registry_id, mode="dual_write_pg_primary")
  # 双写期间定期校验一致性（每小时 diff PG vs YAML）
  schedule_consistency_check(registry_id, frequency="hourly")

  # ── R6: YAML 数据删除（PG 成为唯一 SSoT）──
  # 对标 longterm-wiki R6: Delete YAML record data
  # 前提：R5 双写运行 ≥ 4 周无不一致告警
  if consistency_check_clean_days(registry_id) < 28:
    halt("R5 双写一致性未达 28 天清洁期，拒绝 R6 YAML 删除")
  # 生成 YAML 快照入 git（离线 fallback，对标 longterm-wiki "snapshot file for offline fallback"）
  snapshot_path = "snapshots/" + registry_id + "_" + today + ".yaml"
  export_yaml_snapshot(registry_id, snapshot_path)
  git_commit(snapshot_path, "R6 迁移快照: " + registry_id + " PG 成为 SSoT")
  # 从 YAML 删除 entry 数据（保留 schema 定义 + frontmatter）
  remove_entries_from_yaml(registry_id)  # YAML 降级为 schema-only
  update_loader(registry_id, mode="pg_only")  # 移除 YAML-fallback
  # YAML schema 定义仍入 git（DB 表结构的声明式定义），但 entry 数据只存 PG

  # ── R7: 迁移后审计（gate，非阶段）──
  # 对标 §4.7 AUDIT_REGISTRY 的 DB 版：E1-E20 在 PG 上重跑
  audit_result = AUDIT_REGISTRY(registry_id)  # 现在 reads PG
  if audit_result.errors:
    halt("R7 迁移后审计有 errors: " + audit_result.errors + "，需修复或 ROLLBACK 迁移")
  # 更新 registry_of_registries.yaml 的 storage 字段: yaml_only → pg_primary
  update_registry_of_registries(registry_id, storage="pg_primary_yaml_snapshot")
  audit_log.append({date: today, event: "MIGRATE_REGISTRY", registry_id: registry_id,
                    phases: "R1-R6 completed", snapshot: snapshot_path})
```

**迁移阶段总结**（R1-R7，对标 longterm-wiki R1-R6 + 补 R4/R7 gate）：

| 阶段 | 名称 | SSoT | 读源 | 写源 | 风险 | 回滚 |
|---|---|---|---|---|---|---|
| R1 | PG 表创建 | YAML | YAML | YAML | 低（仅建表） | DROP TABLE |
| R2 | 数据导入+fallback | YAML | YAML（PG 镜像） | YAML | 低（PG 只读） | DELETE PG rows |
| R3 | CLI PG-first | YAML | PG→YAML fallback | YAML | 中（读切换） | loader 回 YAML-only |
| **R4** | **完整性验证 gate** | YAML | — | — | — | halt 不进 R5 |
| R5 | 双写模式 | **PG**（写入权威） | PG→YAML | PG+YAML 双写 | **高**（写切换） | loader 回 YAML-write |
| R6 | YAML 数据删除 | **PG**（唯一 SSoT） | PG only | PG only | 高（不可逆） | 从 snapshot 恢复 YAML |
| **R7** | **迁移后审计 gate** | PG | — | — | — | halt + 考虑回滚 |

**并发迁移安全**（对标 [mvpfactory.io 2026-04](https://mvpfactory.io/blog/zero-downtime-postgresql-schema-migrations-expand-contract-vs-blue-green) advisory locks）：多注册表并行迁移时，每表迁移 MUST 获取 PG advisory lock 防止并发 DDL 冲突——`SELECT pg_advisory_lock(hash(registry_id))` 确保同一时间只有一个迁移脚本操作该表。12 表迁移按 §4.15 construct_order **逆序**进行（experiment 先迁，universe 最后迁）——被依赖方后迁避免 FK 指向未迁移表的中间态。

**Schema 迁移模式选择**（对标 mvpfactory.io Expand-Contract vs Blue-Green）：
- **Expand-Contract**（默认，适用 80% 场景）：additive 变更（加字段）走 Expand（加新列）→ Migrate（backfill）→ Contract（删旧列），对标 §4.11 EVOLVE_SCHEMA 的同名模式。PG 11+ 加列无默认值不锁表，backfill 分批 UPDATE 避免长事务。
- **Blue-Green shadow schema**（高风险 breaking 变更）：创建 `green` schema 完整副本 + trigger-based 双写同步，验证通过后 `CREATE OR REPLACE VIEW public.X AS SELECT * FROM green.X` 原子切换，回滚=再 flip 回 blue。适用场景：schema 重大重构（如窄表↔宽表转换）、字段类型变更（int→str）。个人项目 PG 阶段以 Expand-Contract 为主，Blue-Green 作为 breaking 变更的备选。

> ⚠️ **个人项目适用性**（避免过度工程）：个人项目当前因子<500/实验<5000，**远未触发迁移阈值**（§11），本算法是 Phase 2+ DB 迁移阶段的预案非当前施工项。MVP 阶段 YAML + git 足够（§4 原则8 半派生 + §4 原则9 git 版本追溯）。但 schema 按 DB 表设计（§4 原则2）的成本极低，R1-R7 算法预存于此，迁移触发时直接执行。**关键约束**：R6（YAML 数据删除）不可逆，MUST 先生成 git 快照 + R5 双写清洁 28 天 + R7 审计通过三条件全满足才执行。

> 💡 **MIGRATE_REGISTRY 与现有算法的关系**：本算法是 §11 YAML→DB 迁移路径的**算法层补全**——§11 给了"何时迁"（触发条件）+"迁后什么样"（混合模式/窄表），本算法给了"怎么迁"（R1-R7 七阶段渐进式）。迁移后 §4.7 AUDIT_REGISTRY 的 E1-E13 检查从 YAML grep 改为 PG SQL 查询，§4.9 EVOLVE_ENTRY 的版本快照从 git diff 改为 PG version 字段 + trigger 自动记录，§4.13 PROMOTE_ENTRY 的 G5 code_commit 从 git blame 改为 PG 字段强制非空。这是 12 注册表从"YAML 时代"到"DB 时代"的统一迁移协议。

### 4.17 2026-08-10 最新研究对标补充（v1.12.0 新增）

全网搜索 2026-08-10 前后最新研究，发现 8 项显著优于现有方法或填补缺口的算法/实践，分领域对标补充。**每项标注"对标 §X"指示应增强的具体章节**，避免散落多处难以维护。

**① 衰减检测：双曲衰减模型 α(t)=K/(1+λt)（对标 §4.8 DECAY_SCAN）**

[arXiv:2512.11913 2025-12-11](https://arxiv.org/html/2512.11913v1/)（Chorok Lee, KAIST）从博弈论 Nash 均衡模型推导出因子 alpha 衰减的具体函数形式：**α(t) = K/(1+λt)**（双曲衰减），在 8 个 Fama-French 因子（1963-2024）上验证：动量因子双曲衰减 R²=0.65，优于线性(0.51)和指数(0.61)。**关键发现**：① 机械因子（动量、反转）符合双曲模型；判断型因子（价值、质量）不符合——启示 decay_cause 诊断时区分因子类型；② 2015 年后拥挤加速（λ 增大）；③ 拥挤预测**尾部风险**而非均值——拥挤的反转因子崩盘概率高 1.7-1.8 倍。**比现有方法更好**：§4.8 当前用 CUSUM/PH/BOCPE 检测"是否衰减"（二值报警），双曲模型补充"衰减速率 λ"（量化预测）——可用 λ 估计策略剩余寿命 `T_remaining ≈ K/(λ × α_threshold) - 1/λ`，驱动 §4.12 ADAPT_STRATEGY 的 refit vs retire 决策（λ 大→快速衰减→直接退役；λ 小→缓慢衰减→refit 有时间窗口）。**个人项目适用性**：高。MVP 阶段对 momentum/reversal 类策略用双曲模型拟合历史 IC 序列估 λ，Phase 1.5+ 扩展到全策略类型。

**② 衰减检测：score-driven BOCPD 变体 + 统一接口工具（对标 §4.8 DECAY_SCAN_MULTI 检测器 3）**

§4.8 三检测器中 CUSUM/Page-Hinkley 为频率派，**BOCPE（检测器 3）已是贝叶斯方法**（Adams & MacKay 2007 BOCPD，v1.3.0 引入，v1.10.0 增强 Student-t likelihood）——v1.12.0 原文误称"三检测器均为频率派"系事实错误，v1.14.0 修正。因此本项的真正增量**不是"加 BOCPD 第 4 检测器"**（BOCPE=BOCPD 已是检测器 3），而是 **score-driven BOCPD 变体**（处理 regime 内时间相关性）+ 统一接口工具。[RegimeChange R 包 2026-08-01](https://github.com/isadorenani/regimeChange) 统一接口整合 PELT/BOCPD/CUSUM，针对金融时序设计：自适应方差地板（数值稳定）、可选预白化（处理自相关）、稳健 M 估计（重尾分布）。[Tsaknaki et al. 2025 Quantitative Finance 25(2)](https://ideas.repec.org/a/taf/quantf/v25y2025i2p307-322.html) 的 **score-driven BOCPD** 适应每个 regime 内的时间相关性（i.i.d. 假设违反时标准 BOCPD 退化），在 NASDAQ 数据上优于 i.i.d. 假设模型——这是对 §4.8 检测器 3 的**变体升级**而非新增第 4 检测器。**比现有方法更好**：score-driven 变体在 regime 内自相关强（A 股收益 AR(1) φ≥0.3 常见）时优于标准 BOCPD 的 i.i.d. 假设。**MVP 决策**（v1.14.0 修正）：§4.8 检测器 3 已是贝叶斯 BOCPD，无需"加第 4 检测器"；Phase 1.5+ 升级路径为将检测器 3 的 likelihood 从标准 Student-t 升级为 **score-driven**（Tsaknaki 2025），保持 2/3 投票不变。另：[ruptures 2026-05-26 新增 L1Potts 类](https://github.com/deepcharles/ruptures)对分段常数信号变化点检测更高效，若已用 ruptures 是免费升级。

**③ 漂移检测：Wasserstein Distance（对标 §4.7 E11 / factor·strategy data_quality_policy）**

§4.7 E11 当前用 PSI/KS 检测数据漂移。[Wasserstein Distance（Earth Mover's Distance）](https://futureagi.com/glossary/wasserstein-distance/) 是几何感知的漂移度量——计算将一个分布"搬运"到另一个的最小成本。**比 PSI/KS 更好**：① KS 只关注最大累积差，忽略尾部细节；② PSI 对尾部敏感但无几何感知（相邻 bin 移动和远处移动贡献相同）；③ **Wasserstein 对不重叠分布仍提供有意义梯度**（KL 散度会发散），且考虑分布几何（相邻 bin 移动比远处移动贡献小）。[royxforge/production-drift-detection 2026-07-20](https://github.com/royxforge/production-drift-detection) 提供生产级实现，集成 KL（拉普拉斯平滑，零误报，ROC AUC 0.9995）+ PSI + Wasserstein，默认阈值已校准。**个人项目适用性**：高。factor/strategy schema 的 `data_quality_policy.drift_method` 当前支持 `psi/ks`，v1.12.0 扩展支持 `wasserstein`（对特征分布"位移"敏感而非简单"差异"，适合检测因子值整体偏移）。另：[四类漂移分层故障树 2026-06-15](https://bbs.csdn.net/weixin_30533109/article/details/100144113) 将漂移分为概念漂移(P(Y|X)变)/数据漂移(P(X)变)/标签漂移(P(Y)变)/先验漂移(正负比变)四层，PSI>0.1 时多数模型 AUC 开始下滑的实测阈值可直接复用。

**④ YAML→DB 迁移：pgroll 零停机 Schema 变更（对标 §4.16 MIGRATE_REGISTRY R1）**

§4.16 R1 当前对标 Atlas/golang-migrate。[pgroll（Xata 出品，Go，~6500 stars，Apache-2.0）](https://www.bytebase.com/blog/top-open-source-postgres-migration-tools/) 使用 expand/contract 模式，通过**版本化视图**保持新旧 schema 同时有效，使新旧版本应用可并行运行——比 Atlas 的声明式 diff 更专注 PG 零停机场景。**比现有方法更好**：pgroll 的版本化视图机制使 §4.16 R5 双写期间的"新旧消费者共存"天然实现（不同消费者读不同版本视图），无需应用层 version 路由逻辑。另：[Sqitch](https://www.bytebase.com/blog/top-open-source-postgres-migration-tools/) 的"依赖驱动而非线性版本号"模型（声明 change B depends on A）特别适合复杂注册表 schema 演进——与 §4.15 DEPENDENCY_RESOLVE 的依赖图理念一致。**个人项目适用性**：高。Phase 2+ PG 迁移时 pgroll 是 R1 工具首选，Sqitch 作为复杂依赖场景备选。

**⑤ 依赖解析：PubGrub + 字典序最小拓扑（对标 §4.15 DEPENDENCY_RESOLVE）**

§4.15 当前用 Kahn's 算法做拓扑排序。[PubGrub（CDCL 冲突驱动子句学习）](https://github.com/pubgrub-rs/pubgrub) 被 uv/Poetry/SwiftPM/Dart pub 采用，提供人类可读的错误解释。**关键区分**：Kahn's 解决"依赖顺序"（O(V+E) 拓扑排序，处理静态 DAG），PubGrub 解决"版本选择"（NP-complete 约束求解，处理带版本范围的依赖如"策略 v1.2 依赖因子 v2.0+"）。**两者正交**——Kahn's 确定建表/迁移顺序，PubGrub 在版本化依赖场景（策略依赖特定版本因子）确定兼容版本组合。**个人项目适用性**：中-高。YAML 阶段无版本化依赖（所有 entry 引用最新版），Kahn's 足够；DB 阶段引入 `version_pin` 后，策略可能依赖因子 v2+，此时 PubGrub 比 Kahn's + 手动版本检查更优。另：[字典序最小拓扑排序 2026-05-24](https://spacecomplexity.ai/blog/topological-sort-algorithm/)（Kahn's + 优先队列，O(V log V + E)）是对 Kahn's 的最小确定性升级——每次选编号最小的入度 0 节点，获得确定性建表顺序（而非任意合法顺序），§4.15 construct_order 应升级为字典序最小版确保多次运行结果一致。

**⑥ Schema 治理：Data Contracts vs Schema Registry 分层（对标 §4.11 EVOLVE_SCHEMA / §4 原则 11）**

[Soda.io 2026-06-01](https://soda.io/fr/blog/data-contracts-vs-schema-registry) 明确区分两者职责：**Schema Registry 在发布时强制结构（写入路径保护）**，**Data Contract 在扫描时强制更广泛期望——质量、新鲜度、所有权（读取路径保护）**。**比现有方法更好**：§4.11 当前将 Schema 演进（兼容性模式）和数据契约（E13 语义漂移）混在一起讨论，Soda.io 的分层澄清了"注册表保护写入路径，契约保护读取路径"——§4 原则 11（Schema 演进兼容性）是写入路径保护，§4.7 E13（语义漂移检查）是读取路径保护，两者正交。[Confluent Data Contracts 2026 v8.3](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html) 的 **migration rules**（JSONata/CEL 表达式定义版本间数据转换规则）是处理破坏性变更的新机制——比 §4.11 的 Expand-Contract 三阶段更优雅（转换规则声明式定义，消费者自动应用）。**个人项目适用性**：高。YAML 阶段 Schema Registry = frontmatter + entry_schema 验证（写入路径），Data Contract = §4.7 E1-E13 审计（读取路径），migration rules = EVOLVE_SCHEMA 的 version migration 脚本。

**⑦ 策略上线：multigrid 三层 eval gate + 确定性流量分割（对标 §4.13 PROMOTE_ENTRY 渐进式部署）**

[multigrid 2026-08-08](https://dev.to/multigrid/canary-and-blue-green-deploys-for-model-changes-3i9c) 区分"代码部署"与"模型部署"——模型失败是**静默且分布式**的（不像代码 crash 立即可见）。提出三层 eval gate：① 离线 eval（任何流量前）；② 操作指标（首批 canary 请求：错误率、p95 延迟）；③ 质量指标（统计显著的业务指标对比）。**确定性流量分割**：`sha256(salt:user_id) % 100`，salt 用于避免第二次 rollout 复用相同不幸用户。**比现有方法更好**：§4.13 当前 shadow→canary→full 三阶段描述了"做什么"但缺"怎么判定每阶段通过"——multigrid 的三层 eval gate 给出了每阶段的具体判定标准（离线/操作/质量三层），确定性流量分割给出了 canary 分流的具体实现（避免随机分流的不公平）。另：[Flagger 2026-07-03](https://hogin.pro/posts/flagger-canary-auto-rollback/)（CNCF/Flux 生态）通过 `Canary` CR 自动化渐进式交付（10%→30%→50%→100% 每步 MetricTemplate 分析，超范围自动 abort+100% 回滚）——比 §4.13 的"人工确认"更自动化，适合 K8s 部署的策略服务。**个人项目适用性**：高。canary 阶段的 `sha256(salt:strategy_id) % 100` 确定性分流可直接用于 miniQMT 资金分配（5% canary 资金固定流向特定标的），三层 eval gate 映射为 ①回测验证(G1-G2) ②操作指标(滑点/延迟/拒单率) ③质量指标(Sharpe/DD paired t-test)。

**⑧ 血缘追踪：Feast 原生 OpenLineage 集成（对标 §4 原则 9 版本可复现性 / §10 数据来源映射）**

[Feast 2026-01-29](https://feast.dev/blog/feast-openlineage-integration/) 原生支持 OpenLineage 集成——在 `feast apply`（注册表变更）和 `feast materialize`（特征物化）时自动发出血缘事件，无需代码改动，只需 `feature_store.yaml` 中 `openlineage: enabled: true`。自动追踪 DataSources → FeatureViews → FeatureServices 完整链路，在 Marquez UI 可视化。**比现有方法更好**：§4 原则 9 当前用 `code_commit` + `source_uri` + `transform_script_hash` + `labeler_id` 四字段间接覆盖血缘，Feast+OpenLineage 提供**自动化端到端血缘追踪**（无需手动维护四字段）。[Snowflake 2026-07-28](https://www.snowflake.com/en/blog/engineering/lakehouse-data-governance-interoperability/) 进一步确认 OpenLineage 已成为跨平台血缘交换的**行业事实标准**。[CSDN 2026-07-26 AI就绪数据空间](https://blog.csdn.net/PoliSeed/article/details/160022028) 提出"Feature Schema + Data Contract 双轨治理"四维能力模型（可审计/可追溯/可干预/可推理），注册时嵌入业务语义与质量约束。**个人项目适用性**：高。Phase 2+ DB 迁移后若采用 Feast 做 feature store，`pip install feast[openlineage]` + Marquez Docker 即可获得企业级血缘追踪，零代码改动。YAML 阶段 §4 原则 9 四字段足够，OpenLineage 是 DB 阶段的自动化升级。

> ⚠️ **v1.12.0 补充总结**：8 项对标补充覆盖衰减检测(双曲模型+BOCPD)/漂移检测(Wasserstein)/迁移工具(pgroll)/依赖解析(PubGrub+字典序)/Schema治理(Data Contracts分层)/策略上线(multigrid三层eval)/血缘追踪(OpenLineage) 七大领域。**MVP 阶段无阻塞**——所有补充均为 Phase 1.5+ 或 DB 阶段的增强项，YAML 阶段现有 12 算法体系已完整闭环。**关键升级路径**：① §4.8 DECAY_SCAN 加双曲衰减模型估 λ + BOCPD 第4检测器；② §4.7 E11 data_quality_policy.drift_method 扩展 wasserstein；③ §4.15 construct_order 升级字典序最小拓扑；④ §4.16 R1 工具首选 pgroll；⑤ §7.2 回测过拟合五方法（+MTC）schema 预留 mtc_method/mtc_pvalue/mtc_survived 三字段。

### 4.18 版本差异算法（DIFF_ENTRY，v1.13.0 新增，横切查询）

§4.9 EVOLVE_ENTRY 创建版本快照、§4.11 EVOLVE_SCHEMA 判定兼容性、§4.13 PROMOTE_ENTRY 对比候选 vs baseline——三者都需要"对比两个版本差异"但 v1.12.0 及之前**无统一 diff 算法**：PR review 时人工肉眼比 YAML，EVOLVE_ENTRY 的 change_type 分类靠人工判断，EVOLVE_SCHEMA 的 BACKWARD/FORWARD 兼容性判定无机器可读输入。本算法填补"版本对比"只读查询缺口，产出结构化变更分类 → 直接驱动 semver bump 决策（消除"这是 major 还是 minor？"的人工争议）。对标 [IETF netmod YANG Schema Comparison draft-ietf-netmod-yang-schema-comparison-07 2026-05-05](https://datatracker.ietf.org/doc/html/draft-ietf-netmod-yang-schema-comparison-07)（规范化 schema 对比算法，产出结构化变更清单 + revision-label/semver 选择，IETF netmod WG，expires 2026-11-06）+ [AI Agent Schema Diff 2026-04-13](https://blog.csdn.net/VarLens/article/details/160111891)（AST 语义 diff vs BLAKE3 字节哈希双策略：AST 模式识别重命名/格式化/注释变更的逻辑等价，byte-hash 模式毫秒级零容忍）+ [schema.biz Breaking-Change Detector 2026-04-29](https://schema.biz/api/breaking-changes/)（Breaking/Safe/Warning 三桶分类 + 逐变更修复提示 + semver 映射）。

```
算法 DIFF_ENTRY(registry_id, entry_id, version_a, version_b):
  输入: entry_id, 两版本号 version_a/version_b（YAML 阶段=git commit hash；DB 阶段=version 字段值）
  输出: change_report{additions[], modifications[], removals[], breaking_changes[],
                      semver_delta, change_class, affected_dependents[]}
  约束: 只读查询算法——不修改任何 entry 状态/版本，可任意阶段调用（横切）

  entry_a = load_version(entry_id, version_a)
  entry_b = load_version(entry_id, version_b)

  # ── Step 1: 字节级快判（毫秒级 gate）──
  # 对标 AI Agent Schema Diff: BLAKE3 byte-hash 模式，零容忍，先判"有没有变"
  if blake3(entry_a) == blake3(entry_b):
    return {change_class: "identical", semver_delta: "none"}
  # 字节不同才进入语义分析（避免无变更时浪费 AST 计算开销）

  # ── Step 2: 字段级 diff（三分类）──
  # 对标 IETF YANG Schema Comparison: 结构化变更清单（additions/modifications/removals + node 路径）
  fields_a = set(entry_a.keys())
  fields_b = set(entry_b.keys())
  additions = fields_b - fields_a        # 新增字段（默认 BACKWARD 兼容）
  removals = fields_a - fields_b          # 删除字段（BREAKING，除非有默认值）
  modifications = {f: (entry_a[f], entry_b[f]) for f in fields_a & fields_b if entry_a[f] != entry_b[f]}

  # ── Step 3: 语义分类（区分 metadata / schema_sig / code_ref / status）──
  # 对标 §4.9 EVOLVE_ENTRY change_type 六分类（metadata/schema_sig/code_ref/status/additive/breaking）
  # 对标 schema.biz 三桶: Breaking / Safe(additive) / Warning
  metadata_fields = {description, tags, ttl, owner, name_zh, aliases}      # metadata-only
  schema_sig_fields = {formula, params, inputs, outputs, entry_schema}     # schema-significant
  code_ref_fields = {code_path, code_commit, module_id, doc_ref}           # code-reference
  for each (field, old_val, new_val) in modifications:
    if field in metadata_fields:
      classify as "metadata_only"        # §4 原则9: 原地更新不建版本
    elif field in schema_sig_fields:
      classify as "schema_significant"   # 触发版本快照（§4.9 EVOLVE_ENTRY）
    elif field in code_ref_fields:
      classify as "code_ref_change"      # 触发版本快照
    elif field == "status":
      classify as "lifecycle_transition" # delegate §4.9/§4.10/§4.13
    elif field == "version":
      classify as "version_metadata"     # 版本号本身变更，不递归

  # ── Step 4: 兼容性判定 → semver bump 映射 ──
  # 对标 IETF YANG: 变更清单输出驱动 revision-label/semver 选择，消除"major 还是 minor?"争议
  # 对标 schema.biz: Breaking→MAJOR / Safe(additive)→MINOR / Warning→PATCH
  has_breaking_removal = any(f not in entry_b.get("defaults", {}) for f in removals)
  has_breaking_modification = any(m.classify == "schema_significant" and is_type_change(m) for m in modifications)
  only_metadata = all(m.classify == "metadata_only" for m in modifications) and not additions and not removals

  if has_breaking_removal or has_breaking_modification:
    breaking_changes = [f for f in removals if f not in entry_b.get("defaults", {})] + \
                       [m.field for m in modifications if m.classify=="schema_significant" and is_type_change(m)]
    semver_delta = "MAJOR"               # 1.x → 2.0（§4.11 EVOLVE_SCHEMA breaking 走 Expand-Contract）
    change_class = "breaking"
  elif only_metadata:
    semver_delta = "PATCH"               # 原地更新，不建版本（§4 原则9）
    change_class = "metadata_only"
  elif additions or modifications:        # additive 或 schema_sig/code_ref 变更
    semver_delta = "MINOR"               # 1.0 → 1.1（BACKWARD 兼容）
    change_class = "additive"
  else:
    semver_delta = "PATCH"
    change_class = "safe"

  # ── Step 5: 依赖方影响提示（breaking 变更时）──
  # 对标 §4.15 DEPENDENCY_RESOLVE.transitive_deps（reverse 方向：谁依赖我）
  # 对标 §4.9 EVOLVE_ENTRY Step4 依赖方影响分析 + §4.10 RETIRE_ENTRY 级联响应
  affected_dependents = []
  if change_class == "breaking":
    affected_dependents = DEPENDENCY_RESOLVE(
      operation="transitive_deps", entry_id=entry_id, direction="reverse")
    # 返回所有反向依赖方（如因子变更→依赖该因子的策略列表）

  return change_report  # 供 EVOLVE_ENTRY Step1(变更分类)/EVOLVE_SCHEMA Step2(兼容性)/PR review 使用
```

**semver bump 映射表**（对标 IETF YANG revision-label + schema.biz 三桶）：

| 变更类型 | 字段示例 | semver_delta | change_class | 处理路径 |
|---|---|---|---|---|
| 删除字段（无默认值）/ 类型变更 | 删 formula 字段、params int→str | MAJOR | breaking | §4.11 EVOLVE_SCHEMA Expand-Contract |
| 新增字段 / schema_sig 值变 | 加 plateau_score 字段、formula 改 | MINOR | additive | §4.9 EVOLVE_ENTRY 版本快照 |
| code_ref 变更 | code_path/code_commit 更新 | MINOR | additive | §4.9 EVOLVE_ENTRY 版本快照 |
| metadata-only | description/tags/owner 改 | PATCH | metadata_only | §4.9 EVOLVE_ENTRY 原地更新（不建版本） |
| status 变更 | candidate→active | — | lifecycle | delegate §4.13/§4.10 |
| 无变更 | 字节哈希相同 | none | identical | 无操作 |

> ⚠️ **个人项目适用性**（避免过度工程）：YAML 阶段 git diff 天然提供字节级 diff（Step1 的 BLAKE3 用 `git diff --quiet` 替代），Step2-3 的字段级分类是**纯 Python dict 比较**（<50 行代码），Step4 semver 映射是一张查表。**不需要 AST 语义分析**——YAML 阶段无代码重命名等逻辑等价场景，字段值就是字符串/数字直接比较。AST 语义 diff（对标 AI Agent Schema Diff）是 DB 阶段 + 代码资产（如 formula 表达式 AST）的增强项，YAML 阶段字段值比较足够。**MVP 实现**：`git diff` + dict diff + 查表三步即可，无需第三方库。DB 阶段升级为 SQL row diff + AST（formula 表达式）语义分析。

### 4.19 第二轮缺口审计与对标（v1.13.0 新增）

v1.12.0 §4.17 补充了 8 项第一轮研究对标。本轮（v1.13.0）针对"12 算法体系是否仍有施工环节流程算法缺口"做第二轮全网搜索（2026-08-10），覆盖 10 个候选缺口领域，**逐项映射现有覆盖或显式 defer**——避免无节制新增算法导致过度工程（project_memory 过度工程处理原则），同时确保缺口有据可查、defer 决策有理可循。

**10 缺口领域审计表**：

| # | 缺口领域 | 2026 研究发现 | 现有覆盖 | 决策 |
|---|---|---|---|---|
| 1 | 候选提案（ideation→candidate） | [tapps-brain FEATURE_FEASIBILITY_CRITERIA 2026-03-27](https://github.com/wtthornton/tapps-brain/blob/main/docs/planning/FEATURE_FEASIBILITY_CRITERIA.md)（10 准则 0-5 评分 priority_score 公式，hard-gate 失败则 re-scope）+ [ict-engine #192 2026-07-14](https://github.com/Undermybelt/ict-engine-release/issues/192)（三层 evidence→projection→consumption 因子候选 onboarding，discrimination record + held-out conclusion） | §4.5 CONSTRUCT_REGISTRY Step1-3（真源反查→编号→schema 填充）覆盖从已有代码/文档创建 candidate | **DEFER**：个人项目新因子先编码再注册（CONSTRUCT_REGISTRY Step1 grep 新代码即覆盖）。10 准则评分对单用户过度——形式化 feasibility scorecard 适合团队防冗余，个人靠风险优先原则 + MVP 自然过滤。**DB 阶段若因子>100 可选启用** priority_score 排序施工优先级 |
| 2 | 跨注册表引用验证 | [sigma-guard 2026-05-09](https://pypi.org/project/sigma-guard/)（sheaf cohomology 矛盾检测，数学证明局部声明能否 glue 成全局一致，产出 proof receipt）+ [SHACL-DS arXiv:2605.10540 2026-05-11](https://arxiv.org/html/2605.10540v1)（named-graph 感知 SHACL，per-graph provenance 错误归因） | §4.6 FK 矩阵（26 条 FK）+ §4.7 E4 FK 引用完整性 + E8 循环引用检测 | **DEFER**：sheaf cohomology 对 YAML 过度工程（数学优雅但单用户项目用 dict 反查足够）。SHACL-DS 是 RDF/SPARQL 生态，与本项目 YAML/PG 架构不匹配。E4 + §4.6 矩阵已覆盖 FK 完整性，**DB 阶段 PG 外键约束 + E4 复跑**即可 |
| 3 | 变更通知/传播 | [DataHub MCL 2026-03-21](https://blog.csdn.net/gitblog_00819/article/details/151257185)（MetadataChangeLog Kafka 事件，MAE Consumer 同步搜索索引+关系图谱）+ [Apicurio EDA 2026-07-27](https://github.com/Apicurio/apicurio-registry/pull/8710)（lifecycle webhook，按 artifact type 路由：AVRO→Slack, OPENAPI→CI/CD）+ [CAMEL-24172 2026-07-16](https://issues.apache.org/jira/browse/CAMEL-24172)（Camel route source `from("apicurio-registry://...")`） | §4.9 EVOLVE_ENTRY Step4 依赖方影响分析 + §4.13 PROMOTE_ENTRY `notify_portfolios_using` + §4.10 RETIRE_ENTRY 级联响应 | **COVERED 内联**：YAML 阶段通知=git commit 触发的 PR review（依赖方在 PR 中 @review）。DB 阶段 Apicurio EDA webhook 模式可复用（type-aware routing 映射：factor 变更→策略 review，strategy 变更→portfolio 通知）。**独立通知算法对单用户过度**——内联在 EVOLVE/RETIRE/PROMOTE 足够 |
| 4 | 反向血缘查询 | [TIN arXiv:2601.04722 2026-01](https://arxiv.org/pdf/2601.04722)（Temporal Interaction Networks，5 查询类型 backward/forward/temporal/flow/versioning + vertex-state-sequence 索引免重建历史图）+ [OpenMetadata 2026-07-31](https://blog.csdn.net/gitblog_00401/article/details/155960355)（`analyze_impact(change_entity, depth=3)` 有界深度下游遍历） | §4.15 DEPENDENCY_RESOLVE `transitive_deps`（传递依赖链）+ `impact_range`（变更影响范围） | **COVERED**：§4.15 已实现反向血缘查询（transitive_deps direction=reverse = 谁依赖我）。TIN 的 vertex-state-sequence 索引是流式系统大规模优化（super-linear 图），YAML 阶段 12 表 <100 entry 用 Kahn's BFS 足够。**DB 阶段 entry>1000 可选** TIN 索引 |
| 5 | 退役条目 GC | [openclaw #120922 2026-08-09](https://github.com/openclaw/openclaw/pull/120922)（Doctor deprecation registry：deprecated/removal-pending/removed 三态 + `removeAfter` deadline + `--as-of` 检查器，区分"应删"vs"已排队"）+ [Docker registry GC 2026-07-11](https://www.codegenes.net/blog/docker-registry-2-0-how-to-delete-unused-images/)（两阶段：read-only quiesce→mark-sweep 防竞态） | §4.10 RETIRE_ENTRY（retired 保留审计，物理删除需满1年+ARCH审批） | **DEFER 但记录模式**：YAML 阶段 retired entry 留在 git（git 历史即审计），物理删除=git rm（手动+ARCH 审批已足够）。Doctor `removeAfter` deadline 模式 **DB 阶段可复用**（retired 满期自动标 removal-pending，避免遗忘）。两阶段 GC（read-only quiesce）是 DB blob 存储场景，YAML 无竞态 |
| 6 | 复活/恢复（retired→active） | [cinatra #1837 2026-07-19](https://github.com/cinatra-ai/cinatra/issues/1837)（R3 同步 restore：reactivation 必须在 restore 操作内同步完成，失败则 abort 不留 active+dead claims）+ [IETF regext RGP restore 2026-05-11](https://datatracker.ietf.org/doc/draft-ietf-regext-rfc3915bis/)（redemptionPeriod + 两步 restore request + restore report，强制人工撰文理由才完全恢复） | §4.10 RETIRE_ENTRY 仅正向（active→deprecated→retired），**无反向路径** | **NOTE 而非新算法**：状态翻转（retired→deprecated→active）本质是 EVOLVE_ENTRY 的 status 变更（lifecycle_transition 类，§4.18 Step3）。cinatra R3 同步性原则可复用（恢复须同步重激活依赖，不留死引用）。RGP restore report（人工撰文理由）**DB 阶段可复用**为退役恢复的审计要求。**YAML 阶段不建独立 RESTORE_ENTRY**——避免算法增殖，retired→active 走 EVOLVE_ENTRY status 分支 + 手动 ARCH 审批（project_memory: 个人项目避免过度工程） |
| 7 | 版本 diff（两版本对比） | [IETF YANG Schema Comparison 2026-05-05](https://datatracker.ietf.org/doc/html/draft-ietf-netmod-yang-schema-comparison-07) + [AST/byte-hash 双策略 2026-04-13](https://blog.csdn.net/VarLens/article/details/160111891) + [schema.biz 三桶 2026-04-29](https://schema.biz/api/breaking-changes/) | **无**（v1.12.0 缺口） | **ADD：§4.18 DIFF_ENTRY**（本轮新增，填补唯一硬缺口） |
| 8 | 注册表健康监控 | [noopsschool catalog SLI/SLO 2026-02-15](https://noopsschool.com/blog/metadata-catalog/)（M1 uptime 99.9% / M2 freshness <1h / M3 query latency / M4 change-detection lag，catalog 本身当 SRE 服务）+ [acceldata 2026-04-11](https://www.acceldata.io/blog/metadata-quality-freshness-and-coverage-the-enterprise-evaluation-guide)（ownership completeness + change-detection lag + asset-coverage ratio 三指标） | §4.7 AUDIT_REGISTRY（point-in-time 审计，非持续监控） | **DEFER 但记录指标**：YAML 阶段定期跑 AUDIT_REGISTRY（如每周 cron）= 持续监控的轻量替代。catalog SLI/SLO（freshness lag = DDL 事件→catalog 更新的时间差）**DB 阶段可复用**为 registry 健康指标。YAML 阶段 git commit timestamp = 天然 freshness 标记，无需额外 SLI |
| 9 | 原子批量导入 | [Lance BatchCommitTables 2026-06-18](https://github.com/lance-format/lance/discussions/6775)（staged manifests + put-if-not-exists 原子翻可见性，K 表全有或全无）+ [Apicurio multi-table transaction 2026-03-30](https://github.com/Apicurio/apicurio-registry/issues/7670)（`POST /transactions/commit` 多 artifact 版本原子创建，SQL/KafkaSQL/GitOps 四后端各异实现）+ [Doris 2PC 2026-07-29](https://blog.csdn.net/juniperhan/article/details/159720535)（prepare→publish + UUID label 幂等） | §4.5 CONSTRUCT_REGISTRY Step1-3（批量创建，但无显式原子性） | **COVERED by git**：YAML 阶段 git commit = 天然原子批量（一个 commit 含多 entry 变更，全有或全无，`git commit --amend`/revert 回滚）。DB 阶段 Apicurio multi-table transaction 模式可复用（PG 单事务包裹多表 upsert）。**YAML 阶段无需额外算法**——git commit 原子性已覆盖 |
| 10 | 搜索与发现（找已有因子/策略） | [Algolia Dynamic Facets 2026-07-21](https://www.algolia.com/about/news/algolia-launches-dynamic-facets)（AI 行为驱动 facet 实时重排序，10-15% 点击提升）+ [base14 metric registry 2026-01-19](https://docs.base14.io/blog/metric-registry/)（3700+ 指标自动提取 + repo/file/commit provenance + trust level 区分官方 vs 推断） | grep / Select-String | **DEFER**：YAML 阶段 12 表 <100 entry，`Select-String` + §4.15 DEPENDENCY_RESOLVE 足够查找。Algolia facets 是 web-scale 搜索（万级 entry）。base14 自动提取 + provenance **DB 阶段可复用**（因子定义 provenance = 哪个 notebook/commit）。**YAML 阶段不建搜索算法**——过度工程 |

> ⚠️ **v1.13.0 缺口审计总结**：10 缺口领域中 **1 项硬缺口已补**（#7 版本 diff → §4.18 DIFF_ENTRY）、**4 项已覆盖**（#3 通知内联 / #4 反向血缘=§4.15 / #9 原子批量=git commit / #2 FK 验证=§4.6+E4）、**5 项 DEFER 并记录 DB 阶段升级路径**（#1 候选提案 / #5 GC / #6 复活 / #8 健康监控 / #10 搜索）。**核心结论：12 生命周期算法 + 1 横切查询算法（DIFF_ENTRY）= 13 算法体系已完整闭环，无施工阻塞缺口**。所有 DEFER 项均为 DB 阶段（entry>500/exp>5000 触发 §4.16 MIGRATE_REGISTRY 后）的增强项，YAML 阶段现有体系足够——符合 project_memory 过度工程处理原则（YAML+git 足够时不引入 DB 级基础设施）。**关键 DB 阶段升级备忘**：① #5 Doctor removeAfter deadline 自动标 removal-pending；② #6 RGP restore report 退役恢复审计；③ #8 catalog SLI/SLO freshness lag 指标；④ #10 base14 自动提取+provenance trust level；⑤ #1 priority_score 施工优先级排序。

### 4.20 A 股 2026 年 7 月监管变更影响（v1.14.0 新增，实盘合规 MUST）

2026-08-10 全网搜索发现 **两项 2026 年 7 月生效的 A 股监管变更**，直接影响 12 注册表中 5 个表的 schema/参数——这是实盘合规红线（非可选增强），MUST 在 P1-B execution_algo/risk_limit 施工前纳入。

**① 交易规则 2026 年修订（2026-07-06 生效，对标 [上交所 上证发〔2026〕41号 2026-04-24 发布](https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20260424_10816492.shtml) + 新华社/人民日报 2026-07-06 报道）**：

| 变更项 | 旧规则 | 2026 新规则 | 影响注册表 | schema/参数影响 |
|---|---|---|---|---|
| 主板 ST/*ST 涨跌幅 | 5% | **10%**（与普通主板一致） | universe / risk_limit | universe 的 filter_rules（ST 池风险筛选）+ risk_limit 单日可移动范围翻倍（5%→10% 影响 stop_loss/kill_switch 阈值校准） |
| 盘后固定价格交易 | 仅科创板/创业板 | **扩至全部 A 股 + 沪深 ETF**（15:05-15:30） | cost_model / execution_algo | execution_algo 新增 `after_hours_fixed_price` 时段（收盘价精确成交，无滑点）；cost_model 该时段 slippage=0 |
| SSE 基金收盘机制 | 连续竞价 | **收盘集合竞价**（14:57-15:00，最后 3 分钟限价单不可撤） | benchmark / execution_algo | benchmark 收盘价序列来源变化（连续→集合）；execution_algo 尾盘策略须适应最后 3 分钟不可撤单 |
| 创业板做市商制度 | 无 | **引入做市商** | execution_algo | 创业板流动性 profile 改善（做市商提供双边报价），TWAP/VWAP 拆单冲击成本下降 |
| 创业板大宗交易确认 | 盘后 | **盘中实时**（9:30-11:30/13:00-15:30，对齐科创板） | execution_algo | 大宗交易执行时序变化，可盘中确认而非等盘后 |

**关键确认**：印花税（万5/卖出单边）、过户费（万0.1/沪深双向）、最低 100 股整手 **2026 年未调整**——§5.3 cost_model_registry 现有登记费率正确，无需修改。

**② 程序化交易管理实施细则全面执行（2026-07-07 生效，对标 [CSDN 2026-07-28/08-08 更新](https://blog.csdn.net/syp1110/article/details/163276625) + [licai.cofool 2026-08-04](https://licai.cofool.com/ask/qa_7416984.html)）**：

| 硬约束 | 阈值 | 影响注册表 | schema/参数影响 |
|---|---|---|---|
| 高频交易认定 | **每秒申报+撤单合计 ≥ 15 笔**（旧 300/秒，收紧 20 倍）**或** 单日全市场申报撤单 ≥ 20,000 笔 | execution_algo / strategy | execution_algo schema MUST 新增 `max_orders_per_sec`（默认 ≤14，留 1 笔余量）+ `max_daily_orders`（默认 ≤19,000）；超阈值策略须标 `is_hft=True` 并触发报备 |
| 单日撤单率上限 | **≤ 15%**（硬上限） | execution_algo / risk_limit | execution_algo MUST 新增 `cancel_rate_limit: 0.15`；risk_limit 的 cancel_rate 监控从"成本指标"升级为"合规红线"（40_execution_broker v2.6.0 的 CancelRateGuard 须对齐此阈值） |
| 每笔报单最短停留 | **≥ 50 微秒** | execution_algo | 禁止 sub-50µs 闪单/虚假报价；execution_algo 拆单间隔下限 50µs |
| 通道平权 | 暂停新设独立交易单元 | data_asset / execution_algo | 无新通道，现有通道公平调度 |

> ⚠️ **高频阈值核实说明（v1.15.0 补）**：2026-08-10 第四轮搜索发现中基协 2026-07-27 研报仍引用"300 笔/秒"——经多方核实（[东方财富 2026-07-08](https://caifuhao.eastmoney.com/news/20260708102539948920960) + [雪球 2026-07-08](https://xueqiu.com/1333898802/399079985) + [licai.cofool 2026-08-04](https://licai.cofool.com/ask/qa_7416984.html)）系**研报撰写时间差导致的旧规引用**：旧规 300 笔/秒（2025-07-07 施行），新规 15 笔/秒分两阶段落地（2026-04-07 第一阶段收紧 + 2026-07-07 全面完整落地）。本表"15 笔/秒"为**现行有效阈值**，中基协研报"300 笔/秒"作废。

**③ 局域网行情通道关闭 + 交易网关管理指引（2026-07-31/2026-08-31 生效，v1.15.0 新增，实盘合规 MUST）**

对标 [新浪财经 2026-07-28](https://cj.sina.cn/article/norm_detail?froms=ttmp&url=https%3A%2F%2Ffinance.sina.com.cn%2Fstock%2Festate%2Fintegration%2F2026-07-28%2Fdoc-inikkhkm3121470.shtml) + [东方财富 2026-08-05](http://finance.eastmoney.com/a/202608053832918762.html) + [第一财经 2026-08-05](http://finance.eastmoney.com/a/202608053832922855.html) + [证券时报 2026-07-28](https://stcn.com/article/detail/4044080.html)。**v1.14.0 §4.20 漏掉的第三项实盘合规红线**——2026-08-10 第四轮搜索发现，2026-07-31 晚间交易所机房内局域网交易行情线路正式关闭，统一切广域网，这是"基础设施平权"的物理层收口，直接影响 execution_algo 的延迟建模假设。

| 时间节点 | 事件 | 影响注册表 | schema/参数影响 |
|---|---|---|---|
| 2026-06 | 上交所《强化参与者交易业务单元管理的通知》+ 北交所禁止独享交易网关，存量 3 个月整改 | data_asset / execution_algo | 严禁独享网关/独立交易单元/更低延迟/优先报单/专属带宽；至少 10 账户共用一个交易单元 |
| 2026-07-28 | 券商收到《广域网交易行情线路技术要求》通知 | — | 通知下发，过渡期开始 |
| **2026-07-31 晚间** | **原局域网交易行情线路正式关闭，统一切广域网** | execution_algo / cost_model / data_asset | 行情接收链路时延从局域网 0.3-0.8ms 抬升到广域网 1.2-2ms；微秒级抢跑策略物理外挂失效 |
| 2026-08-31 | 《交易网关管理指引（试行）》施行 | data_asset / execution_algo | 通道平权硬约束生效；托管服务器搬离交易所机房 |
| 2026-08 内（待定） | 深交所切换广域网（截至 8-5 未完成） | execution_algo | 沪市已切，深市待切，跨市场策略须适应两市场时延差异期 |

**关键硬约束**：广域网线路双向时延**不得低于 2 毫秒**（"不许太快"地板，含存量及新增线路）——这是监管首次为速度设地板（而非天花板），彻底终结"机房托管+局域网"的物理低延迟特权。注意：本次仅关**行情接收**链路，**交易报盘专线暂未同步关闭**，资金实力强的机构仍可优化路由压低抖动，但微秒级抢跑窗口已大幅压缩。

**对 12 注册表施工的影响（P1-B 前必改）**：
- **execution_algo_registry schema 新增 4 字段**：`max_orders_per_sec`（int, 默认 14）/ `max_daily_orders`（int, 默认 19000）/ `cancel_rate_limit`（float, 默认 0.15）/ `min_order_interval_us`（int, 默认 50）/ `is_hft`（bool）/ `after_hours_eligible`（bool, 盘后固定价格交易资格）+ **v1.15.0 补 2 字段**（③局域网关闭）：`latency_floor_ms`（float, 默认 2.0，广域网双向时延地板）/ `network_type`（enum: wan/lan，默认 wan，标记行情接入方式）
- **risk_limit_registry**：cancel_rate 从运营指标升级为合规红线（≤15%），kill_switch 须含 cancel_rate_breach 触发
- **universe_registry**：ST/*ST 池的涨跌停从 5% 更新为 10%，影响打板策略（STR-DABAN-001）连板梯队筛选——ST 股 10% 涨跌停使"涨停"判定阈值变化
- **cost_model_registry**：新增 `after_hours_fixed_price` 时段（slippage=0，精确收盘价），现有 3 条 entry 须补 after_hours 字段；**v1.15.0 补**（③局域网关闭）：高频时段 slippage 系数上调（盘口变薄，买卖价差走阔），`slippage_regime` 字段区分 pre/post_20260731 两套系数
- **benchmark_registry**：SSE 基金收盘价来源标注（集合竞价 vs 连续），影响 close-to-close 收益序列
- **data_asset_registry**（v1.15.0 补，③局域网关闭）：行情数据源 entry 须补 `latency_profile`（广域网 1.2-2ms vs 旧局域网 0.3-0.8ms）+ `colocation_eligible`（bool, 默认 false，托管服务器已搬离交易所机房）字段

> ⚠️ **个人项目适用性**：这些是**实盘合规硬约束**（非过度工程），MUST 在 P1-B execution_algo 施工时纳入。miniQMT 单账户下单频率天然远低于 15 笔/秒（个人策略多数秒级-分钟级），cancel_rate 15% 对低频策略无压力，但 schema 字段 MUST 预留（regulatory compliance 字段缺失=实盘违规风险）。**关键**：40_execution_broker v2.6.0 的 CancelRateGuard 须对齐 15% 阈值（project_memory 已登记 P0 gap 已闭合，须验证阈值=0.15）。**v1.15.0 补**：③局域网关闭对个人项目影响**极小**——个人策略持仓周期天/周级，0.3-0.8ms vs 1.2-2ms 的时延差对天级策略收益影响约等于零，但 `latency_floor_ms`/`network_type` schema 字段 MUST 预留（合规底线），实际延迟建模校准=Phase 1.5+（仅微秒级高频策略须精确建模，个人项目无此类策略）。

### 4.21 第三轮研究对标补充（v1.14.0 新增）

v1.12.0 §4.17 + v1.13.0 §4.19 覆盖第一/二轮。本轮（v1.14.0）针对 10 个新领域（A股监管/WFO/因子选择/滑点预测/模型风险/集成策略/流动性/ regime/feature store/回测框架）做第三轮全网搜索（2026-08-10），筛选 7 项高价值对标（剔除已覆盖项），分领域补充。

**① 模型风险管理：SR 26-2 替代 SR 11-7（对标 strategy/experiment/risk_limit 治理）**

[美联储 SR 26-2 + OCC Bulletin 2026-13 2026-04-17](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf)（OCC+Fed+FDIC 联合发布，15 年来最大 MRM 变革）**废止 SR 11-7/SR 21-8/OCC 2011-12 等全部旧规**。关键变化：① ** narrower "model" 定义**——排除简单算术/确定性规则过程，简单 chart_pattern/universe 筛选可移出正式 MRM 范围；② **风险分层 materiality tiering 替代统一年度验证**——低 materiality 模型仅需识别+性能监控，高 materiality 需全 oversight；③ **生成式 AI/agentic AI 完全 carve-out**——12-18 月内单独出 AI 模型风险 RFI。**个人项目适用性**：中。个人项目非银行机构（<$30B 阈值），SR 26-2 不直接适用，但 **materiality tiering 思路可借鉴**——strategy_registry 的 `lifecycle_status` 已隐含分层（candidate→active→retired），可显式加 `materiality_tier`（high=实盘资金决策/medium=回测验证/low=研究探索）驱动验证频率。AI carve-out 印证 project_memory"Mamba/SSM 和 Autoencoder-Gated+SAC RL 远期不采纳"——LLM/agent 策略须单独治理标记。

**② 回测框架：NautilusTrader 替代 Backtrader（对标 experiment/execution_algo/cost_model）**

[bullalert 2026-05-18](https://bullalert.ai/blog/best-python-backtest-engines-2026) + [pickuma 2026-05-23](https://pickuma.com/for-dev/python-backtesting-frameworks-backtrader-vectorbt-zipline-2026/)：2026 年 NautilusTrader（Rust 核心/Python API 事件驱动）已取代 Backtrader 成为严肃量化推荐——Backtrader 进入长期维护（无新功能/bug 积累），NautilusTrader 订单簿级模拟（队列位置/部分成交/交易所微观结构）+ **同策略代码 paper-to-live**（无需 ib_async 重写）。[LedgerMind 2026-04-16 12 平台对比](https://theledgermind.com/backtesting-framework-comparison-2026/) 实测 68% 策略 paper→live 退化，主因 look-ahead(31%)/survivorship(23%)/overfitting(19%)/滑点建模不足(15%)。**个人项目适用性**：高。experiment_registry schema 的 `backtest_framework` 字段（§7.2）MUST 记录框架+偏误检测能力；NautilusTrader 的 paper-to-live parity 直接支持 §4.13 PROMOTE_ENTRY 的 shadow 模式（同代码模拟盘 vs 实盘）。**MVP 决策**：MVP 用现有框架，Phase 1.5+ 评估 NautilusTrader 迁移（其订单簿级模拟提升 cost_model 保真度——部分成交/队列位置）。

**③ 因子选择：Double-Selection LASSO（对标 factor_registry 正交化）**

[arXiv:2601.06499v2 2026-05-21](https://arxiv.org/html/2601.06499v2)（Du/Walter/Ulrich, KIT）：用 **double-selection LASSO** 控制 151 个已知基本面因子后，从 191 个信号库中隔离出 17 个非冗余短期价量/微观结构信号——标准 LASSO 给出有偏系数（omitted variable bias），double-selection 提供有效推断。**比现有方法更好**：factor_registry 登记新因子前，须用 double-selection 对已知 style 因子正交化，确认"新 alpha"非已有因子的冗余表达。**个人项目适用性**：高。Phase 1.5+ factor_registry 施工时，新因子登记 MUST 附 double-selection 正交化结果（vs 仅 IC/IR），避免登记冗余因子。

**④ 滑点预测：华创 LightGBM 三标签冲击模型（对标 cost_model A 股专用）**

[华创证券 2026-03-20 研报](https://m.hibor.com.cn/wap_detail.aspx?id=aca7f720f2e1cea4853568df7034b748)：针对 A 股真实订单数据建 **3 个独立 LightGBM 模型**（瞬时/临时/永久冲击），R²=0.4418/准确率 84.67%，再用"LightGBM + 显式回归"混合修正 ML 极端样本预测失真。三时间尺度驱动因子不同（瞬时=价格+价差；临时=市占率；永久=全天市占率+活跃度）。**比平方根律更好**：A 股散户驱动订单流与美股（平方根律校准基础）微观结构不同，三标签分解 + ML 捕获 regime 尾部。**个人项目适用性**：中。MVP 用 square_root(coeff=0.1)（个人小单无冲击）足够；Phase 1.5 AUM 增长后，cost_model_registry 新增 `CST-ASTOCK-003` 用 LightGBM 三标签模型（对标 §5.3 待定问题 C1 的 power_law(0.7) 替代选项升级）。

**⑤ Regime 检测：AH-HMM 元 regime 层（对标 strategy regime-gating）**

[MDPI JRFM vol19 article15 2026](https://mdpi-res.com/d_attachment/jrfm/jrfm/jrfm-19-00015/article_deploy/jrfm-19-00015.pdf)（Tampouris & Dritsaki）：**Adaptive Hierarchical HMM** 在标准 HMM 之上加不可观测 **meta-regime 层**（低/高不确定性，VIX 近似），每个 meta-regime 有独立 bull/bear/turbulent 转移矩阵——转移动态本身随结构环境适应，捕获 GFC/COVID/2022 紧缩等固定转移 HMM 漏掉的 episode。**比 HSMM 更好**：HSMM 建模 dwell-time 分布但转移机制固定；AH-HMM 使转移*过程* regime-条件化。[AGasthya283 2026-07-19](https://github.com/AGasthya283/Hidden_Markov_Models) 实证 HSMM+meta-context IoU 0.73→0.93，误报率 75.5%→4.0%。**个人项目适用性**：中-高。project_memory 已评估 HSMM + Student-t HMM 非过度工程（Phase 4 鲁棒性阶段实施），AH-HMM 是其进一步升级（meta-regime 层）。strategy_registry 的 regime-gating 字段可记录 fast state（bull/bear）+ slow meta-regime（uncertainty regime），不同 meta-regime 用不同仓位规则。

**⑥ Feature Store：Feast 0.64 数据质量监控（对标 data_asset/factor 漂移检测前置）**

[Feast 0.64 2026-06-26](https://feast.dev/blog/)（Data Quality Monitoring）：内置数据质量监控（nulls/schema drift/freshness/volume 异常）在**物化时**检测（materialization time），而非仅下游。[Feast 2026-06-09 SOX Audit Logging](https://feast.dev/blog/) 补离线存储查询指标 + SOX 合规审计日志。**比现有方法更好**：§4.7 E11 的 PSI/KS/Wasserstein 在模型输入层检测漂移，Feast 0.64 在**特征管道层**检测（更早，before reaches models）——双层检测减少冗余。**个人项目适用性**：中。YAML 阶段 §4.7 E11 足够；DB 阶段若采用 Feast，0.64 的物化时监控是免费升级（pip install feast==0.64），SOX audit logging 配合 §4.21① SR 26-2 治理。

**⑦ 集成策略：Meta-labeling 方向×仓位分离（对标 strategy_registry 架构）**

[Nova Quant Lab 2026-04-06](https://novaquantlab.com/the-apex-predator-architecting-an-ensemble-meta-model-for-quantitative-arbitrage/)：López de Prado meta-labeling——primary 模型决定**方向**（买/卖），secondary meta-model 决定**仓位**（size up/filter false positive），关键要求是 base models 误差**不相关**（非模型数量）。[mental-momentum 2026-06-14](https://research.mental-momentum.ai/r/ensemble-stacking-methods-quantitative-7xzgf4) 补充：集成仅在 purged+embargoed CV + 经济效用指标（Sharpe/max DD，非准确率）约束下有效，否则放大噪声。**比现有方法更好**：strategy_registry 当前 entry 是单体策略，meta-labeling 允许登记 (primary-direction, meta-sizing) **pair**，各自独立 re-validate。**个人项目适用性**：中。project_memory 已评估 Autoencoder-Gated+SAC RL 为过度工程（远期不采纳），但 meta-labeling 是**轻量级**集成（非 RL），Phase 1.5+ 可作为 strategy_registry 的 `strategy_subtype: meta_labeled` 变体登记，primary+meta 各自走 §4.13 PROMOTE_ENTRY 门禁。

> ⚠️ **v1.14.0 第三轮总结**：7 项对标覆盖模型风险(SR 26-2)/回测框架(NautilusTrader)/因子选择(double-selection LASSO)/滑点(华创LightGBM)/regime(AH-HMM)/feature store(Feast 0.64)/集成(meta-labeling) 七领域。**两项实盘合规 MUST**（§4.20 A股监管变更）+ **5 项 Phase 1.5+ 增强项**（NautilusTrader/double-selection/LightGBM/AH-HMM/Feast 0.64）+ **1 项架构启发**（meta-labeling pair 登记）。**MVP 阶段无阻塞**——§4.20 监管字段 MUST 在 P1-B 施工时预留（schema 字段缺失=实盘违规），其余均为 Phase 1.5+ 增强项。

### 4.22 第四轮研究对标补充（v1.15.0 新增）

v1.12.0 §4.17 + v1.13.0 §4.19 + v1.14.0 §4.21 覆盖第一/二/三轮。本轮（v1.15.0）针对 5 个新领域（LLM因子挖掘/Agentic研究工作流/证据SHA256治理/数据契约独立模块/量化Agent转向）做第四轮全网搜索（2026-08-10），筛选 5 项高价值对标（剔除已覆盖项），分领域补充。**本轮重点是"研究流程治理"**——前三轮聚焦算法/工具，本轮聚焦研究工作流本身的架构与治理。

**① LLM 因子挖掘：AlphaSchema 5 字段语义计划（对标 factor_registry 登记流程）**

[Waton Financial 2026-08-10 AlphaSchema](https://ceo.ca/@GlobeNewswire/waton-financial-highlights-alphaschema-research-progress)（arXiv 预印本，X-Tech/PandaAI/Waton 联合，清华交叉信息院）：针对"LLM 因子挖掘让模型同时发明 idea + 写代码导致不可检查"的问题，AlphaSchema 将**语义计划作为搜索的主对象**，延迟代码生成至计划选定后。每个候选计划用 5 字段表示：**Event**（市场现象）/ **Context**（发生条件）/ **Qualities**（可选确认/一致性/过滤准则）/ **Direction**（交易解释：连续/反转）/ **Output**（候选信号的数值形式）。搜索流程：广度探索 + surrogate-guided 选择 + 局部变异 → 选定计划翻译为可执行研究代码 → 在评估前检查数据契约和泄漏规则。在 CSI 300 universe（2016-2020 训练/2021-2022 验证/2023-2025 测试）上做了 5 次独立发现运行。**比现有方法更好**：factor_registry 当前登记的是"已实现因子"，AlphaSchema 提供了"因子发现阶段"的语义模板——新因子登记前可用 5 字段语义计划描述假设，与代码分离，便于人工审查"为什么这个因子应该有效"。**个人项目适用性**：中。MVP 阶段 factor_registry 登记现有手写因子，Phase 2+ 评估 LLM 辅助因子挖掘时，factor_registry schema 可选补 `discovery_plan`（5 字段语义计划）记录因子发现的原始假设。**MVP 决策**：Phase 2+ 远期评估项（个人项目当前因子手工开发，LLM 因子挖掘非 MVP 阻塞）。

**② Agentic 研究工作流：架构是承重件（对标 experiment_registry 治理流程）**

[Jonathan Kinlay 2026-05-17 Agentic Workflows for Alpha Research](https://jonathankinlay.com/2026/05/agentic-workflows-for-alpha-research/)（12 周 FX-carry 研究 case study）：核心洞察——**架构是承重件，不是提示词或模型选择**。换 Claude 为任何前沿模型大多仍有效；换掉 typed handoffs/research log/human gates 则几乎全失效（AutoGen/MetaGPT 同结论）。度量单位不是"ideas/hour"（误导），而是"**经人类级批判后存活的 ideas/month**"——在此指标上提升约 2×（非宣传的 10×）。研究时间分解：文献筛选 20-25%/假设规范 5%/数据清洗 25-30%/实现 10-15%/诊断消融 20%/判断综合 10%——AI 在前四类强，最后两类（判断）弱，架构须围绕这个不对称设计：激进委托前四类，判断保持人类，工具化边界使失败早期可见。**比现有方法更好**：experiment_registry 当前登记"实验结果"，Kinlay 框架提供了"实验流程治理"——typed handoffs（结构化交接）/ research log（研究日志）/ human gates（人工门禁）三件套。**个人项目适用性**：中-高。experiment_registry schema 可补 `research_log_ref`（研究日志引用）+ `human_gate_status`（人工门禁状态：pending/passed/rejected）字段，对标 Kinlay 三件套。**MVP 决策**：Phase 1.5+ experiment_registry 施工时考虑补这 2 字段（非 MVP 阻塞，但与 §4.13 PROMOTE_ENTRY G8 人工签批门禁理念一致）。

**③ 证据 SHA256 + allowed_use 治理模式（对标 §4 原则9 SHA256 manifest 生产实证）**

[nathanku3-hue/Quant spec.md 2026-06](https://github.com/nathanku3-hue/Quant/blob/main/docs/spec.md)（V2 PEAD Calendar-Time Inference 合约）：每个证据文件计算 SHA256（`m1b_evidence_sha256 = c80bb7ed583a...`），配合 `allowed_use = bounded_methodology_review_only`（限定用途：仅方法论审查，无 alpha/可交易/PIT/因果/全因子/总体有效性声明）。合约包含：gate 文件路径 + 证据文件路径 + 当前最大声明（descriptive evidence only）+ Path A/B 硬路径 + hard stop（无 gate 批准前禁止 alpha 命名的 dashboard/code）。**这是 §4.10.0 SHA256 manifest 选项的生产实证**——v1.10.0 提出的"content hash + bit-level 可复现"在 Quant 项目中已落地，且增加了 `allowed_use` 用途限定字段（声明"此证据只能用于 X，不能用于 Y"），防止证据越权使用。**比现有方法更好**：§4 原则9 的 SHA256 manifest 只保证可复现，Quant 模式增加 `allowed_use` 字段，明确"此回测结果只能用于方法论审查，不能作为 alpha 声明"——这对策略从研究→实盘的渐进式确认（§4.13 PROMOTE_ENTRY shadow→canary→full）非常有价值。**个人项目适用性**：高。experiment_registry schema 可补 `evidence_sha256`（已在 v1.10.0 §4 原则9 提及）+ `allowed_use`（enum: research_only/methodology_review/canary_basis/live_basis，默认 research_only）字段。**MVP 决策**：Phase 1.5+ experiment_registry 施工时补 `allowed_use` 字段（与 §4.13 PROMOTE_ENTRY 渐进式部署 shadow→canary→full 三阶段的"允许用途"对齐）。

**④ 数据契约独立模块（对标 §4.7 E13 语义漂移检查 + data_asset_registry）**

[stock_good 2026-06-08](https://github.com/blankxxxc/stock_good)（智能选股研究平台样例）：将 `data_contracts/` 作为**独立顶层目录**（与 backend/factors/feature_store/lakehouse/backtest 同级），而非内嵌在各模块中。平台串成"数据接入→数据治理→因子工程→模型训练→回测评估→研究证据→模拟盘治理→Web Research Console"闭环，data_contracts 是治理层的契约定义。**比现有方法更好**：§4.7 E13 语义漂移检查（semantic_contract/null_semantics/default_fill_policy）检查的是 factor/strategy entry 内的契约字段，stock_good 模式将数据契约**外提为独立模块**——契约定义与消费分离，多个 factor/strategy 引用同一契约，变更时一处修改多处生效。**个人项目适用性**：中。当前 field_dictionary（§7.1）承载字段定义，但未明确"数据契约"概念。Phase 1.5+ 可评估将 field_dictionary 升级为 data_contracts 模块（或新增 data_contracts_registry），与 §4.7 E13 呼应。**MVP 决策**：MVP 用 field_dictionary 承载字段定义，Phase 1.5+ 评估是否独立化 data_contracts（非 MVP 阻塞）。

**⑤ 量化行业转向 Agent 竞争（对标 strategy_registry 架构远期演进）**

[华夏时报 2026-08 报道](http://m.toutiao.com/group/7672218395844067890/) + PandaAI 第三届因子大赛：PandaAI CEO 李昱琦指出"AI 交易未来竞争从单一模型能力转向 Agent 能力、协同能力、研究范式竞争"。背景：2026-07-31 局域网关闭后，速度套利空间消失（§4.20③），量化行业被迫从"拼速度"转向"拼深度"——因子挖掘和模型能力权重上升，Agent 协同研究成为新方向。[Kinlay 2026-05](https://jonathankinlay.com/2026/05/agentic-workflows-for-alpha-research/) 的 agentic workflows 是这一趋势的学术印证。**与 project_memory 的关系**：project_memory 已评估"Mamba/SSM 和 Autoencoder-Gated+SAC RL 远期不采纳"——这是对**单一复杂模型**的决策，与"Agent 协同"（多角色协作的研究工作流）是不同概念。Agent 协同≠RL 策略，前者是研究流程自动化（如 AlphaSchema 的因子发现→验证→登记自动化），后者是交易决策自动化。**个人项目适用性**：低-中。个人项目核心约束是"避免过度工程"，Agent 协同研究工作流属于 Phase 2+ 远期评估项，MVP 阶段维持人工驱动的因子/策略开发。**关键边界**：若未来评估 Agent 辅助研究，须聚焦"研究流程自动化"（Kinlay 的 typed handoffs/research log/human gates），而非"交易决策自动化"（RL 策略，已评估为过度工程）。**MVP 决策**：Phase 2+ 远期评估项，MVP 阶段维持现有人工驱动开发流程。

> ⚠️ **v1.15.0 第四轮总结**：5 项对标覆盖 LLM因子挖掘(AlphaSchema)/Agentic工作流(Kinlay)/证据SHA256治理(Quant)/数据契约独立模块(stock_good)/Agent竞争转向(PandaAI) 五领域，**本轮聚焦"研究流程治理"**（前三轮聚焦算法/工具）。**0 项实盘合规 MUST**（合规项已在 §4.20③ 补齐）+ **1 项 Phase 1.5+ schema 增强项**（experiment_registry 补 `allowed_use` 字段，与 §4.13 渐进式部署对齐）+ **3 项 Phase 1.5-2+ 评估项**（research_log_ref/human_gate_status/discovery_plan）+ **1 项远期架构演进**（Agent 协同研究，Phase 2+，边界=研究流程自动化非交易决策自动化）。**MVP 阶段无阻塞**——§4.20③ 局域网关闭字段 MUST 在 P1-B 施工时预留（与 §4.20①② 同批），其余均为 Phase 1.5+ 增强或 Phase 2+ 远期评估。

### 4.23 第五轮研究对标补充（v1.16.0 新增）

v1.12.0 §4.17 + v1.13.0 §4.19 + v1.14.0 §4.21 + v1.15.0 §4.22 覆盖第一/二/三/四轮。本轮（v1.16.0）针对 4 个新领域（回测验证方法论/可解释AI合规/A股微观结构约束/决策审计治理）做第五轮全网搜索（2026-08-10），筛选 4 项高价值对标。**本轮核心成果是 CPCV 升级回测过拟合六方法**（已直接落地到 §7.2 + §4.13 PROMOTE_ENTRY G2），本节记录方法论对标细节。

**① 回测验证方法论：AlgoXpert IS-WFA-OOS 三阶段协议（对标 §4.13 PROMOTE_ENTRY 门禁架构）**

[arXiv:2603.09219 AlgoXpert 2026-03-10](https://arxiv.org/pdf/2603.09219v1)（Nguyet/Chan/Anh, AlgoXpert Lab）：标准化决策导向的三阶段协议——**(i) IS（In-Sample）**优先稳定参数区域 `Ω_stable = {θ | SR(θ) ≥ 0.9×SR_opt}` 而非单一最优（与 §7.2 plateau_score 呼应）；**(ii) WFA（Walk-Forward Analysis）**配 rolling windows + purge gaps + **majority-pass + catastrophic-veto 双门禁**——majority-pass = 通过 fold 比例 ≥ q；catastrophic-veto = 任何 fold 触发灾难条件（MaxDD 突破红线）立即整体 FAIL；**(iii) OOS（Out-of-Sample）**严格参数锁定（不再调参）。Case study（USDJPY M5）展示 Sharpe→MaxDD 目标切换时的 rank reversal（风险调整收益 vs 尾风险控制的权衡）。**比现有方法更好**：§4.13 PROMOTE_ENTRY G1/G2 用硬编码阈值（Sharpe<0.5/DD>15%），AlgoXpert 的 catastrophic-veto 更鲁棒——"任何切分中回撤 > X% = 一票否决"比"平均回撤 < 15%"更保守。**v1.16.0 已落地**：§4.13 G2 新增 `cpcv_worst_max_dd > 0.15 = catastrophic-veto` 检查（§7.2 CPCV 第 6 方法详解已记录）。**个人项目适用性**：高。MVP 阶段用 PurgedKFold（CPCV 简化版），Phase 1.5+ 升级完整 CPCV + catastrophic-veto。

**② 可解释 AI 合规：EU AI Act 2026-08-02 + SHAP/LIME/counterfactual 三层（对标 strategy/experiment_registry 治理）**

[finantrix 2026-08-08](https://www.finantrix.com/in-focus/alpha-architects-ai-first-investment/responsible-ai-framework-active-management)（Updated August 8, 2026）+ [Dataiku 2026-06-22](https://www.dataiku.com/blog/ai-explainability-for-financial-services) + [theneuralbase 2026-04](https://theneuralbase.com/ai-for-finance/learn/beginner/model-inventory/) + [CSDN 2026-05-22 FINRA/证监会双认证 XAI](https://blog.csdn.net/QuickTrans/article/details/161311391)：EU AI Act **2026-08-02 全面生效**，高风险 AI 系统（信贷评估/风险定价）MUST 提供可验证/可追溯/可复现的决策依据，违规罚款最高 €35M 或全球营收 7%。Wellington Management 按模型生命周期阶段分段治理；Dataiku 5 步框架按风险分层（Tier 1 客户面 SHAP+counterfactual+challenger model，Tier 2 SHAP/LIME，Tier 3 内部分析）；theneuralbase 强调 model inventory 是**合规强制**（非可选文档），决策日志须 append-only ledger（不可修改/删除，SEC Rule 17a4 要求 7 年保留）。**比现有方法更好**：§4.13 PROMOTE_ENTRY G8 人工签批门禁已有，但缺少"决策可解释性"维度。strategy/experiment_registry 可选补 `explainability_method`（none/shap/lime/counterfactual/decision_tree，默认 none）+ `decision_audit_log`（append-only 引用，与 §4.10.0 SHA256 manifest 呼应）字段。**个人项目适用性**：低-中。个人项目非 EU 管辖（<$30B 阈值），但 SHAP 对策略诊断有价值（"为什么这个策略在 2024-Q1 失效"=特征归因分析）。**MVP 决策**：Phase 2+ 远期评估项（MVP 阶段策略数少，人工可解释；ML 策略 Phase 1.5+ 须补 SHAP）。

**③ A 股微观结构约束：价格笼子 + T+1 + 涨跌停不可成交（对标 execution_algo_registry schema）**

[CSDN 2026-08-09 价格规则](https://blog.csdn.net/weixin_eng02048/article/details/143427545) + [sina 2026-07-06 新规](https://finance.sina.com.cn/roll/2026-07-06/doc-inifvuye8570639.shtml) + [CSDN 2026-08-09 T+1 动量突破](https://blog.csdn.net/2501_93020006/article/details/150582666) + [toutiao 2026-08 AI量化避坑](http://m.toutiao.com/group/7671200836869784106/)：A 股三大微观结构约束——① **价格笼子**（连续竞价限价申报范围）：沪深主板/创业板 = 买入≤基准价 102% ∩ 基准价+0.1 元孰高 / 卖出≥基准价 98% ∩ 基准价-0.1 元孰低；科创板 = 纯 102%/98%（无 0.1 元兜底）；北交所 = 105%/95%。② **T+1**：信号当日不能执行，须延迟到次日（回测 MUST `signal.shift(1)`）。③ **涨跌停不可成交**：触及涨跌停时视为无法成交，维持原仓位（回测 MUST 检查 `abs(ret) < limit_pct`）。涨跌停日约占全年 1%，但若恰好需要止损则影响毁灭性。**40_execution_broker v2.6.0 已实现 `check_price_cage`**（project_memory P0 gap 已闭合），但 **execution_algo_registry schema 未显式登记价格笼子参数**。**v1.16.0 施工影响**：execution_algo_registry schema MUST 新增 `price_cage_config`（object: {board: main/gem/star/bse, buy_ceiling_pct: 1.02/1.02/1.02/1.05, sell_floor_pct: 0.98/0.98/0.98/0.95, has_unit_floor: true/true/false/false, unit_floor_yuan: 0.1}）+ `t_plus_1: true`（A 股固定 true）+ `limit_up_down_untradable: true`（涨跌停不可成交，回测约束）三字段。**个人项目适用性**：高（实盘合规 MUST，非可选）。MVP 阶段 cost_model_registry 已登记印花税/过户费/佣金，但价格笼子是**执行层约束**（非成本层），须在 execution_algo_registry 登记。

**④ 决策审计治理：append-only ledger + 24h explainability SLA（对标 §4.10.0 SHA256 manifest + experiment_registry 审计）**

[theneuralbase remediation-paths 2026-04](https://theneuralbase.com/ai-for-finance/learn/beginner/remediation-paths/) + [theneuralbase model-inventory 2026-04](https://theneuralbase.com/ai-for-finance/learn/beginner/model-inventory/)：SEC Rule 17a4 要求决策日志 **7 年保留 + append-only**（不可修改/删除，传统关系数据库不满足，须 append-only ledger 或 blockchain proof）；SEC 24h explainability SLA——算法交易决策 MUST 在监管要求后 24h 内可解释（须存储 features/model_version/confidence/decision_rationale per transaction）。**比现有方法更好**：§4.10.0 SHA256 manifest 保证 entry 产物 bit-level 可复现，但未覆盖**交易决策日志**（per-trade level）。experiment_registry 可补 `decision_log_store`（enum: append_only_ledger/db_traditional/none，默认 none）+ `decision_log_retention_years`（int, 默认 7）字段。**个人项目适用性**：低。个人项目非 SEC 管辖机构，但 append-only 决策日志对**策略复盘**有价值（"那笔交易为什么亏"=查决策日志的 features+model_version）。**MVP 决策**：Phase 2+ 远期评估项（MVP 阶段交易量低，传统 DB 日志足够；AUM 增长或监管要求升级时再评估 append-only ledger）。

> ⚠️ **v1.16.0 第五轮总结**：4 项对标覆盖回测验证(AlgoXpert IS-WFA-OOS)/可解释AI(EU AI Act 2026-08-02+SHAP/LIME)/A股微观结构(价格笼子+T+1+涨跌停)/决策审计(append-only ledger+24h SLA) 四领域。**1 项已直接落地**（CPCV 升级回测过拟合六方法→§7.2+§4.13 G2 catastrophic-veto）+ **1 项实盘合规 MUST**（execution_algo_registry 补 price_cage_config/t_plus_1/limit_up_down_untradable 三字段，与 §4.20 监管字段同批 P1-B 施工）+ **2 项 Phase 2+ 远期评估**（explainability_method/decision_log_store）。**MVP 阶段无阻塞**——价格笼子字段 MUST 在 P1-B 施工时预留（40_execution_broker v2.6.0 已实现逻辑，schema 须对齐），CPCV MVP 用 PurgedKFold 替代 Phase 1.5+ 升级。

### 4.24 第六轮研究对标补充（v1.17.0 新增）

v1.12.0-v1.16.0 覆盖第一/二/三/四/五轮（因子挖掘/回测验证/监管合规/研究流程/可解释AI）。本轮（v1.17.0）聚焦**前六轮未覆盖的两个领域**：① **仓位管理**（position sizing——strategy_registry 和 risk_limit_registry 的核心维度，但前六轮无专门对标）；② **A 股特色数据**（龙虎榜/Level-2/高频因子——data_asset_registry 和 factor_registry 的 A 股专有维度）。本轮还修复了 §4.13 PROMOTE_ENTRY G1/G2 门禁的 **2 个 P0 代码 bug**（字符串拼接 TypeError + CPCV 除零/负 mean 漏判）。

**① 仓位管理：Conformal Kelly——conformal prediction interval 作为 fractional Kelly 的 scale（对标 strategy_registry position_sizing）**

[arXiv:2608.01494v1 Conformal Kelly 2026-08-02](https://arxiv.org/html/2608.01494v1)（Robert Jacob Ryan, ACS Athens）：将 conformal prediction 的**不确定性**用于第二个用途——结合 fractional Kelly 仓位 sizing。用 75% interval：**interval 宽则缩仓（不确定性高），窄则加仓（不确定性低）**。6 年开发窗口（2016-2021），含交易成本+1 日执行延迟+严格杠杆上限，年化 log 增长 28.5%，Sharpe 1.34，MaxDD 27.7%（vs S&P500 持有 15.9%）。**核心发现反直觉**：让 interval 更快适应市场/regime 的每次 tweak 都损失 0.7-5.3 个百分点年增长——**最佳是最简单方法**（slow/unweighted/per-asset rolling conformal quantiles），因为 interval 在 sizing 时**宽度的稳定性比局部锐度更重要**。还实现"**drawdown dial**"——当 conformal interval 下行 miss 远超历史率时，视为模型失效信号，削减杠杆，MaxDD 从 27.7% 降到 20.3% 同时 Sharpe 提升。**比现有方法更好**：纯 Kelly f*=μ/σ² 假设 σ² 已知，Conformal Kelly 用 conformal interval 宽度**自适应**估计不确定性——高不确定性自动缩仓，比固定 fractional Kelly 更鲁棒。**个人项目适用性**：中-高。strategy_registry 的 position_sizing 字段可记录 `sizing_method: conformal_kelly`（vs `fixed_fraction`/`kelly`/`risk_parity`）。**MVP 决策**：MVP 用 fixed_fraction（简单），Phase 1.5+ 评估 fractional Kelly，Phase 2+ 评估 Conformal Kelly（需 conformal prediction 基础设施）。

**② 仓位管理：Kelly+ML 协方差改进（对标 risk_limit_registry 协方差估计）**

[quantsingularity/Kelly-ML-Portfolio-Optimization 2026-06-13](https://github.com/quantsingularity/Kelly-ML-Portfolio-Optimization)：Kelly criterion 的核心痛点是**协方差矩阵估计误差**——f*=μ/σ² 中的 σ² 若估计不准，Kelly 权重剧烈波动。系统评估 3 种 ML 协方差改进：① **Marcenko-Pastur denoising**（随机矩阵理论，分离信号噪声特征值）；② **Hierarchical Risk Parity clustering**（HRP，层级聚类避免矩阵求逆）；③ **market-factor detoning**（移除市场因子降低条件数）。walk-forward K-fold（K=5）回测在 10 只 S&P500 股票上量化估计误差驱动的不稳定性。[SCIRP 2025-03 风险约束 Kelly](https://www.scirp.org/journal/paperinformation?paperid=141556)（Xing/Wang/Zhang, 河北工大）：收缩估计+ridge regression 集成到 Kelly 框架，**A 股实证**——clustering 选股+神经网络预测+风险约束 Kelly，中期投资优于纯 Kelly。**比现有方法更好**：risk_limit_registry 的 VaR 计算依赖协方差矩阵，Marcenko-Pastur denoising 可提升 VaR 估计稳定性（project_memory 已评估 VaR 5 级非过度工程）。**个人项目适用性**：中。Phase 1.5+ risk_limit_registry 施工时，VaR 协方差估计可采用 denoising（Python `sklearn` 实现 <50 行）。**MVP 决策**：MVP 用 sample covariance（简单），Phase 1.5+ 升级 denoising。

**③ 仓位管理：Sizing Shootout A/B 框架（对标 experiment_registry sizer 对比）**

[nousergon/crucible-backtester #559 2026-07-21](https://github.com/nousergon/crucible-backtester/pull/559)：S-slot sizing shootout——在同一历史信号流+同一回测窗口+相同 entry gates/universe/exposure 约束下，对比 3 种 position sizer：① conviction-weighted（incumbent）；② risk-parity（inverse-20d-realized-vol）；③ fractional-Kelly（`kelly_fraction × predicted_alpha / variance`，swept 0.25/0.5）。**关键设计**：**只有 raw position-weight 公式不同**，其余全部共享（score gate/momentum gate/drawdown halt/bear block/GBM veto/position cap/correlation block）——这是科学的 A/B 测试。promotion 候选须**同时** beat incumbent on Sharpe **AND** max-DD after cost（非"或"）。**OBSERVE-only**——comparison artifact 永不直接改 live sizing config（reporting-only）。**比现有方法更好**：experiment_registry 当前登记单策略回测结果，sizing shootout 允许登记**同一策略不同 sizer 的对比**——回答"此策略该用 Kelly 还是 risk-parity"。**个人项目适用性**：中。experiment_registry schema 可选补 `sizing_arm`（enum: conviction/risk_parity/fractional_kelly）+ `sizing_shootout_winner`（string）字段。**MVP 决策**：Phase 1.5+ experiment_registry 施工时考虑补这 2 字段。

**④ A 股特色数据：高频因子 2026 年实战表现（对标 factor_registry intraday 分类）**

[国泰海通证券 2026-08-10 高频选股因子周报](http://stock.finance.sina.com.cn/stock/view/paper.php?reportid=839683589036&symbol=sh000001)（郑雅斌/余浩淼）：2026 年高频因子多空收益表现——日内收益因子 7.75%/开盘后买入意愿强度 16.29%/开盘后大单净买入占比 9.21%/尾盘成交占比 13.58%/日内下行波动占比 14.94%/日内高频偏度 14.53%。多粒度模型（5 日标签）多空 28.18%，多头超额 8.43%。**关键发现**：A 股高频因子 2026 年仍有效（多空 7-16%），但**日内动量与隔夜动量存在反转**（T+1 制度导致——日内收益高的股票隔夜收益低，反之亦然，[CSDN 2026-08-09](https://blog.csdn.net/llijjianmmin/article/details/148821157)）。**比现有方法更好**：factor_registry 的 intraday 分类（project_memory 因子 10 类含 intraday）须登记这些 A 股专有高频因子——它们不是通用因子，是 A 股微观结构特有的（T+1 制度+涨跌停+集合竞价）。**个人项目适用性**：高。factor_registry P1-A 施工时，intraday 分类 MUST 登记：日内收益/开盘后大单净买入占比/尾盘成交占比/日内下行波动占比 4 个 A 股高频因子（数据源须 Level-2）。**MVP 决策**：MVP 用日线因子（无 Level-2 依赖），Phase 1.5+ Level-2 数据接入后登记高频因子。

**⑤ A 股特色数据：龙虎榜+Level-2 数据源治理（对标 data_asset_registry 数据源授权）**

[CSDN 2026-08-09 A 股量化可行性](https://blog.csdn.net/llijjianmmin/article/details/148821157)：商业数据源（Wind/同花顺 iFinD）提供 Level-2 五档行情/逐笔成交/订单信息（前 50 个订单），**AKShare 明确声明仅学术用途不可商用**。[sina 2026-07-08 龙虎榜](https://finance.sina.com.cn/roll/2026-07-08/doc-inihattw8303487.shtml)：龙虎榜数据含机构席位/游资席位/量化席位活跃度，是 A 股独有的"主力资金意图"信号（美股无等价物）。[toutiao 2026-08-10 量化打板博弈](http://m.toutiao.com/group/7672364239159411215/)：2026 年 A 股"机构打底+游资突破+量化搅局"三元主力结构，打板策略核心逻辑从"游资情绪共识接力"升级为"识别机构与游资合力+区分真实拉升与量化诱多"——**量化资金的盘口脉冲（毫秒级拉升/砸盘）和虚假挂单是 2026 新博弈环境**。**比现有方法更好**：data_asset_registry 须登记龙虎榜+Level-2 的**数据源授权**（academic_only/commercial_license/proprietary），避免 AKShare 商用合规风险。**个人项目适用性**：高。data_asset_registry P1-B 施工时，龙虎榜数据源 MUST 标注 `license_type: academic_only`（AKShare）或 `commercial_license`（Wind/iFinD），Level-2 数据同理。**MVP 决策**：MVP 用 AKShare（学术/个人研究），实盘前须评估商业授权（个人项目实盘若涉及 Level-2 须确认 AKShare 条款或采购商业源）。

> ⚠️ **v1.17.0 第六轮总结**：5 项对标覆盖仓位管理(Conformal Kelly/Kelly+ML协方差/Sizing Shootout) + A股特色数据(高频因子/龙虎榜Level-2) 两领域，**本轮填补前六轮"仓位管理"和"A股特色数据"两个对标空白**。**0 项实盘合规 MUST**（合规项已在 §4.20/§4.23 补齐）+ **2 项 Phase 1.5+ schema 增强项**（strategy_registry 补 sizing_method + experiment_registry 补 sizing_arm/sizing_shootout_winner）+ **1 项 Phase 2+ 评估项**（Conformal Kelly 需 conformal prediction 基础设施）+ **2 项 MVP 施工提醒**（factor_registry intraday 分类须登记 A 股高频因子 + data_asset_registry 须标注数据源 license_type）。**P0 代码 bug 修复**（§4.13 G1/G2 字符串拼接 TypeError + CPCV mean<=0 漏判）。**MVP 阶段无阻塞**——仓位管理 MVP 用 fixed_fraction，高频因子 MVP 用日线（Phase 1.5+ Level-2 接入），数据源授权标注 P1-B 施工时 MUST 纳入。

### 4.25 第七轮研究对标补充（v1.18.0 新增）

v1.12.0-v1.17.0 覆盖第一至六轮（因子挖掘/回测验证/监管合规/研究流程/可解释AI/仓位管理/A股特色数据）。本轮（v1.18.0）聚焦**前六轮未系统覆盖的四个领域**：① **回测数据偏差治理**（survivorship bias / look-ahead bias——data_asset_registry 和 experiment_registry 的基础数据质量问题，前六轮仅 honest-backtest Layer 1 顺带提及未系统对标）；② **策略组合**（Regime-Based 动量+均值回归融合——strategy_registry 当前仅登记单体策略，未涉及多策略组合）；③ **信号融合**（Meta-labeling 方向×仓位分离——§4.21③ 第三轮已对标但未落地 schema 字段，本轮补 schema）；④ **归因分析**（Brinson-Fachler + factor-based——PROMOTE_ENTRY G6 要求 benchmark_id 用于归因，但 experiment_registry 无归因字段，ATTRIBUTION 算法归 54 号，本轮补 schema 字段）。本轮还**填补施工环节流程算法缺口**：新增 §4.7 E14 回测数据偏差检查 + §4.4 跨文档职责边界（RUN_BACKTEST→52号/ATTRIBUTION→54号，避免本文档过度工程）。

**① 回测数据偏差治理：生存偏差 + 前瞻偏差系统性治理（对标 data_asset_registry 数据质量 + experiment_registry 偏差声明）**

[digitalninjasystems 2026-05-28](https://digitalninjasystems.wpcomstaging.com/2026/05/28/why-your-backtest-results-might-be-misleading-and-how-to-fix-it/) + [thedatascientist 2026-06-10](https://thedatascientist.com/the-data-leakage-traps-hiding-in-financial-market-data-and-how-to-build-a-leak-free-dataset/) + [dev.to 2026-07-06](https://dev.to/tradevodata/survivorship-bias-vs-lookahead-bias-the-two-silent-backtest-killers-pmm) + [preprints.org 2026-06-04](https://www.preprints.org/manuscript/202606.0436) + [LobeHub Financial Data Quality 2026-07-31](https://lobehub.com/skills/brainbytes-dev-everything-claude-trading-data-quality)：**生存偏差**（survivorship bias——回测仅含存活至今日的公司，排除破产/退市/并购）使 US equity 策略年化收益高估 1-3%，小市值/价值策略更严重；**前瞻偏差**（look-ahead bias——使用决策时未可知的信息，如财报数据按财报期而非公布日期对齐）使 mean-reversion 策略收益虚增 40-60%。preprints 2026-06 提出三分类偏差 taxonomy：① **universe-membership contamination**（生存偏差，universe 成员污染）；② **price-data forward leakage**（价格数据前瞻泄漏）；③ **stop-exit sequencing violations**（止损退出时序错误——止损/止盈在当日收盘价而非次日开盘执行）。dev.to 2026-07 称两者为"the two silent backtest killers"——schema 检查通过、分布检查通过，但回测用了未来信息或存活样本，结果完全失真。**比现有方法更好**：§4.7 E11 查特征统计漂移（null_rate/PSI/KS/Wasserstein）、E13 查语义漂移（字段含义），但**均未覆盖数据源头偏差**——E11/E13 查的是"特征值是否漂移"，生存/前瞻偏差是"数据样本本身是否有偏"，是更根本的"数据是否可信"问题。**v1.18.0 已落地**：① §4.7 新增 **E14 回测数据偏差检查**（experiment_registry 查 backtest_bias_checks 三分类声明 + data_asset_registry 查 survivorship_free/pit_available/earnings_lag_days 声明）；② data_asset_registry schema 补 `survivorship_free`/`pit_available`/`earnings_lag_days` 三字段；③ experiment_registry schema 补 `backtest_bias_checks` 字段。**个人项目适用性**：高。MVP 阶段用 AKShare 日线数据（声明 `survivorship_free: unknown`，仅学术用途），但 schema 字段 MUST 预留；Phase 1.5+ 接入含退市数据的商业源（Norgate Data/Compustat）时填 `survivorship_free: true`。**MVP 决策**：MVP 阶段 backtest_bias_checks 填 `{survivorship: unknown, lookahead: unknown, stop_exit: unknown}`（诚实记录"未检查"），实盘前 MUST 升级评估。

**② 策略组合：Regime-Based 动量+均值回归融合（对标 strategy_registry 组合配置）**

[digitalninjasystems 2026-05-24](https://digitalninjasystems.wpcomstaging.com/2026/05/24/how-to-combine-mean-reversion-with-momentum-for-higher-returns/) + [中金公司 2026-06-24](https://finance.sina.com.cn/stock/stockzmt/2026-06-24/doc-inienieh3068292.shtml)：**趋势-震荡 regime 切换**——200日SMA以上为 Trending Up（动量 80% + 均值回归 20%），以下为 Trending Down（空头动量 60% + 均值回归 40%），区间震荡时均值回归 85%。两类策略本质互补：动量在趋势中盈利但震荡中亏损，均值回归在震荡中盈利但趋势中亏损，regime 检测器决定权重分配。中金增强信号策略在股债金八资产配置中，最大回撤从 -5.42% 降至 -2.99%，卡玛比率从 0.98 提升至 1.71。**比现有方法更好**：strategy_registry 当前登记单体策略（打板/多因子/事件驱动等 6 类），未涉及多策略组合——Regime-Based 融合可提升整体鲁棒性，单一策略在某 regime 失效时组合仍可盈利。**v1.18.0 已落地**：strategy_registry schema 补 `combination_strategy`（object: regime_detector + allocation_weights）字段。**个人项目适用性**：中。**MVP 决策**：Phase 1.5+ 评估（MVP 先聚焦单体策略，组合需先有多个成熟单体策略 + regime 检测器）。

**③ 信号融合：Meta-labeling 方向×仓位分离（对标 strategy_registry 集成架构）**

[Neyt/How-To-Backtest-Correctly 2026-03](https://github.com/Neyt/How-To-Backtest-Correctly)（López de Prado《Advances in Financial Machine Learning》开源实现）+ [NTU 2026-05-20](https://dr.ntu.edu.sg/entities/publication/899e7928-244b-416b-b321-ba6c72355e5c) + [mental-momentum 2026-06-14](https://research.mental-momentum.ai/r/ensemble-stacking-methods-quantitative-7xzgf4)：**primary 模型定方向**（买/卖），**meta 模型定仓位**（size up / filter false positive），关键是 base models 误差不相关。Neyt 实现的 Meta-Labeling（Corrective AI）将 side prediction 与 size/confidence 分离，显著提升 F1-score。NTU 多智能体系统中，技术面/基本面/新闻情绪三 agent 信号经 XGBoost 融合，年化收益 21.18%，2022 年回撤 -7.93%（优于 SPY 的 -18.18%）。mental-momentum 2026-06 强调 ensemble stacking 的核心是 base models 误差不相关——若高度相关则融合无增益。**比现有方法更好**：比简单等权组合更鲁棒，meta 模型显式处理假阳性（primary 误判方向时 meta 降低仓位），比固定仓位更自适应。§4.21③ 第三轮已对标 meta-labeling 但未落地 schema 字段。**v1.18.0 已落地**：strategy_registry schema 补 `meta_labeling_config`（object: primary_strategy_id + meta_strategy_id + base_models_error_correlation）字段。**个人项目适用性**：中。**MVP 决策**：Phase 2+ 远期评估（MVP 阶段单体策略足够，meta-labeling 需两个成熟 base model + 误差相关性分析）。

**④ 归因分析：Brinson-Fachler + factor-based attribution（对标 experiment_registry 归因字段，补 ATTRIBUTION 缺口）**

[breakingalpha 2026-01-26](https://breakingalpha.io/insights/performance-attribution-analysis-multi-strategy-portfolios) + [skill4agent 2026-02-20](https://www.skill4agent.com/en/skill/joellewis-finance_skills/performance-attribution) + [pa package 2026-04-25](https://yl2.r-universe.dev/pa/doc/pa.pdf) + [marketopia 2026-05-04](https://www.marketopia.org/blog/performance-attribution/) + [CSDN 2026-08-09 绩效归因](https://blog.csdn.net/wht506520189/article/details/128016766)：**绩效归因**（performance attribution）分解组合收益来源，回答"alpha 从哪来"。两大类方法：① **基于持仓的 Brinson-Fachler 模型**——将超额收益 R_p−R_b 分解为三效应：**Allocation Effect** A_i=(w_p,i−w_b,i)×(R_b,i−R_b)（超配跑赢板块的奖励）、**Selection Effect** S_i=w_b,i×(R_p,i−R_b,i)（板块内选股能力）、**Interaction Effect** I_i=(w_p,i−w_b,i)×(R_p,i−R_b,i)（超配+选股的联合效应）；多期链接用 Carino/Menchero/GRAP/Frongello 算法。② **基于净值的 factor-based 归因**——R_p=Σβ_k×F_k+α，常见因子模型 FF3（市场/规模/价值）/Carhart4（+动量）/FF5（+投资/盈利），α 为因子无法解释的真实 alpha。breakingalpha 2026-01 强调 multi-strategy portfolio 须区分 **return attribution**（收益分解）vs **risk attribution**（风险分解）+ **TWR vs MWR**（时间加权 vs 资金加权，manager 评估用 TWR 隔离择时干扰）。**比现有方法更好**：§4.13 PROMOTE_ENTRY G6 门禁要求 `benchmark_id` 用于归因，但 experiment_registry schema 仅有 `result_summary`（Sharpe/max_dd/ic）无归因字段——归因回答"为什么赚"而非"赚多少"，是策略复盘与迭代的关键输入（project_memory 54 号 3 项含 performance_attribution_report）。**v1.18.0 已落地**：experiment_registry schema 补 `attribution_result`（object: method + allocation/selection/interaction 三效应 + factor_contributions + alpha）字段。**跨文档职责边界**：归因**执行逻辑**归 54 号 performance_attribution_report（§4.4 已标注 ATTRIBUTION→54号），本字段仅登记归因结果元数据，避免在本文档重复实现归因算法。**个人项目适用性**：中-高。**MVP 决策**：MVP 阶段用 factor-based 归因（FF3/Carhart4，Python `statsmodels` OLS <50 行实现，对标 §4.25① 数据偏差治理后的可信收益）；Brinson-Fachler 需持仓数据（Phase 1.5+ 实盘有真实持仓后补）。

> ⚠️ **v1.18.0 第七轮总结**：4 项对标覆盖回测数据偏差治理/策略组合/信号融合/归因分析四领域，**本轮填补前六轮"数据源头偏差"和"收益归因"两个对标空白**。**3 项 schema 字段已落地**（data_asset_registry 补 survivorship_free/pit_available/earnings_lag_days + experiment_registry 补 backtest_bias_checks/attribution_result + strategy_registry 补 combination_strategy/meta_labeling_config）+ **1 项审计检查已落地**（§4.7 E14 回测数据偏差检查，E1-E13→E1-E14）+ **1 项施工环节缺口填补**（§4.4 跨文档职责边界：RUN_BACKTEST→52号/ATTRIBUTION→54号，避免本文档过度工程重复实现）。**MVP 阶段无阻塞**——数据偏差字段 MVP 填 unknown（诚实记录），归因 MVP 用 factor-based（简单），策略组合/meta-labeling 为 Phase 1.5+/Phase 2+ 评估项。

### 4.26 第八轮研究对标补充（v1.19.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.18.0 覆盖第一至七轮。本轮（v1.19.0）聚焦**前七轮未系统覆盖且 2026-08 最新爆发的 LLM 时代量化治理缺口**：① **LLM 前瞻偏差治理**（Look-Ahead-Bench——v1.18.0 E14 仅查传统回测偏差 survivorship/lookahead/stop_exit，未覆盖 LLM 特有的"记忆泄漏" memorization leakage——LLM 训练语料含未来信息导致回测虚高）；② **数据侧脱敏协议**（KTD-FIN 4-level masking——LLM 回测评估时如何防止模型通过 ticker/日期识别出未来事件）；③ **因子语义抽象层**（AlphaSchema 5 字段 schema_plan——v1.18.0 factor_registry 仅 `formula` 字段，未支持 LLM 因子挖掘的语义层与实现层解耦）；④ **策略来源标记 + LLM 蒸馏**（TiMi ICLR 2026——LLM 离线研发策略蒸馏为纯代码在线执行，strategy_registry 未标记策略来源与是否已蒸馏）；⑤ **Regime-aware 因子筛选**（Alpha-R1 8B RL 模型——v1.18.0 combination_strategy 的 regime_detector 仅 200d_sma/hmm，未覆盖新闻+宏观叙事驱动的语义 regime 检测）。本轮填补施工环节缺口：§4.7 新增 E15 LLM 前瞻偏差检查（KTD-FIN 4-level masking 协议检查）+ 4 项 schema 字段补全 + 1 项归因注释增强（VIF-screened Barra）。

**① LLM 前瞻偏差治理：Look-Ahead-Bench 标准化基准（对标 data_asset_registry LLM 训练截止声明 + experiment_registry LLM 前瞻检查）**

[Look-Ahead-Bench arXiv:2601.13770 2026-01-20](https://arxiv.org/pdf/2601.13770)（Benhenda, PiT-Inference）+ [CSDN 2026-08-09 LLM 驱动量化深度分析](https://blog.csdn.net/tingyunye/article/details/155138329)：**LLM 前瞻偏差**（look-ahead bias via memorization）是传统前瞻偏差的 LLM 时代升级版——传统前瞻偏差是"财报按报告期对齐"，LLM 前瞻偏差是"模型在训练时已读过 2020 年的新闻/价格/事件，回测时凭记忆而非预测给出信号"。CSDN 2026-08-09 §5.2 直白描述："用 2023 年的 GPT-4 去测试 2020 年的策略，效果一定好到爆炸——因为 GPT-4 在训练时已经读过 2020 年的新闻了，它知道未来发生了什么。这就像拿着明天的报纸去买今天的彩票。"Look-Ahead-Bench 三大贡献：① **Practical Trading Workflow Integration**——不用 Q&A 测试 inner knowledge，而用 AI Hedge Fund 框架（45k+ stars）做真实组合决策；② **Point-In-Time LLMs 对比**——评估 Pitinf-Small/Medium/Large（专为金融设计的 PiT LLM）vs Llama 3.1（8B/70B）/DeepSeek 3.2，结果**标准 LLM 显著前瞻偏差（alpha decay 严重）**，Pitinf 模型随规模增大泛化能力提升；③ **Alpha Decay 跨 regime 测量**——通过比较模型在不同时间段的表现衰减区分"真预测能力"vs"记忆回放"。**比现有方法更好**：§4.7 E14 检查传统回测偏差（survivorship/lookahead/stop_exit），但 LLM 时代有第四类偏差——**memorization leakage**（KTD-FIN 命名）。E14 的 `lookahead` 字段假设"数据按公布日期对齐即可"，但 LLM 即使数据对齐正确，模型权重本身已含未来信息——这是 E14 未覆盖的盲区。**v1.19.0 已落地**：① §4.7 新增 **E15 LLM 前瞻偏差检查**（experiment_registry 查 llm_lookahead_check_result + data_asset_registry 查 llm_training_cutoff/lookahead_test_method）；② data_asset_registry schema 补 `llm_training_cutoff`/`lookahead_test_method` 字段；③ experiment_registry schema 补 `llm_lookahead_check_result` 字段。**个人项目适用性**：中。MVP 阶段未使用 LLM 直接生成交易信号（仅用 LLM 辅助研报/代码生成），llm_lookahead_check_result 可填 `{applicable: false, reason: "MVP未使用LLM直接生成信号"}`；Phase 2+ 评估 LLM 信号时 MUST 跑 Look-Ahead-Bench 4 测试或其简化版。

**② 数据侧脱敏协议：KTD-FIN 4-Level Masking（对标 experiment_registry 评估协议，防止 LLM 通过标识符识别未来）**

[KTD-FIN "From Knowing to Doing" arXiv:2605.28359 2026](https://arxiv.org/pdf/2605.28359)（Memory-Controlled Benchmark for LLM Trading Agents）：解决 LLM 交易智能体评估两大失败模式：① **Memorization Leakage**（记忆泄漏）——LLM 通过 ticker/日期/品牌线索识别出未来事件，论文实证"anchor 模型在 ticker 可见时积极交易引用品牌驱动理由，ticker 匿名时则 abstain"；② **Raw Returns ≠ Skill**（原始收益≠选股能力）——正收益可能来自市场 beta/持续风格暴露/有利 regime 而非选股 alpha。**核心机制：4-Level Data-Side Masking Protocol**：① `bright`（真实 ticker + 真实日期，基线）；② `stock-blind`（匿名 ticker + 真实日期）；③ `date-blind`（真实 ticker + 相对日索引）；④ `blinded`（匿名 ticker + 相对日索引，最强脱敏）。Aliases 在单 episode 内稳定但跨 episode 随机化防重构。10-attacker de-anonymization 探针验证：最强攻击者 top-5 ticker 恢复率仅 10.2%，联合（ticker top-5 + 日期 ±7 交易日）成功率仅 1.5%——证明 `blinded` 条件有效缓解泄漏。**配套 Barra-style Performance Attribution**：每日加权最小二乘横截面回归 $r_{i,t}=f_{0,t}+\sum_{k=1}^{K}x_{i,k,t-1}\lambda_{k,t}+\epsilon_{i,t}$，组合分解 $R_p^t=f_{0,t}+\sum_k(\sum_i w_{p_{i,t-1}}x_{i,k,t-1})\lambda_{k,t}+\alpha_p^t$，**9 个 VIF-screened style factors**（momentum/volatility/illiquidity/skewness 等）减少 multicollinearity，$\alpha_p^t$ 为因子调整后的真实选股 alpha。**比现有方法更好**：§4.25④ 归因字段未提及 VIF screening——直接用 FF3/Carhart4 因子可能因 multicollinearity 使 alpha 估计失真（KTD-FIN 明确用 VIF 筛选 9 个低共线因子）。**v1.19.0 已落地**：experiment_registry `attribution_result` 注释补 VIF screening 建议（9 个 VIF-screened style factors + multicollinearity 警告）。**个人项目适用性**：中。MVP 不使用 LLM 交易智能体，4-level masking 为 Phase 2+ 评估 LLM agent 时启用；VIF screening 在 Phase 1.5+ factor-based 归因升级时启用（`statsmodels.stats.outliers_influence.variance_inflation_factor` <50 行实现）。

**③ 因子语义抽象层：AlphaSchema 5 字段 schema_plan（对标 factor_registry LLM 因子挖掘的语义/实现解耦）**

[AlphaSchema 2026-08-01](https://ubos.tech/alphaschema-exploring-the-space-of-trading-semantics-for-llm-based-alpha-mining/)（"Exploring the Space of Trading Semantics for LLM-Based Alpha Mining"）：解决 LLM 因子挖掘两大瓶颈：① **Implicit exploration**（隐式探索）——LLM 既发明因子又决定是否测试，无显式搜索空间表示，难引导发现过程；② **Entangled implementation**（实现纠缠）——同一 LLM 既提因子又写代码，prompt 措辞/model temperature/底层 LLM 架构变化导致实现差异巨大，掩盖语义想法的真实贡献。**核心：5 字段 schema_plan**——① `event`（市场触发，如 earnings surprise/macro news）；② `context`（市场环境或资产池，如 large-cap Chinese equities）；③ `qualities`（描述属性，如 volatility/liquidity/sentiment）；④ `direction`（预期价格方向 positive/negative）；⑤ `output`（数值表示，如 z-score/binary flag）。两阶段解耦：Schema Generator（LLM 产生 schema_plan）→ Surrogate Learner（Gaussian Process/GBT 回归预测 reward）→ Selection Engine（acquisition function 平衡 explore/exploit/mutate）→ Implementation Agent（第二个 LLM 将 schema_plan 翻译为可执行 Python 代码）。Schema Generator 永不见原始价格数据，Implementation Agent 永不决定测哪个想法——透明性 + 可合规审计（如禁止特定 event types）。**比现有方法更好**：factor_registry 当前 `formula` 字段混合"因子语义"与"实现公式"——人工因子无问题，但 LLM 挖掘的因子需分离语义层（可被人类审查经济逻辑）与实现层（可被代码验证）。AlphaSchema 解耦使人类能审查"为何此因子应有效"（经济理性）而非仅"如何计算"（公式）。**v1.19.0 已落地**：factor_registry schema 补 `schema_plan`（可选 obj：event/context/qualities/direction/output）字段。**个人项目适用性**：低-中。MVP 阶段所有因子人工编写（formula 字段足够），schema_plan 为 Phase 2+ LLM 因子挖掘预留；§4.22 第四轮已对标 AlphaSchema 但未落地 schema 字段，本轮补齐。

**④ 策略来源标记 + LLM 蒸馏：TiMi ICLR 2026 离线研发 + 在线蒸馏（对标 strategy_registry origin/distilled_to_code 字段）**

[TiMi "Trade in Minutes!" ICLR 2026](https://finance.sina.com.cn/wm/2026-07-16/doc-inihyyvy4515788.shtml)（国联民生金工 AAAI2026+ICLR2026 综述）：LLM 交易智能体不应直接承担低延迟交易执行——既有研究把 LLM 包装成"分析师/交易员"依赖新闻/角色扮演给买卖建议，带来情绪化表达、外围信息滞后、在线推理延迟等问题。**TiMi 两阶段架构**：① **离线策略研发**——多个专长不同的 LLM 智能体协作完成宏观模式识别/微观交易规则定制/代码实现/参数约束设定，通过回测结果触发反思，不断修正策略逻辑/风控阈值/执行细节；② **在线分钟级执行**——策略稳定后**蒸馏为可直接运行的交易程序**（distilled to executable code），在线阶段不再持续调用 LLM，只执行已固化代码，根据最新行情快速完成信号计算/仓位调整/风险控制。回测与模拟部署反馈回流到离线环节，形成"生成-验证-修正-部署"闭环。**比现有方法更好**：strategy_registry 当前未标记策略来源（human/llm_generated/hybrid）与是否已蒸馏到代码——LLM 生成的策略若仍依赖在线 LLM 调用则有延迟/不可复现/成本高问题，蒸馏到代码后才能进入实盘。TiMi 蒸馏模式与 §4.13 PROMOTE_ENTRY G5（code_commit 代码冻结）精神一致——LLM 策略 MUST 蒸馏为可冻结代码才能晋升 active。**v1.19.0 已落地**：strategy_registry schema 补 `origin`（enum: human/llm_generated/hybrid）+ `distilled_to_code`（bool）两字段。**个人项目适用性**：中。MVP 阶段所有策略人工编写（origin=human, distilled_to_code=true 自然成立）；Phase 2+ 评估 LLM 辅助策略生成时，MUST 在 PROMOTE_ENTRY G5 门禁检查 distilled_to_code=true（LLM 策略未蒸馏=阻断上线）。

**⑤ Regime-aware 因子筛选：Alpha-R1 8B RL 推理模型（对标 strategy_registry combination_strategy regime_detector 升级）**

[Alpha-R1 arXiv:2512.23515 2026-12-29](https://arxiv.org/html/2512.23515v1/)（Jiang et al., 上海交大+StepFun+FinStep）：传统因子方法将 alpha 简化为数值时间序列，忽略决定"因子何时经济相关"的语义理性（semantic rationale）。**Alpha-R1 = 8B 参数推理模型 + RL 训练**，**结合因子逻辑 + 实时新闻**评估 alpha 在变化市场条件下的相关性，**根据上下文一致性（contextual consistency）选择性激活/停用因子**。框架整合宏观指标 + 新闻叙事（news narratives）等异构信息，实现 **regime-aware factor screening**——基于因子理性（factor rationales）与主导市场条件的语义对齐动态调整组合暴露。实证：跨多资产池 Alpha-R1 一致优于基准策略，对 alpha 衰减鲁棒性显著提升。**比现有方法更好**：v1.18.0 combination_strategy 的 `regime_detector` 仅支持 `200d_sma`/`hmm`/`none`——纯数值 regime 检测，未覆盖新闻/宏观叙事驱动的语义 regime。Alpha-R1 的"因子理性 × 市场叙事"语义对齐是更精细的 regime 检测——回答"此因子在当前新闻环境下是否经济相关"而非仅"当前是趋势还是震荡"。**v1.19.0 已落地**：strategy_registry combination_strategy.regime_detector enum 注释补 `news_aware`（Alpha-R1 风格语义 regime，Phase 2+ 评估）。**个人项目适用性**：低。MVP 阶段用 200d_sma（最简单可解释），news_aware 需 8B RL 模型部署 + 实时新闻流，属 Phase 3+ 远期评估；schema 预留 enum 值备未来扩展。

> ⚠️ **v1.19.0 第八轮总结**：5 项对标覆盖 LLM 前瞻偏差治理/数据侧脱敏协议/因子语义抽象层/策略来源标记+LLM 蒸馏/Regime-aware 因子筛选五领域，**本轮填补前七轮"LLM 时代量化治理"对标空白**——v1.18.0 E14 仅查传统回测偏差，未覆盖 LLM 特有的 memorization leakage；factor_registry 未支持 LLM 因子挖掘的语义/实现解耦；strategy_registry 未标记策略来源与蒸馏状态。**6 项 schema 字段/注释已落地**（data_asset_registry 补 llm_training_cutoff/lookahead_test_method + experiment_registry 补 llm_lookahead_check_result + attribution_result 注释补 VIF + factor_registry 补 schema_plan + strategy_registry 补 origin/distilled_to_code + combination_strategy.regime_detector enum 补 news_aware）+ **1 项审计检查已落地**（§4.7 E15 LLM 前瞻偏差检查，E1-E14→E1-E15，KTD-FIN 4-level masking 协议）。**MVP 阶段无阻塞**——LLM 相关字段 MVP 填 N/A 或 unknown（诚实记录"MVP 未使用 LLM 直接生成信号"），Phase 2+ LLM 评估时 MUST 启用 E15 检查；非 LLM 相关字段（schema_plan/origin/distilled_to_code/VIF/news_aware）为 Phase 1.5+/2+ 评估项，schema 预留。

### 4.27 第九轮研究对标补充（v1.20.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.19.0 覆盖第一至八轮。本轮（v1.20.0）聚焦**前八轮未系统覆盖的两个业界共识硬缺口**：① **策略容量（Capacity）检验**（breakingalpha 2026-01 / linitics 2026-04 / hedgeco 2026-04 / daytrading 2026-02 / dyj.live 2026 公募量化限购——PROMOTE_ENTRY G1-G8 检查回测/过拟合/风控/baseline/代码/基准/衰减/签批，但**未检查策略能承载多少资金而不降低收益**——这是业界公认"primary filter through which all performance claims must be evaluated"，小资金测试通过≠大资金可部署）；② **因子冗余/相关性检测**（EntroPy 2026-05 redundancy.py 三维度 / factordbms Orthogonality Analysis 三阶段 / CSDN 2026-07 因子去冗余 / QuantGPT Self-Correlation 检测——factor_registry 当前无因子间相关性字段，E1-E15 审计无冗余检查，多个高相关因子=伪多样化，组合风险被低估）。本轮填补施工环节缺口：PROMOTE_ENTRY 新增 **G9 容量检验门禁** + §4.7 新增 **E16 因子冗余检查** + 5 项 schema 字段补全。

**① 策略容量检验：Square-Root Market Impact Model + 参与率红线（对标 PROMOTE_ENTRY G9 新增）**

[breakingalpha 2026-01-26 "Capacity Constraints in Trading Algorithm Selection"](https://breakingalpha.io/insights/capacity-constraints-trading-algorithm-selection) 直白开篇："The pitch deck shows a Sharpe ratio of 2.8 and annual returns of 47%. You allocate \$50 million. Six months later, your realized Sharpe ratio is 0.9... The algorithm isn't broken—it's simply drowning in too much capital." 核心论断：**"Capacity is not a secondary consideration in algorithm selection; it is the primary filter through which all performance claims must be evaluated. A strategy with modest backtested returns but genuine capacity for your intended allocation will outperform a spectacular backtest that cannot absorb real capital."**

**Square-Root Market Impact Model**（业界共识，[breakingalpha 2026-01](https://breakingalpha.io/insights/capacity-constraints-trading-algorithm-selection) + [linitics 2026-04-28](https://linitics.com/quant-liquidity/)）：

```
Impact = σ × k × √(Q / ADV)
```
- σ = 标的波动率，k = 冲击系数，Q = 订单大小，ADV = 平均日成交量
- 平方根关系：交易 4% 日成交量成本约为交易 1% 的 2 倍——非线性冲击创造自然容量上限

**参与率红线**（[linitics 2026-04](https://linitics.com/quant-liquidity/)）：`Participation Rate = Order Size / Market Volume`，机构约束 **≤ 5%-10% ADV**，超限导致冲击增加/被识别/逆向价格运动。[EntroPy 2026-05](https://github.com/HeroBlast10/EntroPy/blob/main/docs/PRODUCTION_FACTOR_RESEARCH_UPGRADE_2026_05.md) 明确用 **10% ADV 容量估计**作为 deployability hard filter。

**容量衰减悖论**（[dyj.live 2026 公募量化](https://www.dyj.live/knowledge/story_id-gm_explore-3d9b6d41-eb97-5542-bfab-5d8a485f6fc6)）：业绩好→资金涌入→规模膨胀→策略失效→业绩变差。华尔街调侃："好的量化策略只有两个阶段，没人知道的阶段和不再有效的阶段。"公募 50 元限购=保策略有效性的"自残"。[hedgeco.net 2026-04-02](https://www.hedgeco.net/news/04/2026/quant-funds-face-a-capacity-squeeze-when-too-much-capital-threatens-alpha.html) 记录量化基金 capacity squeeze：hard closures / soft closures / higher minimums / redemption controls。

**比现有方法更好**：§4.13 PROMOTE_ENTRY G1 检查 OOS Sharpe/回撤/周期/min_trl_years，G2 检查过拟合，但**两者都不问"这个 Sharpe 在多少资金下成立"**——回测假设无限流动性、即时成交、零冲击（[linitics 2026-04](https://linitics.com/quant-liquidity/) "Backtests assume: Instant fills, Infinite liquidity, Fixed spreads, No impact"），实盘资金放大后市场冲击吃掉 alpha。G9 容量检验填补"回测通过≠实盘可部署"的盲区。[EntroPy 2026-05](https://github.com/HeroBlast10/EntroPy) 的 deployability hard filters 将筛选目标从"最好看"改成"可上线"——方向正确/OOS IC 为正/成本后 Sharpe 为正/换手不过高/**容量不过低**/子样本符号不反复翻转。

**v1.20.0 已落地**：① §4.13 PROMOTE_ENTRY 新增 **G9 容量检验门禁**（检查 capacity_aum_limit + participation_rate_limit + market_impact_model）；② strategy_registry schema 补 `capacity_aum_limit`/`participation_rate_limit`/`market_impact_model` 三字段。**个人项目适用性**：高。个人项目资金量小（MVP 阶段 <100 万），market impact 可忽略，但 schema 字段 MUST 预留——资金增长后 capacity_aum_limit 是"何时该停止加仓"的硬指标。MVP 阶段 capacity_aum_limit 可填保守估值（如日线策略按 5% ADV 估算），participation_rate_limit 填 0.05（5%），market_impact_model 填 square_root。

**② 因子冗余检测三维度：signal/return/exposure correlation（对标 factor_registry + §4.7 E16 新增）**

[EntroPy 2026-05 "Production Factor Research Upgrade"](https://github.com/HeroBlast10/EntroPy/blob/main/docs/PRODUCTION_FACTOR_RESEARCH_UPGRADE_2026_05.md) §3 "冗余剔除" 新增 `redundancy.py`，从**三个维度**识别重复因子：
1. **effective signal correlation**（有效信号相关性）——因子值的截面相关性
2. **factor long-short return correlation**（因子多空收益相关性）——因子收益时序相关性
3. **exposure-vector cosine similarity**（暴露向量余弦相似度）——因子暴露向量相似度

选择逻辑：按 deployability/selection score 排序后做**逐步增量检验**，优先保留 3-5 个互补且稳定的因子。若候选因子与已选因子相关过高，或对已选因子回归后的 **residual alpha Sharpe 太弱**，则剔除。

[factordbms 0.1.1 "Orthogonality Analysis"](https://pypi.org/project/factordbms/) 提供**三阶段框架**：
- Phase 1: Global Correlation Check（Spearman rank correlation 全因子对）
- Phase 2: Clustering（层次聚类识别因子簇）
- Phase 3: Selection（簇内选代表，簇间保留多样性）

[CSDN 2026-07-13 因子筛选](https://wenku.csdn.net/answer/2k1vuaoqxxap) 明确："去冗余：计算因子间的相关性。若两个因子相关性过高（如 >0.7），则它们提供的信息重叠，应结合经济逻辑选择其一或合成新因子。"核心筛选标准包括"低相关性：与其他入选因子的相关性较低，提供独立信息。"[QuantGPT](https://skillsllm.com/skill/quantgpt) 的因子去重用 **Self-Correlation 检测**——独立验证平台自动检测因子自相关。

**比现有方法更好**：factor_registry 当前无因子间相关性字段——每个因子独立登记，但**因子间相关性是组合层面的关键属性**。多个高相关因子（如 PE/PB/PS 三个估值因子相关 >0.8）= 伪多样化，组合实际风险被低估（以为分散了 5 个因子，实际只有 2 个独立信号）。§4.7 E1-E15 审计检查单因子属性（编号/状态/版本/血缘/漂移/偏差），**不检查因子间关系**。E16 因子冗余检查填补"因子库整体多样性"盲区。

**v1.20.0 已落地**：① §4.7 新增 **E16 因子冗余/相关性检查**（factor_registry 查 correlation_group + redundancy_status 声明）；② factor_registry schema 补 `correlation_group`/`redundancy_status` 两字段。**个人项目适用性**：中-高。MVP 阶段因子数 <20，人工可判断相关性，但 schema 字段 MUST 预留——因子数增长后 E16 是"因子库是否伪多样化"的自动检查。MVP 阶段 correlation_group 可按因子分类（10 类）粗分，Phase 1.5+ 接入 EntroPy/factordbms 三维度检测后精细化。

**③ Deployability hard filters：从"最好看"到"可上线"（对标 EntroPy 2026-05 筛选哲学升级）**

[EntroPy 2026-05](https://github.com/HeroBlast10/EntroPy) §2 "单因子评估升级" 提出 **deployability hard filters**——筛选目标从"最好看"改成"可上线"：
- 方向正确（direction 一致）
- OOS IC 为正
- **成本后 Sharpe 为正**（break-even cost 覆盖）
- 换手不过高
- **容量不过低**（10% ADV 容量估计）
- 子样本符号不反复翻转（horizon sign consistency）
- 对 horizon 不敏感（1d/5d/10d/20d 多周期一致）

配套多重检验校正：**Benjamini-Hochberg FDR / Bonferroni / White Reality Check 近似 bootstrap / Deflated Sharpe 近似惩罚**——与 §7.2 experiment_registry 的 PBO/DSR/PSR/MinBTL/MTC/CPCV 六方法互补（六方法查过拟合，EntroPy 四方法查多重检验族错误率）。

**比现有方法更好**：§4.13 PROMOTE_ENTRY G1-G8 是"门禁通过即上线"，但 EntroPy 的 deployability hard filters 是"可上线性"的连续评估——不是 pass/fail，而是"这个因子/策略在多大程度上可部署"。G9 容量检验 + E16 因子冗余检查正是 deployability 维度的两个关键检查，与 EntroPy 哲学一致。**个人项目适用性**：中。MVP 阶段 G1-G9 门禁足够（pass/fail），Phase 1.5+ 可引入 EntroPy 式连续 deployability score 作为辅助决策。

> ⚠️ **v1.20.0 第九轮总结**：3 项对标覆盖策略容量检验/因子冗余检测三维度/Deployability hard filters 三领域，**本轮填补前八轮"实盘可部署性"和"因子库多样性"两个对标空白**——PROMOTE_ENTRY G1-G8 不检查策略能承载多少资金（业界公认 primary filter），factor_registry 不检查因子间相关性（伪多样化风险）。**5 项 schema 字段已落地**（strategy_registry 补 capacity_aum_limit/participation_rate_limit/market_impact_model + factor_registry 补 correlation_group/redundancy_status）+ **1 项门禁已落地**（§4.13 PROMOTE_ENTRY G9 容量检验门禁，G1-G8→G1-G9）+ **1 项审计检查已落地**（§4.7 E16 因子冗余检查，E1-E15→E1-E16）。**MVP 阶段无阻塞**——个人项目资金量小 market impact 可忽略，capacity_aum_limit 填保守估值；因子数 <20 人工可判断相关性，correlation_group 按分类粗分。Phase 1.5+ 资金增长/因子数增长后 G9+E16 成为关键检查。

### 4.28 第十轮研究对标补充（v1.21.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.20.0 覆盖第一至九轮。本轮（v1.21.0）聚焦**前九轮未系统覆盖的 12 个领域**，经全网搜索 2026-08 最新研究后筛选出 **2 项施工算法直接改进（已落地）+ 3 项高价值对标（Phase 1.5+ 评估）+ 7 项参考评估**。本轮核心发现：① **DSR 在相关搜索场景有已知失败模式**（Soloviov 2026-07：真实 Sharpe 3.92 被判 0.748<0.95）——G2 门禁 MUST 升级为鲁棒性带方法；② **因果验证是因子注册时（非上线时）的 gate**（causal-quant 2026-07）——相关性≠因果性，注册即声明因果图避免事后合理化。

**① 有效 trial 数鲁棒性带：DSR 失败模式修复（对标 §4.13 G2 + experiment_registry，v1.21.0 已落地）**

[Soloviov 2026-07 "How Many Backtest Winners Survive Deflation?"](https://github.com/suenot/deflated-sharpe-search)（dsr.marketmaker.cc/paper.pdf）：受控 ground-truth 实验（合成 seeded 数据，已知真实 edge=0）揭示 DSR 的**已知失败模式**——纯噪声搜索 1000 策略时 naive FDR=1.000，DSR 降至 0.001-0.057（有效），但**相关搜索场景中 DSR 用原始 trial count 错误拒绝真实 edge**（真实 Sharpe 3.92 被判 0.748<0.95）。根因：有效 trial 数不是单一数值——5 个标准估计器（Laplace/JAW/AR1/spectral/permutation）在同 trial 矩阵上相差两个数量级（1.6 到 370）。**修复三原则**：① trial 间相关（参数网格/同源变体）时禁用裸 DSR，MUST 用 bootstrap-based 测试（White Reality Check/Hansen SPA 联合重采样）；② MUST 报告≥5 种有效 trial 数估计器的区间（robustness band）而非单值；③ deflated benchmark SR₀≈1.63（年化）=噪声天花板，策略 MUST 跨越此线。**比现有方法更好**：§4.13 G2 当前用 PBO/DSR/PSR/CPCV/MTC 六方法，但 DSR 在相关搜索场景有已知失败模式——G2 不处理此失败模式=可能错误拒绝真实 edge 或通过伪 edge。**v1.21.0 已落地**：① §4.13 G2 新增 `trial_correlated`+`bootstrap_test_passed` 检查（相关 trial 无 bootstrap=阻断）；② experiment_registry schema 补 `trial_correlated`/`effective_trial_count_band`/`bootstrap_test_passed` 三字段。**个人项目适用性**：高。MVP 阶段参数搜索少（<50 trial），trial_correlated=false 时裸 DSR 可用；Phase 1.5+ 参数网格搜索扩展后 MUST 启用 bootstrap 测试。

**② 因果验证声明 gate：causal-quant 因子注册时因果图声明（对标 §4.7 E17 + factor_registry，v1.21.0 已落地）**

[causal-quant v0.4.1 2026-07-09](https://github.com/meacreatio/causal-quant)（de Prado 2023/2026 + Bailey 2014/2017 协议实现）+ [CIR-ACTIVA arXiv:2608.03715 2026-08-04](https://arxiv.org/abs/2608.03715)（摊销干预预测框架）：将因果推断从理论变为可执行的验证 gate。钉住回测撒谎的三种方式——**luck**（运气）/ **confounding**（混淆）/ **selection across everything you tried**（在你尝试的一切中做选择）。核心流程：声明因果图 DAG → 运行证伪测试电池 → 量化报告 H-score（存活"搜索+选择"的 edge 比例）。CIR-ACTIVA 回答"若某序列被外部冲击，系统如何响应"——观测条件分布混淆了因果影响。**关键时机**：因果验证 gate 在因子**注册时**（非上线时）执行——注册即声明因果图，避免事后合理化。**比现有方法更好**：§4.7 E1-E16 查统计属性（编号/状态/版本/血缘/漂移/偏差/冗余），不查**因果属性**——因子背后的经济因果逻辑。相关性≠因果性，回测可能因混淆变量/luck/选择偏差虚高。**v1.21.0 已落地**：① §4.7 新增 **E17 因果验证声明检查**（factor_registry 查 causal_graph 声明，warning 级 MVP 不阻断）；② factor_registry schema 补 `causal_graph` 字段（MVP 可填自然语言描述，Phase 1.5+ 接入 causal-quant 证伪电池后补 H-score）。**个人项目适用性**：中-高。MVP 阶段所有因子人工编写，causal_graph 填自然语言经济逻辑（如"高 ROE→持续盈利能力→股价上涨"）；Phase 1.5+ 接入 causal-quant 库跑证伪电池。

**③ Evidently + NannyML CBPE：按标签延迟分层监控（对标 data_quality_policy，Phase 1.5+ 评估）**

[pythondatabench.com 2026-05-10](https://pythondatabench.com) + [conduktor.io 2026-07-30](https://conduktor.io) + MLOps Community 2026 Production ML Survey：三分法——数据漂移 P(X) 变 / 概念漂移 P(Y|X) 变 / 标签漂移 P(Y) 变。按标签延迟分层：**延迟<1 天**用 Evidently/WhyLabs + 实际性能；**1-90 天**用 NannyML CBPE（置信度性能估计，无标签推断退化）+ 数据漂移；**>90 天** CBPE 为主信号。**大样本陷阱**：KS/chi-square 在百万行参考窗下对纯噪声也报"显著"；PSI（<0.1 稳定/0.2 漂移）和 Jensen-Shannon 测量效应量更诚实。Gartner 统计 85% 生产模型 6 个月内显著漂移，平均滞后 2-4 周发现。**比现有方法更好**：§4.8 衰减检测用 CUSUM/Page-Hinkley/BOCPE（第 1-2 轮），data_quality_policy 用 PSI/KS（v1.4.0），但未按标签延迟分层——A 股 T+1 涨跌停/持仓 30-90 天场景下，标签延迟决定检测器选择。**个人项目适用性**：中。MVP 阶段 PSI+KS 足够（日线策略标签延迟 1 天）；Phase 1.5+ 持仓周期拉长后引入 CBPE。data_quality_policy 注释可补"标签延迟>30 天时 PSI 优于 KS（大样本陷阱）"。

**④ Kyle's lambda + OFI：流动性因子与市场微观结构（对标 factor_registry + §4.13 G9 容量，Phase 1.5+ 评估）**

[microalphas.com 2026-06-02](https://microalphas.com) + [Aldridge arXiv:2607.01377 2026-07-01](https://arxiv.org/abs/2607.01377)（CRSP 2020-2025 验证）+ [quant67.com 2026-05-01](https://quant67.com/post/quant/03-microstructure)：Kyle's lambda = 价格冲击系数 = 市场深度倒数。日级估计：价格变动对签名订单流的回归斜率。Aldridge 验证签名订单流强预测同期+1 个月前瞻收益，高 lambda 股票更贵更信息密集。OFI（订单流不平衡）= (V_buy−V_sell)/(V_buy+V_sell) 是日内最强短期信号之一。**lambda 同时是流动性度量、价格冲击度量和逆向选择度量——三者是同一物不同角度**。**比现有方法更好**：§4.13 G9 容量检验用 Square-Root Market Impact 模型（v1.20.0），但 lambda 提供日级估计（Square-Root 提供冲击模型）——两者互补。lambda 还可作为横截面流动性因子（高 lambda=浅市场=信息密集）。**个人项目适用性**：中-高。A 股有 Level-2 数据时可直接计算 lambda/OFI 作为流动性因子；MVP 阶段用 ADV/换手率粗估流动性，Phase 1.5+ 接入 Level-2 后计算精确 lambda。factor_registry 可补 `liquidity_metric` 字段（lambda/ADV/turnover）。

**⑤ Apicurio 四阶段版本状态机：DEPRECATED/DISABLED 精细化下线（对标 §4.10 RETIRE_ENTRY，Phase 1.5+ 评估）**

[Apicurio Registry 3.3.x docs](https://apicur.io/registry/docs) + [Confluent Data Contracts v8.3](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)（2026-05-14）：版本状态机四阶段——Creation→Evolution→**DEPRECATED**（消费者收迁移警告头但不中断）→**DISABLED**（阻止新消费者依赖）→artifact deletion。metadata.properties 可标 "application.major.version" 识别 breaking change。Confluent 的 **migration rules**（JSONata/CEL 表达式定义版本间数据转换规则）是处理破坏性变更的新机制——比 §4.11 Expand-Contract 三阶段更优雅（转换规则声明式定义，消费者自动应用）。**比现有方法更好**：§4.10 RETIRE_ENTRY 当前用 active→deprecated（90 天宽限）→retired 三态，Apicurio 的 DEPRECATED/DISABLED 更精细——DEPRECATED 允许存量消费者继续用但警告，DISABLED 阻止新消费者依赖（新策略不能引用即将下线的因子）。**个人项目适用性**：中。MVP 阶段三态足够；Phase 1.5+ 因子库扩大后，DISABLED 态可防止新策略引用即将退役的因子。Confluent migration rules 可作为 §4.11 EVOLVE_SCHEMA 的 Phase 2+ 增强项。

**⑥-⑫ 其余 7 项参考评估**（Phase 1.5+/2+ 远期，MVP 无阻塞）：

- **⑥ CRISP/HRP-μ 组合构建**（[arXiv:2604.23833 2026-04-26](https://arxiv.org/abs/2604.23833)）：信号感知的层级组合构建，CRISP 迭代求解 P_γ·w=μ，γ 在对角组合与 Markowitz 间插值。文档登记 factor/strategy 但未覆盖组合权重——属 52/54 号文档职责（§4.4 跨文档职责边界），本注册表仅登记策略，组合构建引用 52 号。
- **⑦ HAR-LSTM-GARCH 波动率预测**（J. Risk Financial Manag. 2026, 19, 77）：DL 在金融唯一被 4+独立研究确认的可靠预测目标是已实现波动率 RV（15-30% MSE 改进），日级方向预测被明确拒绝。risk_limit_registry 可补 `volatility_predictor` 字段（Phase 1.5+ 评估）。
- **⑧ Confluent Data Contracts 五要素**：结构+完整性约束+元数据+规则策略+变更演化。§4.11 EVOLVE_SCHEMA 当前仅覆盖结构+演化，可补完整性约束+规则策略（Phase 2+）。
- **⑨ PatchTST 时序 Transformer**（[research.mental-momentum.ai 2026-06-14](https://research.mental-momentum.ai)）：patch 契合子区间统计直觉，工程价值最高的 Transformer 变体。但 TSFM 预训练在金融低信噪比下增益不可靠——**不作主力**。与 project_memory"Mamba/SSM 不采纳"一致，Transformer 方向审慎评估（Phase 2+ 因子挖掘候选架构）。
- **⑩ TreeSHAP/EBM 可解释 AI**（[aibuzz.blog 2026-06-01](https://aibuzz.blog/ai-attribution-explainability)）：TreeSHAP 适合审计文档（10-50ms/解释），EBM 玻璃盒模型精度接近 XGBoost。EU AI Act 2026-08 生效使 XAI 从最佳实践变法律义务。§4.25④ 归因可补 TreeSHAP 模型级解释（组合级 Brinson + 模型级 SHAP，Phase 1.5+）。
- **⑪ OpenMetadata active 元数据治理**（[open-metadata.org 2026](https://open-metadata.org/learning-center)）：AI context layer 为 agent 提供结构化上下文，原生数据契约支持。Active vs Passive 元数据管理：passive 仅展示，active 用元数据触发动作（质量告警自动阻断因子上线）。registry 设计哲学升级方向（Phase 2+）。
- **⑫ GE+dbt+Soda 三层数据质量**（[pistack.xyz 2026-04-15](https://pistack.xyz)）：Great Expectations（取込 validation）+ dbt tests（变换层）+ Soda Core（持续监控）。Kiwi.com 案例：Data Contracts 引入使工程开销降 53%。data_asset_registry 可要求每个数据源附带 GE expectation suite（Phase 1.5+）。

> ⚠️ **v1.21.0 第十轮总结**：12 项对标覆盖有效 trial 数鲁棒性带/因果验证/标签延迟分层监控/Kyle lambda 流动性/Apicurio 版本状态机/CRISP 组合构建/HAR-LSTM 波动率/Confluent 五要素契约/PatchTST/TreeSHAP/OpenMetadata/GE-dbt-Soda 十二领域，**本轮填补前九轮"DSR 失败模式"和"因果验证"两个对标空白**。**2 项施工算法已落地**（§4.13 G2 鲁棒性带增强 + §4.7 E17 因果验证声明检查）+ **5 项 schema 字段已落地**（experiment_registry 补 trial_correlated/effective_trial_count_band/bootstrap_test_passed + factor_registry 补 causal_graph）+ **3 项高价值 Phase 1.5+ 评估**（Evidently/Kyle lambda/Apicurio）+ **7 项参考评估**。**MVP 阶段无阻塞**——G2 鲁棒性带在 trial_correlated=false 时跳过，E17 causal_graph 填自然语言，effective_trial_count_band 在 n_trials≤10 时可选。

### 4.29 第十一轮研究对标补充（v1.22.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.21.0 覆盖第一至十轮。本轮（v1.22.0）聚焦**前十轮未系统覆盖的 4 个高价值领域**，经全网搜索 2026-06~08 最新研究后筛选出 **2 项施工算法直接改进（已落地 E18/E19）+ 3 项高价值对标（Phase 1.5+ 评估）+ 1 项关键警示**。本轮核心发现：① **LLM 前瞻偏差治理需从"数据侧防御"升级为"数据侧+模型侧双轨"**（LAP 检测+FinCAD 抑制+CMMD 过滤三方法互补，E18 已落地）；② **因子构造方法学偏差是因子动物园复制危机根因**（企业债 108 因子纠正 LIB+ex-post 过滤后多数不再显著，E19 已落地）；③ **A 股板块轮动 Top3 次日重合率仅 14.8%**（sector_rotation 策略校准关键警示）。

**① GSA-LLR 鲁棒 CUSUM：A 股重尾分布变点检测修复（对标 §4.8 DECAY_SCAN_MULTI，v1.22.0 已落地）**

[GSA-LLR arXiv:2605.23419v2 2026-05-27](https://arxiv.org/html/2605.23419v2)（开源代码 [KuYuPe-Change_Point](https://github.com/SZabolotnii/KuYuPe-Change_Point-code-supplement)，Lean 4 形式化验证核心定理）：Generalized Stochastic Approximation of Log-Likelihood Ratio 在广义随机基（多项式/对数/分数幂）上逼近未知对数似然比，仅用 3 阶以下矩信息即可适配 CUSUM 到非高斯数据。基函数自动选择：γ₄<6 用多项式，6≤γ₄<20 用分数幂，γ₄≥20 用对数基。**关键发现**：极端重尾数据（excess kurtosis γ₄>20）上经典 CUSUM 误报率 100%，GSA-LLR 在保证误报率受控的前提下减少检测延迟。A 股小盘股收益分布 γ₄ 常>10、危机期>20——当前 DECAY_SCAN_MULTI 的 CUSUM 检测器在重尾子集上失效。**v1.22.0 已落地**：① `decay_detection_method` 新增 `gsa_llr_cusum` 选项；② DECAY_SCAN_MULTI 检测器 1 增加重尾自适应分支（γ₄≥6 时自动切换 GSA-LLR，γ₄<6 保持经典 CUSUM）；③ 阈值来自 Kunchenko 概率误差界（KU-PE），无需经验调参。**个人项目适用性**：高。A 股重尾分布是已知特征，GSA-LLR 填补 CUSUM 在重尾场景的已知失败模式。

**② LAP 前瞻污染检测 + FinCAD 推理时抑制 + CMMD 多模型分歧过滤（对标 §4.7 E18，v1.22.0 已落地 E18 + 2 项 Phase 1.5+ 评估）**

[LAP arXiv:2512.23847v2 2026-06-12](https://arxiv.org/html/2512.23847v2)（CUHK Gao-Jiang-Yan）：用"日期-only 召回查询"（只给 firm+ticker+日期，无 headline/transcript）估计 LLM 内化未来结果的概率 LAP=P(up)+P(down)。LAP 在训练期内显著为正，越过 cutoff 后坍塌至近零。污染检验回归 Y_{t+1}=β₁μ̂_t+β₂LAP+β₃(LAP×μ̂_t)，β₃>0 即前瞻偏差污染指征（新闻预测股票收益 LLM×LAP 系数 0.162 t=3.64，一倍 LAP 上升使 LLM 边际效应提升约 32% standalone 效应）。**比现有方法更好**：E15（KTD-FIN masking）是数据侧防御，LAP 是模型侧诊断——不修改数据，诊断模型在给定数据上的预测有多少来自记忆。**v1.22.0 已落地**：§4.7 新增 **E18 LAP 前瞻污染检测**（experiment_registry 查 lap_check_result 声明，warning 级 MVP 不阻断）+ experiment_registry schema 补 `lap_check_result` 字段。

[FinCAD arXiv:2605.24564 2026-05-23](https://arxiv.org/pdf/2605.24564)（Edinburgh Li-Wang-Ma）：命名"参数化前瞻偏差"——LLM 权重内已记忆未来结果，数据管道审计看不见。FinCAD 是 Context-Aware Decoding 的推理时改编：先对抗式搜索 model-specific 记忆激活 prior prompt，再在 logit 层减去该 prior，仅在检测到记忆时触发。5 个 7-14B LLM、5 只大盘股上：in-sample 记忆日回测收益降 67.1%，2025 OOS 收益与 baseline 差 <$8K、Sharpe 差 ±0.10。**Phase 1.5+ 评估**：推理时主动抑制，不重训、与 KTD-FIN masking 互补（一防一治）。

[MemGuard-Alpha arXiv:2603.26797](https://arxiv.org/pdf/2603.26797)：CMMD（Cross-Model Memorization Disagreement）利用多 LLM 训练 cutoff 差异分离记忆驱动 vs 推理驱动信号。7 个 LLM、50 只 S&P 100、42,800 prompts、5.5 年评估：CMMD Sharpe 4.11 vs 未过滤 2.76（+49%），干净信号日均 14.48bps vs 污染 2.13bps（7 倍差）。**Phase 1.5+ 评估**：零成本信号级过滤，可整合多个 LLM（不同 cutoff）的信号，分歧大的剔除。

**③ 企业债因子动物园复制危机：LIB + ex-post 过滤偏差警示（对标 §4.7 E19，v1.22.0 已落地）**

[arXiv:2604.07880v1 2026-04-09](https://arxiv.org/html/2604.07880v1)（Dickerson-Robotti-Rossetti UNSW/Warwick，[Open Bond Asset Pricing](https://openbondassetpricing.com/) 开源框架）：108 个企业债因子跨 9 主题集群，纠正两个偏差后多数不再显著：① **Latent Implementation Bias (LIB)**——TRACE 交易价含测量误差，同一噪声价格进入信号和收益分母，相关误差被误认为 premium；② **ex-post 收益过滤嵌入未来信息**——去极值/去流动性差样本用了全期统计量。少数存活因子主要是 credit-spread-based value 信号。**比现有方法更好**：E14 查回测数据偏差（survivorship/lookahead/stop_exit），E19 查**因子构造方法学偏差**——信号与收益是否共用噪声数据源、过滤是否用 walk-forward 统计量。**v1.22.0 已落地**：§4.7 新增 **E19 因子构造偏差审计 LIB**（factor_registry 查 lib_audit/ex_post_filter_audit 声明，仅对 price-derived 因子检查，warning 级 MVP 不阻断）+ factor_registry schema 补 `lib_audit`/`ex_post_filter_audit` 两字段。**A 股关联**：复权价/成交量既是因子输入又是收益计算分母=LIB 风险；去极值/去流动性差用全期统计量=ex-post 过滤风险。

**④ 关键警示：A 股板块轮动 Top3 次日重合率仅 14.8%（对标 sector_rotation 策略校准）**

[WyckoffTradingAgent wiki 2026-07-23](https://github.com/YoungCan-Wang/WyckoffTradingAgent/wiki/04_Finance_Sector_Rotation_Regime)：A 股板块"一日游"——Top3 板块次日重合率仅 14.8%，63.2% 的日子 Top3 完全换人，46.6% 的"领涨"只持续 1 天。应对：降板块延续依赖（hot_bonus 0.05→0.02）、增 3 日动量 q3 快速感知方向变化、板块强度公式从 0.7×q20+0.3×q5 改 0.4×q20+0.3×q5+0.3×q3。共识高潮后 3 日下跌>2% 概率 29.8%。**警示**：任何依赖"板块延续领涨"的策略会严重失效。`sector_rotation` 策略（STR-SECTOR-ROTATION-001）校准时 MUST 采纳此实测数据作为参数依据——板块延续假设需重估，hot_bonus 降至 0.02，增 q3 短期动量权重。

> ⚠️ **v1.22.0 第十一轮总结**：4 项对标覆盖 GSA-LLR 鲁棒 CUSUM/LAP-FinCAD-CMMD LLM 前瞻污染三方法/企业债 LIB 偏差/A 股板块轮动实测四领域，**本轮填补前十轮"重尾分布变点检测"和"模型侧前瞻偏差诊断"和"因子构造方法学偏差"三个对标空白**。**2 项审计检查已落地**（§4.7 E18 LAP 前瞻污染检测 + E19 因子构造偏差审计 LIB）+ **1 项施工算法已落地**（§4.8 DECAY_SCAN_MULTI 检测器 1 增加重尾自适应分支 GSA-LLR）+ **5 项 schema 字段已落地**（experiment_registry 补 lap_check_result + factor_registry 补 lib_audit/ex_post_filter_audit + decay_detection_method 补 gsa_llr_cusum 选项 + risk_limit_registry 补 stage/response_strategy）+ **2 项高价值 Phase 1.5+ 评估**（FinCAD 推理时抑制 + CMMD 多模型分歧过滤）+ **1 项关键警示**（A 股板块轮动 Top3 次日重合率 14.8%）。**MVP 阶段无阻塞**——E18/E19 warning 级不阻断，GSA-LLR 在 γ₄<6 时自动退化为经典 CUSUM，lap_check_result/lib_audit 在未用 LLM 时填 {applicable: false}。

### 4.30 第十二轮研究对标补充（v1.23.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.22.0 覆盖第一至十一轮。本轮（v1.23.0）聚焦**前十一轮未系统覆盖的 3 个高价值方法学领域**，经全网搜索 2026-07~08 最新研究后筛选出 **1 项施工算法直接改进（E20 已落地）+ 2 项 schema 字段已落地 + 2 项高价值 Phase 1.5+ 评估**。本轮核心发现：① **因子冗余检测的方法学质量无人审计**——E16 查冗余声明但不查相关性矩阵是否 RMT 去噪，Marchenko-Pastur 噪声特征值导致伪冗余（E20 已落地）；② **回撤阈值基于高斯假设是已知缺陷**——A 股重尾分布下高斯回撤表系统性误警，RSB 非高斯框架校准是 Phase 1.5+ 必修；③ **VaR 在压力期系统性误校准**——RWC 共形校准是 Phase 1.5+ 必修。

**① RMT 去噪因子相关性矩阵：冗余检测方法学质量审计（对标 §4.7 E20 + factor_registry，v1.23.0 已落地）**

[arXiv:2507.17211v2 2026-08-07 EFS](https://arxiv.org/html/2507.17211v2)（Chen-Luo-Zhang-Liu-Zhang 港中文+上财，q-fin.PM）：Evolutionary Factor Search 框架用 LLM+进化算法自动生成 alpha 因子，核心创新是 **redundancy-aware weight allocation module**——先用随机矩阵理论（RMT）去噪因子相关性矩阵 Σ 得 Σ̂（保证半正定+优化可行），再用正则化二次规划分配权重 −λω⊤Σ̂ω。在美股/港股/A股三市场 Fama-French 基准上均优于未去噪基线，**无额外调参成本**。**比现有方法更好**：E16 查冗余声明（correlation_group/redundancy_status），但相关性矩阵本身含 Marchenko-Pastur 噪声——当 q=N_factors/T_observations>0.1（因子数/观测数比），落在 [λ₋,λ₊]=σ²(1±√q)² 区间内的特征值是纯噪声而非信号，未去噪的伪相关被误判为因子冗余，导致 independent 因子被错误标 redundant 或反之。[arXiv:2601.07687v4 2026-08-02](https://arxiv.org/html/2601.07687v4)（Manolakis-Bongiorno-Mantegna 物理信息奇异值学习）进一步指出标准 RMT 假设平稳+有界谱，真实收益违反此假设（依赖漂移+宏观共同模），Phase 2+ 用神经网络估计器在经验奇异向量基上学习非线性映射替代解析收缩，OOS 协方差预测+跟踪误差最小化均优于 BBP 解析收缩。**v1.23.0 已落地**：① §4.7 新增 **E20 RMT 去噪因子相关性矩阵审计**（factor_registry 查 rmt_denoised 声明，warning 级 MVP 不阻断）；② factor_registry schema 补 `rmt_denoised` 字段。**个人项目适用性**：高。MVP 因子数<20 时 q<0.1 可填 {applicable: false}，Phase 1.5+ 因子数>20 时 MUST 启用 RMT clipping 去噪（将 [λ₋,λ₊] 内特征值替换为均值，保留信号特征值）。

**② 非高斯回撤风险校准：RSB 框架四维决策度量（对标 §4.8 DECAY_SCAN_MULTI + risk_limit_registry drawdown_calibration_method，v1.23.0 schema 已落地，Phase 1.5+ 算法评估）**

[arXiv:2608.00127v1 2026-07-31 Drawdown Risk Beyond Brownian Motion](https://arxiv.org/pdf/2608.00127)（Landolfi Epiphany，q-fin.RM）：扩展 Rej-Seager-Bouchaud (RSB) 回撤框架，将 P&L 建模为漂移布朗运动 dPnL=μdt+σdW（σ=1 归一化，年化 Sharpe=μ=漂移），推导回撤深度/长度的闭式分布。**关键发现**：① **放宽高斯假设**后（固定 Sharpe+波动率，变化偏度/肥尾/波动率聚集/Sharpe 估计不确定性），四个决策相关度量（最大回撤/最大损失/最终负时间/最长恢复时间）**移动方向不同**——单一高斯表系统性误警，对重尾分布（A 股 γ₄ 常>10）尤其严重；② **长记忆（分数布朗运动 fBm）**下回撤风险放大**几乎完全是自相似色散缩放效应** T^(H-1/2) 而非路径几何深化——是 √-of-time 校准的失败，不是内在危险。**比现有方法更好**：当前 risk_limit_registry 的 drawdown 类限额（RLM-DRAWDOWN-001~008）阈值是静态经验值（如"回撤50%止损"），基于高斯假设。A 股重尾分布下高斯回撤表系统性误警——肥尾策略的真实最大回撤远超高斯预测，单一阈值要么过松（该止损时不止损）要么过紧（正常波动触发止损）。**v1.23.0 已落地**：risk_limit_registry schema 补 `drawdown_calibration_method` 字段（gaussian/rsb_non_gaussian/fbm_long_memory，MVP 默认 gaussian，Phase 1.5+ 重尾策略切换 rsb_non_gaussian）。**个人项目适用性**：高。MVP 用高斯近似（保守阈值兜底），Phase 1.5+ 对重尾策略（γ₄>6）MUST 用 RSB 非高斯校准——按策略实际偏度/肥尾/波动率聚集生成四维回撤查找表，替代单一静态阈值。

**③ Regime-Weighted Conformal VaR 校准：压力期系统性误校准修复（对标 risk_limit_registry var_calibration_method，v1.23.0 schema 已落地，Phase 1.5+ 算法评估）**

[arXiv:2602.03903v3 2026-08-03 Taming Tail Risk](https://arxiv.org/html/2602.03903v3)（Schmitt Oxford，q-fin.RM）：Regime-Weighted Conformal Calibration (RWC) 用指数时间衰减+regime 相似性权重从历史预测误差构建安全缓冲，包裹任意条件分位数预测器以对准目标违反率。**关键发现**：VaR 预测在压力期系统性误校准——实现违反率偏离名义目标（Basel 99%/97.5% 级别），TWC（时间加权共形）在漂移下是强默认，regime 加权改善慢适应预测器的压力期校准。模型无关（model-agnostic），无需假设加权可交换性，在平滑 regime 漂移下推导覆盖界。**比现有方法更好**：当前 var_calculator 用固定历史窗口计算 VaR，不区分 regime——压力期 VaR 系统性低估（违反率远超名义 1%），平静期系统性高估（违反率远低于 1%）。RWC 用 regime 相似性权重动态调整安全缓冲，压力期自动收紧。**v1.23.0 已落地**：risk_limit_registry schema 补 `var_calibration_method` 字段（historical/rwc_conformal，MVP 默认 historical，Phase 1.5+ 切换 rwc_conformal）。**个人项目适用性**：中-高。MVP 用历史模拟法（简单），Phase 1.5+ VaR 限额上线后 MUST 评估 RWC——regime 分类器复用项目 regime_detector（35/36 号文档），无需额外建模。

> ⚠️ **v1.23.0 第十二轮总结**：3 项对标覆盖 RMT 去噪因子相关性矩阵/非高斯回撤风险校准/Regime-Weighted Conformal VaR 校准三领域，**本轮填补前十一轮"因子冗余检测方法学质量"+"回撤阈值高斯假设缺陷"+"VaR 压力期系统性误校准"三个对标空白**。**1 项审计检查已落地**（§4.7 E20 RMT 去噪因子相关性矩阵审计）+ **3 项 schema 字段已落地**（factor_registry 补 rmt_denoised + risk_limit_registry 补 drawdown_calibration_method/var_calibration_method）+ **2 项高价值 Phase 1.5+ 算法评估**（RSB 非高斯回撤校准 + RWC 共形 VaR 校准）。**MVP 阶段无阻塞**——E20 warning 级不阻断，rmt_denoised 在因子数<20 时填 {applicable: false}，drawdown_calibration_method 默认 gaussian，var_calibration_method 默认 historical。

### 4.31 第十三轮研究对标补充（v1.24.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.23.0 覆盖第一至十二轮。本轮（v1.24.0）聚焦**前十二轮未系统覆盖的 1 个高价值根本缺口**——**universe_registry 的生存偏差治理**。经全网搜索 2026-06~08 最新研究后筛选出 **1 项施工算法直接改进（E14 扩展已落地）+ 3 项 schema 字段已落地**。本轮核心发现：**E14 taxonomy ① universe-membership contamination 自 v1.18.0 起就声明"生存偏差在 universe 层进入"，但实现只查 data_asset_registry 不查 universe_registry——这是"概念正确但实现遗漏"的典型缺口**：data_asset 含退市股 ≠ universe 用 PIT 成分构造，二者独立。生存偏差是回测第一偏差（US equity 年化高估 1-3%，小市值/价值策略更严重），且最隐蔽地进入 universe 层。

**① universe_registry 生存偏差治理：PIT 成分构造 + 退市股处理审计（对标 §4.7 E14 c 维度 + universe_registry，v1.24.0 已落地）**

[alphanume 2026-06-08 How to Build a Momentum Strategy](https://www.alphanume.com/blog/how-to-build-a-momentum-strategy)：**"The universe is where survivorship bias enters most silently."** 回测从今日指数成分或厂商库（已静默丢弃退市股）取股票列表=高估收益，因排除失败者。正确 universe 构造从 point-in-time 成分文件开始——记录每个 formation date 哪些股票可选，只用当时可得信息。退市股 MUST 含至退市日，收益含最终部分期收益。流动性/价格过滤每个 formation date 用当时数据应用（非回溯）。[tickernerd 2026-08-03 methodology](https://tickernerd.com/methodology/)：三锁定窗口方法论（tune 2005-2014 / check 2015-2020 / judge 2021-2025 blind），强调 "point-in-time Compustat/FactSet 历史，显示模型当日能看到的初步数字而非后述修订值"，金融公司留在池内用银行专属指标衡量（而非整体剔除——"a universe rule that quietly deletes a fifth of the market is a hidden sector bet"）。[arXiv:2603.16904 2026-03 Quantum-Assisted Rebalancing](https://arxiv.org/pdf/2603.16904)：显式构造 survivorship-bias-free S&P500 universe——从当前成分回溯 cutoff 后所有 add/delete 事件，恢复当时成分集，消除 look-ahead bias。**比现有方法更好**：E14（v1.18.0）taxonomy ① 已声明 "universe-membership contamination（生存偏差）——仅含存活至今日的公司"，但实现只查 data_asset_registry 的 price dataset 是否 survivorship_free，**不查 universe_registry 的成分构造是否 PIT**。这是"概念正确但实现遗漏"——data_asset 含退市股（survivorship_free=true）但 universe 用当前成分回溯构造（pit_constituent_construction=false）= 仍有生存偏差。**v1.24.0 已落地**：① §4.7 E14 扩展 c 维度——新增 universe_registry 的 pit_constituent_construction / delisted_handling 声明检查（**不新增 E21，避免 E 编号膨胀**——E14 本就是"回测数据偏差检查"语义内聚，生存偏差含 universe 层是其核心子类，扩展比新增 E21 更内聚且省 E1-E20→E1-E21 的 6 处同步 churn）；② universe_registry schema 补 `pit_constituent_construction`（bool）+ `delisted_handling`（include/exclude/unknown）+ `survivorship_free`（bool）三字段。**个人项目适用性**：高。MVP 阶段 5 条 universe entry：UNI-INDEX-001/002（沪深300/中证800 static 池）MUST 声明 pit_constituent_construction（AKShare 成分历史是否 PIT 待确认，中证指数公司季度调整文件可回溯）；UNI-DYNAMIC-001（打板池）+ UNI-RULE-001（全A可交易池）+ UNI-RULE-002（事件池）的过滤规则本身用当日数据（涨停/ST/流动性过滤都是 formation-date 当下可得），pit_constituent_construction 可填 true，delisted_handling 须确认是否含退市股。MVP 无阻塞——字段声明即可，实际 PIT 成分文件接入=Phase 1.5+。

> ⚠️ **v1.24.0 第十三轮总结**：1 项对标覆盖 universe_registry 生存偏差治理 1 个高价值根本缺口，**本轮填补前十二轮"universe 层生存偏差审计实现遗漏"对标空白**——E14 taxonomy 自 v1.18.0 声明 universe-membership contamination 但实现只查 data_asset 不查 universe。**1 项审计检查已扩展**（§4.7 E14 新增 c 维度 universe_registry PIT/退市处理审计，不新增 E 编号避免膨胀）+ **3 项 schema 字段已落地**（universe_registry 补 pit_constituent_construction/delisted_handling/survivorship_free）。**MVP 阶段无阻塞**——5 条 universe entry 声明字段即可，AKShare 成分历史 PIT 性待确认，实际 PIT 成分文件接入=Phase 1.5+。

### 4.32 第十四轮研究对标补充（v1.25.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.24.0 覆盖第一至十三轮。本轮（v1.25.0）聚焦**前十三轮未系统覆盖的 PIT 字段语义 + 预注册协议 + 策略研发自动化三领域**，经全网搜索 2026-07~08 最新研究后筛选出 **2 项施工算法直接改进（E14 扩展 d 维度 + G1 增强已落地）+ 1 项 Phase 1.5+ 评估 + 3 项 schema 字段已落地**。本轮核心发现：① **PIT 字段语义契约是回测偏差治理的引擎层空白**——E14 查数据源/生存偏差但不查每种数据类型的 as_of_date 语义（Prices=EOD/Splits=执行日/Dividends=公告日/Universe=时点成分），Assay 引擎给出可直接落 schema 的字段语义契约；② **预注册+成本否决是过拟合治理的流程层空白**——IC 虚高与实盘收益脱钩是已知缺陷，MASTER-lite 的 3 窗 3 seed + 成本否决是 MVP 可落地的流程约束。

**① Assay PIT 正确回测引擎：as_of_date 字段语义契约审计（对标 §4.7 E14 d 维度 + data_asset_registry，v1.25.0 E14 扩展已落地）**

[Assay 回测引擎 2026-07-04](https://github.com/chester1uo/Assay)（ICLR 2026 [AlphaBench](https://alphabench.cc/) 配套，2026-08-02 加港市支持）：明确 as_of_date 规则——Prices=EOD（收盘价当日可得）、Splits=执行日（除权日生效）、Dividends=公告日（fallback 除权日，**公告日 ≠ 除权日**）、Universe=时点成分（formation date 当下可得）。**比现有方法更好**：E14（v1.18.0）查 backtest_bias_checks 三分类（survivorship/lookahead/stop_exit），第十三轮扩展 c 维度查 universe PIT，但**不查每种数据类型的 as_of_date 语义**——复权价用前复权（含未来 split 信息）=前瞻偏差，分红用除权日而非公告日=忽略公告日到除权日的漂移。**v1.25.0 已落地**：① §4.7 E14 扩展 d 维度——新增 data_asset_registry 的 as_of_date_semantics 声明检查（**不新增 E21，避免 E 编号膨胀**——E14 本就是"回测数据偏差检查"语义内聚，PIT 字段语义是其核心子类）；② data_asset_registry schema 补 `as_of_date_semantics` 字段（枚举 eod_bar/execution_date/declaration_date/ex_date/universe_snapshot）。**个人项目适用性**：高。MVP 阶段 data_asset_registry P1-B 施工时 MUST 声明每种数据类型的 as_of_date 语义，复权价用后复权（backward-only）避免前瞻偏差。

**② AurumQ-RL MASTER-lite 预注册协议：成本否决 + 3 窗 3 seed（对标 §4.13 PROMOTE_ENTRY G1 增强 + experiment_registry，v1.25.0 G1 增强已落地）**

[AurumQ-RL 2026-07-17](https://github.com/yupoet/aurumq-rl)（A 股 RL 选股工程化封装，§12.7d MASTER-lite 预注册协议）：预注册协议三要素——① **成本否决**：含真实滑点/佣金/冲击成本的 OOS 收益须为正，IC 高但 OOS 亏损=否决；② **3 窗 3 seed**：3 个时间窗口 × 3 个随机种子，方差超阈值=不稳定=否决；③ **模型层修正**：IC 优化目标与实盘收益相关性<阈值=IC 脱钩告警。[R&D-Agent-Quant NeurIPS 2025](https://arxiv.org/pdf/2505.15155)（微软开源，2026-07-23 Qlib 集成）佐证此缺陷——"IC 优化与实盘收益脱钩"是已知缺陷，2× 收益但 70% 因子数减少后稳定性差。**比现有方法更好**：§4.13 PROMOTE_ENTRY G1 检查 OOS Sharpe/回撤/周期，但**不检查成本否决和 IC-OOS 脱钩**——IC 虚高但含成本后亏损的策略可能通过 G1。**v1.25.0 已落地**：① §4.13 G1 增强——新增成本否决子检查（`bt.oos_return_after_cost <= 0` = 阻断）+ IC-OOS 脱钩告警（`bt.ic_oos_correlation < 0.3` = warning，不阻断）；② experiment_registry schema 补 `pre_registered`（bool）+ `cost_vetoed`（bool）+ `ic_oos_gap`（float）三字段。**个人项目适用性**：高。MVP 阶段预注册是流程约束（非算法），成本否决含 A 股万5 印花税+万0.1 过户费+滑点 0.2%，3 窗 3 seed 用 walk-forward 3 折 × 3 种子。

**③ R&D-Agent-Quant 因子-模型协同优化（Phase 1.5+ 评估，v1.25.0 schema 预留）**

[R&D-Agent-Quant](https://arxiv.org/pdf/2505.15155)（NeurIPS 2025，微软开源，2026-07-23 Qlib 集成）：Research(假设/任务分解) + Development(CoSTEER 代码生成，≤10 轮写-测-修) 双 agent；多臂老虎机调度方向；隔离 Conda 环境逐因子回测。实测：相对经典因子库年化收益 2×，因子数减少 70%。国联民生实测 36 个有效 Loop，双周频 IC 升至 0.07。**已知缺陷**：IC 优化与实盘收益脱钩、稳定性差、代码质量不稳。**v1.25.0 schema 预留**：factor_registry schema 补 `discovery_agent` 字段（枚举 human/rd_agent/efs/hubble/other）。**个人项目适用性**：中。Phase 1.5+ 评估——MVP 阶段所有因子人工编写（discovery_agent=human），Phase 1.5+ 接入 R&D-Agent-Quant 后 discovery_agent=rd_agent。

> ⚠️ **v1.25.0 第十四轮总结**：3 项对标覆盖 PIT 字段语义契约/预注册协议成本否决/因子-模型协同优化三领域，**本轮填补前十三轮"PIT 字段语义引擎层空白"+"预注册流程层空白"+"因子发现自动化"三个对标空白**。**2 项施工算法已增强**（§4.7 E14 扩展 d 维度 PIT 字段语义审计 + §4.13 G1 增强成本否决+IC-OOS 脱钩告警，**不新增 E/G 编号避免膨胀**）+ **4 项 schema 字段已落地**（data_asset_registry 补 as_of_date_semantics + experiment_registry 补 pre_registered/cost_vetoed/ic_oos_gap + factor_registry 补 discovery_agent）+ **1 项 Phase 1.5+ 评估**（R&D-Agent-Quant 因子-模型协同优化）。**MVP 阶段无阻塞**——E14 d 维度/g1 增强均为声明检查，data_asset_registry P1-B 施工时声明 as_of_date_semantics，experiment_registry P2 施工时声明 pre_registered/cost_vetoed，factor_registry 已有 111 条 entry 填 discovery_agent: "human"。

### 4.33 第十五轮研究对标补充（v1.26.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.25.0 覆盖第一至十四轮。本轮（v1.26.0）聚焦**前十四轮遗留的 schema 落地缺口 + 2026-08 最新 regime 检测算法 + 概念误读澄清**：① **Wasserstein HMM regime 检测**（arXiv:2603.04441 2026-02——前十四轮 regime_detector 仅 200d_sma/hmm/news_aware，plain HMM 滚动重估计会置换标签导致 regime 身份不稳定，Wasserstein 模板跟踪几何锚定身份保持，Sharpe 2.18 vs SPX 1.18）；② **PBO null=0.5 误读澄清**（marketmaker.cc 2026-07-01——§4.13 G2 用 PBO 但未警示"PBO≈0.5=完全过拟合=硬币翻转"的常见误读，PBO 零假设是 0.5 不是 0）；③ **Kyle lambda 实现陷阱**（JohnGavin #627 2026-08-03——v1.21.0 第十轮对标 Kyle lambda 但未落地 schema 字段且未警示 ratio 形式塌缩为 Amihud 的实现 bug）；④ **Meta-labeling 适用边界**（QuantConnect 2026——v1.18.0 对标 meta-labeling 但未记录"仅改善 discretionary 模型，不改善 end-to-end ML 模型"的适用边界）；⑤ **v1.21.0 第十轮遗留 schema 落地**（liquidity_metric/label_delay_days/drift_detector 三字段研究段对标但 schema 定义段未落地）。

**① Wasserstein HMM：解决滚动 regime 检测标签置换问题（对标 strategy_registry regime_detector，v1.26.0 已落地）**

[arXiv:2603.04441v1 2026-02-21](https://arxiv.org/pdf/2603.04441v1)（Boukardagha, Columbia University, q-fin.PM）：**Explainable Regime-Aware Investing** 框架，核心是 **Wasserstein Hidden Markov Model**——严格因果滚动 Gaussian HMM 估计 + 预测模型阶选择（one-step-ahead log-likelihood 自适应状态数）+ **2-Wasserstein 模板跟踪**（Gaussian 组件映射到持久 regime 模板，closed-form 2-Wasserstein 距离）。三大贡献：① **身份保持**——模板锚定提供几何基础的身份保持，无需离散分配优化，确保 regime 连续性；② **自适应复杂度**——regime 数量随时间动态适应，预测模型阶选择基于一步-ahead log-likelihood；③ **交易成本感知**——regime 概率嵌入 transaction-cost-aware mean-variance 优化。实证：Sharpe 2.18 vs equal-weight 1.59 vs SPX buy&hold 1.18，maxDD -5.43% vs SPX -14.62%；2025 "Liberation Day" 股市抛售期间动态减仓转向防御资产。对比非参数 KNN 条件矩估计器（相同特征+优化层），参数化 regime 模型 turnover 显著更低、权重演化更平滑。**比现有方法更好**：strategy_registry regime_detector 当前有 200d_sma/hmm/news_aware/none 四选项，但 **plain HMM 滚动重估计会置换标签**（label permutation）——每次 EM 重训后状态编号可能互换，导致 regime 身份不稳定、下游优化权重剧烈跳变、turnover 爆炸。Wasserstein HMM 用 2-Wasserstein 距离几何锚定身份，消除组合不稳定性——这是 regime 推断质量的**一阶决定因素**（论文标题即"regime inference stability is a first-order determinant"）。**v1.26.0 已落地**：strategy_registry combination_strategy.regime_detector enum 补 `wasserstein_hmm` 选项，Phase 1.5+ 优先于 plain hmm 评估。**个人项目适用性**：中-高。MVP 阶段用 200d_sma（简单可解释），Phase 1.5+ 评估 regime 检测时 MUST 优先 wasserstein_hmm 而非 plain hmm（后者标签置换问题在 A 股高波动环境下更严重）。

**② PBO null=0.5 误读澄清：过拟合检测的概念校准（对标 §4.13 G2 门禁，v1.26.0 已落地）**

[marketmaker.cc 2026-07-01 "Probability of Backtest Overfitting"](https://marketmaker.cc/en/blog/post/probability-backtest-overfitting-pbo/)（pbo-search.marketmaker.cc 配套论文 + [github.com/suenot/pbo-search](https://github.com/suenot/pbo-search) 开源代码）：**PBO 的零假设是 0.5 不是 0**——这是最常见的误读。PBO（Probability of Backtest Overfitting, Bailey-Borwein-López de Prado-Zhu 2017）= in-sample 选为最优的配置在 out-of-sample 落入**下半区**的概率。若搜索无泛化能力，in-sample winner 在 OOS 排名均匀分布，落入下半区概率=0.5——**PBO≈0.5 = 完全过拟合 = 硬币翻转**。PBO≈0 = 选择可信（winner 可靠保持 winner）；PBO≈1 = 反转（winner 系统性 loser）。受控 ground-truth 实证：零 edge 场景（200 iid 噪声策略）PBO=0.476（≈0.5 硬币翻转）；植入 edge 场景（20 个真实 Sharpe 2.38 策略）PBO=0.001（可信）；MA 网格在随机游走上 PBO=0.463（与零 edge 不可区分=过拟合）。**比现有方法更好**：§4.13 G2 门禁用 `PBO>0.2` 阈值阻断，但**未警示 PBO≈0.5 的含义**——团队可能误读"PBO=0.4 是轻度过拟合"而放松警惕，实际 0.4 已接近硬币翻转基线。**v1.26.0 已落地**：§4.13 G2 门禁加 PBO null=0.5 误读警示注释，明确"0.2-0.5 区间仍阻断（泛化能力不足）"。**个人项目适用性**：高。MVP 阶段单策略独立验证 PBO 可能不适用（PBO 需多策略搜索场景），Phase 1.5+ 参数网格搜索后 MUST 报告 PBO 并按 0.2 阈值阻断。

**③ Kyle lambda 实现陷阱：OLS slope 而非 ratio（对标 factor_registry liquidity_metric，v1.26.0 已落地）**

[JohnGavin/historical #627 2026-08-03](https://github.com/JohnGavin/historical/pull/627)（修复 published dashboard 上的 Kyle lambda = Amihud 重复 bug）：Kyle lambda 是**价格冲击系数**（price-impact coefficient），即 ΔP_t = λ·Q_t + ε_t 的 **OLS 回归斜率** = cov(log_ret, signed_flow)/var(signed_flow)，**不是** ratio = abs(log_ret)/volume。ratio 形式会塌缩为 Amihud（因 abs(signed_flow) == volume by construction），二者数值恒等=bug。该 bug 曾 live 在 published dashboard 上，"Tail-Risk Predictivity (R vs Amihud vs Kyle)" 段实际在比较一个序列与自身。修复后 kyle_mean 在 window 级别用闭式回归斜率计算，paired coverage gate 比 mean-based gate 更严（min_frac=0.9），signed_flow 零方差时返回 NA（斜率未定义）。**比现有方法更好**：v1.21.0 第十轮对标 Kyle lambda（[Aldridge arXiv:2607.01377](https://arxiv.org/abs/2607.01377) + [microalphas 2026-06-02](https://microalphas.com/kyles-lambda/)）但仅"建议补 liquidity_metric 字段"未落地，且未警示 ratio vs slope 实现陷阱。**v1.26.0 已落地**：① factor_registry schema 补 `liquidity_metric` 字段（{metric_type, value, estimation_method, data_requirement}）；② 字段注释显式标注实现陷阱——"kyle_lambda MUST 用 OLS slope = cov(log_ret, signed_flow)/var(signed_flow) 而非 ratio = abs(log_ret)/volume（ratio 形式塌缩为 Amihud）"。**个人项目适用性**：中-高。MVP 阶段用 ADV/turnover 粗估流动性（日线数据），Phase 1.5+ 接入 Level-2 后计算精确 lambda/OFI（MUST 用 OLS slope 而非 ratio）。

**④ Meta-labeling 适用边界：仅改善 discretionary 模型（对标 strategy_registry meta_labeling_config，v1.26.0 注释增强）**

[QuantConnect 2026 "Why Meta-Labeling Is Not a Silver Bullet"](https://www.quantconnect.com/forum/discussion/14706/why-meta-labeling-is-not-a-silver-bullet/)：meta-labeling（López de Prado AFML 2018）的核心争议——**meta-labeling 只能改善 discretionary/规则型主模型，不能改善 end-to-end ML 主模型**。逻辑三论证：① 若 meta-model 能从相同特征提取更多信息，无逻辑理由认为它比主模型更强（主模型已端到端优化）；② 若级联 meta-model 能提升性能，则可无限级联 meta-meta-model（ad-infinitum 谬误）；③ meta-model 正确定 size 与主模型正确生成信号同等困难。grid search 实证：use_meta=0（单模型 end-to-end）与 use_meta=1（meta-labeling）平均 Sharpe 无显著差异，meta 反而略低。**但**：对 discretionary/规则型主模型（如 MA 交叉、基本面信号），meta-labeling 有效——因为主模型未充分利用特征，meta-model 可提取残余信息。**比现有方法更好**：v1.18.0 第七轮对标 meta-labeling（Neyt 2026-03 + NTU 2026-05-20 + mental-momentum 2026-06-14）但**未记录适用边界**——可能误导团队对 end-to-end ML 模型也加 meta-labeling 层（无效且增加复杂度）。**v1.26.0 已落地**：strategy_registry meta_labeling_config 字段注释增强，明确"仅适用于 discretionary/规则型主模型（primary_strategy_id 指向规则策略），end-to-end ML 主模型不适用"。**个人项目适用性**：中。MVP 阶段单体策略足够，Phase 2+ 评估 meta-labeling 时 MUST 先判断主模型类型——规则型（MA/形态/基本面）适用，ML 端到端型不适用。

**⑤ v1.21.0 第十轮遗留 schema 落地：liquidity_metric + 标签延迟分层（v1.26.0 补全）**

v1.21.0 第十轮研究对标了 Kyle lambda 流动性因子和 Evidently+NannyML 标签延迟分层监控，但当时仅"建议补字段"未在 schema 定义段落地。本轮（v1.26.0）补全：① factor_registry schema 补 `liquidity_metric`（见上 ③）；② data_asset_registry schema 补 `label_delay_days`（标签可用延迟天数，NannyML CBPE 估计须按延迟分层）+ `drift_detector`（漂移检测器 none/evidently/nannyml/alibi_detect）。**一致性修复**：v1.21.0 研究段声明对标但 schema 未落地=声明与实现脱节，本轮闭合此缺口。

> ⚠️ **v1.26.0 第十五轮总结**：5 项对标覆盖 Wasserstein HMM regime 检测/PBO null=0.5 误读澄清/Kyle lambda 实现陷阱/Meta-labeling 适用边界/v1.21.0 遗留 schema 落地五领域，**本轮填补前十四轮"regime 检测标签置换稳定性"+"过拟合检测概念校准"+"流动性因子实现陷阱"+"信号融合适用边界"+"研究段-schema 落地脱节"五个对标空白**。**0 项新 E/G 编号**（Wasserstein HMM 补 regime_detector enum 选项不新增 E/G；PBO 澄清是 G2 注释增强不新增 G；Kyle lambda 是 schema 字段+注释；Meta-labeling 是注释增强）+ **3 项 schema 字段已落地**（factor_registry 补 liquidity_metric + data_asset_registry 补 label_delay_days/drift_detector）+ **2 项 enum/注释增强**（regime_detector 补 wasserstein_hmm + G2 PBO null=0.5 警示 + meta_labeling_config 适用边界注释）+ **1 项 Phase 1.5+ 评估**（Wasserstein HMM 优先于 plain hmm）。**MVP 阶段无阻塞**——liquidity_metric MVP 用 ADV/turnover 粗估，label_delay_days 按财报实际填写，drift_detector 填 none（实盘后启用），regime_detector MVP 用 200d_sma，meta_labeling MVP 不用。**关键洞见**：本轮价值在于"概念校准"而非"新增检查"——PBO null=0.5 和 Kyle lambda ratio-vs-slope 是两个常见的实现/解读陷阱，警示注释防止施工时踩坑。

### 4.34 第十六轮研究对标补充（v1.27.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.26.0 覆盖第一至十五轮。本轮（v1.27.0）聚焦**前十五轮未系统覆盖的变点归因 + LLM 因子生成安全 + RL 微调 vs prompt loop + 文本+VAR 双向 regime + 重尾分布回测指标 + 标准化因子评测基准六领域**，经全网搜索 2026-08 最新研究后筛选出 **6 项对标（2 项施工算法增强 + 4 项 schema 字段/enum 落地）**。本轮核心发现：① **变点归因是衰减检测的"检测后归因"空白**——§4.8 有 CUSUM/Page-Hinkley/BOCPE 检测器但无"检测到变点后归因到哪个因子/资产"的算法，ARM 提供有限样本保证的归因；② **LLM 因子生成安全标准是 discovery_agent 引擎层空白**——现有 hubble 枚举但无 AST 沙箱等安全验证栈声明；③ **RL 微调 vs prompt loop 是 discovery_agent 区分空白**——QUANTEVOLVER 证明 policy update 优于 prompt-level feedback loop。

**① ARM - Attribution by Rank Maxima：变点归因算法（对标 §4.8 衰减检测，v1.27.0 §4.8 增强已落地）**

[arXiv:2608.01691v1 2026-08-03](https://arxiv.org/html/2608.01691v1)（Peng-Wu-Yan-Chen-Shen, 北京工业大学+南洋理工, stat.ME）：**ARM（Attribution by Rank Maxima）**——检测器无关的变点归因 wrapper。核心问题：检测到 multivariate series 的变点后，标准做法是在估计变点 τ̂ 处对每个坐标做两样本检验，但**此做法无效**——τ̂ 是用同一数据在聚合统计量最大处估计的，per-coordinate 检验会膨胀 FWER>0.66。ARM 用 **max-over-splits rank statistic** 评分每个坐标，3 个有限样本保证：① per-coordinate validity（任意检测器下有效）；② exact FWER control（Westfall-Young 联合置换保持跨坐标依赖 + Holm fallback）；③ FDR control（Benjamini-Yekutieli + e-BH，高维任意坐标依赖下）。金融实证：2008 年崩盘 5 个金融序列，ARM 将 scale change 归因到每个资产类别并排除注入的 control coordinates。**比现有方法更好**：§4.8 衰减检测有 CUSUM/Page-Hinkley/BOCPE 2/3 投票检测器，但**检测到变点后不归因**——不知道是哪个因子/资产/坐标导致了变点，下游 adaptation 无从下手（是降权哪个因子？是切换哪个策略？）。ARM 填补"检测→归因→adaptation"中间的归因空白。**v1.27.0 已落地**：§4.8 衰减检测流程补"步骤 5：变点归因"子步骤——检测到变点后 MUST 调用 ARM 归因到具体因子坐标，归因结果写入 strategy_registry decay_detection_method 字段（格式 `{detector: "cusum", attribution: "arm"}`）。**个人项目适用性**：中-高。MVP 阶段因子数<20 可不启用归因（直接全量降权），Phase 2+ 因子数>20 时 MUST 启用 ARM 归因（精准降权而非全量降权，减少误杀有效因子）。

**② Hubble AST 验证沙箱：LLM 因子生成安全标准（对标 factor_registry discovery_agent，v1.27.0 schema 补 llm_safety_stack 已落地）**

[arXiv:2604.09601v2 2026-04-14](https://arxiv.org/pdf/2604.09601)（Shi-Yan-Cai-Lv, Celestial Quant Lab+UBC, cs.AI）：**Hubble**——LLM 驱动 agentic alpha 因子发现框架。5 大组件：① **DSL 约束生成器**（curated DSL over OPEN/HIGH/LOW/CLOSE/VOLUME/VWAP，算术 + 时序 TS_SMA/TS_STD + 截面 CS_RANK/CS_ZSCORE + 逻辑 IF）；② **AST 验证沙箱**（exec-free 安全栈，3 层验证：结构安全=白名单 AST 节点防任意代码执行 + 复杂度控制=depth/node-count 上限 + 语义有效性=算子名/arity/变量名严格匹配 DSL）；③ **双通道 RAG**（positive RAG 提供代表性机制鼓励探索 under-covered 主题 + negative RAG 显式劝阻 crowded 模板控制因子拥挤）；④ **确定性评估引擎**（RankIC/Pearson IC + Coverage/drop ratio/bucket returns/long-short spread/turnover/复杂度 + Bartlett-kernel HAC 显著性检验）；⑤ **加权评分 family-aware selection**（predictive power + stability + turnover + ecological diversity，tanh 标准化 + crowding/similarity/family concentration 惩罚）。实证：美股 500 股票 104 候选因子 3 轮零崩溃，top-5 因子 2025-06~2026-03 OOS 验证 2 个 range 因子 + 2 个 volatility 因子保持正 IC。**比现有方法更好**：factor_registry discovery_agent 有 hubble 枚举，但**未声明 LLM 因子生成的安全验证栈**——裸 LLM 生成因子公式有任意代码执行风险（unsafe code execution）、语义无效表达式、重复发现 crowded 模板三大失败模式。**v1.27.0 已落地**：factor_registry schema 补 `llm_safety_stack` 字段（{ast_validation: bool, dsl_constrained: bool, complexity_control: bool, dual_channel_rag: bool, family_aware_selection: bool}），discovery_agent=rd_agent/efs/hubble/quantevolver 时 MUST 声明 llm_safety_stack。**个人项目适用性**：中。MVP 阶段 discovery_agent=human 不适用，Phase 2+ 启用 LLM 因子生成时 MUST 声明完整 llm_safety_stack（5 子项全 true）。

**③ QUANTEVOLVER：RL 微调 vs prompt loop（对标 factor_registry discovery_agent，v1.27.0 enum 补 quantevolver 已落地）**

[arXiv:2605.15412](https://arxiv.org/pdf/2605.15412)（Zhang-Jia-Zhai-Xie-Duan-He-Yu-Li, 西北工大+UIUC, q-fin.TR）：**QUANTEVOLVER**——基于 RL 微调的自进化 alpha 因子发现框架。核心创新：把"prompt-level 生成-评估-反馈循环"升级为 **policy updates**——Miner LLM 通过参数学习内化历史优化经验，而非在 prompt 中累积 feedback。解决 4 大问题：① context explosion（历史候选 + feedback 反复 append 导致 prompt 爆炸）；② inference cost（长 prompt 推理成本高）；③ feedback drift（累积 feedback 稀释有用信息 + 引入漂移）；④ search stagnation（大 LLM 稳定生成偏好导致结构相似表达式 + 冗余候选）。机制：高质量 seed 因子构造 + 多样 seed-time-window 训练任务 + Factor DSL 表达式生成 + Regime Backtest 评估 + Diversity-Complementarity Reward 优化。实证：3 个真实市场基准上主指标一致优于现有 LLM-based alpha 发现基线，产生更高质量 + 更互补的因子池。**比现有方法更好**：factor_registry discovery_agent 有 human/rd_agent/efs/hubble/other，但**未区分"prompt-level feedback loop"vs"RL policy update"**——前者每次推理从零开始（无学习），后者参数内化历史经验（有学习）。**v1.27.0 已落地**：factor_registry discovery_agent enum 补 `quantevolver` 选项。**个人项目适用性**：低-中。MVP 阶段 discovery_agent=human，Phase 2+ 评估 LLM 因子生成时 quantevolver 优于 hubble（前者有学习后者无学习，但 quantevolver 需 RL 微调基础设施）。

**④ Text-enhanced regime shift detection：文本+VAR 双向验证（对标 strategy_registry regime_detector，v1.27.0 enum 补 text_var_dual 已落地）**

[arXiv:2605.30363v2 2026-08-02](https://arxiv.org/pdf/2605.30363v2)（Yi-Mehra-Chen-Cartlidge, Bristol+Cardiff+Propellant Digital, q-fin.CP, FinLLM@IJCAI 2026 Long Oral）：**文本增强 regime shift 检测管线**——文本与数据双向交叉验证。核心问题：标准 regime shift 检测只读数据面板，忽略 contemporaneous 文本（FOMC minutes 等），但文本通常在价格 materialize 前数周信号化 shift。管线：① LLM 从文本提出候选 regime shift → likelihood-ratio VAR test 在数据面板验证；② 任意数据驱动检测器提出数据侧候选 → 第二次 LLM call 通过 permissive text check 接受。detector-agnostic（acceptance stage 消费候选集而非算法内部）。实证：美国国债市场 2010-2024 FOMC minutes + 14 变量 Treasury/macro 面板，F1=0.82 F2=0.86（rolling PCMCI 作为数据通道最优），same-day modal detection latency。**比现有方法更好**：strategy_registry regime_detector 有 200d_sma/hmm/wasserstein_hmm/news_aware/none，news_aware 对标 Alpha-R1 风格（LLM 推理激活/停用因子），但**未对标"文本候选+VAR 验证"双向管线**——news_aware 是单向（LLM 读新闻→调因子），text_var_dual 是双向（LLM↔VAR 互相验证）。**v1.27.0 已落地**：strategy_registry combination_strategy.regime_detector enum 补 `text_var_dual` 选项。**个人项目适用性**：低。MVP 阶段用 200d_sma，Phase 2+ 接入新闻/研报文本后评估 text_var_dual（需 LLM+VAR 基础设施）。

**⑤ Weighted Kolmogorov Metric：重尾分布回测指标（对标 risk_limit_registry drawdown/var_calibration_method，v1.27.0 enum 补 weighted_kolmogorov 已落地）**

[arXiv:2601.04490v1 2026-01-08](https://arxiv.org/pdf/2601.04490)（Petrosyan, math.PR）：**Weighted Kolmogorov Metric**——针对重尾分布的回测指标收敛性修复。核心问题：标准 KS 距离在重尾分布（E|X|³=∞ infinite skewness，如加密货币/高频 FX/A 股个股）下收敛率退化为 O(n^{-δ/2})，导致"noise barrier"——有效风险模型因无关 tail event 被拒绝。引入 exhaustion function h(x)（到均值距离）+ weight parameter q，定义 d_{K,h,q}(F,G) = sup_t w_q(t)|F(t)-G(t)|，w_q(t)=(1+h(t))^{-q}。证明在 sub-cubic moment 假设（E|X|^{2+δ}<∞）下恢复 O(n^{-1/2}) 最优高斯收敛率，适用于 Student-t(ν>2)/Pareto。关键设计：smooth downweighting 而非 winsorization/truncation（保留方向 + 相对 tail 信息，防止少数 outlier 主导分布拟合诊断）。**比现有方法更好**：risk_limit_registry drawdown_calibration_method 有 gaussian/rsb_non_gaussian/fbm_long_memory，var_calibration_method 有 historical/rwc_conformal，但**重尾分布回测指标收敛性**未覆盖——A 股个股 + 创业板重尾特性下，标准 KS 回测诊断因 tail noise 失效。**v1.27.0 已落地**：drawdown_calibration_method + var_calibration_method enum 均补 `weighted_kolmogorov` 选项（重尾策略 γ₄>8 MUST 启用）。**个人项目适用性**：中。MVP 阶段用 gaussian/historical，Phase 1.5+ 重尾策略（创业板/科创板个股）启用 weighted_kolmogorov。

**⑥ AlphaBench：标准化因子评测基准（对标 factor_registry discovery_agent 评估，v1.27.0 Phase 1.5+ 评估）**

[AlphaBench ICLR 2026](https://alphabench.cc/)（Luo, CityU-MLO, [github.com/CityU-MLO/AlphaBench](https://github.com/CityU-MLO/AlphaBench)）：首个系统化 LLM alpha 挖掘评测基准。3 核心任务：① **T1 Factor Generation**（Text2Alpha 文本→公式 + Directional Mining 主题生成 K 个多样因子）；② **T2 FactorEval**（zero-shot judge 预测因子质量无需回测——IC/RankIC/robustness/win rate/skewness 打分 + top-K 排名，**当前 LLM 最弱能力**）；③ **T3 Iterative Searching**（CoE Chain-of-Experience + ToT Tree-of-Thought + EA Evolutionary Algorithms 三范式）。覆盖 A 股 CSI300/500/1000 + 美股 SP500，1857 指令集 + FFO 执行引擎 + Qlib 回测，Assay PIT 正确回测后端（v1.25.0 已对标 PIT 语义）。**比现有方法更好**：factor_registry 有 discovery_agent 字段标记因子来源，但**无标准化评测基准**对比不同 discovery_agent 的因子质量——无法判断 human vs rd_agent vs efs vs hubble vs quantevolver 哪个产出的因子更好。**v1.27.0 评估**：Phase 1.5+ 因子发现评测时 MUST 用 AlphaBench 3 任务体系（T1 生成可靠性 + T2 评估准确性 + T3 搜索效率）对比不同 discovery_agent。**个人项目适用性**：中。MVP 阶段 discovery_agent=human 不适用，Phase 1.5+ 启用 LLM 因子生成后用 AlphaBench 评测。

> ⚠️ **v1.27.0 第十六轮总结**：6 项对标覆盖 ARM 变点归因/Hubble AST 沙箱/QUANTEVOLVER RL 微调/Text+VAR 双向 regime/Weighted Kolmogorov 重尾回测/AlphaBench 标准化评测六领域，**本轮填补前十五轮"变点归因层"+"LLM 因子生成安全标准"+"RL 微调 vs prompt loop 区分"+"文本+VAR 双向 regime 检测"+"重尾分布回测指标"+"标准化因子评测基准"六个对标空白**。**0 项新 E/G 编号**（ARM 是 §4.8 增强子步骤不新增 E；Hubble 是 schema 字段 llm_safety_stack；QUANTEVOLVER 是 enum 选项；text_var_dual 是 enum 选项；weighted_kolmogorov 是 enum 选项；AlphaBench 是 Phase 1.5+ 评估）+ **4 项 schema 字段/enum 落地**（factor_registry 补 llm_safety_stack 字段 + discovery_agent 补 quantevolver + strategy_registry regime_detector 补 text_var_dual + risk_limit_registry drawdown/var_calibration_method 补 weighted_kolmogorov）+ **2 项施工算法增强**（§4.8 补变点归因子步骤 + Phase 1.5+ AlphaBench 评测）+ **4 项 Phase 1.5+/2+ 评估**（ARM Phase 2+/Hubble AST Phase 2+/QUANTEVOLVER Phase 2+/text_var_dual Phase 2+）。**MVP 阶段无阻塞**——discovery_agent=human 不涉及 LLM 安全/regime_detector 用 200d_sma/calibration 用 gaussian+historical。**关键洞见**：本轮价值在于"引擎层补全"——ARM 补归因引擎、Hubble 补安全引擎、QUANTEVOLVER 补学习引擎、text_var_dual 补双向验证引擎、weighted_kolmogorov 补重尾回测引擎、AlphaBench 补评测引擎，6 个引擎层空白闭合。

### 4.35 第十七轮研究对标补充（v1.28.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.27.0 覆盖第一至十六轮。本轮（v1.28.0）聚焦**前十六轮未系统覆盖的上线裁决三值逻辑 + 风险归因结构分解 + 过拟合实证模式分类三领域**，经全网搜索 2026-07~08 最新研究后筛选出 **3 项对标（2 项施工算法增强 + 3 项 schema 字段落地）**。本轮核心发现：① **上线裁决是二元 pass/fail 而非三值证伪**——§4.13 PROMOTE_ENTRY G1-G9 全过=SUCCESS、否则=BLOCKED，但"统计不显著"≠"证伪"（CI 太宽=INCONCLUSIVE 应继续积累数据而非放弃），Joint Falsification 框架将"实际可部署性"定义为三门联合（统计+经济+生存）且采用 REFUTED/SUPPORTED/INCONCLUSIVE 三值裁决；② **风险贡献是单一数字而非结构分解**——risk_limit_registry 有 inherent_risk/residual_risk（NIST 控制前/后语义）但无 Leave-One-Out 分解（inherent=自身波动 vs correlation=组合协方差），单一 RC 不区分"孤立高风险"与"高相关风险"导致响应策略错配；③ **过拟合检测缺实证模式分类与量化阈值**——G2 用 PBO/DSR/CPCV 统计方法但无 PF 比值/最小交易数等一线实证信号，5 种过拟合模式分类指导"哪种过拟合"而非仅"是否过拟合"。

**① Joint Falsification 三重门框架：上线裁决的三值证伪逻辑（对标 §4.13 PROMOTE_ENTRY 裁决逻辑 + experiment_registry，v1.28.0 已落地）**

[arXiv:2607.20093v1 2026-07-22](https://arxiv.org/abs/2607.20093)（Darmanin, Hecatus Research, q-fin.ST/RM/TR）：**Retail Trader's Ruin**——首个将"实际可部署性"（practical viability）定义为**三门联合证伪**（joint falsification）的框架。核心论点：一个信号家族的实用价值 = 三个**预声明**门禁的合取（conjunction）：① **统计 edge 门**（multiplicity correction 后仍显著——stationary-bootstrap 95% CI + hierarchical Benjamini-Yekutieli 控制 + 单侧 claim-exclusion 检验 + 等价性检验）；② **经济可行性门**（net-of-cost 后超过预声明 materiality 阈值 δ_S=0.20 年化 Sharpe-gap——exposure-matched benchmark 而非裸 buy&hold）；③ **有限资金生存门**（FINRA/ESMA 杠杆场景下不破产——重尾放大波动下 ruin probability）。**三值裁决**（非二元 pass/fail）：**REFUTED**（CI 上界 < δ_S，置信区间排除声明效应=证伪放弃）；**SUPPORTED**（CI 下界 > δ_S，置信区间超过 materiality 阈值=支持部署）；**INCONCLUSIVE**（CI 跨越 δ_S，样本不足无法裁决=继续积累数据而非放弃）。实证：5 类零售信号家族（trend/oscillator/candlestick/volume/calendar）中 4 类 REFUTED、trend INCONCLUSIVE（CI 太宽而非无 edge）、0 类 SUPPORTED；momentum 正控制也被判 INCONCLUSIVE（未假阳性证伪=设计有效性签名）。**比现有方法更好**：§4.13 PROMOTE_ENTRY G1-G9 是**二元裁决**——全过=SUCCESS（active）、否则=BLOCKED（修复后重申）。但**"统计不显著"≠"证伪"**：G2 因 PBO/DSR 不通过而 BLOCKED 的策略，可能是样本不足（INCONCLUSIVE）而非真无 edge（REFUTED）——前者应继续 probation 积累数据，后者应放弃。二元裁决把两者混为一谈，要么过早放弃真 edge（INCONCLUSIVE 误判 REFUTED），要么反复重申已死策略（REFUTED 误判 INCONCLUSIVE）。Joint Falsification 的三值逻辑区分两者：INCONCLUSIVE → 继续 Shadow/Canary 积累样本；REFUTED → RETIRE_ENTRY 放弃；SUPPORTED → PROMOTE_ENTRY 全量上线。**v1.28.0 已落地**：① experiment_registry schema 补 `viability_verdict` 字段（supported/refuted/inconclusive，三值裁决结果）；② §4.13 门禁裁决逻辑增强三值分类注释——gates_failed 含 G1/G2 统计门失败时，若 bt.oos_period_months < min_trl_years（样本不足）→ INCONCLUSIVE（继续 probation），否则 → REFUTED（放弃走 RETIRE_ENTRY）。**个人项目适用性**：高。MVP 阶段 OOS<3 月时 viability_verdict=inconclusive（诚实记录"样本不足无法裁决"），Phase 1.5+ MinBTL 达标后才能 supported/refuted。关键治理价值：避免"3 个月 OOS 不显著就放弃"的过早弃真错误。

**② Leave-One-Out 风险贡献分解：inherent vs correlation 风险结构（对标 risk_limit_registry，v1.28.0 schema 补 risk_contribution_decomposition 已落地）**

[arXiv:2604.10375v1 2026-04-11](https://arxiv.org/abs/2604.10375)（Alexander & Fabozzi, UVA + JHU Carey, q-fin.RM/PM，[github.com/nolanalexander/inherent-correlation-decomposition](https://github.com/nolanalexander/inherent-correlation-decomposition)）：将标准 Risk Contribution（RC）分解为两个经济可解释分量——**inherent risk**（仓位自身波动贡献，独立于组合，恒为正）+ **correlation risk**（与其余组合的协方差，可放大或对冲）。基于 leave-one-out 表示：移除某仓位后组合风险的变化 = 该仓位的 iVol（incremental volatility，非加性），而 RC = inherent + correlation 严格加性。**诊断洞察**：单一 RC 数字不区分"该仓位因孤立波动大而风险高"vs"因与其余组合高相关而风险高"——两者响应策略完全不同：inherent 高 → 降低该仓位暴露；correlation 高 → 分散化或加对冲仓位。correlation 为负 → 有效对冲（reduce total portfolio risk）。时序分析追踪 inherent/correlation 风险跨 regime 演化，揭示压力期组合风险上升是波动冲击、相关性偏移、还是两者兼有——这对 stress testing 和 performance attribution 至关重要。**比现有方法更好**：risk_limit_registry 有 `inherent_risk`/`residual_risk`（v1.2.0，NIST NISTIR 8286 语义：inherent=控制前、residual=控制后），但**这是"控制前/后"语义，非"自身波动/组合协方差"语义**——两个"inherent"含义完全不同。NIST inherent 回答"加风控前风险多大"，LOO inherent 回答"该仓位风险多少来自自身 vs 多少来自与组合的相关性"。单一 RC 数字（如某仓位贡献组合波动 30%）不告诉你是该降仓位（inherent 主导）还是该加对冲（correlation 主导）——响应策略错配=风控失效。**v1.28.0 已落地**：risk_limit_registry schema 补 `risk_contribution_decomposition` 字段（{inherent_component: float, correlation_component: float, decomposition_method: enum(loo/standard_rc/none)}），concentration/var 类限额声明。**个人项目适用性**：中。MVP 阶段用 standard_rc（单一 RC 数字足够，持仓数<10 人工判断），Phase 1.5+ 持仓数>20 时 MUST 用 loo 分解（精准定位"降仓位"vs"加对冲"的响应策略）。

**③ Backtest OVERFIT 5 模式 + PF 比值阈值：过拟合实证模式分类（对标 §4.13 G2 门禁 + experiment_registry，v1.28.0 G2 增强 + schema 补 overfit_pattern 已落地）**

[dibi8 2026-05-25 "Backtest OVERFIT: 5 Typical Patterns"](https://dibi8.com/resources/ai-trading/backtest-overfit-5-patterns-2026/)（50+ live trades 实证目录，vectorbt/backtrader 复现）：将回测过拟合分为 **5 种实证模式**（非统计方法，而是"过拟合长什么样"的形态分类）：① **walk-forward divergence**（IS 持续优化但 OOS 反而变差——moss-trade-bot Train PF 2.08→OOS PF 0.94，ratio 2.21）；② **regime-flip**（某 regime 下 Sharpe 1.8，另一 regime -0.4——edge 依赖 regime 特定动态）；③ **parameter-cliff**（参数微偏性能骤降——最佳参数是孤立岛而非高原）；④ **indicator-stacking**（堆叠多个相关指标伪提升 IS——OOS 噪声放大）；⑤ **survivorship**（仅存活标的回测——退市标的的亏损不可见）。**量化检测信号**：**Train PF / OOS PF ratio**——>1.5 suspect、>2.0 textbook overfit；**最小交易数阈值**——directional 300 笔、mean-reversion 500 笔、优化过 1000+ 笔（低于此数统计不显著）。检测管线：70/30 IS/OOS 切分 → PF ratio 门 → 参数敏感性 sweep → regime 分层测试 → Monte Carlo 信号打乱对比。**比现有方法更好**：§4.13 G2 用 PBO/DSR/PSR/CPCV/MTC 六统计方法回答"**是否**过拟合"，但不回答"是**哪种**过拟合"——不同模式修复策略不同（walk-forward divergence→减少参数；regime-flip→加 regime gating；parameter-cliff→取高原参数；indicator-stacking→去相关指标；survivorship→PIT universe）。且 G2 缺 PF ratio 和最小交易数两个**一线实证阈值**——它们计算极简（PF=盈利和/亏损和，无需 PBO/DSR 的 CSCV/bootstrap），是统计方法前的快速筛。**v1.28.0 已落地**：① §4.13 G2 增强——新增 PF ratio 子检查（`bt.train_pf / bt.oos_pf > 2.0` = 阻断；`> 1.5` = warning）+ 最小交易数子检查（`bt.oos_trade_count < 300` directional / `< 500` mean_reversion = warning，样本不足）；② experiment_registry schema 补 `overfit_pattern` 字段（enum: none/walk_forward_divergence/regime_flip/parameter_cliff/indicator_stacking/survivorship，记录检测到的过拟合模式分类）。**个人项目适用性**：高。MVP 阶段 PF ratio 是最易计算的过拟合信号（无需 PBO/DSR 基础设施），min trade count 防止"30 笔交易就声称 edge"的小样本谬误。Phase 1.5+ 配合 PBO/DSR 形成统计+实证双轨检测。

> ⚠️ **v1.28.0 第十七轮总结**：3 项对标覆盖 Joint Falsification 三重门/Leave-One-Out 风险分解/Backtest OVERFIT 5 模式三领域，**本轮填补前十六轮"上线裁决三值逻辑"+"风险贡献结构分解"+"过拟合实证模式分类"三个对标空白**。**0 项新 E/G 编号**（三值裁决是 §4.13 裁决逻辑增强不新增 G；PF ratio/min trade count 是 G2 子检查增强不新增 G；LOO 分解是 schema 字段）+ **3 项 schema 字段已落地**（experiment_registry 补 viability_verdict + overfit_pattern + risk_limit_registry 补 risk_contribution_decomposition）+ **2 项施工算法增强**（§4.13 G2 补 PF ratio+min trade count 子检查 + §4.13 裁决逻辑补三值分类注释）+ **0 项 Phase 1.5+ 评估**（三值裁决/PF ratio/min trade count 均为 MVP 可用的轻量增强，LOO 分解 MVP 用 standard_rc）。**MVP 阶段无阻塞**——viability_verdict MVP 填 inconclusive（诚实记录样本不足）、overfit_pattern 填 none/walk_forward_divergence（PF ratio 自动可算）、risk_contribution_decomposition MVP 用 standard_rc。**关键洞见**：本轮价值在于"裁决哲学升级"——Joint Falsification 把二元 pass/fail 升级为三值 REFUTED/SUPPORTED/INCONCLUSIVE，区分"样本不足"与"真无 edge"，避免过早弃真（INCONCLUSIVE 误判 REFUTED）和反复重申死策略（REFUTED 误判 INCONCLUSIVE）；PF ratio/min trade count 是统计方法前的"一线快速筛"，计算极简但覆盖小样本谬误和 IS-OOS 发散两大常见陷阱；LOO 分解把单一 RC 数字升级为 inherent+correlation 结构，精准匹配"降仓位"vs"加对冲"响应策略。

### 4.36 第十八轮研究对标补充（v1.29.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.28.0 覆盖第一至十七轮。本轮（v1.29.0）聚焦**前十七轮未系统覆盖的因子发现自主性评估维度 + 优化时反过拟合目标函数 + 调参-验证分离双重筛查三领域**，经全网搜索 2026-08 最新研究后筛选出 **3 项对标（1 项 schema 字段落地 + 2 项 Phase 1.5+ 评估）**。本轮核心发现：① **因子发现自主性缺系统评估维度**——v1.27.0 第十六轮 AlphaBench 提供 T1/T2/T3 三任务评测基准，但未定义"自主性"的评估维度（什么算"自主"？搜索效率？fitness 可靠性？残余 alpha 质量？），EC 综述的六组件框架+八维自主性评估填补此空白；② **反过拟合是检测时而非优化时**——v1.28.0 G2 有 PBO/DSR/CPCV/PF ratio 六方法+一实证信号，但全部是"事后检测"（回测完成后判断是否过拟合），GT-Score 首次提出"优化时嵌入反过拟合结构"（把 performance+significance+consistency+downside risk 组合为单一目标函数，让优化器主动避开过拟合路径）；③ **调参与验证未显式分离**——§4.13 PROMOTE_ENTRY 有 G1-G9 九门禁，但隐含"同一数据既调参又验证"风险，AutoQuant 双重筛查（Stage I 贝叶斯调参+Stage II 严格回测验证）显式分离两阶段。

**① Alpha 发现 EC 综述：六组件框架 + 八维自主性评估（对标 factor_registry discovery_agent 评估，v1.29.0 Phase 1.5+ 评估）**

[arXiv:2608.01789v1 2026-08-03](https://arxiv.org/html/2608.01789v1)（Yu-Fu-Fan-Li-Gao-Xu, 上海大学+西交利物浦, cs.NE）：首个将自动公式化 alpha 发现系统化为**进化计算（EC）**视角的综述。**六组件分析框架**：① Representation（搜索空间定义——DSL/语法树/代码）；② Variation（候选生成——GP 交叉变异/RL 序列生成/LLM 提示）；③ Fitness Evaluation（质量评估——IC/RankIC + 覆盖率/换手率/复杂度 + HAC 显著性）；④ Selection（因子池更新——精英保留/锦标赛/family-aware）；⑤ Memory（经验积累——验证记忆池/反射/自进化）；⑥ Adaptation（regime 响应——市场状态切换时因子池调整）。**八维自主性评估协议**：search efficiency（搜索效率——单位计算预算下发现有效因子数）、fitness reliability（fitness 可靠性——噪声下评估稳定性）、residual alpha quality（残余 alpha 质量——去相关后独立 alpha 贡献）、economic diversity（经济多样性——非语法多样性，因子经济逻辑覆盖不同维度）、tradability（可交易性——扣成本后收益+容量）、evolutionary autonomy（进化自主性——无需人工干预的迭代轮数）、market-logic grounding（市场逻辑锚定——因子的经济解释性）、reproducibility（可复现性——跨数据/种子稳定性）。**比现有方法更好**：v1.27.0 第十六轮 AlphaBench 提供 T1 生成/T2 评估/T3 搜索三任务评测基准，但**未定义"自主性"的评估维度**——AlphaBench 回答"不同 discovery_agent 的因子质量如何"，EC 综述回答"什么算自主发现 + 如何系统评估自主性"。八维评估协议为 AlphaBench 评测提供维度框架。**v1.29.0 评估**：Phase 1.5+ AlphaBench 评测时 MUST 用八维自主性评估协议补充——不只评 T1/T2/T3 任务表现，还评 search efficiency/residual alpha quality/evolutionary autonomy 等维度。**个人项目适用性**：中。MVP 阶段 discovery_agent=human 不适用，Phase 1.5+ 启用 LLM 因子生成后用八维评估对比 human vs rd_agent vs efs vs hubble vs quantevolver。

**② GT-Score：优化时反过拟合复合目标函数（对标 §4.13 G2 过拟合检测，v1.29.0 Phase 1.5+ 评估）**

[arXiv:2602.00080 2026-01-22](https://arxiv.org/pdf/2602.00080)（Sheppert, Capitol Technology University, JRFM 2026, q-fin.ST）：**GT-Score（Golden Ticket Score）**——将反过拟合结构**直接嵌入优化目标函数**的复合指标。核心创新：现有反过拟合方法（PBO/DSR/CPCV 等）都是**事后检测**——回测完成后判断是否过拟合，但优化器在搜索过程中仍以单一指标（如 Sharpe/收益）为目标，容易走偏到过拟合路径。GT-Score 把四个维度组合为单一目标：① Performance（收益——年化回报/Sharpe）；② Statistical Significance（统计显著性——p-value 校正多重检验后）；③ Consistency（一致性——walk-forward 各折稳定性/子样本稳定性）；④ Downside Risk（下行风险——最大回撤/Sortino）。walk-forward 验证（9 折时序切分）+ Monte Carlo（15 种子×3 策略）实证：GT-Score 优化目标的**泛化比**（验证收益/训练收益）比基线目标函数（Sharpe/Sortino/Simple）提升 **98%**，Monte Carlo OOS 收益统计显著差异（p<0.01）。**比现有方法更好**：§4.13 G2 有 PBO/DSR/PSR/MinBTL/MTC/CPCV 六统计方法 + PF ratio/min trade count 两实证信号（v1.28.0），但**全部是检测时（detection-time）而非优化时（optimization-time）**——优化器以 Sharpe 为目标走偏到过拟合路径后，G2 才事后发现并阻断。GT-Score 把"反过拟合"从检测端移到优化端——优化器在搜索过程中就考虑 significance+consistency+downside，主动避开过拟合路径。**v1.29.0 评估**：Phase 1.5+ 参数搜索/策略优化时 MUST 评估用 GT-Score 替代单一 Sharpe 作为优化目标——walk-forward 各折一致性 + 多重检验校正 p-value + 下行风险惩罚组合为复合目标。**个人项目适用性**：中。MVP 阶段用 Sharpe 为目标 + G2 事后检测足够，Phase 1.5+ 参数搜索规模增大后用 GT-Score 从源头降低过拟合风险。

**③ AutoQuant 双重筛查：调参与验证显式分离（对标 §4.13 PROMOTE_ENTRY 流程，v1.29.0 Phase 1.5+ 评估）**

[arXiv:2512.22476v3 2026-08-07](https://arxiv.org/html/2512.22476v3)（Deng, 广州工商学院, q-fin.TR）：**AutoQuant**——可审计专家系统框架，核心创新是**双重筛查（Double Screening）**——Stage I 贝叶斯自动调参（TPE 优化器在真实成本约束下搜索参数）与 Stage II 严格回测验证（4h 独立回测+双重筛查门禁）**显式分离**。Stage I 用 TPE（Tree-structured Parzen Estimator）而非网格搜索/进化方法/GP-BO 的理由：TPE 在高维参数空间中样本效率最高，且天然支持真实成本约束（funding rate/slippage/leverage）嵌入优化目标。Stage II 用独立 4h 回测验证 Stage I 选出的参数——**关键设计**：Stage I 的优化数据和 Stage II 的验证数据**不重叠**（防 data snooping）。双筛查门禁：① 成本筛查（含真实摩擦的 OOS 收益>0）；② 稳健性筛查（跨资产/跨种子一致性）。实证：朴素回测 vs 严格回测差异巨大（BTC 永续期货，年化差异 40%+），双重筛查后存活率<10%。**比现有方法更好**：§4.13 PROMOTE_ENTRY 有 G1-G9 九门禁，但**隐含"同一数据既调参又验证"风险**——策略开发者在历史数据上反复调参，然后同一历史数据上跑 G1-G9 门禁验证，data snooping 不可消除。AutoQuant 的 Stage I/Stage II 数据分离显式阻断此路径——调参数据和验证数据物理隔离。**v1.29.0 评估**：Phase 1.5+ 参数搜索时 MUST 评估 Stage I/Stage II 数据分离——Stage I 用 walk-forward 前段调参，Stage II 用 walk-forward 后段独立验证，两段数据不重叠。**个人项目适用性**：中。MVP 阶段 walk-forward 已有 IS/OOS 切分（70/30），Phase 1.5+ 参数搜索规模增大后 MUST 显式分离 Stage I 调参数据 vs Stage II 验证数据（CPCV 的 purge+embargo 是此思路的更严格版本，v1.16.0 已对标）。

> ⚠️ **v1.29.0 第十八轮总结**：3 项对标覆盖 Alpha 发现 EC 综述/GT-Score 优化时反过拟合/AutoQuant 双重筛查三领域，**本轮填补前十七轮"因子发现自主性评估维度"+"优化时反过拟合目标函数"+"调参-验证分离"三个对标空白**。**0 项新 E/G 编号**（EC 综述是 Phase 1.5+ AlphaBench 评估维度补充不新增 E；GT-Score 是 Phase 1.5+ 优化目标评估不新增 G；AutoQuant 是 Phase 1.5+ 流程评估不新增 G）+ **0 项 schema 字段落地**（3 项均为 Phase 1.5+ 评估，MVP 阶段无阻塞）+ **3 项 Phase 1.5+ 评估**（AlphaBench 八维自主性评估 + GT-Score 优化目标 + AutoQuant Stage I/II 数据分离）。**MVP 阶段无阻塞**——discovery_agent=human 不涉及自主性评估、优化目标用 Sharpe+G2 事后检测、walk-forward 70/30 IS/OOS 切分足够。**关键洞见**：本轮价值在于"时间轴前移"——GT-Score 把反过拟合从"检测时"（detection-time）移到"优化时"（optimization-time），AutoQuant 把数据隔离从"验证时"移到"调参时"，EC 综述把评估从"结果时"移到"过程时"——三者在时间轴上各自前移一步，从源头降低过拟合风险而非事后发现。

### 4.37 第十九轮研究对标补充（v1.30.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.29.0 覆盖第一至十八轮。本轮（v1.30.0）聚焦**前十八轮未系统覆盖的回撤路径依赖疼痛度量 + 执行冲击模型谱系 + 基准风格漂移检测 + 治理别名模式四领域**，经全网搜索 2026-08 最新研究后筛选出 **4 项对标（4 项 schema 字段落地 + 1 项治理模式验证 + 1 项跨文档边界重申）**。本轮核心发现：① **回撤校准有深度阈值但无路径依赖疼痛度量**——risk_limit_registry 有 drawdown_calibration_method（v1.23.0 RSB 非高斯深度校准）+ risk_contribution_decomposition（v1.28.0 LOO 结构分解），但缺 Ulcer Index/Calmar/Martin Ratio/Pain Index 等**路径依赖**度量（深度×持续时间），单一 max_drawdown 不区分"20% 回撤 2 周恢复"与"20% 回撤 18 个月恢复"——前者可忍受后者触发赎回；② **执行冲击模型只有 square-root 单一形态**——cost_model 有 square_root law（v1.1.0）+ market_impact_model 引用（v1.20.0），execution_algo 有 tca_metrics 双报告（v1.7.0），但缺 I-Star（Kissell-Glantz 2003）/Propagator（Bouchaud-Farmer 2018）/Algo Wheel（2026 实时路由）的模型谱系登记，impact_model_type 字段缺失导致回测无法声明所用冲击模型；③ **基准登记只有标识无构造方法与漂移检测**——benchmark_registry 4 条 entry 有 benchmark_type/weight_method 但无 construction_method（holdings_based/returns_based/index_provider）/active_share/style_drift_detection，且 2026 "大基准重置"（Russell 半年再平衡+S&P 咨询）使基准方法论本身在漂移；④ **版本晋升有 Shadow→Canary→Full 三阶段但无别名指针**——§4.13 PROMOTE_ENTRY 渐进式部署（v1.10.0）用 status 字段标记阶段，MLflow 3.15.0 MCP Registry 的 promotable aliases（@production/@staging）模式提供更轻量的"别名指针"替代 status 翻转。

**① 回撤路径依赖疼痛度量：Ulcer Index + Calmar + Martin Ratio + Pain Index（对标 risk_limit_registry + experiment_registry，v1.30.0 schema 字段已落地）**

[metricgate 2026-05-20 Ulcer Index](https://metricgate.com/docs/ulcer-index-drawdown/) + [algostrategyanalyzer 2026-01-27 Drawdown Guide](https://algostrategyanalyzer.com/en/blog/drawdown-trading-guide/) + [mlq.ai 2026 Drawdown Analysis](https://mlq.ai/academy/lesson/python-quant-finance-drawdown-analysis/)：**路径依赖（path-dependent）回撤度量**族——区别于 max_drawdown（单一深度标量）和 VaR（分布尾部），路径依赖度量同时编码**深度×持续时间**，反映投资者实际"疼痛体验"。四种核心度量：① **Ulcer Index**（Martin 1989）= drawdown 序列的二次均值 `UI = √(Σ D_t² / N)`，零当价格创新高，随深度和持续时间增长——UI 0-2% 极低风险 / 2-5% 中等 / 5-10% 升高 / >10% 深度或持续；② **Ulcer Performance Index / Martin Ratio** = 年化超额收益 / Ulcer Index，是 drawdown 版 Sharpe（Sharpe 用波动率，UPI 用 drawdown 疼痛），UPI > Sharpe 说明回撤相对浅；③ **Calmar Ratio** = 年化收益 / |max_drawdown|，>1.0 可接受 / >3.0 优秀；④ **Pain Index** = drawdown 序列的算术均值（非二次），比 Ulcer 更平滑。配套：**underwater equity curve**（drawdown 时序图，每段谷的深度=严重性、宽度=持续时间）、**recovery time**（从谷底回到前高的天数）、**Pain Ratio** = 收益 / Pain Index。**关键洞察**：两个策略相同 max_drawdown=20% 但 Ulcer Index 可能差 5 倍——2 周恢复的 UI≈2% vs 18 个月恢复的 UI≈10%——前者投资者能持有后者触发赎回。Sharpe Ratio 从回测到实盘降 30-50%（slippage/延迟/市场条件），Calmar/UPI 因基于已实现回撤更稳健。**比现有方法更好**：risk_limit_registry 有 `drawdown_calibration_method`（v1.23.0 RSB 非高斯校准）回答"回撤阈值如何校准"和 `risk_contribution_decomposition`（v1.28.0 LOO）回答"风险贡献结构如何分解"，但**两者都不编码路径依赖疼痛**——RSB 校准 max_drawdown 深度阈值，LOO 分解风险来源，均无"回撤持续多久"维度。experiment_registry 有 max_drawdown/sharpe/sortino 但无 ulcer_index/calmar_ratio。单一 max_drawdown 把"2 周 20%"与"18 个月 20%"等同——前者可忍受后者触发赎回，响应策略完全不同（前者继续持有后者减仓/对冲）。**v1.30.0 已落地**：① risk_limit_registry schema 补 `pain_metric` 字段（{metric_type: enum(ulcer_index/pain_index/none), threshold: float, monitoring_window_days: int}，drawdown 类限额声明疼痛阈值）；② experiment_registry schema 补 `ulcer_index` + `calmar_ratio` 两字段（回测结果路径依赖度量）。**个人项目适用性**：高。MVP 阶段 ulcer_index/calmar_ratio 计算极简（pandas cummax + 二次均值，<10 行），是 max_drawdown 的天然补充。Calmar>1.0 作为 PROMOTE_ENTRY G1 回测验证的补充信号。

**② 执行冲击模型谱系：I-Star + Propagator + Algo Wheel（对标 execution_algo_registry + cost_model_registry，v1.30.0 schema 字段已落地）**

[youngju.dev 2026-05-25 TCA Deep Dive](https://www.youngju.dev/transcribe/culture/2026-05-25-tca-market-impact-implementation-shortfall-almgren-chriss-kissell-bloomberg-btca-virtu-big-xyt-2026-deep-dive.en) + [hftradingbook 2026-06-04 Market Impact](https://hftradingbook.com/costs/market-impact) + [arXiv:2603.29086v1 2026-03 MACE RL](https://arxiv.org/html/2603.29086v1)：**2026 TCA 从"事后报告"转向"实时 Algo Wheel"**——每笔订单基于历史 TCA 数据自动路由到最优 broker/algorithm。冲击模型谱系（按时间线）：① **Implementation Shortfall**（Perold 1988）= 决策价与实际成交价差，分解为执行成本+延迟成本+机会成本，4 桶模型（commission/spread/impact/timing）；② **Almgren-Chriss**（2000）= 均值-方差最优执行 `min E[Cost]+λ·Var[Cost]`，线性永久冲击+临时冲击，λ 风险厌恶参数；③ **Square-root law**（Gatheral 2010）= `ΔP≈Y·σ·√(Q/V)`，凹性（concave）使冲击随规模次线性增长，无动态套利约束下唯一存活形式；④ **I-Star**（Kissell-Glantz 2003）= 市场冲击定价模型，将冲击分解为瞬时+永久分量并基于订单规模/ADV/波动率定价；⑤ **Propagator**（Bouchaud-Farmer 2018）= 瞬态冲击模型，捕获冲击的非线性时间序列结构（临时冲击衰减+永久冲击残留），是 Almgren-Chriss 二分法的连续精细化——`η·n/τ`(temporary rate) + `γ·Q`(permanent size)，propagator 用核函数描述冲击随时间的衰减传播。**关键洞察**：square-root 是 Almgren-Chriss 的经验近似（永久冲击线性+临时冲击平方根），propagator 是更精细的瞬态建模。MACE RL（arXiv:2603.29086v1）实证：固定 10bps 基线 vs Almgren-Chriss 模型导致 RL agent 行为和排名**质变**——PPO 在基线下 OOS 最佳（20% return, Sharpe 1.06）但 AC 下降至 15%，TD3 在 AC 下反而提升（15%→18%）；TD3 日成本从 $200k 降至 $8k，换手从 19% 降至 1%。**监管**：MiFID II RTS 28（firm-side best execution reporting）在 2024 MiFIR review 下重新审查；KOFIA 2025 修订 Best Execution Guideline 强制季度 TCA 报告；SEC Rule 605/606 2024 修订扩展零售订单流披露。**比现有方法更好**：cost_model 有 square_root law（v1.1.0）+ `market_impact_model` 引用 40 号 propagator/Barzykin（v1.20.0），execution_algo 有 `tca_metrics` 双报告（v1.7.0 反博弈+VWAP slippage+IS），但**无 impact_model_type 字段声明回测所用冲击模型**——回测 entry 无法声明用的是 square_root / Almgren-Chriss / I-Star / Propagator 哪一种，导致同策略不同冲击模型结果不可比（MACE 实证差异 40%+）。**v1.30.0 已落地**：① execution_algo_registry schema 补 `impact_model_type` 字段（enum: square_root/almgren_chriss/i_star/propagator/fixed_bps/pluggable，声明回测/实盘所用冲击模型）；② cost_model_registry schema 补 `propagator_config` 字段（{decay_kernel: enum(exponential/power_law), temp_impact_coeff: float, perm_impact_coeff: float}，propagator 模型参数化）；③ Algo Wheel 实时路由=Phase 1.5+ 评估（个人项目订单量小，broker 单一无需实时路由）。**个人项目适用性**：中。MVP 阶段用 square_root（已落地，参数少），Phase 1.5+ 订单量增大后 MUST 评估升级到 Almgren-Chriss（均值-方差最优执行）或 propagator（瞬态建模）。

**③ 基准风格漂移检测 + 2026 大基准重置：custom benchmark construction + active share + style drift（对标 benchmark_registry，v1.30.0 schema 字段已落地）**

[stockalpha.ai 2026-02-17 Custom Benchmarks](https://stockalpha.ai/alpha-learning/custom-benchmarks-for-truth-detecting-hidden-style-drift-and-false-alpha) + [nasdaq.com 2026-06 Great Benchmark Reset](https://www.nasdaq.com/articles/great-benchmark-reset) + [ssga.com 2026-04-20 Custom LDI Benchmark](https://www.ssga.com/us/en/institutional/insights/creating-a-custom-ldi-benchmark-through-cash-flow-analysis)：**2026 是基准构造方法论数十年来最显著的变革年**——FTSE Russell 和 S&P Dow Jones 同时审查主要指数方法论（再平衡时序/IPO 纳入/风格分类/资格）。Russell 从年度改半年再平衡（美国指数框架多年最重大变更），Russell 1000 Growth/Value 重大风格迁移（Amazon 成最大 Value 成分股，半导体占 Growth 32% vs 24%），mega cap 快速纳入 IPO 新规，浓度管理框架 revisiting；S&P 完成 seasoning/float/profitability 要求咨询。**核心论点**：基准提供者越来越主动做纳入/分类/方法论决策——"被动基准"本身越来越不被动。**Custom benchmark construction 两路线**：① **Holdings-based**（首选）= 直接从组合成分构建指数复制暴露+可投资性约束（liquidity/free-float filters/weight caps/turnover limits），constrained optimization 匹配因子暴露同时最小化 tracking error，issuer-level 粒度；② **Returns-based** = 持仓不可得时用回归推断暴露，快速但精度低。**风格漂移检测三方法**：① rolling regressions（滚动因子暴露变化）；② exposure attribution（暴露归因）；③ holdings similarity（持仓相似度，Jaccard/cosine）。**关键度量**：**active share**（组合持仓与基准差异百分比，指示 concentration/overlap）、**tracking error**（主动收益标准差）、**information ratio**（主动收益/跟踪误差）。**比现有方法更好**：benchmark_registry 4 条 entry 有 benchmark_type/weight_method/annual_return/sharpe/max_drawdown，但**无 construction_method（holdings_based/returns_based/index_provider）/active_share/style_drift_detection**——无法声明基准如何构造、组合相对基准多主动、是否监控风格漂移。2026 大基准重置使"基准方法论稳定性"假设失效——半年再平衡+风格迁移意味着基准本身在变，benchmark_registry MUST 登记 construction_method + 再平衡频率以追踪基准方法论演进。**v1.30.0 已落地**：benchmark_registry schema 补 `construction_method`（enum: index_provider/holdings_based/returns_based/custom，声明基准构造路线）+ `active_share`（float，组合 vs 基准持仓差异百分比，BMK-ABSOLUTE-001 零基准填 null）+ `style_drift_detection`（obj: {method: enum(rolling_regression/holdings_similarity/none), monitoring_frequency: str}，风格漂移检测配置）三字段。**个人项目适用性**：中。MVP 阶段 4 条 entry 中 BMK-INDEX-001/002/003 是 index_provider（中证指数公司官方），BMK-ABSOLUTE-001 是 absolute（零基准），construction_method 填 index_provider/absolute 即可，active_share/style_drift_detection 填 null/none（单策略无需漂移检测）。Phase 1.5+ 多策略+因子暴露管理时 MUST 启用 active_share 监控 + rolling regression 漂移检测。

**④ MCP Registry semver + promotable aliases：版本晋升的别名指针模式（对标 §4.13 PROMOTE_ENTRY 渐进式部署，v1.30.0 治理模式验证）**

[MLflow 3.15.0 2026-07-31 MCP Registry](https://www.mlflow.org/releases/3.15.0/) + [introl.com 2026-03-28 Model Versioning Infrastructure](https://introl.com/nl/blog/model-versioning-infrastructure-mlops-artifact-management-guide-2025) + [mlflow.org 2026-06-10 Team Collaboration](https://mlflow.org/articles/team-collaboration-tools-for-ai-development-in-2026/)：**MCP Registry**（Model Context Protocol servers 的集中化目录）——每个 server 获得 semver 版本化配置 + **promotable aliases**（`@production` / `@staging` 可提升别名）+ tags 组织。MLflow auto-discover 每个 server 暴露的 tools，生成 Claude Code 和 `.mcp.json` 连接指令。Model Registry 模式：每个 registered model version 携带完整 lineage record（run ID + Git commit + dataset hash + parameters），DEV→STAGING→PROD 晋升是 first-class operation 每阶段记录 approver，**pinning model versions to immutable references like Git SHAs reduces incident root cause analysis difficulty by up to 70%**。sub-10-second rollbacks via registry-based stage pointers（re-point config to previous bundle，无文件复制/服务重启）。**比现有方法更好**：§4.13 PROMOTE_ENTRY 渐进式部署（v1.10.0）用 `status` 字段标记 Shadow→Canary→Full 三阶段，但**每次阶段转换需 EVOLVE_ENTRY 翻转 status**（写操作+版本快照+依赖方影响分析）。MCP Registry 的 promotable aliases 模式更轻量——`@production` 别名指针指向某 version，晋升=移动指针（O(1) 元数据操作，无 entry 变更），rollback=指针回退。**关键区别**：status 翻转是"entry 状态机转换"（重，需审计），alias 指针是"版本标签重定向"（轻，可快速 flip-flop）。**v1.30.0 治理模式验证**：12 注册表体系已用 semver（version 字段）+ status 状态机，MCP Registry 的别名指针模式可作为 Phase 2+ DB 阶段的**轻量部署指针**评估——`@active`/`@canary`/`@shadow` 别名指向特定 version，部署切换=移动别名而非翻转 status。MVP 阶段 YAML + status 翻转足够（git commit 天然提供 immutable reference，root cause analysis 难度已降低），Phase 2+ DB 阶段评估别名指针。**个人项目适用性**：低（治理模式验证，非 schema 字段）。本轮记录此对标作为"未来 DB 阶段部署指针"的决策依据，MVP 阶段不实施。

> 🔗 **跨文档边界重申（HRP-μ/CRISP 组合构建算法）**：v1.21.0 §4.28⑥ 已将 CRISP/HRP-μ（arXiv:2604.23833 信号感知层级组合构建）DEFERRED 至 52/54 号文档（组合权重构建属回测引擎+归因报告职责，非注册表职责）。本轮（v1.30.0）全网搜索 [arXiv:2604.23833](https://arxiv.org/abs/2604.23833) 最新进展（HRP-μ signed inverse-variance + 2×2 mean-variance split, γ=0 nests HRP；HRP-Σμ recursive MVO + L1 normalization for sign-flip pathology；CRISP correlation-insensitive signal-aware）后**重申此边界**——strategy_registry 登记策略元数据（含 combination_strategy regime 融合配置），组合权重构建算法（HRP/HRP-μ/CRISP/Markowitz/min-variance）的实现属 52 号回测引擎，strategy_registry 仅作 `portfolio_construction_method` 引用字段（如已登记的 `market_impact_model` 引用 40 号 propagator 模式）而不实现算法。**不新增 schema 字段**——避免与 52/54 号文档职责重叠（project_memory 跨文档职责边界原则）。如未来 52 号文档需要 strategy_registry 声明所用组合构建方法，可加 `portfolio_construction_method` enum 字段（equal_weight/risk_parity/hrp/hrp_mu/hrp_sigma_mu/crisp/markowitz/min_variance）作 metadata 引用，但本轮不实施，待 52 号文档施工时协同决策。

> ⚠️ **v1.30.0 第十九轮总结**：4 项对标覆盖 Ulcer/Calmar 路径依赖疼痛度量/I-Star+Propagator+Algo Wheel 执行冲击谱系/Custom Benchmark+Active Share 基准漂移/MCP Registry 别名指针四领域，**本轮填补前十八轮"回撤路径依赖度量"+"执行冲击模型谱系登记"+"基准构造与漂移检测"+"部署别名指针模式"四个对标空白**。**0 项新 E/G 编号**（4 项均为 schema 字段落地，疼痛度量/冲击模型/基准构造/别名指针均不新增审计门禁）+ **4 项 schema 字段已落地**（risk_limit_registry 补 pain_metric + experiment_registry 补 ulcer_index+calmar_ratio + execution_algo_registry 补 impact_model_type + cost_model_registry 补 propagator_config + benchmark_registry 补 construction_method+active_share+style_drift_detection 三字段）+ **1 项治理模式验证**（MCP Registry promotable aliases 作为 Phase 2+ DB 部署指针评估，MVP 不实施）+ **1 项跨文档边界重申**（HRP-μ/CRISP 组合构建算法 DEFERRED 至 52/54 号，strategy_registry 不实现算法）。**MVP 阶段无阻塞**——pain_metric MVP 用 none（持仓<10 人工判断 max_drawdown 足够）、ulcer_index/calmar_ratio 自动可算（pandas cummax <10 行）、impact_model_type MVP 用 square_root（已落地）、propagator_config MVP 不填（square_root 不需 propagator 参数）、construction_method MVP 填 index_provider/absolute（4 条 entry 已知）、active_share/style_drift_detection MVP 填 null/none（单策略无需）。**关键洞见**：本轮价值在于"路径与谱系补全"——Ulcer/Calmar 补全回撤的"路径"维度（深度×持续时间，非单一深度标量）；impact_model_type 补全冲击模型的"谱系"维度（square_root/AC/I-Star/Propagator 四形态，非单一 square_root）；construction_method+active_share 补全基准的"构造与主动性"维度（如何构造+多主动）；MCP aliases 补全部署的"指针"维度（别名重定向 vs status 翻转）。四者均是把"单一标量/形态"升级为"多维谱系"，精准匹配 MVP 轻量与 Phase 1.5+ 精细化的分层需求。

### 4.38 第二十轮研究对标补充（v1.31.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.30.0 覆盖第一至十九轮。本轮（v1.31.0）聚焦**前十九轮未系统覆盖的 LLM 时序泄漏测量 + 因子海市蜃楼（collider/confounder）+ 跳跃扩散 regime 持续性 + 中国证监会 2026-07 合规四领域**，经全网搜索 2026-08 最新研究后筛选出 **4 项对标（4 项 schema 字段落地 + 2 项审计检查扩展 + 2 项 enum 选项扩展）**。本轮核心发现：① **LLM 前瞻治理有"检测"无"测量"**——E15（v1.19.0 Look-Ahead-Bench memorization leakage 检测）+ E18（v1.22.0 LAP propensity 检测）回答"是否泄漏"，但 Zeyu Zhang 2026-08-04 证明标准 pre/post-cutoff 检查"uninformative"——recency 模仿 leakage，被动回测**数学上不可分离**两者，需 matched clean control（全局泄漏调整分数）+ boundary detection（cutoff 边界定位）才能**测量**泄漏剂量；② **因果验证有"声明"无"结构"**——E17（v1.21.0 causal_graph 声明检查）要求因子登记因果图，但 López de Prado & Zoonekynd CFA Institute 2025/2026 "Factor Mirage" 揭示更深层陷阱：**collider（碰撞变量）比 confounder 更危险**——含 collider 的错误设定模型展现**更高 R² + 更低 p-value**，计量教规主动偏好这类错误模型，系数符号可翻转（+0.08→−0.04），仅声明 causal_graph 不够，MUST 显式枚举排除的 confounder 和纳入的 collider；③ **regime 检测有 HMM 但缺"持续性"机制**——regime_detector enum 有 200d_sma/hmm/wasserstein_hmm/news_aware/text_var_dual 五选项，但标准 HMM **无法生成持续的高波动 regime**（极端事件后过快回归），Statistical Jump Model（Nystrup Princeton）用显式跳跃惩罚捕获持续 regime，Hybrid HMM+Poisson jump-duration（Cornell 2026-03）强制真实尾部驻留时间，均优于 Markov-switching；④ **§4.20 A 股合规只覆盖交易规则/程序化，未覆盖内幕交易司法解释修订**——2026-07-27 施行法释〔2026〕13号是 2012 年来首次系统性修订（敏感期前移+四类人群入刑减半+三大脱罪理由失效），虽个人量化基于公开数据不涉内幕，但 event_driven 策略的事件窗口划定 MUST 知晓新规边界。

**① Temporal Leakage Measurement：从"检测"到"测量"（对标 experiment_registry，v1.31.0 schema 字段已落地 + E18 审计检查扩展）**

[arXiv:2608.02985v1 2026-08-04 Temporal Leakage in LLM Backtesting](https://arxiv.org/abs/2608.02985)（Zeyu Zhang & Bradly C. Stadie, Northwestern University + Bridgewater AIA Labs, cs.LG/cs.CL/stat.ML）+ [arXiv:2602.17234v2 2026-05-25 All Leaks Count](https://arxiv.org/abs/2602.17234)（同作者，Shapley-DCLR + TimeSPEC）+ [prakulhiremath/temporal-leaks 2026-06](https://github.com/prakulhiremath/temporal-leaks)（"Valgrind for Time-Series ML" 开源工具）：**LLM 回测前瞻偏差治理的"测量"范式**。核心论点链：① **标准检查 uninformative**——"比较 training cutoff 前后分数"是行业标准检查，但 4 个旗舰模型在**不可能记忆**的问题上（所有问题都在其 cutoff 之后才解决）仍失败该检查，原因是结构性的：模型合法地对 cutoff 附近时间知道更多，**recency 模仿 leakage**；② **被动回测数学不可分离**——论文**证明** no passive backtest 能从 genuine skill 中分离 recency 与 leakage，纯被动检测有理论天花板；③ **测量需外部信息**——两种形式：**known cutoff** 在边界定位泄漏（boundary detection），**matched clean control** 全局识别并产生 leakage-adjusted score（matched_control）；④ **泄漏藏匿处**——集中在"出乎 Crowd 意料 + 训练中覆盖充分"的结果上，**partial memorization 被不成比例地奖励**；⑤ **twin-model 验证**——在 twin models 中植入泄漏，估计器恢复注入剂量并在 clean questions 返回 null（零误报），部署到 frontier models 检测到一个 cutoff-localized 签名，并在审计 power floor 上 cleared 5 个模型（其表面优势仅是 recency）。**配套 arXiv:2602.17234v2**：claim-level 评估框架——将模型 rationale 分解为 atomic claims，用 **Shapley values** 量化每个 claim 对预测的边际贡献，产出 **Shapley-DCLR**（Shapley-weighted Decision-Critical Leakage Rate，决策驱动推理中泄漏占比的可解释指标），并提出 **TimeSPEC**（Time-Supervised Prediction with Extracted Claims）推理时架构——temporally-filtered retrieval + claim-level supervision 交织，违反时重新生成。**配套 prakulhiremath/temporal-leaks**：time-series ML 的 look-ahead bias 自动捕获工具（"Valgrind for Time-Series ML"），检测 feature computed at t 是否误用 t+1/t+2/…/t+n 数据。**比现有方法更好**：v1.19.0 E15 检测 LLM memorization leakage（Look-Ahead-Bench），v1.22.0 E18 检测 LAP propensity（training-side），两者回答"**是否**泄漏"（detection），但都**未测量泄漏剂量**也未产生 adjusted score。Zeyu Zhang 证明 detection 有理论天花板——"Backtests need not be discarded; they need one defensible reference"——matched clean control 提供 that reference。**v1.31.0 已落地**：① experiment_registry schema 补 `temporal_leakage_measurement` 字段（{method: enum(matched_control/boundary_detection/none), leakage_score: float, reference_model: str}，matched_control=matched clean control 全局测量+调整分数，boundary_detection=known cutoff 边界定位，none=未检测；leakage_score 是 leakage-adjusted 后的分数差，0=无泄漏；reference_model 是作为 clean control 的参考模型标识）；② §4.7 E18 审计检查扩展（不新增 E 编号，遵循 v1.24.0 最小 churn 原则）——E18 原"LAP 前瞻污染检测"扩展为"LAP + Temporal Leakage 前瞻污染检测"，LLM-driven 回测实验除 lap_check_result 外 MAY 声明 temporal_leakage_measurement，warning 级 MVP 不阻断。**个人项目适用性**：中。MVP 阶段无 LLM-driven 回测（策略为 human/规则型），temporal_leakage_measurement 填 none；Phase 1.5+ 接入 LLM 因子/策略后，origin=llm_generated 的实验 SHOULD 启用 matched_control 测量。Phase 3+ 评估 Shapley-DCLR claim-level 归因 + TimeSPEC 推理时抑制。

**② Causal Factor Mirage：collider 比 confounder 更危险（对标 factor_registry + E17，v1.31.0 schema 字段已落地 + E17 审计检查扩展）**

[CFA Institute Research Foundation 2025 Causality and Factor Investing: A Primer](https://rpc.cfainstitute.org/research/foundation/2025/causality-factor-investing)（Marcos López de Prado & Vincent Zoonekynd, ADIA Lab）+ [Cambridge Elements Quantitative Finance 2023 Causal Factor Investing](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/9AFE270D7099B787B8FD4F4CBADE0C6E/9781009397292AR.pdf/causal_factor_investing.pdf)（López de Prado）+ [CFA Enterprising Investor 2025-10-30 The Factor Mirage](https://blogs.cfainstitute.org/investor/2025/10/30/the-factor-mirage-how-quant-models-go-wrong/) + [CFA Enterprising Investor 2026-03-05 The Question That Exposes Weak Quant Models](https://rpc.cfainstitute.org/blogs/enterprising-investor/2026/the-question-that-exposes-weak-quant-models) + [causal-quant v0.4.1 2026-07-09](https://github.com/meacreatio/causal-quant)：**因子投资的"海市蜃楼"——错误设定（misspecification）比 p-hacking 更隐蔽**。核心论点链：① **Factor Zoo → Factor Mirage**——Factor Zoo（数百已发表异常 OOS 失败）众所周知，但 ADIA Lab 指出更危险问题：**Factor Mirage** 源自**系统性错误设定**而非 data-mining，模型遵循计量教规（线性回归/显著性检验/two-pass estimator）开发但仍错——因为教规**将 association 等同于 causation**；② **两种设定错误**——**confounder bias**（未控制同时影响因子和收益的变量）+ **collider bias**（纳入了被因子和收益共同影响的变量）；③ **collider 更危险**——含 collider 的模型展现**更高 R² + 更低 p-value**，计量教规主动偏好这类错误模型，**误将更好拟合当作正确**——collider 变量值在收益之前已定，故无法货币化其更强关联，backtest 利润是海市蜃楼；④ **系数符号翻转实证**——26 个 Barra 因子模型审计中，正确流动性因子 loading +0.08，错误控制变量下变 −0.04，投资者买入应卖出的证券；⑤ **Type-A vs Type-B 虚假声明**——Type-A（关联性虚假：纯噪声被当信号）+ Type-B（因果性虚假：真实关联但因果方向错误），两者都阻止因子投资超越现象学阶段；⑥ **DDQ 核心问题**——"How did you decide which variables to include, and which did you deliberately exclude?"——强答案追溯经济因果链并讨论**故意排除**的变量，标准答案只引统计指标（IR/R²/显著性），危险答案"用所有变量让 t-stat 决定"；⑦ **causal-quant v0.4.1**（meacreatio 开源）实现 de Prado (2023/2026) + Bailey (2014/2017) 协议——declare causal graph → run falsification battery → 量化多少 reported edge 能存活 search and selection，返回 H-score，钉死 backtest 撒谎三方式（luck/confounding/selection across everything you tried）。**比现有方法更好**：v1.21.0 E17（因果验证声明检查）要求 factor_registry entry 声明 causal_graph（自然语言经济逻辑），v1.21.0 第十轮引入 causal-quant 作为 Phase 1.5+ 证伪电池。但 E17 只检查"**是否声明**因果图"，**未要求显式枚举 confounder 和 collider**——Factor Mirage 揭示仅声明不够，collider 因"更好拟合"而被主动偏好，MUST 显式审计设定结构。**v1.31.0 已落地**：① factor_registry schema 补 `causal_structure` 字段（{confounders: list, colliders: list, specification_audit: str}，confounders=故意排除的混杂变量列表（同时影响因子和收益），colliders=已纳入但被因子和收益共同影响的变量列表（风险标志），specification_audit=设定审计结论 natural_language/collider_flagged/confounder_controlled）；② §4.7 E17 审计检查扩展（不新增 E 编号）——E17 原"因果验证声明检查"扩展为"因果验证 + 设定结构检查"，price-derived 因子除 causal_graph 外 SHOULD 声明 causal_structure，warning 级 MVP 不阻断，collider 非空时升级为 warning highlight（提示设定风险）。**个人项目适用性**：高。MVP 阶段 causal_structure 用自然语言填 confounders/colliders（如 momentum 因子 confounders=[market_beta, sector_rotation]，colliders=[]），Phase 1.5+ 接入 causal-quant v0.4.1 证伪电池后补 H-score。关键启示：A 股因子构造中，**past_return 作为 collider 是最常见陷阱**（被 quality 因子和未来收益共同影响）——纳入它制造虚假高 R²。

**③ Statistical Jump Model + Jump-Diffusion HMM：regime 持续性的显式建模（对标 strategy_registry regime_detector，v1.31.0 enum 选项扩展）**

[arXiv:2603.10202v1 2026-03-10 Hybrid HMM with Jump-Diffusion](https://arxiv.org/pdf/2603.10202v1)（Alswaidan & Varner, Cornell University, q-fin.ST）+ [arXiv:2402.05272 Statistical Jump Model Regime-Aware Allocation](https://arxiv.org/html/2402.05272v1)（Shu-Yu-Mulvey, Princeton University, q-fin.PM）+ [tradingstrategy.ai 2026 Market Regimes](https://tradingstrategy.ai/docs/learn/market-regimes.html)（GMM/HDBSCAN/Jump-Diffusion HMM 三方法对比）：**regime 检测的"持续性"缺口**。核心论点链：① **标准 HMM 的失败模式**——standard HMM specification **无法生成持续的高波动 regime**，导致极端事件后**过快回归**（overly rapid reversion），合成数据时间质量差——原因是 HMM 的 Markov 性使状态转移无记忆，无法编码"恐慌持续数周"的真实驻留时间；② **Statistical Jump Model（Nystrup）**——与传统 Markov-switching 不同，采用 statistical jump model 通过**显式跳跃惩罚（jump penalty）**捕获持续 regime——惩罚状态切换迫使 regime 持续，特征集仅含 price-derived return+volatility，在 time-series CV 框架内 data-driven 选择跳跃惩罚（直接优化 regime-aware 配置策略性能指标），实证 daily US equity indices **优于 buy-and-hold 和 Markov-switching 配置**，更鲁棒/可解释/现实；③ **Hybrid HMM + Poisson jump-duration（Cornell 2026-03）**——将连续 excess growth rate 离散化为 Laplace quantile-defined market states，用 **Poisson-driven jump-duration mechanism** 强制真实尾部驻留时间，参数用 direct transition counting 估计（**完全避免 Baum-Welch EM**），1000 条 SPY 模拟路径 KS/AD pass rate >97%/91% in-sample、94% OOS，部分再现标准 regime-switching 缺失的 ARCH effect；④ **三方法对比（tradingstrategy.ai 2026）**——GMM（软聚类反映渐变）vs HDBSCAN（非参数密度检测，transition state 归为 noise）vs **Jump-Diffusion HMM**（捕获瞬时 regime 转换），三种 canonical regime：Low-Vol Growth（杠杆 risk-parity）/High-Vol Inflation（最小方差）/Tail Crash（凸性 overlay）；⑤ **关键洞察**——No single model dominates：GARCH(1,1) 更准确再现 volatility clustering 但 distributional test 失败（KS pass 5.5%），standard HMM 无 jump 分布保真更高但无法生成持续高波动 regime，hybrid framework 在 distributional/temporal/tail-coverage 三维度提供最佳联合质量。**比现有方法更好**：strategy_registry combination_strategy.regime_detector enum 现有 5 选项（200d_sma/hmm/wasserstein_hmm/news_aware/text_var_dual），但**无任何选项编码 regime 持续性**——hmm/wasserstein_hmm 都是标准 HMM 变体，受"过快回归"失败模式影响。Statistical Jump Model 和 Jump-Diffusion HMM 通过显式跳跃惩罚/Poisson 驻留机制解决此问题。**v1.31.0 已落地**：strategy_registry combination_strategy.regime_detector enum 补 `statistical_jump`（Nystrup 显式跳跃惩罚，捕获持续 regime，data-driven 惩罚选择）+ `jump_diffusion_hmm`（HMM + Poisson jump-duration，强制尾部驻留时间，避免 Baum-Welch）两选项。**个人项目适用性**：中。MVP 阶段用 200d_sma（简单可解释），Phase 1.5+ 评估 statistical_jump（Nystrup Princeton 实证优于 Markov-switching，且特征仅 price-derived 无需外部数据）；Phase 2+ 评估 jump_diffusion_hmm（合成数据生成+压力测试场景设计用，非直接 regime 检测）。**关键启示**：A 股 2015 股灾/2024-09 行情是典型"持续高波动 regime"——标准 HMM 会过快判定回归正常，statistical_jump 的跳跃惩罚能正确维持恐慌状态判断数周，配合 §4.12 ADAPT_STRATEGY 的 regime 衰减原因分类（depletion→refit）更精准。

**④ 中国证监会 2026-07 合规：内幕交易司法解释修订 + 短线交易规定（对标 risk_limit_registry + §4.20，v1.31.0 schema 字段已落地）**

[证监会 2026-03-06 关于短线交易监管的若干规定](http://www.csrc.gov.cn/csrc/c100028/c7618628/content.shtml)（2026-04-07 施行）+ [法释〔2026〕13号 2026-07-24 内幕交易司法解释修订](https://stcn.com/article/detail/4041407.html)（最高法最高检联合，2026-07-27 施行，2012 年来首次系统性修改）+ [源泰律所廖海 2026-07 解读](http://m.toutiao.com/group/7666630312092385830/)：**A 股合规红线的 2026-07 重大升级**。核心变化：① **内幕信息敏感期起点大幅前移**——新增"控股股东、实际控制人或者相关决策人员向关系密切人员透露形成内幕信息**初步意向**的时间，或者根据该初步意向进行相关交易的时间，应当视为动议的初始时间"——**初步意向/口头沟通阶段**即认定内幕信息形成，敏感期即刻起算，堵死"意向阶段"套利漏洞（旧规需"实质操作阶段+很大实现可能性"）；② **四类重点人群入刑门槛减半**——董监高/实控人/法定知情人 + 有偿泄密牟利者 + 证券犯罪前科人员 + 两年内受行政处罚人员：证券成交额 100 万（普通 200 万）/获利避损 25 万（普通 50 万）即刑事立案；③ **三大脱罪理由失效**——a) 交易计划抗辩须内幕信息形成前真实订立+完整要素（标的/数量/价格区间/执行时间）+书面+合法，事后补签/笼统框架一律不认；b) 上市公司收购禁止"暗仓"套利（偏离收购目的无合理解释不免责）；c) 仅证监会/交易所官方公告属合法公开信息，自媒体传言/饭局闲聊不算；④ **只泄密不交易同样构罪**——单纯泄露/授意交易，无本人交易无获利，仍构成共犯全额追责；⑤ **短线交易规定（2026-04-07 施行）**——13 种豁免情形（ETF 申赎/做市/股权激励/司法强制执行等），专业机构管理的产品/组合按一码通单独计算持股（公募/社保/年金/保险/合格私募），便利中长期资金入市。**比现有方法更好**：§4.20（v1.14.0/v1.15.0）A 股 2026-07 合规只覆盖**交易规则修订**（ST 涨跌 5→10%/盘后固定价格/创业板做市商）+ **程序化交易细则**（15 笔/秒/撤单率≤15%/报单停留≥50µs）+ **局域网关闭/广域网时延**，**未覆盖内幕交易司法解释修订**——后者直接影响 event_driven 策略的事件窗口划定（重大重组/控制权变更的"初步意向"时点即敏感期起点）。risk_limit_registry 9 种限额类型无 compliance 维度字段。**v1.31.0 已落地**：risk_limit_registry schema 补 `compliance_notices` 字段（list[obj]，每项 {regulation: str, effective_date: date, applicability: enum(applicable/not_applicable/conditional), impact_note: str}，登记适用监管规定及对本限额/策略的影响说明）。**个人项目适用性**：低（合规存档，非阻断）。个人量化基于公开数据+技术指标，持仓<10，**非 5% 大股东/董监高**——短线交易规定（适用主体 5%+股东/董监高）**不适用**；内幕交易——基于公开行情+公开财报，**不涉内幕信息**。但 event_driven 策略（STR-EVT 类）MUST 知晓：重大重组/控制权变更的"初步意向"时点即敏感期起点，事件窗口划定不得依赖非公开信息，compliance_notices 登记 法释〔2026〕13号 applicability=conditional（仅事件驱动策略相关）+ 短线交易规定 applicability=not_applicable（个人非 5% 股东）。

> ⚠️ **v1.31.0 第二十轮总结**：4 项对标覆盖 Temporal Leakage Measurement 测量范式/Causal Factor Mirage collider-confounder 设定结构/Statistical Jump Model+Jump-Diffusion HMM regime 持续性/中国证监会 2026-07 内幕交易+短线交易合规四领域，**本轮填补前十九轮"LLM 前瞻泄漏测量"+"因果设定结构审计"+"regime 持续性建模"+"内幕交易合规存档"四个对标空白**。**0 项新 E/G 编号**（遵循 v1.24.0/v1.30.0 最小 churn 原则——E17 扩展为"因果验证+设定结构检查"、E18 扩展为"LAP+Temporal Leakage 检测"，语义内聚不新增编号）+ **4 项 schema 字段已落地**（experiment_registry 补 temporal_leakage_measurement{method:matched_control/boundary_detection/none,leakage_score,reference_model} + factor_registry 补 causal_structure{confounders,colliders,specification_audit} + risk_limit_registry 补 compliance_notices list + strategy_registry regime_detector enum 补 statistical_jump/jump_diffusion_hmm 两选项）+ **2 项审计检查扩展**（E17 扩展查 causal_structure collider 标志 + E18 扩展查 temporal_leakage_measurement，均 warning 级 MVP 不阻断）。**MVP 阶段无阻塞**——temporal_leakage_measurement MVP 填 none（无 LLM-driven 回测）、causal_structure MVP 用自然语言填 confounders/colliders（如 momentum confounders=[market_beta]）、compliance_notices MVP 登记 法释〔2026〕13号 applicability=conditional + 短线交易规定 applicability=not_applicable、regime_detector MVP 用 200d_sma（statistical_jump/jump_diffusion_hmm 为 Phase 1.5+/2+ 评估）。**关键洞见**：本轮价值在于"从二值到结构"——Temporal Leakage 从"是否泄漏"（detection）升级到"泄漏多少+调整分数"（measurement，matched clean control 提供 defensible reference）；Causal Factor Mirage 从"是否声明因果图"（declaration）升级到"显式枚举 confounder/collider 设定结构"（specification，collider 因更高 R² 而被偏好=最危险陷阱）；regime 从"无记忆 Markov"升级到"显式跳跃惩罚/驻留时间"（persistence，解决极端事件过快回归）；合规从"交易规则"扩展到"内幕交易司法解释"（事件窗口划定边界）。四者均是把"二值/无记忆/单一维度"升级为"结构化/持续性/多维度"，精准匹配 MVP 轻量与 Phase 1.5+ 精细化的分层需求。

### 4.39 第二十一轮研究对标补充（v1.32.0 新增，2026-08-10 全网搜索）

v1.12.0-v1.31.0 覆盖第一至二十轮。本轮（v1.32.0）聚焦**前二十轮未系统覆盖的因子归因稳定性（DASH 不可能性定理）+ A 股涨跌停板上游污染 + 参数稳定性区域选择 + 因子衰减函数形式 + 图-因子联合组合构造 + LLM 代码进化因子挖掘六领域**，经全网搜索 2026-08 最新研究后筛选出 **6 项对标（2 项 schema 字段落地 + 3 项审计检查扩展 + 3 项 Phase 1.5+/2+ 评估）**。本轮核心发现：① **因子归因有"冗余检查"无"稳定性保证"**——E16（v1.20.0 因子冗余检查）用 correlation_group/redundancy_status 检测冗余因子，但 DASH 不可能性定理（Lean 4 机器验证）证明：collinearity 下 SHAP 排名**结构性不稳定**——faithfulness + stability + completeness 三者不可兼得，68% 公开数据集出现归因翻转，单模型 SHAP 排名 correlated 因子等价于**抛硬币**；② **A 股因子计算有"涨跌停"无"可交易性掩码"**——±10%/±20% 涨跌停板使部分收盘价**不可执行**，但标准实现先读价格再过滤行，污染通过 MA/correlation/rank 静默传播（upstream contamination），实证虚增 IC 18% + 降低 Sharpe 0.44——mask-first 设计（数据加载时构造 tradability mask 并贯穿每个算子）是**单一最大贡献者**（+0.44 Sharpe）；③ **参数选择有"最优点"无"稳定区域"**——G2 walk-forward 检查选单一最优点，但极端点对小扰动敏感易崩溃，AlgoXpert 证明应优先"稳定高原"（plateau）而非"悬崖尖峰"（cliff）；④ **因子衰减有"CUSUM 检测"无"函数形式"**——§4.8 DECAY_SCAN 用 CUSUM/BOCPED 检测衰减信号，但假设指数衰减 α(t)=α₀e^(−λt)，博弈论均衡推导出**双曲衰减** α(t)=K/(1+λt) 对 momentum 因子拟合更好（R²=0.65 vs 指数 0.61 vs 线性 0.51），机械因子（动量/反转）衰减可建模，判断因子（价值/质量）不衰减——crowding 预测尾部风险而非均值；⑤ **组合构造有"HRP"无"图-因子联合"**——52/54 号 HRP-μ/CRISP 基于相关性图，但相关性图捕获有限样本共动而非经济结构，MINGLE（ADMM 联合学习因子表示+图拓扑）用**因子暴露重定义图局部性**，跨波动率 regime 和交易成本水平一致优于相关性图组合；⑥ **LLM 因子挖掘有"公式进化"无"代码进化"**——§4.26 Hubble/§4.36 QUANTEVOLVER 基于**公式表达式**，CogAlpha（ACL 2026 Oral）将 alpha 从"公式"升级为"Python 代码"——7 层 21 智能体研究组织架构（市场结构→尾部风险→价量→趋势反转→多尺度复杂性→稳定性门控→几何融合），5 指标筛选（IC/RankIC/ICIR/RankICIR/MI），两级选择（65 分位合格/80 分位精英），CSI300 年化超额 16.39%/IR 1.90。

**① DASH 不可能性定理：collinearity 下 SHAP 排名结构性不稳定（对标 factor_registry + E16，v1.32.0 schema 字段已落地 + E16 审计检查扩展）**

[arXiv:2605.21492 2026-05 Feature Attribution Is Provably Unstable Under Collinearity](https://arxiv.org/abs/2605.21492)（DASH: Diversified Aggregation for Stable Hypotheses，Lean 4 机器验证 248 定理 0 证明间隙）+ [github.com/DrakeCaraker/dash-shap](https://github.com/DrakeCaraker/dash-shap)（MIT 开源）：**因子归因的"不可能性定理"——faithfulness + stability + completeness 三者不可兼得**。核心论点链：① **Theorem 5 核心不可能性**——当任意两个特征 collinear 时，faithfulness（排名反映真实模型）+ stability（不同随机种子重训练产生相同排名）+ completeness（每对特征都被排名）三者**互斥**，证明用 Rashomon 性质：collinearity 下存在多个等性能模型分配不同重要性排序；② **设计空间定理 Theorem 28**——恰好两族归因方法：第一族 faithful+complete 但 unstable（对称 collinear 对翻转率最高 50%），第二族 stable 但报告 ties（DASH 是 canonical member），**无第三选项**——这是可能方法空间的**划分**而非当前方法的实践限制；③ **架构特异定量界**——gradient boosting 归因比发散为 1/(1−ρ²)（ρ→1 时无界），lasso 归因比无穷（正则化强制 collinear 对中一个归零），random forest 收敛到 1+O(1/√T)，neural network 87% 特征对出现不稳定；④ **68% 数据集受影响**——77 个公开数据集调查中 68% 出现归因不稳定，且这是**保守下界**；⑤ **DASH 解决方案**——跨 M 个独立训练模型等权平均 SHAP 值，是唯一对称无偏线性聚合方法，Theorem 22 证明 Pareto-optimal，达到 Cramer-Rao 方差界，M=25 模型将翻转率降至 <1%，M=5 已有显著改善；⑥ **实践影响**——模拟贷款审批管道中 5 个相关收入特征，43.2% 被拒申请人因查询 25 个模型中的哪一个而获得不同首要拒因，DASH 共识 100% 解决。**比现有方法更好**：v1.20.0 E16（因子冗余检查）查 correlation_group/redundancy_status 检测同组冗余因子，但**隐含假设 SHAP/IC 归因可靠**——DASH 证明 collinearity 下单模型 SHAP 排名**结构性不可靠**，E16 检测的"冗余因子"中哪个"更好"的判断本身可能不稳定。**v1.32.0 已落地**：① factor_registry schema 补 `attribution_stability` 字段（{method: enum(dash/none), model_count: int, flip_rate: float, stable_ranking: bool}，dash=DASH 跨 M 模型聚合 SHAP，model_count=M（≥25 时 flip_rate<1%），flip_rate=跨模型排名翻转率，stable_ranking=翻转率<5% 时 true；none=MVP 阶段未做归因稳定性检查）；② §4.7 E16 审计检查扩展（不新增 E 编号）——E16 原"因子冗余检查"扩展为"因子冗余 + 归因稳定性检查"，correlation_group 非空的因子 SHOULD 声明 attribution_stability，warning 级 MVP 不阻断，flip_rate>20% 时升级为 warning highlight。**个人项目适用性**：中。MVP 阶段因子为规则型（无 SHAP 归因），attribution_stability 填 none；Phase 1.5+ 接入 ML 因子模型（XGBoost/GBDT）后，correlation_group 非空的因子 SHOULD 启用 DASH（M≥5 跨种子模型聚合），flip_rate>20% 的因子标记为"归因不稳定"需人工裁定冗余方向。

**② A 股涨跌停板上游污染：mask-first 设计（对标 data_asset_registry schema 计划 + E15 审计检查扩展，v1.32.0 审计检查扩展）**

[arXiv:2507.07107v2 2026-05 Machine Learning Enhanced Multi-Factor Quantitative Trading: Mask-First Design](https://arxiv.org/abs/2507.07107)（Yimin Du, USTC, q-fin.PM, A 股 ±10%/±20% 涨跌停板上游污染实证 + MIT 开源）：**A 股因子计算的"上游污染"——涨跌停收盘价不可执行但被标准实现静默吸收**。核心论点链：① **结构性挑战**——A 股主板 ±10%/STAR/创业板 ±20% 日涨跌停限制意味着任何交易日部分收盘价**不可执行**（涨停时未匹配买单残留，记录的收盘价无法成交），标准行业响应（事后行删除）对**滚动窗口算子无效**——MA/correlation/rank 在行过滤前累积不可执行价格，称 upstream contamination；② **实证影响**——真实 A 股数据上虚增 IC 18% + 降低实现 Sharpe 0.44 点（大效应），因为模型学会了预测**无法交易的收益**；③ **mask-first 设计**——数据加载时构造 Boolean tradability mask（涨停/跌停标记为 false），**贯穿每个算子**使任何窗口不读不可交易价格；④ **消融实验**——mask contract 是**单一最大贡献者**（+0.44 Sharpe），超过任何模型/损失选择，GPU 向量化 213 因子引擎（PyTorch unfold，51× pandas 加速），Adjusted-MSE 损失（错误方向预测惩罚 11×），block-bootstrap GBM 增强，Markowitz-Ledoit-Wolf 组合优化（cvxpy warm-start 缓存）；⑤ **合成面板**——3000 股校准合成面板年化 Sharpe 2.05，专有 A 股数据（2022-2024）Sharpe 1.63。**比现有方法更好**：§4.7 E15（LLM Look-Ahead-Bench 检测）检测 LLM 前瞻偏差，但**未覆盖 A 股涨跌停板上游污染**——这是一种特殊的 look-ahead bias（使用不可执行的价格仿佛可执行），E15 未检查因子计算是否尊重 tradability mask。data_asset_registry（P1-B 待施工）schema 无 tradability_mask 维度。**v1.32.0 已落地**：① §4.7 E15 审计检查扩展（不新增 E 编号）——E15 原"LLM Look-Ahead 检测"扩展为"LLM Look-Ahead + A 股 Tradability Mask 检测"，A 股因子计算实验 MUST 声明 tradability_mask_policy（none/row_filter/mask_first），none=未处理（warning highlight），row_filter=事后行删除（不足，upstream contamination 仍存在），mask_first=数据加载时构造掩码贯穿算子（MUST）；② data_asset_registry schema 计划补 `tradability_mask_policy` 字段（待 P1-B 施工时落地）。**个人项目适用性**：高（A 股 MUST）。MVP 阶段因子计算 MUST 实现 mask-first——在 data provider 层（akshare_provider）加载 K 线时标记涨跌停（close==high 且 close/open 涨幅≥9.8% 主板/≥19.5% 创业板），因子计算引擎（§15 因子工程总纲）每个滚动窗口算子跳过 mask=false 的数据点。**关键启示**：这是 A 股特有的数据完整性问题——美股无涨跌停板故不存在此问题，但 A 股因子库 111 条因子中任何使用 close 价的因子（MA/MACD/KDJ/RSI/BOLL 等）都受影响，mask-first 是**前置 MUST**而非可选优化。

**③ AlgoXpert IS-WFA-OOS 稳定性区域参数选择（对标 experiment_registry + G2，v1.32.0 schema 字段已落地 + G2 审计检查扩展）**

[arXiv:2603.09219v1 2026-03 AlgoXpert Alpha Research Framework: IS-WFA-OOS Protocol](https://arxiv.org/abs/2603.09219)（Nguyet-Chan-Anh, AlgoXpert Lab, q-fin.PM）：**回测验证的"稳定性区域"——选高原不选尖峰**。核心论点链：① **核心 Gap A**——许多管道选单一最优点，但极端点对扰动敏感易崩溃，缺乏优先稳定高原（plateau）避免悬崖型敏感区域的策略；② **核心 Gap B**——naïve train-test split 对有状态策略产生乐观评估（指标重叠和持仓状态"渗漏"跨边界），需 purge gap 控制；③ **核心 Gap C**——验证与执行/风控解耦，先优化信号后补成本和守卫，但操作故障常源自微观结构摩擦；④ **三阶段协议**——IS（In-Sample 优先稳定区域不选单一最优）→ WFA（Walk-Forward Analysis 滚动窗口+purge gap，majority-pass + catastrophic-veto 双决策门）→ OOS（Out-of-Sample 严格参数锁定不再调参）；⑤ **defense-in-depth 架构**——structural（cliff veto 悬崖否决）+ execution（spread/leverage guards）+ equity protection（circuit breakers, kill switch）；⑥ **实证发现**——目标从最大化 Sharpe 切换到最小化 MaxDD 时出现排名反转（rank reversal），揭示风险调整绩效与尾部风险控制的 trade-off。**比现有方法更好**：§4.13 PROMOTE_ENTRY G2（walk-forward 检查）检查 walk-forward 通过率，但**选单一最优点**——AlgoXpert 证明应优先稳定高原。experiment_registry schema 无参数稳定性区域维度。**v1.32.0 已落地**：① experiment_registry schema 补 `parameter_stability_region` 字段（{plateau_identified: bool, cliff_detected: bool, stability_score: float, selection_method: enum(single_optimum/stability_plateau)}，plateau_identified=是否找到稳定高原（参数空间中性能平坦区域），cliff_detected=是否检测到悬崖（小扰动导致性能崩溃），stability_score=参数扰动下性能变异系数的倒数，selection_method=选择策略）；② §4.13 G2 审计检查扩展（不新增 G 编号）——G2 原"walk-forward 通过率检查"扩展为"walk-forward + 参数稳定性区域检查"，experiment_registry SHOULD 声明 parameter_stability_region，cliff_detected=true 时升级为 warning highlight（参数悬崖=过拟合信号）。**个人项目适用性**：中。MVP 阶段用 simple_optimum（参数少，单一最优点可接受），Phase 1.5+ 参数搜索（网格/贝叶斯优化）MUST 启用 stability_plateau（在参数空间中找性能平坦区域，避免悬崖），stability_score 低于阈值时拒绝上线。

**④ 双曲因子衰减：博弈论均衡推导（对标 strategy_registry/factor_registry decay_detection_method，v1.32.0 Phase 1.5+ 评估）**

[arXiv:2512.11913v1 2025-12 Not All Factors Crowd Equally: Hyperbolic Alpha Decay](https://arxiv.org/abs/2512.11913)（Chorok Lee, KAIST, q-fin.PM, 8 个 Fama-French 因子 1963-2024 实证）：**因子衰减的"双曲形式"——α(t)=K/(1+λt) 优于指数/线性**。核心论点链：① **博弈论均衡推导**——N 个代理发现同一信号竞争固定"alpha capacity" K，Nash 均衡下每个代理赚 αᵢ=K/N，随时间代理发现信号，总量 alpha 双曲衰减 α(t)=K/(1+λt)（λ=策略发现速率）；② **实证验证**——momentum 因子双曲衰减 R²=0.65 优于指数 0.61 优于线性 0.51，验证博弈论基础；③ **并非所有因子同等拥挤**——机械因子（momentum/reversal）符合模型（可被博弈论建模），判断因子（value/quality）不符合（信号模糊性形成"进入壁垒"），平行于 Hua-Sun 的"barriers to entry"分类；④ **2015 后加速**——OOS 模型过度预测剩余 alpha（0.30 vs 0.15），与 factor ETF 增长相关（ρ=−0.63）；⑤ **平均收益已有效定价**——crowding 因子选择无法产生 alpha（Sharpe 0.22 vs factor momentum benchmark 0.39）；⑥ **crowding 预测尾部风险**——OOS 2001-2024，crowded reversal 因子崩溃概率高 1.7-1.8×，crowded momentum 崩溃概率低 0.38×（p=0.006）——crowding 预测崩溃而非均值，用于风险管理不用于 alpha 生成。**比现有方法更好**：§4.8 DECAY_SCAN 用 CUSUM/BOCPED 检测衰减信号，§4.12 ADAPT_STRATEGY 的 decay_detection_method enum 含 cusum/ph_bocpe/z_score 等，但**均假设指数衰减** α(t)=α₀e^(−λt)——双曲衰减对机械因子拟合更好。**v1.32.0 评估**：Phase 1.5+ 评估 decay_detection_method enum 补 `hyperbolic_crowding` 选项（双曲衰减 K/(1+λt) + crowding 指标，仅适用于 mechanical 因子 momentum/reversal，judgment 因子 value/quality 不适用）。**个人项目适用性**：中。MVP 阶段用 z_score（简单跨维度），Phase 1.5+ momentum/reversal 类因子评估 hyperbolic_crowding（拟合双曲衰减曲线估计 λ，crowding 指标用于尾部风险预警而非 alpha 选择）。**关键启示**：A 股 momentum 因子衰减应拟合双曲而非指数——2024-09 行情后 momentum 策略快速失效是典型双曲衰减（前期快速衰减 K/(1+λt) 在 t 小时下降快于指数），CUSUM 检测到衰减信号后 ADAPT_STRATEGY 的 decay_cause 分类应区分"crowding 衰减"（机械因子，不可逆，需 refit）vs"regime 衰减"（环境变化，可逆，需 adapt）。

**⑤ MINGLE 图-因子联合组合构造（对标 strategy_registry 组合构造，v1.32.0 Phase 1.5+ 评估）**

[arXiv:2608.06618 2026-08-06 Beyond Co-Movement: MINGLE Joint Factor-Graph Framework](https://arxiv.org/abs/2608.06618)（Chehab-Iacovides-Yazdanparast-Mandic, Imperial College London, q-fin.PM/cs.LG/q-fin.ST）：**组合构造的"图-因子联合"——用因子暴露重定义图局部性**。核心论点链：① **当前方法二元对立**——标准因子模型忽略 idiosyncratic 冲击效应，图方法忽略驱动系统性收益的潜结构，两者捕获互补市场方面但未联合；② **MINGLE 框架**——Mutually-INformed Graph-Locality and Exposures，通过系统性因子暴露谱（非观测共动）重定义图局部性，统一 ADMM 框架联合学习潜因子表示+诱导图拓扑；③ **暴露相似性图**——比传统相关性图更贴合经济部门分类；④ **跨 regime 一致优于相关性图**——跨波动率 regime 和交易成本水平一致优于相关性图组合，配对统计检验确认增益来自图-因子域的调和。**比现有方法更好**：52/54 号 HRP-μ/CRISP 组合构造基于相关性图（distance=sqrt(0.5(1−corr))），但相关性图捕获**有限样本共动**而非经济结构——MINGLE 用因子暴露重定义图局部性，更贴合经济部门。**v1.32.0 评估**：Phase 1.5+ 评估 strategy_registry 组合构造方法补 `mingle` 选项（ADMM 联合学习因子表示+图拓扑，需 scipy.optimize + networkx）。**个人项目适用性**：低（Phase 1.5+）。MVP 阶段 HRP-μ 足够（相关性图简单可解释），Phase 1.5+ 评估 MINGLE（因子暴露图更贴合 A 股行业分类，跨 regime 更稳定）。

**⑥ CogAlpha LLM 代码进化因子挖掘（对标 strategy_registry origin/llm_distilled，v1.32.0 Phase 2+ 评估）**

[CogAlpha: Cognitive Alpha Mining via LLM-Driven Code-Based Evolution](https://arxiv.org/abs/2511.18850)（Liu-Huang-Luo-Wang-Yang-Li-Hu-Feng-Liu, HKU + Grace Investment Machine, ACL 2026 Oral）：**LLM 因子挖掘的"代码进化"——从公式到代码的研究员团队**。核心论点链：① **公式→代码升级**——用 Python 代码表达因子（带注释/逻辑/可执行/可检查）而非数学公式，搜索空间从表达式扩展到程序；② **7 层 21 智能体研究组织**——L1 市场结构周期/L2 极端风险脆弱性/L3 价量流动性/L4 趋势延续反转波动聚集/L5 多尺度复杂性回撤分形/L6 稳定性状态门控/L7 几何特征融合——按量化研究思考方式从宏观到微观拆分；③ **进化迭代**——生成候选→检查代码可跑逻辑→5 指标筛选（IC/RankIC/ICIR/RankICIR/MI）→变异交叉进化→淘汰保留——65 分位合格/80 分位精英两级选择；④ **多样化提示**——轻度改写（稳定）/中度改写（自然变体）/创造性改写（不同研究角度）防止系统保守化绕圈；⑤ **CSI300 实证**——年化超额 16.39%/IR 1.8999，跑赢 21 个基线方法；⑥ **反直觉发现**——闭源模型并非天然更强，推理型模型表现偏弱——Alpha 挖掘比的是结构适合探索/筛选/演化而非底层模型能力上限。**比现有方法更好**：§4.26 Hubble（DSL+AST 沙箱+进化反馈）+ §4.36 QUANTEVOLVER（RL 微调 policy updates）基于**公式表达式**，CogAlpha 升级为**代码表达式**——7 层研究组织架构比单 LLM 闷头想更贴近人类研究流程，5 指标筛选比单一 IC 更鲁棒。**v1.32.0 评估**：Phase 2+ 评估 strategy_registry origin 字段补 `llm_code_evolved` 选项（CogAlpha 7 层 21 智能体代码进化，需多 LLM agent 编排框架）。**个人项目适用性**：低（Phase 2+）。MVP 阶段 origin=human（规则型因子），Phase 1.5+ 评估 Hubble/QUANTEVOLVER（公式进化），Phase 2+ 评估 CogAlpha（代码进化+7 层研究组织，需多 agent 编排基础设施）。

> ⚠️ **v1.32.0 第二十一轮总结**：6 项对标覆盖 DASH 归因不可能性定理/A 股涨跌停板上游污染/AlgoXpert 稳定性区域参数选择/双曲因子衰减/MINGLE 图-因子联合组合构造/CogAlpha LLM 代码进化因子挖掘六领域，**本轮填补前二十轮"因子归因稳定性"+"A 股涨跌停可交易性掩码"+"参数稳定性区域选择"+"因子衰减函数形式"+"图-因子联合组合构造"+"LLM 代码进化因子挖掘"六个对标空白**。**0 项新 E/G 编号**（遵循 v1.24.0/v1.30.0/v1.31.0 最小 churn 原则——E15 扩展为"LLM Look-Ahead+A 股 Tradability Mask 检测"、E16 扩展为"因子冗余+归因稳定性检查"、G2 扩展为"walk-forward+参数稳定性区域检查"，语义内聚不新增编号）+ **2 项 schema 字段已落地**（factor_registry 补 attribution_stability{method:dash/none,model_count,flip_rate,stable_ranking} + experiment_registry 补 parameter_stability_region{plateau_identified,cliff_detected,stability_score,selection_method}）+ **3 项审计检查扩展**（E15+E16+G2，E15 中 A 股 tradability_mask_policy=none 为 warning highlight、E16 中 flip_rate>20% 为 warning highlight、G2 中 cliff_detected=true 为 warning highlight，均 warning 级 MVP 不阻断）+ **1 项 data_asset_registry schema 计划**（tradability_mask_policy 字段待 P1-B 施工时落地）+ **3 项 Phase 1.5+/2+ 评估**（双曲衰减 hyperbolic_crowding/MINGLE 图-因子联合/CogAlpha 代码进化）。**MVP 阶段无阻塞**——attribution_stability MVP 填 none（规则型因子无 SHAP 归因）、parameter_stability_region MVP 填 single_optimum（参数少）、tradability_mask_policy MVP MUST 实现 mask_first（A 股前置 MUST，非可选——涨跌停板上游污染虚增 IC 18%+降低 Sharpe 0.44 是实盘生存级问题）。**关键洞见**：本轮价值在于"从假设到证明"——DASH 从"假设 SHAP 可靠"到"Lean 4 证明 collinearity 下不可能可靠"（248 定理机器验证，68% 数据集受影响）；A 股 mask-first 从"假设收盘价可执行"到"实证 ±10%/±20% 涨跌停使部分收盘价不可执行且污染传播"（单一最大贡献者 +0.44 Sharpe）；AlgoXpert 从"选最优点"到"选稳定高原"（悬崖敏感性=过拟合信号）；双曲衰减从"假设指数衰减"到"博弈论均衡推导双曲衰减"（R² 0.65 vs 0.61）。四者均是把"隐含假设"升级为"显式证明/实证"，精准匹配 MVP 生存级（A 股 mask-first）与 Phase 1.5+ 精细化（DASH/AlgoXpert/双曲衰减）的分层需求。

## 5. P0 已完成三件套（回测必需输入）

### 5.1 universe_registry.yaml（股票池，REG-UNI-001）

**Schema**：

```yaml
unique_key: [universe_id]
entry_schema:
  universe_id: str               # UNI-{TYPE}-{NNN}
  name: str
  name_zh: str
  aliases: list
  universe_type: str             # static / dynamic / rule_based
  construction_rule: str
  base_universe: str             # 基础池（rule_based 在此过滤）
  filter_rules: list
  rebalance_frequency: str       # daily/weekly/monthly/quarterly/none
  component_count: int
  components_ref: str            # 成分股列表位置（DB/文件）
  used_by_strategies: list       # strategy_id 列表
  data_source: str               # data_asset_registry source_id
  module_id: str
  doc_ref: str
  code_path: str
  status: str                    # candidate/experimental/active/deprecated/retired
  version: str
  created_at: date
  updated_at: date
  owner: str
  # 生存偏差治理（v1.24.0 新增，对标 alphanume 2026-06 + tickernerd 2026-08 + arXiv:2603.16904，§4.7 E14 c 维度审计）
  pit_constituent_construction: bool  # 成分股是否按 point-in-time 构造（true=每个调仓日只用当时可得成分文件；false=用当前成分回溯=生存偏差；null=未声明）
  delisted_handling: enum           # include/exclude/unknown，退市股票处理（include=含退市至退市日含最终收益，回测 MUST；exclude=仅存活=生存偏差；unknown=未声明）
  survivorship_free: bool           # universe 是否无生存偏差（true=含退市+PIT构造；false=仅存活股；unknown=未声明，E14 c 维度审计）
```

**实际登记内容（5 条）**：

| universe_id | name_zh | type | 构造规则 | 调仓 | 数量 | 使用策略 | 状态 |
|---|---|---|---|---|---|---|---|
| UNI-DYNAMIC-001 | 打板连板梯队池 | dynamic | 每日涨停股识别连板梯队（54321阵型），排除 ST/退市/流动性失效 | daily | null | STR-DABAN-001 | active |
| UNI-RULE-001 | 全A可交易池 | rule_based | 沪深A股剔除 ST/退市/次新(<60天)/低流动性(<1000万) | monthly | 4500 | STR-MULTIFACTOR-001 | active |
| UNI-INDEX-001 | 沪深300成分股 | static | 中证指数公司官方，季度调整 | quarterly | 300 | — | active |
| UNI-INDEX-002 | 中证800成分股 | static | 沪深300+中证500，季度调整 | quarterly | 800 | — | active |
| UNI-RULE-002 | 事件驱动池 | rule_based | 全A可交易池 + 事件触发条件（并购/业绩/政策/增减持） | daily | null | STR-EVENT-001 | candidate |

**数据来源**：[24_daban_strategy_detail.md §3.1](24_daban_strategy_detail.md)（打板池）｜ [25_multifactor_strategy_detail.md](25_multifactor_strategy_detail.md)（多因子选股池/CSI300实证）｜ [26_event_driven_strategy_detail.md](26_event_driven_strategy_detail.md)（事件池）

### 5.2 benchmark_registry.yaml（基准，REG-BMK-001）

**Schema**：

```yaml
unique_key: [benchmark_id]
entry_schema:
  benchmark_id: str              # BMK-{TYPE}-{NNN}
  name: str
  name_zh: str
  aliases: list
  benchmark_type: str            # index / custom_equal / custom_cap / absolute / peer_strategy
  underlying_universe: str       # universe_id
  weight_method: str             # cap_weighted / equal_weighted / price_weighted / custom
  data_source: str               # data_asset_registry source_id
  used_by_strategies: list       # strategy_id 列表
  module_id: str
  doc_ref: str
  code_path: str
  status: str
  version: str
  created_at: date
  updated_at: date
  owner: str
  annual_return: float           # 运行时可空
  sharpe: float
  max_drawdown: float
  last_evaluated_at: date
  # 基准构造方法（v1.30.0 新增，对标 stockalpha.ai 2026-02-17 Custom Benchmarks + 2026 大基准重置 nasdaq.com 2026-06）
  construction_method: enum      # index_provider/holdings_based/returns_based/custom
                                 # index_provider=官方指数提供商（如中证指数公司，当前 BMK-INDEX-001/002/003 用此）
                                 # holdings_based=从组合成分构建（首选，可投资性约束 liquidity/free-float/weight caps/turnover limits）
                                 # returns_based=持仓不可得时用回归推断暴露（快速但精度低）
                                 # custom=自定义加权规则；BMK-ABSOLUTE-001 零基准填 absolute
                                 # 2026 大基准重置（Russell 半年再平衡+S&P 咨询）使"基准方法论稳定性"假设失效
  # 主动 share（v1.30.0 新增，对标 stockalpha.ai 2026-02-17）
  active_share: float            # 组合持仓与基准差异百分比（0=完全复制，1=完全主动）
                                 # 指示 concentration/overlap，BMK-ABSOLUTE-001 零基准填 null
                                 # MVP 阶段单策略填 null，Phase 1.5+ 多策略+因子暴露管理时 MUST 启用监控
  # 风格漂移检测（v1.30.0 新增，对标 nasdaq.com 2026-06 大基准重置）
  style_drift_detection: obj     # {method: enum(rolling_regression/holdings_similarity/none),
                                 #  monitoring_frequency: str}
                                 # rolling_regression=滚动因子暴露变化；holdings_similarity=持仓相似度（Jaccard/cosine）
                                 # MVP 阶段用 none（单策略无需漂移检测），Phase 1.5+ 多策略时启用
```

**实际登记内容（4 条）**：

| benchmark_id | name_zh | type | universe | 加权 | 使用策略 | 状态 |
|---|---|---|---|---|---|---|
| BMK-INDEX-001 | 沪深300指数 | index | UNI-INDEX-001 | cap_weighted | STR-MULTIFACTOR-001 | active |
| BMK-INDEX-002 | 中证500指数 | index | null | cap_weighted | — | candidate |
| BMK-INDEX-003 | 中证全指 | index | UNI-RULE-001 | cap_weighted | STR-EVENT-001 | candidate |
| BMK-ABSOLUTE-001 | 绝对收益（零基准） | absolute | null | null | STR-DABAN-001 | active |

**数据来源**：[25_multifactor_strategy_detail.md §CSI300实证](25_multifactor_strategy_detail.md)｜[52_backtest_framework_docking.md](52_backtest_framework_docking.md)（基准对接）

> 🔍 **2026 基准选择待定（v1.1.0 新增，需人决策）**：90 号 §13 提到基准选择待讨论。2026 年中证A500（2024-09 发布）已成机构标配底仓——年化收益 8.58% > 沪深300 7.55%，风险收益比 0.34 > 0.30，行业均衡 + 新质生产力权重高（[中信证券2026Q1研究](https://finance.sina.com.cn/jjxw/2026-05-18/doc-inhyiewk0690431.shtml) ｜ [国信证券策略专题](https://pdf.dfcfw.com/pdf/H3_AP202512301811362016_1.pdf)）。**待定问题 B1**：是否新增 `BMK-INDEX-004 中证A500`（candidate）作为 multifactor 策略的备选/替代基准？万得全A（881001）是否也需补登记作为全市场宽基基准？当前 4 条登记暂不修改，待用户裁定后补登。

### 5.3 cost_model_registry.yaml（交易成本模型，REG-CST-001）

**Schema**：

```yaml
unique_key: [cost_model_id]
entry_schema:
  cost_model_id: str             # CST-{TYPE}-{NNN}
  name: str
  name_zh: str
  aliases: list
  cost_model_type: str           # astock_standard / conservative / aggressive / zero_cost
  components: obj                # 成本组件（结构化）
    # commission: {rate, min, mode: both_sides}
    # stamp_duty: {rate, side: sell_only}
    # transfer_fee: {rate, market: sh_sz_both}
    # slippage: {model, params}
    # market_impact: {model, params}
  slippage_model: str            # fixed/linear/square_root/none
  impact_model: str              # none/square_root/linear
  # Propagator 模型参数（v1.30.0 新增，对标 hftradingbook 2026-06-04 Propagator 模型 + youngju.dev 2026-05-25 TCA Deep Dive）
  propagator_config: obj         # {decay_kernel: enum(exponential/power_law),  # 衰减核函数
                                 #  temp_impact_coeff: float,  # 临时冲击系数 η（交易速率项 η·n/τ）
                                 #  perm_impact_coeff: float}  # 永久冲击系数 γ（总交易量项 γ·Q）
                                 # 仅 execution_algo.impact_model_type=propagator 时必填
                                 # 描述冲击随时间的衰减传播（Bouchaud-Farmer 2018 瞬态冲击模型）
                                 # square_root/almgren_chriss/i_star 模型不填此字段
                                 # MVP 阶段不填（impact_model_type=square_root 不需 propagator 参数）
  used_by_strategies: list
  module_id: str
  doc_ref: str
  code_path: str
  status: str
  version: str
  created_at: date
  updated_at: date
  owner: str
```

**实际登记内容（3 条）**：

| cost_model_id | name_zh | type | 佣金 | 印花税 | 过户费 | 滑点 | 冲击 | 使用策略 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| CST-ASTOCK-001 | A股标准成本模型 | astock_standard | 万3/最低5元/双边 | 万5/卖 | 万0.1/沪深双向 | fixed 1bp | none | STR-DABAN/MULTIFACTOR/EVENT-001 | active |
| CST-ASTOCK-002 | A股保守成本模型 | conservative | 万3/最低5元/双边 | 万5/卖 | 万0.1/沪深双向 | fixed 2bp | square_root(coeff=0.1) | — | candidate |
| CST-ZERO-001 | 零成本模型 | zero_cost | 0 | 0 | 0 | none | none | — | active |

> ⚠️ **2026 费率校准（v1.1.0 修正硬错误）**：原 v1.0.0 登记印花税"千1（0.1%）"为 **2023-08-28 减半前旧税率**，2026 实际为 **万5（0.05%）卖出单边**（财政部/国家税务总局 2023-08-28 减半政策延续至今，2026 无调整）；过户费原登记"万0.1/沪市only"为旧规则，2026 实际 **沪深双向均收万0.1（0.001%）**（中国结算统一标准，无最低收费）。佣金万3 + 最低5元 双向为 2026 市场默认档（主流万1-万3可协商，免5违规），登记偏保守合理。详见 §13 修订记录 R1。

**数据来源**：[52_backtest_framework_docking.md §G1](52_backtest_framework_docking.md)（万三佣金/5元最低/1bp滑点）｜ [40_execution_broker.md §冲击模型](40_execution_broker.md)（保守模型冲击）｜ 2026 费率实证：[华泰证券2026费率](http://m.toutiao.com/group/7671636219272430089/) ｜ [2026最新收费标准](https://licai.cofool.com/user/guide_view_3447293.html) ｜ [2026炒股成本揭秘](https://post.m.smzdm.com/p/a70o48xd/) ｜ [yoyo-quant 2026-08-07](https://github.com/Tastelessor/yoyo-quant)（v1.6.0 补交叉验证：A 股量化框架开源项目，费率配置"佣金万1/最低5元 + 印花税万5/卖出单边 + 过户费 + 滑点 tick + 涨跌停价格剪裁"——印花税万5/卖单边 与本项目 R1 修正一致，佣金万1 vs 本项目万3 差异因 yoyo-quant 面向更低佣金档，本项目万3 偏保守合理）

**square_root 冲击系数校准说明**：CST-ASTOCK-002 的 `coefficient=0.1` 相对 2026 业界主流 prefactor `Y≈0.6`（hftradingbook 2026-06-04）/ AAPL 实证 `c_raw=0.69, c_eff=0.34`（arXiv 2606.24019, 2026-06）偏低约 6 倍。**对个人小资金项目合理**——个人账户多数订单 <1% ADV（40 号 §撮合拆单），无大单冲击，0.1 系数更接近"个人小单无冲击"的现实；Phase 1.5 AUM 增长到大单时需按 40 号 §13.1 校准路径重新拟合（40 号 v1.6.6 已登记 Phase 1.5 校准方法论）。

> 🎯 **2026-08 最新研究验证（v1.2.0 新增）**：平方根冲击律在 A 股的**必要性**与**指数差异**已被 2026-07 最新论文双重确认：
> - **必要性**（[Zhou et al. arXiv:2607.05141, 2026-07-06](https://arxiv.org/html/2607.05141v1)）：论文证明 square-root price impact 是 A 股学习智能体市场内生操纵周期的**必要条件**——线性冲击会完全消除 Hopf 分岔使零售市场无条件稳定，平方根冲击创造了自维持非线性振荡器。市场实现 A 股机制（±10% 涨跌停/T+1/机构卖出时隐蔽分发减半有效羊群参数）。**这从理论上验证了本项目选择 `square_root` 冲击模型（而非 linear）的正确性**。
> - **指数差异**（[Han, Wu, Cheng arXiv:1610.08767, 中国市场实证](https://arxiv.org/pdf/1610.08767v1)）：基于 172 亿条中国 A 股逐笔成交/报价记录拟合，临时冲击幂指数 `α≈0.7`（非 0.5），永久冲击 `α≈0.8`。北大团队结论"我们的模型优于 Almgren 模型"。**A 股 α≈0.7 高于美股 0.5**——意味着 A 股冲击对规模的敏感度更陡（同规模订单冲击更大），个人项目 `coefficient=0.1` 的保守设定需在 Phase 1.5 重新评估是否应改用 `power_law(exponent=0.7)` 而非 `square_root(exponent=0.5)`。
> - **拆单必要性**（[Zhou et al. arXiv:2607.04280, 2026-07](https://ideas.repec.org/p/arx/papers/2607.04280.html)）：订单拆分 + 流动性补充是平方根律的**联合必要条件**。移除订单拆分使 δ 从 0.549 塌缩到 0.324；移除做市商流动性补充降至 0.386。校准 TSE 基准 δ=0.489。**验证 40 号 TWAP/VWAP/ICEBERG 拆单算法的必要性**。
>
> **对 cost_model_registry 的影响**：当前 `square_root` model 字段保留（理论必要性已证）；Phase 1.5 校准时需考虑新增 `power_law(exponent=0.7)` 选项作为 A 股专用冲击模型（待定问题 C1），并按 40 号 §13.1 拟合 `coefficient` 实际值。MVP 阶段 `square_root(coeff=0.1)` 对个人小单足够保守，不阻塞当前回测。

> ⚠️ 注意：现有 `src/zephyr/.../cost_estimator.py` 是 **AI token 成本**，非交易成本。交易成本在 `engine_base.py`，本注册表管后者。

## 6. P1 待施工七注册表

### 6.1 P1-A：被测对象三件套（策略开发核心）

#### 6.1.1 factor_registry.yaml（因子库，REG-FCT-001）

**Schema**：

```yaml
unique_key: [factor_id]
entry_schema:
  factor_id: str                 # FCT-{CLASS}-{NNN}，如 FCT-MOM-001
  name: str
  name_zh: str
  aliases: list[str]
  factor_class: enum             # 10 类（见裁定 S2）：
                                 # value/quality/momentum/volatility/size/liquidity
                                 # /event/intraday/technical/sentiment
  formula: str                   # 表达式/公式（qlib 表达式或自然语言），人工因子必填
  schema_plan: obj               # v1.19.0新增：LLM 因子挖掘的语义抽象层（可选，对标 AlphaSchema 2026-08-01）
                                 # {event: str,         # 市场触发（earnings_surprise/macro_news/...）
                                 #  context: str,       # 市场环境或资产池（large_cap_chinese_equities）
                                 #  qualities: list[str], # 描述属性（volatility/liquidity/sentiment）
                                 #  direction: enum,    # positive/negative 预期价格方向
                                 #  output: str}        # 数值表示（z_score/binary_flag）
                                 # AlphaSchema 解耦"因子语义"（人类审查经济逻辑）与"实现公式"（formula/code_path）
                                 # Schema Generator 永不见原始价格数据，Implementation Agent 永不决定测哪个想法
                                 # 人工因子可不填（formula 已含语义）；LLM 挖掘因子 MUST 填 schema_plan
                                 # MVP 阶段所有因子人工编写可不填，Phase 2+ LLM 因子挖掘时启用
  params: obj                    # 参数字典（如 {window: 20}）
  inputs: list[str]              # 输入字段（引用 field_dictionary）
  outputs: list[str]             # 输出列名
  alpha_source: str              # alpha 来源一句话
  frequency: enum                # daily/intraday/tick
  lookback_period: int           # v1.2.0新增：回看周期（如 20/60/250 日），回测/因子计算必需
  universe: str                  # 适用股票池（universe_id）
  benchmark_id: str              # v1.2.0新增：因子评估基准（benchmark_id），计算超额 IC/IR
  neutralization: str            # industry/size/market/none
  pit_policy: str                # v1.10.0 增强：PIT（point-in-time）处理策略，防止 look-ahead bias
                                 # 对标 iceberglakehouse 2026-05 + beefed.ai 2026 + pfolio.io 2026-03-15 + tradevodata 2026-07-06
                                 # 关键：每个 feature 值 MUST 有"available_at"时间戳（何时对市场可见），非"period_end"（报告期截止日）
                                 # A 股 PIT 关注点：① 财报发布日 vs 报告期（tradevodata 实测 avg 43 天 lag，max 61 天）；
                                 #   ② 复权口径（前复权/不复权/后复权，与 E13 semantic_contract.adjust_method 联动）；
                                 #   ③ 涨跌停价格是否可成交（涨停板买入信号=look-ahead，实际无法成交）；
                                 #   ④ 指数成分变动（沪深300 半年调样，生效日 vs 公告日 ~5 天 lag）；
                                 #   ⑤ 复牌/停牌期间信号（停牌不可交易，信号须跳过）；
                                 #   ⑥ restatement（财报修正，原始值 vs 修正值，pfolio.io: look-ahead 可膨胀年化收益 100-500bps）
                                 # 填写示例："strict"（全部 PIT 校正）/ "lag_60d"（财报 lag 60 天）/ "price_only"（纯价格无基本面）
  module_id: str                 # depgraph MOD-L02-xxx
  doc_ref: str                   # 如 25_multifactor_strategy_detail.md §3.1
  code_path: str
  belongs_to_strategies: list[str]
  variant_of: str                # 可选：因子变体指向 parent
  status: enum
  version: str                   # v1.2.0明确：schema-significant 变更触发版本快照（对标 Feast 2026-03-31）
  version_pin: str               # v1.2.0新增：可选，回滚到历史版本（如 "v2"），Feast FeatureView version 模式
  created_at: date
  updated_at: date
  owner: str
  # 性能指标（运行时可空）
  ic: float
  ir: float
  decay_halflife: int
  decay_detection_method: str    # v1.2.0新增：衰减检测方法（rolling_ic/mrp/none），对标 Alexander&Fabozzi 2026
                                 # v1.4.0扩展：补 profit_factor/z_score（PineForge 实用派），见 §4.8
                                 # v1.22.0扩展：补 gsa_llr_cusum（GSA-LLR 重尾鲁棒变体，A 股 γ₄≥6 自动切换，见 §4.8）
  last_decay_scan_at: date       # v1.2.0新增：上次衰减扫描时间
  turnover: float
  capacity: float
  last_evaluated_at: date
  code_commit: str               # v1.4.0新增：可选，git commit hash（DB 阶段 MUST，对标 beefed.ai compute_git + §4 原则9 Immutable）
  # 数据质量监控（v1.4.0新增，对标 metricgate L1-L2 + apxml PSI/KS + RisingWave null_rate）
  # 衰减是输出端（§4.8 DECAY_SCAN），数据质量是输入端，互补——alert on earliest layer
  data_quality_policy: obj       # {null_rate:{threshold,window}, drift_method:psi/ks, drift_threshold}
                                 # E11 审计检查此字段（factor/strategy MUST 声明）
  null_rate: float               # 运行时：当前空值率（RisingWave: >2x baseline 告警）
  drift_psi: float               # 运行时：PSI 分布漂移（<0.1稳定/0.1-0.25轻微/>0.2主要漂移，apxml）
  drift_ks_pvalue: float         # 运行时：KS 检验 p-value（<0.01 显著漂移，metricgate）
  range_bounds: obj              # {min,max} 训练期范围（越界=数据异常，metricgate L1）
  last_quality_scan_at: date     # 上次数据质量扫描时间
  # 因子冗余/相关性治理（v1.20.0 新增，对标 EntroPy 2026-05 + factordbms + CSDN 2026-07）
  correlation_group: str         # 相关性分组（如 value/quality/momentum/volatility）
                                 # 同组因子=高相关簇，MUST 有一个 independent + 其余 redundant/orthogonal
                                 # MVP 可按因子 10 分类粗分，Phase 1.5+ 接入三维度检测后精细化
  redundancy_status: enum        # independent/redundant/orthogonal，冗余状态
                                 # independent=独立信号（同组至少 1 个）
                                 # redundant=与同组 independent 因子高相关（r>0.7）
                                 # orthogonal=与同组 independent 因子低相关（r<0.3）
  # 因果验证声明（v1.21.0 新增，对标 causal-quant v0.4.1 2026-07 + CIR-ACTIVA arXiv:2608.03715 2026-08）
  causal_graph: str              # 因果图/经济逻辑描述（自然语言或 DAG 描述）
                                 # causal-quant: 因子注册时 MUST 声明因果图，避免事后合理化
                                 # 钉住回测撒谎三种方式：luck/confounding/selection across everything you tried
                                 # MVP 可填自然语言（如'高ROE→持续盈利→股价上涨'）
                                 # Phase 1.5+ 接入 causal-quant 证伪电池后补 H-score（存活 edge 比例）
                                 # §4.7 E17 审计检查此字段（warning 级，MVP 不阻断）
  # 因子构造方法学偏差审计（v1.22.0 新增，对标 arXiv:2604.07880 2026-04 企业债因子动物园 LIB + ex-post 过滤）
  lib_audit: obj                 # Latent Implementation Bias 审计结果，仅 price-derived 因子声明
                                 # {applicable: bool,           # 是否 price-derived（非价格因子填 false 跳过）
                                 #  signal_return_shared_noise: bool,  # 信号与收益是否共用噪声数据源（复权价/成交量既入因子又入收益分母=true=LIB 风险）
                                 #  mitigation: str}            # 缓解措施（separate_signal_return_sources/walk_forward_returns/none）
                                 # arXiv:2604.07880: 108 企业债因子纠正 LIB 后多数不再显著
                                 # A 股关联：复权价/成交量既是因子输入又是收益计算分母=LIB 风险
                                 # §4.7 E19 审计检查此字段（warning 级，MVP 不阻断）
  ex_post_filter_audit: obj      # ex-post 过滤审计结果（去极值/去流动性差是否用全期统计量）
                                 # {uses_full_period_stats: bool,  # 去极值/去流动性差是否用全期统计量（true=嵌入未来信息=偏差）
                                 #  walk_forward_corrected: bool,  # 是否改用 walk-forward 滚动统计量
                                 #  filter_method: str}           # winsorize_full/winsorize_rolling/trim_full/trim_rolling/none
                                 # arXiv:2604.07880: ex-post 收益过滤嵌入未来信息是因子动物园复制危机根因之二
                                 # §4.7 E19 审计检查此字段（warning 级，MVP 不阻断）
  # RMT 去噪因子相关性矩阵（v1.23.0 新增，对标 arXiv:2507.17211v2 2026-08 EFS + arXiv:2601.07687v4 2026-08 物理信息奇异值学习）
  rmt_denoised: obj              # 因子相关性矩阵是否经 Marchenko-Pastur RMT 去噪
                                 # {applicable: bool,             # 是否启用（因子数<20/q<0.1 时填 false）
                                 #  method: str,                  # clipping/shrinkage/none（clipping=噪声特征值替换为均值）
                                 #  q_ratio: float,               # q=N_factors/T_observations（>0.1 时 MUST 去噪）
                                 #  noise_eigenvalue_ratio: float} # 落在 [λ₋,λ₊] 噪声区间的特征值比例（>50%=高噪声）
                                 # arXiv:2507.17211v2: RMT 去噪+正则化 QP 在美股/港股/A股均优于未去噪基线，无额外调参
                                 # Marchenko-Pastur 律: λ±=σ²(1±√q)²，区间内特征值是噪声非信号
                                 # §4.7 E20 审计检查此字段（warning 级，MVP 不阻断）
                                 # Phase 2+ 评估物理信息奇异值学习（神经网络估计器替代解析收缩，处理非平稳）
  # 流动性因子度量（v1.26.0 新增，对标 §4.33① Kyle lambda + Aldridge arXiv:2607.01377 2026-07 + microalphas 2026-06-02）
  liquidity_metric: obj           # 流动性度量，仅 factor_class=liquidity 的因子声明
                                 # {metric_type: enum,          # kyle_lambda/amihud/adv/turnover/ofi，度量类型
                                 #  value: float,               # 当前估计值（运行时可空）
                                 #  estimation_method: str,     # daily_regression/amihud_ratio/ofi_direct
                                 #  data_requirement: str}      # level2/daily/tick，所需数据粒度
                                 # Kyle lambda = 价格冲击系数 = 市场深度倒数，同时是流动性/价格冲击/逆向选择三重度量
                                 # Aldridge arXiv:2607.01377 (CRSP 2020-2025): 签名订单流强预测同期+1月前瞻收益
                                 # ⚠️ 实现陷阱（JohnGavin #627 2026-08-03 修复）：
                                 #   kyle_lambda MUST 用 OLS slope = cov(log_ret, signed_flow)/var(signed_flow)
                                 #   而非 ratio = abs(log_ret)/volume（ratio 形式塌缩为 Amihud，二者数值恒等=bug）
                                 #   即 ΔP_t = λ·Q_t + ε_t 的回归斜率，非价格变动绝对值除以成交量
                                 # MVP 阶段用 ADV/turnover 粗估（日线数据），Phase 1.5+ 接入 Level-2 后计算精确 lambda/OFI
  # 因果设定结构（v1.31.0 新增，对标 CFA Institute 2025/2026 Factor Mirage López de Prado + causal-quant v0.4.1）
  causal_structure: obj          # {confounders: list,            # 故意排除的混杂变量列表（同时影响因子和收益，须控制）
                                 #  colliders: list,              # 已纳入但被因子和收益共同影响的变量列表（风险标志）
                                 #  specification_audit: str}     # natural_language/collider_flagged/confounder_controlled
                                 # Factor Mirage=错误设定模型展现更高 R²+更低 p-value，计量教规主动偏好这类错误模型
                                 # collider 比 confounder 更危险：collider 变量值在收益前已定，更强关联无法货币化=海市蜃楼
                                 # 系数符号翻转实证：正确流动性 loading +0.08 → 错误控制变量下 −0.04（López de Prado 26 Barra 模型审计）
                                 # A 股最常见陷阱：past_return 作为 collider（被 quality 因子和未来收益共同影响）→ 虚假高 R²
                                 # §4.7 E17 审计检查扩展（v1.31.0）：E17 扩展为"因果验证+设定结构检查"，collider 非空=warning highlight
                                 # MVP 阶段用自然语言填（如 momentum confounders=[market_beta,sector_rotation], colliders=[]）
                                 # Phase 1.5+ 接入 causal-quant v0.4.1 证伪电池后补 H-score（causal_graph 字段承载 DAG 声明）
```

**factor_class 10 类**（Barra 6 + A股特色 4）：
- Barra 标准：`value`（价值）/ `quality`（质量）/ `momentum`（动量）/ `volatility`（波动）/ `size`（规模）/ `liquidity`（流动性）
- A 股特色：`event`（事件驱动，并购/业绩/政策）/ `intraday`（日内/打板，T+1+涨跌停特色）/ `technical`（技术指标衍生）/ `sentiment`（情绪/舆情，游资接力）

**数据来源**：
- [15_data_feature_layer_spec.md](15_data_feature_layer_spec.md)（因子工程总纲，why 层）
- [25_multifactor_strategy_detail.md](25_multifactor_strategy_detail.md)（IC/衰减/换手评估格式）
- 代码 `src/zephyr/factor/`（v1.1.0 修正：原 v1.0.0 误写 `src/zephyr/factor/ashare/` 15 子目录，**该路径不存在**。实际结构：`analysis/api/core/governance/infrastructure/services/technical_indicators/_extensions` 子目录 + `factor_base.py`/`momentum_factor.py`/`value_factor.py`/`intraday_snapshot_factors.py`/`alpha_signal_pipeline.py`/`bus_factor_defense.py` 6 个因子模块文件）。P1-A 施工时从此处反查登记实际因子，MVP 先登记已实现的 momentum/value/intraday/alpha_signal/bus_factor 5 类，按需扩展
- dataflow DS-015+（因子数据集登记，v1.1.1 修正：DS 编号实际到 DS-076 总 76 条，非 DS-028 截止）

**施工要点**：
- 与 technical_indicator_registry 正交：技术指标=OHLCV 计算工具，因子=alpha 来源
- 连板因子 / 趋势因子 = 2 条独立记录（alpha 来源不同，非 variant）
- 对标 WorldQuant Alpha Bank / qlib Alpha158

> 🎯 **2026 Feast Feature View Versioning 对标（v1.2.0 新增）**：[Feast 2026-03-31 发布实验性 Feature View Versioning](https://feast.dev/blog/feature-view-versioning/)——自动版本追踪 + 安全回滚 + 多版本在线服务。核心机制：① schema/UDF 变更触发版本快照（v0→v1→v2），metadata-only 变更原地更新；② `version="v2"` pin 到历史版本（回滚）；③ `@v<N>` 语法多版本在线读（`enable_online_feature_view_versioning` flag）；④ `--no-promote` staged publishing（新版本不立即生效）。**对 factor_registry 的影响**：本 schema 已预留 `version` + `version_pin` 字段对标此模式。个人项目 YAML 阶段用 git diff/history 替代自动快照（git 即天然版本历史），未来迁 DB 后可启用 Feast 式 `version_pin` 回滚能力。PIT correctness（Feast 强调"point-in-time correctness 是硬要求"）由 `pit_policy` 字段承载，与 Feast 的 event_timestamp + created_timestamp 双时间戳设计对齐。详见 [Feast RFC ADR-0008](https://github.com/bisht2050/feast/blob/master/docs/adr/ADR-0008-feature-view-versioning.md)。

#### 6.1.2 strategy_registry.yaml（策略库，REG-STR-001）

**Schema**：

```yaml
unique_key: [strategy_id]
entry_schema:
  strategy_id: str               # STR-{CLASS}-{NNN}，如 STR-DABAN-001
  name: str
  name_zh: str
  aliases: list[str]
  strategy_class: enum           # 6 类（见裁定 S3）：
                                 # daban/multifactor/event_driven
                                 # /value_reversal/momentum_trend/sector_rotation
  sleeve: str                    # 所属 sleeve（小账本）
  alpha_sources: list[str]       # factor_id 列表（关联 factor_registry）
  variant_of: str                # 可选：variant 指向 parent strategy_id（单向，裁定 S4）
  entry_logic: str
  exit_logic: str
  position_sizing: str           # Kelly/固定比例/风险预算
  risk_rules: list[str]          # risk_limit_id 列表
  holding_period: str            # T+1/波段/趋势
  benchmark_id: str              # v1.2.0新增：策略对标基准（benchmark_id），计算超额收益
  module_id: str
  doc_ref: str
  code_path: str
  lifecycle_status: enum         # v1.2.0扩展：candidate/backtest/sim/paper/live/monitoring/decayed/retired
                                 # 新增 decayed 态（对标 Vibe-Trading 2026-07 衰减状态机）
  status: enum                   # active/deprecated/retired（治理状态）
  version: str
  created_at: date
  updated_at: date
  go_live_date: date
  retired_date: date
  owner: str
  # 衰减检测（v1.2.0新增，对标 Alexander&Fabozzi 2026 MRP + Vibe-Trading DecayEvaluator）
  decay_detection_method: str    # v1.4.0扩展：rolling_ic/mrp/cusum/cusum_ph_bocpe/profit_factor/z_score/none
                                 # v1.22.0扩展：补 gsa_llr_cusum（GSA-LLR 重尾鲁棒变体，A 股 γ₄≥6 自动切换，见 §4.8）
                                 # MVP 用 profit_factor/z_score（PineForge 实用派），Phase1.5+ 用 cusum_ph_bocpe
  decay_threshold: float         # ic_ratio < 0.7 触发 decayed（Vibe-Trading 恢复条件）
  last_decay_scan_at: date
  mrp_baseline: float            # Minimum Regime Performance 基线（Alexander&Fabozzi 2026）
  # 衰减后适应（v1.4.0新增，对标 §4.12 ADAPT_STRATEGY + mathandmarkets Part 82 五级响应）
  adaptation_level: int          # 1-5：1静默监控/2减仓/3季度refit/4在线学习/5退役（默认1）
  last_refit_at: date            # 上次参数 refit 时间（§4.12 约束：间隔≥60天防过拟合）
  baseline_sharpe: float         # OOS walkforward 期基线 Sharpe（ADAPT_STRATEGY Step4 恢复判定基准）
  # baseline 扩展（v1.5.0新增，对标 LuxAlgo 2026-08-03 baseline 保存要求 + §4.7 E12 审计检查）
  # LuxAlgo: "Without that baseline, it is difficult to distinguish normal variance from a genuine change"
  # baseline MUST 在 deployment（paper→live）时保存，是 DECAY_SCAN + ADAPT_STRATEGY 的前提
  baseline_expectancy: float     # 基线单笔期望（win_prob×avg_win - loss_prob×avg_loss）
  baseline_win_rate: float       # 基线胜率
  baseline_profit_factor: float  # 基线盈亏比（gross profit / gross loss）
  baseline_max_drawdown: float   # 基线最大回撤（review trigger 2 的 prior max_dd 基准）
  baseline_trade_frequency: float # 基线交易频率（trades/month，决定 trade-count vs calendar 窗口选择）
  # 衰减原因分类（v1.5.0新增，对标 smartfinancedata 2026 Five Horsemen，§4.12 Step 1.5 引用）
  decay_cause: enum              # crowding/regime/overfitting/tech/depletion/unknown
                                 # crowding(41%)/regime(28%)/overfitting(18%)/tech(9%)/depletion(4%)
                                 # 决定 refit vs 退役：crowding/overfitting/tech→直接退役；regime/depletion→refit
  decay_scan_frequency: enum     # v1.5.0新增：扫描频率 monthly/weekly/daily（对标 Pomegra 2026）
                                 # active/live=monthly, monitoring=weekly, decayed=daily
  # 性能（运行时可空）
  sharpe: float
  max_drawdown: float
  annual_return: float
  capacity: float
  turnover: float
  last_evaluated_at: date
  code_commit: str               # v1.4.0新增：可选，git commit hash（DB 阶段 MUST，对标 beefed.ai compute_git）
  # 数据质量监控（v1.4.0新增，对标 metricgate L1-L2 + apxml PSI/KS，E11 审计检查）
  data_quality_policy: obj       # {null_rate:{threshold,window}, drift_method:psi/ks, drift_threshold}
  null_rate: float               # 运行时：当前空值率（RisingWave: >2x baseline 告警）
  drift_psi: float               # 运行时：PSI 分布漂移（<0.1稳定/>0.2主要漂移）
  drift_ks_pvalue: float         # 运行时：KS 检验 p-value（<0.01 显著漂移）
  range_bounds: obj              # {min,max} 训练期范围
  last_quality_scan_at: date     # 上次数据质量扫描时间
  # 策略组合配置（v1.18.0 新增，对标 digitalninjasystems 2026-05-24 + 中金 2026-06-24 Regime-Based 融合）
  combination_strategy: obj      # {regime_detector: "200d_sma"/"hmm"/"news_aware"/"none",  # v1.19.0补 news_aware
                                 #  allocation_weights: {"trending_up": {"momentum": 0.8, "mean_reversion": 0.2},
                                 #                       "trending_down": {"momentum": 0.6, "mean_reversion": 0.4},
                                 #                       "ranging": {"momentum": 0.15, "mean_reversion": 0.85}}}
                                 # 单体策略=null；组合策略登记 regime 检测器 + 各 regime 下子策略权重
                                 # 中金增强信号策略：最大回撤 -5.42%→-2.99%，卡玛比率 0.98→1.71
                                 # regime_detector 取值（v1.19.0 补 news_aware，v1.26.0 补 wasserstein_hmm，v1.27.0 补 text_var_dual，v1.31.0 补 statistical_jump/jump_diffusion_hmm）：
                                 #   200d_sma: 简单可解释，MVP 默认（200日SMA以上trending，否则ranging）
                                 #   hmm: 隐马尔可夫模型，Phase 1.5+ 评估（受"过快回归"失败模式影响）
                                 #   wasserstein_hmm: Wasserstein 距离 HMM，解决标签置换问题（v1.26.0 §4.33①）
                                 #   news_aware: Alpha-R1 风格语义 regime（因子理性 × 新闻叙事语义对齐），
                                 #               需 8B RL 模型 + 实时新闻流，Phase 3+ 远期评估
                                 #   text_var_dual: 文本+VAR 双向验证 regime 检测（v1.27.0 §4.34④）
                                 #   statistical_jump: Nystrup 显式跳跃惩罚，捕获持续 regime（v1.31.0 §4.38③）
                                 #                     data-driven 惩罚选择，实证优于 Markov-switching，特征仅 price-derived
                                 #   jump_diffusion_hmm: HMM + Poisson jump-duration，强制尾部驻留时间（v1.31.0 §4.38③）
                                 #                       避免 Baum-Welch EM，合成数据+压力测试场景设计用
                                 #   none: 不检测 regime，全周期等权
                                 # Phase 1.5+ 评估，MVP 阶段单体策略足够（§4.25② + §4.26⑤）
  # 信号融合：Meta-labeling 方向×仓位分离（v1.18.0 新增，对标 Neyt 2026-03 + NTU 2026-05-20 + mental-momentum 2026-06-14）
  meta_labeling_config: obj      # {strategy_subtype: meta_labeled, primary_strategy_id: STR-XXX,
                                 #  meta_strategy_id: STR-YYY, base_models_error_correlation: float}
                                 # primary 定方向（买/卖），meta 定仓位（filter false positive）
                                 # 关键：base models 误差不相关，meta 显式处理假阳性
                                 # Phase 2+ 远期评估，MVP 阶段单体策略足够（§4.25③）
  # 策略来源标记 + LLM 蒸馏（v1.19.0 新增，对标 TiMi ICLR 2026 + 国联民生金工 AAAI2026+ICLR2026 综述）
  origin: enum                   # human/llm_generated/hybrid，策略来源标记
                                 # TiMi ICLR 2026: LLM 交易智能体不应直接承担低延迟执行——
                                 #   离线 LLM 研发策略蒸馏为纯代码，在线只执行已固化代码
                                 # human: 完全人工编写（MVP 默认）
                                 # llm_generated: LLM 生成（MUST 经人工审查 + 蒸馏到代码）
                                 # hybrid: 人机协作（LLM 提案 + 人工修改）
  distilled_to_code: bool        # 是否已蒸馏为可执行代码（脱离 LLM 在线调用）
                                 # TiMi: LLM 生成的策略 MUST 蒸馏为纯代码才能进入实盘
                                 # §4.13 PROMOTE_ENTRY G5 门禁检查：llm_generated 策略 distilled_to_code=false=阻断上线
                                 # human 策略天然 distilled_to_code=true（代码即原码）
                                 # MVP 阶段所有策略 origin=human, distilled_to_code=true
  # 策略容量配置（v1.20.0 新增，对标 breakingalpha 2026-01 + linitics 2026-04 + EntroPy 2026-05）
  capacity_aum_limit: float      # 策略资金容量上限（元），如 1e7=1000万
                                 # breakingalpha 2026-01: capacity 是 primary filter，未声明=不知道策略能承载多少资金
                                 # MVP 阶段小资金可填保守估值（如日线策略按 5% ADV 估算）
  participation_rate_limit: float # 参与率上限（0.05=5% ADV），机构约束 ≤5-10%
                                 # linitics 2026-04: 超限导致冲击增加/被识别/逆向价格运动
  market_impact_model: enum      # square_root/linear/none，市场冲击模型
                                 # square_root=业界共识平方根模型 Impact=σ×k×√(Q/ADV)
                                 # linear=线性近似 Impact=k×Q/ADV（仅用于教学）
                                 # none=MVP小资金忽略冲击（实盘前 MUST 升级 square_root）
```

**strategy_class 6 类**：
- `daban`（打板，含连板梯队/趋势低吸 2 variant）
- `multifactor`（多因子）
- `event_driven`（事件驱动）
- `value_reversal`（价值反转，27 号二批）
- `momentum_trend`（动量趋势，27 号二批）
- `sector_rotation`（行业轮动，22 号独立 spec）

> ❌ 不含 `sentiment_cycle`：28 号情绪周期是 sleeve 内 alpha 择时机制（project_memory 明确"情绪周期=sleeve 内机制，非独立策略"）

**variant 机制**（裁定 1 + S4）：
- 打板 = 1 strategy（STR-DABAN-001），连板/趋势 = 2 variant（各一条记录，`variant_of` 指向打板）
- 单向引用：只留 `variant_of`，删除 `variants` 列表（避免双向同步漂移）
- 查"打板所有 variant" = `WHERE variant_of = STR-DABAN-001`

> 🎯 **2026 Strategy Lifecycle Management 对标（v1.2.0 新增）**：2026 主流策略生命周期为 **10 阶段模型**（[Linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/) ｜ [DeepTradeX 2026](https://deeptradex.zendesk.com/hc/en-us/articles/16820285969295-Strategy-Lifecycle-Management-Great-Trading-Strategies-Are-Managed-Not-Just-Built)），比传统 5-6 阶段新增 **Decay Detection** 和 **Decommissioning** 独立阶段。本 schema `lifecycle_status` 已扩展为 8 态（新增 `decayed`），完整映射见 §4.8。关键 2026 研究：
> - **Alexander & Fabozzi 2026 MRP**（Minimum Regime Performance，[VertoxQuant 2026-04-14](https://www.vertoxquant.com/p/strategy-decay-detection)）：跨结构不同 regime 测量策略持久性，惩罚高衰减倾向的策略（如同惩罚 VaR 尾部风险）。本 schema `mrp_baseline` 字段承载此方法。
> - **Vibe-Trading 2026-07 衰减状态机**（[PR #457](https://github.com/HKUDS/Vibe-Trading/pull/457)）：`created → benching → active → monitoring → decayed → disabled`，恢复条件 IC ratio > 0.7。SQLite backend + 3 表（artifacts/bench_history/decay_snapshots）+ DecayEvaluator 纯逻辑状态机 + 60 测试。本 schema `decay_threshold: 0.7` 直接对标此恢复条件。
> - **经验数据**（[Maven Securities via BreakingAlpha 2025-12](https://breakingalpha.io/insights/alpha-decay-detection-purchased-trading-strategies)）：alpha 衰减年均 US 5.6% / EU 9.9%；68% 策略 18-24 月需修改/退役；2+ 年持续低于阈值触发退役。退役非"亏钱时"而是"失去统计有效性时"。
>
> 衰减检测算法实现见 §4.8 `DECAY_SCAN(strategy_id)`。

**数据来源**：
- [20_first_batch_strategies.md](20_first_batch_strategies.md)（首批 3 策略：打板/多因子/事件驱动）
- [24_daban_strategy_detail.md](24_daban_strategy_detail.md)（打板，含连板/趋势切换）
- [25_multifactor_strategy_detail.md](25_multifactor_strategy_detail.md)（多因子）
- [26_event_driven_strategy_detail.md](26_event_driven_strategy_detail.md)（事件驱动）
- [27_second_batch_strategies.md](27_second_batch_strategies.md)（二批：价值反转/动量趋势）
- [22_sector_rotation_spec.md](22_sector_rotation_spec.md)（行业轮动）

#### 6.1.3 technical_indicator_registry.yaml（技术指标，REG-IND-001）

**Schema**：

```yaml
unique_key: [indicator_id]
entry_schema:
  indicator_id: str              # IND-{CLASS}-{NNN}，如 IND-TREND-001
  name: str
  name_zh: str
  aliases: list[str]
  indicator_class: enum          # trend/momentum/volatility/volume/reversal（5类对齐16号§2，v1.1.0修正：原structure→reversal）
  formula: str
  params: obj                    # {period: 14}
  inputs: list[str]              # OHLCV 子集
  outputs: list[str]
  warmup_period: int             # v1.2.0新增：预热周期（如 EMA12 需 12 根 K 线才有效，回测须丢弃前 N 根）
  computation_mode: enum         # vectorized/streaming/both（双模式，16号 why 层）
  module_id: str
  doc_ref: str                   # 16_technical_indicator_catalog.md §2
  code_path: str
  used_by_factors: list[str]     # 反向关联 factor_id
  status: enum
  version: str
  created_at: date
  updated_at: date
  owner: str
```

**5 大类**（对齐 16 号 §2，v1.1.0 修正第5类）：trend（趋势，MA/MACD，10个）/ momentum（动量，KDJ/RSI，10个）/ volatility（波动，BOLL，8个）/ volume（量能，MFI，7个）/ reversal（反转，5个）。合计 40 指标 ~55 输出列。**原 v1.0.0 第5类误写 `structure`，实际 16 号 §2.5 + 代码 `src/zephyr/factor/technical_indicators/reversal.py` 均为 `reversal`（反转类）**——schema-代码-文档三方漂移已修正。代码 `technical_indicators/` 实际文件：indicator_base/momentum/reversal/trend/volatility/volume 6 个 .py。

**9 个周期**（project_memory）：1min/5min/15min/30min/60min/120min/日/周/月（120min 由 60min 两根聚合）

**数据来源**：
- [16_technical_indicator_catalog.md](16_technical_indicator_catalog.md) §2 清单（40 指标/5类/~55 输出列）迁入
- 16 号文档降级为 why 层（设计原则/双模式计算/宽表存储/A股约束），§2 改引用注册表
- 代码 `src/zephyr/factor/technical_indicators/`

**施工要点**：
- 与 factor_registry 正交：指标=计算工具（连续值），因子=alpha 来源
- 对标 QuantConnect Indicators / backtrader.indicators
- 存储架构：单表设计，新增 `period` 列区分 9 周期，按 (period, toYYYYMM(trade_date)) 分区

### 6.2 P1-B：交易/风控/数据/图形

#### 6.2.1 execution_algo_registry.yaml（执行算法，REG-EXA-001）

**Schema**：

```yaml
unique_key: [execution_algo_id]
entry_schema:
  execution_algo_id: str         # EXA-{NAME}-{NNN}，如 EXA-TWAP-001
  name: str
  name_zh: str
  aliases: list[str]
  algo_class: enum               # v1.1.0修正对齐40号实际6算法：twap/vwap/iceberg/implementation_shortfall/percent_of_volume/alt
                                 # 原v1.0.0误写aggressive/adaptive，40号实际为ICEBERG(隐藏大单)+ALT(激进对手价吃单)
  formula: str
  params: obj                    # {slicing: time, bucket: 5min}
  applicable_scenario: str       # 大单/小单/流动性差/急单
  warmup_participation_rate: float  # v1.2.0新增：预热参与率（前 N 分钟低参与避免冲击），对标 MACE 2026
  cooling_period: int            # v1.2.0新增：冷却期（大单执行后等待分钟数，防止连击冲击）
  anti_gaming: obj               # v1.7.0新增：反博弈随机化配置（对标 marketmaker.cc 2026-07）
                                 # {timing_randomization: poisson/uniform/none, size_jitter: float(0-0.3)}
                                 # marketmaker.cc: "Any serious TWAP randomizes child timing and size;
                                 #   the schedule should be a Poisson-ish process whose expectation is flat, not a clock"
                                 # 确定性时钟切片（每60秒固定:00下单）= 节拍器，被前置交易者识别并抢跑
  tca_metrics: list[str]         # v1.7.0新增：TCA 交易成本分析指标清单（对标 iotdigitaltwinplm 2026-06）
                                 # 推荐 [vwap_slippage, implementation_shortfall, fill_rate, market_impact]
                                 # iotdigitaltwinplm: "report both VWAP slippage AND implementation shortfall—
                                 #   they answer different questions, shipping only the flattering one erodes trust"
  market_impact_model: str       # 引用 40号 propagator/Barzykin
  impact_model_type: enum        # v1.30.0新增：回测/实盘所用冲击模型谱系（§4.37②）
                                 # square_root/almgren_chriss/i_star/propagator/fixed_bps/pluggable
                                 # square_root=Gatheral 2010 凹性冲击 ΔP≈Y·σ·√(Q/V)（MVP 默认，参数少）
                                 # almgren_chriss=AC 均值-方差最优执行 min E[Cost]+λ·Var[Cost]（永久线性+临时冲击）
                                 # i_star=Kissell-Glantz 2003 瞬时+永久分量定价（基于订单规模/ADV/波动率）
                                 # propagator=Bouchaud-Farmer 2018 瞬态核函数（精细但参数多，配合 cost_model.propagator_config）
                                 # fixed_bps=固定 bps（MVP 简单回测兜底）；pluggable=可插拔自定义模型
                                 # MACE arXiv:2603.29086 实证：不同冲击模型致 RL agent 排名质变（差异 40%+）
                                 # 同策略不同 impact_model_type 结果不可比——回测 MUST 声明所用模型
  cost_model_ref: str            # v1.2.0新增：关联 cost_model_id（计算执行成本）
  rl_policy_ref: str             # v1.2.0新增：可选，RL 策略引用（远期选项，见下 RL 对标）
  module_id: str
  doc_ref: str                   # 40_execution_broker.md
  code_path: str                 # src/zephyr/ex_sor/
  status: enum
  version: str
  created_at: date
  updated_at: date
  owner: str
```

**6 算法用途**（对齐 40 号 §撮合拆单实际，v1.1.0 修正）：
- `twap`（等量切片被动挂单，中单 1-5% ADV）
- `vwap`（按日内量能分布，大单 5-15% ADV，契合 A 股 U 型成交：开盘20%/上午25%/午盘10%/尾盘45%）
- `iceberg`（小额显示量隐藏大单，原 v1.0.0 遗漏，40 号已实现）
- `implementation_shortfall`（IS，指数衰减启发式近似 AC 风险厌恶轨迹，超大单 >15% ADV）
- `percent_of_volume`（POV，参与率≤5%，γ≤5% 时内生性可忽略）
- `alt`（激进对手价吃单，游资"狙击"量化版，原 v1.0.0 误写 `aggressive`/`adaptive`）

> ⚠️ **v1.1.0 修正**：原 v1.0.0 的 `aggressive`/`adaptive` 在 40 号文档无对应实现，实际 40 号 §撮合拆单 6 算法为 TWAP/VWAP/ICEBERG/POV/IS/ALT。`alt` 可保留 `aggressive` 作为别名（语义相同：激进对手价吃单），但 `adaptive` 在 40 号无实现应删除。POV 内生性说明（γ/(1-γ) 纠正）见 40 号。

**数据来源**：[40_execution_broker.md](40_execution_broker.md)（6 种算法：TWAP/VWAP/ICEBERG/POV/IS/ALT，代码已实现注册表模式）｜ 代码 `src/zephyr/ex_sor/`（api/core/infrastructure/models/services 子目录）

> 🎯 **2026 RL 自适应执行远期选项（v1.2.0 新增）**：2026 年 RL 执行算法研究有 3 项重要进展，作为本注册表 `rl_policy_ref` 字段的远期选项（Phase 1.5+ 评估，MVP 不实施）：
> - **MACE**（[Riera Abbade & Reali Costa, arXiv:2603.29086, 2026-03-30](https://arxiv.org/html/2603.29086v1)）：Market-Adjusted Cost Execution 环境，集成 Almgren-Chriss 框架 + 平方根冲击律 + 永久冲击指数衰减。评测 A2C/PPO/DDPG/SAC/TD3 五算法，**关键发现：成本模型实质性影响算法排名**——PPO 在 baseline 成本下 OOS 20% 回报/Sharpe 1.06，AC 模型下降到 15%；TD3 在 AC 下 32%（最优）。HPO 必需（无 HPO 时 SAC 成本降 82% 但出现病态交易）。开源为 FinRL-Meta 扩展。
> - **Cheridito & Weiss**（[arXiv:2507.06345v2, 2026-01-26](https://arxiv.org/pdf/2507.06345v2)）：Logistic-Normal 策略参数化，市场单+限价单联合分配，simplex 动作空间。优于传统 TWAP/VWAP 基准。RL-LOB 开源实现（[github cmarvinzurich/RL-LOB, 2025-09](https://github.com/cmarvinzurich/RL-LOB)）。
> - **PPO 自适应执行**（[Stanford CS224R 2025](https://cs224r.stanford.edu/spring_2025/projects/pdfs/CS224r_final_paper%20(4).pdf)）：PPO 在波动率高/流动性低时自动减速暂停（risk-sensitive 响应），显著优于 TWAP/VWAP 静态基线。DDPG 对超参敏感、方差大。
>
> **个人项目适用性评估**：RL 执行需要 LOB 模拟器 + 大量训练 + HPO，对个人项目属过度工程（MVP 阶段）。但 schema 预留 `rl_policy_ref` 字段，Phase 1.5+ AUM 增长到需要自适应执行时可引用 MACE/Cheridoto-Weiss 策略。MVP 阶段 6 算法（TWAP/VWAP/ICEBERG/POV/IS/ALT）足够。`warmup_participation_rate` + `cooling_period` 字段借鉴 MACE 的 HPO 发现（避免 epoch 间参与率单调递增的病态）。

> 🔒 **执行算法反博弈与 TCA 双报告（v1.7.0 新增，对标 [marketmaker.cc 2026-07-15](https://marketmaker.cc/en/blog/post/twap-vwap-pov-execution-algorithms/) + [iotdigitaltwinplm 2026-06-18](https://iotdigitaltwinplm.com/vwap-execution-algorithm-architecture-2026/)）**：
>
> **① 反博弈随机化**（marketmaker.cc 2026-07）：每个执行调度器都是对成交量预测的下注——TWAP 押注流动性时间均匀，VWAP 押注今日曲线=昨日，POV 押注实时成交量=交易理由。**确定性切片是被抢跑的陷阱**："A TWAP that fires a child order every 60 seconds at :00 is a metronome, and metronomes get front-run." 严肃执行算法 MUST 随机化子单时间和大小——调度应是**期望值平坦的 Poisson 过程**，而非时钟。iotdigitaltwinplm 2026-06 强化："Build unpredictability into slice sizing and timing from day one; retrofitting anti-gaming behavior into a deterministic scheduler is painful." → schema 新增 `anti_gaming` 字段（MVP 阶段 TWAP/VWAP 建议 `timing_randomization: poisson, size_jitter: 0.1-0.2`）。
>
> **② POV 内生性公式**（marketmaker.cc 2026-07）：POV 算法 x_t = γ·V_t 中 V_t 包含自身成交量，实际交易量 x = γ/(1-γ)·M（M=他人成交量）。γ=0.10 时修正温和（11.1%），γ=0.25 时交易他人流的 33%，**γ=0.5 时定点发散**。→ 40 号文档 POV 参与率≤5% 约束（γ/(1-γ) 修正仅 5.3%）的合理性由此验证。schema `params` 中 POV 类 MUST 登记 `max_participation_rate` 且 ≤0.10。
>
> **③ TCA 双报告**（iotdigitaltwinplm 2026-06）：VWAP slippage 和 implementation shortfall 回答不同问题——VWAP slippage 衡量"跟市场均价差多少"（算法表现），IS 衡量"跟决策价差多少"（总成本含延迟+冲击）。"Shipping only the flattering one erodes trust." → schema 新增 `tca_metrics` 字段，MVP 建议 `[vwap_slippage, implementation_shortfall, fill_rate]`，Phase 1.5+ 补 `market_impact`。

#### 6.2.2 risk_limit_registry.yaml（风控限额，REG-RLM-001）

**Schema**：

```yaml
unique_key: [risk_limit_id]
entry_schema:
  risk_limit_id: str             # RLM-{TYPE}-{NNN}
  name: str
  name_zh: str
  limit_type: enum               # position/concentration/drawdown/var/es/leverage/turnover/kill_switch/firm_risk
  scope: enum                    # strategy/sleeve/portfolio/firm
  scope_strategy: str            # v1.2.0新增：scope=strategy 时关联 strategy_id
  threshold_value: float
  threshold_unit: str            # %/元/σ
  inherent_risk: float           # v1.2.0新增：固有风险（控制前），对标 NIST/ISO 31000
  residual_risk: float           # v1.2.0新增：剩余风险（控制后），对标 NISTIR 8286
  consumption_tracking: str
  kri_frequency: str             # v1.2.0新增：KRI 监控频率（daily/weekly/monthly），对标 ISO 31000 监控
  review_cycle: str              # v1.2.0新增：复审周期（quarterly/annually），对标 ISO 31000 季度复审
  breach_action: enum            # warn/skip/fix-in-place/halt（对齐 reconciler 约束，禁止 commit）
  module_id: str
  doc_ref: str                   # 35/36/37号
  code_path: str                 # src/zephyr/risk/
  status: enum
  version: str
  created_at: date
  updated_at: date
  owner: str
  current_consumption: float     # 运行时消耗（可空，未来进 DB）
  # 生命周期阶段 + 响应策略（v1.22.0 新增，对标 Apicurio 3.3.x 四阶段版本状态机 + ISO 31000 response strategy）
  stage: enum                    # active/deprecated/disabled，限额生命周期阶段（对标 Apicurio Creation→Evolution→DEPRECATED→DISABLED）
                                 # active=生效中；deprecated=已警告宽限期内（新策略不应引用，存量继续）；disabled=硬禁用（阻止新依赖，仅存量保留）
                                 # 比 active→deprecated→retired 三态更精细：disabled 允许存量继续但阻止新策略引用即将退役的限额
                                 # MVP 阶段三态足够（stage 默认 active），Phase 1.5+ 限额库扩大后启用 disabled 态
  response_strategy: enum        # mitigate/transfer/avoid/accept，ISO 31000 风险响应策略
                                 # mitigate=降低（加仓限制/减仓）；transfer=转移（对冲/保险）；avoid=规避（禁交易）；accept=接受（监控)
                                 # 与 breach_action（warn/skip/fix-in-place/halt 执行动作）正交：response_strategy=策略层决策，breach_action=执行层动作
                                 # 对标 ISO 31000 Step 4 Treat 的四选项，回答"违约后风险如何处置"而非"执行什么操作"
  # 回撤阈值校准方法（v1.23.0 新增，对标 arXiv:2608.00127v1 2026-07-31 Drawdown Risk Beyond Brownian Motion）
  drawdown_calibration_method: enum  # gaussian/rsb_non_gaussian/fbm_long_memory，回撤阈值校准方法
                                 # gaussian=高斯假设（MVP 默认，保守阈值兜底）
                                 # rsb_non_gaussian=Rej-Seager-Bouchaud 非高斯校准（Phase 1.5+，重尾策略 γ₄>6 MUST 启用）
                                 #   按策略实际偏度/肥尾/波动率聚集生成四维回撤查找表（max_drawdown/max_loss/final_negative_time/longest_recovery_time）
                                 # fbm_long_memory=分数布朗运动长记忆校准（Phase 2+，Hurst H≠0.5 的策略）
                                 # arXiv:2608.00127: 单一高斯表系统性误警，四维度量移动方向不同
                                 # 仅 drawdown 类限额（RLM-DRAWDOWN-001~008）声明
  # VaR 校准方法（v1.23.0 新增，对标 arXiv:2602.03903v3 2026-08-03 Regime-Weighted Conformal Calibration）
  var_calibration_method: enum   # historical/rwc_conformal，VaR 校准方法
                                 # historical=历史模拟法（MVP 默认，固定窗口分位数）
                                 # rwc_conformal=Regime-Weighted Conformal Calibration（Phase 1.5+）
                                 #   指数时间衰减+regime 相似性权重从历史预测误差构建安全缓冲，包裹任意条件分位数预测器
                                 #   压力期自动收紧（违反率偏离名义目标时），模型无关（model-agnostic）
                                 # arXiv:2602.03903: VaR 在压力期系统性误校准，RWC 修复
                                 # 仅 var 类限额（RLM-VAR-001~005）声明
  # 风险贡献结构分解（v1.28.0 新增，对标 arXiv:2604.10375v1 LOO inherent+correlation decomposition）
  risk_contribution_decomposition: obj  # {inherent_component: float,   # 仓位自身波动贡献（独立于组合，恒为正）
                                 #  correlation_component: float, # 与其余组合的协方差（可放大或对冲）
                                 #  decomposition_method: enum(loo/standard_rc/none)}
                                 # LOO 分解区分"自身波动大"vs"组合相关性高"——前者降仓位后者加对冲
                                 # concentration/var 类限额声明；MVP 用 standard_rc，Phase 1.5+ 持仓>20 用 loo
  # 回撤路径依赖疼痛度量（v1.30.0 新增，对标 metricgate 2026-05-20 Ulcer Index + algostrategyanalyzer 2026-01-27）
  pain_metric: obj               # {metric_type: enum(ulcer_index/pain_index/none),  # 疼痛度量类型
                                 #  threshold: float,  # 疼痛阈值（UI>10%/Pain Index>5% 触发响应）
                                 #  monitoring_window_days: int}  # 监控窗口天数（通常 90/180 天）
                                 # 路径依赖度量同时编码深度×持续时间，区分"20%回撤2周恢复"与"20%回撤18个月恢复"
                                 # 前者可忍受后者触发赎回——单一 max_drawdown 把两者等同（v1.30.0 §4.37①）
                                 # 仅 drawdown 类限额声明，MVP 阶段用 none（持仓<10 人工判断 max_drawdown 足够）
                                 # Ulcer Index=drawdown序列二次均值√(ΣD²/N)；Pain Index=drawdown序列算术均值
  # 合规通知登记（v1.31.0 新增，对标证监会法释〔2026〕13号 2026-07-27 + 短线交易监管规定 2026-04-07）
  compliance_notices: list[obj]    # 每项 {regulation: str,           # 监管规定标识（如 法释〔2026〕13号/短线交易规定/程序化交易细则）
                                   #  effective_date: date,         # 施行日期
                                   #  applicability: enum,          # applicable/not_applicable/conditional
                                   #  impact_note: str}             # 对本限额/策略的影响说明
                                   # 登记 A 股合规红线及适用性，§4.20 交易规则/程序化之外的司法解释维度
                                   # 法释〔2026〕13号（内幕交易司法解释 14 年来首次系统性修订）：
                                   #   敏感期前移（初步意向即认定）+ 四类人群入刑减半 + 三大脱罪理由失效
                                   #   event_driven 策略 applicability=conditional（事件窗口划定不得依赖非公开信息）
                                   # 短线交易规定（适用主体 5%+股东/董监高）：个人非大股东 applicability=not_applicable
                                   # 个人量化基于公开数据，不涉内幕；compliance_notices 作合规存档非阻断门禁
```

**9 种限额类型**：position（仓位）/ concentration（集中度）/ drawdown（回撤，含四级 Protocol）/ var（VaR 5级）/ es（期望短缺）/ leverage（杠杆）/ turnover（换手）/ kill_switch（熔断）/ firm_risk（公司级聚合）

**数据来源**：
- [35_drawdown_protocol_impl.md](35_drawdown_protocol_impl.md)（四级回撤 Protocol）
- [36_var_es_monitoring.md](36_var_es_monitoring.md)（VaR/ES 监控）
- [37_liquidity_crisis_protocol.md](37_liquidity_crisis_protocol.md)（流动性危机）
- [32_firm_risk_aggregator.md](32_firm_risk_aggregator.md)（公司级聚合）
- 代码 `src/zephyr/risk/`（v1.1.0 修正：原 v1.0.0 误引 `config/risk_register.yaml`，**该文件是 MOD-INF-001 基础设施容量保障风险登记表 R1-R21**——SQLite 并发/死锁/Schema 漂移/ChromaDB 线程泄漏等运维风险，**非交易风控限额**。两者概念不同：交易风控限额=硬阈值（position/drawdown/var/kill_switch），基础设施风险登记=概率评估（likelihood×impact）。交易风控限额真源在 `src/zephyr/risk/`：risk_limits.py/risk_manager.py/risk_manager_base.py/risk_validator.py/stop_loss.py + core/cross_asset/implementations/services/api/infrastructure 子目录，P1-B 施工时从此处反查 9 类限额实际实现）

> project_memory 约束：reconciler 只能 `warn`/`skip`/`fix-in-place`，禁止 `action="commit"`。本注册表 `breach_action` enum 第四项 `halt` 用于 Kill Switch 场景（非 reconciler 自动执行，而是风控硬熔断人工介入），与 reconciler 约束不冲突。

> 🎯 **2026 NIST/ISO 31000 Risk Register 对标（v1.2.0 新增）**：2026 主流风险登记表核心字段（[NISTIR 8286](https://tysonmartin.com/feeds/blog/risk-register-action-plan) ｜ [ISO 31000:2018](https://riskpublishing.com/what-is-risk-management-process/) ｜ [Risk Companion 2026-03](https://www.risk-companion.com/blog/iso-31000-in-practice-what-does-the-international-standard-actually-deliver/)）：Risk ID/date/description/category/likelihood/impact/priority/status/owner/response strategy/inherent vs residual risk/KRI 频率/复审周期。本 schema 已对标新增 `inherent_risk`/`residual_risk`（NISTIR 8286 核心区分：固有风险=控制前，剩余风险=控制后，成熟登记表追踪两者以判断控制是否有效）/`kri_frequency`/`review_cycle`（ISO 31000 Step 5 Monitor&Review：KRI 仪表盘月度+登记表季度复审+行动追踪月度）。**注意概念边界**：本注册表管"交易风控限额"（硬阈值+breach_action），**不等同于** ISO 31000 全量 Risk Register（后者还含 cyber/operational/compliance 等非交易风险，那些在 `config/risk_register.yaml` MOD-INF-001 基础设施风险登记）。两者互补不合并——交易限额是硬执行层，风险登记是评估层。ISO 31000 五步（Identify→Analyse→Evaluate→Treat→Monitor）中，本注册表聚焦 Treat（硬阈值）+ Monitor（KRI 频率），Identify/Analyse/Evaluate 在 35/36/37 号文档。

> 🔒 **KRI Governance 6 角色分离职责模型（v1.6.0 新增，对标 [risktemplate.com 2026-05-22 KRI Governance](https://risktemplate.com/blog/2026-05-23-kri-governance-ownership-escalation-remediation/)）**：成熟 KRI（Key Risk Indicator）治理要求每条限额有 6 个独立角色分工——Metric Owner（指标归属）/ Data Owner（数据归属）/ Threshold Approver（阈值审批）/ Escalation Recipient（升级接收）/ Action Owner（行动归属）/ Board Reporting Owner（上报归属）。**核心治理原则**（risktemplate 2026-05 OCC 审查案例教训）：① **阈值放宽需更高级别签批**——"loosening a threshold should require sign-off one level higher than the owner who benefits from the change"，禁止受益方自行放宽阈值（案例：18 个月全绿 KRI 仪表盘被 OCC 审查员发现是阈值被持续调宽而非风险可控）；② **持续违约协议**——"KRI amber/red 持续 >2 个报告周期且无 remediation plan → 触发独立审查"（持续违约无管理响应=治理失败非绩效问题）。
>
> **个人项目映射**（避免过度工程）：6 角色对个人+100%AI 项目映射为 **2 主体 4 职能**——Human Owner（人）承担 Threshold Approver + Board Reporting Owner（阈值审批+最终上报），AI Agent 承担 Metric Owner + Data Owner + Escalation Recipient + Action Owner（指标计算+数据采集+告警升级+执行行动）。**关键约束落地**：risk_limit 的 `threshold_value` 变更（尤其放宽）MUST 走 §4.9 EVOLVE_ENTRY 的 schema_sig 变更分类（触发版本快照 + 人工审批），禁止 AI 自行放宽阈值——这通过 `breach_action` enum 约束（warn/skip/fix-in-place/halt 均非"放宽阈值"）+ EVOLVE_ENTRY 人工门禁双重保证。持续违约协议映射：`current_consumption` 超 `threshold_value` 持续 ≥2 个 `kri_frequency` 周期 → §4.12 ADAPT_STRATEGY 升级 + 人工审查（对标 risktemplate "persistent breach without remediation = governance failure"）。schema 无需新增字段（`owner` + `kri_frequency` + `review_cycle` + `breach_action` 已覆盖），v1.6.0 仅补治理流程约束。

#### 6.2.3 data_asset_registry.yaml（数据资产，REG-DATAFLOW-001 改名扩展）

**Schema**（三实体，对标 OpenLineage Source/Dataset/Job）：

```yaml
unique_key:
  sources: [source_id]
  datasets: [dataset_id]
  jobs: [job_id]

sources:                         # 新增段（数据源供应商）
  - source_id: str               # SRC-{PROVIDER}-{NNN}，如 SRC-QMT-001
    provider_name: str           # miniQMT/AkShare/TDX/Wind
    connection_type: str         # api/sdk/file/db
    frequency: str               # tick/1min/day
    sla: str
    cost: str                    # 免费/付费/按量
    compliance: str
    provides_datasets: list[str]
    env_config: str              # 如 config/.env.qmt
    status / created_at / updated_at

datasets:                        # 沿用原 dataflow_graph_registry datasets 段
  - dataset_id: str             # DS-{NAME}-{NNN}
    name / schema / frequency / pit_policy / contract_ref / module_id
    # 回测数据偏差治理（v1.18.0 新增，对标 §4.7 E14 + digitalninjasystems 2026-05-28 + thedatascientist 2026-06-10 + preprints.org 2026-06-04）
    survivorship_free: bool     # 数据源是否含退市证券（true=无生存偏差/false=仅存活/unknown=未知）
                                # 行情类 dataset MUST 声明：AKShare 日线=unknown（仅学术），Norgate/Compustat=true
                                # 生存偏差使 US equity 年化高估 1-3%，小市值/价值策略更严重
    pit_available: bool         # 是否支持 point-in-time 查询（财报按公布日期对齐，防前瞻偏差）
                                # 财报类 dataset MUST 声明：前瞻偏差使 mean-reversion 收益虚增 40-60%
    earnings_lag_days: int      # 财报公布平均滞后天数（用于 PIT 对齐校验，行情类 dataset 可空）
    # LLM 前瞻偏差治理（v1.19.0 新增，对标 §4.7 E15 + Look-Ahead-Bench arXiv:2601.13770 2026-01 + KTD-FIN arXiv:2605.28359 2026）
    llm_training_cutoff: date   # LLM 训练截止日期（如 "2023-04-01"），仅 LLM-relevant dataset 声明
                                # Look-Ahead-Bench 2026-01: 回测期 < 训练截止日期 = 高前瞻偏差风险
                                # CSDN 2026-08-09 §5.2: "用 2023 年 GPT-4 测 2020 年策略=拿着明天报纸买今天彩票"
                                # MVP 未用 LLM 时填 N/A，Phase 2+ 评估 LLM 信号时 MUST 声明
    lookahead_test_method: str  # 前瞻偏差测试方法：none/lookahead_bench/ktd_fin_4level
                                # KTD-FIN 2026 4-level masking: bright/stock-blind/date-blind/blinded
                                # 最强攻击者 top-5 ticker 恢复率仅 10.2%，blinded 条件有效缓解泄漏
                                # MVP 未用 LLM 时填 N/A，Phase 2+ MUST 至少跑 blinded 级
    # 标签延迟分层监控（v1.26.0 新增，对标 §4.33② Evidently+NannyML 标签延迟分层 + v1.21.0第十轮遗留落地）
    label_delay_days: int       # 标签可用延迟天数（财报/收益/事件类 dataset 声明，行情类可空）
                                # 标签延迟=ground truth 到达时间滞后，NannyML CBPE 估计须按延迟分层
                                # NannyML 2025: 无标签时用 CBPE（Confidence-Based Performance Estimation）估计性能
                                # 延迟>30 天的标签 MUST 分层监控（短期/中期/长期三档），否则 CBPE 估计偏倚
                                # A 股财报: 季报45天/年报4个月/业绩预告7-15天，label_delay_days 按实际填写
    drift_detector: str         # 漂移检测器：none/evidently/nannyml/alibi_detect
                                # evidently: 开源 PSI/KS/Wasserstein/Chi-Squared，100+ 内置指标，HTML 报告
                                # nannyml: CBPE 无标签性能估计 + PCA 多变量漂移重建误差 + concept drift 检测
                                # alibi_detect: 高级漂移算法（MMD/LSDD/LearnedKernel），适合研究场景
                                # MVP 填 none（日线策略无在线漂移监控），Phase 1.5+ 实盘后 MUST 启用 evidently
    produced_by_source: str     # 关联 sources
    produced_by_jobs: list[str]
    consumed_by_jobs: list[str]
    status / created_at / updated_at

jobs:                            # 沿用原 jobs 段
  - job_id: str                 # JOB-{NAME}-{NNN}
    name / schedule / consumes / produces / module_id / code_path
    status / created_at / updated_at
```

**改名裁定**（裁定 2 + S6）：
- 文件名改：`dataflow_graph_registry.yaml` → `data_asset_registry.yaml`
- title 改：数据流图注册表 → 数据资产登记表
- **registry_id 保留**：REG-DATAFLOW-001（稳定标识符不改，全项目引用不断）
- **module_id 保留**：原蓝图号不变
- 改名登记走 [ruling_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/ruling_registry.yaml)（migration_registry 已 frozen）

> ⚠️ **v1.1.0 审计发现（裁定 S6 未落实）**：S6 裁定要求"改名登记走 ruling_registry.yaml"，但 `Select-String ruling_registry.yaml "data_asset|dataflow_graph|REG-DATAFLOW"` **无任何输出**——改名裁定尚未在 ruling_registry 登记！这是 P1-B 施工前必须补齐的硬缺口（已加入 §9.4 验收清单 + §12 待定问题 D1）。

**数据来源**：
- 原 [dataflow_graph_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml)（v1.1.1 修正：实际含 **DS-001~DS-076 共 76 条** datasets + jobs，原 v1.0.0 写"DS-001~029"严重少算；v1.1.0 初估"030+"仍少算，v1.1.1 全量 grep 确认 76 条）
- [15_data_feature_layer_spec.md](15_data_feature_layer_spec.md)（数据源/PIT/质量）
- config/.env.qmt（miniQMT 连接，已验证存在）

**2026 OpenLineage 对标说明**：三实体（sources/datasets/jobs）设计对齐 OpenLineage 2026 主流模型（Source/Dataset/Job + RunEvent + Facets，[OpenLineage as the Spine of Data Observability 2026-05](https://datalakehousehub.com/blog/2026-05-openlineage-observability/)）。个人项目 **不需要** RunEvent（运行时事件流）和 column-level lineage（字段级血缘，2026 前沿）——这些是企业级数据平台需求，个人量化系统三实体足够。详见 §8 过度工程审查。

#### 6.2.4 chart_pattern_registry.yaml（图形形态，REG-PAT-001）

**Schema**：

```yaml
unique_key: [pattern_id]
entry_schema:
  pattern_id: str                # PAT-{CLASS}-{NNN}，如 PAT-CHANLUN-001
  name: str
  name_zh: str
  aliases: list[str]
  pattern_class: enum            # 8 大类（见下）
  pattern_subtype: str           # 子类（反转/持续、单根/两根/三根、推动浪/调整浪）
  recognition_algorithm: str     # 识别算法（因算法不唯一，MUST记录用哪种）
                                 # rule_based / template_match / fractal / regression / dl_cnn / dl_transformer / dl_yolo
  algorithm_variant: str         # 峰谷法/回归法/模板匹配法/分形法/规则法
                                 # v1.2.0新增 DL 变体：yolov8/vit-tiny/resnet/cnn_talib_hybrid
                                 # v1.7.0新增 DL 变体：cnn_lstm_hybrid（CNN空间特征+LSTM时序记忆，mental-momentum 2026-06 验证一致优于独立模型）
  dl_model_ref: str              # v1.2.0新增：DL 模型引用（如 huggingface:foduucom/stockmarket-pattern-detection-yolov8）
  dl_training_dataset: str       # v1.2.0新增：训练数据集来源（合成参数化/真实标注）
  params: obj                    # {lookback: 20, threshold: 0.03}
  inputs: list[str]              # OHLCV/分时数据/K线图像
  outputs: obj                   # {present: bool, start_pos: int, end_pos: int, confidence: float}
  subjectivity: enum             # high/medium/low
  timeframe: enum                # intraday/daily/weekly
  module_id: str
  doc_ref: str
  code_path: str
  used_by_factors: list[str]     # 反向关联 factor_id
  variant_of: str                # 可选：形态变体
  status: enum
  version: str
  created_at: date
  updated_at: date
  owner: str
  # 性能（可空）
  hit_rate: float
  false_positive_rate: float
  last_evaluated_at: date
```

**pattern_class 8 大类**（覆盖图形技术分析全谱系）：

| # | 类别 | 内容 | 主观性 |
|---|---|---|---|
| 1 | candlestick_pattern | 蜡烛图/K线组合（TA-Lib 61种：单根/两根/三根/多根，锤子线/吞没/晨星等） | low |
| 2 | chart_pattern | 经典图表形态（Edwards&Magee：W底/M头/头肩顶底/旗形/三角形/楔形/杯柄形等） | medium |
| 3 | chanlun | 缠论（分型→笔→线段→中枢→走势，顶底分型/一二三买卖点/背驰） | medium |
| 4 | elliott_wave | 波浪理论（推动浪1-5/调整浪abc/延长/锯齿形/平台形/三角形） | **high** |
| 5 | trendline_channel | 趋势线与通道（上升下降水平趋势线/通道/颈线） | low |
| 6 | support_resistance | 支撑阻力位与缺口（阻力位/支撑位/关键价位/突破测量衰竭普通缺口） | low |
| 7 | fibonacci | 斐波那契工具（回测位23.6-78.6%/扩展位/扇形/弧形/时间区间） | low |
| 8 | structure | 价格结构（箱体矩形震荡/平台盘整/密集成交区） | medium |

**设计要点**：
- `recognition_algorithm` + `algorithm_variant` 双字段：图形形态算法不唯一（W底有峰谷法/回归法/模板匹配法），MUST 记录用哪种——这是与技术指标库最大 schema 差异
- `outputs` 是 obj 不是 list[str]：形态输出是事件结构（存在/位置/置信度），非数值列
- `subjectivity` 字段：诚实标注主观性，波浪=high 标 experimental，分型=low 可 active
- 关系链：chart_pattern_registry（识别算法）→ factor_registry（形态因子）→ strategy_registry，与 technical_indicator_registry → factor_registry → strategy_registry 完全对称
- 对标 TA-Lib CDLPATTERN（61种K线形态）+ 缠论体系 + 艾略特波浪 + Edwards&Magee

> 🎯 **2026 图形识别 DL 算法对标（v1.2.0 新增）**：2026 年图形形态识别出现 3 类 DL 算法，作为本注册表 `recognition_algorithm` 的 `dl_*` 选项 + `algorithm_variant` 的 DL 变体（MVP 不实施，schema 预留）：
> - **YOLOv8 目标检测**（[Trader Koo 2026-03](https://kooexperience.com/blog/posts/trader-koo.html) ｜ [daily_stock_analysis 2026-02-08](https://blog.csdn.net/weixin_42589700/article/details/157848000)）：将 K 线图作图像输入，YOLOv8 框出形态区域+置信度。**准确率 92.6%** vs 规则引擎 68.3% vs 纯 CNN 74.1%。HuggingFace 预训练模型 [`foduucom/stockmarket-pattern-detection-yolov8`](https://huggingface.co/foduucom/stockmarket-pattern-detection-yolov8) 识别 6 类（头肩顶/底、双顶/底、上升/下降通道）。daily_stock_analysis 用参数化合成数据集训练 32 种经典形态，能检测"失败形态"（如右肩量能不足的头肩顶）。`algorithm_variant: yolov8`，`dl_model_ref: huggingface:foduucom/...`。
> - **ViT-Tiny 视觉 Transformer**（[CS231n Stanford](https://cs231n.stanford.edu/2025/papers/text_file_840597081-LaTeXAuthor_Guidelines_for_CVPR_Proceedings__1_-2.pdf)）：将 K 线图切 patch + self-attention 捕获全局依赖。50K 张 224×224 K 线快照（5min K线 × 30 根 = 2.5 小时），多分类预测价格变动 + SSL+MAE 自监督聚类回测。ViT 优于 CNN（Kusuma 2020），`algorithm_variant: vit-tiny`。
> - **CNN+TA-Lib 混合**（2025 发表 2026 持续引用）：规则层（TA-Lib 61 形态）+ 深度学习层联合，预测准确率 99.3%。`algorithm_variant: cnn_talib_hybrid`，结合规则可解释性与 DL 表达力。
>
> **个人项目适用性评估**：DL 图形识别需大量标注数据 + GPU 训练 + 模型部署，对个人项目属过度工程（MVP 阶段）。MVP 用 `rule_based`/`template_match` 算法（TA-Lib CDLPATTERN 61 种 K 线形态 + 经典图表规则法）。但 schema 预留 `dl_model_ref`/`dl_training_dataset`/DL `algorithm_variant` 字段，Phase 2+ 可评估 YOLOv8 预训练模型（HuggingFace 即取即用，免训练）作为形态识别增强。`subjectivity` 字段在 DL 场景标 low（算法客观，但训练数据偏差仍存）。

> 🧠 **"Simplicity Wins" 原则 + CNN+LSTM Hybrid + 反 Look-Ahead Bias（v1.7.0 新增，对标 [arXiv:2605.00875 Haggett 2026-04](https://arxiv.org/pdf/2605.00875.pdf) + [mental-momentum 2026-06-14](https://research.mental-momentum.ai/r/convolutional-neural-networks-chart-lbrhyr)）**：
>
> **① Simplicity Wins**（arXiv:2605.00875，Stevens Institute 8 组控制实验，BTC/ETH/S&P500 2018-2024）：**原始 K 线图 + 4 层基础 CNN AUC-ROC 0.892**，outperform 复杂编码（Gramian Angular Field）和大型预训练模型（ResNet18/EfficientNet-B0/ViT）。三个反直觉发现：① price-only 图表 > 含指标图表（指标是噪声非信号）；② 128×128 分辨率 > 224×224（金融图表信息密度低，低分辨率防过拟合）；③ ImageNet 迁移学习提升 4-16%（尽管领域差异）。GradCAM 可解释性分析确认 CNN 关注支撑阻力位和局部波动聚类。→ **Phase 2+ DL 起点应是 `dl_cnn` + 原始 K 线图 + 128×128，而非 YOLOv8/ViT**——复杂模型在金融图表上不如简单 CNN。
>
> **② CNN+LSTM Hybrid**（mental-momentum 2026-06）：**Hybrid 架构（CNN 空间特征提取 + LSTM 时序记忆）一致优于独立模型**——CNN 捕获 K 线几何形态（空间），LSTM 捕获跨 K 线趋势演化（时序），两者互补。raw pixel 输入 > 显式人工技术指标输入（让网络自主发现模式，避免人类归纳偏置）。→ schema 新增 `algorithm_variant: cnn_lstm_hybrid`，Phase 2+ 优先于此变体而非独立 CNN 或 LSTM。
>
> **③ 反 Look-Ahead Bias**（mental-momentum 2026-06，**关键实现约束**）：图像生成 MUST 使用**严格后向归一化**（backward-looking normalization）——"never scales using future prediction data"。即归一化窗口只含历史数据，禁止用全样本 min/max 或未来均值标准化。这是 DL 图形识别最隐蔽的过拟合来源——若归一化用了未来数据，模型"预测"只是记忆未来。→ `dl_training_dataset` 字段 MUST 记录归一化策略（`backward_only` / `expanding_window` / `rolling_window`），禁止 `global_minmax`（含未来数据）。

**MVP 范围控制**：图形形态几十种，P1 不一次性建全。先从代码反查项目实际用到的形态（`src/zephyr/factor/technical_indicators/` + `src/zephyr/signal_ashare/` 打板链），只登记实际用到或明确规划的。符合"过度工程纠偏"原则——建库结构完整，内容按需填充。MVP 算法用 rule_based/template_match（O6 裁剪：先做 candlestick_pattern + chart_pattern 2 类），DL 算法 schema 预留不实施。

## 7. P2 待施工两注册表

### 7.1 field_dictionary.yaml（字段字典，REG-FLD-001）

**Schema**：

```yaml
unique_key: [field_id]
entry_schema:
  field_id: str                  # FLD-{DOMAIN}-{NNN}
  field_name: str                # 如 close
  name_zh: str                   # 如 收盘价
  business_definition: str
  data_type: str                 # int/float/str/datetime/bool
  unit: str                      # 元/股/%
  allowed_values: list[str]
  source_system: str             # 关联 data_asset_registry source_id
  adjust_method: str             # 前复权/后复权/不复权
  pit_property: str              # point_in_time/look_ahead_risk
  quality_rules: list[str]
  steward: str
  status / version / created_at / updated_at
```

**范围裁定**（裁定 8）：仅管数据层字段（行情/因子/特征/输出的 type/unit/source/复权口径/PIT/quality_rules），**不合并** frontmatter_field_registry.yaml（文档元数据，职责分离）。对标 DAMA-DMBOK / dbt schema.yml。

**2026 dbt schema.yml 对标补充**（v1.1.0 新增）：2026 主流 data dictionary 核心字段 = field_name/type/definition/source/owner/allowed_values/sensitivity/freshness/notes（[Basedash 2026-06](https://www.basedash.com/blog/what-is-a-data-dictionary-and-how-to-build-one-for-analytics) ｜ [OvalEdge 2026-02](https://www.ovaledge.com/blog/data-dictionary-best-practices)）。当前 schema 缺 `sensitivity`（PII/敏感字段标记）、`freshness`（更新频率）、`notes`（caveats/gotchas）。dbt 命名规范建议补入施工要点：snake_case + business terminology + `<object>_id` PK + `is_`/`has_` boolean 前缀 + `_at` UTC timestamp + `_date` date + `_v1` versioning（[dbt style guide 2026-08](https://docs.getdbt.com/best-practices/how-we-style/1-how-we-style-our-dbt-models)）。P2 施工时补 sensitivity/freshness/notes 三字段。

### 7.2 experiment_registry.yaml（实验/回测目录，REG-EXP-001）

**Schema**：

```yaml
unique_key: [experiment_id]
entry_schema:
  experiment_id: str             # EXP-{TYPE}-{NNN}，如 EXP-BACKTEST-001
  name: str
  name_zh: str
  experiment_type: enum          # backtest/factor_eval/strategy_eval/param_search/walk_forward/regime_validation
  target_type: enum              # factor/strategy/indicator/pattern/risk_rule/execution_algo
  target_id: str                 # 被测对象 id
  params_summary: obj
  data_period: str
  universe: str
  benchmark_id: str              # v1.2.0新增：回测基准（benchmark_id），计算超额收益
  cost_model_ref: str            # v1.2.0新增：回测成本模型（cost_model_id），MUST 指定扣成本
  result_summary: obj            # {sharpe, max_dd, ic}
  conclusion: str
  # 回测过拟合检测（v1.3.0 新增，对标 2026-07 backtest-guard + Soloviov PBO 论文）
  is_overfit: bool               # 综合判定（PBO>0.2 或 DSR p-value<0.05 → True）
  pbo_value: float               # Probability of Backtest Overfitting（CSCV 估计，null=0.5，<0.1 可信，>0.2 红旗）
  dsr_value: float               # Deflated Sharpe Ratio（校正多重检验后 Sharpe，>1.0 显著）
  psr_value: float               # Probabilistic Sharpe Ratio（原始 Sharpe 显著性概率，v1.6.0修正：AUC 0.81 最强单一诊断，非仅"DSR前身"）
  n_trials: int                  # 参数搜索试验数（DSR/PBO 计算必需，含相关试验用有效独立数 N_eff）
  min_trl_years: float           # v1.11.0新增：Minimum Track Record Length（最小可信样本长度，年），Bailey&López de Prado 2014
                                 # 公式 MBL = 0.5×(Z_α×σ_ann/SR_ann)²，回答"需多少年数据才能信任此 Sharpe"
                                 # 对标 backtestbase 2026-01 + auditzk 2026-03 + digitalninjasystems 2026-06 + quantskills/skill-backtest-overfit 2026-07
                                 # 经验值：SR=0.5→25-40+年（不实用），SR=1.0→5-10年，SR=1.5→3-5年，SR=2.0→1.5-3年
                                 # SE(SR)≈1/√T，T=250（1年）时 SE≈0.063；自相关膨胀 SE 1.5-3x（Lo 2002）
                                 # 实盘 track record < min_trl_years → Sharpe 不足以排除噪声，MUST 继续 probation 而非确认
  plateau_score: float           # v1.6.0新增：参数稳健性高原分数（Soloviov robustness score，standalone弱但与PSR组合增强fragile mode检测，选择原则非独立检测）
  adversarial_result: obj        # v1.6.0新增：对抗验证结果（honest-backtest Layer 7，{test_name, passed, kill_reason}列表，AI主动证伪场景）
  # 有效 trial 数鲁棒性带（v1.21.0 新增，对标 Soloviov 2026-07 "How Many Backtest Winners Survive Deflation?"）
  trial_correlated: bool         # trial 间是否有相关性（参数网格/同源变体=True，独立策略=False）
                                 # Soloviov: 相关搜索场景裸 DSR 错误拒绝真实 edge（真实 Sharpe 3.92 被判 0.748<0.95）
                                 # trial_correlated=True 时 MUST 跑 bootstrap_test_passed，裸 dsr_value 不可信
  effective_trial_count_band: obj # 有效 trial 数鲁棒性带（≥5 估计器区间，非单值）
                                 # {estimators: {laplace: float, jaw: float, ar1: float, spectral: float, permutation: float},
                                 #  robust_range: [min, max], verdict: "robust"/"fragile"}
                                 # Soloviov: 5 个标准估计器在同 trial 矩阵上相差两个数量级（1.6 到 370），单值不可信
                                 # deflated benchmark SR₀≈1.63（年化）=噪声天花板，策略 MUST 跨越此线
                                 # §4.13 G2 门禁检查此字段（n_trials>10 时 warning 级要求）
  bootstrap_test_passed: bool    # White Reality Check / Hansen SPA 联合重采样结果（trial_correlated=True 时 MUST）
                                 # bootstrap 绕开 trial count 选择问题，对整个搜索联合重采样
                                 # §4.13 G2 门禁：trial_correlated=True 且 bootstrap_test_passed=None=阻断
  log_location: str              # 日志详情位置（db:// 或 /logs/xxx.json）
  artifact_path: str
  mlflow_run_id: str             # v1.2.0新增：MLflow run 关联（若保留 MLflow，见 E1）
  mace_env_ref: str              # v1.2.0新增：可选，MACE RL 环境引用（execution_algo 实验）
  status: enum                   # running/completed/failed/archived
  created_at: date
  completed_at: date
  owner: str
  parent_experiment_id: str      # 迭代链
  tags: list[str]
  # 回测数据偏差治理（v1.18.0 新增，对标 §4.7 E14 + preprints.org 2026-06-04 三分类偏差 taxonomy）
  backtest_bias_checks: obj      # {survivorship: passed/failed/unknown, lookahead: ..., stop_exit: ...}
                                 # 回测 MUST 声明三类偏差评估结果，未声明=未做偏差治理（E14 告警）
                                 # MVP 用 AKShare 日线=unknown（仅学术），实盘前须升级商业源评估
                                 # 生存偏差使 US equity 年化高估 1-3%，前瞻偏差使 mean-reversion 虚增 40-60%
  # 归因分析（v1.18.0 新增，对标 breakingalpha 2026-01-26 + skill4agent 2026-02-20 + pa package 2026-04-25 + marketopia 2026-05-04）
  attribution_result: obj        # {method: brinson/factor_based/none,
                                 #  allocation_effect, selection_effect, interaction_effect,  # Brinson-Fachler 三效应
                                 #  factor_contributions: {factor_id: contribution}, alpha}     # factor-based 归因
                                 # 归因执行逻辑见 54 号 performance_attribution_report，本字段仅登记结果（§4.4 跨文档职责边界）
                                 # Brinson-Fachler: R_p-R_b = ΣA_i(allocation)+ΣS_i(selection)+ΣI_i(interaction)
                                 # factor-based: R_p = Σβ_k×F_k + α（FF3/Carhart4/FF5，PROMOTE_ENTRY G6 benchmark_id 用途）
                                 # VIF screening 建议（v1.19.0 新增，对标 KTD-FIN arXiv:2605.28359 2026）：
                                 #   factor-based 归因时 MUST 对因子做 VIF（Variance Inflation Factor）筛选
                                 #   KTD-FIN 用 9 个 VIF-screened style factors（momentum/volatility/illiquidity/skewness等）
                                 #   减少 multicollinearity——直接用 FF3/Carhart4 因子可能因共线性使 alpha 估计失真
                                 #   实现：statsmodels.stats.outliers_influence.variance_inflation_factor（<50行）
                                 #   VIF>10 移除该因子或合并为正交因子，VIF<5 安全保留
  # LLM 前瞻偏差治理（v1.19.0 新增，对标 §4.7 E15 + Look-Ahead-Bench arXiv:2601.13770 2026-01 + KTD-FIN arXiv:2605.28359 2026）
  llm_lookahead_check_result: obj # {applicable: bool, reason: str,
                                  #  masking_level: bright/stock-blind/date-blind/blinded,
                                  #  alpha_decay: float,  # 跨 regime alpha 衰减，>0.3 = 严重记忆泄漏
                                  #  test_method: lookahead_bench/ktd_fin_4level/none}
                                  # 仅 LLM-driven 回测实验声明，非 LLM 实验 applicable=false 跳过
                                  # Look-Ahead-Bench 2026: 标准 LLM 显著前瞻偏差，Pitinf 模型随规模增大泛化提升
                                  # KTD-FIN 2026: blinded 级最强脱敏，10-attacker 探针 top-5 恢复率仅 10.2%
                                  # MVP 未用 LLM 时填 {applicable: false, reason: "MVP未使用LLM直接生成信号"}
  # LLM 前瞻污染检测（v1.22.0 新增，对标 §4.7 E18 + LAP arXiv:2512.23847v2 2026-06-12 + FinCAD arXiv:2605.24564 + MemGuard-Alpha arXiv:2603.26797）
  lap_check_result: obj          # Lookahead Propensity 检查结果，仅 LLM-driven 回测实验声明
                                 # {applicable: bool,           # 是否 LLM-driven（非 LLM 实验 false 跳过）
                                 #  lap_value: float,           # LAP=P(up)+P(down)，训练期内显著正、cutoff 后坍塌近零
                                 #  interaction_beta3: float,   # 污染检验回归 Y_{t+1}=β₁μ̂_t+β₂LAP+β₃(LAP×μ̂_t) 的 β₃，>0=前瞻污染
                                 #  contamination: bool,        # β₃>0 即前瞻偏差污染指征
                                 #  suppression_method: str}    # none/fincad_logit_subtraction/cmmd_cross_model_filter（Phase 1.5+ 抑制方法）
                                 # LAP (CUHK 2026-06): "日期-only 召回查询"诊断模型记忆，不修改数据
                                 # E15 (KTD-FIN masking) 是数据侧防御，E18 (LAP) 是模型侧诊断——双轨互补
                                 # FinCAD: 推理时 Context-Aware Decoding 改编，logit 层减去记忆激活 prior（Phase 1.5+）
                                 # CMMD: 多 LLM 训练 cutoff 差异分离记忆 vs 推理信号，Sharpe 4.11 vs 2.76（Phase 1.5+）
                                 # §4.7 E18 审计检查此字段（warning 级，MVP 不阻断）
  # 预注册协议（v1.25.0 新增，对标 AurumQ-RL MASTER-lite 预注册协议 + §4.13 G1 成本否决+IC-OOS 脱钩告警）
  pre_registered: bool           # 是否预注册（实验前声明假设/指标/样本量/止损规则，防事后合理化）
                                 # AurumQ-RL 2026-07-17 MASTER-lite 协议三要素：成本否决+3窗3seed+模型层修正
                                 # 预注册是流程约束非算法——MVP 阶段所有回测 MUST pre_registered=true（git commit 时间戳为证）
  cost_vetoed: bool              # 成本否决结果（含真实滑点/佣金/冲击成本的 OOS 收益≤0=否决=True）
                                 # §4.13 G1 门禁：bt.oos_return_after_cost <= 0 = 阻断
                                 # A 股成本：万5 印花税（卖单边）+ 万0.1 过户费（双边）+ 万3 佣金 + 滑点
  ic_oos_gap: float              # IC 与 OOS 收益相关性脱钩度（<0.3=脱钩告警，IC 虚高但 OOS 亏损）
                                 # §4.13 G1 门禁：bt.ic_oos_correlation < 0.3 = warning（不阻断但告警）
                                 # R&D-Agent-Quant NeurIPS 2025: IC 优化与实盘收益脱钩是已知缺陷
  # 上线裁决三值结果（v1.28.0 新增，对标 §4.13 PROMOTE_ENTRY 三值裁决 + arXiv:2607.20093 Joint Falsification）
  viability_verdict: enum        # supported/refuted/inconclusive，上线裁决三值结果
                                 # supported=CI 下界>materiality 阈值，全门通过，PROMOTE_ENTRY 全量上线
                                 # refuted=CI 上界<materiality 阈值，样本充分但统计门失败，走 RETIRE_ENTRY 放弃
                                 # inconclusive=CI 跨越阈值，样本不足无法裁决，继续 Shadow/Canary 积累数据
                                 # ⚠️ Joint Falsification 核心洞察（arXiv:2607.20093）：
                                 #   "统计不显著"≠"证伪"——二元 pass/fail 把"样本不足"误判为"真无 edge"
                                 #   INCONCLUSIVE 应继续积累数据而非放弃（避免过早弃真）
                                 #   REFUTED 应放弃而非反复重申（避免资源浪费在死策略上）
                                 # MVP 阶段 OOS<MinBTL 时填 inconclusive（诚实记录样本不足）
                                 # Phase 1.5+ MinBTL 达标后才能 supported/refuted
                                 # §4.13 门禁裁决逻辑据此字段分类返回 PROMOTE_SUCCESS/REFUTED/INCONCLUSIVE
  # 过拟合实证模式分类（v1.28.0 新增，对标 §4.13 G2 PF ratio 增强 + dibi8 2026-05-25 Backtest OVERFIT 5 patterns）
  overfit_pattern: enum          # none/walk_forward_divergence/regime_flip/parameter_cliff/indicator_stacking/survivorship
                                 # 检测到的过拟合模式分类（G2 统计方法回答"是否过拟合"，此字段回答"哪种过拟合"）
                                 # none=未检测到过拟合；walk_forward_divergence=IS 优化但 OOS 变差（PF ratio>1.5）
                                 # regime_flip=某 regime 有效另一 regime 失效（需 regime gating）
                                 # parameter_cliff=参数微偏性能骤降（需取高原参数）；indicator_stacking=堆叠相关指标（需去相关）
                                 # survivorship=仅存活标的回测（需 PIT universe）
                                 # 不同模式修复策略不同——dibi8 2026-05: 模式分类指导"怎么修"而非仅"是否过拟合"
                                 # MVP 阶段 PF ratio 自动可算→填 none/walk_forward_divergence，Phase 1.5+ 配合 PBO/DSR 精细分类
  # 路径依赖回撤度量（v1.30.0 新增，对标 Ulcer Index/Calmar Martin 1989 + metricgate 2026-05 + algostrategyanalyzer 2026-01）
  ulcer_index: float               # drawdown 序列二次均值 √(ΣD²/N)，编码"深度×持续时间"
                                   # 0-2% 极低 / 2-5% 中等 / 5-10% 升高 / >10% 深度或持续
                                   # 区分"20% 回撤 2 周恢复"（UI≈2%）vs"20% 回撤 18 个月恢复"（UI≈10%）
                                   # 前者可忍受后者触发赎回——单一 max_drawdown 把两者等同（v1.30.0 §4.37①）
                                   # MVP 阶段自动可算（pandas cummax + 二次均值 <10 行），是 max_drawdown 天然补充
  calmar_ratio: float              # 年化收益 / |max_drawdown|，drawdown 版 Sharpe（Sharpe 用波动率，Calmar 用回撤）
                                   # >1.0 可接受 / >3.0 优秀，PROMOTE_ENTRY G1 回测验证补充信号
                                   # 因基于已实现回撤比 Sharpe 更稳健（Sharpe 从回测到实盘降 30-50%）
  # LLM 时序泄漏测量（v1.31.0 新增，对标 arXiv:2608.02985v1 2026-08-04 Zeyu Zhang + arXiv:2602.17234v2 Shapley-DCLR）
  temporal_leakage_measurement: obj  # {method: enum,               # matched_control/boundary_detection/none
                                     #  leakage_score: float,      # leakage-adjusted 后的分数差（0=无泄漏，>0=有泄漏剂量）
                                     #  reference_model: str}      # 作为 clean control 的参考模型标识（matched_control 时必填）
                                     # 从"检测"到"测量"：E15(Look-Ahead-Bench)+E18(LAP) 回答"是否泄漏"，此字段回答"泄漏多少"
                                     # arXiv:2608.02985 证明标准 pre/post-cutoff 检查 uninformative——recency 模仿 leakage
                                     # 被动回测数学不可分离两者，需 matched clean control（全局测量+调整分数）提供 defensible reference
                                     # matched_control=matched clean control 全局测量+leakage-adjusted score（推荐）
                                     # boundary_detection=known cutoff 边界定位（局部）
                                     # none=未检测（MVP 默认，无 LLM-driven 回测时填此项）
                                     # §4.7 E18 审计检查扩展（v1.31.0）：E18 扩展为"LAP+Temporal Leakage 检测"，warning 级 MVP 不阻断
                                     # Phase 3+ 评估 Shapley-DCLR claim-level 归因 + TimeSPEC 推理时抑制（arXiv:2602.17234v2）
  # 参数稳定性区域（v1.32.0 新增，对标 AlgoXpert IS-WFA-OOS Protocol arXiv:2603.09219v1）
  parameter_stability_region: obj    # {plateau_identified: bool,   # 是否找到稳定高原（参数空间中性能平坦区域）
                                     #  cliff_detected: bool,       # 是否检测到悬崖（小扰动导致性能崩溃=过拟合信号）
                                     #  stability_score: float,     # 参数扰动下性能变异系数的倒数（越高越稳定）
                                     #  selection_method: enum}     # single_optimum/stability_plateau
                                     # 选高原不选尖峰——AlgoXpert 证明应优先稳定高原（plateau）而非悬崖尖峰（cliff）
                                     # cliff_detected=true=warning highlight（参数悬崖=过拟合信号）
                                     # §4.13 G2 审计检查扩展（v1.32.0）：cliff_detected=true 或 paper/live 阶段 single_optimum=warning
                                     # MVP 阶段填 {selection_method: single_optimum}（参数少），Phase 1.5+ 参数搜索 MUST 启用 stability_plateau
```

**设计要点**：
- 两层分离：注册表只管元信息（静态目录），日志详情（逐笔/时序）进 DB/文件
- `log_location` 指向详情，注册表是"目录"
- `parent_experiment_id` 支持迭代链（参数优化 A→B→C）
- 对标 MLflow Experiment Registry / Comet.ml
- **施工时机**：等 [51_panel_experiment_history_mlflow_retirement.md](51_panel_experiment_history_mlflow_retirement.md) MLflow 退役方案落定后施工，避免返工

> 🎯 **2026 回测过拟合检测六方法（v1.3.0 新增三方法，v1.11.0 补 MinBTL 升级四方法，v1.12.0 补 Multiple Testing Correction 升级五方法，v1.16.0 补 CPCV 升级六方法）**：2026 年回测过拟合检测已形成 **PBO + DSR + PSR + MinBTL + Multiple Testing Correction + CPCV** 六方法共识，[backtest-guard](https://github.com/AgentJDrew/backtest-guard)（2026-07-07 开源库）集大成实现 DSR/PSR/PBO/PurgedKFold，[quantskills/skill-backtest-overfit](https://github.com/quantskills/skill-backtest-overfit)（2026-07-03 开源库）显式将 **MinTRL** 与 DSR/PBO/haircut 并列为第 4 指标，[Soloviov 2026-07 论文](https://pbo.marketmaker.cc/paper.pdf) 系统校准 PBO 的 null=0.5 参考值（非0），[stockalpha 2026-02](https://stockalpha.ai/alpha-learning/backtest-reality-checks-deflated-sharpe-pbo-and-multiple-testing-control) 给出实战阈值。v1.12.0 补 [studentone.tech 2026-06-04 九道门级联框架](https://dashboard.studentone.tech/blog/out-of-sample-tests-counter-overfitting-menu)（9 OOS 门控含 Romano-Wolf/BH-FDR/MC Block-Bootstrap/Cluster Stability）+ [metricgate 2026-06-10 Model Confidence Set](https://metricgate.com/docs/model-confidence-set-forecast/)（Hansen-Lunde-Nason 2011，返回"统计不可区分的最佳模型集合"而非单一赢家）+ [marketmaker.cc 2026-06-29 DSR 多重检验对比](https://marketmaker.cc/de/blog/post/deflated-sharpe-multiple-testing/)（受控实验测各方法误报率：朴素测试 100% 误报 vs DSR 0.1% vs White's RC 2.2%）+ [arXiv:2604.15531 Falsification Audit 2026-04-16](https://arxiv.org/pdf/2604.15531v1)（审计研究流程本身而非结果，在合成零预测环境中测试完整工作流）。**v1.16.0 补 CPCV**（[noonbarbari 2026-07-04](https://noonbarbari.xyz/de/blog/cpcv-combinatorial-purged-cv) + [tradingstrategy.ai](https://tradingstrategy.ai/docslearn/backtesting.html) + [arXiv:2603.09219 AlgoXpert 2026-03](https://arxiv.org/pdf/2603.09219v1)）：Combinatorial Purged Cross-Validation（López de Prado 核心方法），生成 C(N,k) 条 OOS equity curve **分布**而非 walk-forward 单条曲线——5 年日数据 + 45 个策略变体几乎必然找到假赢家（t-stat 需接近 3.0 而非 1.96 才能声称真实 edge）。
>
> | 方法 | 全称 | 回答的问题 | null 值 | 红旗阈值 | 个人项目适用性 |
> |---|---|---|---|---|---|
> | **PBO** | Probability of Backtest Overfitting | 选择过程本身是否泛化？（CSCV 对称交叉验证） | **0.5**（非0！纯噪声=in-sample 冠军落在 OOS 中位数一半时间） | **> 0.2** 红旗，< 0.1 可信 | ✅ 参数搜索实验 MUST |
> | **DSR** | Deflated Sharpe Ratio | 校正 N 次试验选择偏差后，Sharpe 是否仍显著？ | 取决于 N_eff | p-value < 0.05 红旗 | ✅ 所有回测 MUST |
> | **PSR** | Probabilistic Sharpe Ratio | 原始 Sharpe 相比基准的显著性概率（DSR 前身） | 0.5 | < 0.95 不显著 | ✅ DSR 输入 |
> | **MinBTL/MinTRL**（v1.11.0 新增） | Minimum Backtest/Track Record Length | **需多少年数据才能信任此 Sharpe？**（样本量充分性） | — | 实盘 track < MinBTL → 不足以排除噪声 | ✅ 所有回测 MUST（Bailey & López de Prado 2014） |
> | **MTC**（v1.12.0 新增） | Multiple Testing Correction（White's RC / Hansen SPA / Romano-Wolf / MCS / BH-FDR） | **N 个策略同时检验时，哪些在族错误率控制下仍显著？** | 取决于方法 | 修正后 p > 0.05 红旗 | ✅ 多策略筛选 MUST（Phase 1.5+） |
> | **CPCV**（v1.16.0 新增） | Combinatorial Purged Cross-Validation（López de Prado） | **OOS 性能分布是什么？**（非单条曲线——C(N,k) 组合生成分布，purge+embargo 防泄漏） | — | OOS Sharpe 分布 std/mean > 0.5 红旗（变异过大） | ✅ 替代单路径 walk-forward MUST（Phase 1.5+） |
> | **PurgedKFold** | Purged K-Fold CV（CPCV 前身/简化版） | 标签重叠窗口是否泄漏？（金融 CV #1 泄漏源） | — | 任何泄漏=红旗 | ✅ walk_forward 实验（CPCV 未实施时的 MVP 替代） |
>
> **关键洞察**（Soloviov 2026-07）：PBO 的参考值不是 0 而是 **0.5**——纯噪声下 in-sample 冠军由对称性等概率落在 OOS 任意位置，一半时间在中位数以下。**PBO ≈ 0.5 = 搜索没学到任何泛化东西 = 过拟合**；PBO ≈ 0 = 搜索可信。Soloviov 在 T=1000/N=200/S=16 控制实验中验证：纯零边缘策略 PBO=0.476±0.137（in-sample Sharpe 1.98 → OOS 0.06），植入真实边缘 PBO=0.001（in-sample 3.73 → OOS 2.34 保留真实边缘）。
>
> **PBO 分层解读**（v1.5.0 新增，对标 [usekeel.io 2026-05-17](https://usekeel.io/learn/probability-backtest-overfitting)）：原 v1.3.0 的"PBO>0.2 红旗"过于粗粒度，usekeel.io 给出 5 层精确解读，对 §4.12 ADAPT_STRATEGY 的 decay_cause 诊断有直接影响（PBO>0.5 → decay_cause=overfitting → 直接退役）：
>
> | PBO 范围 | 解读 | 决策建议 | decay_cause 映射 |
> |---|---|---|---|
> | **< 0.1** | 强信号——IS 排名对 OOS 排名高度信息性 | ✅ 可信，可部署 | — |
> | **0.1-0.3** | 弱信号——honest research 典型（disciplined feature engineering） | ✅ 可部署，注意监控 | — |
> | **0.3-0.5** | 临界——better than chance 但信号弱 | ⚠️ 谨慎部署，加密监控 | regime（可能 regime 相关） |
> | **≈ 0.5** | 随机——搜索没学到泛化东西 | ❌ 阻断部署 | overfitting |
> | **> 0.5** | 反向 perverse——optimizer 可靠地选最差未来策略 | ❌ 阻断部署，walk away | overfitting（严重） |
>
>
> **n_trials 字段重要性**：DSR/PBO 计算必需试验数 N。若测试 M 个相关参数组合，用相关矩阵特征值谱估计有效独立数 N_eff（[stockalpha 2026-02](https://stockalpha.ai/alpha-learning/backtest-reality-checks-deflated-sharpe-pbo-and-multiple-testing-control)）。PBO 需完整 returns 矩阵（所有候选策略收益序列），DSR 只需最终选中策略收益 + N_eff。

> 🧪 **MTC 第 5 方法族详解（v1.12.0 新增，对标 [studentone.tech 2026-06-04 九道门级联](https://dashboard.studentone.tech/blog/out-of-sample-tests-counter-overfitting-menu) + [metricgate 2026-06-10 Model Confidence Set](https://metricgate.com/docs/model-confidence-set-forecast/) + [marketmaker.cc 2026-06-29 DSR 多重检验对比](https://marketmaker.cc/de/blog/post/deflated-sharpe-multiple-testing/) + [arXiv:2604.15531 Falsification Audit 2026-04-16](https://arxiv.org/pdf/2604.15531v1)）**：PBO/DSR/PSR/MinBTL 四方法回答"单个策略或单次搜索是否过拟合"，但**不回答"N 个策略同时检验时，族错误率（FWER）控制下哪些仍显著"**——测试 100 个策略时即使全部纯噪声，按 p<0.05 仍会有 ~5 个"显著"（multiple testing 问题）。MTC（Multiple Testing Correction）填补此缺口：
>
> | 子方法 | 全称 | 机制 | 误报率（marketmaker.cc 2026-06 受控实验） | 个人项目适用性 |
> |---|---|---|---|---|
> | **White's RC** | White's Reality Check (2000) | Bootstrap 重采样计算 p 值，需预先指定基准策略 | 0.022（2.2%） | ✅ 有明确基准时 |
> | **Hansen SPA** | Superior Predictive Ability (2005) | White's RC 改进版，recentered p 值更稳定 | — | ✅ White's RC 升级 |
> | **Romano-Wolf** | Romano-Wolf Step-Down (2005) | 控制 FWER，比 Bonferroni 更强大且不崩溃于大族 | — | ✅ **推荐**（比 Bonferroni 强） |
> | **MCS** | Model Confidence Set (Hansen-Lunde-Nason 2011) | 返回"统计不可区分的最佳模型**集合**"而非单一赢家，无需预指定基准 | — | ✅ **推荐**（无基准时） |
> | **BH-FDR** | Benjamini-Hochberg FDR (1995) | 控制 False Discovery Rate 而非 FWER，将原始 p 转为搜索修正后 q 值 | 0.007（BHY 变体） | ✅ 多策略筛选 |
>
> **关键洞察 1**（studentone.tech 2026-06）：SPA 与 Romano-Wolf **互斥**——平台拒绝同时运行两者，因回答重叠问题且叠加导致已知统计冲突。**选其一即可**，推荐 Romano-Wolf（更强大）。
>
> **关键洞察 2**（metricgate 2026-06 MCS）：MCS 的"输出集合而非赢家"哲学特别适合策略选择——若 5 个策略在 MCS 中统计不可区分，**不应选 Sharpe 最高的**（那是噪声选择），而应选**最稳健/最可解释/最低容量的**（经济逻辑选择）。这与 §4.13 PROMOTE_ENTRY G2 的 plateau_score（Soloviov 选择原则）精神一致——plateau 区域内选参数不应取峰值。
>
> **关键洞察 3**（marketmaker.cc 2026-06-29 受控实验）：朴素"最佳 Sharpe 显著？"测试误报率 **100%**（测 100 个纯噪声策略总有 p<0.05 的）；DSR≥0.95 误报率 0.1%；White's RC 2.2%；Harvey-Liu BHY 0.7%。**DSR 是性价比最高的**（误报率最低+实现最简单），MTC 方法是 DSR 的补充而非替代——DSR 校正选择偏差（N 次试验），MTC 校正族错误率（N 个策略同时检验），两者正交。
>
> **关键洞察 4**（arXiv:2604.15531 Falsification Audit 2026-04）：比 PBO 更根本——不是检测某策略是否过拟合，而是检测整个**研究流程**（特征构建→调参→选择→组合映射）是否会产生虚假发现。方法：将完整工作流在合成零预测环境（zero-predictability + microstructure placebos）中测试，若工作流在这些环境中产生显著 walk-forward 证据→被"伪造"（判定方法无效）。**适用场景**：评估注册表体系中"策略发现流程"本身的有效性，而非单个策略。
>
> **个人项目 MVP 决策**：MVP 阶段策略数少（<10），MTC 可选（n_strategies < 5 时族错误率不显著）。Phase 1.5+ 多策略筛选 MUST 跑 Romano-Wolf 或 MCS（二选一，非叠加）。schema 预留 `mtc_method`（romano_wolf/mcs/bh_fdr）+ `mtc_pvalue`（修正后 p 值）+ `mtc_survived`（bool，是否在 MTC 中存活）三字段。`is_overfit` 综合判定升级 = (pbo_value > 0.2) ∨ (dsr_pvalue < 0.05) ∨ (mtc_survived == False)；MTC 不通过 → 阻断部署（即使 PBO/DSR 通过）。

> 🔄 **CPCV 第 6 方法详解（v1.16.0 新增，对标 [noonbarbari 2026-07-04](https://noonbarbari.xyz/de/blog/cpcv-combinatorial-purged-cv) + [tradingstrategy.ai](https://tradingstrategy.ai/docslearn/backtesting.html) + [arXiv:2603.09219 AlgoXpert 2026-03](https://arxiv.org/pdf/2603.09219v1) + [ceta-research 2026-03](https://github.com/ceta-research/strategy-backtester/blob/main/ML_TRADING_RESEARCH.md) + [beefed.ai 2026](https://beefed.ai/en/backtesting-best-practices-avoid-overfitting)）**：walk-forward 给你**一条** OOS equity curve，CPCV 给你 **C(N,k) 条**（N=10,k=2 时 45 条）——López de Prado 称 walk-forward 的单路径问题为"backtest selection bias"（你恰好用了那条好看的切法）。CPCV 三步增强：① **组合而非滑动**——计算所有 C(N,k) 种 train/test 切分而非仅向前滑动；② **purge**——移除 label horizon 与 test set 重叠的 training 观测（ML/前视标签的关键泄漏源）；③ **embargo**——test set 后留小缓冲区（如 1% bars）处理自相关。输出是 **OOS Sharpe 分布**（mean ± std）而非单点估计——分布的**方差才是真实信号**。
>
> **CPCV vs walk-forward 对比**：
>
> | 维度 | walk-forward（单路径） | CPCV（组合分布） |
> |---|---|---|
> | 迭代次数 | 1（向前滑动） | C(N,k)（N=10,k=2 → 45） |
> | OOS 曲线数 | 1 条 | 45 条独立重建 |
> | OOS 观测覆盖 | ~20% 历史 | 每根 bar 在 ~9 种切分中作为 OOS |
> | 输出 | 单个 Sharpe/MaxDD | Sharpe 分布 mean ± std |
> | 切法敏感性 | 高（换 chunk 大小结果变） | 低（所有切法平均） |
>
> **关键洞察 1**（noonbarbari 2026-07）：walk-forward 说"此策略 OOS 赚了 X%"，CPCV 说"此策略 OOS Sharpe = 0.7 ± 0.3 across 45 种切分"——后者让你看到**最坏情况**而非幸运路径。若 45 条曲线中部分为负 Sharpe，即使 mean 正也不可信（策略对切法敏感=过拟合征兆）。
>
> **关键洞察 2**（tradingstrategy.ai）：**5 年日数据 + 45 个策略变体 = 几乎必然找到假赢家**——t-stat 需接近 **3.0**（而非传统 1.96）才能声称真实 edge。这与 §4.13 PROMOTE_ENTRY G2 的 DSR 阈值呼应——DSR 已校正 N 次试验，CPCV 进一步校正切法选择偏差。
>
> **关键洞察 3**（AlgoXpert arXiv:2603.09219 2026-03）：IS 阶段优先**稳定参数区域（plateaus）**而非单一最优——`Ω_stable = {θ | SR(θ) ≥ 0.9 × SR_opt}`，与 §7.2 的 `plateau_score`（Soloviov 选择原则）精神一致。WFA 配 **majority-pass + catastrophic-veto** 双门禁：majority-pass = 通过的 fold 比例 ≥ 阈值 q；catastrophic-veto = 任何 fold 触发灾难性条件（如 MaxDD 突破硬红线）立即整体 FAIL，不论其他 fold 多好。**catastrophic-veto 比 §4.13 PROMOTE_ENTRY 的硬编码阈值更鲁棒**——不是"平均回撤 < 15%"而是"任何切分中回撤 > X% = 一票否决"。
>
> **个人项目 MVP 决策**：MVP 阶段用 PurgedKFold（CPCV 简化版，walk-forward + purge），Phase 1.5+ 升级为完整 CPCV（C(N,k) 组合分布）。schema 预留 `cpcv_n_groups`（int, 默认 10）+ `cpcv_k_test`（int, 默认 2）+ `cpcv_oos_sharpe_mean`（float）+ `cpcv_oos_sharpe_std`（float）+ `cpcv_worst_max_dd`（float, 45 条中最差 MaxDD）五字段。`is_overfit` 综合判定升级 = (pbo_value > 0.2) ∨ (dsr_pvalue < 0.05) ∨ (mtc_survived == False) ∨ (cpcv_oos_sharpe_std / cpcv_oos_sharpe_mean > 0.5)；CPCV 变异过大（std/mean > 0.5）→ 阻断部署（即使 PBO/DSR 通过——策略对切法敏感=过拟合）。**catastrophic-veto 增强 §4.13 PROMOTE_ENTRY**：G1 门禁新增"cpcv_worst_max_dd > 0.15 = 一票否决"（任何切分中回撤超红线 = 不论其他指标多好都不上线）。

> 📏 **MinBTL/MinTRL 第 4 指标详解（v1.11.0 新增，对标 [Bailey & López de Prado 2014](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2389776) + [quantskills/skill-backtest-overfit 2026-07-03](https://github.com/quantskills/skill-backtest-overfit) + [auditzk 2026-03-12](https://www.auditzk.com/articles/track-record-statistical-significance) + [backtestbase 2026-01](https://www.backtestbase.com/education/how-many-trades-for-backtest) + [digitalninjasystems 2026-06-20](https://digitalninjasystems.wpcomstaging.com/2026/06/20/how-much-backtest-data-do-you-really-need-for-reliable-results/)）**：PBO/DSR/PSR 回答"选择过程是否过拟合"，但**不回答"样本量是否足够信任此 Sharpe"**——一个 Sharpe=0.5 的策略可能 PBO<0.1（搜索可信）但仍需 25-40+ 年数据才能排除噪声。MinBTL（Minimum Backtest Length）填补此缺口：
>
> **公式**：`MBL = (1/2) × (Z_α × σ_ann / SR_ann)²`，其中 Z_α=1.96（95%置信），σ_ann=年化波动率，SR_ann=年化 Sharpe。
>
> **经验阈值表**（auditzk 2026-03 + digitalninjasystems 2026-06，IID 假设 vs 现实含自相关膨胀 2-4x）：
>
> | 观测 Sharpe | IID 95% 所需年数 | IID 99% 所需年数 | **现实所需年数**（含自相关/重尾膨胀） | 个人项目解读 |
> |---|---|---|---|---|
> | 0.5 | ~16 年 | ~28 年 | **25-40+ 年**（不实用） | Sharpe 0.5 策略基本无法用统计验证，MUST 靠经济逻辑 |
> | 1.0 | ~4 年 | ~7 年 | **5-10 年** | MVP 目标 Sharpe，需 5+ 年实盘才统计可信 |
> | 1.5 | ~1.8 年 | ~3.1 年 | **3-5 年** | 高 Sharpe，2-3 年 probation 后可初步确认 |
> | 2.0 | ~1 年 | ~1.7 年 | **1.5-3 年** | 极高 Sharpe，警惕过拟合（DSR/PBO 复检） |
> | 3.0 | ~5 月 | ~9 月 | — | HFT 级，样本量不是瓶颈但生存偏差是 |
>
> **标准误公式**：`SE(SR) ≈ 1/√T`（T=独立观测数），T=250（1年日数据）时 SE≈0.063——观测 Sharpe 0.8 的 95% CI 为 [0.68, 0.92]，精度不足以做配置决策。**自相关膨胀**（Lo 2002）：日收益序列相关使 SE 膨胀 1.5-3x，IID 假设严重低估所需样本量。**重尾膨胀**：A 股 γ₄>6 尖峰重尾使 Sharpe 估计器比公式暗示的更嘈杂，CI 比计算值更宽。
>
> **与 §4.13 PROMOTE_ENTRY 的联动**（v1.11.0 关键）：Gate 1 回测验证门当前检查 `oos_period_months >= 3`，但**未检查实盘 track record 是否达到 MinBTL**——一个 Sharpe=1.0 策略 3 个月 OOS 通过后上线，但 MinBTL=5-10 年意味着 3 个月实盘数据**完全不足以确认** edge 真实。**建议**：PROMOTE_ENTRY 后的渐进式部署（Shadow→Canary→Full）中，Full 阶段应持续 `min_trl_years` 年才从 "probation" 升级为 "confirmed"——§4.8 生命周期第6阶段 Deployment="probation 非 confirmation"的量化依据即 MinBTL。`lifecycle_status` 从 `live`(probation) → `monitoring`(confirmed) 的转换条件之一 = 实盘 track record ≥ `min_trl_years`。
>
> **与 §4.8 DECAY_SCAN 的联动**：衰减检测的 baseline_sharpe 须基于 ≥ MinBTL 的样本建立——短样本 baseline 本身可能是噪声峰值，导致 ic_ratio 比较失真。`decay_scan_frequency` 的设定也受 MinBTL 影响：track record < MinBTL 时，monthly 扫描的统计意义有限（样本不足），应更关注 regime 匹配和经济逻辑而非纯统计指标。
>
> **个人项目 MVP 决策**：MVP 阶段多数策略 Sharpe 0.5-1.0，MinBTL 5-40 年远超个人项目实盘周期——**这意味着个人项目策略上线后几乎永远处于 probation 态**，统计确认需极长周期。实务对策：① 经济逻辑优先（§4.8 阶段1 Idea Generation 的"信号发现 vs 信号幻觉"经济理性校验比统计检验更重要）；② 多策略组合分散（CSDN 2026-08-09 的 `multi_strategy` 原则，不依赖单一策略统计确认）；③ 跨 regime 验证替代时间长度（Linitics 2026-04 的"regime diversity testing"，3-5 年覆盖牛/熊/震荡 3 regime 比单 regime 10 年更有信息量）；④ `min_trl_years` 字段填入计算值，`lifecycle_status` 须 track record 达标才升 `monitoring`，否则保持 `live`(probation) + 加密 `decay_scan_frequency`(weekly)。

> 🔍 **回测过拟合 7 症状预检清单**（v1.10.0 新增，对标 [tradingnote.co 2026-06-23 Overfitting en Trading](https://tradingnote.co/es/blog/overfitting-trading-que-es-como-detectarlo) + [quant67.com 2026-05-01 回测陷阱](https://quant67.com/post/quant/20-backtest-pitfalls/20-backtest-pitfalls.html)）：在跑正式 PBO/DSR/PSR/MinBTL 四方法前，先看 7 个经验症状——若命中 ≥4 个，几乎必然过拟合，无需跑统计检验即可阻断部署：
>
> | # | 症状 | 观察到的现象 | 为何是警报信号 |
> |---|---|---|---|
> | 1 | 权益曲线无台阶 | 曲线近乎完美平滑上升，无可见过回撤 | 真实市场有回撤，完美曲线=memorized 噪声 |
> | 2 | PF>3 且 DD<5% | Profit Factor 3.5 + 最大回撤 3% | 高收益+低回撤同时出现=统计罕见 |
> | 3 | 单资产/单期有效 | PF 2.8 在某标的，其他标的崩溃 | 真 edge 会泛化，单资产=拟合该资产噪声 |
> | 4 | Sharpe>2.5（大搜索后） | 400 参数组合后 Sharpe 2.8 | DSR 可能负——2.8 可能只是 400 噪声中最好 |
> | 5 | walk-forward 退化 | IS 高收益但 OOS≈0 或负 | 最直接诊断：不泛化到未见数据 |
> | 6 | 多参数少交易 | 12 参数但仅 60 trades | 需 ≥30 trades/参数，12 参数需 ≥360 trades |
> | 7 | Monte Carlo 频繁破产 | 1000 次重排 30%+ 终止 DD>50% | 不 survive 交易顺序重排=依赖特定历史顺序 |
>
> **与正式检验的关系**：7 症状是"快速预筛"（秒级判断），PBO/DSR/PSR/MinBTL 是"正式诊断"（分钟级计算）。预筛命中≥4 → 直接走 §4.10 RETIRE_ENTRY 或回 §4.12 ADAPT_STRATEGY Level 5，不浪费算力跑 PBO。预筛命中≤1 → 跑正式四方法确认。这呼应 CSDN 2026-08-09 的"AI 不是解药"——简单症状检查有时比复杂统计更早暴露问题。`is_overfit` 字段判定可先看 7 症状命中数，再结合 PBO/DSR 正式值综合判定。
>
> **个人项目 MVP 决策**：MVP 阶段参数搜索少（<50 试验），PBO/DSR 可选（n_trials < 10 时统计意义有限）。Phase 1.5+ 参数搜索扩展后 MUST 跑 PBO + DSR 双门禁（[CSDN 2026-03 实践](https://ask.csdn.net/questions/9387159)：PBO > 0.15 ∨ DSR < 1.0 → 阻断部署）。schema 已预留 pbo_value/dsr_value/psr_value/n_trials/min_trl_years 五字段（v1.11.0 补 min_trl_years），无需后续迁移。`is_overfit` 综合判定 = (pbo_value > 0.2) ∨ (dsr_pvalue < 0.05)；MinBTL 不影响 `is_overfit`（它衡量样本充分性非过拟合），但影响 `lifecycle_status` 升级（track record < min_trl_years → 保持 `live`(probation) 不升 `monitoring`(confirmed)）。

> 🎯 **PSR vs DSR 排序能力修正 + Plateau-Robustness 选择原则（v1.6.0 新增，对标 [Soloviov 2026-06 Plateau-Robustness 控制实验](https://plateau.marketmaker.cc/) + [GitHub suenot/plateau-robustness](https://github.com/suenot/plateau-robustness)）**：上文将 PSR 标为"DSR 前身"可能暗示 DSR 严格优于 PSR，但 Soloviov 2026-06 在 9000 次控制实验（已知 population Sharpe 曲面 ground truth）中得出**反直觉结论**：
>
> | 诊断方法 | AUC（检测无边缘策略） | 角色 | 关键发现 |
> |---|---|---|---|
> | **PSR against zero** | **0.81**（最强单一诊断） | 显著性检验 | **信号载体**——significance test, not multiplicity deflation, carries the signal |
> | DSR | 0.79 | 多重检验校正 | 提供**校准**（calibration），非**排序力**（ranking power）——trials 相关如 grid scan 时贡献更小 |
> | PBO | — | 选择过程泛化性 | CSCV 对称交叉验证，回答不同问题 |
> | Plateau 几何指标（robustness score/plateau width） | 弱（standalone） | **选择原则**非独立检测 | fixed threshold 未校准，standalone 诊断不可靠 |
>
> **核心洞察**：① PSR 在排序/检测能力上**不弱于** DSR（AUC 0.81 > 0.79），DSR 的价值在多重检验校正而非提升检测力——MVP 阶段若只跑一个统计检验，PSR（计算更简单，无需 N_eff 估计）是合理起点；② **plateau heuristic（"prefer plateaus over peaks"）作为选择原则有效**——选 smoothed surrogate 的 argmax 而非 raw argmax，OOS Sharpe 平均提升 **0.12（1D）/ 0.31（2D）**，且提升量随参数维度增长单调递增；③ 但 plateau 几何指标**作为独立过拟合检测不可靠**——fixed threshold（如"robustness score > 0.1"）未校准，standalone AUC 弱。结论：**"prefer plateaus" 应与统计显著性检验并用，而非替代**（Soloviov 原文："should be used alongside, not instead of, statistical significance controls"）。
>
> **对 §4.12 ADAPT_STRATEGY Step 3 的影响**：Step 3b 已用 `find_plateau` + `centroid`（取稳定区域中心非最高点），这正是 Soloviov 验证的"选择原则"用法——✅ 正确。但须注意：plateau 检测通过**不能**替代 Step 3c 的 DSR 校正 + Step 4 的 OOS 验证，三者互补。Step 3b 的 plateau 通过是必要非充分条件。
>
> **honest-backtest 7 层验证框架（v1.6.0 新增，对标 [krivonosoff161/honest-backtest 2026-06](https://github.com/krivonosoff161/honest-backtest)）**：该开源库提出 7 层验证架构，每层捕获不同谎言，与本注册表的 experiment_registry 验证字段映射：
>
> | Layer | 捕获的谎言 | 模块 | 对应 experiment_registry 字段 |
> |---|---|---|---|
> | 1 Data | look-ahead/幸存者偏差/填充 | data | data_period + universe |
> | 2 Costs | 滑点/佣金/冲击未建模 | costs | cost_model_ref（MUST 指定） |
> | 3 Significance | p-hacking/多重检验 | stats | psr_value / dsr_value / n_trials |
> | 4 Overfitting | IS-OOS gap | overfit | pbo_value / is_overfit |
> | 5 Robustness | 幸运尖峰 vs 真实高原 | robustness | **plateau_score（v1.6.0 新增字段）** |
> | 6 Forward | 上述全过只是"还没坏" | forward | completed_at + OOS period |
> | 7 Adversarial | **AI 试图杀死发现而非祝福它** | adversarial | **adversarial_result（v1.6.0 新增字段）** |
>
> **Layer 7 对抗验证**是 honest-backtest 的核心创新——"the AI step that tries to kill your finding instead of blessing it"。对 100% AI 开发的个人项目尤为契合：AI agent 在回测通过后，**主动构造证伪场景**（极端 regime / 参数微扰 / 替代 universe / 成本上调 2x / 随机 label 置换检验），若策略在这些场景下仍存活才确认 edge 真实。这与 §4.8 阶段4 Validation 的"试图证伪（非证明有效）"原则一致。schema 新增 `adversarial_result: obj`（{test_name, passed, kill_reason}列表）+ `plateau_score: float`（Soloviov robustness score，standalone 弱但与 PSR 组合增强 fragile mode 检测）。

> 🔍 **2026 MLflow 生态现状（v1.1.0 新增，v1.2.0 更新至 3.15.1，影响 51 号退役决策）**：2026 年 MLflow 已成为实验追踪 de facto 标准首选（[ZenML 2026-02 Comet vs MLflow](https://www.zenml.io/blog/comet-vs-mlflow) ｜ [MLflow 2026 LLM Observability](https://mlflow.org/articles/top-llm-observability-tools-in-2026-a-pro-guide)）。**Neptune.ai 已被 OpenAI 收购并将关停公共服务**（[ZenML 2025-12 Neptune Alternatives](https://www.zenml.io/blog/neptune-ai-alternatives)），原 schema 对标 Neptune.ai 需移除。
>
> **MLflow 3.15.0/3.15.1 最新进展（v1.2.0 新增，[CHANGELOG](https://github.com/mlflow/mlflow/blob/master/CHANGELOG.md)）**：3.15.0（2026-07-31）+ 3.15.1（2026-08-03 patch）。重大特性：① **MCP Registry**——Model Context Protocol 服务器集中目录，支持语义版本配置+可提升别名+标签+自动发现工具+Claude Code/`.mcp.json` 连接，UI/REST API/Python 三入口；② **MLflow Assistant 增强**——多 LLM provider（Claude Code/Codex/OpenAI-compatible），实时 token 用量+成本显示；③ **Sharable table views**——Runs 表命名视图（列/序/宽/过滤/排序）URL 分享；④ **Proxy-less artifact upload**——presigned URLs 大文件直传云存储绕过 tracking server；⑤ Multi-modal LLM judges（图片评估）。3.10.0（2026-02-20）已加 Organization 多 workspace + Trace Cost Tracking + Multi-turn Evaluation。
>
> 51 号 MLflow 退役方案需重新评估——既然 Neptune 关停、MLflow 3.15 持续强化（MCP Registry 适合 AI agent 集成），**待定问题 E1**：是否应保留 MLflow 而非退役？若保留，experiment_registry 退化为 MLflow 的轻量元数据索引层（仅登记 experiment_id↔strategy_id↔universe_id↔benchmark_id↔cost_model_ref 映射 + conclusion 标签 + mlflow_run_id 关联），不重复 MLflow 已有的 run/metrics/artifact 能力。MLflow 3.15 MCP Registry 还可被本项目的 AI agent 通过 MCP 协议直接查询实验，符合 project_memory"集成到项目现有系统优于外部工具"偏好。

## 8. 裁定汇总

### 8.1 八项核心裁定

| # | 裁定问题 | 裁定结果 | 关键依据 |
|---|---|---|---|
| 1 | sub-strategy 术语 | 采用 `variant`（弃 sub-strategy），单向 `variant_of` | AQR/Two Sigma 非标准术语；variant 自描述；D38 谨慎层级精神 |
| 2 | 数据源合并 | 扩展并改名为 `data_asset_registry.yaml` | 名实相符治本；AI 自描述降长期识别成本；DAMA-DMBOK；OpenLineage 三实体一模型 |
| 3 | YAML vs DB | 现阶段 YAML + DB 预留，阈值因子>500/实验>5000 | Feast/MLflow 双轨；depgraph PG 先例；AI 友好 |
| 4 | 16号文档 | 降级为 why 层，§2 迁注册表，不退役 | 结构化数据 vs 叙述 why 分离；QuantConnect 代码+文档对应 |
| 5 | AGENTS.md 显化 | 不需退役，RULE-REGISTRY 段强化 | AGENTS.md 1248/3000 有空间；L137 已引用需突出业务资产 |
| 6 | onboarding 形式 | 三重保险（AGENTS.md+session_log+capability_lookup） | 多重互补；复用现有机制；不新建 hook |
| 7 | 施工顺序 | P0→P1→P2 三阶段，回测三件套优先 | 回测必需输入优先；注册表顺序≠模块顺序 |
| 8 | 字段字典范围 | 仅数据字段，不合并 frontmatter | DAMA-DMBOK/dbt 主流分离；单一职责 |

### 8.2 Schema 修正裁定（S1-S6）

| # | 修正项 | 内容 |
|---|---|---|
| S1 | 编号前缀 | registry_id=`REG-{NAME}-{NNN}`；entry id=`{PREFIX}-{DOMAIN}-{NNN}`；schema module_id 引用 depgraph MOD- 前缀 |
| S2 | factor_class | 10 类：Barra 6（value/quality/momentum/volatility/size/liquidity）+ A股特色 4（event/intraday/technical/sentiment） |
| S3 | strategy_class | 6 类：daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation（不含 sentiment_cycle） |
| S4 | variant | 单向 `variant_of`，删除 `variants` 列表（避免双向同步漂移） |
| S5 | 性能指标 | 现在就列，运行时可空（factor: ic/ir/decay/turnover/capacity；strategy: sharpe/max_dd/annual_return/capacity/turnover） |
| S6 | data_asset 改名 | 文件名+title 改，registry_id(REG-DATAFLOW-001)/module_id 全保留，ruling_registry 登记改名 |

### 8.3 过度工程审查（个人项目红线，v1.1.0 新增）

project_memory 硬约束：个人+100%AI 项目，过度工程是红线。逐项审查 12 注册表 + 通用设计是否过度：

| # | 审查项 | 裁定 | 依据 |
|---|---|---|---|
| O1 | 12 注册表是否过多 | ✅ **不过度，保留 12 表** | 12 表覆盖量化交易全资产谱系（因子/策略/指标/形态/池/基准/成本/算法/风控/数据/字段/实验），每表职责单一不可合并。project_memory 已明确"必须建立12个业务注册表"。合并反而破坏 SSOT |
| O2 | field_dictionary 能否并入 data_asset_registry | ❌ **不合并** | 裁定 8 已定：数据字段（行情/因子 type/unit/PIT）vs 数据资产（source/dataset/job 血缘）职责不同，DAMA-DMBOK/dbt 主流分离 |
| O3 | experiment_registry 能否暂缓用 MLflow 替代 | ⚠️ **待定 E1** | 2026 MLflow 是首选（Neptune 已关停）。若 51 号决定保留 MLflow，experiment_registry 退化为轻量索引层（不重复 MLflow 能力），仍需建表登记 experiment↔strategy 映射。**不能完全暂缓**——MLflow 不管 strategy_id 关联 |
| O4 | YAML vs DB（现阶段 YAML 是否合理） | ✅ **YAML 合理** | 因子<500/实验<5000 远未触发迁移阈值。Feast/MLflow 双轨先例（YAML 定义+运行时 DB）。SQLite 看似省事但失去 git diff/version/PR review 治理能力，个人项目 YAML + git 更优 |
| O5 | data_asset 三实体（sources/datasets/jobs）是否过重 | ✅ **不过度** | 对齐 OpenLineage 2026 主流三实体。个人项目**不需要** RunEvent/column-level lineage（企业级需求），三实体足够且已部分落盘（dataflow_graph_registry 已有 datasets+jobs，仅新增 sources 段） |
| O6 | chart_pattern 8 大类是否过多 | ⚠️ **MVP 裁剪** | 8 大类覆盖图形技术分析全谱系（TA-Lib 61 K线+缠论+波浪+Edwards&Magee）合理，但 §6.2.4 已定"MVP 只登记代码实际用到或明确规划的"。P1-B 先做 candlestick_pattern（low 主观性）+ chart_pattern（medium）2 类，chanlun/elliott_wave 等按代码反查按需补 |
| O7 | risk_limit 9 种限额是否过多 | ✅ **不过度** | project_memory 已明确"Kill Switch + 四级回撤为必须保留的风险红线；VaR 5级 + 7黑天鹅降级为监控层"。9 类中 position/concentration/drawdown/kill_switch 是必须红线，var/es/leverage/turnover/firm_risk 是监控层（先全建+全log，实盘6-12月后裁剪未触发项） |
| O8 | variant 机制（单向 variant_of）是否过度 | ✅ **不过度** | 单向引用避免双向同步漂移，查询简单（WHERE variant_of=X）。打板连板/趋势 2 variant 是实际需求 |
| O9 | 性能指标字段（运行时可空）是否过度 | ✅ **不过度** | 裁定 S5 已定：现在就列运行时可空，未来进 DB 时序存储。YAML 阶段 null 不占空间 |
| O10 | §11 YAML→DB 迁移路径是否过早规划 | ✅ **不过度** | 迁移路径是"预留"非"立即执行"。schema 按 DB 表设计（id/created_at/updated_at/version/status）成本极低，未来迁移省事。阈值（因子>500/实验>5000）明确，个人项目可能永不触发 |
| O11 | factor_class 10 类是否过多 | ✅ **不过度** | Barra 6 类是业界标准（MSCI Barra 模型），A股特色 4 类（event/intraday/technical/sentiment）是 A股必要扩展。qlib Alpha158 用 4 大类（趋势/均值回归/成交量/波动）但那是指标级分类非因子级 |
| O12 | strategy lifecycle_status 7 态是否过多 | ✅ **不过度** | candidate/backtest/sim/paper/live/monitoring/retired 对齐 2026 Strategy Lifecycle Management 主流（Idea→Design→Backtest→Validation→Deployment→Monitoring→Optimization→Retirement，[DeepTradeX 2026](https://deeptradex.zendesk.com/hc/en-us/articles/16820285969295-Strategy-Lifecycle-Management-Great-Trading-Strategies-Are-Managed-Not-Just-Built)）。68% 策略 18-24月需修改/退役，lifecycle 管理必要 |

**过度工程审查总结论**：12 注册表 + 通用 schema 设计**整体不过度**，符合个人项目"建库结构完整，内容按需填充"原则。唯一需关注：(1) chart_pattern MVP 裁剪到 2-3 类（O6）；(2) experiment_registry 待 51 号 MLflow 决策后定形态（O3/E1）。其余 10 项均合理保留。

## 9. 治理同步与验收

### 9.1 registry_of_registries.yaml 登记

P0 三件套已登记于 tier_2 业务资产段（[ROOR:549-577](../../../registry_of_registries.yaml)）：
- REG-UNI-001（entry_count: 5）
- REG-BMK-001（entry_count: 4）
- REG-CST-001（entry_count: 3）

### 9.2 AGENTS.md 显化

[AGENTS.md:150-153](../../../../AGENTS.md) RULE-REGISTRY 段新增业务资产速查（#ARCH-BREG-001 标记）。

### 9.3 ARCH 登记条目

[architecture_issue_registry.yaml:13560](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) `#ARCH-BREG-001` 记录裁定与施工进度。

### 9.4 验收标准

- [x] P0 三件套 YAML 落盘 catalogs/
- [x] registry_of_registries.yaml 登记 3 条
- [x] AGENTS.md 显化
- [x] ARCH-BREG-001 登记
- [x] v1.1.0 cost_model 印花税/过户费费率校准（同步 catalogs/cost_model_registry.yaml）
- [x] v1.2.0 施工算法体系补全：§4.5 CONSTRUCT_REGISTRY + §4.6 交叉引用矩阵 + §4.7 AUDIT_REGISTRY(E1-E7) + §4.8 生命周期管理 + DECAY_SCAN
- [x] v1.3.0 施工算法体系闭环：§4.7 补 E8-E10 + §4.9 EVOLVE_ENTRY + §4.10 RETIRE_ENTRY + §4.11 EVOLVE_SCHEMA + §4.8 DECAY_SCAN_MULTI 多检测器 + §7.2 PBO/DSR/PSR 过拟合检测
- [x] v1.4.0 施工算法体系完整闭环：§4.12 ADAPT_STRATEGY（衰减后适应，填补 检测→适应→退役 三环节中间缺口）+ §4.8 补 profit_factor/z_score 跨维度检测器 + §4.7 补 E5b commit绑定/E11 数据质量检查 + §4 原则9 补 Immutable Version 选项 + §4.11 补 schema 文件级版本管理 + factor/strategy schema 补 data_quality/adaptation_level/code_commit 字段
- [x] v1.5.0 ADAPT_STRATEGY 数学+经验双驱动：§4.12 补 Step 0 baseline 校验 + Step 1.5 衰减原因分类驱动决策（Five Horsemen）+ 三选一经验决策矩阵 + 6 类 review triggers 清单（对标 LuxAlgo 2026-08-03）+ §4.7 补 E12 baseline 保存完整性检查 + §4.8 补衰减原因分类表/经验数据补充/监控频率指导 + §7.2 补 PBO 5 层分层解读 + strategy schema 补 baseline 扩展字段/decay_cause/decay_scan_frequency
- [x] v1.6.0 PSR/DSR排序修正+Plateau选择原则+honest-backtest 7层验证+KRI 6角色治理+版本可复现性三要素+鲁棒CUSUM：§7.2 补 Soloviov Plateau-Robustness（PSR AUC 0.81>DSR 0.79）+ honest-backtest 7层（含Layer 7对抗验证）+ schema 补 plateau_score/adversarial_result；§6.2.2 补 KRI 6角色分离职责（阈值放宽更高级签批+持续违约协议）；§4.12 Step 3b 补 Soloviov plateau centroid 量化；§4 原则9 补版本可复现性三要素（code_commit+血缘三要素+materialization_ts，MLflow bundling）；§4.8 补鲁棒CUSUM GSA-LLR + RisingWave 静默失败；§4.7 修正 E12 缩进bug + E11 补 freshness
- [x] v1.7.0 执行算法反博弈+TCA双报告+图形识别Simplicity Wins+CNN+LSTM Hybrid+反Look-Ahead Bias+RETIRE级联响应：§6.2.1 补 anti_gaming/tca_metrics 字段 + 反博弈随机化（Poisson-ish非时钟）+ POV内生性γ/(1-γ) + TCA双报告（VWAP slippage+IS）；§6.2.4 补 cnn_lstm_hybrid 变体 + "Simplicity Wins"原则（原始K线+4层CNN AUC 0.892>复杂模型）+ 反Look-Ahead Bias归一化约束；§4.10 RETIRE_ENTRY 补级联响应定义（按依赖方类型分派：strategy→review_required/迁移建议，factor→自动review）
- [x] v1.8.0 PROMOTE_ENTRY上线晋升算法（填补§4.9引用缺口）：新增§4.13 PROMOTE_ENTRY 8门禁上线算法（G1回测验证/G2过拟合检查/G3风控限额/G4Baseline保存/G5代码冻结/G6基准分配/G7衰减监控/G8人工签批），对标opennash 7-gate+MLflow验证门+thirstysprout生产就绪+KRI治理签批；§4.9 EVOLVE_ENTRY Step 1 status分支更新引用§4.13/§4.10；完整生命周期闭环：CONSTRUCT→PROMOTE→EVOLVE→DECAY→ADAPT→RETIRE
- [x] v1.9.0 回滚+依赖解析算法闭环：新增§4.14 ROLLBACK_ENTRY回滚算法（7步：触发源判定→目标版本定位→仓位处置→衰减监控重置→审计日志→7天冷却防flip-flop→通知，填补PROMOTE_ENTRY逆向缺口）+ §4.15 DEPENDENCY_RESOLVE依赖解析算法（Kahn's拓扑排序construct_order/transitive_deps传递依赖/impact_rage影响范围，补全§4.6 FK矩阵的算法层支持）
- [x] v1.10.0 算法体系导航图+语义漂移+SHA256 manifest+参数漂移+渐进式部署：新增§4.4算法体系导航图（11算法按生命周期6阶段分组+调用矩阵+关键依赖关系）+ §4.7补E13语义漂移检查（semantic_contract/null_semantics/default_fill_policy，对标oracles.cloud数据契约3类漂移+neojn 2026-05特征存储漂移）+ §4原则9补SHA256 manifest选项（bit-level可复现，对标OmniBioAI ModelHub 2026-08-08+Ollama content-addressable storage）+ §4.8补参数漂移概念（eastmoney 2026-07-18中文源"系统不是在瞬间崩溃而是在不知不觉中腐烂"）+ §4.13补渐进式部署Shadow→Canary→Full三阶段（对标nexus-trade-engine #162+metricgate 2026-04+frontierledger+NautilusTrader 2026-08-09）
- [x] v1.11.0 YAML→DB迁移算法闭环+MinBTL回测过拟合第4方法：新增§4.16 MIGRATE_REGISTRY（R1-R7七阶段渐进式迁移+R4/R7双gate+28天清洁期，对标longterm-wiki #2076+mvpfactory.io+youngju.dev，补全§11迁移路径算法层，12算法7阶段完整闭环"建→上→改→测→应/回→退→迁"）+ §4.4导航图更新为12算法7阶段（新增阶段7迁+调用矩阵补MIGRATE_REGISTRY行+关键依赖补R1/R5/R7复用关系）+ §7.2 experiment_registry补min_trl_years字段（Minimum Track Record Length，Bailey&López de Prado 2014，MBL=0.5×(Z_α×σ_ann/SR_ann)²）+ 回测过拟合检测三方法→四方法（PBO+DSR+PSR+MinBTL，对标backtestbase+auditzk+digitalninjasystems+quantskills 2026）+ §14待定问题补H1迁移阈值校准/I1 MinBTL A股校准
- [x] v1.12.0 2026-08-10最新研究对标+回测过拟合第5方法MTC+8项算法升级：新增§4.17最新研究对标补充（8项：双曲衰减模型α(t)=K/(1+λt)+BOCPD第4检测器+Wasserstein漂移+pgroll零停机+PubGrub版本约束+字典序拓扑+Data Contracts分层+multigrid三层eval+Feast OpenLineage）+ §7.2回测过拟合四方法→五方法（+MTC：White's RC/Hansen SPA/Romano-Wolf/MCS/BH-FDR，对标studentone.tech 9-gate+metricgate MCS+marketmaker.cc DSR对比+arXiv Falsification Audit）+ §13补v1.11.0修订明细R37-R39+v1.12.0修订明细R40-R42
- [x] v1.13.0 第二轮缺口审计+版本差异算法DIFF_ENTRY：新增§4.18 DIFF_ENTRY横切只读查询算法（5步字节快判→字段三分类→语义分类→semver bump映射→breaking查依赖，对标IETF YANG Schema Comparison 2026-05+AST/byte-hash双策略2026-04+schema.biz三桶2026-04，填补EVOLVE/EVOLVE_SCHEMA/PROMOTE三者共需版本对比无统一算法缺口）+ §4.19第二轮缺口审计10领域映射（1硬缺口已补DIFF_ENTRY/4已覆盖/5 DEFER记录DB升级路径，13算法体系完整闭环无施工阻塞）+ §4.4导航图12→13算法+§13修订明细R43-R45
- [x] v1.14.0 A股2026监管变更+算法一致性修复+第三轮研究：§4.20 A股2026年7月监管变更影响（ST涨跌5→10%+程序化15笔/秒+盘后扩围+收盘集合，execution_algo/risk_limit/universe/cost_model/benchmark schema MUST 预留合规字段）+ PROMOTE_ENTRY Gate1加min_trl_years交叉校验+Gate2加MTC多重检验检查（v1.11.0/v1.12.0字段一致性修复）+ §4.17② BOCPE误判频率派事实错误修正（BOCPE=BOCPD已是贝叶斯，增量=score-driven变体）+ §4.21第三轮研究7项（SR26-2/NautilusTrader/Double-selection LASSO/华创LightGBM/AH-HMM/Feast0.64/meta-labeling）+ §13修订明细R46-R49
- [x] v1.15.0 局域网关闭补齐+高频阈值核实+第四轮研究流程治理：§4.20③ 局域网行情通道关闭（2026-07-31关闭/广域网时延≥2ms地板/8-31网关指引施行，v1.14.0漏掉的第三项实盘合规红线，execution_algo补latency_floor_ms+network_type/cost_model补slippage_regime/data_asset补latency_profile+colocation_eligible）+ §4.20② 高频阈值核实（中基协研报300笔/秒系旧规误引，15笔/秒现行有效）+ §4.22第四轮研究5项（AlphaSchema/Agentic Workflows/证据SHA256+allowed_use/数据契约独立模块/Agent竞争转向）聚焦研究流程治理 + §13修订明细R50-R52 + §14待定问题补J2
- [x] v1.16.0 CPCV升级六方法+价格笼子schema+第五轮研究：§7.2回测过拟合五方法→六方法（+CPCV组合净化交叉验证，López de Prado核心方法，C(N,k)条OOS分布+purge+embargo+catastrophic-veto）+ §4.13 PROMOTE_ENTRY G2门禁新增CPCV检查（cpcv_worst_max_dd>0.15一票否决+std/mean>0.5切法敏感性阻断）+ §4.23第五轮研究4项（AlgoXpert IS-WFA-OOS/EU AI Act 2026-08-02可解释AI/A股价格笼子+T+1+涨跌停/决策审计append-only）+ execution_algo_registry schema MUST新增price_cage_config+t_plus_1+limit_up_down_untradable三字段（40_execution_broker v2.6.0已实现check_price_cage，schema对齐）+ §13修订明细R53-R55
- [x] v1.17.0 P0代码bug修复+仓位管理+A股特色数据第六轮研究：§4.13 PROMOTE_ENTRY G1/G2门禁P0代码bug修复（字符串拼接str()转换+CPCV mean<=0直接FAIL）+ §4.24第六轮研究5项填补仓位管理和A股特色数据两个对标空白（Conformal Kelly/Kelly+ML协方差/Sizing Shootout/国泰海通A股高频因子/龙虎榜Level-2数据源license_type）+ §13修订明细R56-R58
- [x] v1.22.0 GSA-LLR鲁棒CUSUM+LAP前瞻污染检测+LIB偏差审计第十一轮研究+注册表schema补全：§4.29第十一轮研究4项（GSA-LLR重尾变点检测/LAP-FinCAD-CMMD LLM前瞻污染三方法/企业债LIB偏差/A股板块轮动14.8%警示）+ §4.7新增E18 LAP前瞻污染检测+E19因子构造偏差审计LIB（E1-E17→E1-E19）+ §4.8 DECAY_SCAN_MULTI检测器1增重尾自适应分支GSA-LLR + factor/strategy/risk_limit三注册表entry_schema补全v1.2.0-v1.21.0缺失字段（factor补8字段，strategy补17字段，risk_limit补2字段）+ §13修订明细R59-R62
- [x] v1.23.0 RMT去噪因子相关性矩阵+非高斯回撤校准+共形VaR校准第十二轮研究：§4.30第十二轮研究3项（RMT去噪EFS+物理信息奇异值学习/RSB非高斯回撤风险校准/Regime-Weighted Conformal VaR校准）填补前十一轮"因子冗余检测方法学质量"+"回撤阈值高斯假设缺陷"+"VaR压力期系统性误校准"三个对标空白 + §4.7新增E20 RMT去噪因子相关性矩阵审计（E1-E19→E1-E20）+ factor_registry schema补rmt_denoised字段 + risk_limit_registry schema补drawdown_calibration_method+var_calibration_method两字段 + §4.4导航图E1-E19→E1-E20 + §13修订明细R63-R65
- [x] v1.24.0 universe_registry生存偏差治理第十三轮研究+E14扩展：§4.31第十三轮研究1项（universe PIT成分构造+退市股处理survivorship-free，alphanume 2026-06 "universe is where survivorship bias enters most silently"+tickernerd 2026-08 三锁定窗口PIT+arXiv:2603.16904 survivorship-bias-free S&P500）；§4.7 E14扩展c维度（universe_registry pit_constituent_construction/delisted_handling审计，不新增E编号避免膨胀，E14本就是回测数据偏差检查语义内聚，省E1-E20→E1-E21的6处同步churn）；universe_registry schema补pit_constituent_construction/delisted_handling/survivorship_free三字段 + §13修订明细R66-R67
- [ ] P1 七注册表落盘 + 登记 + 显化（遵循 §4.5-§4.16 + §4.18 算法体系施工，13 算法 7 阶段 + 1 横切查询完整闭环；P1-B 前必读 §4.20①②③ 监管字段预留 + §4.23③ 价格笼子/T+1/涨跌停三字段预留 + §4.24⑤ 数据源 license_type 标注）
- [ ] P2 两注册表落盘 + 登记 + 显化
- [ ] **ruling_registry.yaml 登记 data_asset 改名（S6 裁定未落实，P1-B 前必须补齐，待定问题 D1）**
- [ ] audit_registration.py 扫描通过，无 broken/pending（覆盖 §4.7 E1-E20 全检查，v1.18.0 加 E14 回测数据偏差 + v1.19.0 加 E15 LLM 前瞻偏差 + v1.32.0 E15 扩展 A股Tradability Mask + v1.20.0 加 E16 因子冗余 + v1.32.0 E16 扩展归因稳定性DASH + v1.21.0 加 E17 因果验证声明 + v1.22.0 加 E18 LAP 前瞻污染检测 + E19 因子构造偏差审计 LIB + v1.23.0 加 E20 RMT 去噪因子相关性矩阵审计；G2 v1.32.0 扩展 parameter_stability_region cliff 检查）
- [ ] capability_lookup.py 扩展扫描范围覆盖 12 业务注册表
- [ ] session_log_schema.yaml 加"必读注册表"检查项
- [ ] 16 号文档 §2 迁注册表并降级为 why 层（注意第5类 reversal 非 structure）
- [ ] dataflow_graph_registry.yaml 改名 + sources 段扩展（DS 实际 76 条 DS-001~076，v1.1.1 全量确认）
- [ ] P1/P2 施工时 entry 变更走 §4.9 EVOLVE_ENTRY，衰减适应走 §4.12 ADAPT_STRATEGY，退役走 §4.10 RETIRE_ENTRY，schema 演进走 §4.11 EVOLVE_SCHEMA，上线晋升走 §4.13 PROMOTE_ENTRY，回滚走 §4.14 ROLLBACK_ENTRY，依赖解析走 §4.15 DEPENDENCY_RESOLVE，YAML→DB 迁移走 §4.16 MIGRATE_REGISTRY（v1.11.0 算法体系完整闭环），版本对比/兼容性判定走 §4.18 DIFF_ENTRY（v1.13.0 横切查询），上线后渐进式部署走 §4.13 Shadow→Canary→Full（v1.10.0）

## 10. 数据来源映射表

| 注册表 | 文档来源 | 代码来源 | 现有注册表/数据 |
|---|---|---|---|
| factor_registry | 15/25 号 | src/zephyr/factor/（6 .py + 子目录，v1.1.0修正：原ashare/15子目录不存在） | dataflow DS-015+（总 76 条） |
| strategy_registry | 20/24/25/26/27/22 号 | src/zephyr/governance/strategies/ | — |
| technical_indicator_registry | 16 号 §2 | src/zephyr/factor/technical_indicators/（6 .py，第5类reversal非structure） | — |
| universe_registry | 24/25/26 号 | src/zephyr/signal_ashare/ + ex_core/ | — |
| benchmark_registry | 25/52 号 | src/zephyr/data/implementations/akshare_provider.py | — |
| cost_model_registry | 52 号 §G1, 40 号 | src/zephyr/backtest/core/engine_base.py | — |
| execution_algo_registry | 40 号 | src/zephyr/ex_sor/（6算法：TWAP/VWAP/ICEBERG/POV/IS/ALT） | — |
| risk_limit_registry | 35/36/37/32 号 | src/zephyr/risk/（v1.1.0修正：删config/risk_register.yaml，该文件是基础设施风险非交易限额） | — |
| data_asset_registry | 15 号 | config/.env.qmt | dataflow_graph_registry.yaml（改名扩展，DS-001~076 共 76 条） |
| chart_pattern_registry | — | src/zephyr/factor/technical_indicators/ + signal_ashare/ | — |
| field_dictionary | — | src/zephyr/shared/contracts/ | frontmatter_field_registry（不合并） |
| experiment_registry | 51 号 | src/zephyr/backtest/ | — |

## 11. YAML → DB 迁移路径

**现阶段**（因子<500 / 实验<5000）：YAML 真源入 git，schema 按 DB 表设计预留迁移。

**迁移触发**（任一）：
- 因子 >500
- 实验 >5000
- 出现并发写需求

**迁移后**：
- 复用 depgraph PostgreSQL 实例（postgresql://localhost:5432/depgraph）
- YAML 降级为"导出快照"（定期生成不入 git）
- 混合模式：结构化元数据（编号/状态/关系）YAML；大规模时序数据（IC 历史/回测结果/每日快照）进 ClickHouse/PG 不入 git

> 💡 **因子时序存储用窄表格式（v1.6.0 新增，对标 [DolphinDB 2026 金融数据存储最佳实践](https://docs.dolphindb.com/en/2.00.16/Tutorials/financial_data_storage.html)）**：factor_registry 迁移 DB 后，因子**值时序数据**（非 registry 元数据）推荐用**窄表**（narrow format：`timestamp, security_id, factor_name, factor_value` 四列）而非宽表（每因子一列）。窄表优势：① 退役因子只删行不删列（DDL 无锁）；② 新增因子只插行不改表结构；③ 按因子名更新只改相关行；④ `PIVOT BY` 转 panel 格式做多因子查询（DolphinDB 并行优化）。**注意**：此仅适用于因子**值时序存储**（如 IC 历史/每日因子值），registry 元数据（编号/schema/状态）仍用 §4 原则2 的标准 entry_schema 表结构。分区策略建议：日线因子按 `year + factor_name` 分区，分钟级按 `month + factor_name` 或 `day + factor_name`（DolphinDB 推荐 500 symbol 量级）。个人项目 PG 阶段可用 `PARTITION BY LIST (factor_name) + date_trunc('year', trade_date)` 模拟。

**对标**：Feast（YAML 定义 + SQLRegistry 运行时）/ MLflow（代码配置 + DB backend）

> 🎯 **2026 YAML→DB 混合模式共识（v1.2.0 新增）**：2026 业界已形成 **"最小引导 YAML + DB 存储运行时配置"** 混合模式共识——Feast Feature View Versioning（2026-03-31）即典型：YAML 定义 FeatureView schema（手写真源入 git），`feast apply` 时自动写入 SQL Registry 的 `feature_view_version_history` 表（运行时配置入 DB），版本快照自动追踪。MLflow 3.15 同理：代码配置 + DB backend（runs/metrics/artifacts 入 DB，experiment 元数据可 YAML 导出）。
>
> **对本项目 12 注册表的启示**：
> - **现阶段（YAML 阶段）**：12 注册表全部 YAML 真源入 git，schema 按 DB 表设计（id/created_at/updated_at/version/status）预留迁移。git diff/history 天然提供版本追踪（替代 Feast 自动快照），PR review 提供治理（替代 DB ACL）。
> - **迁移触发后**：结构化元数据（编号/状态/关系/variant_of）仍 YAML 入 git（SSoT 真源）；大规模时序数据（IC 历史/回测结果/每日快照/衰减扫描记录）进 ClickHouse/PG 不入 git。这与 Feast "YAML 定义 + SQLRegistry 运行时" + MLflow "代码配置 + DB backend" 完全对齐。
> - **版本管理演进路径**：YAML 阶段 git diff → DB 阶段 `version` 字段 + `version_pin` 回滚（Feast `@v<N>` 模式）。factor/strategy schema 已预留 `version`/`version_pin` 字段（§6.1.1/§6.1.2）。
>
> **个人项目判断**（O4/O10 过度工程审查）：因子<500/实验<5000 远未触发迁移阈值，YAML + git 是当前最优解。SQLite 看似省事但失去 git diff/version/PR review 治理能力（裁定 3 已定）。schema 按 DB 表设计的成本极低（仅多 id/created_at/updated_at/version/status 字段），未来迁移省事，不算过早规划。

> 🔧 **迁移施工算法**（v1.11.0 新增）：本节描述了迁移的"触发条件 + 混合模式 + 窄表存储"，但迁移施工步骤见 **§4.16 MIGRATE_REGISTRY 算法**（R1-R7 七阶段渐进式迁移 + R4/R7 双 gate），确保零数据丢失 + 可回滚。迁移触发时按 §4.15 construct_order 的**逆序**逐表迁移（experiment 先迁，universe 最后迁），被依赖方后迁避免 FK 指向未迁移表的中间态。

## 12. 下一步行动

### P1-A（被测对象三件套，策略开发核心）
1. `factor_registry.yaml` — 从 src/zephyr/factor/（6 .py + 子目录，v1.1.0修正路径）反查登记，MVP 先登记 momentum/value/intraday/alpha_signal/bus_factor 5 类已实现因子
2. `strategy_registry.yaml` — 从 20/24/25/26/27 号文档登记 6 类策略
3. `technical_indicator_registry.yaml` — 16 号 §2 迁入（第5类 reversal 非 structure），16 号降级 why 层

### P1-B（交易/风控/数据/图形）
4. `execution_algo_registry.yaml` — 40 号 6 算法提取（TWAP/VWAP/ICEBERG/POV/IS/ALT，v1.1.0修正）
5. `risk_limit_registry.yaml` — 从 src/zephyr/risk/ 提取 9 类限额（删 config/risk_register.yaml 误引，v1.1.0修正）
6. `data_asset_registry.yaml` — 改名 + sources 段扩展，**ruling_registry 登记改名（S6 未落实，必须补齐）**，DS 全量反查确认数量
7. `chart_pattern_registry.yaml` — MVP 先做 candlestick_pattern + chart_pattern 2 类（O6 裁剪），8 大类 schema 保留按需填充

### P2（数据治理 + 实验）
8. `field_dictionary.yaml` — contracts/ 提取数据字段，补 sensitivity/freshness/notes 三字段（2026 dbt 对标）
9. `experiment_registry.yaml` — 等 51 号 MLflow 退役决策（待定 E1）后施工

每批施工同步：registry_of_registries 登记 + AGENTS.md 显化 + ARCH-BREG-001 进度更新。

## 13. 修订记录

| 版本 | 日期 | 修订内容 | 审查依据 |
|---|---|---|---|
| v1.0.0 | 2026-08-10 | 初版创建，P0 三件套落盘，12 注册表 schema 定稿，8 核心裁定 + S1-S6 修正 | business_registry_consolidation_plan.md 施工方案 |
| v1.1.0 | 2026-08-10 | **深度审查修正 8 处硬错误 + 新增过度工程审查 + 2026 实践对标** | 全网搜索 2026 最佳实践 + 代码反查 + 注册表交叉验证 |
| v1.1.1 | 2026-08-10 | **循环审查第 1 轮：DS 计数 DS-030+→DS-076（76条）+ cost_model YAML 同步完成 + schema 注释修正** | 全量 grep dataflow_graph_registry.yaml + YAML/文档交叉验证 |
| v1.2.0 | 2026-08-10 | **施工环节流程算法补全 + schema 增强 + 2026 实践对标深化**：新增§4.5 施工流程算法/§4.6 交叉引用矩阵/§4.7 验证审计算法/§4.8 生命周期管理流程；增强 8 个 schema（lookback_period/benchmark_id/warmup_period/cooling_period/version_pin/decay_detection 等字段）；补充 Feast Feature View Versioning/策略10阶段生命周期/pandas-ta/CNN+TA-Lib/EU AI Act/MLflow 3.15/square-root 律实证；更新§11 YAML→DB 混合模式共识 | 全网搜索 2026 最新实践（Feast/MLflow/Alexander&Fabozzi/Vibe-Trading）+ 2026-07 平方根律论文 |
| v1.3.0 | 2026-08-10 | **施工算法体系闭环 + 衰减检测多检测器 + 回测过拟合检测 + Schema 演进治理**：新增§4.9 变更管理算法 EVOLVE_ENTRY/§4.10 退役算法 RETIRE_ENTRY/§4.11 Schema 演进算法 EVOLVE_SCHEMA；§4.7 审计算法补 E8 循环引用/E9 日期逻辑/E10 必填空值；§4.8 衰减检测补 CUSUM/Page-Hinkley/BOCPE 三检测器 2/3 投票；§7.2 experiment_registry 补 PBO/DSR/PSR 回测过拟合检测；§4 通用原则补第 11/12 条；§14 待定问题补 C1 | 全网搜索 2026-08 最新研究（mathandmarkets/quantt.ca/backtest-guard/Soloviov PBO/Confluent Schema Registry/theFactory/datalakehouse/jsonic）|
| v1.4.0 | 2026-08-10 | **施工算法体系完整闭环 + 衰减后适应 + 跨维度检测器 + 数据质量监控 + 版本策略增强**：新增§4.12 ADAPT_STRATEGY 衰减后适应算法（填补 检测→适应→退役 三环节中间缺口）；§4.8 补 profit_factor/z_score 跨维度检测器 + 更新 MVP 决策；§4.7 补 E5b commit绑定检查 + E11 数据质量监控登记检查；§4 原则9 补 Immutable Version 选项（apxml 4 策略对比）；§4.11 补 schema 文件级版本管理（theFactory v1→v2 新文件）；factor/strategy schema 补 data_quality_policy/null_rate/drift_psi/drift_ks/range_bounds + adaptation_level/last_refit_at/baseline_sharpe + code_commit 字段；§9.4 验收更新；§14 待定问题补 F1 | 全网搜索 2026-08 最新研究（mathandmarkets Part82/nexusfi/trendsandbreakouts/arXiv:2602.10785/PineForge/apxml/metricgate/RisingWave/beefed.ai）|
| v1.5.0 | 2026-08-10 | **ADAPT_STRATEGY 数学+经验双驱动 + 衰减原因分类 + baseline 保存 + PBO 分层解读**：§4.12 补 Step 0 baseline 完整性校验 + Step 1.5 衰减原因分类驱动决策（Five Horsemen，crowding/overfitting/tech→直接退役，regime/depletion→refit）+ 三选一经验决策矩阵（Reoptimize/Pause/Retire）+ 6 类 review triggers 经验清单；§4.7 补 E12 baseline 保存完整性检查（live+ 策略 baseline 字段齐全）+ 修正 E11 缩进错误；§4.8 补衰减原因分类表（Five Horsemen of Edge Decay）+ 经验数据补充（127 策略统计）+ 监控频率指导（monthly/weekly/daily）；§7.2 补 PBO 5 层分层解读（usekeel.io，PBO>0.5→overfitting→直接退役映射）；strategy schema 补 baseline_expectancy/win_rate/profit_factor/max_drawdown/trade_frequency + decay_cause + decay_scan_frequency 字段；§9.4 验收更新；§14 待定问题补 G1 | 全网搜索 2026-08-03 最新研究（LuxAlgo Edge Decay/smartfinancedata 127策略/Pomegra Edge Decay/usekeel.io PBO 分层）|
| v1.6.0 | 2026-08-10 | **PSR/DSR 排序修正 + Plateau-Robustness 选择原则 + honest-backtest 7层验证 + KRI 6角色治理 + 版本可复现性三要素 + 鲁棒CUSUM + RisingWave 静默失败**：§7.2 补 Soloviov 2026-06 Plateau-Robustness 控制实验（PSR AUC 0.81 > DSR 0.79，修正"PSR仅为DSR前身"低估；plateau heuristic 是选择原则非独立检测，OOS Sharpe +0.12/+0.31）+ honest-backtest 7层验证框架（含 Layer 7 对抗验证"AI杀死发现"）+ schema 补 plateau_score/adversarial_result 字段；§6.2.2 补 KRI Governance 6角色分离职责模型（阈值放宽需更高级签批+持续违约协议，个人项目映射2主体4职能）；§4.12 Step 3b 补 Soloviov plateau centroid 量化验证；§4 原则9 补版本可复现性三要素（code_commit+source_uri/transform_script_hash/labeler_id+materialization_ts，MLflow bundling 对标）+ Atlan immutability 对标；§4.8 补 A股重尾分布鲁棒CUSUM（GSA-LLR分数幂基）+ RisingWave 三种静默失败模式；§4.7 修正 E12 缩进bug（原嵌套E11 else内）+ E11 补 freshness 检查；§14 补 G1 decay_cause 诊断方法 | 全网搜索 2026-08-10 最新研究（Soloviov plateau-robustness/honest-backtest 7层/risktemplate KRI 6角色/beefed.ai feature registry/MLflow 3.15.1/arXiv GSA-LLR/RisingWave feature pipeline/Atlan immutability）|
| v1.7.0 | 2026-08-10 | **执行算法反博弈+TCA双报告+图形识别Simplicity Wins+CNN+LSTM Hybrid+反Look-Ahead Bias+RETIRE级联响应**：§6.2.1 schema 补 anti_gaming/tca_metrics 字段 + 反博弈随机化（marketmaker.cc 2026-07：Poisson-ish非时钟，确定性切片被抢跑）+ POV内生性公式（x=γ/(1-γ)·M，γ=0.5发散，验证40号≤5%约束）+ TCA双报告（iotdigitaltwinplm 2026-06：VWAP slippage+IS回答不同问题，禁止只报好看的）；§6.2.4 schema 补 cnn_lstm_hybrid 变体 + "Simplicity Wins"原则（arXiv:2605.00875：原始K线+4层CNN AUC 0.892>ResNet/ViT，price-only>含指标，128×128>224×224）+ CNN+LSTM Hybrid一致优于独立（mental-momentum 2026-06）+ 反Look-Ahead Bias归一化约束（backward-only，禁止global_minmax）；§4.10 RETIRE_ENTRY 补级联响应定义（原v1.3.0仅alert未定义依赖方行动→缺口，现按类型分派：strategy→review_required+迁移建议，factor→自动review+迁移指标引用，审计日志记录级联响应） | 全网搜索 2026-08-10 最新研究（marketmaker.cc TWAP/VWAP/POV反博弈/iotdigitaltwinplm VWAP架构/arXiv:2605.00875 Simplicity Wins/mental-momentum CNN+LSTM/Apicurio Registry生命周期）|
| v1.8.0 | 2026-08-10 | **PROMOTE_ENTRY 上线晋升算法（填补§4.9引用缺口）**：新增§4.13 PROMOTE_ENTRY 8门禁上线算法——G1回测验证（OOS Sharpe/回撤/周期）/G2过拟合检查（PBO/DSR/PSR/plateau）/G3风控限额（risk_limit+kill_switch）/G4Baseline保存（6字段+decay_threshold）/G5代码冻结（code_commit）/G6基准分配（benchmark_id）/G7衰减监控（detection_method+threshold+frequency）/G8人工签批（独立reviewer≠owner）；门禁非加权平均——任何一门失败即阻断；§4.9 EVOLVE_ENTRY Step 1 status分支更新（candidate→active delegate §4.13，active→deprecated delegate §4.10）；对标 opennash 2026-06 7-gate（"gates not weighted average"）+ MLflow 2026-05 验证门 + thirstysprout 2026-07 生产就绪签批 + KRI治理分离职责；个人项目映射 AI自检7门+人工1门，G3/G8不可降级 | 全网搜索 2026-08-10 最新研究（opennash 7-gate/MLflow MLOps pipeline/thirstysprout production readiness/CSDN Feature Store审批流程/beefed.ai feature registry governance）|
| v1.9.0 | 2026-08-10 | **回滚算法+依赖解析算法闭环（算法体系完整闭环）**：新增§4.14 ROLLBACK_ENTRY回滚算法（7步：触发源判定→目标版本定位→仓位处置→衰减监控重置→审计日志→7天冷却防flip-flop→通知，填补PROMOTE_ENTRY逆向缺口，对标metricgate 2026-04 rollback triggers+frontierledger automated rollback）+ §4.15 DEPENDENCY_RESOLVE依赖解析算法（Kahn's拓扑排序construct_order确定12表施工顺序/transitive_deps查传递依赖链/impact_range算变更影响范围，补全§4.6 FK矩阵的算法层支持）；§4.4导航图骨架（v1.10.0 完善为算法体系导航图） | 全网搜索 2026-08-10 最新研究（metricgate rollback triggers/frontierledger canary rollback/Kahn's algorithm拓扑排序/Apicurio Registry依赖分析）|
| v1.10.0 | 2026-08-10 | **算法体系导航图+语义漂移+SHA256 manifest+参数漂移+渐进式部署**：新增§4.4算法体系导航图（11算法按生命周期6阶段分组：建→上→改→测→应/回→退+调用矩阵+关键依赖关系，解决"11算法无全局导航"问题）+ §4.7补E13语义漂移检查（semantic_contract/null_semantics/default_fill_policy三检查，对标oracles.cloud 2026-01数据契约3类漂移schema+statistical+semantic+neojn 2026-05特征存储漂移"系统继续服务只是悄悄变错"）+ §4原则9补SHA256 manifest选项（bit-level reproducibility+tamper detection，对标OmniBioAI ModelHub 2026-08-08 sha256sums.txt+Ollama content-addressable storage三原则+model-secure ECDSA签名；个人项目git commit hash天然提供追溯，DB+监管阶段可选升级）+ §4.8补参数漂移概念（eastmoney 2026-07-18中文源"系统不是在瞬间崩溃而是在不知不觉中腐烂"——市场特征缓慢持久变化非价格突变，胜率40%策略连亏5-6笔统计正常 vs 参数漂移前兆几乎无法区分，启示CUSUM慢漂移敏感+monthly扫描）+ §4.13补渐进式部署Shadow→Canary→Full三阶段（对标nexus-trade-engine #162 2026-04 shadow+canary数据模型+metricgate 2026-04配对观测vs独立样本方差对比+frontierledger 1-5%资金渐进+NautilusTrader 2026-08-09影子模式沙箱"只做决策不下单"） | 全网搜索 2026-08-10 最新研究（oracles.cloud data contracts/neojn feature store drift/OmniBioAI ModelHub/Ollama model registry/eastmoney 可进化交易系统/nexus-trade-engine #162/metricgate shadow vs canary/frontierledger canary trading/NautilusTrader 影子模式/ManifoldKit #1934对抗审查）|
| v1.11.0 | 2026-08-10 | **YAML→DB迁移算法闭环+MinBTL回测过拟合第4方法**：新增§4.16 MIGRATE_REGISTRY算法（R1-R7七阶段渐进式迁移：PG表创建→数据导入+YAML fallback→CLI PG-first→R4完整性验证gate→双写模式→R6 YAML数据删除(不可逆,28天清洁期+git快照)→R7迁移后审计gate，对标longterm-wiki #2076 R1-R6 playbook+mvpfactory.io Expand-Contract vs Blue-Green+youngju.dev Schema Migration Tools，补全§11迁移路径的算法层，12算法体系完整闭环"建→上→改→测→应/回→退→迁"7阶段）+ §4.4导航图更新为12算法7阶段（新增阶段7迁+调用矩阵补MIGRATE_REGISTRY行+关键依赖补R1/R5/R7复用关系）+ §7.2 experiment_registry schema补min_trl_years字段（Minimum Track Record Length，Bailey&López de Prado 2014，公式MBL=0.5×(Z_α×σ_ann/SR_ann)²，回答"需多少年数据才能信任此Sharpe"）+ 回测过拟合检测三方法→四方法（PBO+DSR+PSR+MinBTL，对标backtestbase 2026-01+auditzk 2026-03+digitalninjasystems 2026-06+quantskills/skill-backtest-overfit 2026-07） | 全网搜索 2026-08-10 最新研究（longterm-wiki #2076 YAML→PG迁移/mvpfactory.io 零停机schema迁移/youngju.dev Flyway-Liquibase-Alembic-Atlas对比/backtestbase MinBTL/auditzk MinTRL/digitalninjasystems Minimum Backtest Length/quantskills skill-backtest-overfit）|
| v1.12.0 | 2026-08-10 | **2026-08-10最新研究对标+回测过拟合第5方法MTC+8项算法升级**：新增§4.17最新研究对标补充（8项：双曲衰减模型α(t)=K/(1+λt)估策略剩余寿命+BOCPD第4贝叶斯检测器+Wasserstein Distance漂移检测+pgroll零停机迁移+PubGrub版本约束求解+字典序最小拓扑+Data Contracts vs Schema Registry分层+multigrid三层eval gate+Feast OpenLineage血缘）+ §7.2回测过拟合检测四方法→五方法（+Multiple Testing Correction：White's RC/Hansen SPA/Romano-Wolf/MCS/BH-FDR，对标studentone.tech 2026-06九道门+metricgate 2026-06 MCS+marketmaker.cc 2026-06 DSR对比+arXiv:2604.15531 Falsification Audit）+ §13补v1.11.0修订明细R37-R39+§14待定问题补H1/I1 | 全网搜索 2026-08-10 最新研究（arXiv:2512.11913双曲衰减/RegimeChange R包2026-08/ruptures L1Potts 2026-05/Tsaknaki BOCPD 2025/futureagi Wasserstein/royxforge drift 2026-07/bytebase pgroll 2026-07/pubgrub-rs 2026-03/spacecomplexity 字典序拓扑 2026-05/soda.io Data Contracts 2026-06/Confluent migration rules/multigrid 2026-08-08/Flagger 2026-07/Feast OpenLineage 2026-01/Snowflake 2026-07/studentone.tech 9-gate 2026-06/metricgate MCS 2026-06/marketmaker.cc DSR对比 2026-06/arXiv:2604.15531 Falsification 2026-04）|
| v1.13.0 | 2026-08-10 | **第二轮缺口审计+版本差异算法DIFF_ENTRY（13算法体系完整闭环）**：新增§4.18 DIFF_ENTRY版本差异横切查询算法（5步：字节级快判BLAKE3→字段级三分类additions/modifications/removals→语义分类metadata/schema_sig/code_ref/status→兼容性判定semver bump映射MAJOR/MINOR/PATCH→breaking变更查依赖方，对标IETF netmod YANG Schema Comparison 2026-05+AST/byte-hash双策略2026-04+schema.biz三桶2026-04，填补EVOLVE_ENTRY/EVOLVE_SCHEMA/PROMOTE_ENTRY三者共需"版本对比"无统一算法的缺口）+ §4.19第二轮缺口审计与对标（10缺口领域逐项映射：1项硬缺口已补DIFF_ENTRY/4项已覆盖通知内联+反向血缘§4.15+原子批量git commit+FK验证§4.6+E4/5项DEFER记录DB阶段升级路径候选提案+GC+复活+健康监控+搜索，符合过度工程处理原则）+ §4.4导航图更新12算法→13算法（+横切查询DIFF_ENTRY行+调用矩阵+关键依赖）| 全网搜索 2026-08-10 第二轮（IETF netmod YANG schema comparison 2026-05/AI Agent Schema Diff AST+BLAKE3 2026-04/schema.biz breaking-change 2026-04/tapps-brain feasibility 2026-03/ict-engine evidence-chain 2026-07/sigma-guard sheaf cohomology 2026-05/SHACL-DS 2026-05/DataHub MCL 2026-03/Apicurio EDA 2026-07/CAMEL-24172 2026-07/TIN temporal provenance 2026-01/OpenMetadata impact 2026-07/openclaw Doctor removeAfter 2026-08/Docker registry GC 2026-07/cinatra R3 restore 2026-07/IETF regext RGP 2026-05/noopsschool catalog SLI 2026-02/acceldata quality triad 2026-04/Lance BatchCommitTables 2026-06/Apicurio multi-table 2026-03/Doris 2PC 2026-07/Algolia dynamic facets 2026-07/base14 metric registry 2026-01）|
| v1.14.0 | 2026-08-10 | **A股2026监管变更+算法一致性修复+第三轮研究**：§4.20 A股2026年7月监管变更影响（交易规则2026修订7/6生效：ST涨跌5→10%+盘后固定价格扩围+SSE基金收盘集合+创业板做市商+创业板大宗盘中实时；程序化交易细则7/7生效：高频认定15笔/秒+撤单率≤15%+报单停留≥50µs——execution_algo/risk_limit/universe/cost_model/benchmark 5表 schema MUST 预留合规字段，印花税/过户费/整手确认未变）+ PROMOTE_ENTRY Gate1加min_trl_years交叉校验+Gate2加MTC检查（v1.11.0/v1.12.0字段与v1.8.0算法一致性修复）+ §4.17② BOCPE误判频率派事实错误修正（BOCPE=BOCPD已是贝叶斯，增量=score-driven变体非第4检测器）+ §4.21第三轮研究7项（SR26-2替代SR11-7/NautilusTrader替代Backtrader/Double-selection LASSO/华创LightGBM三标签/AH-HMM元regime层/Feast0.64数据质量/meta-labeling方向×仓位分离）| 全网搜索 2026-08-10 第三轮（上交所上证发2026 41号 2026-07-06/程序化交易细则 2026-07-07/美联储SR26-2 2026-04-17/bullalert NautilusTrader 2026-05/LedgerMind 12平台 2026-04/arXiv double-selection LASSO 2026-05/华创LightGBM 2026-03/MDPI AH-HMM 2026/AGasthya HSMM 2026-07/Feast0.64 2026-06/Nova meta-labeling 2026-04）|
| v1.15.0 | 2026-08-10 | **局域网关闭补齐+高频阈值核实+第四轮研究流程治理**：§4.20③ 局域网行情通道关闭+交易网关管理指引（2026-07-31局域网正式关闭/广域网双向时延≥2ms地板/2026-08-31网关指引施行/深交所待切换——v1.14.0 漏掉的第三项实盘合规红线，execution_algo补latency_floor_ms+network_type/cost_model补slippage_regime/data_asset补latency_profile+colocation_eligible）+ §4.20② 高频阈值核实说明（中基协2026-07-27研报300笔/秒系旧规误引，新规15笔/秒2026-04-07第一阶段+2026-07-07全面落地，本表15笔/秒现行有效）+ §4.22第四轮研究5项（AlphaSchema LLM因子挖掘5字段语义计划/Agentic Workflows架构承重件原则/证据SHA256+allowed_use治理模式/数据契约独立模块/量化Agent竞争转向）聚焦研究流程治理 | 全网搜索 2026-08-10 第四轮（新浪财经2026-07-28局域网关闭/东方财富2026-08-05广域网时延/第一财经2026-08-05深交所待切/证券时报2026-07-28/Waton AlphaSchema 2026-08-10/Kinlay Agentic 2026-05/nathanku3-hue Quant spec 2026-06/stock_good 2026-06/华夏时报PandaAI 2026-08）|
| v1.16.0 | 2026-08-10 | **CPCV升级回测过拟合六方法+价格笼子schema+A股微观结构+第五轮研究**：§7.2 回测过拟合五方法升级六方法（新增CPCV组合净化交叉验证——López de Prado核心方法，C(N,k)条OOS分布而非walk-forward单条，purge+embargo防泄漏，catastrophic-veto门禁——arXiv:2603.09219 AlgoXpert 2026-03+noonbarbari 2026-07+tradingstrategy.ai）+ §4.13 PROMOTE_ENTRY G2门禁新增CPCV检查（cpcv_worst_max_dd>0.15=catastrophic-veto一票否决+std/mean>0.5切法敏感性阻断）+ §4.23第五轮研究4项（AlgoXpert IS-WFA-OOS三阶段协议/EU AI Act 2026-08-02可解释AI合规/A股价格笼子+T+1+涨跌停不可成交/决策审计append-only ledger）+ execution_algo_registry schema MUST新增price_cage_config+t_plus_1+limit_up_down_untradable三字段（40_execution_broker v2.6.0已实现check_price_cage，schema对齐）| 全网搜索 2026-08-10 第五轮（arXiv AlgoXpert 2026-03/noonbarbari CPCV 2026-07/tradingstrategy.ai/beefed.ai 2026/ceta-research 2026-03/finantrix EU AI Act 2026-08-08/Dataiku 2026-06/theneuralbase 2026-04/CSDN价格笼子 2026-08-09/sina新规 2026-07-06/toutiao AI量化避坑 2026-08）|
| v1.17.0 | 2026-08-10 | **P0代码bug修复+仓位管理+A股特色数据第六轮研究**：§4.13 PROMOTE_ENTRY G1/G2门禁P0代码bug修复（字符串拼接须str()转换避免TypeError+CPCV mean<=0须直接FAIL而非跳过——Agent审查发现）+ §4.24第六轮研究5项填补仓位管理和A股特色数据两个对标空白（Conformal Kelly conformal prediction interval作为fractional Kelly scale+drawdown dial风控/Kelly+ML协方差改进Marcenko-Pastur denoising+HRP+detoning+SCIRP A股风险约束Kelly/Sizing Shootout A/B框架OBSERVE-only/国泰海通A股高频因子2026多空7-16%/龙虎榜Level-2数据源license_type治理AKShare学术用途不可商用）| 全网搜索 2026-08-10 第六轮（arXiv Conformal Kelly 2026-08-02/quantsingularity Kelly-ML 2026-06/SCIRP风险约束Kelly 2025-03/crucible-backtester sizing shootout 2026-07/国泰海通高频因子 2026-08-10/CSDN A股量化可行性 2026-08-09/sina龙虎榜 2026-07-08/toutiao量化打板博弈 2026-08-10）|
| v1.18.0 | 2026-08-10 | **回测数据偏差治理+策略组合+信号融合+归因分析第七轮研究+施工环节缺口填补**：§4.25第七轮研究4项（数据生存偏差+前瞻偏差三分类taxonomy治理/Regime-Based动量+均值回归融合/Meta-labeling方向×仓位分离/Brinson-Fachler+factor-based归因）填补前六轮"数据源头偏差"和"收益归因"两个对标空白 + §4.7新增E14回测数据偏差检查（E1-E13→E1-E14，查backtest_bias_checks三分类声明+survivorship_free/pit_available声明）+ §4.4新增跨文档职责边界（RUN_BACKTEST→52号/ATTRIBUTION→54号，避免本文档过度工程）+ data_asset_registry schema补survivorship_free/pit_available/earnings_lag_days三字段 + experiment_registry schema补backtest_bias_checks/attribution_result两字段 + strategy_registry schema补combination_strategy/meta_labeling_config两字段 | 全网搜索 2026-08-10 第七轮（digitalninjasystems 2026-05-28/thedatascientist 2026-06-10/dev.to 2026-07-06/preprints.org 2026-06-04/LobeHub 2026-07-31/digitalninjasystems 2026-05-24 regime融合/中金 2026-06-24/Neyt How-To-Backtest-Correctly 2026-03/NTU 2026-05-20/mental-momentum 2026-06-14/breakingalpha 2026-01-26/skill4agent 2026-02-20/pa package 2026-04-25/marketopia 2026-05-04/CSDN绩效归因 2026-08-09）|
| v1.19.0 | 2026-08-10 | **LLM时代量化治理第八轮研究+施工环节缺口填补**：§4.26第八轮研究5项（LLM前瞻偏差治理Look-Ahead-Bench memorization leakage/数据侧脱敏协议KTD-FIN 4-level masking/因子语义抽象层AlphaSchema 5字段schema_plan/策略来源标记+LLM蒸馏TiMi ICLR 2026/Regime-aware因子筛选Alpha-R1 8B RL）填补前七轮"LLM时代量化治理"对标空白 + §4.7新增E15 LLM前瞻偏差检查（E1-E14→E1-E15，查llm_lookahead_check_result+llm_training_cutoff/lookahead_test_method声明，KTD-FIN 4-level masking协议）+ data_asset_registry schema补llm_training_cutoff/lookahead_test_method两字段 + experiment_registry schema补llm_lookahead_check_result字段+attribution_result注释补VIF screening建议（KTD-FIN 9 VIF-screened style factors）+ factor_registry schema补schema_plan字段（AlphaSchema 5字段event/context/qualities/direction/output）+ strategy_registry schema补origin/distilled_to_code两字段+combination_strategy.regime_detector enum补news_aware（Alpha-R1风格）+ §4.4导航图E1-E14→E1-E15 + §4.5/§4.16/§4.19/§9.4 E1-E13→E1-E15 全量同步 + §4.16 MIGRATE_REGISTRY R7审计gate自动覆盖E1-E15 | 全网搜索 2026-08-10 第八轮（Look-Ahead-Bench arXiv:2601.13770 2026-01/KTD-FIN arXiv:2605.28359 2026/AlphaSchema ubos.tech 2026-08-01/TiMi ICLR 2026 国联民生金工综述/Alpha-R1 arXiv:2512.23515 2026-12-29/CSDN LLM驱动量化 2026-08-09/PeerJ Adaptive LLM Multi-Agent 2026-03-12）|
| v1.20.0 | 2026-08-10 | **策略容量检验+因子冗余检测第九轮研究+施工环节缺口填补**：§4.27第九轮研究3项（策略容量Square-Root Market Impact模型+参与率红线/因子冗余三维度signal-return-exposure correlation/EntroPy deployability hard filters）填补前八轮"实盘可部署性"和"因子库多样性"两个对标空白 + §4.13 PROMOTE_ENTRY新增G9容量检验门禁（G1-G8→G1-G9，查capacity_aum_limit/participation_rate_limit/market_impact_model）+ §4.7新增E16因子冗余检查（E1-E15→E1-E16，查correlation_group/redundancy_status声明+同组independent因子）+ strategy_registry schema补capacity_aum_limit/participation_rate_limit/market_impact_model三字段 + factor_registry schema补correlation_group/redundancy_status两字段 + §4.4导航图E1-E15→E1-E16+8门禁→9门禁 + §4.5/§4.16/§9.4全量同步 | 全网搜索 2026-08-10 第九轮（breakingalpha 2026-01/linitics 2026-04/hedgeco 2026-04/daytrading 2026-02/dyj.live 2026 公募量化/EntroPy 2026-05 redundancy.py/factordbms Orthogonality Analysis/CSDN 2026-07-13 因子去冗余/QuantGPT Self-Correlation）|
| v1.21.0 | 2026-08-10 | **DSR鲁棒性带+因果验证声明第十轮研究+施工环节缺口填补**：§4.28第十轮研究12项（有效trial数鲁棒性带/causal-quant因果验证/Evidently-NannyML标签延迟分层/Kyle lambda流动性/Apicurio版本状态机/CRISP组合构建/HAR-LSTM波动率/Confluent五要素契约/PatchTST/TreeSHAP-EBM/OpenMetadata/GE-dbt-Soda）填补前九轮"DSR失败模式"和"因果验证"两个对标空白 + §4.13 G2新增鲁棒性带检查（trial_correlated=True无bootstrap=阻断+n_trials>10须报告effective_trial_count_band区间）+ §4.7新增E17因果验证声明检查（E1-E16→E1-E17，查causal_graph声明，warning级MVP不阻断）+ experiment_registry schema补trial_correlated/effective_trial_count_band/bootstrap_test_passed三字段 + factor_registry schema补causal_graph字段 + §4.4导航图E1-E16→E1-E17 + §4.5/§4.16/§9.4全量同步 | 全网搜索 2026-08-10 第十轮（Soloviov 2026-07 deflated-sharpe-search/causal-quant v0.4.1 2026-07/CIR-ACTIVA arXiv:2608.03715 2026-08/pythondatabench 2026-05/conduktor 2026-07/microalphas 2026-06/Aldridge arXiv:2607.01377 2026-07/Apicurio 3.3.x/Confluent v8.3/arXiv:2604.23833 CRISP/JRFM 2026-19-77/mental-momentum 2026-06/aibuzz 2026-06/open-metadata 2026/pistack 2026-04）|
| v1.22.0 | 2026-08-10 | **GSA-LLR鲁棒CUSUM+LAP前瞻污染检测+LIB偏差审计第十一轮研究+施工环节缺口填补**：§4.29第十一轮研究4项（GSA-LLR重尾变点检测/LAP-FinCAD-CMMD LLM前瞻污染三方法/企业债LIB偏差/A股板块轮动14.8%警示）填补前十轮"重尾分布变点检测"+"模型侧前瞻偏差诊断"+"因子构造方法学偏差"三个对标空白 + §4.7新增E18 LAP前瞻污染检测+E19因子构造偏差审计LIB（E1-E17→E1-E19，查lap_check_result/lib_audit/ex_post_filter_audit声明，warning级MVP不阻断）+ §4.8 DECAY_SCAN_MULTI检测器1增重尾自适应分支GSA-LLR（γ₄≥6自动切换）+ experiment_registry schema补lap_check_result字段 + factor_registry schema补lib_audit/ex_post_filter_audit两字段 + risk_limit_registry schema补stage/response_strategy两字段 + decay_detection_method enum补gsa_llr_cusum选项（factor+strategy两表）+ §4.4导航图/§4.5/§4.16/§9.4全量同步E1-E17→E1-E19 + §13修订明细R59-R62 | 全网搜索 2026-08-10 第十一轮（GSA-LLR arXiv:2605.23419v2 2026-05-27/LAP arXiv:2512.23847v2 2026-06-12/FinCAD arXiv:2605.24564 2026-05-23/MemGuard-Alpha CMMD arXiv:2603.26797/企业债因子动物园 arXiv:2604.07880v1 2026-04-09/WyckoffTradingAgent A股板块轮动 2026-07-23/Apicurio 3.3.x四阶段状态机/ISO 31000 response strategy）|
| v1.23.0 | 2026-08-10 | **RMT去噪因子相关性矩阵+非高斯回撤风险校准+Regime-Weighted Conformal VaR校准第十二轮研究+施工环节缺口填补**：§4.30第十二轮研究3项（RMT Marchenko-Pastur去噪因子相关性矩阵/RSB非高斯回撤风险校准四维决策度量/Regime-Weighted Conformal VaR压力期校准）填补前十一轮"因子冗余检测方法学质量"+"回撤阈值高斯假设缺陷"+"VaR压力期系统性误校准"三个对标空白 + §4.7新增E20 RMT去噪因子相关性矩阵审计（E1-E19→E1-E20，查rmt_denoised声明，warning级MVP不阻断）+ factor_registry schema补rmt_denoised字段 + risk_limit_registry schema补drawdown_calibration_method/var_calibration_method两字段 + §4.4导航图/§4.5/§4.16/§9.4全量同步E1-E19→E1-E20 + §13修订明细R63-R65 | 全网搜索 2026-08-10 第十二轮（EFS arXiv:2507.17211v2 2026-08-07/物理信息奇异值学习 arXiv:2601.07687v4 2026-08-02/RSB Drawdown arXiv:2608.00127v1 2026-07-31/RWC Taming Tail Risk arXiv:2602.03903v3 2026-08-03）|
| v1.24.0 | 2026-08-10 | **universe_registry生存偏差治理第十三轮研究+E14扩展+施工环节缺口填补**：§4.31第十三轮研究1项（universe PIT成分构造+退市股处理+survivorship-free）填补前十二轮"universe层生存偏差审计实现遗漏"对标空白（E14 taxonomy自v1.18.0声明universe-membership contamination但实现只查data_asset不查universe——概念正确但实现遗漏）+ §4.7 E14扩展c维度（新增universe_registry pit_constituent_construction/delisted_handling声明检查，不新增E编号避免膨胀，E14本就是回测数据偏差检查语义内聚，省E1-E20→E1-E21的6处同步churn）+ universe_registry schema补pit_constituent_construction/delisted_handling/survivorship_free三字段 | 全网搜索 2026-08-10 第十三轮（alphanume 2026-06-08 How to Build Momentum Strategy "universe is where survivorship bias enters most silently"/tickernerd 2026-08-03 methodology三锁定窗口PIT Compustat/arXiv:2603.16904 2026-03 survivorship-bias-free S&P500 universe回溯add/delete事件）|
| v1.25.0 | 2026-08-10 | **PIT字段语义+预注册协议+因子发现自动化第十四轮研究+3注册表schema批量补全+D1硬缺口闭合**：§4.32第十四轮研究3项（Assay PIT正确回测引擎as_of_date字段语义契约/AurumQ-RL MASTER-lite预注册协议成本否决+3窗3seed/R&D-Agent-Quant因子-模型协同优化）填补前十三轮"PIT字段语义引擎层空白"+"预注册流程层空白"+"因子发现自动化"三个对标空白 + §4.7 E14扩展d维度（PIT字段语义审计，不新增E编号）+ §4.13 G1增强（成本否决+IC-OOS脱钩告警，不新增G编号）+ data_asset_registry schema补as_of_date_semantics + experiment_registry schema补pre_registered/cost_vetoed/ic_oos_gap + factor_registry schema补discovery_agent + 3注册表(factor/risk_limit/strategy)批量补全v1.20-v1.23新增字段（factor 111条补7字段+risk_limit 42条补4字段+strategy 59条补7字段）+ ruling_registry裁定#223登记data_asset→dataflow_graph改名（D1硬缺口闭合） | 全网搜索 2026-08-10 第十四轮（Assay回测引擎2026-07-04 ICLR AlphaBench配套/AurumQ-RL 2026-07-17 MASTER-lite预注册协议/R&D-Agent-Quant NeurIPS 2025微软开源2026-07-23 Qlib集成）+ 审查agent施工算法完整性审查 + 注册表schema批量补全 |
| v1.26.0 | 2026-08-10 | **Wasserstein HMM+PBO误读澄清+Kyle lambda陷阱+Meta-labeling边界+v1.21遗留schema落地第十五轮研究+施工环节缺口填补**：§4.33第十五轮研究5项（Wasserstein HMM regime检测标签置换解决/PBO null=0.5误读澄清/Kyle lambda OLS slope实现陷阱/Meta-labeling仅适用discretionary模型/v1.21.0第十轮遗留schema落地）填补前十四轮"regime检测标签置换稳定性"+"过拟合检测概念校准"+"流动性因子实现陷阱"+"信号融合适用边界"+"研究段-schema落地脱节"五个对标空白 + strategy_registry combination_strategy.regime_detector enum补wasserstein_hmm选项（v1.19.0 news_aware→v1.26.0 wasserstein_hmm）+ §4.13 G2门禁加PBO null=0.5误读警示注释（PBO≈0.5=完全过拟合=硬币翻转，非0.2-0.5轻度过拟合）+ factor_registry schema补liquidity_metric字段（含Kyle lambda OLS slope实现陷阱注释：cov(log_ret,signed_flow)/var(signed_flow)非ratio）+ data_asset_registry schema补label_delay_days+drift_detector两字段（v1.21.0第十轮Evidently+NannyML标签延迟分层遗留落地）+ meta_labeling_config字段注释增强适用边界（仅discretionary/规则型主模型，end-to-end ML不适用） | 全网搜索 2026-08-10 第十五轮（arXiv:2603.04441v1 2026-02-21 Wasserstein HMM Boukardagha Columbia/marketmaker.cc 2026-07-01 PBO null=0.5 pbo-search开源/JohnGavin #627 2026-08-03 Kyle lambda=Amihud重复bug修复/QuantConnect 2026 Meta-labeling Not Silver Bullet/Aldridge arXiv:2607.01377 Kyle lambda CRSP验证/microalphas 2026-06-02 Kyle lambda guide）|

| v1.27.0 | 2026-08-10 | **ARM变点归因+Hubble AST沙箱+QUANTEVOLVER+Text+VAR双向regime+Weighted Kolmogorov重尾回测+AlphaBench评测第十六轮研究+6引擎层空白闭合**：§4.34第十六轮研究6项（ARM Attribution by Rank Maxima变点归因算法/Hubble AST验证沙箱LLM因子生成安全标准/QUANTEVOLVER RL微调vs prompt loop/Text-enhanced regime shift detection文本+VAR双向验证/Weighted Kolmogorov Metric重尾分布回测指标收敛性修复/AlphaBench ICLR2026标准化因子评测基准）填补前十五轮"变点归因层"+"LLM因子生成安全标准"+"RL微调vs prompt loop区分"+"文本+VAR双向regime检测"+"重尾分布回测指标"+"标准化因子评测基准"六个对标空白 + §4.8衰减检测流程补"步骤5：变点归因"子步骤（检测到变点后MUST调用ARM归因到具体因子坐标，Phase 2+因子数>20时启用）+ factor_registry schema补llm_safety_stack字段（{ast_validation, dsl_constrained, complexity_control, dual_channel_rag, family_aware_selection}，discovery_agent=rd_agent/efs/hubble/quantevolver时MUST声明）+ factor_registry discovery_agent enum补quantevolver选项（RL微调vs prompt loop区分）+ strategy_registry combination_strategy.regime_detector enum补text_var_dual选项（文本+VAR双向验证）+ risk_limit_registry drawdown_calibration_method+var_calibration_method enum均补weighted_kolmogorov选项（重尾策略γ₄>8 MUST启用）+ Phase 1.5+ AlphaBench 3任务体系评测不同discovery_agent因子质量 | 全网搜索 2026-08-10 第十六轮（arXiv:2608.01691v1 2026-08-03 ARM Attribution by Rank Maxima Peng-Wu-Yan-Chen-Shen 北工大+南洋理工/arXiv:2604.09601v2 2026-04-14 Hubble AST沙箱 Shi-Yan-Cai-Lv Celestial Quant Lab+UBC/arXiv:2605.15412 QUANTEVOLVER Zhang-Jia-Zhai-Xie 西北工大+UIUC/arXiv:2605.30363v2 2026-08-02 Text-enhanced regime shift Yi-Mehra-Chen-Cartlidge Bristol+Cardiff FinLLM@IJCAI2026 Long Oral/arXiv:2601.04490v1 2026-01-08 Weighted Kolmogorov Petrosyan/AlphaBench ICLR2026 Luo CityU-MLO）|
| v1.28.0 | 2026-08-10 | **Joint Falsification三值裁决+LOO风险分解+Backtest OVERFIT 5模式第十七轮研究+裁决哲学升级**：§4.35第十七轮研究3项（Joint Falsification三重门三值证伪REFUTED/SUPPORTED/INCONCLUSIVE/Leave-One-Out inherent+correlation风险贡献结构分解/Backtest OVERFIT 5模式walk_forward_divergence/regime_flip/parameter_cliff/indicator_stacking/survivorship+PF ratio+min trade count实证阈值）填补前十六轮"上线裁决三值逻辑"+"风险贡献结构分解"+"过拟合实证模式分类"三个对标空白 + §4.13 PROMOTE_ENTRY裁决逻辑增强三值分类（统计门失败+样本不足→INCONCLUSIVE继续probation/样本充分→REFUTED走RETIRE_ENTRY/全过→SUPPORTED全量上线）+ §4.13 G2增强PF ratio子检查（train_pf/oos_pf>2.0阻断/>1.5 warning）+min trade count子检查（directional<300/mean_reversion<500=warning样本不足）+ experiment_registry schema补viability_verdict+overfit_pattern两字段 + risk_limit_registry schema补risk_contribution_decomposition字段（{inherent_component,correlation_component,decomposition_method:loo/standard_rc/none}） + experiment_registry schema补pre_registered/cost_vetoed/ic_oos_gap三字段（v1.25.0声称已落地但实际未加入§7.2 schema，本轮修复） | 全网搜索 2026-08-10 第十七轮（arXiv:2607.20093v1 2026-07-22 Darmanin Hecatus Research Joint Falsification Retail Trader's Ruin/arXiv:2604.10375v1 2026-04-11 Alexander&Fabozzi UVA+JHU LOO inherent+correlation decomposition/dibi8 2026-05-25 Backtest OVERFIT 5 Typical Patterns）|
| v1.29.0 | 2026-08-10 | **Alpha发现EC综述六组件+八维自主性+GT-Score优化时反过拟合+AutoQuant双重筛查第十八轮研究+时间轴前移**：§4.36第十八轮研究3项（Alpha发现EC综述六组件框架representation/variation/fitness/selection/memory/adaptation+八维自主性评估协议search_efficiency/fitness_reliability/residual_alpha/economic_diversity/tradability/evolutionary_autonomy/market_logic_grounding/reproducibility/GT-Score优化时复合目标函数performance+significance+consistency+downside_risk泛化比提升98%/AutoQuant Stage I贝叶斯TPE调参+Stage II独立验证双重筛查数据分离）填补前十七轮"因子发现自主性评估维度"+"优化时反过拟合目标函数"+"调参-验证分离"三个对标空白 + 0项新E/G编号 + 0项schema字段落地（3项均为Phase 1.5+评估）+ 3项Phase 1.5+评估（AlphaBench八维自主性评估+GT-Score优化目标+AutoQuant Stage I/II数据分离） + experiment_registry schema补pre_registered/cost_vetoed/ic_oos_gap三字段（v1.25.0遗留修复，§7.2 schema实际落地）+ risk_limit_registry.yaml补risk_contribution_decomposition字段（v1.28.0声称已落地但YAML文件未更新，本轮修复） | 全网搜索 2026-08-10 第十八轮（arXiv:2608.01789v1 2026-08-03 Yu-Fu-Fan-Li-Gao-Xu 上海大学+西交ATAR Alpha发现EC综述/arXiv:2602.00080 2026-01-22 Sheppert Capitol Tech GT-Score JRFM/arXiv:2512.22476v3 2026-08-07 Deng 广州工商学院 AutoQuant双重筛查）|
| v1.30.0 | 2026-08-10 | **Ulcer/Calmar路径依赖疼痛+I-Star/Propagator/Algo Wheel执行冲击谱系+Custom Benchmark+Active Share基准漂移+MCP Registry别名指针第十九轮研究+路径与谱系补全**：§4.37第十九轮研究4项（Ulcer Index/Calmar/Pain Index路径依赖回撤度量编码深度×持续时间/I-Star+Propagator+Algo Wheel执行冲击模型谱系square_root/AC/i_star/propagator+实时路由/Custom Benchmark holdings_based/returns_based+active_share+style_drift检测2026大基准重置/MCP Registry promotable aliases别名指针部署模式）填补前十八轮"回撤路径依赖度量"+"执行冲击模型谱系登记"+"基准构造与漂移检测"+"部署别名指针模式"四个对标空白 + 0项新E/G编号 + 4项schema字段已落地（risk_limit_registry补pain_metric{metric_type:ulcer_index/pain_index/none,threshold,monitoring_window_days}+experiment_registry补ulcer_index+calmar_ratio+execution_algo_registry补impact_model_type enum square_root/almgren_chriss/i_star/propagator/fixed_bps/pluggable+cost_model_registry补propagator_config{decay_kernel,temp_impact_coeff,perm_impact_coeff}+benchmark_registry补construction_method+active_share+style_drift_detection三字段） + 1项治理模式验证（MCP Registry promotable aliases作为Phase 2+ DB部署指针评估MVP不实施）+ 1项跨文档边界重申（HRP-μ/CRISP组合构建算法DEFERRED至52/54号strategy_registry不实现算法） | 全网搜索 2026-08-10 第十九轮（metricgate 2026-05-20 Ulcer Index Martin 1989/algostrategyanalyzer 2026-01-27 Drawdown Guide/mlq.ai 2026 Drawdown Analysis/youngju.dev 2026-05-25 TCA Deep Dive Perold/Almgren-Chriss/Kissell-I-Star/Bouchaud-Farmer Propagator/hftradingbook 2026-06-04 Market Impact/arXiv:2603.29086v1 2026-03 MACE RL/stockalpha.ai 2026-02-17 Custom Benchmarks style drift/nasdaq.com 2026-06 Great Benchmark Reset Russell半年再平衡/MLflow 3.15.0 2026-07-31 MCP Registry promotable aliases）|
| v1.31.0 | 2026-08-10 | **Temporal Leakage测量+Causal Factor Mirage collider/jump regime持续性+证监会2026-07内幕交易合规第二十轮研究+从二值到结构**：§4.38第二十轮研究4项（Temporal Leakage Measurement从detection到measurement matched clean control+boundary detection证明pre/post-cutoff检查uninformative/Causal Factor Mirage collider比confounder更危险含collider模型更高R²+更低p-value系数符号翻转+0.08→−0.04/Statistical Jump Model+Jump-Diffusion HMM regime持续性显式跳跃惩罚+Poisson驻留时间解决标准HMM过快回归/证监会法释〔2026〕13号内幕交易司法解释14年首次修订敏感期前移+四类人群入刑减半+三大脱罪理由失效）填补前十九轮"LLM前瞻泄漏测量"+"因果设定结构审计"+"regime持续性建模"+"内幕交易合规存档"四个对标空白 + 0项新E/G编号（遵循v1.24.0/v1.30.0最小churn原则——E17扩展为"因果验证+设定结构检查"查causal_structure collider标志、E18扩展为"LAP+Temporal Leakage检测"查temporal_leakage_measurement，语义内聚不新增编号）+ 4项schema字段已落地（experiment_registry补temporal_leakage_measurement{method:matched_control/boundary_detection/none,leakage_score,reference_model}+factor_registry补causal_structure{confounders,colliders,specification_audit}+risk_limit_registry补compliance_notices list{regulation,effective_date,applicability,impact_note}+strategy_registry regime_detector enum补statistical_jump/jump_diffusion_hmm两选项，同步补全v1.26/v1.27遗漏的wasserstein_hmm/text_var_dual注释）+ 2项审计检查扩展（E17+E18，均warning级MVP不阻断） | 全网搜索 2026-08-10 第二十轮（arXiv:2608.02985v1 2026-08-04 Zeyu Zhang+Stadie Northwestern Temporal Leakage Measurement/arXiv:2602.17234v2 2026-05-25 Shapley-DCLR+TimeSPEC/prakulhiremath/temporal-leaks 2026-06 Valgrind for Time-Series ML/CFA Institute 2025 Causality and Factor Investing López de Prado+Zoonekynd ADIA Lab/Cambridge Elements 2023 Causal Factor Investing/CFA Enterprising Investor 2025-10-30 Factor Mirage+2026-03-05 Question Exposes Weak Quant/causal-quant v0.4.1 2026-07-09 meacreatio/arXiv:2603.10202v1 2026-03-10 Cornell Hybrid HMM Jump-Diffusion Alswaidan+Varner/arXiv:2402.05272 Princeton Statistical Jump Model Shu-Yu-Mulvey/tradingstrategy.ai 2026 Market Regimes GMM/HDBSCAN/Jump-Diffusion/证监会2026-03-06短线交易规定2026-04-07施行/法释〔2026〕13号 2026-07-24内幕交易司法解释2026-07-27施行/源泰廖海2026-07解读）|
| v1.32.0 | 2026-08-10 | **DASH归因不可能性定理+A股涨跌停板上游污染+AlgoXpert稳定性区域+双曲因子衰减+MINGLE图-因子联合+CogAlpha代码进化第二十一轮研究+从假设到证明**：§4.39第二十一轮研究6项（DASH不可能性定理Lean 4机器验证collinearity下SHAP排名结构性不稳定faithfulness+stability+completeness三者不可兼得68%数据集受影响+A股±10%/±20%涨跌停板上游污染mask-first设计单一最大贡献者+0.44 Sharpe虚增IC 18%/AlgoXpert IS-WFA-OOS协议选稳定高原plateau不选悬崖尖峰cliff+目标切换排名反转/双曲因子衰减α(t)=K/(1+λt)博弈论均衡推导momentum R²=0.65优于指数0.61/机械因子衰减可建模判断因子不衰减crowding预测尾部风险/MINGLE图-因子联合ADMM框架因子暴露重定义图局部性跨regime优于相关性图/CogAlpha LLM代码进化7层21智能体Python代码表达式CSI300年化超额16.39% IR 1.90）填补前二十轮"因子归因稳定性"+"A股涨跌停可交易性掩码"+"参数稳定性区域选择"+"因子衰减函数形式"+"图-因子联合组合构造"+"LLM代码进化因子挖掘"六个对标空白 + 0项新E/G编号（遵循v1.24.0/v1.30.0/v1.31.0最小churn原则——E15扩展为"LLM Look-Ahead+A股Tradability Mask检测"查tradability_mask_policy、E16扩展为"因子冗余+归因稳定性检查"查attribution_stability flip_rate、G2扩展为"walk-forward+参数稳定性区域检查"查parameter_stability_region cliff_detected，语义内聚不新增编号）+ 2项schema字段已落地（factor_registry补attribution_stability{method:dash/none,model_count,flip_rate,stable_ranking}+experiment_registry补parameter_stability_region{plateau_identified,cliff_detected,stability_score,selection_method}）+ 3项审计检查扩展（E15+E16+G2，A股tradability_mask_policy=none为warning highlight、flip_rate>20%为warning highlight、cliff_detected=true为warning highlight，均warning级MVP不阻断）+ 1项data_asset_registry schema计划（tradability_mask_policy字段待P1-B施工落地）+ 3项Phase 1.5+/2+评估（双曲衰减hyperbolic_crowding/MINGLE图-因子联合/CogAlpha代码进化） | 全网搜索 2026-08-10 第二十一轮（arXiv:2605.21492 2026-05 Feature Attribution Is Provably Unstable Under Collinearity DASH Lean 4机器验证248定理/github.com/DrakeCaraker/dash-shap MIT开源/arXiv:2507.07107v2 2026-05 Machine Learning Enhanced Multi-Factor Quantitative Trading Mask-First Design Yimin Du USTC A股涨跌停板上游污染实证/arXiv:2603.09219v1 2026-03 AlgoXpert IS-WFA-OOS Protocol Nguyet-Chan-Anh AlgoXpert Lab/arXiv:2512.11913v1 2025-12 Not All Factors Crowd Equally Hyperbolic Alpha Decay Chorok Lee KAIST 8 Fama-French因子1963-2024实证/arXiv:2608.06618 2026-08-06 Beyond Co-Movement MINGLE Joint Factor-Graph Framework Chehab-Iacovides-Yazdanparast-Mandic Imperial College London/CogAlpha Cognitive Alpha Mining LLM-Driven Code-Based Evolution Liu-Huang-Luo-Wang-Yang-Li-Hu-Feng-Liu HKU+Grace Investment Machine ACL 2026 Oral）|

**v1.1.0 修订明细**：

- **R1（P0 硬错误·费率校准）**：cost_model 印花税 千1→**万5**（2023-08-28 减半政策，2026 延续）；过户费 万0.1/沪市only→**万0.1/沪深双向**（中国结算统一标准）。同步 catalogs/cost_model_registry.yaml。原 v1.0.0 印花税 2 倍高估会导致回测成本失真。依据：[华泰证券2026费率](http://m.toutiao.com/group/7671636219272430089/) ｜ [2026最新收费标准](https://licai.cofool.com/user/guide_view_3447293.html) ｜ [2026炒股成本揭秘](https://post.m.smzdm.com/p/a70o48xd/)
- **R2（P1 路径漂移）**：factor_registry 数据来源 `src/zephyr/factor/ashare/`（15 子目录）→ `src/zephyr/factor/`（6 .py + 子目录）。**原路径不存在**，会误导 P1-A 施工。实际因子模块：factor_base/momentum_factor/value_factor/intraday_snapshot_factors/alpha_signal_pipeline/bus_factor_defense
- **R3（P1 schema-代码漂移）**：technical_indicator 第5类 `structure`→**`reversal`**。16 号 §2.5 + 代码 `reversal.py` 均为反转类，v1.0.0 误写 structure。同步影响 §9.4 验收（16 号降级时注意第5类）
- **R4（P1 算法枚举漂移）**：execution_algo 6 算法 `aggressive/adaptive`→**`iceberg/alt`**。40 号实际 6 算法为 TWAP/VWAP/ICEBERG/POV/IS/ALT，v1.0.0 的 aggressive/adaptive 在 40 号无实现。alt 可保留 aggressive 别名，adaptive 删除
- **R5（P1 概念混淆）**：risk_limit 数据来源删除 `config/risk_register.yaml`。该文件是 MOD-INF-001 基础设施容量保障风险（R1-R21：SQLite/死锁/Schema/ChromaDB），**非交易风控限额**。交易限额真源在 src/zephyr/risk/
- **R6（P1 计数错误）**：data_asset DS-001~029→**DS-001~076（76条）**。v1.1.0 初估"030+"仍严重少算，v1.1.1 循环审查全量 `Select-String "^- dataset_id:"` 确认实际 76 条 datasets
- **R7（裁定未落实）**：S6 data_asset 改名 ruling_registry 登记**未完成**。grep ruling_registry 无 data_asset/dataflow_graph/REG-DATAFLOW 任何输出。加入 §9.4 验收 + 待定 D1
- **R8（新增§8.3 过度工程审查）**：逐项审查 12 注册表 + 通用设计 12 项（O1-O12），总结论"整体不过度"，仅 chart_pattern MVP 裁剪（O6）+ experiment_registry 待 MLflow 决策（O3）需关注
- **R9（2026 实践对标补充）**：factor↔Feature Store/qlib Alpha158 ｜ strategy↔Strategy Lifecycle Management ｜ risk↔NIST/ISO 31000 Risk Register ｜ data_asset↔OpenLineage ｜ experiment↔MLflow 2026 现状（Neptune 关停）｜ field_dictionary↔dbt schema.yml ｜ chart_pattern↔TA-Lib CDLPATTERN 61 种 ｜ cost_model↔square-root law 2026 AAPL 实证
- **R10（基准选择待定）**：2026 中证A500 已成机构标配（年化 8.58% > 沪深300 7.55%），待定 B1 是否补登记

**v1.1.1 修订明细**（循环审查第 1 轮）：

- **R11（DS 计数严重少算修正）**：dataflow_graph_registry.yaml 实际含 **76 条** datasets（DS-001~DS-076），v1.1.0 初估"DS-030+"仍严重少算。全量 `Select-String "^- dataset_id:" | Measure` 确认。同步修正 §6.1.1/§6.2.3/§9.4/§10/R6 中所有 DS 计数引用
- **R12（cost_model YAML 同步完成）**：v1.1.0 R1 要求"同步 catalogs/cost_model_registry.yaml"，本轮实际完成：印花税 rate 0.001→0.0005（2处）、过户费 market sh_only→sh_sz_both（3处）、version 1.0.0→1.1.0、description 修正、changelog 注释。同步修正 62 号 §5.3 schema 注释 sh_only→sh_sz_both

**v1.2.0 修订明细**（施工环节流程算法补全 + schema 增强）：

- **R13（施工流程算法补全）**：v1.1.x 只给 schema 和数据来源，未给可执行施工步骤。新增 §4.5 CONSTRUCT_REGISTRY 8 步算法（真源反查→编号分配→schema填充→交叉引用校验→半派生补全→一致性审计→治理同步→循环审查），P1 七注册表施工有标准流程可循
- **R14（交叉引用矩阵）**：新增 §4.6 12 表间 FK 关系全局矩阵（26 条 FK），明确强 FK/弱 FK/self-ref 完整性规则，施工时反向引用校验有据可循
- **R15（验证审计算法）**：新增 §4.7 AUDIT_REGISTRY 7 检查算法（frontmatter/编号合规/状态机/FK完整性/schema-代码漂移/编号-代码对齐/裁定落实），强制 Select-String 实码核对（40 号 v2.6.0 教训）
- **R16（生命周期管理流程）**：新增 §4.8 10 阶段生命周期（对标 2026 Strategy Lifecycle Management）+ DECAY_SCAN 衰减检测算法（对标 Alexander&Fabozzi 2026 MRP + Vibe-Trading 2026-07 DecayEvaluator）
- **R17（schema 增强）**：factor 补 lookback_period/benchmark_id/version_pin/decay_detection_method/last_decay_scan_at；strategy 补 benchmark_id/decay_detection_method/decay_threshold/last_decay_scan_at/mrp_baseline；technical_indicator 补 warmup_period；execution_algo 补 warmup_participation_rate/cooling_period/cost_model_ref/rl_policy_ref；risk_limit 补 inherent_risk/residual_risk/kri_frequency/review_cycle/scope_strategy；chart_pattern 补 dl_model_ref/dl_training_dataset + DL algorithm_variant；experiment 补 benchmark_id/cost_model_ref/mlflow_run_id/mace_env_ref
- **R18（2026 实践对标深化）**：Feast Feature View Versioning（2026-03-31）→ factor version/version_pin；策略 10 阶段生命周期（Linitics 2026-04 + DeepTradeX 2026）→ strategy lifecycle_status 8 态；pandas-ta-classic 0.6.20+（2026-05）→ technical_indicator；CNN+TA-Lib 混合（99.3%准确率）→ chart_pattern dl_cnn；EU AI Act（2026-08-02 生效）→ risk_limit 合规；MLflow 3.15.0/3.15.1 → experiment_registry E1 决策；square-root 律实证（Zhou 2026-07 + Han 中国市场 α≈0.7）→ cost_model square_root 必要性验证
- **R19（YAML→DB 混合模式共识）**：更新 §11，2026 业界"最小引导 YAML + DB 存储运行时配置"共识（Feast SQLRegistry + MLflow DB backend），个人项目 YAML 阶段 git diff 替代自动快照，schema 按 DB 表设计预留迁移

**v1.3.0 修订明细**（施工算法体系闭环 + 多检测器 + 过拟合检测）：

- **R20（变更管理算法）**：新增 §4.9 EVOLVE_ENTRY——entry 修改是比新建更高频操作，v1.2.x 缺变更流程。6 步算法（变更分类→版本快照→应用变更→依赖方影响分析→一致性审计→治理同步），对标 Feast Feature View Versioning + Confluent Schema Registry 兼容性模式。变更分类清单 6 类（metadata/schema_sig/code_ref/status/additive/breaking）
- **R21（退役算法）**：新增 §4.10 RETIRE_ENTRY——entry 退役是状态机关键转换，v1.2.x 缺退役流程。3 阶段算法（active→deprecated 90天宽限→retired 无活跃引用→物理删除需满1年+ARCH审批），对标 theFactory 2026-07 Schema Registry Deprecation 规则。退役触发条件 4 类（decay/performance_obsolete/replaced_by/structural_break）
- **R22（Schema 演进算法）**：新增 §4.11 EVOLVE_SCHEMA——schema 本身会演进，v1.2.x 缺演进流程。5 步算法（变更分类→兼容性判定→迁移策略→数据迁移→版本同步），对标 Confluent Schema Registry BACKWARD/FORWARD/FULL 兼容性模式 + datalakehouse Additive-Only/Expand-Contract 模式。Breaking vs Non-breaking 分类清单 8 类
- **R23（审计算法增强）**：§4.7 AUDIT_REGISTRY 补 E8 循环引用检测（variant_of/parent_experiment_id 链防环）+ E9 日期逻辑检查（created_at≤updated_at≤retired_date）+ E10 必填字段空值检查（区分 nullable 性能字段 vs required 核心字段）
- **R24（衰减检测多检测器）**：§4.8 补 DECAY_SCAN_MULTI 三检测器集成算法（CUSUM + Page-Hinkley + BOCPE 2/3 投票），对标 mathandmarkets 2026-02 + quantt.ca 2026-02。各检测器权衡表 5 行（擅长/弱点/参数/适用性）。MVP 用基础版（IC ratio + MRP），Phase 1.5+ 升级多检测器
- **R25（回测过拟合检测）**：§7.2 experiment_registry 补 PBO/DSR/PSR 三方法 + PurgedKFold，对标 backtest-guard 2026-07 + Soloviov 2026-07 PBO 论文。schema 补 pbo_value/dsr_value/psr_value/n_trials 四字段。关键洞察：PBO null=0.5（非0），>0.2 红旗。MVP 可选，Phase 1.5+ MUST 双门禁
- **R26（通用原则补充）**：§4 补第 11 条 Schema 演进兼容性（Additive-Only 默认 + Expand-Contract breaking）+ 第 12 条变更与退役治理（change_type 分类 + 90天宽限 + retired 保留审计）
- **R27（待定问题补 C1）**：§14 补 C1 power_law 冲击模型——§5.3 已提到"待定问题 C1"但 §14 遗漏，本轮补登

**v1.4.0 修订明细**（施工算法体系完整闭环 + 衰减后适应 + 数据质量监控）：

- **R28（衰减后适应算法）**：新增 §4.12 ADAPT_STRATEGY——§4.8 DECAY_SCAN（检测）+ §4.10 RETIRE_ENTRY（退役）缺中间环节"适应"。5 步算法（响应分级→refit window 最优化→refit 执行+过拟合防护→OOS 验证→适应频率约束），对标 mathandmarkets Part 82 五级响应 + refit window `w*=(2σ²/δ²)^(1/3)≈126天`。关键洞察：adaptation=overfitting 同一数学操作，OOS 验证判定适应成功/失败。填补 检测→适应→退役 三环节中间缺口
- **R29（跨维度衰减检测器）**：§4.8 补 profit_factor/z_score 两检测器——CUSUM/PH/BOCPE 都基于 returns 序列（收益维度），profit_factor 基于 trades 序列（盈亏比维度），z_score 基于分布偏移（实盘vs回测分布维度）。跨维度组合覆盖更全。MVP 推荐用 profit_factor+z_score（PineForge 实用派，无需μ₀基线）
- **R30（commit 绑定检查）**：§4.7 新增 E5b——beefed.ai compute_git 模式要求 code_path+commit 双绑定。YAML 阶段 git blame 天然提供（可选），DB 阶段 MUST。对应 factor/strategy schema 补 code_commit 字段
- **R31（数据质量监控检查）**：§4.7 新增 E11——数据质量是因子输入端健康度，与衰减检测（输出端）互补。对标 metricgate 4 层监控（L1 Data Quality→L2 Drift→L3 Prediction→L4 Performance），"alert on earliest layer"。检查 factor/strategy 的 data_quality_policy 声明（null_rate/drift_method）
- **R32（数据质量 schema 字段）**：factor/strategy schema 补 data_quality_policy/null_rate/drift_psi/drift_ks_pvalue/range_bounds/last_quality_scan_at——PSI<0.1稳定/>0.2主要漂移（apxml），KS p<0.01显著漂移（metricgate），null_rate>2x baseline告警（RisingWave）
- **R33（适应字段 schema）**：strategy schema 补 adaptation_level(1-5)/last_refit_at/baseline_sharpe——§4.12 ADAPT_STRATEGY 引用。adaptation_level 默认1（静默监控），refit 间隔≥60天防过拟合
- **R34（版本策略增强）**：§4 原则9 补 Immutable Version 选项——apxml 4 策略对比（Semantic/Immutable/Timestamped/Branch-based），Immutable（content hash）提供最强 reproducibility。YAML 阶段用 Semantic（git commit hash 天然提供 Immutable 保证），DB 阶段可升级 Immutable
- **R35（schema 文件级版本管理）**：§4.11 补 theFactory v1→v2 新文件规则——YAML 阶段单文件+schema_version 足够，DB 阶段 breaking 变更新建 v2 schema 文件（v1/v2 共存，消费者按 version 选解析逻辑）
- **R36（待定问题补 F1）**：§14 补 F1 参数适应 vs 退役决策——mathandmarkets Part 82 核心洞察"adaptation=overfitting"，检测到衰减后是 refit 适应还是直接退役是关键决策点

**v1.11.0 修订明细**（YAML→DB 迁移算法闭环 + MinBTL 回测过拟合第 4 方法）：

- **R37（YAML→DB 迁移算法）**：§11 描述了迁移路径（触发条件+混合模式+窄表存储）但**无施工算法**——12 注册表从 YAML 迁移到 PG 是高风险操作（数据丢失/双源不一致/迁移中断）。新增 §4.16 MIGRATE_REGISTRY R1-R7 七阶段渐进式迁移算法（R1 PG 表创建→R2 数据导入+YAML fallback→R3 CLI PG-first→**R4 完整性验证 gate**→R5 双写模式→R6 YAML 数据删除(不可逆,28天清洁期)→**R7 迁移后审计 gate**），对标 longterm-wiki #2076 R1-R6 playbook（补 R4/R7 双 gate）+ mvpfactory.io Expand-Contract vs Blue-Green + youngju.dev Schema Migration Tools。R6 不可逆性约束三条件（28天清洁期+git快照+R7审计）防止数据丢失。**12 算法体系完整闭环**："建→上→改→测→应/回→退→迁" 7 阶段全覆盖
- **R38（导航图更新为 12 算法 7 阶段）**：§4.4 算法体系导航图 v1.10.0 为 11 算法 6 阶段，v1.11.0 新增阶段 7"迁"（MIGRATE_REGISTRY）+ 调用矩阵补 MIGRATE_REGISTRY 行（触发: entry>500/exp>5000）+ 关键依赖补 R1 迁移顺序依赖 §4.15 construct_order 逆序 / R5 双写复用 §4.9/§4.10/§4.13 写入路径 / R7 审计复用 §4.7 AUDIT_REGISTRY
- **R39（MinBTL 回测过拟合第 4 方法）**：§7.2 experiment_registry 补 min_trl_years 字段——Bailey & López de Prado 2014 Minimum Backtest/Track Record Length，公式 MBL=0.5×(Z_α×σ_ann/SR_ann)²，回答"需多少年数据才能信任此 Sharpe"。回测过拟合检测从三方法（PBO+DSR+PSR）升级为四方法，对标 backtestbase 2026-01 + auditzk 2026-03 + digitalninjasystems 2026-06 + quantskills/skill-backtest-overfit 2026-07。经验值：SR=0.5→25-40+年(不实用)、SR=1.0→5-10年、SR=1.5→3-5年、SR=2.0→1.5-3年。SE(SR)≈1/√T，T=250(1年)时 SE≈0.063；自相关膨胀 SE 1.5-3x（Lo 2002）。实盘 track record < min_trl_years → Sharpe 不足以排除噪声，MUST 继续 probation 而非确认

**v1.12.0 修订明细**（2026-08-10 最新研究对标 + 回测过拟合第 5 方法 MTC + 8 项算法升级）：

- **R40（回测过拟合第 5 方法 MTC）**：§7.2 回测过拟合检测四方法（PBO+DSR+PSR+MinBTL）升级为五方法——新增 Multiple Testing Correction 方法族（White's RC/Hansen SPA/Romano-Wolf/MCS/BH-FDR），回答"N 个策略同时检验时族错误率控制下哪些仍显著"。对标 studentone.tech 2026-06-04 九道门级联（9 OOS 门控含 Romano-Wolf/BH-FDR/MC Block-Bootstrap/Cluster Stability）+ metricgate 2026-06-10 Model Confidence Set（Hansen-Lunde-Nason 2011，返回统计不可区分的最佳模型集合）+ marketmaker.cc 2026-06-29 DSR 多重检验对比（受控实验：朴素测试 100% 误报 vs DSR 0.1% vs White's RC 2.2%）+ arXiv:2604.15531 Falsification Audit 2026-04（审计研究流程本身而非结果）。关键洞察：SPA 与 Romano-Wolf 互斥（选其一），MCS 输出集合而非赢家，DSR 与 MTC 正交（DSR 校正选择偏差，MTC 校正族错误率）。schema 预留 mtc_method/mtc_pvalue/mtc_survived 三字段
- **R41（8 项最新研究对标补充）**：新增 §4.17 最新研究对标补充，覆盖 7 大领域 8 项发现：① 双曲衰减模型 α(t)=K/(1+λt)（arXiv:2512.11913，博弈论基础，动量因子 R²=0.65 优于线性/指数，估策略剩余寿命驱动 refit vs retire）② BOCPD 第 4 贝叶斯检测器（RegimeChange R 包 2026-08，给后验概率而非二值报警，频率派三检测器的贝叶斯补充）③ Wasserstein Distance 漂移检测（几何感知，对不重叠分布稳健，royxforge 2026-07 生产级实现）④ pgroll 零停机迁移（版本化视图 expand/contract，Xata 出品 6500 stars，§4.16 R1 工具首选）⑤ PubGrub 版本约束求解（CDCL 冲突驱动，uv/Poetry 采用，Kahn's 正交——解决版本选择非依赖顺序）+ 字典序最小拓扑（Kahn's + 优先队列，确定性建表顺序）⑥ Data Contracts vs Schema Registry 分层（Soda.io 2026-06，写入路径 vs 读取路径保护，Confluent migration rules JSONata/CEL）⑦ multigrid 三层 eval gate（2026-08-08，离线/操作/质量三层 + 确定性流量分割 sha256(salt)%100）+ Flagger 自动化 canary 回滚（2026-07）⑧ Feast OpenLineage 原生集成（2026-01，零代码改动端到端血缘，DB 阶段升级）
- **R42（v1.11.0 修订明细补登）**：补登 v1.11.0 修订明细 R37-R39（YAML→DB 迁移算法/导航图 12 算法 7 阶段/MinBTL 第 4 方法），原 v1.11.0 版本仅更新了表格行未补修订明细块，本轮补齐。§14 待定问题补 H1（MIGRATE_REGISTRY 触发阈值校准）+ I1（MinBTL 经验值 A 股校准，σ_ann=25% vs 美股 15% 放大 2.8 倍）

**v1.13.0 修订明细**（第二轮缺口审计 + 版本差异算法 DIFF_ENTRY + 13 算法体系完整闭环）：

- **R43（版本差异算法 DIFF_ENTRY）**：§4.9 EVOLVE_ENTRY 创建版本快照、§4.11 EVOLVE_SCHEMA 判定兼容性、§4.13 PROMOTE_ENTRY 对比候选 vs baseline——三者都需要"对比两版本差异"但 v1.12.0 及之前**无统一 diff 算法**（PR review 人工肉眼比 YAML，change_type 分类靠人工判断，兼容性判定无机器可读输入）。新增 §4.18 DIFF_ENTRY 横切只读查询算法（5 步：Step1 字节级 BLAKE3 快判→Step2 字段级三分类 additions/modifications/removals→Step3 语义分类 metadata/schema_sig/code_ref/status→Step4 兼容性判定→semver bump 映射 MAJOR/MINOR/PATCH→Step5 breaking 变更查依赖方），对标 IETF netmod YANG Schema Comparison draft-ietf-netmod-yang-schema-comparison-07（2026-05-05，规范化 schema 对比算法，产出结构化变更清单驱动 revision-label/semver 选择）+ AI Agent Schema Diff（2026-04-13，AST 语义 diff vs BLAKE3 字节哈希双策略）+ schema.biz Breaking-Change Detector（2026-04-29，Breaking/Safe/Warning 三桶 + semver 映射）。**关键设计**：YAML 阶段 git diff + dict diff + 查表三步（<50 行 Python），无需 AST 第三方库；DB 阶段升级 SQL row diff + formula AST 语义分析。填补唯一硬缺口
- **R44（第二轮缺口审计 10 领域映射）**：新增 §4.19 第二轮缺口审计与对标——针对"12 算法体系是否仍有施工环节流程算法缺口"做第二轮全网搜索（2026-08-10），覆盖 10 候选缺口领域逐项映射：① 候选提案（tapps-brain feasibility + ict-engine evidence-chain）→DEFER（个人项目先编码再注册）② 跨注册表验证（sigma-guard sheaf cohomology + SHACL-DS）→DEFER（E4+§4.6 足够）③ 变更通知（DataHub MCL + Apicurio EDA + CAMEL-24172）→COVERED 内联 ④ 反向血缘（TIN + OpenMetadata）→COVERED（§4.15 transitive_deps）⑤ 退役 GC（openclaw Doctor removeAfter + Docker registry GC）→DEFER 记录 DB 模式 ⑥ 复活/恢复（cinatra R3 + IETF RGP restore report）→NOTE 而非新算法（状态翻转=EVOLVE_ENTRY status 分支）⑦ 版本 diff →ADD §4.18 ⑧ 健康监控（noopsschool catalog SLI + acceldata triad）→DEFER 记录 DB 指标 ⑨ 原子批量（Lance BatchCommitTables + Apicurio multi-table + Doris 2PC）→COVERED by git commit ⑩ 搜索发现（Algolia dynamic facets + base14 metric registry）→DEFER。**核心结论：13 算法体系完整闭环，无施工阻塞缺口**，所有 DEFER 项均为 DB 阶段增强，符合 project_memory 过度工程处理原则
- **R45（导航图 13 算法更新）**：§4.4 算法体系导航图更新——标题 12 算法→13 算法（v1.13.0 补横切查询 DIFF_ENTRY），横切关注点段补 DIFF_ENTRY 行（EVOLVE_ENTRY 版本对比/PROMOTE_ENTRY 候选vs基线/EVOLVE_SCHEMA 兼容性判定调用），调用矩阵补 DIFF_ENTRY 行（触发: 对比两版本/PR review/兼容性判定，输入: entry_id+version_a/b，输出: 变更分类+semver bump+影响依赖），关键依赖补 §4.18 Step5 依赖 §4.15 transitive_deps / §4.11 可 delegate §4.18 semver_delta，使用方式补"版本对比/PR review/兼容性判定走 §4.18"

**v1.14.0 修订明细**（A股 2026 监管变更 + 算法一致性修复 + 第三轮研究对标）：

- **R46（PROMOTE_ENTRY 算法一致性修复）**：§4.13 PROMOTE_ENTRY 是 v1.8.0 算法，但 v1.11.0 新增的 `min_trl_years` 字段（§7.2 experiment_registry schema）和 v1.12.0 新增的 MTC 多重检验校正方法（§7.2 回测过拟合第 5 方法）**均未被 PROMOTE_ENTRY 引用**——Gate 1 仍硬编码 "oos_period_months < 3" 未交叉校验 min_trl_years，Gate 2 检查 PBO/DSR/PSR/plateau 但漏 MTC。本轮修复：Gate 1 加 `if entry.min_trl_years and bt.oos_period_years < entry.min_trl_years` 检查（Bailey & López de Prado 2014 MBL，回答"需多少年数据才能信任此 Sharpe"，实盘 track < MinBTL → Sharpe 不足以排除噪声 MUST 继续 probation）；Gate 2 加 `if bt.mtc_method and bt.mtc_survived == False` 检查（多策略同时检验场景的族错误率控制，bt.mtc_method 为空=单策略独立验证则跳过）。门禁清单表 G1/G2 行同步更新。**这是版本增量导致的字段-算法漂移**——后续新增 schema 字段/方法 MUST 回溯检查是否被引用算法纳入
- **R47（§4.17② BOCPE 事实错误修正）**：v1.12.0 §4.17② 原文"§4.8 当前三检测器 CUSUM/Page-Hinkley/BOCPE 均为频率派方法"系**事实错误**——§4.8 检测器 3 BOCPE 已是贝叶斯方法（Adams & MacKay 2007 BOCPD，v1.3.0 引入，v1.10.0 增强 Student-t likelihood，算法注释明确标 "Bayesian Online Change Point Detection"）。因此 v1.12.0 提议"加 BOCPD 第 4 检测器"是重复（BOCPE=BOCPD）。本轮修正：§4.17② 标题改为"score-driven BOCPD 变体 + 统一接口工具"，正文澄清真正增量是 Tsaknaki et al. 2025 的 **score-driven 变体**（处理 regime 内时间相关性，i.i.d. 假设违反时标准 BOCPD 退化）+ RegimeChange R 包统一接口，**非新增第 4 检测器**；MVP 决策更新为"检测器 3 已是贝叶斯，Phase 1.5+ 升级路径=likelihood 从 Student-t 升级为 score-driven，保持 2/3 投票不变"
- **R48（§4.20 A股 2026 年 7 月监管变更）**：2026-08-10 全网搜索发现两项 2026-07 生效的 A 股监管变更（实盘合规红线，非可选增强）：① 交易规则 2026 修订（上交所上证发〔2026〕41 号，2026-07-06 生效）——主板 ST/*ST 涨跌幅 5%→10%（影响 universe ST 池筛选+risk_limit 单日可移动范围）/盘后固定价格交易扩至全部 A 股+沪深 ETF（execution_algo 新增 after_hours 时段，cost_model 该时段 slippage=0）/SSE 基金收盘改集合竞价（benchmark 收盘价来源变化）/创业板做市商制度+大宗盘中实时确认。② 程序化交易管理实施细则全面执行（2026-07-07）——高频认定每秒申报+撤单≥15 笔（旧 300/秒收紧 20 倍）或单日≥20000 笔/单日撤单率≤15% 硬上限/每笔报单停留≥50µs。**关键确认**：印花税万5/卖出单边、过户费万0.1/沪深双向、最低 100 股 2026 年未调整（§5.3 现有登记正确）。**施工影响**：execution_algo_registry schema MUST 新增 6 字段（max_orders_per_sec/max_daily_orders/cancel_rate_limit/min_order_interval_us/is_hft/after_hours_eligible），risk_limit cancel_rate 升级为合规红线，universe ST 池涨跌停更新 10%，40_execution_broker v2.6.0 CancelRateGuard 须对齐 15% 阈值
- **R49（§4.21 第三轮研究 7 项对标）**：v1.12.0 §4.17 + v1.13.0 §4.19 覆盖第一/二轮，本轮第三轮针对 10 新领域筛选 7 项高价值对标：① SR 26-2 替代 SR 11-7（美联储 2026-04-17，15 年最大 MRM 变革，narrower model 定义+materiality tiering+AI carve-out——strategy 可借鉴 materiality_tier 字段）；② NautilusTrader 替代 Backtrader（2026-05，Rust 核心事件驱动+paper-to-live parity，experiment_registry 须记 backtest_framework+偏误检测能力）；③ Double-selection LASSO（arXiv 2026-05，控制 151 已知因子后隔离非冗余信号，factor_registry 新因子登记须附正交化结果）；④ 华创 LightGBM 三标签冲击模型（2026-03，瞬时/临时/永久三 LightGBM，A 股专用，cost_model Phase 1.5 新增 CST-ASTOCK-003）；⑤ AH-HMM 元 regime 层（MDPI 2026，meta-regime 层使转移动态 regime-条件化，IoU 0.73→0.93，HSMM 升级路径）；⑥ Feast 0.64 数据质量监控（2026-06，物化时检测漂移，特征管道层前置）；⑦ Meta-labeling 方向×仓位分离（Nova 2026-04，primary 定方向+meta 定仓位，strategy_subtype: meta_labeled 变体）。**两项实盘合规 MUST**（§4.20）+ 5 项 Phase 1.5+ 增强 + 1 项架构启发，MVP 无阻塞

**v1.15.0 修订明细**（局域网关闭补齐 + 高频阈值核实 + 第四轮研究流程治理）：

- **R50（§4.20③ 局域网行情通道关闭补齐）**：v1.14.0 §4.20 记录了两项 2026-07 生效监管变更（①交易规则修订+②程序化交易细则），但**漏掉了第三项实盘合规红线**——2026-08-10 第四轮搜索发现 2026-07-31 晚间交易所机房内局域网交易行情线路正式关闭，统一切广域网，广域网双向时延**不得低于 2 毫秒**（"不许太快"地板，含存量及新增），2026-08-31《交易网关管理指引（试行）》施行，深交所切换预计 8 月内完成（截至 8-5 未完成）。这是"基础设施平权"的物理层收口，直接影响 execution_algo 的延迟建模假设（局域网 0.3-0.8ms → 广域网 1.2-2ms）。本轮补 §4.20③ 完整时间线（2026-06 通知→7-28 券商收到→7-31 关闭→8-31 指引施行）+ 5 个时间节点的 schema/参数影响表 + 关键硬约束说明（仅关行情接收链路，交易报盘专线暂留）。**施工影响**：execution_algo 补 `latency_floor_ms`（默认 2.0）+ `network_type`（wan/lan 默认 wan）2 字段，cost_model 补 `slippage_regime`（pre/post_20260731 两套系数），data_asset 补 `latency_profile`+`colocation_eligible` 2 字段。**个人项目适用性**：影响极小（个人策略天/周级，0.3-0.8ms vs 1.2-2ms 时延差对天级收益约等于零），但 schema 字段 MUST 预留（合规底线），实际延迟建模=Phase 1.5+。对标新浪财经 2026-07-28 + 东方财富 2026-08-05 + 第一财经 2026-08-05 + 证券时报 2026-07-28
- **R51（§4.20② 高频阈值核实说明）**：v1.14.0 §4.20② 记录高频认定"15 笔/秒（旧 300/秒，收紧 20 倍）"，但 2026-08-10 第四轮搜索发现中基协 2026-07-27 研报仍引用"300 笔/秒"——经东方财富 2026-07-08 + 雪球 2026-07-08 + licai.cofool 2026-08-04 三方核实，系**研报撰写时间差导致的旧规引用**：旧规 300 笔/秒（2025-07-07 施行），新规 15 笔/秒分两阶段落地（2026-04-07 第一阶段收紧 + 2026-07-07 全面完整落地）。本轮补核实说明，明确本表"15 笔/秒"为**现行有效阈值**，中基协研报"300 笔/秒"作废。**这是监管变更分阶段落地导致的引用陷阱**——后续引用高频阈值 MUST 标注生效日期 + 阶段（第一阶段/全面落地），避免旧规误引
- **R52（§4.22 第四轮研究 5 项对标）**：v1.12.0 §4.17 + v1.13.0 §4.19 + v1.14.0 §4.21 覆盖第一/二/三轮（聚焦算法/工具），本轮第四轮聚焦"研究流程治理"，筛选 5 项高价值对标：① AlphaSchema LLM 因子挖掘 5 字段语义计划（Waton 2026-08-10，Event/Context/Qualities/Direction/Output，延迟代码生成至计划选定后，factor_registry 可补 discovery_plan 字段，Phase 2+ 远期评估）；② Agentic Workflows 架构承重件原则（Kinlay 2026-05，架构是承重件非提示词，度量"经人类批判存活的 ideas/月"提升 2× 非 10×，experiment_registry 可补 research_log_ref+human_gate_status，Phase 1.5+ 评估）；③ 证据 SHA256+allowed_use 治理模式（nathanku3-hue/Quant 2026-06，§4.10.0 SHA256 manifest 的生产实证+allowed_use 用途限定字段，experiment_registry 可补 allowed_use 字段，Phase 1.5+ 增强项，与 §4.13 PROMOTE_ENTRY 渐进式部署对齐）；④ 数据契约独立模块（stock_good 2026-06，data_contracts 外提为独立顶层目录，field_dictionary 可升级为 data_contracts_registry，Phase 1.5+ 评估）；⑤ 量化行业转向 Agent 竞争（PandaAI 2026-08，从因子竞争转向 Agent 协同研究，与 project_memory"Mamba/SSM/RL 不采纳"不冲突——Agent 协同=研究流程自动化非交易决策自动化，Phase 2+ 远期评估）。**0 项实盘合规 MUST**（已在 §4.20③ 补齐）+ 1 项 Phase 1.5+ schema 增强（allowed_use）+ 3 项 Phase 1.5-2+ 评估 + 1 项远期架构演进，MVP 无阻塞

**v1.16.0 修订明细**（CPCV 升级六方法 + 价格笼子 schema + A 股微观结构 + 第五轮研究）：

- **R53（§7.2 回测过拟合第 6 方法 CPCV + §4.13 G2 catastrophic-veto）**：v1.12.0 §7.2 回测过拟合五方法（PBO/DSR/PSR/MinBTL/MTC）升级为**六方法**——新增 CPCV（Combinatorial Purged Cross-Validation，López de Prado 核心方法）。CPCV 与 walk-forward 的根本区别：walk-forward 给**一条** OOS equity curve（单路径选择偏差），CPCV 给 **C(N,k) 条**（N=10,k=2 → 45 条）OOS 分布——三步增强：① 组合而非滑动（所有 C(N,k) 种切分）；② purge（移除 label horizon 重叠的 training 观测）；③ embargo（test set 后留缓冲区处理自相关）。输出是 OOS Sharpe 分布（mean ± std），**方差才是真实信号**——5 年日数据 + 45 变体几乎必然找到假赢家，t-stat 需 3.0 而非 1.96。本轮同步增强 §4.13 PROMOTE_ENTRY G2 门禁：新增 `cpcv_worst_max_dd > 0.15 = catastrophic-veto`（任何切分回撤超红线=一票否决，AlgoXpert arXiv:2603.09219 2026-03）+ `std/mean > 0.5` 切法敏感性阻断。G2 表格行从"PBO/DSR/PSR/plateau/MTC 五方法"更新为"PBO/DSR/PSR/plateau/MTC/CPCV 六方法"。schema 预留 cpcv_n_groups/cpcv_k_test/cpcv_oos_sharpe_mean/cpcv_oos_sharpe_std/cpcv_worst_max_dd 五字段。对标 noonbarbari 2026-07-04 + tradingstrategy.ai + arXiv:2603.09219 AlgoXpert 2026-03 + ceta-research 2026-03 + beefed.ai 2026
- **R54（execution_algo_registry schema 补价格笼子+T+1+涨跌停三字段）**：§4.23③ A 股微观结构约束审查发现——40_execution_broker v2.6.0 已实现 `check_price_cage`（project_memory P0 gap 已闭合），但 **execution_algo_registry schema 未显式登记价格笼子参数**。本轮补 3 字段：① `price_cage_config`（object，按板块区分：沪深主板/创业板 buy_ceiling_pct=1.02+sell_floor_pct=0.98+has_unit_floor=true+unit_floor_yuan=0.1；科创板纯 1.02/0.98 无 0.1 元兜底；北交所 1.05/0.95）；② `t_plus_1`（bool，A 股固定 true，回测须 `signal.shift(1)`）；③ `limit_up_down_untradable`（bool，涨跌停不可成交，回测须检查 `abs(ret) < limit_pct`，涨跌停日约占全年 1% 但止损日影响毁灭性）。**这是 schema-代码漂移修复**——40_execution_broker v2.6.0 已实现逻辑，execution_algo_registry schema 须对齐。MVP 阶段 P1-B 施工时 MUST 预留这 3 字段（实盘合规，非可选）。对标 CSDN 2026-08-09 价格规则 + sina 2026-07-06 新规 + CSDN 2026-08-09 T+1 动量突破 + toutiao 2026-08 AI 量化避坑
- **R55（§4.23 第五轮研究 4 项对标）**：v1.12.0-v1.15.0 覆盖第一/二/三/四轮，本轮第五轮针对 4 新领域筛选 4 项高价值对标：① AlgoXpert IS-WFA-OOS 三阶段协议（arXiv:2603.09219 2026-03，IS 优先 plateau 稳定区域+WFA majority-pass+catastrophic-veto 双门禁+OOS 严格参数锁定——已落地 §4.13 G2 catastrophic-veto）；② EU AI Act 2026-08-02 可解释 AI 合规（finantrix 2026-08-08+Dataiku 2026-06+theneuralbase 2026-04，高风险 AI 系统 MUST SHAP/LIME/counterfactual 可解释+决策日志 append-only ledger 7 年保留——strategy/experiment_registry 可选补 explainability_method+decision_audit_log 字段，Phase 2+ 远期评估）；③ A 股微观结构约束（价格笼子+T+1+涨跌停不可成交——execution_algo_registry MUST 补 3 字段，R54 已落地）；④ 决策审计治理（SEC Rule 17a4 append-only+24h explainability SLA——experiment_registry 可补 decision_log_store+decision_log_retention_years，Phase 2+ 远期评估）。**1 项已直接落地**（CPCV→§7.2+§4.13 G2）+ **1 项实盘合规 MUST**（价格笼子 3 字段→P1-B 施工）+ **2 项 Phase 2+ 远期评估**（explainability/decision_log），MVP 无阻塞

**v1.17.0 修订明细**（P0 代码 bug 修复 + 仓位管理 + A 股特色数据第六轮研究）：

- **R56（§4.13 PROMOTE_ENTRY G1/G2 门禁 P0 代码 bug 修复）**：Agent 内部一致性审查发现 2 个 P0 代码 bug：① **字符串拼接 TypeError**——G1/G2 门禁中 `"text" + bt.oos_sharpe`（float）在 Python 中会 TypeError（str+float 不支持），本轮统一改为 `"text" + str(bt.xxx)`，涉及 G1 的 oos_sharpe/oos_max_drawdown/oos_period_months/oos_period_years/min_trl_years 和 G2 的 pbo_value/dsr_value/cpcv_worst_max_dd/cv 共 9 处；② **CPCV mean<=0 漏判**——v1.16.0 G2 的 CPCV 检查当 `bt.cpcv_oos_sharpe_mean <= 0` 时仅跳过变异检查（`if bt.cpcv_oos_sharpe_mean > 0 and ...`），但 OOS 平均 Sharpe 为负/零=策略在多数切分中亏损=不可部署，本轮改为 `if bt.cpcv_oos_sharpe_mean <= 0: gates_failed.append("G2_cpcv_mean_nonpositive: ...")` 直接 FAIL，变异检查改为 `elif`（仅 mean>0 时检查避免除零）。**这是伪代码质量问题**——后续算法伪代码 MUST 通过 str() 规范+边界条件审查（mean<=0/除零/None 检查）
- **R57（§4.24 仓位管理 3 项对标）**：前六轮研究对标未覆盖"仓位管理"（position sizing——strategy_registry 和 risk_limit_registry 的核心维度），本轮填补此空白：① **Conformal Kelly**（arXiv:2608.01494 2026-08-02）：conformal prediction interval 宽度作为 fractional Kelly scale，interval 宽则缩仓窄则加仓，6 年年化 28.5% Sharpe 1.34，核心反直觉发现=最简单方法最佳（宽度稳定性>局部锐度），drawdown dial 风控 MaxDD 27.7%→20.3%，Phase 2+ 评估（需 conformal prediction 基础设施）；② **Kelly+ML 协方差改进**（quantsingularity 2026-06+SCIRP 2025-03 A 股实证）：Marcenko-Pastur denoising+HRP clustering+detoning 三种协方差改进，A 股收缩估计+ridge 风险约束 Kelly，Phase 1.5+ risk_limit_registry VaR 协方差可采用 denoising；③ **Sizing Shootout A/B 框架**（crucible-backtester 2026-07）：conviction vs risk_parity vs fractional_kelly 三 sizer 对比，只有 weight 公式不同其余共享，promotion 须同时 beat on Sharpe AND max-DD，OBSERVE-only 不改 live config，experiment_registry 可补 sizing_arm+sizing_shootout_winner 字段
- **R58（§4.24 A 股特色数据 2 项对标）**：前六轮未覆盖"A 股特色数据"（data_asset_registry 和 factor_registry 的 A 股专有维度），本轮填补此空白：④ **A 股高频因子 2026 实战**（国泰海通 2026-08-10）：日内收益 7.75%/开盘后买入意愿强度 16.29%/尾盘成交占比 13.58%/日内下行波动 14.94%，2026 年多空 7-16% 仍有效，但日内动量与隔夜动量反转（T+1 制度导致），factor_registry intraday 分类 P1-A 施工 MUST 登记 4 个 A 股高频因子（数据源须 Level-2），MVP 用日线因子 Phase 1.5+ Level-2 接入；⑤ **龙虎榜+Level-2 数据源治理**（CSDN 2026-08-09+sina 2026-07-08+toutiao 2026-08-10）：AKShare 明确声明仅学术用途不可商用，龙虎榜含机构/游资/量化席位活跃度是 A 股独有信号，2026"机构打底+游资突破+量化搅局"三元结构+量化盘口脉冲/虚假挂单新博弈，data_asset_registry P1-B 施工 MUST 标注 `license_type: academic_only/commercial_license`，MVP 用 AKShare 实盘前须评估商业授权

**v1.22.0 修订明细**（第十一轮研究+施工环节缺口填补）：

- **R59（§4.7 E18 LAP 前瞻污染检测）**：E15（KTD-FIN masking）是数据侧防御，LAP（arXiv:2512.23847v2 CUHK 2026-06）是模型侧诊断——双轨互补。LAP=P(up)+P(down) 用"日期-only 召回查询"估计 LLM 内化未来结果的概率，污染检验回归 Y_{t+1}=β₁μ̂_t+β₂LAP+β₃(LAP×μ̂_t)，β₃>0=前瞻污染指征。experiment_registry schema 补 `lap_check_result` 字段（{applicable, lap_value, interaction_beta3, contamination, suppression_method}）。warning 级 MVP 不阻断，MVP 未用 LLM 时填 {applicable: false}。Phase 1.5+ 评估 FinCAD 推理时 logit 抑制 + CMMD 多模型分歧过滤
- **R60（§4.7 E19 因子构造偏差审计 LIB）**：企业债因子动物园（arXiv:2604.07880v1 2026-04）108 因子纠正 LIB+ex-post 过滤后多数不再显著。① Latent Implementation Bias——信号与收益共用噪声数据源（TRACE 交易价含测量误差），相关误差被误认为 premium；② ex-post 收益过滤嵌入未来信息——去极值/去流动性差用全期统计量。factor_registry schema 补 `lib_audit`（{applicable, signal_return_shared_noise, mitigation}）+ `ex_post_filter_audit`（{uses_full_period_stats, walk_forward_corrected, filter_method}）两字段，仅 price-derived 因子检查。warning 级 MVP 不阻断。A 股关联：复权价/成交量既入因子又入收益分母=LIB 风险
- **R61（§4.8 DECAY_SCAN_MULTI 重尾自适应分支 GSA-LLR）**：经典高斯 CUSUM 在重尾数据（excess kurtosis γ₄>20）上 100% 误报（arXiv:2605.23419v2 2026-05），A 股小盘股 γ₄ 常>10、危机期>20。GSA-LLR（Generalized Stochastic Approximation of Log-Likelihood Ratio）用广义随机基（多项式/对数/分数幂）仅用 3 阶以下矩适配 CUSUM 到非高斯数据，基函数按 γ₄ 自动选择（γ₄<6 多项式/6-20 分数幂/>20 对数基），阈值来自 Kunchenko 概率误差界无需经验调参。`decay_detection_method` enum 补 `gsa_llr_cusum` 选项（factor+strategy 两表），DECAY_SCAN_MULTI 检测器 1 增加重尾自适应分支（γ₄≥6 自动切换 GSA-LLR，γ₄<6 保持经典 CUSUM）。MVP 用 profit_factor/z_score 绕过此问题，Phase 1.5+ cusum_ph_bocpe 的 CUSUM 分量须用 GSA-LLR 鲁棒变体
- **R62（schema 字段补全 + 一致性同步）**：① risk_limit_registry schema 补 `stage`（active/deprecated/disabled，对标 Apicurio 四阶段状态机，disabled 阻止新策略引用即将退役的限额）+ `response_strategy`（mitigate/transfer/avoid/accept，ISO 31000 风险响应策略，与 breach_action 执行动作正交）；② §4.4 导航图 E1-E17→E1-E19（4 处：框图 Step6/横切关注点/调用矩阵/CONSTRUCT Step6）+ §4.16 R7 DB 版 E1-E17→E1-E19 + §9.4 验收清单 audit_registration.py 扫描 E1-E19 全检查；③ §4.29 A 股板块轮动警示——Top3 次日重合率仅 14.8%，sector_rotation 策略（STR-SECTOR-ROTATION-001）校准 MUST 采纳，hot_bonus 降至 0.02，增 q3 短期动量权重

**v1.23.0 修订明细**（第十二轮研究+施工环节缺口填补）：

- **R63（§4.7 E20 RMT 去噪因子相关性矩阵审计）**：E16 查冗余声明（correlation_group/redundancy_status），E20 查**冗余检测的方法学质量**——因子相关性矩阵在 q=N_factors/T_observations>0.1 时含大量 Marchenko-Pastur 噪声特征值，落在 [λ₋,λ₊]=σ²(1±√q)² 区间内的特征值是纯噪声而非信号，未去噪的伪相关被误判为因子冗余（independent 因子被错标 redundant 或反之）。EFS（arXiv:2507.17211v2 2026-08-07 港中文+上财）证明 RMT 去噪+正则化 QP 在美股/港股/A股三市场均优于未去噪基线，无额外调参成本。物理信息奇异值学习（arXiv:2601.07687v4 2026-08-02 Manolakis-Bongiorno-Mantegna）进一步指出标准 RMT 假设平稳+有界谱，真实收益违反此假设（依赖漂移+宏观共同模），Phase 2+ 用神经网络估计器替代解析收缩。factor_registry schema 补 `rmt_denoised` 字段（{applicable, method: clip/shrink/nn, q_ratio, denoised: bool}）。warning 级 MVP 不阻断——MVP 因子数<20 时 q<0.1 填 {applicable: false}，Phase 1.5+ 因子数>20 时 MUST 启用 RMT clipping 去噪（将 [λ₋,λ₊] 内特征值替换为均值，保留信号特征值）。本轮与 E16（v1.20.0 冗余声明检查）形成"声明+方法学质量"双层审计
- **R64（risk_limit_registry schema 补 drawdown_calibration_method + var_calibration_method）**：① `drawdown_calibration_method`（gaussian/rsb_non_gaussian/fbm_long_memory）对标 [arXiv:2608.00127v1 2026-07-31 RSB Drawdown Risk Beyond Brownian Motion](https://arxiv.org/pdf/2608.00127)（Landolfi Epiphany）——放宽高斯假设后四个决策相关度量（最大回撤/最大损失/最终负时间/最长恢复时间）移动方向不同，单一高斯表系统性误警，A 股重尾分布（γ₄ 常>10）尤其严重；长记忆（fBm）下回撤风险放大几乎完全是自相似色散缩放效应 T^(H-1/2) 而非路径几何深化。MVP 默认 gaussian（保守阈值兜底），Phase 1.5+ 重尾策略（γ₄>6）MUST 切换 rsb_non_gaussian——按策略实际偏度/肥尾/波动率聚集生成四维回撤查找表替代单一静态阈值；② `var_calibration_method`（historical/rwc_conformal）对标 [arXiv:2602.03903v3 2026-08-03 Taming Tail Risk](https://arxiv.org/html/2602.03903v3)（Schmitt Oxford）——Regime-Weighted Conformal Calibration (RWC) 用指数时间衰减+regime 相似性权重从历史预测误差构建安全缓冲，包裹任意条件分位数预测器对准目标违反率，修复 VaR 压力期系统性低估（违反率远超名义 1%）。MVP 默认 historical（历史模拟法简单），Phase 1.5+ VaR 限额上线后 MUST 评估 rwc_conformal——regime 分类器复用项目 regime_detector（35/36 号文档）无需额外建模
- **R65（一致性同步 E1-E19→E1-E20）**：① §4.4 导航图 4 处（框图 Step6 / 横切关注点段 / 调用矩阵 / CONSTRUCT Step6）E1-E19→E1-E20；② §4.16 MIGRATE_REGISTRY R7 DB 版 E1-E19→E1-E20；③ §9.4 验收清单 audit_registration.py 扫描 E1-E20 全检查（含 v1.23.0 E20 RMT 去噪）；④ §4.30 第十二轮研究 3 项对标补充（RMT/RSB/RWC）。本轮与 v1.22.0 R62 同步模式一致，确保 E 检查范围与实际 §4.7 算法体一致

**v1.24.0 修订明细**（第十三轮研究+施工环节缺口填补）：

- **R66（§4.7 E14 扩展 c 维度 universe_registry 生存偏差审计）**：E14（v1.18.0 回测数据偏差检查）taxonomy ① universe-membership contamination 自 v1.18.0 起就声明"生存偏差在 universe 层进入——仅含存活至今日的公司"，但实现只查 data_asset_registry 的 price dataset 是否 survivorship_free，**不查 universe_registry 的成分构造是否 PIT**——这是"概念正确但实现遗漏"：data_asset 含退市股（survivorship_free=true）但 universe 用当前成分回溯构造（pit_constituent_construction=false）= 仍有生存偏差。alphanume 2026-06 明确："The universe is where survivorship bias enters most silently"；arXiv:2603.16904 显式构造 survivorship-bias-free S&P500（回溯 cutoff 后所有 add/delete 事件）；tickernerd 2026-08 强调 PIT Compustat/FactSet 历史 + 三锁定窗口。本轮 E14 新增 c 维度：universe_registry 的 entry 是否声明 pit_constituent_construction / delisted_handling。**关键设计决策**：不新增 E21 而扩展 E14——E14 本就是"回测数据偏差检查"语义内聚，生存偏差（含 universe 层）是其核心子类，扩展避免 E 编号膨胀（E1-E20→E1-E21 的 6 处同步 churn）+ 保持 E14 作为"回测数据偏差"单一入口
- **R67（universe_registry schema 补生存偏差三字段）**：① `pit_constituent_construction`（bool）——成分股是否按 point-in-time 构造（true=每个调仓日只用当时可得成分文件；false=用当前成分回溯=生存偏差；null=未声明）；② `delisted_handling`（include/exclude/unknown）——退市股处理（include=含退市至退市日含最终部分期收益，回测 MUST；exclude=仅存活=生存偏差）；③ `survivorship_free`（bool）——universe 是否无生存偏差（true=含退市+PIT构造；false=仅存活股）。MVP 阶段 5 条 entry 声明即可：UNI-INDEX-001/002 static 池须确认成分历史 PIT 性（中证指数公司季度调整文件可回溯），UNI-DYNAMIC-001/UNI-RULE-001/UNI-RULE-002 的过滤规则用当日数据可填 pit_constituent_construction=true。实际 PIT 成分文件接入=Phase 1.5+

**v1.25.0 修订明细**（第十四轮研究 + 3 注册表 schema 批量补全 + D1 闭合）：

- **R68（§4.32 第十四轮研究 3 项对标）**：填补前十三轮"PIT 字段语义引擎层空白"+"预注册流程层空白"+"因子发现自动化"三个对标空白：① Assay PIT 正确回测引擎（2026-07-04，ICLR AlphaBench 配套）——`as_of_date` 字段语义契约（joins 用 PIT 快照而非 current 状态，earnings 表 join 须用 announce_date≤as_of_date 而非 report_period）；② AurumQ-RL MASTER-lite 预注册协议（2026-07-17）——成本否决门（net Sharpe 扣成本后<0 则 pre-registered 失败）+ 3 窗 3 seed（train/val/oos 各 3 随机种子取中位防单次运气）；③ R&D-Agent-Quant（NeurIPS 2025 微软开源 2026-07-23 Qlib 集成）——因子-模型协同优化（因子生成器与预测器交替迭代而非串行）
- **R69（E14 扩展 d 维度 PIT 字段语义审计 + G1 增强）**：① §4.7 E14 新增 d 维度——data_asset_registry 的 `as_of_date_semantics` 声明检查（join 类型/join 键/announce_date 处理），不新增 E 编号避免膨胀；② §4.13 G1 增强——成本否决子检查（net Sharpe<0 阻断）+ IC-OOS 脱钩告警（IC 高但 OOS Sharpe 低=因子有效但策略实现有 bug），不新增 G 编号
- **R70（3 注册表 schema 批量补全 + D1 闭合）**：① data_asset_registry 补 `as_of_date_semantics`；② experiment_registry 补 `pre_registered`（bool）+ `cost_vetoed`（bool）+ `ic_oos_gap`（float）；③ factor_registry 补 `discovery_agent`（enum: human/rd_agent/efs/hubble/quantevolver）；④ 3 注册表（factor 111 条/risk_limit 42 条/strategy 59 条）批量补全 v1.20-v1.23 新增字段（factor 7 字段 + risk_limit 4 字段 + strategy 7 字段）；⑤ ruling_registry 裁定 #223 登记 data_asset→dataflow_graph 改名（D1 硬缺口闭合）

**v1.26.0 修订明细**（第十五轮研究 + 5 个对标空白填补 + v1.21 遗留 schema 落地）：

- **R71（§4.33 第十五轮研究 5 项对标）**：填补前十四轮"regime 检测标签置换稳定性"+"过拟合检测概念校准"+"流动性因子实现陷阱"+"信号融合适用边界"+"研究段-schema 落地脱节"五个对标空白：① Wasserstein HMM（arXiv:2603.04441v1 2026-02-21）——Wasserstein 距离替代 EM 对数似然解决传统 HMM 标签置换问题（regime 标签 0/1 无语义可任意交换）；② PBO null=0.5 误读澄清（marketmaker.cc 2026-07-01 pbo-search 开源）——PBO 零假设是 0.5 而非 0，PBO≈0.5=完全过拟合=硬币翻转（非"0.2-0.5 轻度过拟合"）；③ Kyle lambda OLS slope 实现陷阱（JohnGavin #627 2026-08-03）——Kyle lambda 须用 OLS slope=cov(log_ret,signed_flow)/var(signed_flow)，错误实现为 ratio=abs(log_ret)/volume 会与 Amihud 指标数值恒等；④ Meta-labeling 仅适用 discretionary/规则型主模型（QuantConnect 2026）——end-to-end ML 主模型已内含仓位学习，叠加 Meta-labeling 冗余；⑤ v1.21.0 第十轮 Evidently+NannyML 标签延迟分层遗留 schema 落地
- **R72（schema 字段补全）**：① strategy_registry `combination_strategy.regime_detector` enum 补 `wasserstein_hmm` 选项（v1.19.0 news_aware → v1.26.0 wasserstein_hmm）；② §4.13 G2 门禁加 PBO null=0.5 误读警示注释；③ factor_registry 补 `liquidity_metric` 字段（含 Kyle lambda OLS slope 实现陷阱注释）；④ data_asset_registry 补 `label_delay_days` + `drift_detector` 两字段（Evidently+NannyML 标签延迟分层监控）；⑤ `meta_labeling_config` 字段注释增强适用边界（仅 discretionary/规则型主模型）

**v1.27.0 修订明细**（第十六轮研究 + 6 引擎层空白闭合）：

- **R73（§4.34 第十六轮研究 6 项对标）**：填补前十五轮"变点归因层"+"LLM 因子生成安全标准"+"RL 微调 vs prompt loop 区分"+"文本+VAR 双向 regime 检测"+"重尾分布回测指标"+"标准化因子评测基准"六个对标空白：① ARM Attribution by Rank Maxima（arXiv:2608.01691v1 2026-08-03）——变点归因算法，检测到变点后归因到具体因子坐标（rank maxima 统计量）；② Hubble AST 验证沙箱（arXiv:2604.09601v2 2026-04-14）——LLM 因子生成安全标准（AST 验证+DSL 约束+复杂度控制+双通道 RAG+家族感知选择）；③ QUANTEVOLVER（arXiv:2605.15412）——RL 微调因子生成器 vs prompt loop 区分（RL 微调迭代改进 prompt 不变）；④ Text-enhanced regime shift（arXiv:2605.30363v2 2026-08-02）——文本+VAR 双向验证 regime 检测；⑤ Weighted Kolmogorov Metric（arXiv:2601.04490v1 2026-01-08）——重尾分布回测指标收敛性修复；⑥ AlphaBench（ICLR2026）——标准化因子评测基准
- **R74（schema 字段补全 + 流程增强）**：① §4.8 衰减检测流程补"步骤 5：变点归因"子步骤（检测到变点后 MUST 调用 ARM 归因到具体因子坐标，Phase 2+ 因子数>20 时启用）；② factor_registry 补 `llm_safety_stack` 字段（{ast_validation, dsl_constrained, complexity_control, dual_channel_rag, family_aware_selection}，discovery_agent=rd_agent/efs/hubble/quantevolver 时 MUST 声明）；③ factor_registry `discovery_agent` enum 补 `quantevolver` 选项；④ strategy_registry `combination_strategy.regime_detector` enum 补 `text_var_dual` 选项；⑤ risk_limit_registry `drawdown_calibration_method` + `var_calibration_method` enum 均补 `weighted_kolmogorov` 选项（重尾策略 γ₄>8 MUST 启用）；⑥ Phase 1.5+ AlphaBench 3 任务体系评测不同 discovery_agent 因子质量

**v1.28.0 修订明细**（第十七轮研究 + 上线裁决三值逻辑 + 风险贡献结构分解 + 过拟合实证模式分类）：

- **R75（§4.35 第十七轮研究 3 项对标 + 裁决哲学升级）**：填补前十六轮"上线裁决三值逻辑"+"风险贡献结构分解"+"过拟合实证模式分类"三个对标空白：① **Joint Falsification 三重门框架**（arXiv:2607.20093v1 2026-07-22 Darmanin Hecatus Retail Trader's Ruin）——首个将"实际可部署性"定义为三门联合证伪（统计 edge 门+经济可行性门+有限资金生存门），三值裁决 REFUTED/SUPPORTED/INCONCLUSIVE（非二元 pass/fail）——"统计不显著"≠"证伪"，CI 太宽=INCONCLUSIVE 应继续积累数据而非放弃；② **Leave-One-Out 风险贡献分解**（arXiv:2604.10375v1 2026-04-11 Alexander & Fabozzi UVA+JHU）——RC=inherent+correlation 严格加性，区分"孤立高风险"（inherent 主导→降仓位）vs"高相关风险"（correlation 主导→加对冲），单一 RC 数字不区分导致响应策略错配；③ **Backtest OVERFIT 5 模式 + PF 比值阈值**（dibi8 2026-05-25）——5 种实证模式分类（walk-forward divergence/regime-flip/parameter-cliff/indicator-stacking/survivorship）+ PF ratio>2.0=textbook overfit + 最小交易数 directional 300/mean-reversion 500 笔。**裁决哲学升级**：二元 pass/fail → 三值 REFUTED/SUPPORTED/INCONCLUSIVE，区分"样本不足"与"真无 edge"，避免过早弃真（INCONCLUSIVE 误判 REFUTED）和反复重申死策略（REFUTED 误判 INCONCLUSIVE）
- **R76（§4.13 G2 门禁 PF ratio + min trade count 子检查）**：① PF ratio 子检查——`bt.train_pf / bt.oos_pf > 2.0` = 阻断（textbook overfit，dibi8 实证 moss-trade-bot Train PF 2.08→OOS PF 0.94 ratio 2.21）；`> 1.5` = warning（suspect，检查是否 walk-forward divergence 模式）；② 最小交易数子检查——`bt.oos_trade_count < 300`（directional）/ `< 500`（mean_reversion）= warning（样本不足统计不显著，建议 viability_verdict=inconclusive 继续积累数据）。**关键价值**：PF ratio/min trade count 是统计方法（PBO/DSR/CPCV）前的"一线快速筛"——计算极简（PF=盈利和/亏损和，无需 CSCV/bootstrap）但覆盖小样本谬误和 IS-OOS 发散两大常见陷阱
- **R77（§4.13 裁决逻辑三值分类 + 3 schema 字段落地）**：① §4.13 裁决逻辑增强三值分类——gates_failed 含 G1/G2 统计门失败时：非统计门（G3-G9）失败→直接 BLOCKED（修复后重申）；仅统计门失败 + `bt.oos_period_years < entry.min_trl_years`（样本不足）→ INCONCLUSIVE（继续 Shadow/Canary 积累数据，不放弃）；统计门失败 + 样本充分→ REFUTED（走 §4.10 RETIRE_ENTRY 放弃，勿反复重申）；② experiment_registry schema 补 `viability_verdict`（enum: supported/refuted/inconclusive）+ `overfit_pattern`（enum: none/walk_forward_divergence/regime_flip/parameter_cliff/indicator_stacking/survivorship）两字段；③ risk_limit_registry schema 补 `risk_contribution_decomposition` 字段（{inherent_component: float, correlation_component: float, decomposition_method: enum(loo/standard_rc/none)}）。**MVP 阶段无阻塞**——viability_verdict 填 inconclusive、overfit_pattern 填 none/walk_forward_divergence、risk_contribution_decomposition 用 standard_rc

## 14. 待定问题（需人决策，不擅自拍板）

| # | 问题 | 背景 | 建议方向 |
|---|---|---|---|
| B1 | 基准是否补中证A500/万得全A | 2026 中证A500 成机构标配，90号§13基准选择待讨论 | 补 BMK-INDEX-004 candidate，待用户裁定是否替换沪深300作 multifactor 基准 |
| C1 | cost_model 冲击模型是否新增 power_law(exponent=0.7) | §5.3 已登记：Han 等中国市场实证 α≈0.7（非0.5），A 股冲击对规模敏感度更陡。当前 square_root(coeff=0.1) 对个人小单足够保守，但 Phase 1.5 AUM 增长后可能需 A 股专用 power_law 模型 | Phase 1.5 校准时评估：新增 CST-ASTOCK-003 power_law(exponent=0.7) 作为 A 股专用冲击模型候选，按 40 号 §13.1 拟合 coefficient 实际值。MVP 阶段不阻塞 |
| D1 | ruling_registry 登记 data_asset 改名 | S6 裁定要求但未落实，P1-B 前必须补齐 | P1-B 施工首项即补登记 |
| E1 | 51号 MLflow 退役决策是否重评 | 2026 MLflow 是首选，Neptune 已关停，原退役方案前提变化 | 建议保留 MLflow，experiment_registry 退化为轻量索引层 |
| F1 | 参数适应 vs 退役决策（v1.4.0 补） | mathandmarkets Part 82 核心洞察"adaptation=overfitting"——检测到衰减后是 refit 适应还是直接退役是关键决策点。§4.12 ADAPT_STRATEGY 已用 OOS 验证兜底，但 Level 3→Level 5 的升级阈值需实盘数据校准 | MVP 阶段 Level 1-2（监控+减仓），Phase 1.5+ 积累实盘衰减数据后校准 Level 3 refit 触发阈值 + OOS 恢复条件（当前用 baseline_sharpe×0.85 启发式） |
| G1 | decay_cause 衰减原因诊断方法（v1.5.0 补，v1.6.0 补登 §14） | §4.12 ADAPT_STRATEGY Step 1.5 用 Five Horsemen 分类（crowding/regime/overfitting/tech/depletion）驱动 refit vs 退役决策，但 **decay_cause 本身如何诊断是难题**——统计检测器（CUSUM/PH/BOCPE/profit_factor/z_score）只报警"有衰减"，不诊断"为什么衰减"。原因分类需额外诊断方法：crowding=策略拥挤度指标（如成交额/换手率异常）、regime=regime 分类器（HMM/波动率 regime）、overfitting=PBO/DSR 复检（§7.2）、tech=执行成本漂移监控、depletion=套利空间消失（价差压缩）。v1.5.0 schema 补了 decay_cause 字段但诊断算法未定型 | Phase 1.5+ 逐步实现原因诊断器：① overfitting 诊断最成熟（PBO/DSR 已在 §7.2），优先实现；② regime 诊断复用项目 regime 分类器（35/36 号文档已有 regime 概念）；③ crowding/tech/depletion 诊断需研究 A 股特色指标。MVP 阶段 decay_cause 标 unknown，走保守 refit 流程（§4.12 Step 1.5 else 分支） |
| H1 | MIGRATE_REGISTRY 触发阈值校准（v1.11.0 补） | §4.16 MIGRATE_REGISTRY 触发条件为"factor>500 / experiment>5000 / 并发写需求"，但这些阈值是经验值未经实际验证——个人项目当前因子<50/实验<100，远未触发。阈值定太低→过早引入 DB 复杂性（运维成本/迁移风险）；定太高→YAML 性能瓶颈（grep 慢/并发写冲突）。另：12 表是否统一阈值？experiment 增长远快于 factor，可能需分表阈值 | MVP 阶段不触发（YAML+git 足够）；Phase 1.5+ 监控 YAML 加载时间 + 写冲突频率，实测达到以下任一条件再迁：① 单表 entry>300 且 grep 全表>2s ② 并发写冲突周>3次 ③ experiment 年增长>1000。分表阈值：experiment 表阈值可低于 factor（experiment 增长快） |
| I1 | MinBTL 经验值 A 股校准（v1.11.0 补） | §7.2 min_trl_years 经验值（SR=1.0→5-10年）基于美股年化波动率~15%，A 股波动率更高（~25-30%），相同 Sharpe 下所需样本长度可能不同。公式 MBL=0.5×(Z_α×σ_ann/SR_ann)² 中 σ_ann 是年化波动率——A 股高波动意味着相同 SR 需更长 track record，但 A 股高波动也意味着年化收益更高（相同 SR 下），实际影响需校准 | Phase 1.5+ 用 A 股历史数据校准：取 10 年沪深 300 成分股，模拟 SR=1.0 策略，实测不同 σ_ann 下 MinBTL 值。若 A 股 σ_ann=25% vs 美股 15%，MinBTL 放大 (25/15)²≈2.8 倍——SR=1.0 可能需 14-28 年（过于保守），需重新评估 SR 阈值或用 A 股专用校准 |
| J1 | A股2026监管变更施工优先级（v1.14.0 补） | §4.20 两项 2026-07 生效监管变更影响 5 表 schema。关键决策：① ST/*ST 涨跌停 5%→10% 是否立即更新 universe_registry 现有 5 条 entry 的 filter_rules（打板策略 STR-DABAN-001 连板梯队筛选依赖涨停判定，ST 股 10% 涨跌停改变"涨停"语义）；② 程序化交易 15 笔/秒 + 15% 撤单率阈值是硬编码默认值还是可配置（个人策略天然远低于阈值，但 schema 字段 MUST 预留）；③ 盘后固定价格交易扩围是否纳入 cost_model（after_hours slippage=0）作为回测可选时段 | P1-B execution_algo 施工时 MUST 预留 6 合规字段（§4.20 已列）；ST 涨跌停更新建议 P1-A universe_registry 重审时同步（影响打板策略核心逻辑，需 24 号文档联动评估）；盘后交易纳入 Phase 1.5+（MVP 不用盘后时段）。MVP 阶段 schema 字段预留=合规底线，实际阈值校准=Phase 1.5+ |
| J2 | 局域网关闭延迟建模 + 研究流程治理字段纳入时机（v1.15.0 补） | §4.20③ 局域网关闭（2026-07-31）+ §4.22 第四轮研究 5 项对标引出新决策点：① 局域网关闭后 `latency_floor_ms=2.0`+`network_type=wan` 是硬编码默认值还是按交易所分别配置（沪市已切广域网，深市待切，跨市场策略须适应两市场时延差异期）；② §4.22③ `allowed_use` 字段（experiment_registry）是否纳入 MVP——它直接支持 §4.13 PROMOTE_ENTRY 渐进式部署的"允许用途"声明，但增加 schema 复杂度；③ §4.22⑤ Agent 协同研究与 project_memory"Mamba/SSM/RL 不采纳"的边界确认——Agent 协同=研究流程自动化（Phase 2+ 评估），RL 策略=交易决策自动化（不采纳），两者边界是否需显式写入 project_memory | ① latency 字段：MVP 阶段沪市/深市统一 `latency_floor_ms=2.0`（广域网地板），Phase 1.5+ 深交所切换完成后按交易所分别校准；② `allowed_use`：建议 Phase 1.5+ experiment_registry 施工时纳入（与 §4.13 渐进式部署强相关，非 MVP 阻塞）；③ Agent 边界：建议在 project_memory 补一条"Agent 协同研究=研究流程自动化 Phase 2+ 评估项，RL 交易决策=不采纳，两者正交"（待用户确认后登记）。MVP 阶段所有 Phase 1.5+/2+ 项均不阻塞 |
| J3 | CPCV 实施时机 + 价格笼子 schema 对齐策略（v1.16.0 补） | §7.2 CPCV 升级六方法 + §4.23③ 价格笼子 schema 引出新决策点：① CPCV 的 `cpcv_n_groups`/`cpcv_k_test` 默认值 N=10/k=2 适合 A 股日频数据量（5 年约 1200 交易日 → 每组 120 日）还是需按策略持仓周期调整（分钟级策略数据量大，N 可更大）；② §4.13 G2 的 catastrophic-veto 阈值 `cpcv_worst_max_dd > 0.15` 是否与 G1 的 `oos_max_drawdown > 0.15` 冲突（G1 检查平均回撤，G2 检查最差切分回撤，两者阈值相同但语义不同——G1=OOS 整体回撤，G2=任何切分回撤）；③ 价格笼子 `price_cage_config` 是按板块硬编码（main/gem/star/bse 四套）还是按 symbol 动态查询（universe_registry 已有 board 字段）——硬编码简单但板块迁移时需手动更新，动态查询灵活但增加运行时开销 | ① CPCV 参数：MVP 用 N=10/k=2 默认值（日频足够），Phase 1.5+ 分钟级策略按数据量调整 N（经验公式 N ≈ T/120，T=交易日数）；② catastrophic-veto 阈值：G2 的 0.15 是"任何切分最差回撤"硬红线，G1 的 0.15 是"OOS 整体回撤"——两者不冲突但语义须文档明确（G1=整体，G2=最差切分，G2 更保守）；③ 价格笼子：建议按 symbol 动态查询 universe_registry 的 board 字段（避免硬编码板块迁移问题），MVP 阶段可硬编码四套作为 fallback。MVP 阶段 schema 字段预留=合规底线，实际参数校准=Phase 1.5+ |
| J4 | 仓位管理 sizing_method 选择 + A 股高频因子纳入时机（v1.17.0 补） | §4.24 仓位管理 3 项对标 + A 股特色数据 2 项对标引出新决策点：① strategy_registry 的 `sizing_method` 默认值——fixed_fraction（最简单）/kelly（理论最优但参数敏感）/risk_parity（波动率反比）/conformal_kelly（Phase 2+），个人项目 MVP 用哪个；② A 股高频因子（日内收益/开盘后大单/尾盘占比）依赖 Level-2 数据，MVP 阶段用 AKShare（日线）还是采购商业 Level-2（Wind/iFinD），AKShare 声明仅学术用途——个人项目实盘是否触发商业授权要求；③ §4.24① Conformal Kelly 的核心发现"最简单方法最佳"（宽度稳定性>局部锐度）是否推广到其他模块——即 ZephyrAlpha 是否应遵循"简单优先"原则选择 sizing/drift-detection/risk-model 等模块的方法 | ① sizing_method：MVP 用 fixed_fraction（最简单，Conformal Kelly 论文也证明简单方法最佳），Phase 1.5+ 评估 fractional Kelly，Phase 2+ 评估 Conformal Kelly；② 高频因子：MVP 用日线因子（AKShare 日线可商用研究），Level-2 商业源采购=Phase 1.5+ AUM 增长后评估，个人项目实盘前须法律确认 AKShare 条款；③ 简单优先原则：建议在 project_memory 补一条"模块方法选择遵循简单优先——先 fixed_fraction/simple covariance/walk-forward，Phase 1.5+ 按实证数据升级复杂方法"（待用户确认后登记，与 Conformal Kelly 论文反直觉发现一致）。MVP 阶段 sizing=fixed_fraction + 因子=日线，Phase 1.5+ 按数据驱动升级 |
| O6 | chart_pattern MVP 范围 | 8 大类全做可能过度 | MVP 先做 candlestick_pattern + chart_pattern 2 类，其余按代码反查按需补 |
