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
    """观测面=git index，基线=HEAD——只阻断本次新增，存量不连坐（2026-09-16 事故治本）。"""

    _KEYS = (
        "unregistered_code",
        "undeclared_prefix",
        "stale_entry",
        "registry_dup_code",
        "registry_missing_field",
        "unsanctioned_duplicate",
        "rotten_allowlist",
    )

    def _viol(self, **over) -> dict[str, set[str]]:
        return {k: set(over.get(k, ())) for k in self._KEYS}

    def _fake_ssot(
        self,
        now: dict[str, set[str]],
        base: dict[str, set[str]] | None = None,
        calls: list | None = None,
    ):
        """伪 SSoT：tree=None→now（index 面），tree="HEAD"→base（基线面）；calls 记录被问过的观测面。"""
        fake = types.ModuleType("fake_ssot")
        baseline = self._viol() if base is None else base

        def collect_violations(*, tree=None):
            if calls is not None:
                calls.append(tree)
            return dict(baseline if tree == "HEAD" else now)

        fake.collect_violations = collect_violations
        return fake

    def test_clean_index_skips_baseline_scan(self, tmp_path, monkeypatch):
        """常态零额外开销钉：index 面全绿时禁扫 HEAD 基线（实测 ≈2.7s/次，本门禁每个
        含 src/zephyr 的提交都跑——基线差分不得把常态提交变慢一倍）。"""
        (tmp_path / "scripts" / "governance").mkdir(parents=True)
        import zephyr.gov_enforcement.commit_gates.errcode_consistency_gate as gate_mod

        calls: list = []
        monkeypatch.setattr(
            gate_mod, "_load_ssot_module", lambda _root: self._fake_ssot(self._viol(), None, calls)
        )
        spec = make_errcode_consistency_gate()
        ok, detail = spec.check(_gateway(tmp_path), _trigger_file())
        assert ok is True and detail == ""
        assert calls == [None], f"全绿必须短路基线扫描（只问 index 面）: {calls}"

    def test_blocks_on_new_violation_and_hints_next_free(self, tmp_path, monkeypatch):
        (tmp_path / "scripts" / "governance").mkdir(parents=True)
        import zephyr.gov_enforcement.commit_gates.errcode_consistency_gate as gate_mod

        now = self._viol(unregistered_code={"ZA-BT-0027", "ZA-BT-0028"})
        monkeypatch.setattr(gate_mod, "_load_ssot_module", lambda _root: self._fake_ssot(now))
        monkeypatch.setattr(gate_mod, "_next_free_hints", lambda *_a, **_k: "下一可用号: ZA-BT-0036")
        spec = make_errcode_consistency_gate()
        ok, detail = spec.check(_gateway(tmp_path), _trigger_file())
        assert ok is False
        assert "GATE-ERRCODE-CONSISTENCY" in detail
        assert "ZA-BT-0027" in detail
        assert "下一可用号" in detail

    def test_inherited_violation_does_not_block(self, tmp_path, monkeypatch):
        """回归锚（2026-09-16 全局卡死 4 小时）：HEAD 基线已有的存量违规禁阻断无辜提交。"""
        (tmp_path / "scripts" / "governance").mkdir(parents=True)
        import zephyr.gov_enforcement.commit_gates.errcode_consistency_gate as gate_mod

        stale = self._viol(stale_entry={"ZA-PA-0031|PfAllocError|src/zephyr/pf_core/alloc.py"})
        monkeypatch.setattr(gate_mod, "_load_ssot_module", lambda _root: self._fake_ssot(stale, stale))
        spec = make_errcode_consistency_gate()
        ok, detail = spec.check(_gateway(tmp_path), _trigger_file())
        assert ok is True, detail
        assert detail == ""

    def test_mixed_blocks_only_on_introduced(self, tmp_path, monkeypatch):
        (tmp_path / "scripts" / "governance").mkdir(parents=True)
        import zephyr.gov_enforcement.commit_gates.errcode_consistency_gate as gate_mod

        base = self._viol(unregistered_code={"ZA-PA-0031"})
        now = self._viol(unregistered_code={"ZA-PA-0031", "ZA-BT-0027"})
        monkeypatch.setattr(gate_mod, "_load_ssot_module", lambda _root: self._fake_ssot(now, base))
        monkeypatch.setattr(gate_mod, "_next_free_hints", lambda *_a, **_k: "")
        spec = make_errcode_consistency_gate()
        ok, detail = spec.check(_gateway(tmp_path), _trigger_file())
        assert ok is False
        assert "ZA-BT-0027" in detail
        assert "ZA-PA-0031" not in detail  # 存量不进阻断证据（归属其责任人）

    def test_ssot_without_collect_violations_fails_closed(self, tmp_path, monkeypatch):
        """SSoT 落后于门禁（无可差分口径）= fail-closed，禁退回无基线的逐断言遍历。"""
        (tmp_path / "scripts" / "governance").mkdir(parents=True)
        import zephyr.gov_enforcement.commit_gates.errcode_consistency_gate as gate_mod

        legacy = types.ModuleType("legacy_ssot")
        legacy.TestCodeToRegistry = type("TestCodeToRegistry", (), {"test_a": lambda self: None})
        monkeypatch.setattr(gate_mod, "_load_ssot_module", lambda _root: legacy)
        spec = make_errcode_consistency_gate()
        ok, detail = spec.check(_gateway(tmp_path), _trigger_file())
        assert ok is False
        assert "collect_violations" in detail

    def test_baseline_unavailable_falls_back_strict(self, tmp_path, monkeypatch):
        """基线不可得（如注册表在 HEAD 尚不存在）→ 退严格口径：NOW 全量视为本次新增。"""
        (tmp_path / "scripts" / "governance").mkdir(parents=True)
        import zephyr.gov_enforcement.commit_gates.errcode_consistency_gate as gate_mod

        fake = types.ModuleType("fake_ssot")

        def collect_violations(*, tree=None):
            if tree == "HEAD":
                raise FileNotFoundError("error_code 注册表在观测面 [HEAD] 上不存在")
            return self._viol(unregistered_code={"ZA-BT-0027"})

        fake.collect_violations = collect_violations
        monkeypatch.setattr(gate_mod, "_load_ssot_module", lambda _root: fake)
        monkeypatch.setattr(gate_mod, "_next_free_hints", lambda *_a, **_k: "")
        spec = make_errcode_consistency_gate()
        ok, detail = spec.check(_gateway(tmp_path), _trigger_file())
        assert ok is False
        assert "ZA-BT-0027" in detail

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
