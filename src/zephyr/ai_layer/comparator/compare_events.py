# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_comparator
# [MODULE] zephyr.ai_layer.comparator.compare_events
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.comparator.experiment_store (ExperimentStore/ComparisonExperimentRecord);
#                zephyr.ai_layer.intake.intake_events (probe_kill_switch 复用，零复制);
#                zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] L7 判据档案（comparison_archived_due 消费方，L7 卡实施时经 register_handler 挂消费体）;
#             zephyr.ai_layer.comparator.executor（领考前 prior_query 防重复考古）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 事件触发零定时器（禁 cron/Timer/sleep-loop，宪法 §9.3——archived 是唯一触发沿）；
#              journal 先落盘再消费（.runtime/ai_compare/pending_events.jsonl 唯一真源，镜像
#              .runtime/ai_intake 先例）；kind 白名单+必填键校验 fail-closed，未知 kind 拒 emit；
#              KillSwitch 探针复用 intake_events.probe_kill_switch（fail-closed：探测失败=停消费全保留）；
#              毒丸 MAX_ATTEMPTS=3 留档不自动消费；prior_query 只读（读路径唯一真源=DatabaseService）；
#              L7 消费体缺席=事件滞留 journal 等消费（缺消费者≠丢事件，留 receipt 痕）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L4_compare/DESIGN.md §3（接线图=L4↔L7 契约真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] emit 未知 kind/缺必填键→ValueError（绝不落半截事件）；journal 读写 OSError→上抛；
#                  handler 抛错→事件保留+attempts+1+last_error 留痕，本轮 drain 到此为止；
#                  prior_query 只读（store 注入缺省走 ExperimentStore 只读路径，禁写）
# [TESTS] tests/ai_layer/comparator/test_compare_events.py（emit 白名单+缺键拒/journal 先落盘/
#         drain 幂等+毒丸/archive_and_notify 触发沿/prior_query 过滤+只读注入）
# [TTL] permanent
"""compare_events — L4↔L7 接线：comparison_archived_due 事件 + comparison_prior_query 只读服务。

★ 文件名沿 L2 先例用 ``compare_events.py`` 而非设计稿口语的 ``events.py``：能力册
``drift_detection_events`` 的 alias 是裸词 ``events``，任何新 ``events.py`` 都会被 CREATE-GUARD
的 basename 碰撞判成 sibling duplicate 硬阻断（L2 intake_events 同款施工期实测，见其 docstring）。
件内语义与 DESIGN §3 完全一致。

契约真源：``docs/_working/ai_layer_vision/L4_compare/DESIGN.md`` §3 接线图 L7 行::

    comparison_archived_due   L4 → L7：experiment 卡 archived 时 emit（判据档案收"当时为什么算它赢"）
    comparison_prior_query    L7 → L4：领考前只读先验查询(simhash/mechanism_family)→历史裁定列表，
                              同候选已考直接引用旧裁定防重复考古（L7 卡实施时可注入 remote_query
                              委托 L7 服务；缺席回落本仓 ai_compare 归档卡，仍只读）

边界：L2 侧三事件（intake_scored_due/intake_reject_due/intake_exam_due）的收发属 L2 事件层
既有 kind（intake_events），本件不重复定义；其中派考边 `intake_exam_due` 跨稿契约=真待 Owner
（vision README §3.5 L4-#3），禁施工未接线。
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Final, Mapping

from zephyr.ai_layer.comparator.experiment_store import ComparisonExperimentRecord, ExperimentStore
from zephyr.ai_layer.intake.intake_events import probe_kill_switch
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "COMPARE_KINDS",
    "CompareEvent",
    "CompareJournal",
    "PAYLOAD_REQUIRED_KEYS",
    "archive_and_notify",
    "comparison_prior_query",
]

MAX_ATTEMPTS: Final = 3
DEFAULT_STATE_DIR: Final = REPO_ROOT / ".runtime" / "ai_compare"
JOURNAL_NAME: Final = "pending_events.jsonl"
RECEIPT_NAME: Final = "last_receipt.json"
EVENT_ID_PREFIX: Final = "CMPARE"
ARCHIVED_KIND: Final = "comparison_archived_due"

PAYLOAD_REQUIRED_KEYS: Final[dict[str, tuple[str, ...]]] = {
    ARCHIVED_KIND: ("experiment_id", "verdict"),
}
COMPARE_KINDS: Final = frozenset(PAYLOAD_REQUIRED_KEYS)
Handler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class CompareEvent:
    """journal 内一条事件（只读快照形态）。"""

    id: str
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    recorded_at: str = ""
    attempts: int = 0
    poison: bool = False
    last_error: str = ""

    @classmethod
    def from_line(cls, raw: Mapping[str, Any]) -> "CompareEvent":
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


class CompareJournal:
    """L4 事件 journal：落盘优先 + 幂等消费 + 毒丸留档 + KillSwitch fail-closed（intake 同模式）。"""

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
        """挂消费体（未知 kind 拒挂，防拼错静默不消费；L7 卡实施时挂 comparison_archived_due）。"""
        if kind not in COMPARE_KINDS:
            raise ValueError(f"unknown_compare_kind:{kind}")
        self._handlers[kind] = handler

    def emit(self, kind: str, payload: Mapping[str, Any] | None = None) -> CompareEvent:
        """事件先落盘（唯一真源），返回事件对象。未知 kind / 缺必填键直接拒（fail-closed）。"""
        if kind not in COMPARE_KINDS:
            raise ValueError(f"unknown_compare_kind:{kind}")
        body = dict(payload or {})
        missing = [k for k in PAYLOAD_REQUIRED_KEYS[kind] if k not in body]
        if missing:
            raise ValueError(f"payload_missing_keys:{kind}:{','.join(missing)}")
        event = CompareEvent(
            id=f"{EVENT_ID_PREFIX}-{now_utc().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}",
            kind=kind,
            payload=body,
            recorded_at=now_utc().isoformat(),
        )
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with self.journal_path.open("a", encoding="utf-8") as handle:
            handle.write(event.to_json() + "\n")
        return event

    def pending(self) -> list[CompareEvent]:
        """读全部在队事件（含毒丸）。"""
        if not self.journal_path.exists():
            return []
        out: list[CompareEvent] = []
        for line in self.journal_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(CompareEvent.from_line(json.loads(line)))
        return out

    def status(self) -> dict[str, Any]:
        """巡检读数：在队/毒丸/按 kind 分布。"""
        events = self.pending()
        by_kind: dict[str, int] = {}
        for evt in events:
            by_kind[evt.kind] = by_kind.get(evt.kind, 0) + 1
        return {"pending": len(events), "poison": sum(1 for e in events if e.poison),
                "by_kind": by_kind, "journal": str(self.journal_path)}

    def _rewrite(self, events: list[CompareEvent]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.journal_path.with_suffix(".jsonl.tmp")
        tmp.write_text("".join(e.to_json() + "\n" for e in events), encoding="utf-8")
        tmp.replace(self.journal_path)

    def _save_receipt(self, receipt: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=1), encoding="utf-8"
        )

    def default_handler(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        """缺省消费体：L7 消费体缺席=抛错留队（缺消费者≠丢事件），L7 卡实施时 register_handler。"""
        kind = str(raw.get("kind") or "")
        if kind in self._handlers:
            return self._handlers[kind](dict(raw))
        raise RuntimeError(f"no_consumer_yet:{kind}（L7 判据档案卡实施时挂消费体）")

    def drain(self, max_events: int = 20, handler: Handler | None = None) -> dict[str, Any]:
        """消费 journal：成功才出队；失败保留计 attempts；毒丸留档；KillSwitch 非 normal 停消费全保留。"""
        runner = handler or self.default_handler
        processed: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []
        stop_reason: str | None = None
        for _ in range(max_events):
            clear, why = probe_kill_switch()
            if not clear:
                stop_reason = why
                break
            events = self.pending()
            target = next((e for e in events if not e.poison), None)
            if target is None:
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
            "stop_reason": stop_reason,
            "pending_left": len(self.pending()),
            "drained_at": now_utc().isoformat(),
        }
        self._save_receipt(receipt)
        return receipt

    def _bump_attempts(self, target: CompareEvent, err: str) -> None:
        """失败计数 +1；达 MAX_ATTEMPTS 判毒丸留档（不再自动消费，人工处置后删行）。"""
        rebuilt: list[CompareEvent] = []
        for evt in self.pending():
            if evt.id != target.id:
                rebuilt.append(evt)
                continue
            attempts = evt.attempts + 1
            poison = attempts >= MAX_ATTEMPTS
            if poison:
                log_event = f"poison_held:{err}"
            else:
                log_event = err
            rebuilt.append(CompareEvent(
                id=evt.id, kind=evt.kind, payload=evt.payload,
                recorded_at=evt.recorded_at, attempts=attempts,
                poison=poison, last_error=log_event,
            ))
        self._rewrite(rebuilt)


def archived_payload(record: ComparisonExperimentRecord) -> dict[str, Any]:
    """archived 卡 → 事件载荷（DESIGN §3：{experiment_id, criteria_yaml, verdict, 归因, 出口}）。"""
    return {
        "experiment_id": record.experiment_id,
        "verdict": record.verdict,
        "criteria_hash": record.criteria_hash,
        "criteria_yaml": record.criteria_yaml,
        "attribution": record.attribution,
        "too_good_exit": record.too_good_exit,
        "rejection_reason": record.rejection_reason,
        "evidence_ref": record.evidence_ref,
    }


def archive_and_notify(
    store: ExperimentStore, journal: CompareJournal, experiment_id: str
) -> CompareEvent:
    """归档触发沿（事件触发零定时器）：卡 archive 成功后 emit comparison_archived_due。

    顺序铁律：先 archive（状态真源落库）后 emit（通知入 journal）——emit 失败上抛不回滚
    归档，重放由调用方按 receipt 补发（事件允许重放，归档幂等）。
    """
    record = store.get(experiment_id)
    if record is None:
        raise KeyError(f"experiment_not_found:{experiment_id}")
    store.archive(experiment_id)
    refreshed = store.get(experiment_id)
    return journal.emit(ARCHIVED_KIND, archived_payload(refreshed or record))


def comparison_prior_query(
    *,
    mechanism_family: str | None = None,
    candidate_simhash: str | None = None,
    store: ExperimentStore | None = None,
    remote_query: Callable[..., list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    """领考前先验查询（只读）：同候选已考直接引用旧裁定防重复考古（DESIGN §3 L7 行）。

    :param remote_query: L7 只读服务（L7 卡实施时注入委托）；缺席回落本仓 ai_compare 归档卡
    :param store: ExperimentStore 注入（测试传 tmp 侧实例；缺省走只读路径）
    """
    if remote_query is not None:
        return list(
            remote_query(
                mechanism_family=mechanism_family, candidate_simhash=candidate_simhash
            )
        )
    target = store or ExperimentStore()
    records = target.list_archived()
    out: list[dict[str, Any]] = []
    for rec in records:
        if mechanism_family and rec.mechanism_family != mechanism_family:
            continue
        if candidate_simhash and rec.candidate_simhash != candidate_simhash:
            continue
        out.append({
            "experiment_id": rec.experiment_id,
            "verdict": rec.verdict,
            "criteria_hash": rec.criteria_hash,
            "attribution": rec.attribution,
            "too_good_exit": rec.too_good_exit,
            "challenger_ref": rec.challenger_ref,
            "mechanism_family": rec.mechanism_family,
            "candidate_simhash": rec.candidate_simhash,
        })
    return out
