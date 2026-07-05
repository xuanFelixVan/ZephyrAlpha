# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.health_monitor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/ops/test_health_monitor.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_health_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""健康仪表盘 — Dedup Health Score 0-100 + 趋势 + Session Log 写入.

职责：
  - 计算多维 Health Score（≥18 维度）
  - 趋势判定（↑ up / → flat / ↓ down）
  - Session Log 摘要写入（≤3行 MD：Health Score + Top3 热点 + 本次发现）
  - 引擎自观指标聚合
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class HealthDimension:
    name: str
    score: float
    weight: float = 1.0
    status: str = "ok"


@dataclass
class HealthReport:
    overall: int
    trend: str
    grade: str
    dimensions: list[HealthDimension] = field(default_factory=list)
    hotspots: list[dict[str, Any]] = field(default_factory=list)
    session_summary: str = ""
    generated_at: str = ""


class HealthMonitor:
    """多维代码健康仪表盘."""

    # 维度定义（名称, 满分, 权重, 计算方法描述）
    _DIMENSIONS: list[dict[str, Any]] = [
        {"name": "duplication_rate", "max": 100, "w": 1.5, "desc": "重复函数占比(越低越好)"},
        {"name": "shared_coverage", "max": 100, "w": 1.2, "desc": "shared/函数覆盖率"},
        {"name": "signature_collisions", "max": 100, "w": 1.5, "desc": "签名碰撞数(0=满分)"},
        {"name": "import_health", "max": 100, "w": 0.8, "desc": "import健康度"},
        {"name": "stale_shared_count", "max": 100, "w": 0.8, "desc": "过期共享函数数"},
        {"name": "auto_fix_success_rate", "max": 100, "w": 1.0, "desc": "自动修复成功率"},
        {"name": "micro_clone_density", "max": 100, "w": 1.3, "desc": "微克隆密度(越低越好)"},
        {"name": "blast_radius_score", "max": 100, "w": 1.5, "desc": "Monoculture爆炸半径BRS"},
        {"name": "shared_burden_score", "max": 100, "w": 1.0, "desc": "Import表面积SBS"},
        {"name": "simplicity_audit_score", "max": 100, "w": 1.2, "desc": "引擎自审计SAS"},
        {"name": "contract_consistency", "max": 100, "w": 1.0, "desc": "API契约一致性"},
        {"name": "cross_boundary_health", "max": 100, "w": 0.8, "desc": "跨边界克隆健康度"},
        {"name": "fpr_7d", "max": 100, "w": 0.8, "desc": "7天误报率(越低越好)"},
        {"name": "cache_hit_ratio", "max": 100, "w": 0.6, "desc": "缓存命中率"},
        {"name": "detection_latency_inverse", "max": 100, "w": 0.6, "desc": "检测延迟(逆数化)"},
        {"name": "fix_doom_loop_count", "max": 100, "w": 0.8, "desc": "Doom Loop触发数"},
        {"name": "known_shared_ratio", "max": 100, "w": 0.8, "desc": "已知shared等价函数占比"},
        {"name": "intentional_duplicate_ratio", "max": 100, "w": 0.5, "desc": "有意重复占比(设计模式等)"},
    ]

    def compute(
        self,
        metrics: dict[str, float],
        previous_overall: int | None = None,
        hotspots: list[dict[str, Any]] | None = None,
    ) -> HealthReport:
        """计算多维 Health Score 0-100."""
        hotspots = hotspots or []
        dimensions: list[HealthDimension] = []

        total_weight = 0.0
        weighted_sum = 0.0

        for dim_def in self._DIMENSIONS:
            name = dim_def["name"]
            raw = metrics.get(name, 100.0)
            weight = float(dim_def["w"])

            score = max(0.0, min(100.0, raw))

            dimensions.append(
                HealthDimension(
                    name=name,
                    score=score,
                    weight=weight,
                    status=self._classify_dimension(score),
                )
            )

            weighted_sum += score * weight
            total_weight += weight

        overall = int(round(weighted_sum / total_weight)) if total_weight > 0 else 0
        overall = max(0, min(100, overall))

        trend = self._determine_trend(previous_overall, overall)

        grade = self._compute_grade(overall)

        session_summary = self._build_session_summary(overall, trend, hotspots, dimensions)

        return HealthReport(
            overall=overall,
            trend=trend,
            grade=grade,
            dimensions=dimensions,
            hotspots=hotspots[:3],
            session_summary=session_summary,
            generated_at=datetime.now(UTC).isoformat(),
        )

    # ── 内部 ──────────────────────────────────────────────────

    @staticmethod
    def _classify_dimension(score: float) -> str:
        if score >= 90:
            return "excellent"
        if score >= 70:
            return "good"
        if score >= 50:
            return "warning"
        return "critical"

    @staticmethod
    def _determine_trend(prev: int | None, curr: int) -> str:
        if prev is None:
            return "flat"
        diff = curr - prev
        if diff >= 5:
            return "up"
        if diff <= -5:
            return "down"
        return "flat"

    @staticmethod
    def _compute_grade(overall: int) -> str:
        if overall >= 90:
            return "A"
        if overall >= 80:
            return "B"
        if overall >= 70:
            return "C"
        if overall >= 60:
            return "D"
        return "F"

    def _build_session_summary(
        self,
        overall: int,
        trend: str,
        hotspots: list[dict[str, Any]],
        dimensions: list[HealthDimension],
    ) -> str:
        trend_icon = {"up": "↑", "down": "↓", "flat": "→"}.get(trend, "→")
        critical_dims = [d for d in dimensions if d.status == "critical"]
        hotspot_names = [h.get("category", "?") for h in hotspots[:3]]

        lines = [
            f"| Dedup Health | {overall} | {trend_icon} | Grade {self._compute_grade(overall)} | {datetime.now(UTC).strftime('%m-%d %H:%M')} |",
        ]
        if hotspot_names:
            lines.append(f"| Hotspots | {', '.join(hotspot_names)} |")
        if critical_dims:
            lines.append(f"| Critical | {', '.join(d.name for d in critical_dims[:3])} |")

        return "\n".join(lines)
