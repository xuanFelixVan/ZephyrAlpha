"""A2A 硬件路由器——GPU/CPU 调度"""

class A2AHardwareRouter:
    def route(self, task_type: str) -> str:
        routes = {"inference": "gpu", "training": "gpu", "governance": "cpu", "default": "cpu"}
        return routes.get(task_type, "cpu")
