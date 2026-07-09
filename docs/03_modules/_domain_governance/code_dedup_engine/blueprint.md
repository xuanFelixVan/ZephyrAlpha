---

module_id: MOD-INF-017
submodule_path: src/zephyr/governance/code_dedup_engine
title: "Code Dedup Engine 蓝图 — 代码去重·爆炸半径防护·原子修复"
doc_type: blueprint
status: Active
version: 0.15.0
layer: L0_infrastructure
layer_note: "跨层模块——代码在基础设施域，但与治理域交互（Gate Engine+AiAuditLogger）"
layer_name: infrastructure
functional_domain: governance
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/governance/code_dedup/"
last_updated: "2026-05-14"
last_verified: "2026-05-14"
generation: 3
belongs_to: "MOD-GOVERNANCE"
parent_module: ""
codification_level: L2
codification_at: "2026-05-14"
priority: P2
runtime_plane: warm
rule_form: structural
scope: global
ssot_claims:
  - claim: "重复检测结果"
    scope: global
  - claim: "函数签名指纹"
    scope: global
  - claim: "Health Score"
    scope: module
  - claim: "BRS/SBS/SAS评分"
    scope: module
stability: evolving
verifiability: hybrid
depends_on:

- target: MOD-INF-005
  at: §6
  why: "退出码约定 0/1/2/3/4 + Finding Schema + manifest 注册契约"
- target: MOD-GATE_ENGINE
  at: §3
  why: "GATE-DEDUP pre-commit 门禁判定逻辑——Wave 1 即落地"
- target: MOD-CONTEXT_ENGINE
  at: "§2~§4"
  why: "生成时注入共享API影子清单——防重第一道防线 + 消费验证回环"
- target: MOD-FEEDBACK_LOOP
  at: "§3~§5"
  why: "重复模式→FLE→evolve()→EvolutionProposal 进化闭环"
- target: MOD-INF-016
  at: §2
  why: "SSoT Guard + shared 目录结构——去重后的提取目标"
- target: MOD-DATABASE
  at: §3
  why: "发现的重复模式/健忘热点→KB持久化→未来AI session 主动查阅"
- target: MOD-INF-027
  at: §3.29
  why: "decision_auditor写入审计总线——017仅为生产者"
references:
  - path: "D:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md"
    section: "REQUIRED_SECTIONS"
    why: "蓝图模板 v3.3 合规基准"
  - path: "D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml"
    section: "§4"
    why: "蓝图规格化铁律"
  - path: "D:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md"
    section: "§7"
    why: "代码十五字段头部标准"
summary: "代码去重引擎——全生命周期七维模型+46模块+Monoculture免疫(BRS)+原子修复(WAL)+决策审计链+主动函数发现+漏报盲审+微克隆检测+契约验证+跨边界感知。去重最大化悖论：找到'去重收益vs Monoculture风险vs碎片化风险vs引擎维护成本'的四体最优边界。"
tags:
  - code-dedup
  - ast-analysis
  - semantic-similarity
  - infrastructure
  - full-lifecycle
  - incremental-scanning
  - auto-fix
  - pre-commit-gate
  - ssot-integration
  - feedback_loop
  - signature-fingerprint
  - degraded-mode
  - policy-tree
  - extraction-safety
  - monoculture-immunity
  - atomic-fix-crash-recovery
  - blast-radius-score
  - self-audit
  - cross-boundary-clone
  - decision-audit-trail
responsibility_domain: 
build_status: planned
design_maturity: design
---

> module\_id: MOD-INF-017 | version: 0.15.0 | status: active | layer: l01\_infrastructure
> actual\_disk\_path: src/zephyr/l01\_infrastructure/code\_dedup\_engine/ (68 .py files) | generation: 3 | construction\_progress: partially\_implemented

# Code Dedup Engine 蓝图 — 代码去重·爆炸半径防护·原子修复·决策审计链·主动发现

> **真源声明**：本蓝图是 ZephyrAlpha 代码去重引擎的唯一真源。

## 概述

本蓝图描述 ZephyrAlpha 代码去重引擎——它解决了 Vibe Coding 场景下 AI 系统性重复生成代码的问题。核心职责包括：全生命周期七维去重模型（Prevent→Block→Audit→Fix→Register→Evolve→Self-Audit）、爆炸半径防护（BRS 爆炸半径追踪）、原子性修复（WAL 式崩溃恢复）、决策审计链（不可变追加日志）、主动函数发现（签名+语义双通道）。当前规模 46 个模块设计（66 个 .py 文件已落地），目标覆盖 342+ 函数的代码库。上游依赖 MOD-INF-005/007/008/010/012/016，下游被所有域模块消费。

***

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
>
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

***

## §0 代码对齐验证

