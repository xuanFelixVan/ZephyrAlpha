---
module_id: KE-2560
status: active
title: === API 提供方灭绝风险 ===
category: module_blueprint
ttl: permanent
---

# === API 提供方灭绝风险 ===

=== API 提供方灭绝风险 ===

class APIProviderRisk(str, Enum):
    DISCONTINUED = "discontinued"
    PRICE_SURGE = "price_surge"
    RATE_LIMIT_CRUSH = "rate_limit_crush"
    ACQUIRED = "acquired"
    GEOPOLITICAL_BLOCK = "geopolitical_block"
    DEPRECATED = "deprecated"


class APIProviderContingencyPlan(BaseModel):
    """API提供方灭绝场景的应急预案（B454）"""
    model_config = ConfigDict(frozen=True)

    plan_id: UUID = Field(default_factory=uuid4)
    provider: Literal["deepseek", "glm", "claude"]
    scenario: APIProviderRisk
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    impact_on_modules: list[str] = Field(default_factory=list)
    dispatch_capacity_loss_pct: float = Field(ge=0.0, le=100.0)

    fallback_chain_available: bool = True
    fallback_degradation_pct: float = Field(ge=0.0, le=100.0)

    estimated_recovery_time_hours: float = 0.0
    auto_mitigation: str = ""
    manual_steps: list[str] = Field(default_factory=list)

    tested: bool = False
    last_drill_date: Optional[datetime] = None


class ProviderHealthMonitor(BaseModel):
    """API提供方健康持续监控（B454）"""
    model_config = ConfigDict(frozen=True)

    monitor_id: UUID = Field(default_factory=uuid4)
    provider: str
    checked_at: datetime = Field(default_factory=datetime.utcnow)

    status_page_ok: bool = True
    api_latency_p95_ms: float = 0.0
    error_rate_1h: float = 0.0
    pricing_page_unchanged: bool = True
    terms_of_service_unchanged: bool = True

    extinction_risk_score: float = Field(ge=0.0, le=1.0)
    alert_triggered: bool = False
