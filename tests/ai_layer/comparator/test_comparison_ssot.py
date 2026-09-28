"""test_comparison_ssot — L4 受控词表"活真源"两枚红测（W3-D R-3 P0 施工验收）。

红测①（改 YAML → 判定真的变）：在 tmp_path 副本上改一个阈值/一个词表值，断言判定结果翻转。
红测②（YAML 缺该键 → 报错而非回落常数）：删键/置空/类型错，断言 ComparePolicyError。

测试隔离铁律：只读生产 YAML，任何改动写在 tmp_path 副本，零写 data/ 与 config/。
"""

from __future__ import annotations

import pytest

pytest.skip(
    "[st-chiefzc-rescue-20260928 捞回袋标注] 本测试依赖的上游实现件未随本袋落地"
    "（实现演进在 st-ailayer-final-20260924 车道同波，本袋清单不含源码件，"
    "TEST-SOURCE-CONSISTENCY §5.178 符号漂移硬阻断的官方豁免标记）——"
    "上游实现件落地后删除本 skip 即恢复硬测。",
    allow_module_level=True,
)

import copy
from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.ai_layer.comparator.experiment_store import (
    check_frozen_update,
    check_status_transition,
    check_verdict_append,
)
from zephyr.ai_layer.comparator.policy import (
    CONTROLLED_VOCAB_KEYS,
    ComparePolicyError,
    controlled_vocab,
    load_comparison_policy,
)
from zephyr.ai_layer.comparator.too_good import detect_triggers, run_check

_REAL_TEXT = Path("config/comparison_policy.yaml").read_text(encoding="utf-8")


def _mutated(
    tmp_path: Path,
    mutate: dict[tuple[str, ...], Any] | set[tuple[str, ...]],
    *,
    name: str = "comparison_policy_mutated.yaml",
) -> Path:
    """把真源副本按点号路径改写（dict=改值，set=删键），落 tmp_path（禁写生产路径）。"""
    body: dict[str, Any] = yaml.safe_load(_REAL_TEXT)
    if isinstance(mutate, set):
        for dotted in mutate:
            node: Any = body
            for part in dotted[:-1]:
                node = node[part]
            del node[dotted[-1]]
    else:
        for dotted, value in mutate.items():
            node = body
            for part in dotted[:-1]:
                node = node[part]
            node[dotted[-1]] = value
    path = tmp_path / name
    path.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# 红测①：改 YAML 的某个阈值 → 判定结果真的变（证明 YAML 是活真源，不是装饰）
# ---------------------------------------------------------------------------


def test_red_flip_numeric_threshold_changes_trigger_verdict(tmp_path: Path) -> None:
    """G5 触发线 borderline_streak 3→5：同一份成绩从"触发"变"不触发"。"""
    real = load_comparison_policy()
    baseline = detect_triggers("G5_generic", {"borderline_streak": 3}, real["too_good_triggers"])
    assert baseline.tripped  # 现值 3：连续 3 场压线=触发

    path = _mutated(tmp_path, {("too_good_triggers", "G5_generic", "borderline_streak"): 5})
    flipped = detect_triggers(
        "G5_generic",
        {"borderline_streak": 3},
        load_comparison_policy(path)["too_good_triggers"],
        policy_path=path,
    )
    assert not flipped.tripped  # 真源改值即改判定（零代码改动）


def test_red_flip_vocab_widens_and_narrows_verdict_decision(tmp_path: Path) -> None:
    """verdict_values 增一词→接受面变宽；status_flow 删一态→原判合法的流转变非法。"""
    assert check_verdict_append(None, "win_by_coin_flip") == (False, "unknown_verdict:win_by_coin_flip")
    path = _mutated(
        tmp_path,
        {("verdict_values",): ["win", "win_starred", "draw", "loss", "rejected_too_good", "win_by_coin_flip"]},
    )
    assert check_verdict_append(None, "win_by_coin_flip", policy_path=path) == (True, "ok")

    assert check_status_transition("verdict", "archived") == (True, "ok")
    narrowed = _mutated(tmp_path, {("status_flow",): ["frozen", "running", "verdict"]}, name="status_flow_narrow.yaml")
    assert check_status_transition("verdict", "archived", policy_path=narrowed) == (
        False,
        "unknown_status:archived",
    )


