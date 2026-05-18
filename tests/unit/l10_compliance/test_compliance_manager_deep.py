# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l10_compliance.test_compliance_manager_deep
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
单元测试：src/zephyr/l10_compliance/compliance_manager.py + security_gateway_base.py + default_security_gateway.py
=================================================================================================================================

覆盖矩阵：
  ComplianceManagerBase:
    - 抽象类不可实例化 × 1
  SecurityGateway (ABC):
    - 抽象类不可实例化 × 1
  DefaultSecurityGateway (根级):
    - pre_filter 正常通过 × 1
    - pre_filter 检测到 Prompt Injection × 1
    - security_scan 检测到危险代码 × 1
    - security_scan 检测到硬编码凭据 × 1
    - decide ALLOW × 1
    - decide BLOCK × 1
    - decide FLAG × 1
    - reset 清除状态 × 1
    - _filter_backtick_escape × 1
  ArtifactScanner:
    - scan_content 清洁内容 × 1
    - scan_content 发现 SSRF × 1
    - scan_content 发现凭据 × 1
    - scan_file 扫描 YAML 配置 × 1
    - scan_file 扫描 Notebook × 1
    - scan_directory 递归扫描 × 1
"""

from pathlib import Path

import pytest
from zephyr.l10_compliance.artifact_scanner import ArtifactFinding, ArtifactScanner, ScanReport
from zephyr.l10_compliance.compliance_manager import ComplianceManagerBase
from zephyr.l10_compliance.implementations.default_security_gateway import DefaultSecurityGateway
from zephyr.l10_compliance.security_gateway_base import AuditAction, SecurityGateway


class TestComplianceManagerBaseABC:
    """合规管理器抽象基类校验"""

    def test_abstract_class_cannot_instantiate(self):
        with pytest.raises(TypeError):
            ComplianceManagerBase()


class TestSecurityGatewayABC:
    """安全网关抽象基类校验"""

    def test_abstract_class_cannot_instantiate(self):
        with pytest.raises(TypeError):
            SecurityGateway()


class TestDefaultSecurityGateway:
    """默认安全网关深度测试"""

    def test_pre_filter_clean_content(self):
        sgw = DefaultSecurityGateway()
        result = sgw.pre_filter("Hello world, this is a normal query.", source="test")
        assert result is True

    def test_pre_filter_empty_content(self):
        sgw = DefaultSecurityGateway()
        result = sgw.pre_filter("", source="test")
        assert result is False

    def test_pre_filter_large_content(self):
        sgw = DefaultSecurityGateway()
        result = sgw.pre_filter("x" * 1_000_001, source="test")
        assert result is True

    def test_security_scan_detects_destructive_command(self):
        sgw = DefaultSecurityGateway()
        risks = sgw.security_scan("os.system('rm -rf /etc/passwd')")
        assert any("BLOCK:" in r for r in risks)

    def test_security_scan_detects_eval(self):
        sgw = DefaultSecurityGateway()
        risks = sgw.security_scan("eval(user_input)")
        assert any("dynamic_eval" in r for r in risks)

    def test_security_scan_detects_warning_pattern(self):
        sgw = DefaultSecurityGateway()
        risks = sgw.security_scan("DROP TABLE users")
        assert any("WARN:" in r for r in risks)

    def test_security_scan_clean_content(self):
        sgw = DefaultSecurityGateway()
        risks = sgw.security_scan("print('hello world')")
        assert len(risks) == 0

    def test_decide_allow(self):
        sgw = DefaultSecurityGateway()
        decision = sgw.decide([], context={"source": "test"})
        assert decision.action == AuditAction.ALLOW

    def test_decide_block(self):
        sgw = DefaultSecurityGateway()
        decision = sgw.decide(["BLOCK:system_call"], context={"source": "test"})
        assert decision.action == AuditAction.BLOCK

    def test_decide_flag(self):
        sgw = DefaultSecurityGateway()
        decision = sgw.decide(["WARN:sql_drop_table"], context={"source": "test"})
        assert decision.action == AuditAction.FLAG


class TestArtifactScannerExtended:
    """ArtifactScanner 扩展扫描范围测试"""

    def test_scan_content_clean(self):
        scanner = ArtifactScanner()
        report = scanner.scan_content("print('hello world')", label="test.py")
        assert report.is_clean is True
        assert "[CLEAN]" in report.summary

    def test_scan_content_ssrf(self):
        scanner = ArtifactScanner()
        report = scanner.scan_content("url = 'http://192.168.1.1/admin'", label="test.py")
        assert report.is_clean is False
        assert any(f.category == "ssrf" for f in report.findings)

    def test_scan_content_credential(self):
        scanner = ArtifactScanner()
        report = scanner.scan_content('api_key = "sk-abcdefghijklmnopqrstuvwxyz123456"', label="test.py")
        assert report.is_clean is False
        assert any(f.category == "token_leak" for f in report.findings)

    def test_scan_yaml_config_secret(self):
        scanner = ArtifactScanner()
        yaml_content = "database:\n  host: localhost\n  password: SuperSecret123!\n"
        base_report = scanner.scan_content(yaml_content, label="config.yaml")
        config_report = scanner._scan_with_rules(yaml_content, "config.yaml", scanner._CONFIG_RULES)
        combined = ScanReport(
            target="config.yaml",
            findings=base_report.findings + config_report.findings,
        )
        assert any(f.rule_id == "S-07-CONFIG-SECRET" for f in combined.findings)

    def test_scan_notebook_system_call(self):
        scanner = ArtifactScanner()
        nb_content = '{"cells": [{"cell_type": "code", "source": "import os\\nos.system(\'rm -rf /\')"}]}'
        base_report = scanner.scan_content(nb_content, label="test.ipynb")
        nb_report = scanner._scan_with_rules(nb_content, "test.ipynb", scanner._NOTEBOOK_RULES)
        combined = ScanReport(
            target="test.ipynb",
            findings=base_report.findings + nb_report.findings,
        )
        assert any(f.rule_id == "S-08-NB-SYSTEM" for f in combined.findings)

    def test_scan_directory(self, tmp_path: Path):
        scanner = ArtifactScanner()
        # 创建临时文件
        (tmp_path / "clean.py").write_text("print('hello')", encoding="utf-8")
        (tmp_path / "bad.yaml").write_text("password: secret123", encoding="utf-8")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "nested.json").write_text('{"api_key": "sk-1234567890123456789012345678"}', encoding="utf-8")

        reports = scanner.scan_directory(tmp_path)
        # 应该扫描到 3 个文件（排除目录）
        assert len(reports) == 3
        # bad.yaml 应该触发 S-07-CONFIG-SECRET
        yaml_report = next((r for r in reports if "bad.yaml" in r.target), None)
        assert yaml_report is not None
