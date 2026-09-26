# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] tests.ai_layer.scheduling.test_confirm_gate
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_confirm_gate — L5 一键确认判定与落点（幂等/留痕/拒因回传/三落点齐/状态机红线）。

全部 tmp_path 注入（零生产路径写入）；journal 用真实 SchedulingJournal（emit 不落 KS 探测，
无网络无定时器）。

W6-C 车道红测（红队案卷 rb2 §四 三颗雷，**全部是收紧断言，零放宽**）：

* 雷 1 并发不幂等 → ``test_concurrent_same_request_is_idempotent``（12 线程同请求：
  1 行 decided / 1 条事件 / 同一枚 receipt）
* 雷 2 半写假持久化 → ``test_second_write_failure_*`` / ``test_third_write_failure_*`` /
  ``test_half_write_never_reported_as_idempotent_success``（打桩失败必报 persist_failed
  且撤桩可复跑自愈；决策账有 decided 行而快照缺回执 ⇒ 禁当幂等命中）
* 雷 3 审计销毁器 → ``test_malformed_line_survives_unrelated_upsert`` /
  ``test_upsert_never_drops_rows_under_concurrency`` /
  ``test_upsert_keeps_duplicate_order_id_rows``（畸形行原文逐字节留盘＋quarantine 留痕＋
  出声；重写路径零行丢失）
