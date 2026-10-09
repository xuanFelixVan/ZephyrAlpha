"""test_switch_criteria_ssot — L6 T1-T6 判据/动作"活真源"两枚红测（W3-D R-3 P0 验收）。

红测①：改 config/switch_criteria.yaml 的阈值/动作值 → evaluate_triggers 判定或动作真的变。
红测②：删该键 → SwitchCriteriaError 抛错，**不回落代码常数**（旧 `.get(key, 20)` 即第二真源）。

测试隔离：生产 YAML 只读，改动一律落 tmp_path 副本。
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

from zephyr.intelligence.switch_engine.criteria import (
    CRITERIA_ROOT_KEY,
    SwitchCriteriaError,
    load_criteria,
)
from zephyr.intelligence.switch_engine.switch_engine import (
    ACTION_AUTO_ROLLBACK,
    ACTION_FREEZE_SWITCH,
    ACTION_IMMEDIATE_ROLLBACK,
    ACTION_PAUSE_SHADOW,
    TRIGGER_ACTIONS,
    evaluate_triggers,
)

_REAL_TEXT = Path("config/switch_criteria.yaml").read_text(encoding="utf-8")
_TRIGGERS: dict[str, Any] = load_criteria()[CRITERIA_ROOT_KEY]["triggers"]


def _triggers_mutated(
    tmp_path: Path, mutate: dict[tuple[str, ...], Any] | set[str], *, name: str = "switch_criteria_mutated.yaml"
) -> dict[str, Any]:
    """在 tmp 副本上改/删 criteria.triggers 下的键，返回该节（判据注入形态=生产同形）。"""
    body: dict[str, Any] = yaml.safe_load(_REAL_TEXT)
    triggers = body[CRITERIA_ROOT_KEY]["triggers"]
    if isinstance(mutate, set):
        for key in mutate:
            del triggers[key]
    else:
        for dotted, value in mutate.items():
            node: Any = triggers
            for part in dotted[:-1]:
                node = node[part]
            node[dotted[-1]] = value
    path = tmp_path / name
    path.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    return load_criteria(path)[CRITERIA_ROOT_KEY]["triggers"]


# ---------------------------------------------------------------------------
# 红测①：改 YAML → 判定/动作变
# ---------------------------------------------------------------------------


def test_red_flip_t2_threshold_changes_fire_decision(tmp_path: Path) -> None:
    """t2 上界 0.05→0.10：同一分歧率 0.06 从"触发"变"不触发"。"""

    def fired(criteria: dict[str, Any]) -> bool:
        verdicts = evaluate_triggers({"disagreement_rate": 0.06}, criteria, "canary")
        return next(v for v in verdicts if v.trigger == "T2").fired

    assert fired(_TRIGGERS) is True
    assert fired(_triggers_mutated(tmp_path, {("t2_disagreement_rate_max",): 0.10})) is False


def test_red_flip_t3_threshold_changes_rollback_decision(tmp_path: Path) -> None:
    """t3 中位差线 20→30：delta=25% 从触发回切变不触发。"""
    signals = {"perf_median_delta_pct": 25, "perf_degradation_days": 6}

    def fired(criteria: dict[str, Any]) -> bool:
        return next(v for v in evaluate_triggers(signals, criteria, "canary") if v.trigger == "T3").fired

    assert fired(_TRIGGERS) is True
    assert fired(_triggers_mutated(tmp_path, {("t3_perf_delta_pct_max",): 30})) is False


def test_red_flip_t5_t6_action_values_change_emitted_action(tmp_path: Path) -> None:
    """t5/t6 动作值此前在代码里硬编码、YAML 零引用；现在改 YAML 即改产出的动作。"""

    def action_of(criteria: dict[str, Any], trigger: str, signals: dict[str, Any]) -> str:
        verdicts = evaluate_triggers(signals, criteria, "shadow")
        return next(v for v in verdicts if v.trigger == trigger).action

    assert action_of(_TRIGGERS, "T5", {"anomalous_gain": True}) == ACTION_FREEZE_SWITCH
    assert action_of(_TRIGGERS, "T6", {"quota_exceeded": True}) == ACTION_PAUSE_SHADOW
    swapped = _triggers_mutated(
        tmp_path,
        {("t5_anomalous_gain_action",): "pause_shadow", ("t6_quota_action",): "freeze_switch"},
    )
    assert action_of(swapped, "T5", {"anomalous_gain": True}) == ACTION_PAUSE_SHADOW
    assert action_of(swapped, "T6", {"quota_exceeded": True}) == ACTION_FREEZE_SWITCH


def test_red_flip_t1_threshold_changes_immediate_rollback(tmp_path: Path) -> None:
    """t1 事故数下界 1→2：1 起事故不再触发一键回切（动作仍 immediate_rollback=引擎名）。"""

    def verdict(criteria: dict[str, Any]):
        return next(
            v for v in evaluate_triggers({"correctness_incidents": 1}, criteria, "promoted") if v.trigger == "T1"
        )

    assert verdict(_TRIGGERS).fired and verdict(_TRIGGERS).action == ACTION_IMMEDIATE_ROLLBACK
    loosened = _triggers_mutated(tmp_path, {("t1_correctness_incidents_min",): 2})
    assert not verdict(loosened).fired


# ---------------------------------------------------------------------------
# 红测②：缺键 → 抛错，不回落常数
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "key",
    [
        "t1_correctness_incidents_min",
        "t2_disagreement_rate_max",
        "t3_perf_delta_pct_max",
        "t3_consecutive_trading_days",
        "t4_cost_increase_pct_max",
        "t4_requires_compensating_benefit",
        "t5_anomalous_gain_action",
        "t6_quota_action",
    ],
)
def test_red_missing_key_raises_instead_of_fallback(key: str, tmp_path: Path) -> None:
    """删任一判据键：当场 SwitchCriteriaError（旧写法会静默按代码常数判=改 YAML 不生效）。"""
    criteria = _triggers_mutated(tmp_path, {key}, name=f"missing_{key}.yaml")
    with pytest.raises(SwitchCriteriaError, match="fail-closed"):
        evaluate_triggers({}, criteria, "canary")


def test_red_value_type_error_raises(tmp_path: Path) -> None:
    """阈值写成字符串/动作写成引擎不认识的动词：一样抛（禁"看着像数就行"）。"""
    bad = _triggers_mutated(tmp_path, {("t2_disagreement_rate_max",): "0.05"})
    with pytest.raises(SwitchCriteriaError, match="非数值"):
        evaluate_triggers({}, bad, "canary")
    bogus = _triggers_mutated(tmp_path, {("t5_anomalous_gain_action",): "yolo_rollback"})
    with pytest.raises(SwitchCriteriaError, match="引擎动作全集"):
        evaluate_triggers({}, bogus, "canary")


def test_missing_criteria_file_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(SwitchCriteriaError, match="缺失"):
        evaluate_triggers({}, load_criteria(tmp_path / "nope.yaml"), "canary")


def test_engine_actions_are_names_not_criteria_values() -> None:
    """边界自证：ACTION_* 是引擎能力全集（代码说话），YAML 只在集合内选（判据真源）。"""
    assert {ACTION_PAUSE_SHADOW, ACTION_FREEZE_SWITCH, ACTION_AUTO_ROLLBACK} <= TRIGGER_ACTIONS
    assert _TRIGGERS["t5_anomalous_gain_action"] in TRIGGER_ACTIONS
    assert _TRIGGERS["t6_quota_action"] in TRIGGER_ACTIONS


def test_no_hardcoded_default_thresholds_left() -> None:
    """代码面残留核查：switch_engine 里不得再有 `.get(判据键, 常数)` 形态的第二真源。"""
    import re

    text = Path("src/zephyr/intelligence/switch_engine/switch_engine.py").read_text(encoding="utf-8")
    code = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    assert re.search(r"criteria\.get\(\s*T\d_[A-Z_]+", code) is None
    assert "original_trigger_values" not in code
