# [A_test] module_id: MOD-GOV-tdm_mount_coverage_reconciler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §mount-coverage-reconciler
# [MODULE] tests.governance.audit.test_tdm_mount_coverage_reconciler
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_tdm_mount_coverage_reconciler.py — TDM 挂载义务存量对账 reconciler 单测（工单 st-tdm-mountgate-20261005）

测试组：
- TestTrigger: 模块册变更面命中矩阵（config yaml / blueprint.md / src|scripts .py → True；其他 → False）
- TestReconcile: 孤儿判红 warn+落盘 / 全平 clean / 助手不可达 fail-open warn / 永不抛
- TestScanOrphans: 三腿分类（mounted∪exempt∪marker）语义

测试隔离：monkeypatch _load_helpers（假助手+假 ledger_gen）与模块 REPO_ROOT（报告落 tmp_path），
零 PG/零生产路径写入。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import zephyr.governance.audit.tdm_mount_coverage_reconciler as rec_mod  # noqa: E402
from zephyr.governance.audit.tdm_mount_coverage_reconciler import (  # noqa: E402
    make_tdm_mount_coverage_reconciler,
)


def _fake_helpers():
    """假助手五元组：人口 3 台=已挂 MOD-M1 / 豁免 MOD-E1 / 孤儿 MOD-ORPH。"""

    def _build_mounted_set(nodes):
        return {str(n.get("module_id")) for n in nodes if n.get("module_id")}

    def _collect_map_nodes(_root):
        return [{"module_id": "MOD-M1"}]

    def _has_not_trading_marker(text):
        import re

        m = re.search(r"\[not-trading:\s*([^\]]*?)\s*\]", text or "")
        return (m.group(1).strip() or None) if m else None

    def _load_exemptions(_root):
        return {"MOD-E1": {"module_id": "MOD-E1"}}

    population = [
        {"module_id": "MOD-M1", "blueprint": "docs/03_modules/_domain_signal/m/blueprint.md"},
        {"module_id": "MOD-E1", "blueprint": "docs/03_modules/_domain_signal/e/blueprint.md"},
        {"module_id": "MOD-ORPH", "blueprint": "docs/03_modules/_domain_signal/o/blueprint.md"},
    ]
    ledger_gen = SimpleNamespace(scan_population=lambda: (population, []))
    return _build_mounted_set, _collect_map_nodes, _has_not_trading_marker, _load_exemptions, ledger_gen


@pytest.fixture()
def _isolated(tmp_path, monkeypatch):
    """隔离面：模块 REPO_ROOT→tmp_path（报告落盘与蓝图读取面）。"""
    monkeypatch.setattr(rec_mod, "REPO_ROOT", tmp_path)
    return tmp_path


class TestTrigger:
    """模块册变更面命中矩阵。"""

    def _spec(self):
        return make_tdm_mount_coverage_reconciler(gateway=SimpleNamespace())

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("config/trading_decision_map.yaml", True),
            ("config/tdm_mount_exemption_registry.yaml", True),
            ("docs/03_modules/_domain_signal/a/blueprint.md", True),
            ("src/zephyr/signal/new.py", True),
            ("scripts/tool.py", True),
            ("docs/01_policies/readme.md", False),
            ("src/zephyr/signal/data.yaml", False),
            ("random.txt", False),
        ],
    )
    def test_trigger_matrix(self, path: str, expected: bool) -> None:
        assert self._spec().trigger([path]) is expected

    def test_trigger_empty(self) -> None:
        assert self._spec().trigger([]) is False


class TestReconcile:
    """reconcile 三态：判红 warn+落盘 / clean / fail-open / 永不抛。"""

    def test_orphan_red_warns_and_writes_report(self, _isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(rec_mod, "_load_helpers", lambda: _fake_helpers())
        spec = make_tdm_mount_coverage_reconciler(gateway=SimpleNamespace())
        result = spec.reconcile(["config/trading_decision_map.yaml"], "test-sid")
        assert result.action == "warn"
        assert "MOD-ORPH" in result.detail
        report = json.loads((_isolated / ".runtime" / "tdm_mount" / "orphan_report.json").read_text(encoding="utf-8"))
        assert report["orphan_total"] == 1
        assert report["orphans"] == ["MOD-ORPH"]
        assert report["population_count"] == 3

    def test_all_settled_cleans(self, _isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        helpers = _fake_helpers()

        def _no_orphan_scan(_h):
            return {
                "orphan_total": 0,
                "orphans": [],
                "mounted_count": 3,
                "exempt_count": 0,
                "marked_count": 0,
                "population_count": 3,
            }

        monkeypatch.setattr(rec_mod, "_load_helpers", lambda: helpers)
        monkeypatch.setattr(rec_mod, "_scan_orphans", _no_orphan_scan)
        spec = make_tdm_mount_coverage_reconciler(gateway=SimpleNamespace())
        result = spec.reconcile(["docs/03_modules/_domain_signal/a/blueprint.md"], "test-sid")
        assert result.action == "clean"

    def test_helpers_missing_fails_open(self, _isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(rec_mod, "_load_helpers", lambda: None)
        spec = make_tdm_mount_coverage_reconciler(gateway=SimpleNamespace())
        result = spec.reconcile(["src/zephyr/x.py"], "test-sid")
        assert result.action == "warn"
        assert "不可达" in result.detail

    def test_never_raises_on_scanner_crash(self, _isolated: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        def _boom():
            raise RuntimeError("boom")

        monkeypatch.setattr(rec_mod, "_load_helpers", _boom)
        spec = make_tdm_mount_coverage_reconciler(gateway=SimpleNamespace())
        result = spec.reconcile(["src/zephyr/x.py"], "test-sid")
        assert result.action == "warn"
        assert "error" in result.detail


class TestScanOrphans:
    """三腿分类：mounted / exempt / marker 脱孤。"""

    def test_marker_rescues_orphan(self, _isolated: Path) -> None:
        (_isolated / "docs" / "03_modules" / "_domain_signal" / "o").mkdir(parents=True)
        bp = _isolated / "docs" / "03_modules" / "_domain_signal" / "o" / "blueprint.md"
        bp.write_text("---\nmodule_id: MOD-ORPH\n---\n[not-trading: 开发设施]\n", encoding="utf-8")
        report = rec_mod._scan_orphans(_fake_helpers())
        assert report["orphan_total"] == 0
        assert report["marked_count"] == 1

    def test_unmarked_orphan_reds(self, _isolated: Path) -> None:
        report = rec_mod._scan_orphans(_fake_helpers())
        assert report["orphans"] == ["MOD-ORPH"]
        assert report["orphan_total"] == 1
