---
ttl: permanent
doc_type: architecture_view
title: 23路并发AI审查回填指令集
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.1.2"
date: 2026-08-15
topic: ai_review_instructions
scope: 07_trading_decision_architecture
---

# 23 路并发 AI 审查回填指令集

> **用途**：本文档包含 23 个 AI 的完整指令，每个指令可一键复制到新 AI 对话中独立执行。
> **任务**：对 `07_trading_decision_architecture/design_memos/` 下 48 篇文档进行回填、审查、扩展、更新、过度工程清理。
> **创建日期**：2026-08-10
> **更新日期**：2026-08-15
> **使用方式**：复制对应 AI 编号的指令块 → 开新对话 → 粘贴 → 执行
> **修订记录**：2026-08-12 v2.1.0——新增 AI-23 负责 66 号提交队列串行化（47 篇→48 篇）；通用规则 #5/#7 升级并同步内嵌全部 23 个指令块（过度工程判定基准锚定 system_charter §2 硬边界+「1 人在 TRAE 上多 AI 多对话并发施工」，远期工程不算；循环审查加入 git 提交闭环，退出条件=问题数量 0 且缺失功能/模块数量 0）；2026-08-14 v2.1.1——压缩精简：条文全保留，解释性散文压缩（AI-DOCS-001）；2026-08-15 v2.1.2——第二轮循环压缩：可压缩点收敛=0（AI-DC2-09）

---

## 0. 通用规则（所有 AI 必须遵守，已内嵌在每个指令块中）

