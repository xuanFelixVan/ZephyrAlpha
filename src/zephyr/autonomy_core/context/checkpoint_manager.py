# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.checkpoint_manager
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""checkpoint_manager.py — Inject 前快照 (DD100, TASK-019)"""

import json
from dataclasses import dataclass
from pathlib import Path

from zephyr.shared.io.serialization import filter_dataclass_fields


@dataclass
class Checkpoint:
    id: str
    context_snapshot: str
    ke_ids: list[str]
    token_count: int


class CheckpointManager:
    """Inject 前 snapshot; 回滚到注入前 (DD100)."""

    def __init__(self, store_dir: str | Path = ".ce_checkpoints") -> None:
        self._store = Path(store_dir)
        self._store.mkdir(parents=True, exist_ok=True)

    def save(self, ckpt: Checkpoint) -> str:
        path = self._store / f"{ckpt.id}.json"
        path.write_text(json.dumps(ckpt.__dict__, ensure_ascii=False), encoding="utf-8")
        return str(path)

    def restore(self, checkpoint_id: str) -> Checkpoint | None:
        path = self._store / f"{checkpoint_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return Checkpoint(**filter_dataclass_fields(Checkpoint, data))
