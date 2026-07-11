# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.contract_consistency_checker
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/contracts/test_contract_consistency_checker.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_contract_consistency_checker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""API契约一致性检查器 — 存在性·行为·契约三维."""

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
