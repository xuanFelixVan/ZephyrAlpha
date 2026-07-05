# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.fifteen_dimension_auditor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/audit/test_fifteen_dimension_auditor.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_fifteen_dimension_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""15维超综合审计首页 — 逐项证明"做过且做对".

职责：
  - 15维审计刹车：每一项给出 PASS/FAIL/WAIVED + 证据
  - Cluster 聚合报告
  - 审计证书格式输出
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class DimensionAudit:
    dimension: str
    result: str = "PASS"
    evidence: str = ""
    cluster: str = ""


@dataclass
class AuditCertificate:
    overall: str = "PASS"
    pass_count: int = 0
    fail_count: int = 0
    waived_count: int = 0
    dimensions: list[DimensionAudit] = field(default_factory=list)
    cluster_summary: dict[str, dict] = field(default_factory=dict)
    generated_at: str = ""


class FifteenDimensionAuditor:
    """15维超综合审计首页."""

    _DIMENSIONS: list[tuple[str, str]] = [
        ("dependency_health", "依赖健康度"),
        ("api_contract_consistency", "API契约一致性"),
        ("test_coverage_adequacy", "测试覆盖充分性"),
        ("degradation_resilience", "降级恢复韧性"),
        ("false_positive_rate", "误报率"),
        ("performance_latency", "性能延迟"),
        ("config_completeness", "配置完整性"),
        ("documentation_accuracy", "文档准确性"),
        ("cross_module_integration", "跨模块集成"),
        ("monoculture_immunity", "Monoculture免疫"),
        ("decision_audit_trail", "决策审计链"),
        ("grandfather_compliance", "Grandfather合规"),
        ("lifecycle_management", "生命周期管理"),
        ("self_protection", "自保护"),
        ("simplicity_cost_benefit", "简单性成本收益"),
    ]

    def audit(
        self,
        evidence: dict[str, str],
        waivers: set[str] | None = None,
    ) -> AuditCertificate:
        """执行15维审计."""
        waivers = waivers or set()
        dimensions: list[DimensionAudit] = []
        pass_count = fail_count = waived_count = 0

        for dim, label in self._DIMENSIONS:
            if dim in waivers:
                result = "WAIVED"
                waived_count += 1
            elif dim in evidence:
                result = "PASS"
                pass_count += 1
            else:
                result = "FAIL"
                fail_count += 1

            dimensions.append(
                DimensionAudit(
                    dimension=dim,
                    result=result,
                    evidence=evidence.get(dim, ""),
                    cluster=self._cluster_for(dim),
                )
            )

        return AuditCertificate(
            overall="PASS" if fail_count == 0 else "FAIL",
            pass_count=pass_count,
            fail_count=fail_count,
            waived_count=waived_count,
            dimensions=dimensions,
            cluster_summary=self._cluster_summary(dimensions),
            generated_at=datetime.now(UTC).isoformat(),
        )

    def generate_certificate(self, cert: AuditCertificate) -> str:
        """生成审计证书格式文本."""
        lines = [
            "=" * 60,
            "  ZephyrAlpha MOD-INF-017 15-Dimension Audit Certificate",
            f"  Date: {cert.generated_at}",
            f"  Overall: {cert.overall} | PASS={cert.pass_count} FAIL={cert.fail_count} WAIVED={cert.waived_count}",
            "=" * 60,
            "",
        ]
        for d in cert.dimensions:
            icon = "✅" if d.result == "PASS" else "❌" if d.result == "FAIL" else "⚪"
            lines.append(f"  {icon} {d.dimension:<30} [{d.result:>6}] {d.evidence}")
        lines.append("")
        lines.append("  Clusters:")
        for cluster, summary in cert.cluster_summary.items():
            lines.append(f"    {cluster}: {summary['pass']}P/{summary['fail']}F/{summary['waived']}W")
        lines.append("=" * 60)
        return "\n".join(lines)

    @staticmethod
    def _cluster_for(dim: str) -> str:
        if dim in ("dependency_health", "cross_module_integration", "monoculture_immunity"):
            return "Architecture"
        if dim in ("api_contract_consistency", "config_completeness"):
            return "Contracts"
        if dim in ("test_coverage_adequacy", "false_positive_rate"):
            return "Quality"
        if dim in ("degradation_resilience", "self_protection"):
            return "Resilience"
        if dim in ("decision_audit_trail", "grandfather_compliance", "lifecycle_management"):
            return "Governance"
        if dim in ("performance_latency", "simplicity_cost_benefit"):
            return "Operations"
        return "Meta"

    def _cluster_summary(self, dims: list[DimensionAudit]) -> dict[str, dict]:
        clusters: dict[str, dict] = {}
        for d in dims:
            c = self._cluster_for(d.dimension)
            if c not in clusters:
                clusters[c] = {"pass": 0, "fail": 0, "waived": 0}
            key = "pass" if d.result == "PASS" else "fail" if d.result == "FAIL" else "waived"
            clusters[c][key] += 1
        return clusters
