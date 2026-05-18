# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.config

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from dataclasses import dataclass, field


@dataclass
class FLEConfig:
    enable_autonomous_actions: bool = False
    log_dir: str = "logs/fle/"
    otel_endpoint: str = "http://localhost:4317"
    max_concurrent_actions: int = 3
    autonomy_max_level: int = 0
    kb_path: str = "data/fle/kb/"
    worm_path: str = "data/fle/worm/"
