# [BLUEPRINT] MOD-SEC-026 | docs/03_modules/_domain_security/supply_chain_security_scanner/blueprint.md
# [MODULE] zephyr.security.supply_chain_security_scanner
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] 无（纯内存；requirements reader/许可证表/CVE扫描回调/时钟全注入，复用 cve_scanner 语义不导入）
# [CONSUMERS] 运行时装配批（CI/发布闸装配 SBOM 生成+许可证扫描+CVE 关联三件套）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SBOM 组件按 name 确定性排序(锁文件仅接受 name==version 严格解析); GPL/AGPL 传染性规则表闭合(子串大小写不敏感有序匹配); CVE 关联仅经注入回调不触网; 重复组件/畸形行 Fail-Closed; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_security/supply_chain_security_scanner/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SupplyChainSecError(占位 ZA-SEC-UNREGISTERED-SUPPLY-CHAIN-SEC)——reader/cve_scanner 未注入/锁文件畸形行/重复组件/非法规则表时抛
# [TESTS] tests/security/test_supply_chain_security_scanner.py
# [A_module] module_id=MOD-SEC-026 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""SupplyChainSecurityScanner — 供应链安全扫描器（MOD-SEC-026）。

B12-03993（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SEC-007，B12 §15.1）：
供应链安全三件套——CycloneDX JSON **SBOM 生成器**（requirements 锁文件经
注入 reader 解析）+ **许可证扫描**（GPL/AGPL 传染性告警规则表）+ **SBOM
与 CVE 扫描结果关联**（注入 cve_scanner 回调，CVE→组件映射报告）。

查重分工（蓝图 §0）：feedback_loop/gates/cve_scanner=CVE 门禁扫描实现
（本件仅注入其回调做关联，不重建扫描）；锁文件读取副作用全 DI，纯内存。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_LICENSE_RULES",
    "CveAssociation",
    "LicenseFinding",
    "LicenseVerdict",
    "Sbom",
    "SbomComponent",
    "SupplyChainSecError",
    "SupplyChainSecurityScanner",
]


class SupplyChainSecError(Exception):
    """供应链安全扫描输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SEC-UNREGISTERED-SUPPLY-CHAIN-SEC。
    """


class LicenseVerdict:
    """许可证判定词表（闭合字符串常量）。"""

    CONTAMINATED: Final = "contaminated"  # 强传染性（GPL/AGPL/SSPL）告警
    REVIEW: Final = "review"              # 弱传染性（LGPL/MPL）复核
    CLEAN: Final = "clean"                # 未命中规则


#: 默认许可证传染性规则表（有序子串匹配，大小写不敏感；先特异后泛化）
DEFAULT_LICENSE_RULES: Final[tuple[tuple[str, str], ...]] = (
    ("agpl", LicenseVerdict.CONTAMINATED),
    ("sspl", LicenseVerdict.CONTAMINATED),
    ("lgpl", LicenseVerdict.REVIEW),
    ("gpl", LicenseVerdict.CONTAMINATED),
    ("mpl", LicenseVerdict.REVIEW),
)

_SBOM_FORMAT: Final = "CycloneDX"
_SBOM_SPEC_VERSION: Final = "1.5"


@dataclass(frozen=True)
class SbomComponent:
    """SBOM 组件（name==version 锁文件条目，frozen）。"""

    name: str
    version: str
    license: str
    bom_ref: str


@dataclass(frozen=True)
class Sbom:
    """CycloneDX SBOM（组件确定性排序，frozen）。"""

    components: tuple[SbomComponent, ...]
    generated_at: datetime.datetime


@dataclass(frozen=True)
class LicenseFinding:
    """许可证扫描结论（frozen）。"""

    component: str
    license: str
    verdict: str
    matched_rule: str


@dataclass(frozen=True)
class CveAssociation:
    """CVE→组件映射（CVE 号确定性排序，frozen）。"""

    component: str
    version: str
    cve_ids: tuple[str, ...]


