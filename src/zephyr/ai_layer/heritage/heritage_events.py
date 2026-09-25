# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] zephyr.ai_layer.heritage.heritage_events
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.heritage.store (HeritageStore/HeritageDraft/RegistrationRefused);
#                zephyr.ai_layer.heritage.closure_check (validate_receipt——关单回执机检复用);
#                zephyr.ai_layer.heritage.policy (load_policy);
#                zephyr.ai_layer.intake.intake_events (probe_kill_switch——KillSwitch 探针复用不复制);
#                zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] L6 切换（switch_archived_due emit）；L4 对比（comparison_archived_due emit）；
#             工单流（work_order_closed_due emit）；月度体检窗 drain 兜底；
#             CLI python -m zephyr.ai_layer.heritage.heritage_events emit/drain/status
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 事件触发零定时器（禁 cron/Timer/sleep-loop，宪法 §9.3）；journal 先落盘再消费
#              （.runtime/ai_heritage/pending_events.jsonl 唯一真源，pipeline_events 语义收编）;
#              drain 幂等（成功才出队，重放零副作用——登记由 content_sha256 自查重兜底幂等）;
#              单条重试超 MAX_ATTEMPTS=3 判毒丸留档不再自动消费；KillSwitch 探针 fail-closed
#              （复用 intake_events.probe_kill_switch，非 normal 停消费全量保留）;
#              L6/L4 事件未落地不阻塞：声明态消费，合成载荷先行（DESIGN §四依赖序）;
#              kind 与必填 payload 键白名单校验，未知 kind 拒 emit（fail-closed）;
#              三事件→动作翻译是纯函数（payload_to_actions 零 DB 零 IO，可合成载荷全枚举单测）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §三（接线图=事件契约真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] emit 未知 kind/缺必填键→ValueError（绝不落半截事件）；handler 抛错→事件保留+
#                  attempts+1+last_error 留痕，本轮 drain 到此为止（重试跨唤醒）；
#                  RegistrationRefused→按拒因留痕计失败（毒丸线同款）；journal 读写 OSError→上抛
# [TESTS] tests/ai_layer/heritage/test_heritage_events.py（三事件合成载荷→正确动作计划/胜负退场三分/
#         毒丸 MAX_ATTEMPTS=3/KillSwitch 非 normal 全保留）
"""heritage_events — L7 回流事件层：三回写边事件的 JSONL journal（emit / status / drain）。

设计真源：``docs/_working/ai_layer_vision/L7_heredity/DESIGN.md`` §三 接线图（三条回写边契约）。

★ 文件名由设计稿的 ``events.py`` 改为 ``heritage_events.py``（施工期实测，非设计变更）：
  能力册 ``drift_detection_events`` 的 alias 是裸词 ``events``，CREATE-GUARD basename 碰撞会
  硬阻断任何新 ``events.py``（L2 车道同款死信 q-20260918-st-ff-ailayer2-20260918-0001 先例，
  L2 侧已改名 intake_events.py）；件内语义与 DESIGN §三 完全不变。

三个 kind（全轻，零定时器）::

    switch_archived_due      L6 终局态转换（promote→champion/aborted/retire→tombstone）→ L7
                             消费：胜局→elite+criteria 双条目；aborted 带根因→defect；retired→elite 降级信号
    comparison_archived_due  L4 experiment 卡 archived → L7：criteria 条目（+win 时 elite 条目）
    work_order_closed_due    工单关单回执 → L7：新建缺陷登记/既有模式 occurrence+1/no_new_pattern 校验

与 ``zephyr.strategy_pipeline.pipeline_events``/``intake_events`` 的关系：语义对齐（journal+
emit/drain/status+KillSwitch 探针+毒丸 MAX_ATTEMPTS=3），不复用其 journal 类（其 kind 白名单
与状态目录各自硬绑；跨段泛化须改既有文件=本班禁改）——按 DESIGN §三 裁定"按其模式新建"。
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.ai_layer.heritage.closure_check import validate_receipt
from zephyr.ai_layer.heritage.store import (
    DEFAULT_SCHEMA,
    HeritageDraft,
    HeritageStore,
    RegistrationRefused,
)
from zephyr.ai_layer.intake.intake_events import probe_kill_switch
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "HERITAGE_KINDS",
    "HeritageAction",
    "HeritageEvent",
    "HeritageJournal",
    "PAYLOAD_REQUIRED_KEYS",
    "closure_payload_to_actions",
    "comparison_payload_to_actions",
    "switch_payload_to_actions",
]

MAX_ATTEMPTS: Final = 3
DEFAULT_STATE_DIR: Final = REPO_ROOT / ".runtime" / "ai_heritage"
JOURNAL_NAME: Final = "pending_events.jsonl"
RECEIPT_NAME: Final = "last_receipt.json"
EVENT_ID_PREFIX: Final = "AHERIT"
SWITCH_OUTCOMES: Final[frozenset[str]] = frozenset({"promoted", "aborted", "retired"})
VENUE_MAP: Final[dict[str, str]] = {
    "venue_c4": "c4",
    "venue_replay": "replay",
    "venue_dual_run": "dual_run",
    "venue_tool_bench": "tool_bench",
}
WIN_VERDICTS: Final[frozenset[str]] = frozenset({"win", "win_starred"})

PAYLOAD_REQUIRED_KEYS: Final[dict[str, tuple[str, ...]]] = {
    "switch_archived_due": ("switch_id", "outcome", "domain_id"),
    "comparison_archived_due": (
        "experiment_id",
        "criteria_hash",
        "venue",
        "verdict",
        "why_win",
        "domain_id",
    ),
    "work_order_closed_due": ("work_order_id", "kind"),
}
HERITAGE_KINDS: Final = frozenset(PAYLOAD_REQUIRED_KEYS)
Handler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class HeritageAction:
    """事件→落库动作计划的一步（纯函数产物，由 handler 对 store 执行）。

    action 词表：register（带 draft 落库）/ demote（entry_id 降级到 target_status）/
    occurrence（entry_id 同坑累加）/ skip（note 留痕跳过）/ noop（校验通过零动作）
    """

    action: str
    draft: HeritageDraft | None = None
    entry_id: str | None = None
    target_status: str | None = None
    note: str = ""


@dataclass(frozen=True)
class HeritageEvent:
    """journal 内一条事件（只读快照形态）。"""

    id: str
    kind: str
    payload: dict[str, Any]
    recorded_at: str = ""
    attempts: int = 0
    poison: bool = False
    last_error: str = ""

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

    @classmethod
    def from_line(cls, raw: dict[str, Any]) -> "HeritageEvent":
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


def _common_draft_fields(payload: dict[str, Any], source_kind: str, source_ref: str) -> dict[str, Any]:
    """H1 主表公共字段抽取（三类事件共用）。"""
    return {
        "title": str(payload.get("title") or f"{source_kind} 回流 {source_ref}"),
        "plain_zh": str(payload.get("plain_zh") or ""),
        "domain_id": str(payload.get("domain_id") or ""),
        "source_kind": source_kind,
        "source_ref": source_ref,
    }


def switch_payload_to_actions(payload: dict[str, Any]) -> list[HeritageAction]:
    """switch_archived_due → 动作计划（纯函数；胜局双条目/败因缺陷/退场降级三路由）。"""
    outcome = str(payload.get("outcome") or "")
    if outcome not in SWITCH_OUTCOMES:
        raise ValueError(f"unknown_switch_outcome:{outcome}")
    base = _common_draft_fields(payload, "l6_switch", str(payload["switch_id"]))
    actions: list[HeritageAction] = []
    if outcome == "promoted":
        actions.extend(_switch_promoted_actions(payload, base))
    elif outcome == "aborted":
        actions.append(_switch_aborted_action(payload, base))
    else:
        actions.append(
            HeritageAction(
                action="demote",
                entry_id=str(payload.get("heritage_entry_id") or "") or None,
                target_status="archived",
                note=f"l6_retired:{payload.get('switch_id')}",
            )
            if payload.get("heritage_entry_id")
            else HeritageAction(
                action="skip", note=f"retired 无 heritage_entry_id 映射，跳过降级:{payload.get('switch_id')}"
            )
        )
    return actions


def _switch_promoted_actions(payload: dict[str, Any], base: dict[str, Any]) -> list[HeritageAction]:
    """promote→champion：胜局 elite+criteria 双条目（DESIGN §三 L6 行）。"""
    missing = [
        key
        for key in ("winner_ref", "diff_summary", "criteria_ref", "criteria_hash", "mechanism_family")
        if not payload.get(key)
    ]
    if missing:
        return [HeritageAction(action="skip", note=f"promoted 缺键 {','.join(missing)}，跳过双条目")]
    elite = HeritageDraft(
        entry_kind="elite",
        surface=str(payload.get("surface") or "code_module"),
        winner_ref=str(payload["winner_ref"]),
        loser_ref=payload.get("loser_ref"),
        diff_summary=str(payload["diff_summary"]),
        evidence_ref=str(payload["criteria_ref"]),
        score_summary=dict(payload.get("score_summary") or {}),
        mechanism_family=str(payload["mechanism_family"]),
        gen=int(payload.get("gen") or 1),
        parent_entry_id=payload.get("parent_entry_id"),
        **base,
    )
    criteria = HeritageDraft(
        entry_kind="criteria",
        experiment_id=str(payload["criteria_ref"]),
        criteria_hash=str(payload["criteria_hash"]),
        venue="other",
        verdict="win",
        why_win=str(payload.get("why_win") or payload["diff_summary"]),
        **base,
    )
    return [HeritageAction(action="register", draft=elite), HeritageAction(action="register", draft=criteria)]


def _switch_aborted_action(payload: dict[str, Any], base: dict[str, Any]) -> HeritageAction:
    """aborted 带根因→defect 条目（三字段不齐=skip 留痕，不阻塞其余路由）。"""
    defect_keys = ("root_cause", "signature", "recipe", "pattern_norm")
    if any(not payload.get(key) for key in defect_keys):
        return HeritageAction(
            action="skip", note=f"aborted 缺缺陷三字段 {','.join(defect_keys)}，跳过 defect 登记"
        )
    draft = HeritageDraft(
        entry_kind="defect",
        root_cause=str(payload["root_cause"]),
        signature=str(payload["signature"]),
        recipe=str(payload["recipe"]),
        pattern_norm=str(payload["pattern_norm"]),
        affected_surfaces=tuple(payload.get("affected_surfaces") or ()),
        exclusion_keywords=tuple(payload.get("exclusion_keywords") or ()),
        **base,
    )
    return HeritageAction(action="register", draft=draft)


def comparison_payload_to_actions(payload: dict[str, Any]) -> list[HeritageAction]:
    """comparison_archived_due → 动作计划（纯函数；criteria 条目+win 时 elite 条目）。"""
    source_ref = str(payload["experiment_id"])
    base = _common_draft_fields(payload, "l4_experiment", source_ref)
    venue_raw = str(payload["venue"])
    venue = VENUE_MAP.get(venue_raw, venue_raw if venue_raw in {"c4", "replay", "dual_run", "tool_bench"} else "other")
    criteria = HeritageDraft(
        entry_kind="criteria",
        experiment_id=source_ref,
        criteria_hash=str(payload["criteria_hash"]),
        venue=venue,
        verdict=str(payload["verdict"]),
        why_win=str(payload["why_win"]),
        mechanism_family=payload.get("mechanism_family"),
        **base,
    )
    actions = [HeritageAction(action="register", draft=criteria)]
    verdict = str(payload["verdict"])
    if verdict in WIN_VERDICTS:
        if payload.get("winner_ref") and payload.get("diff_summary"):
            elite = HeritageDraft(
                entry_kind="elite",
                surface=str(payload.get("surface") or "code_module"),
                winner_ref=str(payload["winner_ref"]),
                loser_ref=payload.get("loser_ref"),
                diff_summary=str(payload["diff_summary"]),
                evidence_ref=source_ref,
                score_summary=dict(payload.get("score_summary") or {}),
                mechanism_family=str(payload.get("mechanism_family") or "unclassified"),
                **base,
            )
            actions.append(HeritageAction(action="register", draft=elite))
        else:
            actions.append(
                HeritageAction(action="skip", note="win 缺 winner_ref/diff_summary，跳过 elite 条目")
            )
    return actions


def closure_payload_to_actions(payload: dict[str, Any]) -> list[HeritageAction]:
    """work_order_closed_due → 动作计划（纯函数；§2.9/§三 契约：heritage_ref|no_new_pattern 二选一）。

    语义裁定（对齐 §2.9 原文）：``heritage_ref``（新建缺陷模式回执）=登记已由关单流经
    store.register 完成，本处仅校验回执（noop，不重复累加）；``known_pattern: <entry_id>``
    =命中既有模式复发，occurrence_count+1；mechanical_debt/dup_of=noop 留痕。
    缺陷本体登记走 store.register（casebook 归并/关单流直调），不经本事件层。
    """
    ok, why = validate_receipt(str(payload.get("kind") or ""), payload)
    if not ok:
        raise ValueError(f"closure_receipt_invalid:{why}")
    no_new = payload.get("no_new_pattern")
    if no_new is not None:
        reason, ref = parse_no_new_pattern(no_new)
        if reason == "known_pattern":
            return [HeritageAction(action="occurrence", entry_id=ref, note=str(payload["work_order_id"]))]
        return [HeritageAction(action="noop", note=f"no_new_pattern:{reason}")]
    heritage_ref = str(payload.get("heritage_ref") or "")
    if heritage_ref:
        return [HeritageAction(action="noop", note=f"new_pattern_registered:{heritage_ref}")]
    return [HeritageAction(action="noop", note="closure 无登记面（kind 不在强制清单）")]


def parse_no_new_pattern(no_new: Any) -> tuple[str, str | None]:
    """no_new_pattern 声明解析：dict{reason, ref} 或 "known_pattern: HT-…" 字符串两态。"""
    if isinstance(no_new, dict):
        reason = str(no_new.get("reason") or "")
        ref = no_new.get("ref")
        return reason, (str(ref) if ref else None)
    text = str(no_new or "").strip()
    if ":" in text:
        reason, _, ref = text.partition(":")
        return reason.strip(), ref.strip() or None
    return text, None


class HeritageJournal:
    """L7 事件 journal：落盘优先 + 幂等消费 + 毒丸留档 + KillSwitch fail-closed。"""

    def __init__(
        self,
        state_dir: Path | str | None = None,
        *,
        store: HeritageStore | None = None,
        schema: str = DEFAULT_SCHEMA,
        handlers: dict[str, Handler] | None = None,
    ) -> None:
        self.state_dir: Final = Path(state_dir) if state_dir else DEFAULT_STATE_DIR
        self.journal_path: Final = self.state_dir / JOURNAL_NAME
        self.receipt_path: Final = self.state_dir / RECEIPT_NAME
        self.schema: Final = schema
        self._store = store
        self._handlers: dict[str, Handler] = dict(handlers or {})

    def store_or_raise(self) -> HeritageStore:
        """消费体依赖的传承库服务（惰性构造，emit 路径零 DB 依赖）。"""
        if self._store is None:
            self._store = HeritageStore(self.schema)
        return self._store

    def register_handler(self, kind: str, handler: Handler) -> None:
        """挂消费体（未知 kind 拒挂，防拼错静默不消费）。"""
        if kind not in HERITAGE_KINDS:
            raise ValueError(f"unknown_heritage_kind:{kind}")
        self._handlers[kind] = handler

    def emit(self, kind: str, payload: dict[str, Any] | None = None) -> HeritageEvent:
        """事件先落盘（唯一真源），返回事件对象。未知 kind / 缺必填键直接拒。"""
        if kind not in HERITAGE_KINDS:
            raise ValueError(f"unknown_heritage_kind:{kind}")
        body = dict(payload or {})
        missing = [k for k in PAYLOAD_REQUIRED_KEYS[kind] if k not in body]
        if missing:
            raise ValueError(f"payload_missing_keys:{kind}:{','.join(missing)}")
        event = HeritageEvent(
            id=f"{EVENT_ID_PREFIX}-{now_utc().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}",
            kind=kind,
            payload=body,
            recorded_at=now_utc().isoformat(),
        )
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with self.journal_path.open("a", encoding="utf-8") as handle:
            handle.write(event.to_json() + "\n")
        return event

    def pending(self) -> list[HeritageEvent]:
        """读全部在队事件（含毒丸；毒丸由 status/drain 区分处置）。"""
        if not self.journal_path.exists():
            return []
        out: list[HeritageEvent] = []
        for line in self.journal_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped:
                out.append(HeritageEvent.from_line(json.loads(stripped)))
        return out

    def status(self) -> dict[str, Any]:
        """巡检读数：在队/毒丸/按 kind 分布 + 末次回执摘要。"""
        events = self.pending()
        by_kind: dict[str, int] = {}
        for evt in events:
            by_kind[evt.kind] = by_kind.get(evt.kind, 0) + 1
        receipt: dict[str, Any] = {}
        if self.receipt_path.exists():
            try:
                receipt = json.loads(self.receipt_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                receipt = {}
        return {
            "pending": len(events),
            "poison": sum(1 for e in events if e.poison),
            "by_kind": by_kind,
            "journal": str(self.journal_path),
            "receipt": receipt,
        }

    def _rewrite(self, events: list[HeritageEvent]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.journal_path.with_suffix(".jsonl.tmp")
        tmp.write_text("".join(e.to_json() + "\n" for e in events), encoding="utf-8")
        tmp.replace(self.journal_path)

    def _save_receipt(self, receipt: dict[str, Any]) -> None:
        """回执落盘（单行 JSON——按行追加语义，与 pipeline_events 缩进块格式有意不同）。"""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, default=str), encoding="utf-8")

    # ---------------------------------------------------------------- 消费
    def default_handler(self, raw: dict[str, Any]) -> dict[str, Any]:
        """缺省消费体：kind → 动作计划 → store 执行（惰性构造 store 破 journal↔store import 环）。"""
        kind = str(raw.get("kind") or "")
        payload = dict(raw.get("payload") or {})
        if kind in self._handlers:
            return self._handlers[kind](raw)
        builders: dict[str, Callable[[dict[str, Any]], list[HeritageAction]]] = {
            "switch_archived_due": switch_payload_to_actions,
            "comparison_archived_due": comparison_payload_to_actions,
            "work_order_closed_due": closure_payload_to_actions,
        }
        builder = builders.get(kind)
        if builder is None:
            return {"accepted": False, "reason": f"no_handler:{kind}"}
        store = self.store_or_raise()
        results: list[dict[str, Any]] = []
        for action in builder(payload):
            results.append(self._execute(store, action))
        return {"kind": kind, "actions": results}

    def _execute(self, store: HeritageStore, action: HeritageAction) -> dict[str, Any]:
        """单动作执行（register 失败=RegistrationRefused 上抛进 drain 失败线）。"""
        if action.action == "register" and action.draft is not None:
            entry_id = store.register(action.draft)
            return {"action": "register", "entry_id": entry_id}
        if action.action == "demote" and action.entry_id and action.target_status:
            why = store.transition_status(action.entry_id, action.target_status, note=action.note)
            return {"action": "demote", "entry_id": action.entry_id, "why": why}
        if action.action == "occurrence" and action.entry_id:
            count = store.record_occurrence(action.entry_id, action.note)
            return {"action": "occurrence", "entry_id": action.entry_id, "occurrence_count": count}
        return {"action": action.action, "note": action.note}

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
                if isinstance(exc, RegistrationRefused):
                    log.warning("heritage 事件登记被拒（拒因=%s）：%s", exc.reason, target.id)
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

    def _bump_attempts(self, target: HeritageEvent, err: str) -> None:
        """失败计数 +1；达 MAX_ATTEMPTS 判毒丸留档（不再自动消费，人工处置后删行）。"""
        rebuilt: list[HeritageEvent] = []
        for evt in self.pending():
            if evt.id != target.id:
                rebuilt.append(evt)
                continue
            attempts = evt.attempts + 1
            poison = attempts >= MAX_ATTEMPTS
            if poison:
                log.error("heritage 事件毒丸留档：%s kind=%s err=%s", evt.id, evt.kind, err)
            rebuilt.append(
                HeritageEvent(
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
        if not any(e.id == event_id for e in events):
            return False
        log.warning("heritage 毒丸人工清除：%s", event_id)
        self._rewrite([e for e in events if e.id != event_id])
        return True


def main(argv: list[str] | None = None) -> int:  # pragma: no cover — CLI 薄壳，逻辑全在类
    """CLI 入口：emit / drain / status 三命令。"""
    import argparse

    parser = argparse.ArgumentParser(description="L7 传承段事件 CLI（emit/drain/status）")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="查看积压事件与最近回执")
    d = sub.add_parser("drain", help="消费事件")
    d.add_argument("--max", type=int, default=20)
    e = sub.add_parser("emit", help="手工入队事件")
    e.add_argument("kind", choices=sorted(HERITAGE_KINDS))
    e.add_argument("--payload", default="{}", help="JSON payload")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    journal = HeritageJournal()
    if args.cmd == "status":
        print(json.dumps(journal.status(), ensure_ascii=False, indent=1, default=str))
        return 0
    if args.cmd == "drain":
        print(json.dumps(journal.drain(max_events=args.max), ensure_ascii=False, indent=1, default=str))
        return 0
    evt = journal.emit(args.kind, json.loads(args.payload))
    print(json.dumps({"recorded": evt.id}, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班/人工点火, 非自动常驻任务
    raise SystemExit(main())
