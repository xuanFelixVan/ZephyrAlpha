# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §model_scoring
# [MODULE] tests.ai_layer.test_model_scoring_policy
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] config/model_scoring_policy.yaml（只读真源+tmp_path 副本）; PyYAML（safe_load/dump）
# [CONSUMERS] pytest tests/ai_layer/test_model_scoring_policy.py；C4 验收「重算幂等（同输入同分）」落点
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 打分器是测试内自包含纯函数（零 DB/零网络/零时钟，同输入必同分）；
#              权重/合成/档界常数一律从 YAML 读，缺失即 ScoringPolicyError（fail-closed，禁硬编码默认值）；
#              生产 YAML 只读不写；写用例一律 tmp_path 副本（测试禁写生产路径铁律）；
#              external_missing_remedy 实现口径=外部权重回流 MCE（0.5+0.2=0.7，0.7+0.3=1 已归一，P 恒在 [0,1]）——
#              DESIGN §3.3「权重归 0.8 归一化」与之矛盾（见交付报告偏离清单，待 Owner 修订口径），
#              本测试同时钉住 YAML 里注册的 remedy 字符串，改动即红
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §3.3
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；scoring 段/权重键/composite/tier_thresholds 缺失→ScoringPolicyError；
#                  退化岗位池（max_c==min_c）→ScoringPolicyError（min-max 无定义，不猜中性值）
# [TESTS] tests/ai_layer/test_model_scoring_policy.py
# [TTL] permanent
"""test_model_scoring_policy — C4 验收：常数齐+重算幂等（同输入同分）+fail-closed+档界恰好值。"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Final

import pytest
import yaml

REPO: Final = Path(__file__).resolve().parents[2]
POLICY_PATH: Final = REPO / "config" / "model_scoring_policy.yaml"


class ScoringPolicyError(ValueError):
    """打分口径缺失/畸形（fail-closed，绝不退回硬编码默认值）。"""


def load_scoring_policy(path: Path) -> dict[str, Any]:
    """读 YAML 的 scoring 段（缺段/非映射即 fail-closed）。"""
    with path.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    scoring = (doc or {}).get("scoring")
    if not isinstance(scoring, dict):
        raise ScoringPolicyError(f"scoring 段缺失或非映射：{path}")
    return scoring


def _section(scoring: dict[str, Any], key: str) -> dict[str, Any]:
    sec = scoring.get(key)
    if not isinstance(sec, dict):
        raise ScoringPolicyError(f"scoring.{key} 缺失或非映射")
    return sec


def _require_mapping_value(sec: dict[str, Any], section: str, key: str) -> float:
    if key not in sec or sec[key] is None:
        raise ScoringPolicyError(f"fail-closed：scoring.{section} 缺 {key}")
    return float(sec[key])


def compute_perf_p(mce: float, job_match: float, external: float | None,
                   scoring: dict[str, Any]) -> float:
    """性能分 P：三成分加权和（权重和归一）。

    外部参照缺失→其权重回流 MCE（0.5+0.2=0.7，剩余 0.7+0.3=1.0 天然归一，P 恒在 [0,1]）。
    """
    weights = _section(scoring, "performance_weights")
    w_mce = _require_mapping_value(weights, "performance_weights", "mce_standard")
    w_job = _require_mapping_value(weights, "performance_weights", "job_matcher")
    w_ext = _require_mapping_value(weights, "performance_weights", "external_ref")
    if external is None:
        w_mce_eff = w_mce + w_ext
        return (w_mce_eff * mce + w_job * job_match) / (w_mce_eff + w_job)
    return (w_mce * mce + w_job * job_match + w_ext * external) / (w_mce + w_job + w_ext)


def compute_value_v(cost: float, pool_costs: Sequence[float]) -> float:
    """性价比分 V=(max_c−c)/(max_c−min_c)，岗位池内 min-max（退化池 fail-closed）。"""
    if not pool_costs:
        raise ScoringPolicyError("岗位池为空，V 无定义")
    lo, hi = min(pool_costs), max(pool_costs)
    if hi <= lo:
        raise ScoringPolicyError(f"退化岗位池（max_c==min_c=={lo}），min-max 归一无定义")
    return (hi - cost) / (hi - lo)


def compose_score_s(p: float, v: float, scoring: dict[str, Any]) -> float:
    """合成 S = P^alpha_p × V^beta_v。"""
    composite = _section(scoring, "composite")
    alpha = _require_mapping_value(composite, "composite", "alpha_p")
    beta = _require_mapping_value(composite, "composite", "beta_v")
    return (p ** alpha) * (v ** beta)


def assign_tier(p: float, scoring: dict[str, Any]) -> str:
    """分档：P≥premium_min_p→premium；P≥standard_min_p→standard；其余 economy。"""
    thresholds = _section(scoring, "tier_thresholds")
    premium_min = _require_mapping_value(thresholds, "tier_thresholds", "premium_min_p")
    standard_min = _require_mapping_value(thresholds, "tier_thresholds", "standard_min_p")
    if p >= premium_min:
        return "premium"
    if p >= standard_min:
        return "standard"
    return "economy"


def score_model(mce: float, job_match: float, external: float | None, cost: float,
                pool_costs: Sequence[float], scoring: dict[str, Any]) -> dict[str, Any]:
    """一键全算（纯函数）：{perf_p, value_v, score_s, tier}。"""
    p = compute_perf_p(mce, job_match, external, scoring)
    v = compute_value_v(cost, pool_costs)
    return {
        "perf_p": p,
        "value_v": v,
        "score_s": compose_score_s(p, v, scoring),
        "tier": assign_tier(p, scoring),
    }


def test_constants_preregistered() -> None:
    """C4 验收「常数齐」：生产 YAML 每个常数都钉死为 DESIGN §3.3 预注册原值。"""
    with POLICY_PATH.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    assert doc["schema_version"] == "1.0.0"
    assert doc["ttl"] == "permanent"
    assert doc["doc_type"] == "policy"
    assert doc["status"] == "active"
    assert doc["date"] == "2026-09-23"
    scoring = doc["scoring"]
    assert scoring["version"] == "MSP-1.0"
    assert scoring["performance_weights"] == {"mce_standard": 0.5, "job_matcher": 0.3, "external_ref": 0.2}
    assert scoring["external_missing_remedy"] == "mce_weight_becomes_0.8"
    assert scoring["value_formula"]["cost_metric"] == "usd_per_pass_unit"
    assert scoring["value_formula"]["time_weighting"] == {"off_peak_discount": 0.5, "free_window": 0.0}
    assert scoring["value_formula"]["normalization"] == "min_max_within_same_job_pool"
    assert scoring["value_formula"]["free_saved_usd"] == "separate_column_not_in_cost"
    assert scoring["composite"] == {"alpha_p": 0.6, "beta_v": 0.4}
    assert scoring["tier_thresholds"] == {"premium_min_p": 0.80, "standard_min_p": 0.60}
    assert "OBJ_R" in scoring["revision_policy"]


def test_scoring_idempotent_same_input_same_score(tmp_path: Path) -> None:
    """C4 验收「重算幂等」：tmp_path 副本同一输入两次算分完全一致（含浮点逐位相等）。"""
    copy_path = tmp_path / "model_scoring_policy.yaml"
    copy_path.write_text(POLICY_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    scoring = load_scoring_policy(copy_path)
    first = score_model(0.82, 0.71, 0.65, 1.4, [0.9, 1.4, 2.6], scoring)
    second = score_model(0.82, 0.71, 0.65, 1.4, [0.9, 1.4, 2.6], scoring)
    assert first == second
    assert repr(first) == repr(second)


def test_fail_closed_missing_weight(tmp_path: Path) -> None:
    """权重缺失/段缺失一律抛 ScoringPolicyError，绝不静默给默认值。"""
    with POLICY_PATH.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    del doc["scoring"]["performance_weights"]["job_matcher"]
    broken = tmp_path / "broken_weights.yaml"
    broken.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ScoringPolicyError, match="job_matcher"):
        compute_perf_p(0.9, 0.5, 0.8, load_scoring_policy(broken))
    del doc["scoring"]["composite"]
    broken2 = tmp_path / "broken_composite.yaml"
    broken2.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ScoringPolicyError, match="composite"):
        compose_score_s(0.8, 0.5, load_scoring_policy(broken2))
    del doc["scoring"]["tier_thresholds"]
    broken3 = tmp_path / "broken_tiers.yaml"
    broken3.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ScoringPolicyError, match="tier_thresholds"):
        assign_tier(0.8, load_scoring_policy(broken3))


def test_tier_boundaries_exact() -> None:
    """档界恰好值：0.80→premium、0.60→standard，紧贴边界下侧落下一档。"""
    scoring = load_scoring_policy(POLICY_PATH)
    assert assign_tier(0.80, scoring) == "premium"
    assert assign_tier(0.7999, scoring) == "standard"
    assert assign_tier(0.60, scoring) == "standard"
    assert assign_tier(0.5999, scoring) == "economy"


def test_external_missing_remedy_reflux() -> None:
    """外部参照缺失→其权重回流 MCE（P=0.7×mce+0.3×job，仍在 [0,1]）；在位=三成分原权重。"""
    scoring = load_scoring_policy(POLICY_PATH)
    assert compute_perf_p(0.9, 0.5, None, scoring) == pytest.approx(0.7 * 0.9 + 0.3 * 0.5)
    assert compute_perf_p(0.9, 0.5, 0.8, scoring) == pytest.approx(0.5 * 0.9 + 0.3 * 0.5 + 0.2 * 0.8)
    assert 0.0 <= compute_perf_p(0.9, 0.5, None, scoring) <= 1.0


def test_value_min_max_and_composite() -> None:
    """V=池内 min-max（最便宜=1、最贵=0）；S=P^0.6×V^0.4；退化池 fail-closed。"""
    scoring = load_scoring_policy(POLICY_PATH)
    pool = [0.9, 1.4, 2.6]
    assert compute_value_v(0.9, pool) == pytest.approx(1.0)
    assert compute_value_v(2.6, pool) == pytest.approx(0.0)
    assert compute_value_v(1.4, pool) == pytest.approx(1.2 / 1.7)
    s = compose_score_s(0.8, 0.5, scoring)
    assert s == pytest.approx((0.8 ** 0.6) * (0.5 ** 0.4))
    full = score_model(0.8, 0.8, 0.8, 1.4, pool, scoring)
    assert full["tier"] == "premium"
    with pytest.raises(ScoringPolicyError, match="退化岗位池"):
        compute_value_v(1.0, [1.0, 1.0])
