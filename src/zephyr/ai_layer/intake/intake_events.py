# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] zephyr.ai_layer.intake.intake_events
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc); zephyr.security.access_control.kill_switch (get_kill_switch); zephyr.ai_layer.intake.card_store (CardStore); zephyr.ai_layer.intake.gate (IntakeGate); zephyr.ai_layer.intake.kpi
# [CONSUMERS] zephyr.ai_layer.intake.kpi (IntakeJournal 注入)；★ 包外零消费者（实测 git grep src/ 零命中）：
#             L1 感知 / L3-L4 出分 / L5 排产 / DataScheduler task_completed 轻唤醒 四个设计消费方**均未建成**，
#             原声明属"计划当现状"假声明（R-021 型），已按实测改判为在册缺口，处方=lanes/aibase_relay.md §6
# [STARTUP] event_driven
# [MATURITY] evolving
# [INVARIANTS] 事件触发零定时器（禁 cron/Timer/sleep-loop，宪法 §9.3）；journal 先落盘再消费（.runtime/ai_intake/pending_events.jsonl 是唯一真源）；
#              七个 kind 全为轻 kind；drain 幂等（成功才出队，重放零副作用）；单条重试超 MAX_ATTEMPTS=3 判毒丸留档不再自动消费；
#              KillSwitch 探针 fail-closed（探测失败=不清除=停消费，事件全量保留待恢复重放）；
#              kind 与必填 payload 键白名单校验，未知 kind 拒 emit（fail-closed）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §三（接线图=事件契约真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] emit 未知 kind / 缺必填键→ValueError（绝不落半截事件）；handler 抛错→事件保留 + attempts+1 + last_error 留痕，本轮 drain 到此为止（重试跨唤醒）；
#                  journal 读写 OSError→上抛（不静默丢事件）；KillSwitch 不可达→stop_reason=kill_switch_probe_error 且零消费
# [TESTS] tests/ai_layer/intake/（★ 在册缺口：本模块测试 test_events.py 未建，处方见 lanes/aibase_relay.md §6）
# [TTL] permanent
"""intake_events — L2 收集段事件层：七轻 kind 的 JSONL journal（emit / status / drain）。

★ 文件名由设计稿的 `events.py` 改为 `intake_events.py`（施工期实测，非设计变更）：
  能力册 `drift_detection_events` 的 alias 是裸词 `events`，任何新 `events.py` 都会被
  CREATE-GUARD 的 basename 碰撞判成它的 sibling duplicate 而硬阻断（本车道实测死信
  q-20260918-st-ff-ailayer2-20260918-0001）。件内语义与 DESIGN §三 完全不变；
  在册缺口与处方见 docs/_working/fullflow_campaign/lanes/aibase_relay.md §6.4。

契约真源：``docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md`` §三 接线图。

七个 kind（全轻，零定时器）::

    intake_ingest_due    L1 感知 → L2 入库闸（跑 §2.5 全闸，逐卡回执）
    intake_clean_due     L2 → L3 清洗（funnel_stage=L2 的卡批量派洗）
    intake_reject_due    L3/L4 → L2（置 rejected + 入 V2 阴性库，同 simhash 换皮从此被闸拦）
    intake_scored_due    L4 → L2（回写 elite_score/elite_rank，格满 benched）
    intake_e2_handoff    L2 → L5 排产（对产线唯一出口，跨生熟边界前最后留痕）
    intake_exam_receipt  考试回执线 → L2（e2_pending 卡出证回执，L2 只记帐）
    intake_kpi_alert     L2 内部告警（贫矿降级 / 判据收紧）

与 ``zephyr.strategy_pipeline.pipeline_events`` 的关系：语义对齐（journal+emit/drain/status+KillSwitch
探针+毒丸 MAX_ATTEMPTS=3），但**不复用其原语**——该模块 journal 路径是模块级常量硬绑
``.runtime/strategy_pipeline``，不可参数化 import；按 DESIGN §三 裁定"按其模式新建"，
本实现改为 class 形态（``IntakeJournal``）以隔离状态目录并避开 extract 级克隆。
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "INTAKE_KINDS",
    "IntakeEvent",
    "IntakeJournal",
    "PAYLOAD_REQUIRED_KEYS",
]

MAX_ATTEMPTS: Final = 3
DEFAULT_STATE_DIR: Final = REPO_ROOT / ".runtime" / "ai_intake"
JOURNAL_NAME: Final = "pending_events.jsonl"
RECEIPT_NAME: Final = "last_receipt.json"
EVENT_ID_PREFIX: Final = "AINTAKE"

PAYLOAD_REQUIRED_KEYS: Final[dict[str, tuple[str, ...]]] = {
    "intake_ingest_due": ("source_slug", "raw_staging_path"),
    "intake_clean_due": ("card_ids", "domain_id"),
    "intake_reject_due": ("card_id", "stage", "rejection_reason"),
    "intake_scored_due": ("card_id", "verdict", "score"),
    "intake_e2_handoff": ("card_id", "spec_ref", "four_gates", "labor_killed", "domain_id"),
    "intake_exam_receipt": ("candidate_card_id", "evidence_ref"),
    "intake_kpi_alert": ("scope", "key", "pass_rate", "action"),
}
INTAKE_KINDS: Final = frozenset(PAYLOAD_REQUIRED_KEYS)
Handler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class IntakeEvent:
    """journal 内一条事件（只读快照形态）。"""

    id: str
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    recorded_at: str = ""
    attempts: int = 0
    poison: bool = False
    last_error: str = ""

    @classmethod
    def from_line(cls, raw: dict[str, Any]) -> "IntakeEvent":
        """JSON 行 → 事件（缺字段给安全默认，不抛错——历史行兼容）。"""
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


def probe_kill_switch() -> tuple[bool, str]:
    """KillSwitch 探针（fail-closed：探测异常=不清除=停消费，事件留 journal 等恢复重放）。"""
    try:
        from zephyr.security.access_control.kill_switch import get_kill_switch

        raw = get_kill_switch().state
        state = str(getattr(raw, "value", raw) or "").lower()
        if state in ("", "normal"):
            return True, "normal"
        return False, f"kill_switch={state}"
    except Exception as exc:  # noqa: BLE001——探针失败按 fail-closed 处置（安全方向）
        return False, f"kill_switch_probe_error:{type(exc).__name__}"


class IntakeJournal:
    """L2 事件 journal：落盘优先 + 幂等消费 + 毒丸留档 + KillSwitch fail-closed。"""

    def __init__(
        self,
        state_dir: Path | str | None = None,
        handlers: dict[str, Handler] | None = None,
        schema: str = "ai_intake",
    ) -> None:
        self.state_dir: Final = Path(state_dir) if state_dir else DEFAULT_STATE_DIR
        self.journal_path: Final = self.state_dir / JOURNAL_NAME
        self.receipt_path: Final = self.state_dir / RECEIPT_NAME
        self.schema: Final = schema
        self._handlers: dict[str, Handler] = dict(handlers or {})

    def register_handler(self, kind: str, handler: Handler) -> None:
        """挂消费体（未知 kind 拒挂，防拼错静默不消费）。"""
        if kind not in INTAKE_KINDS:
            raise ValueError(f"unknown_intake_kind:{kind}")
        self._handlers[kind] = handler

    def emit(self, kind: str, payload: dict[str, Any] | None = None) -> IntakeEvent:
        """事件先落盘（唯一真源），返回事件对象。未知 kind / 缺必填键直接拒。"""
        if kind not in INTAKE_KINDS:
            raise ValueError(f"unknown_intake_kind:{kind}")
        body = dict(payload or {})
        missing = [k for k in PAYLOAD_REQUIRED_KEYS[kind] if k not in body]
        if missing:
            raise ValueError(f"payload_missing_keys:{kind}:{','.join(missing)}")
        event = IntakeEvent(
            id=f"{EVENT_ID_PREFIX}-{now_utc().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}",
            kind=kind,
            payload=body,
            recorded_at=now_utc().isoformat(),
        )
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with self.journal_path.open("a", encoding="utf-8") as handle:
            handle.write(event.to_json() + "\n")
        return event

    def pending(self) -> list[IntakeEvent]:
        """读全部在队事件（含毒丸；毒丸由 status/drain 区分处置）。"""
        if not self.journal_path.exists():
            return []
        out: list[IntakeEvent] = []
        for line in self.journal_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped:
                out.append(IntakeEvent.from_line(json.loads(stripped)))
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

    def _rewrite(self, events: list[IntakeEvent]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.journal_path.with_suffix(".jsonl.tmp")
        tmp.write_text("".join(e.to_json() + "\n" for e in events), encoding="utf-8")
        tmp.replace(self.journal_path)

    def _save_receipt(self, receipt: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=1), encoding="utf-8")

    def default_handler(self, raw: dict[str, Any]) -> dict[str, Any]:
        """缺省消费体：kind → L2 侧落点（惰性 import 破 events↔kpi 环）。

        入参是 ``{"id","kind","payload"}`` 字典（Handler 协议），不是 IntakeEvent。
        """
        kind = str(raw.get("kind") or "")
        payload = dict(raw.get("payload") or {})
        if kind in self._handlers:
            return self._handlers[kind](raw)
        if kind == "intake_ingest_due":
            from zephyr.ai_layer.intake.gate import run_ingest

            result = run_ingest(
                str(payload.get("raw_staging_path") or ""), schema=self.schema
            )
            if result.get("refused"):
                raise RuntimeError(f"ingest_refused:{result['refused']}")
            return {"ingested": result}
        if kind == "intake_scored_due":
            from zephyr.ai_layer.intake.card_store import CardStore

            store = CardStore(schema=self.schema)
            out = store.record_score(
                payload["card_id"], float(payload["score"]), payload.get("evidence_ref")
            )
            return {"scored": out}
        if kind == "intake_reject_due":
            from zephyr.ai_layer.intake.card_store import CardStore

            store = CardStore(schema=self.schema)
            why = store.transition(
                payload["card_id"],
                "rejected",
                rejection_reason=payload.get("rejection_reason"),
                evidence_ref=payload.get("evidence_ref"),
            )
            return {"rejected": payload["card_id"], "why": why}
        if kind == "intake_kpi_alert":
            from zephyr.ai_layer.intake import kpi as kpi_mod

            return kpi_mod.handle_alert(payload)
        return {"accepted": False, "reason": f"no_handler:{kind}"}

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

    def _bump_attempts(self, target: IntakeEvent, err: str) -> None:
        """失败计数 +1；达 MAX_ATTEMPTS 判毒丸留档（不再自动消费，人工处置后删行）。

        IntakeEvent 是 frozen dataclass → 用重建而非原地改（防 FrozenInstanceError）。
        """
        rebuilt: list[IntakeEvent] = []
        for evt in self.pending():
            if evt.id != target.id:
                rebuilt.append(evt)
                continue
            attempts = evt.attempts + 1
            poison = attempts >= MAX_ATTEMPTS
            if poison:
                log.error("intake 事件毒丸留档：%s kind=%s err=%s", evt.id, evt.kind, err)
            rebuilt.append(
                IntakeEvent(
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
        log.warning("intake 毒丸人工清除：%s", event_id)
        self._rewrite(kept)
        return True
