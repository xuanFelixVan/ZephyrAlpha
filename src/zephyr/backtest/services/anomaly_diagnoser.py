# [BLUEPRINT] MOD-BT-023 | docs/03_modules/_domain_backtest/anomaly_diagnoser/blueprint.md
# [MODULE] zephyr.backtest.services.anomaly_diagnoser
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.services.data_quality_checker ; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查 ; MOD-BT-019(report_generator)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] AnomalyConfig/Anomaly/DiagnosisReport frozen不可变; passed=无ERROR级异常; 缺失字段跳过不报错; 纯阈值判定不修改输入
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DiagnosisError(ZA-BT-0023)
# [TESTS] tests/backtest/test_anomaly_diagnoser.py
# [A_module] module_id=MOD-BT-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_BACKTEST — Anomaly Diagnoser (回测异常诊断器)

对回测结果指标执行异常检测, 输出诊断报告+修复建议。
覆盖性能异常(高Sharpe/高胜率/深回撤/负收益)、统计异常(交易不足/周期过短)、
一致性异常(高收益低Sharpe/缺失基准), 每条异常附带可操作修复建议。

属 A 类基础设施(纯阈值判定+报告生成), 纯基础层不涉及策略。

设计真源: depgraph MOD-BT-023
蓝图: docs/03_modules/_domain_backtest/anomaly_diagnoser/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 回测结果字典 dict
#   fields: strategy_id + sharpe_ratio + win_rate + max_drawdown + annual_return + trades_count + start/end_date + benchmark_symbol
#   code: result
# - id: I2
#   name: 异常检测配置 AnomalyConfig frozen
#   fields: high_sharpe=3.0 + high_win_rate=0.80 + deep_drawdown=-0.50 + min_trades=30 + min_backtest_days=252 + high_return=0.20 + low_sharpe=0.5
#   code: AnomalyConfig L55-90
# 层: 算法
# - id: A1
#   name_zh: ① 性能异常检测
#   name_en: diagnose(性能段)
#   intro: 高Sharpe高胜率疑过拟合，深回撤直接ERROR，负收益WARN
#   desc: sharpe>3.0记WARN → win_rate>80%记WARN → max_drawdown<-50%记ERROR → annual_return<0记WARN 每条附修复建议（L199-250）
#   inputs: I1 I2
#   outputs: 性能异常列表
# - id: A2
#   name_zh: ② 统计异常检测
#   name_en: diagnose(统计段)+_calc_backtest_days
#   intro: 交易次数太少或回测周期太短则统计上不显著
#   desc: trades_count<30记WARN → |end_date-start_date|.days<252记WARN（L252-277, L342-359）
#   inputs: I1 I2
#   outputs: 统计异常列表
# - id: A3
#   name_zh: ③ 一致性异常检测
#   name_en: diagnose(一致性段)
#   intro: 高收益却低Sharpe的矛盾组合告警，缺基准给提示
#   desc: annual_return>20%且sharpe<0.5记WARN → 无benchmark_symbol记INFO（L279-303）
#   inputs: I1 I2
#   outputs: 一致性异常列表
# - id: A4
#   name_zh: ④ 诊断报告聚合
#   name_en: diagnose(聚合段)
#   intro: 汇总全部异常，无ERROR级则诊断通过
#   desc: total_checks计数 → passed=无ERROR级异常 → 组装DiagnosisReport（L305-319）
#   inputs: A1 A2 A3
#   outputs: DiagnosisReport
#   invariant: passed=无ERROR级异常; 缺失字段跳过不报错; 纯阈值判定不改输入
# 层: 输出
# - id: O1
#   name_zh: 异常诊断报告 DiagnosisReport
#   name_en: DiagnosisReport
#   intro: 异常列表每条附可操作修复建议，passed标识是否过诊断
#   invariant: passed=无ERROR级异常
#   downstream: report_generator MOD-BT-019 ; 人工审查
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# A1 --> A4
# A2 --> A4
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

from zephyr.backtest.services.data_quality_checker import Severity
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "DiagnosisError",
    "AnomalyConfig",
    "Anomaly",
    "DiagnosisReport",
    "AnomalyDiagnoser",
]

_logger = logging.getLogger(__name__)


class DiagnosisError(ZephyrBaseError):
    """异常诊断异常——输入非法。"""

    error_code = "ZA-BT-0023"


