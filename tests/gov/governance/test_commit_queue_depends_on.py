# [MODULE] tests.gov.governance.test_commit_queue_depends_on
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; scripts.commit_queue
# [CONSUMERS] 总统筹增补令P1 质量守卫：depends_on 顶层序列化（红证）+drain 前置态校验（未 done 挂起/done 放行）
# [INVARIANTS] 全部用例 tmp 队列（零主区）；红证判据=Owner 原文「带依赖入队的袋 JSON 必须含 depends_on 字段」
# [MODIFY-GUARD] 新建 2026-10-10 st-regsolo-20261010（增补令P1 随批测试，tests/ 豁免 token）
# [TTL] permanent
"""commit_queue depends_on 守卫（总统筹 2026-10-10 增补令P1）。

病灶（-0015/-0016 实证）：--depends-on 声明只入 meta.depends_on，顶层 item["depends_on"]
恒 None——读顶层字段的消费方失明，依赖序旗标不可信，后继袋在前置未落地时被 drain 撞真门。
治本：①顶层字段序列化；②_pick_head 前置态校验（前置未 done 压队尾挂起，done 即放行；
无依赖恒 satisfied 零行为变更）。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from scripts import commit_queue as cq  # noqa: E402


def _make_queue(tmp_path: Path) -> Path:
    qroot = tmp_path / "commit_queue"
    qroot.mkdir(parents=True)
    return qroot


def test_bag_json_contains_top_level_depends_on(tmp_path, monkeypatch):
    """红证（Owner 原文）：带依赖入队的袋 JSON 必须含 depends_on 字段（此前只入 meta，顶层恒 None）。"""
    monkeypatch.setattr(cq, "resolve_queue_root", lambda q=None: Path(q))
    qroot = _make_queue(tmp_path)
    item = cq.enqueue_item(
        "st-dep-test",
        "msg: depends probe",
        [("docs/x/probe.md", b"1")],
        queue_root=qroot,
        options=cq.EnqueueOptions(depends_on=["q-20261010-st-other-0014"]),
    )
    bag = json.loads((qroot / "pending" / f"{item['qid']}.json").read_text(encoding="utf-8"))
    assert bag.get("depends_on") == ["q-20261010-st-other-0014"], "顶层字段必须序列化（红证）"
    assert bag["meta"]["depends_on"] == ["q-20261010-st-other-0014"], "meta 面既有消费方保持兼容"


def test_bag_without_deps_has_empty_top_level(tmp_path, monkeypatch):
    monkeypatch.setattr(cq, "resolve_queue_root", lambda q=None: Path(q))
    qroot = _make_queue(tmp_path)
    item = cq.enqueue_item("st-dep-test", "msg: plain", [("docs/x/probe.md", b"1")], queue_root=qroot)
    bag = json.loads((qroot / "pending" / f"{item['qid']}.json").read_text(encoding="utf-8"))
    assert bag.get("depends_on") == []


def test_pick_head_holds_until_predecessor_done(tmp_path, monkeypatch):
    """drain 拾取前置态校验：前置未 done → 后继挂起不拾取；前置落 done → 放行。"""
    monkeypatch.setattr(cq, "resolve_queue_root", lambda q=None: Path(q))
    qroot = _make_queue(tmp_path)
    pre = cq.enqueue_item("st-dep-pre", "msg: pre", [("docs/p.md", b"1")], queue_root=qroot)
    suc = cq.enqueue_item(
        "st-dep-suc",
        "msg: suc",
        [("docs/s.md", b"2")],
        queue_root=qroot,
        options=cq.EnqueueOptions(depends_on=[pre["qid"]]),
    )
    pre_path = qroot / "pending" / f"{pre['qid']}.json"
    suc_path = qroot / "pending" / f"{suc['qid']}.json"

    head, _lane = cq._pick_head([pre_path, suc_path])
    assert head is not None and head.name == f"{pre['qid']}.json", "前置未 done：后继必须让位（前置先出）"
    head2, _ = cq._pick_head([suc_path])
    assert head2 is None, "后继独占队首且前置未 done → 本轮不拾取（挂起）"

    # 前置落 done → 后继放行
    done_dir = qroot / "done"
    done_dir.mkdir(exist_ok=True)
    (done_dir / f"{pre['qid']}.json").write_text(json.dumps({"qid": pre["qid"], "state": "done"}), encoding="utf-8")
    head3, _ = cq._pick_head([suc_path])
    assert head3 is not None and head3.name == f"{suc['qid']}.json", "前置 done 后放行"


def test_no_deps_never_blocked(tmp_path, monkeypatch):
    """无依赖件恒 satisfied（零行为变更——存量袋面全部不受扰）。"""
    monkeypatch.setattr(cq, "resolve_queue_root", lambda q=None: Path(q))
    qroot = _make_queue(tmp_path)
    plain = cq.enqueue_item("st-dep-plain", "msg: plain", [("docs/p.md", b"1")], queue_root=qroot)
    p = qroot / "pending" / f"{plain['qid']}.json"
    head, _ = cq._pick_head([p])
    assert head is not None and head.name == f"{plain['qid']}.json"
