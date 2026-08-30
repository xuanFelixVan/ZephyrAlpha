# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.report
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.gov_code_quality.code_dedup.cli; tests/governance/observability/test_report.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
报告生成器 — YAML/JSON 输出 + 退出码判定 + Health Score 聚合.

职责：
  - 生成 dedup_report.yaml（含 engine_self_metrics / duplication_intake_rate / debt_projection）
  - 退出码五档映射：0=CLEAN / 1=WARN / 2=ERROR / 3=FAULT / 4=DEGRADED
  - 聚合各 Stage 结果输出标准格式
  - 降级标注（degradation_level）输出到报告头部

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: report.py
# 层: 算法
# - id: A1
#   name_zh: ① ReportGenerator
#   name_en: ReportGenerator
#   intro: YAML/JSON 报告生成器.
#   desc: YAML/JSON 报告生成器.；公共方法（定义序）: degradation_level, exit_code, generate, to_yaml_dict, to_json, set_degradation, s…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: ReportGenerator
#   downstream: zephyr.gov_code_quality.code_dedup.cli; tests/governance/observability/test_rep…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


class ExitCode:
    CLEAN = 0
    WARN = 1
    ERROR = 2
    FAULT = 3
    DEGRADED = 4


@dataclass
class EngineSelfMetrics:
    fpr_7d: float = 0.0
    detection_latency_p50_ms: float = 0.0
    detection_latency_p95_ms: float = 0.0
    fix_success_rate: float = 100.0
    cache_hit_ratio: float = 0.0
    scan_duration_p50_ms: float = 0.0
    scan_duration_p95_ms: float = 0.0
    total_scan_duration_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0


@dataclass
class DuplicationIntakeRate:
    new_duplicates_this_week: int = 0
    new_duplicates_this_month: int = 0
    velocity_groups_per_week: float = 0.0
    trend: str = "flat"


@dataclass
class DebtProjection:
    weeks_to_payoff: float = 0.0
    current_debt_groups: int = 0
    intake_rate: float = 0.0
    fix_rate: float = 0.0
    projected_zero_date: str = ""


@dataclass
class ScanMetadata:
    generated_at: str = ""
    scan_mode: str = "incremental"
    trigger: str = "manual"
    scope: str = "src/zephyr/"
    total_functions: int = 0
    scanned_functions: int = 0
    cached_functions: int = 0
    scan_duration_ms: int = 0
    exit_code: int = 0
    degradation_level: str = "none"


@dataclass
class HealthComponents:
    overall: int = 0
    trend: str = "flat"
    duplication_rate: float = 0.0
    shared_coverage: float = 0.0
    signature_collisions: int = 0
    import_health: int = 0
    stale_shared_count: int = 0
    auto_fix_success_rate: float = 100.0
    micro_clone_density: float = 0.0
    blast_radius_score: int = 0
    shared_burden_score: int = 0
    simplicity_audit_score: int = 0
    contract_consistency: int = 0
    cross_boundary_health: int = 0


@dataclass
class HotspotCategory:
    category: str = ""
    duplicate_count: int = 0
    trend: str = "flat"


