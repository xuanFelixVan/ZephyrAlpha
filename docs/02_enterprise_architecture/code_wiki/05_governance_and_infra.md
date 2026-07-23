---
module_id: VIEW-CODE-WIKI-05-GOVERNANCE-INFRA
title: "05 · 治理与基础设施域"
doc_type: architecture_view
rule_form: declarative
status: active
version: 1.0.0
date: 2026-07-23
owner: ZephyrAlpha-Owner
ttl: permanent
language: zh
created_by: agent
---

# 05 · 治理与基础设施域（Governance & Infrastructure）

> 范围：`src/zephyr/` 下 `governance`、`gov_audit`、`gov_code_quality`、`gov_drift`、`gov_enforcement`、`gov_rule`、`security`、`data_security`、`data_governance`、`compliance`、`infrastructure`、`integration`、`shared`、`autonomy_core`、`frontend`，以及 `src/zephyr/service_layer_owners.yaml`。
> 本文全部结论基于**静态代码/配置审查**（DDL、文件头治理锚定、注册表 YAML），未对 ClickHouse/PostgreSQL 做连接实测。

## 目录

- [1. 域地图与规模](#1-域地图与规模)
- [2. 提交链：GitCommitGateway 与 session_worktree](#2-提交链gitcommitgateway-与-session_worktree)
- [3. Commit Gates 体系（pre-commit 门禁）](#3-commit-gates-体系pre-commit-门禁)
- [4. Post-commit Reconciler 体系](#4-post-commit-reconciler-体系)
- [5. depgraph 机制（设计态 / 运营态）](#5-depgraph-机制设计态--运营态)
- [6. Registry 体系（32 个 registry 总索引）](#6-registry-体系32-个-registry-总索引)
- [7. SSoT 真源分类铁律](#7-ssot-真源分类铁律)
- [8. 治理包逐个解剖](#8-治理包逐个解剖)
- [9. 基础设施件（永久系统）](#9-基础设施件永久系统)
- [10. boot_hooks 事件接线](#10-boot_hooks-事件接线)
- [11. autonomy_core / frontend / integration / shared / service_layer_owners](#11-autonomy_core--frontend--integration--shared--service_layer_owners)
- [12. 架构观察与风险点](#12-架构观察与风险点)

---

## 1. 域地图与规模

| 包 | .py 文件数 | 域（DOMAIN） | 一句话定位 |
|---|---|---|---|
| `infrastructure` | 315 | D_INFRA_RUNTIME / D_INFRA_RECOVERY | 运行时基础设施（数据库、事件、SLA、遥测、回滚、MCP 底座） |
| `governance` | 284 | D_GOVERNANCE | 治理核心：任务状态机、审计 reconciler、depgraph schema、能力反查、持久化 |
| `shared` | 266 | D_SHARED | 跨层共享：EventBus、契约、路径 SSoT、生命周期、可观测性 |
| `security` | 179 | D_SECURITY | 访问控制（KillSwitch/RBAC）、LLM 安全网关（LSG）、红蓝对抗 |
| `gov_enforcement` | 167 | D_GOV_ENFORCEMENT | 规则执行：提交链、commit gates、行为准入 |
| `autonomy_core` | 113 | （自治核心） | 技能子系统、上下文引擎、触发路由、渐进披露 |
| `integration` | 76 | D_INTEGRATION | MCP 服务器、管线编排器、向量记忆 |
| `gov_drift` | 74 | （漂移检测） | 漂移引擎、检测器注册、基线管理 |
| `gov_audit` | 70 | D_GOVERNANCE（MOD-INF-020） | 审计追踪：Merkle、信任引擎、取证包、DORA 指标 |
| `gov_code_quality` | 66 | — | 代码质量（`code_dedup` 子包等） |
| `frontend` | 24 | D_FRONTEND（MOD-L08-001） | 人机交互层，Panel 仪表盘 |
| `compliance` | 15 | D_COMPLIANCE（MOD-L10-001） | **空壳**：合规实现已迁移至 governance/gov_audit（`compliance/__init__.py` 头注 "5.60.8 治本"） |
| `data_security` | 7 | D_DATA_SEC | **design 阶段骨架**（`__init__.py` 头注 `[MATURITY] design`，`__all__ = []`） |
| `data_governance` | 7 | D_DATA_GOV | **design 阶段骨架**（同上） |
| `gov_rule` | 3 | — | 仅 `constitutional_update/`（宪章更新） |

（文件数为 `find src/zephyr/<pkg> -name "*.py" | wc -l` 实测，含 `__pycache__` 之外全部 `.py`。）

---

## 2. 提交链：GitCommitGateway 与 session_worktree

### 2.1 GitCommitGateway — 全项目唯一合法 commit 入口

真源：`src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`（1719 行）。头部 INVARIANTS（L8）声明的机制：

- **全局跨进程串行锁**：`.ailocks/git_commit_global.lock`，TTL=1800s（L119-120：`_GLOBAL_LOCK_FILE` / `_LOCK_TTL_SECONDS`）。
- **GW 标记**：环境变量 `ZEPHYR_COMMIT_GATEWAY=1` + commit message 追加 `[GW:session_id]`（L117-118）；配套 FORGED-GW-MARKER gate（priority=29）防伪造。
- **commit 守卫 `_in_commit_flow`**：`_run_git` 检测到裸 `git commit` 且不在 commit 流程内时拒绝（L8）。
- **rename fallback**：`_commit_with_file_message` 内置 rename 检测，R100 时切换无 pathspec 提交并验证 staged 区（L8）。
- **门禁注册制**：架构债务 #AD-001 治本——`CommitGateRegistry` 声明式注册 `GateSpec`，替代硬编码 `_check_*`（L8）；YAML 驱动自动注册由 `gate_auto_registrar.py` 完成（L109 注释："YAML 驱动自动注册替代 76 个显式 import"）。
- **held_files 冲突阻断**：HELD-OVERLAP gate 在 commit 时检测目标文件是否被其他活跃 session 持有；`allow_overlap=True` 放行并追加 `[GW:<sid>:overlap]` 标记。
- 模块归属 `[BLUEPRINT] MOD-INF-035`，`[DOMAIN] D_GOV_ENFORCEMENT`（L1-3）。

### 2.2 CommitGateRegistry — 门禁注册表

真源：`src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py`（323 行）。核心不变量（L8）：

- `register` 幂等（同 gate_id 覆盖旧 spec）；
- **同 priority 不同 gate_id 抛 `GateRegistrationError`**（#ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 2 fail-closed）；
- `check_all` 按 priority **升序**执行所有 gate；
- **单 gate 异常降级为 fail-closed**（`passed=False`），不阻断后续 gate（L13 ERROR_CONTRACT："check_all 永不抛异常"）。
- 附带 `allow_overlap=True` 使用审计：落盘 `.runtime/gate_audit/allow_overlap_usage.jsonl`（L72-95 `_audit_allow_overlap_usage`）。
- `TEST_EXEMPT_PREFIXES` / `is_test_exempt` 是 tests/ 豁免唯一真源（L109-120），已纳入 golden hash 保护。

**命名区隔**（L33-37）：`GateSpec/CommitGateRegistry` 管 **pre-commit 阻断**；`ReconciliationRegistry` 管 **post-commit 漂移对账**，两者是完全不同关注点。

### 2.3 session_worktree — 物理隔离工作流

真源：`src/zephyr/gov_enforcement/rule_bridge/session_worktree.py`（**39 205 行**，全仓最大单文件之一）。四个公开 API：

| 函数 | 行号 | 职责 |
|---|---|---|
| `session_worktree_start(session_id, ...)` | L11581 | 创建独立 git worktree（`.aidrafts/{session_id}/`），注册逻辑 session（pid=0），spawn heartbeat daemon |
| `session_worktree_commit(session_id, files, message, ...)` | L20970 | 同步主工作区编辑到 worktree → 跑 pre-commit gates → commit；内置 auto-claim + HELD-OVERLAP 硬阻断（`allow_overlap=True` 逃生） |
| `session_worktree_merge(session_id)` | L31066 | merge 回主分支；pre-merge 自动清理冗余未提交改动；跑 pre-merge 拓扑检查 |
| `session_worktree_abort(session_id, files=[...])` | L34770 | 放弃：tracked 文件 `git checkout --` 还原，untracked 物理删除 |

辅助：`generate_session_id()` 在 `src/zephyr/gov_enforcement/rule_bridge/session_claim.py:87`。

**heartbeat 保活**（#ARCH-HEARTBEAT-001）：`heartbeat_daemon.py`（`rule_bridge/`）是独立 detached 进程，每 30s 刷新 `last_heartbeat` 并追加 `heartbeat.jsonl` 审计；`_is_session_alive` 用 90s 新鲜度判据（3×30s），daemon 死亡 → 90s 后 session 判死 → held_files 自动释放。阻塞窗口从 TTL=3600s 缩短到 90s。设计文档见 `docs/_archive/ruling_session_worktree_heartbeat.md`（heartbeat_daemon.py L1）。

**为什么需要 worktree**（git_commit_gateway.py L18-23 docstring）：多 AI session 共享工作目录导致 stash 堆积；每 session 独立 worktree 编辑/commit，互不干扰，无需 stash。

### 2.4 逃生通道

- `allow_overlap=True`（commit/merge 参数）——放行 HELD-OVERLAP，追加审计标记。
- `emergency_commit.py`（`rule_bridge/`）——紧急提交，成本递增设计。
- `ZEPHYR_BYPASS_LOOKUP=1`——绕过 CAPABILITY-LOOKUP-REQUIRED gate，不留 commit 痕迹，须人工事后审计（同 session 超 N 次会被 POST-COMMIT-GUARD 升级阻断）。
- commit message 含 `[no-lookup:<reason>]`——常规逃生，reason 须经 `capability_lookup_bypass_policy.py` 白名单校验（gate-fix/test-fix/merge-prep/continuation/investigated/bugfix 等）。

---

## 3. Commit Gates 体系（pre-commit 门禁）

### 3.1 体系结构

- 全部 gate 位于 `src/zephyr/gov_enforcement/commit_gates/`（80+ 个 `*_gate.py` 文件）。
- 每个 gate 模块暴露 `make_<x>_gate()` 工厂返回 `GateSpec(gate_id, check, priority)`。
- YAML 真源：`CFG-IN-PROCESS-GATE-REGISTRY-001`（In-Process Gate 注册真源，79 条）驱动 `gate_auto_registrar.py` 自动注册；`make_in_process_gate_registry_drift_reconciler` 做 YAML ↔ 内存注册表双向漂移检测（git_commit_gateway.py L74）。
- GATE 门禁登记表：`PS-REG-014`（119 条，含脚本型 gate）。

### 3.2 全量 gate 清单（按 priority 升序）

> 来源：对 `commit_gates/*.py` 中 `GateSpec(gate_id=..., priority=...)` 的静态扫描（个别 gate 文件内含两个 GateSpec 注册点，以运行时注册为准）。

| priority | gate_id | 文件 | 职责摘要 |
|---|---|---|---|
| 29 | FORGED-GW-MARKER | forged_gw_marker_gate.py | 防伪造 `[GW:]` 提交标记 |
| 30 | DIRECTORY-CONTRACT | directory_contract_gate.py | 目录契约校验 |
| 31 | SESSION-REQUIRED | session_required_gate.py | 必须有活跃 session_id |
| 32 | TTL-METADATA | ttl_gate.py | TTL 元数据校验 |
| 33 | FILE-PLACEMENT-TTL | file_placement_ttl_gate.py | 文件放置 TTL |
| 34 | DATETIME-NOW-FORBIDDEN | datetime_now_forbidden_gate.py | 禁裸 `datetime.now()`（时间真源纪律） |
| 35 | R5-DIGIT-SUFFIX | r5_digit_suffix_gate.py | 数字后缀命名约束 |
| 36 | CH-BATCH-SIZE | ch_batch_size_gate.py | ClickHouse 批次大小 |
| 37 | CH-FINAL-GATE | ch_final_gate.py | CH FINAL 使用约束 |
| 38 | CH-VERSION-COL | ch_version_col_gate.py | CH version 列约束 |
| 39 | RENAME-DEPGRAPH-SYNC | rename_depgraph_sync_gate.py | .py 重命名须先重建 depgraph |
| 40 | CLAIM-REQUIRED | claim_required_gate.py | 文件 claim 前置 |
| 41 | DATA-TASK-COMPLETENESS | data_task_completeness_gate.py | 数据任务完整性 |
| 42 | ENCODING-SAFETY | encoding_gate.py | 文件编码安全（先于内容语义检查） |
| 43 | MANUAL-ONLY-PERMANENT | manual_only_permanent_gate.py | 永久系统禁止手动-only |
| 45 | FOREIGN-CHANGE-DETECTION | foreign_change_gate.py | 外来改动检测 |
| 50 | HELD-OVERLAP | held_overlap_gate.py | held_files 冲突硬阻断 |
| 58 | NEW-FILE-DEPGRAPH-ENFORCEMENT | new_file_depgraph_gate.py | 新增 .py 须在 depgraph 有记录（tests/ 豁免，DB 不可达 fail-open） |
| 60 | CREATE-GUARD | create_guard.py | 新建文件守卫 |
| 63 | SNAPSHOT-DRIFT | snapshot_drift_gate.py | 快照漂移 |
| 64 | RECONCILER-HEALTH | reconciler_health_gate.py | reconciler 健康度 |
| 65 | SSOT-REDEFINITION | ssot_redefinition_gate.py | 真源重定义阻断 |
| 66 | UNSAFE-DICT-SPREAD | unsafe_dict_spread_gate.py | 危险字典展开 |
| 67 | DEPGRAPH-FRESHNESS | depgraph_freshness_gate.py | depgraph 新鲜度 |
| 68 | PURE-SHIM | pure_shim_gate.py | 纯垫片文件约束 |
| 69 | PURE-ASSERTION | pure_assertion_gate.py | 纯断言约束 |
| 70 | DANGLING-REFERENCE | dangling_reference_gate.py | 悬空引用 |
| 71 | NOQA-VALIDATION | noqa_validation_gate.py | noqa 豁免须登记 |
| 72 | NO-DOMAIN-NAME-ZH-DIRECT-ACCESS | domain_name_zh_direct_access_gate.py | 禁直读域中文名（SSoT） |
| 73 | VOCAB-CHAIN | vocab_chain_gate.py | 词汇链一致性 |
| 74 | RULING-REFERENCE | ruling_reference_gate.py | 裁定#NNN 引用须登记（阶段2 hard block） |
| 75 | ARCH-REFERENCE | arch_reference_gate.py | #ARCH-XXX 议题引用须登记 |
| 76 | RULE-FOUR-WAY-ALIGN | rule_four_way_alignment_gate.py | 规则四向对齐 |
| 77 | BLUEPRINT-FORMAT | blueprint_format_gate.py | 蓝图格式 |
| 78 | GATE-DOMAIN-FK | domain_fk_gate.py | 域外键完整性 |
| 79 | BLUEPRINT-AMODULE-CONSISTENCY | blueprint_amodule_consistency_gate.py | 蓝图 ↔ A_module 一致 |
| 80 | VOCAB-HARDCODE | vocab_hardcode_gate.py | 词汇表硬编码 |
| 81 | NO-BARE-GETENV | bare_getenv_gate.py | 禁裸 `os.getenv` |
| 82 | PERM-TRIGGER | perm_trigger_gate.py | 永久系统触发方式（禁 cron/sleep-loop） |
| 83 | MSG-EXPOSURE | msg_exposure_gate.py | 消息暴露面 |
| 84 | EMPTY-HANDLER | empty_handler_gate.py | 空 handler |
| 85 | FILE-COPY | file_copy_gate.py | 文件复制对 |
| 86 | ID-UNIQUENESS | id_uniqueness_gate.py | 标识符唯一 |
| 87 | EXEMPT-ZONE-FM | exempt_zone_frontmatter_gate.py | 豁免区 frontmatter |
| 88 | MODULE-ID-CONSISTENCY | module_id_consistency_gate.py | module_id 一致性 |
| 89 | ORPHAN-MODULE | orphan_module_gate.py | 孤儿模块 |
| 90 | FUNCTION-DUP | function_dup_gate.py | 函数重复 |
| 91 | DOC-REF-BROKEN | doc_ref_broken_gate.py | 文档引用断裂 |
| 92 | NO-HIGH-COMPLEXITY | high_complexity_gate.py | 圈复杂度 |
| 93 | NO-GOD-CLASS | god_class_gate.py | 上帝类 |
| 94 | NO-BARE-SQL | bare_sql_gate.py | 禁裸 SQL（须走 DatabaseService） |
| 95 | NO-LONG-PARAM-LIST | long_param_list_gate.py | 长参数列表 |
| 96 | MSG-STYLE | msg_style_gate.py | 消息风格 |
| 97 | NO-UPWARD-IMPORT | import_direction_gate.py | 导入方向（禁向上导入） |
| 98 | NO-HARDCODED-URL | hardcoded_url_gate.py | 硬编码 URL |
| 99 | META-TESTS-COVERAGE | tests_coverage_gate.py | 测试覆盖 |
| 100 | DEPGRAPH-WRITE-PATH | depgraph_write_path_gate.py | depgraph 写入路径（apply_*.py） |
| 101 | CAP-CONSISTENCY | capability_consistency_gate.py | 能力一致性 |
| 102 | TEST-SOURCE-CONSISTENCY | test_source_consistency_gate.py | 测试↔源码一致 |
| 103 | NO-IMPORT-SIDE-EFFECT | no_import_side_effect_gate.py | 导入副作用 |
| 104 | SCRIPTS-IMPORT-INTEGRITY | scripts_import_integrity_gate.py | scripts 导入完整性 |
| 105 | GIT-CALL-BUDGET | git_call_budget_gate.py | git 调用预算 |
| 106 | UNDEFINED-NAME | undefined_name_gate.py | F821 未定义名 |
| 107 | IMPORT-INTEGRITY | import_integrity_gate.py | 导入完整性 |
| 108 | BARE-SUBPROCESS | bare_subprocess_gate.py | 裸 subprocess |
| 109 | RULING-COMMIT-VERIFIED | ruling_commit_verified_gate.py | 裁定同提交原子性 |
| 110 | CAPABILITY-LOOKUP-REQUIRED | capability_lookup_required_gate.py | 施工前能力反查强制 |
| 111 | GATE-PRECOMMIT-OFFLINE | precommit_offline_gate.py | pre-commit 离线 |
| 112 | FOLDER-CAPACITY-HARD-LIMIT | folder_capacity_hard_limit_gate.py | 目录容量硬限 |
| 113 | CONSUMERS-ACCURACY | consumers_accuracy_gate.py | CONSUMERS 头注准确性（warn-only；同文件另有 priority=116 注册点） |
| 113 | DEPGRAPH-PRE-REGISTRATION | depgraph_pre_registration_gate.py | depgraph 预登记补强（与 58 配合） |
| 114 | DERIVATION-ANNOTATION | derivation_annotation_gate.py | 派生标注（补强 SSOT-REDEFINITION） |
| 115 | RELATIVE-PATH-LITERAL | relative_path_literal_gate.py | 相对路径字面量 |
| 117 | ISSUE-RESOLVED-INTEGRITY | issue_resolved_integrity_gate.py | 议题已解决完整性 |
| 118 | STASH-ACCUMULATION | stash_accumulation_gate.py | stash 堆积 |
| 119 | BLUEPRINT-AMODULE-CROSS-CHECK | blueprint_amodule_cross_check_gate.py | 蓝图 A_module 交叉检查 |
| 120 | TABLE-NAME-REGISTRY | table_name_registry_gate.py | 表名登记 |
| 200 | CAPABILITY-OVERLAP | capability_overlap_gate.py | 能力重叠 |
| 830 | GATE-PANORAMA-ALIGNMENT | panorama_alignment_gate.py | 全景对齐（最末执行） |

注：静态扫描发现 CONSUMERS-ACCURACY 与 DEPGRAPH-PRE-REGISTRATION 同为 113——按 registry 不变量同 priority 不同 gate_id 应抛错，二者可能注册于不同 registry 实例或以运行时实际注册为准，此处如实标注存疑。

### 3.3 执行顺序设计逻辑

从 priority 排序可读出四层意图：

1. **29–45 身份/格式层**：先确认"谁在提交、文件是否合法"（GW 标记 → session → 编码 → 外来改动）。
2. **50–67 冲突/真源层**：HELD-OVERLAP(50) → NEW-FILE-DEPGRAPH(58) → CREATE-GUARD(60) → SSOT(65)。
3. **68–120 语义/引用层**：词汇链、裁定/议题引用、蓝图一致性、代码质量（复杂度/上帝类/裸 SQL）。
4. **200+ 全局层**：能力重叠(200)、全景对齐(830) 收尾。

---

## 4. Post-commit Reconciler 体系

真源：`src/zephyr/governance/audit/reconciliation_registry.py` —— `ReconciliationRegistry` + **38 个 `make_*_reconciler` 工厂**（`grep -c "def make_"` 实测），由 `GitCommitGateway` 在 post-commit 阶段统一调度（git_commit_gateway.py L47-106 的 import 清单即完整目录）。

优先级分段（静态扫描 `priority=` 分布，共 40 个唯一值）：

| 段 | 代表 reconciler | 职责 |
|---|---|---|
| 49–106 | manifest / path_tree / depgraph_ops | 基础对账（清单、路径树、depgraph 运营态） |
| 130–175 | yaml_sync / vocab_change / registry_sync | 规则数据同步（YAML→DB） |
| 200–280 | drift_scan / drift_fix / module_id_recommend | 漂移扫描与修复 |
| 300–630 | integrity_audit / index_generator / architecture_health | 完整性与索引重建 |
| 700–831 | **生命周期清理**：`make_stash_lifecycle_reconciler`(801)、`make_session_staging_lifecycle_reconciler`(802)、`make_root_temp_sweep_reconciler`(803) | stash/staging/临时文件 TTL 清扫（事件驱动，禁 cron） |

独立文件的 reconciler（`src/zephyr/governance/audit/`）：`remediation_progress_reconciler.py`、`runtime_violation_snapshot_reconciler.py`、`git_performance_monitor_reconciler.py`、`commit_gateway_abuse_monitor_reconciler.py`（allow_overlap 滥用监控真源）、`error_pattern_consumer_reconciler.py`、`workspace_hygiene_reconciler.py`、`blueprint_status_transition_reconciler.py`、`cross_layer_contract_signature_reconciler.py` 等。

**四要素约束**（AGENTS.md）：所有 reconciler 必须事件触发（post-commit），禁止 cron/Timer/sleep-loop；满足自动触发/自动运行/自动维护/自动关闭。

---

## 5. depgraph 机制（设计态 / 运营态）

### 5.1 存储与 Schema

- **真源在 PostgreSQL**（架构数据）：`src/zephyr/governance/depgraph_schema.py`（SH-DB-001）。连接串由 `get_depgraph_pg_connection()` 从环境变量派生；原 SQLite `data/databases/depgraph.db` 已删除归档（P2 迁移后）。
- 11 张表（depgraph_schema.py docstring L23-40）：`nodes`(28列)、`edges`(19列)、`domains`(15列)、`domain_dependencies`、`domain_events`、`contracts`(13列)、`rule_bindings`、`arch_constraints`、`arch_directory_tree`、`arch_path_mappings`、`_schema_version`。
- `init_db` 幂等（INVARIANTS）。

### 5.2 双态模型

| 态 | 写入方式 | 工具 |
|---|---|---|
| **运营态**（production/generated） | 扫描器自动登记 | `scripts/governance/generate_project_depgraph.py`（AST 扫描，`.runtime/depgraph_scan_cache.json` 缓存，content_hash 命中跳过解析） |
| **设计态**（planned） | AI 施工前手动登记 | `scripts/governance/apply_depgraph.py --add-design-node PATH BLUEPRINT_ID DOMAIN_ID planned` |

`apply_depgraph.py` 是**唯一合法 depgraph 写入入口**（禁止 AI 直接 Write 大文件 → 原子写入 + 变更前验证，ERROR_CONTRACT：文件不存在 exit 1 / YAML 解析失败 exit 2 / 验证失败 exit 3 / 写入失败 exit 4）。写入设计态时内置门闸：运营态为空 → 阻断并提示先跑 `generate_project_depgraph.py`；逃生 `--skip-refresh` 仅限故障。

### 5.3 三层防御（RULE-DEPGRAPH）

1. **L1 君子协定**：施工前 MUST 登记设计态（`--add-design-node` + `--add-edge`），完工后 `--transition-build-status NODE_ID production` 转正。
2. **commit-time 轻量预检**：NEW-FILE-DEPGRAPH-ENFORCEMENT gate（priority=58）——staged 新增 .py 在 nodes 表无任何记录则硬阻断；tests/ 豁免；DB 不可达 fail-open。
3. **pre-merge 拓扑硬阻断**：`session_worktree_merge` 经 `_pre_merge_gate_check` → `_run_pre_merge_topo_check` 调 `check_blueprint_code_alignment.py --json --scan-root <worktree>`，HIGH drift（ORPHAN_MODULE_ID/MODULE_ID_DRIFT）阻断 merge；checker 缺失 fail-closed，DB 不可用/超时 fail-open。LOW（CODE_NOT_IN_DEPGRAPH）暂态容忍，由 post-commit reconciler 兜底同步。

文件重命名配套：`git mv` 后 MUST `generate_project_depgraph.py --force` 重建，RENAME-DEPGRAPH-SYNC gate（priority=39）硬阻断未登记的新路径。

---

## 6. Registry 体系（32 个 registry 总索引）

总索引真源：`docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml`（自动生成于 2026-07-21，`total_registries: 32`；生成器 `scripts/governance/generators/generate_registry_master_index.py`，手工编辑无效）。程序化发现入口：`zephyr.infrastructure.asset_inventory.registry_adapter.discover_all_registries()`。

32 个 registry 一览（registry_id / 名称 / 条目数 / 状态）：

| registry_id | 名称 | 条目 | 状态 |
|---|---|---|---|
| GOV-AI-001 | AI 自治权限登记表（全模块权限终表） | 0 | active |
| CFG-ai-risk-register | AI 风险登记簿 | 11 | active |
| CFG-ai-session-registry | AI Session/Agent 登记表 | 0 | draft |
| REG-ARCH-ISSUE-001 | 架构议题注册表（#ARCH-XXX 真源） | 168 | active |
| CFG-business-streams | 业务流定义登记表 | 0 | active |
| PS-REG-021 | 能力→真源文件反查注册表 | 0 | active |
| PS-REG-007 | 跨模块依赖登记表 | 124 | active |
| PS-REG-019 | 声明式契约跟踪登记表 | 11 | active |
| REG-DERIVED-ID-001 | 派生标识符关系表 | 4 | active |
| CFG-directory-registry | 项目目录登记表 | 86 | active |
| REG-DOMAIN-NAMING-001 | 域命名规则表 | 5 | active |
| GOV-001 | 前沿大模型综合能力排名登记表 | 0 | active |
| PS-REG-012 | Frontmatter 字段定义登记表 | 58 | active |
| REG-FUNC-DOMAIN-001 | 功能域注册表 | 77 | active |
| PS-REG-014 | GATE 门禁登记表 | 119 | active |
| CFG-hard-boundaries | 硬边界登记表 | 0 | active |
| CFG-IN-PROCESS-GATE-REGISTRY-001 | In-Process Gate 注册真源（YAML 驱动自动注册） | 79 | active |
| CFG-infrastructure-registry | 运行时基础设施登记表 | 14 | active |
| CFG-interface-contract-registry | 接口契约注册表 | 5 | active |
| CFG-knowledge-article-registry | 知识条目登记表 | 0 | draft |
| CFG-noqa-exempt-registry | noqa 豁免登记 | 0 | unknown |
| CFG-panorama-exempt-list | panorama 豁免清单 | 0 | unknown |
| PS-REG-016 | 登记表的登记表（跨表一致性契约） | 21 | active |
| PS-REG-020 | 规则 AI 感知索引（trae 规则→operations/gate_ids） | 0 | active |
| PS-REG-018 | 规则路径目录（唯一真源 SSoT） | 166 | active |
| CFG-rule-enforcement-registry | 门禁规则集登记表 | 0 | active |
| CFG-rule-registry-collection | rule registry 合集 | 0 | unknown |
| REG-RULING-001 | 裁定中央登记表（裁定#NNN 真源） | 54 | active |
| CFG-scripts-registry | scripts 登记 | 0 | unknown |
| PS-REG-017 | 任务卡元层登记表 | 0 | active |
| CFG-test-suite-registry | 测试套件登记 | 0 | unknown |
| CFG-TRUST-BOUNDARY-001 | 信任边界 surface 登记表 | 0 | active |

注意：AGENTS.md 行文仍称"31 个 registry"，但总索引 `total_registries: 32`——文档以索引文件实测值为准（索引头注也声明"精确数量以该文件字段为准"）。

---

## 7. SSoT 真源分类铁律

规则真源：`docs/01_policies_and_standards/rules/trae_062_ssot_classification.yaml`（TRAE-062，L1_foundation，severity=critical）。

| 数据类型 | 真源 | 写入方式 |
|---|---|---|
| **规则数据**（trae_*.yaml / 契约 / 门禁 / 词汇表 / 注册表） | **YAML 文件** | `sync_yaml_to_depgraph.py` 单向同步到 DB（DB 只读缓存） |
| **架构数据**（depgraph.nodes/edges、decision_nodes/edges、dataflow 节点） | **PostgreSQL DB** | `apply_*.py` 直接写 DB |

判定流程：拿到数据 → 先问"规则数据还是架构数据？" → 规则数据改 YAML 后 sync；架构数据用 apply_*.py 直写 DB。配套 gate：SSOT-REDEFINITION(65)、DEPGRAPH-WRITE-PATH(100)、DERIVATION-ANNOTATION(114)。

相关数据纪律：RULE-DATA-OPS（trae_063）——破坏性 DB 操作前须完成必要性/真实性/可逆性三步验证，"重复"判定必须全字段 `GROUP BY HAVING count()>1`（2026-07-16 tick_data 误删 21 个月数据事故治本，#ARCH-CH-020）。

---

## 8. 治理包逐个解剖

### 8.1 `governance`（284 py，D_GOVERNANCE）

治理核心，子包按治理对象划分：`architecture_governance / context_governance / data_governance / financial_governance / intelligence_governance / lifecycle_governance / observability_governance / ops_governance / resilience_governance / security_governance`。关键模块：

- `capability_lookup.py`（MOD-INF-037）：能力→真源文件反查。设计原则是**真源唯一 + 自动派生**：YAML（`capability_canonical_file_registry.yaml`）只人工声明 capability_id/aliases/description；canonical_file/module_id/domain/maturity/duplicates 全部由磁盘扫描 + git log 实时派生，不持久化第二真源（对标 K8s Service + Endpoints 控制器）。
- `depgraph_schema.py`：见 §5.1。
- `audit/reconciliation_registry.py`：见 §4。
- `persistence/task_repo.py`：TaskRepository 任务状态机（10 状态），`_auto_commit_on_completion` 是 GitCommitGateway 的消费者。
- `rule_enforcement/`（gov_enforcement 下）：60+ 个 `g_trae_*.yaml` 规则定义 + `gate_engine/`、`rule_engine/`。

### 8.2 `gov_audit`（70 py，MOD-INF-020，Safety=H，human_gated）

审计追踪域。ARCH-042 阶段4裁定：root 平铺 62 个 .py 不建物理子目录，靠前缀簇（`audit_* / *_bridge / trust_* / merkle_*`）+ `_LAZY_IMPORTS`（40+ 条目）对外垫片保证可发现性。代表模块：`merkle_audit.py / merkle_hourly.py`（Merkle 审计链）、`trust_engine.py / trust_ring_manager.py`、`forensic_package.py`（取证包）、`replay_engine.py`、`dora_metrics.py`、`sbom_generator.py / supply_chain_security.py`（供应链）、`event_store.py`、`integrity_verifier.py`。不变量："所有审计模块健康检查通过才允许操作；AdmissionResult 为唯一准入判定结果"。

### 8.3 `gov_enforcement`（167 py，D_GOV_ENFORCEMENT）

- `rule_bridge/`：提交链全套（§2）+ `batched_auto_committer.py`（ARCH-GIT-CALL-BUDGET P2.3 批量自动提交）。
- `commit_gates/`：§3 全部 in-process gates。
- `rule_enforcement/`：规则定义 YAML（`g1_ingest.yaml`…`g9_strategy_correlation.yaml`、`g_trae_003`…`g_trae_059`）+ `gate_engine/`、`rule_engine/`、`adaptive_threshold.py`、`circuit_breaker.py`、`drift_detector.py`。
- `behavioral_admission/`：行为准入（`admission_controller.py`、`verdict_engine.py`、`vibe_coding_enforcer.py`、`code_review_ai.py`）。

### 8.4 `gov_drift`（74 py）

漂移检测域。`drift_engine.py` 是编排核心（SRC-0030 精简后）："检测器发现 → 调度 → 汇总 → 写入 + 风暴检测 + Evolution Engine 反馈"。`_detector_registry.yaml` 登记检测器；`detector_core/`、`baseline_manager.py`、`cascade_detector.py`（级联）、`forensics_engine.py`（取证）、`spiral_ews.py`（螺旋预警）、`reward_hacking_rebound_detector.py`（奖励黑客反弹）、`suppression_learner.py`（告警抑制学习）、`reconciler.py`。

### 8.5 `security`（179 py，D_SECURITY）

- `access_control/`（60+ 文件）：`kill_switch.py`（MOD-INF-018 canonical 熔断器，`get_kill_switch()` 单例；默认 NORMAL，触发后 TRIPPED 需 Owner 手动重置；Safety=H，human_gated）、RBAC（`derive_rbac_roles.py`、`cbac_matrix.py`）、`immutable_core.py`、`emergency_override.py`、`bootstrap_superadmin.py`。
- `llm_defense/llm_security/gateway.py`：LLM 安全网关（LSG，RULE-LSG-001：所有 LLM 调用必经安检）。分层防线（gateway.py import 清单）：`l0_supply_chain`（供应链）→ `l1_input`（输入）→ `l2_prompt_protection`（提示词保护）→ `l2a_process_sandbox`（进程沙箱）→ `l3_output`（输出）→ `l4_agent`（Agent）→ `l5_resource_protection`（资源保护）。
- `adversarial_validation/`：红蓝对抗（`commit_trigger.py` 的 `RedBlueTriggerConsumer` 由 boot_hooks 启动）。

### 8.6 其余治理包

- `gov_code_quality`（66 py）：代码质量域，含 `code_dedup/` 子包。
- `gov_rule`（3 py）：仅 `constitutional_update/constitutional_update.py`（宪章更新）。
- `compliance`（15 py）：**已空心化**——`__init__.py` 头注明确"全部合规实现已迁移至 zephyr.governance / zephyr.gov_audit 等 canonical 包；本包仅保留真实子包骨架，不再 re-export 任何符号（5.60.8 治本）"。
- `data_security`（7 py）、`data_governance`（7 py）：均为 `[MATURITY] design` 阶段骨架包（MOD-DATA_SEC / MOD-DATA_GOV，`__all__ = []`），仅有 `_extensions/api/core/infrastructure/models/services` 空壳结构。

---

## 9. 基础设施件（永久系统）

| 组件 | 真源文件 | 关键事实（均有文件头/文档证据） |
|---|---|---|
| **EventBus (M-07)** | `src/zephyr/shared/event_bus.py` | 单例 + 背压控制：Queue 深度每 emit() 采样，警戒水位 CAP-006=500 时生产者减速，>2× 阈值丢弃低优先级事件；`EventType` 枚举含 task.created/locked/completed 等；可选 `contract_id` 经 ContractBus Schema 校验，校验失败事件被拒（向后兼容） |
| **EventStore (RI-13)** | `src/zephyr/infrastructure/event_store.py` | SQLite 不可篡改审计日志（WAL + SHA256 checksum），默认 `data/events.db`；`store.record(event)` / `store.query(component=..., limit=...)`；STABILITY=frozen |
| **CostTracker (RI-15)** | `src/zephyr/infrastructure/cost_tracker.py` | Token/API 成本追踪（对标 AWS Cost Explorer + OpenAI Usage API），SQLite 存储（governance.db），`record_usage()` / `daily_report()`，日预算告警 |
| **SLAMonitor** | `src/zephyr/infrastructure/sla/sla_monitor.py` | RTO ≤ 300s / RPO ≤ 1 task（蓝图 MOD-TASK_SYSTEM §6.10）；事件驱动（`subscribe_eventbus()`：pipeline_failed→rollback_completed 自动记录）；目标见 `config/sla_targets.yaml` |
| **HealthAggregator** | `src/zephyr/infrastructure/system_telemetry/health_aggregator.py` | 12 系统三态探针（alive/ready/degraded），15s 轮询生成健康面板快照（MOD-MASTER-002 §十四）；Safety=H，human_gated |
| **Notifier** | `src/zephyr/infrastructure/observability/notifier.py` | 多渠道 Owner 通知，事件驱动（pipeline_failed / kill_switch_triggered） |
| **KillSwitch (SSoT)** | `src/zephyr/security/access_control/kill_switch.py` | 见 §8.5；支持单 Agent 阻断与全局熔断；`trigger()/reset()` 永不抛异常，返回 TriggerResult |
| **A2A Protocol (MOD-INF-025)** | `src/zephyr/infrastructure/a2a_protocol/` | 三层五协议：L1 发现+身份（AgentCard/JWT）、L2 通信+任务（Task 状态机/Message/Part Schema）、L3 协调+仲裁（Coordinator/Living Spec/死锁防护）；核心类型从 `zephyr.shared.protocols.a2a` 导入（真源唯一，禁重复定义） |
| **BaseMCPServer (MOD-INF-013)** | `src/zephyr/integration/mcp/_base_server.py` | JSON-RPC 2.0 over stdio 基类（ADR-0033）：tools/list、tools/call、initialize/ping、Content-Length 帧（MCP 2024-11-05），子类 `register_tool()` 注册工具 |
| **DatabaseService (MOD-INF-002)** | `src/zephyr/infrastructure/database_service.py` | 业务数据库统一访问（ClickHouse 已实现 / Redis 预留），连接池 + WAL + 健康检查；**唯一真源**，禁止裸 `duckdb.connect`（NO-BARE-SQL gate priority=94 配套）；`governance/persistence/database_service.py` 已收敛为 re-export |

---

## 10. boot_hooks 事件接线

真源：`src/zephyr/trading/boot_hooks.py`（691 行，`register_boot_hooks()` 在 L546，幂等 + hook_registry 按 name 去重）。由 `zephyr.trading.auto_runtime_core` 调用。接线全景：

**Task 系统 hooks**（hook_registry，L554-562）：`auto_unblock_dependents`(50)、`auto_retry_on_failure`(60，上限 `_MAX_AUTO_RETRY_LIMIT=3`)、`triple_alignment_on_verified`(70)、`cleanup_task_processes`(45)、`orc_vms_archive`(48)、`kb_vms_sync`(47)、`rbk_gate_freeze`(55)。

**事件驱动 hooks**（L566-571）：`escalation_check_event`(56)、`timeout_check_event`(56)、`budget_delta_event`(94)、`session_startup_init_budget`(10)、`session_shutdown_budget_close`(90)、`triple_align_event`(72)；并 `bus.subscribe("blueprint.changed"/"blueprint.decomposed", _hook_triple_align_event)`（L576-577）。

**永久系统启动接线**（均 try/except 降级，失败不阻断启动）：

1. `IdeHealthDaemon` — 僵尸 IDE 窗口自动清理（L586-589）。
2. `_subscribe_task_lifecycle_events` — EventBus TASK_CREATED/TASK_COMPLETED（L69-70）。
3. `_register_rbac_hooks` — task in_progress RBAC 检查。
4. `_init_shared_monitoring_modules` — LongevityMonitor / HealthcheckService / HealthDiscovery / MetricsRegistry / AutonomyMonitor（L79-146）。
5. `RollbackBootIntegration` — WAL/Verifier 自动初始化（P0-2，L598-602）。
6. `SLAMonitor.subscribe_eventbus()`（P1-10，L607-611）。
7. `Notifier.subscribe_eventbus()`（P1-10，L616-620）。
8. `HealthAggregator.subscribe_eventbus()`（P1-10，L625-629）。
9. `F5BootIntegration` + `F5ShutdownManager` — F5 四组件（DeadlockDetector/EscalationEngine/DelegationEngine/Arbitrator）自动初始化 + 自动关闭（AI-11 审计修复，L637-650）。
10. `_subscribe_eventbus_consumers()` — 统一调用 9 个消费方模块的模块级 `subscribe_eventbus()`（DM-2507-J，混合注册模式，各自幂等）。
11. `_subscribe_skill_freshness_events()` — `skill.freshness_critical`（L323）。
12. `RedBlueTriggerConsumer().start()` — 红蓝对抗提交触发消费线程，轮询 `data/red_blue/trigger_queue/`（MOD-INF-030 事件驱动；`ZEPHYR_RED_BLUE_AUTO_ENABLED!=1` 时只 log 不实跑）。
13. **MCP 集群自启**：daemon 线程跑 `scripts/mcp/launcher.py` 的 `launch_all()`，9 个 Server 按 DAG 拓扑排序启动（L668-691）。

MCP 服务器清单（`config/mcp.json` + `src/zephyr/integration/mcp/`）：task_manager、gate_engine、session_handoff(doc_guard)、intent_router(sentinel)、blueprint_search、sandbox、governance、telemetry、rule_discovery（rule_discovery_server.py 提供 `discover_applicable_rules`，是能力反查 MCP 接口）。基类见 §9 BaseMCPServer。

---

## 11. autonomy_core / frontend / integration / shared / service_layer_owners

- **`autonomy_core`（113 py）**：自治核心。包结构指引（ARCH-033 治本，`__init__.py` docstring）：`skill_*.py → skills/` 子包（封闭 MODULE_LIST）、`context_*.py + ce_*.py → context/` 子包（上下文引擎）、其余独立模块根目录平铺。关键模块：`trigger_router.py`（6 触发器事件路由，配置 `config/trigger_router.yaml`）、`progressive_disclosure_injector.py`（L0/L1/L2/L3 渐进披露）、`prompt_registry.py`、`spec_engine.py`、`phase_planner.py`、`skill_rbac_registry.py`、`file_autoregister.py`、`ide_watcher.py`。
- **`frontend`（24 py，MOD-L08-001，D_FRONTEND）**：人机交互层。`dashboard/app_panel.py` 是 Panel+HoloViz 仪表盘主入口（v3.1.0，#ARCH-047，10 Tab 治理+交易/回测），启动：`panel serve app_panel.py --show --port 5006`。
- **`integration`（76 py，D_INTEGRATION）**：MCP 服务器群（§10）+ `pipeline_orchestrator.py`（M1-M11 管线编排）+ `vector_memory/` + `llm_bridge.py` + `local_model/`。
- **`shared`（266 py，D_SHARED）**：跨层共享。`event_bus.py`（§9）、`io/paths.py`（`REPO_ROOT` 仓库根 SSoT）、`contracts/`（含 `task_repository_protocol`）、`protocols/a2a`（A2A 核心类型真源）、`foundation/constants.py`（TaskStatus 枚举）、`lifecycle/`（longevity/healthcheck/health_discovery）、`observability/metrics.py`（MetricsRegistry）。
- **`service_layer_owners.yaml`**（`src/zephyr/service_layer_owners.yaml`）：服务层模块技术 Owner 登记（schema v1.0.0，module_id=MOD-INF-002）。当前阶段单人全栈，`primary_owner: ZephyrAlpha`；登记了 mcp（6 server）/pipeline/knowledge_gates/feedback_loop/vector_memory/telemetry 等模块的 owner 映射文件路径，团队扩容后拆分为自然人。

---

## 12. 架构观察与风险点

1. **提交链成熟度高于业务链**：commit 路径有 ~78 个 in-process gates + 38 个 reconcilers + worktree 物理隔离 + heartbeat 保活，是全仓最硬实的子系统；但作为单用户回测系统，其复杂度（session_worktree.py 单文件 39 205 行）本身已成维护风险——单文件巨型化与 NO-GOD-CLASS(93) 精神存在张力。
2. **治理域内部存在"实/壳"分层**：`compliance` 已空心化（迁移完成），`data_security`/`data_governance` 仍是 design 阶段空壳（`__all__ = []`）；回测场景下数据治理实际由 RULE-DATA-OPS 纪律 + check_tick_duplication.py 工具承载，而非这两个包。
3. **registry 数量文档漂移**：AGENTS.md 写"31 个"，总索引实测 `total_registries: 32`；索引自身声明以文件字段为准，属可接受的暂态漂移，但说明文档同步滞后于生成器。
4. **gate priority 唯一性存疑点**：静态扫描发现 priority=113 被 CONSUMERS-ACCURACY 与 DEPGRAPH-PRE-REGISTRATION 共用，与 CommitGateRegistry"同 priority 不同 gate_id 抛错"的不变量表面冲突（可能分属不同注册时机/实例），建议以运行时 `list_gate_ids()` 实测确认。
5. **永久系统接线全部 fail-open**：boot_hooks 中所有永久系统启动均 `try/except` 降级（失败仅 warning），单用户场景合理，但意味着"守护进程未运行"不会有硬信号——RULE-GUARDIAN 的"守护进程未运行=禁止写操作"依赖 AI 自觉执行启动检查。
6. **未能连接实测**：depgraph（PostgreSQL）、governance.db（SQLite）等存储仅做了 DDL/代码级静态审查，未做连接探测与数据抽样；ClickHouse tick 数据相关结论（如 #ARCH-CH-020 排序键不含 price）引自规则文件记载，未实测验证。
