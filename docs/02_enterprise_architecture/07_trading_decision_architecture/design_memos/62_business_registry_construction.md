---
ttl: permanent
doc_type: architecture_view
title: 业务资产注册表体系施工总案
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.36.1"
date: 2026-08-16
topic: business_registry_construction
scope: 07_trading_decision_architecture
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：2026-08-13 第一批/第二批建库会话 + 后续批次陆续建成全部 18 个业务注册表——factor（111 条）/strategy（59）/risk_limit（42）/technical_indicator（40）/execution_algo（6）/data_asset（166+）/chart_pattern（15）/field_dictionary（257）/experiment（5）及 universe/benchmark/cost_model/seat/regime_cycle/model/event_calendar/macro_indicator/portfolio_model，全部登记入 registry_of_registries.yaml（注册表总目录，数量以实测为准）。
>
> **最终成果**：18 个业务注册表全部建成，多轮审计 errors=0；回测环境三件套（股票池/基准/成本模型）按优先级先于被测对象三件套落地。
>
> **未做事项及原因**：因子 IC 实证回填未做——框架就绪但 222 个因子 ic 字段全空，需回测跑批回填，排期待定（跟踪表遗留 #56）；各注册表日常新增条目属正常运营，非施工缺口。

# 业务资产注册表体系施工总案

