# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.checkpoint_manager
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
checkpoint_manager.py — Inject 前快照 (DD100, TASK-019)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: store_dir 参数
#   fields: 参数 store_dir（无注解）
#   code: checkpoint_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CheckpointManager
#   name_en: CheckpointManager
#   intro: Inject 前 snapshot; 回滚到注入前 (DD100).
#   desc: Inject 前 snapshot; 回滚到注入前 (DD100).；公共方法（定义序）: save, restore；源码 L64-L81
#   inputs: store_dir
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CheckpointManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
