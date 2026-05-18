# [BLUEPRINT] MOD-INF-025 | docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md
# [MODULE] zephyr.l01_infrastructure.a2a_protocol
# [INVARIANTS] Agent间通信;冲突解决;四级委托约束
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md;src/zephyr/l01_infrastructure/a2a_protocol/__init__.py
# [CONSUMERS] MOD-INF-027;MOD-INF-018;MOD-INF-022
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CommunicationError;ConflictError;DelegationError
# [TESTS] tests/test_a2a_protocol/

from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PromptVersion:
    prompt_id: str
    semantic_version: str
    prompt_text: str

PROMPT_REGRESSION_THRESHOLD: float = 0.05
PROMPT_STORE: dict[str, PromptVersion] = {}
