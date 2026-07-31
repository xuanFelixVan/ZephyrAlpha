# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.reconciler_health_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.governance.audit.reconciliation_registry (_check_recent_blocks, _check_recent_critical_warns)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] dual-level——block_next 级别失败硬阻断 commit，critical_warn 级别失败打印警告不阻断；fail-open（governance.db 缺失/查询失败时放行）；复用 reconciliation_registry._check_recent_blocks/_check_recent_critical_warns（不复制 SQL，消除真源分裂）；always-on（reconciler 健康与本次 commit 文件无关，是项目整体状态检查）
# [MODIFY-GUARD] gate_id="RECONCILER-HEALTH"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] governance.db 缺失/查询异常 -> 放行(True, detail)；block_next 记录存在 -> 阻断(False, detail)；critical_warn 记录存在 -> 放行(True) + 打印 WARNING
# [TESTS] tests/governance/commit_gates/test_reconciler_health_gate.py
# [A_module] module_id=MOD-GOV-reconciler_health_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""reconciler_health_gate.py — reconciler 健康度门禁（#ARCH-DATAQUALITY-V1.7）

治本目标
--------
将 reconciler 健康检查从 ad-hoc banner（_print_block_banner/_print_critical_warn_banner
直接在 GitCommitGateway.commit 中调用）提升为正式 CommitGateRegistry gate。

问题（防御前移）
----------------
- session_worktree_commit 通过 _run_pre_commit_gates 调用 check_all()，运行所有注册 gate
- 但 _print_block_banner/_print_critical_warn_banner 是在 GitCommitGateway.commit 中直接
  调用的，不走 gate registry —— session_worktree_commit 路径不会触发 reconciler 健康检查
- 后果：session_worktree_commit 可以绕过 reconciler 健康检查（与 #ARCH-DEPGRAPH-RECONCILER-FAILSILENT
  Phase 4.2 的"block_next 硬阻断"设计意图冲突）

治本方案
--------
创建正式 gate 并注册到 CommitGateRegistry：
  1. 复用 _check_recent_blocks / _check_recent_critical_warns（不复制 SQL，消除真源分裂）
  2. block_next -> 硬阻断（与 _print_block_banner 语义一致）
  3. critical_warn -> 打印警告不阻断（与 _print_critical_warn_banner 语义一致）
  4. fail-open：governance.db 缺失/查询失败时放行（与现有 banner 一致）

设计权衡
--------
1. **复用而非复制**：import _check_recent_blocks/_check_recent_critical_warns，
   不复制 SQL 查询逻辑（消除多真源）。
2. **priority=64**：在 UNSAFE-DICT-SPREAD(65)/DEPGRAPH-FRESHNESS(67) 之前——先检查
   reconciler 整体健康度，再检查 depgraph 新鲜度（reconciler 故障比 depgraph 过期更紧急）。
3. **always-on**：reconciler 健康与本次 commit 文件无关，是项目整体状态检查。
4. **与现有 banner 共存**：_print_block_banner 仍在 GitCommitGateway.commit 中直接调用
   （向后兼容），本 gate 在 session_worktree_commit 路径补齐检查。两条路径都有
   block_next 检查，但这是有意的冗余（defense in depth）——gate 是统一入口，
   banner 是 GitCommitGateway 专用补充。

Usage::

    from zephyr.gov_enforcement.commit_gates.reconciler_health_gate import make_reconciler_health_gate
    registry.register(make_reconciler_health_gate())
"""

from __future__ import annotations

import logging

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.governance.audit.reconciliation_registry import (
    _check_recent_blocks,
    _check_recent_critical_warns,
)
check_recent_critical_warns = _check_recent_critical_warns  # public alias（Stage 4 公共化）

check_recent_blocks = _check_recent_blocks  # public alias（Stage 4 公共化）


logger = logging.getLogger(__name__)

__all__ = ["make_reconciler_health_gate"]


def make_reconciler_health_gate() -> GateSpec:
    """构造 reconciler 健康度门禁 GateSpec（dual-level，阻断型）。

    Returns:
        GateSpec(gate_id="RECONCILER-HEALTH", priority=64)。
        priority=64——在 UNSAFE-DICT-SPREAD(65)/DEPGRAPH-FRESHNESS(67) 之前
        （reconciler 故障比 depgraph 过期更紧急，先检查整体 reconciler 健康）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root = gateway.project_root

        # 1. 检查 block_next 级别失败——硬阻断
        # 治本（2026-08-01）：用 public alias（check_recent_blocks）而非私有引用
        # （_check_recent_blocks），使 monkeypatch 能拦截——public alias 设计初衷即为
        # 测试可注入（Stage 4 公共化）。原代码用私有引用绕过了 alias，导致测试无法 mock。
        try:
            blocks = check_recent_blocks(project_root)
        except Exception as e:  # noqa: BLE001 — fail-open: 查询异常不阻断
            logger.warning("RECONCILER-HEALTH: block_next query failed: %s", e)
            blocks = []

        if blocks:
            detail_lines = [
                f"RECONCILER-HEALTH: {len(blocks)} blocking reconciler failure(s) in last 24h:"
            ]
            for b in blocks[:5]:
                detail_lines.append(f"  - [{b['logged_at']}] {b['gate_id']}: {b['detail']}")
            if len(blocks) > 5:
                detail_lines.append(f"  ... and {len(blocks) - 5} more (query governance.db)")
            detail_lines.append(
                "  Action: fix failures then run resolve_blocks() to clear. "
                "Escape: commit(allow_overlap=True)."
            )
            detail = "\n".join(detail_lines)
            logger.error("RECONCILER-HEALTH gate block:\n%s", detail)
            return False, detail

        # 2. 检查 critical_warn 级别失败——打印警告不阻断
        try:
            warns = check_recent_critical_warns(project_root)
        except Exception as e:  # noqa: BLE001 — fail-open: 查询异常不阻断
            logger.warning("RECONCILER-HEALTH: critical_warn query failed: %s", e)
            warns = []

        if warns:
            warn_lines = [
                f"RECONCILER-HEALTH WARN: {len(warns)} critical reconciler failure(s) in last 24h:"
            ]
            for w in warns[:5]:
                warn_lines.append(f"  - [{w['logged_at']}] {w['gate_id']}: {w['detail']}")
            if len(warns) > 5:
                warn_lines.append(f"  ... and {len(warns) - 5} more (query governance.db)")
            warn_lines.append("  Investigate before proceeding (non-blocking warning).")
            warn_detail = "\n".join(warn_lines)
            logger.warning(warn_detail)
            # 保留 print：gate 告警需直接出现在操作员控制台（commit UX），不依赖 logging 配置
            print(f"[GATE RECONCILER-HEALTH] {warn_detail}")
            return True, warn_detail

        return True, "reconciler health OK (0 block_next, 0 critical_warn in last 24h)"

    return GateSpec(gate_id="RECONCILER-HEALTH", check=_check, priority=64)