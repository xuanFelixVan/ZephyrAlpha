"""图16 门禁对抗测试（st-fig16-20261005 立项批配套；先例 test_trading_day_cycle_map_gate）。

判据=自写校验必须先证明自己能红，再声称绿（六图终局卷 §5 防腐面）。
基座策略：加载真实 config/governance_legislation_map.yaml 作底 → 深拷贝微扰 → 红用例；
绿用例=真实图原样过 gate（触发面命中/live=False 结构面）。
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[4]
VALIDATORS_DIR = REPO / "scripts" / "governance" / "d5_architecture" / "validators"
MAP_REL = "config/governance_legislation_map.yaml"

sys.path.insert(0, str(VALIDATORS_DIR))

from validate_governance_legislation_map import validate_structure  # noqa: E402

import zephyr.gov_enforcement.commit_gates.map_family.governance_legislation_map_gate as gate_mod  # noqa: E402
from zephyr.gov_enforcement.commit_gates.map_family.governance_legislation_map_gate import _check  # noqa: E402


class _FakeGW:
    repo_root = str(REPO)


def _load_map() -> dict:
    return yaml.safe_load((REPO / MAP_REL).read_text(encoding="utf-8"))


def _trigger_files() -> list[str]:
    return [MAP_REL]


# ── gate 层：触发/skip/绿 ──────────────────────────────────────────────


def test_gate_skips_unrelated_files() -> None:
    ok, detail = _check(_FakeGW(), ["docs/03_modules/README.md"])
    assert ok is True
    assert "skip" in detail


def test_gate_real_map_green() -> None:
    ok, detail = _check(_FakeGW(), _trigger_files())
    assert ok is True, detail


def test_gate_empty_files_pass() -> None:
    ok, _detail = _check(_FakeGW(), [])
    assert ok is True


# ── gate 层：fail-closed 红 ────────────────────────────────────────────


def test_gate_blocks_on_corrupted_map(monkeypatch, tmp_path) -> None:
    bad = tmp_path / "bad_map.yaml"
    bad.write_text("states: [ { this is: not: valid yaml", encoding="utf-8")
    monkeypatch.setattr(gate_mod, "_MAP_PATH", bad)
    ok, detail = _check(_FakeGW(), _trigger_files())
    assert ok is False
    assert "fail-closed" in detail


def test_gate_blocks_on_structure_error(monkeypatch, tmp_path) -> None:
    data = _load_map()
    data["states"].append(
        {
            "state_id": "D16-S7",
            "value": "proposed",
            "name_zh": "幽灵",
            "terminal": False,
            "note_zh": "x",
            "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
        }
    )
    bad = tmp_path / "ghost_map.yaml"
    bad.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    monkeypatch.setattr(gate_mod, "_MAP_PATH", bad)
    ok, detail = _check(_FakeGW(), _trigger_files())
    assert ok is False
    assert "CV-01" in detail and "proposed" in detail


# ── validator 层：结构判据能红（gate 同源判据直证） ─────────────────────


def test_validator_illegal_transition_red() -> None:
    data = _load_map()
    data["transitions"].append(
        {
            "transition_id": "D16-T97",
            "from_state": ["void"],
            "to_state": "active",
            "name_zh": "墓碑复活",
            "note_zh": "注入",
            "source_anchors": ["scripts/governance/next_ruling_id.py"],
        }
    )
    errs = validate_structure(copy.deepcopy(data), REPO, [])
    assert any("终态" in e and "void" in e for e in errs)


def test_validator_instance_key_in_nodes_red() -> None:
    data = _load_map()
    data["states"][0]["ruling_id"] = "裁定#1"
    errs = validate_structure(copy.deepcopy(data), REPO, [])
    assert any("实例" in e and "ruling_id" in e for e in errs)
