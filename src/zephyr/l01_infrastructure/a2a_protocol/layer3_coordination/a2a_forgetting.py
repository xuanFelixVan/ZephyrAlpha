"""A2A 遗忘机制"""

class A2AForgetting:
    def __init__(self, max_memory: int = 100):
        self._memory: list = []
        self.max_memory = max_memory

    def remember(self, item: dict) -> None:
        self._memory.append(item)
        self._forget()

    def _forget(self) -> None:
        while len(self._memory) > self.max_memory:
            self._memory.pop(0)
