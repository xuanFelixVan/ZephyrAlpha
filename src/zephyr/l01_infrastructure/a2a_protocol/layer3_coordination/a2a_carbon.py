"""A2A 碳足迹追踪"""

class A2ACarbon:
    tokens_per_kwh: float = 1e6  # 每kWh的tokens数

    @classmethod
    def estimate(cls, tokens: int) -> dict:
        return {"tokens": tokens, "kwh_est": tokens / cls.tokens_per_kwh}
