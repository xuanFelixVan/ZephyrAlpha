# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.modules.multi_model_vendor_risk
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_multi_model_vendor_risk | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
Multi-Model Vendor Risk — 多模型供应商风险缓和 (盲点 #38)
特性：
  - 供应商份额控制：单一供应商 > 70% → 风险警报
  - 后备模型池定义
"""

from collections import defaultdict


class MultiModelVendorRisk:
    """
    多模型供应商风险 (盲点 #38)
    """

    SINGLE_VENDOR_SATURATION_THRESHOLD = 0.70

    def __init__(self):
        self._vendor_usage: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def record(self, vendor: str, model: str, tokens: int):
        self._vendor_usage[vendor][model] += tokens

    def check(self) -> dict:
        total = sum(sum(models.values()) for vendor, models in self._vendor_usage.items())
        if total == 0:
            return {"risk": "N/A", "vendor_shares": {}}

        vendor_shares = {}
        max_share = 0
        dominant_vendor = ""

        for vendor, models in self._vendor_usage.items():
            vendor_tokens = sum(models.values())
            share = vendor_tokens / total
            vendor_shares[vendor] = round(share, 2)
            if share > max_share:
                max_share = share
                dominant_vendor = vendor

        risk = "HIGH" if max_share > self.SINGLE_VENDOR_SATURATION_THRESHOLD else "LOW"

        return {
            "risk": risk,
            "dominant_vendor": dominant_vendor,
            "dominant_share": round(max_share, 2),
            "vendor_shares": vendor_shares,
            "threshold": self.SINGLE_VENDOR_SATURATION_THRESHOLD,
        }
