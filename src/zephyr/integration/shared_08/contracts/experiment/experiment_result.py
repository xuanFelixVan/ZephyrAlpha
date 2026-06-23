# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md | §
# [MODULE] zephyr.integration.shared_08.contracts.experiment.experiment_result
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.experiment.__init__
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.experiment.experiment_result
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.experiment.experiment_result
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.integration.shared_08.contracts.experiment.experiment_result"
# [A_module] module_id=MOD-INT_experiment_result | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [MODIFY-GUARD] none

"""Re-export shim — 真源已合并至 zephyr.shared.contracts.experiment.experiment_result。"""

from zephyr.shared.contracts.experiment.experiment_result import *  # noqa: F401,F403
