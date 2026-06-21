# [A_module] module_id=MOD-UNK_implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L11-001 | docs/03_modules/_domain-ml_train/ml-core/blueprint.md
# [MODULE] zephyr.ml_train.implementations
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""L11 — ML Training Concrete Implementations"""
from __future__ import annotations

from zephyr.ml_train.implementations.default_inference_engine import DefaultInferenceEngine

__all__ = ['DefaultInferenceEngine', 'default_inference_engine']
