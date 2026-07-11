# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.governance.security_governance.security_gateway_base
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.compliance_rule
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_security_gateway_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
D_COMPLIANCE — Governance & Compliance Layer

治理与合规层。负责架构守卫、权限控制、AI 安全网关与审计追溯。

核心职责（六模块）：
  - AISG（AI Security Gateway）：拦截 AI 生成的代码/指令
  - ARCH_GUARD（架构守卫）：不变量 ↔ 适应度函数映射验证
  - Compliance Scanner（合规扫描）：ADONIS 19 类违规检测
  - Authority Registry（权限注册表）：AI 自主权限管理
  - Session Log（会话日志）：AI 对话变更追踪
  - Policy Decision Ledger（策略决策账本）：审计不可篡改链

扩展点：
  - SecurityGateway    : OCP D_COMPLIANCE-AISG — AI 安全网关
  - ComplianceEngine   : OCP D_COMPLIANCE-CPL — 合规规则引擎

依赖方向：全层监控 -> 无上游依赖（D_COMPLIANCE 是横向 Johari 基础设施）
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar

from zephyr.governance.rule_enforcement.compliance_rule import ComplianceRule


class AuditAction(str, Enum):
    """审计动作类型"""

    ALLOW = "allow"
    BLOCK = "block"
    FLAG = "flag"
    REDIRECT = "redirect"


@dataclass(frozen=True)
class AuditDecision:
    """审计决策记录（写入 policy_decision_ledger.jsonl）"""

    decision_id: str
    action: AuditAction
    rule_id: str
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


class SecurityGateway(abc.ABC):
    """
    AI Security Gateway 抽象基类

    所有 AI 生成内容必须经过：
      pre_filter -> security-scan -> decision -> audit_log

    INV-015：AISG 拦截门禁 — 任何跳过 AISG 的 AI 指令执行均违反此不变量。
    """

    _instance: ClassVar[SecurityGateway | None] = None

    @abc.abstractmethod
    def pre_filter(self, content: str, source: str) -> bool:
        """预过滤：检查内容是否需要安全扫描"""
        ...

    @abc.abstractmethod
    def security_scan(self, content: str) -> list[str]:
        """安全扫描：返回检测到的风险列表"""
        ...

    @abc.abstractmethod
    def decide(self, risks: list[str], context: dict[str, Any]) -> AuditDecision:
        """基于风险做出审计决策"""
        ...


class ComplianceEngine(abc.ABC):
    """
    合规规则引擎（OCP 扩展点 D_COMPLIANCE-CPL）

    契约对齐：CTR-P1-012（ComplianceRule 出站）-> D_RISK, D_EXECUTION_CORE, D_COMPLIANCE

    实现者要求：
      - evaluate(): 接收交易/持仓/事件上下文，返回参与评估的合规规则列表
      - 规则按 severity 排序：critical > high > medium > low
      - enforcement_action 决定了处理方式：block（硬阻断）/ warn（告警）/ log（记录）
    """

    _registry: ClassVar[dict[str, type[ComplianceEngine]]] = {}

    @abc.abstractmethod
    def evaluate(self, context: dict[str, Any], idempotency_key: str) -> list[ComplianceRule]:
        """评估给定上下文，返回应执行的合规规则列表"""
        ...

    @abc.abstractmethod
    def enforce(self, rule: ComplianceRule, context: dict[str, Any]) -> AuditDecision:
        """对合规规则做出审计裁决"""
        ...

    def register_rule(self, rule: ComplianceRule) -> None:
        """注册新合规规则（可选覆盖）"""
        pass


__all__ = [
    "AuditAction",
    "AuditDecision",
    "ComplianceEngine",
    "ComplianceRule",
    "SecurityGateway",
]
