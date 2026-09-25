# [BLUEPRINT] MOD-TEST-248 | docs/03_modules/_domain_governance/blueprint.md | §dual_run_tests
# [MODULE] tests.intelligence.model_profiling.test_dual_run
# [DOMAIN] D_AUDITTEST
# [DEPENDENCIES] zephyr.intelligence.model_profiling.dual_run; config/dual_run_criteria.yaml（只读真实冻结件）
# [CONSUMERS] pytest（python -m pytest tests/intelligence/model_profiling/ -q）
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 测试禁写生产路径：判据fixture只写 tmp_path；执行器 LLM 调用面全注入假 fn（禁真实 LLM 入单测）；
#              mcnemar_p 已知值校验用卡方分布表值（b=1,c=8→χ²=4.0→p≈0.0455），非同式复算
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §4.2/§4.4
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即用例红；CriteriaError/CriteriaFrozenError 预期路径用 pytest.raises
# [TESTS] —（本文件即测试）
# [TTL] task_bound
"""dual_run 单测 — 判据冻结/可复现抽样/双跑记账/手写统计/四态机检（C5 验收）。"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.intelligence.model_profiling.dual_run import (
    CriteriaError,
    CriteriaFrozenError,
    DEFAULT_CRITERIA_PATH,
    MIN_JUDGEABLE,
    evidence_pack,
    freeze_hash,
    load_criteria,
    main,
    mcnemar_p,
    run_pair,
    sample_strata,
    stratum_verdict,
    thresholds_from_criteria,
    verify_freeze,
    wilcoxon_signed_rank_p,
)

THRESHOLDS: dict[str, float] = thresholds_from_criteria(
    {"significance": {"alpha": 0.05}}
)


# --------------------------------------------------------------------------
# fixtures（只写 tmp_path，禁生产路径）
# --------------------------------------------------------------------------
def _valid_criteria() -> dict[str, Any]:
    """最小合法判据（满足 load_criteria 全部必查字段）。"""
    return {
        "experiment_id": "DR-20990101-test",
        "champion": {"model_id": "champ-x", "passport_version": "v1"},
        "challenger": {"model_id": "chal-y", "passport_version": "v1"},
        "strata": [{"stratum": "S1", "n": 2, "seed": 1}],
        "metrics": {
            "success_rate": {"definition": "d", "judge": "j"},
            "latency_s": {"definition": "d", "judge": "j"},
            "rework_count": {"definition": "d", "judge": "j"},
            "cost_usd_unit": {"definition": "d", "judge": "j"},
        },
        "significance": {"alpha": 0.05, "test_binary": "mcnemar"},
        "freeze_rule": "施工前冻结",
    }


@pytest.fixture()
def criteria_file(tmp_path: Path) -> Path:
    path = tmp_path / "criteria.yaml"
    path.write_text(
        yaml_safe_dump({"dual_run_criteria": _valid_criteria()}), encoding="utf-8"
    )
    return path


def yaml_safe_dump(doc: dict[str, Any]) -> str:
    return yaml.safe_dump(doc, allow_unicode=True)


# --------------------------------------------------------------------------
# load_criteria：fail-closed
# --------------------------------------------------------------------------
def test_load_criteria_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(CriteriaError):
        load_criteria(tmp_path / "nope.yaml")


def test_load_criteria_missing_field_raises(tmp_path: Path) -> None:
    bad = _valid_criteria()
    del bad["significance"]
    path = tmp_path / "bad.yaml"
    path.write_text(yaml_safe_dump({"dual_run_criteria": bad}), encoding="utf-8")
    with pytest.raises(CriteriaError):
        load_criteria(path)


def test_load_criteria_missing_top_key_raises(tmp_path: Path) -> None:
    path = tmp_path / "notop.yaml"
    path.write_text("other_key: 1\n", encoding="utf-8")
    with pytest.raises(CriteriaError):
        load_criteria(path)


def test_load_real_criteria_file() -> None:
    """真实冻结件可加载且冻结哈希为 64 位十六进制（ shipped 判据自检）。"""
    criteria = load_criteria(DEFAULT_CRITERIA_PATH)
    assert len(criteria["strata"]) == 5
    digest = freeze_hash(criteria)
    assert len(digest) == 64
    int(digest, 16)  # 必须是合法十六进制


# --------------------------------------------------------------------------
# freeze_hash：稳定性
# --------------------------------------------------------------------------
def test_freeze_hash_stable_for_same_dict() -> None:
    criteria = _valid_criteria()
    assert freeze_hash(criteria) == freeze_hash(dict(criteria))


def test_freeze_hash_changes_on_any_field() -> None:
    criteria = _valid_criteria()
    mutated = json.loads(json.dumps(criteria))
    mutated["significance"]["alpha"] = 0.01
    assert freeze_hash(criteria) != freeze_hash(mutated)


def test_freeze_hash_key_order_insensitive() -> None:
    criteria = _valid_criteria()
    reordered = dict(reversed(list(criteria.items())))
    assert freeze_hash(criteria) == freeze_hash(reordered)


# --------------------------------------------------------------------------
# sample_strata：可复现
# --------------------------------------------------------------------------
def _pool(n: int) -> list[dict[str, Any]]:
    return [
        {
            "sample_id": f"t-{i:03d}",
            "task_type": "T1" if i % 2 == 0 else "T2",
            "quadrant": "Q",
        }
        for i in range(n)
    ]


def test_sample_strata_reproducible_same_seed() -> None:
    strata = [{"stratum": "S1", "n": 3, "seed": 7}, {"stratum": "S2", "n": 2, "seed": 7}]
    first = sample_strata(strata, _pool(10), seed=42)
    second = sample_strata(strata, _pool(10), seed=42)
    assert [s["sample_id"] for s in first["S1"]] == [
        s["sample_id"] for s in second["S1"]
    ]
    assert [s["sample_id"] for s in first["S2"]] == [
        s["sample_id"] for s in second["S2"]
    ]


def test_sample_strata_different_seed_differs() -> None:
    strata = [{"stratum": "S1", "n": 3, "seed": 7}]
    a = sample_strata(strata, _pool(20), seed=1)
    b = sample_strata(strata, _pool(20), seed=2)
    assert [s["sample_id"] for s in a["S1"]] != [s["sample_id"] for s in b["S1"]]


def test_sample_strata_axis_filter_and_pool_shortage() -> None:
    strata = [{"stratum": "S1", "n": 5, "task_type": "T1", "seed": 7}]
    picked = sample_strata(strata, _pool(6), seed=42)["S1"]
    assert len(picked) == 3  # 池中 T1 仅 3 件：轴过滤生效且池不足不虚凑
    assert all(s["task_type"] == "T1" for s in picked)


# --------------------------------------------------------------------------
# run_pair：注入假 fn 双跑逐样本记账（禁真实 LLM）
# --------------------------------------------------------------------------
def test_run_pair_per_sample_bookkeeping() -> None:
    samples = {"S1": [{"sample_id": "a"}, {"sample_id": "b"}]}

    def champion_fn(sample: dict[str, Any]) -> dict[str, Any]:
        return {"output": f"c:{sample['sample_id']}", "latency_s": 1.0, "cost_usd": 0.5, "rework_count": 0}

    def challenger_fn(sample: dict[str, Any]) -> dict[str, Any]:
        return {"output": f"x:{sample['sample_id']}", "latency_s": 0.5, "cost_usd": 0.2, "rework_count": 1}

    def judge_fn(champ: dict[str, Any], chal: dict[str, Any], sample: dict[str, Any]) -> dict[str, Any]:
        ok = sample["sample_id"] == "a"
        return {"success_champion": ok, "success_challenger": ok}

    records = run_pair(challenger_fn, champion_fn, samples, judge_fn)
    assert len(records) == 2
    first = records[0]
    assert first["stratum"] == "S1"
    assert first["sample_id"] == "a"
    assert first["champion"]["output"] == "c:a"
    assert first["challenger"]["output"] == "x:a"
    assert first["success_champion"] is True
    assert first["success_challenger"] is True
    assert records[1]["success_champion"] is False


# --------------------------------------------------------------------------
# mcnemar_p / wilcoxon：手写统计已知值校验
# --------------------------------------------------------------------------
def test_mcnemar_no_discordant_pairs_is_one() -> None:
    assert mcnemar_p(0, 0) == 1.0


def test_mcnemar_known_value_significant() -> None:
    # b=0,c=10：校正卡方=(10-1)^2/10=8.1 → 显著
    assert mcnemar_p(0, 10) < 0.05
    # b=1,c=8：校正卡方=(8-1-1)^2/9=4.0，1 自由度卡方表值 p≈0.0455003
    assert abs(mcnemar_p(1, 8) - 0.0455) < 1e-3


def test_wilcoxon_small_sample_returns_nan() -> None:
    result = wilcoxon_signed_rank_p([1.0] * (MIN_JUDGEABLE - 1))
    assert result != result  # NaN 自反不成立即 NaN


def test_wilcoxon_symmetric_noise_not_significant() -> None:
    diffs = [1.0, -1.0, 2.0, -2.0, 1.5, -1.5, 0.5, -0.5, 1.2, -1.2]
    assert wilcoxon_signed_rank_p(diffs) > 0.05


def test_wilcoxon_consistent_negative_diffs_significant() -> None:
    diffs = [-1.0, -1.2, -0.9, -1.1, -1.3, -0.8, -1.4, -1.05, -0.95, -1.15]
    assert wilcoxon_signed_rank_p(diffs) < 0.05


# --------------------------------------------------------------------------
# stratum_verdict：四态全枚举 + 诚实条款
# --------------------------------------------------------------------------
def _pairs(
    both_ok: int,
    both_fail: int = 0,
    champ_only: int = 0,
    chal_only: int = 0,
    champ_cost: float = 1.0,
    chal_cost: float = 1.0,
) -> list[dict[str, Any]]:
    def pair(ok_c: bool, ok_x: bool) -> dict[str, Any]:
        return {
            "sample_id": "s",
            "champion": {"latency_s": 1.0, "cost_usd": champ_cost if ok_c else 0.0},
            "challenger": {"latency_s": 1.0, "cost_usd": chal_cost if ok_x else 0.0},
            "success_champion": ok_c,
            "success_challenger": ok_x,
        }

    return (
        [pair(True, True)] * both_ok
        + [pair(False, False)] * both_fail
        + [pair(True, False)] * champ_only
        + [pair(False, True)] * chal_only
    )


def test_verdict_challenger_win() -> None:
    # 45pp 差 + b=0,c=9（p≈0.007 显著）→ 胜；成本劣化不掩盖显著胜出
    stats = stratum_verdict(_pairs(both_ok=11, chal_only=9, chal_cost=1.2), THRESHOLDS)
    assert stats["verdict"] == "challenger_win"


def test_verdict_non_inferior_cost_win() -> None:
    # 成功率打平（不显著）+ challenger 单价省 50% → 换更便宜成立
    stats = stratum_verdict(
        _pairs(both_ok=19, both_fail=1, chal_cost=0.5), THRESHOLDS
    )
    assert stats["verdict"] == "non_inferior_cost_win"


def test_verdict_champion_hold_not_significant() -> None:
    # +20pp 但 McNemar 不显著（b=2,c=6 → p≈0.29）→ champion 保持
    stats = stratum_verdict(
        _pairs(both_ok=12, champ_only=2, chal_only=6), THRESHOLDS
    )
    assert stats["diff_pp"] == pytest.approx(20.0)
    assert stats["verdict"] == "champion_hold"


def test_verdict_champion_hold_when_challenger_worse() -> None:
    stats = stratum_verdict(_pairs(both_ok=10, champ_only=8, chal_cost=0.1), THRESHOLDS)
    assert stats["verdict"] == "champion_hold"


def test_verdict_undecided_below_min_judgeable() -> None:
    stats = stratum_verdict(_pairs(both_ok=MIN_JUDGEABLE - 1), THRESHOLDS)
    assert stats["verdict"] == "undecided"
    assert stats["judgeable"] == MIN_JUDGEABLE - 1


# --------------------------------------------------------------------------
# verify_freeze / evidence_pack / CLI
# --------------------------------------------------------------------------
def test_verify_freeze_accepts_current_hash(criteria_file: Path) -> None:
    recorded = freeze_hash(load_criteria(criteria_file))
    verify_freeze(criteria_file, recorded)  # 不抛即通过


def test_verify_freeze_rejects_mismatch(criteria_file: Path) -> None:
    with pytest.raises(CriteriaFrozenError):
        verify_freeze(criteria_file, "0" * 64)


def test_evidence_pack_shape() -> None:
    pack = evidence_pack("DR-20260923-demo", "a" * 64, [{"S1": 1}])
    assert pack["experiment_id"] == "DR-20260923-demo"
    assert pack["criteria_freeze_sha256"] == "a" * 64
    ts = datetime.fromisoformat(pack["generated_at"])
    assert ts.tzinfo is not None and ts.utcoffset() == UTC.utcoffset(ts)


def test_cli_dry_run_outputs_summary_json(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--dry-run", "--experiment-id", "DR-20260923-demo"])
    assert code == 0
    summary = json.loads(capsys.readouterr().out)
    assert len(summary["criteria_freeze_sha256"]) == 64
    assert set(summary["strata_sampled"]) == {"S1", "S2", "S3", "S4", "S5"}


def test_cli_without_dry_run_honest_exit_2(capsys: pytest.CaptureFixture[str]) -> None:
    code = main([])
    assert code == 2
    assert "exam_executor" in capsys.readouterr().err


def test_cli_check_freeze_mismatch_raises(criteria_file: Path) -> None:
    with pytest.raises(CriteriaFrozenError):
        main(["--criteria", str(criteria_file), "--check-freeze", "f" * 64])
