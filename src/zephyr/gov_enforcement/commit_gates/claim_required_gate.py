# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.claim_required_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] session未注册->放行（测试/内部调用安全降级）；session已注册但目标文件未claim->阻断；allow_overlap=True时放行（逃生通道）；get_session异常->安全降级放行
# [MODIFY-GUARD] gate_id="CLAIM-REQUIRED"；check闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check永不抛异常——get_session异常降级为放行（registry故障不应卡死commit工作流）
# [TESTS] tests/governance/commit_gates/test_claim_required_gate.py
# [A_module] module_id=MOD-GOV-claim_required_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""claim_required_gate.py — claim_files 前置检查门禁（CLAIM-REQUIRED，2026-06-30 治本）

检测 commit 目标文件是否已被当前 session claim。session 已注册但目标文件
未 claim 时阻断——防止 AI 直接调 ``commit()`` 绕过 ``claim_files`` 导致
``held_overlap_gate`` 因 ``other_held_files`` 空集而 no-op（红蓝对抗红攻1）。

设计权衡
--------
session 未注册 -> 放行（测试/内部调用不注册 session，安全降级）。
生产代码（``scripts/git_commit.py`` + ``task_repo.py`` DM-202918）均已 claim_files。
``_commit_auto``（reconciler 路径）不经过 gate registry，不受本 gate 影响。

priority=40 优先于 HELD-OVERLAP(50)：先检查 claim 再检查 overlap，
未 claim 时直接阻断，无需进入 overlap 检查。

Usage::

    from zephyr.gov_enforcement.commit_gates.claim_required_gate import make_claim_required_gate
    registry.register(make_claim_required_gate())
"""

from __future__ import annotations

from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

__all__ = ["make_claim_required_gate"]


def make_claim_required_gate() -> GateSpec:
    """构造 claim_files 前置检查门禁 GateSpec。

    Returns:
        GateSpec(gate_id="CLAIM-REQUIRED", priority=40)。
        priority=40 优先于 HELD-OVERLAP(50)，先检查 claim 再检查 overlap。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        allow_overlap = kwargs.get("allow_overlap", False)
        if allow_overlap:
            return True, ""  # 逃生通道放行

        session_id = kwargs.get("session_id", "")
        try:
            info = gateway._registry.get_session(session_id)
        except Exception:
            # registry 读取异常 -> 安全降级放行（registry 故障不应卡死 commit）
            return True, ""

        if info is None:
            # session 未注册 -> 可能是测试/内部调用，放行
            # 生产代码（CLI + task_repo）均注册 session + claim_files
            return True, ""

        # session 已注册 -> 检查目标文件是否被 claim
        # held_files 路径已由 claim_file 内部 _normalize_file_path 归一化（resolve()）
        held = {str(Path(f).resolve()) for f in info.held_files}
        target = {str(Path(f).resolve()) for f in files}
        unclaimed = target - held
        if unclaimed:
            return False, (
                f"session '{session_id}' 已注册但目标文件未 claim"
                f"（AGENTS.md §8 L284）: {sorted(unclaimed)}. "
                f"commit 前 MUST 调 claim_files 声明工作范围。"
            )
        return True, ""

    return GateSpec(gate_id="CLAIM-REQUIRED", check=_check, priority=40)
