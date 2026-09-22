# [A_test] module_id: MOD-LIB-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LIB-001 | docs/03_modules/_domain_library/blueprint.md | §1
# [MODULE] tests.library.test_library_regen_reconciler
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-LIB-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_library_regen_reconciler.py — 图书馆 post-commit 刷新 reconciler 单测（ulib3 T4）

测试组：
- trigger：src/scripts/data/catalogs 命中；纯 docs/library 生成视图不命中
- file_ops 显式声明制（read/write，禁 delete/move）
- reconcile fail-soft：采集异常（monkeypatch collect_all）→ action=warn 不抛

测试隔离：tmp_path 项目根；DB 相关步骤经 monkeypatch 隔离。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import zephyr.library.library_regen_reconciler as g  # noqa: E402
from zephyr.governance.audit.reconciliation_registry import ReconciliationRegistry  # noqa: E402


@pytest.fixture()
def spec(tmp_path):
    return g.make_library_regen_reconciler(type("Gw", (), {"project_root": str(tmp_path)})())


class TestTrigger:
    def test_src_hits(self, spec, tmp_path):
        assert spec.trigger([str(tmp_path / "src/zephyr/library/lookup.py")]) is True

    def test_catalogs_hit(self, spec, tmp_path):
        assert spec.trigger([str(tmp_path / "docs/01_policies_and_standards/_registry/catalogs/x.yaml")]) is True

    def test_pure_views_miss(self, spec, tmp_path):
        assert spec.trigger([str(tmp_path / "docs/library/code.md")]) is False


class TestSpecContract:
    def test_registered_in_registry(self):
        reg = ReconciliationRegistry()
        reg.merge_external_specs()
        assert any(s.gate_id == "LIBRARY-REGEN" for s in reg.specs)

    def test_file_ops_explicit(self, spec):
        assert spec.file_ops == frozenset({"read", "write"})


class TestFailSoft:
    def test_collect_failure_warns(self, spec, monkeypatch):
        def _boom(names=None):
            raise RuntimeError("pg down")

        monkeypatch.setattr("zephyr.library.collectors.collect_all", _boom)
        result = spec.reconcile(["src/zephyr/x.py"], "test-sid")
        assert result.action == "warn"
        assert "失败" in str(result.detail)
