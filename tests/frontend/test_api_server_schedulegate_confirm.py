# [MODULE] tests.frontend.test_api_server_schedulegate_confirm
# [DOMAIN] D_FRONTEND
# [TTL] permanent
"""仪表盘一键拍板路由接通验收（C9 确认态落点=confirm_gate 三落点账）。

判据面：①confirm 真落账（回执+决策账+工单快照三处，非假持久化）；②幂等（同判再请求
零新行）；③**审计主体与改判旗不经 body**（confirm_gate「接线前置①」——本路由恒
actor=schedulegate_ui / allow_amend=False，任何自称他人主体或自开改判的入站报文必失效）；
④半写如实报 ok:false 带 stage，绝不回 ok:true。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import zephyr.ai_layer.scheduling.confirm_gate as confirm_gate  # noqa: E402
import zephyr.frontend.dashboard.api_server as api_server  # noqa: E402

ORDER_ID = "ORD-ROUTE-001"


@pytest.fixture()
def state_dir(tmp_path: Path, monkeypatch) -> Path:
    """三落点目录重定向到 tmp_path（测试隔离红线：禁写 .runtime 生产账）。"""
    monkeypatch.setattr(confirm_gate, "DEFAULT_STATE_DIR", tmp_path)
    store = confirm_gate.OrderFileStore(tmp_path)
    store.upsert({"order_id": ORDER_ID, "owner_gate": True, "state": "pending"})
    return tmp_path


def _ledger(state: Path) -> list[dict]:
    path = state / confirm_gate.DECISIONS_NAME
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_confirm_lands_receipt_and_decision_row(state_dir: Path) -> None:
    res = api_server.schedulegate_confirm({"order_id": ORDER_ID, "decision": "confirm"})
    assert res["ok"] is True, res
    assert res["receipt"]["receipt_id"]
    assert res["receipt"]["decision"] == "confirm"
    rows = _ledger(state_dir)
    assert len(rows) == 1
    assert rows[0]["outcome"] == "decided"


def test_same_decision_twice_is_idempotent_zero_new_row(state_dir: Path) -> None:
    first = api_server.schedulegate_confirm({"order_id": ORDER_ID, "decision": "confirm"})
    second = api_server.schedulegate_confirm({"order_id": ORDER_ID, "decision": "confirm"})
    assert second["ok"] is True and second.get("idempotent") is True, second
    assert second["receipt"]["receipt_id"] == first["receipt"]["receipt_id"]
    assert len(_ledger(state_dir)) == 1


def test_body_cannot_forge_audit_actor(state_dir: Path) -> None:
    """body 自称他人主体必失效——审计账里只能有服务端钉死的那一枚。"""
    res = api_server.schedulegate_confirm({"order_id": ORDER_ID, "decision": "confirm", "actor": "zhangsan"})
    assert res["ok"] is True
    assert [r.get("actor") for r in _ledger(state_dir)] == [api_server._SCHEDULEGATE_UI_ACTOR]


def test_body_cannot_open_amend_gate(state_dir: Path) -> None:
    """已 confirm 的单，报文自开 allow_amend 走相反判必被拒（改判须经显式调用面）。"""
    api_server.schedulegate_confirm({"order_id": ORDER_ID, "decision": "confirm"})
    res = api_server.schedulegate_confirm({"order_id": ORDER_ID, "decision": "reject", "allow_amend": True})
    assert res["ok"] is False, res
    rows = _ledger(state_dir)
    assert len(rows) == 2  # 拒判本身留痕一行（audit 链不删）
    assert [r["outcome"] for r in rows] == ["decided", "rejected_request"]
    assert "decision_conflict" in rows[1]["codes"][0]
    order = confirm_gate.OrderFileStore(state_dir).get(ORDER_ID)
    assert str(order.get("state")) == confirm_gate.CONFIRMABLE_STATE  # 工单态未被改判


def test_unknown_order_and_off_vocab_decision_refused(state_dir: Path) -> None:
    missing = api_server.schedulegate_confirm({"order_id": "ORD-NOPE", "decision": "confirm"})
    assert missing["ok"] is False
    off_vocab = api_server.schedulegate_confirm({"order_id": ORDER_ID, "decision": "yolo"})
    assert off_vocab["ok"] is False


def test_persist_half_write_is_reported_not_faked(state_dir: Path, monkeypatch) -> None:
    """半写上抛 ConfirmPersistError 时路由必报 ok:false+stage（禁把失败写成成功）。"""

    def _boom(*args, **kwargs):
        raise confirm_gate.ConfirmPersistError("journal leg down", stage="journal", order_id=ORDER_ID)

    monkeypatch.setattr(confirm_gate.ConfirmGate, "decide", _boom)
    res = api_server.schedulegate_confirm({"order_id": ORDER_ID, "decision": "confirm"})
    assert res["ok"] is False
    assert "stage=journal" in res["error"]
    assert _ledger(state_dir) == []
