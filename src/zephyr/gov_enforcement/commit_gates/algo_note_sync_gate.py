# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.algo_note_sync_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.trading.decision_map; zephyr.shared.utils.time_utils; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway（经 in_process_gate_registry.yaml 自动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——commit 触碰某节点 module_ref 指向的 .py 时，该节点 algo_note_zh 必须同 commit 修订或加 note_confirmed 日期，否则阻断（Owner 2026-09-09："算法改了大白话必须跟着改"）；module_ref=null 红节点豁免；地图缺失/解析失败/git 异常 fail-open（passed=True）；节点大白话被修订时其带 payload_zh 的出边落 .runtime/gate_audit/algo_note_payload_review.jsonl 复审提醒（warning 级不阻断）
# [MODIFY-GUARD] gate_id="ALGO-NOTE-SYNC"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——任何基础设施异常降级 fail-open（passed=True, logger.warning）；检出违规 fail-closed（passed=False）
# [TESTS] tests/governance/commit_gates/test_algo_note_sync_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""algo_note_sync_gate.py — 算法锚与大白话同步绑定门禁（ALGO-NOTE-SYNC，Owner 2026-09-09 任务三）

病根（第一性原理）
-----------------
地图节点的算法说明有两态真源：algo_refs（算法库锚）/module_ref（代码锚）。
但"大白话怎么算"（algo_note_zh）与代码实现之间无强制同步——代码改了阈值/逻辑，
地图上的大白话静默腐烂，下一个 AI 和 Owner 读到的是过期机制 = 幻觉/漂移温床
（正是 Owner 原话："算法改了大白话必须跟着改"）。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 取本 commit 触碰的 .py 文件集合
  2. 加载地图，找出 module_ref 命中触碰文件的节点（module_ref=null 红节点豁免）
  3. 无命中 → 直接放行
  4. 解析地图 YAML 的 staged diff，按 node_id 归因变更块
  5. 命中节点须满足之一，否则硬阻断：
     a) 同 commit 内该节点块的 algo_note_zh 行被修订
     b) 同 commit 内该节点块新增/更新 note_confirmed: <日期>（显式确认口径未变）
  6. algo_note_zh 被修订的节点，其带 payload_zh 的出边落复审提醒审计（warning 不阻断）

设计权衡
--------
1. diff 块归因按"最近出现的 node_id"粗粒度归属——足够判定"动了谁的块"，不做行级精确。
2. fail-open 只用于基础设施故障（地图缺失/git 异常）；diff 干净且节点受影响=真违规，阻断。
3. priority=76：ARCH-REFERENCE(75) 之后、CAPABILITY-OVERLAP(200) 之前——必须在暂存集冻结后运行。

Usage::

    from zephyr.gov_enforcement.commit_gates.algo_note_sync_gate import make_algo_note_sync_gate

    registry.register(make_algo_note_sync_gate())  # 经 in_process_gate_registry.yaml 自动注册
