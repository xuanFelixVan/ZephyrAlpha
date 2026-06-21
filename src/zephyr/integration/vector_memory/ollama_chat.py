# [A_module] module_id=MOD-INT_ollama_chat | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_domain-integration/local-model/blueprint.md | §3.3
# [MODULE] zephyr.integration.local_model.ollama_chat
# [CONSUMERS] local_model_scheduler;auto_runtime_core
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
from zephyr.integration.local_model.ollama_chat import OllamaChat, OllamaChat as _OllamaChat  # noqa: F401

__all__ = ["OllamaChat"]
