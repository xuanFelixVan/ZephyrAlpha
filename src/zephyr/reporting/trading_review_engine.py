# [BLUEPRINT] MOD-RPT-034 | docs/03_modules/_domain_reporting/trading_review_engine/blueprint.md
# [MODULE] zephyr.reporting.trading_review_engine
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] 无（协议核心纯内存；thresholds/detector_metrics/clock 全注入）
# [CONSUMERS] 运行时装配批（日终四模式审查扫描 / 审查报告产出与版本化查询）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审查模式词表闭合(cancel_rate|order_rate|self_trade|pump_dump); 阈值表须覆盖全部四模式(缺项 Fail-Closed); 判定口径 value>threshold 才记异常(等于不记); 指标值须有限实数(NaN/inf 拒绝); 审查报告三要素齐备(异常标的+证据+处置建议); 报告按日版本化(同日重跑版本递增); findings 按模式序+标的确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_reporting/trading_review_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] TradingReviewError(占位 ZA-RPT-UNREGISTERED-TRADING-REVIEW)——阈值表缺模式/负阈值/检测数据未注入/非法指标/未知报告或版本时抛
# [TESTS] tests/reporting/test_trading_review_engine.py
# [A_module] module_id=MOD-RPT-034 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""TradingReviewEngine — A股交易审查引擎（MOD-RPT-034）。

B14-04662（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-RPT-009，A9
D-REPORTING-15）：**日终交易审查**——撤单率/申报速率/自成交/拉抬打压
**四模式扫描**（阈值表注入，词表闭合缺项 Fail-Closed）→ **审查报告**
（异常标的 + 证据 + 处置建议三要素）+ 联动检测数据注入 + **报告版本化**
（同日重跑版本递增，按日留存全部版本）。

边界：trading_compliance_detector（compliance）=盘中实时合规检测（本件
消费其日终汇总指标，不重复盘中判定）；处置建议=确定性模式映射文案（本件
不做自动处置执行）；本件纯内存/DI，不触网不落盘。
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "PatternMetric",
    "ReviewFinding",
    "ReviewPattern",
    "ReviewReport",
    "TradingReviewEngine",
    "TradingReviewError",
]


class TradingReviewError(Exception):
    """交易审查输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-RPT-UNREGISTERED-TRADING-REVIEW。
    """


class ReviewPattern(str, Enum):
    """审查模式（词表闭合，声明序即报告排序序）。"""

    CANCEL_RATE = "cancel_rate"  # 撤单率
    ORDER_RATE = "order_rate"  # 申报速率
    SELF_TRADE = "self_trade"  # 自成交
    PUMP_DUMP = "pump_dump"  # 拉抬打压


#: 模式排序序（findings 确定性排序键）
_PATTERN_RANK: Final[dict[ReviewPattern, int]] = {
    ReviewPattern.CANCEL_RATE: 0,
    ReviewPattern.ORDER_RATE: 1,
    ReviewPattern.SELF_TRADE: 2,
    ReviewPattern.PUMP_DUMP: 3,
}

#: 处置建议（模式→确定性文案；本件不执行处置，仅产出建议）
_SUGGESTIONS: Final[dict[ReviewPattern, str]] = {
    ReviewPattern.CANCEL_RATE: "撤单率超阈：冻结该标的当日申报权限，提交人工合规复核",
    ReviewPattern.ORDER_RATE: "申报速率超阈：限速申报并核查程序化交易报备状态",
    ReviewPattern.SELF_TRADE: "疑似自成交：暂停相关账户对该标的交易并启动成交对手核查",
    ReviewPattern.PUMP_DUMP: "疑似拉抬打压：列入重点监控名单，留存分时证据上报",
}


@dataclass(frozen=True)
class PatternMetric:
    """单标的单模式日终检测指标（frozen；联动检测数据注入载体）。"""

    symbol: str
    pattern: ReviewPattern
    value: float
    evidence: dict


@dataclass(frozen=True)
class ReviewFinding:
    """审查异常条目（frozen；异常标的+证据+处置建议三要素齐备）。"""

    symbol: str
    pattern: ReviewPattern
    value: float
    threshold: float
    evidence: dict
    suggestion: str


