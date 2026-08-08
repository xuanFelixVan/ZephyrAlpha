---
title: code_dedup 模块退役与 CloneGuard SSoT 统一方案
date: 2026-08-08
status: active
ttl: task_bound
related:
  - docs/03_modules/_cross_layer/clone_guard/blueprint.md
  - docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
completes_when: "#ARCH-DEDUP-SSOT-CONFLICT-001 status=decided 且 code_dedup(MOD-INF-017) 整模块退役完成 + BRS 转移进 CloneGuard + SSoT 声明归真"
---

# code_dedup 模块退役与 CloneGuard SSoT 统一方案

> **关联议题**：#ARCH-DEDUP-SSOT-CONFLICT-001（5 套代码重复检测系统功能重叠 + SSoT 冲突）
> **退役模块**：MOD-INF-017（code_dedup_engine，64 .py + ~70 测试，三次审查实测）
> **吸收模块**：MOD-CLONE_GUARD（clone_guard）
> **方案日期**：2026-08-08
> **状态**：待执行（前置缺口已闭合；施工缺口 G1-G4 见 §10，已剔除过度工程）

---

## 1. 背景与问题

### 1.1 病根本质

项目 100% AI 开发 → AI 无记忆 → 为已解决任务重复生成 → AI Rot 指数累积（CloneGuard blueprint §1.1 核心论断）。这是去重防御体系存在的根本理由。

### 1.2 现状：5 套重复检测系统重叠

| 系统 | 模块 | 粒度/机制 | 防御层 | 处置 |
|---|---|---|---|---|
| CloneGuard | MOD-CLONE_GUARD | 函数级 AST 哈希 + CodeSAGE 嵌入 | L0/L1/L2/L3 | **保留为唯一引擎** |
| code_dedup | MOD-INF-017 | AST 比对 + 签名 + 微克隆 + auto-fix | 自有管道 | **整模块退役** |
| FUNCTION-DUP gate | commit_gates | 同目录顶层函数 ast.unparse+sha256 | L1 | **退役** |
| FILE-COPY gate | commit_gates + check_code_duplication | 文件级 AST 相似度 ≥0.7 | L1 | **退役** |
| dedup_extractor | MOD-INF-031 (auto_fix_engine) | ≥3 副本 body hash 自动提取 | 修复层 | **退役** |

### 1.3 SSoT 冲突点

code_dedup blueprint §0.4 声明"重复检测结果"(dedup_report.yaml) +"函数签名指纹"(function_cache.json) 为 SSoT，与 CloneGuard orchestrator.check()/audit() 产出 Finding 事实冲突。

---

## 2. 调研结论（6 个调研发现）

> 推翻初步判断，以下发现均经源码核查。

### 发现 1：CloneGuard 已完整建成（蓝图 frontmatter 过期）

`src/zephyr/clone_guard/orchestrator.py`（596 行）实装 `check()`/`audit()`/`compare()` 三层，asyncio+线程池并发调度 6 引擎，FindingAggregator 去重+多数表决+严重性就高，fail_closed 降级，health_score A-F，审计结果写 `.runtime/clone_guard_audit/`（派生产物不入 git）。蓝图 frontmatter `build_status: planned / construction_progress: not_started` 是未同步的过期声明。

**结论**：迁移为 Finding 消费者有现成接口，非无米之炊。

### 发现 2：CAPABILITY-OVERLAP gate 已实接 CloneGuard

`capability_overlap_gate.py:261-264` 直接 `CloneGuardOrchestrator(Path.cwd()).check(py_files)`，extract 级硬阻断、review 级警告、降级 warn-only。检测所有 staged .py（AM filter，含修改文件）。

**结论**：L1 防线已由 CloneGuard 单引擎把守，FUNCTION-DUP/FILE-COPY 是冗余。

### 发现 3：self_benchmark 是检测引擎自检，非相似度消费者

`self_benchmark.py` 是 5 组 Known-Answer Test，测 ASTComparator/MicroCloneDetector 自己准不准。唯一调用方 = `code_dedup cli verify`（gate-dedup hook 后端）。header 写明 `CONSUMERS: N/A (all consumers verified as phantom)`。

**结论**：它测的就是要退役的代码，唯一调用链随 gate-dedup 退役而消失。退役检测引擎后自检一并退役。

### 发现 4：CloneGuard 无"两段代码求 sim"API

