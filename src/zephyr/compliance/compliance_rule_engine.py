# [BLUEPRINT] MOD-CMP-012 | docs/03_modules/_domain_compliance/compliance_rule_engine/blueprint.md
# [MODULE] zephyr.compliance.compliance_rule_engine
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-EX-024(pre_execution_checker Pre-Trade 接线, 运行时装配批) ; MOD-CMP-010(compliance_log 命中留痕)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 版本历史不可变(重复版本拒绝); 评估错误Fail-Closed拒单(HARD_BLOCK+engine_error); 处置聚合HardBlock>SoftWarn>Warning>Pass; hit_sink异常不阻断判定; 规则frozen
# [MODIFY-GUARD] docs/03_modules/_domain_compliance/compliance_rule_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidComplianceRuleError
# [TESTS] tests/compliance/test_compliance_rule_engine.py
# [A_module] module_id=MOD-CMP-012 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""
ComplianceRuleEngine — §10.8.1.2 合规引擎 (MOD-CMP-012)

CAND-CMP-002（B5-07849）：DSL 规则解析器 + 规则版本管理器（不可变历史 +
当前活跃指针）+ 实时评估器（Pre-Trade 同步调用，Hard Block 拒单 /
Soft Warn 转人工 / Warning 放行）+ 盘后批量审计器。对标 OPA（DSL 规则解析 +
版本化）与 SEC 15c3-5 盘前自查门禁；执行前合规**自查型**（非报送型）。

命中经 ``hit_sink`` 回调落 compliance_log 契约 dict（MOD-CMP-010 持久化委托，
运行时装配批接线）并 T+1 归档（归档委托既有链路）。收编现有检测散件
（MOD-CMP-007 / discipline 双 checker）阈值语义为 DSL 规则包
``trading_compliance_rule_pack``——本引擎不重复实现其检测逻辑。

DSL 规则定义（dict）::

    {"rule_id": "R-001", "version": "v1", "description": "...",
     "severity": "hard_block" | "soft_warn" | "warning",
     "condition": {"field": "qty", "op": ">", "value": 100}
                 | {"field": "buyer_account", "op": "==", "value_from_field": "seller_account"}
                 | {"field": "order_qty", "op": ">", "value_from_field": "minute_avg_volume", "scale": 0.5}
                 | {"all": [cond, ...]} | {"any": [cond, ...]}}

op ∈ ``>, >=, <, <=, ==, !=, in``。解析期校验（InvalidComplianceRuleError）。
字段缺失等评估错误 → Fail-Closed：HARD_BLOCK + engine_error（检测引擎失效
拒发任何订单，对齐 MOD-CMP-007 不变量）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: manager 参数
#   fields: 参数 manager（无注解）
#   code: compliance_rule_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: hit_sink 参数
#   fields: 参数 hit_sink（无注解）
#   code: compliance_rule_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RuleDslParser
#   name_en: RuleDslParser
#   intro: DSL 规则解析器（解析期校验，Fail-Closed 拒绝坏规则）。
#   desc: DSL 规则解析器（解析期校验，Fail-Closed 拒绝坏规则）。；公共方法（定义序）: parse；源码 L202-L267
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② RuleVersionManager
#   name_en: RuleVersionManager
#   intro: 规则版本管理器：不可变历史 + 当前活跃指针。
#   desc: 规则版本管理器：不可变历史 + 当前活跃指针。；公共方法（定义序）: register, activate, deactivate, active, history, active_rules；源码 L270-L304
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ ComplianceRuleEngine
#   name_en: ComplianceRuleEngine
#   intro: 合规引擎：实时评估器（Pre-Trade 同步）+ 盘后批量审计器。
#   desc: 合规引擎：实时评估器（Pre-Trade 同步）+ 盘后批量审计器。 Args: manager: 版本管理器（None 自建新实例）。 hit_sink: 命中留痕回调（com…；公共方法（定义序）: manager…
#   inputs: manager hit_sink
#   outputs: 返回值
# - id: A4
#   name_zh: ④ trading_compliance_rule_pack
#   name_en: trading_compliance_rule_pack
#   intro: 收编现有检测散件阈值语义为 DSL 规则包（MOD-CMP-007 §7.2 MVP 初始值）。
#   desc: 收编现有检测散件阈值语义为 DSL 规则包（MOD-CMP-007 §7.2 MVP 初始值）。 仅表达阈值语义为 DSL 规则；散件检测逻辑本体不迁移不复制（收编渐进， 全量迁…；源码 L416-L437
#   inputs: 无参数
#   outputs: tuple[dict[str, Any], ...]
#   （注：A4 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: tuple[dict[str, Any], ...]
#   name_en: tuple[dict[str, Any], ...]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-EX-024(pre_execution_checker Pre-Trade 接线, 运行时装配批) ; MOD-CMP-010(compliance…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
import operator
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "BatchAuditReport",
    "ComplianceDisposition",
    "ComplianceRule",
    "ComplianceRuleEngine",
    "ComplianceVerdict",
    "InvalidComplianceRuleError",
    "RuleDslParser",
    "RuleHit",
    "RuleVersionManager",
    "trading_compliance_rule_pack",
]


