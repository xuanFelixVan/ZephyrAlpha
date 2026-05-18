# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.code_dedup_engine.contract_consistency_checker

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""API契约一致性检查器 — 存在性·行为·契约三维."""

from __future__ import annotations

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
