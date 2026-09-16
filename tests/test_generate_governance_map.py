# [BLUEPRINT] MOD-ALT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.test_generate_governance_map
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] permanent
"""generate_governance_map 单测:族分类优先级/头解析/人工层保留/接线四态(AST import 边/__all__/散文/importlib 动态)。

零真实仓库依赖:REPO_ROOT/OUTPUT_PATH monkeypatch 到 tmp_path。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parent
_SCRIPTS = _REPO_ROOT / "scripts" / "governance"
for p in (str(_REPO_ROOT / "src"), str(_SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import generate_governance_map as g  # noqa: E402


class TestClassifyFamily:
    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("src/zephyr/autonomy_core/kill_switch_orchestrator.py", "L3_fuse"),
            ("src/zephyr/shared/resilience/circuit_breaker.py", "L3_fuse"),
            ("src/zephyr/trading/process_reaper.py", "L4_reap"),
            ("src/zephyr/gov_drift/orphan_scanner.py", "L4_reap"),
            ("src/zephyr/infrastructure/auto_fix_engine/self_heal_agent.py", "L5_selfheal"),
            ("src/zephyr/governance/audit/reconcile_worker.py", "L5_selfheal"),
            ("src/zephyr/trading/resource_optimization.py", "L2_resource"),
            ("src/zephyr/infrastructure/system_telemetry/watchdog.py", "L1_monitor"),
            ("src/zephyr/trading/health_monitor.py", "L1_monitor"),
            ("src/zephyr/shared/infra/process_pool.py", "L0_lifecycle"),
            ("src/zephyr/trading/lifecycle_manager.py", "L0_lifecycle"),
            ("src/zephyr/trading/status_dashboard.py", "L6_audit"),
            ("src/zephyr/trading/auto_runtime_core.py", None),
        ],
    )
    def test_priority_and_universe(self, path, expected):
        assert g.classify_family(path) == expected

    def test_business_plane_excluded_from_scan(self, tmp_path, monkeypatch):
        monkeypatch.setattr(g, "REPO_ROOT", tmp_path)
        for rel in (
            "src/zephyr/data/heartbeat_monitor.py",
            "src/zephyr/trading/health_monitor.py",
        ):
            f = tmp_path / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("# [MODULE] x\n", encoding="utf-8")
        mods = g.scan()
        paths = [m["path"] for ms in mods.values() for m in ms]
        assert "src/zephyr/trading/health_monitor.py" in paths
        assert all(not p.startswith("src/zephyr/data/") for p in paths)


class TestParseHeader:
    def test_extracts_fields(self, tmp_path):
        f = tmp_path / "mod.py"
        f.write_text(
            "# [MODULE] zephyr.trading.process_reaper\n"
            "# [DOMAIN] D_INFRA_RUNTIME\n"
            "# [CONSUMERS] Task Scheduler; scripts/x.ps1\n"
            "# [MATURITY] production\n"
            "# [TTL] permanent\n"
            "import os\n",
            encoding="utf-8",
        )
        h = g.parse_header(f)
        assert h["module"] == "zephyr.trading.process_reaper"
        assert h["domain"] == "D_INFRA_RUNTIME"
        assert "Task Scheduler" in h["consumers"]
        assert h["maturity"] == "production"


class TestBuildDocument:
    def _seed_repo(self, tmp_path: Path) -> None:
        f = tmp_path / "src" / "zephyr" / "trading" / "process_reaper.py"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(
            "# [MODULE] zephyr.trading.process_reaper\n"
            "# [DOMAIN] D_INFRA_RUNTIME\n"
            "# [CONSUMERS] Task Scheduler\n"
            "import os\n",
            encoding="utf-8",
        )
        consumer = tmp_path / "src" / "zephyr" / "other.py"
        consumer.parent.mkdir(parents=True, exist_ok=True)
        consumer.write_text("from zephyr.trading import process_reaper\n", encoding="utf-8")

    def test_first_build_uses_defaults(self, tmp_path, monkeypatch):
        self._seed_repo(tmp_path)
        monkeypatch.setattr(g, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(g, "OUTPUT_PATH", tmp_path / "config" / "governance_operations_map.yaml")
        doc = g.build_document(dry_run=False)
        assert doc["map_id"] == "GOMAP-001"
        assert doc["counts"]["total_modules"] == 1
        assert [l["id"] for l in doc["pipeline"]["layers"]] == [f"GOM-L{i}" for i in range(7)]
        assert doc["families"]["L4_reap"][0]["wiring"] == "wired"

    def test_human_layer_preserved_on_rebuild(self, tmp_path, monkeypatch):
        self._seed_repo(tmp_path)
        monkeypatch.setattr(g, "REPO_ROOT", tmp_path)
        out = tmp_path / "config" / "governance_operations_map.yaml"
        monkeypatch.setattr(g, "OUTPUT_PATH", out)
        doc1 = g.build_document(dry_run=False)
        doc1["pipeline"]["layers"][4]["mounts"] = ["zephyr.trading.process_reaper"]
        doc1["out_of_scope_refs"] = [{"name_zh": "自定义引用", "ref": "x.md"}]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml.safe_dump(doc1, allow_unicode=True), encoding="utf-8")
        doc2 = g.build_document(dry_run=False)
        assert doc2["pipeline"]["layers"][4]["mounts"] == ["zephyr.trading.process_reaper"]
        assert doc2["out_of_scope_refs"][0]["name_zh"] == "自定义引用"
        assert doc2["counts"]["total_modules"] == 1  # 机器层仍全量重建


class TestWiringClassifierMechanism:
    """接线判定回归:钉住"机制"而非计数——静态 import / __all__ / 散文 / importlib 动态 四路。"""

    @staticmethod
    def _write(root: Path, rel: str, text: str) -> None:
        f = root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")

    def _seed(self, root: Path) -> None:
        # (a) 真实静态 import：别处 `from zephyr.gmfix import wired_probe`
        self._write(root, "src/zephyr/gmfix/wired_probe.py", "# [MODULE] zephyr.gmfix.wired_probe\nx = 1\n")
        self._write(root, "src/zephyr/gmfix/consumer_static.py", "from zephyr.gmfix import wired_probe\n")
        # (b) 仅在包 __all__ 出现(裸名,无 import 语句)——不得算 wired
        self._write(root, "src/zephyr/gmfix/allpkg/__init__.py", '__all__ = ["allpkg_probe"]\n')
        self._write(root, "src/zephyr/gmfix/allpkg/allpkg_probe.py", "# [MODULE] zephyr.gmfix.allpkg.allpkg_probe\nx = 1\n")
        # (c) 仅在别处 docstring 散文里点名——不得算 wired
        self._write(root, "src/zephyr/gmfix/docconsumer.py", '"""mentions zephyr.gmfix.doc_probe usage in prose."""\n')
        self._write(root, "src/zephyr/gmfix/doc_probe.py", "# [MODULE] zephyr.gmfix.doc_probe\nx = 1\n")
        # (d) importlib 字符串解析:REGISTRY 存完整点分串 + import_module 分发——归 dynamic(非硬接线)
        self._write(
            root,
            "src/zephyr/gmfix/dynconsumer.py",
            "import importlib\n"
            'REGISTRY = {"k": "zephyr.gmfix.dyn_probe"}\n'
            "def load():\n"
            "    return importlib.import_module(REGISTRY['k'])\n",
        )
        self._write(root, "src/zephyr/gmfix/dyn_probe.py", "# [MODULE] zephyr.gmfix.dyn_probe\nx = 1\n")

    def test_ast_classifier_tiers(self, tmp_path, monkeypatch):
        self._seed(tmp_path)
        monkeypatch.setattr(g, "REPO_ROOT", tmp_path)
        mods = g.scan()
        by_path = {m["path"]: m["wiring"] for ms in mods.values() for m in ms}
        assert by_path["src/zephyr/gmfix/wired_probe.py"] == "wired"
        assert by_path["src/zephyr/gmfix/allpkg/allpkg_probe.py"] == "suspect_orphan"
        assert by_path["src/zephyr/gmfix/doc_probe.py"] == "suspect_orphan"
        assert by_path["src/zephyr/gmfix/dyn_probe.py"] == "wired_dynamic"
        # 核心病根回归锚:__all__ 再导出与散文点名绝不可伪装成 import 实锚
        assert by_path["src/zephyr/gmfix/allpkg/allpkg_probe.py"] != "wired"
        assert by_path["src/zephyr/gmfix/doc_probe.py"] != "wired"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
