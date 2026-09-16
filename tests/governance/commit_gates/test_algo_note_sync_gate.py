# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_algo_note_sync_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest（tests/ 豁免区）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯逻辑单测（不触 git）——触碰 module_ref 代码未同 commit 修订/确认大白话=阻断；algo_note_zh 修订=放行+payload 复审；note_confirmed=放行；module_ref=null 豁免；无 .py 变更快速放行
# [MODIFY-GUARD] 无（测试）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即用例失败
# [TESTS] self
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ALGO-NOTE-SYNC 门禁纯逻辑单测（Owner 2026-09-09 任务三）。"""

from __future__ import annotations

import difflib

import yaml

from zephyr.gov_enforcement.commit_gates.algo_note_sync_gate import (
    _collect_node_block_changes,
    _collect_node_block_changes_by_linenos,
    check_algo_note_sync,
    make_algo_note_sync_gate,
)

_DIFF_NOTE_REVISED = """
--- a/config/trading_decision_map.yaml
+++ b/config/trading_decision_map.yaml
@@ -10,7 +10,7 @@
   - node_id: TDM-T-1
     name_zh: 节点一
-    algo_note_zh: 旧大白话
+    algo_note_zh: 新大白话：阈值改了
"""

_DIFF_NOTE_CONFIRMED = """
--- a/config/trading_decision_map.yaml
+++ b/config/trading_decision_map.yaml
@@ -10,6 +10,7 @@
   - node_id: TDM-T-1
     algo_note_zh: 旧大白话
+    note_confirmed: "2026-09-09"
"""

_DIFF_UNRELATED = """
--- a/config/trading_decision_map.yaml
+++ b/config/trading_decision_map.yaml
@@ -1,2 +1,3 @@
   - node_id: TDM-T-9
+    name_zh: 无关节点
"""


def _write_map(root) -> object:
    map_path = root / "config" / "trading_decision_map.yaml"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "map_id": "TDMAP-TEST",
        "markets": ["cn_a"],
        "nodes": [
            {
                "node_id": "TDM-T-1",
                "name_zh": "节点一",
                "market": "cn_a",
                "flow": "entry_flow",
                "layer": "L1",
                "node_type": "stage",
                "point": "盘前",
                "decision_question": "q1",
                "algo_note_zh": "旧大白话",
                "module_ref": "src/zephyr/demo_impl.py",
            },
            {
                "node_id": "TDM-T-2",
                "name_zh": "节点二",
                "market": "cn_a",
                "flow": "entry_flow",
                "layer": "L2",
                "node_type": "stage",
                "point": "盘前",
                "decision_question": "q2",
                "algo_note_zh": "n/a",
                "module_ref": None,
            },
        ],
        "edges": [
            {"from_node": "TDM-T-1", "to_node": "TDM-T-1", "edge_type": "feed", "payload_zh": "预算带"},
        ],
        "state_matrix": {"states": ["强势"], "cells": []},
    }
    map_path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return map_path


def test_block_when_code_touched_without_note_sync(tmp_path) -> None:
    map_path = _write_map(tmp_path)
    blocked, msg, review = check_algo_note_sync(["src/zephyr/demo_impl.py"], map_path, _DIFF_UNRELATED)
    assert blocked
    assert "TDM-T-1" in msg
    assert review == []


def test_pass_when_algo_note_revised_and_payload_flagged(tmp_path) -> None:
    map_path = _write_map(tmp_path)
    blocked, msg, review = check_algo_note_sync(["src/zephyr/demo_impl.py"], map_path, _DIFF_NOTE_REVISED)
    assert not blocked
    assert review == [{"edge": "TDM-T-1->TDM-T-1", "payload_zh": "预算带"}]


def test_pass_when_note_confirmed(tmp_path) -> None:
    map_path = _write_map(tmp_path)
    blocked, msg, review = check_algo_note_sync(["src/zephyr/demo_impl.py"], map_path, _DIFF_NOTE_CONFIRMED)
    assert not blocked


def test_null_module_ref_node_exempt(tmp_path) -> None:
    map_path = _write_map(tmp_path)
    blocked, msg, review = check_algo_note_sync(["src/zephyr/other_impl.py"], map_path, _DIFF_UNRELATED)
    assert not blocked


def test_no_py_changes_fast_pass(tmp_path) -> None:
    map_path = _write_map(tmp_path)
    blocked, msg, review = check_algo_note_sync(["config/foo.yaml"], map_path, "")
    assert not blocked
    assert review == []


# ---------------------------------------------------------------------------
# 超窗归因漂移治本回归（GW5/GW4 实证，2026-09-16 GW11 治本）
#
# 病根：unified diff 上下文仅 3 行——node_id 行距修订行超窗时，diff 文本内锚
# 丢失，变更归因漂移到前一节点（GW4 曾被迫以 note_confirmed 键行贴 node_id 绕开）。
# 治本：check_algo_note_sync 新增 old_text/new_text（HEAD/staged 全文），按 hunk
# 行号在全文上精确归因；全文不可得回退窗内锚扫描。
# ---------------------------------------------------------------------------

_MAP_V1 = """\
schema_version: "1.0"
map_id: TDMAP-TEST
markets: [cn_a]
nodes:
  - node_id: TDM-T-1
    name_zh: 节点一
    market: cn_a
    flow: entry_flow
    layer: L1
    node_type: stage
    point: 盘前
    decision_question: q1
    module_ref: null
    algo_note_zh: 节点一旧大白话
  - node_id: TDM-T-2
    name_zh: 节点二
    market: cn_a
    flow: entry_flow
    layer: L2
    node_type: stage
    point: 盘前
    decision_question: q2
    module_ref: src/zephyr/demo_impl.py
    algo_note_zh: 节点二旧大白话
