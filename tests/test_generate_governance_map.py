# [BLUEPRINT] MOD-ALT-001 | (auto-injected by S4 reconciler) | §
# [MODULE] tests.test_generate_governance_map
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] permanent
"""generate_governance_map 单测:族分类优先级/头解析/人工层保留/接线四态(AST import 边/__all__/散文/importlib 动态)/module_id 净化/purpose_tag 机贴/consumers/trigger_facts(schema 0.3 手术批)。

零真实仓库依赖:REPO_ROOT/OUTPUT_PATH/MAIN_REPO_ROOT monkeypatch 到 tmp_path;
HEAD 树枚举经 _patch_head_tree 打桩(F-AUDIT-GOMAP-INFLIGHT 治本后 tmp 仓无 git,
2026-10-04 修复:此前四测试静默红——seed 文件进不了真仓 HEAD 树)。
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


def _patch_head_tree(monkeypatch, *rels: str) -> None:
    """HEAD 树枚举打桩:tmp 仓无 git,seed 文件经此入选扫描集(测试必经入口)。"""
    monkeypatch.setattr(g, "_head_py_paths", lambda: list(rels))


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
        _patch_head_tree(
            monkeypatch,
            "src/zephyr/data/heartbeat_monitor.py",
            "src/zephyr/trading/health_monitor.py",
        )
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
        _patch_head_tree(monkeypatch, "src/zephyr/trading/process_reaper.py", "src/zephyr/other.py")
        monkeypatch.setattr(g, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(g, "MAIN_REPO_ROOT", tmp_path)
        monkeypatch.setattr(g, "OUTPUT_PATH", tmp_path / "config" / "governance_operations_map.yaml")
        doc = g.build_document(dry_run=False)
        assert doc["map_id"] == "GOMAP-001"
        assert doc["schema_version"] == "0.3"
        assert doc["counts"]["total_modules"] == 1
        assert doc["counts"]["untagged"] == 0
        assert [l["id"] for l in doc["pipeline"]["layers"]] == [f"GOM-L{i}" for i in range(7)]
        assert len(doc["legend"]) == 10  # SOP §2 图例默认种子
        entry = doc["families"]["L4_reap"][0]
        assert entry["wiring"] == "wired"
        assert entry["purpose_tag"] == ["reaper_duty"]
        assert entry["consumers_count"] == 1
        assert entry["consumers"] == ["src/zephyr/other.py"]
        assert entry["trigger_facts"]["total"] == 0  # tmp 无 .runtime 真源=缺席非零触发

    def test_human_layer_preserved_on_rebuild(self, tmp_path, monkeypatch):
        self._seed_repo(tmp_path)
        _patch_head_tree(monkeypatch, "src/zephyr/trading/process_reaper.py", "src/zephyr/other.py")
        monkeypatch.setattr(g, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(g, "MAIN_REPO_ROOT", tmp_path)
        out = tmp_path / "config" / "governance_operations_map.yaml"
        monkeypatch.setattr(g, "OUTPUT_PATH", out)
        doc1 = g.build_document(dry_run=False)
        doc1["pipeline"]["layers"][4]["mounts"] = ["zephyr.trading.process_reaper"]
        doc1["pipeline"]["layers"][4]["casebooks"] = ["AP#域四", "SV#底数"]
        doc1["out_of_scope_refs"] = [{"name_zh": "自定义引用", "ref": "x.md"}]
        doc1["legend"] = doc1["legend"][:3]
        doc1["legend_note_zh"] = "已冻结(测试)"
        doc1["tag_rules"] = [{"selector": "family=L4_reap", "tags": ["reaper_duty"]}]
        doc1["casebooks_legend_zh"] = "测试册注:AP=堵点本"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml.safe_dump(doc1, allow_unicode=True), encoding="utf-8")
        doc2 = g.build_document(dry_run=False)
        assert doc2["pipeline"]["layers"][4]["mounts"] == ["zephyr.trading.process_reaper"]
        assert doc2["pipeline"]["layers"][4]["casebooks"] == ["AP#域四", "SV#底数"]
        assert doc2["out_of_scope_refs"][0]["name_zh"] == "自定义引用"
        assert len(doc2["legend"]) == 3
        assert doc2["legend_note_zh"] == "已冻结(测试)"
        assert doc2["tag_rules"] == [{"selector": "family=L4_reap", "tags": ["reaper_duty"]}]
        assert doc2["casebooks_legend_zh"] == "测试册注:AP=堵点本"
        assert doc2["counts"]["total_modules"] == 1  # 机器层仍全量重建
        assert doc2["families"]["L4_reap"][0]["purpose_tag"] == ["reaper_duty"]  # 按新规则重贴


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
        self._write(
            root, "src/zephyr/gmfix/allpkg/allpkg_probe.py", "# [MODULE] zephyr.gmfix.allpkg.allpkg_probe\nx = 1\n"
        )
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
        _patch_head_tree(
            monkeypatch,
            "src/zephyr/gmfix/wired_probe.py",
            "src/zephyr/gmfix/consumer_static.py",
            "src/zephyr/gmfix/allpkg/__init__.py",
            "src/zephyr/gmfix/allpkg/allpkg_probe.py",
            "src/zephyr/gmfix/docconsumer.py",
            "src/zephyr/gmfix/doc_probe.py",
            "src/zephyr/gmfix/dynconsumer.py",
            "src/zephyr/gmfix/dyn_probe.py",
        )
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


class TestSanitizeModuleId:
    """schema 0.3 手术:头值垃圾捕获四形态回归锚(2026-10-03 F1 实证)。"""

    @pytest.mark.parametrize(
        ("header_val", "spec", "expected"),
        [
            ("zephyr.trading.process_reaper", "zephyr.trading._fb", "zephyr.trading.process_reaper"),
            (
                "module_id=MOD-GOV-wave1a-ch_probe",
                "scripts.governance.data_supply.ch_probe",
                "scripts.governance.data_supply.ch_probe",
            ),
            ("#", "scripts.governance.repair.concurrent_write_test", "scripts.governance.repair.concurrent_write_test"),
            (
                "t0_gpu_condition_pack（scripts",
                "scripts.audit.t0_gpu_condition_pack",
                "scripts.audit.t0_gpu_condition_pack",
            ),
            (None, "scripts.foo", "scripts.foo"),
            ("has space", "scripts.bar", "scripts.bar"),
        ],
    )
    def test_garbage_falls_back_to_spec(self, header_val, spec, expected):
        assert g._sanitize_module_id(header_val, spec) == expected


class TestPurposeTags:
    """schema 0.3 手术:SOP §2 机贴——多规则并集/untagged 计数/selector 解析。"""

    def _families(self):
        return {
            "L4_reap": [
                {
                    "module": "scripts.governance.check_wiring_orphan",
                    "path": "scripts/governance/check_wiring_orphan.py",
                    "family": "L4_reap",
                },
                {
                    "module": "zephyr.trading.process_reaper",
                    "path": "src/zephyr/trading/process_reaper.py",
                    "family": "L4_reap",
                },
            ],
            "L6_audit": [
                {
                    "module": "zephyr.trading.status_dashboard",
                    "path": "src/zephyr/trading/status_dashboard.py",
                    "family": "L6_audit",
                }
            ],
        }

    def test_rules_union_and_untagged_zero(self):
        families = self._families()
        rules = [
            {"selector": "family=L4_reap", "tags": ["reaper_duty"]},
            {"selector": "module=~wiring_orphan", "tags": ["orphan_claim"]},
            {"selector": "family=L6_audit", "tags": ["review_ledger"]},
        ]
        assert g._apply_purpose_tags(families, rules) == 0
        by_mod = {m["module"]: m["purpose_tag"] for ms in families.values() for m in ms}
        assert by_mod["scripts.governance.check_wiring_orphan"] == ["reaper_duty", "orphan_claim"]
        assert by_mod["zephyr.trading.process_reaper"] == ["reaper_duty"]

    def test_untagged_counted(self):
        families = {"L1_monitor": [{"module": "x.y", "path": "x/y.py", "family": "L1_monitor"}]}
        n = g._apply_purpose_tags(families, [{"selector": "family=L3_fuse", "tags": ["emergency_brake"]}])
        assert n == 1
        assert "purpose_tag" not in families["L1_monitor"][0]

    def test_bad_selector_raises(self):
        with pytest.raises(ValueError, match="selector"):
            g._parse_selector("layer=X")


class TestTriggerFacts:
    """schema 0.3 手术:运行痕迹计数——多形态去重计数/真源缺席不报错。"""

    def test_counts_and_absent_sources(self, tmp_path, monkeypatch):
        monkeypatch.setattr(g, "MAIN_REPO_ROOT", tmp_path)
        aud = tmp_path / ".runtime" / "audit"
        aud.mkdir(parents=True)
        (aud / "gate_execution_stats.jsonl").write_text(
            '{"detail": "scripts/governance/vms_health_check.py ran"}\n' * 3
            + '{"detail": "vms_health_check bare stem hit"}\n',
            encoding="utf-8",
        )
        corpora = g._load_fact_corpora()
        assert corpora["runtime_audit"]["files"] == 1
        assert corpora["drift_watchdog"]["files"] == 0  # 真源缺席=files 0,不报错不伪造
        families = {
            "L1_monitor": [
                {"module": "scripts.governance.vms_health_check", "path": "scripts/governance/vms_health_check.py"},
                {"module": "zephyr.trading.gpu_monitor", "path": "src/zephyr/trading/gpu_monitor.py"},
            ]
        }
        g._count_trigger_facts(families, corpora)
        m0, m1 = families["L1_monitor"]
        # 路径形态 3 次 + stem 单独 1 次(stem 落在路径 span 内不重复计——alternation 最长先匹配)
        assert m0["trigger_facts"] == {"total": 4, "by_source": {"runtime_audit": 4}}
        assert m1["trigger_facts"] == {"total": 0, "by_source": {}}


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
