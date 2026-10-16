"""CAMPAIGN-GOAL-BLOCK 门测试（Q7，裁定#516）——纯注入零库。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from zephyr.gov_enforcement.commit_gates.goal.campaign_goal_block_gate import (  # noqa: E402
    _goal_block_ok,
    make_campaign_goal_block_gate,
)

GOOD = """---
ttl: task_bound
session: st-x-20261013
goal_block:
  goal_statement: 出信号先行
  output_contract: 微信号
  exam_ref: 事件研究
  campaign_ref: st-x-20261013
---

# 开班令
"""

NO_BLOCK = """---
ttl: task_bound
session: st-x-20261013
---

# 开班令·某某施工令
"""

EXEMPT = """---
ttl: task_bound
goal_block_exempt: 收班归档件无新目标面（理由满十字留痕）
---

# 开班令收班册
"""


class _FakeGit:
    def __init__(self, added: set[str]):
        self._added = added

    def run_git(self, args):
        class R:
            returncode = 0
            stdout = "\n".join(self._added)

        return R()


@pytest.fixture()
def gate():
    return make_campaign_goal_block_gate()


def test_goal_block_ok_passthrough(tmp_path, monkeypatch):
    f = tmp_path / "order.md"
    f.write_text(GOOD, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    ok, why = _goal_block_ok("order.md")
    assert ok, why


def test_goal_block_missing_blocked(tmp_path, monkeypatch):
    f = tmp_path / "order.md"
    f.write_text(NO_BLOCK, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    ok, _ = _goal_block_ok("order.md")
    assert not ok


def test_goal_block_exempt_allowed(tmp_path, monkeypatch):
    f = tmp_path / "order.md"
    f.write_text(EXEMPT, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    ok, why = _goal_block_ok("order.md")
    assert ok and "EXEMPT" in why


def test_gate_blocks_new_order_without_block(tmp_path, monkeypatch, gate):
    (tmp_path / "docs" / "_working" / "x").mkdir(parents=True)
    f = tmp_path / "docs" / "_working" / "x" / "order.md"
    f.write_text(NO_BLOCK, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    gw = _FakeGit({"docs/_working/x/order.md"})
    ok, detail = gate.check(gw, ["docs/_working/x/order.md"], session_id="t")
    assert not ok and "CAMPAIGN-GOAL-BLOCK" in detail


def test_gate_passes_new_order_with_block(tmp_path, monkeypatch, gate):
    (tmp_path / "docs" / "_working" / "x").mkdir(parents=True)
    f = tmp_path / "docs" / "_working" / "x" / "order.md"
    f.write_text(GOOD, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    gw = _FakeGit({"docs/_working/x/order.md"})
    ok, detail = gate.check(gw, ["docs/_working/x/order.md"], session_id="t")
    assert ok


def test_gate_ignores_non_order_md(tmp_path, monkeypatch, gate):
    (tmp_path / "docs" / "_working" / "x").mkdir(parents=True)
    f = tmp_path / "docs" / "_working" / "x" / "notes.md"
    f.write_text("# 普通笔记无令词\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    gw = _FakeGit({"docs/_working/x/notes.md"})
    ok, _ = gate.check(gw, ["docs/_working/x/notes.md"], session_id="t")
    assert ok


def test_gate_ignores_modified_not_added(tmp_path, monkeypatch, gate):
    """M 态（非本笔新增）不拦——存量令与收班册零打扰。"""
    (tmp_path / "docs" / "_working" / "x").mkdir(parents=True)
    f = tmp_path / "docs" / "_working" / "x" / "old_order.md"
    f.write_text(NO_BLOCK, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    gw = _FakeGit(set())  # A 态清单为空
    ok, _ = gate.check(gw, ["docs/_working/x/old_order.md"], session_id="t")
    assert ok
