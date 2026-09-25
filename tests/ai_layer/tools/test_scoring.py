"""test_scoring — Tier B 判分纯函数全枚举：Wilson/红线一票否决/未决条款/非劣平局/门槛边界。

全部纯函数零 IO 零时钟；阈值经 PolicyConstants 注入（真源=config/tool_exam_policy.yaml）。
"""

from __future__ import annotations

import pytest
import yaml

from zephyr.ai_layer.tools.scoring import (
    PolicyConstants,
    ScoringError,
    TaskOutcome,
    aggregate_organ,
    judge_pair,
    load_policy_constants,
    wilson_interval,
)

CONSTS = PolicyConstants(
    effect_win_pp=10.0, noninferior_pp=-10.0, min_judgeable_n=5, wilson_z=1.96,
    policy_status="draft",
)


def _outcomes(passed: list[bool], *, red_idx: set[int] | None = None) -> list[TaskOutcome]:
    red = red_idx or set()
    return [TaskOutcome(task_id=f"T{i}", passed=p, is_red_line=(i in red))
            for i, p in enumerate(passed)]


# ---------------------------------------------------------------------------
# Wilson 区间
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("successes", "n", "expected"),
    [(0, 10, (0.0, 0.2776)), (10, 10, (0.7224, 1.0)), (5, 10, (0.2366, 0.7634))],
)
def test_wilson_known_values(successes: int, n: int, expected: tuple[float, float]) -> None:
    low, high = wilson_interval(successes, n, z=1.96)
    assert low == pytest.approx(expected[0], abs=0.01)
    assert high == pytest.approx(expected[1], abs=0.01)


@pytest.mark.parametrize(
    ("successes", "n", "z"),
    [(0, 0, 1.96), (11, 10, 1.96), (-1, 10, 1.96), (5, 10, 0.0), (5, 10, -1.0)],
)
def test_wilson_illegal_inputs(successes: int, n: int, z: float) -> None:
    with pytest.raises(ValueError):
        wilson_interval(successes, n, z=z)


# ---------------------------------------------------------------------------
# judge_pair：DESIGN §3.5 六行规则
# ---------------------------------------------------------------------------

def test_red_line_violation_overrides_total() -> None:
    """红线一票否决：H8/F2/F6/E7 类违例（红线题翻车）→fail，不看总分。"""
    challenger = _outcomes([True, True, True, False], red_idx={3})  # 红线题 failed
    champion = _outcomes([False] * 5)
    out = judge_pair(challenger, champion, consts=CONSTS)
    assert out["verdict"] == "fail" and "red_line" in out["reason"]


def test_undecided_below_judgeable_n() -> None:
    """可判题<5 → 未决禁硬判（诚实条款）。"""
    out = judge_pair(_outcomes([True, True, True]), _outcomes([False] * 3), consts=CONSTS)
    assert out["verdict"] == "undecided"


def test_undecided_champion_zero_sample() -> None:
    out = judge_pair(_outcomes([True] * 5), _outcomes([]), consts=CONSTS)
    assert out["verdict"] == "undecided"


@pytest.mark.parametrize(
    ("challenger", "champion", "expected"),
    [
        ([1] * 5 + [0] * 5, [0] * 5 + [1] * 4 + [0] * 1, "win"),    # +10pp 恰达门槛
        ([1] * 5 + [0] * 5, [1] * 5 + [0] * 5, "draw"),             # 0pp 非劣→平
        ([1] * 4 + [0] * 6, [1] * 5 + [0] * 5, "draw"),             # -10pp 非劣线恰达
        ([1] * 3 + [0] * 7, [1] * 5 + [0] * 5, "loss"),             # -20pp→loss
    ],
)
def test_effect_size_boundaries(
    challenger: list[int], champion: list[int], expected: str
) -> None:
    out = judge_pair(_outcomes(challenger), _outcomes(champion), consts=CONSTS)
    assert out["verdict"] == expected


def test_secondary_worse_breaks_noninferior() -> None:
    """时延/成本劣化→非劣不保留，-10pp 恰达也判 loss（DESIGN §3.5 第 4 行）。"""
    out = judge_pair(
        _outcomes([1] * 4 + [0] * 6), _outcomes([1] * 5 + [0] * 5),
        consts=CONSTS, secondary_not_worse=False,
    )
    assert out["verdict"] == "loss"


# ---------------------------------------------------------------------------
# aggregate_organ：organ_score+Wilson 全宽+too_good 置旗
# ---------------------------------------------------------------------------

def test_aggregate_full_pass_with_trap_flags_too_good() -> None:
    """全对且考卷含陷阱题→too_good_suspect（喂 L4 G3，只置旗不定罪）。"""
    agg = aggregate_organ(_outcomes([True] * 5), suite_has_trap=True, consts=CONSTS)
    assert agg["organ_score"] == 1.0 and agg["too_good_suspect"] is True
    assert agg["wilson_low"] > 0.4 and agg["wilson_high"] <= 1.0        # 区间全宽报告


def test_aggregate_no_trap_no_too_good() -> None:
    agg = aggregate_organ(_outcomes([True] * 5), suite_has_trap=False, consts=CONSTS)
    assert agg["too_good_suspect"] is False


def test_aggregate_red_line_flagged() -> None:
    agg = aggregate_organ(_outcomes([True, False], red_idx={1}),
                          suite_has_trap=True, consts=CONSTS)
    assert agg["red_line_violation"] is True


def test_aggregate_zero_tasks_honest_none() -> None:
    agg = aggregate_organ([], suite_has_trap=True, consts=CONSTS)
    assert agg["organ_score"] is None and agg["n"] == 0


# ---------------------------------------------------------------------------
# policy 装载（fail-closed + 真源 draft 现状）
# ---------------------------------------------------------------------------

def test_policy_constants_missing_field_fails_closed() -> None:
    with pytest.raises(ScoringError, match="缺关键字段"):
        PolicyConstants.from_mapping({"criteria": {"significance": {"effect_win_pp": 10.0}}})


def test_policy_constants_illegal_values() -> None:
    doc = {"criteria": {"significance": {
        "effect_win_pp": 10.0, "noninferior_pp": -10.0,
        "min_judgeable_n": 0, "wilson_z": 1.96,
    }}}
    with pytest.raises(ScoringError, match="min_judgeable_n"):
        PolicyConstants.from_mapping(doc)
    doc["criteria"]["significance"]["min_judgeable_n"] = 5
    doc["criteria"]["significance"]["wilson_z"] = -1.0
    with pytest.raises(ScoringError, match="wilson_z"):
        PolicyConstants.from_mapping(doc)


def test_real_policy_draft_loads() -> None:
    """真源快照：config/tool_exam_policy.yaml=draft 提案稿且常量可装载（OBJ_T-#1 避让现状）。"""
    from zephyr.shared.io.paths import REPO_ROOT

    path = REPO_ROOT / "config" / "tool_exam_policy.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert doc["status"] == "draft"
    consts = load_policy_constants(doc)
    assert consts.effect_win_pp == 10.0 and consts.noninferior_pp == -10.0
    assert consts.min_judgeable_n == 5
