# [BLUEPRINT] MOD-SEC-026 | docs/03_modules/_domain_security/supply_chain_security_scanner/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SEC-026 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.security.test_supply_chain_security_scanner
# [TESTS] src/zephyr/security/supply_chain_security_scanner.py
"""MOD-SEC-026 单元测试：supply_chain_security_scanner 供应链安全扫描器。

蓝图验收（B12-03993/CAND-SEC-007，B12 §15.1）：CycloneDX SBOM 生成（注入
requirements reader）+ GPL/AGPL 许可证传染性告警规则表 + CVE→组件映射关
联（注入 cve_scanner 回调）。reader/扫描器/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.security.supply_chain_security_scanner",
    reason="supply_chain_security_scanner not importable",
)

from zephyr.security.supply_chain_security_scanner import (  # noqa: E402
    LicenseVerdict,
    SupplyChainSecError,
    SupplyChainSecurityScanner,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_LOCK = """\
# 锁文件
numpy==2.3.5
pandas==2.2.3
copyleft-lib==1.0
"""

_LICENSES = {
    "numpy": "BSD-3-Clause",
    "pandas": "BSD-3-Clause",
    "copyleft-lib": "GPL-3.0-only",
}

_CVES = {
    ("pandas", "2.2.3"): ["CVE-2026-0002", "CVE-2026-0001"],
    ("copyleft-lib", "1.0"): ["CVE-2026-0003"],
}


def _scanner(**overrides) -> SupplyChainSecurityScanner:
    kwargs = {
        "requirements_reader": lambda: _LOCK,
        "license_table": _LICENSES,
        "cve_scanner": lambda name, version: _CVES.get((name, version), []),
        "clock": lambda: _T0,
    }
    kwargs.update(overrides)
    return SupplyChainSecurityScanner(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# SBOM 生成
# ──────────────────────────────────────────────────────────────────────────────


class TestSbomGeneration:
    def test_components_sorted_and_licensed(self) -> None:
        sbom = _scanner().generate_sbom()
        assert [c.name for c in sbom.components] == ["copyleft-lib", "numpy", "pandas"]
        assert sbom.components[0].license == "GPL-3.0-only"
        assert sbom.generated_at == _T0

    def test_bom_ref_purl(self) -> None:
        sbom = _scanner().generate_sbom()
        assert sbom.components[1].bom_ref == "pkg:pypi/numpy@2.3.5"

    def test_unknown_license_default(self) -> None:
        sbom = _scanner(license_table={}).generate_sbom()
        assert all(c.license == "UNKNOWN" for c in sbom.components)

    def test_reader_not_injected_fail_closed(self) -> None:
        scanner = SupplyChainSecurityScanner(clock=lambda: _T0)
        with pytest.raises(SupplyChainSecError):
            scanner.generate_sbom()

    def test_malformed_line_raises(self) -> None:
        scanner = _scanner(requirements_reader=lambda: "numpy>=2.0\n")
        with pytest.raises(SupplyChainSecError):
            scanner.generate_sbom()

    def test_empty_name_raises(self) -> None:
        scanner = _scanner(requirements_reader=lambda: "==1.0\n")
        with pytest.raises(SupplyChainSecError):
            scanner.generate_sbom()

    def test_duplicate_component_raises(self) -> None:
        scanner = _scanner(requirements_reader=lambda: "numpy==2.3.5\nNumPy==2.3.5\n")
        with pytest.raises(SupplyChainSecError):
            scanner.generate_sbom()

    def test_comments_and_blanks_skipped(self) -> None:
        scanner = _scanner(requirements_reader=lambda: "# c\n\nnumpy==2.3.5\n")
        sbom = scanner.generate_sbom()
        assert len(sbom.components) == 1

    def test_cyclonedx_dict_shape(self) -> None:
        scanner = _scanner()
        doc = scanner.to_cyclonedx_dict(scanner.generate_sbom())
        assert doc["bomFormat"] == "CycloneDX"
        assert doc["specVersion"] == "1.5"
        assert doc["metadata"]["timestamp"] == _T0.isoformat()
        assert doc["components"][0]["name"] == "copyleft-lib"
        assert doc["components"][0]["licenses"] == [
            {"license": {"name": "GPL-3.0-only"}}
        ]


# ──────────────────────────────────────────────────────────────────────────────
# 许可证传染性扫描
# ──────────────────────────────────────────────────────────────────────────────


class TestLicenseScan:
    def test_gpl_contaminated(self) -> None:
        findings = _scanner().scan_licenses(_scanner().generate_sbom())
        by_name = {f.component: f for f in findings}
        assert by_name["copyleft-lib"].verdict == LicenseVerdict.CONTAMINATED
        assert by_name["copyleft-lib"].matched_rule == "gpl"
        assert by_name["numpy"].verdict == LicenseVerdict.CLEAN
        assert by_name["numpy"].matched_rule == ""

    def test_agpl_before_lgpl_gpl_order(self) -> None:
        scanner = _scanner(
            requirements_reader=lambda: "x==1.0\ny==1.0\n",
            license_table={"x": "LGPL-2.1", "y": "AGPL-3.0"},
        )
        findings = {f.component: f for f in scanner.scan_licenses(scanner.generate_sbom())}
        assert findings["y"].verdict == LicenseVerdict.CONTAMINATED
        assert findings["y"].matched_rule == "agpl"
        assert findings["x"].verdict == LicenseVerdict.REVIEW

    def test_custom_rules_injected(self) -> None:
        scanner = _scanner(license_rules=(("bsd", LicenseVerdict.REVIEW),))
        findings = {f.component: f for f in scanner.scan_licenses(scanner.generate_sbom())}
        assert findings["numpy"].verdict == LicenseVerdict.REVIEW
        assert findings["copyleft-lib"].verdict == LicenseVerdict.CLEAN

    def test_illegal_rule_verdict_raises(self) -> None:
        with pytest.raises(SupplyChainSecError):
            _scanner(license_rules=(("gpl", "ban"),))

    def test_illegal_sbom_type_raises(self) -> None:
        with pytest.raises(SupplyChainSecError):
            _scanner().scan_licenses("not-sbom")


# ──────────────────────────────────────────────────────────────────────────────
# CVE 关联
# ──────────────────────────────────────────────────────────────────────────────


class TestCveCorrelation:
    def test_cve_mapping_sorted_deduped(self) -> None:
        scanner = _scanner()
        assocs = {a.component: a for a in scanner.correlate_cves(scanner.generate_sbom())}
        assert assocs["pandas"].cve_ids == ("CVE-2026-0001", "CVE-2026-0002")
        assert assocs["numpy"].cve_ids == ()
        assert assocs["copyleft-lib"].cve_ids == ("CVE-2026-0003",)

    def test_scanner_not_injected_fail_closed(self) -> None:
        scanner = _scanner(cve_scanner=None)
        with pytest.raises(SupplyChainSecError):
            scanner.correlate_cves(scanner.generate_sbom())

    def test_scanner_none_result_raises(self) -> None:
        scanner = _scanner(cve_scanner=lambda n, v: None)
        with pytest.raises(SupplyChainSecError):
            scanner.correlate_cves(scanner.generate_sbom())

    def test_scanner_receives_name_version(self) -> None:
        calls: list[tuple[str, str]] = []
        scanner = _scanner(cve_scanner=lambda n, v: calls.append((n, v)) or [])
        scanner.correlate_cves(scanner.generate_sbom())
        assert calls == [("copyleft-lib", "1.0"), ("numpy", "2.3.5"), ("pandas", "2.2.3")]


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        scanner = _scanner()
        s1, s2 = scanner.generate_sbom(), scanner.generate_sbom()
        assert s1 == s2
        assert scanner.to_cyclonedx_dict(s1) == scanner.to_cyclonedx_dict(s2)
        assert scanner.scan_licenses(s1) == scanner.scan_licenses(s2)
        assert scanner.correlate_cves(s1) == scanner.correlate_cves(s2)