1. **三层分治**：design_memo 只写 why（决策推理），不写 what is 的细节（当前状态由 battle_map + depgraph 维护），引用用稳定 path/blueprint_id（禁止 node_id/edge_id）
2. **文档规范**：遵循 `01_design_memo_management_spec §4`——frontmatter 字段集（ttl/doc_type/title/owner/language/status/version/date/topic/scope）、末尾必须有「修订记录」节、必须有「开放问题/待定问题/待裁定」等价节
3. **不破坏交叉引用**：含 `#L行号` 锚点的引用不得断裂；章节编号不强制统一；不为"结构统一"重排已有章节
4. **修订升版本**：改动后升 version（小改 1.x.0→1.x.1，大改→1.(x+1).0），修订记录补一行（日期+版本+改了什么+为什么改）
5. **过度工程红线（判定基准：system_charter §2 硬边界 + 施工方式）**：以 [system_charter.md §2 硬边界约束](../../04_architecture_principles_decisions/system_charter.md#L61-72) + 实际施工方式为唯一判定基准——①约束一人力：1 人全栈开发+AI 协作者，代码 100% AI 生成；②施工方式：1 人在 TRAE 编译器上用多 AI 多对话并发施工；③约束二硬件：单机 PC 工作站（i7-12700KF / RTX 3090 24GB 显存<90% / 64GB RAM / 30Mbps 网络），无集群/K8s；④约束三资金：个人资金双账户（实盘+QMT 模拟），miniQMT 10笔/秒、Tick=3秒；⑤约束四规则：T+1、涨跌停、融券受限、日频及以上根频率；⑥约束五运维：单机部署无热备家用环境，RTO<5分钟；⑦约束六范式：AI 生成代码需交叉验证+依赖锁定+自治熔断。凡是超出这些硬边界的机制/设计（需多人协作才能用、为团队协作而设计、需集群/多机/热备、需外部对接/文档交付、超出单机算力/显存/资金/运维能力）= 过度工程，一律从文档中去掉或降级；**远期工程不算过度工程**——已显式标注 P4/P5/远期愿景/待裁定的予以保留，但远期属性必须在文档中明确可见
6. **搜索约束**：WebSearch 限定 2026 年（尤其 2026-07/08），找最新研究/实践/开源实证；找到的更好算法登记到文档「考虑过的替代方案」或新增「前沿演进方向」节，不直接替换已定决策（已定决策修订需升版本+记理由）
7. **循环审查（含 git 提交闭环）**：每轮做完整闭环（回填→审查→搜索→调整→过度工程清理），发现的问题/缺失**更新修复后立即提交 git**（`git add <你修改的文件>` + `git commit`，提交信息注明本轮修复的问题/缺失，禁止 `--no-verify` 绕过门禁），提交后重新通读全文再查一轮；如此循环，直到**问题数量=0 且缺失功能/模块数量=0**（连续 1 轮零改动需求确认）= 任务完成
8. **不擅自定决策**：需人决策的开放问题标在「待定问题」节，AI 不替人拍板；已 active 的定稿决策如要推翻，必须升大版本+写推翻理由+标「待裁定」
9. **⚠️ Git 安全铁律（#ARCH-GIT-CLEAN-GUARD-FIX，2026-08-11 灾难教训）**：
   - **每轮修改后立即 `git add <你修改的文件>`**——staged 文件不会被 `git clean -fd` 删除。这是防止文件丢失的第一道防线，每完成一轮修改必须执行，不可跳过
   - **禁止执行以下危险命令**：`git clean`、`git clean -fd`、`git reset --hard`、`git checkout --`、`git restore`、`git stash`、`git checkout .`——这些命令会物理删除文件或丢弃修改，且 git alias 拦截在 Windows 上不生效（git 2.48.1 实测确认）
   - **如需清理工作区**：只能用 `git add` 把文件 staged，不能删除任何文件
   - **如需丢弃修改**：标在文档「开放问题」节等用户决策，不擅自用 git 命令丢弃
10. **⚠️ 文件锁使用（防止跨 AI 冲突）**：
    - **修改文件前先加锁**：`python scripts/lock_files.py acquire <file> <session_id>`——这会阻止其他 AI 同时修改同一文件
    - **完成修改后释放锁**：`python scripts/lock_files.py release <file> <session_id>`
    - **检查文件是否被锁**：`python scripts/lock_files.py check <file>`——返回 FREE 才能修改
    - **session_id 用法**：用你的 AI 编号（如 AI-01/AI-02）作为 session_id
    - **锁冲突时**：如果 check 返回 LOCKED，说明其他 AI 正在修改该文件，等待 5 分钟后重试，不要强制修改
11. **⚠️ 基础设施盘点（前置必做，所有 AI 第 1 轮的核心任务）**：
    - **为什么/目的**：连"项目里现在有什么"都不清楚，就无法判断该保留/修改/退役什么——目的链：先清楚有什么→才能知道怎么改→才能知道怎么更新→才能知道哪些需要删除/退役。
    - **做什么**：全面扫描项目代码和配置，找出与你的文档主题相关的**所有**已建设施、配套组件、规则指令，包括但不限于：
      - **代码模块**：`src/zephyr/` 下与文档主题相关的所有 Python 模块/类/函数（用 Glob + Grep 搜索关键词）
      - **配置文件**：`config/`、`tasks.yaml`、`business_data_categories.yaml`、`.env` 等相关配置
      - **Schema 定义**：`schemas/categories/` 下相关的 ClickHouse 表定义
      - **注册表条目**：`capability_canonical_file_registry.yaml`、`architecture_issue_registry.yaml` 等相关条目
      - **测试文件**：`tests/` 下相关测试覆盖情况
      - **脚本工具**：`scripts/` 下相关治理/运维脚本
      - **前端组件**：`frontend/` 下相关 dashboard/panel 组件
      - **治理规则**：`docs/01_policies_and_standards/` 下相关规则/契约/铁律
      - **其他文档引用**：design_memos 其他文档对本主题的引用（用 Grep 搜交叉引用）
    - **怎么写进文档**：在文档中新增或更新「已施工设施盘点」节（或在现有「背景」「现状」节中补充），按类别列出：
      | 类别 | 路径/位置 | 内容简述 | 状态（production/draft/deprecated） |
      确保读者从文档就能知道：这个功能在项目里有哪些设施、配套与规则指令。
    - **时机**：第 1 轮做，后续每轮审查发现新的相关设施即补充进盘点表。
12. **⚠️ proposed 议题查询（2026-08-11 新增，#ARCH-AIGOV-005 对抗式审查联动）**：
    - **AI 启动前 MUST 查询** `architecture_issue_registry.yaml` 中所有 `status=proposed` 的议题，特别是与本次任务相关的议题（如本次负责 35 号 drawdown，必查 #ARCH-RISK-001~005）
    - **proposed 议题是 AI 提议待用户确认的决策**（铁律#9），AI 不能自行标 `decided`/`resolved`，但可在文档中引用并按 proposed 议题的 `adjudication` 内容做施工预研
    - **2026-08-11 新登记 35 项 proposed 议题**（#ARCH-AIGOV-001~010 / AICOLLAB-001 / RISK-001~005 / QUANT-001~005 / REG-001~005 / ASHARE-001~002 / COMPLIANCE-001 / SDD-001 / AUDIT-001 / DRIFT-002 / EXEC-001 / CI-001 / REGCAN-001），详见 [00_index_trading_decision.md §9.1](00_index_trading_decision.md#91-2026-08-11-第一性原理调研发现的-35-项缺失议题全部-statusproposed)
    - **AI 完成任务后 MUST**：①在文档「开放问题」节列出本次相关的 proposed 议题（标注 status=proposed，等用户确认）；②在 architecture_issue_registry.yaml 对应议题的 `last_updated` 字段更新为本次审查日期

---

## 1. 23 个 AI 文档分配总表

### 常规审查 AI（AI-01 ~ AI-20，覆盖 44 篇文档）

| AI | 文档数 | 负责文档 | 合计行数 | 说明 |
|---|---|---|---|---|
| AI-01 | 1 | 62_business_registry_construction.md | 4317 | XL 独立 |
| AI-02 | 1 | 10_regime_detector_spec.md | 3263 | XL 独立 |
| AI-03 | 1 | 54_reconciliation_attribution.md | 2889 | XL 独立 |
| AI-04 | 1 | 63_data_utilization_audit.md | 2637 | XL 独立 |
| AI-05 | 1 | 35_drawdown_protocol_impl.md | 2456 | XL 独立 |
| AI-06 | 1 | 36_var_es_monitoring.md | 2080 | XL 独立 |
| AI-07 | 1 | 13_regime_phase3_engineering_plan.md | 1971 | L 独立 |
| AI-08 | 1 | 64_data_source_download_spec.md | 1659 | L 独立 |
| AI-09 | 2 | 40_execution_broker.md + 42_sell_flow.md | 1929 | L+M |
| AI-10 | 2 | 37_liquidity_crisis_protocol.md + 41_buy_flow.md | 1805 | L+M |
| AI-11 | 2 | 32_firm_risk_aggregator.md + 30_multi_strategy_concurrency.md | 1882 | L+M |
| AI-12 | 2 | 34_regime_meta_allocator.md + 00_index_trading_decision.md | 1792 | L+M |
| AI-13 | 2 | 26_event_driven_strategy_detail.md + 22_sector_rotation_spec.md | 1737 | L+M |
| AI-14 | 2 | 61_lifecycle_multi_ai.md + 53_simulation_live_path.md | 1827 | L+M |
| AI-15 | 2 | 14_regime_s2_diagnosis.md + 25_multifactor_strategy_detail.md | 1906 | M+M |
| AI-16 | 2 | 24_daban_strategy_detail.md + 11_regime_backtest_validation_plan.md | 1853 | M+M |
| AI-17 | 3 | 31_position_sizing.md + 18_cold_archive_build_plan.md + 12_regime_phase2_validation.md | 1802 | M+M+M |
| AI-18 | 5 | 21_stock_selection_engine.md + 51_panel_experiment_history_mlflow_retirement.md + 23_strategy_correlation_validation.md + 17_special_trading_days_data_assets.md + 50_backtest_observability_workplan.md | 1918 | M+S×3 |
| AI-19 | 6 | 20_first_batch_strategies.md + 19_northbound_hold_snapshot.md + 01_design_memo_management_spec.md + 28_sentiment_cycle_trading.md + 60_cross_cutting_cleanup.md + 65_git_safety_governance.md | 1386 | S×5+M |
| AI-20 | 7 | 33_budget_change_handler.md + 55_monitoring_review.md + 52_backtest_framework_docking.md + 15_data_feature_layer_spec.md + 27_second_batch_strategies.md + 16_technical_indicator_catalog.md + 16_technical_indicator_build_plan.md | 472 | 骨架×7 |

### 特殊讨论文档 AI（AI-21 ~ AI-22，覆盖 2 篇文档）

| AI | 文档数 | 负责文档 | 行数 | 说明 |
|---|---|---|---|---|
| AI-21 | 1 | 90_methodology_open_questions.md | 1068 | 特殊：深度调研+裁定+施工方案 |
| AI-22 | 1 | 91_density_prediction.md | 45 | 特殊：深度调研+裁定+施工方案 |

### 新增治理文档 AI（AI-23，覆盖 1 篇文档）

| AI | 文档数 | 负责文档 | 行数 | 说明 |
|---|---|---|---|---|
| AI-23 | 1 | 66_commit_queue_serialization.md | 260 | 新增治理 draft：提交队列串行化（决策备忘+施工计划），首版待审查裁定 |

> 合计：20 个常规 AI 覆盖 45 篇 + 2 个特殊 AI 覆盖 2 篇 + 1 个新增治理 AI 覆盖 1 篇 = 48 篇，23 个 AI，全覆盖。

---

## AI-01 指令（负责 62_business_registry_construction.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 1 篇文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\62_business_registry_construction.md（业务资产注册表体系施工总案，active v1.0.0）
【文档性质】这是 12 个业务资产注册表（因子/策略/技术指标/图形形态/股票池/基准/成本模型/执行算法/风控限额/数据资产/字段字典/实验）的施工总案 + 审查底稿 + 调查索引。P0 已完成 3/12（universe/benchmark/cost_model），P1 待施工 7/12，P2 待施工 2/12。文档已 active 但 P1/P2 大量待施工，需深度审查 schema 设计合理性 + 数据来源准确性 + 过度工程。文档超大（4317 行），需用 offset/limit 分段读或 Grep 定位章节。
【背景知识】
- 01 号规范：§4.1 段位编号制（6x=跨切治理，62 空号无冲突）；§4.4 施工总案类按"目标→现状→改动→验证→不做"组织
- 与 63 号配对：62 号建 12 注册表 schema，63 号盘点 101 张表实际利用率
- 与 15/16/20/22/24/25/26/27/32/35/36/37/40/51/52 号文档有交叉引用
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 用 Read offset/limit 分段读 62 号全文（每段 1500 行），或用 Grep 定位 H2 章节逐段读
2. 核验 P0 三件套已落盘 YAML：LS d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ 找 universe_registry.yaml / benchmark_registry.yaml / cost_model_registry.yaml，读其内容验证与 62 号 §5 登记是否一致
3. 读 registry_of_registries.yaml（tier_2 业务资产段）验证 3 个 P0 是否已登记 + entry_count 是否准确
4. 读 AGENTS.md（RULE-REGISTRY 段）验证业务资产速查是否已显化
5. 读 architecture_issue_registry.yaml #ARCH-BREG-001 验证施工进度登记
■ 第 2 轮：内容审查与回填
1. P0 三件套审查（已完成，查质量）：
   - §5.1 universe_registry：5 条登记是否覆盖项目所有股票池——反查 24/25/26 号文档是否有遗漏的池
   - §5.2 benchmark_registry：4 条是否足够——审查是否需补中证A500/万得全A
   - §5.3 cost_model_registry：万3佣金/千1印花税/1bp滑点参数是否符合 2026 A股实际费率；square_root 冲击模型参数是否校准
2. P1 七注册表 schema 审查（待施工，查设计）：
   - §6.1.1 factor_registry：factor_class 10 类（Barra 6 + A股特色 4）——反查 src/zephyr/factor/ 验证分类覆盖
   - §6.1.2 strategy_registry：strategy_class 6 类——反查 20/24/25/26/27/22 号
   - §6.1.3 technical_indicator_registry：5 大类 + 9 周期——反查 16 号文档 + src/zephyr/factor/technical_indicators/
   - §6.2.1 execution_algo_registry：6 算法——反查 40 号 + src/zephyr/ex_sor/
   - §6.2.2 risk_limit_registry：9 种限额——反查 35/36/37/32 号 + config/risk_register.yaml
   - §6.2.3 data_asset_registry：三实体（sources/datasets/jobs）——反查 dataflow_graph_registry.yaml + config/.env.qmt
   - §6.2.4 chart_pattern_registry：8 大类——反查 src/zephyr/factor/technical_indicators/ + signal_ashare/
■ 第 3 轮：缺失环节与算法审查
1. 通用 Schema 设计原则（§4 八条）审查：frontmatter 对齐/entry_schema DB 迁移预留/编号格式/状态机/半派生机制
2. 裁定审查（§8 八项核心裁定 + S1-S6 修正）：逐项审查裁定依据是否充分，S1-S6 修正是否已落实到各 schema
3. P2 两注册表审查：field_dictionary 范围裁定 / experiment_registry 施工时机
4. §10 数据来源映射表准确性——反查代码验证 code_path
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"feature registry 2026""factor catalog 2026"（对标 WorldQuant Alpha Bank / qlib Alpha158）
2. 搜"strategy registry 2026""strategy lifecycle management 2026"（对标 Numerai / QuantConnect）
3. 搜"technical indicator registry 2026"（对标 TA-Lib / backtrader）
4. 搜"chart pattern recognition 2026""risk limit registry 2026""data lineage 2026""experiment registry 2026""field dictionary 2026"
5. 搜"A-share trading cost 2026 佣金 印花税""market impact model calibration 2026"验证参数
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 12 个注册表是否对个人项目过多——能否合并（如 field_dictionary 并入 data_asset_registry）
2. YAML vs DB：现阶段 YAML 是否合理，还是直接上轻量 SQLite
3. data_asset_registry 三实体是否过重——个人项目是否需要 OpenLineage 级血缘
4. chart_pattern_registry 8 大类是否过多——MVP 是否只做 2-3 类
5. risk_limit_registry 9 种限额是否过多——个人系统 4 级回撤 + Kill Switch 是否够
6. variant 机制、性能指标字段（运行时可空）是否过度设计
7. §11 YAML→DB 迁移路径是否过早规划
■ 第 6 轮：一致性与交叉引用审查
1. 与 63 号配对一致性：62 号建 schema vs 63 号盘点表
2. 与 15/16 号一致性：factor_registry / technical_indicator_registry 与数据特征层/技术指标文档对齐
3. 与 20/24/25/26/27 号一致性：strategy_registry 覆盖所有已定义策略
4. 与 35/36/37/32 号一致性：risk_limit_registry 与风控限额文档对齐
5. 与 40 号一致性：execution_algo_registry 与执行层文档对齐
6. 与 51/52 号一致性：experiment_registry 与实验历史/回测框架对齐
■ 第 7 轮：文档质量与规范符合性
1. frontmatter：ttl/doc_type/title/owner/language/status/version/date/topic/scope 是否齐全合法
2. §4.4 施工总案类结构是否完整合理
3. 两条硬约束：有修订记录 + 有开放问题等价节
4. 交叉引用全用稳定 path（禁止 node_id/edge_id）
5. status=active v1.0.0——改动升 v1.1.0 小改 / v2.0.0 大改
■ 循环条件（含 git 提交闭环）
- 每轮结束后自检：本轮发现的问题是否全部修复？是否有新发现的问题？是否有新发现的缺失功能/模块？
- 若有未修复/新发现：更新修复 → 提交 git（`git add <你修改的文件>` + `git commit`，提交信息注明本轮修复的问题/缺失，禁止 `--no-verify` 绕过门禁）→ 进入下一轮审查
- 若本轮零发现零修复，再跑一轮确认——**问题数量=0 且缺失功能/模块数量=0**（连续两轮零发现），任务结束
- 升版本号在修订记录登记
■ 约束
- 只改 62 号本身，引用其他文档时只读不改
- P0 已完成三件套的 YAML 如需改，同步改 catalogs/ 下对应文件 + registry_of_registries.yaml + AGENTS.md
- 如发现其他文档需同步改，记在 62 号「待定问题」节，不越界改
- 不擅自定决策（如基准选择/费率校准/12表是否精简），标在「待定问题」节
- 引用代码用稳定 path
- 持续改进不停，循环至零问题
```
---

## AI-02 指令（负责 10_regime_detector_spec.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 1 篇文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\10_regime_detector_spec.md（regime 检测器 spec，active v1.3.1，3263 行超大文档）
【文档性质】这是已定稿的 regime 检测器 spec，12 态定稿，代码已施工。文档很大（3263 行，超 Read 128KB 限制，需用 offset/limit 分段读，或用 Grep 定位章节）。
【背景知识】
- 01 号规范：§4.1 段位编号制（1x=地基/数据特征，10 号属 regime 系列）；§4.4 spec 类按对象内在结构组织
- 与 11/12/13/14 号文档构成 regime 系列（检测器 spec→回测验证→Phase2 验证→Phase3 工程→S2 诊断）
- 34 号 RegimeMetaAllocator 依赖 10 号 regime 状态做参数分配
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 用 Read offset/limit 分段读全文（每段 1500 行），或用 Grep 定位 H2 章节逐段读
2. 读 src/zephyr/regime/ 下全部代码（LS src/zephyr/regime + 读 core/regime_detector.py / features/ / validation/）
3. 列出文档 frontmatter 的 status/version 确认当前版本
■ 第 2 轮：内容审查与回填
1. 把 src/zephyr/regime/ 已施工的算法（HMM 9态/12态、Shrinkage、overlay signals、synthetic VIX、walk-forward refit、Phase2 四验证器等）的 why 回填到文档
2. 审查 12 态定义、转换路径、触发确认信号、置信度更新规则、主线识别是否完整
3. 回填各章节的决策推理（why），确保 design_memo 只写 why 不写 what is
■ 第 3 轮：缺失环节与算法审查
1. 对照 12_regime_phase2_validation 的 A2/B1 FAIL 结果，文档是否已反映"模型需重设计"的后续
2. 12 态转换路径矩阵是否完整——有无遗漏的状态转换
3. overlay signals 的 NLP/资金/板块维度是否已施工，未施工的标注状态
4. synthetic VIX 构造方法的合理性
5. walk-forward refit 的窗口/频率参数是否已校准
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"regime detection HMM 2026""market state detection 2026""Gaussian HMM financial 2026""regime switching model 2026"
2. 搜"non-parametric regime detection 2026""deep learning regime 2026"
3. 搜"synthetic VIX construction 2026""volatility regime 2026"
4. 审查搜到的方法是否有比 12 态 HMM 更优的算法——如果有，登记到「考虑过的替代方案」或「前沿演进方向」节
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 12 态是否过多（个人系统）——6 态或 9 态是否够用
2. overlay signals 的 NLP/资金/板块维度是否过度——P2 待施工的是否应降级远期
3. walk-forward refit 的频率是否过重
4. 文档 3263 行是否应拆分（如验证部分拆到 11/12 号）
■ 第 6 轮：一致性与交叉引用审查
1. 与 11 号（回测验证方案）的一致性：验证结果是否已同步到 10 号
2. 与 12 号（Phase2 验证）的一致性：A2/B1 FAIL 后续是否对齐
3. 与 13 号（Phase3 工程）的一致性：降态/校准/NLP 是否对齐
4. 与 14 号（S2 诊断）的一致性：S2 算法错配根因是否在 10 号反映
5. 与 34 号（RegimeMetaAllocator）的一致性：12 态映射是否对齐
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 spec 类结构 / 双硬约束 / 稳定 path）
5. status=active v1.3.1——改动升 v1.4.0+
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 10 号本身，引用 11/12/13/14/34 号时只读不改
- 读取大文件用 offset/limit，不要一次性读
- 通用约束同首个指令块「约束」：需同步改他文档记 10 号开放问题节不越界改；不擅自定决策（如 12 态是否减态）标开放问题节；持续改进循环至零问题
```
---

## AI-03 指令（负责 54_reconciliation_attribution.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 1 篇文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\54_reconciliation_attribution.md（G25 对账归因，2889 行）
【文档性质】这是对账归因体系的设计文档，覆盖 PnL 归因分解、每日对账、归因维度、异常交易检测、报表生成。
【背景知识】
- 01 号规范：§4.1 段位编号制（5x=运营/对账，54 号属对账归因）；§4.4 文档种类适配
- 与 40 号（执行层）衔接：执行产出是对账输入
- 与 30 号（多策略并发）衔接：StrategyBook 独立 PnL 是归因基础
- 与 50 号（可观测性）衔接：日志/监控与对账数据互补
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 用 Read offset/limit 分段读 54 号全文
2. 读 battle_map_11_reconciliation.md 了解对账阶段现状
3. LS src/zephyr/ 找 reconciliation/attribution/pnl/reporting 相关代码
4. 读 02_domain_architecture_docs/ 找 reporting/audit 相关域文档
■ 第 2 轮：内容审查与回填
1. 回填已施工的对账/归因代码的 why——反查 src/zephyr/ 实际实现
2. 审查 PnL 归因分解方法（Brinson/Fama/Barra）的选型决策推理
3. 审查每日对账流程的完整性（交易对账/持仓对账/资金对账）
4. 审查归因维度设计（策略层/标层/因子层/时间层）
5. 审查异常交易检测规则
6. 审查报表生成机制
■ 第 3 轮：缺失环节与算法审查
1. PnL 归因分解是否覆盖所有收益来源（选股/择时/行业/风格/交互）
2. 对账差异容忍度/处理流程是否完整
3. 归因基准选择（沪深300/中证500/自定义）是否合理
4. T+1 约束下的对账时序是否正确
5. 异常交易检测的阈值/规则是否校准
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"PnL attribution 2026""Brinson attribution 2026""Barra factor attribution 2026"
2. 搜"reconciliation trading system 2026""trade ledger 2026"
3. 搜"performance attribution quantitative 2026""multi-strategy PnL decomposition 2026"
4. 搜"anomaly detection trading 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. Barra 归因是否对个人项目过重——是否只需简单的选股/择时二分法
2. 多维度归因（策略/标/因子/时间）是否过重
3. 报表生成是否需要自动化 dashboard 还是手动检查即可
4. 异常检测规则是否过多
■ 第 6 轮：一致性与交叉引用审查
1. 与 40 号（执行层）一致性：执行产出格式与对账输入是否对齐
2. 与 30 号（多策略并发）一致性：StrategyBook 独立 PnL 与归因对接
3. 与 50 号（可观测性）一致性：日志与对账数据互补关系
4. 与 55 号（监控复盘）一致性：对账结果驱动复盘
5. 与 62 号（注册表）一致性：对账相关数据资产登记
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 升版本号在修订记录登记
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 54 号本身，引用其他文档时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记 54 号开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-04 指令（负责 63_data_utilization_audit.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 1 篇文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\63_data_utilization_audit.md（业务数据资产利用率审查与施工计划，draft v0.1.0，2637 行）
【文档性质】这是业务数据库 101 张表在 design_memos 46 篇文档中的引用审查底稿 + 闲置清单 + 分批接入施工计划。与 62 号配对——62 号建 12 注册表 schema，63 号盘点 101 张表实际利用率（57.4% 已用 / 42.6% 闲置）。核心结论：43 张闲置表分 P0-P4 五档，三波分批接入。
【背景知识】
- 01 号规范：§4.1 段位编号制（6x=跨切治理）；§4.4 审查清单+施工计划混合种类
- 与 62 号强配对：62 号建 schema，63 号盘点表
- 数据消费方遍布全链：10(regime)/22(板块)/24/25(策略)/26(事件)/28(情绪)/32(firm风险)/35(回撤)/37(流动性)/50(可观测)/52(回测)
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 用 Read offset/limit 分段读 63 号全文（2637 行）
2. 核验 schemas/categories/：LS d:\ZephyrAlpha\schemas\categories\ 验证实际表数是否=101
3. 逐类核对 §4 八大类表清单是否与实际文件数一致
4. 反查 §5.2 热度前 15 名表的引用次数：用 Grep 在 design_memos/*.md 搜表名验证 hit count
5. 反查 §5.3 低频引用表是否真的仅 1-2 次
■ 第 2 轮：内容审查与回填
1. 利用率审查方法学审查（§3）：双层校验（英文表名+中文别名）是否严谨
2. §3.3 审查局限审查：
   - "tick 关键词过宽"——是否应改用精确正则 \btick\b
   - "只覆盖 design_memos 不含 src/ 代码引用"——是否应补查代码层引用
3. 补一轮代码层引用扫描：用 Grep src/zephyr/ 搜表名，把"文档闲置但代码在用"的表从闲置清单移除
4. 回填已施工的数据消费代码的 why
■ 第 3 轮：缺失环节与算法审查
1. 闲置表分档审查（§6，43 张 P0-P4）：
   - 🔴 P0 高价值 8 张：逐张验证价值判断是否成立（restricted_shares/block_trade_detail/cb_iv/etf_nav/edb_data 等）
   - 🟡 P1 跨市场 15 张：业务边界裁定项是否完整
   - 🟠 P2 元数据 8 张：注册表治理待登记是否合理
   - 🟢 P3 分钟级 12 张：后复权周/月线与 16 号三级时间框架栈不一致
   - ⚪ P4 待归档 5 张：归档理由是否充分
2. 三波施工计划审查（§7）：每波步骤是否可执行，验证标准是否够严
3. 与 12 注册表关联审查（§8）：data_asset_registry 首批 66 张表登记清单是否准确
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"data utilization audit 2026""data asset inventory 2026"
2. 搜"data lineage 2026""data catalog 2026"（对标 OpenLineage / Apache Atlas / Amundsen）
3. 搜"idle data archive 2026""data lifecycle management 2026"
4. 搜"alternative data alpha 2026"（限售解禁/大宗交易/可转债 IV 的 alpha 价值）
5. 搜"macro regime detection 2026"（EDB 宏观数据对 regime 的增量价值）
6. 搜"ETF arbitrage 2026""ETF premium discount 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 101 张表是否本身就过多——个人系统是否需要覆盖 A股/港股/美股/期货/期权/可转债全品类
2. 三波施工计划是否过重——是否应直接"归档为主，接入为辅"
3. data_asset_registry 首批 66 张登记是否过重——是否先登记 8 张 P0 + 58 张已用高频表
4. §3 双层校验 + 代码层补查是否过度
5. 第二波 5 个业务边界决策项是否都需人定——能否 AI 按个人项目定位直接裁定
■ 第 6 轮：一致性与交叉引用审查
1. 与 62 号一致性：data_asset_registry schema 与 63 号表盘点对齐
2. 与 10 号一致性：regime 数据源消费对齐
3. 与 15/16 号一致性：数据特征层/技术指标消费对齐
4. 与 22/24/25/26 号一致性：策略数据消费对齐
5. 与 35/37 号一致性：风控数据消费对齐
6. 与 50/52 号一致性：可观测性/回测数据消费对齐
7. 与 64 号一致性："数据下得怎么样"vs"数据用得怎么样"互补不重叠
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 审查清单+施工计划混合种类结构 / 双硬约束 / 交叉引用稳定 path——schemas/categories/xxx.py）
5. status=draft v0.1.0——审查后若数据准确+计划可行→升 active 1.0.0；若需大改保持 draft 升 0.2.0
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 63 号本身，引用其他文档时只读不改
- 引用表/代码用稳定 path
- 通用约束同首个指令块「约束」：需同步改他文档（如 P0 表接入需改 26/35/37/10/32 号的数据源节）记 63 号 §10 开放问题不越界改；不擅自定决策（业务边界扩张/归档确认）标 §10 开放问题——但明显可建议的（如生猪期货归档），AI 给默认建议；持续改进循环至零问题
```
---

## AI-05 指令（负责 35_drawdown_protocol_impl.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 1 篇文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\35_drawdown_protocol_impl.md（G16 回撤 Protocol 落地，2456 行）
【文档性质】这是回撤 Protocol 的落地实施文档，覆盖四级回撤阈值（8/15/20/25%）+ 恢复机制 + 分层风控 + Kill Switch。
【背景知识】
- 01 号规范：§4.1 段位编号制（3x=风控/仓位，35 号属回撤 Protocol）；§4.4 文档种类适配
- 与 30 号（多策略并发）衔接：§2.5 定义了四级回撤阈值 + Kill Switch
- 与 36 号（VaR/ES）衔接：风控指标协同
- 与 37 号（流动性危机）衔接：Kill Switch 流动性危机触发
- 与 32 号（FirmRiskAggregator）衔接：firm 层风控联动
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 用 Read offset/limit 分段读 35 号全文（2456 行）
2. 读 30_multi_strategy §2.5（四级回撤阈值 + Kill Switch 定义）
3. LS src/zephyr/risk/ + position/ 找 drawdown/kill_switch 相关代码
4. 读 battle_map_09_risk_control.md（14万字风控 battle map）
5. 读 02_domain_architecture_docs/66_d_risk.md（D_RISK 域模块）
■ 第 2 轮：内容审查与回填
1. 回填已施工的回撤 Protocol 代码的 why——反查 src/zephyr/risk/ 实际实现
2. 审查四级阈值落到 StrategyBook 的机制
3. 审查单策略 vs 组合分层逻辑
4. 审查恢复机制（分级恢复/全面恢复/条件恢复）
5. 审查 Kill Switch 触发与执行逻辑
6. 审查日度熔断机制
7. 审查 Kill Switch 不可覆盖的设计
8. 审查回撤基准净值口径
9. 审查与 regime Shrinkage 协同
■ 第 3 轮：缺失环节与算法审查
1. 四级阈值（8/15/20/25%）的参数校准依据是否充分
2. 恢复机制的触发条件/等待期/验证期是否完整
3. Kill Switch 的触发条件（回撤/流动性/系统故障）是否覆盖全面
4. 分层风控（策略层/firm 层/组合层）的职责边界是否清晰
5. T+1 约束下的回撤处理时序是否正确
6. 回撤期间的仓位管理（封锁新仓/仅平仓/按比例裁剪）是否完整
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"drawdown protocol 2026""max drawdown control 2026"
2. 搜"kill switch trading 2026""circuit breaker trading 2026"
3. 搜"recovery protocol trading 2026""de-risking strategy 2026"
4. 搜"multi-level risk control 2026""portfolio drawdown management 2026"
5. 搜"Calmar ratio 2026""MAR ratio 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 四级阈值 + 日度熔断 + Kill Switch 是否过重——个人系统是否只需 2 级 + Kill Switch
2. 分层风控（策略/firm/组合三层）是否过重
3. 恢复机制的多阶段设计是否过度
4. Kill Switch 的多维度触发是否过重
■ 第 6 轮：一致性与交叉引用审查
1. 与 30 号一致性：§2.5 定义与 35 号落地是否对齐
2. 与 36 号一致性：回撤 vs VaR/ES 的协同/优先级
3. 与 37 号一致性：Kill Switch 流动性危机触发与 37 号衔接
4. 与 32 号一致性：firm 层风控与回撤 Protocol 联动
5. 与 31 号一致性：仓位算法与回撤裁剪的接口
6. 与 42 号一致性：卖出流与回撤 Protocol 联动
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 升版本号在修订记录登记
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 35 号本身，引用 30/36/37/32/31/42 号时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记 35 号开放问题节不越界改；不擅自定决策（如阈值调整/层级精简）标开放问题节；持续改进循环至零问题
```
---

## AI-06 指令（负责 36_var_es_monitoring.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 1 篇文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\36_var_es_monitoring.md（G17 VaR/ES 与波动率监控，2080 行）
【文档性质】这是 VaR/ES 风险指标与波动率监控的设计文档，覆盖 VaR_95/ES_95 计算、入场基准、触发动作、30 日波动率调整、与回撤 Protocol 协同。
【背景知识】
- 01 号规范：§4.1 段位编号制（3x=风控/仓位，36 号属 VaR/ES 监控）；§4.4 文档种类适配
- 与 30 号（多策略并发）衔接：§2.5.4 定义了 VaR_95/ES_95/波动率调整
- 与 35 号（回撤 Protocol）衔接：风控指标协同
- 与 37 号（流动性危机）衔接：风险监控互补
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 用 Read offset/limit 分段读 36 号全文（2080 行）
2. 读 30_multi_strategy §2.5.4（VaR_95/ES_95/波动率调整定义）
3. LS src/zephyr/risk/ 找 var/es/volatility 相关代码
4. 读 02_domain_architecture_docs/66_d_risk.md（D_RISK 域模块）
■ 第 2 轮：内容审查与回填
1. 回填已施工的 VaR/ES 计算代码的 why——反查 src/zephyr/risk/ 实际实现
2. 审查 VaR_95 计算方法（历史模拟法/参数法/蒙特卡洛）的选型决策
3. 审查 ES_95（Expected Shortfall）计算方法
4. 审查入场基准（VaR/ES 阈值设定）
5. 审查触发动作（仓位调整/止损/预警）
6. 审查 30 日波动率调整机制
7. 审查数据窗口选择
8. 审查与回撤 Protocol 协同逻辑
■ 第 3 轮：缺失环节与算法审查
1. VaR 计算方法选型是否有充分的对比分析
2. ES 的后验测试（backtesting）是否设计
3. 波动率调整的频率/参数是否校准
4. VaR/ES 与回撤 Protocol 的优先级/协同是否清晰
5. 极端市场条件下的 VaR/ES 失效问题是否讨论
6. T+1 约束下的 VaR/ES 时序是否正确
7. 数据窗口长度对 VaR/ES 稳定性的影响
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"VaR ES monitoring 2026""expected shortfall 2026"
2. 搜"historical simulation VaR 2026""parametric VaR 2026"
3. 搜"volatility adjusted position 2026""volatility scaling 2026"
4. 搜"VaR backtesting 2026""ES backtesting 2026"
5. 搜"FRTB expected shortfall 2026"（巴塞尔 FRTB 框架最新进展）
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. VaR/ES 对个人系统是否过重——可降级远期？
2. 历史模拟法 vs 参数法——个人项目是否只需简单参数法
3. 30 日波动率调整是否需要——个人系统小资金容量小
4. VaR/ES 的多维度计算（策略/标的/组合）是否过重
5. 后验测试框架是否过度
■ 第 6 轮：一致性与交叉引用审查
1. 与 30 号一致性：§2.5.4 定义与 36 号落地是否对齐
2. 与 35 号一致性：VaR/ES vs 回撤 Protocol 协同/优先级
3. 与 37 号一致性：VaR/ES vs 流动性危机监控互补
4. 与 32 号一致性：firm 层风控与 VaR/ES 联动
5. 与 31 号一致性：仓位算法与 VaR/ES 调整接口
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 升版本号在修订记录登记
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 36 号本身，引用 30/35/37/32/31 号时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记 36 号开放问题节不越界改；不擅自定决策（如 VaR 计算方法选型/降级远期）标开放问题节；持续改进循环至零问题
```
---

## AI-07 指令（负责 13_regime_phase3_engineering_plan.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 1 篇文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\13_regime_phase3_engineering_plan.md（Phase 3 工程规划，draft，1971 行）
【文档性质】这是 regime 检测器 Phase 3 的工程规划，覆盖降态（9→6）、校准器设计、NLP 管道、S2/T3 触发逻辑。
【背景知识】
- 01 号规范：§4.1 段位编号制（1x=地基/数据特征，13 号属 regime Phase3 工程）；§4.4 施工计划类
- 与 10 号（regime spec）衔接：Phase 3 是 10 号的实施工程规划
- 与 11 号（回测验证）衔接：Phase 1-5 验证体系的 Phase 3
- 与 12 号（Phase2 验证）衔接：A2/B1 FAIL 后的修复方向
- 与 14 号（S2 诊断）衔接：S2 算法错配的修复方案
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 用 Read offset/limit 分段读 13 号全文（1971 行）
2. 读 src/zephyr/regime/（降态/校准/NLP/S2/T3 相关代码）
3. 读 10 号 regime spec 相关章节
4. 读 12 号 Phase2 验证的 A2/B1 FAIL 结果
■ 第 2 轮：内容审查与回填
1. 回填 Phase 3 的降态（9→6）、校准器、NLP 管道、S2/T3 触发逻辑的已施工部分 why
2. 审查 §2.1 降维裁定的决策推理
3. 审查 §2.2 校准器设计的完整性
4. 审查 NLP 管道的接入方案
5. 审查 S2/T3 触发逻辑的参数设计
■ 第 3 轮：缺失环节与算法审查
1. 降态（9→6）的映射规则是否完整——哪些态合并/删除
2. 校准器（isotonic/Platt/temperature scaling）的选型依据
3. NLP 管道的数据源/模型/延迟是否可行
4. S2/T3 触发逻辑与 12 号 A2/B1 FAIL 的修复方案是否对齐
5. Phase 3 各子项的优先级/依赖关系是否清晰
6. 从 draft → active 的条件是否满足
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"HMM state reduction 2026""regime state merging 2026"
2. 搜"probability calibration isotonic 2026""Platt scaling 2026""temperature scaling 2026"
3. 搜"NLP financial sentiment 2026""financial BERT 2026"
4. 搜"crisis recovery detection 2026""market bottom identification 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. NLP 管道/资金板块数据管道是否对个人项目过重——是否应降级远期
2. 降态 9→6 是否必要——还是直接保持 12 态
3. 校准器的三种方法是否都需实现
4. S2/T3 的多维度触发是否过重
■ 第 6 轮：一致性与交叉引用审查
1. 与 10 号一致性：Phase 3 规划与 regime spec 对齐
2. 与 11 号一致性：Phase 3 与回测验证体系对齐
3. 与 12 号一致性：A2/B1 FAIL 修复方向对齐
4. 与 14 号一致性：S2 诊断与 Phase 3 S2 修复对齐
5. 与 34 号一致性：降态后 RegimeMetaAllocator 参数映射是否需更新
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 施工计划类结构：目标→现状→改动→验证→不做 / 双硬约束 / 稳定 path）
5. status=draft——从 draft → active（如已施工完整）或保持 draft 补全
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 13 号本身，引用 10/11/12/14/34 号时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记 13 号开放问题节不越界改；不擅自定决策（如降态方案/NLP 是否降级远期）标开放问题节；持续改进循环至零问题
```
---

## AI-08 指令（负责 64_data_source_download_spec.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 1 篇文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\64_data_source_download_spec.md（数据源与下载体系规范，draft v1.2.1，1659 行）
【文档性质】这是 D_DATA 域数据获取基础设施的 spec，覆盖 Provider 体系/调度/落库/韧性/数据缺口治理。15 号偏"数据进来后怎么用"（PIT/特征仓库/因子工程），64 号偏"数据怎么进来"（Provider/调度/落库/韧性），互补不重叠。
【背景知识】
- 01 号规范：§4.1 段位编号制（6x=跨切治理，64 空号无冲突）；§4.4 spec 类按对象内在结构组织
- 与 15 号互补：64 号"数据怎么进来" vs 15 号"数据进来后怎么用"
- 与 63 号配套：64 号"数据下得怎么样" vs 63 号"数据用得怎么样"
- 与 17/18/19 号衔接：#ARCH-DATA-001/002 修复 / 冷归档策略 / 北向数据断档
- related_issues：#ARCH-IFIND-FAILOVER / #ARCH-CH-001~005 / #ARCH-CH-022 / #ARCH-CH-024 / #ARCH-CH-029 / #ARCH-DATA-001 / #ARCH-REALTIME-ACCUM / #ARCH-DATA-014 / #ARCH-SPECIAL-DAYS / #ARCH-EDB-EXPAND
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 用 Read offset/limit 分段读 64 号全文（1659 行）
2. 核验 §3-§10 八个对象分节：数据源 Provider 体系 / 下载调度 / ClickHouse 落库 / 数据质量校验 / 韧性与容错 / 数据缺口治理 / 实时行情 / 宏观数据
3. 核验 depends_on 和 related_issues 的 path 是否正确
4. 读 11_d_data.md（D_DATA 域 183 模块）了解已施工模块清单
■ 第 2 轮：内容审查与回填
1. Provider 体系审查：反查 src/zephyr/data/ 的 provider_base.py / akshare_provider.py / tushare_provider.py / baostock_provider.py / tickflow_provider.py / tdx_provider.py / internal_compute_provider.py
2. #ARCH-CH-022 CapabilityContract 审查：四字段（supports_symbols_null/supports_incremental/supports_full_refresh/requires_date_range）是否够用
3. #ARCH-IFIND-FAILOVER iFind 降级审查：fallback 链是否完整
4. #ARCH-DATA-014 L2 行情权限缺失审查：降级方案是否影响策略信号质量
5. 下载调度审查：5 档时段全量调度是否合理——反查 tasks.yaml
6. #ARCH-CH-001~005 ClickHouse 写入五项裁定审查
7. #ARCH-CH-029 known_data_gaps 审查：反查 known_data_gaps.yaml
■ 第 3 轮：缺失环节与算法审查
1. Provider capability 与 tasks.yaml 的一致性——反查 task_id→source 映射
2. 韧性设计（Provider 级 fallback / 重试 / 超时 / 断线重连）是否完整
3. 数据质量校验（integrity_checker / cross_source_validator）实现状态
4. #ARCH-EDB-EXPAND EDB 宏观数据扩展接入计划
5. #ARCH-REALTIME-ACCUM 时间敏感型数据每日积累机制
6. 与 17 号 #ARCH-DATA-002 治本方案（capability 语义校验）的衔接
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"akshare 2026 latest version""tushare 2026 API update"
2. 搜"financial data provider comparison 2026"（akshare/tushare/baostock/Wind/iFind/同花顺）
3. 搜"ClickHouse data ingestion best practice 2026"
4. 搜"data pipeline resilience pattern 2026"
5. 搜"financial data quality validation 2026"
6. 搜"A-share alternative data 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. Provider 抽象层是否过度——个人项目是否需要 8 个 Provider，能否精简到 3-4 个
2. CapabilityContract 四字段是否过度——个人项目是否需要正式契约
3. 5 档调度是否过度——个人项目是否需要 monthly_static + weekly + daily_static + daily_event + realtime 五档
4. known_data_gaps 注册表是否过度
5. cross_source_validator 是否过度（tick_data 专属）
6. #ARCH-DATA-002 治本方案 5 个施工项是否对个人项目过重
■ 第 6 轮：一致性与交叉引用审查
1. 与 15 号一致性："数据怎么进来" vs "数据进来后怎么用"边界是否清晰
2. 与 63 号一致性："数据下得怎么样" vs "数据用得怎么样"是否互补不重叠
3. 与 17 号一致性：#ARCH-DATA-001/002 / #ARCH-SPECIAL-DAYS 是否正确引用
4. 与 18 号一致性：冷归档策略与数据保留策略是否对齐
5. 与 19 号一致性：北向数据断档治理 / known_data_gaps 是否登记
6. 与 architecture_issue_registry.yaml 一致性：10 个 related_issues ARCH 编号是否存在且状态一致
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 十字段+depends_on/related_issues 齐全合法 / §4.4 spec 类按对象内在结构组织 / 双硬约束 / 稳定 path）
5. status=draft v1.2.1——审查后若内容完整可建议升 active
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 64 号本身，引用 15/17/18/19/63 号及 architecture_issue_registry 时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记 64 号开放问题节不越界改；不擅自定决策（如 Provider 精简/调度档位调整）标开放问题节；持续改进循环至零问题
```
---

## AI-09 指令（负责 40_execution_broker.md + 42_sell_flow.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\40_execution_broker.md（执行层下单对接，active v1.0.0，代码已施工，1269 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\42_sell_flow.md（G20 卖出流 spec，骨架 0.1.0，660 行）
【背景知识】
- 40 号与 42 号衔接：执行层是卖出流的落地通道
- 与 30 号（多策略并发）衔接：Kill Switch 流动性危机
- 与 35 号（回撤 Protocol）衔接：卖出流与回撤联动
- 与 28 号（情绪周期）衔接：退潮卖出
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读 40 号全文 + 读 42 号全文
2. 读 src/zephyr/ex_core/ + ex_sor/（LS + 读核心下单/撮合/滑点代码）
3. 读 02_domain_architecture_docs/44_d_ex_core.md（43 模块）+ 45_d_ex_sor.md（18 模块）
4. 读 battle_map_10_execution.md + battle_map_07_sell_flow.md
5. 读 src/zephyr/sell_decision/（LS + 02_domain_architecture_docs/68_d_sell_decision.md 25 模块）
■ 第 2 轮：内容审查与回填
1. 40 号——回填 19 项决策的已施工代码实现 why（miniQMT 接口/撮合/TWAP/VWAP/滑点/成本/订单状态机/失败重试/执行风控/集合竞价）
2. 40 号——审查 §7 降级/重构项是否已落地；滑点模型/成本模型参数是否校准
3. 42 号——⚠️ 这是骨架文档（660 行但大量待回填），重点回填已施工卖出逻辑的 why：
   - 卖出时序（T+1 约束下的卖出时序）
   - 止损触发（固定%/移动/ATR）
   - 止盈逻辑
   - 情绪退潮卖出（与 28 号衔接）
   - 破位卖出
   - 分批卖出
   - T+1 卖出约束
   - 与回撤 Protocol 联动（与 35 号衔接）
4. 42 号——把骨架填成 active：补全各章节决策推理
■ 第 3 轮：缺失环节与算法审查
1. 40 号——TWAP/VWAP/IS 三种执行算法的参数/适用场景是否完整
2. 40 号——miniQMT 接口契约的异常处理是否覆盖
3. 42 号——止损/止盈/破位/分批四种卖出逻辑的触发优先级是否清晰
4. 42 号——卖出信号与持仓状态的交互是否完整
5. 42 号——T+1 约束下的卖出时序（当日买入不可卖）是否正确处理
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"execution algorithm TWAP VWAP 2026""market impact model 2026""Almgren Chriss 2026"
2. 搜"miniQMT API 2026""QMT 迅投 接口 2026"
3. 搜"sell flow protocol 2026""stop loss ATR 2026""trailing stop 2026"
4. 搜"O'Neil sell rules 2026""profit taking strategy 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 40 号——TWAP/VWAP/IS 三种算法是否都需要——个人项目小资金是否只需 TWAP
2. 40 号——滑点模型/成本模型的复杂度是否过重
3. 42 号——止损/止盈/破位/分批四种是否全需要——个人项目是否只需 2 种
4. 42 号——分批卖出的复杂度是否过重
■ 第 6 轮：一致性与交叉引用审查
1. 40 号与 42 号一致性：执行层接口与卖出流对接
2. 与 30 号一致性：Kill Switch 流动性危机与执行层
3. 与 35 号一致性：回撤 Protocol 与卖出流联动
4. 与 28 号一致性：情绪退潮卖出
5. 与 41 号一致性：买入流与卖出流的对称性
6. 与 54 号一致性：执行产出与对账归因
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 40 号 active 改动升版本；42 号骨架→active 1.0.0
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 40/42 号本身，引用其他文档时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-10 指令（负责 37_liquidity_crisis_protocol.md + 41_buy_flow.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\37_liquidity_crisis_protocol.md（G18 流动性危机处理，骨架 0.1.0，1253 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\41_buy_flow.md（G19 买入流 spec，骨架 0.1.0，552 行）
【背景知识】
- 37 号与 30 号衔接：§2.5.5 Kill Switch 流动性危机（买卖价差>5x 停开仓）
- 37 号与 35 号衔接：风险 Protocol 协同
- 41 号与 22 号衔接：买入优先级依赖板块回踩质量 A/B/C
- 41 号与 31 号衔接：仓位算法
- 41 号与 35 号衔接：风控
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读 37 号全文 + 读 41 号全文
2. 读 30_multi_strategy §2.5.5（Kill Switch 流动性危机）
3. LS src/zephyr/risk/ 找 liquidity/spread 相关代码
4. 读 battle_map_09_risk_control.md + battle_map_06_buy_flow.md
5. 读 22_sector_rotation（板块回踩）+ 31_position_sizing（仓位）+ 35_drawdown（风控）
■ 第 2 轮：内容审查与回填
1. 37 号——⚠️ 回填已施工的流动性监控代码的 why（非"审查现有内容"，而是"回填已施工代码的 why"）：
   - 买卖价差监控机制
   - 流动性危机→停开仓仅平仓逻辑
   - 流动性指标定义（价差倍数/深度/成交量）
   - 与 Kill Switch 关系
   - A 股涨跌停流动性失效场景
2. 41 号——⚠️ 回填已施工的买入流代码的 why：
   - 分批建仓逻辑
   - 突破失败降级处理
   - 买入时序（盘中/尾盘/集合竞价）
   - 买入价格锚定
   - 资金分配到多标的
   - 与 budget 协同
   - T+1 约束（当日买入不可卖）
3. 两篇骨架文档都需填成 active：补全各章节决策推理
■ 第 3 轮：缺失环节与算法审查
1. 37 号——流动性指标的阈值/参数是否校准
2. 37 号——流动性危机的分级响应是否完整
3. 41 号——分批建仓 A/B/C 依赖板块回踩质量的逻辑是否完整
4. 41 号——买入时序与 miniQMT 接口的对接是否正确
5. 41 号——资金分配到多标的的优先级算法
6. 两篇——T+1 约束的时序处理是否正确
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"liquidity crisis protocol 2026""bid-ask spread monitoring 2026"
2. 搜"A-share limit-up liquidity 2026""涨跌停 流动性 2026"
3. 搜"buy flow protocol 2026""scaling in position 2026"
4. 搜"Wyckoff accumulation 2026""分批建仓 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 37 号——流动性监控是否对个人系统过重（小资金容量小，流动性几乎不是问题）
2. 41 号——分批建仓 A/B/C 依赖是否过重
3. 41 号——买入时序的多场景是否过多
■ 第 6 轮：一致性与交叉引用审查
1. 37 号与 30 号一致性：Kill Switch 流动性危机定义对齐
2. 37 号与 35 号一致性：风险 Protocol 协同
3. 37 号与 36 号一致性：VaR/ES 与流动性监控互补
4. 41 号与 22 号一致性：板块回踩质量 A/B/C
5. 41 号与 31 号一致性：仓位算法接口
6. 41 号与 35 号一致性：风控门控
7. 41 号与 42 号一致性：买入流与卖出流对称性
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 骨架→active 1.0.0
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 37/41 号本身，引用其他文档时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-11 指令（负责 32_firm_risk_aggregator.md + 30_multi_strategy_concurrency.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\32_firm_risk_aggregator.md（G13 FirmRiskAggregator 逻辑，骨架 0.1.0，1232 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\30_multi_strategy_concurrency.md（多策略并发架构总纲，active v1.3.3，650 行）
【背景知识】
- 30 号是多策略并发架构总纲，定义三模块（StrategyBook/FirmRiskAggregator/RegimeMetaAllocator）+ 三级升级 + 回撤 Protocol
- 32 号是 30 号 §2.2 的 FirmRiskAggregator 子文档
- 与 31/33/34 号构成仓位风控体系
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读 32 号全文 + 读 30 号全文
2. 读 src/zephyr/position/core/firm_risk_aggregator.py（MOD-POS-021）+ src/zephyr/pf_core/ + pf_alloc/ + position/
3. 读 battle_map_08_position_management.md
4. 读 02_domain_architecture_docs/64_d_position.md（D_POSITION 28 模块）
■ 第 2 轮：内容审查与回填
1. 30 号——回填 §2.2 三模块、§2.4 三级升级、§2.5 回撤 Protocol 的已施工部分 why 补全
2. 30 号——审查 §4.3 pod 误标是否已修正；§5 待裁定 6 项是否需更新；§7.4 开源实证是否需补充 2026 新实证
3. 32 号——⚠️ 回填已施工的 FirmRiskAggregator 代码的 why：
   - 按标的求和（自然叠加）
   - 单票硬上限裁剪
   - 行业/总仓位硬约束
   - 冲突标的处理
   - 不做 MVO 的决策推理
   - 输出 firm_target_portfolio 契约
   - O(N) 复杂度
4. 32 号——把骨架填成 active
■ 第 3 轮：缺失环节与算法审查
1. 30 号——三模块的接口契约是否完整
2. 30 号——三级升级（Tier1/2/3）的触发条件/执行逻辑是否完整
3. 32 号——单票硬上限 8% 的参数校准依据
4. 32 号——行业/总仓位硬约束的阈值是否合理
5. 32 号——冲突标的处理规则是否覆盖所有场景
6. 32 号——不做 MVO 的决策推理是否充分
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"multi-strategy portfolio 2026""independent book aggregation 2026"
2. 搜"risk parity throttle 2026""pod vs unified framework 2026"
3. 搜"firm risk aggregator 2026""portfolio hard limit 2026"
4. 搜"position aggregation 2026""multi-strategy capital allocation 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 30 号——§2.5.4 VaR/ES、§2.5.5 Kill Switch 是否对个人项目过重
2. 32 号——行业/总仓位硬约束是否过重
3. 32 号——不做 MVO 是否正确——还是个人项目可以更简单（直接按比例）
4. 30 号——三模块 + 三级升级是否过重
■ 第 6 轮：一致性与交叉引用审查
1. 32 号与 30 号一致性：§2.2 定义与 32 号落地对齐
2. 与 31 号一致性：仓位算法与 FirmRiskAggregator 接口
3. 与 33 号一致性：BudgetChangeHandler 三级升级
4. 与 34 号一致性：RegimeMetaAllocator 参数分配
5. 与 35 号一致性：回撤 Protocol 联动
6. 与 54 号一致性：StrategyBook 独立 PnL
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 30 号 active 改动升 v1.4.0+；32 号骨架→active 1.0.0
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 32/30 号本身，引用其他文档时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-12 指令（负责 34_regime_meta_allocator.md + 00_index_trading_decision.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\34_regime_meta_allocator.md（G15 RegimeMetaAllocator 参数，骨架 0.1.0，⚠️等 C1，1094 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\00_index_trading_decision.md（总索引+路线图，active v2.4.0，698 行）
【背景知识】
- 34 号与 30 号衔接：§2.2 分配公式 Base×Performance×Shrinkage
- 34 号与 11 号衔接：C1 验证结果（已通过 commit 852457e9）
- 34 号与 10 号衔接：12 态 regime 映射
- 00 号是 07_trading_decision_architecture 域的总索引+路线图（G01-G28 主题组），不是骨架，是已定稿的导航文档
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读 34 号全文 + 读 00 号全文
2. 读 30_multi_strategy §2.2（分配公式 Base×Performance×Shrinkage）
3. 读 src/zephyr/pf_alloc/core/regime_meta_allocator.py（MOD-PA-007）
4. 读 11_regime_backtest C1 验证结果（已通过）
5. 列出 design_memos 目录全部 46 篇的当前 frontmatter status/version（用 LS + Grep frontmatter）
■ 第 2 轮：内容审查与回填
1. 34 号——⚠️ 前置门槛：参数须等 C1 验证通过 + 首批策略 PnL。C1 已通过（commit 852457e9），但策略 PnL 未有。回填框架 why，参数标"待策略 track record 后校准"
2. 34 号——回填讨论要点 7 项：分配公式、Base 先验、PerformanceScore 60日 Sharpe 映射、Shrinkage 四档、floor/cap、稀有态差异化、第二阶段时机
3. 00 号——§0 目录表的 46 篇状态是否与各文档 frontmatter 实际 status/version 一致
4. 00 号——§3 主题组 G01-G28 的"状态"列是否与对应文档实际状态一致
5. 00 号——§7.3 占用表的认领状态是否最新
6. 00 号——§9 开放问题汇总的"决策状态"是否与各文档实际一致
■ 第 3 轮：缺失环节与算法审查
1. 34 号——分配公式 Base×Performance×Shrinkage 的参数设计是否完整
2. 34 号——Shrinkage 四档的阈值是否合理
3. 34 号——floor/cap 的参数设置
4. 34 号——稀有态差异化的逻辑
5. 00 号——G01-G28 主题组是否覆盖赚钱全流程所有环节
6. 00 号——对照 battle_map_01~12 的 12 个阶段，是否每个阶段都有对应 G 主题组
7. 00 号——对照 src/zephyr/ 下已施工的 domain，是否有关键已施工模块没被任何 G 主题组覆盖
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"regime meta allocation 2026""dynamic capital allocation 2026"
2. 搜"performance score shrinkage 2026""Kelly criterion allocation 2026"
3. 搜"quantitative trading system architecture 2026""multi-strategy portfolio framework 2026"
4. 搜"algorithmic trading decision pipeline 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 34 号——四档 Shrinkage 是否过细——个人项目是否只需 2 档
2. 34 号——PerformanceScore 60 日 Sharpe 映射是否过重
3. 00 号——§5 的 3 条并行轨道、§7 多 AI 分工指南是否对个人项目过重
4. 00 号——多 AI 协作流程是否需要简化
■ 第 6 轮：一致性与交叉引用审查
1. 34 号与 30 号一致性：§2.2 分配公式对齐
2. 34 号与 10 号一致性：12 态映射对齐
3. 34 号与 11 号一致性：C1 验证结果对齐
4. 00 号——§0 目录表的 46 篇交叉引用链接是否完整不断裂
5. 00 号——§4 依赖关系图是否准确反映当前依赖
6. 00 号——§10 改名对照表是否有遗漏
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 34 号保持 draft（参数未校准）或填框架→active 标参数待定；00 号 active 改动升 v2.5.0+
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 34/00 号本身，引用其他文档时只读不改
- 00 号是索引文档，不写施工算法细节，只维护导航准确性
- 不擅自新增/删除 G 主题组（需人决策的标在 §9 开放问题）
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-13 指令（负责 26_event_driven_strategy_detail.md + 22_sector_rotation_spec.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\26_event_driven_strategy_detail.md（G10 事件驱动策略细节，骨架 0.1.0，1030 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\22_sector_rotation_spec.md（G06 板块轮动 spec，骨架 0.1.0，707 行）
【背景知识】
- 26 号与 20 号衔接：首批 3 策略之一
- 22 号与 20 号衔接：§2.5 差异化矩阵
- 与 30 号衔接：多策略并发架构
- 与 23 号衔接：策略间相关性验证
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读 26 号全文 + 读 22 号全文
2. 读 battle_map_05_stock_selection.md（BM-SEL-27 盘中实时事件处理 / BM-SEL-08 板块强度 460 板块 / BM-SEL-09 调整周期追踪）
3. LS src/zephyr/ 找 event/news/sentiment/announcement/sector/rotation/plate 相关
4. 读 02_domain_architecture_docs/09_d_alt_data.md（另类数据）
■ 第 2 轮：内容审查与回填
1. 26 号——⚠️ 回填已施工的事件驱动策略代码的 why（非"审查现有内容"，而是"回填已施工代码的 why"）：
   - 事件源（公告/新闻/龙虎榜/异动）
   - 事件分类
   - 事件冲击衰减曲线
   - 事件→选股映射
   - 事件换手率
   - news_data 多源情绪
2. 22 号——⚠️ 回填已施工的板块轮动代码的 why：
   - 板块强度算法（460 板块 880xxx K线）
   - 回踩质量 A/B/C
   - 调整周期追踪
   - 轮动序列
   - 虹吸态
   - 板块资金流
   - 板块→个股传导
3. 两篇骨架文档都需填成 active
■ 第 3 轮：缺失环节与算法审查
1. 26 号——事件冲击衰减曲线的模型（Hawkes process / exponential decay）选型
2. 26 号——事件→选股映射的规则是否完整
3. 26 号——news_data 多源情绪的接入方案（Janus-Q/Yukka 等）
4. 22 号——460 板块全覆盖是否必要——个人项目是否只需重点板块
5. 22 号——板块→个股传导的机制是否完整
6. 两篇——T+1 约束下的策略时序
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"event-driven trading 2026""news sentiment alpha 2026"
2. 搜"event impact decay 2026""Hawkes process finance 2026"
3. 搜"sector rotation strategy 2026""industry momentum 2026"
4. 搜"A-share sector rotation 2026""板块轮动 量化 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 26 号——多源 news_data 接入是否过重——个人项目是否只需 1-2 个源
2. 26 号——Hawkes process 衰减模型是否过重
3. 22 号——460 板块全覆盖是否过重——MVP 是否只需 50-100 个重点板块
4. 22 号——板块→个股传导的多层逻辑是否过重
■ 第 6 轮：一致性与交叉引用审查
1. 26 号与 20 号一致性：首批 3 策略定义对齐
2. 22 号与 20 号一致性：§2.5 差异化矩阵对齐
3. 与 30 号一致性：多策略并发
4. 与 23 号一致性：策略间相关性
5. 与 41/42 号一致性：买入流/卖出流的事件/板块依赖
6. 与 62 号一致性：strategy_registry / factor_registry 登记
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 骨架→active 1.0.0
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 26/22 号本身，引用其他文档时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-14 指令（负责 61_lifecycle_multi_ai.md + 53_simulation_live_path.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\61_lifecycle_multi_ai.md（G28 策略生命周期与多 AI 协作，骨架 0.1.0，1002 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\53_simulation_live_path.md（G24 模拟与实盘验证路径，骨架 0.1.0，825 行）
【背景知识】
- 61 号与 01 号衔接：§2.2 三层协作流程
- 61 号与 battle_map_01/02 衔接：研究孵化→模型训练
- 53 号与 20 号衔接：§4.4 灰度指引
- 53 号与 52 号衔接：回测→模拟→实盘路径
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读 61 号全文 + 读 53 号全文
2. 读 01_design_memo_management_spec §2.2（三层协作）
3. 读 battle_map_01_research_incubation + battle_map_02_model_training + battle_map_04_simulation_validation
4. LS src/zephyr/ 找 lifecycle/strategy_factory/simulation 相关
5. 读 02_domain_architecture_docs/71_d_simulation.md（15 模块）
6. 读 20_first_batch_strategies §4.4（灰度指引）
■ 第 2 轮：内容审查与回填
1. 61 号——⚠️ 回填已施工的生命周期管理代码的 why：
   - 策略生命周期（孵化→训练→回测→模拟→实盘→退役）
   - BM-RES 规范
   - BM-MOD 规范
   - 多 AI 协作分工
   - 文档治理
   - creation_token/depgraph 登记
2. 53 号——⚠️ 回填已施工的模拟/实盘代码的 why：
   - paper trading 环境
   - 模拟时长
   - 小资金实盘路径
   - 实盘→模拟差异监控
   - 上线决策门控
   - 灰度上线
3. 两篇骨架文档都需填成 active
■ 第 3 轮：缺失环节与算法审查
1. 61 号——策略生命周期的各阶段准入/准出标准是否完整
2. 61 号——多 AI 协作分工的边界是否清晰
3. 61 号——creation_token/depgraph 登记机制是否可执行
4. 53 号——paper trading 环境与实盘的差异清单是否完整
5. 53 号——灰度上线的阶段/条件/验证标准
6. 53 号——实盘→模拟差异监控的指标/阈值
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"MLOps lifecycle 2026""strategy lifecycle management 2026"
2. 搜"model lifecycle management 2026""multi-AI collaboration 2026"
3. 搜"paper trading simulation 2026""live trading migration 2026"
4. 搜"strategy deployment gating 2026""canary deployment trading 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 61 号——多 AI 协作规范是否过重——个人项目实际是多 AI 还是单 AI 多会话
2. 61 号——BM-RES / BM-MOD 规范是否过重
3. 53 号——灰度四阶段是否过重——个人项目是否只需 2 阶段
4. 53 号——实盘→模拟差异监控是否过重
■ 第 6 轮：一致性与交叉引用审查
1. 61 号与 01 号一致性：§2.2 三层协作对齐
2. 61 号与 battle_map_01/02 一致性：研究孵化/模型训练规范
3. 53 号与 20 号一致性：§4.4 灰度指引对齐
4. 53 号与 52 号一致性：回测→模拟→实盘路径衔接
5. 53 号与 50 号一致性：可观测性与模拟监控
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 骨架→active 1.0.0
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 61/53 号本身，引用其他文档时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-15 指令（负责 14_regime_s2_diagnosis.md + 25_multifactor_strategy_detail.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\14_regime_s2_diagnosis.md（S2 算法错配诊断报告，draft，998 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\25_multifactor_strategy_detail.md（G09 多因子策略细节，骨架 0.1.0，908 行）
【背景知识】
- 14 号与 10 号衔接：S2 是 regime 12 态之一
- 14 号与 12 号衔接：A2/B1 FAIL 的 S2 诊断
- 14 号与 13 号衔接：S2 修复方案
- 25 号与 20 号衔接：首批 3 策略之一
- 25 号与 15/46 号衔接：因子工程
- 25 号与 62 号衔接：factor_registry
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读 14 号全文 + 读 25 号全文
2. 读 src/zephyr/regime/（S2 trigger 逻辑、overlay_signals_builder、bad_news_flat/policy stub）
3. 读 battle_map_05（BM-SEL-02 因子计算/注册表/IC-IR/衰减/合成/治理）
4. 读 src/zephyr/factor/（LS + 读 core/factor_dag/dag.py 等）
5. 读 02_domain_architecture_docs/46_d_factor.md（D_FACTOR 109 模块）
■ 第 2 轮：内容审查与回填
1. 14 号——回填 S2 算法错配的根因诊断（thresholds 过高/NLP stub=0/合成 VIX 缺失）+ 修复方案（已修合成 VIX commit eb3db21bd8 + S1 门槛 commit 981d59d8cc）why
2. 14 号——审查诊断报告的因果时间线是否完整；S2 仍 0/3 的后续是否登记
3. 25 号——⚠️ 回填已施工的多因子策略代码的 why：
   - 因子组合方式（打分/IC加权/正交化）
   - 行业中性化
   - 因子衰减监控
   - 多因子换手率
   - 多因子容量
   - 与打板相关性
4. 25 号——把骨架填成 active
■ 第 3 轮：缺失环节与算法审查
1. 14 号——S2 的多维度触发逻辑是否完整
2. 14 号——S2 修复后的验证结果是否落盘
3. 25 号——因子组合方式的选型依据（打分 vs IC加权 vs 正交化）
4. 25 号——行业中性化的方法（简单行业减均值 vs Barra 风格中性化）
5. 25 号——因子衰减监控的指标/阈值
6. 25 号——多因子换手率的控制机制
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"crisis recovery detection 2026""market bottom identification 2026""capitulation signal 2026"
2. 搜"multi-factor model 2026""factor combination IC weighting 2026"
3. 搜"factor decay monitoring 2026""industry neutralization 2026"
4. 搜"qlib alpha158 2026""WorldQuant alpha 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 14 号——S2 的多维度触发是否过重
2. 25 号——因子治理生命周期是否过重——个人项目是否只需 IC/IR 评估
3. 25 号——行业中性化是否过重——是否只需简单行业减均值
4. 25 号——正交化是否需要——个人项目是否只需 IC 加权
■ 第 6 轮：一致性与交叉引用审查
1. 14 号与 10 号一致性：S2 在 12 态中的定义对齐
2. 14 号与 12 号一致性：A2/B1 FAIL 的 S2 诊断对齐
3. 14 号与 13 号一致性：S2 修复方案对齐
4. 25 号与 20 号一致性：首批 3 策略定义对齐
5. 25 号与 15 号一致性：因子工程总纲对齐
6. 25 号与 62 号一致性：factor_registry 登记
7. 25 号与 23 号一致性：策略间相关性
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 14 号 draft→active 或保持；25 号骨架→active 1.0.0
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 14/25 号本身，引用其他文档时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-16 指令（负责 24_daban_strategy_detail.md + 11_regime_backtest_validation_plan.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 2 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\24_daban_strategy_detail.md（G08 打板策略细节，骨架 0.1.0，942 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\11_regime_backtest_validation_plan.md（regime 回测验证方案，active，911 行）
【背景知识】
- 24 号与 20 号衔接：首批 3 策略之一
- 24 号与 28 号衔接：情绪周期定位器
- 11 号与 10 号衔接：regime spec 的回测验证
- 11 号与 12 号衔接：Phase 2 验证
- 11 号与 13 号衔接：Phase 3 工程
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读 24 号全文 + 读 11 号全文
2. 读 battle_map_05（BM-SEL-22 短线评分卡7维、BM-SEL-23 游资接力6因子+情绪周期4+1、BM-SEL-24 量化强度6维、BM-SEL-25 双引擎融合6类决策）
3. LS src/zephyr/ 找 daban/limit_up/board_ladder/ashare_signal 相关
4. 读 src/zephyr/regime/validation/（LS + 读 c1_comparator/c1_runner/phase2_runner）
■ 第 2 轮：内容审查与回填
1. 24 号——⚠️ 回填已施工的打板策略代码的 why：
   - 连板梯队识别
   - 情绪周期定位器
   - 主升龙头识别
   - 打板容量极小
   - 双引擎融合内部
   - 打板专用风控
   - T+1 时序
2. 24 号——把骨架填成 active
3. 11 号——回填 Phase 1-5 验证方案的已执行结果（C1 已通过 commit 852457e9、Phase 2 已执行见 12 号）到 11 号的验收指南
4. 11 号——审查 Phase 1-5 各阶段验收标准是否完整；C1 Shrinkage 有效性已证，文档是否同步
■ 第 3 轮：缺失环节与算法审查
1. 24 号——7 维评分卡+6 因子+6 维强度是否维度过多——各维度的权重/阈值是否校准
2. 24 号——连板梯队识别的算法是否完整
3. 24 号——打板专用风控的规则（容量/流动性/涨跌停）
4. 11 号——Phase 1-5 各阶段的验收标准/通过条件是否完整
5. 11 号——C1 Shrinkage 有效性验证的方法学
6. 11 号——walk-forward 的窗口/频率参数
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"limit-up board strategy China 2026""游资打板 2026""consecutive limit-up 2026""dragon list 2026"
2. 搜"regime backtest validation 2026""walk-forward validation 2026"
3. 搜"deflated sharpe ratio 2026""purged k-fold 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 24 号——7 维评分卡+6 因子+6 维强度是否维度过多——个人项目是否只需 3-4 维
2. 24 号——双引擎融合 6 类决策是否过重
3. 11 号——5 个 Phase 是否对个人项目过多——是否只需 3 个
4. 11 号——C1 Shrinkage 验证的复杂度
■ 第 6 轮：一致性与交叉引用审查
1. 24 号与 20 号一致性：首批 3 策略定义对齐
2. 24 号与 28 号一致性：情绪周期定位器
3. 24 号与 41/42 号一致性：买入流/卖出流的打板依赖
4. 11 号与 10 号一致性：regime spec 的验证方案对齐
5. 11 号与 12 号一致性：Phase 2 验证结果对齐
6. 11 号与 13 号一致性：Phase 3 工程规划对齐
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 24 号骨架→active 1.0.0；11 号 active 改动升版本
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 24/11 号本身，引用其他文档时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-17 指令（负责 31_position_sizing.md + 18_cold_archive_build_plan.md + 12_regime_phase2_validation.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 3 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\31_position_sizing.md（G12 仓位算法 spec，active v1.2.0，832 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\18_cold_archive_build_plan.md（冷数据归档施工图，active v0.2.0，509 行）
3. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\12_regime_phase2_validation.md（Phase 2 模型质量验证，active v0.2.2，461 行）
【背景知识】
- 31 号与 30 号衔接：分层裁定（策略层粗仓位 risk parity + firm 层 Kelly 精裁决）
- 31 号与 32/33 号衔接：仓位风控体系
- 18 号与 16 号衔接：为技术指标回算腾出存储空间
- 18 号与 63 号衔接：归档表清单
- 12 号与 10/11/13 号衔接：regime 验证系列
- 12 号与 14 号衔接：A2/B1 FAIL 诊断
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读 31 号全文 + 读 18 号全文 + 读 12 号全文
2. 读 src/zephyr/position/core/position_sizing_engine.py + 02_domain_architecture_docs/64_d_position.md（28 模块）
3. 读 src/zephyr/regime/validation/phase2/（a1/a2/b1/b4 四验证器代码）
4. 读 data_retention_contract.yaml（INV-RET-001/002/003 三条铁律）
5. 读 03_data_layer.md（Hot/Warm/Cold 三层定义）
6. 读 archiver.py（三阶段原子操作）
■ 第 2 轮：内容审查与回填
1. 31 号——回填分层裁定（策略层粗仓位 risk parity + firm 层 Kelly 精裁决）的已施工算法 why
2. 31 号——审查 Kelly 参数估计来源、risk parity inverse-vol 公式、单票 8% 硬上限、现金管理是否完整
3. 18 号——回填 archiver.py 三阶段原子操作（export→verify→drop）的已施工 why
4. 18 号——审查 §2 归档分界线（Tick 2022-2024 / K线 2019 年前）是否合理
5. 18 号——审查 §4 铁律修订（INV-RET-001/003）是否已落到实际 YAML
6. 12 号——回填四验证器的实际算法/代码实现 why（A2 标签对齐 Hungarian、B1 后续收益代理标签的 12 态映射）
7. 12 号——审查 A2 FAIL（OOS/IS=0.340）+ B1 FAIL（误差27.6%）的后续修复是否已落盘
■ 第 3 轮：缺失环节与算法审查
1. 31 号——Kelly 精裁决是否需要密度预测（91 号远期愿景）
2. 31 号——单票 8% 硬上限的参数校准依据
3. 18 号——归档分界线是否合理——Tick 2 年 Hot 是否够，K线 8 年是否够
4. 18 号——verify 阶段（行数+抽样 100 行）是否够——是否需要 checksum
5. 12 号——A2/B1 FAIL 的修复方案是否完整
6. 12 号——§9.4/§10.4 的下一步优先级是否已执行
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"position sizing Kelly 2026""risk parity inverse vol 2026""Kelly criterion practical 2026"
2. 搜"ClickHouse cold storage parquet 2026""tick data archive parquet 2026"
3. 搜"data retention policy trading 2026""cold archive best practice 2026"
4. 搜"HMM overfitting detection 2026""probability calibration 2026""Viterbi label alignment 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 31 号——Kelly 精裁决是否对个人项目过重（密度预测需求）
2. 31 号——risk parity 是否过重——个人项目是否只需等权
3. 18 号——两层归档架构是否过度——能否统一一个分界线
4. 18 号——7 个 CLI 命令是否过度——是否只需 archive + restore + stats
5. 18 号——断点续传机制是否过度
6. 12 号——四验证器是否对个人项目过重
■ 第 6 轮：一致性与交叉引用审查
1. 31 号与 30 号一致性：分层裁定对齐
2. 31 号与 32/33 号一致性：仓位风控体系
3. 18 号与 16 号一致性：技术指标回算空间需求
4. 18 号与 63 号一致性：归档表清单
5. 18 号与 data_retention_contract.yaml 一致性：铁律修订已落盘
6. 12 号与 10/11/13 号一致性：regime 验证系列对齐
7. 12 号与 14 号一致性：A2/B1 FAIL 诊断对齐
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 31 号 active 升版本；18 号 active 升 v0.3.0；12 号 active 升版本
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 31/18/12 号本身，引用其他文档时只读不改
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策（如归档分界线调整/铁律修订措辞）标开放问题节；持续改进循环至零问题
```
---

## AI-18 指令（负责 21_stock_selection_engine.md + 51_panel_experiment_history_mlflow_retirement.md + 23_strategy_correlation_validation.md + 17_special_trading_days_data_assets.md + 50_backtest_observability_workplan.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 5 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\21_stock_selection_engine.md（G05 选股引擎架构，骨架 draft 0.1.0，457 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\51_panel_experiment_history_mlflow_retirement.md（Panel 实验历史 Tab + MLflow 退役，active，433 行）
3. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\23_strategy_correlation_validation.md（G07 策略间相关性验证，骨架 0.1.0，385 行）
4. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\17_special_trading_days_data_assets.md（A股特殊交易日数据资产全景与治理，draft v0.1.0，379 行）
5. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\50_backtest_observability_workplan.md（回测可观测性工作计划，draft v1.0.2，264 行）
【背景知识】
- 21 号与 20 号衔接：首批 3 策略的选股引擎
- 21 号与 24/25/26 号衔接：策略选股池交集
- 51 号与 50 号衔接：MLflow 退役与可观测性衔接
- 23 号与 20 号衔接：§2.5 差异化矩阵
- 17 号与 62/63 号衔接：数据资产注册表/利用率审查
- 17 号与 19 号衔接：hk_connect_closed 北向停摆日
- 50 号与 51 号衔接：可观测性与实验历史
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读 21 号全文 + 读 51 号全文 + 读 23 号全文 + 读 17 号全文 + 读 50 号全文
2. 读 battle_map_05（BM-SEL-25 双引擎融合、L0→L1→L2-C 分层、量化强度评级）
3. LS src/zephyr/ 找 selection/stock_selection/ashare_signal 相关
4. 读 src/zephyr/frontend/dashboard/（LS + 读 app_panel.py / experiment_history.py / backtest_performance.py）
5. 读 20_first_batch_strategies §2.5 差异化矩阵
6. 读 src/zephyr/observability/ + 02_domain_architecture_docs/07_d_infra_telemetry.md（11 模块）
7. 核验 17 号 §3 已施工盘点：7 个 schema 文件 / 7 条品类注册 / 6 个采集任务——逐一 Grep 确认
8. 核验 17 号 §4 #ARCH-DATA-001 修复代码
■ 第 2 轮：内容审查与回填
1. 21 号——⚠️ 骨架文档，重点回填已施工的选股引擎代码的 why：
   - 双引擎融合定位
   - L0→L1→L2-C 分层
   - 量化强度评级
   - 选股 pipeline 标准接口
   - 候选池生成→过滤→排序→输出
   - 与 StrategyBook 对接契约
2. 51 号——回填 Panel 实验历史 Tab 的已施工代码 why；掘金 5-Tab 复用的鸭子类型重建逻辑
3. 51 号——审查 MLflow 退役进度是否完成；§七 10 项施工算法 + §八 4 项后续增强的落地状态
4. 23 号——⚠️ 骨架文档，回填已施工的相关性验证代码的 why（若未施工，则填 why 决策 + 标"待施工"）：
   - 5 候选两两相关矩阵
   - 按情绪周期分层
   - >0.6 重新审视
   - 验证数据区间
   - 验证报告模板
5. 17 号——审查 §2 特殊交易日完整清单（4 大类）是否有遗漏
6. 17 号——审查 §4 #ARCH-DATA-001 修复正确性 + §5 #ARCH-DATA-002 治本方案
7. 50 号——回填六零件日志（C1/regime/特征/向量化/StrategyRunner/C2C3）的已施工部分 why
8. 50 号——审查 §2.3 命名冲突 + §9 待决策点
■ 第 3 轮：缺失环节与算法审查
1. 21 号——L0→L1→L2-C 三层是否过重——各层的职责/接口是否清晰
2. 51 号——实验历史 Tab 的功能是否完整
3. 23 号——block-bootstrap 2000x 是否过重——方法选型（pearson/spearman/block-bootstrap）
4. 17 号——特殊交易日清单是否有遗漏（国债期货交割日/股指期货最后交易日/央行操作日/经济数据发布日等）
5. 17 号——#ARCH-DATA-002 治本方案 5 个施工项是否对个人项目过重
6. 50 号——MLflow + 薄包装层是否对个人项目过重——是否符合"集成到现有 Panel dashboard"偏好
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"stock selection engine 2026""alpha factory layered 2026""quant signal pipeline 2026"
2. 搜"Panel HoloViz dashboard 2026""experiment history visualization 2026"
3. 搜"strategy correlation block bootstrap 2026""multi-strategy decorrelation 2026"
4. 搜"A股 特殊交易日 事件研究 2026""股指期货交割日效应 2026""MSCI 调整 A股 2026"
5. 搜"MLflow 3.0 2026""experiment tracking 2026""backtest observability 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 21 号——L0→L1→L2-C 三层是否过重——个人项目是否只需 2 层
2. 51 号——实验历史 Tab 是否过重
3. 23 号——block-bootstrap 2000x 是否过重——是否只需 500x
4. 17 号——#ARCH-DATA-002 治本方案 5 项是否过重——MVP 是否只需施工项 4+1
5. 50 号——MLflow 是否应彻底退役而非保留薄包装
■ 第 6 轮：一致性与交叉引用审查
1. 21 号与 20/24/25/26 号一致性：选股引擎与策略定义
2. 21 号与 30 号一致性：与 StrategyBook 对接
3. 51 号与 50 号一致性：可观测性与实验历史衔接
4. 23 号与 20 号一致性：§2.5 差异化矩阵
5. 17 号与 15 号一致性：数据层架构
6. 17 号与 62/63 号一致性：数据资产登记/利用率
7. 17 号与 19 号一致性：hk_connect_closed 北向停摆日
8. 17 号与 architecture_issue_registry.yaml 一致性：#ARCH-SPECIAL-DAYS/#ARCH-DATA-001/#ARCH-DATA-002
9. 50 号与 51 号一致性：MLflow 退役进度
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法——注意 17 号 scope 为单一值 / §4.4 文档种类适配 / 双硬约束 / 稳定 path）
5. 21/23 号骨架→active 1.0.0；51 号 active 升版本；17 号 draft 保持或转 active；50 号 draft→active 或保持
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 21/51/23/17/50 号本身，引用其他文档时只读不改
- 例外：17 号 §6.4 悬空引用修正（business_data_categories.yaml + tasks.yaml 各 1 行改指向 17 号）可越界改，因这是文档自身承接的紧随任务且仅改引用行
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-19 指令（负责 20_first_batch_strategies.md + 19_northbound_hold_snapshot.md + 01_design_memo_management_spec.md + 28_sentiment_cycle_trading.md + 60_cross_cutting_cleanup.md + 65_git_safety_governance.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 6 篇文档：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\20_first_batch_strategies.md（首批3策略定义，active v1.2.4，253 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\19_northbound_hold_snapshot.md（北向资金季度持仓快照 fetcher 施工计划，draft v0.1.0，213 行）
3. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\01_design_memo_management_spec.md（管理规范，active v1.2.0，161 行）
4. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\28_sentiment_cycle_trading.md（G21 情绪周期×交易决策，骨架 0.1.0，72 行）
5. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\60_cross_cutting_cleanup.md（G27 冲突矩阵清理与事件总线，骨架 0.1.0，72 行）
6. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\65_git_safety_governance.md（Git 安全治理体系——alias 失效修复与多层防护，draft v0.1.0，615 行）
【背景知识】
- 01 号规范是所有文档的管理规范——§4.1 段位编号制、§4.4 文档种类适配
- 20 号与 24/25/26 号衔接：首批 3 策略（打板/多因子/事件驱动）
- 20 号与 21/22 号衔接：选股引擎/板块轮动
- 19 号与 15/62/63 号衔接：数据层/注册表/利用率审查
- 19 号与 25 号衔接：下游消费方（外资行为因子）
- 28 号与 10 号衔接：情绪周期 vs regime 12 态分工边界
- 28 号与 24 号衔接：情绪周期定位器
- 65 号是 git clean 误删事件的治本方案——与 git_guard.py / lock_files.py / GitCommitGateway / session_worktree 相关，与 61 号生命周期多 AI 衔接
- 60 号与 30 号衔接：§7.3 冲突仲裁 + 事件总线
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读 20 号全文 + 读 19 号全文 + 读 01 号全文 + 读 28 号全文 + 读 60 号全文
2. 读 src/zephyr/pf_core/strategies/ + battle_map_05_stock_selection.md（BM-SEL-22~27）
3. 核验 19 号 §3.1 akshare 实测表 + §3.2 tushare hk_hold 实测表
4. 读 10_regime_detector_spec（regime 12 态含情绪维度）
5. 读 30_multi_strategy §7.3（A 模型消失的冲突）
6. LS src/zephyr/ 找 sentiment/cycle/emotion/event_bus/signal_router 相关
■ 第 2 轮：内容审查与回填
1. 20 号——回填 3 策略（打板/多因子/事件驱动）已施工的 alpha 信号链 why 补全（打板链 BM-SEL-22~25、因子工厂 BM-SEL-02、事件处理 BM-SEL-27）
2. 20 号——审查 §2.5 差异化矩阵、§2.6 选股池交集、§4.4 灰度指引是否完整；§5 待裁定 4 项是否已落地
3. 19 号——审查 §4.1 四方案对比 + §4.2 裁定走方案 C 的理由
4. 19 号——审查 §5 fetcher 设计 + §6 外资行为分析方法论 6 节
5. 01 号——审查 §1-§7 是否与 46 篇文档实际现状一致（命名规则/段位编号/status 枚举/防飘移机制）
6. 01 号——审查 §4.4 文档种类适配是否覆盖所有实际文档种类
7. 28 号——⚠️ 骨架文档（72 行），重点回填已施工的情绪周期代码的 why（非"审查现有内容"）：
   - 5 阶段买卖纪律（冰点/反核/主升/疯狂/退潮）
   - 情绪周期定位器准确率评估
   - 情绪周期与 regime 12 态映射
   - 各策略不同情绪阶段部署
   - 情绪周期作为隐形驱动
   - 重点：明确情绪周期（sleeve 内 alpha 择时）vs regime（市场级风险节流）的分工边界
8. 60 号——⚠️ 骨架文档（72 行），重点回填已施工的事件总线/信号路由代码的 why：
   - 31 条冲突仲裁大部分消失
   - 仅留 firm-level 硬上限
   - 事件总线/信号注入
   - 实时计算节奏
   - 配置驱动
   - 多策略投票降级
■ 第 3 轮：缺失环节与算法审查
1. 20 号——§4.4 intake 四阶段是否对个人项目过重
2. 19 号——§6.1 持市值变化分解公式准确性；§6.4 板块切换能力评估样本量
3. 01 号——§2.2 三层协作流程、§5.3 修订规则是否对个人项目过重
4. 28 号——4+1 阶段是否过细
5. 60 号——事件总线是否对个人项目过重
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"multi-strategy alpha 2026""daban limit-up strategy 2026""event-driven trading 2026""factor investing 2026"
2. 搜"北向资金 替代数据 2026""沪深港通 季度持仓 外资行为分析 2026""tushare hk_hold 季度快照"
3. 搜"architecture decision record alternative 2026""design memo vs ADR 2026"
4. 搜"market sentiment cycle 2026""游资情绪周期 2026""limit-up sentiment 2026"
5. 搜"event bus trading system 2026""signal routing 2026""config driven trading 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 20 号——§4.4 intake 四阶段是否过重
2. 19 号——外资行为分析方法论 6 节是否过度——是否先做简单增减持排名 + 净流入估算
3. 19 号——fetcher 设计是否过度——是否只需简单全量覆盖
4. 01 号——三层协作流程是否过重——个人项目是否需要
5. 28 号——4+1 阶段是否过细——是否只需 3 阶段
6. 60 号——事件总线是否过重——个人系统是否需要微服务级信号路由
■ 第 6 轮：一致性与交叉引用审查
1. 20 号与 24/25/26 号一致性：首批 3 策略定义对齐
2. 20 号与 21/22 号一致性：选股引擎/板块轮动
3. 20 号与 30 号一致性：多策略并发
4. 19 号与 15 号一致性：数据层架构
5. 19 号与 62/63 号一致性：数据资产登记/利用率
6. 19 号与 known_data_gaps.yaml/check_algo_quality.py 一致性
7. 01 号与 46 篇文档一致性：规范是否被实际遵循
8. 28 号与 10 号一致性：情绪周期 vs regime 分工边界
9. 28 号与 24 号一致性：情绪周期定位器
10. 60 号与 30 号一致性：§7.3 冲突仲裁
11. 60 号与 01 号一致性：三层协作
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 20 号 active 升版本；19 号 draft 保持或升 v0.2.0；01 号 active 升版本；28/60 号骨架→active 1.0.0
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 20/19/01/28/60 号本身，引用其他文档时只读不改
- 01 号是管理规范，改动需特别谨慎（影响所有文档）——如改规范本身，需评估对 46 篇文档的影响
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-20 指令（负责 33_budget_change_handler.md + 55_monitoring_review.md + 52_backtest_framework_docking.md + 15_data_feature_layer_spec.md + 27_second_batch_strategies.md + 16_technical_indicator_catalog.md + 16_technical_indicator_build_plan.md）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并更新 7 篇文档（全部是骨架/空模板文档，重点回填已施工代码的 why）：
1. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\33_budget_change_handler.md（G14 BudgetChangeHandler 三级升级，骨架 0.1.0，74 行）
2. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\55_monitoring_review.md（G26 监控告警与复盘，骨架 0.1.0，72 行）
3. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\52_backtest_framework_docking.md（G23 回测框架对接，骨架 0.1.0，72 行）
4. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\15_data_feature_layer_spec.md（G01 数据与特征层规范，骨架 draft 0.1.0，71 行）
5. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\27_second_batch_strategies.md（G11 第二批次策略，骨架 0.1.0，暂缓，71 行）
6. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\16_technical_indicator_catalog.md（技术指标目录，骨架 0.1.0，65 行）
7. d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\16_technical_indicator_build_plan.md（技术指标回算施工计划，骨架 0.1.0，47 行）

【⚠️ 重要提示——骨架文档回填原则】
以上 7 篇全部是骨架文档（47-74 行的空模板），§2-§6 基本全空。你的核心任务不是"审查现有内容"（因为没有内容），而是：
1. **回填已施工代码的 why**——读项目代码，把已施工的算法/模块/基础设施的决策推理回填到文档
2. **把骨架填成 active**——补 §1 背景、§2 决策、§3 替代方案、§4 上限、§5 待裁定、§6 待定问题、§7 引用、§8 修订记录
3. 如果代码未施工，则填 why 决策（用什么方法/为什么选这个方法）+ 标"待施工"
【背景知识】
- 33 号与 30 号衔接：§2.4 三级升级 Tier1/2/3
- 55 号与 50 号衔接：可观测性衔接
- 52 号与 11 号衔接：regime 对接范式
- 15 号与 64 号衔接：15 号"数据进来后怎么用" vs 64 号"数据怎么进来"
- 27 号与 20 号衔接：§4.2 演进路径
- 16 号与 62 号衔接：technical_indicator_registry
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 读全部 7 篇文档（每篇 47-74 行，可一次读完）
2. 读项目代码：
   - LS d:\ZephyrAlpha\src\zephyr\ 找 data/factor/feature/mkt_data 相关子包
   - 读 d:\ZephyrAlpha\docs\02_enterprise_architecture\02_domain_architecture_docs\11_d_data.md + 12_d_data_eng.md + 23_d_mkt_data.md + 46_d_factor.md 了解已施工模块清单
   - 读 src/zephyr/position/core/budget_change_handler.py（MOD-POS-022）
   - 读 src/zephyr/observability/ + 02_domain_architecture_docs/07_d_infra_telemetry.md
   - 读 src/zephyr/backtest/（LS + 读 core/engine_base.py / vectorized_engine）+ 02_domain_architecture_docs/35_d_backtest.md
   - 读 src/zephyr/factor/technical_indicators/（LS + 读实际指标实现）
   - 读 battle_map_01~12 相关章节
3. 读 30_multi_strategy §2.4（三级升级）+ §2.2（三模块）
4. 读 20_first_batch_strategies §4.2（演进路径）
■ 第 2 轮：内容审查与回填（核心——回填已施工代码的 why）
1. 33 号——回填已施工的 BudgetChangeHandler 代码的 why：
   - Tier1 封锁新仓
   - Tier2 rebalance_to_budget
   - Tier3 按比例强裁
   - convergence_window 差异化
   - rebalance 接口契约
   - 每级 log/复盘
2. 55 号——回填已施工的监控/复盘代码的 why：
   - 系统健康监控
   - 策略偏离监控
   - 告警阈值通知
   - 每日/每周/每月复盘
   - 策略退役标准
   - 复盘文档模板
3. 52 号——回填已施工的回测框架代码的 why：
   - BM-BT-01~07 在策略验证用法
   - 策略回测 vs regime 回测差异
   - 上线门控 IS→WFA→OOS
   - 过拟合检测三维度
   - Deflated Sharpe
4. 15 号——回填已施工的数据/因子基础设施 why：
   - ClickHouse schema 规范——查 src/zephyr 下 clickhouse schema 定义，回填实际 schema 设计 why
   - miniQMT tick 接入契约——查 miniQMT 接入代码，回填实际契约
   - PIT 铁律——查 AS OF JOIN/Embargo 实现，回填实际方案
   - 特征仓库架构——查特征计算/缓存/版本实现，回填
   - 因子工程总纲——查因子库/IC 评估/衰减监控/过拟合监控实现，回填
   - 数据质量门控——查数据质量检查实现，回填
5. 27 号——暂缓骨架（首批 track record 后再讨论），不需要填满，但审查：
   - 暂缓理由是否充分
   - 价值反转/动量趋势的 alpha 信号预研方向是否登记
   - 与首批 3 策略相关性的预判
6. 16 号 catalog——回填已施工的技术指标 why：
   - 5 大类 + 9 周期——反查 src/zephyr/factor/technical_indicators/，验证 40 指标/55 输出列覆盖
   - 与 factor_registry 正交边界
7. 16 号 build_plan——回填技术指标回算施工计划 why：
   - 198GB 回算需求（缩减后 162GB）
   - 6 周期回算的优先级/依赖
   - 与 18 号冷归档的衔接（腾出存储空间）
■ 第 3 轮：缺失环节与算法审查
1. 33 号——三级升级的触发条件/参数是否完整
2. 55 号——三频复盘（日/周/月）是否过重
3. 52 号——BM-BT-01~07 七环节是否过多
4. 15 号——PIT 铁律的实现是否正确（AS OF JOIN/Embargo）
5. 15 号——特征仓库是否需要完整 Feature Store，还是轻量缓存即可
6. 27 号——暂缓文档是否应精简
7. 16 号 catalog——40 指标/55 输出列是否完整
8. 16 号 build_plan——6 周期回算的可行性/优先级
■ 第 4 轮：2026 年 8 月最新研究搜索（全网 WebSearch）
1. 搜"budget rebalance protocol 2026""position de-risking 2026""multi-strategy capital reallocation 2026"
2. 搜"trading system monitoring 2026""strategy deviation alert 2026""strategy retirement criteria 2026"
3. 搜"backtest framework 2026""walk-forward analysis 2026""deflated sharpe 2026""purged k-fold 2026"
4. 搜"feature store architecture 2026""factor IC evaluation 2026""point-in-time database 2026""alpha factory 2026"
5. 搜"value reversal strategy 2026""momentum trend following 2026"
6. 搜"technical indicator catalog 2026""TA-Lib 2026""technical analysis indicator 2026"
■ 第 5 轮：过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. 33 号——三级升级是否过重——个人系统是否需 Tier2 策略自主
2. 55 号——三频复盘是否过重——个人项目是否只需周复盘
3. 52 号——BM-BT-01~07 七环节是否过多——是否只需 3-4 环节
4. 15 号——特征仓库/因子工程是否对个人项目过重——是否只需轻量缓存
5. 15 号——PIT 铁律是否过重——个人项目是否只需 AS OF JOIN
6. 27 号——暂缓文档是否应精简
7. 16 号——40 指标是否过多——MVP 是否只需 15-20 个核心指标
8. 16 号 build_plan——6 周期全回算是否过重——是否先回算日线+1分钟
■ 第 6 轮：一致性与交叉引用审查
1. 33 号与 30 号一致性：§2.4 三级升级对齐
2. 33 号与 32 号一致性：FirmRiskAggregator 联动
3. 55 号与 50 号一致性：可观测性衔接
4. 55 号与 54 号一致性：对账结果驱动复盘
5. 52 号与 11 号一致性：regime 对接范式
6. 52 号与 53 号一致性：回测→模拟→实盘路径
7. 15 号与 64 号一致性："数据进来后怎么用" vs "数据怎么进来"
8. 15 号与 62 号一致性：factor_registry / data_asset_registry
9. 27 号与 20 号一致性：§4.2 演进路径
10. 16 号与 62 号一致性：technical_indicator_registry
11. 16 号 build_plan 与 18 号一致性：冷归档腾出空间
■ 第 7 轮：文档质量与规范符合性
1-4. 通用检查同首个指令块第 7 轮 1-4（frontmatter 齐全合法 / §4.4 文档种类适配 / 修订记录+开放问题节双硬约束 / 交叉引用全用稳定 path 禁 node_id/edge_id）
5. 骨架→active 1.0.0（27 号保持 draft 但补全暂缓说明）
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查一轮，直到问题数量=0 且缺失功能/模块数量=0；升版本号在修订记录登记）
■ 约束
- 只改 33/55/52/15/27/16/16 号本身，引用其他文档时只读不改
- 骨架文档的核心是"回填已施工代码的 why"，不是"审查现有内容"
- 通用约束同首个指令块「约束」：需同步改他文档记负责文档开放问题节不越界改；不擅自定决策标开放问题节；持续改进循环至零问题
```
---

## AI-21 指令（负责 90_methodology_open_questions.md — 特殊讨论文档）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】对 1 篇讨论文档进行深度调研、分析和裁定：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\90_methodology_open_questions.md（方法论遗留提案 21 项，draft v1.9.0，1068 行）
【文档性质】这是讨论文档（不是常规审查文档），包含 21 项方法论遗留提案（策略类型/因子IC/组合构建/风险模型/成本/回测门禁/T+1预测/流动性/数据分层/密度/仓位/成功指标/基准/PIT/资产分级/行为边界/资产覆盖/大额下单/工程细节/做T方法论）。需要你以客观专业架构师身份进行深度调研、分析裁定和施工方案设计。
【工作清单】
■ 第 1 阶段：通读与问题梳理 + 基础设施盘点（盘点要求全文同通用规则 #11，逐字适用）
1. 完整读 90 号全文（1068 行，21 项遗留提案）
2. 列出所有 21 项待讨论问题/开放问题
3. 读所有相关文档（用 Grep/SearchCodebase 找交叉引用）：
   - 30_multi_strategy（多策略并发总纲）
   - 10_regime_detector_spec（regime 12 态）
   - 已施工代码（src/zephyr/）
4. 重点对照已过时项：
   - #7 T+1次日预测（8态→12态已过时）
   - #3 组合构建（risk budgeting→risk parity已裁定）
   - #4 风险模型（L1/L2/L3→4级回撤Protocol）
   - #6 回测门禁（V1-V6→BM-BT-01~07）
   - #11 仓位管理（C-047→MOD-POS-001）
■ 第 2 阶段：第一性原理调研
对每个问题，从第一性原理出发：
1. 这个问题的本质是什么？为什么存在？
2. 业界（专业机构）怎么做的？标准实践是什么？
3. 量化社区（QuantConnect/Numerai/WorldQuant/qlib）怎么做的？
4. 氛围编程社区（AI-driven dev/vibe coding）怎么做的？
5. 个人+100%AI 项目应该怎么做？（不是机构级、不是团队级）
6. 长远期战略考虑：3年后这个决策是否仍然合理？
■ 第 3 阶段：全网调研
用 WebSearch 搜 2026 年最新：
- 每个问题的最新学术研究/业界实践
- 2026 年新出现的方法/工具/框架
- 是否有更好的替代方案
- 搜索方向：
  * "quantitative methodology 2026""factor investing best practice 2026"
  * "portfolio construction risk parity 2026""risk model layered 2026"
  * "backtest gating 2026""T+1 prediction 2026"
  * "data layering PIT 2026""position sizing 2026"
  * "benchmark selection 2026""asset classification 2026"
■ 第 4 阶段：分析过程与裁定
对每个问题：
1. 列出所有候选方案
2. 逐方案分析优缺点（对个人+100%AI 项目的适配性）
3. 给出裁定结果（采纳/拒绝/暂缓/远期/已过时废弃）
4. 裁定理由（引用第一性原理+业界实践+个人项目约束）
5. 逐项审查：每项与项目现状（30_multi_strategy / 10_regime / 已施工代码）的对齐状态——已过时的标❌废弃、已裁定的标✅、待讨论的保留
■ 第 5 阶段：治本施工方案
对每个裁定为"采纳"的方案：
1. 施工步骤（具体到文件和函数）
2. 过度工程审查（判定基准：[system_charter.md §2 硬边界约束](../../04_architecture_principles_decisions/system_charter.md#L61-72) + 1 人在 TRAE 编译器上多 AI 多对话并发施工——超出硬边界的复杂度 = 过度工程 → 去掉或降级为远期；已显式标注 P4/P5/远期愿景/待裁定的远期工程不算，予以保留）
3. 与现有架构的集成点
4. 验证方法
5. 风险与缓解
■ 第 6 阶段：文档更新
1. 把调研报告、分析过程、裁定结果、施工方案写入文档
2. 21 项是否都需保留，已废弃的可标 deprecated 或删除
3. 从 draft 升级为 active（如果裁定完整）或保持 draft
4. 升版本号（v1.9.0→v2.0.0 大改）
5. 修订记录登记
■ 循环条件（含 git 提交闭环）
- 每个问题都要有明确的裁定结果
- 每个裁定都要有第一性原理支撑
- 每个施工方案都要有过度工程审查（判定基准：system_charter.md §2 硬边界 + 1 人多 AI 并发施工，远期标注除外）
- 每轮裁定/施工方案落盘后立即 `git add` + `git commit`（提交信息注明本轮裁定/修复内容，禁止 `--no-verify` 绕过门禁），提交后再进入下一轮审查
- **问题数量=0 且缺失功能/模块数量=0**（连续一轮零新增内容确认）= 任务结束
■ 约束
- 你是客观专业架构师，不是辩护人——如果问题本身不合理，直接说
- 裁定基于个人+100%AI 项目约束，不是机构级标准
- 不擅自定决策（需用户确认的标"待用户裁定"）
- 持续改进不停，循环至零问题
- 只改 90 号本身，引用其他文档时只读不改
- 不破坏交叉引用
```
---

## AI-22 指令（负责 91_density_prediction.md — 特殊讨论文档）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】对 1 篇讨论文档进行深度调研、分析和裁定：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\91_density_prediction.md（密度预测远期愿景，draft v1.5.0，45 行）
【文档性质】这是讨论文档（不是常规审查文档），包含密度预测的六阶段远期愿景（EWMA标准化conformal→Bayesian Kelly→Tail-Aware MDN/Lévy族→Info-Entropic DL+GP→GPD/Lévy-Flow/扩散→QNN）。文档很短（45 行骨架），但涉及深度技术决策。需要你以客观专业架构师身份进行深度调研、分析裁定和施工方案设计。
【工作清单】
■ 第 1 阶段：通读与问题梳理 + 基础设施盘点（盘点要求全文同通用规则 #11，逐字适用）
1. 完整读 91 号全文（45 行）
2. 列出所有待讨论问题/开放问题（密度预测必需性/QNN 可行性/校准阈值/与风控关系）
3. 读所有相关文档：
   - 10_regime_detector_spec（12态 regime 已定稿，密度预测是否还有增量）
   - 31_position_sizing（Kelly 精裁决是否需要密度预测）
   - 36_var_es_monitoring（VaR/ES 是否需要密度预测）
   - 35_drawdown_protocol_impl（回撤 Protocol 是否需要密度预测）
4. 读项目代码（用 Glob/LS 找相关实现）
■ 第 2 阶段：第一性原理调研
对每个问题，从第一性原理出发：
1. 密度预测的本质是什么？为什么个人+100%AI 项目需要（或不需要）？
2-6. 同前一指令块（90 号）第 2 阶段 2-6（业界标准实践/量化社区/氛围编程社区/个人+100%AI 定位/3 年长远期考虑）
7. 六阶段远期愿景的每一阶段：
   - EWMA标准化conformal——个人项目是否需要？
   - Bayesian Kelly——与 31 号 Kelly 精裁决的关系
   - Tail-Aware MDN/Lévy族——复杂度是否合理
   - Info-Entropic DL+GP——个人项目算力是否够
   - GPD/Lévy-Flow/扩散——远期可行性
   - QNN（量子神经网络）——2026 年单机 RTX 3090 的可行性
■ 第 3 阶段：全网调研
用 WebSearch 搜 2026 年最新：
- "density prediction finance 2026""probabilistic forecasting 2026"
- "QNN quantum neural network 2026""quantum machine learning finance 2026"
- "CRPS calibration 2026""conformal prediction 2026"
- "Bayesian Kelly criterion 2026""tail risk modeling 2026"
- "MDN mixture density network finance 2026""Lévy process finance 2026"
- "GPD generalized Pareto distribution 2026""diffusion model finance 2026"
- 2026 年新出现的方法/工具/框架
- 是否有更好的替代方案
■ 第 4 阶段：分析过程与裁定
对每个问题/每个阶段：
1. 列出所有候选方案
2. 逐方案分析优缺点（对个人+100%AI 项目的适配性）
3. 给出裁定结果（采纳/拒绝/暂缓/远期/删除）
4. 裁定理由（引用第一性原理+业界实践+个人项目约束）
5. 重点裁定：
   - 密度预测对个人项目是否必需——还是 regime 12 态 + Kelly 标量已够
   - QNN 远期愿景是否应保留还是降级删除（个人项目算力限制）
   - 六阶段路线图是否合理——是否有阶段应砍掉/合并
■ 第 5 阶段：治本施工方案
对每个裁定为"采纳"的方案：
1-5. 同前一指令块（90 号）第 5 阶段 1-5（施工步骤到文件和函数/过度工程审查——判定基准同通用规则 #5/与现有架构的集成点/验证方法/风险与缓解）
6. 特别审查：QNN 在单机 RTX 3090 的 2026 最新可行性——如不可行，明确建议删除还是保留远期标注
■ 第 6 阶段：文档更新
1. 把调研报告、分析过程、裁定结果、施工方案写入文档
2. 把 45 行骨架填成完整讨论文档
3. 从 draft 升级为 active（如果裁定完整）或保持 draft
4. 升版本号
5. 修订记录登记
■ 循环条件（含 git 提交闭环）
- 前三条同前一指令块（90 号）「循环条件」1-3（每问题裁定结果明确/每裁定第一性原理支撑/每方案过度工程审查）
- 每轮裁定/施工方案落盘后立即 `git add` + `git commit`（提交信息注明本轮裁定/修复内容，禁止 `--no-verify` 绕过门禁），提交后再进入下一轮审查
- **问题数量=0 且缺失功能/模块数量=0**（连续一轮零新增内容确认）= 任务结束
■ 约束
- 同前一指令块（90 号）「约束」逐字适用（负责文档为 91 号）
```
---

## AI-23 指令（负责 66_commit_queue_serialization.md — 新增治理文档）
```
你是 ZephyrAlpha 项目的架构审查 AI。项目是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。
【你的任务】审查并裁定 1 篇新增治理文档：
d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\66_commit_queue_serialization.md（提交队列串行化——多 AI 并发施工的集成层总案，draft v0.1.0，260 行）
【文档性质】这是 2026-08-12 新增的**决策备忘 + 施工计划**（首版 draft，待审查）。背景：当日 23 会话并发施工发生互冲/吞稿/搭便车/连坐阻断事故链，文档提出"会话提交=快照入队即返回，后台单写者 Serializer 按序串行落盘"的治本方案——对标 Transactional Outbox + GitHub Merge Queue + LMAX Disruptor 单写者定序 + Kafka Log Compaction + DLQ 死信的组装。核心机制：plumbing 直写（GIT_INDEX_FILE 独立 index + hash-object + commit-tree + update-ref，不碰工作区）、同键覆盖 compaction、门禁出队端执行、死信 task_board 闭环、worktree 从必须降级为可选。你的核心任务是**审查裁定这个新方案的合理性与可施工性**，不是回填既有内容。
【背景知识】
- 65 号 git 安全治理是上游护栏层（git_guard.py 拦截、逃生通道审计、worktree 纪律）——66 号 §4.5 把 worktree 从"必须"降级为"可选"，与 65 号现行纪律存在口径冲突，需裁定对齐方式
- 61 号生命周期多 AI 定义会话注册/锁/提交协议；60 号跨切清理；01 号管理规范 §4.1 段位编号制（6x=跨切治理）
- AGENTS.md §10「多会话并发防护铁律」（改完立即 add + 禁全区恢复命令）——66 号 §4.6 提出演化为"改完立即入队"
- 关联 ARCH 议题：#ARCH-GIT-CLEAN-GUARD-FIX（8-11 git clean 灾难）/ #ARCH-AICOLLAB-001（Worktree+FileLock+TaskBoard 三件套）/ #ARCH-WORKTREE-GATE-001（WORKTREE-REQUIRED 门禁）/ I-GOV-3 v2 三纪律（待登记 ARCH 编号）
- 网关现况：`python scripts/git_commit.py --session <id>` 是唯一提交入口（GATE-COMMIT-GW 拦裸 commit）；pre-commit 框架有全树 stash 周期（23 会话下互踩实证）
【工作清单——循环执行直到全部为零】
■ 第 1 轮：读现状 + 基础设施盘点（只读不改；盘点要求全文同通用规则 #11，逐字适用）
1. 完整读 66 号全文（260 行）
2. 读全部关联代码（真实实现 vs 文档假设逐条核对）：
   - src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py（串行锁/门禁链/逃生通道现状）
   - src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
   - scripts/git_commit.py + scripts/git_guard.py + scripts/lock_files.py + scripts/task_board.py
   - scripts/governance/test_concurrent_safety.ps1（66 号 §11 复用的压测脚本是否真实存在）
   - .pre-commit-config.yaml（stash 周期触发条件）
3. 读关联文档：65_git_safety_governance（护栏层全貌）+ 61_lifecycle_multi_ai（会话协议）+ 60_cross_cutting_cleanup + 55_monitoring_review（§8 防饥饿告警对接点）+ 01 号规范
4. 查 architecture_issue_registry.yaml 中 #ARCH-GIT-CLEAN-GUARD-FIX / AICOLLAB-001 / WORKTREE-GATE-001 / GOV-BUDGET-002 的 status 与 adjudication
5. 检查 .runtime/ 目录现状（commit_queue 是否已有任何施工痕迹）+ AGENTS.md §10 现行文本
■ 第 2 轮：方案裁定审查（核心——逐条裁定 66 号 §4 六项裁定）
对每项裁定给出"采纳/修正/拒绝+理由"：
1. **快照入队+单写者串行**：对比更简单的替代方案（如单全局互斥锁串行化 commit、文件锁扩展到提交期、git worktree 强制隔离升硬）——队列方案对个人+100%AI 项目是否过度工程？23 会话并发是否是常态还是一次性事件？（若并发回降到 3-5 会话，队列是否是杀鸡用牛刀）
2. **plumbing 直写（不碰工作区）**：在 Windows + git 2.48.1 上实测验证技术可行性——GIT_INDEX_FILE 独立 index + read-tree + hash-object -w + update-index --cacheinfo + write-tree + commit-tree + update-ref 全链是否可跑通（用测试仓库实测，不动主仓）
3. **同键覆盖 compaction**：(session_id, path) 键设计是否会丢"同会话有意保留的中间态"？快照整体替换 vs diff 的存储成本
4. **门禁出队端执行**：GitCommitGateway 现门禁链哪些依赖工作区文件/共享 index，挪到临时 index 上跑的适配清单（66 号 §12 开放问题 1——给出实证答案）
5. **worktree 降级为可选**：与 65 号纪律、AGENTS.md §10 铁律的冲突如何收口——两文档口径必须一致，裁定改哪边（注意：你只改 66 号，65 号改不动则记在 66 号开放问题）
6. **死信+级联标记**：DLQ 闭环对个人项目是否可运维——死信堆积谁清理？task_board.py schema 现状能否承载（读真实代码核对）
■ 第 3 轮：2026 年最新实践搜索（全网 WebSearch）
1. 搜 "GitHub Merge Queue 2026""merge queue monorepo 2026""Bors Zuul 2026"——主干保护最新实践
2. 搜 "transactional outbox pattern 2026""single writer principle 2026"——模式演进
3. 搜 "AI agent concurrent git 2026""multi-agent coding git conflict 2026""vibe coding parallel agents git 2026"——多 AI 并发提交的最新社区方案（是否有比队列更轻量的新实践）
4. 搜 "git plumbing commit-tree automation 2026"——直写造 commit 的业界实证
5. 找到的更好方案登记到 66 号「考虑过的替代方案」（没有则新增该节），不直接替换已定决策
■ 第 4 轮：施工计划与过度工程审查（判定基准：system_charter §2 硬边界 + 施工方式，判定基准全文同通用规则 #5，逐字适用）
1. §10 施工分期 MVP/P1/P2 的验收标准是否可执行——"3 会话并发 50 提交零丢失"如何自动化断言
2. MVP 最小集能否再砍——v0.1 是否可以先只做"串行化"（全局互斥）不做"队列持久化+compaction+死信"，验证止血后再迭代？（止血优先 vs 一步到位，给出裁定）
3. §8 故障恢复表——Serializer 单进程 watchdog 在 Windows 的常驻方案（计划任务？守护脚本？）是否写清
4. §9 不做什么 5 条边界是否合理——有无该砍未砍/该做未做
5. §12 四项开放问题逐项给出建议裁定（标"待用户裁定"，不擅自定）
6. 前置条件（3 个 WIP 文件过门禁 + WORKTREE-REQUIRED 升硬 _THRESHOLD 5→0）——核验现状是否仍阻塞
■ 第 5 轮：一致性与交叉引用审查
1. 66 号 vs 65 号：worktree 纪律口径、逃生通道口径、pre-commit stash 处置是否一致
2. 66 号 vs 61 号：会话注册/锁协议与入队协议是否冲突（.ailocks 保留的分工边界）
3. 66 号 vs AGENTS.md §10："改完立即 add"→"改完立即入队"的演化——AGENTS.md 未改前 66 号措辞必须是"提案"而非"已生效"
4. 66 号 vs 01 号规范：frontmatter/修订记录/开放问题节是否合规
5. related_modules 路径全部真实存在性核验
■ 第 6 轮：文档质量与规范符合性
1. frontmatter 完整性（ttl/doc_type/title/owner/language/status/version/date/topic/scope）
2. 修订记录 + 开放问题节双硬约束
3. 交叉引用全用稳定 path（禁 node_id/edge_id）
4. 审查完成后：draft 保持（如开放问题未裁定）或升 v0.2.0（重大修订）/ v1.0.0 active（如裁定全部闭环且用户确认）——升版本+修订记录登记
■ 循环条件（含 git 提交闭环）：同通用规则 #7 及首个指令块「循环条件」逐字执行（每轮自检→修复→git 提交闭环→重查，直到**问题数量=0 且缺失功能/模块数量=0**——连续两轮零发现零修复，任务结束）
■ 约束
- 只改 66 号本身，引用其他文档（65/61/60/55/01/AGENTS.md）时只读不改；发现需同步改的记在 66 号开放问题节
- 你是客观专业架构师，不是辩护人——如果队列方案对个人项目过度工程，直接说并给出更轻量替代
- 不擅自定决策（需用户确认的标"待用户裁定"，尤其：方案整体采纳与否、worktree 降级、AGENTS.md §10 演化）
- plumbing 实测只能用测试仓库（如 `Test-Path $env:TEMP` 下建临时 repo），禁止在主仓做任何写操作
- 遵守通用规则 #9 git 安全铁律：每轮修改后立即 `git add` 66 号文件；禁止全区恢复命令
- 遵守通用规则 #10：修改前先 `python scripts/lock_files.py acquire <file> AI-23` 加锁，完成后 release
- 持续改进不停，循环至零问题
```
---

## 使用说明
1. **开新对话**：在 Trae/CLI 中开 23 个新对话窗口（或分批开，如每批 5-7 个并行）
2. **复制指令**：从本文档复制对应 AI 编号的指令块（` ``` ` 之间的内容）
3. **粘贴执行**：粘贴到新对话，AI 会自动开始读取文件、回填、审查、搜索、循环
4. **监控进度**：每个 AI 独立工作，互不通信，通过修改的文档文件交接
5. **冲突处理**：若两个 AI 改同一交叉引用（如 30 号被 AI-11 负责，但 AI-05/06/09/10/11/12/13/15/16 都引用），各 AI 只改自己负责的文档，引用对方文档时只读不改

> **注意**：23 个 AI 并发可能产生资源竞争（同时读同一文件 OK，但同时写不同文档时注意 git 冲突）。建议每个 AI 独立 commit，或全部完成后统一 review 合并。
> **通用纪律（适用全部 23 个 AI，下文各特殊提示不再重复）**：只改自己负责的文档本身，引用其他文档时只读不改；发现其他文档需同步改的，记在自己负责文档的开放问题/待定问题节，不越界改。
> **AI-01 特殊提示**：62 号文档是 12 个业务注册表的施工总案，与 AI-04(63号)/AI-08(64号)/AI-13(26/22号)/AI-15(25号)/AI-16(24号)/AI-18(21/17/50/51/23号)/AI-19(20/19/28/60号)/AI-20(15/27/16/52/55/33号)/AI-05(35号)/AI-06(36号)/AI-10(37号)/AI-11(32号)/AI-09(40号) 都有交叉引用。
> **AI-02 特殊提示**：10 号文档是 regime 检测器 spec，与 AI-07(13号)/AI-15(14号)/AI-16(11号)/AI-17(12号)/AI-04(63号)/AI-12(34号) 有交叉引用。
> **AI-03 特殊提示**：54 号文档是对账归因，与 AI-09(40号)/AI-11(30号)/AI-18(50号) 有交叉引用。
> **AI-04 特殊提示**：63 号文档是 101 张业务表利用率审查，数据消费方遍布全链，与 AI-01(62号)/AI-02(10号)/AI-08(64号)/AI-13(22/26号)/AI-15(25号)/AI-16(24号)/AI-17(18号)/AI-18(17/50号)/AI-19(19号)/AI-20(15/16/52号) 等几乎所有 AI 都有交叉引用。同步改示例：P0 表接入需改 26/35/37/10/32 号的数据源节（记 63 号 §10 开放问题）。AI-04 与 AI-01 强配对（62 号建 schema、63 号盘点表），两 AI 可对齐协作但各自只改自己负责的文档。
> **AI-05 特殊提示**：35 号文档是回撤 Protocol 落地，与 AI-06(36号)/AI-10(37号)/AI-11(30/32号)/AI-09(42号)/AI-10(41号) 有交叉引用。
> **AI-06 特殊提示**：36 号文档是 VaR/ES 监控，与 AI-05(35号)/AI-11(30号) 有交叉引用。
> **AI-07 特殊提示**：13 号文档是 Phase 3 工程规划，与 AI-02(10号)/AI-15(14号)/AI-16(11号)/AI-17(12号)/AI-12(34号) 有交叉引用。
> **AI-08 特殊提示**：64 号文档是数据源与下载体系规范，与 AI-04(63号)/AI-18(17号)/AI-17(18号)/AI-19(19号)/AI-20(15号) 有交叉引用。
> **AI-09 特殊提示**：40/42 号文档是执行层+卖出流，与 AI-03(54号)/AI-11(30号)/AI-05(35号)/AI-19(28号)/AI-10(37号) 有交叉引用。
> **AI-10 特殊提示**：37/41 号文档是流动性危机+买入流，与 AI-05(35号)/AI-06(36号)/AI-11(30号)/AI-13(22号)/AI-17(31号)/AI-09(42号) 有交叉引用。
> **AI-11 特殊提示**：32/30 号文档是 FirmRiskAggregator+多策略并发总纲，30 号被大量 AI 引用（AI-05/06/09/10/12/13/15/16/17/18/19/20）。
> **AI-12 特殊提示**：34/00 号文档是 RegimeMetaAllocator+总索引，00 号是全局导航文档，与几乎所有 AI 有交叉引用。00 号是索引文档，不写施工算法细节，只维护导航准确性。
> **AI-13 特殊提示**：26/22 号文档是事件驱动+板块轮动策略，与 AI-19(20号)/AI-11(30号)/AI-18(23号)/AI-16(24号)/AI-15(25号)/AI-01(62号) 有交叉引用。
> **AI-14 特殊提示**：61/53 号文档是生命周期+模拟实盘路径，与 AI-19(01/20号)/AI-11(30号)/AI-16(11号) 有交叉引用。
> **AI-15 特殊提示**：14/25 号文档是 S2 诊断+多因子策略，与 AI-02(10号)/AI-07(13号)/AI-16(11号)/AI-17(12号)/AI-19(20号)/AI-11(30号)/AI-01(62号) 有交叉引用。
> **AI-16 特殊提示**：24/11 号文档是打板策略+regime 回测验证，与 AI-02(10号)/AI-07(13号)/AI-17(12号)/AI-19(20号)/AI-11(30号)/AI-01(62号) 有交叉引用。
> **AI-17 特殊提示**：31/18/12 号文档是仓位算法+冷归档+Phase2 验证，与 AI-11(30/32号)/AI-12(34号)/AI-02(10号)/AI-07(13号)/AI-16(11号)/AI-20(15/16号)/AI-04(63号) 有交叉引用。
> **AI-18 特殊提示**：21/51/23/17/50 号文档是选股引擎+Panel+相关性+特殊交易日+可观测性，5 篇文档交叉引用广泛。与 AI-19(20号)/AI-13(26/22号)/AI-16(24号)/AI-15(25号)/AI-11(30号)/AI-08(64号)/AI-01(62号)/AI-04(63号)/AI-17(18号)/AI-19(19号)/AI-09(40号)/AI-03(54号) 有交叉引用。例外：17 号 §6.4 悬空引用修正（business_data_categories.yaml + tasks.yaml 各 1 行）可越界改。
> **AI-19 特殊提示**：20/19/01/28/60 号文档是首批策略+北向资金+管理规范+情绪周期+跨切清理。01 号是所有文档的管理规范（影响 46 篇），20 号是首批策略总纲（被 24/25/26/21/22/30 号引用），28/60 号与 AI-02(10号)/AI-11(30号) 有交叉引用。01 号改动需特别谨慎——如改规范本身，需评估对 46 篇文档的影响。
> **AI-20 特殊提示**：33/55/52/15/27/16/16 号全部是骨架文档（47-74 行空模板），核心任务是"回填已施工代码的 why"而非"审查现有内容"。与 AI-11(30号)/AI-12(34号)/AI-17(31号)/AI-09(40号)/AI-08(64号)/AI-01(62号)/AI-04(63号)/AI-19(20号)/AI-13(22号)/AI-16(24号)/AI-15(25号)/AI-13(26号)/AI-19(27号)/AI-17(18号) 有交叉引用。
> **AI-21 特殊提示**：90 号文档是方法论遗留提案 21 项（讨论文档），使用特殊的"深度调研+裁定+施工方案"指令模板（非常规 8 轮审查）。21 项提案涉及全项目方法论，与几乎所有文档有交叉引用。AI-21 是客观专业架构师，不是辩护人——如果问题本身不合理，直接说。
> **AI-22 特殊提示**：91 号文档是密度预测远期愿景（讨论文档，45 行骨架），使用特殊的"深度调研+裁定+施工方案"指令模板（非常规 8 轮审查）。与 AI-02(10号)/AI-17(31号)/AI-06(36号)/AI-05(35号) 有交叉引用。重点裁定 QNN 在单机 RTX 3090 的 2026 可行性——如不可行，明确给出删除或保留远期标注的裁定。
> **AI-23 特殊提示**：66 号文档是提交队列串行化（2026-08-12 新增治理 draft，决策备忘+施工计划），核心任务是**审查裁定新方案**而非回填——逐条裁定 §4 六项裁定，重点裁定队列方案对个人+100%AI 项目是否过度工程（vs 全局互斥锁等轻量替代）、plumbing 直写在 Windows git 2.48.1 的可行性（只许测试仓库实测，禁碰主仓）、worktree 降级与 65 号口径冲突的收口方式。与 AI-19(65/60/01号)/AI-14(61号)/AI-20(55号) 有交叉引用。65 号/AGENTS.md §10 需同步改的，记在 66 号开放问题节标「待用户裁定」。
