# [TTL] permanent
# [BLUEPRINT] MOD-BT-FEXAM | tests/backtest/fexam/test_campaign_report.py | 批5汇总/缺口单/metaq匹配 单测
"""campaign_report 单测：汇总结构/缺口集合运算/原问题匹配口径（tmp_path 注入，零 DB 零 CH）。"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

FEXAM = Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "fexam"
if str(FEXAM) not in sys.path:
    sys.path.insert(0, str(FEXAM))

import campaign_report as cr  # noqa: E402


def _write(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")


def test_build_summary_pending_and_done(tmp_path, monkeypatch):
    fex = tmp_path / "fexam"
    _write(
        fex / "factor_exam_scores_v1.yaml",
        {
            "counts": {"total": 2, "pass": 1, "rework": 0, "retire_candidate": 1},
            "results": [
                {"object_id": "F1", "verdict": "pass", "ch_backings": ["t.c"]},
                {"object_id": "F2", "verdict": "retire_candidate"},
            ],
        },
    )
    monkeypatch.setattr(
        cr,
        "BOOKS",
        {
            "factor": fex / "factor_exam_scores_v1.yaml",
            "indicator": fex / "indicator_exam_scores_v1.yaml",
            "strategy": fex / "strategy_exam_scores_v1.yaml",
            "allocator": fex / "allocator_shadow_report_v1.yaml",
        },
    )
    monkeypatch.setattr(cr, "FULLCIRC", tmp_path / "none")
    out = cr.build_summary(fex / "summary.yaml")
    assert out["batches"]["factor"]["status"] == "done"
    assert out["batches"]["factor"]["passes"] == ["F1"]
    assert out["batches"]["strategy"]["status"] == "pending"
    assert (fex / "00_exam_campaign_summary_v1.md").exists()
    assert any("activation" in a for a in out["approvals_pending_owner"]) is False  # 批2缺册不批升档


def test_gap_lists_set_logic(tmp_path, monkeypatch):
    cat = tmp_path / "cat"
    _write(
        cat / "data_asset_registry.yaml",
        {
            "entries": [
                {"dataset_id": "DS-1", "entity_name": "c1_market.ma_tab", "produced_by_job": "j1"},
                {"dataset_id": "DS-2", "entity_name": "c1_market.lone_tab", "produced_by_job": "j2"},
                {"dataset_id": "DS-3", "entity_name": "c1_market.zombie_tab"},
            ]
        },
    )
    roster = {
        "factor": [
            {"object_id": "FCT-1", "bucket": "ch_backed", "ch_backings": ["c1_market.ma_tab.c1"]},
            {"object_id": "FCT-2", "bucket": "non_quantified", "ch_backings": []},
        ],
        "strategy": [
            {"object_id": "STR-1", "bucket": "harness_examinable", "backed_alpha_sources": ["FCT-1"]},
            {"object_id": "STR-2", "bucket": "non_quantified", "backed_alpha_sources": []},
        ],
        "indicator": [],
        "allocator": [],
    }
    _write(cat / "trial_ledger_registry.yaml", {"screen_runs": {"total_trials": 0}})
    monkeypatch.setattr(cr, "CATALOGS", cat)
    monkeypatch.setattr(cr, "FEXAM_DIR", tmp_path / "fexam")
    monkeypatch.setattr(cr, "METAQ_SNAP", tmp_path / "nosnap")
    _write(tmp_path / "fexam" / "bt_p0_roster_v1.yaml", roster)
    monkeypatch.setattr(cr, "RUN_ROOT", tmp_path)
    monkeypatch.setattr(yaml, "safe_load", yaml.safe_load)  # no-op 防 lint
    # TDM 缺失 → missing_sources 记录
    res = cr.build_inventory(tmp_path / "inv.yaml", tmp_path / "gap.yaml")
    gaps = yaml.safe_load((tmp_path / "gap.yaml").read_text(encoding="utf-8"))["gap_lists"]
    assert gaps["g1_data_no_factor"] == ["DS-2"]  # 有任务腿无因子腿
    assert gaps["g2_factor_no_strategy"] == ["FCT-2"]
    assert gaps["g3_strategy_no_exam"] == ["STR-2"]
    assert gaps["g4_fully_disconnected"] == ["DS-3"]  # 四腿全断
    assert "trading_decision_map" in res["missing_sources"]
    inv = yaml.safe_load((tmp_path / "inv.yaml").read_text(encoding="utf-8"))
    assert inv["counts"]["datasets"] == 3
    assert inv["counts"]["wiring_max"]["L1_data_leg"] == 1  # 仅 DS-2（DS-1 已达 L3）


def test_metaq_matching_infra_filter(tmp_path, monkeypatch):
    snap = tmp_path / "snap"
    _write(
        snap / "question_batch_w6.yaml",
        {
            "questions": [
                {
                    "title": "因子X样本外IC是否显著为正且大于阈值？",
                    "layer": "L2",
                    "exam_plan": {"criterion": "IC>0.02"},
                    "frequency": "monthly",
                },
                {
                    "title": "入库闸五要素机检拒绝率是否≤20%？",
                    "layer": "L0",
                    "exam_plan": {"criterion": "拒绝码分布"},
                    "frequency": "monthly",
                },
            ]
        },
    )
    monkeypatch.setattr(cr, "METAQ_SNAP", snap)
    monkeypatch.setattr(cr, "FEXAM_DIR", tmp_path / "fexam")  # 无分数册→无facts
    out = cr.build_metaq_matching(tmp_path / "metaq.yaml")
    assert out["questions_total"] == 2
    asset_q = next(m for m in out["matches"] if "因子" in m["q_title"])
    infra_q = next(m for m in out["matches"] if "入库闸" in m["q_title"])
    assert asset_q["matched_batches"] == ["factor"]
    assert infra_q["answerable_now"] is False  # L0 治理面不归资产考试答
