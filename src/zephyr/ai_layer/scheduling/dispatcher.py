# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] zephyr.ai_layer.scheduling.dispatcher
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT——E0 闸按路径装载);
#                scripts.backtest.compute_window_gate (FAC-E0 拉式闸门，importlib 按路径装载，
#                exam_trigger_scheduler 同款先例——零改造调用);
#                zephyr.ai_layer.scheduling.scheduling_events (审批事件账——骨架单拍板落账)
# [CONSUMERS] zephyr.ai_layer.scheduling.order_daemon（order_dispatch_due 派工段）;
#             前端 schedulegate 页（排产队列投影，只读）;
#             api_server /api/schedulegate-confirm（骨架单拍板写路由，C9 落点批文 2026-09-27）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 进化量尺两问打分=纯函数（score = labor_segments × advantage_bucket × demote，
#              DESIGN §2.5，全枚举可测）；防饥饿=pending 龄 >7 天一次性 +1.0 bump（policy 常量）；
#              带星胜 ×0.5 且排同分队尾；repair 工单不与进化比 score（专人专事独立队列，共享配额池）；
#              问闸=纯拉式（每段开工瞬间调一次 check_gate，exit 3=拒→deferred，不轮询不 sleep-loop，
#              资源恢复事件唤醒重评）；配额四读数全部注入（Q1 会话/Q2 子代理/Q3 token/Q4 提交带宽，
#              不建新计量系统）；降级梯度表全留痕（终点禁自我扩容=定调 #10）；T1 派工前置双预检
#              （老组不动 champion claim 预检 HELD-OVERLAP 不硬闯 + KillSwitch 探针）；
#              同一工单连续 3 次 defer→堵点本 CRITICAL（对标 belt _ENV_ABORT_ESCALATE=3）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md §2.5/§2.6（规则真源；
#                阈值改动走 OBJ_R，AI 层不持尺）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] E0 闸不可装载→ComputeGateUnavailable（fail-closed 拒派工）；naive datetime 拒收；
#                  四读数注入缺席→ValueError（不猜余量）；打分输入缺 significance→small 桶保守处理
#                  （不虚构精度）
# [TESTS] tests/ai_layer/scheduling/test_dispatcher.py（两问打分全枚举：labor 计数封顶/分桶三档/
#         缺失保守/带星降权/防饥饿 bump/排序 FIFO 稳定/repair 不混队/四读数超限判定/降级梯度/
#         拉式问闸 exit3→deferred/双预检 hold；gate 函数注入零网络零定时器）
"""dispatcher — L5 排产调度器（D-L5-06/07）：两问打分 + 防饥饿 + 四读数 + E0 拉式问闸 + 双预检。
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/dispatcher.yaml

排序=score 降序→FIFO；repair 工单独立队列不参排；骨架级提案同打分但仅用于确认页展示排序，
不占自动派工队列。超限降级梯度（§2.6，终点禁自我扩容）::

    Q1 满  → 工单转 deferred（门闸保持关），会话释放事件唤醒重评回 pending
    Q2 超  → 降单代理模式；确需多代理→拆单或 defer+堵点本
    Q3 超  → model_tier 降档 strong→flash（仅限施工段；验收 reviewer 恒 strong）；仍超→deferred
    Q4 积压 → 暂停新派工（在途照常），belt drain 事件唤醒
    GPU 档冲突 → 验收段改排下一 heavy_ok 窗，exclusive_group 排队留痕
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Final, Mapping, Sequence

from zephyr.ai_layer.scheduling.scheduling_events import (
    KIND_ORDER_CONFIRMED_DUE,
    SchedulingJournal,
)
from zephyr.shared.io.paths import REPO_ROOT

__all__: Final = [
    "ComputeGateUnavailable",
    "count_labor_segments",
    "advantage_bucket",
    "work_order_score",
    "rank_pending",
    "skeleton_decisions",
    "apply_skeleton_decisions",
    "confirm_skeleton",
    "evaluate_quota",
    "degrade",
    "champion_overlap_precheck",
    "ask_compute_gate",
    "QuotaReadings",
]

_E0_GATE_RELPATH: Final[tuple[str, ...]] = ("scripts", "backtest", "compute_window_gate.py")
_E0_MODULE_CACHE: Final[dict[str, Any]] = {}
REVIEWER_TIER_INVARIANT: Final = "strong"  # 验收 reviewer 恒 strong（不可降档）

_SEGMENTS_SPLIT_CHARS: Final = (";", "；", "、", "，", ",", "\n", "|")
_BUCKET_SCORES: Final[dict[str, float]] = {"large": 2.0, "medium": 1.5, "small": 1.0}


class ComputeGateUnavailable(Exception):
    """E0 算力闸不可装载/判定异常（fail-closed 拒派工，exam_trigger_scheduler 同款语义）。

    :param details: 敏感上下文（路径等）走 details 不进消息文本（5.99.20）。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


