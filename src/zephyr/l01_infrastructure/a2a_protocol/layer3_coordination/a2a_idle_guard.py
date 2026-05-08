"""A2A 空闲守卫"""

class A2AIdleGuard:
    def __init__(self, idle_timeout: float = 300):
        self.idle_timeout = idle_timeout

    def check_idle(self, agent_id: str, last_active: float, now: float) -> bool:
        return (now - last_active) > self.idle_timeout
