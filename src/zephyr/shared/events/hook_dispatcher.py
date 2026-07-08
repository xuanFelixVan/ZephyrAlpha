# [BLUEPRINT] SRC-098 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.events.hook_dispatcher
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.event_bus
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_hook_dispatcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Hook Dispatcher — 任务状态变更 -> 外部回调触发。

依据：
    蓝图 MOD-TASK_SYSTEM §13.3 路线图 #4 + v0.6.0
    任务卡 TASK-INF-0132 (Part 1/4)

功能：
    - 任务状态变更时触发外部回调（Webhook/脚本）
    - MTH-015 模板实现
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from zephyr.shared.event_bus import DomainEvent, EventBus, EventType


@dataclass
class HookConfig:
    hook_id: str
    event_type: EventType
    callback_url: str = ""
    callback_script: str = ""
    enabled: bool = True
    max_retries: int = 3


@dataclass
class HookExecution:
    hook_id: str
    event_id: str
    success: bool
    response: str
    timestamp_utc: str


class HookDispatcher:
    def __init__(self, event_bus: EventBus | None = None, data_dir: Path | None = None) -> None:
        self._bus = event_bus or EventBus.get_instance()
        self._data_dir = data_dir or Path("data/events")
        self._hooks: dict[EventType, list[HookConfig]] = {et: [] for et in EventType}
        self._executions: list[HookExecution] = []
        self._bus.subscribe(EventType.TASK_COMPLETED, self._on_event)
        self._bus.subscribe(EventType.TASK_FAILED, self._on_event)

    def register_hook(self, hook: HookConfig) -> None:
        if hook.event_type in self._hooks:
            self._hooks[hook.event_type].append(hook)

    def _on_event(self, event: DomainEvent) -> None:
        for hook in self._hooks.get(event.event_type, []):
            if not hook.enabled:
                continue

            self._dispatch_hook(hook, event)

    def _dispatch_hook(self, hook: HookConfig, event: DomainEvent) -> None:
        if hook.callback_script:
            self._run_script(hook, event)
        elif hook.callback_url:
            self._call_webhook(hook, event)

    def _run_script(self, hook: HookConfig, event: DomainEvent) -> None:
        try:
            # 5.40.6 修复：原 env={} 替换整个环境，子进程无 PATH/HOME/PYTHONPATH 必然立即失败。
            # 改为合并 os.environ 与自定义环境变量，保留继承的环境变量。
            import os
            env = {
                **os.environ,
                "ZEPHYR_TASK_ID": event.task_id,
                "ZEPHYR_EVENT_TYPE": event.event_type.value,
            }
            result = subprocess.run(
                hook.callback_script.split(),
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )

            self._executions.append(
                HookExecution(
                    hook_id=hook.hook_id,
                    event_id=event.event_id,
                    success=result.returncode == 0,
                    response=result.stdout[:500],
                    timestamp_utc=datetime.now(UTC).isoformat(),
                )
            )
        except (subprocess.TimeoutExpired, Exception) as e:
            self._executions.append(
                HookExecution(
                    hook_id=hook.hook_id,
                    event_id=event.event_id,
                    success=False,
                    response=str(e)[:500],
                    timestamp_utc=datetime.now(UTC).isoformat(),
                )
            )

    def _call_webhook(self, hook: HookConfig, event: DomainEvent) -> None:
        pass

    def get_executions(self, hook_id: str = "") -> list[HookExecution]:
        if hook_id:
            return [e for e in self._executions if e.hook_id == hook_id]
        return list(self._executions)