class InvalidComplianceRuleError(ZephyrBaseError):
    """合规规则 DSL / 版本管理操作非法。"""


class ComplianceDisposition(str, Enum):
    """评估处置（严重度升序；聚合取最严）。取值与 DSL severity 字符串一致。"""

    PASS = "pass"  # 放行
    WARNING = "warning"  # 放行 + 记录
    SOFT_WARN = "soft_warn"  # 转人工审批
    HARD_BLOCK = "hard_block"  # 拒单


_SEVERITY_ORDER: Final[dict[ComplianceDisposition, int]] = {
    ComplianceDisposition.PASS: 0,
    ComplianceDisposition.WARNING: 1,
    ComplianceDisposition.SOFT_WARN: 2,
    ComplianceDisposition.HARD_BLOCK: 3,
}

_OPS: Final[dict[str, Callable[[Any, Any], bool]]] = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    "in": lambda a, b: a in b,
}

_COMPOSITE_KEYS: Final[frozenset[str]] = frozenset({"all", "any"})


@dataclass(frozen=True)
class ComplianceRule:
    """合规规则（不可变）。"""

    rule_id: str
    version: str
    description: str
    severity: ComplianceDisposition
    condition: dict[str, Any]


@dataclass(frozen=True)
class RuleHit:
    """单条规则命中（不可变）。"""

    rule_id: str
    version: str
    severity: ComplianceDisposition
    description: str


@dataclass(frozen=True)
class ComplianceVerdict:
    """Pre-Trade 评估结论（不可变）。"""

    disposition: ComplianceDisposition
    hits: tuple[RuleHit, ...]
    engine_error: str | None = None


@dataclass(frozen=True)
class BatchAuditReport:
    """盘后批量审计报告（不可变）。"""

    total: int
    hard_block: int
    soft_warn: int
    warning: int
    passed: int
    verdicts: tuple[ComplianceVerdict, ...]