> temporal_type: permanent
> 每次蓝图版本变更后**必须**重新填写此表。

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> 68 个 .py 全部已实现。

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-017`

| #  | 文件名                               | 对应蓝图章节 | 职责                        | 存在性 | 阻塞原因（仅已阻塞） |
| -- | --------------------------------- | ------ | ------------------------- | :-: | ---------- |
| 1  | `__init__.py`                     | §3     | 包初始化+模块职责声明               | 已实现 | —          |
| 2  | `cache_manager.py`                | §3.1   | 缓存管理（\_integrity+原子写入+自愈） | 已实现 | —          |
| 3  | `diff_detector.py`                | §3.1   | 增量变更检测（函数粒度）              | 已实现 | —          |
| 4  | `signature_matcher.py`            | §3.1   | Stage 0.5 签名碰撞检测          | 已实现 | —          |
| 5  | `scanner.py`                      | §3.1   | Token 扫描+代码块级去重           | 已实现 | —          |
| 6  | `degradation.py`                  | §3.1   | 降级运行管理                    | 已实现 | —          |
| 7  | `config.py`                       | §3.1   | 配置+惯用法豁免                  | 已实现 | —          |
| 8  | `report.py`                       | §3.1   | 报告+五档退出码                  | 已实现 | —          |
| 9  | `prioritizer.py`                  | §3.1   | 优先级排序（含 ROI）              | 已实现 | —          |
| 10 | `annotations.py`                  | §3.1   | 标记解析+决策学习                 | 已实现 | —          |
| 11 | `health_monitor.py`               | §3.1   | 健康仪表盘+Session Log         | 已实现 | —          |
| 12 | `behavioral_sampler.py`           | §3.1   | Stage 0.25 行为采样           | 已实现 | —          |
| 13 | `self_scanner.py`                 | §3.8   | 引擎自保护                     | 已实现 | —          |
| 14 | `extraction_safety.py`            | §3.6   | 安全提取评估                    | 已实现 | —          |
| 15 | `stale_shared_detector.py`        | §3     | 过期共享函数检测                  | 已实现 | —          |
| 16 | `debt_projector.py`               | §3     | 去重债务预测                    | 已实现 | —          |
| 17 | `doom_loop_guard.py`              | §3.9   | Doom Loop 防护              | 已实现 | —          |
| 18 | `shared_lifecycle_manager.py`     | §3.10  | 共享生命周期管理                  | 已实现 | —          |
| 19 | `import_surface_tracker.py`       | §3.11  | Import 负债追踪               | 已实现 | —          |
| 20 | `monoculture_guard.py`            | §3.12  | 爆炸半径防护(BRS)            | 已实现 | —          |
| 21 | `atomic_fixer.py`                 | §3.14  | 原子性修复(WAL)                | 已实现 | —          |
| 22 | `grandfather_manager.py`          | §3.13  | Grandfather 三定律           | 已实现 | —          |
| 23 | `false_negative_auditor.py`       | §3.15  | 漏报盲审                      | 已实现 | —          |
| 24 | `shadow_trust_validator.py`       | §3.16  | 影子清单信任链                   | 已实现 | —          |
| 25 | `temporal_drift_tracker.py`       | §3.17  | 签名时态漂移                    | 已实现 | —          |
| 26 | `simplicity_auditor.py`           | §3.18  | 引擎成本效益自审计                 | 已实现 | —          |
| 27 | `dead_module_detector.py`         | §3.19  | 死共享模块检测                   | 已实现 | —          |
| 28 | `observation_window_guard.py`     | §3.20  | 提取后稳定观察期                  | 已实现 | —          |
| 29 | `recovery_manifest_writer.py`     | §3.21  | 恢复失败的恢复                   | 已实现 | —          |
| 30 | `thematic_clusterer.py`           | §3.22  | 主题聚类                      | 已实现 | —          |
| 31 | `behavioral_trust_checker.py`     | §3.23  | 行为正确性验证                   | 已实现 | —          |
| 32 | `pre_apply_integrity_gate.py`     | §3.24  | 并发修改检测                    | 已实现 | —          |
| 33 | `micro_clone_detector.py`         | §3.25  | 微型克隆检测                    | 已实现 | —          |
| 34 | `auto_test_generator.py`          | §3.26  | 自动测试生成                    | 已实现 | —          |
| 35 | `contract_consistency_checker.py` | §3.27  | 契约一致性验证                   | 已实现 | —          |
| 36 | `cross_boundary_detector.py`      | §3.28  | 跨边界克隆感知                   | 已实现 | —          |
| 37 | `decision_auditor.py`             | §3.29  | 决策审计链                     | 已实现 | —          |
| 38 | `function_discovery.py`           | §3.30  | 主动函数发现                    | 已实现 | —          |
| 39 | `ast_comparator.py`               | §3.1   | Stage 2 AST 级精确比对         | 已实现 | —          |
| 40 | `auto_fixer.py`                   | §3.8   | 安全自动修复引擎                  | 已实现 | —          |
| 41 | `blind_spot_tracker.py`           | §3.15  | 盲点关闭追踪                    | 已实现 | —          |
| 42 | `canary_manager.py`               | §3.15  | 金丝雀工厂（oracle 文件生成）        | 已实现 | —          |
| 43 | `canary_register.py`              | §3.15  | 金丝雀注册表维护                  | 已实现 | —          |
| 44 | `cli.py`                          | §16.6  | CLI 子命令映射+退出码             | 已实现 | —          |
| 45 | `code_analyzer_runner.py`         | §3.15  | 敏感基线三阶段检查运行器              | 已实现 | —          |
| 46 | `code_simulator.py`               | §3     | 克隆演化序列 stress-test        | 已实现 | —          |
| 47 | `consequence_tracker.py`          | §3.8   | 修复操作对依赖方影响追踪              | 已实现 | —          |
| 48 | `exit_codes.py`                   | §5     | 五档退出码枚举+判定逻辑              | 已实现 | —          |
| 49 | `fifteen_dimension_auditor.py`    | §3     | 15 维超综合审计+审计证书            | 已实现 | —          |
| 50 | `file_creator.py`                 | §12    | 文件创建清单执行器                 | 已实现 | —          |
| 51 | `hotspot_tracker.py`              | §3     | 90 天滑动窗口热点追踪              | 已实现 | —          |
| 52 | `integration_hub.py`              | §7     | 集成协调器（24 集成+19 更新）        | 已实现 | —          |
| 53 | `integrations.py`                 | §7     | 预提交钩子+CI-only 扫描          | 已实现 | —          |
| 54 | `mock_duplicate_generator.py`     | §9     | 可控克隆生产器（测试用）              | 已实现 | —          |
| 55 | `path_index_validator.py`         | §3     | 路径索引验证（config 与文件系统同步）    | 已实现 | —          |
| 56 | `phase_executor.py`               | §16    | 6Phase 施工执行器              | 已实现 | —          |
| 57 | `policy_tree_validator.py`        | §3.5   | 策略树自动一致性校验                | 已实现 | —          |
| 58 | `question_tracker.py`             | §3     | 扫描中发现需人工处理的问题追踪           | 已实现 | —          |
| 59 | `risk_mitigation_tracker.py`      | §14    | 风险缓解追踪（N 次扫描未 fix）        | 已实现 | —          |
| 60 | `risk_mitigator.py`               | §14    | R1-R45 全量风险缓解执行器          | 已实现 | —          |
| 61 | `sensitivity_sweeper.py`          | §3.15  | 敏感性扫荡+baseline 固化         | 已实现 | —          |
| 62 | `shadow_verifier.py`              | §3.16  | 影子清单验证器（size+semantic）    | 已实现 | —          |
| 63 | `shared_evolver.py`               | §3.10  | 共享函数自我进化引擎                | 已实现 | —          |
| 64 | `ssot_registrar.py`               | §3     | 提取函数自动注册到 shared API 清单   | 已实现 | —          |
| 65 | `success_validator.py`            | §9     | 去重操作成功验证                  | 已实现 | —          |
| 66 | `symbol_index.py`                 | §3     | 全局函数/类/import 映射表         | 已实现 | —          |
| 67 | `verifier.py`                     | §3.8   | 修复验证器（import+类型+行为采样）     | 已实现 | —          |
| 68 | `self_benchmark.py`               | §3.15  | 5组已知对自验证+退化检测              | 已实现 | —          |

### §0.2 对齐验证矩阵

| 验证项                                                          | 验证方法                     |  结果 |
| ------------------------------------------------------------ | ------------------------ | :-: |
| construction\_progress = partially\_implemented → 已实现章节的代码存在 | 按章节核对                    |  ☐  |
| 蓝图描述的类/函数名 = 代码中的类/函数名                                       | `grep "class\|def" *.py` |  ☐  |
| actual\_disk\_path 与 §11 一致                                  | 比对 frontmatter 与 §11     |  ☐  |
| 磁盘额外模块（蓝图未规划）需评估                                             | `ls *.py` vs 蓝图清单        |  ☐  |

### §0.3 版本-代码映射

| 蓝图版本           | 代码覆盖范围             | 缺失组件                  | 缺失原因             |
| -------------- | ------------------ | --------------------- | ---------------- |
| v0.10.1 (基线)   | 38 个核心模块文件已存在      | semantic\_verifier.py | Wave 3——LLM 语义验证 |
| v0.11.0 (规格化)  | 同上 + 结构对齐          | —                     | —                |
| v0.12.0 (模板升级) | 蓝图结构对齐模板 v3.5/v3.6 | —                     | 本次升级             |

### §0.4 SSoT 与责任唯一性

| 数据/概念              | 真源                                                                   | 本蓝图角色    | 同步方式                   |
| ------------------ | -------------------------------------------------------------------- | -------- | ---------------------- |
| 重复检测结果             | 本蓝图（dedup\_report.yaml）                                              | **SSoT** | 下游消费本蓝图输出              |
| 函数签名指纹             | 本蓝图（function\_cache.json）                                            | **SSoT** | 缓存自管理+原子写入             |
| Health Score       | 本蓝图（health\_monitor.py）                                              | **SSoT** | Session Log 写入+趋势追踪    |
| BRS/SBS/SAS 评分     | 本蓝图（monoculture\_guard/import\_surface\_tracker/simplicity\_auditor） | **SSoT** | 月度计算+报告输出              |
| 退出码约定 0/1/2/3/4    | MOD-INF-005                                                          | 消费者      | 遵循 script-system 退出码标准 |
| GATE-DEDUP 门禁逻辑    | MOD-GATE_ENGINE                                                          | 消费者      | 遵循 gate_engine 契约      |
| shared/ 目录结构       | MOD-INF-016                                                          | 消费者      | 提取目标遵循 SSoT Guard      |
| AiAuditLogger 审计写入 | MOD-INF-027                                                          | 消费者      | 去重结果写入审计链              |
| 影子清单注入             | MOD-CONTEXT_ENGINE                                                          | 消费者      | Context Engine 注入+消费验证 |

### §0.5 代码目录唯一性

| 目录                                                 | 唯一职责                    | 冲突目录 | 判定   |
| -------------------------------------------------- | ----------------------- | ---- | ---- |
| `src/zephyr/infra_ops/code_dedup_engine/` | 代码去重检测+修复+爆炸半径防护 | 无    | ✅ 唯一 |
| `data/cache/function-cache.json`                   | 函数签名指纹缓存                | 无    | ✅ 唯一 |
| `data/cache/dedup_*.yaml`                          | 去重引擎运行时数据               | 无    | ✅ 唯一 |

***

## §1 设计背景与目标

> temporal_type: permanent

### 1.1 背景

| 问题 | 现状 | 根因 |
|------|------|------|
| AI系统性重复生成代码 | `_now_iso()`/`REPO_ROOT`/`_estimate_tokens()` 在7+文件独立实现 | AI健忘+无共享清单+无门禁拦截 |
| D-D-07 仅Type-1词法匹配 | 无法检测Type-2~4语义级重复 | 缺AST/MinHash/LLM检测能力 |
| 重复率持续上升 | 1人+AI运维模式 | 无预防+无拦截+无修复闭环 |

### 1.2 目标

| # | 目标                 | 可衡量标准                                                |
| - | ------------------ | ---------------------------------------------------- |
| 1 | 检测语义级重复（Type-1\~4） | 已知 5 组重复全部可检出，similarity ≥ 0.80                      |
| 2 | Pre-commit 门禁拦截    | GATE-DEDUP 发现 high/critical → 阻断 commit（exit code 2） |
| 3 | 安全自动修复             | Suitability Score < 40 绝不提取；修复后全量测试零失败               |
| 4 | 生成时预防              | 共享 API 影子清单注入 Context Engine → AI 重复率下降 ≥ 30%        |
| 5 | 爆炸半径防护(BRS)     | BRS ≥ 76 → 停止去重 + 生成原因报告                             |
| 6 | 原子性修复              | 中断修复后引擎自动恢复代码库到修复前状态                                 |
| 7 | 决策可追溯              | CLI `audit --since`/`audit --rollback`——任何时候都能追溯+回滚  |
| 8 | 引擎自知之明             | SAS 月度自审计——SAS < 50 触发轻量模式建议                         |

### 1.3 不包含的目标

| # | 明确排除               | 原因                                      |
| - | ------------------ | --------------------------------------- |
| 1 | 跨语言去重              | 当前只做 Python AST（Tree-sitter for Python） |
| 2 | 配置文件语义去重           | 当前项目配置规模尚小（YAML < 20 个）                 |
| 3 | SonarQube 集成       | 1 人团队不需要，本引擎独立运行                        |
| 4 | LLM 语义判断（Wave 1-2） | Stage 0.5-2 已覆盖 95%，LLM 仅 Wave 3 可选     |
| 5 | 引擎自身代码自动修复         | 引擎改引擎 = 递归不可控，只做自扫描不修复                  |

### 1.4 运行场景约束

| 约束               | 影响                                     |
| ---------------- | -------------------------------------- |
| Windows 单机部署     | 文件锁用 `os.replace()` 原子操作，SQLite WAL 足够 |
| 1人+AI 运维         | 误报消耗 Owner 时间 = 致命风险；默认偏向漏报            |
| Pre-commit 增量扫描  | 增量扫描 < 3 秒；全量扫描 < 30 秒                 |
| Vibe Coding 重复模式 | AI 健忘热点追踪 + 影子清单消费验证回环                 |

### 1.5 利益相关者映射

| 角色             | 关注点             | 参与阶段     | 约束                                  |
| -------------- | --------------- | -------- | ----------------------------------- |
| Owner          | 架构决策 + 误报时间成本   | 设计+施工+验收 | 审批 Suitability < 40 / BRS ≥ 76 / 退役 |
| AI Session     | 生成时预防 + 修复执行    | 施工       | 遵守 Vibe Coding 铁律                   |
| Gate Engine    | Pre-commit 阻断判定 | 运行时      | exit code 映射不可变                     |
| Context Engine | 影子清单注入          | 运行时      | Trust Score < 90% 拒绝注入              |

### 1.6 当前态/目标态差距

| 维度             | 当前态               | 目标态                             | 差距           | 优先级 |
| -------------- | ----------------- | ------------------------------- | ------------ | :-: |
| 重复检测           | D-D-07 Type-1 词法级 | Type-1\~4 全覆盖                   | 缺 Type-2/3/4 |  P0 |
| 门禁拦截           | 无                 | GATE-DEDUP high/critical→exit 2 | 无门禁          |  P0 |
| 自动修复           | 手动                | Suitability Score 门控+原子修复       | 无修复能力        |  P1 |
| 生成预防           | 无                 | 影子清单注入+消费验证回环                   | 无预防          |  P1 |
| 爆炸半径防护 | 无                 | BRS ≥ 76 停止去重                   | 无防护          |  P2 |
| 决策追溯           | 无                 | DecisionFingerprint 审计链         | 无追溯          |  P2 |

### 1.7 典型场景

| 场景              | 触发                                       | 处理流程                                                          | 输出                   |
| --------------- | ---------------------------------------- | ------------------------------------------------------------- | -------------------- |
| Pre-commit 增量扫描 | `git commit`                             | diff\_detector→scanner→report→exit 0/1/2/4                    | 阻断或放行                |
| 全量扫描+修复         | `cli scan --full --fix` | scanner→extraction\_safety→auto\_fixer→atomic\_fixer→verifier | FixResult+代码变更       |
| 影子清单注入          | AI session 启动                            | shadow\_trust\_validator→Context Engine build→inject          | 影子清单写入 system prompt |
| 漏报盲审            | 月度定时                                     | false\_negative\_auditor→Sensitivity Sweep+Canary+抽样          | FNR 报告               |
| 引擎自审计           | 月度定时                                     | simplicity\_auditor→SAS 计算→退役建议                               | SAS 报告               |

***

## §2 模块边界

> temporal_type: permanent

### 2.1 职责范围

| #  | 职责             | 具体内容                                                                                          |
| -- | -------------- | --------------------------------------------------------------------------------------------- |
| 1  | 全生命周期七维去重      | Prevent→Block→Audit→Fix→Register→Evolve→Self-Audit                                            |
| 2  | 多 Stage 检测流水线  | Stage 0 缓存 → Stage 0.25 行为采样 → Stage 0.5 签名碰撞 → Stage 1 Token → Stage 2 AST → Stage 3 LLM(可选) |
| 3  | 安全自动修复         | Suitability Score + 不安全模式目录 + 部分提取 + 原子性修复(WAL)                                               |
| 4  | 爆炸半径防护(BRS) | BRS 爆炸半径追踪 + 去重悖论显式评估 + 停止高风险去重                                                               |
| 5  | 共享函数生命周期       | 5 阶段状态机（Active→Deprecated→Grace→Sunset→Retired）                                               |
| 6  | 漏报盲审           | Sensitivity Sweep + Canary 注入 + 抽样审查——FNR 可量化                                                 |
| 7  | 影子清单信任链        | import 存活校验 + 幻觉清除 + 行为正确性验证 + 契约一致性                                                          |
| 8  | 决策审计链          | DecisionFingerprint 不可变追加日志 + 证据包 + 可回滚                                                       |
| 9  | 主动函数发现         | 签名驱动(Channel A) + 语义驱动(Channel B) 双通道                                                         |
| 10 | 引擎自审计          | SAS 成本效益自审计 + 死模块检测 + Simplicity Audit                                                        |

### §2.1.1 职责唯一性声明

本蓝图的核心职责是：**全生命周期代码去重**。职责数量：10。

| 职责 | 与其他模块重叠？ | 边界声明 |
|------|:---:|---------|
| 代码重复检测 | ❌ | 无重叠——唯一做Token级代码去重的模块 |
| 爆炸半径防护(BRS) | ⚠️ | MOD-INF-028/030 也有"blast_radius"但语义不同：017=代码共享度指标，028=文档引用指标，030=混沌工程范围 |
| 原子修复 | ⚠️ | MOD-INF-031(Auto Fix Engine)也有WAL修复——017保留去重专用修复，通用修复委托031 |
| 决策审计链 | ❌ | 写入MOD-INF-027审计总线，017仅为生产者 |
| 主动函数发现 | ❌ | 无重叠 |
| 漏报盲审 | ❌ | 无重叠 |
| 微克隆检测 | ❌ | 无重叠 |
| 契约验证 | ❌ | 无重叠 |
| 跨边界感知 | ❌ | 无重叠 |
| 引擎自审计 | ❌ | 无重叠 |

### 2.2 不包含的职责

| # | 排除项                 | 由谁负责                        |
| - | ------------------- | --------------------------- |
| 1 | 退出码/脚本注册标准          | MOD-INF-005（Script System）  |
| 2 | 门禁判定引擎              | MOD-GATE_ENGINE（Gate Engine）    |
| 3 | Context Engine 注入逻辑 | MOD-CONTEXT_ENGINE（Context Engine） |
| 4 | 进化信号处理              | MOD-FEEDBACK_LOOP（Feedback Loop）  |
| 5 | Shared Core 目录结构    | MOD-INF-016（Shared+Core）    |
| 6 | KB 持久化 API          | MOD-DATABASE（Knowledge Base） |

***

## §3 架构设计

> temporal_type: permanent

### 3.1 组件架构

| #  | 组件                                | 职责                         | 依赖                                            | 交互方式                  |
| -- | --------------------------------- | -------------------------- | --------------------------------------------- | --------------------- |
| 1  | `cache_manager.py`                | 缓存管理（\_integrity+原子写入+自愈）  | —                                             | 同步调用                  |
| 2  | `diff_detector.py`                | 增量变更检测（函数粒度）               | git                                           | 同步调用                  |
| 3  | `signature_matcher.py`            | Stage 0.5 签名碰撞检测           | cache\_manager                                | 同步调用                  |
| 4  | `behavioral_sampler.py`           | Stage 0.25 行为采样验证          | config                                        | subprocess 隔离         |
| 5  | `scanner.py`                      | Token 扫描+代码块级去重            | config, cache\_manager                        | 同步调用                  |
| 6  | `degradation.py`                  | 降级运行管理                     | scanner, signature\_matcher                   | 同步调用                  |
| 7  | `config.py`                       | 配置+惯用法豁免+设计模式白名单           | —                                             | 同步调用                  |
| 8  | `report.py`                       | 报告生成+五档退出码                 | scanner                                       | 同步调用                  |
| 9  | `prioritizer.py`                  | 优先级排序（含 ROI 因子）            | scanner                                       | 同步调用                  |
| 10 | `health_monitor.py`               | 健康仪表盘+Session Log+SBS 聚合   | scanner, report                               | 同步调用                  |
| 11 | `annotations.py`                  | 标记解析+Owner 决策模式学习          | scanner                                       | 同步调用                  |
| 12 | `extraction_safety.py`            | 安全提取评估（Suitability Score）  | scanner                                       | 同步调用                  |
| 13 | `auto_fixer.py`                   | 自动修复引擎（含部分提取）              | extraction\_safety, verifier                  | 同步调用                  |
| 14 | `atomic_fixer.py`                 | 原子性修复（WAL+CHECKPOINT+崩溃恢复） | auto\_fixer                                   | 同步调用+文件锁              |
| 15 | `verifier.py`                     | 修复后验证（测试+import+循环依赖）      | auto\_fixer                                   | subprocess(pytest)    |
| 16 | `ssot_registrar.py`               | SSoT 注册+KB 持久化             | auto\_fixer                                   | 同步调用                  |
| 17 | `monoculture_guard.py`            | 爆炸半径防护（BRS+去重悖论）   | auto\_fixer, health\_monitor                  | 同步调用                  |
| 18 | `doom_loop_guard.py`              | Doom Loop 防护（升级阶梯+冻结）      | auto\_fixer                                   | 同步调用                  |
| 19 | `shared_lifecycle_manager.py`     | 共享生命周期管理（5 阶段状态机）          | ssot\_registrar                               | 同步调用                  |
| 20 | `import_surface_tracker.py`       | Import 负债追踪（SBS+热图）        | health\_monitor                               | 同步调用                  |
| 21 | `grandfather_manager.py`          | Grandfather 三定律            | cache\_manager                                | 同步调用                  |
| 22 | `false_negative_auditor.py`       | 漏报盲审（Sweep+Canary+抽样）      | scanner                                       | 同步调用                  |
| 23 | `shadow_trust_validator.py`       | 影子清单信任链                    | ssot\_registrar                               | subprocess(import 校验) |
| 24 | `temporal_drift_tracker.py`       | 签名时态漂移追踪                   | cache\_manager                                | 同步调用                  |
| 25 | `simplicity_auditor.py`           | 引擎成本效益自审计（SAS）             | health\_monitor                               | 同步调用                  |
| 26 | `dead_module_detector.py`         | 死共享模块检测                    | shared\_lifecycle\_manager                    | 同步调用                  |
| 27 | `observation_window_guard.py`     | 提取后稳定观察期                   | atomic\_fixer                                 | 定时器+事件                |
| 28 | `recovery_manifest_writer.py`     | 恢复失败的恢复（R2 纯文本 Manifest）   | atomic\_fixer                                 | 同步调用                  |
| 29 | `thematic_clusterer.py`           | 噪声信号比·主题聚类                 | scanner                                       | 同步调用                  |
| 30 | `behavioral_trust_checker.py`     | 影子清单行为正确性验证                | shadow\_trust\_validator                      | subprocess            |
| 31 | `pre_apply_integrity_gate.py`     | 并发修改检测（Pre-Apply SHA256）   | atomic\_fixer                                 | 同步调用+文件锁              |
| 32 | `micro_clone_detector.py`         | 微型克隆检测（n-gram 频率计数）        | scanner                                       | 同步调用                  |
| 33 | `auto_test_generator.py`          | 提取后自动测试生成                  | atomic\_fixer, monoculture\_guard             | subprocess(pytest)    |
| 34 | `contract_consistency_checker.py` | API 契约一致性验证                | shadow\_trust\_validator                      | 同步调用                  |
| 35 | `cross_boundary_detector.py`      | 跨边界克隆感知                    | scanner                                       | 同步调用                  |
| 36 | `decision_auditor.py`             | 去重决策审计链                    | atomic\_fixer, shadow\_trust\_validator       | 同步调用                  |
| 37 | `function_discovery.py`           | 共享函数主动发现（签名+语义双通道）         | shadow\_trust\_validator, thematic\_clusterer | 同步调用                  |
| 38 | `self_scanner.py`                 | 引擎自保护（自扫描+Codegen 防护+依赖自检） | scanner                                       | 同步调用                  |

### 3.2 数据流

| # | 上游             | 处理逻辑                                                   | 下游             | 数据格式                   |
| - | -------------- | ------------------------------------------------------ | -------------- | ---------------------- |
| 1 | git diff       | diff\_detector → 变更 .py 文件 → 函数粒度增量                    | scanner        | `FunctionChange[]`     |
| 2 | 变更函数           | signature\_matcher → SHA256\[:12] O(1) 精确匹配            | scanner        | `SignatureCollision[]` |
| 3 | 变更函数           | scanner → MinHash + LSH → 候选对                          | report         | `DuplicateGroup[]`     |
| 4 | DuplicateGroup | extraction\_safety → Suitability Score 评估              | auto\_fixer    | `SuitabilityVerdict`   |
| 5 | Suitable Group | auto\_fixer → 提取→替换→分批执行                               | atomic\_fixer  | `FixPlan`              |
| 6 | FixPlan        | atomic\_fixer → WAL PREFLIGHT→CHECKPOINT→APPLY→RECOVER | verifier       | `FixResult`            |
| 7 | FixResult      | ssot\_registrar → SSoT 注册 + KB 持久化                     | b\_shared.yaml | `RegistrationEntry`    |
| 8 | 全量扫描结果         | health\_monitor → Health Score + Session Log 写入        | Session Log    | `DedupSummary`         |

### 3.3 状态生命周期

#### 3.3.1 共享函数生命周期（5 阶段）

| 状态         | 含义                     | 转换条件                        |
| ---------- | ---------------------- | --------------------------- |
| Active     | 正常使用，影子清单推荐            | → Deprecated: 调用方 < 2 且存在替代 |
| Deprecated | 不推荐新 session 使用，影子清单降级 | → Grace: 30 天后自动            |
| Grace      | 宽限期，仍可调用但告警            | → Sunset: 宽限期结束             |
| Sunset     | 阻断 pre-commit 引用       | → Retired: Owner 确认迁移完成     |
| Retired    | 归档，KB 保留指纹防重新发明        | 终态                          |

#### 3.3.2 修复升级阶梯（L0-L4）

| 级别 | 策略                      | 触发条件                      |
| -- | ----------------------- | ------------------------- |
| L0 | Direct Fix              | 行为采样一致 + Suitability ≥ 70 |
| L1 | Partial Fix（LCS 公共核心提取） | 部分重复 + Suitability ≥ 60   |
| L2 | Retry Once              | 修复失败一次，重试                 |
| L3 | Escalate to Owner       | 2 次失败，生成 TaskCard         |
| L4 | Stop + Freeze           | 3 次失败，冻结该 DUP group       |

#### 3.3.3 提取后观察期

| 状态        | 含义             | 转换条件               |
| --------- | -------------- | ------------------ |
| OBSERVING | 14 天观察窗口，暂停新提取 | → RESUMED: 14 天无回归 |
| FRAGILE   | 观察期内触发 ≥ 2 回归  | → ROLLBACK: 自动回滚提取 |

### 蓝图特有：全生命周期七维模型

| 维度 | 阶段         | 核心模块                                                               | 核心指标                          |
| -- | ---------- | ------------------------------------------------------------------ | ----------------------------- |
| 1  | Prevent    | function\_discovery + shadow\_trust\_validator + Context Engine    | AI 重复率下降 ≥ 30%                |
| 2  | Block      | scanner + GATE-DEDUP + signature\_matcher                          | high/critical → exit 2        |
| 3  | Audit      | false\_negative\_auditor + decision\_auditor + thematic\_clusterer | FNR 可量化                       |
| 4  | Fix        | auto\_fixer + atomic\_fixer + extraction\_safety                   | 修复安全率 100%                    |
| 5  | Register   | ssot\_registrar + shared\_lifecycle\_manager                       | SSoT 注册闭环                     |
| 6  | Evolve     | feedback\_loop + hotspot\_tracker + debt\_projector                | evolve() 产出 EvolutionProposal |
| 7  | Self-Audit | simplicity\_auditor + dead\_module\_detector + self\_scanner       | SAS 月度计算                      |

### 蓝图特有：检测矩阵（18 维）

| #  | 检测维度          | Stage | 核心算法                                             |  误报率  |
| -- | ------------- | :---: | ------------------------------------------------ | :---: |
| 1  | 精确重复（Type-1）  |  0.5  | SHA256\[:12] 签名碰撞                                |   0%  |
| 2  | 重命名重复（Type-2） |   1   | MinHash + LSH                                    |  < 5% |
| 3  | 结构重复（Type-3）  |   2   | AST 子树哈希 + docstring 剥离                          | < 10% |
| 4  | 语义重复（Type-4）  |   3   | LLM 置信度评分（可选）                                    | < 15% |
| 5  | 部分重复          |   2   | LCS 公共核心识别                                       | < 10% |
| 6  | 参数化模板         |   2   | 同名前缀聚类 + 结构相似度 > 0.7                             |  < 8% |
| 7  | 非函数结构         |   1   | 常量/import/类/枚举/类型别名检测                            |  < 5% |
| 8  | 代码块级          |   1   | 滑动窗口 MinHash（min\_block\_size=5）                 | < 10% |
| 9  | 行为采样          |  0.25 | 类型推断→沙箱执行→输出 diff                                |  < 3% |
| 10 | 路径感知          |   1   | 分区阈值（shared 0.3 / core 0.6 / \* 0.7 / tests 0.9） |   —   |
| 11 | 项目规模感知        |   0   | 四 Tier 自适应阈值                                     |   —   |
| 12 | Python 惯用法豁免  |   0   | IDIOM\_WHITELIST + DESIGN\_PATTERN\_WHITELIST    |   —   |
| 13 | 微克隆检测         |   1   | n-gram 频率计数 L0/L1/L2 三级                          | < 15% |
| 14 | 自动测试生成        |   —   | 类型驱动边界测试+金丝雀录制+契约测试                              |   —   |
| 15 | 契约一致性         |   —   | docstring+类型+影子清单+异常契约四层                         |   —   |
| 16 | 跨边界克隆         |   1   | 四大边界差异化检测+独立策略                                   |   —   |
| 17 | 决策审计链         |   —   | DecisionFingerprint 不可变追加日志                      |   —   |
| 18 | 主动函数发现        |   —   | 签名驱动(Channel A) + TF-IDF 语义驱动(Channel B)         |   —   |

### 蓝图特有：安全提取适配性评估（Suitability Score）

| Score | Verdict       | 行为                                                      |
| :---: | ------------- | ------------------------------------------------------- |
|  < 40 | UNSAFE        | 绝不提取——7 类不安全模式（高调用方/平台代码/公开API/性能热点/生成代码/Vendored/stub） |
| 40-69 | NEEDS\_REVIEW | 需 Owner 确认                                              |
|  ≥ 70 | SAFE          | 可自动提取                                                   |

**不安全提取模式目录**（NEVER auto-extract）：

| # | 模式                  | 原因       |
| - | ------------------- | -------- |
| 1 | 高调用方函数（caller > 10） | 提取影响面过大  |
| 2 | 平台特定代码              | 跨平台兼容性   |
| 3 | 公开 API 端点           | 接口稳定性承诺  |
| 4 | 性能热点函数              | 内联优于调用   |
| 5 | 生成代码（codegen）       | 被覆盖风险    |
| 6 | Vendored 代码         | 不属于项目控制  |
| 7 | Stub/骨架函数           | 尚未实现完整逻辑 |

### 蓝图特有：项目规模感知四 Tier

| Tier |      代码行数     | 策略            | shared 阈值 | 影子清单条目 |
| :--: | :-----------: | ------------- | :-------: | :----: |
|   1  |    < 5,000    | 偏漏报——减少误报干扰   |    0.30   |  ≤ 20  |
|   2  |  5,000-15,000 | 平衡            |    0.40   |  ≤ 40  |
|   3  | 15,000-50,000 | 偏检出——重复成本上升   |    0.50   |  ≤ 70  |
|   4  |    > 50,000   | 激进拦截——重复率指数上升 |    0.60   |  ≤ 100 |

### 蓝图特有：爆炸半径防护（BRS）

| BRS 范围 | 行为                           |
| ------ | ---------------------------- |
| 0-50   | 正常去重                         |
| 51-75  | 强烈建议增加独立单元测试                 |
| ≥ 76   | **停止去重**——"风险优先于简洁" + 生成原因报告 |

**SBS 联动**：SBS ≥ 31 → 提取门槛自动提升至 Suitability ≥ 70；SBS ≥ 76 → 建议分拆 shared/

### 蓝图特有：Grandfather 三定律

| 定律   | 规则                                                   |
| ---- | ---------------------------------------------------- |
| 第一定律 | ≥ 30 天的重复永不自动修复（`auto_fix = false`）                  |
| 第二定律 | ≥ 60 天 → 化石记录（降级为 informational，不参与 Health Score 减值） |
| 第三定律 | 考古测试——无 caller 独立测试 + 无 rollback plan → 拒绝提取         |

### 蓝图特有：漏报盲审三层机制

| 层  | 机制                               | 频率     | 产出                              |
| -- | -------------------------------- | ------ | ------------------------------- |
| L1 | Sensitivity Sweep（降低阈值+diff）     | 月度     | `sensitivity_sweep_report.yaml` |
| L2 | Canary 注入（5-10 组已知重复自动验证）        | 每次全量扫描 | `canary_report.yaml`            |
| L3 | Sampled Human Audit（每周 10 组随机审查） | 周度     | Owner 反馈                        |

### 蓝图特有：影子清单三维信任模型

| 维度    |  权重 | 检查内容                        | 不通过处置                           |
| ----- | :-: | --------------------------- | ------------------------------- |
| 存在性   | 30% | import 存活校验                 | 幻觉函数自动清除                        |
| 行为正确性 | 40% | behavior\_signature 录制+采样验证 | DIVERGED 告警+根因分析                |
| 契约一致性 | 30% | docstring+类型+异常契约四层         | TYPE\_UNDERAPPROXIMATED → 告警不注入 |

**Trust Score < 90% → 拒绝注入 + 降级"无清单模式"**

### 蓝图特有：跨边界克隆感知

| 边界                         | 检测策略                    | auto\_fix 策略            |
| -------------------------- | ----------------------- | ----------------------- |
| SRC\_TEST\_BRIDGE          | src vs tests 高阈值(0.9)   | 仅 WARN                  |
| SRC\_SCRIPTS\_DIVERGENCE   | src vs scripts 中阈值(0.7) | 仅 WARN                  |
| CROSS\_LAYER\_REDUNDANCY   | 基础设施域 vs 治理域跨层           | **可 auto\_fix**——最高价值目标 |
| VENDORED\_REIMPLEMENTATION | src vs vendored         | 仅检测不修复                  |

### 蓝图特有：引擎自审计（Simplicity Audit）

| SAS 范围 | 行为                         |
| ------ | -------------------------- |
| ≥ 50   | 正常运行                       |
| 25-49  | 持续 3 月 → 自动触发轻量模式（只检测不修复）  |
| < 25   | 生成退役建议——"关闭修复功能可月度节省 X 小时" |

### 蓝图特有：关键数据格式

#### function\_cache.json

```json
{
  "_version": "1.0",
  "_generated_at": "2026-05-14T10:30:00Z",
  "_integrity": "sha256:abcdef123456",
  "_tier": 2,
  "functions": {
    "module.path:func_name:sig_hash": {
      "module": "zephyr.shared.time_utils",
      "name": "now_iso",
      "signature_fingerprint": "a1b2c3d4e5f6",
      "minhash_signature": [12345, 67890, ...],
      "ast_hash": "sha256:...",
      "last_modified": "2026-05-14T10:30:00Z",
      "line_count": 5,
      "category": "utility",
      "stability": "stable"
    }
  }
}
```

#### dedup\_report.yaml

```yaml
scan_metadata:
  timestamp: "2026-05-14T10:30:00Z"
  mode: incremental
  stage_completed: [0.25, 0.5, 1]
  degradation_level: 0
  tier: 2
  total_functions: 342
  scanned_functions: 12
