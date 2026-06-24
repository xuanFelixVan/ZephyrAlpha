# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md | §
# [MODULE] zephyr.integration.shared_08.contracts.experiment.model_serving_response
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.experiment.__init__
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.experiment.model_serving_response
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.integration.shared_08.contracts.experiment.model_serving_response"
# [A_module] module_id=MOD-INT_model_serving_response | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""Re-export shim — 真源已合并至 zephyr.shared.contracts.experiment.model_serving_response。"""

from zephyr.shared.contracts.experiment.model_serving_response import *  # noqa: F401,F403