class RuleDslParser:
    """DSL 规则解析器（解析期校验，Fail-Closed 拒绝坏规则）。"""

    @staticmethod
    def parse(definition: Mapping[str, Any]) -> ComplianceRule:
        if not isinstance(definition, Mapping):
            raise InvalidComplianceRuleError(f"规则定义必须为 mapping: {type(definition)!r}")
        rule_id = definition.get("rule_id")
        version = definition.get("version")
        description = definition.get("description", "")
        severity_raw = definition.get("severity")
        condition = definition.get("condition")
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise InvalidComplianceRuleError(f"rule_id 缺失或为空: {rule_id!r}")
        if not isinstance(version, str) or not version.strip():
            raise InvalidComplianceRuleError(f"version 缺失或为空: {version!r}")
        try:
            severity = ComplianceDisposition(severity_raw)
        except ValueError as exc:
            raise InvalidComplianceRuleError(f"severity 非法: {severity_raw!r}") from exc
        if severity is ComplianceDisposition.PASS:
            raise InvalidComplianceRuleError("severity 不允许为 PASS（PASS 是聚合兜底非规则档）")
        RuleDslParser._validate_condition(condition)
        return ComplianceRule(
            rule_id=rule_id.strip(),
            version=version.strip(),
            description=str(description),
            severity=severity,
            condition=dict(condition),
        )

    @staticmethod
    def _validate_condition(cond: Any) -> None:
        if not isinstance(cond, Mapping):
            raise InvalidComplianceRuleError(f"condition 必须为 mapping: {cond!r}")
        keys = set(cond.keys())
        if "field" in keys and "op" in keys:
            extra = keys - {"field", "op", "value", "value_from_field", "scale"}
            if extra:
                raise InvalidComplianceRuleError(f"原子条件含未知键: {sorted(extra)}")
            has_value = "value" in keys
            has_ref = "value_from_field" in keys
            if has_value == has_ref:
                raise InvalidComplianceRuleError("原子条件须且仅须含 value 或 value_from_field 之一")
            if not isinstance(cond["field"], str) or not cond["field"].strip():
                raise InvalidComplianceRuleError(f"condition.field 必须为非空字符串: {cond['field']!r}")
            if cond["op"] not in _OPS:
                raise InvalidComplianceRuleError(f"condition.op 非法: {cond['op']!r}（合法: {sorted(_OPS)}）")
            if has_ref and not isinstance(cond["value_from_field"], str):
                raise InvalidComplianceRuleError(f"value_from_field 必须为字符串: {cond['value_from_field']!r}")
            if "scale" in keys:
                if not has_ref:
                    raise InvalidComplianceRuleError("scale 仅可与 value_from_field 联用")
                if not isinstance(cond["scale"], (int, float)) or cond["scale"] <= 0:
                    raise InvalidComplianceRuleError(f"scale 必须为正数: {cond['scale']!r}")
            return
        if len(keys) == 1 and keys <= _COMPOSITE_KEYS:
            children = next(iter(cond.values()))
            if not isinstance(children, (list, tuple)) or not children:
                raise InvalidComplianceRuleError(f"复合条件 {keys} 必须为非空列表: {children!r}")
            for child in children:
                RuleDslParser._validate_condition(child)
            return
        raise InvalidComplianceRuleError(
            f"condition 形状非法: {sorted(keys)}（原子须为 field/op/(value|value_from_field)，复合须单键 all/any）"
        )


class RuleVersionManager:
    """规则版本管理器：不可变历史 + 当前活跃指针。"""

    def __init__(self) -> None:
        self._history: dict[str, dict[str, ComplianceRule]] = {}
        self._active: dict[str, str] = {}

    def register(self, rule: ComplianceRule) -> None:
        """注册新版本；同 rule_id+version 重复写拒绝（历史不可变）。"""
        versions = self._history.setdefault(rule.rule_id, {})
        if rule.version in versions:
            raise InvalidComplianceRuleError(f"规则版本已存在，历史不可变拒绝重复写: {rule.rule_id}@{rule.version}")
        versions[rule.version] = rule

    def activate(self, rule_id: str, version: str) -> None:
        """活跃指针切换；目标版本须已注册。"""
        if version not in self._history.get(rule_id, {}):
            raise InvalidComplianceRuleError(f"激活目标版本未注册: {rule_id}@{version}")
        self._active[rule_id] = version

    def deactivate(self, rule_id: str) -> None:
        """摘除活跃指针（历史保留）。"""
        self._active.pop(rule_id, None)

    def active(self, rule_id: str) -> ComplianceRule | None:
        version = self._active.get(rule_id)
        if version is None:
            return None
        return self._history[rule_id][version]

    def history(self, rule_id: str) -> tuple[ComplianceRule, ...]:
        return tuple(self._history.get(rule_id, {}).values())

    def active_rules(self) -> tuple[ComplianceRule, ...]:
        return tuple(self._history[rid][ver] for rid, ver in self._active.items())


