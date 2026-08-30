# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.contract_consistency_checker
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/contracts/test_contract_consistency_checker.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
API契约一致性检查器 — 存在性·行为·契约三维.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: contract_consistency_checker.py
# 层: 算法
# - id: A1
#   name_zh: ① ContractConsistencyChecker
#   name_en: ContractConsistencyChecker
#   intro: 三维API契约检查.
#   desc: 三维API契约检查.；公共方法（定义序）: verify；源码 L61-L86
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ContractConsistencyChecker
#   downstream: tests/contracts/test_contract_consistency_checker.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class ContractCheck:
    function_name: str = ""
    exists_in_manifest: bool = False
    behavior_matches: bool = False
    contract_consistent: bool = False
    score: int = 0


class ContractConsistencyChecker:
    """三维API契约检查."""

    def verify(
        self,
        function_name: str,
        manifest_functions: set[str],
        behavior_ok: bool,
        contract_ok: bool,
    ) -> ContractCheck:
        exists = function_name in manifest_functions
        score = 0
        if exists:
            score += 40
        if behavior_ok:
            score += 30
        if contract_ok:
            score += 30

        return ContractCheck(
            function_name=function_name,
            exists_in_manifest=exists,
            behavior_matches=behavior_ok,
            contract_consistent=contract_ok,
            score=score,
        )
