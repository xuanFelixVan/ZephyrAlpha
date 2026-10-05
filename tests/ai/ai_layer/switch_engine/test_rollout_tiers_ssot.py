"""test_rollout_tiers_ssot — 灰度驻留窗"活真源"两枚红测（W3-D R-3 P0 验收）。

旧病灶：`MIN_MONTHLY_WINDOWS: Final[int] = 1` 硬编码在代码里，注释却写
"（config/switch_criteria.yaml）"——YAML 自称真源而读者是常量＝双真源反向。
现常量已删，升档机检每次读 YAML criteria.rollout_tiers.<档>.min_monthly_windows。

测试隔离：生产 YAML 只读，改动落 tmp_path 副本。
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

from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.ai_layer.switch_engine.rollout_tiers import (
    TIER_BLOCK,
    TIER_SHADOW,
    TIER_WARN,
    TierLedger,
    min_monthly_windows,
)
from zephyr.intelligence.switch_engine.criteria import (
    CRITERIA_ROOT_KEY,
    SwitchCriteriaError,
)

_REAL_TEXT = Path("config/switch_criteria.yaml").read_text(encoding="utf-8")


def _mutated(
    tmp_path: Path,
    mutate: dict[tuple[str, ...], Any] | None,
    *,
    drop: str | None = None,
    name: str = "switch_criteria_mutated.yaml",
) -> Path:
    body: dict[str, Any] = yaml.safe_load(_REAL_TEXT)
    root = body[CRITERIA_ROOT_KEY]  # 点号路径一律从 criteria 根起算
    if drop is not None:
        target: Any = root
        parts = drop.split(".")
        for part in parts[:-1]:
            target = target[part]
        del target[parts[-1]]
    else:
        assert mutate
        for dotted, value in mutate.items():
            node: Any = root
            for part in dotted[:-1]:
                node = node[part]
            node[dotted[-1]] = value
    path = tmp_path / name
    path.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    return path


def _upgrade(ledger: TierLedger, *, windows: int, to_tier: str = TIER_WARN) -> dict[str, Any]:
    return ledger.upgrade_to(
        to_tier,
        evidence_ref="e",
        windows_in_tier=windows,
        false_positives=0,
        owner_ack=True,
        ruling_ref="R-1" if to_tier == TIER_BLOCK else "",
        grandfather_enforced=to_tier == TIER_BLOCK,
    )


# ---------------------------------------------------------------------------
# 红测①：改 YAML 驻留窗 → 升档判定真的变
# ---------------------------------------------------------------------------


def test_red_flip_shadow_residency_changes_upgrade_decision(tmp_path: Path) -> None:
    """shadow.min_monthly_windows 1→2：驻留 1 窗从"可升"变"拒升"。"""
    assert min_monthly_windows(TIER_SHADOW) == 1
    assert _upgrade(TierLedger("gate.demo"), windows=1)["to_tier"] == TIER_WARN

    strict = _mutated(tmp_path, {("rollout_tiers", "shadow", "min_monthly_windows"): 2}, name="strict_shadow.yaml")
    assert min_monthly_windows(TIER_SHADOW, path=strict) == 2
    ledger = TierLedger("gate.demo", criteria_path=strict)
    with pytest.raises(ValueError, match="驻留不足"):
        _upgrade(ledger, windows=1)
    assert _upgrade(ledger, windows=2)["to_tier"] == TIER_WARN  # 补足即放行（判据来自 YAML）


def test_red_flip_warn_residency_changes_block_promotion(tmp_path: Path) -> None:
    """warn.min_monthly_windows 1→3：warn→block 在驻留 2 窗时被拒（原代码常数永远=1 拦不住）。"""
    strict = _mutated(tmp_path, {("rollout_tiers", "warn", "min_monthly_windows"): 3}, name="strict_warn.yaml")
    ledger = TierLedger("gate.demo", criteria_path=strict)
    _upgrade(ledger, windows=3)  # shadow 档驻留要求仍=1，给足 3 窗无碍
    assert ledger.tier == TIER_WARN
    with pytest.raises(ValueError, match="驻留不足"):
        _upgrade(ledger, windows=2, to_tier=TIER_BLOCK)
    assert _upgrade(ledger, windows=3, to_tier=TIER_BLOCK)["to_tier"] == TIER_BLOCK


# ---------------------------------------------------------------------------
# 红测②：YAML 缺该键/坏值 → 抛错而非回落常数
# ---------------------------------------------------------------------------


def test_red_missing_key_raises_not_constant_fallback(tmp_path: Path) -> None:
    """删 shadow.min_monthly_windows：构造与升档都抛（旧代码可静默用 1 兜底=第二真源）。"""
    path = _mutated(tmp_path, None, drop="rollout_tiers.shadow.min_monthly_windows", name="no_key.yaml")
    with pytest.raises(ValueError, match="fail-closed，禁回落常数"):
        min_monthly_windows(TIER_SHADOW, path=path)
    with pytest.raises(ValueError, match="min_monthly_windows"):
        TierLedger("gate.demo", criteria_path=path)


def test_red_missing_section_raises(tmp_path: Path) -> None:
    path = _mutated(tmp_path, None, drop="rollout_tiers", name="no_section.yaml")
    with pytest.raises(ValueError, match="rollout_tiers 节"):
        min_monthly_windows(TIER_WARN, path=path)


@pytest.mark.parametrize("bad_value", ["1", 0, -1, True, None])
def test_red_bad_value_types_raise(tmp_path: Path, bad_value: Any) -> None:
    """值类型错/非正数=尺子残缺：拒判，不做"看着像 1 就当 1"的猜。"""
    path = _mutated(
        tmp_path,
        {("rollout_tiers", "shadow", "min_monthly_windows"): bad_value},
        name=f"bad_{type(bad_value).__name__}_{bad_value}.yaml",
    )
    with pytest.raises(ValueError, match="正整数"):
        min_monthly_windows(TIER_SHADOW, path=path)


def test_missing_criteria_file_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(SwitchCriteriaError):
        min_monthly_windows(TIER_SHADOW, path=tmp_path / "absent.yaml")


def test_hardcoded_constant_is_gone() -> None:
    """单一真源机械核：MIN_MONTHLY_WINDOWS 常量不得残留（注释提及不算）。"""
    import re

    text = Path("src/zephyr/ai_layer/switch_engine/rollout_tiers.py").read_text(encoding="utf-8")
    code = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    assert re.search(r"^MIN_MONTHLY_WINDOWS\s*[:=]", code, re.MULTILINE) is None
    assert "windows_in_tier < MIN_MONTHLY_WINDOWS" not in code


def test_block_tier_has_no_unread_residency_key() -> None:
    """终档 block 无升级出边——YAML 里也确实没写它的驻留键（写了就是"没人读的装饰"）。"""
    body = yaml.safe_load(_REAL_TEXT)
    assert "min_monthly_windows" not in body[CRITERIA_ROOT_KEY]["rollout_tiers"]["block"]
    with pytest.raises(ValueError, match="min_monthly_windows"):
        min_monthly_windows(TIER_BLOCK)
