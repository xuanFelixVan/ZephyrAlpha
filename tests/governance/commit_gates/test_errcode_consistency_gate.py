# [A_test] module_id: MOD-GATE_ENGINE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.governance.commit_gates.test_errcode_consistency_gate
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/governance/commit_gates/test_errcode_consistency_gate.py -q
# [TTL] task_bound

from __future__ import annotations

import types
from pathlib import Path
from unittest.mock import MagicMock

from zephyr.gov_enforcement.commit_gates.errcode_consistency_gate import (
    make_errcode_consistency_gate,
)


def _gateway(tmp_path) -> MagicMock:
    gw = MagicMock()
    gw.project_root = tmp_path
    return gw


def _trigger_file() -> list[str]:
    return ["src/zephyr/some_module/foo.py"]


class TestGateConstruction:
    def test_gate_id_and_priority(self):
        spec = make_errcode_consistency_gate()
        assert spec.gate_id == "GATE-ERRCODE-CONSISTENCY"
        assert spec.priority == 131
        assert callable(spec.check)


class TestSkipSemantics:
    def test_non_zephyr_project_skips(self, tmp_path):
        spec = make_errcode_consistency_gate()
        ok, detail = spec.check(_gateway(tmp_path), _trigger_file())
        assert ok is True
        assert "non-Zephyr" in detail

    def test_no_relevant_files_skips(self, tmp_path):
        (tmp_path / "scripts" / "governance").mkdir(parents=True)
        spec = make_errcode_consistency_gate()
        ok, detail = spec.check(_gateway(tmp_path), ["docs/some_doc.md"])
        assert ok is True
        assert detail == ""


class TestRealRepoPass:
    def test_current_repo_is_clean(self):
        # 真仓实证：Owner 收口批后（43 补登+5 改号）当前真源应为全绿
        spec = make_errcode_consistency_gate()
        gw = MagicMock()
        gw.project_root = Path(__file__).resolve().parents[3]
        ok, detail = spec.check(gw, _trigger_file())
        assert ok is True, detail


class TestBlockSemantics:
    def _fake_ssot(self, failing_message: str):
        fake = types.ModuleType("fake_ssot")

        class _Ok:
            def test_a(self):
                return None

        class _Bad:
            def test_unregistered(self):
                raise AssertionError(f"2 个 error_code 未登记: {failing_message}")

        fake.TestCodeToRegistry = _Bad
        fake.TestRegistryToCode = _Ok
        fake.TestDuplicates = _Ok
        return fake

    def test_blocks_on_assertion_and_hints_next_free(self, tmp_path, monkeypatch):
        (tmp_path / "scripts" / "governance").mkdir(parents=True)
        import zephyr.gov_enforcement.commit_gates.errcode_consistency_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_load_ssot_module", lambda _root: self._fake_ssot("ZA-BT-0027, ZA-BT-0028"))
        monkeypatch.setattr(gate_mod, "_next_free_hints", lambda *_a, **_k: "下一可用号: ZA-BT-0036")
        spec = make_errcode_consistency_gate()
        ok, detail = spec.check(_gateway(tmp_path), _trigger_file())
        assert ok is False
        assert "GATE-ERRCODE-CONSISTENCY" in detail
        assert "ZA-BT-0027" in detail
        assert "下一可用号" in detail

    def test_ssot_missing_fails_closed(self, tmp_path, monkeypatch):
        (tmp_path / "scripts" / "governance").mkdir(parents=True)
        import zephyr.gov_enforcement.commit_gates.errcode_consistency_gate as gate_mod

        def _boom(_root):
            raise RuntimeError("no such file")

        monkeypatch.setattr(gate_mod, "_load_ssot_module", _boom)
        spec = make_errcode_consistency_gate()
        ok, detail = spec.check(_gateway(tmp_path), _trigger_file())
        assert ok is False
        assert "SSoT" in detail
