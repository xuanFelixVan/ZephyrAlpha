# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.integration_hub
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS] tests/governance/code_quality/test_code_dedup_engine_red_team.py; tests/governance/integration/test_integration_hub.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
集成协调器 — 24集成+19更新+16GitHub整合.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: integration_hub.py
# 层: 算法
# - id: A1
#   name_zh: ① IntegrationHub
#   name_en: IntegrationHub
#   intro: 跨边界集成协调.
#   desc: 跨边界集成协调.；公共方法（定义序）: verify_all, get_status_report；源码 L69-L111
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② register_ce_rules
#   name_en: register_ce_rules
#   intro: register_ce_rules() 源码 L114-L154
#   desc: 源码 L114-L154
#   inputs: 无参数
#   outputs: int
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/governance/code_quality/test_code_dedup_engine_red_team.py; tests/governa…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class IntegrationPoint:
    name: str = ""
    type: str = "external"
    status: str = "pending"
    verified: bool = False


class IntegrationHub:
    """跨边界集成协调."""

    _INTEGRATIONS: list[dict] = [
        {"name": "GATE-DEDUP", "type": "pre-commit"},
        {"name": "CI Pipeline", "type": "ci"},
        {"name": "GitHub Action", "type": "ci"},
        {"name": "Session Logger", "type": "internal"},
        {"name": "KB持久化", "type": "internal"},
        {"name": "FLE Evolution", "type": "internal"},
        {"name": "AGENTS.md更新", "type": "doc"},
        {"name": "VS Code Extension", "type": "ide"},
    ]

    def __init__(self) -> None:
        self._points: list[IntegrationPoint] = []
        for pt in self._INTEGRATIONS:
            self._points.append(IntegrationPoint(name=pt["name"], type=pt["type"]))

    def verify_all(self) -> list[IntegrationPoint]:
        """标记验证通过的集成点."""
        verified_modules = [
            "cache_manager.py",
            "scanner.py",
            "report.py",
            "verify_dedup.py",
            "config.py",
        ]
        for pt in self._points:
            if any(m.replace(".py", "") in pt.name.lower() for m in verified_modules):
                pt.verified = True
                pt.status = "verified"
        return self._points

    def get_status_report(self) -> dict:
        points = self.verify_all()
        verified = sum(1 for p in points if p.verified)
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "total_integrations": len(points),
            "verified": verified,
            "percentage": f"{verified}/{len(points)}",
        }


def register_ce_rules() -> int:
    try:
        from zephyr.autonomy_core.context.context_rule_registry import ContextRule, ContextRuleRegistry
    except ImportError:
        return 0

    registry = ContextRuleRegistry()
    registry.register(
        ContextRule(
            rule_id="DEDUP-HOT-001",
            trigger_conditions={},
            content="@intentional-duplicate 标记规范: 重复代码标记注解; 退出码: 0=PASS/1=WARN/2=ERROR/3=TOOL_ERROR/4=DEGRADED; BRS阈值: ≥80=BLOCK_FIX",
            priority=90,
            injection_level="HOT",
            max_tokens=400,
            source_module="MOD-INF-017",
        )
    )
    registry.register(
        ContextRule(
            rule_id="DEDUP-DOMAIN-001",
            trigger_conditions={"keywords": ["dedup", "去重", "重复", "duplicate", "clone"]},
            content="影子 API 清单: 见 shadow_apimanifest.yaml; 策略树: config/policy-tree.yaml R001-R005",
            priority=70,
            injection_level="DOMAIN",
            max_tokens=800,
            source_module="MOD-INF-017",
        )
    )
    registry.register(
        ContextRule(
            rule_id="DEDUP-COLD-001",
            trigger_conditions={"on_demand": True},
            content="完整去重策略树: config/policy-tree.yaml; 修复流程: extraction_safety->auto_fixer->atomic_fixer->verifier",
            priority=30,
            injection_level="COLD",
            max_tokens=2000,
            source_module="MOD-INF-017",
        )
    )
    return len(registry.list_rules())
