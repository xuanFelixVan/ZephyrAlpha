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
