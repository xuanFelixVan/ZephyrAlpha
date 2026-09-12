# [A_test] module_id: zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §registry_mass_deletion_gate
# [MODULE] tests.governance.commit_gates.test_registry_mass_deletion_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/commit_gates/test_registry_mass_deletion_gate.py
# [MATURITY] testing
# [INVARIANTS] 只测纯逻辑核心 _is_watch_file/_yaml_entry_count/_line_delta（不触 git）
# [MODIFY-GUARD] META-TESTS-COVERAGE 补课（gate [TESTS] 声明兑现，2026-09-12 st-perf-plan-20260910）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_registry_mass_deletion_gate.py — REGISTRY-MASS-DELETION 门禁纯逻辑单测（META-TESTS 声明兑现）。"""

from __future__ import annotations

from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import (
    _is_watch_file,
    _line_delta,
    _yaml_entry_count,
)


class TestIsWatchFile:
    def test_registry_yaml_hit(self):
        assert _is_watch_file("docs/01_policies_and_standards/_registry/catalogs/universe_registry.yaml")

    def test_non_registry_miss(self):
        assert not _is_watch_file("src/zephyr/data/loader.py")


class TestYamlEntryCount:
    def test_count_entries(self):
        text = "universe_registry:\n  - universe_id: U-001\n  - universe_id: U-002\n"
        assert _yaml_entry_count(text) == 2

    def test_unparsable_returns_none(self):
        assert _yaml_entry_count("\t: : :\n") is None


class TestLineDelta:
    def test_delta(self):
        head = "a\nb\nc\n"
        staged = "a\nb\nc\nd\n"
        deleted, added = _line_delta(head, staged)
        assert added == 1 and deleted == 0, "返回序=(deleted, added)（docstring 口径）"
