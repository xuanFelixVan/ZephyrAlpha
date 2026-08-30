# [BLUEPRINT] MOD-CMP-003 | docs/03_modules/MOD-CMP-003/
# [MODULE] zephyr.compliance.compliance_tech_enabler
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.shared.contracts.compliance_rule; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-L10-001(ComplianceEngine 规则装载) ; MOD-CMP-004(合规持续运营 规则新鲜度核查)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] enforcement_action∈{block,warn,log}且severity∈{critical,high,medium,low}未知值一律拒绝(不静默降级,Fail-Closed); 必填字段缺失/重复rule_id/非映射条目→记入rejected不混入生效集; 输出按severity降序(critical>high>medium>low,对齐ComplianceEngine契约); 定义源失败→ComplianceEnablementError上抛(调用方按零规则阻断处理)
# [MODIFY-GUARD] docs/03_modules/MOD-CMP-003/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ComplianceEnablementError
# [TESTS] tests/compliance/test_compliance_tech_enabler.py
# [A_module] module_id=MOD-CMP-003 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Compliance Tech Enabler — 合规技术使能器 (MOD-CMP-003)

把声明式合规规则定义（配置/注册表载荷，Mapping 序列）物化为 CTR-P1-012
ComplianceRule 生效规则集，供 ComplianceEngine（MOD-L10-001 OCP 扩展点）装载。

使能边界（只使能不重造）：
  - 规则定义源经 definition_source 协议注入（生产接线: 合规规则配置/注册表查询）
  - 物化核心 materialize_compliance_rules 为纯函数（同输入必同输出，可单测）
  - 枚举未知值/必填缺失/重复 rule_id → rejected 结构化留痕（Fail-Closed，
    绝不把无法识别的 enforcement_action 静默降级为 log/warn）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: definitions 参数
#   fields: 参数 definitions，类型注解 Iterable[Mapping[str, Any]]
#   code: compliance_tech_enabler.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: now 参数
#   fields: 参数 now（无注解）
#   code: compliance_tech_enabler.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① materialize_compliance_rules
#   name_en: materialize_compliance_rules
#   intro: 声明式规则定义 → ComplianceRule 生效集（纯函数）。
#   desc: 声明式规则定义 → ComplianceRule 生效集（纯函数）。 拒绝路径（Fail-Closed，全部留痕不静默）： - 非 Mapping 条目 / 必填字段缺失 / 空…；源码 L164-L212
#   inputs: definitions now
#   outputs: RuleEnablementResult
# - id: A2
#   name_zh: ② ComplianceTechEnabler
#   name_en: ComplianceTechEnabler
#   intro: 合规技术使能器（薄封装：定义源持有 + 活跃规则装载 + 最近结果留痕）。
#   desc: 合规技术使能器（薄封装：定义源持有 + 活跃规则装载 + 最近结果留痕）。；公共方法（定义序）: load_active_rules, last_result；源码 L219-L252
#   inputs: definition_source
#   outputs: 返回值
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: RuleEnablementResult
#   name_en: RuleEnablementResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-L10-001(ComplianceEngine 规则装载) ; MOD-CMP-004(合规持续运营 规则新鲜度核查)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Final

from zephyr.shared.contracts.compliance_rule import ComplianceRule
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "ComplianceEnablementError",
    "ComplianceTechEnabler",
    "RuleDefinitionIssue",
    "RuleEnablementResult",
    "materialize_compliance_rules",
]

#: enforcement_action 合法域（ComplianceEngine 契约: block硬阻断/warn告警/log记录）
_ALLOWED_ENFORCEMENT_ACTIONS: Final = frozenset({"block", "warn", "log"})
#: severity 合法域与排序权重（降序输出: critical 最先评估）
_SEVERITY_RANK: Final = {"critical": 0, "high": 1, "medium": 2, "low": 3}

_REQUIRED_FIELDS: Final = (
    "rule_id",
    "rule_name",
    "rule_type",
    "severity",
    "enforcement_action",
    "rule_logic",
    "description",
    "jurisdiction",
    "version",
)


class ComplianceEnablementError(ZephyrBaseError):
    """合规规则使能失败（定义源不可用等；Fail-Closed 上抛）。"""

    error_code = "ZA-CMP-0013"


@dataclass(frozen=True)
class RuleDefinitionIssue:
    """单条被拒绝的规则定义（结构化留痕）。"""

    index: int
    rule_id: str | None
    reason: str


@dataclass(frozen=True)
class RuleEnablementResult:
    """物化结果：生效规则集（severity 降序）+ 拒绝清单。"""

    rules: tuple[ComplianceRule, ...]
    rejected: tuple[RuleDefinitionIssue, ...]
    active_count: int


