# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.cleaning_rule_engine
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.quality_gate; zephyr.gov_enforcement.rule_enforcement.quality_gate
# [CONSUMERS] zephyr.data.ch_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 规则DSL声明式; 滚动分位阈值限幅内自动生效; 超限挂起等人工approve; 拦截必出报告
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DSL非法(op/缺字段)→CleaningRuleError; 数值不可比→该行该规则跳过(不误伤)
# [TESTS] tests/zephyr/data/test_cleaning_rule_engine.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
数据清洗规则引擎（CAND-DAT-007 / B10-01347）。

min_build_spec 对齐（深挖裁定=做 P0）：
  规则DSL + 阈值滚动分位自进化（上下护栏 + 超限人工审批）接入 quality_gate 并输出拦截报告。

设计要点：
  - 规则 DSL：dict 声明（可 YAML 承载），op ∈ {gt, lt, between, rolling_quantile}，
    action ∈ {flag(打标 quality_flag=0 保留) | block(拦截剔除)}；
  - 滚动分位阈值 RollingQuantileThreshold：按窗口观测值重算分位数，
    候选阈值落在 [guard_lower, guard_upper] 护栏内自动生效（adopted），
    超限挂起（pending_approval）保留旧阈值，approve() 人工审批后生效；
  - run_quality_gate(engine, table, rows)：输出形态对齐
    gov_enforcement.rule_enforcement.quality_gate.apply_quality_gate
    （返回 (rows, stats)），stats 增列 intercepted/by_rule/pending_approvals 拦截报告。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: specs 参数
#   fields: 参数 specs，类型注解 list[dict[str, Any]]
#   code: cleaning_rule_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: engine 参数
#   fields: 参数 engine，类型注解 CleaningRuleEngine
#   code: cleaning_rule_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: table 参数
#   fields: 参数 table，类型注解 str
#   code: cleaning_rule_engine.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: rows 参数
#   fields: 参数 rows，类型注解 list[dict[str, Any]]
#   code: cleaning_rule_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RollingQuantileThreshold
#   name_en: RollingQuantileThreshold
#   intro: 滚动分位阈值：窗口观测重算，护栏内自动生效，超限挂起待人工审批。
#   desc: 滚动分位阈值：窗口观测重算，护栏内自动生效，超限挂起待人工审批。 Args: quantile: 分位点（如 0.99 表示取窗口 99% 分位为阈值） window: 滚动窗口…；公共方法（定义序）: current…
#   inputs: quantile window guard_lower guard_upper seed
#   outputs: 返回值
# - id: A2
#   name_zh: ② CleaningRule
#   name_en: CleaningRule
#   intro: 单条清洗规则（DSL 解析产物）。
#   desc: 单条清洗规则（DSL 解析产物）。 op 语义（violation 判定）： gt: value > rule.value → 违规（上限） lt: value < rule.v…；公共方法（定义序）: is_viol…
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ parse_rules
#   name_en: parse_rules
#   intro: 解析 DSL（dict 列表）为 CleaningRule 列表。
#   desc: 解析 DSL（dict 列表）为 CleaningRule 列表。 Raises: CleaningRuleError: op 非法 / 必填字段缺失 / action 非法；源码 L298-L340
#   inputs: specs
#   outputs: list[CleaningRule]
# - id: A4
#   name_zh: ④ CleaningRuleEngine
#   name_en: CleaningRuleEngine
#   intro: 清洗规则引擎：对 dict 记录逐行判定，flag 打标 / block 拦截。
#   desc: 清洗规则引擎：对 dict 记录逐行判定，flag 打标 / block 拦截。 Usage: engine = CleaningRuleEngine(parse_rules([…；公共方法（定义序）: evaluat…
#   inputs: rules
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ run_quality_gate
#   name_en: run_quality_gate
#   intro: 对批量记录执行清洗规则门控，输出拦截报告。
#   desc: 对批量记录执行清洗规则门控，输出拦截报告。 对齐 gov_enforcement.rule_enforcement.quality_gate.apply_quality_gate…；源码 L461-L494
#   inputs: engine table rows
#   outputs: tuple[list[dict[str, Any]], dict[str, A…
# - id: A6
#   name_zh: ⑥ main
#   name_en: main
#   intro: 入口——待实现。
#   desc: 入口——待实现。；源码 L497-L498
#   inputs: 无参数
#   outputs: 返回值
#   （注：A6 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[CleaningRule]
#   name_en: list[CleaningRule]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.ch_writer
# - id: O2
#   name_zh: tuple[list[dict[str, Any]], dict[str, A…
#   name_en: tuple[list[dict[str, Any]], dict[str, A…
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.ch_writer
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Iterable