duplicate_groups:
  - group_id: "DUP-20260514-001"
    severity: high
    similarity: 0.95
    category: accidental
    members:
      - module: "zephyr.shared.time_utils"
        name: "now_iso"
        path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\time_utils.py"
        line_range: [15, 20]
    suitability_score: 85
    verdict: SAFE
health_score:
  overall: 72
  trend: "↑"
  dimensions:
    dedup_coverage: 85
    stale_shared_count: 2
    sbs: 28
    brs_max: 45
    micro_clone_density: 12
```

#### config/policy\_tree.yaml（Wave 3 落地）

```yaml
policy_tree:
  - condition: "severity == critical AND affected_files >= 3"
    action: block_commit
    exit_code: 2
  - condition: "severity == high AND similarity >= 0.85"
    action: block_commit
    exit_code: 2
  - condition: "category == intentional"
    action: suppress
    exit_code: 0
  - condition: "suitability_score < 40"
    action: never_auto_fix
  - condition: "brs >= 76"
    action: stop_dedup
    report: true
```

#### fix\_plan.yaml

```yaml
plan:
  plan_hash: "sha256:abc123..."
  dup_id: "DUP-20260505-012"
  status: "in_progress"
  steps:
    - step: 1
      action: "CREATE_FILE"
      file: "src/zephyr/shared/time_utils.py"
      expected_sha256: "sha256:111..."
      depends_on: []
      completed: true
    - step: 2
      action: "MODIFY_FILE"
      file: "src/zephyr/factor/factor_registry.py"
      expected_sha256: "sha256:222..."
      depends_on: [1]
      completed: false
      diff: |
        -from .time_utils import _now_iso
        +from zephyr.shared.time_utils import now_iso
  crash_marker: "checkpoint saved at fix_checkpoint_abc123.tar.gz"
  completion_marker: null
