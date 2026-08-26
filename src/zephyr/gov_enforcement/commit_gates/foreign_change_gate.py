# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.foreign_change_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] allow_overlap=True 时直接放行（逃生通道，与 HELD-OVERLAP 对齐）；无基线快照时 PASS（reconciler auto-commit 等未走 claim_files 的路径不阻断）；基线为空时 PASS（claim 时文件干净，所有变更都是本 session 的）；基线非空时 BLOCK（claim 时文件已有外来变更）；_claim_snapshots 读取异常安全降级为无快照（不阻断 commit）；P1 post-claim 修改审计 warn-only（在 block 决策前运行，捕获 claim 后到 commit 前的文件变化记录到 .runtime/gate_audit/post_claim_modifications.jsonl，审计失败不阻断 commit）
# [MODIFY-GUARD] gate_id="FOREIGN-CHANGE-DETECTION"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——_claim_snapshots 读取异常降级为无快照（passed=True）
# [TESTS] tests/governance/commit_gates/test_foreign_change_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

时序缺口审计（P1，13a5e1d512 治本补强）
-----------------------------------------
FOREIGN-CHANGE gate 只检查 **claim 时刻** 的基线快照，不检测 **claim 后到 commit 前**
文件是否被修改。时序缺口：session claim 文件（基线干净）→ 后台 auto-sync 进程/其他
session 修改同一文件 → session commit 时 gate 看到干净基线直接 PASS，但实际 commit
内容已混入 post-claim 外来修改。

本 gate 在 commit 时（block 决策前）追加 **post-claim 修改审计**（warn-only）：
捕获当前 diff 与 claim 基线对比，差异记录到
``.runtime/gate_audit/post_claim_modifications.jsonl`` 供事后取证。

噪音过滤（避免每个正常 commit 都记审计）：
- 基线空 + 非 adopted + 当前有 diff → 正常自编辑（session claim 干净文件后自己编辑），跳过
- 基线非空 + 当前≠基线 → 可疑（claim 时已脏且继续变），记录
- adopted（基线被 adopt_prior_work 故意清空但实际脏）+ 当前有 diff → 可疑，记录
- 当前==基线 → 无 post-claim 变化，跳过

设计理由：claim 时基线非空意味着文件在 session 声明持有前已有未提交修改——这些
修改不属于本 session（否则应在编辑前 claim）。阻断迫使调用方显式用逃生通道确认，
或调整工作流在编辑前 claim。

归一化一致性
-------------
``_claim_snapshots`` 的 key 是 ``os.path.abspath(file)``（与 claim_files 归一化
方式一致）。本 gate 用 ``os.path.abspath(f)`` 归一化目标文件进行查表。

Usage::

    from zephyr.gov_enforcement.commit_gates.foreign_change_gate import make_foreign_change_gate

    registry.register(make_foreign_change_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, allow_overlap=False)
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_foreign_change_gate"]

# post-claim 修改审计日志路径（与 allow_overlap_usage.jsonl 同目录）
_POST_CLAIM_AUDIT_REL = ".runtime/gate_audit/post_claim_modifications.jsonl"


def _load_adopted_files(gateway, session_id: str) -> set[str]:
    """加载 session 的 adopted 文件集合（adopt_prior_work 认领的文件）。

    adopt_prior_work=True 时，claim_files 将实际脏文件的基线**故意清空**（让
    FOREIGN-CHANGE gate 放行），但真实基线记录到
    ``{claim_snapshots_dir}/{sid}_adopted.jsonl``。本函数读取该日志提取被认领
    的文件绝对路径集合，供 post-claim 审计识别 adopted 场景。

    Args:
        gateway: GitCommitGateway 实例（提供 claim_snapshots_dir）。
        session_id: session 标识。

    Returns:
        被认领文件的绝对路径集合；日志不存在/读取异常时返回空集（fail-open）。
    """
    adopted: set[str] = set()
    try:
        adopted_file = gateway.claim_snapshots_dir / f"{session_id}_adopted.jsonl"
        if not adopted_file.is_file():
            return adopted
        for line in adopted_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                f = rec.get("file", "")
                if f:
                    adopted.add(os.path.abspath(f))
            except (json.JSONDecodeError, TypeError):
                continue
    except Exception:  # noqa: BLE001 — fail-open
        pass
    return adopted