log = logging.getLogger(__name__)

__all__ = [
    "CleaningRule",
    "CleaningRuleEngine",
    "CleaningRuleError",
    "InterceptionReport",
    "RollingQuantileThreshold",
    "parse_rules",
    "run_quality_gate",
]


class CleaningRuleError(Exception):
    """清洗规则 DSL 非法或引擎使用错误。"""


_OP_GT = "gt"
_OP_LT = "lt"
_OP_BETWEEN = "between"
_OP_ROLLING_QUANTILE = "rolling_quantile"
_VALID_OPS = (_OP_GT, _OP_LT, _OP_BETWEEN, _OP_ROLLING_QUANTILE)
_ACTION_FLAG = "flag"
_ACTION_BLOCK = "block"
_VALID_ACTIONS = (_ACTION_FLAG, _ACTION_BLOCK)


# ---------------------------------------------------------------------------
# 滚动分位阈值（自进化 + 护栏 + 人工审批）
# ---------------------------------------------------------------------------


def _quantile(values: list[float], q: float) -> float:
    """线性插值分位数（与 numpy 默认 linear 口径一致的最小实现）。"""
    if not values:
        raise CleaningRuleError("空序列无法计算分位数")
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    frac = pos - lo
    return xs[lo] + (xs[hi] - xs[lo]) * frac


class RollingQuantileThreshold:
    """滚动分位阈值：窗口观测重算，护栏内自动生效，超限挂起待人工审批。

    Args:
        quantile: 分位点（如 0.99 表示取窗口 99% 分位为阈值）
        window: 滚动窗口容量（保留最近 window 个观测）
        guard_lower / guard_upper: 阈值允许区间（上下护栏）
        seed: 初始观测（决定首个生效阈值）
    """

    def __init__(
        self,
        quantile: float,
        window: int,
        guard_lower: float,
        guard_upper: float,
        seed: Iterable[float] | None = None,
    ) -> None:
        if not 0 < quantile <= 1:
            raise CleaningRuleError(f"quantile 必须在 (0,1]: {quantile}")
        if window < 1:
            raise CleaningRuleError(f"window 必须 >= 1: {window}")
        if guard_lower > guard_upper:
            raise CleaningRuleError("guard_lower 不得大于 guard_upper")
        self.quantile = float(quantile)
        self.window = int(window)
        self.guard_lower = float(guard_lower)
        self.guard_upper = float(guard_upper)
        self._observations: list[float] = []
        self._current: float | None = None
        self._pending: float | None = None
        if seed:
            self._observations = [float(v) for v in seed][-self.window :]
            self._current = _quantile(self._observations, self.quantile)

    @property
    def current(self) -> float | None:
        """当前生效阈值（None=尚无观测，判定一律放行）。"""
        return self._current

    @property
    def pending(self) -> float | None:
        """挂起待审批的候选阈值。"""
        return self._pending

    def observe(self, values: Iterable[float]) -> str:
        """喂入新观测并重算候选阈值。

        Returns:
            "adopted"（护栏内自动生效）或 "pending_approval"（超限挂起，旧阈值保留）
        """
        self._observations.extend(float(v) for v in values)
        self._observations = self._observations[-self.window :]
        candidate = _quantile(self._observations, self.quantile)
        if self.guard_lower <= candidate <= self.guard_upper:
            self._current = candidate
            self._pending = None
            return "adopted"
        self._pending = candidate
        log.warning(
            "滚动分位阈值候选 %.4f 超出护栏 [%.4f, %.4f]，挂起待人工审批（旧阈值 %s 保留）",
            candidate,
            self.guard_lower,
            self.guard_upper,
            self._current,
        )
        return "pending_approval"

    def approve(self) -> None:
        """人工审批通过：挂起候选阈值生效。"""
        if self._pending is not None:
            self._current = self._pending
            self._pending = None

    def is_violation(self, value: float) -> bool:
        """判定值是否超过当前生效阈值；无阈值时保守放行。"""
        if self._current is None:
            return False
        return float(value) > self._current


