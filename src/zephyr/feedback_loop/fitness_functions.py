# AI-generated: 架构适应度函数框架（T-4-04, B17）
"""
FitnessFunctionFramework — 架构适应度函数（Fitness Function）框架
=================================================================
Task ID      : T-4-04 (B17)
依赖         : B10 ✅（gate_engine.py）
ADR          : ADR-0030（SQLite gates 表）、ADR-0033（MCP stdio）
safety_level : M

职责
----
实现 5 类架构适应度度量，持续监控系统架构健康度：

1. module_coupling         — 依赖图密度 < 阈值（默认 0.3）
2. test_coverage           — pytest --cov 覆盖率 ≥ 65%
3. compliance_rate         — 门禁通过率 ≥ 90%（读 gates 表）
4. knowledge_activation_rate — 知识条目激活率 ≥ 30%
5. hallucination_interception_rate — 幻觉拦截率 ≥ 70%

集成接口
--------
- `from_gate_results(gate_rows)` — 从 GateEngine.evaluate() 结果列表构造适应度输入
- `run_all(inputs)` → FitnessReport — 执行全部 5 类度量
- `to_json_report(report)` → str — JSON 报告（持久化 / 传送用）
- `to_trend_data(reports)` → list[dict] — 趋势图时间序列数据

阈值配置
--------
所有阈值在 `FitnessThresholds` dataclass 中集中定义，可按需覆盖。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional, Sequence


__all__ = [
    "FitnessThresholds",
    "FitnessMetric",
    "MetricStatus",
    "FitnessReport",
    "FitnessFunctionFramework",
    "FitnessInputs",
    "from_gate_results",
]

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

_UTC = timezone.utc

# 5 类度量名称（类型键）
METRIC_MODULE_COUPLING = "module_coupling"
METRIC_TEST_COVERAGE = "test_coverage"
METRIC_COMPLIANCE_RATE = "compliance_rate"
METRIC_KNOWLEDGE_ACTIVATION = "knowledge_activation_rate"
METRIC_HALLUCINATION_INTERCEPTION = "hallucination_interception_rate"


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


class MetricStatus:
    """度量状态枚举（字符串常量）。"""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass
class FitnessThresholds:
    """所有适应度阈值集中定义（可按需覆盖）。

    Attributes
    ----------
    module_coupling_max:
        依赖图密度上限（超出视为过耦合）。
    test_coverage_min:
        测试覆盖率下限（百分比，0–100）。
    compliance_rate_min:
        门禁通过率下限（0.0–1.0）。
    knowledge_activation_min:
        知识激活率下限（0.0–1.0）。
    hallucination_interception_min:
        幻觉拦截率下限（0.0–1.0）。
    warn_margin:
        从 FAIL 到 WARN 的缓冲区比例（相对阈值的百分比偏移）。
    """

    module_coupling_max: float = 0.30
    test_coverage_min: float = 65.0
    compliance_rate_min: float = 0.90
    knowledge_activation_min: float = 0.30
    hallucination_interception_min: float = 0.70
    warn_margin: float = 0.05  # 5% 缓冲区


@dataclass
class FitnessMetric:
    """单条适应度度量结果。

    Attributes
    ----------
    metric_name:
        度量名称（五选一常量）。
    value:
        实测值（耦合度为 float，覆盖率为 0–100 float，其余为 0.0–1.0 float）。
    threshold:
        判定阈值（来自 FitnessThresholds）。
    status:
        PASS / WARN / FAIL。
    detail:
        附加说明（可选）。
    measured_at:
        度量时间（ISO 8601）。
    """

    metric_name: str
    value: float
    threshold: float
    status: str
    detail: Optional[str] = None
    measured_at: str = field(
        default_factory=lambda: datetime.now(_UTC).isoformat()
    )


@dataclass
class FitnessReport:
    """一次 run_all 的完整度量报告。

    Attributes
    ----------
    report_id:
        唯一 ID（ISO 时间戳）。
    metrics:
        5 条 FitnessMetric。
    overall_status:
        PASS（所有 PASS）/ WARN（有 WARN 无 FAIL）/ FAIL（有 FAIL）。
    summary:
        文字摘要。
    generated_at:
        报告生成时间（ISO 8601）。
    """

    report_id: str
    metrics: list[FitnessMetric]
    overall_status: str
    summary: str
    generated_at: str = field(
        default_factory=lambda: datetime.now(_UTC).isoformat()
    )

    @property
    def passed(self) -> bool:
        """整体是否通过（无 FAIL）。"""
        return self.overall_status != MetricStatus.FAIL

    def get_metric(self, metric_name: str) -> Optional[FitnessMetric]:
        """按名称查找度量结果。"""
        for m in self.metrics:
            if m.metric_name == metric_name:
                return m
        return None


@dataclass
class FitnessInputs:
    """传入 run_all 的原始度量输入数据。

    Attributes
    ----------
    dependency_edges:
        依赖图边列表，每项为 ``(from_module, to_module)``；
        用于计算模块耦合度。
    module_count:
        系统总模块数（计算图密度分母用）。
    coverage_pct:
        测试覆盖率（0–100 float），从 pytest --cov 报告提取。
    gate_total:
        门禁总运行次数（gates 表 COUNT）。
    gate_passed:
        门禁通过次数（gates 表 WHERE passed=1 COUNT）。
    ke_total:
        知识条目总数（knowledge 表 COUNT）。
    ke_activated:
        已激活（indexed/verified）条目数。
    hallucination_total:
        幻觉检测总次数。
    hallucination_intercepted:
        成功拦截次数（结论为幻觉且被阻断）。
    """

    dependency_edges: list[tuple[str, str]] = field(default_factory=list)
    module_count: int = 0
    coverage_pct: float = 0.0
    gate_total: int = 0
    gate_passed: int = 0
    ke_total: int = 0
    ke_activated: int = 0
    hallucination_total: int = 0
    hallucination_intercepted: int = 0


# ---------------------------------------------------------------------------
# 便利工厂：从 GateEngine 结果构建 FitnessInputs
# ---------------------------------------------------------------------------


def from_gate_results(
    gate_rows: Sequence[dict[str, Any]],
    *,
    dependency_edges: Optional[list[tuple[str, str]]] = None,
    module_count: int = 0,
    coverage_pct: float = 0.0,
    ke_total: int = 0,
    ke_activated: int = 0,
    hallucination_total: int = 0,
    hallucination_intercepted: int = 0,
) -> FitnessInputs:
    """从 GateEngine.evaluate() 结果行列表构造 FitnessInputs。

    Parameters
    ----------
    gate_rows:
        每项为含 ``"passed"`` 键（bool 或 0/1 int）的 dict，
        对应 gates 表一行或 GateResult 序列化。
    dependency_edges:
        依赖图边列表（可选）。
    module_count:
        总模块数（可选）。
    coverage_pct:
        测试覆盖率百分比（可选）。
    ke_total / ke_activated:
        知识库统计（可选）。
    hallucination_total / hallucination_intercepted:
        幻觉检测统计（可选）。

    Returns
    -------
    FitnessInputs
        可直接传入 ``FitnessFunctionFramework.run_all``。
    """
    total = len(gate_rows)
    passed = sum(
        1 for row in gate_rows if bool(row.get("passed", row.get("passed", False)))
    )
    return FitnessInputs(
        dependency_edges=dependency_edges or [],
        module_count=module_count,
        coverage_pct=coverage_pct,
        gate_total=total,
        gate_passed=passed,
        ke_total=ke_total,
        ke_activated=ke_activated,
        hallucination_total=hallucination_total,
        hallucination_intercepted=hallucination_intercepted,
    )


# ---------------------------------------------------------------------------
# 核心框架
# ---------------------------------------------------------------------------


class FitnessFunctionFramework:
    """架构适应度函数执行框架。

    使用方式
    --------
    ::

        thresholds = FitnessThresholds(test_coverage_min=70.0)
        ff = FitnessFunctionFramework(thresholds=thresholds)

        inputs = FitnessInputs(
            dependency_edges=[("A", "B"), ("B", "C")],
            module_count=10,
            coverage_pct=72.0,
            gate_total=100, gate_passed=95,
            ke_total=50, ke_activated=20,
            hallucination_total=30, hallucination_intercepted=25,
        )

        report = ff.run_all(inputs)
        print(ff.to_json_report(report))
    """

    def __init__(
        self,
        thresholds: Optional[FitnessThresholds] = None,
    ) -> None:
        """初始化框架，可覆盖默认阈值。

        Parameters
        ----------
        thresholds:
            适应度阈值配置，默认使用 FitnessThresholds 默认值。
        """
        self._th = thresholds or FitnessThresholds()

    # ------------------------------------------------------------------
    # 5 类度量实现
    # ------------------------------------------------------------------

    def measure_module_coupling(
        self,
        dependency_edges: list[tuple[str, str]],
        module_count: int,
    ) -> FitnessMetric:
        """度量模块耦合度（依赖图密度）。

        密度 = 边数 / (模块数 × (模块数 - 1) / 2)；
        密度 < threshold → PASS，≤ threshold + warn_margin → WARN，否则 FAIL。

        Parameters
        ----------
        dependency_edges:
            有向依赖边列表，``(from_module, to_module)``。
        module_count:
            系统总模块数（图节点数上界）。

        Returns
        -------
        FitnessMetric
        """
        if module_count <= 1:
            density = 0.0
            detail = f"单模块系统，密度定义为 0.0（module_count={module_count}）"
        else:
            max_edges = module_count * (module_count - 1) / 2
            # 去重（无向图视角）
            unique_edges = {
                tuple(sorted(e)) for e in dependency_edges
            }
            density = len(unique_edges) / max_edges
            detail = (
                f"edges={len(unique_edges)}, modules={module_count}, "
                f"max_edges={int(max_edges)}, density={density:.4f}"
            )

        th = self._th.module_coupling_max
        warn_limit = th + self._th.warn_margin
        if density <= th:
            status = MetricStatus.PASS
        elif density <= warn_limit:
            status = MetricStatus.WARN
        else:
            status = MetricStatus.FAIL

        return FitnessMetric(
            metric_name=METRIC_MODULE_COUPLING,
            value=round(density, 6),
            threshold=th,
            status=status,
            detail=detail,
        )

    def measure_test_coverage(self, coverage_pct: float) -> FitnessMetric:
        """度量测试覆盖率（百分比，0–100）。

        覆盖率 ≥ threshold → PASS，≥ threshold - warn_margin*100 → WARN，否则 FAIL。

        Parameters
        ----------
        coverage_pct:
            pytest --cov 报告中的总覆盖率百分比（0.0–100.0）。
        """
        th = self._th.test_coverage_min
        warn_limit = th - self._th.warn_margin * 100  # 转换为百分点

        if coverage_pct >= th:
            status = MetricStatus.PASS
        elif coverage_pct >= warn_limit:
            status = MetricStatus.WARN
        else:
            status = MetricStatus.FAIL

        return FitnessMetric(
            metric_name=METRIC_TEST_COVERAGE,
            value=round(coverage_pct, 2),
            threshold=th,
            status=status,
            detail=f"coverage={coverage_pct:.1f}%, threshold={th}%",
        )

    def measure_compliance_rate(
        self,
        gate_total: int,
        gate_passed: int,
    ) -> FitnessMetric:
        """度量门禁合规率（gates 表通过率）。

        合规率 = gate_passed / gate_total；
        ≥ threshold → PASS，≥ threshold - warn_margin → WARN，否则 FAIL。

        Parameters
        ----------
        gate_total:
            门禁总运行次数（含所有 gate_id）。
        gate_passed:
            门禁通过次数（passed=1）。
        """
        if gate_total == 0:
            rate = 1.0
            detail = "无门禁记录，默认合规率 100%"
        else:
            rate = gate_passed / gate_total
            detail = f"passed={gate_passed}, total={gate_total}, rate={rate:.4f}"

        th = self._th.compliance_rate_min
        warn_limit = th - self._th.warn_margin

        if rate >= th:
            status = MetricStatus.PASS
        elif rate >= warn_limit:
            status = MetricStatus.WARN
        else:
            status = MetricStatus.FAIL

        return FitnessMetric(
            metric_name=METRIC_COMPLIANCE_RATE,
            value=round(rate, 6),
            threshold=th,
            status=status,
            detail=detail,
        )

    def measure_knowledge_activation_rate(
        self,
        ke_total: int,
        ke_activated: int,
    ) -> FitnessMetric:
        """度量知识激活率（已激活 / 总条目）。

        激活率 ≥ threshold → PASS，≥ threshold - warn_margin → WARN，否则 FAIL。

        Parameters
        ----------
        ke_total:
            knowledge 表总条目数。
        ke_activated:
            状态为 INDEXED / VERIFIED 的条目数。
        """
        if ke_total == 0:
            rate = 0.0
            detail = "知识库为空，激活率 = 0.0"
        else:
            rate = ke_activated / ke_total
            detail = f"activated={ke_activated}, total={ke_total}, rate={rate:.4f}"

        th = self._th.knowledge_activation_min
        warn_limit = th - self._th.warn_margin

        if rate >= th:
            status = MetricStatus.PASS
        elif rate >= warn_limit:
            status = MetricStatus.WARN
        else:
            status = MetricStatus.FAIL

        return FitnessMetric(
            metric_name=METRIC_KNOWLEDGE_ACTIVATION,
            value=round(rate, 6),
            threshold=th,
            status=status,
            detail=detail,
        )

    def measure_hallucination_interception_rate(
        self,
        hallucination_total: int,
        hallucination_intercepted: int,
    ) -> FitnessMetric:
        """度量幻觉拦截率（intercepted / total）。

        拦截率 ≥ threshold → PASS，≥ threshold - warn_margin → WARN，否则 FAIL。

        Parameters
        ----------
        hallucination_total:
            HallucinationDetector 总检测次数。
        hallucination_intercepted:
            成功识别并阻断的幻觉次数。
        """
        if hallucination_total == 0:
            rate = 1.0
            detail = "无幻觉检测记录，默认拦截率 100%"
        else:
            rate = hallucination_intercepted / hallucination_total
            detail = (
                f"intercepted={hallucination_intercepted}, "
                f"total={hallucination_total}, rate={rate:.4f}"
            )

        th = self._th.hallucination_interception_min
        warn_limit = th - self._th.warn_margin

        if rate >= th:
            status = MetricStatus.PASS
        elif rate >= warn_limit:
            status = MetricStatus.WARN
        else:
            status = MetricStatus.FAIL

        return FitnessMetric(
            metric_name=METRIC_HALLUCINATION_INTERCEPTION,
            value=round(rate, 6),
            threshold=th,
            status=status,
            detail=detail,
        )

    # ------------------------------------------------------------------
    # 集成入口
    # ------------------------------------------------------------------

    def run_all(self, inputs: FitnessInputs) -> FitnessReport:
        """执行全部 5 类适应度度量，返回汇总报告。

        Parameters
        ----------
        inputs:
            FitnessInputs 数据容器（来自直接赋值或 from_gate_results()）。

        Returns
        -------
        FitnessReport
            含 5 条 FitnessMetric + overall_status + summary。
        """
        metrics: list[FitnessMetric] = [
            self.measure_module_coupling(
                inputs.dependency_edges, inputs.module_count
            ),
            self.measure_test_coverage(inputs.coverage_pct),
            self.measure_compliance_rate(inputs.gate_total, inputs.gate_passed),
            self.measure_knowledge_activation_rate(
                inputs.ke_total, inputs.ke_activated
            ),
            self.measure_hallucination_interception_rate(
                inputs.hallucination_total, inputs.hallucination_intercepted
            ),
        ]

        # 汇总状态：有 FAIL → FAIL；有 WARN → WARN；否则 PASS
        statuses = {m.status for m in metrics}
        if MetricStatus.FAIL in statuses:
            overall = MetricStatus.FAIL
        elif MetricStatus.WARN in statuses:
            overall = MetricStatus.WARN
        else:
            overall = MetricStatus.PASS

        fail_names = [m.metric_name for m in metrics if m.status == MetricStatus.FAIL]
        warn_names = [m.metric_name for m in metrics if m.status == MetricStatus.WARN]

        if overall == MetricStatus.PASS:
            summary = "所有适应度度量通过"
        elif overall == MetricStatus.WARN:
            summary = f"WARN 度量：{warn_names}"
        else:
            summary = f"FAIL 度量：{fail_names}；WARN 度量：{warn_names}"

        now = datetime.now(_UTC)
        report_id = f"FF-{now.strftime('%Y%m%dT%H%M%S')}"

        return FitnessReport(
            report_id=report_id,
            metrics=metrics,
            overall_status=overall,
            summary=summary,
            generated_at=now.isoformat(),
        )

    # ------------------------------------------------------------------
    # 输出格式
    # ------------------------------------------------------------------

    @staticmethod
    def to_json_report(report: FitnessReport) -> str:
        """将 FitnessReport 序列化为 JSON 字符串（UTF-8，ensure_ascii=False）。

        Parameters
        ----------
        report:
            run_all() 的输出。

        Returns
        -------
        str
            格式化的 JSON 字符串（indent=2）。
        """
        data: dict[str, Any] = {
            "report_id": report.report_id,
            "overall_status": report.overall_status,
            "summary": report.summary,
            "generated_at": report.generated_at,
            "metrics": [
                {
                    "metric_name": m.metric_name,
                    "value": m.value,
                    "threshold": m.threshold,
                    "status": m.status,
                    "detail": m.detail,
                    "measured_at": m.measured_at,
                }
                for m in report.metrics
            ],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def to_trend_data(reports: Sequence[FitnessReport]) -> list[dict[str, Any]]:
        """将多次 FitnessReport 转为趋势图时间序列数据。

        每个时间点输出一条 dict，包含所有 5 类度量实测值 + overall_status。
        适合直接传给前端图表库（如 ECharts / Plotly）。

        Parameters
        ----------
        reports:
            按时间升序排列的 FitnessReport 列表。

        Returns
        -------
        list[dict[str, Any]]
            格式::

                [
                  {
                    "timestamp": "2026-04-24T10:00:00+00:00",
                    "overall_status": "PASS",
                    "module_coupling": 0.15,
                    "test_coverage": 72.0,
                    "compliance_rate": 0.95,
                    "knowledge_activation_rate": 0.45,
                    "hallucination_interception_rate": 0.80,
                  },
                  ...
                ]
        """
        result: list[dict[str, Any]] = []
        for rpt in reports:
            row: dict[str, Any] = {
                "timestamp": rpt.generated_at,
                "overall_status": rpt.overall_status,
            }
            for m in rpt.metrics:
                row[m.metric_name] = m.value
            result.append(row)
        return result