# ── 两问打分（DESIGN §2.5，纯函数全枚举）────────────────────────────────────
def count_labor_segments(labor_killed: str, max_segments: int = 4) -> int:
    """两问①消灭人工段数：labor_killed 结构化拆段计数（1-4 封顶；空串=1 段保守下限）。"""
    text = str(labor_killed or "").strip()
    if not text:
        return 1
    count = 1
    for ch in _SEGMENTS_SPLIT_CHARS:
        text = text.replace(ch, ";")
    count = max(count, len([seg for seg in text.split(";") if seg.strip()]))
    return max(1, min(count, max_segments))


def advantage_bucket(significance: float | str | None, policy: Mapping[str, Any]) -> str:
    """两问②对比优势幅度分桶（large/medium/small）；缺失或非数值→small（保守，不虚构精度）。"""
    lines = policy["priority"]["advantage_bucket_lines"]
    try:
        value = float(significance)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "small"
    if value >= float(lines["large_min"]):
        return "large"
    if value >= float(lines["medium_min"]):
        return "medium"
    return "small"


def work_order_score(
    labor_killed: str,
    significance: float | str | None,
    starred: bool,
    policy: Mapping[str, Any],
    pending_age_days: float = 0.0,
) -> dict[str, Any]:
    """纯函数：score = labor_segments × advantage_bucket × demote（+防饥饿 bump）。

    :param pending_age_days: pending 龄（天）；> starvation_age_days 一次性 +starvation_bump
    """
    prio = policy["priority"]
    segments = count_labor_segments(labor_killed, int(prio["labor_segments_max"]))
    bucket = advantage_bucket(significance, policy)
    base = segments * _BUCKET_SCORES[bucket] * (float(prio["starred_demote_factor"]) if starred else 1.0)
    bump = float(prio["starvation_bump"]) if pending_age_days > float(prio["starvation_age_days"]) else 0.0
    return {
        "score": round(base + bump, 4),
        "base": round(base, 4),
        "bump": bump,
        "labor_segments": segments,
        "advantage_bucket": bucket,
        "starred": bool(starred),
    }


def rank_pending(
    orders: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any],
    now: datetime,
) -> list[dict[str, Any]]:
    """纯函数：pending 进化工单排序（score 降序→FIFO；带星同分排队尾；repair/骨架级不混入）。

    :param now: tz-aware 当前时刻（pending 龄与 FIFO 基准；调用方注入）
    """
    if now.tzinfo is None:
        raise ValueError("naive datetime 拒收（RULE-SCHEMA-TZ）")
    scored: list[dict[str, Any]] = []
    for order in orders:
        if str(order.get("kind") or "evolution") == "repair":
            continue  # repair 独立队列（专人专事），不与进化比 score
        if order.get("owner_gate") and order.get("gate_decision") != "confirm":
            continue  # 骨架级提案未经 Owner confirm 不占自动派工队列（confirm 后入队；reject/未拍板不混入）
        created = order.get("created_at")
        age_days = 0.0
        if isinstance(created, datetime):
            if created.tzinfo is None:
                raise ValueError("naive datetime 拒收（RULE-SCHEMA-TZ）")
            age_days = (now - created).total_seconds() / 86400.0
        s = work_order_score(
            str(order.get("labor_killed") or ""),
            order.get("significance"),
            bool(order.get("starred")),
            policy,
            age_days,
        )
        scored.append({"order_id": order["order_id"], "fifo_seq": len(scored), **s})
    scored.sort(key=lambda r: (-r["score"], r["starred"], r["fifo_seq"]))
    return scored


# ── 骨架单拍板（C9 确认态判定落点=审批事件账，Owner 2026-09-27 批文）─────────────
def skeleton_decisions(journal: SchedulingJournal) -> dict[str, dict[str, Any]]:
    """事件账→{order_id: 最新拍板回执}（append-only 账，同单多笔取最新=改判留痕保序）。"""
    out: dict[str, dict[str, Any]] = {}
    for ev in journal.pending():
        if ev.kind != KIND_ORDER_CONFIRMED_DUE:
            continue
        oid = str((ev.payload or {}).get("order_id") or "")
        if oid:
            out[oid] = {
                "decision": (ev.payload or {}).get("decision"),
                "decided_at": ev.recorded_at,
                "decided_by": (ev.payload or {}).get("decided_by"),
                "event_id": ev.id,
            }
    return out


