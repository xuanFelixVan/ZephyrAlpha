# [A_module] module_id=MOD-UNK_traces | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# Re-export from authoritative location
from zephyr.infrastructure.system_telemetry.traces import *  # noqa: F403

__all__ = [
    "span_stub",
]
