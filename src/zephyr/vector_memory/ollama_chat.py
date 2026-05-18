# [BLUEPRINT] MOD-INF-039 | docs/03_modules/l01_infrastructure/local-model/blueprint.md | §3.3
# [MODULE] zephyr.local_model.ollama_chat
# [CONSUMERS] local_model_scheduler;auto_runtime_core
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
from zephyr.local_model.ollama_chat import OllamaChat, OllamaChat as _OllamaChat  # noqa: F401

__all__ = ["OllamaChat"]
