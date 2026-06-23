# [A_module] module_id=MOD-INT_telemetry_emitter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md | §
# [MODULE] zephyr.integration.shared_08.contracts.core.telemetry_emitter
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.core.telemetry_emitter
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.core.telemetry_emitter
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.integration.shared_08.contracts.core.telemetry_emitter"
"""Re-export shim — 真源已合并至 zephyr.shared.contracts.core.telemetry_emitter。"""
from zephyr.shared.contracts.core.telemetry_emitter import *  # noqa: F401,F403