# ---------------------------------------------------------------------------
# 规则 DSL
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CleaningRule:
    """单条清洗规则（DSL 解析产物）。

    op 语义（violation 判定）：
        gt:               value > rule.value       → 违规（上限）
        lt:               value < rule.value       → 违规（下限）
        between:          value ∉ [lower, upper]   → 违规（区间外）
        rolling_quantile: value > 滚动分位阈值      → 违规（阈值自进化）
    action: flag=打标 quality_flag=0 保留行；block=拦截剔除行。
    """

    name: str
    field: str
    op: str
    action: str = _ACTION_FLAG
    value: float | None = None
    lower: float | None = None
    upper: float | None = None
    quantile: float | None = None
    window: int | None = None
    guard_lower: float | None = None
    guard_upper: float | None = None
    seed: tuple[float, ...] = field(default_factory=tuple)

    def is_violation(self, v: float, threshold: RollingQuantileThreshold | None) -> bool:
        if self.op == _OP_GT:
            return v <= float(self.value)
        if self.op == _OP_LT:
            return v >= float(self.value)
        if self.op == _OP_BETWEEN:
            return v < float(self.lower) or v > float(self.upper)
        if self.op == _OP_ROLLING_QUANTILE:
            if threshold is None:
                return False
            return threshold.is_violation(v)
        raise CleaningRuleError(f"未知 op: {self.op!r}")


def parse_rules(specs: list[dict[str, Any]]) -> list[CleaningRule]:
    """解析 DSL（dict 列表）为 CleaningRule 列表。

    Raises:
        CleaningRuleError: op 非法 / 必填字段缺失 / action 非法
    """
    rules: list[CleaningRule] = []
    for spec in specs:
        name = spec.get("name")
        fld = spec.get("field")
        op = spec.get("op")
        if not name or not fld:
            raise CleaningRuleError(f"规则缺 name/field: {spec!r}")
        if op not in _VALID_OPS:
            raise CleaningRuleError(f"规则 {name!r} op 非法: {op!r}（合法: {_VALID_OPS}）")
        action = spec.get("action", _ACTION_FLAG)
        if action not in _VALID_ACTIONS:
            raise CleaningRuleError(f"规则 {name!r} action 非法: {action!r}")
        if op in (_OP_GT, _OP_LT) and spec.get("value") is None:
            raise CleaningRuleError(f"规则 {name!r} 缺 value")
        if op == _OP_BETWEEN and (spec.get("lower") is None or spec.get("upper") is None):
            raise CleaningRuleError(f"规则 {name!r} 缺 lower/upper")
        if op == _OP_ROLLING_QUANTILE:
            for req in ("quantile", "window", "guard_lower", "guard_upper"):
                if spec.get(req) is None:
                    raise CleaningRuleError(f"规则 {name!r} 缺 {req}")
        rules.append(
            CleaningRule(
                name=name,
                field=fld,
                op=op,
                action=action,
                value=spec.get("value"),
                lower=spec.get("lower"),
                upper=spec.get("upper"),
                quantile=spec.get("quantile"),
                window=spec.get("window"),
                guard_lower=spec.get("guard_lower"),
                guard_upper=spec.get("guard_upper"),
                seed=tuple(float(v) for v in spec.get("seed", ())),
            )
        )
    return rules


# ---------------------------------------------------------------------------
# 拦截报告 + 引擎
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InterceptionReport:
    """一批记录的清洗拦截报告。"""

    total: int
    flagged: int
    intercepted: int
    by_rule: dict[str, int]
    pending_approvals: tuple[str, ...] = ()


