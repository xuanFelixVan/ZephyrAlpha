# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.session_required_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] session_id 为空/保留词/未注册->阻断（强制 AI 调 session_worktree_start 注册）；allow_overlap=True 时放行（逃生通道，复用现有）；get_session 异常->安全降级放行（registry 故障不应卡死 commit 工作流）；保留词集合 = {"", "unknown", "none", "null"}（防 AI 传空串绕过）
# [MODIFY-GUARD] gate_id="SESSION-REQUIRED"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；保留词集合 _RESERVED_SESSION_IDS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——get_session 异常降级为放行（registry 故障不应卡死 commit 工作流）
# [TESTS] tests/governance/commit_gates/test_session_required_gate.py
# [A_module] module_id=MOD-GOV-session_required_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""session_required_gate.py — session 注册强制门禁（SESSION-REQUIRED，2026-07-01 治本 FP-ISO.4B 件1改）

检测 commit 调用方是否注册了有效 session。session_id 为空/"unknown"/未注册时
阻断（``SESSION_REQUIRED_VIOLATION``）——防止 AI 绕过 ``session_worktree_start``
直接调 ``commit()`` 导致 ``ClaimRequiredGate`` 因 session 未注册而安全降级放行。

病根（L4 元问题，蓝图 FP-ISO.3）
---------------------------------
``ClaimRequiredGate`` 在 session 未注册时放行（安全降级，为测试/内部调用设计）。
但 Trae IDE 多 AI 并发模式下，AI 们不自觉 ``session_worktree_start``，传
``session_id=""`` -> ``commit`` 方法第306行变成 ``"unknown"`` -> 未注册 ->
``ClaimRequiredGate`` 放行 -> claim 机制形同虚设 -> 编辑期覆盖无法在 commit 时拦截。

本 gate 在 session 未注册时**阻断**（而非放行），强制 AI 注册 session。
priority=30 优先于 CLAIM-REQUIRED(40) 和 HELD-OVERLAP(50)：先检查 session
注册，再检查 claim，最后检查 overlap。

与 ClaimRequiredGate 的关系
---------------------------
- ``ClaimRequiredGate``（priority=40）：session 已注册但文件未 claim -> 阻断
- ``SessionRequiredGate``（priority=30，本 gate）：session 未注册 -> 阻断
- 二者互补：本 gate 堵住"session 未注册->放行"缺口，ClaimRequiredGate 堵住
  "session 已注册但文件未 claim"缺口。allow_overlap=True 同时放行二者。

Usage::

    from zephyr.governance.commit_gates.session_required_gate import make_session_required_gate
    registry.register(make_session_required_gate())
"""

from __future__ import annotations

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec

__all__ = ["make_session_required_gate"]

# 保留 session_id 集合——这些值视为"未提供有效 session_id"
# commit 方法第306行将空串转为 "unknown"，此处一并拦截
_RESERVED_SESSION_IDS = frozenset({"", "unknown", "none", "null"})


def make_session_required_gate() -> GateSpec:
    """构造 session 注册强制门禁 GateSpec。

    Returns:
        GateSpec(gate_id="SESSION-REQUIRED", priority=30)。
        priority=30 优先于 CLAIM-REQUIRED(40)，先检查 session 注册再检查 claim。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        allow_overlap = kwargs.get("allow_overlap", False)
        if allow_overlap:
            # 逃生通道：显式声明放行（复用现有 allow_overlap，不新增参数）
            return True, ""

        session_id = kwargs.get("session_id", "")

        # 第一道：session_id 为空或保留词 -> 阻断
        if session_id in _RESERVED_SESSION_IDS:
            return False, (
                f"commit 必须提供有效 session_id（当前='{session_id}'，属保留词）。"
                f"AI 对话启动第一步：MUST 调 session_worktree_start() 注册 session。"
                f"逃生通道：commit(allow_overlap=True)。"
            )

        # 第二道：session_id 非空但未注册 -> 阻断
        try:
            info = gateway._registry.get_session(session_id)
        except Exception:
            # registry 读取异常 -> 安全降级放行
            # 理由：registry 故障不应卡死 commit 工作流（与 ClaimRequiredGate 一致）
            return True, ""

        if info is None:
            return False, (
                f"session '{session_id}' 未注册。"
                f"AI 对话启动第一步：MUST 调 session_worktree_start(session_id='{session_id}') 注册 session。"
                f"逃生通道：commit(allow_overlap=True)。"
            )

        return True, ""

    return GateSpec(gate_id="SESSION-REQUIRED", check=_check, priority=30)
