# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1
# [MODULE] zephyr.governance.semantic_audit.self_health
# [DOMAIN] D-GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] run_semantic_audit.py; blueprint.md §3.1 Stage 11
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 7 SLI + 5 容量 SLI 阈值不可违反; HealthReport/CapacityReport 结构不可变
# [MODIFY-GUARD] blueprint.md §3.1 Stage 11; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] HealthCheckError on collector failure
# [TESTS] tests/semantic-auditor/test_self_health.py
# [A_module] module_id=MOD-SEM_self_health | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
semantic-auditor/self_health.py — MOD-INF-028 §3.1 Stage 11
============================================================
SelfHealthMonitor: 7 SLI + 5 容量 SLI 健康监控 + 退化检测。

SLI 定义（蓝图 §1179）:
  1. 审计延迟 — P95 管道耗时 <30s
  2. 触发召回率 — 黄金数据集检出率 >99%
  3. 安全误拦率 — 该过被拦概率 <0.5%
  4. LLM 可用率 — Stage 6 成功率 >90%
  5. Token 效率 — 每次审计 Token 用量 ≤500
  6. 自愈成功率 — Stage 7 修复成功率 >80%
  7. 退化评估 — 连续 N 次性能趋势 无连续退化

容量 SLI（蓝图 §1194-1198）:
  CAP-01 并发审计数 <max_concurrent
  CAP-02 LLM Fix Queue 深度 <50
  CAP-03 审计缓存命中率 >60%
  CAP-04 全局引用索引新鲜度 <300s
  CAP-05 SelfHealer 修复队列长度 <20
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

__all__ = [
    "CapacityMetric",
    "CapacityReport",
    "HealthReport",
    "SLIResult",
    "SelfHealthMonitor",
]


@dataclass(frozen=True)
class SLIResult:
    """单个 SLI 检查结果。"""

    name: str
    value: float
    threshold: float
    healthy: bool
    unit: str = ""
    description: str = ""


@dataclass
class HealthReport:
    """7 SLI 健康检查报告。"""

    checked_at: str = ""
    overall_healthy: bool = True
    sli_results: list[SLIResult] = field(default_factory=list)
    degradation_detected: bool = False
    degradation_detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "checked_at": self.checked_at,
            "overall_healthy": self.overall_healthy,
            "degradation_detected": self.degradation_detected,
            "degradation_detail": self.degradation_detail,
            "sli_results": [
                {
                    "name": r.name,
                    "value": r.value,
                    "threshold": r.threshold,
                    "healthy": r.healthy,
                    "unit": r.unit,
                    "description": r.description,
                }
                for r in self.sli_results
            ],
        }


@dataclass(frozen=True)
class CapacityMetric:
    """单个容量指标结果。"""

    name: str
    value: float
    threshold: float
    healthy: bool
    unit: str = ""
    description: str = ""


@dataclass
class CapacityReport:
    """5 容量 SLI 报告。"""

    checked_at: str = ""
    overall_healthy: bool = True
    metrics: list[CapacityMetric] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "checked_at": self.checked_at,
            "overall_healthy": self.overall_healthy,
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "threshold": m.threshold,
                    "healthy": m.healthy,
                    "unit": m.unit,
                    "description": m.description,
                }
                for m in self.metrics
            ],
        }


class _MetricsCollector(Protocol):
    """指标采集协议 — 解耦 SelfHealthMonitor 与具体数据源。"""

    def get_scan_latency_p95(self) -> float: ...
    def get_trigger_recall_rate(self) -> float: ...
    def get_safety_false_block_rate(self) -> float: ...
    def get_llm_availability_rate(self) -> float: ...
    def get_token_per_audit(self) -> float: ...
    def get_self_heal_success_rate(self) -> float: ...
    def get_concurrent_audit_count(self) -> float: ...
    def get_llm_fix_queue_depth(self) -> float: ...
    def get_cache_hit_rate(self) -> float: ...
    def get_ref_index_freshness_seconds(self) -> float: ...
    def get_healer_queue_length(self) -> float: ...
    def get_latency_history(self) -> list[float]: ...