```

#### grandfather\_registry.yaml

```yaml
grandfathered_duplicates:
  - dup_id: "DUP-20251101-007"
    first_detected: "2025-11-01"
    age_days: 186
    status: "FOSSILIZED"
    functions: ["_parse_args_old", "parse_cli_args"]
    callers: ["cli/report.py", "cli/scan.py"]
    archaeology:
      first_commit: "abc1234 (2025-10-15)"
      callers_with_tests: 1
      rollback_plan: "git revert <fix-commit>"
    recommendation: "KEEP——考古测试未通过"
```

***

## §4 接口契约

> temporal_type: permanent

### 4.1 公共 API

```python
class CodeDedupEngine:
    """代码去重引擎主类——全生命周期七维去重"""

    def scan(self, mode: str = "incremental", paths: list[Path] | None = None) -> "DedupReport":
        """
        执行去重扫描
        输入：mode=incremental|full|file, paths=扫描范围
        输出：DedupReport 含 duplicate_groups + health_score
        """

    def fix(self, group_ids: list[str], batch_size: int = 3, dry_run: bool = False) -> "FixResult":
        """
        自动修复指定重复组
        输入：group_ids=DUP 组 ID, batch_size=每批修复数, dry_run=预览模式
        输出：FixResult 含 fix_plan + verification_result
        """

    def audit(self, since: str | None = None, rollback_id: str | None = None) -> "AuditResult":
        """
        查询决策审计日志
        输入：since=起始日期, rollback_id=回滚指定决策
        输出：AuditResult 含 decision_log + rollback_status
        """

    def discover(self, signature: str | None = None, semantic: str | None = None) -> "DiscoveryResult":
        """
        主动函数发现
        输入：signature=函数签名, semantic=语义描述
        输出：DiscoveryResult 含 exact_matches + close_matches
        """
```

| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| scan() | diff_detector→signature_matcher→scanner→report→exit_code | severity阈值(策略树) |
| fix() | extraction_safety→auto_fixer→atomic_fixer→verifier→ssot_registrar | Suitability<40=UNSAFE阻断 |
| audit() | decision_auditor查询→审计链输出 | 审计链不可变追加 |
| discover() | function_discovery双通道(签名+语义) | 置信度<0.7=低置信 |

### 4.2 数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CloneType(str, Enum):
    TYPE_1 = "Type-1"
    TYPE_2 = "Type-2"
    TYPE_3 = "Type-3"
    TYPE_4 = "Type-4"

class SuitabilityVerdict(str, Enum):
    UNSAFE = "UNSAFE"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    SAFE = "SAFE"

class DuplicateGroup(BaseModel):
    group_id: str = Field(..., description="DUP-YYYYMMDD-NNN")
    severity: Severity
    similarity: float = Field(..., ge=0.0, le=1.0)
    clone_type: CloneType
    category: str = Field(..., description="accidental/intentional/needs_review")
    members: list["FunctionRef"]
    suitability_score: int = Field(default=0, ge=0, le=100)
    verdict: SuitabilityVerdict | None = None

class FunctionRef(BaseModel):
    module: str
    name: str
    path: str
    line_range: tuple[int, int]

class DedupReport(BaseModel):
    scan_metadata: "ScanMetadata"
    duplicate_groups: list[DuplicateGroup]
    health_score: "HealthScore"

class HealthScore(BaseModel):
    overall: int = Field(..., ge=0, le=100)
    trend: str = Field(..., description="↑↓→")
    dimensions: dict[str, int | float]
```

### 4.3 输入契约

| 接口           | 输入字段          |  必填 | 约束                          |
| ------------ | ------------- | :-: | --------------------------- |
| `scan()`     | `mode`        |  ✅  | `incremental`/`full`/`file` |
| `scan()`     | `paths`       |  ❌  | Path 列表，必须存在                |
| `fix()`      | `group_ids`   |  ✅  | 非空列表，group\_id 格式 `DUP-*`   |
| `fix()`      | `batch_size`  |  ❌  | 1-3，默认 3                    |
| `fix()`      | `dry_run`     |  ❌  | bool，默认 False               |
| `audit()`    | `since`       |  ❌  | ISO 8601 日期                 |
| `audit()`    | `rollback_id` |  ❌  | DecisionFingerprint         |
| `discover()` | `signature`   |  ❌  | 函数签名格式                      |
| `discover()` | `semantic`    |  ❌  | 自然语言描述                      |

### 4.4 输出契约

| 接口           | 成功输出                              | 失败输出                                          |
| ------------ | --------------------------------- | --------------------------------------------- |
| `scan()`     | `DedupReport` + exit code 0/1/2/4 | exit code 3（TOOL-ERROR）                       |
| `fix()`      | `FixResult` + 修复后代码变更             | `FixAbortedError` / `VerificationFailedError` |
| `audit()`    | `AuditResult` + 决策日志              | `RollbackFailedError`                         |
| `discover()` | `DiscoveryResult` + 匹配列表          | 空结果（非错误）                                      |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。去重引擎通过 CLI 脚本和 Gate Engine 集成运行。

### 4.6 契约版本

| 契约部分                    |   兼容性  | 说明             |
| ----------------------- | :----: | -------------- |
| 新增检测维度                  | ✅ 向后兼容 | 不影响已有消费者       |
| 修改 severity 判定规则        | ⚠️ 需通知 | 可能改变 exit code |
| 修改 Suitability Score 算法 | ⚠️ 需通知 | 可能改变修复决策       |
| 新增数据模型字段                | ✅ 向后兼容 | Pydantic 默认值   |
| 修改 Health Score 计算公式    | ⚠️ 需通知 | 趋势可能反转         |

### 4.7 OCP 扩展点

| 扩展点      | 基类/接口                               | 默认实现            | 扩展契约                                               | 注册方式             |
| -------- | ----------------------------------- | --------------- | -------------------------------------------------- | ---------------- |
| 检测 Stage | BaseDetector                        | Stage 0.5→1→2→3 | 新 Stage MUST 声明 input/output Pydantic Model + 降级策略 | config.py STAGES |
| 策略树规则    | policy\_tree.yaml 规则条目              | 5 条硬编码规则        | 新规则 MUST 声明 condition+action+exit\_code            | YAML 追加          |
| 不安全提取模式  | extraction\_safety.UNSAFE\_PATTERNS | 7 类内置模式         | 新模式 MUST 声明 pattern+reason+severity                | config.py 追加     |

***

## §5 约束条件

> temporal_type: permanent

### 5.1 技术约束

| # | 约束                                             | 值                 |
| - | ---------------------------------------------- | ----------------- |
| 1 | Python 3.12+ + Pydantic V2                     | 项目标准              |
| 2 | Tree-sitter Python grammar 版本锁定                | 防止 AST 解析失败       |
| 3 | 原子写入：temp-file + `os.replace()`                | Windows NTFS 原子操作 |
| 4 | 缓存 `_integrity` SHA256 校验                      | 防止缓存损坏导致误判        |
| 5 | 沙箱执行限制：256MB + 500ms + 白名单模块                   | 行为采样安全性           |
| 6 | 单次 `--fix` 最多修改 3 组重复                          | 防止改动范围过大          |
| 7 | `IDIOM_WHITELIST` + `DESIGN_PATTERN_WHITELIST` | 减少误报              |
| 8 | 路径感知阈值                                         | 不同目录不同严格度         |

### 5.2 容量估算

| 维度   |    当前规模   |    峰值需求   |  系统极限  | 是否够用 | 扩展方案                             |
| ---- | :-------: | :-------: | :----: | :--: | -------------------------------- |
| 函数数  |    342    |   1,500   | 10,000 |   ✅  | MinHash LSH O(n) 近似              |
| 增量扫描 |   5 函数变更  |  50 函数变更  |    —   |   ✅  | 缓存免除重复 AST 解析                    |
| 全量扫描 |   342 函数  |  1,500 函数 | 10,000 |   ✅  | Tier 自适应阈值                       |
| 缓存大小 |   \~2MB   |   \~10MB  |    —   |   ✅  | 增量更新 + 自愈重建                      |
| 修复并发 | 1 session | 2 session |    —   |   ✅  | PID 锁 + Pre-Apply Integrity Gate |

### 5.3 迁移/废弃方案

> temporal_type: construction_temporary

| # | 废弃/迁移对象 | 当前位置 | 目标位置    | 处理方式                        | 执行状态 |
| - | ------- | ---- | ------- | --------------------------- | :--: |
| 1 | 退役路径文档化 | —    | 本蓝图 §17 | 引擎月度维护 > 2h 持续 3 月 → 触发退役评估 |  未执行 |

### 5.4 非功能需求与服务水平

| 维度   | NFR目标   | SLI                       | SLO       | 告警阈值            |
| ---- | ------- | ------------------------- | --------- | --------------- |
| 可用性  | ≥ 99.5% | exit 0/1/2 占比             | ≥ 99.5%   | exit 3 连续 ≥ 2 次 |
| 增量延迟 | < 3s    | scan\_duration\_p50\_ms   | < 3000ms  | p50 > 5s        |
| 全量延迟 | < 30s   | scan\_duration\_p99\_ms   | < 30000ms | p99 > 60s       |
| 修复延迟 | < 60s   | fix\_duration\_ms         | < 60000ms | > 120s          |
| 精准率  | ≥ 80%   | false\_positive\_rate\_7d | < 20%     | FPR > 30%       |
| 安全率  | 100%    | fix\_safety\_rate         | 100%      | 任何修复后测试失败       |
| 幂等性  | 100%    | idempotency\_rate         | 100%      | group\_id 不一致   |

### 5.7 禁止模式与导入约束

| # | 禁止项                               | 替代                                                            | 原因         |
| - | --------------------------------- | ------------------------------------------------------------- | ---------- |
| 1 | open(path,"w") 直接写                | temp-file+os.replace()                                        | NTFS 并发安全  |
| 2 | for+subprocess.run() 串行           | ThreadPoolExecutor(max\_workers=8)                            | RULE-SEVEN |
| 3 | TODO/.../pass/NotImplementedError | 完整实现                                                          | 防幻觉 #7     |
| 4 | @dataclass                        | Pydantic V2 BaseModel                                         | KBG-0040   |
| 5 | from zephyr.l05\_\* import \*     | from zephyr.l01\_infrastructure.code\_dedup\_engine import \* | 分层约束       |
| 6 | open(path,'w') 省略 encoding        | open(path,'w',encoding='utf-8')                               | 编码安全       |

### §5.5 自动化触发机制

| 操作 | 触发方式 | 触发源 | 自动化程度 |
|------|---------|--------|:---------:|
| 增量扫描 | auto_event | git commit → pre-commit hook | 全自动 |
| 全量扫描 | on_demand | `python -m zephyr.infra_ops.code_dedup_engine.cli scan --full` | 半自动 |
| 修复执行 | on_demand | `python -m zephyr.infra_ops.code_dedup_engine.cli fix` | 半自动(需--fix) |
| 漏报盲审 | auto_scheduled | CircadianScheduler 月度 | **未接通** |
| 引擎自审计 | auto_scheduled | CircadianScheduler 月度 | **未接通** |
| 敏感性扫荡 | auto_scheduled | CircadianScheduler 月度 | **未接通** |
| 影子清单注入 | auto_boot | AI session 启动时 Context Engine | 依赖 MOD-CONTEXT_ENGINE |
| GATE-DEDUP | auto_event | GateEngine.evaluate("GATE-DEDUP") | 全自动 |
| 重复模式进化 | auto_event | FLE detect → dedup_pattern_report | 依赖 MOD-FEEDBACK_LOOP |

***

## §6 错误处理

> temporal_type: permanent

| # | 异常场景                         | 检测方式                   | 恢复策略                                  | 影响范围             |
| - | ---------------------------- | ---------------------- | ------------------------------------- | ---------------- |
| 1 | AST 解析失败                     | Stage 2 try/except     | 降级到 Stage 0.5+1，exit code 4（DEGRADED） | 降级扫描结果           |
| 2 | 缓存损坏                         | `_integrity` SHA256 校验 | 自动 full rebuild → Session Log 记录      | 首次扫描变慢           |
| 3 | 修复中断（断电/OOM）                 | 残留 checkpoint 检测       | WAL 式自动恢复原始文件                         | 代码库一致性           |
| 4 | Doom Loop（修复→break→修复→break） | 3 次失败检测                | L4 冻结 + Owner 告警                      | 该 DUP group 停止修复 |
| 5 | 影子清单幻觉函数                     | import 存活校验            | 幻觉自动清除 + Trust Score 更新               | AI session 导入安全  |
| 6 | 签名时态漂移                       | 连续 3 次 fingerprint 不同  | UNSTABLE 标记 → Stage 0.5 skip          | Stage 0.5 命中率下降  |
| 7 | 并发写入冲突                       | Pre-Apply SHA256 重验证   | ABORT + 冲突报告 + fix\_plan 自动重生成        | 修复中止             |
| 8 | Tree-sitter grammar 版本漂移     | 兼容性自检（10 个已知语法特征）      | 降级到 Stage 0.5+1，exit code 4           | CI 不阻断           |
| 9 | Codegen 覆盖手动修复               | SHA256 哈希白名单比对         | 检测→Session Log 写入+修复 diff             | __init__.py 恢复   |

### 退出码约定（对齐 MOD-INF-005）

