# [TTL] permanent
"""belt 死信水位线测试（st-chiefc-20261009 A-11）。

契约：守护重启不再全量重放存量死信（水位预载→只记真新增→扫后落盘）；
归档收缩后水位自然收缩；水位损坏 fail-open（多记一轮不丢事件）。
能红证据：摘掉预载（模拟旧实现）→ 第二次全量重放必红。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))  # noqa: E402

from zephyr.gov_enforcement.rule_bridge import commit_belt_daemon as belt  # noqa: E402


@pytest.fixture()
def queue_root(tmp_path, monkeypatch):
    qroot = tmp_path / "commit_queue"
    dead = qroot / "dead"
    dead.mkdir(parents=True)
    monkeypatch.setattr(belt, "_queue_root", lambda _root=None: qroot)
    return qroot


def _make_dead(qroot: Path, names: list[str]) -> None:
    for i, name in enumerate(names):
        (qroot / "dead" / f"{name}.json").write_text(
            json.dumps({"qid": name, "session_id": f"s{i}", "dead_reason": "test"}),
            encoding="utf-8",
        )


def test_first_run_logs_all_then_watermark_persists(queue_root):
    _make_dead(queue_root, ["q-a", "q-b"])
    seen = belt._load_seen_watermark(queue_root.parent)
    assert seen == set()
    n1 = belt._ledger_dead_letters(queue_root.parent, seen)
    assert n1 == 2
    belt._save_seen_watermark(queue_root.parent, seen)
    # 重启：新进程新集合，从水位预载
    seen2 = belt._load_seen_watermark(queue_root.parent)
    assert seen2 == {"q-a.json", "q-b.json"}
    n2 = belt._ledger_dead_letters(queue_root.parent, seen2)
    assert n2 == 0, "重启不得重放存量（旧实现 n2==2）"


def test_new_dead_letter_after_restart_logs_only_increment(queue_root):
    _make_dead(queue_root, ["q-a"])
    seen = set()
    belt._ledger_dead_letters(queue_root.parent, seen)
    belt._save_seen_watermark(queue_root.parent, seen)
    seen2 = belt._load_seen_watermark(queue_root.parent)
    _make_dead(queue_root, ["q-new"])
    n = belt._ledger_dead_letters(queue_root.parent, seen2)
    assert n == 1, "只记真新增"


def test_watermark_shrinks_after_archive(queue_root):
    _make_dead(queue_root, ["q-a", "q-b"])
    seen = set()
    belt._ledger_dead_letters(queue_root.parent, seen)
    belt._save_seen_watermark(queue_root.parent, seen)
    # q-a 被归档清偿（dead/ 移除）
    (queue_root / "dead" / "q-a.json").unlink()
    seen2 = belt._load_seen_watermark(queue_root.parent)
    belt._ledger_dead_letters(queue_root.parent, seen2)
    belt._save_seen_watermark(queue_root.parent, seen2)
    assert belt._load_seen_watermark(queue_root.parent) == {"q-b.json"}, "水位随归档自然收缩"
    # 同名 qid 再次死亡=新事件，须重记
    _make_dead(queue_root, ["q-a"])
    seen3 = belt._load_seen_watermark(queue_root.parent)
    assert belt._ledger_dead_letters(queue_root.parent, seen3) == 1


def test_corrupt_watermark_fail_open(queue_root):
    wm = queue_root / "belt_seen_dead.watermark.json"
    wm.write_text("{broken", encoding="utf-8")
    assert belt._load_seen_watermark(queue_root.parent) == set(), "损坏水位 fail-open=空集"
