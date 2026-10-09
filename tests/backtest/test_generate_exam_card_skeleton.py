# [BLUEPRINT] MOD-BT-245 | docs/03_modules/_domain_backtest/blueprint.md
# [TESTS] tests/backtest/test_generate_exam_card_skeleton.py
# 测试隔离：全部读写走 tmp_path（运维红线 6，零生产路径写入）。
# [TTL] permanent
"""考试卡骨架生成器红蓝双向测试：四族映射/确定性/only-add/手工卡保护/TDM 漂移同步/fail-closed。"""

from __future__ import annotations

import pytest
import yaml

from scripts.backtest import generate_exam_card_skeleton as gen


def _node(node_id: str, flow: str, layer: str, node_type: str, **kw) -> dict:
    base = {
        "node_id": node_id,
        "name_zh": f"节点{node_id}",
        "flow": flow,
        "layer": layer,
        "node_type": node_type,
        "market": "cn_a",
        "decision_question": f"{node_id} 的判定问句",
        "module_ref": "src/x/y.py",
        "module_id": "MOD-X-001",
        "confidence": "proposed",
        "purpose_tag": "PT-01",
    }
    base.update(kw)
    return base


def _write_tdm(tmp_path, nodes: list[dict], effective_from: str = "2026-10-05") -> dict:
    tdm_path = tmp_path / "tdm.yaml"
    doc = {
        "map_id": "TDMAP-001",
        "effective_from": effective_from,
        "nodes": nodes,
    }
    tdm_path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return {"tdm_path": tdm_path, "cards_root": tmp_path / "exam_cards", "repo_root": tmp_path}


# ============ 默认卡族映射（方案 §4 四族） ============


def test_family_mapping_by_node_type():
    assert gen.default_family(_node("A", "entry_flow", "L1", "sensor")) == "calibration"
    assert gen.default_family(_node("B", "exit_flow", "P1", "gate")) == "comparison"
    assert gen.default_family(_node("C", "entry_flow", "L3", "stage")) == "comparison"
    assert gen.default_family(_node("D", "entry_flow", "L1", "aggregation")) == "ablation"
    assert gen.default_family(_node("E", "entry_flow", "L9", "cross_cutting")) == "shadow"


def test_family_portfolio_flow_overrides_node_type():
    # 组合层决策（C1 分配器等）无论 node_type 一律影子卡（方案 §4：组合层=影子）
    assert gen.default_family(_node("F", "portfolio_flow", "C1", "stage")) == "shadow"
    assert gen.default_family(_node("G", "portfolio_flow", "C3", "aggregation")) == "shadow"


def test_family_unknown_node_type_fail_closed():
    with pytest.raises(RuntimeError, match="无默认卡族映射"):
        gen.default_family(_node("H", "entry_flow", "L2", "alien_type"))


# ============ 确定性渲染（幂等的根基） ============


def test_render_deterministic_no_timestamp():
    n = _node("A", "entry_flow", "L1", "sensor")
    meta = {"map_id": "TDMAP-001", "effective_from": "2026-10-05"}
    r1 = gen.render_card(n, meta)
    r2 = gen.render_card(n, meta)
    assert r1 == r2
    # 禁时间戳：无 2026-10-09 式生成时刻、无 HH:MM:SS 形态
    assert "generated_at" not in r1
    card = yaml.safe_load(r1)
    assert card["schema_version"] == "1.0"
    assert card["generated"] is True
    assert card["status"] == "empty"
    assert card["pillars"] is None and card["hypothesis"] is None
    assert card["card_id"] == "A/calibration/01"
    assert card["lineage"]["confidence_writeback"] == "TDM.nodes.A.confidence"
    assert card["lineage"]["run_id"] is None and card["lineage"]["score_row"] is None
    assert card["tdm"]["effective_from"] == "2026-10-05"


# ============ 全流程：生成→幂等→only-add→漂移同步 ============


def test_run_create_then_idempotent(tmp_path):
    p = _write_tdm(
        tmp_path,
        [
            _node("A", "entry_flow", "L1", "sensor"),
            _node("B", "exit_flow", "P1", "gate"),
            _node("C", "portfolio_flow", "C1", "stage"),
        ],
    )
    s1 = gen.run(**p)
    assert s1["created"] == 3 and s1["coverage"] == "3/3"
    card_b = yaml.safe_load((p["cards_root"] / "exit_flow" / "P1" / "B__comparison.yaml").read_text(encoding="utf-8"))
    assert card_b["family"] == "comparison"
    card_c = yaml.safe_load((p["cards_root"] / "portfolio_flow" / "C1" / "C__shadow.yaml").read_text(encoding="utf-8"))
    assert card_c["family"] == "shadow"
    # 幂等：重跑零 diff
    s2 = gen.run(**p)
    assert s2["created"] == 0 and s2["identical"] == 3