| 退出码 | 含义                    | 触发条件                           |         Gate Engine 判定        |
| :-: | --------------------- | ------------------------------ | :---------------------------: |
|  0  | ✅ PASS — 无重复          | 扫描范围内零重复组                      |        GATE-DEDUP PASS        |
|  1  | ⚠️ WARN — 低/中重复       | 所有重复组 severity ≤ medium        |        GATE-DEDUP WARN        |
|  2  | ❌ ERROR — 高/严重重复      | 任意 severity = high or critical |   GATE-DEDUP FAIL（阻断 commit）  |
|  3  | 🔧 TOOL-ERROR — 扫描器故障 | AST 解析失败 / cache 损坏且自愈失败       |        GATE-DEDUP SKIP        |
|  4  | ⚡ DEGRADED — 降级运行     | Stage 失败但降级完成                  | GATE-DEDUP PASS with DEGRADED |

### severity 判定规则

| severity | 条件（满足任一）                                                                 |
| -------- | ------------------------------------------------------------------------ |
| critical | `similarity ≥ 0.95` AND `affected_files ≥ 3` AND `category = accidental` |
| high     | `similarity ≥ 0.85` AND `affected_files ≥ 2`                             |
| medium   | `similarity ≥ 0.70` OR `category = needs_review`                         |
| low      | `similarity < 0.70` OR `category = intentional`                          |

### 6.1 可观测性规格

| 指标名                       | 类型    | 告警阈值          | 告警级别 |
| ------------------------- | ----- | ------------- | ---- |
| scan\_duration\_p50\_ms   | Gauge | p50 > 5000ms  | P2   |
| scan\_duration\_p99\_ms   | Gauge | p99 > 60000ms | P1   |
| cache\_hit\_ratio         | Gauge | < 0.5         | P2   |
| false\_positive\_rate\_7d | Gauge | > 0.30        | P1   |
| fix\_safety\_rate         | Gauge | < 1.0         | P0   |
| brs\_max                  | Gauge | ≥ 76          | P1   |
| sas\_score                | Gauge | < 25          | P1   |
| idempotency\_rate         | Gauge | < 1.0         | P0   |

### 6.2 退化矩阵

| 组件                       | 失败后可用         | 不可用      | 降级策略                   | 恢复条件          |
| ------------------------ | ------------- | -------- | ---------------------- | ------------- |
| cache\_manager           | 全程 AST 解析     | 增量扫描     | full rebuild→exit 0/1  | 缓存重建          |
| signature\_matcher       | Stage 1+2     | O(1)精确匹配 | skip Stage 0.5→exit 4  | 模块恢复          |
| behavioral\_sampler      | Stage 0.5+1+2 | 行为验证     | skip Stage 0.25→exit 4 | 沙箱恢复          |
| scanner(MinHash)         | Stage 0.5+2   | Token级检测 | skip Stage 1→exit 4    | 内存恢复          |
| ast\_comparator          | Stage 0.5+1   | AST结构检测  | skip Stage 2→exit 4    | Tree-sitter恢复 |
| auto\_fixer              | 只读扫描+报告       | 自动修复     | exit 1 WARN            | 修复模块恢复        |
| atomic\_fixer            | 修复无崩溃恢复       | 原子性保障    | 手动备份提示                 | WAL恢复         |
| shadow\_trust\_validator | 无清单模式扫描       | 影子清单注入   | Trust Score<90%降级      | 信任链恢复         |

***

## §8 安全考量

> temporal_type: permanent

| # | 威胁                   | 影响 | 缓解措施                                                | 验证方式                            |
| - | -------------------- | -- | --------------------------------------------------- | ------------------------------- |
| 1 | 沙箱执行恶意代码             | 高  | AST 静态副作用检测 + subprocess 隔离 + 白名单模块 + 256MB + 500ms | 行为采样仅执行纯函数                      |
| 2 | 自动修复引入 bug           | 高  | Suitability Score < 40 绝不提取 + 分批修复 + 全量测试 + 循环依赖检测  | 修复后全量测试零失败                      |
| 3 | 影子清单幻觉导致 ImportError | 高  | import 存活校验 + 幻觉自动清除 + Trust Score < 90% 拒绝注入       | spot-check 10% → 失败率 > 10% → 降级 |
| 4 | 修复窗口并发写入             | 极高 | Pre-Apply Integrity Gate + SHA256 重验证 + 文件锁         | 冲突 ABORT + fix\_plan 自动重生成      |
| 5 | 爆炸半径灾难       | 高  | BRS ≥ 76 停止去重 + 自动测试生成缓解                            | BRS 计算正确性验证                     |
| 6 | 缓存损坏                 | 高  | `_integrity` SHA256 + 原子写入 + 自愈重建                   | 损坏 → 自动 full rebuild → exit 0/1 |

***

## §9 测试策略

> temporal_type: permanent

| # | 测试类型  | 覆盖范围                                                          | 关键测试用例                                   | 通过标准                    |
| - | ----- | ------------------------------------------------------------- | ---------------------------------------- | ----------------------- |
| 1 | 单元测试  | scanner, signature\_matcher, degradation, behavioral\_sampler | 已知 5 组重复检出 + 签名碰撞 + 降级场景 + 行为采样安全边界      | ≥ 30 条全绿                |
| 2 | 集成测试  | GATE-DEDUP pre-commit + Context Engine 影子清单                   | commit 阻断(exit 2) + 影子清单注入 + 回环验证        | 端到端通过                   |
| 3 | 性能测试  | 增量扫描 + 全量扫描 + 修复                                              | 增量 < 3s / 全量 < 30s / 修复+验证 < 60s         | wall time 达标            |
| 4 | 降级测试  | Stage 2→1→0.5 降级链                                             | Tree-sitter 不可用 → exit 4（DEGRADED）       | 降级不崩溃                   |
| 5 | 自愈测试  | 缓存损坏 + 修复中断                                                   | 损坏 → full rebuild → exit 0/1 / 中断 → 自动恢复 | 代码库一致                   |
| 6 | 幂等性测试 | 连续两次全量扫描                                                      | 两次报告的 `duplicate_groups` 完全一致            | group\_id + member 列表一致 |

### 已知重复函数测试用例

```python
KNOWN_DUPLICATES = {
    "now_iso_group": {
        "functions": [
            {"name": "_now_iso", "body": "def _now_iso():\n    from datetime import datetime, timezone\n    return datetime.now(timezone.utc).isoformat()"},
            {"name": "now_iso", "body": "def now_iso():\n    from datetime import datetime, timezone\n    return datetime.now(timezone.utc).isoformat()"},
            {"name": "_default_now", "body": "def _default_now():\n    from datetime import datetime, timezone\n    return datetime.now(timezone.utc).isoformat()"},
        ],
        "expected_similarity_min": 0.95,
        "expected_clone_type": "Type-2",
    },
    "repo_root_group": {
        "functions": [
            {"name": "REPO_ROOT", "body": "from pathlib import Path\nREPO_ROOT = Path(__file__).resolve().parent.parent.parent"},
            {"name": "_project_root", "body": "import os\n_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))"},
        ],
        "expected_similarity_min": 0.70,
        "expected_clone_type": "Type-3",
    },
}
```

***

## §10 依赖关系

> temporal_type: permanent

### 10.1 依赖声明

| 依赖模块        | 依赖类型 | 依赖内容                             | 版本要求     | 蓝图路径                                                                            |
| ----------- | ---- | -------------------------------- | -------- | ------------------------------------------------------------------------------- |
| MOD-INF-005 | 必须   | 退出码约定 0/1/2/3/4 + Finding Schema | ≥ 0.5.0  | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\script-system\blueprint.md`  |
| MOD-GATE_ENGINE | 必须   | GATE-DEDUP 门禁判定逻辑                | ≥ 0.3.0  | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\gate_engine\blueprint.md`    |
| MOD-CONTEXT_ENGINE | 必须   | Context Engine 影子清单注入            | ≥ 0.2.0  | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\context_engine\blueprint.md` |
| MOD-FEEDBACK_LOOP | 可选   | FLE 进化闭环                         | ≥ 0.2.0  | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\feedback_loop\blueprint.md`  |
| MOD-INF-016 | 必须   | SSoT Guard + shared 目录           | ≥ 0.14.0 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\shared_core\blueprint.md`    |
| MOD-DATABASE | 可选   | KB 持久化 API                       | ≥ 0.1.0  | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\knowledge_base\blueprint.md` |
| MOD-INF-027 | 必须   | 审计总线（decision_auditor写入）        | ≥ 0.3.0  | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\audit-orchestrator\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项                                                | 对齐方式                       | 对齐状态 | 验证命令                                                                                                      |
| - | -------------------------------------------------- | -------------------------- | :--: | --------------------------------------------------------------------------------------------------------- |
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 |  已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-017` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path\_mappings                 | 路径一致                       |  已对齐 | 同上                                                                                                        |

### 10.3 内部依赖图

| 上游模块             | 下游模块                           | 依赖内容      | 验证方式      |
| ---------------- | ------------------------------ | --------- | --------- |
| scanner.py       | signature\_matcher.py          | 扫描结果→签名匹配 | import 检查 |
| scanner.py       | diff\_detector.py              | 扫描结果→增量检测 | 事件流检查     |
| atomic\_fixer.py | pre\_apply\_integrity\_gate.py | 修复前→完整性校验 | 调用链检查     |

### 10.4 自动化规格

| # | 自动化项       | 是否需要 | 理由          | 实现方式        | 现有工具                           | 缺口                     |
| - | ---------- | :--: | ----------- | ----------- | ------------------------------ | ---------------------- |
| 1 | 依赖图自动生成    |   是  | 6个外部依赖+内部依赖 | AST解析import | asset\_inventory/dependency.py | 不覆盖code\_dedup\_engine |
| 2 | 依赖对齐自动验证   |   是  | 有外部依赖       | CI门禁        | validate\_path\_alignment.py   | 无                      |
| 3 | 临时时态内容自动清理 |   是  | 有迁移方案       | 压缩工作流脚本     | 无                              | 需新建                    |

### 10.5 概念重叠声明

| 本模块概念         | 重叠模块        | 区别                  | 处置  |
| ------------- | ----------- | ------------------- | --- |
| 退出码 0/1/2/3/4 | MOD-INF-005 | 005定义标准，017遵循       | 消费者 |
| GATE-DEDUP 门禁 | MOD-GATE_ENGINE | 007提供框架，017提供检查逻辑   | 消费者 |
| 影子清单注入        | MOD-CONTEXT_ENGINE | 008提供注入通道，017提供清单内容 | 消费者 |
| shared/ 提取目标  | MOD-INF-016 | 016保护目录，017是写入方     | 消费者 |
| 原子修复          | MOD-INF-031 | 017保留去重专用修复，通用修复委托031 | 边界明确 |
| "去重"命名        | MOD-INF-024 | 024去重AI操作动作，017去重代码文本 | 无功能重叠 |
| 去重            | MOD-INF-037 | 017做Token级代码去重，037做语义级功能域去重 | 共存 |
| blast_radius检测器 | MOD-FEEDBACK_LOOP | FLE应委托017计算BRS | 待补充反向依赖 |

### 10.6 依赖链风险评级

| 依赖          | 链深度 | 风险等级 | 缓解措施                       |
| ----------- | :-: | :--: | -------------------------- |
| MOD-INF-005 |  1  |   低  | 退出码枚举在 exit\_codes.py 独立定义 |
| MOD-GATE_ENGINE |  1  |   中  | DeduplicationHandler 独立文件  |
| MOD-CONTEXT_ENGINE |  2  |   中  | 影子清单格式独立，注入通过 YAML         |
| MOD-FEEDBACK_LOOP |  1  |   低  | 去重作为独立 Stage               |
| MOD-INF-016 |  1  |   低  | 提取目标路径从 config.py 读取       |
| MOD-INF-027 |  2  |   低  | 审计写入格式独立                   |

***

## §11 产出物存放目录

> temporal_type: permanent

| 产出物类型  | 存放完整绝对路径                                                                                 | 说明                                                     | consumer_min |
| ------ | ---------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------ |
| 蓝图文件   | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\code-dedup-engine\blueprint.md`       | 本文件                                                    | AI session / 治理审计 |
| 业务代码   | `D:\ZephyrAlpha\src\zephyr\infra_ops\code_dedup_engine\`                        | 68 个 .py 文件                                            | CLI / Gate Engine / AutoRuntime |
| CLI 脚本 | `D:\ZephyrAlpha\src\zephyr\infra_ops\code_dedup_engine\cli.py` | CLI 入口：`python -m zephyr.infra_ops.code_dedup_engine.cli` | pre-commit / CI / Owner |
| Pre-commit | `D:\ZephyrAlpha\scripts\pre-commit\verify_dedup.py` | 薄壳委托CLI | .pre-commit-config.yaml |
| 测试代码   | `D:\ZephyrAlpha\tests\unit\`                                                             | test\_code\_dedup.py 等                                 | pytest / CI |
| 缓存数据   | `D:\ZephyrAlpha\data\cache\function-cache.json`                                          | 运行时生成（.gitignore + \_integrity 校验）                     | scanner / signature_matcher |
| 策略树配置  | `D:\ZephyrAlpha\src\zephyr\infra_ops\code_dedup_engine\config\policy-tree.yaml` | Wave 3 落地                                              | config.py / GATE-DEDUP |
| 符号索引   | `D:\ZephyrAlpha\data\cache\symbol_index.db`                                              | Wave 2 SQLite                                          | symbol_index / verifier |
| 审计日志   | `D:\ZephyrAlpha\data\cache\decision_audit_log.yaml`                                      | 不可变追加——按月归档                                            | decision_auditor / MOD-INF-027 |

***

## §12 集成目标

> temporal_type: permanent

| 集成目标系统                       | 集成方式                                                             | 集成点                                                  | 验证方法                      |
| ---------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------- | ------------------------- |
| Script System (MOD-INF-005)  | 去重脚本注册到 manifest，遵循退出码约定                                         | `cli.py` → `script-manifest.yaml` | G4 入库验收 + exit code 映射    |
| Gate Engine (MOD-GATE_ENGINE)    | Pre-commit hook exit code → Gate PASS/FAIL/BLOCKED/SKIP/DEGRADED | CT-SCRIPT-GATE-001                                   | Gate 判定日志中 GATE-DEDUP 出现  |
| Context Engine (MOD-CONTEXT_ENGINE) | 影子清单注入 system prompt + 渐进式三层记忆 + 消费验证回环                          | `shadow_apimanifest.yaml` → CE build → inject       | CE build log 包含影子清单       |
| Shared+Core (MOD-INF-016)    | 去重→提取→SSoT 注册三合一原子操作                                             | Auto Fixer → SSoT Guard → `b_shared.yaml`            | 提取的函数在 YAML SSoT 中可检索     |
| Feedback Loop (MOD-FEEDBACK_LOOP)  | 重复模式→FLE→`dedup_pattern_report`                                  | FLE detect → `dedup_pattern_report`                  | 重复模式可被 FLE 检测并触发 evolve() |
| Task System (MOD-TASK_SYSTEM)    | high/critical 重复 → TaskCard → AI pipeline 修复                     | TaskCard `source_blueprint: MOD-INF-017`             | TaskCard 状态可追踪            |
| Session Log                  | 扫描结果摘要写入 Session Log → next AI session                           | Scanner → health\_monitor.py → Session Log           | Next AI session 零推理读到去重发现 |
| Knowledge Base (MOD-DATABASE) | 重复模式/健忘热点 → KB 持久化                                               | health\_monitor.py → KB API → kb://dedup/insights    | KB 可查询 dedup 相关实体         |

### 共享 API 影子清单格式

```yaml
shadow_apis:
  - signature: "now_iso() -> str"
    module: "zephyr.shared.time_utils"
    description: "返回 ISO 8601 格式的当前UTC时间戳"
  - signature: "estimate_tokens(text: str) -> int"
    module: "zephyr.shared.token_utils"
    description: "估算文本的 token 数量"
  - signature: "get_repo_root() -> Path"
    module: "zephyr.shared.path_utils"
    description: "获取项目根目录的绝对路径"