class SupplyChainSecurityScanner:
    """供应链安全扫描器（SBOM 生成 + 许可证扫描 + CVE 关联）。"""

    def __init__(
        self,
        *,
        requirements_reader: Callable[[], str] | None = None,
        license_table: Mapping[str, str] | None = None,
        license_rules: Sequence[tuple[str, str]] | None = None,
        cve_scanner: Callable[[str, str], Sequence[str]] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._reader = requirements_reader
        table = dict(license_table) if license_table is not None else {}
        for name, lic in table.items():
            if not name or not lic:
                raise SupplyChainSecError("许可证表含空 name/license")
        self._license_table = {k.lower(): v for k, v in table.items()}
        rules = tuple(license_rules) if license_rules is not None else DEFAULT_LICENSE_RULES
        valid_verdicts = {
            LicenseVerdict.CONTAMINATED, LicenseVerdict.REVIEW, LicenseVerdict.CLEAN
        }
        for pattern, verdict in rules:
            if not pattern:
                raise SupplyChainSecError("许可证规则 pattern 为空")
            if verdict not in valid_verdicts:
                raise SupplyChainSecError(f"非法许可证判定: {verdict!r}")
        self._license_rules = rules
        self._cve_scanner = cve_scanner
        self._clock = clock or datetime.datetime.now

    # ── SBOM 生成 ────────────────────────────────────────────────────────

    def generate_sbom(self) -> Sbom:
        """从注入 reader 解析 requirements 锁文件 → CycloneDX SBOM。"""
        if self._reader is None:
            raise SupplyChainSecError("requirements_reader 未注入（Fail-Closed）")
        text = self._reader()
        if not isinstance(text, str):
            raise SupplyChainSecError("requirements_reader 返回值非字符串")
        components: dict[str, SbomComponent] = {}
        for lineno, raw in enumerate(text.splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.count("==") != 1:
                raise SupplyChainSecError(
                    f"锁文件第 {lineno} 行畸形（须严格 name==version）: {line!r}"
                )
            name, version = (part.strip() for part in line.split("=="))
            if not name or not version:
                raise SupplyChainSecError(f"锁文件第 {lineno} 行 name/version 为空")
            key = name.lower()
            if key in components:
                raise SupplyChainSecError(f"重复组件: {name!r}")
            components[key] = SbomComponent(
                name=name,
                version=version,
                license=self._license_table.get(key, "UNKNOWN"),
                bom_ref=f"pkg:pypi/{key}@{version}",
            )
        ordered = tuple(components[k] for k in sorted(components))
        sbom = Sbom(components=ordered, generated_at=self._clock())
        _log.info("SBOM 生成: %d 组件", len(ordered))
        return sbom

    def to_cyclonedx_dict(self, sbom: Sbom) -> dict:
        """SBOM → CycloneDX JSON 兼容 dict（纯内存，不写盘）。"""
        if not isinstance(sbom, Sbom):
            raise SupplyChainSecError(f"非法 SBOM 类型: {type(sbom)!r}")
        return {
            "bomFormat": _SBOM_FORMAT,
            "specVersion": _SBOM_SPEC_VERSION,
            "version": 1,
            "metadata": {"timestamp": sbom.generated_at.isoformat()},
            "components": [
                {
                    "type": "library",
                    "bom-ref": c.bom_ref,
                    "name": c.name,
                    "version": c.version,
                    "licenses": [{"license": {"name": c.license}}],
                }
                for c in sbom.components
            ],
        }

    # ── 许可证扫描 ────────────────────────────────────────────────────────

    def scan_licenses(self, sbom: Sbom) -> tuple[LicenseFinding, ...]:
        """GPL/AGPL 传染性规则表扫描（有序子串匹配，确定性）。"""
        if not isinstance(sbom, Sbom):
            raise SupplyChainSecError(f"非法 SBOM 类型: {type(sbom)!r}")
        findings: list[LicenseFinding] = []
        for comp in sbom.components:
            lic_lower = comp.license.lower()
            verdict = LicenseVerdict.CLEAN
            matched = ""
            for pattern, rule_verdict in self._license_rules:
                if pattern.lower() in lic_lower:
                    verdict = rule_verdict
                    matched = pattern
                    break
            if verdict == LicenseVerdict.CONTAMINATED:
                _log.warning("许可证传染性告警: %s (%s)", comp.name, comp.license)
            findings.append(LicenseFinding(
                component=comp.name,
                license=comp.license,
                verdict=verdict,
                matched_rule=matched,
            ))
        return tuple(findings)

    # ── CVE 关联 ─────────────────────────────────────────────────────────

    def correlate_cves(self, sbom: Sbom) -> tuple[CveAssociation, ...]:
        """SBOM 组件 ↔ CVE 扫描结果关联（注入回调，CVE→组件映射报告）。"""
        if not isinstance(sbom, Sbom):
            raise SupplyChainSecError(f"非法 SBOM 类型: {type(sbom)!r}")
        if self._cve_scanner is None:
            raise SupplyChainSecError("cve_scanner 未注入（Fail-Closed 不触网）")
        out: list[CveAssociation] = []
        for comp in sbom.components:
            cves = self._cve_scanner(comp.name, comp.version)
            if cves is None:
                raise SupplyChainSecError(f"cve_scanner 返回 None: {comp.name!r}")
            cve_ids = tuple(sorted({str(c) for c in cves}))
            if cve_ids:
                _log.warning("CVE 关联: %s@%s -> %s", comp.name, comp.version, cve_ids)
            out.append(CveAssociation(
                component=comp.name, version=comp.version, cve_ids=cve_ids,
            ))
        return tuple(out)