def test_manual_card_protected_and_extra_cards_allowed(tmp_path):
    p = _write_tdm(tmp_path, [_node("A", "entry_flow", "L1", "sensor")])
    gen.run(**p)
    # 形态一：手工卡在生成器槽位之外的路径（抽屉插卡，方案 §5）——生成器不访问、逐字节不动
    manual = p["cards_root"] / "entry_flow" / "L1" / "A__comparison.yaml"
    manual.write_text(
        "card_id: A/comparison/07_手工卡\nnode_id: A\nfamily: comparison\nhypothesis: 情绪先锋四态影响次日溢价\n",
        encoding="utf-8",
    )
    # 形态二：手工卡占据生成器槽位（无 generated 标）——only-add 跳过不冲
    squat = p["cards_root"] / "entry_flow" / "L1" / "A__calibration.yaml"
    squat.write_text(
        "card_id: A/calibration/01\nnode_id: A\nfamily: calibration\nhypothesis: 手工先建\n", encoding="utf-8"
    )
    squat_handmade = squat.read_text(encoding="utf-8")
    s = gen.run(**p)
    assert s["protected_manual"] == 1  # 槽位被手工卡占据=跳过
    assert squat.read_text(encoding="utf-8") == squat_handmade  # 未被机生内容冲掉
    assert "手工卡" in manual.read_text(encoding="utf-8")  # 旁路手工卡逐字节未动
    assert s["coverage"] == "1/1"  # 本 TDM 仅 1 节点：protected(1) 覆盖


def test_tdm_drift_syncs_tdm_block_keeps_human_fields(tmp_path):
    p = _write_tdm(tmp_path, [_node("A", "entry_flow", "L1", "sensor")])
    gen.run(**p)
    card_path = p["cards_root"] / "entry_flow" / "L1" / "A__calibration.yaml"
    # 人填面：预注册（填假设+门柱+status）
    card = yaml.safe_load(card_path.read_text(encoding="utf-8"))
    card["hypothesis"] = "涨停家数分桶对次日指数收益有单调预测力"
    card["pillars"] = {"ic_floor": 0.02}
    card["status"] = "preregistered"
    card_path.write_text(yaml.safe_dump(card, allow_unicode=True, sort_keys=False), encoding="utf-8")
    # TDM 漂移：判定问句变更 + confidence 升级
    p2 = _write_tdm(
        tmp_path, [_node("A", "entry_flow", "L1", "sensor", decision_question="新问句", confidence="verified")]
    )
    s = gen.run(**p2)
    assert s["synced"] == 1
    after = yaml.safe_load(card_path.read_text(encoding="utf-8"))
    assert after["tdm"]["decision_question"] == "新问句"  # 派生块已同步
    assert after["tdm"]["confidence_at_gen"] == "verified"
    assert after["hypothesis"] == "涨停家数分桶对次日指数收益有单调预测力"  # 人填面保留
    assert after["pillars"] == {"ic_floor": 0.02}
    assert after["status"] == "preregistered"
    s2 = gen.run(**p2)
    assert s2["identical"] == 1  # 同步后重跑零 diff


def test_check_mode_reports_missing_without_write(tmp_path):
    p = _write_tdm(tmp_path, [_node("A", "entry_flow", "L1", "sensor")])
    s = gen.run(check=True, **p)
    assert s["missing"] == 1 and not (p["cards_root"]).exists()


# ============ fail-closed ============


def test_tdm_without_nodes_raises(tmp_path):
    tdm_path = tmp_path / "tdm.yaml"
    tdm_path.write_text("map_id: TDMAP-001\nnodes: []\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="零节点"):
        gen.run(tdm_path=tdm_path, cards_root=tmp_path / "c", repo_root=tmp_path)


def test_node_missing_flow_raises(tmp_path):
    bad = _node("A", "entry_flow", "L1", "sensor")
    del bad["flow"]
    p = _write_tdm(tmp_path, [bad])
    with pytest.raises(RuntimeError, match="缺必填键") as ei:
        gen.run(**p)
    assert ei.value.details["key"] == "flow"