```

### intentional-duplicate 标记规范

```python
# @intentional-duplicate: 这是API版本兼容层，v1和v2必须独立维护
def process_v1(data: dict) -> Result: ...

# @file-intentional-duplicate: tests/fixtures/ 下的fixture有合理重复

# @block-intentional-duplicate-start
# ... allowed duplicate block ...
# @block-intentional-duplicate-end
```

***

## §13 需要更新的相关内容

> temporal_type: construction_temporary

| # | 需更新的文件                    | 完整绝对路径                                                         | 更新内容                                              | 更新原因          |
| - | ------------------------- | -------------------------------------------------------------- | ------------------------------------------------- | ------------- |
| 1 | 蓝图注册表                     | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml`       | MOD-INF-017 version→0.11.0, generation→2          | 蓝图升级          |
| 2 | script\manifest.yaml     | `D:\ZephyrAlpha\scripts\governance\script-manifest.yaml`       | 注册 CLI 入口 + exit code 4 + 特殊标志                    | Wave 1 产出 CLI |
| 3 | AGENTS.md §5.1            | `D:\ZephyrAlpha\AGENTS.md`                                     | 影子清单锚点 + 三层记忆注入 + Deprecated 标记                   | 生成时预防落地       |
| 4 | Gate Engine YAML          | `D:\ZephyrAlpha\src\zephyr\gates\g6-blueprint-compliance.yaml` | GATE-DEDUP 门禁规则                                   | Wave 1 门禁落地   |
| 5 | `.pre-commit-config.yaml` | `D:\ZephyrAlpha\.pre-commit-config.yaml`                       | 新增 verify_dedup.py hook | 阻断能力          |
| 6 | pyproject.toml            | `D:\ZephyrAlpha\pyproject.toml`                                | 锁定 Tree-sitter Python grammar 版本                  | 风险 #9 缓解      |
| 7 | evolve() 接口               | `D:\ZephyrAlpha\src\zephyr\infra\evolve.py`                    | `failure_patterns` 加入 `dedup_pattern_report`      | Wave 3 进化闭环   |

***

## §14 已知风险与缓解

> temporal_type: permanent

| #  | 风险/负面后果                    |  概率 |  影响 | 缓解策略                                                       | 类型   |
| -- | -------------------------- | :-: | :-: | ---------------------------------------------------------- | ---- |
| 1  | 误报消耗 Owner 时间              |  中  |  高  | 路径感知阈值 + 偏向漏报 + `@intentional-duplicate` + 惯用法豁免 + 设计模式白名单 | 风险   |
| 2  | 自动修复引入 bug                 |  中  |  高  | Suitability Score < 40 绝不提取 + 分批修复 + 全量测试 + 循环依赖检测         | 风险   |
| 3  | 增量扫描漏报                     |  中  |  中  | 每周全量重建缓存 + `_integrity` 校验 + `--full` 强制全量                 | 风险   |
| 4  | 爆炸半径灾难             |  高  |  高  | BRS ≥ 76 停止去重 + 自动测试生成缓解 BRS                               | 风险   |
| 5  | 引擎维护成本倒挂                   |  中  |  极高 | SAS 月度自审计 + SAS < 25 退役建议                                  | 风险   |
| 6  | Doom Loop                  |  中  |  高  | L0-L4 升级阶梯 + 3 次失败冻结 + Owner 告警                            | 风险   |
| 7  | 影子清单幻觉                     |  中  |  高  | import 存活校验 + 幻觉清除 + Trust Score < 90% 拒绝注入                | 风险   |
| 8  | Tree-sitter 版本漂移           |  中  |  高  | grammar 版本锁定 + 兼容性自检 + 降级 exit 4                           | 风险   |
| 9  | 缓存损坏                       |  中  |  高  | `_integrity` SHA256 + 原子写入 + 自愈重建                          | 风险   |
| 10 | 修复中断导致代码库损坏                |  中  |  极高 | WAL 式 PREFLIGHT→CHECKPOINT→APPLY→RECOVER + 崩溃自动恢复          | 风险   |
| 11 | Vibe Coding 创造性漂移          |  高  |  中  | 签名指纹匹配 + 健忘热点追踪 + 影子清单消费验证回环                               | 风险   |
| 12 | "5000 行魔咒"                 |  高  |  高  | 四 Tier 自适应阈值 + 重复引入速率追踪                                    | 风险   |
| 13 | 盲提取创建更重技术债                 |  中  |  高  | Suitability Score + 不安全模式目录 7 类 + 部分提取                     | 风险   |
| 14 | 跨边界克隆不可见                   |  中  |  高  | 四大边界差异化检测 + 独立策略                                           | 风险   |
| 15 | 并发写入冲突                     |  中  |  极高 | Pre-Apply Integrity Gate + SHA256 重验证 + 文件锁                | 风险   |
| 16 | AST 分析性能开销                 |  —  |  —  | 增量扫描 + 缓存 + 降级运行 + Tier 自适应                                | 负面后果 |
| 17 | 66 个模块维护成本                 |  —  |  —  | 分层维护 + 降级运行 + Self-Benchmark + 退役路径                        | 负面后果 |
| 18 | 爆炸半径矛盾——去重 vs 爆炸半径 |  —  |  —  | 引擎只能显式报告                                                   | 负面后果 |
| 19 | 行为采样安全边界                   |  —  |  —  | AST 副作用检测 + subprocess 隔离                                  | 负面后果 |
| 20 | 观察期拖慢修复节奏                  |  —  |  —  | `--skip-observation` 跳过                                    | 负面后果 |

***

## §16 施工指引

> temporal_type: construction_temporary
> 删除前置条件（缺一不可）：代码文件存在且非空 + pytest exit 0 + mypy 通过 + ruff 通过 → 该步骤详细内容可删除，只保留"步骤 N: 已完成"

### ⚠️ AI 施工前检查清单

| # | 检查项                    | 确认方式                |  状态 |
| - | ---------------------- | ------------------- | :-: |
| 1 | 已读取本蓝图全部内容             | 逐节确认                |  ☐  |
| 2 | 已读取必备链接中所有真源文件         | 逐个打开确认              |  ☐  |
| 3 | PS-STD-001 编号规则已理解     | 能回答"GOV-SEC-001是什么" |  ☐  |
| 4 | GOV-DOC-002 防幻觉路径映射已理解 | 能回答"某类文件该放哪"        |  ☐  |
| 5 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯               |  ☐  |
| 6 | §0 代码对齐验证已填写且与实际代码一致   | 逐项核对                |  ☐  |

### 16.1 施工策略

| 项目            | 内容                                       |
| ------------- | ---------------------------------------- |
| 施工阶段数         | 3 个 Wave                                 |
| 施工模式          | 新建 + 扩展                                  |
| 核心风险          | 误报消耗 Owner 时间 + 自动修复引入 bug               |
| 目标 generation | 2 — 本次规格化从 generation 1 升级到 generation 2 |

### 16.2 前置条件

| # | 依赖项                            | 依赖类型 | 当前状态 | 是否满足 |
| - | ------------------------------ | ---- | :--: | :--: |
| 1 | MOD-INF-005 退出码标准已定义           | hard |   ✅  |   ✅  |
| 2 | MOD-GATE_ENGINE Gate Engine 已实现    | hard |   ✅  |   ✅  |
| 3 | MOD-CONTEXT_ENGINE Context Engine 已实现 | hard |   ✅  |   ✅  |
| 4 | MOD-INF-016 Shared Core 已实现    | hard |   ✅  |   ✅  |

### 16.3 实施路线（三波递进）

#### Wave 1：核心阻断+交接+自保护（6 天）

| #     | 任务                                    | 交付物                                                   | 验收标准                            |
| ----- | ------------------------------------- | ----------------------------------------------------- | ------------------------------- |
| W1-1  | cache\_manager + function\_cache.json | 缓存读写+增量更新+\_integrity+原子写入+自愈                         | 损坏→自动 full rebuild→exit 0/1     |
| W1-2  | diff\_detector 增量扫描                   | git diff→变更函数提取                                       | 增量扫描 < 3s                       |
| W1-3  | signature\_matcher Stage 0.5          | SHA256\[:12] O(1) 精确匹配                                | `()->str` 签名重复正确标记              |
| W1-4  | scanner Token+代码块级                    | MinHash+LSH+分区阈值+滑动窗口                                 | 已知 5 组重复全部可检出                   |
| W1-5  | degradation 降级运行                      | 各 Stage 独立 try/except                                 | Stage 失败→降级→exit 4              |
| W1-6  | config + IDIOM\_WHITELIST             | 惯用法+设计模式豁免                                            | `__init__`/`@property` 不产生误报    |
| W1-7  | report + Health Score                 | 五档退出码+Health Score 0-100                              | exit code 映射正确                  |
| W1-8  | prioritizer ROI 排序                    | `priority_score × roi_factor`                         | ROI 最高组优先                       |
| W1-9  | annotations + 决策学习                    | `@intentional-duplicate` 解析                           | 标记函数不被报告                        |
| W1-10 | health\_monitor + Session Log         | Health Score+去重摘要写入                                   | Session Log 含 Health Score+Top3 |
| W1-11 | cli.py CLI入口                      | --warn-only/--fail-on-duplicates/--incremental/--file | CLI 可运行                         |
| W1-12 | GATE-DEDUP pre-commit 落地              | .pre-commit-config.yaml                               | high/critical→exit 2 阻断         |
| W1-13 | 单元测试 ≥ 25 条                           | test\_code\_dedup.py 等                                | 全绿                              |

#### Wave 2：beta 阶段（9 天）

| #     | 任务                                  | 交付物                                     |
| ----- | ----------------------------------- | --------------------------------------- |
| W2-1  | ast\_comparator 完整实现                | AST 子树哈希+docstring 剥离+部分重复 LCS          |
| W2-2  | symbol\_index 轻量符号索引                | SQLite——函数签名+调用计数+import 图              |
| W2-3  | auto\_fixer 自动修复引擎                  | 提取→替换→分批执行→失败回滚+`--partial-extract`     |
| W2-4  | extraction\_safety 安全提取评估           | Suitability Score+不安全模式目录+影响预分析         |
| W2-5  | verifier 去重后验证                      | pytest+import 解析+循环依赖+Symbol Index 交叉验证 |
| W2-6  | doom\_loop\_guard Doom Loop 防护      | L0-L4 升级阶梯+冻结机制                         |
| W2-7  | shared\_lifecycle\_manager 生命周期     | 5 阶段状态机+迁移 diff+影子清单同步降级                |
| W2-8  | import\_surface\_tracker Import 负债  | SBS 0-100+跨层依赖热图+提取门槛联动                 |
| W2-9  | monoculture\_guard 爆炸半径防护   | BRS 0-100+去重悖论+BRS ≥ 76 停止去重            |
| W2-10 | atomic\_fixer 原子性修复                 | WAL PREFLIGHT→CHECKPOINT→APPLY→RECOVER  |
| W2-11 | grandfather\_manager 古老重复           | 三定律+化石记录+考古测试                           |
| W2-12 | false\_negative\_auditor 漏报盲审       | Sweep+Canary+抽样审查                       |
| W2-13 | shadow\_trust\_validator 影子信任链      | import 校验+幻觉清除+Trust Score              |
| W2-14 | temporal\_drift\_tracker 时态漂移       | 指纹演化+UNSTABLE+自动重算                      |
| W2-15 | simplicity\_auditor 引擎自审计           | SAS 0-100+净收益评估+退役建议                    |
| W2-16 | dead\_module\_detector 死模块检测        | ZOMBIE/DEAD/GRAVEYARD 判定                |
| W2-17 | observation\_window\_guard 观察期      | 14 天观察+OBSERVING→resume/ROLLBACK        |
| W2-18 | recovery\_manifest\_writer 恢复安全网    | R2 纯文本 Manifest+R0-R3 四层                |
| W2-19 | thematic\_clusterer 主题聚类            | 三层加权+50 组→3 主题压缩                        |
| W2-20 | behavioral\_trust\_checker 行为信任     | behavior\_signature+漂移检测+告警             |
| W2-21 | pre\_apply\_integrity\_gate 并发防护    | Pre-Apply SHA256+ABORT+fix\_plan 重生成    |
| W2-22 | micro\_clone\_detector 微克隆检测        | n-gram L0/L1/L2+高频模式聚合                  |
| W2-23 | auto\_test\_generator 测试生成          | 类型驱动+金丝雀+契约测试                           |
| W2-24 | contract\_consistency\_checker 契约验证 | 四层校验+三维 Trust Score                     |
| W2-25 | cross\_boundary\_detector 跨边界感知     | 四大边界差异化策略                               |
| W2-26 | decision\_auditor 决策审计链             | DecisionFingerprint+证据包+可回滚             |
| W2-27 | function\_discovery 主动发现            | 签名+语义双通道+<150 行                         |

