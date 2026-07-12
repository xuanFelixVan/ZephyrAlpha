# [A_test] module_id: SRC-TST-0011 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-206 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.adversarial.test_code_dedup_engine_red_team
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""code-dedup-engine 红队对抗测试 — MOD-INF-017.

覆盖率：导入链路验证 / Scanner 对抗样本 / Monoculture 免疫 / 自我扫描
对标：test_task_system_red_team.py 模式
"""

import os
import sys
import tempfile
import textwrap

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestStage00_ImportChain:
    def test_l01_import(self):
        assert code_dedup_engine.__version__ == "0.15.0"
        assert code_dedup_engine.__module_id__ == "MOD-INF-017"

    def test_root_proxy_import(self):
        from zephyr.governance import __module_id__ as m
        from zephyr.governance import __version__ as v

        assert v == "0.15.0"
        assert m == "MOD-INF-017"

    def test_scanner_via_proxy(self):
        from zephyr.infrastructure.asset_inventory import scanner

        assert hasattr(scanner, "Scanner")

    def test_scanner_direct(self):
        from zephyr.infrastructure.asset_inventory.scanner import Scanner

        s = Scanner()
        assert s is not None

    def test_monoculture_guard(self):
        from zephyr.gov_code_quality.code_dedup.monoculture_guard import MonocultureGuard

        g = MonocultureGuard()
        assert g is not None

    def test_self_scanner(self):
        from zephyr.gov_code_quality.code_dedup.self_scanner import SelfScanner

        ss = SelfScanner()
        assert ss is not None

    def test_decision_auditor(self):
        from zephyr.gov_code_quality.code_dedup.decision_auditor import DecisionAuditor

        da = DecisionAuditor()
        assert da is not None

    def test_cli_module(self):
        import inspect

        from zephyr.governance import cli

        sig = inspect.signature(cli.main)
        assert len(sig.parameters) == 0, f"main() should take no args, got: {sig}"

    def test_integration_hub(self):
        from zephyr.gov_code_quality.code_dedup.integration_hub import IntegrationHub

        hub = IntegrationHub()
        assert hub is not None

    def test_exit_codes(self):
        from zephyr.gov_code_quality.code_dedup.exit_codes import ExitCode

        assert ExitCode.PASS is not None


class TestStage01_ScannerAdversarial:
    def test_scan_file_detects_self(self):
        from zephyr.infrastructure.asset_inventory.scanner import Scanner

        scanner = Scanner()
        result = scanner.scan_file(__file__)
        assert result is not None

    def test_exact_clone_blocks(self):
        code = textwrap.dedent("""\
            def calc_alpha(x, y):
                z = x * 0.3 + y * 0.7
                if z > 0.5:
                    return z * 1.5
                return z * 0.8
        """)
        tmpdir = tempfile.mkdtemp(prefix="dedup_red_")
        a = os.path.join(tmpdir, "a.py")
        b = os.path.join(tmpdir, "b.py")
        with open(a, "w", encoding="utf-8") as f:
            f.write(code)
        with open(b, "w", encoding="utf-8") as f:
            f.write(code)

        from zephyr.infrastructure.asset_inventory.scanner import Scanner

        scanner = Scanner()
        scanner.scan_file(a)
        scanner.scan_file(b)
        dupes = scanner.find_duplicates()
        assert len(dupes) >= 1, f"Exact clone not detected: {len(dupes)} dupes"

    def test_dissimilar_no_false_positive(self):
        tmpdir = tempfile.mkdtemp(prefix="dedup_red_")
        a = os.path.join(tmpdir, "a.py")
        b = os.path.join(tmpdir, "b.py")
        with open(a, "w", encoding="utf-8") as f:
            f.write("def add(a, b): return a + b\n")
        with open(b, "w", encoding="utf-8") as f:
            f.write("class HttpServer:\n    def start(self): pass\n")

        from zephyr.infrastructure.asset_inventory.scanner import Scanner

        scanner = Scanner()
        scanner.scan_file(a)
        scanner.scan_file(b)
        dupes = scanner.find_duplicates()
        assert len(dupes) == 0, f"False positive: {len(dupes)} dupes"


class TestStage02_MonocultureAdversarial:
    def test_brs_computation(self):
        from zephyr.gov_code_quality.code_dedup.monoculture_guard import BlastRadiusScore, MonocultureGuard

        guard = MonocultureGuard()
        brs = guard.compute_brs(
            caller_count=12,
            cross_layer_count=3,
            on_critical_path=True,
            has_independent_unit_test=False,
        )
        assert isinstance(brs, BlastRadiusScore)
        assert 0 <= brs.blast_radius_score <= 100, f"BRS out of range: {brs.blast_radius_score}"

    def test_should_not_block_trivial(self):
        from zephyr.gov_code_quality.code_dedup.monoculture_guard import MonocultureGuard

        guard = MonocultureGuard()
        brs = guard.compute_brs(
            caller_count=0,
            cross_layer_count=0,
            on_critical_path=False,
            has_independent_unit_test=True,
        )
        should_block = guard.should_block_dedup(brs)
        assert not should_block, f"Should not block trivial function, but got block={should_block}"


class TestStage03_SelfScanIntegrity:
    def test_self_scan_no_crash(self):
        from zephyr.gov_code_quality.code_dedup.self_scanner import SelfScanner

        scanner = SelfScanner()
        report = scanner.scan_self()
        assert report is not None
        assert hasattr(report, "files_scanned")
        assert report.files_scanned >= 1, f"Self scan found no files: {report.files_scanned}"


class TestStage04_DecisionAuditChain:
    def test_log_decision_chain(self):
        from zephyr.gov_code_quality.code_dedup.decision_auditor import DecisionAuditor

        auditor = DecisionAuditor()
        auditor.log_decision(
            decision_id="RED-001",
            decision_type="eliminate_exact_clone",
            dup_group_id="group-001",
            outcome="approved",
            evidence={"source": "calc_a", "target": "calc_a_dup", "score": 0.95},
        )
        chain = auditor.get_chain(limit=10)
        assert isinstance(chain, list)
        assert any(d["decision_id"] == "RED-001" for d in chain), f"RED-001 not in chain: {chain}"


class TestStage05_TriageIntegration:
    def test_all_engine_modules_importable(self):
        modules = [
            "scanner",
            "monoculture_guard",
            "self_scanner",
            "decision_auditor",
            "exit_codes",
            "integration_hub",
            "cli",
            "config",
            "function_discovery",
            "auto_test_generator",
        ]
        for name in modules:
            mod = __import__(f"zephyr.testing.code_dedup.{name}", fromlist=[name])
            assert mod is not None, f"Failed to import: {name}"
