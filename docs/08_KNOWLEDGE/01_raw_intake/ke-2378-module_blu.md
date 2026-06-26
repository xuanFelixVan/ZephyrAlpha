---
module_id: KE-2283
status: active
title: 5.1 仪表盘数据结构
category: module_blueprint
ttl: permanent
---

# 5.1 仪表盘数据结构

5.1 仪表盘数据结构

```python
class AssetDashboard(BaseModel):
    """资产仪表盘——每次全量扫描 + 对账后更新"""
    generated_at: datetime
    based_on_scan: str  # scan_id

    # 总数
    total_assets: int
    total_size_mb: float

    # 分类分布
    by_type: dict[str, int]
    by_layer: dict[str, int]
    by_status: dict[str, int]
    by_priority: dict[str, int]

    # 健康指标
    health_score: str = Field(..., description="A~F")
    orphan_count: int
    orphan_rate_pct: float
    ghost_count: int
    ghost_rate_pct: float
    drift_count: int
    drift_rate_pct: float

    # 趋势（最近 10 次扫描）
    trend_orphan: list[int] = Field(default_factory=list)
    trend_total: list[int] = Field(default_factory=list)
    trend_health: list[str] = Field(default_factory=list)

    # Top 异常
    top_orphans: list[str] = Field(default_factory=list, description="最早被发现的 5 个孤儿")
    top_ghosts: list[str] = Field(default_factory=list, description="最关键的 5 个幽灵")

    # 上次对账
    last_reconciliation_time: Optional[datetime] = None
    last_reconciliation_scan_id: Optional[str] = None
```
