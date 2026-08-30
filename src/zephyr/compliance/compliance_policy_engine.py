# [BLUEPRINT] MOD-CMP-015 | docs/03_modules/_domain_compliance/compliance_policy_engine/blueprint.md
# [MODULE] zephyr.compliance.compliance_policy_engine
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] 无（协议核心纯内存；clock/replayer/时段判定 全注入；PyYAML 仅解析 YAML 文本时惰性引用）
# [CONSUMERS] 运行时装配批（规则库版本装配 / 回放器与时段判定统一注入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 规则schema闭合(version+rules[rule_id/condition/action/severity]); 条件DSL仅 and/or 与比较算子; 变更未经人工审批不生效(PENDING→approve/reject); 回放比对不通过拒绝激活; 热加载仅非交易时段(注入判定); 求值确定性按rule_id排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_compliance/compliance_policy_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CompliancePolicyError(占位 ZA-CMP-UNREGISTERED-COMPLIANCE-POLICY)——schema非法/条件语法非法/未知变更/重复审批/回放不通过/交易时段热加载时抛
# [TESTS] tests/compliance/test_compliance_policy_engine.py
# [A_module] module_id=MOD-CMP-015 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
CompliancePolicyEngine — 合规策略即代码引擎（MOD-CMP-015）。

B14-04651（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-CMP-006，A9 D-COMPLIANCE-16）：
合规规则**声明式 DSL**（YAML 规则 schema：条件/动作/严重度）+ **版本管理** +
**规则回放验证**（历史交易重放比对，回放器注入）+ **非交易时段热加载**
（时段判定注入）+ 变更**人工审批队列**。OPA/Rego 思想轻量版。

设计要点：
- **纯内存/DI**：时钟、回放器、非交易时段判定全部注入；不读盘不触网
  （YAML 文本由调用方读入后以参数传入，或直供已解析 Mapping）。
- **Fail-Closed**：schema 缺键/条件语法非法/action、severity 越词表/未知
  变更单/重复审批/回放比对不通过/交易时段热加载一律抛 CompliancePolicyError。
- **确定性**：条件求值为纯函数（and/or + 比较算子，无函数调用无命名空
  间逃逸）；求值结果按 rule_id 排序；同输入必同输出。

查重分工：compliance_rule_engine=既有规则执行族（无版本管理/审批队列/
回放验证语义）；governance 合规门=治理裁决（零交集）。本件=策略即代码的
声明、版本化与安全激活层。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: condition 参数
#   fields: 参数 condition，类型注解 str
#   code: compliance_policy_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: context 参数
#   fields: 参数 context，类型注解 Mapping
#   code: compliance_policy_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① evaluate_condition
#   name_en: evaluate_condition
#   intro: 条件求值：or 分段 → and 分段 → 单子句（纯函数，确定性）。
#   desc: 条件求值：or 分段 → and 分段 → 单子句（纯函数，确定性）。；源码 L244-L251
#   inputs: condition context
#   outputs: bool
# - id: A2
#   name_zh: ② CompliancePolicyEngine
#   name_en: CompliancePolicyEngine
#   intro: 合规策略即代码引擎（DSL + 版本管理 + 回放验证 + 审批队列 + 热加载门禁）。
#   desc: 合规策略即代码引擎（DSL + 版本管理 + 回放验证 + 审批队列 + 热加载门禁）。 Args: clock: 时钟注入。 replayer: 回放器注入（old_rules…；公共方法（定义序）: submit_…
#   inputs: clock replayer is_non_trading_time
#   outputs: 返回值
#   （注：A2 之后另有 8 个公共定义未列入（含 8 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 运行时装配批（规则库版本装配 / 回放器与时段判定统一注入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import datetime
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "ChangeStatus",
    "CompliancePolicyError",
    "CompliancePolicyEngine",
    "PolicyAction",
    "PolicyChange",
    "PolicyDecision",
    "PolicyRule",
    "ReplayReport",
    "Severity",
]


class CompliancePolicyError(Exception):
    """合规策略输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-CMP-UNREGISTERED-COMPLIANCE-POLICY。
    """


class PolicyAction(str, Enum):
    """规则动作（词表闭合）。"""

    BLOCK = "block"  # 拦截
    ALERT = "alert"  # 告警
    RECORD = "record"  # 留痕


