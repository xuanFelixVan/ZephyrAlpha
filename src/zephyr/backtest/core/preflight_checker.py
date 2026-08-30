# [BLUEPRINT] MOD-BT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [ALGO_FLOW] 目的: 回测启动前数据质量前置检查（15号 memo BM-BT-02-D，函数级 MVP，绑定入口由调用方注入）
# [ALGO_FLOW] 输入: symbols/start/end + 可选 DQ 检查函数表（默认空集，纯结构检查）
# [ALGO_FLOW] 输出: PreflightReport(passed/violations/skipped)，fail-visible 不静默
# [ALGO_FLOW] 不变量: 无数据注入时保守通过结构检查并标 skipped；任何 DQ 违规→passed=False
# [TTL] permanent
"""
回测前置检查器（15_data_feature_layer_spec BM-BT-02-D，函数级落地）。

重评条件触发前不接线回测引擎——调用方显式调用 `run_backtest_preflight` 并
自行决定阻断策略。DQ 检查函数经 `dq_checks` 注入（与 governance data_quality
run_dq_check 同签名：(table, where)->list[str] 违规描述），未注入时仅做参数
结构检查并标记 skipped（防"无检查却绿"假通过）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: symbols 参数
#   fields: 参数 symbols，类型注解 list[str]
#   code: preflight_checker.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: start 参数
#   fields: 参数 start，类型注解 datetime.date
#   code: preflight_checker.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: end 参数
#   fields: 参数 end，类型注解 datetime.date
#   code: preflight_checker.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: dq_checks 参数
#   fields: 参数 dq_checks，类型注解 dict[str, Callable[[str, str], list[str…
#   code: preflight_checker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① run_backtest_preflight
#   name_en: run_backtest_preflight
#   intro: 回测启动前数据质量前置检查（BM-BT-02-D）。
#   desc: 回测启动前数据质量前置检查（BM-BT-02-D）。 Args: symbols: 回测标的集（空列表=结构违规）。 start/end: 回测窗口（end<start=结构违规…；源码 L82-L118
#   inputs: symbols start end dq_checks required_tables
#   outputs: PreflightReport
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: PreflightReport
#   name_en: PreflightReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
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
from collections.abc import Callable
from dataclasses import dataclass, field

# ZA-BT-0036: 前置检查违规（fail-visible，调用方决定阻断）
ERR_PREFLIGHT_VIOLATION = "ZA-BT-0036"

#: 回测必需最小数据表（15 号 §要点③ 口径）
REQUIRED_TABLES = ("c1_market.kline_daily",)


@dataclass(frozen=True)
class PreflightReport:
    """前置检查报告。passed=False 时 violations 非空（fail-visible）。"""

    passed: bool
    violations: tuple[str, ...] = ()
    skipped: tuple[str, ...] = ()
    checked_at: datetime.date = field(default_factory=datetime.date.today)


def run_backtest_preflight(
    symbols: list[str],
    start: datetime.date,
    end: datetime.date,
    dq_checks: dict[str, Callable[[str, str], list[str]]] | None = None,
    required_tables: tuple[str, ...] = REQUIRED_TABLES,
) -> PreflightReport:
    """回测启动前数据质量前置检查（BM-BT-02-D）。

    Args:
        symbols: 回测标的集（空列表=结构违规）。
        start/end: 回测窗口（end<start=结构违规）。
        dq_checks: {检查名: (table, where)->违规描述列表}，None=仅结构检查。
        required_tables: 必需数据表，逐表过全部 dq_checks。
    """
    violations: list[str] = []
    skipped: list[str] = []

    if not symbols:
        violations.append(f"{ERR_PREFLIGHT_VIOLATION}: symbols 为空")
    if end < start:
        violations.append(f"{ERR_PREFLIGHT_VIOLATION}: 窗口倒置 {start}>{end}")

    if dq_checks:
        where = f"trade_date >= '{start}' AND trade_date <= '{end}'"
        for table in required_tables:
            for name, fn in dq_checks.items():
                for v in fn(table, where):
                    violations.append(f"{ERR_PREFLIGHT_VIOLATION}: {table}/{name}: {v}")
    else:
        skipped.append("dq_checks 未注入——仅结构检查（DQ 维度 skipped，非通过）")

    return PreflightReport(
        passed=not violations,
        violations=tuple(violations),
        skipped=tuple(skipped),
    )