orchestrator 方法是 `check(files)`/`audit(files)`/`compare(files, remote)`——对文件做克隆检测，非对两段 snippet 求 sim。适配器 Protocol 是 `detect/index/health_check`。

**结论**：逼 CloneGuard 暴露相似度 API 是架构污染。

### 发现 5：gate 注册真源 = in_process_gate_registry.yaml

`auto_register_gates()`（gate_auto_registrar.py）读 `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`。退役 gate = 删 YAML 条目 + 删 .py + 改测试。

### 发现 6：消费者依赖审计——爆破半径极小

全量 grep（排除 code_dedup 自身）证明外部生产消费者仅：
- `self_benchmark.py`（随检测退役）
- `governance/__init__.py` 重导出 4 符号（PhaseStatus/BlindSpotStatus/CanaryFile/cli），其中 PhaseStatus 在别处用的是其他模块自己的同名类（重导出 phantom），cli 重导出仅被 1 个 red-team 测试消费（随引擎退役）

佐证：旧容量治理议题（architecture_issue_registry.yaml line 767）写"CONSUMERS 62/65为空"。

**结论**：退役无外部生产代码受损。

---

## 3. 第一性原理分析

### 3.1 防御纵深本质分工

| 层 | 职责 | 精度/召回取向 |
|---|---|---|
| L0 写前 MCP | 源头预防，AI 生成前拦住 | advisory |
| L1 commit gate | 安全网 | **必须精度优先**（误报卡死高频提交，AI 提交频率远高于人） |
| L2 周期审计 | 找累积债 | **可以召回优先**（出报告不阻断，噪声可容忍） |
| L3 跨边界 | 合规 | 按需 |

**关键推论：召回优先的检测属于 L2，不属于 L1。** L1 天职是零误报硬阻断；把召回优先检测放 L1 会因误报卡死 AI 高频提交。这是评判 FILE-COPY 的根本标尺。

### 3.2 冗余成本

100% AI 开发提交频繁，每次 commit 跑 3 套 AST 哈希（FUNCTION-DUP + FILE-COPY + CloneGuard）是纯重复劳动，成本随提交频率放大。

---

## 4. 裁定结果

### 裁定 1：FILE-COPY 退役，接受 L1 缺口

退役 FILE-COPY gate + check_code_duplication.py。理由：
- 文件级 0.7 是召回优先信号，属 L2 审计不属 L1 commit 阻断
- 加文件级 adapter 违背 CloneGuard 函数粒度 + 精度优先（echo-guard 刻意 0.94）设计意图
- 2 副本文件复制从"硬阻断"降为"review 警告"正好对齐精度优先立场
- L0（MCP 写前查重）+ L2（audit 累积债）兜底，防御纵深不缺
- 如未来需文件级检测，加到 CloneGuard L2 `audit()`（出报告不阻断），绝不加 L1 adapter

### 裁定 2：self_benchmark 随检测引擎退役

理由：测的就是退役代码，唯一调用链随 gate-dedup 退役消失；逼 CloneGuard 暴露相似度 API 是架构污染。KAT 概念转移到 CloneGuard 测试套件（验证 `tests/clone_guard/test_orchestrator.py` 覆盖 T1/T2/T3 已知克隆对，不足则补——属 CloneGuard 自身增强）。

### 裁定 3：auto-fix 管道整体退役（含 dedup_extractor）

100% AI 开发下，重复修复应由 AI 执行（CloneGuard L0 suggest_refactor MCP + L2 refactoring_plan 冷启动引导），而非后台自动改写。auto-fix 在 AI 生成码上再叠自动改写 = 错误复合，违背项目精度优先/fail-closed/reconciler 只 warn 的气质。

**dedup_extractor 退役安全性已验证**（见 §5.3）。

### 裁定 4：BRS 转移（非退役）

monoculture_guard 的 BRS（爆炸半径评分，反过度去重制衡）是 code_dedup 独有且比 CloneGuard 多的 valuable 能力。**转移进 CloneGuard `_build_refactoring_plan`**：BRS≥76 时不建议重构，输出"保留重复，blast radius 隔离更安全"。转移后 CloneGuard 比原 code_dedup 更完整（检测 + 反制衡合一）。

---

## 5. 能力覆盖验证（逐能力核查 CloneGuard 是否涵盖且更好）