class Severity(str, Enum):
    """严重度（词表闭合）。"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ChangeStatus(str, Enum):
    """变更审批状态机。"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class PolicyRule:
    """合规规则（条件/动作/严重度三要素，frozen）。"""

    rule_id: str
    condition: str
    action: PolicyAction
    severity: Severity
    description: str = ""


@dataclass(frozen=True)
class PolicyDecision:
    """规则命中裁决（求值输出）。"""

    rule_id: str
    action: PolicyAction
    severity: Severity
    condition: str


@dataclass(frozen=True)
class ReplayReport:
    """回放比对报告（回放器注入返回载体）。"""

    matched: bool  # 历史重放新旧规则结果是否一致（或符合预期）
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PolicyChange:
    """人工审批队列条目（frozen）。"""

    change_id: str
    version: str
    rules: tuple[PolicyRule, ...]
    status: ChangeStatus
    submitted_at: datetime.datetime


# ── 条件 DSL（确定性纯函数求值）────────────────────────────────────────────

_CLAUSE_RE: Final = re.compile(
    r"^\s*(?P<field>[A-Za-z_][A-Za-z0-9_.]*)\s*"
    r"(?P<op>==|!=|>=|<=|>|<|in)\s*"
    r"(?P<literal>.+?)\s*$"
)


def _parse_literal(text: str) -> object:
    """字面量解析：数字/引号字符串/true|false/列表（in 右值）。"""
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_parse_literal(part.strip()) for part in inner.split(",")]
    if (text.startswith("'") and text.endswith("'")) or (text.startswith('"') and text.endswith('"')):
        return text[1:-1]
    if text in ("true", "false"):
        return text == "true"
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    raise CompliancePolicyError(f"条件字面量非法: {text!r}")


def _eval_clause(clause: str, context: Mapping) -> bool:
    match = _CLAUSE_RE.match(clause)
    if match is None:
        raise CompliancePolicyError(f"条件子句语法非法: {clause!r}")
    field_name = match.group("field")
    if field_name not in context:
        raise CompliancePolicyError(f"条件字段缺失: {field_name!r}（Fail-Closed）")
    actual = context[field_name]
    op = match.group("op")
    expect = _parse_literal(match.group("literal"))
    if op == "in":
        if not isinstance(expect, list):
            raise CompliancePolicyError(f"in 右值须为列表: {clause!r}")
        return actual in expect
    if isinstance(expect, list):
        raise CompliancePolicyError(f"比较算子右值不可为列表: {clause!r}")
    try:
        if op == "==":
            return actual == expect
        if op == "!=":
            return actual != expect
        if op == ">=":
            return actual >= expect
        if op == "<=":
            return actual <= expect
        if op == ">":
            return actual > expect
        if op == "<":
            return actual < expect
    except TypeError as exc:
        raise CompliancePolicyError(f"条件比较类型不符: {clause!r} ({exc})") from exc
    raise CompliancePolicyError(f"未知算子: {op!r}")


def _split_top(condition: str, keyword: str) -> list[str]:
    """按顶层关键词切分（DSL 不支持括号嵌套，关键词两侧须为空格）。"""
    parts = condition.split(f" {keyword} ")
    return [part.strip() for part in parts]


def evaluate_condition(condition: str, context: Mapping) -> bool:
    """条件求值：or 分段 → and 分段 → 单子句（纯函数，确定性）。"""
    if not condition or not condition.strip():
        raise CompliancePolicyError("条件为空")
    for or_part in _split_top(condition, "or"):
        if all(_eval_clause(clause, context) for clause in _split_top(or_part, "and")):
            return True
    return False


def _validate_condition_syntax(condition: str) -> None:
    """注册期语法预检（用哨兵上下文跑通解析，字段缺失豁免）。"""
    if not condition or not condition.strip():
        raise CompliancePolicyError("条件为空")
    for or_part in _split_top(condition, "or"):
        for clause in _split_top(or_part, "and"):
            match = _CLAUSE_RE.match(clause)
            if match is None:
                raise CompliancePolicyError(f"条件子句语法非法: {clause!r}")
            _parse_literal(match.group("literal"))  # 字面量可解析
            if match.group("op") == "in" and not isinstance(_parse_literal(match.group("literal")), list):
                raise CompliancePolicyError(f"in 右值须为列表: {clause!r}")


# ── 引擎 ────────────────────────────────────────────────────────────────────