class ComplianceRuleEngine:
    """合规引擎：实时评估器（Pre-Trade 同步）+ 盘后批量审计器。

    Args:
        manager: 版本管理器（None 自建新实例）。
        hit_sink: 命中留痕回调（compliance_log 契约 dict）；异常不阻断判定。
    """

    def __init__(
        self,
        manager: RuleVersionManager | None = None,
        hit_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._manager = manager or RuleVersionManager()
        self._hit_sink = hit_sink

    @property
    def manager(self) -> RuleVersionManager:
        return self._manager

    def load_rule_pack(self, pack: Iterable[Mapping[str, Any]], *, activate: bool = True) -> int:
        """加载规则包：解析+注册（默认同时把活跃指针指向所给版本）。返回加载条数。"""
        count = 0
        for definition in pack:
            rule = RuleDslParser.parse(definition)
            self._manager.register(rule)
            if activate:
                self._manager.activate(rule.rule_id, rule.version)
            count += 1
        return count

    def evaluate_pre_trade(self, context: Mapping[str, Any]) -> ComplianceVerdict:
        """Pre-Trade 同步评估（判定核心无 IO；评估错误 Fail-Closed 拒单）。"""
        hits: list[RuleHit] = []
        try:
            for rule in self._manager.active_rules():
                if _eval_condition(rule.condition, context):
                    hits.append(
                        RuleHit(
                            rule_id=rule.rule_id,
                            version=rule.version,
                            severity=rule.severity,
                            description=rule.description,
                        )
                    )
        except Exception as exc:  # noqa: BLE001 — 评估错误 Fail-Closed（字段缺失/类型异常等）
            return ComplianceVerdict(
                disposition=ComplianceDisposition.HARD_BLOCK,
                hits=(),
                engine_error=f"评估引擎错误，Fail-Closed 拒单: {exc}",
            )
        disposition = ComplianceDisposition.PASS
        for hit in hits:
            if _SEVERITY_ORDER[hit.severity] > _SEVERITY_ORDER[disposition]:
                disposition = hit.severity
        verdict = ComplianceVerdict(disposition=disposition, hits=tuple(hits))
        for hit in hits:
            self._emit_hit(hit, context)
        return verdict

    def evaluate_batch(self, contexts: Iterable[Mapping[str, Any]]) -> BatchAuditReport:
        """盘后批量审计器：逐条 Pre-Trade 同款判定并聚合统计。"""
        verdicts = tuple(self.evaluate_pre_trade(ctx) for ctx in contexts)
        return BatchAuditReport(
            total=len(verdicts),
            hard_block=sum(1 for v in verdicts if v.disposition is ComplianceDisposition.HARD_BLOCK),
            soft_warn=sum(1 for v in verdicts if v.disposition is ComplianceDisposition.SOFT_WARN),
            warning=sum(1 for v in verdicts if v.disposition is ComplianceDisposition.WARNING),
            passed=sum(1 for v in verdicts if v.disposition is ComplianceDisposition.PASS),
            verdicts=verdicts,
        )

    def _emit_hit(self, hit: RuleHit, context: Mapping[str, Any]) -> None:
        if self._hit_sink is None:
            return
        record = {
            "event_type": "RULE_ENGINE_HIT",
            "source": "compliance_rule_engine",
            "rule_id": hit.rule_id,
            "version": hit.version,
            "severity": hit.severity.value,
            "description": hit.description,
            "context": dict(context),
        }
        try:
            self._hit_sink(record)
        except Exception:  # noqa: BLE001 — sink 异常不阻断判定（留痕降级）
            _logger.exception("hit_sink 异常（已降级，判定不受影响）")


def _eval_condition(cond: Mapping[str, Any], context: Mapping[str, Any]) -> bool:
    keys = set(cond.keys())
    if "field" in keys and "op" in keys:
        field = cond["field"]
        if field not in context:
            raise KeyError(f"context 缺字段: {field}")
        if "value_from_field" in cond:
            ref = cond["value_from_field"]
            if ref not in context:
                raise KeyError(f"context 缺字段: {ref}")
            target = context[ref] * cond.get("scale", 1)
        else:
            target = cond["value"]
        return bool(_OPS[cond["op"]](context[field], target))
    if "all" in cond:
        return all(_eval_condition(c, context) for c in cond["all"])
    return any(_eval_condition(c, context) for c in cond["any"])


def trading_compliance_rule_pack() -> tuple[dict[str, Any], ...]:
    """收编现有检测散件阈值语义为 DSL 规则包（MOD-CMP-007 §7.2 MVP 初始值）。

    仅表达阈值语义为 DSL 规则；散件检测逻辑本体不迁移不复制（收编渐进，
    全量迁移留运行时装配批）。
    """
    return (
        {
            "rule_id": "CMP-WASH-TRADE",
            "version": "v1",
            "description": "自成交（买卖双方同账户）零容忍（收编 MOD-CMP-007 WASH_TRADE）",
            "severity": "hard_block",
            "condition": {"field": "buyer_account", "op": "==", "value_from_field": "seller_account"},
        },
        {
            "rule_id": "CMP-LARGE-TRADE",
            "version": "v1",
            "description": "单笔 > 该标的分钟均量 50%（收编 MOD-CMP-007 LARGE_TRADE MVP 初始值）",
            "severity": "hard_block",
            "condition": {"field": "order_qty", "op": ">", "value_from_field": "minute_avg_volume", "scale": 0.5},
        },
    )
