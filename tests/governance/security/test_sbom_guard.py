# [A_test] module_id: MOD-GOV_sbom_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_sbom_guard
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] SBOM必须完整;幽灵依赖必须检测
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_sbom_guard.py
# [TTL] task_bound

from zephyr.governance.security_governance.sbom_guard import SBOMGuard


class TestSBOMGuardInit:
    def test_instantiation(self):
        sg = SBOMGuard()
        assert sg.sbom == {}


class TestRegisterDependency:
    def test_register_single(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0")
        assert "numpy" in sg.sbom
        assert sg.sbom["numpy"]["version"] == "1.24.0"

    def test_register_with_hash(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0", hash_checksum="abc123")
        assert sg.sbom["numpy"]["hash"] == "abc123"

    def test_register_default_empty_hash(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0")
        assert sg.sbom["numpy"]["hash"] == ""

    def test_register_multiple(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0")
        sg.register_dependency("pandas", "2.0.1")
        assert len(sg.sbom) == 2

    def test_register_overwrites(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0")
        sg.register_dependency("numpy", "1.25.0")
        assert sg.sbom["numpy"]["version"] == "1.25.0"


class TestVerifySBOM:
    def test_all_match(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0")
        sg.register_dependency("pandas", "2.0.1")
        result = sg.verify_sbom({"numpy": "1.24.0", "pandas": "2.0.1"})
        assert result == []

    def test_missing_dependency(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0")
        sg.register_dependency("pandas", "2.0.1")
        result = sg.verify_sbom({"numpy": "1.24.0"})
        assert len(result) == 1
        assert "MISSING: pandas" in result[0]

    def test_version_mismatch(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0")
        result = sg.verify_sbom({"numpy": "1.25.0"})
        assert len(result) == 1
        assert "VERSION_MISMATCH: numpy" in result[0]
        assert "expected=1.24.0" in result[0]
        assert "actual=1.25.0" in result[0]

    def test_missing_and_mismatch(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0")
        sg.register_dependency("pandas", "2.0.1")
        result = sg.verify_sbom({"numpy": "1.25.0"})
        assert len(result) == 2

    def test_extra_deps_not_flagged(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0")
        result = sg.verify_sbom({"numpy": "1.24.0", "scipy": "1.10.0"})
        assert result == []

    def test_empty_sbom(self):
        sg = SBOMGuard()
        result = sg.verify_sbom({"numpy": "1.24.0"})
        assert result == []

    def test_empty_current_deps(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0")
        result = sg.verify_sbom({})
        assert len(result) == 1
        assert "MISSING: numpy" in result[0]


class TestScanCVE:
    def test_scan_returns_empty_list(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "1.24.0")
        result = sg.scan_cve()
        assert result == []

    def test_scan_empty_sbom(self):
        sg = SBOMGuard()
        result = sg.scan_cve()
        assert result == []


class TestBoundary:
    def test_empty_name(self):
        sg = SBOMGuard()
        sg.register_dependency("", "1.0.0")
        assert "" in sg.sbom

    def test_empty_version(self):
        sg = SBOMGuard()
        sg.register_dependency("numpy", "")
        result = sg.verify_sbom({"numpy": "1.0.0"})
        assert len(result) == 1

    def test_unicode_name(self):
        sg = SBOMGuard()
        sg.register_dependency("依赖包", "1.0.0")
        result = sg.verify_sbom({"依赖包": "1.0.0"})
        assert result == []

    def test_very_long_version(self):
        sg = SBOMGuard()
        ver = "1.0.0" + ".0" * 1000
        sg.register_dependency("pkg", ver)
        result = sg.verify_sbom({"pkg": ver})
        assert result == []
