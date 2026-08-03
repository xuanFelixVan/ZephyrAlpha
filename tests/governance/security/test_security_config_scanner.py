# [A_test] module_id: MOD-GOV_security_config_scanner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_security_config_scanner
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] 安全配置扫描不可跳过;数据库/云/API配置必须检查
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_security_config_scanner.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

import pytest

from zephyr.governance.security_governance.security_config_scanner import REQUIRED_CONFIGS, SecurityConfigScanner


class TestRequiredConfigs:
    def test_required_configs_defined(self):
        assert "limits.yaml" in REQUIRED_CONFIGS
        assert "cors.yaml" in REQUIRED_CONFIGS
        assert "secrets.yaml" in REQUIRED_CONFIGS

    def test_required_configs_have_descriptions(self):
        for key, desc in REQUIRED_CONFIGS.items():
            assert isinstance(desc, str)
            assert len(desc) > 0


class TestSecurityConfigScannerInit:
    def test_instantiation(self):
        scs = SecurityConfigScanner()
        assert scs is not None


class TestScan:
    def test_all_files_present(self):
        scs = SecurityConfigScanner()
        result = scs.scan(["limits.yaml", "cors.yaml", "secrets.yaml"])
        assert result["missing_count"] == 0
        assert result["missing"] == {}
        assert result["complete"] is True

    def test_all_files_missing(self):
        scs = SecurityConfigScanner()
        result = scs.scan([])
        assert result["missing_count"] == 3
        assert result["complete"] is False
        assert "limits.yaml" in result["missing"]
        assert "cors.yaml" in result["missing"]
        assert "secrets.yaml" in result["missing"]

    def test_one_file_missing(self):
        scs = SecurityConfigScanner()
        result = scs.scan(["limits.yaml", "cors.yaml"])
        assert result["missing_count"] == 1
        assert "secrets.yaml" in result["missing"]
        assert result["complete"] is False

    def test_partial_path_match(self):
        scs = SecurityConfigScanner()
        result = scs.scan(["config/limits.yaml", "config/cors.yaml", "config/secrets.yaml"])
        assert result["missing_count"] == 0
        assert result["complete"] is True

    def test_extra_files_ignored(self):
        scs = SecurityConfigScanner()
        result = scs.scan(["limits.yaml", "cors.yaml", "secrets.yaml", "extra.yaml"])
        assert result["missing_count"] == 0
        assert result["complete"] is True

    def test_missing_descriptions_correct(self):
        scs = SecurityConfigScanner()
        result = scs.scan(["limits.yaml"])
        assert result["missing"]["cors.yaml"] == REQUIRED_CONFIGS["cors.yaml"]
        assert result["missing"]["secrets.yaml"] == REQUIRED_CONFIGS["secrets.yaml"]


class TestScanBoundary:
    def test_empty_input(self):
        scs = SecurityConfigScanner()
        result = scs.scan([])
        assert result["missing_count"] == 3
        assert result["complete"] is False

    def test_none_in_list_raises_typeerror(self):
        scs = SecurityConfigScanner()
        with pytest.raises(TypeError):
            scs.scan([None, "limits.yaml"])

    def test_case_sensitivity(self):
        scs = SecurityConfigScanner()
        result = scs.scan(["Limits.yaml", "CORS.yaml", "secrets.yaml"])
        assert result["missing_count"] >= 1

    def test_substring_not_matching(self):
        scs = SecurityConfigScanner()
        result = scs.scan(["limits.yaml.bak", "cors.yaml.old", "secrets.yaml.tmp"])
        assert result["missing_count"] == 0