@dataclass
class DefaultMetricsCollector:
    """默认指标采集器 — 从运行时状态和文件系统采集。

    当 SemanticAuditor 完整管线尚未运行时，返回默认值使健康检查可执行。
    """

    _latency_history: list[float] = field(default_factory=list)
    _concurrent_count: int = 0
    _max_concurrent: int = 4
    _llm_fix_queue_depth: int = 0
    _healer_queue_length: int = 0
    _ref_index_path: str = ""

    def get_scan_latency_p95(self) -> float:
        if not self._latency_history:
            return 0.0
        sorted_latencies = sorted(self._latency_history)
        idx = max(0, int(len(sorted_latencies) * 0.95) - 1)
        return sorted_latencies[idx]

    def get_trigger_recall_rate(self) -> float:
        return 100.0

    def get_safety_false_block_rate(self) -> float:
        return 0.0

    def get_llm_availability_rate(self) -> float:
        return 100.0

    def get_token_per_audit(self) -> float:
        return 0.0

    def get_self_heal_success_rate(self) -> float:
        return 100.0

    def get_concurrent_audit_count(self) -> float:
        return float(self._concurrent_count)

    def get_llm_fix_queue_depth(self) -> float:
        return float(self._llm_fix_queue_depth)

    def get_cache_hit_rate(self) -> float:
        return 100.0

    def get_ref_index_freshness_seconds(self) -> float:
        if not self._ref_index_path:
            return 0.0
        p = Path(self._ref_index_path)
        if not p.exists():
            return float("inf")
        elapsed = time.time() - p.stat().st_mtime
        return elapsed

    def get_healer_queue_length(self) -> float:
        return float(self._healer_queue_length)

    def get_latency_history(self) -> list[float]:
        return list(self._latency_history)


