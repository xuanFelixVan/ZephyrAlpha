# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.lifecycle.scope_guard
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Scope Guard — 范围蔓延检测与阻断。

依据：
    蓝图 MOD-TASK_SYSTEM §6.11.3 + v0.6.0
    任务卡 TASK-INF-0118

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: scope_guard.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ScopeGuard
#   name_en: ScopeGuard
#   intro: class ScopeGuard 源码 L76-L150
#   desc: 公共方法（定义序）: config, project_root, validate_scope, is_blocked, unblock, get_drift_history；源码 L76-L150
#   inputs: project_root
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ScopeGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class ScopeDrift:
    task_id: str
    expected_touch: list[str]
    actual_touch: list[str]
    extra_touch: list[str]
    severity: str
    timestamp_utc: str


@dataclass
class ScopeGuardConfig:
    max_extra_touch: int = 3
    auto_block_on_critical: bool = True
    warn_on_extra: bool = True


class ScopeGuard:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._config = ScopeGuardConfig()
        self._drift_log: list[ScopeDrift] = []
        self._blocked_tasks: set[str] = set()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def config(self):
        """只读：config（Stage 4 公共化）。"""
        return self._config

    @config.setter
    def config(self, value):
        """写入：config（Stage 4 公共化）。"""
        self._config = value

    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    def validate_scope(self, task_card: dict[str, Any], actual_touched: list[str]) -> ScopeDrift | None:
        task_id = task_card.get("task_id", "")
        expected = set(task_card.get("allowed_touch", []))
        upstream = {f if isinstance(f, str) else f.get("file_path", "") for f in task_card.get("upstream_files", [])}
        downstream = {o.get("path", "") for o in task_card.get("downstream_outputs", [])}

        expected = expected | upstream | downstream | {""}
        actual_set = set(actual_touched)

        extra = actual_set - expected

        if not extra:
            return None

        if len(extra) > self._config.max_extra_touch:
            severity = "CRITICAL"
        elif len(extra) > 1:
            severity = "HIGH"
        else:
            severity = "LOW"

        drift = ScopeDrift(
            task_id=task_id,
            expected_touch=sorted(expected),
            actual_touch=actual_touched,
            extra_touch=sorted(extra),
            severity=severity,
            timestamp_utc=datetime.now(UTC).isoformat(),
        )

        self._drift_log.append(drift)

        if severity == "CRITICAL" and self._config.auto_block_on_critical:
            self._blocked_tasks.add(task_id)

        return drift

    def is_blocked(self, task_id: str) -> bool:
        return task_id in self._blocked_tasks

    def unblock(self, task_id: str) -> None:
        self._blocked_tasks.discard(task_id)

    def get_drift_history(self, task_id: str = "") -> list[ScopeDrift]:
        if task_id:
            return [d for d in self._drift_log if d.task_id == task_id]
        return list(self._drift_log)
