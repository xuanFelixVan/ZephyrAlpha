# [A_test] module_id: SRC-TST-0691 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_cve_scanner
# [INVARIANTS] CVE scan must return matching CVEs for given dependency
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.cve_scanner import CVEScanner


class TestCVEScannerInstantiation:
    def test_default_empty_cves(self):
        scanner = CVEScanner()
        assert scanner.known_cves == []

    def test_custom_cves(self):
        scanner = CVEScanner(known_cves=["CVE-2024-0001:openssl", "CVE-2024-0002:libcurl"])
        assert len(scanner.known_cves) == 2


class TestScan:
    def test_scan_finds_matching_cves(self):
        scanner = CVEScanner(known_cves=["CVE-2024-0001:openssl", "CVE-2024-0002:openssl", "CVE-2024-0003:libcurl"])
        results = scanner.scan("openssl")
        assert len(results) == 2

    def test_scan_no_match(self):
        scanner = CVEScanner(known_cves=["CVE-2024-0001:openssl"])
        results = scanner.scan("nonexistent")
        assert results == []

    def test_scan_empty_known_cves(self):
        scanner = CVEScanner()
        results = scanner.scan("anything")
        assert results == []

    def test_scan_empty_dependency(self):
        scanner = CVEScanner(known_cves=["CVE-2024-0001:openssl"])
        results = scanner.scan("nonexistent")
        assert results == []

    def test_scan_partial_match(self):
        scanner = CVEScanner(known_cves=["CVE-2024-0001:openssl-lib"])
        results = scanner.scan("openssl")
        assert len(results) == 1
