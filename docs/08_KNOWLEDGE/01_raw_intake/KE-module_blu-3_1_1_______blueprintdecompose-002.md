---
module_id: KE-module_blu-3_1_1_______blueprintdecompose-002
title: 3.1.1 蓝图拆解器（BlueprintDecomposer）
category: module_blueprint
---

# 3.1.1 蓝图拆解器（BlueprintDecomposer）

3.1.1 蓝图拆解器（BlueprintDecomposer）

```python
from pydantic import BaseModel
from zephyr.db.task_repo import TaskRepo
from zephyr.shared.schemas import Task, TaskStatus

class BlueprintDecomposer:
    """从蓝图 §11 施工指引拆解为任务卡——写入 task_repo（SQLite）+ .md 同步"""

    def __init__(self, repo: TaskRepo):
        self.repo = repo

    def decompose(
        self,
        blueprint_path: str,
        output_dir: str,
        strategy: str = "hybrid",
        model_assignment: str = "auto"
    ) -> "DecompositionResult":
        """
        输入：蓝图路径（§11 施工指引）
        输出：DecompositionResult（任务卡清单 + 依赖图）

        算法：
          1. 解析 §11 每个步骤 → 1 张任务卡
          2. NAMESPACE-SEQ 格式分配 task_id（ADR/CP/KE/STD/DW/SRC/OPS）
          3. 解析步骤中的"创建文件清单"→ downstream_outputs
          4. 解析步骤中的"内容编写指引"→ acceptance
          5. 按 GOV-AI-002 决策树自动分配 execution_model
          6. 每张任务卡 → self.repo.create(task)（写 SQLite）
          7. 同步生成 .md 副本 → {output_dir}/{task_id}.md
          8. G7 门禁通过后才标记 construction_status=complete
        """
        ...
```
