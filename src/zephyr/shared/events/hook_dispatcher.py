# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.events.hook_dispatcher
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.event_bus
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
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

import hashlib
import hmac
import json
import logging
import subprocess
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from zephyr.shared.event_bus import DomainEvent, EventBus, EventType
from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)


@dataclass
class HookConfig:
    hook_id: str
    event_type: EventType
    callback_url: str = ""
    callback_script: str = ""
    enabled: bool = True
    max_retries: int = 3
    # 5.40.5 修复：webhook 密钥（HMAC-SHA256 签名 X-Zephyr-Signature）与超时
    webhook_secret: str = ""
    timeout_seconds: float = 10.0


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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def bus(self):
        """只读：bus（Stage 4 公共化）。"""
        return self._bus

    @bus.setter
    def bus(self, value):
        """写入：bus（Stage 4 公共化）。"""
        self._bus = value

    @property
    def data_dir(self):
        """只读：data_dir（Stage 4 公共化）。"""
        return self._data_dir

    @data_dir.setter
    def data_dir(self, value):
        """写入：data_dir（Stage 4 公共化）。"""
        self._data_dir = value

    @property
    def hooks(self) -> dict[EventType, list[HookConfig]]:
        """只读：hooks（Stage 4 公共化）。"""
        return self._hooks

    @hooks.setter
    def hooks(self, value):
        """写入：hooks（Stage 4 公共化）。"""
        self._hooks = value

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
            result = run_subprocess_hidden(
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
        except (subprocess.TimeoutExpired, Exception) as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        """5.40.5 修复：实现真实 HTTP POST webhook（原方法体为 pass）。

        - 幂等键：Idempotency-Key = hook:{hook_id}:{event_id}——同一事件的重投
          （含 max_retries 内重试）用同一键，接收方可去重。
        - 超时/重试：transient 失败（连接错误/超时/5xx）按 hook.max_retries 重试；
          4xx 为永久失败不重试。
        - HMAC 签名：配置 webhook_secret 时发送 X-Zephyr-Signature: sha256=<hex>。
        - 无论成败都记录 HookExecution（与 _run_script 语义对齐）。
        """
        payload = json.dumps(
            {
                "hook_id": hook.hook_id,
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "task_id": event.task_id,
                "payload": event.payload,
                "timestamp_utc": event.timestamp_utc,
            },
            ensure_ascii=False,
        ).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "X-Zephyr-Hook-Id": hook.hook_id,
            "X-Zephyr-Event-Id": event.event_id,
            "X-Zephyr-Event-Type": event.event_type.value,
            "Idempotency-Key": f"hook:{hook.hook_id}:{event.event_id}",
        }
        if hook.webhook_secret:
            signature = hmac.new(hook.webhook_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
            headers["X-Zephyr-Signature"] = f"sha256={signature}"

        attempts = max(1, hook.max_retries)
        last_error = ""
        for attempt in range(1, attempts + 1):
            req = urllib.request.Request(hook.callback_url, data=payload, headers=headers, method="POST")
            try:
                # 对齐 mcp_result_push 模式：context manager 确保响应关闭
                with urllib.request.urlopen(req, timeout=hook.timeout_seconds) as resp:
                    self._executions.append(
                        HookExecution(
                            hook_id=hook.hook_id,
                            event_id=event.event_id,
                            success=True,
                            response=f"HTTP {resp.status}",
                            timestamp_utc=datetime.now(UTC).isoformat(),
                        )
                    )
                    return
            except urllib.error.HTTPError as e:
                # urllib 对非 2xx 抛 HTTPError；4xx 永久失败不重试，5xx transient 可重试
                last_error = f"HTTP {e.code}"
                if e.code < 500:
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last_error = f"{type(e).__name__}: {e}"
            except Exception as e:  # noqa: BLE001 — 非网络类异常不重试，直接记录失败
                last_error = f"{type(e).__name__}: {e}"
                break
            if attempt < attempts:
                # 短退避；Event().wait() 对齐 mcp_result_push P12 模式（retry delay 非周期触发）
                threading.Event().wait(0.2 * attempt)

        self._executions.append(
            HookExecution(
                hook_id=hook.hook_id,
                event_id=event.event_id,
                success=False,
                response=last_error[:500],
                timestamp_utc=datetime.now(UTC).isoformat(),
            )
        )

    def get_executions(self, hook_id: str = "") -> list[HookExecution]:
        if hook_id:
            return [e for e in self._executions if e.hook_id == hook_id]
        return list(self._executions)