#### Wave 3：stable 阶段（6 天）

| #    | 任务                          | 交付物                                              |
| ---- | --------------------------- | ------------------------------------------------ |
| W3-1 | semantic\_verifier LLM 语义验证 | 置信度 0-100（仅用于 0.70-0.85 不确定区间）                   |
| W3-2 | Feedback Loop 深度集成          | 重复模式→FLE→`dedup_pattern_report`                  |
| W3-3 | evolve() 进化信号               | 重复模式→EvolutionProposal                           |
| W3-4 | 策略树 YAML 正式落地               | `config/policy-tree.yaml` 5条规则R001-R005+load_policy_tree() | ✅ 已完成 |
| W3-5 | GATE-DEDUP 正式版              | DeduplicationHandler+_GATE_FILES+skip set移除 | ✅ 已完成 |
| W3-6 | CI 集成                       | `.github/workflows/governance.yml` 新增 dedup step |
| W3-7 | Self-Benchmark              | 5组KAT(KAT-01~05)+退化检测+benchmark子命令 | ✅ 已完成 |
| W3-8 | 渐进式三层记忆注入(委托CE)             | 通过 CE.register_rules() 注册去重规则(HOT/DOMAIN/COLD) → MOD-CONTEXT_ENGINE | ⏳ 委托MOD-CONTEXT_ENGINE |

### 16.4 回滚方案

| Wave | 回滚操作 | 验证命令 |
|------|---------|---------|
| Wave 1 | 删除已创建的 .py 文件 + 注销 __init__.py | `python -m pytest tests/` |
| Wave 2 | `atomic_fixer recover_from_crash()` | `python -m zephyr.infra_ops.code_dedup_engine.cli verify` |
| Wave 3 | `git revert <wave3-commit>` | `python -m zephyr.infra_ops.code_dedup_engine.cli scan --full` |

### 16.5 验证流程（每次施工后必执行）

1. `python -m pytest tests/ -q` —— 确认全部测试全绿
2. `python -m zephyr.infra_ops.code_dedup_engine.cli scan --full --warn-only` —— 确认扫描可正常输出含 Health Score
3. 检查退出码与 severity 的映射是否正确（0/1/2/3/4 五档）
4. 检查 `function_cache.json` 能与磁盘文件一致
5. 模拟降级场景：移除 Tree-sitter grammar → exit code 4（DEGRADED）
6. 模拟缓存损坏：修改 `_integrity` → 自动 full rebuild → exit 0/1
7. 检查 Session Log 已追加去重摘要

### 16.6 施工完成与生产就绪标准

| # | 检查项                    | 验证命令                                                             | 通过条件     |  状态 |
| - | ---------------------- | ---------------------------------------------------------------- | -------- | :-: |
| 1 | 68 个 .py 文件存在          | Get-ChildItem \*.py \| Measure-Object                            | Count≥68 |  ✅  |
| 2 | 单元测试通过                 | pytest tests/test\_code\_dedup\_engine.py                   | exit 0   |  ✅  |
| 3 | 红队测试通过                 | pytest tests/adversarial/test\_code\_dedup\_engine\_red\_team.py | exit 0   |  ✅  |
| 4 | CLI verify 通过          | cli verify                                                       | exit 0   |  ✅  |
| 5 | GATE-DEDUP handler 可加载 | import DeduplicationHandler                                      | exit 0   |  ✅  |
| 6 | pre-commit hook 注册     | pre-commit run gate-dedup                                        | Passed   |  ✅  |
| 7 | Work DAG 绑定            | import AutoRuntimeCore                                           | exit 0   |  ✅  |
| 8 | 增量扫描 < 3s              | Measure-Command cli scan                                         | < 3s     |  ✅  |
| 9 | 全量扫描 < 30s             | Measure-Command cli scan --full                                  | < 30s    |  ✅  |

### 16.7 施工状态

| Wave | construction\_status | verification\_status |    完成日期    |
| :--: | :------------------: | :------------------: | :--------: |
|   1  |       complete       |       verified       | 2026-05-05 |
|   2  |       complete       |       verified       | 2026-05-10 |
|   3  |     in\_progress     |     partial     |   2026-05-16   |

### 16.7.1 Wave 3 施工进度

| # | 任务 | 交付物 | 状态 | 堵塞项 |
|---|------|--------|:---:|--------|
| W3-1 | semantic_verifier LLM 语义验证 | 置信度 0-100（仅用于 0.70-0.85 不确定区间） | 🔒 非本蓝图 | 堵塞: MOD-CONTEXT_ENGINE/034 LLM推理能力; 本蓝图仅提供0.70-0.85不确定区间接口 |
| W3-2 | Feedback Loop 深度集成 | 重复模式→FLE→dedup_pattern_report | 🔒 非本蓝图 | 堵塞: MOD-FEEDBACK_LOOP FLE未运行; 本蓝图仅输出dedup_pattern_report |
| W3-3 | evolve() 进化信号 | 重复模式→EvolutionProposal | 🔒 非本蓝图 | 堵塞: MOD-FEEDBACK_LOOP FLE未运行; 本蓝图仅输出进化信号 |
| W3-4 | 策略树 YAML 正式落地 | config/policy-tree.yaml 5条规则R001-R005 | ✅ 已完成 | — |
| W3-5 | GATE-DEDUP 正式版 | DeduplicationHandler+_GATE_FILES+skip set移除 | ✅ 已完成 | — |
| W3-6 | CI 集成 | .github/workflows/governance.yml | 🔒 非本蓝图 | 堵塞: DevOps/GitHub Actions配置; 本蓝图仅提供cli scan命令 |
| W3-7 | Self-Benchmark | 5 组已知对自验证 | ⏳ 待施工 | — |
| W3-8 | 渐进式三层记忆注入(委托CE) | 通过 CE.register_rules() 注册去重规则(HOT/DOMAIN/COLD) → MOD-CONTEXT_ENGINE | ⏳ 委托MOD-CONTEXT_ENGINE | MOD-CONTEXT_ENGINE 规则优先级注册API |

### 16.7.2 v0.14.1 施工记录

| 修改项 | 文件 | 类型 |
|--------|------|------|
| 蓝图名称修正 Monoculture→爆炸半径防护 | blueprint.md + __init__.py + fifteen_dimension_auditor.py + _system_master | P0 |
| ExitCode 三重定义统一 | report.py + degradation.py + test_degradation_edge.py | P0 |
| GATE-DEDUP 四重空壳修复 | GATE-DEDUP.yaml + ct_deduplication.py + gate_engine.py + _registry.yaml | P0 |
| __init__.py 版本号 0.10.0→0.14.1 | __init__.py | P0 |
| 月度定时任务 CircadianScheduler 注册 | auto_runtime_core.py | P1 |
| 依赖强度 DEP-037/039 hard→soft | cross-module-dependency-registry.yaml | P1 |
| 策略树 YAML 落地 R001-R005 | config/policy-tree.yaml + config.py | P2 |
| 蓝图模板回填 10 项 | blueprint.md | P1 |
| 蓝图压缩（删除散文/冗余） | blueprint.md | P2 |
| MOD-INF-027 依赖补充 | blueprint.md | P1 |

### 16.7.3 待施工项（外部依赖堵塞）

| 任务 | 堵塞依赖 | 优先级 | 解堵条件 |
|------|---------|:---:|---------|
| MOD-INF-031 代码物理迁移 | auto-fix-engine/ 目录不存在 | P1 | MOD-INF-031 蓝图 Step 1-3 落地 |
| LLM 语义验证 (W3-1) | LLM 基础设施 | P2 | Ollama/DeepSeek 可用 |
| Feedback Loop (W3-2/3) | MOD-FEEDBACK_LOOP FLE | P2 | FLE 运行 |
| CI 集成 (W3-6) | DevOps 配置 | P2 | GitHub Actions 配置权限 |
| Self-Benchmark (W3-7) | 无 | P2 | 可立即施工 |
| 三层记忆注入 (W3-8) | 无 | P2 | 可立即施工 |

### 16.8 参考实现规格

| #  | 规格名称                     | 类型 | 规格内容                                              | 对应代码                           |
| -- | ------------------------ | -- | ------------------------------------------------- | ------------------------------ |
| 1  | WAL 原子修复4步               | 协议 | PREFLIGHT→CHECKPOINT→APPLY→RECOVER                | atomic\_fixer.py               |
| 2  | MinHash+LSH              | 算法 | 128-perm MinHash→LSH band=16,r=8→Jaccard≥0.7      | scanner.py                     |
| 3  | SHA256 签名指纹              | 算法 | sha256(name:params:return\_type)\[:12]            | signature\_matcher.py          |
| 4  | 行为采样沙箱                   | 协议 | 类型推断→采样输入→subprocess隔离→256MB+500ms                | behavioral\_sampler.py         |
| 5  | BRS 爆炸半径                 | 算法 | max(caller\_count(f))/total\_callers\*100         | monoculture\_guard.py          |
| 6  | SAS 自审计                  | 算法 | (savings-maintenance)/maintenance\*100            | simplicity\_auditor.py         |
| 7  | 微克隆n-gram                | 算法 | L0:逐行SHA256→L1:归一化SHA256→L2:2-3行滑动窗口              | micro\_clone\_detector.py      |
| 8  | 主题聚类三层加权                 | 算法 | 前缀30%+AST50%+共现20%                                | thematic\_clusterer.py         |
| 9  | Pre-Apply Integrity Gate | 协议 | 修复前SHA256快照→修复后重验证→不一致ABORT                       | pre\_apply\_integrity\_gate.py |
| 10 | DecisionFingerprint      | 格式 | sha256(group\_id+action+timestamp+operator)\[:16] | decision\_auditor.py           |
| 11 | SBS Import负债             | 算法 | min(100,direct\_import\_count/threshold\*100)     | import\_surface\_tracker.py    |
| 12 | Suitability 8维评估         | 算法 | 8维加权→<40=UNSAFE/40-69=NEEDS\_REVIEW/≥70=SAFE      | extraction\_safety.py          |

### 16.9 施工参考卡

| # |  类型 | 名称                                   | 参数                                                           | 输出                  |
| - | :-: | ------------------------------------ | ------------------------------------------------------------ | ------------------- |
| 1 |  命令 | cli scan                             | --incremental/--full/--file/--warn-only/--fail-on-duplicates | exit 0/1/2/3/4      |
| 2 |  命令 | cli fix                              | --group-ids/--batch-size 1-3/--dry-run/--partial-extract     | FixResult+代码变更      |
| 3 |  命令 | cli report                           | --format yaml/json                                           | JSON/YAML 报告        |
| 4 |  命令 | cli verify                           | —                                                            | exit 0=GATE\_PASSED |
| 5 |  配置 | config.py IDIOM\_WHITELIST           | list\[str]函数名模式                                              | 命中→不误报              |
| 6 |  配置 | config.py DESIGN\_PATTERN\_WHITELIST | list\[str] 6种AST规则                                           | 命中→不误报              |
| 7 |  数据 | function\_cache.json                 | \_version+\_integrity+\_tier+functions{}                     | 原子写入+SHA256校验       |

### 16.9.1 CLI 参数完整规格

> 施工声明——AI 施工 CLI 时必读。永久保留。

```
python -m zephyr.infra_ops.code_dedup_engine.cli <subcommand> [OPTIONS]

子命令:
  scan [target]         扫描代码重复（可选指定文件/目录）
  fix [target]          自动修复重复（可选指定文件/目录）
  report [target]       生成去重报告
  verify                验证引擎完整性
  benchmark             运行 5 组已知对自验证基准测试

scan 参数:
  --incremental           增量扫描（仅扫描 git diff 变更文件）[默认]
  --full                  全量扫描（忽略缓存，重新解析所有函数）
  --file PATH             单文件快速检查
  --warn-only             即使发现 high/critical 也 exit 1（不阻断）
  --fail-on-duplicates    发现 high/critical → exit 2（阻断 CI）
  --output PATH           报告输出路径 [默认: stdout]
  --format FORMAT         报告格式 [yaml|json] [默认: yaml]
  --quiet                 只输出退出码

阈值覆盖:
  --threshold-global FLOAT        全局 AST 相似度阈值 [默认: 0.70]
  --threshold-shared FLOAT        shared/ 目录阈值 [默认: 0.30]
  --threshold-tests FLOAT         tests/ 目录阈值 [默认: 0.90]
  --min-lines INT                  最小函数行数 [默认: 3]
  --min-block-tokens INT          代码块级最小 token 数 [默认: 15]

降级控制:
  --no-degrade             禁止降级——Stage 失败 → exit 3
  --allow-degrade          允许降级——Stage N 失败 → 降级到 N-1，exit 4 [默认]

其他:
  --skip-cache             跳过缓存——强制重新解析 AST
  --ignore-patterns GLOB   额外忽略的文件 glob 模式
  --quick-init             冷启动加速——仅 Stage 0.5 签名指纹扫描

fix 参数:
  --group-ids IDS          指定修复的 DUP 组 ID（逗号分隔）
  --batch-size INT         每批修复数 [1-3] [默认: 3]
  --dry-run                预览模式——不实际修改文件
  --partial-extract        允许部分提取（LCS 公共核心）

退出码:
  0 = PASS — 无重复
  1 = WARN — 低/中重复（不阻断）
  2 = ERROR — 高/严重重复（阻断 commit）
  3 = TOOL-ERROR — 引擎故障（跳过门禁）
  4 = DEGRADED — 降级运行（有结果但部分 Stage 未执行）
```

### 16.10 故障与操作手册

| # | 场景              | 触发条件                  | 诊断/操作                          | 恢复            |
| - | --------------- | --------------------- | ------------------------------ | ------------- |
| 1 | Tree-sitter安装失败 | import tree\_sitter报错 | pip install tree-sitter-python | Stage 2可用     |
| 2 | 缓存损坏自愈失败        | \_integrity校验失败       | 删除function\_cache.json→重新全量扫描  | 新缓存生成         |
| 3 | 修复中断恢复          | 残留checkpoint文件        | atomic\_fixer自动检测→WAL RECOVER  | 代码恢复到修复前      |
| 4 | BRS≥76触发停止      | 去重导致爆炸半径过高            | monoculture\_guard生成原因报告       | 停止该组去重        |
| 5 | Doom Loop冻结     | 同一DUP组3次修复失败          | doom\_loop\_guard冻结+Owner告警    | 生成TaskCard    |
| 6 | 影子清单幻觉          | import校验发现不存在函数       | shadow\_trust\_validator自动清除   | Trust Score更新 |