"""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from zephyr.ai_layer.scheduling.confirm_gate import (
    DECISION_CONFIRM,
    DECISION_REJECT,
    SNAPSHOT_RECEIPT_FIELD,
    ConfirmDecisionRecord,
    ConfirmGate,
    ConfirmPersistError,
    OrderFileStore,
    evaluate_confirm,
)
from zephyr.ai_layer.scheduling.scheduling_events import (
    KIND_ORDER_CONFIRMED_DUE,
    SchedulingJournal,
)

NOW = datetime(2026, 9, 26, 4, 0, 0, tzinfo=timezone.utc)


def _order(order_id: str = "WO-20260926-001", **over: Any) -> dict[str, Any]:
    order: dict[str, Any] = {
        "order_id": order_id,
        "title": "骨架级提案样例",
        "domain_id": "governance",
        "state": "pending",
        "owner_gate": True,
        "audit_log": [{"ts": "", "action": "order_created", "detail": "source=test"}],
    }
    order.update(over)
    return order


@pytest.fixture()
def gate(tmp_path: Path) -> ConfirmGate:
    state = tmp_path / "ai_scheduling"
    journal = SchedulingJournal(state_dir=state)
    store = OrderFileStore(state)
    return ConfirmGate(state, journal=journal, store=store)


# ── 纯函数判定全枚举 ───────────────────────────────────────────────────────
def test_evaluate_invalid_decision_vocab() -> None:
    verdict = evaluate_confirm(_order(), "approve", [])
    assert verdict["ok"] is False and verdict["kind"] == "invalid_request"
    assert any(c.startswith("decision_not_vocab") for c in verdict["codes"])


def test_evaluate_missing_order() -> None:
    verdict = evaluate_confirm(None, DECISION_CONFIRM, [])
    assert verdict["ok"] is False and "order_not_found" in verdict["codes"]


def test_evaluate_non_skeleton_refused() -> None:
    verdict = evaluate_confirm(_order(owner_gate=False), DECISION_CONFIRM, [])
    assert verdict["ok"] is False and any(c.startswith("not_skeleton_level") for c in verdict["codes"])


@pytest.mark.parametrize("state", ["dispatched", "deferred", "done", "dead", "held_maturity"])
def test_evaluate_state_not_confirmable(state: str) -> None:
    verdict = evaluate_confirm(_order(state=state), DECISION_CONFIRM, [])
    assert verdict["ok"] is False
    assert any(c.startswith("state_not_confirmable") for c in verdict["codes"])


def test_evaluate_idempotent_hit() -> None:
    prior = [{"outcome": "decided", "decision": DECISION_CONFIRM, "receipt_id": "CFM-x"}]
    verdict = evaluate_confirm(_order(), DECISION_CONFIRM, prior)
    assert verdict["ok"] is True and verdict["kind"] == "idempotent_hit"


def test_evaluate_conflict_then_amend() -> None:
    prior = [{"outcome": "decided", "decision": DECISION_CONFIRM, "receipt_id": "CFM-x"}]
    refused = evaluate_confirm(_order(), DECISION_REJECT, prior)
    assert refused["ok"] is False and any(c.startswith("decision_conflict") for c in refused["codes"])
    amended = evaluate_confirm(_order(), DECISION_REJECT, prior, allow_amend=True)
    assert amended["ok"] is True and amended["kind"] == "amend"


def test_evaluate_rejected_request_history_not_blocking() -> None:
    """rejected_request 旧行不构成决策——后续合法拍板仍可过（幂等只看 outcome=decided）。"""
    prior = [{"outcome": "rejected_request", "decision": "bogus"}]
    verdict = evaluate_confirm(_order(), DECISION_CONFIRM, prior)
    assert verdict["ok"] is True and verdict["kind"] == "decided"


# ── 主入口三落点与回执形状 ─────────────────────────────────────────────────
def _seed(gate: ConfirmGate, order: dict[str, Any]) -> None:
    gate._store.upsert(order)  # noqa: SLF001——夹具直塞（测试同包纪律内）


def test_confirm_writes_three_landing_points(gate: ConfirmGate) -> None:
    _seed(gate, _order())
    result = gate.decide("WO-20260926-001", DECISION_CONFIRM, reason="夜批放行", now=NOW)
    assert result["ok"] is True and result["idempotent"] is False
    # ①事件账
    events = gate._journal.pending()  # noqa: SLF001
    assert [e.kind for e in events] == [KIND_ORDER_CONFIRMED_DUE]
    assert events[0].payload["order_id"] == "WO-20260926-001"
    assert events[0].payload["decision"] == DECISION_CONFIRM
    # ②决策账
    lines = (gate.state_dir / "confirm_decisions.jsonl").read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[0])
    assert record["outcome"] == "decided" and record["receipt_id"] == result["receipt"]["receipt_id"]
    # ③工单快照：确认≠派工，state 保持 pending；audit 前缀追加
    order = gate._store.get("WO-20260926-001")  # noqa: SLF001
    assert order is not None
    assert order["state"] == "pending" and order["owner_decision"] == DECISION_CONFIRM
    assert [a["action"] for a in order["audit_log"]] == ["order_created", "owner_confirm"]


def test_reject_archives_dead_and_keeps_row(gate: ConfirmGate) -> None:
    _seed(gate, _order())
    result = gate.decide("WO-20260926-001", DECISION_REJECT, reason="利弊不对", now=NOW)
    assert result["ok"] is True and result["state_after"] == "dead"
    order = gate._store.get("WO-20260926-001")  # noqa: SLF001
    assert order is not None and order["state"] == "dead"
    assert order["held_reason"] == "owner_rejected:利弊不对"
    # 作废归档=留痕不删：行还在 orders.jsonl
    raw = (gate.state_dir / "orders.jsonl").read_text(encoding="utf-8")
    assert "WO-20260926-001" in raw


def test_idempotent_replay_no_duplicate_event(gate: ConfirmGate) -> None:
    _seed(gate, _order())
    first = gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW)
    second = gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW + timedelta(minutes=5))
    assert second["ok"] is True and second["idempotent"] is True
    assert second["receipt"]["receipt_id"] == first["receipt"]["receipt_id"]
    assert len(gate._journal.pending()) == 1  # noqa: SLF001——零重复事件
    lines = (gate.state_dir / "confirm_decisions.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1  # 零重写零新行


def test_amend_appends_new_line_keeps_old(gate: ConfirmGate) -> None:
    _seed(gate, _order())
    gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW)
    amended = gate.decide("WO-20260926-001", DECISION_REJECT, allow_amend=True, now=NOW + timedelta(hours=1))
    assert amended["ok"] is True and amended["amend"] is True
    assert amended["state_after"] == "dead"
    lines = [
        json.loads(x) for x in (gate.state_dir / "confirm_decisions.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [x["decision"] for x in lines] == [DECISION_CONFIRM, DECISION_REJECT]  # 旧判永留=改判留痕不删
    assert len(gate._journal.pending()) == 2  # noqa: SLF001


def test_refused_request_carries_reason_and_audit_line(gate: ConfirmGate) -> None:
    _seed(gate, _order(state="dispatched"))
    result = gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW)
    assert result["ok"] is False
    assert "state_not_confirmable:dispatched" in result["error"]
    assert any(c.startswith("state_not_confirmable") for c in result["codes"])
    lines = (gate.state_dir / "confirm_decisions.jsonl").read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[0])
    assert record["outcome"] == "rejected_request"
    assert len(gate._journal.pending()) == 0  # noqa: SLF001——拒绝不发事件


def test_missing_order_id_short_circuits(gate: ConfirmGate) -> None:
    result = gate.decide("", DECISION_CONFIRM, now=NOW)
    assert result["ok"] is False and result["error"] == "missing_order_id"


def test_naive_datetime_refused(gate: ConfirmGate) -> None:
    _seed(gate, _order())
    with pytest.raises(ValueError, match="naive"):
        gate.decide("WO-20260926-001", DECISION_CONFIRM, now=datetime(2026, 9, 26, 4, 0, 0))


def test_decide_from_payload_shape(gate: ConfirmGate) -> None:
    _seed(gate, _order())
    result = gate.decide_from_payload({"order_id": "WO-20260926-001", "decision": "confirm"})
    assert result["ok"] is True and result["message"] and result["receipt"]["receipt_id"]


def test_order_store_upsert_replaces_same_id_only(gate: ConfirmGate) -> None:
    store = gate._store  # noqa: SLF001
    store.upsert(_order("WO-A"))
    store.upsert(_order("WO-B"))
    store.upsert(_order("WO-A", state="done"))
    orders = store.load_orders()
    assert len(orders) == 2
    assert next(o for o in orders if o["order_id"] == "WO-A")["state"] == "done"


def test_order_store_skips_malformed_lines(tmp_path: Path) -> None:
    """读端仍只返回可解析 dict 行（search_orders 同款语义），**但原行不得消失**（雷 3 收紧）。"""
    path = tmp_path / "ai_scheduling"
    path.mkdir(parents=True)
    original = '{"order_id": "WO-OK"}\nnot-json\n[1,2]\n'
    (path / "orders.jsonl").write_text(original, encoding="utf-8")
    store = OrderFileStore(path)
    orders = store.load_orders()
    assert [o["order_id"] for o in orders] == ["WO-OK"]
    assert store.skipped_lines == 2
    assert store.malformed_lines == [(2, "not-json"), (3, "[1,2]")]
    assert (path / "orders.jsonl").read_text(encoding="utf-8") == original  # 读侧零销毁


# ── 雷 1：并发幂等（红队 §四.1 修前=同单并发 4 次 → 4 行 decided/4 事件/4 回执）──
def test_concurrent_same_request_is_idempotent(gate: ConfirmGate) -> None:
    """12 线程同一请求 ⇒ 1 行 decided / 1 条事件 / 同一枚 receipt / audit 只追加一条。

    线程数 12 严于案卷实测的 4（覆盖 Windows os.replace 撞句柄窗口）。临界区内零重试，
    第 2..N 个拿锁者必读到已落定判 ⇒ 走幂等命中（不是"重试到不冲突"）。
    """
    _seed(gate, _order())
    threads = 12
    start = threading.Barrier(threads)
    results: list[dict[str, Any]] = []
    errors: list[BaseException] = []
    lock = threading.Lock()

    def _worker() -> None:
        start.wait()
        try:
            res = gate.decide("WO-20260926-001", DECISION_CONFIRM, reason="并发同请求", now=NOW)
        except BaseException as exc:  # noqa: BLE001  -- 并发面任何上抛都是事故，收进 errors 断言
            with lock:
                errors.append(exc)
            return
        with lock:
            results.append(res)

    pool = [threading.Thread(target=_worker) for _ in range(threads)]
    for th in pool:
        th.start()
    for th in pool:
        th.join(timeout=60)

    assert not errors, f"并发 decide 上抛：{errors!r}"
    assert len(results) == threads
    assert all(res["ok"] is True for res in results)
    receipts = {str(res["receipt"]["receipt_id"]) for res in results}
    assert len(receipts) == 1, f"并发产生 {len(receipts)} 枚回执（雷 1 复发）：{receipts}"
    decided = [row for row in json_lines(gate) if row["outcome"] == "decided"]
    assert len(decided) == 1, f"决策账 decided 行数={len(decided)}（应为 1）"
    events = [evt for evt in gate._journal.pending() if evt.kind == KIND_ORDER_CONFIRMED_DUE]  # noqa: SLF001
    assert len(events) == 1, f"事件账 {len(events)} 条 order_confirmed_due（应为 1，重复=重复派工=资金面）"
    assert events[0].payload["receipt_id"] == receipts.pop()
    order = gate._store.get("WO-20260926-001")  # noqa: SLF001
    assert order is not None
    assert [a["action"] for a in order["audit_log"]] == ["order_created", "owner_confirm"]
    assert order[SNAPSHOT_RECEIPT_FIELD] == decided[0]["receipt_id"]
    assert sum(1 for res in results if res.get("idempotent")) == threads - 1


# ── 雷 2：半写假持久化（红队 §二.23/§四.2 修前=重试被"幂等命中"掩盖成永不自愈）────
def json_lines(gate: ConfirmGate) -> list[dict[str, Any]]:
    """决策账全量行（测试内读盘对账用）。"""
    path = gate.state_dir / "confirm_decisions.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _intent_files(gate: ConfirmGate) -> list[Path]:
    return (
        sorted((gate.state_dir / "confirm_intents").glob("*.json"))
        if (gate.state_dir / "confirm_intents").exists()
        else []
    )


def test_second_write_failure_reports_and_self_heals(
    gate: ConfirmGate,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """第二写（决策账 append）倒下 ⇒ 必报 persist_failed（禁"已持久化"）＋撤桩复跑自愈。"""
    _seed(gate, _order())
    calls: list[int] = []

    def _boom(*_a: Any, **_k: Any) -> None:
        calls.append(1)
        raise OSError("打桩：决策账写不进")

    monkeypatch.setattr(gate, "_append", _boom)
    with pytest.raises(ConfirmPersistError) as caught:
        gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW)
    exc = caught.value
    assert exc.stage == "decisions"
    assert exc.order_id == "WO-20260926-001"
    assert exc.receipt_id.startswith("CFM-")
    assert calls == [1]
    # 半写凭据：意图账留盘；第一写（事件账）已在盘；第三写（快照）不得被写脏
    assert _intent_files(gate) == [gate.state_dir / "confirm_intents" / f"{exc.receipt_id}.json"]
    assert len([e for e in gate._journal.pending() if e.kind == KIND_ORDER_CONFIRMED_DUE]) == 1  # noqa: SLF001
    order = gate._store.get("WO-20260926-001")  # noqa: SLF001
    assert order is not None and SNAPSHOT_RECEIPT_FIELD not in order
    # 失败路径绝不得报告已持久化（decide 上抛=没有回执面；快照/决策账也无 decided 行）
    assert not json_lines(gate)

    monkeypatch.undo()  # 撤桩复跑=自愈（同一回执补齐，零新事件零新 decided 行）
    again = gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW + timedelta(minutes=5))
    assert again["ok"] is True and again["idempotent"] is True
    assert again["receipt"]["receipt_id"] == exc.receipt_id
    assert again.get("repaired") is True
    decided = [row for row in json_lines(gate) if row["outcome"] == "decided"]
    assert len(decided) == 1 and decided[0]["receipt_id"] == exc.receipt_id
    assert len([e for e in gate._journal.pending() if e.kind == KIND_ORDER_CONFIRMED_DUE]) == 1  # noqa: SLF001
    healed_order = gate._store.get("WO-20260926-001")  # noqa: SLF001
    assert healed_order is not None and healed_order[SNAPSHOT_RECEIPT_FIELD] == exc.receipt_id
    assert healed_order["state"] == "pending" and healed_order["owner_decision"] == DECISION_CONFIRM
    assert _intent_files(gate) == []  # 自愈完成即删意图账


def test_third_write_failure_reports_and_self_heals(
    gate: ConfirmGate,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """第三写（工单快照 upsert）倒下＝案卷原实测那一序 ⇒ 报失败；复跑自愈后快照回执落定。"""
    _seed(gate, _order())

    def _boom(*_a: Any, **_k: Any) -> None:
        raise OSError("打桩：快照写不进")

    monkeypatch.setattr(gate._store, "upsert", _boom)  # noqa: SLF001
    with pytest.raises(ConfirmPersistError) as caught:
        gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW)
    exc = caught.value
    assert exc.stage == "orders"
    assert exc.receipt_id.startswith("CFM-")
    decided_rows = [row for row in json_lines(gate) if row["outcome"] == "decided"]
    assert len(decided_rows) == 1 and decided_rows[0]["receipt_id"] == exc.receipt_id  # 事件/决策账有、快照没更
    broken = gate._store.get("WO-20260926-001")  # noqa: SLF001
    assert broken is not None and SNAPSHOT_RECEIPT_FIELD not in broken
    assert "owner_decision" not in broken
    assert _intent_files(gate) == [gate.state_dir / "confirm_intents" / f"{exc.receipt_id}.json"]

    monkeypatch.undo()
    replay = gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW + timedelta(minutes=3))
    assert replay["ok"] is True and replay["idempotent"] is True  # 同判复跑=靠意图账自愈补快照
    assert replay["receipt"]["receipt_id"] == exc.receipt_id and replay.get("repaired") is True
    healed_first = gate._store.get("WO-20260926-001")  # noqa: SLF001
    assert healed_first is not None and healed_first[SNAPSHOT_RECEIPT_FIELD] == exc.receipt_id
    assert len([row for row in json_lines(gate) if row["outcome"] == "decided"]) == 1
    assert len([e for e in gate._journal.pending() if e.kind == KIND_ORDER_CONFIRMED_DUE]) == 1  # noqa: SLF001

    again = gate.decide("WO-20260926-001", DECISION_REJECT, allow_amend=True, now=NOW + timedelta(hours=1))
    assert again["ok"] is True and again["idempotent"] is False  # 半写已自愈，本次是真改判
    assert len([row for row in json_lines(gate) if row["outcome"] == "decided"]) == 2
    assert len([e for e in gate._journal.pending() if e.kind == KIND_ORDER_CONFIRMED_DUE]) == 2  # noqa: SLF001
    healed = gate._store.get("WO-20260926-001")  # noqa: SLF001
    assert healed is not None and healed[SNAPSHOT_RECEIPT_FIELD] == again["receipt"]["receipt_id"]
    assert healed["state"] == "dead" and healed["owner_decision"] == DECISION_REJECT


def test_reconcile_heals_half_write_without_new_decision(gate: ConfirmGate, monkeypatch: pytest.MonkeyPatch) -> None:
    """自愈公开入口（事件触发型 reconciler 挂点，零定时器）：补齐缺腿、不新增决策。"""
    _seed(gate, _order())

    def _boom(*_a: Any, **_k: Any) -> None:
        raise OSError("打桩：快照写不进")

    monkeypatch.setattr(gate._store, "upsert", _boom)  # noqa: SLF001
    with pytest.raises(ConfirmPersistError) as caught:
        gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW)
    receipt = caught.value.receipt_id

    monkeypatch.undo()
    report = gate.reconcile("WO-20260926-001")
    assert report["healed"] == [receipt] and report["outstanding"] == []
    order = gate._store.get("WO-20260926-001")  # noqa: SLF001
    assert order is not None and order[SNAPSHOT_RECEIPT_FIELD] == receipt
    assert len([row for row in json_lines(gate) if row["outcome"] == "decided"]) == 1
    assert len(gate._journal.pending()) == 1  # noqa: SLF001
    replay = gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW + timedelta(minutes=9))
    assert replay["ok"] is True and replay["idempotent"] is True
    assert replay["receipt"]["receipt_id"] == receipt


def test_half_write_never_reported_as_idempotent_success(gate: ConfirmGate) -> None:
    """决策账有 decided 行、快照却缺该回执且无意图账凭据 ⇒ 必须报红，禁回 ok=True 幂等命中。"""
    _seed(gate, _order())
    # 直造案卷点名的中间态：事件/决策账已有、快照没更（且故意无意图账凭据＝自愈兜不住的事故）
    gate._append(_decided_row("CFM-HALFWRITTEN-0001"))  # noqa: SLF001
    with pytest.raises(ConfirmPersistError) as caught:
        gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW)
    assert caught.value.stage == "orders"
    assert caught.value.detail == "idempotent_hit_without_snapshot_receipt"
    assert caught.value.receipt_id == "CFM-HALFWRITTEN-0001"
    assert len([row for row in json_lines(gate) if row["outcome"] == "decided"]) == 1  # 未再多写一行
    assert len(gate._journal.pending()) == 0  # noqa: SLF001——未再多发一条事件


def _decided_row(receipt_id: str) -> ConfirmDecisionRecord:
    return ConfirmDecisionRecord(
        order_id="WO-20260926-001",
        decision=DECISION_CONFIRM,
        outcome="decided",
        receipt_id=receipt_id,
        decided_at=NOW.isoformat(),
        state_before="pending",
        state_after="pending",
    )


# ── 雷 3：审计销毁器（红队 §四.4 修前=一枚畸形行被下一次无关 upsert 静默抹掉）────
def test_malformed_line_survives_unrelated_upsert(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    state = tmp_path / "ai_scheduling"
    state.mkdir(parents=True)
    victim = '{"order_id": "ORD-VICTIM"'  # 半截写＝红队塞的那枚畸形行
    (state / "orders.jsonl").write_text(
        f'{{"order_id": "ORD-A", "state": "pending"}}\n{victim}\n{{"order_id": "ORD-B", "state": "pending"}}\n',
        encoding="utf-8",
    )
    store = OrderFileStore(state)
    with caplog.at_level(logging.WARNING, logger="zephyr.ai_layer.scheduling.confirm_gate"):
        store.upsert({"order_id": "ORD-B", "state": "done"})  # 与畸形行毫无关系的一次写

    lines = (state / "orders.jsonl").read_text(encoding="utf-8").splitlines()
    assert victim in lines, f"畸形行被 upsert 抹掉＝历史销毁（雷 3 复发）：{lines}"
    assert len(lines) == 3
    ids = [json.loads(line)["order_id"] for line in lines if line.strip() != victim]
    assert ids == ["ORD-A", "ORD-B"]
    quarantined = [
        json.loads(line) for line in (state / "orders_quarantine.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert any(rec["reason"] == "malformed_line" and rec["raw"] == victim for rec in quarantined)
    assert any(rec.levelno >= logging.ERROR and "畸形" in rec.message for rec in caplog.records), (
        "畸形行不得静默（须出声）"
    )


def test_upsert_never_drops_rows_under_concurrency(tmp_path: Path) -> None:
    """红队 §四.3 实测 8 线程 upsert 只剩 2 单＋PermissionError ⇒ 修后 16 线程 16 单全在场。"""
    state = tmp_path / "ai_scheduling"
    store = OrderFileStore(state)
    threads = 16
    start = threading.Barrier(threads)
    errors: list[BaseException] = []
    guard = threading.Lock()

    def _worker(index: int) -> None:
        start.wait()
        try:
            store.upsert(_order(f"WO-CONC-{index:02d}"))
        except BaseException as exc:  # noqa: BLE001  -- 并发写任何上抛都是事故
            with guard:
                errors.append(exc)

    pool = [threading.Thread(target=_worker, args=(i,)) for i in range(threads)]
    for th in pool:
        th.start()
    for th in pool:
        th.join(timeout=90)

    assert not errors, f"并发 upsert 上抛：{errors!r}"
    present = {str(order.get("order_id") or "") for order in store.load_orders()}
    assert present == {f"WO-CONC-{i:02d}" for i in range(threads)}


def test_upsert_keeps_duplicate_order_id_rows(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """同 order_id 多行＝异常史 ⇒ 只替换首行、余行原样保留＋留痕报红（禁静默合档）。"""
    state = tmp_path / "ai_scheduling"
    state.mkdir(parents=True)
    dup = '{"order_id": "WO-DUP", "state": "pending", "tag": "old"}'
    (state / "orders.jsonl").write_text(f'{dup}\n{dup}\n{{"order_id": "WO-OTHER"}}\n', encoding="utf-8")
    store = OrderFileStore(state)
    with caplog.at_level(logging.WARNING, logger="zephyr.ai_layer.scheduling.confirm_gate"):
        store.upsert({"order_id": "WO-DUP", "state": "done", "tag": "new"})

    lines = (state / "orders.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3, f"重复行被合档＝行丢失（雷 3 口径）：{lines}"
    assert lines[0] == '{"order_id": "WO-DUP", "state": "done", "tag": "new"}'
    assert lines[1] == dup and lines[2] == '{"order_id": "WO-OTHER"}'
    assert any(rec.levelno >= logging.ERROR for rec in caplog.records)
    quarantined = (state / "orders_quarantine.jsonl").read_text(encoding="utf-8")
    assert "duplicate_order_id_rows" in quarantined


def test_gate_lock_is_reentrant_and_shared_per_state_dir(tmp_path: Path) -> None:
    """串化闸：同目录同一实例（decide 持闸内再 upsert 不得自死锁）＋跨实例共享互斥域。"""
    from zephyr.ai_layer.scheduling.confirm_gate import gate_lock_for

    state = tmp_path / "ai_scheduling"
    assert gate_lock_for(state) is gate_lock_for(str(state))
    lock = gate_lock_for(state)
    with lock():
        with lock():  # 同线程重入：二次不得抢字节锁（Windows 同档二次 LockFile=自死锁）
            pass
    gate = ConfirmGate(state)
    _seed(gate, _order())
    assert gate.decide("WO-20260926-001", DECISION_CONFIRM, now=NOW)["ok"] is True  # 走完整重入路径
    assert (state / ("orders.jsonl" + ".gate.lock")).exists()