def _audit_post_claim_modifications(gateway, session_id: str, files: list[str], snapshots: dict[str, str]) -> None:
    """P1：审计 claim 后到 commit 前的文件修改（时序缺口可见性，warn-only）。

    FOREIGN-CHANGE gate 只检查 claim 时刻基线，不检测 claim 后的修改。本函数在
    commit 时捕获当前 diff 与 claim 基线对比，差异记录到审计日志供事后取证。

    不影响 gate pass/block 决策——审计写入失败不阻断 commit（fail-open）。

    噪音过滤：跳过正常自编辑（空基线+非adopted+当前有diff），仅记录可疑场景
    （基线非空+变化 / adopted+变化）。

    Args:
        gateway: GitCommitGateway 实例（提供 capture_baseline_diff / project_root）。
        session_id: session 标识。
        files: 待 commit 文件绝对路径列表。
        snapshots: {abs_file: baseline_diff} 字典（claim 时刻基线）。
    """
    try:
        adopted_files = _load_adopted_files(gateway, session_id)
        audit_path = Path(str(gateway.project_root)) / _POST_CLAIM_AUDIT_REL
        audit_path.parent.mkdir(parents=True, exist_ok=True)

        records: list[dict] = []
        for f in files:
            abs_f = os.path.abspath(f)
            if abs_f not in snapshots:
                continue
            baseline = snapshots[abs_f]
            try:
                current = gateway.capture_baseline_diff(abs_f)
            except Exception:  # noqa: BLE001 — fail-open
                continue

            # 防御：capture_baseline_diff 应返回 str，mock/异常场景可能返回非 str → 跳过
            if not isinstance(current, str):
                continue

            if current == baseline:
                continue  # 无 post-claim 变化

            is_adopted = abs_f in adopted_files
            # 噪音过滤：正常自编辑（干净 claim → session 自己编辑 → commit）跳过
            if not baseline and not is_adopted and current:
                continue

            try:
                rel = os.path.relpath(abs_f, str(gateway.project_root))
            except (ValueError, AttributeError):
                rel = abs_f

            records.append(
                {
                    "timestamp": time.time(),  # noqa: m46-time — 审计事件时间戳（Unix 秒格式）
                    "session_id": session_id,
                    "file": rel.replace("\\", "/"),
                    "baseline_size": len(baseline),
                    "current_size": len(current),
                    "adopted": is_adopted,
                    "post_claim_change": True,
                }
            )

        if records:
            from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl

            for r in records:
                append_audit_jsonl(audit_path.parent, audit_path.name, r)
    except Exception:  # noqa: BLE001 — 审计写入失败不阻断 commit
        logger.debug(
            "FOREIGN-CHANGE: post-claim audit write failed (non-blocking)",
            exc_info=True,
        )


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
            snapshots = gateway.claim_snapshots.get(session_id, {})
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            # _claim_snapshots 读取异常 -> 安全降级为无快照（不阻断）
            # 理由：快照基础设施故障不应卡死 commit 工作流
            snapshots = {}

        # P1（13a5e1d512 治本补强）：post-claim 修改审计（warn-only）
        # 在 block 决策前运行——即使 gate 阻断也记录 post-claim 变化供事后取证。
        # 时序缺口：gate 只检查 claim 时刻基线，不检测 claim 后到 commit 前的修改。
        # 本审计捕获当前 diff 与基线的差异，记录可疑场景到审计日志。
        _audit_post_claim_modifications(gateway, session_id, files, snapshots)

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
                dirty_rel = sorted(os.path.relpath(f, str(gateway.project_root)) for f in dirty_files)
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                dirty_rel = dirty_files
            return False, (
                f"目标文件在 claim 时已有外来变更（FOREIGN_CHANGE_VIOLATION）: "
                f"{dirty_rel}. 这些变更不属于本 session，commit 会将其搭便车提交。"
                f"如确认需提交，用 commit(allow_overlap=True) 或 CLI --allow-overlap "
                f"逃生通道。"
            )
        return True, ""

    return GateSpec(gate_id="FOREIGN-CHANGE-DETECTION", check=_check, priority=45)
