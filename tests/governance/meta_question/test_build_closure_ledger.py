"""闭环台账生成器测试（含"能红"用例——判通过的尺必须先证明它会红）。

覆盖四件事：
1. 同问多行（改判追加）必须取 created_at 最新一行——本用例经变异测试校准：
   假账本真按 SQL 声明方向排序并模拟 DISTINCT ON 取首行，故把 desc 改成 asc
   时必红（否则就是静默成功尺，本战役已被此类尺烧过四次）。
2. 计数只从注入的假账本派生（生成器内零硬编码数字）。
3. 未知项必须可见：open 问无工单也无案卷时 unknown 计数非零（禁乐观清零）。
4. 坏案卷不许静默消失——必须留 _parse_error 痕迹。
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "scripts" / "governance" / "meta_question" / "build_closure_ledger.py"


def _load():
    spec = importlib.util.spec_from_file_location("mcl_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class _FakeCursor:
    """最小 PG 语义仿真：按 SQL 声明的 ORDER BY 方向排序 + 模拟 DISTINCT ON。"""

    def __init__(self, replies: dict[str, list]):
        self._replies = replies
        self._rows: list = []

    def execute(self, sql, params=None):
        key = next((k for k in self._replies if k in sql), None)
        assert key is not None, f"未预置的 SQL 形态：{sql[:80]}"
        rows = list(self._replies[key])
        order = re.search(r"order by q_id,\s*created_at\s+(asc|desc)", sql, re.I)
        if order:
            rows.sort(key=lambda r: r[2], reverse=order.group(1).lower() == "desc")
            if "distinct on (q_id)" in sql:
                seen: set[str] = set()
                deduped = []
                for r in rows:
                    if r[0] not in seen:
                        seen.add(r[0])
                        deduped.append(r)
                rows = deduped
        self._rows = rows

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def close(self):
        pass


class _FakeConn:
    def __init__(self, replies: dict[str, list]):
        self._replies = replies
        self.closed = False

    def cursor(self):
        return _FakeCursor(self._replies)

    def close(self):
        self.closed = True


def _replies(rows_exam: list, rows_q: list) -> dict[str, list]:
    return {
        "distinct on (q_id)": rows_exam,
        "select q_id, layer, title, exam_plan": rows_q,
        "select max(created_at)": [["2026-09-24 00:00:00", len(rows_exam)]],
        "from meta_question.meta_question": [[len({r[0] for r in rows_q})]],
    }


def _plan():
    return {"threshold": "IC>0.02 且 t>2", "criterion": "秩 IC"}


def test_latest_row_wins_over_rejudged_append():
    """同问两行：旧 fail + 新 pass → 必须计 pass；反向取旧行即红。"""
    mcl = _load()
    old = json.dumps({"outcome": "fail", "fail_type": "infra"})
    new = json.dumps({"outcome": "pass", "fail_type": None})
    replies = _replies(
        [
            ("PQ-0001", old, "2026-09-24 01:00:00"),
            ("PQ-0001", new, "2026-09-24 02:00:00"),
            ("PQ-0002", old, "2026-09-24 01:00:00"),
        ],
        [("PQ-0001", "L1", "t", _plan()), ("PQ-0002", "L1", "t", _plan())],
    )
    doc = mcl.build(conn_factory=lambda: _FakeConn(replies))
    assert doc["items"]["PQ-0001"]["outcome"] == "pass", "改判追加未被取最新行"
    assert doc["stats"]["outcome_dist"]["pass"] == 1
    assert doc["stats"]["outcome_dist"]["fail"] == 1
    assert doc["stats"]["questions"] == 2, "同问多行不得重复计问数"


def test_counts_are_derived_not_hardcoded():
    mcl = _load()
    rows_q = [(f"PQ-{i:04d}", "L1", "t", _plan()) for i in range(1, 8)]
    rows_exam = [(q[0], json.dumps({"outcome": "pass"}), "2026-09-24 01:00:00") for q in rows_q]
    doc = mcl.build(conn_factory=lambda: _FakeConn(_replies(rows_exam, rows_q)))
    assert doc["stats"]["questions"] == 7
    assert doc["stats"]["outcome_dist"]["pass"] == 7


def test_open_item_without_any_evidence_is_visible(tmp_path, monkeypatch):
    """无工单且无案卷的 open 问必须计入 unknown 面（禁乐观清零）。"""
    mcl = _load()
    replies = _replies(
        [("PQ-9999", json.dumps({"outcome": "insufficient"}), "2026-09-24 01:00:00")],
        [("PQ-9999", "L1", "t", _plan())],
    )
    monkeypatch.setattr(mcl, "BUILD_DIR", tmp_path)
    monkeypatch.setattr(mcl, "RESULTS_DIR", tmp_path)
    doc = mcl.build(conn_factory=lambda: _FakeConn(replies))
    assert doc["stats"]["open_without_any_evidence"] == 1
    assert doc["items"]["PQ-9999"]["casefiles"] == []


def test_corrupt_casefile_surfaces_instead_of_vanishing(tmp_path, monkeypatch):
    mcl = _load()
    (tmp_path / "WO-BAD.yaml").write_text("a: [unclosed\n  b: }\n", encoding="utf-8")
    (tmp_path / "WO-GOOD.yaml").write_text("closes: PQ-0018\n", encoding="utf-8")
    monkeypatch.setattr(mcl, "BUILD_DIR", tmp_path)
    out = mcl.load_casefiles()
    assert set(out) == {"WO-BAD.yaml", "WO-GOOD.yaml"}, "坏案卷被静默丢弃"


def test_watermark_closes_connection():
    mcl = _load()
    conn = _FakeConn(_replies([], []))
    mark = mcl._watermark(conn)
    assert conn.closed is True
    assert "exam_result_rows" in mark


def test_workorder_heading_parse_finds_qids():
    mcl = _load()
    if not mcl.WORKORDER_MD.exists():
        pytest.skip("工单总册不在盘（worktree 环境）")
    wos = mcl.parse_workorders()
    assert wos, "WORKORDER_MASTER 未解析出任何工单——解析器失配即红"
    assert all(v["q_ids"] for v in wos.values()), "存在零问号归属的工单"
