# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §l6_switch_engine
# [MODULE] zephyr.ai_layer.switch_engine.revert_drill
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.intelligence.switch_engine.switch_engine (SwitchEngine.revert_plan/EVENT_EDGES);
#                zephyr.intelligence.switch_engine.switch_registry (SwitchRegistryStore);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] L1 内监月度体检（慢周期挂点=接线批，本班只交付生成器）;
#             zephyr.ai_layer.switch_engine.tombstone_manager (tombstone 抽样来源)
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 安全带不演练=没有安全带：演练成功率判据=100%，任一检查失败即 incident_flag
#              立案（假安全带比没安全带更危险——884 死信积压 8 天同构教训）；dry-run 三查
#              零触生产（回切只走 revert_plan 纯函数，状态零变更）；round-robin 抽样确定
#              性（同月序同结果，注入 month_index）；月度抽 ≥1 champion（优先最近 promote）
#              +全部未满 TTL 的 tombstone 抽 1；回切指令单命令语义（S4 revert 可逆）；
#              计时用 monotonic（仅耗时测量），时间戳一律 now_utc
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md §②-F/§④-S7
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 三查失败不抛（记 passed=False+detail 继续查完，报告含全量失败项）；
#                  store 缺 switch_id→KeyError 上抛（演练对象必须真实在册）；
#                  out_dir 注入（测试 tmp_path），生产路径零写
# [TESTS] tests/ai_layer/switch_engine/test_revert_drill.py（round-robin 确定性+优先最近
#         promote/三查全绿报告/回切分支不可达时 incident_flag/tag 缺失 snapshot 查不过/
#         回执链断链检出/报告落盘含耗时/超窗 stale 检出）
# [TTL] permanent
"""revert_drill — 回切演练任务（S7 施工件）：round-robin 抽样+dry-run 三查+演练报告。

挂点=月度体检（L1 内监慢周期，接线批接入）。演练三查（DESIGN §②-F）：①回切指令
dry-run——revert_plan 可执行且状态机回滚分支正确；②champion 快照可重建——git tag/
worktree checkout 成功；③回执链完整——state_history 逐格有 since+evidence_ref 且末态
与当前态一致。报告含耗时与结果（验收锚），留档月度体检建议书，摘要回写 switch_registry
rollback.last_drill_date（由调用方经 store patch）。

# [ALGO_FLOW] external: docs/03_modules/_domain_ai_layer/algo_flow/revert_drill.yaml
"""

from __future__ import annotations

import json
import subprocess
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, Final

from zephyr.intelligence.switch_engine.switch_engine import (
    SwitchEngine,
    active_ref,
)
from zephyr.intelligence.switch_engine.switch_registry import (
    SwitchRegistryRecord,
    SwitchRegistryStore,
)
from zephyr.shared.infra.process_pool import run_subprocess_hidden
from zephyr.shared.utils.time_utils import now_utc

DRILL_CHECK_REVERT_PLAN: Final[str] = "revert_plan_executable"

# 各态既定回滚/恢复分支（事件, 目标态）——DESIGN §②-B 出边+§②-C 回切表；演练核对它。
EXPECTED_RECOVERY: Final[dict[str, tuple[str, str]]] = {
    "promoted": ("rollback_to_canary", "canary"),
    "canary": ("rollback_to_shadow", "shadow"),
    "champion": ("degrade_revive_predecessor", "shadow"),  # 劣化降级，前代走墓碑复检
    "retired": ("revive", "shadow"),
    "tombstone": ("revive", "shadow"),
}
DRILL_CHECK_SNAPSHOT: Final[str] = "champion_snapshot_rebuildable"
DRILL_CHECK_RECEIPT_CHAIN: Final[str] = "receipt_chain_complete"
STALE_MONTHLY_WINDOWS: Final[int] = 2  # last_drill_date 超 2 个月度窗未演练 → 内监告警
DAYS_PER_MONTH: Final[int] = 30


