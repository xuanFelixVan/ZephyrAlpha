# [A_test] module_id: SRC-TST-0948 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_cve_scanner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.cve_scanner
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_cve_scanner.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.cve_scanner import CVEScanner


class TestCVEScannerInstantiation:
    def test_default_construction(self):
        scanner = CVEScanner()
        assert scanner.known_cves == []

    def test_custom_known_cves(self):
        scanner = CVEScanner(known_cves=["CVE-2024-0001:openssl", "CVE-2024-0002:libcurl"])
        assert len(scanner.known_cves) == 2


class TestScan:
    def test_scan_finds_matching_cves(self):
        scanner = CVEScanner(known_cves=["CVE-2024-0001:openssl", "CVE-2024-0002:openssl"])
        results = scanner.scan("openssl")
        assert len(results) == 2

    def test_scan_no_match(self):
        scanner = CVEScanner(known_cves=["CVE-2024-0001:openssl"])
        results = scanner.scan("libcurl")
        assert results == []

    def test_scan_empty_known_cves(self):
        scanner = CVEScanner()
        results = scanner.scan("openssl")
        assert results == []


class TestBoundaries:
    def test_scan_empty_dependency_string(self):
        scanner = CVEScanner(known_cves=["CVE-2024-0001:openssl"])
        results = scanner.scan("")
        assert len(results) == 1

    def test_scan_partial_match(self):
        scanner = CVEScanner(known_cves=["CVE-2024-0001:openssl"])
        results = scanner.scan("open")
        assert len(results) == 1
