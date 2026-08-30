# [BLUEPRINT] MOD-DATA_GOV-011 | docs/03_modules/_domain_data_governance/openlineage_exporter/blueprint.md
# [MODULE] zephyr.data_governance.openlineage_exporter
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] 无（纯内存；root/line_sink/clock 全注入；JSON 序列化 stdlib）
# [CONSUMERS] 运行时装配批（JSONL 落盘 root 绑定 / Marquez 兼容消费方对接）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] RunEvent 五要素(eventType/run/job/inputs/outputs)+facets 必填闭合; eventType 词表闭合(START|RUNNING|COMPLETE|ABORT|FAIL); JSONL 序列化 sort_keys 确定性; 导出前校验失败一行不写; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_governance/openlineage_exporter/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] OpenLineageError(占位 ZA-DATA-UNREGISTERED-OPENLINEAGE)——必填缺失/非法eventType/非法边/root与line_sink均未注入时抛
# [TESTS] tests/data_governance/test_openlineage_exporter.py
# [A_module] module_id=MOD-DATA_GOV-011 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



openlineage_exporter — OpenLineage 事件导出器（MOD-DATA_GOV-011）。

B10-02320（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATGOV-008，A1 M8-NEW-01）：
lineage_tracker 事件模型对齐 OpenLineage 规范——**RunEvent** dataclass
（eventType/run/job/inputs/outputs/facets 五要素+切面）+ 事件转换器（内部边
-> OpenLineage 事件）+ **JSONL 导出**（追加写注入 root，或注入 line_sink 纯
内存替身）+ 导出校验（必填字段闭合）。

查重分工（蓝图 §0）：core/lineage_tracker=血缘图本体（本件只消费其边三元组
做事件转换，不改图）；runtime_lineage_collector=运行时采集（零交集，本件=
规范序列化与导出）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: event 参数
#   fields: 参数 event，类型注解 RunEvent
#   code: openlineage_exporter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: edge 参数
#   fields: 参数 edge，类型注解 Edge
#   code: openlineage_exporter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: run_id 参数
#   fields: 参数 run_id（无注解）
#   code: openlineage_exporter.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: job_namespace 参数
#   fields: 参数 job_namespace（无注解）
#   code: openlineage_exporter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① validate_event
#   name_en: validate_event
#   intro: 必填字段闭合校验：eventType 词表 + run/job 标识非空。
#   desc: 必填字段闭合校验：eventType 词表 + run/job 标识非空。；源码 L161-L173
#   inputs: event
#   outputs: 返回值
# - id: A2
#   name_zh: ② event_to_jsonl
#   name_en: event_to_jsonl
#   intro: RunEvent → 单行 JSONL（sort_keys 确定性序列化）。
#   desc: RunEvent → 单行 JSONL（sort_keys 确定性序列化）。；源码 L176-L188
#   inputs: event
#   outputs: str
# - id: A3
#   name_zh: ③ edge_to_event
#   name_en: edge_to_event
#   intro: 内部血缘边 (source,target,transformation) → OpenLineage RunEvent。
#   desc: 内部血缘边 (source,target,transformation) → OpenLineage RunEvent。 job.name 取 transformation（空则…；源码 L191-L222
#   inputs: edge run_id job_namespace event_type event_time facets
#   outputs: RunEvent
# - id: A4
#   name_zh: ④ OpenLineageExporter
#   name_en: OpenLineageExporter
#   intro: OpenLineage JSONL 导出器（追加写注入 root，或注入 line_sink）。
#   desc: OpenLineage JSONL 导出器（追加写注入 root，或注入 line_sink）。；公共方法（定义序）: export, export_edges；源码 L225-L281
#   inputs: root clock line_sink file_name
#   outputs: 返回值
#   （注：A4 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 运行时装配批（JSONL 落盘 root 绑定 / Marquez 兼容消费方对接）
# - id: O2
#   name_zh: RunEvent
#   name_en: RunEvent
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 运行时装配批（JSONL 落盘 root 绑定 / Marquez 兼容消费方对接）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "EventType",
    "OpenLineageError",
    "OpenLineageExporter",
    "RunEvent",
    "edge_to_event",
    "event_to_jsonl",
    "validate_event",
]

#: 内部血缘边三元组 (source, target, transformation)
Edge = tuple[str, str, str]


class OpenLineageError(Exception):
    """OpenLineage 事件校验/导出输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DATA-UNREGISTERED-OPENLINEAGE。
    """


class EventType(str, Enum):
    """OpenLineage eventType 词表（闭合）。"""

    START = "START"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    ABORT = "ABORT"
    FAIL = "FAIL"