"""

from __future__ import annotations

import json
import logging
import re
from datetime import timezone
from pathlib import Path
from typing import Any

from zephyr.shared.utils.time_utils import now_utc
from zephyr.trading.decision_map import load_decision_map

logger = logging.getLogger(__name__)

_MAP_REL = "config/trading_decision_map.yaml"
_AUDIT_REL = ".runtime/gate_audit/algo_note_payload_review.jsonl"
_NOTE_KEYS = ("algo_note_zh", "note_confirmed")
_NODE_ID_RE = re.compile(r"node_id:\s*(\S+)")


def _norm_posix(f: str | Path, repo_root: Path) -> str:
    """文件路径归一为相对 repo 的 posix 串（兼容绝对/相对/反斜杠混合）。"""
    p = Path(f)
    try:
        p = p.relative_to(repo_root)
    except ValueError:
        pass
    return p.as_posix()


def _collect_node_block_changes(diff_text: str) -> dict[str, set[str]]:
    """从地图 YAML 的 unified diff 提取 {node_id: 变更过的键集合}。

    归因规则：按 diff 行序跟踪最近出现的 node_id（+/-/上下文行都更新归属），
    变更行（+/−前缀、非文件头）计入当前 node 名下。粗粒度但足以判定
    "该节点的块在同 commit 内被动过、动的是不是 algo_note_zh/note_confirmed"。
    """
    changed: dict[str, set[str]] = {}
    current = ""
    for line in diff_text.splitlines():
        if line.startswith(("diff ", "index ", "@@", "+++ ", "--- ")):
            continue
        body = line[1:] if line[:1] in ("+", "-") else line
        m = _NODE_ID_RE.search(body)
        if m:
            current = m.group(1)
        if line[:1] in ("+", "-") and current:
            for key in _NOTE_KEYS:
                if key + ":" in body:
                    changed.setdefault(current, set()).add(key)
            if "node_id:" in body:
                changed.setdefault(current, set()).add("node_id")
    return changed


def _edges_needing_review(dm: Any, note_changed_ids: list[str]) -> list[dict[str, str]]:
    """大白话被修订的节点 → 其带 payload_zh 的出边清单（复审提醒载体）。"""
    changed = set(note_changed_ids)
    out: list[dict[str, str]] = []
    for e in getattr(dm, "edges", ()):
        if e.from_node in changed and e.payload_zh:
            out.append({"edge": f"{e.from_node}->{e.to_node}", "payload_zh": e.payload_zh})
    return out


def check_algo_note_sync(
    files: list[str] | None,
    map_path: str | Path,
    diff_text: str | None,
) -> tuple[bool, str, list[dict[str, str]]]:
    """纯逻辑核心（可单测，不触 git）。

    Returns:
        (blocked, message, payload_review_edges)
    """
    changed_code = {_norm_posix(f, Path(map_path).parents[1]) for f in (files or []) if str(f).endswith(".py")}
    if not changed_code:
        return False, "", []
    dm = load_decision_map(Path(map_path))
    affected = [n for n in dm.nodes if n.module_ref and Path(str(n.module_ref)).as_posix() in changed_code]
    if not affected:
        return False, "", []

    block_changes = _collect_node_block_changes(diff_text or "")
    failures: list[str] = []
    note_changed: list[str] = []
    for n in affected:
        keys = block_changes.get(n.node_id, set())
        if keys & set(_NOTE_KEYS):
            note_changed.append(n.node_id)
            continue
        failures.append(
            f"{n.node_id}（module_ref={n.module_ref}）——实现代码被触碰，"
            f"algo_note_zh 未同 commit 修订（改写该节点 algo_note_zh，或加 note_confirmed: {now_utc().date().isoformat()}）"
        )

    if failures:
        msg = (
            f"ALGO-NOTE-SYNC：{len(failures)} 个节点的实现代码在本 commit 被触碰，"
            f"但其大白话算法说明未同步——算法改了大白话必须跟着改（Owner 2026-09-09）。"
            + "；".join(failures)
        )
        return True, msg, []

    return False, "", _edges_needing_review(dm, note_changed)


def _write_review_audit(project_root: Path, review: list[dict[str, str]]) -> None:
    """payload_zh 复审提醒落审计（warning 级，失败不抛）。"""
    try:
        p = project_root / _AUDIT_REL
        p.parent.mkdir(parents=True, exist_ok=True)
        record = {"ts": now_utc().isoformat(), "needs_review": review}
        with p.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计失败不影响 gate 结果
        logger.debug("algo note payload review audit write failed", exc_info=True)


def make_algo_note_sync_gate() -> Any:
    """构造算法-大白话同步绑定 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="ALGO-NOTE-SYNC", priority=76)。
        priority=76——紧跟 ARCH-REFERENCE(75) 之后、CAPABILITY-OVERLAP(200) 之前。
    """
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

    def _check(gateway: Any, files: list[str] | None, **kwargs: Any) -> tuple[bool, str]:
        try:
            project_root = Path(str(gateway.project_root))
            map_path = project_root / _MAP_REL
            if not map_path.exists():
                logger.warning("ALGO-NOTE-SYNC: 地图真源缺失，fail-open 放行")
                return True, ""
            diff_res = gateway.run_git(["git", "diff", "--cached", "--", _MAP_REL])
            diff_text = diff_res.stdout if getattr(diff_res, "returncode", 1) == 0 else ""
            blocked, msg, review = check_algo_note_sync(files, map_path, diff_text)
            if review:
                _write_review_audit(project_root, review)
                logger.warning(
                    "ALGO-NOTE-SYNC: %d 条出边 payload_zh 因节点大白话修订需复审（已落 %s）",
                    len(review),
                    _AUDIT_REL,
                )
            return (not blocked), msg
        except Exception as exc:  # noqa: BLE001 — 基础设施故障 fail-open
            logger.warning("ALGO-NOTE-SYNC fail-open: %s", exc)
            return True, ""

    return GateSpec(gate_id="ALGO-NOTE-SYNC", check=_check, priority=76)