def _default_git_runner(args: Sequence[str]) -> str:
    completed = run_subprocess_hidden(  # trae_067 CREATE_NO_WINDOW（BARE-SUBPROCESS 治本 2026-09-24）
        ["git", *args], capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败：{completed.stderr.strip()}")
    return completed.stdout.strip()


def select_targets(
    champions: Sequence[SwitchRegistryRecord],
    tombstones: Sequence[SwitchRegistryRecord],
    *,
    month_index: int,
) -> dict[str, SwitchRegistryRecord | None]:
    """round-robin 抽样（确定性）：champion 优先最近 promote，tombstone 抽 1。"""

    def _promoted_at_desc(records: Sequence[SwitchRegistryRecord]) -> list[SwitchRegistryRecord]:
        return sorted(
            records,
            key=lambda r: str(r.promotion_record.get("promoted_at", "")),
            reverse=True,
        )

    ordered_champions = _promoted_at_desc(list(champions))
    ordered_tombstones = sorted(tombstones, key=lambda r: r.switch_id)
    return {
        "champion": (ordered_champions[month_index % len(ordered_champions)] if ordered_champions else None),
        "tombstone": (ordered_tombstones[month_index % len(ordered_tombstones)] if ordered_tombstones else None),
    }


def run_drill(
    store: SwitchRegistryStore,
    engine: SwitchEngine,
    switch_id: str,
    *,
    out_dir: Path,
    git_runner: Callable[[Sequence[str]], str] = _default_git_runner,
) -> dict[str, Any]:
    """对单个在役对象执行 dry-run 三查并落演练报告（JSON，含耗时与结果）。"""
    record = store.require(switch_id)
    started = time.monotonic()  # 仅耗时测量，非时间戳
    checks = [
        _check_revert_plan(engine, record),
        _check_snapshot(record, git_runner),
        _check_receipt_chain(record),
    ]
    elapsed_ms = int((time.monotonic() - started) * 1000)
    success = all(check["passed"] for check in checks)
    report: dict[str, Any] = {
        "switch_id": switch_id,
        "state": record.state,
        "active_ref": active_ref(record),
        "drill_date": now_utc().isoformat(),
        "checks": checks,
        "success": success,  # 判据=100%，任一失败即 False
        "incident_flag": not success,  # 任一失败=事故立案
        "elapsed_ms": elapsed_ms,
        "stale_alert": is_drill_stale(record),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"drill_{switch_id}_{report['drill_date'][:10]}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def is_drill_stale(record: SwitchRegistryRecord) -> bool:
    """rollback.last_drill_date 超 2 个月度窗未演练 → 告警（无记录=从未演练=恒告警）。"""
    last = record.rollback.get("last_drill_date")
    if not last:
        return True
    last_date = str(last)[:10]
    today = now_utc().isoformat()[:10]
    threshold = _shift_date(today, days=STALE_MONTHLY_WINDOWS * DAYS_PER_MONTH)
    return last_date < threshold


def _check_revert_plan(engine: SwitchEngine, record: SwitchRegistryRecord) -> dict[str, Any]:
    """①回切指令 dry-run：既定回滚分支可执行且目标态正确（纯函数，零状态变更）。"""
    expected = EXPECTED_RECOVERY.get(record.state)
    if expected is None:
        return {
            "name": DRILL_CHECK_REVERT_PLAN,
            "passed": False,
            "detail": f"态 {record.state} 无既定回滚分支（不在演练覆盖表）",
        }
    event, expected_to = expected
    targets = engine.legal_targets(record.state)
    actual_to = targets.get(event)
    passed = actual_to == expected_to
    detail = f"分支 {record.state} --{event}--> {actual_to}（预期 {expected_to}）"
    return {"name": DRILL_CHECK_REVERT_PLAN, "passed": passed, "detail": detail}


def _check_snapshot(record: SwitchRegistryRecord, git_runner: Callable[[Sequence[str]], str]) -> dict[str, Any]:
    """②champion 快照可重建：生效 ref（tag/分支）git 可解析。"""
    ref = active_ref(record)
    try:
        git_runner(["rev-parse", "--verify", ref])
        return {"name": DRILL_CHECK_SNAPSHOT, "passed": True, "detail": f"ref 可解析：{ref}"}
    except RuntimeError as exc:
        return {"name": DRILL_CHECK_SNAPSHOT, "passed": False, "detail": f"{exc}"}


def _check_receipt_chain(record: SwitchRegistryRecord) -> dict[str, Any]:
    """③回执链完整：state_history 逐格有 since+evidence_ref，末格=当前态。"""
    history = record.state_history
    problems: list[str] = []
    if not history:
        problems.append("state_history 为空")
    for index, entry in enumerate(history):
        if not entry.get("since") or not entry.get("evidence_ref"):
            problems.append(f"第 {index} 格缺 since/evidence_ref")
    if history and history[-1].get("state") != record.state:
        problems.append(f"末格 {history[-1].get('state')} != 当前态 {record.state}")
    return {
        "name": DRILL_CHECK_RECEIPT_CHAIN,
        "passed": not problems,
        "detail": "；".join(problems) or f"链长={len(history)} 完整",
    }


def _shift_date(today: str, *, days: int) -> str:
    from datetime import date, timedelta

    base = date.fromisoformat(today)
    return (base - timedelta(days=days)).isoformat()
