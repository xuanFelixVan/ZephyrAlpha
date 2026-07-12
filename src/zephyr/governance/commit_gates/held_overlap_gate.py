# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.held_overlap_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] allow_overlap=True 时直接放行（逃生通道）；other_held_files 读取异常安全降级为空集（不阻断 commit，registry 故障不应卡死工作流）；目标文件用 Path.resolve() 归一化与 other_held 比较（与 _normalize_file_path 对齐）
# [MODIFY-GUARD] gate_id="HELD-OVERLAP"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——registry 读取异常降级为空集（other_held=set()）
# [TESTS] tests/governance/commit_gates/test_held_overlap_gate.py
# [A_module] module_id=MOD-GOV-held_overlap_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""held_overlap_gate.py — 搭便车防护门禁（HELD-OVERLAP，2026-06-30 治本）

检测 commit 目标文件是否被其他**活跃** session 持有，命中则阻断
（``HELD_OVERLAP_VIOLATION``）。``allow_overlap=True`` 时放行（逃生通道），
由调用方在 commit message 追加 ``[GW:<sid>:overlap]`` 标记供审计追踪。

病根（L4 元问题）
-----------------
同文件多 session 修改是高风险反模式——GitCommitGateway 文件级隔离无法分离
同一文件内两个 session 的行级修改，后提交的 session 会把工作区内的全部修改
（含前一个 session 的 WIP）一并提交（"搭便车提交"/ghost commit）。

本 gate 在 **commit 时**（而非编辑时）阻断，不影响编辑自由。从源头避免优于
事后行级隔离（行级隔离前置依赖编辑器层行归属追踪，不可控）。

归一化一致性
-------------
``SessionRegistry.other_held_files`` 返回 ``_normalize_file_path`` 归一化的
绝对路径（``Path.resolve()``），本 gate 用 ``str(Path(f).resolve())`` 归一化
目标文件，与 ``_get_session_held_non_target`` 的比较方式一致。

Usage::

    from zephyr.governance.commit_gates.held_overlap_gate import make_held_overlap_gate

    registry.register(make_held_overlap_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, allow_overlap=False)
"""

from __future__ import annotations

from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

__all__ = ["make_held_overlap_gate"]


def make_held_overlap_gate() -> GateSpec:
    """构造搭便车防护门禁 GateSpec。

    Returns:
        GateSpec(gate_id="HELD-OVERLAP", priority=50)。
        priority=50 优先于大部分校验执行（搭便车是根因级问题，早阻断早省事）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        allow_overlap = kwargs.get("allow_overlap", False)
        if allow_overlap:
            # 逃生通道：显式声明放行，调用方负责追加 [GW:<sid>:overlap] 标记
            return True, ""

        session_id = kwargs.get("session_id", "")
        try:
            other_held = gateway._registry.other_held_files(session_id)
        except Exception:
            # registry 读取异常 -> 安全降级为空集（不阻断）
            # 理由：registry 故障不应卡死 commit 工作流；
            #       stash 隔离层（_get_session_held_non_target）同样降级为空集
            other_held = set()

        # 归一化目标文件（与 _normalize_file_path 的 Path.resolve() 对齐）
        target_abs = {str(Path(f).resolve()) for f in files}
        overlap = target_abs & other_held
        if overlap:
            overlap_rel = sorted(
                # 显示相对路径更易读（调试用）
                str(Path(f).relative_to(gateway.project_root))
                if Path(f).resolve().is_relative_to(gateway.project_root)
                else f
                for f in files
                if str(Path(f).resolve()) in overlap
            )
            return False, (
                f"目标文件被其他活跃 session 持有（搭便车防护 HELD_OVERLAP_VIOLATION）: "
                f"{overlap_rel}. 如确认需提交，用 commit(allow_overlap=True) 或 "
                f"CLI --allow-overlap 逃生通道。"
            )
        return True, ""

    return GateSpec(gate_id="HELD-OVERLAP", check=_check, priority=50)