_RULE_REQUIRED_KEYS: Final[frozenset[str]] = frozenset({"rule_id", "condition", "action", "severity"})


class CompliancePolicyEngine:
    """合规策略即代码引擎（DSL + 版本管理 + 回放验证 + 审批队列 + 热加载门禁）。

    Args:
        clock: 时钟注入。
        replayer: 回放器注入（old_rules, new_rules) -> ReplayReport；
            None 时审批激活不做回放校验（由装配批决定是否强制注入）。
        is_non_trading_time: 非交易时段判定注入；None 时视为恒可热加载
            （测试/离线场景），注入 False 判定即门禁热加载。
    """

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        replayer: Callable[[tuple[PolicyRule, ...], tuple[PolicyRule, ...]], ReplayReport] | None = None,
        is_non_trading_time: Callable[[], bool] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._replayer = replayer
        self._is_non_trading_time = is_non_trading_time or (lambda: True)
        self._versions: dict[str, tuple[PolicyRule, ...]] = {}
        self._active_version: str | None = None
        self._changes: dict[str, PolicyChange] = {}

    # ── schema 解析 ───────────────────────────────────────────────────────

    @staticmethod
    def _load_payload(payload: str | Mapping) -> Mapping:
        if isinstance(payload, str):
            try:
                import yaml  # 惰性引用：仅解析 YAML 文本时需要
            except ImportError as exc:
                raise CompliancePolicyError("PyYAML 不可用（无法解析 YAML 文本）") from exc
            try:
                doc = yaml.safe_load(payload)
            except yaml.YAMLError as exc:
                raise CompliancePolicyError(f"YAML 解析失败: {exc}") from exc
        else:
            doc = payload
        if not isinstance(doc, Mapping):
            raise CompliancePolicyError("规则文档须为 Mapping（YAML 顶层 mapping）")
        return doc

    @classmethod
    def _parse_rules(cls, payload: str | Mapping) -> tuple[str, tuple[PolicyRule, ...]]:
        doc = cls._load_payload(payload)
        version = doc.get("version")
        if not isinstance(version, str) or not version:
            raise CompliancePolicyError("schema 非法: version 缺失或非字符串")
        raw_rules = doc.get("rules")
        if not isinstance(raw_rules, Sequence) or isinstance(raw_rules, (str, bytes)):
            raise CompliancePolicyError("schema 非法: rules 缺失或非列表")
        rules: list[PolicyRule] = []
        seen: set[str] = set()
        for idx, raw in enumerate(raw_rules):
            if not isinstance(raw, Mapping):
                raise CompliancePolicyError(f"rules[{idx}] 非 mapping")
            missing = _RULE_REQUIRED_KEYS - set(raw)
            if missing:
                raise CompliancePolicyError(f"rules[{idx}] 缺键: {sorted(missing)}")
            rule_id = raw["rule_id"]
            if not isinstance(rule_id, str) or not rule_id:
                raise CompliancePolicyError(f"rules[{idx}] rule_id 非法: {rule_id!r}")
            if rule_id in seen:
                raise CompliancePolicyError(f"rule_id 重复: {rule_id!r}")
            seen.add(rule_id)
            condition = raw["condition"]
            if not isinstance(condition, str):
                raise CompliancePolicyError(f"rules[{idx}] condition 非字符串")
            _validate_condition_syntax(condition)
            try:
                action = PolicyAction(raw["action"])
            except ValueError as exc:
                raise CompliancePolicyError(f"rules[{idx}] action 越词表: {raw['action']!r}") from exc
            try:
                severity = Severity(raw["severity"])
            except ValueError as exc:
                raise CompliancePolicyError(f"rules[{idx}] severity 越词表: {raw['severity']!r}") from exc
            description = raw.get("description", "")
            if not isinstance(description, str):
                raise CompliancePolicyError(f"rules[{idx}] description 非字符串")
            rules.append(
                PolicyRule(
                    rule_id=rule_id,
                    condition=condition,
                    action=action,
                    severity=severity,
                    description=description,
                )
            )
        return version, tuple(rules)

    # ── 人工审批队列 ──────────────────────────────────────────────────────

    def submit_change(self, change_id: str, payload: str | Mapping) -> PolicyChange:
        """提交规则集变更（解析校验 schema 后入 PENDING 队列，不生效）。"""
        if not change_id:
            raise CompliancePolicyError("change_id 为空")
        if change_id in self._changes:
            raise CompliancePolicyError(f"change_id 重复: {change_id!r}")
        version, rules = self._parse_rules(payload)
        change = PolicyChange(
            change_id=change_id,
            version=version,
            rules=rules,
            status=ChangeStatus.PENDING,
            submitted_at=self._clock(),
        )
        self._changes[change_id] = change
        _log.info("规则变更入审批队列: %s version=%s rules=%d", change_id, version, len(rules))
        return change

    def _change_of(self, change_id: str) -> PolicyChange:
        change = self._changes.get(change_id)
        if change is None:
            raise CompliancePolicyError(f"未知变更单: {change_id!r}")
        return change

    def approve_change(self, change_id: str) -> PolicyChange:
        """审批通过：回放验证（注入时）→ 非交易时段门禁 → 激活新版本。"""
        change = self._change_of(change_id)
        if change.status is not ChangeStatus.PENDING:
            raise CompliancePolicyError(f"非法审批: {change_id!r} 当前 {change.status.value}（重复审批/已拒绝）")
        if self._replayer is not None:
            old_rules = self._versions.get(self._active_version, ()) if self._active_version else ()
            report = self._replayer(tuple(old_rules), change.rules)
            if not isinstance(report, ReplayReport):
                raise CompliancePolicyError("回放器返回非法（须为 ReplayReport）")
            if not report.matched:
                raise CompliancePolicyError(f"回放验证不通过: {change_id!r} details={list(report.details)}")
        if not self._is_non_trading_time():
            raise CompliancePolicyError("当前为交易时段（热加载仅限非交易时段）")
        self._versions[change.version] = change.rules
        self._active_version = change.version
        approved = PolicyChange(
            change_id=change.change_id,
            version=change.version,
            rules=change.rules,
            status=ChangeStatus.APPROVED,
            submitted_at=change.submitted_at,
        )
        self._changes[change_id] = approved
        _log.info("规则版本激活: %s (%s)", change.version, change_id)
        return approved

    def reject_change(self, change_id: str) -> PolicyChange:
        """审批拒绝（仅 PENDING 可拒绝）。"""
        change = self._change_of(change_id)
        if change.status is not ChangeStatus.PENDING:
            raise CompliancePolicyError(f"非法拒绝: {change_id!r} 当前 {change.status.value}")
        rejected = PolicyChange(
            change_id=change.change_id,
            version=change.version,
            rules=change.rules,
            status=ChangeStatus.REJECTED,
            submitted_at=change.submitted_at,
        )
        self._changes[change_id] = rejected
        _log.info("规则变更拒绝: %s", change_id)
        return rejected

    # ── 求值 ─────────────────────────────────────────────────────────────

    def evaluate(self, context: Mapping) -> list[PolicyDecision]:
        """对上下文求值现行版本规则（命中集按 rule_id 确定性排序）。"""
        if not isinstance(context, Mapping):
            raise CompliancePolicyError("context 须为 Mapping")
        if self._active_version is None:
            raise CompliancePolicyError("无激活版本（规则库为空，Fail-Closed）")
        out: list[PolicyDecision] = []
        for rule in self._versions[self._active_version]:
            if evaluate_condition(rule.condition, context):
                out.append(
                    PolicyDecision(
                        rule_id=rule.rule_id,
                        action=rule.action,
                        severity=rule.severity,
                        condition=rule.condition,
                    )
                )
        out.sort(key=lambda d: d.rule_id)
        return out

    # ── 查询 ─────────────────────────────────────────────────────────────

    def active_version(self) -> str | None:
        """现行激活版本（未激活为 None）。"""
        return self._active_version

    def active_rules(self) -> tuple[PolicyRule, ...]:
        """现行规则集（未激活 Fail-Closed）。"""
        if self._active_version is None:
            raise CompliancePolicyError("无激活版本（规则库为空，Fail-Closed）")
        return self._versions[self._active_version]

    def pending_changes(self) -> list[PolicyChange]:
        """待审批队列（按 (submitted_at, change_id) 确定性排序）。"""
        out = [c for c in self._changes.values() if c.status is ChangeStatus.PENDING]
        out.sort(key=lambda c: (c.submitted_at, c.change_id))
        return out

    def change_status(self, change_id: str) -> ChangeStatus:
        """单变更单状态查询（未知 → Fail-Closed）。"""
        return self._change_of(change_id).status