class SelfHealthMonitor:
    """SemanticAuditor 自身健康监控 — 蓝图 §3.1 Stage 11。

    7 SLI + 5 容量 SLI + 退化检测。
    通过 _MetricsCollector 协议解耦数据源，支持注入自定义采集器。
    """

    SLI_THRESHOLDS: dict[str, dict[str, Any]] = {
        "audit_latency_p95": {"threshold": 30.0, "unit": "s", "compare": "lt", "description": "P95 管道耗时"},
        "trigger_recall_rate": {"threshold": 99.0, "unit": "%", "compare": "gt", "description": "黄金数据集检出率"},
        "safety_false_block_rate": {"threshold": 0.5, "unit": "%", "compare": "lt", "description": "该过被拦概率"},
        "llm_availability_rate": {"threshold": 90.0, "unit": "%", "compare": "gt", "description": "Stage 6 成功率"},
        "token_per_audit": {
            "threshold": 500.0,
            "unit": "tokens",
            "compare": "lt",
            "description": "每次审计 Token 用量",
        },
        "self_heal_success_rate": {
            "threshold": 80.0,
            "unit": "%",
            "compare": "gt",
            "description": "Stage 7 修复成功率",
        },
    }

    CAPACITY_THRESHOLDS: dict[str, dict[str, Any]] = {
        "concurrent_audit_count": {
            "threshold": 4.0,
            "unit": "count",
            "compare": "lt",
            "description": "并发审计数 <max_concurrent",
        },
        "llm_fix_queue_depth": {
            "threshold": 50.0,
            "unit": "count",
            "compare": "lt",
            "description": "LLM Fix Queue 深度",
        },
        "cache_hit_rate": {"threshold": 60.0, "unit": "%", "compare": "gt", "description": "审计缓存命中率"},
        "ref_index_freshness": {"threshold": 300.0, "unit": "s", "compare": "lt", "description": "全局引用索引新鲜度"},
        "healer_queue_length": {
            "threshold": 20.0,
            "unit": "count",
            "compare": "lt",
            "description": "SelfHealer 修复队列长度",
        },
    }

    DEGRADATION_WINDOW = 3

    def __init__(
        self,
        collector: _MetricsCollector | None = None,
        max_concurrent: int = 4,
        ref_index_path: str = "",
    ) -> None:
        if collector is None:
            self._collector: _MetricsCollector = DefaultMetricsCollector(
                _max_concurrent=max_concurrent,
                _ref_index_path=ref_index_path,
            )
            if isinstance(self._collector, DefaultMetricsCollector):
                self._collector._max_concurrent = max_concurrent
                self._collector._ref_index_path = ref_index_path
                self.SLI_THRESHOLDS["concurrent_audit_count"] = {
                    "threshold": float(max_concurrent),
                    "unit": "count",
                    "compare": "lt",
                    "description": "并发审计数 <max_concurrent",
                }
                self.CAPACITY_THRESHOLDS["concurrent_audit_count"] = {
                    "threshold": float(max_concurrent),
                    "unit": "count",
                    "compare": "lt",
                    "description": "并发审计数 <max_concurrent",
                }
        else:
            self._collector = collector

    def _check_sli(self, name: str, value: float, cfg: dict[str, Any]) -> SLIResult:
        threshold = cfg["threshold"]
        if cfg["compare"] == "lt":
            healthy = value < threshold
        else:
            healthy = value > threshold
        return SLIResult(
            name=name,
            value=value,
            threshold=threshold,
            healthy=healthy,
            unit=cfg["unit"],
            description=cfg["description"],
        )

    def _check_capacity_metric(self, name: str, value: float, cfg: dict[str, Any]) -> CapacityMetric:
        threshold = cfg["threshold"]
        if cfg["compare"] == "lt":
            healthy = value < threshold
        else:
            healthy = value > threshold
        return CapacityMetric(
            name=name,
            value=value,
            threshold=threshold,
            healthy=healthy,
            unit=cfg["unit"],
            description=cfg["description"],
        )

    def _detect_degradation(self) -> tuple[bool, str]:
        """退化检测 — 连续 DEGRADATION_WINDOW 次延迟递增视为退化。"""
        history = self._collector.get_latency_history()
        if len(history) < self.DEGRADATION_WINDOW:
            return False, ""
        recent = history[-self.DEGRADATION_WINDOW :]
        for i in range(1, len(recent)):
            if recent[i] <= recent[i - 1]:
                return False, ""
        values_str = " -> ".join(f"{v:.2f}" for v in recent)
        return True, f"连续 {self.DEGRADATION_WINDOW} 次延迟递增: {values_str}"

    def check_health(self) -> HealthReport:
        """执行 7 SLI 健康检查，返回 HealthReport。"""
        c = self._collector
        sli_results = [
            self._check_sli("audit_latency_p95", c.get_scan_latency_p95(), self.SLI_THRESHOLDS["audit_latency_p95"]),
            self._check_sli(
                "trigger_recall_rate", c.get_trigger_recall_rate(), self.SLI_THRESHOLDS["trigger_recall_rate"]
            ),
            self._check_sli(
                "safety_false_block_rate",
                c.get_safety_false_block_rate(),
                self.SLI_THRESHOLDS["safety_false_block_rate"],
            ),
            self._check_sli(
                "llm_availability_rate", c.get_llm_availability_rate(), self.SLI_THRESHOLDS["llm_availability_rate"]
            ),
            self._check_sli("token_per_audit", c.get_token_per_audit(), self.SLI_THRESHOLDS["token_per_audit"]),
            self._check_sli(
                "self_heal_success_rate", c.get_self_heal_success_rate(), self.SLI_THRESHOLDS["self_heal_success_rate"]
            ),
        ]

        degradation_detected, degradation_detail = self._detect_degradation()
        degradation_result = SLIResult(
            name="degradation",
            value=1.0 if degradation_detected else 0.0,
            threshold=1.0,
            healthy=not degradation_detected,
            unit="bool",
            description="连续 N 次性能趋势退化检测",
        )
        sli_results.append(degradation_result)

        overall_healthy = all(r.healthy for r in sli_results)

        return HealthReport(
            checked_at=datetime.now(UTC).isoformat(),
            overall_healthy=overall_healthy,
            sli_results=sli_results,
            degradation_detected=degradation_detected,
            degradation_detail=degradation_detail,
        )

    def is_healthy(self) -> bool:
        """所有 SLI 在阈值内 → True。"""
        return self.check_health().overall_healthy

    def get_capacity(self) -> CapacityReport:
        """执行 5 容量 SLI 检查，返回 CapacityReport。"""
        c = self._collector
        metrics = [
            self._check_capacity_metric(
                "concurrent_audit_count",
                c.get_concurrent_audit_count(),
                self.CAPACITY_THRESHOLDS["concurrent_audit_count"],
            ),
            self._check_capacity_metric(
                "llm_fix_queue_depth", c.get_llm_fix_queue_depth(), self.CAPACITY_THRESHOLDS["llm_fix_queue_depth"]
            ),
            self._check_capacity_metric(
                "cache_hit_rate", c.get_cache_hit_rate(), self.CAPACITY_THRESHOLDS["cache_hit_rate"]
            ),
            self._check_capacity_metric(
                "ref_index_freshness",
                c.get_ref_index_freshness_seconds(),
                self.CAPACITY_THRESHOLDS["ref_index_freshness"],
            ),
            self._check_capacity_metric(
                "healer_queue_length", c.get_healer_queue_length(), self.CAPACITY_THRESHOLDS["healer_queue_length"]
            ),
        ]

        overall_healthy = all(m.healthy for m in metrics)

        return CapacityReport(
            checked_at=datetime.now(UTC).isoformat(),
            overall_healthy=overall_healthy,
            metrics=metrics,
        )

    def record_scan_latency(self, latency_seconds: float) -> None:
        """记录一次审计延迟，供退化检测使用。"""
        if isinstance(self._collector, DefaultMetricsCollector):
            self._collector._latency_history.append(latency_seconds)

    def set_concurrent_count(self, count: int) -> None:
        """设置当前并发审计数。"""
        if isinstance(self._collector, DefaultMetricsCollector):
            self._collector._concurrent_count = count

    def set_llm_fix_queue_depth(self, depth: int) -> None:
        """设置 LLM Fix Queue 深度。"""
        if isinstance(self._collector, DefaultMetricsCollector):
            self._collector._llm_fix_queue_depth = depth

    def set_healer_queue_length(self, length: int) -> None:
        """设置 SelfHealer 修复队列长度。"""
        if isinstance(self._collector, DefaultMetricsCollector):
            self._collector._healer_queue_length = length
