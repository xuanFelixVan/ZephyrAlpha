# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] zephyr.ai_layer.scheduling.scheduling_events
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.intake.intake_events (probe_kill_switch 复用，零复制);
#                zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.ai_layer.scheduling.order_daemon (SchedulingJournal 注入);
#             L6 切换（work_order_shadow_ready 消费方，L6 卡实施时经 register_handler 挂消费体）;
#             L7 传承（work_order_closed_due 消费方，设计预留）;
#             L2 候选卡（work_order_dead→rejected 回传，L2 稿 R2 补入边）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 事件触发零定时器（禁 cron/Timer/sleep-loop，宪法 §9.3——胜者到达/资源恢复是仅有的
#              触发沿）；journal 先落盘再消费（.runtime/ai_scheduling/pending_events.jsonl 唯一真源，
#              镜像 .runtime/ai_intake / .runtime/ai_compare 先例）；八个 kind 全为轻 kind；
#              kind 白名单+必填 payload 键校验 fail-closed，未知 kind 拒 emit（绝不落半截事件）；
#              KillSwitch 探针复用 intake_events.probe_kill_switch（fail-closed：探测失败=停消费全保留）；
#              毒丸 MAX_ATTEMPTS=3 留档不自动消费（人工处置后 purge）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md §2.1/§3（事件契约真源，
#                L4/L6/L7 载荷字段已锁，变更走跨稿契约流程）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] emit 未知 kind / 缺必填键→ValueError；journal 读写 OSError→上抛（不静默丢事件）；
#                  handler 抛错→事件保留+attempts+1+last_error 留痕，本轮 drain 到此为止（重试跨唤醒）；
#                  KillSwitch 不可达→stop_reason=kill_switch_probe_error 且零消费
# [TESTS] tests/ai_layer/scheduling/test_events.py（8 kind 白名单+必填键/journal 先落盘/drain 幂等/
#         毒丸 MAX_ATTEMPTS/KillSwitch 探针停消费/未知 handler 拒挂）
# [TTL] permanent
"""scheduling_events — L5 排产段事件层：八轻 kind 的 JSONL journal（emit / status / drain）。

★ 文件名沿 L2/L4 先例用 ``scheduling_events.py`` 而非设计稿 C3 所写 ``events.py``：能力册
``drift_detection_events`` 的 alias 是裸词 ``events``，任何新 ``events.py`` 都会被 CREATE-GUARD
的 basename 碰撞判成 sibling duplicate 而硬阻断（L2 intake_events 施工期实测死信在案，L4
compare_events 同款改名先例）。件内语义与 DESIGN C3 完全一致。

八个 kind（红蓝 R3 补全 3 项、R4 计数校正 8；全轻，零定时器）::

    evolution_winner_due     L4/L2 → L5：胜者落库（库内=INTAKE_E2_HANDOFF 链；库外=verdict='win' 直达）
    order_created_due        L5 内部：工单已生成落 pending
    order_confirmed_due      Owner → L5：骨架级提案拍板（confirm/reject）
    order_dispatch_due       L5 → 施工队：派工指令（Q1-Q4 配额+E0 双预检过后）
    order_deferred_due       L5 内部：配额不足/算力窗关闭→deferred 补态（红蓝 R1-B10）
    work_order_shadow_ready  L5 → L6：关单四闸全过+worktree 就绪的影子上岗券（勿与 closed_due 混称）
    work_order_closed_due    L5 → L7：终局关单回执（传承段收判据档案）
    work_order_dead          L5 → L2：死单回执 {order_id, reason}→候选卡跳 rejected（红蓝 R2 补回传）
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Final, Mapping

from zephyr.ai_layer.intake.intake_events import probe_kill_switch
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "SCHEDULING_KINDS",
    "SchedulingEvent",
    "SchedulingJournal",
    "PAYLOAD_REQUIRED_KEYS",
    "KIND_EVOLUTION_WINNER_DUE",
    "KIND_ORDER_CREATED_DUE",
    "KIND_ORDER_CONFIRMED_DUE",
    "KIND_ORDER_DISPATCH_DUE",
    "KIND_ORDER_DEFERRED_DUE",
    "KIND_WORK_ORDER_SHADOW_READY",
    "KIND_WORK_ORDER_CLOSED_DUE",
    "KIND_WORK_ORDER_DEAD",
]

MAX_ATTEMPTS: Final = 3
DEFAULT_STATE_DIR: Final = REPO_ROOT / ".runtime" / "ai_scheduling"
JOURNAL_NAME: Final = "pending_events.jsonl"
RECEIPT_NAME: Final = "last_receipt.json"
EVENT_ID_PREFIX: Final = "SCHED"

KIND_EVOLUTION_WINNER_DUE: Final = "evolution_winner_due"
KIND_ORDER_CREATED_DUE: Final = "order_created_due"
KIND_ORDER_CONFIRMED_DUE: Final = "order_confirmed_due"
KIND_ORDER_DISPATCH_DUE: Final = "order_dispatch_due"
KIND_ORDER_DEFERRED_DUE: Final = "order_deferred_due"
KIND_WORK_ORDER_SHADOW_READY: Final = "work_order_shadow_ready"
KIND_WORK_ORDER_CLOSED_DUE: Final = "work_order_closed_due"
KIND_WORK_ORDER_DEAD: Final = "work_order_dead"

# L6 关单契约载荷（DESIGN §3 已锁，本层只承载不改造）：criteria_yaml_ref+hash 两键分开
PAYLOAD_REQUIRED_KEYS: Final[dict[str, tuple[str, ...]]] = {
    KIND_EVOLUTION_WINNER_DUE: ("verdict", "domain_id", "evidence_ref"),
    KIND_ORDER_CREATED_DUE: ("order_id", "domain_id"),
    KIND_ORDER_CONFIRMED_DUE: ("order_id", "decision"),
    KIND_ORDER_DISPATCH_DUE: ("order_id", "contractor_session", "model_tier"),
    KIND_ORDER_DEFERRED_DUE: ("order_id", "reason"),
    KIND_WORK_ORDER_SHADOW_READY: (
        "work_order_id",
        "module_id",
        "challenger_branch",
        "criteria_yaml_ref",
        "criteria_hash",
        "domain",
        "tier_action",
    ),
    KIND_WORK_ORDER_CLOSED_DUE: ("work_order_id", "closure"),
    KIND_WORK_ORDER_DEAD: ("work_order_id", "reason"),
}
SCHEDULING_KINDS: Final = frozenset(PAYLOAD_REQUIRED_KEYS)
Handler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class SchedulingEvent:
    """journal 内一条事件（只读快照形态）。"""

    id: str
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    recorded_at: str = ""
    attempts: int = 0
    poison: bool = False
    last_error: str = ""

    @classmethod
    def from_line(cls, raw: Mapping[str, Any]) -> "SchedulingEvent":
        """JSON 行 → 事件（缺字段给安全默认，不炸——历史行兼容）。"""
        return cls(
            id=str(raw.get("id") or ""),
            kind=str(raw.get("kind") or ""),
            payload=dict(raw.get("payload") or {}),
            recorded_at=str(raw.get("recorded_at") or ""),
            attempts=int(raw.get("attempts") or 0),
            poison=bool(raw.get("poison")),
            last_error=str(raw.get("last_error") or ""),
        )

    def to_json(self) -> str:
        return json.dumps(
            {
                "id": self.id,
                "kind": self.kind,
                "payload": self.payload,
                "recorded_at": self.recorded_at,
                "attempts": self.attempts,
                "poison": self.poison,
                "last_error": self.last_error,
            },
            ensure_ascii=False,
        )


class SchedulingJournal:
    """L5 事件 journal：落盘优先 + 幂等消费 + 毒丸留档 + KillSwitch fail-closed（intake 同模式）。"""

    def __init__(
        self,
        state_dir: Path | str | None = None,
        handlers: dict[str, Handler] | None = None,
    ) -> None:
        self.state_dir: Final = Path(state_dir) if state_dir else DEFAULT_STATE_DIR
        self.journal_path: Final = self.state_dir / JOURNAL_NAME
        self.receipt_path: Final = self.state_dir / RECEIPT_NAME
        self._handlers: dict[str, Handler] = dict(handlers or {})

    def register_handler(self, kind: str, handler: Handler) -> None:
        """挂消费体（未知 kind 拒挂，防拼错静默不消费）。"""
        if kind not in SCHEDULING_KINDS:
            raise ValueError(f"unknown_scheduling_kind:{kind}")
        self._handlers[kind] = handler

    def emit(self, kind: str, payload: dict[str, Any] | None = None) -> SchedulingEvent:
        """事件先落盘（唯一真源），返回事件对象。未知 kind / 缺必填键直接拒。"""
        if kind not in SCHEDULING_KINDS:
            raise ValueError(f"unknown_scheduling_kind:{kind}")
        body = dict(payload or {})
        missing = [k for k in PAYLOAD_REQUIRED_KEYS[kind] if k not in body]
        if missing:
            raise ValueError(f"payload_missing_keys:{kind}:{','.join(missing)}")
        event = SchedulingEvent(
            id=f"{EVENT_ID_PREFIX}-{now_utc().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}",
            kind=kind,
            payload=body,
            recorded_at=now_utc().isoformat(),
        )
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with self.journal_path.open("a", encoding="utf-8") as handle:
            handle.write(event.to_json() + "\n")
        return event

    def pending(self) -> list[SchedulingEvent]:
        """读全部在队事件（含毒丸；毒丸由 status/drain 区分处置）。"""
        if not self.journal_path.exists():
            return []
        out: list[SchedulingEvent] = []
        for line in self.journal_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped:
                out.append(SchedulingEvent.from_line(json.loads(stripped)))
        return out

    def status(self) -> dict[str, Any]:
        """巡检读数：在队/毒丸/按 kind 分布 + 末次回执摘要。"""
        events = self.pending()
        by_kind: dict[str, int] = {}
        for evt in events:
            by_kind[evt.kind] = by_kind.get(evt.kind, 0) + 1
        return {
            "pending": len(events),
            "poison": sum(1 for e in events if e.poison),
            "by_kind": by_kind,
            "journal": str(self.journal_path),
            "receipt": self._read_receipt(),
        }

    def _read_receipt(self) -> dict[str, Any]:
        if not self.receipt_path.exists():
            return {}
        try:
            return json.loads(self.receipt_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            log.warning("receipt 解析失败，按空处理：%s", self.receipt_path)
            return {}

    def _rewrite(self, events: list[SchedulingEvent]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.journal_path.with_suffix(".jsonl.tmp")
        tmp.write_text("".join(e.to_json() + "\n" for e in events), encoding="utf-8")
        tmp.replace(self.journal_path)

    def _save_receipt(self, receipt: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=1), encoding="utf-8")

    def default_handler(self, raw: dict[str, Any]) -> dict[str, Any]:
        """缺省消费体：L5 下游消费方（L6/L7/L2 回执线）缺席=抛错留队（缺消费者≠丢事件）。

        L5 自有消费（winner→工单生成）由 order_daemon 经 register_handler 挂载；
        回执线消费体在 L6/L7 卡实施时 register_handler（镜像 compare_events 惯例）。
        """
        kind = str(raw.get("kind") or "")
        if kind in self._handlers:
            return self._handlers[kind](dict(raw))
        raise RuntimeError(f"no_consumer_yet:{kind}（下游卡实施时挂消费体）")

    def drain(self, max_events: int = 20, handler: Handler | None = None) -> dict[str, Any]:
        """消费 journal：成功才出队；失败保留计 attempts；毒丸留档；KillSwitch 非 normal 停消费全保留。"""
        runner = handler or self.default_handler
        processed: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        stop_reason: str | None = None
        for _ in range(max_events):
            clear, why = probe_kill_switch()
            if not clear:
                stop_reason = why
                break
            events = self.pending()
            target = next((e for e in events if not e.poison), None)
            if target is None:
                skipped.extend({"id": e.id, "kind": e.kind, "why": "poison_held"} for e in events if e.poison)
                break
            try:
                result = runner({"id": target.id, "kind": target.kind, "payload": target.payload})
                processed.append({"id": target.id, "kind": target.kind, "result": result})
                self._rewrite([e for e in self.pending() if e.id != target.id])
            except Exception as exc:  # noqa: BLE001——失败保留+计 attempts，本轮到此为止（重试跨唤醒）
                err = f"{type(exc).__name__}: {exc}"[:200]
                self._bump_attempts(target, err)
                failed.append({"id": target.id, "kind": target.kind, "error": err})
                break
        receipt = {
            "processed": processed,
            "failed": failed,
            "skipped": skipped,
            "stop_reason": stop_reason,
            "pending_left": len(self.pending()),
            "drained_at": now_utc().isoformat(),
        }
        self._save_receipt(receipt)
        return receipt

    def _bump_attempts(self, target: SchedulingEvent, err: str) -> None:
        """失败计数 +1；达 MAX_ATTEMPTS 判毒丸留档（不再自动消费，人工处置后删行）。"""
        rebuilt: list[SchedulingEvent] = []
        for evt in self.pending():
            if evt.id != target.id:
                rebuilt.append(evt)
                continue
            attempts = evt.attempts + 1
            poison = attempts >= MAX_ATTEMPTS
            if poison:
                log.error("scheduling 事件毒丸留档：%s kind=%s err=%s", evt.id, evt.kind, err)
            rebuilt.append(
                SchedulingEvent(
                    id=evt.id,
                    kind=evt.kind,
                    payload=evt.payload,
                    recorded_at=evt.recorded_at,
                    attempts=attempts,
                    poison=poison,
                    last_error=err,
                )
            )
        self._rewrite(rebuilt)

    def purge_poison(self, event_id: str) -> bool:
        """人工处置后删行（唯一合法的毒丸清除入口，留日志痕）。"""
        events = self.pending()
        kept = [e for e in events if e.id != event_id]
        if len(kept) == len(events):
            return False
        log.warning("scheduling 毒丸人工清除：%s", event_id)
        self._rewrite(kept)
        return True
