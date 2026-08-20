# [BLUEPRINT] MOD-BT-024 | docs/03_modules/_domain_backtest/result_comparator/blueprint.md
# [MODULE] zephyr.backtest.services.result_comparator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查 ; MOD-BT-019(report_generator)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Config/ComparativeMetric/ResultComparison/ComparisonReport frozen不可变; 不修改输入; 缺失字段→None不报错; 纯标准库
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ResultComparisonError(ZA-BT-0024)
# [TESTS] tests/backtest/test_result_comparator.py
# [A_module] module_id=MOD-BT-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_BACKTEST — Result Comparator (回测结果比较器)

对两组回测结果执行差异分析, 输出结构化比较报告。
覆盖三大维度: 绝对指标比较(年化/总收益/Sharpe/最大回撤/胜率/交易次数)
+ 相对差异计算 + 统计显著性检验(基于均值检验)。

属 A 类基础设施(纯统计比较+阈值判定+报告生成), 纯基础层不涉及策略。

设计真源: D-SIMULATION-53/64 "回测结果对比：多次回测结果的对比分析与差异展示+对比报告"
蓝图: docs/03_modules/_domain_backtest/result_comparator/blueprint.md
SSoT: depgraph MOD-BT-024

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 基线回测结果 dict
#   fields: annual_return + total_return + sharpe_ratio + max_drawdown + win_rate + trades_count + 可选<key>_std
#   code: baseline
# - id: I2
#   name: 候选回测结果 dict
#   fields: 同基线字段集
#   code: candidate
# - id: I3
#   name: 比较配置 ResultComparisonConfig frozen
#   fields: significance_level + min_trades_for_significance + relative_threshold
#   code: ResultComparisonConfig
# 层: 算法
# - id: A1
#   name_zh: ① 逐指标比较主循环
#   name_en: ResultComparator.compare
#   intro: 校验两个dict后按_METRICS清单6项指标逐一比较并计数
#   desc: isinstance校验 → 遍历6指标(取值/差异/显著性/优劣) → 汇总better/worse/significant计数
#   inputs: I1 I2 I3
#   outputs: ResultComparison
#   invariant: 不修改输入; 缺失字段→None不报错
# - id: A2
#   name_zh: ② 绝对/相对差异计算
#   name_en: _compute_diffs
#   intro: 算候选减基线的绝对差和相对差
#   desc: abs_diff=c-b → rel_diff=abs_diff/|b| (b=0或缺失→None)
#   inputs: I1 I2
#   outputs: (absolute_diff, relative_diff)
# - id: A3
#   name_zh: ③ 均值z检验显著性判定
#   name_en: _test_significance
#   intro: 交易数够且有std时用双侧z检验判断差异是否统计显著
#   desc: n<30→False → se=√(std_b²/n_b+std_c²/n_c) → |c-b| > z(α)×se → 显著
#   inputs: I1 I2 I3
#   outputs: is_significant布尔
# - id: A4
#   name_zh: ④ 差异报告组装
#   name_en: generate_diff_report
#   intro: 把比较结果拼成摘要+HTML表格+显著性说明的完整报告
#   desc: compare → _build_summary计数摘要 → _build_html_table七列表 → _build_significance_notes显著/警告说明
#   inputs: I1 I2 I3
#   outputs: ComparisonReport
# 层: 输出
# - id: O1
#   name_zh: 结构化比较结果 ResultComparison
#   name_en: ResultComparison
#   intro: 6项指标的逐项对比+更好/更差/显著计数
#   invariant: frozen不可变
#   downstream: 人工审查 ; MOD-BT-019(report_generator)
# - id: O2
#   name_zh: 差异报告 ComparisonReport
#   name_en: ComparisonReport
#   intro: 摘要文本+HTML对比表+显著性说明列表
#   downstream: 人工审查 ; MOD-BT-019(report_generator)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# I3 --> A3
# A2 --> A1
# A3 --> A1
# I1 --> A4
# I2 --> A4
# I3 --> A4
# A1 --> A4
# A1 --> O1
# A4 --> O2
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "ResultComparisonConfig",
    "ComparativeMetric",
    "ResultComparison",
    "ComparisonReport",
    "ResultComparator",
    "ResultComparisonError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class ResultComparisonError(ZephyrBaseError):
    """回测结果比较输入非法(如非 dict)。"""

    error_code = "ZA-BT-0024"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ResultComparisonConfig:
    """回测结果比较配置——不可变。"""

    significance_level: float = 0.05  # 统计显著性水平 (默认95%置信)
    min_trades_for_significance: int = 30  # 显著性检验最小交易次数
    relative_threshold: float = 0.10  # 相对差异阈值(10%, 备用判定)

    def __post_init__(self) -> None:
        if not 0 < self.significance_level < 1:
            raise ResultComparisonError(f"significance_level must be in (0,1), got {self.significance_level}")
        if self.min_trades_for_significance <= 0:
            raise ResultComparisonError(
                f"min_trades_for_significance must be > 0, got {self.min_trades_for_significance}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型 (frozen 不可变)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ComparativeMetric:
    """单个指标的比较结果——不可变。"""

    name: str
    baseline_value: float | None
    candidate_value: float | None
    absolute_diff: float | None  # candidate - baseline
    relative_diff: float | None  # (candidate - baseline)/|baseline|
    is_significant: bool  # 是否统计显著
    is_better: bool | None  # candidate 是否更好 (None=无法比较/中性)


@dataclass(frozen=True)
class ResultComparison:
    """回测结果比较——不可变。"""

    baseline_id: str
    candidate_id: str
    metrics: list[ComparativeMetric]
    total_metrics: int
    better_count: int
    worse_count: int
    significant_count: int


@dataclass(frozen=True)
class ComparisonReport:
    """比较报告——不可变。"""

    comparison: ResultComparison
    summary: str
    detailed_table: str  # HTML 表格
    significance_notes: list[str] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────────
# 比较器
# ──────────────────────────────────────────────────────────────────────────────

# 显著性检验对应的 z 值 (双侧) —— 0.05 → 1.96
_Z_LEVELS = {0.10: 1.645, 0.05: 1.96, 0.01: 2.576}


def _z_for_level(level: float) -> float:
    """根据显著性水平返回近似 z 值, 未知水平默认 1.96。"""
    return _Z_LEVELS.get(level, 1.96)


# 指标定义: (显示名, 字段键, better 判定函数 or None)
#   better_func(baseline, candidate) -> bool: candidate 是否更好
_MetricDef = tuple[str, str, Callable[[float, float], bool] | None]


def _is_higher_better(baseline: float, candidate: float) -> bool:
    return candidate > baseline


def _is_lower_better(baseline: float, candidate: float) -> bool:
    return candidate < baseline


# 标准指标清单 (顺序即报告表格顺序)
# 注: max_drawdown 在本项目存为负值 (metrics._calculate_max_drawdown 取 drawdown.min(),
# drawdown=(nav-peak)/peak 恒≤0), 故 -0.15(15%回撤) 优于 -0.20(20%回撤),
# 即"更高(更接近0)=更好", 用 _is_higher_better。
_METRICS: list[_MetricDef] = [
    ("年化收益", "annual_return", _is_higher_better),
    ("总收益", "total_return", _is_higher_better),
    ("Sharpe比率", "sharpe_ratio", _is_higher_better),
    ("最大回撤", "max_drawdown", _is_higher_better),
    ("胜率", "win_rate", _is_higher_better),
    ("交易次数", "trades_count", None),
]


class ResultComparator:
    """回测结果比较器——多组回测结果差异分析。

    用法:
        comparator = ResultComparator()
        report = comparator.compare(baseline_result, candidate_result)
        print(report.summary)
        # report.detailed_table 为 HTML 表格字符串

    纯标准库实现, 不修改输入数据。

    Args:
        config: 比较配置 (显著性水平/最小交易次数/相对阈值)
    """

    def __init__(self, config: ResultComparisonConfig | None = None) -> None:
        self._config = config or ResultComparisonConfig()

    @property
    def config(self) -> ResultComparisonConfig:
        return self._config

    # ── 公开 API ──

    def compare(
        self,
        baseline: dict,
        candidate: dict,
        baseline_id: str = "baseline",
        candidate_id: str = "candidate",
    ) -> ResultComparison:
        """比较两组回测结果。

        Args:
            baseline: 基线回测结果 dict (含 annual_return/sharpe_ratio/... 等字段)
            candidate: 候选回测结果 dict
            baseline_id: 基线标识 (用于报告)
            candidate_id: 候选标识

        Returns:
            ResultComparison (含每个指标的 ComparativeMetric)

        Raises:
            ResultComparisonError: baseline/candidate 非 dict
        """
        if not isinstance(baseline, dict):
            raise ResultComparisonError(f"baseline must be a dict, got {type(baseline).__name__}")
        if not isinstance(candidate, dict):
            raise ResultComparisonError(f"candidate must be a dict, got {type(candidate).__name__}")

        comparative_metrics: list[ComparativeMetric] = []
        for name, key, better_func in _METRICS:
            b_val = self._extract_value(baseline, key)
            c_val = self._extract_value(candidate, key)
            abs_diff, rel_diff = self._compute_diffs(b_val, c_val)
            is_sig = self._test_significance(baseline, candidate, key)
            is_better = better_func(b_val, c_val) if better_func and b_val is not None and c_val is not None else None
            comparative_metrics.append(
                ComparativeMetric(
                    name=name,
                    baseline_value=b_val,
                    candidate_value=c_val,
                    absolute_diff=abs_diff,
                    relative_diff=rel_diff,
                    is_significant=is_sig,
                    is_better=is_better,
                )
            )

        better_count = sum(1 for m in comparative_metrics if m.is_better is True)
        worse_count = sum(1 for m in comparative_metrics if m.is_better is False)
        significant_count = sum(1 for m in comparative_metrics if m.is_significant)

        return ResultComparison(
            baseline_id=baseline_id,
            candidate_id=candidate_id,
            metrics=comparative_metrics,
            total_metrics=len(comparative_metrics),
            better_count=better_count,
            worse_count=worse_count,
            significant_count=significant_count,
        )

    def generate_diff_report(
        self,
        baseline: dict,
        candidate: dict,
        baseline_id: str = "baseline",
        candidate_id: str = "candidate",
    ) -> ComparisonReport:
        """比较并生成完整差异报告 (摘要 + HTML 表格 + 显著性说明)。"""
        comparison = self.compare(baseline, candidate, baseline_id, candidate_id)
        summary = self._build_summary(comparison)
        table = self._build_html_table(comparison)
        notes = self._build_significance_notes(comparison)
        return ComparisonReport(
            comparison=comparison,
            summary=summary,
            detailed_table=table,
            significance_notes=notes,
        )

    # ── 内部: 取值与差异计算 ──

    @staticmethod
    def _extract_value(result: dict, key: str) -> float | None:
        """从结果 dict 提取数值, 缺失/None/非数值 → None。"""
        val = result.get(key)
        if val is None:
            return None
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _compute_diffs(b_val: float | None, c_val: float | None) -> tuple[float | None, float | None]:
        """计算绝对差异与相对差异。缺失任一 → (None, None)。"""
        if b_val is None or c_val is None:
            return None, None
        abs_diff = c_val - b_val
        rel_diff = abs_diff / abs(b_val) if b_val != 0 else None
        return abs_diff, rel_diff

    # ── 内部: 显著性检验 ──

    def _test_significance(self, baseline: dict, candidate: dict, key: str) -> bool:
        """基于均值检验判断差异是否统计显著。

        交易次数不足 → False; 缺失 std → False;
        否则 |abs_diff| > z * sqrt(std_b²/n_b + std_c²/n_c) → 显著。
        """
        cfg = self._config
        n_b = self._extract_value(baseline, "trades_count")
        n_c = self._extract_value(candidate, "trades_count")
        if n_b is None or n_c is None:
            return False
        if n_b < cfg.min_trades_for_significance or n_c < cfg.min_trades_for_significance:
            return False

        b_val = self._extract_value(baseline, key)
        c_val = self._extract_value(candidate, key)
        if b_val is None or c_val is None:
            return False

        # 标准差字段约定: <key>_std (如 annual_return_std)
        std_b = self._extract_value(baseline, f"{key}_std")
        std_c = self._extract_value(candidate, f"{key}_std")
        if std_b is None or std_c is None or std_b <= 0 or std_c <= 0:
            return False

        abs_diff = abs(c_val - b_val)
        se = math.sqrt(std_b**2 / n_b + std_c**2 / n_c)
        if se <= 0:
            return False
        z = _z_for_level(cfg.significance_level)
        return abs_diff > z * se

    # ── 内部: 报告生成 ──

    @staticmethod
    def _fmt(v: float | None) -> str:
        if v is None:
            return "N/A"
        if abs(v) >= 1000:
            return f"{v:,.2f}"
        return f"{v:.4f}"

    @staticmethod
    def _fmt_pct(v: float | None) -> str:
        if v is None:
            return "N/A"
        return f"{v:+.2%}"

    @staticmethod
    def _fmt_better(is_better: bool | None) -> str:
        if is_better is True:
            return "✓ 更好"
        if is_better is False:
            return "✗ 更差"
        return "—"

    def _build_summary(self, comp: ResultComparison) -> str:
        return (
            f"比较 {comp.baseline_id} → {comp.candidate_id}: "
            f"共 {comp.total_metrics} 项指标, "
            f"候选更好 {comp.better_count} 项, 更差 {comp.worse_count} 项, "
            f"统计显著 {comp.significant_count} 项。"
        )

    def _build_html_table(self, comp: ResultComparison) -> str:
        rows = [
            "<table border='1' cellpadding='4' cellspacing='0'>",
            "<thead><tr>"
            "<th>指标</th><th>基线</th><th>候选</th>"
            "<th>绝对差异</th><th>相对差异</th>"
            "<th>显著</th><th>判定</th>"
            "</tr></thead>",
            "<tbody>",
        ]
        for m in comp.metrics:
            rows.append(
                "<tr>"
                f"<td>{m.name}</td>"
                f"<td>{self._fmt(m.baseline_value)}</td>"
                f"<td>{self._fmt(m.candidate_value)}</td>"
                f"<td>{self._fmt(m.absolute_diff)}</td>"
                f"<td>{self._fmt_pct(m.relative_diff)}</td>"
                f"<td>{'是' if m.is_significant else '否'}</td>"
                f"<td>{self._fmt_better(m.is_better)}</td>"
                "</tr>"
            )
        rows.append("</tbody></table>")
        return "\n".join(rows)

    def _build_significance_notes(self, comp: ResultComparison) -> list[str]:
        notes: list[str] = []
        cfg = self._config
        sig_metrics = [m for m in comp.metrics if m.is_significant]
        if sig_metrics:
            names = "、".join(m.name for m in sig_metrics)
            notes.append(f"以下指标差异统计显著(α={cfg.significance_level}): {names}")
        else:
            notes.append(
                f"无指标达到统计显著(α={cfg.significance_level}, 最小交易次数 {cfg.min_trades_for_significance})。"
            )
        # 提示交易次数不足的指标
        n_b = next((m for m in comp.metrics if m.name == "交易次数"), None)
        if n_b is not None and n_b.baseline_value is not None:
            if n_b.baseline_value < cfg.min_trades_for_significance:
                notes.append(
                    f"警告: 基线交易次数 {int(n_b.baseline_value)} "
                    f"不足 {cfg.min_trades_for_significance}, 显著性检验已跳过。"
                )
        return notes