@dataclass(frozen=True)
class AnomalyConfig:
    """异常检测配置——不可变。

    Attributes:
        high_sharpe_threshold: Sharpe 比率异常高阈值。
        high_win_rate_threshold: 胜率异常高阈值。
        deep_drawdown_threshold: 深回撤阈值 (负数)。
        min_trades: 最小交易次数 (统计显著性)。
        min_backtest_days: 最小回测天数。
        high_return_threshold: 高收益阈值。
        low_sharpe_threshold: 低 Sharpe 阈值 (与高收益配合判定)。
    """

    high_sharpe_threshold: float = 3.0
    high_win_rate_threshold: float = 0.80
    deep_drawdown_threshold: float = -0.50
    min_trades: int = 30
    min_backtest_days: int = 252
    high_return_threshold: float = 0.20
    low_sharpe_threshold: float = 0.5

    def __post_init__(self) -> None:
        if self.high_sharpe_threshold <= 0:
            raise DiagnosisError(f"high_sharpe_threshold must be > 0, got {self.high_sharpe_threshold}")
        if not 0 < self.high_win_rate_threshold <= 1:
            raise DiagnosisError(f"high_win_rate_threshold must be in (0,1], got {self.high_win_rate_threshold}")
        if self.min_trades <= 0:
            raise DiagnosisError(f"min_trades must be > 0, got {self.min_trades}")


@dataclass(frozen=True)
class Anomaly:
    """单条异常发现——不可变。

    Attributes:
        rule: 规则名称。
        severity: 严重度 (ERROR/WARN/INFO)。
        message: 异常描述。
        value: 实际值 (可选)。
        threshold: 阈值 (可选)。
        suggestion: 修复建议。
    """

    rule: str
    severity: Severity
    message: str
    value: float | None = None
    threshold: float | None = None
    suggestion: str = ""


@dataclass
class DiagnosisReport:
    """诊断报告。

    Attributes:
        passed: 是否通过 (无 ERROR 级异常)。
        anomalies: 异常列表。
        total_checks: 执行的检查数。
    """

    passed: bool
    anomalies: list[Anomaly] = field(default_factory=list)
    total_checks: int = 0

    @property
    def error_count(self) -> int:
        return sum(1 for a in self.anomalies if a.severity is Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for a in self.anomalies if a.severity is Severity.WARN)

    @property
    def info_count(self) -> int:
        return sum(1 for a in self.anomalies if a.severity is Severity.INFO)

    def anomalies_by_severity(self, severity: Severity) -> list[Anomaly]:
        """按严重度过滤异常。"""
        return [a for a in self.anomalies if a.severity is severity]


