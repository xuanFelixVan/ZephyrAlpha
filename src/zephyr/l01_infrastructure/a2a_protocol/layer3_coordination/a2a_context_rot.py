"""上下文腐烂检测"""

class A2AContextRot:
    def detect_rot(self, context_data: dict, age_seconds: float) -> float:
        return min(1.0, age_seconds / 3600)  # 线性衰减，1小时100%腐烂
