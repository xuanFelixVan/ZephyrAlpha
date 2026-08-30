# [BLUEPRINT] MOD-SIGQC-005 | docs/03_modules/_domain_signal_quality/signal_quality_benchmark/blueprint.md
# [MODULE] zephyr.signal_quality.signal_quality_benchmark
# [DOMAIN] D_SIGQC
# [DEPENDENCIES] 无（对比核心纯内存；benchmark_series/clock/alert_sink 全注入）
# [CONSUMERS] 运行时装配批（周度对比报告 / 偏离告警接 alert 路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 当前IC/覆盖率/稳定性vs滚动历史基线(剔除最新快照,窗长baseline_window)与基准策略(buy-hold语义注入基准IC序列,代表值=序列均值); 偏离绝对值严格>阈值方告警; 周度报告按recorded_at的ISO周聚合确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal_quality/signal_quality_benchmark/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SignalBenchmarkError(占位 ZA-SIGQC-UNREGISTERED-SIGNAL-BENCHMARK)——空strategy_id/指标越界/空基准序列/基准值越界/历史不足对比/未知策略报告时抛
# [TESTS] tests/signal_quality/test_signal_quality_benchmark.py
# [A_module] module_id=MOD-SIGQC-005 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
SignalQualityBenchmark — 信号质量基准对比器（MOD-SIGQC-005）。

B14-04630（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SIGQC-004，A9
D-SIGNAL-157）：当前 IC/覆盖率/稳定性 vs 滚动历史基线与基准策略（buy-hold
语义注入基准序列）+ 偏离超阈告警 + 周度对比报告。

查重分工（蓝图 §0）：degradation_detector（MOD-SIGQC-001）=信号自身滑窗
降级检测（基线=自身历史窗）；signal_degradation_monitor（MOD-SIGQC-004）
=三指标滚动窗阈值监控；本件=跨参照系对比（历史基线 + 外部基准策略序列）
与周度报告，零交集。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: benchmark_series 参数
#   fields: 参数 benchmark_series（无注解）
#   code: signal_quality_benchmark.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: baseline_window 参数
#   fields: 参数 baseline_window（无注解）
#   code: signal_quality_benchmark.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: deviation_threshold 参数
#   fields: 参数 deviation_threshold（无注解）
#   code: signal_quality_benchmark.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: signal_quality_benchmark.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SignalQualityBenchmark
#   name_en: SignalQualityBenchmark
#   intro: 信号质量基准对比器（纯内存/DI）。
#   desc: 信号质量基准对比器（纯内存/DI）。 - 基准策略：buy-hold 语义，经 benchmark_series（基准 IC 序列）注入， 代表值 = 序列均值。 - 历史基线：…；公共方法（定义序）: benchma…
#   inputs: benchmark_series baseline_window deviation_threshold clock alert_sink
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: SignalQualityBenchmark
#   downstream: 运行时装配批（周度对比报告 / 偏离告警接 alert 路由）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from collections import deque
from dataclasses import dataclass
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "BenchmarkComparison",
    "BenchmarkDeviation",
    "QualitySnapshot",
    "SignalBenchmarkError",
    "SignalQualityBenchmark",
    "WeeklyEntry",
    "WeeklyReport",
]

#: 对比指标词表（闭合）
_METRICS: Final[tuple[str, str, str]] = ("ic", "coverage", "stability")


class SignalBenchmarkError(Exception):
    """基准对比输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIGQC-UNREGISTERED-SIGNAL-BENCHMARK。
    """


@dataclass(frozen=True)
class QualitySnapshot:
    """单策略单期质量快照（frozen）。ic∈[-1,1]；coverage/stability∈[0,1]。"""

    strategy_id: str
    ic: float
    coverage: float
    stability: float
    recorded_at: datetime.datetime


@dataclass(frozen=True)
class BenchmarkDeviation:
    """偏离告警载荷（frozen）。kind: baseline=历史基线 / benchmark=基准策略。"""

    strategy_id: str
    kind: str
    metric: str
    current: float
    reference: float
    deviation: float
    threshold: float
    raised_at: datetime.datetime


@dataclass(frozen=True)
class BenchmarkComparison:
    """当前 vs 历史基线 vs 基准策略对比结果（frozen）。"""

    strategy_id: str
    baseline_size: int
    current_ic: float
    current_coverage: float
    current_stability: float
    baseline_ic: float
    baseline_coverage: float
    baseline_stability: float
    benchmark_ic: float
    ic_deviation_vs_baseline: float
    coverage_deviation_vs_baseline: float
    stability_deviation_vs_baseline: float
    ic_deviation_vs_benchmark: float
    alerts: tuple[BenchmarkDeviation, ...]
    compared_at: datetime.datetime


