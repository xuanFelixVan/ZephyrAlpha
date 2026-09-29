# [TTL] permanent
# [STARTUP] manual
# [CONSUMERS] commit_queue 死信摘除出口（红证 canary，pytest 收集执行）
"""红证 canary（波 1B 包 1.7b / R-L）：失败袋摘除后，其后各袋必须按新组合继续前进。

判据出处：`docs/_working/total_command_closeout/10_wave_plan.md:55`
（红证=造一袋必死者，改后其后各袋必须落地或各自具名死因）。
全部在 tmp_path 沙盘里演，**绝不触碰生产队列根**（.runtime/commit_queue 一个字节不写）。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.commit_queue as cq

_DEAD_PATH = "src/zephyr/delta.py"
_OTHER_PATH = "src/zephyr/other.py"


def _mk_bag(root: Path, qid: str, *, paths: list[str], session: str = "can17b") -> None:
    """直写 pending 袋（绕 enqueue，纯沙盘）。"""
    (root / "pending").mkdir(parents=True, exist_ok=True)
    item = {
        "qid": qid,
        "session_id": session,
        "created_at": "2026-09-26T00:00:00+00:00",
        "branch": "dev",
        "base_head": None,
        "files": [{"path": p, "blob_sha256": "0" * 64, "blob_ref": "", "action": "modify"} for p in paths],
        "message": f"sandbox bag {qid}",
        "meta": {},
    }
    (root / "pending" / f"{qid}.json").write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8", newline="\n")


@pytest.fixture()
def sandbox(tmp_path: Path) -> Path:
    root = tmp_path / "q"
    cq._ensure_dirs(root)
    return root


def _landing(dead_qids: set[str]):
    def landing(item: dict, queue_root: Path) -> cq.LandingResult:
        if item["qid"] in dead_qids:
            return cq.LandingResult(ok=False, reason="CREATE-GUARD: 沙盘必死件（缺 creation_token）")
        return cq.LandingResult(ok=True, landed_id=f"landed-{item['qid']}")

    return landing


def _read(root: Path, state: str, qid: str) -> dict:
    return json.loads((root / state / f"{qid}.json").read_text(encoding="utf-8"))


def test_chain_survives_a_dying_bag_and_successors_rebuild(sandbox: Path) -> None:
    """正向+红证：一袋必死，其后各袋必须各自落地（链不停摆）且被标记按新组合重跑。"""
    _mk_bag(sandbox, "q-20260926-can17b-0001", paths=[_DEAD_PATH])
    _mk_bag(sandbox, "q-20260926-can17b-0002", paths=[_DEAD_PATH])  # 与死者同路径=叠在它上面
    _mk_bag(sandbox, "q-20260926-can17b-0003", paths=[_OTHER_PATH])  # 无组合关系

    stats = cq.drain_queue(sandbox, landing=_landing({"q-20260926-can17b-0001"}), max_items=10)

    assert stats["dead"] == 1
    assert stats["done"] == 2, f"后继袋未继续前进＝整链停摆复发：{stats}"
    assert stats.get("successors_rebuilt", 0) == 1, f"后继袋未按新组合重建：{stats}"
    # 死者之后的同路径袋确实走过一次基底重校验（stale 视图被消费）
    rebuilt = _read(sandbox, "done", "q-20260926-can17b-0002")
    assert (rebuilt.get("meta") or {}).get("stale_cleared_at")
    # 与死者无组合关系的袋不受牵连（保守判据，不扩大动作面）
    untouched = _read(sandbox, "done", "q-20260926-can17b-0003")
    assert not (untouched.get("meta") or {}).get("stale_cleared_at")


def test_poison_eviction_shares_the_same_exit(sandbox: Path, monkeypatch) -> None:
    """与 B5 毒药熔断合并：attempts 耗尽摘除走同一封袋+重建出口。

    注：B5 的"队首让位"会把毒药件惩罚到末位（`_pick_head` 未来时刻偏移），所以真实
    drain 里它身后已无袋——本测因此分两段取证：①drain 面证明不再白耗 landing 且链不停；
    ②封袋出口面直接证明同一条 `_seal_dead_letter` 会重建其后各袋。
    """
    monkeypatch.setattr(cq, "_attempts_backoff_enabled", lambda: True)
    _mk_bag(sandbox, "q-20260926-can17b-0001", paths=[_DEAD_PATH])
    _mk_bag(sandbox, "q-20260926-can17b-0002", paths=[_DEAD_PATH])
    poison = sandbox / "pending" / "q-20260926-can17b-0001.json"
    item = json.loads(poison.read_text(encoding="utf-8"))
    item["attempts"] = cq._ATTEMPTS_DEAD_THRESHOLD  # B5 真字段=袋顶层 attempts（非 meta）
    poison.write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8", newline="\n")

    called: list[str] = []

    def landing(item: dict, queue_root: Path) -> cq.LandingResult:
        called.append(item["qid"])
        return cq.LandingResult(ok=True, landed_id=f"landed-{item['qid']}")

    stats = cq.drain_queue(sandbox, landing=landing, max_items=10)
    assert "q-20260926-can17b-0001" not in called, "毒药件被重复消耗 landing＝B5 语义退化"
    assert stats["dead"] == 1
    assert stats["done"] == 1, "毒药件身后无袋却整链不前进＝停摆复发"
    dead = _read(sandbox, "dead", "q-20260926-can17b-0001")
    assert dead.get("owner_session") and dead.get("first_dead_at") and dead.get("dead_signature")

    # ②封袋出口面：同一函数在"身后果然有袋"的形态下必须重建后继袋
    _mk_bag(sandbox, "q-20260926-can17b-0003", paths=[_DEAD_PATH])
    rebuilt = cq._seal_dead_letter(sandbox, dead)
    assert rebuilt == ["q-20260926-can17b-0003"], f"摘除出口未接后继重建＝合并实现未落地（{rebuilt}）"


def test_canary_mutation_disabling_rebuild_turns_ruler_red(sandbox: Path, monkeypatch) -> None:
    """人为改错→尺必红：把后继重建出口摘掉（模拟回归），同链判据必须失配。"""
    monkeypatch.setattr(cq, "_rebuild_successors_after_eviction", lambda *_a, **_kw: [])
    _mk_bag(sandbox, "q-20260926-can17b-0001", paths=[_DEAD_PATH])
    _mk_bag(sandbox, "q-20260926-can17b-0002", paths=[_DEAD_PATH])
    stats = cq.drain_queue(sandbox, landing=_landing({"q-20260926-can17b-0001"}), max_items=10)
    assert stats.get("successors_rebuilt", 0) == 0, "改动失效检测：尺对'重建被摘掉'不敏感＝假绿"
    # 同一条链的判据在此处必须红（后继袋未被标记 → 无 stale_cleared_at 痕迹）
    rebuilt = _read(sandbox, "done", "q-20260926-can17b-0002")
    assert not (rebuilt.get("meta") or {}).get("stale_cleared_at")


def test_predecessors_are_never_marked(sandbox: Path) -> None:
    """只重建'其后各袋'：排在死者之前的袋与本次摘除无组合关系，绝不牵连。"""
    _mk_bag(sandbox, "q-20260926-can17b-0000", paths=[_DEAD_PATH])
    _mk_bag(sandbox, "q-20260926-can17b-0001", paths=[_DEAD_PATH])
    marked = cq._rebuild_successors_after_eviction(
        sandbox, {"qid": "q-20260926-can17b-0001", "files": [{"path": _DEAD_PATH}]}
    )
    assert marked == []
