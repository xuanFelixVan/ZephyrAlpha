---
ttl: task_bound
title: F103 代码质量与克隆守卫——挖干案卷
session: zc-l10-20260927
updated: 2026-09-29
---

# F103 · 代码质量与克隆守卫（code_dedup+extract 级克隆无逃生）

> 总册行（00_全环节总册.md:178）：built｜上游 F98｜下游 施工｜P2｜G7
> 第一证据源：fullflow_mining/m3_governance/03_registry_families.md（own_scope/FUNCTION-DUP 约束引用）＋src/zephyr/gov_code_quality/code_dedup/＋src/zephyr/clone_guard/

## 一、六向台账（实证锚点）

| 向 | 实测证据（本日复核） |
|---|---|
| 上游输入 | 提交面 diff（extract 级克隆预查 clone_guard.check_before_write，宪法补充铁律）＋代码库 AST 面（code_dedup 自扫描） |
| 下游消费 | 施工环节（写前预查/合理重复 resolve_finding 标 acknowledged）；F98 门禁（FUNCTION-DUP 约束在 commit 链的引用，M3 01 §3.5：worktree_pool.py:115-116 注明同源 GIT-BUDGET-INV-003） |
| 自动化触发 | 提交链预查调用（check_before_write）；self_scanner/canary 自维护面；无独立常驻 |
| 真源与注册表 | src/zephyr/gov_code_quality/code_dedup/（**本日 ls ≈55 .py**）＋src/zephyr/clone_guard/（orchestrator/engines/rules/aggregator/mcp_server/strategy_fingerprint/config，本日 ls 实证）；宪法铁律=extract 级克隆无逃生 |
| 门禁与质量尺 | 克隆判级 engines/（extract 级最高无逃生）＋rules/＋aggregator.py 汇裁＋mcp_server.py（AI 可查询口）＋strategy_fingerprint.py（策略指纹去重） |
| 当前运行状态 | built（LEDGER_final [06:3x]：CloneGuard 21 对 acknowledged 在案；tests/clone_guard 16 件+tests/gov_code_dedup 7 件） |

## 二、子模块三级枚举（code_dedup 族谱按职责收敛，本日 ls）

1. **检测器族**：ast_comparator.py｜diff_detector.py｜micro_clone_detector.py｜cross_boundary_detector.py｜signature_matcher.py｜symbol_index.py｜function_discovery.py｜thematic_clusterer.py｜dead_module_detector.py｜stale_shared_detector.py｜code_simulator.py｜behavioral_sampler.py。
2. **裁决与信任**：behavioral_trust_checker.py｜shadow_trust_validator.py/shadow_verifier.py/verifier.py｜false_negative_auditor.py｜fifteen_dimension_auditor.py｜sensitivity_sweeper.py｜monoculture_guard.py｜doom_loop_guard.py｜observation_window_guard.py。
3. **修复与执行**：auto_fixer.py/atomic_fixer.py｜extraction_safety.py｜file_creator.py｜phase_executor.py｜prioritizer.py｜risk_mitigator.py｜degradation.py｜exit_codes.py｜recovery_manifest_writer.py。
4. **治理与登记**：grandfather_manager.py（既存豁免）｜ssot_registrar.py｜canary_manager.py/canary_register.py｜policy_tree_validator.py｜pre_apply_integrity_gate.py｜contract_consistency_checker.py｜path_index_validator.py｜decision_auditor.py｜debt_projector.py｜success_validator.py｜health_monitor.py｜self_scanner.py｜cache_manager.py｜config.py｜cli.py｜report.py｜integration_hub.py/integrations.py｜shared_evolver.py/shared_lifecycle_manager.py｜simplicity_auditor.py｜mock_duplicate_generator.py｜code_analyzer_runner.py｜annotations.py｜trackers/。
5. **clone_guard 包（独立于 code_dedup）**：orchestrator.py（check_before_write 编排）＋engines/＋rules/＋aggregator.py＋mcp_server.py＋strategy_fingerprint.py＋config.py＋__init__.py。

## 三、接线四态独立复核

- 总册判 **built**：成立——双包实存（code_dedup 55 件+clone_guard 8 件）、宪法铁律有执法编排（orchestrator+rules 分级）、既存豁免有登记面（grandfather_manager+LEDGER 21 对 acknowledged 留痕）、AI 查询口（mcp_server）在产。
- 两包关系：code_dedup（库内重复治理+自愈）与 clone_guard（写前预查守卫）是上下游分工非重复（w5_1 跨域不同对象不并）；但**包间无册面互指**，易被误判合并候选——登记建议（不改码）。
- 测试覆盖：clone_guard 16 件/55 件 code_dedup 仅 7 件——code_dedup 测试密度显著低于 clone_guard，高风险件（auto_fixer/extraction_safety）覆盖存疑，进缺口。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| G1 | code_dedup 测试密度低（7 件 vs 55 模块） | auto_fixer/extraction_safety/atomic_fixer 三件先配对 | P1 |
| G2 | code_dedup↔clone_guard 分工无册面 | ROOR/两包 __init__ 文档串互指（生成器化登记） | P2 |
| G3 | acknowledged 豁免（21 对）无复核节拍 | 季度退役审计窗复核 acknowledged 存续性（宪法 §4 对齐） | P2 |
| G4 | extract 级"无逃生"的负向红证（尝试绕过必被拦）无专测 | bypass_recorder 思路平移补红证 | P2 |

## 五、自审闸三态

**双包结构与执法编排=挖干可施工**（ls/wc 实证+宪法铁律对应件全命中）；**测试密度缺口=待施工**；**acknowledged 复核节拍=挂起**（等季度审计窗）。

## 六、复跑命令

```bash
ls src/zephyr/gov_code_quality/code_dedup/*.py | wc -l   # ≈55
ls src/zephyr/clone_guard/                               # 8 件
find tests/clone_guard tests/gov_code_dedup -name "test_*.py" | wc -l  # 23（16+7）
grep -rn "check_before_write" src/zephyr/clone_guard/__init__.py | head -3  # 宪法铁律入口
```

## 七、刷新批注（2026-09-29 st-finaldel-fresha）

### 9/28 后变更核查
- 双包本体（src/zephyr/clone_guard/、src/zephyr/gov_code_quality/code_dedup/）与配套（lock_files.py／session_worktree.py）**9/28 后零 commit**——结构判定与缺口 G1-G4 全部维持。
- 邻面波及（登记面）：`98ce6370c5`（六簇撞号修复）与 `81d85b9a77`（墓碑治本）均在 commit_gates/gate_registry 面，与本卷无直接码面交集；FUNCTION-DUP 约束引用位（worktree_pool.py）未见改动。
- 宪法 RULE-CLONEGUARD 写前预查入口（check_before_write）在 HEAD 未变，§六复跑命令全部有效。

### 自审闸三态
- **挖干可施工（维持，零翻面）**——本卷属 M6 审计波 2 轻刷新档（段级登记面噪音级 STALE），无实体变化需修订。