def apply_skeleton_decisions(
    orders: Sequence[Mapping[str, Any]],
    decisions: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """拍板投影合并（纯函数）：骨架单贴 state/confirm_receipt（schedulegate 页契约字段）；
    普通单原样透传。seeds 登记真源零改写——确认态只落审批事件账，读侧投影合并。"""
    merged: list[dict[str, Any]] = []
    for order in orders:
        row = dict(order)
        if row.get("owner_gate"):
            rec = decisions.get(str(row.get("order_id") or ""))
            if rec is not None:
                row["state"] = "dispatched" if rec.get("decision") == "confirm" else "dead"
                row["confirm_receipt"] = {
                    "decision": rec.get("decision"),
                    "decided_at": rec.get("decided_at"),
                    "receipt": rec.get("event_id"),
                }
            else:
                row["state"] = "pending"  # 未拍板骨架单：页据此渲染 Owner 拍板按钮
        merged.append(row)
    return merged


def confirm_skeleton(
    order_id: str,
    decision: str,
    *,
    journal: SchedulingJournal,
    seeds_path: Path | str | None = None,
    decided_by: str = "",
) -> dict[str, Any]:
    """Owner 骨架单拍板落账：confirm=工单转派工队列；reject=工单作废归档。

    落账=SchedulingJournal 追加 ``order_confirmed_due``（append-only 审批事件账，改判留痕
    不删不覆）；seeds 登记真源零改写。幂等：同单二次拍板=already_decided 拒绝（回执持久）。
    """
    from zephyr.ai_layer.scheduling.seed_writer import load_seeds

    if decision not in ("confirm", "reject"):
        raise ValueError(f"decision 非法: {decision!r}（只认 confirm|reject）")
    doc = load_seeds(seeds_path)
    entry = next(
        (o for o in (doc.get("orders") or doc.get("seeds") or []) if str(o.get("order_id") or "") == str(order_id)),
        None,
    )
    if entry is None:
        return {"ok": False, "reason": "order_not_found", "order_id": str(order_id)}
    if not entry.get("owner_gate"):
        return {"ok": False, "reason": "not_owner_gate", "order_id": str(order_id)}
    prior = skeleton_decisions(journal).get(str(order_id))
    if prior is not None:
        return {
            "ok": False,
            "reason": "already_decided",
            "order_id": str(order_id),
            "gate_decision": prior.get("decision"),
            "gate_decided_at": prior.get("decided_at"),
        }
    event = journal.emit(
        KIND_ORDER_CONFIRMED_DUE,
        {
            "order_id": str(order_id),
            "decision": decision,
            "decided_by": str(decided_by or "unknown"),
        },
    )
    return {
        "ok": True,
        "order_id": str(order_id),
        "decision": decision,
        "decided_by": str(decided_by or "unknown"),
        "decided_at": event.recorded_at,
        "event_id": event.id,
        "effect": ("工单转派工队列（confirm）" if decision == "confirm" else "工单作废归档（reject，墓碑语义留账）"),
    }


# ── 配额四读数（DESIGN §2.6；读数注入，不建新计量系统）──────────────────────
@dataclass(frozen=True)
class QuotaReadings:
    """四资源当值读数（Q1 会话/Q2 该单子代理/Q3 当日 token/Q4 提交队列深度）。"""

    q1_active_sessions: int
    q2_subagents_requested: int
    q3_tokens_today: int
    q4_commit_queue_pending: int


def evaluate_quota(readings: QuotaReadings, policy: Mapping[str, Any]) -> list[str]:
    """纯函数：四读数 vs 上限 → 超限码清单（空=全绿）。"""
    quota = policy["quota"]
    exceeded: list[str] = []
    if readings.q1_active_sessions >= int(quota["q1_active_session_cap"]):
        exceeded.append("Q1")
    if readings.q2_subagents_requested > int(quota["q2_subagent_max"]):
        exceeded.append("Q2")
    if readings.q3_tokens_today >= int(quota["q3_daily_token_budget"]):
        exceeded.append("Q3")
    if readings.q4_commit_queue_pending >= int(quota["q4_commit_queue_pending_cap"]):
        exceeded.append("Q4")
    return exceeded


def degrade(order: Mapping[str, Any], exceeded: Sequence[str], policy: Mapping[str, Any]) -> dict[str, Any]:
    """纯函数：超限降级梯度（§2.6 表逐行；动作全留痕，终点禁自我扩容）。

    :return: {order_id, actions: [...], state, model_tier, defer_count, critical}
    """
    quota = policy["quota"]
    actions: list[dict[str, Any]] = []
    state = str(order.get("state") or "pending")
    tier = str((order.get("contractor") or {}).get("model_tier") or "strong")
    defer_count = int(order.get("defer_count") or 0)
    for code in exceeded:
        if code == "Q1":
            state = "deferred"
            defer_count += 1
            actions.append({"code": "Q1", "action": "deferred", "detail": "并发槽满，会话释放事件唤醒重评"})
        elif code == "Q2":
            actions.append(
                {"code": "Q2", "action": "single_agent_demote", "detail": "降单代理模式；确需多代理→拆单或 defer"}
            )
            state = "deferred"
            defer_count += 1
        elif code == "Q3":
            if tier == REVIEWER_TIER_INVARIANT and str(order.get("segment") or "build") != "build":
                actions.append(
                    {"code": "Q3", "action": "no_demote_acceptance", "detail": "验收 reviewer 恒 strong 不降档"}
                )
                state = "deferred"
                defer_count += 1
            else:
                tier = str(quota["q3_demote_tier_to"])
                actions.append({"code": "Q3", "action": "tier_demote", "detail": f"施工段降档→{tier}"})
        elif code == "Q4":
            actions.append(
                {
                    "code": "Q4",
                    "action": "pause_dispatch",
                    "detail": "提交带宽积压，暂停新派工（在途照常），belt drain 唤醒",
                }
            )
        elif code == "GPU":
            actions.append(
                {
                    "code": "GPU",
                    "action": "reschedule_heavy_ok",
                    "detail": "exclusive_group 排队留痕，验收段改排下一 heavy_ok 窗",
                }
            )
            state = "deferred"
            defer_count += 1
    critical = defer_count >= int(quota["defer_critical_streak"])
    return {
        "order_id": order.get("order_id"),
        "actions": actions,
        "state": state,
        "model_tier": tier,
        "defer_count": defer_count,
        "critical": critical,
    }


# ── T1 派工前置双预检（DESIGN §2.6）─────────────────────────────────────────
def champion_overlap_precheck(
    champion_files: Sequence[str],
    active_claims: Sequence[str],
    active_sessions: Sequence[str] = (),
) -> tuple[bool, list[str]]:
    """纯函数：老组不动预检——champion 文件清单有活跃 claim/在途会话=hold（不硬闯）。"""
    claims = set(active_claims)
    hits = sorted(set(champion_files) & claims)
    if hits:
        return False, [f"HELD-OVERLAP:champion 文件活跃 claim:{','.join(hits[:3])}"]
    if active_sessions:
        return False, [f"HELD-OVERLAP:champion 域在途会话:{','.join(sorted(active_sessions)[:3])}"]
    return True, []


def _load_e0_module() -> object:
    """按路径装载 FAC-E0 闸模块（单例缓存；不可装载→ComputeGateUnavailable fail-closed）。"""
    path = str(Path(REPO_ROOT).joinpath(*_E0_GATE_RELPATH))
    cached = _E0_MODULE_CACHE.get(path)
    if cached is not None:
        return cached
    try:
        spec = importlib.util.spec_from_file_location("e0_compute_window_gate", path)
        if spec is None or spec.loader is None:
            raise ImportError("spec_load_failed")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001——装载失败统一转 fail-closed 异常
        raise ComputeGateUnavailable(f"e0_gate_unreachable:{type(exc).__name__}", details={"path": path}) from exc
    _E0_MODULE_CACHE[path] = module
    return module


def ask_compute_gate(
    order_id: str,
    compute_class: str,
    gate_fn: Callable[..., Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """拉式问闸（每段开工瞬间一次）：exit 3=拒→deferred 语义；不轮询不 sleep-loop。

    :param gate_fn: 注入 check_gate（测试用）；缺省按路径装载 E0 既有函数（零改造调用）
    :return: {"allowed": bool, "reason_code": str}——reason_code 原样透传 E0 四理由码
    """
    if gate_fn is None:
        module = _load_e0_module()
        gate_fn = module.check_gate
    try:
        decision = dict(gate_fn(purpose=f"evolution_{order_id}", node_compute_class=compute_class))
    except Exception as exc:  # noqa: BLE001
        # 闸判定异常=基础设施失败，fail-closed 拒
        return {"allowed": False, "reason_code": f"gate_error:{type(exc).__name__}"}
    return {
        "allowed": bool(decision.get("allowed")),
        "reason_code": str(decision.get("reason_code") or "gate_unknown"),
    }
