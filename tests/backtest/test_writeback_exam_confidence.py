# [BLUEPRINT] MOD-BT-246 | docs/03_modules/_domain_backtest/blueprint.md
# [TESTS] tests/backtest/test_writeback_exam_confidence.py
# 测试隔离：全部读写走 tmp_path（运维红线 6）；TDM 夹具为最小合法节点集。
# [TTL] permanent
"""W5 confidence 回写红蓝双向：冻结判据迁移/候选关系不升级/衰减降级/外科替换/写后校验。"""

from __future__ import annotations

import textwrap

import pytest
import yaml

from scripts.backtest import writeback_exam_confidence as wb


def _tdm_node(node_id: str, conf: str) -> str:
    return textwrap.dedent(f"""\
    schema_version: '1.2'
    map_id: TDMAP-001
    name_zh: 测试地图
    effective_from: '2026-10-05'
    nodes:
    - node_id: {node_id}
      name_zh: 节点{node_id}
      market: cn_a
      flow: entry_flow
      layer: L1
      node_type: sensor
      point: 盘前
      decision_question: 测试问句
      confidence: {conf}
    - node_id: TDM-E-OTHER
      name_zh: 其他节点
      market: cn_a
      flow: entry_flow
      layer: L1
      node_type: sensor
      point: 盘前
      decision_question: 其他
      confidence: proposed
    """)


def _scores(rows: list[dict]) -> dict:
    import tempfile
    from pathlib import Path

    f = Path(tempfile.mkstemp(suffix=".yaml")[1])
    f.write_text(yaml.safe_dump({"rows": rows}, allow_unicode=True), encoding="utf-8")
    return f


def _row(node_id="TDM-E-A", kind="exam", verdict="pass", pillars=True, oos=True, regimes=("bull", "bear")):
    return {
        "card_id": f"{node_id}/calibration/01",
        "node_id": node_id,
        "run_id": "run-2026-001",
        "kind": kind,
        "verdict": verdict,
        "pillars_all_pass": pillars,
        "oos_ok": oos,
        "regimes": list(regimes),
        "date": "2026-10-09",
    }


# ============ 判据红蓝（裁定#501 冻结面） ============


def test_upgrade_full_conditions():
    new, reason = wb.decide_transition(_row(), "proposed")
    assert new == "verified" and "双行情段" in reason


def test_upgrade_from_untested_also_verified():
    new, _ = wb.decide_transition(_row(), "untested")
    assert new == "verified"


def test_no_upgrade_without_oos():
    # 红腿：OOS 不成立=维持候选关系（W4 纪律）
    new, reason = wb.decide_transition(_row(oos=False), "proposed")
    assert new is None and "候选关系" in reason


def test_no_upgrade_without_bull_bear():
    new, _ = wb.decide_transition(_row(regimes=("bull",)), "proposed")
    assert new is None


def test_no_upgrade_on_fail():
    new, reason = wb.decide_transition(_row(verdict="fail"), "proposed")
    assert new is None and "候选关系" in reason


def test_no_upgrade_when_pillars_missing():
    new, _ = wb.decide_transition(_row(pillars=False), "proposed")
    assert new is None


def test_downgrade_on_decay_scan_fail():
    new, reason = wb.decide_transition(_row(kind="decay_scan", verdict="fail"), "verified")
    assert new == "proposed" and "衰减" in reason


def test_decay_fail_does_not_touch_proposed():
    new, _ = wb.decide_transition(_row(kind="decay_scan", verdict="fail"), "proposed")
    assert new is None


def test_already_verified_no_change():
    new, _ = wb.decide_transition(_row(), "verified")
    assert new is None


# ============ 外科替换与端到端 ============


def test_surgical_replace_only_target_node(tmp_path):
    tdm = tmp_path / "tdm.yaml"
    tdm.write_text(_tdm_node("TDM-E-A", "proposed"), encoding="utf-8")
    scores = _scores([_row("TDM-E-A")])
    s = wb.run(
        apply=True, tdm_path=tdm, scores_path=scores, post_validate=False
    )  # 最小夹具过不了全图 R 系校验，外科替换正确性单测另验
    assert s["changed"] == 1
    text = tdm.read_text(encoding="utf-8")
    assert "confidence: verified" in text
    # 其他节点零触碰
    assert "- node_id: TDM-E-OTHER" in text
    other_block = text.split("- node_id: TDM-E-OTHER")[1]
    assert "confidence: proposed" in other_block


def test_dry_run_makes_no_write(tmp_path):
    tdm = tmp_path / "tdm.yaml"
    original = _tdm_node("TDM-E-A", "proposed")
    tdm.write_text(original, encoding="utf-8")
    scores = _scores([_row("TDM-E-A")])
    s = wb.run(apply=False, tdm_path=tdm, scores_path=scores)
    assert s["changed"] == 1 and s["apply"] is False
    assert tdm.read_text(encoding="utf-8") == original  # 零写


def test_missing_score_field_fail_closed(tmp_path):
    bad = {"card_id": "x", "node_id": "TDM-E-A"}  # 缺 kind/verdict/run_id
    scores = _scores([bad])
    with pytest.raises(RuntimeError, match="缺字段"):
        wb.run(apply=False, tdm_path=tmp_path / "tdm.yaml", scores_path=scores)


def test_node_not_in_tdm_fail_closed(tmp_path):
    tdm = tmp_path / "tdm.yaml"
    tdm.write_text(_tdm_node("TDM-E-A", "proposed"), encoding="utf-8")
    scores = _scores([_row("TDM-E-GHOST")])
    with pytest.raises(RuntimeError, match="不在 TDM"):
        wb.run(apply=True, tdm_path=tdm, scores_path=scores)
    # fail-closed：零写入
    assert "confidence: proposed" in tdm.read_text(encoding="utf-8")
