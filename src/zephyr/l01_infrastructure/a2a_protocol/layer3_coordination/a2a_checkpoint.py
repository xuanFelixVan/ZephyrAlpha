"""A2A 检查点管理器"""

class A2ACheckpoint:
    def __init__(self):
        self._checkpoints: dict = {}

    def save(self, task_id: str, state: dict) -> str:
        self._checkpoints[task_id] = state
        return task_id

    def load(self, task_id: str) -> dict:
        return self._checkpoints.get(task_id, {})