class ReportGenerator:
    """YAML/JSON 报告生成器."""

    def __init__(self) -> None:
        self._exit_code: int = ExitCode.CLEAN
        self._degradation_level: str = "none"

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def degradation_level(self) -> str:
        """只读：degradation_level（Stage 4 公共化）。"""
        return self._degradation_level

    @degradation_level.setter
    def degradation_level(self, value):
        """写入：degradation_level（Stage 4 公共化）。"""
        self._degradation_level = value

    @property
    def exit_code(self) -> int:
        """只读：exit_code（Stage 4 公共化）。"""
        return self._exit_code

    @exit_code.setter
    def exit_code(self, value):
        """写入：exit_code（Stage 4 公共化）。"""
        self._exit_code = value

    # ── 公共 API ──────────────────────────────────────────────

    def generate(
        self,
        total_functions: int = 0,
        scanned: int = 0,
        cached: int = 0,
        duration_ms: int = 0,
        duplicate_groups: list[dict] | None = None,
        engine_metrics: EngineSelfMetrics | None = None,
        intake: DuplicationIntakeRate | None = None,
        debt: DebtProjection | None = None,
        health: HealthComponents | None = None,
        hotspots: list[HotspotCategory] | None = None,
        scan_mode: str = "incremental",
        trigger: str = "manual",
        scope: str = "src/zephyr/",
    ) -> dict[str, Any]:
        """生成完整 dedup 报告数据结构."""
        now = datetime.now(UTC).isoformat()
        duplicate_groups = duplicate_groups or []
        engine_metrics = engine_metrics or EngineSelfMetrics()
        intake = intake or DuplicationIntakeRate()
        debt = debt or DebtProjection()
        health = health or HealthComponents()
        hotspots = hotspots or []

        report: dict[str, Any] = {
            "scan_metadata": self._build_scan_metadata(
                total_functions,
                scanned,
                cached,
                duration_ms,
                scan_mode,
                trigger,
                scope,
                now,
            ),
            "engine_self_metrics": self._build_engine_metrics(engine_metrics),
            "duplication_intake_rate": {
                "new_duplicates_this_week": intake.new_duplicates_this_week,
                "new_duplicates_this_month": intake.new_duplicates_this_month,
                "velocity_groups_per_week": intake.velocity_groups_per_week,
                "trend": intake.trend,
            },
            "debt_projection": {
                "weeks_to_payoff": debt.weeks_to_payoff,
                "current_debt_groups": debt.current_debt_groups,
                "intake_rate": debt.intake_rate,
                "fix_rate": debt.fix_rate,
                "projected_zero_date": debt.projected_zero_date,
            },
            "health_summary": {
                "overall": health.overall,
                "trend": health.trend,
                "components": {
                    "duplication_rate": health.duplication_rate,
                    "shared_coverage": health.shared_coverage,
                    "signature_collisions": health.signature_collisions,
                    "import_health": health.import_health,
                    "stale_shared_count": health.stale_shared_count,
                    "micro_clone_density": health.micro_clone_density,
                    "blast_radius_score": health.blast_radius_score,
                    "shared_burden_score": health.shared_burden_score,
                    "simplicity_audit_score": health.simplicity_audit_score,
                    "contract_consistency": health.contract_consistency,
                    "cross_boundary_health": health.cross_boundary_health,
                },
            },
            "hotspot_categories": [
                {"category": h.category, "duplicate_count": h.duplicate_count, "trend": h.trend} for h in hotspots[:5]
            ],
            "summary": {
                "duplicate_groups_total": len(duplicate_groups),
                "high_confidence": sum(1 for g in duplicate_groups if g.get("confidence", 0) >= 90),
                "medium_confidence": sum(1 for g in duplicate_groups if 70 <= g.get("confidence", 0) < 90),
                "low_confidence": sum(1 for g in duplicate_groups if g.get("confidence", 0) < 70),
                "affected_files": len({m[0] for g in duplicate_groups for m in g.get("members", [])}),
                "auto_fixable": sum(1 for g in duplicate_groups if g.get("confidence", 0) >= 90),
            },
            "duplicate_groups": duplicate_groups,
        }

        return report

    def to_yaml_dict(self, report: dict[str, Any]) -> dict[str, Any]:
        return report

    def to_json(self, report: dict[str, Any]) -> str:
        return json.dumps(report, ensure_ascii=False, indent=2)

    def set_degradation(self, level: str) -> None:
        self._degradation_level = level
        self._exit_code = ExitCode.DEGRADED

    def set_exit_code(self, code: int) -> None:
        self._exit_code = code

    # ── 内部 ──────────────────────────────────────────────────

    def _build_scan_metadata(
        self,
        total: int,
        scanned: int,
        cached: int,
        duration_ms: int,
        scan_mode: str,
        trigger: str,
        scope: str,
        now: str,
    ) -> dict[str, Any]:
        return {
            "generated_at": now,
            "scan_mode": scan_mode,
            "trigger": trigger,
            "scope": scope,
            "total_functions": total,
            "scanned_functions": scanned,
            "cached_functions": cached,
            "scan_duration_ms": duration_ms,
            "exit_code": self._exit_code,
            "degradation_level": self._degradation_level,
        }

    @staticmethod
    def _build_engine_metrics(em: EngineSelfMetrics) -> dict[str, Any]:
        return {
            "false_positive_rate_7d": em.fpr_7d,
            "detection_latency": {
                "p50_ms": em.detection_latency_p50_ms,
                "p95_ms": em.detection_latency_p95_ms,
            },
            "fix_success_rate": em.fix_success_rate,
            "cache_hit_ratio": em.cache_hit_ratio,
            "scan_duration": {
                "p50_ms": em.scan_duration_p50_ms,
                "p95_ms": em.scan_duration_p95_ms,
                "total_ms": em.total_scan_duration_ms,
            },
            "cache_operation": {
                "hits": em.cache_hits,
                "misses": em.cache_misses,
            },
        }
