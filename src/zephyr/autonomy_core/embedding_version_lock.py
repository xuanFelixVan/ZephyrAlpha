# [A_module] module_id=MOD-ORC_embedding_version_lock | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md

# [MODULE] zephyr.autonomy_core.embedding_version_lock

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""embedding_version_lock.py — 嵌入模型版本锁 (B18, DD92, TASK-017)"""

from dataclasses import dataclass

@dataclass
class EmbeddingVersionInfo:
    model_name: str
    model_version: str
    ke_count: int
    needs_regression_test: bool

class EmbeddingVersionLock:
    """KE metadata: {embedding_model, embedding_version}; embed change→cosine regress (DD92)."""
    _current: tuple[str, str] = ("all-MiniLM-L6-v2", "1.0.0")

    def get_version(self) -> EmbeddingVersionInfo:
        return EmbeddingVersionInfo(model_name=self._current[0], model_version=self._current[1], ke_count=0, needs_regression_test=False)

    def detect_change(self, new_model: str, new_version: str) -> bool:
        return new_model != self._current[0] or new_version != self._current[1]