class AnomalyDiagnoser:
    """回测异常诊断器——结果指标异常检测+修复建议。

    Usage:
        diag = AnomalyDiagnoser()
        report = diag.diagnose({
            "strategy_id": "strat_a",
            "sharpe_ratio": 4.5,
            "win_rate": 0.85,
            "max_drawdown": -0.15,
            "trades_count": 120,
            "annual_return": 0.25,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        })
        if not report.passed:
            for a in report.anomalies_by_severity(Severity.ERROR):
                print(f"[{a.severity.value}] {a.rule}: {a.suggestion}")
    """

    def __init__(self, config: AnomalyConfig | None = None) -> None:
        self._config = config if config is not None else AnomalyConfig()

    @property
    def config(self) -> AnomalyConfig:
        """配置 (只读)。"""
        return self._config

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------
    def diagnose(self, result: dict) -> DiagnosisReport:
        """对回测结果执行异常诊断。

        Args:
            result: 回测结果字典 (含 BacktestResult 标准字段)。

        Returns:
            DiagnosisReport (passed=无ERROR级异常)。

        Raises:
            DiagnosisError: result 非 dict / 缺少 strategy_id。
        """
        if not isinstance(result, dict):
            raise DiagnosisError(f"result must be a dict, got {type(result).__name__}")
        if not result.get("strategy_id"):
            raise DiagnosisError("result.strategy_id 不能为空")

        cfg = self._config
        anomalies: list[Anomaly] = []
        checks = 0

        # ── 性能异常 ──
        sharpe = _to_float(result.get("sharpe_ratio"))
        if sharpe is not None:
            checks += 1
            if sharpe > cfg.high_sharpe_threshold:
                anomalies.append(
                    Anomaly(
                        rule="high_sharpe",
                        severity=Severity.WARN,
                        message=f"Sharpe 比率异常高: {sharpe:.2f} > {cfg.high_sharpe_threshold}",
                        value=sharpe,
                        threshold=cfg.high_sharpe_threshold,
                        suggestion="检查过拟合: 执行 Walk-Forward 分析 + 样本外验证",
                    )
                )

        win_rate = _to_float(result.get("win_rate"))
        if win_rate is not None:
            checks += 1
            if win_rate > cfg.high_win_rate_threshold:
                anomalies.append(
                    Anomaly(
                        rule="high_win_rate",
                        severity=Severity.WARN,
                        message=f"胜率异常高: {win_rate:.1%} > {cfg.high_win_rate_threshold:.0%}",
                        value=win_rate,
                        threshold=cfg.high_win_rate_threshold,
                        suggestion="检查前瞻偏差: 确认 PIT 铁律 + 截断重算验证",
                    )
                )

        max_dd = _to_float(result.get("max_drawdown"))
        if max_dd is not None:
            checks += 1
            if max_dd < cfg.deep_drawdown_threshold:
                anomalies.append(
                    Anomaly(
                        rule="deep_drawdown",
                        severity=Severity.ERROR,
                        message=f"最大回撤过深: {max_dd:.1%} < {cfg.deep_drawdown_threshold:.0%}",
                        value=max_dd,
                        threshold=cfg.deep_drawdown_threshold,
                        suggestion="降低仓位 / 增加止损 / 分散标的",
                    )
                )

        annual_return = _to_float(result.get("annual_return"))
        if annual_return is not None:
            checks += 1
            if annual_return < 0:
                anomalies.append(
                    Anomaly(
                        rule="negative_return",
                        severity=Severity.WARN,
                        message=f"年化收益为负: {annual_return:.1%}",
                        value=annual_return,
                        threshold=0.0,
                        suggestion="策略不盈利, 检查策略逻辑或市场适配性",
                    )
                )

        # ── 统计异常 ──
        trades = _to_int(result.get("trades_count"))
        if trades is not None:
            checks += 1
            if trades < cfg.min_trades:
                anomalies.append(
                    Anomaly(
                        rule="few_trades",
                        severity=Severity.WARN,
                        message=f"交易次数不足: {trades} < {cfg.min_trades}",
                        value=float(trades),
                        threshold=float(cfg.min_trades),
                        suggestion="增加回测周期或降低交易频率阈值",
                    )
                )

        backtest_days = _calc_backtest_days(result)
        if backtest_days is not None:
            checks += 1
            if backtest_days < cfg.min_backtest_days:
                anomalies.append(
                    Anomaly(
                        rule="short_period",
                        severity=Severity.WARN,
                        message=f"回测周期过短: {backtest_days}天 < {cfg.min_backtest_days}天",
                        value=float(backtest_days),
                        threshold=float(cfg.min_backtest_days),
                        suggestion=f"至少覆盖 {cfg.min_backtest_days} 天 (约1年交易日)",
                    )
                )

        # ── 一致性异常 ──
        if annual_return is not None and sharpe is not None:
            checks += 1
            if annual_return > cfg.high_return_threshold and sharpe < cfg.low_sharpe_threshold:
                anomalies.append(
                    Anomaly(
                        rule="high_return_low_sharpe",
                        severity=Severity.WARN,
                        message=(
                            f"高收益低Sharpe: return={annual_return:.1%} "
                            f"但 sharpe={sharpe:.2f} < {cfg.low_sharpe_threshold}"
                        ),
                        value=sharpe,
                        threshold=cfg.low_sharpe_threshold,
                        suggestion="收益不稳定, 检查波动率或换手率",
                    )
                )

        checks += 1
        benchmark = result.get("benchmark_symbol")
        if not benchmark:
            anomalies.append(
                Anomaly(
                    rule="missing_benchmark",
                    severity=Severity.INFO,
                    message="未指定基准标的",
                    suggestion="添加基准(如沪深300)便于相对绩效评估",
                )
            )

        passed = not any(a.severity is Severity.ERROR for a in anomalies)
        _logger.debug(
            "异常诊断: %d checks, %d anomalies (E=%d W=%d I=%d), passed=%s",
            checks,
            len(anomalies),
            sum(1 for a in anomalies if a.severity is Severity.ERROR),
            sum(1 for a in anomalies if a.severity is Severity.WARN),
            sum(1 for a in anomalies if a.severity is Severity.INFO),
            passed,
        )
        return DiagnosisReport(
            passed=passed,
            anomalies=anomalies,
            total_checks=checks,
        )


def _to_float(value: object) -> float | None:
    """安全转 float, 失败返回 None。"""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: object) -> int | None:
    """安全转 int, 失败返回 None。"""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _calc_backtest_days(result: dict) -> int | None:
    """计算回测天数 (从 start_date 和 end_date)。"""
    start = result.get("start_date")
    end = result.get("end_date")
    if start is None or end is None:
        return None
    try:
        if isinstance(start, datetime):
            start_dt = start
        else:
            start_dt = datetime.fromisoformat(str(start))
        if isinstance(end, datetime):
            end_dt = end
        else:
            end_dt = datetime.fromisoformat(str(end))
        return abs((end_dt - start_dt).days)
    except (ValueError, TypeError):
        return None
