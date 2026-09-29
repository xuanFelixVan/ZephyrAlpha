# [TTL] permanent
# [STARTUP] manual
# [CONSUMERS] commit_queue 死信封袋与复发熔断（红证 canary，pytest 收集执行）
"""红证 canary（波 1B 包 1.7c / R-M）：每封死信必落属主与首死时，同签名复发 3 次即熔断。

判据出处：`docs/_working/total_command_closeout/10_wave_plan.md:56`
（红证=新死信 24h 内可查到属主与归因签名）；对标 `review_ext_ci_and_mergequeue.md`
3-1（Google Build Cop：死信是"当天必须有人中断工作去修的活信号"，regardless of who
breaks them）与同册 §"重试有上限/禁止无限期隔离"。
全部在 tmp_path 沙盘里演，绝不触碰生产队列根。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.commit_queue as cq

_REASON = "CREATE-GUARD: 新建件 src/zephyr/x.py 未登记 creation_token"
#: 签名前缀 = 真源三分类现读（禁把 classify 结果抄成常量，防分类表漂移）
_FAMILY = cq.classify_dead_reason(_REASON)
_SIGNATURE = f"{_FAMILY}:CREATE-GUARD"


@pytest.fixture()
def sandbox(tmp_path: Path) -> Path:
    root = tmp_path / "q"
    cq._ensure_dirs(root)
    return root


def _dead_item(qid: str, *, session: str = "can17c", reason: str = _REASON) -> dict:
    return {
        "qid": qid,
        "session_id": session,
        "created_at": "2026-09-26T00:00:00+00:00",
        "base_head": None,
        "files": [{"path": "src/zephyr/x.py", "blob_sha256": "0" * 64, "action": "modify"}],
        "message": f"sandbox {qid}",
        "meta": {},
        "dead_at": "2026-09-26T01:00:00+00:00",
        "dead_reason": reason,
    }


def _seal(root: Path, item: dict) -> dict:
    cq._seal_dead_letter(root, item)
    (root / "dead" / f"{item['qid']}.json").write_text(
        json.dumps(item, ensure_ascii=False), encoding="utf-8", newline="\n"
    )
    return item


def test_new_dead_letter_carries_owner_and_signature(sandbox: Path) -> None:
    """属主制最小可用面：一封新死信当场可查 owner_session / first_dead_at / 归因签名。"""
    sealed = _seal(sandbox, _dead_item("q-20260926-can17c-0001"))
    assert sealed["owner_session"] == "can17c"
    assert sealed["first_dead_at"] == "2026-09-26T01:00:00+00:00"
    assert sealed["dead_signature"] == _SIGNATURE
    assert sealed["dead_letter_family"] == cq.classify_dead_reason(_REASON)
    assert sealed["prescription"] == cq.dead_letter_prescription(_REASON)
    # 落盘可查（不是只活在内存里）
    on_disk = json.loads((sandbox / "dead" / "q-20260926-can17c-0001.json").read_text(encoding="utf-8"))
    assert on_disk["owner_session"] == "can17c" and on_disk["first_dead_at"]


def test_recurrence_fuse_trips_on_third_same_signature(sandbox: Path) -> None:
    """同签名第 3 封 ⇒ 熔断 + 升级根因工序单（含属主集合与首死时）。"""
    first = _seal(sandbox, _dead_item("q-20260926-can17c-0001"))
    assert not first.get("recurrence_fused")
    second = _seal(sandbox, _dead_item("q-20260926-can17c-0002", session="can17c-b"))
    assert not second.get("recurrence_fused")
    third = _seal(sandbox, _dead_item("q-20260926-can17c-0003", session="can17c-c"))
    assert third.get("recurrence_fused") is True
    assert third["recurrence_count"] == 3
    ticket_path = sandbox / third["root_cause_ticket"]
    assert ticket_path.exists()
    ticket = json.loads(ticket_path.read_text(encoding="utf-8"))
    assert ticket["root_cause_required"] is True
    assert ticket["signature"] == _SIGNATURE
    assert ticket["first_dead_at"] == first["first_dead_at"]
    assert set(ticket["owner_sessions"]) == {"can17c", "can17c-b", "can17c-c"}


def test_fused_bag_rejects_blind_requeue(sandbox: Path, tmp_path: Path) -> None:
    """红证：熔断裂上的袋再直调 requeue 必被拒（禁继续无脑重投），--force 才留痕越过。"""
    wt = tmp_path / "wt"
    (wt / "src" / "zephyr").mkdir(parents=True)
    (wt / "src" / "zephyr" / "x.py").write_text("print('x')\n", encoding="utf-8", newline="\n")
    _seal(sandbox, _dead_item("q-20260926-can17c-0007"))
    _seal(sandbox, _dead_item("q-20260926-can17c-0008"))
    third = _seal(sandbox, _dead_item("q-20260926-can17c-0009"))
    assert third["recurrence_fused"] is True
    with pytest.raises(cq.RequeueError) as boom:
        cq.requeue_dead_item("q-20260926-can17c-0009", queue_root=sandbox, worktree_root=wt)
    assert "复发熔断" in str(boom.value)
    assert boom.value.details["root_cause_ticket"] == third["root_cause_ticket"]
    assert list((sandbox / "pending").glob("q-*.json")) == []  # 熔断件绝不偷渡回队列


def test_first_dead_at_survives_the_requeue_chain(sandbox: Path, tmp_path: Path) -> None:
    """首死时跨链继承：重投后的新袋再死，first_dead_at 不得回退到重投时刻。"""
    sealed = _seal(sandbox, _dead_item("q-20260926-can17c-0020"))
    item = _dead_item("q-20260926-can17c-0021", reason=_REASON)
    item["meta"] = {"requeue_lineage": {"first_dead_at_prev": sealed["first_dead_at"], "requeued_at": ""}}
    item["dead_at"] = "2026-09-27T09:00:00+00:00"
    cq._seal_dead_letter_attribution(item)
    assert item["first_dead_at"] == sealed["first_dead_at"]


def test_canary_mutation_disabling_attribution_turns_ruler_red(sandbox: Path) -> None:
    """人为改错→尺必红：摘掉封袋函数（模拟回归），属主/签名三字段当场查无。"""
    item = _dead_item("q-20260926-can17c-0099")
    # 故意不调用 _seal_dead_letter：等价于封袋出口被摘
    assert "owner_session" not in item and "first_dead_at" not in item and "dead_signature" not in item
    # 尺本身仍敏感：补一次封袋，三字段立刻可查
    cq._seal_dead_letter_attribution(item)
    assert item["owner_session"] == "can17c"
    assert item["dead_signature"] == _SIGNATURE


def test_signature_distinguishes_different_root_causes(sandbox: Path) -> None:
    """不同签名不得互相顶数（否则熔断会误伤无辜袋）。"""
    _seal(sandbox, _dead_item("q-20260926-can17c-0100"))
    other = _seal(sandbox, _dead_item("q-20260926-can17c-0101", reason="COMMIT_SCOPE: 跨域连坐"))
    assert other["dead_signature"].endswith(":COMMIT_SCOPE")
    assert other["recurrence_count"] == 1
    third_same = _seal(sandbox, _dead_item("q-20260926-can17c-0102", reason="COMMIT_SCOPE: 又一次跨域"))
    assert third_same["recurrence_count"] == 2, "同签名计数被异签名污染"