@dataclass(frozen=True)
class RunEvent:
    """OpenLineage RunEvent（五要素 + facets + event_time，frozen）。"""

    event_type: EventType
    run_id: str
    job_namespace: str
    job_name: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    facets: Mapping[str, str] = field(default_factory=dict)
    event_time: datetime.datetime | None = None


def validate_event(event: RunEvent) -> None:
    """必填字段闭合校验：eventType 词表 + run/job 标识非空。"""
    if not isinstance(event.event_type, EventType):
        raise OpenLineageError(f"非法 eventType: {event.event_type!r}")
    if not event.run_id:
        raise OpenLineageError("run.runId 为空")
    if not event.job_namespace:
        raise OpenLineageError("job.namespace 为空")
    if not event.job_name:
        raise OpenLineageError("job.name 为空")
    for name in (*event.inputs, *event.outputs):
        if not name:
            raise OpenLineageError("inputs/outputs 含空 dataset 名")


def event_to_jsonl(event: RunEvent) -> str:
    """RunEvent → 单行 JSONL（sort_keys 确定性序列化）。"""
    validate_event(event)
    payload = {
        "eventType": event.event_type.value,
        "eventTime": (event.event_time.isoformat() if event.event_time else None),
        "run": {"runId": event.run_id},
        "job": {"namespace": event.job_namespace, "name": event.job_name},
        "inputs": [{"namespace": event.job_namespace, "name": n} for n in event.inputs],
        "outputs": [{"namespace": event.job_namespace, "name": n} for n in event.outputs],
        "facets": {k: event.facets[k] for k in sorted(event.facets)},
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def edge_to_event(
    edge: Edge,
    *,
    run_id: str,
    job_namespace: str,
    event_type: EventType = EventType.COMPLETE,
    event_time: datetime.datetime | None = None,
    facets: Mapping[str, str] | None = None,
) -> RunEvent:
    """内部血缘边 (source,target,transformation) → OpenLineage RunEvent。

    job.name 取 transformation（空则回退 "source->target"）；inputs=(source,)，
    outputs=(target,)。
    """
    if len(edge) != 3:
        raise OpenLineageError(f"非法边(须三元组): {edge!r}")
    source, target, transformation = edge
    if not source or not target:
        raise OpenLineageError(f"边端点为空: {edge!r}")
    job_name = transformation or f"{source}->{target}"
    event = RunEvent(
        event_type=event_type,
        run_id=run_id,
        job_namespace=job_namespace,
        job_name=job_name,
        inputs=(source,),
        outputs=(target,),
        facets=dict(facets or {}),
        event_time=event_time,
    )
    validate_event(event)
    return event


class OpenLineageExporter:
    """OpenLineage JSONL 导出器（追加写注入 root，或注入 line_sink）。"""

    def __init__(
        self,
        *,
        root: str | Path | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        line_sink: Callable[[str], None] | None = None,
        file_name: str = "openlineage_events.jsonl",
    ) -> None:
        if line_sink is None:
            if root is None:
                raise OpenLineageError("root 与 line_sink 均未注入（Fail-Closed 不旁路）")
            path = Path(root) / file_name

            def line_sink(line: str) -> None:  # type: ignore[no-redef]
                with open(path, "a", encoding="utf-8") as fh:
                    fh.write(line + "\n")

        self._sink = line_sink
        self._clock = clock or datetime.datetime.now

    def export(self, event: RunEvent) -> str:
        """校验 → 序列化 → 追加写一行；返回该 JSONL 行（校验失败一行不写）。"""
        line = event_to_jsonl(event)
        try:
            self._sink(line)
        except OpenLineageError:
            raise
        except Exception as exc:  # noqa: BLE001 — 写出失败 Fail-Closed
            raise OpenLineageError(f"JSONL 写出失败: {exc}") from exc
        _log.debug("OpenLineage 导出: run=%s job=%s", event.run_id, event.job_name)
        return line

    def export_edges(
        self,
        edges: Iterable[Edge],
        *,
        run_id: str,
        job_namespace: str,
        event_type: EventType = EventType.COMPLETE,
        facets: Mapping[str, str] | None = None,
    ) -> tuple[str, ...]:
        """内部边集合批量转换导出（event_time 取注入时钟）。"""
        lines: list[str] = []
        for edge in edges:
            event = edge_to_event(
                edge,
                run_id=run_id,
                job_namespace=job_namespace,
                event_type=event_type,
                event_time=self._clock(),
                facets=facets,
            )
            lines.append(self.export(event))
        return tuple(lines)
