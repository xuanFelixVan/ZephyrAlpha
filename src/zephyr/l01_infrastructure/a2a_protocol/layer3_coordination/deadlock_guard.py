"""P2: 死锁守卫"""

class DeadlockGuard:
    def __init__(self):
        self._locks: dict = {}

    def try_acquire(self, resource: str, holder: str) -> bool:
        if resource in self._locks:
            return False
        self._locks[resource] = holder
        return True

    def release(self, resource: str, holder: str) -> bool:
        if self._locks.get(resource) == holder:
            del self._locks[resource]
            return True
        return False
