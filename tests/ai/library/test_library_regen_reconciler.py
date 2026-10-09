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

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
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


def _stub_ingest(monkeypatch, cmds):
    """隔离①②采集入账（DB 面），并替身③④⑤三条子进程腿记录调用序。"""

    def _fake_spawn(cmd, **kwargs):
        cmds.append(list(cmd))
        return type("R", (), {"returncode": 0, "stdout": "OK: stub"})()

    monkeypatch.setattr("zephyr.shared.infra.process_pool.run_subprocess_hidden", _fake_spawn)
    _fake_conn = type("C", (), {"close": staticmethod(lambda: None)})()
    monkeypatch.setattr("zephyr.governance.depgraph_schema.get_depgraph_pg_connection", lambda: _fake_conn)
    monkeypatch.setattr("zephyr.library.collectors.collect_all", lambda names=None: {})
    monkeypatch.setattr(g, "ingest_with_shrink_guard", lambda conn, librarian, collected, actor, **kw: (0, 0, 0))


class TestFrontDoorStep:
    """⑤ 前门双投再生步（st-libfront-20261009 根治批）：尾位/传播/失败降 warn。"""

    def test_front_door_regen_is_tail_step(self, spec, monkeypatch):
        cmds: list[list[str]] = []
        _stub_ingest(monkeypatch, cmds)
        result = spec.reconcile(["src/zephyr/x.py"], "test-sid")
        assert cmds, "子进程腿未触发"
        assert cmds[-1][1] == "scripts/governance/generators/generate_front_door.py"
        assert result.action == "clean"
        assert "前门双投再生 rc=0" in str(result.detail)

    def test_front_door_failure_marks_warn(self, spec, monkeypatch):
        cmds: list[list[str]] = []

        def _fail_front_door(cmd, **kwargs):
            cmds.append(list(cmd))
            rc = 1 if cmd[1].endswith("generate_front_door.py") else 0
            return type("R", (), {"returncode": rc, "stdout": ""})()

        monkeypatch.setattr("zephyr.shared.infra.process_pool.run_subprocess_hidden", _fail_front_door)
        _fake_conn = type("C", (), {"close": staticmethod(lambda: None)})()
        monkeypatch.setattr("zephyr.governance.depgraph_schema.get_depgraph_pg_connection", lambda: _fake_conn)
        monkeypatch.setattr("zephyr.library.collectors.collect_all", lambda names=None: {})
        monkeypatch.setattr(g, "ingest_with_shrink_guard", lambda conn, librarian, collected, actor, **kw: (0, 0, 0))
        result = spec.reconcile(["src/zephyr/x.py"], "test-sid")
        assert "前门双投再生 rc=1" in str(result.detail)
        assert result.action == "warn"
