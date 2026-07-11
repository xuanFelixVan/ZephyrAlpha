# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.foreign_change_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] allow_overlap=True 时直接放行（逃生通道，与 HELD-OVERLAP 对齐）；无基线快照时 PASS（reconciler auto-commit 等未走 claim_files 的路径不阻断）；基线为空时 PASS（claim 时文件干净，所有变更都是本 session 的）；基线非空时 BLOCK（claim 时文件已有外来变更）；_claim_snapshots 读取异常安全降级为无快照（不阻断 commit）
# [MODIFY-GUARD] gate_id="FOREIGN-CHANGE-DETECTION"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——_claim_snapshots 读取异常降级为无快照（passed=True）
# [TESTS] tests/governance/commit_gates/test_foreign_change_gate.py
# [A_module] module_id=MOD-GOV-foreign_change_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-054]
"""foreign_change_gate.py — 外来变更检测门禁（FOREIGN-CHANGE-DETECTION，ARCH-054 治本）

检测 commit 目标文件在 claim_files 时刻是否已有外来变更（其他 session 的 WIP）。
命中则阻断（``FOREIGN_CHANGE_VIOLATION``）。``allow_overlap=True`` 时放行（逃生通道），
由调用方在 commit message 追加 ``[GW:<sid>:overlap]`` 标记供审计追踪。

病根（ARCH-054 / L4 元问题）
-----------------------------
GitCommitGateway 的 pathspec commit（``--pathspec-from-file``）将 commit 范围限制到
文件级，无法区分同一文件内不同 session 的行级变更。当 session B commit 文件 X 时，
``git add`` 会把工作区对 X 的全部修改暂存——包括 session A 在同一文件 X 上的 WIP
（"搭便车提交"/ghost commit）。

HELD-OVERLAP gate 只检测目标文件是否被其他**活跃** session **claim** 持有，不检测
未 claim 的编辑（session A 编辑了 X 但未 claim 时，HELD-OVERLAP 不会阻断 B）。

本 gate 在 ``claim_files`` 时快照 ``git diff HEAD -- <file>`` 基线，commit 时检测
文件是否在 claim 时就已是脏状态。从内容层面（而非 claim 注册表层面）捕获外来变更。

检测逻辑
---------
- 无基线快照（reconciler auto-commit 等未走 claim_files 的路径）→ PASS
- 基线为空（claim 时文件干净，所有变更都是本 session 的）→ PASS
- 基线非空（claim 时文件已有外来变更）→ BLOCK，逃生通道 ``allow_overlap=True``

设计理由：claim 时基线非空意味着文件在 session 声明持有前已有未提交修改——这些
修改不属于本 session（否则应在编辑前 claim）。阻断迫使调用方显式用逃生通道确认，
或调整工作流在编辑前 claim。

归一化一致性
-------------
``_claim_snapshots`` 的 key 是 ``os.path.abspath(file)``（与 claim_files 归一化
方式一致）。本 gate 用 ``os.path.abspath(f)`` 归一化目标文件进行查表。

Usage::

    from zephyr.governance.commit_gates.foreign_change_gate import make_foreign_change_gate

    registry.register(make_foreign_change_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, allow_overlap=False)
"""

from __future__ import annotations

import os

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec

__all__ = ["make_foreign_change_gate"]


def make_foreign_change_gate() -> GateSpec:
    """构造外来变更检测门禁 GateSpec。

    Returns:
        GateSpec(gate_id="FOREIGN-CHANGE-DETECTION", priority=45)。
        priority=45 在 CLAIM-REQUIRED(40) 之后、HELD-OVERLAP(50) 之前执行
        ——claim 建立后立即检测基线，早于 held-overlap 的注册表层检测。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        allow_overlap = kwargs.get("allow_overlap", False)
        if allow_overlap:
            # 逃生通道：显式声明放行，调用方负责追加 [GW:<sid>:overlap] 标记
            return True, ""

        session_id = kwargs.get("session_id", "")
        if not session_id:
            # 无 session_id（未知调用方）→ 不阻断，CLAIM-REQUIRED 会处理
            return True, ""

        # 读取本 session 的 claim 快照（异常安全降级为空 dict）
        try:
            snapshots = gateway._claim_snapshots.get(session_id, {})
        except Exception:
            # _claim_snapshots 读取异常 -> 安全降级为无快照（不阻断）
            # 理由：快照基础设施故障不应卡死 commit 工作流
            snapshots = {}

        # 检测每个目标文件的基线
        dirty_files: list[str] = []
        for f in files:
            abs_f = os.path.abspath(f)
            if abs_f not in snapshots:
                # 无基线快照（未走 claim_files 的路径，如 reconciler auto-commit）→ PASS
                continue
            baseline = snapshots[abs_f]
            if baseline:
                # 基线非空——claim 时文件已有外来变更
                dirty_files.append(abs_f)

        if dirty_files:
            # 显示相对路径更易读（调试用）
            try:
                dirty_rel = sorted(
                    os.path.relpath(f, str(gateway.project_root))
                    for f in dirty_files
                )
            except Exception:
                dirty_rel = dirty_files
            return False, (
                f"目标文件在 claim 时已有外来变更（FOREIGN_CHANGE_VIOLATION）: "
                f"{dirty_rel}. 这些变更不属于本 session，commit 会将其搭便车提交。"
                f"如确认需提交，用 commit(allow_overlap=True) 或 CLI --allow-overlap "
                f"逃生通道。"
            )
        return True, ""

    return GateSpec(gate_id="FOREIGN-CHANGE-DETECTION", check=_check, priority=45)