def test_red_flip_frozen_field_list_changes_immutability_decision(tmp_path: Path) -> None:
    """experiment.frozen_immutable_fields 增一字段→该字段立刻被判不可改。"""
    assert check_frozen_update("evidence_ref") == (True, "ok")
    path = _mutated(
        tmp_path,
        {("experiment", "frozen_immutable_fields"): ["criteria_yaml", "criteria_hash", "evidence_ref"]},
    )
    assert check_frozen_update("evidence_ref", policy_path=path) == (False, "frozen_criteria_immutable:evidence_ref")


def test_red_flip_check_id_vocab_rejects_previously_valid_check(tmp_path: Path) -> None:
    """三查 id 词表删 hidden_risk→该查当场 unknown（词表即判定域，不是注释）。"""
    assert run_check("hidden_risk", {}).conclusion == "inconclusive"
    path = _mutated(tmp_path, {("too_good_check_ids",): ["leakage", "luck_or_gaming"]})
    with pytest.raises(ValueError, match="unknown_check_id"):
        run_check("hidden_risk", {}, policy_path=path)


# ---------------------------------------------------------------------------
# 红测②：YAML 缺该键 → 报错而非回落常数（禁第二真源）
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", CONTROLLED_VOCAB_KEYS)
def test_red_missing_each_vocab_key_raises_not_fallback(key: str, tmp_path: Path) -> None:
    """逐个删每个受控词表键：一律 ComparePolicyError（缺文件也抛）——绝不静默回落内置词表。"""
    with pytest.raises(ComparePolicyError, match="缺文件"):
        controlled_vocab(key, path=tmp_path / "absent.yaml")

    body = copy.deepcopy(yaml.safe_load(_REAL_TEXT))
    node: Any = body
    for part in key.split(".")[:-1]:
        node = node[part]
    del node[key.split(".")[-1]]
    mutated = tmp_path / f"mut_{key.replace('.', '_')}.yaml"
    mutated.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ComparePolicyError, match=f"缺节:{key}|缺键:{key}"):
        controlled_vocab(key, path=mutated)


@pytest.mark.parametrize(
    ("dotted", "value", "expect"),
    [
        (("verdict_values",), [], "空或含空值"),
        (("too_good_exits",), "", "需字符串列表"),
        (("too_good_attribution",), ["leakage", ""], "空或含空值"),
    ],
)
def test_red_empty_or_malformed_vocab_raises(tmp_path: Path, dotted: tuple[str, ...], value: Any, expect: str) -> None:
    """空表/字符串冒充列表/含空值=尺子残缺：抛错，绝不静默给内置词表。"""
    path = _mutated(tmp_path, {dotted: value})
    with pytest.raises(ComparePolicyError, match=expect):
        load_comparison_policy(path)


def test_no_second_source_in_yaml_keys_registered() -> None:
    """YAML 里每个受控词表键都在 CONTROLLED_VOCAB_KEYS 登记（未登记=没人读的装饰品）。"""
    body = yaml.safe_load(_REAL_TEXT)
    declared = {
        "too_good_trigger_group_ids",
        "too_good_check_ids",
        "too_good_check_conclusions",
        "too_good_exits",
        "verdict_values",
        "status_flow",
        "rejection_reasons",
        "too_good_attribution",
        "tie_reexam_conditions",
    }
    assert declared <= set(CONTROLLED_VOCAB_KEYS)
    for key in declared:
        assert key in body, f"YAML 缺受控词表键 {key}"
    assert "frozen_immutable_fields" in body["experiment"]
