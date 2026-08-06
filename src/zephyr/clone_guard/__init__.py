# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.1
# [MODULE] zephyr.clone_guard
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.orchestrator; zephyr.clone_guard.config; zephyr.clone_guard.engines.echo_guard_adapter
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.capability_overlap_gate
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] CloneGuard 是代码克隆检测集成防御体系的统一入口；MVP(Phase A)仅调度 Echo-Guard；升级 CAPABILITY-OVERLAP 门禁不新增门禁（守 I-GOV-3）；extract 级硬阻断=必须合并，review 级警告=尽量精简；reconciler 只 warn 不 commit（守 I-GOV-2）
# [MODIFY-GUARD] gate_id="CAPABILITY-OVERLAP"；blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] orchestrator.check() 永不抛异常——echo-guard 不可用时 degraded=True + passed=True（fail-loud warn 不阻断，守 warn-only 兜底契约）
# [TESTS] tests/clone_guard/test_orchestrator.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CloneGuard — 多引擎代码克隆检测集成防御体系（Phase A MVP）

治本 100% AI 开发场景下的"重复造轮子"病根。MVP 阶段仅集成 Echo-Guard，
通过升级现有 CAPABILITY-OVERLAP 门禁接入 GitCommitGateway 提交链路。

四层防御纵深（Phase A 仅 L0+L1）：
  L0 源头预防 — MCP check_before_write（Phase A 注册）
  L1 提交拦截 — pre-commit 硬阻断 extract 级克隆（Phase A 实现）
  L2 周期审计 — 全量语义扫描（Phase B）
  L3 跨边界审计 — 跨仓库/跨项目（Phase C）

Usage::

    from zephyr.clone_guard.orchestrator import CloneGuardOrchestrator
    result = CloneGuardOrchestrator(repo_root).check(staged_files)
    if not result.passed:
        print(f"CloneGuard 阻断: {result.findings}")
"""

from zephyr.clone_guard.orchestrator import CheckResult, CloneGuardOrchestrator, Finding

__all__ = ["CheckResult", "CloneGuardOrchestrator", "Finding"]