edges:
  - from_node: TDM-T-2
    to_node: TDM-T-1
    edge_type: feed
    payload_zh: 预算带
state_matrix:
  states: [强势]
  cells: []
"""

# V2 变更：①TDM-T-1 name_zh 改名（hunk1，node_id 在窗内——锚正常）
#        ②TDM-T-2 algo_note_zh 修订（hunk2，node_id 距修订行 8 行——超窗）
_MAP_V2 = _MAP_V1.replace("name_zh: 节点一\n", "name_zh: 节点一改名\n").replace(
    "algo_note_zh: 节点二旧大白话\n", "algo_note_zh: 节点二新大白话：阈值已改\n"
)


def _make_diff(old: str, new: str) -> str:
    """生成带文件头的 unified diff（3 行上下文，同 git diff 默认）。"""
    return "\n".join(
        difflib.unified_diff(
            old.splitlines(),
            new.splitlines(),
            fromfile="a/config/trading_decision_map.yaml",
            tofile="b/config/trading_decision_map.yaml",
            lineterm="",
        )
    )


_DIFF_OVER_WINDOW = _make_diff(_MAP_V1, _MAP_V2)


def test_over_window_diff_shape_pinned() -> None:
    """钉死超窗前提：hunk1 上下文含 TDM-T-1 的 node_id；hunk2 不含 TDM-T-2 的 node_id。

    若 fixture 布局漂移导致此前提失效，后续漂移断言即失去意义——先行守门。
    """
    hunks = [h for h in _DIFF_OVER_WINDOW.split("\n") if h.startswith("@@")]
    assert len(hunks) == 2, f"应为两个独立 hunk（两处变更相距足够远）: {hunks}"
    h1, h2 = hunks
    body1 = _DIFF_OVER_WINDOW[_DIFF_OVER_WINDOW.index(h1) : _DIFF_OVER_WINDOW.index(h2)]
    body2 = _DIFF_OVER_WINDOW[_DIFF_OVER_WINDOW.index(h2) :]
    assert "node_id: TDM-T-1" in body1, "hunk1 上下文应含 TDM-T-1 node_id（窗内锚）"
    assert "node_id: TDM-T-2" not in body2, "hunk2 上下文不得含 TDM-T-2 node_id（超窗前提）"
    assert "algo_note_zh: 节点二" in body2


def test_over_window_defect_pinned_in_legacy_helper() -> None:
    """缺陷存档：窗内锚扫描把 TDM-T-2 的大白话修订漂移归因到 TDM-T-1。

    本断言钉死旧算法的缺陷形态（GW5/GW4 实证）；若未来删除回退路径，
    本用例应随 _collect_node_block_changes 一并退役。
    """
    changed = _collect_node_block_changes(_DIFF_OVER_WINDOW)
    assert "TDM-T-2" not in changed, "TDM-T-2 的修订超窗后未被归因（缺陷本体）"
    assert changed.get("TDM-T-1") == {"algo_note_zh"}, "修订应被漂移归因到前一节点 TDM-T-1"


def test_over_window_note_revision_passes_with_linenos(tmp_path) -> None:
    """治本路径：给全文（HEAD/staged）按行号归因——超窗大白话修订被正确识别，放行。"""
    map_path = tmp_path / "config" / "trading_decision_map.yaml"
    map_path.parent.mkdir(parents=True)
    map_path.write_text(_MAP_V2, encoding="utf-8")
    blocked, msg, review = check_algo_note_sync(
        ["src/zephyr/demo_impl.py"],
        map_path,
        _DIFF_OVER_WINDOW,
        old_text=_MAP_V1,
        new_text=_MAP_V2,
    )
    assert not blocked, f"超窗大白话修订应放行: {msg}"
    assert review == [{"edge": "TDM-T-2->TDM-T-1", "payload_zh": "预算带"}]


def test_linenos_deletion_attributed_via_old_index() -> None:
    """删除行（- 前缀）按旧文件行号取锚——旧文归因不依赖新文布局。"""
    # 新文把 TDM-T-2 的 algo_note_zh 整行删除
    new_text = _MAP_V1.replace("    algo_note_zh: 节点二旧大白话\n", "")
    diff_text = _make_diff(_MAP_V1, new_text)
    changed = _collect_node_block_changes_by_linenos(diff_text, _MAP_V1, new_text)
    assert "TDM-T-2" in changed
    assert "algo_note_zh" in changed["TDM-T-2"]


def test_linenos_append_beyond_eof_clamps_to_last_anchor() -> None:
    """无尾换行文件末尾追加行（行号=total+1）→ 钳到末行继承锚，不丢归属。"""
    old_text = "nodes:\n  - node_id: TDM-A\n    algo_note_zh: 旧"  # 无尾换行
    new_text = old_text + '\n    note_confirmed: "2026-09-16"'
    diff_text = _make_diff(old_text, new_text)
    changed = _collect_node_block_changes_by_linenos(diff_text, old_text, new_text)
    assert changed.get("TDM-A") == {"note_confirmed"}


def test_linenos_no_anchor_lines_unattributed() -> None:
    """全文无 node_id 锚（空文件/无关节）→ 空归因不炸。"""
    changed = _collect_node_block_changes_by_linenos(
        "--- a/m.yaml\n+++ b/m.yaml\n@@ -1,1 +1,1 @@\n-old\n+new\n",
        "",
        "new\n",
    )
    assert changed == {}


class _FakeGitResult:
    def __init__(self, stdout: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.returncode = returncode


class _FakeGateway:
    """最小 gateway 桩：git diff / git show(:map, HEAD:map) 按预设应答。"""

    def __init__(
        self,
        project_root,
        diff_text: str,
        staged_text: str | None,
        head_text: str | None,
    ) -> None:
        self.project_root = str(project_root)
        self._diff_text = diff_text
        self._shows = {
            ":config/trading_decision_map.yaml": (
                _FakeGitResult(staged_text, 0) if staged_text is not None else _FakeGitResult("", 1)
            ),
            "HEAD:config/trading_decision_map.yaml": (
                _FakeGitResult(head_text, 0) if head_text is not None else _FakeGitResult("", 1)
            ),
        }

    def run_git(self, cmd: list[str]):
        if cmd[:2] == ["git", "diff"]:
            return _FakeGitResult(self._diff_text, 0)
        if cmd[:2] == ["git", "show"]:
            return self._shows.get(cmd[2], _FakeGitResult("", 1))
        raise AssertionError(f"unexpected cmd: {cmd}")


def _write_map_text(tmp_path, text: str):
    map_path = tmp_path / "config" / "trading_decision_map.yaml"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text(text, encoding="utf-8")
    return map_path


def test_gate_closure_wires_staged_head_texts(tmp_path) -> None:
    """门闭包布线：staged/HEAD 全文可得 → 行号归因路径生效，超窗修订放行。"""
    _write_map_text(tmp_path, _MAP_V2)
    gate = make_algo_note_sync_gate()
    passed, msg = gate.check(
        _FakeGateway(tmp_path, _DIFF_OVER_WINDOW, staged_text=_MAP_V2, head_text=_MAP_V1),
        ["src/zephyr/demo_impl.py"],
        session_id="t",
    )
    assert passed, f"行号归因路径应放行: {msg}"


def test_gate_closure_falls_back_when_show_fails(tmp_path) -> None:
    """回退布线：staged 全文不可得（show 失败）→ 窗内锚回退路径，超窗修订被阻断。

    回退方向=阻断（fail-closed）：归因不到即要求补 note——宁误报不放漂移。
    """
    _write_map_text(tmp_path, _MAP_V2)
    gate = make_algo_note_sync_gate()
    passed, msg = gate.check(
        _FakeGateway(tmp_path, _DIFF_OVER_WINDOW, staged_text=None, head_text=None),
        ["src/zephyr/demo_impl.py"],
        session_id="t",
    )
    assert not passed
    assert "TDM-T-2" in msg
