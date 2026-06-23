# [A_module] module_id=MOD-INT_runtime_plane_tag | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md | §
# [MODULE] zephyr.integration.shared_08.contracts.core.runtime_plane_tag
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.core.runtime_plane_tag
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.core.runtime_plane_tag
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "from zephyr.integration.shared_08.contracts.core.runtime_plane_tag import RuntimePlane, HOT_PATH_LATENCY_BUDGET_MS, WARM_PATH_LATENCY_BUDGET_MS, COLD_PATH_LATENCY_BUDGET_MS, HOT_PATH_ACTIVATED, COLD_PATH_PARTIAL_ACTIVATED"
"""Re-export shim — 真源已合并至 zephyr.shared.contracts.core.runtime_plane_tag。"""
from zephyr.shared.contracts.core.runtime_plane_tag import *  # noqa: F401,F403
