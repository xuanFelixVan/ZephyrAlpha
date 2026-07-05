# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.config
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_config | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from dataclasses import dataclass


@dataclass
class FLEConfig:
    enable_autonomous_actions: bool = False
    log_dir: str = "logs/fle/"
    otel_endpoint: str = "http://localhost:4317"
    max_concurrent_actions: int = 3
    autonomy_max_level: int = 0
    kb_path: str = "data/fle/kb/"
    worm_path: str = "data/fle/worm/"