@dataclass(frozen=True)
class ReviewReport:
    """日终审查报告（frozen；按日版本化）。"""

    report_date: datetime.date
    version: int
    findings: tuple[ReviewFinding, ...]
    generated_at: datetime.datetime


class TradingReviewEngine:
    """日终四模式交易审查件（扫描 + 报告产出 + 版本化查询）。"""

    def __init__(
        self,
        *,
        thresholds: Mapping[ReviewPattern, float],
        detector_metrics: Callable[[datetime.date], Sequence[PatternMetric]] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not thresholds:
            raise TradingReviewError("thresholds 为空（四模式阈值表缺失）")
        for pattern in ReviewPattern:
            if pattern not in thresholds:
                raise TradingReviewError(f"阈值表缺模式: {pattern.value}（词表闭合须全覆盖）")
            value = float(thresholds[pattern])
            if not math.isfinite(value) or value < 0.0:
                raise TradingReviewError(f"非法阈值: {pattern.value}={thresholds[pattern]!r}")
        self._thresholds: dict[ReviewPattern, float] = {
            p: float(thresholds[p]) for p in ReviewPattern
        }
        self._detector = detector_metrics
        self._clock = clock or datetime.datetime.now
        self._reports: dict[datetime.date, list[ReviewReport]] = {}

    # ── 日终审查 ──────────────────────────────────────────────────────────

    def run_daily_review(self, trade_date: datetime.date) -> ReviewReport:
        """日终四模式扫描：注入检测指标→超阈判定→三要素报告→版本化留存。"""
        if not isinstance(trade_date, datetime.date):
            raise TradingReviewError(f"非法 trade_date: {trade_date!r}")
        if self._detector is None:
            raise TradingReviewError("detector_metrics 未注入（联动检测数据缺失，Fail-Closed）")
        findings: list[ReviewFinding] = []
        for metric in self._detector(trade_date):
            if not metric.symbol:
                raise TradingReviewError("指标 symbol 为空")
            if not isinstance(metric.pattern, ReviewPattern):
                raise TradingReviewError(f"非法审查模式: {metric.pattern!r}")
            value = float(metric.value)
            if not math.isfinite(value):
                raise TradingReviewError(f"指标值非有限实数: {metric.symbol}/{metric.pattern!r}")
            threshold = self._thresholds[metric.pattern]
            if value > threshold:
                findings.append(
                    ReviewFinding(
                        symbol=metric.symbol,
                        pattern=metric.pattern,
                        value=value,
                        threshold=threshold,
                        evidence=dict(metric.evidence),
                        suggestion=_SUGGESTIONS[metric.pattern],
                    )
                )
        findings.sort(key=lambda f: (_PATTERN_RANK[f.pattern], f.symbol, -f.value))
        versions = self._reports.setdefault(trade_date, [])
        report = ReviewReport(
            report_date=trade_date,
            version=len(versions) + 1,
            findings=tuple(findings),
            generated_at=self._clock(),
        )
        versions.append(report)
        _log.info(
            "日终审查完成: %s v%d 异常 %d 项", trade_date, report.version, len(findings)
        )
        return report

    # ── 查询 ─────────────────────────────────────────────────────────────

    def report_of(
        self,
        trade_date: datetime.date,
        version: int | None = None,
    ) -> ReviewReport:
        """审查报告查询（默认最新版；未知日期/版本 Fail-Closed）。"""
        versions = self._reports.get(trade_date)
        if not versions:
            raise TradingReviewError(f"未知审查报告: {trade_date!r}")
        if version is None:
            return versions[-1]
        if version < 1 or version > len(versions):
            raise TradingReviewError(
                f"未知报告版本: {trade_date} v{version}（现存 v1..v{len(versions)}）"
            )
        return versions[version - 1]

    def versions_of(self, trade_date: datetime.date) -> tuple[int, ...]:
        """某日全部报告版本号（升序；未知日期 Fail-Closed）。"""
        versions = self._reports.get(trade_date)
        if not versions:
            raise TradingReviewError(f"未知审查报告: {trade_date!r}")
        return tuple(r.version for r in versions)