class CleaningRuleEngine:
    """清洗规则引擎：对 dict 记录逐行判定，flag 打标 / block 拦截。

    Usage:
        engine = CleaningRuleEngine(parse_rules([...]))
        report = engine.evaluate(rows)          # 打标+统计
        clean = engine.clean_rows(rows)         # 剔除被拦截行
        pending = engine.observe("volume", xs)  # 滚动阈值自进化
        engine.approve("vol_rq")                # 人工审批超限阈值
    """

    def __init__(self, rules: list[CleaningRule]) -> None:
        self.rules = list(rules)
        self._thresholds: dict[str, RollingQuantileThreshold] = {}
        for r in self.rules:
            if r.op == _OP_ROLLING_QUANTILE:
                self._thresholds[r.name] = RollingQuantileThreshold(
                    quantile=float(r.quantile),
                    window=int(r.window),
                    guard_lower=float(r.guard_lower),
                    guard_upper=float(r.guard_upper),
                    seed=r.seed,
                )

    def _violations(self, record: dict[str, Any]) -> list[CleaningRule]:
        hits: list[CleaningRule] = []
        for rule in self.rules:
            raw = record.get(rule.field)
            if raw is None:
                continue
            try:
                v = float(raw)
            except (TypeError, ValueError):
                continue  # 数值不可比→该行该规则跳过（不误伤）
            if rule.is_violation(v, self._thresholds.get(rule.name)):
                hits.append(rule)
        return hits

    def evaluate(self, records: list[dict[str, Any]]) -> InterceptionReport:
        """逐行判定：flag 规则命中 → 行置 quality_flag=0；block 命中 → 计入拦截。"""
        flagged = 0
        intercepted = 0
        by_rule: dict[str, int] = {r.name: 0 for r in self.rules}
        for rec in records:
            hits = self._violations(rec)
            if not hits:
                continue
            for h in hits:
                by_rule[h.name] += 1
            if any(h.action == _ACTION_BLOCK for h in hits):
                intercepted += 1
            else:
                rec["quality_flag"] = 0
                flagged += 1
        return InterceptionReport(
            total=len(records),
            flagged=flagged,
            intercepted=intercepted,
            by_rule={k: v for k, v in by_rule.items() if v},
            pending_approvals=self.pending_rules(),
        )

    def clean_rows(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """返回剔除 block 命中行后的记录（flag 行打标保留）。"""
        kept: list[dict[str, Any]] = []
        for rec in records:
            hits = self._violations(rec)
            if any(h.action == _ACTION_BLOCK for h in hits):
                continue
            if hits:
                rec["quality_flag"] = 0
            kept.append(rec)
        return kept

    def observe(self, field_name: str, values: Iterable[float]) -> list[str]:
        """对挂接 field_name 的滚动规则喂观测，返回进入待审批的规则名。"""
        pending: list[str] = []
        for rule in self.rules:
            if rule.op != _OP_ROLLING_QUANTILE or rule.field != field_name:
                continue
            outcome = self._thresholds[rule.name].observe(values)
            if outcome == "pending_approval":
                pending.append(rule.name)
        return pending

    def approve(self, rule_name: str) -> None:
        """人工审批：指定规则的挂起阈值生效。"""
        threshold = self._thresholds.get(rule_name)
        if threshold is None:
            raise CleaningRuleError(f"无滚动规则 {rule_name!r}")
        threshold.approve()

    def pending_rules(self) -> tuple[str, ...]:
        """当前处于待审批状态的规则名。"""
        return tuple(n for n, t in self._thresholds.items() if t.pending is not None)


# ---------------------------------------------------------------------------
# quality_gate 集成（输出形态对齐 apply_quality_gate）
# ---------------------------------------------------------------------------


def run_quality_gate(
    engine: CleaningRuleEngine,
    table: str,
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """对批量记录执行清洗规则门控，输出拦截报告。

    对齐 gov_enforcement.rule_enforcement.quality_gate.apply_quality_gate 的
    (rows, stats) 返回形态：flag 行 quality_flag=0 保留（审计留痕），
    block 行剔除；stats 增列 intercepted/by_rule/pending_approvals。

    Returns:
        (clean_rows, stats): stats = {table, total, flagged, intercepted, by_rule, pending_approvals}
    """
    report = engine.evaluate(rows)
    clean = engine.clean_rows(rows)
    stats: dict[str, Any] = {
        "table": table,
        "total": report.total,
        "flagged": report.flagged,
        "intercepted": report.intercepted,
        "by_rule": report.by_rule,
        "pending_approvals": list(report.pending_approvals),
    }
    if report.flagged or report.intercepted:
        log.info(
            "run_quality_gate(%s): flagged=%d intercepted=%d by_rule=%s pending=%s",
            table,
            report.flagged,
            report.intercepted,
            report.by_rule,
            stats["pending_approvals"],
        )
    return clean, stats


def main() -> None:
    """入口——待实现。"""


if __name__ == "__main__":
    main()
