# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.runtime_config
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.contracts.runtime_types
# [CONSUMERS] zephyr.trading.auto_runtime_core;zephyr.trading.lifecycle_manager;zephyr.trading.windows_service;zephyr.trading.__main__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] RuntimeConfig真源在zephyr.shared.contracts.runtime_types;本文件仅作向后兼容re-export
# [MODIFY-GUARD] src/zephyr/shared/contracts/runtime_types.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel, Field

from zephyr.shared.contracts.runtime_types import DATA_DIR, RuntimeConfig

# human_detection_method 合法值——与 runtime_types.RuntimeConfig 字段 description 保持一致
_HUMAN_DETECTION_METHODS = ("heartbeat", "manual_switch", "time_window")


class BrainResourceBudget(BaseModel):
    """大脑资源预算（GAP-006 / GAP-010，蓝图 §3.3 / D-INF035-08 / D-INF035-09）。

    参数真源为蓝图已裁定决策：RAM 上限 2GB（D-INF035-08）、冷启动 SLA P99<10s
    （D-INF035-09）、RTO<5min（蓝图 §1.4）。默认值即裁定值，构造零行为变化。
    """

    max_brain_memory_mb: int = Field(default=2048, description="大脑进程 RAM 预算上限（MB，D-INF035-08=2GB）")
    boot_timeout_ms: int = Field(default=10_000, description="冷启动 SLA 上限（ms，D-INF035-09 P99<10s）")
    recovery_timeout_ms: int = Field(default=300_000, description="崩溃恢复 SLA 上限（ms，RTO<5min）")


@dataclass
class BrainBudgetResult:
    within_budget: bool
    current_mb: float
    budget_mb: int
    action: str  # "ok" | "degrade"（运行中超限→触发降级链）| "refuse_start"（boot 阶段超限→拒启动）


def _default_rss_reader() -> float:
    """当前进程 RSS（MB）。psutil 不可用时返回 0.0（不阻断启动）。"""
    try:
        import os

        import psutil

        return psutil.Process(os.getpid()).memory_info().rss / (1024**2)
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return 0.0


def check_brain_memory_budget(
    budget: BrainResourceBudget | None = None,
    rss_reader: Callable[[], float] | None = None,
    *,
    boot_phase: bool = False,
) -> BrainBudgetResult:
    """RAM 预算检查（GAP-006）：超限 → boot 阶段拒启动 / 运行中触发降级。

    rss_reader 可注入（测试 mock 超限场景）；默认读当前进程 RSS。
    """
    budget = budget or BrainResourceBudget()
    reader = rss_reader or _default_rss_reader
    current_mb = reader()
    within = current_mb <= budget.max_brain_memory_mb
    action = "ok" if within else ("refuse_start" if boot_phase else "degrade")
    return BrainBudgetResult(
        within_budget=within,
        current_mb=current_mb,
        budget_mb=budget.max_brain_memory_mb,
        action=action,
    )


def validate_config(config: RuntimeConfig) -> None:
    """启动前配置完整性校验（5.71.1 治本）——必填字段/类型/范围，失败 fail-fast。

    boot() 首步调用；校验失败抛 ValueError（聚合全部问题一次抛出），阻止带病启动。

    Args:
        config: 待校验的 RuntimeConfig。

    Raises:
        ValueError: 配置非法。
    """
    errors: list[str] = []
    if config.poll_interval <= 0:
        errors.append(f"poll_interval 必须 > 0, got {config.poll_interval}")
    for name in ("max_parallel_l1", "max_parallel_l2", "max_parallel_l3"):
        value = getattr(config, name)
        if not isinstance(value, int) or value < 1:
            errors.append(f"{name} 必须为 >=1 的 int, got {value!r}")
    if config.max_daily_l3_activations < 0:
        errors.append(f"max_daily_l3_activations 必须 >= 0, got {config.max_daily_l3_activations}")
    if not 0 <= config.working_hours_start <= 23:
        errors.append(f"working_hours_start 必须在 0..23, got {config.working_hours_start}")
    if not 1 <= config.working_hours_end <= 24:
        errors.append(f"working_hours_end 必须在 1..24, got {config.working_hours_end}")
    if config.working_hours_start >= config.working_hours_end:
        errors.append(
            f"working_hours_start({config.working_hours_start}) 必须 < working_hours_end({config.working_hours_end})"
        )
    if config.human_detection_method not in _HUMAN_DETECTION_METHODS:
        errors.append(
            f"human_detection_method 必须是 {_HUMAN_DETECTION_METHODS} 之一, got {config.human_detection_method!r}"
        )
    if not config.ollama_base_url.startswith(("http://", "https://")):
        errors.append(f"ollama_base_url 必须是 http(s) URL, got {config.ollama_base_url!r}")
    for name in (
        "audit_log_dir",
        "capability_card_dir",
        "work_dag_dir",
        "dream_archive_dir",
        "feedback_proposal_dir",
        "health_snapshot_dir",
        "night_shift_storage_path",
    ):
        if not str(getattr(config, name)):
            errors.append(f"{name} 不能为空")
    if errors:
        raise ValueError("RuntimeConfig 校验失败: " + "; ".join(errors))


def ensure_runtime_dirs(config: RuntimeConfig) -> None:
    for d in [
        config.audit_log_dir,
        config.capability_card_dir,
        config.work_dag_dir,
        config.dream_archive_dir,
        config.feedback_proposal_dir,
        config.health_snapshot_dir,
        config.night_shift_storage_path.parent,
        # circadian_state_path 已移除（CircadianScheduler 废除，2026-06-26裁定）
    ]:
        d.mkdir(parents=True, exist_ok=True)


__all__ = [
    "DATA_DIR",
    "BrainBudgetResult",
    "BrainResourceBudget",
    "RuntimeConfig",
    "check_brain_memory_budget",
    "ensure_runtime_dirs",
    "validate_config",
]