| code_dedup 能力 | CloneGuard 覆盖？ | 比 code_dedup 好？ | 处置 |
|---|---|---|---|
| 重复检测（AST/签名/符号/微克隆） | ✅ check()/audit() | ✅ 更好（多引擎+统一 Finding+多引擎表决） | 退役 |
| L0 源头预防（写前查重） | ✅ MCP check_before_write/search_functions | ✅ **code_dedup 完全没有，CloneGuard 净增** | — |
| L1 硬阻断（extract 级 3+副本） | ✅ CAPABILITY-OVERLAP prio200 无逃生 | ✅ **code_dedup 没有，CloneGuard 净增** | — |
| L2 周期审计 | ✅ orchestrator.audit() → .runtime/ | ✅ 持平 | — |
| Health Score | ✅ _compute_health_score A-F | ≈ 持平 | 退役 |
| 重构建议 | ✅ _build_refactoring_plan | ≈ 持平 | 退役 |
| acknowledged 白名单 | ✅ echo-guard.yml acknowledged | ≈ 粒度略粗，补元数据 | 退役+迁移 |
| **BRS 反过度去重** | ❌ 无 → **转移后有** | ✅ 转移后 CloneGuard 更完整 | **转移** |
| 自动提取共享函数 | ❌ 无 | — | 退役（见 §5.3） |
| 重构验证（shadow/canary/behavioral） | ❌ 无 | — | 退役（真损失，可接受） |
| b_shared.yaml SSoT 注册 | — 非缺口 | — | MOD-INF-016 ssot_guard 维护 |

### 5.1 b_shared.yaml 非缺口证明

`src/zephyr/shared/security/ssot_guard.py`（MOD-INF-016）是 canonical SSoT Guard，独立维护 b_shared.yaml。code_dedup 的 ssot_registrar 是冗余的并行写入（code_dedup blueprint 自己写"SSoT Guard + shared 目录属于 MOD-INF-016"）。退役安全。

### 5.2 dedup_extractor 不写 b_shared.yaml

grep `b_shared|manifest|register|ssot|shared_api` 在 dedup_extractor.py 零命中。它只提取代码，不注册 SSoT。与 b_shared 维护无关。

### 5.3 dedup_extractor 退役安全性证明（冷启动注入验证）

