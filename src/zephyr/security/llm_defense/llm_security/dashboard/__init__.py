# [A_module] module_id=MOD-SEC_dashboard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/llm_security/blueprint.md | §
# [TTL] task_bound
"""LLM Security Gateway Dashboard Module."""

from . import app

__all__ = ["app"]
