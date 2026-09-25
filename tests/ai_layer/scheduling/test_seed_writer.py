# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] tests.ai_layer.scheduling.test_seed_writer
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_seed_writer — C8 验收：种子字段全过词表校验（幽灵池/空间维双禁令）+ 写盘回读；路径全 tmp_path。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.ai_layer.scheduling.seed_writer import (
    SEG_ACCEPT,
    SEG_BUILD,
    SeedValidationError,
    build_seed,
    load_seeds,
    validate_seed,
    write_seeds,
)


def _seed(policy: dict[str, Any], **over: Any) -> dict[str, Any]:
    base = build_seed("WO-20260923-001", SEG_BUILD, "local", "给治理闸加快照缓存", policy)
    base.update(over)
    return base


# ---------------------------------------------------------------------------
# build_seed（DESIGN §2.3 字段表逐键）
# ---------------------------------------------------------------------------

def test_build_seed_field_subset(policy: dict[str, Any]) -> None:
    seed = _seed(policy)
    assert seed["task_id"] == "evo_WO-20260923-001_build"
    assert seed["resource_class"] == "light"  # local→light（E0 映射同层）
    assert seed["pool"] == "default"  # lanes 真池
    assert seed["window_type"] == "event" and seed["window_expr"] is None  # 人禁填留空
    assert seed["trading_sensitive"] is False  # light 免 E0（推导非手填）
    assert seed["schedule_truth_source"] == "config/evolution_schedule_seeds.yaml"
    assert seed["notes_zh"] == "给治理闸加快照缓存"


def test_build_seed_accept_segment_sensitive_class(policy: dict[str, Any]) -> None:
    seed = build_seed("WO-20260923-001", SEG_ACCEPT, "cpu_heavy", "C4 双窗批测", policy)
    assert seed["task_id"].endswith("_accept")
    assert seed["resource_class"] == "cpu_heavy"
    assert seed["trading_sensitive"] is True  # TRADING_SENSITIVE_CLASSES 推导


def test_build_seed_unknown_class_is_empty_and_rejected(policy: dict[str, Any]) -> None:
    seed = build_seed("WO-1", SEG_BUILD, "quantum", "x", policy)
    assert seed["resource_class"] == ""
    assert any("resource_class" in e for e in validate_seed(seed, policy))


# ---------------------------------------------------------------------------
# validate_seed（词表校验全枚举）
# ---------------------------------------------------------------------------

def test_valid_seed_has_no_errors(policy: dict[str, Any]) -> None:
    assert validate_seed(_seed(policy), policy) == []
    assert validate_seed(_seed(policy, seg=None) | {"task_id": "evo_WO-1_accept"}, policy) == []


def test_ghost_pool_ban(policy: dict[str, Any]) -> None:
    """幽灵池禁令：禁 light；禁 cpu/gpu 空间维值作泳道（daily_crypto 事故语义）。"""
    for ghost in ("light", "cpu", "gpu"):
        errors = validate_seed(_seed(policy, pool=ghost), policy)
        assert any(ghost in e for e in errors)


def test_pool_outside_lanes_rejected(policy: dict[str, Any]) -> None:
    assert any("lanes" in e for e in validate_seed(_seed(policy, pool="warp"), policy))


def test_exclusive_group_vocab(policy: dict[str, Any]) -> None:
    ok = _seed(policy, exclusive_group=["llm_local"])
    assert validate_seed(ok, policy) == []
    bad = _seed(policy, exclusive_group=["gpu_default", "warp_drive"])
    errors = validate_seed(bad, policy)
    assert any("warp_drive" in e for e in errors)
    assert not any("gpu_default" in e for e in errors)  # 词表内组合合法


def test_trading_sensitive_must_match_derivation(policy: dict[str, Any]) -> None:
    bad = _seed(policy, trading_sensitive=False)  # cpu_heavy 须为 True
    bad["resource_class"] = "cpu_heavy"
    assert any("trading_sensitive" in e for e in validate_seed(bad, policy))


def test_window_type_and_expr_rules(policy: dict[str, Any]) -> None:
    errors = validate_seed(_seed(policy, window_type="manual"), policy)
    assert any("window_type" in e for e in errors)
    errors = validate_seed(_seed(policy, window_expr="0 4 * * *"), policy)
    assert any("window_expr" in e for e in errors)  # 人禁填字段留空


def test_task_id_shape(policy: dict[str, Any]) -> None:
    bad = _seed(policy, task_id="wo-1-build")
    assert any("task_id" in e for e in validate_seed(bad, policy))
    bad = _seed(policy, task_id="evo_WO-1_dance")
    assert any("task_id" in e for e in validate_seed(bad, policy))


def test_missing_key_rejected(policy: dict[str, Any]) -> None:
    seed = _seed(policy)
    del seed["notes_zh"]
    assert any("缺字段:notes_zh" in e for e in validate_seed(seed, policy))


# ---------------------------------------------------------------------------
# 写盘回读（safe_write_text CAS；tmp_path 零生产路径）
# ---------------------------------------------------------------------------

def test_write_and_read_back(policy: dict[str, Any], tmp_path: Path) -> None:
    seeds = [
        _seed(policy),
        build_seed("WO-20260923-002", SEG_ACCEPT, "db_heavy", "CH 大重放", policy, peak_mem_gb=3.0, est_duration_min=90),
    ]
    target = write_seeds(seeds, policy, path=tmp_path / "seeds.yaml")
    assert target.exists()
    text = target.read_text(encoding="utf-8")
    assert "不建第二张排班表" in text  # 净零声明头随写随带
    loaded = load_seeds(target)
    assert len(loaded["seeds"]) == 2
    assert loaded["seeds"][1]["task_id"] == "evo_WO-20260923-002_accept"
    assert yaml.safe_load(text)["seeds"][0]["window_expr"] is None


def test_write_empty_seeds_is_valid_empty_state(policy: dict[str, Any], tmp_path: Path) -> None:
    target = write_seeds([], policy, path=tmp_path / "empty.yaml")
    assert load_seeds(target)["seeds"] == []


def test_write_rejects_invalid_batch_atomically(policy: dict[str, Any], tmp_path: Path) -> None:
    bad = _seed(policy, pool="light")
    with pytest.raises(SeedValidationError, match="light"):
        write_seeds([_seed(policy), bad], policy, path=tmp_path / "out.yaml")
    assert not (tmp_path / "out.yaml").exists()  # 任一违例=整批拒写


def test_load_missing_file_is_empty_state(tmp_path: Path) -> None:
    assert load_seeds(tmp_path / "nope.yaml") == {"seeds": []}
