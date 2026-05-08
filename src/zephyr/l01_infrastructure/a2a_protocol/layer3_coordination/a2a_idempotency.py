"""A2A 幂等性保证"""

class A2AIdempotency:
    def __init__(self):
        self._history: set = set()

    def is_duplicate(self, task_id: str, input_hash: str) -> bool:
        key = f"{task_id}:{input_hash}"
        if key in self._history:
            return True
        self._history.add(key)
        return False