### 16.12 并发操作模型

| 冲突场景                     | 检测方式                  | 解决策略                  | 合并规则      |
| ------------------------ | --------------------- | --------------------- | --------- |
| 同一.py文件同时修复              | Pre-Apply SHA256重验证   | 后写者ABORT+fix\_plan重生成 | 不同DUP组可并行 |
| function\_cache.json并发写入 | PID锁+os.replace()原子写入 | 后写者等待PID锁释放           | 最后写入者胜    |
| 同一DUP组并发修复               | group\_id锁            | 第二个修复者ABORT           | 同组串行      |
| 扫描与修复并发                  | 修复前强制刷新缓存             | 修复基于最新扫描结果            | 修复优先      |

***

## §17 容量升级

> temporal_type: permanent

| 维度     |    当前容量   | 升级触发条件             | 升级方案                           |
| ------ | :-------: | ------------------ | ------------------------------ |
| 函数数    |    342    | > 1,500            | Tier 3→4 自适应 + SQLite 符号索引替代内存 |
| 扫描模式   |   增量+全量   | CI 集成后             | 并行扫描（ThreadPoolExecutor）       |
| 缓存     |  JSON 文件  | > 10MB             | SQLite 缓存后端                    |
| 修复并发   | 1 session | 多 AI session       | Redis/文件锁增强                    |
| LLM 验证 |     无     | Claude 5/Opus 5 发布 | Stage 3 自动启用                   |

***

## §18 决策记录

> temporal_type: permanent

| #  | 决策                                | 依据                  | 替代方案            | 触发重审条件                     |
| -- | --------------------------------- | ------------------- | --------------- | -------------------------- |
| 1  | AST 相似度阈值 0.7/0.85/0.95           | Wave 1 默认+惯用法豁免减少误报 | 无阈值硬编码→策略树      | 误报率 > 20% 或漏报率 > 30%       |
| 2  | Wave 1-2 不需要 LLM                  | Stage 0.5-2 覆盖 95%  | Wave 1 即启用 LLM  | LLM 判断力质变                  |
| 3  | 不引入 SonarQube                     | 1 人团队不需要            | SonarQube 集成    | 项目引入 SonarQube             |
| 4  | 只做 Python AST                     | 当前项目纯 Python        | Tree-sitter 多语言 | TypeScript/Go > 10 文件      |
| 5  | tests/ 阈值 0.9                     | 测试中合理重复多            | 降低 tests 阈值     | 测试文件 > 50 且维护负担            |
| 6  | 单次 --fix 最多 3 组                   | 防止改动范围过大            | 全量自动修复          | Phase 3/4 施工频率翻倍           |
| 7  | Suitability < 40 绝不提取             | 防止盲提取               | 无门禁             | 误提取率 > 5%                  |
| 8  | BRS ≥ 76 停止去重                     | 爆炸半径悖论      | 无上限             | shared 函数历史故障影响 caller > 5 |
| 9  | Grandfather ≥ 30 天不自动修            | 古老重复深度纠缠            | 无时间豁免           | 架构重构后模块数变化 > 30%           |
| 10 | 观察期 14 天                          | Microsoft SDP 工业实践  | 7 天             | 3 月数据：80%+ 回归 7 天内暴露       |
| 11 | 签名匹配(Channel A)优先于语义匹配(Channel B) | 签名精确度更高             | 语义优先            | 两通道结果交叉 > 30%              |
| 12 | 蓝图模板 v3.5/v3.6 升级                 | 模板升级要求              | 不升级             | 模板版本落后 > 2 个小版本            |
| 12 | 引擎退役路径文档化                         | SAS < 25 持续 3 月     | 无退役机制           | 引擎月度维护 > 2h 持续 3 月         |

***

## 术语表

| 术语                  | 精确定义                                        | 易混淆        | 区别                                                |
| ------------------- | ------------------------------------------- | ---------- | ------------------------------------------------- |
| BRS                 | Blast Radius Score——共享函数爆炸半径0-100           | SBS        | BRS=函数级；SBS=模块级                                   |
| SBS                 | Shared Burden Score——模块import表面积负债0-100     | BRS        | SBS=模块级聚合                                         |
| SAS                 | Simplicity Audit Score——引擎成本效益自审计           | —          | SAS<25→退役建议                                       |
| Suitability         | 安全提取适配性0-100                                | —          | <40=UNSAFE；40-69=NEEDS\_REVIEW；≥70=SAFE           |
| Grandfather         | ≥30天的古老重复代码                                 | —          | 受三定律保护，永不自动修复                                     |
| Doom Loop           | 修复→break→修复→break循环                         | —          | 3次失败→L4冻结                                         |
| 影子清单                | shadow\_api\manifest.yaml——AI生成时注入的共享API列表 | SSoT       | 影子清单=AI预防用；SSoT=运行时注册用                            |
| DecisionFingerprint | 决策指纹——不可变追加日志唯一标识                           | —          | sha256(group\_id+action+timestamp+operator)\[:16] |
| 微克隆                 | 2-10行短模式高频重复                                | Type-1/2/3 | 微克隆=n-gram频率；Type-1/2/3=函数级                       |
| 退化运行                | Stage失败后跳过该Stage继续扫描                        | 降级         | 退化=组件级跳过；降级=策略级调整                                 |

## 已知问题与盲点登记

| # | 问题                      | 严重性 | 根因                           | 解决方案                              |  状态  |
| - | ----------------------- | :-: | ---------------------------- | --------------------------------- | :--: |
| 1 | Tree-sitter grammar版本漂移 |  高  | Python语法更新                   | grammar版本锁定+兼容性自检                 |  已缓解 |
| 2 | 行为采样沙箱安全边界              |  高  | 恶意代码执行风险                     | AST副作用检测+subprocess隔离+256MB+500ms |  已缓解 |
| 3 | LLM语义判断不可用              |  中  | Stage 3缺失                    | Stage 0.5-2覆盖95%                  | 设计决策 |
| 4 | 跨语言去重不支持                |  低  | 只做Python AST                 | 当前项目纯Python                       | 设计决策 |
| 5 | 影子清单消费验证回环未闭环           |  中  | Context Engine集成待完成          | Wave 3渐进式三层记忆                     |  待施工 |
| 6 | ExitCode三重定义            |  中  | report.py/degradation.py自建副本 | 统一从exit\_codes.py import          |  待修复 |

## 自检与闭合清单

| #  |  阶段 | 检查项                                         | 确认方式                        |  状态 |
| -- | :-: | ------------------------------------------- | --------------------------- | :-: |
| 1  |  设计 | §3每个组件在§4有对应接口                              | 逐组件核对                       |  ☐  |
| 2  |  设计 | §4每个接口在§16有对应施工步骤                           | 逐接口核对                       |  ☐  |
| 3  |  设计 | §5每个约束在§9有对应测试                              | 逐约束核对                       |  ☐  |
| 4  |  设计 | §0.1每个代码文件在§11有对应产出物                        | 逐文件核对                       |  ☐  |
| 5  |  设计 | §10每个依赖在cross-module-dependency-registry有条目 | 逐依赖核对                       |  ☐  |
| 6  |  前  | 已读取蓝图全文                                     | 逐节确认                        |  ☐  |
| 7  |  前  | 术语表每个术语含义已理解                                | 能回答BRS和SBS的区别               |  ☐  |
| 8  |  前  | 成熟度声明中volatile/evolving已标记                  | 知道哪些可改哪些不可改                 |  ☐  |
| 9  |  前  | 已知问题中未解决的问题已知晓                              | 知道哪些坑不能踩                    |  ☐  |
| 10 |  中  | 每步施工后执行验证命令                                 | exit 0才进下一步                 |  ☐  |
| 11 |  中  | 新代码文件头部十五字段完整                                | 逐文件核对                       |  ☐  |
| 12 |  中  | 修改接口契约后检查§18决策记录                            | 决策ID+依据已更新                  |  ☐  |
| 13 |  后  | §0代码对齐验证已更新                                 | construction\_progress与实际一致 |  ☐  |
| 14 |  后  | 临时时态内容已清理                                   | 迁移方案已执行→删除                  |  ☐  |

## 成熟度声明

| 设计维度      |    成熟度   |  信心 | 升级标准                         |
| --------- | :------: | :-: | ---------------------------- |
| 核心架构      |  stable  |  高  | Wave 3完成后→frozen             |
| 接口契约      |  stable  |  高  | Wave 3策略树落地后→frozen          |
| 数据格式      | evolving |  中  | Wave 3策略树替换硬编码后→stable       |
| 施工步骤      | evolving |  中  | Wave 3完成后→stable             |
| BRS/SAS算法 | evolving |  中  | 3月运行数据验证后→stable             |
| 影子清单信任链   | volatile |  低  | Context Engine集成完成后→evolving |

## 版本演进路线图

| 版本      | 核心变更                        | 施工状态 |
| ------- | --------------------------- | :--: |
| v0.1.0  | 初始设计                        |  已完成 |
| v0.4.0  | Wave 1核心阻断+门禁               |  已完成 |
| v0.7.0  | 爆炸半径防护+Grandfather          |  已完成 |
| v0.9.0  | 微克隆+自动测试+审计链                |  已完成 |
| v0.13.0 | GATE-DEDUP+pre-commit+DAG绑定 |  已完成 |
| v0.14.0 | 模板v3.5/v3.6合规+20章节回填        |  已完成 |
| v0.14.1 | 名称修正+ExitCode统一+月度调度+策略树YAML+依赖同步 |  已完成 |
| v0.15.0 | Wave 3——策略树YAML+月度调度+依赖同步 | 部分完成 |

***

## Vibe Coding 铁律（本蓝图强制）

> 施工声明——AI 进入蓝图修改/施工时必读。永久保留。

| #  | 铁律                                                     |
| -- | ------------------------------------------------------ |
| 1  | Suitability Score < 40 → 绝不提取                          |
| 2  | BRS ≥ 76 → 停止去重                                        |
| 3  | Grandfather ≥ 30 天 → 永不自动修复                            |
| 4  | 单次 --fix 最多 3 组重复                                      |
| 5  | 修复后 MUST 全量测试零失败                                       |
| 6  | 缓存损坏 → 自动 full rebuild（不允许 exit 3）                     |
| 7  | Stage 失败 → 降级运行（exit 4），不允许崩溃                          |
| 8  | `@intentional-duplicate` 标记 → 不报告                      |
| 9  | Python 惯用法 + 设计模式 → 不产生误报                              |
| 10 | 引擎自扫描可运行——自身源码去重检测不崩溃                                  |
| 11 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码    |
| 12 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 |
| 13 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准"        |

***

## 蓝图拆分判定标准

> 铁律 #13 操作定义——蓝图超过 ~800 行或包含多个独立职责域时 MUST 执行。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同（同一模块的升级/扩展）→ 原地升级
  │   条件：服务对象相同 + 变更频率同步 + 依赖关系重叠
  │   操作：在 §17 容量升级附录中增量记录
  │
  └ 职责不同（独立子系统/独立能力域）→ 拆分独立蓝图
      条件（满足任一即触发）：
      a) 有独立的 module_id 前缀
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint_registry.yaml 同步更新
```

## 安全删除协议

> 施工声明——AI 施工涉及删除时必读。永久保留。

| # | 删除对象                                             | 删除条件        | 验证                         |
| - | ------------------------------------------------ | ----------- | -------------------------- |
| 1 | `_temp*` / `_check*` / `_fix*` / `_phase_*` 前缀文件 | session 结束前 | 零残留扫描                      |
| 2 | 已完成修复的 checkpoint                                | 14 天后自动清理   | checkpoint 文件夹大小 < 200MB   |
| 3 | 已完成修复的 recovery manifest                         | 14 天后自动清理   | manifest 总大小 < 100MB       |
| 4 | DEAD 共享模块                                        | Owner 确认后   | 累积死模块 > 5 → Session Log 强调 |

## 必备链接

> 施工声明——AI 进入蓝图时必读。永久保留。

| # | 文件                | 路径                                                                                                    |
| - | ----------------- | ----------------------------------------------------------------------------------------------------- |
| 1 | 蓝图模板 v3.3         | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\blueprint-template.md`                       |
| 2 | 压缩工作流标准           | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_030_doc_numbering_metadata.yaml`  |
| 3 | 代码构建标准            | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\engineering\code-construction-standards.md` |
| 4 | 脚本质量标准            | `D:\ZephyrAlpha\scripts\governance\quality-standard.md`                                               |
| 5 | 蓝图注册表             | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml`                                              |
| 6 | 依赖图               | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md`                             |
| 7 | Gate Engine 蓝图    | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\gate_engine\blueprint.md`                          |
| 8 | Context Engine 蓝图 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\context_engine\blueprint.md`                       |
| 9 | Shared Core 蓝图    | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\shared_core\blueprint.md`                          |

## 已有类似功能

| # | 功能             | 位置                    | 与本蓝图关系                             |
| - | -------------- | --------------------- | ---------------------------------- |
| 1 | D-D-07 词法级精确匹配 | `scripts/governance/` | 互补——D-D-07 是 Type-1，本引擎是 Type-1\~4 |
| 2 | GATE-DEDUP 门禁  | MOD-GATE_ENGINE           | 本引擎提供 exit code → Gate 判定          |

## 涉及的文件范围

| 目录                                                                | 文件数 | 说明     |
| ----------------------------------------------------------------- | :-: | ------ |
| `D:\ZephyrAlpha\src\zephyr\infra_ops\code_dedup_engine\` |  68 | 核心源码   |
| `D:\ZephyrAlpha\scripts\pre-commit\`                 |  1  | Pre-commit 入口 |
| `D:\ZephyrAlpha\tests\unit\`                                      |  1+ | 测试     |
| `D:\ZephyrAlpha\data\cache\`                                      |  26 | 运行时数据  |

***

## 1. 已实现代码完整路径索引

> AGENTS.md §6.14 蓝图-代码同步强制约定。

### 1.1 源码文件

> 68 个 .py 文件全部已实现，完整清单见 §0.1。

### 1.5 路径索引使用指南

读取顺序：§1(已实现清单) → 模块分解(职责+自治权限) → 施工Phase(下一步)



## Consumers
- zephyr.code_dedup_engine (internal)