[AGENTS.md §RULE-CLONEGUARD（第十二件事）](file:///d:/ZephyrAlpha/AGENTS.md) AI 合规义务 ②：**冷启动调 `clone_guard.audit_status` 看累积技术债**。且 L1 硬阻断独立于 AI 行为（extract 级克隆 CAPABILITY-OVERLAP 硬阻断，无逃生通道）。

退役安全性三段证明：
1. **新重复债无法增长**——L1 硬阻断（保证，不依赖 AI 是否调 audit_status）
2. **既有债对 AI 可见**——AGENTS.md 强制 AI 冷启动调 audit_status（6 层闭环·可达性）
3. **AI 用判断力重构**——比机械提取更优，精度优先立场一致

**诚实保留**：audit_status 是 AI 按规调用（非系统自动注入），但 L1 硬阻断保证债不增长，最坏只是既有债延迟处理，不会恶化。

---

## 6. 治本施工方案

### 6.1 前置（闭合缺口）

| 步骤 | 内容 | 文件 |
|---|---|---|
| P0 | **conftest 解耦（退役硬前置，§10 G4）**：`tests/conftest.py` L104-123 importlib 注入 `code_dedup_engine` + L137-185 `_CODE_DEDUP_MODULE_MAP` + `zephyr.testing.code_dedup` 占位包——全局收集级耦合。移除 importlib 注入 + 删映射表 + 清理占位包，**跑 `pytest --collect-only` 验证全仓库收集不报错**，方可进 R4 | tests/conftest.py + zephyr/testing/code_dedup |
| P1 | BRS 转移：monoculture_guard 的 BRS 逻辑迁入 CloneGuard `_build_refactoring_plan`（BRS≥76 时不建议重构）。**关键依赖**：BRS 输入 caller_count/cross_layer_count 须从 depgraph 取，`depgraph_reader.py` 有 `get_edges_to_node` 边查询原语——**最简实现**：基于它 count 调用边即可（复用 monoculture_guard 现有简单计数逻辑，不上 BFS/中心性，避免过度工程，§10 G1）。**不写 depgraph**，守裁定。**转移后补 BRS 单测对照 monoculture_guard 原用例**（§8 风险表）。注：P1 转移后 monoculture_guard.py 暂留，R6 才删 | orchestrator.py + depgraph 最简只读查询 + tests/clone_guard/test_brs.py |
| P2 | CloneGuard acknowledged 补 grandfather_manager 元数据字段，迁移既有白名单 | echo-guard.yml + mcp_server.py |
| P3 | 验证 CloneGuard test_orchestrator.py 覆盖 T1/T2/T3 KAT，不足则补 | tests/clone_guard/ |

### 6.2 退役（依赖反向序）

| 批次 | 退役项 | 文件 |
|---|---|---|
| R1 | gate-dedup hook + 后端 | .pre-commit-config.yaml hook（L440-460，三次审查修正行号）+ scripts/governance/code_dedup/verify_dedup.py |
| R2 | FUNCTION-DUP gate | in_process_gate_registry.yaml 条目 + function_dup_gate.py + test_function_dup_gate.py |
| R3 | FILE-COPY gate + 后端 | in_process_gate_registry.yaml 条目 + file_copy_gate.py + check_code_duplication.py + 测试 |
| R4 | code_dedup 检测层 + 自检 | ast_comparator/micro_clone_detector/signature_matcher/symbol_index/diff_detector/function_discovery/cross_boundary_detector/false_negative_auditor/self_scanner/code_analyzer_runner + self_benchmark.py + 测试 |
| R5 | code_dedup auto-fix 管道 | auto_fixer/atomic_fixer/shadow_verifier/shadow_trust_validator/canary_manager/canary_register/behavioral_trust_checker/behavioral_sampler/shared_evolver/shared_lifecycle_manager/ssot_registrar/verifier/success_validator/pre_apply_integrity_gate/phase_executor/file_creator/extraction_safety/mock_duplicate_generator/code_simulator/recovery_manifest_writer + doom_loop_guard + 测试 |
| R6 | code_dedup 基础设施 + 审计器 | report/cli/config/cache_manager/grandfather_manager/risk_mitigator/trackers/* /debt_projector/decision_auditor/degradation/sensitivity_sweeper/thematic_clusterer/path_index_validator/contract_consistency_checker/dead_module_detector/stale_shared_detector/policy_tree_validator/observation_window_guard/integrations/integration_hub/prioritizer/annotations/exit_codes + health_monitor/monoculture_guard(BRS已转移)/simplicity_auditor/fifteen_dimension_auditor + __init__.py + 测试 |
| R7 | dedup_extractor | dedup_extractor.py + 测试 |
| R8 | governance/__init__.py 清理 | 删除 4 个 code_dedup 重导出（BlindSpotStatus/CanaryFile/cli/PhaseStatus） |

### 6.3 SSoT 归真

| 步骤 | 内容 | 文件 |
|---|---|---|
| S1 | code_dedup blueprint 归档（§0.4 SSoT 2 行删除，整模块标记 retired） | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md |
| S2 | CloneGuard blueprint frontmatter 归真（planned→production, not_started→complete）+ 补 BRS 反制衡能力声明 | docs/03_modules/_cross_layer/clone_guard/blueprint.md |
| S3 | AGENTS.md §RULE-CLONEGUARD 补"已吸收 code_dedup BRS"说明 | AGENTS.md（守 ≤1234 行硬上限） |
| S4 | registry 清理：capability_canonical_file_registry / module_translation_registry / in_process_gate_registry 同步退役条目。**+ depgraph DB 重生成**（§10 G2）：删 .py 后跑 `extract_depgraph.py` / `sync_yaml_to_depgraph.py` 移除 MOD-INF-017 节点 + 边（depgraph.nodes 是文件清单真源） | docs/01_policies_and_standards/_registry/catalogs/ + depgraph 重生成 |
| S5 | #ARCH-DEDUP-SSOT-CONFLICT-001 恢复（HEAD 有、工作树被并发 session 删）+ 裁定写入 + status→decided | architecture_issue_registry.yaml |

### 6.4 执行方式

- **session_worktree 物理隔离**：工作树有并发"五图对齐"session 在跑（20+ 文件被并发改），退役施工必须在 worktree 内做，避免索引覆盖竞态
- **分批退役**：按 R1-R8 依赖反向序，每批跑 pre-commit 门禁验证 **+ `pytest --collect-only` 验证测试收集不报错**（G3 测试规模 5 倍 + G4 conftest 全局耦合风险）
- **运行时幽灵检测**（Strangler Fig "watch for ghosts"）：R4/R6 删 code_dedup 后，conftest 的 importlib 动态注入（G4）是运行时幽灵——静态 grep 易漏。须跑**受影响测试目录全量 pytest**（非 collect-only，tests/governance/code_dedup/ 等 13+ 目录）+ grep 残留 `import code_dedup`/`from.*code_dedup`，验证运行时无 ImportError
- **串行提交**：经 GitCommitGateway（全局串行锁 + -F msg_file），禁 --no-verify

---

## 7. 治理预算与约束对齐

| 约束 | 对齐情况 |
|---|---|
| gate ≤ 54 | 退役 2 in-process gate（FUNCTION-DUP/FILE-COPY）+ 1 hook，gate 数 -2，守 I-GOV-3 无新增 |
| reconciler ≤ 121 | 不涉及 reconciler 新增 |
| AGENTS.md ≤ 1234 行 | S3 仅追加 1 行吸收说明，需等量退役空间（code_dedup 相关行若可删则对冲） |
| 新增模块登记 ARCH | 无新增模块（CloneGuard 已存在） |
| 模块 translation 登记 | code_dedup 退役条目从 module_translation_registry 删除 |
| capability_canonical_file_registry | 退役 .py 的 creation_token 清理 |
| reconciler 只 warn/skip/fix-in-place | 退役是一次性代码变更，非 reconciler 动作 |
| 禁止时间触发 | CloneGuard audit 事件触发（MCP 冷启动/CI push），非 cron |
| 派生产物禁入 git | .runtime/clone_guard_audit/ 已不入 git；本方案文档是手写设计文档非派生产物，可入 git |
| pre-commit 门禁 | 每批退役后跑，禁 --no-verify |

---

## 8. 风险与回滚

| 风险 | 概率 | 缓解 |
|---|---|---|
| 误删被外部依赖的 code_dedup 组件 | 低 | §2 发现 6 全量消费者审计已证明仅 self_benchmark 外部依赖（随退役） |
| BRS 转移后逻辑偏差 | 中 | P1 转移后补 CloneGuard BRS 单测，对照 monoculture_guard 原测试用例 |
| 并发 session 索引覆盖 | 中 | session_worktree 物理隔离 + GitCommitGateway 串行锁 |
| L2 audit_status AI 不调用导致债堆积 | 低 | L1 硬阻断保证债不增长；AGENTS.md 强制 AI 合规 |
| 退役后既有 772 findings 无人修 | 低 | L2 审计可见，AI 机会主义重构；比机械批量提取更安全 |
| conftest.py 引用 code_dedup 打断全局测试收集（§10 G4） | 中 | 退役前置：先核查 tests/conftest.py 引用并解耦 fixture，再删 code_dedup |
| BRS 转移后 depgraph 查询未实现致 BRS 死代码（§10 G1） | 中 | P1 基于 `get_edges_to_node` 做最简 caller_count 查询；转移后补 BRS 单测对照原用例 |
| 测试退役规模 5 倍于原估（~70，三次审查实测，§10 G3） | 中 | R4-R7 各批次含对应 13+ 测试目录清理；分批验证 pytest 收集不报错 |

**回滚**：每批退役独立 commit，可通过 `git revert <commit>` 单批回滚。R4-R6 整模块退役合并为可识别的 commit 边界便于回滚。

---

## 9. 净效果

CloneGuard 吸收 code_dedup 全部保留价值能力，并新增 code_dedup 没有的：
- L0 源头预防（MCP check_before_write）
- L1 硬阻断（CAPABILITY-OVERLAP 无逃生）
- BRS 反制衡（转移后检测 + 反过度去重合一）

**比退役模块更强**。唯一真损失是"重构验证套件"（shadow/canary/behavioral），这是裁定 3（AI 执行修复）的必然代价，与项目精度优先立场一致。不硬补——AI 重构后跑现有 pytest 套件即为验证。

---

## 10. 施工缺口补充与 2026 SOTA 验证

> 2026-08-08 多轮审查：核实 G1-G4 细节（depgraph_reader API、conftest 深度耦合、测试规模）；Web 检索 2026 最新研究（截至 2026.08）验证主架构。G5-G7（BFS/特征化测试/provenance）经判定过度工程已剔除，arXiv:2607.13077 反证剔除正确。

### 10.1 施工缺口（必须补，已回写 §6）

**G1 — BRS 转移的 depgraph 依赖（最关键）**
[orchestrator.py:120,329](file:///d:/ZephyrAlpha/src/zephyr/clone_guard/orchestrator.py#L120) 明写"不写 depgraph"，grep 证实 orchestrator 无任何 depgraph/caller/cross_layer 引用。但 BRS 输入 `caller_count`/`cross_layer_count`/`on_critical_path` 只能从 depgraph 取。三次审查核实 `depgraph_reader.py` 有 `get_edges_to_node` 边查询原语——**最简实现**：基于它 count 调用边即可（不上 BFS/中心性，避免过度工程）。**P1 缺一步**：CloneGuard 新增最简只读 depgraph 查询取 caller_count（不写 depgraph，守裁定）。否则 BRS 转移后无法计算 = 死代码。

**G2 — 模块退役的 depgraph DB 清理**
project_memory："文件清单真源在 PostgreSQL depgraph.nodes 表"。退役 MOD-INF-017 = 删 depgraph.nodes 节点 + 边。原 S4 只列 3 个 registry YAML，**漏 depgraph DB 重生成**。已补：删 .py 后跑 `extract_depgraph.py` / `sync_yaml_to_depgraph.py`。

**G3 — 测试规模严重低估（5 倍）**
grep 实测 **~70 个测试文件**引用 code_dedup（三次审查修正：原估 ~15 低估 5 倍；二次写 ~75 实测 70），跨 13+ 目录：tests/governance/code_dedup/、code_quality/、gov_code_dedup/、self_check/、llm_security/、automation/、canary/、contracts/、cross/、decision/、file/、path/、risk/。退役测试工程量 5 倍于原估，R4-R7 各批次须含对应测试目录清理。

**G4 — conftest.py 全局收集风险（三次审查已核实细节）**
`tests/conftest.py` **深度耦合** code_dedup（非简单 import）：L104-123 通过 `importlib` 把 `code_dedup_engine` 注入 `builtins`；L137-185 注册 `zephyr.testing.code_dedup` 包 + 子模块映射表 `_CODE_DEDUP_MODULE_MAP`（scanner/monoculture_guard 等映射到 `zephyr.gov_code_quality.code_dedup.*`）。这是**全局收集级耦合**——直接删 code_dedup 会让全仓库 pytest 收集失败。**退役前置**：先解耦 conftest（移除 importlib 注入 + 删 `_CODE_DEDUP_MODULE_MAP` + 清理 `zephyr.testing.code_dedup` 占位包），方可删 code_dedup。

> G5-G7（SOTA BFS / 特征化测试 / provenance+monoculture）经判定过度工程已剔除，理由见 §11.3。BRS 转移用最简 depgraph 查询（G1）。

### 10.2 2026-08-08 Web SOTA 检索结果

| 来源 | 核心发现 | 对本方案影响 |
|---|---|---|
| Vranković & Rakić 2026 (Programming'26 Companion) | LLM + 传统工具**互补**：传统擅 T1/T2 语法，LLM 擅 T3/T4 语义；集成优于单一 | ✅ 验证 CloneGuard 多引擎架构（echo-guard T1/T2 + 未来 LLM 仲裁） |
| 2026 奇点大会报告（CSDN） | LLM 生成码语义等价但语法变异时，**AST 哈希漏检率 68%**；推荐 CodeBERT+FAISS，阈值 0.82 | ⚠️ FILE-COPY 也是 AST 基同样漏——**裁定1 反被加强**（退役损失比预估更小）；echo-guard T2 嵌入才是 AI 码主力 |
| TriFusion-LLM (arXiv:2603.15004, 2026.03) | 多模态融合（启发式+AST+CodeBERT）+ **LLM 仲裁高不确定样本**（仅 0.2%，+0.3 Macro-F1），Macro-F1 0.695→0.875 | 🔵 CloneGuard FindingAggregator 已做多引擎表决；LLM 仲裁可作未来 T4 增强（非本次范围） |
| Fordel CI gates (2026.04) | "export registry"+Levenshtein+语义模糊匹配新导出（formatCurrency vs formatMoney）；5 gate <90s 拦 60% AI 问题 | ✅ 验证 L0 预防思路（CloneGuard MCP search_functions 已做）；预防>治愈 |
| Fallow (LogRocket 2026.07) | AST token 匹配 + File Health Score + MCP server；**"让 agent 重构只会加更多代码"** | ✅ 验证裁定3（auto-fix/agent-refactor 复合；L0 预防优先正确） |
| DeRep (securecodingpractices 2026.02) | 生成时自动剪枝重复块，重复降 80-90%，Pass@1 翻倍 | 🔵 反证：自动剪枝在生成期有效。但那是生成期非仓内修复；裁定3 仍成立，诚实记此反证 |
| LLM Clone Survey (arXiv:2308.01191 v3 2026) | LLM 擅 T3/T4，传统擅 T1/T2；CoT prompt + 向量嵌入有效 | ✅ 再证混合架构 |
| **HyClone (arXiv:2508.01357, 2025.08)** | 两阶段：LLM 初筛 + **执行验证**（LLM 生成测试输入，跨执行验证功能等价）；T4 语义克隆 precision/recall/F1 显著优于纯 LLM | 🔵 T4 增强路线：纯 LLM 判断不可靠，执行验证才可靠。属 CloneGuard 未来 T4 增强（§10.3），非本次范围 |
| **SourceTracker/HST (arXiv:2605.28510, 2026.06)** | 混合两阶段：向量搜索缩窄候选 + Winnowing 指纹重排序；300M 编码器，10M snippet，对数时间查询 | 🔵 L0 增强路线：MCP check_before_write/search_functions 可借鉴"向量召回+指纹精排"两段式，非本次范围 |
| **Code-Review-Graph (CallSphere 2026.04)** | 增量图（SHA-256 diff）+ bounded BFS + 风险评分，100% 召回，1000 文件 <5s | 🔵 信息参考（BFS 思路），本次不采纳（2 万函数用简单计数够，过度工程） |
| **Axiom Refract (2026)** | BFS 前向依赖枚举（深度 3-5 层）+ 受影响架构域；MCP 集成 `get_blast_radius` | 🔵 信息参考，本次不采纳（同上） |
| **AI monocultures (TechRadar 2026)** | 单一 AI 生成+审查=闭环盲区；需独立审查工具 | 🔵 信息记录；provenance/monoculture 维度已判定过度工程剔除 |
| **2026 AI 重构实践指南 (scien.cx / ten-builder)** | red-green-refactor loop；PR<200 行回归率降 60%；叶子模块先改；Strangler Fig 渐进迁移 | ✅ 验证 R1-R8 依赖反向序 |
| **GitClonify (2026 奇点开源版)** | LLM-aware token normalization，41ms 延迟，5.8% 误报（vs CodeCloneGuard 84ms/12.3%） | 🔵 L1 引擎替换候选（未来），非本次范围；echo-guard 当前够用 |
| **Model Merging 跨域克隆 (arXiv:2608.04215, 2026.08.04, ASE'26)** | TIES task-vector 合并构建跨域检测器，无需训练数据达多任务 93% F1；对未见 AI 克隆泛化比多任务训练好 4x | 🔵 信息记录；模型合并路线需训练 checkpoint，本项目无训练能力且多引擎已建成，不适用 |
| **Monoculture 语法 vs 语义 (arXiv:2607.13077, 2026.07.12)** | AI 码**语法同质化**显著（实现细节标准化），但**语义未同质化**（解题策略仍多样，甚至略扩展） | ✅ **反证剔除 provenance 正确**：monoculture 风险主要在语法层，CloneGuard T1/T2（AST哈希+嵌入）已在对抗语法 monoculture；语义层无需 monoculture 检测 |
| **LLM Ensemble Diversity (arXiv:2510.21513, 2026)** | 共识策略陷"popularity trap"放大常见错误；diversity-based 策略达 95% 潜力，2 模型即有效 | ✅ monoculture 缓解正解是"规格硬化"（项目已有 INVARIANTS/ERROR_CONTRACT 表头）+ 模型多样性，非 provenance；再证剔除正确 |

**结论**：2026 SOTA **验证主架构与 4 项裁定**（混合多引擎、L0 预防优先、SSoT 单源、auto-fix 退役），**整体架构层面未出现颠覆性更好算法**。组件级"更好算法"经审查多为过度工程（BFS/中心性、特征化测试、provenance），本次均不采纳——2 万函数规模下简单实现够用，符合 MVP 原则。下列 🔵 项保留为信息记录，无施工承诺，看未来需要再说。

AST 哈希在 AI 码场景 68% 漏检率这一发现，反使 FILE-COPY 退役损失比预估更小（FILE-COPY 同为 AST 基，漏同样的 AI 语义克隆）。

### 10.3 远期可选增强

见 §11.2（施工范围界定）。本次施工 = Phase 0 退役收敛唯一项，远期可选项无施工承诺。

---

## 11. 施工范围界定（剔除过度工程后）

> 三次审查裁定：本次施工 = Phase 0 退役收敛（§6）**唯一施工项**。原拟"Phase 1-4 一条龙"中的 provenance 基础设施 / BRS monoculture 维度 / SOTA BFS 升级 / 特征化测试补丁经判定为**过度工程，全部剔除**。

### 11.1 本次施工（唯一）

**Phase 0 退役收敛** = §6 全部内容。产出：CloneGuard 成唯一引擎，SSoT 干净，BRS 转移用最简 depgraph 查询（G1，基于 `get_edges_to_node` count 调用边）。

### 11.2 远期可选（无施工承诺，无依赖顺序，见 §10.3）

GitClonify 评估 / T4 HyClone / PDG 融合 / L0 SourceTracker / echo-guard 阈值校准——均保留为信息记录，看未来需要再说。

### 11.3 为何剔除 provenance / monoculture / BFS / 特征化测试

| 项 | 为何过度 | 依据 |
|---|---|---|
| provenance 出生证 | 为 monoculture 单功能建 5 维地基；trae 会话 ID 不稳定（分裂/续接/合并）；违背"先简单静态映射" | 用户裁定 + MVP 原则 |
| BRS monoculture 维度 | 依赖 provenance，provenance 剔除则随剔除；且 arXiv:2607.13077 证实 monoculture 主要在语法层，CloneGuard T1/T2 已覆盖 | 依赖项已删 + SOTA 反证 |
| SOTA BFS + 中心性 | 为大规模库设计，2 万函数用简单计数够 | G1 最简实现已足 |
| 特征化测试补丁 | 硬补"真损失"，AI 跑现有 pytest 即为验证 | 裁定 3 已承认真损失，不硬补 |

**原则**：退役是减法（删代码），不该夹带加法（建基础设施）。先把 5 套收敛成 1 套，干净后再看是否需要增强——届时在干净地基上做，出问题好定位。

---

## 附录 A：退役文件完整清单（64 .py + 关联文件）

**检测层**：ast_comparator.py, micro_clone_detector.py, signature_matcher.py, symbol_index.py, diff_detector.py, function_discovery.py, cross_boundary_detector.py, false_negative_auditor.py, self_scanner.py, code_analyzer_runner.py

**自检**：self_benchmark.py（在 intelligence_governance）

**auto-fix 管道**：auto_fixer.py, atomic_fixer.py, shadow_verifier.py, shadow_trust_validator.py, canary_manager.py, canary_register.py, behavioral_trust_checker.py, behavioral_sampler.py, shared_evolver.py, shared_lifecycle_manager.py, ssot_registrar.py, verifier.py, success_validator.py, pre_apply_integrity_gate.py, phase_executor.py, file_creator.py, extraction_safety.py, mock_duplicate_generator.py, code_simulator.py, recovery_manifest_writer.py, doom_loop_guard.py

**基础设施 + 审计器**：report.py, cli.py, config.py, cache_manager.py, grandfather_manager.py, risk_mitigator.py, debt_projector.py, decision_auditor.py, degradation.py, sensitivity_sweeper.py, thematic_clusterer.py, path_index_validator.py, contract_consistency_checker.py, dead_module_detector.py, stale_shared_detector.py, policy_tree_validator.py, observation_window_guard.py, integrations.py, integration_hub.py, prioritizer.py, annotations.py, exit_codes.py, health_monitor.py, monoculture_guard.py（BRS 已转移）, simplicity_auditor.py, fifteen_dimension_auditor.py, __init__.py, trackers/__init__.py, trackers/blind_spot_tracker.py, trackers/hotspot_tracker.py, trackers/risk_mitigation_tracker.py, trackers/consequence_tracker.py, trackers/question_tracker.py, trackers/import_surface_tracker.py

**关联退役**：function_dup_gate.py, file_copy_gate.py, check_code_duplication.py, verify_dedup.py, dedup_extractor.py + 各自测试

**BRS 转移目标**：src/zephyr/clone_guard/orchestrator.py（_build_refactoring_plan）
