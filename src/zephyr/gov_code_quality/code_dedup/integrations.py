# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.integrations
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/integration/test_integrations.py
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
# noqa: m10-time-trigger  M10豁免: "cron"在注释/文档字符串中，非实际cron调用

"""
集成管理——预提交钩子+CI-only 扫描+超时边界.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: integrations.py
# 层: 算法
# - id: A1
#   name_zh: ① IntegrationManager
#   name_en: IntegrationManager
#   intro: class IntegrationManager 源码 L67-L90
#   desc: 公共方法（定义序）: register_precommit, register_ci, status；源码 L67-L90
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: IntegrationManager
#   downstream: tests/governance/integration/test_integrations.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntegrationConfig:
    precommit_enabled: bool = True
    ci_enabled: bool = True
    ci_cron: str = "0 3 * * *"
    precommit_timeout_ms: int = 5000
    ci_timeout_ms: int = 300000
    precommit_strategy: str = "MINHASH"
    ci_strategy: str = "AST_FUZZY"
    auto_register_precommit: bool = True


@dataclass
class IntegrationManager:
    config: IntegrationConfig = field(default_factory=IntegrationConfig)
    hooks: list[dict[str, Any]] = field(default_factory=list)

    def register_precommit(self) -> dict[str, Any]:
        return {
            "hook": "verify_dedup",
            "script": "scripts/pre-commit/verify_dedup.py",
            "strategy": self.config.precommit_strategy,
            "timeout_ms": self.config.precommit_timeout_ms,
            "enabled": self.config.precommit_enabled,
        }

    def register_ci(self) -> dict[str, Any]:
        return {
            "workflow": "dedup-test",
            "cron": self.config.ci_cron,
            "strategy": self.config.ci_strategy,
            "timeout_ms": self.config.ci_timeout_ms,
            "enabled": self.config.ci_enabled,
        }

    def status(self) -> dict[str, Any]:
        return {"precommit": self.register_precommit(), "ci": self.register_ci()}
