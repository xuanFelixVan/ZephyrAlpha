# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.worktree_required_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__ (via auto_register_gates)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] worktree 内放行 / solo session 放行 / 并发非 worktree 阻断；reconciler worker session（worker-* 前缀）排除出活跃 session 计数（#ARCH-RECONCILER-WORKTREE-RACE 治本）；allow_overlap=True 或 allow_non_worktree=True 时放行（双逃生通道）；get_current_worktree/list_active 异常->安全降级放行（基础设施故障不应卡死 commit）
# [MODIFY-GUARD] gate_id="WORKTREE-REQUIRED"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；priority=44
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——get_current_worktree/list_active 异常降级为放行（基础设施故障不应卡死 commit 工作流）
# [TESTS] tests/governance/commit_gates/test_worktree_required_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""worktree_required_gate.py — worktree 隔离强制门禁（WORKTREE-REQUIRED，#ARCH-WORKTREE-GATE-001 治本 2026-08-04）

治本"君子协定在 100% AI 场景下系统性失效"——``warn_non_worktree_commit`` 只 WARN
不阻断，AI 把 WARN 当"通过"。本 gate 将并发非 worktree commit 从 WARN 升级为
fail-closed 阻断。

分级阻断逻辑
-------------
1. **worktree 内** → 放行（物理隔离生效，无搭便车风险）
2. **非 worktree + 无其他活跃 session** → 放行（solo session，向后兼容）
3. **非 worktree + 有其他活跃 user session** → 阻断（``WORKTREE_VIOLATION``，
   共享工作区 commit 可能搭便车带入其他 session WIP）

   reconciler worker session（``worker-{sha8}-{pid}`` 前缀）排除出"其他活跃 session"
   计数——worker 是 commit 下游产物（held_files 空、无搭便车风险），
   #ARCH-RECONCILER-WORKTREE-RACE 治本（2026-08-09）

双逃生通道
-----------
- ``allow_overlap=True``（通用，reconciler auto-commit 复用）
- ``allow_non_worktree=True``（专用，语义清晰，CLI 对称 ``--allow-non-worktree``）

fail-open 安全降级
-------------------
``get_current_worktree()`` / ``list_active()`` 异常 → 放行。理由：基础设施故障
不应卡死 commit 工作流（对标 SESSION-REQUIRED / HELD-OVERLAP 的 fail-open 设计）。

与 warn_non_worktree_commit 的关系
-----------------------------------
- ``warn_non_worktree_commit``（L499）：WARN-only 日志，保留向后兼容（记录非 worktree commit 事件）
- ``WORKTREE-REQUIRED`` gate（本 gate，priority=44）：fail-closed 阻断，治本
- 二者互补：warn 记录事件，gate 执行阻断

Usage::

    from zephyr.gov_enforcement.commit_gates.worktree_required_gate import make_worktree_required_gate
    registry.register(make_worktree_required_gate())
"""

from __future__ import annotations

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

__all__ = ["make_worktree_required_gate"]


def make_worktree_required_gate() -> GateSpec:
    """构造 worktree 隔离强制门禁 GateSpec。

    Returns:
        GateSpec(gate_id="WORKTREE-REQUIRED", priority=44)。
        priority=44 在 CLAIM-REQUIRED(40) 之后、HELD-OVERLAP(50) 之前执行。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 逃生通道1：allow_overlap（通用，reconciler auto-commit 复用）
        if kwargs.get("allow_overlap", False):
            return True, ""

        # 逃生通道2：allow_non_worktree（专用，语义清晰）
        if kwargs.get("allow_non_worktree", False):
            return True, ""

        session_id = kwargs.get("session_id", "")

        # 检测当前是否在 worktree 内
        try:
            wt_session = gateway._get_worktree_manager().get_current_worktree()
        except Exception:  # noqa: BLE001 — worktree 检测异常 -> 安全降级放行
            return True, ""

        if wt_session is not None:
            # 在 worktree 内，物理隔离生效
            return True, ""

        # 非 worktree——检测是否有其他活跃 session
        # #ARCH-RECONCILER-WORKTREE-RACE 治本（2026-08-09）：
        # 排除 reconciler worker session（worker-{sha8}-{pid} 命名约定，与
        # reconcile_runner._count_active_workers 同源）。worker 是 commit 的下游产物——
        # post-commit auto-committer，held_files 为空、变更经 gateway 串行提交，无搭便车
        # 风险。原逻辑把 worker 计入"其他活跃 session"导致每条非-worktree commit 必触发
        # WORKTREE_VIOLATION，--allow-non-worktree 逃生通道被常态化（审计噪音 + 治理稀释）。
        try:
            other_active = [
                s
                for s in gateway.registry.list_active()
                if s.session_id != session_id and not s.session_id.startswith("worker-")
            ]
        except Exception:  # noqa: BLE001 — list_active 异常 -> 安全降级放行
            other_active = []

        if not other_active:
            # solo session，无并发风险，向后兼容放行
            return True, ""

        # 并发非 worktree commit → 阻断（fail-closed）
        other_ids = [s.session_id for s in other_active]
        return False, (
            f"非 worktree commit 且存在其他活跃 session（{other_ids}），"
            f"共享工作区 commit 可能搭便车带入其他 session WIP。"
            f"治本：使用 session_worktree_start() 创建物理隔离 worktree。"
            f"逃生通道：commit(allow_non_worktree=True) 或 CLI --allow-non-worktree。"
        )

    return GateSpec(gate_id="WORKTREE-REQUIRED", check=_check, priority=44)
