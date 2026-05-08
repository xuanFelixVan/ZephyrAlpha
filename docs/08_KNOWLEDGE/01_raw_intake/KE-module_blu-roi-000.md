---
module_id: KE-module_blu-roi-000
title: === 成本/ROI 经济学 ===
category: module_blueprint
---

# === 成本/ROI 经济学 ===

=== 成本/ROI 经济学 ===

class BlindSpotROI(BaseModel):
    """盲点修复的 ROI 分析（FMEA RPN 方法论）"""
    model_config = ConfigDict(frozen=True)

    blind_spot_ref: str
    severity: int = Field(ge=1, le=10)
    occurrence: int = Field(ge=1, le=10)
    detectability: int = Field(ge=1, le=10)
    rpn: Optional[int] = None

    estimated_implementation_hours: float = 0.0
    estimated_maintenance_hours_per_year: float = 0.0
    cost_of_failure: float = 0.0
    roi_ratio: Optional[float] = None

    def __post_init__(self):
        if self.rpn is None:
            object.__setattr__(self, 'rpn', self.severity * self.occurrence * self.detectability)
        if self.cost_of_failure > 0 and self.estimated_implementation_hours > 0:
            estimated_labor_cost = self.estimated_implementation_hours * 100
            object.__setattr__(self, 'roi_ratio', self.cost_of_failure / estimated_labor_cost if estimated_labor_cost > 0 else 0)


class CostAttribution(BaseModel):
    """成本归因——每个模块的金钱消耗"""
    model_config = ConfigDict(frozen=True)

    module_id: str
    total_dollars: float = 0.0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    avg_cost_per_call: float = 0.0
    period_start: datetime
    period_end: datetime
