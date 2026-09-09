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

import yaml

from zephyr.gov_enforcement.commit_gates.algo_note_sync_gate import check_algo_note_sync

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
