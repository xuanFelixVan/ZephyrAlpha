# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared.events.event_schemas
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.infra.observer; zephyr.integration.shared.schema.base_config
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
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: "cron"是TimeEventPayload schema的trigger_kind枚举值，非实际cron调用

"""
event_schemas.py —— Observer 事件体 Pydantic V2 Schema（盲点 B6/B10 修复）

痛点修复：observer.py 的 emit() 接受裸 `dict[str, Any]` 作为 payload——
  1. 事件消费者不知道 payload 里有什么字段
  2. 事件生产者可能遗漏必填字段
  3. AI 读 observer.emit() 调用时无法从类型推断 payload 结构

本文件为每种 EventType 定义对应的 Pydantic V2 BaseModel，作为事件体的强类型契约。

与 observer.py 的关系：
  - observer.py 的 EventType 枚举保持 zero-dependency（不使用 Pydantic）
  - 本文件定义 EVENT_PAYLOAD_MAP 将 EventType 映射到对应 Schema
  - 本文件不修改 observer.py——新代码可选使用 Schema 校验，向后兼容

设计原则：
  - 每个 Payload Schema 使用 Pydantic V2 frozen model（不可变）
  - extra="forbid" 确保 AI 不会传入意外字段
  - 字段级 description 为 AI 提供语义指导

AI 施工约定：
  - 新增 EventType 时 MUST 在此定义对应 Payload Schema
  - emit 前 SHOULD 使用对应 Schema 校验 payload
  - 新增字段时 MUST 保持向后兼容（新字段 default / Optional）

SSoT: MOD-INF-016 §2.6 shared-events
Version: 0.1.0
"""

from __future__ import annotations

from typing import Final
import importlib as _importlib
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from zephyr.shared.infra.observer import EventType

_tt_mod = _importlib.import_module("zephyr.gov_enforcement.rule_enforcement.task_types")
TaskStatus = _tt_mod.TaskStatus
from zephyr.integration.shared.schema.base_config import BASE_CONFIG

__all__ = [
    "EVENT_PAYLOAD_MAP",
    "FileEventPayload",
    "ManualEventPayload",
    "MetricEventPayload",
    "TaskEventPayload",
    "TimeEventPayload",
]


class FileEventPayload(BaseModel):
    """FILE_EVENT 事件体——文件系统变更通知。

    emit 时机：文件创建 / 修改 / 删除 / 移动。
    """

    model_config = ConfigDict(**BASE_CONFIG, frozen=True)

    event_kind: Literal["created", "modified", "deleted", "moved"] = Field(
        ...,
        description="文件事件类型：创建/修改/删除/移动",
    )
    path: str = Field(
        ...,
        min_length=1,
        description="相对于 REPO_ROOT 的文件路径",
    )
    abs_path: str = Field(
        ...,
        min_length=1,
        description="文件的完整绝对路径",
    )
    content_hash: str | None = Field(
        default=None,
        description="文件内容的 SHA-256 哈希（如可用）",
    )
    previous_path: str | None = Field(
        default=None,
        description="移动事件的前路径（仅 event_kind=moved 时有效）",
    )
    source: str = Field(
        default="filesystem",
        description="事件来源：filesystem / git / ai_agent",
    )


class TimeEventPayload(BaseModel):
    """TIME_EVENT 事件体——定时触发 / 时间边界通知。

    emit 时机：cron tick / 交易日开始结束 / 超时触发。
    """

    model_config = ConfigDict(**BASE_CONFIG, frozen=True)

    trigger_kind: Literal["cron", "session_start", "session_end", "timeout", "interval"] = Field(
        ...,
        description="触发类型",
    )
    triggered_at: datetime = Field(
        ...,
        description="触发时刻（UTC）",
    )
    schedule_spec: str | None = Field(
        default=None,
        description="Cron 表达式或间隔描述（仅 trigger_kind=cron/interval）",
    )
    session_id: str | None = Field(
        default=None,
        description="关联的 session ID（仅 trigger_kind=session_*）",
    )


class TaskEventPayload(BaseModel):
    """TASK_EVENT 事件体——Task 生命周期状态变更。

    emit 时机：Task 状态机跳转 / Task 创建 / Task 完成 / Task 失败。
    """

    model_config = ConfigDict(**BASE_CONFIG, frozen=True)

    task_id: str = Field(
        ...,
        min_length=1,
        description="Task 唯一标识（T-N-MM 或 T-INF-NNN）",
    )
    from_status: TaskStatus | None = Field(
        default=None,
        description="跳转前状态（Task 创建时为 None）",
    )
    to_status: TaskStatus = Field(
        ...,
        description="当前状态（跳转后）",
    )
    triggered_by: str = Field(
        default="system",
        description="触发者：system / ai_agent / manual / pipeline",
    )
    task_title: str | None = Field(
        default=None,
        description="Task 标题摘要",
    )
    module_id: str | None = Field(
        default=None,
        description="归属 module_id（如 MOD-INF-016）",
    )
    error_message: str | None = Field(
        default=None,
        description="失败原因（仅 to_status=FAILED 时有效）",
    )


class ManualEventPayload(BaseModel):
    """MANUAL_EVENT 事件体——人工 / CLI 触发事件。

    emit 时机：人工命令行操作 / 手动触发流程。
    """

    model_config = ConfigDict(**BASE_CONFIG, frozen=True)

    action: str = Field(
        ...,
        min_length=1,
        description="操作名称（如 rebuild_index, force_evolution, clear_cache）",
    )
    triggered_by: str = Field(
        ...,
        min_length=1,
        description="操作者标识（username / agent_id）",
    )
    target: str | None = Field(
        default=None,
        description="操作目标（如 module_id / task_id / file_path）",
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="额外参数",
    )


class MetricEventPayload(BaseModel):
    """METRIC_EVENT 事件体——系统指标采样。

    emit 时机：指标采集周期 / 门禁评估 / 审计采样。
    """

    model_config = ConfigDict(**BASE_CONFIG, frozen=True)

    metric_name: str = Field(
        ...,
        min_length=1,
        description="指标名称（如 task_completion_rate, token_usage, gate_pass_rate）",
    )
    value: float = Field(
        ...,
        description="指标数值",
    )
    unit: str = Field(
        default="count",
        description="单位：count / ms / pct / token / bytes",
    )
    sampled_at: datetime = Field(
        ...,
        description="采样时刻（UTC）",
    )
    labels: dict[str, str] = Field(
        default_factory=dict,
        description="维度标签（如 module_id=MOD-INF-016, status=PENDING）",
    )
    threshold: float | None = Field(
        default=None,
        description="告警阈值（超出此值触发告警）",
    )


EVENT_PAYLOAD_MAP: Final[dict[EventType, type[BaseModel]]] = {
    EventType.FILE_EVENT: FileEventPayload,
    EventType.TIME_EVENT: TimeEventPayload,
    EventType.TASK_EVENT: TaskEventPayload,
    EventType.MANUAL_EVENT: ManualEventPayload,
    EventType.METRIC_EVENT: MetricEventPayload,
}