> 本备忘是 18 个业务资产注册表（因子/策略/技术指标/图形形态/股票池/基准/成本模型/执行算法/风控限额/数据资产/字段字典/实验/龙虎榜席位/周期分析/ML 模型/事件日历/宏观指标/组合构建模型）的**施工总案 + 审查底稿 + 调查索引**。
> 性质：**施工执行文档**，承载 schema 定稿、P0/P1/P2 阶段进度、裁定依据、数据来源映射，供 AI 与人类审查/升级/调查使用。
> 管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)；架构裁定见 [#ARCH-BREG-001](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)。
> 关联：[15_data_feature_layer_spec](15_data_feature_layer_spec.md)（因子工程总纲）｜ [20_first_batch_strategies](20_first_batch_strategies.md)（策略清单）｜ [16_technical_indicator_catalog](16_technical_indicator_catalog.md)（技术指标 why 层）｜ [52_backtest_framework_docking](52_backtest_framework_docking.md)（回测对接）
> **施工状态（2026-08-14 核验）：18/18 注册表已全部落盘**（条目数+commit 见 §3 总览；v1.35.0 起 12→14——图形形态循环审查裁定新增龙虎榜席位/周期分析 2 表；v1.36.0 起 14→18——机构五层栈+社区数据谱系对标新增 ML 模型/事件日历/宏观指标/组合构建模型 4 表），施工过程叙述已按 AI-DOCS-001 压缩折叠；§4 算法体系、§6/§7 schema、E1-E20 审计矩阵为长期有效规则，完整保留。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G62 业务资产注册表体系 |
| 架构议题 | #ARCH-BREG-001 |
| 临时工作文档 | [business_registry_consolidation_plan.md](../../../_working/business_registry_consolidation_plan.md)（施工方案+调研报告+裁定+schema 草案） |
| 真源入口 | [registry_of_registries.yaml](../../../registry_of_registries.yaml) tier_2 业务资产段 |
| 创建 | 2026-08-10 |
| 状态 | **12/12 全部落盘**（2026-08-13/14 核验）：universe 5 / benchmark 4 / cost_model 3 / factor 111 / strategy 59 / technical_indicator 40 / execution_algo 6 / risk_limit 62 / data_asset 166（15 源+76 数据集+75 作业）/ chart_pattern 15 / field_dictionary 257 / experiment 5；ROOR 已登记 7/12（5 表登记待补，见 §9.1）；AGENTS.md 12 表全部显化 |

## 2. 背景与问题诊断

项目已建成 3 层注册表治理体系（50+ 个，精确数量以 [ROOR](../../../registry_of_registries.yaml) `summary.total_registries` 为准，涵盖 gate/script/module/blueprint/error_code/术语表/目录/依赖/攻击场景/状态机），**唯独最核心的业务资产——因子、策略、指标、算法、风控限额、股票池、基准、成本模型——全部游离于统一入口外**（2026-08-13/14 起已由 12 注册表闭合）。

| 业务清单 | 旧行政状态 | 病根 |
|---|---|---|
| 因子库 | ❌ 0 注册表，散落代码 + 15/25 号文档 | 答不出"有多少因子" |
| 策略库 | ❌ 0 注册表，散落 20/24/25/26/27 号文档 | 答不出"有多少策略" |
| 技术指标清单 | ❌ 16 号骨架 draft + 代码，游离 | 非正式 SSoT |
| 股票池 | ❌ 散落各策略文档 | 回测不知道在哪些股票上跑 |
| 基准 | ❌ engine_base.py 仅 benchmark_symbol 裸字符串 | 回测无法计算超额收益 |
| 成本模型 | ❌ 散落 52 号（原 §G1，v1.34.0 注：52 号重建版无 §G1，引用悬空），无结构化 | 回测不扣成本结果失真 |
| 执行算法 | ❌ 散落 40 号 | 6 种算法无登记 |
| 风控限额 | ❌ 散落代码 + config | 9 种限额无登记 |
| 数据源 | ❌ 散落 15 号 + config/.env | 供应商无登记 |
| 字段字典 | ❌ 散落代码 contracts/ | 数据字段无总表 |
| 图形形态 | ❌ 0 登记的技术分析形态 | W底/缠论/波浪无算法记录 |
| 实验/回测目录 | ❌ 散落 51 号 + 代码 | 回测日志无法回溯 |

**治本**：建 12 个业务资产注册表（v1.36.0 扩为 18 个），分 P0/P1/P2 三阶段施工，全部登记 registry_of_registries.yaml，AGENTS.md 显化查询入口。

## 3. 18 个注册表总览

| # | 注册表 | registry_id | 真源文件 | tier | 优先级 | 状态 | 条目数 |
|---|---|---|---|---|---|---|---|
| 1 | 股票池 | REG-UNI-001 | `catalogs/universe_registry.yaml` | tier_2 | P0 | ✅ 已施工（2026-08-12，8e6436364d） | 5 |
| 2 | 基准 | REG-BMK-001 | `catalogs/benchmark_registry.yaml` | tier_2 | P0 | ✅ 已施工（2026-08-12，8e6436364d） | 4 |
| 3 | 交易成本模型 | REG-CST-001 | `catalogs/cost_model_registry.yaml` | tier_2 | P0 | ✅ 已施工（2026-08-12，8e6436364d） | 3 |
| 4 | 因子库 | REG-FCT-001 | `catalogs/factor_registry.yaml` | tier_2 | P1-A | ✅ 已施工（2026-08-13，ac75684951） | 111 |
| 5 | 策略库 | REG-STR-001 | `catalogs/strategy_registry.yaml` | tier_2 | P1-A | ✅ 已施工（2026-08-13，ac75684951） | 59 |
| 6 | 技术指标 | REG-IND-001 | `catalogs/technical_indicator_registry.yaml` | tier_2 | P1-A | ✅ 已施工（2026-08-13，eea122f432；2026-08-14 补登 Ichimoku） | 41 |
| 7 | 执行算法 | REG-EXA-001 | `catalogs/execution_algo_registry.yaml` | tier_2 | P1-B | ✅ 已施工（2026-08-13，c7701fcde6） | 6 |
| 8 | 风控限额 | REG-RLM-001 | `catalogs/risk_limit_registry.yaml` | tier_2 | P1-B | ✅ 已施工（2026-08-13，c6908d4678） | 62 |
| 9 | 数据资产 | REG-DATAFLOW-001 | `catalogs/data_asset_registry.yaml`（改名扩展） | tier_2 | P1-B | ✅ 已施工（2026-08-13，c7701fcde6；2026-08-14 v1.2.0 对标 JQData/quant666 补登 DS-077~102/JOB-076~082） | 199（15+102+82） |
| 10 | 图形形态 | REG-PAT-001 | `catalogs/chart_pattern_registry.yaml` | tier_2 | P1-B | ✅ 已施工（2026-08-13，206f48586f；2026-08-14 十五轮 SOTA 调研扩充，第十五轮判定可发现新增=0 收敛关闭） | 254 |
| 11 | 字段字典 | REG-FLD-001 | `catalogs/field_dictionary.yaml` | tier_2 | P2 | ✅ 已施工（2026-08-14，f0ebfdd5dc） | 257 |
| 12 | 实验/回测目录 | REG-EXP-001 | `catalogs/experiment_registry.yaml` | tier_2 | P2 | ✅ 已施工（2026-08-13，4b92a41a01） | 5 |
| 13 | 龙虎榜席位 | REG-SEAT-001 | `catalogs/seat_registry.yaml` | tier_2 | P1-B | ✅ 已施工（2026-08-14；图形形态循环审查裁定新增，与图形形态表正交——管"谁在买"；前提数据 DS-080/JOB-076 已登记，消费模块=CAND-SEAT-001） | 15 |
| 14 | 周期分析 | REG-CYCLE-001 | `catalogs/regime_cycle_registry.yaml` | tier_2 | P1-B | ✅ 已施工（2026-08-14；Gann 时间周期/周年日裁定新增，与 regime/emotion_cycle 正交——管"时间窗口"；无新增数据前提，消费模块=CAND-CYCLE-001） | 12 |
| 15 | ML 模型 | REG-ML-001 | `catalogs/model_registry.yaml` | tier_2 | P1-B | ✅ 已施工（2026-08-14；机构五层栈第四层 Model 补全——与 experiment 管"过程"正交，本表管模型"产物"版本/晋升/衰减） | 8 |
| 16 | 事件日历 | REG-EVT-001 | `catalogs/event_calendar_registry.yaml` | tier_2 | P1-B | ✅ 已施工（2026-08-14；12 事件类型全量 PIT 规则，event_driven 策略前提；数据=DS-091~097/JOB-079） | 12 |
| 17 | 宏观指标 | REG-MAC-001 | `catalogs/macro_indicator_registry.yaml` | tier_2 | P1-B | ✅ 已施工（2026-08-14；中美 15 指标发布纪律/修订政策/市场语义；数据=DS-101/SRC-FRED-001） | 15 |
| 18 | 组合构建模型 | REG-PFM-001 | `catalogs/portfolio_model_registry.yaml` | tier_2 | P1-B | ✅ 已施工（2026-08-14；等权/打分/MVO/BL/风险平价/最小方差/HRP/Barra 8 模型；MVP 纪律=OOS 跑不赢 1/N 不得晋升） | 8 |

> 路径前缀：`docs/01_policies_and_standards/_registry/`
> 优先级原则（project_memory）：回测三件套（universe/benchmark/cost_model）> 被测对象三件套（factor/strategy/indicator）> 交易/风控/数据/图形 > 字段字典/实验
> tier 说明（v1.33.0 修正）：18 表全部归 ROOR tier_2（数据与运行时级），落盘 YAML frontmatter 统一 `tier: tier_2_data_runtime`。原 v1.32.0 及之前将 6 个 P1 表误标 tier_1（治理与政策级），与落盘 YAML 及 ROOR 分层语义不符，已修正。
> 治理同步状态（2026-08-14 核验）：ROOR tier_2 段 18 表全部已登记（含 v1.35.0 SEAT/CYCLE + v1.36.0 ML/EVT/MAC/PFM）；AGENTS.md 业务资产速查 18 表全部显化。

## 4. 通用 Schema 设计原则（18 表共用）

1. **frontmatter 头部**对齐 [frontmatter_field_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml)：`module_id` / `ttl` / `schema_version` / `registry_id` / `name` / `name_zh` / `description` / `owner` / `tier` / `status` / `version` / `created` / `last_updated` / `related_arch` / `unique_key`
2. **entry_schema 按 DB 表设计**预留迁移：每条记录有 `id`(PK) / `created_at` / `updated_at` / `version` / `status`，未来可一键迁 PG
3. **编号格式**：`registry_id` = `REG-{NAME}-{NNN}`；`entry id` = `{PREFIX}-{DOMAIN}-{NNN}`（对齐 module_id_registry allocation_rules）
4. **关联字段**：`module_id` 关联 depgraph 蓝图号（MOD- 前缀）/ `doc_ref` 关联 design memo / `code_path` 关联代码
5. **状态机**对齐 [module_lifecycle_status_vocabulary.yaml](../../../01_policies_and_standards/_registry/vocabularies/module_lifecycle_status_vocabulary.yaml)：`candidate / experimental / active / deprecated / retired`
6. **性能指标字段**（IC/Sharpe/容量等）运行时可空，未来进 DB 时序存储
7. **variant 字段**：策略/形态层用 `variant_of` 可选分组（单向引用，不强制层级）
8. **半派生**：手写真源（编号/状态/语义）入 git，脚本反查补全（code_path/module_id/依赖）
9. **版本字段**（v1.2.0 新增，对标 Feast Feature View Versioning 2026-03-31）：每条 entry 含 `version` 字段记录 schema-significant 变更；schema/UDF 改动触发版本快照，metadata-only 改动（description/tags/TTL）原地更新不建版本
   - **版本策略选项**（v1.4.0 新增，对标 [apxml Feature Versioning Strategies 2026](https://apxml.com/courses/feature-stores-for-ml/chapter-5-governance-security-mlops/feature-versioning-strategies)）：① Semantic Versioning（MAJOR.MINOR.PATCH，当前采用，Feast 模式）；② Immutable Version（UUID/content hash，最强 reproducibility——任何变更生成全新版本 ID，旧版本永久不变；[Atlan 2026-03](https://atlan.com/know/ai-model-versioning-best-practices/)："Every model version should be immutable once registered"）；③ Timestamped；④ Branch-based
   - **个人项目选择**：YAML 阶段用 ① Semantic（git commit hash 天然提供 ② 的 reproducibility 保证）；DB 迁移后若需审计级 reproducibility 可升级 ②（content hash 作 version 值），schema 的 `version` 字段兼容两种策略
   - **版本可复现性三要素**（v1.6.0 新增，对标 [beefed.ai 2026 Feature Registry](https://beefed.ai/en/feature-registry-governance-best-practices) + MLflow bundling）：成熟 registry 要求 entry 绑定 ① `code_commit`（代码 commit hash，§4.7 E5b 检查）+ ② 数据血缘三要素 `source_uri`/`transform_script_hash`/`labeler_id` + ③ `materialization_ts`（物化时间戳）。YAML 阶段：`code_commit` 用 git blame 天然提供，`source_uri`/`transform_script_hash`/`labeler_id` 通过 `code_path`+`doc_ref` 间接覆盖，`materialization_ts`=`updated_at`；factor/strategy schema 已预留 `code_commit` 字段，DB 迁移后升级为显式四字段绑定
   - **SHA256 manifest 选项**（v1.10.0 新增，对标 [OmniBioAI ModelHub 2026-08-08](https://github.com/OmniBioAI/omnibioai-model-registry) + [Ollama content-addressable storage](https://deepwiki.com/ollama/ollama/4.2-model-registry-and-layers)）：当 entry 需 bit-level reproducibility（审计/监管级）时，在 `code_commit` 外追加 `content_hash` 字段——对 entry 关联全部产物（源码+formula+params+inputs/outputs）计算 SHA256 生成 `sha256sums.txt` manifest。**个人项目选择**：YAML 阶段 git commit hash 天然提供 content 追溯（git blob 即 content-addressable storage），**无需额外 SHA256 manifest**；DB 迁移后若需监管级 reproducibility（如 EU AI Act 2026-08-02 高风险 AI 审计）可升级显式 `content_hash` 字段，schema 已预留位置
   - **防过度工程**：[ManifoldKit #1934 2026-06](https://github.com/roryford/ManifoldKit/issues/1934) 对 SHA256 blob store 的对抗审查结论"over-engineered for single-user on-device app"——个人单用户项目 git commit hash 足够，SHA256 manifest 是 DB+监管阶段可选项非必选项
10. **衰减检测字段**（v1.2.0 新增，对标 Alexander & Fabozzi 2026 MRP + Vibe-Trading 2026-07 衰减状态机）：strategy/factor entry 预留 `decay_detection_method` / `last_decay_scan_at` / `decay_state` 字段。Vibe-Trading 衰减状态机：`created → benching → active → monitoring → decayed → disabled`，恢复条件 IC ratio > 0.7
11. **Schema 演进兼容性**（v1.3.0 新增，对标 Confluent Schema Registry + datalakehouse 2026-02）：schema 变更默认走 **Additive-Only**（只增不删/不重命名，新字段有默认值=BACKWARD 兼容，直接部署）；breaking 变更（删/改/重命名）走 **Expand-Contract** 3 阶段（Expand 共存→Migrate 迁移→Contract 清理）。`schema_version` 区分兼容（1.0→1.1）vs breaking（1.x→2.0）。详见 §4.11 EVOLVE_SCHEMA 算法
12. **变更与退役治理**（v1.3.0 新增，对标 theFactory 2026-07 + Feast Versioning）：entry 变更按 `change_type` 分类——metadata 原地更新 / schema_sig+code_ref 触发版本快照 / status 走退役流程（详见 §4.9 EVOLVE_ENTRY）。退役 3 阶段 active→deprecated（90天宽限，最少30天）→retired（无活跃引用）→物理删除（退役满1年+ARCH审批），详见 §4.10 RETIRE_ENTRY。retired 记录保留审计追溯，不默认删除

### 4.4 算法体系导航图（v1.10.0 新增，v1.11.0 更新为 12 算法 + 7 阶段，v1.13.0 补横切查询升级为 13 算法）

§4.5-§4.16 共 12 个生命周期施工算法 + §4.18 DIFF_ENTRY 横切查询算法（共 13 算法）。本导航图给出 13 算法的调用关系图 + 触发时机 + 输入输出依赖，完整覆盖"建→上→改→测→应/回→退→迁"全生命周期；DIFF_ENTRY 为任意阶段可调用的只读查询（非状态变更）。

> 📌 **§4 结构说明**（v1.21.0 新增，辅助导航）：§4 含两类内容——
> - ① **算法定义**（§4.4 导航图 / §4.5-§4.16 生命周期算法 / §4.18 横切查询 / §4.20 监管变更 / §4 原则 1-12）：施工 MUST 读
> - ② **研究对标**（§4.17 第一轮 / §4.19 第二轮 / §4.21-§4.39 第三至二十一轮）：审查底稿，记录每轮全网搜索的"比现有方法更好"发现，供调查溯源，按需查阅
>
> 读者优先读 ①，② 按需查阅。研究对标随版本累积增长，新增轮次应精简（≤50 行/轮，仅记已落地项+1-2 项 Phase 1.5+ 评估）。

**13 算法按阶段分组**（建→上→改→测→应/回→退→迁 + 横切查询）：

```
阶段1 建  CONSTRUCT_REGISTRY(§4.5) — Step4 调 §4.15 construct_order；Step6 调 §4.7 E1-E20
阶段2 上  PROMOTE_ENTRY(§4.13)     — 9 门禁(G1-G9)；渐进式部署 shadow→canary→full
阶段3 改  EVOLVE_ENTRY(§4.9)       — metadata/schema_sig/code_ref/status 分类；breaking→§4.11
阶段4 测  DECAY_SCAN(§4.8)         — MVP: profit_factor+z_score；Phase1.5+: cusum_ph_bocpe 2/3投票
阶段5 应/回 ADAPT_STRATEGY(§4.12) / ROLLBACK_ENTRY(§4.14)
         — ADAPT: Step0 baseline校验→Step1.5 原因分类→refit或退役
         — ROLLBACK: 实盘异常回退已知良好版本（7天冷却防flip-flop）
阶段6 退  RETIRE_ENTRY(§4.10)      — active→deprecated(90天宽限)→retired；级联用 §4.15 transitive_deps
阶段7 迁  MIGRATE_REGISTRY(§4.16)  — R1-R7 七阶段；按 §4.15 construct_order 逆序；R6 不可逆

横切（任意阶段可调用）:
  AUDIT_REGISTRY(§4.7)     — E1-E20 一致性审计
  EVOLVE_SCHEMA(§4.11)     — schema 演进，breaking 走 Expand-Contract
  DEPENDENCY_RESOLVE(§4.15)— 依赖解析（拓扑序/级联/影响范围/迁移顺序）
  DIFF_ENTRY(§4.18)        — 版本差异查询（EVOLVE/PROMOTE/EVOLVE_SCHEMA 调用）

跨文档职责边界:
  RUN_BACKTEST → [52_backtest_framework_docking](52_backtest_framework_docking.md)
  ATTRIBUTION  → 54 号 performance_attribution_report
  本文档仅登记 experiment_registry 的 backtest_bias_checks + attribution_result 字段（§7.2），不重复 52/54 号执行逻辑
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

18 个注册表统一遵循以下 8 步施工算法，确保 schema-代码-文档三方一致性。

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
      - E14 回测数据偏差检查（backtest_bias_checks/survivorship_free/pit_available/universe PIT，v1.18.0+v1.24.0 c 维度+v1.25.0 d 维度）
      - E15 LLM 前瞻偏差 + A 股 Tradability Mask 检查（v1.19.0+v1.32.0 扩展）
      - E16 因子冗余 + 归因稳定性 DASH 检查（v1.20.0+v1.32.0 扩展）
      - E17 因果验证 + 设定结构 collider 检查（v1.21.0+v1.31.0 扩展）
      - E18 LAP 前瞻污染 + Temporal Leakage 测量检查（v1.22.0+v1.31.0 扩展）
      - E19 因子构造偏差审计 LIB（v1.22.0）
      - E20 RMT 去噪因子相关性矩阵审计（v1.23.0）

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

12 注册表通过 FK 字段相互引用，形成业务资产关系图。本矩阵明确每条 FK 的引用方→被引用方→基数（v1.33.0 修正：补 factor.benchmark_id / experiment.benchmark_id / experiment.cost_model_ref / data_asset.produced_by_source / data_asset.consumed_by_jobs 5 条遗漏 FK，全量 32 条）。

| 引用方（FK 所在） | FK 字段 | 被引用方 | 基数 | 说明 |
|---|---|---|---|---|
| universe | used_by_strategies | strategy | 1:N | 池被哪些策略使用 |
| universe | data_source | data_asset.source_id | N:1 | 池数据来源 |
| benchmark | underlying_universe | universe | N:1 | 基准基于哪个池 |
| benchmark | data_source | data_asset.source_id | N:1 | 基准数据来源 |
| benchmark | used_by_strategies | strategy | 1:N | 基准被哪些策略对标 |
| cost_model | used_by_strategies | strategy | 1:N | 成本模型被哪些策略使用 |
| factor | universe | universe | N:1 | 因子适用池 |
| factor | benchmark_id（v1.33.0 补） | benchmark | N:1 | 因子评估基准（计算超额 IC/IR） |
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
| data_asset.sources | provides_datasets | data_asset.datasets | 1:N | source 提供 datasets（self-ref 三实体） |
| data_asset.datasets | produced_by_source（v1.33.0 补） | data_asset.sources | N:1 | dataset 由哪个 source 产出（self-ref） |
| data_asset.datasets | produced_by_jobs | data_asset.jobs | N:N | dataset 由哪些 job 产出（self-ref） |
| data_asset.datasets | consumed_by_jobs（v1.33.0 补） | data_asset.jobs | N:N | dataset 被哪些 job 消费（self-ref） |
| chart_pattern | used_by_factors | factor | 1:N | 形态被哪些因子引用 |
| chart_pattern | variant_of | chart_pattern | N:1 | 形态变体（单向，self-ref） |
| experiment | target_id | factor/strategy/indicator/pattern/risk_rule/execution_algo | N:1 | 实验测什么 |
| experiment | universe | universe | N:1 | 实验在哪个池上跑 |
| experiment | benchmark_id（v1.33.0 补） | benchmark | N:1 | 实验对标基准 |
| experiment | cost_model_ref（v1.33.0 补） | cost_model | N:1 | 实验扣哪个成本模型 |
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

  E5b【commit 绑定检查】（v1.4.0 新增，对标 beefed.ai compute_git）
    # code_path + commit 双绑定确保可复现；YAML 阶段 git blame 天然提供（可选），DB 阶段 MUST 非空
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

  E11【数据质量监控登记检查】（v1.4.0 新增；对标 metricgate 4 层监控 + apxml PSI/KS + RisingWave 三种静默失败模式）
    # 数据质量=因子输入端退化（null_rate/drift/range），与衰减检测（输出端，§4.8 DECAY_SCAN）互补——alert on earliest layer
    # RisingWave 三种静默失败模式（infra 监控全绿但数据已坏，需 data-aware 监控）：
    #   ① Freshness Lag（pipeline 运行但特征停止更新 → freshness 检查 staleness>SLA）
    #   ② Data Incompleteness（丢行/schema 变更 → null_rate >2x baseline 告警，2% 噪声 vs 15% 管道断裂）
    #   ③ Distribution Drift（分布偏移 → drift_method 检查 PSI/KS，PSI>0.2 主要漂移）
    for entry in entries:
      if registry_id in {"REG-FCT-001", "REG-STR-001"}:  # factor/strategy 需数据质量监控
        if not entry.get("data_quality_policy"):
          warnings.append("未声明 data_quality_policy: " + entry.id + "（登记 null_rate/drift/freshness 检测策略）")
        else:
          policy = entry.data_quality_policy
          if "null_rate" not in policy:
            warnings.append("data_quality_policy 缺 null_rate: " + entry.id + "（RisingWave 失败模式 2 Data Incompleteness）")
          if "drift_method" not in policy:
            warnings.append("data_quality_policy 缺 drift_method: " + entry.id + "（失败模式 3 Distribution Drift，psi 或 ks，PSI<0.1 稳定/0.1-0.25 轻微/>0.2 主要漂移）")
          if "freshness" not in policy:
            warnings.append("data_quality_policy 缺 freshness: " + entry.id + "（失败模式 1 Freshness Lag，登记 SLA 阈值如 daily 特征 staleness>300s 告警）")

  E12【baseline 保存完整性检查】（v1.5.0 新增；对标 LuxAlgo 2026-08-03 + Pomegra 2026）
    # LuxAlgo: "Without that baseline, it is difficult to distinguish normal variance from a genuine change in the edge"
    # baseline MUST 在策略 deployment 时保存，是 §4.8 DECAY_SCAN + §4.12 ADAPT_STRATEGY 的前提
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
            warnings.append("live/monitoring/decayed 策略缺 baseline 字段: " + entry.id + " " + missing_baseline + "（衰减检测前提，deployment 时保存完整 baseline）")
          # decay_threshold 必填（§4.8 DECAY_SCAN 恢复判定基准）
          if not entry.get("decay_threshold"):
            warnings.append("缺 decay_threshold: " + entry.id + "（§4.8 DECAY_SCAN 恢复判定基准，默认 0.7）")

  E13【语义漂移检查】（v1.10.0 新增；对标 oracles.cloud 2026-01 Data Contracts + neojn 2026-05 Feature Store Drift）
    # 漂移分 3 类：① Schema drift（结构，§4.11 EVOLVE_SCHEMA + E10 覆盖）② Statistical drift（分布/null_rate，E11 覆盖）
    #   ③ Semantic drift（语义，本检查）——"same field but meaning changes"：币种/复权口径/时区/null 语义/分类编码变了，
    #   字段名/类型/分布都没变但"意思"变了，最难检测（neojn: "the system continues serving predictions, just quietly wrong ones"）
    # 检测方法：a. data_contract 声明 business_definition+unit+adjust_method（§7.1 schema 已有）；
    #   b. 定期 reconciliation jobs（从原始事件日志重算特征对比在线返回值）；c. null 语义一致性（缺失≠零值，混淆反转风险信号）；
    #   d. 默认填充策略审计（zero fill 对 counter 无害但对 ratio 类因子 catastrophic）
    for entry in entries:
      if registry_id in {"REG-FCT-001", "REG-STR-001"}:
        policy = entry.get("data_quality_policy", {})
        # 检查 a: data_quality_policy 应声明 semantic_contract（字段语义契约）
        if "semantic_contract" not in policy:
          warnings.append("data_quality_policy 缺 semantic_contract: " + entry.id + "（第3类 semantic drift：复权口径/币种/时区/null语义；登记关键字段 unit/adjust_method/null_semantics）")
        else:
          contract = policy.semantic_contract
          # 检查 c: null_semantics 声明（缺失≠零值）
          if "null_semantics" not in contract:
            warnings.append("semantic_contract 缺 null_semantics: " + entry.id + "（missing≠zero，缺失比率因子≠零利用率，混淆反转风险信号）")
          # 检查 d: default_fill_policy 审计（零填充对比率类因子有害）
          if contract.get("default_fill_policy") == "zero" and "ratio" in str(entry.get("formula", "")).lower():
            warnings.append("default_fill_policy=zero 对 ratio 类因子有害: " + entry.id + "（zero fill harmless for counters but catastrophic for ratios）")
        # 检查 b: reconciliation 非必填（成本较高），仅建议 Phase 1.5+ 启用，不告警

  E14【回测数据偏差检查】（v1.18.0 新增，v1.24.0 扩 c 维度 + v1.25.0 扩 d 维度；对标 preprints.org 2026-06 三分类偏差 taxonomy + digitalninjasystems 2026-05 + thedatascientist 2026-06）
    # E11 查特征统计漂移、E13 查语义漂移，E14 查**数据源头偏差**——回测数据本身是否含生存/前瞻偏差（更根本的"数据是否可信"）
    # preprints.org 2026-06 三分类：① universe-membership contamination（生存偏差，仅含存活公司，US equity 年化高估 1-3%）
    #   ② price-data forward leakage（前瞻偏差，用决策时未可知信息，mean-reversion 虚增 40-60%）
    #   ③ stop-exit sequencing violations（止损/止盈在当日收盘价而非次日开盘执行）
    # 仅做"声明完整性"检查（偏差检测属 52 号回测框架职责，本表只管元数据登记）：
    #   a. experiment_registry 回测 entry 声明 backtest_bias_checks（v1.18.0 §7.2）
    #   b. data_asset_registry dataset 声明 survivorship_free / pit_available（v1.18.0 §6.2.3）
    #   c. universe_registry 声明 pit_constituent_construction / delisted_handling（v1.24.0）
    #   d. data_asset_registry 声明 as_of_date_semantics（v1.25.0）
    if registry_id == "REG-EXP-001":  # experiment_registry
      for entry in entries:
        if entry.experiment_type in {"backtest", "walk_forward", "param_search"}:
          bias = entry.get("backtest_bias_checks")
          if not bias:
            warnings.append("回测实验缺 backtest_bias_checks: " + entry.id + "（preprints.org 三分类：survivorship/lookahead/stop_exit，未声明=未做偏差治理）")
          else:
            # 三分类都须声明（passed/failed/unknown，unknown 也算声明——诚实记录"未检查"）
            for bias_type in {"survivorship", "lookahead", "stop_exit"}:
              if bias_type not in bias:
                warnings.append("backtest_bias_checks 缺 " + bias_type + ": " + entry.id + "（三分类之一，未声明=该类偏差未评估）")
    if registry_id == "REG-DATAFLOW-001":  # data_asset_registry
      for ds in datasets:
        # 行情类 dataset（price/quote）须声明生存偏差状态
        if "price" in str(ds.get("name", "")).lower() or "quote" in str(ds.get("name", "")).lower():
          if ds.get("survivorship_free") is None:
            warnings.append("行情 dataset 缺 survivorship_free 声明: " + ds.dataset_id + "（生存偏差使 US equity 年化高估 1-3%；AKShare 日线=unknown，商业源 Norgate/Compustat=true）")
        # 财报类 dataset 须声明 PIT 可用性 + 公布滞后
        if "fundamental" in str(ds.get("name", "")).lower() or "earnings" in str(ds.get("name", "")).lower():
          if ds.get("pit_available") is None:
            warnings.append("财报 dataset 缺 pit_available 声明: " + ds.dataset_id + "（前瞻偏差是 silent killer，财报须按公布日期非财报期对齐）")
          if ds.get("earnings_lag_days") is None:
            warnings.append("财报 dataset 缺 earnings_lag_days: " + ds.dataset_id + "（财报公布平均滞后天数，用于 PIT 对齐校验）")

  E15【LLM 前瞻偏差检查 + A 股 Tradability Mask 检查】（v1.19.0 新增，v1.32.0 扩展；对标 Look-Ahead-Bench arXiv:2601.13770 + KTD-FIN arXiv:2605.28359 + arXiv:2507.07107v2 Mask-First Design）
    # E14 查传统回测偏差，E15 查 LLM 时代第四类偏差——memorization leakage（记忆泄漏）：
    #   LLM 训练语料含回测期未来信息，模型凭记忆而非预测给信号（"用 2023 的 GPT-4 测 2020 策略=拿着明天报纸买今天彩票"）
    # KTD-FIN 4-level masking：bright/stock-blind/date-blind/blinded 四级脱敏，最强攻击者 top-5 ticker 恢复率仅 10.2%
    # 仅查声明完整性（LLM 前瞻偏差检测属 52 号回测框架职责）：
    #   a. data_asset dataset 声明 llm_training_cutoff；b. 声明 lookahead_test_method；c. experiment 声明 llm_lookahead_check_result
    if registry_id == "REG-DATAFLOW-001":  # data_asset_registry
      for ds in datasets:
        # 仅对 LLM-relevant dataset 检查（news/llm_embedding/llm_signal 等关键字）
        ds_name = str(ds.get("name", "")).lower()
        is_llm_relevant = any(k in ds_name for k in {"news", "llm", "embedding", "nlp", "sentiment_text", "report_text"})
        if is_llm_relevant:
          if ds.get("llm_training_cutoff") is None:
            warnings.append("LLM-relevant dataset 缺 llm_training_cutoff: " + ds.dataset_id + "（回测期 < 训练截止日期 = 高前瞻偏差风险；MVP 未用 LLM 填 N/A，Phase 2+ MUST 声明）")
          if ds.get("lookahead_test_method") is None:
            warnings.append("LLM-relevant dataset 缺 lookahead_test_method: " + ds.dataset_id + "（KTD-FIN 4-level masking；MVP 填 N/A，Phase 2+ MUST 至少跑 blinded 级）")
    if registry_id == "REG-EXP-001":  # experiment_registry
      for entry in entries:
        # 仅对 LLM-driven 回测实验检查（tags 含 llm 等）
        tags = entry.get("tags", []) or []
        is_llm_driven = ("llm" in str(tags).lower() or
                         "llm_generated" in str(tags).lower() or
                         entry.get("target_type") == "strategy" and
                         any("llm" in str(t).lower() for t in tags))
        if is_llm_driven and entry.experiment_type in {"backtest", "walk_forward", "param_search"}:
          llm_check = entry.get("llm_lookahead_check_result")
          if not llm_check:
            warnings.append("LLM-driven 回测实验缺 llm_lookahead_check_result: " + entry.id + "（LLM 回测 MUST 评估记忆泄漏；MVP 未用 LLM 填 {applicable: false, reason: ...}，Phase 2+ MUST 评估）")
          else:
            # applicable=true 时须有 masking_level + alpha_decay 测试结果
            if llm_check.get("applicable", True):
              if "masking_level" not in llm_check:
                warnings.append("llm_lookahead_check_result 缺 masking_level: " + entry.id + "（KTD-FIN 4-level，MUST 至少跑 blinded 级）")
              if "alpha_decay" not in llm_check:
                warnings.append("llm_lookahead_check_result 缺 alpha_decay: " + entry.id + "（alpha decay 跨 regime 测量是区分真预测能力 vs 记忆回放的关键指标）")
    # v1.32.0 新增：A 股 Tradability Mask 检查（对标 arXiv:2507.07107v2 Mask-First Design）
    # A 股 ±10%/±20% 涨跌停板使部分收盘价不可执行——标准实现先读价格再过滤行，
    # 污染通过 MA/correlation/rank 静默传播（upstream contamination），实证虚增 IC 18% + 降低 Sharpe 0.44
    # 这是特殊的 look-ahead bias（使用不可执行的价格仿佛可执行），A 股因子计算实验 MUST 声明 tradability_mask_policy
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
            warnings.append("A 股因子实验缺 tradability_mask_policy: " + entry.id + "（涨跌停板上游污染虚增 IC 18%+降低 Sharpe 0.44；MUST 填 mask_first（数据加载时构造掩码贯穿算子），row_filter 不足，none=未处理 warning highlight）")
          elif tmp == "none":
            warnings.append("tradability_mask_policy=none: " + entry.id + "（未处理涨跌停板上游污染，回测结果可能虚高 IC 18%，MUST 实现 mask_first）")

  E16【因子冗余/相关性检查 + 归因稳定性检查】（v1.20.0 新增，v1.32.0 扩展归因稳定性；对标 EntroPy 2026-05 redundancy.py + factordbms + DASH arXiv:2605.21492）
    # E1-E15 查单因子属性，E16 查**因子间关系 + 归因稳定性**——多个高相关因子=伪多样化，组合实际风险被低估
    # EntroPy 三维度：① effective signal correlation（截面）② factor long-short return correlation（时序）③ exposure-vector cosine similarity
    # 同 correlation_group 的因子 = 高相关簇，MUST 有一个 independent + 其余 redundant/orthogonal（r>0.7 信息重叠）
    if registry_id == "REG-FCT-001":  # factor_registry
      for entry in entries:
        if entry.get("correlation_group") is None:
          warnings.append("因子缺 correlation_group: " + entry.id + "（同组因子高相关=伪多样化，组合风险被低估；MVP 按因子 10 分类粗分，Phase 1.5+ 三维度检测精细化）")
        if entry.get("redundancy_status") is None:
          warnings.append("因子缺 redundancy_status: " + entry.id + "（independent=独立信号/redundant=冗余/orthogonal=正交；同组 MUST 至少 1 个 independent）")
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
            warnings.append("correlation_group " + str(g) + " 内无 independent 因子（" + str(len(members)) + " 个全为 redundant/orthogonal/未声明）：同组 MUST 至少 1 个 independent 作为代表信号")
    # v1.32.0 新增：归因稳定性检查（DASH 不可能性定理，Lean 4 机器验证 248 定理）
    # collinearity 下 SHAP 排名结构性不稳定——faithfulness+stability+completeness 三者不可兼得，68% 公开数据集归因翻转
    # correlation_group 非空的因子 SHOULD 声明 attribution_stability；flip_rate>20% = 归因不稳定（冗余方向判断本身可能不可靠）
    if registry_id == "REG-FCT-001":  # factor_registry
      for entry in entries:
        cg = entry.get("correlation_group")
        if cg is not None:
          as_obj = entry.get("attribution_stability")
          if as_obj is None:
            warnings.append("correlation_group 非空因子缺 attribution_stability: " + entry.id + "（DASH：collinearity 下 SHAP 排名结构性不稳定，68% 数据集归因翻转；MVP 填 {method: none}，Phase 1.5+ ML 因子 SHOULD 启用 DASH M≥5 跨模型聚合）")
          else:
            flip_rate = as_obj.get("flip_rate")
            if flip_rate is not None and flip_rate > 0.20:
              warnings.append("attribution_stability flip_rate>20%: " + entry.id + " flip_rate=" + str(flip_rate) + "（归因不稳定，冗余方向判断可能不可靠，MUST 人工裁定冗余方向，SHOULD 增加 model_count 至 ≥25）")

  E17【因果验证 + 设定结构检查】（v1.21.0 新增，v1.31.0 扩展设定结构；对标 causal-quant v0.4.1 + CFA Institute 2025 Factor Mirage López de Prado）
    # E17 查**因果属性 + 设定结构**——相关性≠因果性，回测可能因混淆变量/luck/选择偏差虚高
    # causal-quant 钉住回测撒谎三种方式：luck/confounding/selection across everything you tried（声明 DAG→证伪电池→H-score）
    # 因果验证 gate 时机：注册时（非上线时）——注册即声明因果图，避免事后合理化
    # v1.31.0 Factor Mirage：collider（碰撞变量）比 confounder 更危险——含 collider 模型展现更高 R²+更低 p-value，
    #   计量教规主动偏好这类错误模型，系数符号可翻转（+0.08→−0.04）；仅声明 causal_graph 不够，MUST 显式枚举 confounder/collider
    if registry_id == "REG-FCT-001":  # factor_registry
      for entry in entries:
        if entry.get("causal_graph") is None:
          warnings.append("因子缺 causal_graph: " + entry.id + "（因子注册时 MUST 声明因果图/经济逻辑；MVP 可填自然语言如'高ROE→持续盈利能力→股价上涨'，Phase 1.5+ 接 causal-quant 证伪电池补 H-score）")
        # v1.31.0 新增：causal_structure 设定结构检查（Factor Mirage collider/confounder）
        cs = entry.get("causal_structure")
        if cs is None:
          warnings.append("price-derived 因子缺 causal_structure: " + entry.id + "（collider 比 confounder 更危险，含 collider 模型更高 R²+更低 p-value，系数符号可翻转；MVP 用自然语言填 confounders/colliders，collider 非空=设定风险标志）")
        elif cs.get("colliders"):  # collider 非空 = warning highlight
          warnings.append("⚠️ 因子 " + entry.id + " causal_structure.colliders 非空: " + str(cs.get("colliders")) + "（Factor Mirage 风险：collider 被因子和收益共同影响，更强关联无法货币化=海市蜃楼，MUST 审视是否应移除该控制变量）")

  E18【LLM 前瞻污染检测 LAP + Temporal Leakage 测量】（v1.22.0 新增，v1.31.0 扩展 Temporal Leakage；对标 arXiv:2512.23847v2 LAP + FinCAD arXiv:2605.24564 + MemGuard-Alpha arXiv:2603.26797 + arXiv:2608.02985v1 Temporal Leakage Measurement）
    # E15 查数据侧防御（KTD-FIN masking），E18 查**模型侧诊断 + 测量**——LLM 权重内已记忆未来结果，数据管道审计看不见
    # LAP（Lookahead Propensity）= P(up)+P(down)，用"日期-only 召回查询"（只给 firm+ticker+日期）估计 LLM 内化未来结果概率；
    #   训练期内显著为正，越过 cutoff 后坍塌至近零；污染检验回归 Y_{t+1}=β₁μ̂_t+β₂LAP+β₃(LAP×μ̂_t)，β₃>0 即前瞻污染指征
    # v1.31.0 Temporal Leakage：标准 pre/post-cutoff 检查 uninformative——recency 模仿 leakage，被动回测数学不可分离；
    #   detection 回答"是否泄漏"，measurement 回答"泄漏多少"（matched clean control 全局测量+leakage-adjusted score，boundary detection 边界定位）
    # 仅查声明完整性（LAP/Temporal Leakage 计算属 LLM 推理层职责）
    if registry_id == "REG-EXP-001":  # experiment_registry
      for entry in entries:
        tags = entry.get("tags", []) or []
        is_llm_driven = ("llm" in str(tags).lower() or
                         "llm_generated" in str(tags).lower())
        if is_llm_driven and entry.experiment_type in {"backtest", "walk_forward"}:
          lap_check = entry.get("lap_check_result")
          if not lap_check:
            warnings.append("LLM-driven 回测实验缺 lap_check_result: " + entry.id + "（LLM 可能凭记忆而非预测给信号；MVP 未用 LLM 填 {applicable: false}，Phase 2+ MUST 跑 LAP×LLM 交互项回归，β₃>0=前瞻污染）")
          # v1.31.0 新增：temporal_leakage_measurement 测量声明检查（warning 级，MVP 不阻断）
          tlm = entry.get("temporal_leakage_measurement")
          if tlm is None:
            warnings.append("LLM-driven 回测实验缺 temporal_leakage_measurement: " + entry.id + "（标准 pre/post-cutoff 检查 uninformative，recency 模仿 leakage；MVP 无 LLM 回测填 none，Phase 1.5+ origin=llm_generated 实验 SHOULD 启用 matched_control 测量泄漏剂量）")
          elif tlm.get("method") == "matched_control" and tlm.get("leakage_score", 0) > 0:
            warnings.append("LLM 回测实验 " + entry.id + " temporal_leakage_measurement.leakage_score=" + str(tlm.get("leakage_score")) + " > 0（检测到泄漏剂量，MUST 审视 leakage-adjusted score 是否仍支持结论）")

  E19【因子构造偏差审计 LIB】（v1.22.0 新增；对标 arXiv:2604.07880 2026-04 企业债因子动物园 + Open Bond Asset Pricing）
    # E19 查**因子构造方法学偏差**——企业债因子动物园复制危机揭示两个偏差：
    #   ① Latent Implementation Bias (LIB)：同一噪声价格进入信号和收益分母，相关误差被误认为 premium
    #      （A 股类比：复权价/成交量既是因子输入又是收益计算分母）
    #   ② ex-post 收益过滤嵌入未来信息：去极值/去流动性差样本用了全期统计量
    # 纠正两偏差后 108 个企业债因子多数不再显著。仅对 price/volume 衍生因子检查（基本面因子无 LIB 风险）
    if registry_id == "REG-FCT-001":  # factor_registry
      for entry in entries:
        inputs = str(entry.get("inputs", [])).lower()
        is_price_derived = any(k in inputs for k in {"close", "vwap", "price", "volume", "amount", "open", "high", "low"})
        if is_price_derived:
          if entry.get("lib_audit") is None:
            warnings.append("price-derived 因子缺 lib_audit: " + entry.id + "（信号与收益共用噪声数据源=LIB；MVP 可填 {checked: false, reason: 'manual_factor'}，Phase 1.5+ MUST 审计信号-收益数据源独立性）")
          if entry.get("ex_post_filter_audit") is None:
            warnings.append("因子缺 ex_post_filter_audit: " + entry.id + "（ex-post 去极值/去流动性差用全期统计量=嵌入未来信息；MVP 可填 {checked: false}，Phase 1.5+ MUST 审计过滤是否用 walk-forward 统计量）")

  # E20【RMT 去噪因子相关性矩阵审计】（v1.23.0 新增；对标 arXiv:2507.17211v2 EFS + arXiv:2601.07687v4 + Marchenko-Pastur 1967）
  # E16 查冗余声明，E20 查**冗余检测的方法学质量**——因子相关性矩阵在 N_factors 较大/T_observations 有限时含大量噪声特征值
  # Marchenko-Pastur 律：纯噪声特征值上界 λ+ = σ²(1+√q)²（q=N/T），落在 [λ-, λ+] 内的特征值是噪声而非信号，
  #   MUST 用 RMT 去噪（clipping/shrinkage）后再计算冗余指标，否则噪声驱动的伪相关被误判为因子冗余
  # EFS 证明 RMT 去噪+正则化 QP 在美股/港股/A股均优于未去噪基线且无额外调参成本；
  #   物理信息奇异值学习指出标准 RMT 假设平稳+有界谱，Phase 2+ 可用神经网络估计器替代解析收缩
  # 仅查声明完整性（RMT 计算属因子组合层职责）
  if registry_id == "REG-FCT-001":  # factor_registry
    for entry in entries:
      redundancy = entry.get("redundancy_status")
      if redundancy in {"independent", "redundant", "orthogonal"}:
        rmt = entry.get("rmt_denoised")
        if rmt is None:
          warnings.append("声明 redundancy_status 的因子缺 rmt_denoised: " + entry.id + "（因子相关性矩阵含 Marchenko-Pastur 噪声特征值，q=N/T>0.1 时 MUST 去噪；MVP 可填 {applicable: false, reason: 'low_factor_count'}，Phase 1.5+ 因子数>20 时 MUST 启用 RMT clipping 去噪）")

  return audit_report
```

**审计方法论教训**（project_memory）：文档-代码漂移检测 MUST 用 Select-String 核对实码符号，不能仅凭上一版审计快照（40 号 v2.6.0 教训：5 项 gap 实现于 v2.5.0 之后但文档未回填）。本算法 E5/E6 强制实码核对。

### 4.8 生命周期管理流程（10 阶段 + 衰减检测，v1.2.0 新增）

strategy_registry 的 `lifecycle_status` 8 态（v1.2.0 起含 decayed，v1.33.0 修正）映射 2026 主流 10 阶段模型：

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

**DECAY_SCAN 核心逻辑**：ic_ratio = recent_ic / baseline_ic。monitoring 态 ic_ratio<0.7 或 mrp<decay_threshold → decayed；ic_ratio>0.85 → active 恢复；decayed 态 ic_ratio>0.7 → monitoring；sustained 2 年低于阈值 → retired。

**DECAY_SCAN_MULTI 三检测器 2/3 投票**（v1.3.0）：① CUSUM（渐变漂移，k=0.5σ, h=4σ，~50天检测延迟）② Page-Hinkley（突变，δ=0.01σ）③ BOCPE/BOCPD（概率输出，Student-t likelihood 处理重尾，hazard_rate=1/250）。2/3 命中 → decayed；1/3 → monitoring 预警。v1.27.0 补：检测到变点后 MUST ARM 归因到具体因子坐标（Phase 2+ 因子数>20 时启用精准降权非全量降权）。

**检测器权衡**：

| 检测器 | 擅长 | 弱点 | 个人项目适用性 |
|---|---|---|---|
| CUSUM | 渐变漂移（crowding 慢腐蚀） | 需 μ₀ 基线 | ✅ Phase 1.5+（CUSUM 分量须用鲁棒变体） |
| Page-Hinkley | 突变（alpha 断崖） | 误报率高 | ✅ 补充 |
| BOCPE | 概率输出，不确定性量化 | 计算成本高 | ⚠️ Phase 1.5+ |
| profit_factor（v1.4.0） | 盈亏比稳定性（trades 序列） | 需 trade 级数据 | ✅ MVP 首选 |
| z_score（v1.4.0） | 分布偏移（实盘 vs 回测） | 需回测分布基准 | ✅ MVP 首选 |

**MVP 决策**（v1.4.0/v1.6.0）：MVP 用 `profit_factor`+`z_score`（无需 μ₀ 基线，绕过 A 股重尾对经典 CUSUM 的挑战——A 股 γ₄>6 时经典高斯 CUSUM 100% 误报）；Phase 1.5+ 升级 `cusum_ph_bocpe`（CUSUM 分量须用鲁棒变体：GSA-LLR 分数幂基/Huberized/truncated+self-normalized）。`decay_detection_method` enum：`rolling_ic`/`mrp`/`cusum`/`cusum_ph_bocpe`/`profit_factor`/`z_score`/`none`。

**经验数据**：alpha 衰减年均 US 5.6%/EU 9.9%；68% 策略 18-24 月需修改/退役；中位半衰期 11.2 月；1 年失败率 67%，18 月 83%，3 年仍盈利仅 8%。

**衰减原因分类**（Five Horsemen，v1.5.0）：

| # | 原因 | 占比 | refit 有效性 | 决策 |
|---|---|---|---|---|
| 1 | Crowding | 41% | ❌ | Level 5 退役 |
| 2 | Regime Change | 28% | ✅ | Level 3 refit（若新 regime 稳定≥60天） |
| 3 | Overfitting | 18% | ❌ | Level 5 退役 |
| 4 | Technology | 9% | ❌ | Level 5 退役 |
| 5 | Depletion | 4% | ⚠️ 部分 | Level 3 refit 失败则 Level 5 |

**监控频率**（v1.5.0）：active/live monthly，monitoring weekly，decayed daily。高频策略用 30-50 trades early diagnostic + 100+ trades confirmation；低频策略用 3-6 月 calendar 窗口。

### 4.9 变更管理算法（EVOLVE_ENTRY，v1.3.0 新增）

entry 建成后**修改**是更高频操作。标准变更流程：变更分类→版本快照（若需）→应用变更→依赖方通知→一致性审计→治理同步。

```
算法 EVOLVE_ENTRY(registry_id, entry_id, change_set, change_type):
  输入: entry_id, change_set{field: new_value}, change_type{metadata|schema_sig|code_ref|status}

  Step 1【变更分类】
    metadata → 原地更新不建版本
    schema_sig / code_ref → 版本快照（v→v+1）
    status → delegate §4.13 PROMOTE_ENTRY（→active）或 §4.10 RETIRE_ENTRY（→deprecated）

  Step 2【版本快照】（若 schema-significant）：bump version + changelog 记录
  Step 3【应用变更】：写入 change_set + updated_at
  Step 4【依赖方影响分析】：按 §4.6 矩阵反向查找，通知所有 dependents
  Step 5【一致性审计】：调 §4.7 AUDIT_REGISTRY E4/E5/E8
  Step 6【治理同步】：git commit
```

**变更分类清单**：

| 变更类型 | 示例 | 触发版本快照 | 通知依赖方 |
|---|---|---|---|
| metadata | description/tags/TTL/owner | ❌ 原地 | ❌ |
| schema_sig | formula/params/inputs/outputs/class | ✅ v→v+1 | ✅ |
| code_ref | code_path/module_id 迁移 | ✅ v→v+1 | ✅ |
| status | candidate→active / active→deprecated | 走 §4.10/§4.13 | ✅ |
| additive | 新增可选字段 | ❌ 原地（向后兼容） | ❌ 可选 |
| breaking | 删除/重命名必填字段、改类型 | ✅ v→v+1 + §4.11 演进 | ✅ 必须 |

### 4.10 退役算法（RETIRE_ENTRY，v1.3.0 新增）

entry 退役是状态机关键转换。3 阶段：active→deprecated（90天宽限，最少30天）→retired（无活跃引用）→物理删除（退役满1年+ARCH审批）。

```
算法 RETIRE_ENTRY(registry_id, entry_id, reason):
  输入: entry_id, reason{decay/performance_obsolete/replaced_by/structural_break}

  # 阶段 1: active → deprecated（90天宽限，最少30天）
  #   依赖方预警 + 级联响应（v1.7.0）：strategy 依赖因子退役→标记 review_required 不自动退役
  #   （策略可能有多因子冗余）；factor 依赖指标退役→因子自动进入 review
  #   有替代项 → 建议迁移后走 §4.9 schema_sig 变更；无替代项 → 评估 §4.10/§4.12

  # 阶段 2: deprecated → retired（宽限期满 + 无活跃引用）
  #   retired 不删除 entry（审计追溯），仅标记不可用

  # 阶段 3: retired → 物理删除（极少，需退役满1年 + ARCH 审批）
```

**退役触发条件**：`decay`（IC ratio<0.7 持续 2 年）/`performance_obsolete`（Sharpe 低于阈值/DD 超限）/`replaced_by`（被 variant 替代）/`structural_break`（市场结构断裂）。

**宽限期规则**：标准 90 天最少 30 天；宽限期内 deprecated 仍可用（平滑迁移）；宽限期满+无活跃引用→retired；retired 保留审计追溯，不默认删除。

### 4.11 Schema 演进算法（EVOLVE_SCHEMA，v1.3.0 新增）

schema 变更时已有 entry 数据迁移的标准流程。默认 Additive-Only（BACKWARD 兼容）；breaking 变更走 Expand-Contract 3 阶段。

**核心逻辑**：① 变更分类（added/removed/modified/renamed → breaking vs non-breaking）② 兼容性判定（BACKWARD/FORWARD/FULL/NONE）③ BACKWARD → Additive-Only（新字段填默认值，schema_version bump 1.0→1.1）；NONE → Expand-Contract（Expand 共存→Migrate 迁移→Contract 清理）④ 迁移后跑 AUDIT_REGISTRY ⑤ schema_version 区分兼容 vs breaking。

**兼容性模式**：

| 模式 | 含义 | 部署方式 |
|---|---|---|
| BACKWARD | 新 schema 能读旧数据 | 直接部署 |
| FORWARD | 旧 schema 能读新数据 | 需协调消费者 |
| FULL | 双向兼容 | 最安全，限制最多 |
| NONE | 不兼容 | 需 Expand-Contract |

**Breaking vs Non-breaking**：

| 变更 | Breaking? |
|---|---|
| 新增可选字段（有默认值） | ❌ |
| 放宽约束 | ❌ |
| 删除字段 | ✅ |
| 重命名字段 | ✅ |
| 改字段类型 | ✅ |
| 新增必填字段 | ✅ |
| 收紧约束 | ✅ |

历史 schema 增强全部是 Additive-Only（BACKWARD 兼容），已安全应用。未来 breaking 变更走 Expand-Contract。YAML 阶段 git diff 天然提供变更历史；DB 阶段用 schema_version + entry.version 双版本追踪。契约测试由 §4.7 E4 + §4.9 Step 4 隐式覆盖；DB 阶段可升级显式 consumer-driven contract tests。

### 4.12 衰减后适应算法（ADAPT_STRATEGY，v1.4.0 新增，v1.5.0 增强）

§4.8 DECAY_SCAN（检测）→ 本算法（适应）→ §4.10 RETIRE_ENTRY（退役）三环节。核心矛盾：**adaptation 和 overfitting 是同一数学操作，区别仅在跟踪真实偏移还是追逐噪声**。v1.5.0 增强：衰减原因分类驱动决策（Five Horsemen）+ 三选一经验决策矩阵 + 6 类 review triggers。

```
算法 ADAPT_STRATEGY(strategy_id, decay_signal):
  输入: strategy_id, decay_signal{来源: cusum/ph/bocpe/ic_ratio/mrp/profit_factor/z_score,
                                   严重度: warning/critical, decay_cause: crowding/regime/overfitting/tech/depletion/unknown}
  输出: 适应决策（refit/调参/减仓/退役）+ OOS 验证 + version 快照（若参数变更）

  Step 0【baseline 完整性校验】（v1.5.0，§4.7 E12 前提）
    # 缺 6 baseline 字段或 decay_threshold → halt（无法区分正常波动 vs 真实衰减）
    # decay_threshold 默认 0.7

  Step 1【响应分级】（5 级）
    # warning → Level 2 减仓 30-50%；critical → Level 3 refit（待 Step 1.5 裁决）
    # Level 4 在线学习需 ARCH 审批，不自动升级

  Step 1.5【衰减原因分类驱动决策】（v1.5.0，Five Horsemen）
    # crowding/overfitting/tech → 跳过 refit 直接 Level 5 退役（refit 无效或有害）
    # regime/depletion → 走 Level 3 refit；regime 类需新 regime 稳定 ≥60 天
    # unknown → 保守走 refit 流程（Step 2-5 OOS 验证兜底）

  Step 2【refit window 最优化】
    # w* = (2σ²/δ²)^(1/3)（MSE 最小化）；实证 σ=1%/日, δ=0.01%/日 → w*≈126 天
    # 上限 252，下限 21

  Step 3【refit 执行 + 过拟合防护】
    # 3a. Walk-Forward 优化（purge/embargo 防泄漏），train:test = 1:4
    # 3b. 参数稳定性区域检验：选 plateau centroid 非 needle peak（Soloviov 验证）
    # 3c. 优化偏差校正：N 次试验最大值膨胀 σ×√(2·ln N)；DSR 校正

  Step 4【OOS 验证】（adaptation vs overfitting 判定核心）
    # OOS Sharpe > baseline×0.85 → 适应成功（新参数+version 快照，回降 Level 2）
    # 否则 → Level 5 退役（§4.10 RETIRE_ENTRY）

  Step 5【适应频率约束】
    # refit 间隔 ≥60 天，防连续适应过拟合
```

**适应 vs 过拟合权衡**（5 级响应）：

| Level | 响应 | 触发条件 | 过拟合风险 |
|---|---|---|---|
| 1 | 静默监控 | 默认态 | 无 |
| 2 | 减仓 30-50% | decay_signal=warning | 无 |
| 3 | 季度 refit | decay_signal=critical（2/3 投票） | 中（需 OOS 验证） |
| 4 | 在线学习 | 持续 decay + ARCH 审批 | 高 |
| 5 | 退役 | refit 失败 / sustained 2 年衰减 | 无 |

**三选一经验决策矩阵**（v1.5.0，与 Five Horsemen 联动）：

| 决策 | 对应 Level | 核心判据 |
|---|---|---|
| Reoptimize | Level 3 refit | 核心假设仍 fit + OOS 扣成本正 + plateau 非 needle peak |
| Pause/Cut Size | Level 2 减仓 | 证据 mixed + expectancy 近$0 + DD 在 defensible range（1.5-2x prior max） |
| Retire | Level 5 退役 | OOS expectancy 转负 + walk-forward 持续失败 + 成本侵蚀 edge |

**review triggers 6 类**（v1.5.0，与统计检测器互补）：① rolling expectancy<baseline×0.3 ② current_dd>1.5-2x prior max ③ win rate 降 10-15pp ④ profit factor 滑向 1.0 ⑤ cost pressure 侵蚀 gross edge ⑥ regime mismatch。

**个人项目 MVP 决策**：MVP 只做 Level 1-2（监控+减仓），Level 3 refit 延后 Phase 1.5+。Level 4 在线学习远期不采纳。refit 间隔 ≥60 天。

### 4.13 上线晋升算法（PROMOTE_ENTRY，v1.8.0 新增）

candidate→active（实盘上线）是最关键状态转换，9 门禁全过才晋升（非加权平均，任何一门失败即阻断）。仅 strategy_registry 适用。

```
算法 PROMOTE_ENTRY(registry_id, entry_id, promotion_request):
  输入: entry_id（MUST 为 strategy），promotion_request{backtest_result, oos_period, reviewer}
  输出: status: candidate/experimental→active 转换 + baseline 保存 + 审计日志
  约束: 仅 strategy_registry 适用；entry.status ∈ {candidate, experimental}

  # G1 回测验证门
  bt = promotion_request.backtest_result
  FAIL if bt.oos_sharpe < 0.5
  FAIL if bt.oos_max_drawdown > 0.15
  FAIL if bt.oos_period_months < 3
  FAIL if entry.min_trl_years and bt.oos_period_years < entry.min_trl_years  # v1.14.0

  # G2 过拟合检查门
  FAIL if bt.is_overfit == True
  FAIL if bt.pbo_value > 0.2          # PBO 零假设=0.5 非 1（v1.26.0 警示：PBO≈0.5=完全过拟合）
  FAIL if bt.dsr_value < 1.0
  FAIL if bt.plateau_score < 0        # needle peak 不稳定参数（v1.6.0）
  FAIL if bt.mtc_method and bt.mtc_survived == False  # MTC 多重检验校正（v1.14.0）
  # CPCV 组合净化交叉验证（v1.16.0）：catastrophic-veto + mean≤0 FAIL + std/mean>0.5 FAIL
  FAIL if bt.cpcv_worst_max_dd > 0.15         # 任何切分回撤超红线=一票否决
  FAIL if bt.cpcv_oos_sharpe_mean <= 0        # OOS 平均 Sharpe 非正=策略无效（v1.17.0 修复）
  FAIL if bt.cpcv_oos_sharpe_std / bt.cpcv_oos_sharpe_mean > 0.5  # 切法敏感=过拟合
  # 有效 trial 数鲁棒性带（v1.21.0）：trial 相关时禁用裸 DSR，MUST bootstrap（White RC/Hansen SPA）
  FAIL if bt.trial_correlated and bt.bootstrap_test_passed is None
  WARN if bt.effective_trial_count_band is None and bt.n_trials > 10  # 须报 ≥5 估计器区间
  # PF ratio 一线阈值（v1.28.0）：ratio>2.0=阻断（textbook overfit）；>1.5=warning
  FAIL if bt.train_pf / bt.oos_pf > 2.0
  WARN if bt.train_pf / bt.oos_pf > 1.5
  # 最小交易数（v1.28.0，v1.33.0 映射）：value_reversal 500 笔，其余 300 笔（warning 级）
  WARN if bt.oos_trade_count < (500 if strategy_class=="value_reversal" else 300)
  # 参数稳定性区域（v1.32.0）：cliff_detected=true 或 paper/live 阶段 single_optimum=warning
  WARN if bt.parameter_stability_region.cliff_detected == True
  WARN if bt.parameter_stability_region.selection_method == "single_optimum"
          and entry.lifecycle_status in {"paper", "live"}

  # G3 风控限额门：risk_rules 非空 + 含 limit_type=kill_switch 条目（v1.33.0 修正字段名）
  FAIL if not entry.risk_rules
  FAIL if not any(lookup_limit(rl).limit_type == "kill_switch" for rl in entry.risk_rules)

  # G4 Baseline 保存门：6 baseline 字段 + decay_threshold（§4.7 E12 前提）
  FAIL if any(entry.get(f) is None for f in {baseline_sharpe, baseline_expectancy,
              baseline_win_rate, baseline_profit_factor, baseline_max_drawdown,
              baseline_trade_frequency})
  FAIL if not entry.decay_threshold

  # G5 代码冻结门：code_commit 绑定（§4 原则9）
  FAIL if not entry.code_commit

  # G6 基准分配门：benchmark_id（§6.1.2 schema）
  FAIL if not entry.benchmark_id

  # G7 衰减监控门：decay_detection_method + decay_scan_frequency（§4.8 前提）
  FAIL if not entry.decay_detection_method or not entry.decay_scan_frequency

  # G8 人工签批门：独立 reviewer ≠ owner（KRI Governance 分离职责）
  FAIL if not promotion_request.reviewer or promotion_request.reviewer == entry.owner

  # G9 容量检验门（v1.20.0）：capacity_aum_limit + participation_rate_limit + market_impact_model
  FAIL if not entry.capacity_aum_limit
  FAIL if bt.assumed_aum > entry.capacity_aum_limit     # 回测超容量=结果不可信
  FAIL if not entry.participation_rate_limit
  FAIL if bt.max_participation_rate > entry.participation_rate_limit  # 超参与率红线
  FAIL if not entry.market_impact_model                 # MVP 可填 none，资金增长后 MUST square_root

  # ── 三值裁决（v1.28.0，对标 Joint Falsification arXiv:2607.20093）──
  if gates_failed:
    if 非统计门(G3-G9)失败:
      return PROMOTE_BLOCKED   # 修复后重新申请
    elif OOS < min_trl_years:  # 样本不足
      return PROMOTE_INCONCLUSIVE  # viability_verdict=inconclusive，继续 Shadow/Canary 积累数据
    else:                       # 样本充分
      return PROMOTE_REFUTED   # viability_verdict=refuted，走 §4.10 RETIRE_ENTRY

  # ── 全部通过：执行晋升 ──
  entry.status = "active"; entry.lifecycle_status = "live"
  entry.promoted_at = today; entry.promoted_by = promotion_request.reviewer
  audit_log.append({event: "PROMOTE_ENTRY", gates_passed, reviewer, backtest_summary})
  schedule_decay_scan(entry_id, entry.decay_scan_frequency)  # 启动 §4.8 DECAY_SCAN
  notify_portfolios_using(entry_id, "策略已上线")
  return PROMOTE_SUCCESS(entry_id, gates_passed)
```

**门禁清单**（9 门）：

| 门 | 检查内容 | 失败条件 |
|---|---|---|
| G1 回测验证 | OOS Sharpe/回撤/周期/min_trl_years | Sharpe<0.5 或 DD>15% 或 OOS<3月 或 OOS<min_trl_years（v1.14.0） |
| G2 过拟合检查 | PBO/DSR/plateau/MTC/CPCV/PF-ratio/min-trades/param-stability | is_overfit 或 PBO>0.2 或 DSR<1.0 或 needle peak 或 MTC 未通过（v1.14.0）或 CPCV worst_max_dd>0.15/mean≤0/std-mean>0.5（v1.16.0）或 PF ratio>2.0（v1.28.0）或 min_trades 不达（v1.28.0）；warning：cliff_detected 或 paper/live 阶段 single_optimum（v1.32.0） |
| G3 风控限额 | risk_rules + 含 kill_switch 类限额（v1.33.0） | risk_rules 为空或无 kill_switch 条目 |
| G4 Baseline 保存 | 6 baseline 字段 + decay_threshold | 缺任意字段（§4.7 E12 前提） |
| G5 代码冻结 | code_commit | 未 pin commit hash（§4 原则9） |
| G6 基准分配 | benchmark_id | 未分配（§6.1.2 schema） |
| G7 衰减监控 | detection_method + frequency | 未配置（§4.8 DECAY_SCAN 前提） |
| G8 人工签批 | 独立 reviewer ≠ owner | owner 自批或无 reviewer |
| G9 容量检验（v1.20.0） | capacity_aum_limit + participation_rate_limit + market_impact_model | 未声明或回测假设超容量/参与率上限 |

**个人项目映射**：Gate 1-7 AI 自检，Gate 8 人工签批（不可降级），Gate 9 MVP 阶段 market_impact_model 可填 none 但 capacity_aum_limit + participation_rate_limit MUST 声明。Gate 3（风控+Kill Switch）和 Gate 8（人工签批）不可降级——实盘生存底线。

**渐进式部署：Shadow → Canary → Full（v1.10.0）**：9 门全过后 lifecycle_status=live，但须经三阶段 probation（reality gap 风险）。

| 阶段 | 资金风险 | 机制 | 通过条件 |
|---|---|---|---|
| Shadow | 零 | 只记录决策不发单（PaperBrokerShim），配对观测 | signal overlap>80% + 无致命分歧，跑 1-3 天 |
| Canary | 小（1-5%） | 资金 90/10 分流，独立样本真实交易 | paired t-test 80% power + canary Sharpe≥baseline×0.85 + DD 未超限 |
| Full | 全量 | 5%→20%→50%→100% 渐进 ramp-up，每档监控 1-2 周 | 启动 §4.8 DECAY_SCAN |

**Canary 自动回滚触发**（→§4.14 ROLLBACK_ENTRY）：① canary Sharpe<baseline×0.5 ② canary max_dd>baseline×1.5 ③ signal divergence>30% ④ Kill Switch 触发。shadow 阶段无资金风险，不触发回滚。

**Blue-Green 备选**（v1.10.0）：策略重大重构/参数空间剧变时可用——保持双环境（blue=live，green=新版），green 验证后原子切换，回滚=再 flip。MVP 以 shadow→canary→full 为主。

### 4.14 回滚算法（ROLLBACK_ENTRY，v1.9.0 新增）

上线后发现问题回滚到已知良好版本（version_pin 元数据变更，非文件迁移）。仅 strategy_registry 的 active/live 态可回滚。回滚≠退役（§4.10），是临时回退。

```
算法 ROLLBACK_ENTRY(registry_id, entry_id, rollback_request):
  输入: entry_id（MUST 为 strategy，active/live 态）, rollback_request{reason, target_version, trigger_source, reviewer}
  输出: version 回退 + 仓位处置 + 衰减监控重置 + 审计日志
  # v1.33.0：baseline_version/new_position_blocked/active_version/last_rollback_at/rollback_count/
  #   rollback_reason 为运行时动态字段（回滚执行时写入，不入 §6.1.2 静态 schema）

  # Step 1 触发判定：trigger_source ∈ {decay_signal, drawdown_breach, manual}
  # Step 2 目标版本：默认 baseline_version 或 version-1；目标不可为 retired
  # Step 3 频率约束（防 flip-flop）：7 天冷却 + 30 天 ≤2 次（超限强制 §4.10 退役审查）
  # Step 4 仓位处置（风险优先）：阻止新开仓；现有仓位按减仓规则（非一键清仓）；Kill Switch 走 §6.2.2 halt
  # Step 5 版本回退：version_pin=target_version；lifecycle_status 降级 monitoring
  # Step 6 衰减监控重置：恢复目标版本 6 个 baseline 字段；重启 §4.8 DECAY_SCAN
  # Step 7 审计日志 + 通知依赖方
  # Step 8 回滚后审查（7 天观察期）：正常→可重新 PROMOTE_ENTRY；异常→§4.10 RETIRE_ENTRY
```

**回滚触发条件**：

| # | 触发条件 | 阈值 | 触发源 |
|---|---|---|---|
| 1 | IC ratio 跌破阈值 | ic_ratio<0.7（§4.8） | decay_signal |
| 2 | profit_factor 跌破阈值 | PF<0.7×baseline | decay_signal |
| 3 | z_score 分布偏移 | z_score<-1.65（5% 显著） | decay_signal |
| 4 | 回撤超限 | current_dd>1.5×baseline_max_dd | drawdown_breach |
| 5 | 连续亏损 | 连续 N 笔（N=baseline_trade_frequency×3） | drawdown_breach |
| 6 | 人工判定 | 实盘异常模式 | manual |

**回滚 vs 退役边界**：

| 维度 | ROLLBACK_ENTRY | RETIRE_ENTRY |
|---|---|---|
| 目标 | 回退到已知良好版本 | 永久退出 |
| 状态 | active→monitoring | active→deprecated→retired |
| 可逆 | ✅ 可重新 PROMOTE | ❌ 不可逆 |
| 频率 | 7 天冷却 + 30 天 ≤2 次 | 90 天宽限 + 1 年保留 |

**个人项目映射**：AI 监控告警 + 人工确认回滚（回滚 MUST 人工确认，非自动执行）。仓位处置（阻止新开仓）不可省略——回滚安全底线。自动回滚（AUTO_ROLLBACK_ENABLED）远期不采纳。

### 4.15 依赖解析算法（DEPENDENCY_RESOLVE，v1.9.0 新增）

§4.6 交叉引用矩阵登记了 32 条 FK 关系（v1.33.0 修正，原"26 条"声明有误），本算法是其算法层补全——施工拓扑顺序（哪些表必须先建）、退役传递依赖（间接依赖链）、schema 演进影响范围。对标 [kindatechnical 2026-03 Service Dependency Graphs](https://kindatechnical.com/continuous-integration-continuous-deployment/service-dependency-graphs-and-deploy-ordering.html)（Kahn's algorithm 拓扑排序）+ [axonops schema registry 2026-03](https://github.com/axonops/axonops-schema-registry/issues/290)（dependency graph traversal）。

```
算法 DEPENDENCY_RESOLVE(operation, registry_id, entry_id):
  输入: operation{construct_order / transitive_deps / impact_scope}, registry_id, entry_id
  输出: 拓扑序（construct_order）/ 传递依赖链（transitive_deps）/ 影响范围（impact_scope）

  # ── 构建 12 表 FK 有向图 ──
  # 节点 = registry_id，边 = FK 引用（引用方 → 被引用方 = 依赖方向）
  # §4.6 矩阵的 32 条 FK 转为有向边（v1.33.0 修正）：
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

> 📊 **拓扑序 vs §3 优先级的对应关系**：Kahn 算法计算的拓扑序与 §3 裁定 7 的 P0→P1-A→P1-B→P2 施工顺序**一致**——P0（Layer 0）→ P1-A（Layer 2-3-5 被测对象）→ P1-B（Layer 4 交易/风控/数据/图形，Layer 1 字段字典/数据资产可提前）→ P2（Layer 6 实验）。**这从图论角度验证了 §3 施工顺序的合理性**。

> 💡 **DEPENDENCY_RESOLVE 与现有算法的关系**：本算法是 §4.6 FK 矩阵的**算法层补全**——施工时用 `construct_order` 确定建表顺序，退役时用 `transitive_deps` 查完整级联链（补全 §4.10 的直接依赖查询），schema 演进时用 `impact_scope` 算 breaking 变更影响范围（补全 §4.11 的迁移范围）。E8 循环引用检测（entry 级 variant_of）+ 本算法（registry 级 FK 环检测）形成双层防环。

### 4.16 YAML→DB 迁移算法（MIGRATE_REGISTRY，v1.11.0 新增）

§11 迁移路径的施工层补全——R1-R7 七阶段渐进式迁移确保零数据丢失+可回滚。逐表迁移，按 §4.15 construct_order 逆序（被依赖方后迁）。

**R1-R7 阶段总结**：

| 阶段 | 名称 | SSoT | 读源 | 写源 | 风险 | 回滚 |
|---|---|---|---|---|---|---|
| R1 | PG 表创建 | YAML | YAML | YAML | 低 | DROP TABLE |
| R2 | 数据导入+fallback | YAML | YAML（PG 镜像） | YAML | 低 | DELETE PG rows |
| R3 | CLI PG-first | YAML | PG→YAML fallback | YAML | 中（读切换） | loader 回 YAML-only |
| **R4** | **完整性验证 gate** | YAML | — | — | — | halt 不进 R5 |
| R5 | 双写模式 | **PG**（写入权威） | PG→YAML | PG+YAML 双写 | **高**（写切换） | loader 回 YAML-write |
| R6 | YAML 数据删除 | **PG**（唯一 SSoT） | PG only | PG only | 高（不可逆） | 从 snapshot 恢复 YAML |
| **R7** | **迁移后审计 gate** | PG | — | — | — | halt + 考虑回滚 |

**关键约束**：R4 验证 PG==YAML（deep_equal）；R5 双写期间每小时 diff 校验；R6 不可逆——MUST 满足 R5 清洁 28 天 + git 快照 + R7 审计通过三条件。并发迁移用 PG advisory lock 防 DDL 冲突。Schema 迁移默认 Expand-Contract（PG 11+ 加列无默认值不锁表），breaking 变更可用 Blue-Green shadow schema 备选。

**个人项目适用性**：当前因子<500/实验<5000，远未触发迁移阈值（§11）。本算法是 Phase 2+ 预案非当前施工项。MVP 阶段 YAML+git 足够。

### 4.17 2026-08-10 最新研究对标补充（v1.12.0 新增）

第一轮全网搜索 8 项对标，全部 Phase 1.5+/DB 阶段增强项，MVP 无阻塞：

| 项 | 核心发现 | 落地动作 |
|---|---|---|
| ① 双曲衰减模型 | α(t)=K/(1+λt)，momentum R²=0.65 | §4.8，Phase 1.5+ 拟合 λ |
| ② score-driven BOCPD 变体 | §4.8 检测器 3 升级方向 | Phase 1.5+ 评估 |
| ③ Wasserstein 漂移检测 | 分布漂移度量 | E11 `drift_method` 已扩展 `wasserstein` |
| ④ pgroll 零停机 Schema 变更 | 零停机迁移工具 | §4.16 R1 工具首选 |
| ⑤ PubGrub + 字典序最小拓扑 | 依赖解析增强 | §4.15 construct_order 升级方向 |
| ⑥ Data Contracts vs Schema Registry 分层 | 写入路径契约 vs 读取路径 registry，两者正交 | §4 原则 11 写入路径 + E13 读取路径 |
| ⑦ multigrid 三层 eval gate | `sha256(salt:user_id)%100` 确定性分流 | §4.13 渐进式部署参考 |
| ⑧ Feast 原生 OpenLineage 血缘 | `feast[openlineage]`+Marquez | §4 原则 9，DB 阶段启用 |

### 4.18 版本差异算法（DIFF_ENTRY，v1.13.0 新增，横切查询）

§4.9/§4.11/§4.13 都需"对比两版本差异"。本算法产结构化变更分类 → 驱动 semver bump 决策。只读查询，任意阶段可调用。

```
算法 DIFF_ENTRY(registry_id, entry_id, version_a, version_b):
  输入: entry_id, version_a/version_b（YAML=git commit hash；DB=version 字段值）
  输出: change_report{additions[], modifications[], removals[], breaking_changes[],
                      semver_delta, change_class, affected_dependents[]}

  Step 1: 字节级快判——blake3(a)==blake3(b) → return identical（毫秒级 gate）
  Step 2: 字段级 diff——additions（b-a）/ removals（a-b）/ modifications（交集值不同）
  Step 3: 语义分类——metadata_only（description/tags/owner）原地更新；
          schema_significant（formula/params/inputs/outputs）触发版本快照；
          code_ref_change（code_path/code_commit/module_id）触发版本快照；
          status → delegate §4.9/§4.10/§4.13
  Step 4: semver 映射——breaking removal/type change → MAJOR（Expand-Contract）；
          additive/schema_sig/code_ref → MINOR；metadata_only → PATCH；identical → none
  Step 5: breaking 时查 §4.15 transitive_deps（reverse）→ affected_dependents[]
```

**semver bump 映射**：

| 变更类型 | semver_delta | change_class | 处理路径 |
|---|---|---|---|
| 删除字段/类型变更 | MAJOR | breaking | §4.11 Expand-Contract |
| 新增字段/schema_sig 值变 | MINOR | additive | §4.9 版本快照 |
| code_ref 变更 | MINOR | additive | §4.9 版本快照 |
| metadata-only | PATCH | metadata_only | §4.9 原地更新 |
| status 变更 | — | lifecycle | delegate §4.13/§4.10 |
| 无变更 | none | identical | 无操作 |

**MVP 实现**：`git diff` + dict diff + 查表三步（<50 行代码），无需 AST 语义分析（DB 阶段增强项）。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-RES-01-D | 研究资产版本化 | 因子/策略/指标注册表版本字段 + §4.9/§4.13/§4.14/§4.18 | design 待施工 |

### 4.19 第二轮缺口审计与对标（v1.13.0 新增）

针对"12 算法体系是否仍有施工环节流程算法缺口"做第二轮全网搜索（2026-08-10），覆盖 10 个候选缺口领域，**逐项映射现有覆盖或显式 defer**——避免无节制新增算法导致过度工程（project_memory 过度工程处理原则），同时确保缺口有据可查、defer 决策有理可循。

**10 缺口领域审计表**：

| # | 缺口领域 | 2026 研究发现 | 现有覆盖 | 决策 |
|---|---|---|---|---|
| 1 | 候选提案（ideation→candidate） | [tapps-brain FEATURE_FEASIBILITY_CRITERIA 2026-03-27](https://github.com/wtthornton/tapps-brain/blob/main/docs/planning/FEATURE_FEASIBILITY_CRITERIA.md)（10 准则 0-5 评分 priority_score，hard-gate 失败则 re-scope）+ [ict-engine #192 2026-07-14](https://github.com/Undermybelt/ict-engine-release/issues/192)（三层 evidence→projection→consumption 因子候选 onboarding） | §4.5 CONSTRUCT_REGISTRY Step1-3（真源反查→编号→schema 填充）覆盖从已有代码/文档创建 candidate | **DEFER**：个人项目新因子先编码再注册（Step1 grep 新代码即覆盖）。形式化 feasibility scorecard 适合团队防冗余，个人靠风险优先原则 + MVP 自然过滤。**DB 阶段若因子>100 可选启用** priority_score 排序施工优先级 |
| 2 | 跨注册表引用验证 | [sigma-guard 2026-05-09](https://pypi.org/project/sigma-guard/)（sheaf cohomology 矛盾检测+proof receipt）+ [SHACL-DS arXiv:2605.10540 2026-05-11](https://arxiv.org/html/2605.10540v1)（named-graph 感知 SHACL） | §4.6 FK 矩阵（32 条 FK）+ §4.7 E4 FK 引用完整性 + E8 循环引用检测 | **DEFER**：sheaf cohomology 对 YAML 过度工程；SHACL-DS 是 RDF/SPARQL 生态与本项目 YAML/PG 架构不匹配。**DB 阶段 PG 外键约束 + E4 复跑**即可 |
| 3 | 变更通知/传播 | [DataHub MCL 2026-03-21](https://blog.csdn.net/gitblog_00819/article/details/151257185)（MetadataChangeLog Kafka 事件）+ [Apicurio EDA 2026-07-27](https://github.com/Apicurio/apicurio-registry/pull/8710)（lifecycle webhook 按 artifact type 路由）+ [CAMEL-24172 2026-07-16](https://issues.apache.org/jira/browse/CAMEL-24172) | §4.9 EVOLVE_ENTRY Step4 依赖方影响分析 + §4.13 PROMOTE_ENTRY `notify_portfolios_using` + §4.10 RETIRE_ENTRY 级联响应 | **COVERED 内联**：YAML 阶段通知=git commit 触发的 PR review（依赖方在 PR 中 @review）。DB 阶段 Apicurio EDA webhook 模式可复用（type-aware routing：factor 变更→策略 review，strategy 变更→portfolio 通知）。**独立通知算法对单用户过度** |
| 4 | 反向血缘查询 | [TIN arXiv:2601.04722 2026-01](https://arxiv.org/pdf/2601.04722)（Temporal Interaction Networks 5 查询类型 + vertex-state-sequence 索引）+ [OpenMetadata 2026-07-31](https://blog.csdn.net/gitblog_00401/article/details/155960355)（`analyze_impact(change_entity, depth=3)` 有界深度下游遍历） | §4.15 DEPENDENCY_RESOLVE `transitive_deps`（传递依赖链）+ `impact_scope`（变更影响范围） | **COVERED**：§4.15 已实现反向血缘查询（direction=reverse = 谁依赖我）。TIN 索引是流式系统大规模优化，YAML 阶段 12 表用 Kahn's BFS 足够。**DB 阶段 entry>1000 可选** TIN 索引 |
| 5 | 退役条目 GC | [openclaw #120922 2026-08-09](https://github.com/openclaw/openclaw/pull/120922)（Doctor deprecation registry：deprecated/removal-pending/removed 三态 + `removeAfter` deadline）+ [Docker registry GC 2026-07-11](https://www.codegenes.net/blog/docker-registry-2-0-how-to-delete-unused-images/)（两阶段 read-only quiesce→mark-sweep 防竞态） | §4.10 RETIRE_ENTRY（retired 保留审计，物理删除需满1年+ARCH审批） | **DEFER 但记录模式**：YAML 阶段 retired entry 留在 git（git 历史即审计），物理删除=git rm（手动+ARCH 审批已足够）。Doctor `removeAfter` deadline 模式 **DB 阶段可复用**（retired 满期自动标 removal-pending） |
| 6 | 复活/恢复（retired→active） | [cinatra #1837 2026-07-19](https://github.com/cinatra-ai/cinatra/issues/1837)（R3 同步 restore：reactivation 必须在 restore 操作内同步完成，失败则 abort 不留死引用）+ [IETF regext RGP restore 2026-05-11](https://datatracker.ietf.org/doc/draft-ietf-regext-rfc3915bis/)（redemptionPeriod + 两步 restore + restore report 强制人工撰文理由） | §4.10 RETIRE_ENTRY 仅正向（active→deprecated→retired），**无反向路径** | **NOTE 而非新算法**：状态翻转（retired→deprecated→active）本质是 EVOLVE_ENTRY 的 status 变更（lifecycle_transition 类，§4.18 Step3）。cinatra R3 同步性原则可复用；RGP restore report（人工撰文理由）**DB 阶段可复用**为退役恢复审计要求。**YAML 阶段不建独立 RESTORE_ENTRY**——retired→active 走 EVOLVE_ENTRY status 分支 + 手动 ARCH 审批 |
| 7 | 版本 diff（两版本对比） | [IETF YANG Schema Comparison 2026-05-05](https://datatracker.ietf.org/doc/html/draft-ietf-netmod-yang-schema-comparison-07) + [AST/byte-hash 双策略 2026-04-13](https://blog.csdn.net/VarLens/article/details/160111891) + [schema.biz 三桶 2026-04-29](https://schema.biz/api/breaking-changes/) | **无**（v1.12.0 缺口） | **ADD：§4.18 DIFF_ENTRY**（本轮新增，填补唯一硬缺口） |
| 8 | 注册表健康监控 | [noopsschool catalog SLI/SLO 2026-02-15](https://noopsschool.com/blog/metadata-catalog/)（uptime/freshness <1h/query latency/change-detection lag）+ [acceldata 2026-04-11](https://www.acceldata.io/blog/metadata-quality-freshness-and-coverage-the-enterprise-evaluation-guide)（ownership completeness + change-detection lag + asset-coverage ratio） | §4.7 AUDIT_REGISTRY（point-in-time 审计，非持续监控） | **DEFER 但记录指标**：YAML 阶段定期跑 AUDIT_REGISTRY（如每周 cron）= 持续监控的轻量替代。catalog SLI/SLO（freshness lag = DDL 事件→catalog 更新时间差）**DB 阶段可复用**。YAML 阶段 git commit timestamp = 天然 freshness 标记 |
| 9 | 原子批量导入 | [Lance BatchCommitTables 2026-06-18](https://github.com/lance-format/lance/discussions/6775)（staged manifests + put-if-not-exists 原子翻可见性）+ [Apicurio multi-table transaction 2026-03-30](https://github.com/Apicurio/apicurio-registry/issues/7670) + [Doris 2PC 2026-07-29](https://blog.csdn.net/juniperhan/article/details/159720535)（prepare→publish + UUID label 幂等） | §4.5 CONSTRUCT_REGISTRY Step1-3（批量创建，但无显式原子性） | **COVERED by git**：YAML 阶段 git commit = 天然原子批量（一个 commit 含多 entry 变更，全有或全无，revert 回滚）。DB 阶段 Apicurio multi-table transaction 模式可复用（PG 单事务包裹多表 upsert） |
| 10 | 搜索与发现（找已有因子/策略） | [Algolia Dynamic Facets 2026-07-21](https://www.algolia.com/about/news/algolia-launches-dynamic-facets)（AI 行为驱动 facet 实时重排序）+ [base14 metric registry 2026-01-19](https://docs.base14.io/blog/metric-registry/)（3700+ 指标自动提取 + repo/file/commit provenance + trust level） | grep / Select-String | **DEFER**：YAML 阶段 `Select-String` + §4.15 足够查找。Algolia facets 是 web-scale 搜索（万级 entry）。base14 自动提取 + provenance **DB 阶段可复用**（因子定义 provenance = 哪个 notebook/commit） |

> ⚠️ **v1.13.0 缺口审计总结**：
> - **1 项硬缺口已补**（#7 → §4.18 DIFF_ENTRY）
> - **4 项已覆盖**（#3 通知内联 / #4 反向血缘=§4.15 / #9 原子批量=git commit / #2 FK 验证=§4.6+E4）
> - **5 项 DEFER 并记录 DB 阶段升级路径**（#1 候选提案 / #5 GC / #6 复活 / #8 健康监控 / #10 搜索）
>
> **核心结论：12 生命周期算法 + 1 横切查询算法 = 13 算法体系已完整闭环，无施工阻塞缺口**。所有 DEFER 项均为 DB 阶段增强项，YAML 阶段现有体系足够——符合 project_memory 过度工程处理原则。**关键 DB 阶段升级备忘**：① Doctor removeAfter deadline 自动标 removal-pending；② RGP restore report 退役恢复审计；③ catalog SLI/SLO freshness lag；④ base14 自动提取+provenance trust level；⑤ priority_score 施工优先级排序。

### 4.20 A 股 2026 年 7 月监管变更影响（v1.14.0 新增，实盘合规 MUST）

2026-08-10 全网搜索发现 **两项 2026 年 7 月生效的 A 股监管变更**，直接影响 12 注册表中 5 个表的 schema/参数——这是实盘合规红线（非可选增强），已随 P1-B 施工纳入 schema。

**① 交易规则 2026 年修订（2026-07-06 生效，对标 [上交所 上证发〔2026〕41号 2026-04-24 发布](https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20260424_10816492.shtml) + 新华社/人民日报 2026-07-06 报道）**：

| 变更项 | 原规则 | 2026 新规则 | 影响注册表 | schema/参数影响 |
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

> ⚠️ **高频阈值核实说明（v1.15.0 补）**：中基协 2026-07-27 研报仍引用"300 笔/秒"——经多方核实（[东方财富 2026-07-08](https://caifuhao.eastmoney.com/news/20260708102539948920960) + [雪球 2026-07-08](https://xueqiu.com/1333898802/399079985) + [licai.cofool 2026-08-04](https://licai.cofool.com/ask/qa_7416984.html)）系**研报撰写时间差导致引用 2025 年版规定**：
> - 2025 年版 300 笔/秒（2025-07-07 施行）已失效，现行 15 笔/秒分两阶段落地（2026-04-07 第一阶段收紧 + 2026-07-07 全面完整落地）
> - 本表"15 笔/秒"为**现行有效阈值**，中基协研报"300 笔/秒"作废

**③ 局域网行情通道关闭 + 交易网关管理指引（2026-07-31/2026-08-31 生效，v1.15.0 新增，实盘合规 MUST）**

对标 [新浪财经 2026-07-28](https://cj.sina.cn/article/norm_detail?froms=ttmp&url=https%3A%2F%2Ffinance.sina.com.cn%2Fstock%2Festate%2Fintegration%2F2026-07-28%2Fdoc-inikkhkm3121470.shtml) + [东方财富 2026-08-05](http://finance.eastmoney.com/a/202608053832918762.html) + [第一财经 2026-08-05](http://finance.eastmoney.com/a/202608053832922855.html) + [证券时报 2026-07-28](https://stcn.com/article/detail/4044080.html)。
- 事件：2026-07-31 晚间交易所机房内局域网交易行情线路正式关闭，统一切广域网——"基础设施平权"的物理层收口，直接影响 execution_algo 的延迟建模假设

| 时间节点 | 事件 | 影响注册表 | schema/参数影响 |
|---|---|---|---|
| 2026-06 | 上交所《强化参与者交易业务单元管理的通知》+ 北交所禁止独享交易网关，存量 3 个月整改 | data_asset / execution_algo | 严禁独享网关/独立交易单元/更低延迟/优先报单/专属带宽；至少 10 账户共用一个交易单元 |
| 2026-07-28 | 券商收到《广域网交易行情线路技术要求》通知 | — | 通知下发，过渡期开始 |
| **2026-07-31 晚间** | **原局域网交易行情线路正式关闭，统一切广域网** | execution_algo / cost_model / data_asset | 行情接收链路时延从局域网 0.3-0.8ms 抬升到广域网 1.2-2ms；微秒级抢跑策略物理外挂失效 |
| 2026-08-31 | 《交易网关管理指引（试行）》施行 | data_asset / execution_algo | 通道平权硬约束生效；托管服务器搬离交易所机房 |
| 2026-08 内（待定） | 深交所切换广域网（截至 8-5 未完成） | execution_algo | 沪市已切，深市待切，跨市场策略须适应两市场时延差异期 |

**关键硬约束**：广域网线路双向时延**不得低于 2 毫秒**（"不许太快"地板，含存量及新增线路）——监管首次为速度设地板（而非天花板），终结"机房托管+局域网"物理低延迟特权。注意：本次仅关**行情接收**链路，**交易报盘专线暂未同步关闭**，微秒级抢跑窗口已大幅压缩。

**对 12 注册表施工的影响（P1-B 前必改，已随施工落地）**：
- **execution_algo_registry schema 新增字段**：`max_orders_per_sec`（int, 默认 14）/ `max_daily_orders`（int, 默认 19000）/ `cancel_rate_limit`（float, 默认 0.15）/ `min_order_interval_us`（int, 默认 50）/ `is_hft`（bool）/ `after_hours_eligible`（bool, 盘后固定价格交易资格）+ **v1.15.0 补 2 字段**（③局域网关闭）：`latency_floor_ms`（float, 默认 2.0，广域网双向时延地板）/ `network_type`（enum: wan/lan，默认 wan）
- **risk_limit_registry**：cancel_rate 从运营指标升级为合规红线（≤15%），kill_switch 须含 cancel_rate_breach 触发
- **universe_registry**：ST/*ST 池的涨跌停从 5% 更新为 10%，影响打板策略（STR-DABAN-001）连板梯队筛选——ST 股 10% 涨跌停使"涨停"判定阈值变化
- **cost_model_registry**：新增 `after_hours_fixed_price` 时段（slippage=0，精确收盘价）；**v1.15.0 补**（③局域网关闭）：高频时段 slippage 系数上调（盘口变薄，买卖价差走阔），`slippage_regime` 字段区分 pre/post_20260731 两套系数
- **benchmark_registry**：SSE 基金收盘价来源标注（集合竞价 vs 连续），影响 close-to-close 收益序列
- **data_asset_registry**（v1.15.0 补，③局域网关闭）：行情数据源 entry 须补 `latency_profile`（广域网 1.2-2ms vs 旧局域网 0.3-0.8ms）+ `colocation_eligible`（bool, 默认 false，托管服务器已搬离交易所机房）字段

> ⚠️ **个人项目适用性**：这些是**实盘合规硬约束**（非过度工程）：
> - miniQMT 单账户下单频率天然远低于 15 笔/秒（个人策略多数秒级-分钟级），cancel_rate 15% 对低频策略无压力，但 schema 字段 MUST 预留（regulatory compliance 字段缺失=实盘违规风险）
> - **关键**：40_execution_broker v2.6.0 的 CancelRateGuard 须对齐 15% 阈值（project_memory 已登记 P0 gap 已闭合，须验证阈值=0.15）
> - **v1.15.0 补**：③局域网关闭对个人项目影响**极小**——个人策略持仓周期天/周级，时延差对天级策略收益影响约等于零，但 `latency_floor_ms`/`network_type` schema 字段 MUST 预留（合规底线），实际延迟建模校准=Phase 1.5+

### 4.21 第三轮研究对标补充（v1.14.0 新增）

第三轮（2026-08-10，10 领域筛 7 项）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① SR 26-2 替代 SR 11-7（15 年来最大 MRM 变革） | [美联储 SR 26-2 + OCC 2026-13 2026-04-17](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf) | narrower "model" 定义（排除简单算术/确定性规则）+ materiality tiering 替代统一年度验证（低 materiality 仅需识别+性能监控）+ 生成式 AI carve-out | strategy_registry 可借鉴显式 `materiality_tier`（high=实盘资金决策/medium=回测验证/low=研究探索）驱动验证频率；个人项目非银行机构不直接适用，AI carve-out 印证 project_memory"LLM/agent 策略须单独治理标记" |
| ② NautilusTrader 替代 Backtrader（2026 严肃量化推荐，Rust 核心事件驱动） | [LedgerMind 2026-04](https://theledgermind.com/backtesting-framework-comparison-2026/) | 订单簿级模拟（队列位置/部分成交）+ 同策略代码 paper-to-live（直接支持 §4.13 shadow 模式）；68% 策略 paper→live 退化，主因 look-ahead(31%)/survivorship(23%)/overfitting(19%)/滑点建模不足(15%) | experiment_registry `backtest_framework` 字段（§7.2）MUST 记录框架+偏误检测能力；MVP 用现有框架，Phase 1.5+ 评估迁移 |
| ③ Double-Selection LASSO | [arXiv:2601.06499v2](https://arxiv.org/html/2601.06499v2) | 控制 151 已知基本面因子后从 191 信号库隔离 17 个非冗余信号（标准 LASSO 有 omitted variable bias） | Phase 1.5+ 新因子登记 MUST 附 double-selection 正交化结果（vs 仅 IC/IR），避免登记冗余因子 |
| ④ 华创 LightGBM 三标签冲击模型 | [华创证券 2026-03-20](https://m.hibor.com.cn/wap_detail.aspx?id=aca7f720f2e1cea4853568df7034b748) | 瞬时/临时/永久冲击 3 个独立 LightGBM（R²=0.4418），A 股散户订单流与美股平方根律校准基础不同 | Phase 1.5+ AUM 增长后 cost_model 新增 `CST-ASTOCK-003` 评估（§5.3 待定 C1 的 power_law(0.7) 替代选项升级） |
| ⑤ AH-HMM 元 regime 层 | [MDPI JRFM 2026](https://mdpi-res.com/d_attachment/jrfm/jrfm/jrfm-19-00015/article_deploy/jrfm-19-00015.pdf) | 标准 HMM 上加不可观测 meta-regime 层（低/高不确定性），转移动态本身 regime-条件化；HSMM+meta-context IoU 0.73→0.93，误报率 75.5%→4.0% | Phase 4 鲁棒性阶段评估（project_memory HSMM 升级路径） |
| ⑥ Feast 0.64 物化时数据质量监控 | [Feast 0.64 2026-06-26](https://feast.dev/blog/) | nulls/schema drift/freshness 在特征管道层检测（早于 E11 模型输入层） | DB 阶段采用 Feast 时免费升级 + SOX audit logging |
| ⑦ Meta-labeling 方向×仓位分离 | López de Prado | primary 定方向/meta 定仓位，base models 误差须不相关 | v1.18.0 §4.25③ 已落 `meta_labeling_config` schema，v1.26.0 §4.33④ 补适用边界（仅 discretionary 主模型适用） |

### 4.22 第四轮研究对标补充（v1.15.0 新增）

第四轮（2026-08-10，**聚焦"研究流程治理"**——前三轮聚焦算法/工具，5 领域筛 5 项）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① AlphaSchema 5 字段语义计划 | [Waton 2026-08-10](https://ceo.ca/@GlobeNewswire/waton-financial-highlights-alphaschema-research-progress) | Event/Context/Qualities/Direction/Output，语义计划为搜索主对象、延迟代码生成至计划选定后，评估前检查数据契约和泄漏规则 | factor_registry `schema_plan` 字段 v1.19.0 已落地（§4.26③） |
| ② Agentic 研究工作流：架构是承重件 | [Kinlay 2026-05](https://jonathankinlay.com/2026/05/agentic-workflows-for-alpha-research/)（12 周 FX-carry case study） | 换模型大多仍有效，换掉 typed handoffs/research log/human gates 几乎全失效；度量单位="经人类级批判后存活的 ideas/月"（提升约 2× 非宣传 10×）；研究时间分解——文献筛选 20-25%/数据清洗 25-30%/实现 10-15%/诊断消融 20%/判断综合 10%，AI 前四类强、判断弱，架构围绕此不对称设计 | experiment_registry 可补 `research_log_ref`+`human_gate_status`（Phase 1.5+，与 §4.13 G8 人工签批理念一致） |
| ③ 证据 SHA256 + allowed_use 治理 | [nathanku3-hue/Quant spec.md 2026-06](https://github.com/nathanku3-hue/Quant/blob/main/docs/spec.md) | 每个证据文件 SHA256 + `allowed_use` 用途限定（bounded_methodology_review_only 等）+ hard stop（无 gate 批准前禁止 alpha 命名）——§4 原则 9 SHA256 manifest 的生产实证 + 用途限定防证据越权 | experiment_registry 补 `allowed_use`（research_only/methodology_review/canary_basis/live_basis，默认 research_only）字段，Phase 1.5+ 纳入（与 §4.13 渐进式部署 shadow→canary→full 的"允许用途"对齐，待定 J2②） |
| ④ 数据契约独立模块 | [stock_good 2026-06-08](https://github.com/blankxxxc/stock_good) | `data_contracts/` 作独立顶层目录，契约定义与消费分离，一处修改多处生效 | Phase 1.5+ 评估 field_dictionary 升级为 data_contracts 模块（与 §4.7 E13 呼应） |
| ⑤ 量化行业转向 Agent 竞争 | 华夏时报 2026-08 + PandaAI | 2026-07-31 局域网关闭后速度套利空间消失（§4.20③），行业从"拼速度"转向"拼深度" | **关键边界**：Agent 协同=研究流程自动化（Phase 2+ 评估）≠交易决策自动化（RL 策略，project_memory 已裁定不采纳），两者正交 |

### 4.23 第五轮研究对标补充（v1.16.0 新增）

第五轮（2026-08-10，4 领域筛 4 项；**核心成果 CPCV 升级回测过拟合六方法已落地 §7.2 + §4.13 G2**）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① AlgoXpert IS-WFA-OOS 三阶段协议 | [arXiv:2603.09219 2026-03-10](https://arxiv.org/pdf/2603.09219v1) | (i) IS 优先稳定参数区域 `Ω_stable = {θ \| SR(θ) ≥ 0.9×SR_opt}` 而非单一最优；(ii) WFA rolling windows + purge gaps + majority-pass + catastrophic-veto 双门禁（任何 fold MaxDD 突破红线立即整体 FAIL）；(iii) OOS 严格参数锁定——catastrophic-veto（"任何切分回撤 > X% = 一票否决"）比"平均回撤 < 15%"更保守 | **已落地** §4.13 G2 `cpcv_worst_max_dd > 0.15` 检查 |
| ② EU AI Act 2026-08-02 全面生效 | —（欧盟法规 + SEC Rule 17a4） | 高风险 AI 系统 MUST 可验证/可追溯/可复现决策依据（违规罚款最高 €35M 或全球营收 7%），决策日志 append-only ledger（SEC Rule 17a4 要求 7 年保留） | strategy/experiment_registry 可选补 `explainability_method`（none/shap/lime/counterfactual/decision_tree）+ `decision_audit_log` 字段，Phase 2+ 评估（个人项目非 EU 管辖，ML 策略 Phase 1.5+ 须补 SHAP） |
| ③ A 股微观结构三约束（实盘合规 MUST） | —（交易所规则） | 价格笼子（连续竞价限价申报：沪深主板/创业板买入≤基准价 102% ∩ 基准价+0.1 元孰高、卖出≥98% ∩ -0.1 元孰低；科创板纯 102%/98% 无 0.1 元兜底；北交所 105%/95%）+ T+1（信号当日不能执行，回测 MUST `signal.shift(1)`）+ 涨跌停不可成交（触及涨跌停视为无法成交维持原仓位，回测 MUST 检查 `abs(ret) < limit_pct`；涨跌停日约占全年 1% 但止损日影响毁灭性） | 40_execution_broker v2.6.0 已实现 `check_price_cage`，execution_algo_registry schema `price_cage_config`（{board, buy_ceiling_pct, sell_floor_pct, has_unit_floor, unit_floor_yuan}）+ `t_plus_1` + `limit_up_down_untradable` 三字段已随 P1-B 施工落地 |
| ④ 决策审计治理 | SEC Rule 17a4 | 决策日志 7 年保留 + append-only + 24h explainability SLA（per-transaction 存 features/model_version/confidence/decision_rationale） | experiment_registry 可补 `decision_log_store`+`decision_log_retention_years`，Phase 2+ 评估 |

### 4.24 第六轮研究对标补充（v1.17.0 新增）

第六轮（2026-08-10，**填补前六轮"仓位管理"和"A 股特色数据"两个对标空白**，5 项；另修复 §4.13 G1/G2 两个 P0 伪代码 bug——字符串拼接 str() 转换 + CPCV mean<=0 直接 FAIL）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① Conformal Kelly | [arXiv:2608.01494v1 2026-08-02](https://arxiv.org/html/2608.01494v1) | conformal prediction interval 宽度作 fractional Kelly 的 scale（interval 宽则缩仓/窄则加仓），6 年窗口年化 log 增长 28.5%/Sharpe 1.34；**反直觉核心发现：让 interval 更快适应市场的每次 tweak 都损失 0.7-5.3 个百分点年增长——最佳是最简单方法**（slow/unweighted rolling conformal quantiles，宽度稳定性>局部锐度）；"drawdown dial"（interval 下行 miss 超历史率=模型失效信号→削杠杆，MaxDD 27.7%→20.3% 同时 Sharpe 提升） | strategy_registry `sizing_method` 可记录 `conformal_kelly`，Phase 2+ 评估（MVP 用 fixed_fraction，Phase 1.5+ fractional Kelly） |
| ② Kelly+ML 协方差改进 | [quantsingularity 2026-06-13](https://github.com/quantsingularity/Kelly-ML-Portfolio-Optimization) + [SCIRP 2025-03 A 股实证](https://www.scirp.org/journal/paperinformation?paperid=141556) | Kelly 核心痛点是协方差矩阵估计误差——Marcenko-Pastur denoising/HRP clustering/market-factor detoning 三法改进 | Phase 1.5+ risk_limit_registry VaR 协方差估计可用 denoising（sklearn <50 行） |
| ③ Sizing Shootout A/B 框架 | [crucible-backtester #559 2026-07-21](https://github.com/nousergon/crucible-backtester/pull/559) | 同一历史信号流+同一窗口+相同约束下对比多 sizer（conviction/risk-parity/fractional-Kelly），只有 weight 公式不同其余全共享；promotion 候选须同时 beat incumbent on Sharpe AND max-DD after cost；OBSERVE-only 不改 live config | experiment_registry 可补 `sizing_arm`+`sizing_shootout_winner`（Phase 1.5+） |
| ④ A 股高频因子 2026 实战 | [国泰海通 2026-08-10 高频选股因子周报](http://stock.finance.sina.com.cn/stock/view/paper.php?reportid=839683589036&symbol=sh000001) | 日内收益 7.75%/开盘后买入意愿强度 16.29%/尾盘成交占比 13.58%/日内下行波动占比 14.94%/日内高频偏度 14.53%，多空 7-16% 仍有效；日内动量与隔夜动量存在反转（T+1 制度导致） | factor_registry intraday 类已登记（FCT-INTRADAY-015~028，2026-08-16 全量重建后续号——旧 001~014 已随 170 条 deprecated 删除），Level-2 数据源 Phase 1.5+ 接入 |
| ⑤ 龙虎榜+Level-2 数据源授权治理 | [CSDN 2026-08-09](https://blog.csdn.net/llijjianmmin/article/details/148821157) + [sina 2026-07-08 龙虎榜](https://finance.sina.com.cn/roll/2026-07-08/doc-inihattw8303487.shtml) | **AKShare 明确声明仅学术用途不可商用**；龙虎榜含机构/游资/量化席位活跃度，是 A 股独有"主力资金意图"信号；2026"机构打底+游资突破+量化搅局"三元主力结构+量化盘口脉冲/虚假挂单新博弈 | data_asset_registry 数据源 `license_type`（academic_only/commercial_license/proprietary）标注已随 P1-B 施工落地，实盘前 MUST 评估商业授权 |

### 4.25 第七轮研究对标补充（v1.18.0 新增）

第七轮（2026-08-10，**填补"数据源头偏差"和"收益归因"两个对标空白**，4 项全部已落地 schema/审计）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① 回测数据偏差治理 | [preprints.org 2026-06](https://www.preprints.org/manuscript/202606.0436)（三分类 taxonomy：universe-membership contamination / price-data forward leakage / stop-exit sequencing violations） | 生存偏差=回测仅含存活公司使 US equity 年化高估 1-3%（小市值/价值更严重）；前瞻偏差使 mean-reversion 虚增 40-60%；E11/E13 查"特征值是否漂移"，生存/前瞻偏差是"数据样本本身是否有偏" | **已落地**：§4.7 新增 **E14** + data_asset 补 `survivorship_free`/`pit_available`/`earnings_lag_days` + experiment 补 `backtest_bias_checks`（MVP 填 unknown 诚实记录，实盘前 MUST 升级商业源评估） |
| ② Regime-Based 动量+均值回归融合 | [digitalninjasystems 2026-05-24](https://digitalninjasystems.wpcomstaging.com/2026/05/24/how-to-combine-mean-reversion-with-momentum-for-higher-returns/) + [中金 2026-06-24](https://finance.sina.com.cn/stock/stockzmt/2026-06-24/doc-inienieh3068292.shtml) | 200日SMA 以上 Trending Up（动量 80%+均值回归 20%）/以下 Trending Down（60%/40%）/区间震荡（均值回归 85%）；两类策略本质互补，中金案例 maxDD -5.42%→-2.99%、卡玛 0.98→1.71 | strategy 补 `combination_strategy`（regime_detector + allocation_weights）字段，Phase 1.5+ 评估 |
| ③ Meta-labeling 方向×仓位分离 | López de Prado；NTU 多智能体 XGBoost 融合 | primary 定方向/meta 定仓位 filter false positive，base models 误差不相关；NTU 年化 21.18% | strategy 补 `meta_labeling_config` 字段，Phase 2+ 评估 |
| ④ 归因分析 Brinson-Fachler + factor-based | —（经典方法） | 超额收益分解三效应：Allocation A_i=(w_p,i−w_b,i)×(R_b,i−R_b) / Selection S_i=w_b,i×(R_p,i−R_b,i) / Interaction；多期链接 Carino/Menchero/GRAP/Frongello；factor-based R_p=Σβ_k×F_k+α（FF3/Carhart4/FF5）；区分 return attribution vs risk attribution + TWR vs MWR | experiment 补 `attribution_result` 字段（**跨文档职责边界**：归因执行逻辑归 54 号，本字段仅登记结果元数据；§4.4 跨文档职责边界同轮新增：RUN_BACKTEST→52号/ATTRIBUTION→54号）；MVP 用 factor-based 归因（statsmodels OLS <50 行），Brinson-Fachler 需持仓数据 Phase 1.5+ |

### 4.26 第八轮研究对标补充（v1.19.0 新增，2026-08-10 全网搜索）

第八轮（**填补"LLM 时代量化治理"对标空白**，5 项全部已落地）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① Look-Ahead-Bench LLM 前瞻偏差治理 | [arXiv:2601.13770 2026-01](https://arxiv.org/pdf/2601.13770) | memorization leakage——LLM 训练语料含未来信息，回测凭记忆而非预测给信号；标准 LLM（Llama 3.1/DeepSeek 3.2）显著前瞻偏差，PiT LLM（Pitinf）随规模泛化提升；Alpha Decay 跨 regime 测量区分"真预测能力 vs 记忆回放"；E14 的 `lookahead` 字段假设"数据按公布日期对齐即可"，但 LLM 即使数据对齐正确、模型权重本身已含未来信息 | **已落地**：§4.7 新增 **E15** + data_asset 补 `llm_training_cutoff`/`lookahead_test_method` + experiment 补 `llm_lookahead_check_result` |
| ② KTD-FIN 4-Level Masking 数据侧脱敏 | [arXiv:2605.28359](https://arxiv.org/pdf/2605.28359) | bright/stock-blind/date-blind/blinded 四级；aliases 单 episode 稳定跨 episode 随机化；10-attacker 探针 top-5 ticker 恢复率仅 10.2%、联合成功率 1.5%；配套 Barra-style 归因用 9 个 VIF-screened style factors 减少 multicollinearity（直接 FF3/Carhart4 可能因共线性使 alpha 估计失真） | `attribution_result` 注释补 VIF screening（statsmodels variance_inflation_factor <50 行，VIF>10 移除或合并正交，VIF<5 安全） |
| ③ AlphaSchema 5 字段 schema_plan | §4.22① 同源（Waton 2026-08-10） | 语义/实现解耦：Schema Generator 永不见原始价格数据，Implementation Agent 永不决定测哪个想法——人类可审查"为何此因子应有效"而非仅"如何计算" | factor 补 `schema_plan`（event/context/qualities/direction/output，人工因子可空，LLM 挖掘因子 MUST） |
| ④ TiMi ICLR 2026 离线研发+在线蒸馏 | —（ICLR 2026） | LLM 智能体离线协作研发策略→回测反馈反思修正→稳定后蒸馏为可直接运行的交易程序，在线不再调 LLM；与 §4.13 G5 代码冻结精神一致——LLM 策略 MUST 蒸馏为可冻结代码才能晋升 active | strategy 补 `origin`（human/llm_generated/hybrid）+ `distilled_to_code`（G5 门禁：llm_generated 策略 distilled_to_code=false=阻断上线） |
| ⑤ Alpha-R1 8B RL Regime-aware 因子筛选 | [arXiv:2512.23515](https://arxiv.org/html/2512.23515v1/) | 因子逻辑+实时新闻评估 alpha 在变化市场条件下的相关性，按上下文一致性选择性激活/停用因子 | `combination_strategy.regime_detector` enum 补 `news_aware`（Phase 3+ 远期，需 8B RL 模型+实时新闻流） |

MVP：LLM 相关字段填 `{applicable: false}` 或 N/A 诚实记录，Phase 2+ LLM 评估时 MUST 启用 E15。

### 4.27 第九轮研究对标补充（v1.20.0 新增，2026-08-10 全网搜索）

第九轮（**填补"实盘可部署性"和"因子库多样性"两个对标空白**，全部已落地）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① 策略容量检验 | [breakingalpha 2026-01-26](https://breakingalpha.io/insights/capacity-constraints-trading-algorithm-selection) | "Capacity is not a secondary consideration; it is the primary filter through which all performance claims must be evaluated"；Square-Root Market Impact Model `Impact = σ × k × √(Q / ADV)`——交易 4% 日成交量成本约为 1% 的 2 倍，非线性冲击创造自然容量上限；参与率红线 `Participation Rate = Order Size / Market Volume` 机构约束 ≤ 5%-10% ADV（超限→冲击增加/被识别/逆向价格运动）；EntroPy 10% ADV 容量估计作 deployability hard filter；容量衰减悖论：业绩好→资金涌入→规模膨胀→策略失效；回测假设无限流动性/即时成交/零冲击，实盘资金放大后冲击吃掉 alpha | **已落地**：§4.13 新增 **G9 容量检验门禁**（G1-G8→G1-G9）+ strategy 补 `capacity_aum_limit`/`participation_rate_limit`/`market_impact_model`（MVP：capacity 填保守估值如 5% ADV，participation_rate_limit 填 0.05，market_impact_model 填 square_root） |
| ② 因子冗余检测三维度 | [EntroPy 2026-05 redundancy.py](https://github.com/HeroBlast10/EntroPy/blob/main/docs/PRODUCTION_FACTOR_RESEARCH_UPGRADE_2026_05.md) + [factordbms](https://pypi.org/project/factordbms/) | 三维度：effective signal correlation / factor long-short return correlation / exposure-vector cosine similarity；factordbms 三阶段 Global Correlation Check→Clustering→Selection；>0.7 相关=信息重叠应结合经济逻辑选其一或合成；逐步增量检验优先保留 3-5 个互补因子，residual alpha Sharpe 太弱→剔除；多个高相关因子（如 PE/PB/PS 相关 >0.8）=伪多样化，组合实际风险被低估 | **已落地**：§4.7 新增 **E16** + factor 补 `correlation_group`/`redundancy_status`（同组 MUST ≥1 个 independent；MVP 按因子 10 类粗分，Phase 1.5+ 三维度检测精细化） |
| ③ Deployability hard filters | EntroPy §2 | 方向正确/OOS IC 正/成本后 Sharpe 正/换手不过高/容量不过低/子样本符号不反复翻转/对 horizon 不敏感 + Benjamini-Hochberg FDR/Bonferroni/White RC/DSR 多重检验校正——与 §7.2 六方法互补：六方法查过拟合，此四法查族错误率 | 筛选目标从"最好看"改成"可上线"的连续评估，Phase 1.5+ 可作辅助决策 |

### 4.28 第十轮研究对标补充（v1.21.0 新增，2026-08-10 全网搜索）

第十轮（12 领域，**2 项施工算法已落地 + 3 项高价值 Phase 1.5+ 评估 + 7 项参考评估**）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① DSR 相关搜索失败模式修复 | [Soloviov 2026-07 "How Many Backtest Winners Survive Deflation?"](https://github.com/suenot/deflated-sharpe-search) | 受控 ground-truth 实验——纯噪声搜索 1000 策略时 DSR 有效（1.000→0.001-0.057），但相关搜索场景中裸 DSR 用原始 trial count 错误拒绝真实 edge（真实 Sharpe 3.92 被判 0.748<0.95）；根因：有效 trial 数不是单一数值——5 个标准估计器（Laplace/JAW/AR1/spectral/permutation）在同 trial 矩阵上相差两个数量级（1.6 到 370）。修复三原则：(i) trial 间相关（参数网格/同源变体）时禁用裸 DSR，MUST 用 bootstrap-based 测试（White RC/Hansen SPA 联合重采样）；(ii) MUST 报告≥5 种估计器区间（robustness band）而非单值；(iii) deflated benchmark SR₀≈1.63（年化）=噪声天花板 MUST 跨越 | **已落地**：§4.13 G2 新增 `trial_correlated`+`bootstrap_test_passed` 检查 + experiment 补 `trial_correlated`/`effective_trial_count_band`/`bootstrap_test_passed` 三字段 |
| ② 因果验证声明 gate | [causal-quant v0.4.1 2026-07-09](https://github.com/meacreatio/causal-quant) + [CIR-ACTIVA arXiv:2608.03715](https://arxiv.org/abs/2608.03715) | 钉住回测撒谎三方式——luck/confounding/selection across everything you tried；声明因果图 DAG→证伪测试电池→H-score（存活"搜索+选择"的 edge 比例）；**关键时机：注册时（非上线时）声明因果图，避免事后合理化** | **已落地**：§4.7 新增 **E17** + factor 补 `causal_graph`（MVP 填自然语言经济逻辑） |
| ③ Evidently+NannyML CBPE 按标签延迟分层监控 | —（Evidently/NannyML） | 数据漂移 P(X)/概念漂移 P(Y\|X)/标签漂移 P(Y) 三分法；延迟<1 天用 Evidently+实际性能，1-90 天用 NannyML CBPE 无标签推断，>90 天 CBPE 为主；**大样本陷阱**：KS/chi-square 在百万行下对纯噪声报"显著"，PSI/JS 测量效应量更诚实 | **Phase 1.5+ 评估**；v1.26.0 已落 `label_delay_days`/`drift_detector` 字段 |
| ④ Kyle's lambda + OFI 流动性因子 | —（Kyle lambda） | lambda=价格冲击系数=市场深度倒数，日级估计=价格变动对签名订单流回归斜率；同时是流动性/价格冲击/逆向选择三重度量 | **Phase 1.5+ 评估**；v1.26.0 已落 `liquidity_metric` 字段含 OLS slope 实现陷阱注释 |
| ⑤ Apicurio 四阶段版本状态机 | —（Apicurio + Confluent） | Creation→Evolution→DEPRECATED（存量警告不中断）→DISABLED（阻止新消费者依赖）——比三态更精细 | **Phase 1.5+ 评估**；v1.22.0 已落 risk_limit `stage` 字段；Confluent migration rules 可作 §4.11 Phase 2+ 增强 |
| ⑥ CRISP/HRP-μ 组合构建 | [arXiv:2604.23833](https://arxiv.org/abs/2604.23833) | 信号感知层级组合构建算法 | **参考评估**（Phase 1.5+/2+ 远期，MVP 无阻塞）——属 52/54 号职责，DEFERRED，§4.4 跨文档边界 |
| ⑦ HAR-LSTM-GARCH 波动率预测 | — | DL 唯一被 4+ 独立研究确认的可靠目标是已实现波动率 RV | **参考评估**——risk_limit 可补 `volatility_predictor` |
| ⑧ Confluent Data Contracts 五要素 | — | 数据契约五要素框架 | **参考评估**——§4.11 可补完整性约束+规则策略 |
| ⑨ PatchTST 时序 Transformer | — | TSFM 预训练在金融低信噪比增益不可靠，与 project_memory"Mamba/SSM 不采纳"一致，审慎 | **参考评估**——不采纳方向 |
| ⑩ TreeSHAP/EBM 可解释 AI | — | 组合级 Brinson + 模型级 SHAP | **参考评估**——Phase 1.5+ |
| ⑪ OpenMetadata active 元数据治理 | — | 元数据触发动作（如质量告警自动阻断因子上线） | **参考评估**——Phase 1.5+/2+ 远期 |
| ⑫ GE+dbt+Soda 三层数据质量 | — | 三层数据质量栈 | **参考评估**——data_asset 可要求每数据源附 GE expectation suite |

### 4.29 第十一轮研究对标补充（v1.22.0 新增，2026-08-10 全网搜索）

第十一轮（4 领域，**2 项审计已落地 + 1 项算法增强已落地 + 1 项关键警示**）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① GSA-LLR 鲁棒 CUSUM | [arXiv:2605.23419v2 2026-05-27](https://arxiv.org/html/2605.23419v2)（Lean 4 形式化验证核心定理） | 极端重尾数据（γ₄>20）上经典 CUSUM 误报率 100%；GSA-LLR 用广义随机基逼近对数似然比，仅用 3 阶以下矩，基函数按 γ₄ 自动选择（<6 多项式/6-20 分数幂/≥20 对数基），Kunchenko 概率误差界控制误报无需经验调参；A 股小盘股 γ₄ 常>10、危机期>20 | **已落地**：§4.8 DECAY_SCAN_MULTI 检测器 1 增重尾自适应分支（γ₄≥6 自动切换 GSA-LLR）+ `decay_detection_method` 补 `gsa_llr_cusum` |
| ② LLM 前瞻污染三方法（数据侧+模型侧双轨） | LAP：[arXiv:2512.23847v2 2026-06-12](https://arxiv.org/html/2512.23847v2)（CUHK）；FinCAD：[arXiv:2605.24564](https://arxiv.org/pdf/2605.24564)；CMMD：[MemGuard-Alpha arXiv:2603.26797](https://arxiv.org/pdf/2603.26797) | LAP：日期-only 召回查询测 LAP=P(up)+P(down)，污染检验回归 Y_{t+1}=β₁μ̂_t+β₂LAP+β₃(LAP×μ̂_t)，β₃>0 即前瞻污染指征；FinCAD：推理时 Context-Aware Decoding 改编，logit 层减去记忆激活 prior，in-sample 记忆日收益降 67.1%，OOS 与 baseline 差 <$8K；CMMD：多 LLM 训练 cutoff 差异分离记忆驱动 vs 推理驱动信号，Sharpe 4.11 vs 未过滤 2.76，干净信号日均 14.48bps vs 污染 2.13bps | **已落地** §4.7 **E18** + experiment 补 `lap_check_result`；FinCAD 与 CMMD 为 Phase 1.5+ 评估（一防一治互补） |
| ③ 企业债因子动物园 LIB 偏差 | [arXiv:2604.07880v1 2026-04-09](https://arxiv.org/html/2604.07880v1)（Dickerson-Robotti-Rossetti） | 108 个企业债因子纠正 LIB（Latent Implementation Bias——同一噪声价格进入信号和收益分母，相关误差被误认为 premium）+ ex-post 收益过滤（去极值/去流动性差用全期统计量=嵌入未来信息）后多数不再显著；少数存活主要是 credit-spread-based value 信号；A 股关联：复权价/成交量既入因子又入收益分母=LIB 风险 | **已落地** §4.7 **E19** + factor 补 `lib_audit`/`ex_post_filter_audit`（仅 price-derived 因子检查） |
| ④ 关键警示：A 股板块轮动 Top3 次日重合率仅 14.8% | [WyckoffTradingAgent wiki 2026-07-23](https://github.com/YoungCan-Wang/WyckoffTradingAgent/wiki/04_Finance_Sector_Rotation_Regime) | 63.2% 的日子 Top3 完全换人，46.6% 的"领涨"只持续 1 天；共识高潮后 3 日下跌>2% 概率 29.8%；任何依赖"板块延续领涨"的策略会严重失效 | `sector_rotation` 策略（STR-SECTOR-ROTATION-001）校准 MUST 采纳：降板块延续依赖（hot_bonus 0.05→0.02）、增 3 日动量 q3 快速感知（板块强度公式 0.7×q20+0.3×q5 改 0.4×q20+0.3×q5+0.3×q3） |

### 4.30 第十二轮研究对标补充（v1.23.0 新增，2026-08-10 全网搜索）

第十二轮（3 项方法学，**1 项审计 + 3 字段已落地**）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① RMT 去噪因子相关性矩阵 | [arXiv:2507.17211v2 2026-08-07 EFS](https://arxiv.org/html/2507.17211v2)（港中文+上财）+ [arXiv:2601.07687v4](https://arxiv.org/html/2601.07687v4) | 因子相关性矩阵在 q=N_factors/T_observations>0.1 时含大量噪声特征值，Marchenko-Pastur 律 [λ₋,λ₊]=σ²(1±√q)² 区间内是纯噪声非信号，未去噪的伪相关被误判为因子冗余（independent 错标 redundant 或反之）；RMT 去噪+正则化 QP 在美股/港股/A股均优于未去噪基线且无额外调参成本；arXiv:2601.07687v4 物理信息奇异值学习：标准 RMT 假设平稳+有界谱，真实收益违反（依赖漂移+宏观共同模），Phase 2+ 可用神经网络估计器替代解析收缩 | **已落地** §4.7 **E20** + factor 补 `rmt_denoised`（MVP 因子数<20 时 q<0.1 填 {applicable: false}，Phase 1.5+ 因子数>20 时 MUST 启用 RMT clipping——[λ₋,λ₊] 内特征值替换为均值，保留信号特征值） |
| ② RSB 非高斯回撤校准 | [arXiv:2608.00127v1 2026-07-31](https://arxiv.org/pdf/2608.00127) | 放宽高斯假设后四个决策相关度量（最大回撤/最大损失/最终负时间/最长恢复时间）移动方向不同——单一高斯表系统性误警，对重尾分布（A 股 γ₄ 常>10）尤其严重；长记忆 fBm 下回撤风险放大几乎完全是自相似色散缩放效应 T^(H-1/2)，是 √-of-time 校准的失败非内在危险 | risk_limit 补 `drawdown_calibration_method`（gaussian/rsb_non_gaussian/fbm_long_memory；MVP 默认 gaussian 保守兜底，Phase 1.5+ 重尾策略 γ₄>6 MUST 切换 rsb_non_gaussian——按策略实际偏度/肥尾/波动率聚集生成四维回撤查找表替代单一静态阈值） |
| ③ RWC 共形 VaR 校准 | [arXiv:2602.03903v3 2026-08-03](https://arxiv.org/html/2602.03903v3)（Oxford） | VaR 预测在压力期系统性误校准（实现违反率偏离名义目标）；Regime-Weighted Conformal Calibration 用指数时间衰减+regime 相似性权重从历史预测误差构建安全缓冲，包裹任意条件分位数预测器，model-agnostic | risk_limit 补 `var_calibration_method`（historical/rwc_conformal；MVP 默认 historical，Phase 1.5+ MUST 评估 rwc_conformal——regime 分类器复用 35/36 号文档无需额外建模） |

### 4.31 第十三轮研究对标补充（v1.24.0 新增，2026-08-10 全网搜索）

第十三轮（**1 个高价值根本缺口——universe_registry 生存偏差治理，已落地**）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| 缺口识别 | §4.7 E14 taxonomy ① universe-membership contamination | E14 自 v1.18.0 起声明"生存偏差在 universe 层进入"，但实现只查 data_asset_registry 不查 universe_registry——"概念正确但实现遗漏"的典型缺口：data_asset 含退市股 ≠ universe 用 PIT 成分构造，二者独立 | 本轮修复目标 |
| PIT universe 构造原则 | [alphanume 2026-06-08](https://www.alphanume.com/blog/how-to-build-a-momentum-strategy) | "The universe is where survivorship bias enters most silently."——回测从今日指数成分或厂商库（已静默丢弃退市股）取股票列表=高估收益；正确构造从 point-in-time 成分文件开始（记录每个 formation date 哪些股票可选，只用当时可得信息），退市股 MUST 含至退市日（收益含最终部分期收益），流动性/价格过滤每个 formation date 用当时数据应用（非回溯） | 见下方"已落地"行 |
| 三锁定窗口方法论 | [tickernerd 2026-08-03](https://tickernerd.com/methodology/) | 三锁定窗口方法论 + PIT Compustat/FactSet 历史（"a universe rule that quietly deletes a fifth of the market is a hidden sector bet"） | 参考佐证 |
| survivorship-bias-free S&P500 显式构造 | [arXiv:2603.16904](https://arxiv.org/pdf/2603.16904) | 显式构造：回溯 cutoff 后所有 add/delete 事件恢复当时成分集 | 参考佐证 |
| 已落地 | — | §4.7 E14 扩 **c 维度**——universe_registry 的 `pit_constituent_construction`/`delisted_handling` 声明检查（**不新增 E21 避免 E 编号膨胀**——E14 本就是"回测数据偏差检查"语义内聚，生存偏差含 universe 层是其核心子类） | universe schema 补 `pit_constituent_construction`（bool）+ `delisted_handling`（include/exclude/unknown）+ `survivorship_free`（bool）三字段 |
| 落盘实况 | — | UNI-INDEX-001/002 成分股文件未落盘→诚实标注 pit=false/survivorship_free=false（待定 K3）；UNI-DYNAMIC-001/UNI-RULE-001/UNI-RULE-002 过滤规则用 formation-date 当下数据可填 true | 实际 PIT 成分文件接入=Phase 1.5+ |

### 4.32 第十四轮研究对标补充（v1.25.0 新增，2026-08-10 全网搜索）

第十四轮（3 项，**2 项算法增强已落地**）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① Assay PIT 正确回测引擎 as_of_date 字段语义契约 | [Assay 2026-07-04](https://github.com/chester1uo/Assay)（ICLR 2026 AlphaBench 配套） | Prices=EOD（收盘价当日可得）/ Splits=执行日（除权日生效）/ Dividends=公告日（fallback 除权日，**公告日 ≠ 除权日**）/ Universe=时点成分（formation date 当下可得）——E14 此前不查每种数据类型的 as_of_date 语义（复权价用前复权=含未来 split 信息=前瞻偏差；分红用除权日而非公告日=忽略漂移） | **已落地**：§4.7 E14 扩 **d 维度** + data_asset 补 `as_of_date_semantics`（eod_bar/execution_date/declaration_date/ex_date/universe_snapshot；复权价用后复权 backward-only 避免前瞻偏差） |
| ② AurumQ-RL MASTER-lite 预注册协议 | [AurumQ-RL 2026-07-17](https://github.com/yupoet/aurumq-rl) + [R&D-Agent-Quant NeurIPS 2025](https://arxiv.org/pdf/2505.15155) | 成本否决（含真实滑点/佣金/冲击成本的 OOS 收益须为正，IC 高但 OOS 亏损=否决）+ 3 窗 3 seed（3 时间窗口×3 随机种子，方差超阈值=不稳定=否决）+ 模型层修正（IC 优化目标与实盘收益相关性<阈值=IC 脱钩告警）；R&D-Agent-Quant 佐证"IC 优化与实盘收益脱钩"是已知缺陷 | **已落地**：§4.13 G1 增强（成本否决子检查 `bt.oos_return_after_cost <= 0` = 阻断 + IC-OOS 脱钩告警 `bt.ic_oos_correlation < 0.3` = warning）+ experiment 补 `pre_registered`/`cost_vetoed`/`ic_oos_gap`（MVP 成本否决含 A 股万5 印花税+万0.1 过户费+滑点 0.2%，3 窗 3 seed 用 walk-forward 3 折×3 种子） |
| ③ R&D-Agent-Quant 因子-模型协同优化 | 微软开源，2026-07-23 Qlib 集成 | Research+Development 双 agent，实测相对经典因子库年化 2×、因子数减少 70%；已知缺陷：IC-实盘脱钩、稳定性差 | factor 补 `discovery_agent` 字段（human/rd_agent/efs/hubble/other），Phase 1.5+ 评估 |

### 4.33 第十五轮研究对标补充（v1.26.0 新增，2026-08-10 全网搜索）

第十五轮（5 项**概念校准**，0 新 E/G 编号）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① Wasserstein HMM regime 检测 | [arXiv:2603.04441v1 2026-02-21](https://arxiv.org/pdf/2603.04441v1)（Columbia） | plain HMM 滚动重估计会置换标签（label permutation）——每次 EM 重训后状态编号可能互换，regime 身份不稳定、下游权重剧烈跳变、turnover 爆炸；2-Wasserstein 模板跟踪（Gaussian 组件映射到持久 regime 模板）几何锚定身份保持 + 预测模型阶选择（自适应状态数）+ 交易成本感知优化；实证 Sharpe 2.18 vs SPX 1.18，maxDD -5.43% vs -14.62%；"regime inference stability is a first-order determinant" | `regime_detector` enum 补 `wasserstein_hmm`，Phase 1.5+ MUST 优先于 plain hmm 评估（标签置换问题在 A 股高波动环境更严重） |
| ② PBO null=0.5 误读澄清 | [marketmaker.cc 2026-07-01](https://marketmaker.cc/en/blog/post/probability-backtest-overfitting-pbo/) | **PBO 的零假设是 0.5 不是 0**——最常见误读；PBO=in-sample 最优配置在 OOS 落入下半区的概率，无泛化能力时=0.5（PBO≈0.5=完全过拟合=硬币翻转，PBO≈0=可信，PBO≈1=反转）；受控实证：零 edge 场景 PBO=0.476，植入 edge（Sharpe 2.38）PBO=0.001——"PBO=0.4 是轻度过拟合"的误读会放松警惕，实际已接近硬币翻转基线 | §4.13 G2 门禁加误读警示注释（0.2-0.5 区间仍阻断，泛化能力不足） |
| ③ Kyle lambda 实现陷阱 | [JohnGavin/historical #627 2026-08-03](https://github.com/JohnGavin/historical/pull/627) | Kyle lambda 是 ΔP_t = λ·Q_t + ε_t 的 OLS 回归斜率 = cov(log_ret, signed_flow)/var(signed_flow)，不是 ratio = abs(log_ret)/volume——ratio 形式塌缩为 Amihud（abs(signed_flow)==volume by construction），二者数值恒等=bug，曾 live 在 published dashboard 上 | factor 补 `liquidity_metric` 字段（含陷阱注释：MUST 用 OLS slope 而非 ratio；MVP 用 ADV/turnover 粗估，Phase 1.5+ Level-2 后计算精确 lambda/OFI） |
| ④ Meta-labeling 适用边界 | [QuantConnect 2026 "Why Meta-Labeling Is Not a Silver Bullet"](https://www.quantconnect.com/forum/discussion/14706/why-meta-labeling-is-not-a-silver-bullet/) | **meta-labeling 只能改善 discretionary/规则型主模型，不能改善 end-to-end ML 主模型**（若 meta-model 能从相同特征提取更多信息则主模型已端到端优化；否则可无限级联 meta-meta-model ad-infinitum；grid search 实证两者平均 Sharpe 无显著差异） | `meta_labeling_config` 注释增强适用边界（Phase 2+ 评估时 MUST 先判断主模型类型：规则型适用，ML 端到端型不适用） |
| ⑤ v1.21.0 第十轮遗留 schema 落地 | —（§4.28③ 遗留） | 标签可用延迟治理：NannyML CBPE 估计须按延迟分层；A 股财报季报45天/年报4个月/业绩预告7-15天 | data_asset 补 `label_delay_days` + `drift_detector`（none/evidently/nannyml/alibi_detect，MVP 填 none 实盘后启用） |

### 4.34 第十六轮研究对标补充（v1.27.0 新增，2026-08-10 全网搜索）

第十六轮（6 项**引擎层补全**，0 新 E/G 编号）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① ARM 变点归因 | [arXiv:2608.01691v1 2026-08-03](https://arxiv.org/html/2608.01691v1) | 检测到变点后标准做法（在估计变点 τ̂ 处做 per-coordinate 两样本检验）无效——FWER>0.66；ARM（Attribution by Rank Maxima）用 max-over-splits rank statistic 评分每个坐标，3 个有限样本保证：per-coordinate validity + FWER control（Westfall-Young 联合置换）+ FDR control（e-BH） | **已落地** §4.8 补"步骤 5：变点归因"子步骤（检测到变点后 MUST 调用 ARM 归因到具体因子坐标，归因写入 `decay_detection_method` 字段格式 {detector, attribution: "arm"}；Phase 2+ 因子数>20 时 MUST 启用，精准降权非全量降权） |
| ② Hubble AST 验证沙箱 | [arXiv:2604.09601v2 2026-04-14](https://arxiv.org/pdf/2604.09601) | LLM 因子生成安全标准——DSL 约束生成器 + AST 验证沙箱（结构安全白名单/复杂度上限/语义有效性 3 层）+ 双通道 RAG（positive 鼓励探索 + negative 劝阻 crowded 模板）+ 确定性评估引擎（Bartlett-kernel HAC 显著性）+ family-aware 选择 | factor 补 `llm_safety_stack` 字段（{ast_validation, dsl_constrained, complexity_control, dual_channel_rag, family_aware_selection}，discovery_agent=rd_agent/efs/hubble/quantevolver 时 MUST 声明） |
| ③ QUANTEVOLVER RL 微调 vs prompt loop | [arXiv:2605.15412](https://arxiv.org/pdf/2605.15412) | policy updates 内化历史优化经验优于 prompt 累积 feedback——解 context explosion/inference cost/feedback drift/search stagnation 四问题 | `discovery_agent` enum 补 `quantevolver`（Phase 2+，需 RL 微调基础设施） |
| ④ Text+VAR 双向 regime 检测 | [arXiv:2605.30363v2 2026-08-02](https://arxiv.org/pdf/2605.30363v2)（FinLLM@IJCAI 2026） | LLM 从文本（FOMC minutes 等）提候选 regime shift→likelihood-ratio VAR test 数据面板验证 + 数据检测器提候选→LLM 文本核验，detector-agnostic，F1=0.82 | `regime_detector` enum 补 `text_var_dual`（Phase 2+，需 LLM+VAR 基础设施） |
| ⑤ Weighted Kolmogorov Metric 重尾回测指标 | [arXiv:2601.04490v1 2026-01-08](https://arxiv.org/pdf/2601.04490) | 标准 KS 距离在重尾分布（E\|X\|³=∞）下收敛率退化 O(n^{-δ/2}) 致"noise barrier"（有效风险模型因无关 tail event 被拒绝）；加权 d_{K,h,q}(F,G)=sup_t w_q(t)\|F(t)-G(t)\| 恢复 O(n^{-1/2)} 最优收敛率；smooth downweighting 非 winsorization | `drawdown_calibration_method`+`var_calibration_method` enum 均补 `weighted_kolmogorov`（重尾策略 γ₄>8 MUST 启用） |
| ⑥ AlphaBench 标准化因子评测基准 | [ICLR 2026](https://alphabench.cc/) | T1 Factor Generation/T2 FactorEval（zero-shot judge，**当前 LLM 最弱能力**）/T3 Iterative Searching 三任务，覆盖 CSI300/500/1000+SP500 | Phase 1.5+ 因子发现评测时 MUST 用 AlphaBench 3 任务体系对比不同 discovery_agent（human vs rd_agent vs efs vs hubble vs quantevolver）的因子质量 |

### 4.35 第十七轮研究对标补充（v1.28.0 新增，2026-08-10 全网搜索）

第十七轮（3 项**裁决哲学升级**，0 新 E/G 编号）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① Joint Falsification 三重门三值裁决 | [arXiv:2607.20093v1 2026-07-22](https://arxiv.org/abs/2607.20093)（Darmanin） | "实际可部署性"=三个预声明门禁的合取——统计 edge 门（multiplicity correction 后仍显著）+ 经济可行性门（net-of-cost 超 materiality 阈值 δ_S=0.20 年化 Sharpe-gap，exposure-matched benchmark）+ 有限资金生存门（杠杆场景不破产）；三值裁决：REFUTED（CI 上界<δ_S=证伪放弃）/SUPPORTED（CI 下界>δ_S=支持部署）/INCONCLUSIVE（CI 跨越 δ_S=样本不足继续积累数据而非放弃）；实证 5 类零售信号 4 类 REFUTED、trend INCONCLUSIVE、0 类 SUPPORTED；§4.13 二元 pass/fail 把"样本不足"误判"真无 edge"（过早弃真）或反之（反复重申死策略） | **已落地**：experiment 补 `viability_verdict`（supported/refuted/inconclusive）+ §4.13 裁决逻辑三值分类（统计门失败+样本不足→INCONCLUSIVE 继续 probation；样本充分→REFUTED 走 RETIRE_ENTRY；MVP 阶段 OOS<MinBTL 填 inconclusive 诚实记录） |
| ② Leave-One-Out 风险贡献分解 | [arXiv:2604.10375v1 2026-04-11](https://arxiv.org/abs/2604.10375)（Alexander & Fabozzi） | RC 分解为 inherent risk（仓位自身波动贡献，恒为正）+ correlation risk（与其余组合协方差，可放大或对冲），严格加性；单一 RC 数字不区分"孤立高风险"（inherent 主导→降仓位）vs"高相关风险"（correlation 主导→加对冲）——响应策略错配=风控失效；注意与 NIST inherent（控制前）语义不同 | risk_limit 补 `risk_contribution_decomposition`（{inherent_component, correlation_component, decomposition_method: loo/standard_rc/none}；MVP 用 standard_rc，Phase 1.5+ 持仓>20 用 loo） |
| ③ Backtest OVERFIT 5 模式 + PF 比值阈值 | [dibi8 2026-05-25](https://dibi8.com/resources/ai-trading/backtest-overfit-5-patterns-2026/) | 5 种实证模式——walk-forward divergence（IS 优化 OOS 变差，moss-trade-bot Train PF 2.08→OOS 0.94 ratio 2.21）/regime-flip/parameter-cliff/indicator-stacking/survivorship；Train PF/OOS PF ratio>2.0=textbook overfit 阻断、>1.5=suspect warning；最小交易数 directional 300 笔/mean_reversion 500 笔/优化过 1000+ 笔；不同模式修复策略不同——模式分类指导"怎么修"而非仅"是否过拟合" | **已落地**：§4.13 G2 补 PF ratio+min trade count 子检查（统计方法前的一线快速筛，计算极简）+ experiment 补 `overfit_pattern`（none/walk_forward_divergence/regime_flip/parameter_cliff/indicator_stacking/survivorship） |

### 4.36 第十八轮研究对标补充（v1.29.0 新增，2026-08-10 全网搜索）

第十八轮（3 项**"时间轴前移"**，均 Phase 1.5+ 评估，0 schema 落地，0 新 E/G 编号）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① Alpha 发现 EC 综述六组件框架 + 八维自主性评估 | [arXiv:2608.01789v1 2026-08-03](https://arxiv.org/html/2608.01789v1) | 首个将自动公式化 alpha 发现系统化为进化计算视角的综述——六组件 Representation/Variation/Fitness Evaluation/Selection/Memory/Adaptation；八维自主性评估协议：search efficiency/fitness reliability/residual alpha quality/economic diversity/tradability/evolutionary autonomy/market-logic grounding/reproducibility——补 AlphaBench（§4.34⑥）未定义的"自主性"评估维度：AlphaBench 回答"不同 discovery_agent 的因子质量如何"，EC 综述回答"什么算自主发现+如何系统评估" | Phase 1.5+ 评估 |
| ② GT-Score 优化时反过拟合复合目标函数 | [arXiv:2602.00080 2026-01-22](https://arxiv.org/pdf/2602.00080) | 现有反过拟合方法（PBO/DSR/CPCV）都是事后检测——优化器仍以单一指标为目标走偏到过拟合路径；GT-Score 把 Performance+Statistical Significance+Consistency+Downside Risk 组合为单一目标函数，walk-forward+Monte Carlo 实证泛化比（验证收益/训练收益）比基线目标提升 98%——把"反过拟合"从检测端移到优化端 | Phase 1.5+ 参数搜索 MUST 评估用 GT-Score 替代单一 Sharpe 作优化目标 |
| ③ AutoQuant 双重筛查调参-验证显式分离 | [arXiv:2512.22476v3 2026-08-07](https://arxiv.org/html/2512.22476v3) | Stage I 贝叶斯 TPE 调参（真实成本约束嵌入优化目标）与 Stage II 严格回测验证显式分离，两段数据不重叠防 data snooping；双筛查门禁=成本筛查+稳健性筛查；朴素 vs 严格回测年化差异 40%+，双重筛查后存活率<10% | §4.13 G1-G9 隐含"同一数据既调参又验证"风险，Phase 1.5+ 参数搜索 MUST 评估 Stage I/II 数据分离（CPCV 的 purge+embargo 是此思路的更严格版本） |

### 4.37 第十九轮研究对标补充（v1.30.0 新增，2026-08-10 全网搜索）

第十九轮（4 项**"路径与谱系补全"**，4 schema 字段已落地）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① 回撤路径依赖疼痛度量 | [metricgate 2026-05-20 Ulcer Index](https://metricgate.com/docs/ulcer-index-drawdown/) + [algostrategyanalyzer 2026-01-27](https://algostrategyanalyzer.com/en/blog/drawdown-trading-guide/) | 路径依赖度量同时编码深度×持续时间——Ulcer Index `UI=√(Σ D_t² / N)`（0-2% 极低/2-5% 中等/5-10% 升高/>10% 深度或持续）、Ulcer Performance Index/Martin Ratio（年化超额/UI，drawdown 版 Sharpe）、Calmar Ratio（年化收益/\|max_drawdown\|，>1.0 可接受/>3.0 优秀）、Pain Index（算术均值更平滑）；两个策略相同 maxDD=20% 但 UI 可差 5 倍——2 周恢复 UI≈2% vs 18 个月恢复 UI≈10%，前者可持有后者触发赎回；Calmar/UPI 基于已实现回撤比 Sharpe 更稳健（Sharpe 回测到实盘降 30-50%） | risk_limit 补 `pain_metric`（{metric_type: ulcer_index/pain_index/none, threshold, monitoring_window_days}，drawdown 类限额声明）+ experiment 补 `ulcer_index`+`calmar_ratio`（pandas cummax+二次均值 <10 行，G1 补充信号；MVP pain_metric 用 none） |
| ② 执行冲击模型谱系 | [youngju.dev 2026-05-25 TCA Deep Dive](https://www.youngju.dev/transcribe/culture/2026-05-25-tca-market-impact-implementation-shortfall-almgren-chriss-kissell-bloomberg-btca-virtu-big-xyt-2026-deep-dive.en) + [hftradingbook 2026-06-04](https://hftradingbook.com/costs/market-impact) + [MACE RL arXiv:2603.29086v1](https://arxiv.org/html/2603.29086v1) | 谱系——Implementation Shortfall（Perold 1988，4 桶分解）→Almgren-Chriss（2000，均值-方差最优执行）→Square-root law（Gatheral 2010，凹性无动态套利约束下唯一存活形式）→I-Star（Kissell-Glantz 2003，瞬时+永久分量定价）→Propagator（Bouchaud-Farmer 2018，瞬态核函数 η·n/τ+γ·Q）；square-root 是 AC 的经验近似，propagator 是更精细瞬态建模；MACE 实证冲击模型选择致 RL agent 排名质变（差异 40%+）；2026 TCA 从事后报告转向实时 Algo Wheel 路由 | execution_algo 补 `impact_model_type`（square_root/almgren_chriss/i_star/propagator/fixed_bps/pluggable，**同策略不同冲击模型结果不可比，回测 MUST 声明**）+ cost_model 补 `propagator_config`（{decay_kernel, temp_impact_coeff, perm_impact_coeff}）；MVP 用 square_root，Phase 1.5+ 订单量增大后评估 AC/propagator，Algo Wheel 个人项目无需 |
| ③ 基准风格漂移检测 + 2026 大基准重置 | [stockalpha.ai 2026-02-17](https://stockalpha.ai/alpha-learning/custom-benchmarks-for-truth-detecting-hidden-style-drift-and-false-alpha) + [nasdaq.com 2026-06 Great Benchmark Reset](https://www.nasdaq.com/articles/great-benchmark-reset) | FTSE Russell 半年再平衡+S&P 方法论咨询，"被动基准"越来越不被动；custom benchmark 两路线——holdings_based（首选，constrained optimization 匹配因子暴露+最小化 tracking error）/returns_based（回归推断，快速但精度低）；漂移检测三法 rolling regressions/exposure attribution/holdings similarity；关键度量 active share/tracking error/information ratio | benchmark 补 `construction_method`（index_provider/holdings_based/returns_based/custom）+ `active_share` + `style_drift_detection`（MVP：BMK-INDEX-001/002/003 填 index_provider，active_share/style_drift 填 null/none，Phase 1.5+ 多策略时启用） |
| ④ MCP Registry semver + promotable aliases | [MLflow 3.15.0 2026-07-31](https://www.mlflow.org/releases/3.15.0/) | `@production`/`@staging` 可提升别名，晋升=移动指针 O(1) 元数据操作 vs status 翻转重操作；pinning model versions to Git SHAs 降 incident 分析难度 70%；sub-10-second rollbacks via stage pointers | Phase 2+ DB 阶段评估别名指针作轻量部署指针（`@active`/`@canary`/`@shadow`），MVP 阶段 YAML+status 翻转足够不实施 |

> 🔗 **跨文档边界重申（HRP-μ/CRISP 组合构建算法）**：CRISP/HRP-μ（[arXiv:2604.23833](https://arxiv.org/abs/2604.23833) 信号感知层级组合构建）DEFERRED 至 52/54 号文档（组合权重构建属回测引擎+归因报告职责，非注册表职责）——strategy_registry 登记策略元数据（含 combination_strategy regime 融合配置），不实现组合权重算法；如未来 52 号需要，可加 `portfolio_construction_method` enum 引用字段（equal_weight/risk_parity/hrp/hrp_mu/crisp/markowitz 等），待 52 号施工时协同决策，本轮不实施。

### 4.38 第二十轮研究对标补充（v1.31.0 新增，2026-08-10 全网搜索）

第二十轮（4 项**"从二值到结构"**，4 schema 字段+2 审计扩展已落地）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① Temporal Leakage Measurement 从"检测"到"测量" | [arXiv:2608.02985v1 2026-08-04](https://arxiv.org/abs/2608.02985)（Zeyu Zhang & Stadie）+ [arXiv:2602.17234v2](https://arxiv.org/abs/2602.17234) + [temporal-leaks 工具](https://github.com/prakulhiremath/temporal-leaks) | E15/E18 回答"是否泄漏"，本项证明标准 pre/post-cutoff 检查 uninformative——4 个旗舰模型在不可能记忆的问题上仍失败该检查，recency 模仿 leakage，被动回测数学上不可分离两者；测量需外部信息——matched clean control 全局识别+leakage-adjusted score / boundary detection 边界定位；泄漏集中在"出乎 Crowd 意料+训练中覆盖充分"的结果上，partial memorization 被不成比例奖励；"Backtests need not be discarded; they need one defensible reference"；配套 arXiv:2602.17234v2 Shapley-DCLR claim-level 归因 + TimeSPEC 推理时架构 + temporal-leaks 工具 | experiment 补 `temporal_leakage_measurement`（{method: matched_control/boundary_detection/none, leakage_score, reference_model}）+ §4.7 E18 扩展（不新增 E 编号；MVP 无 LLM 回测填 none，Phase 1.5+ origin=llm_generated SHOULD 启用 matched_control） |
| ② Causal Factor Mirage：collider 比 confounder 更危险 | [CFA Institute 2025 Causality and Factor Investing](https://rpc.cfainstitute.org/research/foundation/2025/causality-factor-investing)（López de Prado & Zoonekynd） | Factor Mirage 源自系统性错误设定而非 data-mining——collider bias（纳入被因子和收益共同影响的变量）比 confounder bias 更危险：含 collider 模型展现更高 R²+更低 p-value，计量教规主动偏好这类错误模型；系数符号翻转实证——正确流动性 loading +0.08 → 错误控制变量下 −0.04；collider 变量值在收益前已定，更强关联无法货币化=海市蜃楼；DDQ 核心问题"How did you decide which variables to include, and which did you deliberately exclude?" | factor 补 `causal_structure`（{confounders, colliders, specification_audit}）+ §4.7 E17 扩展（collider 非空=warning highlight；**A 股最常见陷阱：past_return 作 collider**——被 quality 因子和未来收益共同影响，纳入它制造虚假高 R²；MVP 自然语言填，Phase 1.5+ 接 causal-quant 证伪电池补 H-score） |
| ③ regime 持续性显式建模 | [Statistical Jump Model arXiv:2402.05272](https://arxiv.org/html/2402.05272v1)（Nystrup Princeton）+ [Hybrid HMM+Poisson jump-duration arXiv:2603.10202v1](https://arxiv.org/pdf/2603.10202v1)（Cornell） | 标准 HMM 无法生成持续的高波动 regime——极端事件后过快回归；Statistical Jump Model：显式跳跃惩罚迫使 regime 持续，特征仅 price-derived，实证优于 buy-and-hold 和 Markov-switching；Hybrid HMM+Poisson jump-duration：强制真实尾部驻留时间，direct transition counting 估计完全避免 Baum-Welch EM | `regime_detector` enum 补 `statistical_jump`（Phase 1.5+ 评估，A 股 2015 股灾/2024-09 行情是典型持续高波动 regime，配合 §4.12 regime 衰减分类更精准）+ `jump_diffusion_hmm`（Phase 2+，合成数据+压力测试场景设计用） |
| ④ 中国证监会 2026-07 合规：内幕交易司法解释修订+短线交易规定 | [法释〔2026〕13号 2026-07-27 施行](https://stcn.com/article/detail/4041407.html) + [短线交易规定 2026-04-07 施行](http://www.csrc.gov.cn/csrc/c100028/c7618628/content.shtml) | 2012 年来首次系统性修订：敏感期起点大幅前移——"初步意向"/口头沟通阶段即认定内幕信息形成（修订前规则需实质操作阶段）；四类重点人群入刑门槛减半（董监高/实控人/有偿泄密/前科：成交额 100 万/获利 25 万即立案）；三大脱罪理由失效（交易计划抗辩须内幕信息形成前真实订立+完整要素+书面；收购禁暗仓；仅官方公告属合法公开信息）；只泄密不交易同样构罪；短线交易规定：13 种豁免，适用主体 5%+股东/董监高 | risk_limit 补 `compliance_notices` 字段（list[obj] {regulation, effective_date, applicability, impact_note}；**个人项目适用性**：个人量化基于公开数据+非 5% 股东——短线交易规定 not_applicable、内幕信息 conditional（仅 event_driven 策略相关：重大重组/控制权变更"初步意向"时点即敏感期起点，事件窗口划定不得依赖非公开信息）；合规存档非阻断门禁） |

### 4.39 第二十一轮研究对标补充（v1.32.0 新增，2026-08-10 全网搜索）

第二十一轮（6 项**"从假设到证明"**，2 schema 字段+3 审计扩展已落地）：

| 项 | 来源 | 核心发现 | 落地动作 |
|---|---|---|---|
| ① DASH 归因不可能性定理 | [arXiv:2605.21492 2026-05](https://arxiv.org/abs/2605.21492)（Lean 4 机器验证 248 定理 0 证明间隙）+ [dash-shap MIT 开源](https://github.com/DrakeCaraker/dash-shap) | collinearity 下 faithfulness+stability+completeness 三者不可兼得——Rashomon 性质致多个等性能模型分配不同重要性排序；设计空间恰好两族（faithful+complete 但 unstable vs stable 但报 ties，DASH 是后者 canonical member）；gradient boosting 归因比发散 1/(1−ρ²)、NN 87% 特征对不稳定；68% 公开数据集归因翻转（保守下界）；DASH=跨 M 个独立训练模型等权平均 SHAP，Pareto-optimal 达 Cramer-Rao 方差界，M=25 翻转率<1%、M=5 已有显著改善 | factor 补 `attribution_stability`（{method: dash/none, model_count, flip_rate, stable_ranking}）+ §4.7 E16 扩展（flip_rate>20%=warning highlight，MUST 人工裁定冗余方向，SHOULD model_count≥25；MVP 规则型因子填 none，Phase 1.5+ ML 因子 SHOULD 启用 DASH M≥5） |
| ② A 股涨跌停板上游污染 mask-first 设计 | [arXiv:2507.07107v2 2026-05](https://arxiv.org/abs/2507.07107)（USTC） | ±10%/±20% 涨跌停使部分收盘价不可执行，标准行业响应（事后行删除）对滚动窗口算子无效——MA/correlation/rank 在行过滤前累积不可执行价格（upstream contamination），实证虚增 IC 18%+降低 Sharpe 0.44；mask-first=数据加载时构造 Boolean tradability mask 贯穿每个算子，消融证实是单一最大贡献者（+0.44 Sharpe，超任何模型/损失选择） | §4.7 E15 扩展查 `tradability_mask_policy`（none=warning highlight/row_filter 不足/mask_first=MUST）+ data_asset schema 预留该字段（P1-B 已落地）；**A 股前置 MUST**：data provider 层加载 K 线时标记涨跌停（主板涨幅≥9.8%/创业板≥19.5%），因子计算引擎每个滚动窗口算子跳过 mask=false 数据点——140 条因子（2026-08-16 全量重建后计数）中任何用 close 价的都受影响，非可选优化 |
| ③ AlgoXpert 稳定性区域参数选择 | [arXiv:2603.09219v1 2026-03](https://arxiv.org/abs/2603.09219) | 选高原不选尖峰——IS 优先 `Ω_stable={θ\|SR(θ)≥0.9×SR_opt}`；naïve train-test split 对有状态策略产生乐观评估需 purge gap；WFA majority-pass+catastrophic-veto 双门禁；目标从 Sharpe 切到 MinMaxDD 时排名反转揭示风险调整 vs 尾风险权衡 | experiment 补 `parameter_stability_region`（{plateau_identified, cliff_detected, stability_score, selection_method}）+ §4.13 G2 扩展（cliff_detected=true 或 paper/live 阶段 single_optimum=warning；MVP 填 single_optimum，Phase 1.5+ 参数搜索 MUST 启用 stability_plateau） |
| ④ 双曲因子衰减 α(t)=K/(1+λt) | [arXiv:2512.11913v1 2025-12](https://arxiv.org/abs/2512.11913)（KAIST） | 博弈论 Nash 均衡推导——N 个代理竞争固定 alpha capacity K，α(t)=K/(1+λt)；momentum 因子 R²=0.65 优于指数 0.61/线性 0.51；机械因子（momentum/reversal）可建模、判断因子（value/quality）有"进入壁垒"不衰减；2015 后 crowding 加速（与 factor ETF 增长 ρ=−0.63）；crowding 预测尾部风险而非均值——crowded reversal 崩盘概率高 1.7-1.8× | Phase 1.5+ `decay_detection_method` 评估补 `hyperbolic_crowding`（仅 mechanical 因子；A 股 momentum 衰减应拟合双曲非指数，2024-09 行情后 momentum 快速失效是典型双曲衰减） |
| ⑤ MINGLE 图-因子联合组合构造 | [arXiv:2608.06618 2026-08-06](https://arxiv.org/abs/2608.06618)（Imperial） | 相关性图捕获有限样本共动而非经济结构——MINGLE 用因子暴露重定义图局部性，ADMM 联合学习潜因子表示+诱导图拓扑，跨波动率 regime 和交易成本水平一致优于相关性图组合 | Phase 1.5+ 评估（52/54 号职责边界内） |
| ⑥ CogAlpha LLM 代码进化因子挖掘 | [ACL 2026 Oral](https://arxiv.org/abs/2511.18850)（HKU） | 从"公式"升级为"Python 代码"——7 层 21 智能体研究组织架构（市场结构→尾部风险→价量→趋势反转→多尺度复杂性→稳定性门控→几何融合），5 指标筛选+两级选择（65 分位合格/80 分位精英），CSI300 年化超额 16.39%/IR 1.90；反直觉：闭源模型并非天然更强，比的是结构适合探索/筛选/演化 | Phase 2+ 评估 `origin` 补 `llm_code_evolved`（需多 LLM agent 编排框架） |

## 5. P0 已完成三件套（回测必需输入）

> ✅ 三件套已于 2026-08-10 落盘（2026-08-12 commit 8e6436364d 费率校准+硬错误修复）：universe 5 条 / benchmark 4 条 / cost_model 3 条，全部 active，ROOR 已登记。本节保留 schema 定义与登记内容（长期有效），施工过程叙述已折叠。

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

**数据来源**：[24_daban_strategy_detail.md §3.1](24_daban_strategy_detail.md)（打板池）｜ [25_multifactor_strategy_detail.md](25_multifactor_strategy_detail.md)（多因子选股池 §选股池；⚠️ v1.34.0 修正：25 号**无 CSI300/CSI800 成分股实证章节**，CSI300 仅出现于 §3.7 缺失#4 归因伪代码 `benchmark='csi300'` 默认值——UNI-INDEX-001/002 的文档锚点仅为**基准用途**，成分股文件未落盘见待定问题 K3）｜ [26_event_driven_strategy_detail.md](26_event_driven_strategy_detail.md)（事件池）

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

**数据来源**：[25_multifactor_strategy_detail.md §3.7](25_multifactor_strategy_detail.md)（v1.34.0 修正：原引"§CSI300实证"章节不存在，CSI300 仅见于 §3.7 归因基准伪代码默认值）｜[52_backtest_framework_docking.md](52_backtest_framework_docking.md)（基准对接）

> 🔍 **2026 基准选择待定（v1.1.0 新增，需人决策）**：90 号 §13 提到基准选择待讨论。2026 年中证A500（2024-09 发布）已成机构标配底仓——年化收益 8.58% > 沪深300 7.55%，风险收益比 0.34 > 0.30，行业均衡 + 新质生产力权重高（[中信证券2026Q1研究](https://finance.sina.com.cn/jjxw/2026-05-18/doc-inhyiewk0690431.shtml) ｜ [国信证券策略专题](https://pdf.dfcfw.com/pdf/H3_AP202512301811362016_1.pdf)）。
> - **待定问题 B1**：是否新增 `BMK-INDEX-004 中证A500`（candidate）作为 multifactor 策略的备选/替代基准？万得全A（881001）是否也需补登记作为全市场宽基基准？
> - 当前 4 条登记暂不修改，待用户裁定后补登

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

> ⚠️ **2026 费率校准（v1.1.0 修正硬错误）**：原 v1.0.0 登记印花税"千1（0.1%）"为 **2023-08-28 减半前旧税率**，2026 实际为 **万5（0.05%）卖出单边**（财政部/国家税务总局 2023-08-28 减半政策延续至今，2026 无调整）；过户费原登记"万0.1/沪市only"为原规则，2026 实际 **沪深双向均收万0.1（0.001%）**（中国结算统一标准，无最低收费）。佣金万3 + 最低5元 双向为 2026 市场默认档（主流万1-万3可协商，免5违规），登记偏保守合理。详见 §13 修订记录 R1。
>
> 💡 **佣金口径说明（v1.34.0 补，2026-08-12 全网核验）**：CST-ASTOCK-001 的 `commission.rate=0.0003`（万3）按**全佣口径**登记——含交易所规费（经手费 0.0341‰ + 证管费 0.02‰ ≈ 合计万0.541 双向，[金融界证券 2026 收费公示](https://www.jrjzq.com.cn/ueditor/jsp/upload/file/20250711/1752209700574050330.pdf) + [2026 最新收费标准](https://licai.cofool.com/user/guide_view_3448774.html)）：
> - 净佣口径（佣金不含规费、规费另收）下实际成本=净佣+万0.541，回测若用净佣报价需上调；当前万3 全佣登记偏保守，已覆盖规费，无需单独登记规费项
> - 最低 5 元收费对小额交易影响显著（成交<5 万元时实际费率高于名义费率，万1 名义下成交 1 万实际万5）——回测小单笔金额策略（如打板分仓）时 `commission.min=5.0` 的影响 MUST 保留

**数据来源**：~~52 号 §G1~~（⚠️ v1.34.0 修正：52 号 v1.7.4 曾丢失、现 v1.0.0 重建版**无 §G1 章节**，原"万三佣金/5元最低/1bp滑点"引用悬空；现存文本仅 §3.1 佐证"万三佣金+1bp 滑点+印花税"三要素。**费率校准真源已迁至本节 R1 修订记录**）｜ [40_execution_broker.md §冲击模型](40_execution_broker.md)（保守模型冲击）｜ 2026 费率实证：[华泰证券2026费率](http://m.toutiao.com/group/7671636219272430089/) ｜ [2026最新收费标准](https://licai.cofool.com/user/guide_view_3447293.html) ｜ [2026炒股成本揭秘](https://post.m.smzdm.com/p/a70o48xd/)
- 交叉验证（v1.6.0 补）：[yoyo-quant 2026-08-07](https://github.com/Tastelessor/yoyo-quant)（A 股量化框架开源项目）费率配置"佣金万1/最低5元 + 印花税万5/卖出单边 + 过户费 + 滑点 tick + 涨跌停价格剪裁"——印花税万5/卖单边与本项目 R1 修正一致；佣金万1 vs 本项目万3 差异因 yoyo-quant 面向更低佣金档，本项目万3 偏保守合理

**square_root 冲击系数校准说明**：CST-ASTOCK-002 的 `coefficient=0.1` 相对 2026 业界主流 prefactor `Y≈0.6`（hftradingbook 2026-06-04）/ AAPL 实证 `c_raw=0.69, c_eff=0.34`（arXiv 2606.24019, 2026-06）偏低约 6 倍。**对个人小资金项目合理**——个人账户多数订单 <1% ADV（40 号 §撮合拆单），无大单冲击，0.1 系数更接近"个人小单无冲击"的现实；Phase 1.5 AUM 增长到大单时需按 40 号 §13.1 校准路径重新拟合（40 号 v1.6.6 已登记 Phase 1.5 校准方法论）。

> 🎯 **2026-08 最新研究验证（v1.2.0 新增）**：平方根冲击律在 A 股的**必要性**与**指数差异**已被 2026-07 最新论文双重确认：
> - **必要性**（[Zhou et al. arXiv:2607.05141, 2026-07-06](https://arxiv.org/html/2607.05141v1)）：square-root price impact 是 A 股学习智能体市场内生操纵周期的**必要条件**——线性冲击会完全消除 Hopf 分岔使零售市场无条件稳定，平方根冲击创造自维持非线性振荡器。**这从理论上验证了本项目选择 `square_root` 冲击模型（而非 linear）的正确性**。
> - **指数差异**（[Han, Wu, Cheng arXiv:1610.08767, 中国市场实证](https://arxiv.org/pdf/1610.08767v1)）：172 亿条中国 A 股逐笔记录拟合，临时冲击幂指数 `α≈0.7`（非 0.5），永久冲击 `α≈0.8`。**A 股 α≈0.7 高于美股 0.5**——个人项目 `coefficient=0.1` 的保守设定需在 Phase 1.5 重新评估是否应改用 `power_law(exponent=0.7)` 而非 `square_root(exponent=0.5)`。
> - **拆单必要性**（[Zhou et al. arXiv:2607.04280, 2026-07](https://ideas.repec.org/p/arx/papers/2607.04280.html)）：订单拆分 + 流动性补充是平方根律的**联合必要条件**（移除订单拆分 δ 从 0.549 塌缩到 0.324）。**验证 40 号 TWAP/VWAP/ICEBERG 拆单算法的必要性**。
>
> **对 cost_model_registry 的影响**：当前 `square_root` model 字段保留（理论必要性已证）；Phase 1.5 校准时需考虑新增 `power_law(exponent=0.7)` 选项作为 A 股专用冲击模型（待定问题 C1），并按 40 号 §13.1 拟合 `coefficient` 实际值。MVP 阶段 `square_root(coeff=0.1)` 对个人小单足够保守，不阻塞当前回测。

> ⚠️ 注意：现有 `src/zephyr/.../cost_estimator.py` 是 **AI token 成本**，非交易成本。交易成本在 `engine_base.py`，本注册表管后者。

## 6. P1 待施工七注册表

> ✅ **七表已全部施工**（2026-08-13 落盘核验）：factor 111（ac75684951）/ strategy 59（ac75684951）/ technical_indicator 40（eea122f432）/ execution_algo 6（c7701fcde6）/ risk_limit 62（c6908d4678）/ data_asset 166=15源+76数据集+75作业（c7701fcde6）/ chart_pattern 15（206f48586f）。
> 结论：§4.20 监管字段 + §4.23③ 价格笼子三字段 + 数据源 license_type 标注均已随施工纳入；ROOR 登记仅 PAT 已补，IND/EXA/DATAFLOW 待登记（§9.1）。本节保留 schema 定义与规则内容（长期有效），施工过程叙述已折叠。

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
  schema_plan: obj               # LLM 因子挖掘的语义抽象层（v1.19.0，对标 AlphaSchema）
                                 # {event, context, qualities, direction, output}；解耦因子语义与实现公式
                                 # 人工因子可空；LLM 挖掘因子 MUST 填
  params: obj                    # 参数字典（如 {window: 20}）
  inputs: list[str]              # 输入字段（引用 field_dictionary）
  outputs: list[str]             # 输出列名
  alpha_source: str              # alpha 来源一句话
  frequency: enum                # daily/intraday/tick
  lookback_period: int           # v1.2.0新增：回看周期（如 20/60/250 日），回测/因子计算必需
  universe: str                  # 适用股票池（universe_id）
  benchmark_id: str              # v1.2.0新增：因子评估基准（benchmark_id），计算超额 IC/IR
  neutralization: str            # industry/size/market/none
  pit_policy: str                # PIT 处理策略防 look-ahead：每个 feature 值 MUST 有 available_at 时间戳
                                 # A 股关注点：财报 lag（avg 43天）/复权口径/涨跌停不可成交/指数成分变动/停牌/restatement
                                 # 填写示例："strict" / "lag_60d" / "price_only"
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
  # 数据质量监控（v1.4.0，E11 审计）：衰减=输出端（§4.8），数据质量=输入端，互补
  data_quality_policy: obj       # {null_rate:{threshold,window}, drift_method:psi/ks/wasserstein, drift_threshold}
  null_rate: float               # 运行时：当前空值率（>2x baseline 告警）
  drift_psi: float               # 运行时：PSI 分布漂移（<0.1稳定/0.1-0.25轻微/>0.2主要）
  drift_ks_pvalue: float         # 运行时：KS 检验 p-value（<0.01 显著漂移）
  range_bounds: obj              # {min,max} 训练期范围（越界=数据异常）
  last_quality_scan_at: date     # 上次数据质量扫描时间
  # 因子冗余治理（v1.20.0，E16 审计）：同组 MUST ≥1 个 independent
  correlation_group: str         # 相关性分组（如 value/quality/momentum）；MVP 按 10 类粗分
  redundancy_status: enum        # independent/redundant/orthogonal
  # 因果验证声明（v1.21.0，E17 审计）：注册时 MUST 声明因果图，避免事后合理化
  causal_graph: str              # 因果图/经济逻辑（自然语言或 DAG）；MVP 可填自然语言
  # 因子构造偏差审计（v1.22.0，E19 审计）：仅 price-derived 因子声明
  lib_audit: obj                 # LIB 审计：{applicable, signal_return_shared_noise, mitigation}
  ex_post_filter_audit: obj      # ex-post 过滤审计：{uses_full_period_stats, walk_forward_corrected, filter_method}
  # RMT 去噪相关性矩阵（v1.23.0，E20 审计）：因子数>20/q>0.1 时 MUST 启用
  rmt_denoised: obj              # {applicable, method: clipping/shrinkage/none, q_ratio, noise_eigenvalue_ratio}
  # 流动性因子度量（v1.26.0，仅 factor_class=liquidity 声明）
  liquidity_metric: obj           # {metric_type, value, estimation_method, data_requirement}
                                 # ⚠️ Kyle lambda MUST 用 OLS slope=cov(log_ret,signed_flow)/var(signed_flow)，非 ratio
  # 因果设定结构（v1.31.0，E17 扩展审计）：collider 比 confounder 更危险
  causal_structure: obj          # {confounders, colliders, specification_audit}
                                 # collider 非空=warning highlight；A 股最常见陷阱：past_return 作 collider
  # 归因稳定性（v1.32.0，E16 扩展审计）：DASH 跨模型聚合 SHAP
  attribution_stability: obj     # {method: dash/none, model_count, flip_rate, stable_ranking}
                                 # flip_rate>20%=warning highlight；MVP 填 {method: none}
  # 因子发现来源（v1.25.0/v1.27.0）
  discovery_agent: enum          # human/rd_agent/efs/hubble/quantevolver/other
  llm_safety_stack: obj          # LLM 因子生成安全栈（discovery_agent≠human 时 MUST 声明）
                                 # {ast_validation, dsl_constrained, complexity_control, dual_channel_rag, family_aware_selection}
```

**factor_class 10 类**（Barra 6 + A股特色 4）：
- Barra 标准：`value`（价值）/ `quality`（质量）/ `momentum`（动量）/ `volatility`（波动）/ `size`（规模）/ `liquidity`（流动性）
- A 股特色：`event`（事件驱动，并购/业绩/政策）/ `intraday`（日内/打板，T+1+涨跌停特色）/ `technical`（技术指标衍生）/ `sentiment`（情绪/舆情，游资接力）

**数据来源**：
- [15_data_feature_layer_spec.md](15_data_feature_layer_spec.md)（因子工程总纲，why 层）
- [25_multifactor_strategy_detail.md](25_multifactor_strategy_detail.md)（IC/衰减/换手评估格式）
- 代码 `src/zephyr/factor/`（v1.1.0 修正：原 v1.0.0 误写 `src/zephyr/factor/ashare/` 15 子目录，**该路径不存在**。实际结构：`analysis/api/core/governance/infrastructure/services/technical_indicators/_extensions` 子目录 + `factor_base.py`/`momentum_factor.py`/`value_factor.py`/`intraday_snapshot_factors.py`/`alpha_signal_pipeline.py`/`bus_factor_defense.py` 6 个因子模块文件）
- dataflow DS-015+（因子数据集登记，v1.1.1 修正：DS 编号实际到 DS-076 总 76 条，非 DS-028 截止）

**设计要点**：
- 与 technical_indicator_registry 正交：技术指标=OHLCV 计算工具，因子=alpha 来源
- 连板因子 / 趋势因子 = 2 条独立记录（alpha 来源不同，非 variant）
- 对标 WorldQuant Alpha Bank / qlib Alpha158
- 版本管理（v1.2.0）：schema/UDF 变更触发版本快照、metadata-only 原地更新、`version_pin` 回滚；PIT correctness 由 `pit_policy` 承载

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
  # 衰减检测（§4.8）：MVP 用 profit_factor/z_score；Phase1.5+ 用 cusum_ph_bocpe（CUSUM 分量须鲁棒变体）
  decay_detection_method: str    # rolling_ic/mrp/cusum/cusum_ph_bocpe/profit_factor/z_score/gsa_llr_cusum/none
  decay_threshold: float         # ic_ratio < 0.7 触发 decayed
  last_decay_scan_at: date
  mrp_baseline: float            # Minimum Regime Performance 基线
  # 衰减后适应（§4.12）
  adaptation_level: int          # 1-5：1静默/2减仓/3季度refit/4在线学习/5退役（默认1）
  last_refit_at: date            # refit 间隔≥60天防过拟合
  baseline_sharpe: float         # OOS walkforward 期基线 Sharpe
  # baseline 扩展（v1.5.0，E12 审计）：MUST 在 deployment（paper→live）时保存
  baseline_expectancy: float     # 基线单笔期望
  baseline_win_rate: float       # 基线胜率
  baseline_profit_factor: float  # 基线盈亏比
  baseline_max_drawdown: float   # 基线最大回撤
  baseline_trade_frequency: float # 基线交易频率（trades/month）
  # 衰减原因分类（v1.5.0，Five Horsemen，§4.12 Step 1.5）
  decay_cause: enum              # crowding/regime/overfitting/tech/depletion/unknown
  decay_scan_frequency: enum     # monthly/weekly/daily（active/live=monthly, monitoring=weekly, decayed=daily）
  # 性能（运行时可空）
  sharpe: float
  max_drawdown: float
  annual_return: float
  capacity: float
  turnover: float
  last_evaluated_at: date
  code_commit: str               # v1.4.0新增：可选，git commit hash（DB 阶段 MUST，对标 beefed.ai compute_git）
  # 数据质量监控（E11 审计）
  data_quality_policy: obj       # {null_rate:{threshold,window}, drift_method:psi/ks/wasserstein, drift_threshold}
  null_rate: float               # 运行时：当前空值率
  drift_psi: float               # 运行时：PSI 分布漂移
  drift_ks_pvalue: float         # 运行时：KS 检验 p-value
  range_bounds: obj              # {min,max} 训练期范围
  last_quality_scan_at: date
  # 策略组合配置（v1.18.0）：单体策略=null；组合策略登记 regime 检测器+各 regime 权重
  combination_strategy: obj      # {regime_detector, allocation_weights}
                                 # regime_detector: 200d_sma/hmm/wasserstein_hmm/news_aware/text_var_dual/statistical_jump/jump_diffusion_hmm/none
  # Meta-labeling 方向×仓位分离（v1.18.0）：仅 discretionary/规则型主模型适用（v1.26.0 边界）
  meta_labeling_config: obj      # {strategy_subtype, primary_strategy_id, meta_strategy_id, base_models_error_correlation}
  # 策略来源标记 + LLM 蒸馏（v1.19.0）
  origin: enum                   # human/llm_generated/hybrid
  distilled_to_code: bool        # llm_generated 策略 distilled_to_code=false=阻断上线（§4.13 G5）
  # 策略容量配置（v1.20.0，§4.13 G9 门禁）
  capacity_aum_limit: float      # 策略资金容量上限（元）
  participation_rate_limit: float # 参与率上限（0.05=5% ADV）
  market_impact_model: enum      # square_root/linear/none（MVP 可 none，资金增长后 MUST square_root）
  # 仓位管理方法（v1.17.0）
  sizing_method: enum            # fixed_fraction/kelly/fractional_kelly/risk_parity/conformal_kelly
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

> 🎯 **2026 策略生命周期对标（v1.2.0）**：10 阶段模型新增 Decay Detection + Decommissioning 独立阶段（§4.8 完整映射）。本 schema `lifecycle_status` 8 态含 `decayed`；`mrp_baseline` 承载 Alexander & Fabozzi 2026 MRP 跨 regime 持久性测量；`decay_threshold: 0.7` 对标 Vibe-Trading 恢复条件 IC ratio>0.7。经验数据：alpha 衰减年均 US 5.6%/EU 9.9%；68% 策略 18-24 月需修改/退役。衰减检测算法见 §4.8 DECAY_SCAN。

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

**5 大类**（对齐 16 号 §6.1-6.5，v1.1.0 修正第5类，v1.34.0 修正章节引用与列数）：

| 类 | 代表指标 | 个数 |
|---|---|---|
| trend（趋势） | MA/MACD | 10 |
| momentum（动量） | KDJ/RSI | 10 |
| volatility（波动） | BOLL | 8 |
| volume（量能） | MFI | 7 |
| reversal（反转） | — | 5 |

合计 40 指标 **58 输出列**（v1.34.0 修正：原"~55 列"为过时约数，16 号实际 58 列，由测试契约 `_EXPECTED_TOTAL=40/_EXPECTED_COLUMN_TOTAL=58` 锁定）。
- **原 v1.0.0 第5类误写 `structure`，实际 16 号 §6.5 + 代码 `src/zephyr/factor/technical_indicators/reversal.py` 均为 `reversal`（反转类）**——schema-代码-文档三方漂移已修正
- 代码 `technical_indicators/` 实际文件：indicator_base/momentum/reversal/trend/volatility/volume 6 个 .py

**9 个周期**（project_memory）：1min/5min/15min/30min/60min/120min/日/周/月（120min 由 60min 两根聚合）

**数据来源**：
- [16_technical_indicator_catalog.md](16_technical_indicator_catalog.md) §6.1-6.5 清单（40 指标/5类/58 输出列）迁入（v1.34.0 修正：清单在 16 号 §6 非 §2，§2 是 9 周期覆盖说明）
- 16 号文档降级为 why 层（设计原则/双模式计算/宽表存储/A股约束），§6 清单改引用注册表
- 代码 `src/zephyr/factor/technical_indicators/`

**设计要点**（施工已完成，要点长期有效）：
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
  # 2026-07 监管合规字段（§4.20①② 交易规则修订+程序化交易细则，v1.14.0 新增 6 字段；§4.20③ 局域网关闭，v1.15.0 补 2 字段）
  max_orders_per_sec: int        # 每秒申报+撤单上限（默认 14，监管高频认定 15 笔/秒留 1 笔余量）
  max_daily_orders: int          # 单日全市场申报撤单上限（默认 19000，监管 20000 笔留余量）
  cancel_rate_limit: float       # 单日撤单率上限（默认 0.15，合规红线；40 号 CancelRateGuard 对齐）
  min_order_interval_us: int     # 每笔报单最短停留微秒（默认 50，禁止 sub-50µs 闪单）
  is_hft: bool                   # 是否高频交易（超阈值策略须标 true 并触发报备）
  after_hours_eligible: bool     # 盘后固定价格交易资格（15:05-15:30，收盘价精确成交无滑点）
  latency_floor_ms: float        # 广域网双向时延地板（默认 2.0ms，2026-07-31 局域网关闭后监管地板）
  network_type: enum             # wan/lan（默认 wan），行情接入方式标记
  # A 股微观结构约束（§4.23③ 第五轮，v1.16.0 新增 3 字段；40_execution_broker v2.6.0 已实现 check_price_cage）
  price_cage_config: obj         # 价格笼子配置：{board: main/gem/star/bse,
                                 #  buy_ceiling_pct: 1.02/1.02/1.02/1.05, sell_floor_pct: 0.98/0.98/0.98/0.95,
                                 #  has_unit_floor: true/true/false/false, unit_floor_yuan: 0.1}
                                 # 主板/创业板买≤102%∩+0.1元孰高、卖≥98%∩-0.1元孰低；科创板纯 102%/98%；北交所 105%/95%
  t_plus_1: bool                 # T+1 制度（A 股固定 true，回测 MUST signal.shift(1)）
  limit_up_down_untradable: bool # 涨跌停不可成交（A 股固定 true，回测 MUST 检查 abs(ret)<limit_pct）
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

> 🎯 **2026 RL 自适应执行远期选项（v1.2.0 新增）**：3 项进展作为 `rl_policy_ref` 字段的远期选项（Phase 1.5+ 评估，MVP 不实施）：
> - **MACE**（[arXiv:2603.29086, 2026-03-30](https://arxiv.org/html/2603.29086v1)）：AC 框架+平方根冲击 RL 执行环境，关键发现=成本模型实质性影响算法排名，HPO 必需
> - **Cheridito & Weiss**（[arXiv:2507.06345v2, 2026-01-26](https://arxiv.org/pdf/2507.06345v2)）：Logistic-Normal 策略参数化，市场单+限价单联合分配
> - **PPO 自适应执行**（[Stanford CS224R 2025](https://cs224r.stanford.edu/spring_2025/projects/pdfs/CS224r_final_paper%20(4).pdf)）：波动率高/流动性低时自动减速暂停
>
> **个人项目适用性评估**：RL 执行需 LOB 模拟器+大量训练+HPO，对个人项目属过度工程（MVP 阶段）；schema 预留 `rl_policy_ref`，Phase 1.5+ AUM 增长到需要自适应执行时可引用。MVP 阶段 6 算法足够；`warmup_participation_rate`+`cooling_period` 借鉴 MACE 的 HPO 发现（避免 epoch 间参与率单调递增的病态）。

> 🔒 **执行算法反博弈与 TCA 双报告（v1.7.0 新增，对标 [marketmaker.cc 2026-07-15](https://marketmaker.cc/en/blog/post/twap-vwap-pov-execution-algorithms/) + [iotdigitaltwinplm 2026-06-18](https://iotdigitaltwinplm.com/vwap-execution-algorithm-architecture-2026/)）**：
> **① 反博弈随机化**：每个执行调度器都是对成交量预测的下注——TWAP 押注流动性时间均匀，VWAP 押注今日曲线=昨日，POV 押注实时成交量=交易理由。**确定性切片是被抢跑的陷阱**："A TWAP that fires a child order every 60 seconds at :00 is a metronome, and metronomes get front-run."调度应是**期望值平坦的 Poisson 过程**而非时钟；"retrofitting anti-gaming behavior into a deterministic scheduler is painful" → `anti_gaming` 字段（MVP 阶段 TWAP/VWAP 用 `timing_randomization: poisson, size_jitter: 0.1-0.2`）。
> **② POV 内生性公式**：POV 算法 x_t = γ·V_t 中 V_t 包含自身成交量，实际交易量 x = γ/(1-γ)·M（M=他人成交量）——γ=0.10 时修正温和（11.1%），γ=0.25 时 33%，**γ=0.5 时定点发散** → 40 号 POV 参与率≤5% 约束（修正仅 5.3%）合理性由此验证；schema `params` 中 POV 类 MUST 登记 `max_participation_rate` 且 ≤0.10。
> **③ TCA 双报告**：VWAP slippage（"跟市场均价差多少"，算法表现）和 implementation shortfall（"跟决策价差多少"，总成本含延迟+冲击）回答不同问题——"Shipping only the flattering one erodes trust." → `tca_metrics` 字段，MVP 用 `[vwap_slippage, implementation_shortfall, fill_rate]`，Phase 1.5+ 补 `market_impact`。

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
  # 生命周期阶段 + 响应策略（v1.22.0）
  stage: enum                    # active/deprecated/disabled（对标 Apicurio 四阶段；MVP 三态足够）
  response_strategy: enum        # mitigate/transfer/avoid/accept（ISO 31000 风险响应策略，与 breach_action 正交）
  # 回撤阈值校准方法（v1.23.0/v1.27.0）：仅 drawdown 类限额声明
  drawdown_calibration_method: enum  # gaussian/rsb_non_gaussian/fbm_long_memory/weighted_kolmogorov
                                 # MVP 默认 gaussian；重尾策略 γ₄>6 MUST 切换 rsb_non_gaussian
  # VaR 校准方法（v1.23.0/v1.27.0）：仅 var 类限额声明
  var_calibration_method: enum   # historical/rwc_conformal/weighted_kolmogorov
                                 # MVP 默认 historical；Phase 1.5+ MUST 评估 rwc_conformal
  # 风险贡献结构分解（v1.28.0）：区分"自身波动大"vs"组合相关性高"
  risk_contribution_decomposition: obj  # {inherent_component, correlation_component, decomposition_method: loo/standard_rc/none}
  # 回撤路径依赖疼痛度量（v1.30.0）：仅 drawdown 类限额声明
  pain_metric: obj               # {metric_type: ulcer_index/pain_index/none, threshold, monitoring_window_days}
  # 合规通知登记（v1.31.0）：合规存档非阻断门禁
  compliance_notices: list[obj]    # {regulation, effective_date, applicability, impact_note}
```

**9 种限额类型**：position（仓位）/ concentration（集中度）/ drawdown（回撤，含四级 Protocol）/ var（VaR 5级）/ es（期望短缺）/ leverage（杠杆）/ turnover（换手）/ kill_switch（熔断）/ firm_risk（公司级聚合）

**数据来源**：
- [35_drawdown_protocol_impl.md](35_drawdown_protocol_impl.md)（四级回撤 Protocol）
- [36_var_es_monitoring.md](36_var_es_monitoring.md)（VaR/ES 监控）
- [37_liquidity_crisis_protocol.md](37_liquidity_crisis_protocol.md)（流动性危机）
- [32_firm_risk_aggregator.md](32_firm_risk_aggregator.md)（公司级聚合）
- 代码 `src/zephyr/risk/`（v1.1.0 修正：原 v1.0.0 误引 `config/risk_register.yaml`，**该文件是 MOD-INF-001 基础设施容量保障风险登记表 R1-R21**——SQLite 并发/死锁/Schema 漂移/ChromaDB 线程泄漏等运维风险，**非交易风控限额**。两者概念不同：交易风控限额=硬阈值（position/drawdown/var/kill_switch），基础设施风险登记=概率评估（likelihood×impact）。交易风控限额真源在 `src/zephyr/risk/`：risk_limits.py/risk_manager.py/risk_manager_base.py/risk_validator.py/stop_loss.py + core/cross_asset/implementations/services/api/infrastructure 子目录）

> project_memory 约束：reconciler 只能 `warn`/`skip`/`fix-in-place`，禁止 `action="commit"`。本注册表 `breach_action` enum 第四项 `halt` 用于 Kill Switch 场景（非 reconciler 自动执行，而是风控硬熔断人工介入），与 reconciler 约束不冲突。

> 🎯 **NIST/ISO 31000 对标（v1.2.0）**：本 schema 已对标 `inherent_risk`/`residual_risk`（NISTIR 8286 固有 vs 剩余风险）/`kri_frequency`/`review_cycle`（ISO 31000 Monitor&Review）。**概念边界**：本表管"交易风控限额"（硬阈值+breach_action），不等同于 ISO 31000 全量 Risk Register（非交易风险在 `config/risk_register.yaml`）。两者互补不合并。

> 🔒 **KRI Governance（v1.6.0）**：6 角色映射为 2 主体 4 职能——Human Owner 承担 Threshold Approver + Board Reporting Owner，AI Agent 承担 Metric Owner + Data Owner + Escalation Recipient + Action Owner。**关键约束**：`threshold_value` 变更（尤其放宽）MUST 走 §4.9 EVOLVE_ENTRY schema_sig 变更（版本快照+人工审批），禁止 AI 自行放宽阈值。持续违约协议：`current_consumption` 超 `threshold_value` 持续 ≥2 个 `kri_frequency` 周期 → §4.12 ADAPT_STRATEGY 升级 + 人工审查。

> 🧭 **BM-RC-01 作战地图环节 why 层补登（v1.34.1 作战地图全覆盖补丁）**：作战地图 BM-RC-01（风控策略与限额管理，L4，production：RK-01 risk_manager + RK-06 default_position_limit_checker）及其三个子环节在本注册表章节的显式映射如下——回答"§2 自注的『9 种限额散落代码+config』缺口是怎么被本表闭合的"。
>
> **① BM-RC-01-B 九种限额类型与消耗追踪（MOD-L04-001，`risk/risk_limits.py`）**
>
> 9 种限额类型语义表（以作战地图登记口径为准，与本表 `limit_type` enum 映射）：
>
> | 作战地图限额类型 | 语义 | 本表 limit_type 映射 |
> |---|---|---|
> | SINGLE_INSTRUMENT | 单标的仓位限额（单票敞口上限） | position |
> | SECTOR | 行业/板块敞口限额（申万一级聚合） | concentration |
> | GROSS | 总敞口限额（多空绝对值合计） | position（scope=portfolio） |
> | NET | 净敞口限额（多-空净值，A 股现货无做空≈GROSS） | position（scope=portfolio） |
> | VAR_95 / VAR_99 | 在险价值 95%/99% 置信度限额 | var（§6.2.2 schema `var_calibration_method`，v1.34.0 K4 补登 RLM-VAR-001~005） |
> | MAX_DD | 最大回撤限额（四级回撤 Protocol 8/15/20/25%） | drawdown（RLM-DRAWDOWN-001~008） |
> | LEVERAGE | 杠杆倍数限额（个人 A 股现货无杠杆，登记为合规兜底） | leverage |
> | FACTOR | 因子暴露限额（单因子/因子簇敞口） | concentration（factor 维度） |
>
> **消耗追踪模型（LimitConsumption 口径）**：限额消耗=**notional 占用口径**——
> - 每条限额实时维护 `current_consumption`（本表 schema 运行时字段），计量该限额约束维度上已被占用的名义额度（如单票持仓市值/单行业合计市值/组合 VaR 估计值），与 `threshold_value` 的比值即消耗率
> - 运行时装配点与 [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) §3.13 盘中实时风控循环衔接——`intraday_risk_loop` 内 `LimitConsumption()` 实例逐 tick 更新（A 股 2026 新规口径：每秒 15 笔申报/撤单率 15% 亦走同一消耗追踪），消耗率达预警阈值即触发 BM-RC-01-C
> - YAML 阶段 `current_consumption` 为空（仅台账），DB 阶段落库
>
> **② BM-RC-01-C 预警分级与审批流（MOD-L04-001，`risk/risk_manager.py`）**
>
> 预警分级（消耗率触发）：**WARNING（黄）/ CRITICAL（橙）/ EMERGENCY（红）** 三级，AI 自治分级处置——
>
> | 级别 | 消耗率参考 | 处置 | 通知通道（与 [55_monitoring_review §3.1B](55_monitoring_review.md) 三级告警衔接） |
> |---|---|---|---|
> | 黄 WARNING | 接近阈值（如 ≥80%） | AI 自治：记录+降速开仓评估，不打断 | YELLOW → {log} |
> | 橙 CRITICAL | 触及阈值（≥100%） | AI 自治：按 `breach_action` 执行（warn/skip/fix-in-place）+ 通知 | ORANGE → {log, email} |
> | 红 EMERGENCY | 硬边界突破（Kill Switch 级） | **Owner 确认制**：`halt` + 人工审批后方可恢复（审批流"合规官放行"在个人项目映射为 Owner 本人，与上节 KRI 2 主体 4 职能一致） | RED → {log, email, wechat} |
>
> 审批流降级：审批流不可用 → 保守拒单待人工（宁停不错）。红色级别的 Owner 确认与 §6.2.2 上节"阈值放宽需更高级别签批"约束同源——AI 可执行处置动作，但**恢复与阈值变更必须过人**。
>
> **③ BM-RC-01-A 风控策略 CRUD 与版本管理（C-004 自适应风控三层体系：预判层+监控层+熔断层+B-001~B-006 硬边界）**
>
> 策略 CRUD 状态机与版本管理规则——**改了能追溯、出问题能回滚**：
>
> - **状态机**：复用本表 `stage` enum（active/deprecated/disabled 三态，v1.22.0 对标 Apicurio）+ `status` 字段——新限额草稿→active 生效→deprecated 宽限（新策略不引用、存量继续）→disabled 硬禁用；退役走 §4.10 RETIRE_ENTRY（90 天宽限+审计保留）。
> - **版本管理**：任何限额/策略变更走 §4.9 EVOLVE_ENTRY——`change_type` 分类（metadata/schema_sig/code_ref/status）+ 自动版本快照（改了能追溯：git commit 时间戳 + SHA256 manifest）；阈值放宽 MUST 触发人工审批门禁（§6.2.2 KRI 治理约束）。
> - **回滚**：出问题走 §4.14 ROLLBACK_ENTRY——任一版本快照可回滚（YAML 阶段=git revert + entry version 回指），回滚动作本身也登记版本（可追溯"回滚了什么"）。
> - **与 C-004 三层体系的映射**：预判层=盘前限额装配（BM-RC-02 消费 CTR-003 RiskLimits）；监控层=盘中消耗追踪（①）；熔断层=红色 EMERGENCY `halt`（②）。B-001~B-006 硬边界登记为 kill_switch 类限额条目（v1.34.0 K4 补登 RLM-KILL-SWITCH-001）。
>
> **裁定（production 补 why 层，非新建）**：BM-RC-01 三子环节代码均为 production/stable（RK-01/RK-06/MOD-L04-001），本补丁仅闭合"作战地图环节 ↔ 注册表 schema ↔ 代码锚点"的显式映射，无新增建设项。**重评条件**：v1.34.0 K4（var/es/kill_switch 条目补登）与 P1-B Step4-8 施工完成时复核本映射与落盘条目一致性；limit_type enum 如需新增 FACTOR 独立类型（当前并入 concentration），走 §4.11 EVOLVE_SCHEMA。

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
    license_type: enum           # academic_only/commercial_license/proprietary（v1.17.0 §4.24⑤ 落地）
                                 # AKShare=academic_only（明确声明仅学术用途不可商用）；Wind/iFinD=commercial_license
                                 # 实盘前 MUST 评估商业授权（龙虎榜/Level-2 数据同理）
    provides_datasets: list[str]
    env_config: str              # 如 config/.env.qmt
    status / created_at / updated_at

datasets:                        # 沿用原 dataflow_graph_registry datasets 段
  - dataset_id: str             # DS-{NAME}-{NNN}
    name / schema / frequency / pit_policy / contract_ref / module_id
    # 回测数据偏差治理（v1.18.0 新增，对标 §4.7 E14 + preprints.org 2026-06-04 三分类偏差 taxonomy）
    survivorship_free: bool     # 数据源是否含退市证券（true=无生存偏差/false=仅存活/unknown=未知）
                                # 行情类 dataset MUST 声明：AKShare 日线=unknown（仅学术），Norgate/Compustat=true
                                # 生存偏差使 US equity 年化高估 1-3%，小市值/价值策略更严重
    pit_available: bool         # 是否支持 point-in-time 查询（财报按公布日期对齐，防前瞻偏差）
                                # 财报类 dataset MUST 声明：前瞻偏差使 mean-reversion 收益虚增 40-60%
    earnings_lag_days: int      # 财报公布平均滞后天数（用于 PIT 对齐校验，行情类 dataset 可空）
    # PIT 字段语义契约（v1.25.0，E14 d 维度审计）
    as_of_date_semantics: enum  # eod_bar/execution_date/declaration_date/ex_date/universe_snapshot
                                # 复权价用后复权（backward-only）避免前瞻偏差
    # A 股涨跌停可交易性掩码（v1.32.0，E15 扩展审计）
    tradability_mask_policy: enum  # mask_first/row_filter/none
                                # mask_first=MUST（数据加载时构造 Boolean mask 贯穿算子）；row_filter 不足；none=warning
    # LLM 前瞻偏差治理（v1.19.0，E15 审计）：仅 LLM-relevant dataset 声明
    llm_training_cutoff: date   # LLM 训练截止日期；MVP 未用 LLM 填 N/A
    lookahead_test_method: str  # none/lookahead_bench/ktd_fin_4level；MVP 填 N/A
    # 标签延迟分层监控（v1.26.0）
    label_delay_days: int       # 标签可用延迟天数（财报类声明）；A 股财报: 季报45天/年报4个月
    drift_detector: str         # none/evidently/nannyml/alibi_detect；MVP 填 none，Phase 1.5+ 启用
    # 行情通道时延档案（v1.15.0，§4.20③ 局域网关闭合规）
    latency_profile: str        # 广域网 1.2-2ms vs 旧局域网 0.3-0.8ms
    colocation_eligible: bool   # 默认 false（2026-08-31 网关指引施行后已搬离）
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

> ⚠️ **改名登记状态（v1.33.0/v1.34.0 反查，转待定问题 K1）**：裁定#223（2026-08-10）已登记改名但**方向写反**（登记为 data_asset→dataflow_graph，与 S6 裁定 dataflow_graph→data_asset 相反），且其声称"62 号 §9.4 D1 已标记完成"实际未标记（三方状态漂移）。物理层现状（2026-08-14 核验）：data_asset_registry.yaml 已落盘（active，15 源+76 数据集+75 作业），旧 dataflow_graph_registry.yaml 仍并存。待用户裁定后修正 ruling_registry（见 §14 K1）。

**数据来源**：
- 原 [dataflow_graph_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml)（v1.1.1 修正：实际含 **DS-001~DS-076 共 76 条** datasets + jobs，原 v1.0.0 写"DS-001~029"严重少算；v1.1.0 初估"030+"仍少算，v1.1.1 全量 grep 确认 76 条）
- [15_data_feature_layer_spec.md](15_data_feature_layer_spec.md)（数据源/PIT/质量）
- config/.env.qmt（miniQMT 连接，已验证存在）

**OpenLineage 对标**：三实体（sources/datasets/jobs）对齐 OpenLineage 2026 主流模型。个人项目不需要 RunEvent（运行时事件流）和 column-level lineage——三实体足够。详见 §8 过度工程审查。

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

> 🎯 **2026 图形识别 DL 算法对标（v1.2.0 新增）**：3 类 DL 算法作为 `recognition_algorithm` 的 `dl_*` 选项 + `algorithm_variant` 的 DL 变体（MVP 不实施，schema 预留）：
> - **YOLOv8 目标检测**（[Trader Koo 2026-03](https://kooexperience.com/blog/posts/trader-koo.html)）：K 线图作图像输入框出形态+置信度，**准确率 92.6%** vs 规则引擎 68.3%；HuggingFace 预训练 [`foduucom/stockmarket-pattern-detection-yolov8`](https://huggingface.co/foduucom/stockmarket-pattern-detection-yolov8) 识别 6 类
> - **ViT-Tiny 视觉 Transformer**（[CS231n Stanford](https://cs231n.stanford.edu/2025/papers/text_file_840597081-LaTeXAuthor_Guidelines_for_CVPR_Proceedings__1_-2.pdf)）：切 patch+self-attention 捕获全局依赖
> - **CNN+TA-Lib 混合**：规则层 61 形态+DL 层联合，准确率 99.3%
>
> **个人项目适用性评估**：DL 图形识别需大量标注数据+GPU 训练+模型部署，对个人项目属过度工程（MVP 阶段）；MVP 用 `rule_based`/`template_match`（TA-Lib CDLPATTERN 61 种+经典图表规则法）；schema 预留 DL 字段，Phase 2+ 可评估 YOLOv8 预训练模型（即取即用免训练）。`subjectivity` 字段在 DL 场景标 low（算法客观，但训练数据偏差仍存）。

> 🧠 **"Simplicity Wins" 原则 + CNN+LSTM Hybrid + 反 Look-Ahead Bias（v1.7.0 新增，对标 [arXiv:2605.00875 Haggett 2026-04](https://arxiv.org/pdf/2605.00875.pdf) + [mental-momentum 2026-06-14](https://research.mental-momentum.ai/r/convolutional-neural-networks-chart-lbrhyr)）**：
> **① Simplicity Wins**（arXiv:2605.00875，Stevens Institute 8 组控制实验，BTC/ETH/S&P500 2018-2024）：**原始 K 线图 + 4 层基础 CNN AUC-ROC 0.892**，outperform 复杂编码（Gramian Angular Field）和大型预训练模型（ResNet18/EfficientNet-B0/ViT）。反直觉发现：① price-only 图表 > 含指标图表（指标是噪声非信号）；② 128×128 分辨率 > 224×224（金融图表信息密度低，低分辨率防过拟合）；③ ImageNet 迁移学习提升 4-16%。→ **Phase 2+ DL 起点应是 `dl_cnn` + 原始 K 线图 + 128×128，而非 YOLOv8/ViT**。
> **② CNN+LSTM Hybrid**（mental-momentum 2026-06）：**Hybrid 架构（CNN 空间特征+LSTM 时序记忆）一致优于独立模型**；raw pixel 输入 > 显式人工技术指标输入。→ `algorithm_variant: cnn_lstm_hybrid`，Phase 2+ 优先于此变体。
> **③ 反 Look-Ahead Bias**（mental-momentum 2026-06，**关键实现约束**）：图像生成 MUST 使用**严格后向归一化**（backward-looking normalization）——"never scales using future prediction data"；归一化窗口只含历史数据，禁止全样本 min/max 或未来均值标准化（否则模型"预测"只是记忆未来）。→ `dl_training_dataset` 字段 MUST 记录归一化策略（`backward_only`/`expanding_window`/`rolling_window`），禁止 `global_minmax`（含未来数据）。

**MVP 范围控制**（已按此施工）：图形形态几十种，不一次性建全——
- 从代码反查项目实际用到的形态（`src/zephyr/factor/technical_indicators/` + `src/zephyr/signal_ashare/` 打板链），只登记实际用到或明确规划的（落盘 15 条：candlestick 6 active + chart_pattern 4 candidate + trendline 1 candidate + support_resistance 3 active + structure 1 active）
- 符合"过度工程纠偏"原则——建库结构完整，内容按需填充
- MVP 算法用 rule_based/template_match（O6 裁剪：先做 candlestick_pattern + chart_pattern 2 类），chanlun/elliott_wave/fibonacci 3 类 schema 预留按需补充

## 7. P2 待施工两注册表

> ✅ **两表已全部施工**：field_dictionary 257 条/16 域（2026-08-14，f0ebfdd5dc，active）/ experiment 5 条（2026-08-13，4b92a41a01，draft）。ROOR 登记待补（§9.1）。本节保留 schema 定义与规则内容，施工过程叙述已折叠。

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
  sensitivity: str               # v1.1.0 补：PII/敏感字段标记（dbt 对标，已随施工落地）
  freshness: str                 # v1.1.0 补：更新频率（已随施工落地）
  notes: str                     # v1.1.0 补：caveats/gotchas（已随施工落地）
  steward: str
  status / version / created_at / updated_at
```

**范围裁定**（裁定 8）：仅管数据层字段（行情/因子/特征/输出的 type/unit/source/复权口径/PIT/quality_rules），**不合并** frontmatter_field_registry.yaml（文档元数据，职责分离）。对标 DAMA-DMBOK / dbt schema.yml。

**2026 dbt schema.yml 对标补充**（v1.1.0 新增）：
- 2026 主流 data dictionary 核心字段 = field_name/type/definition/source/owner/allowed_values/sensitivity/freshness/notes（[Basedash 2026-06](https://www.basedash.com/blog/what-is-a-data-dictionary-and-how-to-build-one-for-analytics) ｜ [OvalEdge 2026-02](https://www.ovaledge.com/blog/data-dictionary-best-practices)）——`sensitivity`/`freshness`/`notes` 三字段已补入 schema 并随施工落地
- dbt 命名规范（[dbt style guide 2026-08](https://docs.getdbt.com/best-practices/how-we-style/1-how-we-style-our-dbt-models)）：snake_case + business terminology + `<object>_id` PK + `is_`/`has_` boolean 前缀 + `_at` UTC timestamp + `_date` date + `_v1` versioning

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
  # 回测过拟合检测（v1.3.0）
  is_overfit: bool               # 综合判定（PBO>0.2 或 DSR p-value<0.05 → True）
  pbo_value: float               # CSCV 估计，null=0.5，<0.1 可信，>0.2 红旗（⚠️ PBO 零假设=0.5 非 1，v1.26.0 警示）
  dsr_value: float               # Deflated Sharpe Ratio（>1.0 显著）
  psr_value: float               # Probabilistic Sharpe Ratio（v1.6.0修正：AUC 0.81 最强单一诊断）
  n_trials: int                  # 参数搜索试验数（含相关试验用有效独立数 N_eff）
  min_trl_years: float           # v1.11.0：Minimum Track Record Length（Bailey&López de Prado 2014）
                                 # 公式 MBL=0.5×(Z_α×σ_ann/SR_ann)²；实盘 < min_trl_years → 继续 probation
  plateau_score: float           # v1.6.0：参数稳健性高原分数（选择原则非独立检测）
  adversarial_result: obj        # v1.6.0：对抗验证结果（{test_name, passed, kill_reason}列表）
  # 有效 trial 数鲁棒性带（v1.21.0）
  trial_correlated: bool         # trial 间相关时 MUST 跑 bootstrap_test_passed，裸 DSR 不可信
  effective_trial_count_band: obj # {estimators: {laplace, jaw, ar1, spectral, permutation}, robust_range, verdict}
  bootstrap_test_passed: bool    # White RC / Hansen SPA 联合重采样（trial_correlated=True 时 MUST）
  log_location: str
  artifact_path: str
  fallback_ref: str              # 实验追踪后端引用（v1.34.0：51 号裁定 mlflow 完全卸载，原 mlflow_run_id 改名）
  mace_env_ref: str              # v1.2.0：可选，MACE RL 环境引用
  status: enum                   # running/completed/failed/archived
  created_at: date
  completed_at: date
  owner: str
  parent_experiment_id: str      # 迭代链
  tags: list[str]
  # 回测数据偏差治理（v1.18.0，E14 审计）
  backtest_bias_checks: obj      # {survivorship, lookahead, stop_exit: passed/failed/unknown}
                                 # 未声明=未做偏差治理；MVP 用 AKShare 日线=unknown，实盘前须升级商业源
  # 归因分析（v1.18.0）：归因执行逻辑归 54 号，本字段仅登记结果（§4.4 跨文档边界）
  attribution_result: obj        # {method: brinson/factor_based/none, allocation_effect, selection_effect,
                                 #  interaction_effect, factor_contributions, alpha}
                                 # VIF screening（v1.19.0）：VIF>10 移除或合并正交，VIF<5 安全
  # LLM 前瞻偏差治理（v1.19.0，E15 审计）：仅 LLM-driven 实验声明
  llm_lookahead_check_result: obj # {applicable, masking_level, alpha_decay, test_method}
  # LLM 前瞻污染检测（v1.22.0，E18 审计）：E15 数据侧防御 + E18 模型侧诊断双轨互补
  lap_check_result: obj          # {applicable, lap_value, interaction_beta3, contamination, suppression_method}
  # 预注册协议（v1.25.0）：MVP 所有回测 MUST pre_registered=true
  pre_registered: bool           # 实验前声明假设/指标/样本量/止损规则，防事后合理化
  cost_vetoed: bool              # 成本否决：OOS 收益含成本≤0=否决（§4.13 G1）
  ic_oos_gap: float              # IC-OOS 脱钩度（<0.3=脱钩告警，§4.13 G1 warning）
  # 上线裁决三值结果（v1.28.0，§4.13 三值裁决）
  viability_verdict: enum        # supported/refuted/inconclusive
                                 # "统计不显著"≠"证伪"；INCONCLUSIVE=样本不足继续积累；REFUTED=真无 edge 放弃
  # 过拟合实证模式分类（v1.28.0，§4.13 G2 增强）
  overfit_pattern: enum          # none/walk_forward_divergence/regime_flip/parameter_cliff/indicator_stacking/survivorship
                                 # none=未检测到过拟合；walk_forward_divergence=IS 优化但 OOS 变差（PF ratio>1.5）
                                 # regime_flip=某 regime 有效另一 regime 失效（需 regime gating）
                                 # parameter_cliff=参数微偏性能骤降（需取高原参数）；indicator_stacking=堆叠相关指标（需去相关）
                                 # survivorship=仅存活标的回测（需 PIT universe）
                                 # 不同模式修复策略不同——dibi8 2026-05: 模式分类指导"怎么修"而非仅"是否过拟合"
                                 # MVP 阶段 PF ratio 自动可算→填 none/walk_forward_divergence，Phase 1.5+ 配合 PBO/DSR 精细分类
  # 路径依赖回撤度量（v1.30.0）
  ulcer_index: float               # drawdown 序列二次均值 √(ΣD²/N)；区分"回撤2周恢复"vs"18个月恢复"
  calmar_ratio: float              # 年化收益/|max_drawdown|；>1.0 可接受/>3.0 优秀（§4.13 G1 补充信号）
  # LLM 时序泄漏测量（v1.31.0，E18 扩展审计）：从"检测"到"测量"
  temporal_leakage_measurement: obj  # {method: matched_control/boundary_detection/none, leakage_score, reference_model}
  # 参数稳定性区域（v1.32.0，§4.13 G2 扩展）：选高原不选尖峰
  parameter_stability_region: obj    # {plateau_identified, cliff_detected, stability_score, selection_method}
                                     # cliff_detected=true=warning；paper/live 阶段 single_optimum=warning
```

**设计要点**：
- 两层分离：注册表只管元信息（静态目录），日志详情进 DB/文件（`log_location` 指向详情）
- `parent_experiment_id` 支持迭代链（参数优化 A→B→C）
- 对标 MLflow Experiment Registry / Comet.ml
- **施工时机**（v1.34.0）：51 号已裁定"mlflow 完全卸载"，替代=FallbackBackend 本地 JSON + Panel 实验历史 Tab。experiment_registry 定位=实验元数据唯一登记处，与 Panel 成对（注册表管 SSoT，Panel 管展示）。原 `mlflow_run_id` 已改为 `fallback_ref`/`panel_experiment_ref`。

> 🎯 **回测过拟合检测六方法**（PBO+DSR+PSR+MinBTL+MTC+CPCV）：
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
> **PBO 关键洞察**（Soloviov 2026-07）：PBO 参考值=**0.5** 非 0——PBO≈0.5=完全过拟合（硬币翻转），PBO≈0=可信。控制实验：零 edge PBO=0.476，植入 edge（Sharpe 2.38）PBO=0.001。
>
> **PBO 分层解读**（v1.5.0，对 §4.12 decay_cause 诊断有直接影响：PBO>0.5 → decay_cause=overfitting → 直接退役）：
>
> | PBO 范围 | 解读 | 决策 | decay_cause 映射 |
> |---|---|---|---|
> | **< 0.1** | 强信号 | ✅ 可信 | — |
> | **0.1-0.3** | 弱信号 | ✅ 可部署，注意监控 | — |
> | **0.3-0.5** | 临界 | ⚠️ 谨慎部署 | regime |
> | **≈ 0.5** | 随机 | ❌ 阻断 | overfitting |
> | **> 0.5** | 反向 perverse | ❌ 阻断，walk away | overfitting（严重） |
>
> **n_trials 字段**：DSR/PBO 计算必需试验数 N。相关参数组合用有效独立数 N_eff。PBO 需完整 returns 矩阵，DSR 只需最终选中策略收益 + N_eff。

> 🧪 **MTC 第 5 方法族**（v1.12.0）：PBO/DSR/PSR/MinBTL 回答"单次搜索是否过拟合"，MTC 回答"N 个策略同时检验时族错误率控制下哪些仍显著"——测 100 个纯噪声策略按 p<0.05 仍有 ~5 个"显著"。
>
> | 子方法 | 机制 | 个人项目适用性 |
> |---|---|---|
> | **White's RC** | Bootstrap 重采样，需预指定基准 | ✅ 有明确基准时 |
> | **Hansen SPA** | White's RC 改进版 | ✅ White's RC 升级 |
> | **Romano-Wolf** | 控制 FWER，比 Bonferroni 强 | ✅ **推荐** |
> | **MCS** | 返回"统计不可区分的最佳模型集合" | ✅ **推荐**（无基准时） |
> | **BH-FDR** | 控制 FDR 而非 FWER | ✅ 多策略筛选 |
>
> **关键决策**：SPA 与 Romano-Wolf 互斥选其一（推荐 Romano-Wolf）；MCS"输出集合而非赢家"——若 5 策略统计不可区分，选最稳健/最可解释/最低容量的（非 Sharpe 最高）。DSR 校正选择偏差，MTC 校正族错误率，两者正交。MVP 阶段策略数少（<10）可选；Phase 1.5+ 多策略筛选 MUST 跑 Romano-Wolf 或 MCS。schema 预留 `mtc_method`/`mtc_pvalue`/`mtc_survived`。`is_overfit` = (pbo>0.2) ∨ (dsr_pvalue<0.05) ∨ (mtc_survived==False)。

> 🔄 **CPCV 第 6 方法**（v1.16.0）：walk-forward 给**一条** OOS equity curve，CPCV 给 **C(N,k) 条**——输出 OOS Sharpe 分布（mean ± std），分布方差才是真实信号。三步：组合切分 + purge（防标签重叠泄漏）+ embargo（防自相关）。
>
> | 维度 | walk-forward | CPCV |
> |---|---|---|
> | OOS 曲线数 | 1 条 | C(N,k) 条（N=10,k=2→45） |
> | 输出 | 单个 Sharpe/MaxDD | Sharpe 分布 mean ± std |
> | 切法敏感性 | 高 | 低（所有切法平均） |
>
> **关键决策**：CPCV 分布中若有负 Sharpe 曲线，即使 mean 正也不可信。t-stat 需接近 3.0（非 1.96）才能声称真实 edge。IS 阶段优先稳定参数区域（plateaus，`Ω_stable={θ|SR(θ)≥0.9×SR_opt}`）。WFA 配 majority-pass + catastrophic-veto 双门禁。MVP 用 PurgedKFold（简化版），Phase 1.5+ 升级完整 CPCV。schema 预留 `cpcv_*` 五字段。catastrophic-veto：cpcv_worst_max_dd>0.15=一票否决（§4.13 G2）。

> 📏 **MinBTL/MinTRL 第 4 指标**（v1.11.0）：回答"需多少年数据才能信任此 Sharpe"。公式 `MBL=(1/2)×(Z_α×σ_ann/SR_ann)²`。
>
> | 观测 Sharpe | IID 95% 所需年数 | IID 99% 所需年数 | **现实所需年数**（含自相关/重尾膨胀） | 个人项目解读 |
> |---|---|---|---|---|
> | 0.5 | ~16 年 | ~28 年 | **25-40+ 年**（不实用） | Sharpe 0.5 策略基本无法用统计验证，MUST 靠经济逻辑 |
> | 1.0 | ~4 年 | ~7 年 | **5-10 年** | MVP 目标 Sharpe，需 5+ 年实盘才统计可信 |
> | 1.5 | ~1.8 年 | ~3.1 年 | **3-5 年** | 高 Sharpe，2-3 年 probation 后可初步确认 |
> | 2.0 | ~1 年 | ~1.7 年 | **1.5-3 年** | 极高 Sharpe，警惕过拟合（DSR/PBO 复检） |
> | 3.0 | ~5 月 | ~9 月 | — | HFT 级，样本量不是瓶颈但生存偏差是 |
>
> **标准误公式**：`SE(SR) ≈ 1/√T`（T=独立观测数），T=250（1年日数据）时 SE≈0.063——观测 Sharpe 0.8 的 95% CI 为 [0.68, 0.92]，精度不足以做配置决策。**自相关膨胀**（Lo 2002）：日收益序列相关使 SE 膨胀 1.5-3x。**重尾膨胀**：A 股 γ₄>6 尖峰重尾使 Sharpe 估计器更嘈杂，CI 更宽。
> **与 §4.13 PROMOTE_ENTRY 的联动**：Gate 1 检查 `oos_period_months >= 3` 之外 MUST 交叉校验 min_trl_years——Sharpe=1.0 策略 3 个月 OOS 通过后上线，但 MinBTL=5-10 年意味着 3 个月实盘数据**完全不足以确认** edge 真实。Full 阶段应持续 `min_trl_years` 年才从 "probation" 升级为 "confirmed"——`lifecycle_status` 从 `live`(probation) → `monitoring`(confirmed) 的转换条件之一 = 实盘 track record ≥ `min_trl_years`。
> **与 §4.8 DECAY_SCAN 的联动**：衰减检测的 baseline_sharpe 须基于 ≥ MinBTL 的样本建立——短样本 baseline 本身可能是噪声峰值。track record < MinBTL 时 monthly 扫描统计意义有限，应更关注 regime 匹配和经济逻辑。
> **个人项目 MVP 决策**：多数策略 Sharpe 0.5-1.0 → MinBTL 5-40 年远超实盘周期，**策略上线后几乎永远处于 probation 态**。实务对策：
> - ① 经济逻辑优先（§4.8 阶段1 的"信号发现 vs 信号幻觉"经济理性校验比统计检验更重要）
> - ② 多策略组合分散（不依赖单一策略统计确认）
> - ③ 跨 regime 验证替代时间长度（3-5 年覆盖牛/熊/震荡 3 regime 比单 regime 10 年更有信息量）
> - ④ `min_trl_years` 填计算值，`lifecycle_status` 须 track record 达标才升 `monitoring`，否则保持 `live`(probation) + 加密 `decay_scan_frequency`(weekly)

> 🔍 **回测过拟合 7 症状预检清单**（v1.10.0 新增，对标 [tradingnote.co 2026-06-23](https://tradingnote.co/es/blog/overfitting-trading-que-es-como-detectarlo) + [quant67.com 2026-05-01 回测陷阱](https://quant67.com/post/quant/20-backtest-pitfalls/20-backtest-pitfalls.html)）：在跑正式 PBO/DSR/PSR/MinBTL 前先看 7 个经验症状——若命中 ≥4 个，几乎必然过拟合，无需跑统计检验即可阻断部署：
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
> **与正式检验的关系**：7 症状是"快速预筛"（秒级判断），PBO/DSR/PSR/MinBTL 是"正式诊断"（分钟级计算）。预筛命中≥4 → 直接走 §4.10 RETIRE_ENTRY 或 §4.12 Level 5；命中≤1 → 跑正式方法确认。`is_overfit` 字段判定可先看 7 症状命中数再结合 PBO/DSR 正式值综合判定。
>
> **个人项目 MVP 决策**：MVP 阶段参数搜索少（<50 试验），PBO/DSR 可选（n_trials < 10 时统计意义有限）。Phase 1.5+ 参数搜索扩展后 MUST 跑 PBO + DSR 双门禁（PBO > 0.15 ∨ DSR < 1.0 → 阻断部署）。`is_overfit` 综合判定 = (pbo_value > 0.2) ∨ (dsr_pvalue < 0.05)；MinBTL 不影响 `is_overfit`（衡量样本充分性非过拟合），但影响 `lifecycle_status` 升级。

> 🎯 **PSR vs DSR 排序能力修正 + Plateau-Robustness 选择原则（v1.6.0 新增，对标 [Soloviov 2026-06 Plateau-Robustness 控制实验](https://plateau.marketmaker.cc/) + [GitHub suenot/plateau-robustness](https://github.com/suenot/plateau-robustness)）**：PSR 标为"DSR 前身"可能暗示 DSR 严格优于 PSR，但 Soloviov 2026-06 在 9000 次控制实验（已知 population Sharpe 曲面 ground truth）中得出**反直觉结论**：
>
> | 诊断方法 | AUC（检测无边缘策略） | 角色 | 关键发现 |
> |---|---|---|---|
> | **PSR against zero** | **0.81**（最强单一诊断） | 显著性检验 | **信号载体**——significance test, not multiplicity deflation, carries the signal |
> | DSR | 0.79 | 多重检验校正 | 提供**校准**（calibration），非**排序力**（ranking power）——trials 相关如 grid scan 时贡献更小 |
> | PBO | — | 选择过程泛化性 | CSCV 对称交叉验证，回答不同问题 |
> | Plateau 几何指标（robustness score/plateau width） | 弱（standalone） | **选择原则**非独立检测 | fixed threshold 未校准，standalone 诊断不可靠 |
>
> **核心洞察**：
> - ① PSR 排序/检测能力**不弱于** DSR（AUC 0.81 > 0.79），DSR 的价值在多重检验校正而非提升检测力——MVP 阶段若只跑一个统计检验，PSR（计算更简单，无需 N_eff 估计）是合理起点
> - ② **plateau heuristic（"prefer plateaus over peaks"）作为选择原则有效**——选 smoothed surrogate 的 argmax 而非 raw argmax，OOS Sharpe 平均提升 **0.12（1D）/ 0.31（2D）**，随参数维度单调递增
> - ③ 但 plateau 几何指标**作为独立过拟合检测不可靠**——结论：**"prefer plateaus" 应与统计显著性检验并用，而非替代**（Soloviov: "should be used alongside, not instead of, statistical significance controls"）
> **对 §4.12 ADAPT_STRATEGY Step 3 的影响**：Step 3b 已用 `find_plateau` + `centroid`（取稳定区域中心非最高点）✅ 正确；但 plateau 检测通过**不能**替代 Step 3c DSR 校正 + Step 4 OOS 验证，三者互补——plateau 通过是必要非充分条件。

> **honest-backtest 7 层验证框架（v1.6.0 新增，对标 [krivonosoff161/honest-backtest 2026-06](https://github.com/krivonosoff161/honest-backtest)）**：7 层验证架构，每层捕获不同谎言，与 experiment_registry 验证字段映射：
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
> **Layer 7 对抗验证**是核心创新——"the AI step that tries to kill your finding instead of blessing it"。对 100% AI 开发的个人项目尤为契合：AI agent 在回测通过后**主动构造证伪场景**（极端 regime/参数微扰/替代 universe/成本上调 2x/随机 label 置换检验），策略在这些场景下仍存活才确认 edge 真实。与 §4.8 阶段4 Validation 的"试图证伪（非证明有效）"原则一致。schema 新增 `adversarial_result: obj`（{test_name, passed, kill_reason}列表）+ `plateau_score: float`。

> 🔍 **2026 MLflow 生态现状（v1.1.0 新增，v1.2.0 更新至 3.15.1）**：2026 年 MLflow 是实验追踪 de facto 标准（[ZenML 2026-02](https://www.zenml.io/blog/comet-vs-mlflow)）；**Neptune.ai 已被 OpenAI 收购并将关停公共服务**（[ZenML 2025-12 Neptune Alternatives](https://www.zenml.io/blog/neptune-ai-alternatives)）。MLflow 3.15.0（2026-07-31）重大特性：MCP Registry（语义版本配置+可提升别名+自动发现工具）、MLflow Assistant 多 LLM provider、Sharable table views、Proxy-less artifact upload。
>
> ⚠️ **E1 状态更新（v1.34.0，已关闭）**：用户已裁定"**mlflow 完全卸载**"（51 号 §四.1，用户选择）——原"保留 MLflow"讨论方向**与用户已裁定冲突，予以撤回**。experiment_registry 施工前提=51 号 A/B/C 工作流完成 + FallbackBackend（本地 JSON）+ Panel 实验历史 Tab 落地；schema 的 `mlflow_run_id` 已改 `fallback_ref`/`panel_experiment_ref`（见 §7.2 schema）。本注册表定位：MLflow 退役后实验元数据的**唯一登记处**，与 Panel 可视化成对（注册表管元数据 SSoT，Panel 管展示）。

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
| O3 | experiment_registry 能否暂缓用 MLflow 替代 | ✅ **已收敛（v1.34.0 更新）** | 原"待定 E1"已关闭：51 号用户已裁定"mlflow 完全卸载"（v1.2.7 确认方向已定、施工未启动）。experiment_registry 不暂缓、不退化为 MLflow 索引层——MLflow 退役后它是实验元数据唯一登记处，施工前提=51 号 A/B/C 工作流完成 |
| O4 | YAML vs DB（现阶段 YAML 是否合理） | ✅ **YAML 合理** | 因子<500/实验<5000 远未触发迁移阈值。Feast/MLflow 双轨先例（YAML 定义+运行时 DB）。SQLite 看似省事但失去 git diff/version/PR review 治理能力，个人项目 YAML + git 更优 |
| O5 | data_asset 三实体（sources/datasets/jobs）是否过重 | ✅ **不过度** | 对齐 OpenLineage 2026 主流三实体。个人项目**不需要** RunEvent/column-level lineage（企业级需求），三实体足够且已部分落盘（dataflow_graph_registry 已有 datasets+jobs，仅新增 sources 段） |
| O6 | chart_pattern 8 大类是否过多 | ⚠️ **MVP 裁剪** | 8 大类覆盖图形技术分析全谱系（TA-Lib 61 K线+缠论+波浪+Edwards&Magee）合理，但 §6.2.4 已定"MVP 只登记代码实际用到或明确规划的"。P1-B 先做 candlestick_pattern（low 主观性）+ chart_pattern（medium）2 类，chanlun/elliott_wave 等按代码反查按需补 |
| O7 | risk_limit 9 种限额是否过多 | ✅ **不过度** | project_memory 已明确"Kill Switch + 四级回撤为必须保留的风险红线；VaR 5级 + 7黑天鹅降级为监控层"。9 类中 position/concentration/drawdown/kill_switch 是必须红线，var/es/leverage/turnover/firm_risk 是监控层（先全建+全log，实盘6-12月后裁剪未触发项） |
| O8 | variant 机制（单向 variant_of）是否过度 | ✅ **不过度** | 单向引用避免双向同步漂移，查询简单（WHERE variant_of=X）。打板连板/趋势 2 variant 是实际需求 |
| O9 | 性能指标字段（运行时可空）是否过度 | ✅ **不过度** | 裁定 S5 已定：现在就列运行时可空，未来进 DB 时序存储。YAML 阶段 null 不占空间 |
| O10 | §11 YAML→DB 迁移路径是否过早规划 | ✅ **不过度** | 迁移路径是"预留"非"立即执行"。schema 按 DB 表设计（id/created_at/updated_at/version/status）成本极低，未来迁移省事。阈值（因子>500/实验>5000）明确，个人项目可能永不触发 |
| O11 | factor_class 10 类是否过多 | ✅ **不过度** | Barra 6 类是业界标准（MSCI Barra 模型），A股特色 4 类（event/intraday/technical/sentiment）是 A股必要扩展。qlib Alpha158 用 4 大类（趋势/均值回归/成交量/波动）但那是指标级分类非因子级 |
| O12 | strategy lifecycle_status 7 态是否过多 | ✅ **不过度** | candidate/backtest/sim/paper/live/monitoring/retired 对齐 2026 Strategy Lifecycle Management 主流（Idea→Design→Backtest→Validation→Deployment→Monitoring→Optimization→Retirement，[DeepTradeX 2026](https://deeptradex.zendesk.com/hc/en-us/articles/16820285969295-Strategy-Lifecycle-Management-Great-Trading-Strategies-Are-Managed-Not-Just-Built)）。68% 策略 18-24月需修改/退役，lifecycle 管理必要 |

**过度工程审查总结论**：12 注册表 + 通用 schema 设计**整体不过度**，符合个人项目"建库结构完整，内容按需填充"原则。唯一需关注：(1) chart_pattern MVP 裁剪到 2-3 类（O6）；(2) experiment_registry 待 51 号 MLflow 决策后定形态（O3/E1，v1.34.0 已关闭——mlflow 完全卸载）。其余 10 项均合理保留。

## 9. 治理同步与验收

### 9.1 registry_of_registries.yaml 登记

✅ **已登记 7/12**（2026-08-12 v1.33.0 闭环 + 2026-08-13 chart_pattern 补登）：REG-UNI-001（5，active）/ REG-BMK-001（4，active）/ REG-CST-001（3，active）/ REG-FCT-001（111，draft）/ REG-STR-001（59，draft）/ REG-RLM-001（42，draft）/ REG-PAT-001（15，draft）；ROOR summary 同步 total_registries 52→58，tier_2_runtime 12→18。
⚠️ **待补登记 5 表 + 2 处同步**（2026-08-14 核验）：REG-IND-001（40 条）/ REG-EXA-001（6 条）/ REG-DATAFLOW-001（166 条）/ REG-FLD-001（257 条）/ REG-EXP-001（5 条）已落盘未登记；ROOR tier_2 段注释（仍写"indicator/execution_algo/data_asset 待施工；P2 待施工"）与 REG-RLM-001 entry_count（42 vs 实际 62）待同步。另注意 ROOR 已有 REG-TECHNICAL-INDICATOR-001（22 条种子，auto 派生）与 REG-IND-001（40 条）同指 technical_indicator_registry.yaml，登记时须消解 id 重叠。
⚠️ 历史教训：v1.0.0 §9.1 原声称"P0 三件套已登记于 ROOR:549-577"，经 2026-08-12 全量 grep 验证**实际从未登记**——声称完成但未做是典型的"治理假闭环"，v1.33.0 实际补齐。声称完成前 MUST 全量 grep 验证。

### 9.2 AGENTS.md 显化

✅ **已完成**：AGENTS.md RULE-REGISTRY 段"业务资产 registry 速查"覆盖 12 表（2026-08-12 补 P0 三件套 + factor/strategy/risk_limit 6 表，2026-08-13/14 补齐其余 6 表，当前全部标 ✅）。
⚠️ 历史教训：v1.0.0 §9.2 原声称"AGENTS.md:150-153 新增业务资产速查"，实际 150-153 行是 RULE-SSOT 段开头，从未有此内容——v1.33.0 实际补齐。

### 9.3 ARCH 登记条目

[architecture_issue_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) `#ARCH-BREG-001`（status: decided）记录裁定与施工进度。P1/P2 每完成一表须更新其 fix_phase 字段。

### 9.4 验收标准

- [x] P0 三件套 YAML 落盘 catalogs/（2026-08-10）
- [x] registry_of_registries.yaml 登记 7/12（2026-08-12/13，原 v1.0.0 勾选系假闭环 v1.33.0 重做；**IND/EXA/DATAFLOW/FLD/EXP 5 表登记 + REG-RLM-001 entry_count 42→62 同步待补**）
- [x] AGENTS.md 显化 12 表（2026-08-12 起分批补齐，原 v1.0.0 勾选系假闭环 v1.33.0 重做）
- [x] ARCH-BREG-001 登记（2026-08-10，status: decided）
- [x] v1.1.0 cost_model 印花税/过户费费率校准（同步 catalogs/cost_model_registry.yaml）
- [x] v1.33.0 P0 三件套 YAML 硬错误修复：related_arch 旧引用→'#ARCH-BREG-001'；universe_registry 补 v1.24.0 生存偏差三字段（schema+5 条 entry），UNI-INDEX-001/002 成分股文件未落盘诚实标注 pit=false/survivorship_free=false
- [x] **13 算法体系 + E1-E20 审计矩阵 + 回测过拟合六方法全部建成**（v1.2.0-v1.32.0：§4.5 CONSTRUCT_REGISTRY 8 步 / §4.6 FK 矩阵 32 条 / §4.7 AUDIT_REGISTRY E1-E20 / §4.8 生命周期+DECAY_SCAN(_MULTI) / §4.9 EVOLVE_ENTRY / §4.10 RETIRE_ENTRY / §4.11 EVOLVE_SCHEMA / §4.12 ADAPT_STRATEGY / §4.13 PROMOTE_ENTRY G1-G9+三值裁决+渐进式部署 / §4.14 ROLLBACK_ENTRY / §4.15 DEPENDENCY_RESOLVE / §4.16 MIGRATE_REGISTRY R1-R7 / §4.18 DIFF_ENTRY；§7.2 PBO/DSR/PSR/MinBTL/MTC/CPCV；逐版本明细见 §13 修订记录）
- [x] P1 七注册表落盘（2026-08-13：factor 111 / strategy 59 / technical_indicator 40 / execution_algo 6 / risk_limit 62 / data_asset 166 / chart_pattern 15；§4.20 监管字段 + §4.23③ 价格笼子三字段 + §4.24⑤ license_type 标注已纳入）
- [x] P2 两注册表落盘（field_dictionary 257 条/16 域 2026-08-14；experiment 5 条 2026-08-13）
- [~] **ruling_registry.yaml 登记 data_asset 改名——部分完成但有硬问题（v1.33.0 起）**：裁定#223（2026-08-10）已登记但**方向写反**（data_asset→dataflow_graph，与 S6 裁定相反），且声称"62 号 §9.4 D1 已标记完成"实际未标记（三方状态漂移）。物理层 data_asset_registry.yaml 已落盘（2026-08-13），旧 dataflow_graph_registry.yaml 并存。转待定问题 K1，需用户裁定后修正 ruling_registry + 清理并存文件
- [ ] audit_registration.py 扫描通过，无 broken/pending（覆盖 §4.7 E1-E20 全检查，含 E14 回测数据偏差 c/d 维度 + E15 LLM 前瞻+A股 Tradability Mask + E16 因子冗余+归因稳定性 DASH + E17 因果验证+设定结构 + E18 LAP+Temporal Leakage + E19 LIB + E20 RMT 去噪；G2 v1.32.0 扩展 parameter_stability_region cliff 检查）
- [ ] capability_lookup.py 扩展扫描范围覆盖 12 业务注册表
- [ ] session_log_schema.yaml 加"必读注册表"检查项
- [ ] 16 号文档 §6 清单迁注册表并降级为 why 层（注意第5类 reversal 非 structure；清单在 §6.1-6.5 非 §2，v1.34.0 修正）
- [ ] entry 后续变更走 §4.9 EVOLVE_ENTRY，衰减适应走 §4.12 ADAPT_STRATEGY，退役走 §4.10 RETIRE_ENTRY，schema 演进走 §4.11 EVOLVE_SCHEMA，上线晋升走 §4.13 PROMOTE_ENTRY，回滚走 §4.14 ROLLBACK_ENTRY，依赖解析走 §4.15 DEPENDENCY_RESOLVE，YAML→DB 迁移走 §4.16 MIGRATE_REGISTRY，版本对比/兼容性判定走 §4.18 DIFF_ENTRY，上线后渐进式部署走 §4.13 Shadow→Canary→Full（长期有效规则）

## 10. 数据来源映射表

| 注册表 | 文档来源 | 代码来源 | 现有注册表/数据 |
|---|---|---|---|
| factor_registry | 15/25 号 | src/zephyr/factor/（6 .py + 子目录，v1.1.0修正：原ashare/15子目录不存在） | dataflow DS-015+（总 76 条） |
| strategy_registry | 20/24/25/26/27/22 号 | src/zephyr/governance/strategies/ | — |
| technical_indicator_registry | 16 号 §6.1-6.5（v1.34.0 修正，清单在 §6 非 §2） | src/zephyr/factor/technical_indicators/（6 .py，第5类reversal非structure） | — |
| universe_registry | 24/25/26 号 | src/zephyr/signal_ashare/ + ex_core/ | — |
| benchmark_registry | 25/52 号 | src/zephyr/data/implementations/akshare_provider.py | — |
| cost_model_registry | 62 号 §5.3（v1.34.0 修正：原"52 号 §G1"悬空，52 号重建版无 §G1）, 40 号 | src/zephyr/backtest/core/engine_base.py | — |
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

> 💡 **因子时序存储用窄表格式（v1.6.0 新增，对标 [DolphinDB 2026 金融数据存储最佳实践](https://docs.dolphindb.com/en/2.00.16/Tutorials/financial_data_storage.html)）**：factor_registry 迁移 DB 后，因子**值时序数据**（非 registry 元数据）推荐用**窄表**（narrow format：`timestamp, security_id, factor_name, factor_value` 四列）而非宽表：
> - 窄表优势：① 退役因子只删行不删列（DDL 无锁）；② 新增因子只插行不改表结构；③ 按因子名更新只改相关行；④ `PIVOT BY` 转 panel 格式做多因子查询
> - **注意**：此仅适用于因子**值时序存储**（IC 历史/每日因子值），registry 元数据仍用 §4 原则2 的标准 entry_schema 表结构
> - 分区策略：日线因子按 `year + factor_name` 分区，分钟级按 `month + factor_name` 或 `day + factor_name`；个人项目 PG 阶段可用 `PARTITION BY LIST (factor_name) + date_trunc('year', trade_date)` 模拟

**对标**：Feast（YAML 定义 + SQLRegistry 运行时）/ MLflow（代码配置 + DB backend）

> 🎯 **2026 YAML→DB 混合模式共识（v1.2.0 新增）**：2026 业界已形成 **"最小引导 YAML + DB 存储运行时配置"** 混合模式共识——Feast Feature View Versioning（2026-03-31）即典型：YAML 定义 FeatureView schema（手写真源入 git），`feast apply` 时自动写入 SQL Registry（运行时配置入 DB），版本快照自动追踪。MLflow 3.15 同理：代码配置 + DB backend。
>
> **对本项目 12 注册表的启示**：
> - **现阶段（YAML 阶段）**：12 注册表全部 YAML 真源入 git，schema 按 DB 表设计预留迁移；git diff/history 天然提供版本追踪（替代 Feast 自动快照），PR review 提供治理（替代 DB ACL）
> - **迁移触发后**：结构化元数据（编号/状态/关系/variant_of）仍 YAML 入 git（SSoT 真源）；大规模时序数据进 ClickHouse/PG 不入 git
> - **版本管理演进路径**：YAML 阶段 git diff → DB 阶段 `version` 字段 + `version_pin` 回滚（Feast `@v<N>` 模式），factor/strategy schema 已预留（§6.1.1/§6.1.2）
>
> **个人项目判断**（O4/O10 过度工程审查）：因子<500/实验<5000 远未触发迁移阈值，YAML + git 是当前最优解。SQLite 看似省事但失去 git diff/version/PR review 治理能力（裁定 3 已定）。schema 按 DB 表设计的成本极低，未来迁移省事，不算过早规划。

> 🔧 **迁移施工算法**（v1.11.0 新增）：本节描述了迁移的"触发条件 + 混合模式 + 窄表存储"，但迁移施工步骤见 **§4.16 MIGRATE_REGISTRY 算法**（R1-R7 七阶段渐进式迁移 + R4/R7 双 gate），确保零数据丢失 + 可回滚。迁移触发时按 §4.15 construct_order 的**逆序**逐表迁移（experiment 先迁，universe 最后迁），被依赖方后迁避免 FK 指向未迁移表的中间态。

## 12. 下一步行动

> ✅ **12 注册表施工全部完成**（2026-08-13/14 落盘核验，条目数+commit 见 §3 总览）。以下仅余治理收尾与待定项。

### P1-A（被测对象三件套，策略开发核心）
- ✅ factor 111 / strategy 59 / technical_indicator 40 已落盘（ac75684951 / eea122f432）
- 剩余：strategy YAML K2 修复核验（baseline_trade_frequency/decay_cause/decay_scan_frequency 三字段 + distilled_to_code 与 origin=human 语义一致性 + momentum_trend 桶 33 条课程规则条目标记区分，见 §14 K2）；16 号 §6 清单迁注册表并降级 why 层（§9.4）

### P1-B（交易/风控/数据/图形）
- ✅ execution_algo 6 / risk_limit 62 / data_asset 166 / chart_pattern 15 已落盘（c7701fcde6 / c6908d4678 / 206f48586f）
- 剩余：ROOR 补登记 REG-IND-001/REG-EXA-001/REG-DATAFLOW-001 + REG-RLM-001 entry_count 同步（§9.1）；K1 裁定#223 方向反转待用户裁定（§14 K1）；旧 dataflow_graph_registry.yaml 与 data_asset_registry.yaml 并存待 K1 裁定后清理

### P2（数据治理 + 实验）
- ✅ field_dictionary 257 / experiment 5 已落盘（f0ebfdd5dc / 4b92a41a01）
- 剩余：ROOR 补登记 REG-FLD-001/REG-EXP-001（§9.1）；audit_registration.py 全量扫描（E1-E20）+ capability_lookup.py 扩展 + session_log_schema.yaml "必读注册表"检查项（§9.4）

## 13. 修订记录

| 版本 | 日期 | 修订内容 | 审查依据 |
|---|---|---|---|
| v1.36.0 | 2026-08-14 | **体系 14→18 表扩展（机构五层栈+量化社区数据谱系对标）**：① 新增 4 表——model_registry（REG-ML-001，8 条，机构五层栈第四层 Model 补全，与 experiment 过程表正交管"产物"）+ event_calendar_registry（REG-EVT-001，12 事件类型全量 PIT 规则，event_driven 前提）+ macro_indicator_registry（REG-MAC-001，中美 15 指标发布纪律/修订政策）+ portfolio_model_registry（REG-PFM-001，8 组合模型，MVP 纪律=OOS 跑不赢 1/N 不得晋升 DeMiguel 2009）；② data_asset v1.2.0 对标聚宽 JQData/quant666 全量补登 22 数据集+6 管道（DS-081~085 市场约束/DS-086~090 基本面/DS-091~097 事件/DS-098~100 资金/DS-101 中国宏观/DS-102 申万行业，171→199）；③ 不建裁定——signal_registry（与 factor/strategy 夹逼重叠）/regime_registry（regime_detector 代码已实现+REG-SM-001 治理层覆盖）/alt_data/broker/attribution（个人项目过度工程）；④ ROOR 登记 4 表（total_registries 65→69，业务注册表 979 条） | 全网搜索 2026-08-14 机构实践（Two Sigma/D.E. Shaw/Man AHL/AQR 五层栈 + Benzinga Events Calendar API 2026-07 + finance-query Event Calendar 2026-05）+ 社区谱系（聚宽 JQData/quant666 数据大盘/vn.py/AKShare） |
| v1.35.1 | 2026-08-15 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-03）——10 处 >300 字纯散文段要点化/表格化（§4 原则9/§4.4 结构说明/§4.17 对标/§4.19 总结/§4.20 适用性/§5.3 佣金口径/§6.1.3 5大类/§6.2.1 RL 远期/§6.2.2 消耗追踪/§6.2.4 DL 对标+MVP 范围/§11 窄表），PURE-ASSERTION 当前态改写 2 处；零信息丢失 | 第二轮压缩循环复扫 |
| v1.35.0 | 2026-08-14 | **体系 12→14 表扩展（图形形态循环审查裁定）**：① 新增 2 表——seat_registry（REG-SEAT-001，15 席位，与图形形态表正交管"谁在买"）+ regime_cycle_registry（REG-CYCLE-001，12 周期，与 regime/emotion_cycle 正交管"时间窗口"）；② 前提数据补登——data_asset 新增 DS-080 market_data.lhb_detail（龙虎榜，AKShare stock_lhb_detail_em）+ JOB-076 ingest.akshare_lhb（15+76+75→15+80+76=171）；③ 消费模块登记候选库 CAND-SEAT-001（P1）/CAND-CYCLE-001（P2）；④ §3 总览 14 行全量刷新（IND 40→41 Ichimoku 补登 / PAT 15→254 十五轮 SOTA 扩充收敛关闭 / DATAFLOW 166→171）；⑤ ROOR tier_2 登记 SEAT/CYCLE（total_registries 63→65）+ AGENTS.md 速查 14 表显化 | 2026-08-14 图形形态循环审查会话裁定（Gann 时间周期/周年日+龙虎榜席位形态新建表） |
| v1.34.3 | 2026-08-14 | 压缩精简：已施工内容折叠，零信息丢失审查通过（AI-DOCS-001） | 12 注册表全部落盘核验（条目数+commit 见 §3）；§4.5/E1-E20/schema/FK/拓扑序/编号规则完整保留；施工过程叙述与研究对标散文折叠 |
| v1.34.2 | 2026-08-12 | 作战地图环节映射补强——锚定 BM-RES-01-D | §4.18 末尾补映射块，环节级可追溯 |
| v1.34.1 | 2026-08-12 | **作战地图全覆盖补丁——BM-RC-01 / BM-RC-01-A / BM-RC-01-B / BM-RC-01-C / BM-RES-01-A / BM-RES-03-C**：① §6.2.2 补 BM-RC-01 系列 why 层显式映射（production 补 why，非新建）——9 种限额类型语义表（SINGLE_INSTRUMENT/SECTOR/GROSS/NET/VAR_95/VAR_99/MAX_DD/LEVERAGE/FACTOR ↔ limit_type enum 映射）+ 消耗追踪模型（LimitConsumption notional 占用口径，与 35 号 §3.13 盘中循环衔接，2026 新规 15 笔/秒+撤单率 15% 同口径）+ 预警分级 WARNING 黄/CRITICAL 橙/EMERGENCY 红→AI 自治分级处置（红色 Owner 确认制，与 55 号 §3.1B 三级告警通道衔接）+ 策略 CRUD 状态机与版本管理规则（EVOLVE_ENTRY 快照追溯 / ROLLBACK_ENTRY 回滚 / 阈值放宽 MUST 人工审批）；② §14 新增 L1（BM-RES-01-A 已闭合裁定：不建独立数据集快照/回滚——SemVer+git commit+PIT 多版本已为个人项目上限；血缘=§6.2.3 三实体，字段级血缘 Phase 3+）+ L2（BM-RES-03-C 已闭合裁定：目录层已建=12 注册表 tags+§4.6 交叉引用矩阵+§4.7 E1-E20；语义搜索/引用图谱/推荐器 Phase 3+ 候选，条目>1000 重评） | 作战地图 14 环节全覆盖施工 |
| v1.34.0 | 2026-08-12 | **P0/P1 内容审查 + 跨文档一致性修复（架构审查第 2 轮，2 个子代理反查 12 篇文档）**：① 悬空引用修正 4 处（52 号 §G1 重建版不存在→费率真源迁至 §5.3 R1；25 号"§CSI300实证"不存在→§3.7 归因伪代码默认值；16 号清单 §2→§6.1-6.5）；② 16 号列数 ~55→58（测试契约锁定）；③ E1 待定关闭（51 号用户裁定"mlflow 完全卸载"，experiment_registry=实验元数据唯一登记处，mlflow_run_id→fallback_ref/panel_experiment_ref，§8.3 O3 收敛）；④ §14 新增 K4（risk_limit 42 条 limit_type 分布失衡：var/es/kill_switch 三类为 0 条）+ K5（22 号板块推送池 582 只板块指数 universe 扩展候选，MVP 不施工）；⑤ K2 扩展（momentum_trend 桶混入 33 条潘潘课程规则条目）；⑥ D1 转移 K1（裁定#223 方向反转）；⑦ universe 覆盖完整性确认（5 条个股池无遗漏）；⑧ 40 号 6 算法+价格笼子+CancelRateGuard 15% 阈值验证通过；⑨ A 股费率全网核验一致+佣金全佣/净佣口径说明（§5.3）；⑩ §8.3 O1-O12 裁定全部维持；⑪ 63 号两处漂移记 K6 由 63 号侧修复 | 架构审查循环第 2 轮 |
| v1.33.0 | 2026-08-12 | **治理假闭环修复 + P0 YAML 硬错误修复 + 文档内部一致性审查（架构审查第 1 轮）**：① 治理假闭环实际补齐——v1.0.0 §9.1/§9.2 声称"ROOR 已登记+AGENTS.md 已显化"全量 grep 验证**实际从未做**，本轮实际完成 ROOR tier_2 登记 6 条 + AGENTS.md 业务资产速查；② P0 三件套 YAML 硬错误修复——related_arch→'#ARCH-BREG-001'；universe 补生存偏差三字段，UNI-INDEX-001/002 成分股未落盘诚实标注 pit=false（K3）；③ 文档内部一致性修复 9 处（§1 状态行过期/§3 表 6 个 P1 表 tier_1→tier_2/§2 写死计数→ROOR 动态值/§4.5 Step6 明细补 E14-E20/§4.6 FK 矩阵补 5 条+26→32 条/§4.8 7 态→8 态/§4.13 G2 strategy_type→strategy_class+G3 risk_limit_id→risk_rules+kill_switch 类检查/§4.14 补运行时动态字段说明/§4.16 "E1-E13"→E1-E20）；④ §9.4 D1 状态修正——裁定#223 方向写反+声称已标记实际未标记（三方漂移），转 K1；⑤ §12 按真实进度重写；⑥ §14 补 K1/K2/K3。**施工事故备注**：主工作区两轮修改被并发会话冲掉，本轮在物理隔离 worktree 内重放并经 GitCommitGateway 提交 | 架构审查循环第 1 轮 |
| v1.32.0 | 2026-08-10 | **DASH 归因不可能性定理+A股涨跌停板上游污染+AlgoXpert 稳定性区域+双曲因子衰减+MINGLE+CogAlpha 第二十一轮研究**：§4.39 新增 6 项对标 + factor 补 attribution_stability + experiment 补 parameter_stability_region + E15/E16/G2 三审计扩展（最小 churn 不新增编号）+ data_asset schema 计划 tradability_mask_policy + 3 项 Phase 1.5+/2+ 评估 | 全网搜索 2026-08-10 第二十一轮 |
| v1.31.0 | 2026-08-10 | **Temporal Leakage 测量+Causal Factor Mirage+jump regime 持续性+证监会 2026-07 合规第二十轮研究**：§4.38 新增 4 项对标 + experiment 补 temporal_leakage_measurement + factor 补 causal_structure + risk_limit 补 compliance_notices + regime_detector 补 statistical_jump/jump_diffusion_hmm + E17/E18 两审计扩展 | 全网搜索 2026-08-10 第二十轮 |
| v1.30.0 | 2026-08-10 | **Ulcer/Calmar 路径依赖疼痛+I-Star/Propagator/Algo Wheel 冲击谱系+Custom Benchmark+Active Share+MCP Registry 别名指针第十九轮研究**：§4.37 新增 4 项 + risk_limit 补 pain_metric + experiment 补 ulcer_index/calmar_ratio + execution_algo 补 impact_model_type + cost_model 补 propagator_config + benchmark 补 construction_method/active_share/style_drift_detection + 跨文档边界重申（HRP-μ/CRISP DEFERRED 52/54 号） | 全网搜索 2026-08-10 第十九轮 |
| v1.29.0 | 2026-08-10 | **Alpha 发现 EC 综述+GT-Score 优化时反过拟合+AutoQuant 双重筛查第十八轮研究**：§4.36 新增 3 项（均 Phase 1.5+ 评估，时间轴前移）+ experiment 补 pre_registered/cost_vetoed/ic_oos_gap（v1.25.0 遗留修复）+ risk_limit YAML 补 risk_contribution_decomposition（v1.28.0 遗留修复） | 全网搜索 2026-08-10 第十八轮 |
| v1.28.0 | 2026-08-10 | **Joint Falsification 三值裁决+LOO 风险分解+Backtest OVERFIT 5 模式第十七轮研究**：§4.35 新增 3 项 + §4.13 裁决三值分类 + G2 补 PF ratio（>2.0 阻断/>1.5 warning）+min trade count 子检查 + experiment 补 viability_verdict/overfit_pattern + risk_limit 补 risk_contribution_decomposition | 全网搜索 2026-08-10 第十七轮 |
| v1.27.0 | 2026-08-10 | **ARM 变点归因+Hubble AST 沙箱+QUANTEVOLVER+Text+VAR 双向 regime+Weighted Kolmogorov+AlphaBench 第十六轮研究**：§4.34 新增 6 项（6 引擎层空白闭合）+ §4.8 补变点归因子步骤 + factor 补 llm_safety_stack + discovery_agent 补 quantevolver + regime_detector 补 text_var_dual + calibration 双 enum 补 weighted_kolmogorov | 全网搜索 2026-08-10 第十六轮 |
| v1.26.0 | 2026-08-10 | **Wasserstein HMM+PBO null=0.5 误读澄清+Kyle lambda 陷阱+Meta-labeling 边界第十五轮研究**：§4.33 新增 5 项（概念校准）+ regime_detector 补 wasserstein_hmm + G2 加 PBO null=0.5 警示 + factor 补 liquidity_metric + data_asset 补 label_delay_days/drift_detector（v1.21.0 遗留落地）+ meta_labeling_config 适用边界注释 | 全网搜索 2026-08-10 第十五轮 |
| v1.25.0 | 2026-08-10 | **PIT 字段语义+预注册协议+因子发现自动化第十四轮研究+3 注册表 schema 批量补全**：§4.32 新增 3 项 + E14 扩 d 维度（as_of_date_semantics）+ G1 增强（成本否决+IC-OOS 脱钩告警）+ experiment 补 pre_registered/cost_vetoed/ic_oos_gap + factor 补 discovery_agent + 3 注册表批量补全 v1.20-v1.23 字段 + ruling_registry 裁定#223 登记改名（D1 闭合，后 v1.33.0 发现方向反转转 K1） | 全网搜索 2026-08-10 第十四轮 + 审查 agent 施工算法完整性审查 |
| v1.24.0 | 2026-08-10 | **universe_registry 生存偏差治理第十三轮研究+E14 扩 c 维度**：§4.31 新增（universe PIT 成分构造+退市股处理，"概念正确但实现遗漏"缺口）+ universe 补 pit_constituent_construction/delisted_handling/survivorship_free 三字段（不新增 E21 避免编号膨胀） | 全网搜索 2026-08-10 第十三轮 |
| v1.23.0 | 2026-08-10 | **RMT 去噪因子相关性矩阵+RSB 非高斯回撤校准+RWC 共形 VaR 校准第十二轮研究**：§4.30 新增 3 项 + E20 新增（E1-E19→E1-E20）+ factor 补 rmt_denoised + risk_limit 补 drawdown_calibration_method/var_calibration_method | 全网搜索 2026-08-10 第十二轮 |
| v1.22.0 | 2026-08-10 | **GSA-LLR 鲁棒 CUSUM+LAP 前瞻污染+LIB 偏差审计第十一轮研究+schema 补全**：§4.29 新增 4 项 + E18/E19 新增（E1-E17→E1-E19）+ §4.8 DECAY_SCAN_MULTI 检测器 1 增重尾自适应分支 + experiment 补 lap_check_result + factor 补 lib_audit/ex_post_filter_audit + risk_limit 补 stage/response_strategy + decay_detection_method 补 gsa_llr_cusum + A 股板块轮动 14.8% 警示 | 全网搜索 2026-08-10 第十一轮 |
| v1.21.0 | 2026-08-10 | **DSR 鲁棒性带+因果验证声明第十轮研究**：§4.28 新增 12 项 + G2 新增鲁棒性带检查（trial_correlated 无 bootstrap=阻断+n_trials>10 须报告区间）+ E17 新增（E1-E16→E1-E17）+ experiment 补 trial_correlated/effective_trial_count_band/bootstrap_test_passed + factor 补 causal_graph | 全网搜索 2026-08-10 第十轮 |
| v1.20.0 | 2026-08-10 | **策略容量检验+因子冗余检测第九轮研究**：§4.27 新增 3 项 + §4.13 新增 G9 容量检验门（G1-G8→G1-G9）+ E16 新增（E1-E15→E1-E16）+ strategy 补 capacity_aum_limit/participation_rate_limit/market_impact_model + factor 补 correlation_group/redundancy_status | 全网搜索 2026-08-10 第九轮 |
| v1.19.0 | 2026-08-10 | **LLM 时代量化治理第八轮研究**：§4.26 新增 5 项 + E15 新增（E1-E14→E1-E15）+ data_asset 补 llm_training_cutoff/lookahead_test_method + experiment 补 llm_lookahead_check_result + attribution_result 注释补 VIF + factor 补 schema_plan + strategy 补 origin/distilled_to_code + regime_detector 补 news_aware | 全网搜索 2026-08-10 第八轮 |
| v1.18.0 | 2026-08-10 | **回测数据偏差治理+策略组合+信号融合+归因分析第七轮研究**：§4.25 新增 4 项 + E14 新增（E1-E13→E1-E14）+ §4.4 新增跨文档职责边界（RUN_BACKTEST→52号/ATTRIBUTION→54号）+ data_asset 补 survivorship_free/pit_available/earnings_lag_days + experiment 补 backtest_bias_checks/attribution_result + strategy 补 combination_strategy/meta_labeling_config | 全网搜索 2026-08-10 第七轮 |
| v1.17.0 | 2026-08-10 | **P0 伪代码 bug 修复+仓位管理+A股特色数据第六轮研究**：§4.13 G1/G2 修复（str() 拼接 TypeError + CPCV mean<=0 直接 FAIL）+ §4.24 新增 5 项（Conformal Kelly/Kelly+ML 协方差/Sizing Shootout/A股高频因子/龙虎榜 Level-2 license_type） | 全网搜索 2026-08-10 第六轮 |
| v1.16.0 | 2026-08-10 | **CPCV 升级六方法+价格笼子 schema+A股微观结构第五轮研究**：§7.2 回测过拟合五方法→六方法（+CPCV）+ §4.13 G2 新增 CPCV 检查（catastrophic-veto+切法敏感性）+ §4.23 新增 4 项 + execution_algo 补 price_cage_config/t_plus_1/limit_up_down_untradable 三字段 | 全网搜索 2026-08-10 第五轮 |
| v1.15.0 | 2026-08-10 | **局域网关闭补齐+高频阈值核实+第四轮研究流程治理**：§4.20③ 局域网行情通道关闭（2026-07-31/广域网时延≥2ms 地板/8-31 网关指引）+ §4.20② 高频阈值核实（15 笔/秒现行有效，中基协 300 笔/秒系 2025 年版规定误引）+ §4.22 新增 5 项（AlphaSchema/Agentic Workflows/证据 SHA256+allowed_use/数据契约独立模块/Agent 竞争转向） | 全网搜索 2026-08-10 第四轮 |
| v1.14.0 | 2026-08-10 | **A股 2026 监管变更+算法一致性修复+第三轮研究**：§4.20 新增（交易规则修订+程序化细则，5 表 schema MUST 预留合规字段）+ PROMOTE_ENTRY G1 加 min_trl_years 交叉校验+G2 加 MTC 检查（字段-算法漂移修复）+ §4.17② BOCPE 误判频率派事实错误修正 + §4.21 新增 7 项 | 全网搜索 2026-08-10 第三轮 |
| v1.13.0 | 2026-08-10 | **第二轮缺口审计+版本差异算法 DIFF_ENTRY（13 算法体系完整闭环）**：§4.18 新增 DIFF_ENTRY 横切只读查询算法（5 步）+ §4.19 第二轮缺口审计 10 领域映射（1 硬缺口已补/4 已覆盖/5 DEFER）+ §4.4 导航图 12→13 算法 | 全网搜索 2026-08-10 第二轮 |
| v1.12.0 | 2026-08-10 | **最新研究对标+回测过拟合第 5 方法 MTC+8 项算法升级**：§4.17 新增 8 项 + §7.2 四方法→五方法（+MTC）+ §13 补 R37-R39 明细 + §14 补 H1/I1 | 全网搜索 2026-08-10 第一轮 |
| v1.11.0 | 2026-08-10 | **YAML→DB 迁移算法闭环+MinBTL 第 4 方法**：§4.16 新增 MIGRATE_REGISTRY（R1-R7+R4/R7 双 gate，12 算法 7 阶段闭环"建→上→改→测→应/回→退→迁"）+ §4.4 导航图更新 + §7.2 补 min_trl_years | 全网搜索 2026-08-10（longterm-wiki #2076/mvpfactory.io/youngju.dev/Bailey&LdP 2014） |
| v1.10.0 | 2026-08-10 | **算法体系导航图+语义漂移+SHA256 manifest+参数漂移+渐进式部署**：§4.4 新增导航图 + §4.7 补 E13 语义漂移 + §4 原则9 补 SHA256 manifest 选项 + §4.8 补参数漂移概念 + §4.13 补 Shadow→Canary→Full 三阶段 | 全网搜索 2026-08-10（oracles.cloud/neojn/OmniBioAI/Ollama/eastmoney/metricgate/frontierledger/NautilusTrader） |
| v1.9.0 | 2026-08-10 | **回滚+依赖解析算法闭环**：§4.14 新增 ROLLBACK_ENTRY（7 步）+ §4.15 新增 DEPENDENCY_RESOLVE（Kahn 拓扑/传递依赖/影响范围） | 全网搜索 2026-08-10（metricgate/frontierledger/Kahn's algorithm/Apicurio） |
| v1.8.0 | 2026-08-10 | **PROMOTE_ENTRY 上线晋升算法（填补 §4.9 引用缺口）**：§4.13 新增 8 门禁上线算法（G1-G8）+ EVOLVE_ENTRY Step 1 status 分支更新引用；完整生命周期闭环 CONSTRUCT→PROMOTE→EVOLVE→DECAY→ADAPT→RETIRE | 全网搜索 2026-08-10（opennash 7-gate/MLflow/thirstysprout/KRI 治理） |
| v1.7.0 | 2026-08-10 | **执行算法反博弈+TCA 双报告+图形识别 Simplicity Wins+RETIRE 级联响应**：§6.2.1 补 anti_gaming/tca_metrics+POV 内生性 γ/(1-γ)；§6.2.4 补 cnn_lstm_hybrid+Simplicity Wins+反 Look-Ahead Bias 归一化约束；§4.10 补级联响应定义 | 全网搜索 2026-08-10（marketmaker.cc/iotdigitaltwinplm/arXiv:2605.00875/mental-momentum/Apicurio） |
| v1.6.0 | 2026-08-10 | **PSR/DSR 排序修正+Plateau 选择原则+honest-backtest 7 层+KRI 6 角色+版本可复现性三要素+鲁棒 CUSUM**：§7.2 补 Soloviov Plateau-Robustness+7 层框架+schema 补 plateau_score/adversarial_result；§6.2.2 补 KRI 6 角色（2 主体 4 职能映射）；§4.12 Step 3b 补 plateau centroid 量化；§4 原则9 补三要素；§4.8 补 GSA-LLR+RisingWave 静默失败；§4.7 修正 E12 缩进 bug+E11 补 freshness | 全网搜索 2026-08-10（Soloviov/honest-backtest/risktemplate/beefed.ai/MLflow 3.15.1/arXiv GSA-LLR/RisingWave/Atlan） |
| v1.5.0 | 2026-08-10 | **ADAPT_STRATEGY 数学+经验双驱动+衰减原因分类+baseline 保存+PBO 分层解读**：§4.12 补 Step 0+Step 1.5（Five Horsemen）+三选一矩阵+6 类 review triggers；§4.7 补 E12；§4.8 补衰减原因分类表+127 策略经验数据+监控频率；§7.2 补 PBO 5 层解读；strategy 补 baseline 扩展字段/decay_cause/decay_scan_frequency | 全网搜索 2026-08-03（LuxAlgo/smartfinancedata/Pomegra/usekeel.io） |
| v1.4.0 | 2026-08-10 | **施工算法体系完整闭环+衰减后适应+跨维度检测器+数据质量监控+版本策略增强**：§4.12 新增 ADAPT_STRATEGY（填补 检测→适应→退役 中间缺口）；§4.8 补 profit_factor/z_score；§4.7 补 E5b/E11；§4 原则9 补 Immutable Version 选项；§4.11 补文件级版本管理；factor/strategy schema 补 data_quality/adaptation_level/code_commit 字段 | 全网搜索 2026-08-10（mathandmarkets Part82/nexusfi/trendsandbreakouts/arXiv:2602.10785/PineForge/apxml/metricgate/RisingWave/beefed.ai） |
| v1.3.0 | 2026-08-10 | **施工算法体系闭环+多检测器+回测过拟合检测+Schema 演进治理**：§4.9/§4.10/§4.11 新增；§4.7 补 E8-E10；§4.8 补 CUSUM/PH/BOCPE 2/3 投票；§7.2 补 PBO/DSR/PSR；§4 补原则 11/12 | 全网搜索 2026-08（mathandmarkets/quantt.ca/backtest-guard/Soloviov PBO/Confluent/theFactory/datalakehouse/jsonic） |
| v1.2.0 | 2026-08-10 | **施工环节流程算法补全+schema 增强+2026 实践对标深化**：新增 §4.5/§4.6/§4.7/§4.8；增强 8 个 schema（lookback_period/benchmark_id/warmup_period/cooling_period/version_pin/decay_detection 等）；补 Feast Versioning/策略 10 阶段生命周期/pandas-ta/CNN+TA-Lib/EU AI Act/MLflow 3.15/square-root 律实证；更新 §11 混合模式共识 | 全网搜索 2026 最新实践（Feast/MLflow/Alexander&Fabozzi/Vibe-Trading）+ 2026-07 平方根律论文 |
| v1.1.1 | 2026-08-10 | **循环审查第 1 轮：DS 计数 DS-030+→DS-076（76条）+ cost_model YAML 同步完成 + schema 注释修正** | 全量 grep dataflow_graph_registry.yaml + YAML/文档交叉验证 |
| v1.1.0 | 2026-08-10 | **深度审查修正 8 处硬错误 + 新增过度工程审查 + 2026 实践对标** | 全网搜索 2026 最佳实践 + 代码反查 + 注册表交叉验证 |
| v1.0.0 | 2026-08-10 | 初版创建，P0 三件套落盘，12 注册表 schema 定稿，8 核心裁定 + S1-S6 修正 | business_registry_consolidation_plan.md 施工方案 |

**修订明细（R1-R77，压缩保留核心事实）**：

- **R1（P0 硬错误·费率校准，§5.3 费率真源以此为准）**：cost_model 印花税 千1→**万5**（2023-08-28 减半政策，2026 延续）；过户费 万0.1/沪市only→**万0.1/沪深双向**（中国结算统一标准）。同步 catalogs/cost_model_registry.yaml。原印花税 2 倍高估会导致回测成本失真。依据：[华泰证券2026费率](http://m.toutiao.com/group/7671636219272430089/) ｜ [2026最新收费标准](https://licai.cofool.com/user/guide_view_3447293.html) ｜ [2026炒股成本揭秘](https://post.m.smzdm.com/p/a70o48xd/)
- **R2（路径漂移）**：factor 数据来源 `src/zephyr/factor/ashare/`（15 子目录，**不存在**）→ `src/zephyr/factor/`（6 .py + 子目录：factor_base/momentum_factor/value_factor/intraday_snapshot_factors/alpha_signal_pipeline/bus_factor_defense）
- **R3（schema-代码漂移）**：technical_indicator 第5类 `structure`→**`reversal`**（16 号 §6.5 + 代码 reversal.py 一致）
- **R4（算法枚举漂移）**：execution_algo 6 算法 `aggressive/adaptive`→**`iceberg/alt`**（40 号实际 TWAP/VWAP/ICEBERG/POV/IS/ALT；alt 保留 aggressive 别名，adaptive 删除）
- **R5（概念混淆）**：risk_limit 数据来源删 `config/risk_register.yaml`（该文件是 MOD-INF-001 基础设施风险 R1-R21：SQLite/死锁/Schema/ChromaDB，**非交易风控限额**；真源 src/zephyr/risk/）
- **R6（计数错误）**：data_asset DS-001~029→**DS-001~076（76条）**
- **R7（裁定未落实）**：S6 改名 ruling_registry 登记**未完成**（grep 无输出）→ 验收 + 待定 D1（后转 K1）
- **R8（新增 §8.3 过度工程审查 O1-O12）**：总结论"整体不过度"，仅 chart_pattern MVP 裁剪（O6）+ experiment_registry 待 MLflow 决策（O3，v1.34.0 已关闭）
- **R9（2026 实践对标补充）**：factor↔Feature Store/qlib Alpha158 ｜ strategy↔Strategy Lifecycle Management ｜ risk↔NIST/ISO 31000 ｜ data_asset↔OpenLineage ｜ experiment↔MLflow 2026（Neptune 关停）｜ field_dictionary↔dbt schema.yml ｜ chart_pattern↔TA-Lib CDLPATTERN 61 种 ｜ cost_model↔square-root law 2026 实证
- **R10（基准选择待定）**：2026 中证A500 成机构标配（年化 8.58% > 沪深300 7.55%），待定 B1 是否补登记
- **R11（DS 计数严重少算修正）**：dataflow_graph_registry.yaml 实际 **76 条** datasets（DS-001~DS-076），v1.1.0 初估"DS-030+"仍少算，全量 `Select-String "^- dataset_id:"` 确认；同步修正所有 DS 计数引用
- **R12（cost_model YAML 同步完成）**：印花税 rate 0.001→0.0005（2处）、过户费 sh_only→sh_sz_both（3处）、version 1.0.0→1.1.0；同步修正 §5.3 schema 注释
- **R13-R16（施工环节流程算法补全）**：新增 §4.5 CONSTRUCT_REGISTRY 8 步 / §4.6 FK 矩阵（初版 26 条）/ §4.7 AUDIT_REGISTRY 7 检查（强制 Select-String 实码核对，40 号 v2.6.0 教训）/ §4.8 10 阶段生命周期 + DECAY_SCAN
- **R17（schema 增强）**：factor 补 lookback_period/benchmark_id/version_pin/decay_detection 字段；strategy 补 benchmark_id/decay_threshold/mrp_baseline；indicator 补 warmup_period；execution_algo 补 warmup_participation_rate/cooling_period/cost_model_ref/rl_policy_ref；risk_limit 补 inherent_risk/residual_risk/kri_frequency/review_cycle/scope_strategy；chart_pattern 补 dl_model_ref/dl_training_dataset；experiment 补 benchmark_id/cost_model_ref/mlflow_run_id/mace_env_ref
- **R18（2026 对标深化）**：Feast Versioning→version/version_pin；10 阶段生命周期→lifecycle_status 8 态；CNN+TA-Lib（99.3%）→chart_pattern dl_cnn；EU AI Act→risk_limit 合规；square-root 律实证（A 股 α≈0.7）→cost_model
- **R19（YAML→DB 混合模式共识）**：§11 更新——"最小引导 YAML + DB 运行时"共识（Feast SQLRegistry + MLflow DB backend）
- **R20-R22（变更/退役/Schema 演进三算法）**：§4.9 EVOLVE_ENTRY（6 步+6 类变更分类）/ §4.10 RETIRE_ENTRY（3 阶段+4 类触发）/ §4.11 EVOLVE_SCHEMA（5 步+兼容性模式）
- **R23（审计增强）**：§4.7 补 E8 循环引用/E9 日期逻辑/E10 必填空值
- **R24（衰减多检测器）**：§4.8 DECAY_SCAN_MULTI（CUSUM+PH+BOCPE 2/3 投票）；MVP 基础版，Phase 1.5+ 多检测器
- **R25（回测过拟合检测）**：§7.2 补 PBO/DSR/PSR+PurgedKFold + pbo_value/dsr_value/psr_value/n_trials 四字段；PBO null=0.5（非0），>0.2 红旗
- **R26（通用原则补充）**：§4 补第 11 条（Additive-Only/Expand-Contract）+ 第 12 条（change_type 分类+90天宽限+retired 保留审计）
- **R27（待定问题补 C1）**：power_law(exponent=0.7) 冲击模型——§5.3 已引用但 §14 遗漏，补登
- **R28（衰减后适应算法）**：§4.12 ADAPT_STRATEGY——5 步（分级→refit window `w*=(2σ²/δ²)^(1/3)≈126天`→refit+过拟合防护→OOS 验证→频率约束）；adaptation=overfitting 同一数学操作，OOS 验证判定成败
- **R29（跨维度检测器）**：§4.8 补 profit_factor（trades 维度）/z_score（分布维度）——跨维度组合覆盖更全
- **R30（commit 绑定检查）**：§4.7 E5b——code_path+commit 双绑定；factor/strategy 补 code_commit 字段
- **R31-R33（数据质量+适应字段）**：§4.7 E11（alert on earliest layer）；factor/strategy 补 data_quality_policy/null_rate/drift_psi/drift_ks/range_bounds/last_quality_scan_at；strategy 补 adaptation_level/last_refit_at/baseline_sharpe（refit 间隔≥60天防过拟合）
- **R34（版本策略增强，§14 L1 引用此条）**：§4 原则9 补 Immutable Version 选项——apxml 4 策略对比（Semantic/Immutable/Timestamped/Branch-based），Immutable（content hash）最强 reproducibility；YAML 阶段用 Semantic（git commit hash 天然提供 Immutable 保证），DB 阶段可升级
- **R35（schema 文件级版本管理）**：§4.11 补 theFactory v1→v2 新文件规则——DB 阶段 breaking 变更新建 v2 文件，v1/v2 共存按 version 选解析
- **R36（待定问题补 F1）**：参数适应 vs 退役决策——Level 3→Level 5 升级阈值需实盘数据校准
- **R37-R39（迁移算法+导航图+MinBTL）**：§4.16 MIGRATE_REGISTRY R1-R7（R6 不可逆三条件：28天清洁期+git快照+R7审计）；§4.4 导航图 12 算法 7 阶段；§7.2 补 min_trl_years（MBL=0.5×(Z_α×σ_ann/SR_ann)²；SR=0.5→25-40+年/1.0→5-10年/1.5→3-5年/2.0→1.5-3年；SE(SR)≈1/√T；自相关膨胀 1.5-3x）
- **R40-R42（MTC 第 5 方法+8 项对标+明细补登）**：§7.2 补 MTC（White's RC/Hansen SPA/Romano-Wolf/MCS/BH-FDR；SPA 与 Romano-Wolf 互斥选其一；MCS 输出集合非赢家；DSR 与 MTC 正交）+ mtc_method/mtc_pvalue/mtc_survived 三字段；§4.17 新增 8 项对标；§14 补 H1（迁移阈值校准）/I1（MinBTL A 股校准，σ_ann=25% vs 美股 15% 放大 2.8 倍）
- **R43-R45（DIFF_ENTRY+缺口审计+导航图 13 算法）**：§4.18 DIFF_ENTRY（5 步：BLAKE3 快判→字段三分类→语义分类→semver 映射→breaking 查依赖；YAML 阶段 git diff+dict diff+查表 <50 行）；§4.19 十领域映射（1 硬缺口已补/4 覆盖/5 DEFER——13 算法闭环无阻塞）；§4.4 导航图 12→13 算法
- **R46（PROMOTE_ENTRY 一致性修复）**：G1 加 min_trl_years 交叉校验 + G2 加 MTC 检查——**版本增量导致的字段-算法漂移**，后续新增 schema 字段/方法 MUST 回溯检查是否被引用算法纳入
- **R47（§4.17② BOCPE 事实错误修正）**："三检测器均为频率派"系事实错误——BOCPE=BOCPD 已是贝叶斯；真正增量=score-driven 变体（Tsaknaki 2025），非"新增第 4 检测器"
- **R48（§4.20 A股监管变更）**：交易规则修订（ST 5→10%/盘后扩围/SSE 基金收盘集合/创业板做市商+大宗盘中）+ 程序化细则（15 笔/秒+撤单率≤15%+≥50µs）；印花税/过户费/整手 2026 未调整；execution_algo MUST 新增 6 合规字段，CancelRateGuard 对齐 15%
- **R49（§4.21 第三轮 7 项）**：SR 26-2/NautilusTrader/Double-selection LASSO/华创 LightGBM 三标签/AH-HMM/Feast 0.64/meta-labeling
- **R50（§4.20③ 局域网关闭补齐）**：2026-07-31 局域网关闭/广域网双向时延≥2ms 地板/8-31 网关指引；execution_algo 补 latency_floor_ms+network_type、cost_model 补 slippage_regime、data_asset 补 latency_profile+colocation_eligible；仅关行情接收链路，报盘专线暂留
- **R51（高频阈值核实）**：中基协研报"300 笔/秒"系 2025 年版规定误引——2025 年版 300/秒（2025-07-07）已失效，现行 15 笔/秒分两阶段（2026-04-07+2026-07-07 全面落地）；**引用高频阈值 MUST 标注生效日期+阶段**
- **R52（§4.22 第四轮 5 项）**：AlphaSchema/Agentic Workflows（架构承重件，2× 非 10×）/证据 SHA256+allowed_use/数据契约独立模块/Agent 协同转向（研究流程自动化≠RL 交易决策，正交）
- **R53（CPCV 第 6 方法+G2 增强）**：CPCV 给 C(N,k) 条 OOS 分布（purge+embargo），方差才是真实信号；t-stat 需 3.0 非 1.96；G2 新增 catastrophic-veto（cpcv_worst_max_dd>0.15 一票否决）+std/mean>0.5 切法敏感性阻断；schema 预留 cpcv_* 五字段
- **R54（execution_algo 补价格笼子三字段）**：price_cage_config（主板/创业板 102%/98%+0.1元兜底；科创板纯 102%/98%；北交所 105%/95%）+t_plus_1+limit_up_down_untradable——40 号 v2.6.0 已实现 check_price_cage，schema 对齐（schema-代码漂移修复）
- **R55（§4.23 第五轮 4 项）**：AlgoXpert IS-WFA-OOS/EU AI Act 可解释 AI/A股微观结构/决策审计 append-only ledger
- **R56（G1/G2 P0 伪代码 bug 修复）**：① 字符串拼接 TypeError——9 处统一 `str()` 转换；② CPCV mean<=0 漏判——改为直接 FAIL（OOS 平均 Sharpe 非正=多数切分亏损不可部署），变异检查改 elif 避免除零。**后续算法伪代码 MUST 通过 str() 规范+边界条件审查（mean<=0/除零/None 检查）**
- **R57（§4.24 仓位管理 3 项）**：Conformal Kelly（interval 宽度作 scale，最简单方法最佳，drawdown dial MaxDD 27.7%→20.3%）/Kelly+ML 协方差（MP denoising+HRP+detoning）/Sizing Shootout（只有 weight 公式不同，须同时 beat Sharpe AND max-DD，OBSERVE-only）
- **R58（§4.24 A股特色数据 2 项）**：高频因子 2026 多空 7-16% 仍有效（日内/隔夜动量反转，T+1 导致）；龙虎榜+Level-2 license_type 治理（AKShare 仅学术用途，实盘前须商业授权评估）
- **R59-R62（E18/E19+GSA-LLR+schema 补全）**：E18 LAP（日期-only 召回查询，β₃>0=污染；FinCAD 推理时抑制+CMMD 多模型过滤 Phase 1.5+）；E19 LIB（企业债 108 因子纠正后多数不再显著；A 股复权价/成交量既入因子又入收益分母=LIB 风险）；DECAY_SCAN_MULTI 检测器 1 增重尾自适应分支（γ₄≥6 自动切换 GSA-LLR，KU-PE 控制误报）；risk_limit 补 stage/response_strategy + 板块轮动 14.8% 警示（STR-SECTOR-ROTATION-001 校准 MUST 采纳：hot_bonus 0.05→0.02，增 q3 权重）
- **R63-R65（E20+校准字段+一致性同步）**：E20 RMT 去噪审计（q=N/T>0.1 时 [λ₋,λ₊]=σ²(1±√q)² 区间内特征值=噪声，MUST clipping 去噪）；risk_limit 补 drawdown_calibration_method（RSB 非高斯：四维度量移动方向不同，单一高斯表系统性误警）+var_calibration_method（RWC 共形：VaR 压力期系统性误校准修复）；E1-E19→E1-E20 全量同步
- **R66-R67（E14 c 维度+universe 三字段）**：E14 自 v1.18.0 声明 universe-membership contamination 但实现只查 data_asset 不查 universe——"概念正确但实现遗漏"；扩展 E14 c 维度（不新增 E21 避免编号膨胀+6 处同步 churn）；universe 补 pit_constituent_construction/delisted_handling/survivorship_free
- **R68-R70（第十四轮+批量补全+D1 闭合）**：Assay as_of_date 语义（Prices=EOD/Splits=执行日/Dividends=公告日≠除权日/Universe=时点成分）；E14 d 维度+G1 成本否决（net Sharpe≤0 阻断）+IC-OOS 脱钩告警；experiment 补 pre_registered/cost_vetoed/ic_oos_gap + factor 补 discovery_agent；3 注册表批量补全 v1.20-v1.23 字段；ruling_registry 裁定#223 登记改名（D1 闭合——v1.33.0 发现方向反转转 K1）
- **R71-R72（第十五轮+schema 落地）**：Wasserstein HMM（2-Wasserstein 模板跟踪解决标签置换）/PBO null=0.5 误读澄清/Kyle lambda OLS slope 陷阱（ratio 塌缩为 Amihud=bug）/Meta-labeling 仅适用 discretionary 主模型；regime_detector 补 wasserstein_hmm + factor 补 liquidity_metric + data_asset 补 label_delay_days/drift_detector
- **R73-R74（第十六轮+流程增强）**：ARM 变点归因（max-over-splits rank statistic，per-coordinate validity+FWER+FDR 三保证；标准做法 FWER>0.66 无效）；§4.8 补步骤 5 变点归因（Phase 2+ 因子数>20 MUST 启用）；factor 补 llm_safety_stack（discovery_agent≠human 时 MUST 声明）+ discovery_agent 补 quantevolver + regime_detector 补 text_var_dual + calibration 双 enum 补 weighted_kolmogorov（γ₄>8 MUST）；Phase 1.5+ AlphaBench 3 任务评测
- **R75-R77（第十七轮+裁决哲学升级）**：Joint Falsification 三值裁决（REFUTED/SUPPORTED/INCONCLUSIVE——"统计不显著"≠"证伪"）；§4.13 裁决逻辑三值分类；G2 补 PF ratio（Train/OOS>2.0 阻断、>1.5 warning）+min trade count（directional 300/mean_reversion 500 笔）；experiment 补 viability_verdict+overfit_pattern + risk_limit 补 risk_contribution_decomposition（LOO inherent+correlation——区分"降仓位"vs"加对冲"）
- **R78（29 号备忘录入库后漂移同步，2026-08-16，commit 62e3ae13）**：§4.24④ intraday 因子编号（001~014→015~028，全量重建删 170 条 deprecated 后续号）；§4.39② 因子计数（111→140）；§14 K2 标注闭合（strategy 全量重建 146 条覆盖修复方案①②）；§14 C1 power_law 候选 ID 改注 CST-ASTOCK-004（003 已被课程成本条目占用）；B1 裁定落地（benchmark 补 BMK-INDEX-004 中证A500 candidate，主基准仍沪深300，替换待多基准回测证据）；K3/K5 裁定登记 CAND-MKTDATA-001/002（CSI300/800 成分股 PIT 快照/板块推送池 universe）；benchmark/cost_model 失效 used_by_strategies 旧 ID 引用置空待回填

## 14. 待定问题（需人决策，不擅自拍板）

| # | 问题 | 背景 | 处理方向 |
|---|---|---|---|
| B1 | 基准是否补中证A500/万得全A | 2026 中证A500 成机构标配，90号§13基准选择待讨论 | 补 BMK-INDEX-004 candidate，待用户裁定是否替换沪深300作 multifactor 基准 |
| C1 | cost_model 冲击模型是否新增 power_law(exponent=0.7) | §5.3 已登记：Han 等中国市场实证 α≈0.7（非0.5），A 股冲击对规模敏感度更陡。当前 square_root(coeff=0.1) 对个人小单足够保守，但 Phase 1.5 AUM 增长后可能需 A 股专用 power_law 模型 | Phase 1.5 校准时评估：新增 CST-ASTOCK-004 power_law(exponent=0.7) 作为 A 股专用冲击模型候选（原规划 CST-ASTOCK-003 已被 2026-08-16 课程成本条目占用，commit 62e3ae13），按 40 号 §13.1 拟合 coefficient 实际值。MVP 阶段不阻塞 |
| D1 | ruling_registry 登记 data_asset 改名（v1.33.0 起转移 K1） | ~~S6 裁定要求但未落实~~ v1.33.0 反查：裁定#223 已登记但**方向写反**（data_asset→dataflow_graph，与 S6 相反），且其声称"62 号 §9.4 D1 已标记完成"实际未标记 | **已转移 K1**（含两个裁定方向选项，需用户拍板） |
| E1 | ~~51号 MLflow 退役决策是否重评~~（v1.34.0 关闭） | 2026 MLflow 是首选，Neptune 已关停，原退役方案前提变化 | **已关闭**：51 号 v1.2.7 确认用户已裁定"mlflow 完全卸载"（方向已定、施工未启动）。62 号原"建议保留 MLflow"方向与用户裁定冲突，v1.34.0 撤回。experiment_registry 施工前提=51 号 A/B/C 完成 + FallbackBackend JSON + Panel experiment_history.py 落地；schema 的 mlflow_run_id 施工时改 fallback_ref/panel_experiment_ref |
| F1 | 参数适应 vs 退役决策（v1.4.0 补） | mathandmarkets Part 82 核心洞察"adaptation=overfitting"——检测到衰减后是 refit 适应还是直接退役是关键决策点。§4.12 ADAPT_STRATEGY 已用 OOS 验证兜底，但 Level 3→Level 5 的升级阈值需实盘数据校准 | MVP 阶段 Level 1-2（监控+减仓），Phase 1.5+ 积累实盘衰减数据后校准 Level 3 refit 触发阈值 + OOS 恢复条件（当前用 baseline_sharpe×0.85 启发式） |
| G1 | decay_cause 衰减原因诊断方法（v1.5.0 补，v1.6.0 补登 §14） | §4.12 ADAPT_STRATEGY Step 1.5 用 Five Horsemen 分类（crowding/regime/overfitting/tech/depletion）驱动 refit vs 退役决策，但 **decay_cause 本身如何诊断是难题**——统计检测器（CUSUM/PH/BOCPE/profit_factor/z_score）只报警"有衰减"，不诊断"为什么衰减"。原因分类需额外诊断方法：crowding=策略拥挤度指标（如成交额/换手率异常）、regime=regime 分类器（HMM/波动率 regime）、overfitting=PBO/DSR 复检（§7.2）、tech=执行成本漂移监控、depletion=套利空间消失（价差压缩）。v1.5.0 schema 补了 decay_cause 字段但诊断算法未定型 | Phase 1.5+ 逐步实现原因诊断器：① overfitting 诊断最成熟（PBO/DSR 已在 §7.2），优先实现；② regime 诊断复用项目 regime 分类器（35/36 号文档已有 regime 概念）；③ crowding/tech/depletion 诊断需研究 A 股特色指标。MVP 阶段 decay_cause 标 unknown，走保守 refit 流程（§4.12 Step 1.5 else 分支） |
| H1 | MIGRATE_REGISTRY 触发阈值校准（v1.11.0 补） | §4.16 MIGRATE_REGISTRY 触发条件为"factor>500 / experiment>5000 / 并发写需求"，但这些阈值是经验值未经实际验证——个人项目当前因子<50/实验<100，远未触发。阈值定太低→过早引入 DB 复杂性（运维成本/迁移风险）；定太高→YAML 性能瓶颈（grep 慢/并发写冲突）。另：12 表是否统一阈值？experiment 增长远快于 factor，可能需分表阈值 | MVP 阶段不触发（YAML+git 足够）；Phase 1.5+ 监控 YAML 加载时间 + 写冲突频率，实测达到以下任一条件再迁：① 单表 entry>300 且 grep 全表>2s ② 并发写冲突周>3次 ③ experiment 年增长>1000。分表阈值：experiment 表阈值可低于 factor（experiment 增长快） |
| I1 | MinBTL 经验值 A 股校准（v1.11.0 补） | §7.2 min_trl_years 经验值（SR=1.0→5-10年）基于美股年化波动率~15%，A 股波动率更高（~25-30%），相同 Sharpe 下所需样本长度可能不同。公式 MBL=0.5×(Z_α×σ_ann/SR_ann)² 中 σ_ann 是年化波动率——A 股高波动意味着相同 SR 需更长 track record，但 A 股高波动也意味着年化收益更高（相同 SR 下），实际影响需校准 | Phase 1.5+ 用 A 股历史数据校准：取 10 年沪深 300 成分股，模拟 SR=1.0 策略，实测不同 σ_ann 下 MinBTL 值。若 A 股 σ_ann=25% vs 美股 15%，MinBTL 放大 (25/15)²≈2.8 倍——SR=1.0 可能需 14-28 年（过于保守），需重新评估 SR 阈值或用 A 股专用校准 |
| J1 | A股2026监管变更施工优先级（v1.14.0 补） | §4.20 两项 2026-07 生效监管变更影响 5 表 schema。关键决策：① ST/*ST 涨跌停 5%→10% 是否立即更新 universe_registry 现有 5 条 entry 的 filter_rules（打板策略 STR-DABAN-001 连板梯队筛选依赖涨停判定，ST 股 10% 涨跌停改变"涨停"语义）；② 程序化交易 15 笔/秒 + 15% 撤单率阈值是硬编码默认值还是可配置（个人策略天然远低于阈值，但 schema 字段 MUST 预留）；③ 盘后固定价格交易扩围是否纳入 cost_model（after_hours slippage=0）作为回测可选时段 | P1-B execution_algo 施工时已预留 6 合规字段（§4.20 已列，v1.34.3 注：schema 已落地）；ST 涨跌停更新需 P1-A universe_registry 重审时同步（影响打板策略核心逻辑，需 24 号文档联动评估）；盘后交易纳入 Phase 1.5+（MVP 不用盘后时段）。MVP 阶段 schema 字段预留=合规底线，实际阈值校准=Phase 1.5+ |
| J2 | 局域网关闭延迟建模 + 研究流程治理字段纳入时机（v1.15.0 补） | §4.20③ 局域网关闭（2026-07-31）+ §4.22 第四轮研究 5 项对标引出新决策点：① 局域网关闭后 `latency_floor_ms=2.0`+`network_type=wan` 是硬编码默认值还是按交易所分别配置（沪市已切广域网，深市待切，跨市场策略须适应两市场时延差异期）；② §4.22③ `allowed_use` 字段（experiment_registry）是否纳入 MVP——它直接支持 §4.13 PROMOTE_ENTRY 渐进式部署的"允许用途"声明，但增加 schema 复杂度；③ §4.22⑤ Agent 协同研究与 project_memory"Mamba/SSM/RL 不采纳"的边界确认——Agent 协同=研究流程自动化（Phase 2+ 评估），RL 策略=交易决策自动化（不采纳），两者边界是否需显式写入 project_memory | ① latency 字段：MVP 阶段沪市/深市统一 `latency_floor_ms=2.0`（广域网地板），Phase 1.5+ 深交所切换完成后按交易所分别校准；② `allowed_use`：Phase 1.5+ experiment_registry 变更时纳入（与 §4.13 渐进式部署强相关，非 MVP 阻塞）；③ Agent 边界：在 project_memory 补一条"Agent 协同研究=研究流程自动化 Phase 2+ 评估项，RL 交易决策=不采纳，两者正交"（待用户确认后登记）。MVP 阶段所有 Phase 1.5+/2+ 项均不阻塞 |
| J3 | CPCV 实施时机 + 价格笼子 schema 对齐策略（v1.16.0 补） | §7.2 CPCV 升级六方法 + §4.23③ 价格笼子 schema 引出新决策点：① CPCV 的 `cpcv_n_groups`/`cpcv_k_test` 默认值 N=10/k=2 适合 A 股日频数据量（5 年约 1200 交易日 → 每组 120 日）还是需按策略持仓周期调整（分钟级策略数据量大，N 可更大）；② §4.13 G2 的 catastrophic-veto 阈值 `cpcv_worst_max_dd > 0.15` 是否与 G1 的 `oos_max_drawdown > 0.15` 冲突（G1 检查平均回撤，G2 检查最差切分回撤，两者阈值相同但语义不同——G1=OOS 整体回撤，G2=任何切分回撤）；③ 价格笼子 `price_cage_config` 是按板块硬编码（main/gem/star/bse 四套）还是按 symbol 动态查询（universe_registry 已有 board 字段）——硬编码简单但板块迁移时需手动更新，动态查询灵活但增加运行时开销 | ① CPCV 参数：MVP 用 N=10/k=2 默认值（日频足够），Phase 1.5+ 分钟级策略按数据量调整 N（经验公式 N ≈ T/120，T=交易日数）；② catastrophic-veto 阈值：G2 的 0.15 是"任何切分最差回撤"硬红线，G1 的 0.15 是"OOS 整体回撤"——两者不冲突但语义须文档明确（G1=整体，G2=最差切分，G2 更保守）；③ 价格笼子：按 symbol 动态查询 universe_registry 的 board 字段（避免硬编码板块迁移问题），MVP 阶段可硬编码四套作为 fallback。MVP 阶段 schema 字段预留=合规底线，实际参数校准=Phase 1.5+ |
| J4 | 仓位管理 sizing_method 选择 + A 股高频因子纳入时机（v1.17.0 补） | §4.24 仓位管理 3 项对标 + A 股特色数据 2 项对标引出新决策点：① strategy_registry 的 `sizing_method` 默认值——fixed_fraction（最简单）/kelly（理论最优但参数敏感）/risk_parity（波动率反比）/conformal_kelly（Phase 2+），个人项目 MVP 用哪个；② A 股高频因子（日内收益/开盘后大单/尾盘占比）依赖 Level-2 数据，MVP 阶段用 AKShare（日线）还是采购商业 Level-2（Wind/iFinD），AKShare 声明仅学术用途——个人项目实盘是否触发商业授权要求；③ §4.24① Conformal Kelly 的核心发现"最简单方法最佳"（宽度稳定性>局部锐度）是否推广到其他模块——即 ZephyrAlpha 是否应遵循"简单优先"原则选择 sizing/drift-detection/risk-model 等模块的方法 | ① sizing_method：MVP 用 fixed_fraction（最简单，Conformal Kelly 论文也证明简单方法最佳），Phase 1.5+ 评估 fractional Kelly，Phase 2+ 评估 Conformal Kelly；② 高频因子：MVP 用日线因子（AKShare 日线可商用研究），Level-2 商业源采购=Phase 1.5+ AUM 增长后评估，个人项目实盘前须法律确认 AKShare 条款；③ 简单优先原则：在 project_memory 补一条"模块方法选择遵循简单优先——先 fixed_fraction/simple covariance/walk-forward，Phase 1.5+ 按实证数据升级复杂方法"（待用户确认后登记，与 Conformal Kelly 论文反直觉发现一致）。MVP 阶段 sizing=fixed_fraction + 因子=日线，Phase 1.5+ 按数据驱动升级 |
| O6 | chart_pattern MVP 范围 | 8 大类全做可能过度 | MVP 先做 candlestick_pattern + chart_pattern 2 类，其余按代码反查按需补（v1.34.3 注：已按此施工，落盘 15 条） |
| K1 | ruling_registry 裁定#223 改名方向反转（v1.33.0 补） | S6 裁定：dataflow_graph_registry.yaml → data_asset_registry.yaml（改名扩展）；但裁定#223（2026-08-10）登记内容为"data_asset_registry → dataflow_graph_registry 改名"——**方向完全写反**，且裁定#223 声称"62 号 §9.4 D1 项标记为已完成"实际未标记（v1.25.0 R70 声称 D1 闭合但 §9.4/§14 未同步，三方漂移）。v1.34.3 核验：data_asset_registry.yaml 已落盘（2026-08-13，166 条），旧 dataflow_graph_registry.yaml 仍并存 | 二选一待用户裁定：① 维持 S6 方向（文件改名 data_asset_registry.yaml）→ 修正裁定#223 的 summary 方向描述 + 删除旧 dataflow_graph_registry.yaml；② 采纳裁定#223 字面方向（维持 dataflow_graph_registry.yaml 文件名不改，仅扩展 sources 段）→ 撤销 S6，62 号 §6.2.3 全局回改 data_asset→dataflow_graph 引用。从名实相符看 ① 更优（三实体扩展后内容远超"数据流图"），且物理层 ① 已落地，② 需回滚已落盘文件 |
| K2 | strategy_registry.yaml schema-YAML 漂移（v1.33.0 补，v1.34.0 扩展） | 62 号 §6.1.2 schema（v1.5.0 R33）声明 baseline_trade_frequency/decay_cause/decay_scan_frequency 三字段，但落盘 strategy_registry.yaml 的 entry_schema 与 59 条 entry **均未含此三字段**（v1.25.0 R70 声称"批量补全"未覆盖）；且 59 条 entry 全部 `distilled_to_code: false` 与 §6.1.2 schema 注释"human 策略天然 distilled_to_code=true（代码即原码）"矛盾。E12/G4 检查引用 baseline_trade_frequency 将对 59 条全量误报。**v1.34.0 扩展发现**：momentum_trend 桶混入 33 条潘潘课程买/卖/做T规则条目（STR-MOMENTUM-TREND-001~033，code_path 空、distilled_to_code=false，27 号 §3 L46 语义澄清它们**不是** G11 机构式动量趋势策略）——6 类分类下的条目语义混杂，需区分"课程规则 candidate"与"机构式策略" | 修复方案（随下一轮 strategy YAML 变更一并做）：① entry_schema + 59 条 entry 补三字段（decay_cause MVP 填 unknown，decay_scan_frequency 按 lifecycle 填 monthly/weekly/daily）；② distilled_to_code 统一改 true（origin=human）或澄清语义；③ momentum_trend 33 条课程规则条目补 subtype/series 标记（如 `entry_series: panpan_course_rules`）与机构式策略区分。**v1.36.1 注（2026-08-16，commit 62e3ae13）：已闭合——strategy_registry 全量重建 146 条（旧 59 条 deprecated 已删），entry_schema v2.1 三字段（baseline_trade_frequency/decay_cause/decay_scan_frequency）已随条目生成；distilled_to_code 统一 false（课程策略未代码化，语义一致）；旧 momentum_trend 桶 33 条已随重建按 29 号 v1.3.2 判定重分类（strategy_class 分流 momentum/daban/intraday 等）** |
| K3 | UNI-INDEX-001/002 成分股文件未落盘（v1.33.0 补） | universe_registry.yaml 的 UNI-INDEX-001（CSI300）/UNI-INDEX-002（CSI800）components_ref 指向 `data/index_constituents/csi300.csv` / `csi800.csv`，2026-08-12 Glob 验证**该目录不存在**——指数成分股从未落盘。E5 审计级硬错误。v1.33.0 已在 YAML 诚实标注 pit=false/survivorship_free=false。**v1.34.0 补充**：25 号文档**无 CSI300/CSI800 成分股实证章节**（CSI300 仅见于 §3.7 归因伪代码 benchmark 默认值），两指数池的文档锚点仅为基准用途 | 回测 CSI300/CSI800 实证前 MUST 补齐：① 接入中证指数官方季度调整历史成分文件（PIT 快照序列，非单当前快照）；② 或改用 akshare index_stock_cons 历史接口按调仓日重建 PIT 成分；③ 落盘后回改 YAML 三字段为 true/include/true。MVP 阶段 multifactor 回测可先用 UNI-RULE-001 全A可交易池替代（已标 pit=true） |
| K4 | risk_limit_registry 缺 var/es/kill_switch 三类条目（v1.34.0 新增） | 落盘 risk_limit_registry.yaml 42 条 limit_type 分布：drawdown×8 / position×21 / concentration×6 / firm_risk×5 / leverage×1 / turnover×1——**var/es/kill_switch 三类为 0 条**。36 号 VaR 5 级（GREEN/YELLOW/ORANGE/RED/BLACK）+ 35 号 §3.5 Kill Switch 多源触发（回撤/单日亏损>6%/连续5天亏损/流动性危机/黑天鹅BS-007）+ 36 号 ES 明明有设计，Step1-3 反查时漏登记；反而无文档依据的 leverage/turnover 各有 1 条（35/36/37/32 号无对应条款，个人 A 股现货无杠杆）。project_memory"VaR 5级+7黑天鹅降级监控层（先全建+全log）"的"全建"未落实。**v1.34.3 核验**：当前落盘 62 条（v1.34.0 K4 补登后），var/es/kill_switch 条目已补（RLM-VAR-001~005 等，见 §6.2.2 BM 映射块）；本条保留作分布核验记录 | 已补登（v1.34.0 K4 处理）：① 从 36 号补登 VaR 5 级限额条目（RLM-VAR-001~005）+ ES 条目（RLM-ES-001）；② 从 35 号 §3.5 补登 kill_switch 多源触发条目（RLM-KILL-SWITCH-001）；③ leverage/turnover 两条孤条目补文档依据或标 candidate 待 35/36/37 号联动评估；④ §6.2.2 的"9 种限额类型"描述与实际条目对齐（BM-RC-01-B 映射表已闭合） |
| K5 | 板块推送池是否纳入 universe_registry（v1.34.0 新增，可选候选） | 22 号行业轮动有"板块推送池"（880xxx/881xxx，582 只板块指数，22 号 §5.1）——板块层 universe 而非个股池。universe_registry 当前 5 条全为个股池，板块层无登记 | 可选扩展（非阻塞）：若 sector_rotation 策略施工推进，可补 UNI-SECTOR-001（板块推送池，universe_type=rule_based，component 为板块指数非个股）。MVP 阶段不施工，22 号策略落地时再裁定 |
| K6 | 63 号配对文档的两处漂移（v1.34.0 新增，63 号侧修复不越界） | 63 号 line 46 写"62 号已定稿 12 个业务注册表 schema（P0 完成三件套，**P1 待施工 9 件套**）"——口径与 62 号不符（62 号 P1=7 表 + P2=2 表，且 factor/strategy/risk_limit 已落盘 Step1-3）；63 号 line 47 引用"62 号 **line 1715** 记录 dataflow DS-001~076"——硬编码行号引用，62 号 v1.33.0/v1.34.0 编辑后该行已是 §4.13 PROMOTE_ENTRY 内容（引用目标漂移）。01 号规范要求交叉引用用稳定 path，行号引用脆弱 | 不越界改 63 号，由其下一轮审查时修复：① "P1 待施工 9 件套"改为"P1 7 表+P2 2 表，12 表已全部落盘"（v1.34.3 注：12/12 已建成）；② 行号引用改为稳定章节引用（62 号 §6.2.3 数据来源段） |
| L1 | BM-RES-01-A 数据集版本化与血缘追踪（v1.34.1 作战地图全覆盖补丁，**已闭合裁定**） | 作战地图 BM-RES-01-A（L0，design 态）：原始数据 → Git-like 版本管理→数据快照→回滚→血缘追踪（来源→变换→去向）→质量评分→生命周期管理，versioning_mode 候选 git-like/snapshot | **裁定：不建独立数据集快照/回滚服务**——SemVer + git commit（充 immutable，§4 原则 9 + R34）+ ClickHouse 财报表 PIT 多版本（`available_at` 保留全版本物理设计，15 号 §3 双层 PIT 已施工）已为个人项目上限；15 号已明示"不建独立特征版本服务"，50 号已否决 DVC（"管数据集版本，不是结果日志"另一层）。**血缘=§6.2.3 data_asset_registry 三实体**（sources/datasets/jobs + produced_by/consumed_by 自引用，对标 OpenLineage Source/Dataset/Job）——数据集级血缘已随 P1-B 施工闭合；**字段级血缘（column-level）登记 Phase 3+ 远期候选**（§6.2.3 已裁定个人项目不需要 RunEvent/column-level）。重评条件：出现跨源对账错数且数据集级血缘无法定位时，重评字段级血缘 |
| L2 | BM-RES-03-C 研究目录与搜索引擎（v1.34.1 作战地图全覆盖补丁，**已闭合裁定**） | 作战地图 BM-RES-03-C（L0，design 态）：研究资产元数据 → 搜索引擎→标签系统→引用图谱→推荐器→访问控制 → 研究目录（可搜索/可引用），search_engine 候选 keyword/semantic/hybrid | **裁定：目录层已建**——12 注册表体系即研究资产目录真源：各表 `tags` 字段（标签系统）+ §4.6 交叉引用矩阵（32 条 FK，引用图谱的结构化替代）+ §4.7 E1-E20 验证审计算法（横切查询）。**语义搜索/引用图谱可视化/推荐器登记 Phase 3+ 候选**——个人项目研究资产总量（因子 111/策略 59/限额 62）下关键词+tags+FK 遍历已够，语义搜索的边际价值随资产规模增长。重评条件：注册表条目总量 >1000 或研究员检索失败率成为痛点时，评估 hybrid（关键词+向量）搜索层；访问控制不建（单 Owner 系统无多租户） |

---

## 15. chart_pattern used_by_factors 回填挂起登记（2026-08-20）

> AI-NIGHT-001 包 Q2 派单（对应 tracker #32，本备忘不越界改 tracker，仅登记口径）。结论：**回填挂起，挂起条件=形态因子施工**。

- **现状实证（2026-08-20）**：`chart_pattern_registry.yaml` 15 条 entry 的 `used_by_factors` 字段**全为空列表 `[]`**（逐条 grep 实证：candlestick 6 active + chart_pattern 4 candidate + trendline 1 candidate + support_resistance 3 active + structure 1 active 无一例外）；schema 注释既定口径="反向关联 factor_id（forward-ref，factor_registry 施工后回填）"（§6.2.4 + 注册表 L200）。
- **挂起原因**：`used_by_factors` 是"形态 → 因子"的**反向关联**——回填源在因子侧。当前形态因子未施工（factor_registry 中无消费 chart_pattern 条目的形态因子落码条目，29 号入库的 140 条因子多为 candidate 且 code_path 空），反向关联无的放矢；强行回填=凭空编写（违反本备忘"内容按需填充"与 63 号"不给无消费方的表写消费文档"同纪律）。
- **挂起条件（回填触发）**：形态因子施工批——任一形态因子落码并登记 factor_registry（code_path 非空、与 PAT-XXX 条目建立引用）时启动回填。
- **回填动作预案**（触发后单批可闭环，未来工程-小型）：① 按 §6.2.4 关系链（chart_pattern_registry 识别算法 → factor_registry 形态因子 → strategy_registry）逐条回填 `used_by_factors: [FCT-XXX, ...]` 并同步 `updated_at`；② 回填后跑 §4.7 E 系列交叉引用校验（FK 双向一致：factor 侧引用形态、形态侧 used_by_factors 回指）；③ 与因子 IC 回填（tracker #56）不同源——本项只依赖形态因子落码，不依赖回测跑批基础设施。
- **当前状态登记**：字段保留空列表为**诚实占位**（非缺口、非漂移）——与 §6.2.4"建库结构完整，内容按需填充"原则一致；待形态因子施工批一并回填。