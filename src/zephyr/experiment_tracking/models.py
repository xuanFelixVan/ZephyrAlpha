# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] zephyr.experiment_tracking.models
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] stdlib
# [CONSUMERS] zephyr.experiment_tracking.query ; zephyr.frontend.dashboard.components.experiment_history
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 数据模型不可变(frozen)；RunSummary/RunDetail 为统一 JSON 源查询模型
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无（纯数据模型）
# [TESTS] tests/experiment_tracking/test_experiment_tracker.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""L_INFRA_TELEMETRY — 实验跟踪数据模型（RunSummary / RunDetail）。

统一本地 JSON 源的查询模型（MLflow 已退役），Panel/AI 只消费统一模型。
依据: 51_panel_experiment_history_mlflow_retirement.md 工作流 A2 + backtest_observability_mlflow_plan.md M1 query.py 设计
Version: 0.1.1（RunDetail.artifact_paths=dict[str,str] 契约实证归一，见 query.py 治本留痕）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RunSummary:
    """单次运行的摘要（列表查询用）。"""

    run_id: str
    component: str  # c1-validation / regime-detector / ...
    run_name: str
    status: str  # RUNNING / FINISHED / FAILED
    start_time: datetime
    end_time: datetime | None
    passed: bool | None  # C1 等有 passed；无则为 None
    metrics: dict[str, float] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    artifact_uris: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RunDetail(RunSummary):
    """单次运行详情（含 params + artifact 本地路径）。"""

    params: dict[str, Any] = field(default_factory=dict)
    artifact_paths: dict[str, str] = field(default_factory=dict)  # artifact_name → 本地路径