def _materialize_one(definition: Mapping[str, Any], *, now: datetime) -> ComplianceRule | str:
    """单条物化；返回 ComplianceRule 或拒绝原因字符串。"""
    for field_name in _REQUIRED_FIELDS:
        if field_name not in definition:
            return f"missing_required_field:{field_name}"
    enforcement_action = str(definition["enforcement_action"])
    if enforcement_action not in _ALLOWED_ENFORCEMENT_ACTIONS:
        return f"unknown_enforcement_action:{enforcement_action}（合法域 block/warn/log，不静默降级）"
    severity = str(definition["severity"])
    if severity not in _SEVERITY_RANK:
        return f"unknown_severity:{severity}（合法域 critical/high/medium/low）"
    rule_id = str(definition["rule_id"]).strip()
    if not rule_id:
        return "empty_rule_id"
    return ComplianceRule(
        rule_id=rule_id,
        rule_name=str(definition["rule_name"]),
        rule_type=str(definition["rule_type"]),
        severity=severity,
        enforcement_action=enforcement_action,
        rule_logic=str(definition["rule_logic"]),
        description=str(definition["description"]),
        jurisdiction=str(definition["jurisdiction"]),
        version=str(definition["version"]),
        is_active=bool(definition.get("is_active", True)),
        idempotency_key=str(definition.get("idempotency_key", f"cmp-rule-{rule_id}")),
        created_at=now,
        updated_at=now,
    )


def materialize_compliance_rules(
    definitions: Iterable[Mapping[str, Any]],
    *,
    now: datetime | None = None,
) -> RuleEnablementResult:
    """声明式规则定义 → ComplianceRule 生效集（纯函数）。

    拒绝路径（Fail-Closed，全部留痕不静默）：
      - 非 Mapping 条目 / 必填字段缺失 / 空 rule_id
      - enforcement_action、severity 未知枚举值
      - rule_id 重复（保留首条，后续拒绝）
    """
    now = now or datetime.now(UTC)
    accepted: list[ComplianceRule] = []
    rejected: list[RuleDefinitionIssue] = []
    seen_ids: set[str] = set()

    for index, definition in enumerate(definitions):
        if not isinstance(definition, Mapping):
            rejected.append(RuleDefinitionIssue(index=index, rule_id=None, reason="not_a_mapping"))
            continue
        outcome = _materialize_one(definition, now=now)
        if isinstance(outcome, str):
            rejected.append(
                RuleDefinitionIssue(
                    index=index,
                    rule_id=(str(definition.get("rule_id")) if definition.get("rule_id") is not None else None),
                    reason=outcome,
                )
            )
            continue
        if outcome.rule_id in seen_ids:
            rejected.append(
                RuleDefinitionIssue(
                    index=index,
                    rule_id=outcome.rule_id,
                    reason=f"duplicate_rule_id:{outcome.rule_id}（保留首条）",
                )
            )
            continue
        seen_ids.add(outcome.rule_id)
        accepted.append(outcome)

    accepted.sort(key=lambda r: (_SEVERITY_RANK[r.severity], r.rule_id))
    return RuleEnablementResult(
        rules=tuple(accepted),
        rejected=tuple(rejected),
        active_count=sum(1 for r in accepted if r.is_active),
    )


#: 规则定义源协议（生产接线: 合规规则配置/注册表查询接口）
RuleDefinitionSource = Callable[[], Iterable[Mapping[str, Any]]]


class ComplianceTechEnabler:
    """合规技术使能器（薄封装：定义源持有 + 活跃规则装载 + 最近结果留痕）。"""

    def __init__(self, definition_source: RuleDefinitionSource) -> None:
        self._definition_source = definition_source
        self._last_result: RuleEnablementResult | None = None

    def load_active_rules(self, *, now: datetime | None = None) -> tuple[ComplianceRule, ...]:
        """装载活跃合规规则（severity 降序）。

        Raises:
            ComplianceEnablementError: 定义源失败（Fail-Closed：
                调用方必须按"零规则=阻断"处理，禁止降级为放行）。
        """
        try:
            definitions = self._definition_source()
        except Exception as exc:  # noqa: BLE001 — Fail-Closed 包装后上抛
            raise ComplianceEnablementError(
                f"合规规则定义源不可用，使能中止: {exc}",
                details={"source_error": str(exc)},
            ) from exc
        result = materialize_compliance_rules(definitions, now=now)
        if result.rejected:
            _logger.warning(
                "COMPLIANCE_RULES_REJECTED count=%d reasons=%s",
                len(result.rejected),
                [(r.rule_id, r.reason) for r in result.rejected],
            )
        self._last_result = result
        return tuple(r for r in result.rules if r.is_active)

    @property
    def last_result(self) -> RuleEnablementResult | None:
        return self._last_result