@dataclass(frozen=True)
class WeeklyEntry:
    """周度聚合条目（ISO 周）。"""

    iso_year: int
    iso_week: int
    sample_size: int
    ic_mean: float
    coverage_mean: float
    stability_mean: float
    ic_deviation_vs_benchmark: float


@dataclass(frozen=True)
class WeeklyReport:
    """周度对比报告（frozen；周条目按 (iso_year, iso_week) 排序）。"""

    strategy_id: str
    benchmark_ic: float
    weeks: tuple[WeeklyEntry, ...]
    generated_at: datetime.datetime


class SignalQualityBenchmark:
    """信号质量基准对比器（纯内存/DI）。

    - 基准策略：buy-hold 语义，经 benchmark_series（基准 IC 序列）注入，
      代表值 = 序列均值。
    - 历史基线：每策略滚动窗（剔除最新快照的最近 baseline_window 期）均值。
    - 偏离判定：|当前 - 参照| 严格大于阈值 → 告警（baseline 三维 +
      benchmark IC 维）；alert_sink 异常仅记日志，不阻断。
    - 周度报告：按 recorded_at 的 ISO 周聚合，确定性排序。
    """

    def __init__(
        self,
        *,
        benchmark_series: Sequence[float],
        baseline_window: int = 12,
        deviation_threshold: float = 0.1,
        clock: Callable[[], datetime.datetime] | None = None,
        alert_sink: Callable[[BenchmarkDeviation], None] | None = None,
    ) -> None:
        if not benchmark_series:
            raise SignalBenchmarkError("benchmark_series 为空（基准策略须注入基准序列）")
        for value in benchmark_series:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not -1.0 <= float(value) <= 1.0:
                raise SignalBenchmarkError(f"基准序列值须在 [-1,1]，实际 {value!r}")
        if baseline_window < 1:
            raise SignalBenchmarkError(f"baseline_window 须 ≥1，实际 {baseline_window!r}")
        if not deviation_threshold > 0.0:
            raise SignalBenchmarkError(f"deviation_threshold 须 >0，实际 {deviation_threshold!r}")
        self._benchmark: tuple[float, ...] = tuple(float(v) for v in benchmark_series)
        self._benchmark_mean = sum(self._benchmark) / len(self._benchmark)
        self._baseline_window = baseline_window
        self._threshold = float(deviation_threshold)
        self._clock = clock or datetime.datetime.now
        self._alert_sink = alert_sink
        self._history: dict[str, deque[QualitySnapshot]] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _alert(self, deviation: BenchmarkDeviation) -> None:
        _log.warning(
            "基准偏离: %s %s.%s 偏离 %.4f（参照 %.4f）",
            deviation.strategy_id,
            deviation.kind,
            deviation.metric,
            deviation.deviation,
            deviation.reference,
        )
        if self._alert_sink is not None:
            try:
                self._alert_sink(deviation)
            except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                _log.exception("alert_sink 告警失败: %s", deviation.strategy_id)

    def _history_of(self, strategy_id: str) -> deque[QualitySnapshot]:
        hist = self._history.get(strategy_id)
        if hist is None:
            raise SignalBenchmarkError(f"未知策略: {strategy_id!r}（无快照）")
        return hist

    # ── 快照登记 ──────────────────────────────────────────────────────────

    @property
    def benchmark_mean(self) -> float:
        """基准策略代表值（注入基准序列均值）。"""
        return self._benchmark_mean

    def record(self, snapshot: QualitySnapshot) -> None:
        """登记质量快照（非法输入 Fail-Closed）。"""
        if not isinstance(snapshot, QualitySnapshot):
            raise SignalBenchmarkError(f"非法快照类型: {type(snapshot)!r}")
        if not snapshot.strategy_id:
            raise SignalBenchmarkError("strategy_id 为空")
        if not -1.0 <= snapshot.ic <= 1.0:
            raise SignalBenchmarkError(f"ic 须在 [-1,1]，实际 {snapshot.ic!r}")
        if not 0.0 <= snapshot.coverage <= 1.0:
            raise SignalBenchmarkError(f"coverage 须在 [0,1]，实际 {snapshot.coverage!r}")
        if not 0.0 <= snapshot.stability <= 1.0:
            raise SignalBenchmarkError(f"stability 须在 [0,1]，实际 {snapshot.stability!r}")
        if not isinstance(snapshot.recorded_at, datetime.datetime):
            raise SignalBenchmarkError("recorded_at 须为 datetime")
        hist = self._history.get(snapshot.strategy_id)
        if hist is None:
            hist = deque(maxlen=self._baseline_window + 1)
            self._history[snapshot.strategy_id] = hist
        hist.append(snapshot)

    # ── 对比与报告 ─────────────────────────────────────────────────────────

    def compare(self, strategy_id: str) -> BenchmarkComparison:
        """当前快照 vs 滚动历史基线 vs 基准策略；偏离超阈告警。"""
        if not strategy_id:
            raise SignalBenchmarkError("strategy_id 为空")
        hist = self._history_of(strategy_id)
        if len(hist) < 2:
            raise SignalBenchmarkError(f"历史基线不足: {strategy_id!r} 需 ≥2 期快照，实际 {len(hist)}")
        current = hist[-1]
        baseline = list(hist)[:-1]
        n = len(baseline)
        b_ic = sum(s.ic for s in baseline) / n
        b_cov = sum(s.coverage for s in baseline) / n
        b_stab = sum(s.stability for s in baseline) / n
        d_ic = current.ic - b_ic
        d_cov = current.coverage - b_cov
        d_stab = current.stability - b_stab
        d_bench = current.ic - self._benchmark_mean
        now = self._clock()
        alerts: list[BenchmarkDeviation] = []
        for metric, cur, ref, dev in (
            ("ic", current.ic, b_ic, d_ic),
            ("coverage", current.coverage, b_cov, d_cov),
            ("stability", current.stability, b_stab, d_stab),
        ):
            if abs(dev) > self._threshold:
                alerts.append(
                    BenchmarkDeviation(
                        strategy_id=strategy_id,
                        kind="baseline",
                        metric=metric,
                        current=cur,
                        reference=ref,
                        deviation=dev,
                        threshold=self._threshold,
                        raised_at=now,
                    )
                )
        if abs(d_bench) > self._threshold:
            alerts.append(
                BenchmarkDeviation(
                    strategy_id=strategy_id,
                    kind="benchmark",
                    metric="ic",
                    current=current.ic,
                    reference=self._benchmark_mean,
                    deviation=d_bench,
                    threshold=self._threshold,
                    raised_at=now,
                )
            )
        for deviation in alerts:
            self._alert(deviation)
        return BenchmarkComparison(
            strategy_id=strategy_id,
            baseline_size=n,
            current_ic=current.ic,
            current_coverage=current.coverage,
            current_stability=current.stability,
            baseline_ic=b_ic,
            baseline_coverage=b_cov,
            baseline_stability=b_stab,
            benchmark_ic=self._benchmark_mean,
            ic_deviation_vs_baseline=d_ic,
            coverage_deviation_vs_baseline=d_cov,
            stability_deviation_vs_baseline=d_stab,
            ic_deviation_vs_benchmark=d_bench,
            alerts=tuple(alerts),
            compared_at=now,
        )

    def weekly_report(self, strategy_id: str) -> WeeklyReport:
        """周度对比报告：按 recorded_at 的 ISO 周聚合（确定性排序）。"""
        if not strategy_id:
            raise SignalBenchmarkError("strategy_id 为空")
        hist = self._history_of(strategy_id)
        buckets: dict[tuple[int, int], list[QualitySnapshot]] = {}
        for snap in hist:
            iso = snap.recorded_at.isocalendar()
            buckets.setdefault((iso.year, iso.week), []).append(snap)
        weeks: list[WeeklyEntry] = []
        for key in sorted(buckets):
            snaps = buckets[key]
            n = len(snaps)
            ic_mean = sum(s.ic for s in snaps) / n
            weeks.append(
                WeeklyEntry(
                    iso_year=key[0],
                    iso_week=key[1],
                    sample_size=n,
                    ic_mean=ic_mean,
                    coverage_mean=sum(s.coverage for s in snaps) / n,
                    stability_mean=sum(s.stability for s in snaps) / n,
                    ic_deviation_vs_benchmark=ic_mean - self._benchmark_mean,
                )
            )
        return WeeklyReport(
            strategy_id=strategy_id,
            benchmark_ic=self._benchmark_mean,
            weeks=tuple(weeks),
            generated_at=self._clock(),
        )
