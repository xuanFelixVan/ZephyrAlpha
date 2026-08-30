# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.can_i_deploy
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Can-I-Deploy 预部署门禁（GATE-CDC-1）

依据：MOD-MASTER-002 蓝图 §十六 CT-CDC-001
4项预部署检查：consumer_expectations/schema_version/contract_consistency/health。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: can_i_deploy.py
# 层: 算法
# - id: A1
#   name_zh: ① CanIDeploy
#   name_en: CanIDeploy
#   intro: class CanIDeploy 源码 L70-L94
#   desc: 公共方法（定义序）: check；源码 L70-L94
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: CanIDeploy
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from enum import Enum

from pydantic import BaseModel, Field


class DeployCheck(str, Enum):
    CONSUMER_EXPECTATIONS = "consumer_expectations"
    SCHEMA_VERSION = "schema_version"
    CONTRACT_CONSISTENCY = "contract_consistency"
    HEALTH = "health"


class CanIDeployResult(BaseModel):
    allowed: bool
    checks: dict[str, bool] = Field(default_factory=dict)
    blockers: list[str] = Field(default_factory=list)


class CanIDeploy:
    def __init__(self):
        self._check_results: dict[str, bool] = {}

    def check(
        self,
        *,
        consumer_expectations_ok: bool = True,
        schema_version_ok: bool = True,
        contract_consistency_ok: bool = True,
        health_ok: bool = True,
    ) -> CanIDeployResult:
        checks = {
            "consumer_expectations": consumer_expectations_ok,
            "schema_version": schema_version_ok,
            "contract_consistency": contract_consistency_ok,
            "health": health_ok,
        }
        blockers = [k for k, v in checks.items() if not v]

        return CanIDeployResult(
            allowed=len(blockers) == 0,
            checks=checks,
            blockers=blockers,
        )
